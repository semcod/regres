"""Tests for doctor module."""

from regres.doctor import FileAction, ShellCommand, Diagnosis


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

def test_file_action_defaults():
    a = FileAction(path="/a/b.ts", action="move")
    assert a.path == "/a/b.ts"
    assert a.action == "move"
    assert a.target is None
    assert a.reason == ""


def test_file_action_full():
    a = FileAction(
        path="/a/b.ts",
        action="move",
        target="/c/d.ts",
        reason="duplicate",
    )
    assert a.target == "/c/d.ts"
    assert a.reason == "duplicate"


def test_shell_command_defaults():
    c = ShellCommand(command="git status", description="check git")
    assert c.command == "git status"
    assert c.description == "check git"
    assert c.cwd is None


def test_diagnosis():
    d = Diagnosis(
        summary="Missing import",
        problem_type="import_error",
        severity="high",
        nlp_description="Import module is missing",
    )
    assert d.summary == "Missing import"
    assert d.problem_type == "import_error"
    assert d.severity == "high"


# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

def test_import_doctor():
    import regres.doctor  # noqa: F401


def test_import_doctor_main():
    from regres.doctor import main
    assert callable(main)
