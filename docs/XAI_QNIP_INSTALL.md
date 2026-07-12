# Install xAI/Grok for MirrorME QNIP

This guide enables the live xAI/Grok critic adapter in the MirrorME / QVIREAX reasoning pipeline.

It does **not** install physical quantum-network hardware. Grok is an advisory reasoning component above the QNIP control layer. It cannot generate entanglement, verify hardware telemetry, authorize controllers, or send pulse-level commands.

---

## Architecture

```text
QNIP service intent or architecture question
    |
    v
VIREAX / QVIREAX ModelRouter
    |
    +-- Grok / xAI critic adapter
    |       |
    |       +-- POST https://api.x.ai/v1/responses
    |
    +-- deterministic policy, verification, and audit layers
```

The xAI output is treated as a model response. It is not trusted quantum evidence.

---

## Requirements

- Python 3.10 or newer
- network access to `https://api.x.ai`
- an xAI API key with available credits
- the MirrorME repository

No additional Python package is required. The adapter uses the Python standard library.

---

## 1. Obtain an xAI API key

Create the key in the xAI API Console.

Do not paste the key into chat, commit it to Git, place it in browser code, or use a `VITE_` prefix.

---

## 2. Configure PowerShell

For the current PowerShell session:

```powershell
$env:XAI_API_KEY = "PASTE_YOUR_XAI_KEY_LOCALLY"
$env:XAI_MODEL = "grok-4.5"
$env:XAI_BASE_URL = "https://api.x.ai/v1"
```

To persist the variables for the Windows user account:

```powershell
[Environment]::SetEnvironmentVariable(
  "XAI_API_KEY",
  "PASTE_YOUR_XAI_KEY_LOCALLY",
  "User"
)

[Environment]::SetEnvironmentVariable("XAI_MODEL", "grok-4.5", "User")
[Environment]::SetEnvironmentVariable("XAI_BASE_URL", "https://api.x.ai/v1", "User")
```

Open a new terminal after setting persistent variables.

---

## 3. Verify configuration

Do not print the key. Check only whether it exists:

```powershell
if ($env:XAI_API_KEY) {
  Write-Host "XAI_API_KEY is configured"
} else {
  Write-Host "XAI_API_KEY is missing"
}
```

---

## 4. Run tests

From the MirrorME repository root:

```powershell
python -m unittest discover -s qviraex/vireax/tests -p "test_*.py" -v
```

The xAI adapter tests use a fake HTTP response and do not spend API credits.

---

## 5. Run QVIREAX with Grok

```powershell
python -m qviraex
```

Expected mode line when the key is configured:

```text
xAI Grok adapter: LIVE_XAI_API
```

When `XAI_API_KEY` is absent, QVIREAX uses:

```text
xAI Grok adapter: STATIC_SIMULATION
```

The mode is explicit so a static response cannot be mistaken for a live xAI response.

---

## 6. Direct adapter example

```python
from qviraex.vireax.adapters import AdapterEnvelope, AdapterSpec, XAIAdapter

spec = AdapterSpec(
    model="Grok",
    provider="xAI",
    role="critic",
    capabilities=("technical_critique", "contradiction_detection", "qnip_review"),
)

adapter = XAIAdapter(spec)
result = adapter.respond(
    AdapterEnvelope(
        target_model="Grok",
        role="critic",
        prompt="Review the QNIP routing and fidelity assumptions.",
        metadata={"session_id": "QNIP-LOCAL-001"},
    )
)

print(result.output)
print(result.metadata["adapter_mode"])
```

---

## API behavior

The adapter sends:

```text
POST https://api.x.ai/v1/responses
Authorization: Bearer <XAI_API_KEY>
Content-Type: application/json
```

Request properties:

```json
{
  "model": "grok-4.5",
  "input": [
    {
      "role": "system",
      "content": "MirrorME/QNIP critic boundary..."
    },
    {
      "role": "user",
      "content": "The task text"
    }
  ],
  "store": false
}
```

`store` is explicitly set to `false` by the adapter.

The adapter records response identifiers and token usage but never includes the API key in result metadata.

---

## QNIP authority boundary

Grok MAY:

- critique a proposed topology
- identify contradictions
- challenge fidelity assumptions
- suggest tests and failure injection
- review an audit summary
- compare simulated and hardware-reported claims

Grok MUST NOT:

- directly authorize a QNIP session
- control a quantum node or regional controller
- generate or retrieve QKD keys
- label simulated telemetry as physical telemetry
- move a Bell pair to `VERIFIED`
- bypass deterministic policy gates
- claim physical entanglement without evidence

All operational decisions remain with authenticated controllers, deterministic policy, evidence validation, and explicit human authorization.

---

## Troubleshooting

### `XAI_API_KEY is required`

The environment variable is missing from the current terminal. Set it locally and reopen PowerShell when using a persistent user variable.

### `xAI API HTTP 401`

The key is invalid, revoked, incorrectly copied, or not authorized.

### `xAI API HTTP 429`

The account has reached a rate or credit limit. Retry only after checking the account limits.

### `xAI API unreachable`

Check DNS, firewall, proxy, and access to `api.x.ai`.

### Static mode appears unexpectedly

Confirm the key exists in the same terminal process that runs:

```powershell
python -m qviraex
```

---

## Security rules

- Keep `XAI_API_KEY` server-side.
- Never add `XAI_API_KEY` to GitHub Pages, Vite browser variables, or client-side JavaScript.
- Never commit `.env`, `.env.local`, terminal history exports, or secret-bearing logs.
- Use separate keys for development and production.
- Apply account-side spending and rate limits.
- Do not send raw QKD keys, private keys, seed phrases, passwords, or unrestricted detector data to an external model.
- Redact personal or operationally sensitive data before model submission.

---

## Official API references

- xAI documentation: `https://docs.x.ai/`
- xAI API console: `https://console.x.ai/`
- Responses endpoint: `https://api.x.ai/v1/responses`
