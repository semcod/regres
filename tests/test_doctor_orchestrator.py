"""Tests for doctor_orchestrator module."""
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from regres.doctor_orchestrator import DoctorOrchestrator
from regres.doctor_models import Diagnosis, FileAction, ShellCommand

# ---------------------------------------------------------------------------
# Initialization tests
# ---------------------------------------------------------------------------

def test_init_sets_scan_root():
    d = DoctorOrchestrator(Path("/tmp"))
    assert str(d.scan_root) == "/tmp"
    assert d.diagnoses == []
    assert d.analysis_plan == []
    assert d.analysis_context == {}

def test_module_path_map_non_empty():
    d = DoctorOrchestrator(Path("/tmp"))
    assert "connect-test" in d.MODULE_PATH_MAP
    assert d.MODULE_PATH_MAP["connect-test"].endswith("connect-test")

def test_module_path_map_contains_all_modules():
    d = DoctorOrchestrator(Path("/tmp"))
    expected_modules = [
        "connect-test", "connect-test-protocol", "connect-test-device",
        "connect-test-full", "connect-scenario", "connect-manager",
        "connect-reports", "connect-config", "connect-data",
        "connect-id", "connect-template", "connect-workshop"
    ]
    for module in expected_modules:
        assert module in d.MODULE_PATH_MAP

# ---------------------------------------------------------------------------
# Analysis plan tests
# ---------------------------------------------------------------------------

def test_reset_analysis_plan():
    d = DoctorOrchestrator(Path("/tmp"))
    d.add_plan_step("test", "reason", "cmd")
    assert len(d.analysis_plan) == 1
    d.reset_analysis_plan()
    assert d.analysis_plan == []

def test_add_plan_step_basic():
    d = DoctorOrchestrator(Path("/tmp"))
    d.add_plan_step("step1", "test reason", "test cmd")
    assert len(d.analysis_plan) == 1
    assert d.analysis_plan[0]["name"] == "step1"
    assert d.analysis_plan[0]["reason"] == "test reason"
    assert d.analysis_plan[0]["command"] == "test cmd"
    assert d.analysis_plan[0]["status"] == "planned"

def test_add_plan_step_with_status():
    d = DoctorOrchestrator(Path("/tmp"))
    d.add_plan_step("step1", "test reason", "test cmd", status="done")
    assert d.analysis_plan[0]["status"] == "done"

def test_add_plan_step_with_details():
    d = DoctorOrchestrator(Path("/tmp"))
    d.add_plan_step("step1", "test reason", "test cmd", details="extra info")
    assert d.analysis_plan[0]["details"] == "extra info"

def test_set_analysis_context():
    d = DoctorOrchestrator(Path("/tmp"))
    d.set_analysis_context("key1", "value1")
    assert d.analysis_context["key1"] == "value1"
    d.set_analysis_context("key2", {"nested": "data"})
    assert d.analysis_context["key2"] == {"nested": "data"}

# ---------------------------------------------------------------------------
# analyze_from_url tests
# ---------------------------------------------------------------------------

def test_analyze_from_url_valid_module(tmp_path: Path):
    """Test analyze_from_url with a valid module path."""
    d = DoctorOrchestrator(tmp_path)
    module_path = tmp_path / "connect-test" / "frontend" / "src" / "modules" / "connect-test"
    module_path.mkdir(parents=True)
    
    with patch.object(d, 'analyze_with_defscan', return_value=[]):
        with patch.object(d, 'analyze_with_refactor', return_value=[]):
            with patch.object(d, 'analyze_git_history', return_value=[]):
                result = d.analyze_from_url("http://localhost/connect-test")
                assert isinstance(result, list)

def test_analyze_from_url_invalid_url(tmp_path: Path):
    """Test analyze_from_url with invalid URL returns empty list."""
    d = DoctorOrchestrator(tmp_path)
    result = d.analyze_from_url("not-a-url")
    assert result == []

def test_analyze_from_url_module_not_exists(tmp_path: Path):
    """Test analyze_from_url when module path doesn't exist."""
    d = DoctorOrchestrator(tmp_path)
    result = d.analyze_from_url("http://localhost/nonexistent-module")
    assert result == []

# ---------------------------------------------------------------------------
# analyze_import_errors tests
# ---------------------------------------------------------------------------

def test_analyze_import_errors_missing_log():
    d = DoctorOrchestrator(Path("/tmp"))
    result = d.analyze_import_errors(Path("/nonexistent"))
    assert result == []

def test_analyze_import_errors_with_valid_log(tmp_path: Path):
    """Test analyze_import_errors with a valid TS error log."""
    d = DoctorOrchestrator(tmp_path)
    log_path = tmp_path / "errors.log"
    log_path.write_text("""
frontend/src/test.ts(10,5): error TS2307: Cannot find module 'missing-mod'
frontend/src/test.ts(15,3): error TS2305: has no exported member 'Foo'
""")
    
    # Create a test file to simulate the source
    test_file = tmp_path / "frontend" / "src" / "test.ts"
    test_file.parent.mkdir(parents=True)
    test_file.write_text("import { something } from 'missing-mod'")
    
    result = d.analyze_import_errors(log_path)
    assert isinstance(result, list)

def test_analyze_import_errors_empty_log(tmp_path: Path):
    """Test analyze_import_errors with empty log."""
    d = DoctorOrchestrator(tmp_path)
    log_path = tmp_path / "errors.log"
    log_path.write_text("")
    result = d.analyze_import_errors(log_path)
    assert result == []


