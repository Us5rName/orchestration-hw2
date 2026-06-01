"""Tests for prompt_builder module."""

from debate.services.debate_state import DebateState
from debate.services.prompt_builder import (
    build_con_prompt,
    build_debate_summary,
    build_pro_prompt,
    build_verdict_prompt,
    get_last_argument,
)


class TestBuildProPrompt:
    """Test pro prompt building."""

    def test_opening_prompt_no_context(self) -> None:
        """Opening prompt when no previous CON argument."""
        state = DebateState(topic="Test", max_rounds=3)
        state.current_round = 1
        prompt = build_pro_prompt(state)
        assert "opening PRO argument" in prompt

    def test_counter_prompt_with_context(self) -> None:
        """Counter prompt includes CON argument."""
        state = DebateState(topic="Test", max_rounds=3)
        state.current_round = 2
        state.record_argument(agent="con", content="Con says no")
        prompt = build_pro_prompt(state)
        assert "Counter the following CON argument" in prompt
        assert "Con says no" in prompt


class TestBuildConPrompt:
    """Test con prompt building."""

    def test_con_prompt_includes_pro_content(self) -> None:
        """Con prompt includes pro's argument."""
        state = DebateState(topic="Test", max_rounds=3)
        state.current_round = 1
        prompt = build_con_prompt(state, {"content": "Pro says yes"})
        assert "Counter the following PRO argument" in prompt
        assert "Pro says yes" in prompt


class TestGetLastArgument:
    """Test retrieving last argument."""

    def test_returns_last_argument(self) -> None:
        """Returns the last argument from specified agent."""
        state = DebateState(topic="Test", max_rounds=3)
        state.record_argument(agent="pro", content="First")
        state.record_argument(agent="con", content="Counter")
        state.record_argument(agent="pro", content="Second")
        assert get_last_argument(state, "pro") == "Second"

    def test_returns_empty_when_none(self) -> None:
        """Returns empty string when no arguments exist."""
        state = DebateState(topic="Test", max_rounds=3)
        assert get_last_argument(state, "pro") == ""


class TestBuildDebateSummary:
    """Test debate summary building."""

    def test_summary_includes_all_arguments(self) -> None:
        """Summary includes all arguments."""
        state = DebateState(topic="Test", max_rounds=3)
        state.current_round = 1
        state.record_argument(agent="pro", content="Pro argues")
        summary = build_debate_summary(state)
        assert "PRO: Pro argues" in summary


class TestBuildVerdictPrompt:
    """Test verdict prompt building."""

    def test_verdict_prompt_includes_summary(self) -> None:
        """Verdict prompt includes debate summary."""
        state = DebateState(topic="Test", max_rounds=3)
        prompt = build_verdict_prompt(state)
        assert "Evaluate the following debate" in prompt
        assert "No ties allowed" in prompt
