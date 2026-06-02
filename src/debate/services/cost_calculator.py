"""CostCalculator — pure token-cost math, independent of provider code.

Input: UsageRecord instances + pricing config dict from setup.json
Output: float costs per call / per round / per debate
Setup: stateless module; pricing unit is per_1m_tokens (default)
       Pricing config shape: {"unit": "per_1m_tokens", "pro": {"input": N, "output": N}, ...}
"""

from .usage_record import UsageRecord

_UNIT_DIVISORS: dict[str, float] = {
    "per_1m_tokens": 1_000_000.0,
    "per_1k_tokens": 1_000.0,
}


def _divisor(unit: str) -> float:
    """Return the token divisor for the given pricing unit string."""
    return _UNIT_DIVISORS.get(unit, 1_000_000.0)


def cost_for_record(record: UsageRecord, pricing_config: dict) -> float:
    """Compute the USD cost for a single UsageRecord.

    Args:
        record: Token usage for one LLM call.
        pricing_config: Dict from setup.json 'pricing' section.

    Returns:
        Cost in USD; 0.0 when usage is unavailable or role not in pricing.
    """
    if not record.available:
        return 0.0
    role_cfg = pricing_config.get(record.role, {})
    if not role_cfg:
        return 0.0
    div = _divisor(pricing_config.get("unit", "per_1m_tokens"))
    return (
        record.input_tokens * role_cfg.get("input", 0.0) / div
        + record.output_tokens * role_cfg.get("output", 0.0) / div
    )


def summarize_round(records: list[UsageRecord], pricing_config: dict) -> dict:
    """Aggregate token usage and cost for one debate round.

    Args:
        records: UsageRecords for the round (typically pro + con).
        pricing_config: Dict from setup.json 'pricing' section.

    Returns:
        Dict with round number, per-agent breakdown, and total_cost_usd.
    """
    breakdown = []
    total_cost = 0.0
    for rec in records:
        cost = cost_for_record(rec, pricing_config)
        total_cost += cost
        breakdown.append({
            "role": rec.role,
            "provider": rec.provider_name,
            "model": rec.model,
            "input_tokens": rec.input_tokens,
            "output_tokens": rec.output_tokens,
            "total_tokens": rec.total_tokens,
            "cost_usd": round(cost, 6),
            "available": rec.available,
        })
    return {
        "round": records[0].round_number if records else 0,
        "breakdown": breakdown,
        "total_cost_usd": round(total_cost, 6),
    }


def summarize_debate(all_records: list[UsageRecord], pricing_config: dict) -> dict:
    """Aggregate token usage and cost across the full debate.

    Args:
        all_records: All UsageRecords collected (all rounds + judge).
        pricing_config: Dict from setup.json 'pricing' section.

    Returns:
        Dict with total tokens, per-role breakdown, and total_cost_usd.
    """
    total_in = sum(r.input_tokens for r in all_records)
    total_out = sum(r.output_tokens for r in all_records)
    total_cost = 0.0
    by_role: dict[str, dict] = {}
    for rec in all_records:
        cost = cost_for_record(rec, pricing_config)
        total_cost += cost
        entry = by_role.setdefault(
            rec.role, {"input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0}
        )
        entry["input_tokens"] += rec.input_tokens
        entry["output_tokens"] += rec.output_tokens
        entry["cost_usd"] = round(entry["cost_usd"] + cost, 6)
    return {
        "total_input_tokens": total_in,
        "total_output_tokens": total_out,
        "total_tokens": total_in + total_out,
        "total_cost_usd": round(total_cost, 6),
        "by_role": by_role,
    }
