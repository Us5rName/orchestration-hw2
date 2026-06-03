# AI Debate System

Multi-agent AI debate system where two LLM-powered agents argue opposing sides of a topic
under the supervision of a Judge agent. Built for the AI Orchestration course — Dr. Sagol.

## How It Works

```
User → TerminalMenu → DebateSDK → DebateOrchestrator
                                        │
                         ┌──────────────┼──────────────┐
                         ▼              ▼              ▼
                     ProAgent       ConAgent       JudgeAgent
                         │              │              │
                    (research)    (research +     (persuasion-
                                  quality-std)    scoring)
                         │              │
                    SearchService  SearchService
                         │
                    ApiGatekeeper   LLMProvider (OpenAI / Anthropic / Gemini)
```

- **Pro** argues one side using live web search for citations.
- **Con** argues the other side, cross-checking evidence and challenging methodology.
- **Judge** scores persuasiveness (no ties), then declares a winner.
- **ApiGatekeeper** provides rate limiting, retries, and call queuing — runtime safety control verification is part of the Final Submission Readiness Roadmap.

## Quick Start

```bash
git clone <repo>
cd orchestration-hw2

# Install dependencies
uv sync

# Copy and fill in API keys
cp .env-example .env
# Edit .env — add at least one provider key

# Run
uv run debate
```

### PyCharm / IDE Debug Setup

Because the project uses a `src/` layout, running `src/main.py` directly causes
import errors (`ModuleNotFoundError: No module named 'debate'`). Use one of these approaches instead:

**Option A — uv run (terminal, always works)**
```bash
uv run debate
```

**Option B — PyCharm Run/Debug Configuration**

1. Open *Run → Edit Configurations* → `+` → *Python*
2. Set **Module name** to `debate.main` (not *Script path*)
3. Set **Working directory** to the project root (`orchestration-hw2/`)
4. Set **Python interpreter** to the `.venv` created by `uv sync`
5. Click *OK* — use this configuration for all debug sessions

The entry point `debate.main` detects the project root by walking upward from
`__file__`, so it works correctly from any working directory.

### Minimal `.env`

```dotenv
OPENAI_API_KEY=sk-...
```

## Configuration

All tuneable values live in `config/setup.json` — no hardcoded values in code.

```json
{
  "debate": {
    "topic": "Real Madrid vs Barcelona - which is better?",
    "max_rounds": 5,
    "max_tokens_per_agent": 50000,
    "request_timeout_seconds": 600
  },
  "agents": {
    "judge":  { "provider": "openai", "model": "gpt-4o-mini", "temperature": 0.3, "skills": ["persuasion-scoring"] },
    "pro":    { "provider": "openai", "model": "gpt-4o-mini", "temperature": 0.7, "skills": ["research-analysis"] },
    "con":    { "provider": "openai", "model": "gpt-4o-mini", "temperature": 0.7, "skills": ["research-analysis", "quality-standards"] }
  },
  "gatekeeper": {
    "requests_per_minute": 30,
    "requests_per_hour": 500,
    "max_retries": 3,
    "retry_delay_seconds": 5
  }
}
```

**Budget tip**: reduce `max_rounds` from 10 → 3 to cut costs by ~70% while still getting a verdict.

### Supported Providers

| Provider  | `"provider"` value | Key env var            |
|-----------|--------------------|------------------------|
| OpenAI    | `"openai"`         | `OPENAI_API_KEY`       |
| Anthropic | `"anthropic"`      | `ANTHROPIC_API_KEY`    |
| Gemini    | `"gemini"`         | `GOOGLE_GENAI_API_KEY` |
| Any OpenAI-compatible | `"openai"` + `"base_url"` | — |

Set `"base_url"` in the agent config to point at OpenRouter, Ollama, or any other OpenAI-compatible endpoint.

## Terminal Interface

```
AI Debate System v1.00

1. Start Debate
2. View Logs
3. Configuration
4. Exit

Select option: _
```

### Start Debate output

```
Starting debate...

Winner: pro
Pro Score: 78
Con Score: 72
Justification: The pro side presented a clear, well-structured argument with concrete
statistics and logical sequencing, making it easy to follow and compelling. While the
con side offered nuanced context and counter-points, its arguments were less tightly
organized, reducing overall persuasiveness.
```

## Full Debate Transcript

