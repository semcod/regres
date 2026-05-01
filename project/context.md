# System Architecture Analysis

## Overview

- **Project**: /home/tom/github/semcod/regres
- **Primary Language**: md
- **Languages**: md: 17, python: 13, yaml: 9, shell: 2, toml: 1
- **Analysis Mode**: static
- **Total Functions**: 1805
- **Total Classes**: 19
- **Modules**: 44
- **Entry Points**: 1610

## Architecture by Module

### SUMD
- **Functions**: 830
- **Classes**: 4
- **File**: `SUMD.md`

### project.map.toon
- **Functions**: 538
- **File**: `map.toon.yaml`

### SUMR
- **Functions**: 292
- **Classes**: 4
- **File**: `SUMR.md`

### regres.doctor_orchestrator
- **Functions**: 127
- **Classes**: 2
- **File**: `doctor_orchestrator.py`

### regres.regres
- **Functions**: 55
- **Classes**: 1
- **File**: `regres.py`

### regres.refactor
- **Functions**: 52
- **File**: `refactor.py`

### regres.defscan
- **Functions**: 45
- **Classes**: 1
- **File**: `defscan.py`

### regres.doctor_cli
- **Functions**: 30
- **File**: `doctor_cli.py`

### regres.import_error_toon_report
- **Functions**: 13
- **Classes**: 2
- **File**: `import_error_toon_report.py`

### regres.version_check
- **Functions**: 10
- **File**: `version_check.py`

### regres.regres_cli
- **Functions**: 9
- **File**: `regres_cli.py`

### regres.doctor_config
- **Functions**: 5
- **Classes**: 1
- **File**: `doctor_config.py`

### docs.DOCTOR
- **Functions**: 1
- **Classes**: 1
- **File**: `DOCTOR.md`

### docs.DEFSCAN
- **Functions**: 1
- **File**: `DEFSCAN.md`

### docs.README
- **Functions**: 1
- **File**: `README.md`

### regres.doctor_models
- **Functions**: 0
- **Classes**: 3
- **File**: `doctor_models.py`

## Key Entry Points

Main execution flows into the system:

### regres.regres_cli.main
- **Calls**: regres.version_check.check_version, argparse.ArgumentParser, parser.add_subparsers, subparsers.add_parser, regres_parser.add_argument, regres_parser.add_argument, regres_parser.add_argument, regres_parser.add_argument

### regres.doctor_orchestrator.DoctorOrchestrator._render_affected_files
- **Calls**: lines.append, lines.append, self._build_candidate_patch_index, report.get, lines.append, lines.append, None.join, lines.append

### regres.refactor.cmd_hotmap
> Mapa katalogów wg koncentracji podobnych plików.
Wskaźnik 'hotness' = liczba par podobnych / liczba plików w katalogu × 100.
Wysoki hotness = kandydat
- **Calls**: getattr, getattr, regres.refactor.iter_files, list, defaultdict, defaultdict, dir_file_count.items, hotmap.sort

### regres.doctor_orchestrator.DoctorOrchestrator.render_markdown
> Renderuje raport w formacie Markdown.
- **Calls**: lines.extend, lines.extend, lines.extend, lines.extend, lines.extend, lines.extend, enumerate, self._normalize_diagnoses

### regres.doctor_orchestrator.DoctorOrchestrator._render_decision_workflow
- **Calls**: lines.append, lines.append, enumerate, lines.append, lines.append, lines.append, lines.append, report.get

### regres.refactor.cmd_diff
> Unified diff dwóch plików. Opcja --normalize usuwa komentarze/stringi.
- **Calls**: Path, Path, regres.refactor.read_text, regres.refactor.read_text, getattr, regres.refactor.similarity_ratio, list, docs.DEFSCAN.print

### regres.refactor.cmd_dead
> Wykrywa symbole zdefiniowane ale prawdopodobnie nieużywane.
Definicje: pliki z --word.
Sprawdzenie: czy symbol pojawia się jako identyfikator w jakimk
- **Calls**: getattr, regres.refactor.iter_files, regres.refactor.iter_files, defaultdict, set, None.join, defined.items, dead.sort

### regres.refactor.cmd_similar
- **Calls**: getattr, regres.refactor.iter_files, list, range, pairs.sort, docs.DEFSCAN.print, docs.DEFSCAN.print, docs.DEFSCAN.print

