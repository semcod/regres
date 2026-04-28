#!/usr/bin/env python3
"""
defscan.py — skaner duplikatów definicji klas, funkcji i modeli danych.

Wyciąga PEŁNE CIAŁA definicji (nie tylko pierwszą linię) i porównuje
ich podobieństwo między sobą. Wyniki posortowane od najczęściej
powtarzających się nazw do najrzadszych.

Obsługiwane języki: Python (.py), TypeScript/JavaScript (.ts .tsx .js .jsx),
                    CSS/SCSS (.css .scss), Go (.go), Rust (.rs)

UŻYCIE:
  python defscan.py                        # skanuj bieżący katalog
  python defscan.py --path /projekt        # inny katalog
  python defscan.py --name ProtocolStatus  # filtruj konkretną nazwę
  python defscan.py --kind class           # tylko klasy
  python defscan.py --min-count 2          # min. liczba duplikatów
  python defscan.py --min-sim 40           # pokaż pary z podobieństwem ≥ 40%
  python defscan.py --json > report.json   # eksport JSON
  python defscan.py --md > report.md       # eksport Markdown

TRYB FOCUS (folder vs reszta projektu — porównanie po nazwie):
  python defscan.py --focus ./backend
  python defscan.py --focus ./backend --scope .

TRYB SEED (similarity globalna — szuka podobnych ciał, niezależnie od nazwy):
  python defscan.py --seed ./backend --similar-global --min-sim 60
  python defscan.py --seed ./backend/app/models --kind class --min-sim 70

PRZYKŁADY:
  # Znajdź wszystkie klasy zdefiniowane w więcej niż 1 miejscu
  python defscan.py --kind class --min-count 2

  # Sprawdź konkretny symbol
  python defscan.py --name ProtocolStatus --min-sim 0

  # Pełny raport do wklejenia do LLM
  python defscan.py --min-count 2 --json > dup-report.json

  # Czy ./backend duplikuje cokolwiek z reszty projektu?
  python defscan.py --focus ./backend --min-sim 50

  # Znajdź ukryte duplikaty modeli backendu (różne nazwy, podobny kod)
  python defscan.py --seed ./backend --kind class --min-sim 70
"""

import ast
import fnmatch
import re
import sys
import json
import argparse
import textwrap
from pathlib import Path
from difflib import SequenceMatcher
from collections import defaultdict
from typing import Optional

# ---------------------------------------------------------------------------
# Stałe
# ---------------------------------------------------------------------------

IGNORED_DIRS = {
    '.git', '.github', '__pycache__', 'node_modules', '.venv', 'venv', 'env',
    'dist', 'build', 'target', 'out', '.next', '.nuxt',
    'coverage', '.pytest_cache', '.mypy_cache', '_archive', '.cache',
}

# Mapowanie rozszerzenia → język
EXT_LANG = {
    '.py': 'python',
    '.ts': 'typescript', '.tsx': 'typescript',
    '.js': 'javascript', '.jsx': 'javascript',
    '.go': 'go',
    '.rs': 'rust',
    '.css': 'css', '.scss': 'scss', '.less': 'css',
}

# Kolory ANSI (wyłączane gdy --no-color lub redirect do pliku)
USE_COLOR = sys.stdout.isatty()

def c(text: str, code: str) -> str:
    if not USE_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"

RED    = '31'
YELLOW = '33'
GREEN  = '32'
CYAN   = '36'
BOLD   = '1'
DIM    = '2'

# ---------------------------------------------------------------------------
# Ekstrakcja ciał definicji
# ---------------------------------------------------------------------------

class Definition:
    """Pojedyncza definicja (klasa / funkcja / enum / interface / mixin)."""
    __slots__ = ('name', 'kind', 'path', 'line_start', 'line_end',
                 'body', 'body_normalized', 'lang', 'bases', 'decorators')

    def __init__(self, name, kind, path, line_start, line_end,
                 body, lang, bases=None, decorators=None):
        self.name = name
        self.kind = kind
        self.path = str(path)
        self.line_start = line_start
        self.line_end = line_end
        self.body = body                          # oryginalna treść
        self.body_normalized = _normalize(body)  # do porównania
        self.lang = lang
        self.bases = bases or []                 # klasy bazowe
        self.decorators = decorators or []

    @property
    def loc(self) -> int:
        """Lines of code (bez pustych)."""
        return sum(1 for l in self.body.splitlines() if l.strip())

    def __repr__(self):
        return f"<Def {self.kind} {self.name} {self.path}:{self.line_start}>"


def _normalize(text: str) -> str:
    """Normalizacja kodu do porównania: usuwa komentarze, stringi, białe znaki."""
    # Blokowe /* ... */
    text = re.sub(r'/\*.*?\*/', ' ', text, flags=re.DOTALL)
    # Jednolinijkowe //
    text = re.sub(r'//[^\n]*', ' ', text)
    # Python #
    text = re.sub(r'#[^\n]*', ' ', text)
    # Docstringi Python (triple-quoted)
    text = re.sub(r'""".*?"""', '"DS"', text, flags=re.DOTALL)
    text = re.sub(r"'''.*?'''", '"DS"', text, flags=re.DOTALL)
    # Literały stringów
    text = re.sub(r'''(['"`])(?:\\.|(?!\1).)*?\1''', '"S"', text)
    # Białe znaki → pojedyncze spacje
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def sim(a: Definition, b: Definition) -> float:
    """Podobieństwo ciał (0–100%)."""
    na = a.body_normalized
    nb = b.body_normalized
    if not na or not nb:
        return 0.0
    return SequenceMatcher(None, na, nb).ratio() * 100


# ---------------------------------------------------------------------------
# Ekstraktory per język
# ---------------------------------------------------------------------------

