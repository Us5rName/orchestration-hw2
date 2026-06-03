"""Tests for config_validator module — version and all-configs validation."""

import json
from pathlib import Path

import pytest

from debate.shared.config_validator import (
    ConfigValidationError,
    validate_all_configs,
    validate_config_version,
)


class TestValidateConfigVersion:
    """Test config version validation."""

    def test_valid_version_passes(self, tmp_path: Path) -> None:
        """Valid version does not raise."""
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({"version": "1.00"}))
        validate_config_version(str(config_file))  # must not raise

    def test_invalid_json_raises(self, tmp_path: Path) -> None:
        """Malformed JSON raises ConfigValidationError."""
        bad = tmp_path / "bad.json"
        bad.write_text("{not valid json")
        with pytest.raises(ConfigValidationError, match="Invalid JSON"):
            validate_config_version(str(bad))

    def test_missing_version_raises(self, tmp_path: Path) -> None:
        """Missing version key raises ConfigValidationError."""
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({"other": "data"}))
        with pytest.raises(ConfigValidationError, match="version"):
            validate_config_version(str(config_file))

    def test_version_mismatch_raises(self, tmp_path: Path) -> None:
        """Version mismatch raises ConfigValidationError."""
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({"version": "0.99"}))
        with pytest.raises(ConfigValidationError, match="mismatch"):
            validate_config_version(str(config_file))

    def test_missing_file_raises(self) -> None:
        """Missing file raises ConfigValidationError."""
        with pytest.raises(ConfigValidationError, match="not found"):
            validate_config_version(str(Path("/nonexistent/path/config.json")))


class TestValidateAllConfigs:
    """Test validating all configs."""

    def _write_valid_files(self, tmp_path: Path) -> tuple[Path, Path, Path]:
        """Write minimal valid config files to tmp_path."""
        pricing = {
            "unit": "per_1m_tokens",
            "judge": {"input": 0.15, "output": 0.60},
            "pro": {"input": 0.15, "output": 0.60},
            "con": {"input": 0.15, "output": 0.60},
        }
        setup = tmp_path / "setup.json"
        setup.write_text(json.dumps({"version": "1.00", "pricing": pricing}))
        logging_cfg = tmp_path / "logging.json"
        logging_cfg.write_text(json.dumps({"version": "1.00"}))
        rate = tmp_path / "rate.json"
        rate.write_text(json.dumps({"rate_limits": {"version": "1.00"}}))
        return setup, rate, logging_cfg

    def test_validates_all_files(self, tmp_path: Path) -> None:
        """All valid config files pass without raising."""
        setup, rate, logging_cfg = self._write_valid_files(tmp_path)
        validate_all_configs(str(setup), str(rate), str(logging_cfg))

    def test_works_from_any_cwd(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """validate_all_configs works regardless of current working directory."""
        monkeypatch.chdir(tmp_path)
        validate_all_configs()  # Uses real project config — must not raise

    def test_rate_limits_version_mismatch_raises(self, tmp_path: Path) -> None:
        """Nested rate_limits version mismatch raises ConfigValidationError."""
        pricing = {"unit": "per_1m_tokens",
                   "judge": {"input": 0.15, "output": 0.60},
                   "pro": {"input": 0.15, "output": 0.60},
                   "con": {"input": 0.15, "output": 0.60}}
        setup = tmp_path / "setup.json"
        setup.write_text(json.dumps({"version": "1.00", "pricing": pricing}))
        logging_cfg = tmp_path / "logging.json"
        logging_cfg.write_text(json.dumps({"version": "1.00"}))
        rate = tmp_path / "rate.json"
        rate.write_text(json.dumps({"rate_limits": {"version": "0.00"}}))
        with pytest.raises(ConfigValidationError, match="mismatch"):
            validate_all_configs(str(setup), str(rate), str(logging_cfg))

    def test_pricing_error_raises(self, tmp_path: Path) -> None:
        """Missing pricing in setup.json raises ConfigValidationError."""
        setup = tmp_path / "setup.json"
        setup.write_text(json.dumps({"version": "1.00"}))
        logging_cfg = tmp_path / "logging.json"
        logging_cfg.write_text(json.dumps({"version": "1.00"}))
        rate = tmp_path / "rate.json"
        rate.write_text(json.dumps({"rate_limits": {"version": "1.00"}}))
        with pytest.raises(ConfigValidationError, match="pricing"):
            validate_all_configs(str(setup), str(rate), str(logging_cfg))
