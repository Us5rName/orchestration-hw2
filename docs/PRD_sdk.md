# PRD — SDK Architecture

## Overview

The SDK is the single entry point for all debate operations. It wires together configuration, providers, agents, the orchestrator, and infrastructure components (logger, gatekeeper, watchdog). All external consumers (CLI, GUI, REST) delegate to the SDK.

## Theoretical Background

The SDK follows the **Facade pattern** — it provides a unified interface to a complex subsystem. This ensures:
- Single point of integration for consumers
- Centralized dependency management
- Consistent configuration flow
- Separation of concerns between presentation and business logic

## Components

| Component | File | Responsibility |
|-----------|------|---------------|
| `DebateSDK` | `sdk/sdk.py` | Single entry point, wires all components |
| `ProviderFactory` | `sdk/provider_factory.py` | Creates LLM providers from config |
| `TerminalMenu` | `cli/menu.py` | CLI menu — thin presentation layer |

## Specific Requirements

### SDK-1: Configuration Loading
- SDK loads config from `config/setup.json` via ConfigManager
- All components initialized from config values
- No hardcoded values in SDK

### SDK-2: Provider Factory
- Creates providers based on config (`provider` field per agent)
- Reads API keys from environment variables
- Supports OpenAI, Anthropic, Gemini

### SDK-3: Agent Creation
- Creates JudgeAgent, ProAgent, ConAgent from config
- Each agent gets its own provider instance
- Agent parameters from config (model, temperature, timeout)

### SDK-4: Debate Execution
- `run_debate()` creates orchestrator and runs full debate
- Returns verdict dict with winner, scores, justification, history
- Logs debate start and completion

### SDK-5: Log Access
- `get_logs()` reads recent log lines from log file
- Configurable line count (default: 50)
- Returns message if no log file exists

## Expected I/O

### SDK Input
```json
{
    "config_path": "config/setup.json"
}
```

### SDK Output (run_debate)
```json
{
    "winner": "pro | con",
    "pro_score": 80,
    "con_score": 70,
    "justification": "string",
    "history": [
        {"agent": "pro", "round": 1, "content": "...", "references": []}
    ]
}
```

## Architecture

```
External Consumers (CLI / GUI / REST)
        |
        v
+-------+-------+
|  DebateSDK    |  <-- Single entry point
+-------+-------+
        |
   +----+----+
   |         |
   v         v
Provider   DebateOrchestrator
Factory     |
            v
       +----+----+
       |         |
       v         v
    Agents    DebateState
       |
       v
    LLM Providers
       |
       v
    ApiGatekeeper
```

## Constraints

- SDK must not exceed 150 lines of code
- No business logic in CLI — all delegates to SDK
- API keys from environment variables only
- All config values from JSON files

## Alternatives Considered

| Alternative | Rejected Because |
|-------------|-----------------|
| SDK as thin wrapper | Need centralized wiring of components |
| CLI creates components directly | Violates sdk-architecture skill |
| Hardcoded provider selection | Violates code-review-config skill |

## Success Criteria

- [x] SDK loads config and creates all components
- [x] Provider factory supports all 3 providers
- [x] CLI delegates all logic to SDK
- [x] All modules under 150 lines
- [x] 11 SDK tests, 0 Ruff violations
