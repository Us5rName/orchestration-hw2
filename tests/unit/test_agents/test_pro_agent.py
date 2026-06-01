"""Tests for ProAgent."""

from unittest.mock import MagicMock

from debate.agents.pro_agent import ProAgent


def _make_agent() -> ProAgent:
    """Create a ProAgent with mocked provider."""
    provider = MagicMock()
    provider.chat.return_value = '{"content": "pro argument"}'
    return ProAgent(provider, "gpt-4o-mini", 0.7, 30.0, "test topic")


class TestProAgentRole:
    """Test ProAgent role and skill."""

    def test_role_is_pro(self) -> None:
        """ProAgent role is 'pro'."""
        agent = _make_agent()
        assert agent.role == "pro"

    def test_prompt_mentions_research(self) -> None:
        """System prompt includes research-analysis skill."""
        agent = _make_agent()
        prompt = agent._build_system_prompt()
        assert "research" in prompt.lower() or "evidence" in prompt.lower()

    def test_prompt_includes_topic(self) -> None:
        """System prompt includes the debate topic."""
        agent = _make_agent()
        prompt = agent._build_system_prompt()
        assert "test topic" in prompt


class TestProAgentThink:
    """Test ProAgent think method."""

    def test_think_returns_pro_response(self) -> None:
        """Think returns response with pro role."""
        agent = _make_agent()
        result = agent.think("opponent said X")
        assert result["agent"] == "pro"
        assert result["content"] == "pro argument"
