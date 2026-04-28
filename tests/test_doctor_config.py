"""Regression tests for ``regres.doctor_config``."""

from __future__ import annotations

import io
import os
from pathlib import Path

import pytest

from regres.doctor_config import (
    CONFIG_FIELDS,
    DoctorConfig,
    ENV_FILE_RELATIVE,
    load_config,
)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


def _clear_regres_env(monkeypatch):
    """Strip any REGRES_* variables from os.environ so each test is isolated."""
    for env_name, _attr, _default, _parser, _help in CONFIG_FIELDS:
        monkeypatch.delenv(env_name, raising=False)


# --------------------------------------------------------------------------
# Default behavior + auto-creation
# --------------------------------------------------------------------------


def test_load_config_uses_defaults_and_creates_env_file(tmp_path: Path, monkeypatch):
    _clear_regres_env(monkeypatch)
    cfg = load_config(tmp_path)
    # Defaults declared in CONFIG_FIELDS must be honored.
    assert cfg.history_window_days == 30
    assert cfg.history_max_iterations == 30
    assert cfg.history_shrinkage_factor == 0.5
    assert cfg.dependency_chain_depth == 1
    assert cfg.print_banner is True
    # And the .env file is auto-created with self-documenting comments.
    env_path = tmp_path / ENV_FILE_RELATIVE
    assert env_path.is_file()
    text = env_path.read_text(encoding="utf-8")
    assert "REGRES_HISTORY_WINDOW_DAYS" in text
    assert cfg.env_file_existed is False
    assert cfg.sources["history_window_days"] == "default"


# --------------------------------------------------------------------------
# .env -> os.environ -> CLI priority chain
# --------------------------------------------------------------------------


def test_load_config_priority_env_file_over_default(tmp_path: Path, monkeypatch):
    _clear_regres_env(monkeypatch)
    env_path = tmp_path / ".regres" / ".env"
    env_path.parent.mkdir(parents=True)
    env_path.write_text(
        "# user override\nREGRES_HISTORY_WINDOW_DAYS=90\n",
        encoding="utf-8",
    )
    cfg = load_config(tmp_path)
    assert cfg.history_window_days == 90
    assert cfg.sources["history_window_days"] == "file"
    assert cfg.env_file_existed is True


def test_load_config_priority_environ_over_file(tmp_path: Path, monkeypatch):
    _clear_regres_env(monkeypatch)
    env_path = tmp_path / ".regres" / ".env"
    env_path.parent.mkdir(parents=True)
    env_path.write_text("REGRES_HISTORY_WINDOW_DAYS=90\n", encoding="utf-8")
    monkeypatch.setenv("REGRES_HISTORY_WINDOW_DAYS", "180")
    cfg = load_config(tmp_path)
    assert cfg.history_window_days == 180
    assert cfg.sources["history_window_days"] == "env"


def test_load_config_priority_cli_overrides_environ(tmp_path: Path, monkeypatch):
    _clear_regres_env(monkeypatch)
    monkeypatch.setenv("REGRES_HISTORY_WINDOW_DAYS", "180")
    cfg = load_config(tmp_path, cli_overrides={"history_window_days": 7})
    assert cfg.history_window_days == 7
    assert cfg.sources["history_window_days"] == "cli"


# --------------------------------------------------------------------------
# Bad values -> graceful fallback
# --------------------------------------------------------------------------


def test_load_config_invalid_int_falls_back_to_default(tmp_path: Path, monkeypatch):
    _clear_regres_env(monkeypatch)
    monkeypatch.setenv("REGRES_HISTORY_WINDOW_DAYS", "not-a-number")
    cfg = load_config(tmp_path)
    assert cfg.history_window_days == 30
    assert cfg.sources["history_window_days"] == "default"


# --------------------------------------------------------------------------
# Boolean parsing for print_banner
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw,expected",
    [("0", False), ("false", False), ("FALSE", False), ("no", False), ("off", False),
     ("1", True), ("true", True), ("yes", True)],
)
def test_load_config_print_banner_parsing(tmp_path: Path, monkeypatch, raw, expected):
    _clear_regres_env(monkeypatch)
    monkeypatch.setenv("REGRES_PRINT_BANNER", raw)
    cfg = load_config(tmp_path)
    assert cfg.print_banner is expected


# --------------------------------------------------------------------------
# Banner output
# --------------------------------------------------------------------------


def test_banner_output_mentions_active_window_and_help(tmp_path: Path, monkeypatch):
    _clear_regres_env(monkeypatch)
    cfg = load_config(tmp_path, cli_overrides={"history_window_days": 14})
    buf = io.StringIO()
    cfg.print_banner_to(stream=buf)
    out = buf.getvalue()
    assert "active scan window" in out
    assert "14 days" in out  # cli override visible
    assert "REGRES_HISTORY_WINDOW_DAYS" in out
    assert "--history-window-days" in out


def test_banner_disabled_emits_nothing(tmp_path: Path, monkeypatch):
    _clear_regres_env(monkeypatch)
    cfg = load_config(tmp_path, cli_overrides={"print_banner": False})
    buf = io.StringIO()
    cfg.print_banner_to(stream=buf)
    assert buf.getvalue() == ""
