"""Tests for structured output contracts — AgentResponse."""

import pytest

from debate.services.contracts import (
    AgentResponse,
    agent_response_from_dict,
    validate_agent_dict,
)

# ---------------------------------------------------------------------------
# AgentResponse
# ---------------------------------------------------------------------------

class TestAgentResponse:
    """AgentResponse validates content and field types on construction."""

    def test_valid_plain_text(self) -> None:
        r = AgentResponse(content="Hello world")
        assert r.content == "Hello world"

    def test_valid_with_references(self) -> None:
        r = AgentResponse(content="Arg", references=["src1"])
        assert r.references == ["src1"]

    def test_valid_with_metadata(self) -> None:
        r = AgentResponse(content="Arg", metadata={"round": 1})
        assert r.metadata["round"] == 1

    def test_empty_content_raises(self) -> None:
        with pytest.raises(ValueError, match="non-empty"):
            AgentResponse(content="")

    def test_whitespace_only_content_raises(self) -> None:
        with pytest.raises(ValueError, match="non-empty"):
            AgentResponse(content="   ")

    def test_null_byte_in_content_raises(self) -> None:
        with pytest.raises(ValueError, match="control characters"):
            AgentResponse(content="hello\x00world")

    def test_control_char_in_content_raises(self) -> None:
        with pytest.raises(ValueError, match="control characters"):
            AgentResponse(content="not-json-at-all \x00\x01")

    def test_references_must_be_list(self) -> None:
        with pytest.raises(ValueError, match="list"):
            AgentResponse(content="ok", references="not-a-list")  # type: ignore[arg-type]

    def test_metadata_must_be_dict(self) -> None:
        with pytest.raises(ValueError, match="dict"):
            AgentResponse(content="ok", metadata=[])  # type: ignore[arg-type]

    def test_newlines_in_content_are_allowed(self) -> None:
        r = AgentResponse(content="line1\nline2")
        assert "line1" in r.content

    def test_tab_in_content_is_allowed(self) -> None:
        r = AgentResponse(content="col1\tcol2")
        assert r.content == "col1\tcol2"


# ---------------------------------------------------------------------------
# agent_response_from_dict
# ---------------------------------------------------------------------------

class TestAgentResponseFromDict:
    """agent_response_from_dict parses and validates raw response dicts."""

    def test_valid_json_response(self) -> None:
        d = {"content": "Pro argues.", "references": ["ref1"], "agent": "pro"}
        r = agent_response_from_dict(d)
        assert r.content == "Pro argues."
        assert r.role == "pro"
        assert r.references == ["ref1"]

    def test_plain_text_response(self) -> None:
        d = {"content": "Simple response."}
        r = agent_response_from_dict(d)
        assert r.content == "Simple response."

    def test_empty_content_raises(self) -> None:
        with pytest.raises(ValueError):
            agent_response_from_dict({"content": ""})

    def test_missing_content_raises(self) -> None:
        with pytest.raises(ValueError):
            agent_response_from_dict({})

    def test_control_chars_raise(self) -> None:
        with pytest.raises(ValueError):
            agent_response_from_dict({"content": "bad\x00content"})

    def test_validate_agent_dict_function(self) -> None:
        validate_agent_dict({"content": "valid"})

    def test_validate_agent_dict_raises_on_empty(self) -> None:
        with pytest.raises(ValueError):
            validate_agent_dict({"content": ""})