def _get_body(node, lines: list[str]) -> tuple[int, int, str]:
    """Get the start line, end line, and body text of an AST node."""
    start = node.lineno
    end = max(
        getattr(n, 'end_lineno', node.lineno)
        for n in ast.walk(node)
    )
    body_lines = lines[start - 1:end]
    return start, end, '\n'.join(body_lines)


def _get_decorators(node) -> list[str]:
    """Extract decorator strings from an AST node."""
    return [
        ast.unparse(dec) if hasattr(ast, 'unparse') else ''
        for dec in getattr(node, 'decorator_list', [])
    ]


def _collect_class_method_ids(tree) -> set[int]:
    """Collect ids of methods defined inside classes."""
    class_method_ids: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    class_method_ids.add(id(item))
    return class_method_ids


def _extract_class_definitions(node: ast.ClassDef, path: Path, lines: list[str]) -> list[Definition]:
    """Extract class and method definitions from a ClassDef node."""
    defs = []
    start, end, body = _get_body(node, lines)
    bases = [ast.unparse(b) if hasattr(ast, 'unparse') else '' for b in node.bases]
    defs.append(Definition(
        name=node.name, kind='class',
        path=path, line_start=start, line_end=end,
        body=body, lang='python',
        bases=bases,
        decorators=_get_decorators(node),
    ))
    for item in node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            ms, me, mb = _get_body(item, lines)
            defs.append(Definition(
                name=f"{node.name}.{item.name}", kind='method',
                path=path, line_start=ms, line_end=me,
                body=mb, lang='python',
                decorators=_get_decorators(item),
            ))
    return defs


def _extract_function_definition(node, path: Path, lines: list[str], class_method_ids: set[int]) -> list[Definition]:
    """Extract a top-level function definition, skipping class methods."""
    if id(node) in class_method_ids:
        return []
    start, end, body = _get_body(node, lines)
    return [Definition(
        name=node.name, kind='function',
        path=path, line_start=start, line_end=end,
        body=body, lang='python',
        decorators=_get_decorators(node),
    )]


def extract_python(path: Path) -> list[Definition]:
    """Używa modułu ast — precyzyjne wyodrębnienie z zachowaniem linii."""
    text = path.read_text(encoding='utf-8', errors='ignore')
    lines = text.splitlines()
    defs = []

    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError:
        return []

    class_method_ids = _collect_class_method_ids(tree)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            defs.extend(_extract_class_definitions(node, path, lines))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defs.extend(_extract_function_definition(node, path, lines, class_method_ids))

    return defs


def _extract_block_ts(text: str, start_pos: int) -> str:
    """
    Wyciąga blok { ... } z pozycji start_pos w tekście TS/JS.
    Obsługuje zagnieżdżenia i stringi.
    """
    depth = 0
    in_string = None
    i = start_pos
    block_start = None

    while i < len(text):
        ch = text[i]

        # Obsługa stringów
        if in_string:
            if ch == '\\':
                i += 2
                continue
            if ch == in_string:
                in_string = None
            i += 1
            continue

        if ch in ('"', "'", '`'):
            in_string = ch
        elif ch == '/' and i + 1 < len(text):
            if text[i + 1] == '/':
                # Jednolinijkowy komentarz
                nl = text.find('\n', i)
                i = nl + 1 if nl != -1 else len(text)
                continue
            elif text[i + 1] == '*':
                end = text.find('*/', i + 2)
                i = end + 2 if end != -1 else len(text)
                continue
        elif ch == '{':
            if block_start is None:
                block_start = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and block_start is not None:
                return text[block_start:i + 1]
        i += 1
    return text[start_pos:] if block_start is None else ''


# Wzorce do ekstrakcji TS/JS
_TS_CLASS_RE = re.compile(
    r'(?:export\s+)?(?:abstract\s+)?class\s+(\w+)'
    r'(?:\s*<[^>]*>)?'                              # generyki
    r'(?:\s+extends\s+([\w<>, ]+?))?'
    r'(?:\s+implements\s+([\w<>, ]+?))?'
    r'\s*\{',
    re.MULTILINE,
)
_TS_INTERFACE_RE = re.compile(
    r'(?:export\s+)?interface\s+(\w+)'
    r'(?:\s*<[^>]*>)?'
    r'(?:\s+extends\s+([\w<>, ]+?))?'
    r'\s*\{',
    re.MULTILINE,
)
_TS_ENUM_RE = re.compile(
    r'(?:export\s+)?(?:const\s+)?enum\s+(\w+)\s*\{',
    re.MULTILINE,
)
_TS_TYPE_RE = re.compile(
    r'(?:export\s+)?type\s+(\w+)(?:\s*<[^>]*>)?\s*=\s*\{',
    re.MULTILINE,
)
_TS_FUNC_RE = re.compile(
    r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*'
    r'(?:<[^>]*>)?\s*\([^)]*\)'
    r'(?:\s*:\s*[\w<>\[\]|& ]+)?\s*\{',
    re.MULTILINE,
)
_TS_ARROW_RE = re.compile(
    r'(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*'
    r'(?:async\s+)?(?:\([^)]*\)|[\w]+)\s*(?::\s*[\w<>\[\]|& ]+)?\s*=>\s*\{',
    re.MULTILINE,
)


def _lineno_at(text: str, pos: int) -> int:
    return text[:pos].count('\n') + 1


