"""Config version and skill-role validation at startup."""

import json
import sys
from pathlib import Path

from .version import REQUIRED_CONFIG_VERSION

_JUDGE_SKILLS: frozenset[str] = frozenset({"persuasion-scoring"})
_DEBATER_SKILLS: frozenset[str] = frozenset({"research-analysis", "quality-standards"})
_VALID_PRICING_UNITS: frozenset[str] = frozenset({"per_1m_tokens", "per_1k_tokens"})
_PRICING_ROLES: frozenset[str] = frozenset({"judge", "pro", "con"})


def _load_json(path: str) -> dict:
    """Load a JSON file and return its contents."""
    file_path = Path(path)
    if not file_path.exists():
        print(f"ERROR: Config file not found: {path}")
        sys.exit(1)
    with open(file_path, encoding="utf-8") as f:
        return json.load(f)


def validate_config_version(path: str, version_key: str = "version") -> None:
    """Validate that a config file's version matches the required version.

    Args:
        path: Path to the JSON config file.
        version_key: The key that holds the version string.
            For rate_limits.json the version is nested under "rate_limits".

    Raises:
        SystemExit: If versions don't match or file is missing.
    """
    data = _load_json(path)
    file_version = data.get(version_key)

    if file_version is None:
        print(f"ERROR: No '{version_key}' key in {path}")
        sys.exit(1)

    if file_version != REQUIRED_CONFIG_VERSION:
        print(
            f"ERROR: Version mismatch in {path}: "
            f"expected {REQUIRED_CONFIG_VERSION}, got {file_version}"
        )
        sys.exit(1)


def validate_pricing(config: dict) -> None:
    """Validate that the pricing section has required structure.

    Args:
        config: Parsed setup.json dict.

    Raises:
        ValueError: If pricing is missing, has an unsupported unit, or any
            role is missing input/output prices or uses non-numeric values.
    """
    pricing = config.get("pricing")
    if pricing is None:
        raise ValueError("Missing 'pricing' section in config")
    unit = pricing.get("unit")
    if unit not in _VALID_PRICING_UNITS:
        raise ValueError(
            f"Invalid pricing unit {unit!r}; expected one of {sorted(_VALID_PRICING_UNITS)}"
        )
    for role in _PRICING_ROLES:
        role_cfg = pricing.get(role)
        if not role_cfg:
            raise ValueError(f"Missing pricing for role {role!r}")
        for key in ("input", "output"):
            val = role_cfg.get(key)
            if val is None or not isinstance(val, (int, float)):
                raise ValueError(f"Invalid pricing[{role!r}][{key!r}]: {val!r}")


def validate_agent_skills(config: dict) -> None:
    """Validate skill assignments match agent role semantics.

    Judge may only use judge skills. Pro and Con may only use debater skills.

    Args:
        config: Parsed setup.json dict.

    Raises:
        ValueError: If an agent is assigned a skill that does not match its role.
    """
    agents = config.get("agents", {})

    judge_skills = set(agents.get("judge", {}).get("skills", []))
    invalid_judge = judge_skills & _DEBATER_SKILLS
    if invalid_judge:
        raise ValueError(f"Judge cannot use debater skills: {sorted(invalid_judge)}")

    for role in ("pro", "con"):
        skills = set(agents.get(role, {}).get("skills", []))
        invalid = skills & _JUDGE_SKILLS
        if invalid:
            raise ValueError(f"'{role}' agent cannot use judge skills: {sorted(invalid)}")


def validate_all_configs(
    setup_path: str = "config/setup.json",
    rate_limits_path: str = "config/rate_limits.json",
    logging_path: str = "config/logging_config.json",
) -> None:
    """Validate all config files at startup.

    Args:
        setup_path: Path to main setup config.
        rate_limits_path: Path to rate limits config.
        logging_path: Path to logging config.
    """
    validate_config_version(setup_path, "version")
    validate_config_version(logging_path, "version")

    # Rate limits has nested version under "rate_limits" key
    rate_data = _load_json(rate_limits_path)
    nested_version = rate_data.get("rate_limits", {}).get("version")
    if nested_version != REQUIRED_CONFIG_VERSION:
        print(
            f"ERROR: Nested version mismatch in {rate_limits_path}: "
            f"expected {REQUIRED_CONFIG_VERSION}, got {nested_version}"
        )
        sys.exit(1)

    try:
        setup_data = _load_json(setup_path)
        validate_agent_skills(setup_data)
        validate_pricing(setup_data)
    except ValueError as exc:
        print(f"ERROR: Invalid configuration — {exc}")
        sys.exit(1)
