"""Tests for AgentBase."""

from unittest.mock import MagicMock

import pytest

from debate.agents.base_agent import AgentBase
from debate.skills.base_skill import AgentSkill


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
def mock_provider() -> MagicMock:
    """Return a mocked LLM provider."""
    provider = MagicMock()
    provider.chat.return_value = '{"content": "test response"}'
    return provider


@pytest.fixture
def agent(mock_provider: MagicMock) -> ConcreteAgent:
    """Return a concrete agent with mocked provider."""
    return ConcreteAgent(
        provider=mock_provider,
        model="test-model",
        temperature=0.7,
        timeout=30.0,
    )


class TestAgentBaseInit:
    """Test AgentBase initialization."""

    def test_stores_provider(self, agent: ConcreteAgent, mock_provider: MagicMock) -> None:
        """Agent stores its LLM provider."""
        assert agent.provider is mock_provider

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
        calls = agent.provider.chat.call_args
        messages = calls.args[0]
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "user question"

    def test_think_includes_role(self, agent: ConcreteAgent) -> None:
        """Think includes agent role in response."""
        result = agent.think("test")
        assert result["agent"] == "test"


class TestAgentBaseSkills:
    """Test AgentBase skill composition."""

    def test_skill_block_empty_with_no_skills(self, mock_provider: MagicMock) -> None:
        """_build_skill_block returns empty string when no skills assigned."""
        agent = ConcreteAgent(mock_provider, "m", 0.7, 30.0)
        assert agent._build_skill_block() == ""

    def test_skill_block_joins_instructions(self, mock_provider: MagicMock) -> None:
        """_build_skill_block joins instructions from all skills."""
        s1 = _make_skill("s1", "Instruction one.")
        s2 = _make_skill("s2", "Instruction two.")
        agent = ConcreteAgent(mock_provider, "m", 0.7, 30.0, skills=[s1, s2])
        block = agent._build_skill_block()
        assert "Instruction one." in block
        assert "Instruction two." in block

    def test_think_passes_tools_to_provider(self, mock_provider: MagicMock) -> None:
        """think() passes skill tool defs to provider.chat()."""
        tool_def = {"name": "search", "description": "...", "parameters": {}}
        skill = _make_skill("research", "Do research.", tool=tool_def)
        agent = ConcreteAgent(mock_provider, "m", 0.7, 30.0, skills=[skill])
        agent.think("test prompt")
        _, tools_arg, executor_arg = mock_provider.chat.call_args.args
        assert tools_arg == [tool_def]
        assert executor_arg is not None

    def test_think_no_tools_passes_none(self, mock_provider: MagicMock) -> None:
        """think() passes None tools when skills have no tool definitions."""
        skill = _make_skill("no-tool", "Instructions.", tool=None)
        agent = ConcreteAgent(mock_provider, "m", 0.7, 30.0, skills=[skill])
        agent.think("test prompt")
        _, tools_arg, executor_arg = mock_provider.chat.call_args.args
        assert tools_arg is None
        assert executor_arg is None

    def test_execute_tool_search_delegates_to_skill(self, mock_provider: MagicMock) -> None:
        """_execute_tool dispatches search to the skill that returns results."""
        skill = _make_skill("research", "Research.")
        skill.search.return_value = ["Result one", "Result two"]
        agent = ConcreteAgent(mock_provider, "m", 0.7, 30.0, skills=[skill])
        result = agent._execute_tool("search", {"query": "test"})
        assert "Result one" in result
        skill.search.assert_called_once_with("test")

    def test_execute_tool_unknown_returns_empty(self, mock_provider: MagicMock) -> None:
        """_execute_tool returns empty string for unknown tool names."""
        agent = ConcreteAgent(mock_provider, "m", 0.7, 30.0)
        assert agent._execute_tool("unknown_tool", {}) == ""


class TestAgentLogging:
    """Test that AgentBase emits structured log entries."""

    def _agent_with_logger(self, mock_provider: MagicMock, skills=None) -> tuple:
        logger = MagicMock()
        agent = ConcreteAgent(mock_provider, "m", 0.7, 30.0, skills=skills, logger=logger)
        return agent, logger

    def test_think_logs_active_skills(self, mock_provider: MagicMock) -> None:
        """think() logs the names of active skills before the LLM call."""
        skill = _make_skill("research-analysis", "Do research.")
        agent, logger = self._agent_with_logger(mock_provider, skills=[skill])
        agent.think("prompt")
        messages = [c[0][0] for c in logger.info.call_args_list]
        assert any("research-analysis" in m for m in messages)

    def test_think_no_log_when_no_skills(self, mock_provider: MagicMock) -> None:
        """think() does not log skill line when agent has no skills."""
        agent, logger = self._agent_with_logger(mock_provider, skills=[])
        agent.think("prompt")
        messages = [c[0][0] for c in logger.info.call_args_list]
        assert not any("skills active" in m for m in messages)

    def test_think_no_log_when_no_logger(self, mock_provider: MagicMock) -> None:
        """think() does not crash when logger is None."""
        skill = _make_skill("research-analysis", "Do research.")
        agent = ConcreteAgent(mock_provider, "m", 0.7, 30.0, skills=[skill])
        agent.think("prompt")  # must not raise

    def test_tool_call_logged(self, mock_provider: MagicMock) -> None:
        """_execute_tool logs the tool name and query."""
        skill = _make_skill("research-analysis", "Do research.")
        skill.search.return_value = ["result"]
        agent, logger = self._agent_with_logger(mock_provider, skills=[skill])
        agent._execute_tool("search", {"query": "test query"})
        messages = [c[0][0] for c in logger.info.call_args_list]
        assert any("search" in m and "test query" in m for m in messages)

    def test_tool_result_count_logged(self, mock_provider: MagicMock) -> None:
        """_execute_tool logs the number of results returned."""
        skill = _make_skill("research-analysis", "Do research.")
        skill.search.return_value = ["r1", "r2", "r3"]
        agent, logger = self._agent_with_logger(mock_provider, skills=[skill])
        agent._execute_tool("search", {"query": "q"})
        messages = [c[0][0] for c in logger.info.call_args_list]
        assert any("3 item(s)" in m for m in messages)

    def test_unknown_tool_logs_no_handler(self, mock_provider: MagicMock) -> None:
        """_execute_tool logs 'no handler' for unknown tools."""
        agent, logger = self._agent_with_logger(mock_provider)
        agent._execute_tool("unknown", {})
        messages = [c[0][0] for c in logger.info.call_args_list]
        assert any("no handler" in m for m in messages)
