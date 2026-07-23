from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

from .models import ProcessEvent, ProcessRecord, ProcessState


_ALLOWED_TRANSITIONS: dict[ProcessState, set[ProcessState]] = {
    ProcessState.RECEIVED: {
        ProcessState.AUTHENTICATED,
        ProcessState.REJECTED,
        ProcessState.FAILED_RETRYABLE,
        ProcessState.FAILED_TERMINAL,
    },
    ProcessState.AUTHENTICATED: {
        ProcessState.NODE_VERIFIED,
        ProcessState.REJECTED,
        ProcessState.FAILED_RETRYABLE,
        ProcessState.FAILED_TERMINAL,
    },
    ProcessState.NODE_VERIFIED: {
        ProcessState.AUTHORIZED,
        ProcessState.REJECTED,
        ProcessState.QUARANTINED,
        ProcessState.FAILED_RETRYABLE,
        ProcessState.FAILED_TERMINAL,
    },
    ProcessState.AUTHORIZED: {
        ProcessState.VALIDATED,
        ProcessState.REJECTED,
        ProcessState.QUARANTINED,
        ProcessState.FAILED_RETRYABLE,
        ProcessState.FAILED_TERMINAL,
    },
    ProcessState.VALIDATED: {
        ProcessState.PREPARED,
        ProcessState.REJECTED,
        ProcessState.QUARANTINED,
        ProcessState.FAILED_RETRYABLE,
        ProcessState.FAILED_TERMINAL,
    },
    ProcessState.PREPARED: {
        ProcessState.COMMITTED,
        ProcessState.FAILED_RETRYABLE,
        ProcessState.FAILED_TERMINAL,
    },
    ProcessState.COMMITTED: {
        ProcessState.AUDITED,
        ProcessState.FAILED_RETRYABLE,
        ProcessState.FAILED_TERMINAL,
    },
    ProcessState.AUDITED: {
        ProcessState.COMPLETED,
        ProcessState.FAILED_RETRYABLE,
        ProcessState.FAILED_TERMINAL,
    },
    ProcessState.FAILED_RETRYABLE: {
        ProcessState.AUTHENTICATED,
        ProcessState.NODE_VERIFIED,
        ProcessState.AUTHORIZED,
        ProcessState.VALIDATED,
        ProcessState.PREPARED,
        ProcessState.COMMITTED,
        ProcessState.AUDITED,
        ProcessState.FAILED_TERMINAL,
    },
}


def transition(
    record: ProcessRecord,
    target: ProcessState,
    *,
    code: str,
    details: dict[str, str] | None = None,
) -> ProcessRecord:
    if record.terminal:
        raise ValueError("terminal process cannot transition")
    allowed = _ALLOWED_TRANSITIONS.get(record.state, set())
    if target not in allowed:
        raise ValueError(f"invalid process transition: {record.state} -> {target}")
    if not code.strip():
        raise ValueError("transition code must not be empty")

    now = datetime.now(UTC)
    event = ProcessEvent(
        previous_state=record.state,
        state=target,
        code=code,
        occurred_at=now,
        details=dict(details or {}),
    )
    attempt = record.attempt + 1 if target is ProcessState.FAILED_RETRYABLE else record.attempt
    return replace(
        record,
        state=target,
        updated_at=now,
        attempt=attempt,
        events=record.events + (event,),
    )
