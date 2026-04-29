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
