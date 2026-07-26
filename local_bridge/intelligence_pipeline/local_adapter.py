"""Map friendly local MirrorME payloads onto contract-shaped router request/session.

The hard-rule enforcers require full contract envelopes. Local Thin Line / MirrorME
experiments often send a shorter shape. When ``session.local_only`` is true (or the
request uses ``type`` instead of ``request_class``), this adapter fills a **stub**
authenticated envelope.

This does **not** grant production trust. It only enables integration testing.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any

ROUTER_AUDIENCE = "civilisation.one.global-intelligence-router"

TYPE_TO_CLASS = {
    "scientific": "scientific_job",
    "scientific_job": "scientific_job",
    "publication": "publication_candidate",
    "publication_candidate": "publication_candidate",
    "chat": "chat",
    "research_assist": "research_assist",
    "validate": "scientific_job",
}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")


def _hash_payload(obj: Any) -> str:
    raw = json.dumps(obj, sort_keys=True, default=str).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def is_friendly_payload(request: dict[str, Any] | None, session: dict[str, Any] | None) -> bool:
    request = request or {}
    session = session or {}
    if session.get("local_only") is True:
        return True
    if "type" in request and "request_class" not in request:
        return True
    if "actor_id" in session and "member_public_id" not in session:
        return True
    return False


def adapt_local_payload(
    request: dict[str, Any] | None,
    session: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return (contract_request, contract_session) for local stub use."""
    request = dict(request or {})
    session = dict(session or {})

    if not is_friendly_payload(request, session) and request.get("request_class") and session.get(
        "member_public_id"
    ):
        # Already contract-shaped
        return request, session

    now = _utc_now()
    member = (
        session.get("member_public_id")
        or session.get("actor_id")
        or "local-member"
    )
    session_id = session.get("session_id") or "mirrorme-local-session"
    request_id = request.get("request_id") or f"req_local_{int(now.timestamp())}"

    raw_type = str(request.get("type") or request.get("request_class") or "scientific")
    request_class = TYPE_TO_CLASS.get(raw_type, "scientific_job")
    if request.get("requested_action") == "validate" and request_class == "chat":
        request_class = "scientific_job"

    scopes = list(
        session.get("scopes")
        or ["route:chat", "route:scientific", "route:publication_candidate"]
    )
    # Local MK owner convenience scopes for stub only
    if session.get("actor_role") in {"MK", "mk", "scientific_publication_authority"}:
        for s in ("route:scientific", "route:publication_candidate"):
            if s not in scopes:
                scopes.append(s)

    adapted_session: dict[str, Any] = {
        "schema_version": "1.0.0",
        "session_id": session_id,
        "member_public_id": member,
        "node_id": session.get("node_id") or "mirrorme-local-node",
        "authenticator": session.get("authenticator") or "session_token",
        "scopes": scopes,
        "issued_at_utc": session.get("issued_at_utc") or _iso(now),
        "expires_at_utc": session.get("expires_at_utc") or _iso(now + timedelta(hours=2)),
        "audience": session.get("audience") or ROUTER_AUDIENCE,
        "revoked": False,
        "local_only": True,
        "actor_role": session.get("actor_role"),
        "stub_adapted": True,
    }

    inputs = request.get("inputs") or request.get("payload") or {}
    provenance = request.get("input_provenance")
    if not provenance:
        provenance = [
            {
                "source_class": "user_selected_context",
                "content_hash": _hash_payload(inputs),
                "description": request.get("objective") or "local scientific inputs",
            }
        ]

    consent = request.get("consent_flags") or {
        "allow_router": True,
        "allow_private_mkone": True,
        "allow_validation_report": True,
        "allow_mk_human_review": True,
        "allow_publication": False,
    }

    proof_value = (
        (request.get("client_proof") or {}).get("value")
        if isinstance(request.get("client_proof"), dict)
        else None
    ) or f"local-stub-token-{session_id}"

    adapted_request: dict[str, Any] = {
        "schema_version": "1.0.0",
        "request_id": request_id,
        "session_id": session_id,
        "member_public_id": member,
        "node_id": adapted_session["node_id"],
        "request_class": request_class,
        "issued_at_utc": request.get("issued_at_utc") or _iso(now),
        "consent_flags": consent,
        "client_proof": {
            "type": "bearer_session_token",
            "value": str(proof_value),
        },
        "payload": {
            "objective": request.get("objective"),
            "requested_action": request.get("requested_action") or "validate",
            "inputs": inputs,
            "input_provenance": provenance,
            # preserve friendly type for engine stub
            "friendly_type": raw_type,
        },
        "input_provenance": provenance,
        "stub_adapted": True,
        "local_only": True,
    }

    return adapted_request, adapted_session
