# Import Repair Compact Report

## TOON Global Payload

```toon
report:
  schema: import_repair_report.v2
  generated_at: "2026-04-28T13:09:58.809954+00:00"
  scan_root: "frontend/src"
  metrics:
    total_errors: 30
    affected_files: 16
    ts2307: 30
    ts2305: 0

  top_missing_modules[]:
    module count
    "./helpers/cql-iframe" 7
    "@c2004/frontend-host/modules/connect-manager/components/icon.component" 4
    "@c2004/frontend-host/modules/connect-manager/components/connect-table/connect-table.component" 2
    "../services/tables-config.service" 1
    "../services/dialog.service" 1
    "@c2004/frontend-host/modules/connect-manager/utils/html.utils" 1
    "@c2004/frontend-host/modules/connect-manager/utils/fetch.utils" 1
    "./helpers/connect-manager-test-types" 1
    "@c2004/frontend-host/modules/connect-manager/utils/logger" 1
    "@c2004/frontend-host/modules/connect-manager/components/connect-table" 1
    "../../../pages/helpers/connect-template-iframe" 1
    "../../../utils/html.utils" 1
    "../../connect-config/cqrs/singleton" 1
    "../../../pages/connect-data-generic.search.page" 1
    "./requests-search.page" 1
    "./requests-new-request.page" 1
    "./services-search.page" 1
    "./transport-search.page" 1
    "./dispositions-search.page" 1
    "./generic.search.page" 1

  files[]:
    file error_count ts2307 ts2305
    "/home/tom/github/maskservice/c2004/connect-workshop/frontend/src/modules/connect-workshop/pages-index.ts" 6 6 0
    "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-library.page.ts" 5 5 0
    "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-variables.page.ts" 3 3 0
    "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-activities.page.ts" 2 2 0
    "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-test-types.page.ts" 2 2 0
    "/home/tom/github/maskservice/c2004/connect-template/frontend/src/modules/connect-template/pages/template-json.page.ts" 2 2 0
    "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-intervals.page.ts" 1 1 0
    "/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-dsl-editor.page.ts" 1 1 0
    "/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-func-editor.page.ts" 1 1 0
    "/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-library-editor.page.ts" 1 1 0
    "/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-map-editor.page.ts" 1 1 0
    "/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-scenario-editor.page.ts" 1 1 0
    "/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-scenarios.page.ts" 1 1 0
    "/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-templates.page.ts" 1 1 0
    "/home/tom/github/maskservice/c2004/connect-template/frontend/src/modules/connect-template/pages/template-editor.page.ts" 1 1 0
    "/home/tom/github/maskservice/c2004/connect-reports/frontend/src/modules/connect-reports/pages/filter.page.ts" 1 1 0

  file_error_rows[]:
    file code line col module member message
    "/home/tom/github/maskservice/c2004/connect-workshop/frontend/src/modules/connect-workshop/pages-index.ts" TS2307 3 36 "./requests-search.page" "" "Cannot find module './requests-search.page' or its corresponding type declarations."
    "/home/tom/github/maskservice/c2004/connect-workshop/frontend/src/modules/connect-workshop/pages-index.ts" TS2307 4 40 "./requests-new-request.page" "" "Cannot find module './requests-new-request.page' or its corresponding type declarations."
    "/home/tom/github/maskservice/c2004/connect-workshop/frontend/src/modules/connect-workshop/pages-index.ts" TS2307 5 36 "./services-search.page" "" "Cannot find module './services-search.page' or its corresponding type declarations."
    "/home/tom/github/maskservice/c2004/connect-workshop/frontend/src/modules/connect-workshop/pages-index.ts" TS2307 6 37 "./transport-search.page" "" "Cannot find module './transport-search.page' or its corresponding type declarations."
    "/home/tom/github/maskservice/c2004/connect-workshop/frontend/src/modules/connect-workshop/pages-index.ts" TS2307 7 40 "./dispositions-search.page" "" "Cannot find module './dispositions-search.page' or its corresponding type declarations."
    "/home/tom/github/maskservice/c2004/connect-workshop/frontend/src/modules/connect-workshop/pages-index.ts" TS2307 9 43 "./generic.search.page" "" "Cannot find module './generic.search.page' or its corresponding type declarations."
    "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-library.page.ts" TS2307 3 37 "../services/tables-config.service" "" "Cannot find module '../services/tables-config.service' or its corresponding type declarations."
    "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-library.page.ts" TS2307 4 31 "../services/dialog.service" "" "Cannot find module '../services/dialog.service' or its corresponding type declarations."
    "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-library.page.ts" TS2307 5 28 "@c2004/frontend-host/modules/connect-manager/utils/html.utils" "" "Cannot find module '@c2004/frontend-host/modules/connect-manager/utils/html.utils' or its corresponding type declarations."
    "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-library.page.ts" TS2307 6 31 "@c2004/frontend-host/modules/connect-manager/utils/fetch.utils" "" "Cannot find module '@c2004/frontend-host/modules/connect-manager/utils/fetch.utils' or its corresponding type declarations."
    "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-library.page.ts" TS2307 7 31 "@c2004/frontend-host/modules/connect-manager/components/icon.component" "" "Cannot find module '@c2004/frontend-host/modules/connect-manager/components/icon.component' or its corresponding type declarations."
    "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-variables.page.ts" TS2307 4 24 "@c2004/frontend-host/modules/connect-manager/utils/logger" "" "Cannot find module '@c2004/frontend-host/modules/connect-manager/utils/logger' or its corresponding type declarations."
    "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-variables.page.ts" TS2307 5 39 "@c2004/frontend-host/modules/connect-manager/components/connect-table" "" "Cannot find module '@c2004/frontend-host/modules/connect-manager/components/connect-table' or its corresponding type declarations."
    "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-variables.page.ts" TS2307 7 31 "@c2004/frontend-host/modules/connect-manager/components/icon.component" "" "Cannot find module '@c2004/frontend-host/modules/connect-manager/components/icon.component' or its corresponding type declarations."
    "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-activities.page.ts" TS2307 2 39 "@c2004/frontend-host/modules/connect-manager/components/connect-table/connect-table.component" "" "Cannot find module '@c2004/frontend-host/modules/connect-manager/components/connect-table/connect-table.component' or its corresponding type declarations."
    "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-activities.page.ts" TS2307 3 31 "@c2004/frontend-host/modules/connect-manager/components/icon.component" "" "Cannot find module '@c2004/frontend-host/modules/connect-manager/components/icon.component' or its corresponding type declarations."
    "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-test-types.page.ts" TS2307 6 8 "./helpers/connect-manager-test-types" "" "Cannot find module './helpers/connect-manager-test-types' or its corresponding type declarations."
    "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-test-types.page.ts" TS2307 7 31 "@c2004/frontend-host/modules/connect-manager/components/icon.component" "" "Cannot find module '@c2004/frontend-host/modules/connect-manager/components/icon.component' or its corresponding type declarations."
    "/home/tom/github/maskservice/c2004/connect-template/frontend/src/modules/connect-template/pages/template-json.page.ts" TS2307 6 28 "../../../utils/html.utils" "" "Cannot find module '../../../utils/html.utils' or its corresponding type declarations."
    "/home/tom/github/maskservice/c2004/connect-template/frontend/src/modules/connect-template/pages/template-json.page.ts" TS2307 7 31 "../../connect-config/cqrs/singleton" "" "Cannot find module '../../connect-config/cqrs/singleton' or its corresponding type declarations."
    "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-intervals.page.ts" TS2307 2 39 "@c2004/frontend-host/modules/connect-manager/components/connect-table/connect-table.component" "" "Cannot find module '@c2004/frontend-host/modules/connect-manager/components/connect-table/connect-table.component' or its corresponding type declarations."
    "/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-dsl-editor.page.ts" TS2307 9 67 "./helpers/cql-iframe" "" "Cannot find module './helpers/cql-iframe' or its corresponding type declarations."
    "/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-func-editor.page.ts" TS2307 8 67 "./helpers/cql-iframe" "" "Cannot find module './helpers/cql-iframe' or its corresponding type declarations."
    "/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-library-editor.page.ts" TS2307 8 67 "./helpers/cql-iframe" "" "Cannot find module './helpers/cql-iframe' or its corresponding type declarations."
    "/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-map-editor.page.ts" TS2307 8 67 "./helpers/cql-iframe" "" "Cannot find module './helpers/cql-iframe' or its corresponding type declarations."
    "/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-scenario-editor.page.ts" TS2307 8 67 "./helpers/cql-iframe" "" "Cannot find module './helpers/cql-iframe' or its corresponding type declarations."
    "/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-scenarios.page.ts" TS2307 8 67 "./helpers/cql-iframe" "" "Cannot find module './helpers/cql-iframe' or its corresponding type declarations."
    "/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-templates.page.ts" TS2307 1 67 "./helpers/cql-iframe" "" "Cannot find module './helpers/cql-iframe' or its corresponding type declarations."
    "/home/tom/github/maskservice/c2004/connect-template/frontend/src/modules/connect-template/pages/template-editor.page.ts" TS2307 1 103 "../../../pages/helpers/connect-template-iframe" "" "Cannot find module '../../../pages/helpers/connect-template-iframe' or its corresponding type declarations."
    "/home/tom/github/maskservice/c2004/connect-reports/frontend/src/modules/connect-reports/pages/filter.page.ts" TS2307 2 35 "../../../pages/connect-data-generic.search.page" "" "Cannot find module '../../../pages/connect-data-generic.search.page' or its corresponding type declarations."
```

