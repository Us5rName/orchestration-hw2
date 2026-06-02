# TODO — AI Debate System

## Phase 1: Foundation
- [x] Create PRD.md
- [x] Create PLAN.md
- [x] Create TODO.md
- [x] Create pyproject.toml with dependencies
- [x] Create .env-example
- [x] Create .gitignore
- [x] Create config/setup.json
- [x] Create config/rate_limits.json
- [x] Create config/logging_config.json

## Phase 2: Shared Infrastructure
- [x] ConfigManager — load and validate config
- [x] LogManager — structured logging with FIFO rotation
- [x] ApiGatekeeper — rate limiting, queuing, retries
- [x] Watchdog — process monitoring and keep-alive
- [x] Constants — immutable project constants

## Phase 3: LLM Providers
- [x] ILLMProvider — abstract base interface
- [x] OpenAIProvider — OpenAI API implementation
- [x] AnthropicProvider — Anthropic API implementation
- [x] GeminiProvider — Google Gemini API implementation
- [x] SearchService — DuckDuckGo search abstraction

## Phase 4: Agents
- [x] AgentBase — abstract base agent class
- [x] JudgeAgent — judge/mediator agent
- [x] ProAgent — pro-side debater
- [x] ConAgent — con-side debater

## Phase 5: Services
- [x] DebateState — debate state tracking
- [x] DebateOrchestrator — manages debate flow

## Phase 6: SDK & CLI
- [x] DebateSDK — single entry point
- [x] ProviderFactory — creates providers from config
- [x] TerminalMenu — CLI menu interface
- [x] main.py — entry point

## Phase 7: Tests (TDD)
- [x] Unit tests for ConfigManager
- [x] Unit tests for LogManager
- [x] Unit tests for ApiGatekeeper
- [x] Unit tests for Watchdog
- [x] Unit tests for LLM providers
- [x] Unit tests for agents
- [x] Unit tests for DebateOrchestrator
- [x] Unit tests for DebateSDK
- [x] Unit tests for version, constants, config_validator
- [x] Unit tests for prompt_builder, verdict, CLI menu
- [x] Integration test for full debate flow
- [x] Verify ≥85% coverage (96% achieved)

## Phase 8: Agent Skills
- [x] Create `docs/PRD_agent_skills.md`
- [x] `AgentSkill` abstract base class (`src/debate/skills/base_skill.py`)
- [x] `ResearchAnalysisSkill` — evidence, data, citations; wraps `SearchService` for live search (`skills/research_analysis.py`)
- [x] `QualityStandardsSkill` — fallacies, methodology, rigor (`skills/quality_standards.py`)
- [x] `PersuasionScoringSkill` — persuasiveness scoring, no ties (`skills/persuasion_scoring.py`)
- [x] `SkillRegistry` + `default_registry()` factory (`skills/registry.py`)
- [x] `skills/__init__.py` — export public API
- [x] Update `config/setup.json` — add `"skills": [...]` list per agent
- [x] Update `ConfigValidator` — validate `skills` list per agent config
- [x] Update `AgentBase` — accept `skills: list[AgentSkill]`; add `_build_skill_block()` and tool executor
- [x] Update `JudgeAgent`, `ProAgent`, `ConAgent` — call `_build_skill_block()` in system prompt
- [x] Update `DebateSDK` — resolve skills from registry and inject into agents
- [x] Unit tests: `test_skills/test_base_skill.py`
- [x] Unit tests: `test_skills/test_skills.py` (all 3 concrete skills)
- [x] Unit tests: `test_skills/test_registry.py`
- [x] Update `test_agents/test_base_agent.py` — test skill composition
- [x] Update `test_sdk/test_sdk.py` — test skill wiring through SDK
- [x] Update `test_shared/test_config_validator.py` — test skills key validation and role-skill compatibility
- [x] Verify ≥85% coverage maintained (174 tests, all passing)
- [x] 0 Ruff violations

## Phase 9: Documentation & Polish
- [x] README.md with screenshots
- [x] Ruff check — zero violations
- [x] Full debate session test
- [x] Final checklist review

## Phase 10: Usage & Cost Tracking
- [x] `UsageRecord` dataclass + `build_from_delta()` factory (`services/usage_record.py`)
- [x] `_record_usage()` / `_record_unavailable_usage()` accumulator helpers in `base_provider.py`
- [x] Match/case usage extraction for OpenAI, Anthropic, Gemini (dict + typed-object + None branches)
- [x] `CostCalculator` — pure math module: `cost_for_record`, `summarize_round`, `summarize_debate`
- [x] Pricing config in `config/setup.json` — per-role input/output rates, per_1m_tokens unit
- [x] `validate_pricing()` in `config_validator.py` — catches missing/invalid pricing at startup
- [x] `orchestrator_logging.py` — `log_round_cost` and `log_debate_cost` helpers
- [x] `DebateOrchestrator` — delta-snapshot per agent turn, per-round cost log, debate cost summary
- [x] `DebateSDK` — propagates `pricing` config to orchestrator
- [x] Tests: `test_usage_record.py`, `test_cost_calculator.py` (new)
- [x] Tests: usage branch coverage for all 3 provider test files
- [x] Tests: pricing validation tests in `test_config_validator.py`
- [x] Tests: cost_summary assertions in `test_orchestrator.py`
- [x] 230 tests passing · 99% coverage · 0 Ruff violations
- [x] README updated with automatic cost tracking documentation

