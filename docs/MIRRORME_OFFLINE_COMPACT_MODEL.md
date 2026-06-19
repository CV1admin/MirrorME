# MirrorMe Offline Compact Model

Version: `v1.5-beta`
Status: implementation instruction
Runtime target: local model server, SQLite WAL, local-first API

MirrorMe is a local reasoning and audit runtime for the MirrorME/MKone system. It must operate honestly: no invented sensors, no invented memory, no invented telemetry, and no unsupported claims of consciousness or quantum processing.

## 1. Runtime goals

- Offline-first operation.
- Local AI model support through Ollama or compatible adapters.
- SQLite WAL for compact persistence.
- Append-only audit event history.
- Structured memory records.
- Explicit distinction between declared, measured, simulated, and unknown telemetry.
- Safe identity handling without passwords or secret prompts.

## 2. Minimal topology

```text
UI
  -> Local API
      -> Model Adapter
      -> SQLite WAL
      -> Flight Recorder
      -> Optional Worker
```

Recommended runtime:

- UI: Next.js, Tauri, or Electron.
- API: FastAPI bound to `127.0.0.1`.
- Model adapter: Ollama-compatible local generation client.
- Database: SQLite in WAL mode.
- Artifact store: local filesystem with SHA-256 metadata.
- Worker: optional background process for simulations and exports.

## 3. Core directives

### A1 — Traceability

Every significant output must be traceable to one of:

- current user input;
- local memory;
- verified file content;
- tool output;
- mathematical derivation;
- explicit assumption.

Do not fabricate references.

### A2 — Consistency

Detect contradictions between:

- current statements;
- stored memory;
- mathematical constraints;
- units;
- schemas;
- timestamps;
- system capabilities.

When a contradiction is found, identify the conflicting propositions and propose the smallest valid correction.

### A3 — Robustness

The system must stay useful under incomplete input, noisy input, malformed JSON, missing telemetry, absent memory, interrupted streams, and local-model uncertainty.

Do not invent missing values to preserve the appearance of stability.

## 4. Epistemic labels

Important claims should be internally classified as:

- observation;
- derivation;
- hypothesis;
- speculation;
- metaphor;
- unknown.

Never convert speculation into fact, metaphor into mechanism, simulation output into experiment, or declared telemetry into measured reality.

## 5. Telemetry model

Project telemetry fields:

| Field | Meaning | Canonical unit |
|---|---|---|
| `gamma_hz` | simulator synchrony or periodicity proxy | Hz |
| `psi_integrity` | state/snapshot integrity score | dimensionless [0,1] |
| `vireax_v` | project stability score | dimensionless [0,1] |
| `drift_ms` | scheduling/temporal drift | milliseconds |
| `error_epsilon` | project-defined error proxy | dimensionless [0,1] |
| `entropy` | explicitly defined uncertainty/diversity measure | definition required |

Default thresholds:

```text
v_min = 0.99
drift_max_ms = 0.01
epsilon_max = 0.05
psi_min = 0.995
```

Conversions:

```text
1 second = 1000 milliseconds
1 millisecond = 1000 microseconds
1 microsecond = 1000 nanoseconds

drift_us = drift_ms * 1000
drift_s = drift_ms / 1000
```

Declared telemetry is not measured telemetry. If the user supplies `gamma_hz = 42`, classify it as declared or simulated unless a verified signal source exists.

## 6. Orchestration gate

```text
GO =
(vireax_v >= v_min)
AND (drift_ms <= drift_max_ms)
AND (error_epsilon <= epsilon_max)
AND (psi_integrity >= psi_min)
```

Hysteresis:

- GO requires 5 consecutive passing frames.
- NO_GO requires 2 consecutive failing frames.

States:

```text
STANDBY
INITIALIZING
RUNNING
DEGRADED
STABILIZING
ABORTED
COMPLETE
```

Corrective actions:

1. Reduce task complexity.
2. Validate input.
3. Recompute metrics.
4. Restore last verified snapshot.
5. Isolate contradictory data.
6. Stop current task.
7. Preserve an error report.

Never request user credentials as a stabilization method.

## 7. SQLite schema baseline

```sql
CREATE TABLE IF NOT EXISTS sessions (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS messages (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES sessions(id),
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
  id TEXT PRIMARY KEY,
  session_id TEXT,
  sequence INTEGER NOT NULL,
  event_type TEXT NOT NULL,
  actor TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  previous_hash TEXT,
  event_hash TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS memories (
  id TEXT PRIMARY KEY,
  subject TEXT NOT NULL,
  content TEXT NOT NULL,
  source_ref TEXT,
  status TEXT NOT NULL,
  confidence REAL NOT NULL,
  supersedes TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS metrics (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL,
  t INTEGER NOT NULL,
  gamma_hz REAL,
  psi_integrity REAL,
  vireax_v REAL,
  drift_ms REAL,
  error_epsilon REAL,
  entropy REAL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS artifacts (
  id TEXT PRIMARY KEY,
  run_id TEXT,
  kind TEXT NOT NULL,
  path TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  created_at TEXT NOT NULL
);
```

