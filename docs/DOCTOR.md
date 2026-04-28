# DOCTOR — Orchestrator Analizy i Generator Akcji Naprawczych

`doctor` to orchestrator analizy regresji, który na bazie wyników z innych narzędzi (`regres`, `refactor`, `defscan`, `import-error-toon-report`) wyciąga wnioski i generuje konkretne akcje naprawcze w formie NLP opisów oraz poleceń shell.

## Funkcjonalności

Doctor analizuje wyniki z różnych narzędzi i:

1. **Wyciąga wnioski** o naturze problemów (błędy importów, duplikaty, regresje)
2. **Generuje NLP opisy** zrozumiałe dla człowieka
3. **Tworzy polecenia shell** do automatycznej naprawy
4. **Sugeruje akcje na plikach** (move, copy, delete, modify, create)
5. **Ocenia pewność** (confidence) każdej diagnozy

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
- **problem_type** — typ problemu (import_error, duplicate, regression)
- **severity** — poziom ważności (low, medium, high, critical)
- **nlp_description** — szczegółowy opis w języku naturalnym
- **file_actions** — lista akcji na plikach
- **shell_commands** — lista poleceń shell do wykonania
- **confidence** — pewność diagnozy (0.0 - 1.0)

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

# 3. Przejrzyj raport i wykonaj akcje
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

- Integracja z LLM dla generowania bardziej inteligentnych sugestii
- Automatyczne wykonywanie bezpiecznych akcji
- Integracja z CI/CD
- Historia diagnoz i śledzenie postępu napraw
