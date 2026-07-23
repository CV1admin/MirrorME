# OIIIDS Resource Exchange

**OIIIDS** means **Origin Irreducible Intelligence Information Distribution System**.

It defines the resource-centric exchange loop:

```text
MirrorME member node
  -> create and hash a resource
  -> authorise and sign publication
  -> Civilisation.One registry/gateway
  -> validate, index and distribute
  -> authorised MirrorME member node
  -> verify, read and create a referenced next version
  -> repeat
```

## Design principles

1. **Resource, not message, is the durable exchange unit.**
2. **Every version is immutable.** A changed resource receives a new version and references the previous envelope digest.
3. **Local autonomy is preserved.** MirrorME nodes retain local stores and explicit policy boundaries.
4. **Identity and authority are external inputs.** Telemetry, trace baggage and resource metadata never establish authorisation.
5. **Integrity is checked before access.** Content hashes and signatures are verified before a resource is returned.
6. **Audit and observability remain separate.** Observer records integrity-relevant events; OpenTelemetry records operational behavior.
7. **No secrets enter resources, logs, traces or browser code.**

## Current implementation

The first implementation is intentionally transport-neutral and includes:

- immutable versioned resource manifests;
- canonical JSON hashing;
- access scopes and explicit allowed principals;
- a pluggable signing interface;
- an in-memory development store;
- publish, read and next-version operations;
- an Observer sink interface;
- integrity and access-control tests.

The included `HMACSigner` is for local development only. Production should use asymmetric node signatures backed by a protected keystore.

## Python example

```python
from oiiids import (
    AccessScope,
    InMemoryResourceStore,
    ResourceEnvelope,
    ResourceExchangeService,
    ResourceManifest,
    ResourcePayload,
)
from oiiids.security import HMACSigner

service = ResourceExchangeService(
    store=InMemoryResourceStore(),
    signer=HMACSigner(b"replace-with-at-least-32-secret-bytes"),
)

manifest = ResourceManifest.create(
    resource_type="knowledge.note",
    creator_node_id="mirrorme-node-a",
    owner_principal="member:marek",
    access_scope=AccessScope.TRUSTED_GROUP,
    allowed_principals=("member:peer",),
)

envelope = ResourceEnvelope.create(
    manifest,
    ResourcePayload(
        media_type="application/json",
        summary="Shared member knowledge",
        data={"statement": "resource-oriented communication"},
    ),
)

result = service.publish(envelope, principal="member:marek")
assert result.accepted
```

## Required production adapters

The next integration stage should add:

- authenticated Civilisation.One principal resolution;
- Ed25519 signatures and key rotation;
- encrypted payload storage;
- SQLite/PostgreSQL/Qdrant persistence adapters;
- MCP resources and tools for discovery and exchange;
- delta manifests and offline synchronization;
- conflict detection for concurrent versions;
- OpenTelemetry spans and metrics;
- Observer hash-chain adapter;
- retention, revocation and deletion-policy enforcement.

## Research basis

The architecture follows established patterns from federated data systems, provenance-preserving member nodes, policy-driven data exchange and decentralized research environments. These support the separation of local ownership, shared registries, explicit policy, provenance and reproducible derivation.

OIIIDS is an engineering name for this project, not an established scientific theory or claim of irreducible intelligence.
