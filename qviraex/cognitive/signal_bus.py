from __future__ import annotations

import json
from copy import deepcopy
from datetime import UTC, datetime
from hashlib import sha256
from threading import RLock
from typing import Any, Iterable
from uuid import uuid4

from qviraex.existence.schemas import CognitiveSignal, EpistemicClass


class SignalBusError(RuntimeError):
    pass


SignalBusSnapshot = tuple[CognitiveSignal, ...]


def _canonical_json(data: dict[str, Any]) -> str:
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _clone_signal(signal: CognitiveSignal) -> CognitiveSignal:
    """Return a detached signal so callers cannot mutate the internal chain."""

    return CognitiveSignal(
        signal_id=signal.signal_id,
        signal_type=signal.signal_type,
        node_id=signal.node_id,
        sequence=signal.sequence,
        payload=deepcopy(signal.payload),
        epistemic_class=signal.epistemic_class,
        previous_hash=signal.previous_hash,
        signal_hash=signal.signal_hash,
        created_at=signal.created_at,
    )


def _signal_body(signal: CognitiveSignal) -> dict[str, Any]:
    return {
        "signal_id": signal.signal_id,
        "signal_type": signal.signal_type,
        "node_id": signal.node_id,
        "sequence": signal.sequence,
        "payload": signal.payload,
        "epistemic_class": signal.epistemic_class.value,
        "previous_hash": signal.previous_hash,
        "created_at": signal.created_at,
    }


class CognitiveSignalBus:
    """In-memory append-only signal chain.

    This bus is a runtime integrity mechanism. It does not perform durable
    storage, network publication, or automatic memory promotion.
    """

    def __init__(self, *, node_id: str) -> None:
        if not isinstance(node_id, str) or not node_id.strip():
            raise ValueError("node_id must be non-empty")
        self.node_id = node_id
        self._signals: list[CognitiveSignal] = []
        self._lock = RLock()

    @property
    def head_hash(self) -> str | None:
        with self._lock:
            return self._signals[-1].signal_hash if self._signals else None

    @property
    def sequence(self) -> int:
        with self._lock:
            return len(self._signals)

    def publish(
        self,
        *,
        signal_type: str,
        payload: dict[str, Any],
        epistemic_class: EpistemicClass,
    ) -> CognitiveSignal:
        if not isinstance(signal_type, str) or not signal_type.strip():
            raise ValueError("signal_type must be non-empty")
        if not isinstance(payload, dict):
            raise TypeError("payload must be a dictionary")
        if not isinstance(epistemic_class, EpistemicClass):
            raise TypeError("epistemic_class must be an EpistemicClass")

        with self._lock:
            sequence = len(self._signals) + 1
            previous_hash = self._signals[-1].signal_hash if self._signals else None
            created_at = datetime.now(UTC).isoformat()
            signal_id = str(uuid4())
            stored_payload = deepcopy(payload)
            body = {
                "signal_id": signal_id,
                "signal_type": signal_type,
                "node_id": self.node_id,
                "sequence": sequence,
                "payload": stored_payload,
                "epistemic_class": epistemic_class.value,
                "previous_hash": previous_hash,
                "created_at": created_at,
            }
            try:
                canonical = _canonical_json(body)
            except (TypeError, ValueError) as exc:
                raise SignalBusError("signal payload must be finite JSON data") from exc

            signal_hash = f"sha256:{sha256(canonical.encode('utf-8')).hexdigest()}"
            signal = CognitiveSignal(
                signal_id=signal_id,
                signal_type=signal_type,
                node_id=self.node_id,
                sequence=sequence,
                payload=stored_payload,
                epistemic_class=epistemic_class,
                previous_hash=previous_hash,
                signal_hash=signal_hash,
                created_at=created_at,
            )
            self._signals.append(signal)
            return _clone_signal(signal)

    @staticmethod
    def verify_snapshot(
        signals: Iterable[CognitiveSignal],
        *,
        expected_node_id: str | None = None,
        expected_head_hash: str | None = None,
        expected_length: int | None = None,
    ) -> bool:
        """Validate a detached chain, optionally against trusted anchors.

        Hash linkage alone detects mutation but not a consistently re-hashed
        replacement or truncation. ``expected_head_hash`` and ``expected_length``
        provide the external anchors needed to detect those cases.
        """

        if expected_length is not None:
            if (
                isinstance(expected_length, bool)
                or not isinstance(expected_length, int)
                or expected_length < 0
            ):
                raise ValueError("expected_length must be a non-negative integer")
        if expected_node_id is not None and (
            not isinstance(expected_node_id, str) or not expected_node_id.strip()
        ):
            raise ValueError("expected_node_id must be a non-empty string")
        if expected_head_hash is not None and (
            not isinstance(expected_head_hash, str) or not expected_head_hash.strip()
        ):
            raise ValueError("expected_head_hash must be a non-empty string")

        materialized = tuple(signals)
        if expected_length is not None and len(materialized) != expected_length:
            return False

        previous_hash: str | None = None
        for expected_sequence, signal in enumerate(materialized, start=1):
            if not isinstance(signal, CognitiveSignal):
                return False
            if expected_node_id is not None and signal.node_id != expected_node_id:
                return False
            if signal.sequence != expected_sequence:
                return False
            if signal.previous_hash != previous_hash:
                return False
            try:
                canonical = _canonical_json(_signal_body(signal))
            except (TypeError, ValueError):
                return False
            expected_hash = f"sha256:{sha256(canonical.encode('utf-8')).hexdigest()}"
            if signal.signal_hash != expected_hash:
                return False
            previous_hash = signal.signal_hash

        actual_head = materialized[-1].signal_hash if materialized else None
        if expected_head_hash is not None and actual_head != expected_head_hash:
            return False
        return True

    def verify_chain(
        self,
        *,
        expected_head_hash: str | None = None,
        expected_length: int | None = None,
    ) -> bool:
        with self._lock:
            return self.verify_snapshot(
                tuple(self._signals),
                expected_node_id=self.node_id,
                expected_head_hash=expected_head_hash,
                expected_length=expected_length,
            )

    def snapshot(self) -> SignalBusSnapshot:
        with self._lock:
            return tuple(_clone_signal(signal) for signal in self._signals)

    def _capture_state(self) -> SignalBusSnapshot:
        """Capture an internal rollback point for a higher-level transaction."""

        return self.snapshot()

    def _restore_state(self, snapshot: SignalBusSnapshot) -> None:
        """Restore a previously captured valid prefix after transaction failure."""

        with self._lock:
            if not self.verify_snapshot(snapshot, expected_node_id=self.node_id):
                raise SignalBusError("cannot restore an invalid signal snapshot")
            self._signals = [_clone_signal(signal) for signal in snapshot]
