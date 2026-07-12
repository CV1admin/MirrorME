# MirrorME Quantum Network Integration Protocol

Protocol identifier:

```text
QNIP-ME/v0.1
```

Status: experimental, simulation-first engineering specification.

Owner context: Civilisation.One / MKone / MirrorME.

Date: 2026-07-12.

---

## 1. Purpose

QNIP-ME defines how MirrorME and MKone may request, coordinate, observe, verify, and audit quantum-network resources without coupling the application layer to a specific quantum hardware platform.

The protocol treats MKone as the orchestration, verification, and governance layer above regional controllers and quantum-node runtimes. MKone does not perform pulse-level hardware control.

This document uses the terms **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** as normative requirements.

---

## 2. Truth boundary

QNIP-ME is an integration and control protocol. It is not evidence that a physical quantum network exists or that entanglement has been generated.

A deployment MUST label every event as one of:

```text
SIMULATED
HARDWARE_REPORTED
HARDWARE_VERIFIED
HYBRID
```

The following claims are prohibited unless supported by hardware evidence and an explicit verification method:

- successful physical entanglement
- quantum teleportation
- quantum-secure communication
- quantum identity verification
- biological or consciousness verification
- faster-than-light communication
- external account ownership

Simulation data MUST NOT be presented as physical telemetry.

---

## 3. Scope

QNIP-ME covers:

- node registration and capability discovery
- policy authorization and admission control
- topology and resource-state reporting
- path computation
- quantum-memory reservation
- Bell-pair generation requests
- heralding-event correlation
- memory lifecycle tracking
- purification or distillation requests
- entanglement swapping requests
- fidelity and timing verification
- delivery and consumption records
- failure handling
- tamper-evident audit records
- simulation and hardware-adapter boundaries

QNIP-ME does not define:

- laser pulse sequences
- photonic source construction
- detector electronics
- quantum-memory physics
- a specific QEC code
- a specific repeater generation
- a new cryptographic identity system
- a replacement for authenticated classical networking

---

## 4. Architectural model

### 4.1 Three planes

```text
Governance Plane
    |
    | policy, authorization, priority, audit requirements
    v
Classical Control Plane
    |
    | scheduling, routing, heralding, resource state, commands
    v
Quantum Resource Plane
    |
    | photons, qubits, memories, gates, measurements
    v
Physical or simulated quantum substrate
```

Control direction:

```text
G -> C -> Q
```

Evidence and telemetry direction:

```text
Q -> C -> G
```

The governance plane MUST NOT directly issue pulse-level instructions to hardware.

### 4.2 Communication channels

QNIP-ME separates three channel classes:

1. **Quantum channel**
   - photons or other physical quantum carriers
   - entanglement-distribution operations
   - no classical application payload

2. **Real-time classical channel**
   - hardware timing
   - heralding
   - detector outcomes
   - Bell-state-measurement outcomes
   - swap coordination
   - low-latency state transitions

3. **Non-real-time classical channel**
   - topology exchange
   - policy decisions
   - session setup
   - resource reservation
   - audit logs
   - configuration and diagnostics

A quantum link MAY include a dedicated classical coordination channel, but the quantum and classical records MUST remain logically distinguishable.

---

## 5. Components and responsibilities

### 5.1 MirrorME UI

MirrorME MAY:

- submit high-level quantum service intents
- display topology and resource state
- display session lifecycle
- display verified and simulated telemetry
- inspect audit evidence
- cancel a pending request when policy permits

MirrorME MUST NOT:

- directly drive quantum hardware
- generate hardware timing pulses
- bypass a regional controller
- mark a session verified solely from UI state

### 5.2 MKone governance coordinator

MKone is responsible for:

- policy evaluation
- operator and application authorization
- priority assignment
- purpose limitation
- admission constraints
- audit-policy selection
- approval or rejection of service intents

MKone produces an authorization decision, not a physical hardware command.

### 5.3 QNIP coordinator

The QNIP coordinator is responsible for:

- translating authorized intent into a quantum service request
- selecting candidate paths
- reserving resources
- coordinating controllers
- tracking lifecycle state
- correlating evidence
- calculating readiness and confidence indicators
- exposing stable APIs to MirrorME

### 5.4 Regional quantum controller

A regional controller is responsible for:

