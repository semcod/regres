# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.57] - 2026-05-01

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update docs/README.md
- Update project/README.md
- Update project/context.md

### Other
- Update app.doql.less
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- Update project/evolution.toon.yaml
- ... and 12 more files

## [0.1.56] - 2026-05-01

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md
- Update docs/DOCTOR.md
- Update docs/README.md
- Update project/README.md
- Update project/context.md

### Other
- Update app.doql.less
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- Update project/evolution.toon.yaml
- ... and 9 more files

## [0.1.55] - 2026-05-01

### Added
- **`--runtime-log` end-to-end** — doctor_cli + regres_cli forwarding dla diagnostyki runtime z logów konsoli
- **`runtime_icon_registry_miss` diagnosis** — wykrywa brakujące wpisy w rejestrze ikon na podstawie logów runtime (emoji-tokeny używane w UI bez definicji SVG)
- **Rozszerzone wzorce placeholderów** — dodano generic 'w trakcie migracji' do `PLACEHOLDER_TEXT_PATTERNS`
- Nowe workflows: `.windsurf/workflows/c2004-preanalysis-predeploy.md` i `.windsurf/workflows/c2004-security-settings-baseline.md`

### Fixed
- **`DoctorOrchestrator._extract_page_token`** — poprawione parsowanie nested routes (np. `connect-test/operator-workshop`), wcześniej zwracało `None`

### Test
- **109 testów przechodzi** — `test_doctor_orchestrator.py` + `test_doctor_cli.py`

### Docs
- Aktualizacja README.md, TODO.md, docs/DOCTOR.md o nowe funkcjonalności

## [0.1.54] - 2026-04-29

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update docs/README.md
- Update project/README.md
- Update project/context.md

### Test
- Update tests/test_doctor_cli.py
- Update tests/test_doctor_orchestrator.py

### Other
- Update app.doql.less
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- Update project/evolution.toon.yaml
- ... and 7 more files

## [0.1.53] - 2026-04-29

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update docs/README.md
- Update project/README.md
- Update project/context.md

### Other
- Update app.doql.less
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- Update project/evolution.toon.yaml
- ... and 9 more files

## [0.1.52] - 2026-04-29

### Docs
- Update README.md

### Test
- Update tests/test_doctor_orchestrator.py

### Other
- Update regres/doctor_orchestrator.py

## [0.1.51] - 2026-04-29

### Docs
- Update README.md

### Other
- Update regres/doctor_orchestrator.py

## [0.1.50] - 2026-04-29

### Docs
- Update .regres/connect-test-reports-doctor.md
- Update .windsurf/workflows/c2004-preanalysis-predeploy.md
- Update .windsurf/workflows/c2004-security-settings-baseline.md
- Update README.md

## [0.1.49] - 2026-04-29

### Docs
- Update README.md

### Test
- Update tests/test_doctor_cli.py
- Update tests/test_doctor_orchestrator.py

### Other
- Update regres/doctor_cli.py
- Update regres/doctor_orchestrator.py
- Update regres/regres_cli.py

## [0.1.48] - 2026-04-29

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update docs/README.md
- Update project/README.md
- Update project/context.md

### Other
- Update app.doql.less
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- Update project/evolution.toon.yaml
- ... and 9 more files

## [0.1.47] - 2026-04-29

### Docs
- Update README.md
- Update TODO.md

### Other
- Update regres/doctor_orchestrator.py

## [0.1.46] - 2026-04-28

### Docs
- Update README.md
- Update TODO.md

## [0.1.45] - 2026-04-28

### Docs
- Update README.md

### Other
- Update regres/doctor_cli.py

## [0.1.44] - 2026-04-28

### Docs
- Update README.md

### Test
- Update tests/test_doctor_config.py

### Other
- Update regres/version_check.py

## [0.1.43] - 2026-04-28

### Docs
- Update README.md

### Other
- Update regres/doctor_cli.py
- Update regres/doctor_orchestrator.py
- Update regres/regres_cli.py

## [0.1.42] - 2026-04-28

### Docs
- Update README.md

### Other
- Update regres/doctor_config.py
- Update regres/doctor_orchestrator.py

## [0.1.41] - 2026-04-28

### Docs
- Update README.md
- Update TODO.md

### Test
- Update tests/test_doctor_orchestrator.py

### Other
- Update regres/doctor_cli.py
- Update regres/doctor_orchestrator.py