## Phase 11 — Architecture Refactor and Test Consolidation

### Branch 1 — test/refactor-harness-and-duplicates
- [ ] Build reliable typed fakes for providers and agents (replace MagicMock-heavy tests)
- [ ] Consolidate duplicated provider tests into contract-style tests where possible
- [ ] Split test files that exceed the 150-line limit into focused units
- [ ] Replace direct abstract-class instantiation tests with `inspect`-based abstractness tests
- [ ] Keep or improve meaningful coverage; do not delete tests just to reduce count

### Branch 2 — refactor/typed-config-sdk-boundary
- [ ] Introduce typed config section dataclasses or models (DebateConfig, AgentConfig, GatekeeperConfig, etc.)
- [ ] Make `ConfigManager` expose typed accessors in addition to raw `get()`
- [ ] Type the `DebateSDK` public boundary (no `object` parameters)
- [ ] Type the CLI/menu boundary — accept a concrete `DebateSDK` or narrow `Protocol`
- [ ] Type agents: replace `provider: object` with `provider: LLMProvider`
- [ ] Type the logger boundary consistently (`LogManager | None` throughout)

### Branch 3 — refactor/provider-result-contract
- [ ] Define an internal `ProviderResult` datatype (response text + usage metadata)
- [ ] Make `OpenAIProvider`, `AnthropicProvider`, and `GeminiProvider` return `ProviderResult`
- [ ] Centralise usage extraction — no usage-parsing logic outside provider adapters
- [ ] Keep vendor-specific SDK details isolated inside each provider's `_chat()` method
- [ ] Add `UsageSnapshot` or equivalent so delta tracking does not depend on mutable state

### Branch 4 — refactor/structured-agent-outputs
- [ ] Define internal schemas for debate messages, agent responses, judge decisions, and debate results
- [ ] Validate all agent outputs against schema on receipt
- [ ] Reject and raise on invalid JSON, invalid winner value, tie decisions, missing required fields
- [ ] Ensure the orchestrator never continues with a malformed agent response

### Branch 5 — refactor/parent-controlled-state-machine
- [ ] Make the father/judge as sole communication router explicit in code, not just docs
- [ ] Ensure `ProAgent` and `ConAgent` have no direct references to each other
- [ ] Add explicit `DebatePolicy` (or equivalent) for round rules, tie prevention, and winner validation
- [ ] Add tests that assert no direct child-to-child communication path exists
- [ ] Add tests for parent routing and no-tie enforcement at the orchestrator boundary
- [ ] Log every important debate state transition (round start, argument received, verdict issued)

### Branch 6 — refactor/gatekeeper-watchdog-real-use
- [ ] Audit whether `ApiGatekeeper` is in the real provider call path (not just instantiated)
- [ ] Audit whether `Watchdog` is called during the real debate loop (not just constructed)
- [ ] If decorative: wire `ApiGatekeeper` into provider calls and `Watchdog` into the debate loop, OR document clearly as future work in PLAN.md
- [ ] Add tests that verify rate-limiting fires when requests-per-minute is exceeded
- [ ] Add a test that verifies the watchdog ping is called during `orchestrator.run()`

### Branch 7 — docs/skills-canonicalization
- [ ] Clarify canonical skill locations: runtime debate-agent skills vs Claude Code development-time skills
- [ ] Verify whether `.claude/skills/` exists locally and document or remove the ambiguity
- [ ] If duplicate skill directories exist, establish one source of truth and remove or archive the other
- [ ] Update `docs/PRD_agent_skills.md` to reflect the final canonical location

### Branch 8 — chore/logs-cleanup-verification
- [ ] Verify no runtime log files are tracked in git (`git status` and `git ls-files logs/`)
- [ ] Verify `.gitignore` excludes `logs/` correctly
- [ ] If sample logs are needed for documentation, move them to `docs/examples/`
- [ ] Do not commit generated runtime artifacts

### Branch 9 — quality/final-validation
- [ ] Run full unit, integration, lint, and coverage suite; all must pass
- [ ] Verify every Python source file is within the 150 non-blank/non-comment line limit
- [ ] Update README, TODO, PLAN, and PROMPT_LOG with final state
- [ ] Perform a smoke test (`uv run debate`) verifying end-to-end flow with a real API key

## Definition of Done

| Phase | Criteria |
|-------|----------|
| Foundation | Config files load; pyproject.toml works with uv |
| Infrastructure | Gatekeeper rate-limits; logger rotates; watchdog monitors |
| Providers | All 3 providers callable; search works |
| Agents | Agents produce JSON responses; judge scores |
| Services | Orchestrator runs 10-round debate |
| SDK/CLI | Terminal menu works; SDK exposes all operations |
| Tests | ≥85% coverage; 0 Ruff violations |
| Agent Skills | Skills are modular classes; config-driven; composable; tested in isolation |
| Documentation | README complete; full debate transcript included |
