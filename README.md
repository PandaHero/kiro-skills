# Kiro Spec Workflow

Stateful Kiro-inspired spec-driven development workflow for Codex and skills-compatible runtimes.

This skill turns spec work into a real runtime instead of a loose collection of markdown templates. It persists workflow state in `.kiro/specs/<feature-name>/meta.json`, enforces approval gates between phases, and keeps execution limited to one approved task at a time.

## Why This Skill Exists

Most "spec workflow" skills stop at generating `requirements.md`, `design.md`, and `tasks.md`. That reproduces the outer shape of Kiro, but not the part that actually matters: routing into spec mode only when asked, keeping phase state on disk, forcing review before moving forward, and preventing agents from silently chewing through multiple tasks.

This skill focuses on that missing runtime behavior.

## What Makes It Different

- Persisted workflow state in `meta.json`
- Explicit `requirements -> design -> tasks -> execute` phase gates
- Review approval commands instead of implicit phase jumps
- Task lists written as code-agent prompts rather than human PM checklists
- Single active task tracking for execution discipline
- `feature`, `design-first`, and `bugfix` workflow variants

## Install

```bash
npx skills add https://github.com/PandaHero/kiro-skills --skill kiro-spec-workflow
```

## Good Fits

- New features that need requirements, design, and incremental implementation
- Risky refactors where design and task decomposition matter
- Bugfixes that need regression boundaries and unchanged-behavior guards
- Teams that want planning artifacts in the repository instead of in chat history

## Quick Start

Initialize a standard feature workflow:

```bash
python scripts/init_spec.py user-authentication --variant feature
python scripts/detect_state.py .kiro/specs/user-authentication
```

Approve and advance:

```bash
python scripts/approve_phase.py .kiro/specs/user-authentication requirements
python scripts/advance_phase.py .kiro/specs/user-authentication
```

Validate and enter single-task execution:

```bash
python scripts/validate_spec.py .kiro/specs/user-authentication
python scripts/sync_task_status.py .kiro/specs/user-authentication --set-current 2
python scripts/next_task.py .kiro/specs/user-authentication
```

## Example Prompts

- `Use $kiro-spec-workflow to create a feature spec for a login system.`
- `Use $kiro-spec-workflow to turn this bug report into a bugfix workflow.`
- `Use $kiro-spec-workflow to review my existing .kiro/specs/payment-sync state and tell me the next legal phase.`
- `Use $kiro-spec-workflow to execute task 2 from my approved user-authentication spec.`

## Core Runtime Files

- `SKILL.md`: main operating instructions
- `references/state-model.md`: persisted workflow contract
- `references/engines/*.md`: routing and phase engines
- `references/variants/*.md`: variant-specific guidance
- `scripts/spec_runtime.py`: shared workflow helpers
- `scripts/init_spec.py`: initialize spec directories and `meta.json`
- `scripts/detect_state.py`: inspect current phase and next legal action
- `scripts/approve_phase.py`: record explicit review approval
- `scripts/advance_phase.py`: move to the next legal phase
- `scripts/validate_spec.py`: validate docs, approvals, and traceability
- `scripts/sync_task_status.py`: sync `tasks.md` with active-task state
- `scripts/next_task.py`: recommend the next executable task
- `scripts/route_request.py`: heuristic do/spec router

## Positioning

- Unofficial and Kiro-inspired
- Focused on workflow discipline rather than proprietary prompt cloning
- Strongest support is for the standard feature-spec workflow
- `design-first` and `bugfix` are included as lighter variants