def test_analyze_runtime_console_missing_log(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    result = d.analyze_runtime_console(tmp_path / "missing-runtime.log")
    assert result == []


def test_analyze_runtime_console_icon_not_found(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    runtime_log = tmp_path / "runtime.log"
    runtime_log.write_text(
        "\n".join([
            "logs-collector.component.ts:55 [IconComponent] SVG icon not found: 📝 - Available icons: 149",
            "logs-collector.component.ts:55 [IconComponent] SVG icon not found: 📄 - Available icons: 149",
            "logs-collector.component.ts:55 [IconComponent] SVG icon not found: 📝 - Available icons: 149",
        ]),
        encoding="utf-8",
    )

    result = d.analyze_runtime_console(runtime_log)

    assert len(result) == 1
    diag = result[0]
    assert diag.problem_type == "runtime_icon_registry_miss"
    assert diag.severity == "medium"
    assert "📝" in diag.nlp_description
    assert "📄" in diag.nlp_description


def test_extract_page_token_for_nested_module_path(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    assert d._extract_page_token("connect-test/operator-workshop", "connect-test") == "operator-workshop"


def test_find_page_files_falls_back_to_host_iframe_wrapper(tmp_path: Path):
    """Regression test for c2004-style host iframe wrappers.

    The connect-scenario / connect-template / connect-id / connect-manager
    monorepo modules contain an empty placeholder ``frontend/src/modules/<name>``
    directory (created by scaffolding) but the actual page implementation is
    an iframe wrapper located in the host frontend at
    ``frontend/src/pages/<module>-<token>.page.ts``. The doctor must locate
    these pages instead of reporting ``page_missing``.
    """
    d = DoctorOrchestrator(tmp_path)
    module_path = tmp_path / "connect-scenario" / "frontend" / "src" / "modules" / "connect-scenario"
    module_path.mkdir(parents=True)  # exists, but empty (no module-local pages)

    host_pages = tmp_path / "frontend" / "src" / "pages"
    host_pages.mkdir(parents=True)
    wrapper = host_pages / "connect-scenario-scenarios.page.ts"
    wrapper.write_text(
        """
import { renderCqlIframe, cqlIframeStyles, attachCqlIframe } from './helpers/cql-iframe';
const IFRAME_PATH = '/scenarios';
const IFRAME_TITLE = 'CQL Scenarios Editor';
export class ScenariosPage {
  render(): string { return ScenariosPage.getContent(); }
  static getContent(): string { return renderCqlIframe(IFRAME_PATH, IFRAME_TITLE); }
  static getStyles(): string { return cqlIframeStyles(); }
  static attachEventListeners(root?: HTMLElement): void { attachCqlIframe(root, IFRAME_PATH); }
}
""",
        encoding="utf-8",
    )

    matches = d._find_page_files(module_path, "scenarios", module_name="connect-scenario")
    assert len(matches) == 1
    assert matches[0] == wrapper

    # And via the public entry point — must NOT report page_missing.
    result = d.analyze_page_implementations(
        "connect-scenario-scenarios", module_path, "connect-scenario",
    )
    assert all(diag.problem_type != "page_missing" for diag in result)


def test_page_stub_detects_generic_migration_phrase(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    module_path = tmp_path / "connect-test" / "frontend" / "src" / "modules" / "connect-test"
    pages_dir = module_path / "pages"
    pages_dir.mkdir(parents=True)
    page_file = pages_dir / "reports.page.ts"
    page_file.write_text(
        """
export class ReportsPage {
  render(): string {
    return '<div>Raporty</div><p>Widok raportów jest w trakcie migracji.</p>';
  }
}
""",
        encoding="utf-8",
    )

    result = d.analyze_page_implementations("connect-test/reports", module_path, "connect-test")

    assert len(result) == 1
    assert result[0].problem_type == "page_placeholder"
    assert "placeholder" in result[0].summary.lower()

# ---------------------------------------------------------------------------
# analyze_duplicates tests
# ---------------------------------------------------------------------------

def test_analyze_duplicates_missing_report():
    d = DoctorOrchestrator(Path("/tmp"))
    result = d.analyze_duplicates(Path("/nonexistent"))
    assert result == []

def test_analyze_duplicates_valid_report(tmp_path: Path):
    """Test analyze_duplicates with valid JSON report."""
    d = DoctorOrchestrator(tmp_path)
    report_path = tmp_path / "duplicates.json"
    report_data = {
        "duplicates": [
            {"name": "Foo", "count": 3, "locations": ["/a/Foo.ts", "/b/Foo.ts", "/c/Foo.ts"]},
            {"name": "Bar", "count": 1, "locations": ["/a/Bar.ts"]}
        ]
    }
    report_path.write_text(json.dumps(report_data))
    
    result = d.analyze_duplicates(report_path)
    assert len(result) == 1  # Only count > 1
    assert result[0].summary == "Duplikat definicji 'Foo' (3 wystąpień)"

def test_analyze_duplicates_invalid_json(tmp_path: Path):
    """Test analyze_duplicates with invalid JSON."""
    d = DoctorOrchestrator(tmp_path)
    report_path = tmp_path / "duplicates.json"
    report_path.write_text("invalid json {{{")
    result = d.analyze_duplicates(report_path)
    assert result == []

# ---------------------------------------------------------------------------
# analyze_git_history tests
# ---------------------------------------------------------------------------

def test_analyze_git_history_no_git():
    d = DoctorOrchestrator(Path("/tmp"))
    result = d.analyze_git_history("foo.ts")
    assert result == []

def test_analyze_git_history_with_git(tmp_path: Path):
    """Test analyze_git_history with git repository."""
    # Create a git repo
    import subprocess
    subprocess.run(["git", "init"], cwd=str(tmp_path), capture_output=True)
    
    d = DoctorOrchestrator(tmp_path)
    result = d.analyze_git_history("foo.ts")
    assert isinstance(result, list)

def test_analyze_git_history_timeout(tmp_path: Path):
    """Test analyze_git_history handles timeout."""
    import subprocess
    subprocess.run(["git", "init"], cwd=str(tmp_path), capture_output=True)
    
    d = DoctorOrchestrator(tmp_path)
    with patch('regres.doctor_orchestrator.subprocess.run') as mock_run:
        from subprocess import TimeoutExpired
        mock_run.side_effect = TimeoutExpired("cmd", 30)
        result = d.analyze_git_history("foo.ts")
        assert result == []

# ---------------------------------------------------------------------------
# analyze_with_defscan tests
# ---------------------------------------------------------------------------

def test_analyze_with_defscan_subprocess_failure(tmp_path: Path):
    """Test analyze_with_defscan handles subprocess failure."""
    d = DoctorOrchestrator(tmp_path)
    with patch('regres.doctor_orchestrator.subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stdout="")
        result = d.analyze_with_defscan(tmp_path)
        assert result == []

def test_analyze_with_defscan_timeout(tmp_path: Path):
    """Test analyze_with_defscan handles timeout."""
    d = DoctorOrchestrator(tmp_path)
    with patch('regres.doctor_orchestrator.subprocess.run') as mock_run:
        from subprocess import TimeoutExpired
        mock_run.side_effect = TimeoutExpired("cmd", 60)
        result = d.analyze_with_defscan(tmp_path)
        assert result == []

# ---------------------------------------------------------------------------
# analyze_with_refactor tests
# ---------------------------------------------------------------------------

def test_analyze_with_refactor_subprocess_failure(tmp_path: Path):
    """Test analyze_with_refactor handles subprocess failure."""
    d = DoctorOrchestrator(tmp_path)
    with patch('regres.doctor_orchestrator.subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stdout="")
        result = d.analyze_with_refactor(tmp_path)
        assert result == []

def test_analyze_with_refactor_with_wrappers(tmp_path: Path):
    """Test analyze_with_refactor detects wrappers."""
    d = DoctorOrchestrator(tmp_path)
    with patch('regres.doctor_orchestrator.subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="file1-wrapper.ts\nfile2-wrapper.ts\nfile3.ts"
        )
        result = d.analyze_with_refactor(tmp_path)
        assert len(result) > 0
        assert result[0].problem_type == "wrapper_analysis"

# ---------------------------------------------------------------------------
# apply_fixes tests
# ---------------------------------------------------------------------------

def test_apply_fixes_empty():
    d = DoctorOrchestrator(Path("/tmp"))
    result = d.apply_fixes([])
    assert result["dry_run"] is True
    assert result["actions_performed"] == []
    assert result["errors"] == []

def test_apply_fixes_with_modify_action():
    d = DoctorOrchestrator(Path("/tmp"))
    diagnosis = Diagnosis(
        summary="Test",
        problem_type="import_error",
        severity="high",
        nlp_description="Test",
        file_actions=[FileAction(path="/tmp/test.ts", action="modify", reason="test")]
    )
    result = d.apply_fixes([diagnosis], dry_run=True)
    assert len(result["actions_performed"]) == 1
    assert result["actions_performed"][0]["action"] == "modify"
    assert result["actions_performed"][0]["dry_run"] is True

def test_apply_fixes_with_delete_action(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    test_file = tmp_path / "test.ts"
    test_file.write_text("content")
    
    diagnosis = Diagnosis(
        summary="Test",
        problem_type="duplicate",
        severity="medium",
        nlp_description="Test",
        file_actions=[FileAction(path="test.ts", action="delete", reason="dup")]
    )
    result = d.apply_fixes([diagnosis], dry_run=True)
    assert len(result["actions_performed"]) == 1
    assert result["actions_performed"][0]["action"] == "delete"
    # File should still exist in dry_run mode
    assert test_file.exists()

def test_apply_fixes_with_shell_command():
    d = DoctorOrchestrator(Path("/tmp"))
    diagnosis = Diagnosis(
        summary="Test",
        problem_type="import_error",
        severity="high",
        nlp_description="Test",
        shell_commands=[ShellCommand(command="echo test", description="test cmd")]
    )
    result = d.apply_fixes([diagnosis], dry_run=True)
    assert len(result["actions_performed"]) == 1
    assert result["actions_performed"][0]["action"] == "shell_command"
    assert result["actions_performed"][0]["dry_run"] is True

def test_apply_fixes_error_handling():
    d = DoctorOrchestrator(Path("/tmp"))
    diagnosis = Diagnosis(
        summary="Test",
        problem_type="import_error",
        severity="high",
        nlp_description="Test",
        file_actions=[FileAction(path="/nonexistent/file.ts", action="delete", reason="test")]
    )
    result = d.apply_fixes([diagnosis], dry_run=False)
    # Current behavior: action is recorded even if file doesn't exist
    # Error is only raised if the file operation actually fails
    assert len(result["actions_performed"]) >= 1

# ---------------------------------------------------------------------------
# generate_report tests
# ---------------------------------------------------------------------------

def test_generate_report_empty():
    d = DoctorOrchestrator(Path("/tmp"))
    r = d.generate_report()
    assert r["scan_root"] == "/tmp"
    assert r["diagnoses"] == []
    assert "analysis_plan" in r
    assert "analysis_context" in r

def test_generate_report_with_diagnoses():
    d = DoctorOrchestrator(Path("/tmp"))
    d.diagnoses.append(Diagnosis(
        summary="Test diag",
        problem_type="import_error",
        severity="high",
        nlp_description="Test description",
        confidence=0.85
    ))
    r = d.generate_report()
    assert len(r["diagnoses"]) == 1
    assert r["diagnoses"][0]["summary"] == "Test diag"
    assert r["diagnoses"][0]["confidence"] == 0.85

def test_generate_report_with_analysis_plan():
    d = DoctorOrchestrator(Path("/tmp"))
    d.add_plan_step("step1", "reason1", "cmd1", status="done")
    r = d.generate_report()
    assert len(r["analysis_plan"]) == 1
    assert r["analysis_plan"][0]["name"] == "step1"

def test_generate_report_with_analysis_context():
    d = DoctorOrchestrator(Path("/tmp"))
    d.set_analysis_context("snapshot", ["file1.ts", "file2.ts"])
    r = d.generate_report()
    assert r["analysis_context"]["snapshot"] == ["file1.ts", "file2.ts"]

# ---------------------------------------------------------------------------
# render_markdown tests
# ---------------------------------------------------------------------------

def test_render_markdown_empty():
    d = DoctorOrchestrator(Path("/tmp"))
    r = d.generate_report()
    md = d.render_markdown(r)
    assert "# Doctor Report" in md
    assert "/tmp" in md
    assert "**Diagnoses:** 0" in md

def test_render_markdown_with_diagnoses():
    d = DoctorOrchestrator(Path("/tmp"))
    d.diagnoses.append(Diagnosis(
        summary="Test diag",
        problem_type="import_error",
        severity="high",
        nlp_description="Test description",
        confidence=0.85
    ))
    r = d.generate_report()
    md = d.render_markdown(r)
    assert "Test diag" in md
    assert "import_error" in md
    assert "high" in md
    assert "85%" in md

def test_render_markdown_with_file_actions():
    d = DoctorOrchestrator(Path("/tmp"))
    d.diagnoses.append(Diagnosis(
        summary="Test diag",
        problem_type="import_error",
        severity="high",
        nlp_description="Test description",
        file_actions=[FileAction(path="/tmp/test.ts", action="modify", reason="test")]
    ))
    r = d.generate_report()
    md = d.render_markdown(r)
    assert "### File Actions" in md
    assert "modify:" in md

def test_render_markdown_with_shell_commands():
    d = DoctorOrchestrator(Path("/tmp"))
    d.diagnoses.append(Diagnosis(
        summary="Test diag",
        problem_type="import_error",
        severity="high",
        nlp_description="Test description",
        shell_commands=[ShellCommand(command="echo test", description="test cmd")]
    ))
    r = d.generate_report()
    md = d.render_markdown(r)
    assert "### Shell Commands" in md
    assert "```bash" in md

def test_render_markdown_severity_emojis():
    d = DoctorOrchestrator(Path("/tmp"))
    for severity, emoji in [("low", "🟢"), ("medium", "🟡"), ("high", "🟠"), ("critical", "🔴")]:
        d.diagnoses = []
        d.diagnoses.append(Diagnosis(
            summary=f"Test {severity}",
            problem_type="test",
            severity=severity,
            nlp_description="Test"
        ))
        r = d.generate_report()
        md = d.render_markdown(r)
        assert emoji in md

def test_render_markdown_with_decision_workflow():
    d = DoctorOrchestrator(Path("/tmp"))
    d.add_plan_step("step1", "reason1", "cmd1", status="done")
    r = d.generate_report()
    md = d.render_markdown(r)
    assert "## Decision Workflow" in md
    assert "step1" in md

# ---------------------------------------------------------------------------
# generate_llm_diagnosis tests
# ---------------------------------------------------------------------------

def test_generate_llm_diagnosis():
    d = DoctorOrchestrator(Path("/tmp"))
    out = d.generate_llm_diagnosis("http://localhost/test", Path("/tmp"))
    assert "# LLM-Based Diagnosis Report" in out
    assert "localhost/test" in out

def test_generate_llm_diagnosis_sections():
    d = DoctorOrchestrator(Path("/tmp"))
    out = d.generate_llm_diagnosis("http://localhost/test", Path("/tmp"))
    expected_sections = [
        "## Git History Context",
        "## Code Structure Analysis",
        "## Duplicate Analysis (defscan)",
        "## Wrapper Analysis (refactor)",
        "## NLP Diagnosis & Recommendations",
        "## Proposed Fixes",
        "## Shell Commands to Execute",
        "## Summary"
    ]
    for section in expected_sections:
        assert section in out

# ---------------------------------------------------------------------------
# Helper method tests
# ---------------------------------------------------------------------------

def test_extract_module_name():
    d = DoctorOrchestrator(Path("/tmp"))
    assert d._extract_module_name("connect-test/foo") == "connect-test"
    assert d._extract_module_name("unknown/path") == "unknown"
    assert d._extract_module_name("") == ""

def test_resolve_module_path(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    # Create the expected directory structure
    module_path = tmp_path / "connect-test" / "frontend" / "src" / "modules" / "connect-test"
    module_path.mkdir(parents=True)
    result = d._resolve_module_path("connect-test")
    assert result is not None and result.endswith("connect-test")
    assert d._resolve_module_path("nonexistent") is None

def test_import_exists_in_source(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    test_file = tmp_path / "test.ts"
    test_file.write_text("import { foo } from 'bar'")
    
    assert d._import_exists_in_source("test.ts", "bar") is True
    assert d._import_exists_in_source("test.ts", "baz") is False

def test_import_exists_in_source_commented(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    test_file = tmp_path / "test.ts"
    test_file.write_text("// import { foo } from 'bar'")
    
    assert d._import_exists_in_source("test.ts", "bar") is False

def test_resolve_alias_target(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    # Create a file in a typical location
    target = tmp_path / "frontend" / "src" / "components" / "Button.tsx"
    target.parent.mkdir(parents=True)
    target.write_text("export const Button = () => null")
    
    result = d._resolve_alias_target("@c2004/components/Button")
    assert result is not None
    assert "Button" in result

def test_parse_ts_errors(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    log_path = tmp_path / "errors.log"
    log_path.write_text("""
frontend/src/test.ts(10,5): error TS2307: Cannot find module 'missing-mod'
frontend/src/test.ts(15,3): error TS2305: has no exported member 'Foo'
""")
    
    errors = d._parse_ts_errors(log_path)
    assert "frontend/src/test.ts" in errors
    assert len(errors["frontend/src/test.ts"]) == 2

def test_validate_errors(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    test_file = tmp_path / "test.ts"
    test_file.write_text("import { foo } from 'bar'")
    
    errors = ["Cannot find module 'bar'", "Cannot find module 'baz'"]
    validated = d._validate_errors("test.ts", errors)
    assert len(validated) == 1  # Only 'bar' exists in source
    assert "bar" in validated[0]

def test_extract_missing_modules():
    d = DoctorOrchestrator(Path("/tmp"))
    errors = [
        "Cannot find module 'foo'",
        "Cannot find module 'bar'",
        "Some other error"
    ]
    modules = d._extract_missing_modules(errors)
    assert set(modules) == {"foo", "bar"}

def test_find_main_location():
    d = DoctorOrchestrator(Path("/tmp"))
    locations = ["/a/Foo.ts", "/shared/Foo.ts", "/b/Foo.ts"]
    result = d._find_main_location(locations)
    assert result == "/shared/Foo.ts"

def test_find_main_location_no_shared():
    d = DoctorOrchestrator(Path("/tmp"))
    locations = ["/a/Foo.ts", "/b/Foo.ts", "/c/Foo.ts"]
    result = d._find_main_location(locations)
    assert result == "/a/Foo.ts"

def test_analyze_history_patterns():
    d = DoctorOrchestrator(Path("/tmp"))
    history = [
        "abc123 move file to module",
        "def456 rename component",
        "ghi789 extract function"
    ]
    result = d._analyze_history_patterns("test.ts", history)
    assert result is not None
    assert result.problem_type == "scope_drift"

def test_analyze_history_patterns_no_moves():
    d = DoctorOrchestrator(Path("/tmp"))
    history = [
        "abc123 fix bug",
        "def456 add feature",
        "ghi789 update docs"
    ]
    result = d._analyze_history_patterns("test.ts", history)
    assert result is None


# c2004-maskservice-patch-v7: module-loader compliance check
def _make_module_entry(tmp_path: Path, module_name: str, body: str) -> Path:
    module_dir = tmp_path / module_name
    module_dir.mkdir(parents=True, exist_ok=True)
    entry = module_dir / f"{module_name}.module.ts"
    entry.write_text(body, encoding="utf-8")
    return module_dir


def test_module_loader_compliance_passes_with_module_class(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    module_dir = _make_module_entry(
        tmp_path, "connect-foo",
        "export class ConnectFooModule { metadata = {}; }\n",
    )
    assert d.analyze_module_loader_compliance(module_dir, "connect-foo") is None


def test_module_loader_compliance_passes_with_default_export(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    module_dir = _make_module_entry(
        tmp_path, "connect-foo",
        "class Foo {}\nexport default Foo;\n",
    )
    assert d.analyze_module_loader_compliance(module_dir, "connect-foo") is None


def test_module_loader_compliance_flags_view_only_export(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    module_dir = _make_module_entry(
        tmp_path, "connect-deleted",
        "export class ConnectDeletedView {}\n",
    )
    diag = d.analyze_module_loader_compliance(module_dir, "connect-deleted")
    assert diag is not None
    assert diag.problem_type == "module_loader_no_class"
    assert diag.severity == "critical"
    assert "ConnectDeletedModule" in diag.nlp_description
    # Suggested wrapper should reuse the existing view class name
    assert "ConnectDeletedView" in diag.nlp_description


def test_module_loader_compliance_returns_none_when_entry_missing(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    module_dir = tmp_path / "connect-foo"
    module_dir.mkdir()
    assert d.analyze_module_loader_compliance(module_dir, "connect-foo") is None


# c2004-maskservice-patch-v8: page-registry compliance check
def _make_pages_index(tmp_path: Path, module_name: str, body: str) -> Path:
    module_dir = tmp_path / module_name
    module_dir.mkdir(parents=True, exist_ok=True)
    (module_dir / "pages-index.ts").write_text(body, encoding="utf-8")
    return module_dir


def test_page_registry_compliance_passes_when_default_present(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    module_dir = _make_pages_index(
        tmp_path, "connect-foo",
        """
        import { BasePageManager } from 'shared/base-page-manager';
        export const ConnectFooPages = {
          'requests-search': SomePage,
          'services-search': OtherPage,
        };
        export class ConnectFooPageManager extends BasePageManager {
          constructor() {
            super({ moduleName: 'connect-foo', defaultPage: 'requests-search', pages: ConnectFooPages as any });
          }
        }
        """,
    )
    assert d.analyze_page_registry_compliance(module_dir, "connect-foo") is None


def test_page_registry_compliance_flags_empty_registry(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    module_dir = _make_pages_index(
        tmp_path, "connect-workshop",
        """
        export const ConnectWorkshopPages = {
          // 'requests-search': WorkshopGenericSearchPage,
          // 'services-search': WorkshopGenericSearchPage,
        };
        export class ConnectWorkshopPageManager extends BasePageManager {
          constructor() {
            super({ moduleName: 'connect-workshop', defaultPage: 'requests-search', pages: ConnectWorkshopPages as any });
          }
        }
        """,
    )
    diag = d.analyze_page_registry_compliance(module_dir, "connect-workshop")
    assert diag is not None
    assert diag.problem_type == "page_registry_default_missing"
    assert diag.severity == "critical"
    assert "requests-search" in diag.summary
    assert "ConnectWorkshopPages" in diag.summary or "ConnectWorkshopPages" in diag.nlp_description


def test_page_registry_compliance_flags_default_not_in_registry(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    module_dir = _make_pages_index(
        tmp_path, "connect-bar",
        """
        export const ConnectBarPages = {
          'real-page': RealPage,
        };
        export class ConnectBarPageManager extends BasePageManager {
          constructor() {
            super({ moduleName: 'connect-bar', defaultPage: 'missing-default', pages: ConnectBarPages as any });
          }
        }
        """,
    )
    diag = d.analyze_page_registry_compliance(module_dir, "connect-bar")
    assert diag is not None
    assert diag.problem_type == "page_registry_default_missing"
    assert "missing-default" in diag.nlp_description


def test_page_registry_compliance_returns_none_when_no_index(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    module_dir = tmp_path / "connect-foo"
    module_dir.mkdir()
    assert d.analyze_page_registry_compliance(module_dir, "connect-foo") is None

# ---------------------------------------------------------------------------
# Helper function tests (refactored from _diagnose_page_stub)
# ---------------------------------------------------------------------------

def test_check_page_stub_indicators_placeholder_text(tmp_path: Path):
    """Test _check_page_stub_indicators detects placeholder text."""
    d = DoctorOrchestrator(tmp_path)
    text = "To jest placeholder w trakcie migracji"
    has_placeholder, is_short_stub, empty_render = d._check_page_stub_indicators(text, 5)
    assert has_placeholder is True
    assert is_short_stub is False
    assert empty_render is False

def test_check_page_stub_indicators_short_stub(tmp_path: Path):
    """Test _check_page_stub_indicators detects short stub."""
    d = DoctorOrchestrator(tmp_path)
    text = "render() { return 'placeholder'; }"
    has_placeholder, is_short_stub, empty_render = d._check_page_stub_indicators(text, 10)
    assert has_placeholder is False
    assert is_short_stub is True
    assert empty_render is False

def test_check_page_stub_indicators_empty_render(tmp_path: Path):
    """Test _check_page_stub_indicators detects empty render."""
    d = DoctorOrchestrator(tmp_path)
    text = "render() { return ''; }"
    has_placeholder, is_short_stub, empty_render = d._check_page_stub_indicators(text, 20)
    assert has_placeholder is False
    assert is_short_stub is False
    assert empty_render is True

def test_check_page_stub_indicators_normal_page(tmp_path: Path):
    """Test _check_page_stub_indicators with normal page content."""
    d = DoctorOrchestrator(tmp_path)
    text = "class TestPage { render() { return '<div>Content</div>'; } }"
    has_placeholder, is_short_stub, empty_render = d._check_page_stub_indicators(text, 50)
    assert has_placeholder is False
    assert is_short_stub is False
    assert empty_render is False

def test_detect_content_regression(tmp_path: Path):
    """Test _detect_content_regression detects shrinkage."""
    d = DoctorOrchestrator(tmp_path)
    history_candidates = [
        {"line_count": 100, "hash": "abc123"},
        {"line_count": 80, "hash": "def456"},
    ]
    is_regression = d._detect_content_regression(30, history_candidates, False)
    assert is_regression is True

def test_detect_content_regression_no_regression(tmp_path: Path):
    """Test _detect_content_regression when no regression."""
    d = DoctorOrchestrator(tmp_path)
    history_candidates = [
        {"line_count": 100, "hash": "abc123"},
    ]
    is_regression = d._detect_content_regression(80, history_candidates, False)
    assert is_regression is False

def test_detect_content_regression_with_placeholder(tmp_path: Path):
    """Test _detect_content_regression ignores placeholder case."""
    d = DoctorOrchestrator(tmp_path)
    history_candidates = [
        {"line_count": 100, "hash": "abc123"},
    ]
    is_regression = d._detect_content_regression(10, history_candidates, True)
    assert is_regression is False

def test_detect_content_regression_empty_history(tmp_path: Path):
    """Test _detect_content_regression with empty history."""
    d = DoctorOrchestrator(tmp_path)
    is_regression = d._detect_content_regression(10, [], False)
    # Empty history returns empty list (falsy)
    assert not is_regression

def test_add_backup_candidate_none(tmp_path: Path):
    """Test _add_backup_candidate with None candidate."""
    d = DoctorOrchestrator(tmp_path)
    actions = []
    commands = []
    nlp_lines = []
    
    d._add_backup_candidate(None, "test.ts", actions, commands, nlp_lines)
    
    assert len(actions) == 0
    assert len(commands) == 0
    assert len(nlp_lines) == 0

def test_add_backup_candidate_with_path(tmp_path: Path):
    """Test _add_backup_candidate with valid path."""
    d = DoctorOrchestrator(tmp_path)
    backup_path = tmp_path / "backup.ts"
    backup_path.write_text("backup content")
    
    actions = []
    commands = []
    nlp_lines = []
    
    d._add_backup_candidate(backup_path, "test.ts", actions, commands, nlp_lines)
    
    assert len(actions) == 1
    assert len(commands) == 1
    assert len(nlp_lines) == 1
    assert "backup" in nlp_lines[0].lower()

def test_add_history_candidates_empty(tmp_path: Path):
    """Test _add_history_candidates with empty list."""
    d = DoctorOrchestrator(tmp_path)
    actions = []
    commands = []
    nlp_lines = []
    
    d._add_history_candidates([], "test.ts", actions, commands, nlp_lines)
    
    assert len(actions) == 0
    assert len(commands) == 0
    assert len(nlp_lines) == 0

def test_add_history_candidates_with_data(tmp_path: Path):
    """Test _add_history_candidates with valid candidates."""
    d = DoctorOrchestrator(tmp_path)
    history_candidates = [
        {"hash": "abc123", "date": "2024-01-01", "line_count": 100, "source_path": "test.ts", "fingerprint": "abc"},
    ]
    actions = []
    commands = []
    nlp_lines = []
    
    d._add_history_candidates(history_candidates, "test.ts", actions, commands, nlp_lines)
    
    assert len(actions) == 1
    assert len(commands) == 2  # 1 for show, 1 for comparison
    assert len(nlp_lines) == 1
    assert "kandydatów" in nlp_lines[0]


# ---------------------------------------------------------------------------
# resolve_symlink tests
# ---------------------------------------------------------------------------

def test_resolve_symlink_regular_file(tmp_path: Path):
    f = tmp_path / "real.ts"
    f.write_text("content")
    result = DoctorOrchestrator.resolve_symlink(f)
    assert result == f.resolve()


def test_resolve_symlink_with_symlink(tmp_path: Path):
    target = tmp_path / "target.ts"
    target.write_text("content")
    link = tmp_path / "link.ts"
    link.symlink_to(target)
    result = DoctorOrchestrator.resolve_symlink(link)
    assert result == target.resolve()


def test_resolve_symlink_nonexistent(tmp_path: Path):
    result = DoctorOrchestrator.resolve_symlink(tmp_path / "ghost.ts")
    assert isinstance(result, Path)


# ---------------------------------------------------------------------------
# _map_workspace_to_frontend tests
# ---------------------------------------------------------------------------

def test_map_workspace_to_frontend_matches_pattern(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    src = tmp_path / "connect-config" / "frontend" / "src" / "modules" / "connect-config" / "pages" / "foo.ts"
    result = d._map_workspace_to_frontend(src)
    expected = tmp_path / "frontend" / "src" / "modules" / "connect-config" / "pages" / "foo.ts"
    assert result == expected


def test_map_workspace_to_frontend_no_match(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    src = tmp_path / "frontend" / "src" / "modules" / "connect-config" / "pages" / "foo.ts"
    result = d._map_workspace_to_frontend(src)
    assert result == src


def test_map_workspace_to_frontend_different_module_names(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    src = tmp_path / "connect-config" / "frontend" / "src" / "modules" / "connect-other" / "foo.ts"
    result = d._map_workspace_to_frontend(src)
    assert result == src


# ---------------------------------------------------------------------------
# _find_symlink_base tests
# ---------------------------------------------------------------------------

def test_find_symlink_base_no_symlink(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    nested = tmp_path / "a" / "b" / "c.ts"
    nested.parent.mkdir(parents=True)
    nested.write_text("x")
    assert d._find_symlink_base(nested) is None


def test_find_symlink_base_with_symlinked_dir(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    real_dir = tmp_path / "real_dir"
    real_dir.mkdir()
    link_dir = tmp_path / "link_dir"
    link_dir.symlink_to(real_dir)
    file_in_link = link_dir / "file.ts"
    result = d._find_symlink_base(file_in_link)
    assert result is not None


# ---------------------------------------------------------------------------
# _extract_relative_imports tests
# ---------------------------------------------------------------------------

def test_extract_relative_imports_double_quoted(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    text = 'import { Foo } from "./foo";\nimport { Bar } from "../bar";'
    result = d._extract_relative_imports(text)
    assert "./foo" in result
    assert "../bar" in result


def test_extract_relative_imports_single_quoted(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    text = "import { Baz } from './baz';"
    result = d._extract_relative_imports(text)
    assert "./baz" in result


def test_extract_relative_imports_skips_absolute(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    text = 'import { X } from "some-library";\nimport { Y } from "./local";'
    result = d._extract_relative_imports(text)
    assert "./local" in result
    assert "some-library" not in result


def test_extract_relative_imports_deduplicates(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    text = 'import { A } from "./same";\nimport { B } from "./same";'
    result = d._extract_relative_imports(text)
    assert result.count("./same") == 1


def test_extract_relative_imports_empty(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    assert d._extract_relative_imports("") == []


# ---------------------------------------------------------------------------
# _resolve_relative_import tests
# ---------------------------------------------------------------------------

def test_resolve_relative_import_finds_ts_file(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    target = tmp_path / "frontend" / "src" / "helper.ts"
    target.parent.mkdir(parents=True)
    target.write_text("export const x = 1;")
    from_file = tmp_path / "frontend" / "src" / "page.ts"
    from_file.write_text("")
    resolved, tried = d._resolve_relative_import(from_file, "./helper")
    assert resolved == target
    assert any("helper" in t for t in tried)


def test_resolve_relative_import_not_found(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    from_file = tmp_path / "frontend" / "src" / "page.ts"
    from_file.parent.mkdir(parents=True)
    from_file.write_text("")
    resolved, tried = d._resolve_relative_import(from_file, "./nonexistent-module")
    assert resolved is None
    assert len(tried) > 0


def test_resolve_relative_import_with_explicit_extension(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    target = tmp_path / "frontend" / "src" / "utils.ts"
    target.parent.mkdir(parents=True)
    target.write_text("export {};")
    from_file = tmp_path / "frontend" / "src" / "consumer.ts"
    from_file.write_text("")
    resolved, _ = d._resolve_relative_import(from_file, "./utils.ts")
    assert resolved == target


def test_resolve_relative_import_maps_workspace_to_frontend(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    target = tmp_path / "frontend" / "src" / "modules" / "connect-config" / "helper.ts"
    target.parent.mkdir(parents=True)
    target.write_text("export const h = 1;")
    from_file = tmp_path / "connect-config" / "frontend" / "src" / "modules" / "connect-config" / "page.ts"
    from_file.parent.mkdir(parents=True)
    from_file.write_text("")
    resolved, _ = d._resolve_relative_import(from_file, "./helper")
    assert resolved == target


# ---------------------------------------------------------------------------
# analyze_dependency_chain tests
# ---------------------------------------------------------------------------

def test_analyze_dependency_chain_no_imports(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    target = tmp_path / "page.ts"
    target.write_text("export class Foo { render() { return '<div/>'; } }")
    result = d.analyze_dependency_chain(target, max_depth=1)
    assert result == []


def test_analyze_dependency_chain_broken_import(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    target = tmp_path / "frontend" / "src" / "page.ts"
    target.parent.mkdir(parents=True)
    target.write_text('import { X } from "./missing-dep";')
    result = d.analyze_dependency_chain(target, max_depth=1)
    broken = [r for r in result if not r.get("exists")]
    assert len(broken) == 1
    assert "missing-dep" in broken[0]["import"]


def test_analyze_dependency_chain_resolved_import(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    base = tmp_path / "frontend" / "src"
    base.mkdir(parents=True)
    dep = base / "dep.ts"
    dep.write_text("export const x = 1;")
    target = base / "page.ts"
    target.write_text('import { x } from "./dep";')
    result = d.analyze_dependency_chain(target, max_depth=1)
    resolved = [r for r in result if r.get("exists")]
    assert len(resolved) == 1


def test_analyze_dependency_chain_missing_file(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    result = d.analyze_dependency_chain(tmp_path / "nonexistent.ts", max_depth=1)
    assert result == []


# ---------------------------------------------------------------------------
# analyze_module_loader_compliance tests
# ---------------------------------------------------------------------------

def test_analyze_module_loader_compliance_no_entry_file(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    module_dir = tmp_path / "connect-foo"
    module_dir.mkdir()
    result = d.analyze_module_loader_compliance(module_dir, "connect-foo")
    assert result is None


def test_analyze_module_loader_compliance_has_default_export(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    module_dir = tmp_path / "connect-foo"
    module_dir.mkdir()
    entry = module_dir / "connect-foo.module.ts"
    entry.write_text("export default class ConnectFooModule {}")
    result = d.analyze_module_loader_compliance(module_dir, "connect-foo")
    assert result is None


def test_analyze_module_loader_compliance_has_module_class(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    module_dir = tmp_path / "connect-bar"
    module_dir.mkdir()
    entry = module_dir / "connect-bar.module.ts"
    entry.write_text("export class ConnectBarModule extends BaseModule {}")
    result = d.analyze_module_loader_compliance(module_dir, "connect-bar")
    assert result is None


def test_analyze_module_loader_compliance_no_module_export(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    module_dir = tmp_path / "connect-baz"
    module_dir.mkdir()
    entry = module_dir / "connect-baz.module.ts"
    entry.write_text("export class ConnectBazView {}\nexport class ConnectBazHelper {}")
    result = d.analyze_module_loader_compliance(module_dir, "connect-baz")
    assert result is not None
    assert result.problem_type == "module_loader_no_class"
    assert result.severity == "critical"
    assert "ConnectBazModule" in result.nlp_description


# ---------------------------------------------------------------------------
# _fingerprint_page_content tests
# ---------------------------------------------------------------------------

def test_fingerprint_page_content_extracts_heading(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    html = "<div><h2>Konfiguracja systemu</h2><p>opis</p></div>"
    result = d._fingerprint_page_content(html)
    assert "Konfiguracja systemu" in result


def test_fingerprint_page_content_known_marker(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    result = d._fingerprint_page_content("some text Sitemap here")
    assert "Sitemap" in result


def test_fingerprint_page_content_empty(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    result = d._fingerprint_page_content("")
    assert result == ""


def test_fingerprint_page_content_max_length(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    html = "".join(f"<h1>Heading {i}</h1>" for i in range(20))
    result = d._fingerprint_page_content(html)
    assert len(result) <= 200


# ---------------------------------------------------------------------------
# _filter_actionable_diagnoses tests
# ---------------------------------------------------------------------------

def test_filter_actionable_diagnoses_keeps_with_file_actions(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    from regres.doctor_models import FileAction
    diag = Diagnosis(
        summary="test", problem_type="page_placeholder", severity="high",
        nlp_description="desc",
        file_actions=[FileAction(path="foo.ts", action="modify", reason="fix")],
    )
    result = d._filter_actionable_diagnoses([diag])
    assert len(result) == 1


def test_filter_actionable_diagnoses_keeps_import_error(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    diag = Diagnosis(
        summary="test", problem_type="import_error", severity="high",
        nlp_description="desc",
    )
    result = d._filter_actionable_diagnoses([diag])
    assert len(result) == 1


def test_filter_actionable_diagnoses_drops_empty(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    diag = Diagnosis(
        summary="no actions", problem_type="wrapper_analysis", severity="low",
        nlp_description="desc",
    )
    result = d._filter_actionable_diagnoses([diag])
    assert len(result) == 0


def test_filter_actionable_diagnoses_mixed(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    from regres.doctor_models import ShellCommand
    keep = Diagnosis(
        summary="keep", problem_type="import_error", severity="high",
        nlp_description="d", shell_commands=[ShellCommand(command="ls", description="x")],
    )
    drop = Diagnosis(
        summary="drop", problem_type="wrapper_analysis", severity="low",
        nlp_description="d",
    )
    result = d._filter_actionable_diagnoses([keep, drop])
    assert len(result) == 1
    assert result[0].summary == "keep"


# ---------------------------------------------------------------------------
# _build_url_fallback_diagnosis tests
# ---------------------------------------------------------------------------

def test_build_url_fallback_diagnosis_returns_diagnosis(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    module_path = tmp_path / "connect-foo"
    module_path.mkdir()
    diag = d._build_url_fallback_diagnosis("connect-foo/settings", module_path)
    assert diag is not None
    assert diag.problem_type == "url_targeted_review"
    assert diag.severity == "low"


def test_build_url_fallback_diagnosis_includes_candidate_file(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    module_path = tmp_path / "connect-foo"
    module_path.mkdir()
    ts_file = module_path / "settings-helper.ts"
    ts_file.write_text("export const x = 1;")
    diag = d._build_url_fallback_diagnosis("connect-foo/settings", module_path)
    paths = [a.path for a in diag.file_actions]
    assert any("settings" in p for p in paths)


# ---------------------------------------------------------------------------
# probe_vite_runtime transport error tests
# ---------------------------------------------------------------------------

def test_probe_vite_runtime_transport_error(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    with patch("urllib.request.urlopen") as mock_urlopen:
        import urllib.error
        mock_urlopen.side_effect = urllib.error.URLError("connection refused")
        result = d.probe_vite_runtime("http://localhost:8100", "frontend/src/page.ts")
    assert result["ok"] is False
    assert result["transport_error"]  # non-empty string


def test_probe_vite_runtime_ok_response(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b"export class Foo {}"
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response
        result = d.probe_vite_runtime("http://localhost:8100", "frontend/src/page.ts")
    assert result["ok"] is True
    assert result["status"] == 200


# ---------------------------------------------------------------------------
# analyze_runtime_console edge case tests
# ---------------------------------------------------------------------------

def test_analyze_runtime_console_no_icon_lines(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    log = tmp_path / "runtime.log"
    log.write_text("normal log line\nanother line\n[ERROR] something else", encoding="utf-8")
    result = d.analyze_runtime_console(log)
    assert result == []


def test_analyze_runtime_console_single_icon(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    log = tmp_path / "runtime.log"
    log.write_text(
        "[IconComponent] SVG icon not found: 🔐 - Available icons: 50",
        encoding="utf-8",
    )
    result = d.analyze_runtime_console(log)
    assert len(result) == 1
    assert result[0].problem_type == "runtime_icon_registry_miss"
    assert "🔐" in result[0].nlp_description


def test_analyze_runtime_console_many_icons_severity_high(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    log = tmp_path / "runtime.log"
    lines = [
        f"[IconComponent] SVG icon not found: icon-{i} - Available icons: 50"
        for i in range(10)
    ]
    log.write_text("\n".join(lines), encoding="utf-8")
    result = d.analyze_runtime_console(log)
    assert len(result) == 1
    assert result[0].severity == "high"


def test_analyze_runtime_console_deduplicates_icons(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    log = tmp_path / "runtime.log"
    log.write_text(
        "\n".join([
            "[IconComponent] SVG icon not found: 📝 - Available icons: 149",
        ] * 20),
        encoding="utf-8",
    )
    result = d.analyze_runtime_console(log)
    assert len(result) == 1
    assert result[0].nlp_description.count("📝") == 1


# ---------------------------------------------------------------------------
# _extract_page_token edge cases
# ---------------------------------------------------------------------------

def test_extract_page_token_module_name_only(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    assert d._extract_page_token("connect-test", "connect-test") is None


def test_extract_page_token_hyphenated_subpage(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    assert d._extract_page_token("connect-config-security-settings", "connect-config") == "security-settings"


def test_extract_page_token_empty_path(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    assert d._extract_page_token("", "connect-test") is None


def test_extract_page_token_unrelated_module(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    assert d._extract_page_token("other-module/page", "connect-test") is None


# ---------------------------------------------------------------------------
# collect_structure_snapshot tests
# ---------------------------------------------------------------------------

def test_collect_structure_snapshot_empty_dir(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    result = d.collect_structure_snapshot(max_entries=10)
    assert isinstance(result, list)


def test_collect_structure_snapshot_returns_ts_files(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    frontend_src = tmp_path / "frontend" / "src"
    frontend_src.mkdir(parents=True)
    (frontend_src / "foo.ts").write_text("export class Foo {}")
    (frontend_src / "bar.ts").write_text("export class Bar {}")
    result = d.collect_structure_snapshot(max_entries=50)
    assert isinstance(result, list)
    assert all(isinstance(e, str) for e in result)
    assert any("foo.ts" in p or "bar.ts" in p for p in result)


def test_collect_structure_snapshot_respects_max_entries(tmp_path: Path):
    d = DoctorOrchestrator(tmp_path)
    src = tmp_path / "frontend" / "src"
    src.mkdir(parents=True)
    for i in range(30):
        (src / f"file{i}.ts").write_text(f"export const x{i} = {i};")
    result = d.collect_structure_snapshot(max_entries=10)
    assert len(result) <= 10
