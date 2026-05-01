<!-- code2docs:start --># regres

![version](https://img.shields.io/badge/version-0.1.0-blue) ![python](https://img.shields.io/badge/python-%3E%3D3.11-blue) ![coverage](https://img.shields.io/badge/coverage-unknown-lightgrey) ![functions](https://img.shields.io/badge/functions-1931-green)
> **1931** functions | **19** classes | **47** files | CC̄ = 5.6

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
├── TODO
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
        ├── connect-test-reports-doctor
    ├── import-error-toon-report
            ├── c2004-security-settings-baseline
            ├── c2004-preanalysis-predeploy
        ├── toon
            ├── toon
    ├── regres
    ├── doctor_config
    ├── doctor_models
    ├── doctor
    ├── version_check
    ├── doctor_cli
├── regres/
    ├── refactor
    ├── import_error_toon_report
    ├── regres_cli
    ├── defscan
    ├── doctor_orchestrator
    ├── prompt
        ├── toon
        ├── toon
        ├── toon
    ├── context
        ├── toon
    ├── README
    ├── calls
        ├── toon
```

## API Overview

### Classes

- **`DoctorOrchestrator`** — —
- **`GitCommit`** — —
- **`Definition`** — —
- **`DoctorOrchestrator`** — —
- **`GitCommit`** — —
- **`Definition`** — —
- **`DoctorOrchestrator`** — —
- **`GitCommit`** — —
- **`DoctorConfig`** — Resolved runtime configuration for one ``doctor`` invocation.
- **`FileAction`** — Akcja na pliku.
- **`ShellCommand`** — Polecenie shell do wykonania.
- **`Diagnosis`** — Diagnoza problemu i plan naprawy.
- **`TsError`** — —
- **`ReportData`** — —
- **`Definition`** — Pojedyncza definicja (klasa / funkcja / enum / interface / mixin).
- **`DoctorOrchestrator`** — Orchestrator analizy i generator akcji.

### Functions

- `resolve_symlink()` — —
- `build_project_relation_map()` — —
- `analyze_from_url()` — —
- `analyze_dependency_chain()` — —
- `probe_vite_runtime()` — —
- `analyze_module_loader_compliance()` — —
- `analyze_page_registry_compliance()` — —
- `analyze_page_implementations()` — —
- `analyze_runtime_console()` — —
- `analyze_import_errors()` — —
- `analyze_duplicates()` — —
- `analyze_git_history()` — —
- `analyze_with_defscan()` — —
- `analyze_with_refactor()` — —
- `apply_fixes()` — —
- `generate_llm_diagnosis()` — —
- `generate_report()` — —
- `render_markdown()` — —
- `reset_analysis_plan()` — —
- `add_plan_step()` — —
- `update_last_plan_step()` — —
- `set_analysis_context()` — —
- `summarize_affected_files()` — —
- `generate_patch_scripts()` — —
- `collect_structure_snapshot()` — —
- `collect_preliminary_refactor_proposals()` — —
- `add_history_entry()` — —
- `add_manual_entry()` — —
- `write()` — —
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
- `main()` — —
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
- `load_config()` — —
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
- `check_version()` — —
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
- `test_build_parser()` — —
- `test_parser_scan_root()` — —
- `test_parser_all()` — —
- `test_parser_url()` — —
- `test_parser_llm()` — —
- `test_parser_import_log()` — —
- `test_parser_defscan_report()` — —
- `test_parser_apply()` — —
- `test_parser_dry_run()` — —
- `test_parser_git_history()` — —
- `test_parser_out_md()` — —
- `test_parser_out_json()` — —
- `test_parser_runtime_log()` — —
- `test_parser_defscan_scan()` — —
- `test_parser_refactor_scan()` — —
- `test_parser_multiple_args()` — —
- `test_refresh_import_no_frontend()` — —
- `test_refresh_import_with_frontend_subprocess_failure()` — —
- `test_refresh_import_timeout()` — —
- `test_handle_url_mode_without_llm()` — —
- `test_handle_url_mode_with_llm()` — —
- `test_handle_url_mode_with_llm_saves_to_file()` — —
- `test_handle_url_mode_with_apply()` — —
- `test_handle_import_errors_with_log()` — —
- `test_handle_import_errors_without_log_all_flag()` — —
- `test_handle_import_errors_with_git_history()` — —
- `test_handle_defscan_refactor_with_report()` — —
- `test_handle_defscan_refactor_with_scan()` — —
- `test_handle_defscan_refactor_with_refactor_scan()` — —
- `test_handle_defscan_refactor_none()` — —
- `test_save_report_to_stdout()` — —
- `test_save_report_to_json()` — —
- `test_save_report_to_md()` — —
- `test_save_report_to_both_formats()` — —
- `test_refresh_import_error_log_success()` — —
- `test_refresh_import_error_log_no_frontend()` — —
- `test_refresh_import_error_log_subprocess_failure()` — —
- `test_refresh_import_error_log_timeout()` — —
- `test_refresh_import_error_log_file_not_found()` — —
- `test_handle_import_errors_with_subprocess_mock()` — —
- `test_handle_import_errors_without_frontend()` — —
- `test_handle_defscan_refactor_subprocess_mock()` — —
- `test_handle_auto_decision_flow_runtime_log()` — —
- `test_full_workflow_with_all_mocks()` — —
- `test_derive_vite_base_from_explicit_arg()` — —
- `test_derive_vite_base_from_url()` — —
- `test_derive_vite_base_no_url()` — —
- `test_derive_vite_base_invalid_url()` — —
- `test_derive_vite_base_https_url()` — —
- `test_load_config_uses_defaults_and_creates_env_file()` — —
- `test_load_config_priority_env_file_over_default()` — —
- `test_load_config_priority_environ_over_file()` — —
- `test_load_config_priority_cli_overrides_environ()` — —
- `test_load_config_invalid_int_falls_back_to_default()` — —
- `test_load_config_print_banner_parsing()` — —
- `test_banner_output_mentions_active_window_and_help()` — —
- `test_banner_disabled_emits_nothing()` — —
- `run_doctor_command()` — —
- `test_doctor_cli_help()` — —
- `test_doctor_cli_version()` — —
- `test_url_mode_module_not_found()` — —
- `test_url_mode_with_existing_module()` — —
- `test_url_mode_with_markdown_output()` — —
- `test_url_mode_both_outputs()` — —
- `test_import_error_with_log_file()` — —
- `test_import_error_with_nonexistent_log()` — —
- `test_defscan_with_report_file()` — —
- `test_all_mode_basic()` — —
- `test_all_mode_with_markdown()` — —
- `test_patch_generation_with_dir()` — —
- `test_no_patches_flag()` — —
- `test_invalid_scan_root()` — —
- `test_concurrent_runs()` — —
- `test_real_world_scenario_missing_imports()` — —
- `test_real_world_scenario_module_analysis()` — —
- `test_analysis_plan_structure()` — —
- `test_diagnosis_structure()` — —
- `test_file_action_all_action_types()` — —
- `test_file_action_empty_path()` — —
- `test_file_action_none_path()` — —
- `test_file_action_with_special_characters()` — —
- `test_file_action_target_without_reason()` — —
- `test_file_action_reason_without_target()` — —
- `test_file_action_equality()` — —
- `test_shell_command()` — —
- `test_shell_command_with_cwd()` — —
- `test_shell_command_empty_command()` — —
- `test_shell_command_empty_description()` — —
- `test_shell_command_none_description()` — —
- `test_shell_command_multiline()` — —
- `test_shell_command_with_special_chars()` — —
- `test_shell_command_with_quotes()` — —
- `test_diagnosis_defaults()` — —
- `test_diagnosis_with_actions()` — —
- `test_diagnosis_with_shell_commands()` — —
- `test_diagnosis_with_both_actions_and_commands()` — —
- `test_diagnosis_confidence_bounds()` — —
- `test_diagnosis_severity_levels()` — —
- `test_diagnosis_problem_types()` — —
- `test_diagnosis_empty_summary()` — —
- `test_diagnosis_empty_nlp_description()` — —
- `test_diagnosis_multiple_file_actions()` — —
- `test_diagnosis_multiple_shell_commands()` — —
- `test_diagnosis_unicode_in_fields()` — —
- `test_diagnosis_long_description()` — —
- `test_diagnosis_confidence_out_of_bounds()` — —
- `test_diagnosis_immutability_of_lists()` — —
- `test_diagnosis_with_none_confidence()` — —
- `test_init_sets_scan_root()` — —
- `test_module_path_map_non_empty()` — —
- `test_module_path_map_contains_all_modules()` — —
- `test_reset_analysis_plan()` — —
- `test_add_plan_step_basic()` — —
- `test_add_plan_step_with_status()` — —
- `test_add_plan_step_with_details()` — —
- `test_set_analysis_context()` — —
- `test_analyze_from_url_valid_module()` — —
- `test_analyze_from_url_invalid_url()` — —
- `test_analyze_from_url_module_not_exists()` — —
- `test_analyze_import_errors_missing_log()` — —
- `test_analyze_import_errors_with_valid_log()` — —
- `test_analyze_import_errors_empty_log()` — —
- `test_analyze_runtime_console_missing_log()` — —
- `test_analyze_runtime_console_icon_not_found()` — —
- `test_extract_page_token_for_nested_module_path()` — —
- `test_find_page_files_falls_back_to_host_iframe_wrapper()` — —
- `test_page_stub_detects_generic_migration_phrase()` — —
- `test_analyze_duplicates_missing_report()` — —
- `test_analyze_duplicates_valid_report()` — —
- `test_analyze_duplicates_invalid_json()` — —
- `test_analyze_git_history_no_git()` — —
- `test_analyze_git_history_with_git()` — —
- `test_analyze_git_history_timeout()` — —
- `test_analyze_with_defscan_subprocess_failure()` — —
- `test_analyze_with_defscan_timeout()` — —
- `test_analyze_with_refactor_subprocess_failure()` — —
- `test_analyze_with_refactor_with_wrappers()` — —
- `test_apply_fixes_empty()` — —
- `test_apply_fixes_with_modify_action()` — —
- `test_apply_fixes_with_delete_action()` — —
- `test_apply_fixes_with_shell_command()` — —
- `test_apply_fixes_error_handling()` — —
- `test_generate_report_empty()` — —
- `test_generate_report_with_diagnoses()` — —
- `test_generate_report_with_analysis_plan()` — —
- `test_generate_report_with_analysis_context()` — —
- `test_render_markdown_empty()` — —
- `test_render_markdown_with_diagnoses()` — —
- `test_render_markdown_with_file_actions()` — —
- `test_render_markdown_with_shell_commands()` — —
- `test_render_markdown_severity_emojis()` — —
- `test_render_markdown_with_decision_workflow()` — —
- `test_generate_llm_diagnosis()` — —
- `test_generate_llm_diagnosis_sections()` — —
- `test_extract_module_name()` — —
- `test_resolve_module_path()` — —
- `test_import_exists_in_source()` — —
- `test_import_exists_in_source_commented()` — —
- `test_resolve_alias_target()` — —
- `test_parse_ts_errors()` — —
- `test_validate_errors()` — —
- `test_extract_missing_modules()` — —
- `test_find_main_location()` — —
- `test_find_main_location_no_shared()` — —
- `test_analyze_history_patterns()` — —
- `test_analyze_history_patterns_no_moves()` — —
- `test_module_loader_compliance_passes_with_module_class()` — —
- `test_module_loader_compliance_passes_with_default_export()` — —
- `test_module_loader_compliance_flags_view_only_export()` — —
- `test_module_loader_compliance_returns_none_when_entry_missing()` — —
- `test_page_registry_compliance_passes_when_default_present()` — —
- `test_page_registry_compliance_flags_empty_registry()` — —
- `test_page_registry_compliance_flags_default_not_in_registry()` — —
- `test_page_registry_compliance_returns_none_when_no_index()` — —
- `test_check_page_stub_indicators_placeholder_text()` — —
- `test_check_page_stub_indicators_short_stub()` — —
- `test_check_page_stub_indicators_empty_render()` — —
- `test_check_page_stub_indicators_normal_page()` — —
- `test_detect_content_regression()` — —
- `test_detect_content_regression_no_regression()` — —
- `test_detect_content_regression_with_placeholder()` — —
- `test_detect_content_regression_empty_history()` — —
- `test_add_backup_candidate_none()` — —
- `test_add_backup_candidate_with_path()` — —
- `test_add_history_candidates_empty()` — —
- `test_add_history_candidates_with_data()` — —
- `test_resolve_symlink_regular_file()` — —
- `test_resolve_symlink_with_symlink()` — —
- `test_resolve_symlink_nonexistent()` — —
- `test_map_workspace_to_frontend_matches_pattern()` — —
- `test_map_workspace_to_frontend_no_match()` — —
- `test_map_workspace_to_frontend_different_module_names()` — —
- `test_find_symlink_base_no_symlink()` — —
- `test_find_symlink_base_with_symlinked_dir()` — —
- `test_extract_relative_imports_double_quoted()` — —
- `test_extract_relative_imports_single_quoted()` — —
- `test_extract_relative_imports_skips_absolute()` — —
- `test_extract_relative_imports_deduplicates()` — —
- `test_extract_relative_imports_empty()` — —
- `test_resolve_relative_import_finds_ts_file()` — —
- `test_resolve_relative_import_not_found()` — —
- `test_resolve_relative_import_with_explicit_extension()` — —
- `test_resolve_relative_import_maps_workspace_to_frontend()` — —
- `test_analyze_dependency_chain_no_imports()` — —
- `test_analyze_dependency_chain_broken_import()` — —
- `test_analyze_dependency_chain_resolved_import()` — —
- `test_analyze_dependency_chain_missing_file()` — —
- `test_analyze_module_loader_compliance_no_entry_file()` — —
- `test_analyze_module_loader_compliance_has_default_export()` — —
- `test_analyze_module_loader_compliance_has_module_class()` — —
- `test_analyze_module_loader_compliance_no_module_export()` — —
- `test_fingerprint_page_content_extracts_heading()` — —
- `test_fingerprint_page_content_known_marker()` — —
- `test_fingerprint_page_content_empty()` — —
- `test_fingerprint_page_content_max_length()` — —
- `test_filter_actionable_diagnoses_keeps_with_file_actions()` — —
- `test_filter_actionable_diagnoses_keeps_import_error()` — —
- `test_filter_actionable_diagnoses_drops_empty()` — —
- `test_filter_actionable_diagnoses_mixed()` — —
- `test_build_url_fallback_diagnosis_returns_diagnosis()` — —
- `test_build_url_fallback_diagnosis_includes_candidate_file()` — —
- `test_probe_vite_runtime_transport_error()` — —
- `test_probe_vite_runtime_ok_response()` — —
- `test_analyze_runtime_console_no_icon_lines()` — —
- `test_analyze_runtime_console_single_icon()` — —
- `test_analyze_runtime_console_many_icons_severity_high()` — —
- `test_analyze_runtime_console_deduplicates_icons()` — —
- `test_extract_page_token_module_name_only()` — —
- `test_extract_page_token_hyphenated_subpage()` — —
- `test_extract_page_token_empty_path()` — —
- `test_extract_page_token_unrelated_module()` — —
- `test_collect_structure_snapshot_empty_dir()` — —
- `test_collect_structure_snapshot_returns_ts_files()` — —
- `test_collect_structure_snapshot_respects_max_entries()` — —
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
- `resolve_symlink()` — —
- `build_project_relation_map()` — —
- `analyze_from_url()` — —
- `analyze_dependency_chain()` — —
- `probe_vite_runtime()` — —
- `analyze_module_loader_compliance()` — —
- `analyze_page_registry_compliance()` — —
- `analyze_page_implementations()` — —
- `analyze_runtime_console()` — —
- `analyze_import_errors()` — —
- `analyze_duplicates()` — —
- `analyze_git_history()` — —
- `analyze_with_defscan()` — —
- `analyze_with_refactor()` — —
- `apply_fixes()` — —
- `generate_llm_diagnosis()` — —
- `generate_report()` — —
- `reset_analysis_plan()` — —
- `add_plan_step()` — —
- `update_last_plan_step()` — —
- `set_analysis_context()` — —
- `summarize_affected_files()` — —
- `generate_patch_scripts()` — —
- `collect_structure_snapshot()` — —
- `collect_preliminary_refactor_proposals()` — —
- `add_history_entry()` — —
- `add_manual_entry()` — —
- `write()` — —
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
- `load_config(scan_root, cli_overrides)` — Build a :class:`DoctorConfig` honoring the resolution order described in
- `check_version(local_version)` — Check PyPI for a newer version and prompt the user to update.
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
- `load_config()` — —
- `check_version()` — —
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
- `analyze_custom_metric()` — —
- `print()` — —
- `generate_readme()` — —
- `resolve_symlink()` — —
- `build_project_relation_map()` — —
- `analyze_from_url()` — —
- `analyze_dependency_chain()` — —
- `probe_vite_runtime()` — —
- `analyze_module_loader_compliance()` — —
- `analyze_page_registry_compliance()` — —
- `analyze_page_implementations()` — —
- `analyze_runtime_console()` — —
- `analyze_import_errors()` — —
- `analyze_duplicates()` — —
- `analyze_git_history()` — —
- `analyze_with_defscan()` — —
- `analyze_with_refactor()` — —
- `apply_fixes()` — —
- `generate_llm_diagnosis()` — —
- `generate_report()` — —
- `reset_analysis_plan()` — —
- `add_plan_step()` — —
- `update_last_plan_step()` — —
- `set_analysis_context()` — —
- `summarize_affected_files()` — —
- `generate_patch_scripts()` — —
- `collect_structure_snapshot()` — —
- `collect_preliminary_refactor_proposals()` — —
- `add_history_entry()` — —
- `add_manual_entry()` — —
- `write()` — —
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
- `test_build_parser()` — —
- `test_parser_scan_root()` — —
- `test_parser_all()` — —
- `test_parser_url()` — —
- `test_parser_llm()` — —
- `test_parser_import_log()` — —
- `test_parser_defscan_report()` — —
- `test_parser_apply()` — —
- `test_parser_dry_run()` — —
- `test_parser_git_history()` — —
- `test_parser_out_md()` — —
- `test_parser_out_json()` — —
- `test_parser_runtime_log()` — —
- `test_parser_defscan_scan()` — —
- `test_parser_refactor_scan()` — —
- `test_parser_multiple_args()` — —
- `test_refresh_import_no_frontend()` — —
- `test_refresh_import_with_frontend_subprocess_failure()` — —
- `test_refresh_import_timeout()` — —
- `test_handle_url_mode_without_llm()` — —
- `test_handle_url_mode_with_llm()` — —
- `test_handle_url_mode_with_llm_saves_to_file()` — —
- `test_handle_url_mode_with_apply()` — —
- `test_handle_import_errors_with_log()` — —
- `test_handle_import_errors_without_log_all_flag()` — —
- `test_handle_import_errors_with_git_history()` — —
- `test_handle_defscan_refactor_with_report()` — —
- `test_handle_defscan_refactor_with_scan()` — —
- `test_handle_defscan_refactor_with_refactor_scan()` — —
- `test_handle_defscan_refactor_none()` — —
- `test_save_report_to_stdout()` — —
- `test_save_report_to_json()` — —
- `test_save_report_to_md()` — —
- `test_save_report_to_both_formats()` — —
- `test_refresh_import_error_log_success()` — —
- `test_refresh_import_error_log_no_frontend()` — —
- `test_refresh_import_error_log_subprocess_failure()` — —
- `test_refresh_import_error_log_timeout()` — —
- `test_refresh_import_error_log_file_not_found()` — —
- `test_handle_import_errors_with_subprocess_mock()` — —
- `test_handle_import_errors_without_frontend()` — —
- `test_handle_defscan_refactor_subprocess_mock()` — —
- `test_handle_auto_decision_flow_runtime_log()` — —
- `test_full_workflow_with_all_mocks()` — —
- `test_derive_vite_base_from_explicit_arg()` — —
- `test_derive_vite_base_from_url()` — —
- `test_derive_vite_base_no_url()` — —
- `test_derive_vite_base_invalid_url()` — —
- `test_derive_vite_base_https_url()` — —
- `test_load_config_uses_defaults_and_creates_env_file()` — —
- `test_load_config_priority_env_file_over_default()` — —
- `test_load_config_priority_environ_over_file()` — —
- `test_load_config_priority_cli_overrides_environ()` — —
- `test_load_config_invalid_int_falls_back_to_default()` — —
- `test_load_config_print_banner_parsing()` — —
- `test_banner_output_mentions_active_window_and_help()` — —
- `test_banner_disabled_emits_nothing()` — —
- `run_doctor_command()` — —
- `test_doctor_cli_help()` — —
- `test_doctor_cli_version()` — —
- `test_url_mode_module_not_found()` — —
- `test_url_mode_with_existing_module()` — —
- `test_url_mode_with_markdown_output()` — —
- `test_url_mode_both_outputs()` — —
- `test_import_error_with_log_file()` — —
- `test_import_error_with_nonexistent_log()` — —
- `test_defscan_with_report_file()` — —
- `test_all_mode_basic()` — —
- `test_all_mode_with_markdown()` — —
- `test_patch_generation_with_dir()` — —
- `test_no_patches_flag()` — —
- `test_invalid_scan_root()` — —
- `test_concurrent_runs()` — —
- `test_real_world_scenario_missing_imports()` — —
- `test_real_world_scenario_module_analysis()` — —
- `test_analysis_plan_structure()` — —
- `test_diagnosis_structure()` — —
- `test_file_action_all_action_types()` — —
- `test_file_action_empty_path()` — —
- `test_file_action_none_path()` — —
- `test_file_action_with_special_characters()` — —
- `test_file_action_target_without_reason()` — —
- `test_file_action_reason_without_target()` — —
- `test_file_action_equality()` — —
- `test_shell_command()` — —
- `test_shell_command_with_cwd()` — —
- `test_shell_command_empty_command()` — —
- `test_shell_command_empty_description()` — —
- `test_shell_command_none_description()` — —
- `test_shell_command_multiline()` — —
- `test_shell_command_with_special_chars()` — —
- `test_shell_command_with_quotes()` — —
- `test_diagnosis_defaults()` — —
- `test_diagnosis_with_actions()` — —
- `test_diagnosis_with_shell_commands()` — —
- `test_diagnosis_with_both_actions_and_commands()` — —
- `test_diagnosis_confidence_bounds()` — —
- `test_diagnosis_severity_levels()` — —
- `test_diagnosis_problem_types()` — —
- `test_diagnosis_empty_summary()` — —
- `test_diagnosis_empty_nlp_description()` — —
- `test_diagnosis_multiple_file_actions()` — —
- `test_diagnosis_multiple_shell_commands()` — —
- `test_diagnosis_unicode_in_fields()` — —
- `test_diagnosis_long_description()` — —
- `test_diagnosis_confidence_out_of_bounds()` — —
- `test_diagnosis_immutability_of_lists()` — —
- `test_diagnosis_with_none_confidence()` — —
- `test_init_sets_scan_root()` — —
- `test_module_path_map_non_empty()` — —
- `test_module_path_map_contains_all_modules()` — —
- `test_reset_analysis_plan()` — —
- `test_add_plan_step_basic()` — —
- `test_add_plan_step_with_status()` — —
- `test_add_plan_step_with_details()` — —
- `test_set_analysis_context()` — —
- `test_analyze_from_url_valid_module()` — —
- `test_analyze_from_url_invalid_url()` — —
- `test_analyze_from_url_module_not_exists()` — —
- `test_analyze_import_errors_missing_log()` — —
- `test_analyze_import_errors_with_valid_log()` — —
- `test_analyze_import_errors_empty_log()` — —
- `test_analyze_runtime_console_missing_log()` — —
- `test_analyze_runtime_console_icon_not_found()` — —
- `test_extract_page_token_for_nested_module_path()` — —
- `test_find_page_files_falls_back_to_host_iframe_wrapper()` — —
- `test_page_stub_detects_generic_migration_phrase()` — —
- `test_analyze_duplicates_missing_report()` — —
- `test_analyze_duplicates_valid_report()` — —
- `test_analyze_duplicates_invalid_json()` — —
- `test_analyze_git_history_no_git()` — —
- `test_analyze_git_history_with_git()` — —
- `test_analyze_git_history_timeout()` — —
- `test_analyze_with_defscan_subprocess_failure()` — —
- `test_analyze_with_defscan_timeout()` — —
- `test_analyze_with_refactor_subprocess_failure()` — —
- `test_analyze_with_refactor_with_wrappers()` — —
- `test_apply_fixes_empty()` — —
- `test_apply_fixes_with_modify_action()` — —
- `test_apply_fixes_with_delete_action()` — —
- `test_apply_fixes_with_shell_command()` — —
- `test_apply_fixes_error_handling()` — —
- `test_generate_report_empty()` — —
- `test_generate_report_with_diagnoses()` — —
- `test_generate_report_with_analysis_plan()` — —
- `test_generate_report_with_analysis_context()` — —
- `test_render_markdown_empty()` — —
- `test_render_markdown_with_diagnoses()` — —
- `test_render_markdown_with_file_actions()` — —
- `test_render_markdown_with_shell_commands()` — —
- `test_render_markdown_severity_emojis()` — —
- `test_render_markdown_with_decision_workflow()` — —
- `test_generate_llm_diagnosis()` — —
- `test_generate_llm_diagnosis_sections()` — —
- `test_extract_module_name()` — —
- `test_resolve_module_path()` — —
- `test_import_exists_in_source()` — —
- `test_import_exists_in_source_commented()` — —
- `test_resolve_alias_target()` — —
- `test_parse_ts_errors()` — —
- `test_validate_errors()` — —
- `test_extract_missing_modules()` — —
- `test_find_main_location()` — —
- `test_find_main_location_no_shared()` — —
- `test_analyze_history_patterns()` — —
- `test_analyze_history_patterns_no_moves()` — —
- `test_module_loader_compliance_passes_with_module_class()` — —
- `test_module_loader_compliance_passes_with_default_export()` — —
- `test_module_loader_compliance_flags_view_only_export()` — —
- `test_module_loader_compliance_returns_none_when_entry_missing()` — —
- `test_page_registry_compliance_passes_when_default_present()` — —
- `test_page_registry_compliance_flags_empty_registry()` — —
- `test_page_registry_compliance_flags_default_not_in_registry()` — —
- `test_page_registry_compliance_returns_none_when_no_index()` — —
- `test_check_page_stub_indicators_placeholder_text()` — —
- `test_check_page_stub_indicators_short_stub()` — —
- `test_check_page_stub_indicators_empty_render()` — —
- `test_check_page_stub_indicators_normal_page()` — —
- `test_detect_content_regression()` — —
- `test_detect_content_regression_no_regression()` — —
- `test_detect_content_regression_with_placeholder()` — —
- `test_detect_content_regression_empty_history()` — —
- `test_add_backup_candidate_none()` — —
- `test_add_backup_candidate_with_path()` — —
- `test_add_history_candidates_empty()` — —
- `test_add_history_candidates_with_data()` — —
- `test_resolve_symlink_regular_file()` — —
- `test_resolve_symlink_with_symlink()` — —
- `test_resolve_symlink_nonexistent()` — —
- `test_map_workspace_to_frontend_matches_pattern()` — —
- `test_map_workspace_to_frontend_no_match()` — —
- `test_map_workspace_to_frontend_different_module_names()` — —
- `test_find_symlink_base_no_symlink()` — —
- `test_find_symlink_base_with_symlinked_dir()` — —
- `test_extract_relative_imports_double_quoted()` — —
- `test_extract_relative_imports_single_quoted()` — —
- `test_extract_relative_imports_skips_absolute()` — —
- `test_extract_relative_imports_deduplicates()` — —
- `test_extract_relative_imports_empty()` — —
- `test_resolve_relative_import_finds_ts_file()` — —
- `test_resolve_relative_import_not_found()` — —
- `test_resolve_relative_import_with_explicit_extension()` — —
- `test_resolve_relative_import_maps_workspace_to_frontend()` — —
- `test_analyze_dependency_chain_no_imports()` — —
- `test_analyze_dependency_chain_broken_import()` — —
- `test_analyze_dependency_chain_resolved_import()` — —
- `test_analyze_dependency_chain_missing_file()` — —
- `test_analyze_module_loader_compliance_no_entry_file()` — —
- `test_analyze_module_loader_compliance_has_default_export()` — —
- `test_analyze_module_loader_compliance_has_module_class()` — —
- `test_analyze_module_loader_compliance_no_module_export()` — —
- `test_fingerprint_page_content_extracts_heading()` — —
- `test_fingerprint_page_content_known_marker()` — —
- `test_fingerprint_page_content_empty()` — —
- `test_fingerprint_page_content_max_length()` — —
- `test_filter_actionable_diagnoses_keeps_with_file_actions()` — —
- `test_filter_actionable_diagnoses_keeps_import_error()` — —
- `test_filter_actionable_diagnoses_drops_empty()` — —
- `test_filter_actionable_diagnoses_mixed()` — —
- `test_build_url_fallback_diagnosis_returns_diagnosis()` — —
- `test_build_url_fallback_diagnosis_includes_candidate_file()` — —
- `test_probe_vite_runtime_transport_error()` — —
- `test_probe_vite_runtime_ok_response()` — —
- `test_analyze_runtime_console_no_icon_lines()` — —
- `test_analyze_runtime_console_single_icon()` — —
- `test_analyze_runtime_console_many_icons_severity_high()` — —
- `test_analyze_runtime_console_deduplicates_icons()` — —
- `test_extract_page_token_module_name_only()` — —
- `test_extract_page_token_hyphenated_subpage()` — —
- `test_extract_page_token_empty_path()` — —
- `test_extract_page_token_unrelated_module()` — —
- `test_collect_structure_snapshot_empty_dir()` — —
- `test_collect_structure_snapshot_returns_ts_files()` — —
- `test_collect_structure_snapshot_respects_max_entries()` — —
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


## Project Structure

📄 `.regres.connect-test-reports-doctor`
📄 `.regres.import-error-toon-report`
📄 `.windsurf.workflows.c2004-preanalysis-predeploy`
📄 `.windsurf.workflows.c2004-security-settings-baseline`
📄 `CHANGELOG`
📄 `Makefile`
📄 `README`
📄 `SUMD` (830 functions, 4 classes)
📄 `SUMR` (292 functions, 4 classes)
📄 `TODO`
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
📄 `project.map.toon` (1878 functions)
📄 `project.project.toon`
📄 `project.prompt`
📄 `pyproject`
📦 `regres`
📄 `regres.defscan` (45 functions, 1 classes)
📄 `regres.doctor`
📄 `regres.doctor_cli` (30 functions)
📄 `regres.doctor_config` (5 functions, 1 classes)
📄 `regres.doctor_models` (3 classes)
📄 `regres.doctor_orchestrator` (127 functions, 2 classes)
📄 `regres.import_error_toon_report` (13 functions, 2 classes)
📄 `regres.refactor` (52 functions)
📄 `regres.regres` (55 functions, 1 classes)
📄 `regres.regres_cli` (9 functions)
📄 `regres.version_check` (10 functions)
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