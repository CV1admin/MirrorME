from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class DreamStatus(StrEnum):
    GENERATED = "GENERATED"
    SIMULATED = "SIMULATED"
    TESTED = "TESTED"
    REJECTED = "REJECTED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


@dataclass(frozen=True)
class DreamCandidate:
    candidate_id: str
    description: str
    assumptions: tuple[str, ...]
    inverse_test: str
    boundary_test: str
    null_test: str
    adversarial_test: str
    expected_gain: float
    risk: float
    cost: float


@dataclass(frozen=True)
class DreamEvaluation:
    candidate: DreamCandidate
    score: float
    closure_residual: float
    tests_passed: tuple[str, ...]
    tests_failed: tuple[str, ...]
    status: DreamStatus


CandidateGenerator = Callable[[dict[str, Any], int], tuple[DreamCandidate, ...]]
CandidateEvaluator = Callable[[DreamCandidate, dict[str, Any]], tuple[float, tuple[str, ...], tuple[str, ...]]]


class DreamEngine:
    """Controlled offline reflection and candidate evaluation.

    The engine can generate and test proposals. It cannot modify model weights,
    policies, identity state, or durable memory.
    """

    def __init__(
        self,
        *,
        generator: CandidateGenerator,
        evaluator: CandidateEvaluator,
        maximum_candidates: int = 8,
        closure_threshold: float = 0.05,
    ) -> None:
        if not 3 <= maximum_candidates <= 32:
            raise ValueError("maximum_candidates must be between 3 and 32")
        self.generator = generator
        self.evaluator = evaluator
        self.maximum_candidates = maximum_candidates
        self.closure_threshold = closure_threshold

    def run(self, normalized_state: dict[str, Any]) -> tuple[DreamEvaluation, ...]:
        candidates = self.generator(dict(normalized_state), self.maximum_candidates)
        if len(candidates) < 3:
            raise ValueError("dream mode requires at least three materially different candidates")
        if len(candidates) > self.maximum_candidates:
            raise ValueError("generator exceeded candidate budget")
        if len({candidate.candidate_id for candidate in candidates}) != len(candidates):
            raise ValueError("candidate IDs must be unique")

        evaluations: list[DreamEvaluation] = []
        for candidate in candidates:
            measured_gain, passed, failed = self.evaluator(candidate, dict(normalized_state))
            closure_residual = abs(candidate.expected_gain - measured_gain)
            base_score = measured_gain - 0.5 * candidate.risk - 0.25 * candidate.cost
            score = round(max(0.0, min(1.0, base_score)), 4)

            if failed or score <= 0.0:
                status = DreamStatus.REJECTED
            elif closure_residual <= self.closure_threshold:
                status = DreamStatus.REVIEW_REQUIRED
            else:
                status = DreamStatus.TESTED

            evaluations.append(
                DreamEvaluation(
                    candidate=candidate,
                    score=score,
                    closure_residual=round(closure_residual, 6),
                    tests_passed=passed,
                    tests_failed=failed,
                    status=status,
                )
            )
        return tuple(sorted(evaluations, key=lambda item: item.score, reverse=True))

    @staticmethod
    def promotion_authorized(_: DreamEvaluation) -> bool:
        """Dream Mode never authorizes its own persistence or deployment."""

        return False
