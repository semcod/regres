from __future__ import annotations

import runpy
from pathlib import Path


def main() -> int:
    script = Path(__file__).resolve().parent / "scripts" / "import-error-toon-report.py"
    runpy.run_path(str(script), run_name="__main__")
    return 0
