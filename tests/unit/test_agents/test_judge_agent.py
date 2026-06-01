"""Tests for JudgeAgent."""

from unittest.mock import MagicMock

from debate.agents.judge_agent import JudgeAgent


def _make_agent() -> JudgeAgent:
    """Create a JudgeAgent with mocked provider."""
    provider = MagicMock()
    provider.chat.return_value = (
        '{"winner": "pro", "pro_score": 80, "con_score": 70, '
        '"justification": "pro was more persuasive"}'
    )
    return JudgeAgent(provider, "gpt-4o-mini", 0.3, 30.0, "test topic")


class TestJudgeAgentRole:
    """Test JudgeAgent role."""

    def test_role_is_judge(self) -> None:
        """JudgeAgent role is 'judge'."""
        agent = _make_agent()
        assert agent.role == "judge"

    def test_prompt_mentions_persuasiveness(self) -> None:
        """System prompt focuses on persuasiveness, not facts."""
        agent = _make_agent()
        prompt = agent._build_system_prompt()
        assert "persuasive" in prompt.lower() or "persuasion" in prompt.lower()

    def test_prompt_forbids_ties(self) -> None:
        """System prompt explicitly forbids ties."""
        agent = _make_agent()
        prompt = agent._build_system_prompt()
        assert "no tie" in prompt.lower() or "never" in prompt.lower()


class TestJudgeAgentVerdict:
    """Test JudgeAgent verdict method."""

    def test_verdict_returns_winner(self) -> None:
        """Verdict returns a decision with winner."""
        agent = _make_agent()
        result = agent.think("evaluate both sides")
        assert result["agent"] == "judge"
        assert result["winner"] in ("pro", "con")

    def test_verdict_has_scores(self) -> None:
        """Verdict includes differential scores."""
        agent = _make_agent()
        result = agent.think("evaluate")
        assert "pro_score" in result
        assert "con_score" in result
