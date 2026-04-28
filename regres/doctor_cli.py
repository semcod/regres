#!/usr/bin/env python3
"""
doctor_cli.py — CLI entry point and helpers for doctor module.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from .doctor_models import Diagnosis
from .doctor_orchestrator import DoctorOrchestrator
from .version_check import check_version
try:
    from importlib.metadata import version as _get_version
except ImportError:
    from importlib_metadata import version as _get_version  # type: ignore[no-redef]


def _handle_url_mode(args, doctor: DoctorOrchestrator, scan_root: Path) -> None:
    """Handle URL-based discovery and analysis mode."""
    from urllib.parse import urlparse

    doctor.reset_analysis_plan()

    parsed = urlparse(args.url)
    normalized_path = parsed.path.strip('/')
    module_name = None
    route_hint = None

    for hint, mapped_module in doctor.URL_ROUTE_MODULE_HINTS.items():
        if normalized_path.startswith(hint):
            route_hint = mapped_module
            module_name = mapped_module
            break

    if not module_name:
        for possible_module in doctor.MODULE_PATH_MAP.keys():
            if normalized_path.startswith(possible_module):
                module_name = possible_module
                break

    if not module_name:
        parts = normalized_path.split('/')
        if parts:
            module_name = parts[0]

    doctor.add_plan_step(
        name="url discovery",
        reason="Wyznaczenie modułu docelowego i zakresu analizy na podstawie URL.",
        command=f"python -m regres.regres_cli doctor --scan-root {scan_root} --url {args.url}",
        status="done",
        details=(
            f"route hint matched: {route_hint}" if route_hint
            else f"module inferred: {module_name or 'unknown'}"
        ),
        inputs={
            "url": args.url,
            "url_path": normalized_path,
            "had_route_hint": bool(route_hint),
        },
        outputs={
            "module_name": module_name or "unknown",
            "route_hint": route_hint,
        },
        decision=(
            f"URL prefix dopasowany do hint-a `{route_hint}` → moduł `{module_name}`"
            if route_hint else
            f"Brak hint-a; pierwszy segment URL → moduł `{module_name}`"
        ),
    )

    doctor.set_analysis_context("url_target", {
        "url": args.url,
        "path": normalized_path,
        "module_name": module_name,
        "route_hint": route_hint,
    })

    structure_snapshot = doctor.collect_structure_snapshot(max_entries=120)
    if structure_snapshot:
        doctor.set_analysis_context("structure_snapshot", structure_snapshot)

    module_path_str = doctor.MODULE_PATH_MAP.get(module_name)
    if module_path_str:
        module_path = scan_root / module_path_str
        doctor.add_plan_step(
            name="module scope resolution",
            reason="Mapowanie modułu URL na ścieżkę w repozytorium.",
            command=f"# resolved module path: {module_path}",
            status="done" if module_path.exists() else "warning",
            details=None if module_path.exists() else "resolved path does not exist",
        )

        if not module_path.exists():
            from .doctor_models import Diagnosis, FileAction, ShellCommand
            doctor.diagnoses.append(Diagnosis(
                summary=f"Nie znaleziono modułu '{module_name}' dla URL {args.url}",
                problem_type="module_not_found",
                severity="medium",
                nlp_description=(
                    f"Ścieżka modułu '{module_name}' została rozwiązana z mapowania, ale katalog nie istnieje: {module_path}. "
                    "Sprawdź czy moduł istnieje w projekcie."
                ),
                file_actions=[FileAction(
                    path="doctor_orchestrator.py",
                    action="review",
                    reason=f"Ścieżka modułu '{module_name}' nie istnieje na dysku",
                )],
                shell_commands=[ShellCommand(
                    command=f"find {scan_root} -type d -name '{module_name}'",
                    description=f"Wyszukaj katalog modułu '{module_name}' w projekcie",
                )],
                confidence=0.9,
            ))
        else:
            # c2004-maskservice-patch-v2: page implementation analysis runs
            # even in --llm mode so URL-targeted stub/placeholder pages are
            # always reported as actionable diagnoses, not just hidden inside
            # an LLM narrative.
            page_token = doctor._extract_page_token(normalized_path, module_name)
            doctor.add_plan_step(
                name="page implementation analysis",
                reason="Wykrycie placeholder/stub plików strony pasujących do URL.",
                command=(
                    f"python -m regres.regres_cli doctor --scan-root {scan_root} "
                    f"--url {args.url}"
                ),
                status="done",
                inputs={
                    "module_path": str(module_path),
                    "page_token": page_token,
                    "history_window_days": doctor.HISTORY_DEFAULT_DAYS,
                    "history_max_iterations": doctor.HISTORY_DEFAULT_ITERATIONS,
                },
                decision=(
                    f"Z URL `{normalized_path}` wyciągnięto token strony `{page_token}`. "
                    f"Szukam plików `*{page_token}.page.ts` w `{module_path}` i sprawdzam "
                    "stub/placeholder oraz regresję względem historii git."
                ),
            )
            page_diagnoses = doctor.analyze_page_implementations(
                normalized_path, module_path, module_name,
            )
            doctor.update_last_plan_step(outputs={
                "diagnoses_found": len(page_diagnoses),
                "problem_types": [d.problem_type for d in page_diagnoses],
            })
            doctor.diagnoses.extend(page_diagnoses)
            doctor.set_analysis_context(
                "page_implementation_findings",
                [
                    {
                        "summary": d.summary,
                        "problem_type": d.problem_type,
                        "severity": d.severity,
                        "files": [a.path for a in d.file_actions],
                    }
                    for d in page_diagnoses
                ],
            )

            # c2004-maskservice-patch-v5: dependency chain analysis. We walk
            # imports of:
            #   (a) any file flagged by page diagnoses (modify action),
            #   (b) the URL-target page file itself even if no page diagnosis
            #       fired — to catch cases where the page looks fine content-
            #       wise but its imports are broken (Vite 500 at runtime).
            chain_targets: List[Path] = []
            for diag in page_diagnoses:
                for action in diag.file_actions:
                    if action.action != "modify":
                        continue
                    if (action.target or "").startswith("git:"):
                        continue
                    candidate = scan_root / action.path
                    if candidate.exists() and candidate not in chain_targets:
                        chain_targets.append(candidate)
            # Always include the resolved page files even when no diag fired.
            for page_file in doctor._find_page_files(module_path, page_token or ""):
                if page_file.exists() and page_file not in chain_targets:
                    chain_targets.append(page_file)

            if chain_targets:
                doctor.add_plan_step(
                    name="dependency chain analysis",
                    reason=(
                        "Po wykryciu placeholder/regresji prześledź relatywne importy "
                        "celu, aby znaleźć powiązane pliki wymagające naprawy."
                    ),
                    command=(
                        f"python -m regres.regres_cli doctor --scan-root {scan_root} "
                        f"--url {args.url} --all --git-history"
                    ),
                    status="done",
                    inputs={
                        "targets": [str(p.relative_to(scan_root)) for p in chain_targets],
                        "max_depth": 1,
                    },
                    decision=(
                        "Walk imports of każdego pliku celu (depth=1); zaznacz broken/stub. "
                        "Każdy broken link → następny krok regres na nim."
                    ),
                )
                chains_data: List[Dict[str, Any]] = []
                broken_total = 0
                stub_total = 0
                for tgt in chain_targets:
                    chain = doctor.analyze_dependency_chain(tgt, max_depth=1)
                    try:
                        target_rel = str(tgt.relative_to(scan_root)).replace("\\", "/")
                    except ValueError:
                        target_rel = str(tgt)
                    chains_data.append({"target": target_rel, "chain": chain})
                    broken_total += sum(1 for c in chain if not c.get("exists"))
                    stub_total += sum(1 for c in chain if c.get("is_page_stub"))
                doctor.set_analysis_context("dependency_chains", chains_data)
                doctor.update_last_plan_step(outputs={
                    "files_analyzed": len(chain_targets),
                    "broken_imports": broken_total,
                    "stub_imports": stub_total,
                })

                # c2004-maskservice-patch-v6: Vite runtime probe. Auto-derive
                # base URL from --url if --vite-base not explicit. The probe
                # gives us the AUTHORITATIVE answer about what's broken — much
                # better than filesystem-only checks because it accounts for
                # mounts, aliases, wrappers, etc.
                vite_base = getattr(args, "vite_base", None)
                if not vite_base and args.url:
                    try:
                        from urllib.parse import urlparse as _up
                        _parsed = _up(args.url)
                        if _parsed.scheme and _parsed.netloc:
                            vite_base = f"{_parsed.scheme}://{_parsed.netloc}"
                    except Exception:
                        vite_base = None

                if vite_base:
                    doctor.add_plan_step(
                        name="vite runtime probe",
                        reason=(
                            "Pobierz każdy plik celu z dev-servera Vite, aby uzyskać "
                            "autorytatywny status runtime (200 OK / 500 z 'Failed to "
                            "resolve import'). To wykrywa błędy w wrapperach i alias-ach, "
                            "których nie widzi sam test istnienia plików."
                        ),
                        command=f"# probing {len(chain_targets)} files via {vite_base}",
                        status="done",
                        inputs={
                            "vite_base": vite_base,
                            "files": [str(p.relative_to(scan_root)) for p in chain_targets],
                        },
                    )
                    vite_results: List[Dict[str, Any]] = []
                    visited_via_vite: set = set()
                    queue: List[Path] = list(chain_targets)
                    max_vite_probes = 20
                    while queue and len(vite_results) < max_vite_probes:
                        current = queue.pop(0)
                        try:
                            current_rel = str(current.relative_to(scan_root)).replace("\\", "/")
                        except ValueError:
                            current_rel = str(current)
                        if current_rel in visited_via_vite:
                            continue
                        visited_via_vite.add(current_rel)
                        result = doctor.probe_vite_runtime(vite_base, current_rel)
                        result["target"] = current_rel
                        vite_results.append(result)
                        # If broken, follow the failed import: try to resolve
                        # the missing_import_from path on disk and recurse on
                        # IT (since the failure originated from THAT file).
                        if not result["ok"] and result.get("missing_import_from"):
                            mfrom = result["missing_import_from"]
                            mfrom_path = scan_root / mfrom
                            if not mfrom_path.exists():
                                mfrom_path = scan_root / "frontend" / mfrom
                            if mfrom_path.exists() and mfrom_path not in queue:
                                queue.append(mfrom_path)
                    doctor.set_analysis_context("vite_runtime_results", vite_results)
                    broken_via_vite = sum(1 for r in vite_results if not r["ok"])
                    doctor.update_last_plan_step(outputs={
                        "probes": len(vite_results),
                        "broken_via_vite": broken_via_vite,
                    })

                    # Synthesize diagnoses for any Vite-broken file.
                    from .doctor_models import Diagnosis as _Diag2, FileAction as _FA2, ShellCommand as _SC2
                    for r in vite_results:
                        if r["ok"]:
                            continue
                        if r.get("transport_error"):
                            continue  # skip pure network errors
                        target_rel = r["target"]
                        nlp_lines = [
                            f"Vite zwrócił {r['status']} dla `{r['url']}`.",
                        ]
                        if r.get("error_message"):
                            nlp_lines.append(f"Wiadomość: {r['error_message']}")
                        if r.get("missing_import"):
                            nlp_lines.append(
                                f"Brakujący import: `{r['missing_import']}` z "
                                f"`{r.get('missing_import_from','?')}`"
                            )
                        sc2: List[_SC2] = [_SC2(
                            command=f"curl -s '{r['url']}' | head -40",
                            description="Podgląd surowej odpowiedzi Vite",
                        )]
                        if r.get("missing_import_from"):
                            url_hint = doctor._suggest_url_for_path(r["missing_import_from"])
                            if url_hint:
                                sc2.append(_SC2(
                                    command=(
                                        f".venv/bin/python -m regres.regres_cli doctor "
                                        f"--scan-root {scan_root} --url '{url_hint}' --all "
                                        f"--git-history --vite-base {vite_base}"
                                    ),
                                    description=(
                                        f"Naprawa łańcuchowa: regres na pliku, "
                                        f"który zgłosił błąd ({r['missing_import_from']})"
                                    ),
                                ))
                        doctor.diagnoses.append(_Diag2(
                            summary=(
                                f"Vite runtime: `{target_rel}` zwraca {r['status']}"
                                + (
                                    f" — brakujący import `{r['missing_import']}`"
                                    if r.get("missing_import") else ""
                                )
                            ),
                            problem_type="vite_runtime_failure",
                            severity="critical",
                            nlp_description="\n".join(nlp_lines),
                            file_actions=[_FA2(
                                path=r.get("missing_import_from") or target_rel,
                                action="modify",
                                reason=(
                                    f"Vite nie potrafił zresolwować importu "
                                    f"`{r.get('missing_import','?')}` z tego pliku."
                                ),
                            )],
                            shell_commands=sc2,
                            confidence=0.95,
                        ))

                # c2004-maskservice-patch-v5: surface broken imports as their
                # own diagnoses so they appear in the diagnosis list, get a
                # severity, and (where the import targets a `.page.ts` file)
                # become a pointer for the user to invoke regres recursively
                # on the chained file.
                from .doctor_models import Diagnosis as _Diag, FileAction as _FA, ShellCommand as _SC
                for entry in chains_data:
                    target_rel = entry["target"]
                    chain = entry["chain"] or []
                    broken = [c for c in chain if not c.get("exists")]
                    stubs = [c for c in chain if c.get("is_page_stub")]
                    if not broken and not stubs:
                        continue
                    nlp_lines = [
                        f"Plik `{target_rel}` zawiera relatywne importy, które nie są zresolwowane "
                        f"({len(broken)} broken, {len(stubs)} stub). Vite zwróci 500 przy próbie "
                        "załadowania strony, dopóki łańcuch nie zostanie naprawiony."
                    ]
                    fa: List[_FA] = [_FA(
                        path=target_rel,
                        action="modify",
                        reason="Imports require rewriting or chained restore.",
                    )]
                    # Pull git history candidates for the target file so the
                    # patch-script generator emits auto-rewrite patches per
                    # candidate (the same flow as page_content_regression).
                    target_path_obj = scan_root / target_rel
                    page_token_for_target = target_path_obj.stem.replace(".page", "")
                    try:
                        history_for_target = doctor._collect_page_history_candidates(
                            page_token_for_target, module_name or "", target_path_obj,
                        )
                    except Exception:
                        history_for_target = []
                    for hc in history_for_target[:8]:
                        fa.append(_FA(
                            path=target_rel,
                            action="modify",
                            target=f"git:{hc['hash']}:{hc['source_path']}",
                            reason=(
                                f"[{hc.get('date','?')}] {hc['hash']} • "
                                f"{hc.get('line_count','?')} linii • {hc['source_path']}"
                                + (f" • {hc['fingerprint']}" if hc.get("fingerprint") else "")
                            ),
                        ))
                    sc: List[_SC] = []
                    for c in broken[:6]:
                        nlp_lines.append(f"- BROKEN `{c['import']}` z `{c['from_file']}`")
                        sc.append(_SC(
                            command=f"# Tried: {', '.join(c.get('tried', [])[:3])}",
                            description=f"Import `{c['import']}` nie znaleziony",
                        ))
                        url_hint = doctor._suggest_url_for_path(c["import"])
                        if url_hint:
                            sc.append(_SC(
                                command=(
                                    f".venv/bin/python -m regres.regres_cli doctor "
                                    f"--scan-root {scan_root} --url '{url_hint}' --all "
                                    f"--git-history --out-md .regres/{Path(c['import']).stem}-doctor.md"
                                ),
                                description=f"Następny krok: regres na {url_hint}",
                            ))
                    for c in stubs[:6]:
                        resolved = c.get("resolved_path", "?")
                        nlp_lines.append(f"- STUB `{resolved}` ← `{c['import']}` (placeholder page)")
                        url_hint = doctor._suggest_url_for_path(resolved)
                        if url_hint:
                            sc.append(_SC(
                                command=(
                                    f".venv/bin/python -m regres.regres_cli doctor "
                                    f"--scan-root {scan_root} --url '{url_hint}' --all "
                                    f"--git-history --out-md .regres/{Path(resolved).stem}-doctor.md"
                                ),
                                description=f"Naprawa łańcuchowa: {url_hint}",
                            ))
                    doctor.diagnoses.append(_Diag(
                        summary=(
                            f"Łańcuch importów `{target_rel}` ma {len(broken)} "
                            "niezresolwowanych i " f"{len(stubs)} placeholder linków"
                        ),
                        problem_type="import_resolution_failure",
                        severity="high" if broken else "medium",
                        nlp_description="\n".join(nlp_lines),
                        file_actions=fa,
                        shell_commands=sc,
                        confidence=0.8,
                    ))

            if args.llm:
                doctor.add_plan_step(
                    name="llm report generation",
                    reason="Wygenerowanie raportu opisowego na podstawie kontekstu modułu.",
                    command=f"python -m regres.regres_cli doctor --scan-root {scan_root} --url {args.url} --llm",
                    status="done",
                )
                llm_report = doctor.generate_llm_diagnosis(args.url, module_path)
                if args.out_md:
                    out_md = Path(args.out_md)
                    out_md.write_text(llm_report, encoding="utf-8")
                    print(f"LLM diagnosis saved to {out_md}")
                else:
                    print(llm_report)
                # fall through so structured report (with page findings) is
                # still saved by _save_report() in JSON/MD form.

            else:
                doctor.add_plan_step(
                    name="targeted module analysis",
                    reason="Uruchomienie diagnostyki modułu wynikającego z URL.",
                    command=f"python -m regres.regres_cli doctor --scan-root {scan_root} --url {args.url}",
                    status="done",
                )
                diagnoses = doctor.analyze_from_url(args.url)
                doctor.diagnoses.extend(diagnoses)
    else:
        doctor.add_plan_step(
            name="module scope resolution",
            reason="Mapowanie modułu URL na ścieżkę w repozytorium.",
            command="# no module mapping found",
            status="warning",
            details="Moduł nie istnieje w strukturze projektu.",
        )
        from .doctor_models import Diagnosis, FileAction, ShellCommand
        doctor.diagnoses.append(Diagnosis(
            summary=f"Nie znaleziono modułu '{module_name}' dla URL {args.url}",
            problem_type="module_not_found",
            severity="medium",
            nlp_description=(
                f"Nie udało się rozwiązać ścieżki modułu '{module_name}' z URL {args.url}. "
                "Sprawdź czy moduł istnieje w projekcie lub czy mapowanie MODULE_PATH_MAP jest poprawne."
            ),
            file_actions=[FileAction(
                path="doctor_orchestrator.py",
                action="review",
                reason=f"Brak mapowania lub ścieżki dla modułu '{module_name}'",
            )],
            shell_commands=[ShellCommand(
                command=f"find {scan_root} -type d -name '{module_name}'",
                description=f"Wyszukaj katalog modułu '{module_name}' w projekcie",
            )],
            confidence=0.9,
        ))

    if args.apply:
        dry_run = not args.dry_run if args.dry_run else True
        fix_results = doctor.apply_fixes(doctor.diagnoses, dry_run=dry_run)
        print(f"Fixes applied: {len(fix_results['actions_performed'])} actions, {len(fix_results['errors'])} errors")
        if fix_results['errors']:
            print("Errors:")
            for err in fix_results['errors']:
                print(f"  - {err}")


def _handle_import_errors(args, doctor: DoctorOrchestrator, scan_root: Path, refresh_fn) -> None:
    """Handle import error analysis."""
    import_log = Path(args.import_log) if args.import_log else scan_root / ".regres" / "import-error-toon-report.raw.log"

    if args.all and not args.import_log:
        refresh_fn(scan_root, import_log)

    diagnoses = doctor.analyze_import_errors(import_log)
    doctor.diagnoses.extend(diagnoses)

    if args.git_history and args.all:
        for diag in diagnoses:
            if diag.problem_type == "import_error":
                for action in diag.file_actions:
                    if action.path:
                        git_diagnoses = doctor.analyze_git_history(action.path)
                        doctor.diagnoses.extend(git_diagnoses)


def _handle_defscan_refactor(args, doctor: DoctorOrchestrator) -> None:
    """Handle defscan and refactor analyses."""
    if args.defscan_report:
        diagnoses = doctor.analyze_duplicates(Path(args.defscan_report))
        doctor.diagnoses.extend(diagnoses)

    if args.defscan_scan:
        diagnoses = doctor.analyze_with_defscan(Path(args.defscan_scan))
        doctor.diagnoses.extend(diagnoses)

    if args.refactor_scan:
        diagnoses = doctor.analyze_with_refactor(Path(args.refactor_scan))
        doctor.diagnoses.extend(diagnoses)


def _handle_auto_decision_flow(args, doctor: DoctorOrchestrator, scan_root: Path, refresh_fn) -> None:
    """Run parameter-driven analysis sequence and record plan/context."""
    doctor.reset_analysis_plan()

    structure_snapshot = doctor.collect_structure_snapshot(max_entries=120)
    if structure_snapshot:
        doctor.set_analysis_context("structure_snapshot", structure_snapshot)

    # When --all is used, prioritize broad structural scans first.
    if args.all:
        doctor.add_plan_step(
            name="defscan pre-scan",
            reason="Wykrycie duplikatów i kandydatów do konsolidacji przed naprawą importów.",
            command=f"python -m regres.regres_cli defscan --path {scan_root} --json",
            status="done",
        )
        doctor.diagnoses.extend(doctor.analyze_with_defscan(scan_root))

        doctor.add_plan_step(
            name="refactor pre-scan",
            reason="Wykrycie wrapperów i potencjalnych problemów strukturalnych.",
            command=f"python -m regres.regres_cli refactor wrappers --path {scan_root}",
            status="done",
        )
        doctor.diagnoses.extend(doctor.analyze_with_refactor(scan_root))

    # Import analysis from provided or refreshed log.
    import_log = Path(args.import_log) if args.import_log else scan_root / ".regres" / "import-error-toon-report.raw.log"
    if args.all and not args.import_log:
        refreshed = refresh_fn(scan_root, import_log)
        doctor.add_plan_step(
            name="import log refresh",
            reason="Odświeżenie logu TS, aby uniknąć decyzji na nieaktualnych błędach.",
            command=f"python -m regres.regres_cli import-error-toon-report --frontend-cwd {scan_root / 'frontend'} --scan-root {scan_root}",
            status="done" if refreshed else "warning",
            details="refresh failed; fallback to existing log" if not refreshed else None,
        )

    if args.import_log or args.all:
        doctor.add_plan_step(
            name="import diagnostics",
            reason="Detekcja TS2307/TS2305 i przygotowanie akcji naprawczych.",
            command=f"python -m regres.regres_cli doctor --scan-root {scan_root} --import-log {import_log}",
            status="done",
        )
        import_diagnoses = doctor.analyze_import_errors(import_log)
        doctor.diagnoses.extend(import_diagnoses)

        # "regres" phase: history/context over files flagged by import diagnostics.
        affected_files = []
        for diag in import_diagnoses:
            for action in diag.file_actions:
                if action.path:
                    affected_files.append(action.path)
        affected_files = list(dict.fromkeys(affected_files))

        if affected_files:
            doctor.add_plan_step(
                name="regres history phase",
                reason="Analiza historii zmian dla plików z błędami importów.",
                command="git log --oneline --follow -- <affected-file>",
                status="done",
                details=f"files analyzed: {len(affected_files)}",
            )
            for p in affected_files:
                doctor.diagnoses.extend(doctor.analyze_git_history(p))

    # Additional explicit scans requested by parameters.
    if args.defscan_report:
        doctor.add_plan_step(
            name="defscan report merge",
            reason="Włączenie diagnoz z zewnętrznego raportu defscan.",
            command=f"python -m regres.regres_cli doctor --defscan-report {args.defscan_report}",
            status="done",
        )
        doctor.diagnoses.extend(doctor.analyze_duplicates(Path(args.defscan_report)))

    if args.defscan_scan:
        doctor.add_plan_step(
            name="defscan targeted scan",
            reason="Dodatkowe skanowanie wskazanego zakresu.",
            command=f"python -m regres.regres_cli defscan --path {args.defscan_scan} --json",
            status="done",
        )
        doctor.diagnoses.extend(doctor.analyze_with_defscan(Path(args.defscan_scan)))

    if args.refactor_scan:
        doctor.add_plan_step(
            name="refactor targeted scan",
            reason="Dodatkowa analiza wrapperów dla wskazanego zakresu.",
            command=f"python -m regres.regres_cli refactor wrappers --path {args.refactor_scan}",
            status="done",
        )
        doctor.diagnoses.extend(doctor.analyze_with_refactor(Path(args.refactor_scan)))

    doctor.set_analysis_context(
        "preliminary_refactor_proposals",
        doctor.collect_preliminary_refactor_proposals(),
    )


def _save_report(doctor: DoctorOrchestrator, args) -> None:
    """Save report to JSON/Markdown or print to stdout."""
    report = doctor.generate_report()

    # c2004-maskservice-patch-v4: derive a stable basename for companion
    # artifacts (.sh patches, index, future reports). Prefer --out-md, fall
    # back to --out-json, finally to a generic 'doctor'.
    basename = "doctor"
    out_dir: Optional[Path] = None
    if args.out_md:
        out_md_path = Path(args.out_md)
        basename = out_md_path.stem
        out_dir = out_md_path.parent
    elif args.out_json:
        out_json_path = Path(args.out_json)
        basename = out_json_path.stem
        out_dir = out_json_path.parent

    # Resolve patches output directory.
    patches_dir: Optional[Path] = None
    out_patches_dir_val = getattr(args, "out_patches_dir", None)
    if out_patches_dir_val and isinstance(out_patches_dir_val, (str, Path)):
        patches_dir = Path(out_patches_dir_val)
    elif out_dir is not None:
        patches_dir = out_dir

    generated_patches: List[Dict[str, str]] = []
    if patches_dir is not None and not getattr(args, "no_patches", False):
        generated_patches = doctor.generate_patch_scripts(patches_dir, basename)
        if generated_patches:
            report["generated_patches"] = generated_patches

    if args.out_json:
        out_json = Path(args.out_json)
        out_json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Report saved to {out_json}")

    if args.out_md:
        out_md = Path(args.out_md)
        md_text = doctor.render_markdown(report)
        # Append patches section so the markdown report points at the .sh files.
        if generated_patches:
            md_text = md_text.rstrip() + "\n\n" + _render_patches_section(generated_patches)
        out_md.write_text(md_text, encoding="utf-8")
        print(f"Markdown report saved to {out_md}")

    if generated_patches:
        non_index = [p for p in generated_patches if p["kind"] != "index"]
        print(f"Patch scripts generated: {len(non_index)} (in {patches_dir})")
        for p in generated_patches:
            kind_tag = "INDEX" if p["kind"] == "index" else p["candidate"]
            print(f"  [{kind_tag}] {p['path']}")

    if not args.out_json and not args.out_md:
        md_text = doctor.render_markdown(report)
        if generated_patches:
            md_text = md_text.rstrip() + "\n\n" + _render_patches_section(generated_patches)
        print(md_text)


def _render_patches_section(patches: List[Dict[str, str]]) -> str:
    """Render the 'Generated Patches' section appended to markdown reports."""
    lines = ["## Generated Patches", ""]
    non_index = [p for p in patches if p["kind"] != "index"]
    index_entry = next((p for p in patches if p["kind"] == "index"), None)
    if not non_index:
        lines.append("Brak wygenerowanych patchy (żadna diagnoza nie sugerowała modyfikacji).")
        lines.append("")
        return "\n".join(lines)

    lines.append(
        f"Wygenerowano {len(non_index)} patch-y `.sh`. Każdy jest niezależny — "
        "wykonuje backup (`<plik>.before-<timestamp>`), aplikuje zmianę i drukuje "
        "instrukcję revert. Jeśli pierwsza opcja okaże się błędna, uruchom kolejną."
    )
    lines.append("")
    if index_entry:
        lines.append(f"**Index:** `bash {index_entry['path']}` — wypisuje wszystkie dostępne patche.")
        lines.append("")
    lines.append("| # | Diagnoza | Kandydat | Plik patcha |")
    lines.append("|---|---|---|---|")
    for i, p in enumerate(non_index, 1):
        lines.append(
            f"| {i} | {p['diagnosis']} | `{p['candidate']}` | `{p['path']}` |"
        )
    lines.append("")
    lines.append("```bash")
    lines.append("# Aplikuj wybrany patch:")
    if non_index:
        lines.append(f"bash {non_index[0]['path']}")
    lines.append("# Jeśli treść jest błędna — przywróć backup i wybierz inny:")
    lines.append("# cp <target>.before-<timestamp> <target>")
    if len(non_index) > 1:
        lines.append(f"bash {non_index[1]['path']}")
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def _refresh_import_error_log(project_root: Path, log_path: Path) -> bool:
    """Odświeża log błędów importów TS przez import_error_toon_report."""
    frontend_cwd = project_root / "frontend"
    if not frontend_cwd.exists():
        return False

    regres_repo_root = Path(__file__).resolve().parents[1]

    out_md = project_root / ".regres" / "import-error-toon-report.md"
    cmd = [
        sys.executable,
        "-m",
        "regres.regres_cli",
        "import-error-toon-report",
        "--frontend-cwd",
        str(frontend_cwd),
        "--scan-root",
        str(project_root),
        "--out-md",
        str(out_md),
        "--out-raw-log",
        str(log_path),
    ]

    try:
        result = subprocess.run(
            cmd,
            cwd=str(regres_repo_root),
            capture_output=True,
            text=True,
            timeout=180,
        )
        if result.returncode != 0:
            if result.stderr:
                print(f"[doctor] warning: could not refresh import log: {result.stderr.strip()}")
            return False
        return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def _build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for doctor CLI."""
    parser = argparse.ArgumentParser(
        description="doctor — orchestrator analizy regresji i generator akcji naprawczych",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "UŻYCIE:\n"
            "  python doctor.py --scan-root .\n"
            "  python doctor.py --import-log .regres/import-error-toon-report.raw.log\n"
            "  python doctor.py --regres-report regres-report.json\n"
            "  python doctor.py --all --scan-root ."
        ),
    )
    parser.add_argument('--scan-root', default='.', help='Katalog główny projektu')
    parser.add_argument('--import-log', help='Ścieżka do logu błędów importów TS')
    parser.add_argument('--defscan-report', help='Ścieżka do raportu defscan (JSON)')
    parser.add_argument('--regres-report', help='Ścieżka do raportu regres (JSON)')
    parser.add_argument('--all', action='store_true', help='Uruchom wszystkie analizy')
    parser.add_argument('--url', help='Analizuj moduł na podstawie URL (np. http://localhost:8100/connect-scenario)')
    parser.add_argument('--apply', action='store_true', help='Wykonaj akcje naprawcze')
    parser.add_argument('--dry-run', action='store_true', help='Dry-run dla akcji naprawczych (domyślne)')
    parser.add_argument('--llm', action='store_true', help='Generuj szczegółowy raport LLM markdown z kontekstem')
    parser.add_argument('--git-history', action='store_true', help='Analizuj historię git plików z błędami')
    parser.add_argument('--defscan-scan', help='Uruchom defscan na konkretnym katalogu')
    parser.add_argument('--refactor-scan', help='Uruchom refactor wrappers na konkretnym katalogu')
    parser.add_argument('--out-md', help='Ścieżka do raportu Markdown')
    parser.add_argument('--out-json', help='Ścieżka do raportu JSON')
    parser.add_argument(
        '--out-patches-dir',
        help=(
            'Katalog, do którego zostaną zapisane skrypty `.sh` patchy (po jednym na każdą '
            'opcję restore-z-historii oraz na każdą diagnozę z file_actions=modify). '
            'Domyślnie używany jest katalog --out-md/--out-json.'
        ),
    )
    parser.add_argument(
        '--no-patches',
        action='store_true',
        help='Nie generuj skryptów `.sh` (tylko raport JSON/MD).',
    )
    parser.add_argument(
        '--vite-base',
        default=None,
        help=(
            'URL bazowy serwera Vite (np. http://localhost:8100). Gdy podany, '
            'regres dla każdego pliku celu pobiera odpowiadający /src/<...> URL '
            'i parsuje błąd 500 (Failed to resolve import) — to autorytatywny '
            'sygnał runtime, niezależny od testu istnienia plików na dysku.'
        ),
    )
    return parser


def main() -> None:
    """Main entry point for doctor CLI."""
    check_version(_get_version("regres"))
    parser = _build_parser()
    args = parser.parse_args()

    scan_root = Path(args.scan_root).resolve()
    doctor = DoctorOrchestrator(scan_root)

    if args.url:
        _handle_url_mode(args, doctor, scan_root)
        _save_report(doctor, args)
        return

    _handle_auto_decision_flow(args, doctor, scan_root, _refresh_import_error_log)
    _save_report(doctor, args)


if __name__ == '__main__':
    main()
