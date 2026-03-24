# Kiro Spec Workflow

Unofficial Codex skill that adapts a Kiro-style spec workflow into a reusable package. It keeps the core planning discipline intact: requirements, then design, then tasks, then one approved task at a time during execution.

## What It Includes

- `SKILL.md`: operational instructions for the skill
- `agents/openai.yaml`: UI metadata for skills-compatible hosts
- `references/`: workflow rules, EARS guidance, and document templates
- `scripts/init_spec.py`: create `.kiro/specs/<feature-name>/` from templates
- `scripts/validate_spec.py`: validate spec structure and traceability
- `scripts/next_task.py`: recommend the next executable task

## Directory Layout

```text
kiro-spec-workflow/
|- SKILL.md
|- README.md
|- agents/
|  `- openai.yaml
|- references/
|  |- workflow-rules.md
|  |- ears-patterns.md
|  |- requirements-template.md
|  |- design-template.md
|  `- tasks-template.md
`- scripts/
   |- init_spec.py
   |- validate_spec.py
   `- next_task.py
```

## Local Use

```bash
python scripts/init_spec.py user-authentication
python scripts/validate_spec.py .kiro/specs/user-authentication
python scripts/next_task.py .kiro/specs/user-authentication/tasks.md
```

## Publish As A Public Skill

1. Make this folder the root of a public GitHub repository.
2. Push the repository.
3. Install it with:

```bash
npx skills add https://github.com/<owner>/<repo> --skill kiro-spec-workflow
```

## Notes

- This package is unofficial and Kiro-inspired.
- It is designed around the standard feature-spec flow.
- It does not include proprietary Kiro prompts verbatim.