def extract_typescript(path: Path) -> list[Definition]:
    text = path.read_text(encoding='utf-8', errors='ignore')
    lang = 'typescript' if path.suffix in ('.ts', '.tsx') else 'javascript'
    defs = []

    patterns_kinds = [
        (_TS_CLASS_RE,     'class'),
        (_TS_INTERFACE_RE, 'interface'),
        (_TS_ENUM_RE,      'enum'),
        (_TS_TYPE_RE,      'type'),
        (_TS_FUNC_RE,      'function'),
        (_TS_ARROW_RE,     'function'),
    ]

    for pattern, kind in patterns_kinds:
        for m in pattern.finditer(text):
            name = m.group(1)
            line_start = _lineno_at(text, m.start())
            # Wyciągnij blok od pozycji { w dopasowaniu
            brace_pos = text.find('{', m.start())
            if brace_pos == -1:
                continue
            body_block = _extract_block_ts(text, brace_pos)
            if not body_block:
                continue

            full_body = text[m.start(): brace_pos + len(body_block)]
            line_end = line_start + full_body.count('\n')

            bases = []
            if kind == 'class' and m.lastindex and m.lastindex >= 2 and m.group(2):
                bases = [b.strip() for b in re.split(r',\s*', m.group(2))]

            defs.append(Definition(
                name=name, kind=kind,
                path=path, line_start=line_start, line_end=line_end,
                body=full_body, lang=lang, bases=bases,
            ))

    return defs


_GO_FUNC_RE = re.compile(
    r'^func\s+(?:\(\w+\s+\*?(\w+)\)\s+)?(\w+)\s*\([^)]*\)',
    re.MULTILINE,
)
_GO_STRUCT_RE = re.compile(r'^type\s+(\w+)\s+struct\s*\{', re.MULTILINE)
_GO_INTERFACE_RE = re.compile(r'^type\s+(\w+)\s+interface\s*\{', re.MULTILINE)


def extract_go(path: Path) -> list[Definition]:
    text = path.read_text(encoding='utf-8', errors='ignore')
    defs = []

    for pattern, kind in [(_GO_STRUCT_RE, 'struct'), (_GO_INTERFACE_RE, 'interface')]:
        for m in pattern.finditer(text):
            name = m.group(1)
            brace_pos = text.find('{', m.start())
            body = _extract_block_ts(text, brace_pos)
            full = text[m.start(): m.start() + text[m.start():].find(body) + len(body)]
            ls = _lineno_at(text, m.start())
            defs.append(Definition(name=name, kind=kind, path=path,
                                   line_start=ls, line_end=ls + full.count('\n'),
                                   body=full, lang='go'))
    for m in _GO_FUNC_RE.finditer(text):
        receiver = m.group(1)
        name = m.group(2)
        full_name = f"{receiver}.{name}" if receiver else name
        brace_pos = text.find('{', m.end())
        if brace_pos == -1:
            continue
        body = _extract_block_ts(text, brace_pos)
        full = text[m.start(): m.start() + text[m.start():].find(body) + len(body)]
        ls = _lineno_at(text, m.start())
        defs.append(Definition(name=full_name, kind='function', path=path,
                               line_start=ls, line_end=ls + full.count('\n'),
                               body=full, lang='go'))
    return defs


_RS_STRUCT_RE = re.compile(r'^(?:pub\s+)?struct\s+(\w+)', re.MULTILINE)
_RS_ENUM_RE   = re.compile(r'^(?:pub\s+)?enum\s+(\w+)', re.MULTILINE)
_RS_TRAIT_RE  = re.compile(r'^(?:pub\s+)?trait\s+(\w+)', re.MULTILINE)
_RS_FN_RE     = re.compile(r'^(?:pub\s+)?(?:async\s+)?fn\s+(\w+)', re.MULTILINE)


def extract_rust(path: Path) -> list[Definition]:
    text = path.read_text(encoding='utf-8', errors='ignore')
    defs = []
    for pattern, kind in [(_RS_STRUCT_RE, 'struct'), (_RS_ENUM_RE, 'enum'),
                           (_RS_TRAIT_RE, 'trait'), (_RS_FN_RE, 'function')]:
        for m in pattern.finditer(text):
            name = m.group(1)
            brace_pos = text.find('{', m.start())
            if brace_pos == -1:
                continue
            body = _extract_block_ts(text, brace_pos)
            full = text[m.start(): m.start() + text[m.start():].find(body) + len(body)]
            ls = _lineno_at(text, m.start())
            defs.append(Definition(name=name, kind=kind, path=path,
                                   line_start=ls, line_end=ls + full.count('\n'),
                                   body=full, lang='rust'))
    return defs


def extract_file(path: Path) -> list[Definition]:
    ext = path.suffix.lower()
    try:
        if ext == '.py':
            return extract_python(path)
        elif ext in ('.ts', '.tsx', '.js', '.jsx'):
            return extract_typescript(path)
        elif ext == '.go':
            return extract_go(path)
        elif ext == '.rs':
            return extract_rust(path)
    except Exception as e:
        print(f"  [WARN] {path}: {e}", file=sys.stderr)
    return []


# ---------------------------------------------------------------------------
# .gitignore support
# ---------------------------------------------------------------------------

def load_gitignore(root: Path) -> list[tuple[str, bool]]:
    """Wczytuje wzorce z ``root/.gitignore``. Zwraca listę (pattern, is_negation)."""
    gitignore = root / '.gitignore'
    if not gitignore.exists():
        return []
    patterns: list[tuple[str, bool]] = []
    for line in gitignore.read_text(encoding='utf-8', errors='ignore').splitlines():
        line = line.rstrip()
        if not line or line.startswith('#'):
            continue
        neg = line.startswith('!')
        pat = line[1:] if neg else line
        pat = pat.rstrip()
        if not pat:
            continue
        patterns.append((pat, neg))
    return patterns


def _match_anchored_pattern(rel_str: str, pat_cmp: str, is_dir: bool) -> bool:
    """Match an anchored gitignore pattern against a relative path."""
    if fnmatch.fnmatch(rel_str, pat_cmp):
        return True
    if is_dir:
        parts = rel_str.split('/')
        for i in range(1, len(parts)):
            prefix = '/'.join(parts[:i])
            if fnmatch.fnmatch(prefix, pat_cmp):
                return True
    return False


