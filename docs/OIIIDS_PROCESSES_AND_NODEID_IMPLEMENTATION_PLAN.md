# OIIIDS Processes and NodeID Implementation Plan

## Purpose

This document defines the implementation sequence for turning the current transport-neutral OIIIDS resource library into a process-driven, node-authenticated subsystem for MirrorME and Civilisation.One.

The plan deliberately separates four concerns:

1. **Node identity** — which cryptographic node produced an operation.
2. **Principal identity** — which authenticated member or service is acting.
3. **Authorization** — whether that principal and node may perform the operation.
4. **Process orchestration** — the deterministic lifecycle through which a resource operation passes.

A resource field, telemetry attribute, trace context value, or caller-supplied node label is never sufficient proof of any of these concerns.

---

## Repository review

### Existing strengths

The current OIIIDS core already provides:

- immutable resource envelope objects;
- deterministic payload canonicalization and SHA-256 digests;
- explicit resource versions and parent-digest provenance;
- access scopes and explicit allowed-principal lists;
- a pluggable signer protocol;
- publish and read integrity checks;
- a resource-store abstraction;
- an Observer audit boundary;
- tests for authorization, tampering, and version chaining.

### Current gaps

The current implementation must not yet be treated as a production node network because:

- `creator_node_id` is an unchecked string;
- the HMAC signer is a shared-secret development mechanism;
- signatures do not identify a public verification key;
- no NodeID registry, node lifecycle, revocation, rotation, or expiry model exists;
- no authenticated operation context binds principal, node and request;
- resource publication is implemented as direct method logic rather than an explicit process state machine;
- no idempotency key or operation record exists;
- audit recording is not transactional with storage;
- access rules still partially derive effective policy from resource metadata;
- the in-memory store is not durable or concurrency-safe;
- no quarantine path exists for malformed or suspicious resources;
- no offline sync, conflict detection or CRDT process exists.

---

# Part I — NodeID subsystem

## 1. NodeID format

Use a stable, self-describing identifier derived from a public key fingerprint:

```text
nodeid:cv1:<base32-sha256-public-key>
```

Example:

```text
nodeid:cv1:m7y2...k9q
```

Properties:

- globally unique without a central sequential allocator;
- stable while the root identity remains valid;
- independently derivable and verifiable;
- contains no member email, device name or other personal information;
- does not itself convey authorization or trust.

The implementation should use the full SHA-256 digest internally. Short display forms are UI-only and must not be accepted by security APIs.

## 2. Node record

```python
@dataclass(frozen=True, slots=True)
class NodeRecord:
    node_id: NodeID
    owner_principal: str
    status: NodeStatus
    created_at: datetime
    activated_at: datetime | None
    suspended_at: datetime | None
    revoked_at: datetime | None
    metadata: Mapping[str, str]
```

Recommended states:

```text
PENDING -> ACTIVE -> SUSPENDED -> ACTIVE
                  -> REVOKED
PENDING -> REJECTED
```

`REVOKED` and `REJECTED` are terminal. Node status transitions require signed governance operations and audit events.

## 3. Verification keys

A node may have multiple historical verification keys:

```python
@dataclass(frozen=True, slots=True)
class NodeKeyRecord:
    key_id: str
    node_id: NodeID
    algorithm: str
    public_key: bytes
    status: KeyStatus
    valid_from: datetime
    valid_until: datetime | None
    revoked_at: datetime | None
    replaces_key_id: str | None
```

Production default:

```text
Ed25519
```

Rules:

- private keys remain on the MirrorME node or protected signing service;
- Civilisation.One stores public keys and lifecycle data only;
- every signature includes `node_id`, `key_id`, algorithm and signing time;
- old public keys remain available for historical verification;
- rotation adds a new key record rather than overwriting the previous record;
- key revocation does not retroactively erase valid historical signatures;
- verification evaluates key validity at the claimed operation time and applies compromise policy separately.

## 4. Node proof

Define a signed proof object:

```python
@dataclass(frozen=True, slots=True)
class NodeProof:
    node_id: NodeID
    key_id: str
    algorithm: str
    signed_at: datetime
    nonce: str
    signature: str
```

The signature covers a domain-separated canonical transcript:

```text
OIIIDS-NODE-PROOF-V1\n
operation_id\n
method\n
resource_digest\n
principal_session_id\n
nonce\n
signed_at
```

