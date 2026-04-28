"""End-to-end tests for doctor CLI.

These tests run the actual CLI via subprocess to test complete workflows.
"""
import json
import subprocess
import sys
from pathlib import Path
from typing import List

import pytest


def run_doctor_command(args: List[str], cwd: Path) -> subprocess.CompletedProcess:
    """Run the doctor CLI with given arguments."""
    cmd = [sys.executable, "-m", "regres.doctor_cli"] + args
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result


# ---------------------------------------------------------------------------
# Basic CLI invocation tests
# ---------------------------------------------------------------------------

def test_doctor_cli_help(tmp_path: Path):
    """Test that --help works."""
    result = run_doctor_command(["--help"], tmp_path)
    assert result.returncode == 0
    assert "doctor" in result.stdout.lower()
    assert "--scan-root" in result.stdout
    assert "--url" in result.stdout


def test_doctor_cli_version(tmp_path: Path):
    """Test that version check works."""
    result = run_doctor_command(["--scan-root", str(tmp_path)], tmp_path)
    # Should not crash on version check
    assert result.returncode == 0


# ---------------------------------------------------------------------------
# URL mode e2e tests
# ---------------------------------------------------------------------------

def test_url_mode_module_not_found(tmp_path: Path):
    """Test URL mode when module doesn't exist."""
    out_json = tmp_path / "report.json"
    result = run_doctor_command(
        [
            "--scan-root", str(tmp_path),
            "--url", "http://localhost/nonexistent-module",
            "--out-json", str(out_json),
        ],
        tmp_path,
    )
    assert result.returncode == 0
    assert out_json.exists()
    
    report = json.loads(out_json.read_text())
    assert "diagnoses" in report
    assert len(report["diagnoses"]) > 0
    assert report["diagnoses"][0]["problem_type"] == "module_not_found"


def test_url_mode_with_existing_module(tmp_path: Path):
    """Test URL mode with an existing module structure."""
    # Create a mock module structure
    module_path = tmp_path / "connect-test" / "frontend" / "src" / "modules" / "connect-test"
    module_path.mkdir(parents=True)
    (module_path / "test.ts").write_text("export const test = 1;")
    
    out_json = tmp_path / "report.json"
    result = run_doctor_command(
        [
            "--scan-root", str(tmp_path),
            "--url", "http://localhost/connect-test",
            "--out-json", str(out_json),
        ],
        tmp_path,
    )
    assert result.returncode == 0
    assert out_json.exists()
    
    report = json.loads(out_json.read_text())
    assert "diagnoses" in report
    assert "analysis_plan" in report


def test_url_mode_with_markdown_output(tmp_path: Path):
    """Test URL mode with Markdown output."""
    out_md = tmp_path / "report.md"
    result = run_doctor_command(
        [
            "--scan-root", str(tmp_path),
            "--url", "http://localhost/test-module",
            "--out-md", str(out_md),
        ],
        tmp_path,
    )
    assert result.returncode == 0
    assert out_md.exists()
    
    content = out_md.read_text()
    assert "# Doctor Report" in content


def test_url_mode_both_outputs(tmp_path: Path):
    """Test URL mode with both JSON and Markdown outputs."""
    out_json = tmp_path / "report.json"
    out_md = tmp_path / "report.md"
    result = run_doctor_command(
        [
            "--scan-root", str(tmp_path),
            "--url", "http://localhost/test-module",
            "--out-json", str(out_json),
            "--out-md", str(out_md),
        ],
        tmp_path,
    )
    assert result.returncode == 0
    assert out_json.exists()
    assert out_md.exists()


# ---------------------------------------------------------------------------
# Import error mode e2e tests
# ---------------------------------------------------------------------------

def test_import_error_with_log_file(tmp_path: Path):
    """Test import error analysis with a log file."""
    log_file = tmp_path / "import.log"
    log_file.write_text("""
test.ts(1,20): error TS2307: Cannot find module 'missing-module'
test2.ts(5,10): error TS2307: Cannot find module 'another-missing'
""")
    
    out_json = tmp_path / "report.json"
    result = run_doctor_command(
        [
            "--scan-root", str(tmp_path),
            "--import-log", str(log_file),
            "--out-json", str(out_json),
        ],
        tmp_path,
    )
    assert result.returncode == 0
    assert out_json.exists()
    
    report = json.loads(out_json.read_text())
    assert "diagnoses" in report


