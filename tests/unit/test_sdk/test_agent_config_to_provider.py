"""Tests: agent config values propagate through to provider creation.

Verifies that per-agent settings (model, temperature, base_url) defined in
setup.json are forwarded to the ProviderFactory when creating provider
instances.
"""

from unittest.mock import MagicMock, patch

from debate.sdk.sdk import DebateSDK


class TestAgentConfigToProvider:
    """Agent config values propagate through to provider creation."""

    def test_model_propagates_to_provider(self, base_config: dict, mock_get_factory) -> None:
        """Agent model flows from config to provider creation."""
        base_config["agents"]["judge"]["model"] = "gpt-4o"

        with (
            patch("debate.sdk.sdk.ConfigManager") as mock_cm,
            patch("debate.sdk.sdk.create_provider", return_value=MagicMock()) as mock_factory,
        ):
            mock_cm.return_value.get = MagicMock(side_effect=mock_get_factory(base_config))
            sdk = DebateSDK(config_path="config/setup.json")
            sdk._create_agent("judge")

            provider_cfg = mock_factory.call_args[0][1]
            assert provider_cfg["model"] == "gpt-4o"

    def test_temperature_propagates_to_provider(self, base_config: dict, mock_get_factory) -> None:
        """Agent temperature flows from config to provider creation."""
        base_config["agents"]["pro"]["temperature"] = 0.9

        with (
            patch("debate.sdk.sdk.ConfigManager") as mock_cm,
            patch("debate.sdk.sdk.create_provider", return_value=MagicMock()) as mock_factory,
        ):
            mock_cm.return_value.get = MagicMock(side_effect=mock_get_factory(base_config))
            sdk = DebateSDK(config_path="config/setup.json")
            sdk._create_agent("pro")

            provider_cfg = mock_factory.call_args[0][1]
            assert provider_cfg["temperature"] == 0.9

    def test_base_url_propagates_to_provider(self, base_config: dict, mock_get_factory) -> None:
        """Agent base_url flows from config to provider creation."""
        base_config["agents"]["con"]["base_url"] = "http://custom:8080/v1"

        with (
            patch("debate.sdk.sdk.ConfigManager") as mock_cm,
            patch("debate.sdk.sdk.create_provider", return_value=MagicMock()) as mock_factory,
        ):
            mock_cm.return_value.get = MagicMock(side_effect=mock_get_factory(base_config))
            sdk = DebateSDK(config_path="config/setup.json")
            sdk._create_agent("con")

            provider_cfg = mock_factory.call_args[0][1]
            assert provider_cfg["base_url"] == "http://custom:8080/v1"
