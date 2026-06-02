"""Tests for orchestrator_logging helpers."""

from unittest.mock import MagicMock

import pytest

from debate.services.orchestrator_logging import (
    log_agent_response,
    log_debate_complete,
    log_debate_start,
    log_round_start,
    log_verdict,
)


@pytest.fixture
def logger() -> MagicMock:
    return MagicMock()


class TestLogAgentResponse:
    """Tests for log_agent_response."""

    def test_logs_content(self, logger: MagicMock) -> None:
        """Logs the agent content string."""
        log_agent_response(logger, "PRO", {"content": "hello"})
        logger.info.assert_called()
        assert "hello" in logger.info.call_args_list[0][0][0]

    def test_no_refs_skips_ref_log(self, logger: MagicMock) -> None:
        """No second log call when references list is empty."""
        log_agent_response(logger, "PRO", {"content": "hello"})
        assert logger.info.call_count == 1

    def test_string_references_joined(self, logger: MagicMock) -> None:
        """String references are comma-joined in the log."""
        log_agent_response(logger, "PRO", {"content": "x", "references": ["a", "b"]})
        calls = [c[0][0] for c in logger.info.call_args_list]
        assert any("a, b" in c for c in calls)

    def test_dict_references_do_not_crash(self, logger: MagicMock) -> None:
        """Dict references are coerced to str instead of raising TypeError."""
        refs = [{"title": "Foo", "url": "http://example.com"}]
        log_agent_response(logger, "CON", {"content": "x", "references": refs})
        assert logger.info.call_count == 2

    def test_mixed_references_coerced(self, logger: MagicMock) -> None:
        """Mixed str/dict references are all coerced to str."""
        refs = ["plain string", {"title": "Dict ref"}]
        log_agent_response(logger, "CON", {"content": "x", "references": refs})
        calls = [c[0][0] for c in logger.info.call_args_list]
        assert any("plain string" in c for c in calls)

    def test_none_logger_is_noop(self) -> None:
        """Passing None as logger does not raise."""
        log_agent_response(None, "PRO", {"content": "x", "references": [{"k": "v"}]})


class TestOtherLogHelpers:
    """Smoke tests for remaining log helpers."""

    def test_log_debate_start(self, logger: MagicMock) -> None:
        log_debate_start(logger, "AI vs Humans", 5)
        logger.info.assert_called_once()

    def test_log_round_start(self, logger: MagicMock) -> None:
        log_round_start(logger, 2, 10)
        logger.info.assert_called_once()

    def test_log_verdict(self, logger: MagicMock) -> None:
        log_verdict(logger, {"winner": "pro", "pro_score": 80, "con_score": 70, "justification": "j"})
        assert logger.info.call_count == 2

    def test_log_debate_complete(self, logger: MagicMock) -> None:
        log_debate_complete(logger, "pro", 80, 70)
        logger.info.assert_called_once()
