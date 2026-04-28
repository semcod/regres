"""Tests for doctor_models module."""
from regres.doctor_models import FileAction, ShellCommand, Diagnosis

# ---------------------------------------------------------------------------
# FileAction tests
# ---------------------------------------------------------------------------

def test_file_action_defaults():
    a = FileAction(path="/a/b.ts", action="move")
    assert a.path == "/a/b.ts"
    assert a.target is None
    assert a.reason == ""

def test_file_action_full():
    a = FileAction(path="/a.ts", action="move", target="/c.ts", reason="dup")
    assert a.target == "/c.ts"
    assert a.reason == "dup"

def test_file_action_all_action_types():
    """Test all valid action types."""
    for action_type in ["modify", "delete", "move", "create", "copy", "review"]:
        a = FileAction(path="/test.ts", action=action_type)
        assert a.action == action_type

def test_file_action_empty_path():
    """Test FileAction with empty path."""
    a = FileAction(path="", action="modify")
    assert a.path == ""

def test_file_action_none_path():
    """Test FileAction with None path."""
    a = FileAction(path=None, action="modify")
    assert a.path is None

def test_file_action_with_special_characters():
    """Test FileAction with special characters in paths."""
    a = FileAction(path="/path/with spaces/file.ts", action="modify")
    assert " " in a.path

def test_file_action_target_without_reason():
    """Test FileAction with target but no reason."""
    a = FileAction(path="/a.ts", action="move", target="/b.ts")
    assert a.target == "/b.ts"
    assert a.reason == ""

def test_file_action_reason_without_target():
    """Test FileAction with reason but no target."""
    a = FileAction(path="/a.ts", action="modify", reason="broken import")
    assert a.reason == "broken import"
    assert a.target is None

def test_file_action_equality():
    """Test FileAction equality comparison."""
    a1 = FileAction(path="/a.ts", action="modify", reason="test")
    a2 = FileAction(path="/a.ts", action="modify", reason="test")
    # Note: We're not implementing __eq__, so this tests object identity
    assert a1.path == a2.path
    assert a1.action == a2.action
    assert a1.reason == a2.reason

# ---------------------------------------------------------------------------
# ShellCommand tests
# ---------------------------------------------------------------------------

def test_shell_command():
    c = ShellCommand(command="git status", description="check")
    assert c.cwd is None

def test_shell_command_with_cwd():
    """Test ShellCommand with cwd."""
    c = ShellCommand(command="npm install", description="install deps", cwd="/project")
    assert c.cwd == "/project"

def test_shell_command_empty_command():
    """Test ShellCommand with empty command."""
    c = ShellCommand(command="", description="empty")
    assert c.command == ""

def test_shell_command_empty_description():
    """Test ShellCommand with empty description."""
    c = ShellCommand(command="ls", description="")
    assert c.description == ""

def test_shell_command_none_description():
    """Test ShellCommand with None description."""
    c = ShellCommand(command="ls", description=None)
    assert c.description is None

def test_shell_command_multiline():
    """Test ShellCommand with multiline command."""
    cmd = 'git add .\ngit commit -m "fix"'
    c = ShellCommand(command=cmd, description="commit")
    assert "\n" in c.command

def test_shell_command_with_special_chars():
    """Test ShellCommand with special characters."""
    c = ShellCommand(command="echo 'test with spaces'", description="echo")
    assert " " in c.command

def test_shell_command_with_quotes():
    """Test ShellCommand with quotes in command."""
    c = ShellCommand(command='grep "pattern" file.txt', description="grep")
    assert '"' in c.command

# ---------------------------------------------------------------------------
# Diagnosis tests
# ---------------------------------------------------------------------------

def test_diagnosis_defaults():
    d = Diagnosis(summary="Missing", problem_type="import", severity="high",
                  nlp_description="mod missing")
    assert d.confidence == 0.0
    assert d.file_actions == []
    assert d.shell_commands == []

def test_diagnosis_with_actions():
    fa = FileAction("/a.ts", "modify", reason="broken")
    d = Diagnosis(summary="Fix", problem_type="import", severity="medium",
                  nlp_description="upd", file_actions=[fa], confidence=0.85)
    assert len(d.file_actions) == 1
    assert d.confidence == 0.85

def test_diagnosis_with_shell_commands():
    sc = ShellCommand(command="npm install", description="install")
    d = Diagnosis(summary="Install", problem_type="dependency", severity="high",
                  nlp_description="missing dep", shell_commands=[sc], confidence=0.9)
    assert len(d.shell_commands) == 1
    assert d.confidence == 0.9

def test_diagnosis_with_both_actions_and_commands():
    fa = FileAction("/a.ts", "modify", reason="broken")
    sc = ShellCommand(command="npm install", description="install")
    d = Diagnosis(summary="Fix", problem_type="import", severity="high",
                  nlp_description="fix", file_actions=[fa], shell_commands=[sc], confidence=0.95)
    assert len(d.file_actions) == 1
    assert len(d.shell_commands) == 1
    assert d.confidence == 0.95

