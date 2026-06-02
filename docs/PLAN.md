# PLAN — AI Debate System Architecture

## C4 Model

### Context Diagram

```mermaid
graph TD
    User:::accent0 -->|Terminal CLI| System[System Debate]
    System -->|API Calls| OpenAI[OpenAI API]
    System -->|API Calls| Anthropic[Anthropic API]
    System -->|API Calls| Google[Google Gemini API]
    System -->|Search| Search[Search Engine]
```

### Container Diagram

```mermaid
graph TD
    CLI[Terminal CLI] -->|delegates| SDK[SDK Layer]
    SDK -->|orchestrates| DebateOrchestrator[Debate Orchestrator]
    SDK -->|resolves| SkillRegistry[Skill Registry]
    SkillRegistry -->|injects skills into| JudgeAgent[Judge Agent]
    SkillRegistry -->|injects skills into| ProAgent[Pro Agent]
    SkillRegistry -->|injects skills into| ConAgent[Con Agent]
    DebateOrchestrator -->|manages| JudgeAgent
    DebateOrchestrator -->|manages| ProAgent
    DebateOrchestrator -->|manages| ConAgent
    JudgeAgent -->|via| Gatekeeper[API Gatekeeper]
    ProAgent -->|via| Gatekeeper
    ConAgent -->|via| Gatekeeper
    Gatekeeper -->|rate-limited| LLMProviders[LLM Providers]
    ResearchAnalysisSkill -->|search| SearchTool[Search Tool]
    SDK -->|uses| Logger[Structured Logger]
    SDK -->|uses| ConfigManager[Config Manager]
    SDK -->|uses| Watchdog[Watchdog Monitor]
```

### Component Diagram

```mermaid
graph TD
    subgraph SDK
        DebateSDK[DebateSDK]
    end

    subgraph Domain
        DebateOrchestrator[DebateOrchestrator]
        AgentBase[Agent Base Class]
        JudgeAgent[JudgeAgent]
        ProAgent[ProAgent]
        ConAgent[ConAgent]
        DebateState[DebateState]
    end

    subgraph Skills
        AgentSkill[AgentSkill ABC]
        ResearchAnalysisSkill[ResearchAnalysisSkill]
        QualityStandardsSkill[QualityStandardsSkill]
        PersuasionScoringSkill[PersuasionScoringSkill]
        SkillRegistry[SkillRegistry]
    end

    subgraph Infrastructure
        LLMProvider[LLM Provider Interface]
        OpenAIProvider[OpenAIProvider]
        AnthropicProvider[AnthropicProvider]
        GeminiProvider[GeminiProvider]
        ApiGatekeeper[ApiGatekeeper]
        SearchService[SearchService]
    end

    subgraph Shared
        ConfigManager[ConfigManager]
        LogManager[LogManager]
        Watchdog[Watchdog]
    end

    DebateSDK --> DebateOrchestrator
    DebateSDK --> SkillRegistry
    SkillRegistry --> AgentSkill
    ResearchAnalysisSkill --> AgentSkill
    QualityStandardsSkill --> AgentSkill
    PersuasionScoringSkill --> AgentSkill
    DebateOrchestrator --> AgentBase
    JudgeAgent --> AgentBase
    ProAgent --> AgentBase
    ConAgent --> AgentBase
    AgentBase --> AgentSkill
    AgentBase --> LLMProvider
    OpenAIProvider --> LLMProvider
    AnthropicProvider --> LLMProvider
    GeminiProvider --> LLMProvider
    LLMProvider --> ApiGatekeeper
    ProAgent --> SearchService
    ConAgent --> SearchService
    DebateOrchestrator --> DebateState
    DebateOrchestrator --> Watchdog
    ApiGatekeeper --> ConfigManager
    DebateSDK --> LogManager
```

## Architecture Design

### OOP Class Hierarchy

```mermaid
graph TD
    subgraph Core
        AgentBase[AgentBase]
        JudgeAgent[JudgeAgent]
        ProAgent[ProAgent]
        ConAgent[ConAgent]
    end

    subgraph Skills
        AgentSkill[AgentSkill ABC]
        ResearchAnalysisSkill[ResearchAnalysisSkill]
        QualityStandardsSkill[QualityStandardsSkill]
        PersuasionScoringSkill[PersuasionScoringSkill]
        SkillRegistry[SkillRegistry]
    end

    subgraph Providers
        ILLMProvider[ILLMProvider Interface]
        OpenAIProvider[OpenAIProvider]
        AnthropicProvider[AnthropicProvider]
        GeminiProvider[GeminiProvider]
    end

    subgraph Services
        ApiGatekeeper[ApiGatekeeper]
        SearchService[SearchService]
        DebateOrchestrator[DebateOrchestrator]
        DebateState[DebateState]
    end

    subgraph Shared
        ConfigManager[ConfigManager]
        LogManager[LogManager]
        Watchdog[Watchdog]
    end

    subgraph SDK
        DebateSDK[DebateSDK]
    end

    subgraph CLI
        TerminalMenu[TerminalMenu]
    end

    JudgeAgent -->|extends| AgentBase
    ProAgent -->|extends| AgentBase
    ConAgent -->|extends| AgentBase
    ResearchAnalysisSkill -->|implements| AgentSkill
    QualityStandardsSkill -->|implements| AgentSkill
    PersuasionScoringSkill -->|implements| AgentSkill
    AgentBase -->|composes| AgentSkill
    SkillRegistry -->|holds| AgentSkill
    OpenAIProvider -->|implements| ILLMProvider
    AnthropicProvider -->|implements| ILLMProvider
    GeminiProvider -->|implements| ILLMProvider
    AgentBase -->|uses| ILLMProvider
    AgentBase -->|uses| ApiGatekeeper
    AgentBase -->|delegates search| AgentSkill
    ResearchAnalysisSkill -->|uses| SearchService
    DebateOrchestrator -->|uses| JudgeAgent
    DebateOrchestrator -->|uses| ProAgent
    DebateOrchestrator -->|uses| ConAgent
    DebateOrchestrator -->|uses| DebateState
    DebateOrchestrator -->|uses| Watchdog
    DebateSDK -->|uses| DebateOrchestrator
    DebateSDK -->|uses| LogManager
    TerminalMenu -->|uses| DebateSDK
```

