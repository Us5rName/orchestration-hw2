"""Tests: agent config values reach the agent instance attributes.

Verifies that per-agent settings (topic, model, temperature) defined in
setup.json are stored on the agent instance after creation.
"""

from unittest.mock import MagicMock, patch

from debate.sdk.sdk import DebateSDK


class TestAgentConfigToAgent:
    """Agent config values reach the agent instance attributes."""

    def test_topic_propagates_to_agent(self, base_config: dict, mock_get_factory) -> None:
        """Debate topic reaches the agent instance."""
        base_config["debate"]["topic"] = "Climate Change Policy"

        with (
            patch("debate.sdk.sdk.ConfigManager") as mock_cm,
            patch("debate.sdk.sdk.create_provider", return_value=MagicMock()),
        ):
            mock_cm.return_value.get = MagicMock(side_effect=mock_get_factory(base_config))
            sdk = DebateSDK(config_path="config/setup.json")
            agent = sdk._create_agent("pro")

            assert agent.topic == "Climate Change Policy"

    def test_agent_model_propagates(self, base_config: dict, mock_get_factory) -> None:
        """Agent model reaches the agent instance."""
        base_config["agents"]["con"]["model"] = "claude-3-sonnet"

        with (
            patch("debate.sdk.sdk.ConfigManager") as mock_cm,
            patch("debate.sdk.sdk.create_provider", return_value=MagicMock()),
        ):
            mock_cm.return_value.get = MagicMock(side_effect=mock_get_factory(base_config))
            sdk = DebateSDK(config_path="config/setup.json")
            agent = sdk._create_agent("con")

            assert agent.model == "claude-3-sonnet"

    def test_agent_temperature_propagates(self, base_config: dict, mock_get_factory) -> None:
        """Agent temperature reaches the agent instance."""
        base_config["agents"]["judge"]["temperature"] = 0.1

        with (
            patch("debate.sdk.sdk.ConfigManager") as mock_cm,
            patch("debate.sdk.sdk.create_provider", return_value=MagicMock()),
        ):
            mock_cm.return_value.get = MagicMock(side_effect=mock_get_factory(base_config))
            sdk = DebateSDK(config_path="config/setup.json")
            agent = sdk._create_agent("judge")

            assert agent.temperature == 0.1
