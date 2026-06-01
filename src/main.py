"""Entry point for the AI debate system."""

from debate.cli.menu import TerminalMenu
from debate.sdk.sdk import DebateSDK
from debate.shared.config_validator import validate_all_configs
from debate.shared.version import __version__


def main() -> None:
    """Main entry point — validate config, create SDK, launch menu."""
    validate_all_configs()
    print(f"AI Debate System v{__version__}")
    sdk = DebateSDK()
    menu = TerminalMenu(sdk)
    menu.run()


if __name__ == "__main__":
    main()
