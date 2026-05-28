"""LogManager — structured logging with FIFO rotation.

Input: config (dict) — log_directory, max_files, max_lines_per_file, level, format
Output: configured logger with info/debug/warning/error methods
Setup: log_directory created if missing; rotation by line count
"""

import logging
import os
from pathlib import Path


class _LineRotatingHandler(logging.Handler):
    """Custom handler that rotates log files by line count."""

    def __init__(
        self,
        log_dir: str,
        max_files: int,
        max_lines: int,
        fmt: str,
    ) -> None:
        super().__init__()
        self.log_dir = Path(log_dir)
        self.max_files = max_files
        self.max_lines = max_lines
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.formatter = logging.Formatter(fmt)
        self._current_file = self.log_dir / "debate.log"

    def _rotate(self) -> None:
        """Shift log files: N-1 → N, N-2 → N-1, ..., 0 → 1, delete oldest."""
        for i in range(self.max_files - 1, 0, -1):
            old = self.log_dir / f"debate.{i}.log"
            new = self.log_dir / f"debate.{i + 1}.log"
            if old.exists():
                old.rename(new)
        if self._current_file.exists():
            self._current_file.rename(self.log_dir / "debate.1.log")

    def _check_rotation(self) -> None:
        """Rotate if current file exceeds max_lines."""
        if self._current_file.exists():
            line_count = sum(1 for _ in self._current_file.open())
            if line_count >= self.max_lines:
                self._rotate()

    def _cleanup_old(self) -> None:
        """Remove files beyond max_files."""
        logs = sorted(self.log_dir.glob("debate.*.log"))
        while len(logs) >= self.max_files:
            logs[0].unlink()
            logs = sorted(self.log_dir.glob("debate.*.log"))

    def emit(self, record: logging.LogRecord) -> None:
        """Write a log record, rotating if needed."""
        self._check_rotation()
        self._cleanup_old()
        line = self.formatter.format(record)
        with open(self._current_file, "a", encoding="utf-8") as f:
            f.write(line + os.linesep)


class LogManager:
    """
    Input: config (dict) — log_directory, max_files, max_lines_per_file,
           level, format
    Output: logger with info/debug/warning/error methods
    Setup: log_directory created if missing
    """

    def __init__(self, config: dict) -> None:
        """Initialize LogManager from config dict.

        Args:
            config: Dict with log_directory, max_files,
                    max_lines_per_file, level, format.
        """
        self.logger = logging.getLogger("debate")
        self.logger.setLevel(getattr(logging, config.get("level", "INFO").upper(), logging.INFO))
        self.logger.handlers.clear()

        handler = _LineRotatingHandler(
            log_dir=config.get("log_directory", "logs"),
            max_files=config.get("max_files", 20),
            max_lines=config.get("max_lines_per_file", 500),
            fmt=config.get(
                "format",
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            ),
        )
        self.logger.addHandler(handler)

    def info(self, message: str) -> None:
        """Log an info message."""
        self.logger.info(message)

    def debug(self, message: str) -> None:
        """Log a debug message."""
        self.logger.debug(message)

    def warning(self, message: str) -> None:
        """Log a warning message."""
        self.logger.warning(message)

    def error(self, message: str) -> None:
        """Log an error message."""
        self.logger.error(message)
