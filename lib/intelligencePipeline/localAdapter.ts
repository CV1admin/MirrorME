/** Map friendly local MirrorME payloads onto contract-shaped request/session (stub). */
import { ROUTER_AUDIENCE, type ConsentFlags, type RouterRequest, type RouterSession } from './types';

const TYPE_TO_CLASS: Record<string, RouterRequest['request_class']> = {
  scientific: 'scientific_job',
  scientific_job: 'scientific_job',
  publication: 'publication_candidate',
  publication_candidate: 'publication_candidate',
  chat: 'chat',
  research_assist: 'research_assist',
  validate: 'scientific_job',
};

/** Friendly local shapes accepted for integration tests. */
export type FriendlyRequest = Partial<RouterRequest> & {
  type?: string;
  objective?: string;
  inputs?: Record<string, unknown>;
  requested_action?: string;
  request_id?: string;
};

export type FriendlySession = Partial<RouterSession> & {
  actor_id?: string;
  actor_role?: string;
  local_only?: boolean;
};

function simpleHash(obj: unknown): string {
  const s = JSON.stringify(obj);
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (Math.imul(31, h) + s.charCodeAt(i)) | 0;
  return `sha256:stub${(h >>> 0).toString(16)}`;
}

export function isFriendlyPayload(request?: FriendlyRequest | null, session?: FriendlySession | null): boolean {
  const r = request || {};
  const s = session || {};
  if (s.local_only === true) return true;
  if (r.type && !r.request_class) return true;
  if (s.actor_id && !s.member_public_id) return true;
  return false;
}

export function adaptLocalPayload(
  request?: FriendlyRequest | null,
  session?: FriendlySession | null,
): { request: RouterRequest; session: RouterSession } {
  const r = { ...(request || {}) } as FriendlyRequest;
  const s = { ...(session || {}) } as FriendlySession;

  if (!isFriendlyPayload(r, s) && r.request_class && s.member_public_id && s.session_id) {
    return { request: r as RouterRequest, session: s as RouterSession };
  }

  const now = new Date();
  const member = s.member_public_id || s.actor_id || 'local-member';
  const sessionId = s.session_id || 'mirrorme-local-session';
  const requestId = r.request_id || `req_local_${now.getTime()}`;
  const rawType = String(r.type || r.request_class || 'scientific');
  let requestClass = TYPE_TO_CLASS[rawType] || 'scientific_job';
  if (r.requested_action === 'validate' && requestClass === 'chat') {
    requestClass = 'scientific_job';
  }

  const scopes = [...(s.scopes || ['route:chat', 'route:scientific', 'route:publication_candidate'])];
  if (s.actor_role === 'MK' || s.actor_role === 'scientific_publication_authority') {
    for (const sc of ['route:scientific', 'route:publication_candidate']) {
      if (!scopes.includes(sc)) scopes.push(sc);
    }
  }

  const inputs = r.inputs || (r.payload as { inputs?: Record<string, unknown> } | undefined)?.inputs || {};
  const provenance =
    r.input_provenance ||
    (r.payload as { input_provenance?: RouterRequest['input_provenance'] } | undefined)?.input_provenance || [
      {
        source_class: 'user_selected_context',
        content_hash: simpleHash(inputs),
        description: r.objective || 'local scientific inputs',
      },
    ];

  const consent: ConsentFlags = r.consent_flags || {
    allow_router: true,
    allow_private_mkone: true,
    allow_validation_report: true,
    allow_mk_human_review: true,
    allow_publication: false,
  };

  const proofValue = r.client_proof?.value || `local-stub-token-${sessionId}`;

  const adaptedSession: RouterSession = {
    schema_version: '1.0.0',
    session_id: sessionId,
    member_public_id: member,
    node_id: s.node_id || 'mirrorme-local-node',
    authenticator: s.authenticator || 'session_token',
    scopes,
    issued_at_utc: s.issued_at_utc || now.toISOString(),
    expires_at_utc: s.expires_at_utc || new Date(now.getTime() + 2 * 3600_000).toISOString(),
    audience: s.audience || ROUTER_AUDIENCE,
    revoked: false,
  };

  const adaptedRequest: RouterRequest = {
    schema_version: '1.0.0',
    request_id: requestId,
    session_id: sessionId,
    member_public_id: member,
    node_id: adaptedSession.node_id,
    request_class: requestClass,
    issued_at_utc: r.issued_at_utc || now.toISOString(),
    consent_flags: consent,
    client_proof: {
      type: r.client_proof?.type || 'bearer_session_token',
      value: String(proofValue),
    },
    payload: {
      objective: r.objective,
      requested_action: r.requested_action || 'validate',
      inputs,
      input_provenance: provenance,
      friendly_type: rawType,
    },
    input_provenance: provenance,
  };

  return { request: adaptedRequest, session: adaptedSession };
}