This prevents the same signature from being replayed as another operation type or against another resource.

## 5. Principal-to-node binding

Node ownership and session identity are distinct.

An authenticated gateway produces an immutable operation context:

```python
@dataclass(frozen=True, slots=True)
class OperationContext:
    operation_id: UUID
    principal: str
    session_id: str
    node_id: NodeID
    authenticated_at: datetime
    authorization_snapshot_id: str
    trace_context: Mapping[str, str]
```

Rules:

- principal comes from the verified gateway session;
- node identity comes from NodeProof verification;
- server-side policy confirms the principal may operate the node;
- trace context remains operational metadata only;
- authorization is evaluated against a versioned policy snapshot.

---

# Part II — Process orchestration

## 6. Process model

Introduce explicit operation processes instead of embedding the whole lifecycle in one service method.

Initial process types:

```text
NODE_REGISTER
NODE_ACTIVATE
NODE_ROTATE_KEY
NODE_SUSPEND
NODE_REVOKE
RESOURCE_PUBLISH
RESOURCE_READ
RESOURCE_MIRROR
RESOURCE_SUPERSEDE
RESOURCE_WITHDRAW
RESOURCE_SYNC
RESOURCE_QUARANTINE
CONFLICT_RESOLVE
```

Each process has a durable process record:

```python
@dataclass(frozen=True, slots=True)
class ProcessRecord:
    process_id: UUID
    process_type: ProcessType
    state: ProcessState
    operation_id: UUID
    principal: str
    node_id: NodeID
    resource_id: UUID | None
    resource_version: int | None
    created_at: datetime
    updated_at: datetime
    failure_code: str | None
    authorization_snapshot_id: str
```

## 7. Common process states

```text
RECEIVED
  -> AUTHENTICATED
  -> NODE_VERIFIED
  -> AUTHORIZED
  -> VALIDATED
  -> PREPARED
  -> COMMITTED
  -> AUDITED
  -> COMPLETED
```

Failure states:

```text
REJECTED
QUARANTINED
FAILED_RETRYABLE
FAILED_TERMINAL
```

A process may move only through explicitly allowed transitions. Completed and rejected records are immutable.

## 8. Publication process

```text
RECEIVED
  -> validate operation envelope and size limits
AUTHENTICATED
  -> resolve gateway principal and session
NODE_VERIFIED
  -> verify NodeProof and active key
AUTHORIZED
  -> evaluate namespace, owner and publication policy
VALIDATED
  -> canonicalize resource and verify content digest
PREPARED
  -> check idempotency and version uniqueness
COMMITTED
  -> atomically store immutable resource version
AUDITED
  -> append integrity-protected Observer event
COMPLETED
```

Required rejection codes:

```text
invalid_operation
payload_too_large
session_invalid
node_unknown
node_inactive
key_unknown
key_expired
key_revoked
signature_invalid
node_principal_mismatch
publish_forbidden
digest_mismatch
version_conflict
parent_not_found
parent_digest_mismatch
policy_changed
storage_failure
audit_failure
```

## 9. Read and mirror process

```text
RECEIVED
  -> validate query and limits
AUTHENTICATED
  -> resolve principal and node
NODE_VERIFIED
  -> require active node for private or group resources
AUTHORIZED
  -> evaluate server-side read policy
VALIDATED
  -> load and verify resource digest and signature
COMMITTED
  -> record mirror receipt or read receipt where required
AUDITED
  -> append access audit event without private payload
COMPLETED
```

A downloaded resource must be quarantined before indexing or model access when any integrity check fails.

## 10. Node registration process

```text
RECEIVED
  -> validate registration request
AUTHENTICATED
  -> require verified member or service principal
NODE_VERIFIED
  -> verify proof-of-possession of submitted public key
AUTHORIZED
  -> evaluate node-registration policy and quotas
VALIDATED
  -> derive NodeID and reject duplicate/conflicting key material
PREPARED
  -> create PENDING node and key records
COMMITTED
  -> persist records atomically
AUDITED
  -> record registration event
COMPLETED
```

Activation is a separate policy process. Registration must not silently grant platform permissions.

## 11. Key rotation process

A rotation request must be authorized by at least one of:

