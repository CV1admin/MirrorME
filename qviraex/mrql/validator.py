from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .ast import RitualDocument, SequenceBlock


class MRQLValidationError(ValueError):
    pass


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    issues: tuple[str, ...] = ()


class MRQLValidator:
    def __init__(self, schema_path: str | Path | None = None) -> None:
        self.schema_path = Path(schema_path) if schema_path is not None else None

    def validate(self, ritual: RitualDocument) -> ValidationResult:
        issues: list[str] = []
        if not ritual.name:
            issues.append("ritual name is required")
        if not ritual.version:
            issues.append("ritual version is required")
        if ritual.metadata is None:
            issues.append("metadata block is required")
        if ritual.sequence is None:
            issues.append("sequence block is required")
        if ritual.field is None:
            issues.append("field block is required")

        if ritual.sequence is not None and not isinstance(ritual.sequence, SequenceBlock):
            issues.append("sequence block has an invalid type")

        return ValidationResult(valid=not issues, issues=tuple(issues))

    def ensure_valid(self, ritual: RitualDocument) -> None:
        result = self.validate(ritual)
        if not result.valid:
            raise MRQLValidationError("; ".join(result.issues))