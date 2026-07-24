from __future__ import annotations

import unittest
from dataclasses import replace

from local_bridge.v04_service import MKultraV04Service
from qviraex.evolution import GovernedEvolutionEngine, ProposalState
from qviraex.existence.schemas import (
    AuthorizedSession,
    LifecycleState,
    VerifiedIdentityContext,
)
from qviraex.mkultra_v04 import MKultraV04Runtime
from qviraex.thin_line import ClaimLayer, ClaimRegistry, seed_thin_line_registry


SCORES = {
    "evidence": 0.8,
    "testability": 0.9,
    "reversibility": 0.9,
    "safety": 0.95,
    "integrity": 0.9,
}


def proposal_kwargs(evidence_claim_ids: tuple[str, ...]) -> dict[str, object]:
    return {
        "objective": "Add a deterministic diagnostics panel",
        "target_components": ("ui", "local_bridge"),
        "evidence_claim_ids": evidence_claim_ids,
        "predicted_benefit": "Expose inspectable runtime state",
        "risks": ("stale status data",),
        "test_plan": ("run unit tests", "run TypeScript checks"),
        "rollback_plan": ("revert the feature branch",),
        "requested_changes": ("add read-only status endpoint",),
    }


def make_identity() -> VerifiedIdentityContext:
    return VerifiedIdentityContext(
        node_id="did:cv1:mkultra-v04-test",
        capsule_id="sha256:" + "a" * 64,
        member_id="CV1-MEMBER-V04",
        genesis_hash="sha256:" + "b" * 64,
        key_fingerprint="sha256:" + "c" * 64,
        lifecycle_state=LifecycleState.ACTIVE,
        consent_active=True,
    )


def make_session(identity: VerifiedIdentityContext) -> AuthorizedSession:
    return AuthorizedSession(
        session_id="MK04-TEST",
        runtime_id="RUNTIME-V04-TEST",
        operator="VIREAX",
        node_id=identity.node_id,
        persistence_authorized=False,
        external_actions_authorized=False,
    )


class ThinLineClaimRegistryTests(unittest.TestCase):
    def test_seed_registry_is_hash_linked_and_epistemically_separated(self) -> None:
        registry = seed_thin_line_registry()
        self.assertEqual(registry.count, 5)
        self.assertTrue(registry.verify())
        layers = {record.draft.layer for record in registry.snapshot()}
        self.assertIn(ClaimLayer.MYTHOLOGY_STORY, layers)
        self.assertIn(ClaimLayer.PHYSICAL_HYPOTHESIS, layers)
        self.assertIn(ClaimLayer.MATHEMATICAL_DEFINITION, layers)
        self.assertIn(ClaimLayer.COMPUTATIONAL_ANALOGY, layers)
        self.assertIn(ClaimLayer.COGNITIVE_HYPOTHESIS, layers)

    def test_registry_detects_detached_record_tampering(self) -> None:
        registry = seed_thin_line_registry()
        records = registry.snapshot()
        tampered_draft = replace(records[1].draft, statement="tampered")
        tampered = replace(records[1], draft=tampered_draft)
        snapshot = (records[0], tampered, *records[2:])
        self.assertFalse(
            ClaimRegistry.verify_snapshot(
                snapshot,
                expected_head_hash=registry.head_hash,
                expected_count=registry.count,
            )
        )


