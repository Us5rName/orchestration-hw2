"""Shared fixtures for SDK config propagation tests.

Provides reusable config and mock helpers so propagation tests stay
focused on their specific concern rather than setup boilerplate.
"""

from collections.abc import Callable

import pytest


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
