"""Tests for doctor_cli module."""
import argparse
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from regres.doctor_cli import (
    _build_parser,
    _refresh_import_error_log,
    _handle_url_mode,
    _handle_import_errors,
    _handle_defscan_refactor,
    _save_report,
)
from regres.doctor_orchestrator import DoctorOrchestrator
from regres.doctor_models import Diagnosis, FileAction

# ---------------------------------------------------------------------------
# Parser tests
# ---------------------------------------------------------------------------

def test_build_parser():
    parser = _build_parser()
    assert isinstance(parser, argparse.ArgumentParser)

def test_parser_scan_root():
    parser = _build_parser()
    args = parser.parse_args(["--scan-root", "."])
    assert args.scan_root == "."

def test_parser_all():
    parser = _build_parser()
    args = parser.parse_args(["--all"])
    assert args.all is True

def test_parser_url():
    parser = _build_parser()
    args = parser.parse_args(["--url", "http://localhost/connect-test"])
    assert args.url == "http://localhost/connect-test"

def test_parser_llm():
    parser = _build_parser()
    args = parser.parse_args(["--url", "http://x", "--llm"])
    assert args.llm is True

def test_parser_import_log():
    parser = _build_parser()
    args = parser.parse_args(["--import-log", "/path/to/log"])
    assert args.import_log == "/path/to/log"

def test_parser_defscan_report():
    parser = _build_parser()
    args = parser.parse_args(["--defscan-report", "/path/to/report.json"])
    assert args.defscan_report == "/path/to/report.json"

def test_parser_apply():
    parser = _build_parser()
    args = parser.parse_args(["--apply"])
    assert args.apply is True

def test_parser_dry_run():
    parser = _build_parser()
    args = parser.parse_args(["--dry-run"])
    assert args.dry_run is True

def test_parser_git_history():
    parser = _build_parser()
    args = parser.parse_args(["--git-history"])
    assert args.git_history is True

def test_parser_out_md():
    parser = _build_parser()
    args = parser.parse_args(["--out-md", "/path/to/report.md"])
    assert args.out_md == "/path/to/report.md"

def test_parser_out_json():
    parser = _build_parser()
    args = parser.parse_args(["--out-json", "/path/to/report.json"])
    assert args.out_json == "/path/to/report.json"

def test_parser_defscan_scan():
    parser = _build_parser()
    args = parser.parse_args(["--defscan-scan", "/path/to/scan"])
    assert args.defscan_scan == "/path/to/scan"

def test_parser_refactor_scan():
    parser = _build_parser()
    args = parser.parse_args(["--refactor-scan", "/path/to/scan"])
    assert args.refactor_scan == "/path/to/scan"

def test_parser_multiple_args():
    parser = _build_parser()
    args = parser.parse_args(["--all", "--scan-root", "/tmp", "--out-md", "report.md"])
    assert args.all is True
    assert args.scan_root == "/tmp"
    assert args.out_md == "report.md"

# ---------------------------------------------------------------------------
# _refresh_import_error_log tests
# ---------------------------------------------------------------------------

def test_refresh_import_no_frontend():
    result = _refresh_import_error_log(Path("/tmp"), Path("/tmp/log"))
    assert result is False

