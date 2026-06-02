"""Typed config dataclasses for all sections of setup.json.

Each dataclass has a from_dict() classmethod that reads from a raw dict
with sensible defaults matching config/setup.json.
"""

from dataclasses import dataclass, field


@dataclass
class DebateConfig:
    """Top-level debate section."""

    topic: str = ""
    max_rounds: int = 3
    max_tokens_per_agent: int = 50000
    request_timeout_seconds: float = 600.0

    @classmethod
    def from_dict(cls, data: dict) -> "DebateConfig":
        return cls(
            topic=data.get("topic", ""),
            max_rounds=data.get("max_rounds", 3),
            max_tokens_per_agent=data.get("max_tokens_per_agent", 50000),
            request_timeout_seconds=float(data.get("request_timeout_seconds", 600.0)),
        )


@dataclass
class AgentConfig:
    """Per-agent section (judge / pro / con)."""

    provider: str = "openai"
    model: str = ""
    temperature: float = 0.7
    timeout: float = 60.0
    skills: list[str] = field(default_factory=list)
    base_url: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "AgentConfig":
        return cls(
            provider=data.get("provider", "openai"),
            model=data.get("model", ""),
            temperature=float(data.get("temperature", 0.7)),
            timeout=float(data.get("timeout", 60.0)),
            skills=list(data.get("skills", [])),
            base_url=data.get("base_url"),
        )


@dataclass
class LoggingConfig:
    """Logging section."""

    log_directory: str = "logs"
    max_files: int = 20
    max_lines_per_file: int = 500
    level: str = "INFO"
    format: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    @classmethod
    def from_dict(cls, data: dict) -> "LoggingConfig":
        return cls(
            log_directory=data.get("log_directory", "logs"),
            max_files=data.get("max_files", 20),
            max_lines_per_file=data.get("max_lines_per_file", 500),
            level=data.get("level", "INFO"),
            format=data.get("format", "%(asctime)s [%(levelname)s] %(name)s: %(message)s"),
        )

    def to_dict(self) -> dict:
        """Return a dict compatible with LogManager.__init__."""
        return {
            "log_directory": self.log_directory,
            "max_files": self.max_files,
            "max_lines_per_file": self.max_lines_per_file,
            "level": self.level,
            "format": self.format,
        }


@dataclass
class PricingRoleConfig:
    """Input/output price for a single role."""

    input: float = 0.0
    output: float = 0.0

    @classmethod
    def from_dict(cls, data: dict) -> "PricingRoleConfig":
        return cls(
            input=float(data.get("input", 0.0)),
            output=float(data.get("output", 0.0)),
        )


@dataclass
class PricingConfig:
    """Pricing section."""

    unit: str = "per_1m_tokens"
    judge: PricingRoleConfig = field(default_factory=PricingRoleConfig)
    pro: PricingRoleConfig = field(default_factory=PricingRoleConfig)
    con: PricingRoleConfig = field(default_factory=PricingRoleConfig)

    @classmethod
    def from_dict(cls, data: dict) -> "PricingConfig":
        return cls(
            unit=data.get("unit", "per_1m_tokens"),
            judge=PricingRoleConfig.from_dict(data.get("judge", {})),
            pro=PricingRoleConfig.from_dict(data.get("pro", {})),
            con=PricingRoleConfig.from_dict(data.get("con", {})),
        )