- managing nodes within an administrative or timing domain
- applying local scheduling policy
- translating abstract operations into vendor-specific adapter calls
- reporting topology and capabilities
- enforcing memory and timing deadlines
- collecting hardware evidence

### 5.5 Quantum node runtime

A node runtime is responsible for:

- local link-generation attempts
- memory allocation and release
- local gates and measurements through an adapter
- heralding-event production
- pair-ID association
- local expiry enforcement
- reporting device health and calibration state

### 5.6 Hardware or simulator adapter

Every node runtime MUST use an adapter with an explicit mode:

```text
SIMULATOR
HARDWARE
HYBRID
```

The adapter MUST expose capability metadata and MUST NOT silently substitute simulated results for failed hardware operations.

---

## 6. Identity and trust model

### 6.1 Local MirrorME handshake

`MirrorME-Local-Handshake/v0.1` may establish a local UI session boundary. It is not sufficient authentication for a physical quantum network.

A verified local MirrorME session MAY authorize access to local simulation features, subject to local policy.

It MUST NOT, by itself, authorize:

- remote node control
- hardware reservation
- quantum key retrieval
- production network configuration
- access to raw detector or key material

### 6.2 Production control-plane identity

Production controllers and nodes MUST use authenticated classical identities. A deployment SHOULD use:

- mutually authenticated transport
- hardware-backed or operating-system-backed private keys
- certificate or explicit key allowlists
- replay protection
- short-lived authorization tokens
- role and scope restrictions
- post-quantum-capable algorithm agility

Quantum communication does not remove the requirement to authenticate the classical channel.

### 6.3 Identifiers

The following identifiers are opaque strings or UUIDs:

```text
network_id
controller_id
node_id
link_id
request_id
session_id
reservation_id
pair_id
memory_slot_id
event_id
audit_id
```

Identifiers MUST NOT encode secret key material.

---

## 7. Capability model

Each node MUST publish a capability document.

Example:

```json
{
  "protocol": "QNIP-ME/v0.1",
  "node_id": "qnode-pl-001",
  "controller_id": "qctrl-pl-central",
  "mode": "SIMULATOR",
  "roles": ["END_NODE", "REPEATER"],
  "quantum_interfaces": [
    {
      "interface_id": "qi-0",
      "carrier": "PHOTONIC",
      "encoding": "POLARIZATION",
      "wavelength_nm": 1550.0
    }
  ],
  "memory": {
    "slots": 16,
    "coherence_model": "ADAPTER_REPORTED",
    "max_reported_lifetime_ms": 100.0
  },
  "operations": [
    "GENERATE_LINK_PAIR",
    "STORE_PAIR",
    "PURIFY_PAIR",
    "SWAP_PAIR",
    "MEASURE_PAIR",
    "RELEASE_PAIR"
  ],
  "timing": {
    "source": "SYSTEM_CLOCK",
    "quality": "UNVERIFIED",
    "max_offset_ns": null
  },
  "calibration": {
    "state": "SIMULATED",
    "valid_until": null
  }
}
```

A coordinator MUST reject a path when any required operation is unsupported by a node on that path.

---

## 8. Entanglement resource lifecycle

The canonical Bell-pair lifecycle is:

```text
REQUESTED
  -> RESERVED
  -> GENERATING
  -> HERALDED
  -> STORED
  -> PURIFYING
  -> SWAPPING
  -> VERIFIED
  -> CONSUMED
```

Not every session requires `PURIFYING` or `SWAPPING`; these states MAY be skipped when the requested service and topology do not require them.

Terminal exception states are:

```text
FAILED
EXPIRED
CANCELLED
RELEASED
```

### 8.1 State rules

- `REQUESTED`: service request accepted for evaluation.
- `RESERVED`: required node, memory, channel, and timing resources reserved.
- `GENERATING`: elementary-link generation attempts are active.
- `HERALDED`: a correlated heralding event reports candidate pair generation.
- `STORED`: both pair halves are associated with valid memory slots or immediate-use endpoints.
- `PURIFYING`: two or more candidate pairs are being consumed to improve a retained pair.
- `SWAPPING`: Bell-state measurements are extending entanglement across hops.
- `VERIFIED`: the service-specific verification policy has passed.
- `CONSUMED`: the application has measured, teleported through, or otherwise consumed the resource.
- `EXPIRED`: memory age or policy deadline has been exceeded.