def _match_unanchored_pattern(name: str, rel: Path, rel_str: str, pat_cmp: str, is_dir: bool) -> bool:
    """Match an unanchored gitignore pattern against a file name or path parts."""
    if fnmatch.fnmatch(name, pat_cmp):
        return True
    for part in rel.parts:
        if fnmatch.fnmatch(part, pat_cmp):
            return True
    if is_dir:
        parts = rel_str.split('/')
        for i in range(len(parts) - 1):
            if fnmatch.fnmatch(parts[i], pat_cmp):
                return True
    return False


def _path_ignored_by_gitignore(path: Path, root: Path,
                                patterns: list[tuple[str, bool]]) -> bool:
    """Sprawdza czy ``path`` (względem ``root``) pasuje do .gitignore."""
    try:
        rel = path.relative_to(root)
    except ValueError:
        return False
    rel_str = rel.as_posix()
    name = path.name
    ignored = False
    for pat, neg in patterns:
        is_dir = pat.endswith('/')
        pat_cmp = pat.rstrip('/')
        anchored = '/' in pat_cmp or pat.startswith('/')
        if pat.startswith('/'):
            pat_cmp = pat_cmp.lstrip('/')
        if anchored:
            matched = _match_anchored_pattern(rel_str, pat_cmp, is_dir)
        else:
            matched = _match_unanchored_pattern(name, rel, rel_str, pat_cmp, is_dir)
        if matched:
            ignored = not neg
    return ignored


# ---------------------------------------------------------------------------
# Skanowanie projektu
# ---------------------------------------------------------------------------

def _should_skip_file(
    p: Path,
    exts: set[str],
    only_within_resolved: Optional[Path],
    gitignore_root_resolved: Path,
    gitignore_patterns: Optional[list[tuple[str, bool]]],
) -> bool:
    """Return True if a file should be skipped during scanning."""
    if not p.is_file():
        return True
    if any(part in IGNORED_DIRS for part in p.parts):
        return True
    if any(part.startswith('.') for part in p.parts):
        return True
    if gitignore_patterns and _path_ignored_by_gitignore(
        p, gitignore_root_resolved, gitignore_patterns
    ):
        return True
    if p.suffix.lower() not in exts:
        return True
    if only_within_resolved is not None:
        try:
            p.resolve().relative_to(only_within_resolved)
        except ValueError:
            return True
    return False


def scan(root: Path, name_filter: Optional[str] = None,
         kind_filter: Optional[str] = None,
         only_within: Optional[Path] = None,
         gitignore_patterns: Optional[list[tuple[str, bool]]] = None,
         gitignore_root: Optional[Path] = None,
         ext_filter: Optional[set[str]] = None) -> dict[str, list[Definition]]:
    """
    Zwraca słownik: base_name → [Definition, ...]
    Klucz to bazowa nazwa (bez prefiksu klasy dla metod).

    Jeśli ``only_within`` jest podane, do indeksu trafiają wyłącznie pliki
    znajdujące się wewnątrz tej ścieżki (po resolve()).
    """
    index: dict[str, list[Definition]] = defaultdict(list)
    exts = set(EXT_LANG.keys())
    if ext_filter is not None:
        exts &= {e.lower() for e in ext_filter}
    only_within_resolved = only_within.resolve() if only_within else None
    gitignore_root_resolved = (gitignore_root.resolve()
                               if gitignore_root is not None
                               else root.resolve())
    if gitignore_patterns is None:
        gitignore_patterns = load_gitignore(gitignore_root_resolved)

    for p in root.rglob('*'):
        if _should_skip_file(p, exts, only_within_resolved, gitignore_root_resolved, gitignore_patterns):
            continue

        defs = extract_file(p)
        for d in defs:
            # Bazowa nazwa: dla "ClassName.methodName" bierz "methodName"
            base = d.name.split('.')[-1] if '.' in d.name else d.name

            if name_filter and base.lower() != name_filter.lower():
                continue
            if kind_filter and d.kind != kind_filter:
                continue

            index[base].append(d)

    return index


def _def_key(d: Definition) -> tuple:
    """Klucz identyfikujący definicję — używany do deduplikacji między skanami."""
    return (d.path, d.line_start, d.name, d.kind)


# ---------------------------------------------------------------------------
# Tryb seed: similarity globalna (porównanie ciał, nie nazw)
# ---------------------------------------------------------------------------

def compare_seed_to_all(
    seed_defs: list[Definition],
    all_defs: list[Definition],
    min_sim: float,
    skip_same_name: bool = False,
) -> list[tuple[Definition, list[tuple[Definition, float]]]]:
    """
    Dla każdej definicji z seed znajduje wszystkie definicje w all_defs
    z podobieństwem ciała ≥ min_sim.

    Zwraca: [(seed_def, [(other_def, similarity), ...]), ...]
    posortowane wg najlepszego dopasowania w obrębie listy matches malejąco.
    Wpisy bez dopasowań są pomijane.
    """
    results = []
    seed_keys = {_def_key(s) for s in seed_defs}

    for s in seed_defs:
        s_key = _def_key(s)
        matches: list[tuple[Definition, float]] = []
        for d in all_defs:
            d_key = _def_key(d)
            if d_key == s_key:
                continue
            # Pomijamy inne seedy, jeśli porównujemy seed→reszta
            if d_key in seed_keys:
                continue
            if skip_same_name and d.name.split('.')[-1] == s.name.split('.')[-1]:
                continue
            similarity = sim(s, d)
            if similarity >= min_sim:
                matches.append((d, similarity))
        if matches:
            matches.sort(key=lambda x: x[1], reverse=True)
            results.append((s, matches))

    # Sortuj seedy wg najwyższego podobieństwa malejąco
    results.sort(key=lambda r: r[1][0][1], reverse=True)
    return results


# ---------------------------------------------------------------------------
# Analiza podobieństwa w grupie
# ---------------------------------------------------------------------------

