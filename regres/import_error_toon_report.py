from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FRONTEND_CWD = PROJECT_ROOT / "frontend"
DEFAULT_OUT_MD = PROJECT_ROOT / ".regres" / "import-error-toon-report.md"
DEFAULT_RAW_LOG = PROJECT_ROOT / ".regres" / "import-error-toon-report.raw.log"

TS_ERROR_RE = re.compile(
    r"^(?P<file>.+?\.(?:ts|tsx))\((?P<line>\d+),(?P<col>\d+)\):\s+error\s+(?P<code>TS\d+):\s+(?P<msg>.+)$"
)
MISSING_MODULE_RE = re.compile(r"Cannot find module '([^']+)'")
EXPORTED_MEMBER_RE = re.compile(r"has no exported member '([^']+)'")


@dataclass
class TsError:
    file_rel: str
    line: int
    col: int
    code: str
    message: str
    module_path: str | None
    member_name: str | None


@dataclass
class ReportData:
    errors: list[TsError]
    raw_log: str


def toon_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create compact Toon markdown from TS errors")
    parser.add_argument("--input-log", type=Path, default=None, help="Use existing log instead of running type-check")
    parser.add_argument("--frontend-cwd", type=Path, default=DEFAULT_FRONTEND_CWD)
    parser.add_argument("--typecheck-cmd", default="npm run -s type-check")
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    parser.add_argument("--out-raw-log", type=Path, default=DEFAULT_RAW_LOG)
    parser.add_argument("--max-files", type=int, default=40)
    parser.add_argument("--max-errors-per-file", type=int, default=10)
    parser.add_argument("--include-codes", default="TS2307,TS2305")
    parser.add_argument("--scan-root", default="frontend/src")
    return parser.parse_args()


def run_typecheck(cwd: Path, command: str) -> str:
    # Clear TypeScript incremental cache to avoid stale diagnostics.
    for tsbuildinfo in cwd.rglob("*.tsbuildinfo"):
        try:
            tsbuildinfo.unlink()
        except OSError:
            pass
    proc = subprocess.run(
        command,
        cwd=str(cwd),
        shell=True,
        text=True,
        capture_output=True,
        check=False,
    )
    out = (proc.stdout or "") + ("\n" if proc.stdout and proc.stderr else "") + (proc.stderr or "")
    return out.strip()


