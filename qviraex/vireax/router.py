from __future__ import annotations

from dataclasses import dataclass, field

from .adapters import AdapterEnvelope, AdapterResult, StaticAdapter


@dataclass
class ModelRouter:
    registry: dict[str, StaticAdapter] = field(default_factory=dict)

    def register(self, adapter: StaticAdapter) -> None:
        self.registry[adapter.spec.model] = adapter

    def dispatch(self, target_model: str, envelope: AdapterEnvelope) -> AdapterResult:
        if target_model not in self.registry:
            raise KeyError(f"adapter not registered: {target_model}")
        return self.registry[target_model].respond(envelope)