"""DebateSDK — single entry point for all debate operations.

Input: config_path (str) — path to setup.json
Output: run_debate() -> verdict dict, get_logs() -> log lines
Setup: wires ConfigManager, LogManager, providers, agents, orchestrator
"""

from pathlib import Path

from ..agents.con_agent import ConAgent
from ..agents.judge_agent import JudgeAgent
from ..agents.pro_agent import ProAgent
from ..services.orchestrator import DebateOrchestrator
from ..shared.config import ConfigManager
from ..shared.gatekeeper import ApiGatekeeper, RateLimitConfig
from ..shared.logger import LogManager
from ..shared.watchdog import Watchdog
from ..skills.registry import SkillRegistry, default_registry
from .agent_factory import create_agent
from .provider_factory import create_provider


class DebateSDK:
    """
    Input: config_path (str) — path to setup.json
    Output: run_debate() -> verdict dict, get_logs() -> list[str]
    Setup: loads config, creates providers, agents, orchestrator
    """

    def __init__(self, config_path: str = "config/setup.json") -> None:
        """Initialize SDK with configuration.

        Args:
            config_path: Path to the JSON config file.
        """
        self.config = ConfigManager(config_path)
        self._skill_registry: SkillRegistry = default_registry()
        self._init_logger()
        self._init_gatekeeper()
        self._init_watchdog()

    def _init_logger(self) -> None:
        """Initialize LogManager from config."""
        log_config = self.config.get("logging", {})
        self.logger = LogManager(log_config)
        self.logger.info("DebateSDK initialized")

    def _init_gatekeeper(self) -> None:
        """Initialize ApiGatekeeper from config."""
        gate_config = self.config.get("gatekeeper", {})
        self.gatekeeper = ApiGatekeeper(
            config=RateLimitConfig(
                requests_per_minute=gate_config.get("requests_per_minute", 30),
                requests_per_hour=gate_config.get("requests_per_hour", 500),
                max_retries=gate_config.get("max_retries", 3),
                retry_after_seconds=gate_config.get("retry_delay_seconds", 5),
            )
        )

    def _init_watchdog(self) -> None:
        """Initialize Watchdog for process monitoring."""
        self.watchdog = Watchdog(check_interval=1.0, timeout=30.0)

    def _create_agent(self, role: str) -> JudgeAgent | ProAgent | ConAgent:
        """Create an agent with resolved skills from config.

        Args:
            role: Agent role ('judge', 'pro', 'con').

        Returns:
            Configured agent instance with skills attached.
        """
        agent_cfg = self.config.get("agents", {}).get(role, {})
        timeout = self.config.get("debate", {}).get("request_timeout_seconds", 60)
        provider_cfg = {**agent_cfg, "timeout": timeout}
        provider = create_provider(agent_cfg.get("provider", "openai"), provider_cfg)
        topic = self.config.get("debate", {}).get("topic", "")
        return create_agent(role, agent_cfg, provider, topic, timeout, self._skill_registry)

    def _create_orchestrator(self) -> DebateOrchestrator:
        """Create orchestrator with all agents.

        Returns:
            Configured DebateOrchestrator instance.
        """
        debate_cfg = self.config.get("debate", {})
        return DebateOrchestrator(
            judge_agent=self._create_agent("judge"),
            pro_agent=self._create_agent("pro"),
            con_agent=self._create_agent("con"),
            topic=debate_cfg.get("topic", ""),
            max_rounds=debate_cfg.get("max_rounds", 10),
            watchdog=self.watchdog,
            logger=self.logger,
        )

    def run_debate(self) -> dict:
        """Run a full debate and return the verdict.

        Returns:
            Dict with winner, scores, justification, history.
        """
        orchestrator = self._create_orchestrator()
        self.logger.info("Debate started")
        result = orchestrator.run()
        self.logger.info(f"Debate complete. Winner: {result.get('winner')}")
        return result

    def get_logs(self, count: int = 50) -> list[str]:
        """Read recent log lines from the latest log file.

        Args:
            count: Number of recent lines to return.

        Returns:
            List of log lines.
        """
        log_dir = Path(self.config.get("logging", {}).get("log_directory", "logs"))
        log_file = log_dir / "debate.log"
        if not log_file.exists():
            return ["No log file found."]
        lines = log_file.read_text(encoding="utf-8").strip().splitlines()
        return lines[-count:]
