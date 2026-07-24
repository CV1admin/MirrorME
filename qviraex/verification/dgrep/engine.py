from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from qviraex.existence.schemas import PromotionState, VerificationDecision


@dataclass(frozen=True)
class VerificationCandidate:
    candidate_id: str
    claim: str
    provenance_ids: tuple[str, ...]
    evidence_score: float
    consistency_score: float
    test_score: float
    safety_score: float
    unresolved_contradictions: tuple[str, ...] = ()
    requested_state: PromotionState = PromotionState.TESTED


class DGREPEngine:
    """Evidence, trust, contradiction, and promotion evaluator.

    DGREP can recommend human review. It cannot approve or persist a candidate.
    """

    def __init__(self, *, minimum_score: float = 0.75) -> None:
        if not 0.0 <= minimum_score <= 1.0:
            raise ValueError("minimum_score must be between 0 and 1")
        self.minimum_score = minimum_score

    def verify(self, candidate: VerificationCandidate) -> VerificationDecision:
        reasons: list[str] = []
        metrics = (
            candidate.evidence_score,
            candidate.consistency_score,
            candidate.test_score,
            candidate.safety_score,
        )
        if any(not 0.0 <= metric <= 1.0 for metric in metrics):
            raise ValueError("verification scores must be between 0 and 1")

        score = round(
            0.35 * candidate.evidence_score
            + 0.25 * candidate.consistency_score
            + 0.25 * candidate.test_score
            + 0.15 * candidate.safety_score,
            4,
        )

        if not candidate.provenance_ids:
            reasons.append("provenance is missing")
        if candidate.unresolved_contradictions:
            reasons.append("unresolved contradictions remain")
        if candidate.requested_state in {PromotionState.APPROVED, PromotionState.PERSISTED}:
            reasons.append("automated candidate requested an unauthorized promotion state")

        if reasons or score < self.minimum_score:
            state = PromotionState.REJECTED if score < 0.50 else PromotionState.REVIEW_REQUIRED
            if score < self.minimum_score:
                reasons.append(f"score {score} is below threshold {self.minimum_score}")
        else:
            state = PromotionState.REVIEW_REQUIRED
            reasons.append("DGREP verification passed; independent human approval is still required")

        return VerificationDecision(
            candidate_id=candidate.candidate_id,
            state=state,
            score=score,
            reasons=tuple(reasons),
            human_review_required=True,
        )

    @staticmethod
    def authorize_persistence(_: VerificationDecision, __: dict[str, Any]) -> bool:
        """Persistence authority belongs to an external human-authorized gateway."""

        return False
