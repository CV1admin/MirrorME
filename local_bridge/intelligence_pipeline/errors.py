"""Typed failure codes for hard-rule enforcers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class EnforceError(Exception):
    code: str
    message: str
    hard_rule: int
    details: dict[str, Any] | None = None

    def __str__(self) -> str:
        return f"[hard_rule={self.hard_rule}] {self.code}: {self.message}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "hard_rule": self.hard_rule,
            "details": self.details or {},
        }