- the currently valid node key;
- a separately registered recovery key;
- a governed administrator recovery process with enhanced audit.

The rotation operation binds:

- old key ID;
- new public key;
- new key ID;
- activation time;
- optional expiry;
- reason;
- authorization snapshot.

The old key becomes `RETIRED`, unless compromise handling requires `REVOKED`.

---

# Part III — Proposed repository structure

```text
oiiids/
  identity/
    __init__.py
    node_id.py
    models.py
    registry.py
    proofs.py
    keys.py
    policy.py

  processes/
    __init__.py
    models.py
    transitions.py
    engine.py
    repository.py
    errors.py
    idempotency.py

    handlers/
      node_register.py
      node_activate.py
      node_rotate_key.py
      node_suspend.py
      node_revoke.py
      resource_publish.py
      resource_read.py
      resource_mirror.py
      resource_withdraw.py
      resource_sync.py
      conflict_resolve.py

  persistence/
    sqlite.py
    migrations/

  quarantine/
    models.py
    repository.py

  observer/
    events.py
    adapter.py
```

Existing modules should remain as compatibility boundaries until the new processes are tested. Avoid a single large rewrite.

---

# Part IV — Interfaces

## Node registry

```python
class NodeRegistry(Protocol):
    def register_pending(self, node: NodeRecord, key: NodeKeyRecord) -> None: ...
    def get_node(self, node_id: NodeID) -> NodeRecord | None: ...
    def get_key(self, node_id: NodeID, key_id: str) -> NodeKeyRecord | None: ...
    def list_keys(self, node_id: NodeID) -> Iterable[NodeKeyRecord]: ...
    def transition_node(self, node_id: NodeID, transition: NodeTransition) -> NodeRecord: ...
    def add_key(self, key: NodeKeyRecord) -> None: ...
    def transition_key(self, key_id: str, transition: KeyTransition) -> NodeKeyRecord: ...
```

## Process repository

```python
class ProcessRepository(Protocol):
    def create(self, record: ProcessRecord) -> None: ...
    def get(self, process_id: UUID) -> ProcessRecord | None: ...
    def get_by_operation_id(self, operation_id: UUID) -> ProcessRecord | None: ...
    def transition(self, process_id: UUID, expected: ProcessState, target: ProcessState) -> ProcessRecord: ...
```

## Policy engine

```python
class AuthorizationPolicy(Protocol):
    def authorize(self, request: AuthorizationRequest) -> AuthorizationDecision: ...
```

The policy result includes a stable policy snapshot ID so later audits can identify exactly which rules produced a decision.

---

# Part V — Persistence and transaction boundaries

## SQLite first implementation

Use SQLite for a single local node and integration environment, with:

- WAL mode;
- foreign keys enabled;
- explicit transactions;
- unique constraints on NodeID, key ID, operation ID, resource ID/version and digest;
- append-only audit references;
- migrations committed to the repository.

Recommended tables:

```text
nodes
node_keys
node_principal_bindings
process_records
process_transitions
idempotency_records
resources
resource_versions
resource_receipts
quarantined_resources
policy_snapshots
observer_event_refs
```

## Atomicity

The following must commit in one database transaction where possible:

- process transition to `COMMITTED`;
- immutable resource version write;
- idempotency result write;
- outbox event for Observer/audit processing.

Use a transactional outbox rather than calling a remote audit system inside the primary database transaction. The outbox worker delivers the event and transitions the process from `COMMITTED` to `AUDITED` and `COMPLETED`.

---

# Part VI — Security invariants

The implementation must enforce these invariants:

1. A NodeID is derived from verified public-key material, never accepted as a free-form security assertion.
2. A valid signature proves possession of a key, not member authorization, trustworthiness or scientific truth.
3. Principal authorization is evaluated independently of resource metadata.
4. Every security-sensitive operation binds principal, NodeID, key ID, operation ID, method, resource digest and nonce.
5. Operation IDs are idempotent and cannot produce different successful results.
6. Published resource versions are immutable.
7. Duplicate resource ID/version pairs with different digests are rejected and audited.
8. Revoked nodes cannot create new accepted operations.
9. Historical signatures remain verifiable using retained public-key records and lifecycle timestamps.
10. Telemetry, baggage and UI labels never grant authority.
11. Private payloads, keys and bearer tokens never enter operational telemetry.
12. Integrity failures are quarantined; they are not automatically repaired or indexed.

