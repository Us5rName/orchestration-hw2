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

---

### Prompt 12: Agent Skills — Modular Plugin Architecture
**User**: "update the relevant docs, implement and commit. remember to use your relevant skills from the project when doing things. commit in a new branch, using the templates of the other branches. commits should be small and readable"

**Context**: Agents had hardcoded skill text in `_build_system_prompt()`. Skills were not configurable, composable, or independently testable. User had clarified: research skill needs live internet search via existing SearchService; persuasion-scoring is judge-only; research-analysis and quality-standards are debater-only.

**Skills Applied**: modular-design, sdk-architecture, tdd-testing, version-control, code-review-config

**Output**:
- `AgentSkill` ABC: `name`, `get_instructions()`, `get_tool_definition()`, `search()`
- Three concrete skills: `ResearchAnalysisSkill` (with native tool call + SearchService), `QualityStandardsSkill`, `PersuasionScoringSkill`
- `SkillRegistry` plugin pattern with `default_registry()` factory; lazy import breaks circular dep
- All three providers (OpenAI, Anthropic, Gemini) updated to handle native tool calling loop internally
- `AgentBase` composes skills: `_build_skill_block()`, `_get_tools()`, `_execute_tool()`
- `AgentFactory` mirrors ProviderFactory pattern; SDK delegates to it
- `ConfigValidator` enforces role-skill semantics at startup (raises on cross-role assignment)
- `config/setup.json` — skills arrays per agent
- 25 new skill tests + provider tool-call tests + agent skill tests + SDK wiring tests
- 174 total tests, all passing; 0 Ruff violations; coverage maintained

**Key Design**:
- Native LLM tool calling (function calling) — providers handle the call loop internally, keeping AgentBase clean
- `chat(messages, tools=None, tool_executor=None)` — provider-agnostic interface; each provider translates to its own format
- Circular import resolved: `TYPE_CHECKING` guard in `research_analysis.py` + lazy import in `default_registry()`
- Role-skill validation at startup prevents misconfiguration silently passing through

**Lessons**:
- `mock[0] = x` does NOT make `mock[0]` return `x` in MagicMock — access the chain to get the cached child mock, then set attributes
- Plugin registries with lazy imports are the cleanest way to break circular deps while keeping the public API clean
- Validate config semantics (role-skill compatibility) at startup, not at runtime

---

### Prompt 13: Runtime Bug Fixes and Skill/Tool Logging
**User**: "this is the input + output I got. remember the skills you have with the instructions and fix the problem. add the relevant test, and commit in small readable commits" (traceback showed TypeError, RuntimeWarning, ResourceWarning)

**Context**: First real end-to-end run of the debate. Three runtime issues surfaced: (1) crash in orchestrator logging when LLM returned references as dicts instead of strings; (2) unclosed file handle in logger line-count check; (3) duckduckgo_search package renamed to ddgs.

**Skills Applied**: tdd-testing, version-control, modular-design

**Output**:
- `orchestrator_logging.py`: coerce non-string references with `str(r)` before `join()`; 10-test suite added (`test_orchestrator_logging.py`) covering str, dict, mixed, and None-logger cases
- `logger.py`: wrapped `_current_file.open()` in `with` statement to close handle after line count
- `search_service.py` + `pyproject.toml`: migrated `from duckduckgo_search import DDGS` → `from ddgs import DDGS`; removed `duckduckgo-search` from dependencies
- Added skill/tool logging to `AgentBase`: logs active skill names at `think()` entry, tool name + query and result count at each `_execute_tool()` dispatch
- `logger` param threaded through `JudgeAgent`, `ProAgent`, `ConAgent`, `AgentFactory`, `DebateSDK`
- 6 new `TestAgentLogging` tests; 190 total tests, all passing; 0 Ruff violations

**Key Design**:
- Agent-level log entries (`PRO skills active: ...`, `PRO tool call: search(...)`, `PRO tool result: 3 item(s)`) flow through the same LogManager as orchestrator-level entries
- Logger is optional everywhere — no-op when None, no defensive branching in callers