### regres.doctor_orchestrator.DoctorOrchestrator._render_project_relation_map
- **Calls**: None.get, relation.get, lines.append, lines.append, lines.append, lines.append, lines.append, lines.append

### regres.doctor_orchestrator.DoctorOrchestrator._diagnose_import_issue
> Diagnozuje problem z importami i generuje plan naprawy.
- **Calls**: Diagnosis, module.startswith, module.replace, self._resolve_alias_target, commands.append, len, any, actions.append

### regres.refactor.cmd_cluster
- **Calls**: getattr, regres.refactor.iter_files, defaultdict, sorted, docs.DEFSCAN.print, getattr, regres.refactor.read_text, None.append

### regres.regres.main
- **Calls**: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument

### regres.doctor_orchestrator.DoctorOrchestrator._collect_git_relation_changes
- **Calls**: int, int, proc.stdout.splitlines, None.exists, getattr, getattr, subprocess.run, line.startswith

### regres.doctor_orchestrator.DoctorOrchestrator.analyze_page_registry_compliance
> Detect empty/misconfigured page registries that would recurse forever.

Reads `<module_path>/pages-index.ts`. If a `defaultPage` is configured
but the
- **Calls**: self._PAGES_INDEX_DEFAULT_PAGE_RE.search, m_default.group, self._PAGES_INDEX_PAGES_REF_RE.search, Diagnosis, entry.read_text, m_ref.group, re.compile, block_re.search

### regres.doctor_orchestrator.DoctorOrchestrator.analyze_runtime_console
> Analizuje log runtime (console/browser) pod kątem błędów UI.

Aktualnie wykrywa m.in. przypadki `SVG icon not found: ...` i tworzy
diagnozę, która pom
- **Calls**: self._RUNTIME_ICON_NOT_FOUND_RE.findall, sorted, sum, None.join, Diagnosis, log_path.exists, log_path.read_text, icon_name.strip

### regres.refactor.cmd_duplicates
- **Calls**: regres.refactor.iter_files, defaultdict, docs.DEFSCAN.print, enumerate, getattr, None.append, docs.DEFSCAN.print, docs.DEFSCAN.print

### regres.import_error_toon_report.main
- **Calls**: regres.version_check.check_version, regres.import_error_toon_report.parse_args, regres.import_error_toon_report.parse_ts_errors, ReportData, regres.import_error_toon_report.render_markdown, args.out_md.parent.mkdir, args.out_md.write_text, args.out_raw_log.parent.mkdir

### regres.doctor_orchestrator.DoctorOrchestrator.analyze_module_loader_compliance
> Detect *.module.ts entry files that won't load via the lazy registry.

The loader (host `frontend/src/modules/index.ts`) requires either a
`default` e
- **Calls**: bool, bool, self._ANY_CLASS_EXPORT_RE.findall, Diagnosis, entry.read_text, self._MODULE_DEFAULT_EXPORT_RE.search, self._MODULE_CLASS_EXPORT_RE.search, None.replace

### regres.doctor_orchestrator.DoctorOrchestrator._collect_defscan_context
- **Calls**: None.join, io.StringIO, output.strip, defscan.main, sys.stdout.getvalue, json.loads, lines.append, lines.append

### regres.refactor.cmd_find
- **Calls**: regres.refactor.iter_files, results.sort, docs.DEFSCAN.print, docs.DEFSCAN.print, docs.DEFSCAN.print, docs.DEFSCAN.print, regres.refactor.read_text, regres.refactor.count_word

### regres.refactor.cmd_symbols
> Indeks symboli (funkcje, klasy, selektory CSS, id HTML…).

--cross-lang   → ta sama nazwa symbolu w więcej niż jednym języku
--find-dups    → ta sama 
- **Calls**: getattr, getattr, regres.refactor.iter_files, regres.refactor._build_symbol_index, regres.refactor._render_file_symbols, getattr, getattr, sorted

### regres.refactor.cmd_wrappers
> Wykrywa cienkie pliki-wrappery / legacy shims / barrel files.
Heurystyki: krótkie + sys.path + dynamic import + barrel export + sygnatury tekstowe.
- **Calls**: getattr, regres.refactor.iter_files, results.sort, docs.DEFSCAN.print, docs.DEFSCAN.print, docs.DEFSCAN.print, docs.DEFSCAN.print, getattr

