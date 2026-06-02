"""Tests for shared/paths.py — cwd-independent project path resolution."""

from pathlib import Path

import pytest

from debate.shared.paths import (
    CONFIG_DIR,
    DEFAULT_DEBATE_LOG_PATH,
    DEFAULT_LOGGING_PATH,
    DEFAULT_RATE_LIMITS_PATH,
    DEFAULT_SETUP_PATH,
    LOGS_DIR,
    PROJECT_ROOT,
    ProjectPathError,
    resolve_project_path,
)


class TestProjectRoot:
    """Test PROJECT_ROOT discovery."""

    def test_project_root_contains_pyproject(self) -> None:
        """PROJECT_ROOT has pyproject.toml."""
        assert (PROJECT_ROOT / "pyproject.toml").exists()

    def test_project_root_contains_config_dir(self) -> None:
        """PROJECT_ROOT has config/ directory."""
        assert (PROJECT_ROOT / "config").is_dir()

    def test_project_root_is_absolute(self) -> None:
        """PROJECT_ROOT is an absolute path."""
        assert PROJECT_ROOT.is_absolute()

    def test_config_dir_is_absolute(self) -> None:
        """CONFIG_DIR is an absolute path under PROJECT_ROOT."""
        assert CONFIG_DIR.is_absolute()
        assert CONFIG_DIR == PROJECT_ROOT / "config"

    def test_logs_dir_is_absolute(self) -> None:
        """LOGS_DIR is an absolute path under PROJECT_ROOT."""
        assert LOGS_DIR.is_absolute()
        assert LOGS_DIR == PROJECT_ROOT / "logs"


class TestDefaultPaths:
    """Test default path constants point to real files."""

    def test_default_setup_path_exists(self) -> None:
        """DEFAULT_SETUP_PATH points to the real setup.json."""
        assert DEFAULT_SETUP_PATH.exists()
        assert DEFAULT_SETUP_PATH.name == "setup.json"

    def test_default_rate_limits_path_exists(self) -> None:
        """DEFAULT_RATE_LIMITS_PATH points to real rate_limits.json."""
        assert DEFAULT_RATE_LIMITS_PATH.exists()

    def test_default_logging_path_exists(self) -> None:
        """DEFAULT_LOGGING_PATH points to real logging_config.json."""
        assert DEFAULT_LOGGING_PATH.exists()

    def test_all_defaults_are_absolute(self) -> None:
        """All DEFAULT_* constants are absolute paths."""
        for p in (DEFAULT_SETUP_PATH, DEFAULT_RATE_LIMITS_PATH, DEFAULT_LOGGING_PATH, DEFAULT_DEBATE_LOG_PATH):
            assert p.is_absolute(), f"{p} is not absolute"


class TestResolveProjectPath:
    """Test resolve_project_path behavior."""

    def test_relative_path_resolves_to_project_root(self) -> None:
        """Relative paths are anchored to PROJECT_ROOT."""
        resolved = resolve_project_path("config/setup.json")
        assert resolved == PROJECT_ROOT / "config" / "setup.json"
        assert resolved.is_absolute()

    def test_absolute_path_is_preserved(self, tmp_path: Path) -> None:
        """Absolute paths are returned unchanged."""
        abs_path = tmp_path / "custom.json"
        assert resolve_project_path(abs_path) == abs_path

    def test_path_object_accepted(self) -> None:
        """Path objects are accepted as well as strings."""
        resolved = resolve_project_path(Path("config/setup.json"))
        assert resolved == PROJECT_ROOT / "config" / "setup.json"

    def test_tilde_expansion(self) -> None:
        """~ is expanded in the returned path."""
        result = resolve_project_path("~/somefile.json")
        assert "~" not in str(result)
        assert result.is_absolute()

    def test_cwd_independent(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """resolve_project_path gives the same result from any CWD."""
        monkeypatch.chdir(tmp_path)
        resolved = resolve_project_path("config/setup.json")
        assert resolved == PROJECT_ROOT / "config" / "setup.json"


class TestProjectPathError:
    """Test ProjectPathError is a RuntimeError."""

    def test_project_path_error_is_runtime_error(self) -> None:
        """ProjectPathError inherits from RuntimeError."""
        exc = ProjectPathError("test")
        assert isinstance(exc, RuntimeError)
