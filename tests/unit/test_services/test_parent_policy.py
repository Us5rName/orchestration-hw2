"""Tests proving parent-controlled debate policy.

The orchestrator (parent) is the sole routing, control, and validation
boundary.  Pro and Con agents must never communicate directly.
"""

import inspect

from debate.agents.con_agent import ConAgent
from debate.agents.pro_agent import ProAgent
from debate.services.orchestrator import DebateOrchestrator
from tests.fakes.agents import ScriptedAgent

PRO_CONTENT = "Pro argues the topic strongly."
CON_CONTENT = "Con challenges the claim."
PRO_RESPONSE = {"content": PRO_CONTENT, "references": []}
CON_RESPONSE = {"content": CON_CONTENT, "references": []}
JUDGE_RESPONSE = {
    "winner": "pro",
    "pro_score": 80,
    "con_score": 70,
    "justification": "Pro was more persuasive.",
}


class RecordingAgent(ScriptedAgent):
    """ScriptedAgent that records every prompt it receives."""

    def __init__(self, role_name: str, responses: list[dict]) -> None:
        super().__init__(role_name, responses)
        self.received_prompts: list[str] = []

    def think(self, user_prompt: str) -> dict:
        self.received_prompts.append(user_prompt)
        return super().think(user_prompt)


class TestChildAgentIsolation:
    """Child agents have no knowledge of each other."""

    def test_pro_agent_does_not_import_con_agent(self) -> None:
        import debate.agents.pro_agent as pro_module
        assert not hasattr(pro_module, "ConAgent")

    def test_con_agent_does_not_import_pro_agent(self) -> None:
        import debate.agents.con_agent as con_module
        assert not hasattr(con_module, "ProAgent")

    def test_pro_constructor_has_no_con_param(self) -> None:
        sig = inspect.signature(ProAgent.__init__)
        assert "con" not in sig.parameters and "con_agent" not in sig.parameters

    def test_con_constructor_has_no_pro_param(self) -> None:
        sig = inspect.signature(ConAgent.__init__)
        assert "pro" not in sig.parameters and "pro_agent" not in sig.parameters

    def test_child_instances_have_no_cross_references(self) -> None:
        pro = ScriptedAgent("pro", [PRO_RESPONSE] * 5)
        con = ScriptedAgent("con", [CON_RESPONSE] * 5)
        judge = ScriptedAgent("judge", [JUDGE_RESPONSE] * 5)
        DebateOrchestrator(
            judge_agent=judge, pro_agent=pro, con_agent=con,
            topic="Test", max_rounds=1,
        ).run()
        pro_id, con_id = id(pro), id(con)
        for val in vars(pro).values():
            assert id(val) != con_id
        for val in vars(con).values():
            assert id(val) != pro_id


class TestOrchestratorRouting:
    """Orchestrator builds and mediates all prompts between agents."""

    def test_con_receives_orchestrator_built_prompt_with_pro_content(self) -> None:
        con = RecordingAgent("con", [CON_RESPONSE] * 5)
        orc = DebateOrchestrator(
            judge_agent=ScriptedAgent("judge", [JUDGE_RESPONSE] * 5),
            pro_agent=ScriptedAgent("pro", [PRO_RESPONSE] * 5),
            con_agent=con,
            topic="Test topic",
            max_rounds=1,
        )
        orc.run()
        assert con.received_prompts and PRO_CONTENT in con.received_prompts[0]

    def test_judge_receives_full_debate_summary(self) -> None:
        judge = RecordingAgent("judge", [JUDGE_RESPONSE] * 5)
        orc = DebateOrchestrator(
            judge_agent=judge,
            pro_agent=ScriptedAgent("pro", [PRO_RESPONSE] * 5),
            con_agent=ScriptedAgent("con", [CON_RESPONSE] * 5),
            topic="Test topic",
            max_rounds=1,
        )
        orc.run()
        jp = judge.received_prompts[0]
        assert PRO_CONTENT in jp and CON_CONTENT in jp


class TestTurnOrder:
    """Debate turn order is deterministic: pro before con each round, judge last."""

    def test_per_round_pro_precedes_con_in_history(self) -> None:
        orc = DebateOrchestrator(
            judge_agent=ScriptedAgent("judge", [JUDGE_RESPONSE] * 5),
            pro_agent=ScriptedAgent("pro", [PRO_RESPONSE] * 5),
            con_agent=ScriptedAgent("con", [CON_RESPONSE] * 5),
            topic="Test", max_rounds=3,
        )
        orc.run()
        for rnd in range(1, 4):
            entries = [e for e in orc.state.history if e["round"] == rnd]
            assert len(entries) == 2
            assert entries[0]["agent"] == "pro"
            assert entries[1]["agent"] == "con"

    def test_judge_called_once_after_all_rounds(self) -> None:
        judge = ScriptedAgent("judge", [JUDGE_RESPONSE] * 5)
        pro = ScriptedAgent("pro", [PRO_RESPONSE] * 5)
        con = ScriptedAgent("con", [CON_RESPONSE] * 5)
        DebateOrchestrator(
            judge_agent=judge, pro_agent=pro, con_agent=con,
            topic="Test", max_rounds=2,
        ).run()
        assert judge._idx == 1
        assert pro._idx == 2
        assert con._idx == 2

    def test_history_alternates_pro_con(self) -> None:
        orc = DebateOrchestrator(
            judge_agent=ScriptedAgent("judge", [JUDGE_RESPONSE] * 5),
            pro_agent=ScriptedAgent("pro", [PRO_RESPONSE] * 5),
            con_agent=ScriptedAgent("con", [CON_RESPONSE] * 5),
            topic="Test", max_rounds=3,
        )
        orc.run()
        agents = [e["agent"] for e in orc.state.history]
        assert agents == ["pro", "con"] * 3
