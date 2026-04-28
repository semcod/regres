"""Tests for doctor_cli module."""
import argparse
from pathlib import Path
from regres.doctor_cli import _build_parser, _refresh_import_error_log

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

def test_refresh_import_no_frontend():
    result = _refresh_import_error_log(Path("/tmp"), Path("/tmp/log"))
    assert result is False
