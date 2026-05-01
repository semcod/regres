# DOCTOR — Orchestrator Analizy i Generator Akcji Naprawczych

`doctor` to orchestrator analizy regresji, który na bazie wyników z innych narzędzi (`regres`, `refactor`, `defscan`, `import-error-toon-report`) wyciąga wnioski i generuje konkretne akcje naprawcze w formie NLP opisów oraz poleceń shell.

## Funkcjonalności

Doctor analizuje wyniki z różnych narzędzi i:

1. **Wyciąga wnioski** o naturze problemów (błędy importów, duplikaty, regresje)
2. **Generuje NLP opisy** zrozumiałe dla człowieka
3. **Tworzy polecenia shell** do automatycznej naprawy
4. **Sugeruje akcje na plikach** (move, copy, delete, modify, create)
5. **Ocenia pewność** (confidence) każdej diagnozy
6. **Buduje automatyczny plan decyzyjny** na bazie parametrów CLI
7. **Generuje raport wykonawczy krok po kroku** (manual + LLM-ready)

## Automatyczny silnik decyzyjny (parameter-driven)

Doctor podejmuje kolejność działań na podstawie przekazanych parametrów.

### Domyślna strategia dla `--all`

1. `defscan` pre-scan (duplikaty / kandydaci do konsolidacji)
2. `refactor` pre-scan (wrappery / problemy strukturalne)
3. odświeżenie logu importów TS (`import-error-toon-report`)
4. analiza importów (`TS2307/TS2305`)
5. faza "regres" (historia git plików dotkniętych błędami)
6. synteza planu i wstępnych propozycji refaktoryzacji

### Dostosowanie do parametrów

- `--import-log` → analiza importów z podanego logu (bez wymuszonego refresh)
- `--defscan-report` / `--defscan-scan` → dołączenie dodatkowych wyników defscan
- `--refactor-scan` → dołączenie dodatkowych wyników refactor
- `--url --llm` → raport modułowy z sekcjami kontekstowymi + playbook
- `--runtime-log` → analiza logów runtime (np. brakujące ikony w rejestrze SVG)

## Użycie

### Podstawowe użycie

```bash
# Analiza błędów importów z domyślnego logu
regres doctor --import-log .regres/import-error-toon-report.raw.log

# Analiza duplikatów z raportu defscan
regres doctor --defscan-report defscan-report.json

# Pełna analiza (wszystkie dostępne dane)
regres doctor --all --scan-root .
```

### Zapisywanie raportów

```bash
# Zapisz raport Markdown
regres doctor --all --out-md .regres/doctor-report.md

# Zapisz raport JSON
regres doctor --all --out-json .regres/doctor-report.json
```

## Struktura diagnozy

Każda diagnoza zawiera:

- **summary** — krótki podsumowanie problemu
- **problem_type** — typ problemu (import_error, duplicate, regression, vite_runtime_failure, module_loader_no_class, page_registry_default_missing, runtime_icon_registry_miss, placeholder_page)
- **severity** — poziom ważności (low, medium, high, critical)
- **nlp_description** — szczegółowy opis w języku naturalnym
- **file_actions** — lista akcji na plikach
- **shell_commands** — lista poleceń shell do wykonania
- **confidence** — pewność diagnozy (0.0 - 1.0)

Dodatkowo raport zawiera metadane orkiestracji:

- **analysis_plan** — sekwencja kroków podjętych przez silnik decyzyjny
- **analysis_context** — kontekst (snapshot struktury, propozycje refaktoryzacji)

## Sekcje raportu Markdown (nowy format)

Raport Markdown generowany przez `doctor` zawiera teraz:

1. **Decision Workflow** — uzasadniona kolejność kroków + komendy
2. **Project Structure Snapshot** — szybki obraz struktury TS
3. **Preliminary Refactor Proposals** — wstępne propozycje refaktoryzacji
4. **Diagnoses** — klasyczne diagnozy (`severity`, `confidence`, `actions`)
5. **Step-by-Step Repair Playbook** — instrukcja wykonawcza 1..N

### Step-by-Step Repair Playbook

Każdy krok zawiera trzy codeblocki:

1. `Analyze` (`bash`) — komendy rozpoznawcze
2. `Apply changes` (`diff`) — szablon patcha (LLM/manual)
3. `Validate` (`bash`) — komendy walidacyjne po zmianie

To pozwala wykonywać naprawy zarówno ręcznie, jak i przez LLM w trybie iteracyjnym.

## Przykładowy raport