Topic: **Real Madrid vs Barcelona — which is better?** (1-round demo)

---

**PRO** *(research-analysis skill, 1 search call → 5 results)*

> Real Madrid is unequivocally the superior club when measured by historical achievement,
> global impact, and consistent excellence.
>
> 1. **Record European Success** — 15 UEFA Champions League titles vs Barcelona's 5.
> 2. **Domestic Supremacy** — 35 La Liga titles vs 27.
> 3. **Overall Trophy Haul** — 100+ major trophies vs ~95.
> 4. **Global Brand** — #1 Deloitte Football Money League 2023, #1 Forbes most valuable clubs.
> 5. **Player Legacy** — Di Stéfano, Puskás, Raúl, Ronaldo, Modrić.
>
> *References*: soccermag.com, livesoccertv.com, statista.com, deloitte.com, forbes.com

---

**CON** *(research-analysis + quality-standards skills, 2 search calls → 10 results)*

> While the pro side touts raw trophy counts, those numbers hide crucial context.
>
> 1. **European gap is historical** — Barcelona's 5 titles are all post-2006 (modern era); Real's extra 10 include 12 pre-1998 wins when competition was far weaker.
> 2. **Recent domestic dominance flips** — Barcelona won 10 La Liga titles 2005–2023 vs Real's 5.
> 3. **Trophy inflation** — Real's "100+" includes extinct regional competitions; Barcelona's 95 are higher-proportion modern honours.
> 4. **Financial gap is closing** — €30M revenue gap in 2022-23; Barcelona's fiscal reforms show long-term stability.
> 5. **La Masia vs Galáctico model** — Messi, Xavi, Iniesta, Busquets shaped modern football; Real buys stars rather than developing them.
>
> *References*: wikipedia.org, laliga.com, deloitte.com, uefa.com

---

**JUDGE** *(persuasion-scoring skill)*

> **Winner: PRO** — Pro 78 / Con 72
>
> The pro side presented a clear, well-structured argument with concrete statistics and
> logical sequencing. The con side offered nuanced counter-points but was less tightly
> organised, reducing persuasiveness.

---

## Agent Skills (Plugin System)

Skills are modular classes implementing `AgentSkill`. They inject instruction text and
(optionally) a native LLM tool call into agents at runtime.

| Skill | Agents | What it does |
|-------|--------|--------------|
| `research-analysis` | Pro, Con | Live web search; injects evidence-based reasoning instructions + search tool |
| `quality-standards` | Con | Critical evaluation; identifies fallacies and methodology weaknesses |
| `persuasion-scoring` | Judge | Scores arguments on persuasiveness 0–100; enforces no-tie rule |

### Adding a New Skill

1. Create `src/debate/skills/my_skill.py` implementing `AgentSkill`.
2. Register it in `skills/registry.py → default_registry()`.
3. Add the skill name to the relevant agent's `"skills"` list in `config/setup.json`.

### Adding a New LLM Provider

1. Create `src/debate/providers/my_provider.py` implementing `ILLMProvider.chat()`.
2. Register it in `sdk/provider_factory.py`.
3. Set `"provider": "my-provider"` in agent config.

## Token Cost Analysis

### Automatic Per-Round Tracking

Every debate automatically logs token usage and cost per turn. Tokens are captured via a **delta-snapshot** pattern: the provider's cumulative counter is read before and after each agent call, and the difference is attributed to that specific turn. This handles multi-step tool-call loops correctly.

The `run()` result includes a `cost_summary` dict:

```json
{
  "total_tokens": 6635,
  "total_cost_usd": 0.000994,
  "by_role": {
    "pro":   {"input_tokens": 1096, "output_tokens": 511,  "cost_usd": 0.000471},
    "con":   {"input_tokens": 1865, "output_tokens": 1227, "cost_usd": 0.001015},
    "judge": {"input_tokens": 1770, "output_tokens": 166,  "cost_usd": 0.000365}
  }
}
```

Pricing rates are configured in `config/setup.json` under the `"pricing"` key (per_1m_tokens, separate input/output rates per role).

### Live Run Results

Live run on `openai/gpt-oss-20b:free` (OpenRouter), 1 round, topic: Real Madrid vs Barcelona.

### Actual Token Usage (1 round, 2026-06-02)

