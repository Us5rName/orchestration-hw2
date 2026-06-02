"""Shared fixtures for SDK config propagation tests.

Provides reusable config and mock helpers so propagation tests stay
focused on their specific concern rather than setup boilerplate.
"""

from collections.abc import Callable
from unittest.mock import MagicMock

import pytest

from debate.shared.config_models import AgentConfig, DebateConfig, LoggingConfig, PricingConfig
from debate.shared.gatekeeper import RateLimitConfig


def _base_config() -> dict:
    """Return minimal valid config for propagation tests."""
    return {
        "version": "1.00",
        "debate": {
            "topic": "AI is beneficial",
            "max_rounds": 3,
            "request_timeout_seconds": 60,
        },
        "agents": {
            "judge": {"provider": "openai", "model": "gpt-4o-mini", "temperature": 0.3},
            "pro": {"provider": "openai", "model": "gpt-4o-mini", "temperature": 0.7},
            "con": {"provider": "openai", "model": "gpt-4o-mini", "temperature": 0.7},
        },
        "gatekeeper": {
            "requests_per_minute": 30,
            "requests_per_hour": 500,
            "max_retries": 3,
            "retry_delay_seconds": 5,
        },
        "logging": {
            "log_directory": "logs",
            "max_files": 20,
            "max_lines_per_file": 500,
        },
    }


@pytest.fixture
def base_config() -> dict:
    """Fresh copy of base config for each test."""
    return _base_config()


@pytest.fixture
def mock_get_factory() -> Callable[[dict], Callable]:
    """Factory that creates a mock ConfigManager.get callback for a config dict."""

    def factory(config_data: dict) -> Callable:
        def mock_get(key: str, default=None):
            return config_data.get(key, default)

        return mock_get

    return factory


def apply_typed_config(mock_cm_instance: MagicMock, config_data: dict) -> None:
    """Configure mock ConfigManager instance with all typed property accessors.

    Call after setting up mock_cm.return_value so that both the legacy .get()
    and the new typed properties (logging_config, debate_config, etc.) work.
    """
    debate = config_data.get("debate", {})
    timeout = float(debate.get("request_timeout_seconds", 60))

    mock_cm_instance.logging_config = LoggingConfig.from_dict(config_data.get("logging", {}))
    mock_cm_instance.debate_config = DebateConfig.from_dict(debate)
    mock_cm_instance.pricing_config = PricingConfig.from_dict(config_data.get("pricing", {}))
    gate = config_data.get("gatekeeper", {})
    mock_cm_instance.gatekeeper_config = RateLimitConfig(
        requests_per_minute=gate.get("requests_per_minute", 30),
        requests_per_hour=gate.get("requests_per_hour", 500),
        max_retries=gate.get("max_retries", 3),
        retry_after_seconds=float(gate.get("retry_delay_seconds", 5)),
    )
    mock_cm_instance.agent_config = lambda role: AgentConfig.from_dict(
        {**config_data.get("agents", {}).get(role, {}), "timeout": timeout}
    )
