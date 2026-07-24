# Lightful integration boundary

MirrorME uses a small, deterministic subset of Jean Charbonneau's Lightful Reasoning
Framework as an optional decision guard in the VIREAX center node.

The integration implements:

- explicit Safety, Consent, and Dignity checks;
- informed authority decomposition for external actions;
- evidence floors proportional to stakes;
- preference for reversible trials under uncertainty;
- human sovereignty and independent review for high-stakes decisions;
- audit-ledger recording of every applied decision.

It deliberately does not import metaphysical claims, treat resonance as evidence, detect
consciousness, infer consent, or grant authority. The guard receives caller-declared facts,
returns a deterministic decision, and runs after the existing MirrorME policy gate. It
cannot override a policy rejection.

## Example

```python
from qviraex.vireax import LightfulContext

result = node.run(
    session_id="VX-1",
    operator="VIREAX",
    task="Prepare a local draft",
    model_roles={"GPT": "architect"},
    lightful_context=LightfulContext(
        decision_target="prepare local draft",
        decision_actor="MirrorME",
        consent_relevance="no",
        consent_status="not_applicable",
        evidence_status="sufficient",
        reversibility="high",
        authorized_to_act="yes",
        can_verify_after_action="yes",
    ),
)
```

If `lightful_context` is omitted, the guard does not invent missing facts and the legacy
VIREAX flow remains unchanged.
