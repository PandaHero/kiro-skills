# EARS Patterns

EARS stands for Easy Approach to Requirements Syntax. Use it to turn vague product language into testable acceptance criteria.

## Core Patterns

- Event-driven:
  - `WHEN [event] THEN [system] SHALL [response]`
- Conditional:
  - `IF [precondition] THEN [system] SHALL [response]`
- Ongoing state:
  - `WHILE [state] THE SYSTEM SHALL [response]`
- Context-specific:
  - `WHERE [feature context] THE SYSTEM SHALL [response]`
- Optional feature:
  - `WHEN [optional feature is enabled] THEN [system] SHALL [response]`
- Ubiquitous constraint:
  - `THE SYSTEM SHALL [global behavior or constraint]`

## Good Examples

1. `WHEN a signed-in user saves a draft THEN the system SHALL persist the draft without losing existing attachments.`
2. `IF the API returns a timeout THEN the system SHALL show a retryable error state and preserve unsaved form input.`
3. `WHILE a background sync is in progress THE SYSTEM SHALL prevent duplicate sync requests for the same record.`
4. `WHERE the user lacks permission THE SYSTEM SHALL hide destructive actions and reject direct requests with an authorization error.`

## Writing Rules

- Keep one behavior per acceptance criterion.
- Use observable outcomes.
- Name the trigger or condition explicitly.
- Prefer product language over implementation details.
- Split mixed behaviors into separate lines.

## Anti-Patterns

- Avoid vague verbs like `handle`, `support`, or `optimize` without an observable result.
- Avoid bundling multiple outcomes into one criterion.
- Avoid implementation specifics unless they are truly required.
- Avoid acceptance criteria that depend on manual interpretation.
