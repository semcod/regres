# regres TODO

> **Note:** Zakończone zadania przeniesione do [CHANGELOG.md](CHANGELOG.md)

## Active backlog

### Detection (orchestrator)
- [ ] **`module_view_signature_mismatch`** — wykrywać klasy `*View extends BaseConnectView` które nie implementują `renderContainer()`/`loadCurrentPage()`/`_syncFromUrlInner()` (powoduje runtime `... is abstract` lub cichy brak renderingu).
- [ ] **`menu_container_missing`** — gdy `app.initializer` loguje `Sidebar menu container not found`, regres powinien identyfikować, którego selektora brakuje (`#sidebar-menu` itp.) i mapować do modułu, który jest aktywny.
- [ ] **Submodule mirror import resolver** — niektóre moduły (`connect-id`, `connect-manager`, `connect-scenario`) są symlink-ami do `<submodule>/frontend/src/modules/<name>`. Chain analysis powinna lepiej rozpoznawać tę topologię, żeby nie zgłaszać fałszywie nierozwiązanych importów.

### CLI / UX
- [ ] `--auto-apply-low-risk` — automatyczne stosowanie patch-y dla diagnoz z `confidence >= 0.95` i pojedynczą zmianą jednego pliku.
- [ ] `--watch` (lub TestQL integration) — pętla URL-probe → diagnoza → patch dla CI.
- [ ] Eksport diagnoz w formacie TOON dla `import-error-toon-report.md` (spójność z istniejącym narzędziem).

### Docs
- [ ] Workflow w README dla `--apply` (kiedy bezpieczne, kiedy wymagane review).
- [ ] Dodać sekcję "FAQ — false positives" z pattern-ami wykluczanymi przez `_filter_actionable_diagnoses`.

### Refactor
- [ ] `doctor_cli.py::_handle_url_mode` ma ~360 linii — wyodrębnić: `_run_chain_analysis`, `_run_vite_probe`, `_run_loader_compliance`.
- [ ] Pull `MODULE_PATH_MAP` do osobnego pliku konfiguracyjnego (YAML) — projekt-specific.

---

## Active Issues

nie działa:
 http://localhost:8100/connect-config-labels?font=default&theme=dark&role=admin&lang=pl&size=100
napraw z uzyciem paczki regres w celu analizy powiazan bilbiotek, z uwzglednieniem historii git 
i duplikatow nazw i zawartosci w systemie plikow:
 /home/tom/github/semcod/regres/README.md
sparwdz czy strona po przywroceniu, naprawie, ma komunikacje z backendem
jesli paczka regres nie działa poprawnie to ją popraw i reuzyj nowa wersje