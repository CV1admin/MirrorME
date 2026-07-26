/** Hard rule #5 — optional publication, never automatic (STUB). */
import { assertNotPublished } from './enforceValidationReport';
import {
  PipelineEnforceError,
  type ConsentFlags,
  type MkDecision,
  type PublicationRequest,
  type ValidationReport,
} from './types';

export function enforceOptionalPublication(args: {
  report: ValidationReport;
  decision: MkDecision;
  publicationRequest?: PublicationRequest | null;
  consentFlags?: ConsentFlags;
}): Record<string, unknown> {
  const { report, decision, publicationRequest, consentFlags } = args;
  assertNotPublished(report);

  if (decision.outcome !== 'approved_for_publication') {
    throw new PipelineEnforceError(
      'publication_not_approved',
      'hard rule #4 decision must be approved_for_publication',
      5,
    );
  }
  if (consentFlags?.allow_publication !== true) {
    throw new PipelineEnforceError(
      'publication_consent_missing',
      'allow_publication consent required at publish time',
      5,
    );
  }
  if (!publicationRequest) {
    return {
      status: 'not_published',
      reason: 'no_publish_intent',
      hard_rule: 5,
      message: 'Approval does not publish; explicit intent required',
      stub: true,
    };
  }
  if (publicationRequest.confirm_publish !== true) {
    return {
      status: 'not_published',
      reason: 'confirm_publish_false',
      hard_rule: 5,
      stub: true,
    };
  }
  if (publicationRequest.decision_id !== decision.decision_id) {
    throw new PipelineEnforceError('publication_id_mismatch', 'decision_id mismatch', 5);
  }
  if (publicationRequest.validation_report_id !== report.validation_report_id) {
    throw new PipelineEnforceError('publication_id_mismatch', 'validation_report_id mismatch', 5);
  }
  if (publicationRequest.request_id !== report.request_id) {
    throw new PipelineEnforceError('publication_id_mismatch', 'request_id mismatch', 5);
  }

  return {
    status: 'publish_intent_accepted',
    hard_rule: 5,
    publication_request_id: publicationRequest.publication_request_id,
    next: 'build_publication_package',
    stub: true,
    note: 'STUB: does not perform actual public release',
  };
}
