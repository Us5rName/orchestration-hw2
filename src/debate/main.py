"""Entry point for the AI debate system.

This is the only module that may call sys.exit().  All shared/library
modules raise ConfigValidationError; this module catches it and exits.
"""

import sys

from debate.cli.menu import TerminalMenu
from debate.sdk.sdk import DebateSDK
from debate.shared.config_validator import ConfigValidationError, validate_all_configs
from debate.shared.version import __version__


def main() -> None:
    """Validate config, create SDK, and launch the interactive menu."""
    try:
        validate_all_configs()
    except ConfigValidationError as exc:
        print(f"ERROR: Invalid configuration — {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    print(f"AI Debate System v{__version__}")
    sdk = DebateSDK()
    menu = TerminalMenu(sdk)
    menu.run()


if __name__ == "__main__":
    main()
