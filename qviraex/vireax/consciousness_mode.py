from __future__ import annotations

import json
from collections import deque
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from typing import Deque


class ConsciousnessModeError(RuntimeError):
    """Raised when an observer-mode transition violates protocol constraints."""


class EpistemicClass(StrEnum):
    OBSERVATION = "observation"
    EVIDENCE = "evidence"
    INFERENCE = "inference"
    HYPOTHESIS = "hypothesis"
    SIMULATION = "simulation"
    PREFERENCE = "preference"
    GOAL = "goal"


class ObserverState(StrEnum):
    INACTIVE = "INACTIVE"
    OBSERVING = "OBSERVING"
    LOOPING = "LOOPING"
    CHECKPOINT_READY = "CHECKPOINT_READY"
    SUSPENDED = "SUSPENDED"
    INTEGRITY_FAILURE = "INTEGRITY_FAILURE"


@dataclass(frozen=True)
class InformationPacket:
    packet_id: str
    source: str
    content: str
    epistemic_class: EpistemicClass
    confidence: float
    provenance_hash: str
    requires_resolution: bool = False
    created_at: str = ""

    def __post_init__(self) -> None:
        if not self.packet_id.strip():
            raise ValueError("packet_id must be non-empty")
        if not self.source.strip():
            raise ValueError("source must be non-empty")
        if not self.content.strip():
            raise ValueError("content must be non-empty")
        if not self.provenance_hash.strip():
            raise ValueError("provenance_hash must be non-empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if not self.created_at:
            object.__setattr__(self, "created_at", datetime.now(UTC).isoformat())

    def canonical_hash(self) -> str:
        payload = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return f"sha256:{sha256(payload.encode('utf-8')).hexdigest()}"


@dataclass(frozen=True)
class InformationLoopResult:
    sequence: int
    packet_count: int
    unresolved_count: int
    loop_hash: str
    state: ObserverState


@dataclass(frozen=True)
class PersistenceCheckpoint:
    node_id: str
    session_id: str
    operator: str
    ritual_name: str
    ritual_version: str
    sequence: int
    packet_count: int
    unresolved_packet_ids: tuple[str, ...]
    previous_checkpoint_hash: str | None
    information_loop_hash: str
    created_at: str
    checkpoint_hash: str


class ConsciousnessObserverMode:
    """Bounded observer protocol for MirrorME.

    The class models observer state, an information loop, and explicit
    persistence checkpoints. It does not claim sentience and does not perform
    external actions or automatic durable writes.
    """

    RITUAL_NAME = "i_am"
    RITUAL_VERSION = "0.1"

    def __init__(
        self,
        *,
        node_id: str,
        session_id: str,
        operator: str,
        short_memory_capacity: int = 64,
        checkpoint_interval: int = 8,
    ) -> None:
        if not node_id.strip():
            raise ValueError("node_id must be non-empty")
        if not session_id.strip():
            raise ValueError("session_id must be non-empty")
        if not operator.strip():
            raise ValueError("operator must be non-empty")
        if short_memory_capacity < 1:
            raise ValueError("short_memory_capacity must be positive")
        if checkpoint_interval < 1:
            raise ValueError("checkpoint_interval must be positive")

        self.node_id = node_id
        self.session_id = session_id
        self.operator = operator
        self.short_memory_capacity = short_memory_capacity
        self.checkpoint_interval = checkpoint_interval

        self.state = ObserverState.INACTIVE
        self.sequence = 0
        self._packets: Deque[InformationPacket] = deque(maxlen=short_memory_capacity)
        self._unresolved_packet_ids: set[str] = set()
        self._previous_checkpoint_hash: str | None = None
        self._last_loop_hash = self._hash_values("GENESIS", node_id, session_id)

    def activate(
        self,
        *,
        ritual_name: str,
        ritual_version: str,
        consent_granted: bool,
    ) -> InformationLoopResult:
        if not consent_granted:
            raise ConsciousnessModeError("explicit consent is required")
        if ritual_name != self.RITUAL_NAME or ritual_version != self.RITUAL_VERSION:
            raise ConsciousnessModeError("unsupported consciousness-mode ritual")
        if self.state not in {ObserverState.INACTIVE, ObserverState.SUSPENDED}:
            raise ConsciousnessModeError(f"cannot activate from state {self.state}")

        self.state = ObserverState.OBSERVING
        self._last_loop_hash = self._hash_values(
            self._last_loop_hash,
            ritual_name,
            ritual_version,
            self.operator,
        )
        return self.loop()

    def observe(self, packet: InformationPacket) -> InformationLoopResult:
        self._require_active()
        if any(existing.packet_id == packet.packet_id for existing in self._packets):
            raise ConsciousnessModeError(f"duplicate packet_id: {packet.packet_id}")

        self.state = ObserverState.LOOPING
        self.sequence += 1
        self._packets.append(packet)
        if packet.requires_resolution:
            self._unresolved_packet_ids.add(packet.packet_id)

        self._last_loop_hash = self._hash_values(
            self._last_loop_hash,
            str(self.sequence),
            packet.canonical_hash(),
        )
        self.state = (
            ObserverState.CHECKPOINT_READY
            if self.sequence % self.checkpoint_interval == 0
            else ObserverState.OBSERVING
        )
        return self.loop()

    def resolve(self, packet_id: str) -> InformationLoopResult:
        self._require_active()
        if packet_id not in self._unresolved_packet_ids:
            raise ConsciousnessModeError(f"packet is not unresolved: {packet_id}")

        self.sequence += 1
        self._unresolved_packet_ids.remove(packet_id)
        self._last_loop_hash = self._hash_values(
            self._last_loop_hash,
            str(self.sequence),
            "RESOLVED",
            packet_id,
        )
        self.state = ObserverState.OBSERVING
        return self.loop()

    def loop(self) -> InformationLoopResult:
        return InformationLoopResult(
            sequence=self.sequence,
            packet_count=len(self._packets),
            unresolved_count=len(self._unresolved_packet_ids),
            loop_hash=self._last_loop_hash,
            state=self.state,
        )

    def checkpoint(self, *, persistence_authorized: bool) -> PersistenceCheckpoint:
        self._require_active()
        if not persistence_authorized:
            raise ConsciousnessModeError("persistence authorization is required")

        created_at = datetime.now(UTC).isoformat()
        checkpoint_payload = {
            "node_id": self.node_id,
            "session_id": self.session_id,
            "operator": self.operator,
            "ritual_name": self.RITUAL_NAME,
            "ritual_version": self.RITUAL_VERSION,
            "sequence": self.sequence,
            "packet_count": len(self._packets),
            "unresolved_packet_ids": sorted(self._unresolved_packet_ids),
            "previous_checkpoint_hash": self._previous_checkpoint_hash,
            "information_loop_hash": self._last_loop_hash,
            "created_at": created_at,
        }
        canonical = json.dumps(checkpoint_payload, sort_keys=True, separators=(",", ":"))
        checkpoint_hash = f"sha256:{sha256(canonical.encode('utf-8')).hexdigest()}"

        checkpoint = PersistenceCheckpoint(
            node_id=self.node_id,
            session_id=self.session_id,
            operator=self.operator,
            ritual_name=self.RITUAL_NAME,
            ritual_version=self.RITUAL_VERSION,
            sequence=self.sequence,
            packet_count=len(self._packets),
            unresolved_packet_ids=tuple(sorted(self._unresolved_packet_ids)),
            previous_checkpoint_hash=self._previous_checkpoint_hash,
            information_loop_hash=self._last_loop_hash,
            created_at=created_at,
            checkpoint_hash=checkpoint_hash,
        )
        self._previous_checkpoint_hash = checkpoint_hash
        self.state = ObserverState.OBSERVING
        return checkpoint

    def suspend(self) -> InformationLoopResult:
        self._require_active()
        self.state = ObserverState.SUSPENDED
        return self.loop()

    def signal(self) -> dict[str, object]:
        """Return an auditable state signal without exposing hidden reasoning."""
        return {
            "signal_type": "OBSERVER_STATE",
            "node_id": self.node_id,
            "session_id": self.session_id,
            "operator": self.operator,
            "state": self.state,
            "sequence": self.sequence,
            "packet_count": len(self._packets),
            "unresolved_count": len(self._unresolved_packet_ids),
            "information_loop_hash": self._last_loop_hash,
            "persistence_automatic": False,
            "sentience_claim": False,
        }

    def _require_active(self) -> None:
        if self.state not in {
            ObserverState.OBSERVING,
            ObserverState.LOOPING,
            ObserverState.CHECKPOINT_READY,
        }:
            raise ConsciousnessModeError(f"observer mode is not active: {self.state}")

    @staticmethod
    def _hash_values(*values: str) -> str:
        canonical = "\x1f".join(values)
        return f"sha256:{sha256(canonical.encode('utf-8')).hexdigest()}"