A pair MUST NOT transition to `VERIFIED` solely because a command completed successfully. Verification requires evidence defined by the session policy.

---

## 9. Quantum service request

Example request:

```json
{
  "protocol": "QNIP-ME/v0.1",
  "request_id": "8b884a5f-2b80-44a7-b676-cf0f3e5ed03b",
  "source_node": "qnode-pl-001",
  "destination_node": "qnode-uk-001",
  "application": "DISTRIBUTED_TEST",
  "purpose": "LAB_VALIDATION",
  "mode_required": "SIMULATOR_OR_HARDWARE",
  "pair_count": 10,
  "minimum_fidelity": 0.85,
  "minimum_rate_bpps": 0.1,
  "maximum_setup_latency_ms": 5000,
  "maximum_pair_age_ms": 50,
  "priority": 50,
  "allow_purification": true,
  "allow_multi_hop": true,
  "allow_preemption": false,
  "audit_level": "FULL",
  "requested_by": {
    "application_id": "mirrorme-console",
    "operator_session_id": "local-session-reference"
  }
}
```

### 9.1 Admission constraints

A request MUST be rejected when:

- source or destination is unknown
- requested mode conflicts with the path mode
- required fidelity cannot be conservatively predicted
- memory deadlines cannot be met
- timing quality is insufficient
- policy denies the purpose or operator scope
- required hardware is unhealthy or uncalibrated
- required classical authentication is absent
- resources cannot be reserved without prohibited preemption

---

## 10. Message envelope

Every non-real-time control message MUST use a common envelope.

```json
{
  "protocol": "QNIP-ME/v0.1",
  "message_type": "SESSION_CREATE",
  "message_id": "uuid",
  "correlation_id": "request-or-session-id",
  "sender_id": "component-id",
  "recipient_id": "component-id",
  "sequence": 1,
  "issued_at": "2026-07-12T12:00:00.000000000Z",
  "expires_at": "2026-07-12T12:00:05.000000000Z",
  "mode": "SIMULATED",
  "body": {},
  "auth": {
    "scheme": "DEPLOYMENT_POLICY",
    "key_id": "opaque-key-reference",
    "signature": "base64-or-detached-reference"
  }
}
```

Receivers MUST reject:

- unsupported protocol versions
- expired messages
- duplicate message IDs
- invalid sequence transitions
- unauthorized senders
- mismatched mode declarations
- invalid signatures when signatures are required

---

## 11. Core message types

```text
NODE_REGISTER
NODE_HEARTBEAT
NODE_CAPABILITIES
LINK_STATE_UPDATE
TOPOLOGY_SNAPSHOT
POLICY_DECISION
SESSION_CREATE
SESSION_ACCEPT
SESSION_REJECT
RESOURCE_RESERVE
RESOURCE_RESERVED
RESOURCE_RELEASE
GENERATION_START
GENERATION_ATTEMPT
HERALD_EVENT
MEMORY_STORE
MEMORY_EXPIRE
PURIFICATION_START
PURIFICATION_RESULT
SWAP_START
SWAP_RESULT
PAIR_VERIFY
PAIR_VERIFIED
PAIR_DELIVER
PAIR_CONSUMED
SESSION_CANCEL
SESSION_COMPLETE
SESSION_FAILED
AUDIT_EVENT
```

Real-time hardware messages MAY use a compact binary transport, but they MUST preserve semantic equivalence with the defined event fields.

---

## 12. End-to-end sequence

### Stage 0 — Local and application boundary

1. MirrorME establishes its local session boundary.
2. MirrorME submits a high-level intent.
3. MKone evaluates operator scope, application purpose, and governance policy.
4. A policy decision is issued.

### Stage 1 — Discovery

1. The QNIP coordinator obtains a current topology snapshot.
2. Controllers provide node and link capabilities.
3. Unhealthy, stale, uncalibrated, or incompatible resources are excluded.

### Stage 2 — Path and admission

1. Candidate paths are generated.
2. Fidelity, rate, memory, timing, and policy constraints are evaluated.
3. Admission control accepts, rejects, or queues the request.
4. A selected path is recorded with its prediction inputs.

### Stage 3 — Reservation

