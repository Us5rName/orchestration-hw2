"""ScriptedAgent — a typed agent fake for the test harness.

Returns preset dicts from think() in sequence without making any LLM
call. Use this in orchestrator / debate-flow tests that verify routing
and state logic, not individual agent behaviour.
"""

from debate.agents.base_agent import AgentBase
from tests.fakes.providers import FakeProvider


class ScriptedAgent(AgentBase):
    """Agent that returns scripted think() dicts in sequence.

    Bypasses the provider entirely; suitable for tests that care about
    what the orchestrator does with agent responses, not how agents
    produce them.
    """

    def __init__(
        self,
        role_name: str = "fake",
        responses: list[dict] | None = None,
    ) -> None:
        super().__init__(
            provider=FakeProvider(),
            model="fake-model",
            temperature=0.7,
            timeout=30.0,
        )
        self._role_name = role_name
        self._scripted: list[dict] = list(responses or [{"content": ""}])
        self._idx = 0

    @property
    def role(self) -> str:
        return self._role_name

    def _build_system_prompt(self) -> str:
        return f"You are the {self._role_name} agent."

    def think(self, user_prompt: str) -> dict:
        if self._idx < len(self._scripted):
            resp = self._scripted[self._idx]
            self._idx += 1
        else:
            resp = {"content": ""}
        return {**resp, "agent": self._role_name}
