"""UsageRecord — structured token usage from one LLM provider call.

Input: provider_name, model, role, token counts, round_number, available flag
Output: dataclass consumed by CostCalculator and round-level logging
Setup: no external dependencies; imported by orchestrator and cost_calculator
"""

from dataclasses import dataclass


@dataclass
class UsageRecord:
    """Token usage for one LLM call within the debate.

    Attributes:
        provider_name: Provider identifier (openai, anthropic, gemini).
        model: Model name used for the call.
        role: Agent role (judge, pro, con).
        input_tokens: Prompt/input token count.
        output_tokens: Completion/output token count.
        total_tokens: input_tokens + output_tokens.
        round_number: Debate round this call belongs to; 0 = judge evaluation.
        available: False when the provider returned no usage metadata.
    """

    provider_name: str
    model: str
    role: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    round_number: int
    available: bool