## TOON Compact Tickets

```toon
tickets[]:
  file error_count primary_code
  "/home/tom/github/maskservice/c2004/connect-workshop/frontend/src/modules/connect-workshop/pages-index.ts" 6 TS2307
  "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-library.page.ts" 5 TS2307
  "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-variables.page.ts" 3 TS2307
  "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-activities.page.ts" 2 TS2307
  "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-test-types.page.ts" 2 TS2307
  "/home/tom/github/maskservice/c2004/connect-template/frontend/src/modules/connect-template/pages/template-json.page.ts" 2 TS2307
  "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-intervals.page.ts" 1 TS2307
  "/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-dsl-editor.page.ts" 1 TS2307
  "/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-func-editor.page.ts" 1 TS2307
  "/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-library-editor.page.ts" 1 TS2307
  "/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-map-editor.page.ts" 1 TS2307
  "/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-scenario-editor.page.ts" 1 TS2307
  "/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-scenarios.page.ts" 1 TS2307
  "/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-templates.page.ts" 1 TS2307
  "/home/tom/github/maskservice/c2004/connect-template/frontend/src/modules/connect-template/pages/template-editor.page.ts" 1 TS2307
  "/home/tom/github/maskservice/c2004/connect-reports/frontend/src/modules/connect-reports/pages/filter.page.ts" 1 TS2307

ticket_errors[]:
  file code line col module message
  "/home/tom/github/maskservice/c2004/connect-workshop/frontend/src/modules/connect-workshop/pages-index.ts" TS2307 3 36 "./requests-search.page" "Cannot find module './requests-search.page' or its corresponding type declarations."
  "/home/tom/github/maskservice/c2004/connect-workshop/frontend/src/modules/connect-workshop/pages-index.ts" TS2307 4 40 "./requests-new-request.page" "Cannot find module './requests-new-request.page' or its corresponding type declarations."
  "/home/tom/github/maskservice/c2004/connect-workshop/frontend/src/modules/connect-workshop/pages-index.ts" TS2307 5 36 "./services-search.page" "Cannot find module './services-search.page' or its corresponding type declarations."
  "/home/tom/github/maskservice/c2004/connect-workshop/frontend/src/modules/connect-workshop/pages-index.ts" TS2307 6 37 "./transport-search.page" "Cannot find module './transport-search.page' or its corresponding type declarations."
  "/home/tom/github/maskservice/c2004/connect-workshop/frontend/src/modules/connect-workshop/pages-index.ts" TS2307 7 40 "./dispositions-search.page" "Cannot find module './dispositions-search.page' or its corresponding type declarations."
  "/home/tom/github/maskservice/c2004/connect-workshop/frontend/src/modules/connect-workshop/pages-index.ts" TS2307 9 43 "./generic.search.page" "Cannot find module './generic.search.page' or its corresponding type declarations."
  "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-library.page.ts" TS2307 3 37 "../services/tables-config.service" "Cannot find module '../services/tables-config.service' or its corresponding type declarations."
  "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-library.page.ts" TS2307 4 31 "../services/dialog.service" "Cannot find module '../services/dialog.service' or its corresponding type declarations."
  "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-library.page.ts" TS2307 5 28 "@c2004/frontend-host/modules/connect-manager/utils/html.utils" "Cannot find module '@c2004/frontend-host/modules/connect-manager/utils/html.utils' or its corresponding type declarations."
  "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-library.page.ts" TS2307 6 31 "@c2004/frontend-host/modules/connect-manager/utils/fetch.utils" "Cannot find module '@c2004/frontend-host/modules/connect-manager/utils/fetch.utils' or its corresponding type declarations."
  "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-library.page.ts" TS2307 7 31 "@c2004/frontend-host/modules/connect-manager/components/icon.component" "Cannot find module '@c2004/frontend-host/modules/connect-manager/components/icon.component' or its corresponding type declarations."
  "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-variables.page.ts" TS2307 4 24 "@c2004/frontend-host/modules/connect-manager/utils/logger" "Cannot find module '@c2004/frontend-host/modules/connect-manager/utils/logger' or its corresponding type declarations."
  "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-variables.page.ts" TS2307 5 39 "@c2004/frontend-host/modules/connect-manager/components/connect-table" "Cannot find module '@c2004/frontend-host/modules/connect-manager/components/connect-table' or its corresponding type declarations."
  "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-variables.page.ts" TS2307 7 31 "@c2004/frontend-host/modules/connect-manager/components/icon.component" "Cannot find module '@c2004/frontend-host/modules/connect-manager/components/icon.component' or its corresponding type declarations."
  "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-activities.page.ts" TS2307 2 39 "@c2004/frontend-host/modules/connect-manager/components/connect-table/connect-table.component" "Cannot find module '@c2004/frontend-host/modules/connect-manager/components/connect-table/connect-table.component' or its corresponding type declarations."
  "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-activities.page.ts" TS2307 3 31 "@c2004/frontend-host/modules/connect-manager/components/icon.component" "Cannot find module '@c2004/frontend-host/modules/connect-manager/components/icon.component' or its corresponding type declarations."
  "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-test-types.page.ts" TS2307 6 8 "./helpers/connect-manager-test-types" "Cannot find module './helpers/connect-manager-test-types' or its corresponding type declarations."
  "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-test-types.page.ts" TS2307 7 31 "@c2004/frontend-host/modules/connect-manager/components/icon.component" "Cannot find module '@c2004/frontend-host/modules/connect-manager/components/icon.component' or its corresponding type declarations."
  "/home/tom/github/maskservice/c2004/connect-template/frontend/src/modules/connect-template/pages/template-json.page.ts" TS2307 6 28 "../../../utils/html.utils" "Cannot find module '../../../utils/html.utils' or its corresponding type declarations."
  "/home/tom/github/maskservice/c2004/connect-template/frontend/src/modules/connect-template/pages/template-json.page.ts" TS2307 7 31 "../../connect-config/cqrs/singleton" "Cannot find module '../../connect-config/cqrs/singleton' or its corresponding type declarations."
  "/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-intervals.page.ts" TS2307 2 39 "@c2004/frontend-host/modules/connect-manager/components/connect-table/connect-table.component" "Cannot find module '@c2004/frontend-host/modules/connect-manager/components/connect-table/connect-table.component' or its corresponding type declarations."
  "/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-dsl-editor.page.ts" TS2307 9 67 "./helpers/cql-iframe" "Cannot find module './helpers/cql-iframe' or its corresponding type declarations."
  "/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-func-editor.page.ts" TS2307 8 67 "./helpers/cql-iframe" "Cannot find module './helpers/cql-iframe' or its corresponding type declarations."
  "/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-library-editor.page.ts" TS2307 8 67 "./helpers/cql-iframe" "Cannot find module './helpers/cql-iframe' or its corresponding type declarations."
  "/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-map-editor.page.ts" TS2307 8 67 "./helpers/cql-iframe" "Cannot find module './helpers/cql-iframe' or its corresponding type declarations."
  "/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-scenario-editor.page.ts" TS2307 8 67 "./helpers/cql-iframe" "Cannot find module './helpers/cql-iframe' or its corresponding type declarations."
  "/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-scenarios.page.ts" TS2307 8 67 "./helpers/cql-iframe" "Cannot find module './helpers/cql-iframe' or its corresponding type declarations."
  "/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-templates.page.ts" TS2307 1 67 "./helpers/cql-iframe" "Cannot find module './helpers/cql-iframe' or its corresponding type declarations."
  "/home/tom/github/maskservice/c2004/connect-template/frontend/src/modules/connect-template/pages/template-editor.page.ts" TS2307 1 103 "../../../pages/helpers/connect-template-iframe" "Cannot find module '../../../pages/helpers/connect-template-iframe' or its corresponding type declarations."
  "/home/tom/github/maskservice/c2004/connect-reports/frontend/src/modules/connect-reports/pages/filter.page.ts" TS2307 2 35 "../../../pages/connect-data-generic.search.page" "Cannot find module '../../../pages/connect-data-generic.search.page' or its corresponding type declarations."
```