## [0.1.40] - 2026-04-28

### Docs
- Update README.md

## [0.1.39] - 2026-04-28

### Docs
- Update CHANGELOG.md
- Update README.md
- Update TODO.md

### Test
- Update tests/test_doctor_orchestrator.py

### Other
- Update VERSION
- Update img.png
- Update regres/doctor_cli.py
- Update regres/doctor_orchestrator.py
- Update regres/regres_cli.py

## [0.1.38] - 2026-04-28

### Added
- **Module-loader compliance check** (`module_loader_no_class`): nowa metoda `DoctorOrchestrator.analyze_module_loader_compliance(module_path, module_name)` wykrywa pliki `<name>.module.ts`, które nie eksportują klasy `*Module` ani `default`. Bez nich host `frontend/src/modules/index.ts` rzuca runtime `No Module class found in ...`. Diagnoza generuje gotowy fragment kodu `extends BaseModule` do wklejenia (severity: critical, confidence: 0.95).
- **CLI integration**: `_handle_url_mode` w `doctor_cli.py` wywołuje `analyze_module_loader_compliance` po `analyze_page_implementations` i dodaje krok do planu z inputs/outputs/decision.
- **MODULE_PATH_MAP**: nowy wpis `connect-deleted → connect-deleted/frontend/src/modules/connect-deleted`.
- **Tests**: 4 nowe testy w `tests/test_doctor_orchestrator.py` pokrywają: pass-on-Module-class, pass-on-default-export, flag-on-view-only, no-entry-file (242 testy → wszystkie przechodzą).

### Changed
- README.md przepisany: sekcja "What's new (0.1.38)", workflow URL→naprawa, tabela `problem_type` z severity i metodą wykrycia.

## [0.1.37] - 2026-04-28

### Added (skumulowane 0.1.32–0.1.37)
- **Vite runtime probe** (`probe_vite_runtime`): GET pliku celu z dev-servera Vite, parsowanie 500 z embedded JSON i `Failed to resolve import "X" from "Y"`. CLI flag `--vite-base` (autoderywowane z `--url`). Łańcuchowe sondowanie: jeśli probe zwraca błąd, plik źródłowy `missing_import_from` jest dodawany do kolejki. Tworzy diagnozy `vite_runtime_failure` (critical) z komendami curl + recursive regres.
- **Dependency chain analysis** (`analyze_dependency_chain`): BFS po relatywnych importach pliku celu (depth=1) z resolverem rozszerzeń (`.ts`, `.tsx`, `/index.ts`, …). Każdy broken/stub link generuje diagnozę `import_resolution_failure` (high/medium) z gotową komendą regres do naprawy łańcuchowej.
- **Patch scripts z trybami `--preview` / `--diff` / `--apply`** + automatyczne przepisywanie ścieżek importów po przywróceniu pliku z innego głębokiego poziomu w drzewie.
- **Decision-tree workflow w raporcie**: README, plan kroków z `inputs`/`outputs`/`decision`, snapshot struktury (`collect_structure_snapshot`), kolumna "decision" w renderingu Markdown.
- **History-based candidates**: `_collect_page_history_candidates` zwraca kandydatów z historii git w oknie 2 dni LUB 10 iteracji (zależnie co większe), z wykryciem `HISTORY_SHRINKAGE_FACTOR=0.5` (current < 50% recent max).

### Other
- Update VERSION, regres/doctor_cli.py, regres/doctor_orchestrator.py

## [0.1.30] - 2026-04-28

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update docs/README.md
- Update project/README.md
- Update project/context.md

### Other
- Update VERSION
- Update app.doql.less
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- ... and 9 more files

## [0.1.27] - 2026-04-28

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update docs/README.md
- Update project/README.md
- Update project/context.md

### Other
- Update app.doql.less
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- Update project/evolution.toon.yaml
- ... and 8 more files

## [0.1.26] - 2026-04-28

### Docs
- Update README.md

### Other
- Update regres/doctor_orchestrator.py

## [0.1.25] - 2026-04-28

### Docs
- Update README.md

### Test
- Update tests/test_doctor_e2e.py

### Other
- Update VERSION
- Update regres/doctor_orchestrator.py

## [0.1.23] - 2026-04-28

### Docs
- Update README.md

### Other
- Update VERSION
- Update regres/doctor_cli.py

## [0.1.21] - 2026-04-28

### Docs
- Update README.md

