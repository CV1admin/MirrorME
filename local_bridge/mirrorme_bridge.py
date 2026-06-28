#!/usr/bin/env python3
"""Local MirrorME bridge.

This process runs only on the operator's machine. It gives the MirrorME browser UI
one stable local endpoint and proxies chat requests to a local Ollama runtime.

Default route:
    MirrorME UI -> http://localhost:8765/api/chat -> http://localhost:11434/api/chat

No API keys are required. No request is sent to a cloud model by this bridge.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "llama3.1:8b"


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, separators=(",", ":")).encode("utf-8")


def _read_json(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    length = int(handler.headers.get("Content-Length", "0") or "0")
    if length <= 0:
        return {}
    raw = handler.rfile.read(length)
    if not raw:
        return {}
    return json.loads(raw.decode("utf-8"))


class MirrorMeBridgeHandler(BaseHTTPRequestHandler):
    server_version = "MirrorMeLocalBridge/0.1"

    def _cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type,Authorization")
        self.send_header("Cache-Control", "no-store")

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = _json_bytes(payload)
        self.send_response(status)
        self._cors_headers()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        if self.path.rstrip("/") == "/health":
            self._send_json(
                200,
                {
                    "ok": True,
                    "service": "mirrorme-local-bridge",
                    "default_model": self.server.default_model,  # type: ignore[attr-defined]
                    "ollama_url": self.server.ollama_url,  # type: ignore[attr-defined]
                },
            )
            return

        self._send_json(404, {"ok": False, "error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        if self.path.rstrip("/") != "/api/chat":
            self._send_json(404, {"ok": False, "error": "not_found"})
            return

        try:
            payload = _read_json(self)
            self._proxy_ollama_chat(payload)
        except json.JSONDecodeError:
            self._send_json(400, {"ok": False, "error": "invalid_json"})
        except urllib.error.URLError as exc:
            self._send_json(
                502,
                {
                    "ok": False,
                    "error": "ollama_unreachable",
                    "detail": str(exc.reason),
                    "hint": "Start Ollama with `ollama serve` and pull the selected model.",
                },
            )
        except Exception as exc:  # defensive boundary for local operator visibility
            self._send_json(500, {"ok": False, "error": "bridge_error", "detail": str(exc)})

    def _proxy_ollama_chat(self, payload: dict[str, Any]) -> None:
        ollama_url = self.server.ollama_url.rstrip("/")  # type: ignore[attr-defined]
        default_model = self.server.default_model  # type: ignore[attr-defined]

        payload.setdefault("model", default_model)
        payload.setdefault("stream", True)

        request = urllib.request.Request(
            f"{ollama_url}/api/chat",
            data=_json_bytes(payload),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(request, timeout=120) as response:
            self.send_response(response.status)
            self._cors_headers()
            self.send_header("Content-Type", "application/x-ndjson")
            self.end_headers()

            while True:
                chunk = response.read(4096)
                if not chunk:
                    break
                self.wfile.write(chunk)
                self.wfile.flush()

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("[MirrorMeBridge] " + fmt % args + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local MirrorME bridge.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), MirrorMeBridgeHandler)
    server.ollama_url = args.ollama_url  # type: ignore[attr-defined]
    server.default_model = args.model  # type: ignore[attr-defined]

    print(f"MirrorME local bridge running at http://{args.host}:{args.port}")
    print(f"Proxy target: {args.ollama_url}/api/chat")
    print(f"Default model: {args.model}")
    server.serve_forever()


if __name__ == "__main__":
    main()
