#!/usr/bin/env python3
"""
Narzędzie do analizy kodu przy refaktoryzacji.
Zero zewnętrznych zależności — tylko Python 3.10+ stdlib.

TRYBY:
  find       – wyszukaj słowo (rozmiar, linie, JSON)
  duplicates – identyczne pliki (MD5)
  similar    – częściowe duplikaty treści (difflib, opcja --normalize)
  cluster    – grupowanie po prefixach nazw
  deps       – graf importów / zależności
  symbols    – indeks funkcji/klas/selektorów; znajdź kto co definiuje
  wrappers   – wykryj cienkie pliki delegujące do innych (legacy shims)
  dead       – symbole zdefiniowane ale nigdzie nieużywane
  diff       – unified diff dwóch podobnych plików
  hotmap     – mapa katalogów: gdzie jest najwięcej duplikacji
  report     – pełny raport JSON dla LLM

PRZYKŁADY:
  python refactor.py find encoder
  python refactor.py symbols encoder --kind function
  python refactor.py symbols --cross-lang encoder  # ta sama nazwa w py+ts
  python refactor.py symbols --find-dups encoder   # zdefiniowane wielokrotnie
  python refactor.py wrappers
  python refactor.py dead encoder
  python refactor.py diff services/a.py services/b.py --normalize
  python refactor.py similar encoder --normalize --min-sim 55
  python refactor.py hotmap encoder
  python refactor.py report encoder --out enc.json --preview --normalize
"""

import ast
import hashlib
import json
import re
import sys
import argparse
from collections import defaultdict
from pathlib import Path
from difflib import SequenceMatcher, unified_diff
from typing import Optional, Any

# ---------------------------------------------------------------------------
# Stałe
# ---------------------------------------------------------------------------

DEFAULT_EXTENSIONS = {
    '.py', '.ts', '.js', '.jsx', '.tsx', '.java', '.go', '.rs',
    '.c', '.cpp', '.h', '.hpp',
    '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
    '.md', '.txt', '.rst',
    '.html', '.css', '.scss', '.less', '.vue', '.svelte',
}

IGNORED_DIRS = {
    '.git', '.github', '__pycache__', 'node_modules', '.venv', 'venv', 'env',
    'dist', 'build', 'target', 'out', '.next', '.nuxt',
    'coverage', '.pytest_cache', '.mypy_cache', '_archive', '.cache',
}

IMPORT_PATTERNS = [
    r'^\s*(?:from|import)\s+([\w./]+)',
    r'''\b(?:import|require)\b\s*(?:\(?\s*['"]([^'"\n\r]+)['"]\s*\)?|[^'"\n\r]+\s+from\s+['"]([^'"\n\r]+)['"])''',
    r'''<script[^>]+src=['"]([^'"\n\r]+)['"]''',
    r'''@import\s+['"]([^'"\n\r]+)['"]''',
]

