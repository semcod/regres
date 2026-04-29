---
description: c2004 pre-analysis and pre-deploy gates for regres doctor
---
1. Ustaw zmienne dla projektu i URL:
   ```bash
   SCAN_ROOT=/home/tom/github/maskservice/c2004
   URL='http://localhost:8100/connect-config-role-permissions?font=default&theme=dark&role=admin&lang=pl&size=100'
   RUNTIME_LOG="$SCAN_ROOT/.regres/runtime-console.log"
   ```

2. Uruchom pre-analysis gate (odśwież TS import log):
   ```bash
   python3 -m regres.regres_cli import-error-toon-report \
     --frontend-cwd "$SCAN_ROOT/frontend" \
     --scan-root "$SCAN_ROOT" \
     --out-md "$SCAN_ROOT/.regres/import-error-toon-report.md" \
     --out-raw-log "$SCAN_ROOT/.regres/import-error-toon-report.raw.log"
   ```

3. Uruchom doctor URL gate z pełnym kontekstem (defscan/refactor/git/vite/runtime):
   ```bash
   python3 -m regres.regres_cli doctor \
     --scan-root "$SCAN_ROOT" \
     --url "$URL" \
     --all \
     --git-history \
     --vite-base http://localhost:8100 \
     --runtime-log "$RUNTIME_LOG" \
     --out-md "$SCAN_ROOT/.regres/predeploy-doctor.md"
   ```

4. Zweryfikuj HTTP gate (backend + route):
   ```bash
   curl -s -o /dev/null -w 'icons_status=%{http_code}\n' http://localhost:8100/api/v3/icons
   curl -s -o /dev/null -w 'route_status=%{http_code}\n' "$URL"
   ```

5. Sprawdź wyniki w raporcie:
   - Otwórz `"$SCAN_ROOT/.regres/predeploy-doctor.md"`.
   - Zablokuj wdrożenie, jeśli występują `page_content_regression`, `import_resolution_failure` lub `runtime_icon_registry_miss`.

6. Jeśli są wygenerowane patche `.sh`, przejrzyj je najpierw w trybie preview/diff:
   ```bash
   bash "$SCAN_ROOT/.regres/predeploy-doctor-patches-index.sh"
   # następnie dla wybranego patcha:
   # bash <patch>.sh --preview
   # bash <patch>.sh --diff
   # bash <patch>.sh
   ```

7. Po zastosowaniu poprawek uruchom gate ponownie (kroki 3-5) i wdrażaj dopiero przy czystym raporcie.
