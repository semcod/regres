# regres TODO

## Done (0.1.45)
- [x] **`DoctorConfig` + `.regres/.env` loader** (`regres/doctor_config.py`) z 4-tier priority chain: CLI > os.environ > .regres/.env > defaults. Plik `.env` auto-tworzony z self-documenting komentarzami.
- [x] **Startup banner** drukowany na stderr przed każdą analizą — pokazuje aktywne okno (history days, max iterations, shrinkage factor, vite base, config file path) + dokładny env-var name i flagę CLI dla każdej wartości.
- [x] **Nowe flagi CLI**: `--history-window-days`, `--history-max-iterations`, `--history-shrinkage-factor`, `--no-banner` (z env-var counterparts `REGRES_*`). Flagi zarejestrowane w obu parserach (`doctor_cli.py` + `regres_cli.py`).
- [x] **Defaults bumped**: `HISTORY_DEFAULT_DAYS` 2→30, `HISTORY_DEFAULT_ITERATIONS` 10→30. Plan-step inputs w raporcie używają teraz `doctor.config.*` zamiast hardcoded constants.
- [x] **`version_check._write_env` rewrite** — zachowuje komentarze i nieznane klucze (poprzednio nukował szablon).
- [x] **Bug fix**: `--vite-base` był zarejestrowany w `regres_cli.py` ale nie forwardowany przez `_build_doctor_argv` → naprawione.
- [x] URL → moduł → ścieżka decyzyjna → raport → patch script (preview/diff/apply)
- [x] Vite runtime probe + parsowanie `Failed to resolve import` (chained)
- [x] Dependency chain analysis (BFS, depth=1) z gotowymi komendami chained-regres
- [x] Patch script auto-rewrite ścieżek importów po przywróceniu pliku
- [x] **Module-loader compliance check** (`module_loader_no_class`) — wykrywa `<name>.module.ts` bez `*Module`/`default`, generuje gotowy snippet `BaseModule`
- [x] **Page-registry compliance check** (`page_registry_default_missing`) — wykrywa `pages-index.ts` z `defaultPage` nieobecnym w rejestrze stron (root cause infinite recursion w `BasePageManager.loadPageByKey`)
- [x] Mapping `connect-deleted` w `MODULE_PATH_MAP`
- [x] **261/261 testy przechodzą** (15 nowych w `test_doctor_config.py` pokrywa: defaults, auto-creation, priority chain, invalid-value fallback, boolean parsing, banner output, banner suppression).

## Active backlog

### Detection (orchestrator)
- [ ] **`module_view_signature_mismatch`** — wykrywać klasy `*View extends BaseConnectView` które nie implementują `renderContainer()`/`loadCurrentPage()`/`_syncFromUrlInner()` (powoduje runtime `... is abstract` lub cichy brak renderingu).
- [ ] **`menu_container_missing`** — gdy `app.initializer` loguje `Sidebar menu container not found`, regres powinien identyfikować, którego selektora brakuje (`#sidebar-menu` itp.) i mapować do modułu, który jest aktywny.
- [ ] **Icon registry gap** (`[IconComponent] SVG icon not found: 🔐`) — wykrywać emoji-tokeny używane w UI bez wpisu w `SVG_DEFINITIONS` / API icons.
- [ ] **Submodule mirror import resolver** — niektóre moduły (`connect-id`, `connect-manager`, `connect-scenario`) są symlink-ami do `<submodule>/frontend/src/modules/<name>`. Chain analysis powinna lepiej rozpoznawać tę topologię, żeby nie zgłaszać fałszywie nierozwiązanych importów.

### CLI / UX
- [ ] `--auto-apply-low-risk` — automatyczne stosowanie patch-y dla diagnoz z `confidence >= 0.95` i pojedynczą zmianą jednego pliku.
- [ ] `--watch` (lub TestQL integration) — pętla URL-probe → diagnoza → patch dla CI.
- [ ] Eksport diagnoz w formacie TOON dla `import-error-toon-report.md` (spójność z istniejącym narzędziem).

### Docs
- [ ] Rozszerzyć `docs/DOCTOR.md` o pełny opis nowych typów diagnoz (`vite_runtime_failure`, `module_loader_no_class`, `import_resolution_failure`).
- [ ] Workflow w README dla `--apply` (kiedy bezpieczne, kiedy wymagane review).
- [ ] Dodać sekcję "FAQ — false positives" z pattern-ami wykluczanymi przez `_filter_actionable_diagnoses`.

### Refactor
- [ ] `doctor_cli.py::_handle_url_mode` ma ~360 linii — wyodrębnić: `_run_chain_analysis`, `_run_vite_probe`, `_run_loader_compliance`.
- [ ] Pull `MODULE_PATH_MAP` do osobnego pliku konfiguracyjnego (YAML) — projekt-specific.