from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
import json
from typing import Any
from uuid import UUID, uuid4


class AccessScope(StrEnum):
    PRIVATE = "private"
    TRUSTED_GROUP = "trusted_group"
    PROJECT = "project"
    ORGANISATION = "organisation"
    COMMUNITY = "community"
    PUBLIC = "public"


class ResourceStatus(StrEnum):
    DRAFT = "draft"
    VALIDATED = "validated"
    SIGNED = "signed"
    PUBLISHED = "published"
    REVOKED = "revoked"


@dataclass(frozen=True, slots=True)
class ResourcePayload:
    media_type: str
    data: dict[str, Any] | list[Any] | str | int | float | bool | None
    summary: str = ""

    def canonical_bytes(self) -> bytes:
        document = {
            "media_type": self.media_type,
            "summary": self.summary,
            "data": self.data,
        }
        return json.dumps(
            document,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")

    @property
    def digest(self) -> str:
        return f"sha256:{sha256(self.canonical_bytes()).hexdigest()}"


@dataclass(frozen=True, slots=True)
class ResourceManifest:
    resource_id: UUID
    version: int
    resource_type: str
    creator_node_id: str
    owner_principal: str
    access_scope: AccessScope
    created_at: datetime
    parent_digest: str | None = None
    citations: tuple[str, ...] = ()
    allowed_principals: tuple[str, ...] = ()
    status: ResourceStatus = ResourceStatus.DRAFT

    @classmethod
    def create(
        cls,
        *,
        resource_type: str,
        creator_node_id: str,
        owner_principal: str,
        access_scope: AccessScope = AccessScope.PRIVATE,
        parent_digest: str | None = None,
        citations: tuple[str, ...] = (),
        allowed_principals: tuple[str, ...] = (),
        resource_id: UUID | None = None,
        version: int = 1,
    ) -> "ResourceManifest":
        if not resource_type.strip():
            raise ValueError("resource_type must not be empty")
        if not creator_node_id.strip():
            raise ValueError("creator_node_id must not be empty")
        if not owner_principal.strip():
            raise ValueError("owner_principal must not be empty")
        if version < 1:
            raise ValueError("version must be positive")

        return cls(
            resource_id=resource_id or uuid4(),
            version=version,
            resource_type=resource_type,
            creator_node_id=creator_node_id,
            owner_principal=owner_principal,
            access_scope=access_scope,
            created_at=datetime.now(UTC),
            parent_digest=parent_digest,
            citations=citations,
            allowed_principals=allowed_principals,
        )


@dataclass(frozen=True, slots=True)
class ResourceEnvelope:
    manifest: ResourceManifest
    payload: ResourcePayload
    content_digest: str
    signature: str | None = None
    observer_hash: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        manifest: ResourceManifest,
        payload: ResourcePayload,
        *,
        metadata: dict[str, str] | None = None,
    ) -> "ResourceEnvelope":
        return cls(
            manifest=manifest,
            payload=payload,
            content_digest=payload.digest,
            metadata=dict(metadata or {}),
        )

    def canonical_manifest_bytes(self) -> bytes:
        manifest = asdict(self.manifest)
        manifest["resource_id"] = str(self.manifest.resource_id)
        manifest["created_at"] = self.manifest.created_at.isoformat()
        manifest["access_scope"] = self.manifest.access_scope.value
        manifest["status"] = self.manifest.status.value
        document = {
            "manifest": manifest,
            "content_digest": self.content_digest,
            "metadata": self.metadata,
        }
        return json.dumps(
            document,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")

    @property
    def envelope_digest(self) -> str:
        digest_input = self.canonical_manifest_bytes() + self.payload.canonical_bytes()
        return f"sha256:{sha256(digest_input).hexdigest()}"

    def verify_digest(self) -> bool:
        return self.content_digest == self.payload.digest
