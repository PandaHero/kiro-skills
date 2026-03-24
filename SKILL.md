---
name: kiro-spec-workflow
description: "Use when the user explicitly wants a Kiro-style spec workflow: create or revise repo-persisted requirements, design, and task docs before implementation, or execute exactly one approved task from an existing spec."
---

# Kiro Spec Workflow

## Overview

Use this skill when the user wants formal, repo-persisted planning artifacts instead of jumping straight into implementation. It adapts the public Kiro-style flow into Codex: requirements, then design, then task planning, with explicit approval gates and one-task-at-a-time execution.

## When To Use

Use this skill when the user explicitly asks to:

- create a spec or specification
- draft formal requirements, design, or implementation plan documents
- work in `.kiro/specs/<feature-name>/`
- revise an existing spec
- execute a specific task from an approved spec

Do not use this skill as the default for ordinary coding requests. If the user is asking to build or fix something directly and does not explicitly want spec work, stay in normal implementation mode.

## Routing Rules

- Default to normal implementation mode unless the user explicitly asks for spec work.
- Derive a short kebab-case feature name for the spec directory.
- Persist artifacts in `.kiro/specs/<feature-name>/`.
- Treat requirements, design, and tasks as separate approval gates.
- Do not combine multiple phases into one interaction.
- If the user asks to execute a task, always read the full spec first.

## Workflow

### 1. Requirements

- Create `.kiro/specs/<feature-name>/requirements.md` if it does not exist.
- Generate the first draft immediately from the user's rough idea. Do not begin with a chain of clarification questions.
- Use `references/requirements-template.md` as the base structure.
- Structure each requirement as:
  - `### Requirement N`
  - `**User Story:** As a ..., I want ..., so that ...`
  - `#### Acceptance Criteria`
  - numbered EARS statements
- Consider edge cases, UX constraints, failure cases, and success criteria in the first draft.
- After each revision, ask for explicit approval before continuing to design.

### 2. Design

- Only begin after requirements are explicitly approved.
- Read the requirements before designing.
- Research gaps in-thread when needed. Keep research in the conversation, not in a separate research file.
- Create `.kiro/specs/<feature-name>/design.md` using `references/design-template.md`.
- Cover every approved requirement and include:
  - Overview
  - Architecture
  - Components and Interfaces
  - Data Models
  - Error Handling
  - Testing Strategy
- Use Mermaid diagrams when they add clarity.
- After each revision, ask for explicit approval before continuing to tasks.

### 3. Tasks

- Only begin after design is explicitly approved.
- Read both requirements and design first.
- Create `.kiro/specs/<feature-name>/tasks.md` using `references/tasks-template.md`.
- Convert the design into a series of prompts for a coding agent:
  - incremental
  - test-aware
  - no large jumps in complexity
  - each step builds on earlier work
  - final steps wire the system together
- Each task must:
  - be a numbered checkbox
  - stay within at most two levels of hierarchy
  - focus only on writing, modifying, or testing code
  - include `Files/Components`
  - include `Requirements` that reference granular acceptance-criteria IDs such as `1.1` or `2.3`
- Exclude non-coding work such as deployment, manual UAT, performance data collection, business rollout, training, marketing, or documentation-only tasks.
- After each revision, ask for explicit approval and stop when the task plan is approved.

### 4. Execute One Task

When the user asks to execute a task from an existing spec:

- Always read `requirements.md`, `design.md`, and `tasks.md` first.
- If the requested task has subtasks, start with the first relevant subtask.
- Execute exactly one task.
- Do not start the next task automatically.
- After finishing, stop and let the user review.
- If the user asks what to do next, use `scripts/next_task.py` to recommend the next pending task.

## Quality Rules

- Maintain traceability from tasks back to granular requirement IDs.
- Do not assume missing requirements. Ask targeted questions only after the initial draft exists.
- If gaps appear during design or task planning, move back to the earlier phase instead of papering over them.
- Keep implementation details in `design.md` and execution steps in `tasks.md`.
- Prefer `scripts/validate_spec.py` before asking for approval or before executing a task from a mature spec.

## Bundled Resources

- `references/workflow-rules.md`: distilled workflow rules and guardrails
- `references/ears-patterns.md`: quick EARS reference and examples
- `references/requirements-template.md`: starter template for requirements docs
- `references/design-template.md`: starter template for design docs
- `references/tasks-template.md`: starter template for implementation plans
- `scripts/init_spec.py`: scaffold a new `.kiro/specs/<feature-name>/` directory
- `scripts/validate_spec.py`: validate structure, EARS coverage, task formatting, and traceability
- `scripts/next_task.py`: recommend the next executable task from `tasks.md`

## Quick Commands

```bash
python scripts/init_spec.py user-authentication
python scripts/validate_spec.py .kiro/specs/user-authentication
python scripts/next_task.py .kiro/specs/user-authentication/tasks.md
```
