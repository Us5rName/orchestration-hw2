"""Verdict — judge evaluation and result formatting.

Input: judge_agent, debate_state, verdict dict
Output: formatted result with winner, scores, history
Setup: no configuration needed
"""

from ..agents.base_agent import AgentBase
from .debate_state import DebateState
from .prompt_builder import build_verdict_prompt


def decide_winner(judge: AgentBase, state: DebateState) -> dict:
    """Ask judge to evaluate the debate and declare a winner.

    Args:
        judge: Judge agent.
        state: Current debate state.

    Returns:
        Dict with winner, scores, and justification.
    """
    verdict_prompt = build_verdict_prompt(state)
    return judge.think(verdict_prompt)


def record_verdict(state: DebateState, verdict: dict) -> None:
    """Record the judge's verdict in the debate state.

    Args:
        state: Current debate state.
        verdict: Judge's verdict dict with winner and scores.
    """
    state.set_verdict(
        winner=verdict.get("winner", ""),
        pro_score=verdict.get("pro_score", 0),
        con_score=verdict.get("con_score", 0),
    )


def format_result(verdict: dict, history: list[dict]) -> dict:
    """Format the final result with verdict and history.

    Args:
        verdict: Judge's verdict dict.
        history: Full debate history.

    Returns:
        Complete result dict.
    """
    return {
        "winner": verdict.get("winner"),
        "pro_score": verdict.get("pro_score"),
        "con_score": verdict.get("con_score"),
        "justification": verdict.get("justification", ""),
        "history": history,
    }
