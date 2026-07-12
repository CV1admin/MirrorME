from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol


@dataclass(frozen=True)
class AdapterSpec:
    model: str
    provider: str
    role: str
    enabled: bool = True
    capabilities: tuple[str, ...] = ()
    limits: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AdapterEnvelope:
    target_model: str
    role: str
    prompt: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AdapterResult:
    model: str
    provider: str
    role: str
    output: str
    confidence: float
    metadata: dict[str, Any] = field(default_factory=dict)


class Adapter(Protocol):
    spec: AdapterSpec

    def respond(self, envelope: AdapterEnvelope) -> AdapterResult:
        ...


class StaticAdapter:
    def __init__(self, spec: AdapterSpec) -> None:
        self.spec = spec

    def respond(self, envelope: AdapterEnvelope) -> AdapterResult:
        output = f"{self.spec.model} [{envelope.role}] processed: {envelope.prompt}".strip()
        return AdapterResult(
            model=self.spec.model,
            provider=self.spec.provider,
            role=envelope.role,
            output=output,
            confidence=0.72,
            metadata={
                "adapter_mode": "STATIC_SIMULATION",
                "capabilities": self.spec.capabilities,
                **envelope.metadata,
            },
        )


class XAIAdapter:
    """Server-side xAI Responses API adapter for the Grok critic role.

    The API key is read from ``XAI_API_KEY`` unless passed explicitly. The
    adapter never exposes the key in its result metadata and sets ``store`` to
    false for every request.
    """

    DEFAULT_BASE_URL = "https://api.x.ai/v1"
    DEFAULT_MODEL_ID = "grok-4.5"

    def __init__(
        self,
        spec: AdapterSpec,
        *,
        api_key: str | None = None,
        model_id: str | None = None,
        base_url: str | None = None,
        timeout: float = 120.0,
        urlopen: Callable[..., Any] = urllib.request.urlopen,
    ) -> None:
        resolved_key = (api_key or os.getenv("XAI_API_KEY", "")).strip()
        if not resolved_key:
            raise ValueError("XAI_API_KEY is required for the live xAI adapter")

        self.spec = spec
        self.api_key = resolved_key
        self.model_id = (model_id or os.getenv("XAI_MODEL", self.DEFAULT_MODEL_ID)).strip()
        self.base_url = (base_url or os.getenv("XAI_BASE_URL", self.DEFAULT_BASE_URL)).rstrip("/")
        self.timeout = timeout
        self._urlopen = urlopen

    def respond(self, envelope: AdapterEnvelope) -> AdapterResult:
        payload = {
            "model": self.model_id,
            "input": [
                {
                    "role": "system",
                    "content": self._system_instruction(envelope),
                },
                {
                    "role": "user",
                    "content": envelope.prompt,
                },
            ],
            "store": False,
        }
        request = urllib.request.Request(
            f"{self.base_url}/responses",
            data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "MirrorME-QNIP/0.1",
            },
            method="POST",
        )

        try:
            with self._urlopen(request, timeout=self.timeout) as response:
                body = response.read()
        except urllib.error.HTTPError as exc:
            detail = self._read_error_body(exc)
            raise RuntimeError(f"xAI API HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"xAI API unreachable: {exc.reason}") from exc

        try:
            decoded = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError("xAI API returned invalid JSON") from exc

        output = self._extract_output_text(decoded)
        usage = decoded.get("usage") if isinstance(decoded.get("usage"), dict) else {}

        return AdapterResult(
            model=self.spec.model,
            provider=self.spec.provider,
            role=envelope.role,
            output=output,
            confidence=0.72,
            metadata={
                "adapter_mode": "LIVE_XAI_API",
                "api": "responses",
                "xai_model_id": decoded.get("model", self.model_id),
                "response_id": decoded.get("id"),
                "response_status": decoded.get("status"),
                "store": False,
                "usage": usage,
                "confidence_mode": "adapter_default_not_model_probability",
                "capabilities": self.spec.capabilities,
                **envelope.metadata,
            },
        )

    @staticmethod
    def _system_instruction(envelope: AdapterEnvelope) -> str:
        return (
            "You are Grok operating as the independent critic inside the "
            "Civilisation.One MirrorME/QNIP reasoning pipeline. Critically test "
            "assumptions, identify contradictions, separate simulation from "
            "hardware evidence, and propose falsifiable checks. Do not claim "
            "access to quantum hardware, physical telemetry, private systems, or "
            "external actions. Return a concise technical assessment. "
            f"Assigned role: {envelope.role}."
        )

    @staticmethod
    def _extract_output_text(payload: dict[str, Any]) -> str:
        direct = payload.get("output_text")
        if isinstance(direct, str) and direct.strip():
            return direct.strip()

        fragments: list[str] = []
        output_items = payload.get("output", [])
        if isinstance(output_items, list):
            for item in output_items:
                if not isinstance(item, dict):
                    continue
                content_items = item.get("content", [])
                if not isinstance(content_items, list):
                    continue
                for content in content_items:
                    if not isinstance(content, dict):
                        continue
                    if content.get("type") == "output_text" and isinstance(content.get("text"), str):
                        text = content["text"].strip()
                        if text:
                            fragments.append(text)

        if not fragments:
            raise RuntimeError("xAI API response did not contain output_text")
        return "\n".join(fragments)

    @staticmethod
    def _read_error_body(exc: urllib.error.HTTPError) -> str:
        try:
            body = exc.read().decode("utf-8", errors="replace").strip()
        except Exception:
            body = ""
        return body[:1000] or str(exc.reason)
