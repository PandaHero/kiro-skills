# Tasks Engine

Use this engine only when the current phase is `tasks`.

## Behavior

- Read the approved upstream documents first.
- Convert design into prompts for a coding agent rather than a human project checklist.
- Keep tasks incremental, test-aware, and tightly scoped.

## Output Rules

- Write to `.kiro/specs/<feature-name>/tasks.md`.
- Use a numbered checkbox list with at most two levels of hierarchy.
- Every executable task must include:
  - a concrete coding objective
  - `Files/Components`
  - `Requirements` referencing granular IDs such as `1.2`
- Do not include deployment, manual QA, performance data collection, training, or marketing work.

## Gate

- After every edit, ask exactly:
  - `Do the tasks look good?`
- Stop once tasks are approved. Do not implement in the planning workflow.