### Key Classes

| Class | Responsibility |
|-------|---------------|
| `AgentBase` | Abstract base for all agents; LLM call, skill composition, prompt building, timeout |
| `JudgeAgent` | Enforces rules, scores persuasiveness, decides winner |
| `ProAgent` | Argues positive side; uses search for evidence |
| `ConAgent` | Argues negative side; uses search for evidence |
| `AgentSkill` | Abstract base for all agent skills; defines `name`, `get_instructions()`, and default no-op `search()` |
| `ResearchAnalysisSkill` | Injects evidence-driven instruction text; owns `SearchService` and implements `search()`; usable by any agent |
| `QualityStandardsSkill` | Injects critical-evaluation, fallacy-finding instruction text; usable by any agent |
| `PersuasionScoringSkill` | Injects persuasiveness-scoring, no-tie instruction text; usable by any agent |
| `SkillRegistry` | Maps skill name strings → `AgentSkill` instances; plugin registry |
| `ILLMProvider` | Interface for LLM providers |
| `OpenAIProvider` | OpenAI API implementation |
| `AnthropicProvider` | Anthropic API implementation |
| `GeminiProvider` | Google Gemini API implementation |
| `ApiGatekeeper` | Rate limiting, queuing, retries |
| `SearchService` | Internet search abstraction |
| `DebateOrchestrator` | Manages debate flow and rounds |
| `DebateState` | Tracks debate state, arguments, scores |
| `PromptBuilder` | Constructs debate prompts for agents |
| `Verdict` | Judge evaluation and result formatting |
| `DebateSDK` | Single entry point — wires all components |
| `ProviderFactory` | Creates LLM providers from config |
| `TerminalMenu` | CLI menu interface |
| `ConfigManager` | Loads and validates configuration |
| `LogManager` | Structured logging with FIFO rotation |
| `Watchdog` | Process monitoring and keep-alive |
| `TerminalMenu` | CLI menu interface |

### JSON Communication Format

```json
{
    "type": "argument",
    "agent": "pro",
    "round": 1,
    "content": "My argument here...",
    "references": ["source_url"],
    "timestamp": "2024-01-01T00:00:00Z"
}
```

### Configuration Schema

```json
{
    "version": "1.00",
    "debate": {
        "topic": "Real Madrid vs Barcelona - which is better?",
        "max_rounds": 10,
        "max_tokens_per_agent": 500,
        "request_timeout_seconds": 60
    },
    "agents": {
        "judge": {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "temperature": 0.3
        },
        "pro": {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "temperature": 0.7
        },
        "con": {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "temperature": 0.7
        }
    },
    "gatekeeper": {
        "requests_per_minute": 30,
        "requests_per_hour": 500,
        "max_retries": 3,
        "retry_delay_seconds": 5
    },
    "logging": {
        "max_files": 20,
        "max_lines_per_file": 500,
        "log_directory": "logs"
    }
}
```

## ADRs

### ADR-001: LLM Provider Abstraction
**Decision**: Use interface-based LLM provider abstraction
**Rationale**: LLM provider-agnostic requirement; allows swapping providers via config
**Trade-offs**: More initial code; simpler long-term maintenance

### ADR-002: JSON Communication
**Decision**: All inter-agent communication via JSON
**Rationale**: Structured, monitorable, token-efficient per requirements
**Trade-offs**: Less natural than free text; requires prompt engineering

### ADR-003: Judge as Mediator
**Decision**: All messages flow through Judge
**Rationale**: Requirement; allows Judge to enforce rules and prevent agreement

### ADR-004: Duckduckgo Search
**Decision**: Use DuckDuckGo for free, no-key search
**Rationale**: No API key needed; sufficient for citation purposes

