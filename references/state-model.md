# State Model

The workflow is persisted in `.kiro/specs/<feature-name>/meta.json`.

## Core Fields

- `schema_version`: Current runtime schema version
- `feature_name`: Kebab-case feature directory name
- `feature_title`: Human-readable title
- `variant`: `feature`, `design-first`, or `bugfix`
- `phase`: Current workflow phase
- `approvals`: Per-document approval flags
- `docs`: Document file names for this variant
- `execution.current_task`: The only task that may be actively executed
- `execution.last_completed_task`: Most recently finished task
- `execution.pending_tasks`: Pending task numbers from `tasks.md`
- `execution.completed_tasks`: Completed task numbers from `tasks.md`
- `history`: Timestamped workflow events

## Variant Phase Orders

- `feature`: `requirements -> design -> tasks -> execute -> completed`
- `design-first`: `design -> tasks -> execute -> completed`
- `bugfix`: `bugfix -> design -> tasks -> execute -> completed`

## Invariants

- A phase may advance only when its document exists and has explicit approval.
- `execute` may begin only after `tasks` is approved.
- Only one task may be marked as active in `execution.current_task`.
- If a selected task has unfinished subtasks, the first unfinished subtask becomes the active task.
- The workflow may move backward when design or task planning reveals gaps in an earlier document.

## Review Prompts

- Requirements: `Do the requirements look good? If so, we can move on to the design.`
- Bugfix: `Does the bugfix analysis look good? If so, we can move on to the design.`
- Design: `Does the design look good? If so, we can move on to the implementation plan.`
- Tasks: `Do the tasks look good?`
