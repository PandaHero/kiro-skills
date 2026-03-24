# Design-First Workflow

This variant starts at technical design instead of formal requirements.

## Intent

- Use when the user already knows the implementation direction and wants to reason about architecture before formalizing every user story.
- Keep design explicit, then decompose into code-agent tasks.

## Phase Order

- `design -> tasks -> execute -> completed`

## Rules

- Make assumptions visible in the design overview.
- If design discussions uncover unresolved product behavior, move back to a feature spec workflow instead of hiding the gap.
- Task decomposition rules remain identical to the standard workflow.