### regres.doctor_cli.main
> Main entry point for doctor CLI.
- **Calls**: regres.version_check.check_version, regres.doctor_cli._build_parser, parser.parse_args, None.resolve, regres.doctor_config.load_config, config.print_banner_to, DoctorOrchestrator, regres.doctor_cli._handle_auto_decision_flow

### regres.doctor_orchestrator.DoctorOrchestrator.analyze_from_url
> Analizuje moduł na podstawie URL.
- **Calls**: self._extract_module_name, self._resolve_module_path, diagnoses.extend, diagnoses.extend, diagnoses.extend, full_module_path.rglob, self._filter_actionable_diagnoses, self._build_url_fallback_diagnosis

### regres.doctor_orchestrator.DoctorOrchestrator._render_step_by_step_playbook
> Renderuje playbook krok po kroku.
- **Calls**: enumerate, lines.append, lines.append, diag.get, diag.get, sorted, lines.append, lines.append

### regres.refactor.cmd_report
> Generuje kompleksowy raport JSON dla LLM.
- **Calls**: getattr, getattr, getattr, docs.DEFSCAN.print, regres.refactor.iter_files, regres.refactor._collect_file_infos, regres.refactor._find_md5_duplicates, regres.refactor._find_name_clusters

### regres.doctor_orchestrator.DoctorOrchestrator.probe_vite_runtime
> GET a single source file from the Vite dev server, parse 500 errors.

Args:
  vite_base: e.g. "http://localhost:8100" (no trailing slash).
  file_rel:
- **Calls**: file_rel.replace, re.match, urllib.request.Request, m.group, vite_base.rstrip, re.finditer, self._VITE_FAILED_IMPORT_RE.search, urllib.request.urlopen

### regres.doctor_orchestrator.DoctorOrchestrator._render_apply_step
- **Calls**: lines.append, lines.append, lines.append, lines.append, lines.append, lines.append, lines.append, lines.append

### regres.doctor_orchestrator.DoctorOrchestrator._discover_module_path_map
> Discover module roots from filesystem layout.

Priority:
1) <repo>/<module>/frontend/src/modules/<module>
2) <repo>/frontend/src/modules/<module>
3) <
- **Calls**: self.scan_root.glob, flat_modules.exists, self.scan_root.glob, self.MODULE_PATH_MAP.items, None.replace, flat_modules.glob, full_path.exists, path.is_dir

### regres.doctor_orchestrator.DoctorOrchestrator._find_page_files
> Lokalizuje pliki strony pasujące do tokenu URL.

Two locations are searched:

1. Inside the resolved module path (recursive ``*.page.ts`` glob).
2. In
- **Calls**: page_token.lower, set, module_path.rglob, file_path.name.lower, name.replace, _consider, host_pages.is_dir, base.endswith

## Process Flows

Key execution flows identified:

### Flow 1: main
```
main [regres.regres_cli]
  └─ →> check_version
      └─> _get_pypi_version
      └─> _save_last_check
          └─> _read_env
```

### Flow 2: _render_affected_files
```
_render_affected_files [regres.doctor_orchestrator.DoctorOrchestrator]
```

### Flow 3: cmd_hotmap
```
cmd_hotmap [regres.refactor]
  └─> iter_files
```

### Flow 4: render_markdown
```
render_markdown [regres.doctor_orchestrator.DoctorOrchestrator]
```

### Flow 5: _render_decision_workflow
```
_render_decision_workflow [regres.doctor_orchestrator.DoctorOrchestrator]
```

### Flow 6: cmd_diff
```
cmd_diff [regres.refactor]
  └─> read_text
  └─> read_text
```

### Flow 7: cmd_dead
```
cmd_dead [regres.refactor]
  └─> iter_files
  └─> iter_files
```

### Flow 8: cmd_similar
```
cmd_similar [regres.refactor]
  └─> iter_files
```

### Flow 9: _render_project_relation_map
```
_render_project_relation_map [regres.doctor_orchestrator.DoctorOrchestrator]
```

### Flow 10: _diagnose_import_issue
```
_diagnose_import_issue [regres.doctor_orchestrator.DoctorOrchestrator]
```

## Key Classes

