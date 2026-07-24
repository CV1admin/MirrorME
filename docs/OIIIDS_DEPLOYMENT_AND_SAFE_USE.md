# OIIIDS Deployment, Management, Installation, and Safe Use

This guide covers the current OIIIDS core included in MirrorME. It is a development-stage, transport-neutral resource exchange library. It is not yet a production network service.

## Current status

Implemented:

- immutable versioned resource envelopes
- canonical JSON hashing
- content and envelope integrity checks
- explicit access scopes and principal allowlists
- pluggable signing interface
- development-only HMAC signer
- in-memory resource store
- publish, read, verify, and next-version operations
- Observer audit sink boundary

Not yet production-ready:

- asymmetric node signatures
- protected key storage and rotation
- encrypted payloads
- durable database storage
- authenticated network API
- MCP resource endpoints
- CRDT/offline reconciliation
- distributed authorization service
- OpenTelemetry deployment
- backup and disaster recovery

Do not expose the current library directly to the public internet.

## Installation

### Requirements

- Python 3.11 or later
- Git
- a local virtual environment

### Clone and enter the repository

```bash
git clone https://github.com/CV1admin/MirrorME.git
cd MirrorME
```

### Create a virtual environment

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux or macOS:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### Install the project dependencies

Use the repository's existing Python dependency mechanism when present. For the standalone OIIIDS core, no external runtime dependency is required by the current implementation.

Install test tooling:

```bash
python -m pip install --upgrade pip
python -m pip install pytest
```

### Run the OIIIDS tests

```bash
python -m pytest tests/test_oiiids.py -q
```

Do not continue to deployment if any integrity, authorization, or tamper-detection test fails.

## Local development use

The current service is intended to be embedded in a trusted local process.

Example lifecycle:

```python
from oiiids.security import HMACSigner
from oiiids.service import ResourceExchangeService
from oiiids.store import InMemoryResourceStore

store = InMemoryResourceStore()
signer = HMACSigner(
    key_id="dev-node",
    secret=b"replace-this-development-secret",
)
service = ResourceExchangeService(store=store, signer=signer)
```

The HMAC signer is for local testing only. It does not provide independent public-key identity between nodes because every verifier with the secret can also forge signatures.

## Safe deployment model

Deploy OIIIDS only behind the authenticated Civilisation.One gateway.

```text
MirrorME member node
  -> authenticated Civilisation.One gateway
  -> authorization and consent policy
  -> OIIIDS resource service
  -> durable resource store
  -> Observer audit adapter
```

The browser must not write directly to the resource store. MirrorME clients must not call private MKone components directly.

### Minimum production components

Before any external deployment, replace or add:

1. Ed25519 or equivalent asymmetric signatures.
2. Key identifiers, revocation, rotation, and expiration.
3. Operating-system or hardware-backed secret storage.
4. Durable SQLite for a single local node, or PostgreSQL for a shared service.
5. Encryption at rest and TLS in transit.
6. Authenticated gateway identity mapped to an internal principal.
7. Policy checks independent from resource metadata.
8. Rate limiting, quotas, payload limits, and request timeouts.
9. Immutable audit records separate from operational logs.
10. Tested backup, restore, and corruption-recovery procedures.

## Configuration management

Keep configuration outside source control.

Recommended environment variables for a future service wrapper:

```text
OIIIDS_ENVIRONMENT=development
OIIIDS_DATABASE_URL=
OIIIDS_SIGNING_KEY_ID=
OIIIDS_PRIVATE_KEY_FILE=
OIIIDS_MAX_RESOURCE_BYTES=10485760
OIIIDS_ALLOWED_CLOCK_SKEW_SECONDS=30
OIIIDS_AUDIT_ENABLED=true
```

Never commit:

- private keys
- HMAC secrets
- API tokens
- database passwords
- member data
- decrypted private resources
- `.env` files

Use separate keys and databases for development, staging, and production.

## Identity and authorization

Resource metadata is descriptive, not authoritative.

Do not trust these fields as proof of identity or permission:

- creator names supplied by a client
- owner fields inside a payload
- OpenTelemetry baggage
- trace attributes
- node labels
- declared trust levels

Effective identity must come from a verified gateway session. Effective authorization must be evaluated by server-side policy.

Recommended order:

```text
authenticate principal
  -> resolve node/member identity
  -> evaluate resource policy
  -> validate envelope and payload limits
  -> perform operation
  -> record audit event
```

## Key management

