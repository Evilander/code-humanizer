from __future__ import annotations

import io
import tokenize
from pathlib import Path

from .models import RewriteResult
from .rules import LOW_SIGNAL_COMMENT_PATTERNS


def rewrite_file(path: Path, apply: bool = False) -> RewriteResult:
    original = path.read_text(encoding="utf-8", errors="ignore")
    rewritten, change_count = rewrite_text(original, suffix=path.suffix.lower())
    changed = rewritten != original
    if apply and changed:
        path.write_text(rewritten, encoding="utf-8")
    return RewriteResult(
        path=str(path),
        changed=changed,
        original=original,
        rewritten=rewritten,
        change_count=change_count,
    )


def rewrite_text(text: str, suffix: str = "") -> tuple[str, int]:
    lines = text.splitlines()
    output: list[str] = []
    changes = 0
    blank_run = 0
    removable_comment_lines = _python_low_signal_comment_lines(text) if suffix == ".py" else set()

    for index, line in enumerate(lines, start=1):
        trimmed = line.rstrip()
        if trimmed != line:
            changes += 1

        if index in removable_comment_lines:
            changes += 1
            continue

        if trimmed == "":
            blank_run += 1
            if blank_run > 2:
                changes += 1
                continue
        else:
            blank_run = 0

        output.append(trimmed)

    rewritten = "\n".join(output)
    if text.endswith("\n"):
        rewritten += "\n"
    return rewritten, changes


def _python_low_signal_comment_lines(text: str) -> set[int]:
    lines = text.splitlines()
    removable: set[int] = set()
    try:
        tokens = tokenize.generate_tokens(io.StringIO(text).readline)
    except tokenize.TokenError:
        return removable

    for token in tokens:
        if token.type != tokenize.COMMENT:
            continue
        line_number, column = token.start
        comment_line = lines[line_number - 1] if 0 < line_number <= len(lines) else ""
        prefix = comment_line[:column]
        if prefix.strip():
            continue
        body = token.string.removeprefix("#").strip()
        if not body:
            continue
        if any(pattern.match(body) for pattern in LOW_SIGNAL_COMMENT_PATTERNS):
            removable.add(line_number)
    return removable
