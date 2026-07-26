"""Hard rule #1 — authentication required before routing (STUB)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..errors import EnforceError

ROUTER_AUDIENCE = "civilisation.one.global-intelligence-router"
SCIENTIFIC_CLASSES = {"scientific_job", "publication_candidate"}
CLASS_SCOPES = {
    "chat": {"route:chat"},
    "research_assist": {"route:chat"},
    "scientific_job": {"route:scientific"},
    "publication_candidate": {"route:scientific", "route:publication_candidate"},
    "admin_ops": {"route:admin_ops"},
}


def _parse_utc(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value)


def enforce_auth(
    request: dict[str, Any],
    session: dict[str, Any] | None,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Fail closed if request/session are not authenticated for the router.

    STUB: verifies presence, audience, expiry, scopes, and non-empty proof.
    Does not verify cryptographic signatures.
    """
    now = now or datetime.now(timezone.utc)

    if not request:
        raise EnforceError("auth_missing", "router request missing", 1)
    if not session:
        raise EnforceError("auth_missing", "session missing", 1)

    if session.get("audience") != ROUTER_AUDIENCE:
        raise EnforceError("auth_invalid", "session audience mismatch", 1)
    if session.get("revoked") is True:
        raise EnforceError("auth_invalid", "session revoked", 1)

    expires = session.get("expires_at_utc")
    if not expires:
        raise EnforceError("auth_invalid", "session missing expires_at_utc", 1)
    if _parse_utc(str(expires)) <= now:
        raise EnforceError("auth_invalid", "session expired", 1)

    required = ("request_id", "session_id", "member_public_id", "request_class", "client_proof")
    for key in required:
        if not request.get(key):
            raise EnforceError("auth_missing", f"request missing {key}", 1, {"field": key})

    if request.get("session_id") != session.get("session_id"):
        raise EnforceError("auth_invalid", "session_id mismatch", 1)
    if request.get("member_public_id") != session.get("member_public_id"):
        raise EnforceError("auth_invalid", "member_public_id mismatch", 1)

    proof = request.get("client_proof") or {}
    if not isinstance(proof, dict) or not proof.get("type") or not proof.get("value"):
        raise EnforceError("auth_proof_failed", "client_proof incomplete", 1)

    # STUB integrity: reject obviously empty / placeholder proofs
    value = str(proof["value"]).strip()
    if len(value) < 8 or value.lower() in {"unsigned", "none", "null", "placeholder"}:
        raise EnforceError("auth_proof_failed", "client_proof not acceptable (stub)", 1)

    request_class = request["request_class"]
    needed = CLASS_SCOPES.get(request_class)
    if not needed:
        raise EnforceError("auth_invalid", f"unknown request_class {request_class}", 1)

    scopes = set(session.get("scopes") or [])
    if not needed.issubset(scopes):
        raise EnforceError(
            "authz_insufficient_scope",
            f"session scopes {sorted(scopes)} missing {sorted(needed - scopes)}",
            1,
            {"needed": sorted(needed), "have": sorted(scopes)},
        )

    if request_class in SCIENTIFIC_CLASSES and not request.get("consent_flags"):
        raise EnforceError(
            "auth_invalid",
            "scientific request_class requires consent_flags (envelope rule)",
            1,
        )

    return {
        "outcome": "auth_ok",
        "hard_rule": 1,
        "request_id": request["request_id"],
        "session_id": session["session_id"],
        "member_public_id": session["member_public_id"],
        "request_class": request_class,
        "stub": True,
        "note": "STUB: cryptographic proof verification not implemented",
    }
