# Using the Intelligence Pipeline

The pipeline connects three layers:

```text
MirrorME client → local bridge :8765 → Router scientific pipeline
```

## 1. Verify the Router

From the Router repository:

```bash
python tests/test_pipeline_stub.py -v
```

Expected result:

```text
OK
```

(all tests pass; currently 7+ cases including the friendly local payload path)

If the project uses pytest:

```bash
python -m pytest tests/test_pipeline_stub.py -v
```

## 2. Call it directly from Python

Friendly **local** payloads (recommended for Thin Line experiments) are automatically
adapted to the full hard-rule contracts when `local_only: true` or when `type` is used
instead of `request_class`.

```python
from intelligence_router import run_scientific_pipeline

request = {
    "request_id": "thin-line-test-001",
    "type": "scientific",
    "objective": "Evaluate the Thin Line persistence functional",
    "inputs": {
        "equation": "lambda_TL = Q_top**2 * R * log(1 + E_SB/E_P)",
        "parameters": {
            "Q_top": 0.8,
            "R": 0.9,
            "E_SB": 2.0,
            "E_P": 10.0,
        },
    },
    "requested_action": "validate",
}

session = {
    "session_id": "mirrorme-local-001",
    "actor_id": "mk-owner",
    "actor_role": "MK",
    "local_only": True,
}

result = run_scientific_pipeline(
    request=request,
    session=session,
)

print(result.stage)
print(result.data["validation_report"]["results_summary"])
```

A scientific job should finish with:

```text
awaiting_mk_review
```

That is intentional. The pipeline generated a **validation report** but did **not**
approve or publish it (hard rules #3 and #4).

You can also inspect:

```python
print(result.to_dict())
```

## 3. Call it from the MirrorME TypeScript client

```typescript
import { runScientificPipeline } from '@/lib/intelligencePipeline';

const result = runScientificPipeline({
  request: {
    request_id: 'thin-line-test-001',
    type: 'scientific',
    objective: 'Evaluate the Thin Line persistence functional',
    inputs: {
      equation: 'lambda_TL = Q_top**2 * R * log(1 + E_SB/E_P)',
      parameters: {
        Q_top: 0.8,
        R: 0.9,
        E_SB: 2.0,
        E_P: 10.0,
      },
    },
    requested_action: 'validate',
  } as any,
  session: {
    session_id: 'mirrorme-local-001',
    actor_id: 'mk-owner',
    actor_role: 'MK',
    local_only: true,
  } as any,
});

console.log(result.stage);
```

(`runScientificPipeline` is synchronous in the current stub.)

## 4. Call the local bridge

Start the bridge, then PowerShell:

```powershell
$body = @{
    request = @{
        request_id = "thin-line-test-001"
        type = "scientific"
        objective = "Evaluate the Thin Line persistence functional"
        inputs = @{
            equation = "lambda_TL = Q_top**2 * R * log(1 + E_SB/E_P)"
            parameters = @{
                Q_top = 0.8
                R = 0.9
                E_SB = 2.0
                E_P = 10.0
            }
        }
        requested_action = "validate"
    }
    session = @{
        session_id = "mirrorme-local-001"
        actor_id = "mk-owner"
        actor_role = "MK"
        local_only = $true
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:8765/api/intelligence/route" `
    -ContentType "application/json" `
    -Body $body
```

Or with `curl`:

```bash
curl -X POST http://127.0.0.1:8765/api/intelligence/route \
  -H "Content-Type: application/json" \
  -d "{\"request\":{\"request_id\":\"thin-line-test-001\",\"type\":\"scientific\",\"objective\":\"Evaluate the Thin Line persistence functional\",\"requested_action\":\"validate\",\"inputs\":{\"equation\":\"lambda_TL = Q_top**2 * R * log(1 + E_SB/E_P)\",\"parameters\":{\"Q_top\":0.8,\"R\":0.9,\"E_SB\":2.0,\"E_P\":10.0}}},\"session\":{\"session_id\":\"mirrorme-local-001\",\"actor_id\":\"mk-owner\",\"actor_role\":\"MK\",\"local_only\":true}}"
```

## Review and publication states

Expected controlled flow:

```text
submitted
→ routed
→ validation_report_generated
→ awaiting_mk_review
→ approved or rejected
→ approved_for_publication
→ explicitly confirmed (confirm_publish: true)
→ publish_intent_accepted (stub does not publicly release)
```

Publication requires **both**:

1. Marek Kowalski decision `outcome: "approved_for_publication"` (hard rule #4)  
2. Explicit publication request with `confirm_publish: true` (hard rule #5)

Neither alone publishes anything. A validation report is **never** a publication (hard rule #3).

## Current trust limitations

Treat the implementation as an **integration stub**:

* Proof checking measures field presence; it does not perform cryptographic verification.
* Local friendly payloads are adapted to contracts only when `local_only` / friendly shape is detected.
* MKone may evaluate a declared Thin Line functional numerically; that is **not** scientific proof.
* `awaiting_mk_review` is a mandatory stopping point for scientific / MKone reports.
* Approval and publication remain separate decisions.
* No output should be described as scientifically proven merely because the pipeline accepted its structure.

Also see:

* [INTELLIGENCE_PIPELINE_STUB.md](../INTELLIGENCE_PIPELINE_STUB.md)
* Org hard rules: `Civilisation-one/.github/architecture/HARD_RULES_INDEX.md`