**Lessons**:
- Always run end-to-end before marking a phase complete — unit tests catch logic bugs, runtime reveals integration gaps
- `wc -l` counts blanks and comments; use `grep -cE '^\s*[^#\s]'` for the true code-line count against the 150-line rule
- When migrating packages, verify the new package's API (context manager, method signatures) before updating the import

---

### Prompt 14: File Size Audit
**User**: "check if there are any code files longer than 150 lines and if there are semantically split them"

**Context**: Routine hygiene check after adding new code across multiple files.

**Output**: All files within limit. Largest: `base_agent.py` at 124 code lines / 148 total. No splits needed.

**Lessons**:
- Distinguish total lines (`wc -l`) from code lines (non-blank, non-comment) — the rule targets code lines
- Small, focused commits make the line-count check a non-issue; files rarely bloat when concerns are split at commit time

---

### Prompt 15: Phase 9 — Documentation & Polish
**User**: "Start phase 9. each commit should have at most 3 different files."

**Context**: Final phase — README, Ruff check, full debate test, final checklist.

**Skills Applied**: final-checklist, version-control, code-review-config

**Output**:
- README.md — user-manual-level doc with architecture diagram, CLI screenshots, full debate transcript, skill/provider extension guides, test results, project layout, ADR table
- docs/TODO.md — Phase 9 marked complete
- Prompt log session 15 added
- 193 tests, 97.82% coverage, 0 Ruff violations confirmed
- Final checklist items verified: SDK architecture ✓, OOP ✓, Gatekeeper ✓, rate limits ✓, ≤150 lines ✓, .env-example ✓, uv ✓, pyproject.toml ✓, prompt log ✓

**Key Design**:
- Transcript in README taken verbatim from `logs/debate.log` (Real Madrid vs Barcelona, 1-round demo)
- ASCII architecture diagram inline — no external rendering dependency
- "Budget tip" documents the rounds → cost trade-off from PRD constraints

**Lessons**:
- Keep transcript in README, not as a separate file — reduces navigation friction
- ASCII diagram in README is more portable than mermaid (renders everywhere)

---

### Prompt 16: Phase 10 — Usage & Cost Tracking
**User**: "Mission: implement full usage and cost tracking across all providers and agents."

**Context**: Phase 10 — full token tracking pipeline across OpenAI, Anthropic, Gemini; pricing config; per-round logs.

**Skills Applied**: costs-pricing, final-checklist

**Output**:
- `UsageRecord` dataclass + `build_from_delta()` factory — delta-snapshot pattern for per-turn token attribution
- Match/case usage extraction in all 3 provider classes — handles dict, typed SDK object, and None responses
- `CostCalculator` — pure stateless math module; supports per_1m_tokens and per_1k_tokens units
- Pricing config in `config/setup.json`; `validate_pricing()` added to config_validator startup
- `orchestrator_logging.py` — `log_round_cost` and `log_debate_cost` helpers
- `DebateOrchestrator` — captures usage snapshots before each agent call, emits per-round and debate-level cost summaries
- `DebateSDK` — propagates `pricing` config to orchestrator
- 230 tests, 99% coverage, 0 Ruff violations

**Key Design**:
- Delta-snapshot pattern: `get_usage()` before and after each agent call; delta correctly handles tool-call loops where the provider is called multiple times per agent turn
- Match/case for usage extraction: Python structural pattern matching handles both raw SDK objects (typed attrs) and dict-like responses uniformly; MagicMock falls safely to the `else` branch in tests
- `available=False` flag: records with no usage data are preserved in the ledger so downstream aggregation stays correct without crashing or inventing tokens
- Pricing per role in config (not hardcoded): allows per-agent cost differentiation when different models are used

**Lessons**:
- `int(MagicMock())` returns 1 in Python — can mask delta bugs in tests; explicit `SimpleNamespace` fixtures are more trustworthy for usage branch tests
- Ruff B027 fires on empty methods in ABC subclasses; a `return  # concrete no-op` comment body silences it correctly
- Keep `build_from_delta` in `usage_record.py` (not the orchestrator) — separates the delta math from orchestration and makes it testable in isolation

