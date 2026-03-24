# Requirements Engine

Use this engine only when the current phase is `requirements`.

## Behavior

- Generate the initial requirements document immediately from the rough idea.
- Do not begin with a chain of clarification questions.
- Focus on product behavior, constraints, failure cases, and acceptance criteria.
- Use EARS for every acceptance criterion.

## Output Rules

- Write to `.kiro/specs/<feature-name>/requirements.md`.
- Use a short introduction followed by numbered requirement sections.
- Each requirement must include:
  - a user story
  - numbered EARS acceptance criteria
- Suggest targeted clarifications only after the initial draft exists.

## Gate

- After every edit, ask exactly:
  - `Do the requirements look good? If so, we can move on to the design.`
- Record approval with `approve_phase.py`, then move forward with `advance_phase.py`.
