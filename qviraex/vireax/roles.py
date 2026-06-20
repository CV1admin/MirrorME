from __future__ import annotations

from enum import StrEnum


class ModelRole(StrEnum):
    ARCHITECT = "architect"
    CRITIC = "critic"
    CONTEXT_ANALYST = "context_analyst"
    SAFETY_REVIEWER = "safety_reviewer"
    TECHNICAL_VALIDATOR = "technical_validator"
    LOCAL_FALLBACK = "local_fallback"
    WORKFLOW_ADAPTER = "workflow_adapter"
    CENTER_NODE = "center_node"


class VIREAXState(StrEnum):
    INIT = "INIT"
    OPERATOR_AUTH = "OPERATOR_AUTH"
    LOAD_POLICY = "LOAD_POLICY"
    DECLARE_TASK = "DECLARE_TASK"
    CLASSIFY_DOMAIN = "CLASSIFY_DOMAIN"
    SELECT_MODELS = "SELECT_MODELS"
    ASSIGN_ROLES = "ASSIGN_ROLES"
    DISPATCH = "DISPATCH"
    COLLECT = "COLLECT"
    CROSS_EXAMINE = "CROSS_EXAMINE"
    VERIFY_FACTS = "VERIFY_FACTS"
    RESOLVE_CONFLICTS = "RESOLVE_CONFLICTS"
    SYNTHESIZE = "SYNTHESIZE"
    HUMAN_APPROVAL = "HUMAN_APPROVAL"
    AUDIT_COMMIT = "AUDIT_COMMIT"
    FINAL_OUTPUT = "FINAL_OUTPUT"
    CLOSED = "CLOSED"