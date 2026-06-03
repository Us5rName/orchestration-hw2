"""Tests for structured output contracts — JudgeDecision."""

import pytest

from debate.services.contracts import (
    JudgeDecision,
    judge_decision_from_dict,
    validate_judge_dict,
)

# ---------------------------------------------------------------------------
# JudgeDecision
# ---------------------------------------------------------------------------

class TestJudgeDecision:
    """JudgeDecision validates winner, scores, and reasoning on construction."""

    def test_valid_pro_winner(self) -> None:
        d = JudgeDecision(winner="pro", pro_score=80, con_score=70, reasoning_summary="Better.")
        assert d.winner == "pro"

    def test_valid_con_winner(self) -> None:
        d = JudgeDecision(winner="con", pro_score=60, con_score=75, reasoning_summary="Stronger.")
        assert d.winner == "con"

    def test_invalid_winner_raises(self) -> None:
        with pytest.raises(ValueError, match="'pro' or 'con'"):
            JudgeDecision(winner="nobody", pro_score=80, con_score=70, reasoning_summary="?")

    def test_tie_raises(self) -> None:
        with pytest.raises(ValueError, match="tie"):
            JudgeDecision(winner="pro", pro_score=75, con_score=75, reasoning_summary="draw")

    def test_empty_reasoning_raises(self) -> None:
        with pytest.raises(ValueError, match="non-empty"):
            JudgeDecision(winner="pro", pro_score=80, con_score=70, reasoning_summary="")

    def test_whitespace_reasoning_raises(self) -> None:
        with pytest.raises(ValueError, match="non-empty"):
            JudgeDecision(winner="pro", pro_score=80, con_score=70, reasoning_summary="  ")

    def test_rule_violations_default_empty(self) -> None:
        d = JudgeDecision(winner="pro", pro_score=80, con_score=70, reasoning_summary="ok")
        assert d.rule_violations == []

    def test_rule_violations_must_be_list(self) -> None:
        with pytest.raises(ValueError, match="list"):
            JudgeDecision(
                winner="pro", pro_score=80, con_score=70,
                reasoning_summary="ok", rule_violations="bad",  # type: ignore[arg-type]
            )

    def test_non_numeric_pro_score_raises(self) -> None:
        with pytest.raises(ValueError, match="numeric"):
            JudgeDecision(
                winner="pro", pro_score="high", con_score=70,  # type: ignore[arg-type]
                reasoning_summary="ok",
            )

    def test_non_numeric_con_score_raises(self) -> None:
        with pytest.raises(ValueError, match="numeric"):
            JudgeDecision(
                winner="pro", pro_score=80, con_score="low",  # type: ignore[arg-type]
                reasoning_summary="ok",
            )


# ---------------------------------------------------------------------------
# judge_decision_from_dict
# ---------------------------------------------------------------------------

class TestJudgeDecisionFromDict:
    """judge_decision_from_dict parses and validates raw verdict dicts."""

    def test_valid_verdict_with_justification(self) -> None:
        d = {"winner": "pro", "pro_score": 80, "con_score": 70, "justification": "Better."}
        dec = judge_decision_from_dict(d)
        assert dec.winner == "pro"
        assert dec.reasoning_summary == "Better."

    def test_valid_verdict_with_reasoning_summary(self) -> None:
        d = {"winner": "con", "pro_score": 60, "con_score": 75, "reasoning_summary": "Stronger."}
        dec = judge_decision_from_dict(d)
        assert dec.reasoning_summary == "Stronger."

    def test_invalid_winner_raises(self) -> None:
        with pytest.raises(ValueError):
            judge_decision_from_dict(
                {"winner": "nobody", "pro_score": 80, "con_score": 70, "justification": "?"}
            )

    def test_tie_raises(self) -> None:
        with pytest.raises(ValueError):
            judge_decision_from_dict(
                {"winner": "pro", "pro_score": 75, "con_score": 75, "justification": "draw"}
            )

    def test_missing_reasoning_raises(self) -> None:
        with pytest.raises(ValueError):
            judge_decision_from_dict({"winner": "pro", "pro_score": 80, "con_score": 70})

    def test_validate_judge_dict_function(self) -> None:
        validate_judge_dict(
            {"winner": "pro", "pro_score": 80, "con_score": 70, "justification": "ok"}
        )

    def test_validate_judge_dict_raises_on_invalid_winner(self) -> None:
        with pytest.raises(ValueError):
            validate_judge_dict(
                {"winner": "tie", "pro_score": 80, "con_score": 70, "justification": "?"}
            )
