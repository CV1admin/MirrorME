from __future__ import annotations

import unittest

from qviraex.existence.schemas import AuthorizedSession, LifecycleState, VerifiedIdentityContext


class AuthoritySchemaTests(unittest.TestCase):
    def test_string_false_cannot_authorize_persistence(self) -> None:
        with self.assertRaisesRegex(TypeError, "persistence_authorized"):
            AuthorizedSession(
                session_id="SESSION-1",
                runtime_id="RUNTIME-1",
                operator="VIREAX",
                node_id="did:cv1:test-node",
                persistence_authorized="false",  # type: ignore[arg-type]
                external_actions_authorized=False,
            )

    def test_string_false_cannot_authorize_external_actions(self) -> None:
        with self.assertRaisesRegex(TypeError, "external_actions_authorized"):
            AuthorizedSession(
                session_id="SESSION-1",
                runtime_id="RUNTIME-1",
                operator="VIREAX",
                node_id="did:cv1:test-node",
                persistence_authorized=False,
                external_actions_authorized="false",  # type: ignore[arg-type]
            )

    def test_direct_identity_context_rejects_string_consent(self) -> None:
        with self.assertRaisesRegex(TypeError, "consent_active"):
            VerifiedIdentityContext(
                node_id="did:cv1:test-node",
                capsule_id="sha256:" + "a" * 64,
                member_id="CV1-MEMBER-001",
                genesis_hash="sha256:" + "b" * 64,
                key_fingerprint="sha256:" + "c" * 64,
                lifecycle_state=LifecycleState.ACTIVE,
                consent_active="false",  # type: ignore[arg-type]
            )

    def test_invalid_node_scheme_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "did:cv1"):
            AuthorizedSession(
                session_id="SESSION-1",
                runtime_id="RUNTIME-1",
                operator="VIREAX",
                node_id="not-a-cv1-did",
            )


if __name__ == "__main__":
    unittest.main()
