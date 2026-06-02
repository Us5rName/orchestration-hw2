"""AgentFactory — creates agent instances with skills resolved from config.

Input: role (str), agent_cfg (dict), provider (LLMProvider),
       topic (str), timeout (float), registry (SkillRegistry)
Output: JudgeAgent | ProAgent | ConAgent with skills attached
Setup: resolves skill names via SkillRegistry; mirrors ProviderFactory pattern
"""

from ..agents.con_agent import ConAgent
from ..agents.judge_agent import JudgeAgent
from ..agents.pro_agent import ProAgent
from ..providers.base_provider import LLMProvider
from ..skills.registry import SkillRegistry


def create_agent(
    role: str,
    agent_cfg: dict,
    provider: LLMProvider,
    topic: str,
    timeout: float,
    registry: SkillRegistry,
) -> JudgeAgent | ProAgent | ConAgent:
    """Create an agent with skills resolved from the SkillRegistry.

    Args:
        role: Agent role ('judge', 'pro', 'con').
        agent_cfg: Agent config dict (model, temperature, skills list).
        provider: Configured LLM provider instance.
        topic: The debate topic.
        timeout: Request timeout in seconds.
        registry: SkillRegistry used to resolve skill name strings.

    Returns:
        Configured agent instance with resolved skills.
    """
    skill_names = agent_cfg.get("skills", [])
    skills = [registry.get(name) for name in skill_names]
    model = agent_cfg.get("model", "")

    if role == "judge":
        return JudgeAgent(
            provider, model, agent_cfg.get("temperature", 0.3), timeout, topic, skills
        )
    if role == "pro":
        return ProAgent(
            provider, model, agent_cfg.get("temperature", 0.7), timeout, topic, skills
        )
    return ConAgent(
        provider, model, agent_cfg.get("temperature", 0.7), timeout, topic, skills
    )
