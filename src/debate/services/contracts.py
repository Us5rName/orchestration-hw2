"""Structured output contracts for agent and judge responses.

Input: raw dicts from agent.think() or judge.think()
Output: validated AgentResponse or JudgeDecision dataclasses
Setup: no configuration needed; raises ValueError on invalid input
"""

from dataclasses import dataclass, field

_VALID_WINNERS = ("pro", "con")


@dataclass
class AgentResponse:
    """Validated agent output.

    Raises ValueError on construction if any field is invalid.
    """

    content: str
    role: str = ""
    references: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.content, str) or not self.content.strip():
            raise ValueError("AgentResponse.content must be a non-empty string")
        if _has_control_chars(self.content):
            raise ValueError(
                "AgentResponse.content contains invalid control characters"
            )
        if not isinstance(self.references, list):
            raise ValueError("AgentResponse.references must be a list")
        if not isinstance(self.metadata, dict):
            raise ValueError("AgentResponse.metadata must be a dict")


@dataclass
class JudgeDecision:
    """Validated judge verdict.

    Raises ValueError on construction if any field is invalid.
    """

    winner: str
    pro_score: float
    con_score: float
    reasoning_summary: str
    rule_violations: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.winner not in _VALID_WINNERS:
            raise ValueError(
                f"JudgeDecision.winner must be 'pro' or 'con', got {self.winner!r}"
            )
        if not isinstance(self.pro_score, (int, float)):
            raise ValueError("JudgeDecision.pro_score must be numeric")
        if not isinstance(self.con_score, (int, float)):
            raise ValueError("JudgeDecision.con_score must be numeric")
        if self.pro_score == self.con_score:
            raise ValueError(
                "JudgeDecision: pro_score and con_score must not be equal (no ties)"
            )
        if not isinstance(self.reasoning_summary, str) or not self.reasoning_summary.strip():
            raise ValueError("JudgeDecision.reasoning_summary must be a non-empty string")
        if not isinstance(self.rule_violations, list):
            raise ValueError("JudgeDecision.rule_violations must be a list")


def agent_response_from_dict(d: dict) -> AgentResponse:
    """Parse and validate a raw agent response dict.

    Raises:
        ValueError: if content is missing, empty, or contains control characters.
    """
    return AgentResponse(
        content=d.get("content", ""),
        role=str(d.get("role", d.get("agent", ""))),
        references=list(d.get("references", [])),
        metadata={
            k: v for k, v in d.items()
            if k not in ("content", "role", "agent", "references")
        },
    )


def judge_decision_from_dict(d: dict) -> JudgeDecision:
    """Parse and validate a raw judge verdict dict.

    Accepts 'justification', 'reasoning_summary', or 'explanation' as the
    reasoning field name for compatibility with existing LLM outputs.

    Raises:
        ValueError: if winner is invalid, scores are tied, or reasoning is missing.
    """
    reasoning = (
        d.get("reasoning_summary")
        or d.get("justification")
        or d.get("explanation", "")
    )
    return JudgeDecision(
        winner=str(d.get("winner", "")),
        pro_score=d.get("pro_score", 0),
        con_score=d.get("con_score", 0),
        reasoning_summary=str(reasoning) if reasoning else "",
        rule_violations=list(d.get("rule_violations", [])),
    )


def validate_agent_dict(d: dict) -> None:
    """Validate a raw agent response dict in-place (without building the dataclass).

    Raises:
        ValueError: if content is invalid.
    """
    agent_response_from_dict(d)


def validate_judge_dict(d: dict) -> None:
    """Validate a raw judge verdict dict in-place (without building the dataclass).

    Raises:
        ValueError: if the verdict is structurally invalid.
    """
    judge_decision_from_dict(d)


def _has_control_chars(s: str) -> bool:
    """Return True if s contains ASCII control characters (except tab/LF/CR)."""
    return any(ord(c) < 32 and ord(c) not in (9, 10, 13) for c in s)
