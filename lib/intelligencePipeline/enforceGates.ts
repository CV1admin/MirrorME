/** Hard rule #2 — policy, consent, provenance, audit (STUB). */
import { PipelineEnforceError, type RouterRequest, type RouterSession } from './types';

const SCIENTIFIC = new Set(['scientific_job', 'publication_candidate']);

function gate(outcome: 'pass' | 'fail', reason_code: string, detail = '') {
  return { outcome, reason_code, detail };
}

function simpleHash(obj: unknown): string {
  // Non-crypto stub fingerprint for trail completeness
  const s = JSON.stringify(obj);
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (Math.imul(31, h) + s.charCodeAt(i)) | 0;
  return `stubhash:${(h >>> 0).toString(16)}`;
}

export function enforceGates(
  request: RouterRequest,
  session: RouterSession,
  options: { authEventRef: string; auditWritable?: boolean } = { authEventRef: 'auth:unknown' },
): Record<string, unknown> {
  const auditWritable = options.auditWritable !== false;
  const requestClass = request.request_class;
  const gates: Record<string, ReturnType<typeof gate>> = {};
  const scopes = new Set(session.scopes || []);

  if (SCIENTIFIC.has(requestClass) && !scopes.has('route:scientific')) {
    gates.policy = gate('fail', 'policy_denied', 'route:scientific required');
  } else if (requestClass === 'publication_candidate' && !scopes.has('route:publication_candidate')) {
    gates.policy = gate('fail', 'policy_denied', 'route:publication_candidate required');
  } else {
    gates.policy = gate('pass', 'ok');
  }
  if (gates.policy.outcome === 'fail') {
    throw failTrail(request, session, options.authEventRef, gates, 'policy');
  }

  const flags = request.consent_flags || {};
  if (SCIENTIFIC.has(requestClass)) {
    const required = [
      'allow_router',
      'allow_private_mkone',
      'allow_validation_report',
      'allow_mk_human_review',
    ] as const;
    const missing = required.filter((k) => flags[k] !== true);
    if (requestClass === 'publication_candidate' && flags.allow_publication !== true) {
      missing.push('allow_publication' as typeof required[number]);
    }
    if (missing.length) {
      gates.consent = gate('fail', 'consent_insufficient', `missing: ${missing.join(',')}`);
    } else {
      gates.consent = gate('pass', 'ok');
    }
  } else {
    gates.consent = flags.allow_router === false ? gate('fail', 'consent_missing', 'allow_router false') : gate('pass', 'ok');
  }
  if (gates.consent.outcome === 'fail') {
    throw failTrail(request, session, options.authEventRef, gates, 'consent', flags);
  }

  const provenance =
    request.payload?.input_provenance || request.input_provenance || [];
  if (SCIENTIFIC.has(requestClass)) {
    if (!Array.isArray(provenance) || provenance.length < 1) {
      gates.provenance = gate('fail', 'provenance_incomplete', 'no input_provenance');
    } else {
      const bad = provenance.some((p) => !p.source_class || !p.content_hash);
      gates.provenance = bad
        ? gate('fail', 'provenance_incomplete', 'items missing fields')
        : gate('pass', 'ok');
    }
  } else {
    gates.provenance = gate('pass', 'ok');
  }
  if (gates.provenance.outcome === 'fail') {
    throw failTrail(request, session, options.authEventRef, gates, 'provenance', flags, provenance);
  }

  if (!auditWritable) {
    gates.audit = gate('fail', 'audit_unavailable', 'audit log not writable');
    throw failTrail(request, session, options.authEventRef, gates, 'audit', flags, provenance);
  }
  gates.audit = gate('pass', 'ok');

  return {
    schema_version: '1.0.0',
    gate_trail_id: `gt_${Math.random().toString(16).slice(2, 10)}`,
    request_id: request.request_id,
    session_id: session.session_id,
    created_at_utc: new Date().toISOString(),
    auth_event_ref: options.authEventRef,
    policy_version: 'stub-1.0.0',
    gates,
    consent_snapshot_hash: simpleHash(flags),
    provenance_set_hash: simpleHash(provenance),
    overall: 'pass',
    stub: true,
  };
}

function failTrail(
  request: RouterRequest,
  session: RouterSession,
  authEventRef: string,
  gates: Record<string, ReturnType<typeof gate>>,
  failed: string,
  flags: unknown = {},
  provenance: unknown[] = [],
): PipelineEnforceError {
  for (const name of ['policy', 'consent', 'provenance', 'audit']) {
    if (!gates[name]) {
      gates[name] = gate('fail', 'other', `not evaluated; stopped at ${failed}`);
    }
  }
  const trail = {
    schema_version: '1.0.0',
    gate_trail_id: `gt_${Math.random().toString(16).slice(2, 10)}`,
    request_id: request.request_id,
    session_id: session.session_id,
    created_at_utc: new Date().toISOString(),
    auth_event_ref: authEventRef,
    gates,
    consent_snapshot_hash: simpleHash(flags),
    provenance_set_hash: simpleHash(provenance),
    overall: 'fail' as const,
    stub: true,
  };
  return new PipelineEnforceError(
    gates[failed].reason_code,
    `gate ${failed} failed: ${gates[failed].detail}`,
    2,
    { gate_trail: trail, failed_gate: failed },
  );
}
