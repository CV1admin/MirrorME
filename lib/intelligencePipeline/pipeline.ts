/** Client-side scientific pipeline stub (hard rules #1–#5). */
import { enforceAuth } from './enforceAuth';
import { enforceGates } from './enforceGates';
import { enforceMkReviewRequired } from './enforceMkReview';
import { enforceOptionalPublication } from './enforcePublication';
import { enforceValidationReportNotPublication } from './enforceValidationReport';
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

function stubMkoneEngine(request: RouterRequest, gateTrail: Record<string, unknown>): ValidationReport {
  return {
    schema_version: '1.0.0',
    validation_report_id: `vr_${Math.random().toString(16).slice(2, 12)}`,
    request_id: request.request_id,
    created_at_utc: new Date().toISOString(),
    engine: { name: 'mkone-stub', version: '0.0.0-stub' },
    methods_summary: 'STUB engine: no scientific computation performed.',
    results_summary: 'STUB results: pipeline enforcement path only.',
    claims: [
      {
        claim_id: 'c1',
        text: 'Stub pipeline executed hard-rule enforcers only.',
        classification: 'engineering_observation',
      },
    ],
    gate_trail_ref: String(gateTrail.gate_trail_id || ''),
    recommended_review_actions: ['Do not treat as science', 'Await Marek Kowalski review if scientific'],
    publication_candidate: request.request_class === 'publication_candidate',
  };
}

export function runScientificPipeline(args: {
  request: RouterRequest;
  session: RouterSession;
  mkDecision?: MkDecision | null;
  publicationRequest?: PublicationRequest | null;
  auditWritable?: boolean;
}): PipelineResult {
  const { request, session, mkDecision, publicationRequest, auditWritable = true } = args;
  try {
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
