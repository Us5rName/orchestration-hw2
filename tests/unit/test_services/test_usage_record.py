"""Tests for UsageRecord and build_from_delta."""

from debate.services.usage_record import UsageRecord, build_from_delta


class TestUsageRecord:
    """Test UsageRecord dataclass."""

    def test_fields_stored(self) -> None:
        """All fields are stored correctly."""
        rec = UsageRecord(
            provider_name="openai",
            model="gpt-4o-mini",
            role="pro",
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            round_number=1,
            available=True,
        )
        assert rec.provider_name == "openai"
        assert rec.model == "gpt-4o-mini"
        assert rec.role == "pro"
        assert rec.input_tokens == 100
        assert rec.output_tokens == 50
        assert rec.total_tokens == 150
        assert rec.round_number == 1
        assert rec.available is True

    def test_available_false_when_zero_tokens(self) -> None:
        """available=False signals provider returned no metadata."""
        rec = UsageRecord(
            provider_name="openai", model="m", role="con",
            input_tokens=0, output_tokens=0, total_tokens=0,
            round_number=2, available=False,
        )
        assert rec.available is False


class TestBuildFromDelta:
    """Test build_from_delta factory function."""

    def _snap(self, inp: int, out: int) -> dict:
        return {"input_tokens": inp, "output_tokens": out}

    def test_delta_computed_correctly(self) -> None:
        """Token delta = after - before."""
        rec = build_from_delta("openai", "gpt-4o-mini", "pro",
                               self._snap(100, 40), self._snap(160, 65), 1)
        assert rec.input_tokens == 60
        assert rec.output_tokens == 25
        assert rec.total_tokens == 85
        assert rec.available is True

    def test_available_false_when_no_delta(self) -> None:
        """available=False when both deltas are zero."""
        snap = self._snap(100, 40)
        rec = build_from_delta("openai", "gpt-4o-mini", "judge", snap, snap, 0)
        assert rec.available is False
        assert rec.input_tokens == 0

    def test_negative_delta_clamped_to_zero(self) -> None:
        """Negative delta (counter reset) is clamped to 0."""
        rec = build_from_delta("openai", "m", "con",
                               self._snap(200, 80), self._snap(10, 5), 2)
        assert rec.input_tokens == 0
        assert rec.output_tokens == 0

    def test_round_number_stored(self) -> None:
        """round_number is stored in the record."""
        rec = build_from_delta("openai", "m", "pro",
                               self._snap(0, 0), self._snap(50, 20), 3)
        assert rec.round_number == 3

    def test_metadata_propagated(self) -> None:
        """provider_name, model, role are stored unchanged."""
        rec = build_from_delta("anthropic", "claude-3", "judge",
                               self._snap(0, 0), self._snap(10, 5), 0)
        assert rec.provider_name == "anthropic"
        assert rec.model == "claude-3"
        assert rec.role == "judge"
