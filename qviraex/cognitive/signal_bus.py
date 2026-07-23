from __future__ import annotations

import json
from datetime import UTC, datetime
from hashlib import sha256
from threading import RLock
from typing import Any
from uuid import uuid4

from qviraex.existence.schemas import CognitiveSignal, EpistemicClass


class SignalBusError(RuntimeError):
    pass


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
        return self._signals[-1].signal_hash if self._signals else None

    @property
    def sequence(self) -> int:
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

        with self._lock:
            sequence = len(self._signals) + 1
            previous_hash = self.head_hash
            created_at = datetime.now(UTC).isoformat()
            signal_id = str(uuid4())
            body = {
                "signal_id": signal_id,
                "signal_type": signal_type,
                "node_id": self.node_id,
                "sequence": sequence,
                "payload": payload,
                "epistemic_class": epistemic_class.value,
                "previous_hash": previous_hash,
                "created_at": created_at,
            }
            canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
            signal_hash = f"sha256:{sha256(canonical.encode('utf-8')).hexdigest()}"
            signal = CognitiveSignal(
                signal_id=signal_id,
                signal_type=signal_type,
                node_id=self.node_id,
                sequence=sequence,
                payload=dict(payload),
                epistemic_class=epistemic_class,
                previous_hash=previous_hash,
                signal_hash=signal_hash,
                created_at=created_at,
            )
            self._signals.append(signal)
            return signal

    def verify_chain(self) -> bool:
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
            canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
            expected_hash = f"sha256:{sha256(canonical.encode('utf-8')).hexdigest()}"
            if signal.signal_hash != expected_hash:
                return False
            previous_hash = signal.signal_hash
        return True

    def snapshot(self) -> tuple[CognitiveSignal, ...]:
        return tuple(self._signals)
