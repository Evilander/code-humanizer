# Claude Code Companion: Code Humanizer

Use this workflow when a user asks to make code less "AI slop" and more expert-level.

## Goals

1. Reduce reviewer burden (clarity, ownership, testability).
2. Keep behavior stable by default.
3. Separate safe cleanup from risky architectural refactors.

## Workflow

1. Run baseline scan:
   - `python -m humanize_code.cli scan <target-path>`
2. Apply safe rewrites:
   - `python -m humanize_code.cli rewrite <target-path> --diff`
   - `python -m humanize_code.cli rewrite <target-path> --apply`
3. Re-run scan and tests.
4. Create suggest-only plan for high-risk items:
   - Rename generic identifiers to domain names.
   - Replace broad exception handling with typed exceptions.
   - Split long functions and deep nesting.
   - Remove speculative abstractions not justified by real use.

## Risk Policy

- Safe auto-apply:
  - Remove low-signal comments.
  - Normalize trailing whitespace.
  - Collapse excessive blank-line runs.
- Suggest-only:
  - Public API/CLI renames.
  - Exception taxonomy changes.
  - Architecture-level decomposition.
  - Output-contract or exit-code changes.

## Output Template

Provide:

1. Top issues by severity with file:line.
2. Safe rewrites performed and why they are behavior-preserving.
3. Suggested risky rewrites with impact/risk/rollback notes.
