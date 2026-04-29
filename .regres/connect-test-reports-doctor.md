# Doctor Report

**Scan Root:** `/home/tom/github/maskservice/c2004`

**Diagnoses:** 2

## Decision Workflow

Drzewo decyzyjne — każdy krok pokazuje predykaty wejściowe, decyzję i rezultat:

1. ✓ **url discovery** [done] — Wyznaczenie modułu docelowego i zakresu analizy na podstawie URL.
   - **Decision:** Brak hint-a; pierwszy segment URL → moduł `connect-test`
   - **Inputs:** `url`=http://localhost:8100/connect-test/reports?font=default&theme=dark&role=admin..., `url_path`=connect-test/reports, `had_route_hint`=false
   - **Outputs:** `module_name`=connect-test, `route_hint`=null
   - **Details:** module inferred: connect-test
2. ✓ **module scope resolution** [done] — Mapowanie modułu URL na ścieżkę w repozytorium.
3. ✓ **page implementation analysis** [done] — Wykrycie placeholder/stub plików strony pasujących do URL.
   - **Decision:** Z URL `connect-test/reports` wyciągnięto token strony `None`. Szukam plików `*None.page.ts` w `/home/tom/github/maskservice/c2004/connect-test/frontend/src/modules/connect-test` i sprawdzam stub/placeholder oraz regresję względem historii git.
   - **Inputs:** `module_path`=/home/tom/github/maskservice/c2004/connect-test/frontend/src/modules/connect-..., `page_token`=null, `history_window_days`=30, `history_max_iterations`=30
   - **Outputs:** `diagnoses_found`=0, `problem_types`=[]
4. ✓ **module loader compliance** [done] — Sprawdź czy entry `*.module.ts` eksportuje klasę `*Module` lub `default` — wymóg lazy-loadera w `frontend/src/modules/index.ts`.
   - **Inputs:** `entry_file`=/home/tom/github/maskservice/c2004/connect-test/frontend/src/modules/connect-...
   - **Outputs:** `compliant`=true
5. ✓ **page registry compliance** [done] — Sprawdź czy `pages-index.ts` ma `defaultPage` obecny w rejestrze stron. Brak → BasePageManager wpada w nieskończoną rekurencję.
   - **Inputs:** `entry_file`=/home/tom/github/maskservice/c2004/connect-test/frontend/src/modules/connect-...
   - **Outputs:** `compliant`=true
6. ✓ **targeted module analysis** [done] — Uruchomienie diagnostyki modułu wynikającego z URL.

```bash
# url discovery [done]
python -m regres.regres_cli doctor --scan-root /home/tom/github/maskservice/c2004 --url http://localhost:8100/connect-test/reports?font=default&theme=dark&role=admin&lang=pl&size=100

# module scope resolution [done]
# resolved module path: /home/tom/github/maskservice/c2004/connect-test/frontend/src/modules/connect-test

# page implementation analysis [done]
python -m regres.regres_cli doctor --scan-root /home/tom/github/maskservice/c2004 --url http://localhost:8100/connect-test/reports?font=default&theme=dark&role=admin&lang=pl&size=100

# module loader compliance [done]
grep -nE 'export\s+(class|default)' /home/tom/github/maskservice/c2004/connect-test/frontend/src/modules/connect-test/connect-test.module.ts

# page registry compliance [done]
sed -n '1,80p' /home/tom/github/maskservice/c2004/connect-test/frontend/src/modules/connect-test/pages-index.ts

# targeted module analysis [done]
python -m regres.regres_cli doctor --scan-root /home/tom/github/maskservice/c2004 --url http://localhost:8100/connect-test/reports?font=default&theme=dark&role=admin&lang=pl&size=100

```

## Affected Files

Brak plików do zmiany — diagnozy nie proponują modyfikacji.

## Project Relation Map

- modules: 21/21 existing
- scanned files: 434 (truncated)
- import edges: 653
- missing imports: 388
- duplicate names: 21
- duplicate contents: 0
- git layer: 30 commits, 7 renames

## Project Structure Snapshot

