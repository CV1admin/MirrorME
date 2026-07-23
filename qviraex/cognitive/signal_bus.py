from __future__ import annotations

import json
from copy import deepcopy
from datetime import UTC, datetime
from hashlib import sha256
from threading import RLock
from typing import Any
from uuid import uuid4

from qviraex.existence.schemas import CognitiveSignal, EpistemicClass


class SignalBusError(RuntimeError):
    pass


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


class CognitiveSignalBus:
    """In-memory append-only signal chain.

    This bus is a runtime integrity mechanism. It does not perform durable
    storage, network publication, or automatic memory promotion.
    """

    def __init__(self, *, node_id: str) -> None:
        if not node_id.strip():
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
        if not signal_type.strip():
            raise ValueError("signal_type must be non-empty")
        if not isinstance(payload, dict):
            raise TypeError("payload must be a dictionary")

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

    def verify_chain(self) -> bool:
        with self._lock:
            previous_hash: str | None = None
            for expected_sequence, signal in enumerate(self._signals, start=1):
                if signal.sequence != expected_sequence:
                    return False
                if signal.previous_hash != previous_hash:
                    return False
                body = {
                    "signal_id": signal.signal_id,
                    "signal_type": signal.signal_type,
                    "node_id": signal.node_id,
                    "sequence": signal.sequence,
                    "payload": signal.payload,
                    "epistemic_class": signal.epistemic_class.value,
                    "previous_hash": signal.previous_hash,
                    "created_at": signal.created_at,
                }
                try:
                    canonical = _canonical_json(body)
                except (TypeError, ValueError):
                    return False
                expected_hash = f"sha256:{sha256(canonical.encode('utf-8')).hexdigest()}"
                if signal.signal_hash != expected_hash:
                    return False
                previous_hash = signal.signal_hash
            return True

    def snapshot(self) -> tuple[CognitiveSignal, ...]:
        with self._lock:
            return tuple(_clone_signal(signal) for signal in self._signals)