### regres.doctor_orchestrator.DoctorOrchestrator
> Orchestrator analizy i generator akcji.
- **Methods**: 123
- **Key Methods**: regres.doctor_orchestrator.DoctorOrchestrator.__init__, regres.doctor_orchestrator.DoctorOrchestrator.resolve_symlink, regres.doctor_orchestrator.DoctorOrchestrator._discover_module_path_map, regres.doctor_orchestrator.DoctorOrchestrator._get_module_path_map, regres.doctor_orchestrator.DoctorOrchestrator._get_url_route_module_hints, regres.doctor_orchestrator.DoctorOrchestrator.build_project_relation_map, regres.doctor_orchestrator.DoctorOrchestrator._init_relation_structure, regres.doctor_orchestrator.DoctorOrchestrator._collect_module_files, regres.doctor_orchestrator.DoctorOrchestrator._filter_scoped_files, regres.doctor_orchestrator.DoctorOrchestrator._analyze_imports

### regres.doctor_orchestrator._PatchIndexBuilder
> Helper class to build patch index file content.
- **Methods**: 4
- **Key Methods**: regres.doctor_orchestrator._PatchIndexBuilder.__init__, regres.doctor_orchestrator._PatchIndexBuilder.add_history_entry, regres.doctor_orchestrator._PatchIndexBuilder.add_manual_entry, regres.doctor_orchestrator._PatchIndexBuilder.write

### regres.defscan.Definition
> Pojedyncza definicja (klasa / funkcja / enum / interface / mixin).
- **Methods**: 3
- **Key Methods**: regres.defscan.Definition.__init__, regres.defscan.Definition.loc, regres.defscan.Definition.__repr__

### regres.doctor_config.DoctorConfig
> Resolved runtime configuration for one ``doctor`` invocation.
- **Methods**: 2
- **Key Methods**: regres.doctor_config.DoctorConfig.banner_lines, regres.doctor_config.DoctorConfig.print_banner_to

### docs.DOCTOR.DoctorOrchestrator
- **Methods**: 0

### regres.regres.GitCommit
- **Methods**: 0

### regres.doctor_models.FileAction
> Akcja na pliku.
- **Methods**: 0

### regres.doctor_models.ShellCommand
> Polecenie shell do wykonania.
- **Methods**: 0

### regres.doctor_models.Diagnosis
> Diagnoza problemu i plan naprawy.
- **Methods**: 0

### regres.import_error_toon_report.TsError
- **Methods**: 0

### regres.import_error_toon_report.ReportData
- **Methods**: 0

### SUMR.DoctorOrchestrator
- **Methods**: 0

### SUMR._PatchIndexBuilder
- **Methods**: 0

### SUMR.GitCommit
- **Methods**: 0

### SUMR.Definition
- **Methods**: 0

### SUMD.DoctorOrchestrator
- **Methods**: 0

### SUMD._PatchIndexBuilder
- **Methods**: 0

### SUMD.GitCommit
- **Methods**: 0

### SUMD.Definition
- **Methods**: 0

## Data Transformation Functions

Key functions that process and transform data:

### regres.regres.parse_numstat_block
- **Output to**: None.split, a.isdigit, d.isdigit, len, int

### regres.doctor_config._parse_env_file
> Parse a ``KEY=VALUE`` file. Ignores blanks and ``#`` comments.
- **Output to**: text.splitlines, path.is_file, path.read_text, raw.strip, line.partition

### regres.version_check._parse_version
- **Output to**: tuple, int, v.split, x.isdigit

### regres.refactor._format_imports
> Format imports list for toon output.
- **Output to**: None.strip, None.strip, None.join, regres.refactor._sanitize, str

### regres.refactor._format_preview
> Format preview text for toon output.
- **Output to**: regres.refactor._sanitize, len, isinstance

### regres.refactor.build_parser
- **Output to**: argparse.ArgumentParser, p.add_argument, p.add_argument, p.add_argument, p.add_subparsers

### regres.import_error_toon_report.parse_args
- **Output to**: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument

### regres.import_error_toon_report.parse_ts_errors
- **Output to**: log_text.splitlines, TS_ERROR_RE.match, m.group, m.group, MISSING_MODULE_RE.search

### regres.defscan._build_argument_parser
> Build and return the argument parser for defscan.
- **Output to**: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument

### SUMR._parse_history_output

