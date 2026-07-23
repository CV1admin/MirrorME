from __future__ import annotations

import unittest

from qviraex.cognitive.continuum import CognitiveContinuum
from qviraex.cognitive.signal_bus import CognitiveSignalBus, SignalBusError
from qviraex.existence.schemas import (
    AuthorizedSession,
    EpistemicClass,
    LifecycleState,
    VerifiedIdentityContext,
)
from qviraex.identity.capsule import IdentityCapsuleError, IdentityCapsuleVerifier, capsule_hash
from qviraex.modes.dream.engine import DreamCandidate, DreamEngine
from qviraex.modes.imagination.orchestrator import (
    BranchCandidate,
    BranchRole,
    ImaginationOrchestrator,
)
from qviraex.mkultra_v03 import MKultraRuntime


def make_capsule(*, consent: object = True) -> dict[str, object]:
    capsule: dict[str, object] = {
        "member_id": "CV1-MEMBER-001",
        "node_id": "did:cv1:test-node",
        "capsule_id": "pending",
        "genesis_hash": "sha256:" + "1" * 64,
        "root_key_fingerprint": "sha256:" + "2" * 64,
        "lifecycle_state": "ACTIVE",
        "consent_active": consent,
        "signatures": {"member": "test-only"},
    }
    capsule["capsule_id"] = capsule_hash(capsule)
    return capsule


def make_runtime() -> MKultraRuntime:
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
        session_id="MK03-INTEGRITY",
        runtime_id="RUNTIME-INTEGRITY",
        operator="VIREAX",
        node_id=identity.node_id,
        persistence_authorized=False,
        external_actions_authorized=False,
    )
    return MKultraRuntime(identity=identity, session=session)


class IdentityIntegrityTests(unittest.TestCase):
    def test_string_false_is_not_active_consent(self) -> None:
        capsule = make_capsule(consent="false")
        with self.assertRaisesRegex(IdentityCapsuleError, "JSON boolean"):
            IdentityCapsuleVerifier(lambda _: True).verify(
                capsule,
                expected_document_hash=str(capsule["capsule_id"]),
            )

    def test_signature_verifier_must_return_boolean_true(self) -> None:
        capsule = make_capsule()
        with self.assertRaisesRegex(IdentityCapsuleError, "signature verification failed"):
            IdentityCapsuleVerifier(lambda _: "truthy").verify(  # type: ignore[arg-type]
                capsule,
                expected_document_hash=str(capsule["capsule_id"]),
            )

    def test_node_id_scheme_is_enforced(self) -> None:
        capsule = make_capsule()
        capsule["node_id"] = "arbitrary-node"
        capsule["capsule_id"] = capsule_hash(capsule)
        with self.assertRaisesRegex(IdentityCapsuleError, "did:cv1"):
            IdentityCapsuleVerifier(lambda _: True).verify(
                capsule,
                expected_document_hash=str(capsule["capsule_id"]),
            )


class SignalIntegrityTests(unittest.TestCase):
    def test_nested_payload_mutation_cannot_change_internal_chain(self) -> None:
        bus = CognitiveSignalBus(node_id="did:cv1:test-node")
        payload = {"nested": {"count": 1}}
        published = bus.publish(
            signal_type="mirrorme.test",
            payload=payload,
            epistemic_class=EpistemicClass.OBSERVATION,
        )

        payload["nested"]["count"] = 2
        published.payload["nested"]["count"] = 3
        snapshot = bus.snapshot()
        snapshot[0].payload["nested"]["count"] = 4

        self.assertTrue(bus.verify_chain())
        self.assertEqual(bus.snapshot()[0].payload["nested"]["count"], 1)

    def test_non_finite_signal_payload_is_rejected(self) -> None:
        bus = CognitiveSignalBus(node_id="did:cv1:test-node")
        with self.assertRaisesRegex(SignalBusError, "finite JSON"):
            bus.publish(
                signal_type="mirrorme.test",
                payload={"score": float("nan")},
                epistemic_class=EpistemicClass.HYPOTHESIS,
            )
        self.assertEqual(bus.sequence, 0)


