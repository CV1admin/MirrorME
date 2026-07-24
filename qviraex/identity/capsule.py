from __future__ import annotations

import json
import re
from collections.abc import Callable
from hashlib import sha256
from typing import Any

from qviraex.existence.schemas import LifecycleState, VerifiedIdentityContext


class IdentityCapsuleError(RuntimeError):
    pass


_SHA256_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
_NODE_ID_PATTERN = re.compile(r"^did:cv1:[A-Za-z0-9._:-]+$")


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


def _require_string(capsule: dict[str, Any], field: str) -> str:
    value = capsule.get(field)
    if not isinstance(value, str) or not value.strip():
        raise IdentityCapsuleError(f"{field} must be a non-empty string")
    return value


def _require_sha256(value: str, field: str) -> str:
    if _SHA256_PATTERN.fullmatch(value) is None:
        raise IdentityCapsuleError(
            f"{field} must use lowercase sha256:<64 hexadecimal characters>"
        )
    return value


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
        if not isinstance(capsule, dict):
            raise IdentityCapsuleError("capsule must be a JSON object")

        missing = sorted(self.REQUIRED_FIELDS.difference(capsule))
        if missing:
            raise IdentityCapsuleError(f"missing capsule fields: {missing}")

        expected_hash = _require_sha256(expected_document_hash, "expected_document_hash")
        member_id = _require_string(capsule, "member_id")
        node_id = _require_string(capsule, "node_id")
        capsule_id = _require_sha256(
            _require_string(capsule, "capsule_id"),
            "capsule_id",
        )
        genesis_hash = _require_sha256(
            _require_string(capsule, "genesis_hash"),
            "genesis_hash",
        )
        key_fingerprint = _require_sha256(
            _require_string(capsule, "root_key_fingerprint"),
            "root_key_fingerprint",
        )
        lifecycle_value = _require_string(capsule, "lifecycle_state")

        if _NODE_ID_PATTERN.fullmatch(node_id) is None:
            raise IdentityCapsuleError("node_id must use the did:cv1 scheme")

        consent_active = capsule["consent_active"]
        if type(consent_active) is not bool:
            raise IdentityCapsuleError("consent_active must be a JSON boolean")

        computed = capsule_hash(capsule)
        if computed != expected_hash:
            raise IdentityCapsuleError("capsule commitment hash mismatch")

        if capsule_id != expected_hash:
            raise IdentityCapsuleError("capsule_id must equal immutable commitment hash")

        if self._signature_verifier is None:
            raise IdentityCapsuleError("signature verifier is required")
        signature_result = self._signature_verifier(capsule)
        if type(signature_result) is not bool or not signature_result:
            raise IdentityCapsuleError("capsule signature verification failed")

        try:
            lifecycle = LifecycleState(lifecycle_value)
        except ValueError as exc:
            raise IdentityCapsuleError("unsupported lifecycle state") from exc

        return VerifiedIdentityContext(
            node_id=node_id,
            capsule_id=capsule_id,
            member_id=member_id,
            genesis_hash=genesis_hash,
            key_fingerprint=key_fingerprint,
            lifecycle_state=lifecycle,
            consent_active=consent_active,
        )
