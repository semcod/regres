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
import subprocess
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
        "connect-id": "connect-id/frontend/src/modules/connect-id",
        "connect-template": "connect-template/frontend/src/modules/connect-template",
        "connect-workshop": "connect-workshop/frontend/src/modules/connect-workshop",
    }

    def analyze_from_url(self, url: str) -> List[Diagnosis]:
        """Analizuje moduł na podstawie URL."""
        # Parsuj URL aby wyodrębnić ścieżkę
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            path = parsed.path.strip('/')
        except:
            path = url.strip('/')

        # Wyodrębnij nazwę modułu z ścieżki
        module_name = None
        for possible_module in self.MODULE_PATH_MAP.keys():
            if path.startswith(possible_module):
                module_name = possible_module
                break

        if not module_name:
            # Spróbuj dopasować pierwszą część ścieżki
            parts = path.split('/')
            if parts:
                module_name = parts[0]

        if not module_name:
            return []

        # Znajdź katalog modułu
        module_path = self.MODULE_PATH_MAP.get(module_name)
        if not module_path:
            # Spróbuj znaleźć katalog automatycznie
            for possible_path in [
                f"{module_name}/frontend/src/modules/{module_name}",
                f"{module_name}/frontend/src",
                f"{module_name}/backend",
                f"frontend/src/modules/{module_name}",
            ]:
                full_path = self.scan_root / possible_path
                if full_path.exists():
                    module_path = possible_path
                    break

        if not module_path:
            return []

        full_module_path = self.scan_root / module_path
        if not full_module_path.exists():
            return []

        # Uruchom wszystkie analizy na tym module
        diagnoses = []

        # Defscan
        defscan_diags = self.analyze_with_defscan(full_module_path)
        diagnoses.extend(defscan_diags)

        # Refactor
        refactor_diags = self.analyze_with_refactor(full_module_path)
        diagnoses.extend(refactor_diags)

        # Git history dla plików w module
        for file_path in full_module_path.rglob("*.ts"):
            relative_path = str(file_path.relative_to(self.scan_root))
            git_diags = self.analyze_git_history(relative_path)
            diagnoses.extend(git_diags)

        return diagnoses

    def analyze_import_errors(self, log_path: Path) -> List[Diagnosis]:
        """Analizuje błędy importów z logu TS."""
        if not log_path.exists():
            return []

        diagnoses = []
        errors_by_file = self._parse_ts_errors(log_path)

        for file_path, errors in errors_by_file.items():
            # Filtrowanie: sprawdź czy import nadal istnieje w pliku źródłowym
            # (wyklucza błędy ze starego cache tsc)
            validated_errors = []
            for err_line in errors:
                mod_match = re.search(r"Cannot find module '([^']+)'", err_line)
                if mod_match:
                    module_name = mod_match.group(1)
                    if self._import_exists_in_source(file_path, module_name):
                        validated_errors.append(err_line)
                else:
                    validated_errors.append(err_line)

            if not validated_errors:
                continue

            missing_modules = self._extract_missing_modules(validated_errors)
            if missing_modules:
                diag = self._diagnose_import_issue(file_path, missing_modules)
                diagnoses.append(diag)

        return diagnoses

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
        # Mapowanie aliasów na katalogi (heurystyka bazująca na c2004)
        suffix = alias_path.replace("@c2004/", "")
        candidates = [
            self.scan_root / "frontend" / "src" / suffix,
            self.scan_root / "frontend" / "src" / "modules" / suffix,
            self.scan_root / "frontend" / "src" / "components" / suffix,
            self.scan_root / suffix,
        ]
        # Dodaj rozszerzenia TS jeśli brak
        for cand in candidates:
            if cand.exists():
                return str(cand.relative_to(self.scan_root)).replace("\\", "/")
            for ext in (".ts", ".tsx", ".js", ".json"):
                if cand.with_suffix(ext).exists():
                    return str(cand.with_suffix(ext).relative_to(self.scan_root)).replace("\\", "/")
            # Sprawdź index
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
        concrete_fixes: list[str] = []

        # Analiza ścieżek modułów
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
                # Sprawdź czy plik istnieje
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
                    # Plik istnieje, może brak eksportu – niższy priorytet
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
        # Obniż priorytet jeśli nie znaleziono żadnych konkretnych ścieżek
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

    def analyze_git_history(self, file_path: str) -> List[Diagnosis]:
        """Analizuje historię git pliku aby wykryć wzorce scope."""
        if not (self.scan_root / ".git").exists():
            return []

        diagnoses = []
        try:
            # Pobierz historię pliku
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
                    # Analiza wzorców w historii
                    diag = self._analyze_history_patterns(file_path, lines)
                    if diag:
                        diagnoses.append(diag)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return diagnoses

    def _analyze_history_patterns(self, file_path: str, history_lines: List[str]) -> Optional[Diagnosis]:
        """Analizuje wzorce w historii git."""
        # Sprawdź czy plik był często przenoszony
        move_keywords = ['move', 'rename', 'refactor', 'extract', 'migrate']
        move_count = sum(1 for line in history_lines if any(kw in line.lower() for kw in move_keywords))

        if move_count >= 2:
            actions = []
            commands = []

            # Sugeruj sprawdzenie czy plik jest w odpowiednim module
            if 'connect-test' in file_path and 'connect-protocol' in str(history_lines):
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
                for item in data.get("duplicates", []):
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
            # Sprawdź wrappery
            cmd = [sys.executable, "-m", "regres.refactor", "wrappers", "--path", str(path)]
            result = subprocess.run(
                cmd,
                cwd=str(self.scan_root),
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0 and result.stdout.strip():
                # Parsuj wynik refactor wrappers
                lines = result.stdout.strip().split('\n')
                wrapper_count = len([l for l in lines if 'wrapper' in l.lower()])

                if wrapper_count > 0:
                    actions = []
                    commands = []

                    actions.append(FileAction(
                        path=str(path),
                        action="review",
                        reason=f"Wykryto {wrapper_count} wrapperów - sprawdź czy są potrzebne"
                    ))
                    commands.append(ShellCommand(
                        command=f"regres refactor wrappers --path {path}",
                        description="Przejrzyj wrappery w katalogu"
                    ))

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
            # Wykonaj FileActions
            for action in diag.file_actions:
                try:
                    if action.action == "modify":
                        if not dry_run:
                            # Modyfikacja pliku - placeholder dla implementacji
                            results["actions_performed"].append({
                                "action": action.action,
                                "path": action.path,
                                "reason": action.reason
                            })
                        else:
                            results["actions_performed"].append({
                                "action": action.action,
                                "path": action.path,
                                "reason": action.reason,
                                "dry_run": True
                            })
                    elif action.action == "delete":
                        if not dry_run:
                            file_path = self.scan_root / action.path
                            if file_path.exists():
                                file_path.unlink()
                                results["actions_performed"].append({
                                    "action": action.action,
                                    "path": action.path,
                                    "reason": action.reason
                                })
                        else:
                            results["actions_performed"].append({
                                "action": action.action,
                                "path": action.path,
                                "reason": action.reason,
                                "dry_run": True
                            })
                    elif action.action == "move":
                        if not dry_run:
                            src = self.scan_root / action.path
                            dst = self.scan_root / action.target if action.target else None
                            if src.exists() and dst:
                                dst.parent.mkdir(parents=True, exist_ok=True)
                                src.rename(dst)
                                results["actions_performed"].append({
                                    "action": action.action,
                                    "path": action.path,
                                    "target": action.target,
                                    "reason": action.reason
                                })
                        else:
                            results["actions_performed"].append({
                                "action": action.action,
                                "path": action.path,
                                "target": action.target,
                                "reason": action.reason,
                                "dry_run": True
                            })
                except Exception as e:
                    results["errors"].append({
                        "action": action.action,
                        "path": action.path,
                        "error": str(e)
                    })

            # Wykonaj ShellCommands
            for cmd in diag.shell_commands:
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
                    results["errors"].append({
                        "command": cmd.command,
                        "error": str(e)
                    })

        return results

    def generate_llm_diagnosis(self, url: str, module_path: Path) -> str:
        """Generuje szczegółowy raport markdown z kontekstem historycznym i strukturalnym."""
        lines = []
        
        # Header
        lines.append("# LLM-Based Diagnosis Report")
        lines.append(f"**URL:** {url}")
        lines.append(f"**Module Path:** {module_path}")
        lines.append(f"**Scan Root:** {self.scan_root}")
        lines.append("")
        
        # Kontekst historii git
        lines.append("## Git History Context")
        lines.append("")
        git_context = self._collect_git_context(module_path)
        lines.append(git_context)
        lines.append("")
        
        # Analiza struktury kodu
        lines.append("## Code Structure Analysis")
        lines.append("")
        structure_context = self._collect_structure_context(module_path)
        lines.append(structure_context)
        lines.append("")
        
        # Duplikaty (defscan)
        lines.append("## Duplicate Analysis (defscan)")
        lines.append("")
        defscan_context = self._collect_defscan_context(module_path)
        lines.append(defscan_context)
        lines.append("")
        
        # Wrapper analysis (refactor)
        lines.append("## Wrapper Analysis (refactor)")
        lines.append("")
        refactor_context = self._collect_refactor_context(module_path)
        lines.append(refactor_context)
        lines.append("")
        
        # NLP Diagnosis
        lines.append("## NLP Diagnosis & Recommendations")
        lines.append("")
        lines.append("### Problem Summary")
        lines.append("Based on the analysis above, the following issues were detected:")
        lines.append("")
        
        # Zbierz wszystkie diagnozy
        all_diagnoses = []
        all_diagnoses.extend(self.analyze_with_defscan(module_path))
        all_diagnoses.extend(self.analyze_with_refactor(module_path))
        for file_path in module_path.rglob("*.ts"):
            relative_path = str(file_path.relative_to(self.scan_root))
            all_diagnoses.extend(self.analyze_git_history(relative_path))
        
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
        
        # Codeblocks z propozycjami napraw
        lines.append("## Proposed Fixes")
        lines.append("")
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
        
        # Shell commands
        lines.append("## Shell Commands to Execute")
        lines.append("")
        lines.append("```bash")
        for diag in all_diagnoses:
            for cmd in diag.shell_commands:
                lines.append(f"# {cmd.description}")
                lines.append(cmd.command)
                if cmd.cwd:
                    lines.append(f"# cwd: {cmd.cwd}")
                lines.append("")
        lines.append("```")
        lines.append("")

        # Step-by-step playbook (LLM + manual)
        normalized_diags = [
            {
                "summary": d.summary,
                "nlp_description": d.nlp_description,
                "file_actions": [
                    {
                        "path": a.path,
                        "action": a.action,
                        "target": a.target,
                        "reason": a.reason,
                    }
                    for a in d.file_actions
                ],
                "shell_commands": [
                    {
                        "command": c.command,
                        "description": c.description,
                        "cwd": c.cwd,
                    }
                    for c in d.shell_commands
                ],
            }
            for d in all_diagnoses
        ]
        lines.extend(self._render_step_by_step_playbook(normalized_diags, llm_mode=True))
        lines.append("")
        
        # Summary
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- Total issues detected: {len(all_diagnoses)}")
        lines.append(f"- Files analyzed: {len(list(module_path.rglob('*.ts')))}")
        lines.append(f"- Confidence score: {(sum(d.confidence for d in all_diagnoses) / len(all_diagnoses) if all_diagnoses else 0):.0%}")
        lines.append("")
        
        return "\n".join(lines)

    def _render_step_by_step_playbook(self, diagnoses: List[Dict[str, Any]], llm_mode: bool = False) -> List[str]:
        """Renderuje playbook krok po kroku z codeblockami do ręcznego lub LLM-driven wykonania."""
        lines: List[str] = []
        lines.append("## Step-by-Step Repair Playbook")
        lines.append("")

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

            lines.append("**1) Analyze**")
            lines.append("```bash")
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
                    lines.append(f"grep -n \"import\" {p}")
            else:
                lines.append("# Brak shell commands dla tej diagnozy")
            lines.append("```")
            lines.append("")

            lines.append("**2) Apply changes**")
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

            lines.append("**3) Validate**")
            lines.append("```bash")
            lines.append("python -m regres.regres_cli doctor --scan-root . --all --out-md .regres/doctor-after-step.md")
            if paths:
                for p in paths[:3]:
                    lines.append(f"grep -n \"Cannot find module\" .regres/import-error-toon-report.raw.log | grep \"{p}\" || true")
            lines.append("```")
            lines.append("")

        return lines
    
    def _collect_git_context(self, module_path: Path) -> str:
        """Zbiera kontekst historii git dla modułu."""
        lines = []
        lines.append("```bash")
        lines.append("# Recent commits affecting this module")
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
        except:
            lines.append("# Git history not available")
        lines.append("```")
        return "\n".join(lines)
    
    def _collect_structure_context(self, module_path: Path) -> str:
        """Zbiera kontekst struktury kodu."""
        lines = []
        lines.append("```")
        lines.append("# Directory structure")
        for item in sorted(module_path.rglob("*")):
            if item.is_file() and item.suffix == ".ts":
                rel = item.relative_to(module_path)
                lines.append(f"  {rel}")
        lines.append("```")
        return "\n".join(lines)
    
    def _collect_defscan_context(self, module_path: Path) -> str:
        """Zbiera kontekst duplikatów z defscan."""
        lines = []
        try:
            from regres import defscan
            import io
            import sys
            
            # Przechwyć stdout
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            try:
                # Wywołaj defscan bezpośrednio
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
                    for dup in duplicates[:5]:  # Limit to 5
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
        """Zbiera kontekst wrapperów z refactor."""
        lines = []
        try:
            from regres import refactor
            import io
            import sys
            
            # Przechwyć stdout
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            try:
                # Wywołaj refactor bezpośrednio --path jest globalnym argumentem
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
                    lines.append("```")
                lines.append("")

        lines.extend(self._render_step_by_step_playbook(report.get('diagnoses', []), llm_mode=False))

        return "\n".join(lines)


def _handle_url_mode(args, doctor, scan_root):
    """Handle URL-based discovery and analysis mode."""
    from urllib.parse import urlparse
    
    parsed = urlparse(args.url)
    path = parsed.path.strip('/')
    module_name = None
    for possible_module in doctor.MODULE_PATH_MAP.keys():
        if path.startswith(possible_module):
            module_name = possible_module
            break
    if not module_name:
        parts = path.split('/')
        if parts:
            module_name = parts[0]
    
    module_path_str = doctor.MODULE_PATH_MAP.get(module_name)
    if module_path_str:
        module_path = scan_root / module_path_str
        
        if args.llm:
            llm_report = doctor.generate_llm_diagnosis(args.url, module_path)
            if args.out_md:
                out_md = Path(args.out_md)
                out_md.write_text(llm_report, encoding="utf-8")
                print(f"LLM diagnosis saved to {out_md}")
            else:
                print(llm_report)
            return
    
    diagnoses = doctor.analyze_from_url(args.url)
    doctor.diagnoses.extend(diagnoses)
    
    if args.apply:
        dry_run = not args.dry_run if args.dry_run else True
        fix_results = doctor.apply_fixes(diagnoses, dry_run=dry_run)
        print(f"Fixes applied: {len(fix_results['actions_performed'])} actions, {len(fix_results['errors'])} errors")
        if fix_results['errors']:
            print("Errors:")
            for err in fix_results['errors']:
                print(f"  - {err}")


def _handle_import_errors(args, doctor, scan_root, refresh_fn):
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


def _handle_defscan_refactor(args, doctor):
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


def _save_report(doctor, args):
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

    out_md = project_root / ".regres" / "import-error-toon-report.md"
    cmd = [
        sys.executable,
        "-m",
        "regres.import_error_toon_report",
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
            cwd=str(project_root),
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
    parser.add_argument('--url', help='Analizuj moduł na podstawie URL (np. http://localhost:8100/connect-scenario)')
    parser.add_argument('--apply', action='store_true', help='Wykonaj akcje naprawcze')
    parser.add_argument('--dry-run', action='store_true', help='Dry-run dla akcji naprawczych (domyślne)')
    parser.add_argument('--llm', action='store_true', help='Generuj szczegółowy raport LLM markdown z kontekstem')
    parser.add_argument('--git-history', action='store_true', help='Analizuj historię git plików z błędami')
    parser.add_argument('--defscan-scan', help='Uruchom defscan na konkretnym katalogu')
    parser.add_argument('--refactor-scan', help='Uruchom refactor wrappers na konkretnym katalogu')
    parser.add_argument('--out-md', help='Ścieżka do raportu Markdown')
    parser.add_argument('--out-json', help='Ścieżka do raportu JSON')
    args = parser.parse_args()

    scan_root = Path(args.scan_root).resolve()
    doctor = DoctorOrchestrator(scan_root)

    if args.url:
        _handle_url_mode(args, doctor, scan_root)
        _save_report(doctor, args)
        return

    if args.import_log or args.all:
        _handle_import_errors(args, doctor, scan_root, _refresh_import_error_log)

    _handle_defscan_refactor(args, doctor)
    _save_report(doctor, args)


if __name__ == '__main__':
    main()
