"""Tests for doctor_orchestrator module."""
from pathlib import Path
from regres.doctor_orchestrator import DoctorOrchestrator
from regres.doctor_models import Diagnosis, FileAction

def test_init_sets_scan_root():
    d = DoctorOrchestrator(Path("/tmp"))
    assert str(d.scan_root) == "/tmp"
    assert d.diagnoses == []

def test_module_path_map_non_empty():
    d = DoctorOrchestrator(Path("/tmp"))
    assert "connect-test" in d.MODULE_PATH_MAP
    assert d.MODULE_PATH_MAP["connect-test"].endswith("connect-test")

def test_analyze_import_errors_missing_log():
    d = DoctorOrchestrator(Path("/tmp"))
    result = d.analyze_import_errors(Path("/nonexistent"))
    assert result == []

def test_analyze_duplicates_missing_report():
    d = DoctorOrchestrator(Path("/tmp"))
    result = d.analyze_duplicates(Path("/nonexistent"))
    assert result == []

def test_analyze_git_history_no_git():
    d = DoctorOrchestrator(Path("/tmp"))
    result = d.analyze_git_history("foo.ts")
    assert result == []

def test_apply_fixes_empty():
    d = DoctorOrchestrator(Path("/tmp"))
    result = d.apply_fixes([])
    assert result["dry_run"] is True
    assert result["actions_performed"] == []
    assert result["errors"] == []

def test_generate_report_empty():
    d = DoctorOrchestrator(Path("/tmp"))
    r = d.generate_report()
    assert r["scan_root"] == "/tmp"
    assert r["diagnoses"] == []

def test_render_markdown_empty():
    d = DoctorOrchestrator(Path("/tmp"))
    r = d.generate_report()
    md = d.render_markdown(r)
    assert "# Doctor Report" in md
    assert "/tmp" in md

def test_generate_llm_diagnosis():
    d = DoctorOrchestrator(Path("/tmp"))
    out = d.generate_llm_diagnosis("http://localhost/test", Path("/tmp"))
    assert "# LLM-Based Diagnosis Report" in out
    assert "localhost/test" in out

def test_extract_module_name():
    d = DoctorOrchestrator(Path("/tmp"))
    assert d._extract_module_name("connect-test/foo") == "connect-test"
    assert d._extract_module_name("unknown/path") == "unknown"

def test_resolve_module_path():
    d = DoctorOrchestrator(Path("/tmp"))
    assert d._resolve_module_path("connect-test").endswith("connect-test")
    assert d._resolve_module_path("nonexistent") is None
