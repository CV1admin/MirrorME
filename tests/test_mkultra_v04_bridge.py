from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from local_bridge.mirrorme_bridge import MirrorMeBridgeHandler
from local_bridge.mkultra_v04_bridge import MKultraV04BridgeHandler


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MODELFILE = REPOSITORY_ROOT / "ollama" / "Modelfile.mkultra-v0.4"


class MKultraV04BridgeOutputTests(unittest.TestCase):
    def test_chat_proxy_forces_thinking_disabled_without_mutating_input(self) -> None:
        handler = object.__new__(MKultraV04BridgeHandler)
        payload = {
            "model": "mkultra:0.4",
            "stream": True,
            "think": True,
            "messages": [{"role": "user", "content": "E, M"}],
        }

        with patch.object(MirrorMeBridgeHandler, "_proxy_ollama_chat") as proxy:
            handler._proxy_ollama_chat(payload)

        self.assertTrue(payload["think"])
        proxy.assert_called_once()
        proxied_payload = proxy.call_args.args[0]
        self.assertIsNot(proxied_payload, payload)
        self.assertFalse(proxied_payload["think"])
        self.assertEqual(proxied_payload["messages"], payload["messages"])

    def test_modelfile_disables_thinking_and_routes_read_only_requests_directly(self) -> None:
        content = MODELFILE.read_text(encoding="utf-8")

        self.assertIn("/no_think", content)
        self.assertIn("Answer read-only requests directly", content)
        self.assertIn("Read-only requests do not require human approval", content)
        self.assertIn("Do not print hidden reasoning", content)

    def test_modelfile_contains_correct_144_arithmetic_guard(self) -> None:
        content = MODELFILE.read_text(encoding="utf-8")

        self.assertIn("F_12 = 144 = 12^2 = 2^4*3^2", content)
        self.assertIn("24*3^2 = 216", content)


if __name__ == "__main__":
    unittest.main()
