# Example Debate — 5 Rounds

> **Note**: This transcript is generated with deterministic mock agents (`MultiScriptedAgent`)
> routed through the real `DebateOrchestrator`. No paid API was called. All arguments were
> authored as representative content to illustrate the system's routing and verdict logic.
> The orchestrator behaviour, round structure, parent-mediated routing, and cost reporting
> are identical to a live debate.

---

## Debate Parameters

| Parameter | Value |
|-----------|-------|
| **Topic** | Artificial intelligence should be regulated by international law |
| **Max rounds** | 5 |
| **Pro agent** | mock-v1 (deterministic) |
| **Con agent** | mock-v1 (deterministic) |
| **Judge agent** | mock-v1 (deterministic) |
| **Routing** | Parent-controlled — orchestrator mediates all turns |
| **Pricing unit** | per\_1m\_tokens (mock; all token counts are 0) |

---

## Round 1

**PRO**

International regulation of AI is essential to prevent an uncoordinated arms race. Without
binding international law, powerful nations will deploy increasingly capable AI systems for
military advantage, creating catastrophic risks for all of humanity. We already have
precedents in nuclear non-proliferation treaties and chemical weapons conventions. AI poses
comparable civilizational risks. Regulatory frameworks would establish red lines around
autonomous weapons, mass surveillance, and decision systems that affect fundamental rights.
Furthermore, regulation creates a level playing field so smaller economies are not
permanently disadvantaged by AI capabilities concentrated in a handful of countries.

*References:* UN General Assembly Resolution 77/211; OECD AI Principles 2023

---

**CON**

International regulation of AI would create a lowest-common-denominator framework that
protects entrenched incumbents and locks in existing power imbalances. Proposals at UN
bodies have consistently been weaponized by authoritarian governments to justify censorship
and surveillance, not to protect citizens. China and Russia would participate in any
international AI treaty only to the extent that it codifies state control of information.
Meanwhile, legitimate democratic innovation would be burdened by compliance costs. The
premise that we need international law assumes a consensus on AI values that does not exist
and cannot be coerced through treaty.

*References:* Freedom House (2023). Freedom on the Net Report; Mueller, M. (2010). Networks
and States.

---

## Round 2

**PRO**

The evidence for harm from unregulated AI is already accumulating. Facial recognition
systems deployed without oversight have produced wrongful arrests at rates three times higher
for darker-skinned individuals. Algorithmic hiring tools trained on biased historical data
have systematically excluded qualified candidates from marginalized groups. International law
would mandate impact assessments, require transparency reports, and establish liability for
harms. The EU AI Act demonstrates that regulation is technically feasible. Extending this
globally through treaty law would prevent regulatory arbitrage where companies simply
relocate to jurisdictions without protections.

*References:* Buolamwini & Gebru (2018) Gender Shades; EU AI Act 2024

---

**CON**

The AI bias harms my opponent cites are real, but the solution is domestic enforcement of
existing anti-discrimination law — not a new international treaty. Courts and regulators in
the US and EU have successfully applied existing frameworks to algorithmic discrimination
cases. International treaties notoriously lack enforcement mechanisms: signatories routinely
ignore provisions with no meaningful consequence. The Chemical Weapons Convention has not
prevented chemical weapons use. Adding another treaty layer to AI harms would create
bureaucratic friction for compliant firms while bad actors — including state actors —
simply ignore it.

*References:* Citron & Pasquale (2014). The Scored Society; CWC Non-Compliance Examples,
OPCW Reports

---

## Round 3

**PRO**

Security risks from uncoordinated AI development represent a genuine global commons problem.
Each nation acting in its own interest produces a collectively worse outcome — precisely the
scenario that international law is designed to address. Autonomous code-generation tools
have already been used in ransomware campaigns. These threats cross borders instantly. Only
international treaty obligations with verification mechanisms can align the incentives of
competing states toward shared safety standards. Regulation does not prevent beneficial
innovation — safety standards in aviation, pharmaceuticals, and nuclear energy have
coexisted with enormous technological progress.

*References:* Asilomar AI Principles (2017); Hendrycks et al. (2023). An Overview of
Catastrophic AI Risks.

---

**CON**

The comparison to nuclear and chemical weapons is analytically flawed. AI is a
general-purpose technology more analogous to electricity or the internet — pervasive,
dual-use by design, and enormously beneficial. Regulating AI at the international level
would be like establishing a UN treaty to govern software development. Innovation cycles in
AI are measured in months; treaty negotiation takes years or decades. By the time any
agreement is ratified, it will be obsolete and counterproductive. The Internet Governance
Forum has spent decades failing to produce binding global internet standards for exactly
this reason.

*References:* Drezner, D. (2019). The Technology Fallacy; IGF History and Limitations

---

## Round 4

**PRO**