def test_refresh_import_with_frontend_subprocess_failure(tmp_path: Path):
    """Test that subprocess failure returns False."""
    frontend = tmp_path / "frontend"
    frontend.mkdir()
    log_path = tmp_path / "log.txt"
    
    with patch('regres.doctor_cli.subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stderr="error")
        result = _refresh_import_error_log(tmp_path, log_path)
        assert result is False

def test_refresh_import_timeout(tmp_path: Path):
    """Test that timeout returns False."""
    frontend = tmp_path / "frontend"
    frontend.mkdir()
    log_path = tmp_path / "log.txt"
    
    with patch('regres.doctor_cli.subprocess.run') as mock_run:
        from subprocess import TimeoutExpired
        mock_run.side_effect = TimeoutExpired("cmd", 180)
        result = _refresh_import_error_log(tmp_path, log_path)
        assert result is False

# ---------------------------------------------------------------------------
# _handle_url_mode tests
# ---------------------------------------------------------------------------

def test_handle_url_mode_without_llm(tmp_path: Path):
    """Test URL mode without LLM flag."""
    doctor = DoctorOrchestrator(tmp_path)
    args = Mock(url="http://localhost/connect-test", llm=False, apply=False, dry_run=True)
    
    with patch.object(doctor, 'analyze_from_url', return_value=[]):
        _handle_url_mode(args, doctor, tmp_path)
        assert doctor.analyze_from_url.called

def test_handle_url_mode_with_llm(tmp_path: Path):
    """Test URL mode with LLM flag."""
    doctor = DoctorOrchestrator(tmp_path)
    args = Mock(url="http://localhost/connect-test", llm=True, out_md=None)
    
    with patch.object(doctor, 'generate_llm_diagnosis', return_value="# LLM Report"):
        _handle_url_mode(args, doctor, tmp_path)
        assert doctor.generate_llm_diagnosis.called

def test_handle_url_mode_with_llm_saves_to_file(tmp_path: Path):
    """Test URL mode with LLM flag saves to file."""
    doctor = DoctorOrchestrator(tmp_path)
    out_md = tmp_path / "report.md"
    args = Mock(url="http://localhost/connect-test", llm=True, out_md=str(out_md))
    
    with patch.object(doctor, 'generate_llm_diagnosis', return_value="# LLM Report"):
        _handle_url_mode(args, doctor, tmp_path)
        assert out_md.exists()
        assert "# LLM Report" in out_md.read_text()

def test_handle_url_mode_with_apply(tmp_path: Path):
    """Test URL mode with apply flag."""
    doctor = DoctorOrchestrator(tmp_path)
    diagnosis = Diagnosis(
        summary="Test",
        problem_type="import_error",
        severity="high",
        nlp_description="Test description"
    )
    args = Mock(url="http://localhost/connect-test", llm=False, apply=True, dry_run=False)
    
    with patch.object(doctor, 'analyze_from_url', return_value=[diagnosis]):
        with patch.object(doctor, 'apply_fixes', return_value={"actions_performed": ["action1"], "errors": []}):
            _handle_url_mode(args, doctor, tmp_path)
            assert doctor.apply_fixes.called

# ---------------------------------------------------------------------------
# _handle_import_errors tests
# ---------------------------------------------------------------------------

def test_handle_import_errors_with_log(tmp_path: Path):
    """Test import error handling with explicit log path."""
    doctor = DoctorOrchestrator(tmp_path)
    log_path = tmp_path / "import.log"
    log_path.write_text("test log content")
    args = Mock(import_log=str(log_path), all=False, git_history=False)
    refresh_fn = Mock()
    
    with patch.object(doctor, 'analyze_import_errors', return_value=[]):
        _handle_import_errors(args, doctor, tmp_path, refresh_fn)
        assert doctor.analyze_import_errors.called
        assert not refresh_fn.called

def test_handle_import_errors_without_log_all_flag(tmp_path: Path):
    """Test import error handling without log but with all flag triggers refresh."""
    doctor = DoctorOrchestrator(tmp_path)
    args = Mock(import_log=None, all=True, git_history=False)
    refresh_fn = Mock(return_value=True)
    
    with patch.object(doctor, 'analyze_import_errors', return_value=[]):
        _handle_import_errors(args, doctor, tmp_path, refresh_fn)
        assert refresh_fn.called

def test_handle_import_errors_with_git_history(tmp_path: Path):
    """Test import error handling with git history analysis."""
    doctor = DoctorOrchestrator(tmp_path)
    log_path = tmp_path / "import.log"
    log_path.write_text("test log content")
    
    diagnosis = Diagnosis(
        summary="Import error",
        problem_type="import_error",
        severity="high",
        nlp_description="Test",
        file_actions=[FileAction(path="/tmp/test.ts", action="modify")]
    )
    args = Mock(import_log=str(log_path), all=True, git_history=True)
    refresh_fn = Mock()
    
    with patch.object(doctor, 'analyze_import_errors', return_value=[diagnosis]):
        with patch.object(doctor, 'analyze_git_history', return_value=[]):
            _handle_import_errors(args, doctor, tmp_path, refresh_fn)
            assert doctor.analyze_git_history.called

# ---------------------------------------------------------------------------
# _handle_defscan_refactor tests
# ---------------------------------------------------------------------------

def test_handle_defscan_refactor_with_report(tmp_path: Path):
    """Test defscan/refactor handling with report."""
    doctor = DoctorOrchestrator(tmp_path)
    report_path = tmp_path / "report.json"
    report_path.write_text('{"test": "data"}')
    args = Mock(defscan_report=str(report_path), defscan_scan=None, refactor_scan=None)
    
    with patch.object(doctor, 'analyze_duplicates', return_value=[]):
        _handle_defscan_refactor(args, doctor)
        assert doctor.analyze_duplicates.called

def test_handle_defscan_refactor_with_scan(tmp_path: Path):
    """Test defscan/refactor handling with scan."""
    doctor = DoctorOrchestrator(tmp_path)
    scan_path = tmp_path / "scan"
    scan_path.mkdir()
    args = Mock(defscan_report=None, defscan_scan=str(scan_path), refactor_scan=None)
    
    with patch.object(doctor, 'analyze_with_defscan', return_value=[]):
        _handle_defscan_refactor(args, doctor)
        assert doctor.analyze_with_defscan.called

def test_handle_defscan_refactor_with_refactor_scan(tmp_path: Path):
    """Test defscan/refactor handling with refactor scan."""
    doctor = DoctorOrchestrator(tmp_path)
    scan_path = tmp_path / "scan"
    scan_path.mkdir()
    args = Mock(defscan_report=None, defscan_scan=None, refactor_scan=str(scan_path))
    
    with patch.object(doctor, 'analyze_with_refactor', return_value=[]):
        _handle_defscan_refactor(args, doctor)
        assert doctor.analyze_with_refactor.called

def test_handle_defscan_refactor_none(tmp_path: Path):
    """Test defscan/refactor handling with no scans."""
    doctor = DoctorOrchestrator(tmp_path)
    args = Mock(defscan_report=None, defscan_scan=None, refactor_scan=None)
    
    _handle_defscan_refactor(args, doctor)
    assert len(doctor.diagnoses) == 0

# ---------------------------------------------------------------------------
# _save_report tests
# ---------------------------------------------------------------------------

def test_save_report_to_stdout(tmp_path: Path):
    """Test saving report to stdout."""
    doctor = DoctorOrchestrator(tmp_path)
    args = Mock(out_json=None, out_md=None)
    
    with patch('builtins.print') as mock_print:
        _save_report(doctor, args)
        assert mock_print.called

def test_save_report_to_json(tmp_path: Path):
    """Test saving report to JSON file."""
    doctor = DoctorOrchestrator(tmp_path)
    out_json = tmp_path / "report.json"
    args = Mock(out_json=str(out_json), out_md=None)
    
    _save_report(doctor, args)
    assert out_json.exists()
    import json
    content = json.loads(out_json.read_text())
    assert "scan_root" in content

def test_save_report_to_md(tmp_path: Path):
    """Test saving report to Markdown file."""
    doctor = DoctorOrchestrator(tmp_path)
    out_md = tmp_path / "report.md"
    args = Mock(out_json=None, out_md=str(out_md))
    
    _save_report(doctor, args)
    assert out_md.exists()
    content = out_md.read_text()
    assert "# Doctor Report" in content

def test_save_report_to_both_formats(tmp_path: Path):
    """Test saving report to both JSON and Markdown."""
    doctor = DoctorOrchestrator(tmp_path)
    out_json = tmp_path / "report.json"
    out_md = tmp_path / "report.md"
    args = Mock(out_json=str(out_json), out_md=str(out_md))
    
    _save_report(doctor, args)
    assert out_json.exists()
    assert out_md.exists()
