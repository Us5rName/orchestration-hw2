"""Tests for verdict module."""

from unittest.mock import MagicMock

from debate.services.debate_state import DebateState
from debate.services.verdict import decide_winner, format_result, record_verdict


class TestDecideWinner:
    """Test decide_winner function."""

    def test_calls_judge_think(self) -> None:
        """decide_winner calls judge.think with verdict prompt."""
        judge = MagicMock()
        judge.think.return_value = {
            "winner": "pro", "pro_score": 80, "con_score": 70,
            "justification": "Pro was more persuasive.",
        }
        state = DebateState(topic="Test", max_rounds=3)
        result = decide_winner(judge, state)
        judge.think.assert_called_once()
        assert result["winner"] == "pro"


class TestRecordVerdict:
    """Test record_verdict function."""

    def test_records_verdict_in_state(self) -> None:
        """record_verdict updates state with verdict."""
        state = DebateState(topic="Test", max_rounds=3)
        verdict = {"winner": "con", "pro_score": 60, "con_score": 75}
        record_verdict(state, verdict)
        assert state.winner == "con"
        assert state.pro_score == 60
        assert state.con_score == 75


class TestFormatResult:
    """Test format_result function."""

    def test_formats_complete_result(self) -> None:
        """format_result returns complete result dict."""
        verdict = {"winner": "pro", "pro_score": 80, "con_score": 70, "justification": "Better"}
        history = [{"agent": "pro", "round": 1, "content": "Arg", "references": []}]
        result = format_result(verdict, history)
        assert result["winner"] == "pro"
        assert result["justification"] == "Better"
        assert result["history"] == history
