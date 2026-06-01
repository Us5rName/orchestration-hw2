"""DebateOrchestrator — manages debate flow and rounds.

Input: judge_agent, pro_agent, con_agent, topic, max_rounds, watchdog
Output: run() -> final verdict with winner and scores
Setup: creates DebateState, coordinates agents through rounds
"""

from ..agents.base_agent import AgentBase
from .debate_state import DebateState
from .prompt_builder import build_con_prompt, build_pro_prompt
from .verdict import decide_winner, format_result, record_verdict


class DebateOrchestrator:
    """
    Input: judge_agent, pro_agent, con_agent, topic, max_rounds, watchdog
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
        watchdog: object | None = None,
    ) -> None:
        """Initialize orchestrator with agents and debate config.

        Args:
            judge_agent: Judge agent that mediates and scores.
            pro_agent: Pro-side debater.
            con_agent: Con-side debater.
            topic: The debate topic.
            max_rounds: Maximum number of debate rounds.
            watchdog: Optional process monitor.

        Raises:
            ValueError: If max_rounds is less than 1.
        """
        if max_rounds < 1:
            raise ValueError("max_rounds must be at least 1")

        self.judge = judge_agent
        self.pro = pro_agent
        self.con = con_agent
        self.watchdog = watchdog
        self.state = DebateState(topic=topic, max_rounds=max_rounds)

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

        pro_response = self._run_pro_turn()
        con_response = self._run_con_turn(pro_response)

        return {
            "round": self.state.current_round,
            "pro": pro_response,
            "con": con_response,
        }

    def run(self) -> dict:
        """Run the full debate and return the judge's verdict.

        Returns:
            Dict with winner, scores, justification, and full history.
        """
        for _ in range(self.state.max_rounds):
            self.run_round()

        verdict = decide_winner(self.judge, self.state)
        record_verdict(self.state, verdict)
        return format_result(verdict, self.state.history)

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
