<!-- code2docs:start --># regres

![version](https://img.shields.io/badge/version-0.1.0-blue) ![python](https://img.shields.io/badge/python-%3E%3D3.11-blue) ![coverage](https://img.shields.io/badge/coverage-unknown-lightgrey) ![functions](https://img.shields.io/badge/functions-951-green)
> **951** functions | **21** classes | **41** files | CC̄ = 5.8

> Auto-generated project documentation from source code analysis.

**Author:** Tom Sapletta  
**License:** Apache-2.0[(LICENSE)](./LICENSE)  
**Repository:** [https://github.com/semcod/regres](https://github.com/semcod/regres)

## Installation

### From PyPI

```bash
pip install regres
```

### From Source

```bash
git clone https://github.com/semcod/regres
cd regres
pip install -e .
```


## Quick Start

### CLI Usage

```bash
# Generate full documentation for your project
regres ./my-project

# Only regenerate README
regres ./my-project --readme-only

# Preview what would be generated (no file writes)
regres ./my-project --dry-run

# Check documentation health
regres check ./my-project

# Sync — regenerate only changed modules
regres sync ./my-project
```

### Python API

```python
from regres import generate_readme, generate_docs, Code2DocsConfig

# Quick: generate README
generate_readme("./my-project")

# Full: generate all documentation
config = Code2DocsConfig(project_name="mylib", verbose=True)
docs = generate_docs("./my-project", config=config)
```




## Architecture

```
regres/
├── SUMR
├── goal
├── Makefile
├── SUMD
├── pyproject
├── tree
├── CHANGELOG
├── project
├── README
    ├── REGRES
    ├── REFACTOR
    ├── DOCTOR
    ├── import-error-toon-report
    ├── DEFSCAN
    ├── README
        ├── import-error-toon-report
    ├── import-error-toon-report
        ├── toon
            ├── toon
    ├── regres
    ├── doctor_models
    ├── doctor
    ├── doctor_cli
├── regres/
    ├── refactor
    ├── import_error_toon_report
    ├── regres_cli
    ├── doctor_orchestrator
    ├── context
        ├── toon
        ├── toon
    ├── README
        ├── toon
    ├── prompt
        ├── toon
    ├── calls
        ├── toon
    ├── defscan
```

## API Overview

### Classes

- **`GitCommit`** — —
- **`DoctorOrchestrator`** — —
- **`Definition`** — —
- **`FileAction`** — —
- **`ShellCommand`** — —
- **`Diagnosis`** — —
- **`GitCommit`** — —
- **`DoctorOrchestrator`** — —
- **`Definition`** — —
- **`FileAction`** — —
- **`ShellCommand`** — —
- **`Diagnosis`** — —
- **`DoctorOrchestrator`** — —
- **`GitCommit`** — —
- **`FileAction`** — Akcja na pliku.
- **`ShellCommand`** — Polecenie shell do wykonania.
- **`Diagnosis`** — Diagnoza problemu i plan naprawy.
- **`TsError`** — —
- **`ReportData`** — —
- **`DoctorOrchestrator`** — Orchestrator analizy i generator akcji.
- **`Definition`** — Pojedyncza definicja (klasa / funkcja / enum / interface / mixin).

### Functions

- `run_git()` — —
- `find_repo_root()` — —
- `resolve_target_file()` — —
- `to_rel()` — —
- `safe_read_text()` — —
- `sha256_of_file()` — —
- `content_metrics()` — —
- `resolve_local_import()` — —
- `extract_local_imports()` — —
- `resolve_import_at_commit()` — —
- `check_imports_at_commit()` — —
- `find_last_working_commit()` — —
- `search_missing_in_history()` — —
- `analyze_regression()` — —
- `extract_symbols()` — —
- `track_filename_history()` — —
- `find_current_locations()` — —
- `classify_problem()` — —
- `dependency_tree()` — —
- `reverse_references()` — —
- `exact_and_near_duplicates()` — —
- `trace_name_and_hash_candidates()` — —
- `parse_numstat_block()` — —
- `file_lineage()` — —
- `changed_files_for_commit()` — —
- `references_in_recent_commits()` — —
- `file_content_at_commit()` — —
- `resolve_import_historical()` — —
- `historical_dependency_tree()` — —
- `analyze_evolution()` — —
- `find_last_good_version()` — —
- `llm_context_packet()` — —
- `render_markdown()` — —
- `analyze_file()` — —
- `main()` — —
- `analyze_from_url()` — —
- `analyze_import_errors()` — —
- `analyze_duplicates()` — —
- `analyze_git_history()` — —
- `analyze_with_defscan()` — —
- `analyze_with_refactor()` — —
- `apply_fixes()` — —
- `generate_llm_diagnosis()` — —
- `generate_report()` — —
- `iter_files()` — —
- `read_text()` — —
- `md5_file()` — —
- `count_word()` — —
- `line_count()` — —
- `similarity_ratio()` — —
- `normalize_code()` — —
- `rel()` — —
- `name_prefix()` — —
- `extract_imports()` — —
- `extract_symbols_ast()` — —
- `extract_symbols_regex()` — —
- `get_symbols()` — —
- `wrapper_score()` — —
- `cmd_find()` — —
- `cmd_duplicates()` — —
- `cmd_similar()` — —
- `cmd_symbols()` — —
- `cmd_wrappers()` — —
- `cmd_dead()` — —
- `cmd_diff()` — —
- `cmd_hotmap()` — —
- `cmd_cluster()` — —
- `cmd_deps()` — —
- `to_json_toon()` — —
- `cmd_report()` — —
- `build_parser()` — —
- `c()` — —
- `sim()` — —
- `extract_python()` — —
- `extract_typescript()` — —
- `extract_go()` — —
- `extract_rust()` — —
- `extract_file()` — —
- `load_gitignore()` — —
- `scan()` — —
- `compare_seed_to_all()` — —
- `analyse_group()` — —
- `classify_similarity()` — —
- `render_text()` — —
- `render_seed_text()` — —
- `render_seed_markdown()` — —
- `render_seed_json()` — —
- `render_json()` — —
- `loc()` — —
- `c()` — —
- `sim()` — —
- `extract_python()` — —
- `extract_typescript()` — —
- `extract_go()` — —
- `extract_rust()` — —
- `extract_file()` — —
- `load_gitignore()` — —
- `scan()` — —
- `compare_seed_to_all()` — —
- `analyse_group()` — —
- `classify_similarity()` — —
- `render_text()` — —
- `render_markdown()` — —
- `render_seed_text()` — —
- `render_seed_markdown()` — —
- `render_seed_json()` — —
- `render_json()` — —
- `main()` — —
- `toon_quote()` — —
- `parse_args()` — —
- `run_typecheck()` — —
- `normalize_file_rel()` — —
- `parse_ts_errors()` — —
- `suggestions_for_error()` — —
- `grouped_errors()` — —
- `metrics()` — —
- `to_toon_block_legacy()` — —
- `to_toon_global_payload()` — —
- `to_toon_compact_per_file()` — —
- `iter_files()` — —
- `read_text()` — —
- `md5_file()` — —
- `count_word()` — —
- `line_count()` — —
- `similarity_ratio()` — —
- `normalize_code()` — —
- `rel()` — —
- `name_prefix()` — —
- `extract_imports()` — —
- `extract_symbols_ast()` — —
- `extract_symbols_regex()` — —
- `get_symbols()` — —
- `wrapper_score()` — —
- `cmd_find()` — —
- `cmd_duplicates()` — —
- `cmd_similar()` — —
- `cmd_symbols()` — —
- `cmd_wrappers()` — —
- `cmd_dead()` — —
- `cmd_diff()` — —
- `cmd_hotmap()` — —
- `cmd_cluster()` — —
- `cmd_deps()` — —
- `to_json_toon()` — —
- `cmd_report()` — —
- `build_parser()` — —
- `run_git()` — —
- `find_repo_root()` — —
- `resolve_target_file()` — —
- `to_rel()` — —
- `safe_read_text()` — —
- `sha256_of_file()` — —
- `content_metrics()` — —
- `resolve_local_import()` — —
- `extract_local_imports()` — —
- `resolve_import_at_commit()` — —
- `check_imports_at_commit()` — —
- `find_last_working_commit()` — —
- `search_missing_in_history()` — —
- `analyze_regression()` — —
- `extract_symbols()` — —
- `track_filename_history()` — —
- `find_current_locations()` — —
- `classify_problem()` — —
- `dependency_tree()` — —
- `reverse_references()` — —
- `exact_and_near_duplicates()` — —
- `trace_name_and_hash_candidates()` — —
- `parse_numstat_block()` — —
- `file_lineage()` — —
- `changed_files_for_commit()` — —
- `references_in_recent_commits()` — —
- `file_content_at_commit()` — —
- `resolve_import_historical()` — —
- `historical_dependency_tree()` — —
- `analyze_evolution()` — —
- `find_last_good_version()` — —
- `llm_context_packet()` — —
- `analyze_file()` — —
- `test_ext_lang_mappings()` — —
- `test_ignored_dirs()` — —
- `test_c_without_color()` — —
- `test_normalize_strips_comments()` — —
- `test_normalize_collapses_whitespace()` — —
- `test_definition_repr()` — —
- `test_definition_similarity_identical()` — —
- `test_definition_similarity_different()` — —
- `test_classify_similarity_identical()` — —
- `test_classify_similarity_high()` — —
- `test_classify_similarity_medium()` — —
- `test_classify_similarity_low()` — —
- `test_load_gitignore_missing()` — —
- `test_load_gitignore_reads_patterns()` — —
- `test_path_ignored_by_gitignore()` — —
- `test_file_action_defaults()` — —
- `test_file_action_full()` — —
- `test_shell_command_defaults()` — —
- `test_diagnosis()` — —
- `test_import_doctor()` — —
- `test_import_doctor_main()` — —
- `test_ts_error_re_matches()` — —
- `test_ts_error_re_no_match_for_plain_text()` — —
- `test_missing_module_re()` — —
- `test_exported_member_re()` — —
- `test_toon_quote_escapes()` — —
- `test_parse_ts_errors_basic()` — —
- `test_parse_ts_errors_filters_code()` — —
- `test_parse_ts_errors_empty()` — —
- `test_suggestions_ts2307_alias()` — —
- `test_suggestions_ts2307_relative()` — —
- `test_suggestions_ts2305()` — —
- `test_suggestions_unknown_code()` — —
- `test_grouped_errors()` — —
- `test_metrics()` — —
- `test_metrics_empty()` — —
- `test_to_toon_block_legacy()` — —
- `test_to_toon_global_payload()` — —
- `test_to_toon_compact_per_file()` — —
- `test_ts_error_dataclass()` — —
- `test_report_data()` — —
- `test_default_extensions_contains_py()` — —
- `test_ignored_dirs_contains_node_modules()` — —
- `test_count_word_case_insensitive()` — —
- `test_count_word_case_sensitive()` — —
- `test_line_count()` — —
- `test_similarity_ratio_identical()` — —
- `test_similarity_ratio_empty()` — —
- `test_similarity_ratio_different()` — —
- `test_normalize_code_strips_comments()` — —
- `test_rel_path()` — —
- `test_name_prefix()` — —
- `test_extract_imports_python()` — —
- `test_extract_imports_ts()` — —
- `test_extract_symbols_regex_python()` — —
- `test_extract_symbols_regex_ts()` — —
- `test_wrapper_score_empty()` — —
- `test_wrapper_score_high_for_reexport()` — —
- `test_md5_file_consistent()` — —
- `test_read_text_reads_utf8()` — —
- `test_placeholder()` — —
- `test_import()` — —
- `test_import_regres_module()` — —
- `test_import_refactor_module()` — —
- `test_import_defscan_module()` — —
- `test_import_import_error_toon_report()` — —
- `test_regres_cli_module_exists()` — —
- `test_regres_cli_import()` — —
- `test_import_error_toon_report_main_signature()` — —
- `test_regres_cli_help()` — —
- `test_regres_cli_doctor_help()` — —
- `test_regres_cli_defscan_help()` — —
- `test_regres_cli_refactor_help()` — —
- `test_regres_cli_doctor_on_self()` — —
- `test_git_commit_fields()` — —
- `test_find_repo_root_finds_git()` — —
- `test_find_repo_root_raises_when_no_git()` — —
- `test_dedupe_paths()` — —
- `test_check_absolute_path_existing()` — —
- `test_check_absolute_path_missing()` — —
- `test_check_relative_paths()` — —
- `test_resolve_single_or_error()` — —
- `test_resolve_single_or_error_raises()` — —
- `test_to_rel()` — —
- `test_safe_read_text_utf8()` — —
- `test_sha256_of_file_consistent()` — —
- `test_content_metrics()` — —
- `test_extract_local_imports()` — —
- `test_extract_symbols_ts()` — —
- `test_parse_numstat_block()` — —
- `test_parse_numstat_block_empty()` — —
- `analyze_from_url()` — —
- `analyze_import_errors()` — —
- `analyze_duplicates()` — —
- `analyze_git_history()` — —
- `analyze_with_defscan()` — —
- `analyze_with_refactor()` — —
- `apply_fixes()` — —
- `generate_llm_diagnosis()` — —
- `generate_report()` — —
- `loc()` — —
- `analyze_custom_metric()` — —
- `print()` — —
- `generate_readme()` — —
- `run_git(args, cwd)` — —
- `find_repo_root(start)` — —
- `resolve_target_file(file_arg, cwd, repo_root, scan_root)` — —
- `to_rel(path, repo_root)` — —
- `safe_read_text(path)` — —
- `sha256_of_file(path)` — —
- `content_metrics(text, path)` — —
- `resolve_local_import(raw_import, file_path, repo_root)` — —
- `extract_local_imports(text)` — —
- `resolve_import_at_commit(raw_import, file_rel, repo_root, commit_sha)` — —
- `check_imports_at_commit(repo_root, rel_path, commit_sha)` — —
- `find_last_working_commit(repo_root, rel_path, commits)` — —
- `search_missing_in_history(repo_root, missing_imports, file_rel)` — —
- `analyze_regression(repo_root, rel_path, commits, current_text)` — —
- `extract_symbols(text)` — —
- `track_filename_history(repo_root, basename)` — —
- `find_current_locations(repo_root, basename)` — —
- `classify_problem(repo_root, target_rel, current_text, evolution)` — —
- `dependency_tree(file_path, repo_root, max_depth)` — —
- `reverse_references(file_path, repo_root, scan_root, max_hits)` — —
- `exact_and_near_duplicates(file_path, repo_root, scan_root, near_threshold)` — —
- `trace_name_and_hash_candidates(file_path, repo_root, scan_root, max_candidates)` — —
- `parse_numstat_block(lines)` — —
- `file_lineage(repo_root, rel_file, max_commits)` — —
- `changed_files_for_commit(repo_root, commit_sha, limit)` — —
- `references_in_recent_commits(repo_root, commits, max_commits)` — —
- `file_content_at_commit(repo_root, rel_path, commit_sha)` — —
- `resolve_import_historical(raw_import, file_rel, repo_root, commit_sha)` — —
- `historical_dependency_tree(repo_root, rel_path, commit_sha, max_depth)` — —
- `analyze_evolution(repo_root, rel_path, commits, current_text)` — —
- `find_last_good_version(evolution, min_lines, min_similarity, max_results)` — —
- `llm_context_packet(report)` — —
- `render_markdown(report)` — —
- `analyze_file(target_file, scan_root, max_commits, tree_depth)` — —
- `main()` — —
- `main()` — Main entry point for doctor CLI.
- `iter_files(root, extensions, word_filter, case_sensitive)` — —
- `read_text(p)` — —
- `md5_file(p)` — —
- `count_word(text, word, case_sensitive)` — —
- `line_count(text)` — —
- `similarity_ratio(a, b)` — —
- `normalize_code(text, ext)` — Normalizuje kod przed porównaniem:
- `rel(p, root)` — —
- `name_prefix(name, depth)` — —
- `extract_imports(text)` — —
- `extract_symbols_ast(text, filepath)` — Dla Pythona używa modułu ast — precyzyjniejsze niż regex.
- `extract_symbols_regex(text, ext)` — Wyciąga symbole wg wzorców dla danego języka.
- `get_symbols(p, text)` — —
- `wrapper_score(text)` — Heurystyczna ocena czy plik jest wrapperem/shimem.
- `cmd_find(args, root)` — —
- `cmd_duplicates(args, root)` — —
- `cmd_similar(args, root)` — —
- `cmd_symbols(args, root)` — Indeks symboli (funkcje, klasy, selektory CSS, id HTML…).
- `cmd_wrappers(args, root)` — Wykrywa cienkie pliki-wrappery / legacy shims / barrel files.
- `cmd_dead(args, root)` — Wykrywa symbole zdefiniowane ale prawdopodobnie nieużywane.
- `cmd_diff(args, root)` — Unified diff dwóch plików. Opcja --normalize usuwa komentarze/stringi.
- `cmd_hotmap(args, root)` — Mapa katalogów wg koncentracji podobnych plików.
- `cmd_cluster(args, root)` — —
- `cmd_deps(args, root)` — —
- `to_json_toon(data)` — Konwertuje dict do formatu toon (YAML-like).
- `cmd_report(args, root)` — Generuje kompleksowy raport JSON dla LLM.
- `build_parser()` — —
- `main()` — —
- `toon_quote(value)` — —
- `parse_args()` — —
- `run_typecheck(cwd, command)` — —
- `normalize_file_rel(raw_file, cwd)` — —
- `parse_ts_errors(log_text, cwd, include_codes)` — —
- `suggestions_for_error(err)` — —
- `grouped_errors(errors)` — —
- `metrics(errors)` — —
- `to_toon_block_legacy(file_rel, errs, max_errors)` — —
- `to_toon_global_payload(report, scan_root, max_files, max_errors_per_file)` — —
- `to_toon_compact_per_file(grouped, max_files, max_errors)` — —
- `render_markdown(report, scan_root, max_files, max_errors_per_file)` — —
- `main()` — —
- `main()` — —
- `main()` — —
- `c()` — —
- `sim()` — —
- `extract_python()` — —
- `extract_typescript()` — —
- `extract_go()` — —
- `extract_rust()` — —
- `extract_file()` — —
- `load_gitignore()` — —
- `scan()` — —
- `compare_seed_to_all()` — —
- `analyse_group()` — —
- `classify_similarity()` — —
- `render_text()` — —
- `render_markdown()` — —
- `render_seed_text()` — —
- `render_seed_markdown()` — —
- `render_seed_json()` — —
- `render_json()` — —
- `iter_files()` — —
- `read_text()` — —
- `md5_file()` — —
- `count_word()` — —
- `line_count()` — —
- `similarity_ratio()` — —
- `normalize_code()` — —
- `rel()` — —
- `name_prefix()` — —
- `extract_imports()` — —
- `extract_symbols_ast()` — —
- `extract_symbols_regex()` — —
- `get_symbols()` — —
- `wrapper_score()` — —
- `cmd_find()` — —
- `cmd_duplicates()` — —
- `cmd_similar()` — —
- `cmd_symbols()` — —
- `cmd_wrappers()` — —
- `cmd_dead()` — —
- `cmd_diff()` — —
- `cmd_hotmap()` — —
- `cmd_cluster()` — —
- `cmd_deps()` — —
- `to_json_toon()` — —
- `cmd_report()` — —
- `build_parser()` — —
- `run_git()` — —
- `find_repo_root()` — —
- `resolve_target_file()` — —
- `to_rel()` — —
- `safe_read_text()` — —
- `sha256_of_file()` — —
- `content_metrics()` — —
- `resolve_local_import()` — —
- `extract_local_imports()` — —
- `resolve_import_at_commit()` — —
- `check_imports_at_commit()` — —
- `find_last_working_commit()` — —
- `search_missing_in_history()` — —
- `analyze_regression()` — —
- `extract_symbols()` — —
- `track_filename_history()` — —
- `find_current_locations()` — —
- `classify_problem()` — —
- `dependency_tree()` — —
- `reverse_references()` — —
- `exact_and_near_duplicates()` — —
- `trace_name_and_hash_candidates()` — —
- `parse_numstat_block()` — —
- `file_lineage()` — —
- `changed_files_for_commit()` — —
- `references_in_recent_commits()` — —
- `file_content_at_commit()` — —
- `resolve_import_historical()` — —
- `historical_dependency_tree()` — —
- `analyze_evolution()` — —
- `find_last_good_version()` — —
- `llm_context_packet()` — —
- `analyze_file()` — —
- `toon_quote()` — —
- `parse_args()` — —
- `run_typecheck()` — —
- `normalize_file_rel()` — —
- `parse_ts_errors()` — —
- `suggestions_for_error()` — —
- `grouped_errors()` — —
- `metrics()` — —
- `to_toon_block_legacy()` — —
- `to_toon_global_payload()` — —
- `to_toon_compact_per_file()` — —
- `print()` — —
- `analyze_custom_metric()` — —
- `generate_readme()` — —
- `analyze_from_url()` — —
- `analyze_import_errors()` — —
- `analyze_duplicates()` — —
- `analyze_git_history()` — —
- `analyze_with_defscan()` — —
- `analyze_with_refactor()` — —
- `apply_fixes()` — —
- `generate_llm_diagnosis()` — —
- `generate_report()` — —
- `loc()` — —
- `test_ext_lang_mappings()` — —
- `test_ignored_dirs()` — —
- `test_c_without_color()` — —
- `test_normalize_strips_comments()` — —
- `test_normalize_collapses_whitespace()` — —
- `test_definition_repr()` — —
- `test_definition_similarity_identical()` — —
- `test_definition_similarity_different()` — —
- `test_classify_similarity_identical()` — —
- `test_classify_similarity_high()` — —
- `test_classify_similarity_medium()` — —
- `test_classify_similarity_low()` — —
- `test_load_gitignore_missing()` — —
- `test_load_gitignore_reads_patterns()` — —
- `test_path_ignored_by_gitignore()` — —
- `test_file_action_defaults()` — —
- `test_file_action_full()` — —
- `test_shell_command_defaults()` — —
- `test_diagnosis()` — —
- `test_import_doctor()` — —
- `test_import_doctor_main()` — —
- `test_ts_error_re_matches()` — —
- `test_ts_error_re_no_match_for_plain_text()` — —
- `test_missing_module_re()` — —
- `test_exported_member_re()` — —
- `test_toon_quote_escapes()` — —
- `test_parse_ts_errors_basic()` — —
- `test_parse_ts_errors_filters_code()` — —
- `test_parse_ts_errors_empty()` — —
- `test_suggestions_ts2307_alias()` — —
- `test_suggestions_ts2307_relative()` — —
- `test_suggestions_ts2305()` — —
- `test_suggestions_unknown_code()` — —
- `test_grouped_errors()` — —
- `test_metrics()` — —
- `test_metrics_empty()` — —
- `test_to_toon_block_legacy()` — —
- `test_to_toon_global_payload()` — —
- `test_to_toon_compact_per_file()` — —
- `test_ts_error_dataclass()` — —
- `test_report_data()` — —
- `test_default_extensions_contains_py()` — —
- `test_ignored_dirs_contains_node_modules()` — —
- `test_count_word_case_insensitive()` — —
- `test_count_word_case_sensitive()` — —
- `test_line_count()` — —
- `test_similarity_ratio_identical()` — —
- `test_similarity_ratio_empty()` — —
- `test_similarity_ratio_different()` — —
- `test_normalize_code_strips_comments()` — —
- `test_rel_path()` — —
- `test_name_prefix()` — —
- `test_extract_imports_python()` — —
- `test_extract_imports_ts()` — —
- `test_extract_symbols_regex_python()` — —
- `test_extract_symbols_regex_ts()` — —
- `test_wrapper_score_empty()` — —
- `test_wrapper_score_high_for_reexport()` — —
- `test_md5_file_consistent()` — —
- `test_read_text_reads_utf8()` — —
- `test_placeholder()` — —
- `test_import()` — —
- `test_import_regres_module()` — —
- `test_import_refactor_module()` — —
- `test_import_defscan_module()` — —
- `test_import_import_error_toon_report()` — —
- `test_regres_cli_module_exists()` — —
- `test_regres_cli_import()` — —
- `test_import_error_toon_report_main_signature()` — —
- `test_regres_cli_help()` — —
- `test_regres_cli_doctor_help()` — —
- `test_regres_cli_defscan_help()` — —
- `test_regres_cli_refactor_help()` — —
- `test_regres_cli_doctor_on_self()` — —
- `test_git_commit_fields()` — —
- `test_find_repo_root_finds_git()` — —
- `test_find_repo_root_raises_when_no_git()` — —
- `test_dedupe_paths()` — —
- `test_check_absolute_path_existing()` — —
- `test_check_absolute_path_missing()` — —
- `test_check_relative_paths()` — —
- `test_resolve_single_or_error()` — —
- `test_resolve_single_or_error_raises()` — —
- `test_to_rel()` — —
- `test_safe_read_text_utf8()` — —
- `test_sha256_of_file_consistent()` — —
- `test_content_metrics()` — —
- `test_extract_local_imports()` — —
- `test_extract_symbols_ts()` — —
- `test_parse_numstat_block()` — —
- `test_parse_numstat_block_empty()` — —
- `c(text, code)` — —
- `sim(a, b)` — Podobieństwo ciał (0–100%).
- `extract_python(path)` — Używa modułu ast — precyzyjne wyodrębnienie z zachowaniem linii.
- `extract_typescript(path)` — —
- `extract_go(path)` — —
- `extract_rust(path)` — —
- `extract_file(path)` — —
- `load_gitignore(root)` — Wczytuje wzorce z ``root/.gitignore``. Zwraca listę (pattern, is_negation).
- `scan(root, name_filter, kind_filter, only_within)` — Zwraca słownik: base_name → [Definition, ...]
- `compare_seed_to_all(seed_defs, all_defs, min_sim, skip_same_name)` — Dla każdej definicji z seed znajduje wszystkie definicje w all_defs
- `analyse_group(defs)` — Dla listy definicji o tej samej nazwie oblicza macierz podobieństwa
- `classify_similarity(pct)` — Zwraca (etykieta, kolor_ANSI).
- `render_text(groups, root, min_sim, show_body_lines)` — —
- `render_markdown(groups, root, min_sim)` — —
- `render_seed_text(results, root, top_per_seed, show_body_lines)` — —
- `render_seed_markdown(results, root, top_per_seed)` — —
- `render_seed_json(results, root)` — —
- `render_json(groups, root)` — —
- `main()` — —


## Project Structure

📄 `.regres.import-error-toon-report`
📄 `CHANGELOG`
📄 `Makefile`
📄 `README`
📄 `SUMD` (431 functions, 7 classes)
📄 `SUMR` (197 functions, 7 classes)
📄 `docs.DEFSCAN` (1 functions)
📄 `docs.DOCTOR` (1 functions, 1 classes)
📄 `docs.README` (1 functions)
📄 `docs.REFACTOR`
📄 `docs.REGRES`
📄 `docs.import-error-toon-report`
📄 `goal`
📄 `project`
📄 `project.README`
📄 `project.analysis.toon`
📄 `project.calls`
📄 `project.calls.toon`
📄 `project.context`
📄 `project.duplication.toon`
📄 `project.evolution.toon`
📄 `project.map.toon` (1030 functions)
📄 `project.project.toon`
📄 `project.prompt`
📄 `pyproject`
📦 `regres`
📄 `regres.defscan` (43 functions, 1 classes)
📄 `regres.doctor`
📄 `regres.doctor_cli` (8 functions)
📄 `regres.doctor_models` (3 classes)
📄 `regres.doctor_orchestrator` (49 functions, 1 classes)
📄 `regres.import_error_toon_report` (13 functions, 2 classes)
📄 `regres.refactor` (52 functions)
📄 `regres.regres` (55 functions, 1 classes)
📄 `regres.regres_cli` (1 functions)
📄 `scripts.import-error-toon-report`
📄 `testql-scenarios.generated-cli-tests.testql.toon`
📄 `tree`

## Requirements

- Python >= >=3.11


## Contributing

**Contributors:**
- Tom Softreck <tom@sapletta.com>
- Tom Sapletta <tom-sapletta-com@users.noreply.github.com>

We welcome contributions! Open an issue or pull request to get started.
### Development Setup

```bash
# Clone the repository
git clone https://github.com/semcod/regres
cd regres

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```


<!-- code2docs:end -->