"""Hard rule #5 — optional publication, never automatic (STUB)."""

from __future__ import annotations

from typing import Any

from ..errors import EnforceError
from .validation_report import assert_not_published


def enforce_optional_publication(
    *,
    report: dict[str, Any],
    decision: dict[str, Any],
    publication_request: dict[str, Any] | None,
    consent_flags: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Allow packaging only with explicit publish intent after MK approval."""
    assert_not_published(report)

    if decision.get("outcome") != "approved_for_publication":
        raise EnforceError(
            "publication_not_approved",
            "hard rule #4 decision must be approved_for_publication",
            5,
        )

    flags = consent_flags or {}
    if flags.get("allow_publication") is not True:
        raise EnforceError(
            "publication_consent_missing",
            "allow_publication consent required at publish time",
            5,
        )

    if publication_request is None:
        return {
            "status": "not_published",
            "reason": "no_publish_intent",
            "hard_rule": 5,
            "message": "Approval does not publish; explicit intent required",
            "stub": True,
        }

    if publication_request.get("confirm_publish") is not True:
        return {
            "status": "not_published",
            "reason": "confirm_publish_false",
            "hard_rule": 5,
            "stub": True,
        }

    # Bind ids
    if publication_request.get("decision_id") != decision.get("decision_id"):
        raise EnforceError("publication_id_mismatch", "decision_id mismatch", 5)
    if publication_request.get("validation_report_id") != report.get("validation_report_id"):
        raise EnforceError("publication_id_mismatch", "validation_report_id mismatch", 5)
    if publication_request.get("request_id") != report.get("request_id"):
        raise EnforceError("publication_id_mismatch", "request_id mismatch", 5)

    return {
        "status": "publish_intent_accepted",
        "hard_rule": 5,
        "publication_request_id": publication_request.get("publication_request_id"),
        "next": "build_publication_package",
        "stub": True,
        "note": "STUB: does not perform actual public release",
    }
