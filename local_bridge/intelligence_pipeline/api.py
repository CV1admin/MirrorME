"""Wire hard-rule pipeline into local MirrorME bridge helpers."""
from __future__ import annotations

from typing import Any

from .pipeline import PipelineResult, run_scientific_pipeline


def handle_scientific_route(body: dict[str, Any]) -> dict[str, Any]:
    """Expect {request, session, mk_decision?, publication_request?}."""
    result: PipelineResult = run_scientific_pipeline(
        request=body.get("request") or {},
        session=body.get("session") or {},
        mk_decision=body.get("mk_decision"),
        publication_request=body.get("publication_request"),
        audit_writable=body.get("audit_writable", True),
    )
    return {
        "ok": result.ok,
        "stage": result.stage,
        "data": result.data,
        "error": result.error,
        "stub": True,
        "contracts": "Civilisation-one/.github + local contracts/",
    }
