from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Block:
    name: str
    values: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MetadataBlock(Block):
    pass


@dataclass(frozen=True)
class FieldBlock(Block):
    pass


@dataclass(frozen=True)
class OperationBlock(Block):
    arguments: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SequenceBlock(Block):
    operations: tuple[OperationBlock, ...] = ()


@dataclass(frozen=True)
class RitualDocument:
    name: str
    version: str
    metadata: MetadataBlock | None = None
    constraints: Block | None = None
    field: FieldBlock | None = None
    sequence: SequenceBlock | None = None
    raw_text: str = ""