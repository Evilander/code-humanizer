---
name: code-humanizer
description: Detect and reduce AI-slop code patterns while preserving behavior by default. Use when a user asks to make code more expert-level, less generic, easier to review, or less likely to be AI-generated; also use for PR hygiene passes focused on naming quality, exception scope, duplicated logic, deep nesting, low-signal comments, and maintainability risk in Python or polyglot repositories.
---

# Code Humanizer

Run an opinionated AI-slop triage workflow that protects behavior while improving maintainability and review quality.

## Workflow

1. Baseline scan.
2. Apply only safe rewrites automatically.
3. Re-run scan and tests.
4. Produce suggest-only recommendations for risky improvements.

## Step 1: Baseline Scan

Run:

```bash
python skills/code-humanizer/scripts/run_humanizer.py scan <target-path>
```

Use `--json` when another tool should consume the result:

```bash
python skills/code-humanizer/scripts/run_humanizer.py scan <target-path> --json
```

Prioritize `critical` and `high` issues first, then tackle `medium`.

## Step 2: Safe Rewrites

Preview:

```bash
python skills/code-humanizer/scripts/run_humanizer.py rewrite <target-path> --diff
```

Apply:

```bash
python skills/code-humanizer/scripts/run_humanizer.py rewrite <target-path> --apply
```

Safe rewrites are intentionally narrow:

- Remove low-signal comments that restate obvious behavior.
- Trim trailing whitespace.
- Collapse excessive blank-line runs.

## Step 3: Verification

After safe rewrites:

1. Re-run project tests.
2. Re-run scan and compare score trend.
3. Confirm no public behavior contract changed.

## Step 4: Suggest-Only Improvements

Do not auto-apply these without explicit approval:

- Rename public identifiers or CLI flags.
- Replace broad exception handling with typed taxonomies.
- Split long functions or large files where structure changes are non-trivial.
- Remove speculative abstractions that may alter extension points.

For each suggest-only item, include:

1. File and line.
2. Why it matters for reviewability/maintainability.
3. Risk level and rollback note.

## References

Read only what is needed:

- Core taxonomy and source links: `references/ai_slop_taxonomy.md`
- Community complaint patterns: `references/reddit_patterns.md`
