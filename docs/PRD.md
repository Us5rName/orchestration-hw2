# PRD — AI Debate System

## Overview

An AI debate system where two LLM-powered agents (Pro and Con) argue opposing sides of a chosen topic under the supervision of a third agent (Judge). The debate flows through the Judge, uses structured JSON communication, and produces a definitive winner based on persuasiveness — not factual correctness.

## Problem Statement

Need a system that demonstrates multi-agent AI orchestration with:
- Provider-agnostic LLM integration
- Structured debate with real contradiction
- Centralized API management (gatekeeper)
- SDK-based architecture
- Terminal-based operation

## Goals & Success Metrics

| Goal | Metric |
|------|--------|
| Functional debate | ≥10 rounds of argument → counter-argument |
| Real contradiction | Agents don't collapse into agreement |
| Judge decides winner | No ties allowed; persuasive scoring |
| LLM-agnostic | Works with OpenAI, Anthropic, Google, etc. |
| Code quality | 0 Ruff violations, ≥85% test coverage |

## Functional Requirements

### FR1: Three-Agent Architecture
- **Judge (Father)**: Orchestrates debate, enforces rules, decides winner
- **Pro Agent**: Argues one side of the topic
- **Con Agent**: Argues the opposing side

### FR2: Debate Flow
- All messages flow through the Judge: `Child → Judge → Child`
- JSON-structured communication
- Each agent must reference opponent's last argument
- Respectful, PC dialogue enforced

### FR3: Minimum 10 Rounds
- Configurable round count (default: 10)
- Each round = argument → counter-argument

### FR4: Internet Search
- Agents can search the internet for citations
- Search tool is mandatory for evidence-backed arguments

### FR5: Judge Scoring
- Judge scores persuasiveness, not factual correctness
- Differential scoring (e.g., 80%/70%) — no ties
- Final verdict with justification

### FR6: LLM Provider Agnostic
- Abstract LLM provider interface
- Configurable provider per agent
- Supports OpenAI, Anthropic, Google Gemini, etc.

### FR7: Terminal Menu Operation
- Interactive CLI menu for operation
- Options: start debate, view logs, configure, exit

### FR8: SDK Layer
- All business logic accessible through SDK
- CLI/GUI are thin presentation layers

## Non-Functional Requirements

| Requirement | Detail |
|-------------|--------|
| Timeouts | Every API request has configurable timeout |
| Watchdog | Keep-alive monitoring; restart failed processes |
| OOP | Class-based architecture with inheritance |
| TDD | Test-driven development with ≥85% coverage |
| Linter | Ruff with zero violations |
| Config | No hardcoded values — all in config files |
| Security | .env for secrets; .env-example committed |
| Logging | FIFO log rotation (configurable: files × lines) |
| Gatekeeper | Rate limiting, queuing, retries for all API calls |
| UV | Virtual environment via uv + pyproject.toml |

## Constraints

- Budget-limited users may reduce rounds from 10 → 5 (documented in README)
- Debate language: English or Hebrew (not Arabic)
- Must use real LLM calls (no hardcoded debate text)
- Must be operable from terminal

## Target Audience

University course submission — AI Orchestration, Dr. Sagol.
