# Directory Submission Copy

## Title

Kiro Spec Workflow

## Short Description

Stateful Kiro-style workflow for requirements, design, tasks, and one-task-at-a-time execution.

## Long Description

Kiro Spec Workflow is a Kiro-inspired skill for Codex and other skills-compatible runtimes. It turns spec-driven development into a persisted workflow instead of a loose set of markdown templates. The skill stores workflow phase, approvals, and active-task state in `.kiro/specs/<feature-name>/meta.json`, then enforces explicit gates between requirements, design, tasks, and execution.

It is designed for users who want repository-backed planning artifacts, strict review checkpoints, and incremental execution discipline. It also includes `feature`, `design-first`, and `bugfix` variants.

## Suggested Categories

- Development
- Productivity
- Planning

## Suggested Tags

- specs
- requirements
- design
- tasks
- workflow
- bugfix
- design-first
- coding-agent

## Key Selling Points

- Persists workflow state on disk instead of hiding it in chat
- Enforces explicit approval before phase transitions
- Writes task plans as prompts for a coding agent
- Tracks a single active task during execution
- Supports feature, bugfix, and design-first modes

## Install Command

```bash
npx skills add https://github.com/PandaHero/kiro-skills --skill kiro-spec-workflow
```

## Repository

https://github.com/PandaHero/kiro-skills

## Example Prompts

- `Use $kiro-spec-workflow to create a feature spec for a login system.`
- `Use $kiro-spec-workflow to turn this bug report into a bugfix workflow.`
- `Use $kiro-spec-workflow to tell me the next phase for .kiro/specs/payment-sync.`
- `Use $kiro-spec-workflow to execute task 2 from my approved spec.`

## Notes

- Unofficial and Kiro-inspired
- Reproduces workflow discipline, not proprietary internal prompts verbatim