def analyse_group(defs: list[Definition]) -> list[dict]:
    """
    Dla listy definicji o tej samej nazwie oblicza macierz podobieństwa
    i zwraca listę par (i, j, similarity%).
    """
    pairs = []
    for i in range(len(defs)):
        for j in range(i + 1, len(defs)):
            s = sim(defs[i], defs[j])
            pairs.append({'i': i, 'j': j, 'similarity': round(s, 1)})
    pairs.sort(key=lambda x: x['similarity'], reverse=True)
    return pairs


def classify_similarity(pct: float) -> tuple[str, str]:
    """Zwraca (etykieta, kolor_ANSI)."""
    if pct >= 95:
        return "IDENTYCZNE",   RED
    elif pct >= 75:
        return "PRAWIE KOPIE", YELLOW
    elif pct >= 50:
        return "PODOBNE",      CYAN
    elif pct >= 25:
        return "CZĘŚCIOWE",    GREEN
    else:
        return "RÓŻNE",        DIM


# ---------------------------------------------------------------------------
# Renderowanie
# ---------------------------------------------------------------------------

def _short_path(path: str, root: str) -> str:
    try:
        return str(Path(path).relative_to(root))
    except ValueError:
        return path


def render_text(groups: list[tuple[str, list[Definition], list[dict]]],
                root: str, min_sim: float = 0.0,
                show_body_lines: int = 6) -> str:
    lines = []
    total_defs = sum(len(g[1]) for g in groups)
    lines.append(c(f"{'='*70}", BOLD))
    lines.append(c(f"  defscan — znalezione duplikaty definicji", BOLD))
    lines.append(c(f"  Grup: {len(groups)}  |  Definicji łącznie: {total_defs}", DIM))
    lines.append(c(f"{'='*70}", BOLD))
    lines.append("")

    for rank, (name, defs, pairs) in enumerate(groups, 1):
        count = len(defs)
        kinds = sorted({d.kind for d in defs})
        langs = sorted({d.lang for d in defs})

        lines.append(c(f"#{rank}  {name}", BOLD) +
                     c(f"  [{', '.join(kinds)}]", CYAN) +
                     c(f"  {count}× definicji", YELLOW) +
                     c(f"  języki: {', '.join(langs)}", DIM))

        for idx, d in enumerate(defs):
            sp = _short_path(d.path, root)
            loc_info = c(f"{d.loc} LOC", DIM)
            bases_str = c(f"  extends: {', '.join(d.bases)}", DIM) if d.bases else ""
            lines.append(f"  [{idx}] {sp}:{d.line_start}–{d.line_end}  {loc_info}{bases_str}")

            # Podgląd ciała
            if show_body_lines > 0:
                preview = d.body.strip().splitlines()[:show_body_lines]
                for pl in preview:
                    lines.append(c(f"       │ {pl}", DIM))
                if len(d.body.strip().splitlines()) > show_body_lines:
                    total_body = len(d.body.strip().splitlines())
                    lines.append(c(f"       │ … ({total_body} linii)", DIM))

        # Macierz podobieństwa
        relevant_pairs = [p for p in pairs if p['similarity'] >= min_sim]
        if relevant_pairs:
            lines.append(c(f"  Podobieństwo par (≥{min_sim}%):", BOLD))
            for p in relevant_pairs:
                label, col = classify_similarity(p['similarity'])
                da = defs[p['i']]
                db = defs[p['j']]
                sp_a = _short_path(da.path, root)
                sp_b = _short_path(db.path, root)
                sim_str = c(f"{p['similarity']:5.1f}%", col)
                label_str = c(f"[{label}]", col)
                lines.append(f"    [{p['i']}]↔[{p['j']}]  {sim_str} {label_str}")
                lines.append(c(f"          {sp_a}:{da.line_start}", DIM))
                lines.append(c(f"          {sp_b}:{db.line_start}", DIM))

        lines.append("")

    return '\n'.join(lines)


def render_markdown(groups: list[tuple[str, list[Definition], list[dict]]],
                    root: str, min_sim: float = 0.0) -> str:
    lines = []
    lines.append("# defscan — Raport duplikatów definicji\n")
    lines.append(f"Grup: {len(groups)}  |  "
                 f"Definicji łącznie: {sum(len(g[1]) for g in groups)}\n")
    lines.append("---\n")

    for rank, (name, defs, pairs) in enumerate(groups, 1):
        kinds = sorted({d.kind for d in defs})
        langs = sorted({d.lang for d in defs})
        lines.append(f"## #{rank} `{name}` — {len(defs)}× "
                     f"[{', '.join(kinds)}] | {', '.join(langs)}\n")

        lines.append("| # | Plik | Linie | LOC | Klasy bazowe |")
        lines.append("|---|------|-------|-----|--------------|")
        for idx, d in enumerate(defs):
            sp = _short_path(d.path, root)
            bases = ', '.join(d.bases) if d.bases else "—"
            lines.append(f"| [{idx}] | `{sp}` | {d.line_start}–{d.line_end} "
                         f"| {d.loc} | {bases} |")
        lines.append("")

        # Podgląd
        for idx, d in enumerate(defs):
            sp = _short_path(d.path, root)
            preview = '\n'.join(d.body.strip().splitlines()[:8])
            lines.append(f"<details><summary>[{idx}] {sp}:{d.line_start}</summary>\n")
            lines.append(f"```{d.lang}\n{preview}\n```\n</details>\n")

        relevant_pairs = [p for p in pairs if p['similarity'] >= min_sim]
        if relevant_pairs:
            lines.append("**Podobieństwo par:**\n")
            lines.append("| Para | Podobieństwo | Ocena |")
            lines.append("|------|-------------|-------|")
            for p in relevant_pairs:
                label, _ = classify_similarity(p['similarity'])
                lines.append(f"| [{p['i']}]↔[{p['j']}] | {p['similarity']}% | {label} |")
            lines.append("")

        lines.append("---\n")
    return '\n'.join(lines)


