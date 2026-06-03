# TODO — AI Debate System

## Current Verified Status

> Last verified: 2026-06-03 · Final validation is pending completion of all readiness branches.

| Check | Result |
|-------|--------|
| `uv run ruff check .` | Pending — import-order formatting gate in progress (issue #24) |
| `uv run pytest -q` | Baseline: 264 passed · 3 xfailed · final validation pending |
| Coverage (`--cov=src`) | Baseline: 97.38% · final validation pending |
| Structured output contracts | Enforcement planned — issue #26 |
| Parent-controlled policy | Verification planned — issue #27 |
| Runtime safety controls | Verification planned — issue #28 |
| `config/setup_example.json` | Configuration consistency check in progress — issue #25 |
| Python 150-line rule | Maintainability pass in progress — issue #29 |

---

## Completed Work Log

### Phase 1: Foundation
- [x] Create PRD.md, PLAN.md, TODO.md
- [x] Create pyproject.toml with dependencies
- [x] Create .env-example, .gitignore
- [x] Create config/setup.json, config/rate_limits.json, config/logging_config.json

### Phase 2: Shared Infrastructure
- [x] ConfigManager — load and validate config
- [x] LogManager — structured logging with FIFO rotation
- [x] ApiGatekeeper — rate limiting, queuing, retries
- [x] Watchdog — process monitoring and keep-alive
- [x] Constants — immutable project constants

### Phase 3: LLM Providers
- [x] `LLMProvider` abstract base interface
- [x] `OpenAIProvider`, `AnthropicProvider`, `GeminiProvider`
- [x] `SearchService` — DuckDuckGo search abstraction

### Phase 4: Agents
- [x] `AgentBase` — abstract base agent class
- [x] `JudgeAgent`, `ProAgent`, `ConAgent`

### Phase 5: Services
- [x] `DebateState` — debate state tracking
- [x] `DebateOrchestrator` — manages debate flow

### Phase 6: SDK & CLI
- [x] `DebateSDK` — single entry point
- [x] `ProviderFactory`, `AgentFactory`
- [x] `TerminalMenu` — CLI menu interface
- [x] `main.py` — CWD-independent entry point

### Phase 7: Tests
- [x] Unit tests for all modules
- [x] Integration test for full debate flow
- [x] Coverage ≥85% verified

### Phase 8: Agent Skills
- [x] `AgentSkill` ABC + `ResearchAnalysisSkill`, `QualityStandardsSkill`, `PersuasionScoringSkill`
- [x] `SkillRegistry` + `default_registry()` factory
- [x] Skills wired through SDK, config-driven, tested in isolation

### Phase 9: Documentation & Polish
- [x] README with architecture diagrams, full transcript, ADRs
- [x] Full end-to-end smoke test

### Phase 10: Usage & Cost Tracking
- [x] `UsageRecord` + `build_from_delta()` delta-snapshot pattern
- [x] `CostCalculator` — pure stateless math module
- [x] Pricing config in `config/setup.json`; `validate_pricing()` at startup
- [x] Per-round and full-debate cost logging

### Release Quality Gate: Typed Boundaries
- [x] `config_models.py` typed dataclasses (`DebateConfig`, `AgentConfig`, etc.)
- [x] `protocols.py` — `LoggerProtocol`, `DebateSDKProtocol`
- [x] `ConfigManager` typed property accessors; no raw dict access at call sites
- [x] `FakeProvider`, `ScriptedAgent`, `FakeLogger` typed test fakes
- [x] `TestOrchestratorArchitecture` class with structural verification tests
- [x] `contract.py` shared helpers for provider contract assertions

---

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
- **Note**: 6 Ruff I001 import-sort violations introduced post-merge; resolved in fix/ruff-and-config-example

### Release Quality Gate — fix/ruff-and-config-example ✅
- [x] Fix 6 Ruff I001 import-sort violations (`con_agent.py`, `judge_agent.py`, `pro_agent.py`, `sdk.py`, `orchestrator.py`, `verdict.py`)
- [x] Add `pricing` section to `config/setup_example.json`; set `max_rounds: 5`
- [x] Add `TestSetupExampleConsistency` to `test_config_validator.py` — verifies example passes `validate_pricing()`
- **Result**: 266 passed · 3 xfailed · 97.38% coverage · 0 Ruff violations (issues #24 and #25 ready for closure after PR merge)

---

## Final Submission Readiness Roadmap

| Order | Branch | Release-Readiness Goal | Issues |
|-------|--------|------------------------|--------|
| 1 | `fix/ruff-and-config-example` | Code quality gate + configuration consistency | #24, #25 |
| 2 | `refactor/structured-output-contracts` | Structured output contract enforcement | #26 |
| 3 | `refactor/parent-controlled-policy` | Parent-controlled debate policy verification | #27 |
| 4 | `refactor/runtime-safety-controls` | Runtime safety control verification | #28 |
| 5 | `refactor/line-limit-split` | Maintainability rule compliance | #29 |
| 6 | `docs/developer-guide-and-example` | Developer guide + 5-round example | #18, #20 |
| 7 | `chore/final-submission-validation` | Final validation checklist | #30 |

---

## GitHub Issue Mapping

| Issue | Title | Branch | Status |
|-------|-------|--------|--------|
| #18 | docs: add developer onboarding guide | `docs/developer-guide-and-example` | open |
| #20 | docs: add real 5-round debate example | `docs/developer-guide-and-example` | open |
| #24 | release: pass final code quality gate | `fix/ruff-and-config-example` | open |
| #25 | release: complete configuration consistency check | `fix/ruff-and-config-example` | open |
| #26 | release: enforce structured output contracts | `refactor/structured-output-contracts` | open |
| #27 | release: verify parent-controlled debate policy | `refactor/parent-controlled-policy` | open |
| #28 | release: verify runtime safety controls | `refactor/runtime-safety-controls` | open |
| #29 | release: satisfy 150-line maintainability rule | `refactor/line-limit-split` | open |
| #30 | release: complete final submission validation | `chore/final-submission-validation` | open |

---

## Final Submission Checklist

> Complete all items before submitting. Do not check a box unless a command confirms it.

- [ ] `uv run ruff check .` passes with zero violations
- [ ] `uv run pytest -q` passes
- [ ] Zero xfailed tests remain
- [ ] Coverage remains above 85%
- [ ] `config/setup_example.json` includes pricing and passes validation
- [ ] Structured output contracts are enforced (winner, scores, JSON schema)
- [ ] Parent-controlled policy is verified by passing tests
- [ ] Runtime safety controls are verified or scoped accurately in documentation
- [ ] All Python files satisfy the 150-line maintainability rule
- [ ] README metrics match final command outputs
- [ ] `docs/prompt_log/PROMPT_LOG.md` is updated
- [ ] No secrets or generated artifacts are tracked in git

---

## Deferred Future Work

The following items are intentionally out of scope for final submission and are documented here for transparency:

- **ProviderResult typed return**: A `ProviderResult` datatype would further formalize the provider boundary. The current string-return with delta-snapshot usage tracking is correct and fully tested. This is a future improvement, not a correctness gap.
- **Skills canonicalization**: No ambiguity between runtime agent skills and project skills was found during audit. No action needed.
- **Log rotation artifact cleanup**: `logs/` is excluded by `.gitignore` and no log files are tracked. No action needed.

---

## Definition of Done

| Phase | Criteria |
|-------|----------|
| Foundation | Config files load; pyproject.toml works with uv |
| Infrastructure | Gatekeeper rate-limits; logger rotates; watchdog monitors |
| Providers | All 3 providers callable; search works |
| Agents | Agents produce structured responses; judge scores |
| Services | Orchestrator runs multi-round debate |
| SDK/CLI | Terminal menu works; SDK exposes all operations |
| Tests | ≥85% coverage; zero Ruff violations |
| Agent Skills | Skills are modular classes; config-driven; composable; tested in isolation |
| Documentation | README complete; 5-round example in docs/example_debate.md |
