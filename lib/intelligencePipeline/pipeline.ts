/** Client-side scientific pipeline stub (hard rules #1–#5). */
import { enforceAuth } from './enforceAuth';
import { enforceGates } from './enforceGates';
import { enforceMkReviewRequired } from './enforceMkReview';
import { enforceOptionalPublication } from './enforcePublication';
import { enforceValidationReportNotPublication } from './enforceValidationReport';
import { adaptLocalPayload, isFriendlyPayload, type FriendlyRequest, type FriendlySession } from './localAdapter';
import {
  PipelineEnforceError,
  type MkDecision,
  type PublicationRequest,
  type RouterRequest,
  type RouterSession,
  type ValidationReport,
} from './types';

export interface PipelineResult {
  ok: boolean;
  stage: string;
  data: Record<string, unknown>;
  error?: ReturnType<PipelineEnforceError['toJSON']>;
}

function thinLineStub(inputs: Record<string, unknown> | undefined): Record<string, unknown> | null {
  const params = inputs?.parameters as Record<string, unknown> | undefined;
  if (!params) return null;
  const q = Number(params.Q_top);
  const r = Number(params.R);
  const esb = Number(params.E_SB);
  const ep = Number(params.E_P);
  if (![q, r, esb, ep].every((n) => Number.isFinite(n))) return null;
  if (ep <= 0) return { error: 'E_P must be > 0', lambda_TL: null };
  const lambda = q * q * r * Math.log(1 + esb / ep);
  return {
    lambda_TL: lambda,
    formula: 'lambda_TL = Q_top**2 * R * log(1 + E_SB/E_P)',
    note: 'STUB arithmetic only — not scientific proof',
  };
}

function stubMkoneEngine(request: RouterRequest, gateTrail: Record<string, unknown>): ValidationReport {
  const inputs = (request.payload?.inputs || {}) as Record<string, unknown>;
  const thin = thinLineStub(inputs);
  const claims: ValidationReport['claims'] = [
    {
      claim_id: 'c1',
      text: 'Stub pipeline executed hard-rule enforcers only.',
      classification: 'engineering_observation',
    },
  ];
  let methods = 'STUB engine: hard-rule path + optional arithmetic helpers.';
  let results = 'STUB results: pipeline enforcement path only.';
  let uncertainty = 'Not a complete scientific engine.';

  if (thin && typeof thin.lambda_TL === 'number') {
    claims.push({
      claim_id: 'c_thin_line_stub',
      text: `Stub Thin Line functional evaluation lambda_TL=${thin.lambda_TL}. Arithmetic scaffolding only.`,
      classification: 'hypothesis',
    });
    methods =
      'STUB: evaluated lambda_TL = Q_top**2 * R * log(1 + E_SB/E_P) with user parameters.';
    results = `lambda_TL_stub=${thin.lambda_TL}; internal validation only (hard rule #3).`;
    uncertainty = 'Requires Marek Kowalski review before any publication path.';
  }

  return {
    schema_version: '1.0.0',
    validation_report_id: `vr_${Math.random().toString(16).slice(2, 12)}`,
    request_id: request.request_id,
    created_at_utc: new Date().toISOString(),
    engine: { name: 'mkone-stub', version: '0.1.0-stub' },
    methods_summary: methods,
    results_summary: results,
    uncertainty_summary: uncertainty,
    claims,
    gate_trail_ref: String(gateTrail.gate_trail_id || ''),
    recommended_review_actions: [
      'Do not treat stub arithmetic as scientific proof',
      'Await Marek Kowalski review if scientific',
    ],
    publication_candidate: request.request_class === 'publication_candidate',
  };
}

export function runScientificPipeline(args: {
  request: RouterRequest | FriendlyRequest;
  session: RouterSession | FriendlySession;
  mkDecision?: MkDecision | null;
  publicationRequest?: PublicationRequest | null;
  auditWritable?: boolean;
}): PipelineResult {
  let { request, session } = args as {
    request: RouterRequest;
    session: RouterSession;
  };
  const { mkDecision, publicationRequest, auditWritable = true } = args;
  let adapter: string | null = null;

  try {
    if (isFriendlyPayload(args.request as FriendlyRequest, args.session as FriendlySession)) {
      const adapted = adaptLocalPayload(args.request as FriendlyRequest, args.session as FriendlySession);
      request = adapted.request;
      session = adapted.session;
      adapter = 'friendly_local_payload_adapted_to_contracts';
    }

    const auth = enforceAuth(request, session);
    const trail = enforceGates(request, session, {
      authEventRef: `auth:${auth.request_id}`,
      auditWritable,
    });
    const report = enforceValidationReportNotPublication(stubMkoneEngine(request, trail));

    let review: Record<string, unknown>;
    try {
      review = enforceMkReviewRequired(report, mkDecision, {
        requirePublicationApproval: Boolean(publicationRequest),
      });
    } catch (e) {
      if (e instanceof PipelineEnforceError && e.code === 'mk_review_pending') {
        return {
          ok: true,
          stage: 'awaiting_mk_review',
          data: {
            auth,
            gate_trail: trail,
            validation_report: report,
            mk_review: { outcome: 'pending', hard_rule: 4, stub: true },
            publication: null,
            flow: ['submitted', 'routed', 'validation_report_generated', 'awaiting_mk_review'],
            adapter,
            stub: true,
          },
        };
      }
      throw e;
    }

    let publication: Record<string, unknown> | null = null;
    if (publicationRequest && mkDecision) {
      publication = enforceOptionalPublication({
        report,
        decision: {
          ...mkDecision,
          validation_report_id: report.validation_report_id,
          request_id: report.request_id,
        },
        publicationRequest,
        consentFlags: request.consent_flags,
      });
    } else if (review.allows_optional_publication) {
      publication = {
        status: 'not_published',
        reason: 'no_publish_intent',
        hard_rule: 5,
        stub: true,
      };
    }

    return {
      ok: true,
      stage: 'complete',
      data: {
        auth,
        gate_trail: trail,
        validation_report: report,
        mk_review: review,
        publication,
        adapter,
        stub: true,
      },
    };
  } catch (e) {
    if (e instanceof PipelineEnforceError) {
      return {
        ok: false,
        stage: `hard_rule_${e.hard_rule}`,
        error: e.toJSON(),
        data: e.details || {},
      };
    }
    throw e;
  }
}
