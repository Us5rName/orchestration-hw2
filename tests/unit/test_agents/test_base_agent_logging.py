"""Tests for AgentBase structured logging behaviour.

Split from test_base_agent.py to keep both files under the 150-line limit.
"""

from unittest.mock import MagicMock

from debate.agents.base_agent import AgentBase
from debate.skills.base_skill import AgentSkill
from tests.fakes.providers import FakeProvider


class ConcreteAgent(AgentBase):
    """Minimal concrete agent for testing."""

    @property
    def role(self) -> str:
        return "test"

    def _build_system_prompt(self) -> str:
        base = "You are a test agent."
        skill_block = self._build_skill_block()
        return f"{base}\n\n{skill_block}" if skill_block else base


def _make_skill(name: str, instructions: str, tool: dict | None = None) -> AgentSkill:
    skill = MagicMock(spec=AgentSkill)
    skill.name = name
    skill.get_instructions.return_value = instructions
    skill.get_tool_definition.return_value = tool
    skill.search.return_value = []
    return skill


def _agent_with_logger(
    skills: list | None = None,
    responses: list[str] | None = None,
) -> tuple[ConcreteAgent, MagicMock]:
    provider = FakeProvider(responses or ['{"content": "ok"}'])
    logger = MagicMock()
    agent = ConcreteAgent(provider, "m", 0.7, 30.0, skills=skills, logger=logger)
    return agent, logger


class TestAgentLogging:
    """AgentBase emits structured log entries for skills and tool calls."""

    def test_think_logs_active_skills(self) -> None:
        """think() logs the names of active skills before the LLM call."""
        skill = _make_skill("research-analysis", "Do research.")
        agent, logger = _agent_with_logger(skills=[skill])
        agent.think("prompt")
        messages = [c[0][0] for c in logger.info.call_args_list]
        assert any("research-analysis" in m for m in messages)

    def test_think_no_log_when_no_skills(self) -> None:
        """think() does not log a skill line when agent has no skills."""
        agent, logger = _agent_with_logger(skills=[])
        agent.think("prompt")
        messages = [c[0][0] for c in logger.info.call_args_list]
        assert not any("skills active" in m for m in messages)

    def test_think_no_crash_when_no_logger(self) -> None:
        """think() does not crash when logger is None."""
        skill = _make_skill("research-analysis", "Do research.")
        provider = FakeProvider(['{"content": "ok"}'])
        agent = ConcreteAgent(provider, "m", 0.7, 30.0, skills=[skill])
        agent.think("prompt")  # must not raise

    def test_tool_call_logged(self) -> None:
        """_execute_tool logs the tool name and query."""
        skill = _make_skill("research-analysis", "Do research.")
        skill.search.return_value = ["result"]
        agent, logger = _agent_with_logger(skills=[skill])
        agent._execute_tool("search", {"query": "test query"})
        messages = [c[0][0] for c in logger.info.call_args_list]
        assert any("search" in m and "test query" in m for m in messages)

    def test_tool_result_count_logged(self) -> None:
        """_execute_tool logs the number of results returned."""
        skill = _make_skill("research-analysis", "Do research.")
        skill.search.return_value = ["r1", "r2", "r3"]
        agent, logger = _agent_with_logger(skills=[skill])
        agent._execute_tool("search", {"query": "q"})
        messages = [c[0][0] for c in logger.info.call_args_list]
        assert any("3 item(s)" in m for m in messages)

    def test_unknown_tool_logs_no_handler(self) -> None:
        """_execute_tool logs 'no handler' for unknown tools."""
        agent, logger = _agent_with_logger()
        agent._execute_tool("unknown", {})
        messages = [c[0][0] for c in logger.info.call_args_list]
        assert any("no handler" in m for m in messages)
