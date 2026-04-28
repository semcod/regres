"""Tests for regres core module."""

from pathlib import Path

from regres.regres import (
    GitCommit,
    find_repo_root,
    _dedupe_paths,
    _check_absolute_path,
    _check_relative_paths,
    _resolve_single_or_error,
    to_rel,
    safe_read_text,
    sha256_of_file,
    content_metrics,
    extract_local_imports,
    extract_symbols,
    parse_numstat_block,
)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

def test_git_commit_fields():
    c = GitCommit(
        sha="abc123",
        short_sha="abc",
        date="2024-01-01",
        author="Test",
        subject="msg",
        file_statuses=["M", "A"],
        insertions=5,
        deletions=2,
    )
    assert c.sha == "abc123"
    assert c.insertions == 5
    assert c.deletions == 2


# ---------------------------------------------------------------------------
# find_repo_root
# ---------------------------------------------------------------------------

def test_find_repo_root_finds_git(tmp_path: Path):
    (tmp_path / ".git").mkdir()
    found = find_repo_root(tmp_path / "sub")
    assert found.resolve() == tmp_path.resolve()


def test_find_repo_root_raises_when_no_git(tmp_path: Path):
    import pytest
    with pytest.raises(RuntimeError):
        find_repo_root(tmp_path)


# ---------------------------------------------------------------------------
# Path utilities
# ---------------------------------------------------------------------------

def test_dedupe_paths():
    p = Path("/tmp")
    result = _dedupe_paths([p, p, Path("/tmp")])
    assert len(result) == 1


def test_check_absolute_path_existing(tmp_path: Path):
    f = tmp_path / "file.txt"
    f.write_text("x")
    assert _check_absolute_path(f) == f.resolve()


def test_check_absolute_path_missing():
    assert _check_absolute_path(Path("/nonexistent")) is None


def test_check_relative_paths(tmp_path: Path):
    f = tmp_path / "a.txt"
    f.write_text("x")
    result = _check_relative_paths(Path("a.txt"), (tmp_path,))
    assert len(result) == 1
    assert result[0].resolve() == f.resolve()


def test_resolve_single_or_error():
    p = Path("/tmp")
    assert _resolve_single_or_error([p], "error") == p


def test_resolve_single_or_error_raises():
    import pytest
    with pytest.raises(FileNotFoundError):
        _resolve_single_or_error([], "nothing")
    with pytest.raises(FileNotFoundError):
        _resolve_single_or_error([Path("/a"), Path("/b")], "too many")


def test_to_rel():
    assert to_rel(Path("/a/b/c"), Path("/a")) == "b/c"


# ---------------------------------------------------------------------------
# File I/O
# ---------------------------------------------------------------------------

def test_safe_read_text_utf8(tmp_path: Path):
    f = tmp_path / "test.txt"
    f.write_text("hello", encoding="utf-8")
    assert safe_read_text(f) == "hello"


def test_sha256_of_file_consistent(tmp_path: Path):
    f = tmp_path / "test.txt"
    f.write_text("hello")
    h1 = sha256_of_file(f)
    h2 = sha256_of_file(f)
    assert h1 == h2
    assert len(h1) == 64


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def test_content_metrics(tmp_path: Path):
    text = "import { os } from './utils';\n\nclass Foo:\n    pass\n\nexport { Foo }\n"
    p = tmp_path / "test.ts"
    p.write_text(text)
    m = content_metrics(text, p)
    assert m["lines"] == 6
    assert m["non_empty_lines"] == 4
    assert m["class_count"] == 1
    assert m["imports_count"] == 1
    assert m["exports_count"] == 1


# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

def test_extract_local_imports():
    text = "import { a } from './utils';\nexport * from './other';\n"
    imports = extract_local_imports(text)
    assert "./utils" in imports
    assert "./other" in imports


# ---------------------------------------------------------------------------
# Symbols
# ---------------------------------------------------------------------------

def test_extract_symbols_ts():
    text = "export function foo() {}\nexport class Bar {}\n"
    syms = extract_symbols(text)
    assert "foo" in syms
    assert "Bar" in syms


# ---------------------------------------------------------------------------
# parse_numstat_block
# ---------------------------------------------------------------------------

def test_parse_numstat_block():
    lines = ["5\t2\tfile.ts", "10\t0\tother.ts"]
    ins, dels = parse_numstat_block(lines)
    assert ins == 15
    assert dels == 2


def test_parse_numstat_block_empty():
    assert parse_numstat_block([]) == (0, 0)
