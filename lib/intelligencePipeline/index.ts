/**
 * MirrorME client stubs for Civilisation.One Global Intelligence Pipeline hard rules.
 * Canonical contracts: Civilisation-one/.github/contracts (copied under ./contracts).
 */
export { enforceAuth } from './enforceAuth';
export { enforceGates } from './enforceGates';
export { enforceValidationReportNotPublication, assertNotPublished } from './enforceValidationReport';
export { enforceMkReviewRequired } from './enforceMkReview';
export { enforceOptionalPublication } from './enforcePublication';
export { runScientificPipeline, type PipelineResult } from './pipeline';
export { adaptLocalPayload, isFriendlyPayload, type FriendlyRequest, type FriendlySession } from './localAdapter';
export {
  PipelineEnforceError,
  ROUTER_AUDIENCE,
  INTERNAL_REPORT_BANNER,
  type RouterRequest,
  type RouterSession,
  type ValidationReport,
  type MkDecision,
  type PublicationRequest,
  type ConsentFlags,
} from './types';
