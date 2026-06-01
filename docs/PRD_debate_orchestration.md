# PRD — Debate Orchestration Mechanism

## Overview

The debate orchestration mechanism coordinates three AI agents (Pro, Con, Judge) through a structured multi-round debate. It manages state, constructs prompts, and produces a final verdict.

## Theoretical Background

The system implements a **mediated debate pattern** where:
- All arguments flow through a central orchestrator
- A judge agent evaluates persuasiveness (not factual correctness)
- Structured JSON communication ensures machine-readability
- Round-based progression enables incremental argumentation

## Components

| Component | File | Responsibility |
|-----------|------|---------------|
| `DebateState` | `debate_state.py` | Tracks rounds, history, scores, winner |
| `DebateOrchestrator` | `orchestrator.py` | Coordinates rounds and agents |
| `PromptBuilder` | `prompt_builder.py` | Constructs prompts for each agent |
| `Verdict` | `verdict.py` | Judge evaluation and result formatting |

## Specific Requirements

### ORC-1: Round Management
- Each round consists of one Pro argument + one Con counter-argument
- Rounds are numbered sequentially starting from 1
- Maximum rounds configurable (default: 10)

### ORC-2: Argument History
- All arguments stored with agent, round, content, references
- History accessible for judge evaluation
- References from search citations preserved

### ORC-3: Prompt Construction
- Pro prompts include Con's last argument to counter
- Con prompts include Pro's argument to counter
- Opening prompts have no counter-context

### ORC-4: Verdict
- Judge evaluates persuasiveness, not factual correctness
- Differential scoring (e.g., 80% vs 70%)
- No ties allowed
- JSON response with winner, scores, justification

## Expected I/O

### Input
```json
{
    "topic": "string",
    "max_rounds": 10,
    "judge_agent": "AgentBase",
    "pro_agent": "AgentBase",
    "con_agent": "AgentBase"
}
```

### Output
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

## Performance Metrics

| Metric | Target |
|--------|-------|
| Max rounds | 10 (configurable) |
| Arguments per round | 2 (pro + con) |
| Total API calls per debate | 2 * max_rounds + 1 (judge) |

## Constraints

- `max_rounds` must be >= 1
- All agents must implement `AgentBase` interface
- Judge must respond in JSON format
- No ties allowed in final verdict

## Alternatives Considered

| Alternative | Rejected Because |
|-------------|-----------------|
| Direct agent communication | No central control; harder to monitor |
| Single prompt debate | No incremental argumentation; less persuasive |
| Fact-based scoring | Requires fact-checking; out of scope |

## Success Criteria

- [x] Orchestrator runs full debate with configurable rounds
- [x] All arguments recorded in history
- [x] Judge produces verdict with no ties
- [x] All modules under 150 lines
- [x] 100% test coverage for services