def render_seed_text(
    results: list[tuple[Definition, list[tuple[Definition, float]]]],
    root: str,
    top_per_seed: int = 10,
    show_body_lines: int = 4,
) -> str:
    lines = []
    lines.append(c(f"{'='*70}", BOLD))
    lines.append(c(f"  defscan — seed similarity (porównanie ciał)", BOLD))
    lines.append(c(f"  Seedów z dopasowaniami: {len(results)}", DIM))
    lines.append(c(f"{'='*70}", BOLD))
    lines.append("")

    for rank, (seed, matches) in enumerate(results, 1):
        sp = _short_path(seed.path, root)
        loc_info = c(f"{seed.loc} LOC", DIM)
        lines.append(
            c(f"#{rank}  {seed.name}", BOLD)
            + c(f"  [{seed.kind}/{seed.lang}]", CYAN)
            + f"  {sp}:{seed.line_start}–{seed.line_end}  "
            + loc_info
        )
        if show_body_lines > 0:
            preview = seed.body.strip().splitlines()[:show_body_lines]
            for pl in preview:
                lines.append(c(f"     │ {pl}", DIM))
            if len(seed.body.strip().splitlines()) > show_body_lines:
                total = len(seed.body.strip().splitlines())
                lines.append(c(f"     │ … ({total} linii)", DIM))

        shown = matches[:top_per_seed] if top_per_seed else matches
        for d, simv in shown:
            label, col = classify_similarity(simv)
            sp_d = _short_path(d.path, root)
            sim_str = c(f"{simv:5.1f}%", col)
            label_str = c(f"[{label}]", col)
            same_name = d.name.split('.')[-1] == seed.name.split('.')[-1]
            name_tag = c(" (ta sama nazwa)", DIM) if same_name else ""
            lines.append(
                f"   {sim_str} {label_str}  {d.name} "
                f"[{d.kind}/{d.lang}]  {sp_d}:{d.line_start}{name_tag}"
            )
        if top_per_seed and len(matches) > top_per_seed:
            lines.append(c(f"   … pominięto {len(matches) - top_per_seed} dopasowań", DIM))
        lines.append("")

    return '\n'.join(lines)


def render_seed_markdown(
    results: list[tuple[Definition, list[tuple[Definition, float]]]],
    root: str,
    top_per_seed: int = 10,
) -> str:
    lines = []
    lines.append("# defscan — Seed similarity (porównanie ciał)\n")
    lines.append(f"Seedów z dopasowaniami: {len(results)}\n")
    lines.append("---\n")
    for rank, (seed, matches) in enumerate(results, 1):
        sp = _short_path(seed.path, root)
        lines.append(
            f"## #{rank} `{seed.name}` — {seed.kind}/{seed.lang} "
            f"`{sp}:{seed.line_start}–{seed.line_end}` ({seed.loc} LOC)\n"
        )
        lines.append("| % | Etykieta | Nazwa | Rodzaj | Plik:Linia | Ta sama nazwa |")
        lines.append("|---|---------|-------|--------|------------|---------------|")
        shown = matches[:top_per_seed] if top_per_seed else matches
        for d, simv in shown:
            label, _ = classify_similarity(simv)
            sp_d = _short_path(d.path, root)
            same_name = "tak" if d.name.split('.')[-1] == seed.name.split('.')[-1] else "nie"
            lines.append(
                f"| {simv:.1f}% | {label} | `{d.name}` | {d.kind}/{d.lang} "
                f"| `{sp_d}:{d.line_start}` | {same_name} |"
            )
        if top_per_seed and len(matches) > top_per_seed:
            lines.append(f"\n_… pominięto {len(matches) - top_per_seed} dopasowań_\n")
        lines.append("---\n")
    return '\n'.join(lines)


def render_seed_json(
    results: list[tuple[Definition, list[tuple[Definition, float]]]],
    root: str,
) -> str:
    out = []
    for rank, (seed, matches) in enumerate(results, 1):
        out.append({
            'rank': rank,
            'seed': {
                'name': seed.name,
                'kind': seed.kind,
                'lang': seed.lang,
                'path': _short_path(seed.path, root),
                'line_start': seed.line_start,
                'line_end': seed.line_end,
                'loc': seed.loc,
                'body_preview': seed.body.strip()[:400],
            },
            'matches': [
                {
                    'similarity': round(simv, 1),
                    'similarity_class': classify_similarity(simv)[0],
                    'name': d.name,
                    'kind': d.kind,
                    'lang': d.lang,
                    'path': _short_path(d.path, root),
                    'line_start': d.line_start,
                    'line_end': d.line_end,
                    'loc': d.loc,
                    'same_name': d.name.split('.')[-1] == seed.name.split('.')[-1],
                }
                for d, simv in matches
            ],
        })
    return json.dumps(out, indent=2, ensure_ascii=False)


