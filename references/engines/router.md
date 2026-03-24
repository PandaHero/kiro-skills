# Router Engine

Use this engine to decide whether the skill should engage the spec workflow at all.

## Rules

- Default to normal implementation mode unless the user explicitly asks for a formal spec, requirements document, design document, implementation plan, or spec task execution.
- Treat requests to start, execute, continue, or inspect a spec task as spec workflow requests.
- When in doubt, classify as normal implementation mode rather than spec mode.

## Runtime

- Use `python scripts/route_request.py "<user request>"` when routing is ambiguous.
- If the request is about an existing spec, resolve the feature directory first.
- If the request is an ordinary coding task, do not force this workflow on the user.
