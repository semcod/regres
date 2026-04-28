#!/usr/bin/env python3
"""
doctor_orchestrator.py — analysis orchestrator and diagnosis generator.
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from .doctor_models import Diagnosis, FileAction, ShellCommand


class DoctorOrchestrator:
    """Orchestrator analizy i generator akcji."""

    def __init__(self, scan_root: Path):
        self.scan_root = scan_root.resolve()
        self.diagnoses: List[Diagnosis] = []
        self.analysis_plan: List[Dict[str, Any]] = []
        self.analysis_context: Dict[str, Any] = {}

    # Mapowanie URL paths do katalogów modułów
    MODULE_PATH_MAP = {
        "connect-test": "connect-test/frontend/src/modules/connect-test",
        "connect-test-protocol": "connect-test-protocol/frontend/src/modules/connect-test-protocol",
        "connect-test-device": "connect-test-device/frontend/src/modules/connect-test-device",
        "connect-test-full": "connect-test-full/frontend/src/modules/connect-test-full",
        "connect-scenario": "connect-scenario/frontend/src/modules/connect-scenario",
        "connect-manager": "connect-manager/frontend/src/modules/connect-manager",
        "connect-reports": "connect-reports/frontend/src/modules/connect-reports",
        "connect-config": "connect-config/frontend/src/modules/connect-config",
        "connect-data": "connect-data/backend",
        "connect-deleted": "connect-deleted/frontend/src/modules/connect-deleted",
        "connect-id": "connect-id/frontend/src/modules/connect-id",
        "connect-template": "connect-template/frontend/src/modules/connect-template",
        "connect-workshop": "connect-workshop/frontend/src/modules/connect-workshop",
    }

    URL_ROUTE_MODULE_HINTS = {
        "connect-test/protocol-steps": "connect-test-protocol",
        "connect-test/protocol": "connect-test-protocol",
    }

    # ------------------------------------------------------------------
    # Public analysis API
    # ------------------------------------------------------------------

    def analyze_from_url(self, url: str) -> List[Diagnosis]:
        """Analizuje moduł na podstawie URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            path = parsed.path.strip('/')
        except Exception:
            path = url.strip('/')

        module_name = self._extract_module_name(path)
        if not module_name:
            return []

        module_path = self._resolve_module_path(module_name)
        if not module_path:
            return []

        full_module_path = self.scan_root / module_path
        if not full_module_path.exists():
            return []

        diagnoses = []
        # c2004-maskservice-patch-v2: page implementation analysis runs first
        # so URL-targeted page stubs (e.g. "Strona w trakcie migracji") are
        # detected before broader structural scans.
        diagnoses.extend(self.analyze_page_implementations(path, full_module_path, module_name))
        diagnoses.extend(self.analyze_with_defscan(full_module_path))
        diagnoses.extend(self.analyze_with_refactor(full_module_path))

        for file_path in full_module_path.rglob("*.ts"):
            relative_path = str(file_path.relative_to(self.scan_root))
            git_diags = self.analyze_git_history(relative_path)
            diagnoses.extend(git_diags)

        actionable = self._filter_actionable_diagnoses(diagnoses)
        if actionable:
            return actionable

        fallback = self._build_url_fallback_diagnosis(path, full_module_path)
        return [fallback] if fallback else []

    # ------------------------------------------------------------------
    # Page implementation analysis (URL-targeted stub/placeholder detection)
    # ------------------------------------------------------------------

    PLACEHOLDER_TEXT_PATTERNS = (
        "strona w trakcie migracji",
        "page under migration",
        "coming soon",
        "wkrótce",
        "todo: implement",
        "not implemented yet",
        "placeholder-page",
        "placeholder page",
    )

    # c2004-maskservice-patch-v5: relative-import detection for dependency chain
    # analysis. We use the same regex as the patch-script rewriter so behavior
    # is consistent between detection and remediation.
    _RELATIVE_IMPORT_DQ = re.compile(r'(?:from|import)\s+"(\.{1,2}/[^"]+)"')
    _RELATIVE_IMPORT_SQ = re.compile(r"(?:from|import)\s+'(\.{1,2}/[^']+)'")

    # File extensions tried when resolving an import without explicit suffix.
    _IMPORT_RESOLUTION_SUFFIXES = (".ts", ".tsx", ".js", ".jsx", "/index.ts", "/index.tsx", "/index.js")

    def analyze_dependency_chain(
        self,
        target_file: Path,
        max_depth: int = 1,
    ) -> List[Dict[str, Any]]:
        """Walk relative imports of `target_file` and report resolution status.

        For each import, returns:
          {
            "depth": int,
            "from_file": str (relative to scan_root),
            "import": str (raw import path),
            "resolved_path": Optional[str] (relative; first existing match),
            "exists": bool,
            "is_page_stub": bool,            # True if resolved file is a placeholder page
            "tried": List[str],              # full list of paths tried
          }

        The walk is breadth-first up to `max_depth`. Depth 1 = direct imports of
        the target. We deliberately keep the depth shallow because each broken
        import is itself a candidate for an independent regres analysis run; the
        markdown report links them so the user can perform a chained repair.
        """
        results: List[Dict[str, Any]] = []
        if not target_file.exists():
            return results
        visited: set = set()
        queue: List[tuple] = [(target_file, 1)]
        while queue:
            current, depth = queue.pop(0)
            if depth > max_depth:
                continue
            try:
                key = str(current.resolve())
            except OSError:
                key = str(current)
            if key in visited:
                continue
            visited.add(key)
            try:
                text = current.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            imports = self._extract_relative_imports(text)
            try:
                from_rel = str(current.relative_to(self.scan_root)).replace("\\", "/")
            except ValueError:
                from_rel = str(current)
            for raw in imports:
                resolved, tried = self._resolve_relative_import(current, raw)
                exists = resolved is not None
                is_page_stub = False
                if exists and resolved is not None:
                    if resolved.suffix in (".ts", ".tsx") and resolved.name.endswith(".page.ts"):
                        try:
                            sample = resolved.read_text(encoding="utf-8")
                            lower = sample.lower()
                            if any(p in lower for p in self.PLACEHOLDER_TEXT_PATTERNS):
                                is_page_stub = True
                        except (OSError, UnicodeDecodeError):
                            pass
                resolved_rel = None
                if resolved is not None:
                    try:
                        resolved_rel = str(resolved.relative_to(self.scan_root)).replace("\\", "/")
                    except ValueError:
                        resolved_rel = str(resolved)
                results.append({
                    "depth": depth,
                    "from_file": from_rel,
                    "import": raw,
                    "resolved_path": resolved_rel,
                    "exists": exists,
                    "is_page_stub": is_page_stub,
                    "tried": tried,
                })
                if exists and resolved is not None and depth < max_depth:
                    queue.append((resolved, depth + 1))
        return results

    def _extract_relative_imports(self, text: str) -> List[str]:
        """Extract relative-only imports (./ or ../) from TS/JS source."""
        seen: List[str] = []
        for m in self._RELATIVE_IMPORT_DQ.finditer(text):
            seen.append(m.group(1))
        for m in self._RELATIVE_IMPORT_SQ.finditer(text):
            seen.append(m.group(1))
        # Stable de-dup, preserve order.
        deduped: List[str] = []
        seen_set: set = set()
        for item in seen:
            if item not in seen_set:
                deduped.append(item)
                seen_set.add(item)
        return deduped

    def _resolve_relative_import(
        self,
        from_file: Path,
        raw_import: str,
    ) -> tuple:
        """Try to resolve a relative import to an existing file on disk.

        Returns (resolved_path or None, tried_paths_list).
        """
        base = from_file.parent
        candidates: List[Path] = []
        if "." in raw_import.rsplit("/", 1)[-1]:
            # Has explicit extension or .ext-like segment; try as-is first.
            candidates.append((base / raw_import).resolve())
        for suffix in self._IMPORT_RESOLUTION_SUFFIXES:
            candidates.append((base / (raw_import + suffix)).resolve())
        tried: List[str] = []
        for cand in candidates:
            try:
                rel = str(cand.relative_to(self.scan_root)).replace("\\", "/")
            except ValueError:
                rel = str(cand)
            tried.append(rel)
            if cand.exists() and cand.is_file():
                return cand, tried
        return None, tried

    # c2004-maskservice-patch-v6: Vite runtime probing. Filesystem checks miss
    # cases where (a) the file exists but a Vite alias/mount routes it to a
    # different path, (b) a wrapper file `export *`s from a non-mounted path,
    # or (c) a transitive import in the page-load chain fails. By GET-ing the
    # served URL we get the dev-server's authoritative answer.
    _VITE_FAILED_IMPORT_RE = re.compile(
        r'Failed to resolve import\s+\\?["\']([^"\']+)\\?["\']\s+from\s+\\?["\']([^"\']+)\\?["\']'
    )

    def probe_vite_runtime(
        self,
        vite_base: str,
        file_rel: str,
        timeout: float = 5.0,
    ) -> Dict[str, Any]:
        """GET a single source file from the Vite dev server, parse 500 errors.

        Args:
          vite_base: e.g. "http://localhost:8100" (no trailing slash).
          file_rel: repo-relative path to a file under `frontend/src/...`,
            e.g. "frontend/src/modules/connect-manager/connect-manager.view.ts".
            Will be remapped to the Vite-served URL `/src/...` form.
          timeout: HTTP timeout in seconds.

        Returns dict:
          {
            "url": str,
            "status": int,                  # 0 if request failed
            "ok": bool,                     # 200
            "error_message": Optional[str],
            "missing_import": Optional[str],
            "missing_import_from": Optional[str],
            "transport_error": Optional[str],
          }

        Heuristic: strip a leading `frontend/` from `file_rel` then prepend
        `/src/`. For files under submodule mirrors (e.g. `connect-config/
        frontend/src/modules/connect-config/...`), the mirror is mounted into
        Vite at `/src/modules/connect-config/...`, so we strip the
        `<submodule>/frontend/` prefix.
        """
        import urllib.request
        import urllib.error
        import json as _json

        # Map repo-relative path to Vite-served URL.
        normalized = file_rel.replace("\\", "/")
        # Strip e.g. "connect-config/frontend/" or "frontend/" prefixes.
        m = re.match(r'^(?:[^/]+/)?frontend/(.*)$', normalized)
        if not m:
            return {
                "url": "",
                "status": 0,
                "ok": False,
                "error_message": None,
                "missing_import": None,
                "missing_import_from": None,
                "transport_error": "file_rel not under <module>/frontend/ — cannot derive Vite URL",
            }
        url_path = "/" + m.group(1)
        url = vite_base.rstrip("/") + url_path

        req = urllib.request.Request(url, headers={"Accept": "*/*"})
        body = ""
        status = 0
        transport_error: Optional[str] = None
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                status = resp.status
                body = resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            status = e.code
            try:
                body = e.read().decode("utf-8", errors="replace")
            except Exception:
                body = ""
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            transport_error = str(e)

        ok = status == 200
        missing_import: Optional[str] = None
        missing_import_from: Optional[str] = None
        error_message: Optional[str] = None
        if status >= 400 and body:
            # Vite serves a 500 HTML wrapper containing JSON describing the
            # error. Try the embedded JSON first, then fall back to a regex on
            # the raw body.
            for candidate_match in re.finditer(r'const\s+error\s*=\s*(\{.*?\});', body, re.DOTALL):
                try:
                    err_obj = _json.loads(candidate_match.group(1))
                    error_message = err_obj.get("message") or error_message
                    break
                except Exception:
                    continue
            mfail = self._VITE_FAILED_IMPORT_RE.search(body)
            if mfail:
                missing_import = mfail.group(1)
                missing_import_from = mfail.group(2)

        return {
            "url": url,
            "status": status,
            "ok": ok,
            "error_message": error_message,
            "missing_import": missing_import,
            "missing_import_from": missing_import_from,
            "transport_error": transport_error,
        }

    # c2004-maskservice-patch-v7: lazy-loader contract check. The host's
    # `frontend/src/modules/index.ts` registry only resolves a class if it has
    # either a `default` export OR a class export whose name matches /Module$/.
    # A `<name>.module.ts` entry that exports only e.g. `XxxView` will throw at
    # runtime: `Error: No Module class found in ./<name>/<name>.module.ts`.
    # This check is purely static and complements the Vite runtime probe.
    _MODULE_DEFAULT_EXPORT_RE = re.compile(r"\bexport\s+default\b")
    _MODULE_CLASS_EXPORT_RE = re.compile(
        r"export\s+(?:abstract\s+)?class\s+([A-Z]\w*Module)\b"
    )
    _ANY_CLASS_EXPORT_RE = re.compile(
        r"export\s+(?:abstract\s+)?class\s+([A-Z]\w*)\b"
    )

    def analyze_module_loader_compliance(
        self,
        module_path: Path,
        module_name: str,
    ) -> Optional[Diagnosis]:
        """Detect *.module.ts entry files that won't load via the lazy registry.

        The loader (host `frontend/src/modules/index.ts`) requires either a
        `default` export or a class whose name matches `*Module`. If neither
        is present, runtime throws `No Module class found in ...`.

        Returns a critical Diagnosis when the convention is violated, else None.
        """
        entry = module_path / f"{module_name}.module.ts"
        if not entry.exists() or not entry.is_file():
            return None
        try:
            text = entry.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None
        has_default = bool(self._MODULE_DEFAULT_EXPORT_RE.search(text))
        has_module_class = bool(self._MODULE_CLASS_EXPORT_RE.search(text))
        if has_default or has_module_class:
            return None
        exports = self._ANY_CLASS_EXPORT_RE.findall(text)
        try:
            rel = str(entry.relative_to(self.scan_root)).replace("\\", "/")
        except ValueError:
            rel = str(entry)
        suggested_class = (
            "".join(part.capitalize() for part in module_name.split("-"))
            + "Module"
        )
        view_class = exports[0] if exports else "YourView"
        suggestion_block = (
            "import { ModuleMetadata } from '../module.interface';\n"
            "import { BaseModule } from '../base.module';\n\n"
            f"export class {suggested_class} extends BaseModule {{\n"
            "  readonly metadata: ModuleMetadata = {\n"
            f"    name: '{module_name}',\n"
            "    version: '1.0.0',\n"
            "    dependencies: [],\n"
            "  };\n"
            f"  getDisplayName(): string {{ return '{module_name}'; }}\n"
            "  protected async viewImport() {\n"
            f"    return {{ ViewClass: {view_class} as any }};\n"
            "  }\n"
            "  protected viewArgs(): any[] { return [this]; }\n"
            "}\n\n"
            f"export default {suggested_class};\n"
        )
        nlp = (
            f"Plik `{rel}` jest entry-point modułu, ale **nie eksportuje** klasy "
            f"z sufiksem `*Module` ani `export default`. Loader "
            f"`frontend/src/modules/index.ts` rzuci runtime:\n"
            f"`Error: No Module class found in ./{module_name}/{module_name}.module.ts`.\n\n"
            f"Aktualne eksporty klas: {', '.join(exports) if exports else '(brak)'}.\n\n"
            f"Sugerowany dodatek do pliku:\n```ts\n{suggestion_block}```"
        )
        return Diagnosis(
            summary=(
                f"Module entry `{rel}` nie spełnia konwencji loadera "
                f"(brak `*Module` lub `default`)"
            ),
            problem_type="module_loader_no_class",
            severity="critical",
            nlp_description=nlp,
            file_actions=[FileAction(
                path=rel,
                action="modify",
                reason=(
                    f"Dodaj `export class {suggested_class} extends BaseModule "
                    f"{{ ... }}` oraz `export default {suggested_class};`."
                ),
            )],
            shell_commands=[
                ShellCommand(
                    command=f"sed -n '1,40p' {rel}",
                    description="Podgląd początku pliku",
                ),
                ShellCommand(
                    command=f"grep -nE 'export\\s+(class|default)' {rel}",
                    description="Znajdź obecne eksporty",
                ),
            ],
            confidence=0.95,
        )

    def analyze_page_implementations(
        self,
        route_path: str,
        module_path: Path,
        module_name: str,
    ) -> List[Diagnosis]:
        """Wykrywa stub/placeholder strony powiązane z URL-em."""
        page_token = self._extract_page_token(route_path, module_name)
        if not page_token:
            return []

        candidates = self._find_page_files(module_path, page_token)
        if not candidates:
            return [self._build_missing_page_diagnosis(route_path, module_path, module_name, page_token)]

        diagnoses: List[Diagnosis] = []
        for page_file in candidates:
            diag = self._diagnose_page_stub(page_file, page_token, module_name)
            if diag is not None:
                diagnoses.append(diag)
        return diagnoses

    def _extract_page_token(self, route_path: str, module_name: str) -> Optional[str]:
        """Zwraca sub-token URL po nazwie modułu (np. 'sitemap')."""
        if not route_path:
            return None
        path = route_path.strip('/').split('?', 1)[0]
        first_segment = path.split('/', 1)[0]
        if not first_segment:
            return None
        if first_segment == module_name:
            return None
        if first_segment.startswith(module_name + '-'):
            return first_segment[len(module_name) + 1 :]
        parts = path.split('/')
        if len(parts) > 1 and parts[0] == module_name:
            return parts[1]
        return None

    def _find_page_files(self, module_path: Path, page_token: str) -> List[Path]:
        """Lokalizuje pliki strony pasujące do tokenu URL."""
        token = page_token.lower()
        matches: List[Path] = []
        seen: set = set()
        for file_path in module_path.rglob("*.page.ts"):
            name = file_path.name.lower()
            base = name.replace('.page.ts', '')
            if base == token or base.endswith('-' + token) or base.endswith('.' + token):
                key = str(file_path.resolve())
                if key not in seen:
                    seen.add(key)
                    matches.append(file_path)
        return matches

    # c2004-maskservice-patch-v3: history scan tunables. We default to a
    # 2-day OR 10-iterations window (whichever yields more candidates) so the
    # operator gets enough versions to pick from when the current file looks
    # smaller/different from recent past.
    HISTORY_DEFAULT_DAYS = 2
    HISTORY_DEFAULT_ITERATIONS = 10
    HISTORY_SHRINKAGE_FACTOR = 0.5  # current must be < 50% of recent max to flag

    def _diagnose_page_stub(
        self,
        page_file: Path,
        page_token: str,
        module_name: str,
    ) -> Optional[Diagnosis]:
        """Zwraca diagnozę, jeżeli plik strony to stub/placeholder lub uległa skróceniu."""
        try:
            text = page_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None

        line_count = sum(1 for _ in text.splitlines())
        lower_text = text.lower()
        has_placeholder_text = any(p in lower_text for p in self.PLACEHOLDER_TEXT_PATTERNS)
        is_short_stub = line_count <= 15 and 'render' in text and 'placeholder' in lower_text
        empty_render = bool(re.search(r"render\s*\([^)]*\)\s*[:\w\s<>|]*\{\s*return\s+['\"`]['\"`]\s*;?\s*\}", text))

        try:
            relative = page_file.relative_to(self.scan_root)
        except ValueError:
            relative = page_file
        relative_str = str(relative).replace("\\", "/")

        # Always collect git history candidates for the page name across the
        # repository — even if the current file is not a recognized stub. This
        # lets us flag content regression (e.g. user replaced a 517-line page
        # with a 159-line minimal config form) and offer concrete restore
        # actions with hashes/dates/stats.
        history_candidates = self._collect_page_history_candidates(
            page_token, module_name, page_file,
        )

        max_historical_lines = max((c["line_count"] for c in history_candidates), default=0)
        is_content_regression = (
            history_candidates
            and max_historical_lines > 0
            and line_count < max(40, int(max_historical_lines * self.HISTORY_SHRINKAGE_FACTOR))
            and not has_placeholder_text  # placeholder case handled separately
        )

        if not (has_placeholder_text or is_short_stub or empty_render or is_content_regression):
            return None

        backup_candidate = self._find_backup_page_implementation(page_token, module_name)

        actions: List[FileAction] = [
            FileAction(
                path=relative_str,
                action="modify",
                reason=(
                    f"Plik strony zawiera placeholder ({line_count} linii). "
                    "Zaimplementuj klasę `*Page` z metodami `render()`/`getStyles()`/"
                    "`setupEventListeners()` używanymi przez `pages-index.ts`."
                    if has_placeholder_text or is_short_stub or empty_render
                    else (
                        f"Aktualna wersja ma {line_count} linii, ale w historii git "
                        f"istnieje wersja o {max_historical_lines} liniach. Wybierz "
                        "kandydata z listy historycznej i przywróć jego zawartość."
                    )
                ),
            )
        ]
        commands: List[ShellCommand] = [
            ShellCommand(
                command=f"sed -n '1,40p' {relative_str}",
                description="Podgląd aktualnej zawartości",
            )
        ]

        if has_placeholder_text or is_short_stub or empty_render:
            problem_type = "page_placeholder"
            summary = f"Strona '{page_token}' w module '{module_name}' to placeholder"
            nlp_lines = [
                f"Plik `{relative_str}` jest placeholder-em (długość {line_count} linii). "
                "URL kieruje na ten plik, więc UI pokazuje komunikat zamiast właściwej strony."
            ]
        else:
            problem_type = "page_content_regression"
            summary = (
                f"Strona '{page_token}' uległa skróceniu "
                f"({line_count} linii vs historyczne max {max_historical_lines})"
            )
            nlp_lines = [
                f"Plik `{relative_str}` ma obecnie {line_count} linii, ale w historii git "
                f"występuje wersja {max_historical_lines}-liniowa. Możliwe, że ostatnia "
                "edycja usunęła fragmenty (np. listę dynamicznych tras, sekcje pomocnicze). "
                "Sprawdź kandydatów historycznych i przywróć właściwą zawartość."
            ]

        # Add backup module candidate (other repo location, not git history)
        if backup_candidate:
            backup_str = str(backup_candidate).replace("\\", "/")
            nlp_lines.append(
                f"Pełna implementacja istnieje w `{backup_str}` – możliwe źródło referencyjne."
            )
            actions.append(
                FileAction(
                    path=backup_str,
                    action="review",
                    reason="Źródło referencyjne implementacji do skopiowania",
                )
            )
            commands.append(
                ShellCommand(
                    command=f"diff -u {backup_str} {relative_str}",
                    description="Porównaj implementację referencyjną z aktualnym plikiem",
                )
            )

        # c2004-maskservice-patch-v3: emit git history candidates as actionable
        # restore options. Each candidate lists hash, date, line count, source
        # path (in case the file was renamed/moved) and a short content
        # fingerprint so the user can pick the right version.
        if history_candidates:
            nlp_lines.append(
                f"Znaleziono {len(history_candidates)} kandydatów w historii git "
                f"(okres ostatnie {self.HISTORY_DEFAULT_DAYS} dni lub "
                f"{self.HISTORY_DEFAULT_ITERATIONS} iteracji, sortowane od najnowszego)."
            )
            for cand in history_candidates:
                fp = cand.get("fingerprint") or ""
                fp_short = (fp[:80] + "…") if len(fp) > 80 else fp
                actions.append(
                    FileAction(
                        path=relative_str,
                        action="modify",
                        target=f"git:{cand['hash']}:{cand['source_path']}",
                        reason=(
                            f"[{cand['date']}] {cand['hash']} • "
                            f"{cand['line_count']} linii • {cand['source_path']}"
                            + (f" • {fp_short}" if fp_short else "")
                        ),
                    )
                )
                commands.append(
                    ShellCommand(
                        command=(
                            f"git show {cand['hash']}:{cand['source_path']} "
                            f"> {relative_str}"
                        ),
                        description=(
                            f"Przywróć wersję {cand['hash']} z {cand['date']} "
                            f"({cand['line_count']} linii) jeśli to poprawna treść"
                        ),
                    )
                )
            commands.append(
                ShellCommand(
                    command=(
                        f"for h in "
                        + " ".join(c['hash'] for c in history_candidates[:5])
                        + f"; do echo \"=== $h ===\"; "
                        + "git show $h:"
                        + history_candidates[0]['source_path']
                        + " | wc -l; done"
                    ),
                    description="Porównaj statystyki wszystkich kandydatów",
                )
            )

        confidence = 0.9 if (has_placeholder_text or is_short_stub or empty_render) else 0.7

        return Diagnosis(
            summary=summary,
            problem_type=problem_type,
            severity="high",
            nlp_description=" ".join(nlp_lines),
            file_actions=actions,
            shell_commands=commands,
            confidence=confidence,
        )

    def _collect_page_history_candidates(
        self,
        page_token: str,
        module_name: str,
        current_file: Path,
        days: Optional[int] = None,
        iterations: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Zbiera kandydatów z historii git dla danej strony.

        Strategia:
        1. Wyszukaj wszystkie commity dotyczące plików `*<token>.page.ts`
           w całym repozytorium (głębokość = max(days, iterations)).
        2. Dla każdego (hash, plik) zapisz hash, datę, ścieżkę, liczbę linii
           i krótki fingerprint (pierwsze nietrywialne nagłówki).
        3. Deduplikuj po (hash, ścieżka) i sortuj od najnowszego.
        """
        if not (self.scan_root / ".git").exists():
            return []

        days = days if days is not None else self.HISTORY_DEFAULT_DAYS
        iterations = iterations if iterations is not None else self.HISTORY_DEFAULT_ITERATIONS

        # Pathspecs: any file ending in `<token>.page.ts` anywhere in the repo.
        pathspec = f"*{page_token}.page.ts"
        try:
            since_arg = f"--since={days}.days.ago"
            # Get a wider window initially: max(days*5, iterations*3) commits.
            log_cmd = [
                "git", "log", "--all",
                "--pretty=format:%H|%ad",
                "--date=short",
                "--name-only",
                f"-n{max(iterations * 3, 30)}",
                "--", pathspec,
            ]
            res = subprocess.run(
                log_cmd, cwd=str(self.scan_root),
                capture_output=True, text=True, timeout=30,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return []
        if res.returncode != 0 or not res.stdout.strip():
            return []

        # Parse commits — alternating "hash|date" lines and file paths.
        candidates: List[Dict[str, Any]] = []
        seen_keys: set = set()
        current_commit: Optional[Dict[str, Any]] = None
        for line in res.stdout.splitlines():
            if not line.strip():
                current_commit = None
                continue
            if "|" in line and len(line.split("|", 1)[0]) == 40:
                commit_hash, date_str = line.split("|", 1)
                current_commit = {"hash": commit_hash[:8], "full_hash": commit_hash, "date": date_str}
                continue
            if current_commit is None:
                continue
            file_path = line.strip()
            if not file_path.endswith(f"{page_token}.page.ts") and not file_path.endswith(".page.ts"):
                continue
            # Match the page token in the basename
            base = file_path.rsplit("/", 1)[-1].lower().replace(".page.ts", "")
            tok = page_token.lower()
            if not (base == tok or base.endswith("-" + tok)):
                continue
            key = (current_commit["full_hash"], file_path)
            if key in seen_keys:
                continue
            seen_keys.add(key)

            # Read content at this commit
            try:
                show = subprocess.run(
                    ["git", "show", f"{current_commit['full_hash']}:{file_path}"],
                    cwd=str(self.scan_root),
                    capture_output=True, text=True, timeout=10,
                )
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
            if show.returncode != 0:
                continue
            content = show.stdout
            line_count = content.count("\n") + (0 if content.endswith("\n") else 1)
            fingerprint = self._fingerprint_page_content(content)
            candidates.append({
                "hash": current_commit["hash"],
                "full_hash": current_commit["full_hash"],
                "date": current_commit["date"],
                "source_path": file_path,
                "line_count": line_count,
                "fingerprint": fingerprint,
            })

        # Sort newest first by date+hash; cap to iterations.
        candidates.sort(key=lambda c: (c["date"], c["full_hash"]), reverse=True)
        # De-dupe near-identical sizes from same source_path keeping newest.
        deduped: List[Dict[str, Any]] = []
        size_seen: set = set()
        for c in candidates:
            sig = (c["source_path"], c["line_count"])
            if sig in size_seen:
                continue
            size_seen.add(sig)
            deduped.append(c)
            if len(deduped) >= iterations:
                break
        return deduped

    def _fingerprint_page_content(self, content: str) -> str:
        """Krótki opis zawartości — wyciąga znaczące nagłówki/tytuły z HTML/string."""
        keywords: List[str] = []
        # Extract <h1>..<h3>, page-header titles, and known section markers.
        for match in re.finditer(r"<h[1-3][^>]*>([^<]{3,80})</h[1-3]>", content, re.IGNORECASE):
            keywords.append(match.group(1).strip())
            if len(keywords) >= 3:
                break
        for match in re.finditer(r"\b(label|title)>([^<]{3,80})<", content, re.IGNORECASE):
            keywords.append(match.group(2).strip())
            if len(keywords) >= 5:
                break
        # Detect signature sections in the page (Polish UI hints).
        for marker in ("Wszystkie dostępne strony", "Sitemap", "Konfiguracja",
                       "Lista", "Tabela", "Routes", "discoveredRoutes"):
            if marker in content and marker not in keywords:
                keywords.append(marker)
        return "; ".join(dict.fromkeys(keywords))[:200]

    def _find_backup_page_implementation(
        self,
        page_token: str,
        module_name: str,
    ) -> Optional[Path]:
        """Szuka pełnej implementacji strony w innych modułach (np. *-network/ui/)."""
        token = page_token.lower()
        modules_dir = self.scan_root / "modules"
        if not modules_dir.exists():
            return None
        best_candidate: Optional[Path] = None
        best_size = 0
        for path in modules_dir.rglob("*.page.ts"):
            name = path.name.lower()
            base = name.replace('.page.ts', '')
            if not (base == token or base.endswith('-' + token)):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            lower_text = text.lower()
            if any(p in lower_text for p in self.PLACEHOLDER_TEXT_PATTERNS):
                continue
            line_count = sum(1 for _ in text.splitlines())
            if line_count < 30:
                continue
            if line_count > best_size:
                best_size = line_count
                best_candidate = path
        if best_candidate is None:
            return None
        try:
            return best_candidate.relative_to(self.scan_root)
        except ValueError:
            return best_candidate

    def _build_missing_page_diagnosis(
        self,
        route_path: str,
        module_path: Path,
        module_name: str,
        page_token: str,
    ) -> Diagnosis:
        """Diagnoza dla URL nie mającego pliku strony w module."""
        try:
            module_relative = module_path.relative_to(self.scan_root)
        except ValueError:
            module_relative = module_path
        module_str = str(module_relative).replace("\\", "/")

        backup = self._find_backup_page_implementation(page_token, module_name)
        actions: List[FileAction] = [
            FileAction(
                path=f"{module_str}/pages/{module_name}-{page_token}.page.ts",
                action="modify",
                reason=(
                    f"Brak pliku strony dla URL '/{route_path}'. Utwórz nową klasę "
                    f"strony z metodami `render`/`getStyles` i zarejestruj ją w "
                    f"`pages-index.ts` pod kluczem '{page_token}'."
                ),
            )
        ]
        commands: List[ShellCommand] = [
            ShellCommand(
                command=f"grep -RIn \"'{page_token}'\" {module_str}",
                description="Sprawdź czy klucz strony jest już zarejestrowany",
            )
        ]
        if backup is not None:
            backup_str = str(backup).replace("\\", "/")
            actions.append(
                FileAction(
                    path=backup_str,
                    action="review",
                    reason="Skopiuj implementację referencyjną",
                )
            )
            commands.append(
                ShellCommand(
                    command=f"cat {backup_str}",
                    description="Pokaż kod referencyjny strony",
                )
            )
        return Diagnosis(
            summary=f"Brak strony '{page_token}' w module '{module_name}'",
            problem_type="page_missing",
            severity="high",
            nlp_description=(
                f"URL '/{route_path}' wskazuje na stronę o tokenie '{page_token}', "
                f"ale nie znaleziono żadnego pliku `*-{page_token}.page.ts` w "
                f"`{module_str}`."
            ),
            file_actions=actions,
            shell_commands=commands,
            confidence=0.85,
        )

    @staticmethod
    def _filter_actionable_diagnoses(diagnoses: List[Diagnosis]) -> List[Diagnosis]:
        """Retain only diagnoses that can actually be acted on."""
        actionable: List[Diagnosis] = []
        for diag in diagnoses:
            if diag.file_actions or diag.shell_commands:
                actionable.append(diag)
                continue
            if diag.problem_type == "import_error":
                actionable.append(diag)
        return actionable

    def _build_url_fallback_diagnosis(self, route_path: str, module_path: Path) -> Optional[Diagnosis]:
        """Create a targeted guidance diagnosis when no actionable findings were generated."""
        candidates: List[str] = []
        token_candidates = [
            route_path.split("/")[-1],
            route_path.replace("/", "-"),
        ]
        for token in token_candidates:
            token = token.strip()
            if not token:
                continue
            for file_path in module_path.rglob("*.ts"):
                name = file_path.name.lower()
                if token.lower() in name:
                    try:
                        candidates.append(str(file_path.relative_to(self.scan_root)).replace("\\", "/"))
                    except ValueError:
                        continue
        candidates = list(dict.fromkeys(candidates))[:5]

        actions = [
            FileAction(
                path=p,
                action="review",
                reason="Sprawdź dynamiczne importy, eksporty strony i powiązanie z rejestrem page managera",
            )
            for p in candidates
        ]

        frontend_cwd = self.scan_root / "frontend"
        commands = [
            ShellCommand(
                command=(
                    f"python -m regres.regres_cli import-error-toon-report --frontend-cwd {frontend_cwd} "
                    f"--scan-root {self.scan_root} --out-md {self.scan_root / '.regres' / 'import-error-toon-report.md'} "
                    f"--out-raw-log {self.scan_root / '.regres' / 'import-error-toon-report.raw.log'}"
                ),
                description="Odśwież import diagnostics zanim zaproponujesz naprawę",
            )
        ]

        return Diagnosis(
            summary=f"Brak jednoznacznej automatycznej naprawy dla trasy '{route_path}'",
            problem_type="url_targeted_review",
            severity="low",
            nlp_description=(
                "Automatyczna analiza strukturalna nie wykryła bezpośredniej, pewnej naprawy. "
                "Raport został zawężony do kroków diagnostycznych i plików najbardziej związanych z trasą URL."
            ),
            file_actions=actions,
            shell_commands=commands,
            confidence=0.6,
        )

    def analyze_import_errors(self, log_path: Path) -> List[Diagnosis]:
        """Analizuje błędy importów z logu TS."""
        if not log_path.exists():
            return []

        diagnoses = []
        errors_by_file = self._parse_ts_errors(log_path)

        for file_path, errors in errors_by_file.items():
            validated_errors = self._validate_errors(file_path, errors)
            if not validated_errors:
                continue

            missing_modules = self._extract_missing_modules(validated_errors)
            if missing_modules:
                diag = self._diagnose_import_issue(file_path, missing_modules)
                diagnoses.append(diag)

        return diagnoses

    def analyze_duplicates(self, report_path: Path) -> List[Diagnosis]:
        """Analizuje duplikaty z raportu defscan."""
        if not report_path.exists():
            return []

        diagnoses = []
        try:
            with open(report_path, encoding="utf-8") as f:
                data = json.load(f)

            for item in data.get("duplicates", []):
                if item.get("count", 0) > 1:
                    diag = self._diagnose_duplicate(item)
                    diagnoses.append(diag)
        except (json.JSONDecodeError, KeyError):
            pass

        return diagnoses

    def analyze_git_history(self, file_path: str) -> List[Diagnosis]:
        """Analizuje historię git pliku aby wykryć wzorce scope."""
        if not (self.scan_root / ".git").exists():
            return []

        diagnoses = []
        try:
            cmd = ["git", "log", "--oneline", "--follow", "--", file_path]
            result = subprocess.run(
                cmd,
                cwd=str(self.scan_root),
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    diag = self._analyze_history_patterns(file_path, lines)
                    if diag:
                        diagnoses.append(diag)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return diagnoses

    def analyze_with_defscan(self, path: Path) -> List[Diagnosis]:
        """Używa defscan do analizy duplikatów w konkretnym katalogu."""
        diagnoses = []
        try:
            cmd = [sys.executable, "-m", "regres.defscan", "--path", str(path), "--json"]
            result = subprocess.run(
                cmd,
                cwd=str(self.scan_root),
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout)
                duplicates = data if isinstance(data, list) else data.get("duplicates", [])
                for item in duplicates:
                    if item.get("count", 0) > 1:
                        diag = self._diagnose_duplicate(item)
                        diagnoses.append(diag)
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            pass

        return diagnoses

    def analyze_with_refactor(self, path: Path) -> List[Diagnosis]:
        """Używa refactor do analizy kodu w konkretnym katalogu."""
        diagnoses = []
        try:
            cmd = [sys.executable, "-m", "regres.refactor", "wrappers", "--path", str(path)]
            result = subprocess.run(
                cmd,
                cwd=str(self.scan_root),
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                wrapper_count = len([l for l in lines if 'wrapper' in l.lower()])

                if wrapper_count > 0:
                    actions = [FileAction(
                        path=str(path),
                        action="review",
                        reason=f"Wykryto {wrapper_count} wrapperów - sprawdź czy są potrzebne"
                    )]
                    commands = [ShellCommand(
                        command=f"regres refactor wrappers --path {path}",
                        description="Przejrzyj wrappery w katalogu"
                    )]
                    diagnoses.append(Diagnosis(
                        summary=f"Wykryto {wrapper_count} wrapperów w {path}",
                        problem_type="wrapper_analysis",
                        severity="low",
                        nlp_description=f"W katalogu {path} wykryto {wrapper_count} plików-wrapper. Należy przejrzeć czy wszystkie są potrzebne czy można je usunąć.",
                        file_actions=actions,
                        shell_commands=commands,
                        confidence=0.6
                    ))
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return diagnoses

    def apply_fixes(self, diagnoses: List[Diagnosis], dry_run: bool = True) -> Dict[str, Any]:
        """Wykonuje akcje naprawcze z diagnoz."""
        results = {
            "dry_run": dry_run,
            "actions_performed": [],
            "errors": []
        }

        for diag in diagnoses:
            for action in diag.file_actions:
                self._apply_file_action(action, dry_run, results)

            for cmd in diag.shell_commands:
                self._apply_shell_command(cmd, dry_run, results)

        return results

    def generate_llm_diagnosis(self, url: str, module_path: Path) -> str:
        """Generuje szczegółowy raport markdown z kontekstem historycznym i strukturalnym."""
        sections = [
            self._build_header(url, module_path),
            self._build_section("## Git History Context", self._collect_git_context(module_path)),
            self._build_section("## Code Structure Analysis", self._collect_structure_context(module_path)),
            self._build_section("## Duplicate Analysis (defscan)", self._collect_defscan_context(module_path)),
            self._build_section("## Wrapper Analysis (refactor)", self._collect_refactor_context(module_path)),
            self._build_nlp_diagnosis(module_path),
            self._build_proposed_fixes(module_path),
            self._build_shell_commands(module_path),
            self._build_playbook(module_path),
            self._build_summary(module_path),
        ]
        return "\n".join(sections)

    def generate_report(self) -> Dict[str, Any]:
        """Generuje kompletny raport diagnoz."""
        # c2004-maskservice-patch-v4: dedupe diagnoses produced by overlapping
        # analyzers (np. analyze_from_url + analyze_page_implementations).
        # Klucz: (summary, problem_type, primary modify path).
        deduped: List[Diagnosis] = []
        seen_keys: set = set()
        for diag in self.diagnoses:
            primary_path = next(
                (a.path for a in diag.file_actions
                 if a.action == "modify" and not (a.target or "").startswith("git:")),
                "",
            )
            key = (diag.summary, diag.problem_type, primary_path)
            if key in seen_keys:
                continue
            seen_keys.add(key)
            deduped.append(diag)
        self.diagnoses = deduped
        return {
            "scan_root": str(self.scan_root),
            "analysis_plan": self.analysis_plan,
            "analysis_context": self.analysis_context,
            "affected_files": self.summarize_affected_files(),
            "diagnoses": [
                {
                    "summary": d.summary,
                    "problem_type": d.problem_type,
                    "severity": d.severity,
                    "nlp_description": d.nlp_description,
                    "file_actions": [
                        {
                            "path": a.path,
                            "action": a.action,
                            "target": a.target,
                            "reason": a.reason
                        }
                        for a in d.file_actions
                    ],
                    "shell_commands": [
                        {
                            "command": c.command,
                            "description": c.description,
                            "cwd": c.cwd
                        }
                        for c in d.shell_commands
                    ],
                    "confidence": d.confidence
                }
                for d in self.diagnoses
            ]
        }

    def render_markdown(self, report: Dict[str, Any]) -> str:
        """Renderuje raport w formacie Markdown."""
        lines = ["# Doctor Report\n", f"**Scan Root:** `{report['scan_root']}`\n", f"**Diagnoses:** {len(report['diagnoses'])}\n"]

        lines.extend(self._render_decision_workflow(report))
        lines.extend(self._render_affected_files(report))
        lines.extend(self._render_dependency_chain(report))
        lines.extend(self._render_structure_snapshot(report))
        lines.extend(self._render_preliminary_refactor_proposals(report))

        for i, diag in enumerate(report['diagnoses'], 1):
            severity_emoji = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}.get(diag['severity'], "⚪")
            lines.append(f"## {severity_emoji} {i}. {diag['summary']}")
            lines.append(f"**Type:** {diag['problem_type']} | **Severity:** {diag['severity']} | **Confidence:** {diag['confidence']:.0%}\n")
            lines.append(f"**Description:** {diag['nlp_description']}\n")

            if diag['file_actions']:
                lines.append("### File Actions")
                lines.append("```")
                for action in diag['file_actions']:
                    lines.append(f"{action['action']}: {action['path']}")
                    if action.get('target'):
                        lines.append(f"  -> {action['target']}")
                    if action.get('reason'):
                        lines.append(f"  ({action['reason']})")
                lines.append("```\n")

            if diag['shell_commands']:
                lines.append("### Shell Commands")
                lines.append("```bash")
                for cmd in diag['shell_commands']:
                    lines.append(f"# {cmd['description']}")
                    lines.append(cmd['command'])
                    if cmd['cwd']:
                        lines.append(f"# cwd: {cmd['cwd']}")
                    lines.append("")
                lines.append("```")
                lines.append("")

        normalized_diags = self._normalize_diagnoses(report.get('diagnoses', []))
        lines.extend(self._render_step_by_step_playbook(normalized_diags, llm_mode=False))
        return "\n".join(lines)

    def reset_analysis_plan(self) -> None:
        self.analysis_plan = []

    def add_plan_step(
        self,
        name: str,
        reason: str,
        command: str,
        status: str = "planned",
        details: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None,
        outputs: Optional[Dict[str, Any]] = None,
        decision: Optional[str] = None,
    ) -> None:
        """Rejestruje krok planu z pełnym kontekstem decyzji.

        - inputs: predykaty/parametry, na podstawie których krok wybrano
          (np. {"url": "...", "module_name": "connect-config", "had_route_hint": True}).
        - outputs: rezultaty kroku (np. {"placeholder_files_found": 1}).
        - decision: krótkie zdanie wyjaśniające: dlaczego ten krok teraz, na bazie inputs.
        """
        step: Dict[str, Any] = {
            "name": name,
            "reason": reason,
            "command": command,
            "status": status,
        }
        if details:
            step["details"] = details
        if inputs:
            step["inputs"] = inputs
        if outputs:
            step["outputs"] = outputs
        if decision:
            step["decision"] = decision
        self.analysis_plan.append(step)

    def update_last_plan_step(self, **kwargs: Any) -> None:
        """Aktualizuje ostatni dodany krok planu (np. po wykonaniu)."""
        if not self.analysis_plan:
            return
        self.analysis_plan[-1].update(kwargs)

    def set_analysis_context(self, key: str, value: Any) -> None:
        self.analysis_context[key] = value

    # c2004-maskservice-patch-v4: collect a single source of truth for which
    # files would be modified by the diagnoses, so the report (and any
    # downstream patch script generation) can show the user exactly what
    # changes are proposed.
    def summarize_affected_files(self) -> List[Dict[str, Any]]:
        seen: Dict[str, Dict[str, Any]] = {}
        for diag in self.diagnoses:
            for action in diag.file_actions:
                if action.action not in ("modify", "create", "delete", "move"):
                    continue
                key = action.path
                if key not in seen:
                    seen[key] = {
                        "path": action.path,
                        "actions": [],
                        "diagnoses": [],
                    }
                target = action.target or ""
                seen[key]["actions"].append({
                    "action": action.action,
                    "target": target,
                    "reason": action.reason,
                    "problem_type": diag.problem_type,
                })
                if diag.summary not in seen[key]["diagnoses"]:
                    seen[key]["diagnoses"].append(diag.summary)
        return list(seen.values())

    # c2004-maskservice-patch-v4: per-candidate `.sh` patch generator.
    # When a diagnosis lists several restore candidates (e.g. multiple git
    # history hashes for a `page_content_regression`), we want the user to
    # be able to apply each one independently with a backup safety-net.
    def generate_patch_scripts(
        self,
        out_dir: Path,
        basename: str,
    ) -> List[Dict[str, str]]:
        """Tworzy `.sh` patche dla każdej opcji w diagnozach.

        Zwraca listę metadanych: [{"path": ..., "diagnosis": ..., "candidate": ..., "kind": ...}].
        Każdy skrypt:
          1. Drukuje banner co robi.
          2. Sprawdza czy plik docelowy istnieje (jeśli tak — backup z timestampem).
          3. Aplikuje zmianę (git show / cp / sed).
          4. Drukuje podsumowanie + wskazówkę jak cofnąć (revert hint).
        """
        out_dir.mkdir(parents=True, exist_ok=True)
        generated: List[Dict[str, str]] = []
        index_lines: List[str] = [
            "#!/usr/bin/env bash",
            "# Auto-generated patch index by regres doctor",
            f"# Basename: {basename}",
            "# Use: bash <patch-file>.sh",
            "",
            "set -euo pipefail",
            "",
            'cat <<"EOF"',
            "Available patches (run any of them individually):",
            "EOF",
            "",
        ]

        counter = 0
        for diag_idx, diag in enumerate(self.diagnoses, 1):
            # Group git history candidates per diagnosis.
            history_candidates = [
                a for a in diag.file_actions
                if a.action == "modify" and (a.target or "").startswith("git:")
            ]
            if history_candidates:
                # Detect target file (the "modify" action without git target).
                primary_target_path = None
                for a in diag.file_actions:
                    if a.action == "modify" and not (a.target or "").startswith("git:"):
                        primary_target_path = a.path
                        break
                if primary_target_path is None and history_candidates:
                    primary_target_path = history_candidates[0].path

                for cand_idx, cand_action in enumerate(history_candidates, 1):
                    counter += 1
                    target_spec = cand_action.target or ""
                    # target format: git:<short_hash>:<source_path>
                    parts = target_spec.split(":", 2)
                    if len(parts) != 3:
                        continue
                    _, git_hash, source_path = parts
                    script_path = out_dir / (
                        f"{basename}-patch-{counter:02d}-{git_hash}.sh"
                    )
                    script_lines = self._render_patch_script(
                        diag=diag,
                        diag_idx=diag_idx,
                        cand_idx=cand_idx,
                        total_cands=len(history_candidates),
                        git_hash=git_hash,
                        source_path=source_path,
                        target_path=primary_target_path or "",
                        reason=cand_action.reason,
                    )
                    script_path.write_text("\n".join(script_lines), encoding="utf-8")
                    try:
                        script_path.chmod(0o755)
                    except OSError:
                        pass
                    generated.append({
                        "path": str(script_path),
                        "diagnosis": diag.summary,
                        "candidate": git_hash,
                        "kind": "git_history_restore",
                    })
                    index_lines.append(
                        f'echo "  bash {script_path.name}  # [{diag.problem_type}] {git_hash} → {primary_target_path}"'
                    )

            # Fallback: plain shell commands not tied to candidate hashes.
            if not history_candidates and diag.shell_commands:
                # Only generate a script if there is a real "modify" action.
                modify_action = next(
                    (a for a in diag.file_actions if a.action == "modify"), None,
                )
                if modify_action is None:
                    continue
                counter += 1
                script_path = out_dir / (
                    f"{basename}-patch-{counter:02d}-{diag.problem_type}.sh"
                )
                script_lines = self._render_generic_patch_script(
                    diag=diag,
                    diag_idx=diag_idx,
                    target_path=modify_action.path,
                )
                script_path.write_text("\n".join(script_lines), encoding="utf-8")
                try:
                    script_path.chmod(0o755)
                except OSError:
                    pass
                generated.append({
                    "path": str(script_path),
                    "diagnosis": diag.summary,
                    "candidate": diag.problem_type,
                    "kind": "manual_fix",
                })
                index_lines.append(
                    f'echo "  bash {script_path.name}  # [{diag.problem_type}] manual fix → {modify_action.path}"'
                )

        if generated:
            index_path = out_dir / f"{basename}-patches-index.sh"
            index_lines.append("")
            index_path.write_text("\n".join(index_lines), encoding="utf-8")
            try:
                index_path.chmod(0o755)
            except OSError:
                pass
            generated.insert(0, {
                "path": str(index_path),
                "diagnosis": "INDEX",
                "candidate": "",
                "kind": "index",
            })

        return generated

    def _render_patch_script(
        self,
        diag: "Diagnosis",
        diag_idx: int,
        cand_idx: int,
        total_cands: int,
        git_hash: str,
        source_path: str,
        target_path: str,
        reason: str,
    ) -> List[str]:
        """Render a `.sh` patch script with three modes:

        - default (apply): backup + restore + import-path rewrite
        - `--preview`: show first 60 lines + diff vs current; no modification
        - `--diff`: show full diff vs current; no modification
        """
        scan_root = str(self.scan_root)
        return [
            "#!/usr/bin/env bash",
            "# Auto-generated by regres doctor — git history restore patch.",
            f"# Diagnosis #{diag_idx}: {diag.summary}",
            f"# Candidate {cand_idx}/{total_cands}: {git_hash}",
            f"# Reason: {reason}",
            "#",
            "# Modes:",
            f"#   bash {Path('.').name}/<patch>.sh             # apply (backup → restore → rewrite imports)",
            f"#   bash {Path('.').name}/<patch>.sh --preview   # show content + diff, no changes",
            f"#   bash {Path('.').name}/<patch>.sh --diff      # show full unified diff vs current",
            "",
            "set -euo pipefail",
            "",
            f'SCAN_ROOT="{scan_root}"',
            f'TARGET="{target_path}"',
            f'GIT_HASH="{git_hash}"',
            f'SOURCE_PATH="{source_path}"',
            f'TS="$(date +%Y%m%dT%H%M%S)"',
            'BACKUP="${TARGET}.before-${TS}"',
            'MODE="${1:-apply}"',
            "",
            'cd "$SCAN_ROOT"',
            "",
            'echo "[regres-patch] Diagnosis: ' + diag.summary.replace('"', '\\"') + '"',
            'echo "[regres-patch] Mode: $MODE"',
            'echo "[regres-patch] Source: ${GIT_HASH}:${SOURCE_PATH}"',
            'echo "[regres-patch] Target: ${TARGET}"',
            "",
            "# ---------- Preview / Diff modes ----------",
            'if [ "$MODE" = "--preview" ]; then',
            '  echo "[regres-patch] === Remote content (first 60 lines) ==="',
            '  git show "${GIT_HASH}:${SOURCE_PATH}" | sed -n "1,60p"',
            '  echo "[regres-patch] === Diff vs current target (unified, max 200 lines) ==="',
            '  if [ -f "$TARGET" ]; then',
            '    diff -u <(git show "${GIT_HASH}:${SOURCE_PATH}") "$TARGET" | sed -n "1,200p" || true',
            '  else',
            '    echo "(target does not exist yet)"',
            '  fi',
            '  exit 0',
            'fi',
            'if [ "$MODE" = "--diff" ]; then',
            '  if [ -f "$TARGET" ]; then',
            '    diff -u <(git show "${GIT_HASH}:${SOURCE_PATH}") "$TARGET" || true',
            '  else',
            '    git show "${GIT_HASH}:${SOURCE_PATH}"',
            '  fi',
            '  exit 0',
            'fi',
            "",
            "# ---------- Apply mode ----------",
            'if [ -f "$TARGET" ]; then',
            '  cp -p "$TARGET" "$BACKUP"',
            '  echo "[regres-patch] Backup saved: $BACKUP"',
            "else",
            '  mkdir -p "$(dirname "$TARGET")"',
            '  echo "[regres-patch] Target did not exist; will be created."',
            "fi",
            "",
            'git show "${GIT_HASH}:${SOURCE_PATH}" > "$TARGET"',
            'echo "[regres-patch] Wrote $(wc -l < "$TARGET") lines to $TARGET"',
            "",
            "# ---------- Rewrite relative imports for new location ----------",
            "# When restoring content from a historical path, relative imports may",
            "# become invalid in two ways:",
            "#   A) the new directory has a different depth than the historical one",
            "#   B) the new file lives in a mirrored module root (e.g. connect-config/",
            "#      frontend/src/...) — imports must be resolved within the new tree,",
            "#      not against the original repo-root layout.",
            "# We detect the closest 'src/' (or 'frontend/src/') boundary above the",
            "# target file and remap each import suffix into that mirror tree before",
            "# computing the new relative path.",
            f'SOURCE_DIR="$(dirname "${{SOURCE_PATH}}")"',
            f'TARGET_DIR="$(dirname "${{TARGET}}")"',
            'if [ "$SOURCE_DIR" != "$TARGET_DIR" ]; then',
            '  echo "[regres-patch] Source dir ($SOURCE_DIR) ≠ target dir ($TARGET_DIR); rewriting relative imports..."',
            '  python3 - "$TARGET" "$SOURCE_DIR" "$TARGET_DIR" <<\'PYEOF\'',
            "import os, re, sys",
            "target, source_dir, target_dir = sys.argv[1], sys.argv[2], sys.argv[3]",
            "with open(target, 'r', encoding='utf-8') as f:",
            "    text = f.read()",
            "",
            "def detect_src_root(d):",
            "    parts = d.replace(os.sep, '/').split('/')",
            "    # Prefer the closest 'src' segment to the file. If preceded by",
            "    # 'frontend', use 'frontend/src' as the boundary.",
            "    for i in range(len(parts) - 1, -1, -1):",
            "        if parts[i] == 'src':",
            "            if i > 0 and parts[i - 1] == 'frontend':",
            "                return '/'.join(parts[:i + 1]), 'frontend/src'",
            "            return '/'.join(parts[:i + 1]), 'src'",
            "    return None, None",
            "",
            "src_source, marker_source = detect_src_root(source_dir)",
            "src_target, marker_target = detect_src_root(target_dir)",
            "",
            "import_re_dq = re.compile(r'(from\\s+|import\\s+)(\")(\\.{1,2}/[^\"]+)(\")')",
            "import_re_sq = re.compile(r'(from\\s+|import\\s+)(\\')(\\.{1,2}/[^\\']+)(\\')')",
            "rewritten_count = 0",
            "",
            "def rewrite(m):",
            "    global rewritten_count",
            "    prefix, q1, path, q2 = m.group(1), m.group(2), m.group(3), m.group(4)",
            "    # Step 1: resolve historical absolute (repo-root-relative) using source_dir.",
            "    abs_resolved = os.path.normpath(os.path.join(source_dir, path))",
            "    # Step 2: if both source and target sit inside a 'src' tree, remap by",
            "    # swapping the source 'src/' root prefix for the target 'src/' root prefix.",
            "    if src_source and src_target and abs_resolved.startswith(src_source + '/'):",
            "        suffix = abs_resolved[len(src_source) + 1:]",
            "        abs_resolved = src_target + '/' + suffix",
            "    # Step 3: compute new relative from target_dir.",
            "    new_rel = os.path.relpath(abs_resolved, start=target_dir)",
            "    if not new_rel.startswith('.'):",
            "        new_rel = './' + new_rel",
            "    new_rel = new_rel.replace(os.sep, '/')",
            "    rewritten_count += 1",
            "    return f'{prefix}{q1}{new_rel}{q2}'",
            "",
            "text2 = import_re_dq.sub(rewrite, text)",
            "text2 = import_re_sq.sub(rewrite, text2)",
            "if text2 != text:",
            "    with open(target, 'w', encoding='utf-8') as f:",
            "        f.write(text2)",
            "    print(f'[regres-patch] Rewrote {rewritten_count} relative imports.')",
            "    print(f'[regres-patch]   src boundary: {marker_source} → {marker_target}')",
            "else:",
            "    print('[regres-patch] No relative imports needed rewriting.')",
            "PYEOF",
            "fi",
            "",
            "# ---------- Verify (best-effort) ----------",
            "echo \"[regres-patch] First 5 imports after restore:\"",
            'grep -E "^import |^from " "$TARGET" | head -5 || true',
            "",
            'echo "[regres-patch] Done. To revert:"',
            'if [ -f "$BACKUP" ]; then',
            '  echo "  cp \\"$BACKUP\\" \\"$TARGET\\""',
            "else",
            '  echo "  rm \\"$TARGET\\"   # target was created from scratch"',
            "fi",
            "",
        ]

    def _render_generic_patch_script(
        self,
        diag: "Diagnosis",
        diag_idx: int,
        target_path: str,
    ) -> List[str]:
        scan_root = str(self.scan_root)
        lines = [
            "#!/usr/bin/env bash",
            "# Auto-generated by regres doctor — manual fix patch.",
            f"# Diagnosis #{diag_idx}: {diag.summary}",
            f"# Problem type: {diag.problem_type}",
            "#",
            "# This patch is a thin wrapper around the suggested shell commands.",
            "# Review and edit before running if you are unsure.",
            "",
            "set -euo pipefail",
            "",
            f'SCAN_ROOT="{scan_root}"',
            f'TARGET="{target_path}"',
            f'TS="$(date +%Y%m%dT%H%M%S)"',
            'BACKUP="${TARGET}.before-${TS}"',
            "",
            'cd "$SCAN_ROOT"',
            "",
            'if [ -f "$TARGET" ]; then',
            '  cp -p "$TARGET" "$BACKUP"',
            '  echo "[regres-patch] Backup saved: $BACKUP"',
            "fi",
            "",
        ]
        for cmd in diag.shell_commands:
            desc = cmd.description.replace('"', '\\"')
            lines.append(f'echo "[regres-patch] {desc}"')
            lines.append(cmd.command)
            lines.append("")
        lines.append('echo "[regres-patch] Done. Review changes and revert from \\"$BACKUP\\" if needed."')
        lines.append("")
        return lines

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _extract_module_name(self, path: str) -> Optional[str]:
        normalized_path = path.strip('/')
        for route_prefix, mapped_module in self.URL_ROUTE_MODULE_HINTS.items():
            if normalized_path.startswith(route_prefix):
                return mapped_module

        for possible_module in self.MODULE_PATH_MAP.keys():
            if path.startswith(possible_module):
                return possible_module
        parts = path.split('/')
        return parts[0] if parts else None

    def _resolve_module_path(self, module_name: str) -> Optional[str]:
        module_path = self.MODULE_PATH_MAP.get(module_name)
        if module_path and (self.scan_root / module_path).exists():
            return module_path
        for possible_path in [
            f"{module_name}/frontend/src/modules/{module_name}",
            f"{module_name}/frontend/src",
            f"{module_name}/backend",
            f"frontend/src/modules/{module_name}",
            module_name,
            f"src/{module_name}",
        ]:
            full_path = self.scan_root / possible_path
            if full_path.exists():
                return possible_path
        return None

    def _import_exists_in_source(self, file_path: str, module_name: str) -> bool:
        """Sprawdza czy dany import (niezakomentowany) wciąż istnieje w pliku źródłowym."""
        full_path = self.scan_root / file_path
        if not full_path.exists():
            return False
        try:
            text = full_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return False

        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
                continue
            if module_name in line and ("import " in line or "from " in line or "require(" in line):
                return True
        return False

    def _resolve_alias_target(self, alias_path: str) -> Optional[str]:
        """Próbuje znaleźć rzeczywistą ścieżkę dla aliasu @c2004/*."""
        suffix = alias_path.replace("@c2004/", "")
        candidates = [
            self.scan_root / "frontend" / "src" / suffix,
            self.scan_root / "frontend" / "src" / "modules" / suffix,
            self.scan_root / "frontend" / "src" / "components" / suffix,
            self.scan_root / suffix,
        ]
        for cand in candidates:
            if cand.exists():
                return str(cand.relative_to(self.scan_root)).replace("\\", "/")
            for ext in (".ts", ".tsx", ".js", ".json"):
                if cand.with_suffix(ext).exists():
                    return str(cand.with_suffix(ext).relative_to(self.scan_root)).replace("\\", "/")
            if (cand / "index.ts").exists():
                return str((cand / "index.ts").relative_to(self.scan_root)).replace("\\", "/")
        return None

    def _parse_ts_errors(self, log_path: Path) -> Dict[str, List[str]]:
        """Parsuje log błędów TS."""
        errors_by_file = {}
        ts2307_re = re.compile(r"TS2307:.*?Cannot find module '([^']+)'")
        ts2305_re = re.compile(r"TS2305:.*?has no exported member '([^']+)'")
        file_re = re.compile(r"([^\s]+\.ts[^\s]*?)\((\d+),\d+\)")

        current_file = None

        with open(log_path, encoding="utf-8") as f:
            for line in f:
                file_match = file_re.search(line)
                if file_match:
                    current_file = file_match.group(1)

                if current_file:
                    if "TS2307" in line or "TS2305" in line:
                        errors_by_file.setdefault(current_file, []).append(line)

        return errors_by_file

    def _validate_errors(self, file_path: str, errors: List[str]) -> List[str]:
        validated = []
        for err_line in errors:
            mod_match = re.search(r"Cannot find module '([^']+)'", err_line)
            if mod_match:
                module_name = mod_match.group(1)
                if self._import_exists_in_source(file_path, module_name):
                    validated.append(err_line)
            else:
                validated.append(err_line)
        return validated

    def _extract_missing_modules(self, errors: List[str]) -> List[str]:
        modules = []
        ts2307_re = re.compile(r"Cannot find module '([^']+)'")
        for error in errors:
            match = ts2307_re.search(error)
            if match:
                modules.append(match.group(1))
        return list(set(modules))

    def _diagnose_import_issue(self, file_path: str, missing_modules: List[str]) -> Diagnosis:
        """Diagnozuje problem z importami i generuje plan naprawy."""
        actions = []
        commands = []
        concrete_fixes: List[str] = []

        for module in missing_modules:
            if module.startswith("@c2004/"):
                alias = module.replace("@c2004/", "")
                resolved = self._resolve_alias_target(module)
                if resolved:
                    actions.append(FileAction(
                        path=file_path,
                        action="modify",
                        reason=f"Zmień import `{module}` na relatywną ścieżkę do `{resolved}` (lub dodaj alias w vite.config.ts)"
                    ))
                    concrete_fixes.append(f"`{module}` → `../{resolved}` (dostosuj głębokość)")
                else:
                    actions.append(FileAction(
                        path=file_path,
                        action="modify",
                        reason=f"Zmień import `{module}` na poprawną ścieżkę (plik nie istnieje pod żadnym znanym aliasem)"
                    ))
                commands.append(ShellCommand(
                    command=f"grep -n '{module}' {file_path}",
                    description=f"Znajdź import {module} w pliku"
                ))
            elif module.startswith("./") or module.startswith("../"):
                source_dir = (self.scan_root / file_path).parent
                target = source_dir / module
                ext_checks = [".ts", ".tsx", ".js", ""]
                found = any((target.with_suffix(ext) if ext else target).exists() for ext in ext_checks)
                if not found:
                    actions.append(FileAction(
                        path=file_path,
                        action="modify",
                        reason=f"Ścieżka `{module}` nie istnieje względem `{file_path}`"
                    ))
                    commands.append(ShellCommand(
                        command=f"ls -la {(source_dir / module).parent} 2>/dev/null || echo 'Brak katalogu'",
                        description=f"Sprawdź czy katalog dla {module} istnieje"
                    ))
                else:
                    actions.append(FileAction(
                        path=file_path,
                        action="modify",
                        reason=f"Plik `{module}` istnieje, ale brakuje w nim eksportu – sprawdź nazwę symbolu"
                    ))

        nlp_desc = (
            f"W pliku `{file_path}` wykryto błędy importów dla modułów: {', '.join(missing_modules)}. "
            + (f"Sugerowane poprawki: {', '.join(concrete_fixes)}. " if concrete_fixes else "")
            + "Należy sprawdzić konfigurację ścieżek w tsconfig.json / vite.config.ts oraz upewnić się, "
            "że wszystkie wymagane moduły są dostępne w monorepo."
        )

        severity = "high" if len(missing_modules) > 3 else "medium"
        if not concrete_fixes and not any(a.action == "modify" for a in actions):
            severity = "low"

        return Diagnosis(
            summary=f"Błędy importów w {file_path}",
            problem_type="import_error",
            severity=severity,
            nlp_description=nlp_desc,
            file_actions=actions,
            shell_commands=commands,
            confidence=0.85 if concrete_fixes else 0.6
        )

    def _diagnose_duplicate(self, duplicate_data: Dict[str, Any]) -> Diagnosis:
        """Diagnozuje problem z duplikatami."""
        name = duplicate_data.get("name", "unknown")
        count = duplicate_data.get("count", 0)
        locations = duplicate_data.get("locations", [])

        actions = []
        commands = []

        if count > 2:
            main_location = self._find_main_location(locations)
            for loc in locations:
                if loc != main_location:
                    actions.append(FileAction(
                        path=loc,
                        action="delete",
                        reason=f"Duplikat {name} - zachowaj tylko w {main_location}"
                    ))
                    commands.append(ShellCommand(
                        command=f"rm {loc}",
                        description=f"Usuń duplikat {name}"
                    ))

        nlp_desc = (
            f"Wykryto {count} duplikatów definicji '{name}'. "
            "Należy skonsolidować definicje w jednym miejscu, "
            f"najlepiej w pakiecie shared, i usunąć pozostałe kopie."
        )

        return Diagnosis(
            summary=f"Duplikat definicji '{name}' ({count} wystąpień)",
            problem_type="duplicate",
            severity="medium",
            nlp_description=nlp_desc,
            file_actions=actions,
            shell_commands=commands,
            confidence=0.9
        )

    def _find_main_location(self, locations: List[str]) -> str:
        for loc in locations:
            if "shared" in loc.lower():
                return loc
        return locations[0] if locations else ""

    def _analyze_history_patterns(self, file_path: str, history_lines: List[str]) -> Optional[Diagnosis]:
        move_keywords = ['move', 'rename', 'refactor', 'extract', 'migrate']
        move_count = sum(1 for line in history_lines if any(kw in line.lower() for kw in move_keywords))

        if move_count >= 2:
            actions = []
            commands = []
            if (
                ('connect-test' in file_path or 'connect-test-protocol' in file_path)
                and ('protocol' in file_path or 'connect-protocol' in str(history_lines).lower())
            ):
                actions.append(FileAction(
                    path=file_path,
                    action="review",
                    reason=f"Plik był przenoszony {move_count} razy - sprawdź czy jest w odpowiednim module"
                ))
                commands.append(ShellCommand(
                    command=f"git log --follow --oneline -- {file_path}",
                    description="Sprawdź historię pliku"
                ))

            return Diagnosis(
                summary=f"Plik {file_path} ma bogatą historię zmian ({move_count} przeniesień)",
                problem_type="scope_drift",
                severity="medium",
                nlp_description=f"Plik {file_path} był wielokrotnie przenoszony ({move_count} razy). Należy sprawdzić czy jest w odpowiednim module scope czy wymaga konsolidacji.",
                file_actions=actions,
                shell_commands=commands,
                confidence=0.7
            )
        return None

    def _apply_file_action(self, action: FileAction, dry_run: bool, results: Dict[str, Any]) -> None:
        try:
            if action.action == "modify":
                record = {"action": action.action, "path": action.path, "reason": action.reason}
                if dry_run:
                    record["dry_run"] = True
                results["actions_performed"].append(record)
            elif action.action == "delete":
                if not dry_run:
                    file_path = self.scan_root / action.path
                    if file_path.exists():
                        file_path.unlink()
                record = {"action": action.action, "path": action.path, "reason": action.reason}
                if dry_run:
                    record["dry_run"] = True
                results["actions_performed"].append(record)
            elif action.action == "move":
                if not dry_run:
                    src = self.scan_root / action.path
                    dst = self.scan_root / action.target if action.target else None
                    if src.exists() and dst:
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        src.rename(dst)
                record = {"action": action.action, "path": action.path, "target": action.target, "reason": action.reason}
                if dry_run:
                    record["dry_run"] = True
                results["actions_performed"].append(record)
        except Exception as e:
            results["errors"].append({"action": action.action, "path": action.path, "error": str(e)})

    def _apply_shell_command(self, cmd: ShellCommand, dry_run: bool, results: Dict[str, Any]) -> None:
        try:
            if not dry_run:
                result = subprocess.run(
                    cmd.command,
                    shell=True,
                    cwd=cmd.cwd or str(self.scan_root),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                results["actions_performed"].append({
                    "action": "shell_command",
                    "command": cmd.command,
                    "description": cmd.description,
                    "cwd": cmd.cwd,
                    "returncode": result.returncode
                })
            else:
                results["actions_performed"].append({
                    "action": "shell_command",
                    "command": cmd.command,
                    "description": cmd.description,
                    "cwd": cmd.cwd,
                    "dry_run": True
                })
        except Exception as e:
            results["errors"].append({"command": cmd.command, "error": str(e)})

    # ------------------------------------------------------------------
    # LLM report sections
    # ------------------------------------------------------------------

    def _build_header(self, url: str, module_path: Path) -> str:
        return f"""# LLM-Based Diagnosis Report
**URL:** {url}
**Module Path:** {module_path}
**Scan Root:** {self.scan_root}
"""

    @staticmethod
    def _build_section(title: str, content: str) -> str:
        return f"{title}\n\n{content}\n"

    def _build_nlp_diagnosis(self, module_path: Path) -> str:
        lines = ["## NLP Diagnosis & Recommendations\n", "### Problem Summary", "Based on the analysis above, the following issues were detected:", ""]
        all_diagnoses = self._collect_all_diagnoses(module_path)
        if all_diagnoses:
            for i, diag in enumerate(all_diagnoses, 1):
                lines.append(f"{i}. **{diag.summary}**")
                lines.append(f"   - Type: {diag.problem_type}")
                lines.append(f"   - Severity: {diag.severity}")
                lines.append(f"   - Confidence: {diag.confidence:.0%}")
                lines.append(f"   - {diag.nlp_description}")
                lines.append("")
        else:
            lines.append("No issues detected in this module.")
            lines.append("")
        return "\n".join(lines)

    def _build_proposed_fixes(self, module_path: Path) -> str:
        lines = ["## Proposed Fixes\n"]
        all_diagnoses = self._collect_all_diagnoses(module_path)
        for diag in all_diagnoses:
            if diag.file_actions:
                lines.append(f"### Fix for: {diag.summary}")
                lines.append("")
                lines.append("```typescript")
                lines.append("// Proposed code changes:")
                for action in diag.file_actions:
                    if action.action == "modify":
                        lines.append(f"// Modify: {action.path}")
                        lines.append(f"// Reason: {action.reason}")
                lines.append("```")
                lines.append("")
        return "\n".join(lines)

    def _build_shell_commands(self, module_path: Path) -> str:
        lines = ["## Shell Commands to Execute\n", "```bash"]
        all_diagnoses = self._collect_all_diagnoses(module_path)
        for diag in all_diagnoses:
            for cmd in diag.shell_commands:
                lines.append(f"# {cmd.description}")
                lines.append(cmd.command)
                if cmd.cwd:
                    lines.append(f"# cwd: {cmd.cwd}")
                lines.append("")
        lines.append("```")
        return "\n".join(lines)

    def _build_playbook(self, module_path: Path) -> str:
        all_diagnoses = self._collect_all_diagnoses(module_path)
        normalized = self._normalize_diagnoses([
            {"summary": d.summary, "nlp_description": d.nlp_description,
             "file_actions": [{"path": a.path, "action": a.action, "target": a.target, "reason": a.reason} for a in d.file_actions],
             "shell_commands": [{"command": c.command, "description": c.description, "cwd": c.cwd} for c in d.shell_commands]}
            for d in all_diagnoses
        ])
        return "\n".join(self._render_step_by_step_playbook(normalized, llm_mode=True))

    def _build_summary(self, module_path: Path) -> str:
        all_diagnoses = self._collect_all_diagnoses(module_path)
        total = len(all_diagnoses)
        files = len(list(module_path.rglob('*.ts')))
        confidence = (sum(d.confidence for d in all_diagnoses) / total if total else 0)
        return f"""## Summary

- Total issues detected: {total}
- Files analyzed: {files}
- Confidence score: {confidence:.0%}
"""

    def _collect_all_diagnoses(self, module_path: Path) -> List[Diagnosis]:
        diagnoses = []
        diagnoses.extend(self.analyze_with_defscan(module_path))
        diagnoses.extend(self.analyze_with_refactor(module_path))
        for file_path in module_path.rglob("*.ts"):
            relative_path = str(file_path.relative_to(self.scan_root))
            diagnoses.extend(self.analyze_git_history(relative_path))
        return diagnoses

    def _normalize_diagnoses(self, diagnoses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return diagnoses

    def _render_decision_workflow(self, report: Dict[str, Any]) -> List[str]:
        lines = ["## Decision Workflow", ""]
        plan = report.get("analysis_plan", []) or []
        if not plan:
            lines.append("Brak zarejestrowanego planu decyzyjnego.")
            lines.append("")
            return lines

        lines.append("Drzewo decyzyjne — każdy krok pokazuje predykaty wejściowe, decyzję i rezultat:")
        lines.append("")
        for idx, step in enumerate(plan, 1):
            status = step.get("status", "planned")
            status_icon = {
                "done": "✓", "warning": "⚠", "skipped": "⊘",
                "planned": "…", "error": "✗",
            }.get(status, "•")
            lines.append(f"{idx}. {status_icon} **{step.get('name', 'step')}** [{status}] — {step.get('reason', '')}")
            if step.get("decision"):
                lines.append(f"   - **Decision:** {step['decision']}")
            if step.get("inputs"):
                inputs_str = ", ".join(
                    f"`{k}`={self._fmt_plan_value(v)}" for k, v in step["inputs"].items()
                )
                lines.append(f"   - **Inputs:** {inputs_str}")
            if step.get("outputs"):
                outputs_str = ", ".join(
                    f"`{k}`={self._fmt_plan_value(v)}" for k, v in step["outputs"].items()
                )
                lines.append(f"   - **Outputs:** {outputs_str}")
            if step.get("details"):
                lines.append(f"   - **Details:** {step['details']}")
        lines.append("")
        lines.append("```bash")
        for step in plan:
            cmd = step.get("command")
            if cmd:
                lines.append(f"# {step.get('name', 'step')} [{step.get('status', 'planned')}]")
                lines.append(cmd)
                lines.append("")
        lines.append("```")
        lines.append("")
        return lines

    @staticmethod
    def _fmt_plan_value(value: Any) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        if value is None:
            return "null"
        if isinstance(value, (list, tuple)):
            return "[" + ", ".join(str(v) for v in value) + "]"
        s = str(value)
        if len(s) > 80:
            return s[:77] + "..."
        return s

    def _render_affected_files(self, report: Dict[str, Any]) -> List[str]:
        affected = report.get("affected_files", []) or []
        lines = ["## Affected Files", ""]
        if not affected:
            lines.append("Brak plików do zmiany — diagnozy nie proponują modyfikacji.")
            lines.append("")
            return lines
        lines.append(
            f"Pliki, które zostałyby zmienione przez sugestie regres ({len(affected)} unikalnych):"
        )
        lines.append("")
        patch_index = self._build_candidate_patch_index(report)
        for entry in affected:
            actions = entry.get("actions", []) or []
            diag_summary = "; ".join(entry.get("diagnoses", []) or [])
            target_path = entry["path"]
            lines.append(f"### `{target_path}`")
            if diag_summary:
                lines.append(f"_Diagnozy:_ {diag_summary}")
            lines.append("")
            direct = [a for a in actions if not (a.get("target") or "").startswith("git:")]
            git_cands = [a for a in actions if (a.get("target") or "").startswith("git:")]
            if direct:
                lines.append("**Bezpośrednie akcje:**")
                for a in direct:
                    extra = f" → `{a['target']}`" if a.get("target") else ""
                    lines.append(f"- `{a['action']}`{extra} — {a.get('reason', '')}")
                lines.append("")
            if git_cands:
                lines.append(f"**Kandydaci z historii git ({len(git_cands)}, od najnowszego):**")
                lines.append("")
                for a in git_cands:
                    target_spec = a.get("target", "")
                    parts = target_spec.split(":", 2)
                    if len(parts) != 3:
                        lines.append(f"- `{target_spec}` — {a.get('reason', '')}")
                        continue
                    _, h, src = parts
                    patch_path = patch_index.get((target_path, h))
                    lines.append(f"#### Kandydat `{h}` ← `{src}`")
                    lines.append(f"_{a.get('reason', '')}_")
                    lines.append("")
                    lines.append("**Sprawdź zanim zastosujesz:**")
                    lines.append("```bash")
                    lines.append(f"# 1) Podgląd zdalnej zawartości (60 linii) i diff vs current:")
                    if patch_path:
                        lines.append(f"bash {patch_path} --preview")
                    else:
                        lines.append(
                            f'git show {h}:{src} | sed -n "1,60p"\n'
                            f'diff -u <(git show {h}:{src}) {target_path}'
                        )
                    lines.append("")
                    lines.append(f"# 2) Pełen unified diff:")
                    if patch_path:
                        lines.append(f"bash {patch_path} --diff")
                    else:
                        lines.append(f"diff -u <(git show {h}:{src}) {target_path}")
                    lines.append("")
                    lines.append(f"# 3) Zastosuj (backup + restore + auto-rewrite import paths):")
                    if patch_path:
                        lines.append(f"bash {patch_path}")
                    else:
                        lines.append(f"git show {h}:{src} > {target_path}")
                    lines.append("```")
                    lines.append("")
        return lines

    def _build_candidate_patch_index(
        self, report: Dict[str, Any],
    ) -> Dict[tuple, str]:
        """Map (target_path, git_hash) → patch script path for cross-reference."""
        index: Dict[tuple, str] = {}
        patches = report.get("generated_patches", []) or []
        # Need pair (target, hash). target_path comes from diag's primary modify
        # action; we re-derive that from `self.diagnoses` since the report dict
        # is the merged view. patches list has 'candidate'=hash and 'diagnosis'.
        diag_target_map: Dict[str, str] = {}
        for diag in self.diagnoses:
            primary = next(
                (a.path for a in diag.file_actions
                 if a.action == "modify" and not (a.target or "").startswith("git:")),
                "",
            )
            diag_target_map[diag.summary] = primary
        for p in patches:
            if p.get("kind") != "git_history_restore":
                continue
            target = diag_target_map.get(p.get("diagnosis", ""), "")
            cand = p.get("candidate", "")
            if target and cand:
                index[(target, cand)] = p.get("path", "")
        return index

    def _render_dependency_chain(self, report: Dict[str, Any]) -> List[str]:
        """Render the per-target dependency chain results stored in context."""
        chains = report.get("analysis_context", {}).get("dependency_chains", []) or []
        lines: List[str] = ["## Dependency Chain", ""]
        if not chains:
            return []
        lines.append(
            "Po analizie strony URL, regres prześledził relatywne importy każdego "
            "wykrytego pliku celu. Niespójne importy oznaczają, że po przywróceniu "
            "treści historycznej trzeba wykonać dodatkowe kroki naprawy."
        )
        lines.append("")
        for entry in chains:
            target = entry.get("target", "")
            chain = entry.get("chain", []) or []
            lines.append(f"### `{target}`")
            if not chain:
                lines.append("Brak relatywnych importów (lub plik niedostępny).")
                lines.append("")
                continue
            broken = [c for c in chain if not c.get("exists")]
            stubs = [c for c in chain if c.get("is_page_stub")]
            ok = [c for c in chain if c.get("exists") and not c.get("is_page_stub")]
            lines.append(
                f"_Imports total:_ {len(chain)} | "
                f"_OK:_ {len(ok)} | "
                f"_Broken:_ {len(broken)} | "
                f"_Page stubs (transitive):_ {len(stubs)}"
            )
            lines.append("")
            if broken:
                lines.append("**Niezresolwowane importy (wymagają dalszej analizy):**")
                lines.append("")
                for c in broken:
                    lines.append(f"- `{c['import']}` z `{c['from_file']}`")
                    lines.append(f"  - Tried: {', '.join('`' + t + '`' for t in c.get('tried', [])[:4])}")
                    suggested_url = self._suggest_url_for_path(c['import'])
                    if suggested_url:
                        lines.append(
                            f"  - **Następny krok:** `regres doctor --scan-root {self.scan_root} "
                            f"--url '{suggested_url}' --all --git-history --out-md "
                            f".regres/{Path(c['import']).stem}-doctor.md`"
                        )
                lines.append("")
            if stubs:
                lines.append("**Importy wskazujące na placeholder pages (cascade repair):**")
                lines.append("")
                for c in stubs:
                    resolved = c.get("resolved_path", "?")
                    lines.append(f"- `{resolved}` ← imported as `{c['import']}` z `{c['from_file']}`")
                    suggested_url = self._suggest_url_for_path(resolved)
                    if suggested_url:
                        lines.append(
                            f"  - **Naprawa łańcuchowa:** `regres doctor --scan-root {self.scan_root} "
                            f"--url '{suggested_url}' --all --git-history --out-md "
                            f".regres/{Path(resolved).stem}-doctor.md`"
                        )
                lines.append("")
            if ok and not broken and not stubs:
                lines.append("Wszystkie importy są poprawne — łańcuch zależności jest spójny.")
                lines.append("")
        # Append a guidance block when there is at least one broken/stub link.
        if any(
            (not c.get("exists")) or c.get("is_page_stub")
            for entry in chains for c in (entry.get("chain") or [])
        ):
            lines.append("### Multi-step repair plan")
            lines.append("")
            lines.append("Wieloetapowy plan naprawy łańcuchowej:")
            lines.append("")
            lines.append("1. **Napraw najpierw plik celu** (URL z błędem) używając jednego z patchy `.sh` powyżej.")
            lines.append("2. **Zrefreshuj stronę**. Jeśli runtime nadal pokazuje błąd, zobacz Vite/console.")
            lines.append("3. **Uruchom regres na każdym broken/stub imporcie** — komendy są podane wyżej.")
            lines.append("4. **Powtórz krok 1-3** dla każdego pliku w łańcuchu, aż wszystkie importy są zresolwowane.")
            lines.append("5. **Zweryfikuj** poprzez `curl -s -o /dev/null -w '%{http_code}' <vite_url>` — oczekiwany 200.")
            lines.append("")
        return lines

    def _suggest_url_for_path(self, raw_or_path: str) -> Optional[str]:
        """Best-effort guess: given a TS path, propose a URL/route to feed back into regres.

        Heuristics:
          - If the path contains `pages/<name>.page.ts`, propose `http://localhost:8100/<name>`.
          - Otherwise, return None (caller will skip the suggestion).
        """
        token = raw_or_path.replace("\\", "/")
        m = re.search(r"pages/([^/]+)\.page\.ts", token)
        if m:
            return f"http://localhost:8100/{m.group(1)}"
        # Trailing path segment without .page suffix — at least propose a URL stub.
        m2 = re.search(r"/([a-z0-9][a-z0-9\-]+)(?:\.ts|\.tsx)?$", token, re.IGNORECASE)
        if m2:
            return f"http://localhost:8100/{m2.group(1)}"
        return None

    def _render_structure_snapshot(self, report: Dict[str, Any]) -> List[str]:
        lines = ["## Project Structure Snapshot", ""]
        snapshot = report.get("analysis_context", {}).get("structure_snapshot", [])
        if not snapshot:
            return lines
        lines.append("```text")
        lines.extend(snapshot)
        lines.append("```")
        lines.append("")
        return lines

    def _render_preliminary_refactor_proposals(self, report: Dict[str, Any]) -> List[str]:
        lines = ["## Preliminary Refactor Proposals", ""]
        proposals = report.get("analysis_context", {}).get("preliminary_refactor_proposals", [])
        if not proposals:
            lines.append("Brak wstępnych propozycji refaktoryzacji.")
            lines.append("")
            return lines
        lines.append("```markdown")
        for item in proposals:
            lines.append(f"- {item}")
        lines.append("```")
        lines.append("")
        return lines

    def collect_structure_snapshot(self, max_entries: int = 80) -> List[str]:
        entries: List[str] = []
        preferred_roots = [
            self.scan_root / "frontend" / "src",
            self.scan_root / "connect-manager" / "frontend" / "src",
            self.scan_root / "connect-scenario" / "frontend" / "src",
        ]

        for root in preferred_roots:
            if root.exists() and root.is_dir():
                for p in root.rglob("*.ts"):
                    try:
                        entries.append(str(p.relative_to(self.scan_root)).replace("\\", "/"))
                    except ValueError:
                        continue
                    if len(entries) >= max_entries:
                        return entries
        return entries

    def collect_preliminary_refactor_proposals(self) -> List[str]:
        proposals: List[str] = []
        for d in self.diagnoses:
            if d.problem_type == "duplicate":
                proposals.append(d.summary)
            elif d.problem_type == "wrapper_analysis":
                proposals.append(d.summary)
            elif d.problem_type == "scope_drift":
                proposals.append(d.summary)
            elif d.problem_type == "import_error":
                proposals.append(d.summary)
        # dedupe preserving order
        return list(dict.fromkeys(proposals))

    def _render_step_by_step_playbook(self, diagnoses: List[Dict[str, Any]], llm_mode: bool = False) -> List[str]:
        """Renderuje playbook krok po kroku."""
        lines = ["## Step-by-Step Repair Playbook", ""]
        if not diagnoses:
            lines.append("Brak kroków naprawczych do wykonania.")
            lines.append("")
            return lines

        for idx, diag in enumerate(diagnoses, 1):
            summary = diag.get("summary", "Issue")
            description = diag.get("nlp_description", "")
            file_actions = diag.get("file_actions", []) or []
            shell_commands = diag.get("shell_commands", []) or []
            paths = sorted({a.get("path") for a in file_actions if a.get("path")})

            lines.append(f"### Step {idx}. {summary}")
            if description:
                lines.append(description)
            lines.append("")
            lines.extend(self._render_analyze_step(shell_commands, paths))
            lines.extend(self._render_apply_step(llm_mode, paths))
            lines.extend(self._render_validate_step(paths))
        return lines

    def _render_analyze_step(self, shell_commands: List[Dict[str, Any]], paths: List[str]) -> List[str]:
        lines = ["**1) Analyze**", "```bash"]
        if shell_commands:
            for cmd in shell_commands[:6]:
                if cmd.get("description"):
                    lines.append(f"# {cmd['description']}")
                if cmd.get("command"):
                    lines.append(cmd["command"])
                if cmd.get("cwd"):
                    lines.append(f"# cwd: {cmd['cwd']}")
                lines.append("")
        elif paths:
            for p in paths:
                lines.append(f'grep -n "import" {p}')
        else:
            lines.append("# Brak shell commands dla tej diagnozy")
        lines.append("```")
        lines.append("")
        return lines

    def _render_apply_step(self, llm_mode: bool, paths: List[str]) -> List[str]:
        lines = ["**2) Apply changes**"]
        if llm_mode:
            lines.append("```text")
            lines.append("Task: Apply the patch(es) below exactly, one file at a time.")
            lines.append("Rules: Keep scope minimal, edit only indicated imports/exports, do not refactor unrelated code.")
            lines.append("After patching: run validation commands from step 3.")
            lines.append("```")
            lines.append("")
        lines.append("```diff")
        if paths:
            for p in paths:
                lines.append("*** Begin Patch")
                lines.append(f"*** Update File: {p}")
                lines.append("@@")
                lines.append("-<old_code>")
                lines.append("+<new_code>")
                lines.append("*** End Patch")
                lines.append("")
        else:
            lines.append("# No file path detected for this diagnosis")
            lines.append("# Add a focused patch for the affected file manually")
        lines.append("```")
        lines.append("")
        return lines

    def _render_validate_step(self, paths: List[str]) -> List[str]:
        lines = ["**3) Validate**", "```bash"]
        lines.append("python -m regres.regres_cli doctor --scan-root . --all --out-md .regres/doctor-after-step.md")
        if paths:
            for p in paths[:3]:
                lines.append(f'grep -n "Cannot find module" .regres/import-error-toon-report.raw.log | grep "{p}" || true')
        lines.append("```")
        lines.append("")
        return lines

    # ------------------------------------------------------------------
    # Context collectors
    # ------------------------------------------------------------------

    def _collect_git_context(self, module_path: Path) -> str:
        lines = ["```bash", "# Recent commits affecting this module"]
        try:
            cmd = ["git", "log", "--oneline", "-10", "--", str(module_path)]
            result = subprocess.run(
                cmd,
                cwd=str(self.scan_root),
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                lines.append(result.stdout.strip())
            else:
                lines.append("# Git history not available")
        except Exception:
            lines.append("# Git history not available")
        lines.append("```")
        return "\n".join(lines)

    def _collect_structure_context(self, module_path: Path) -> str:
        lines = ["```", "# Directory structure"]
        for item in sorted(module_path.rglob("*")):
            if item.is_file() and item.suffix == ".ts":
                rel = item.relative_to(module_path)
                lines.append(f"  {rel}")
        lines.append("```")
        return "\n".join(lines)

    def _collect_defscan_context(self, module_path: Path) -> str:
        lines = []
        try:
            from regres import defscan
            import io
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            try:
                sys.argv = ["defscan", "--path", str(module_path), "--json"]
                defscan.main()
                output = sys.stdout.getvalue()
            finally:
                sys.stdout = old_stdout
            if output.strip():
                data = json.loads(output)
                duplicates = data if isinstance(data, list) else data.get("duplicates", [])
                if duplicates:
                    lines.append(f"Found {len(duplicates)} duplicate definitions")
                    for dup in duplicates[:5]:
                        if isinstance(dup, dict):
                            lines.append(f"- {dup.get('name', 'unknown')}: {dup.get('count', 0)} occurrences")
                        else:
                            lines.append(f"- {dup}")
                else:
                    lines.append("No duplicates found")
            else:
                lines.append("No duplicates found")
        except Exception as e:
            lines.append(f"Defscan analysis error: {str(e)}")
        return "\n".join(lines)

    def _collect_refactor_context(self, module_path: Path) -> str:
        lines = []
        try:
            from regres import refactor
            import io
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            try:
                sys.argv = ["refactor", "--path", str(module_path), "wrappers"]
                refactor.main()
                output = sys.stdout.getvalue()
            finally:
                sys.stdout = old_stdout
            if output.strip():
                lines.append(output.strip())
            else:
                lines.append("No wrappers found")
        except Exception as e:
            lines.append(f"Refactor analysis error: {str(e)}")
        return "\n".join(lines)
