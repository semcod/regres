"""Version checking against PyPI with caching and user preference storage."""

from __future__ import annotations

import json
import sys
import time
import urllib.request
from pathlib import Path

PYPI_URL = "https://pypi.org/pypi/regres/json"
CACHE_TTL_SECONDS = 3600  # 1 hour between checks
ENV_FILENAME = ".regres/.env"


def _find_env_path() -> Path:
    """Walk up from cwd looking for .regres/.env, default to cwd/.regres/.env."""
    cwd = Path.cwd().resolve()
    for path in [cwd] + list(cwd.parents):
        env = path / ENV_FILENAME
        if env.exists():
            return env
    return cwd / ENV_FILENAME


def _read_env() -> dict[str, str]:
    env_path = _find_env_path()
    if not env_path.exists():
        return {}
    result: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, val = line.split("=", 1)
            result[key.strip()] = val.strip()
    return result


def _write_env(data: dict[str, str]) -> None:
    env_path = _find_env_path()
    env_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{k}={v}" for k, v in data.items()]
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _get_pypi_version() -> str | None:
    try:
        req = urllib.request.Request(
            PYPI_URL,
            headers={
                "Accept": "application/json",
                "User-Agent": "regres-version-check",
            },
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return str(data["info"]["version"])
    except Exception:
        return None


def _parse_version(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in v.split(".") if x.isdigit())


def _is_newer(remote: str, local: str) -> bool:
    return _parse_version(remote) > _parse_version(local)


def _should_check() -> bool:
    env = _read_env()
    if env.get("REGRES_SKIP_VERSION_CHECK") == "1":
        return False
    last_check = env.get("REGRES_LAST_VERSION_CHECK")
    if last_check:
        try:
            last = int(last_check)
            if time.time() - last < CACHE_TTL_SECONDS:
                return False
        except ValueError:
            pass
    return True


def _save_last_check() -> None:
    env = _read_env()
    env["REGRES_LAST_VERSION_CHECK"] = str(int(time.time()))
    _write_env(env)


def _save_skip_preference() -> None:
    env = _read_env()
    env["REGRES_SKIP_VERSION_CHECK"] = "1"
    _write_env(env)


def check_version(local_version: str) -> None:
    """Check PyPI for a newer version and prompt the user to update.

    - Caches the check for CACHE_TTL_SECONDS.
    - Respects REGRES_SKIP_VERSION_CHECK=1 in .regres/.env.
    - In interactive TTY, asks if the user wants to update now.
    - If the user declines, saves the skip preference to .regres/.env.
    """
    if not _should_check():
        return

    remote = _get_pypi_version()
    _save_last_check()

    if remote is None:
        return

    if _is_newer(remote, local_version):
        print(
            f"⚠️  Nowa wersja regres dostępna: v{remote} (masz v{local_version})",
            file=sys.stderr,
        )
        print(
            f"   Zaktualizuj: pip install -U regres",
            file=sys.stderr,
        )

        if sys.stdin.isatty():
            print("   Czy chcesz zaktualizować teraz? [t/N]: ", end="", flush=True)
            try:
                answer = input().strip().lower()
                if answer in ("t", "tak", "y", "yes"):
                    import subprocess

                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", "-U", "regres"],
                        check=False,
                    )
                else:
                    _save_skip_preference()
                    print(
                        "   Pominięto. Aby ponownie sprawdzać, usuń "
                        "REGRES_SKIP_VERSION_CHECK z .regres/.env",
                        file=sys.stderr,
                    )
            except (EOFError, KeyboardInterrupt):
                _save_skip_preference()
                print(file=sys.stderr)
                print(
                    "   Pominięto (przerwane). Aby ponownie sprawdzać, usuń "
                    "REGRES_SKIP_VERSION_CHECK z .regres/.env",
                    file=sys.stderr,
                )
