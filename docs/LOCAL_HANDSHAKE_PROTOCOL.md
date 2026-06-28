# MirrorME Local Handshake Protocol

Protocol version:

```text
MirrorME-Local-Handshake/v0.1
```

Purpose: establish a local MirrorME session boundary before deeper local memory, identity, or trust functions are enabled.

This protocol is deliberately conservative. It confirms a local runtime session and operator declaration. It does **not** prove legal identity, biological identity, consciousness, external account ownership, or cryptographic personhood.

---

## Trust boundary

The protocol verifies only these local facts:

1. The local bridge is reachable.
2. The bridge issued a fresh nonce.
3. The client returned the same nonce.
4. The client supplied the required confirmation phrase.
5. The declared operator name matches the configured local operator string.
6. The bridge and Ollama target are loopback/local addresses.

It does not verify:

- government identity
- biometrics
- private keys
- seed phrases
- passwords
- email account ownership
- consciousness
- quantum state
- biological state
- external device state

---

## Endpoint summary

```text
GET  /api/handshake/challenge
POST /api/handshake/verify
GET  /api/handshake/status?session_id=...
```

Default bridge:

```text
http://localhost:8765
```

---

## Stage 0 — Bridge health

Request:

```bash
curl http://localhost:8765/health
```

Expected fields:

```json
{
  "ok": true,
  "service": "mirrorme-local-bridge",
  "handshake_protocol": "MirrorME-Local-Handshake/v0.1"
}
```

---

## Stage 1 — Challenge

Request:

```bash
curl http://localhost:8765/api/handshake/challenge
```

Example response shape:

```json
{
  "ok": true,
  "protocol": "MirrorME-Local-Handshake/v0.1",
  "state": "CHALLENGE_ISSUED",
  "session_id": "uuid",
  "nonce": "random_nonce",
  "issued_at_unix": 1780000000,
  "expires_at_unix": 1780000300,
  "operator_expected": "Marek K",
  "required_confirmation_phrase": "CONFIRM_LOCAL_MIRRORME"
}
```

The nonce is short-lived and expires after 300 seconds.

---

## Stage 2 — Verify

Request:

```bash
curl -X POST http://localhost:8765/api/handshake/verify \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "PASTE_SESSION_ID",
    "nonce": "PASTE_NONCE",
    "operator": "Marek K",
    "confirmation_phrase": "CONFIRM_LOCAL_MIRRORME",
    "client_capabilities": {
      "ui": "MirrorME",
      "local_storage": true,
      "chat_endpoint": "http://localhost:8765/api/chat"
    }
  }'
```

Expected response shape:

```json
{
  "ok": true,
  "protocol": "MirrorME-Local-Handshake/v0.1",
  "state": "VERIFIED_LOCAL_SESSION",
  "session_id": "uuid",
  "operator": "Marek K",
  "trust_score": 1.0,
  "trust_mode": "local_operator_confirmation_not_cryptographic_authentication",
  "checks": {
    "nonce_valid": true,
    "confirmation_phrase_valid": true,
    "operator_match": true,
    "bridge_loopback": true,
    "ollama_loopback": true
  },
  "warnings": []
}
```

---

## Stage 3 — Status

Request:

```bash
curl "http://localhost:8765/api/handshake/status?session_id=PASTE_SESSION_ID"
```

Expected response shape:

```json
{
  "ok": true,
  "protocol": "MirrorME-Local-Handshake/v0.1",
  "session": {
    "session_id": "uuid",
    "state": "VERIFIED_LOCAL_SESSION",
    "operator": "Marek K",
    "trust_score": 1.0
  }
}
```

The nonce is not returned by the status endpoint after the challenge stage.

---

## Trust score model

Current local score is intentionally simple:

```text
base score:                  0.40
operator name match:          +0.20
bridge bound to loopback:     +0.20
Ollama target is loopback:    +0.20
maximum:                       1.00
```

Interpretation:

```text
1.00  local session confirmed under expected conditions
0.80  local session confirmed, one weak condition
0.60  local session confirmed, multiple weak conditions
<0.60 do not enable memory or identity-sensitive features
```

This score is an operational readiness score, not objective truth probability.

---

## Failure cases

### Missing or expired session

```json
{"ok": false, "error": "handshake_session_not_found_or_expired"}
```

### Nonce mismatch

```json
{"ok": false, "error": "nonce_mismatch"}
```

### Confirmation phrase mismatch

```json
{"ok": false, "error": "confirmation_phrase_mismatch"}
```

### Missing session ID in status request

```json
{"ok": false, "error": "session_id_required"}
```

---

## Operator configuration

Default operator:

```text
Marek K
```

Override at bridge startup:

```bash
python local_bridge/mirrorme_bridge.py --operator "Marek K"
```

---

## Security rules

- Keep the bridge bound to `127.0.0.1` unless explicitly secured.
- Do not request passwords, seed phrases, private keys, recovery codes, or bank details.
- Do not put API keys in browser localStorage.
- Do not treat operator string matching as legal identity verification.
- Do not enable persistent memory until the operator explicitly approves a memory policy.
- Do not expose the bridge to the public internet.

---

## Integration plan

1. Add Settings UI handshake panel.
2. Store only the current `session_id` in browser localStorage.
3. Display state: `NO_SESSION`, `CHALLENGE_ISSUED`, `VERIFIED_LOCAL_SESSION`, or `EXPIRED`.
4. Gate persistent memory behind `VERIFIED_LOCAL_SESSION` and explicit operator approval.
5. Add optional stronger local signing later using a local key store or OS keychain.

---

## Status

```text
Bridge health:        implemented
Challenge endpoint:   implemented
Verify endpoint:      implemented
Status endpoint:      implemented
UI handshake panel:   pending
Memory gate:          pending
Cryptographic proof:  not implemented
```
