# PRD — Agent Skills System

## Overview

Agents currently embed their skill identity as hardcoded strings inside `_build_system_prompt()`.
The skill is effectively invisible to the rest of the system — it cannot be configured, composed,
discovered, or tested in isolation. This PRD defines a proper **agent skills system**: modular,
pluggable behavior units that inject specialist instructions into an agent's system prompt and are
wired through the SDK and config.

## Problem Statement

The current approach has three concrete failure modes:

1. **Not configurable** — changing an agent's skill requires modifying Python source code.
2. **Not composable** — an agent can only have one hardcoded skill; multi-skill agents are impossible.
3. **Not testable** — the skill text is buried inside a method; it cannot be asserted on in isolation.

The **extensibility skill** requires a plugin architecture with clear interfaces and lifecycle hooks.
The **modular-design skill** requires every building block to have a well-defined input/output
contract and be independently testable. The **sdk-architecture skill** requires all wiring to flow
through the SDK. None of these requirements are currently met for agent skills.

## Goals & Success Metrics

| Goal | Metric |
|------|--------|
| Skills are modular | Each skill is an independent class with a single responsibility |
| Skills are configurable | Skill names assigned per-agent in `setup.json` |
| Skills are composable | An agent can hold and merge N skills |
| Skills are discoverable | `SkillRegistry` maps names → classes |
| Skills are testable | Each skill class tested in isolation |
| No hardcoded skill text | `_build_system_prompt()` reads from skill objects only |
| Code quality maintained | 0 Ruff violations, ≥85% test coverage |

## Functional Requirements

### SK-1: AgentSkill Abstract Base
- An abstract class `AgentSkill` with:
  - `name: str` — abstract property, unique kebab-case identifier (e.g. `"research-analysis"`)
  - `get_instructions() -> str` — abstract method, returns the skill's system-prompt injection text
  - `search(query: str) -> list[str]` — concrete method, default returns `[]`; override in skills
    that support live internet search. Returns formatted citation strings ready for prompt injection.
- Lives in `src/debate/skills/base_skill.py`
- Max 50 lines

### SK-2: Concrete Skill Implementations
Three skill classes, each independently usable by any agent:

| Class | Name | Instruction Focus | Has Search |
|-------|------|-------------------|------------|
| `ResearchAnalysisSkill` | `research-analysis` | Evidence, data, citations, studies | Yes — via `SearchService` |
| `QualityStandardsSkill` | `quality-standards` | Fallacies, methodology, rigor | No |
| `PersuasionScoringSkill` | `persuasion-scoring` | Score by persuasiveness, no ties | No |

Each in its own file under `src/debate/skills/`. Max 60 lines each.

Skills have **role semantics** — not every skill is appropriate for every agent:

| Skill | Judge | Pro | Con |
|-------|-------|-----|-----|
| `research-analysis` | ✗ not relevant | ✓ | ✓ |
| `quality-standards` | ✗ not relevant | ✓ | ✓ |
| `persuasion-scoring` | ✓ | ✗ not relevant | ✗ not relevant |

Debater agents (Pro, Con) build and challenge arguments — research and critical evaluation apply.
The Judge scores and decides — persuasion scoring applies; gathering evidence or critiquing
methodology is not its role.

Valid configurations for debaters (Pro and Con):
- `["research-analysis"]` — evidence-driven with live search
- `["quality-standards"]` — pure logical critique, no search
- `["research-analysis", "quality-standards"]` — searches for evidence AND applies critical evaluation

`ResearchAnalysisSkill` accepts a `SearchService` in its constructor. This replaces the current
direct dependency `ProAgent → SearchService` with `ResearchAnalysisSkill → SearchService`,
keeping search as a capability owned by the skill rather than the agent. When multiple agents
are configured with `research-analysis`, each receives its own `ResearchAnalysisSkill` instance
backed by the shared (stateless) `SearchService`.

### SK-3: SkillRegistry
- A `SkillRegistry` class that maps skill name strings → `AgentSkill` instances
- Lives in `src/debate/skills/registry.py`
- API:
  - `register(skill: AgentSkill) -> None`
  - `get(name: str) -> AgentSkill` — raises `KeyError` for unknown names
  - `list_names() -> list[str]`
- Pre-populated with the three built-in skills via `default_registry()` factory
- Max 60 lines

### SK-4: Config Schema Extension
Add `skills` key to each agent in `config/setup.json`:

```json
"agents": {
    "judge": { "provider": "openai", "model": "gpt-4o-mini",
               "temperature": 0.3, "skills": ["persuasion-scoring"] },
    "pro":   { "provider": "openai", "model": "gpt-4o-mini",
               "temperature": 0.7, "skills": ["research-analysis"] },
    "con":   { "provider": "openai", "model": "gpt-4o-mini",
               "temperature": 0.7, "skills": ["research-analysis", "quality-standards"] }
}
```

