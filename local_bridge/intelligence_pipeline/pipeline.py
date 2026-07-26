"""End-to-end scientific pipeline stub enforcing hard rules #1–#5."""

from __future__ import annotations

import math
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from .enforce.auth import enforce_auth
from .enforce.gates import enforce_gates
from .enforce.mk_review import enforce_mk_review_required
from .enforce.publication import enforce_optional_publication
from .enforce.validation_report import enforce_validation_report_not_publication
from .errors import EnforceError
from .local_adapter import adapt_local_payload, is_friendly_payload


@dataclass
class PipelineResult:
    ok: bool
    stage: str
    data: dict[str, Any] = field(default_factory=dict)
    error: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _thin_line_stub(inputs: dict[str, Any]) -> dict[str, Any] | None:
    """Optional numeric check for Thin Line-style parameters (still a stub)."""
    params = inputs.get("parameters") if isinstance(inputs, dict) else None
    if not isinstance(params, dict):
        return None
    try:
        q_top = float(params["Q_top"])
        r = float(params["R"])
        e_sb = float(params["E_SB"])
        e_p = float(params["E_P"])
    except (KeyError, TypeError, ValueError):
        return None
    if e_p <= 0:
        return {
            "lambda_TL": None,
            "error": "E_P must be > 0",
            "classification": "engineering_observation",
        }
    # lambda_TL = Q_top**2 * R * log(1 + E_SB/E_P)
    lambda_tl = (q_top**2) * r * math.log(1.0 + (e_sb / e_p))
    return {
        "lambda_TL": lambda_tl,
        "formula": "lambda_TL = Q_top**2 * R * log(1 + E_SB/E_P)",
        "parameters_used": {
            "Q_top": q_top,
            "R": r,
            "E_SB": e_sb,
            "E_P": e_p,
        },
        "note": "STUB arithmetic only — not a scientific proof of Thin Line theory",
    }


def _stub_mkone_engine(request: dict[str, Any], gate_trail: dict[str, Any]) -> dict[str, Any]:
    """Private MKone scientific engine stub — produces a draft validation report."""
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    payload = request.get("payload") or {}
    inputs = payload.get("inputs") if isinstance(payload, dict) else {}
    if not inputs and isinstance(request.get("inputs"), dict):
        inputs = request["inputs"]

    thin = _thin_line_stub(inputs or {})
    claims: list[dict[str, Any]] = [
        {
            "claim_id": "c1",
            "text": "Stub pipeline executed hard-rule enforcers only.",
            "classification": "engineering_observation",
        }
    ]
    methods = "STUB engine: hard-rule path + optional arithmetic helpers."
    results = "STUB results: pipeline enforcement path only."
    uncertainty = "Not a complete scientific engine."

    if thin and thin.get("lambda_TL") is not None:
        claims.append(
            {
                "claim_id": "c_thin_line_stub",
                "text": (
                    f"Stub evaluation of declared Thin Line functional yields "
                    f"lambda_TL={thin['lambda_TL']:.6g} for supplied parameters. "
                    "This is arithmetic scaffolding, not empirical proof."
                ),
                "classification": "hypothesis",
            }
        )
        methods = (
            "STUB: evaluated supplied functional form "
            "lambda_TL = Q_top**2 * R * log(1 + E_SB/E_P) with user parameters."
        )
        results = (
            f"lambda_TL_stub={thin['lambda_TL']:.6g}; "
            "report is internal validation only (hard rule #3)."
        )
        uncertainty = (
            "Parameter provenance, domain validity, and theory status require "
            "Marek Kowalski review before any publication path."
        )
    elif thin and thin.get("error"):
        claims.append(
            {
                "claim_id": "c_thin_line_error",
                "text": f"Thin Line stub could not evaluate: {thin['error']}",
                "classification": "engineering_observation",
            }
        )
        results = f"STUB evaluation error: {thin['error']}"

    return {
        "schema_version": "1.0.0",
        "validation_report_id": f"vr_{uuid.uuid4().hex[:16]}",
        "request_id": request["request_id"],
        "created_at_utc": now,
        "engine": {"name": "mkone-stub", "version": "0.1.0-stub"},
        "methods_summary": methods,
        "results_summary": results,
        "uncertainty_summary": uncertainty,
        "input_provenance": (request.get("payload") or {}).get("input_provenance")
        or request.get("input_provenance")
        or [],
        "claims": claims,
        "gate_trail_ref": gate_trail.get("gate_trail_id", ""),
        "recommended_review_actions": [
            "Do not treat stub arithmetic as scientific proof",
            "Marek Kowalski manual review required for publication-class claims",
            "Replace stub engine before real review packages",
        ],
        "publication_candidate": request.get("request_class") == "publication_candidate",
        "stub_engine_detail": thin,
    }


def run_scientific_pipeline(
    *,
    request: dict[str, Any],
    session: dict[str, Any],
    mk_decision: dict[str, Any] | None = None,
    publication_request: dict[str, Any] | None = None,
    audit_writable: bool = True,
) -> PipelineResult:
    """Run #1 → #2 → stub MKone → #3 → #4 → optional #5.

    Accepts either full contract envelopes or friendly local MirrorME payloads
    (``type: scientific``, ``local_only: true``, etc.). Friendly payloads are
    adapted to contracts for stub testing only.
    """
    adapted_note = None
    try:
        if is_friendly_payload(request, session):
            request, session = adapt_local_payload(request, session)
            adapted_note = "friendly_local_payload_adapted_to_contracts"

        auth = enforce_auth(request, session)
        trail = enforce_gates(
            request,
            session,
            auth_event_ref=f"auth:{auth['request_id']}",
            audit_writable=audit_writable,
        )
        raw_report = _stub_mkone_engine(request, trail)
        report = enforce_validation_report_not_publication(raw_report)

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
                        "flow": [
                            "submitted",
                            "routed",
                            "validation_report_generated",
                            "awaiting_mk_review",
                        ],
                        "adapter": adapted_note,
                        "stub": True,
                    },
                )
            raise

        pub: dict[str, Any] | None = None
        if publication_request is not None:
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
                "message": "approved_for_publication does not auto-publish; confirm_publish required",
                "stub": True,
            }

        flow = [
            "submitted",
            "routed",
            "validation_report_generated",
            "mk_review_recorded",
        ]
        if pub and pub.get("status") == "publish_intent_accepted":
            flow.extend(["approved_for_publication", "explicitly_confirmed", "publish_intent_accepted"])
        elif review.get("allows_optional_publication"):
            flow.append("approved_for_publication")

        return PipelineResult(
            ok=True,
            stage="complete",
            data={
                "auth": auth,
                "gate_trail": trail,
                "validation_report": report,
                "mk_review": review,
                "publication": pub,
                "flow": flow,
                "adapter": adapted_note,
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
