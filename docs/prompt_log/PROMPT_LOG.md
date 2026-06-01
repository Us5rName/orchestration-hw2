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

### Prompt 6a: Phase 4 Agents
**User**: "yes. Remember that the agents must use skills"

**Context**: Build Phase 4 — AgentBase + 3 concrete agents with distinct skills.

**Skills Applied**: sdk-architecture, modular-design, tdd-testing, code-review-config

**Output**:
- AgentBase: abstract base with think(), JSON parsing (6 tests)
- ProAgent: research-analysis skill — evidence, data, citations (4 tests)
- ConAgent: quality-standards skill — critical evaluation, fallacies (4 tests)
- JudgeAgent: persuasiveness scoring, no ties, JSON verdict (5 tests)
- 19 agent tests total, 0 Ruff violations
- New branch: feature/agents

**Key Design**: Distinct skills guarantee real contradiction:
- Pro cites data → Con challenges methodology
- Judge scores persuasion, not facts

---

### Prompt 6: Phase 3 LLM Providers
**User**: "yes" (after branch creation discussion)

**Context**: Build Phase 3 — LLM providers and search service.

**Skills Applied**: sdk-architecture, modular-design, tdd-testing, code-review-config

**Output**:
- LLMProvider: abstract base with chat() interface (6 tests)
- OpenAIProvider: OpenAI SDK, mocked tests (4 tests)
- AnthropicProvider: Anthropic SDK, mocked tests (4 tests)
- GeminiProvider: Google Genai SDK, mocked tests (4 tests)
- SearchService: DuckDuckGo search, no API key (3 tests)
- All providers inherit LLMProvider — zero code duplication
- base_url configurable per provider (Ollama, LM Studio, proxies)
- New branch: feature/llm-providers
- 21 provider tests total, 0 Ruff violations

**Lessons**:
- Mock SDK clients in __init__ by patching before fixture creation
- Patch module-level imports (e.g. genai not Genai for google-genai)

---

### Prompt 6b: Phase 2 Shared Infrastructure
**User**: "go on. remember to read the skills curefully (They are requirements) and make short readable commits"

**Context**: Build Phase 2 — ConfigManager, LogManager, ApiGatekeeper, Watchdog.

**Skills Applied**: tdd-testing, api-gatekeeper, modular-design, code-review-config, project-setup, version-control

**Output**:
- ConfigManager: JSON config loader with version access (9 tests)
- LogManager: FIFO line-based rotation (5 tests)
- ApiGatekeeper: rate limiting, retries, queue status (7 tests)
- Watchdog: keep-alive ping, on-death callback (4 tests)
- 25 total tests, 0 Ruff violations
- New branch: feature/shared-infrastructure

**Lessons**:
- Skill says "meaningful messages" — nothing about conventional commit format
- Small commits = one logical unit per commit
- Create matching branches per phase

---

## Best Practices Established

1. Plan before code — PRD → PLAN → TODO → approval → implement
2. Feature branches — one per phase
3. Meaningful commits — what changed and why
4. Prompt log — document AI-assisted decisions
5. TDD cycle — RED (test) → GREEN (impl) → REFACTOR (ruff) → commit