def normalize_file_rel(raw_file: str, cwd: Path) -> str:
    p = Path(raw_file)
    if not p.is_absolute():
        p = (cwd / p).resolve()
    try:
        return str(p.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(p).replace("\\", "/")


def parse_ts_errors(log_text: str, cwd: Path, include_codes: set[str]) -> list[TsError]:
    errors: list[TsError] = []
    for ln in log_text.splitlines():
        m = TS_ERROR_RE.match(ln.strip())
        if not m:
            continue
        code = m.group("code")
        if include_codes and code not in include_codes:
            continue
        msg = m.group("msg")
        miss = MISSING_MODULE_RE.search(msg)
        member = EXPORTED_MEMBER_RE.search(msg)
        errors.append(
            TsError(
                file_rel=normalize_file_rel(m.group("file"), cwd),
                line=int(m.group("line")),
                col=int(m.group("col")),
                code=code,
                message=msg,
                module_path=miss.group(1) if miss else None,
                member_name=member.group(1) if member else None,
            )
        )
    return errors


def suggestions_for_error(err: TsError) -> list[str]:
    out: list[str] = []
    if err.code == "TS2307":
        mod = err.module_path or ""
        if mod.startswith("@c2004/"):
            out.append("Sprawdź alias w `frontend/vite.config.ts` i czy docelowy plik istnieje.")
        elif mod.startswith("./") or mod.startswith("../"):
            out.append("Zweryfikuj relatywną ścieżkę i poziom zagnieżdżenia po refaktorze.")
            if mod.count("../") >= 3:
                out.append("Rozważ zamianę głębokiej ścieżki na alias `@c2004/*`.")
        else:
            out.append("Sprawdź czy import wskazuje na poprawny pakiet/moduł.")
    elif err.code == "TS2305":
        out.append("Sprawdź eksporty docelowego modułu i ewentualny cykl wrapperów re-export.")
        if err.member_name:
            out.append(f"Zweryfikuj, czy symbol `{err.member_name}` jest rzeczywiście eksportowany.")
    return out


def grouped_errors(errors: Iterable[TsError]) -> dict[str, list[TsError]]:
    grouped: dict[str, list[TsError]] = defaultdict(list)
    for e in errors:
        grouped[e.file_rel].append(e)
    return dict(grouped)


def metrics(errors: list[TsError]) -> dict[str, int]:
    c = Counter(e.code for e in errors)
    return {
        "total_errors": len(errors),
        "affected_files": len({e.file_rel for e in errors}),
        "ts2307": c.get("TS2307", 0),
        "ts2305": c.get("TS2305", 0),
    }


def to_toon_block_legacy(file_rel: str, errs: list[TsError], max_errors: int) -> str:
    lines = [
        "```toon",
        "kind: import_repair_ticket",
        f"file: {file_rel}",
        f"error_count: {len(errs)}",
        "errors:",
    ]
    for e in errs[:max_errors]:
        lines.append(f"  - code: {e.code}")
        lines.append(f"    line: {e.line}")
        lines.append(f"    col: {e.col}")
        if e.module_path:
            lines.append(f"    module: '{e.module_path}'")
        lines.append(f"    message: '{e.message.replace("'", "\\'")}'")

    actions: list[str] = []
    for e in errs[:max_errors]:
        actions.extend(suggestions_for_error(e))
    uniq_actions = list(dict.fromkeys(actions))
    if uniq_actions:
        lines.append("actions:")
        for a in uniq_actions[:6]:
            lines.append(f"  - '{a.replace("'", "\\'")}'")
    lines.append("```")
    return "\n".join(lines)


def to_toon_global_payload(
    report: ReportData,
    scan_root: str,
    max_files: int,
    max_errors_per_file: int,
) -> str:
    grouped = grouped_errors(report.errors)
    m = metrics(report.errors)
    module_counter = Counter(e.module_path for e in report.errors if e.module_path)
    file_order = sorted(grouped.items(), key=lambda kv: len(kv[1]), reverse=True)

    lines: list[str] = [
        "```toon",
        "report:",
        "  schema: import_repair_report.v2",
        f"  generated_at: {toon_quote(datetime.now(timezone.utc).isoformat())}",
        f"  scan_root: {toon_quote(scan_root)}",
        "  metrics:",
        f"    total_errors: {m['total_errors']}",
        f"    affected_files: {m['affected_files']}",
        f"    ts2307: {m['ts2307']}",
        f"    ts2305: {m['ts2305']}",
        "",
        "  top_missing_modules[]:",
        "    module count",
    ]

    for mod, cnt in module_counter.most_common(20):
        lines.append(f"    {toon_quote(mod)} {cnt}")

    lines.extend([
        "",
        "  files[]:",
        "    file error_count ts2307 ts2305",
    ])
    for file_rel, errs in file_order[:max_files]:
        c = Counter(e.code for e in errs)
        lines.append(
            f"    {toon_quote(file_rel)} {len(errs)} {c.get('TS2307', 0)} {c.get('TS2305', 0)}"
        )

    lines.extend([
        "",
        "  file_error_rows[]:",
        "    file code line col module member message",
    ])
    for file_rel, errs in file_order[:max_files]:
        for e in errs[:max_errors_per_file]:
            lines.append(
                "    "
                + " ".join(
                    [
                        toon_quote(file_rel),
                        e.code,
                        str(e.line),
                        str(e.col),
                        toon_quote(e.module_path or ""),
                        toon_quote(e.member_name or ""),
                        toon_quote(e.message),
                    ]
                )
            )

    lines.append("```")
    return "\n".join(lines)


def to_toon_compact_per_file(grouped: dict[str, list[TsError]], max_files: int, max_errors: int) -> str:
    file_order = sorted(grouped.items(), key=lambda kv: len(kv[1]), reverse=True)
    lines: list[str] = [
        "```toon",
        "tickets[]:",
        "  file error_count primary_code",
    ]
    for file_rel, errs in file_order[:max_files]:
        primary_code = Counter(e.code for e in errs).most_common(1)[0][0] if errs else ""
        lines.append(f"  {toon_quote(file_rel)} {len(errs)} {primary_code}")

    lines.extend([
        "",
        "ticket_errors[]:",
        "  file code line col module message",
    ])
    for file_rel, errs in file_order[:max_files]:
        for e in errs[:max_errors]:
            lines.append(
                f"  {toon_quote(file_rel)} {e.code} {e.line} {e.col} {toon_quote(e.module_path or '')} {toon_quote(e.message)}"
            )

    lines.append("```")
    return "\n".join(lines)


def render_markdown(report: ReportData, scan_root: str, max_files: int, max_errors_per_file: int) -> str:
    grouped = grouped_errors(report.errors)
    m = metrics(report.errors)

    module_counter = Counter(e.module_path for e in report.errors if e.module_path)
    file_order = sorted(grouped.items(), key=lambda kv: len(kv[1]), reverse=True)

    out: list[str] = [
        "# Import Repair Compact Report",
        "",
        "## TOON Global Payload",
        "",
        to_toon_global_payload(report, scan_root, max_files, max_errors_per_file),
        "",
        "## TOON Compact Tickets",
        "",
        to_toon_compact_per_file(grouped, max_files, max_errors_per_file),
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| total_errors | {m['total_errors']} |",
        f"| affected_files | {m['affected_files']} |",
        f"| TS2307 | {m['ts2307']} |",
        f"| TS2305 | {m['ts2305']} |",
        f"| scan_root | `{scan_root}` |",
        "",
    ]

    if module_counter:
        out.extend([
            "## Top Missing Modules",
            "",
            "| module | count |",
            "|---|---:|",
        ])
        for mod, cnt in module_counter.most_common(20):
            out.append(f"| `{mod}` | {cnt} |")
        out.append("")

    out.extend([
        "## Files (Toon blocks - legacy ticket style)",
        "",
    ])

    for file_rel, errs in file_order[:max_files]:
        out.append(f"### `{file_rel}` ({len(errs)})")
        out.append("")
        out.append(to_toon_block_legacy(file_rel, errs, max_errors_per_file))
        out.append("")

    out.extend([
        "## Raw Log (truncated)",
        "",
        "```text",
        "\n".join(report.raw_log.splitlines()[:200]),
        "```",
        "",
    ])

    return "\n".join(out)


def main() -> int:
    args = parse_args()
    include_codes = {x.strip() for x in args.include_codes.split(",") if x.strip()}

    if args.input_log:
        raw_log = args.input_log.read_text(encoding="utf-8")
    else:
        raw_log = run_typecheck(args.frontend_cwd, args.typecheck_cmd)

    errs = parse_ts_errors(raw_log, args.frontend_cwd, include_codes)

    report = ReportData(errors=errs, raw_log=raw_log)
    md = render_markdown(report, args.scan_root, args.max_files, args.max_errors_per_file)

    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(md, encoding="utf-8")
    args.out_raw_log.parent.mkdir(parents=True, exist_ok=True)
    args.out_raw_log.write_text(raw_log, encoding="utf-8")

    print(f"[import-error-toon-report] saved markdown: {args.out_md}")
    print(f"[import-error-toon-report] saved raw log: {args.out_raw_log}")
    print(f"[import-error-toon-report] parsed errors: {len(errs)} in {len({e.file_rel for e in errs})} files")

    return 0


if __name__ == "__main__":
    sys.exit(main())
