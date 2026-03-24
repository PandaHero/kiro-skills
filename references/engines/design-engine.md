# Design Engine

Use this engine only when the current phase is `design`.

## Behavior

- Read the approved prior document first.
- Identify research gaps and resolve them in the conversation, not in a standalone research file.
- Convert approved requirements or bugfix constraints into a concrete technical design.

## Output Rules

- Write to `.kiro/specs/<feature-name>/design.md`.
- Cover:
  - Overview
  - Architecture
  - Components and Interfaces
  - Data Models
  - Error Handling
  - Testing Strategy
- Explain major design decisions and constraints.
- Use Mermaid only when it adds clarity.

## Gate

- After every edit, ask exactly:
  - `Does the design look good? If so, we can move on to the implementation plan.`
- If design reveals missing requirements or bugfix scope, move the workflow back instead of papering over the gap.