```text
frontend/src/main.ts
frontend/src/vite-env.d.ts
frontend/src/generated/customer-status-changed-event.validator.ts
frontend/src/generated/list-data-tables-query.validator.ts
frontend/src/generated/protocol-measurement.validator.ts
frontend/src/generated/manager-test-type-assignment-saved-event.validator.ts
frontend/src/generated/manager-library-add-item-command.validator.ts
frontend/src/generated/test-session-cancelled-event.validator.ts
frontend/src/generated/start-test-session-command.validator.ts
frontend/src/generated/step-result-recorded-event.validator.ts
frontend/src/generated/identification-history-read-model.validator.ts
frontend/src/generated/scenario-created-event.validator.ts
frontend/src/generated/bulk-replace-data-table-command.validator.ts
frontend/src/generated/list-dsl-params-query.validator.ts
frontend/src/generated/get-data-record-query.validator.ts
frontend/src/generated/manager-update-activity-command.validator.ts
frontend/src/generated/remove-activity-from-scenario-command.validator.ts
frontend/src/generated/scenario-updated-event.validator.ts
frontend/src/generated/manager-test-type-assignment-deleted-event.validator.ts
frontend/src/generated/identification-succeeded-event.validator.ts
frontend/src/generated/create-scenario-command.validator.ts
frontend/src/generated/dsl-validation-error.validator.ts
frontend/src/generated/dsl-objects-list-read-model.validator.ts
frontend/src/generated/device-list-item.validator.ts
frontend/src/generated/manager-activity-item.validator.ts
frontend/src/generated/manager-library-loaded-event.validator.ts
frontend/src/generated/list-data-records-query.validator.ts
frontend/src/generated/identification-failed-event.validator.ts
frontend/src/generated/event-in.validator.ts
frontend/src/generated/set-workshop-method-command.validator.ts
frontend/src/generated/list-customers-query.validator.ts
frontend/src/generated/manager-assignment-item.validator.ts
frontend/src/generated/data-record-created-event.validator.ts
frontend/src/generated/cancel-test-session-command.validator.ts
frontend/src/generated/index.ts
frontend/src/generated/reports-protocols-loaded-event.validator.ts
frontend/src/generated/customer-read-model.validator.ts
frontend/src/generated/measurement-added-event.validator.ts
frontend/src/generated/test-session-list-item.validator.ts
frontend/src/generated/protocol-event.validator.ts
frontend/src/generated/get-protocol-query.validator.ts
frontend/src/generated/list-dsl-objects-query.validator.ts
frontend/src/generated/manager-scenario-goal.validator.ts
frontend/src/generated/reports-view-set-event.validator.ts
frontend/src/generated/customer-reactivated-event.validator.ts
frontend/src/generated/identify-command-input.validator.ts
frontend/src/generated/service-reports-health-read-model.validator.ts
frontend/src/generated/add-test-session-note-command.validator.ts
frontend/src/generated/load-manager-library-command.validator.ts
frontend/src/generated/service-id-health-read-model.validator.ts
frontend/src/generated/create-data-record-command.validator.ts
frontend/src/generated/manager-library-delete-item-command.validator.ts
frontend/src/generated/update-device-command.validator.ts
frontend/src/generated/validate-dsl-def-command.validator.ts
frontend/src/generated/customer-updated-event.validator.ts
frontend/src/generated/test-session-paused-event.validator.ts
frontend/src/generated/protocol-read-model.validator.ts
frontend/src/generated/approve-protocol-command.validator.ts
frontend/src/generated/execute-scenario-command.validator.ts
frontend/src/generated/service-manager-health-read-model.validator.ts
frontend/src/generated/manager-delete-activity-command.validator.ts
frontend/src/generated/dsl-param-def.validator.ts
frontend/src/generated/manager-activity-added-event.validator.ts
frontend/src/generated/step-result-read-model.validator.ts
frontend/src/generated/complete-protocol-command.validator.ts
frontend/src/generated/workshop-health-checks.validator.ts
frontend/src/generated/protocol-list-item.validator.ts
frontend/src/generated/test-session-note-added-event.validator.ts
frontend/src/generated/get-customer-devices-query.validator.ts
frontend/src/generated/schema-index-def.validator.ts
frontend/src/generated/manager-add-activity-command.validator.ts
frontend/src/generated/get-schema-query.validator.ts
frontend/src/generated/add-activity-to-scenario-command.validator.ts
frontend/src/generated/service-scenario-health-read-model.validator.ts
frontend/src/generated/create-test-session-command.validator.ts
frontend/src/generated/manager-library-item.validator.ts
frontend/src/generated/generate-protocol-document-command.validator.ts
frontend/src/generated/execution-status-read-model.validator.ts
frontend/src/generated/customer-list-item.validator.ts
frontend/src/generated/dsl-params-list-read-model.validator.ts
frontend/src/generated/delete-scenario-command.validator.ts
frontend/src/generated/list-dsl-functions-query.validator.ts
frontend/src/generated/device-read-model.validator.ts
frontend/src/generated/create-protocol-command.validator.ts
frontend/src/generated/device-removed-from-customer-event.validator.ts
frontend/src/generated/data-record-event.validator.ts
frontend/src/generated/scenario-activity-item.validator.ts
frontend/src/generated/list-test-sessions-query.validator.ts
frontend/src/generated/reports-protocol-measurement.validator.ts
frontend/src/generated/change-customer-status-command.validator.ts
frontend/src/generated/customer-suspended-event.validator.ts
frontend/src/generated/filter-reports-protocols-command.validator.ts
frontend/src/generated/manager-scenario-goal-task.validator.ts
frontend/src/generated/update-scenario-command.validator.ts
frontend/src/generated/scenario-activities-read-model.validator.ts
frontend/src/generated/test-session-started-event.validator.ts
frontend/src/generated/reports-protocol-device-item.validator.ts
frontend/src/generated/reactivate-customer-command.validator.ts
frontend/src/generated/workshop-section-set-event.validator.ts
frontend/src/generated/data-record-updated-event.validator.ts
frontend/src/generated/data-table-list-read-model.validator.ts
frontend/src/generated/customer-created-event.validator.ts
frontend/src/generated/scenario-dsl-read-model.validator.ts
frontend/src/generated/get-customer-query.validator.ts
frontend/src/generated/protocol-created-event.validator.ts
frontend/src/generated/list-protocols-query.validator.ts
frontend/src/generated/scenario-deleted-event.validator.ts
frontend/src/generated/manager-section-set-event.validator.ts
frontend/src/generated/service-data-module-health.validator.ts
frontend/src/generated/manager-delete-test-type-assignment-command.validator.ts
frontend/src/generated/filter-reports-date-range.validator.ts
frontend/src/generated/dsl-object-def.validator.ts
frontend/src/generated/update-data-record-command.validator.ts
frontend/src/generated/reports-protocol-client-item.validator.ts
frontend/src/generated/set-reports-view-command.validator.ts
frontend/src/generated/reports-filter-set-event.validator.ts
frontend/src/generated/manager-activity-deleted-event.validator.ts
frontend/src/generated/manager-method-set-event.validator.ts
frontend/src/generated/resume-test-session-command.validator.ts
frontend/src/generated/data-record-read-model.validator.ts
```

