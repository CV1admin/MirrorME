from __future__ import annotations

import json
import os
import unittest
from unittest.mock import patch

from qviraex.vireax.adapters import AdapterEnvelope, AdapterSpec, XAIAdapter


class _FakeResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self._body = json.dumps(payload).encode("utf-8")

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        del exc_type, exc, traceback

    def read(self) -> bytes:
        return self._body


class XAIAdapterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = AdapterSpec(
            model="Grok",
            provider="xAI",
            role="critic",
            capabilities=("qnip_review",),
        )

    def test_requires_api_key(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "XAI_API_KEY"):
                XAIAdapter(self.spec)

    def test_sends_non_stored_responses_request(self) -> None:
        captured: dict[str, object] = {}

        def fake_urlopen(request, timeout):
            captured["url"] = request.full_url
            captured["authorization"] = request.get_header("Authorization")
            captured["timeout"] = timeout
            captured["payload"] = json.loads(request.data.decode("utf-8"))
            return _FakeResponse(
                {
                    "id": "resp-test-001",
                    "model": "grok-4.5",
                    "status": "completed",
                    "output": [
                        {
                            "type": "message",
                            "role": "assistant",
                            "content": [
                                {
                                    "type": "output_text",
                                    "text": "The routing assumption needs a measured fidelity model.",
                                }
                            ],
                        }
                    ],
                    "usage": {
                        "input_tokens": 20,
                        "output_tokens": 9,
                        "total_tokens": 29,
                    },
                }
            )

        adapter = XAIAdapter(
            self.spec,
            api_key="xai-test-key",
            model_id="grok-4.5",
            urlopen=fake_urlopen,
            timeout=30.0,
        )
        result = adapter.respond(
            AdapterEnvelope(
                target_model="Grok",
                role="critic",
                prompt="Review this QNIP route.",
                metadata={"session_id": "test-session"},
            )
        )

        self.assertEqual(captured["url"], "https://api.x.ai/v1/responses")
        self.assertEqual(captured["authorization"], "Bearer xai-test-key")
        self.assertEqual(captured["timeout"], 30.0)

        request_payload = captured["payload"]
        self.assertIsInstance(request_payload, dict)
        self.assertEqual(request_payload["model"], "grok-4.5")
        self.assertFalse(request_payload["store"])
        self.assertEqual(request_payload["input"][1]["content"], "Review this QNIP route.")

        self.assertEqual(result.output, "The routing assumption needs a measured fidelity model.")
        self.assertEqual(result.metadata["adapter_mode"], "LIVE_XAI_API")
        self.assertEqual(result.metadata["response_id"], "resp-test-001")
        self.assertFalse(result.metadata["store"])
        self.assertNotIn("xai-test-key", json.dumps(result.metadata))

    def test_rejects_response_without_text(self) -> None:
        def fake_urlopen(request, timeout):
            del request, timeout
            return _FakeResponse({"id": "empty", "output": [], "status": "completed"})

        adapter = XAIAdapter(self.spec, api_key="xai-test-key", urlopen=fake_urlopen)
        with self.assertRaisesRegex(RuntimeError, "did not contain output_text"):
            adapter.respond(
                AdapterEnvelope(
                    target_model="Grok",
                    role="critic",
                    prompt="Review.",
                )
            )


if __name__ == "__main__":
    unittest.main()
