from __future__ import annotations

from pathlib import Path

from .models import RewriteResult
from .rules import LOW_SIGNAL_COMMENT_PATTERNS


def rewrite_file(path: Path, apply: bool = False) -> RewriteResult:
    original = path.read_text(encoding="utf-8", errors="ignore")
    rewritten, change_count = rewrite_text(original)
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


def rewrite_text(text: str) -> tuple[str, int]:
    lines = text.splitlines()
    output: list[str] = []
    changes = 0
    blank_run = 0

    for line in lines:
        trimmed = line.rstrip()
        if trimmed != line:
            changes += 1

        if _is_low_signal_comment(trimmed):
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


def _is_low_signal_comment(line: str) -> bool:
    stripped = line.strip()
    if stripped.startswith("#"):
        body = stripped.removeprefix("#").strip()
    elif stripped.startswith("//"):
        body = stripped.removeprefix("//").strip()
    else:
        return False
    if not body:
        return False
    return any(pattern.match(body) for pattern in LOW_SIGNAL_COMMENT_PATTERNS)

