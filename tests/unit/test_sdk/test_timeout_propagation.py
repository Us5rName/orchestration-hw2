"""Tests: timeout flows from debate config to providers and agents.

Verifies that request_timeout_seconds defined in setup.json actually reaches
both the Provider (for API calls) and the Agent (for storage). This catches
the disconnect where config values are read but never forwarded.
"""

from unittest.mock import MagicMock, patch

from debate.sdk.sdk import DebateSDK
from debate.shared.paths import DEFAULT_SETUP_PATH
from tests.unit.test_sdk.conftest import apply_typed_config


class TestTimeoutPropagation:
    """Timeout flows from debate config to providers and agents."""

    def test_timeout_reaches_provider(self, base_config: dict, mock_get_factory) -> None:
        """request_timeout_seconds flows from config to provider creation."""
        base_config["debate"]["request_timeout_seconds"] = 600

        with (
            patch("debate.sdk.sdk.ConfigManager") as mock_cm,
            patch("debate.sdk.sdk.create_provider", return_value=MagicMock()) as mock_factory,
        ):
            mock_cm.return_value.get = MagicMock(side_effect=mock_get_factory(base_config))
            apply_typed_config(mock_cm.return_value, base_config)
            sdk = DebateSDK(config_path=DEFAULT_SETUP_PATH)
            sdk._create_agent("judge")

            provider_cfg = mock_factory.call_args[0][1]
            assert provider_cfg["timeout"] == 600

    def test_timeout_propagates_to_agent(self, base_config: dict, mock_get_factory) -> None:
        """request_timeout_seconds reaches the agent instance."""
        base_config["debate"]["request_timeout_seconds"] = 450

        with (
            patch("debate.sdk.sdk.ConfigManager") as mock_cm,
            patch("debate.sdk.sdk.create_provider", return_value=MagicMock()),
        ):
            mock_cm.return_value.get = MagicMock(side_effect=mock_get_factory(base_config))
            apply_typed_config(mock_cm.return_value, base_config)
            sdk = DebateSDK(config_path=DEFAULT_SETUP_PATH)
            agent = sdk._create_agent("judge")

            assert agent.timeout == 450
