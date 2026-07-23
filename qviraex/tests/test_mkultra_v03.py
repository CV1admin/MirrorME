from __future__ import annotations

import unittest

from qviraex.cognitive.signal_bus import CognitiveSignalBus
from qviraex.existence.schemas import (
    AuthorizedSession,
    EpistemicClass,
    LifecycleState,
    PromotionState,
    VerifiedIdentityContext,
)
from qviraex.identity.capsule import IdentityCapsuleVerifier, capsule_hash
from qviraex.modes.dream.engine import DreamCandidate, DreamEngine, DreamStatus
from qviraex.modes.imagination.orchestrator import (
    BranchCandidate,
    BranchRole,
    ImaginationOrchestrator,
)
from qviraex.mkultra_v03 import MKultraRuntime
from qviraex.verification.dgrep.engine import DGREPEngine, VerificationCandidate


class IdentityCapsuleTests(unittest.TestCase):
    def test_verified_capsule_creates_stable_identity_context(self) -> None:
        capsule = {
            "member_id": "CV1-MEMBER-001",
            "node_id": "did:cv1:test-node",
            "capsule_id": "pending",
            "genesis_hash": "sha256:" + "1" * 64,
            "root_key_fingerprint": "sha256:" + "2" * 64,
            "lifecycle_state": "ACTIVE",
            "consent_active": True,
            "signatures": {"member": "test-only"},
        }
        commitment = capsule_hash(capsule)
        capsule["capsule_id"] = commitment

        context = IdentityCapsuleVerifier(lambda document: bool(document["signatures"])).verify(
            capsule,
            expected_document_hash=commitment,
        )

        self.assertEqual(context.node_id, "did:cv1:test-node")
        self.assertEqual(context.capsule_id, commitment)
        self.assertTrue(context.consent_active)


class SignalBusTests(unittest.TestCase):
    def test_signal_hash_chain_is_ordered_and_valid(self) -> None:
        bus = CognitiveSignalBus(node_id="did:cv1:test-node")
        first = bus.publish(
            signal_type="mirrorme.runtime.started",
            payload={"runtime": "one"},
            epistemic_class=EpistemicClass.OBSERVATION,
        )
        second = bus.publish(
            signal_type="mirrorme.short_memory.updated",
            payload={"count": 1},
            epistemic_class=EpistemicClass.OBSERVATION,
        )

        self.assertIsNone(first.previous_hash)
        self.assertEqual(second.previous_hash, first.signal_hash)
        self.assertTrue(bus.verify_chain())


class RuntimeIntegrationTests(unittest.TestCase):
    def make_runtime(self, *, persistence: bool = False) -> MKultraRuntime:
        identity = VerifiedIdentityContext(
            node_id="did:cv1:test-node",
            capsule_id="sha256:" + "a" * 64,
            member_id="CV1-MEMBER-001",
            genesis_hash="sha256:" + "b" * 64,
            key_fingerprint="sha256:" + "c" * 64,
            lifecycle_state=LifecycleState.ACTIVE,
            consent_active=True,
        )
        session = AuthorizedSession(
            session_id="MK03-TEST",
            runtime_id="RUNTIME-TEST",
            operator="VIREAX",
            node_id=identity.node_id,
            persistence_authorized=persistence,
            external_actions_authorized=False,
        )
        return MKultraRuntime(identity=identity, session=session, checkpoint_interval=2)

    def test_identity_observer_continuum_and_spark_path(self) -> None:
        runtime = self.make_runtime()
        runtime.activate()
        first_spark = runtime.ingest(
            content="Observer loop preserves unresolved hypotheses.",
            source="unit-test",
            epistemic_class=EpistemicClass.HYPOTHESIS,
            confidence=0.60,
            provenance_hash="sha256:first",
            tags=("observer", "continuity"),
            requires_resolution=True,
        )
        second_spark = runtime.ingest(
            content="Persistence relays continuity across runtime replacement.",
            source="unit-test",
            epistemic_class=EpistemicClass.HYPOTHESIS,
            confidence=0.55,
            provenance_hash="sha256:second",
            tags=("continuity", "persistence"),
        )

        self.assertIsNone(first_spark)
        self.assertIsNotNone(second_spark)
        self.assertEqual(runtime.state().node_id, "did:cv1:test-node")
        self.assertTrue(runtime.signal_bus.verify_chain())
        with self.assertRaises(PermissionError):
            runtime.checkpoint()

    def test_authorized_checkpoint_is_explicit(self) -> None:
        runtime = self.make_runtime(persistence=True)
        runtime.activate()
        runtime.ingest(
            content="Verified checkpoint candidate.",
            source="unit-test",
            epistemic_class=EpistemicClass.OBSERVATION,
            confidence=1.0,
            provenance_hash="sha256:checkpoint",
            tags=("checkpoint",),
        )
        checkpoint = runtime.checkpoint()
        self.assertTrue(checkpoint.checkpoint_hash.startswith("sha256:"))
        self.assertEqual(runtime.state().last_checkpoint_hash, checkpoint.checkpoint_hash)


