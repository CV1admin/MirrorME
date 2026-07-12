from __future__ import annotations

import json
import os

from qviraex.mrql import MRQLParser
from qviraex.vireax.adapters import AdapterSpec, StaticAdapter, XAIAdapter
from qviraex.vireax.center_node import VIREAXCenterNode
from qviraex.vireax.router import ModelRouter


def run_qviraex() -> None:
    parser = MRQLParser()
    ritual = parser.parse(
        """ritual demo v0.1 {
sequence {
RUN {
  step: "Run QVIREAX"
}
}
}"""
    )

    router = ModelRouter()
    for spec in [
        AdapterSpec(model="GPT", provider="OpenAI", role="architect"),
        AdapterSpec(model="Claude", provider="Anthropic", role="safety_reviewer"),
        AdapterSpec(model="Llama", provider="Meta", role="local_fallback"),
    ]:
        router.register(StaticAdapter(spec))

    grok_spec = AdapterSpec(
        model="Grok",
        provider="xAI",
        role="critic",
        capabilities=("technical_critique", "contradiction_detection", "qnip_review"),
    )
    xai_live = bool(os.getenv("XAI_API_KEY", "").strip())
    if xai_live:
        router.register(XAIAdapter(grok_spec))
    else:
        router.register(StaticAdapter(grok_spec))

    node = VIREAXCenterNode(router=router)
    result = node.run(
        session_id="QVIREAX-DEMO-001",
        operator="QVIREAX",
        task="Review the QNIP-ME quantum network integration architecture",
        model_roles={
            "GPT": "architect",
            "Grok": "critic",
            "Claude": "safety_reviewer",
            "Llama": "local_fallback",
        },
    )

    print("QVIREAX online")
    print(f"MRQL ritual: {ritual.name} v{ritual.version}")
    print(f"xAI Grok adapter: {'LIVE_XAI_API' if xai_live else 'STATIC_SIMULATION'}")
    print(f"VIREAX state: {result.state}")
    print(f"Next action: {result.next_action}")
    print(f"Audit hash: {result.audit_hash}")
    print("Result JSON:")
    print(json.dumps(result.__dict__, indent=2, sort_keys=True))


if __name__ == "__main__":
    run_qviraex()
