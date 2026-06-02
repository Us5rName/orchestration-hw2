"""Tests for DebateOrchestrator.

Uses ScriptedAgent (typed fake) instead of bare MagicMock so tests
verify orchestrator routing logic, not mock wiring.

Architecture-intent tests for constraints not yet enforced in
production are marked xfail with a reference to the branch that will
implement them (Branch 4 — structured outputs, Branch 5 — state machine).
"""

import pytest

from debate.services.orchestrator import DebateOrchestrator
from tests.fakes.agents import ScriptedAgent


# ---------------------------------------------------------------------------
# Fixtures
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


# ---------------------------------------------------------------------------
# Architecture-intent tests
# ---------------------------------------------------------------------------

class TestOrchestratorArchitecture:
    """Structural constraints for the parent-controlled debate model.

    Tests that currently pass verify constraints already true in production.
    Tests marked xfail describe constraints that Branch 4/5 will enforce.
    """

    def test_child_agents_have_no_direct_reference_to_each_other(
        self, orchestrator: DebateOrchestrator
    ) -> None:
        """Pro and con agents hold no instance-level reference to each other."""
        pro_id = id(orchestrator.pro)
        con_id = id(orchestrator.con)
        for val in vars(orchestrator.pro).values():
            assert id(val) != con_id, "pro holds a direct reference to con"
        for val in vars(orchestrator.con).values():
            assert id(val) != pro_id, "con holds a direct reference to pro"

    def test_orchestrator_is_sole_caller_of_agent_think(
        self, judge: ScriptedAgent, pro: ScriptedAgent, con: ScriptedAgent
    ) -> None:
        """After run(), think() was called exactly once per round per agent.

        Pro and con are called max_rounds times each; judge is called once.
        This verifies the orchestrator drives all communication — agents
        never call each other.
        """
        orc = DebateOrchestrator(
            judge_agent=judge, pro_agent=pro, con_agent=con,
            topic="Test", max_rounds=2,
        )
        orc.run()
        assert pro._idx == 2
        assert con._idx == 2
        assert judge._idx == 1

    @pytest.mark.xfail(
        reason="Branch 4 will reject tied scores — orchestrator does not yet validate",
        strict=False,
    )
    def test_judge_tie_is_rejected(
        self, pro: ScriptedAgent, con: ScriptedAgent
    ) -> None:
        """A judge verdict with equal pro and con scores must be rejected."""
        tie_judge = ScriptedAgent("judge", [
            {"winner": "pro", "pro_score": 75, "con_score": 75, "justification": "draw"}
        ] * 5)
        orc = DebateOrchestrator(
            judge_agent=tie_judge, pro_agent=pro, con_agent=con,
            topic="Test", max_rounds=1,
        )
        result = orc.run()
        assert result["pro_score"] != result["con_score"]

    @pytest.mark.xfail(
        reason="Branch 4 will validate agent output — invalid JSON not yet rejected",
        strict=False,
    )
    def test_invalid_agent_output_raises(
        self, judge: ScriptedAgent, con: ScriptedAgent
    ) -> None:
        """Malformed agent output must raise rather than silently propagate."""
        bad_pro = ScriptedAgent("pro", [{"content": "not-json-at-all \x00\x01"}] * 5)
        orc = DebateOrchestrator(
            judge_agent=judge, pro_agent=bad_pro, con_agent=con,
            topic="Test", max_rounds=1,
        )
        with pytest.raises((ValueError, KeyError)):
            orc.run()

    @pytest.mark.xfail(
        reason="Branch 5 will enforce judge routing — winner validation not yet structural",
        strict=False,
    )
    def test_winner_must_be_pro_or_con(
        self, pro: ScriptedAgent, con: ScriptedAgent
    ) -> None:
        """Judge verdict winner must be 'pro' or 'con', not an arbitrary string."""
        bad_judge = ScriptedAgent("judge", [
            {"winner": "nobody", "pro_score": 80, "con_score": 70, "justification": "?"}
        ] * 5)
        orc = DebateOrchestrator(
            judge_agent=bad_judge, pro_agent=pro, con_agent=con,
            topic="Test", max_rounds=1,
        )
        result = orc.run()
        assert result["winner"] in ("pro", "con")
