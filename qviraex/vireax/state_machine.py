from __future__ import annotations

from dataclasses import dataclass

from .roles import VIREAXState


class VIREAXEvent(str):
    pass


_TRANSITIONS: dict[VIREAXState, tuple[VIREAXState, ...]] = {
    VIREAXState.INIT: (VIREAXState.OPERATOR_AUTH,),
    VIREAXState.OPERATOR_AUTH: (VIREAXState.LOAD_POLICY,),
    VIREAXState.LOAD_POLICY: (VIREAXState.DECLARE_TASK,),
    VIREAXState.DECLARE_TASK: (VIREAXState.CLASSIFY_DOMAIN,),
    VIREAXState.CLASSIFY_DOMAIN: (VIREAXState.SELECT_MODELS,),
    VIREAXState.SELECT_MODELS: (VIREAXState.ASSIGN_ROLES,),
    VIREAXState.ASSIGN_ROLES: (VIREAXState.DISPATCH,),
    VIREAXState.DISPATCH: (VIREAXState.COLLECT,),
    VIREAXState.COLLECT: (VIREAXState.CROSS_EXAMINE,),
    VIREAXState.CROSS_EXAMINE: (VIREAXState.VERIFY_FACTS,),
    VIREAXState.VERIFY_FACTS: (VIREAXState.RESOLVE_CONFLICTS,),
    VIREAXState.RESOLVE_CONFLICTS: (VIREAXState.SYNTHESIZE,),
    VIREAXState.SYNTHESIZE: (VIREAXState.HUMAN_APPROVAL,),
    VIREAXState.HUMAN_APPROVAL: (VIREAXState.AUDIT_COMMIT,),
    VIREAXState.AUDIT_COMMIT: (VIREAXState.FINAL_OUTPUT,),
    VIREAXState.FINAL_OUTPUT: (VIREAXState.CLOSED,),
}


@dataclass(frozen=True)
class ReduceResult:
    state: VIREAXState
    allowed: bool
    reason: str = ""


def reduce_state(state: VIREAXState, next_state: VIREAXState) -> ReduceResult:
    allowed_states = _TRANSITIONS.get(state, ())
    if next_state not in allowed_states:
        return ReduceResult(state=state, allowed=False, reason=f"invalid transition: {state} -> {next_state}")
    return ReduceResult(state=next_state, allowed=True)