1. Memory slots are reserved.
2. quantum interfaces are reserved.
3. timing windows are reserved.
4. classical real-time correlation channels are prepared.
5. all reservations receive an expiry deadline.

### Stage 4 — Elementary-link generation

1. Controllers schedule generation attempts.
2. Node runtimes execute adapter-specific operations.
3. Heralding events are correlated by attempt ID and timing window.
4. Candidate pairs receive pair IDs.
5. Failed or ambiguous attempts are discarded.

### Stage 5 — Storage and error management

1. Candidate pair halves are associated with memory slots.
2. Pair age starts from the adapter-defined creation or heralding reference.
3. Purification is performed only when permitted and resource-feasible.
4. Pairs below the service threshold are discarded or retried.

### Stage 6 — Swapping

1. Swap operations are scheduled from the selected path plan.
2. Bell-state-measurement results are reported over the real-time classical channel.
3. Endpoint correction metadata is correlated with the resulting pair.
4. Consumed intermediate pairs are released.
5. Predicted and measured fidelity metadata is updated.

### Stage 7 — Verification and delivery

1. The verification policy evaluates evidence completeness.
2. The pair is marked `VERIFIED` only when required checks pass.
3. The application receives a pair reference, not raw private hardware state.
4. The pair is consumed, released, or expired.
5. The session closes with a final audit summary.

---

## 13. Routing and resource model

For a candidate path \(P\), an independent-event approximation MAY estimate generation success as:

```text
p_success(P) = product(p_link_e) * product(p_swap_v)
```

This approximation MUST be labelled as a model, not a measurement.

A path cost MAY be defined as:

```text
J(P) =
    w_loss * [-log(max(p_success(P), epsilon))]
  + w_time * predicted_completion_time(P)
  + w_age  * predicted_max_pair_age(P)
  + w_mem  * memory_pressure(P)
  + w_risk * evidence_uncertainty(P)
```

Subject to:

```text
predicted_fidelity(P) >= requested_minimum_fidelity
predicted_rate(P)     >= requested_minimum_rate
predicted_latency(P)  <= requested_maximum_latency
predicted_pair_age(P) <= requested_maximum_pair_age
```

The fidelity model MUST be adapter-specific or explicitly configured. A generic memory-decay model MAY use:

```text
F(t) = F_inf + [F_0 - F_inf] * exp(-t / T_coh)
```

where `F_inf`, `F_0`, and `T_coh` are measured, calibrated, simulated, or conservatively configured values. Their provenance MUST be recorded.

Routing MUST consider more than hop count. At minimum it SHOULD consider:

- link success probability
- generation rate
- swap success probability
- current memory pressure
- memory lifetime
- predicted fidelity
- purification cost
- timing quality
- controller and node health
- evidence quality

---

## 14. Timing model

Quantum-network operations are deadline-sensitive because memory fidelity degrades and heralding events must be correlated.

Each timing-capable component MUST expose:

```text
clock_source
clock_state
clock_offset_ns
offset_uncertainty_ns
frequency_error_ppb
last_sync_time
holdover_state
timing_domain_id
```

Timestamp fields SHOULD use UTC for human and audit interoperability and MAY additionally use TAI or a monotonic hardware counter for precise event correlation.

A deployment MAY use White Rabbit or another IEEE 1588-compatible timing system. The protocol does not assume sub-nanosecond performance unless the timing adapter reports and verifies it.

A `HERALD_EVENT` MUST include:

```json
{
  "attempt_id": "uuid",
  "link_id": "qlink-001",
  "detector_event_id": "opaque",
  "timestamp_ns": 1783857600000000000,
  "clock_domain": "wr-domain-01",
  "offset_uncertainty_ns": 0.5,
  "coincidence_window_ns": 2.0,
  "result": "CANDIDATE_SUCCESS"
}
```

Events with incompatible clock domains or excessive uncertainty MUST NOT be correlated as a verified heralding success.

---

## 15. API surface

The stable local coordinator API is versioned independently from vendor adapters.

Suggested endpoints:

```text
GET    /qnet/v1/health
GET    /qnet/v1/capabilities
GET    /qnet/v1/topology
GET    /qnet/v1/nodes
GET    /qnet/v1/nodes/{node_id}
POST   /qnet/v1/sessions
GET    /qnet/v1/sessions/{session_id}
POST   /qnet/v1/sessions/{session_id}/cancel
GET    /qnet/v1/sessions/{session_id}/events
GET    /qnet/v1/audit/{audit_id}
```