`skills` is a list — any agent can hold any combination of skills. An empty list `[]` is valid
(agent falls back to its hardcoded base prompt). Validated by `ConfigValidator`.

### SK-5: AgentBase Skill Composition
- `AgentBase.__init__` accepts `skills: list[AgentSkill]` (default `[]`)
- `_build_skill_block() -> str` — concatenates `skill.get_instructions()` for all skills
- `_build_system_prompt()` in concrete agents calls `_build_skill_block()` instead of
  embedding raw text
- No change to `think()` or `_parse_response()` — skill injection is purely at prompt-build time

### SK-6: SDK Wiring
- `ProviderFactory` (or a new `SkillFactory`) resolves skill names from agent config
  using the `SkillRegistry`
- `DebateSDK._create_agents()` passes resolved skill lists to agent constructors
- No skill resolution logic outside the SDK layer

### SK-8: Skill–Role Validation
- `ConfigValidator` enforces role semantics at startup:
  - Judge config must not include `research-analysis` or `quality-standards`
  - Pro/Con config must not include `persuasion-scoring`
- Violation raises `ValueError` with a clear message before any API call is made
- Tested in `test_config_validator.py`

### SK-7: Search Moved into ResearchAnalysisSkill
`ProAgent` currently calls `SearchService` directly. After this phase, search is a capability
**owned by the skill**, not the agent:

- `ResearchAnalysisSkill.__init__` accepts a `SearchService` instance
- `ResearchAnalysisSkill.search(query)` delegates to `SearchService.search()` and returns
  formatted citation strings (e.g. `"[title] href"`)
- `AgentBase` gains a `search(query: str) -> list[str]` method that iterates `self.skills` and
  returns results from the first skill whose `search()` returns non-empty results
- `ProAgent` calls `self.search(query)` — no direct import of `SearchService`
- `ConAgent` has no search-capable skill; its `search()` call returns `[]` (no-op)
- `DebateSDK` passes the existing `SearchService` instance into `ResearchAnalysisSkill` at
  construction time — zero new infrastructure required

## Non-Functional Requirements

| Requirement | Detail |
|-------------|--------|
| File size | Max 150 lines per file (skills are small — target ≤60 lines each) |
| Testability | Each skill, the registry, and AgentBase skill composition tested in isolation |
| No hardcoding | Skill text lives exclusively in skill classes; zero duplication |
| Extensibility | Adding a new skill = one new class + one `registry.register()` call |
| Backwards compat | `AgentBase(skills=[])` works identically to today when skills list is empty |

## Expected I/O

### SkillRegistry.get(name)
- **Input**: `name: str` (e.g. `"research-analysis"`)
- **Output**: `AgentSkill` instance
- **Edge case**: unknown name → `KeyError` with message listing valid names

### AgentBase._build_skill_block()
- **Input**: `self.skills: list[AgentSkill]`
- **Output**: `str` — newline-joined skill instructions, empty string when list is empty

### AgentBase.think(prompt)
- **Input / Output**: unchanged from today

## Constraints & Alternatives Considered

**Why not load skills from YAML/JSON text files?**
Text files cannot be unit-tested as classes, cannot have logic, and cannot be imported with type
safety. Class-based skills are the modular-design and extensibility standard.

**Why not make search a skill?**
Search is a tool call with side effects (network I/O). Skills are stateless prompt injections.
Mixing the two would violate single responsibility. Search stays as `SearchService`.

**Why SkillRegistry instead of direct imports?**
Registry decouples the agent from the concrete skill class, enabling external skill packages and
config-driven assignment without changing agent source code. This follows the extensibility plugin
architecture pattern.

## Success Criteria

| ID | Criterion | Test |
|----|-----------|------|
| SK-1 | `AgentSkill` ABC enforces `name` and `get_instructions()` | `test_base_skill.py` |
| SK-2 | Each concrete skill returns non-empty, unique instruction text | `test_skills.py` |
| SK-2b | `ResearchAnalysisSkill.search()` returns formatted citations; others return `[]` | `test_skills.py` |
| SK-3 | Registry raises `KeyError` for unknown name; returns correct instance for known | `test_registry.py` |
| SK-4 | Config with `skills` list loads and validates without error | `test_config_validator.py` |
| SK-5 | `_build_skill_block()` concatenates multiple skill texts | `test_base_agent.py` |
| SK-6 | SDK passes correct skill objects to agents based on config | `test_sdk.py` |
| SK-8 | `ConfigValidator` rejects judge with debater skills and vice versa | `test_config_validator.py` |
| All | 0 Ruff violations, ≥85% coverage | CI / `pytest --cov` |
