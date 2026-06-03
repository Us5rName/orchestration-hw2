"""Config dict builders for DebateSDK wiring.

These pure functions translate typed config objects into the plain dicts
that provider_factory and agent_factory expect, keeping sdk.py concise.
"""


def build_provider_dict(agent_cfg) -> dict:
    """Build the provider_factory input dict from an agent config object."""
    return {
        "provider": agent_cfg.provider,
        "model": agent_cfg.model,
        "temperature": agent_cfg.temperature,
        "base_url": agent_cfg.base_url,
        "timeout": agent_cfg.timeout,
    }


def build_agent_dict(agent_cfg) -> dict:
    """Build the agent_factory input dict from an agent config object."""
    return {
        "model": agent_cfg.model,
        "temperature": agent_cfg.temperature,
        "skills": agent_cfg.skills,
    }


def build_pricing_dict(pricing_cfg) -> dict:
    """Build the orchestrator pricing dict from a pricing config object."""
    return {
        "unit": pricing_cfg.unit,
        "judge": {"input": pricing_cfg.judge.input, "output": pricing_cfg.judge.output},
        "pro": {"input": pricing_cfg.pro.input, "output": pricing_cfg.pro.output},
        "con": {"input": pricing_cfg.con.input, "output": pricing_cfg.con.output},
    }
