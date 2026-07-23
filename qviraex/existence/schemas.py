from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class LifecycleState(StrEnum):
    GENESIS = "GENESIS"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    RECOVERY = "RECOVERY"
    ARCHIVED = "ARCHIVED"
    INTEGRITY_FAILURE = "INTEGRITY_FAILURE"


class EpistemicClass(StrEnum):
    OBSERVATION = "observation"
    EVIDENCE = "evidence"
    INFERENCE = "inference"
    HYPOTHESIS = "hypothesis"
    SIMULATION = "simulation"
    PREFERENCE = "preference"
    GOAL = "goal"
    SYNTHETIC_CANDIDATE = "synthetic_candidate"


class PromotionState(StrEnum):
    GENERATED = "GENERATED"
    COMPARED = "COMPARED"
    SIMULATED = "SIMULATED"
    TESTED = "TESTED"
    DGREP_VERIFIED = "DGREP_VERIFIED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    APPROVED = "APPROVED"
    PERSISTED = "PERSISTED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class VerifiedIdentityContext:
    node_id: str
    capsule_id: str
    member_id: str
    genesis_hash: str
    key_fingerprint: str
    lifecycle_state: LifecycleState
    consent_active: bool
    verified_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def __post_init__(self) -> None:
        required = {
            "node_id": self.node_id,
            "capsule_id": self.capsule_id,
            "member_id": self.member_id,
            "genesis_hash": self.genesis_hash,
            "key_fingerprint": self.key_fingerprint,
        }
        for name, value in required.items():
            if not value.strip():
                raise ValueError(f"{name} must be non-empty")
        if self.lifecycle_state is not LifecycleState.ACTIVE:
            raise ValueError("identity lifecycle must be ACTIVE")
        if not self.consent_active:
            raise ValueError("active consent is required")


@dataclass(frozen=True)
class AuthorizedSession:
    session_id: str
    runtime_id: str
    operator: str
    node_id: str
    persistence_authorized: bool = False
    external_actions_authorized: bool = False

    def __post_init__(self) -> None:
        for name in ("session_id", "runtime_id", "operator", "node_id"):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} must be non-empty")


@dataclass(frozen=True)
class CognitiveSignal:
    signal_id: str
    signal_type: str
    node_id: str
    sequence: int
    payload: dict[str, Any]
    epistemic_class: EpistemicClass
    previous_hash: str | None
    signal_hash: str
    created_at: str


@dataclass(frozen=True)
class VerificationDecision:
    candidate_id: str
    state: PromotionState
    score: float
    reasons: tuple[str, ...]
    human_review_required: bool = True
