"""Shared contract assertions for all LLM provider tests.

These helpers encode the LLMProvider contract: every concrete provider
must store base attributes and accumulate token usage correctly.
Importing them in vendor-specific test files means Branch 3 can
migrate to ProviderResult by changing these helpers in one place.
"""

from debate.providers.base_provider import LLMProvider


def assert_base_attrs(
    prov: LLMProvider,
    expected_model: str,
    expected_temperature: float,
) -> None:
    """Assert that base LLMProvider attributes are stored correctly."""
    assert prov.model == expected_model
    assert prov.temperature == expected_temperature


def assert_usage_zero(prov: LLMProvider) -> None:
    """Assert that a provider's cumulative usage counters are at zero."""
    usage = prov.get_usage()
    assert usage == {"input_tokens": 0, "output_tokens": 0}


def assert_usage_recorded(
    prov: LLMProvider,
    expected_input: int,
    expected_output: int,
) -> None:
    """Assert that a provider recorded the expected token counts."""
    usage = prov.get_usage()
    assert usage["input_tokens"] == expected_input
    assert usage["output_tokens"] == expected_output
