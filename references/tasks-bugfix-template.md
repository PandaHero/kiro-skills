# Implementation Plan

## Planning Rules

- Keep the plan focused on writing, modifying, or testing code.
- Use a numbered checkbox list with at most two levels of hierarchy.
- Keep the fix incremental and regression-driven.
- Reference granular acceptance-criteria IDs in every executable task.
- Execution happens one task at a time.

## Tasks

- [ ] 1. Reproduce the bug with an automated failing test
  - Files/Components: `src/...`, `tests/...`
  - Requirements: 1.1, 1.3
  - Notes: Capture the broken behavior before changing implementation.

- [ ] 2. Implement the smallest safe fix
  - [ ] 2.1 Isolate and update the failing code path
    - Files/Components: `src/...`, `tests/...`
    - Requirements: 1.1, 1.2
  - [ ] 2.2 Add regression guards for unchanged behavior
    - Files/Components: `src/...`, `tests/...`
    - Requirements: 1.3

- [ ] 3. Tighten regression coverage around adjacent edge cases
  - Files/Components: `src/...`, `tests/...`
  - Requirements: 1.2, 1.3
