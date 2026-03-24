# Workflow Rules

This reference captures the operational rules behind the skill.

## Routing

- Default to normal implementation mode.
- Enter spec workflow only when the user explicitly asks for a formal spec, requirements document, design document, implementation plan, or execution of an existing spec task.
- Use a short kebab-case feature name and persist documents in `.kiro/specs/<feature-name>/`.

## Approval Gates

- Requirements must be explicitly approved before design.
- Design must be explicitly approved before tasks.
- Tasks must be explicitly approved before implementation.
- After every revision, ask for approval again.
- Do not merge phases into one interaction.

## Requirements Rules

- Draft the first requirements document immediately from the rough idea.
- Do not begin with a sequence of clarification questions.
- Use EARS acceptance criteria.
- Consider edge cases, failures, UX constraints, and success criteria in the first pass.

## Design Rules

- Research only what is needed to fill design gaps.
- Keep research in the conversation rather than a standalone research file.
- Make the design answer the approved requirements, not replace them.
- Keep implementation details in the design, not in the task list.

## Task Rules

- Treat tasks as prompts for a coding agent.
- Keep tasks incremental and test-aware.
- Use at most two levels of hierarchy.
- Every task must be actionable through code changes or automated tests.
- Every task must reference granular acceptance-criteria IDs such as `1.1` or `2.3`.
- Exclude deployment, user interviews, manual UAT, performance data gathering, training, marketing, and other non-coding tasks.

## Execution Rules

- Always read `requirements.md`, `design.md`, and `tasks.md` before executing a task.
- If a top-level task has subtasks, start with the subtask.
- Execute one task only.
- Stop after the task is complete and let the user review.
- Do not automatically continue to the next task.

## Traceability

- Acceptance criteria are the atomic requirement units.
- Task references should point to those atomic IDs.
- Use `validate_spec.py` to catch missing coverage before implementation starts.
