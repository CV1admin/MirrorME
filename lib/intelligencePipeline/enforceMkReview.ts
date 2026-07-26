/** Hard rule #4 — Marek Kowalski manual review (STUB). */
import { PipelineEnforceError, type MkDecision, type ValidationReport } from './types';

export function enforceMkReviewRequired(
  report: ValidationReport,
  decision: MkDecision | null | undefined,
  options: { requirePublicationApproval?: boolean } = {},
): Record<string, unknown> {
  const scientific =
    Boolean(report.publication_candidate) ||
    Boolean(options.requirePublicationApproval) ||
    (report.engine?.name || '').toLowerCase().startsWith('mkone');

  if (!scientific && !options.requirePublicationApproval) {
    return { outcome: 'review_not_required', hard_rule: 4, stub: true };
  }

  if (!decision) {
    throw new PipelineEnforceError(
      'mk_review_pending',
      'Marek Kowalski manual review required; no decision record',
      4,
      { validation_report_id: report.validation_report_id },
    );
  }

  if (decision.reviewer?.name !== 'Marek Kowalski') {
    throw new PipelineEnforceError(
      'mk_review_invalid',
      'reviewer.name must be Marek Kowalski',
      4,
    );
  }
  if (decision.reviewer?.role !== 'scientific_publication_authority') {
    throw new PipelineEnforceError('mk_review_invalid', 'reviewer.role invalid', 4);
  }

  const { checklist } = decision;
  for (const key of ['identity_and_integrity', 'scientific_honesty', 'safety_and_policy'] as const) {
    if (checklist?.[key] !== true) {
      throw new PipelineEnforceError(
        'mk_review_checklist_incomplete',
        `checklist.${key} must be true`,
        4,
      );
    }
  }

  if (decision.outcome === 'approved_for_publication') {
    if (checklist.publication_readiness !== true) {
      throw new PipelineEnforceError(
        'mk_review_checklist_incomplete',
        'publication_readiness required for approved_for_publication',
        4,
      );
    }
    if (decision.validation_report_id !== report.validation_report_id) {
      throw new PipelineEnforceError('mk_review_mismatch', 'validation_report_id mismatch', 4);
    }
    if (decision.request_id !== report.request_id) {
      throw new PipelineEnforceError('mk_review_mismatch', 'request_id mismatch', 4);
    }
  }

  if (options.requirePublicationApproval && decision.outcome !== 'approved_for_publication') {
    throw new PipelineEnforceError(
      'mk_review_not_approved_for_publication',
      `outcome is ${decision.outcome}`,
      4,
    );
  }

  if (decision.automated === true || decision.auto_approved === true) {
    throw new PipelineEnforceError(
      'mk_review_automation_forbidden',
      'automated MK approval is forbidden',
      4,
    );
  }

  return {
    outcome: decision.outcome,
    decision_id: decision.decision_id,
    hard_rule: 4,
    allows_optional_publication: decision.outcome === 'approved_for_publication',
    stub: true,
  };
}
