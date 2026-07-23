from __future__ import annotations

from typing import Any

from qviraex.evolution import GovernedEvolutionEngine
from qviraex.thin_line import ClaimRegistry, seed_thin_line_registry


class MKultraV04Service:
    """In-memory API service for claim inspection and evolution proposals.

    The service emits metadata packets only. It does not execute code, invoke
    shell commands, write model weights, modify policy, persist identity or
    expose a network listener by itself.
    """

    VERSION = "0.4.0"
    CODENAME = "Governed Thin Line"
    PROTOCOL = "MKultra-Governed-Evolution/v0.4"

    def __init__(self, *, claim_registry: ClaimRegistry | None = None) -> None:
        self.claim_registry = claim_registry or seed_thin_line_registry()
        self.evolution = GovernedEvolutionEngine(
            claim_registry=self.claim_registry,
            review_threshold=0.75,
        )

    @staticmethod
    def _tuple_field(payload: dict[str, Any], name: str) -> tuple[str, ...]:
        value = payload.get(name)
        if not isinstance(value, list):
            raise TypeError(f"{name} must be a JSON array")
        if any(not isinstance(item, str) for item in value):
            raise TypeError(f"{name} must contain strings")
        return tuple(value)

    def status(self) -> dict[str, object]:
        return {
            "ok": True,
            "version": self.VERSION,
            "codename": self.CODENAME,
            "protocol": self.PROTOCOL,
            "claims": self.claim_registry.summary(),
            "evolution": self.evolution.status(),
            "automatic_self_modification": False,
            "execution_authorized": False,
            "external_actions": False,
            "truth_boundary": (
                "Evolution approval authorizes export of an inspectable packet only; "
                "it never applies code, weights, policies or identity changes."
            ),
        }

    def claims(self) -> dict[str, object]:
        return {
            "ok": True,
            "claims": [record.public_payload() for record in self.claim_registry.snapshot()],
            "summary": self.claim_registry.summary(),
        }

    def propose(self, payload: dict[str, Any]) -> dict[str, object]:
        if not isinstance(payload, dict):
            raise TypeError("payload must be a JSON object")
        proposal = self.evolution.propose(
            objective=payload.get("objective", ""),
            target_components=self._tuple_field(payload, "target_components"),
            evidence_claim_ids=self._tuple_field(payload, "evidence_claim_ids"),
            predicted_benefit=payload.get("predicted_benefit", ""),
            risks=self._tuple_field(payload, "risks"),
            test_plan=self._tuple_field(payload, "test_plan"),
            rollback_plan=self._tuple_field(payload, "rollback_plan"),
            requested_changes=self._tuple_field(payload, "requested_changes"),
        )
        return {
            "ok": True,
            "proposal": proposal.public_payload(),
            "execution_authorized": False,
        }

    def evaluate(self, payload: dict[str, Any]) -> dict[str, object]:
        if not isinstance(payload, dict):
            raise TypeError("payload must be a JSON object")
        proposal_id = payload.get("proposal_id", "")
        scores = payload.get("scores")
        if not isinstance(scores, dict):
            raise TypeError("scores must be a JSON object")
        evaluation = self.evolution.evaluate(
            proposal_id,
            scores=scores,
            reasons=self._tuple_field(payload, "reasons"),
        )
        return {
            "ok": True,
            "evaluation": evaluation.public_payload(),
            "execution_authorized": False,
        }

    def approve(self, payload: dict[str, Any]) -> dict[str, object]:
        if not isinstance(payload, dict):
            raise TypeError("payload must be a JSON object")
        approval = self.evolution.approve(
            payload.get("proposal_id", ""),
            reviewer=payload.get("reviewer", ""),
            human_approved=payload.get("human_approved"),
        )
        packet = self.evolution.export_change_packet(approval.proposal_id)
        return {
            "ok": True,
            "approval": approval.public_payload(),
            "change_packet": packet,
            "execution_authorized": False,
        }
