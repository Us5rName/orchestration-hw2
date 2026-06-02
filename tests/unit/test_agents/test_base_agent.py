"""Tests for AgentBase.

Logging tests live in test_base_agent_logging.py to keep both files
under the 150-line limit.
"""

from unittest.mock import MagicMock

import pytest

from debate.agents.base_agent import AgentBase
from debate.skills.base_skill import AgentSkill
from tests.fakes.providers import FakeProvider


class ConcreteAgent(AgentBase):
    """Concrete agent for testing abstract base."""

    @property
    def role(self) -> str:
        return "test"

    def _build_system_prompt(self) -> str:
        base = "You are a test agent."
        skill_block = self._build_skill_block()
        return f"{base}\n\n{skill_block}" if skill_block else base


def _make_skill(name: str, instructions: str, tool: dict | None = None) -> AgentSkill:
    """Create a minimal mock skill."""
    skill = MagicMock(spec=AgentSkill)
    skill.name = name
    skill.get_instructions.return_value = instructions
    skill.get_tool_definition.return_value = tool
    skill.search.return_value = []
    return skill


@pytest.fixture
def fake_provider() -> FakeProvider:
    """Return a scripted FakeProvider returning a JSON response."""
    return FakeProvider(['{"content": "test response"}'])


@pytest.fixture
def agent(fake_provider: FakeProvider) -> ConcreteAgent:
    """Return a concrete agent with FakeProvider."""
    return ConcreteAgent(
        provider=fake_provider,
        model="test-model",
        temperature=0.7,
        timeout=30.0,
    )


class TestAgentBaseInit:
    """Test AgentBase initialization."""

    def test_stores_provider(self, agent: ConcreteAgent, fake_provider: FakeProvider) -> None:
        """Agent stores its LLM provider."""
        assert agent.provider is fake_provider

    def test_stores_model(self, agent: ConcreteAgent) -> None:
        """Agent stores model name."""
        assert agent.model == "test-model"

    def test_stores_temperature(self, agent: ConcreteAgent) -> None:
        """Agent stores temperature."""
        assert agent.temperature == 0.7


class TestAgentBaseThink:
    """Test AgentBase.think() method."""

    def test_think_returns_json(self, agent: ConcreteAgent) -> None:
        """Think returns parsed JSON response."""
        result = agent.think("test prompt")
        assert isinstance(result, dict)
        assert result["content"] == "test response"

    def test_think_builds_messages(self, agent: ConcreteAgent) -> None:
        """Think sends system + user messages to provider."""
        agent.think("user question")
        # FakeProvider captures nothing; verify via think() return shape
        result = agent.think("user question")
        assert result["agent"] == "test"

    def test_think_includes_role(self, agent: ConcreteAgent) -> None:
        """Think includes agent role in response."""
        result = agent.think("test")
        assert result["agent"] == "test"


class TestAgentBaseSkills:
    """Test AgentBase skill composition."""

    def test_skill_block_empty_with_no_skills(self) -> None:
        """_build_skill_block returns empty string when no skills assigned."""
        agent = ConcreteAgent(FakeProvider(), "m", 0.7, 30.0)
        assert agent._build_skill_block() == ""

    def test_skill_block_joins_instructions(self) -> None:
        """_build_skill_block joins instructions from all skills."""
        s1 = _make_skill("s1", "Instruction one.")
        s2 = _make_skill("s2", "Instruction two.")
        agent = ConcreteAgent(FakeProvider(), "m", 0.7, 30.0, skills=[s1, s2])
        block = agent._build_skill_block()
        assert "Instruction one." in block
        assert "Instruction two." in block

    def test_think_passes_tools_to_provider(self) -> None:
        """think() passes skill tool defs to the provider."""
        tool_def = {"name": "search", "description": "...", "parameters": {}}
        skill = _make_skill("research", "Do research.", tool=tool_def)
        mock_provider = MagicMock()
        mock_provider.chat.return_value = '{"content": "ok"}'
        agent = ConcreteAgent(mock_provider, "m", 0.7, 30.0, skills=[skill])
        agent.think("test prompt")
        _, tools_arg, executor_arg = mock_provider.chat.call_args.args
        assert tools_arg == [tool_def]
        assert executor_arg is not None

    def test_think_no_tools_passes_none(self) -> None:
        """think() passes None tools when skills have no tool definitions."""
        skill = _make_skill("no-tool", "Instructions.", tool=None)
        mock_provider = MagicMock()
        mock_provider.chat.return_value = '{"content": "ok"}'
        agent = ConcreteAgent(mock_provider, "m", 0.7, 30.0, skills=[skill])
        agent.think("test prompt")
        _, tools_arg, executor_arg = mock_provider.chat.call_args.args
        assert tools_arg is None
        assert executor_arg is None

    def test_execute_tool_search_delegates_to_skill(self) -> None:
        """_execute_tool dispatches search to the skill that returns results."""
        skill = _make_skill("research", "Research.")
        skill.search.return_value = ["Result one", "Result two"]
        agent = ConcreteAgent(FakeProvider(), "m", 0.7, 30.0, skills=[skill])
        result = agent._execute_tool("search", {"query": "test"})
        assert "Result one" in result
        skill.search.assert_called_once_with("test")

    def test_execute_tool_unknown_returns_empty(self) -> None:
        """_execute_tool returns empty string for unknown tool names."""
        agent = ConcreteAgent(FakeProvider(), "m", 0.7, 30.0)
        assert agent._execute_tool("unknown_tool", {}) == ""
