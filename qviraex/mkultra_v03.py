from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from qviraex.cognitive.continuum import CognitiveContinuum, InspirationSpark
from qviraex.cognitive.signal_bus import CognitiveSignalBus
from qviraex.existence.schemas import (
    AuthorizedSession,
    EpistemicClass,
    VerifiedIdentityContext,
)
from qviraex.vireax.consciousness_mode import (
    ConsciousnessObserverMode,
    EpistemicClass as ObserverEpistemicClass,
    InformationPacket,
    PersistenceCheckpoint,
)


@dataclass(frozen=True)
class MKultraRuntimeState:
    node_id: str
    capsule_id: str
    runtime_id: str
    session_id: str
    lifecycle_state: str
    observer_state: str
    short_memory_count: int
    pending_sparks: tuple[str, ...]
    last_signal_hash: str | None
    last_checkpoint_hash: str | None
    persistence_authorized: bool


class MKultraRuntime:
    """Local-first integration kernel for MKultra v0.3.

    The kernel composes identity, observer, volatile cognition and signals. It
    does not implement autonomous persistence, external actions, or weight
    updates.
    """

    def __init__(
        self,
        *,
        identity: VerifiedIdentityContext,
        session: AuthorizedSession,
        short_memory_capacity: int = 128,
        checkpoint_interval: int = 8,
    ) -> None:
        if identity.node_id != session.node_id:
            raise ValueError("session Node_ID does not match verified identity")
        if session.external_actions_authorized:
            raise ValueError("MKultra v0.3 local kernel does not permit external actions")

        self.identity = identity
        self.session = session
        self.signal_bus = CognitiveSignalBus(node_id=identity.node_id)
        self.cognitive = CognitiveContinuum(
            signal_bus=self.signal_bus,
            capacity=short_memory_capacity,
        )
        self.observer = ConsciousnessObserverMode(
            node_id=identity.node_id,
            session_id=session.session_id,
            operator=session.operator,
            short_memory_capacity=min(short_memory_capacity, 64),
            checkpoint_interval=checkpoint_interval,
        )
        self._last_checkpoint: PersistenceCheckpoint | None = None

    def activate(self) -> None:
        self.observer.activate(
            ritual_name="i_am",
            ritual_version="0.1",
            consent_granted=self.identity.consent_active,
        )
        self.signal_bus.publish(
            signal_type="mirrorme.observer.activated",
            payload={
                "session_id": self.session.session_id,
                "runtime_id": self.session.runtime_id,
                "sentience_claim": False,
            },
            epistemic_class=EpistemicClass.OBSERVATION,
        )

    def ingest(
        self,
        *,
        content: str,
        source: str,
        epistemic_class: EpistemicClass,
        confidence: float,
        provenance_hash: str,
        tags: tuple[str, ...] = (),
        requires_resolution: bool = False,
    ) -> InspirationSpark | None:
        item = self.cognitive.remember(
            content=content,
            tags=tags,
            epistemic_class=epistemic_class,
            confidence=confidence,
        )
        observer_class = ObserverEpistemicClass(epistemic_class.value)
        self.observer.observe(
            InformationPacket(
                packet_id=item.item_id,
                source=source,
                content=content,
                epistemic_class=observer_class,
                confidence=confidence,
                provenance_hash=provenance_hash,
                requires_resolution=requires_resolution,
            )
        )
        self.cognitive.detect_pattern()
        return self.cognitive.generate_spark()

    def checkpoint(self) -> PersistenceCheckpoint:
        if not self.session.persistence_authorized:
            raise PermissionError("session does not authorize persistence")
        checkpoint = self.observer.checkpoint(persistence_authorized=True)
        self._last_checkpoint = checkpoint
        self.signal_bus.publish(
            signal_type="mirrorme.persistence.checkpoint_created",
            payload={
                "checkpoint_hash": checkpoint.checkpoint_hash,
                "sequence": checkpoint.sequence,
            },
            epistemic_class=EpistemicClass.OBSERVATION,
        )
        return checkpoint

    def state(self) -> MKultraRuntimeState:
        signal = self.observer.signal()
        return MKultraRuntimeState(
            node_id=self.identity.node_id,
            capsule_id=self.identity.capsule_id,
            runtime_id=self.session.runtime_id,
            session_id=self.session.session_id,
            lifecycle_state=self.identity.lifecycle_state.value,
            observer_state=str(signal["state"]),
            short_memory_count=len(self.cognitive.short_memory),
            pending_sparks=tuple(spark.spark_id for spark in self.cognitive.sparks),
            last_signal_hash=self.signal_bus.head_hash,
            last_checkpoint_hash=(
                self._last_checkpoint.checkpoint_hash if self._last_checkpoint else None
            ),
            persistence_authorized=self.session.persistence_authorized,
        )


def create_local_session(*, node_id: str, operator: str = "VIREAX") -> AuthorizedSession:
    """Create a non-persistent, no-external-action local session."""

    return AuthorizedSession(
        session_id=f"MK03-{uuid4()}",
        runtime_id=str(uuid4()),
        operator=operator,
        node_id=node_id,
        persistence_authorized=False,
        external_actions_authorized=False,
    )