Controller-facing endpoints or message-bus topics MAY be separate from the MirrorME-facing API.

A production API MUST NOT expose raw key material, private keys, seed values, detector secrets, or unrestricted hardware commands.

---

## 16. MirrorME local bridge integration

The existing MirrorME bridge remains the local browser integration boundary.

Recommended topology:

```text
MirrorME UI
    |
    | localhost:8765
    v
MirrorME local bridge
    |
    | high-level /api/qnet proxy only
    v
QNIP coordinator sidecar
    |
    | authenticated controller protocol
    v
Regional controllers
    |
    v
Quantum node runtimes -> hardware or simulator adapters
```

Recommended sidecar default:

```text
http://127.0.0.1:8770
```

The bridge SHOULD expose only:

```text
GET  /api/qnet/health
GET  /api/qnet/topology
POST /api/qnet/sessions
GET  /api/qnet/sessions/{session_id}
POST /api/qnet/sessions/{session_id}/cancel
```

Rules:

- quantum-network routes MUST be disabled by default
- activation MUST require explicit configuration
- the sidecar MUST bind to loopback by default
- wildcard CORS MUST NOT be used for production hardware access
- MirrorME MUST send only high-level intents
- the bridge MUST NOT accept pulse-level or vendor-native hardware commands
- remote controllers MUST require separate authenticated transport
- local handshake state MUST NOT be treated as remote controller identity

---

## 17. Evidence and verification

A `PAIR_VERIFY` policy MAY require:

- complete heralding evidence
- matching pair IDs at both endpoints
- compatible timing domains
- memory-slot association
- no expired reservation
- age below the service maximum
- fidelity estimate with provenance
- required swap outcomes
- required purification outcomes
- controller signatures
- calibration validity
- hardware mode consistency

Verification result:

```json
{
  "pair_id": "pair-uuid",
  "state": "VERIFIED",
  "mode": "HARDWARE_REPORTED",
  "fidelity": {
    "value": 0.88,
    "method": "ADAPTER_ESTIMATE",
    "confidence": 0.72,
    "provenance": ["calibration-42", "swap-event-19"]
  },
  "age_ms": 12.4,
  "evidence_complete": true,
  "verified_at": "2026-07-12T12:00:01.100000000Z",
  "verifier_id": "qnip-coordinator-01"
}
```

`HARDWARE_REPORTED` means hardware or controller telemetry reported the event. It does not automatically mean the event was independently validated.

`HARDWARE_VERIFIED` requires a deployment-defined independent verification procedure.

---

## 18. Audit model

Every state transition MUST create an audit event when `audit_level` is `FULL`.

Audit events SHOULD be append-only and hash chained:

```text
h_i = H(h_(i-1) || canonical_json(event_i))
```

An audit record SHOULD contain:

```text
audit_id
event_id
session_id
pair_id
previous_hash
event_hash
actor_id
action
old_state
new_state
timestamp
mode
evidence_references
policy_decision_reference
```

Audit logs MUST NOT include:

- raw quantum keys
- private keys
- passwords
- seed phrases
- unrestricted detector dumps containing sensitive material
- personal data not required by policy

A blockchain anchor MAY record an audit hash, but the operational event data SHOULD remain off-chain and access controlled.

---

## 19. Failure codes

```text
QNIP_UNAUTHORIZED
QNIP_POLICY_DENIED
QNIP_UNKNOWN_NODE
QNIP_INCOMPATIBLE_CAPABILITY
QNIP_NO_PATH
QNIP_RESOURCE_EXHAUSTED
QNIP_RESERVATION_EXPIRED
QNIP_TIMING_UNLOCKED
QNIP_TIMING_UNCERTAIN
QNIP_GENERATION_FAILED
QNIP_HERALD_AMBIGUOUS
QNIP_MEMORY_EXPIRED
QNIP_FIDELITY_BELOW_THRESHOLD
QNIP_PURIFICATION_FAILED
QNIP_SWAP_FAILED
QNIP_EVIDENCE_INCOMPLETE
QNIP_MODE_MISMATCH
QNIP_ADAPTER_UNAVAILABLE
QNIP_CONTROLLER_UNREACHABLE
QNIP_CANCELLED
QNIP_INTERNAL_ERROR
```

