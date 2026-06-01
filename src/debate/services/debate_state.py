"""DebateState — tracks debate progress, arguments, and scores.

Input: topic (str), max_rounds (int)
Output: current state (round, history, scores, winner)
Setup: initialized by DebateOrchestrator
"""

from dataclasses import dataclass, field


@dataclass
class DebateState:
    """
    Input: topic (str), max_rounds (int)
    Output: current state with round, history, scores, winner
    Setup: initialized with topic and max_rounds
    """

    topic: str
    max_rounds: int
    current_round: int = 0
    history: list[dict] = field(default_factory=list)
    pro_score: float = 0.0
    con_score: float = 0.0
    winner: str | None = None

    def record_argument(
        self, agent: str, content: str, references: list[str] | None = None
    ) -> None:
        """Record an agent's argument in the debate history.

        Args:
            agent: Agent role ('pro' or 'con').
            content: Argument content.
            references: Optional source references.
        """
        self.history.append(
            {
                "agent": agent,
                "round": self.current_round,
                "content": content,
                "references": references or [],
            }
        )

    def advance_round(self) -> None:
        """Increment the current round counter."""
        self.current_round += 1

    @property
    def is_complete(self) -> bool:
        """Check if the debate has reached the maximum rounds.

        Returns:
            True if all rounds have been completed.
        """
        return self.current_round >= self.max_rounds

    def set_verdict(self, winner: str, pro_score: float, con_score: float) -> None:
        """Record the final verdict with winner and scores.

        Args:
            winner: Winning side ('pro' or 'con').
            pro_score: Pro's persuasiveness score.
            con_score: Con's persuasiveness score.
        """
        self.winner = winner
        self.pro_score = pro_score
        self.con_score = con_score
