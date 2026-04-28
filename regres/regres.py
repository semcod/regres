from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


IMPORT_RE = re.compile(
    r"(?:import\s+(?:type\s+)?[^\n]*?from\s+['\"]([^'\"]+)['\"]|"
    r"export\s+\*\s+from\s+['\"]([^'\"]+)['\"])"
)
FUNC_RE = re.compile(r"\bfunction\b|=>")
CLASS_RE = re.compile(r"\bclass\b")
EXPORT_RE = re.compile(r"\bexport\b")


@dataclass
class GitCommit:
    sha: str
    short_sha: str
    date: str
    author: str
    subject: str
    file_statuses: List[str]
    insertions: int
    deletions: int


def run_git(args: List[str], cwd: Path) -> str:
    cmd = ["git", *args]
    out = subprocess.check_output(cmd, cwd=str(cwd), text=True, stderr=subprocess.DEVNULL)
    return out


def find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    while True:
        if (cur / ".git").exists():
            return cur
        if cur.parent == cur:
            raise RuntimeError("Nie znaleziono .git")
        cur = cur.parent


def _dedupe_paths(paths: List[Path]) -> List[Path]:
    seen: Set[str] = set()
    out: List[Path] = []
    for p in paths:
        rp = str(p.resolve())
        if rp in seen:
            continue
        seen.add(rp)
        out.append(p.resolve())
    return out


def _check_absolute_path(raw: Path) -> Path | None:
    """Check if the raw path is absolute and exists."""
    if raw.is_absolute():
        if raw.exists() and raw.is_file():
            return raw.resolve()
    return None


def _check_relative_paths(raw: Path, bases: tuple) -> list[Path]:
    """Check relative paths against multiple base directories."""
    candidates = []
    for base in bases:
        cand = (base / raw).resolve()
        if cand.exists() and cand.is_file():
            candidates.append(cand)
    return _dedupe_paths(candidates)


def _search_by_name_suffix(name: str, suffix: str, roots: tuple) -> list[Path]:
    """Search for files by name/suffix in given roots."""
    candidates = []
    for root in roots:
        if not root.exists() or not root.is_dir():
            continue
        for p in root.rglob(name):
            if not p.is_file():
                continue
            try:
                rel = str(p.resolve().relative_to(root.resolve())).replace("\\", "/")
            except ValueError:
                rel = str(p.resolve()).replace("\\", "/")
            if not suffix or rel.endswith(suffix) or p.name == name:
                candidates.append(p.resolve())
    return _dedupe_paths(candidates)


def _resolve_single_or_error(candidates: list[Path], error_msg: str) -> Path:
    """Return single candidate or raise error with message."""
    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1:
        raise FileNotFoundError(
            error_msg + ", ".join(str(p) for p in candidates[:12])
        )
    raise FileNotFoundError(error_msg)


def resolve_target_file(file_arg: str, cwd: Path, repo_root: Path, scan_root: Path) -> Path:
    raw = Path(file_arg)

    abs_result = _check_absolute_path(raw)
    if abs_result:
        return abs_result

    candidates = _check_relative_paths(raw, (cwd, repo_root, scan_root))
    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1:
        raise FileNotFoundError(
            "Niejednoznaczny --file; podaj pełniejszą ścieżkę. Kandydaci: "
            + ", ".join(str(p) for p in candidates[:12])
        )

    suffix = file_arg.replace("\\", "/").lstrip("./")
    name = raw.name if raw.name else suffix
    candidates = _search_by_name_suffix(name, suffix, (scan_root, repo_root))
    
    if len(candidates) == 1:
        return candidates[0]

    if len(candidates) > 1:
        preferred = [p for p in candidates if str(p).startswith(str(scan_root.resolve()))]
        preferred = _dedupe_paths(preferred)
        if len(preferred) == 1:
            return preferred[0]
        show = preferred if preferred else candidates
        raise FileNotFoundError(
            "Niejednoznaczny --file po wyszukaniu historycznym; podaj pełną ścieżkę. Kandydaci: "
            + ", ".join(str(p) for p in show[:20])
        )

    raise FileNotFoundError(
        f"Nie znaleziono pliku dla --file='{file_arg}'. "
        f"Sprawdzono: cwd={cwd}, repo_root={repo_root}, scan_root={scan_root}."
    )


def to_rel(path: Path, repo_root: Path) -> str:
    return str(path.resolve().relative_to(repo_root))


def safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1", errors="replace")


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def content_metrics(text: str, path: Path) -> Dict[str, Any]:
    lines = text.splitlines()
    non_empty = [ln for ln in lines if ln.strip()]
    return {
        "path": str(path),
        "bytes": path.stat().st_size if path.exists() else 0,
        "lines": len(lines),
        "non_empty_lines": len(non_empty),
        "imports_count": len([m for m in IMPORT_RE.finditer(text)]),
        "exports_count": len(EXPORT_RE.findall(text)),
        "class_count": len(CLASS_RE.findall(text)),
        "function_like_count": len(FUNC_RE.findall(text)),
        "sha256": sha256_of_file(path),
    }


def resolve_local_import(raw_import: str, file_path: Path, repo_root: Path) -> Optional[str]:
    if not raw_import:
        return None
    if raw_import.startswith("@"):
        return None
    if not (raw_import.startswith("./") or raw_import.startswith("../")):
        return None

    base = (file_path.parent / raw_import).resolve()
    base_str = str(base)
    candidates = [
        base,
        Path(base_str + ".ts"),
        Path(base_str + ".tsx"),
        Path(base_str + ".js"),
        Path(base_str + ".py"),
        base / "index.ts",
        base / "index.tsx",
        base / "index.js",
        base / "__init__.py",
    ]
    for c in candidates:
        if c.exists():
            try:
                return str(c.relative_to(repo_root))
            except ValueError:
                return str(c)
    return None


def extract_local_imports(text: str) -> List[str]:
    results: List[str] = []
    for m in IMPORT_RE.finditer(text):
        imp = m.group(1) or m.group(2) or ""
        if imp.startswith("./") or imp.startswith("../"):
            results.append(imp)
    return results


