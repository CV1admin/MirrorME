from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from .node_id import NodeID


class NodeStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    REJECTED = "rejected"


class KeyStatus(StrEnum):
    ACTIVE = "active"
    RETIRED = "retired"
    REVOKED = "revoked"


@dataclass(frozen=True, slots=True)
class NodeKeyRecord:
    key_id: str
    public_key: bytes
    status: KeyStatus = KeyStatus.ACTIVE
    created_at: datetime = datetime.now(UTC)
    expires_at: datetime | None = None
    revoked_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.key_id.strip():
            raise ValueError("key_id must not be empty")
        if len(self.public_key) != 32:
            raise ValueError("Ed25519 public key must contain exactly 32 bytes")
        if self.status is KeyStatus.REVOKED and self.revoked_at is None:
            raise ValueError("revoked key requires revoked_at")

    def is_usable_at(self, instant: datetime) -> bool:
        if self.status is not KeyStatus.ACTIVE:
            return False
        if self.expires_at is not None and instant >= self.expires_at:
            return False
        return True


@dataclass(frozen=True, slots=True)
class NodeRecord:
    node_id: NodeID
    owner_principal: str
    status: NodeStatus
    keys: tuple[NodeKeyRecord, ...]
    registered_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if not self.owner_principal.strip():
            raise ValueError("owner_principal must not be empty")
        if not self.keys:
            raise ValueError("node requires at least one verification key")
        if len({key.key_id for key in self.keys}) != len(self.keys):
            raise ValueError("node key IDs must be unique")
        for key in self.keys:
            if NodeID.from_public_key(key.public_key) != self.node_id:
                raise ValueError("every node key must derive the same NodeID")

    def key(self, key_id: str) -> NodeKeyRecord | None:
        return next((key for key in self.keys if key.key_id == key_id), None)

    def may_operate(self) -> bool:
        return self.status is NodeStatus.ACTIVE
