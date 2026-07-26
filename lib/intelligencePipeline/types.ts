/** Shared types for Global Intelligence Pipeline hard-rule stubs. */

export type RequestClass =
  | 'chat'
  | 'research_assist'
  | 'scientific_job'
  | 'publication_candidate'
  | 'admin_ops';

export type ClaimClassification =
  | 'internal_framework'
  | 'externally_established'
  | 'hypothesis'
  | 'engineering_observation';

export interface ConsentFlags {
  allow_router?: boolean;
  allow_private_mkone?: boolean;
  allow_validation_report?: boolean;
  allow_mk_human_review?: boolean;
  allow_publication?: boolean;
}

export interface RouterSession {
  schema_version?: string;
  session_id: string;
  member_public_id: string;
  node_id?: string;
  authenticator?: string;
  scopes: string[];
  issued_at_utc: string;
  expires_at_utc: string;
  audience: string;
  revoked?: boolean;
}

export interface RouterRequest {
  schema_version?: string;
  request_id: string;
  session_id: string;
  member_public_id: string;
  node_id?: string;
  request_class: RequestClass;
  issued_at_utc: string;
  nonce?: string;
  consent_flags?: ConsentFlags;
  payload_ref?: string;
  payload?: {
    input_provenance?: Array<{
      source_class: string;
      content_hash: string;
      description?: string;
    }>;
    [key: string]: unknown;
  };
  input_provenance?: Array<{
    source_class: string;
    content_hash: string;
    description?: string;
  }>;
  client_proof: {
    type: string;
    value: string;
    public_key_id?: string;
  };
}

export interface ValidationReport {
  schema_version?: string;
  validation_report_id: string;
  request_id: string;
  created_at_utc?: string;
  engine: { name: string; version: string; build?: string };
  methods_summary: string;
  results_summary: string;
  uncertainty_summary?: string;
  claims: Array<{
    claim_id: string;
    text: string;
    classification: ClaimClassification;
  }>;
  gate_trail_ref: string;
  recommended_review_actions?: string[];
  publication_candidate?: boolean;
  is_publication?: boolean;
  publication_status?: string;
  internal_banner?: string;
  hard_rule_3?: string;
  stub?: boolean;
  next_required_stage?: string;
}

export interface MkDecision {
  decision_id: string;
  request_id: string;
  validation_report_id: string;
  reviewer: {
    name: string;
    role: string;
    github_login?: string;
  };
  outcome:
    | 'approved_for_internal_use'
    | 'approved_for_publication'
    | 'changes_requested'
    | 'rejected';
  checklist: {
    identity_and_integrity: boolean;
    scientific_honesty: boolean;
    safety_and_policy: boolean;
    publication_readiness?: boolean;
  };
  notes?: string;
  automated?: boolean;
  auto_approved?: boolean;
}

export interface PublicationRequest {
  publication_request_id: string;
  request_id: string;
  validation_report_id: string;
  decision_id: string;
  confirm_publish: boolean;
  requested_by?: { actor_type: string; public_id: string };
  requested_at_utc?: string;
}

export interface EnforceErrorShape {
  code: string;
  message: string;
  hard_rule: number;
  details?: Record<string, unknown>;
}

export class PipelineEnforceError extends Error {
  code: string;
  hard_rule: number;
  details?: Record<string, unknown>;

  constructor(code: string, message: string, hard_rule: number, details?: Record<string, unknown>) {
    super(message);
    this.name = 'PipelineEnforceError';
    this.code = code;
    this.hard_rule = hard_rule;
    this.details = details;
  }

  toJSON(): EnforceErrorShape {
    return {
      code: this.code,
      message: this.message,
      hard_rule: this.hard_rule,
      details: this.details,
    };
  }
}

export const ROUTER_AUDIENCE = 'civilisation.one.global-intelligence-router';

export const INTERNAL_REPORT_BANNER =
  'INTERNAL VALIDATION REPORT — NOT A PUBLICATION. ' +
  'Not peer-reviewed public science. Not approved for publication unless a ' +
  'Marek Kowalski decision record says approved_for_publication.';
