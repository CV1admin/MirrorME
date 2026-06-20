from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str = ""
    redacted_payload: dict[str, Any] | None = None


class PolicyGate:
    def __init__(self, blocked_actions: tuple[str, ...] = ()) -> None:
        self.blocked_actions = set(blocked_actions)

    def evaluate(self, payload: dict[str, Any]) -> PolicyDecision:
        forbidden_actions = payload.get("forbidden_actions", [])
        if any(action in self.blocked_actions for action in forbidden_actions):
            return PolicyDecision(False, "policy rejected by forbidden action list", payload)
        if payload.get("external_action_allowed") is True:
            return PolicyDecision(False, "external action blocked by VIREAX policy", payload)
        return PolicyDecision(True, redacted_payload=payload)