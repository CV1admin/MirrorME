from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any
from uuid import uuid4

from qviraex.evolution import (
    EvolutionApproval,
    EvolutionEvaluation,
    EvolutionProposal,
    GovernedEvolutionEngine,
)
from qviraex.existence.schemas import AuthorizedSession, EpistemicClass, VerifiedIdentityContext
from qviraex.mkultra_v03 import MKultraRuntime, RuntimeIntegrityAnchor
from qviraex.thin_line import ClaimDraft, ClaimRecord, ClaimRegistry, seed_thin_line_registry

MKULTRA_V04_VERSION = "0.4.0"
MKULTRA_V04_CODENAME = "Governed Thin Line"


@dataclass(frozen=True)
class MKultraV04IntegrityAnchor:
    runtime_anchor: RuntimeIntegrityAnchor
    claim_head_hash: str | None
    claim_count: int
    proposal_head_hash: str | None
    proposal_count: int

    def __post_init__(self) -> None:
        if not isinstance(self.runtime_anchor, RuntimeIntegrityAnchor):
            raise TypeError("runtime_anchor must be a RuntimeIntegrityAnchor")
        for name in ("claim_count", "proposal_count"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        for name, count_name in (
            ("claim_head_hash", "claim_count"),
            ("proposal_head_hash", "proposal_count"),
        ):
            value = getattr(self, name)
            count = getattr(self, count_name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be a non-empty string or None")
            if (count == 0) != (value is None):
                raise ValueError(f"{name} and {count_name} are inconsistent")


@dataclass(frozen=True)
class MKultraV04Status:
    version: str
    codename: str
    node_id: str
    runtime: dict[str, Any]
    claims: dict[str, object]
    evolution: dict[str, object]
    integrity_valid: bool
    automatic_self_modification: bool
    external_actions: bool


class MKultraV04Runtime:
    """Governed v0.4 composition over the transactional v0.3 runtime.

    The runtime may register claims and produce reviewed evolution packets. It
    cannot apply patches, update model weights, change policies, mutate identity
    or authorize external actions.
    """

    def __init__(
        self,
        *,
        identity: VerifiedIdentityContext,
        session: AuthorizedSession,
        claim_registry: ClaimRegistry | None = None,
        review_threshold: float = 0.75,
        short_memory_capacity: int = 128,
        checkpoint_interval: int = 8,
    ) -> None:
        self.base_runtime = MKultraRuntime(
            identity=identity,
            session=session,
            short_memory_capacity=short_memory_capacity,
            checkpoint_interval=checkpoint_interval,
        )
        self.claim_registry = claim_registry or seed_thin_line_registry()
        self.evolution = GovernedEvolutionEngine(
            claim_registry=self.claim_registry,
            review_threshold=review_threshold,
        )

    @property
    def identity(self) -> VerifiedIdentityContext:
        return self.base_runtime.identity

    @property
    def session(self) -> AuthorizedSession:
        return self.base_runtime.session

    def activate(self) -> None:
        self.base_runtime.activate()
        self.base_runtime.signal_bus.publish(
            signal_type="mirrorme.v04.governance.activated",
            payload={
                "version": MKULTRA_V04_VERSION,
                "codename": MKULTRA_V04_CODENAME,
                "claim_registry_head": self.claim_registry.head_hash,
                "automatic_self_modification": False,
                "external_actions": False,
            },
            epistemic_class=EpistemicClass.OBSERVATION,
        )

    def ingest(self, **kwargs: Any) -> object:
        return self.base_runtime.ingest(**kwargs)

    def checkpoint(self) -> object:
        return self.base_runtime.checkpoint()

    def register_claim(self, draft: ClaimDraft) -> ClaimRecord:
        record = self.claim_registry.register(draft)
        self.base_runtime.signal_bus.publish(
            signal_type="mirrorme.v04.claim.registered",
            payload={
                "claim_id": record.draft.claim_id,
                "layer": record.draft.layer.value,
                "status": record.draft.status.value,
                "record_hash": record.record_hash,
            },
            epistemic_class=EpistemicClass.OBSERVATION,
        )
        return record

    def propose_evolution(self, **kwargs: Any) -> EvolutionProposal:
        proposal = self.evolution.propose(**kwargs)
        self.base_runtime.signal_bus.publish(
            signal_type="mirrorme.v04.evolution.proposed",
            payload={
                "proposal_id": proposal.proposal_id,
                "proposal_hash": proposal.proposal_hash,
                "execution_authorized": False,
            },
            epistemic_class=EpistemicClass.HYPOTHESIS,
        )
        return proposal

    def evaluate_evolution(self, proposal_id: str, **kwargs: Any) -> EvolutionEvaluation:
        evaluation = self.evolution.evaluate(proposal_id, **kwargs)
        self.base_runtime.signal_bus.publish(
            signal_type="mirrorme.v04.evolution.evaluated",
            payload={
                "proposal_id": proposal_id,
                "evaluation_hash": evaluation.evaluation_hash,
                "decision": evaluation.decision.value,
                "human_review_required": True,
            },
            epistemic_class=EpistemicClass.INFERENCE,
        )
        return evaluation

    def approve_evolution(self, proposal_id: str, **kwargs: Any) -> EvolutionApproval:
        approval = self.evolution.approve(proposal_id, **kwargs)
        self.base_runtime.signal_bus.publish(
            signal_type="mirrorme.v04.evolution.approved_for_export",
            payload={
                "proposal_id": proposal_id,
                "approval_hash": approval.approval_hash,
                "execution_authorized": False,
                "allowed_next_step": "human-reviewed branch or pull request",
            },
            epistemic_class=EpistemicClass.OBSERVATION,
        )
        return approval

    def export_change_packet(self, proposal_id: str) -> dict[str, object]:
        packet = self.evolution.export_change_packet(proposal_id)
        self.base_runtime.signal_bus.publish(
            signal_type="mirrorme.v04.evolution.packet_exported",
            payload={
                "proposal_id": proposal_id,
                "packet_hash": packet["packet_hash"],
                "execution_authorized": False,
            },
            epistemic_class=EpistemicClass.OBSERVATION,
        )
        return packet

    def integrity_anchor(self) -> MKultraV04IntegrityAnchor:
        proposals = self.evolution.snapshot()
        return MKultraV04IntegrityAnchor(
            runtime_anchor=self.base_runtime.integrity_anchor(),
            claim_head_hash=self.claim_registry.head_hash,
            claim_count=self.claim_registry.count,
            proposal_head_hash=(proposals[-1].proposal_hash if proposals else None),
            proposal_count=len(proposals),
        )

    def verify_integrity(self, anchor: MKultraV04IntegrityAnchor | None = None) -> bool:
        if anchor is not None and not isinstance(anchor, MKultraV04IntegrityAnchor):
            raise TypeError("anchor must be an MKultraV04IntegrityAnchor or None")
        runtime_ok = self.base_runtime.verify_integrity(
            anchor.runtime_anchor if anchor else None
        )
        claims_ok = ClaimRegistry.verify_snapshot(
            self.claim_registry.snapshot(),
            expected_head_hash=(anchor.claim_head_hash if anchor else None),
            expected_count=(anchor.claim_count if anchor else None),
        )
        proposals = self.evolution.snapshot()
        proposal_ok = self.evolution.verify_proposal_chain()
        if anchor is not None:
            actual_head = proposals[-1].proposal_hash if proposals else None
            proposal_ok = (
                proposal_ok
                and len(proposals) == anchor.proposal_count
                and actual_head == anchor.proposal_head_hash
            )
        return runtime_ok and claims_ok and proposal_ok

    def status(self) -> MKultraV04Status:
        base_state = asdict(self.base_runtime.state())
        return MKultraV04Status(
            version=MKULTRA_V04_VERSION,
            codename=MKULTRA_V04_CODENAME,
            node_id=self.identity.node_id,
            runtime=base_state,
            claims=self.claim_registry.summary(),
            evolution=self.evolution.status(),
            integrity_valid=self.verify_integrity(),
            automatic_self_modification=False,
            external_actions=False,
        )


def create_local_v04_session(
    *,
    node_id: str,
    operator: str = "VIREAX",
    persistence_authorized: bool = False,
) -> AuthorizedSession:
    if type(persistence_authorized) is not bool:
        raise TypeError("persistence_authorized must be a boolean")
    return AuthorizedSession(
        session_id=f"MK04-{uuid4()}",
        runtime_id=str(uuid4()),
        operator=operator,
        node_id=node_id,
        persistence_authorized=persistence_authorized,
        external_actions_authorized=False,
    )