def resolve_import_at_commit(
    raw_import: str, file_rel: str, repo_root: Path, commit_sha: str
) -> Optional[str]:
    if not raw_import:
        return None
    if not (raw_import.startswith("./") or raw_import.startswith("../")):
        return None

    base = Path(os.path.normpath(str(Path(file_rel).parent / raw_import)))
    base_str = os.path.normpath(str(base))
    candidates_rel = [
        base_str,
        os.path.normpath(base_str + ".ts"),
        os.path.normpath(base_str + ".tsx"),
        os.path.normpath(base_str + ".js"),
        os.path.normpath(base_str + ".py"),
        os.path.normpath(str(base / "index.ts")),
        os.path.normpath(str(base / "index.tsx")),
        os.path.normpath(str(base / "index.js")),
        os.path.normpath(str(base / "__init__.py")),
    ]
    for c_rel in candidates_rel:
        if file_content_at_commit(repo_root, c_rel, commit_sha) is not None:
            return c_rel
    return None


def check_imports_at_commit(
    repo_root: Path, rel_path: str, commit_sha: str
) -> Dict[str, Any]:
    if commit_sha == "HEAD":
        current_file = (repo_root / rel_path).resolve()
        text = safe_read_text(current_file) if current_file.exists() and current_file.is_file() else file_content_at_commit(repo_root, rel_path, commit_sha)
    else:
        text = file_content_at_commit(repo_root, rel_path, commit_sha)
    if text is None:
        return {"exists": False, "imports": [], "broken": [], "ok": []}

    imports = extract_local_imports(text)
    broken: List[str] = []
    ok: List[str] = []
    resolved: List[str] = []
    current_abs = (repo_root / rel_path).resolve()
    for imp in imports:
        if commit_sha == "HEAD":
            res = resolve_local_import(imp, current_abs, repo_root)
        else:
            res = resolve_import_at_commit(imp, rel_path, repo_root, commit_sha)
        if res:
            ok.append(imp)
            resolved.append(res)
        else:
            broken.append(imp)

    return {
        "exists": True,
        "lines": len(text.splitlines()),
        "imports": imports,
        "import_count": len(imports),
        "broken_count": len(broken),
        "ok_count": len(ok),
        "broken": broken,
        "ok": ok,
        "resolved": resolved,
    }


def find_last_working_commit(
    repo_root: Path, rel_path: str, commits: List[GitCommit]
) -> Optional[Dict[str, Any]]:
    for c in commits:
        check = check_imports_at_commit(repo_root, rel_path, c.sha)
        if check["exists"] and check["broken_count"] == 0 and check["import_count"] > 0:
            return {
                "sha": c.sha,
                "short_sha": c.short_sha,
                "date": c.date,
                "subject": c.subject,
                "lines": check["lines"],
                "imports": check["imports"],
                "ok_count": check["ok_count"],
            }
        if check["exists"] and check["broken_count"] == 0 and check["import_count"] == 0:
            # Plik bez lokalnych importów - też uznajemy za działający, jeśli szukamy cokolwiek
            return {
                "sha": c.sha,
                "short_sha": c.short_sha,
                "date": c.date,
                "subject": c.subject,
                "lines": check["lines"],
                "imports": [],
                "ok_count": 0,
            }
    return None


def search_missing_in_history(
    repo_root: Path, missing_imports: List[str], file_rel: str
) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for imp in missing_imports:
        base = Path(file_rel).parent / imp
        # Szukamy w historii git plików o podobnej nazwie
        stem = Path(imp).stem
        if stem in seen:
            continue
        seen.add(stem)
        try:
            raw = run_git(
                ["log", "--all", "--full-history", "--oneline", "--", f"**/{stem}*"],
                repo_root,
            )
            lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
            last_line = lines[0] if lines else None
            out.append(
                {
                    "import": imp,
                    "stem": stem,
                    "history_found": len(lines) > 0,
                    "history_count": len(lines),
                    "last_commit_line": last_line,
                }
            )
        except subprocess.CalledProcessError:
            out.append(
                {
                    "import": imp,
                    "stem": stem,
                    "history_found": False,
                    "history_count": 0,
                    "last_commit_line": None,
                }
            )
    return out


def analyze_regression(
    repo_root: Path, rel_path: str, commits: List[GitCommit], current_text: str
) -> Dict[str, Any]:
    current_check = check_imports_at_commit(repo_root, rel_path, "HEAD")
    broken = current_check.get("broken", [])
    all_ok = current_check.get("broken_count", 0) == 0

    last_working = None
    first_broken = None
    if not all_ok and broken:
        last_working = find_last_working_commit(repo_root, rel_path, commits)
        if last_working:
            # Znajdź pierwszy popsuty commit (commit przed last_working lub pierwszy w historii z broken)
            for idx, c in enumerate(commits):
                if c.sha == last_working["sha"]:
                    # Popsuty to ten przed last_working (jeśli istnieje)
                    if idx > 0:
                        first_broken = {
                            "sha": commits[idx - 1].sha,
                            "short_sha": commits[idx - 1].short_sha,
                            "date": commits[idx - 1].date,
                            "subject": commits[idx - 1].subject,
                        }
                    break

    missing_history = search_missing_in_history(repo_root, broken, rel_path) if broken else []

    # Generuj rekomendację
    recommendations: List[str] = []
    if broken:
        for mh in missing_history:
            if mh["history_found"]:
                recommendations.append(
                    f"Plik z importu `{mh['import']}` (stem: {mh['stem']}) istnieje w historii git. "
                    f"Sprawdź `git log --all --full-history -- **/{mh['stem']}*`. "
                    f"Ostatni commit: {mh['last_commit_line']}"
                )
            else:
                recommendations.append(
                    f"Plik z importu `{mh['import']}` (stem: {mh['stem']}) NIE istnieje w historii git. "
                    f"Możliwe, że symbol został wbudowany do innego pliku lub usunięty."
                )

    return {
        "current_broken_imports": broken,
        "current_all_ok": all_ok,
        "current_import_count": current_check.get("import_count", 0),
        "current_lines": current_check.get("lines", 0),
        "last_working_commit": last_working,
        "first_broken_commit": first_broken,
        "missing_imports_history": missing_history,
        "recommendations": recommendations,
    }


