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

### Branch 1 — test/refactor-harness-and-duplicates ✅
- [x] Add `tests/fakes/providers.py` — `FakeProvider` (typed, scripted, replaces bare `MagicMock`)
- [x] Add `tests/fakes/agents.py` — `ScriptedAgent` (typed, deterministic `think()`)
- [x] Replace `type: ignore[abstract]` with `inspect.isabstract()` in `test_base_provider.py` and `test_base_skill.py`
- [x] Add `tests/unit/test_providers/contract.py` — shared `assert_base_attrs`, `assert_usage_zero`, `assert_usage_recorded` helpers; all 3 vendor files use them
- [x] Split `test_base_agent.py` (157 → 113 code lines) — `TestAgentLogging` moved to `test_base_agent_logging.py` (74 lines); `FakeProvider` replaces bare `MagicMock` fixture
- [x] Refactor `test_orchestrator.py` — `ScriptedAgent` replaces bare `MagicMock` agents; new `TestOrchestratorArchitecture` class with 2 passing + 3 xfail arch-intent tests
- [x] Refactor `tests/integration/test_debate_flow.py` — `ScriptedAgent` replaces bare `MagicMock`; removed duplicated fixture definitions
- **Result**: 264 passed · 3 xfailed · 98.62% coverage · 0 Ruff violations
- **xfail tests (intentional)**:
  - `test_judge_tie_is_rejected` — Branch 4 will enforce tie detection
  - `test_invalid_agent_output_raises` — Branch 4 will validate agent output
  - `test_winner_must_be_pro_or_con` — Branch 5 will enforce winner validation

### Branch 2 — refactor/typed-config-sdk-boundary ✅
- [x] Add `src/debate/shared/config_models.py` — `DebateConfig`, `AgentConfig`, `LoggingConfig` (with `to_dict()`), `PricingRoleConfig`, `PricingConfig` dataclasses with `from_dict()` classmethods
- [x] Add `src/debate/shared/protocols.py` — `LoggerProtocol` (structural, `@runtime_checkable`), `DebateSDKProtocol`
- [x] `ConfigManager` — typed property accessors: `.debate_config`, `.logging_config`, `.gatekeeper_config` (returns `RateLimitConfig`), `.pricing_config`, `.agent_config(role)`
- [x] `DebateSDK` — uses typed config properties throughout; no raw `config.get("section", {})` calls
- [x] `TerminalMenu` — `sdk: DebateSDKProtocol` (replaces `sdk: object`)
- [x] All agents (`ProAgent`, `ConAgent`, `JudgeAgent`, `AgentBase`) — `provider: LLMProvider`, `logger: LoggerProtocol | None`
- [x] `DebateOrchestrator` — `watchdog: Watchdog | None`, `logger: LoggerProtocol | None`
- [x] `orchestrator_logging.py` — all 8 functions use `logger: LoggerProtocol | None`
- [x] `agent_factory.py` — `logger: LoggerProtocol | None`
- [x] Add `tests/fakes/logger.py` — `FakeLogger` implementing `LoggerProtocol` with `.messages` property
- [x] `test_base_agent_logging.py` and `test_orchestrator_logging.py` — use `FakeLogger` instead of bare `MagicMock`
- [x] SDK tests updated — `apply_typed_config()` helper in conftest wires new typed accessors on mocked `ConfigManager`
- **Result**: 264 passed · 3 xfailed · 97.69% coverage · 0 Ruff violations

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
