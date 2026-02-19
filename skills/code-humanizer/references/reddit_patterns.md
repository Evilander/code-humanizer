# Reddit Complaint Patterns

## Recurring Complaints

1. Review throughput collapse from high-volume low-quality AI PRs.
2. Contributors cannot explain or debug generated code.
3. Untested, non-compiling patches consume reviewer cycles.
4. Random abstractions, duplication, and vague naming.
5. Code passes superficial review but fails under edge cases.
6. Technical debt accumulation due to low-context generation.

## Practical Translation Into Rules

- Flag generic names and duplicated blocks.
- Flag broad exception handling.
- Penalize deep nesting/long functions.
- Treat TODO/FIXME as unresolved maintenance debt.
- Keep auto-apply rewrites restricted to behavior-preserving cleanup.

## Example Threads

- https://www.reddit.com/r/ExperiencedDevs/comments/1nx21xo/how_to_maintain_code_quality_with_ai_slop/
- https://www.reddit.com/r/ExperiencedDevs/comments/1jfhqye/reviewing_coworkers_aigenerated_prs/
- https://www.reddit.com/r/opensource/comments/1q3f89b/open_source_is_being_ddosed_by_ai_slop_and_github/
- https://www.reddit.com/r/cscareerquestions/comments/1oa5nx7/ai_slop_code_ai_is_hiding_incompetence_that_used/
- https://www.reddit.com/r/programming/comments/1it1usc/how_ai_generated_code_accelerates_technical_debt/
