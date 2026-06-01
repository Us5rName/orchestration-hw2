"""Integration test for full debate flow."""

from unittest.mock import MagicMock

import pytest

from debate.services.orchestrator import DebateOrchestrator


@pytest.fixture
def mock_judge() -> MagicMock:
    """Return a mock JudgeAgent."""
    judge = MagicMock()
    judge.role = "judge"
    judge.think.return_value = {
        "winner": "pro",
        "pro_score": 80,
        "con_score": 70,
        "justification": "Pro presented stronger evidence",
    }
    return judge


@pytest.fixture
def mock_pro() -> MagicMock:
    """Return a mock ProAgent."""
    pro = MagicMock()
    pro.role = "pro"
    pro.think.return_value = {
        "content": "Pro argues with evidence",
        "references": ["http://example.com"],
    }
    return pro


@pytest.fixture
def mock_con() -> MagicMock:
    """Return a mock ConAgent."""
    con = MagicMock()
    con.role = "con"
    con.think.return_value = {"content": "Con challenges methodology", "references": []}
    return con


class TestFullDebateFlow:
    """Integration test for complete debate flow."""

    def test_full_debate_completes(
        self, mock_judge: MagicMock, mock_pro: MagicMock, mock_con: MagicMock
    ) -> None:
        """Full debate runs all rounds and produces verdict."""
        orchestrator = DebateOrchestrator(
            judge_agent=mock_judge,
            pro_agent=mock_pro,
            con_agent=mock_con,
            topic="AI is beneficial",
            max_rounds=3,
        )
        result = orchestrator.run()

        assert result["winner"] == "pro"
        assert result["pro_score"] == 80
        assert result["con_score"] == 70
        assert len(result["history"]) == 6  # 2 args * 3 rounds

    def test_history_contains_all_arguments(
        self, mock_judge: MagicMock, mock_pro: MagicMock, mock_con: MagicMock
    ) -> None:
        """Debate history contains all arguments from both sides."""
        orchestrator = DebateOrchestrator(
            judge_agent=mock_judge,
            pro_agent=mock_pro,
            con_agent=mock_con,
            topic="AI is beneficial",
            max_rounds=2,
        )
        orchestrator.run()

        pro_args = [h for h in orchestrator.state.history if h["agent"] == "pro"]
        con_args = [h for h in orchestrator.state.history if h["agent"] == "con"]
        assert len(pro_args) == 2
        assert len(con_args) == 2

    def test_state_is_complete_after_run(
        self, mock_judge: MagicMock, mock_pro: MagicMock, mock_con: MagicMock
    ) -> None:
        """DebateState is marked complete after run."""
        orchestrator = DebateOrchestrator(
            judge_agent=mock_judge,
            pro_agent=mock_pro,
            con_agent=mock_con,
            topic="AI is beneficial",
            max_rounds=2,
        )
        orchestrator.run()
        assert orchestrator.state.is_complete is True
