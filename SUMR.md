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
- **version**: `0.1.47`
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

## Workflows

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

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

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

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 41f 19816L | md:14,python:13,yaml:9,shell:2,txt:1,toml:1 | 2026-04-29
# CC̄=1.3 | critical:16/1410 | dups:0 | cycles:0

HEALTH[18]:
  🔴 GOD   SUMR.md = 1023L, 5 classes, 226m, max CC=0.0
  🔴 GOD   SUMD.md = 1231L, 5 classes, 488m, max CC=0.0
  🟡 CC    _render_classification_section CC=15 (limit:15)
  🟡 CC    iter_files CC=15 (limit:15)
  🟡 CC    wrapper_score CC=15 (limit:15)
  🟡 CC    cmd_hotmap CC=16 (limit:15)
  🟡 CC    _run_seed_mode CC=17 (limit:15)
  🟡 CC    analyze_dependency_chain CC=21 (limit:15)
  🟡 CC    analyze_page_registry_compliance CC=15 (limit:15)
  🟡 CC    _diagnose_page_stub CC=31 (limit:15)
  🟡 CC    _collect_page_history_candidates CC=23 (limit:15)
  🟡 CC    generate_patch_scripts CC=26 (limit:15)
  🟡 CC    _diagnose_import_issue CC=15 (limit:15)
  🟡 CC    _render_affected_files CC=22 (limit:15)
  🟡 CC    _render_dependency_chain CC=28 (limit:15)
  🟡 CC    _handle_url_mode CC=91 (limit:15)
  🟡 CC    _handle_auto_decision_flow CC=18 (limit:15)
  🟡 CC    _save_report CC=20 (limit:15)

REFACTOR[3]:
  1. split SUMR.md  (god module)
  2. split SUMD.md  (god module)
  3. split 16 high-CC methods  (CC>15)

PIPELINES[94]:
  [1] Src [_resolve_single_or_error]: _resolve_single_or_error
      PURITY: 100% pure
  [2] Src [main]: main → find_repo_root
      PURITY: 100% pure
  [3] Src [cmd_find]: cmd_find → iter_files
      PURITY: 100% pure
  [4] Src [cmd_duplicates]: cmd_duplicates → iter_files
      PURITY: 100% pure
  [5] Src [cmd_similar]: cmd_similar → iter_files
      PURITY: 100% pure

LAYERS:
  regres/                         CC̄=6.5    ←in:0  →out:135  !! split
  │ !! doctor_orchestrator       2683L  1C   75m  CC=31     ←0
  │ !! regres                    1495L  1C   55m  CC=15     ←1
  │ !! defscan                   1261L  1C   45m  CC=17     ←2
  │ !! refactor                  1237L  0C   52m  CC=16     ←2
  │ !! doctor_cli                 966L  0C    9m  CC=91     ←0
  │ import_error_toon_report   372L  2C   13m  CC=10     ←0
  │ doctor_config              263L  1C    5m  CC=14     ←1
  │ regres_cli                 209L  0C    9m  CC=7      ←0
  │ version_check              185L  0C   10m  CC=10     ←0
  │ doctor_models               36L  3C    0m  CC=0.0    ←0
  │ __init__                    20L  0C    0m  CC=0.0    ←0
  │ doctor                       6L  0C    0m  CC=0.0    ←0
  │
  docs/                           CC̄=0.0    ←in:132  →out:0
  │ !! README.md                 1117L  0C    1m  CC=0.0    ←0
  │ REGRES.md                  220L  0C    0m  CC=0.0    ←0
  │ DOCTOR.md                  198L  1C    1m  CC=0.0    ←0
  │ DEFSCAN.md                 164L  0C    1m  CC=0.0    ←7
  │ REFACTOR.md                 87L  0C    0m  CC=0.0    ←0
  │ import-error-toon-report.md    76L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! SUMD.md                   1231L  5C  488m  CC=0.0    ←3
  │ !! SUMR.md                   1023L  5C  226m  CC=0.0    ←0
  │ !! goal.yaml                  512L  0C    0m  CC=0.0    ←0
  │ CHANGELOG.md               465L  0C    0m  CC=0.0    ←0
  │ README.md                  120L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              54L  0C    0m  CC=0.0    ←0
  │ TODO.md                     47L  0C    0m  CC=0.0    ←0
  │ project.sh                  41L  0C    0m  CC=0.0    ←0
  │ tree.sh                      1L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │
  project/                        CC̄=0.0    ←in:0  →out:0
  │ !! calls.yaml                3320L  0C    0m  CC=0.0    ←0
  │ !! map.toon.yaml              512L  0C  420m  CC=0.0    ←0
  │ !! context.md                 507L  0C    0m  CC=0.0    ←0
  │ README.md                  339L  0C    0m  CC=0.0    ←0
  │ calls.toon.yaml            170L  0C    0m  CC=0.0    ←0
  │ analysis.toon.yaml         106L  0C    0m  CC=0.0    ←0
  │ evolution.toon.yaml         82L  0C    0m  CC=0.0    ←0
  │ project.toon.yaml           55L  0C    0m  CC=0.0    ←0
  │ prompt.txt                  47L  0C    0m  CC=0.0    ←0
  │ duplication.toon.yaml        9L  0C    0m  CC=0.0    ←0
  │
  .regres/                        CC̄=0.0    ←in:0  →out:0
  │ !! import-error-toon-report.md   549L  0C    0m  CC=0.0    ←0
  │
  scripts/                        CC̄=0.0    ←in:0  →out:0
  │ import-error-toon-report    11L  0C    0m  CC=0.0    ←0
  │
  testql-scenarios/               CC̄=0.0    ←in:0  →out:0
  │ generated-cli-tests.testql.toon.yaml    20L  0C    0m  CC=0.0    ←0
  │
  ── zero ──
     Makefile                                  0L

