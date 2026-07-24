from __future__ import annotations

import json
import re
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from math import isfinite
from threading import RLock
from typing import Iterable
from uuid import uuid4

from qviraex.thin_line.claims import ClaimLayer, ClaimRegistry, ClaimStatus

_SHA256_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
_SCORE_KEYS = ("evidence", "testability", "reversibility", "safety", "integrity")


class ProposalState(StrEnum):
    DRAFT = "DRAFT"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPORTED = "EXPORTED"


def _require_text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def _require_text_tuple(value: object, name: str, *, minimum: int = 1) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        raise TypeError(f"{name} must be a tuple")
    if len(value) < minimum:
        raise ValueError(f"{name} must contain at least {minimum} item(s)")
    normalized = tuple(_require_text(item, f"{name} item") for item in value)
    if len(set(normalized)) != len(normalized):
        raise ValueError(f"{name} must not contain duplicates")
    return normalized


def _score(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be numeric")
    try:
        result = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} is outside the finite float range") from exc
    if not isfinite(result) or not 0.0 <= result <= 1.0:
        raise ValueError(f"{name} must be finite and between 0 and 1")
    return result


def _canonical_json(payload: dict[str, object]) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


@dataclass(frozen=True)
class EvolutionProposal:
    proposal_id: str
    objective: str
    target_components: tuple[str, ...]
    evidence_claim_ids: tuple[str, ...]
    predicted_benefit: str
    risks: tuple[str, ...]
    test_plan: tuple[str, ...]
    rollback_plan: tuple[str, ...]
    requested_changes: tuple[str, ...]
    created_at: str
    sequence: int
    previous_hash: str | None
    proposal_hash: str
    state: ProposalState = ProposalState.DRAFT

    def __post_init__(self) -> None:
        _require_text(self.proposal_id, "proposal_id")
        _require_text(self.objective, "objective")
        object.__setattr__(self, "target_components", _require_text_tuple(self.target_components, "target_components"))
        object.__setattr__(self, "evidence_claim_ids", _require_text_tuple(self.evidence_claim_ids, "evidence_claim_ids"))
        _require_text(self.predicted_benefit, "predicted_benefit")
        object.__setattr__(self, "risks", _require_text_tuple(self.risks, "risks"))
        object.__setattr__(self, "test_plan", _require_text_tuple(self.test_plan, "test_plan"))
        object.__setattr__(self, "rollback_plan", _require_text_tuple(self.rollback_plan, "rollback_plan"))
        object.__setattr__(self, "requested_changes", _require_text_tuple(self.requested_changes, "requested_changes"))
        _require_text(self.created_at, "created_at")
        if isinstance(self.sequence, bool) or not isinstance(self.sequence, int) or self.sequence < 1:
            raise ValueError("sequence must be a positive integer")
        if self.previous_hash is not None and _SHA256_PATTERN.fullmatch(self.previous_hash) is None:
            raise ValueError("previous_hash must be lowercase sha256:<64 hexadecimal characters>")
        if _SHA256_PATTERN.fullmatch(self.proposal_hash) is None:
            raise ValueError("proposal_hash must be lowercase sha256:<64 hexadecimal characters>")
        if not isinstance(self.state, ProposalState):
            raise TypeError("state must be a ProposalState")

    def body(self) -> dict[str, object]:
        return {
            "proposal_id": self.proposal_id,
            "objective": self.objective,
            "target_components": list(self.target_components),
            "evidence_claim_ids": list(self.evidence_claim_ids),
            "predicted_benefit": self.predicted_benefit,
            "risks": list(self.risks),
            "test_plan": list(self.test_plan),
            "rollback_plan": list(self.rollback_plan),
            "requested_changes": list(self.requested_changes),
            "created_at": self.created_at,
            "sequence": self.sequence,
            "previous_hash": self.previous_hash,
        }

    def public_payload(self) -> dict[str, object]:
        return {**self.body(), "proposal_hash": self.proposal_hash, "state": self.state.value}


