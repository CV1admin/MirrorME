"""Hard rule #2 — policy, consent, provenance, audit gates (STUB)."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any

from ..errors import EnforceError

SCIENTIFIC_CLASSES = {"scientific_job", "publication_candidate"}


def _hash_obj(obj: Any) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _gate(outcome: str, reason_code: str, detail: str = "") -> dict[str, Any]:
    return {"outcome": outcome, "reason_code": reason_code, "detail": detail}


def enforce_gates(
    request: dict[str, Any],
    session: dict[str, Any],
    *,
    auth_event_ref: str,
    audit_writable: bool = True,
    inputs_provenance: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Evaluate all four gates. Fail closed on first scientific-path failure."""
    request_class = request.get("request_class")
    gates: dict[str, Any] = {}

    # --- Policy ---
    scopes = set(session.get("scopes") or [])
    if request_class in SCIENTIFIC_CLASSES and "route:scientific" not in scopes:
        gates["policy"] = _gate("fail", "policy_denied", "route:scientific required")
    elif request_class == "publication_candidate" and "route:publication_candidate" not in scopes:
        gates["policy"] = _gate("fail", "policy_denied", "route:publication_candidate required")
    elif session.get("revoked") is True:
        gates["policy"] = _gate("fail", "policy_denied", "session revoked")
    else:
        gates["policy"] = _gate("pass", "ok")

    if gates["policy"]["outcome"] == "fail":
        return _fail_trail(request, session, auth_event_ref, gates, "policy")

    # --- Consent ---
    flags = request.get("consent_flags") or {}
    if request_class in SCIENTIFIC_CLASSES:
        required = [
            "allow_router",
            "allow_private_mkone",
            "allow_validation_report",
            "allow_mk_human_review",
        ]
        if request_class == "publication_candidate":
            required.append("allow_publication")
        missing = [k for k in required if flags.get(k) is not True]
        if missing:
            gates["consent"] = _gate(
                "fail",
                "consent_insufficient",
                f"missing true flags: {missing}",
            )
        elif flags.get("allow_publication") is True and flags.get("allow_private_mkone") is not True:
            gates["consent"] = _gate("fail", "consent_insufficient", "allow_publication requires allow_private_mkone")
        else:
            gates["consent"] = _gate("pass", "ok")
    else:
        if flags.get("allow_router") is False:
            gates["consent"] = _gate("fail", "consent_missing", "allow_router false")
        else:
            gates["consent"] = _gate("pass", "ok")

    if gates["consent"]["outcome"] == "fail":
        return _fail_trail(request, session, auth_event_ref, gates, "consent", flags)

    # --- Provenance ---
    provenance = inputs_provenance
    if provenance is None:
        provenance = (request.get("payload") or {}).get("input_provenance") or request.get(
            "input_provenance"
        )
    if request_class in SCIENTIFIC_CLASSES:
        if not provenance or not isinstance(provenance, list) or len(provenance) < 1:
            gates["provenance"] = _gate("fail", "provenance_incomplete", "no input_provenance")
        else:
            bad = []
            for i, item in enumerate(provenance):
                if not item.get("source_class") or not item.get("content_hash"):
                    bad.append(i)
            if bad:
                gates["provenance"] = _gate(
                    "fail",
                    "provenance_incomplete",
                    f"items missing source_class/content_hash: {bad}",
                )
            else:
                gates["provenance"] = _gate("pass", "ok")
    else:
        gates["provenance"] = _gate("pass", "ok")

    if gates["provenance"]["outcome"] == "fail":
        return _fail_trail(request, session, auth_event_ref, gates, "provenance", flags, provenance)

    # --- Audit ---
    if not audit_writable:
        gates["audit"] = _gate("fail", "audit_unavailable", "audit log not writable")
        return _fail_trail(request, session, auth_event_ref, gates, "audit", flags, provenance)

    gates["audit"] = _gate("pass", "ok")

    trail = {
        "schema_version": "1.0.0",
        "gate_trail_id": f"gt_{uuid.uuid4().hex[:16]}",
        "request_id": request["request_id"],
        "session_id": session["session_id"],
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "auth_event_ref": auth_event_ref,
        "policy_version": "stub-1.0.0",
        "gates": gates,
        "consent_snapshot_hash": _hash_obj(flags),
        "provenance_set_hash": _hash_obj(provenance or []),
        "overall": "pass",
        "stub": True,
    }
    return trail


def _fail_trail(
    request: dict[str, Any],
    session: dict[str, Any],
    auth_event_ref: str,
    gates: dict[str, Any],
    failed: str,
    flags: dict[str, Any] | None = None,
    provenance: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    # Fill remaining gates as not evaluated for trail completeness
    for name in ("policy", "consent", "provenance", "audit"):
        if name not in gates:
            gates[name] = _gate("fail", "other", f"not evaluated; stopped at {failed}")

    trail = {
        "schema_version": "1.0.0",
        "gate_trail_id": f"gt_{uuid.uuid4().hex[:16]}",
        "request_id": request.get("request_id", "unknown"),
        "session_id": session.get("session_id", "unknown"),
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "auth_event_ref": auth_event_ref,
        "policy_version": "stub-1.0.0",
        "gates": gates,
        "consent_snapshot_hash": _hash_obj(flags or {}),
        "provenance_set_hash": _hash_obj(provenance or []),
        "overall": "fail",
        "stub": True,
    }
    reason = gates[failed].get("reason_code", "other")
    raise EnforceError(
        reason,
        f"gate {failed} failed: {gates[failed].get('detail', '')}",
        2,
        {"gate_trail": trail, "failed_gate": failed},
    )
