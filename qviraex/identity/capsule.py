from __future__ import annotations

import json
from collections.abc import Callable
from hashlib import sha256
from typing import Any

from qviraex.existence.schemas import LifecycleState, VerifiedIdentityContext


class IdentityCapsuleError(RuntimeError):
    pass


def canonical_json(data: dict[str, Any]) -> bytes:
    """Return deterministic UTF-8 JSON for content addressing.

    Production deployments should replace this compact implementation with a
    formally audited RFC 8785 JSON Canonicalization Scheme implementation.
    """

    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def capsule_commitment_payload(data: dict[str, Any]) -> dict[str, Any]:
    """Return the signed commitment body without circular envelope fields.

    ``capsule_id`` and ``signatures`` are envelope values derived from or made
    over this body. Including them in their own digest would create an
    impossible self-referential hash requirement.
    """

    return {
        key: value
        for key, value in data.items()
        if key not in {"capsule_id", "signatures"}
    }


def capsule_hash(data: dict[str, Any]) -> str:
    body = capsule_commitment_payload(data)
    return f"sha256:{sha256(canonical_json(body)).hexdigest()}"


class IdentityCapsuleVerifier:
    """Verify immutable capsule integrity and return an authority context.

    Signature verification is injected because the repository deliberately
    does not implement private-key handling or invent a trust root.
    """

    REQUIRED_FIELDS = {
        "member_id",
        "node_id",
        "capsule_id",
        "genesis_hash",
        "root_key_fingerprint",
        "lifecycle_state",
        "consent_active",
    }

    def __init__(
        self,
        signature_verifier: Callable[[dict[str, Any]], bool] | None = None,
    ) -> None:
        self._signature_verifier = signature_verifier

    def verify(
        self,
        capsule: dict[str, Any],
        *,
        expected_document_hash: str,
    ) -> VerifiedIdentityContext:
        missing = sorted(self.REQUIRED_FIELDS.difference(capsule))
        if missing:
            raise IdentityCapsuleError(f"missing capsule fields: {missing}")

        computed = capsule_hash(capsule)
        if computed != expected_document_hash:
            raise IdentityCapsuleError("capsule commitment hash mismatch")

        if capsule["capsule_id"] != expected_document_hash:
            raise IdentityCapsuleError("capsule_id must equal immutable commitment hash")

        declared_genesis = str(capsule["genesis_hash"])
        if not declared_genesis.startswith("sha256:"):
            raise IdentityCapsuleError("genesis_hash must be a sha256 multiform string")

        if self._signature_verifier is None:
            raise IdentityCapsuleError("signature verifier is required")
        if not self._signature_verifier(capsule):
            raise IdentityCapsuleError("capsule signature verification failed")

        try:
            lifecycle = LifecycleState(str(capsule["lifecycle_state"]))
        except ValueError as exc:
            raise IdentityCapsuleError("unsupported lifecycle state") from exc

        return VerifiedIdentityContext(
            node_id=str(capsule["node_id"]),
            capsule_id=str(capsule["capsule_id"]),
            member_id=str(capsule["member_id"]),
            genesis_hash=declared_genesis,
            key_fingerprint=str(capsule["root_key_fingerprint"]),
            lifecycle_state=lifecycle,
            consent_active=bool(capsule["consent_active"]),
        )
