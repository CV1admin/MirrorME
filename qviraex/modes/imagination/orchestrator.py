from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from statistics import mean
from typing import Any


class BranchRole(StrEnum):
    CONSTRUCTIVE_ARCHITECT = "constructive_architect"
    SCIENTIFIC_SKEPTIC = "scientific_skeptic"
    COUNTERFACTUAL_MIRROR = "counterfactual_mirror"
    BOUNDARY_EXPLORER = "boundary_explorer"
    SYSTEMS_ENGINEER = "systems_engineer"
    ADVERSARIAL_AUDITOR = "adversarial_auditor"
    NOVELTY_EXPLORER = "novelty_explorer"
    MINIMALIST = "minimalist"


@dataclass(frozen=True)
class BranchCandidate:
    branch_id: str
    role: BranchRole
    central_claim: str
    mechanism: str
    assumptions: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    predictions: tuple[str, ...]
    failure_conditions: tuple[str, ...]
    confidence: float
    metrics: dict[str, float]

    def __post_init__(self) -> None:
        if not self.central_claim.strip() or not self.mechanism.strip():
            raise ValueError("candidate claim and mechanism must be non-empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class ComparisonResult:
    candidates: tuple[BranchCandidate, ...]
    scores: dict[str, float]
    diversity: float
    pareto_branch_ids: tuple[str, ...]
    unresolved_conflicts: tuple[str, ...]


CandidateRunner = Callable[[BranchRole, str, dict[str, Any]], BranchCandidate]


class ImaginationOrchestrator:
    """Run isolated idea branches and compare structured summaries.

    The orchestrator exchanges candidate records, not private reasoning traces.
    Provider-backed real parallelism is supplied through the runner callback.
    """

    DEFAULT_ROLES = (
        BranchRole.CONSTRUCTIVE_ARCHITECT,
        BranchRole.SCIENTIFIC_SKEPTIC,
        BranchRole.COUNTERFACTUAL_MIRROR,
        BranchRole.BOUNDARY_EXPLORER,
        BranchRole.SYSTEMS_ENGINEER,
        BranchRole.ADVERSARIAL_AUDITOR,
    )

    def __init__(
        self,
        *,
        runner: CandidateRunner,
        roles: tuple[BranchRole, ...] = DEFAULT_ROLES,
        minimum_diversity: float = 0.20,
    ) -> None:
        if len(roles) < 4:
            raise ValueError("imagination mode requires at least four branches")
        if len(set(roles)) != len(roles):
            raise ValueError("branch roles must be unique")
        self.runner = runner
        self.roles = roles
        self.minimum_diversity = minimum_diversity

    def run(self, *, objective: str, shared_context: dict[str, Any]) -> ComparisonResult:
        if not objective.strip():
            raise ValueError("objective must be non-empty")

        candidates = tuple(
            self.runner(role, objective, dict(shared_context))
            for role in self.roles
        )
        branch_ids = [candidate.branch_id for candidate in candidates]
        if len(set(branch_ids)) != len(branch_ids):
            raise ValueError("runner returned duplicate branch IDs")

        diversity = self._mean_diversity(candidates)
        scores = {
            candidate.branch_id: self._score(candidate)
            for candidate in candidates
        }
        pareto_ids = self._pareto_front(candidates)
        conflicts = self._find_conflicts(candidates)

        return ComparisonResult(
            candidates=candidates,
            scores=scores,
            diversity=diversity,
            pareto_branch_ids=pareto_ids,
            unresolved_conflicts=conflicts,
        )

    def diversity_gate_passes(self, result: ComparisonResult) -> bool:
        return result.diversity >= self.minimum_diversity

    @staticmethod
    def _score(candidate: BranchCandidate) -> float:
        metric = candidate.metrics
        positive = (
            metric.get("evidence", 0.0)
            + metric.get("consistency", 0.0)
            + metric.get("feasibility", 0.0)
            + metric.get("testability", 0.0)
            + metric.get("novelty", 0.0)
        ) / 5.0
        penalty = (
            metric.get("risk", 0.0)
            + metric.get("cost", 0.0)
            + metric.get("assumption_burden", 0.0)
        ) / 3.0
        return round(max(0.0, min(1.0, 0.75 * positive + 0.25 * (1.0 - penalty))), 4)

    @staticmethod
    def _tokens(candidate: BranchCandidate) -> set[str]:
        text = " ".join((candidate.central_claim, candidate.mechanism, *candidate.assumptions))
        return {token.strip(".,:;()[]{}\"'").lower() for token in text.split() if token.strip()}

    def _mean_diversity(self, candidates: tuple[BranchCandidate, ...]) -> float:
        distances: list[float] = []
        for index, left in enumerate(candidates):
            left_tokens = self._tokens(left)
            for right in candidates[index + 1 :]:
                right_tokens = self._tokens(right)
                union = left_tokens | right_tokens
                similarity = len(left_tokens & right_tokens) / max(len(union), 1)
                distances.append(1.0 - similarity)
        return round(mean(distances), 4) if distances else 0.0

    @staticmethod
    def _dominates(left: BranchCandidate, right: BranchCandidate) -> bool:
        keys = ("evidence", "consistency", "feasibility", "testability")
        left_values = [left.metrics.get(key, 0.0) for key in keys]
        right_values = [right.metrics.get(key, 0.0) for key in keys]
        no_worse = all(a >= b for a, b in zip(left_values, right_values, strict=True))
        strictly_better = any(a > b for a, b in zip(left_values, right_values, strict=True))
        lower_or_equal_risk = left.metrics.get("risk", 1.0) <= right.metrics.get("risk", 1.0)
        return no_worse and strictly_better and lower_or_equal_risk

    def _pareto_front(self, candidates: tuple[BranchCandidate, ...]) -> tuple[str, ...]:
        survivors = []
        for candidate in candidates:
            if not any(
                self._dominates(other, candidate)
                for other in candidates
                if other.branch_id != candidate.branch_id
            ):
                survivors.append(candidate.branch_id)
        return tuple(survivors)

    @staticmethod
    def _find_conflicts(candidates: tuple[BranchCandidate, ...]) -> tuple[str, ...]:
        conflicts: list[str] = []
        for index, left in enumerate(candidates):
            left_failures = {item.lower() for item in left.failure_conditions}
            for right in candidates[index + 1 :]:
                if right.central_claim.lower() in left_failures or left.central_claim.lower() in {
                    item.lower() for item in right.failure_conditions
                }:
                    conflicts.append(f"{left.branch_id}<->{right.branch_id}")
        return tuple(conflicts)