# === Problem classification ============================================

PROBLEM_TYPES = {
    "HEALTHY": "Plik działa, brak regresji",
    "FILE_RENAMED": "Plik został przeniesiony pod inną ścieżkę (ta sama nazwa, inna lokalizacja)",
    "FILE_DELETED": "Plik istniał historycznie, został usunięty bez następcy",
    "FILE_NEVER_EXISTED": "Import wskazuje na plik, który nigdy nie istniał (literówka/błędna ścieżka)",
    "WRAPPER_REGRESSION": "Plik został zredukowany do cienkiego wrappera; logika gdzie indziej",
    "BROKEN_IMPORTS_MOVED_MODULE": "Plik został przeniesiony do innego modułu, ścieżki względne się rozjechały",
    "SYMBOLS_EXTRACTED": "Symbole pliku zostały wyodrębnione do innych plików",
    "MASS_REWRITE": "Plik został kompletnie przepisany (similarity ~0)",
    "TREE_RESTRUCTURED": "Drzewo zależności pliku zostało przebudowane",
}

SYMBOL_RE = re.compile(
    r"export\s+(?:default\s+)?(?:async\s+)?"
    r"(?:const|let|var|function|class|interface|type|enum)\s+"
    r"([A-Za-z_$][\w$]*)"
)
SYMBOL_BRACE_RE = re.compile(r"export\s*\{([^}]+)\}")


def extract_symbols(text: str) -> List[str]:
    out: Set[str] = set()
    for m in SYMBOL_RE.finditer(text):
        out.add(m.group(1))
    for m in SYMBOL_BRACE_RE.finditer(text):
        for raw in m.group(1).split(","):
            name = raw.strip().split(" as ")[0].strip()
            if name:
                out.add(name)
    return sorted(out)


def track_filename_history(repo_root: Path, basename: str) -> List[Dict[str, str]]:
    try:
        raw = run_git(
            ["log", "--all", "--full-history", "--name-status",
             "--pretty=format:%H%x09%cI%x09%s", "--", f"**/{basename}"],
            repo_root,
        )
    except subprocess.CalledProcessError:
        return []

    entries: List[Dict[str, str]] = []
    cur_commit: Optional[Dict[str, str]] = None
    for line in raw.splitlines():
        if "\t" in line and not line[0].isalpha() and not line.startswith(("A", "M", "D", "R", "C")):
            continue
        parts = line.split("\t")
        if len(parts) >= 3 and len(parts[0]) == 40:
            cur_commit = {"sha": parts[0], "date": parts[1], "subject": parts[2]}
        elif cur_commit and len(parts) >= 2:
            status = parts[0]
            path = parts[-1]
            entries.append({**cur_commit, "status": status, "path": path})
    return entries


def find_current_locations(repo_root: Path, basename: str) -> List[str]:
    out: List[str] = []
    for p in repo_root.rglob(basename):
        if p.is_file() and ".git" not in p.parts and "node_modules" not in p.parts:
            try:
                out.append(str(p.relative_to(repo_root)))
            except ValueError:
                out.append(str(p))
    return sorted(out)


def _classify_import_problem(repo_root: Path, mh: dict) -> dict:
    """Classify a single import problem."""
    imp = mh["import"]
    stem = mh["stem"]
    candidates = find_current_locations(repo_root, f"{stem}.ts")
    candidates += find_current_locations(repo_root, f"{stem}.tsx")
    candidates += find_current_locations(repo_root, f"{stem}.js")

    if candidates:
        problem_type = "FILE_RENAMED"
        recommendation = (
            f"Zaktualizuj ścieżkę importu — plik istnieje pod: "
            + ", ".join(f"`{c}`" for c in candidates[:3])
        )
    elif mh["history_found"]:
        problem_type = "FILE_DELETED"
        recommendation = (
            f"Plik istniał w historii ({mh['history_count']} commitów), ale został usunięty. "
            f"Przywróć z `git show <sha>:<path>` lub zintegruj logikę inline."
        )
    else:
        problem_type = "FILE_NEVER_EXISTED"
        recommendation = (
            f"Plik o nazwie `{stem}` nie istnieje w historii git. "
            f"Sprawdź pisownię lub usuń import."
        )
    return {
        "import": imp,
        "stem": stem,
        "type": problem_type,
        "current_locations": candidates[:5],
        "recommendation": recommendation,
    }


def _determine_primary_type(import_problems: list, broken: list, target_dir: str, 
                            current_lines: int, evolution: list) -> tuple[str, float, list]:
    """Determine the primary problem type and confidence."""
    primary_type = "HEALTHY"
    confidence = 1.0
    evidence: List[str] = []
    
    all_ok = len(broken) == 0
    
    if not all_ok:
        type_counts: Dict[str, int] = {}
        for ip in import_problems:
            type_counts[ip["type"]] = type_counts.get(ip["type"], 0) + 1
        if type_counts:
            primary_type = max(type_counts.items(), key=lambda x: x[1])[0]
            total = len(import_problems)
            confidence = round(type_counts[primary_type] / total, 2)
            evidence.append(
                f"{type_counts[primary_type]}/{total} popsutych importów ma typ {primary_type}"
            )

        if "modules/" in target_dir and primary_type == "FILE_RENAMED":
            module_jump = any(imp.count("../") >= 3 for imp in broken)
            if module_jump:
                primary_type = "BROKEN_IMPORTS_MOVED_MODULE"
                evidence.append(
                    f"Plik znajduje się w `{target_dir}`, ale ma importy z głębokim `../` — "
                    f"prawdopodobnie został przeniesiony bez aktualizacji ścieżek"
                )
    else:
        if current_lines <= 5 and evolution:
            for e in evolution[1:]:
                if e["lines"] >= 20 and e["similarity_to_current"] < 0.3:
                    primary_type = "WRAPPER_REGRESSION"
                    confidence = 0.8
                    evidence.append(
                        f"Aktualnie {current_lines} linii, w `{e['short_sha']}` było {e['lines']} linii "
                        f"(similarity {e['similarity_to_current']})"
                    )
                    break

        if evolution and len(evolution) >= 2:
            for e in evolution[:5]:
                if e["similarity_to_current"] < 0.1 and abs(e["line_delta"]) > 50:
                    if primary_type == "HEALTHY":
                        primary_type = "MASS_REWRITE"
                        confidence = 0.7
                        evidence.append(
                            f"Commit `{e['short_sha']}`: similarity {e['similarity_to_current']}, "
                            f"line_delta {e['line_delta']}"
                        )
                    break
    
    return primary_type, confidence, evidence


