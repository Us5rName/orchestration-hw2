"""Tests for ConAgent."""

from unittest.mock import MagicMock

from debate.agents.con_agent import ConAgent


def _make_agent() -> ConAgent:
    """Create a ConAgent with mocked provider."""
    provider = MagicMock()
    provider.chat.return_value = '{"content": "con argument"}'
    return ConAgent(provider, "gpt-4o-mini", 0.7, 30.0, "test topic")


class TestConAgentRole:
    """Test ConAgent role and skill."""

    def test_role_is_con(self) -> None:
        """ConAgent role is 'con'."""
        agent = _make_agent()
        assert agent.role == "con"

    def test_prompt_mentions_quality(self) -> None:
        """System prompt includes quality-standards skill."""
        agent = _make_agent()
        prompt = agent._build_system_prompt()
        assert "quality" in prompt.lower() or "critical" in prompt.lower()

    def test_prompt_includes_topic(self) -> None:
        """System prompt includes the debate topic."""
        agent = _make_agent()
        prompt = agent._build_system_prompt()
        assert "test topic" in prompt


class TestConAgentThink:
    """Test ConAgent think method."""

    def test_think_returns_con_response(self) -> None:
        """Think returns response with con role."""
        agent = _make_agent()
        result = agent.think("opponent said X")
        assert result["agent"] == "con"
        assert result["content"] == "con argument"
