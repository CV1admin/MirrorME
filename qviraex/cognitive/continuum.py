from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from math import isfinite
from threading import RLock
from typing import Deque
from uuid import uuid4

from qviraex.cognitive.signal_bus import CognitiveSignalBus
from qviraex.existence.schemas import EpistemicClass


@dataclass(frozen=True)
class ShortMemoryItem:
    item_id: str
    content: str
    tags: tuple[str, ...]
    epistemic_class: EpistemicClass
    confidence: float
    created_at: str


@dataclass(frozen=True)
class InspirationSpark:
    spark_id: str
    source_item_ids: tuple[str, ...]
    candidate_idea: str
    shared_tags: tuple[str, ...]
    confidence: float
    expires_at: str


@dataclass(frozen=True)
class CognitiveContinuumSnapshot:
    memory: tuple[ShortMemoryItem, ...]
    sparks: tuple[tuple[str, InspirationSpark], ...]


class CognitiveContinuum:
    """Bounded runtime memory with non-persistent background signals.

    The class deliberately separates volatile memory and inspiration candidates
    from the durable identity continuum.
    """

    def __init__(
        self,
        *,
        signal_bus: CognitiveSignalBus,
        capacity: int = 128,
        spark_ttl_seconds: int = 3600,
    ) -> None:
        if isinstance(capacity, bool) or not isinstance(capacity, int) or capacity < 4:
            raise ValueError("capacity must be an integer of at least 4")
        if (
            isinstance(spark_ttl_seconds, bool)
            or not isinstance(spark_ttl_seconds, int)
            or spark_ttl_seconds <= 0
        ):
            raise ValueError("spark_ttl_seconds must be a positive integer")
        self.signal_bus = signal_bus
        self.capacity = capacity
        self.spark_ttl_seconds = spark_ttl_seconds
        self._memory: Deque[ShortMemoryItem] = deque(maxlen=capacity)
        self._sparks: dict[str, InspirationSpark] = {}
        self._lock = RLock()

    @property
    def short_memory(self) -> tuple[ShortMemoryItem, ...]:
        with self._lock:
            return tuple(self._memory)

    @property
    def sparks(self) -> tuple[InspirationSpark, ...]:
        with self._lock:
            self.expire_sparks()
            return tuple(self._sparks.values())

    @staticmethod
    def _coerce_confidence(value: object) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("confidence must be a finite number")
        try:
            result = float(value)
        except OverflowError as exc:
            raise ValueError("confidence is outside the finite float range") from exc
        if not isfinite(result) or not 0.0 <= result <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        return result

    def remember(
        self,
        *,
        content: str,
        tags: tuple[str, ...],
        epistemic_class: EpistemicClass,
        confidence: float,
    ) -> ShortMemoryItem:
        if not isinstance(content, str) or not content.strip():
            raise ValueError("content must be non-empty")
        if not isinstance(epistemic_class, EpistemicClass):
            raise TypeError("epistemic_class must be an EpistemicClass")
        confidence_value = self._coerce_confidence(confidence)
        if not isinstance(tags, tuple):
            raise TypeError("tags must be a tuple")
        if any(not isinstance(tag, str) for tag in tags):
            raise TypeError("all tags must be strings")

        with self._lock:
            memory_before = tuple(self._memory)
            signal_before = self.signal_bus._capture_state()
            try:
                item = ShortMemoryItem(
                    item_id=str(uuid4()),
                    content=content,
                    tags=tuple(sorted({tag.strip().lower() for tag in tags if tag.strip()})),
                    epistemic_class=epistemic_class,
                    confidence=confidence_value,
                    created_at=datetime.now(UTC).isoformat(),
                )
                self._memory.append(item)
                self.signal_bus.publish(
                    signal_type="mirrorme.short_memory.updated",
                    payload={
                        "item_id": item.item_id,
                        "memory_count": len(self._memory),
                        "persistent": False,
                    },
                    epistemic_class=epistemic_class,
                )
                return item
            except Exception:
                self._memory = deque(memory_before, maxlen=self.capacity)
                self.signal_bus._restore_state(signal_before)
                raise

    def detect_pattern(self, *, minimum_occurrences: int = 2) -> tuple[str, ...]:
        if (
            isinstance(minimum_occurrences, bool)
            or not isinstance(minimum_occurrences, int)
            or minimum_occurrences < 2
        ):
            raise ValueError("minimum_occurrences must be an integer of at least 2")
        with self._lock:
            counts = Counter(tag for item in self._memory for tag in item.tags)
            patterns = tuple(sorted(tag for tag, count in counts.items() if count >= minimum_occurrences))
            if patterns:
                self.signal_bus.publish(
                    signal_type="mirrorme.subconscious.pattern_detected",
                    payload={"patterns": patterns, "evidential": False},
                    epistemic_class=EpistemicClass.INFERENCE,
                )
            return patterns

    def generate_spark(self) -> InspirationSpark | None:
        with self._lock:
            if len(self._memory) < 2:
                return None
            left, right = self._memory[-2], self._memory[-1]
            shared = tuple(sorted(set(left.tags).intersection(right.tags)))
            if not shared:
                return None

            sparks_before = dict(self._sparks)
            signal_before = self.signal_bus._capture_state()
            try:
                confidence = min(left.confidence, right.confidence) * 0.75
                spark = InspirationSpark(
                    spark_id=str(uuid4()),
                    source_item_ids=(left.item_id, right.item_id),
                    candidate_idea=f"Explore relation between: {left.content} | {right.content}",
                    shared_tags=shared,
                    confidence=round(confidence, 4),
                    expires_at=(datetime.now(UTC) + timedelta(seconds=self.spark_ttl_seconds)).isoformat(),
                )
                self._sparks[spark.spark_id] = spark
                self.signal_bus.publish(
                    signal_type="mirrorme.inspiration.spark_generated",
                    payload={
                        "spark_id": spark.spark_id,
                        "source_item_ids": spark.source_item_ids,
                        "confidence": spark.confidence,
                        "persistent": False,
                    },
                    epistemic_class=EpistemicClass.HYPOTHESIS,
                )
                return spark
            except Exception:
                self._sparks = sparks_before
                self.signal_bus._restore_state(signal_before)
                raise

    def expire_sparks(self) -> int:
        with self._lock:
            now = datetime.now(UTC)
            expired = [
                spark_id
                for spark_id, spark in self._sparks.items()
                if datetime.fromisoformat(spark.expires_at) <= now
            ]
            for spark_id in expired:
                del self._sparks[spark_id]
            return len(expired)

    def _capture_state(self) -> CognitiveContinuumSnapshot:
        with self._lock:
            return CognitiveContinuumSnapshot(
                memory=tuple(self._memory),
                sparks=tuple(self._sparks.items()),
            )

    def _restore_state(self, snapshot: CognitiveContinuumSnapshot) -> None:
        if not isinstance(snapshot, CognitiveContinuumSnapshot):
            raise TypeError("snapshot must be a CognitiveContinuumSnapshot")
        with self._lock:
            self._memory = deque(snapshot.memory, maxlen=self.capacity)
            self._sparks = dict(snapshot.sparks)