def classify_problem(
    repo_root: Path,
    target_rel: str,
    current_text: str,
    evolution: List[Dict[str, Any]],
    regression: Dict[str, Any],
    duplicates: Dict[str, Any],
) -> Dict[str, Any]:
    basename = Path(target_rel).name
    current_lines = len(current_text.splitlines())
    current_symbols = extract_symbols(current_text)
    broken = regression.get("current_broken_imports", [])

    import_problems = [
        _classify_import_problem(repo_root, mh)
        for mh in regression.get("missing_imports_history", [])
    ]

    target_dir = str(Path(target_rel).parent)
    primary_type, confidence, evidence = _determine_primary_type(
        import_problems, broken, target_dir, current_lines, evolution
    )

    name_history = track_filename_history(repo_root, basename)[:30]
    paths_in_history = sorted({h["path"] for h in name_history if h.get("path")})
    is_basename_unique = len([p for p in paths_in_history if Path(p).name == basename]) <= 1

    return {
        "primary_type": primary_type,
        "primary_type_description": PROBLEM_TYPES.get(primary_type, ""),
        "confidence": confidence,
        "evidence": evidence,
        "current_symbols": current_symbols,
        "current_symbol_count": len(current_symbols),
        "import_problems": import_problems,
        "filename_history": {
            "basename": basename,
            "paths_seen": paths_in_history[:20],
            "is_basename_unique": is_basename_unique,
            "entries_count": len(name_history),
        },
    }


def dependency_tree(file_path: Path, repo_root: Path, max_depth: int = 3) -> Dict[str, Any]:
    seen: set[str] = set()

    def walk(node_path: Path, depth: int) -> Dict[str, Any]:
        rel = to_rel(node_path, repo_root)
        if rel in seen:
            return {"path": rel, "cycle": True, "children": []}
        seen.add(rel)

        text = safe_read_text(node_path)
        children = []
        if depth < max_depth:
            for m in IMPORT_RE.finditer(text):
                imp = m.group(1) or m.group(2) or ""
                resolved = resolve_local_import(imp, node_path, repo_root)
                if resolved:
                    c_abs = (repo_root / resolved).resolve()
                    if c_abs.exists() and c_abs.is_file():
                        children.append(walk(c_abs, depth + 1))

        return {
            "path": rel,
            "imports_local": len(children),
            "children": children,
        }

    return walk(file_path, 0)


def reverse_references(file_path: Path, repo_root: Path, scan_root: Path, max_hits: int = 500) -> List[str]:
    rel_target = to_rel(file_path, repo_root)
    refs: List[str] = []
    exts = {".ts", ".tsx", ".js", ".py"}
    for p in scan_root.rglob("*"):
        if not p.is_file() or p.suffix not in exts:
            continue
        if p.resolve() == file_path.resolve():
            continue
        txt = safe_read_text(p)
        for m in IMPORT_RE.finditer(txt):
            imp = m.group(1) or m.group(2) or ""
            resolved = resolve_local_import(imp, p, repo_root)
            if resolved == rel_target:
                refs.append(to_rel(p, repo_root))
                break
        if len(refs) >= max_hits:
            break
    return sorted(refs)


def exact_and_near_duplicates(
    file_path: Path,
    repo_root: Path,
    scan_root: Path,
    near_threshold: float = 0.92,
    max_near: int = 20,
) -> Dict[str, Any]:
    target_hash = sha256_of_file(file_path)
    target_text = safe_read_text(file_path)
    target_lines = len(target_text.splitlines())
    target_rel = to_rel(file_path, repo_root)
    exts = {".ts", ".tsx", ".js", ".py"}

    exact: List[str] = []
    near: List[Dict[str, Any]] = []

    for p in scan_root.rglob("*"):
        if not p.is_file() or p.suffix not in exts:
            continue
        if p.resolve() == file_path.resolve():
            continue
        rel = to_rel(p, repo_root)
        h = sha256_of_file(p)
        if h == target_hash:
            exact.append(rel)
            continue
        cand_text = safe_read_text(p)
        cand_lines = len(cand_text.splitlines())
        score = SequenceMatcher(None, target_text, cand_text).ratio()
        max_lines = max(target_lines, cand_lines)
        line_ratio = (min(target_lines, cand_lines) / max_lines) if max_lines > 0 else 1.0
        adjusted = score * line_ratio
        if adjusted >= near_threshold:
            near.append(
                {
                    "path": rel,
                    "similarity": round(adjusted, 4),
                    "raw_similarity": round(score, 4),
                    "target_lines": target_lines,
                    "candidate_lines": cand_lines,
                }
            )

    near.sort(key=lambda x: x["similarity"], reverse=True)
    return {
        "target": target_rel,
        "target_sha256": target_hash,
        "exact_duplicates": sorted(exact),
        "near_duplicates": near[:max_near],
    }


