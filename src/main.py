"""Entry point for the AI debate system."""

from debate.shared.config_validator import validate_all_configs
from debate.shared.version import __version__


def main() -> None:
    """Main entry point."""
    validate_all_configs()
    print(f"AI Debate System v{__version__}")


if __name__ == "__main__":
    main()
