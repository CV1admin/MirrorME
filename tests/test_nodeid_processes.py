from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from oiiids.identity import (
    KeyStatus,
    NodeID,
    NodeKeyRecord,
    NodeRecord,
    NodeStatus,
    OperationContext,
    SignedOperationProof,
)
from oiiids.processes import ProcessRecord, ProcessState, ProcessType, transition


PUBLIC_KEY = bytes(range(32))


def test_node_id_is_deterministic_and_parsable() -> None:
    first = NodeID.from_public_key(PUBLIC_KEY)
    second = NodeID.from_public_key(PUBLIC_KEY)

    assert first == second
    assert NodeID.parse(str(first)) == first
    assert str(first).startswith("nodeid:cv1:")


def test_node_id_rejects_invalid_public_key_length() -> None:
    with pytest.raises(ValueError, match="32 bytes"):
        NodeID.from_public_key(b"short")


def test_node_record_requires_key_to_match_node_id() -> None:
    node_id = NodeID.from_public_key(PUBLIC_KEY)
    wrong_key = bytes(reversed(range(32)))
    now = datetime.now(UTC)

    with pytest.raises(ValueError, match="derive the same NodeID"):
        NodeRecord(
            node_id=node_id,
            owner_principal="member:marek",
            status=NodeStatus.ACTIVE,
            keys=(NodeKeyRecord("key-1", wrong_key),),
            registered_at=now,
            updated_at=now,
        )


def test_revoked_or_expired_key_is_not_usable() -> None:
    now = datetime.now(UTC)
    active = NodeKeyRecord("active", PUBLIC_KEY)
    expired = NodeKeyRecord("expired", PUBLIC_KEY, expires_at=now - timedelta(seconds=1))
    revoked = NodeKeyRecord(
        "revoked",
        PUBLIC_KEY,
        status=KeyStatus.REVOKED,
        revoked_at=now,
    )

    assert active.is_usable_at(now) is True
    assert expired.is_usable_at(now) is False
    assert revoked.is_usable_at(now) is False


def test_operation_context_binds_method_session_nonce_and_digest() -> None:
    node_id = NodeID.from_public_key(PUBLIC_KEY)
    operation_id = uuid4()
    first = OperationContext.create(
        operation_id=operation_id,
        principal="member:marek",
        node_id=node_id,
        key_id="key-1",
        method="resource.publish",
        gateway_session_id="session-a",
        nonce="nonce-a",
        resource_digest="sha256:abc",
    )
    replayed_for_other_method = replace(first, method="resource.withdraw")

    assert first.digest != replayed_for_other_method.digest


def test_signed_operation_proof_rejects_wrong_signature_length() -> None:
    context = OperationContext.create(
        operation_id=uuid4(),
        principal="member:marek",
        node_id=NodeID.from_public_key(PUBLIC_KEY),
        key_id="key-1",
        method="resource.publish",
        gateway_session_id="session-a",
        nonce="nonce-a",
    )

    with pytest.raises(ValueError, match="64 bytes"):
        SignedOperationProof(context=context, signature=b"invalid")


def test_process_happy_path_is_guarded_and_auditable() -> None:
    process = ProcessRecord.create(
        process_id=uuid4(),
        process_type=ProcessType.RESOURCE_PUBLISH,
        idempotency_key="publish-001",
        principal="member:marek",
        node_id=NodeID.from_public_key(PUBLIC_KEY),
    )

    for state in (
        ProcessState.AUTHENTICATED,
        ProcessState.NODE_VERIFIED,
        ProcessState.AUTHORIZED,
        ProcessState.VALIDATED,
        ProcessState.PREPARED,
        ProcessState.COMMITTED,
        ProcessState.AUDITED,
        ProcessState.COMPLETED,
    ):
        process = transition(process, state, code=state.value)

    assert process.terminal is True
    assert process.state is ProcessState.COMPLETED
    assert len(process.events) == 9


def test_process_rejects_skipped_state_and_terminal_transition() -> None:
    process = ProcessRecord.create(
        process_id=uuid4(),
        process_type=ProcessType.RESOURCE_READ,
        idempotency_key="read-001",
        principal="member:peer",
    )

    with pytest.raises(ValueError, match="invalid process transition"):
        transition(process, ProcessState.COMMITTED, code="skip")

    rejected = transition(process, ProcessState.REJECTED, code="authentication_failed")
    with pytest.raises(ValueError, match="terminal process"):
        transition(rejected, ProcessState.AUTHENTICATED, code="retry")


def test_retryable_failure_increments_attempt() -> None:
    process = ProcessRecord.create(
        process_id=uuid4(),
        process_type=ProcessType.RESOURCE_SYNC,
        idempotency_key="sync-001",
        principal="member:marek",
    )
    failed = transition(process, ProcessState.FAILED_RETRYABLE, code="temporary_store_error")

    assert failed.attempt == 1
    retried = transition(failed, ProcessState.AUTHENTICATED, code="retry")
    assert retried.attempt == 1
