from __future__ import annotations

import re

SEVERITY_WEIGHT: dict[str, int] = {
    "critical": 25,
    "high": 15,
    "medium": 8,
    "low": 4,
}

SEVERITY_ORDER: dict[str, int] = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}

DEFAULT_EXTENSIONS: set[str] = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".go",
    ".rs",
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".hpp",
    ".cs",
    ".php",
    ".rb",
}

DEFAULT_EXCLUDED_DIRS: set[str] = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "build",
}

DEFAULT_TEST_DIRS: set[str] = {
    "test",
    "tests",
    "__tests__",
}

GENERIC_IDENTIFIER_NAMES: set[str] = {
    "process_data",
    "handle_request",
    "helper",
    "utils",
    "util",
    "manager",
    "service",
    "main_logic",
    "do_stuff",
    "process",
    "handler",
}

LOW_SIGNAL_COMMENT_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^\s*(this|that)\s+(function|method|class)\s+", re.IGNORECASE),
    re.compile(r"^\s*(simply|just)\s+", re.IGNORECASE),
    re.compile(r"^\s*(sets?|gets?|returns?|checks?)\s+", re.IGNORECASE),
    re.compile(r"^\s*(initialize|initializes)\s+", re.IGNORECASE),
)

TODO_PATTERN = re.compile(r"\b(TODO|FIXME|XXX)\b", re.IGNORECASE)
TODO_COMMENT_PATTERN = re.compile(r"^\s*(#|//|/\*)\s*(TODO|FIXME|XXX)\b", re.IGNORECASE)
PY_BARE_EXCEPT_PATTERN = re.compile(r"^\s*except\s*:\s*$")
PY_BROAD_EXCEPT_PATTERN = re.compile(r"^\s*except\s+Exception(?:\s+as\s+\w+)?\s*:\s*$")
PY_FUNC_OR_CLASS_PATTERN = re.compile(r"^\s*(def|class)\s+([A-Za-z_][A-Za-z0-9_]*)\b")
JS_FUNC_PATTERN = re.compile(
    r"^\s*(?:function\s+([A-Za-z_][A-Za-z0-9_]*)|\bconst\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\()"
)