### SUMR._parse_commit_line

### SUMR._parse_ts_errors

### SUMR._validate_errors

### SUMR._render_validate_step

### SUMR.parse_numstat_block

### SUMR._format_imports

### SUMR._format_preview

### SUMR.build_parser

### SUMR._build_argument_parser

### SUMR._build_parser

### project.map.toon._build_argument_parser

### project.map.toon._build_parser

### project.map.toon._parse_env_file

### project.map.toon.parse_args

### project.map.toon.parse_ts_errors

## Behavioral Patterns

### recursion__collect_tree_paths
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: regres.regres._collect_tree_paths

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `regres.defscan.render_text` - 55 calls
- `regres.regres_cli.main` - 54 calls
- `regres.refactor.build_parser` - 49 calls
- `regres.refactor.cmd_hotmap` - 42 calls
- `regres.defscan.render_seed_text` - 42 calls
- `regres.doctor_orchestrator.DoctorOrchestrator.render_markdown` - 39 calls
- `regres.defscan.render_markdown` - 35 calls
- `regres.regres.llm_context_packet` - 33 calls
- `regres.defscan.extract_go` - 32 calls
- `regres.refactor.cmd_diff` - 31 calls
- `regres.import_error_toon_report.to_toon_global_payload` - 31 calls
- `regres.regres.trace_name_and_hash_candidates` - 28 calls
- `regres.refactor.cmd_dead` - 28 calls
- `regres.refactor.cmd_similar` - 26 calls
- `regres.regres.analyze_file` - 25 calls
- `regres.refactor.cmd_cluster` - 25 calls
- `regres.regres.exact_and_near_duplicates` - 24 calls
- `regres.regres.main` - 24 calls
- `regres.regres.resolve_target_file` - 23 calls
- `regres.import_error_toon_report.render_markdown` - 23 calls
- `regres.regres.resolve_import_historical` - 22 calls
- `regres.doctor_orchestrator.DoctorOrchestrator.analyze_page_registry_compliance` - 22 calls
- `regres.doctor_orchestrator.DoctorOrchestrator.analyze_runtime_console` - 22 calls
- `regres.regres.resolve_import_at_commit` - 21 calls
- `regres.regres.render_markdown` - 20 calls
- `regres.refactor.wrapper_score` - 20 calls
- `regres.refactor.cmd_duplicates` - 20 calls
- `regres.import_error_toon_report.main` - 20 calls
- `regres.doctor_orchestrator.DoctorOrchestrator.analyze_module_loader_compliance` - 20 calls
- `regres.refactor.cmd_find` - 19 calls
- `regres.refactor.cmd_symbols` - 19 calls
- `regres.refactor.cmd_wrappers` - 19 calls
- `regres.defscan.render_seed_markdown` - 19 calls
- `regres.doctor_cli.main` - 19 calls
- `regres.doctor_orchestrator.DoctorOrchestrator.analyze_from_url` - 19 calls
- `regres.regres.check_imports_at_commit` - 18 calls
- `regres.regres.classify_problem` - 18 calls
- `regres.refactor.cmd_report` - 18 calls
- `regres.doctor_orchestrator.DoctorOrchestrator.probe_vite_runtime` - 18 calls
- `regres.regres.analyze_evolution` - 17 calls

## System Interactions

How components interact:

```mermaid
graph TD
    main --> check_version
    main --> ArgumentParser
    main --> add_subparsers
    main --> add_parser
    main --> add_argument
    _render_affected_fil --> append
    _render_affected_fil --> _build_candidate_pat
    _render_affected_fil --> get
    cmd_hotmap --> getattr
    cmd_hotmap --> iter_files
    cmd_hotmap --> list
    cmd_hotmap --> defaultdict
    render_markdown --> extend
    _render_decision_wor --> append
    _render_decision_wor --> enumerate
    cmd_diff --> Path
    cmd_diff --> read_text
    cmd_diff --> getattr
    cmd_dead --> getattr
    cmd_dead --> iter_files
    cmd_dead --> defaultdict
    cmd_dead --> set
    cmd_similar --> getattr
    cmd_similar --> iter_files
    cmd_similar --> list
    cmd_similar --> range
    cmd_similar --> sort
    _render_project_rela --> get
    _render_project_rela --> append
    _diagnose_import_iss --> Diagnosis
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.