## Metrics

| Metric | Value |
|---|---:|
| total_errors | 30 |
| affected_files | 16 |
| TS2307 | 30 |
| TS2305 | 0 |
| scan_root | `frontend/src` |

## Top Missing Modules

| module | count |
|---|---:|
| `./helpers/cql-iframe` | 7 |
| `@c2004/frontend-host/modules/connect-manager/components/icon.component` | 4 |
| `@c2004/frontend-host/modules/connect-manager/components/connect-table/connect-table.component` | 2 |
| `../services/tables-config.service` | 1 |
| `../services/dialog.service` | 1 |
| `@c2004/frontend-host/modules/connect-manager/utils/html.utils` | 1 |
| `@c2004/frontend-host/modules/connect-manager/utils/fetch.utils` | 1 |
| `./helpers/connect-manager-test-types` | 1 |
| `@c2004/frontend-host/modules/connect-manager/utils/logger` | 1 |
| `@c2004/frontend-host/modules/connect-manager/components/connect-table` | 1 |
| `../../../pages/helpers/connect-template-iframe` | 1 |
| `../../../utils/html.utils` | 1 |
| `../../connect-config/cqrs/singleton` | 1 |
| `../../../pages/connect-data-generic.search.page` | 1 |
| `./requests-search.page` | 1 |
| `./requests-new-request.page` | 1 |
| `./services-search.page` | 1 |
| `./transport-search.page` | 1 |
| `./dispositions-search.page` | 1 |
| `./generic.search.page` | 1 |

