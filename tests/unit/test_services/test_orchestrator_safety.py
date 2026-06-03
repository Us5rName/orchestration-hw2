"""Tests for DebateOrchestrator — parent-controlled policy and safety constraints.

Tests that currently pass verify constraints already enforced in production.
Tests marked xfail describe constraints that Branch 4/5 will enforce.
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

    def test_judge_tie_is_rejected(
        self, pro: ScriptedAgent, con: ScriptedAgent
    ) -> None:
        """A judge verdict with equal pro and con scores must raise ValueError."""
        tie_judge = ScriptedAgent("judge", [
            {"winner": "pro", "pro_score": 75, "con_score": 75, "justification": "draw"}
        ] * 5)
        orc = DebateOrchestrator(
            judge_agent=tie_judge, pro_agent=pro, con_agent=con,
            topic="Test", max_rounds=1,
        )
        with pytest.raises(ValueError, match="tie"):
            orc.run()

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
        with pytest.raises(ValueError, match="pro.*con|con.*pro"):
            orc.run()
