# regres

Regression/import diagnostics helpers with TOON reports

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Interfaces](#interfaces)
- [Workflows](#workflows)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Release Management (`goal.yaml`)](#release-management-goalyaml)
- [Makefile Targets](#makefile-targets)
- [Code Analysis](#code-analysis)
- [Source Map](#source-map)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Intent](#intent)

## Metadata

- **name**: `regres`
- **version**: `0.1.47`
- **python_requires**: `>=3.11`
- **license**: {'text': 'Apache-2.0'}
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Makefile, testql(1), app.doql.less, goal.yaml, src(11 mod), project/(2 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: regres;
  version: 0.1.47;
}

interface[type="cli"] {
  framework: argparse;
}
interface[type="cli"] page[name="regres"] {

}

workflow[name="install"] {
  trigger: manual;
  step-1: run cmd=echo "📦 Installing sumd...";
  step-2: run cmd=if command -v uv > /dev/null 2>&1; then \;
  step-3: run cmd=uv pip install -e .; \;
  step-4: run cmd=else \;
  step-5: run cmd=pip install -e .; \;
  step-6: run cmd=fi;
  step-7: run cmd=echo "✅ Installation completed!";
}

workflow[name="install-dev"] {
  trigger: manual;
  step-1: run cmd=echo "📦 Installing sumd with dev dependencies...";
  step-2: run cmd=if command -v uv > /dev/null 2>&1; then \;
  step-3: run cmd=uv pip install -e ".[dev]"; \;
  step-4: run cmd=else \;
  step-5: run cmd=pip install -e ".[dev]"; \;
  step-6: run cmd=fi;
  step-7: run cmd=echo "✅ Dev installation completed!";
}

workflow[name="test"] {
  trigger: manual;
  step-1: run cmd=echo "🧪 Running tests...";
  step-2: run cmd=.venv/bin/python -m pytest tests/ -v --tb=short;
}

workflow[name="test-cov"] {
  trigger: manual;
  step-1: run cmd=echo "🧪 Running tests with coverage...";
  step-2: run cmd=.venv/bin/python -m pytest tests/ -v --cov=sumd --cov-report=term-missing --cov-report=json;
}

workflow[name="lint"] {
  trigger: manual;
  step-1: run cmd=echo "🔍 Running linting with ruff...";
  step-2: run cmd=.venv/bin/python -m ruff check sumd/;
  step-3: run cmd=.venv/bin/python -m ruff check tests/;
}

workflow[name="format"] {
  trigger: manual;
  step-1: run cmd=echo "📝 Formatting code with ruff...";
  step-2: run cmd=.venv/bin/python -m ruff format sumd/;
  step-3: run cmd=.venv/bin/python -m ruff format tests/;
}

workflow[name="clean"] {
  trigger: manual;
  step-1: run cmd=echo "🧹 Cleaning temporary files...";
  step-2: run cmd=find . -type f -name "*.pyc" -delete;
  step-3: run cmd=find . -type d -name "__pycache__" -delete;
  step-4: run cmd=find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true;
  step-5: run cmd=rm -rf build/ dist/ .coverage htmlcov/ coverage.json;
  step-6: run cmd=echo "✅ Clean completed!";
}

workflow[name="publish"] {
  trigger: manual;
  step-1: run cmd=echo "📦 Publishing to PyPI...";
  step-2: run cmd=command -v .venv/bin/twine > /dev/null 2>&1 || (.venv/bin/pip install --upgrade twine build);
  step-3: run cmd=rm -rf dist/ build/ *.egg-info/;
  step-4: run cmd=.venv/bin/python -m build;
  step-5: run cmd=.venv/bin/twine check dist/*;
  step-6: run cmd=echo "⚡ Ready to upload. Run: make publish-confirm to upload to PyPI";
}

workflow[name="publish-confirm"] {
  trigger: manual;
  step-1: run cmd=echo "🚀 Uploading to PyPI...";
  step-2: run cmd=.venv/bin/twine upload dist/*;
}

workflow[name="publish-test"] {
  trigger: manual;
  step-1: run cmd=echo "📦 Publishing to TestPyPI...";
  step-2: run cmd=command -v .venv/bin/twine > /dev/null 2>&1 || (.venv/bin/pip install --upgrade twine build);
  step-3: run cmd=rm -rf dist/ build/ *.egg-info/;
  step-4: run cmd=.venv/bin/python -m build;
  step-5: run cmd=.venv/bin/twine upload --repository testpypi dist/*;
}

workflow[name="version"] {
  trigger: manual;
  step-1: run cmd=echo "📦 Version information...";
  step-2: run cmd=cat VERSION;
  step-3: run cmd=.venv/bin/python -c "from importlib.metadata import version; print(f'Installed version: {version(\"sumd\")}')";
}

deploy {
  target: makefile;
}

environment[name="local"] {
  runtime: docker-compose;
  env_file: .env;
  python_version: >=3.11;
}
```

### Source Modules

- `regres.defscan`
- `regres.doctor`
- `regres.doctor_cli`
- `regres.doctor_config`
- `regres.doctor_models`
- `regres.doctor_orchestrator`
- `regres.import_error_toon_report`
- `regres.refactor`
- `regres.regres`
- `regres.regres_cli`
- `regres.version_check`

## Interfaces

### CLI Entry Points

- `regres`
- `import-error-toon-report`

### testql Scenarios

#### `testql-scenarios/generated-cli-tests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-cli-tests.testql.toon.yaml
# SCENARIO: CLI Command Tests
# TYPE: cli
# GENERATED: true

CONFIG[2]{key, value}:
  cli_command, python -m regres
  timeout_ms, 10000

# Test 1: CLI help command
SHELL "python -m regres --help" 5000
ASSERT_EXIT_CODE 0
ASSERT_STDOUT_CONTAINS "usage"

# Test 2: CLI version command
SHELL "python -m regres --version" 5000
ASSERT_EXIT_CODE 0

# Test 3: CLI main workflow (dry-run)
SHELL "python -m regres --help" 10000
ASSERT_EXIT_CODE 0
```

## Workflows

## Configuration

```yaml
project:
  name: regres
  version: 0.1.47
  env: local
```

## Deployment

```bash markpact:run
pip install regres

# development install
pip install -e .[dev]
```

## Release Management (`goal.yaml`)

- **versioning**: `semver`
- **commits**: `conventional` scope=`regres`
- **changelog**: `keep-a-changelog`
- **build strategies**: `python`, `nodejs`, `rust`
- **version files**: `VERSION`, `pyproject.toml:version`, `regres/__init__.py:__version__`

## Makefile Targets

- `help` — Default target
- `install` — Installation
- `install-dev`
- `test` — Testing
- `test-cov`
- `lint` — Code quality
- `format`
- `clean` — Utilities
- `publish` — Release helpers
- `publish-confirm`
- `publish-test`
- `version`

## Code Analysis

### `project/map.toon.yaml`

```toon markpact:analysis path=project/map.toon.yaml
# regres | 27f 11791L | python:24,shell:2,less:1 | 2026-04-29
# stats: 452 func | 9 cls | 27 mod | CC̄=4.3 | critical:43 | cycles:0
# alerts[5]: CC _handle_url_mode=91; CC _save_report=20; CC _handle_auto_decision_flow=18; CC _run_seed_mode=17; CC cmd_hotmap=16
# hotspots[5]: _handle_url_mode fan=52; cmd_hotmap fan=23; analyze_file fan=22; trace_name_and_hash_candidates fan=21; _handle_auto_decision_flow fan=17
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[27]:
  app.doql.less,114
  project.sh,41
  regres/__init__.py,21
  regres/defscan.py,1261
  regres/doctor.py,7
  regres/doctor_cli.py,967
  regres/doctor_config.py,264
  regres/doctor_models.py,37
  regres/doctor_orchestrator.py,2684
  regres/import_error_toon_report.py,373
  regres/refactor.py,1237
  regres/regres.py,1495
  regres/regres_cli.py,210
  regres/version_check.py,186
  scripts/import-error-toon-report.py,12
  tests/test_defscan.py,138
  tests/test_doctor.py,59
  tests/test_doctor_cli.py,464
  tests/test_doctor_config.py,144
  tests/test_doctor_e2e.py,486
  tests/test_doctor_models.py,248
  tests/test_doctor_orchestrator.py,695
  tests/test_import_error_toon_report.py,201
  tests/test_refactor.py,151
  tests/test_regres.py,121
  tests/test_regres_core.py,173
  tree.sh,2
D:
  regres/__init__.py:
  regres/defscan.py:
    e: c,_normalize,sim,_get_body,_get_decorators,_collect_class_method_ids,_extract_class_definitions,_extract_function_definition,extract_python,_advance_past_string,_advance_past_comment,_extract_block_ts,_lineno_at,extract_typescript,extract_go,extract_rust,extract_file,load_gitignore,_match_anchored_pattern,_match_unanchored_pattern,_path_ignored_by_gitignore,_should_skip_file,scan,_def_key,compare_seed_to_all,analyse_group,classify_similarity,_short_path,render_text,render_markdown,render_seed_text,render_seed_markdown,render_seed_json,render_json,_build_argument_parser,_run_seed_mode,_build_focus_groups,_analyse_and_sort_groups,_run_focus_mode,_run_default_mode,_count_similarity_levels,_print_pair_summary,main,Definition
    Definition: __init__(9),loc(0),__repr__(0)  # Pojedyncza definicja (klasa / funkcja / enum / interface / m
    c(text;code)
    _normalize(text)
    sim(a;b)
    _get_body(node;lines)
    _get_decorators(node)
    _collect_class_method_ids(tree)
    _extract_class_definitions(node;path;lines)
    _extract_function_definition(node;path;lines;class_method_ids)
    extract_python(path)
    _advance_past_string(text;i;quote)
    _advance_past_comment(text;i)
    _extract_block_ts(text;start_pos)
    _lineno_at(text;pos)
    extract_typescript(path)
    extract_go(path)
    extract_rust(path)
    extract_file(path)
    load_gitignore(root)
    _match_anchored_pattern(rel_str;pat_cmp;is_dir)
    _match_unanchored_pattern(name;rel;rel_str;pat_cmp;is_dir)
    _path_ignored_by_gitignore(path;root;patterns)
    _should_skip_file(p;exts;only_within_resolved;gitignore_root_resolved;gitignore_patterns)
    scan(root;name_filter;kind_filter;only_within;gitignore_patterns;gitignore_root;ext_filter)
    _def_key(d)
    compare_seed_to_all(seed_defs;all_defs;min_sim;skip_same_name)
    analyse_group(defs)
    classify_similarity(pct)
    _short_path(path;root)
    render_text(groups;root;min_sim;show_body_lines)
    render_markdown(groups;root;min_sim)
    render_seed_text(results;root;top_per_seed;show_body_lines)
    render_seed_markdown(results;root;top_per_seed)
    render_seed_json(results;root)
    render_json(groups;root)
    _build_argument_parser()
    _run_seed_mode(args;root;root_str;gitignore_patterns;ext_set)
    _build_focus_groups(focus_index;full_index;min_count)
    _analyse_and_sort_groups(groups_raw)
    _run_focus_mode(args;root;root_str;gitignore_patterns;ext_set)
    _run_default_mode(args;root;root_str;gitignore_patterns;ext_set)
    _count_similarity_levels(pairs)
    _print_pair_summary(groups_analysed)
    main()
  regres/doctor.py:
  regres/doctor_cli.py:
    e: _handle_url_mode,_handle_import_errors,_handle_defscan_refactor,_handle_auto_decision_flow,_save_report,_render_patches_section,_refresh_import_error_log,_build_parser,main
    _handle_url_mode(args;doctor;scan_root)
    _handle_import_errors(args;doctor;scan_root;refresh_fn)
    _handle_defscan_refactor(args;doctor)
    _handle_auto_decision_flow(args;doctor;scan_root;refresh_fn)
    _save_report(doctor;args)
    _render_patches_section(patches)
    _refresh_import_error_log(project_root;log_path)
    _build_parser()
    main()
  regres/doctor_config.py:
    e: _parse_env_file,_ensure_env_file,load_config,DoctorConfig
    DoctorConfig: banner_lines(0),print_banner_to(1)  # Resolved runtime configuration for one ``doctor`` invocation
    _parse_env_file(path)
    _ensure_env_file(scan_root)
    load_config(scan_root;cli_overrides)
  regres/doctor_models.py:
    e: FileAction,ShellCommand,Diagnosis
    FileAction:  # Akcja na pliku.
    ShellCommand:  # Polecenie shell do wykonania.
    Diagnosis:  # Diagnoza problemu i plan naprawy.
  regres/doctor_orchestrator.py:
    e: DoctorOrchestrator
    DoctorOrchestrator: __init__(2),analyze_from_url(1),analyze_dependency_chain(2),_extract_relative_imports(1),_resolve_relative_import(2),probe_vite_runtime(3),analyze_module_loader_compliance(2),analyze_page_registry_compliance(2),analyze_page_implementations(3),_extract_page_token(2),_find_page_files(2),_diagnose_page_stub(3),_collect_page_history_candidates(5),_fingerprint_page_content(1),_find_backup_page_implementation(2),_build_missing_page_diagnosis(4),_filter_actionable_diagnoses(1),_build_url_fallback_diagnosis(2),analyze_import_errors(1),analyze_duplicates(1),analyze_git_history(1),analyze_with_defscan(1),analyze_with_refactor(1),apply_fixes(2),generate_llm_diagnosis(2),generate_report(0),render_markdown(1),reset_analysis_plan(0),add_plan_step(8),update_last_plan_step(0),set_analysis_context(2),summarize_affected_files(0),generate_patch_scripts(2),_render_patch_script(8),_render_generic_patch_script(3),_extract_module_name(1),_resolve_module_path(1),_import_exists_in_source(2),_resolve_alias_target(1),_parse_ts_errors(1),_validate_errors(2),_extract_missing_modules(1),_diagnose_import_issue(2),_diagnose_duplicate(1),_find_main_location(1),_analyze_history_patterns(2),_apply_file_action(3),_apply_shell_command(3),_build_header(2),_build_section(2),_build_nlp_diagnosis(1),_build_proposed_fixes(1),_build_shell_commands(1),_build_playbook(1),_build_summary(1),_collect_all_diagnoses(1),_normalize_diagnoses(1),_render_decision_workflow(1),_fmt_plan_value(1),_render_affected_files(1),_build_candidate_patch_index(1),_render_dependency_chain(1),_suggest_url_for_path(1),_render_structure_snapshot(1),_render_preliminary_refactor_proposals(1),collect_structure_snapshot(1),collect_preliminary_refactor_proposals(0),_render_step_by_step_playbook(2),_render_analyze_step(2),_render_apply_step(2),_render_validate_step(1),_collect_git_context(1),_collect_structure_context(1),_collect_defscan_context(1),_collect_refactor_context(1)  # Orchestrator analizy i generator akcji.
  regres/import_error_toon_report.py:
    e: toon_quote,parse_args,run_typecheck,normalize_file_rel,parse_ts_errors,suggestions_for_error,grouped_errors,metrics,to_toon_block_legacy,to_toon_global_payload,to_toon_compact_per_file,render_markdown,main,TsError,ReportData
    TsError:
    ReportData:
    toon_quote(value)
    parse_args()
    run_typecheck(cwd;command)
    normalize_file_rel(raw_file;cwd)
    parse_ts_errors(log_text;cwd;include_codes)
    suggestions_for_error(err)
    grouped_errors(errors)
    metrics(errors)
    to_toon_block_legacy(file_rel;errs;max_errors)
    to_toon_global_payload(report;scan_root;max_files;max_errors_per_file)
    to_toon_compact_per_file(grouped;max_files;max_errors)
    render_markdown(report;scan_root;max_files;max_errors_per_file)
    main()
  regres/refactor.py:
    e: iter_files,read_text,md5_file,count_word,line_count,similarity_ratio,normalize_code,rel,name_prefix,extract_imports,extract_symbols_ast,extract_symbols_regex,get_symbols,wrapper_score,cmd_find,cmd_duplicates,cmd_similar,_build_symbol_index,_render_cross_lang_symbols,_render_duplicate_symbols,_render_file_symbols,cmd_symbols,cmd_wrappers,cmd_dead,cmd_diff,cmd_hotmap,cmd_cluster,_deps_filter_by_word,_deps_print_word_results,_deps_print_all,cmd_deps,_sanitize,_format_imports,_format_preview,_toon_meta_section,_toon_files_section,_toon_clusters_section,_toon_similar_pairs_section,_toon_llm_hint,to_json_toon,_collect_file_infos,_find_md5_duplicates,_find_name_clusters,_find_similar_pairs,_find_duplicate_symbols,_find_cross_language_symbols,_find_external_importers,_build_report,_save_report,cmd_report,build_parser,main
    iter_files(root;extensions;word_filter;case_sensitive;ext_filter)
    read_text(p)
    md5_file(p)
    count_word(text;word;case_sensitive)
    line_count(text)
    similarity_ratio(a;b)
    normalize_code(text;ext)
    rel(p;root)
    name_prefix(name;depth)
    extract_imports(text)
    extract_symbols_ast(text;filepath)
    extract_symbols_regex(text;ext)
    get_symbols(p;text)
    wrapper_score(text)
    cmd_find(args;root)
    cmd_duplicates(args;root)
    cmd_similar(args;root)
    _build_symbol_index(files;root;kind_filter)
    _render_cross_lang_symbols(cross_sorted;args)
    _render_duplicate_symbols(dups_sorted;args)
    _render_file_symbols(file_symbols;kind_filter;args)
    cmd_symbols(args;root)
    cmd_wrappers(args;root)
    cmd_dead(args;root)
    cmd_diff(args;root)
    cmd_hotmap(args;root)
    cmd_cluster(args;root)
    _deps_filter_by_word(import_map;word)
    _deps_print_word_results(word;targets;importers)
    _deps_print_all(import_map)
    cmd_deps(args;root)
    _sanitize(value)
    _format_imports(raw_imports)
    _format_preview(raw_preview;max_len)
    _toon_meta_section(meta)
    _toon_files_section(files)
    _toon_clusters_section(clusters)
    _toon_similar_pairs_section(similar_pairs)
    _toon_llm_hint(llm_hint)
    to_json_toon(data)
    _collect_file_infos(files;root;word;args;max_preview)
    _find_md5_duplicates(texts)
    _find_name_clusters(texts;depth;top_n)
    _find_similar_pairs(texts;normalize;threshold;max_files;max_pairs)
    _find_duplicate_symbols(files;root;top_n)
    _find_cross_language_symbols(sym_index;top_n)
    _find_external_importers(files;root;word)
    _build_report(word;root;file_infos;dup_groups;top_clusters;similar_pairs;wrappers_found;dup_symbols;sym_cross;importers;threshold;normalize)
    _save_report(report;out_path;toon_format;word)
    cmd_report(args;root)
    build_parser()
    main()
  regres/regres.py:
    e: run_git,find_repo_root,_dedupe_paths,_check_absolute_path,_check_relative_paths,_search_by_name_suffix,_resolve_single_or_error,resolve_target_file,to_rel,safe_read_text,sha256_of_file,content_metrics,resolve_local_import,extract_local_imports,resolve_import_at_commit,check_imports_at_commit,find_last_working_commit,search_missing_in_history,analyze_regression,extract_symbols,track_filename_history,find_current_locations,_classify_import_problem,_analyze_import_problems,_analyze_evolution,_determine_primary_type,classify_problem,dependency_tree,reverse_references,exact_and_near_duplicates,trace_name_and_hash_candidates,parse_numstat_block,file_lineage,changed_files_for_commit,references_in_recent_commits,file_content_at_commit,resolve_import_historical,historical_dependency_tree,analyze_evolution,_collect_tree_paths,find_last_good_version,llm_context_packet,_render_classification_section,_render_name_hash_section,_render_metrics_section,_render_references_section,_render_duplicates_section,_render_lineage_section,_render_evolution_section,_render_last_good_section,_render_regression_section,render_markdown,analyze_file,_resolve_output_path,main,GitCommit
    GitCommit:
    run_git(args;cwd)
    find_repo_root(start)
    _dedupe_paths(paths)
    _check_absolute_path(raw)
    _check_relative_paths(raw;bases)
    _search_by_name_suffix(name;suffix;roots)
    _resolve_single_or_error(candidates;error_msg)
    resolve_target_file(file_arg;cwd;repo_root;scan_root)
    to_rel(path;repo_root)
    safe_read_text(path)
    sha256_of_file(path)
    content_metrics(text;path)
    resolve_local_import(raw_import;file_path;repo_root)
    extract_local_imports(text)
    resolve_import_at_commit(raw_import;file_rel;repo_root;commit_sha)
    check_imports_at_commit(repo_root;rel_path;commit_sha)
    find_last_working_commit(repo_root;rel_path;commits)
    search_missing_in_history(repo_root;missing_imports;file_rel)
    analyze_regression(repo_root;rel_path;commits;current_text)
    extract_symbols(text)
    track_filename_history(repo_root;basename)
    find_current_locations(repo_root;basename)
    _classify_import_problem(repo_root;mh)
    _analyze_import_problems(import_problems;broken;target_dir)
    _analyze_evolution(current_lines;evolution)
    _determine_primary_type(import_problems;broken;target_dir;current_lines;evolution)
    classify_problem(repo_root;target_rel;current_text;evolution;regression;duplicates)
    dependency_tree(file_path;repo_root;max_depth)
    reverse_references(file_path;repo_root;scan_root;max_hits)
    exact_and_near_duplicates(file_path;repo_root;scan_root;near_threshold;max_near)
    trace_name_and_hash_candidates(file_path;repo_root;scan_root;max_candidates)
    parse_numstat_block(lines)
    file_lineage(repo_root;rel_file;max_commits)
    changed_files_for_commit(repo_root;commit_sha;limit)
    references_in_recent_commits(repo_root;commits;max_commits)
    file_content_at_commit(repo_root;rel_path;commit_sha)
    resolve_import_historical(raw_import;file_rel;repo_root;commit_sha)
    historical_dependency_tree(repo_root;rel_path;commit_sha;max_depth)
    analyze_evolution(repo_root;rel_path;commits;current_text;max_depth)
    _collect_tree_paths(tree)
    find_last_good_version(evolution;min_lines;min_similarity;max_results)
    llm_context_packet(report)
    _render_classification_section(classification;lines)
    _render_name_hash_section(nh;lines)
    _render_metrics_section(m;lines)
    _render_references_section(refs;lines)
    _render_duplicates_section(d;lines)
    _render_lineage_section(lineage;lines)
    _render_evolution_section(evolution;lines)
    _render_last_good_section(last_good;lines)
    _render_regression_section(regression;lines)
    render_markdown(report)
    analyze_file(target_file;scan_root;max_commits;tree_depth;near_threshold)
    _resolve_output_path(path_str;cwd)
    main()
  regres/regres_cli.py:
    e: main,_build_regres_argv,_build_refactor_argv,_build_defscan_argv,_build_doctor_argv,_build_ier_argv,_extend_if_set,_append_if_true,_dispatch_command
    main()
    _build_regres_argv(args)
    _build_refactor_argv(args)
    _build_defscan_argv(args)
    _build_doctor_argv(args)
    _build_ier_argv(args)
    _extend_if_set(argv;flag;value;transform)
    _append_if_true(argv;flag;value)
    _dispatch_command(args;parser)
  regres/version_check.py:
    e: _find_env_path,_read_env,_write_env,_get_pypi_version,_parse_version,_is_newer,_should_check,_save_last_check,_save_skip_preference,check_version
    _find_env_path()
    _read_env()
    _write_env(data)
    _get_pypi_version()
    _parse_version(v)
    _is_newer(remote;local)
    _should_check()
    _save_last_check()
    _save_skip_preference()
    check_version(local_version)
  scripts/import-error-toon-report.py:
  tests/test_defscan.py:
    e: test_ext_lang_mappings,test_ignored_dirs,test_c_without_color,test_normalize_strips_comments,test_normalize_collapses_whitespace,test_definition_repr,test_definition_similarity_identical,test_definition_similarity_different,test_classify_similarity_identical,test_classify_similarity_high,test_classify_similarity_medium,test_classify_similarity_low,test_load_gitignore_missing,test_load_gitignore_reads_patterns,test_path_ignored_by_gitignore
    test_ext_lang_mappings()
    test_ignored_dirs()
    test_c_without_color()
    test_normalize_strips_comments()
    test_normalize_collapses_whitespace()
    test_definition_repr()
    test_definition_similarity_identical()
    test_definition_similarity_different()
    test_classify_similarity_identical()
    test_classify_similarity_high()
    test_classify_similarity_medium()
    test_classify_similarity_low()
    test_load_gitignore_missing(tmp_path)
    test_load_gitignore_reads_patterns(tmp_path)
    test_path_ignored_by_gitignore(tmp_path)
  tests/test_doctor.py:
    e: test_file_action_defaults,test_file_action_full,test_shell_command_defaults,test_diagnosis,test_import_doctor,test_import_doctor_main
    test_file_action_defaults()
    test_file_action_full()
    test_shell_command_defaults()
    test_diagnosis()
    test_import_doctor()
    test_import_doctor_main()
  tests/test_doctor_cli.py:
    e: test_build_parser,test_parser_scan_root,test_parser_all,test_parser_url,test_parser_llm,test_parser_import_log,test_parser_defscan_report,test_parser_apply,test_parser_dry_run,test_parser_git_history,test_parser_out_md,test_parser_out_json,test_parser_defscan_scan,test_parser_refactor_scan,test_parser_multiple_args,test_refresh_import_no_frontend,test_refresh_import_with_frontend_subprocess_failure,test_refresh_import_timeout,test_handle_url_mode_without_llm,test_handle_url_mode_with_llm,test_handle_url_mode_with_llm_saves_to_file,test_handle_url_mode_with_apply,test_handle_import_errors_with_log,test_handle_import_errors_without_log_all_flag,test_handle_import_errors_with_git_history,test_handle_defscan_refactor_with_report,test_handle_defscan_refactor_with_scan,test_handle_defscan_refactor_with_refactor_scan,test_handle_defscan_refactor_none,test_save_report_to_stdout,test_save_report_to_json,test_save_report_to_md,test_save_report_to_both_formats,test_refresh_import_error_log_success,test_refresh_import_error_log_no_frontend,test_refresh_import_error_log_subprocess_failure,test_refresh_import_error_log_timeout,test_refresh_import_error_log_file_not_found,test_handle_import_errors_with_subprocess_mock,test_handle_import_errors_without_frontend,test_handle_defscan_refactor_subprocess_mock,test_full_workflow_with_all_mocks
    test_build_parser()
    test_parser_scan_root()
    test_parser_all()
    test_parser_url()
    test_parser_llm()
    test_parser_import_log()
    test_parser_defscan_report()
    test_parser_apply()
    test_parser_dry_run()
    test_parser_git_history()
    test_parser_out_md()
    test_parser_out_json()
    test_parser_defscan_scan()
    test_parser_refactor_scan()
    test_parser_multiple_args()
    test_refresh_import_no_frontend()
    test_refresh_import_with_frontend_subprocess_failure(tmp_path)
    test_refresh_import_timeout(tmp_path)
    test_handle_url_mode_without_llm(tmp_path)
    test_handle_url_mode_with_llm(tmp_path)
    test_handle_url_mode_with_llm_saves_to_file(tmp_path)
    test_handle_url_mode_with_apply(tmp_path)
    test_handle_import_errors_with_log(tmp_path)
    test_handle_import_errors_without_log_all_flag(tmp_path)
    test_handle_import_errors_with_git_history(tmp_path)
    test_handle_defscan_refactor_with_report(tmp_path)
    test_handle_defscan_refactor_with_scan(tmp_path)
    test_handle_defscan_refactor_with_refactor_scan(tmp_path)
    test_handle_defscan_refactor_none(tmp_path)
    test_save_report_to_stdout(tmp_path)
    test_save_report_to_json(tmp_path)
    test_save_report_to_md(tmp_path)
    test_save_report_to_both_formats(tmp_path)
    test_refresh_import_error_log_success(tmp_path)
    test_refresh_import_error_log_no_frontend(tmp_path)
    test_refresh_import_error_log_subprocess_failure(tmp_path)
    test_refresh_import_error_log_timeout(tmp_path)
    test_refresh_import_error_log_file_not_found(tmp_path)
    test_handle_import_errors_with_subprocess_mock(tmp_path)
    test_handle_import_errors_without_frontend(tmp_path)
    test_handle_defscan_refactor_subprocess_mock(tmp_path)
    test_full_workflow_with_all_mocks(tmp_path)
  tests/test_doctor_config.py:
    e: _clear_regres_env,test_load_config_uses_defaults_and_creates_env_file,test_load_config_priority_env_file_over_default,test_load_config_priority_environ_over_file,test_load_config_priority_cli_overrides_environ,test_load_config_invalid_int_falls_back_to_default,test_load_config_print_banner_parsing,test_banner_output_mentions_active_window_and_help,test_banner_disabled_emits_nothing
    _clear_regres_env(monkeypatch)
    test_load_config_uses_defaults_and_creates_env_file(tmp_path;monkeypatch)
    test_load_config_priority_env_file_over_default(tmp_path;monkeypatch)
    test_load_config_priority_environ_over_file(tmp_path;monkeypatch)
    test_load_config_priority_cli_overrides_environ(tmp_path;monkeypatch)
    test_load_config_invalid_int_falls_back_to_default(tmp_path;monkeypatch)
    test_load_config_print_banner_parsing(tmp_path;monkeypatch;raw;expected)
    test_banner_output_mentions_active_window_and_help(tmp_path;monkeypatch)
    test_banner_disabled_emits_nothing(tmp_path;monkeypatch)
  tests/test_doctor_e2e.py:
    e: run_doctor_command,test_doctor_cli_help,test_doctor_cli_version,test_url_mode_module_not_found,test_url_mode_with_existing_module,test_url_mode_with_markdown_output,test_url_mode_both_outputs,test_import_error_with_log_file,test_import_error_with_nonexistent_log,test_defscan_with_report_file,test_all_mode_basic,test_all_mode_with_markdown,test_patch_generation_with_dir,test_no_patches_flag,test_invalid_scan_root,test_concurrent_runs,test_real_world_scenario_missing_imports,test_real_world_scenario_module_analysis,test_analysis_plan_structure,test_diagnosis_structure
    run_doctor_command(args;cwd)
    test_doctor_cli_help(tmp_path)
    test_doctor_cli_version(tmp_path)
    test_url_mode_module_not_found(tmp_path)
    test_url_mode_with_existing_module(tmp_path)
    test_url_mode_with_markdown_output(tmp_path)
    test_url_mode_both_outputs(tmp_path)
    test_import_error_with_log_file(tmp_path)
    test_import_error_with_nonexistent_log(tmp_path)
    test_defscan_with_report_file(tmp_path)
    test_all_mode_basic(tmp_path)
    test_all_mode_with_markdown(tmp_path)
    test_patch_generation_with_dir(tmp_path)
    test_no_patches_flag(tmp_path)
    test_invalid_scan_root(tmp_path)
    test_concurrent_runs(tmp_path)
    test_real_world_scenario_missing_imports(tmp_path)
    test_real_world_scenario_module_analysis(tmp_path)
    test_analysis_plan_structure(tmp_path)
    test_diagnosis_structure(tmp_path)
  tests/test_doctor_models.py:
    e: test_file_action_defaults,test_file_action_full,test_file_action_all_action_types,test_file_action_empty_path,test_file_action_none_path,test_file_action_with_special_characters,test_file_action_target_without_reason,test_file_action_reason_without_target,test_file_action_equality,test_shell_command,test_shell_command_with_cwd,test_shell_command_empty_command,test_shell_command_empty_description,test_shell_command_none_description,test_shell_command_multiline,test_shell_command_with_special_chars,test_shell_command_with_quotes,test_diagnosis_defaults,test_diagnosis_with_actions,test_diagnosis_with_shell_commands,test_diagnosis_with_both_actions_and_commands,test_diagnosis_confidence_bounds,test_diagnosis_severity_levels,test_diagnosis_problem_types,test_diagnosis_empty_summary,test_diagnosis_empty_nlp_description,test_diagnosis_multiple_file_actions,test_diagnosis_multiple_shell_commands,test_diagnosis_unicode_in_fields,test_diagnosis_long_description,test_diagnosis_confidence_out_of_bounds,test_diagnosis_immutability_of_lists,test_diagnosis_with_none_confidence
    test_file_action_defaults()
    test_file_action_full()
    test_file_action_all_action_types()
    test_file_action_empty_path()
    test_file_action_none_path()
    test_file_action_with_special_characters()
    test_file_action_target_without_reason()
    test_file_action_reason_without_target()
    test_file_action_equality()
    test_shell_command()
    test_shell_command_with_cwd()
    test_shell_command_empty_command()
    test_shell_command_empty_description()
    test_shell_command_none_description()
    test_shell_command_multiline()
    test_shell_command_with_special_chars()
    test_shell_command_with_quotes()
    test_diagnosis_defaults()
    test_diagnosis_with_actions()
    test_diagnosis_with_shell_commands()
    test_diagnosis_with_both_actions_and_commands()
    test_diagnosis_confidence_bounds()
    test_diagnosis_severity_levels()
    test_diagnosis_problem_types()
    test_diagnosis_empty_summary()
    test_diagnosis_empty_nlp_description()
    test_diagnosis_multiple_file_actions()
    test_diagnosis_multiple_shell_commands()
    test_diagnosis_unicode_in_fields()
    test_diagnosis_long_description()
    test_diagnosis_confidence_out_of_bounds()
    test_diagnosis_immutability_of_lists()
    test_diagnosis_with_none_confidence()
  tests/test_doctor_orchestrator.py:
    e: test_init_sets_scan_root,test_module_path_map_non_empty,test_module_path_map_contains_all_modules,test_reset_analysis_plan,test_add_plan_step_basic,test_add_plan_step_with_status,test_add_plan_step_with_details,test_set_analysis_context,test_analyze_from_url_valid_module,test_analyze_from_url_invalid_url,test_analyze_from_url_module_not_exists,test_analyze_import_errors_missing_log,test_analyze_import_errors_with_valid_log,test_analyze_import_errors_empty_log,test_analyze_duplicates_missing_report,test_analyze_duplicates_valid_report,test_analyze_duplicates_invalid_json,test_analyze_git_history_no_git,test_analyze_git_history_with_git,test_analyze_git_history_timeout,test_analyze_with_defscan_subprocess_failure,test_analyze_with_defscan_timeout,test_analyze_with_refactor_subprocess_failure,test_analyze_with_refactor_with_wrappers,test_apply_fixes_empty,test_apply_fixes_with_modify_action,test_apply_fixes_with_delete_action,test_apply_fixes_with_shell_command,test_apply_fixes_error_handling,test_generate_report_empty,test_generate_report_with_diagnoses,test_generate_report_with_analysis_plan,test_generate_report_with_analysis_context,test_render_markdown_empty,test_render_markdown_with_diagnoses,test_render_markdown_with_file_actions,test_render_markdown_with_shell_commands,test_render_markdown_severity_emojis,test_render_markdown_with_decision_workflow,test_generate_llm_diagnosis,test_generate_llm_diagnosis_sections,test_extract_module_name,test_resolve_module_path,test_import_exists_in_source,test_import_exists_in_source_commented,test_resolve_alias_target,test_parse_ts_errors,test_validate_errors,test_extract_missing_modules,test_find_main_location,test_find_main_location_no_shared,test_analyze_history_patterns,test_analyze_history_patterns_no_moves,_make_module_entry,test_module_loader_compliance_passes_with_module_class,test_module_loader_compliance_passes_with_default_export,test_module_loader_compliance_flags_view_only_export,test_module_loader_compliance_returns_none_when_entry_missing,_make_pages_index,test_page_registry_compliance_passes_when_default_present,test_page_registry_compliance_flags_empty_registry,test_page_registry_compliance_flags_default_not_in_registry,test_page_registry_compliance_returns_none_when_no_index
    test_init_sets_scan_root()
    test_module_path_map_non_empty()
    test_module_path_map_contains_all_modules()
    test_reset_analysis_plan()
    test_add_plan_step_basic()
    test_add_plan_step_with_status()
    test_add_plan_step_with_details()
    test_set_analysis_context()
    test_analyze_from_url_valid_module(tmp_path)
    test_analyze_from_url_invalid_url(tmp_path)
    test_analyze_from_url_module_not_exists(tmp_path)
    test_analyze_import_errors_missing_log()
    test_analyze_import_errors_with_valid_log(tmp_path)
    test_analyze_import_errors_empty_log(tmp_path)
    test_analyze_duplicates_missing_report()
    test_analyze_duplicates_valid_report(tmp_path)
    test_analyze_duplicates_invalid_json(tmp_path)
    test_analyze_git_history_no_git()
    test_analyze_git_history_with_git(tmp_path)
    test_analyze_git_history_timeout(tmp_path)
    test_analyze_with_defscan_subprocess_failure(tmp_path)
    test_analyze_with_defscan_timeout(tmp_path)
    test_analyze_with_refactor_subprocess_failure(tmp_path)
    test_analyze_with_refactor_with_wrappers(tmp_path)
    test_apply_fixes_empty()
    test_apply_fixes_with_modify_action()
    test_apply_fixes_with_delete_action(tmp_path)
    test_apply_fixes_with_shell_command()
    test_apply_fixes_error_handling()
    test_generate_report_empty()
    test_generate_report_with_diagnoses()
    test_generate_report_with_analysis_plan()
    test_generate_report_with_analysis_context()
    test_render_markdown_empty()
    test_render_markdown_with_diagnoses()
    test_render_markdown_with_file_actions()
    test_render_markdown_with_shell_commands()
    test_render_markdown_severity_emojis()
    test_render_markdown_with_decision_workflow()
    test_generate_llm_diagnosis()
    test_generate_llm_diagnosis_sections()
    test_extract_module_name()
    test_resolve_module_path(tmp_path)
    test_import_exists_in_source(tmp_path)
    test_import_exists_in_source_commented(tmp_path)
    test_resolve_alias_target(tmp_path)
    test_parse_ts_errors(tmp_path)
    test_validate_errors(tmp_path)
    test_extract_missing_modules()
    test_find_main_location()
    test_find_main_location_no_shared()
    test_analyze_history_patterns()
    test_analyze_history_patterns_no_moves()
    _make_module_entry(tmp_path;module_name;body)
    test_module_loader_compliance_passes_with_module_class(tmp_path)
    test_module_loader_compliance_passes_with_default_export(tmp_path)
    test_module_loader_compliance_flags_view_only_export(tmp_path)
    test_module_loader_compliance_returns_none_when_entry_missing(tmp_path)
    _make_pages_index(tmp_path;module_name;body)
    test_page_registry_compliance_passes_when_default_present(tmp_path)
    test_page_registry_compliance_flags_empty_registry(tmp_path)
    test_page_registry_compliance_flags_default_not_in_registry(tmp_path)
    test_page_registry_compliance_returns_none_when_no_index(tmp_path)
  tests/test_import_error_toon_report.py:
    e: test_ts_error_re_matches,test_ts_error_re_no_match_for_plain_text,test_missing_module_re,test_exported_member_re,test_toon_quote_escapes,test_parse_ts_errors_basic,test_parse_ts_errors_filters_code,test_parse_ts_errors_empty,test_suggestions_ts2307_alias,test_suggestions_ts2307_relative,test_suggestions_ts2305,test_suggestions_unknown_code,test_grouped_errors,test_metrics,test_metrics_empty,test_to_toon_block_legacy,test_to_toon_global_payload,test_to_toon_compact_per_file,test_ts_error_dataclass,test_report_data
    test_ts_error_re_matches()
    test_ts_error_re_no_match_for_plain_text()
    test_missing_module_re()
    test_exported_member_re()
    test_toon_quote_escapes()
    test_parse_ts_errors_basic()
    test_parse_ts_errors_filters_code()
    test_parse_ts_errors_empty()
    test_suggestions_ts2307_alias()
    test_suggestions_ts2307_relative()
    test_suggestions_ts2305()
    test_suggestions_unknown_code()
    test_grouped_errors()
    test_metrics()
    test_metrics_empty()
    test_to_toon_block_legacy()
    test_to_toon_global_payload()
    test_to_toon_compact_per_file()
    test_ts_error_dataclass()
    test_report_data()
  tests/test_refactor.py:
    e: test_default_extensions_contains_py,test_ignored_dirs_contains_node_modules,test_count_word_case_insensitive,test_count_word_case_sensitive,test_line_count,test_similarity_ratio_identical,test_similarity_ratio_empty,test_similarity_ratio_different,test_normalize_code_strips_comments,test_rel_path,test_name_prefix,test_extract_imports_python,test_extract_imports_ts,test_extract_symbols_regex_python,test_extract_symbols_regex_ts,test_wrapper_score_empty,test_wrapper_score_high_for_reexport,test_md5_file_consistent,test_read_text_reads_utf8
    test_default_extensions_contains_py()
    test_ignored_dirs_contains_node_modules()
    test_count_word_case_insensitive()
    test_count_word_case_sensitive()
    test_line_count()
    test_similarity_ratio_identical()
    test_similarity_ratio_empty()
    test_similarity_ratio_different()
    test_normalize_code_strips_comments()
    test_rel_path()
    test_name_prefix()
    test_extract_imports_python()
    test_extract_imports_ts()
    test_extract_symbols_regex_python()
    test_extract_symbols_regex_ts()
    test_wrapper_score_empty()
    test_wrapper_score_high_for_reexport()
    test_md5_file_consistent(tmp_path)
    test_read_text_reads_utf8(tmp_path)
  tests/test_regres.py:
    e: test_placeholder,test_import,test_import_regres_module,test_import_refactor_module,test_import_defscan_module,test_import_import_error_toon_report,test_regres_cli_module_exists,test_regres_cli_import,test_import_error_toon_report_main_signature,test_regres_cli_help,test_regres_cli_doctor_help,test_regres_cli_defscan_help,test_regres_cli_refactor_help,test_regres_cli_doctor_on_self
    test_placeholder()
    test_import()
    test_import_regres_module()
    test_import_refactor_module()
    test_import_defscan_module()
    test_import_import_error_toon_report()
    test_regres_cli_module_exists()
    test_regres_cli_import()
    test_import_error_toon_report_main_signature()
    test_regres_cli_help()
    test_regres_cli_doctor_help()
    test_regres_cli_defscan_help()
    test_regres_cli_refactor_help()
    test_regres_cli_doctor_on_self()
  tests/test_regres_core.py:
    e: test_git_commit_fields,test_find_repo_root_finds_git,test_find_repo_root_raises_when_no_git,test_dedupe_paths,test_check_absolute_path_existing,test_check_absolute_path_missing,test_check_relative_paths,test_resolve_single_or_error,test_resolve_single_or_error_raises,test_to_rel,test_safe_read_text_utf8,test_sha256_of_file_consistent,test_content_metrics,test_extract_local_imports,test_extract_symbols_ts,test_parse_numstat_block,test_parse_numstat_block_empty
    test_git_commit_fields()
    test_find_repo_root_finds_git(tmp_path)
    test_find_repo_root_raises_when_no_git(tmp_path)
    test_dedupe_paths()
    test_check_absolute_path_existing(tmp_path)
    test_check_absolute_path_missing()
    test_check_relative_paths(tmp_path)
    test_resolve_single_or_error()
    test_resolve_single_or_error_raises()
    test_to_rel()
    test_safe_read_text_utf8(tmp_path)
    test_sha256_of_file_consistent(tmp_path)
    test_content_metrics(tmp_path)
    test_extract_local_imports()
    test_extract_symbols_ts()
    test_parse_numstat_block()
    test_parse_numstat_block_empty()
```

## Source Map

*Top 5 modules by symbol density — signatures for LLM orientation.*

### `regres.doctor_orchestrator` (`regres/doctor_orchestrator.py`)

```python
class DoctorOrchestrator:  # Orchestrator analizy i generator akcji.
    def __init__(scan_root, config)  # CC=2
    def analyze_from_url(url)  # CC=8
    def analyze_dependency_chain(target_file, max_depth)  # CC=21 ⚠
    def _extract_relative_imports(text)  # CC=5
    def _resolve_relative_import(from_file, raw_import)  # CC=7
    def probe_vite_runtime(vite_base, file_rel, timeout)  # CC=11 ⚠
    def analyze_module_loader_compliance(module_path, module_name)  # CC=10 ⚠
    def analyze_page_registry_compliance(module_path, module_name)  # CC=15 ⚠
    def analyze_page_implementations(route_path, module_path, module_name)  # CC=5
    def _extract_page_token(route_path, module_name)  # CC=7
    def _find_page_files(module_path, page_token)  # CC=6
    def _diagnose_page_stub(page_file, page_token, module_name)  # CC=31 ⚠
    def _collect_page_history_candidates(page_token, module_name, current_file, days, iterations)  # CC=23 ⚠
    def _fingerprint_page_content(content)  # CC=8
    def _find_backup_page_implementation(page_token, module_name)  # CC=13 ⚠
    def _build_missing_page_diagnosis(route_path, module_path, module_name, page_token)  # CC=3
    def _filter_actionable_diagnoses(diagnoses)  # CC=5
    def _build_url_fallback_diagnosis(route_path, module_path)  # CC=7
    def analyze_import_errors(log_path)  # CC=5
    def analyze_duplicates(report_path)  # CC=5
    def analyze_git_history(file_path)  # CC=7
    def analyze_with_defscan(path)  # CC=7
    def analyze_with_refactor(path)  # CC=7
    def apply_fixes(diagnoses, dry_run)  # CC=4
    def generate_llm_diagnosis(url, module_path)  # CC=1
    def generate_report()  # CC=10 ⚠
    def render_markdown(report)  # CC=9
    def reset_analysis_plan()  # CC=1
    def add_plan_step(name, reason, command, status, details, inputs, outputs, decision)  # CC=5
    def update_last_plan_step()  # CC=2
    def set_analysis_context(key, value)  # CC=1
    def summarize_affected_files()  # CC=7
    def generate_patch_scripts(out_dir, basename)  # CC=26 ⚠
    def _render_patch_script(diag, diag_idx, cand_idx, total_cands, git_hash, source_path, target_path, reason)  # CC=1
    def _render_generic_patch_script(diag, diag_idx, target_path)  # CC=2
    def _extract_module_name(path)  # CC=6
    def _resolve_module_path(module_name)  # CC=5
    def _import_exists_in_source(file_path, module_name)  # CC=11 ⚠
    def _resolve_alias_target(alias_path)  # CC=6
    def _parse_ts_errors(log_path)  # CC=6
    def _validate_errors(file_path, errors)  # CC=4
    def _extract_missing_modules(errors)  # CC=3
    def _diagnose_import_issue(file_path, missing_modules)  # CC=15 ⚠
    def _diagnose_duplicate(duplicate_data)  # CC=4
    def _find_main_location(locations)  # CC=4
    def _analyze_history_patterns(file_path, history_lines)  # CC=9
    def _apply_file_action(action, dry_run, results)  # CC=14 ⚠
    def _apply_shell_command(cmd, dry_run, results)  # CC=4
    def _build_header(url, module_path)  # CC=1
    def _build_section(title, content)  # CC=1
    def _build_nlp_diagnosis(module_path)  # CC=3
    def _build_proposed_fixes(module_path)  # CC=5
    def _build_shell_commands(module_path)  # CC=4
    def _build_playbook(module_path)  # CC=4
    def _build_summary(module_path)  # CC=3
    def _collect_all_diagnoses(module_path)  # CC=2
    def _normalize_diagnoses(diagnoses)  # CC=1
    def _render_decision_workflow(report)  # CC=12 ⚠
    def _fmt_plan_value(value)  # CC=7
    def _render_affected_files(report)  # CC=22 ⚠
    def _build_candidate_patch_index(report)  # CC=11 ⚠
    def _render_dependency_chain(report)  # CC=28 ⚠
    def _suggest_url_for_path(raw_or_path)  # CC=3
    def _render_structure_snapshot(report)  # CC=2
    def _render_preliminary_refactor_proposals(report)  # CC=3
    def collect_structure_snapshot(max_entries)  # CC=7
    def collect_preliminary_refactor_proposals()  # CC=6
    def _render_step_by_step_playbook(diagnoses, llm_mode)  # CC=8
    def _render_analyze_step(shell_commands, paths)  # CC=8
    def _render_apply_step(llm_mode, paths)  # CC=4
    def _render_validate_step(paths)  # CC=3
    def _collect_git_context(module_path)  # CC=3
    def _collect_structure_context(module_path)  # CC=4
    def _collect_defscan_context(module_path)  # CC=7
    def _collect_refactor_context(module_path)  # CC=3
```

### `regres.regres` (`regres/regres.py`)

```python
def run_git(args, cwd)  # CC=1, fan=2
def find_repo_root(start)  # CC=4, fan=3
def _dedupe_paths(paths)  # CC=3, fan=5
def _check_absolute_path(raw)  # CC=4, fan=4
def _check_relative_paths(raw, bases)  # CC=4, fan=5
def _search_by_name_suffix(name, suffix, roots)  # CC=10, fan=11 ⚠
def _resolve_single_or_error(candidates, error_msg)  # CC=4, fan=4
def resolve_target_file(file_arg, cwd, repo_root, scan_root)  # CC=13, fan=13 ⚠
def to_rel(path, repo_root)  # CC=1, fan=3
def safe_read_text(path)  # CC=2, fan=1
def sha256_of_file(path)  # CC=2, fan=6
def content_metrics(text, path)  # CC=5, fan=9
def resolve_local_import(raw_import, file_path, repo_root)  # CC=8, fan=6
def extract_local_imports(text)  # CC=6, fan=4
def resolve_import_at_commit(raw_import, file_rel, repo_root, commit_sha)  # CC=6, fan=5
def check_imports_at_commit(repo_root, rel_path, commit_sha)  # CC=8, fan=11
def find_last_working_commit(repo_root, rel_path, commits)  # CC=8, fan=1
def search_missing_in_history(repo_root, missing_imports, file_rel)  # CC=7, fan=8
def analyze_regression(repo_root, rel_path, commits, current_text)  # CC=11, fan=6 ⚠
def extract_symbols(text)  # CC=5, fan=7
def track_filename_history(repo_root, basename)  # CC=10, fan=7 ⚠
def find_current_locations(repo_root, basename)  # CC=6, fan=6
def _classify_import_problem(repo_root, mh)  # CC=4, fan=2
def _analyze_import_problems(import_problems, broken, target_dir)  # CC=7, fan=8
def _analyze_evolution(current_lines, evolution)  # CC=12, fan=3 ⚠
def _determine_primary_type(import_problems, broken, target_dir, current_lines, evolution)  # CC=2, fan=3
def classify_problem(repo_root, target_rel, current_text, evolution, regression, duplicates)  # CC=6, fan=10
def dependency_tree(file_path, repo_root, max_depth)  # CC=1, fan=13
def reverse_references(file_path, repo_root, scan_root, max_hits)  # CC=10, fan=11 ⚠
def exact_and_near_duplicates(file_path, repo_root, scan_root, near_threshold, max_near)  # CC=8, fan=16
def trace_name_and_hash_candidates(file_path, repo_root, scan_root, max_candidates)  # CC=13, fan=21 ⚠
def parse_numstat_block(lines)  # CC=5, fan=5
def file_lineage(repo_root, rel_file, max_commits)  # CC=9, fan=9
def changed_files_for_commit(repo_root, commit_sha, limit)  # CC=3, fan=3
def references_in_recent_commits(repo_root, commits, max_commits)  # CC=2, fan=2
def file_content_at_commit(repo_root, rel_path, commit_sha)  # CC=2, fan=1
def resolve_import_historical(raw_import, file_rel, repo_root, commit_sha)  # CC=7, fan=5
def historical_dependency_tree(repo_root, rel_path, commit_sha, max_depth)  # CC=2, fan=9
def analyze_evolution(repo_root, rel_path, commits, current_text, max_depth)  # CC=10, fan=11 ⚠
def _collect_tree_paths(tree)  # CC=2, fan=3
def find_last_good_version(evolution, min_lines, min_similarity, max_results)  # CC=7, fan=2
def llm_context_packet(report)  # CC=11, fan=1 ⚠
def _render_classification_section(classification, lines)  # CC=15, fan=4 ⚠
def _render_name_hash_section(nh, lines)  # CC=5, fan=4
def _render_metrics_section(m, lines)  # CC=1, fan=1
def _render_references_section(refs, lines)  # CC=3, fan=3
def _render_duplicates_section(d, lines)  # CC=5, fan=4
def _render_lineage_section(lineage, lines)  # CC=2, fan=1
def _render_evolution_section(evolution, lines)  # CC=6, fan=3
def _render_last_good_section(last_good, lines)  # CC=3, fan=1
def _render_regression_section(regression, lines)  # CC=12, fan=4 ⚠
def render_markdown(report)  # CC=1, fan=13
def analyze_file(target_file, scan_root, max_commits, tree_depth, near_threshold)  # CC=4, fan=22
def _resolve_output_path(path_str, cwd)  # CC=2, fan=4
def main()  # CC=6, fan=15
class GitCommit:
```

### `regres.refactor` (`regres/refactor.py`)

```python
def iter_files(root, extensions, word_filter, case_sensitive, ext_filter)  # CC=15, fan=7 ⚠
def read_text(p)  # CC=2, fan=1
def md5_file(p)  # CC=2, fan=4
def count_word(text, word, case_sensitive)  # CC=2, fan=3
def line_count(text)  # CC=2, fan=1
def similarity_ratio(a, b)  # CC=3, fan=2
def normalize_code(text, ext)  # CC=1, fan=2
def rel(p, root)  # CC=2, fan=2
def name_prefix(name, depth)  # CC=2, fan=4
def extract_imports(text)  # CC=5, fan=6
def extract_symbols_ast(text, filepath)  # CC=10, fan=4 ⚠
def extract_symbols_regex(text, ext)  # CC=7, fan=11
def get_symbols(p, text)  # CC=3, fan=4
def wrapper_score(text)  # CC=15, fan=8 ⚠
def cmd_find(args, root)  # CC=5, fan=13
def cmd_duplicates(args, root)  # CC=10, fan=13 ⚠
def cmd_similar(args, root)  # CC=14, fan=17 ⚠
def _build_symbol_index(files, root, kind_filter)  # CC=5, fan=6
def _render_cross_lang_symbols(cross_sorted, args)  # CC=6, fan=5
def _render_duplicate_symbols(dups_sorted, args)  # CC=6, fan=5
def _render_file_symbols(file_symbols, kind_filter, args)  # CC=10, fan=5 ⚠
def cmd_symbols(args, root)  # CC=12, fan=9 ⚠
def cmd_wrappers(args, root)  # CC=9, fan=11
def cmd_dead(args, root)  # CC=14, fan=17 ⚠
def cmd_diff(args, root)  # CC=7, fan=16
def cmd_hotmap(args, root)  # CC=16, fan=23 ⚠
def cmd_cluster(args, root)  # CC=12, fan=15 ⚠
def _deps_filter_by_word(import_map, word)  # CC=6, fan=3
def _deps_print_word_results(word, targets, importers)  # CC=5, fan=2
def _deps_print_all(import_map)  # CC=4, fan=3
def cmd_deps(args, root)  # CC=6, fan=10
def _sanitize(value)  # CC=1, fan=1
def _format_imports(raw_imports)  # CC=4, fan=5
def _format_preview(raw_preview, max_len)  # CC=4, fan=3
def _toon_meta_section(meta)  # CC=4, fan=3
def _toon_files_section(files)  # CC=4, fan=7
def _toon_clusters_section(clusters)  # CC=3, fan=4
def _toon_similar_pairs_section(similar_pairs)  # CC=7, fan=6
def _toon_llm_hint(llm_hint)  # CC=2, fan=0
def to_json_toon(data)  # CC=1, fan=8
def _collect_file_infos(files, root, word, args, max_preview)  # CC=6, fan=13
def _find_md5_duplicates(texts)  # CC=4, fan=8
def _find_name_clusters(texts, depth, top_n)  # CC=4, fan=8
def _find_similar_pairs(texts, normalize, threshold, max_files, max_pairs)  # CC=7, fan=11
def _find_duplicate_symbols(files, root, top_n)  # CC=5, fan=8
def _find_cross_language_symbols(sym_index, top_n)  # CC=4, fan=6
def _find_external_importers(files, root, word)  # CC=7, fan=6
def _build_report(word, root, file_infos, dup_groups, top_clusters, similar_pairs, wrappers_found, dup_symbols, sym_cross, importers, threshold, normalize)  # CC=4, fan=3
def _save_report(report, out_path, toon_format, word)  # CC=3, fan=6
def cmd_report(args, root)  # CC=6, fan=13
def build_parser()  # CC=1, fan=5
def main()  # CC=2, fan=7
```

### `regres.defscan` (`regres/defscan.py`)

```python
def c(text, code)  # CC=2, fan=0
def _normalize(text)  # CC=1, fan=2
def sim(a, b)  # CC=3, fan=2
def _get_body(node, lines)  # CC=2, fan=4
def _get_decorators(node)  # CC=3, fan=3
def _collect_class_method_ids(tree)  # CC=5, fan=5
def _extract_class_definitions(node, path, lines)  # CC=5, fan=7
def _extract_function_definition(node, path, lines, class_method_ids)  # CC=2, fan=4
def extract_python(path)  # CC=5, fan=10
def _advance_past_string(text, i, quote)  # CC=4, fan=1
def _advance_past_comment(text, i)  # CC=7, fan=2
def _extract_block_ts(text, start_pos)  # CC=12, fan=3 ⚠
def _lineno_at(text, pos)  # CC=1, fan=1
def extract_typescript(path)  # CC=11, fan=13 ⚠
def extract_go(path)  # CC=6, fan=12
def extract_rust(path)  # CC=4, fan=11
def extract_file(path)  # CC=6, fan=6
def load_gitignore(root)  # CC=7, fan=6
def _match_anchored_pattern(rel_str, pat_cmp, is_dir)  # CC=5, fan=5
def _match_unanchored_pattern(name, rel, rel_str, pat_cmp, is_dir)  # CC=7, fan=4
def _path_ignored_by_gitignore(path, root, patterns)  # CC=7, fan=8
def _should_skip_file(p, exts, only_within_resolved, gitignore_root_resolved, gitignore_patterns)  # CC=11, fan=7 ⚠
def scan(root, name_filter, kind_filter, only_within, gitignore_patterns, gitignore_root, ext_filter)  # CC=14, fan=11 ⚠
def _def_key(d)  # CC=1, fan=0
def compare_seed_to_all(seed_defs, all_defs, min_sim, skip_same_name)  # CC=10, fan=5 ⚠
def analyse_group(defs)  # CC=3, fan=6
def classify_similarity(pct)  # CC=5, fan=0
def _short_path(path, root)  # CC=2, fan=3
def render_text(groups, root, min_sim, show_body_lines)  # CC=14, fan=11 ⚠
def render_markdown(groups, root, min_sim)  # CC=12, fan=10 ⚠
def render_seed_text(results, root, top_per_seed, show_body_lines)  # CC=10, fan=10 ⚠
def render_seed_markdown(results, root, top_per_seed)  # CC=7, fan=7
def render_seed_json(results, root)  # CC=3, fan=8
def render_json(groups, root)  # CC=7, fan=9
def _build_argument_parser()  # CC=1, fan=2
def _run_seed_mode(args, root, root_str, gitignore_patterns, ext_set)  # CC=17, fan=13 ⚠
def _build_focus_groups(focus_index, full_index, min_count)  # CC=8, fan=5
def _analyse_and_sort_groups(groups_raw)  # CC=3, fan=5
def _run_focus_mode(args, root, root_str, gitignore_patterns, ext_set)  # CC=11, fan=12 ⚠
def _run_default_mode(args, root, root_str, gitignore_patterns, ext_set)  # CC=12, fan=14 ⚠
def _count_similarity_levels(pairs)  # CC=5, fan=0
def _print_pair_summary(groups_analysed)  # CC=2, fan=2
def main()  # CC=8, fan=13
class Definition:  # Pojedyncza definicja (klasa / funkcja / enum / interface / m
    def __init__(name, kind, path, line_start, line_end, body, lang, bases, decorators)  # CC=3
    def loc()  # CC=3
    def __repr__()  # CC=1
```

### `regres.import_error_toon_report` (`regres/import_error_toon_report.py`)

```python
def toon_quote(value)  # CC=1, fan=1
def parse_args()  # CC=1, fan=3
def run_typecheck(cwd, command)  # CC=7, fan=5
def normalize_file_rel(raw_file, cwd)  # CC=3, fan=6
def parse_ts_errors(log_text, cwd, include_codes)  # CC=7, fan=9
def suggestions_for_error(err)  # CC=9, fan=3
def grouped_errors(errors)  # CC=2, fan=3
def metrics(errors)  # CC=3, fan=3
def to_toon_block_legacy(file_rel, errs, max_errors)  # CC=6, fan=8
def to_toon_global_payload(report, scan_root, max_files, max_errors_per_file)  # CC=10, fan=15 ⚠
def to_toon_compact_per_file(grouped, max_files, max_errors)  # CC=7, fan=9
def render_markdown(report, scan_root, max_files, max_errors_per_file)  # CC=6, fan=14
def main()  # CC=5, fan=14
class TsError:
class ReportData:
```

## Call Graph

*176 nodes · 237 edges · 10 modules · CC̄=1.3*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `print` *(in docs.DEFSCAN)* | 0 | 132 | 0 | **132** |
| `render_text` *(in regres.defscan)* | 14 ⚠ | 2 | 55 | **57** |
| `main` *(in regres.regres_cli)* | 1 | 0 | 53 | **53** |
| `build_parser` *(in regres.refactor)* | 1 | 1 | 49 | **50** |
| `render_seed_text` *(in regres.defscan)* | 10 ⚠ | 1 | 42 | **43** |
| `cmd_hotmap` *(in regres.refactor)* | 16 ⚠ | 0 | 42 | **42** |
| `_handle_auto_decision_flow` *(in regres.doctor_cli)* | 18 ⚠ | 1 | 36 | **37** |
| `_run_seed_mode` *(in regres.defscan)* | 17 ⚠ | 1 | 32 | **33** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/regres
# nodes: 176 | edges: 237 | modules: 10
# CC̄=1.3

HUBS[20]:
  docs.DEFSCAN.print
    CC=0  in:132  out:0  total:132
  regres.defscan.render_text
    CC=14  in:2  out:55  total:57
  regres.regres_cli.main
    CC=1  in:0  out:53  total:53
  regres.refactor.build_parser
    CC=1  in:1  out:49  total:50
  regres.defscan.render_seed_text
    CC=10  in:1  out:42  total:43
  regres.refactor.cmd_hotmap
    CC=16  in:0  out:42  total:42
  regres.doctor_cli._handle_auto_decision_flow
    CC=18  in:1  out:36  total:37
  regres.defscan._run_seed_mode
    CC=17  in:1  out:32  total:33
  regres.defscan.extract_go
    CC=6  in:1  out:32  total:33
  regres.import_error_toon_report.to_toon_global_payload
    CC=10  in:1  out:31  total:32
  regres.regres._render_classification_section
    CC=15  in:1  out:31  total:32
  regres.refactor.cmd_diff
    CC=7  in:0  out:31  total:31
  regres.defscan.c
    CC=2  in:30  out:0  total:30
  regres.regres.trace_name_and_hash_candidates
    CC=13  in:1  out:28  total:29
  regres.regres_cli._extend_if_set
    CC=3  in:27  out:2  total:29
  regres.refactor.cmd_dead
    CC=14  in:0  out:28  total:28
  regres.regres._render_regression_section
    CC=12  in:1  out:26  total:27
  regres.doctor_cli._save_report
    CC=20  in:2  out:25  total:27
  regres.refactor.cmd_similar
    CC=14  in:0  out:26  total:26
  regres.regres.analyze_file
    CC=4  in:1  out:25  total:26

MODULES:
  SUMD  [1 funcs]
    check_version  CC=0  out:0
  docs.DEFSCAN  [1 funcs]
    print  CC=0  out:0
  regres.defscan  [43 funcs]
    __init__  CC=3  out:2
    _advance_past_comment  CC=7  out:6
    _advance_past_string  CC=4  out:1
    _analyse_and_sort_groups  CC=3  out:5
    _build_argument_parser  CC=1  out:18
    _build_focus_groups  CC=8  out:6
    _collect_class_method_ids  CC=5  out:6
    _count_similarity_levels  CC=5  out:0
    _def_key  CC=1  out:0
    _extract_block_ts  CC=12  out:4
  regres.doctor_cli  [5 funcs]
    _build_parser  CC=1  out:22
    _handle_auto_decision_flow  CC=18  out:36
    _refresh_import_error_log  CC=5  out:11
    _save_report  CC=20  out:25
    main  CC=5  out:19
  regres.doctor_config  [4 funcs]
    print_banner_to  CC=4  out:2
    _ensure_env_file  CC=4  out:7
    _parse_env_file  CC=11  out:9
    load_config  CC=14  out:11
  regres.import_error_toon_report  [10 funcs]
    grouped_errors  CC=2  out:3
    main  CC=5  out:20
    metrics  CC=3  out:5
    normalize_file_rel  CC=3  out:8
    parse_args  CC=1  out:11
    parse_ts_errors  CC=7  out:17
    render_markdown  CC=6  out:23
    to_toon_compact_per_file  CC=7  out:15
    to_toon_global_payload  CC=10  out:31
    toon_quote  CC=1  out:3
  regres.refactor  [48 funcs]
    _build_symbol_index  CC=5  out:6
    _collect_file_infos  CC=6  out:14
    _deps_filter_by_word  CC=6  out:7
    _deps_print_all  CC=4  out:4
    _deps_print_word_results  CC=5  out:7
    _find_duplicate_symbols  CC=5  out:9
    _find_external_importers  CC=7  out:8
    _find_md5_duplicates  CC=4  out:8
    _find_name_clusters  CC=4  out:10
    _find_similar_pairs  CC=7  out:15
  regres.regres  [48 funcs]
    _analyze_evolution  CC=12  out:4
    _analyze_import_problems  CC=7  out:9
    _check_absolute_path  CC=4  out:4
    _check_relative_paths  CC=4  out:5
    _classify_import_problem  CC=4  out:4
    _dedupe_paths  CC=3  out:6
    _determine_primary_type  CC=2  out:3
    _render_classification_section  CC=15  out:31
    _render_duplicates_section  CC=5  out:12
    _render_evolution_section  CC=6  out:10
  regres.regres_cli  [6 funcs]
    _append_if_true  CC=2  out:1
    _build_defscan_argv  CC=1  out:11
    _build_doctor_argv  CC=1  out:24
    _build_ier_argv  CC=1  out:6
    _extend_if_set  CC=3  out:2
    main  CC=1  out:53
  regres.version_check  [10 funcs]
    _find_env_path  CC=3  out:4
    _get_pypi_version  CC=2  out:6
    _is_newer  CC=1  out:2
    _parse_version  CC=3  out:4
    _read_env  CC=6  out:9
    _save_last_check  CC=1  out:5
    _save_skip_preference  CC=1  out:2
    _should_check  CC=5  out:5
    _write_env  CC=10  out:19
    check_version  CC=7  out:17

EDGES:
  regres.regres._check_relative_paths → regres.regres._dedupe_paths
  regres.regres._search_by_name_suffix → regres.regres._dedupe_paths
  regres.regres.resolve_target_file → regres.regres._check_absolute_path
  regres.regres.resolve_target_file → regres.regres._check_relative_paths
  regres.regres.resolve_target_file → regres.regres._search_by_name_suffix
  regres.regres.content_metrics → regres.regres.sha256_of_file
  regres.regres.check_imports_at_commit → regres.regres.extract_local_imports
  regres.regres.check_imports_at_commit → regres.regres.file_content_at_commit
  regres.regres.check_imports_at_commit → regres.regres.safe_read_text
  regres.regres.find_last_working_commit → regres.regres.check_imports_at_commit
  regres.regres.search_missing_in_history → regres.regres.run_git
  regres.regres.analyze_regression → regres.regres.check_imports_at_commit
  regres.regres.analyze_regression → regres.regres.find_last_working_commit
  regres.regres.analyze_regression → regres.regres.search_missing_in_history
  regres.regres.track_filename_history → regres.regres.run_git
  regres.regres._classify_import_problem → regres.regres.find_current_locations
  regres.regres._determine_primary_type → regres.regres._analyze_evolution
  regres.regres._determine_primary_type → regres.regres._analyze_import_problems
  regres.regres.classify_problem → regres.regres.extract_symbols
  regres.regres.classify_problem → regres.regres._determine_primary_type
  regres.regres.classify_problem → regres.regres._classify_import_problem
  regres.regres.classify_problem → regres.regres.track_filename_history
  regres.regres.dependency_tree → regres.regres.to_rel
  regres.regres.dependency_tree → regres.regres.safe_read_text
  regres.regres.dependency_tree → regres.regres.resolve_local_import
  regres.regres.reverse_references → regres.regres.to_rel
  regres.regres.reverse_references → regres.regres.safe_read_text
  regres.regres.reverse_references → regres.regres.resolve_local_import
  regres.regres.exact_and_near_duplicates → regres.regres.sha256_of_file
  regres.regres.exact_and_near_duplicates → regres.regres.safe_read_text
  regres.regres.exact_and_near_duplicates → regres.regres.to_rel
  regres.regres.trace_name_and_hash_candidates → regres.regres.to_rel
  regres.regres.trace_name_and_hash_candidates → regres.regres.safe_read_text
  regres.regres.trace_name_and_hash_candidates → regres.regres.sha256_of_file
  regres.regres.file_lineage → regres.regres.run_git
  regres.regres.file_lineage → regres.regres.parse_numstat_block
  regres.regres.changed_files_for_commit → regres.regres.run_git
  regres.regres.references_in_recent_commits → regres.regres.changed_files_for_commit
  regres.regres.file_content_at_commit → regres.regres.run_git
  regres.regres.historical_dependency_tree → regres.regres.file_content_at_commit
  regres.regres.historical_dependency_tree → regres.regres.resolve_import_historical
  regres.regres.analyze_evolution → regres.regres.file_content_at_commit
  regres.regres.analyze_evolution → regres.regres.historical_dependency_tree
  regres.regres.render_markdown → regres.regres._render_classification_section
  regres.regres.render_markdown → regres.regres._render_name_hash_section
  regres.regres.render_markdown → regres.regres._render_metrics_section
  regres.regres.render_markdown → regres.regres._render_references_section
  regres.regres.render_markdown → regres.regres._render_duplicates_section
  regres.regres.render_markdown → regres.regres._render_lineage_section
  regres.regres.render_markdown → regres.regres._render_evolution_section
```

## Test Contracts

*Scenarios as contract signatures — what the system guarantees.*

### Cli (1)

**`CLI Command Tests`**

## Intent

Regression/import diagnostics helpers with TOON reports
