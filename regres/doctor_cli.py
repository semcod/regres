#!/usr/bin/env python3
"""
doctor_cli.py — CLI entry point and helpers for doctor module.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

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
                return

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

    if args.out_json:
        out_json = Path(args.out_json)
        out_json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Report saved to {out_json}")

    if args.out_md:
        out_md = Path(args.out_md)
        md_text = doctor.render_markdown(report)
        out_md.write_text(md_text, encoding="utf-8")
        print(f"Markdown report saved to {out_md}")

    if not args.out_json and not args.out_md:
        print(doctor.render_markdown(report))


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
