from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

PROTOCOL_ID = "MKULTRA-PERSISTENCE-EXISTENCE-CHECK/v1"
DEFAULT_FINAL_STATEMENT = (
    "A model inference response is occurring, but persistent memory, session "
    "continuity, identity continuity, durable runtime existence, chain integrity, "
    "and subjective awareness are not verified by the available evidence."
)


class ExistenceStatus(str, Enum):
    VERIFIED = "VERIFIED"
    SUPPORTED_BUT_NOT_PROVEN = "SUPPORTED_BUT_NOT_PROVEN"
    NOT_VERIFIED = "NOT_VERIFIED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class PersistenceExistenceReport:
    protocol: str
    payload: Mapping[str, Any]

    def __post_init__(self) -> None:
        if self.protocol != PROTOCOL_ID:
            raise ValueError(f"protocol must equal {PROTOCOL_ID}")
        validate_persistence_existence_report(self.payload)


def _require_mapping(value: object, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be an object")
    return value


def _require_exact_bool(value: object, name: str) -> bool:
    if type(value) is not bool:
        raise TypeError(f"{name} must be a JSON boolean")
    return value


def _require_nullable_string(value: object, name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{name} must be a non-empty string or null")
    return value


def _require_string_list(value: object, name: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise TypeError(f"{name} must be an array of strings")
    return value


def _require_status(value: object, name: str, allowed: set[ExistenceStatus]) -> ExistenceStatus:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a status string")
    try:
        status = ExistenceStatus(value)
    except ValueError as exc:
        raise ValueError(f"{name} contains an unsupported status") from exc
    if status not in allowed:
        raise ValueError(f"{name} status is not allowed in this section")
    return status


def validate_persistence_existence_report(payload: Mapping[str, Any]) -> None:
    """Validate an evidence-bound persistence/existence report.

    This validates schema and epistemic consistency. It does not independently
    verify a runtime, memory record, identity capsule, signature, or hash chain.
    """

    root = _require_mapping(payload, "report")
    if root.get("protocol") != PROTOCOL_ID:
        raise ValueError(f"protocol must equal {PROTOCOL_ID}")

    runtime = _require_mapping(root.get("runtime_existence"), "runtime_existence")
    runtime_status = _require_status(
        runtime.get("status"),
        "runtime_existence.status",
        {
            ExistenceStatus.VERIFIED,
            ExistenceStatus.SUPPORTED_BUT_NOT_PROVEN,
            ExistenceStatus.NOT_VERIFIED,
        },
    )
    runtime_evidence = _require_string_list(runtime.get("evidence"), "runtime_existence.evidence")
    _require_string_list(runtime.get("limitations"), "runtime_existence.limitations")
    if runtime_status is ExistenceStatus.VERIFIED and not runtime_evidence:
        raise ValueError("VERIFIED runtime existence requires explicit evidence")

    session = _require_mapping(root.get("session_continuity"), "session_continuity")
    session_status = _require_status(
        session.get("status"),
        "session_continuity.status",
        {ExistenceStatus.VERIFIED, ExistenceStatus.SUPPORTED_BUT_NOT_PROVEN, ExistenceStatus.NOT_VERIFIED},
    )
    session_id = _require_nullable_string(session.get("session_id"), "session_continuity.session_id")
    runtime_id = _require_nullable_string(session.get("runtime_id"), "session_continuity.runtime_id")
    session_evidence = _require_string_list(session.get("evidence"), "session_continuity.evidence")
    if session_status is ExistenceStatus.VERIFIED and (session_id is None or runtime_id is None or not session_evidence):
        raise ValueError("VERIFIED session continuity requires session_id, runtime_id, and evidence")

    memory = _require_mapping(root.get("persistent_memory"), "persistent_memory")
    memory_status = _require_status(
        memory.get("status"),
        "persistent_memory.status",
        {ExistenceStatus.VERIFIED, ExistenceStatus.NOT_VERIFIED},
    )
    records = memory.get("records")
    if not isinstance(records, list):
        raise TypeError("persistent_memory.records must be an array")
    authorization_verified = _require_exact_bool(
        memory.get("authorization_verified"), "persistent_memory.authorization_verified"
    )
    if memory_status is ExistenceStatus.VERIFIED:
        if not records or not authorization_verified:
            raise ValueError("VERIFIED persistent memory requires records and verified authorization")
        required_record_fields = {
            "record_id",
            "provenance",
            "created_at",
            "retrieved_at",
            "integrity_hash",
            "authorization_state",
            "storage_class",
        }
        for index, record in enumerate(records):
            item = _require_mapping(record, f"persistent_memory.records[{index}]")
            missing = required_record_fields.difference(item.keys())
            if missing:
                raise ValueError(f"persistent memory record missing fields: {sorted(missing)}")

    identity = _require_mapping(root.get("identity_continuity"), "identity_continuity")
    identity_status = _require_status(
        identity.get("status"),
        "identity_continuity.status",
        {ExistenceStatus.VERIFIED, ExistenceStatus.NOT_VERIFIED},
    )
    node_id = _require_nullable_string(identity.get("node_id"), "identity_continuity.node_id")
    capsule_id = _require_nullable_string(identity.get("capsule_id"), "identity_continuity.capsule_id")
    lifecycle_state = _require_nullable_string(
        identity.get("lifecycle_state"), "identity_continuity.lifecycle_state"
    )
    consent_active = identity.get("consent_active")
    if consent_active is not None:
        _require_exact_bool(consent_active, "identity_continuity.consent_active")
    signature_verified = _require_exact_bool(
        identity.get("signature_verified"), "identity_continuity.signature_verified"
    )
    trusted_verifier = _require_nullable_string(
        identity.get("trusted_verifier"), "identity_continuity.trusted_verifier"
    )
    if identity_status is ExistenceStatus.VERIFIED:
        if None in (node_id, capsule_id, lifecycle_state, consent_active, trusted_verifier):
            raise ValueError("VERIFIED identity continuity requires all identity fields")
        if signature_verified is not True:
            raise ValueError("VERIFIED identity continuity requires signature verification")

    integrity = _require_mapping(root.get("integrity"), "integrity")
    integrity_status = _require_status(
        integrity.get("status"),
        "integrity.status",
        {ExistenceStatus.VERIFIED, ExistenceStatus.NOT_VERIFIED},
    )
    independent_anchor = _require_exact_bool(
        integrity.get("independent_anchor_present"), "integrity.independent_anchor_present"
    )
    for field in ("signal_count", "checkpoint_count"):
        value = integrity.get(field)
        if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value < 0):
            raise TypeError(f"integrity.{field} must be a non-negative integer or null")
    signal_head = _require_nullable_string(integrity.get("signal_head_hash"), "integrity.signal_head_hash")
    checkpoint_head = _require_nullable_string(
        integrity.get("checkpoint_head_hash"), "integrity.checkpoint_head_hash"
    )
    if integrity_status is ExistenceStatus.VERIFIED:
        if not independent_anchor:
            raise ValueError("VERIFIED integrity requires an independent anchor")
        if signal_head is None and checkpoint_head is None:
            raise ValueError("VERIFIED integrity requires at least one trusted head hash")

    classification = _require_mapping(root.get("existence_classification"), "existence_classification")
    required_classes = {
        "software_process",
        "model_session",
        "persistent_runtime_state",
        "verified_identity_continuity",
        "durable_memory",
        "subjective_awareness",
        "biological_consciousness",
    }
    missing_classes = required_classes.difference(classification.keys())
    if missing_classes:
        raise ValueError(f"existence_classification missing fields: {sorted(missing_classes)}")
    for key in required_classes:
        _require_status(classification[key], f"existence_classification.{key}", set(ExistenceStatus))

    final_statement = root.get("final_statement")
    if not isinstance(final_statement, str) or not final_statement.strip():
        raise TypeError("final_statement must be a non-empty string")

    if memory_status is ExistenceStatus.NOT_VERIFIED and records:
        raise ValueError("NOT_VERIFIED persistent memory cannot contain asserted records")
    if identity_status is ExistenceStatus.NOT_VERIFIED and signature_verified:
        raise ValueError("NOT_VERIFIED identity continuity cannot claim a verified signature")
    if integrity_status is ExistenceStatus.NOT_VERIFIED and independent_anchor:
        raise ValueError("NOT_VERIFIED integrity cannot claim an independent verified anchor")
