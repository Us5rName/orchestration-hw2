"""ConfigManager — load and access JSON configuration files.

Input: path (str) — path to a JSON config file
Output: dict-like accessor via get(), version via get_version()
Setup: file must exist and contain valid JSON
"""

import json
from pathlib import Path


class ConfigManager:
    """
    Input: path (str) — path to JSON config file
    Output: get(key, default) -> any, get_version() -> str
    Setup: valid JSON file with optional "version" key
    """

    def __init__(self, path: str) -> None:
        """Load config from JSON file.

        Args:
            path: Path to the JSON config file.

        Raises:
            FileNotFoundError: If the config file does not exist.
            json.JSONDecodeError: If the file contains invalid JSON.
        """
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(file_path, encoding="utf-8") as f:
            self._data: dict = json.load(f)

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
