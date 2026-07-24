from __future__ import annotations

import http.client
import json
import threading
import unittest

from local_bridge.mirrorme_bridge import (
    DEFAULT_ALLOWED_ORIGINS,
    DEFAULT_MODEL,
    HANDSHAKE_CONFIRMATION_PHRASE,
    HANDSHAKE_PROTOCOL_VERSION,
    MirrorMeBridgeHandler,
    ThreadingHTTPServer,
)


class BridgeServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), MirrorMeBridgeHandler)
        cls.server.ollama_url = "http://127.0.0.1:11434"
        cls.server.default_model = DEFAULT_MODEL
        cls.server.operator = "Marek K"
        cls.server.allowed_origins = set(DEFAULT_ALLOWED_ORIGINS)
        cls.server.handshake_sessions = {}
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.port = cls.server.server_address[1]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def request(self, method: str, path: str, payload=None, origin=None):
        headers = {}
        body = None
        if payload is not None:
            body = json.dumps(payload)
            headers["Content-Type"] = "application/json"
        if origin is not None:
            headers["Origin"] = origin
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=3)
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        raw = response.read()
        connection.close()
        return response.status, dict(response.getheaders()), json.loads(raw) if raw else None

    def test_health_and_allowed_origin(self) -> None:
        status, headers, payload = self.request("GET", "/health", origin="http://localhost:3000")
        self.assertEqual(status, 200)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["handshake_protocol"], HANDSHAKE_PROTOCOL_VERSION)
        self.assertEqual(headers.get("Access-Control-Allow-Origin"), "http://localhost:3000")

    def test_disallowed_origin_is_rejected(self) -> None:
        status, _, payload = self.request("GET", "/health", origin="https://example.com")
        self.assertEqual(status, 403)
        self.assertEqual(payload["error"], "origin_not_allowed")

    def test_handshake_lifecycle_and_nonce_redaction(self) -> None:
        status, _, challenge = self.request("GET", "/api/handshake/challenge")
        self.assertEqual(status, 200)

        status, _, verified = self.request(
            "POST",
            "/api/handshake/verify",
            {
                "session_id": challenge["session_id"],
                "nonce": challenge["nonce"],
                "operator": "Marek K",
                "confirmation_phrase": HANDSHAKE_CONFIRMATION_PHRASE,
            },
        )
        self.assertEqual(status, 200)
        self.assertEqual(verified["state"], "VERIFIED_LOCAL_SESSION")
        self.assertEqual(verified["readiness_mode"], "local_runtime_confirmation_not_authentication")

        status, _, session = self.request(
            "GET", f"/api/handshake/status?session_id={challenge['session_id']}"
        )
        self.assertEqual(status, 200)
        self.assertNotIn("nonce", session["session"])
        self.assertEqual(session["session"]["state"], "VERIFIED_LOCAL_SESSION")

    def test_nonce_mismatch_is_rejected(self) -> None:
        _, _, challenge = self.request("GET", "/api/handshake/challenge")
        status, _, payload = self.request(
            "POST",
            "/api/handshake/verify",
            {
                "session_id": challenge["session_id"],
                "nonce": "wrong",
                "operator": "Marek K",
                "confirmation_phrase": HANDSHAKE_CONFIRMATION_PHRASE,
            },
        )
        self.assertEqual(status, 403)
        self.assertEqual(payload["error"], "nonce_mismatch")


if __name__ == "__main__":
    unittest.main()
