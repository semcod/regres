#!/usr/bin/env python3
"""
doctor_config.py — runtime configuration for the regres ``doctor``.

Resolution order (lowest → highest priority):

1. **Hard-coded defaults** (this file).
2. **``<scan_root>/.regres/.env``** — simple ``KEY=VALUE`` file (one per line,
   ``#`` comments allowed, blank lines ignored).  This file is auto-created on
   first use so the user can edit values by hand without remembering names.
3. **Process environment variables** (e.g. exported in the shell).
4. **CLI flags** (``--history-window-days``, ``--history-max-iterations`` …).

All variables share the prefix ``REGRES_`` so they never clash with unrelated
environment state.

The config object is intentionally small — only knobs that operators actually
change.  Add more fields here when new tunables are introduced; the loader
will pick them up automatically as long as they are declared in
``CONFIG_FIELDS``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Field declarations
# ---------------------------------------------------------------------------

# Each entry: (env_var_name, dataclass_attr, default_value, parser, help_text).
# ``parser`` converts the raw string from .env / os.environ to the typed value.
CONFIG_FIELDS: List[Tuple[str, str, Any, Any, str]] = [
    (
        "REGRES_HISTORY_WINDOW_DAYS",
        "history_window_days",
        30,
        int,
        "How many days back regres scans git history for page-restore candidates.",
    ),
    (
        "REGRES_HISTORY_MAX_ITERATIONS",
        "history_max_iterations",
        30,
        int,
        "Maximum number of git commits regres inspects per page (cap).",
    ),
    (
        "REGRES_HISTORY_SHRINKAGE_FACTOR",
        "history_shrinkage_factor",
        0.5,
        float,
        "Current page must be < (factor * recent_max_lines) to flag regression.",
    ),
    (
        "REGRES_VITE_BASE",
        "vite_base",
        "",
        str,
        "Default Vite dev-server URL when --vite-base is not provided (e.g. http://localhost:8100).",
    ),
    (
        "REGRES_DEPENDENCY_CHAIN_DEPTH",
        "dependency_chain_depth",
        1,
        int,
        "BFS depth used by dependency-chain analysis (relative imports only).",
    ),
    (
        "REGRES_STRUCTURE_SNAPSHOT_MAX_ENTRIES",
        "structure_snapshot_max_entries",
        120,
        int,
        "Max files listed in the structure snapshot section of the markdown report.",
    ),
    (
        "REGRES_PRINT_BANNER",
        "print_banner",
        True,
        lambda s: str(s).strip().lower() not in ("0", "false", "no", "off"),
        "Print the startup banner showing the active scan window.",
    ),
]

ENV_FILE_RELATIVE = Path(".regres") / ".env"


# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------


@dataclass
class DoctorConfig:
    """Resolved runtime configuration for one ``doctor`` invocation."""

    # NOTE: keep field names in sync with CONFIG_FIELDS attr_name.
    history_window_days: int = 30
    history_max_iterations: int = 30
    history_shrinkage_factor: float = 0.5
    vite_base: str = ""
    dependency_chain_depth: int = 1
    structure_snapshot_max_entries: int = 120
    print_banner: bool = True

    # Bookkeeping (not user-settable directly)
    scan_root: Path = field(default_factory=Path.cwd)
    env_file_path: Optional[Path] = None
    env_file_existed: bool = False
    sources: Dict[str, str] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Pretty-print the active configuration as a startup banner.
    # ------------------------------------------------------------------
    def banner_lines(self) -> List[str]:
        """Return a list of lines describing the active scan window."""
        env_path = self.env_file_path or (self.scan_root / ENV_FILE_RELATIVE)
        existed = "exists" if self.env_file_existed else "auto-created"
        lines = [
            "regres doctor — active scan window:",
            f"  history window:     {self.history_window_days} days "
            f"(set REGRES_HISTORY_WINDOW_DAYS or pass --history-window-days N)",
            f"  history iterations: {self.history_max_iterations} commits "
            f"(set REGRES_HISTORY_MAX_ITERATIONS or pass --history-max-iterations N)",
            f"  shrinkage factor:   {self.history_shrinkage_factor} "
            "(REGRES_HISTORY_SHRINKAGE_FACTOR; flag regression when current_lines < factor * recent_max)",
            f"  dependency depth:   {self.dependency_chain_depth} "
            "(REGRES_DEPENDENCY_CHAIN_DEPTH)",
            f"  vite base:          {self.vite_base or '(none — pass --vite-base)'}",
            f"  config file:        {env_path}  ({existed})",
            "  edit values manually or run:  echo 'REGRES_HISTORY_WINDOW_DAYS=90' >> "
            f"{env_path}",
        ]
        return lines

    def print_banner_to(self, stream=None) -> None:
        if not self.print_banner:
            return
        import sys

        out = stream if stream is not None else sys.stderr
        for line in self.banner_lines():
            print(line, file=out)


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


def _parse_env_file(path: Path) -> Dict[str, str]:
    """Parse a ``KEY=VALUE`` file. Ignores blanks and ``#`` comments."""
    if not path.is_file():
        return {}
    out: Dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return out
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        # Strip surrounding quotes if present.
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        if key:
            out[key] = value
    return out


