"""Tests for ConAgent."""

from unittest.mock import MagicMock

from debate.agents.con_agent import ConAgent
from debate.skills.quality_standards import QualityStandardsSkill


def _make_agent(skills=None) -> ConAgent:
    """Create a ConAgent with mocked provider."""
    provider = MagicMock()
    provider.chat.return_value = '{"content": "con argument"}'
    return ConAgent(provider, "gpt-4o-mini", 0.7, 30.0, "test topic", skills)


class TestConAgentRole:
    """Test ConAgent role and skill."""

    def test_role_is_con(self) -> None:
        """ConAgent role is 'con'."""
        agent = _make_agent()
        assert agent.role == "con"

    def test_prompt_includes_topic(self) -> None:
        """System prompt includes the debate topic."""
        agent = _make_agent()
        prompt = agent._build_system_prompt()
        assert "test topic" in prompt

    def test_prompt_includes_skill_instructions(self) -> None:
        """System prompt includes skill instructions when skills assigned."""
        skill = QualityStandardsSkill()
        agent = _make_agent(skills=[skill])
        prompt = agent._build_system_prompt()
        assert "quality-standards" in prompt.lower() or "critical" in prompt.lower()

    def test_prompt_no_skill_block_when_no_skills(self) -> None:
        """System prompt has no skill block when no skills are assigned."""
        agent = _make_agent()
        assert "SKILL" not in agent._build_system_prompt()


class TestConAgentThink:
    """Test ConAgent think method."""

    def test_think_returns_con_response(self) -> None:
        """Think returns response with con role."""
        agent = _make_agent()
        result = agent.think("opponent said X")
        assert result["agent"] == "con"
        assert result["content"] == "con argument"
