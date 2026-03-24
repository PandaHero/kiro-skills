# Bugfix Workflow

This variant starts with a bugfix analysis document instead of feature requirements.

## Intent

- Capture the broken behavior, reproduction, regression constraints, and root-cause hypothesis first.
- Preserve unchanged behavior explicitly.
- Keep the fix scoped and surgical unless the analysis proves a wider refactor is required.

## Phase Order

- `bugfix -> design -> tasks -> execute -> completed`

## Bugfix Document Rules

- Record the observed behavior and expected behavior separately.
- List unaffected behavior that must remain stable.
- Add regression-focused acceptance criteria.
- Use the design and task phases only after the bugfix analysis is explicitly approved.