| Agent | Input tokens | Output tokens | Total |
|-------|-------------|---------------|-------|
| Pro | 1,096 | 511 | 1,607 |
| Con | 1,865 | 1,227 | 3,092 |
| Judge | 1,770 | 166 | 1,936 |
| **Total** | **4,731** | **1,904** | **6,635** |

### Cost Per Model (1 round)

| Model | Input $/1M | Output $/1M | Estimated cost |
|-------|-----------|-------------|----------------|
| `gpt-oss-20b:free` (OpenRouter) | $0 | $0 | **$0.000** |
| GPT-4o-mini | $0.15 | $0.60 | **$0.0018** |
| GPT-4o | $2.50 | $10.00 | **$0.031** |
| Claude 3.5 Haiku | $0.80 | $4.00 | **$0.011** |
| Gemini 1.5 Flash | $0.075 | $0.30 | **$0.0009** |

### 5-Round Debate Estimate

Pro/Con scale linearly with rounds; Judge sees the full history once at the end (~5× input).
Estimated totals: **~22,800 input / ~9,100 output tokens**.

| Model | 5-round estimate |
|-------|-----------------|
| GPT-4o-mini | **~$0.009** |
| GPT-4o | **~$0.15** |
| Claude 3.5 Haiku | **~$0.055** |
| Gemini 1.5 Flash | **~$0.004** |

### Optimization Strategies

1. **Free-tier models** — OpenRouter free models cost $0; ideal for development and demos.
2. **Reduce rounds** — each round adds ~5,000 tokens; lower `max_rounds` in `config/setup.json`.
3. **Gemini Flash** — 10–30× cheaper than GPT-4o at comparable quality for debate tasks.
4. **Limit output** — lower `max_tokens_per_agent` to cap response size per turn.

## Tests & Quality

```
Baseline: 264 passed, 3 xfailed (pending readiness gates) · 97.4% coverage · final validation pending
```

Structured output contract enforcement, parent-controlled policy verification, and runtime safety
control verification are part of the Final Submission Readiness Roadmap — see `docs/TODO.md`.

Run tests:

```bash
uv run pytest --cov=src
```

Run linter:

```bash
uv run ruff check .
```

## Project Layout

```
orchestration-hw2/
├── src/
│   ├── main.py                   # Legacy shim → debate.main
│   └── debate/
│       ├── main.py               # Real entry point (uv run debate)
│       ├── agents/               # ProAgent, ConAgent, JudgeAgent, AgentBase
│       ├── cli/                  # TerminalMenu
│       ├── providers/            # OpenAI, Anthropic, Gemini + ILLMProvider
│       ├── sdk/                  # DebateSDK, ProviderFactory, AgentFactory
│       ├── services/             # Orchestrator, DebateState, PromptBuilder, Verdict
│       ├── shared/               # ConfigManager, LogManager, ApiGatekeeper, Watchdog, paths
│       └── skills/               # AgentSkill ABC + 3 concrete skills + SkillRegistry
├── tests/
│   ├── unit/                     # Module-level unit tests
│   └── integration/              # End-to-end debate flow
├── config/
│   ├── setup.json                # Main config (topic, models, rounds, rate limits)
│   ├── rate_limits.json          # Gatekeeper rate-limit profiles
│   └── logging_config.json       # Log rotation settings
├── docs/
│   ├── PRD.md                    # Product requirements
│   ├── PLAN.md                   # Architecture (C4, class hierarchy)
│   ├── TODO.md                   # Phase tracker
│   ├── PRD_agent_skills.md       # Skills plugin design
│   ├── PRD_debate_orchestration.md
│   ├── PRD_sdk.md
│   └── prompt_log/PROMPT_LOG.md  # AI-assisted development log
├── logs/                         # FIFO-rotated debate transcripts
├── pyproject.toml
├── uv.lock
└── .env-example
```

## Architecture Decisions

| ADR | Decision | Rationale |
|-----|----------|-----------|
| ADR-001 | Interface-based LLM provider abstraction | Provider-agnostic requirement |
| ADR-002 | JSON inter-agent communication | Structured, monitorable, token-efficient |
| ADR-003 | Judge as mediator — all messages flow through Judge | Homework requirement |
| ADR-004 | DuckDuckGo search (no API key) | Free, sufficient for citations |
| ADR-005 | Class-based Agent Skills plugin system | Configurable, composable, independently testable |