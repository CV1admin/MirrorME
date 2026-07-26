"""Hard rule #4 — Marek Kowalski manual review (STUB)."""

from __future__ import annotations

from typing import Any

from ..errors import EnforceError

PUBLICATION_OUTCOME = "approved_for_publication"
ALLOWED_OUTCOMES = {
    "approved_for_internal_use",
    "approved_for_publication",
    "changes_requested",
    "rejected",
}


def enforce_mk_review_required(
    report: dict[str, Any],
    decision: dict[str, Any] | None,
    *,
    require_publication_approval: bool = False,
) -> dict[str, Any]:
    """Block publication-class progress without a valid MK decision record."""
    scientific = bool(
        report.get("publication_candidate")
        or require_publication_approval
        or (report.get("engine") or {}).get("name", "").lower().startswith("mkone")
    )

    if not scientific and not require_publication_approval:
        return {
            "outcome": "review_not_required",
            "hard_rule": 4,
            "stub": True,
        }

    if decision is None:
        raise EnforceError(
            "mk_review_pending",
            "Marek Kowalski manual review required; no decision record",
            4,
            {"validation_report_id": report.get("validation_report_id")},
        )

    if decision.get("reviewer", {}).get("name") != "Marek Kowalski":
        raise EnforceError(
            "mk_review_invalid",
            "reviewer.name must be Marek Kowalski on this authority path",
            4,
        )
    if decision.get("reviewer", {}).get("role") != "scientific_publication_authority":
        raise EnforceError("mk_review_invalid", "reviewer.role invalid", 4)

    outcome = decision.get("outcome")
    if outcome not in ALLOWED_OUTCOMES:
        raise EnforceError("mk_review_invalid", f"unknown outcome {outcome}", 4)

    checklist = decision.get("checklist") or {}
    for key in ("identity_and_integrity", "scientific_honesty", "safety_and_policy"):
        if checklist.get(key) is not True:
            raise EnforceError(
                "mk_review_checklist_incomplete",
                f"checklist.{key} must be true",
                4,
            )

    if outcome == PUBLICATION_OUTCOME:
        if checklist.get("publication_readiness") is not True:
            raise EnforceError(
                "mk_review_checklist_incomplete",
                "publication_readiness required for approved_for_publication",
                4,
            )
        if decision.get("validation_report_id") != report.get("validation_report_id"):
            raise EnforceError(
                "mk_review_mismatch",
                "decision.validation_report_id does not match report",
                4,
            )
        if decision.get("request_id") != report.get("request_id"):
            raise EnforceError(
                "mk_review_mismatch",
                "decision.request_id does not match report",
                4,
            )

    if require_publication_approval and outcome != PUBLICATION_OUTCOME:
        raise EnforceError(
            "mk_review_not_approved_for_publication",
            f"outcome is {outcome}, need approved_for_publication",
            4,
        )

    # Automation must never invent approval
    if decision.get("automated") is True or decision.get("auto_approved") is True:
        raise EnforceError(
            "mk_review_automation_forbidden",
            "automated MK approval is forbidden",
            4,
        )

    return {
        "outcome": outcome,
        "decision_id": decision.get("decision_id"),
        "hard_rule": 4,
        "allows_optional_publication": outcome == PUBLICATION_OUTCOME,
        "stub": True,
    }
