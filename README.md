# Code Humanizer

Clean up your AI Agent's slop.

`code-humanizer` is a Python project plus agent-ready skill files that detect and reduce "AI slop" patterns in source code.

It focuses on two outcomes:

1. Surface maintainability issues that reviewers repeatedly complain about.
2. Apply only low-risk cleanup automatically, while labeling higher-risk rewrites as suggest-only.

## What Counts As AI Slop (Practical)

- Generic, context-free naming (`process_data`, `manager`, `helper`)
- Over-broad exception handling (`except Exception`, bare `except`)
- Low-signal comments that restate obvious code
- Deep nesting and bloated functions
- Repeated boilerplate blocks
- TODO/FIXME placeholders left in production paths

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
```

Scan a repository:

```bash
code-humanizer scan .
```

By default, test files are excluded to reduce noise in production-focused triage. Include tests explicitly:

```bash
code-humanizer scan . --include-tests
```

Emit JSON:

```bash
code-humanizer scan . --json
```

Preview safe rewrites:

```bash
code-humanizer rewrite . --diff
```

Apply safe rewrites:

```bash
code-humanizer rewrite . --apply
```

Include test files in rewrite mode if needed:

```bash
code-humanizer rewrite . --include-tests --diff
```

Run tests:

```bash
pytest -q
```

## Included Agent Resources

- Codex skill: `skills/code-humanizer/SKILL.md`
- Claude companion guide: `claude-code/CLAUDE.md`
- Research references: `skills/code-humanizer/references/`
