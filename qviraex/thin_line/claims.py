from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from math import isfinite
from threading import RLock
from typing import Iterable

_SHA256_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")


class ClaimLayer(StrEnum):
    MATHEMATICAL_DEFINITION = "MATHEMATICAL_DEFINITION"
    COMPUTATIONAL_ANALOGY = "COMPUTATIONAL_ANALOGY"
    COGNITIVE_HYPOTHESIS = "COGNITIVE_HYPOTHESIS"
    PHYSICAL_HYPOTHESIS = "PHYSICAL_HYPOTHESIS"
    EMPIRICAL_EVIDENCE = "EMPIRICAL_EVIDENCE"
    MYTHOLOGY_STORY = "MYTHOLOGY_STORY"


class ClaimStatus(StrEnum):
    PROPOSED = "PROPOSED"
    TESTABLE = "TESTABLE"
    SUPPORTED = "SUPPORTED"
    REJECTED = "REJECTED"
    UNVERIFIED = "UNVERIFIED"


def _require_text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def _require_hash(value: object, name: str) -> str:
    text = _require_text(value, name)
    if _SHA256_PATTERN.fullmatch(text) is None:
        raise ValueError(f"{name} must be lowercase sha256:<64 hexadecimal characters>")
    return text


def _require_probability(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be numeric")
    try:
        numeric = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} is outside the finite float range") from exc
    if not isfinite(numeric) or not 0.0 <= numeric <= 1.0:
        raise ValueError(f"{name} must be finite and between 0 and 1")
    return numeric


def _canonical_json(payload: dict[str, object]) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