@dataclass(frozen=True)
class EvolutionEvaluation:
    proposal_id: str
    scores: tuple[tuple[str, float], ...]
    overall_score: float
    decision: ProposalState
    reasons: tuple[str, ...]
    evaluated_at: str
    evaluation_hash: str
    human_review_required: bool = True

    def __post_init__(self) -> None:
        _require_text(self.proposal_id, "proposal_id")
        if not isinstance(self.scores, tuple):
            raise TypeError("scores must be a tuple")
        score_map = dict(self.scores)
        if tuple(sorted(score_map)) != tuple(sorted(_SCORE_KEYS)):
            raise ValueError(f"scores must contain exactly: {', '.join(_SCORE_KEYS)}")
        normalized = tuple((key, _score(score_map[key], key)) for key in _SCORE_KEYS)
        object.__setattr__(self, "scores", normalized)
        object.__setattr__(self, "overall_score", _score(self.overall_score, "overall_score"))
        if self.decision not in {ProposalState.REVIEW_REQUIRED, ProposalState.REJECTED}:
            raise ValueError("evaluation decision must be REVIEW_REQUIRED or REJECTED")
        object.__setattr__(self, "reasons", _require_text_tuple(self.reasons, "reasons"))
        _require_text(self.evaluated_at, "evaluated_at")
        if _SHA256_PATTERN.fullmatch(self.evaluation_hash) is None:
            raise ValueError("evaluation_hash must be lowercase sha256:<64 hexadecimal characters>")
        if type(self.human_review_required) is not bool or not self.human_review_required:
            raise ValueError("human_review_required must be true")

    def public_payload(self) -> dict[str, object]:
        return {
            "proposal_id": self.proposal_id,
            "scores": dict(self.scores),
            "overall_score": self.overall_score,
            "decision": self.decision.value,
            "reasons": list(self.reasons),
            "evaluated_at": self.evaluated_at,
            "evaluation_hash": self.evaluation_hash,
            "human_review_required": self.human_review_required,
        }


@dataclass(frozen=True)
class EvolutionApproval:
    proposal_id: str
    proposal_hash: str
    evaluation_hash: str
    reviewer: str
    approved_at: str
    approval_hash: str
    execution_authorized: bool = False
    weight_update_authorized: bool = False
    policy_update_authorized: bool = False
    identity_update_authorized: bool = False

    def __post_init__(self) -> None:
        _require_text(self.proposal_id, "proposal_id")
        for name in ("proposal_hash", "evaluation_hash", "approval_hash"):
            value = getattr(self, name)
            if _SHA256_PATTERN.fullmatch(value) is None:
                raise ValueError(f"{name} must be lowercase sha256:<64 hexadecimal characters>")
        _require_text(self.reviewer, "reviewer")
        _require_text(self.approved_at, "approved_at")
        for name in (
            "execution_authorized",
            "weight_update_authorized",
            "policy_update_authorized",
            "identity_update_authorized",
        ):
            if type(getattr(self, name)) is not bool:
                raise TypeError(f"{name} must be a boolean")
            if getattr(self, name):
                raise ValueError(f"{name} must remain false in MKultra v0.4")

    def public_payload(self) -> dict[str, object]:
        return {
            "proposal_id": self.proposal_id,
            "proposal_hash": self.proposal_hash,
            "evaluation_hash": self.evaluation_hash,
            "reviewer": self.reviewer,
            "approved_at": self.approved_at,
            "approval_hash": self.approval_hash,
            "execution_authorized": False,
            "weight_update_authorized": False,
            "policy_update_authorized": False,
            "identity_update_authorized": False,
        }


