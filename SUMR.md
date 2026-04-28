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
- **version**: `0.1.6`
- **python_requires**: `>=3.11`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Makefile, testql(1), app.doql.less, goal.yaml, src(8 mod), project/(5 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: regres;
  version: 0.1.6;
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
- `regres.doctor_models`
- `regres.doctor_orchestrator`
- `regres.import_error_toon_report`
- `regres.refactor`
- `regres.regres`
- `regres.regres_cli`

## Workflows

## Source Map

*Top 5 modules by symbol density — signatures for LLM orientation.*

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
def _determine_primary_type(import_problems, broken, target_dir, current_lines, evolution)  # CC=19, fan=9 ⚠
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

### `regres.doctor_orchestrator` (`regres/doctor_orchestrator.py`)

```python
class DoctorOrchestrator:  # Orchestrator analizy i generator akcji.
    def __init__(scan_root)  # CC=1
    def analyze_from_url(url)  # CC=6
    def analyze_import_errors(log_path)  # CC=5
    def analyze_duplicates(report_path)  # CC=5
    def analyze_git_history(file_path)  # CC=7
    def analyze_with_defscan(path)  # CC=6
    def analyze_with_refactor(path)  # CC=7
    def apply_fixes(diagnoses, dry_run)  # CC=4
    def generate_llm_diagnosis(url, module_path)  # CC=1
    def generate_report()  # CC=4
    def render_markdown(report)  # CC=9
    def _extract_module_name(path)  # CC=4
    def _resolve_module_path(module_name)  # CC=4
    def _import_exists_in_source(file_path, module_name)  # CC=11 ⚠
    def _resolve_alias_target(alias_path)  # CC=6
    def _parse_ts_errors(log_path)  # CC=6
    def _validate_errors(file_path, errors)  # CC=4
    def _extract_missing_modules(errors)  # CC=3
    def _diagnose_import_issue(file_path, missing_modules)  # CC=15 ⚠
    def _diagnose_duplicate(duplicate_data)  # CC=4
    def _find_main_location(locations)  # CC=4
    def _analyze_history_patterns(file_path, history_lines)  # CC=7
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
    def _render_step_by_step_playbook(diagnoses, llm_mode)  # CC=8
    def _render_analyze_step(shell_commands, paths)  # CC=8
    def _render_apply_step(llm_mode, paths)  # CC=4
    def _render_validate_step(paths)  # CC=3
    def _collect_git_context(module_path)  # CC=3
    def _collect_structure_context(module_path)  # CC=4
    def _collect_defscan_context(module_path)  # CC=7
    def _collect_refactor_context(module_path)  # CC=3
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
def cmd_deps(args, root)  # CC=18, fan=12 ⚠
def to_json_toon(data)  # CC=23, fan=10 ⚠
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
def extract_python(path)  # CC=14, fan=18 ⚠
def _extract_block_ts(text, start_pos)  # CC=18, fan=2 ⚠
def _lineno_at(text, pos)  # CC=1, fan=1
def extract_typescript(path)  # CC=11, fan=13 ⚠
def extract_go(path)  # CC=6, fan=12
def extract_rust(path)  # CC=4, fan=11
def extract_file(path)  # CC=6, fan=6
def load_gitignore(root)  # CC=7, fan=6
def _path_ignored_by_gitignore(path, root, patterns)  # CC=19, fan=11 ⚠
def scan(root, name_filter, kind_filter, only_within, gitignore_patterns, gitignore_root, ext_filter)  # CC=23, fan=15 ⚠
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
def _run_focus_mode(args, root, root_str, gitignore_patterns, ext_set)  # CC=20, fan=17 ⚠
def _run_default_mode(args, root, root_str, gitignore_patterns, ext_set)  # CC=17, fan=13 ⚠
def main()  # CC=8, fan=13
class Definition:  # Pojedyncza definicja (klasa / funkcja / enum / interface / m
    def __init__(name, kind, path, line_start, line_end, body, lang, bases, decorators)  # CC=3
    def loc()  # CC=3
    def __repr__()  # CC=1
```

### `regres.doctor` (`regres/doctor.py`)

```python
def _handle_url_mode(args, doctor, scan_root)  # CC=12, fan=14 ⚠
def _handle_import_errors(args, doctor, scan_root, refresh_fn)  # CC=10, fan=5 ⚠
def _handle_defscan_refactor(args, doctor)  # CC=4, fan=5
def _save_report(doctor, args)  # CC=5, fan=6
def _refresh_import_error_log(project_root, log_path)  # CC=5, fan=5
def main()  # CC=4, fan=10
class FileAction:  # Akcja na pliku.
class ShellCommand:  # Polecenie shell do wykonania.
class Diagnosis:  # Diagnoza problemu i plan naprawy.
class DoctorOrchestrator:  # Orchestrator analizy i generator akcji.
    def __init__(scan_root)  # CC=1
    def analyze_from_url(url)  # CC=13 ⚠
    def analyze_import_errors(log_path)  # CC=8
    def _import_exists_in_source(file_path, module_name)  # CC=11 ⚠
    def _resolve_alias_target(alias_path)  # CC=6
    def _parse_ts_errors(log_path)  # CC=6
    def _extract_missing_modules(errors)  # CC=3
    def _diagnose_import_issue(file_path, missing_modules)  # CC=15 ⚠
    def analyze_duplicates(report_path)  # CC=5
    def _diagnose_duplicate(duplicate_data)  # CC=4
    def _find_main_location(locations)  # CC=4
    def analyze_git_history(file_path)  # CC=7
    def _analyze_history_patterns(file_path, history_lines)  # CC=7
    def analyze_with_defscan(path)  # CC=6
    def analyze_with_refactor(path)  # CC=7
    def apply_fixes(diagnoses, dry_run)  # CC=18 ⚠
    def generate_llm_diagnosis(url, module_path)  # CC=16 ⚠
    def _render_step_by_step_playbook(diagnoses, llm_mode)  # CC=20 ⚠
    def _collect_git_context(module_path)  # CC=3
    def _collect_structure_context(module_path)  # CC=4
    def _collect_defscan_context(module_path)  # CC=7
    def _collect_refactor_context(module_path)  # CC=3
    def generate_report()  # CC=4
    def render_markdown(report)  # CC=9
```

## Call Graph

*126 nodes · 175 edges · 6 modules · CC̄=1.6*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `print` *(in docs.DEFSCAN)* | 0 | 123 | 0 | **123** |
| `to_json_toon` *(in regres.refactor)* | 23 ⚠ | 1 | 60 | **61** |
| `render_text` *(in regres.defscan)* | 14 ⚠ | 2 | 55 | **57** |
| `build_parser` *(in regres.refactor)* | 1 | 1 | 49 | **50** |
| `render_seed_text` *(in regres.defscan)* | 10 ⚠ | 1 | 42 | **43** |
| `cmd_hotmap` *(in regres.refactor)* | 16 ⚠ | 0 | 42 | **42** |
| `extract_python` *(in regres.defscan)* | 14 ⚠ | 1 | 37 | **38** |
| `extract_go` *(in regres.defscan)* | 6 | 1 | 32 | **33** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/regres
# nodes: 126 | edges: 175 | modules: 6
# CC̄=1.6

HUBS[20]:
  docs.DEFSCAN.print
    CC=0  in:123  out:0  total:123
  regres.refactor.to_json_toon
    CC=23  in:1  out:60  total:61
  regres.defscan.render_text
    CC=14  in:2  out:55  total:57
  regres.refactor.build_parser
    CC=1  in:1  out:49  total:50
  regres.defscan.render_seed_text
    CC=10  in:1  out:42  total:43
  regres.refactor.cmd_hotmap
    CC=16  in:0  out:42  total:42
  regres.defscan.extract_python
    CC=14  in:1  out:37  total:38
  regres.defscan.extract_go
    CC=6  in:1  out:32  total:33
  regres.defscan._run_focus_mode
    CC=20  in:1  out:32  total:33
  regres.defscan._run_seed_mode
    CC=17  in:1  out:32  total:33
  regres.regres._render_classification_section
    CC=15  in:1  out:31  total:32
  regres.import_error_toon_report.to_toon_global_payload
    CC=10  in:1  out:31  total:32
  regres.refactor.cmd_diff
    CC=7  in:0  out:31  total:31
  regres.defscan.c
    CC=2  in:30  out:0  total:30
  regres.regres.trace_name_and_hash_candidates
    CC=13  in:1  out:28  total:29
  regres.refactor.cmd_dead
    CC=14  in:0  out:28  total:28
  regres.regres._render_regression_section
    CC=12  in:1  out:26  total:27
  regres.refactor.cmd_deps
    CC=18  in:0  out:27  total:27
  regres.defscan.scan
    CC=23  in:5  out:22  total:27
  regres.refactor.cmd_similar
    CC=14  in:0  out:26  total:26

MODULES:
  docs.DEFSCAN  [1 funcs]
    print  CC=0  out:0
  regres.defscan  [28 funcs]
    __init__  CC=3  out:2
    _build_argument_parser  CC=1  out:18
    _def_key  CC=1  out:0
    _extract_block_ts  CC=18  out:6
    _lineno_at  CC=1  out:1
    _normalize  CC=1  out:8
    _run_default_mode  CC=17  out:25
    _run_focus_mode  CC=20  out:32
    _run_seed_mode  CC=17  out:32
    _short_path  CC=2  out:3
  regres.doctor  [3 funcs]
    _handle_url_mode  CC=12  out:19
    _refresh_import_error_log  CC=5  out:9
    _save_report  CC=5  out:11
  regres.import_error_toon_report  [10 funcs]
    grouped_errors  CC=2  out:3
    main  CC=5  out:18
    metrics  CC=3  out:5
    normalize_file_rel  CC=3  out:8
    parse_args  CC=1  out:11
    parse_ts_errors  CC=7  out:17
    render_markdown  CC=6  out:23
    to_toon_compact_per_file  CC=7  out:15
    to_toon_global_payload  CC=10  out:31
    toon_quote  CC=1  out:3
  regres.refactor  [38 funcs]
    _build_symbol_index  CC=5  out:6
    _collect_file_infos  CC=6  out:14
    _find_duplicate_symbols  CC=5  out:9
    _find_external_importers  CC=7  out:8
    _find_md5_duplicates  CC=4  out:8
    _find_name_clusters  CC=4  out:10
    _find_similar_pairs  CC=7  out:15
    _render_cross_lang_symbols  CC=6  out:8
    _render_duplicate_symbols  CC=6  out:9
    _render_file_symbols  CC=10  out:12
  regres.regres  [46 funcs]
    _check_absolute_path  CC=4  out:4
    _check_relative_paths  CC=4  out:5
    _classify_import_problem  CC=4  out:4
    _dedupe_paths  CC=3  out:6
    _determine_primary_type  CC=19  out:14
    _render_classification_section  CC=15  out:31
    _render_duplicates_section  CC=5  out:12
    _render_evolution_section  CC=6  out:10
    _render_last_good_section  CC=3  out:3
    _render_lineage_section  CC=2  out:3

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
  regres.regres.render_markdown → regres.regres._render_last_good_section
  regres.regres.render_markdown → regres.regres._render_regression_section
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
# nodes: 126 | edges: 175 | modules: 6
# CC̄=1.6

HUBS[20]:
  docs.DEFSCAN.print
    CC=0  in:123  out:0  total:123
  regres.refactor.to_json_toon
    CC=23  in:1  out:60  total:61
  regres.defscan.render_text
    CC=14  in:2  out:55  total:57
  regres.refactor.build_parser
    CC=1  in:1  out:49  total:50
  regres.defscan.render_seed_text
    CC=10  in:1  out:42  total:43
  regres.refactor.cmd_hotmap
    CC=16  in:0  out:42  total:42
  regres.defscan.extract_python
    CC=14  in:1  out:37  total:38
  regres.defscan.extract_go
    CC=6  in:1  out:32  total:33
  regres.defscan._run_focus_mode
    CC=20  in:1  out:32  total:33
  regres.defscan._run_seed_mode
    CC=17  in:1  out:32  total:33
  regres.regres._render_classification_section
    CC=15  in:1  out:31  total:32
  regres.import_error_toon_report.to_toon_global_payload
    CC=10  in:1  out:31  total:32
  regres.refactor.cmd_diff
    CC=7  in:0  out:31  total:31
  regres.defscan.c
    CC=2  in:30  out:0  total:30
  regres.regres.trace_name_and_hash_candidates
    CC=13  in:1  out:28  total:29
  regres.refactor.cmd_dead
    CC=14  in:0  out:28  total:28
  regres.regres._render_regression_section
    CC=12  in:1  out:26  total:27
  regres.refactor.cmd_deps
    CC=18  in:0  out:27  total:27
  regres.defscan.scan
    CC=23  in:5  out:22  total:27
  regres.refactor.cmd_similar
    CC=14  in:0  out:26  total:26

MODULES:
  docs.DEFSCAN  [1 funcs]
    print  CC=0  out:0
  regres.defscan  [28 funcs]
    __init__  CC=3  out:2
    _build_argument_parser  CC=1  out:18
    _def_key  CC=1  out:0
    _extract_block_ts  CC=18  out:6
    _lineno_at  CC=1  out:1
    _normalize  CC=1  out:8
    _run_default_mode  CC=17  out:25
    _run_focus_mode  CC=20  out:32
    _run_seed_mode  CC=17  out:32
    _short_path  CC=2  out:3
  regres.doctor  [3 funcs]
    _handle_url_mode  CC=12  out:19
    _refresh_import_error_log  CC=5  out:9
    _save_report  CC=5  out:11
  regres.import_error_toon_report  [10 funcs]
    grouped_errors  CC=2  out:3
    main  CC=5  out:18
    metrics  CC=3  out:5
    normalize_file_rel  CC=3  out:8
    parse_args  CC=1  out:11
    parse_ts_errors  CC=7  out:17
    render_markdown  CC=6  out:23
    to_toon_compact_per_file  CC=7  out:15
    to_toon_global_payload  CC=10  out:31
    toon_quote  CC=1  out:3
  regres.refactor  [38 funcs]
    _build_symbol_index  CC=5  out:6
    _collect_file_infos  CC=6  out:14
    _find_duplicate_symbols  CC=5  out:9
    _find_external_importers  CC=7  out:8
    _find_md5_duplicates  CC=4  out:8
    _find_name_clusters  CC=4  out:10
    _find_similar_pairs  CC=7  out:15
    _render_cross_lang_symbols  CC=6  out:8
    _render_duplicate_symbols  CC=6  out:9
    _render_file_symbols  CC=10  out:12
  regres.regres  [46 funcs]
    _check_absolute_path  CC=4  out:4
    _check_relative_paths  CC=4  out:5
    _classify_import_problem  CC=4  out:4
    _dedupe_paths  CC=3  out:6
    _determine_primary_type  CC=19  out:14
    _render_classification_section  CC=15  out:31
    _render_duplicates_section  CC=5  out:12
    _render_evolution_section  CC=6  out:10
    _render_last_good_section  CC=3  out:3
    _render_lineage_section  CC=2  out:3

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
  regres.regres.render_markdown → regres.regres._render_last_good_section
  regres.regres.render_markdown → regres.regres._render_regression_section
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 37f 15073L | md:13,python:10,yaml:9,shell:2,toml:1,txt:1 | 2026-04-28
# CC̄=1.6 | critical:19/850 | dups:0 | cycles:0

HEALTH[20]:
  🔴 GOD   regres/doctor.py = 1209L, 4 classes, 30m, max CC=20
  🔴 GOD   SUMR.md = 919L, 8 classes, 160m, max CC=0.0
  🔴 GOD   SUMD.md = 933L, 8 classes, 251m, max CC=0.0
  🟡 CC    _determine_primary_type CC=19 (limit:15)
  🟡 CC    _render_classification_section CC=15 (limit:15)
  🟡 CC    _diagnose_import_issue CC=15 (limit:15)
  🟡 CC    apply_fixes CC=18 (limit:15)
  🟡 CC    generate_llm_diagnosis CC=16 (limit:15)
  🟡 CC    _render_step_by_step_playbook CC=20 (limit:15)
  🟡 CC    iter_files CC=15 (limit:15)
  🟡 CC    wrapper_score CC=15 (limit:15)
  🟡 CC    cmd_hotmap CC=16 (limit:15)
  🟡 CC    cmd_deps CC=18 (limit:15)
  🟡 CC    to_json_toon CC=23 (limit:15)
  🟡 CC    main CC=42 (limit:15)
  🟡 CC    _extract_block_ts CC=18 (limit:15)
  🟡 CC    _path_ignored_by_gitignore CC=19 (limit:15)
  🟡 CC    scan CC=23 (limit:15)
  🟡 CC    _run_seed_mode CC=17 (limit:15)
  🟡 CC    _run_focus_mode CC=20 (limit:15)

REFACTOR[4]:
  1. split regres/doctor.py  (god module)
  2. split SUMR.md  (god module)
  3. split SUMD.md  (god module)
  4. split 17 high-CC methods  (CC>15)

PIPELINES[82]:
  [1] Src [_resolve_single_or_error]: _resolve_single_or_error
      PURITY: 100% pure
  [2] Src [main]: main → find_repo_root
      PURITY: 100% pure
  [3] Src [__init__]: __init__
      PURITY: 100% pure
  [4] Src [analyze_from_url]: analyze_from_url
      PURITY: 100% pure
  [5] Src [analyze_import_errors]: analyze_import_errors
      PURITY: 100% pure

LAYERS:
  regres/                         CC̄=6.7    ←in:0  →out:123  !! split
  │ !! regres                    1483L  1C   53m  CC=19     ←1
  │ !! doctor                    1209L  4C   30m  CC=20     ←1
  │ !! refactor                  1198L  0C   41m  CC=23     ←3
  │ !! defscan                   1189L  1C   31m  CC=23     ←3
  │ !! doctor_orchestrator        874L  1C   41m  CC=15     ←0
  │ import_error_toon_report   365L  2C   13m  CC=10     ←0
  │ !! regres_cli                 197L  0C    1m  CC=42     ←0
  │ doctor_models               36L  3C    0m  CC=0.0    ←0
  │ __init__                    13L  0C    0m  CC=0.0    ←0
  │
  docs/                           CC̄=0.0    ←in:123  →out:0
  │ !! README.md                  796L  0C    1m  CC=0.0    ←0
  │ REGRES.md                  220L  0C    0m  CC=0.0    ←0
  │ DEFSCAN.md                 164L  0C    1m  CC=0.0    ←5
  │ DOCTOR.md                  150L  1C    1m  CC=0.0    ←0
  │ REFACTOR.md                 87L  0C    0m  CC=0.0    ←0
  │ import-error-toon-report.md    76L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! SUMD.md                    933L  8C  251m  CC=0.0    ←0
  │ !! SUMR.md                    919L  8C  160m  CC=0.0    ←0
  │ !! goal.yaml                  512L  0C    0m  CC=0.0    ←0
  │ CHANGELOG.md                98L  0C    0m  CC=0.0    ←0
  │ README.md                   66L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              52L  0C    0m  CC=0.0    ←0
  │ project.sh                  41L  0C    0m  CC=0.0    ←0
  │ tree.sh                      1L  0C    0m  CC=0.0    ←0
  │ Makefile                     0L  0C    0m  CC=0.0    ←0
  │
  project/                        CC̄=0.0    ←in:0  →out:0
  │ !! calls.yaml                2233L  0C    0m  CC=0.0    ←0
  │ context.md                 495L  0C    0m  CC=0.0    ←0
  │ README.md                  339L  0C    0m  CC=0.0    ←0
  │ map.toon.yaml              299L  0C  226m  CC=0.0    ←0
  │ calls.toon.yaml            149L  0C    0m  CC=0.0    ←0
  │ analysis.toon.yaml         108L  0C    0m  CC=0.0    ←0
  │ evolution.toon.yaml         82L  0C    0m  CC=0.0    ←0
  │ project.toon.yaml           53L  0C    0m  CC=0.0    ←0
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
            docs  regres
    docs      ──    ←123  hub
  regres     123      ──  !! fan-out
  CYCLES: none
  HUB: docs/ (fan-in=123)
  SMELL: regres/ fan-out=123 → split needed

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 11 groups | 10f 6575L | 2026-04-28

SUMMARY:
  files_scanned: 10
  total_lines:   6575
  dup_groups:    11
  dup_fragments: 22
  saved_lines:   239
  scan_ms:       4384

HOTSPOTS[2] (files with most duplication):
  regres/doctor.py  dup=239L  groups=11  frags=11  (3.6%)
  regres/doctor_orchestrator.py  dup=216L  groups=11  frags=11  (3.3%)

DUPLICATES[11] (ranked by impact):
  [dea9ff092f524f29] ! EXAC  _diagnose_duplicate  L=40 N=2 saved=40 sim=1.00
      regres/doctor.py:350-389  (_diagnose_duplicate)
      regres/doctor_orchestrator.py:483-520  (_diagnose_duplicate)
  [73c41f53e79443fe] ! EXAC  _analyze_history_patterns  L=33 N=2 saved=33 sim=1.00
      regres/doctor.py:430-462  (_analyze_history_patterns)
      regres/doctor_orchestrator.py:528-555  (_analyze_history_patterns)
  [0a737c5207711771] ! EXAC  generate_report  L=32 N=2 saved=32 sim=1.00
      regres/doctor.py:958-989  (generate_report)
      regres/doctor_orchestrator.py:239-270  (generate_report)
  [caccfe65b3c5513b]   EXAC  analyze_git_history  L=28 N=2 saved=28 sim=1.00
      regres/doctor.py:401-428  (analyze_git_history)
      regres/doctor_orchestrator.py:114-139  (analyze_git_history)
  [c77c283d21c7b780]   EXAC  analyze_with_defscan  L=24 N=2 saved=24 sim=1.00
      regres/doctor.py:464-487  (analyze_with_defscan)
      regres/doctor_orchestrator.py:141-163  (analyze_with_defscan)
  [8e6d28d8bf269acf]   EXAC  _resolve_alias_target  L=21 N=2 saved=21 sim=1.00
      regres/doctor.py:196-216  (_resolve_alias_target)
      regres/doctor_orchestrator.py:352-369  (_resolve_alias_target)
  [16eaf6b4fdef6076]   EXAC  analyze_duplicates  L=21 N=2 saved=21 sim=1.00
      regres/doctor.py:328-348  (analyze_duplicates)
      regres/doctor_orchestrator.py:95-112  (analyze_duplicates)
  [1ba77f9697512800]   EXAC  _import_exists_in_source  L=17 N=2 saved=17 sim=1.00
      regres/doctor.py:178-194  (_import_exists_in_source)
      regres/doctor_orchestrator.py:334-350  (_import_exists_in_source)
  [15ce3d3b8eecb028]   EXAC  _extract_missing_modules  L=11 N=2 saved=11 sim=1.00
      regres/doctor.py:241-251  (_extract_missing_modules)
      regres/doctor_orchestrator.py:404-411  (_extract_missing_modules)
  [13bcf7c7b7dcfb25]   EXAC  _find_main_location  L=9 N=2 saved=9 sim=1.00
      regres/doctor.py:391-399  (_find_main_location)
      regres/doctor_orchestrator.py:522-526  (_find_main_location)
  [d70944bf2f7f7e38]   EXAC  __init__  L=3 N=2 saved=3 sim=1.00
      regres/doctor.py:60-62  (__init__)
      regres/doctor_orchestrator.py:19-21  (__init__)

REFACTOR[11] (ranked by priority):
  [1] ◐ extract_class      → regres/utils/_diagnose_duplicate.py
      WHY: 2 occurrences of 40-line block across 2 files — saves 40 lines
      FILES: regres/doctor.py, regres/doctor_orchestrator.py
  [2] ◐ extract_class      → regres/utils/_analyze_history_patterns.py
      WHY: 2 occurrences of 33-line block across 2 files — saves 33 lines
      FILES: regres/doctor.py, regres/doctor_orchestrator.py
  [3] ◐ extract_class      → regres/utils/generate_report.py
      WHY: 2 occurrences of 32-line block across 2 files — saves 32 lines
      FILES: regres/doctor.py, regres/doctor_orchestrator.py
  [4] ○ extract_class      → regres/utils/analyze_git_history.py
      WHY: 2 occurrences of 28-line block across 2 files — saves 28 lines
      FILES: regres/doctor.py, regres/doctor_orchestrator.py
  [5] ○ extract_class      → regres/utils/analyze_with_defscan.py
      WHY: 2 occurrences of 24-line block across 2 files — saves 24 lines
      FILES: regres/doctor.py, regres/doctor_orchestrator.py
  [6] ○ extract_class      → regres/utils/_resolve_alias_target.py
      WHY: 2 occurrences of 21-line block across 2 files — saves 21 lines
      FILES: regres/doctor.py, regres/doctor_orchestrator.py
  [7] ○ extract_class      → regres/utils/analyze_duplicates.py
      WHY: 2 occurrences of 21-line block across 2 files — saves 21 lines
      FILES: regres/doctor.py, regres/doctor_orchestrator.py
  [8] ○ extract_class      → regres/utils/_import_exists_in_source.py
      WHY: 2 occurrences of 17-line block across 2 files — saves 17 lines
      FILES: regres/doctor.py, regres/doctor_orchestrator.py
  [9] ○ extract_class      → regres/utils/_extract_missing_modules.py
      WHY: 2 occurrences of 11-line block across 2 files — saves 11 lines
      FILES: regres/doctor.py, regres/doctor_orchestrator.py
  [10] ○ extract_class      → regres/utils/_find_main_location.py
      WHY: 2 occurrences of 9-line block across 2 files — saves 9 lines
      FILES: regres/doctor.py, regres/doctor_orchestrator.py
  [11] ○ extract_class      → regres/utils/__init__.py
      WHY: 2 occurrences of 3-line block across 2 files — saves 3 lines
      FILES: regres/doctor.py, regres/doctor_orchestrator.py

QUICK_WINS[7] (low risk, high savings — do first):
  [4] extract_class      saved=28L  → regres/utils/analyze_git_history.py
      FILES: doctor.py, doctor_orchestrator.py
  [5] extract_class      saved=24L  → regres/utils/analyze_with_defscan.py
      FILES: doctor.py, doctor_orchestrator.py
  [6] extract_class      saved=21L  → regres/utils/_resolve_alias_target.py
      FILES: doctor.py, doctor_orchestrator.py
  [7] extract_class      saved=21L  → regres/utils/analyze_duplicates.py
      FILES: doctor.py, doctor_orchestrator.py
  [8] extract_class      saved=17L  → regres/utils/_import_exists_in_source.py
      FILES: doctor.py, doctor_orchestrator.py
  [9] extract_class      saved=11L  → regres/utils/_extract_missing_modules.py
      FILES: doctor.py, doctor_orchestrator.py
  [10] extract_class      saved=9L  → regres/utils/_find_main_location.py
      FILES: doctor.py, doctor_orchestrator.py

EFFORT_ESTIMATE (total ≈ 9.7h):
  hard   _diagnose_duplicate                 saved=40L  ~120min
  hard   _analyze_history_patterns           saved=33L  ~99min
  hard   generate_report                     saved=32L  ~96min
  medium analyze_git_history                 saved=28L  ~56min
  medium analyze_with_defscan                saved=24L  ~48min
  medium _resolve_alias_target               saved=21L  ~42min
  medium analyze_duplicates                  saved=21L  ~42min
  medium _import_exists_in_source            saved=17L  ~34min
  easy   _extract_missing_modules            saved=11L  ~22min
  easy   _find_main_location                 saved=9L  ~18min
  ... +1 more (~6min)

METRICS-TARGET:
  dup_groups:  11 → 0
  saved_lines: 239 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 850 func | 13f | 2026-04-28

NEXT[10] (ranked by impact):
  [1] !! SPLIT           regres/regres.py
      WHY: 1483L, 1 classes, max CC=19
      EFFORT: ~4h  IMPACT: 28177

  [2] !! SPLIT           regres/refactor.py
      WHY: 1198L, 0 classes, max CC=23
      EFFORT: ~4h  IMPACT: 27554

  [3] !! SPLIT           regres/doctor.py
      WHY: 1209L, 4 classes, max CC=20
      EFFORT: ~4h  IMPACT: 24180

  [4] !! SPLIT-FUNC      main  CC=42  fan=18
      WHY: CC=42 exceeds 15
      EFFORT: ~1h  IMPACT: 756

  [5] !  SPLIT-FUNC      scan  CC=23  fan=21
      WHY: CC=23 exceeds 15
      EFFORT: ~1h  IMPACT: 483

  [6] !  SPLIT-FUNC      cmd_hotmap  CC=16  fan=24
      WHY: CC=16 exceeds 15
      EFFORT: ~1h  IMPACT: 384

  [7] !  SPLIT-FUNC      _run_focus_mode  CC=20  fan=18
      WHY: CC=20 exceeds 15
      EFFORT: ~1h  IMPACT: 360

  [8] !  SPLIT-FUNC      to_json_toon  CC=23  fan=15
      WHY: CC=23 exceeds 15
      EFFORT: ~1h  IMPACT: 345

  [9] !  SPLIT-FUNC      DoctorOrchestrator.generate_llm_diagnosis  CC=16  fan=19
      WHY: CC=16 exceeds 15
      EFFORT: ~1h  IMPACT: 304

  [10] !  SPLIT-FUNC      cmd_deps  CC=18  fan=15
      WHY: CC=18 exceeds 15
      EFFORT: ~1h  IMPACT: 270


RISKS[3]:
  ⚠ Splitting regres/regres.py may break 53 import paths
  ⚠ Splitting regres/doctor.py may break 30 import paths
  ⚠ Splitting regres/refactor.py may break 41 import paths

METRICS-TARGET:
  CC̄:          1.6 → ≤1.1
  max-CC:      42 → ≤20
  god-modules: 5 → 0
  high-CC(≥15): 19 → ≤9
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
  prev CC̄=1.5 → now CC̄=1.6
```

## Intent

Regression/import diagnostics helpers with TOON reports
