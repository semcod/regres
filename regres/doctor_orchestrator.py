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
        "connect-id": "connect-id/frontend/src/modules/connect-id",
        "connect-template": "connect-template/frontend/src/modules/connect-template",
        "connect-workshop": "connect-workshop/frontend/src/modules/connect-workshop",
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
        diagnoses.extend(self.analyze_with_defscan(full_module_path))
        diagnoses.extend(self.analyze_with_refactor(full_module_path))

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
        return {
            "scan_root": str(self.scan_root),
            "analysis_plan": self.analysis_plan,
            "analysis_context": self.analysis_context,
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
    ) -> None:
        step = {
            "name": name,
            "reason": reason,
            "command": command,
            "status": status,
        }
        if details:
            step["details"] = details
        self.analysis_plan.append(step)

    def set_analysis_context(self, key: str, value: Any) -> None:
        self.analysis_context[key] = value

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _extract_module_name(self, path: str) -> Optional[str]:
        for possible_module in self.MODULE_PATH_MAP.keys():
            if path.startswith(possible_module):
                return possible_module
        parts = path.split('/')
        return parts[0] if parts else None

    def _resolve_module_path(self, module_name: str) -> Optional[str]:
        module_path = self.MODULE_PATH_MAP.get(module_name)
        if module_path:
            return module_path
        for possible_path in [
            f"{module_name}/frontend/src/modules/{module_name}",
            f"{module_name}/frontend/src",
            f"{module_name}/backend",
            f"frontend/src/modules/{module_name}",
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

        lines.append("Kolejność kroków wybrana automatycznie na bazie parametrów wejściowych:")
        lines.append("")
        for idx, step in enumerate(plan, 1):
            lines.append(f"{idx}. **{step.get('name', 'step')}** — {step.get('reason', '')}")
            if step.get("details"):
                lines.append(f"   - {step['details']}")
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
                proposals.append(f"Skonsoliduj duplikaty: {d.summary}")
            elif d.problem_type == "wrapper_analysis":
                proposals.append(f"Zredukuj wrappery i uprość API: {d.summary}")
            elif d.problem_type == "scope_drift":
                proposals.append(f"Ustabilizuj scope modułu na bazie historii: {d.summary}")
            elif d.problem_type == "import_error":
                proposals.append(f"Ujednolić aliasy/importy: {d.summary}")
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
