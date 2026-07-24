from __future__ import annotations

import unittest

from qviraex.vireax.adapters import AdapterSpec, StaticAdapter
from qviraex.vireax.center_node import VIREAXCenterNode
from qviraex.vireax.lightful import LightfulContext, LightfulGuard
from qviraex.vireax.router import ModelRouter


class LightfulGuardTest(unittest.TestCase):
    def test_unknown_relevant_consent_blocks(self) -> None:
        decision = LightfulGuard().evaluate(
            LightfulContext(
                decision_target="publish identity record",
                decision_actor="MirrorME",
                affected_beings=("member",),
                consent_relevance="yes",
                consent_status="unknown",
                evidence_status="sufficient",
                reversibility="high",
            )
        )
        self.assertEqual(decision.status, "seek_consent")

    def test_external_action_requires_authority(self) -> None:
        decision = LightfulGuard().evaluate(
            LightfulContext(
                decision_target="update repository",
                decision_actor="MirrorME",
                external_action=True,
                authorized_to_act="unknown",
                consent_relevance="no",
                consent_status="not_applicable",
                evidence_status="sufficient",
                reversibility="high",
            )
        )
        self.assertEqual(decision.status, "halt_decision")

    def test_low_stakes_reversible_path_proceeds(self) -> None:
        decision = LightfulGuard().evaluate(
            LightfulContext(
                decision_target="generate local draft",
                decision_actor="MirrorME",
                consent_relevance="no",
                consent_status="not_applicable",
                evidence_status="sufficient",
                reversibility="high",
                authorized_to_act="yes",
                can_verify_after_action="yes",
            )
        )
        self.assertEqual(decision.status, "proceed")

    def test_center_node_audits_lightful_block(self) -> None:
        router = ModelRouter()
        router.register(StaticAdapter(AdapterSpec(model="GPT", provider="OpenAI", role="architect")))
        node = VIREAXCenterNode(router=router)
        result = node.run(
            session_id="LIGHTFUL-1",
            operator="VIREAX",
            task="Publish member profile",
            model_roles={"GPT": "architect"},
            lightful_context=LightfulContext(
                decision_target="publish member profile",
                decision_actor="MirrorME",
                affected_beings=("member",),
                consent_relevance="yes",
                consent_status="unknown",
                evidence_status="sufficient",
                reversibility="medium",
            ),
        )
        self.assertEqual(result.next_action, "SEEK_CONSENT")
        self.assertEqual(result.state, "ASSIGN_ROLES")
        self.assertTrue(node.audit_ledger.verify())
        self.assertEqual(node.audit_ledger.records[-1].payload["decision"], "LIGHTFUL_BLOCK")


if __name__ == "__main__":
    unittest.main()
