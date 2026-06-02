"""Config version and skill-role validation at startup.

All functions raise ConfigValidationError on invalid configuration.
The application entry point (main.py) is responsible for catching
ConfigValidationError and converting it to SystemExit.
"""

import json
from pathlib import Path

from .paths import (
    DEFAULT_LOGGING_PATH,
    DEFAULT_RATE_LIMITS_PATH,
    DEFAULT_SETUP_PATH,
    resolve_project_path,
)
from .version import REQUIRED_CONFIG_VERSION

_JUDGE_SKILLS: frozenset[str] = frozenset({"persuasion-scoring"})
_DEBATER_SKILLS: frozenset[str] = frozenset({"research-analysis", "quality-standards"})
_VALID_PRICING_UNITS: frozenset[str] = frozenset({"per_1m_tokens", "per_1k_tokens"})
_PRICING_ROLES: frozenset[str] = frozenset({"judge", "pro", "con"})


class ConfigValidationError(RuntimeError):
    """Raised when project configuration is invalid."""


def _load_json(path: Path) -> dict:
    """Load JSON from path; raise ConfigValidationError on any failure."""
    if not path.exists():
        raise ConfigValidationError(f"Config file not found: {path}")
    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise ConfigValidationError(f"Invalid JSON in {path}: {exc}") from exc


def validate_config_version(path: str | Path, version_key: str = "version") -> None:
    """Validate that a config file's version matches the required version.

    Args:
        path: Path to the JSON config file (absolute or relative to project root).
        version_key: Key that holds the version string.

    Raises:
        ConfigValidationError: If version is missing, mismatched, or file is absent.
    """
    resolved = resolve_project_path(path)
    data = _load_json(resolved)
    file_version = data.get(version_key)
    if file_version is None:
        raise ConfigValidationError(f"No '{version_key}' key in {resolved}")
    if file_version != REQUIRED_CONFIG_VERSION:
        raise ConfigValidationError(
            f"Version mismatch in {resolved}: "
            f"expected {REQUIRED_CONFIG_VERSION}, got {file_version}"
        )


def validate_pricing(config: dict) -> None:
    """Validate that the pricing section has required structure.

    Args:
        config: Parsed setup.json dict.

    Raises:
        ConfigValidationError: If pricing is missing, invalid, or incomplete.
    """
    pricing = config.get("pricing")
    if pricing is None:
        raise ConfigValidationError("Missing 'pricing' section in config")
    unit = pricing.get("unit")
    if unit not in _VALID_PRICING_UNITS:
        raise ConfigValidationError(
            f"Invalid pricing unit {unit!r}; expected one of {sorted(_VALID_PRICING_UNITS)}"
        )
    for role in _PRICING_ROLES:
        role_cfg = pricing.get(role)
        if not role_cfg:
            raise ConfigValidationError(f"Missing pricing for role {role!r}")
        for key in ("input", "output"):
            val = role_cfg.get(key)
            if val is None or not isinstance(val, (int, float)):
                raise ConfigValidationError(f"Invalid pricing[{role!r}][{key!r}]: {val!r}")


def validate_agent_skills(config: dict) -> None:
    """Validate skill assignments match agent role semantics.

    Args:
        config: Parsed setup.json dict.

    Raises:
        ConfigValidationError: If an agent is assigned a skill that does not match its role.
    """
    agents = config.get("agents", {})
    judge_skills = set(agents.get("judge", {}).get("skills", []))
    invalid_judge = judge_skills & _DEBATER_SKILLS
    if invalid_judge:
        raise ConfigValidationError(
            f"Judge cannot use debater skills: {sorted(invalid_judge)}"
        )
    for role in ("pro", "con"):
        skills = set(agents.get(role, {}).get("skills", []))
        invalid = skills & _JUDGE_SKILLS
        if invalid:
            raise ConfigValidationError(
                f"'{role}' agent cannot use judge skills: {sorted(invalid)}"
            )


def validate_all_configs(
    setup_path: str | Path | None = None,
    rate_limits_path: str | Path | None = None,
    logging_path: str | Path | None = None,
) -> None:
    """Validate all config files at startup.

    Args:
        setup_path: Path to main setup config; defaults to DEFAULT_SETUP_PATH.
        rate_limits_path: Path to rate limits config; defaults to DEFAULT_RATE_LIMITS_PATH.
        logging_path: Path to logging config; defaults to DEFAULT_LOGGING_PATH.

    Raises:
        ConfigValidationError: On any version mismatch, missing file, or invalid config.
    """
    setup = resolve_project_path(setup_path) if setup_path else DEFAULT_SETUP_PATH
    rate = resolve_project_path(rate_limits_path) if rate_limits_path else DEFAULT_RATE_LIMITS_PATH
    log = resolve_project_path(logging_path) if logging_path else DEFAULT_LOGGING_PATH

    validate_config_version(setup, "version")
    validate_config_version(log, "version")

    rate_data = _load_json(rate)
    nested_version = rate_data.get("rate_limits", {}).get("version")
    if nested_version != REQUIRED_CONFIG_VERSION:
        raise ConfigValidationError(
            f"Version mismatch in {rate}: "
            f"expected {REQUIRED_CONFIG_VERSION}, got {nested_version}"
        )

    setup_data = _load_json(setup)
    validate_agent_skills(setup_data)
    validate_pricing(setup_data)
