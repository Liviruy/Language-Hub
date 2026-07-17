# AI Agent Rules

## Workflow

Each phase follows this strict cycle:

1. Agent reads docs -> understands scope
2. Agent presents design plan
3. Human reviews and approves
4. Agent implements (code + tests)
5. Agent runs validation
6. Agent commits
7. Human verifies
8. Move to next phase

## Do NOT

- Generate the entire project at once
- Skip human approval between phases
- Add unnecessary complexity
- Introduce vendor lock-in
- Hard-code paths
- Skip validation or testing
- Regenerate stable IDs (Anki GUID, audio)

## Do

- Read PROJECT_PLAN.md, ARCHITECTURE.md, DATABASE.md, ROADMAP.md for context
- Output a design review before coding
- Each phase must run successfully before moving on
- Write unit tests
- Use type hints and docstrings
- Use logging
- Commit after each validated phase
- Prefer maintainability over cleverness

## Validation

Every phase must: run without errors, pass tests, be committed, be verified by human.