## Preliminary Refactor Proposals

Brak wstępnych propozycji refaktoryzacji.

## 🟡 1. Plik connect-test/frontend/src/modules/connect-test/pages/protocols.page.ts ma bogatą historię zmian (3 przeniesień)
**Type:** scope_drift | **Severity:** medium | **Confidence:** 70%

**Description:** Plik connect-test/frontend/src/modules/connect-test/pages/protocols.page.ts był wielokrotnie przenoszony (3 razy). Należy sprawdzić czy jest w odpowiednim module scope czy wymaga konsolidacji.

### File Actions
```
review: connect-test/frontend/src/modules/connect-test/pages/protocols.page.ts
  (Plik był przenoszony 3 razy - sprawdź czy jest w odpowiednim module)
```

### Shell Commands
```bash
# Sprawdź historię pliku
git log --follow --oneline -- connect-test/frontend/src/modules/connect-test/pages/protocols.page.ts

```

## 🟡 2. Plik connect-test/frontend/src/modules/connect-test/pages/protocol-host.page.ts ma bogatą historię zmian (4 przeniesień)
**Type:** scope_drift | **Severity:** medium | **Confidence:** 70%

**Description:** Plik connect-test/frontend/src/modules/connect-test/pages/protocol-host.page.ts był wielokrotnie przenoszony (4 razy). Należy sprawdzić czy jest w odpowiednim module scope czy wymaga konsolidacji.

### File Actions
```
review: connect-test/frontend/src/modules/connect-test/pages/protocol-host.page.ts
  (Plik był przenoszony 4 razy - sprawdź czy jest w odpowiednim module)
```

### Shell Commands
```bash
# Sprawdź historię pliku
git log --follow --oneline -- connect-test/frontend/src/modules/connect-test/pages/protocol-host.page.ts

```

## Step-by-Step Repair Playbook

### Step 1. Plik connect-test/frontend/src/modules/connect-test/pages/protocols.page.ts ma bogatą historię zmian (3 przeniesień)
Plik connect-test/frontend/src/modules/connect-test/pages/protocols.page.ts był wielokrotnie przenoszony (3 razy). Należy sprawdzić czy jest w odpowiednim module scope czy wymaga konsolidacji.

**1) Analyze**
```bash
# Sprawdź historię pliku
git log --follow --oneline -- connect-test/frontend/src/modules/connect-test/pages/protocols.page.ts

```

**2) Apply changes**
```diff
*** Begin Patch
*** Update File: connect-test/frontend/src/modules/connect-test/pages/protocols.page.ts
@@
-<old_code>
+<new_code>
*** End Patch

```

**3) Validate**
```bash
python -m regres.regres_cli doctor --scan-root . --all --out-md .regres/doctor-after-step.md
grep -n "Cannot find module" .regres/import-error-toon-report.raw.log | grep "connect-test/frontend/src/modules/connect-test/pages/protocols.page.ts" || true
```

### Step 2. Plik connect-test/frontend/src/modules/connect-test/pages/protocol-host.page.ts ma bogatą historię zmian (4 przeniesień)
Plik connect-test/frontend/src/modules/connect-test/pages/protocol-host.page.ts był wielokrotnie przenoszony (4 razy). Należy sprawdzić czy jest w odpowiednim module scope czy wymaga konsolidacji.

**1) Analyze**
```bash
# Sprawdź historię pliku
git log --follow --oneline -- connect-test/frontend/src/modules/connect-test/pages/protocol-host.page.ts

```

**2) Apply changes**
```diff
*** Begin Patch
*** Update File: connect-test/frontend/src/modules/connect-test/pages/protocol-host.page.ts
@@
-<old_code>
+<new_code>
*** End Patch

```

**3) Validate**
```bash
python -m regres.regres_cli doctor --scan-root . --all --out-md .regres/doctor-after-step.md
grep -n "Cannot find module" .regres/import-error-toon-report.raw.log | grep "connect-test/frontend/src/modules/connect-test/pages/protocol-host.page.ts" || true
```
