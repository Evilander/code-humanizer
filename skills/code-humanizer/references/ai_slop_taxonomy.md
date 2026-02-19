# AI Slop Code Taxonomy

## Working Definition

Use "AI slop code" for code that looks plausible but is weakly grounded in project context, weakly verified, and expensive to review.

## High-Value Detection Targets

1. Generic identifiers that hide domain intent.
2. Over-broad exception handling and low observability.
3. Low-signal comments that restate code.
4. Deep nesting and long functions.
5. Repeated boilerplate blocks that should be extracted.
6. TODO/FIXME placeholders in production paths.
7. Unverified changes with no test evidence.

## Safe vs Suggest-Only

Safe auto-apply:

- Remove low-signal comments.
- Normalize trailing whitespace.
- Limit excessive blank-line runs.

Suggest-only:

- Rename public symbols/CLI flags.
- Change exception taxonomy.
- Decompose architecture across modules.
- Alter output/contract behavior.

## Source Notes

Use these as orientation signals, not absolute truth:

- USENIX/arXiv package hallucination findings:
  - https://arxiv.org/abs/2406.10279
  - https://arxiv.org/abs/2401.01701
- Security weakness findings in generated code:
  - https://arxiv.org/abs/2310.02059
- Maintainability and duplication trends:
  - https://www.gitclear.com/coding_on_copilot_data_shows_ais_downward_pressure_on_code_quality
- Code smell study:
  - https://arxiv.org/abs/2510.03029
- Contributor policy guardrails:
  - https://coder.com/docs/about/contributing/AI_CONTRIBUTING
  - https://contributing.godotengine.org/en/latest/pull_requests/pull_request_guidelines.html
  - https://openinfra.org/legal/ai-policy/
