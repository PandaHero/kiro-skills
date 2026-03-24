# Kiro Spec Workflow

Unofficial Codex skill that adapts a Kiro-style spec workflow into a reusable package. This version is stateful: it persists workflow phase, approvals, and active task selection in `.kiro/specs/<feature-name>/meta.json` instead of treating the skill as a static template set.

## What Changed In V2

- Added a persisted workflow state model
- Added explicit approval and phase-advance commands
- Added request routing heuristics
- Split behavior into phase-specific engine documents
- Added single-task execution state tracking
- Added `feature`, `design-first`, and `bugfix` variants

## Runtime Files

- `SKILL.md`: main workflow instructions
- `agents/openai.yaml`: UI metadata
- `references/state-model.md`: persisted workflow contract
- `references/engines/*.md`: routing and phase engines
- `references/variants/*.md`: variant-specific guidance
- `scripts/spec_runtime.py`: shared workflow helpers
- `scripts/init_spec.py`: initialize spec directories and `meta.json`
- `scripts/detect_state.py`: inspect current phase and next action
- `scripts/approve_phase.py`: record explicit review approval
- `scripts/advance_phase.py`: move to the next legal phase
- `scripts/validate_spec.py`: validate docs, approvals, and traceability
- `scripts/sync_task_status.py`: sync `tasks.md` with the active task state
- `scripts/next_task.py`: recommend the next executable task
- `scripts/route_request.py`: heuristic do/spec router

## Typical Flow

```bash
python scripts/init_spec.py user-authentication --variant feature
python scripts/detect_state.py .kiro/specs/user-authentication
python scripts/approve_phase.py .kiro/specs/user-authentication requirements
python scripts/advance_phase.py .kiro/specs/user-authentication
python scripts/validate_spec.py .kiro/specs/user-authentication
python scripts/sync_task_status.py .kiro/specs/user-authentication --set-current 2
```

## Publish And Install

Install from GitHub with:

```bash
npx skills add https://github.com/PandaHero/kiro-skills --skill kiro-spec-workflow
```

## Notes

- This package is unofficial and Kiro-inspired.
- It reproduces workflow discipline, not proprietary internal prompts verbatim.
- The primary supported path is the feature-spec workflow, with lighter support for `design-first` and `bugfix`.