## Files (Toon blocks - legacy ticket style)

### `/home/tom/github/maskservice/c2004/connect-workshop/frontend/src/modules/connect-workshop/pages-index.ts` (6)

```toon
kind: import_repair_ticket
file: /home/tom/github/maskservice/c2004/connect-workshop/frontend/src/modules/connect-workshop/pages-index.ts
error_count: 6
errors:
  - code: TS2307
    line: 3
    col: 36
    module: './requests-search.page'
    message: 'Cannot find module \'./requests-search.page\' or its corresponding type declarations.'
  - code: TS2307
    line: 4
    col: 40
    module: './requests-new-request.page'
    message: 'Cannot find module \'./requests-new-request.page\' or its corresponding type declarations.'
  - code: TS2307
    line: 5
    col: 36
    module: './services-search.page'
    message: 'Cannot find module \'./services-search.page\' or its corresponding type declarations.'
  - code: TS2307
    line: 6
    col: 37
    module: './transport-search.page'
    message: 'Cannot find module \'./transport-search.page\' or its corresponding type declarations.'
  - code: TS2307
    line: 7
    col: 40
    module: './dispositions-search.page'
    message: 'Cannot find module \'./dispositions-search.page\' or its corresponding type declarations.'
  - code: TS2307
    line: 9
    col: 43
    module: './generic.search.page'
    message: 'Cannot find module \'./generic.search.page\' or its corresponding type declarations.'
actions:
  - 'Zweryfikuj relatywną ścieżkę i poziom zagnieżdżenia po refaktorze.'
```

