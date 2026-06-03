"""Tests for DebateOrchestrator — initialization, round execution, and full run.

Uses ScriptedAgent (typed fake) instead of bare MagicMock so tests
verify orchestrator routing logic, not mock wiring.
"""

import pytest

from debate.services.orchestrator import DebateOrchestrator
from tests.fakes.agents import ScriptedAgent

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

PRO_RESPONSE = {"content": "Pro argues the point.", "references": []}
CON_RESPONSE = {"content": "Con challenges the claim.", "references": []}
JUDGE_RESPONSE = {
    "winner": "pro",
    "pro_score": 80,
    "con_score": 70,
    "justification": "Pro was more persuasive.",
}


@pytest.fixture
def judge() -> ScriptedAgent:
    return ScriptedAgent("judge", [JUDGE_RESPONSE] * 10)


@pytest.fixture
def pro() -> ScriptedAgent:
    return ScriptedAgent("pro", [PRO_RESPONSE] * 10)


@pytest.fixture
def con() -> ScriptedAgent:
    return ScriptedAgent("con", [CON_RESPONSE] * 10)


@pytest.fixture
def orchestrator(judge: ScriptedAgent, pro: ScriptedAgent, con: ScriptedAgent) -> DebateOrchestrator:
    return DebateOrchestrator(
        judge_agent=judge,
        pro_agent=pro,
        con_agent=con,
        topic="AI is beneficial",
        max_rounds=3,
    )


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

class TestOrchestratorInit:
    """Orchestrator stores configuration and creates initial state."""

    def test_creates_debate_state(self, orchestrator: DebateOrchestrator) -> None:
        assert orchestrator.state is not None

    def test_state_has_correct_topic(self, orchestrator: DebateOrchestrator) -> None:
        assert orchestrator.state.topic == "AI is beneficial"

    def test_state_has_correct_max_rounds(self, orchestrator: DebateOrchestrator) -> None:
        assert orchestrator.state.max_rounds == 3

    def test_agents_stored(self, orchestrator: DebateOrchestrator) -> None:
        assert orchestrator.judge is not None
        assert orchestrator.pro is not None
        assert orchestrator.con is not None

    def test_invalid_max_rounds_raises(
        self, judge: ScriptedAgent, pro: ScriptedAgent, con: ScriptedAgent
    ) -> None:
        with pytest.raises(ValueError):
            DebateOrchestrator(
                judge_agent=judge, pro_agent=pro, con_agent=con,
                topic="Test", max_rounds=0,
            )


# ---------------------------------------------------------------------------
# Round execution
# ---------------------------------------------------------------------------

class TestOrchestratorRunRound:
    """A single debate round records both arguments in order."""

    def test_run_round_calls_pro_then_con(self, orchestrator: DebateOrchestrator) -> None:
        orchestrator.run_round()
        args = [h["agent"] for h in orchestrator.state.history]
        assert args == ["pro", "con"]

    def test_run_round_adds_to_history(self, orchestrator: DebateOrchestrator) -> None:
        orchestrator.run_round()
        assert len(orchestrator.state.history) == 2
        assert orchestrator.state.current_round == 1

    def test_run_round_with_override(self, orchestrator: DebateOrchestrator) -> None:
        orchestrator.run_round(round_number=5)
        assert orchestrator.state.current_round == 5

    def test_run_round_includes_round_cost(self, orchestrator: DebateOrchestrator) -> None:
        result = orchestrator.run_round()
        assert "round_cost" in result
        assert "total_cost_usd" in result["round_cost"]
        assert "breakdown" in result["round_cost"]


# ---------------------------------------------------------------------------
# Full debate run
# ---------------------------------------------------------------------------

class TestOrchestratorRun:
    """Full run completes all rounds and returns a verdict."""

    def test_run_completes_all_rounds(self, orchestrator: DebateOrchestrator) -> None:
        result = orchestrator.run()
        assert result["winner"] == "pro"
        assert len(orchestrator.state.history) == 6  # 2 args × 3 rounds

    def test_run_result_includes_cost_summary(self, orchestrator: DebateOrchestrator) -> None:
        result = orchestrator.run()
        assert "cost_summary" in result
        summary = result["cost_summary"]
        assert "total_tokens" in summary
        assert "total_cost_usd" in summary
        assert "by_role" in summary
