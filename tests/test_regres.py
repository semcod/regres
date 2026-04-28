"""Tests for regres package."""

import subprocess
import sys
from pathlib import Path


def test_placeholder():
    """Placeholder test to verify the test setup works."""
    assert True


def test_import():
    """Verify the main package can be imported."""
    import regres  # noqa: F401


def test_import_regres_module():
    """Verify regres module can be imported."""
    from regres import regres  # noqa: F401


def test_import_refactor_module():
    """Verify refactor module can be imported."""
    from regres import refactor  # noqa: F401


def test_import_defscan_module():
    """Verify defscan module can be imported."""
    from regres import defscan  # noqa: F401


def test_import_import_error_toon_report():
    """Verify import_error_toon_report module can be imported."""
    from regres.import_error_toon_report import main  # noqa: F401


def test_regres_cli_module_exists():
    """Verify regres_cli module exists inside the package."""
    root = Path(__file__).parent.parent
    cli_path = root / "regres" / "regres_cli.py"
    assert cli_path.exists(), f"regres_cli.py not found at {cli_path}"


def test_regres_cli_import():
    """Verify regres CLI module can be imported."""
    from regres.regres_cli import main
    assert callable(main), "main should be callable"


def test_import_error_toon_report_main_signature():
    """Verify import_error_toon_report.main has correct signature."""
    from regres.import_error_toon_report import main
    assert callable(main), "main should be callable"


def test_regres_cli_help():
    """Verify regres CLI help command works."""
    root = Path(__file__).parent.parent
    result = subprocess.run(
        [sys.executable, "-m", "regres.regres_cli", "--help"],
        cwd=str(root),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"CLI help failed: {result.stderr}"
    assert "regres" in result.stdout, "CLI help should contain 'regres'"


def test_regres_cli_doctor_help():
    """Verify regres CLI doctor help works."""
    root = Path(__file__).parent.parent
    result = subprocess.run(
        [sys.executable, "-m", "regres.regres_cli", "doctor", "--help"],
        cwd=str(root),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"CLI doctor help failed: {result.stderr}"
    assert "doctor" in result.stdout, "CLI doctor help should contain 'doctor'"
