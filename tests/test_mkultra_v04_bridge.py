from __future__ import annotations

import unittest
from unittest.mock import patch

from local_bridge.mirrorme_bridge import MirrorMeBridgeHandler
from local_bridge.mkultra_v04_bridge import MKultraV04BridgeHandler


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


if __name__ == "__main__":
    unittest.main()
