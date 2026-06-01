"""Tests for DebateState."""

import pytest

from debate.services.debate_state import DebateState


@pytest.fixture
def state() -> DebateState:
    """Return a DebateState instance."""
    return DebateState(topic="AI is beneficial", max_rounds=3)


class TestDebateStateInit:
    """Test DebateState initialization."""

    def test_initial_round_is_zero(self, state: DebateState) -> None:
        """Current round starts at 0."""
        assert state.current_round == 0

    def test_initial_history_is_empty(self, state: DebateState) -> None:
        """History starts empty."""
        assert state.history == []

    def test_initial_winner_is_none(self, state: DebateState) -> None:
        """Winner starts as None."""
        assert state.winner is None

    def test_stores_topic(self, state: DebateState) -> None:
        """Topic is stored correctly."""
        assert state.topic == "AI is beneficial"

    def test_stores_max_rounds(self, state: DebateState) -> None:
        """Max rounds is stored correctly."""
        assert state.max_rounds == 3


class TestDebateStateRecordArgument:
    """Test recording arguments."""

    def test_records_pro_argument(self, state: DebateState) -> None:
        """Recording an argument adds it to history."""
        state.record_argument(agent="pro", content="Pro argues")
        assert len(state.history) == 1
        assert state.history[0]["agent"] == "pro"

    def test_records_references(self, state: DebateState) -> None:
        """Recording with references stores them."""
        state.record_argument(agent="pro", content="Arg", references=["url"])
        assert state.history[0]["references"] == ["url"]

    def test_default_empty_references(self, state: DebateState) -> None:
        """Missing references default to empty list."""
        state.record_argument(agent="pro", content="Arg")
        assert state.history[0]["references"] == []


class TestDebateStateAdvanceRound:
    """Test round advancement."""

    def test_advances_round(self, state: DebateState) -> None:
        """advance_round increments current_round."""
        state.advance_round()
        assert state.current_round == 1


class TestDebateStateIsComplete:
    """Test completion check."""

    def test_not_complete_initially(self, state: DebateState) -> None:
        """Debate is not complete at start."""
        assert not state.is_complete

    def test_complete_after_max_rounds(self, state: DebateState) -> None:
        """Debate is complete after max_rounds."""
        state.current_round = 3
        assert state.is_complete


class TestDebateStateSetVerdict:
    """Test setting verdict."""

    def test_sets_winner(self, state: DebateState) -> None:
        """set_verdict sets the winner."""
        state.set_verdict(winner="pro", pro_score=80, con_score=70)
        assert state.winner == "pro"

    def test_sets_scores(self, state: DebateState) -> None:
        """set_verdict sets both scores."""
        state.set_verdict(winner="pro", pro_score=80, con_score=70)
        assert state.pro_score == 80
        assert state.con_score == 70
