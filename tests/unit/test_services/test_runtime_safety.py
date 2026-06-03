"""Tests verifying runtime safety controls are wired into debate execution."""

from unittest.mock import MagicMock

import pytest

from debate.services.orchestrator import DebateOrchestrator
from debate.shared.gatekeeper import ApiGatekeeper, RateLimitConfig
from debate.shared.watchdog import Watchdog
from tests.fakes.agents import ScriptedAgent

PRO_RESPONSE = {"content": "Pro argues the point.", "references": []}
CON_RESPONSE = {"content": "Con challenges the claim.", "references": []}
JUDGE_RESPONSE = {
    "winner": "pro",
    "pro_score": 80,
    "con_score": 70,
    "justification": "Pro was more persuasive.",
}


@pytest.fixture
def scripted_agents() -> tuple[ScriptedAgent, ScriptedAgent, ScriptedAgent]:
    judge = ScriptedAgent("judge", [JUDGE_RESPONSE] * 10)
    pro = ScriptedAgent("pro", [PRO_RESPONSE] * 10)
    con = ScriptedAgent("con", [CON_RESPONSE] * 10)
    return judge, pro, con


@pytest.fixture
def mock_gatekeeper() -> MagicMock:
    gk = MagicMock(spec=ApiGatekeeper)
    gk.execute.side_effect = lambda fn, *args, **kwargs: fn(*args, **kwargs)
    return gk


@pytest.fixture
def fast_gatekeeper() -> ApiGatekeeper:
    config = RateLimitConfig(max_retries=0, retry_after_seconds=0.0)
    return ApiGatekeeper(config)


@pytest.fixture
def mock_watchdog() -> MagicMock:
    return MagicMock(spec=Watchdog)


class TestGatekeeperRuntime:
    """ApiGatekeeper is invoked for every agent think() call in a debate."""

    def test_gatekeeper_execute_called_each_round(
        self,
        scripted_agents: tuple,
        mock_gatekeeper: MagicMock,
    ) -> None:
        """Gatekeeper.execute() is called for pro, con, and judge per debate."""
        judge, pro, con = scripted_agents
        orc = DebateOrchestrator(
            judge_agent=judge, pro_agent=pro, con_agent=con,
            topic="Test", max_rounds=1, gatekeeper=mock_gatekeeper,
        )
        orc.run()
        # 1 pro + 1 con per round + 1 judge verdict = 3 total for 1 round
        assert mock_gatekeeper.execute.call_count == 3

    def test_gatekeeper_scales_with_rounds(
        self,
        scripted_agents: tuple,
        mock_gatekeeper: MagicMock,
    ) -> None:
        """execute() count grows with round count: 2 agents/round + 1 judge."""
        judge, pro, con = scripted_agents
        orc = DebateOrchestrator(
            judge_agent=judge, pro_agent=pro, con_agent=con,
            topic="Test", max_rounds=3, gatekeeper=mock_gatekeeper,
        )
        orc.run()
        assert mock_gatekeeper.execute.call_count == 7  # 3*2 + 1

    def test_debate_completes_with_real_gatekeeper(
        self,
        scripted_agents: tuple,
        fast_gatekeeper: ApiGatekeeper,
    ) -> None:
        """Debate succeeds end-to-end when routed through ApiGatekeeper."""
        judge, pro, con = scripted_agents
        orc = DebateOrchestrator(
            judge_agent=judge, pro_agent=pro, con_agent=con,
            topic="Test", max_rounds=1, gatekeeper=fast_gatekeeper,
        )
        result = orc.run()
        assert result["winner"] == "pro"
        assert fast_gatekeeper.total_calls == 3

    def test_gatekeeper_optional_debate_still_runs(
        self, scripted_agents: tuple,
    ) -> None:
        """Gatekeeper is optional; debate completes without it."""
        judge, pro, con = scripted_agents
        orc = DebateOrchestrator(
            judge_agent=judge, pro_agent=pro, con_agent=con,
            topic="Test", max_rounds=1,
        )
        result = orc.run()
        assert result["winner"] == "pro"


class TestWatchdogRuntime:
    """Watchdog.ping() is called once per debate round."""

    def test_watchdog_pinged_once_per_round(
        self,
        scripted_agents: tuple,
        mock_watchdog: MagicMock,
    ) -> None:
        """ping() is called exactly once per round."""
        judge, pro, con = scripted_agents
        orc = DebateOrchestrator(
            judge_agent=judge, pro_agent=pro, con_agent=con,
            topic="Test", max_rounds=3, watchdog=mock_watchdog,
        )
        orc.run()
        assert mock_watchdog.ping.call_count == 3

    def test_debate_completes_with_healthy_watchdog(
        self, scripted_agents: tuple,
    ) -> None:
        """Debate runs to completion with a real Watchdog that stays alive."""
        judge, pro, con = scripted_agents
        real_watchdog = Watchdog(check_interval=1.0, timeout=30.0)
        orc = DebateOrchestrator(
            judge_agent=judge, pro_agent=pro, con_agent=con,
            topic="Test", max_rounds=1, watchdog=real_watchdog,
        )
        result = orc.run()
        assert result["winner"] == "pro"
        assert real_watchdog.is_alive()

    def test_watchdog_optional_debate_still_runs(
        self, scripted_agents: tuple,
    ) -> None:
        """Watchdog is optional; debate completes without it."""
        judge, pro, con = scripted_agents
        orc = DebateOrchestrator(
            judge_agent=judge, pro_agent=pro, con_agent=con,
            topic="Test", max_rounds=1,
        )
        result = orc.run()
        assert result["winner"] == "pro"
