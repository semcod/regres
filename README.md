# regres
![img.png](img.png)

Narzędzia do analizy regresji, refaktoryzacji i duplikatów kodu — z naciskiem na **autonomiczne wykrywanie regresji frontendu** (placeholder pages, broken imports, runtime 500 z Vite, niezgodność konwencji loadera modułów) i generowanie skryptów naprawczych z trybami `--preview` / `--diff` / `--apply`.

## Installation

```bash
pip install -e .
```

## What's new (0.1.55)

- **`--runtime-log` end-to-end** — doctor_cli + regres_cli forwarding dla diagnostyki runtime z logów konsoli (np. `[IconComponent] SVG icon not found`).
- **`runtime_icon_registry_miss` diagnosis** — wykrywa brakujące wpisy w rejestrze ikon na podstawie logów runtime (emoji-tokeny używane w UI bez definicji SVG).
- **Fixed `DoctorOrchestrator._extract_page_token`** — poprawione parsowanie nested routes (np. `connect-test/operator-workshop`), wcześniej zwracało `None`.
- **Rozszerzone wzorce placeholderów** — dodano generic 'w trakcie migracji' do `PLACEHOLDER_TEXT_PATTERNS`.
- **Page-registry compliance check** (`page_registry_default_missing`) — parsuje `<module>/pages-index.ts`, weryfikuje że `defaultPage` istnieje w rejestrze stron (z pominięciem zakomentowanych wpisów). Brak → krytyczna diagnoza z gotową instrukcją naprawy.
- **Module-loader compliance check** (`module_loader_no_class`) — wykrywa pliki `<name>.module.ts`, które nie eksportują klasy `*Module` ani `default`.
- **Vite runtime probe** (`--vite-base`, autoderywowane z `--url`) — pobiera plik celu z dev-servera Vite i parsuje błędy 500.
- **Dependency chain analysis** — BFS po relatywnych importach pliku celu (depth=1); zaznacza `BROKEN`/`STUB`.
- **Decision-tree workflow w raporcie** — ścieżka decyzyjna, snapshot struktury, plan kroków.
- **Patch scripts z `--preview` / `--diff` / `--apply`** + automatyczne przepisywanie ścieżek importów.
- Nowe workflows: `.windsurf/workflows/c2004-preanalysis-predeploy.md` i `.windsurf/workflows/c2004-security-settings-baseline.md`.

### What's new (0.1.40-0.1.45)

- **`DoctorConfig` + `.regres/.env` loader** — 4-tier priority chain: CLI > os.environ > .regres/.env > defaults.
- **Startup banner** — pokazuje aktywne okno analizy (history days, max iterations, shrinkage factor, vite base).
- **Nowe flagi CLI**: `--history-window-days`, `--history-max-iterations`, `--history-shrinkage-factor`, `--no-banner`.
- **Defaults bumped**: `HISTORY_DEFAULT_DAYS` 2→30, `HISTORY_DEFAULT_ITERATIONS` 10→30.
- Mapping `connect-deleted` w `MODULE_PATH_MAP`.

## Usage

Główny CLI `regres` obsługuje następujące komendy:

- `regres` — analiza regresji plików (historia, zmiany)
- `regres refactor` — analiza kodu przy refaktoryzacji (duplikaty, zależności, symbole)
- `regres defscan` — skaner duplikatów definicji klas, funkcji i modeli
- `regres doctor` — orchestrator analizy i generator akcji naprawczych (z trybem URL)
- `regres import-error-toon-report` — raport błędów importów TS w formacie Toon

### Doctor — typowy workflow URL → naprawa

```bash
# 1) Analiza konkretnej strony, która nie wyświetla się poprawnie:
regres doctor \
  --scan-root /path/to/repo \
  --url 'http://localhost:8100/connect-config-sitemap?...' \
  --all --git-history \
  --vite-base http://localhost:8100 \
  --out-md .regres/sitemap-doctor.md

# Raport zawiera:
#   - Plan kroków (decision-tree) z inputs/outputs/decision per krok
#   - Page implementation analysis (placeholder/stub detection)
#   - Module loader compliance (czy <name>.module.ts spełnia kontrakt loadera)
#   - Dependency chain (broken/stub linki w importach celu)
#   - Vite runtime probe (autorytatywny status 200/500 + missing import)
#   - Patch scripts z preview/diff/apply per kandydat z historii git

# 2) Każdy "broken link" w raporcie zawiera gotową komendę regres
#    dla pliku, który zgłosił błąd — wystarczy ją skopiować i uruchomić,
#    aby kontynuować naprawę łańcuchową.

# 3) Po wybraniu kandydata uruchom patch script:
bash .regres/patches/<page-token>/restore-<hash>.sh --preview   # podgląd
bash .regres/patches/<page-token>/restore-<hash>.sh --diff      # diff
bash .regres/patches/<page-token>/restore-<hash>.sh --apply     # zapis
```

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
regres doctor --url http://localhost:8100/connect-deleted --vite-base http://localhost:8100

# Raport błędów importów TS
regres import-error-toon-report
```

## Diagnozy `doctor` — typy

| `problem_type`               | Severity   | Wykrycie |
|-----------------------------|------------|----------|
| `page_content_regression`   | high       | git history pokazuje znacznie większą poprzednią wersję pliku |
| `placeholder_page`          | high       | tekst pasuje do `PLACEHOLDER_TEXT_PATTERNS` (w tym 'w trakcie migracji') |
| `import_resolution_failure` | high/medium| BFS po relatywnych importach — nie rozwiązany / placeholder |
| `vite_runtime_failure`      | critical   | HTTP probe Vite zwraca 500 z `Failed to resolve import` |
| `module_loader_no_class`    | critical   | `<name>.module.ts` bez `*Module` / `export default` |
| `page_registry_default_missing` | critical | `pages-index.ts` ma `defaultPage` nieobecny w rejestrze → ryzyko nieskończonej rekurencji w `BasePageManager` |
| `runtime_icon_registry_miss`| medium/high| Logi runtime z `[IconComponent] SVG icon not found: <emoji>` — brak definicji ikony w rejestrze |
| `module_not_found`          | medium     | URL prefix bez modułu w `MODULE_PATH_MAP` (obsługa nested routes: `connect-test/operator-workshop`) |
| `import_error`              | medium     | TS2307/TS2305 z logu kompilatora |

## Documentation

- [REGRES](docs/REGRES.md) — analiza regresji plików
- [REFACTOR](docs/REFACTOR.md) — analiza kodu przy refaktoryzacji
- [DEFSCAN](docs/DEFSCAN.md) — skaner duplikatów definicji
- [DOCTOR](docs/DOCTOR.md) — orchestrator analizy i generator akcji naprawczych
- [import-error-toon-report](docs/import-error-toon-report.md) — raport błędów importów TS

## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.1.56-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$7.50-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-12.2h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $7.5000 (53 commits)
- 👤 **Human dev:** ~$1215 (12.2h @ $100/h, 30min dedup)

Generated on 2026-05-01 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

## License

Licensed under Apache-2.0.
