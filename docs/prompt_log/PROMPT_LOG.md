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

### Prompt 7: Phase 5 Services
**User**: "start phase 5. Go over docs. Use the relevant skills when working. Remember they are not recommendations, but requirements"

**Context**: Build Phase 5 — DebateState and DebateOrchestrator services.

**Skills Applied**: modular-design, sdk-architecture, tdd-testing, code-review-config, project-setup, version-control

**Output**:
- DebateState: dataclass tracking topic, rounds, history, scores, winner (13 tests)
- DebateOrchestrator: coordinates debate rounds with pro/con turns (8 tests)
- PromptBuilder: constructs prompts for pro, con, and judge agents
- Verdict: judge evaluation and result formatting
- Per-algorithm PRD: PRD_debate_orchestration.md
- Updated PLAN.md with new modules in project structure and Key Classes
- Updated TODO.md marking Phase 5 complete
- New branch: feature/services
- 21 service tests total, 0 Ruff violations

**Key Design**:
- Semantic splits to respect 150-line rule (blank/comment lines excluded)
- Orchestrator (119 lines) focuses on round flow
- PromptBuilder (100 lines) handles prompt construction
- Verdict (57 lines) handles judge evaluation and result formatting
- DebateState as dataclass — simple, immutable-friendly state tracking

**Lessons**:
- Plan splits BEFORE writing code — initial orchestrator was 186 lines
- Extract by concern: round execution vs prompt building vs verdict
- Per-algorithm PRDs are required by project-setup skill — don't skip
- Update PLAN.md project structure when adding new files
- Prompt log is a requirement, not optional

---

### Prompt 8: Phase 6 SDK & CLI
**User**: "Start phase 6. in addition to the skills, use the information from the prompt log"

**Context**: Build Phase 6 — DebateSDK, TerminalMenu, main.py entry point.

**Skills Applied**: sdk-architecture, modular-design, tdd-testing, code-review-config, project-setup, version-control

**Output**:
- DebateSDK: single entry point wiring all components (140 lines, 5 tests)
- ProviderFactory: creates LLM providers from config (59 lines, 6 tests)
- TerminalMenu: CLI menu with start debate, view logs, configure, exit (63 lines)
- main.py: updated entry point creating SDK and launching menu (19 lines)
- Updated PLAN.md with SDK/CLI modules
- Updated TODO.md marking Phase 6 complete
- New branch: feature/sdk-cli
- 11 SDK tests total, 0 Ruff violations

**Key Design**:
- SDK is the single entry point — all business logic flows through it
- CLI is a thin presentation layer that delegates to SDK (no business logic)
- ProviderFactory reads API keys from environment variables
- SDK loads config, creates providers, agents, orchestrator
- Prompt log lessons applied: plan splits BEFORE writing code

**Lessons**:
- Mock provider classes in tests (real providers need API keys)
- Use `@patch` on module-level imports for provider factories
- SDK should not exceed 150 lines — extract provider factory early
- TerminalMenu delegates ALL logic to SDK per sdk-architecture skill

---

### Prompt 9: Phase 7 Tests
**User**: "now do it for phase 7"

**Context**: Build Phase 7 — comprehensive test coverage to reach ≥85%.

**Skills Applied**: tdd-testing, code-review-config, project-setup, version-control

**Output**:
- test_version.py: version constants (2 tests)
- test_constants.py: all project constants (4 tests)
- test_config_validator.py: config validation (5 tests)
- test_prompt_builder.py: prompt building functions (7 tests)
- test_verdict.py: verdict functions (3 tests)
- test_menu.py: CLI menu with mocked input (4 tests)
- test_orchestrator.py: added run() and round_number override tests
- test_sdk.py: added get_logs with file test
- test_debate_flow.py: integration test for full debate (3 tests)
- Coverage: 96% (up from 76%, target was 85%)
- 128 total tests, 0 Ruff violations
- New branch: feature/tests

**Key Design**:
- Tests mirror src/ structure (tests/unit/test_<module>/)
- All external dependencies mocked (API keys, file I/O, user input)
- Integration test verifies end-to-end debate flow
- Coverage report shows 96% — well above 85% requirement

**Lessons**:
- Use `side_effect=SystemExit(1)` to mock sys.exit properly
- Combine nested `with` statements to satisfy SIM117
- Use `pytest.raises` for tests that trigger SystemExit
- Mock `builtins.input` for CLI tests
- Coverage gaps are usually in newly added modules

---

### Prompt 10: Fix Timeout Disconnect
**User**: "Looking at the grep results, `timeout` flows through the codebase but there's a disconnect — the config value reaches the agents but isn't actually used for API calls."

**Context**: Previous agent identified that `ProviderFactory` creates providers with hardcoded `timeout=60` instead of using the configured `request_timeout_seconds` from `setup.json`.

**Skills Applied**: code-review-config, tdd-testing, version-control

**Output**:
- Fixed `sdk.py` to read timeout BEFORE creating provider and inject it into provider config
- Added 8 config propagation tests split into 3 semantic files
- Tests verify timeout, model, temperature, base_url, topic all reach their destinations
- Coverage: 96%, 136 total tests, 0 Ruff violations

**Key Design**:
- Config values must flow through the entire chain, not stop at agents
- ProviderFactory reads `timeout` from config dict — SDK must inject it
- Tests split semantically: timeout propagation, agent→provider, agent→agent

**Lessons**:
- Always verify config values reach their final destination, not just intermediate stops
- Use `mock_factory.call_args` to capture what was passed to mocked functions
- Extract shared test fixtures to `conftest.py` to avoid duplication

---

### Prompt 11: Enhance Debate Logging
**User**: "the logs don't give information. please fix it. the logs must include number of tool calls per response and the responses themselves, in addition to the decisions of the judge."

**Context**: SDK only logged "DebateSDK initialized", "Debate started", "Debate complete". No round-level detail, no agent responses, no judge decisions.

**Skills Applied**: modular-design, project-setup, version-control

**Output**:
- Created `orchestrator_logging.py` — dedicated module for debate event logging
- Orchestrator now logs: round progress, full agent responses, references, judge verdict with scores and justification
- SDK wires its LogManager to the orchestrator
- Split orchestrator semantically: core coordination vs logging concern

**Key Design**:
- Logging as separate module with pure functions taking logger as parameter
- No truncation — full responses and justifications logged
- Logger is optional — no-op when not provided (backwards compatible)

**Lessons**:
- Split semantically by concern, not just by line count
- Logging is a cross-cutting concern that deserves its own module
- Pure functions for logging make it independently testable and swappable

---

## Best Practices Established

1. Plan before code — PRD → PLAN → TODO → approval → implement
2. Feature branches — one per phase
3. Meaningful commits — what changed and why
4. Prompt log — document AI-assisted decisions
5. TDD cycle — RED (test) → GREEN (impl) → REFACTOR (ruff) → commit
