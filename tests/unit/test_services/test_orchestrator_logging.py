"""Tests for orchestrator_logging helpers."""

import pytest

from debate.services.orchestrator_logging import (
    log_agent_response,
    log_debate_complete,
    log_debate_start,
    log_round_start,
    log_verdict,
)
from tests.fakes.logger import FakeLogger


@pytest.fixture
def logger() -> FakeLogger:
    return FakeLogger()


class TestLogAgentResponse:
    """Tests for log_agent_response."""

    def test_logs_content(self, logger: FakeLogger) -> None:
        """Logs the agent content string."""
        log_agent_response(logger, "PRO", {"content": "hello"})
        assert len(logger.messages) >= 1
        assert "hello" in logger.messages[0]

    def test_no_refs_skips_ref_log(self, logger: FakeLogger) -> None:
        """No second log call when references list is empty."""
        log_agent_response(logger, "PRO", {"content": "hello"})
        assert len(logger.messages) == 1

    def test_string_references_joined(self, logger: FakeLogger) -> None:
        """String references are comma-joined in the log."""
        log_agent_response(logger, "PRO", {"content": "x", "references": ["a", "b"]})
        assert any("a, b" in m for m in logger.messages)

    def test_dict_references_do_not_crash(self, logger: FakeLogger) -> None:
        """Dict references are coerced to str instead of raising TypeError."""
        refs = [{"title": "Foo", "url": "http://example.com"}]
        log_agent_response(logger, "CON", {"content": "x", "references": refs})
        assert len(logger.messages) == 2

    def test_mixed_references_coerced(self, logger: FakeLogger) -> None:
        """Mixed str/dict references are all coerced to str."""
        refs = ["plain string", {"title": "Dict ref"}]
        log_agent_response(logger, "CON", {"content": "x", "references": refs})
        assert any("plain string" in m for m in logger.messages)

    def test_none_logger_is_noop(self) -> None:
        """Passing None as logger does not raise."""
        log_agent_response(None, "PRO", {"content": "x", "references": [{"k": "v"}]})


class TestOtherLogHelpers:
    """Smoke tests for remaining log helpers."""

    def test_log_debate_start(self, logger: FakeLogger) -> None:
        log_debate_start(logger, "AI vs Humans", 5)
        assert len(logger.messages) == 1

    def test_log_round_start(self, logger: FakeLogger) -> None:
        log_round_start(logger, 2, 10)
        assert len(logger.messages) == 1

    def test_log_verdict(self, logger: FakeLogger) -> None:
        log_verdict(logger, {"winner": "pro", "pro_score": 80, "con_score": 70, "justification": "j"})
        assert len(logger.messages) == 2

    def test_log_debate_complete(self, logger: FakeLogger) -> None:
        log_debate_complete(logger, "pro", 80, 70)
        assert len(logger.messages) == 1