def trace_name_and_hash_candidates(
    file_path: Path,
    repo_root: Path,
    scan_root: Path,
    max_candidates: int = 20,
) -> Dict[str, Any]:
    target_rel = to_rel(file_path, repo_root)
    target_name = file_path.name
    target_text = safe_read_text(file_path)
    target_hash = sha256_of_file(file_path)
    target_lines = len(target_text.splitlines())

    candidates: List[Dict[str, Any]] = []
    seen: Set[str] = set()

    for root in (scan_root, repo_root):
        if not root.exists() or not root.is_dir():
            continue
        for p in root.rglob(target_name):
            if not p.is_file():
                continue
            rel = to_rel(p, repo_root)
            if rel == target_rel:
                continue
            if rel in seen:
                continue
            seen.add(rel)

            cand_text = safe_read_text(p)
            cand_hash = sha256_of_file(p)
            cand_lines = len(cand_text.splitlines())
            raw_sim = SequenceMatcher(None, target_text, cand_text).ratio()
            max_lines = max(target_lines, cand_lines)
            line_ratio = (min(target_lines, cand_lines) / max_lines) if max_lines > 0 else 1.0
            similarity = raw_sim * line_ratio

            last_commit = None
            try:
                raw = run_git(
                    [
                        "log",
                        "-n",
                        "1",
                        "--date=iso-strict",
                        "--pretty=format:%H%x1f%h%x1f%ad%x1f%s",
                        "--",
                        rel,
                    ],
                    repo_root,
                ).strip()
                if raw:
                    parts = raw.split("\x1f", 3)
                    if len(parts) == 4:
                        last_commit = {
                            "sha": parts[0],
                            "short_sha": parts[1],
                            "date": parts[2],
                            "subject": parts[3],
                        }
            except subprocess.CalledProcessError:
                last_commit = None

            candidates.append(
                {
                    "path": rel,
                    "same_name": True,
                    "same_hash": cand_hash == target_hash,
                    "similarity": round(similarity, 4),
                    "raw_similarity": round(raw_sim, 4),
                    "target_lines": target_lines,
                    "candidate_lines": cand_lines,
                    "last_commit": last_commit,
                }
            )

    candidates.sort(
        key=lambda x: (
            0 if x["same_hash"] else 1,
            -x["similarity"],
            x["path"],
        )
    )
    return {
        "target": target_rel,
        "target_name": target_name,
        "target_sha256": target_hash,
        "candidates": candidates[:max_candidates],
    }


def parse_numstat_block(lines: List[str]) -> Tuple[int, int]:
    ins = 0
    dels = 0
    for ln in lines:
        parts = ln.strip().split("\t")
        if len(parts) < 2:
            continue
        a, d = parts[0], parts[1]
        if a.isdigit():
            ins += int(a)
        if d.isdigit():
            dels += int(d)
    return ins, dels


def file_lineage(repo_root: Path, rel_file: str, max_commits: int = 60) -> List[GitCommit]:
    fmt = "%H%x1f%h%x1f%ad%x1f%an%x1f%s"
    raw = run_git(
        [
            "log",
            "--follow",
            f"--max-count={max_commits}",
            "--date=iso-strict",
            f"--pretty=format:{fmt}",
            "--name-status",
            "--numstat",
            "--",
            rel_file,
        ],
        repo_root,
    )
    lines = raw.splitlines()
    commits: List[GitCommit] = []

    i = 0
    while i < len(lines):
        line = lines[i]
        if "\x1f" not in line:
            i += 1
            continue

        sha, short_sha, date, author, subject = line.split("\x1f", 4)
        i += 1
        statuses: List[str] = []
        numstats: List[str] = []
        while i < len(lines) and "\x1f" not in lines[i]:
            cur = lines[i].strip()
            if cur:
                if "\t" in cur and (cur[0].isdigit() or cur[0] == "-"):
                    numstats.append(cur)
                else:
                    statuses.append(cur)
            i += 1
        ins, dels = parse_numstat_block(numstats)
        commits.append(
            GitCommit(
                sha=sha,
                short_sha=short_sha,
                date=date,
                author=author,
                subject=subject,
                file_statuses=statuses,
                insertions=ins,
                deletions=dels,
            )
        )
    return commits


def changed_files_for_commit(repo_root: Path, commit_sha: str, limit: int = 120) -> List[str]:
    raw = run_git(["show", "--name-only", "--pretty=format:", commit_sha], repo_root)
    files = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    return files[:limit]


def references_in_recent_commits(repo_root: Path, commits: List[GitCommit], max_commits: int = 10) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for c in commits[:max_commits]:
        out.append(
            {
                "sha": c.sha,
                "short_sha": c.short_sha,
                "subject": c.subject,
                "related_files": changed_files_for_commit(repo_root, c.sha),
            }
        )
    return out


def file_content_at_commit(repo_root: Path, rel_path: str, commit_sha: str) -> Optional[str]:
    try:
        return run_git(["show", f"{commit_sha}:{rel_path}"], repo_root)
    except subprocess.CalledProcessError:
        return None


def resolve_import_historical(raw_import: str, file_rel: str, repo_root: Path, commit_sha: str) -> Optional[str]:
    if not raw_import:
        return None
    if raw_import.startswith("@"):
        return None
    if not (raw_import.startswith("./") or raw_import.startswith("../")):
        return None

    base = Path(os.path.normpath(str(Path(file_rel).parent / raw_import)))
    base_str = os.path.normpath(str(base))
    candidates_rel = [
        base_str,
        os.path.normpath(base_str + ".ts"),
        os.path.normpath(base_str + ".tsx"),
        os.path.normpath(base_str + ".js"),
        os.path.normpath(base_str + ".py"),
        os.path.normpath(str(base / "index.ts")),
        os.path.normpath(str(base / "index.tsx")),
        os.path.normpath(str(base / "index.js")),
        os.path.normpath(str(base / "__init__.py")),
    ]
    for c_rel in candidates_rel:
        if file_content_at_commit(repo_root, c_rel, commit_sha) is not None:
            return c_rel
    return None


def historical_dependency_tree(
    repo_root: Path,
    rel_path: str,
    commit_sha: str,
    max_depth: int = 2,
) -> Optional[Dict[str, Any]]:
    text = file_content_at_commit(repo_root, rel_path, commit_sha)
    if text is None:
        return None

    seen: set[str] = set()

    def walk(node_rel: str, depth: int) -> Dict[str, Any]:
        if node_rel in seen:
            return {"path": node_rel, "cycle": True, "children": []}
        seen.add(node_rel)

        node_text = file_content_at_commit(repo_root, node_rel, commit_sha)
        if node_text is None:
            return {"path": node_rel, "missing": True, "children": []}

        children = []
        if depth < max_depth:
            for m in IMPORT_RE.finditer(node_text):
                imp = m.group(1) or m.group(2) or ""
                resolved = resolve_import_historical(imp, node_rel, repo_root, commit_sha)
                if resolved:
                    children.append(walk(resolved, depth + 1))

        return {"path": node_rel, "imports_local": len(children), "children": children}

    return walk(rel_path, 0)


