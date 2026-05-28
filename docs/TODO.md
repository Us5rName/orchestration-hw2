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
- [ ] ConfigManager — load and validate config
- [ ] LogManager — structured logging with FIFO rotation
- [ ] ApiGatekeeper — rate limiting, queuing, retries
- [ ] Watchdog — process monitoring and keep-alive
- [ ] Constants — immutable project constants

## Phase 3: LLM Providers
- [ ] ILLMProvider — abstract base interface
- [ ] OpenAIProvider — OpenAI API implementation
- [ ] AnthropicProvider — Anthropic API implementation
- [ ] GeminiProvider — Google Gemini API implementation
- [ ] SearchService — DuckDuckGo search abstraction

## Phase 4: Agents
- [ ] AgentBase — abstract base agent class
- [ ] JudgeAgent — judge/mediator agent
- [ ] ProAgent — pro-side debater
- [ ] ConAgent — con-side debater

## Phase 5: Services
- [ ] DebateState — debate state tracking
- [ ] DebateOrchestrator — manages debate flow

## Phase 6: SDK & CLI
- [ ] DebateSDK — single entry point
- [ ] TerminalMenu — CLI menu interface
- [ ] main.py — entry point

## Phase 7: Tests (TDD)
- [ ] Unit tests for ConfigManager
- [ ] Unit tests for LogManager
- [ ] Unit tests for ApiGatekeeper
- [ ] Unit tests for Watchdog
- [ ] Unit tests for LLM providers
- [ ] Unit tests for agents
- [ ] Unit tests for DebateOrchestrator
- [ ] Unit tests for DebateSDK
- [ ] Integration test for full debate flow
- [ ] Verify ≥85% coverage

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
