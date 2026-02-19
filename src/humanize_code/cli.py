from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path

from .analyzer import analyze_file, iter_source_files, summarize_severity
from .models import FileReport, Issue
from .rewriter import rewrite_file
from .rules import DEFAULT_EXTENSIONS, SEVERITY_ORDER


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="code-humanizer",
        description="Detect and reduce AI-slop code patterns with safe rewrites.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Analyze source files and score AI-slop risk.")
    scan_parser.add_argument("paths", nargs="+", help="File or directory paths.")
    scan_parser.add_argument("--json", action="store_true", help="Emit JSON instead of human-readable text.")
    scan_parser.add_argument(
        "--fail-on",
        choices=["none", "low", "medium", "high", "critical"],
        default="none",
        help="Return exit code 2 if any issue at or above this severity exists.",
    )
    scan_parser.add_argument(
        "--extensions",
        nargs="*",
        default=None,
        help="Override extension set, example: --extensions .py .ts .tsx",
    )
    scan_parser.add_argument(
        "--include-tests",
        action="store_true",
        help="Include test files in analysis (excluded by default).",
    )

    rewrite_parser = subparsers.add_parser("rewrite", help="Preview or apply safe rewrites.")
    rewrite_parser.add_argument("paths", nargs="+", help="File or directory paths.")
    rewrite_parser.add_argument("--apply", action="store_true", help="Write safe rewrites to disk.")
    rewrite_parser.add_argument("--diff", action="store_true", help="Print unified diff for changed files.")
    rewrite_parser.add_argument(
        "--extensions",
        nargs="*",
        default=None,
        help="Override extension set, example: --extensions .py .js",
    )
    rewrite_parser.add_argument(
        "--include-tests",
        action="store_true",
        help="Include test files in rewrite pass (excluded by default).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "scan":
        return run_scan(args)
    if args.command == "rewrite":
        return run_rewrite(args)
    parser.print_help()
    return 1


def run_scan(args: argparse.Namespace) -> int:
    paths = [Path(item) for item in args.paths]
    extensions = set(args.extensions) if args.extensions else DEFAULT_EXTENSIONS
    files = iter_source_files(paths, extensions=extensions, include_tests=args.include_tests)
    reports = [analyze_file(path) for path in files]
    reports = [report for report in reports if report.issues]

    if args.json:
        payload = {
            "file_count": len(files),
            "flagged_file_count": len(reports),
            "reports": [report.to_dict() for report in reports],
        }
        print(json.dumps(payload, indent=2))
    else:
        _print_human_scan(files, reports)

    if args.fail_on != "none" and _has_severity_at_or_above(reports, args.fail_on):
        return 2
    return 0


def run_rewrite(args: argparse.Namespace) -> int:
    paths = [Path(item) for item in args.paths]
    extensions = set(args.extensions) if args.extensions else DEFAULT_EXTENSIONS
    files = iter_source_files(paths, extensions=extensions, include_tests=args.include_tests)

    changed_reports = []
    for path in files:
        report = rewrite_file(path, apply=args.apply)
        if report.changed:
            changed_reports.append(report)
            mode = "applied" if args.apply else "preview"
            print(f"[{mode}] {report.path} ({report.change_count} safe changes)")
            if args.diff:
                diff = difflib.unified_diff(
                    report.original.splitlines(),
                    report.rewritten.splitlines(),
                    fromfile=f"{report.path}:before",
                    tofile=f"{report.path}:after",
                    lineterm="",
                )
                print("\n".join(diff))
    if not changed_reports:
        print("No safe rewrites were necessary.")
    return 0


def _print_human_scan(files: list[Path], reports: list[FileReport]) -> None:
    print(f"Scanned files: {len(files)}")
    print(f"Flagged files: {len(reports)}")
    severity_totals = _summarize_reports(reports)
    if severity_totals:
        summary = ", ".join(
            f"{severity}={count}"
            for severity, count in sorted(severity_totals.items(), key=lambda item: SEVERITY_ORDER[item[0]], reverse=True)
        )
        print(f"Issues by severity: {summary}")
    print("")
    for report in reports:
        print(f"{report.path}  slop_score={report.score}")
        for issue in report.issues:
            print(_format_issue(issue))
        print("")


def _format_issue(issue: Issue) -> str:
    line_text = f"line {issue.line}" if issue.line else "line ?"
    base = f"  - [{issue.severity.upper()}] {issue.code} ({line_text}): {issue.message}"
    if issue.suggestion:
        base += f" | Suggestion: {issue.suggestion}"
    return base


def _has_severity_at_or_above(reports: list[FileReport], threshold: str) -> bool:
    threshold_value = SEVERITY_ORDER[threshold]
    for report in reports:
        counts = summarize_severity(report.issues)
        for severity, count in counts.items():
            if count and SEVERITY_ORDER.get(severity, 0) >= threshold_value:
                return True
    return False


def _summarize_reports(reports: list[FileReport]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for report in reports:
        for severity, count in summarize_severity(report.issues).items():
            totals[severity] = totals.get(severity, 0) + count
    return totals


if __name__ == "__main__":
    raise SystemExit(main())