### Other
- Update regres/doctor_orchestrator.py

## [0.1.20] - 2026-04-28

### Docs
- Update README.md

## [0.1.19] - 2026-04-28

### Docs
- Update README.md

### Other
- Update regres/doctor_orchestrator.py

## [0.1.18] - 2026-04-28

### Docs
- Update README.md
- Update TODO.md

### Other
- Update regres/doctor_cli.py
- Update regres/doctor_orchestrator.py

## [0.1.17] - 2026-04-28

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update docs/README.md
- Update project/README.md
- Update project/context.md

### Other
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- Update project/evolution.toon.yaml
- Update project/flow.mmd
- ... and 7 more files

## [0.1.16] - 2026-04-28

### Docs
- Update README.md

### Other
- Update regres/defscan.py

## [0.1.15] - 2026-04-28

### Docs
- Update README.md

### Other
- Update regres/regres_cli.py

## [0.1.14] - 2026-04-28

### Docs
- Update README.md

### Other
- Update regres/doctor_cli.py
- Update regres/import_error_toon_report.py

## [0.1.13] - 2026-04-28

### Docs
- Update README.md

### Other
- Update regres/__init__.py
- Update regres/regres_cli.py
- Update regres/version_check.py

## [0.1.12] - 2026-04-28

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update docs/README.md
- Update project/README.md
- Update project/context.md

### Test
- Update tests/test_doctor_cli.py
- Update tests/test_doctor_models.py
- Update tests/test_doctor_orchestrator.py

### Other
- Update app.doql.less
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- Update project/evolution.toon.yaml
- ... and 9 more files

## [0.1.11] - 2026-04-28

### Docs
- Update README.md

### Other
- Update regres/refactor.py

## [0.1.10] - 2026-04-28

### Docs
- Update README.md

### Other
- Update regres/defscan.py

## [0.1.9] - 2026-04-28

### Docs
- Update README.md

### Other
- Update regres/defscan.py
- Update regres/doctor_orchestrator.py
- Update regres/refactor.py

## [0.1.8] - 2026-04-28

### Docs
- Update README.md

### Test
- Update tests/test_doctor_cli.py

## [0.1.7] - 2026-04-28

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update docs/README.md
- Update project/README.md
- Update project/context.md

### Test
- Update tests/test_defscan.py
- Update tests/test_doctor.py
- Update tests/test_import_error_toon_report.py
- Update tests/test_refactor.py
- Update tests/test_regres_core.py

### Other
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- Update project/evolution.toon.yaml
- Update project/flow.mmd
- ... and 11 more files

## [0.1.6] - 2026-04-28

### Docs
- Update README.md

### Other
- Update regres/doctor.py
- Update regres/import_error_toon_report.py
- Update regres/regres_cli.py

## [0.1.5] - 2026-04-28

### Docs
- Update README.md

### Test
- Update tests/test_regres.py

## [0.1.4] - 2026-04-28

### Docs
- Update README.md
- Update regres/DEFSCAN.md
- Update regres/REFACTOR.md
- Update regres/REGRES.md

### Test
- Update tests/test_regres.py

### Other
- Update regres/doctor.py
- Update regres/regres_cli.py

## [0.1.3] - 2026-04-28

### Docs
- Update README.md
- Update docs/DEFSCAN.md
- Update docs/DOCTOR.md
- Update docs/REFACTOR.md
- Update docs/REGRES.md

### Test
- Update tests/test_regres.py

### Other
- Update regres/__init__.py
- Update regres/defscan.py
- Update regres/doctor.py
- Update regres/refactor.py
- Update regres/regres.py
- Update regres_cli.py

## [0.1.2] - 2026-04-28

### Docs
- Update README.md

### Other
- Update regres/__init__.py
- Update regres/import_error_toon_report.py
- Update regres_cli.py
- Update scripts/import-error-toon-report.py

## [0.1.1] - 2026-04-28

### Docs
- Update .regres/import-error-toon-report.md
- Update DEFSCAN.md
- Update README.md
- Update REFACTOR.md
- Update REGRES.md
- Update docs/import-error-toon-report.md

### Test
- Update tests/test_regres.py

### Other
- Update .gitignore
- Update Makefile
- Update VERSION
- Update defscan.py
- Update project.sh
- Update refactor.py
- Update regres.py
- Update regres_cli.py
- Update scripts/import-error-toon-report.py
- Update tree.sh

