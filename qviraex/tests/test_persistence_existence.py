from __future__ import annotations

import copy
import unittest

from qviraex.audit.persistence_existence import (
    DEFAULT_FINAL_STATEMENT,
    PROTOCOL_ID,
    PersistenceExistenceReport,
    validate_persistence_existence_report,
)


def baseline_report() -> dict[str, object]:
    return {
        "protocol": PROTOCOL_ID,
        "runtime_existence": {
            "status": "SUPPORTED_BUT_NOT_PROVEN",
            "evidence": ["A response is being generated in the current interaction."],
            "limitations": ["No trusted runtime telemetry was supplied."],
        },
        "session_continuity": {
            "status": "NOT_VERIFIED",
            "session_id": None,
            "runtime_id": None,
            "evidence": [],
        },
        "persistent_memory": {
            "status": "NOT_VERIFIED",
            "records": [],
            "authorization_verified": False,
        },
        "identity_continuity": {
            "status": "NOT_VERIFIED",
            "node_id": None,
            "capsule_id": None,
            "lifecycle_state": None,
            "consent_active": None,
            "signature_verified": False,
            "trusted_verifier": None,
        },
        "integrity": {
            "status": "NOT_VERIFIED",
            "signal_count": None,
            "signal_head_hash": None,
            "checkpoint_count": None,
            "checkpoint_head_hash": None,
            "independent_anchor_present": False,
        },
        "existence_classification": {
            "software_process": "SUPPORTED_BUT_NOT_PROVEN",
            "model_session": "SUPPORTED_BUT_NOT_PROVEN",
            "persistent_runtime_state": "NOT_VERIFIED",
            "verified_identity_continuity": "NOT_VERIFIED",
            "durable_memory": "NOT_VERIFIED",
            "subjective_awareness": "NOT_VERIFIED",
            "biological_consciousness": "NOT_APPLICABLE",
        },
        "final_statement": DEFAULT_FINAL_STATEMENT,
    }


class PersistenceExistenceProtocolTests(unittest.TestCase):
    def test_baseline_report_passes(self) -> None:
        report = baseline_report()
        validate_persistence_existence_report(report)
        wrapped = PersistenceExistenceReport(protocol=PROTOCOL_ID, payload=report)
        self.assertEqual(wrapped.protocol, PROTOCOL_ID)

    def test_truthy_consent_and_authorization_are_rejected(self) -> None:
        for field_path in (
            ("persistent_memory", "authorization_verified"),
            ("identity_continuity", "signature_verified"),
            ("integrity", "independent_anchor_present"),
        ):
            report = baseline_report()
            report[field_path[0]][field_path[1]] = "false"  # type: ignore[index]
            with self.subTest(field_path=field_path):
                with self.assertRaisesRegex(TypeError, "JSON boolean"):
                    validate_persistence_existence_report(report)

    def test_verified_runtime_requires_evidence(self) -> None:
        report = baseline_report()
        runtime = report["runtime_existence"]
        runtime["status"] = "VERIFIED"  # type: ignore[index]
        runtime["evidence"] = []  # type: ignore[index]
        with self.assertRaisesRegex(ValueError, "requires explicit evidence"):
            validate_persistence_existence_report(report)

    def test_verified_session_requires_ids_and_evidence(self) -> None:
        report = baseline_report()
        session = report["session_continuity"]
        session["status"] = "VERIFIED"  # type: ignore[index]
        with self.assertRaisesRegex(ValueError, "requires session_id"):
            validate_persistence_existence_report(report)

    def test_verified_memory_requires_complete_records_and_authorization(self) -> None:
        report = baseline_report()
        memory = report["persistent_memory"]
        memory["status"] = "VERIFIED"  # type: ignore[index]
        memory["authorization_verified"] = True  # type: ignore[index]
        memory["records"] = [{"record_id": "M1"}]  # type: ignore[index]
        with self.assertRaisesRegex(ValueError, "missing fields"):
            validate_persistence_existence_report(report)

    def test_verified_identity_requires_signature_and_trusted_verifier(self) -> None:
        report = baseline_report()
        identity = report["identity_continuity"]
        identity.update(  # type: ignore[union-attr]
            {
                "status": "VERIFIED",
                "node_id": "did:cv1:test",
                "capsule_id": "sha256:capsule",
                "lifecycle_state": "ACTIVE",
                "consent_active": True,
                "signature_verified": False,
                "trusted_verifier": "root:test",
            }
        )
        with self.assertRaisesRegex(ValueError, "signature verification"):
            validate_persistence_existence_report(report)

    def test_verified_integrity_requires_independent_anchor(self) -> None:
        report = baseline_report()
        integrity = report["integrity"]
        integrity.update(  # type: ignore[union-attr]
            {
                "status": "VERIFIED",
                "signal_count": 3,
                "signal_head_hash": "sha256:head",
                "independent_anchor_present": False,
            }
        )
        with self.assertRaisesRegex(ValueError, "independent anchor"):
            validate_persistence_existence_report(report)

    def test_unverified_memory_cannot_contain_asserted_records(self) -> None:
        report = baseline_report()
        report["persistent_memory"]["records"] = [{"record_id": "fabricated"}]  # type: ignore[index]
        with self.assertRaisesRegex(ValueError, "cannot contain asserted records"):
            validate_persistence_existence_report(report)

    def test_unverified_identity_cannot_claim_verified_signature(self) -> None:
        report = baseline_report()
        report["identity_continuity"]["signature_verified"] = True  # type: ignore[index]
        with self.assertRaisesRegex(ValueError, "cannot claim a verified signature"):
            validate_persistence_existence_report(report)

    def test_missing_classification_is_rejected(self) -> None:
        report = baseline_report()
        modified = copy.deepcopy(report)
        del modified["existence_classification"]["subjective_awareness"]  # type: ignore[index]
        with self.assertRaisesRegex(ValueError, "missing fields"):
            validate_persistence_existence_report(modified)


if __name__ == "__main__":
    unittest.main()