Failures MUST include whether retry is safe:

```json
{
  "error": "QNIP_MEMORY_EXPIRED",
  "retryable": true,
  "stage": "STORED",
  "detail": "Pair exceeded the application maximum age.",
  "evidence_reference": "audit-event-uuid"
}
```

---

## 20. Safety and security requirements

- Classical control channels MUST be authenticated.
- Authorization MUST be evaluated before reservation or hardware action.
- Replayed commands MUST be rejected.
- Expired reservations MUST be released automatically.
- A node MUST fail closed when mode or identity cannot be established.
- Hardware adapters MUST validate command ranges.
- The coordinator MUST apply rate limits and request quotas.
- Production hardware control MUST use an explicit allowlist.
- QKD output, when present, MUST be handled as key material and never logged as ordinary telemetry.
- Quantum resources MUST NOT be described as transmitting ordinary messages faster than light.
- A simulated result MUST remain marked simulated throughout its lifecycle and audit trail.
- AI-generated recommendations MAY assist scheduling but MUST NOT bypass deterministic safety and policy gates.

---

## 21. Conformance tests

A QNIP-ME implementation SHOULD pass at least these tests:

1. Reject unknown protocol version.
2. Reject expired message.
3. Reject duplicate message ID.
4. Reject invalid state transition.
5. Reject hardware-required request on simulator-only path.
6. Reject insufficient fidelity prediction.
7. Reject missing timing lock when required.
8. Expire a stored pair after its deadline.
9. Release resources after failure.
10. Preserve `SIMULATED` mode through all derived events.
11. Prevent local handshake from authorizing remote hardware control.
12. Prevent wildcard browser origin from accessing production controller routes.
13. Verify audit hash-chain continuity.
14. Keep raw key material out of logs.
15. Correlate heralding events only inside the configured timing window.
16. Reject a swap when input pair references are missing or consumed.
17. Mark verification incomplete when evidence is missing.
18. Complete a simulator end-to-end lifecycle through `CONSUMED`.

---

## 22. Implementation phases

### Phase 0 — Deterministic simulator

```text
Topology model
Node capability registry
Bell-pair lifecycle engine
Routing and admission control
Event stream
Audit chain
MirrorME status UI
```

### Phase 1 — Adapter contract

```text
Simulator adapter
Mock hardware adapter
Timing adapter
Controller API
Conformance tests
Failure injection
```

### Phase 2 — Single laboratory link

```text
Two end nodes
One elementary quantum link
Real heralding telemetry
Memory or immediate measurement path
Strict hardware/simulation separation
```

### Phase 3 — Repeater-assisted laboratory network

```text
Multiple links
One or more repeater nodes
Memory reservation
Purification support
Entanglement swapping
End-to-end verification
```

### Phase 4 — Multi-domain orchestration

```text
Regional controllers
Federated policy
Cross-domain authentication
Service-level constraints
Independent evidence verification
Operational security review
```

---

## 23. Initial status

```text
Protocol document:                 implemented
MirrorME local handshake:          implemented separately
Local chat bridge:                 implemented separately
QNIP coordinator sidecar:          not implemented
Quantum service API:               not implemented
Topology registry:                 not implemented
Lifecycle simulator:               not implemented
Hardware adapter:                  not implemented
White Rabbit timing adapter:       not implemented
Independent quantum verification:  not implemented
```

---

## 24. References

- RFC 9340, *Architectural Principles for a Quantum Internet*, IRTF Quantum Internet Research Group, March 2023. This is an informational architectural reference, not an Internet Standards Track protocol.
- CERN White Rabbit Project documentation and IEEE 1588 timing references.
- MirrorME Local Handshake Protocol, `docs/LOCAL_HANDSHAKE_PROTOCOL.md`.
- MirrorME local bridge, `local_bridge/mirrorme_bridge.py`.

---

## 25. Canonical definition

```text
MKone-QNet is the Civilisation.One quantum-network orchestration,
verification, and governance layer.

QNIP-ME is its integration protocol between MirrorME, governance,
classical controllers, node runtimes, and simulated or physical
quantum resources.

It coordinates quantum resources; it does not claim to create new
physics, replace hardware, or prove quantum events without evidence.
```