Critics claim regulation will slow innovation, but the empirical evidence points the other
way. The EU GDPR initially faced similar objections; post-GDPR studies found that the
regulation accelerated investment in privacy-preserving technologies and built consumer
trust that expanded the overall market. Clear regulatory frameworks reduce legal uncertainty
for investors and create predictable environments for long-term R&D investment. Countries
with strong pharmaceutical regulation remain global leaders in drug innovation precisely
because safety standards establish consumer confidence. International AI regulation would
produce the same effect: a larger, more trusted global AI market.

*References:* Goldfarb & Tucker (2022). Digital Economics.; GDPR Economic Impact Studies,
Copenhagen Economics 2023

---

**CON**

GDPR is the wrong model for AI. GDPR governs data processing — a relatively well-defined
domain. AI systems are architecturally diverse: large language models, reinforcement
learning agents, computer vision systems. A single international framework would need to
encompass all of them, inevitably producing vague standards that compliance teams exploit
through superficial procedural changes. The EU AI Act has already been criticized by AI
safety researchers for focusing on use-case categories rather than capability thresholds.
Scaling this to an international treaty amplifies every design flaw. Better outcomes come
from adaptive domestic regulation with mutual recognition agreements.

*References:* Brundage et al. (2022). Improving Governance of the AI Supply Chain; EU AI
Act Critique, Future of Life Institute 2024

---

## Round 5

**PRO**

To summarize the pro case: international AI regulation is not a constraint on progress but
its prerequisite. History consistently shows that technologies posing societal-scale risks
require binding international agreements to be deployed safely. We have working models from
existing treaty regimes, demonstrated regulatory feasibility from national frameworks, and
mounting evidence of real-world harms from unregulated deployment. The alternative — a
regulatory vacuum where the most powerful and least cautious actors set the pace — is far
more dangerous for innovation, security, and human rights than any international oversight
framework could be.

*References:* Summary synthesis of rounds 1–4; Dafoe (2018). AI Governance: A Research
Agenda

---

**CON**

The con case rests on three pillars my opponent has not answered. First, international AI
regulation would be captured by authoritarian states to legitimize repression. Second,
existing legal frameworks are sufficient for documented harms and are already being applied.
Third, AI is too fast-moving and heterogeneous for treaty-timescale governance. Adaptive
domestic frameworks with interoperability agreements — like financial regulation's Basel
Accords model — achieve international coordination without locking in a lowest-common-
denominator treaty. Innovation leadership requires regulatory agility, not a global
compliance regime.

*References:* Summary synthesis of con rounds 1–4; Basel Accords as Soft-Law Alternative

---

## Judge Decision

**Winner: PRO**

| | Score |
|---|---|
| Pro | **74** |
| Con | **68** |

**Justification:**

Both sides demonstrated substantial command of the evidence. Pro built a coherent cumulative
case: international regulatory precedents exist, documented harms are already occurring, and
existing national frameworks like the EU AI Act establish technical feasibility. The
innovation-suppression objection was effectively rebutted with GDPR empirical evidence.
Con's strongest arguments were the enforcement gap in international law and the risk of
authoritarian co-optation — both serious concerns. However, Con's counter-proposal concedes
the need for international coordination while arguing for a different form. Pro's response
that a regulatory vacuum is riskier than imperfect international oversight is persuasive
given the speed of AI capability growth.

---

## Usage and Cost Summary

> Token counts are zero because mock agents were used. In a live debate with real LLM
> providers, this section reports per-agent token usage and USD cost.

| Role | Input tokens | Output tokens |
|------|-------------|--------------|
| Pro  | 0 | 0 |
| Con  | 0 | 0 |
| Judge | 0 | 0 |
| **Total** | **0** | **0** |

**Total cost: $0.0000** (mock run — no real API calls)

In a live run with `gpt-4o-mini` for debaters and `gpt-4o` for the judge over 5 rounds,
expected cost is approximately **$0.02–$0.05** depending on response length.
See `config/setup_example.json` for reference pricing values.

---

## How This Was Generated

This example was produced by running the real `DebateOrchestrator` with
`MultiScriptedAgent` instances (deterministic scripted responses) rather than live LLM
providers. The orchestrator routing, state management, contract validation, and cost
reporting are identical to a live debate. Only the agent `think()` method is stubbed.

To regenerate or adapt this example:

```python
from debate.services.orchestrator import DebateOrchestrator

class MockAgent:
    def __init__(self, role, responses):
        self.role = role
        self._responses = responses
        self._idx = 0
        class _FakeProvider:
            provider_name = "mock"
            model = "mock-v1"
            def get_usage(self): return {"input_tokens": 0, "output_tokens": 0}
        self.provider = _FakeProvider()

    def think(self, prompt):
        resp = self._responses[self._idx % len(self._responses)]
        self._idx += 1
        return resp

# ... define PRO_RESPONSES, CON_RESPONSES, JUDGE_RESPONSE
orc = DebateOrchestrator(
    judge_agent=MockAgent("judge", [JUDGE_RESPONSE]),
    pro_agent=MockAgent("pro", PRO_RESPONSES),
    con_agent=MockAgent("con", CON_RESPONSES),
    topic="Your debate topic here",
    max_rounds=5,
)
result = orc.run()
print("Winner:", result["winner"])
```
