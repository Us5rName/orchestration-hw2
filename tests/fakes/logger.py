"""FakeLogger — typed test double implementing LoggerProtocol."""

from debate.shared.protocols import LoggerProtocol


class FakeLogger:
    """Records log calls for assertion in tests.

    Implements LoggerProtocol so it passes isinstance checks.
    Access recorded messages via the .messages property.
    """

    def __init__(self) -> None:
        self._messages: list[str] = []

    def info(self, message: str) -> None:
        self._messages.append(message)

    def debug(self, message: str) -> None:
        self._messages.append(message)

    def warning(self, message: str) -> None:
        self._messages.append(message)

    def error(self, message: str) -> None:
        self._messages.append(message)

    @property
    def messages(self) -> list[str]:
        """Return a snapshot of all recorded log messages."""
        return list(self._messages)


assert isinstance(FakeLogger(), LoggerProtocol), "FakeLogger must satisfy LoggerProtocol"