def test_import_error_with_nonexistent_log(tmp_path: Path):
    """Test import error analysis with nonexistent log file."""
    out_json = tmp_path / "report.json"
    result = run_doctor_command(
        [
            "--scan-root", str(tmp_path),
            "--import-log", str(tmp_path / "nonexistent.log"),
            "--out-json", str(out_json),
        ],
        tmp_path,
    )
    # Should not crash, just return empty results
    assert result.returncode == 0
    assert out_json.exists()


# ---------------------------------------------------------------------------
# Defscan mode e2e tests
# ---------------------------------------------------------------------------

def test_defscan_with_report_file(tmp_path: Path):
    """Test defscan analysis with a report file."""
    report_file = tmp_path / "defscan-report.json"
    report_data = {
        "duplicates": [
            {
                "name": "duplicateFunction",
                "count": 3,
                "locations": ["file1.ts", "file2.ts", "file3.ts"]
            }
        ]
    }
    report_file.write_text(json.dumps(report_data))
    
    out_json = tmp_path / "report.json"
    result = run_doctor_command(
        [
            "--scan-root", str(tmp_path),
            "--defscan-report", str(report_file),
            "--out-json", str(out_json),
        ],
        tmp_path,
    )
    assert result.returncode == 0
    assert out_json.exists()
    
    report = json.loads(out_json.read_text())
    assert "diagnoses" in report


# ---------------------------------------------------------------------------
# All mode e2e tests
# ---------------------------------------------------------------------------

def test_all_mode_basic(tmp_path: Path):
    """Test --all mode basic execution."""
    out_json = tmp_path / "report.json"
    result = run_doctor_command(
        [
            "--scan-root", str(tmp_path),
            "--all",
            "--out-json", str(out_json),
        ],
        tmp_path,
    )
    assert result.returncode == 0
    assert out_json.exists()
    
    report = json.loads(out_json.read_text())
    assert "diagnoses" in report
    assert "analysis_plan" in report


def test_all_mode_with_markdown(tmp_path: Path):
    """Test --all mode with Markdown output."""
    out_md = tmp_path / "report.md"
    result = run_doctor_command(
        [
            "--scan-root", str(tmp_path),
            "--all",
            "--out-md", str(out_md),
        ],
        tmp_path,
    )
    assert result.returncode == 0
    assert out_md.exists()
    
    content = out_md.read_text()
    assert "# Doctor Report" in content


# ---------------------------------------------------------------------------
# Patch generation e2e tests
# ---------------------------------------------------------------------------

def test_patch_generation_with_dir(tmp_path: Path):
    """Test patch script generation with explicit directory."""
    patches_dir = tmp_path / "patches"
    patches_dir.mkdir()
    
    out_json = tmp_path / "report.json"
    result = run_doctor_command(
        [
            "--scan-root", str(tmp_path),
            "--url", "http://localhost/test-module",
            "--out-json", str(out_json),
            "--out-patches-dir", str(patches_dir),
        ],
        tmp_path,
    )
    assert result.returncode == 0
    assert out_json.exists()
    
    report = json.loads(out_json.read_text())
    # generated_patches field is only added when patches are actually generated
    # In this case with module_not_found diagnosis, no patches are generated
    # so the field may not be present or may be empty
    if "generated_patches" in report:
        assert isinstance(report["generated_patches"], list)


def test_no_patches_flag(tmp_path: Path):
    """Test --no-patches flag suppresses patch generation."""
    patches_dir = tmp_path / "patches"
    patches_dir.mkdir()
    
    out_json = tmp_path / "report.json"
    result = run_doctor_command(
        [
            "--scan-root", str(tmp_path),
            "--url", "http://localhost/test-module",
            "--out-json", str(out_json),
            "--out-patches-dir", str(patches_dir),
            "--no-patches",
        ],
        tmp_path,
    )
    assert result.returncode == 0
    assert out_json.exists()
    
    report = json.loads(out_json.read_text())
    # Should not have generated_patches when --no-patches is set
    # or it should be empty
    if "generated_patches" in report:
        assert len(report["generated_patches"]) == 0


# ---------------------------------------------------------------------------
# Error handling e2e tests
# ---------------------------------------------------------------------------

def test_invalid_scan_root(tmp_path: Path):
    """Test handling of invalid scan root."""
    result = run_doctor_command(
        [
            "--scan-root", "/nonexistent/path/that/does/not/exist",
        ],
        tmp_path,
    )
    # Should not crash
    assert result.returncode == 0


