"""Legacy shim — the real entry point is debate.main.

Run with:
    uv run debate
    python -m debate.main
"""

from debate.main import main

if __name__ == "__main__":
    main()
