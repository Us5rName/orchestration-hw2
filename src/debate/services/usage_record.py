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


def build_from_delta(
    provider_name: str,
    model: str,
    role: str,
    snapshot_before: dict,
    snapshot_after: dict,
    round_number: int,
) -> "UsageRecord":
    """Build a UsageRecord from cumulative usage snapshots taken before and after a call.

    Args:
        provider_name: Provider identifier string.
        model: Model name string.
        role: Agent role ('judge', 'pro', 'con').
        snapshot_before: get_usage() result captured before the agent call.
        snapshot_after: get_usage() result captured after the agent call.
        round_number: Debate round number; 0 for judge evaluation.

    Returns:
        UsageRecord with delta tokens; available=False when both deltas are zero.
    """
    in_d = max(int(snapshot_after.get("input_tokens", 0)) - int(snapshot_before.get("input_tokens", 0)), 0)
    out_d = max(int(snapshot_after.get("output_tokens", 0)) - int(snapshot_before.get("output_tokens", 0)), 0)
    return UsageRecord(
        provider_name=provider_name,
        model=model,
        role=role,
        input_tokens=in_d,
        output_tokens=out_d,
        total_tokens=in_d + out_d,
        round_number=round_number,
        available=in_d > 0 or out_d > 0,
    )