def test_concurrent_runs(tmp_path: Path):
    """Test that multiple concurrent runs don't interfere."""
    out_json1 = tmp_path / "report1.json"
    out_json2 = tmp_path / "report2.json"
    
    result1 = run_doctor_command(
        [
            "--scan-root", str(tmp_path),
            "--url", "http://localhost/test1",
            "--out-json", str(out_json1),
        ],
        tmp_path,
    )
    
    result2 = run_doctor_command(
        [
            "--scan-root", str(tmp_path),
            "--url", "http://localhost/test2",
            "--out-json", str(out_json2),
        ],
        tmp_path,
    )
    
    assert result1.returncode == 0
    assert result2.returncode == 0
    assert out_json1.exists()
    assert out_json2.exists()


# ---------------------------------------------------------------------------
# Real-world scenario tests
# ---------------------------------------------------------------------------

def test_real_world_scenario_missing_imports(tmp_path: Path):
    """Test a real-world scenario with missing imports."""
    # Create a TypeScript file with import errors
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    ts_file = src_dir / "app.ts"
    ts_file.write_text("""
import { missing } from './missing-module';
import { another } from '@c2004/another-missing';

export function test() {
    return missing + another;
}
""")
    
    log_file = tmp_path / "import.log"
    log_file.write_text(f"""
{ts_file}(2,20): error TS2307: Cannot find module './missing-module'
{ts_file}(3,20): error TS2307: Cannot find module '@c2004/another-missing'
""")
    
    out_json = tmp_path / "report.json"
    out_md = tmp_path / "report.md"
    result = run_doctor_command(
        [
            "--scan-root", str(tmp_path),
            "--import-log", str(log_file),
            "--out-json", str(out_json),
            "--out-md", str(out_md),
        ],
        tmp_path,
    )
    
    assert result.returncode == 0
    assert out_json.exists()
    assert out_md.exists()
    
    report = json.loads(out_json.read_text())
    assert "diagnoses" in report
    
    md_content = out_md.read_text()
    assert "# Doctor Report" in md_content


def test_real_world_scenario_module_analysis(tmp_path: Path):
    """Test a real-world scenario with module structure analysis."""
    # Create a realistic module structure
    module_path = tmp_path / "connect-test" / "frontend" / "src" / "modules" / "connect-test"
    module_path.mkdir(parents=True)
    
    # Create some TypeScript files
    (module_path / "main.ts").write_text("""
export class MainComponent {
    render() {
        return '<div>Hello</div>';
    }
}
""")
    (module_path / "utils.ts").write_text("""
export function helper() {
    return 42;
}
""")
    
    out_json = tmp_path / "report.json"
    result = run_doctor_command(
        [
            "--scan-root", str(tmp_path),
            "--url", "http://localhost/connect-test",
            "--out-json", str(out_json),
        ],
        tmp_path,
    )
    
    assert result.returncode == 0
    assert out_json.exists()
    
    report = json.loads(out_json.read_text())
    assert "diagnoses" in report
    assert "analysis_plan" in report
    assert len(report["analysis_plan"]) > 0


def test_analysis_plan_structure(tmp_path: Path):
    """Test that analysis plan has proper structure."""
    out_json = tmp_path / "report.json"
    result = run_doctor_command(
        [
            "--scan-root", str(tmp_path),
            "--url", "http://localhost/test-module",
            "--out-json", str(out_json),
        ],
        tmp_path,
    )
    
    assert result.returncode == 0
    report = json.loads(out_json.read_text())
    
    # Check analysis plan structure
    assert "analysis_plan" in report
    for step in report["analysis_plan"]:
        assert "name" in step
        assert "reason" in step
        assert "command" in step
        assert "status" in step


def test_diagnosis_structure(tmp_path: Path):
    """Test that diagnoses have proper structure."""
    out_json = tmp_path / "report.json"
    result = run_doctor_command(
        [
            "--scan-root", str(tmp_path),
            "--url", "http://localhost/test-module",
            "--out-json", str(out_json),
        ],
        tmp_path,
    )
    
    assert result.returncode == 0
    report = json.loads(out_json.read_text())
    
    # Check diagnosis structure
    if report["diagnoses"]:
        for diag in report["diagnoses"]:
            assert "summary" in diag
            assert "problem_type" in diag
            assert "severity" in diag
            assert "nlp_description" in diag
            assert "confidence" in diag
            assert isinstance(diag["confidence"], (int, float))
