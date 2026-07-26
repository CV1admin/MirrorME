"""End-to-end scientific pipeline stub enforcing hard rules #1–#5."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .enforce.auth import enforce_auth
from .enforce.gates import enforce_gates
from .enforce.mk_review import enforce_mk_review_required
from .enforce.publication import enforce_optional_publication
from .enforce.validation_report import enforce_validation_report_not_publication
from .errors import EnforceError


@dataclass
class PipelineResult:
    ok: bool
    stage: str
    data: dict[str, Any] = field(default_factory=dict)
    error: dict[str, Any] | None = None


def _stub_mkone_engine(request: dict[str, Any], gate_trail: dict[str, Any]) -> dict[str, Any]:
    """Private MKone scientific engine stub — produces a draft validation report."""
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "schema_version": "1.0.0",
        "validation_report_id": f"vr_{uuid.uuid4().hex[:16]}",
        "request_id": request["request_id"],
        "created_at_utc": now,
        "engine": {"name": "mkone-stub", "version": "0.0.0-stub"},
        "methods_summary": "STUB engine: no scientific computation performed.",
        "results_summary": "STUB results: pipeline enforcement path only.",
        "uncertainty_summary": "Not applicable — stub.",
        "input_provenance": (request.get("payload") or {}).get("input_provenance")
        or request.get("input_provenance")
        or [],
        "claims": [
            {
                "claim_id": "c1",
                "text": "Stub pipeline executed hard-rule enforcers only.",
                "classification": "engineering_observation",
            }
        ],
        "gate_trail_ref": gate_trail.get("gate_trail_id", ""),
        "recommended_review_actions": [
            "Do not treat as science",
            "Replace stub engine before real review",
        ],
        "publication_candidate": request.get("request_class") == "publication_candidate",
    }


def run_scientific_pipeline(
    *,
    request: dict[str, Any],
    session: dict[str, Any],
    mk_decision: dict[str, Any] | None = None,
    publication_request: dict[str, Any] | None = None,
    audit_writable: bool = True,
) -> PipelineResult:
    """Run #1 → #2 → stub MKone → #3 → #4 → optional #5."""
    try:
        auth = enforce_auth(request, session)
        trail = enforce_gates(
            request,
            session,
            auth_event_ref=f"auth:{auth['request_id']}",
            audit_writable=audit_writable,
        )
        raw_report = _stub_mkone_engine(request, trail)
        report = enforce_validation_report_not_publication(raw_report)

        want_pub = request.get("request_class") == "publication_candidate"
        try:
            review = enforce_mk_review_required(
                report,
                mk_decision,
                require_publication_approval=bool(publication_request),
            )
        except EnforceError as review_exc:
            if review_exc.code == "mk_review_pending":
                return PipelineResult(
                    ok=True,
                    stage="awaiting_mk_review",
                    data={
                        "auth": auth,
                        "gate_trail": trail,
                        "validation_report": report,
                        "mk_review": {
                            "outcome": "pending",
                            "hard_rule": 4,
                            "stub": True,
                        },
                        "publication": None,
                        "stub": True,
                    },
                )
            raise

        pub: dict[str, Any] | None = None
        if publication_request is not None:
            # Bind decision to live report ids for stub convenience
            decision = dict(mk_decision or {})
            decision.setdefault("validation_report_id", report["validation_report_id"])
            decision.setdefault("request_id", report["request_id"])
            pub = enforce_optional_publication(
                report=report,
                decision=decision,
                publication_request=publication_request,
                consent_flags=request.get("consent_flags"),
            )
        elif review.get("allows_optional_publication"):
            pub = {
                "status": "not_published",
                "reason": "no_publish_intent",
                "hard_rule": 5,
                "message": "approved_for_publication does not auto-publish",
                "stub": True,
            }

        return PipelineResult(
            ok=True,
            stage="complete",
            data={
                "auth": auth,
                "gate_trail": trail,
                "validation_report": report,
                "mk_review": review,
                "publication": pub,
                "stub": True,
            },
        )
    except EnforceError as exc:
        return PipelineResult(
            ok=False,
            stage=f"hard_rule_{exc.hard_rule}",
            error=exc.to_dict(),
            data=exc.details or {},
        )