class GovernedEvolutionTests(unittest.TestCase):
    def test_mythology_only_evidence_cannot_pass_engineering_review(self) -> None:
        registry = seed_thin_line_registry()
        engine = GovernedEvolutionEngine(claim_registry=registry)
        proposal = engine.propose(
            **proposal_kwargs(("TL-HYPER-SYMMETRY-001",)),
            proposal_id="MK04-EVO-MYTH",
            created_at="2026-07-23T12:40:00+00:00",
        )
        evaluation = engine.evaluate(
            proposal.proposal_id,
            scores=SCORES,
            reasons=("high implementation quality",),
            evaluated_at="2026-07-23T12:41:00+00:00",
        )
        self.assertEqual(evaluation.decision, ProposalState.REJECTED)
        self.assertIn("mythology-only", " ".join(evaluation.reasons))

    def test_review_and_approval_never_authorize_execution(self) -> None:
        registry = seed_thin_line_registry()
        engine = GovernedEvolutionEngine(claim_registry=registry)
        proposal = engine.propose(
            **proposal_kwargs(("TL-MIRROR-ENGINE-SCAFFOLD-001",)),
            proposal_id="MK04-EVO-REVIEW",
            created_at="2026-07-23T12:42:00+00:00",
        )
        evaluation = engine.evaluate(
            proposal.proposal_id,
            scores=SCORES,
            reasons=("tests and rollback are explicit",),
            evaluated_at="2026-07-23T12:43:00+00:00",
        )
        self.assertEqual(evaluation.decision, ProposalState.REVIEW_REQUIRED)

        with self.assertRaisesRegex(TypeError, "human_approved"):
            engine.approve(
                proposal.proposal_id,
                reviewer="VIREAX",
                human_approved=1,  # type: ignore[arg-type]
            )

        approval = engine.approve(
            proposal.proposal_id,
            reviewer="VIREAX",
            human_approved=True,
            approved_at="2026-07-23T12:44:00+00:00",
        )
        self.assertFalse(approval.execution_authorized)
        packet = engine.export_change_packet(proposal.proposal_id)
        self.assertFalse(packet["execution_authorized"])
        self.assertTrue(packet["operator_action_required"])
        self.assertEqual(packet["allowed_next_step"], "human-reviewed branch or pull request")

    def test_proposal_chain_detects_tampering(self) -> None:
        registry = seed_thin_line_registry()
        engine = GovernedEvolutionEngine(claim_registry=registry)
        engine.propose(
            **proposal_kwargs(("TL-MIRROR-ENGINE-SCAFFOLD-001",)),
            proposal_id="MK04-EVO-CHAIN",
            created_at="2026-07-23T12:45:00+00:00",
        )
        self.assertTrue(engine.verify_proposal_chain())
        engine._proposals[0] = replace(engine._proposals[0], objective="tampered")
        self.assertFalse(engine.verify_proposal_chain())


class MKultraV04RuntimeTests(unittest.TestCase):
    def test_runtime_composes_v03_integrity_claims_and_evolution(self) -> None:
        identity = make_identity()
        runtime = MKultraV04Runtime(identity=identity, session=make_session(identity))
        runtime.activate()
        initial_anchor = runtime.integrity_anchor()
        status = runtime.status()
        self.assertEqual(status.version, "0.4.0")
        self.assertEqual(status.claims["count"], 5)
        self.assertTrue(status.integrity_valid)
        self.assertFalse(status.automatic_self_modification)

        proposal = runtime.propose_evolution(
            **proposal_kwargs(("TL-MIRROR-ENGINE-SCAFFOLD-001",)),
            proposal_id="MK04-EVO-RUNTIME",
            created_at="2026-07-23T12:46:00+00:00",
        )
        self.assertFalse(runtime.verify_integrity(initial_anchor))
        current_anchor = runtime.integrity_anchor()
        self.assertTrue(runtime.verify_integrity(current_anchor))

        runtime.evaluate_evolution(
            proposal.proposal_id,
            scores=SCORES,
            reasons=("bounded proposal",),
            evaluated_at="2026-07-23T12:47:00+00:00",
        )
        approval = runtime.approve_evolution(
            proposal.proposal_id,
            reviewer="VIREAX",
            human_approved=True,
            approved_at="2026-07-23T12:48:00+00:00",
        )
        self.assertFalse(approval.execution_authorized)
        self.assertTrue(runtime.verify_integrity(runtime.integrity_anchor()))


class MKultraV04ServiceTests(unittest.TestCase):
    def test_service_exposes_read_only_status_and_governed_flow(self) -> None:
        service = MKultraV04Service()
        status = service.status()
        self.assertEqual(status["version"], "0.4.0")
        self.assertFalse(status["automatic_self_modification"])
        self.assertEqual(len(service.claims()["claims"]), 5)

        payload = {
            "objective": "Add a deterministic diagnostics panel",
            "target_components": ["ui"],
            "evidence_claim_ids": ["TL-MIRROR-ENGINE-SCAFFOLD-001"],
            "predicted_benefit": "Inspectability",
            "risks": ["stale data"],
            "test_plan": ["unit test"],
            "rollback_plan": ["revert branch"],
            "requested_changes": ["read-only endpoint"],
        }
        proposal = service.propose(payload)["proposal"]
        proposal_id = proposal["proposal_id"]
        evaluation = service.evaluate(
            {
                "proposal_id": proposal_id,
                "scores": SCORES,
                "reasons": ["bounded and testable"],
            }
        )
        self.assertEqual(evaluation["evaluation"]["decision"], "REVIEW_REQUIRED")
        approved = service.approve(
            {
                "proposal_id": proposal_id,
                "reviewer": "VIREAX",
                "human_approved": True,
            }
        )
        self.assertFalse(approved["execution_authorized"])
        self.assertFalse(approved["change_packet"]["execution_authorized"])


if __name__ == "__main__":
    unittest.main()
