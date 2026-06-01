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

## Phase 8: Documentation & Polish
- [ ] README.md with screenshots
- [ ] Ruff check — zero violations
- [ ] Full debate session test
- [ ] Final checklist review

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
| Documentation | README complete; full debate transcript included |