### ADR-005: Class-Based Agent Skills Plugin Architecture
**Decision**: Agent skills are classes implementing `AgentSkill` ABC, registered in `SkillRegistry`,
and injected into agents via constructor
**Rationale**: Skills were previously hardcoded strings inside `_build_system_prompt()` — not
configurable, not composable, not independently testable. The extensibility skill requires a plugin
architecture; the modular-design skill requires independent testability; sdk-architecture requires
all wiring through the SDK. Class-based skills satisfy all three.
**Trade-offs**: More files than a single dict of strings; offset by testability and extensibility gains
**Alternatives rejected**:
- YAML/JSON text files: no type safety, no logic, cannot be unit-tested as classes
- Skill as a mixin on the agent: violates single responsibility, couples skill to agent class hierarchy

## Project Structure

```
skills-test/
├── src/
│   └── debate/
│       ├── __init__.py
│       ├── sdk/
│       │   ├── sdk.py
│       │   └── provider_factory.py
│       ├── services/
│       │   ├── orchestrator.py
│       │   ├── debate_state.py
│       │   ├── prompt_builder.py
│       │   ├── verdict.py
│       │   └── search_service.py
│       ├── agents/
│       │   ├── base_agent.py
│       │   ├── judge_agent.py
│       │   ├── pro_agent.py
│       │   └── con_agent.py
│       ├── skills/
│       │   ├── __init__.py
│       │   ├── base_skill.py
│       │   ├── research_analysis.py
│       │   ├── quality_standards.py
│       │   ├── persuasion_scoring.py
│       │   └── registry.py
│       ├── providers/
│       │   ├── base_provider.py
│       │   ├── openai_provider.py
│       │   ├── anthropic_provider.py
│       │   └── gemini_provider.py
│       ├── shared/
│       │   ├── gatekeeper.py
│       │   ├── config.py
│       │   ├── logger.py
│       │   └── watchdog.py
│       ├── cli/
│       │   └── menu.py  # TerminalMenu
│       └── constants.py
├── tests/
│   ├── unit/
│   │   ├── test_agents/
│   │   ├── test_skills/
│   │   ├── test_providers/
│   │   ├── test_services/
│   │   ├── test_shared/
│   │   └── test_sdk/
│   └── integration/
│       ├── test_debate_flow.py
│       └── conftest.py
├── config/
│   ├── setup.json
│   ├── rate_limits.json
│   └── logging_config.json
├── docs/
│   ├── PRD.md
│   ├── PLAN.md
│   ├── TODO.md
│   ├── PRD_sdk.md
│   ├── PRD_debate_orchestration.md
│   └── PRD_agent_skills.md
├── README.md
├── pyproject.toml
├── .env-example
├── .gitignore
└── src/main.py
```

## Phase 11 — Architecture Refactor Plan

### Why tests are refactored before production code

Tests are the specification. Before restructuring production code we must ensure the test suite
accurately describes the target architecture. If we refactor production code first, the existing
MagicMock-heavy tests will pass without actually verifying the new contracts — the mocks are too
permissive. Refactoring the test harness first (Branch 1) means every subsequent production
change is validated by tests that reflect the intended design, not just tests that happen to pass.

### Why provider contracts, typed config boundaries, and structured outputs are core architecture

Right now the system has three loosely-typed boundaries:

1. **Config boundary**: `ConfigManager.get()` returns raw dicts; callers do `.get("key", default)`
   everywhere, spreading knowledge of the config schema across the codebase. A typed config
   model (Branch 2) encodes the schema once and makes every caller statically verifiable.

2. **Provider boundary**: each provider returns a raw string and updates mutable internal counters.
   A `ProviderResult` contract (Branch 3) means orchestration code never needs to know which
   provider produced the result, and usage accounting is no longer side-effectful.

3. **Agent output boundary**: agents return dicts from `json.loads()`. Nothing validates that the
   winner field exists, that scores are integers, or that a tie was not returned. Structured output
   schemas (Branch 4) make invalid agent responses a hard, early failure rather than a silent
   downstream bug.

These three are architecture work, not polish — they determine how trustworthy the system is at
runtime and how safely it can be extended.

### Why the parent/judge must be the only communication router

The homework requirement and ADR-003 both state that all messages flow through the Judge.
Currently this is enforced by convention (the orchestrator calls agents in the right order) rather
than by structure (agents cannot call each other). Branch 5 makes the invariant structural:
`ProAgent` and `ConAgent` will have no reference to each other, and the communication policy
(`DebatePolicy`) will be an explicit, testable object rather than implicit orchestrator behaviour.
This also makes the system easier to extend: new policies (e.g. rebuttals, mediator interventions)
can be added without modifying agent classes.

### Why gatekeeper/watchdog infrastructure must be real or honestly documented

`ApiGatekeeper` and `Watchdog` are constructed and listed in the architecture diagrams, but
inspection of the runtime path shows they are not in the hot path of actual API calls or the
debate loop. This is a correctness gap: the system claims rate limiting and keep-alive monitoring
that does not actually fire. Branch 6 resolves this by either wiring them into the real path
(preferred) or documenting their current status as "future work" with explicit TODOs, so the
architecture documentation is honest about what the system actually does.
