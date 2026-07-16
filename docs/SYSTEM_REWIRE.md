# MirrorME System Rewire

Version: 1.0
Date: 2026-07-16
Owner: Marek Kowalski, CEO of Civilisation.One

## Role separation

| Component | Responsibility | Public access |
|---|---|---|
| MirrorME | Member UI, local-first chat, consent, status and audit display | Yes |
| Civilisation.One Global Intelligence Router | Authentication, policy, routing, rate limits, provenance and audit | Controlled |
| MKone | Equation registry, dimensional checks, simulations, uncertainty and quantum verification | No direct public access |
| Human review | Scientific acceptance and publication decision | Marek Kowalski |
| SciSpace evidence adapter | Paper discovery and source metadata | Router-mediated input only |

## Non-negotiable boundaries

1. The browser never receives provider secrets or a private MKone endpoint.
2. MirrorME sends scientific work only to an authenticated Civilisation.One router.
3. The router creates an immutable submission ID and audit record before forwarding.
4. MKone returns a validation report, not an automatic truth declaration.
5. Status classes remain separated: E, C, D, P, H and X.
6. Hypotheses and phenomenological models cannot be promoted automatically.
7. Quantum-reasoning submissions remain private and are submitted under Marek Kowalski's authority.
8. Publication requires an explicit human transition from reviewed to published.
9. Simulated telemetry must remain labelled simulated.
10. Local Ollama operation remains available without cloud transmission.

## Request envelope

```json
{
  "protocol": "CV1-SCI/1.0",
  "submission_id": "uuid",
  "submitted_at": "ISO-8601",
  "actor": {
    "subject": "authenticated-user-id",
    "role": "member|operator|ceo",
    "authority": "standard|scientific-submit"
  },
  "consent": {
    "external_processing": false,
    "store_audit_record": true
  },
  "task": {
    "kind": "explain|validate|simulate|quantum-verify",
    "content_hash": "sha256:...",
    "classification": "E|C|D|P|H|X"
  },
  "routing": {
    "requested_engine": "mkone",
    "direct_engine_access": false
  },
  "provenance": [],
  "idempotency_key": "uuid"
}
```

The full submission content should be encrypted in transit and stored according to the selected privacy policy. The envelope must never contain API keys.

## Validation response

```json
{
  "submission_id": "uuid",
  "report_id": "uuid",
  "engine": "mkone",
  "status": "accepted|quarantined|rejected|needs-review",
  "checks": {
    "schema": "pass|fail",
    "dimensions": "pass|fail|not-applicable",
    "boundary_conditions": "pass|fail|not-tested",
    "source_support": "supported|partial|unsupported",
    "hypothesis_separation": "pass|fail"
  },
  "uncertainty": {
    "score": 0.0,
    "method": "declared-method"
  },
  "publication_state": "private",
  "audit_hash": "sha256:..."
}
```

## Publication state machine

```text
DRAFT -> SUBMITTED -> VALIDATING -> PRIVATE_REVIEW
PRIVATE_REVIEW -> REVISION_REQUIRED | REJECTED | APPROVED
APPROVED -> PUBLISHED only by explicit human action
```

No model, router, simulation, or evidence search service may perform the final publication transition.

## Evidence handling

SciSpace or another literature service may propose sources. The router must record DOI, title, authors, publication year, retrieval time and the exact claim being supported. Search rank is not evidence strength. Prefer primary literature, official constants releases and recognized standards.

## Deployment order

1. Keep MirrorME static UI free of server secrets.
2. Add an authenticated Civilisation.One router endpoint.
3. Implement the request and response schemas above.
4. Add server-side provider adapters.
5. Connect MKone behind the router.
6. Load MKdataONE into the MKone registry, not into client JavaScript.
7. Add schema, unit, authorization and publication-gate tests.
8. Enable external processing only through explicit consent.
