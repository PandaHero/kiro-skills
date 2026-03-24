---
name: kiro-spec-workflow
description: "Use when the user explicitly wants a Kiro-style spec workflow: create or revise repo-persisted requirements, design, and task docs before implementation, or execute exactly one approved task from an existing spec."
---

# Kiro Spec Workflow

## Overview

Use this skill when the user explicitly wants spec-driven development rather than immediate implementation. This version treats the workflow as persisted runtime state in `.kiro/specs/<feature-name>/meta.json`, with explicit phase gates, review checkpoints, and one-task-at-a-time execution.

## Core Principle

Kiro's useful behavior is not the existence of three markdown files. The useful behavior is:

- explicit routing into spec mode only when requested
- repo-persisted workflow state
- strict document approval gates
- task lists written for a coding agent rather than a human project tracker
- single-task execution with an enforced stop for review

Follow those behaviors exactly.

## Step 1: Route The Request

- Default to ordinary implementation mode unless the user explicitly asks for a spec, requirements document, design document, implementation plan, or execution of a spec task.
- Use `references/engines/router.md` when routing is ambiguous.
- Optionally run:

```bash
python scripts/route_request.py "<user request>"
```

## Step 2: Resolve Or Create Workflow State

- Every spec lives in `.kiro/specs/<feature-name>/`.
- Every active workflow must have `.kiro/specs/<feature-name>/meta.json`.
- If the user is starting fresh, initialize the workflow with:

```bash
python scripts/init_spec.py <feature-name> --variant feature
```

- Supported variants:
  - `feature`
  - `design-first`
  - `bugfix`
- If the user is working on an existing spec, inspect state with:

```bash
python scripts/detect_state.py .kiro/specs/<feature-name> --json
```

## Step 3: Obey The Current Phase Engine

Read the engine that matches `meta.json.phase` and behave according to it.

- `requirements`: `references/engines/requirements-engine.md`
- `bugfix`: `references/variants/bugfix-workflow.md`
- `design`: `references/engines/design-engine.md`
- `tasks`: `references/engines/tasks-engine.md`
- `execute`: `references/engines/execute-task-engine.md`

Do not blend phases together. If the workflow is in `requirements`, do not produce design. If it is in `tasks`, do not start implementing.

## Step 4: Enforce Review Gates

After every edit to a reviewable document:

- ask for explicit approval
- do not assume implicit approval
- do not move forward until approval is explicit

Use these exact review prompts:

- Requirements: `Do the requirements look good? If so, we can move on to the design.`
- Bugfix: `Does the bugfix analysis look good? If so, we can move on to the design.`
- Design: `Does the design look good? If so, we can move on to the implementation plan.`
- Tasks: `Do the tasks look good?`

When approval is received:

```bash
python scripts/approve_phase.py .kiro/specs/<feature-name> <phase>
python scripts/advance_phase.py .kiro/specs/<feature-name>
python scripts/detect_state.py .kiro/specs/<feature-name>
```

If a later phase reveals missing information in an earlier document, move backward instead of improvising around the gap.

## Step 5: Keep Traceability Intact

- Use EARS acceptance criteria for feature requirements and bugfix acceptance criteria.
- Tasks must reference granular acceptance-criteria IDs such as `1.2`.
- Tasks are prompts for a coding agent, not general project-management bullets.
- Keep implementation details in `design.md` and execution steps in `tasks.md`.
- Validate mature specs with:

```bash
python scripts/validate_spec.py .kiro/specs/<feature-name>
```

## Step 6: Execute Exactly One Task

When phase is `execute`:

- read the spec documents first
- use `sync_task_status.py` to determine the active task
- execute exactly one task
- if a requested top-level task has subtasks, begin with the first unfinished subtask
- after implementation, update `tasks.md`, sync state, and stop

Useful commands:

```bash
python scripts/sync_task_status.py .kiro/specs/<feature-name> --set-current 2
python scripts/next_task.py .kiro/specs/<feature-name>
python scripts/sync_task_status.py .kiro/specs/<feature-name>
```

Do not continue to the next task automatically.

## Variant Notes

- `feature`: standard `requirements -> design -> tasks -> execute`
- `design-first`: use when architecture is the main unknown and product behavior is already constrained
- `bugfix`: start with bug reproduction, regression boundaries, and unchanged behavior before design

See:

- `references/variants/design-first-workflow.md`
- `references/variants/bugfix-workflow.md`
- `references/state-model.md`

## Bundled Resources

- `scripts/spec_runtime.py`: shared workflow runtime
- `scripts/route_request.py`: heuristic do/spec router
- `scripts/init_spec.py`: initialize a spec directory and `meta.json`
- `scripts/detect_state.py`: inspect current workflow state
- `scripts/approve_phase.py`: record explicit approval
- `scripts/advance_phase.py`: move to the next legal phase
- `scripts/validate_spec.py`: validate docs plus workflow state
- `scripts/sync_task_status.py`: keep execution state aligned with `tasks.md`
- `scripts/next_task.py`: recommend the next executable task
- `references/engines/*.md`: phase-specific operating rules
- `references/*.md`: templates and traceability references
