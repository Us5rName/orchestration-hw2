"""Orchestrator logging — structured debate event logging.

Separates logging concern from orchestration logic. All debate events
(rounds, agent responses, verdicts) flow through these helpers so the
orchestrator stays focused on coordination.
"""


def log_debate_start(logger: object | None, topic: str, max_rounds: int) -> None:
    """Log the start of a debate."""
    _safe_log(logger, "Debate started: %s (%d rounds)", topic, max_rounds)


def log_round_start(logger: object | None, current: int, total: int) -> None:
    """Log the start of a debate round."""
    _safe_log(logger, "--- Round %d/%d ---", current, total)


def log_agent_response(logger: object | None, agent: str, response: dict) -> None:
    """Log an agent's full response with references."""
    content = response.get("content", "")
    _safe_log(logger, "%s response: %s", agent, content)
    refs = response.get("references", [])
    if refs:
        _safe_log(logger, "%s references: %s", agent, ", ".join(refs))


def log_verdict(logger: object | None, verdict: dict) -> None:
    """Log the judge's verdict with scores and full justification."""
    _safe_log(
        logger,
        "Judge verdict: winner=%s, pro_score=%.0f, con_score=%.0f",
        verdict.get("winner"),
        verdict.get("pro_score", 0),
        verdict.get("con_score", 0),
    )
    justification = verdict.get("justification", "")
    if justification:
        _safe_log(logger, "Judge justification: %s", justification)


def log_debate_complete(
    logger: object | None, winner: str, pro_score: float, con_score: float
) -> None:
    """Log the final result of the debate."""
    _safe_log(
        logger,
        "Debate complete. Winner: %s (Pro: %.0f, Con: %.0f)",
        winner,
        pro_score,
        con_score,
    )


def _safe_log(logger: object | None, message: str, *args: object) -> None:
    """Log a message only if a logger is configured."""
    if logger is not None:
        logger.info(message % args)
