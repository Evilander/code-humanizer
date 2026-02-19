from __future__ import annotations

import ast
from collections import Counter, defaultdict
from pathlib import Path

from .models import FileReport, Issue
from .rules import (
    DEFAULT_EXTENSIONS,
    DEFAULT_EXCLUDED_DIRS,
    DEFAULT_TEST_DIRS,
    GENERIC_IDENTIFIER_NAMES,
    JS_FUNC_PATTERN,
    LOW_SIGNAL_COMMENT_PATTERNS,
    PY_BARE_EXCEPT_PATTERN,
    PY_BROAD_EXCEPT_PATTERN,
    PY_FUNC_OR_CLASS_PATTERN,
    SEVERITY_WEIGHT,
    TODO_COMMENT_PATTERN,
)


def iter_source_files(
    paths: list[Path],
    extensions: set[str] | None = None,
    include_tests: bool = False,
    excluded_dirs: set[str] | None = None,
) -> list[Path]:
    exts = extensions or DEFAULT_EXTENSIONS
    skip_dirs = excluded_dirs or DEFAULT_EXCLUDED_DIRS
    discovered: list[Path] = []
    for path in paths:
        if path.is_file():
            if path.suffix.lower() in exts:
                if _should_skip_file(path, include_tests=include_tests, excluded_dirs=skip_dirs):
                    continue
                discovered.append(path)
            continue
        if path.is_dir():
            for file in path.rglob("*"):
                if not file.is_file():
                    continue
                if _has_excluded_dir(file, skip_dirs):
                    continue
                if file.suffix.lower() in exts:
                    if _should_skip_file(file, include_tests=include_tests, excluded_dirs=skip_dirs):
                        continue
                    discovered.append(file)
    return sorted(set(discovered))


def analyze_file(path: Path) -> FileReport:
    text = path.read_text(encoding="utf-8", errors="ignore")
    issues = analyze_text(text, suffix=path.suffix.lower())
    score = calculate_score(issues)
    return FileReport(path=str(path), score=score, issues=issues)


def analyze_text(text: str, suffix: str = "") -> list[Issue]:
    lines = text.splitlines()
    issues: list[Issue] = []

    issues.extend(_find_generic_names(lines, suffix))
    issues.extend(_find_broad_exceptions(lines, suffix))
    issues.extend(_find_low_signal_comments(lines))
    issues.extend(_find_deep_nesting(lines, suffix))
    issues.extend(_find_duplicate_blocks(lines))
    issues.extend(_find_todo_markers(lines))

    if suffix == ".py":
        issues.extend(_find_long_python_functions(text))

    if len(lines) > 700:
        issues.append(
            Issue(
                code="LARGE_FILE",
                severity="low",
                line=1,
                message="Very large file; split responsibilities to improve readability.",
                suggestion="Refactor into smaller modules with clear ownership.",
            )
        )

    return issues


def calculate_score(issues: list[Issue]) -> int:
    score = sum(SEVERITY_WEIGHT.get(issue.severity, 0) for issue in issues[:20])
    return min(score, 100)


def _find_generic_names(lines: list[str], suffix: str) -> list[Issue]:
    findings: list[Issue] = []
    for index, line in enumerate(lines, start=1):
        if suffix == ".py":
            match = PY_FUNC_OR_CLASS_PATTERN.match(line)
            name = match.group(2) if match else None
        elif suffix in {".js", ".jsx", ".ts", ".tsx"}:
            match = JS_FUNC_PATTERN.match(line)
            name = (match.group(1) or match.group(2)) if match else None
        else:
            name = None
        if name and name.lower() in GENERIC_IDENTIFIER_NAMES:
            findings.append(
                Issue(
                    code="GENERIC_NAME",
                    severity="medium",
                    line=index,
                    message=f"Generic identifier '{name}' hides domain intent.",
                    suggestion="Rename using task-specific domain terms.",
                )
            )
    return findings


def _find_broad_exceptions(lines: list[str], suffix: str) -> list[Issue]:
    if suffix != ".py":
        return []
    findings: list[Issue] = []
    for index, line in enumerate(lines, start=1):
        if PY_BARE_EXCEPT_PATTERN.match(line):
            findings.append(
                Issue(
                    code="BARE_EXCEPT",
                    severity="high",
                    line=index,
                    message="Bare except catches everything and hides failure mode.",
                    suggestion="Catch explicit exception types and handle intentionally.",
                )
            )
        elif PY_BROAD_EXCEPT_PATTERN.match(line):
            findings.append(
                Issue(
                    code="BROAD_EXCEPTION",
                    severity="medium",
                    line=index,
                    message="Over-broad exception handling reduces observability.",
                    suggestion="Catch narrower exception classes and preserve context.",
                )
            )
    return findings


