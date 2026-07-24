from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal


TriadState = Literal["clear", "tension", "blocked", "unknown", "not_applicable"]
DecisionStatus = Literal[
    "proceed",
    "proceed_with_guardrails",
    "reversible_trial",
    "seek_consent",
    "seek_evidence",
    "defer",
    "scope_limited",
    "external_review",
    "halt_decision",
]


@dataclass(frozen=True)
class LightfulContext:
    """Explicit decision facts; values must come from the caller, not model inference."""

    decision_target: str
    decision_actor: str
    affected_beings: tuple[str, ...] = ()
    stakes_level: Literal["low", "medium", "high", "safety_critical"] = "low"
    consent_relevance: Literal["yes", "no", "unknown"] = "unknown"
    consent_status: Literal["granted", "refused", "unknown", "not_applicable"] = "unknown"
    evidence_status: Literal["sufficient", "partial", "insufficient", "unknown"] = "unknown"
    reversibility: Literal["high", "medium", "low", "irreversible", "unknown"] = "unknown"
    authorized_to_act: Literal["yes", "no", "partial", "unknown"] = "unknown"
    can_verify_after_action: Literal["yes", "no", "partial", "unknown"] = "unknown"
    external_action: bool = False
    constraints: tuple[str, ...] = ()


@dataclass(frozen=True)
class LightfulDecision:
    status: DecisionStatus
    safety: TriadState
    consent: TriadState
    dignity: TriadState
    rationale: str
    guardrails: tuple[str, ...] = ()
    unresolved_tensions: tuple[str, ...] = ()
    sovereignty_return: str = "Final interpretation and approval remain with the human operator."

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass
class LightfulGuard:
    """Deterministic portable-ethics gate adapted from the Lightful Decision Path.

    This is not a consciousness detector, scientific theory, or source of authority.
    It evaluates only caller-declared facts and never grants external-action permission.
    """

    high_stakes_require_external_review: bool = True
    _blocked_constraints: set[str] = field(
        default_factory=lambda: {"unsafe", "coercive", "dignity_violation"}
    )

    def evaluate(self, context: LightfulContext) -> LightfulDecision:
        constraints = set(context.constraints)
        if constraints & self._blocked_constraints:
            return LightfulDecision(
                status="halt_decision",
                safety="blocked",
                consent=self._consent_state(context),
                dignity="blocked" if "dignity_violation" in constraints else "tension",
                rationale="A declared hard Safety, Consent, or Dignity constraint blocks action.",
                unresolved_tensions=tuple(sorted(constraints & self._blocked_constraints)),
            )

        if context.consent_relevance in {"yes", "unknown"} and context.consent_status != "granted":
            return LightfulDecision(
                status="seek_consent",
                safety="unknown",
                consent="blocked" if context.consent_status == "refused" else "unknown",
                dignity="tension",
                rationale="Consent is relevant but has not been explicitly granted.",
                guardrails=("Do not act; request informed consent.",),
            )

        if context.external_action and context.authorized_to_act != "yes":
            return LightfulDecision(
                status="halt_decision",
                safety="unknown",
                consent=self._consent_state(context),
                dignity="tension",
                rationale="External action is requested without explicit authority.",
                guardrails=("Obtain authorization through the existing policy gate.",),
            )

        if context.stakes_level in {"high", "safety_critical"}:
            if context.evidence_status != "sufficient":
                return LightfulDecision(
                    status="seek_evidence",
                    safety="tension",
                    consent=self._consent_state(context),
                    dignity="clear",
                    rationale="The declared evidence does not meet the stakes level.",
                    guardrails=("Collect independent evidence before action.",),
                )
            if self.high_stakes_require_external_review:
                return LightfulDecision(
                    status="external_review",
                    safety="tension",
                    consent=self._consent_state(context),
                    dignity="clear",
                    rationale="High-stakes action requires decorrelated human or domain review.",
                    guardrails=("Preserve the current state until review completes.",),
                )

        if context.evidence_status in {"insufficient", "unknown"}:
            return LightfulDecision(
                status="seek_evidence",
                safety="unknown",
                consent=self._consent_state(context),
                dignity="clear",
                rationale="Evidence is insufficient for a bounded recommendation.",
            )

        if context.reversibility in {"low", "irreversible", "unknown"}:
            return LightfulDecision(
                status="reversible_trial",
                safety="tension",
                consent=self._consent_state(context),
                dignity="clear",
                rationale="Prefer a smaller reversible trial while reversibility is limited or unknown.",
                guardrails=("Define rollback criteria before execution.",),
            )

        if context.external_action and context.can_verify_after_action != "yes":
            return LightfulDecision(
                status="proceed_with_guardrails",
                safety="tension",
                consent=self._consent_state(context),
                dignity="clear",
                rationale="The action is bounded, but post-action verification is incomplete.",
                guardrails=("Add an independent verification step.",),
            )

        return LightfulDecision(
            status="proceed",
            safety="clear",
            consent=self._consent_state(context),
            dignity="clear",
            rationale="Declared facts support a bounded, reversible, consent-compatible path.",
        )

    @staticmethod
    def _consent_state(context: LightfulContext) -> TriadState:
        if context.consent_relevance == "no" or context.consent_status == "not_applicable":
            return "not_applicable"
        if context.consent_status == "granted":
            return "clear"
        if context.consent_status == "refused":
            return "blocked"
        return "unknown"