### `/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-library.page.ts` (5)

```toon
kind: import_repair_ticket
file: /home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-library.page.ts
error_count: 5
errors:
  - code: TS2307
    line: 3
    col: 37
    module: '../services/tables-config.service'
    message: 'Cannot find module \'../services/tables-config.service\' or its corresponding type declarations.'
  - code: TS2307
    line: 4
    col: 31
    module: '../services/dialog.service'
    message: 'Cannot find module \'../services/dialog.service\' or its corresponding type declarations.'
  - code: TS2307
    line: 5
    col: 28
    module: '@c2004/frontend-host/modules/connect-manager/utils/html.utils'
    message: 'Cannot find module \'@c2004/frontend-host/modules/connect-manager/utils/html.utils\' or its corresponding type declarations.'
  - code: TS2307
    line: 6
    col: 31
    module: '@c2004/frontend-host/modules/connect-manager/utils/fetch.utils'
    message: 'Cannot find module \'@c2004/frontend-host/modules/connect-manager/utils/fetch.utils\' or its corresponding type declarations.'
  - code: TS2307
    line: 7
    col: 31
    module: '@c2004/frontend-host/modules/connect-manager/components/icon.component'
    message: 'Cannot find module \'@c2004/frontend-host/modules/connect-manager/components/icon.component\' or its corresponding type declarations.'
actions:
  - 'Zweryfikuj relatywną ścieżkę i poziom zagnieżdżenia po refaktorze.'
  - 'Sprawdź alias w `frontend/vite.config.ts` i czy docelowy plik istnieje.'
```

### `/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-variables.page.ts` (3)

```toon
kind: import_repair_ticket
file: /home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-variables.page.ts
error_count: 3
errors:
  - code: TS2307
    line: 4
    col: 24
    module: '@c2004/frontend-host/modules/connect-manager/utils/logger'
    message: 'Cannot find module \'@c2004/frontend-host/modules/connect-manager/utils/logger\' or its corresponding type declarations.'
  - code: TS2307
    line: 5
    col: 39
    module: '@c2004/frontend-host/modules/connect-manager/components/connect-table'
    message: 'Cannot find module \'@c2004/frontend-host/modules/connect-manager/components/connect-table\' or its corresponding type declarations.'
  - code: TS2307
    line: 7
    col: 31
    module: '@c2004/frontend-host/modules/connect-manager/components/icon.component'
    message: 'Cannot find module \'@c2004/frontend-host/modules/connect-manager/components/icon.component\' or its corresponding type declarations.'
actions:
  - 'Sprawdź alias w `frontend/vite.config.ts` i czy docelowy plik istnieje.'
```

