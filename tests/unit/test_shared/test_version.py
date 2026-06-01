"""Tests for version module."""

from debate.shared.version import REQUIRED_CONFIG_VERSION, __version__


class TestVersion:
    """Test version constants."""

    def test_version_exists(self) -> None:
        """__version__ is defined."""
        assert __version__ == "1.00"

    def test_required_config_version_exists(self) -> None:
        """REQUIRED_CONFIG_VERSION is defined."""
        assert REQUIRED_CONFIG_VERSION == "1.00"