```markdown
# Doctor Report

**Scan Root:** `/home/tom/project`
**Diagnoses:** 2

## 🟠 1. Błędy importów in frontend/src/components/Button.tsx
**Type:** import_error | **Severity:** high | **Confidence:** 80%

**Description:** W pliku frontend/src/components/Button.tsx wykryto błędy importów dla modułów: @c2004/ui-kit. Należy sprawdzić konfigurację ścieżek w tsconfig.json oraz upewnić się, że wszystkie wymagane moduły są dostępne w monorepo.

### File Actions
```
modify: frontend/src/components/Button.tsx
  (Zmień import @c2004/ui-kit na poprawną ścieżkę)
```

### Shell Commands
```bash
# Manualna korekta importu @c2004/ui-kit
# Przejrzyj frontend/src/components/Button.tsx i popraw import @c2004/ui-kit
```

## 🟡 2. Duplikat definicji 'ButtonProps' (3 wystąpienia)
**Type:** duplicate | **Severity:** medium | **Confidence:** 90%

**Description:** Wykryto 3 duplikaty definicji 'ButtonProps'. Należy skonsolidować definicje w jednym miejscu, najlepiej w pakiecie shared, i usunąć pozostałe kopie.

### File Actions
```
delete: frontend/src/components/Button.tsx
  -> packages/ui-kit/src/types.ts
  (Duplikat ButtonProps - zachowaj tylko w packages/ui-kit/src/types.ts)
```

### Shell Commands
```bash
# Usuń duplikat ButtonProps
rm frontend/src/components/Button.tsx
```
```

## Integracja z innymi narzędziami

Doctor może analizować wyniki z:

1. **import-error-toon-report** — błędy importów TypeScript
2. **defscan** — duplikaty definicji klas, funkcji, modeli
3. **regres** — analiza regresji plików i historii zmian
4. **refactor** — analiza kodu przy refaktoryzacji

## Przykłady workflow

### Workflow 1: Naprawa błędów importów

```bash
# 1. Generuj log błędów TS
npm run typecheck > .regres/import-error-toon-report.raw.log

# 2. Uruchom doctor
regres doctor --import-log .regres/import-error-toon-report.raw.log --out-md .regres/doctor-report.md

# 3. Przejrzyj raport i wykonaj sugerowane akcje
```

### Workflow 2: Pełna analiza projektu

```bash
# 1. Uruchom wszystkie narzędzia
regres import-error-toon-report
regres defscan --kind class --min-count 2 --json .regres/defscan-report.json

# 2. Uruchom doctor z wszystkimi danymi
regres doctor --all --scan-root . --out-md .regres/doctor-report.md

# 3. Wykonuj kroki z sekcji "Step-by-Step Repair Playbook"
#    (Analyze -> Apply changes -> Validate)
```

### Workflow 3: Analiza logów runtime (brakujące ikony)

```bash
# Analiza logów runtime z wykrywaniem brakujących ikon w rejestrze
regres doctor --runtime-log .regres/runtime.log --scan-root . --out-md .regres/runtime-report.md

# Połączona analiza URL + runtime log
regres doctor --url http://localhost:8100/connect-config-labels \
  --runtime-log .regres/runtime.log \
  --scan-root . \
  --out-md .regres/combined-report.md
```

### Obsługa nested routes

Doctor obsługuje parsowanie zagnieżdżonych ścieżek URL (np. `connect-test/operator-workshop`):

```bash
# Dla URL z nested route, doctor poprawnie wyciąga page token
regres doctor --url http://localhost:8100/connect-test/operator-workshop \
  --scan-root . \
  --all --git-history \
  --out-md .regres/operator-workshop-report.md
```

## Rozszerzalność

Doctor jest zaprojektowany jako rozszerzalny orchestrator. Możesz dodawać nowe analizatory:

```python
class DoctorOrchestrator:
    def analyze_custom_metric(self, data_path: Path) -> List[Diagnosis]:
        # Twoja własna analiza
        diagnoses = []
        # ... logika analizy
        return diagnoses
```

## Przyszłe rozszerzenia

- [ ] **`module_view_signature_mismatch`** — wykrywać klasy `*View extends BaseConnectView` które nie implementują `renderContainer()`/`loadCurrentPage()`/`_syncFromUrlInner()`.
- [ ] **`menu_container_missing`** — gdy `app.initializer` loguje `Sidebar menu container not found`, identyfikować brakujący selektor.
- [ ] **Submodule mirror import resolver** — lepsza obsługa symlink-ów do `<submodule>/frontend/src/modules/<name>`.
- [ ] `--auto-apply-low-risk` — automatyczne stosowanie patch-y dla diagnoz z `confidence >= 0.95`.
- [ ] `--watch` — pętla URL-probe → diagnoza → patch dla CI.
- [ ] Integracja z CI/CD
- [ ] Historia diagnoz i śledzenie postępu napraw
