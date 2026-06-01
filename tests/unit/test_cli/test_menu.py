"""Tests for TerminalMenu."""

from unittest.mock import MagicMock, patch

import pytest

from debate.cli.menu import TerminalMenu


@pytest.fixture
def mock_sdk() -> MagicMock:
    """Return a mock SDK."""
    sdk = MagicMock()
    sdk.run_debate.return_value = {
        "winner": "pro",
        "pro_score": 80,
        "con_score": 70,
        "justification": "Better arguments",
    }
    sdk.get_logs.return_value = ["log line 1", "log line 2"]
    return sdk


@pytest.fixture
def menu(mock_sdk: MagicMock) -> TerminalMenu:
    """Return a TerminalMenu instance."""
    return TerminalMenu(sdk=mock_sdk)


class TestMenuExit:
    """Test menu exit."""

    def test_exit_breaks_loop(self, menu: TerminalMenu) -> None:
        """Option 4 exits the menu loop."""
        with patch("builtins.input", return_value="4"):
            menu.run()


class TestMenuViewLogs:
    """Test viewing logs."""

    def test_view_logs_calls_sdk(self, menu: TerminalMenu) -> None:
        """Option 2 calls sdk.get_logs."""
        with patch("builtins.input", side_effect=["2", "4"]), patch("builtins.print"):
            menu.run()
            menu.sdk.get_logs.assert_called_once_with(count=20)


class TestMenuStartDebate:
    """Test starting debate."""

    def test_start_debate_calls_sdk(self, menu: TerminalMenu) -> None:
        """Option 1 calls sdk.run_debate."""
        with patch("builtins.input", side_effect=["1", "4"]), patch("builtins.print"):
            menu.run()
            menu.sdk.run_debate.assert_called_once()


class TestMenuInvalidOption:
    """Test invalid option handling."""

    def test_invalid_option_prints_message(self, menu: TerminalMenu) -> None:
        """Invalid option prints error message."""
        with patch("builtins.input", side_effect=["9", "4"]), patch("builtins.print") as mock_print:
            menu.run()
            mock_print.assert_any_call("Invalid option.")
