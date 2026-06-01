"""PromptBuilder — constructs debate prompts for agents.

Input: debate_state (DebateState), agent responses
Output: formatted prompt strings for pro, con, and judge
Setup: no configuration needed
"""

from .debate_state import DebateState


def build_pro_prompt(state: DebateState) -> str:
    """Build prompt for pro agent's argument.

    Args:
        state: Current debate state.

    Returns:
        Prompt string with context from previous round.
    """
    context = get_last_argument(state, "con")
    if context:
        return (
            f"TOPIC: {state.topic}\n"
            f"Round {state.current_round}. "
            f"Counter the following CON argument:\n{context}\n\n"
            "Present your PRO argument in JSON format."
        )
    return (
        f"TOPIC: {state.topic}\n"
        f"Round {state.current_round}. "
        "Present your opening PRO argument in JSON format."
    )


def build_con_prompt(state: DebateState, pro_response: dict) -> str:
    """Build prompt for con agent's counter-argument.

    Args:
        state: Current debate state.
        pro_response: Pro agent's response dict.

    Returns:
        Prompt string with pro's argument to counter.
    """
    pro_content = pro_response.get("content", "")
    return (
        f"TOPIC: {state.topic}\n"
        f"Round {state.current_round}. "
        f"Counter the following PRO argument:\n{pro_content}\n\n"
        "Present your CON counter-argument in JSON format."
    )


def build_verdict_prompt(state: DebateState) -> str:
    """Build prompt for judge's final verdict.

    Args:
        state: Current debate state.

    Returns:
        Prompt string with full debate summary.
    """
    summary = build_debate_summary(state)
    return (
        "Evaluate the following debate and declare a winner. "
        "Score persuasiveness, not factual correctness. "
        "No ties allowed. Respond in JSON format.\n\n"
        f"{summary}"
    )


def get_last_argument(state: DebateState, agent: str) -> str:
    """Retrieve the last argument from a specific agent.

    Args:
        state: Current debate state.
        agent: Agent role ('pro' or 'con').

    Returns:
        Last argument content, or empty string if none.
    """
    for entry in reversed(state.history):
        if entry["agent"] == agent:
            return entry["content"]
    return ""


def build_debate_summary(state: DebateState) -> str:
    """Build a summary of all arguments for the judge.

    Args:
        state: Current debate state.

    Returns:
        Formatted string with all round arguments.
    """
    lines = [f"TOPIC: {state.topic}\n"]
    for entry in state.history:
        lines.append(f"[Round {entry['round']}] {entry['agent'].upper()}: {entry['content']}")
    return "\n\n".join(lines)