# Wzorce ekstrakcji symboli wg języka
# Każdy wpis: (regex, group_index, kind_label)
SYMBOL_PATTERNS: dict[str, list[tuple[str, int, str]]] = {
    '.py': [
        (r'^def\s+(\w+)\s*\(', 1, 'function'),
        (r'^class\s+(\w+)\s*[:(]', 1, 'class'),
        (r'^(\w+)\s*=\s*', 1, 'variable'),
        (r'^\s{4}def\s+(\w+)\s*\(', 1, 'method'),
    ],
    '.ts': [
        (r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*[(<]', 1, 'function'),
        (r'(?:export\s+)?(?:abstract\s+)?class\s+(\w+)', 1, 'class'),
        (r'(?:export\s+)?interface\s+(\w+)', 1, 'interface'),
        (r'(?:export\s+)?type\s+(\w+)\s*=', 1, 'type'),
        (r'(?:export\s+)?const\s+(\w+)\s*[:=]', 1, 'const'),
        (r'^\s+(?:private|public|protected|readonly)?\s+(\w+)\s*[:(]', 1, 'method'),
    ],
    '.js': [
        (r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*[(<]', 1, 'function'),
        (r'(?:export\s+)?class\s+(\w+)', 1, 'class'),
        (r'(?:export\s+)?const\s+(\w+)\s*=', 1, 'const'),
        (r'(?:module\.exports\.(\w+))', 1, 'export'),
    ],
    '.css': [
        (r'([\w#.\-\[\]:>+~@][^\{]{0,80})\{', 1, 'selector'),
    ],
    '.scss': [
        (r'^\s*(@mixin\s+[\w-]+)', 1, 'mixin'),
        (r'^\s*(@function\s+[\w-]+)', 1, 'function'),
        (r'([\w#.\-\[\]:>+~@&][^\{]{0,80})\{', 1, 'selector'),
    ],
    '.html': [
        (r'\bid=["\'](\w[\w-]*)["\']', 1, 'id'),
        (r'<(\w[\w-]*)', 1, 'element'),
    ],
    '.go': [
        (r'^func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\(', 1, 'function'),
        (r'^type\s+(\w+)\s+struct', 1, 'struct'),
        (r'^type\s+(\w+)\s+interface', 1, 'interface'),
    ],
    '.rs': [
        (r'^(?:pub\s+)?fn\s+(\w+)\s*[(<]', 1, 'function'),
        (r'^(?:pub\s+)?struct\s+(\w+)', 1, 'struct'),
        (r'^(?:pub\s+)?trait\s+(\w+)', 1, 'trait'),
        (r'^(?:pub\s+)?enum\s+(\w+)', 1, 'enum'),
    ],
}

# Rozszerzenia dziedziczące wzorce
SYMBOL_PATTERNS['.jsx'] = SYMBOL_PATTERNS['.js']
SYMBOL_PATTERNS['.tsx'] = SYMBOL_PATTERNS['.ts']
SYMBOL_PATTERNS['.less'] = SYMBOL_PATTERNS['.css']
SYMBOL_PATTERNS['.vue'] = SYMBOL_PATTERNS['.ts'] + SYMBOL_PATTERNS['.css']
SYMBOL_PATTERNS['.svelte'] = SYMBOL_PATTERNS['.ts'] + SYMBOL_PATTERNS['.css']

# Heurystyki wrapperów
WRAPPER_SIGNATURES = [
    r'[Ll]egacy\s+(?:compatibility\s+)?wrapper',
    r'[Cc]ompatibility\s+wrapper',
    r'[Ll]egacy\s+shim',
    r'[Ff]orwarding\s+to',
    r'delegates?\s+to',
    r're-?export',
    r'barrel\s+file',
    r'export\s*\*\s*from',
    r'module\.exports\s*=\s*require',
    r'sys\.path\.insert',
    r'sys\.path\.append',
    r'importlib\.util\.spec_from_file_location',
    r'runpy\.run_path',
]

# ---------------------------------------------------------------------------
# Pomocnicze
# ---------------------------------------------------------------------------

def iter_files(root: Path, extensions=None, word_filter: Optional[str] = None,
               case_sensitive: bool = False,
               ext_filter: Optional[set] = None) -> list[Path]:
    """Iterate over files in root, applying various filters."""
    exts = ext_filter or extensions or DEFAULT_EXTENSIONS
    result = []
    for p in root.rglob('*'):
        if not _is_valid_file(p, exts):
            continue
        if word_filter and not _file_contains_word(p, word_filter, case_sensitive):
            continue
        result.append(p)
    return result


def _is_valid_file(p: Path, exts: set) -> bool:
    """Check if path is a valid file (not directory, not ignored, correct extension)."""
    if not p.is_file():
        return False
    if any(part in IGNORED_DIRS for part in p.parts):
        return False
    if any(part.startswith('.') for part in p.parts):
        return False
    if p.suffix.lower() not in exts:
        return False
    return True


def _file_contains_word(p: Path, word_filter: str, case_sensitive: bool) -> bool:
    """Check if file content contains the specified word."""
    try:
        content = p.read_text(encoding='utf-8', errors='ignore')
        needle = word_filter if case_sensitive else word_filter.lower()
        hay = content if case_sensitive else content.lower()
        return needle in hay
    except Exception:
        return False


def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return ''


def md5_file(p: Path) -> str:
    h = hashlib.md5()
    try:
        h.update(p.read_bytes())
    except Exception:
        pass
    return h.hexdigest()


def count_word(text: str, word: str, case_sensitive: bool = False) -> int:
    if not case_sensitive:
        text = text.lower()
        word = word.lower()
    return text.split().count(word)


def line_count(text: str) -> int:
    return text.count('\n') + 1 if text else 0


def similarity_ratio(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio() * 100


def normalize_code(text: str, ext: str) -> str:
    """
    Normalizuje kod przed porównaniem:
    - usuwa komentarze blokowe /* ... */ i jednolinijkowe // ...  # ...
    - zastępuje literały stringów placeholderem "S"
    - normalizuje białe znaki do pojedynczej spacji
    Dzięki temu similar --normalize wykrywa tę samą logikę z innymi nazwami zmiennych.
    """
    text = re.sub(r'/\*.*?\*/', ' ', text, flags=re.DOTALL)
    text = re.sub(r'//[^\n]*', ' ', text)
    text = re.sub(r'#[^\n]*', ' ', text)
    text = re.sub(r'''(['"`])(?:\\.|(?!\1).)*?\1''', '"S"', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def rel(p: Path, root: Path) -> str:
    try:
        return str(p.relative_to(root))
    except ValueError:
        return str(p)


def name_prefix(name: str, depth: int = 2) -> str:
    stem = Path(name).stem
    parts = re.split(r'[-_.]', stem)
    return '-'.join(parts[:depth]) if len(parts) >= depth else stem


def extract_imports(text: str) -> list[str]:
    found = []
    for pat in IMPORT_PATTERNS:
        for m in re.finditer(pat, text, re.MULTILINE):
            for g in m.groups():
                if g:
                    found.append(g.strip())
    return list(set(found))


# ---------------------------------------------------------------------------
# Ekstrakcja symboli
# ---------------------------------------------------------------------------

def extract_symbols_ast(text: str, filepath: str) -> list[dict]:
    """Dla Pythona używa modułu ast — precyzyjniejsze niż regex."""
    try:
        tree = ast.parse(text, filename=filepath)
    except SyntaxError:
        return []
    symbols = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols.append({'name': node.name, 'kind': 'function', 'line': node.lineno})
        elif isinstance(node, ast.ClassDef):
            symbols.append({'name': node.name, 'kind': 'class', 'line': node.lineno})
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    symbols.append({'name': item.name, 'kind': 'method', 'line': item.lineno})
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    symbols.append({'name': target.id, 'kind': 'variable', 'line': node.lineno})
    return symbols


def extract_symbols_regex(text: str, ext: str) -> list[dict]:
    """Wyciąga symbole wg wzorców dla danego języka."""
    patterns = SYMBOL_PATTERNS.get(ext.lower(), [])
    symbols = []
    seen = set()
    for lineno, line in enumerate(text.splitlines(), 1):
        for pattern, group, kind in patterns:
            m = re.search(pattern, line)
            if m:
                name = m.group(group).strip()
                if name and len(name) > 1:
                    key = (name, kind, lineno)
                    if key not in seen:
                        seen.add(key)
                        symbols.append({'name': name, 'kind': kind, 'line': lineno})
    return symbols


def get_symbols(p: Path, text: str) -> list[dict]:
    ext = p.suffix.lower()
    if ext == '.py':
        syms = extract_symbols_ast(text, str(p))
        if syms:
            return syms
    return extract_symbols_regex(text, ext)


# ---------------------------------------------------------------------------
# Wrapper score
# ---------------------------------------------------------------------------

def wrapper_score(text: str) -> dict:
    """
    Heurystyczna ocena czy plik jest wrapperem/shimem.
    Score 0–100: im wyższy, tym bardziej prawdopodobne.
    """
    reasons = []
    score = 0

    score, reasons = _check_wrapper_signatures(text, score, reasons)
    score, reasons = _check_file_length(text, score, reasons)
    score, reasons = _check_import_density(text, score, reasons)
    score, reasons = _check_sys_manipulation(text, score, reasons)
    score, reasons = _check_barrel_export(text, score, reasons)
    score, reasons = _check_dynamic_import(text, score, reasons)

    return {'score': min(score, 100), 'reasons': reasons}


def _check_wrapper_signatures(text: str, score: int, reasons: list) -> tuple[int, list]:
    """Check for wrapper signatures in text."""
    for sig in WRAPPER_SIGNATURES:
        if re.search(sig, text, re.IGNORECASE):
            score += 30
            reasons.append(f'signature: {sig[:50]}')
            break
    return score, reasons


def _check_file_length(text: str, score: int, reasons: list) -> tuple[int, list]:
    """Check if file is short (likely a wrapper)."""
    non_blank = [l for l in text.splitlines() if l.strip()]
    if len(non_blank) < 50:
        score += 20
        reasons.append(f'short ({len(non_blank)} non-blank lines)')
    return score, reasons


def _check_import_density(text: str, score: int, reasons: list) -> tuple[int, list]:
    """Check if file is import-dense."""
    non_blank = [l for l in text.splitlines() if l.strip()]
    import_lines = [l for l in text.splitlines()
                    if re.match(r'^\s*(import|from|require|export \* from)', l)]
    if non_blank and len(import_lines) / max(len(non_blank), 1) > 0.4:
        score += 25
        reasons.append(f'import-dense ({len(import_lines)}/{len(non_blank)} lines)')
    return score, reasons


def _check_sys_manipulation(text: str, score: int, reasons: list) -> tuple[int, list]:
    """Check for sys.path/modules manipulation."""
    if 'sys.path' in text or 'sys.modules' in text:
        score += 20
        reasons.append('sys.path/modules manipulation')
    return score, reasons


def _check_barrel_export(text: str, score: int, reasons: list) -> tuple[int, list]:
    """Check for barrel export pattern."""
    if re.search(r'export\s*\*\s*from', text):
        score += 35
        reasons.append('barrel export (* from)')
    return score, reasons


def _check_dynamic_import(text: str, score: int, reasons: list) -> tuple[int, list]:
    """Check for dynamic import patterns."""
    if 'runpy' in text or 'importlib' in text:
        score += 25
        reasons.append('dynamic import (runpy/importlib)')
    return score, reasons


# ---------------------------------------------------------------------------
# Tryby
# ---------------------------------------------------------------------------

def cmd_find(args, root: Path):
    files = iter_files(root, word_filter=args.word,
                       case_sensitive=getattr(args, 'case_sensitive', False))
    results = []
    for p in files:
        text = read_text(p)
        cnt = count_word(text, args.word, getattr(args, 'case_sensitive', False))
        results.append({
            'path': rel(p, root), 'word_count': cnt,
            'lines': line_count(text), 'size_bytes': p.stat().st_size,
        })
    results.sort(key=lambda x: x['word_count'], reverse=True)

    if args.json:
        print(json.dumps({'word': args.word, 'files': results}, indent=2, ensure_ascii=False))
        return
    print(f"Znaleziono {len(results)} plików zawierających: '{args.word}'")
    print(f"{'Plik':<70} {'Wyst':>5} {'Linie':>7} {'Bajty':>9}")
    print('-' * 95)
    for r in results:
        print(f"{r['path']:<70} {r['word_count']:>5} {r['lines']:>7} {r['size_bytes']:>9}")
    print(f"\nSuma wystąpień: {sum(r['word_count'] for r in results)}")


def cmd_duplicates(args, root: Path):
    word = getattr(args, 'word', '') or ''
    files = iter_files(root, word_filter=word or None)
    hash_map: dict[str, list[str]] = defaultdict(list)
    for p in files:
        hash_map[md5_file(p)].append(rel(p, root))
    groups = {h: paths for h, paths in hash_map.items() if len(paths) > 1}

    if args.json:
        print(json.dumps({'duplicate_groups': list(groups.values())}, indent=2, ensure_ascii=False))
        return
    if not groups:
        print("Nie znaleziono identycznych plików.")
        return
    print(f"Znaleziono {len(groups)} grup identycznych plików:\n")
    for i, (h, paths) in enumerate(groups.items(), 1):
        print(f"Grupa {i} [MD5: {h[:8]}…]")
        for p in paths:
            print(f"  {p}")
        print()


def cmd_similar(args, root: Path):
    word = getattr(args, 'word', '') or ''
    normalize = getattr(args, 'normalize', False)
    files = iter_files(root, word_filter=word or None)
    texts_raw = {rel(p, root): read_text(p) for p in files}
    texts = {k: normalize_code(v, Path(k).suffix) for k, v in texts_raw.items()} \
        if normalize else texts_raw

    threshold = args.min_sim
    paths = list(texts.keys())
    pairs = []
    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            a, b = paths[i], paths[j]
            sim = similarity_ratio(texts[a], texts[b])
            if sim >= threshold:
                pairs.append({
                    'file_a': a, 'file_b': b,
                    'similarity': round(sim, 1),
                    'normalized': normalize,
                })
    pairs.sort(key=lambda x: x['similarity'], reverse=True)

    if args.json:
        print(json.dumps({'threshold': threshold, 'pairs': pairs}, indent=2, ensure_ascii=False))
        return
    if not pairs:
        print(f"Nie znaleziono par z podobieństwem ≥ {threshold}%" +
              (" [znorm.]" if normalize else "") + ".")
        return
    mode = " [znormalizowane — komentarze/stringi usunięte]" if normalize else ""
    print(f"Pary plików ≥ {threshold}%{mode} ({len(pairs)} par):\n")
    print(f"{'Sim%':>6}  {'Plik A':<50}  Plik B")
    print('-' * 120)
    for p in pairs:
        print(f"{p['similarity']:>5}%  {p['file_a']:<50}  {p['file_b']}")


def _build_symbol_index(files, root, kind_filter=''):
    """Build index of symbols by name across all files."""
    index: dict[str, list[dict]] = defaultdict(list)
    file_symbols: dict[str, list[dict]] = {}
    
    for p in files:
        text = read_text(p)
        syms = get_symbols(p, text)
        path_str = rel(p, root)
        file_symbols[path_str] = syms
        for s in syms:
            if kind_filter and s['kind'] != kind_filter:
                continue
            index[s['name']].append({
                'path': path_str, 'kind': s['kind'],
                'line': s['line'], 'ext': p.suffix.lower(),
            })
    
    return index, file_symbols


def _render_cross_lang_symbols(cross_sorted, args):
    """Render cross-language symbols output."""
    if args.json:
        print(json.dumps({'cross_language_symbols': {k: v for k, v in cross_sorted}},
                         indent=2, ensure_ascii=False))
        return
    
    print(f"Symbole w wielu językach ({len(cross_sorted)}):\n")
    for name, defs in cross_sorted[:60]:
        langs = sorted({d['ext'] for d in defs})
        print(f"  {name:<40} [{', '.join(langs)}]")
        for d in defs:
            print(f"    {d['path']}:{d['line']} ({d['kind']})")


def _render_duplicate_symbols(dups_sorted, args):
    """Render duplicate symbols output."""
    if args.json:
        print(json.dumps({'duplicate_symbols': {k: v for k, v in dups_sorted}},
                         indent=2, ensure_ascii=False))
        return
    
    print(f"Symbole zdefiniowane wielokrotnie ({len(dups_sorted)}):\n")
    for name, defs in dups_sorted[:60]:
        kinds = sorted({d['kind'] for d in defs})
        print(f"  {name:<40} ({', '.join(kinds)}) — {len(defs)}×")
        for d in defs:
            print(f"    {d['path']}:{d['line']}")


def _render_file_symbols(file_symbols, kind_filter, args):
    """Render symbols per file output."""
    if args.json:
        print(json.dumps({'file_symbols': file_symbols}, indent=2, ensure_ascii=False))
        return
    
    kind_label = f" [{kind_filter}]" if kind_filter else ""
    print(f"Symbole w plikach{kind_label}:\n")
    for path, syms in sorted(file_symbols.items()):
        filtered = [s for s in syms if not kind_filter or s['kind'] == kind_filter]
        if not filtered:
            continue
        print(f"{path} ({len(filtered)} symboli)")
        for s in filtered[:20]:
            print(f"  {s['line']:>5}  {s['kind']:<12}  {s['name']}")
        if len(filtered) > 20:
            print(f"  … i {len(filtered) - 20} więcej")
        print()


def cmd_symbols(args, root: Path):
    """
    Indeks symboli (funkcje, klasy, selektory CSS, id HTML…).

    --cross-lang   → ta sama nazwa symbolu w więcej niż jednym języku
    --find-dups    → ta sama nazwa w więcej niż jednym pliku
    (bez flag)     → pokaż symbole per plik
    """
    word = getattr(args, 'word', '') or ''
    kind_filter = getattr(args, 'kind', '') or ''
    cross_lang = getattr(args, 'cross_lang', False)
    find_dups = getattr(args, 'find_dups', False)

    files = iter_files(root, word_filter=word or None)
    index, file_symbols = _build_symbol_index(files, root, kind_filter)

    if cross_lang:
        cross = {name: defs for name, defs in index.items()
                 if len({d['ext'] for d in defs}) > 1}
        cross_sorted = sorted(cross.items(),
                              key=lambda x: len({d['ext'] for d in x[1]}), reverse=True)
        _render_cross_lang_symbols(cross_sorted, args)
        return

    if find_dups:
        dups = {name: defs for name, defs in index.items() if len(defs) > 1}
        dups_sorted = sorted(dups.items(), key=lambda x: len(x[1]), reverse=True)
        _render_duplicate_symbols(dups_sorted, args)
        return

    _render_file_symbols(file_symbols, kind_filter, args)


def cmd_wrappers(args, root: Path):
    """
    Wykrywa cienkie pliki-wrappery / legacy shims / barrel files.
    Heurystyki: krótkie + sys.path + dynamic import + barrel export + sygnatury tekstowe.
    """
    word = getattr(args, 'word', '') or ''
    min_score = getattr(args, 'min_score', 40)
    files = iter_files(root, word_filter=word or None)

    results = []
    for p in files:
        text = read_text(p)
        ws = wrapper_score(text)
        if ws['score'] >= min_score:
            results.append({
                'path': rel(p, root),
                'score': ws['score'],
                'reasons': ws['reasons'],
                'lines': line_count(text),
            })
    results.sort(key=lambda x: x['score'], reverse=True)

    if args.json:
        print(json.dumps({'wrappers': results}, indent=2, ensure_ascii=False))
        return
    if not results:
        print(f"Nie znaleziono wrapperów (próg score={min_score}).")
        return
    print(f"Wykryte wrappery / shims / barrels (score ≥ {min_score}):\n")
    print(f"{'Score':>5}  {'Linie':>6}  Plik")
    print('-' * 80)
    for r in results:
        print(f"{r['score']:>5}  {r['lines']:>6}  {r['path']}")
        for reason in r['reasons']:
            print(f"         ↳ {reason}")
    print(f"\nŁącznie: {len(results)} plików")


def cmd_dead(args, root: Path):
    """
    Wykrywa symbole zdefiniowane ale prawdopodobnie nieużywane.
    Definicje: pliki z --word.
    Sprawdzenie: czy symbol pojawia się jako identyfikator w jakimkolwiek innym pliku.

    UWAGA: heurystyka tekstowa — false positives przy dynamicznych wywołaniach.
    """
    word = getattr(args, 'word', '') or ''
    min_len = getattr(args, 'min_len', 4)

    source_files = iter_files(root, word_filter=word or None)
    all_files = iter_files(root)

    defined: dict[str, list[dict]] = defaultdict(list)
    source_paths = set()
    for p in source_files:
        path_str = rel(p, root)
        source_paths.add(path_str)
        text = read_text(p)
        for sym in get_symbols(p, text):
            if len(sym['name']) >= min_len:
                defined[sym['name']].append({
                    'path': path_str, 'kind': sym['kind'], 'line': sym['line'],
                })

    # Corpus referencji (wszystkie pliki poza źródłowymi)
    full_corpus = '\n'.join(
        read_text(p) for p in all_files if rel(p, root) not in source_paths
    )

    dead = []
    for name, defs in defined.items():
        if not re.search(r'\b' + re.escape(name) + r'\b', full_corpus):
            dead.append({'name': name, 'definitions': defs})
    dead.sort(key=lambda x: x['name'])

    if args.json:
        print(json.dumps({'potentially_dead_symbols': dead}, indent=2, ensure_ascii=False))
        return
    if not dead:
        print("Nie znaleziono potencjalnie martwych symboli.")
        return
    print(f"Potencjalnie martwe symbole ({len(dead)}):\n")
    for d in dead:
        print(f"  {d['name']:<40}")
        for df in d['definitions']:
            print(f"    {df['path']}:{df['line']} ({df['kind']})")
    print(f"\nUWAGA: heurystyka tekstowa — weryfikuj przed usunięciem.")


def cmd_diff(args, root: Path):
    """Unified diff dwóch plików. Opcja --normalize usuwa komentarze/stringi."""
    path_a = Path(args.file_a)
    path_b = Path(args.file_b)
    if not path_a.exists():
        path_a = root / args.file_a
    if not path_b.exists():
        path_b = root / args.file_b

    text_a = read_text(path_a)
    text_b = read_text(path_b)
    normalize = getattr(args, 'normalize', False)

    if normalize:
        ext = path_a.suffix
        ta = normalize_code(text_a, ext).splitlines(keepends=True)
        tb = normalize_code(text_b, ext).splitlines(keepends=True)
    else:
        ta = text_a.splitlines(keepends=True)
        tb = text_b.splitlines(keepends=True)

    sim = similarity_ratio(''.join(ta), ''.join(tb))
    diff = list(unified_diff(ta, tb,
                             fromfile=str(args.file_a), tofile=str(args.file_b),
                             n=getattr(args, 'context', 3)))

    if args.json:
        print(json.dumps({
            'file_a': str(args.file_a), 'file_b': str(args.file_b),
            'similarity': round(sim, 1), 'normalized': normalize,
            'diff_lines': len(diff), 'diff': ''.join(diff),
        }, indent=2, ensure_ascii=False))
        return

    mode = " [znormalizowane]" if normalize else ""
    print(f"Diff{mode}: {args.file_a} ↔ {args.file_b}  (podobieństwo: {sim:.1f}%)\n")
    if not diff:
        print("Pliki identyczne.")
        return
    sys.stdout.writelines(diff)


def cmd_hotmap(args, root: Path):
    """
    Mapa katalogów wg koncentracji podobnych plików.
    Wskaźnik 'hotness' = liczba par podobnych / liczba plików w katalogu × 100.
    Wysoki hotness = kandydat do refaktoryzacji.
    """
    word = getattr(args, 'word', '') or ''
    normalize = getattr(args, 'normalize', False)
    threshold = getattr(args, 'min_sim', 60.0)

    texts, paths_list = _collect_and_normalize_files(root, word, normalize)
    dir_file_count = _count_files_per_dir(paths_list)
    dir_pair_count, total_pairs = _count_similar_pairs(
        paths_list, texts, threshold, dir_file_count
    )
    hotmap = _calculate_hotmap(dir_file_count, dir_pair_count)

    _render_hotmap_output(args, hotmap, paths_list, total_pairs, threshold, normalize)


def _collect_and_normalize_files(
    root: Path, word: str, normalize: bool
) -> tuple[dict[str, str], list[str]]:
    """Collect files and optionally normalize their content."""
    files = iter_files(root, word_filter=word or None)
    texts_raw = {rel(p, root): read_text(p) for p in files}
    texts = {k: normalize_code(v, Path(k).suffix) for k, v in texts_raw.items()} \
        if normalize else texts_raw
    return texts, list(texts.keys())


def _count_files_per_dir(paths_list: list[str]) -> dict[str, int]:
    """Count files per directory."""
    dir_file_count: dict[str, int] = defaultdict(int)
    for path in paths_list:
        dir_file_count[str(Path(path).parent)] += 1
    return dir_file_count


def _count_similar_pairs(
    paths_list: list[str],
    texts: dict[str, str],
    threshold: float,
    dir_file_count: dict[str, int],
) -> tuple[dict[str, int], int]:
    """Count similar file pairs per directory."""
    dir_pair_count: dict[str, int] = defaultdict(int)
    total_pairs = 0

    if len(paths_list) > 300:
        return dir_pair_count, total_pairs

    for i in range(len(paths_list)):
        for j in range(i + 1, len(paths_list)):
            a, b = paths_list[i], paths_list[j]
            sim = similarity_ratio(texts[a], texts[b])
            if sim >= threshold:
                total_pairs += 1
                da, db = str(Path(a).parent), str(Path(b).parent)
                dir_pair_count[da] += 1
                if da != db:
                    dir_pair_count[db] += 1

    return dir_pair_count, total_pairs


def _calculate_hotmap(
    dir_file_count: dict[str, int], dir_pair_count: dict[str, int]
) -> list[dict]:
    """Calculate hotness percentage for each directory."""
    hotmap = []
    for d, fc in dir_file_count.items():
        pairs = dir_pair_count.get(d, 0)
        hotmap.append({
            'dir': d, 'files': fc, 'similar_pairs': pairs,
            'hotness_pct': round(pairs / max(fc, 1) * 100, 1),
        })
    hotmap.sort(key=lambda x: x['similar_pairs'], reverse=True)
    return hotmap


def _render_hotmap_output(
    args, hotmap: list[dict], paths_list: list[str],
    total_pairs: int, threshold: float, normalize: bool
) -> None:
    """Render hotmap output in JSON or text format."""
    if args.json:
        print(json.dumps({
            'total_files': len(paths_list), 'total_similar_pairs': total_pairs,
            'threshold': threshold, 'dirs': hotmap,
        }, indent=2, ensure_ascii=False))
        return

    print(f"Mapa duplikacji (próg: {threshold}%, {'znorm.' if normalize else 'surowe'}):\n")
    print(f"{'Katalog':<55} {'Pliki':>6} {'Pary':>6} {'Hot%':>7}")
    print('-' * 80)
    for h in hotmap:
        bar = '█' * min(int(h['hotness_pct'] / 10), 20)
        print(f"{h['dir']:<55} {h['files']:>6} {h['similar_pairs']:>6} "
              f"{h['hotness_pct']:>6}% {bar}")
    print(f"\nŁącznie: {len(paths_list)} plików, {total_pairs} par podobnych")


def cmd_cluster(args, root: Path):
    word = getattr(args, 'word', '') or ''
    depth = getattr(args, 'depth', 2)
    files = iter_files(root, word_filter=word or None)
    clusters: dict[str, list[dict]] = defaultdict(list)
    for p in files:
        text = read_text(p)
        clusters[name_prefix(p.name, depth)].append({
            'path': rel(p, root), 'lines': line_count(text), 'size_bytes': p.stat().st_size,
        })
    sorted_clusters = sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True)

    if args.json:
        out = {k: v for k, v in sorted_clusters if len(v) >= args.min_group}
        print(json.dumps({'clusters': out}, indent=2, ensure_ascii=False))
        return
    print(f"Klastry nazw plików (prefix głębokość={depth}, min. {args.min_group}):\n")
    for prefix, members in sorted_clusters:
        if len(members) < args.min_group:
            continue
        tl = sum(m['lines'] for m in members)
        tb = sum(m['size_bytes'] for m in members)
        print(f"[{prefix}] — {len(members)} plików, {tl} linii, {tb} bajtów")
        for m in sorted(members, key=lambda x: x['path']):
            print(f"  {m['path']:<70} {m['lines']:>6} linii")
        print()


def _deps_filter_by_word(import_map: dict[str, list[str]], word: str) -> tuple[list, list]:
    """Filter import map by a search word."""
    importers, targets = [], []
    for path, imports in import_map.items():
        matched = [i for i in imports if word.lower() in i.lower()]
        if matched:
            importers.append({'file': path, 'imports': matched})
        if word.lower() in path.lower():
            targets.append({'file': path, 'imports': import_map[path]})
    return importers, targets


def _deps_print_word_results(word: str, targets: list, importers: list) -> None:
    """Print dependency results filtered by word."""
    print(f"=== Pliki z '{word}' w nazwie ===")
    for t in targets:
        print(f"\n  {t['file']}")
        if t['imports']:
            print(f"  importuje: {', '.join(t['imports'][:10])}")
    print(f"\n=== Pliki importujące '{word}' ===")
    for im in importers:
        print(f"\n  {im['file']}")
        for i in im['imports']:
            print(f"    -> {i}")


def _deps_print_all(import_map: dict[str, list[str]]) -> None:
    """Print full dependency map."""
    for path, imports in sorted(import_map.items()):
        if imports:
            print(f"{path}")
            for i in imports:
                print(f"  -> {i}")


def cmd_deps(args, root: Path):
    word = getattr(args, 'word', '') or ''
    files = iter_files(root)
    import_map: dict[str, list[str]] = {}
    for p in files:
        import_map[rel(p, root)] = extract_imports(read_text(p))

    if word:
        importers, targets = _deps_filter_by_word(import_map, word)
        if args.json:
            print(json.dumps({
                'word': word,
                'files_containing_word': targets,
                'files_importing_word': importers,
            }, indent=2, ensure_ascii=False))
            return
        _deps_print_word_results(word, targets, importers)
    else:
        if args.json:
            print(json.dumps({'import_map': import_map}, indent=2, ensure_ascii=False))
        else:
            _deps_print_all(import_map)


def _sanitize(value: str) -> str:
    """Sanitize string for toon format by escaping newlines and commas."""
    return value.replace(',', ';').replace('\n', '↵ ').replace('\r', '↵ ').replace('\f', '↵ ').replace('\v', '↵ ')


def _format_imports(raw_imports: list) -> str:
    """Format imports list for toon output."""
    imports = [_sanitize(str(i)).strip() for i in raw_imports if _sanitize(str(i)).strip()]
    if imports:
        return f"[{len(imports)}]:" + ','.join(imports[:5])
    return "[0]:"


def _format_preview(raw_preview: Any, max_len: int = 200) -> str:
    """Format preview text for toon output."""
    if not isinstance(raw_preview, str) or not raw_preview:
        return ''
    preview_escaped = _sanitize(raw_preview)
    if len(preview_escaped) > max_len:
        preview_escaped = preview_escaped[:max_len] + '…'
    return preview_escaped


def _toon_meta_section(meta: dict) -> list[str]:
    """Render meta section for toon format."""
    lines = []
    for key, value in meta.items():
        if isinstance(value, bool):
            value = 'true' if value else 'false'
        lines.append(f"{key}: {value}")
    lines.append('')
    return lines


def _toon_files_section(files: list) -> list[str]:
    """Render files section for toon format."""
    if not files:
        return []
    lines = []
    file_fields = ','.join(files[0].keys())
    lines.append(f"files[{len(files)}]{{{file_fields}}}:")
    for f in files:
        path = f.get('path', '')
        word_count = f.get('word_count', 0)
        lines_count = f.get('lines', 0)
        size_bytes = f.get('size_bytes', 0)
        imports_str = _format_imports(f.get('imports', []))
        preview_escaped = _format_preview(f.get('preview', '') or '')
        lines.append(f"  {path},{word_count},{lines_count},{size_bytes},{imports_str},{preview_escaped}")
    lines.append('')
    return lines


def _toon_clusters_section(clusters: dict) -> list[str]:
    """Render name_clusters section for toon format."""
    if not clusters:
        return []
    lines = []
    lines.append(f"name_clusters[{len(clusters)}]:")
    for cluster_name, cluster_files in clusters.items():
        files_list = ','.join(cluster_files)
        lines.append(f"  - {cluster_name}: files[{len(cluster_files)}]: {files_list}")
    lines.append('')
    return lines


def _toon_similar_pairs_section(similar_pairs: list) -> list[str]:
    """Render similar_pairs section for toon format."""
    if not similar_pairs or not isinstance(similar_pairs, list) or not similar_pairs:
        return []
    if not isinstance(similar_pairs[0], dict):
        return []
    lines = []
    pair_fields = ','.join(similar_pairs[0].keys())
    lines.append(f"similar_pairs[{len(similar_pairs)}]{{{pair_fields}}}:")
    for pair in similar_pairs:
        if isinstance(pair, dict):
            file_a = pair.get('file_a', '')
            file_b = pair.get('file_b', '')
            similarity = pair.get('similarity', 0)
            lines.append(f"  {file_a},{file_b},{similarity}")
    lines.append('')
    return lines


def _toon_llm_hint(llm_hint: str) -> list[str]:
    """Render LLM prompt hint for toon format."""
    if not llm_hint:
        return []
    return [f'llm_prompt_hint: "{llm_hint}"']


def to_json_toon(data: dict) -> str:
    """Konwertuje dict do formatu toon (YAML-like)."""
    lines = []
    lines.extend(_toon_meta_section(data.get('meta', {})))
    lines.extend(_toon_files_section(data.get('files', [])))
    lines.extend(_toon_clusters_section(data.get('name_clusters', {})))
    lines.extend(_toon_similar_pairs_section(data.get('similar_pairs', [])))
    lines.extend(_toon_llm_hint(data.get('llm_prompt_hint', '')))
    return '\n'.join(lines)


def _collect_file_infos(files, root, word, args, max_preview=2000):
    """Collect file information including word count, symbols, and wrapper score."""
    file_infos, texts = [], {}
    for p in files:
        text = read_text(p)
        texts[rel(p, root)] = text
        cnt = count_word(text, word)
        syms = get_symbols(p, text)
        ws = wrapper_score(text)
        preview = (text[:max_preview] + '…') if len(text) > max_preview else text
        file_infos.append({
            'path': rel(p, root),
            'word_count': cnt,
            'lines': line_count(text),
            'size_bytes': p.stat().st_size,
            'imports': extract_imports(text)[:20],
            'symbols': [s['name'] for s in syms
                        if s['kind'] in ('function', 'class', 'method')][:20],
            'wrapper_score': ws['score'],
            'wrapper_reasons': ws['reasons'],
            'preview': preview.replace('\n', '↵ ') if getattr(args, 'preview', False) else None,
        })
    file_infos.sort(key=lambda x: x['word_count'], reverse=True)
    return file_infos, texts


def _find_md5_duplicates(texts):
    """Find duplicate files by MD5 hash."""
    hash_map: dict[str, list[str]] = defaultdict(list)
    for path, text in texts.items():
        hash_map[hashlib.md5(text.encode()).hexdigest()].append(path)
    return [paths for paths in hash_map.values() if len(paths) > 1]


def _find_name_clusters(texts, depth=2, top_n=30):
    """Find files with similar name prefixes."""
    clusters: dict[str, list[str]] = defaultdict(list)
    for path in texts:
        clusters[name_prefix(Path(path).name, depth)].append(path)
    top_clusters = sorted(
        {k: v for k, v in clusters.items() if len(v) >= 2}.items(),
        key=lambda x: len(x[1]), reverse=True,
    )[:top_n]
    return dict(top_clusters)


def _find_similar_pairs(texts, normalize, threshold, max_files=200, max_pairs=50):
    """Find similar file pairs based on content similarity."""
    texts_cmp = {k: normalize_code(v, Path(k).suffix) for k, v in texts.items()} \
        if normalize else texts
    paths_list = list(texts_cmp.keys())
    similar_pairs = []
    if len(paths_list) <= max_files:
        for i in range(len(paths_list)):
            for j in range(i + 1, len(paths_list)):
                a, b = paths_list[i], paths_list[j]
                sim = similarity_ratio(texts_cmp[a], texts_cmp[b])
                if sim >= threshold:
                    similar_pairs.append({'file_a': a, 'file_b': b, 'similarity': round(sim, 1)})
        similar_pairs.sort(key=lambda x: x['similarity'], reverse=True)
        similar_pairs = similar_pairs[:max_pairs]
    else:
        similar_pairs = [{'note': f'Za dużo plików ({len(paths_list)}) — użyj similar --word'}]
    return similar_pairs


def _find_duplicate_symbols(files, root, top_n=30):
    """Find symbols defined in multiple files."""
    sym_index: dict[str, list[dict]] = defaultdict(list)
    for p in files:
        text = read_text(p)
        for s in get_symbols(p, text):
            sym_index[s['name']].append({
                'path': rel(p, root), 'kind': s['kind'], 'line': s['line'],
            })
    dup_symbols = sorted(
        [{'name': k, 'defs': v} for k, v in sym_index.items() if len(v) > 1],
        key=lambda x: len(x['defs']), reverse=True,
    )[:top_n]
    return dup_symbols, sym_index


def _find_cross_language_symbols(sym_index, top_n=20):
    """Find symbols defined in multiple languages."""
    sym_cross = []
    for name, defs in sym_index.items():
        langs = {Path(d['path']).suffix for d in defs}
        if len(langs) > 1:
            sym_cross.append({'name': name, 'langs': sorted(langs), 'defs': defs})
    sym_cross.sort(key=lambda x: len(x['langs']), reverse=True)
    return sym_cross[:top_n]


def _find_external_importers(files, root, word):
    """Find files outside the matched set that import the word."""
    source_paths = {rel(p, root) for p in files}
    importers = []
    for p in iter_files(root):
        path_str = rel(p, root)
        if path_str in source_paths:
            continue
        matched = [i for i in extract_imports(read_text(p)) if word.lower() in i.lower()]
        if matched:
            importers.append({'file': path_str, 'matched_imports': matched})
    return importers[:30]


def _build_report(word, root, file_infos, dup_groups, top_clusters, 
                  similar_pairs, wrappers_found, dup_symbols, sym_cross, 
                  importers, threshold, normalize):
    """Build the complete report structure."""
    return {
        'meta': {
            'word': word,
            'root': str(root),
            'total_files_with_word': len(file_infos),
            'total_word_occurrences': sum(f['word_count'] for f in file_infos),
            'duplicate_groups_md5': len(dup_groups),
            'similar_pairs_above_threshold': len(similar_pairs),
            'similarity_threshold': threshold,
            'normalized_similarity': normalize,
            'wrappers_found': len(wrappers_found),
            'duplicate_symbol_names': len(dup_symbols),
            'cross_language_symbols': len(sym_cross),
        },
        'files': file_infos,
        'duplicate_groups': dup_groups,
        'name_clusters': top_clusters,
        'similar_pairs': similar_pairs,
        'wrappers': [{'path': w['path'], 'score': w['wrapper_score'],
                      'reasons': w['wrapper_reasons']} for w in wrappers_found],
        'duplicate_symbols': dup_symbols,
        'cross_language_symbols': sym_cross,
        'external_importers': importers,
        'llm_prompt_hint': (
            f"Raport analizy kodu dla: '{word}'. "
            f"{len(file_infos)} plików, {len(dup_groups)} grup duplikatów MD5, "
            f"{len(similar_pairs)} par podobnych (próg {threshold}%, "
            f"{'znormalizowane' if normalize else 'surowe'}), "
            f"{len(wrappers_found)} wrapperów/shimów, "
            f"{len(dup_symbols)} zduplikowanych symboli, "
            f"{len(sym_cross)} symboli cross-language. "
            f"Zaproponuj refaktoryzację: które pliki scalić, które usunąć, "
            f"jak ujednolicić nazewnictwo i symbole."
        ),
    }


def _save_report(report, out_path, toon_format, word):
    """Save report to file in JSON or TOON format."""
    if toon_format:
        toon_content = f"# Refactor Analysis Report: {word}\n"
        toon_content += "# Generated by refactor.py\n\n"
        toon_content += to_json_toon(report)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(toon_content)
        print(f"\n✅  Raport toon: {out_path}", file=sys.stderr)
    else:
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n✅  Raport: {out_path}", file=sys.stderr)
    
    for k, v in report['meta'].items():
        print(f"   {k}: {v}", file=sys.stderr)


def cmd_report(args, root: Path):
    """Generuje kompleksowy raport JSON dla LLM."""
    word = args.word
    normalize = getattr(args, 'normalize', False)
    toon_format = getattr(args, 'toon', False)
    threshold = getattr(args, 'min_sim', 60.0)
    print(f"Generowanie raportu dla: '{word}'…", file=sys.stderr)

    files = iter_files(root, word_filter=word)
    file_infos, texts = _collect_file_infos(files, root, word, args)
    
    dup_groups = _find_md5_duplicates(texts)
    top_clusters = _find_name_clusters(texts)
    similar_pairs = _find_similar_pairs(texts, normalize, threshold)
    wrappers_found = [f for f in file_infos if f['wrapper_score'] >= 40]
    dup_symbols, sym_index = _find_duplicate_symbols(files, root)
    sym_cross = _find_cross_language_symbols(sym_index)
    importers = _find_external_importers(files, root, word)

    report = _build_report(word, root, file_infos, dup_groups, top_clusters,
                          similar_pairs, wrappers_found, dup_symbols, sym_cross,
                          importers, threshold, normalize)

    out_path = getattr(args, 'out', None) or f'refactor-report-{word}.json'
    _save_report(report, out_path, toon_format, word)

    if getattr(args, 'json', False) and not toon_format:
        print(json.dumps(report, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser():
    p = argparse.ArgumentParser(
        description='refactor.py — analiza kodu przy refaktoryzacji',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument('--path', '-p', default='.', help='Katalog główny projektu')
    p.add_argument('--json', action='store_true', help='Wyjście JSON na stdout')
    p.add_argument('--extensions', '-e', nargs='+', help='Filtr rozszerzeń (.py .ts …)')
    sub = p.add_subparsers(dest='cmd', required=True)

    def word_arg(sp, required=False):
        sp.add_argument('word', nargs=(None if required else '?'), default='',
                        help='Filtruj pliki zawierające to słowo')

    # find
    pf = sub.add_parser('find', help='Wyszukaj słowo w plikach')
    pf.add_argument('word')
    pf.add_argument('-c', '--case-sensitive', action='store_true')

    # duplicates
    pd = sub.add_parser('duplicates', help='Identyczne pliki (MD5 hash)')
    word_arg(pd)

    # similar
    ps = sub.add_parser('similar', help='Częściowe duplikaty treści (difflib)')
    word_arg(ps)
    ps.add_argument('--min-sim', type=float, default=60.0, metavar='PCT')
    ps.add_argument('--normalize', action='store_true',
                    help='Usuń komentarze i stringi przed porównaniem')

    # cluster
    pc = sub.add_parser('cluster', help='Grupuj pliki po prefixie nazwy')
    word_arg(pc)
    pc.add_argument('--depth', type=int, default=2, help='Głębokość prefixu (segmenty nazwy)')
    pc.add_argument('--min-group', type=int, default=2, help='Min. pliki w grupie')

    # deps
    pdep = sub.add_parser('deps', help='Graf importów / zależności')
    word_arg(pdep)

    # symbols  ← NOWY
    psym = sub.add_parser('symbols',
                          help='Indeks symboli: funkcje, klasy, selektory CSS, id HTML')
    word_arg(psym)
    psym.add_argument('--kind', default='',
                      help='function|class|method|interface|type|const|selector|id|…')
    psym.add_argument('--cross-lang', action='store_true',
                      help='Pokaż symbole zdefiniowane w więcej niż jednym języku')
    psym.add_argument('--find-dups', action='store_true',
                      help='Pokaż symbole zdefiniowane w wielu plikach')

    # wrappers  ← NOWY
    pw = sub.add_parser('wrappers',
                        help='Wykryj legacy shims, barrel files, proxy wrappers')
    word_arg(pw)
    pw.add_argument('--min-score', type=int, default=40,
                    help='Minimalny score heurystyczny 0-100 (domyślnie 40)')

    # dead  ← NOWY
    pde = sub.add_parser('dead',
                         help='Symbole zdefiniowane ale prawdopodobnie nieużywane')
    word_arg(pde)
    pde.add_argument('--min-len', type=int, default=4,
                     help='Min. długość nazwy symbolu (domyślnie 4)')

    # diff  ← NOWY
    pdiff = sub.add_parser('diff', help='Unified diff dwóch plików')
    pdiff.add_argument('file_a', help='Plik A (ścieżka względna lub absolutna)')
    pdiff.add_argument('file_b', help='Plik B')
    pdiff.add_argument('--normalize', action='store_true',
                       help='Usuń komentarze/stringi przed diffem')
    pdiff.add_argument('--context', type=int, default=3, help='Linie kontekstu')

    # hotmap  ← NOWY
    phot = sub.add_parser('hotmap',
                          help='Mapa katalogów wg koncentracji podobnych plików')
    word_arg(phot)
    phot.add_argument('--min-sim', type=float, default=60.0, metavar='PCT')
    phot.add_argument('--normalize', action='store_true')

    # report
    pr = sub.add_parser('report', help='Pełny raport JSON dla LLM (wszystkie analizy)')
    pr.add_argument('word', help='Słowo / temat raportu')
    pr.add_argument('--out', '-o', metavar='FILE', help='Plik wyjściowy (domyślnie: refactor-report-WORD.json)')
    pr.add_argument('--json', action='store_true', help='Drukuj JSON na stdout')
    pr.add_argument('--min-sim', type=float, default=60.0, metavar='PCT')
    pr.add_argument('--normalize', action='store_true',
                    help='Użyj znormalizowanego podobieństwa w raporcie')
    pr.add_argument('--preview', action='store_true',
                    help='Dołącz podgląd treści pliku (~2000 znaków)')
    pr.add_argument('--toon', action='store_true',
                    help='Generuj wyjście w formacie toon (YAML-like)')

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    root = Path(args.path).resolve()

    if not root.exists():
        print(f"Błąd: katalog nie istnieje: {root}", file=sys.stderr)
        sys.exit(1)

    dispatch = {
        'find': cmd_find,
        'duplicates': cmd_duplicates,
        'similar': cmd_similar,
        'cluster': cmd_cluster,
        'deps': cmd_deps,
        'symbols': cmd_symbols,
        'wrappers': cmd_wrappers,
        'dead': cmd_dead,
        'diff': cmd_diff,
        'hotmap': cmd_hotmap,
        'report': cmd_report,
    }
    dispatch[args.cmd](args, root)


if __name__ == '__main__':
    main()