#!/usr/bin/env python3
"""MKultra v0.4 local bridge.

Extends the existing loopback-only MirrorME bridge with governed-evolution and
Thin Line claim-inspection endpoints. No endpoint executes patches or modifies
model weights, policies, identity or external systems.
"""

from __future__ import annotations

import argparse
import json
import urllib.parse
from http.server import ThreadingHTTPServer
from typing import Any

try:  # package import when launched with ``python -m``
    from local_bridge.mirrorme_bridge import (
        DEFAULT_ALLOWED_ORIGINS,
        DEFAULT_HOST,
        DEFAULT_OLLAMA_URL,
        DEFAULT_OPERATOR,
        MirrorMeBridgeHandler,
        _read_json,
    )
    from local_bridge.v04_service import MKultraV04Service
except ModuleNotFoundError:  # direct script launch from repository root
    from mirrorme_bridge import (  # type: ignore[no-redef]
        DEFAULT_ALLOWED_ORIGINS,
        DEFAULT_HOST,
        DEFAULT_OLLAMA_URL,
        DEFAULT_OPERATOR,
        MirrorMeBridgeHandler,
        _read_json,
    )
    from v04_service import MKultraV04Service  # type: ignore[no-redef]

DEFAULT_PORT = 8765
DEFAULT_MODEL = "mkultra:0.4"


class MKultraV04BridgeHandler(MirrorMeBridgeHandler):
    server_version = "MKultraLocalBridge/0.4"

    def do_GET(self) -> None:  # noqa: N802
        if not self._request_origin_allowed():
            self._send_json(403, {"ok": False, "error": "origin_not_allowed"})
            return
        path = urllib.parse.urlparse(self.path).path.rstrip("/")
        if path == "/api/v04/status":
            self._send_json(200, self.server.v04_service.status())  # type: ignore[attr-defined]
            return
        if path == "/api/v04/claims":
            self._send_json(200, self.server.v04_service.claims())  # type: ignore[attr-defined]
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        if not self._request_origin_allowed():
            self._send_json(403, {"ok": False, "error": "origin_not_allowed"})
            return
        path = urllib.parse.urlparse(self.path).path.rstrip("/")
        routes = {
            "/api/v04/evolution/propose": "propose",
            "/api/v04/evolution/evaluate": "evaluate",
            "/api/v04/evolution/approve": "approve",
        }
        action = routes.get(path)
        if action is None:
            super().do_POST()
            return

        try:
            payload = _read_json(self)
            if not self._verified_local_session(payload):
                self._send_json(
                    403,
                    {
                        "ok": False,
                        "error": "verified_local_session_required",
                        "truth_boundary": "Local session confirmation only; not legal identity proof.",
                    },
                )
                return
            service: MKultraV04Service = self.server.v04_service  # type: ignore[attr-defined]
            result = getattr(service, action)(payload)
            self._send_json(200, result)
        except json.JSONDecodeError:
            self._send_json(400, {"ok": False, "error": "invalid_json"})
        except (TypeError, ValueError, KeyError, PermissionError) as exc:
            self._send_json(
                400,
                {
                    "ok": False,
                    "error": type(exc).__name__,
                    "detail": str(exc),
                    "execution_authorized": False,
                },
            )
        except Exception as exc:
            self._send_json(
                500,
                {
                    "ok": False,
                    "error": "v04_bridge_error",
                    "detail": str(exc),
                    "execution_authorized": False,
                },
            )

    def _verified_local_session(self, payload: dict[str, Any]) -> bool:
        session_id = payload.get("session_id")
        if not isinstance(session_id, str) or not session_id:
            return False
        self._remove_expired_handshakes()
        session = self.server.handshake_sessions.get(session_id)  # type: ignore[attr-defined]
        return bool(session and session.get("state") == "VERIFIED_LOCAL_SESSION")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the MKultra v0.4 local bridge.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--operator", default=DEFAULT_OPERATOR)
    parser.add_argument(
        "--allowed-origin",
        action="append",
        dest="allowed_origins",
        help="Browser origin allowed to call the bridge; repeat for multiple origins.",
    )
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), MKultraV04BridgeHandler)
    server.ollama_url = args.ollama_url  # type: ignore[attr-defined]
    server.default_model = args.model  # type: ignore[attr-defined]
    server.operator = args.operator  # type: ignore[attr-defined]
    server.allowed_origins = set(args.allowed_origins or DEFAULT_ALLOWED_ORIGINS)  # type: ignore[attr-defined]
    server.handshake_sessions = {}  # type: ignore[attr-defined]
    server.v04_service = MKultraV04Service()  # type: ignore[attr-defined]

    print(f"MKultra v0.4 bridge running at http://{args.host}:{args.port}")
    print(f"Proxy target: {args.ollama_url}/api/chat")
    print(f"Default model: {args.model}")
    print("Governed evolution: proposal/export only; automatic execution disabled")
    server.serve_forever()


if __name__ == "__main__":
    main()
