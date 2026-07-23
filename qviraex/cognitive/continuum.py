from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
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
        if capacity < 4:
            raise ValueError("capacity must be at least 4")
        self.signal_bus = signal_bus
        self.capacity = capacity
        self.spark_ttl_seconds = spark_ttl_seconds
        self._memory: Deque[ShortMemoryItem] = deque(maxlen=capacity)
        self._sparks: dict[str, InspirationSpark] = {}

    @property
    def short_memory(self) -> tuple[ShortMemoryItem, ...]:
        return tuple(self._memory)

    @property
    def sparks(self) -> tuple[InspirationSpark, ...]:
        self.expire_sparks()
        return tuple(self._sparks.values())

    def remember(
        self,
        *,
        content: str,
        tags: tuple[str, ...],
        epistemic_class: EpistemicClass,
        confidence: float,
    ) -> ShortMemoryItem:
        if not content.strip():
            raise ValueError("content must be non-empty")
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")

        item = ShortMemoryItem(
            item_id=str(uuid4()),
            content=content,
            tags=tuple(sorted({tag.strip().lower() for tag in tags if tag.strip()})),
            epistemic_class=epistemic_class,
            confidence=confidence,
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

    def detect_pattern(self, *, minimum_occurrences: int = 2) -> tuple[str, ...]:
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
        if len(self._memory) < 2:
            return None
        left, right = self._memory[-2], self._memory[-1]
        shared = tuple(sorted(set(left.tags).intersection(right.tags)))
        if not shared:
            return None

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

    def expire_sparks(self) -> int:
        now = datetime.now(UTC)
        expired = [
            spark_id
            for spark_id, spark in self._sparks.items()
            if datetime.fromisoformat(spark.expires_at) <= now
        ]
        for spark_id in expired:
            del self._sparks[spark_id]
        return len(expired)