class RuntimeAtomicityTests(unittest.TestCase):
    def test_ingest_before_activation_does_not_mutate_state(self) -> None:
        runtime = make_runtime()
        with self.assertRaisesRegex(RuntimeError, "activated"):
            runtime.ingest(
                content="candidate",
                source="unit-test",
                epistemic_class=EpistemicClass.HYPOTHESIS,
                confidence=0.5,
                provenance_hash="sha256:test",
            )
        self.assertEqual(len(runtime.cognitive.short_memory), 0)
        self.assertEqual(runtime.signal_bus.sequence, 0)

    def test_invalid_packet_fails_before_memory_or_signal_mutation(self) -> None:
        runtime = make_runtime()
        runtime.activate()
        initial_signal_count = runtime.signal_bus.sequence

        with self.assertRaisesRegex(ValueError, "source"):
            runtime.ingest(
                content="candidate",
                source="",
                epistemic_class=EpistemicClass.HYPOTHESIS,
                confidence=0.5,
                provenance_hash="sha256:test",
            )

        self.assertEqual(len(runtime.cognitive.short_memory), 0)
        self.assertEqual(runtime.signal_bus.sequence, initial_signal_count)
        self.assertEqual(runtime.observer.sequence, 0)

    def test_cognitive_confidence_rejects_boolean(self) -> None:
        bus = CognitiveSignalBus(node_id="did:cv1:test-node")
        continuum = CognitiveContinuum(signal_bus=bus)
        with self.assertRaisesRegex(TypeError, "confidence"):
            continuum.remember(
                content="candidate",
                tags=(),
                epistemic_class=EpistemicClass.HYPOTHESIS,
                confidence=True,  # type: ignore[arg-type]
            )
        self.assertEqual(len(continuum.short_memory), 0)
        self.assertEqual(bus.sequence, 0)


class CandidateValidationTests(unittest.TestCase):
    @staticmethod
    def valid_metrics() -> dict[str, float]:
        return {
            "evidence": 0.7,
            "consistency": 0.7,
            "feasibility": 0.7,
            "testability": 0.7,
            "novelty": 0.7,
            "risk": 0.2,
            "cost": 0.2,
            "assumption_burden": 0.2,
        }

    def test_imagination_candidate_rejects_missing_metrics(self) -> None:
        metrics = self.valid_metrics()
        del metrics["risk"]
        with self.assertRaisesRegex(ValueError, "missing"):
            BranchCandidate(
                branch_id="branch-1",
                role=BranchRole.CONSTRUCTIVE_ARCHITECT,
                central_claim="claim",
                mechanism="mechanism",
                assumptions=("assumption",),
                evidence_ids=("evidence",),
                predictions=("prediction",),
                failure_conditions=("failure",),
                confidence=0.7,
                metrics=metrics,
            )

    def test_imagination_runner_cannot_mislabel_branch_role(self) -> None:
        def runner(
            role: BranchRole,
            objective: str,
            context: dict[str, object],
        ) -> BranchCandidate:
            del role, objective, context
            return BranchCandidate(
                branch_id="wrong-role",
                role=BranchRole.CONSTRUCTIVE_ARCHITECT,
                central_claim="claim",
                mechanism="mechanism",
                assumptions=("assumption",),
                evidence_ids=("evidence",),
                predictions=("prediction",),
                failure_conditions=("failure",),
                confidence=0.7,
                metrics=self.valid_metrics(),
            )

        with self.assertRaisesRegex(ValueError, "requested role"):
            ImaginationOrchestrator(runner=runner).run(
                objective="test role binding",
                shared_context={},
            )

    def test_dream_candidate_rejects_non_finite_values(self) -> None:
        with self.assertRaisesRegex(ValueError, "expected_gain"):
            DreamCandidate(
                candidate_id="dream-1",
                description="candidate",
                assumptions=("assumption",),
                inverse_test="inverse",
                boundary_test="boundary",
                null_test="null",
                adversarial_test="adversarial",
                expected_gain=float("nan"),
                risk=0.1,
                cost=0.1,
            )

    def test_dream_evaluator_rejects_non_finite_gain(self) -> None:
        candidates = tuple(
            DreamCandidate(
                candidate_id=f"dream-{index}",
                description="candidate",
                assumptions=("assumption",),
                inverse_test="inverse",
                boundary_test="boundary",
                null_test="null",
                adversarial_test="adversarial",
                expected_gain=0.5,
                risk=0.1,
                cost=0.1,
            )
            for index in range(3)
        )

        engine = DreamEngine(
            generator=lambda state, limit: candidates,
            evaluator=lambda candidate, state: (float("nan"), (), ()),
        )
        with self.assertRaisesRegex(ValueError, "measured gain"):
            engine.run({})


if __name__ == "__main__":
    unittest.main()
