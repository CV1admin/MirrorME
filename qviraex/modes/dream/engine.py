from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from math import isfinite
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

    def __post_init__(self) -> None:
        required_strings = {
            "candidate_id": self.candidate_id,
            "description": self.description,
            "inverse_test": self.inverse_test,
            "boundary_test": self.boundary_test,
            "null_test": self.null_test,
            "adversarial_test": self.adversarial_test,
        }
        for name, value in required_strings.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be non-empty")
        if any(not isinstance(value, str) or not value.strip() for value in self.assumptions):
            raise ValueError("assumptions must contain non-empty strings")
        for name in ("expected_gain", "risk", "cost"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be numeric")
            numeric = float(value)
            if not isfinite(numeric) or not 0.0 <= numeric <= 1.0:
                raise ValueError(f"{name} must be finite and between 0 and 1")


@dataclass(frozen=True)
class DreamEvaluation:
    candidate: DreamCandidate
    score: float
    closure_residual: float
    tests_passed: tuple[str, ...]
    tests_failed: tuple[str, ...]
    status: DreamStatus


CandidateGenerator = Callable[[dict[str, Any], int], tuple[DreamCandidate, ...]]
CandidateEvaluator = Callable[
    [DreamCandidate, dict[str, Any]],
    tuple[float, tuple[str, ...], tuple[str, ...]],
]


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
        if not isfinite(float(closure_threshold)) or not 0.0 <= closure_threshold <= 1.0:
            raise ValueError("closure_threshold must be finite and between 0 and 1")
        self.generator = generator
        self.evaluator = evaluator
        self.maximum_candidates = maximum_candidates
        self.closure_threshold = closure_threshold

    def run(self, normalized_state: dict[str, Any]) -> tuple[DreamEvaluation, ...]:
        candidates = self.generator(dict(normalized_state), self.maximum_candidates)
        if not isinstance(candidates, tuple):
            raise TypeError("dream generator must return a tuple")
        if any(not isinstance(candidate, DreamCandidate) for candidate in candidates):
            raise TypeError("dream generator must return DreamCandidate instances")
        if len(candidates) < 3:
            raise ValueError("dream mode requires at least three materially different candidates")
        if len(candidates) > self.maximum_candidates:
            raise ValueError("generator exceeded candidate budget")
        if len({candidate.candidate_id for candidate in candidates}) != len(candidates):
            raise ValueError("candidate IDs must be unique")

        evaluations: list[DreamEvaluation] = []
        for candidate in candidates:
            measured_gain, passed, failed = self.evaluator(candidate, dict(normalized_state))
            if isinstance(measured_gain, bool) or not isinstance(measured_gain, (int, float)):
                raise TypeError("measured gain must be numeric")
            measured_gain_value = float(measured_gain)
            if not isfinite(measured_gain_value) or not 0.0 <= measured_gain_value <= 1.0:
                raise ValueError("measured gain must be finite and between 0 and 1")
            if not isinstance(passed, tuple) or not isinstance(failed, tuple):
                raise TypeError("evaluator test results must be tuples")
            if any(not isinstance(item, str) or not item.strip() for item in (*passed, *failed)):
                raise ValueError("test result names must be non-empty strings")

            closure_residual = abs(candidate.expected_gain - measured_gain_value)
            base_score = measured_gain_value - 0.5 * candidate.risk - 0.25 * candidate.cost
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
