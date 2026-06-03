"""Turn execution and usage helpers for DebateOrchestrator.

These standalone functions encapsulate the per-turn agent invocation logic
so the orchestrator class stays focused on debate flow coordination.
"""

from ..agents.base_agent import AgentBase
from ..shared.gatekeeper import ApiGatekeeper
from .contracts import validate_agent_dict
from .debate_state import DebateState
from .prompt_builder import build_con_prompt, build_pro_prompt
from .usage_record import UsageRecord, build_from_delta


def run_pro_turn(
    state: DebateState,
    pro_agent: AgentBase,
    gatekeeper: ApiGatekeeper | None = None,
) -> dict:
    """Execute pro agent's turn and record the argument in state."""
    pro_prompt = build_pro_prompt(state)
    if gatekeeper:
        pro_response = gatekeeper.execute(pro_agent.think, pro_prompt)
    else:
        pro_response = pro_agent.think(pro_prompt)
    validate_agent_dict(pro_response)
    state.record_argument(
        agent="pro",
        content=pro_response.get("content", ""),
        references=pro_response.get("references", []),
    )
    return pro_response


def run_con_turn(
    state: DebateState,
    con_agent: AgentBase,
    pro_response: dict,
    gatekeeper: ApiGatekeeper | None = None,
) -> dict:
    """Execute con agent's turn and record the counter-argument in state."""
    con_prompt = build_con_prompt(state, pro_response)
    if gatekeeper:
        con_response = gatekeeper.execute(con_agent.think, con_prompt)
    else:
        con_response = con_agent.think(con_prompt)
    validate_agent_dict(con_response)
    state.record_argument(
        agent="con",
        content=con_response.get("content", ""),
        references=con_response.get("references", []),
    )
    return con_response


def build_usage_record(
    agents_map: dict,
    state: DebateState,
    role: str,
    snapshot_before: dict,
    round_number: int | None = None,
) -> UsageRecord:
    """Build a UsageRecord from provider token delta since a pre-call snapshot."""
    agent = agents_map[role]
    rn = round_number if round_number is not None else state.current_round
    return build_from_delta(
        str(agent.provider.provider_name),
        str(agent.provider.model),
        role,
        snapshot_before,
        agent.provider.get_usage(),
        rn,
    )
