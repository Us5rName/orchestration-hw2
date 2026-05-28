# Prompt Engineering Log

## Session 1 — Planning Phase (2026-05-28)

### Prompt 1: Initial Request
**User**: "implement the program. another requirement: llm provider agnostic. NOTE: I am the one dictating the pace of your development"

**Context**: University assignment — AI debate system with 3 agents (Judge, Pro, Con). Full requirements provided in Hebrew.

**Output**: Created PRD.md, PLAN.md, TODO.md with full architecture.

**Best Practice**: Always create planning docs before coding when project-setup skill is active.

---

### Prompt 2: Architecture Clarification
**User**: "Does the judge spawn the debaters?"

**Context**: Clarifying the agent hierarchy — who creates whom.

**Output**: Explained two options (Judge spawns vs Orchestrator spawns), recommended separate orchestrator for infra concerns.

**Improvement**: User pushed back — clarified that Judge spawns children, Orchestrator handles infra only.

---

### Prompt 3: Homework Requirement
**User**: "It says in the homework that the father should decide who wins"

**Context**: Confirming Judge's role matches homework requirements.

**Output**: Mapped homework requirements to design decisions.

---

### Prompt 4: Version Control Commit
**User**: "Commit the changes" + attached version-control skill

**Context**: Commit planning documents following version-control skill.

**Output**: Committed to master (mistake), then fixed by creating feature branch.

**Improvement**: Should have created feature branch first. Added prompt log retroactively.

---

---

### Prompt 5: Phase 1 Foundation
**User**: "go ahead. Remember to use the skills on demand when relevant. The instructions of the skills are requirements, not recommendations"

**Context**: Build Phase 1 — project structure, config files, dependencies.

**Skills Applied**: version-control, code-review-config, package-organization, project-setup

**Output**:
- pyproject.toml with Ruff, pytest, coverage config
- .env-example with API key placeholders
- 3 config files (setup.json, rate_limits.json, logging_config.json) — all v1.00
- Full src/debate/ package structure with __init__.py files
- uv.lock with 47 locked packages
- Ruff: 0 violations

**Best Practice**: Always run `uv lock`, `uv sync`, and `ruff check` before committing.

---

## Best Practices Established

1. **Plan before code** — PRD → PLAN → TODO → approval → implement
2. **Feature branches** — never commit directly to master
3. **Meaningful commits** — describe what changed and why
4. **Prompt log** — document AI-assisted decisions for traceability
