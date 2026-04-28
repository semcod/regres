"""Tests for import_error_toon_report module."""

from pathlib import Path

from regres.import_error_toon_report import (
    TsError,
    ReportData,
    toon_quote,
    parse_ts_errors,
    suggestions_for_error,
    grouped_errors,
    metrics,
    to_toon_block_legacy,
    to_toon_global_payload,
    to_toon_compact_per_file,
    TS_ERROR_RE,
    MISSING_MODULE_RE,
    EXPORTED_MEMBER_RE,
)


# ---------------------------------------------------------------------------
# Regex constants
# ---------------------------------------------------------------------------

def test_ts_error_re_matches():
    line = "src/app.ts(42,5): error TS2307: Cannot find module './foo'."
    m = TS_ERROR_RE.match(line)
    assert m is not None
    assert m.group("file") == "src/app.ts"
    assert m.group("line") == "42"
    assert m.group("col") == "5"
    assert m.group("code") == "TS2307"
    assert "Cannot find module" in m.group("msg")


def test_ts_error_re_no_match_for_plain_text():
    assert TS_ERROR_RE.match("random text without ts error") is None


def test_missing_module_re():
    msg = "Cannot find module '@c2004/core'"
    m = MISSING_MODULE_RE.search(msg)
    assert m is not None
    assert m.group(1) == "@c2004/core"


def test_exported_member_re():
    msg = "Module './utils' has no exported member 'foo'."
    m = EXPORTED_MEMBER_RE.search(msg)
    assert m is not None
    assert m.group(1) == "foo"


# ---------------------------------------------------------------------------
# toon_quote
# ---------------------------------------------------------------------------

def test_toon_quote_escapes():
    assert toon_quote('a"b') == '"a\\"b"'
    assert toon_quote("a\\b") == '"a\\\\b"'
    assert toon_quote("a\nb") == '"a\\nb"'


# ---------------------------------------------------------------------------
# parse_ts_errors
# ---------------------------------------------------------------------------

def test_parse_ts_errors_basic():
    log = (
        "src/a.ts(1,2): error TS2307: Cannot find module './missing'.\n"
        "src/b.ts(3,4): error TS2305: Module './utils' has no exported member 'x'.\n"
    )
    errs = parse_ts_errors(log, Path("/tmp"), {"TS2307", "TS2305"})
    assert len(errs) == 2
    assert errs[0].code == "TS2307"
    assert errs[0].module_path == "./missing"
    assert errs[1].code == "TS2305"
    assert errs[1].member_name == "x"


def test_parse_ts_errors_filters_code():
    log = "src/a.ts(1,2): error TS9999: Some other error.\n"
    errs = parse_ts_errors(log, Path("/tmp"), {"TS2307"})
    assert len(errs) == 0


def test_parse_ts_errors_empty():
    assert parse_ts_errors("", Path("/tmp"), set()) == []


# ---------------------------------------------------------------------------
# suggestions_for_error
# ---------------------------------------------------------------------------

def test_suggestions_ts2307_alias():
    err = TsError("f", 1, 1, "TS2307", "msg", "@c2004/core", None)
    s = suggestions_for_error(err)
    assert any("alias" in x for x in s)


def test_suggestions_ts2307_relative():
    err = TsError("f", 1, 1, "TS2307", "msg", "../../../../utils", None)
    s = suggestions_for_error(err)
    assert any("relatywną ścieżkę" in x for x in s)
    assert any("alias" in x for x in s)


def test_suggestions_ts2305():
    err = TsError("f", 1, 1, "TS2305", "msg", None, "foo")
    s = suggestions_for_error(err)
    assert any("eksporty" in x for x in s)
    assert any("foo" in x for x in s)


def test_suggestions_unknown_code():
    err = TsError("f", 1, 1, "TS9999", "msg", None, None)
    assert suggestions_for_error(err) == []


# ---------------------------------------------------------------------------
# grouped_errors
# ---------------------------------------------------------------------------

def test_grouped_errors():
    e1 = TsError("a.ts", 1, 1, "TS2307", "m1", None, None)
    e2 = TsError("a.ts", 2, 2, "TS2305", "m2", None, None)
    e3 = TsError("b.ts", 1, 1, "TS2307", "m3", None, None)
    grouped = grouped_errors([e1, e2, e3])
    assert set(grouped.keys()) == {"a.ts", "b.ts"}
    assert len(grouped["a.ts"]) == 2
    assert len(grouped["b.ts"]) == 1


# ---------------------------------------------------------------------------
# metrics
# ---------------------------------------------------------------------------

def test_metrics():
    e1 = TsError("a.ts", 1, 1, "TS2307", "m", None, None)
    e2 = TsError("a.ts", 2, 2, "TS2305", "m", None, None)
    e3 = TsError("b.ts", 1, 1, "TS2307", "m", None, None)
    m = metrics([e1, e2, e3])
    assert m["total_errors"] == 3
    assert m["affected_files"] == 2
    assert m["ts2307"] == 2
    assert m["ts2305"] == 1


def test_metrics_empty():
    assert metrics([]) == {"total_errors": 0, "affected_files": 0, "ts2307": 0, "ts2305": 0}


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def test_to_toon_block_legacy():
    err = TsError("a.ts", 1, 2, "TS2307", "Cannot find module './x'.", "./x", None)
    block = to_toon_block_legacy("a.ts", [err], 10)
    assert "```toon" in block
    assert "TS2307" in block
    assert "a.ts" in block
    assert "./x" in block


def test_to_toon_global_payload():
    err = TsError("a.ts", 1, 2, "TS2307", "msg", "./x", None)
    report = ReportData(errors=[err], raw_log="log")
    out = to_toon_global_payload(report, "src", 40, 10)
    assert "import_repair_report.v2" in out
    assert "total_errors: 1" in out
    assert "a.ts" in out


def test_to_toon_compact_per_file():
    err = TsError("a.ts", 1, 2, "TS2307", "msg", "./x", None)
    grouped = {"a.ts": [err]}
    out = to_toon_compact_per_file(grouped, 40, 10)
    assert "tickets[]:" in out
    assert "ticket_errors[]:" in out
    assert "a.ts" in out


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

def test_ts_error_dataclass():
    err = TsError(file_rel="x.ts", line=5, col=3, code="TS2307",
                  message="m", module_path="./a", member_name="foo")
    assert err.file_rel == "x.ts"
    assert err.line == 5
    assert err.col == 3


def test_report_data():
    rd = ReportData(errors=[], raw_log="")
    assert rd.errors == []
    assert rd.raw_log == ""
