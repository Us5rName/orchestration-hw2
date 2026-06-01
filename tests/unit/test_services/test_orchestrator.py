"""Tests for DebateOrchestrator."""

from unittest.mock import MagicMock

import pytest

from debate.services.orchestrator import DebateOrchestrator


@pytest.fixture
def mock_judge() -> MagicMock:
    """Return a mock JudgeAgent."""
    judge = MagicMock()
    judge.role = "judge"
    return judge


@pytest.fixture
def mock_pro() -> MagicMock:
    """Return a mock ProAgent."""
    pro = MagicMock()
    pro.role = "pro"
    return pro


@pytest.fixture
def mock_con() -> MagicMock:
    """Return a mock ConAgent."""
    con = MagicMock()
    con.role = "con"
    return con


@pytest.fixture
def mock_watchdog() -> MagicMock:
    """Return a mock Watchdog."""
    return MagicMock()


@pytest.fixture
def orchestrator(
    mock_judge: MagicMock, mock_pro: MagicMock, mock_con: MagicMock, mock_watchdog: MagicMock
) -> DebateOrchestrator:
    """Return a DebateOrchestrator with mocked agents."""
    return DebateOrchestrator(
        judge_agent=mock_judge,
        pro_agent=mock_pro,
        con_agent=mock_con,
        topic="AI is beneficial",
        max_rounds=3,
        watchdog=mock_watchdog,
    )


class TestOrchestratorInit:
    """Test DebateOrchestrator initialization."""

    def test_creates_debate_state(self, orchestrator: DebateOrchestrator) -> None:
        """Orchestrator creates a DebateState internally."""
        assert orchestrator.state is not None

    def test_state_has_correct_topic(self, orchestrator: DebateOrchestrator) -> None:
        """DebateState has the correct topic."""
        assert orchestrator.state.topic == "AI is beneficial"

    def test_state_has_correct_max_rounds(self, orchestrator: DebateOrchestrator) -> None:
        """DebateState has the correct max_rounds."""
        assert orchestrator.state.max_rounds == 3

    def test_agents_stored(self, orchestrator: DebateOrchestrator) -> None:
        """Agents are stored correctly."""
        assert orchestrator.judge is not None
        assert orchestrator.pro is not None
        assert orchestrator.con is not None

    def test_invalid_max_rounds_raises(
        self,
        mock_judge: MagicMock,
        mock_pro: MagicMock,
        mock_con: MagicMock,
        mock_watchdog: MagicMock,
    ) -> None:
        """Negative max_rounds raises ValueError."""
        with pytest.raises(ValueError):
            DebateOrchestrator(
                judge_agent=mock_judge,
                pro_agent=mock_pro,
                con_agent=mock_con,
                topic="Test",
                max_rounds=0,
                watchdog=mock_watchdog,
            )


class TestOrchestratorRunRound:
    """Test running a single round of debate."""

    def test_run_round_calls_pro_think(self, orchestrator: DebateOrchestrator) -> None:
        """run_round calls pro's think method."""
        orchestrator.pro.think.return_value = {"content": "Pro argues", "references": []}
        orchestrator.con.think.return_value = {"content": "Con counters", "references": []}
        orchestrator.run_round()
        orchestrator.pro.think.assert_called_once()

    def test_run_round_calls_con_think(self, orchestrator: DebateOrchestrator) -> None:
        """run_round calls con's think method."""
        orchestrator.pro.think.return_value = {"content": "Pro argues", "references": []}
        orchestrator.con.think.return_value = {"content": "Con counters", "references": []}
        orchestrator.run_round()
        orchestrator.con.think.assert_called_once()

    def test_run_round_adds_to_history(self, orchestrator: DebateOrchestrator) -> None:
        """run_round adds arguments to debate history."""
        orchestrator.pro.think.return_value = {"content": "Pro argues", "references": []}
        orchestrator.con.think.return_value = {"content": "Con counters", "references": []}
        orchestrator.run_round()
        assert len(orchestrator.state.history) == 2
        assert orchestrator.state.current_round == 1