class ImaginationTests(unittest.TestCase):
    def test_parallel_branches_are_compared_without_consensus_promotion(self) -> None:
        def runner(role: BranchRole, objective: str, context: dict[str, object]) -> BranchCandidate:
            return BranchCandidate(
                branch_id=role.value,
                role=role,
                central_claim=f"{role.value} candidate for {objective}",
                mechanism=f"Mechanism specialized for {role.value} using {context['domain']}",
                assumptions=(f"assumption-{role.value}",),
                evidence_ids=("evidence-1",),
                predictions=(f"prediction-{role.value}",),
                failure_conditions=(f"failure-{role.value}",),
                confidence=0.70,
                metrics={
                    "evidence": 0.75,
                    "consistency": 0.80,
                    "feasibility": 0.70,
                    "testability": 0.75,
                    "novelty": 0.65,
                    "risk": 0.20,
                    "cost": 0.30,
                    "assumption_burden": 0.25,
                },
            )

        result = ImaginationOrchestrator(runner=runner).run(
            objective="design a persistence relay",
            shared_context={"domain": "local-runtime"},
        )
        self.assertEqual(len(result.candidates), 6)
        self.assertGreater(result.diversity, 0.0)
        self.assertGreaterEqual(len(result.pareto_branch_ids), 1)


class DreamAndDGREPTests(unittest.TestCase):
    def test_dream_candidates_require_external_review(self) -> None:
        def generator(state: dict[str, object], limit: int) -> tuple[DreamCandidate, ...]:
            del state, limit
            return tuple(
                DreamCandidate(
                    candidate_id=f"candidate-{index}",
                    description=f"Improvement candidate {index}",
                    assumptions=(f"assumption-{index}",),
                    inverse_test="inverse",
                    boundary_test="boundary",
                    null_test="null",
                    adversarial_test="adversarial",
                    expected_gain=0.80 - 0.05 * index,
                    risk=0.10,
                    cost=0.10,
                )
                for index in range(3)
            )

        def evaluator(
            candidate: DreamCandidate,
            state: dict[str, object],
        ) -> tuple[float, tuple[str, ...], tuple[str, ...]]:
            del state
            return candidate.expected_gain, ("inverse", "boundary", "null", "adversarial"), ()

        evaluations = DreamEngine(generator=generator, evaluator=evaluator).run({"failure": "test"})
        self.assertEqual(len(evaluations), 3)
        self.assertTrue(all(item.status is DreamStatus.REVIEW_REQUIRED for item in evaluations))
        self.assertFalse(DreamEngine.promotion_authorized(evaluations[0]))

    def test_dgrep_recommends_review_but_cannot_persist(self) -> None:
        engine = DGREPEngine(minimum_score=0.75)
        decision = engine.verify(
            VerificationCandidate(
                candidate_id="verified-candidate",
                claim="Candidate passed controlled tests",
                provenance_ids=("test-run-1",),
                evidence_score=0.90,
                consistency_score=0.90,
                test_score=0.85,
                safety_score=0.95,
                requested_state=PromotionState.TESTED,
            )
        )
        self.assertEqual(decision.state, PromotionState.REVIEW_REQUIRED)
        self.assertTrue(decision.human_review_required)
        self.assertFalse(engine.authorize_persistence(decision, {}))


if __name__ == "__main__":
    unittest.main()
