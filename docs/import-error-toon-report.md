# Import Error Toon Report

Skrypt pomaga szybko ogarnąć błędy typu import/export po refaktoryzacji frontendu.
Generuje **kompaktowy raport Markdown** z metrykami i rozszerzonym payloadem `TOON` (token-oriented).

## Cel

- zebrać błędy `TS2307` i `TS2305`
- pokazać metryki (ile błędów / ile plików)
- dać listę plików do naprawy w formacie łatwym do przekazania dalej
- wygenerować bloki `toon` gotowe do użycia w automatyzacji/taskach
- wygenerować sekcje tabelaryczne TOON (`[]` + header row) dla uniform arrays

## Użycie

```bash
# 1) automatycznie odpala type-check (frontend)
python3 scripts/import-error-toon-report.py

# 2) z gotowego logu
python3 scripts/import-error-toon-report.py --input-log .regres/typecheck.log

# 3) limit i własny plik raportu
python3 scripts/import-error-toon-report.py \
  --max-files 25 \
  --max-errors-per-file 8 \
  --out-md .regres/import-toon.md
```

## Wynik

Domyślnie:

- Markdown: `.regres/import-error-toon-report.md`
- raw log: `.regres/import-error-toon-report.raw.log`

## Format raportu

Raport zawiera:

1. `TOON Global Payload` (pełny snapshot błędów i metryk)
2. `TOON Compact Tickets` (krótka lista ticketów do napraw)
3. `Metrics` (sumaryczne statystyki)
4. `Top Missing Modules` (najczęściej brakujące importy)
5. `Files (Toon blocks - legacy ticket style)`

Przykład TOON (tabelaryczny):

```toon
report:
  schema: import_repair_report.v2
  scan_root: "frontend/src"
  metrics:
    total_errors: 30
    affected_files: 16

  files[]:
    file error_count ts2307 ts2305
    "connect-test-device/frontend/src/modules/connect-test-device/pages/device-testing.page.ts" 3 3 0

  file_error_rows[]:
    file code line col module member message
    "connect-test-device/frontend/src/modules/connect-test-device/pages/device-testing.page.ts" TS2307 24 37 "@c2004/connect-test/utils/normalize" "" "Cannot find module ..."
```

## Parametry

- `--input-log` – wejściowy log zamiast uruchamiania `type-check`
- `--frontend-cwd` – katalog, gdzie uruchamiany jest `type-check` (domyślnie `frontend/`)
- `--typecheck-cmd` – komenda type-check (domyślnie `npm run -s type-check`)
- `--include-codes` – kody TS do raportu (domyślnie `TS2307,TS2305`)
- `--max-files` – ile plików pokazać
- `--max-errors-per-file` – ile błędów pokazać per plik
- `--out-md` – plik markdown
- `--out-raw-log` – surowy log
- `--scan-root` – etykieta informacyjna w metrykach
