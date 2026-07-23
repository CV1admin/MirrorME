from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from math import isfinite
from typing import Any


_SHA256_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
_NODE_ID_PATTERN = re.compile(r"^did:cv1:[A-Za-z0-9._:-]+$")


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


def _require_non_empty(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value


def _require_node_id(value: object, field_name: str = "node_id") -> str:
    text = _require_non_empty(value, field_name)
    if _NODE_ID_PATTERN.fullmatch(text) is None:
        raise ValueError(f"{field_name} must use the did:cv1 scheme")
    return text


def _require_sha256(value: object, field_name: str) -> str:
    text = _require_non_empty(value, field_name)
    if _SHA256_PATTERN.fullmatch(text) is None:
        raise ValueError(
            f"{field_name} must use lowercase sha256:<64 hexadecimal characters>"
        )
    return text


def _require_bool(value: object, field_name: str) -> bool:
    if type(value) is not bool:
        raise TypeError(f"{field_name} must be a boolean")
    return value


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
        _require_node_id(self.node_id)
        _require_sha256(self.capsule_id, "capsule_id")
        _require_non_empty(self.member_id, "member_id")
        _require_sha256(self.genesis_hash, "genesis_hash")
        _require_sha256(self.key_fingerprint, "key_fingerprint")
        _require_non_empty(self.verified_at, "verified_at")
        if not isinstance(self.lifecycle_state, LifecycleState):
            raise TypeError("lifecycle_state must be a LifecycleState")
        if self.lifecycle_state is not LifecycleState.ACTIVE:
            raise ValueError("identity lifecycle must be ACTIVE")
        if not _require_bool(self.consent_active, "consent_active"):
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
        _require_non_empty(self.session_id, "session_id")
        _require_non_empty(self.runtime_id, "runtime_id")
        _require_non_empty(self.operator, "operator")
        _require_node_id(self.node_id)
        _require_bool(self.persistence_authorized, "persistence_authorized")
        _require_bool(self.external_actions_authorized, "external_actions_authorized")


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

    def __post_init__(self) -> None:
        _require_non_empty(self.signal_id, "signal_id")
        _require_non_empty(self.signal_type, "signal_type")
        _require_node_id(self.node_id)
        if isinstance(self.sequence, bool) or not isinstance(self.sequence, int) or self.sequence < 1:
            raise ValueError("sequence must be a positive integer")
        if not isinstance(self.payload, dict):
            raise TypeError("payload must be a dictionary")
        if not isinstance(self.epistemic_class, EpistemicClass):
            raise TypeError("epistemic_class must be an EpistemicClass")
        if self.previous_hash is not None:
            _require_sha256(self.previous_hash, "previous_hash")
        _require_sha256(self.signal_hash, "signal_hash")
        _require_non_empty(self.created_at, "created_at")


@dataclass(frozen=True)
class VerificationDecision:
    candidate_id: str
    state: PromotionState
    score: float
    reasons: tuple[str, ...]
    human_review_required: bool = True

    def __post_init__(self) -> None:
        _require_non_empty(self.candidate_id, "candidate_id")
        if not isinstance(self.state, PromotionState):
            raise TypeError("state must be a PromotionState")
        if isinstance(self.score, bool) or not isinstance(self.score, (int, float)):
            raise TypeError("score must be numeric")
        if not isfinite(float(self.score)) or not 0.0 <= self.score <= 1.0:
            raise ValueError("score must be finite and between 0 and 1")
        if any(not isinstance(reason, str) or not reason.strip() for reason in self.reasons):
            raise ValueError("reasons must contain non-empty strings")
        _require_bool(self.human_review_required, "human_review_required")
