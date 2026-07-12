from __future__ import annotations

import unittest

from qviraex.vireax.adapters import AdapterSpec, StaticAdapter
from qviraex.vireax.center_node import VIREAXCenterNode
from qviraex.vireax.router import ModelRouter


class VIREAXSmokeTest(unittest.TestCase):
    def test_final_output_approved(self) -> None:
        router = ModelRouter()
        for spec in [
            AdapterSpec(model="GPT", provider="OpenAI", role="architect"),
            AdapterSpec(model="Grok", provider="xAI", role="critic"),
            AdapterSpec(model="Gemini", provider="Google", role="context_analyst"),
            AdapterSpec(model="Claude", provider="Anthropic", role="safety_reviewer"),
            AdapterSpec(model="DeepSeek", provider="DeepSeek", role="technical_validator"),
            AdapterSpec(model="Llama", provider="Meta", role="local_fallback"),
        ]:
            router.register(StaticAdapter(spec))

        node = VIREAXCenterNode(router=router)
        result = node.run(
            session_id="VX-SESSION-0001",
            operator="VIREAX",
            task="Design multi-model reasoning protocol",
            model_roles={
                "GPT": "architect",
                "Grok": "critic",
                "Gemini": "context_analyst",
                "Claude": "safety_reviewer",
                "DeepSeek": "technical_validator",
                "Llama": "local_fallback",
            },
        )

        self.assertEqual(result.state, "FINAL_OUTPUT")
        self.assertEqual(result.next_action, "COMMIT_AUDIT")
        self.assertTrue(result.audit_hash.startswith("sha256:"))
        self.assertGreater(result.evidence_level, 0)
        self.assertTrue(result.responses)
        self.assertTrue(
            all(response["metadata"]["adapter_mode"] == "STATIC_SIMULATION" for response in result.responses)
        )


if __name__ == "__main__":
    unittest.main()
