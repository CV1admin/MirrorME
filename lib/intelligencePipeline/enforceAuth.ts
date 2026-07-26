/** Hard rule #1 — auth required (STUB). */
import {
  PipelineEnforceError,
  ROUTER_AUDIENCE,
  type RouterRequest,
  type RouterSession,
} from './types';

const CLASS_SCOPES: Record<string, string[]> = {
  chat: ['route:chat'],
  research_assist: ['route:chat'],
  scientific_job: ['route:scientific'],
  publication_candidate: ['route:scientific', 'route:publication_candidate'],
  admin_ops: ['route:admin_ops'],
};

const SCIENTIFIC = new Set(['scientific_job', 'publication_candidate']);

export function enforceAuth(
  request: RouterRequest | null | undefined,
  session: RouterSession | null | undefined,
  now: Date = new Date(),
): Record<string, unknown> {
  if (!request) {
    throw new PipelineEnforceError('auth_missing', 'router request missing', 1);
  }
  if (!session) {
    throw new PipelineEnforceError('auth_missing', 'session missing', 1);
  }
  if (session.audience !== ROUTER_AUDIENCE) {
    throw new PipelineEnforceError('auth_invalid', 'session audience mismatch', 1);
  }
  if (session.revoked === true) {
    throw new PipelineEnforceError('auth_invalid', 'session revoked', 1);
  }
  if (!session.expires_at_utc || new Date(session.expires_at_utc) <= now) {
    throw new PipelineEnforceError('auth_invalid', 'session expired', 1);
  }

  for (const key of ['request_id', 'session_id', 'member_public_id', 'request_class'] as const) {
    if (!request[key]) {
      throw new PipelineEnforceError('auth_missing', `request missing ${key}`, 1, { field: key });
    }
  }
  if (request.session_id !== session.session_id) {
    throw new PipelineEnforceError('auth_invalid', 'session_id mismatch', 1);
  }
  if (request.member_public_id !== session.member_public_id) {
    throw new PipelineEnforceError('auth_invalid', 'member_public_id mismatch', 1);
  }

  const proof = request.client_proof;
  if (!proof?.type || !proof?.value) {
    throw new PipelineEnforceError('auth_proof_failed', 'client_proof incomplete', 1);
  }
  const value = String(proof.value).trim();
  if (value.length < 8 || ['unsigned', 'none', 'null', 'placeholder'].includes(value.toLowerCase())) {
    throw new PipelineEnforceError('auth_proof_failed', 'client_proof not acceptable (stub)', 1);
  }

  const needed = CLASS_SCOPES[request.request_class];
  if (!needed) {
    throw new PipelineEnforceError('auth_invalid', `unknown request_class ${request.request_class}`, 1);
  }
  const scopes = new Set(session.scopes || []);
  const missing = needed.filter((s) => !scopes.has(s));
  if (missing.length) {
    throw new PipelineEnforceError(
      'authz_insufficient_scope',
      `missing scopes: ${missing.join(', ')}`,
      1,
      { missing },
    );
  }

  if (SCIENTIFIC.has(request.request_class) && !request.consent_flags) {
    throw new PipelineEnforceError(
      'auth_invalid',
      'scientific request_class requires consent_flags',
      1,
    );
  }

  return {
    outcome: 'auth_ok',
    hard_rule: 1,
    request_id: request.request_id,
    session_id: session.session_id,
    member_public_id: session.member_public_id,
    request_class: request.request_class,
    stub: true,
    note: 'STUB: cryptographic proof verification not implemented',
  };
}