def _find_low_signal_comments(lines: list[str]) -> list[Issue]:
    findings: list[Issue] = []
    for index, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("#"):
            body = stripped.removeprefix("#").strip()
        elif stripped.startswith("//"):
            body = stripped.removeprefix("//").strip()
        else:
            continue
        if not body:
            continue
        if any(pattern.match(body) for pattern in LOW_SIGNAL_COMMENT_PATTERNS):
            findings.append(
                Issue(
                    code="LOW_SIGNAL_COMMENT",
                    severity="low",
                    line=index,
                    message="Comment likely restates obvious code behavior.",
                    suggestion="Remove it, or replace with rationale and trade-offs.",
                )
            )
    return findings


def _find_deep_nesting(lines: list[str], suffix: str) -> list[Issue]:
    findings: list[Issue] = []
    if suffix == ".py":
        for index, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            depth = (len(line) - len(line.lstrip(" "))) // 4
            if depth >= 4:
                findings.append(
                    Issue(
                        code="DEEP_NESTING",
                        severity="medium",
                        line=index,
                        message="Deep nesting increases cognitive load.",
                        suggestion="Use guard clauses and extract focused helper functions.",
                    )
                )
                break
        return findings

    if suffix in {".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".rs", ".c", ".cc", ".cpp", ".cs"}:
        depth = 0
        for index, line in enumerate(lines, start=1):
            depth += line.count("{")
            depth -= line.count("}")
            if depth >= 5:
                findings.append(
                    Issue(
                        code="DEEP_NESTING",
                        severity="medium",
                        line=index,
                        message="Deep brace nesting indicates complex control flow.",
                        suggestion="Split branches into smaller units and return early.",
                    )
                )
                break
    return findings


def _find_duplicate_blocks(lines: list[str], window: int = 4) -> list[Issue]:
    normalized: list[tuple[int, str]] = []
    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("//"):
            continue
        normalized.append((idx, stripped))
    if len(normalized) < window * 2:
        return []

    fingerprint_index: defaultdict[tuple[str, ...], list[int]] = defaultdict(list)
    for i in range(0, len(normalized) - window + 1):
        block = tuple(token for _, token in normalized[i : i + window])
        fingerprint_index[block].append(normalized[i][0])

    findings: list[Issue] = []
    for block, starts in fingerprint_index.items():
        if len(starts) < 2:
            continue
        if len(set(block)) <= 1:
            continue
        findings.append(
            Issue(
                code="DUPLICATE_BLOCK",
                severity="medium",
                line=starts[1],
                message=f"Repeated {window}-line block appears {len(starts)} times.",
                suggestion="Extract shared behavior when repetition represents one concept.",
            )
        )
        break
    return findings


def _find_todo_markers(lines: list[str]) -> list[Issue]:
    findings: list[Issue] = []
    for index, line in enumerate(lines, start=1):
        if TODO_COMMENT_PATTERN.search(line):
            findings.append(
                Issue(
                    code="TODO_MARKER",
                    severity="low",
                    line=index,
                    message="TODO/FIXME marker left in source.",
                    suggestion="Resolve it or create a tracked issue reference.",
                )
            )
    return findings


def _find_long_python_functions(text: str) -> list[Issue]:
    findings: list[Issue] = []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return findings

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start = getattr(node, "lineno", 0)
            end = getattr(node, "end_lineno", start)
            length = max(0, end - start + 1)
            if length > 80:
                findings.append(
                    Issue(
                        code="LONG_FUNCTION",
                        severity="medium",
                        line=start,
                        message=f"Function '{node.name}' is {length} lines long.",
                        suggestion="Split into composable functions with explicit responsibilities.",
                    )
                )
    return findings


def summarize_severity(issues: list[Issue]) -> dict[str, int]:
    return dict(Counter(issue.severity for issue in issues))


def _has_excluded_dir(path: Path, excluded_dirs: set[str]) -> bool:
    return any(part in excluded_dirs for part in path.parts)


def _looks_like_test_file(path: Path) -> bool:
    name = path.name.lower()
    if name.startswith("test_") or name.endswith("_test.py"):
        return True
    if ".test." in name or ".spec." in name:
        return True
    return any(part.lower() in DEFAULT_TEST_DIRS for part in path.parts)


def _should_skip_file(path: Path, include_tests: bool, excluded_dirs: set[str]) -> bool:
    if _has_excluded_dir(path, excluded_dirs):
        return True
    if include_tests:
        return False
    return _looks_like_test_file(path)