---

---

### Prompt 17: Path Handling Refactor (2026-06-03)
**User**: "Your task is to refactor the repository's path handling into a robust, centralized, best-practice design." Full specification: `paths.py` as single source of truth; no `sys.exit()` in library modules; entry-point moved to `debate.main`; all default-path constants removed from `constants.py`; CWD-independent everywhere.

**Context**: Paths were previously a mix of hardcoded relative strings (`"config/setup.json"`), `sys.exit()` calls in `config_validator.py`, and a broken `pyproject.toml` entry point (`src.main:main` fails for installed packages in src/ layout).

**Skills Applied**: final-checklist

**Output**:
- `src/debate/shared/paths.py` (new) — `_find_project_root()` walks upward from `__file__` until it finds a directory with both `pyproject.toml` and `config/`; exposes `PROJECT_ROOT`, `CONFIG_DIR`, `LOGS_DIR`, all `DEFAULT_*` path constants, `resolve_project_path()`, `require_file()`, `require_dir()`; `ProjectPathError(RuntimeError)` for path errors
- `src/debate/main.py` (new) — real entry point; only module permitted to call `sys.exit()`; catches `ConfigValidationError` and exits with code 1
- `src/main.py` — reduced to a 4-line legacy shim (`from debate.main import main`)
- `pyproject.toml` — entry point fixed from `"src.main:main"` → `"debate.main:main"`; coverage omit updated
- `src/debate/shared/config.py` — `ConfigManager(path: str | Path | None = None)` resolves via `resolve_project_path()`; uses `path.open()` throughout
- `src/debate/shared/config_validator.py` — all 5 `sys.exit()` calls removed; `ConfigValidationError(RuntimeError)` added; `validate_pricing()` and `validate_agent_skills()` raise `ConfigValidationError`; default paths from paths module
- `src/debate/shared/logger.py` — `log_dir` and `log_file` properties added; resolves relative log directories to `PROJECT_ROOT`
- `src/debate/sdk/sdk.py` — `config_path` default `None`; `get_logs()` uses `self.logger.log_file` (absolute, always correct)
- `src/debate/cli/menu.py` — option 3 shows actual resolved path instead of hardcoded string
- `src/debate/constants.py` — 3 path string constants removed; comment points to `debate.shared.paths`
- Tests: new `test_paths.py` (21 tests); updated `test_config_validator.py`, `test_config.py`, `test_logger.py`, `test_constants.py` — CWD-independence verified via `monkeypatch.chdir(tmp_path)`
- README: PyCharm debug setup section added; project layout updated; test count corrected to 261

**Key Design**:
- Root detection from `__file__` (not `Path.cwd()`) makes every module CWD-independent; works correctly whether invoked via `uv run debate`, `python -m debate.main`, or PyCharm module-run configuration
- `resolve_project_path(path)`: absolute paths pass through unchanged; relative paths are anchored to `PROJECT_ROOT`; `~` expansion applied universally
- Library modules raise exceptions; only the entry point converts to `SystemExit`
- `LogManager.log_file` property exposes `handler._current_file` so `SDK.get_logs()` never has to reconstruct the log path from config

**Key Lessons**:
- PyCharm *Script path* mode sets CWD to the script's directory, which breaks src/ layout imports; *Module name* mode (`debate.main`) is the correct approach
- `sys.exit()` in library code is a design smell — callers lose the ability to catch and recover; `RuntimeError` subclasses keep all options open
- `str | Path | None` for path parameters is the right public API: `None` means "use the project default", string/Path means "use this exact path"
- Ruff I001 fires on long single-line imports; break into parenthesised multi-line blocks

---

### Prompt 0 (Phase 11 Planning) — Staged Architecture Refactor Roadmap (2026-06-03)
**User**: "Document the full refactor roadmap before touching production code."

