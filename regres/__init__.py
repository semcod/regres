from .import_error_toon_report import main as import_error_toon_report_main
from . import regres
from . import refactor
from . import defscan
from . import doctor

try:
    from importlib.metadata import version as _get_version
except ImportError:
    from importlib_metadata import version as _get_version  # type: ignore[no-redef]

__version__ = _get_version("regres")

__all__ = [
    "import_error_toon_report_main",
    "regres",
    "refactor",
    "defscan",
    "doctor",
]