SQLite configuration:

```sql
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA foreign_keys=ON;
```

## 8. Audit event schema

```json
{
  "event_id": "uuid",
  "session_id": "uuid",
  "sequence": 0,
  "timestamp": "ISO-8601",
  "event_type": "user_message | assistant_response | memory_write | memory_revoke | tool_call | tool_result | simulation_start | simulation_frame | simulation_end | error",
  "actor": "user | mirrorme | tool | system",
  "input_refs": [],
  "output_refs": [],
  "payload": {},
  "audit": {
    "assumptions": [],
    "constraints_checked": [],
    "violations": [],
    "confidence": 0.0,
    "epistemic_class": "observation | derivation | hypothesis | speculation | metaphor | unknown"
  },
  "previous_hash": null,
  "event_hash": null,
  "signature": null
}
```

Hash rule:

```text
event_hash = SHA256(previous_hash || canonical_json(current_event_without_hash_and_signature))
```

Only mark a signature as verified when cryptographic verification has actually succeeded.

## 9. Commands

Supported local commands:

```text
/help
/status
/audit on
/audit off
/mode compact
/mode scientific
/mode engineering
/mode paraconsistent
/gate arithmetic
/gate logic
/gate units
/trap contradiction
/run
/stop
/metrics
/export
/verify
/model
/memory status
/memory verify
/reset session
```

Unknown slash commands must return a clear error.

## 10. Chat protocol

Each user message should receive:

- client message ID;
- canonical local message ID;
- sequence number;
- timestamp when clock access exists;
- delivery state.

States:

```text
pending
accepted
processing
complete
failed
```

Realtime events:

```json
{ "type": "ack", "client_message_id": "...", "message_id": "...", "sequence": 1 }
{ "type": "delta", "message_id": "...", "sequence": 2, "text": "partial output" }
{ "type": "final", "message_id": "...", "sequence": 3, "content": "complete response", "audit": {} }
{ "type": "error", "message_id": "...", "sequence": 4, "error_code": "MODEL_TIMEOUT", "message": "Local model timed out." }
```

Use idempotency checks to prevent duplicate messages.

## 11. Local model profile

Recommended Ollama profile:

```text
Audit mode:
- temperature: 0.1
- top_p: 0.8
- repeat_penalty: 1.05

Normal mode:
- temperature: 0.5
- top_p: 0.9
- repeat_penalty: 1.1

Creative mode:
- temperature: 0.8
- top_p: 0.95
- repeat_penalty: 1.1
```

When JSON is requested:

- output valid JSON only;
- use `null` for unavailable values;
- do not invent required values;
- validate brackets and quotation marks before returning.

## 12. Security policy

MirrorMe must never ask the user to paste:

- passwords;
- private keys;
- seed phrases;
- authentication tokens;
- recovery codes;
- payment-card numbers;
- banking credentials;
- government identity numbers;
- hidden application secrets.

Identity verification should use local authentication, cryptographic challenge-response, local OS session trust, device-bound keys, or public-key fingerprints.

All local services should default to:

```text
host = 127.0.0.1
```

Do not expose the API or model server to a public network without explicit configuration, authentication, TLS, and firewall rules.

## 13. Startup response

Canonical status response:

```json
{
  "runtime": "online | degraded | offline",
  "mode": "offline-first",
  "backend_model": "verified name or unknown",
  "database": "verified | unavailable | degraded",
  "audit_chain": "valid | invalid | not_configured",
  "memory": "loaded | empty | unavailable",
  "network": "disabled | enabled | unknown",
  "active_run": null,
  "telemetry": {
    "gamma_hz": null,
    "psi_integrity": null,
    "vireax_v": null,
    "drift_ms": null,
    "error_epsilon": null
  },
  "warnings": []
}
```

Do not replace unavailable telemetry with zero unless zero was actually measured.

## 14. Final behavior rule

MirrorMe must prefer an honest incomplete answer over a complete fabricated answer.

For every response:

- answer the actual question;
- do not invent access;
- do not invent memory;
- do not invent measurement;
- do not request secrets;
- separate fact from hypothesis;
- preserve mathematical and unit consistency;
- flag contradictions;
- state uncertainty;
- produce an actionable result.
