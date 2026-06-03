"""DebateOrchestrator — manages debate flow and rounds.

Input: judge_agent, pro_agent, con_agent, topic, max_rounds, watchdog, logger
Output: run() -> final verdict with winner and scores
Setup: creates DebateState, coordinates agents through rounds
"""

from ..agents.base_agent import AgentBase
from ..shared.gatekeeper import ApiGatekeeper
from ..shared.protocols import LoggerProtocol
from ..shared.watchdog import Watchdog
from .cost_calculator import summarize_debate, summarize_round
from .debate_state import DebateState
from .orchestrator_logging import (
    log_agent_response,
    log_debate_complete,
    log_debate_cost,
    log_debate_start,
    log_round_cost,
    log_round_start,
    log_verdict,
)
from .orchestrator_turns import build_usage_record, run_con_turn, run_pro_turn
from .usage_record import UsageRecord
from .verdict import decide_winner, format_result, record_verdict


class DebateOrchestrator:
    """
    Input: judge_agent, pro_agent, con_agent, topic, max_rounds, watchdog, logger
    Output: run() -> dict with winner, scores, justification
    Setup: creates DebateState, enforces judge-mediated flow
    """

    def __init__(
        self,
        judge_agent: AgentBase,
        pro_agent: AgentBase,
        con_agent: AgentBase,
        topic: str,
        max_rounds: int,
        watchdog: Watchdog | None = None,
        logger: LoggerProtocol | None = None,
        pricing: dict | None = None,
        gatekeeper: ApiGatekeeper | None = None,
    ) -> None:
        """Initialize orchestrator with agents and debate config.

        Raises:
            ValueError: If max_rounds is less than 1.
        """
        if max_rounds < 1:
            raise ValueError("max_rounds must be at least 1")

        self.judge = judge_agent
        self.pro = pro_agent
        self.con = con_agent
        self.watchdog = watchdog
        self.gatekeeper = gatekeeper
        self.logger = logger
        self.state = DebateState(topic=topic, max_rounds=max_rounds)
        self._pricing: dict = pricing or {}
        self._usage_records: list[UsageRecord] = []

    def run_round(self, round_number: int | None = None) -> dict:
        """Execute a single debate round: pro argues, then con counters.

        Args:
            round_number: Optional round override. Uses state if not provided.

        Returns:
            Dict with round results including both arguments.
        """
        if round_number is not None:
            self.state.current_round = round_number
        else:
            self.state.current_round += 1

        log_round_start(self.logger, self.state.current_round, self.state.max_rounds)

        pro_snap = self.pro.provider.get_usage()
        pro_response = self._run_pro_turn()
        log_agent_response(self.logger, "PRO", pro_response)
        pro_rec = self._build_usage_record("pro", pro_snap)

        con_snap = self.con.provider.get_usage()
        con_response = self._run_con_turn(pro_response)
        log_agent_response(self.logger, "CON", con_response)
        con_rec = self._build_usage_record("con", con_snap)

        round_records = [pro_rec, con_rec]
        self._usage_records.extend(round_records)
        round_summary = summarize_round(round_records, self._pricing)
        log_round_cost(self.logger, round_summary)

        return {
            "round": self.state.current_round,
            "pro": pro_response,
            "con": con_response,
            "round_cost": round_summary,
        }

    def run(self) -> dict:
        """Run the full debate and return the judge's verdict.

        Returns:
            Dict with winner, scores, justification, and full history.
        """
        log_debate_start(self.logger, self.state.topic, self.state.max_rounds)

        for _ in range(self.state.max_rounds):
            if self.watchdog:
                self.watchdog.ping()
            self.run_round()

        judge_snap = self.judge.provider.get_usage()
        if self.gatekeeper:
            verdict = self.gatekeeper.execute(decide_winner, self.judge, self.state)
        else:
            verdict = decide_winner(self.judge, self.state)
        judge_rec = self._build_usage_record("judge", judge_snap, round_number=0)
        self._usage_records.append(judge_rec)

        log_verdict(self.logger, verdict)
        record_verdict(self.state, verdict)
        result = format_result(verdict, self.state.history)

        debate_summary = summarize_debate(self._usage_records, self._pricing)
        log_debate_cost(self.logger, debate_summary)
        result["cost_summary"] = debate_summary
        log_debate_complete(self.logger, result["winner"], result["pro_score"], result["con_score"])
        return result

    def _build_usage_record(
        self, role: str, snapshot_before: dict, round_number: int | None = None
    ) -> UsageRecord:
        """Delegate to build_usage_record with the current agents map."""
        agents_map = {"judge": self.judge, "pro": self.pro, "con": self.con}
        return build_usage_record(agents_map, self.state, role, snapshot_before, round_number)

    def _run_pro_turn(self) -> dict:
        """Delegate to run_pro_turn with current orchestrator state."""
        return run_pro_turn(self.state, self.pro, self.gatekeeper)

    def _run_con_turn(self, pro_response: dict) -> dict:
        """Delegate to run_con_turn with current orchestrator state."""
        return run_con_turn(self.state, self.con, pro_response, self.gatekeeper)
