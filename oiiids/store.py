from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol
from uuid import UUID

from .models import ResourceEnvelope


class ResourceStore(Protocol):
    def put(self, envelope: ResourceEnvelope) -> None: ...

    def get(self, resource_id: UUID, version: int | None = None) -> ResourceEnvelope | None: ...

    def list_latest(self) -> Iterable[ResourceEnvelope]: ...


class InMemoryResourceStore:
    def __init__(self) -> None:
        self._resources: dict[UUID, dict[int, ResourceEnvelope]] = {}

    def put(self, envelope: ResourceEnvelope) -> None:
        versions = self._resources.setdefault(envelope.manifest.resource_id, {})
        current = versions.get(envelope.manifest.version)
        if current is not None and current.envelope_digest != envelope.envelope_digest:
            raise ValueError("resource version already exists with different content")
        versions[envelope.manifest.version] = envelope

    def get(self, resource_id: UUID, version: int | None = None) -> ResourceEnvelope | None:
        versions = self._resources.get(resource_id)
        if not versions:
            return None
        selected_version = version if version is not None else max(versions)
        return versions.get(selected_version)

    def list_latest(self) -> Iterable[ResourceEnvelope]:
        for versions in self._resources.values():
            yield versions[max(versions)]
