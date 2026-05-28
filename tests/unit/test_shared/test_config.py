"""Tests for ConfigManager."""

import json
from pathlib import Path

import pytest

from debate.shared.config import ConfigManager


@pytest.fixture
def sample_config(tmp_path: Path) -> str:
    """Create a temporary config file."""
    data = {"version": "1.00", "key": "value", "nested": {"a": 1}}
    path = tmp_path / "config.json"
    path.write_text(json.dumps(data))
    return str(path)


class TestConfigManagerInit:
    """Test ConfigManager initialization."""

    def test_load_valid_config(self, sample_config: str) -> None:
        """ConfigManager loads valid JSON."""
        cfg = ConfigManager(sample_config)
        assert cfg.get("key") == "value"

    def test_missing_file_raises(self) -> None:
        """ConfigManager raises FileNotFoundError for missing path."""
        with pytest.raises(FileNotFoundError):
            ConfigManager("nonexistent.json")

    def test_invalid_json_raises(self, tmp_path: Path) -> None:
        """ConfigManager raises JSONDecodeError for bad JSON."""
        bad = tmp_path / "bad.json"
        bad.write_text("{invalid}")
        with pytest.raises(json.JSONDecodeError):
            ConfigManager(str(bad))


class TestConfigManagerGet:
    """Test ConfigManager.get() accessor."""

    def test_get_existing_key(self, sample_config: str) -> None:
        """get() returns value for existing key."""
        cfg = ConfigManager(sample_config)
        assert cfg.get("key") == "value"

    def test_get_missing_returns_none(self, sample_config: str) -> None:
        """get() returns None for missing key."""
        cfg = ConfigManager(sample_config)
        assert cfg.get("missing") is None

    def test_get_with_default(self, sample_config: str) -> None:
        """get() returns default for missing key."""
        cfg = ConfigManager(sample_config)
        assert cfg.get("missing", "default") == "default"

    def test_get_nested(self, sample_config: str) -> None:
        """get() returns nested dict."""
        cfg = ConfigManager(sample_config)
        assert cfg.get("nested") == {"a": 1}


class TestConfigManagerVersion:
    """Test version access."""

    def test_get_version(self, sample_config: str) -> None:
        """get_version() returns version string."""
        cfg = ConfigManager(sample_config)
        assert cfg.get_version() == "1.00"

    def test_version_missing_raises(self, tmp_path: Path) -> None:
        """get_version() raises KeyError if no version."""
        data = {"key": "value"}
        path = tmp_path / "no_ver.json"
        path.write_text(json.dumps(data))
        cfg = ConfigManager(str(path))
        with pytest.raises(KeyError):
            cfg.get_version()
