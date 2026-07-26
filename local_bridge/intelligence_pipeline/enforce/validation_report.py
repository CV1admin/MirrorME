"""Hard rule #3 — validation report is not a publication (STUB)."""

from __future__ import annotations

from typing import Any

from ..errors import EnforceError

ALLOWED_CLASSIFICATIONS = {
    "internal_framework",
    "externally_established",
    "hypothesis",
    "engineering_observation",
}

INTERNAL_BANNER = (
    "INTERNAL VALIDATION REPORT — NOT A PUBLICATION. "
    "Not peer-reviewed public science. Not approved for publication unless a "
    "Marek Kowalski decision record says approved_for_publication."
)


def enforce_validation_report_not_publication(report: dict[str, Any]) -> dict[str, Any]:
    """Stamp and validate a report; forbid treating it as publication."""
    if not report:
        raise EnforceError("report_missing", "validation report missing", 3)

    required = [
        "validation_report_id",
        "request_id",
        "engine",
        "methods_summary",
        "results_summary",
        "claims",
        "gate_trail_ref",
    ]
    for key in required:
        if not report.get(key):
            raise EnforceError("report_incomplete", f"report missing {key}", 3, {"field": key})

    claims = report.get("claims")
    if not isinstance(claims, list) or len(claims) < 1:
        raise EnforceError("report_incomplete", "claims must be a non-empty list", 3)

    for claim in claims:
        cls = claim.get("classification")
        if cls not in ALLOWED_CLASSIFICATIONS:
            raise EnforceError(
                "report_claim_invalid",
                f"invalid claim classification: {cls}",
                3,
                {"claim_id": claim.get("claim_id")},
            )

    # Hard rule #3: never auto-promote to publication
    stamped = dict(report)
    stamped["is_publication"] = False
    stamped["publication_status"] = "not_a_publication"
    stamped["internal_banner"] = INTERNAL_BANNER
    stamped["hard_rule_3"] = "validation_report_is_not_publication"
    stamped["stub"] = True

    if stamped.get("publication_candidate") is True:
        stamped["next_required_stage"] = "marek_kowalski_manual_review"
    else:
        stamped["next_required_stage"] = "internal_use_or_mk_review_if_scientific"

    return stamped


def assert_not_published(report: dict[str, Any]) -> None:
    """Call before any publish path; report alone is insufficient."""
    if report.get("is_publication") is True:
        raise EnforceError(
            "report_treated_as_publication",
            "validation report flagged as publication — forbidden by hard rule #3",
            3,
        )
    if report.get("publication_status") == "published":
        raise EnforceError(
            "report_treated_as_publication",
            "validation report publication_status=published is forbidden",
            3,
        )