### Development

Generate a unique random HMAC secret for each local environment. Never reuse a production secret in development.

### Production

Use asymmetric signing:

- private key remains on the originating MirrorME node or trusted signing service
- Civilisation.One stores only public verification material
- every key has a stable key ID
- rotations create new key records rather than overwriting history
- revoked keys remain available for historical verification with revocation timestamps

Do not log keys, signatures' source material, authorization headers, or decrypted payloads.

## Resource publication rules

Before accepting a publication:

1. Confirm the authenticated principal may publish under the resource namespace.
2. Reject oversized payloads before parsing deeply.
3. Canonicalize the payload deterministically.
4. Compute and verify the content digest.
5. Verify the signature against the authorized key.
6. Reject duplicate version identifiers with different content.
7. Preserve parent and provenance references.
8. Write the resource atomically.
9. Append an audit event only after the storage result is known.

Published versions are immutable. Corrections create a new version.

## Reading and selective mirroring

A MirrorME node should pull only resources allowed by both:

- Civilisation.One authorization policy
- the node's local mirroring policy

Recommended local controls:

```yaml
mirroring:
  maximum_resource_bytes: 10485760
  maximum_resources_per_sync: 1000
  allow_public: true
  allow_group: true
  allow_private: false
  trusted_namespaces:
    - civilisation.one/research
    - civilisation.one/education
```

Verify digest and signature before exposing a downloaded resource to indexing, models, tools, or users.

Quarantine invalid resources rather than attempting automatic repair.

## Updates and rollback

Use branch and pull-request deployment. Do not patch production directly.

Recommended process:

```text
feature branch
  -> tests
  -> security review
  -> pull request
  -> protected-branch checks
  -> merge
  -> staged deployment
  -> smoke tests
  -> production rollout
```

For rollback:

- roll back executable code to the previous known-good commit
- do not delete already published immutable resources
- publish corrective withdrawal or superseding resources where necessary
- retain audit records describing the rollback

## Backups

For a durable implementation, back up:

- resource envelopes
- payload blobs
- provenance indexes
- public key registry
- authorization policy versions
- Observer audit records

Test restoration regularly. A backup that has not been restored in a test is not considered verified.

## Logging and telemetry

Operational logs and OpenTelemetry data must not contain:

- raw private resource payloads
- prompts or completions containing member data
- bearer tokens
- signing material
- email addresses unless explicitly required and protected
- authorization decisions' secret inputs

Telemetry is for correlation and system health. It is not an authorization source.

Observer audit records should be separate, integrity-protected, and restricted.

## Incident handling

On suspected key compromise:

1. Disable the affected key for new publications.
2. Record the revocation time.
3. Issue a replacement key.
4. Identify all resources signed after the suspected compromise time.
5. Re-verify or republish affected resources.
6. Preserve the original history and incident audit trail.

On corrupted storage:

1. Stop writes.
2. Snapshot the affected storage for investigation.
3. Restore from a verified backup.
4. Recompute all content and envelope digests.
5. Compare against audit and provenance records.
6. Resume service only after integrity checks pass.

## Safe-use rules for members

- Treat externally supplied resources as untrusted until verified.
- Do not publish secrets, credentials, private keys, or unnecessary personal data.
- Check visibility and recipient policy before publication.
- Keep evidence, inference, hypothesis, and opinion clearly distinguished.
- Do not present a signature as proof that a claim is scientifically true; it proves who signed specific bytes.
- Do not use reputation, majority vote, or AI confidence as a substitute for evidence.
- Preserve conflicting knowledge claims until reviewed rather than silently deleting one branch.
- Require explicit authorization for withdrawal, deletion, or access-policy changes.

## Management checklist

Daily or per deployment:

- verify health and error rates
- review authorization denials and integrity failures
- confirm backups completed
- check storage growth and quotas
- inspect failed signature verification events

Weekly:

- review dependency and security updates
- test a sample restore
- audit active signing keys and service accounts
- review quarantined resources

Before production release:

- all tests pass
- no development HMAC signer is enabled
- no secret is present in repository history
- TLS and authentication are enforced
- resource-size and rate limits are enabled
- backup restoration has been tested
- audit storage is operational
- rollback procedure has been exercised

## Current deployment conclusion

The merged OIIIDS core is deployable for local development and integration testing only. Public or member-facing production deployment must wait until asymmetric signing, durable storage, authenticated APIs, encryption, and operational controls are implemented and tested.