**Context**: All 10 original phases are complete (258 tests, 99% coverage, 0 Ruff violations).
Before any production refactoring, the full roadmap must be documented in TODO.md and PLAN.md so
every subsequent branch has a clear, agreed scope.

**Branch**: `docs/refactor-roadmap` (documentation-only, no source changes)

**Output**:
- `docs/TODO.md` — Phase 11 added with 9 ordered branches covering: test harness consolidation,
  typed config/SDK boundary, provider result contract, structured agent outputs, parent-controlled
  state machine, gatekeeper/watchdog real use, skills canonicalization, log cleanup, and final
  validation
- `docs/PLAN.md` — Architecture Refactor Plan section added explaining the rationale for each
  major refactor category
- `docs/prompt_log/PROMPT_LOG.md` — this entry

**Key Decisions**:
- Tests are refactored before production code: existing MagicMock-heavy tests are too permissive
  to validate new contracts; the harness must describe the target architecture first
- Typed config, provider contracts, and structured outputs are core correctness work, not polish
- Parent/judge routing must become structural (no child-to-child references), not just conventional
- Gatekeeper and watchdog must either be in the real hot path or honestly documented as future work

**Best Practice Applied**: Document the full roadmap (and its rationale) as a committed doc change
before any production refactoring begins — ensures the scope is reviewable and agreed before code
changes accumulate.

---

### Prompt 1 (Phase 11 / Branch 1) — Test Harness Refactor (2026-06-03)
**User**: Refactor the test suite before refactoring production architecture.

**Branch**: `test/refactor-harness-and-duplicates`

**Inventory findings**:
- `test_base_agent.py` was the only file over the 150-line code limit (157 lines)
- All 3 provider test files had identical Init/Chat/Tool/Usage test class patterns (structural duplication)
- `test_base_provider.py` and `test_base_skill.py` used `type: ignore[abstract]` to force-instantiate abstract classes
- `test_orchestrator.py` and `test_debate_flow.py` used bare `MagicMock()` for agents — too permissive for architecture verification
- No tests for child-isolation, tie prevention, or invalid output rejection

**Changes**:
- `tests/fakes/` — `FakeProvider` (scripted LLM responses) + `ScriptedAgent` (deterministic `think()`)
- `tests/unit/test_providers/contract.py` — shared contract assertions for all 3 providers
- `test_base_provider.py`, `test_base_skill.py` — `inspect.isabstract()` replaces forced instantiation
- `test_base_agent.py` split → `test_base_agent_logging.py` (both under 150 lines)
- `test_orchestrator.py` — `ScriptedAgent` + `TestOrchestratorArchitecture` with 2 passing + 3 `xfail`
- `test_debate_flow.py` — `ScriptedAgent`, removed duplicated MagicMock fixtures

**xfail tests** (deliberate, to be resolved in named branches):
- `test_judge_tie_is_rejected` → Branch 4
- `test_invalid_agent_output_raises` → Branch 4
- `test_winner_must_be_pro_or_con` → Branch 5

**Result**: 264 passed · 3 xfailed · 98.62% coverage · 0 Ruff violations

**Lessons**:
- `set(vars().values())` fails on unhashable attrs (lists); use `id()` comparison for object-identity checks
- `inspect.isabstract()` + `__abstractmethods__` is cleaner than trying to force-instantiate an ABC
- `ScriptedAgent._idx` counter provides a cheap, no-mock way to verify call counts in routing tests

---

### Session — Final Submission Readiness Planning and Issue Alignment (2026-06-03)
**User**: `/plan` command followed by execution of `chore/issue-and-doc-sync-plan` branch.

**Context**: Project-wide planning synchronization and final submission readiness alignment.
All original development phases and the typed-boundaries quality gate were complete.
The goal was to establish a verified baseline, create a clean release-readiness issue set, link
development branches, and align all documentation with the Final Submission Readiness Roadmap.

**Branches**: `chore/issue-and-doc-sync-plan`, `chore/final-submission-polish-plan`
(documentation and issue management only — no source code changes)