### `/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-activities.page.ts` (2)

```toon
kind: import_repair_ticket
file: /home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-activities.page.ts
error_count: 2
errors:
  - code: TS2307
    line: 2
    col: 39
    module: '@c2004/frontend-host/modules/connect-manager/components/connect-table/connect-table.component'
    message: 'Cannot find module \'@c2004/frontend-host/modules/connect-manager/components/connect-table/connect-table.component\' or its corresponding type declarations.'
  - code: TS2307
    line: 3
    col: 31
    module: '@c2004/frontend-host/modules/connect-manager/components/icon.component'
    message: 'Cannot find module \'@c2004/frontend-host/modules/connect-manager/components/icon.component\' or its corresponding type declarations.'
actions:
  - 'Sprawdź alias w `frontend/vite.config.ts` i czy docelowy plik istnieje.'
```

### `/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-test-types.page.ts` (2)

```toon
kind: import_repair_ticket
file: /home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-test-types.page.ts
error_count: 2
errors:
  - code: TS2307
    line: 6
    col: 8
    module: './helpers/connect-manager-test-types'
    message: 'Cannot find module \'./helpers/connect-manager-test-types\' or its corresponding type declarations.'
  - code: TS2307
    line: 7
    col: 31
    module: '@c2004/frontend-host/modules/connect-manager/components/icon.component'
    message: 'Cannot find module \'@c2004/frontend-host/modules/connect-manager/components/icon.component\' or its corresponding type declarations.'
actions:
  - 'Zweryfikuj relatywną ścieżkę i poziom zagnieżdżenia po refaktorze.'
  - 'Sprawdź alias w `frontend/vite.config.ts` i czy docelowy plik istnieje.'
```

### `/home/tom/github/maskservice/c2004/connect-template/frontend/src/modules/connect-template/pages/template-json.page.ts` (2)

