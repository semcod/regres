---
description: c2004 baseline gate for connect-config-security-settings
---
1. Ustaw zmienne:
   ```bash
   SCAN_ROOT=/home/tom/github/maskservice/c2004
   URL='http://localhost:8100/connect-config-security-settings?font=default&theme=dark&role=admin&lang=pl&size=100'
   RUNTIME_LOG="$SCAN_ROOT/.regres/runtime-console.log"
   ```

2. Odśwież import diagnostics:
   ```bash
   python3 -m regres.regres_cli import-error-toon-report \
     --frontend-cwd "$SCAN_ROOT/frontend" \
     --scan-root "$SCAN_ROOT" \
     --out-md "$SCAN_ROOT/.regres/import-error-toon-report.md" \
     --out-raw-log "$SCAN_ROOT/.regres/import-error-toon-report.raw.log"
   ```

3. Uruchom baseline doctor dla URL:
   ```bash
   python3 -m regres.regres_cli doctor \
     --scan-root "$SCAN_ROOT" \
     --url "$URL" \
     --all \
     --git-history \
     --vite-base http://localhost:8100 \
     --runtime-log "$RUNTIME_LOG" \
     --out-md "$SCAN_ROOT/.regres/security-settings-baseline-doctor.md"
   ```

4. Szybki gate HTTP:
   ```bash
   curl -s -o /dev/null -w 'icons_status=%{http_code}\n' http://localhost:8100/api/v3/icons
   curl -s -o /dev/null -w 'route_status=%{http_code}\n' "$URL"
   ```

5. Zaakceptuj baseline tylko gdy raport nie zawiera krytycznych regresji:
   - brak `page_content_regression`
   - brak `import_resolution_failure`
   - brak `runtime_icon_registry_miss`
