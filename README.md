# regres

Narzędzia do analizy regresji, refaktoryzacji i duplikatów kodu.

## Installation

```bash
pip install -e .
```

## Usage

Główny CLI `regres` obsługuje następujące komendy:

- `regres` — analiza regresji plików (historia, zmiany)
- `regres refactor` — analiza kodu przy refaktoryzacji (duplikaty, zależności, symbole)
- `regres defscan` — skaner duplikatów definicji klas, funkcji i modeli
- `regres doctor` — orchestrator analizy i generator akcji naprawczych
- `regres import-error-toon-report` — raport błędów importów TS w formacie Toon

### Examples

```bash
# Analiza regresji pliku
regres regres --file path/to/file.py

# Analiza kodu przy refaktoryzacji
regres refactor find encoder
regres refactor symbols encoder
regres refactor duplicates

# Skan duplikatów definicji
regres defscan
regres defscan --kind class --min-count 2

# Orchestrator analizy i generator akcji naprawczych
regres doctor --all
regres doctor --import-log .regres/import-error-toon-report.raw.log --out-md .regres/doctor-report.md

# Raport błędów importów TS
regres import-error-toon-report
```

## Documentation

- [REGRES](docs/REGRES.md) — analiza regresji plików
- [REFACTOR](docs/REFACTOR.md) — analiza kodu przy refaktoryzacji
- [DEFSCAN](docs/DEFSCAN.md) — skaner duplikatów definicji
- [DOCTOR](docs/DOCTOR.md) — orchestrator analizy i generator akcji naprawczych
- [import-error-toon-report](docs/import-error-toon-report.md) — raport błędów importów TS

## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.1.9-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$1.50-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-3.3h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $1.5000 (10 commits)
- 👤 **Human dev:** ~$325 (3.3h @ $100/h, 30min dedup)

Generated on 2026-04-28 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

## License

Licensed under Apache-2.0.
