"""DebateOrchestrator — manages debate flow and rounds.

Input: judge_agent, pro_agent, con_agent, topic, max_rounds, watchdog, logger
Output: run() -> final verdict with winner and scores
Setup: creates DebateState, coordinates agents through rounds
"""

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
from .prompt_builder import build_con_prompt, build_pro_prompt
from .usage_record import UsageRecord, build_from_delta
from .verdict import decide_winner, format_result, record_verdict
from ..agents.base_agent import AgentBase
from ..shared.protocols import LoggerProtocol
from ..shared.watchdog import Watchdog


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
            self.run_round()

        judge_snap = self.judge.provider.get_usage()
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
        """Build a UsageRecord from provider delta since a pre-call snapshot.

        Args:
            role: Agent role string ('judge', 'pro', 'con').
            snapshot_before: get_usage() snapshot taken before the agent call.
            round_number: Override round; defaults to current state round.

        Returns:
            UsageRecord with delta tokens; available=False when delta is zero.
        """
        agent = {"judge": self.judge, "pro": self.pro, "con": self.con}[role]
        rn = round_number if round_number is not None else self.state.current_round
        return build_from_delta(
            str(agent.provider.provider_name),
            str(agent.provider.model),
            role,
            snapshot_before,
            agent.provider.get_usage(),
            rn,
        )

    def _run_pro_turn(self) -> dict:
        """Execute pro agent's turn and record the argument.

        Returns:
            Pro agent's response dict.
        """
        pro_prompt = build_pro_prompt(self.state)
        pro_response = self.pro.think(pro_prompt)
        self.state.record_argument(
            agent="pro",
            content=pro_response.get("content", ""),
            references=pro_response.get("references", []),
        )
        return pro_response

    def _run_con_turn(self, pro_response: dict) -> dict:
        """Execute con agent's turn and record the counter-argument.

        Args:
            pro_response: Pro agent's response dict.

        Returns:
            Con agent's response dict.
        """
        con_prompt = build_con_prompt(self.state, pro_response)
        con_response = self.con.think(con_prompt)
        self.state.record_argument(
            agent="con",
            content=con_response.get("content", ""),
            references=con_response.get("references", []),
        )
        return con_response
