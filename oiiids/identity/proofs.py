from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
import json
from uuid import UUID

from .node_id import NodeID


@dataclass(frozen=True, slots=True)
class OperationContext:
    operation_id: UUID
    principal: str
    node_id: NodeID
    key_id: str
    method: str
    resource_digest: str | None
    gateway_session_id: str
    nonce: str
    issued_at: datetime

    def __post_init__(self) -> None:
        for name, value in (
            ("principal", self.principal),
            ("key_id", self.key_id),
            ("method", self.method),
            ("gateway_session_id", self.gateway_session_id),
            ("nonce", self.nonce),
        ):
            if not value.strip():
                raise ValueError(f"{name} must not be empty")
        if self.issued_at.tzinfo is None:
            raise ValueError("issued_at must be timezone-aware")

    @classmethod
    def create(
        cls,
        *,
        operation_id: UUID,
        principal: str,
        node_id: NodeID,
        key_id: str,
        method: str,
        gateway_session_id: str,
        nonce: str,
        resource_digest: str | None = None,
    ) -> "OperationContext":
        return cls(
            operation_id=operation_id,
            principal=principal,
            node_id=node_id,
            key_id=key_id,
            method=method,
            resource_digest=resource_digest,
            gateway_session_id=gateway_session_id,
            nonce=nonce,
            issued_at=datetime.now(UTC),
        )

    def canonical_bytes(self) -> bytes:
        document = {
            "operation_id": str(self.operation_id),
            "principal": self.principal,
            "node_id": str(self.node_id),
            "key_id": self.key_id,
            "method": self.method,
            "resource_digest": self.resource_digest,
            "gateway_session_id": self.gateway_session_id,
            "nonce": self.nonce,
            "issued_at": self.issued_at.isoformat(),
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
class SignedOperationProof:
    context: OperationContext
    signature: bytes

    def __post_init__(self) -> None:
        if len(self.signature) != 64:
            raise ValueError("Ed25519 signature must contain exactly 64 bytes")
