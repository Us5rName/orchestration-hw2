"""ConfigManager — load and access JSON configuration files.

Input: path (str | Path | None) — config file; None → DEFAULT_SETUP_PATH
Output: dict-like accessor via get(), version via get_version()
Setup: relative paths resolved via resolve_project_path (project-root-anchored)
"""

import json
from pathlib import Path

from .paths import DEFAULT_SETUP_PATH, resolve_project_path


class ConfigManager:
    """
    Input: path (str | Path | None) — JSON config file
    Output: get(key, default) -> any, get_version() -> str
    Setup: valid JSON file with optional "version" key
    """

    def __init__(self, path: str | Path | None = None) -> None:
        """Load config from JSON file.

        Args:
            path: Path to JSON config file.  None uses DEFAULT_SETUP_PATH.
                  Relative paths are resolved relative to the project root.

        Raises:
            FileNotFoundError: If the resolved config file does not exist.
            json.JSONDecodeError: If the file contains invalid JSON.
        """
        self.path: Path = resolve_project_path(path if path is not None else DEFAULT_SETUP_PATH)
        self._data: dict = self._load_config()

    def _load_config(self) -> dict:
        if not self.path.exists():
            raise FileNotFoundError(f"Config file not found: {self.path}")
        with self.path.open(encoding="utf-8") as f:
            return json.load(f)

    def get(self, key: str, default: object = None) -> object:
        """Get a config value by key.

        Args:
            key: The config key to look up.
            default: Value returned if key is missing.

        Returns:
            The config value, or default if key not found.
        """
        return self._data.get(key, default)

    def get_version(self) -> str:
        """Get the config file version.

        Returns:
            Version string from the "version" key.

        Raises:
            KeyError: If "version" key is missing.
        """
        if "version" not in self._data:
            raise KeyError("Config file missing 'version' key")
        return self._data["version"]
