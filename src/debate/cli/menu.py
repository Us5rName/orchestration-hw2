"""TerminalMenu — interactive CLI for the debate system.

Input: sdk (DebateSDK)
Output: interactive menu loop with options
Setup: delegates all logic to SDK
"""


class TerminalMenu:
    """
    Input: sdk (DebateSDK)
    Output: interactive menu loop
    Setup: thin presentation layer, delegates to SDK
    """

    def __init__(self, sdk: object) -> None:
        """Initialize menu with SDK.

        Args:
            sdk: DebateSDK instance for all operations.
        """
        self.sdk = sdk

    def run(self) -> None:
        """Run the interactive menu loop."""
        print("=== AI Debate System ===")
        while True:
            self._print_menu()
            choice = input("Select option: ").strip()
            if choice == "1":
                self._start_debate()
            elif choice == "2":
                self._view_logs()
            elif choice == "3":
                print("Configuration loaded from config/setup.json")
            elif choice == "4":
                print("Goodbye!")
                break
            else:
                print("Invalid option.")

    def _print_menu(self) -> None:
        """Print the menu options."""
        print("\n1. Start Debate")
        print("2. View Logs")
        print("3. Configuration")
        print("4. Exit")

    def _start_debate(self) -> None:
        """Start a debate via SDK and print results."""
        print("\nStarting debate...\n")
        result = self.sdk.run_debate()
        print(f"Winner: {result.get('winner')}")
        print(f"Pro Score: {result.get('pro_score')}")
        print(f"Con Score: {result.get('con_score')}")
        print(f"Justification: {result.get('justification')}")

    def _view_logs(self) -> None:
        """View recent logs via SDK."""
        logs = self.sdk.get_logs(count=20)
        print("\n--- Recent Logs ---")
        for line in logs:
            print(line)
