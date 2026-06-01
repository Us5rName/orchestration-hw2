"""ProviderFactory — creates LLM provider instances from configuration.

Input: provider_type (str), config dict with model/temperature/etc.
Output: LLMProvider instance (OpenAI, Anthropic, or Gemini)
Setup: reads API keys from environment variables
"""

import os

from ..providers.anthropic_provider import AnthropicProvider
from ..providers.base_provider import LLMProvider
from ..providers.gemini_provider import GeminiProvider
from ..providers.openai_provider import OpenAIProvider


def create_provider(provider_type: str, config: dict) -> LLMProvider:
    """Create an LLM provider instance from configuration.

    Args:
        provider_type: Provider name ('openai', 'anthropic', 'gemini').
        config: Dict with model, base_url, temperature, timeout.

    Returns:
        Configured LLMProvider instance.

    Raises:
        ValueError: If provider_type is not supported.
    """
    model = config.get("model", "gpt-4o-mini")
    base_url = config.get("base_url")
    temperature = config.get("temperature", 0.7)
    timeout = config.get("timeout", 60)

    if provider_type == "openai":
        return OpenAIProvider(
            model=model,
            base_url=base_url,
            temperature=temperature,
            timeout=timeout,
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
    if provider_type == "anthropic":
        return AnthropicProvider(
            model=model,
            base_url=base_url,
            temperature=temperature,
            timeout=timeout,
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
        )
    if provider_type == "gemini":
        return GeminiProvider(
            model=model,
            base_url=base_url,
            temperature=temperature,
            timeout=timeout,
            api_key=os.environ.get("GOOGLE_GENAI_API_KEY"),
        )

    raise ValueError(f"Unsupported provider: {provider_type}")
