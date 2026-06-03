# Developer Guide — AI Agent Debate System

## Repository Purpose

This project implements a multi-agent AI debate system as a university course assignment.
Three LLM agents — **Pro**, **Con**, and **Judge** — conduct structured debates on a given
topic. The orchestrator (the "parent") routes all communication; agents never communicate
directly with each other.

See `docs/PRD.md` for the full product requirements and `docs/PLAN.md` for the architecture
rationale.

---

## Quick Start

```bash
# 1. Install dependencies with uv
uv sync --group dev

# 2. Copy and fill in your API keys
cp .env-example .env
# Edit .env — add at least one of: OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY

# 3. Copy the example config and adjust settings
cp config/setup_example.json config/setup.json
# Edit config/setup.json — choose provider/model per agent, set max_rounds, etc.

# 4. Run the CLI
uv run debate
```

---

## uv Workflow

This project uses [uv](https://github.com/astral-sh/uv) for package management.

| Task | Command |
|------|---------|
| Install / sync dependencies | `uv sync --group dev` |
| Add a runtime dependency | `uv add <package>` |
| Add a dev dependency | `uv add --group dev <package>` |
| Run a script in the project env | `uv run <command>` |
| Run the CLI | `uv run debate` |
| Run Python directly | `uv run python3 <script.py>` |

Always use `uv run` rather than activating the venv manually — it keeps the environment
consistent across machines.

---

## Running the CLI

```bash
uv run debate
```

The terminal menu offers:
1. **Start debate** — runs a full debate using `config/setup.json`
2. **View recent logs** — tails the last 50 lines from `logs/debate.log`
3. **Configure** — shows the active config path
4. **Exit**

### Non-interactive smoke test

```bash
printf '4\n' | uv run debate
```

This selects menu option 4 (Exit) without calling any paid API.

---

## Running Tests

```bash
# All tests, concise output
uv run pytest -q

# Verbose output with test names
uv run pytest -v

# Single file
uv run pytest tests/unit/test_services/test_orchestrator_flow.py -v

# Single test
uv run pytest tests/unit/test_services/test_orchestrator_flow.py::TestOrchestratorRun::test_run_completes_all_rounds -v
```

**Expected baseline**: 321 passed · 0 xfailed · 1 warning.

No test should call a real paid API. All external calls are mocked or use
`ScriptedAgent` / `FakeProvider` from `tests/fakes/`.

---

## Running Coverage

```bash
uv run pytest --cov=src --cov-report=term-missing -q
```

**Expected baseline**: ≥ 97% coverage.
The project targets ≥ 85% as the minimum gate. Coverage below 85% blocks submission.

```bash
# Generate HTML report for detailed line-level view
uv run pytest --cov=src --cov-report=html -q
open htmlcov/index.html
```

---

## Running Ruff

```bash
# Check only
uv run ruff check .

# Auto-fix fixable violations
uv run ruff check . --fix

# Format (import sorting + code style)
uv run ruff format .
```

**Expected**: zero violations before every commit. Ruff is configured in `pyproject.toml`
under `[tool.ruff]`.

---

## Configuration

### Setup file

`config/setup.json` is the primary runtime config (not committed — local only).
`config/setup_example.json` is the committed reference example.

Key sections:

```json
{
  "version": "1.00",
  "debate": {
    "topic": "AI should be regulated by international law",
    "max_rounds": 5
  },
  "agents": {
    "judge": { "provider": "openai", "model": "gpt-4o", "skills": ["persuasion-scoring"] },
    "pro":   { "provider": "openai", "model": "gpt-4o-mini", "skills": ["research-analysis"] },
    "con":   { "provider": "openai", "model": "gpt-4o-mini", "skills": ["quality-standards"] }
  },
  "pricing": {
    "unit": "per_1m_tokens",
    "judge": { "input": 2.50, "output": 10.00 },
    "pro":   { "input": 0.15, "output": 0.60 },
    "con":   { "input": 0.15, "output": 0.60 }
  }
}
```

Run `uv run debate` — `ConfigManager` validates the config at startup and raises
`ConfigValidationError` for any structural or pricing issues.

### Rate limits and logging

`config/rate_limits.json` — controls `ApiGatekeeper` (requests/second, retry behaviour).
`config/logging_config.json` — controls `LogManager` (log directory, max file size).

---

## Secrets Policy

| File | Purpose | Committed? |
|------|---------|-----------|
| `.env` | Runtime API keys | **No** — in `.gitignore` |
| `.env-example` | Placeholder template | **Yes** |
| `config/setup.json` | Active config | **No** — in `.gitignore` |
| `config/setup_example.json` | Reference config | **Yes** |

Never commit `.env`, `config/setup.json`, or any file containing real API keys.
`ProviderFactory` reads keys from environment variables (`OPENAI_API_KEY`, etc.) at
runtime, not from the config file.

---

## Adding a Provider

1. Create `src/debate/providers/myprovider_provider.py` (under 150 lines).
2. Subclass `LLMProvider` from `src/debate/providers/base_provider.py`.
3. Implement `_chat(messages, tools, tool_executor)` and `_extract_usage(response)`.
4. Register the provider name in `src/debate/sdk/provider_factory.py` under the
   `_PROVIDER_MAP` dict.
5. Add `MYPROVIDER_API_KEY` to `.env-example`.
6. Add tests in `tests/unit/test_providers/test_myprovider_provider.py` following the
   pattern in the existing provider test files.

---

## Adding a Skill

Skills are loaded by `SkillRegistry` and injected into agents via config.

1. Create `src/debate/skills/my_skill.py` (under 150 lines).
2. Subclass `AgentSkill` from `src/debate/skills/base_skill.py`.
3. Implement `name`, `get_instructions()`, and optionally `get_tool_definition()` /
   `search()`.
4. Register the skill in `src/debate/skills/registry.py` inside `default_registry()`.
5. Add skill name to the appropriate agent's `skills` list in `config/setup_example.json`.
6. Enforce role semantics in `src/debate/shared/config_validator.py`
   (`JUDGE_ONLY_SKILLS` / `DEBATER_ONLY_SKILLS` sets).
7. Add tests in `tests/unit/test_skills/`.

---

## 150-Line Rule

Every Python file in `src/` and `tests/` must stay under 150 lines (raw line count).

Check before committing:

```bash
python3 - <<'PY'
from pathlib import Path
violations = []
for root in ["src", "tests"]:
    for path in sorted(Path(root).rglob("*.py")):
        lines = path.read_text(encoding="utf-8").splitlines()
        if len(lines) > 150:
            violations.append((len(lines), path))
if violations:
    for n, p in violations: print(f"{n:4d} raw | {p}")
else:
    print("All files under 150 lines.")
PY
```

When a file approaches the limit, split by semantic concern:
- Extract cohesive helpers to a `_helpers.py` or `_<concern>.py` sibling module.
- Split test files by behavior class (e.g., `test_foo_flow.py` + `test_foo_errors.py`).
- Never delete tests to reduce line count.

---

## Updating TODO.md and Prompt Log

After every branch merged to master:

1. **`docs/TODO.md`** — update the _Current Verified Status_ table with fresh command
   outputs; mark the relevant checklist item; update the GitHub Issue Mapping table.

2. **`docs/prompt_log/PROMPT_LOG.md`** — add an entry with:
   - branch name and issue number
   - what changed
   - final `ruff`, `pytest`, coverage outputs
   - any key design decisions or lessons

These files are committed on the same branch as the change, not as a separate
documentation-only commit.

---

## Logs and Transcripts

Debate transcripts are written to `logs/debate.log` (or the path in
`config/logging_config.json`). The `logs/` directory is excluded by `.gitignore`.

To read recent log lines programmatically:

```python
from debate.sdk import DebateSDK
sdk = DebateSDK()
lines = sdk.get_logs(count=100)
print("\n".join(lines))
```

---

## Avoiding Generated Artifacts in Git

The following are excluded by `.gitignore` and must never be committed:

| Pattern | Reason |
|---------|--------|
| `logs/` | Runtime debate transcripts |
| `.env` | API keys |
| `config/setup.json` | Local runtime config |
| `__pycache__/`, `*.pyc` | Python bytecode |
| `.pytest_cache/`, `.coverage` | Test artifacts |
| `.ruff_cache/` | Linter cache |
| `htmlcov/` | Coverage HTML report |
| `.venv/` | Virtual environment |

Before committing, always run `git status` to confirm no unintended files are staged.

---

## Project Structure

```
src/debate/
├── agents/          # JudgeAgent, ProAgent, ConAgent, AgentBase
├── cli/             # TerminalMenu
├── providers/       # OpenAI, Anthropic, Gemini, base provider
├── sdk/             # DebateSDK (single entry point), factories, wiring
├── services/        # Orchestrator, DebateState, contracts, verdict, ...
├── shared/          # ConfigManager, LogManager, Watchdog, ApiGatekeeper, paths
├── skills/          # AgentSkill ABC, three concrete skills, SkillRegistry
└── main.py          # Entry point (only file that calls sys.exit)

tests/
├── fakes/           # FakeProvider, ScriptedAgent, FakeLogger
└── unit/            # mirrors src/ structure
```

---

## See Also

- `docs/PRD.md` — product requirements and acceptance criteria
- `docs/PLAN.md` — architecture decisions and rationale
- `docs/example_debate.md` — annotated 5-round mock debate transcript
- `config/setup_example.json` — reference configuration with all sections
