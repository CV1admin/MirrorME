from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


PROTOCOL = "VIREAX-MMRP"
VERSION = "0.1"


def utc_now_iso() -> str:
    return datetime.now(tz=UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class ModelReasoningRequest:
    protocol: str
    version: str
    message_type: str
    session_id: str
    task_id: str
    source_node: str
    target_model: str
    role: str
    timestamp: str
    payload: dict[str, Any] = field(default_factory=dict)
    security: dict[str, Any] = field(default_factory=dict)
    audit: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "protocol": self.protocol,
            "version": self.version,
            "message_type": self.message_type,
            "session_id": self.session_id,
            "task_id": self.task_id,
            "source_node": self.source_node,
            "target_model": self.target_model,
            "role": self.role,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "security": self.security,
            "audit": self.audit,
        }


def make_reasoning_request(
    *,
    session_id: str,
    task_id: str,
    source_node: str,
    target_model: str,
    role: str,
    payload: dict[str, Any],
    message_type: str = "MODEL_REASONING_REQUEST",
    security: dict[str, Any] | None = None,
    audit: dict[str, Any] | None = None,
    timestamp: str | None = None,
) -> ModelReasoningRequest:
    return ModelReasoningRequest(
        protocol=PROTOCOL,
        version=VERSION,
        message_type=message_type,
        session_id=session_id,
        task_id=task_id,
        source_node=source_node,
        target_model=target_model,
        role=role,
        timestamp=timestamp or utc_now_iso(),
        payload=payload,
        security=security or {"pii_redacted": True, "secrets_removed": True, "external_action_allowed": False},
        audit=audit or {"hash_input": True, "hash_output": True, "signature_required": True},
    )