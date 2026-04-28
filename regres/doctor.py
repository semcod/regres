#!/usr/bin/env python3
"""doctor.py — thin re-export wrapper for backward compatibility."""

from .doctor_models import FileAction, ShellCommand, Diagnosis  # noqa: F401
from .doctor_orchestrator import DoctorOrchestrator  # noqa: F401
from .doctor_cli import main  # noqa: F401