def analyze_evolution(
    repo_root: Path,
    rel_path: str,
    commits: List[GitCommit],
    current_text: str,
    max_depth: int = 1,
) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    prev_tree: Optional[Dict[str, Any]] = None
    for c in commits:
        hist_text = file_content_at_commit(repo_root, rel_path, c.sha)
        if hist_text is None:
            continue
        hist_lines = len(hist_text.splitlines())
        current_lines = len(current_text.splitlines())
        sim = SequenceMatcher(None, current_text, hist_text).ratio()

        tree = historical_dependency_tree(repo_root, rel_path, c.sha, max_depth=max_depth)
        tree_paths_before: set[str] = set()
        tree_paths_after: set[str] = set()
        if prev_tree:
            tree_paths_before = _collect_tree_paths(prev_tree)
        if tree:
            tree_paths_after = _collect_tree_paths(tree)

        tree_changed = tree_paths_before != tree_paths_after if prev_tree else False
        tree_diff_add = sorted(tree_paths_after - tree_paths_before) if prev_tree else []
        tree_diff_remove = sorted(tree_paths_before - tree_paths_after) if prev_tree else []

        entry = {
            "sha": c.sha,
            "short_sha": c.short_sha,
            "date": c.date,
            "subject": c.subject,
            "lines": hist_lines,
            "current_lines": current_lines,
            "line_delta": hist_lines - current_lines,
            "similarity_to_current": round(sim, 4),
            "tree_imports_count": len(tree_paths_after) if tree else 0,
            "tree_changed": tree_changed,
            "tree_added": tree_diff_add,
            "tree_removed": tree_diff_remove,
        }
        out.append(entry)
        if tree:
            prev_tree = tree
    return out


def _collect_tree_paths(tree: Dict[str, Any]) -> set[str]:
    paths: set[str] = {tree.get("path", "")}
    for child in tree.get("children", []):
        paths.update(_collect_tree_paths(child))
    return paths


