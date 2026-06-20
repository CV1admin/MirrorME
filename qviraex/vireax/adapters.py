from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


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
            metadata={"capabilities": self.spec.capabilities, **envelope.metadata},
        )