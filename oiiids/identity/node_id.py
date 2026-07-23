from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import base64
import re


_NODE_ID_PREFIX = "nodeid:cv1:"
_NODE_ID_RE = re.compile(r"^nodeid:cv1:[a-z2-7]{52}$")


@dataclass(frozen=True, slots=True)
class NodeID:
    """Stable Civilisation.One node identifier derived from public-key bytes.

    NodeID is an identifier, not an authorization grant. Authorization must be
    evaluated independently using a verified principal and node registry state.
    """

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not _NODE_ID_RE.fullmatch(normalized):
            raise ValueError("invalid NodeID format")
        object.__setattr__(self, "value", normalized)

    @classmethod
    def from_public_key(cls, public_key: bytes) -> "NodeID":
        if len(public_key) != 32:
            raise ValueError("Ed25519 public key must contain exactly 32 bytes")
        digest = sha256(public_key).digest()
        encoded = base64.b32encode(digest).decode("ascii").rstrip("=").lower()
        return cls(f"{_NODE_ID_PREFIX}{encoded}")

    @classmethod
    def parse(cls, value: str) -> "NodeID":
        return cls(value)

    def __str__(self) -> str:
        return self.value
