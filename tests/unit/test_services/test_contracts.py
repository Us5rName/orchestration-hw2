"""Tests for structured output contracts (AgentResponse, JudgeDecision)."""

import pytest

from debate.services.contracts import (
    AgentResponse,
    JudgeDecision,
    agent_response_from_dict,
    judge_decision_from_dict,
    validate_agent_dict,
    validate_judge_dict,
)


# ---------------------------------------------------------------------------
# AgentResponse
# ---------------------------------------------------------------------------

class TestAgentResponse:
    """AgentResponse validates content and field types on construction."""

    def test_valid_plain_text(self) -> None:
        r = AgentResponse(content="Hello world")
        assert r.content == "Hello world"

    def test_valid_with_references(self) -> None:
        r = AgentResponse(content="Arg", references=["src1"])
        assert r.references == ["src1"]

    def test_valid_with_metadata(self) -> None:
        r = AgentResponse(content="Arg", metadata={"round": 1})
        assert r.metadata["round"] == 1

    def test_empty_content_raises(self) -> None:
        with pytest.raises(ValueError, match="non-empty"):
            AgentResponse(content="")

    def test_whitespace_only_content_raises(self) -> None:
        with pytest.raises(ValueError, match="non-empty"):
            AgentResponse(content="   ")

    def test_null_byte_in_content_raises(self) -> None:
        with pytest.raises(ValueError, match="control characters"):
            AgentResponse(content="hello\x00world")

    def test_control_char_in_content_raises(self) -> None:
        with pytest.raises(ValueError, match="control characters"):
            AgentResponse(content="not-json-at-all \x00\x01")

    def test_references_must_be_list(self) -> None:
        with pytest.raises(ValueError, match="list"):
            AgentResponse(content="ok", references="not-a-list")  # type: ignore[arg-type]

    def test_metadata_must_be_dict(self) -> None:
        with pytest.raises(ValueError, match="dict"):
            AgentResponse(content="ok", metadata=[])  # type: ignore[arg-type]

    def test_newlines_in_content_are_allowed(self) -> None:
        r = AgentResponse(content="line1\nline2")
        assert "line1" in r.content

    def test_tab_in_content_is_allowed(self) -> None:
        r = AgentResponse(content="col1\tcol2")
        assert r.content == "col1\tcol2"


# ---------------------------------------------------------------------------
# agent_response_from_dict
# ---------------------------------------------------------------------------

class TestAgentResponseFromDict:
    """agent_response_from_dict parses and validates raw response dicts."""

    def test_valid_json_response(self) -> None:
        d = {"content": "Pro argues.", "references": ["ref1"], "agent": "pro"}
        r = agent_response_from_dict(d)
        assert r.content == "Pro argues."
        assert r.role == "pro"
        assert r.references == ["ref1"]

    def test_plain_text_response(self) -> None:
        d = {"content": "Simple response."}
        r = agent_response_from_dict(d)
        assert r.content == "Simple response."

    def test_empty_content_raises(self) -> None:
        with pytest.raises(ValueError):
            agent_response_from_dict({"content": ""})

    def test_missing_content_raises(self) -> None:
        with pytest.raises(ValueError):
            agent_response_from_dict({})

    def test_control_chars_raise(self) -> None:
        with pytest.raises(ValueError):
            agent_response_from_dict({"content": "bad\x00content"})

    def test_validate_agent_dict_function(self) -> None:
        validate_agent_dict({"content": "valid"})

    def test_validate_agent_dict_raises_on_empty(self) -> None:
        with pytest.raises(ValueError):
            validate_agent_dict({"content": ""})


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
