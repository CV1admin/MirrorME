from __future__ import annotations

from dataclasses import dataclass, field

from .adapters import Adapter, AdapterEnvelope, AdapterResult


@dataclass
class ModelRouter:
    registry: dict[str, Adapter] = field(default_factory=dict)

    def register(self, adapter: Adapter) -> None:
        self.registry[adapter.spec.model] = adapter

    def dispatch(self, target_model: str, envelope: AdapterEnvelope) -> AdapterResult:
        if target_model not in self.registry:
            raise KeyError(f"adapter not registered: {target_model}")
        return self.registry[target_model].respond(envelope)