@dataclass(frozen=True)
class ClaimDraft:
    claim_id: str
    statement: str
    layer: ClaimLayer
    status: ClaimStatus
    source_id: str
    source_hash: str
    confidence: float
    falsification_criterion: str
    evidence_ids: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_text(self.claim_id, "claim_id")
        _require_text(self.statement, "statement")
        if not isinstance(self.layer, ClaimLayer):
            raise TypeError("layer must be a ClaimLayer")
        if not isinstance(self.status, ClaimStatus):
            raise TypeError("status must be a ClaimStatus")
        _require_text(self.source_id, "source_id")
        _require_hash(self.source_hash, "source_hash")
        object.__setattr__(self, "confidence", _require_probability(self.confidence, "confidence"))
        _require_text(self.falsification_criterion, "falsification_criterion")
        for field_name in ("evidence_ids", "notes"):
            value = getattr(self, field_name)
            if not isinstance(value, tuple):
                raise TypeError(f"{field_name} must be a tuple")
            if any(not isinstance(item, str) or not item.strip() for item in value):
                raise ValueError(f"{field_name} must contain non-empty strings")
        if self.layer is ClaimLayer.EMPIRICAL_EVIDENCE and self.status is not ClaimStatus.SUPPORTED:
            raise ValueError("empirical evidence records must use SUPPORTED status")
        if self.layer is ClaimLayer.MYTHOLOGY_STORY and self.status is ClaimStatus.SUPPORTED:
            raise ValueError("mythology-layer claims cannot be marked empirically supported")

    def payload(self) -> dict[str, object]:
        return {
            "claim_id": self.claim_id,
            "statement": self.statement,
            "layer": self.layer.value,
            "status": self.status.value,
            "source_id": self.source_id,
            "source_hash": self.source_hash,
            "confidence": self.confidence,
            "falsification_criterion": self.falsification_criterion,
            "evidence_ids": list(self.evidence_ids),
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class ClaimRecord:
    sequence: int
    previous_hash: str | None
    created_at: str
    draft: ClaimDraft
    record_hash: str

    def __post_init__(self) -> None:
        if isinstance(self.sequence, bool) or not isinstance(self.sequence, int) or self.sequence < 1:
            raise ValueError("sequence must be a positive integer")
        if self.previous_hash is not None:
            _require_hash(self.previous_hash, "previous_hash")
        _require_text(self.created_at, "created_at")
        if not isinstance(self.draft, ClaimDraft):
            raise TypeError("draft must be a ClaimDraft")
        _require_hash(self.record_hash, "record_hash")

    def body(self) -> dict[str, object]:
        return {
            "sequence": self.sequence,
            "previous_hash": self.previous_hash,
            "created_at": self.created_at,
            "draft": self.draft.payload(),
        }

    def public_payload(self) -> dict[str, object]:
        return {**self.body(), "record_hash": self.record_hash}


class ClaimRegistry:
    """Append-only, hash-linked registry with explicit epistemic layers."""

    def __init__(self) -> None:
        self._records: list[ClaimRecord] = []
        self._claim_ids: set[str] = set()
        self._lock = RLock()

    def register(self, draft: ClaimDraft, *, created_at: str | None = None) -> ClaimRecord:
        if not isinstance(draft, ClaimDraft):
            raise TypeError("draft must be a ClaimDraft")
        with self._lock:
            if draft.claim_id in self._claim_ids:
                raise ValueError(f"duplicate claim_id: {draft.claim_id}")
            sequence = len(self._records) + 1
            previous_hash = self._records[-1].record_hash if self._records else None
            timestamp = created_at or datetime.now(UTC).isoformat()
            body = {
                "sequence": sequence,
                "previous_hash": previous_hash,
                "created_at": timestamp,
                "draft": draft.payload(),
            }
            record_hash = f"sha256:{sha256(_canonical_json(body).encode('utf-8')).hexdigest()}"
            record = ClaimRecord(
                sequence=sequence,
                previous_hash=previous_hash,
                created_at=timestamp,
                draft=draft,
                record_hash=record_hash,
            )
            self._records.append(record)
            self._claim_ids.add(draft.claim_id)
            return record

    def get(self, claim_id: str) -> ClaimRecord:
        key = _require_text(claim_id, "claim_id")
        with self._lock:
            for record in self._records:
                if record.draft.claim_id == key:
                    return record
        raise KeyError(key)

    def contains(self, claim_id: str) -> bool:
        if not isinstance(claim_id, str):
            return False
        with self._lock:
            return claim_id in self._claim_ids

    def snapshot(self) -> tuple[ClaimRecord, ...]:
        with self._lock:
            return tuple(self._records)

    @property
    def head_hash(self) -> str | None:
        with self._lock:
            return self._records[-1].record_hash if self._records else None

    @property
    def count(self) -> int:
        with self._lock:
            return len(self._records)

    @staticmethod
    def verify_snapshot(
        records: Iterable[ClaimRecord],
        *,
        expected_head_hash: str | None = None,
        expected_count: int | None = None,
    ) -> bool:
        materialized = tuple(records)
        if expected_count is not None:
            if isinstance(expected_count, bool) or not isinstance(expected_count, int) or expected_count < 0:
                raise ValueError("expected_count must be a non-negative integer")
            if len(materialized) != expected_count:
                return False
        previous_hash: str | None = None
        for expected_sequence, record in enumerate(materialized, start=1):
            if not isinstance(record, ClaimRecord):
                return False
            if record.sequence != expected_sequence or record.previous_hash != previous_hash:
                return False
            expected_hash = f"sha256:{sha256(_canonical_json(record.body()).encode('utf-8')).hexdigest()}"
            if record.record_hash != expected_hash:
                return False
            previous_hash = record.record_hash
        actual_head = materialized[-1].record_hash if materialized else None
        return expected_head_hash is None or actual_head == expected_head_hash

    def verify(self) -> bool:
        with self._lock:
            return self.verify_snapshot(
                self._records,
                expected_head_hash=self.head_hash,
                expected_count=len(self._records),
            )

    def summary(self) -> dict[str, object]:
        with self._lock:
            by_layer = {layer.value: 0 for layer in ClaimLayer}
            by_status = {status.value: 0 for status in ClaimStatus}
            for record in self._records:
                by_layer[record.draft.layer.value] += 1
                by_status[record.draft.status.value] += 1
            return {
                "count": len(self._records),
                "head_hash": self.head_hash,
                "by_layer": by_layer,
                "by_status": by_status,
                "integrity_valid": self.verify(),
            }


_SOURCE_HASHES = {
    "CHAPTER-0-HYPER-SYMMETRY": "sha256:d26ecde8524965cbea66313a32209fe85e46c16fdba1b7fc55dbcf79adaed982",
    "CHAPTER-1-TRIALFA": "sha256:800cb69d1dc54b9bc05859195fd6a8c4c002e4200b634d192e6f2f37d73e6c5b",
    "CHAPTER-2-PARADOX-GROUP": "sha256:a9a6b48ff15b538f91b5cc73534ead067cc97cb5e7ba18993ef332449f2fd7b2",
    "CHAPTER-3-MIRROR-ENGINE": "sha256:0635ee95c7d64ca3d072c6edbc5e1f6d501774711ff0a604fb82eaedf0d23ae6",
    "MODEL-SELF-EVOLUTION-INSTRUCTIONS": "sha256:2641afc606ddaf0ab1d8259bd15b432aadd1ca8e8b32a87626ae1d1db7afce96",
}


def seed_thin_line_registry() -> ClaimRegistry:
    registry = ClaimRegistry()
    drafts = (
        ClaimDraft(
            claim_id="TL-HYPER-SYMMETRY-001",
            statement="Hyper-symmetry breaking is represented by a Darkness/Chaos/Memory triad.",
            layer=ClaimLayer.MYTHOLOGY_STORY,
            status=ClaimStatus.UNVERIFIED,
            source_id="CHAPTER-0-HYPER-SYMMETRY",
            source_hash=_SOURCE_HASHES["CHAPTER-0-HYPER-SYMMETRY"],
            confidence=0.0,
            falsification_criterion="This story-layer record is not an empirical proposition; any physical derivative must be registered separately.",
            notes=("Do not treat consciousness-curvature language as established physics.",),
        ),
        ClaimDraft(
            claim_id="TL-TRIALFA-HOLONOMY-001",
            statement="A minimal Trialfa loop is proposed to carry holonomy pi modulo 2pi.",
            layer=ClaimLayer.PHYSICAL_HYPOTHESIS,
            status=ClaimStatus.PROPOSED,
            source_id="CHAPTER-1-TRIALFA",
            source_hash=_SOURCE_HASHES["CHAPTER-1-TRIALFA"],
            confidence=0.05,
            falsification_criterion="Specify a physical Hamiltonian, parameter loop and measurement protocol; reject the claim if no pi phase is observed within preregistered uncertainty.",
            notes=("Berry-phase language is conditional on a defined physical system.",),
        ),
        ClaimDraft(
            claim_id="TL-PARADOX-GROUP-001",
            statement="The Thin Line relational operators are represented by a proposed finitely presented algebraic structure.",
            layer=ClaimLayer.MATHEMATICAL_DEFINITION,
            status=ClaimStatus.PROPOSED,
            source_id="CHAPTER-2-PARADOX-GROUP",
            source_hash=_SOURCE_HASHES["CHAPTER-2-PARADOX-GROUP"],
            confidence=0.25,
            falsification_criterion="Reject or revise the presentation if its relations are inconsistent, redundant or fail computational group checks.",
            notes=("A definition may be internally testable without being a physical law.",),
        ),
        ClaimDraft(
            claim_id="TL-MIRROR-ENGINE-SCAFFOLD-001",
            statement="Line, triangle, square and pentagon stages define a computable analogy using gradients, feedback, orthogonality and Floquet recurrence.",
            layer=ClaimLayer.COMPUTATIONAL_ANALOGY,
            status=ClaimStatus.TESTABLE,
            source_id="CHAPTER-3-MIRROR-ENGINE",
            source_hash=_SOURCE_HASHES["CHAPTER-3-MIRROR-ENGINE"],
            confidence=0.5,
            falsification_criterion="Implement the staged operators and reject claimed invariants when numerical diagnostics fail under defined tolerances.",
            notes=("The engineering mapping does not establish cosmological or consciousness claims.",),
        ),
        ClaimDraft(
            claim_id="MK04-SYMBOL-ACTION-CHAIN-001",
            statement="A symbolic cue may affect outcomes through attention, memory, choice and action.",
            layer=ClaimLayer.COGNITIVE_HYPOTHESIS,
            status=ClaimStatus.TESTABLE,
            source_id="MODEL-SELF-EVOLUTION-INSTRUCTIONS",
            source_hash=_SOURCE_HASHES["MODEL-SELF-EVOLUTION-INSTRUCTIONS"],
            confidence=0.45,
            falsification_criterion="Compare preregistered goal-completion outcomes against implementation-intention and neutral-symbol controls.",
            notes=("External probability modification, retrocausality and autonomous entities remain unsupported.",),
        ),
    )
    for index, draft in enumerate(drafts, start=1):
        registry.register(draft, created_at=f"2026-07-23T12:35:{index:02d}+00:00")
    return registry