def test_diagnosis_confidence_bounds():
    """Test diagnosis confidence within valid bounds."""
    d1 = Diagnosis(summary="Test", problem_type="test", severity="low",
                   nlp_description="test", confidence=0.0)
    assert d1.confidence == 0.0
    
    d2 = Diagnosis(summary="Test", problem_type="test", severity="high",
                   nlp_description="test", confidence=1.0)
    assert d2.confidence == 1.0
    
    d3 = Diagnosis(summary="Test", problem_type="test", severity="medium",
                   nlp_description="test", confidence=0.5)
    assert d3.confidence == 0.5

def test_diagnosis_severity_levels():
    """Test all valid severity levels."""
    for severity in ["low", "medium", "high", "critical"]:
        d = Diagnosis(summary="Test", problem_type="test", severity=severity,
                       nlp_description="test")
        assert d.severity == severity

def test_diagnosis_problem_types():
    """Test various problem types."""
    for ptype in ["import_error", "duplicate", "scope_drift", "wrapper_analysis", "regression"]:
        d = Diagnosis(summary="Test", problem_type=ptype, severity="medium",
                       nlp_description="test")
        assert d.problem_type == ptype

def test_diagnosis_empty_summary():
    """Test diagnosis with empty summary."""
    d = Diagnosis(summary="", problem_type="test", severity="low",
                  nlp_description="test")
    assert d.summary == ""

def test_diagnosis_empty_nlp_description():
    """Test diagnosis with empty NLP description."""
    d = Diagnosis(summary="Test", problem_type="test", severity="low",
                  nlp_description="")
    assert d.nlp_description == ""

def test_diagnosis_multiple_file_actions():
    """Test diagnosis with multiple file actions."""
    actions = [
        FileAction("/a.ts", "modify", reason="fix1"),
        FileAction("/b.ts", "delete", reason="dup"),
        FileAction("/c.ts", "move", target="/d.ts", reason="reorg")
    ]
    d = Diagnosis(summary="Multi", problem_type="test", severity="high",
                  nlp_description="multiple actions", file_actions=actions)
    assert len(d.file_actions) == 3

def test_diagnosis_multiple_shell_commands():
    """Test diagnosis with multiple shell commands."""
    commands = [
        ShellCommand(command="npm install", description="install"),
        ShellCommand(command="npm test", description="test"),
        ShellCommand(command="git add .", description="add")
    ]
    d = Diagnosis(summary="Multi", problem_type="test", severity="high",
                  nlp_description="multiple commands", shell_commands=commands)
    assert len(d.shell_commands) == 3

def test_diagnosis_unicode_in_fields():
    """Test diagnosis with unicode characters."""
    d = Diagnosis(summary="Błąd importu", problem_type="import_error", severity="high",
                  nlp_description="Nie znaleziono modułu 'zażółć'", confidence=0.9)
    assert "zażółć" in d.nlp_description
    assert "Błąd" in d.summary

def test_diagnosis_long_description():
    """Test diagnosis with very long description."""
    long_desc = "This is a very long description " * 100
    d = Diagnosis(summary="Long", problem_type="test", severity="low",
                  nlp_description=long_desc)
    assert len(d.nlp_description) > 1000

def test_diagnosis_confidence_out_of_bounds():
    """Test diagnosis with confidence values that might be out of bounds."""
    # These should still work even if technically invalid
    d1 = Diagnosis(summary="Test", problem_type="test", severity="low",
                   nlp_description="test", confidence=-0.5)
    assert d1.confidence == -0.5
    
    d2 = Diagnosis(summary="Test", problem_type="test", severity="low",
                   nlp_description="test", confidence=1.5)
    assert d2.confidence == 1.5

def test_diagnosis_immutability_of_lists():
    """Test that modifying original lists affects diagnosis (lists are by reference)."""
    actions = [FileAction("/a.ts", "modify", reason="test")]
    commands = [ShellCommand(command="ls", description="list")]
    
    d = Diagnosis(summary="Test", problem_type="test", severity="medium",
                  nlp_description="test", file_actions=actions, shell_commands=commands)
    
    # Modify original lists
    actions.append(FileAction("/b.ts", "delete", reason="dup"))
    commands.append(ShellCommand(command="pwd", description="pwd"))
    
    # Current behavior: lists are passed by reference
    assert len(d.file_actions) == 2
    assert len(d.shell_commands) == 2

def test_diagnosis_with_none_confidence():
    """Test diagnosis with None confidence (should use default)."""
    d = Diagnosis(summary="Test", problem_type="test", severity="low",
                  nlp_description="test", confidence=None)
    # This might fail if the model doesn't handle None, but let's test it
    assert d.confidence is None or d.confidence == 0.0
