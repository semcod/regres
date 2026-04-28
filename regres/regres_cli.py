#!/usr/bin/env python3
"""
regres — narzędzia do analizy regresji, refaktoryzacji i duplikatów kodu.

KOMENDY:
  regres          — analiza regresji plików (historia, zmiany)
  refactor        — analiza kodu przy refaktoryzacji (duplikaty, zależności, symbole)
  defscan         — skaner duplikatów definicji klas, funkcji i modeli
  doctor          — orchestrator analizy i generator akcji naprawczych
  import-error-toon-report — raport błędów importów TS w formacie Toon

PRZYKŁADY:
  regres regres.py
  regres find encoder
  regres duplicates
  regres symbols encoder
  regres defscan
  regres doctor --all
  regres import-error-toon-report
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import regres
from . import refactor
from . import defscan
from . import doctor
from .import_error_toon_report import main as import_error_toon_report_main
from .version_check import check_version
from importlib.metadata import version as _get_version


def main() -> int:
    check_version(_get_version("regres"))
    parser = argparse.ArgumentParser(
        prog="regres",
        description="Narzędzia do analizy regresji, refaktoryzacji i duplikatów kodu.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command", help="Komenda do uruchomienia")

    # regres subcommand
    regres_parser = subparsers.add_parser("regres", help="Analiza regresji plików")
    regres_parser.add_argument("path", nargs="?", help="Ścieżka do pliku lub katalogu")
    regres_parser.add_argument("--name", help="Filtruj po nazwie")
    regres_parser.add_argument("--hash", help="Filtruj po hashu")
    regres_parser.add_argument("--history", action="store_true", help="Pokaż historię zmian")

    # refactor subcommand
    refactor_parser = subparsers.add_parser("refactor", help="Analiza kodu przy refaktoryzacji")
    refactor_parser.add_argument("mode", nargs="?", help="Tryb: find, duplicates, similar, cluster, deps, symbols, wrappers, dead, diff, hotmap, report")
    refactor_parser.add_argument("args", nargs=argparse.REMAINDER, help="Argumenty dla trybu refactor")

    # defscan subcommand
    defscan_parser = subparsers.add_parser("defscan", help="Skaner duplikatów definicji")
    defscan_parser.add_argument("--path", help="Ścieżka do skanowania")
    defscan_parser.add_argument("--name", help="Filtruj po nazwie")
    defscan_parser.add_argument("--kind", help="Rodzaj definicji")
    defscan_parser.add_argument("--min-count", type=int, help="Min. liczba duplikatów")
    defscan_parser.add_argument("--min-sim", type=int, help="Min. podobieństwo")
    defscan_parser.add_argument("--json", action="store_true", help="Eksport JSON")
    defscan_parser.add_argument("--md", action="store_true", help="Eksport Markdown")
    defscan_parser.add_argument("--focus", help="Tryb focus: folder vs reszta projektu")
    defscan_parser.add_argument("--scope", help="Scope dla trybu focus")
    defscan_parser.add_argument("--seed", help="Tryb seed: similarity globalna")
    defscan_parser.add_argument("--similar-global", action="store_true", help="Szukaj podobnych ciał niezależnie od nazwy")

    # doctor subcommand
    doctor_parser = subparsers.add_parser("doctor", help="Orchestrator analizy i generator akcji naprawczych")
    doctor_parser.add_argument("--scan-root", default=".", help="Katalog główny projektu")
    doctor_parser.add_argument("--import-log", help="Ścieżka do logu błędów importów TS")
    doctor_parser.add_argument("--defscan-report", help="Ścieżka do raportu defscan (JSON)")
    doctor_parser.add_argument("--regres-report", help="Ścieżka do raportu regres (JSON)")
    doctor_parser.add_argument("--all", action="store_true", help="Uruchom wszystkie analizy")
    doctor_parser.add_argument("--url", help="Analizuj moduł na podstawie URL (np. http://localhost:8100/connect-scenario)")
    doctor_parser.add_argument("--apply", action="store_true", help="Wykonaj akcje naprawcze")
    doctor_parser.add_argument("--dry-run", action="store_true", help="Dry-run dla akcji naprawczych (domyślne)")
    doctor_parser.add_argument("--llm", action="store_true", help="Generuj szczegółowy raport LLM markdown z kontekstem")
    doctor_parser.add_argument("--git-history", action="store_true", help="Analizuj historię git plików z błędami")
    doctor_parser.add_argument("--defscan-scan", help="Uruchom defscan na konkretnym katalogu")
    doctor_parser.add_argument("--refactor-scan", help="Uruchom refactor wrappers na konkretnym katalogu")
    doctor_parser.add_argument("--vite-base", dest="vite_base", help="Vite dev-server base URL (np. http://localhost:8100). Auto-derywowane z --url jeśli nie podane.")
    doctor_parser.add_argument("--out-md", help="Ścieżka do raportu Markdown")
    doctor_parser.add_argument("--out-json", help="Ścieżka do raportu JSON")

    # import-error-toon-report subcommand
    ier_parser = subparsers.add_parser("import-error-toon-report", help="Raport błędów importów TS w formacie Toon")
    ier_parser.add_argument("--input-log", help="Użyj istniejącego logu zamiast uruchamiania type-check")
    ier_parser.add_argument("--frontend-cwd", help="Katalog frontend (dla type-check)")
    ier_parser.add_argument("--typecheck-cmd", help="Komenda type-check (np. npm run -s type-check)")
    ier_parser.add_argument("--out-md", help="Ścieżka do raportu markdown", default=".regres/import-error-toon-report.md")
    ier_parser.add_argument("--out-raw-log", help="Ścieżka do surowego logu", default=".regres/import-error-toon-report.raw.log")
    ier_parser.add_argument("--scan-root", help="Wartość scan_root do raportu")

    args = parser.parse_args()
    return _dispatch_command(args, parser)


def _build_regres_argv(args) -> list[str]:
    argv = ["regres.py"]
    if args.path:
        argv.append(args.path)
    if args.name:
        argv.extend(["--name", args.name])
    if args.hash:
        argv.extend(["--hash", args.hash])
    if args.history:
        argv.append("--history")
    return argv


def _build_refactor_argv(args) -> list[str]:
    argv = ["refactor.py"]
    if args.mode:
        argv.append(args.mode)
    argv.extend(args.args)
    return argv


def _build_defscan_argv(args) -> list[str]:
    argv = ["defscan.py"]
    _extend_if_set(argv, "--path", args.path)
    _extend_if_set(argv, "--name", args.name)
    _extend_if_set(argv, "--kind", args.kind)
    _extend_if_set(argv, "--min-count", args.min_count, str)
    _extend_if_set(argv, "--min-sim", args.min_sim, str)
    _append_if_true(argv, "--json", args.json)
    _append_if_true(argv, "--md", args.md)
    _extend_if_set(argv, "--focus", args.focus)
    _extend_if_set(argv, "--scope", args.scope)
    _extend_if_set(argv, "--seed", args.seed)
    _append_if_true(argv, "--similar-global", args.similar_global)
    return argv


def _build_doctor_argv(args) -> list[str]:
    argv = ["doctor.py"]
    _extend_if_set(argv, "--scan-root", args.scan_root)
    _extend_if_set(argv, "--import-log", args.import_log)
    _extend_if_set(argv, "--defscan-report", args.defscan_report)
    _extend_if_set(argv, "--regres-report", args.regres_report)
    _append_if_true(argv, "--all", args.all)
    _extend_if_set(argv, "--url", args.url)
    _append_if_true(argv, "--apply", args.apply)
    _append_if_true(argv, "--dry-run", args.dry_run)
    _append_if_true(argv, "--llm", args.llm)
    _append_if_true(argv, "--git-history", args.git_history)
    _extend_if_set(argv, "--defscan-scan", args.defscan_scan)
    _extend_if_set(argv, "--refactor-scan", args.refactor_scan)
    _extend_if_set(argv, "--out-md", args.out_md)
    _extend_if_set(argv, "--out-json", args.out_json)
    return argv


def _build_ier_argv(args) -> list[str]:
    argv = ["import-error-toon-report.py"]
    _extend_if_set(argv, "--input-log", args.input_log)
    _extend_if_set(argv, "--frontend-cwd", args.frontend_cwd)
    _extend_if_set(argv, "--typecheck-cmd", args.typecheck_cmd)
    _extend_if_set(argv, "--out-md", args.out_md)
    _extend_if_set(argv, "--out-raw-log", args.out_raw_log)
    _extend_if_set(argv, "--scan-root", args.scan_root)
    return argv


def _extend_if_set(argv: list[str], flag: str, value, transform=None) -> None:
    if value:
        argv.extend([flag, transform(value) if transform else value])


def _append_if_true(argv: list[str], flag: str, value) -> None:
    if value:
        argv.append(flag)


def _dispatch_command(args, parser) -> int:
    dispatch_map = {
        "regres": (lambda a: setattr(sys, "argv", _build_regres_argv(a)) or regres.main(),),
        "refactor": (lambda a: setattr(sys, "argv", _build_refactor_argv(a)) or refactor.main(),),
        "defscan": (lambda a: setattr(sys, "argv", _build_defscan_argv(a)) or defscan.main(),),
        "doctor": (lambda a: setattr(sys, "argv", _build_doctor_argv(a)) or doctor.main(),),
        "import-error-toon-report": (lambda a: setattr(sys, "argv", _build_ier_argv(a)) or import_error_toon_report_main(),),
    }
    if args.command in dispatch_map:
        return dispatch_map[args.command][0](args)
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
