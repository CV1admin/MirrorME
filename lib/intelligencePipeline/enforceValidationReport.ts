/** Hard rule #3 — validation report ≠ publication (STUB). */
import {
  INTERNAL_REPORT_BANNER,
  PipelineEnforceError,
  type ValidationReport,
} from './types';

const ALLOWED = new Set([
  'internal_framework',
  'externally_established',
  'hypothesis',
  'engineering_observation',
]);

const REQUIRED_REPORT_FIELDS = [
  'validation_report_id',
  'request_id',
  'engine',
  'methods_summary',
  'results_summary',
  'claims',
  'gate_trail_ref',
] as const satisfies ReadonlyArray<keyof ValidationReport>;

function hasRequiredValue(value: unknown): boolean {
  return value !== undefined && value !== null && value !== '';
}

export function enforceValidationReportNotPublication(
  report: ValidationReport | null | undefined,
): ValidationReport {
  if (!report) {
    throw new PipelineEnforceError('report_missing', 'validation report missing', 3);
  }
  for (const key of REQUIRED_REPORT_FIELDS) {
    if (!hasRequiredValue(report[key])) {
      throw new PipelineEnforceError('report_incomplete', `report missing ${key}`, 3, { field: key });
    }
  }
  if (!Array.isArray(report.claims) || report.claims.length < 1) {
    throw new PipelineEnforceError('report_incomplete', 'claims must be non-empty', 3);
  }
  for (const claim of report.claims) {
    if (!ALLOWED.has(claim.classification)) {
      throw new PipelineEnforceError(
        'report_claim_invalid',
        `invalid classification ${claim.classification}`,
        3,
      );
    }
  }

  return {
    ...report,
    is_publication: false,
    publication_status: 'not_a_publication',
    internal_banner: INTERNAL_REPORT_BANNER,
    hard_rule_3: 'validation_report_is_not_publication',
    stub: true,
    next_required_stage: report.publication_candidate
      ? 'marek_kowalski_manual_review'
      : 'internal_use_or_mk_review_if_scientific',
  };
}

export function assertNotPublished(report: ValidationReport): void {
  if (report.is_publication === true || report.publication_status === 'published') {
    throw new PipelineEnforceError(
      'report_treated_as_publication',
      'validation report must not be treated as publication (hard rule #3)',
      3,
    );
  }
}