```toon
kind: import_repair_ticket
file: /home/tom/github/maskservice/c2004/connect-template/frontend/src/modules/connect-template/pages/template-json.page.ts
error_count: 2
errors:
  - code: TS2307
    line: 6
    col: 28
    module: '../../../utils/html.utils'
    message: 'Cannot find module \'../../../utils/html.utils\' or its corresponding type declarations.'
  - code: TS2307
    line: 7
    col: 31
    module: '../../connect-config/cqrs/singleton'
    message: 'Cannot find module \'../../connect-config/cqrs/singleton\' or its corresponding type declarations.'
actions:
  - 'Zweryfikuj relatywną ścieżkę i poziom zagnieżdżenia po refaktorze.'
  - 'Rozważ zamianę głębokiej ścieżki na alias `@c2004/*`.'
```

### `/home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-intervals.page.ts` (1)

```toon
kind: import_repair_ticket
file: /home/tom/github/maskservice/c2004/connect-manager/frontend/src/pages/connect-manager-intervals.page.ts
error_count: 1
errors:
  - code: TS2307
    line: 2
    col: 39
    module: '@c2004/frontend-host/modules/connect-manager/components/connect-table/connect-table.component'
    message: 'Cannot find module \'@c2004/frontend-host/modules/connect-manager/components/connect-table/connect-table.component\' or its corresponding type declarations.'
actions:
  - 'Sprawdź alias w `frontend/vite.config.ts` i czy docelowy plik istnieje.'
```

### `/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-dsl-editor.page.ts` (1)

```toon
kind: import_repair_ticket
file: /home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-dsl-editor.page.ts
error_count: 1
errors:
  - code: TS2307
    line: 9
    col: 67
    module: './helpers/cql-iframe'
    message: 'Cannot find module \'./helpers/cql-iframe\' or its corresponding type declarations.'
actions:
  - 'Zweryfikuj relatywną ścieżkę i poziom zagnieżdżenia po refaktorze.'
```

### `/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-func-editor.page.ts` (1)

```toon
kind: import_repair_ticket
file: /home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-func-editor.page.ts
error_count: 1
errors:
  - code: TS2307
    line: 8
    col: 67
    module: './helpers/cql-iframe'
    message: 'Cannot find module \'./helpers/cql-iframe\' or its corresponding type declarations.'
actions:
  - 'Zweryfikuj relatywną ścieżkę i poziom zagnieżdżenia po refaktorze.'
```

### `/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-library-editor.page.ts` (1)

```toon
kind: import_repair_ticket
file: /home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-library-editor.page.ts
error_count: 1
errors:
  - code: TS2307
    line: 8
    col: 67
    module: './helpers/cql-iframe'
    message: 'Cannot find module \'./helpers/cql-iframe\' or its corresponding type declarations.'
actions:
  - 'Zweryfikuj relatywną ścieżkę i poziom zagnieżdżenia po refaktorze.'
```

### `/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-map-editor.page.ts` (1)

```toon
kind: import_repair_ticket
file: /home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-map-editor.page.ts
error_count: 1
errors:
  - code: TS2307
    line: 8
    col: 67
    module: './helpers/cql-iframe'
    message: 'Cannot find module \'./helpers/cql-iframe\' or its corresponding type declarations.'
actions:
  - 'Zweryfikuj relatywną ścieżkę i poziom zagnieżdżenia po refaktorze.'
```

### `/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-scenario-editor.page.ts` (1)

```toon
kind: import_repair_ticket
file: /home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-scenario-editor.page.ts
error_count: 1
errors:
  - code: TS2307
    line: 8
    col: 67
    module: './helpers/cql-iframe'
    message: 'Cannot find module \'./helpers/cql-iframe\' or its corresponding type declarations.'
actions:
  - 'Zweryfikuj relatywną ścieżkę i poziom zagnieżdżenia po refaktorze.'
```

### `/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-scenarios.page.ts` (1)

```toon
kind: import_repair_ticket
file: /home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-scenarios.page.ts
error_count: 1
errors:
  - code: TS2307
    line: 8
    col: 67
    module: './helpers/cql-iframe'
    message: 'Cannot find module \'./helpers/cql-iframe\' or its corresponding type declarations.'
actions:
  - 'Zweryfikuj relatywną ścieżkę i poziom zagnieżdżenia po refaktorze.'
```

### `/home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-templates.page.ts` (1)

```toon
kind: import_repair_ticket
file: /home/tom/github/maskservice/c2004/connect-scenario/frontend/src/pages/connect-scenario-templates.page.ts
error_count: 1
errors:
  - code: TS2307
    line: 1
    col: 67
    module: './helpers/cql-iframe'
    message: 'Cannot find module \'./helpers/cql-iframe\' or its corresponding type declarations.'
actions:
  - 'Zweryfikuj relatywną ścieżkę i poziom zagnieżdżenia po refaktorze.'
```

### `/home/tom/github/maskservice/c2004/connect-template/frontend/src/modules/connect-template/pages/template-editor.page.ts` (1)

```toon
kind: import_repair_ticket
file: /home/tom/github/maskservice/c2004/connect-template/frontend/src/modules/connect-template/pages/template-editor.page.ts
error_count: 1
errors:
  - code: TS2307
    line: 1
    col: 103
    module: '../../../pages/helpers/connect-template-iframe'
    message: 'Cannot find module \'../../../pages/helpers/connect-template-iframe\' or its corresponding type declarations.'
actions:
  - 'Zweryfikuj relatywną ścieżkę i poziom zagnieżdżenia po refaktorze.'
  - 'Rozważ zamianę głębokiej ścieżki na alias `@c2004/*`.'
```

### `/home/tom/github/maskservice/c2004/connect-reports/frontend/src/modules/connect-reports/pages/filter.page.ts` (1)

```toon
kind: import_repair_ticket
file: /home/tom/github/maskservice/c2004/connect-reports/frontend/src/modules/connect-reports/pages/filter.page.ts
error_count: 1
errors:
  - code: TS2307
    line: 2
    col: 35
    module: '../../../pages/connect-data-generic.search.page'
    message: 'Cannot find module \'../../../pages/connect-data-generic.search.page\' or its corresponding type declarations.'
actions:
  - 'Zweryfikuj relatywną ścieżkę i poziom zagnieżdżenia po refaktorze.'
  - 'Rozważ zamianę głębokiej ścieżki na alias `@c2004/*`.'
```

## Raw Log (truncated)

```text
../connect-manager/frontend/src/pages/connect-manager-activities.page.ts(2,39): error TS2307: Cannot find module '@c2004/frontend-host/modules/connect-manager/components/connect-table/connect-table.component' or its corresponding type declarations.
../connect-manager/frontend/src/pages/connect-manager-activities.page.ts(3,31): error TS2307: Cannot find module '@c2004/frontend-host/modules/connect-manager/components/icon.component' or its corresponding type declarations.
../connect-manager/frontend/src/pages/connect-manager-intervals.page.ts(2,39): error TS2307: Cannot find module '@c2004/frontend-host/modules/connect-manager/components/connect-table/connect-table.component' or its corresponding type declarations.
../connect-manager/frontend/src/pages/connect-manager-library.page.ts(3,37): error TS2307: Cannot find module '../services/tables-config.service' or its corresponding type declarations.
../connect-manager/frontend/src/pages/connect-manager-library.page.ts(4,31): error TS2307: Cannot find module '../services/dialog.service' or its corresponding type declarations.
../connect-manager/frontend/src/pages/connect-manager-library.page.ts(5,28): error TS2307: Cannot find module '@c2004/frontend-host/modules/connect-manager/utils/html.utils' or its corresponding type declarations.
../connect-manager/frontend/src/pages/connect-manager-library.page.ts(6,31): error TS2307: Cannot find module '@c2004/frontend-host/modules/connect-manager/utils/fetch.utils' or its corresponding type declarations.
../connect-manager/frontend/src/pages/connect-manager-library.page.ts(7,31): error TS2307: Cannot find module '@c2004/frontend-host/modules/connect-manager/components/icon.component' or its corresponding type declarations.
../connect-manager/frontend/src/pages/connect-manager-test-types.page.ts(6,8): error TS2307: Cannot find module './helpers/connect-manager-test-types' or its corresponding type declarations.
../connect-manager/frontend/src/pages/connect-manager-test-types.page.ts(7,31): error TS2307: Cannot find module '@c2004/frontend-host/modules/connect-manager/components/icon.component' or its corresponding type declarations.
../connect-manager/frontend/src/pages/connect-manager-variables.page.ts(4,24): error TS2307: Cannot find module '@c2004/frontend-host/modules/connect-manager/utils/logger' or its corresponding type declarations.
../connect-manager/frontend/src/pages/connect-manager-variables.page.ts(5,39): error TS2307: Cannot find module '@c2004/frontend-host/modules/connect-manager/components/connect-table' or its corresponding type declarations.
../connect-manager/frontend/src/pages/connect-manager-variables.page.ts(7,31): error TS2307: Cannot find module '@c2004/frontend-host/modules/connect-manager/components/icon.component' or its corresponding type declarations.
../connect-scenario/frontend/src/pages/connect-scenario-dsl-editor.page.ts(9,67): error TS2307: Cannot find module './helpers/cql-iframe' or its corresponding type declarations.
../connect-scenario/frontend/src/pages/connect-scenario-func-editor.page.ts(8,67): error TS2307: Cannot find module './helpers/cql-iframe' or its corresponding type declarations.
../connect-scenario/frontend/src/pages/connect-scenario-library-editor.page.ts(8,67): error TS2307: Cannot find module './helpers/cql-iframe' or its corresponding type declarations.
../connect-scenario/frontend/src/pages/connect-scenario-map-editor.page.ts(8,67): error TS2307: Cannot find module './helpers/cql-iframe' or its corresponding type declarations.
../connect-scenario/frontend/src/pages/connect-scenario-scenario-editor.page.ts(8,67): error TS2307: Cannot find module './helpers/cql-iframe' or its corresponding type declarations.
../connect-scenario/frontend/src/pages/connect-scenario-scenarios.page.ts(8,67): error TS2307: Cannot find module './helpers/cql-iframe' or its corresponding type declarations.
../connect-scenario/frontend/src/pages/connect-scenario-templates.page.ts(1,67): error TS2307: Cannot find module './helpers/cql-iframe' or its corresponding type declarations.
../connect-template/frontend/src/modules/connect-template/pages/template-editor.page.ts(1,103): error TS2307: Cannot find module '../../../pages/helpers/connect-template-iframe' or its corresponding type declarations.
../connect-template/frontend/src/modules/connect-template/pages/template-json.page.ts(6,28): error TS2307: Cannot find module '../../../utils/html.utils' or its corresponding type declarations.
../connect-template/frontend/src/modules/connect-template/pages/template-json.page.ts(7,31): error TS2307: Cannot find module '../../connect-config/cqrs/singleton' or its corresponding type declarations.
src/modules/connect-reports/pages/filter.page.ts(2,35): error TS2307: Cannot find module '../../../pages/connect-data-generic.search.page' or its corresponding type declarations.
src/modules/connect-workshop/pages-index.ts(3,36): error TS2307: Cannot find module './requests-search.page' or its corresponding type declarations.
src/modules/connect-workshop/pages-index.ts(4,40): error TS2307: Cannot find module './requests-new-request.page' or its corresponding type declarations.
src/modules/connect-workshop/pages-index.ts(5,36): error TS2307: Cannot find module './services-search.page' or its corresponding type declarations.
src/modules/connect-workshop/pages-index.ts(6,37): error TS2307: Cannot find module './transport-search.page' or its corresponding type declarations.
src/modules/connect-workshop/pages-index.ts(7,40): error TS2307: Cannot find module './dispositions-search.page' or its corresponding type declarations.
src/modules/connect-workshop/pages-index.ts(9,43): error TS2307: Cannot find module './generic.search.page' or its corresponding type declarations.
```
