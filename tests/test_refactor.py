"""Tests for refactor module."""

from pathlib import Path

from regres.refactor import (
    DEFAULT_EXTENSIONS,
    IGNORED_DIRS,
    count_word,
    line_count,
    similarity_ratio,
    normalize_code,
    rel,
    name_prefix,
    extract_imports,
    md5_file,
    read_text,
    extract_symbols_regex,
    wrapper_score,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_default_extensions_contains_py():
    assert ".py" in DEFAULT_EXTENSIONS
    assert ".ts" in DEFAULT_EXTENSIONS


def test_ignored_dirs_contains_node_modules():
    assert "node_modules" in IGNORED_DIRS
    assert ".git" in IGNORED_DIRS


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def test_count_word_case_insensitive():
    assert count_word("Hello hello HELLO", "hello") == 3


def test_count_word_case_sensitive():
    assert count_word("Hello hello HELLO", "hello", case_sensitive=True) == 1


def test_line_count():
    assert line_count("a\nb\nc") == 3
    assert line_count("") == 0
    assert line_count("single") == 1


def test_similarity_ratio_identical():
    assert similarity_ratio("abc", "abc") == 100.0


def test_similarity_ratio_empty():
    assert similarity_ratio("", "abc") == 0.0
    assert similarity_ratio("abc", "") == 0.0


def test_similarity_ratio_different():
    result = similarity_ratio("abc", "axc")
    assert 0.0 < result < 100.0


def test_normalize_code_strips_comments():
    code = "a = 1  // comment\nb = 2 /* block */"
    out = normalize_code(code, ".ts")
    assert "comment" not in out
    assert "block" not in out
    assert "a = 1" in out


def test_rel_path():
    assert rel(Path("/a/b/c"), Path("/a")) == "b/c"


def test_name_prefix():
    assert name_prefix("encoder-core.service.ts", depth=2) == "encoder-core"
    assert name_prefix("foo-bar-baz.py", depth=2) == "foo-bar"


def test_extract_imports_python():
    code = "from os import path\nimport sys\n"
    imports = extract_imports(code)
    assert "os" in imports
    assert "sys" in imports


def test_extract_imports_ts():
    code = "import { x } from './utils';\n"
    imports = extract_imports(code)
    assert "./utils" in imports


# ---------------------------------------------------------------------------
# Symbol extraction
# ---------------------------------------------------------------------------

def test_extract_symbols_regex_python():
    code = "def foo(): pass\nclass Bar:\n    pass\n"
    syms = extract_symbols_regex(code, ".py")
    names = {s["name"] for s in syms}
    assert "foo" in names
    assert "Bar" in names


def test_extract_symbols_regex_ts():
    code = "export function foo() {}\ninterface Bar {}\n"
    syms = extract_symbols_regex(code, ".ts")
    names = {s["name"] for s in syms}
    assert "foo" in names
    assert "Bar" in names


# ---------------------------------------------------------------------------
# Wrapper score
# ---------------------------------------------------------------------------

def test_wrapper_score_empty():
    score = wrapper_score("")
    assert isinstance(score, dict)
    assert "score" in score


def test_wrapper_score_high_for_reexport():
    code = "export * from './other';\n"
    score = wrapper_score(code)
    assert score["score"] > 0


# ---------------------------------------------------------------------------
# md5 / read_text
# ---------------------------------------------------------------------------

def test_md5_file_consistent(tmp_path: Path):
    p = tmp_path / "test.txt"
    p.write_text("hello")
    h1 = md5_file(p)
    h2 = md5_file(p)
    assert h1 == h2
    assert len(h1) == 32


def test_read_text_reads_utf8(tmp_path: Path):
    p = tmp_path / "test.txt"
    p.write_text("zażółć", encoding="utf-8")
    assert read_text(p) == "zażółć"
