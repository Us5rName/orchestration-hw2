"""Integration test for full debate flow.

Uses ScriptedAgent so the integration layer tests orchestration wiring
(DebateOrchestrator + DebateState + verdict pipeline) without making
real LLM calls.  Vendor-specific provider behaviour is tested in the
unit/test_providers/ suite.
"""

from debate.services.orchestrator import DebateOrchestrator
from tests.fakes.agents import ScriptedAgent

PRO_RESPONSE = {"content": "Pro argues with evidence", "references": ["http://example.com"]}
CON_RESPONSE = {"content": "Con challenges methodology", "references": []}
JUDGE_RESPONSE = {
    "winner": "pro",
    "pro_score": 80,
    "con_score": 70,
    "justification": "Pro presented stronger evidence",
}


def _make_orchestrator(max_rounds: int = 3) -> DebateOrchestrator:
    return DebateOrchestrator(
        judge_agent=ScriptedAgent("judge", [JUDGE_RESPONSE] * 10),
        pro_agent=ScriptedAgent("pro", [PRO_RESPONSE] * 10),
        con_agent=ScriptedAgent("con", [CON_RESPONSE] * 10),
        topic="AI is beneficial",
        max_rounds=max_rounds,
    )


class TestFullDebateFlow:
    """Integration tests for the complete debate pipeline."""

    def test_full_debate_completes(self) -> None:
        """Full debate runs all rounds and produces verdict."""
        result = _make_orchestrator(3).run()
        assert result["winner"] == "pro"
        assert result["pro_score"] == 80
        assert result["con_score"] == 70
        assert len(result["history"]) == 6  # 2 args × 3 rounds

    def test_history_contains_all_arguments(self) -> None:
        """Debate history records arguments from both sides for every round."""
        orc = _make_orchestrator(2)
        orc.run()
        pro_args = [h for h in orc.state.history if h["agent"] == "pro"]
        con_args = [h for h in orc.state.history if h["agent"] == "con"]
        assert len(pro_args) == 2
        assert len(con_args) == 2

    def test_state_is_complete_after_run(self) -> None:
        """DebateState is marked complete after run()."""
        orc = _make_orchestrator(2)
        orc.run()
        assert orc.state.is_complete is True
