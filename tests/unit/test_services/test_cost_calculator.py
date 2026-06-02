"""Tests for CostCalculator (cost_for_record, summarize_round, summarize_debate)."""

import pytest

from debate.services.cost_calculator import cost_for_record, summarize_debate, summarize_round
from debate.services.usage_record import UsageRecord


def _rec(
    role: str = "pro",
    inp: int = 1000,
    out: int = 500,
    available: bool = True,
    round_number: int = 1,
) -> UsageRecord:
    return UsageRecord(
        provider_name="openai",
        model="gpt-4o-mini",
        role=role,
        input_tokens=inp,
        output_tokens=out,
        total_tokens=inp + out,
        round_number=round_number,
        available=available,
    )


_PRICING = {
    "unit": "per_1m_tokens",
    "judge": {"input": 0.15, "output": 0.60},
    "pro": {"input": 0.15, "output": 0.60},
    "con": {"input": 0.15, "output": 0.60},
}

_PRICING_1K = {
    "unit": "per_1k_tokens",
    "pro": {"input": 0.002, "output": 0.002},
}


class TestCostForRecord:
    """Test cost_for_record."""

    def test_basic_cost_calculation(self) -> None:
        """Cost = input*rate/div + output*rate/div."""
        rec = _rec(role="pro", inp=1_000_000, out=1_000_000)
        cost = cost_for_record(rec, _PRICING)
        assert cost == pytest.approx(0.15 + 0.60)

    def test_unavailable_returns_zero(self) -> None:
        """Unavailable record yields zero cost."""
        rec = _rec(available=False, inp=9999, out=9999)
        assert cost_for_record(rec, _PRICING) == 0.0

    def test_missing_role_returns_zero(self) -> None:
        """Role absent from pricing config yields zero cost."""
        rec = _rec(role="unknown_role", inp=1000, out=500)
        assert cost_for_record(rec, _PRICING) == 0.0

    def test_per_1k_unit(self) -> None:
        """per_1k_tokens unit divides by 1000."""
        rec = _rec(role="pro", inp=1000, out=1000)
        cost = cost_for_record(rec, _PRICING_1K)
        assert cost == pytest.approx(0.002 + 0.002)

    def test_small_token_count(self) -> None:
        """Small token counts produce small costs."""
        rec = _rec(role="pro", inp=100, out=50)
        cost = cost_for_record(rec, _PRICING)
        assert cost == pytest.approx(100 * 0.15 / 1_000_000 + 50 * 0.60 / 1_000_000)


class TestSummarizeRound:
    """Test summarize_round."""

    def test_aggregates_two_records(self) -> None:
        """Round summary combines pro and con costs."""
        records = [_rec("pro", 1_000_000, 0), _rec("con", 0, 1_000_000, round_number=1)]
        summary = summarize_round(records, _PRICING)
        assert summary["round"] == 1
        assert summary["total_cost_usd"] == pytest.approx(0.15 + 0.60)
        assert len(summary["breakdown"]) == 2

    def test_unavailable_record_in_breakdown(self) -> None:
        """Unavailable record appears in breakdown with available=False."""
        records = [_rec("pro", available=False)]
        summary = summarize_round(records, _PRICING)
        assert summary["breakdown"][0]["available"] is False
        assert summary["total_cost_usd"] == 0.0

    def test_empty_records_returns_zero_round(self) -> None:
        """Empty record list returns round=0."""
        summary = summarize_round([], _PRICING)
        assert summary["round"] == 0
        assert summary["total_cost_usd"] == 0.0


class TestSummarizeDebate:
    """Test summarize_debate."""

    def test_total_tokens_summed(self) -> None:
        """Total tokens = sum of all records."""
        records = [_rec("pro", 100, 50), _rec("con", 200, 80), _rec("judge", 300, 120, round_number=0)]
        summary = summarize_debate(records, _PRICING)
        assert summary["total_input_tokens"] == 600
        assert summary["total_output_tokens"] == 250
        assert summary["total_tokens"] == 850

    def test_by_role_grouping(self) -> None:
        """by_role aggregates across multiple rounds."""
        records = [
            _rec("pro", 100, 50, round_number=1),
            _rec("pro", 200, 80, round_number=2),
            _rec("con", 150, 60, round_number=1),
        ]
        summary = summarize_debate(records, _PRICING)
        assert summary["by_role"]["pro"]["input_tokens"] == 300
        assert summary["by_role"]["pro"]["output_tokens"] == 130

    def test_total_cost_usd_present(self) -> None:
        """total_cost_usd key is present and non-negative."""
        records = [_rec("pro", 1000, 500)]
        summary = summarize_debate(records, _PRICING)
        assert summary["total_cost_usd"] >= 0.0
