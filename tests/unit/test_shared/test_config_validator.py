"""Tests for config_validator module."""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


class TestValidateConfigVersion:
    """Test config version validation."""

    def test_valid_version_passes(self, tmp_path: Path) -> None:
        """Valid version does not raise."""
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({"version": "1.00"}))
        # Should not raise
        from debate.shared.config_validator import validate_config_version

        validate_config_version(str(config_file))

    def test_missing_version_raises(self, tmp_path: Path) -> None:
        """Missing version key triggers sys.exit."""
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({"other": "data"}))
        with patch.object(sys, "exit") as mock_exit:
            from debate.shared.config_validator import validate_config_version

            validate_config_version(str(config_file))
            assert mock_exit.call_count >= 1

    def test_version_mismatch_raises(self, tmp_path: Path) -> None:
        """Version mismatch raises SystemExit."""
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({"version": "0.99"}))
        with patch.object(sys, "exit"):
            from debate.shared.config_validator import validate_config_version

            validate_config_version(str(config_file))
            sys.exit.assert_called_once()

    def test_missing_file_raises(self) -> None:
        """Missing file triggers sys.exit."""
        with patch.object(sys, "exit", side_effect=SystemExit(1)):
            from debate.shared.config_validator import validate_config_version

            with pytest.raises(SystemExit):
                validate_config_version("nonexistent.json")


class TestValidateAllConfigs:
    """Test validating all configs."""

    def test_validates_all_files(self, tmp_path: Path) -> None:
        """All config files are validated."""
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
        from debate.shared.config_validator import validate_all_configs

        validate_all_configs(str(setup), str(rate), str(logging_cfg))
