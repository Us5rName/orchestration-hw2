"""Tests for AgentSkill abstract base class."""

import inspect

import pytest

from debate.skills.base_skill import AgentSkill


class ConcreteSkill(AgentSkill):
    """Minimal concrete skill for testing the ABC."""

    @property
    def name(self) -> str:
        return "test-skill"

    def get_instructions(self) -> str:
        return "Test instructions."


class TestAgentSkillABC:
    """Test that AgentSkill enforces its interface."""

    def test_is_abstract(self) -> None:
        """AgentSkill is an abstract class."""
        assert inspect.isabstract(AgentSkill)

    def test_abstract_methods(self) -> None:
        """AgentSkill declares name and get_instructions as abstract."""
        assert "name" in AgentSkill.__abstractmethods__
        assert "get_instructions" in AgentSkill.__abstractmethods__

    def test_concrete_subclass_instantiates(self) -> None:
        """Concrete subclass instantiates without error."""
        skill = ConcreteSkill()
        assert skill is not None

    def test_name_returns_identifier(self) -> None:
        """name property returns the skill identifier."""
        assert ConcreteSkill().name == "test-skill"

    def test_get_instructions_returns_string(self) -> None:
        """get_instructions returns a non-empty string."""
        instructions = ConcreteSkill().get_instructions()
        assert isinstance(instructions, str)
        assert len(instructions) > 0


class TestAgentSkillDefaults:
    """Test AgentSkill default implementations."""

    def test_default_tool_definition_is_none(self) -> None:
        """get_tool_definition returns None by default."""
        assert ConcreteSkill().get_tool_definition() is None

    def test_default_search_returns_empty_list(self) -> None:
        """search returns an empty list by default."""
        result = ConcreteSkill().search("any query")
        assert result == []
