"""Centralized project path resolution — single source of truth for all paths.

PROJECT_ROOT is discovered by walking upward from this file until a directory
containing both pyproject.toml and config/ is found.  All other modules should
import path constants from here instead of computing or guessing them.

Input:  __file__ location (auto-detected)
Output: PROJECT_ROOT, CONFIG_DIR, LOGS_DIR, DEFAULT_* constants,
        resolve_project_path(), require_file(), require_dir()
"""

from pathlib import Path


class ProjectPathError(RuntimeError):
    """Raised when project paths cannot be resolved."""


def _find_project_root() -> Path:
    """Walk upward from this file until finding pyproject.toml + config/.

    Returns:
        Absolute Path to the project root directory.

    Raises:
        ProjectPathError: If no ancestor directory satisfies both conditions.
    """
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "pyproject.toml").exists() and (current / "config").is_dir():
            return current
        current = current.parent
    raise ProjectPathError(
        "Project root not found — no ancestor directory contains both "
        "pyproject.toml and config/"
    )


PROJECT_ROOT: Path = _find_project_root()
CONFIG_DIR: Path = PROJECT_ROOT / "config"
LOGS_DIR: Path = PROJECT_ROOT / "logs"

DEFAULT_SETUP_PATH: Path = CONFIG_DIR / "setup.json"
DEFAULT_RATE_LIMITS_PATH: Path = CONFIG_DIR / "rate_limits.json"
DEFAULT_LOGGING_PATH: Path = CONFIG_DIR / "logging_config.json"
DEFAULT_DEBATE_LOG_PATH: Path = LOGS_DIR / "debate.log"


def resolve_project_path(path: str | Path) -> Path:
    """Resolve path relative to PROJECT_ROOT; preserve absolute paths.

    Rules:
        - Absolute paths are returned unchanged (after expanduser).
        - Relative paths are anchored to PROJECT_ROOT.
        - Supports ~ home-directory expansion.

    Args:
        path: A string or Path (absolute or relative).

    Returns:
        An absolute Path.
    """
    p = Path(path).expanduser()
    if p.is_absolute():
        return p
    return PROJECT_ROOT / p


def require_file(path: str | Path) -> Path:
    """Resolve path and raise ProjectPathError if it is not an existing file.

    Args:
        path: A string or Path.

    Returns:
        Resolved absolute Path to an existing file.

    Raises:
        ProjectPathError: If the resolved path does not exist or is not a file.
    """
    resolved = resolve_project_path(path)
    if not resolved.is_file():
        raise ProjectPathError(f"Required file not found: {resolved}")
    return resolved


def require_dir(path: str | Path) -> Path:
    """Resolve path and raise ProjectPathError if it is not an existing directory.

    Args:
        path: A string or Path.

    Returns:
        Resolved absolute Path to an existing directory.

    Raises:
        ProjectPathError: If the resolved path does not exist or is not a directory.
    """
    resolved = resolve_project_path(path)
    if not resolved.is_dir():
        raise ProjectPathError(f"Required directory not found: {resolved}")
    return resolved
