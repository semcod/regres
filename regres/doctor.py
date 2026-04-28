#!/usr/bin/env python3
"""
doctor.py — orchestrator analizy regresji i generator akcji naprawczych.

Analizuje wyniki z regres, refactor, defscan i import-error-toon-report,
a następnie generuje:
- NLP opis problemu i rozwiązania
- Polecenia shell do wykonania
- Listę plików do przeniesienia/zmodyfikowania

UŻYCIE:
  python doctor.py --scan-root .
  python doctor.py --import-log .regres/import-error-toon-report.raw.log
  python doctor.py --regres-report regres-report.json
  python doctor.py --all --scan-root .
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class FileAction:
    """Akcja na pliku."""
    path: str
    action: str  # move, copy, delete, modify, create
    target: Optional[str] = None  # ścieżka docelowa dla move/copy
    reason: str = ""  # dlaczego ta akcja jest potrzebna


@dataclass
class ShellCommand:
    """Polecenie shell do wykonania."""
    command: str
    description: str
    cwd: Optional[str] = None


@dataclass
class Diagnosis:
    """Diagnoza problemu i plan naprawy."""
    summary: str
    problem_type: str  # import_error, duplicate, regression, etc.
    severity: str  # low, medium, high, critical
    nlp_description: str
    file_actions: List[FileAction] = field(default_factory=list)
    shell_commands: List[ShellCommand] = field(default_factory=list)
    confidence: float = 0.0


class DoctorOrchestrator:
    """Orchestrator analizy i generator akcji."""

    def __init__(self, scan_root: Path):
        self.scan_root = scan_root.resolve()
        self.diagnoses: List[Diagnosis] = []

    def analyze_import_errors(self, log_path: Path) -> List[Diagnosis]:
        """Analizuje błędy importów z logu TS."""
        if not log_path.exists():
            return []

        diagnoses = []
        errors_by_file = self._parse_ts_errors(log_path)

        for file_path, errors in errors_by_file.items():
            # Analiza wzorców błędów
            missing_modules = self._extract_missing_modules(errors)

            if missing_modules:
                diag = self._diagnose_import_issue(file_path, missing_modules)
                diagnoses.append(diag)

        return diagnoses

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
                    if "TS2307" in line:
                        errors_by_file.setdefault(current_file, []).append(line)
                    elif "TS2305" in line:
                        errors_by_file.setdefault(current_file, []).append(line)

        return errors_by_file

    def _extract_missing_modules(self, errors: List[str]) -> List[str]:
        """Wyciąga brakujące moduły z błędów."""
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

        # Analiza ścieżek modułów
        for module in missing_modules:
            if module.startswith("@c2004/"):
                # Brakujący alias w monorepo
                alias = module.replace("@c2004/", "")
                actions.append(FileAction(
                    path=file_path,
                    action="modify",
                    reason=f"Zmień import {module} na poprawną ścieżkę"
                ))
                commands.append(ShellCommand(
                    command=f"# Przejrzyj {file_path} i popraw import {module}",
                    description=f"Manualna korekta importu {module}"
                ))

            elif module.startswith("./") or module.startswith("../"):
                # Relatywna ścieżka - może być problem z głębokością
                actions.append(FileAction(
                    path=file_path,
                    action="modify",
                    reason=f"Sprawdź czy ścieżka {module} jest poprawna"
                ))

        nlp_desc = (
            f"W pliku {file_path} wykryto błędy importów dla modułów: {', '.join(missing_modules)}. "
            "Należy sprawdzić konfigurację ścieżek w tsconfig.json oraz upewnić się, "
            "że wszystkie wymagane moduły są dostępne w monorepo."
        )

        return Diagnosis(
            summary=f"Błędy importów w {file_path}",
            problem_type="import_error",
            severity="high" if len(missing_modules) > 3 else "medium",
            nlp_description=nlp_desc,
            file_actions=actions,
            shell_commands=commands,
            confidence=0.8
        )

    def analyze_duplicates(self, report_path: Path) -> List[Diagnosis]:
        """Analizuje duplikaty z raportu defscan."""
        if not report_path.exists():
            return []

        diagnoses = []

        try:
            with open(report_path, encoding="utf-8") as f:
                data = json.load(f)

            # Analiza duplikatów
            for item in data.get("duplicates", []):
                if item.get("count", 0) > 1:
                    diag = self._diagnose_duplicate(item)
                    diagnoses.append(diag)

        except (json.JSONDecodeError, KeyError):
            pass

        return diagnoses

    def _diagnose_duplicate(self, duplicate_data: Dict[str, Any]) -> Diagnosis:
        """Diagnozuje problem z duplikatami."""
        name = duplicate_data.get("name", "unknown")
        count = duplicate_data.get("count", 0)
        locations = duplicate_data.get("locations", [])

        actions = []
        commands = []

        # Sugerowanie konsolidacji
        if count > 2:
            # Znajdź główną lokalizację (np. w shared package)
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
        """Znajduje główną lokalizację dla konsolidacji."""
        # Preferuj lokalizacje w shared packages
        for loc in locations:
            if "shared" in loc.lower():
                return loc

        # Zwróć pierwszą lokalizację
        return locations[0] if locations else ""

    def generate_report(self) -> Dict[str, Any]:
        """Generuje kompletny raport diagnoz."""
        return {
            "scan_root": str(self.scan_root),
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
        lines = []
        lines.append("# Doctor Report\n")
        lines.append(f"**Scan Root:** `{report['scan_root']}`\n")
        lines.append(f"**Diagnoses:** {len(report['diagnoses'])}\n")

        for i, diag in enumerate(report['diagnoses'], 1):
            severity_emoji = {
                "low": "🟢",
                "medium": "🟡",
                "high": "🟠",
                "critical": "🔴"
            }.get(diag['severity'], "⚪")

            lines.append(f"## {severity_emoji} {i}. {diag['summary']}")
            lines.append(f"**Type:** {diag['problem_type']} | **Severity:** {diag['severity']} | **Confidence:** {diag['confidence']:.0%}\n")
            lines.append(f"**Description:** {diag['nlp_description']}\n")

            if diag['file_actions']:
                lines.append("### File Actions")
                lines.append("```")
                for action in diag['file_actions']:
                    lines.append(f"{action.action}: {action.path}")
                    if action.target:
                        lines.append(f"  -> {action.target}")
                    if action.reason:
                        lines.append(f"  ({action.reason})")
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
                lines.append("```\n")

        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="doctor — orchestrator analizy regresji i generator akcji naprawczych",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument('--scan-root', default='.', help='Katalog główny projektu')
    parser.add_argument('--import-log', help='Ścieżka do logu błędów importów TS')
    parser.add_argument('--defscan-report', help='Ścieżka do raportu defscan (JSON)')
    parser.add_argument('--regres-report', help='Ścieżka do raportu regres (JSON)')
    parser.add_argument('--all', action='store_true', help='Uruchom wszystkie analizy')
    parser.add_argument('--out-md', help='Ścieżka do raportu Markdown')
    parser.add_argument('--out-json', help='Ścieżka do raportu JSON')
    args = parser.parse_args()

    scan_root = Path(args.scan_root).resolve()
    doctor = DoctorOrchestrator(scan_root)

    # Analiza błędów importów
    if args.import_log or args.all:
        import_log = Path(args.import_log) if args.import_log else scan_root / ".regres" / "import-error-toon-report.raw.log"
        diagnoses = doctor.analyze_import_errors(import_log)
        doctor.diagnoses.extend(diagnoses)

    # Analiza duplikatów
    if args.defscan_report:
        diagnoses = doctor.analyze_duplicates(Path(args.defscan_report))
        doctor.diagnoses.extend(diagnoses)

    # Generowanie raportu
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

    # Domyślnie wyświetl Markdown na stdout
    if not args.out_json and not args.out_md:
        print(doctor.render_markdown(report))


if __name__ == '__main__':
    main()
