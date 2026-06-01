"""Tests for AgentBase."""

from unittest.mock import MagicMock

import pytest

from debate.agents.base_agent import AgentBase


class ConcreteAgent(AgentBase):
    """Concrete agent for testing abstract base."""

    @property
    def role(self) -> str:
        return "test"

    def _build_system_prompt(self) -> str:
        return "You are a test agent."


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