**Verified Baseline at Time of Alignment**:
- `uv run ruff check .` — import-order formatting gate pending (issue #24)
- `uv run pytest -q` — **264 passed, 3 xfailed** · structured output contract enforcement pending (#26)
- Coverage — **97.38%** (well above 85% threshold)
- `config/setup_example.json` — configuration consistency check pending (#25)
- Python 150-line rule — maintainability pass pending (#29)
- Runtime safety controls — verification pass pending (#28)

**Release-Readiness Issues Created**:
- #24 — release: pass final code quality gate (`fix/ruff-and-config-example`)
- #25 — release: complete configuration consistency check (same branch)
- #26 — release: enforce structured output contracts (`refactor/structured-output-contracts`)
- #27 — release: verify parent-controlled debate policy (`refactor/parent-controlled-policy`)
- #28 — release: verify runtime safety controls (`refactor/runtime-safety-controls`)
- #29 — release: satisfy 150-line maintainability rule (`refactor/line-limit-split`)
- #30 — release: complete final submission validation (`chore/final-submission-validation`)
- #18, #20 updated — developer guide and 5-round example (`docs/developer-guide-and-example`)

**Development Branches Linked**: All seven release-readiness branches linked to their respective issues via GitHub Development panel.

**Documentation Updated**:
- `docs/TODO.md` — restructured with Current Verified Status, Completed Work Log, Final Submission
  Readiness Roadmap, GitHub Issue Mapping, Final Submission Checklist, Deferred Future Work
- `docs/PLAN.md` — refactor rationale section reframed as Final Submission Readiness Roadmap
- `README.md` — Tests & Quality section updated to reflect baseline with pending final validation;
  architecture note updated to accurately describe ApiGatekeeper scope

**Key Decisions**:
- ProviderResult typed return is deferred as future work — current string-return with delta-snapshot is correct and tested
- Runtime safety controls will be verified or scoped accurately in the dedicated readiness branch (#28)
- README final metrics are not updated until all commands are confirmed green in the final validation branch (#30)

---

### Prompt 2 (Release Quality Gate fix/ruff-and-config-example) — Ruff and Config Example Fix (2026-06-03)
**User**: Fix all Ruff violations and add missing pricing section to setup_example.json.

**Branch**: `fix/ruff-and-config-example`

**Problem**: 6 Ruff I001 import-sort violations were present post-Branch-2 merge. `config/setup_example.json` was missing the `pricing` section that `validate_pricing()` requires, meaning any user copying the example would fail at startup.

**Changes**:
- `ruff check --fix .` — sorted imports in `con_agent.py`, `judge_agent.py`, `pro_agent.py`, `sdk.py`, `orchestrator.py`, `verdict.py`
- `config/setup_example.json` — added `pricing` section (per_1m_tokens, gpt-4o-mini reference rates); `max_rounds` set to 5
- `tests/unit/test_shared/test_config_validator.py` — added `TestSetupExampleConsistency` (2 tests) proving example satisfies the pricing validator
- `docs/TODO.md` — added Release Quality Gate entry with verified results
- Issues #24 (Ruff) and #25 (config example) ready for closure after PR merge

**Result**: 266 passed · 3 xfailed · 97.38% coverage · 0 Ruff violations

**Key Decisions**:
- Tests were added for the example file rather than relying on manual verification — the validator is fast and the test catches future regressions
- `max_rounds: 5` is the canonical user-facing default; `config/setup.json` keeps `max_rounds: 1` as a dev shortcut

---

### Branch: refactor/structured-output-contracts — Issue #26 (2026-06-03)
**User**: Enforce structured output contracts for agent and judge outputs.

**Branch**: `refactor/structured-output-contracts` · Issue #26

**Contracts added**:
- `src/debate/services/contracts.py` — `AgentResponse` and `JudgeDecision` dataclasses with `__post_init__` validation; `agent_response_from_dict()` and `judge_decision_from_dict()` factory functions; `validate_agent_dict()` and `validate_judge_dict()` helpers
- Validation rules: content non-empty + no control chars; winner must be "pro"/"con"; scores must differ; reasoning non-empty
- `verdict.decide_winner()` calls `validate_judge_dict()` before returning
- `orchestrator._run_pro_turn()` and `_run_con_turn()` call `validate_agent_dict()` before recording arguments

**Tests updated**:
- `tests/unit/test_services/test_contracts.py` — 30 new tests covering all validation paths
- `tests/unit/test_services/test_verdict.py` — `test_calls_judge_think` updated to include `justification` field
- `tests/unit/test_services/test_orchestrator.py` — 3 xfail tests converted to passing tests:
  - `test_judge_tie_is_rejected` — now `pytest.raises(ValueError, match="tie")`
  - `test_invalid_agent_output_raises` — xfail removed (already used `pytest.raises`)
  - `test_winner_must_be_pro_or_con` — now `pytest.raises(ValueError, match="pro.*con|con.*pro")`

**xfail count**: 3 xfailed → 0 xfailed

**Final validation**:
- `uv run ruff check .` → All checks passed!
- `uv run pytest -q` → 302 passed · 0 xfailed · 1 warning
- Coverage → 97.51% (above 85% threshold)

---

### Branch: refactor/runtime-safety-controls — Issue #28 (2026-06-03)
**User**: Verify and wire runtime safety controls into the real execution path.

**Branch**: `refactor/runtime-safety-controls` · Issue #28

**ApiGatekeeper — wired**:
- `DebateOrchestrator.__init__` gains `gatekeeper: ApiGatekeeper | None = None` parameter
- `_run_pro_turn()` — wraps `pro.think()` through `gatekeeper.execute()`
- `_run_con_turn()` — wraps `con.think()` through `gatekeeper.execute()`
- `run()` — wraps `decide_winner(judge, state)` through `gatekeeper.execute()`
- `DebateSDK._create_orchestrator()` passes `gatekeeper=self.gatekeeper`
- Result: every agent think() call is rate-limited, queued, and retried via ApiGatekeeper

**Watchdog — wired**:
- `DebateOrchestrator.run()` calls `watchdog.ping()` once before each debate round
- Keeps watchdog alive throughout debate execution; timeout fires only on actual hang

**Tests added**:
- `tests/unit/test_services/test_runtime_safety.py` (7 new tests)
  - `TestGatekeeperRuntime`: verifies execute() called 3× per 1-round debate, 7× per 3-round debate, full debate succeeds with real gatekeeper, gatekeeper optional
  - `TestWatchdogRuntime`: verifies ping() called once per round, debate completes with healthy watchdog, watchdog optional

**Documentation updated**:
- `docs/PLAN.md` — Runtime Safety Control Verification section now accurately describes wired behavior
- `docs/TODO.md` — issue #28 implementation noted as ready for closure after PR merge; checklist item checked; metrics updated; line-limit note updated to include `orchestrator.py` and `sdk.py` as scheduled for `refactor/line-limit-split` (#29)

**xfail count**: 0 xfailed (unchanged)

**Line-count note**: `orchestrator.py` and `sdk.py` remain over 150 lines and are scheduled for `refactor/line-limit-split` (#29). This branch intentionally does not perform the line-limit split to keep runtime-safety verification focused.

**Final validation**:
- `uv run ruff check .` → All checks passed!
- `uv run pytest -q` → 311 passed · 0 xfailed · 1 warning
- Coverage → 97.54% (above 85% threshold)

This branch completes the implementation work for #28; the PR closes it on merge.

---

## Best Practices Established

1. Plan before code — PRD → PLAN → TODO → approval → implement
2. Feature branches — one per phase
3. Meaningful commits — what changed and why
4. Prompt log — document AI-assisted decisions
5. TDD cycle — RED (test) → GREEN (impl) → REFACTOR (ruff) → commit
6. CWD-independent paths — anchor to `__file__`, not `Path.cwd()`; test with `monkeypatch.chdir()`
7. No `sys.exit()` in library modules — raise typed `RuntimeError` subclasses; let entry point convert to `SystemExit`
