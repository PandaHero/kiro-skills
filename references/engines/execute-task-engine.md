# Execute Task Engine

Use this engine only when the workflow phase is `execute`.

## Preconditions

- Read `requirements.md`, `design.md`, and `tasks.md` before making changes.
- Confirm tasks are approved.
- Use `sync_task_status.py` to determine or set the single active task.

## Behavior

- Execute exactly one task.
- If a top-level task has subtasks, begin with the first unfinished subtask.
- Verify the implementation against the requirement references attached to that task.
- Do not implement adjacent tasks while working on the active task.
- Once the task is complete, update the checkbox in `tasks.md`, sync execution state, and stop for review.

## If The User Is Just Asking

- If the user asks what the next task is, answer the question and do not start coding automatically.
- If the user asks for task clarification, explain the task without switching into implementation unless they explicitly ask.
