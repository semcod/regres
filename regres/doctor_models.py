#!/usr/bin/env python3
"""
doctor_models.py — dataclasses for doctor module.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


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
