"""Tests for defscan module."""

from pathlib import Path

from regres.defscan import (
    Definition,
    EXT_LANG,
    IGNORED_DIRS,
    c,
    _normalize,
    sim,
    classify_similarity,
    load_gitignore,
    _path_ignored_by_gitignore,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_ext_lang_mappings():
    assert EXT_LANG[".py"] == "python"
    assert EXT_LANG[".ts"] == "typescript"
    assert EXT_LANG[".tsx"] == "typescript"


def test_ignored_dirs():
    assert "__pycache__" in IGNORED_DIRS
    assert "node_modules" in IGNORED_DIRS


# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------

def test_c_without_color():
    assert c("text", "31") == "text"


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

def test_normalize_strips_comments():
    text = "a = 1 /* block */ b = 2 // line\n"
    out = _normalize(text)
    assert "block" not in out
    assert "line" not in out
    assert "a = 1" in out
    assert "b = 2" in out


def test_normalize_collapses_whitespace():
    text = "a   =   1"
    out = _normalize(text)
    assert "  " not in out


# ---------------------------------------------------------------------------
# Definition
# ---------------------------------------------------------------------------

def test_definition_repr():
    d = Definition(
        name="Foo",
        kind="class",
        path="/x/y.py",
        line_start=10,
        line_end=20,
        body="class Foo: pass",
        lang="python",
    )
    assert "Foo" in repr(d)
    assert "class" in repr(d)


def test_definition_similarity_identical():
    d1 = Definition("A", "class", "p1", 1, 3, "class A: pass", "python")
    d2 = Definition("A", "class", "p2", 5, 7, "class A: pass", "python")
    assert sim(d1, d2) == 100.0


def test_definition_similarity_different():
    d1 = Definition("A", "class", "p1", 1, 3, "class A: pass", "python")
    d2 = Definition("B", "class", "p2", 5, 7, "class B: x=1", "python")
    assert sim(d1, d2) < 100.0


# ---------------------------------------------------------------------------
# classify_similarity
# ---------------------------------------------------------------------------

def test_classify_similarity_identical():
    label, color = classify_similarity(100)
    assert label == "IDENTYCZNE"


def test_classify_similarity_high():
    label, color = classify_similarity(85)
    assert label == "PRAWIE KOPIE"


def test_classify_similarity_medium():
    label, color = classify_similarity(65)
    assert label == "PODOBNE"


def test_classify_similarity_low():
    label, color = classify_similarity(30)
    assert label == "CZĘŚCIOWE"


# ---------------------------------------------------------------------------
# gitignore
# ---------------------------------------------------------------------------

def test_load_gitignore_missing(tmp_path: Path):
    patterns = load_gitignore(tmp_path)
    assert patterns == []


def test_load_gitignore_reads_patterns(tmp_path: Path):
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("*.pyc\nnode_modules/\n")
    patterns = load_gitignore(tmp_path)
    assert len(patterns) == 2
    assert patterns[0] == ("*.pyc", False)
    assert patterns[1] == ("node_modules/", False)


def test_path_ignored_by_gitignore(tmp_path: Path):
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("*.pyc\n")
    patterns = load_gitignore(tmp_path)
    assert _path_ignored_by_gitignore(tmp_path / "foo.pyc", tmp_path, patterns)
    assert not _path_ignored_by_gitignore(tmp_path / "foo.py", tmp_path, patterns)
