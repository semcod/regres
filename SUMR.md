# regres

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Workflows](#workflows)
- [Source Map](#source-map)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Refactoring Analysis](#refactoring-analysis)
- [Intent](#intent)

## Metadata

- **name**: `regres`
- **version**: `0.1.56`
- **python_requires**: `>=3.11`
- **license**: {'text': 'Apache-2.0'}
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Makefile, testql(1), app.doql.less, goal.yaml, src(11 mod), project/(5 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: regres;
  version: 0.1.56;
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

## Workflows

## Source Map

*Top 5 modules by symbol density — signatures for LLM orientation.*

### `regres.doctor_orchestrator` (`regres/doctor_orchestrator.py`)

```python
class DoctorOrchestrator:  # Orchestrator analizy i generator akcji.
    def __init__(scan_root, config)  # CC=1
    def resolve_symlink(path)  # CC=2
    def _discover_module_path_map()  # CC=1
    def _to_rel_path(path)  # CC=1
    def _discover_monorepo_frontend_roots(discovered)  # CC=5
    def _discover_flat_frontend_roots(discovered)  # CC=5
    def _discover_backend_only_roots(discovered)  # CC=5
    def _apply_fallback_entries(discovered)  # CC=4
    def _get_module_path_map()  # CC=2
    def _get_url_route_module_hints()  # CC=1
    def build_project_relation_map()  # CC=3
    def _init_relation_structure()  # CC=1
    def _collect_module_files(module_map)  # CC=7
    def _filter_scoped_files(module_files, max_files)  # CC=5
    def _analyze_imports(scoped_files)  # CC=6
    def _detect_duplicates(scoped_files)  # CC=7
    def _build_relation_summary(module_nodes, scoped_files, module_files, imports_edges, missing_imports, by_name, by_content, include_git)  # CC=3
    def _collect_git_relation_changes()  # CC=14 ⚠
    def _rel_or_abs(path)  # CC=2
    def analyze_from_url(url)  # CC=8
    def analyze_dependency_chain(target_file, max_depth)  # CC=3
    def _process_imports_at_file(current, depth, max_depth, visited)  # CC=10 ⚠
    def _get_file_key(file_path)  # CC=2
    def _build_import_entry(current, from_rel, raw, depth)  # CC=1
    def _check_page_stub(resolved)  # CC=6
    def _get_resolved_rel_path(resolved)  # CC=3
    def _extract_relative_imports(text)  # CC=5
    def _resolve_relative_import(from_file, raw_import)  # CC=7
    def _map_workspace_to_frontend(file_path)  # CC=2
    def _find_symlink_base(file_path)  # CC=5
    def probe_vite_runtime(vite_base, file_rel, timeout)  # CC=11 ⚠
    def analyze_module_loader_compliance(module_path, module_name)  # CC=10 ⚠
    def analyze_page_registry_compliance(module_path, module_name)  # CC=4
    def _read_registry_file(entry)  # CC=4
    def _extract_default_page(text)  # CC=2
    def _extract_registry_name(text)  # CC=2
    def _extract_registry_keys(text, registry_name)  # CC=3
    def _is_default_page_present(default_page, keys)  # CC=1
    def _get_relative_path(entry)  # CC=2
    def _build_registry_diagnosis(rel, default_page, registry_name, keys)  # CC=3
    def _build_registry_nlp(rel, default_page, registry_name, keys)  # CC=4
    def analyze_page_implementations(route_path, module_path, module_name)  # CC=5
    def analyze_runtime_console(log_path)  # CC=13 ⚠
    def _extract_page_token(route_path, module_name)  # CC=10 ⚠
    def _find_page_files(module_path, page_token)  # CC=7
    def _check_page_stub_indicators(text, line_count)  # CC=4
    def _detect_content_regression(line_count, history_candidates, has_placeholder)  # CC=5
    def _build_stub_diagnosis_actions(relative_str, line_count, max_historical_lines, has_placeholder, is_short_stub, empty_render, is_content_regression, page_token)  # CC=7
    def _add_backup_candidate(backup_candidate, relative_str, actions, commands, nlp_lines)  # CC=2
    def _add_history_candidates(history_candidates, relative_str, actions, commands, nlp_lines)  # CC=7
    def _diagnose_page_stub(page_file, page_token, module_name)  # CC=12 ⚠
    def _collect_page_history_candidates(page_token, module_name, current_file, days, iterations)  # CC=3
    def _resolve_history_params(days, iterations)  # CC=3
    def _run_git_history_query(page_token, iterations)  # CC=4
    def _parse_history_output(stdout, page_token)  # CC=5
    def _parse_commit_line(line, current_commit)  # CC=4
    def _try_extract_candidate(line, page_token, commit, seen_keys)  # CC=7
    def _get_file_at_commit(full_hash, file_path)  # CC=3
    def _dedupe_and_limit_candidates(candidates, iterations)  # CC=4
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
    def generate_patch_scripts(out_dir, basename)  # CC=9
    def _extract_history_candidates(diag)  # CC=5
    def _find_primary_target(diag, history_candidates)  # CC=6
    def _generate_history_patch(diag, diag_idx, cand_idx, cand_action, history_candidates, primary_target, out_dir, basename, counter)  # CC=4
    def _try_generate_generic_patch(diag, diag_idx, out_dir, basename, counter)  # CC=4
    def _write_script(path, lines)  # CC=2
    def _render_patch_script(diag, diag_idx, cand_idx, total_cands, git_hash, source_path, target_path, reason)  # CC=1
    def _render_generic_patch_script(diag, diag_idx, target_path)  # CC=2
    def _render_project_relation_map(report)  # CC=5
    def _extract_module_name(path)  # CC=6
    def _resolve_module_path(module_name)  # CC=5
    def _import_exists_in_source(file_path, module_name)  # CC=11 ⚠
    def _resolve_alias_target(alias_path)  # CC=6
    def _parse_ts_errors(log_path)  # CC=6
    def _validate_errors(file_path, errors)  # CC=4
    def _extract_missing_modules(errors)  # CC=3
    def _diagnose_import_issue(file_path, missing_modules)  # CC=6
    def _handle_c2004_alias_import(module, file_path, actions, commands, concrete_fixes)  # CC=2
    def _handle_relative_import(module, file_path, actions, commands)  # CC=4
    def _build_import_nlp_description(file_path, missing_modules, concrete_fixes)  # CC=2
    def _determine_import_severity(missing_modules, concrete_fixes, actions)  # CC=5
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
    def _render_affected_files(report)  # CC=4
    def _render_affected_file_entry(entry, patch_index)  # CC=10 ⚠
    def _render_direct_actions(direct)  # CC=4
    def _render_git_candidates(git_cands, target_path, patch_index)  # CC=3
    def _render_git_candidate(action, target_path, patch_index)  # CC=5
    def _build_candidate_patch_index(report)  # CC=11 ⚠
    def _render_dependency_chain(report)  # CC=4
    def _render_chain_header()  # CC=1
    def _render_single_chain_entry(entry)  # CC=3
    def _categorize_chain_imports(chain)  # CC=8
    def _render_chain_summary(total, ok, broken, stubs)  # CC=1
    def _render_broken_imports(broken)  # CC=4
    def _render_stub_imports(stubs)  # CC=3
    def _render_suggested_command(path, kind)  # CC=3
    def _render_ok_chain_status(ok, broken, stubs)  # CC=4
    def _render_repair_plan_if_needed(chains)  # CC=6
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
class _PatchIndexBuilder:  # Helper class to build patch index file content.
    def __init__(basename)  # CC=1
    def add_history_entry(path, problem_type, candidate, target)  # CC=1
    def add_manual_entry(path, problem_type, target)  # CC=1
    def write(out_dir)  # CC=2
```

### `regres.refactor` (`regres/refactor.py`)

```python
def iter_files(root, extensions, word_filter, case_sensitive, ext_filter)  # CC=7, fan=4
def _is_valid_file(p, exts)  # CC=7, fan=4
def _file_contains_word(p, word_filter, case_sensitive)  # CC=4, fan=2
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
def wrapper_score(text)  # CC=1, fan=7
def _check_wrapper_signatures(text, score, reasons)  # CC=3, fan=2
def _check_file_length(text, score, reasons)  # CC=4, fan=4
def _check_import_density(text, score, reasons)  # CC=7, fan=6
def _check_sys_manipulation(text, score, reasons)  # CC=3, fan=1
def _check_barrel_export(text, score, reasons)  # CC=2, fan=2
def _check_dynamic_import(text, score, reasons)  # CC=3, fan=1
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
def cmd_hotmap(args, root)  # CC=2, fan=6
def _collect_and_normalize_files(root, word, normalize)  # CC=5, fan=8
def _count_files_per_dir(paths_list)  # CC=2, fan=3
def _count_similar_pairs(paths_list, texts, threshold, dir_file_count)  # CC=6, fan=6
def _calculate_hotmap(dir_file_count, dir_pair_count)  # CC=2, fan=6
def _render_hotmap_output(args, hotmap, paths_list, total_pairs, threshold, normalize)  # CC=4, fan=5
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
def _render_classification_section(classification, lines)  # CC=2, fan=6
def _render_classification_header(classification, lines)  # CC=2, fan=2
def _render_evidence(classification, lines)  # CC=3, fan=2
def _render_import_problems(classification, lines)  # CC=5, fan=3
def _render_current_symbols(classification, lines)  # CC=3, fan=4
def _render_filename_history(classification, lines)  # CC=5, fan=2
def _render_name_hash_section(nh, lines)  # CC=5, fan=4
def _render_metrics_section(m, lines)  # CC=1, fan=1
def _render_references_section(refs, lines)  # CC=3, fan=3
def _render_duplicates_section(d, lines)  # CC=5, fan=4
def _render_lineage_section(lineage, lines)  # CC=2, fan=1
def _render_evolution_section(evolution, lines)  # CC=6, fan=3
def _render_last_good_section(last_good, lines)  # CC=3, fan=1
def _render_regression_section(regression, lines)  # CC=3, fan=7
def _render_broken_imports(regression, lines)  # CC=2, fan=3
def _render_last_working_commit(regression, lines)  # CC=2, fan=2
def _render_first_broken_commit(regression, lines)  # CC=2, fan=2
def _render_missing_imports_history(regression, lines)  # CC=5, fan=2
def _render_recommendations(regression, lines)  # CC=3, fan=3
def render_markdown(report)  # CC=1, fan=13
def analyze_file(target_file, scan_root, max_commits, tree_depth, near_threshold)  # CC=4, fan=22
def _resolve_output_path(path_str, cwd)  # CC=2, fan=4
def main()  # CC=6, fan=15
class GitCommit:
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
def _run_seed_mode(args, root, root_str, gitignore_patterns, ext_set)  # CC=2, fan=9
def _resolve_seed_params(args, root)  # CC=4, fan=5
def _print_seed_header(seed_path, scope_path, min_sim)  # CC=1, fan=1
def _scan_all_definitions(scope_path, args, gitignore_patterns, root, ext_set)  # CC=5, fan=2
def _scan_seed_definitions(scope_path, seed_path, args, gitignore_patterns, root, ext_set)  # CC=5, fan=2
def _compare_seed_similarity(seed_defs, all_defs, min_sim, args)  # CC=2, fan=1
def _render_seed_results(results, root_str, args)  # CC=3, fan=4
def _print_seed_summary(results)  # CC=2, fan=3
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

### `regres.doctor_cli` (`regres/doctor_cli.py`)

```python
def _append_url_module_not_found_diagnosis(doctor, scan_root, module_name, args_url)  # CC=3, fan=4
def _run_page_implementation_analysis(args, doctor, scan_root, normalized_path, module_name, module_path)  # CC=2, fan=8
def _run_module_loader_compliance_check(doctor, module_path, module_name)  # CC=2, fan=4
def _create_import_chain_diagnoses(doctor, scan_root, chains_data, module_name)  # CC=3, fan=2
def _create_single_chain_diagnosis(entry, doctor, scan_root, module_name)  # CC=9, fan=7
def _build_chain_nlp_description(target_rel, broken, stubs)  # CC=1, fan=1
def _build_file_actions_for_chain(target_rel, doctor, scan_root, module_name)  # CC=4, fan=5
def _format_history_reason(hc)  # CC=2, fan=1
def _build_shell_commands_for_chain(broken, stubs, scan_root, doctor)  # CC=1, fan=3
def _build_commands_for_broken(broken, scan_root, doctor)  # CC=3, fan=6
def _build_commands_for_stubs(stubs, scan_root, doctor)  # CC=3, fan=5
def _build_regres_command(scan_root, url_hint, path)  # CC=1, fan=1
def _derive_vite_base(args)  # CC=6, fan=2
def _run_vite_runtime_probe(args, doctor, scan_root, chain_targets, vite_base)  # CC=13, fan=16 ⚠
def _create_vite_runtime_diagnoses(doctor, scan_root, vite_results, vite_base)  # CC=10, fan=7 ⚠
def _collect_dependency_chain_targets(doctor, scan_root, page_diagnoses, module_path, page_token)  # CC=12, fan=4 ⚠
def _run_dependency_chain_analysis(args, doctor, scan_root, chain_targets)  # CC=8, fan=11
def _run_page_registry_compliance_check(doctor, module_path, module_name)  # CC=2, fan=4
def _run_llm_or_targeted_analysis(args, doctor, scan_root, module_path)  # CC=3, fan=7
def _run_url_module_analysis(args, doctor, scan_root, normalized_path, module_name, module_path)  # CC=5, fan=11
def _resolve_runtime_log_path(args, scan_root)  # CC=7, fan=6
def _handle_runtime_log_diagnostics(args, doctor, scan_root)  # CC=6, fan=8
def _handle_url_mode(args, doctor, scan_root)  # CC=1, fan=8
def _resolve_module_from_url(doctor, normalized_path)  # CC=8, fan=6
def _record_url_discovery_step(doctor, scan_root, url, normalized_path, module_name, route_hint)  # CC=5, fan=2
def _setup_url_analysis_context(args, doctor, normalized_path, module_name, route_hint)  # CC=2, fan=6
def _handle_module_resolution(args, doctor, scan_root, normalized_path, module_name)  # CC=4, fan=7
def _record_module_not_found_step(doctor)  # CC=1, fan=1
def _record_module_resolution_step(doctor, module_path, path_exists)  # CC=3, fan=1
def _apply_fixes_if_requested(args, doctor)  # CC=5, fan=3
def _handle_import_errors(args, doctor, scan_root, refresh_fn)  # CC=10, fan=5 ⚠
def _handle_defscan_refactor(args, doctor)  # CC=4, fan=5
def _handle_auto_decision_flow(args, doctor, scan_root, refresh_fn)  # CC=3, fan=8
def _setup_analysis_context(args, doctor, scan_root)  # CC=2, fan=6
def _run_prescans(doctor, scan_root)  # CC=1, fan=4
def _run_import_analysis(args, doctor, scan_root, refresh_fn)  # CC=5, fan=5
def _get_import_log_path(args, scan_root)  # CC=2, fan=1
def _refresh_import_log(doctor, scan_root, import_log, refresh_fn)  # CC=3, fan=2
def _run_regress_history_phase(doctor, import_diagnoses)  # CC=3, fan=5
def _collect_affected_files(diagnoses)  # CC=4, fan=3
def _run_additional_scans(args, doctor, scan_root)  # CC=4, fan=6
def _save_report(doctor, args)  # CC=5, fan=8
def _derive_output_basename(args)  # CC=3, fan=1
def _resolve_patches_dir(args, out_dir)  # CC=3, fan=3
def _generate_and_attach_patches(doctor, patches_dir, basename, args, report)  # CC=4, fan=2
def _save_json_report(report, out_json_path)  # CC=1, fan=4
def _save_markdown_report(doctor, report, out_md_path, generated_patches)  # CC=2, fan=6
def _print_patches_info(patches, patches_dir)  # CC=6, fan=2
def _print_report_to_stdout(doctor, report, generated_patches)  # CC=2, fan=4
def _render_patches_section(patches)  # CC=10, fan=5 ⚠
def _refresh_import_error_log(project_root, log_path)  # CC=5, fan=7
def _build_parser()  # CC=1, fan=2
def main()  # CC=5, fan=13
```

## Call Graph

*250 nodes · 331 edges · 10 modules · CC̄=1.0*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `print` *(in docs.DEFSCAN)* | 0 | 132 | 0 | **132** |
| `render_text` *(in regres.defscan)* | 14 ⚠ | 2 | 55 | **57** |
| `main` *(in regres.regres_cli)* | 1 | 0 | 54 | **54** |
| `build_parser` *(in regres.refactor)* | 1 | 1 | 49 | **50** |
| `render_seed_text` *(in regres.defscan)* | 10 ⚠ | 1 | 42 | **43** |
| `extract_go` *(in regres.defscan)* | 6 | 1 | 32 | **33** |
| `to_toon_global_payload` *(in regres.import_error_toon_report)* | 10 ⚠ | 1 | 31 | **32** |
| `cmd_diff` *(in regres.refactor)* | 7 | 0 | 31 | **31** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/regres
# nodes: 250 | edges: 331 | modules: 10
# CC̄=1.0

HUBS[20]:
  docs.DEFSCAN.print
    CC=0  in:132  out:0  total:132
  regres.defscan.render_text
    CC=14  in:2  out:55  total:57
  regres.regres_cli.main
    CC=1  in:0  out:54  total:54
  regres.refactor.build_parser
    CC=1  in:1  out:49  total:50
  regres.defscan.render_seed_text
    CC=10  in:1  out:42  total:43
  regres.defscan.extract_go
    CC=6  in:1  out:32  total:33
  regres.import_error_toon_report.to_toon_global_payload
    CC=10  in:1  out:31  total:32
  regres.refactor.cmd_diff
    CC=7  in:0  out:31  total:31
  regres.defscan.c
    CC=2  in:30  out:0  total:30
  regres.regres_cli._extend_if_set
    CC=3  in:28  out:2  total:30
  regres.regres.trace_name_and_hash_candidates
    CC=13  in:1  out:28  total:29
  regres.refactor.cmd_dead
    CC=14  in:0  out:28  total:28
  regres.regres_cli._build_doctor_argv
    CC=1  in:1  out:26  total:27
  regres.refactor.cmd_similar
    CC=14  in:0  out:26  total:26
  regres.regres.analyze_file
    CC=4  in:1  out:25  total:26
  regres.doctor_cli._render_patches_section
    CC=10  in:2  out:24  total:26
  regres.refactor.cmd_cluster
    CC=12  in:0  out:25  total:25
  regres.regres.exact_and_near_duplicates
    CC=8  in:1  out:24  total:25
  regres.import_error_toon_report.render_markdown
    CC=6  in:1  out:23  total:24
  regres.regres.resolve_target_file
    CC=13  in:1  out:23  total:24

MODULES:
  docs.DEFSCAN  [1 funcs]
    print  CC=0  out:0
  project.map.toon  [1 funcs]
    _normalize  CC=0  out:0
  regres.defscan  [49 funcs]
    __init__  CC=3  out:2
    _advance_past_comment  CC=7  out:6
    _advance_past_string  CC=4  out:1
    _analyse_and_sort_groups  CC=3  out:5
    _build_argument_parser  CC=1  out:18
    _build_focus_groups  CC=8  out:6
    _collect_class_method_ids  CC=5  out:6
    _compare_seed_similarity  CC=2  out:1
    _count_similarity_levels  CC=5  out:0
    _def_key  CC=1  out:0
  regres.doctor_cli  [50 funcs]
    _append_url_module_not_found_diagnosis  CC=3  out:4
    _apply_fixes_if_requested  CC=5  out:6
    _build_chain_nlp_description  CC=1  out:2
    _build_commands_for_broken  CC=3  out:8
    _build_commands_for_stubs  CC=3  out:5
    _build_file_actions_for_chain  CC=4  out:6
    _build_parser  CC=1  out:23
    _build_regres_command  CC=1  out:1
    _build_shell_commands_for_chain  CC=1  out:4
    _collect_affected_files  CC=4  out:3
  regres.doctor_config  [4 funcs]
    print_banner_to  CC=4  out:2
    _ensure_env_file  CC=4  out:10
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
  regres.refactor  [61 funcs]
    _build_symbol_index  CC=5  out:6
    _calculate_hotmap  CC=2  out:6
    _check_barrel_export  CC=2  out:2
    _check_dynamic_import  CC=3  out:1
    _check_file_length  CC=4  out:5
    _check_import_density  CC=7  out:10
    _check_sys_manipulation  CC=3  out:1
    _check_wrapper_signatures  CC=3  out:2
    _collect_and_normalize_files  CC=5  out:8
    _collect_file_infos  CC=6  out:14
  regres.regres  [58 funcs]
    _analyze_evolution  CC=12  out:4
    _analyze_import_problems  CC=7  out:9
    _check_absolute_path  CC=4  out:4
    _check_relative_paths  CC=4  out:5
    _classify_import_problem  CC=4  out:4
    _dedupe_paths  CC=3  out:6
    _determine_primary_type  CC=2  out:3
    _render_broken_imports  CC=2  out:5
    _render_classification_header  CC=2  out:5
    _render_classification_section  CC=2  out:6
  regres.regres_cli  [6 funcs]
    _append_if_true  CC=2  out:1
    _build_defscan_argv  CC=1  out:11
    _build_doctor_argv  CC=1  out:26
    _build_ier_argv  CC=1  out:6
    _extend_if_set  CC=3  out:2
    main  CC=1  out:54
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
  regres.doctor_config.DoctorConfig.print_banner_to → docs.DEFSCAN.print
  regres.doctor_config.load_config → regres.doctor_config._ensure_env_file
  regres.doctor_config.load_config → regres.doctor_config._parse_env_file
  regres.version_check._read_env → regres.version_check._find_env_path
  regres.version_check._write_env → regres.version_check._find_env_path
  regres.version_check._is_newer → regres.version_check._parse_version
  regres.version_check._should_check → regres.version_check._read_env
  regres.version_check._save_last_check → regres.version_check._read_env
  regres.version_check._save_last_check → regres.version_check._write_env
  regres.version_check._save_skip_preference → regres.version_check._read_env
  regres.version_check._save_skip_preference → regres.version_check._write_env
  regres.version_check.check_version → regres.version_check._get_pypi_version
  regres.version_check.check_version → regres.version_check._save_last_check
  regres.version_check.check_version → regres.version_check._is_newer
  regres.version_check.check_version → regres.version_check._should_check
  regres.version_check.check_version → docs.DEFSCAN.print
  regres.doctor_cli._create_import_chain_diagnoses → regres.doctor_cli._create_single_chain_diagnosis
  regres.doctor_cli._create_single_chain_diagnosis → regres.doctor_cli._build_chain_nlp_description
  regres.doctor_cli._create_single_chain_diagnosis → regres.doctor_cli._build_file_actions_for_chain
  regres.doctor_cli._create_single_chain_diagnosis → regres.doctor_cli._build_shell_commands_for_chain
  regres.doctor_cli._build_file_actions_for_chain → regres.doctor_cli._format_history_reason
  regres.doctor_cli._build_shell_commands_for_chain → regres.doctor_cli._build_commands_for_broken
  regres.doctor_cli._build_shell_commands_for_chain → regres.doctor_cli._build_commands_for_stubs
  regres.doctor_cli._build_commands_for_broken → regres.doctor_cli._build_regres_command
  regres.doctor_cli._build_commands_for_stubs → regres.doctor_cli._build_regres_command
  regres.doctor_cli._run_llm_or_targeted_analysis → docs.DEFSCAN.print
  regres.doctor_cli._run_url_module_analysis → regres.doctor_cli._run_page_implementation_analysis
  regres.doctor_cli._run_url_module_analysis → regres.doctor_cli._run_module_loader_compliance_check
  regres.doctor_cli._run_url_module_analysis → regres.doctor_cli._run_page_registry_compliance_check
  regres.doctor_cli._run_url_module_analysis → regres.doctor_cli._collect_dependency_chain_targets
  regres.doctor_cli._run_url_module_analysis → regres.doctor_cli._run_llm_or_targeted_analysis
  regres.doctor_cli._run_url_module_analysis → regres.doctor_cli._run_dependency_chain_analysis
  regres.doctor_cli._run_url_module_analysis → regres.doctor_cli._derive_vite_base
  regres.doctor_cli._run_url_module_analysis → regres.doctor_cli._create_import_chain_diagnoses
  regres.doctor_cli._run_url_module_analysis → regres.doctor_cli._run_vite_runtime_probe
  regres.doctor_cli._handle_runtime_log_diagnostics → regres.doctor_cli._resolve_runtime_log_path
  regres.doctor_cli._handle_url_mode → regres.doctor_cli._resolve_module_from_url
  regres.doctor_cli._handle_url_mode → regres.doctor_cli._record_url_discovery_step
  regres.doctor_cli._handle_url_mode → regres.doctor_cli._setup_url_analysis_context
  regres.doctor_cli._handle_url_mode → regres.doctor_cli._handle_module_resolution
  regres.doctor_cli._handle_url_mode → regres.doctor_cli._apply_fixes_if_requested
  regres.doctor_cli._setup_url_analysis_context → regres.doctor_cli._handle_runtime_log_diagnostics
  regres.doctor_cli._handle_module_resolution → regres.doctor_cli._record_module_resolution_step
  regres.doctor_cli._handle_module_resolution → regres.doctor_cli._record_module_not_found_step
  regres.doctor_cli._handle_module_resolution → regres.doctor_cli._append_url_module_not_found_diagnosis
  regres.doctor_cli._handle_module_resolution → regres.doctor_cli._run_url_module_analysis
  regres.doctor_cli._apply_fixes_if_requested → docs.DEFSCAN.print
  regres.doctor_cli._handle_auto_decision_flow → regres.doctor_cli._setup_analysis_context
  regres.doctor_cli._handle_auto_decision_flow → regres.doctor_cli._run_import_analysis
  regres.doctor_cli._handle_auto_decision_flow → regres.doctor_cli._run_additional_scans
```

## Test Contracts

*Scenarios as contract signatures — what the system guarantees.*

### Cli (1)

**`CLI Command Tests`**

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/regres
# nodes: 250 | edges: 331 | modules: 10
# CC̄=1.0

HUBS[20]:
  docs.DEFSCAN.print
    CC=0  in:132  out:0  total:132
  regres.defscan.render_text
    CC=14  in:2  out:55  total:57
  regres.regres_cli.main
    CC=1  in:0  out:54  total:54
  regres.refactor.build_parser
    CC=1  in:1  out:49  total:50
  regres.defscan.render_seed_text
    CC=10  in:1  out:42  total:43
  regres.defscan.extract_go
    CC=6  in:1  out:32  total:33
  regres.import_error_toon_report.to_toon_global_payload
    CC=10  in:1  out:31  total:32
  regres.refactor.cmd_diff
    CC=7  in:0  out:31  total:31
  regres.defscan.c
    CC=2  in:30  out:0  total:30
  regres.regres_cli._extend_if_set
    CC=3  in:28  out:2  total:30
  regres.regres.trace_name_and_hash_candidates
    CC=13  in:1  out:28  total:29
  regres.refactor.cmd_dead
    CC=14  in:0  out:28  total:28
  regres.regres_cli._build_doctor_argv
    CC=1  in:1  out:26  total:27
  regres.refactor.cmd_similar
    CC=14  in:0  out:26  total:26
  regres.regres.analyze_file
    CC=4  in:1  out:25  total:26
  regres.doctor_cli._render_patches_section
    CC=10  in:2  out:24  total:26
  regres.refactor.cmd_cluster
    CC=12  in:0  out:25  total:25
  regres.regres.exact_and_near_duplicates
    CC=8  in:1  out:24  total:25
  regres.import_error_toon_report.render_markdown
    CC=6  in:1  out:23  total:24
  regres.regres.resolve_target_file
    CC=13  in:1  out:23  total:24

MODULES:
  docs.DEFSCAN  [1 funcs]
    print  CC=0  out:0
  project.map.toon  [1 funcs]
    _normalize  CC=0  out:0
  regres.defscan  [49 funcs]
    __init__  CC=3  out:2
    _advance_past_comment  CC=7  out:6
    _advance_past_string  CC=4  out:1
    _analyse_and_sort_groups  CC=3  out:5
    _build_argument_parser  CC=1  out:18
    _build_focus_groups  CC=8  out:6
    _collect_class_method_ids  CC=5  out:6
    _compare_seed_similarity  CC=2  out:1
    _count_similarity_levels  CC=5  out:0
    _def_key  CC=1  out:0
  regres.doctor_cli  [50 funcs]
    _append_url_module_not_found_diagnosis  CC=3  out:4
    _apply_fixes_if_requested  CC=5  out:6
    _build_chain_nlp_description  CC=1  out:2
    _build_commands_for_broken  CC=3  out:8
    _build_commands_for_stubs  CC=3  out:5
    _build_file_actions_for_chain  CC=4  out:6
    _build_parser  CC=1  out:23
    _build_regres_command  CC=1  out:1
    _build_shell_commands_for_chain  CC=1  out:4
    _collect_affected_files  CC=4  out:3
  regres.doctor_config  [4 funcs]
    print_banner_to  CC=4  out:2
    _ensure_env_file  CC=4  out:10
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
  regres.refactor  [61 funcs]
    _build_symbol_index  CC=5  out:6
    _calculate_hotmap  CC=2  out:6
    _check_barrel_export  CC=2  out:2
    _check_dynamic_import  CC=3  out:1
    _check_file_length  CC=4  out:5
    _check_import_density  CC=7  out:10
    _check_sys_manipulation  CC=3  out:1
    _check_wrapper_signatures  CC=3  out:2
    _collect_and_normalize_files  CC=5  out:8
    _collect_file_infos  CC=6  out:14
  regres.regres  [58 funcs]
    _analyze_evolution  CC=12  out:4
    _analyze_import_problems  CC=7  out:9
    _check_absolute_path  CC=4  out:4
    _check_relative_paths  CC=4  out:5
    _classify_import_problem  CC=4  out:4
    _dedupe_paths  CC=3  out:6
    _determine_primary_type  CC=2  out:3
    _render_broken_imports  CC=2  out:5
    _render_classification_header  CC=2  out:5
    _render_classification_section  CC=2  out:6
  regres.regres_cli  [6 funcs]
    _append_if_true  CC=2  out:1
    _build_defscan_argv  CC=1  out:11
    _build_doctor_argv  CC=1  out:26
    _build_ier_argv  CC=1  out:6
    _extend_if_set  CC=3  out:2
    main  CC=1  out:54
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
  regres.doctor_config.DoctorConfig.print_banner_to → docs.DEFSCAN.print
  regres.doctor_config.load_config → regres.doctor_config._ensure_env_file
  regres.doctor_config.load_config → regres.doctor_config._parse_env_file
  regres.version_check._read_env → regres.version_check._find_env_path
  regres.version_check._write_env → regres.version_check._find_env_path
  regres.version_check._is_newer → regres.version_check._parse_version
  regres.version_check._should_check → regres.version_check._read_env
  regres.version_check._save_last_check → regres.version_check._read_env
  regres.version_check._save_last_check → regres.version_check._write_env
  regres.version_check._save_skip_preference → regres.version_check._read_env
  regres.version_check._save_skip_preference → regres.version_check._write_env
  regres.version_check.check_version → regres.version_check._get_pypi_version
  regres.version_check.check_version → regres.version_check._save_last_check
  regres.version_check.check_version → regres.version_check._is_newer
  regres.version_check.check_version → regres.version_check._should_check
  regres.version_check.check_version → docs.DEFSCAN.print
  regres.doctor_cli._create_import_chain_diagnoses → regres.doctor_cli._create_single_chain_diagnosis
  regres.doctor_cli._create_single_chain_diagnosis → regres.doctor_cli._build_chain_nlp_description
  regres.doctor_cli._create_single_chain_diagnosis → regres.doctor_cli._build_file_actions_for_chain
  regres.doctor_cli._create_single_chain_diagnosis → regres.doctor_cli._build_shell_commands_for_chain
  regres.doctor_cli._build_file_actions_for_chain → regres.doctor_cli._format_history_reason
  regres.doctor_cli._build_shell_commands_for_chain → regres.doctor_cli._build_commands_for_broken
  regres.doctor_cli._build_shell_commands_for_chain → regres.doctor_cli._build_commands_for_stubs
  regres.doctor_cli._build_commands_for_broken → regres.doctor_cli._build_regres_command
  regres.doctor_cli._build_commands_for_stubs → regres.doctor_cli._build_regres_command
  regres.doctor_cli._run_llm_or_targeted_analysis → docs.DEFSCAN.print
  regres.doctor_cli._run_url_module_analysis → regres.doctor_cli._run_page_implementation_analysis
  regres.doctor_cli._run_url_module_analysis → regres.doctor_cli._run_module_loader_compliance_check
  regres.doctor_cli._run_url_module_analysis → regres.doctor_cli._run_page_registry_compliance_check
  regres.doctor_cli._run_url_module_analysis → regres.doctor_cli._collect_dependency_chain_targets
  regres.doctor_cli._run_url_module_analysis → regres.doctor_cli._run_llm_or_targeted_analysis
  regres.doctor_cli._run_url_module_analysis → regres.doctor_cli._run_dependency_chain_analysis
  regres.doctor_cli._run_url_module_analysis → regres.doctor_cli._derive_vite_base
  regres.doctor_cli._run_url_module_analysis → regres.doctor_cli._create_import_chain_diagnoses
  regres.doctor_cli._run_url_module_analysis → regres.doctor_cli._run_vite_runtime_probe
  regres.doctor_cli._handle_runtime_log_diagnostics → regres.doctor_cli._resolve_runtime_log_path
  regres.doctor_cli._handle_url_mode → regres.doctor_cli._resolve_module_from_url
  regres.doctor_cli._handle_url_mode → regres.doctor_cli._record_url_discovery_step
  regres.doctor_cli._handle_url_mode → regres.doctor_cli._setup_url_analysis_context
  regres.doctor_cli._handle_url_mode → regres.doctor_cli._handle_module_resolution
  regres.doctor_cli._handle_url_mode → regres.doctor_cli._apply_fixes_if_requested
  regres.doctor_cli._setup_url_analysis_context → regres.doctor_cli._handle_runtime_log_diagnostics
  regres.doctor_cli._handle_module_resolution → regres.doctor_cli._record_module_resolution_step
  regres.doctor_cli._handle_module_resolution → regres.doctor_cli._record_module_not_found_step
  regres.doctor_cli._handle_module_resolution → regres.doctor_cli._append_url_module_not_found_diagnosis
  regres.doctor_cli._handle_module_resolution → regres.doctor_cli._run_url_module_analysis
  regres.doctor_cli._apply_fixes_if_requested → docs.DEFSCAN.print
  regres.doctor_cli._handle_auto_decision_flow → regres.doctor_cli._setup_analysis_context
  regres.doctor_cli._handle_auto_decision_flow → regres.doctor_cli._run_import_analysis
  regres.doctor_cli._handle_auto_decision_flow → regres.doctor_cli._run_additional_scans
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 44f 23686L | md:17,python:13,yaml:9,shell:2,toml:1,txt:1 | 2026-05-01
# CC̄=1.0 | critical:0/2033 | dups:0 | cycles:0

HEALTH[2]:
  🔴 GOD   SUMR.md = 1140L, 4 classes, 346m, max CC=0.0
  🔴 GOD   SUMD.md = 1507L, 4 classes, 706m, max CC=0.0

REFACTOR[2]:
  1. split SUMR.md  (god module)
  2. split SUMD.md  (god module)

PIPELINES[161]:
  [1] Src [print_banner_to]: print_banner_to → print
      PURITY: 100% pure
  [2] Src [_handle_import_errors]: _handle_import_errors
      PURITY: 100% pure
  [3] Src [_handle_defscan_refactor]: _handle_defscan_refactor
      PURITY: 100% pure
  [4] Src [_refresh_import_error_log]: _refresh_import_error_log → print
      PURITY: 100% pure
  [5] Src [main]: main → check_version → _get_pypi_version
      PURITY: 100% pure

LAYERS:
  regres/                         CC̄=4.8    ←in:0  →out:133  !! split
  │ !! doctor_orchestrator       3586L  2C  148m  CC=14     ←0
  │ !! regres                    1545L  1C   65m  CC=13     ←1
  │ !! doctor_cli                1365L  0C   53m  CC=13     ←0
  │ !! refactor                  1323L  0C   65m  CC=14     ←2
  │ !! defscan                   1296L  1C   52m  CC=14     ←2
  │ import_error_toon_report   372L  2C   13m  CC=10     ←0
  │ doctor_config              269L  1C    5m  CC=14     ←1
  │ regres_cli                 211L  0C    9m  CC=7      ←0
  │ version_check              185L  0C   10m  CC=10     ←3
  │ doctor_models               36L  3C    0m  CC=0.0    ←0
  │ __init__                    20L  0C    0m  CC=0.0    ←0
  │ doctor                       6L  0C    0m  CC=0.0    ←0
  │
  docs/                           CC̄=0.0    ←in:132  →out:0
  │ !! README.md                 1320L  0C    1m  CC=0.0    ←0
  │ DOCTOR.md                  227L  1C    1m  CC=0.0    ←0
  │ REGRES.md                  220L  0C    0m  CC=0.0    ←0
  │ DEFSCAN.md                 164L  0C    1m  CC=0.0    ←7
  │ REFACTOR.md                 87L  0C    0m  CC=0.0    ←0
  │ import-error-toon-report.md    76L  0C    0m  CC=0.0    ←0
  │
  project/                        CC̄=0.0    ←in:0  →out:0
  │ !! calls.yaml                4397L  0C    0m  CC=0.0    ←0
  │ !! map.toon.yaml              658L  0C  558m  CC=0.0    ←1
  │ !! context.md                 531L  0C    0m  CC=0.0    ←0
  │ README.md                  339L  0C    0m  CC=0.0    ←0
  │ calls.toon.yaml            179L  0C    0m  CC=0.0    ←0
  │ analysis.toon.yaml         104L  0C    0m  CC=0.0    ←0
  │ evolution.toon.yaml         62L  0C    0m  CC=0.0    ←0
  │ project.toon.yaml           52L  0C    0m  CC=0.0    ←0
  │ prompt.txt                  47L  0C    0m  CC=0.0    ←0
  │ duplication.toon.yaml        9L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! SUMD.md                   1507L  4C  706m  CC=0.0    ←0
  │ !! SUMR.md                   1140L  4C  346m  CC=0.0    ←0
  │ !! CHANGELOG.md               622L  0C    0m  CC=0.0    ←0
  │ !! goal.yaml                  512L  0C    0m  CC=0.0    ←0
  │ README.md                  133L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              54L  0C    0m  CC=0.0    ←0
  │ project.sh                  41L  0C    0m  CC=0.0    ←0
  │ TODO.md                     35L  0C    0m  CC=0.0    ←0
  │ tree.sh                      1L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │
  .regres/                        CC̄=0.0    ←in:0  →out:0
  │ !! import-error-toon-report.md   549L  0C    0m  CC=0.0    ←0
  │ connect-test-reports-doctor.md   283L  0C    0m  CC=0.0    ←0
  │
  scripts/                        CC̄=0.0    ←in:0  →out:0
  │ import-error-toon-report    11L  0C    0m  CC=0.0    ←0
  │
  .windsurf/                      CC̄=0.0    ←in:0  →out:0
  │ c2004-preanalysis-predeploy.md    51L  0C    0m  CC=0.0    ←0
  │ c2004-security-settings-baseline.md    41L  0C    0m  CC=0.0    ←0
  │
  testql-scenarios/               CC̄=0.0    ←in:0  →out:0
  │ generated-cli-tests.testql.toon.yaml    20L  0C    0m  CC=0.0    ←0
  │
  ── zero ──
     Makefile                                  0L

COUPLING:
                    regres         docs  project.map
       regres           ──          132            1  !! fan-out
         docs         ←132           ──               hub
  project.map           ←1                        ──
  CYCLES: none
  HUB: docs/ (fan-in=132)
  SMELL: regres/ fan-out=133 → split needed

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 1 groups | 13f 10225L | 2026-05-01

SUMMARY:
  files_scanned: 13
  total_lines:   10225
  dup_groups:    1
  dup_fragments: 2
  saved_lines:   6
  scan_ms:       2500

HOTSPOTS[1] (files with most duplication):
  regres/refactor.py  dup=12L  groups=1  frags=2  (0.1%)

DUPLICATES[1] (ranked by impact):
  [5e5c4380c75d33c1]   STRU  _check_sys_manipulation  L=6 N=2 saved=6 sim=1.00
      regres/refactor.py:360-365  (_check_sys_manipulation)
      regres/refactor.py:376-381  (_check_dynamic_import)

REFACTOR[1] (ranked by priority):
  [1] ○ extract_function   → regres/utils/_check_sys_manipulation.py
      WHY: 2 occurrences of 6-line block across 1 files — saves 6 lines
      FILES: regres/refactor.py

QUICK_WINS[1] (low risk, high savings — do first):
  [1] extract_function   saved=6L  → regres/utils/_check_sys_manipulation.py
      FILES: refactor.py

EFFORT_ESTIMATE (total ≈ 0.2h):
  easy   _check_sys_manipulation             saved=6L  ~12min

METRICS-TARGET:
  dup_groups:  1 → 0
  saved_lines: 6 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 2033 func | 15f | 2026-05-01

NEXT[3] (ranked by impact):
  [1] !! SPLIT           regres/doctor_orchestrator.py
      WHY: 3586L, 2 classes, max CC=14
      EFFORT: ~4h  IMPACT: 50204

  [2] !! SPLIT           regres/regres.py
      WHY: 1545L, 1 classes, max CC=13
      EFFORT: ~4h  IMPACT: 20085

  [3] !! SPLIT           regres/doctor_cli.py
      WHY: 1365L, 0 classes, max CC=13
      EFFORT: ~4h  IMPACT: 17745


RISKS[3]:
  ⚠ Splitting regres/doctor_orchestrator.py may break 148 import paths
  ⚠ Splitting regres/regres.py may break 65 import paths
  ⚠ Splitting regres/doctor_cli.py may break 53 import paths

METRICS-TARGET:
  CC̄:          1.0 → ≤0.7
  max-CC:      14 → ≤7
  god-modules: 5 → 0
  high-CC(≥15): 0 → ≤0
  hub-types:   0 → ≤0

PATTERNS (language parser shared logic):
  _extract_declarations() in base.py — unified extraction for:
    - TypeScript: interfaces, types, classes, functions, arrow funcs
    - PHP: namespaces, traits, classes, functions, includes
    - Ruby: modules, classes, methods, requires
    - C++: classes, structs, functions, #includes
    - C#: classes, interfaces, methods, usings
    - Java: classes, interfaces, methods, imports
    - Go: packages, functions, structs
    - Rust: modules, functions, traits, use statements

  Shared regex patterns per language:
    - import: language-specific import/require/using patterns
    - class: class/struct/trait declarations with inheritance
    - function: function/method signatures with visibility
    - brace_tracking: for C-family languages ({ })
    - end_keyword_tracking: for Ruby (module/class/def...end)

  Benefits:
    - Consistent extraction logic across all languages
    - Reduced code duplication (~70% reduction in parser LOC)
    - Easier maintenance: fix once, apply everywhere
    - Standardized FunctionInfo/ClassInfo models

HISTORY:
  prev CC̄=1.0 → now CC̄=1.0
```

## Intent

Regression/import diagnostics helpers with TOON reports
