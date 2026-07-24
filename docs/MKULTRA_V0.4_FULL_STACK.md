# MKultra v0.4 Full Stack

## Release identity

```text
Name:      MKultra
Version:   0.4.0
Codename:  Governed Thin Line
Status:    integration-development
Model:     mkultra:0.4
```

MKultra v0.4 extends the transactional and hash-anchored v0.3 runtime with:

1. a provenance-backed Thin Line claim registry;
2. explicit epistemic-layer separation;
3. a hash-linked evolution-proposal chain;
4. deterministic evaluation metadata;
5. exact human approval for change-packet export;
6. a loopback-only local API;
7. a browser governance console;
8. an Ollama persona and Windows launch/update scripts.

It does **not** implement autonomous self-modification.

## Authority model

The allowed sequence is:

```text
source claim
  -> evolution proposal
  -> structured evaluation
  -> human review
  -> approval for export
  -> inspectable change packet
  -> human-reviewed Git branch or pull request
```

The forbidden sequence is:

```text
model output
  -X-> execute patch
  -X-> update weights
  -X-> update policy
  -X-> change identity
  -X-> write durable memory
  -X-> perform external action
```

An approved packet contains:

```json
{
  "execution_authorized": false,
  "operator_action_required": true,
  "allowed_next_step": "human-reviewed branch or pull request"
}
```

## Epistemic layers

| Layer | Meaning | May be treated as established fact? |
|---|---|---|
| `MATHEMATICAL_DEFINITION` | Project-defined formal object | Only as a definition; consistency still requires checking |
| `COMPUTATIONAL_ANALOGY` | Executable structural analogy | No physical interpretation without validation |
| `COGNITIVE_HYPOTHESIS` | Testable behavioral/cognitive proposition | Only after controlled evidence |
| `PHYSICAL_HYPOTHESIS` | Proposed physical mechanism | No; requires equations, units, coupling and experiment |
| `EMPIRICAL_EVIDENCE` | Reproducible measured result | Yes, within its protocol and uncertainty |
| `MYTHOLOGY_STORY` | Narrative or symbolic framework | No empirical authority |

A mythology-layer claim cannot, by itself, pass an engineering evolution review.

## Provenance sources

The v0.4 source manifest records SHA-256 digests and classifications for:

- `Chapter_0_Hyper_Symmetry_Nothing.md`;
- `chapter_1_trialfa.md`;
- `chapter_2_thin_line_paradox_group.md`;
- `chapter_3_thin_line_mirror_engine_rigorous.md`;
- `Model Self-Evolution Instructions.txt`.

The source manifest proves which bytes were classified. It does not prove that a source claim is correct.

## Hash integrity

The claim and proposal registries are append-only hash chains.

For record `i`:

```text
H_i = SHA256(canonical(record_i_without_hash))
previous_hash_i = H_(i-1)
```

Mutation is detected by recomputing every record. Truncation or wholesale substitution requires a separately retained anchor:

```text
trusted anchor = (head_hash, record_count)
```

The current implementation uses deterministic sorted-key JSON. Production requires an audited RFC 8785 canonicalization implementation.

## Governed evaluation

Every proposal must define:

- objective;
- target components;
- evidence claim identifiers;
- predicted benefit;
- risks;
- test plan;
- rollback plan;
- requested changes.

Evaluation dimensions are:

```text
evidence
 testability
 reversibility
 safety
 integrity
```

Each score is finite and bounded:

```text
0 <= score <= 1
```

The default review threshold is `0.75`. Passing the threshold moves the proposal to `REVIEW_REQUIRED`, never directly to execution.

## Local API

Start the v0.4 bridge on loopback:

```powershell
py -3 local_bridge\mkultra_v04_bridge.py --model "mkultra:0.4"
```

Read-only routes:

```text
GET /api/v04/status
GET /api/v04/claims
```

Verified-local-session routes:

```text
POST /api/v04/evolution/propose
POST /api/v04/evolution/evaluate
POST /api/v04/evolution/approve
```

The local handshake is session confirmation only. It is not cryptographic identity proof.

## Browser console

Open:

```text
http://localhost:3000/#/mkultra-v04
```

The console displays:

- claim-registry integrity;
- claim layers and source hashes;
- proposal-chain integrity;
- review threshold;
- proposal/evaluation/approval counts;
- exported audit packets;
- the permanent `execution_authorized: false` boundary.

## One-command Windows launch

```powershell
cd "C:\Users\TheSteelWill\MirrorME"
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\run-mkultra-v0.4.ps1
```

The launcher:

1. locates `python`, `py -3` or `python3`;
2. verifies Ollama;
3. builds `mkultra:0.4` from `qwen3:8b` when absent;
4. starts the v0.4 bridge on port `8765`;
5. starts Vite on port `3000`;
6. opens `/#/mkultra-v04`.

## Update and verification

```powershell
cd "C:\Users\TheSteelWill\MirrorME"
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\update-mkultra-v0.4.ps1
```

Validation-only:

```powershell
.\scripts\update-mkultra-v0.4.ps1 -SkipModel
```

Model-only:

```powershell
.\scripts\update-mkultra-v0.4.ps1 -SkipChecks
```

Manual checks:

```powershell
npm ci
npm run check
py -3 -m unittest discover -s tests -p "test_*.py" -v
ollama show mkultra:0.4
```

## Production gates

v0.4 remains non-production until all of the following are implemented and independently reviewed:

- RFC 8785 canonicalization;
- real cryptographic signatures and trust roots;
- authenticated reviewer-role binding;
- encrypted durable storage and deletion policy;
- concurrency and property-based testing;
- replay protection across process restarts;
- model, retrieval and hallucination benchmarks;
- security review of the local bridge and exported packets;
- documented release signing and rollback procedure.