COUPLING:
          regres    docs    SUMD
  regres      ──     132       3  !! fan-out
    docs    ←132      ──          hub
    SUMD      ←3              ──
  CYCLES: none
  HUB: docs/ (fan-in=132)
  SMELL: regres/ fan-out=135 → split needed

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 0 groups | 13f 8744L | 2026-04-29

SUMMARY:
  files_scanned: 13
  total_lines:   8744
  dup_groups:    0
  dup_fragments: 0
  saved_lines:   0
  scan_ms:       2769
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 1410 func | 15f | 2026-04-29

NEXT[10] (ranked by impact):
  [1] !! SPLIT           regres/doctor_orchestrator.py
      WHY: 2683L, 1 classes, max CC=31
      EFFORT: ~4h  IMPACT: 83173

  [2] !! SPLIT           regres/regres.py
      WHY: 1495L, 1 classes, max CC=15
      EFFORT: ~4h  IMPACT: 22425

  [3] !! SPLIT           regres/defscan.py
      WHY: 1261L, 1 classes, max CC=17
      EFFORT: ~4h  IMPACT: 21437

  [4] !! SPLIT-FUNC      _handle_url_mode  CC=91  fan=71
      WHY: CC=91 exceeds 15
      EFFORT: ~1h  IMPACT: 6461

  [5] !! SPLIT-FUNC      DoctorOrchestrator._diagnose_page_stub  CC=31  fan=24
      WHY: CC=31 exceeds 15
      EFFORT: ~1h  IMPACT: 744

  [6] !  SPLIT-FUNC      DoctorOrchestrator._collect_page_history_candidates  CC=23  fan=25
      WHY: CC=23 exceeds 15
      EFFORT: ~1h  IMPACT: 575

  [7] !! SPLIT-FUNC      DoctorOrchestrator.generate_patch_scripts  CC=26  fan=17
      WHY: CC=26 exceeds 15
      EFFORT: ~1h  IMPACT: 442

  [8] !  SPLIT-FUNC      cmd_hotmap  CC=16  fan=24
      WHY: CC=16 exceeds 15
      EFFORT: ~1h  IMPACT: 384

  [9] !  SPLIT-FUNC      DoctorOrchestrator.analyze_dependency_chain  CC=21  fan=18
      WHY: CC=21 exceeds 15
      EFFORT: ~1h  IMPACT: 378

  [10] !  SPLIT-FUNC      _handle_auto_decision_flow  CC=18  fan=17
      WHY: CC=18 exceeds 15
      EFFORT: ~1h  IMPACT: 306


RISKS[3]:
  ⚠ Splitting regres/doctor_orchestrator.py may break 75 import paths
  ⚠ Splitting regres/regres.py may break 55 import paths
  ⚠ Splitting regres/defscan.py may break 45 import paths

METRICS-TARGET:
  CC̄:          1.3 → ≤0.9
  max-CC:      91 → ≤20
  god-modules: 5 → 0
  high-CC(≥15): 16 → ≤8
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
  prev CC̄=1.1 → now CC̄=1.3
```

## Intent

Regression/import diagnostics helpers with TOON reports