def render_json(groups: list[tuple[str, list[Definition], list[dict]]],
                root: str) -> str:
    out = []
    for rank, (name, defs, pairs) in enumerate(groups, 1):
        label, _ = classify_similarity(
            max((p['similarity'] for p in pairs), default=0)
        )
        out.append({
            'rank': rank,
            'name': name,
            'count': len(defs),
            'kinds': sorted({d.kind for d in defs}),
            'langs': sorted({d.lang for d in defs}),
            'max_similarity': max((p['similarity'] for p in pairs), default=None),
            'similarity_class': label,
            'definitions': [
                {
                    'path': _short_path(d.path, root),
                    'kind': d.kind,
                    'lang': d.lang,
                    'line_start': d.line_start,
                    'line_end': d.line_end,
                    'loc': d.loc,
                    'bases': d.bases,
                    'decorators': d.decorators,
                    'body_preview': d.body.strip()[:400],
                    'body_normalized_len': len(d.body_normalized),
                }
                for d in defs
            ],
            'similarity_pairs': pairs,
        })
    return json.dumps(out, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _build_argument_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser for defscan."""
    parser = argparse.ArgumentParser(
        description='defscan — skaner duplikatów klas, funkcji i modeli danych',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument('--path', '-p', default='.',
                        help='Katalog główny projektu (domyślnie: .)')
    parser.add_argument('--name', '-n', default='',
                        help='Filtruj po nazwie symbolu (dokładne dopasowanie, case-insensitive)')
    parser.add_argument('--kind', '-k', default='',
                        choices=['', 'class', 'function', 'method', 'interface',
                                 'enum', 'type', 'struct', 'trait'],
                        help='Filtruj po rodzaju definicji')
    parser.add_argument('--ext', '-e', action='append', default=[],
                        help='Filtruj po rozszerzeniu pliku (można podać wiele, np. --ext .py --ext .ts). Bez tej flagi skanowane są wszystkie obsługiwane języki.')
    parser.add_argument('--min-count', '-c', type=int, default=2,
                        help='Min. liczba definicji o tej samej nazwie (domyślnie: 2)')
    parser.add_argument('--min-sim', '-s', type=float, default=0.0,
                        help='Min. próg podobieństwa %% dla par (domyślnie: 0 = pokaż wszystkie)')
    parser.add_argument('--preview', type=int, default=6, metavar='LINES',
                        help='Liczba linii podglądu ciała (0 = wyłącz, domyślnie: 6)')
    parser.add_argument('--json', action='store_true',
                        help='Eksport JSON na stdout')
    parser.add_argument('--md', action='store_true',
                        help='Eksport Markdown na stdout')
    parser.add_argument('--no-color', action='store_true',
                        help='Wyłącz kolory ANSI')
    parser.add_argument('--top', type=int, default=0,
                        help='Pokaż tylko TOP N grup (0 = wszystkie)')
    parser.add_argument('--focus', default='',
                        help='Tryb FOCUS: folder źródłowy (np. ./backend) — '
                             'porównuje jego definicje z resztą projektu po nazwie')
    parser.add_argument('--scope', default='',
                        help='Zakres porównania dla --focus (domyślnie: --path)')
    parser.add_argument('--seed', default='',
                        help='Tryb SEED: folder z definicjami bazowymi do similarity globalnej')
    parser.add_argument('--similar-global', action='store_true',
                        help='Razem z --seed: porównuj seed z całym projektem (domyślnie włączone)')
    parser.add_argument('--seed-top', type=int, default=10,
                        help='Liczba najlepszych dopasowań pokazywanych per seed (domyślnie: 10)')
    parser.add_argument('--seed-skip-same-name', action='store_true',
                        help='W trybie SEED ignoruj dopasowania o tej samej nazwie (zostawia tylko ukryte duplikaty)')
    return parser


def _run_seed_mode(args, root: Path, root_str: str, gitignore_patterns, ext_set):
    """Execute SEED mode: global similarity comparison."""
    seed_path = Path(args.seed).resolve()
    if not seed_path.exists():
        print(f"Błąd: seed nie istnieje: {seed_path}", file=sys.stderr)
        sys.exit(1)

    scope_path = Path(args.scope).resolve() if args.scope else root
    min_sim = args.min_sim if args.min_sim > 0 else 60.0

    print(f"Tryb SEED similarity globalna", file=sys.stderr)
    print(f"  Seed:    {seed_path}", file=sys.stderr)
    print(f"  Zakres:  {scope_path}", file=sys.stderr)
    print(f"  min-sim: {min_sim}%  (z --min-sim, domyślnie 60%)", file=sys.stderr)

    full_index = scan(scope_path,
                      name_filter=args.name or None,
                      kind_filter=args.kind or None,
                      gitignore_patterns=gitignore_patterns,
                      gitignore_root=root,
                      ext_filter=ext_set)
    all_defs = [d for defs in full_index.values() for d in defs]

    seed_index = scan(scope_path,
                      name_filter=args.name or None,
                      kind_filter=args.kind or None,
                      only_within=seed_path,
                      gitignore_patterns=gitignore_patterns,
                      gitignore_root=root,
                      ext_filter=ext_set)
    seed_defs = [d for defs in seed_index.values() for d in defs]

    print(f"  Seed defs: {len(seed_defs)}, all defs: {len(all_defs)}",
          file=sys.stderr)

    results = compare_seed_to_all(
        seed_defs, all_defs, min_sim,
        skip_same_name=args.seed_skip_same_name,
    )

    if args.top:
        results = results[:args.top]

    if not results:
        print("Brak dopasowań spełniających kryteria.", file=sys.stderr)
        return

    if args.json:
        print(render_seed_json(results, root_str))
    elif args.md:
        print(render_seed_markdown(results, root_str,
                                   top_per_seed=args.seed_top))
    else:
        print(render_seed_text(results, root_str,
                               top_per_seed=args.seed_top,
                               show_body_lines=args.preview))

    n_total = sum(len(m) for _, m in results)
    print(f"\nPodsumowanie SEED:", file=sys.stderr)
    print(f"  Seedów z dopasowaniami: {len(results)}", file=sys.stderr)
    print(f"  Łączna liczba dopasowań: {n_total}", file=sys.stderr)


def _build_focus_groups(
    focus_index: dict, full_index: dict, min_count: int
) -> list[tuple[str, list]]:
    """Build groups of definitions that exist in focus and elsewhere."""
    groups_raw = []
    for name, focus_defs in focus_index.items():
        other_defs_all = full_index.get(name, [])
        if not other_defs_all:
            continue
        focus_keys = {_def_key(d) for d in focus_defs}
        other_defs = [d for d in other_defs_all if _def_key(d) not in focus_keys]
        if not other_defs:
            continue
        combined = focus_defs + other_defs
        if len(combined) < min_count:
            continue
        groups_raw.append((name, combined))
    return groups_raw


def _analyse_and_sort_groups(groups_raw: list[tuple[str, list]]) -> list[tuple[str, list, list]]:
    """Analyse groups for similarity and sort by size and max similarity."""
    groups_analysed = []
    for name, defs in groups_raw:
        pairs = analyse_group(defs)
        groups_analysed.append((name, defs, pairs))
    groups_analysed.sort(
        key=lambda x: (len(x[1]), max((p['similarity'] for p in x[2]), default=0)),
        reverse=True,
    )
    return groups_analysed


def _run_focus_mode(args, root: Path, root_str: str, gitignore_patterns, ext_set):
    """Execute FOCUS mode: compare folder vs rest of project by name."""
    focus_path = Path(args.focus).resolve()
    if not focus_path.exists():
        print(f"Błąd: focus nie istnieje: {focus_path}", file=sys.stderr)
        sys.exit(1)

    scope_path = Path(args.scope).resolve() if args.scope else root
    print(f"Tryb FOCUS", file=sys.stderr)
    print(f"  Focus: {focus_path}", file=sys.stderr)
    print(f"  Scope: {scope_path}", file=sys.stderr)

    focus_index = scan(scope_path,
                       name_filter=args.name or None,
                       kind_filter=args.kind or None,
                       only_within=focus_path,
                       gitignore_patterns=gitignore_patterns,
                       gitignore_root=root,
                       ext_filter=ext_set)
    full_index = scan(scope_path,
                      name_filter=args.name or None,
                      kind_filter=args.kind or None,
                      gitignore_patterns=gitignore_patterns,
                      gitignore_root=root,
                      ext_filter=ext_set)

    groups_raw = _build_focus_groups(focus_index, full_index, args.min_count)
    groups_analysed = _analyse_and_sort_groups(groups_raw)

    if args.top:
        groups_analysed = groups_analysed[:args.top]

    if not groups_analysed:
        print("Nie znaleziono grup spełniających kryteria (FOCUS).",
              file=sys.stderr)
        return

    print(f"Znaleziono {len(groups_analysed)} grup focus↔reszta.",
          file=sys.stderr)

    if args.json:
        print(render_json(groups_analysed, root_str))
    elif args.md:
        print(render_markdown(groups_analysed, root_str,
                              min_sim=args.min_sim))
    else:
        print(render_text(groups_analysed, root_str,
                          min_sim=args.min_sim,
                          show_body_lines=args.preview))


def _run_default_mode(args, root: Path, root_str: str, gitignore_patterns, ext_set):
    """Execute default mode: find duplicates by name in entire project."""
    print(f"Skanowanie: {root}", file=sys.stderr)
    index = scan(root,
                 name_filter=args.name or None,
                 kind_filter=args.kind or None,
                 gitignore_patterns=gitignore_patterns,
                 gitignore_root=root,
                 ext_filter=ext_set)
    print(f"Znaleziono {sum(len(v) for v in index.values())} definicji "
          f"w {len(index)} unikalnych nazwach.", file=sys.stderr)

    groups_raw = [(name, defs)
                  for name, defs in index.items()
                  if len(defs) >= args.min_count]

    groups_analysed = []
    for name, defs in groups_raw:
        pairs = analyse_group(defs)
        groups_analysed.append((name, defs, pairs))

    groups_analysed.sort(
        key=lambda x: (len(x[1]), max((p['similarity'] for p in x[2]), default=0)),
        reverse=True,
    )

    if args.top:
        groups_analysed = groups_analysed[:args.top]

    if not groups_analysed:
        print("Nie znaleziono grup spełniających kryteria.", file=sys.stderr)
        return

    if args.json:
        print(render_json(groups_analysed, root_str))
    elif args.md:
        print(render_markdown(groups_analysed, root_str, min_sim=args.min_sim))
    else:
        print(render_text(groups_analysed, root_str,
                          min_sim=args.min_sim,
                          show_body_lines=args.preview))

    _print_pair_summary(groups_analysed)


def _count_similarity_levels(pairs: list) -> tuple[int, int, int]:
    """Count pairs by similarity thresholds."""
    identyczne, kopie, podobne = 0, 0, 0
    for p in pairs:
        sim = p['similarity']
        if sim >= 95:
            identyczne += 1
        elif sim >= 75:
            kopie += 1
        elif sim >= 50:
            podobne += 1
    return identyczne, kopie, podobne


def _print_pair_summary(groups_analysed: list) -> None:
    """Print summary of similarity levels across all groups."""
    total_identyczne = 0
    total_kopie = 0
    total_podobne = 0
    for _, _, pairs in groups_analysed:
        i, k, p = _count_similarity_levels(pairs)
        total_identyczne += i
        total_kopie += k
        total_podobne += p

    print(f"\nPodsumowanie par:", file=sys.stderr)
    print(f"  Identyczne (≥95%):   {total_identyczne}", file=sys.stderr)
    print(f"  Prawie kopie (≥75%): {total_kopie}", file=sys.stderr)
    print(f"  Podobne (≥50%):      {total_podobne}", file=sys.stderr)


def main():
    parser = _build_argument_parser()
    args = parser.parse_args()

    global USE_COLOR
    if args.no_color or args.json or args.md:
        USE_COLOR = False

    root = Path(args.path).resolve()
    if not root.exists():
        print(f"Błąd: katalog nie istnieje: {root}", file=sys.stderr)
        sys.exit(1)

    root_str = str(root)
    gitignore_patterns = load_gitignore(root)
    ext_set = set(args.ext) if args.ext else None

    if args.seed:
        _run_seed_mode(args, root, root_str, gitignore_patterns, ext_set)
    elif args.focus:
        _run_focus_mode(args, root, root_str, gitignore_patterns, ext_set)
    else:
        _run_default_mode(args, root, root_str, gitignore_patterns, ext_set)


if __name__ == '__main__':
    main()