def _ensure_env_file(scan_root: Path) -> Tuple[Path, bool]:
    """Ensure ``<scan_root>/.regres/.env`` exists, return ``(path, existed_before)``."""
    env_path = scan_root / ENV_FILE_RELATIVE
    if env_path.is_file():
        return env_path, True
    try:
        env_path.parent.mkdir(parents=True, exist_ok=True)
        # Write a self-documenting template with all known keys.
        lines = [
            "# regres doctor — runtime configuration",
            "# This file is auto-created on first run. Edit values below or",
            "# override with shell exports / CLI flags. Each key documents itself.",
            "#",
        ]
        for env_name, _attr, default, _parser, help_text in CONFIG_FIELDS:
            lines.append(f"# {help_text}")
            lines.append(f"# {env_name}={default}")
            lines.append("")
        env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except OSError:
        # Read-only filesystem etc. — non-fatal, just skip.
        pass
    return env_path, False


def load_config(
    scan_root: Path,
    cli_overrides: Optional[Dict[str, Any]] = None,
) -> DoctorConfig:
    """Build a :class:`DoctorConfig` honoring the resolution order described in
    the module docstring.

    Args:
        scan_root: Project root (we look for ``.regres/.env`` there).
        cli_overrides: Mapping of dataclass-attribute → value from argparse.
            ``None`` values are ignored so missing flags fall through.
    """
    scan_root = scan_root.resolve()
    env_path, existed_before = _ensure_env_file(scan_root)
    file_values = _parse_env_file(env_path)

    cfg_kwargs: Dict[str, Any] = {}
    sources: Dict[str, str] = {}

    overrides = cli_overrides or {}
    for env_name, attr_name, default, parser, _help in CONFIG_FIELDS:
        # Priority chain: CLI > os.environ > .env file > default.
        cli_value = overrides.get(attr_name)
        if cli_value is not None and cli_value != "":
            cfg_kwargs[attr_name] = cli_value
            sources[attr_name] = "cli"
            continue
        env_value = os.environ.get(env_name)
        if env_value is not None and env_value != "":
            try:
                cfg_kwargs[attr_name] = parser(env_value)
                sources[attr_name] = "env"
                continue
            except (TypeError, ValueError):
                pass
        file_value = file_values.get(env_name)
        if file_value is not None and file_value != "":
            try:
                cfg_kwargs[attr_name] = parser(file_value)
                sources[attr_name] = "file"
                continue
            except (TypeError, ValueError):
                pass
        cfg_kwargs[attr_name] = default
        sources[attr_name] = "default"

    cfg_kwargs["scan_root"] = scan_root
    cfg_kwargs["env_file_path"] = env_path
    cfg_kwargs["env_file_existed"] = existed_before
    cfg_kwargs["sources"] = sources

    # Filter to the actual dataclass fields to be future-proof.
    valid_attrs = {f.name for f in fields(DoctorConfig)}
    cfg_kwargs = {k: v for k, v in cfg_kwargs.items() if k in valid_attrs}
    return DoctorConfig(**cfg_kwargs)


__all__ = ["DoctorConfig", "load_config", "CONFIG_FIELDS", "ENV_FILE_RELATIVE"]