class GovernedEvolutionEngine:
    """Proposal-only evolution system with mandatory human review.

    Approval authorizes export of an inspectable change packet. It never applies
    code changes, writes model weights, changes policies, changes identity or
    grants external-action authority.
    """

    def __init__(self, *, claim_registry: ClaimRegistry, review_threshold: float = 0.75) -> None:
        if not isinstance(claim_registry, ClaimRegistry):
            raise TypeError("claim_registry must be a ClaimRegistry")
        self.claim_registry = claim_registry
        self.review_threshold = _score(review_threshold, "review_threshold")
        self._proposals: list[EvolutionProposal] = []
        self._evaluations: dict[str, EvolutionEvaluation] = {}
        self._approvals: dict[str, EvolutionApproval] = {}
        self._lock = RLock()

    def propose(
        self,
        *,
        objective: str,
        target_components: tuple[str, ...],
        evidence_claim_ids: tuple[str, ...],
        predicted_benefit: str,
        risks: tuple[str, ...],
        test_plan: tuple[str, ...],
        rollback_plan: tuple[str, ...],
        requested_changes: tuple[str, ...],
        proposal_id: str | None = None,
        created_at: str | None = None,
    ) -> EvolutionProposal:
        objective_text = _require_text(objective, "objective")
        targets = _require_text_tuple(target_components, "target_components")
        evidence_ids = _require_text_tuple(evidence_claim_ids, "evidence_claim_ids")
        benefit = _require_text(predicted_benefit, "predicted_benefit")
        risk_items = _require_text_tuple(risks, "risks")
        tests = _require_text_tuple(test_plan, "test_plan")
        rollback = _require_text_tuple(rollback_plan, "rollback_plan")
        changes = _require_text_tuple(requested_changes, "requested_changes")
        missing = tuple(claim_id for claim_id in evidence_ids if not self.claim_registry.contains(claim_id))
        if missing:
            raise ValueError(f"unknown evidence claim ids: {missing}")

        with self._lock:
            identifier = proposal_id or f"MK04-EVO-{uuid4()}"
            if any(item.proposal_id == identifier for item in self._proposals):
                raise ValueError(f"duplicate proposal_id: {identifier}")
            timestamp = created_at or datetime.now(UTC).isoformat()
            sequence = len(self._proposals) + 1
            previous_hash = self._proposals[-1].proposal_hash if self._proposals else None
            body = {
                "proposal_id": identifier,
                "objective": objective_text,
                "target_components": list(targets),
                "evidence_claim_ids": list(evidence_ids),
                "predicted_benefit": benefit,
                "risks": list(risk_items),
                "test_plan": list(tests),
                "rollback_plan": list(rollback),
                "requested_changes": list(changes),
                "created_at": timestamp,
                "sequence": sequence,
                "previous_hash": previous_hash,
            }
            proposal_hash = f"sha256:{sha256(_canonical_json(body).encode('utf-8')).hexdigest()}"
            proposal = EvolutionProposal(
                proposal_id=identifier,
                objective=objective_text,
                target_components=targets,
                evidence_claim_ids=evidence_ids,
                predicted_benefit=benefit,
                risks=risk_items,
                test_plan=tests,
                rollback_plan=rollback,
                requested_changes=changes,
                created_at=timestamp,
                sequence=sequence,
                previous_hash=previous_hash,
                proposal_hash=proposal_hash,
            )
            self._proposals.append(proposal)
            return proposal

    def get_proposal(self, proposal_id: str) -> EvolutionProposal:
        identifier = _require_text(proposal_id, "proposal_id")
        with self._lock:
            for proposal in self._proposals:
                if proposal.proposal_id == identifier:
                    return proposal
        raise KeyError(identifier)

    def evaluate(
        self,
        proposal_id: str,
        *,
        scores: dict[str, object],
        reasons: tuple[str, ...],
        evaluated_at: str | None = None,
    ) -> EvolutionEvaluation:
        if not isinstance(scores, dict):
            raise TypeError("scores must be a dictionary")
        if set(scores) != set(_SCORE_KEYS):
            raise ValueError(f"scores must contain exactly: {', '.join(_SCORE_KEYS)}")
        normalized_scores = tuple((key, _score(scores[key], key)) for key in _SCORE_KEYS)
        reason_items = _require_text_tuple(reasons, "reasons")

        with self._lock:
            proposal = self.get_proposal(proposal_id)
            if proposal.state is not ProposalState.DRAFT:
                raise ValueError(f"proposal is not evaluable from state {proposal.state}")
            evidence_records = tuple(self.claim_registry.get(claim_id) for claim_id in proposal.evidence_claim_ids)
            evidence_only_story = all(
                record.draft.layer is ClaimLayer.MYTHOLOGY_STORY for record in evidence_records
            )
            evidence_rejected = any(
                record.draft.status is ClaimStatus.REJECTED for record in evidence_records
            )
            overall = round(sum(value for _, value in normalized_scores) / len(normalized_scores), 6)
            decision = (
                ProposalState.REJECTED
                if evidence_only_story or evidence_rejected or overall < self.review_threshold
                else ProposalState.REVIEW_REQUIRED
            )
            generated_reasons = list(reason_items)
            if evidence_only_story:
                generated_reasons.append("mythology-only evidence cannot support an engineering evolution proposal")
            if evidence_rejected:
                generated_reasons.append("one or more evidence claims are rejected")
            if overall < self.review_threshold:
                generated_reasons.append("overall score is below the review threshold")
            timestamp = evaluated_at or datetime.now(UTC).isoformat()
            evaluation_body = {
                "proposal_id": proposal.proposal_id,
                "proposal_hash": proposal.proposal_hash,
                "scores": dict(normalized_scores),
                "overall_score": overall,
                "decision": decision.value,
                "reasons": generated_reasons,
                "evaluated_at": timestamp,
                "human_review_required": True,
            }
            evaluation_hash = f"sha256:{sha256(_canonical_json(evaluation_body).encode('utf-8')).hexdigest()}"
            evaluation = EvolutionEvaluation(
                proposal_id=proposal.proposal_id,
                scores=normalized_scores,
                overall_score=overall,
                decision=decision,
                reasons=tuple(generated_reasons),
                evaluated_at=timestamp,
                evaluation_hash=evaluation_hash,
                human_review_required=True,
            )
            self._evaluations[proposal.proposal_id] = evaluation
            self._replace_proposal(replace(proposal, state=decision))
            return evaluation

    def approve(
        self,
        proposal_id: str,
        *,
        reviewer: str,
        human_approved: bool,
        approved_at: str | None = None,
    ) -> EvolutionApproval:
        if type(human_approved) is not bool:
            raise TypeError("human_approved must be a boolean")
        if not human_approved:
            raise PermissionError("explicit human approval is required")
        reviewer_name = _require_text(reviewer, "reviewer")

        with self._lock:
            proposal = self.get_proposal(proposal_id)
            if proposal.state is not ProposalState.REVIEW_REQUIRED:
                raise ValueError(f"proposal cannot be approved from state {proposal.state}")
            evaluation = self._evaluations.get(proposal.proposal_id)
            if evaluation is None or evaluation.decision is not ProposalState.REVIEW_REQUIRED:
                raise ValueError("review-required evaluation is missing")
            timestamp = approved_at or datetime.now(UTC).isoformat()
            body = {
                "proposal_id": proposal.proposal_id,
                "proposal_hash": proposal.proposal_hash,
                "evaluation_hash": evaluation.evaluation_hash,
                "reviewer": reviewer_name,
                "approved_at": timestamp,
                "execution_authorized": False,
                "weight_update_authorized": False,
                "policy_update_authorized": False,
                "identity_update_authorized": False,
            }
            approval_hash = f"sha256:{sha256(_canonical_json(body).encode('utf-8')).hexdigest()}"
            approval = EvolutionApproval(
                proposal_id=proposal.proposal_id,
                proposal_hash=proposal.proposal_hash,
                evaluation_hash=evaluation.evaluation_hash,
                reviewer=reviewer_name,
                approved_at=timestamp,
                approval_hash=approval_hash,
            )
            self._approvals[proposal.proposal_id] = approval
            self._replace_proposal(replace(proposal, state=ProposalState.APPROVED))
            return approval

    def export_change_packet(self, proposal_id: str) -> dict[str, object]:
        with self._lock:
            proposal = self.get_proposal(proposal_id)
            if proposal.state is not ProposalState.APPROVED:
                raise PermissionError("proposal must be approved before export")
            evaluation = self._evaluations[proposal.proposal_id]
            approval = self._approvals[proposal.proposal_id]
            packet = {
                "schema": "MKultra-Governed-Evolution/v0.4",
                "proposal": proposal.public_payload(),
                "evaluation": evaluation.public_payload(),
                "approval": approval.public_payload(),
                "execution_authorized": False,
                "operator_action_required": True,
                "allowed_next_step": "human-reviewed branch or pull request",
            }
            packet_hash = f"sha256:{sha256(_canonical_json(packet).encode('utf-8')).hexdigest()}"
            return {**packet, "packet_hash": packet_hash}

    def snapshot(self) -> tuple[EvolutionProposal, ...]:
        with self._lock:
            return tuple(self._proposals)

    def verify_proposal_chain(self) -> bool:
        with self._lock:
            previous_hash: str | None = None
            for expected_sequence, proposal in enumerate(self._proposals, start=1):
                if proposal.sequence != expected_sequence or proposal.previous_hash != previous_hash:
                    return False
                expected_hash = f"sha256:{sha256(_canonical_json(proposal.body()).encode('utf-8')).hexdigest()}"
                if proposal.proposal_hash != expected_hash:
                    return False
                previous_hash = proposal.proposal_hash
            return True

    def status(self) -> dict[str, object]:
        with self._lock:
            state_counts = {state.value: 0 for state in ProposalState}
            for proposal in self._proposals:
                state_counts[proposal.state.value] += 1
            return {
                "proposal_count": len(self._proposals),
                "evaluation_count": len(self._evaluations),
                "approval_count": len(self._approvals),
                "review_threshold": self.review_threshold,
                "proposal_chain_valid": self.verify_proposal_chain(),
                "state_counts": state_counts,
                "automatic_execution": False,
                "direct_weight_update": False,
                "direct_policy_update": False,
                "direct_identity_update": False,
            }

    def _replace_proposal(self, updated: EvolutionProposal) -> None:
        for index, current in enumerate(self._proposals):
            if current.proposal_id == updated.proposal_id:
                self._proposals[index] = updated
                return
        raise KeyError(updated.proposal_id)
