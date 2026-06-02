"""Structural protocols for the debate system.

Using typing.Protocol allows components to accept duck-typed objects
without importing concrete classes, avoiding circular imports.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from .config import ConfigManager


@runtime_checkable
class LoggerProtocol(Protocol):
    """Anything that can log info/debug/warning/error messages."""

    def info(self, message: str) -> None: ...
    def debug(self, message: str) -> None: ...
    def warning(self, message: str) -> None: ...
    def error(self, message: str) -> None: ...


class DebateSDKProtocol(Protocol):
    """Minimal interface that TerminalMenu needs from the SDK."""

    def run_debate(self) -> dict: ...
    def get_logs(self, count: int = 50) -> list[str]: ...
    def get_token_usage(self) -> dict[str, dict[str, int]]: ...

    @property
    def config(self) -> ConfigManager: ...

    @property
    def logger(self) -> LoggerProtocol: ...

    @property
    def log_file(self) -> Path: ...
