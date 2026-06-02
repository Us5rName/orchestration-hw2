"""Tests for ProAgent."""

from unittest.mock import MagicMock

from debate.agents.pro_agent import ProAgent
from debate.skills.research_analysis import ResearchAnalysisSkill


def _make_agent(skills=None) -> ProAgent:
    """Create a ProAgent with mocked provider."""
    provider = MagicMock()
    provider.chat.return_value = '{"content": "pro argument"}'
    return ProAgent(provider, "gpt-4o-mini", 0.7, 30.0, "test topic", skills)


class TestProAgentRole:
    """Test ProAgent role and skill."""

    def test_role_is_pro(self) -> None:
        """ProAgent role is 'pro'."""
        agent = _make_agent()
        assert agent.role == "pro"

    def test_prompt_includes_topic(self) -> None:
        """System prompt includes the debate topic."""
        agent = _make_agent()
        prompt = agent._build_system_prompt()
        assert "test topic" in prompt

    def test_prompt_includes_skill_instructions(self) -> None:
        """System prompt includes skill instructions when skills assigned."""
        mock_svc = MagicMock()
        mock_svc.search.return_value = []
        skill = ResearchAnalysisSkill(mock_svc)
        agent = _make_agent(skills=[skill])
        prompt = agent._build_system_prompt()
        assert "research-analysis" in prompt.lower() or "evidence" in prompt.lower()

    def test_prompt_no_skill_block_when_no_skills(self) -> None:
        """System prompt has no skill block when no skills are assigned."""
        agent = _make_agent()
        assert "SKILL" not in agent._build_system_prompt()


class TestProAgentThink:
    """Test ProAgent think method."""

    def test_think_returns_pro_response(self) -> None:
        """Think returns response with pro role."""
        agent = _make_agent()
        result = agent.think("opponent said X")
        assert result["agent"] == "pro"
        assert result["content"] == "pro argument"