---

# Part VII — Test programme

## NodeID tests

```text
public key deterministically derives the same NodeID
one-bit public-key change derives a different NodeID
short/display NodeID is rejected by security interfaces
proof-of-possession succeeds for the matching private key
proof fails for altered operation ID, method, digest, nonce or principal session
unknown, expired and revoked keys are rejected
historical signatures verify against their historical validity interval
```

## Process tests

```text
invalid transition is rejected
replayed operation ID returns the original result
same operation ID with different input is rejected
publication cannot skip authentication, node verification or authorization
storage failure does not produce COMPLETED state
outbox retry does not duplicate audit events
policy snapshot changes cause stale prepared operations to re-authorize or fail
```

## Three-node scenarios

```text
Node A publishes version 1
Nodes B and C mirror it
B and C independently create concurrent descendants offline
sync detects concurrent branches
both branches are retained
conflict-resolution process creates a signed superseding resource
all nodes converge on the same accepted history without deleting prior versions
```

## Abuse tests

```text
forged creator_node_id
valid node signature used by unauthorized principal
signature replayed for another method
oversized resource
malformed canonical JSON edge cases
version collision
key rotation race
revoked node publishing from an offline queue
quarantine bypass attempt
telemetry baggage containing fake roles or permissions
```

---

# Part VIII — Implementation phases

## Phase 1 — NodeID primitives

Deliver:

- typed `NodeID` value object;
- Ed25519 key and signature adapter;
- deterministic NodeID derivation;
- node/key lifecycle models;
- in-memory registry;
- NodeProof canonical transcript;
- unit tests.

No network endpoint is included in this phase.

## Phase 2 — Process engine

Deliver:

- process and transition models;
- transition validator;
- idempotency records;
- operation context;
- publication handler using the existing resource store;
- read handler;
- deterministic failure codes;
- unit and integration tests.

## Phase 3 — SQLite persistence

Deliver:

- migrations;
- durable node registry;
- durable process repository;
- durable resource store;
- transactional outbox;
- backup and restore test script;
- corruption and concurrency tests.

## Phase 4 — Node lifecycle handlers

Deliver:

- register;
- activate;
- suspend;
- revoke;
- rotate key;
- recovery path;
- policy snapshots;
- audit events.

## Phase 5 — Gateway/API boundary

Deliver:

- authenticated server-side endpoints;
- strict request schemas;
- payload, timeout and rate limits;
- TLS deployment configuration;
- nonce/replay protection;
- no browser access to private keys or database credentials.

## Phase 6 — Offline sync and conflict processes

Deliver:

- signed sync manifests;
- selective mirroring policy;
- concurrent-branch detection;
- CRDT/change-resource adapters;
- semantic conflict records;
- resolution process;
- checkpoint and compaction policy.

## Phase 7 — Operations and production hardening

Deliver:

- OpenTelemetry with redaction;
- independent Observer adapter;
- key compromise runbook;
- backup and disaster-recovery validation;
- staged deployment and rollback automation;
- security review and threat model.

---

# Part IX — Pull-request sequence

Use small, reviewable pull requests:

```text
PR A: NodeID value objects and Ed25519 primitives
PR B: node registry and lifecycle models
PR C: process-state engine and idempotency
PR D: publish/read process handlers
PR E: SQLite persistence and transactional outbox
PR F: registration, activation and key rotation
PR G: authenticated API boundary
PR H: offline sync, conflict detection and resolution
PR I: telemetry, Observer integration and operational hardening
```

Each PR must include tests and must not enable public deployment before the production gate is satisfied.

---

# Production gate

External member-facing deployment remains prohibited until all of the following are true:

- Ed25519 node signing is enabled and HMAC is disabled outside tests;
- node registration, activation, suspension, revocation and rotation are operational;
- durable storage and migrations are tested;
- authenticated gateway identity is mapped to server-side authorization;
- replay protection and idempotency are enforced;
- resource and operation limits are enforced;
- transactional audit delivery is verified;
- backup restoration and rollback are exercised;
- private data is excluded from telemetry;
- security and abuse tests pass;
- the system has completed a staged integration deployment.

Until then, the system remains a local development and integration-testing implementation.