def find_last_good_version(
    evolution: List[Dict[str, Any]],
    min_lines: int = 0,
    min_similarity: float = 0.0,
    max_results: int = 5,
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for entry in evolution:
        if min_lines > 0 and entry["lines"] < min_lines:
            continue
        if min_similarity > 0 and entry["similarity_to_current"] < min_similarity:
            continue
        results.append(entry)
        if len(results) >= max_results:
            break
    return results


def llm_context_packet(report: Dict[str, Any]) -> Dict[str, Any]:
    lineage = report.get("lineage", [])
    top_recent = lineage[:8]
    near_dups = report.get("duplicates", {}).get("near_duplicates", [])[:8]
    name_hash_candidates = report.get("name_hash_candidates", {}).get("candidates", [])[:8]
    reverse_refs = report.get("references", {}).get("reverse_imports", [])[:50]
    evolution = report.get("evolution", [])
    last_good = report.get("last_good_version", [])
    regression = report.get("regression", {})
    return {
        "target": report.get("target_file"),
        "file_metrics": report.get("metrics", {}),
        "recent_lineage": top_recent,
        "reverse_imports": reverse_refs,
        "exact_duplicates": report.get("duplicates", {}).get("exact_duplicates", []),
        "near_duplicates": near_dups,
        "name_hash_candidates": name_hash_candidates,
        "dependency_tree": report.get("dependency_tree", {}),
        "evolution_summary": evolution[:8] if evolution else [],
        "last_good_version": last_good[:3] if last_good else [],
        "regression_detective": {
            "current_broken_imports": regression.get("current_broken_imports", []),
            "last_working_commit": regression.get("last_working_commit"),
            "first_broken_commit": regression.get("first_broken_commit"),
            "recommendations": regression.get("recommendations", [])[:5],
        } if regression else {},
        "classification": {
            "primary_type": (report.get("classification") or {}).get("primary_type"),
            "primary_type_description": (report.get("classification") or {}).get("primary_type_description"),
            "confidence": (report.get("classification") or {}).get("confidence"),
            "evidence": (report.get("classification") or {}).get("evidence", []),
            "import_problems": (report.get("classification") or {}).get("import_problems", [])[:10],
            "current_symbols": (report.get("classification") or {}).get("current_symbols", [])[:20],
            "filename_history": (report.get("classification") or {}).get("filename_history", {}),
        },
    }


def _render_classification_section(classification: dict, lines: list):
    """Render the classification section of the report."""
    if not classification:
        return
    
    ptype = classification.get("primary_type", "HEALTHY")
    pdesc = classification.get("primary_type_description", "")
    conf = classification.get("confidence", 0)
    lines.append(f"## Klasyfikacja problemu: **{ptype}** (confidence={conf})")
    if pdesc:
        lines.append(f"> {pdesc}")
    
    ev = classification.get("evidence", [])
    if ev:
        lines.append("")
        lines.append("**Dowody:**")
        for e in ev:
            lines.append(f"- {e}")

    ips = classification.get("import_problems", [])
    if ips:
        lines.append("")
        lines.append("### Klasyfikacja per-import")
        lines.append("")
        lines.append("| import | typ | obecne lokalizacje | rekomendacja |")
        lines.append("|---|---|---|---|")
        for ip in ips[:30]:
            locs = ", ".join(f"`{l}`" for l in ip.get("current_locations", [])[:3]) or "—"
            lines.append(
                f"| `{ip['import']}` | **{ip['type']}** | {locs} | {ip['recommendation']} |"
            )

    symbols = classification.get("current_symbols", [])
    if symbols:
        lines.append("")
        lines.append(f"**Eksportowane symbole ({len(symbols)}):** "
                     + ", ".join(f"`{s}`" for s in symbols[:20]))

    fh = classification.get("filename_history", {})
    if fh and fh.get("paths_seen"):
        lines.append("")
        lines.append(f"### Historia ścieżek dla nazwy `{fh['basename']}`")
        for p in fh["paths_seen"][:10]:
            lines.append(f"- `{p}`")
        if not fh.get("is_basename_unique"):
            lines.append(f"\n> Nazwa pliku występowała w wielu lokalizacjach — "
                         f"możliwe rename'y lub duplikaty.")
    lines.append("")


def _render_name_hash_section(nh: dict, lines: list):
    """Render the name/hash candidates section."""
    nh_candidates = nh.get("candidates", [])
    lines.extend([
        "## Name/Hash Candidates",
        f"- target_name: `{nh.get('target_name', '')}`",
        f"- candidates: {len(nh_candidates)}",
        "",
    ])
    if nh_candidates:
        for item in nh_candidates:
            commit = item.get("last_commit") or {}
            commit_info = ""
            if commit.get("short_sha"):
                commit_info = f" (last: `{commit['short_sha']}` {commit.get('date', '')[:10]} '{commit.get('subject', '')}')"
            lines.append(
                f"- `{item['path']}` same_hash={item['same_hash']} similarity={item['similarity']}"
                f" lines={item['target_lines']}/{item['candidate_lines']}{commit_info}"
            )
        lines.append("")


def _render_metrics_section(m: dict, lines: list):
    """Render the metrics section."""
    lines.extend([
        "## Metryki",
        f"- lines: {m['lines']}",
        f"- non_empty_lines: {m['non_empty_lines']}",
        f"- imports_count: {m['imports_count']}",
        f"- exports_count: {m['exports_count']}",
        f"- class_count: {m['class_count']}",
        f"- function_like_count: {m['function_like_count']}",
        f"- sha256: `{m['sha256']}`",
        "",
    ])


def _render_references_section(refs: dict, lines: list):
    """Render the references section."""
    lines.extend([
        "## Referencje",
        f"- reverse_imports_count: {len(refs['reverse_imports'])}",
        "",
    ])

    if refs["reverse_imports"]:
        lines.append("### Reverse imports")
        for r in refs["reverse_imports"]:
            lines.append(f"- `{r}`")
        lines.append("")


def _render_duplicates_section(d: dict, lines: list):
    """Render the duplicates section."""
    lines.extend([
        "## Duplikaty",
        f"- exact_duplicates: {len(d['exact_duplicates'])}",
        f"- near_duplicates: {len(d['near_duplicates'])}",
        "",
    ])

    if d["exact_duplicates"]:
        lines.append("### Exact")
        for p in d["exact_duplicates"]:
            lines.append(f"- `{p}`")
        lines.append("")

    if d["near_duplicates"]:
        lines.append("### Near")
        for item in d["near_duplicates"]:
            raw = item.get("raw_similarity", item["similarity"])
            tl = item.get("target_lines", "?")
            cl = item.get("candidate_lines", "?")
            lines.append(
                f"- `{item['path']}` "
                f"similarity={item['similarity']} "
                f"(raw={raw}, lines={tl}/{cl})"
            )
        lines.append("")


def _render_lineage_section(lineage: list, lines: list):
    """Render the file lineage/history section."""
    lines.append("## Historia pliku")
    for c in lineage[:20]:
        lines.append(
            f"- `{c['short_sha']}` {c['date']} {c['author']}: {c['subject']} "
            f"(+{c['insertions']}/-{c['deletions']})"
        )
    lines.append("")


def _render_evolution_section(evolution: list, lines: list):
    """Render the evolution section."""
    if not evolution:
        return
    
    lines.append("## Ewolucja pliku (historia drzewa zależności)")
    lines.append("")
    lines.append("| commit | data | linie | delta | similarity | tree | zmiany w drzewie |")
    lines.append("|---|---|---|---|---|---|---|")
    for e in evolution[:20]:
        tree_info = f"+{len(e['tree_added'])}/-{len(e['tree_removed'])}" if e["tree_changed"] else "="
        tree_detail = ""
        if e["tree_added"]:
            tree_detail += f" +{', '.join(e['tree_added'][:2])}"
        if e["tree_removed"]:
            tree_detail += f" -{', '.join(e['tree_removed'][:2])}"
        lines.append(
            f"| `{e['short_sha']}` {e['date'][:10]} | {e['subject'][:30]} | "
            f"{e['lines']} | {e['line_delta']:+,d} | {e['similarity_to_current']} | "
            f"{e['tree_imports_count']} | {tree_info}{tree_detail[:40]} |"
        )
    lines.append("")


def _render_last_good_section(last_good: list, lines: list):
    """Render the last good versions section."""
    if not last_good:
        return
    
    lines.append("## Ostatnie wersje spełniające kryteria (>= aktualnych linii)")
    for e in last_good:
        lines.append(
            f"- `{e['short_sha']}` {e['date'][:10]} — {e['lines']} linii "
            f"(delta {e['line_delta']:+,d}), similarity={e['similarity_to_current']}, "
            f"'{e['subject']}'"
        )
    lines.append("")


def _render_regression_section(regression: dict, lines: list):
    """Render the regression detective section."""
    if not regression or regression.get("current_all_ok", True):
        return
    
    lines.append("## Regression Detective")
    lines.append("")
    
    broken = regression.get("current_broken_imports", [])
    lines.append(f"### Aktualnie popsute importy ({len(broken)})")
    for b in broken:
        lines.append(f"- `{b}` → **NIE ISTNIEJE** w obecnej wersji")
    lines.append("")

    lw = regression.get("last_working_commit")
    if lw:
        lines.append("### Ostatni działający commit")
        lines.append(
            f"- `{lw['short_sha']}` {lw['date'][:10]} — {lw['lines']} linii, "
            f"{lw['ok_count']} importów OK — '{lw['subject']}'"
        )
        lines.append("")

    fb = regression.get("first_broken_commit")
    if fb:
        lines.append("### Pierwszy popsuty commit")
        lines.append(
            f"- `{fb['short_sha']}` {fb['date'][:10]} — '{fb['subject']}'"
        )
        lines.append("")

    mh = regression.get("missing_imports_history", [])
    if mh:
        lines.append("### Poszukiwanie zaginionych plików w historii")
        for item in mh:
            status = "✅ ZNALEZIONO" if item["history_found"] else "❌ NIE ZNALEZIONO"
            lines.append(
                f"- `{item['import']}` (stem: `{item['stem']}`) — {status} "
                f"({item['history_count']} commitów w historii)"
            )
            if item["last_commit_line"]:
                lines.append(f"  - Ostatni commit: `{item['last_commit_line']}`")
        lines.append("")

    recs = regression.get("recommendations", [])
    if recs:
        lines.append("### Rekomendacje naprawy")
        for i, r in enumerate(recs, 1):
            lines.append(f"{i}. {r}")
        lines.append("")


def render_markdown(report: Dict[str, Any]) -> str:
    lines = [
        f"# REGRES report: `{report['target_file']}`",
        "",
    ]

    _render_classification_section(report.get("classification", {}), lines)
    _render_name_hash_section(report.get("name_hash_candidates", {}), lines)
    _render_metrics_section(report["metrics"], lines)
    _render_references_section(report["references"], lines)
    _render_duplicates_section(report["duplicates"], lines)
    _render_lineage_section(report["lineage"], lines)
    _render_evolution_section(report.get("evolution", []), lines)
    _render_last_good_section(report.get("last_good_version", []), lines)
    _render_regression_section(report.get("regression", {}), lines)

    lines.append("## Prompt-ready context")
    lines.append("```json")
    lines.append(json.dumps(report["llm_context"], ensure_ascii=False, indent=2))
    lines.append("```")
    return "\n".join(lines)


def analyze_file(
    target_file: Path,
    scan_root: Path,
    max_commits: int,
    tree_depth: int,
    near_threshold: float,
) -> Dict[str, Any]:
    repo_root = find_repo_root(target_file.parent)
    target_abs = target_file.resolve()
    if not target_abs.exists() or not target_abs.is_file():
        raise FileNotFoundError(f"Nie znaleziono pliku: {target_file}")
    target_rel = to_rel(target_abs, repo_root)

    text = safe_read_text(target_abs)
    metrics = content_metrics(text, target_abs)
    dep_tree = dependency_tree(target_abs, repo_root, max_depth=tree_depth)
    rev_refs = reverse_references(target_abs, repo_root, scan_root.resolve())
    dups = exact_and_near_duplicates(
        file_path=target_abs,
        repo_root=repo_root,
        scan_root=scan_root.resolve(),
        near_threshold=near_threshold,
    )
    name_hash = trace_name_and_hash_candidates(
        file_path=target_abs,
        repo_root=repo_root,
        scan_root=scan_root.resolve(),
    )

    commits = file_lineage(repo_root, target_rel, max_commits=max_commits)
    lineage = [
        {
            "sha": c.sha,
            "short_sha": c.short_sha,
            "date": c.date,
            "author": c.author,
            "subject": c.subject,
            "file_statuses": c.file_statuses,
            "insertions": c.insertions,
            "deletions": c.deletions,
        }
        for c in commits
    ]

    history_refs = references_in_recent_commits(repo_root, commits, max_commits=12)

    evolution = analyze_evolution(
        repo_root=repo_root,
        rel_path=target_rel,
        commits=commits,
        current_text=text,
        max_depth=1,
    )

    last_good = find_last_good_version(
        evolution,
        min_lines=len(text.splitlines()),
        max_results=3,
    )

    regression = analyze_regression(repo_root, target_rel, commits, text)
    classification = classify_problem(
        repo_root=repo_root,
        target_rel=target_rel,
        current_text=text,
        evolution=evolution,
        regression=regression,
        duplicates=dups,
    )

    report: Dict[str, Any] = {
        "target_file": target_rel,
        "repo_root": str(repo_root),
        "metrics": metrics,
        "dependency_tree": dep_tree,
        "references": {
            "reverse_imports": rev_refs,
            "recent_commit_related_files": history_refs,
        },
        "duplicates": dups,
        "name_hash_candidates": name_hash,
        "lineage": lineage,
        "evolution": evolution,
        "last_good_version": last_good,
        "regression": regression,
        "classification": classification,
    }
    report["llm_context"] = llm_context_packet(report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="REGRES: analiza regresji i rodowodu plików")
    parser.add_argument("--file", required=True, help="Plik docelowy (relative lub absolute)")
    parser.add_argument("--scan-root", default=".", help="Katalog do skanowania referencji i duplikatów")
    parser.add_argument("--max-commits", type=int, default=80, help="Maks. liczba commitów historii")
    parser.add_argument("--tree-depth", type=int, default=3, help="Głębokość drzewa zależności")
    parser.add_argument("--near-threshold", type=float, default=0.92, help="Próg podobieństwa duplikatów")
    parser.add_argument("--out-json", default="", help="Ścieżka output JSON")
    parser.add_argument("--out-md", default="", help="Ścieżka output Markdown")
    args = parser.parse_args()

    cwd = Path.cwd().resolve()
    repo_root = find_repo_root(cwd)

    scan_root = Path(args.scan_root)
    if not scan_root.is_absolute():
        scan_root = (cwd / scan_root).resolve()

    file_path = resolve_target_file(args.file, cwd=cwd, repo_root=repo_root, scan_root=scan_root)

    report = analyze_file(
        target_file=file_path,
        scan_root=scan_root,
        max_commits=args.max_commits,
        tree_depth=args.tree_depth,
        near_threshold=args.near_threshold,
    )

    json_text = json.dumps(report, ensure_ascii=False, indent=2)
    md_text = render_markdown(report)

    if args.out_json:
        out_json = Path(args.out_json)
        if not out_json.is_absolute():
            out_json = (Path.cwd() / out_json).resolve()
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json_text, encoding="utf-8")

    if args.out_md:
        out_md = Path(args.out_md)
        if not out_md.is_absolute():
            out_md = (Path.cwd() / out_md).resolve()
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(md_text, encoding="utf-8")

    if not args.out_json and not args.out_md:
        print(json_text)


if __name__ == "__main__":
    main()