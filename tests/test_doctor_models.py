"""Tests for doctor_models module."""
from regres.doctor_models import FileAction, ShellCommand, Diagnosis

def test_file_action_defaults():
    a = FileAction(path="/a/b.ts", action="move")
    assert a.path == "/a/b.ts"
    assert a.target is None

def test_file_action_full():
    a = FileAction(path="/a.ts", action="move", target="/c.ts", reason="dup")
    assert a.target == "/c.ts"
    assert a.reason == "dup"

def test_shell_command():
    c = ShellCommand(command="git status", description="check")
    assert c.cwd is None

def test_diagnosis_defaults():
    d = Diagnosis(summary="Missing", problem_type="import", severity="high",
                  nlp_description="mod missing")
    assert d.confidence == 0.0
    assert d.file_actions == []

def test_diagnosis_with_actions():
    fa = FileAction("/a.ts", "modify", reason="broken")
    d = Diagnosis(summary="Fix", problem_type="import", severity="medium",
                  nlp_description="upd", file_actions=[fa], confidence=0.85)
    assert len(d.file_actions) == 1
    assert d.confidence == 0.85
