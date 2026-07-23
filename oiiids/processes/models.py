from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from oiiids.identity.node_id import NodeID


class ProcessType(StrEnum):
    NODE_REGISTER = "node_register"
    NODE_ACTIVATE = "node_activate"
    NODE_ROTATE_KEY = "node_rotate_key"
    NODE_SUSPEND = "node_suspend"
    NODE_REVOKE = "node_revoke"
    RESOURCE_PUBLISH = "resource_publish"
    RESOURCE_READ = "resource_read"
    RESOURCE_MIRROR = "resource_mirror"
    RESOURCE_SUPERSEDE = "resource_supersede"
    RESOURCE_WITHDRAW = "resource_withdraw"
    RESOURCE_SYNC = "resource_sync"
    RESOURCE_QUARANTINE = "resource_quarantine"
    CONFLICT_RESOLVE = "conflict_resolve"


class ProcessState(StrEnum):
    RECEIVED = "received"
    AUTHENTICATED = "authenticated"
    NODE_VERIFIED = "node_verified"
    AUTHORIZED = "authorized"
    VALIDATED = "validated"
    PREPARED = "prepared"
    COMMITTED = "committed"
    AUDITED = "audited"
    COMPLETED = "completed"
    REJECTED = "rejected"
    QUARANTINED = "quarantined"
    FAILED_RETRYABLE = "failed_retryable"
    FAILED_TERMINAL = "failed_terminal"


TERMINAL_STATES = {
    ProcessState.COMPLETED,
    ProcessState.REJECTED,
    ProcessState.QUARANTINED,
    ProcessState.FAILED_TERMINAL,
}


@dataclass(frozen=True, slots=True)
class ProcessEvent:
    previous_state: ProcessState | None
    state: ProcessState
    code: str
    occurred_at: datetime
    details: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ProcessRecord:
    process_id: UUID
    process_type: ProcessType
    idempotency_key: str
    principal: str
    node_id: NodeID | None
    state: ProcessState
    created_at: datetime
    updated_at: datetime
    resource_digest: str | None = None
    attempt: int = 0
    payload: dict[str, Any] = field(default_factory=dict)
    events: tuple[ProcessEvent, ...] = ()

    def __post_init__(self) -> None:
        if not self.idempotency_key.strip():
            raise ValueError("idempotency_key must not be empty")
        if not self.principal.strip():
            raise ValueError("principal must not be empty")
        if self.attempt < 0:
            raise ValueError("attempt must not be negative")
        if self.created_at.tzinfo is None or self.updated_at.tzinfo is None:
            raise ValueError("process timestamps must be timezone-aware")

    @classmethod
    def create(
        cls,
        *,
        process_id: UUID,
        process_type: ProcessType,
        idempotency_key: str,
        principal: str,
        node_id: NodeID | None = None,
        resource_digest: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> "ProcessRecord":
        now = datetime.now(UTC)
        initial = ProcessEvent(None, ProcessState.RECEIVED, "received", now)
        return cls(
            process_id=process_id,
            process_type=process_type,
            idempotency_key=idempotency_key,
            principal=principal,
            node_id=node_id,
            state=ProcessState.RECEIVED,
            created_at=now,
            updated_at=now,
            resource_digest=resource_digest,
            payload=dict(payload or {}),
            events=(initial,),
        )

    @property
    def terminal(self) -> bool:
        return self.state in TERMINAL_STATES
