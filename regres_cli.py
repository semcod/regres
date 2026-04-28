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

from regres import regres
from regres import refactor
from regres import defscan
from regres import doctor
from regres.import_error_toon_report import main as import_error_toon_report_main


def main() -> int:
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
    doctor_parser.add_argument("--out-md", help="Ścieżka do raportu Markdown")
    doctor_parser.add_argument("--out-json", help="Ścieżka do raportu JSON")

    # import-error-toon-report subcommand
    ier_parser = subparsers.add_parser("import-error-toon-report", help="Raport błędów importów TS w formacie Toon")
    ier_parser.add_argument("--log-path", help="Ścieżka do logu kompilatora TS", default=".regres/import-error-toon-report.raw.log")
    ier_parser.add_argument("--report-path", help="Ścieżka do raportu", default=".regres/import-error-toon-report.md")

    args = parser.parse_args()

    if args.command == "regres":
        sys.argv = ["regres.py"]
        if args.path:
            sys.argv.append(args.path)
        if args.name:
            sys.argv.extend(["--name", args.name])
        if args.hash:
            sys.argv.extend(["--hash", args.hash])
        if args.history:
            sys.argv.append("--history")
        return regres.main()

    elif args.command == "refactor":
        sys.argv = ["refactor.py"]
        if args.mode:
            sys.argv.append(args.mode)
        sys.argv.extend(args.args)
        return refactor.main()

    elif args.command == "defscan":
        sys.argv = ["defscan.py"]
        if args.path:
            sys.argv.extend(["--path", args.path])
        if args.name:
            sys.argv.extend(["--name", args.name])
        if args.kind:
            sys.argv.extend(["--kind", args.kind])
        if args.min_count:
            sys.argv.extend(["--min-count", str(args.min_count)])
        if args.min_sim:
            sys.argv.extend(["--min-sim", str(args.min_sim)])
        if args.json:
            sys.argv.append("--json")
        if args.md:
            sys.argv.append("--md")
        if args.focus:
            sys.argv.extend(["--focus", args.focus])
        if args.scope:
            sys.argv.extend(["--scope", args.scope])
        if args.seed:
            sys.argv.extend(["--seed", args.seed])
        if args.similar_global:
            sys.argv.append("--similar-global")
        return defscan.main()

    elif args.command == "doctor":
        sys.argv = ["doctor.py"]
        if args.scan_root:
            sys.argv.extend(["--scan-root", args.scan_root])
        if args.import_log:
            sys.argv.extend(["--import-log", args.import_log])
        if args.defscan_report:
            sys.argv.extend(["--defscan-report", args.defscan_report])
        if args.regres_report:
            sys.argv.extend(["--regres-report", args.regres_report])
        if args.all:
            sys.argv.append("--all")
        if args.out_md:
            sys.argv.extend(["--out-md", args.out_md])
        if args.out_json:
            sys.argv.extend(["--out-json", args.out_json])
        return doctor.main()

    elif args.command == "import-error-toon-report":
        sys.argv = ["import-error-toon-report.py"]
        sys.argv.extend(["--log-path", args.log_path])
        sys.argv.extend(["--report-path", args.report_path])
        return import_error_toon_report_main()

    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
