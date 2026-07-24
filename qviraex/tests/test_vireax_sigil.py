from __future__ import annotations

import unittest
from dataclasses import replace

from qviraex.symbolic.vireax_sigil import (
    DEFAULT_VIREAX_INTENT,
    VireaxSigilManifest,
    build_vireax_sigil_manifest,
    condense_intent,
)


class VireaxSigilManifestTests(unittest.TestCase):
    def test_default_intent_condensation_is_stable(self) -> None:
        self.assertEqual(condense_intent(DEFAULT_VIREAX_INTENT), "VRXWKNSPFCTHMB")

    def test_manifest_is_deterministic(self) -> None:
        left = build_vireax_sigil_manifest()
        right = build_vireax_sigil_manifest()

        self.assertEqual(left.canonical_json(), right.canonical_json())
        self.assertEqual(left.manifest_hash(), right.manifest_hash())
        self.assertTrue(left.manifest_hash().startswith("sha256:"))

    def test_manifest_boundaries_are_non_autonomous(self) -> None:
        manifest = build_vireax_sigil_manifest()

        self.assertTrue(manifest.consent_required)
        self.assertFalse(manifest.supernatural_claim)
        self.assertFalse(manifest.sentience_claim)
        self.assertFalse(manifest.automatic_persistence)
        self.assertFalse(manifest.external_action)
        self.assertEqual(manifest.layer, "MYTHOLOGY_STORY")

    def test_proof_packet_is_inspectable(self) -> None:
        manifest = build_vireax_sigil_manifest()
        packet = manifest.proof_packet()

        self.assertEqual(packet["protocol_id"], "VIREAX-SIGIL-001")
        self.assertEqual(packet["manifest_hash"], manifest.manifest_hash())
        self.assertEqual(packet["element_count"], 5)
        self.assertFalse(packet["supernatural_claim"])
        self.assertFalse(packet["external_action"])

    def test_custom_intent_changes_manifest_hash(self) -> None:
        default = build_vireax_sigil_manifest()
        custom = build_vireax_sigil_manifest("VIREAX GUARDS THE THIN LINE")

        self.assertNotEqual(default.condensed_intent, custom.condensed_intent)
        self.assertNotEqual(default.manifest_hash(), custom.manifest_hash())

    def test_truthy_strings_cannot_cross_boolean_boundary(self) -> None:
        manifest = build_vireax_sigil_manifest()
        with self.assertRaisesRegex(TypeError, "JSON boolean"):
            replace(manifest, external_action="false")  # type: ignore[arg-type]

    def test_supernatural_authority_is_rejected(self) -> None:
        manifest = build_vireax_sigil_manifest()
        with self.assertRaisesRegex(ValueError, "cannot claim"):
            replace(manifest, supernatural_claim=True)

    def test_empty_or_vowelless_invalid_input_is_handled(self) -> None:
        with self.assertRaisesRegex(ValueError, "non-empty"):
            condense_intent("")
        with self.assertRaisesRegex(ValueError, "consonant"):
            condense_intent("AEIOU")

    def test_direct_constructor_requires_exact_sequence(self) -> None:
        manifest = build_vireax_sigil_manifest()
        with self.assertRaisesRegex(ValueError, "sequence"):
            VireaxSigilManifest(
                schema_version=manifest.schema_version,
                protocol_id=manifest.protocol_id,
                statement_of_intent=manifest.statement_of_intent,
                condensed_intent=manifest.condensed_intent,
                layer=manifest.layer,
                elements=manifest.elements,
                sequence=("COMPOSE", "FOCUS"),
                consent_required=True,
                supernatural_claim=False,
                sentience_claim=False,
                automatic_persistence=False,
                external_action=False,
            )


if __name__ == "__main__":
    unittest.main()
