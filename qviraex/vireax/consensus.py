from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConsensusWeights:
    accuracy: float = 0.30
    evidence: float = 0.25
    coherence: float = 0.20
    usefulness: float = 0.15
    risk: float = 0.10


@dataclass(frozen=True)
class ConsensusScore:
    model: str
    role: str
    accuracy_score: float
    evidence_score: float
    coherence_score: float
    usefulness_score: float
    risk_score: float
    final_weight: float
    output: str


def score_response(
    *,
    model: str,
    role: str,
    output: str,
    accuracy_score: float,
    evidence_score: float,
    coherence_score: float,
    usefulness_score: float,
    risk_score: float,
    weights: ConsensusWeights | None = None,
) -> ConsensusScore:
    weights = weights or ConsensusWeights()
    final_weight = (
        weights.accuracy * accuracy_score
        + weights.evidence * evidence_score
        + weights.coherence * coherence_score
        + weights.usefulness * usefulness_score
        - weights.risk * risk_score
    )
    return ConsensusScore(
        model=model,
        role=role,
        accuracy_score=accuracy_score,
        evidence_score=evidence_score,
        coherence_score=coherence_score,
        usefulness_score=usefulness_score,
        risk_score=risk_score,
        final_weight=final_weight,
        output=output,
    )


def select_best_response(responses: list[ConsensusScore]) -> ConsensusScore | None:
    if not responses:
        return None
    return max(responses, key=lambda item: item.final_weight)