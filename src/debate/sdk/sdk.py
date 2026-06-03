"""DebateSDK — single entry point for all debate operations.

Input: config_path (str | Path | None) — path to setup.json; None uses DEFAULT_SETUP_PATH
Output: run_debate() -> verdict dict, get_logs() -> log lines
Setup: wires ConfigManager, LogManager, providers, agents, orchestrator
"""

from pathlib import Path

from .agent_factory import create_agent
from .provider_factory import create_provider
from ..agents.con_agent import ConAgent
from ..agents.judge_agent import JudgeAgent
from ..agents.pro_agent import ProAgent
from ..services.orchestrator import DebateOrchestrator
from ..shared.config import ConfigManager
from ..shared.gatekeeper import ApiGatekeeper
from ..shared.logger import LogManager
from ..shared.watchdog import Watchdog
from ..skills.registry import SkillRegistry, default_registry


class DebateSDK:
    """
    Input: config_path (str | Path | None) — path to setup.json; None = project default
    Output: run_debate() -> verdict dict, get_logs() -> list[str]
    Setup: loads config, creates providers, agents, orchestrator
    """

    def __init__(self, config_path: str | Path | None = None) -> None:
        """Initialize SDK with configuration.

        Args:
            config_path: Path to the JSON config file.  None uses DEFAULT_SETUP_PATH.
                         Relative paths are resolved relative to the project root.
        """
        self.config = ConfigManager(config_path)
        self._skill_registry: SkillRegistry = default_registry()
        self._init_logger()
        self._init_gatekeeper()
        self._init_watchdog()

    def _init_logger(self) -> None:
        """Initialize LogManager from config."""
        self.logger = LogManager(self.config.logging_config.to_dict())
        self.logger.info("DebateSDK initialized")

    def _init_gatekeeper(self) -> None:
        """Initialize ApiGatekeeper from config."""
        self.gatekeeper = ApiGatekeeper(config=self.config.gatekeeper_config)

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
        agent_cfg = self.config.agent_config(role)
        debate_cfg = self.config.debate_config
        provider_dict = {
            "provider": agent_cfg.provider,
            "model": agent_cfg.model,
            "temperature": agent_cfg.temperature,
            "base_url": agent_cfg.base_url,
            "timeout": agent_cfg.timeout,
        }
        provider = create_provider(agent_cfg.provider, provider_dict)
        agent_dict = {
            "model": agent_cfg.model,
            "temperature": agent_cfg.temperature,
            "skills": agent_cfg.skills,
        }
        return create_agent(
            role, agent_dict, provider, debate_cfg.topic,
            agent_cfg.timeout, self._skill_registry, self.logger,
        )

    def _create_orchestrator(self) -> DebateOrchestrator:
        """Create orchestrator with all agents.

        Returns:
            Configured DebateOrchestrator instance.
        """
        debate_cfg = self.config.debate_config
        pricing_cfg = self.config.pricing_config
        pricing_dict = {
            "unit": pricing_cfg.unit,
            "judge": {"input": pricing_cfg.judge.input, "output": pricing_cfg.judge.output},
            "pro": {"input": pricing_cfg.pro.input, "output": pricing_cfg.pro.output},
            "con": {"input": pricing_cfg.con.input, "output": pricing_cfg.con.output},
        }
        self._orchestrator = DebateOrchestrator(
            judge_agent=self._create_agent("judge"),
            pro_agent=self._create_agent("pro"),
            con_agent=self._create_agent("con"),
            topic=debate_cfg.topic,
            max_rounds=debate_cfg.max_rounds,
            watchdog=self.watchdog,
            logger=self.logger,
            pricing=pricing_dict,
        )
        return self._orchestrator

    def get_token_usage(self) -> dict[str, dict[str, int]]:
        """Return token usage per agent role from the last debate.

        Returns:
            Dict mapping role -> {input_tokens, output_tokens}.
        """
        if not hasattr(self, "_orchestrator"):
            return {}
        orc = self._orchestrator
        return {
            "judge": orc.judge.provider.get_usage(),
            "pro": orc.pro.provider.get_usage(),
            "con": orc.con.provider.get_usage(),
        }

    def run_debate(self) -> dict:
        """Run a full debate and return the verdict.

        Returns:
            Dict with winner, scores, justification, history, token_usage.
        """
        orchestrator = self._create_orchestrator()
        self.logger.info("Debate started")
        result = orchestrator.run()
        usage = self.get_token_usage()
        result["token_usage"] = usage
        total_in = sum(v["input_tokens"] for v in usage.values())
        total_out = sum(v["output_tokens"] for v in usage.values())
        self.logger.info(f"Token usage — in: {total_in}, out: {total_out}")
        self.logger.info(f"Debate complete. Winner: {result.get('winner')}")
        return result

    def get_logs(self, count: int = 50) -> list[str]:
        """Read recent log lines from the current log file.

        Args:
            count: Number of recent lines to return.

        Returns:
            List of log lines.
        """
        log_file = self.logger.log_file
        if not log_file.exists():
            return ["No log file found."]
        lines = log_file.read_text(encoding="utf-8").strip().splitlines()
        return lines[-count:]
