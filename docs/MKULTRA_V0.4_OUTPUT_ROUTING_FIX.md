# MKultra v0.4 Output-Routing Correction

## Resolved defects

This correction addresses three independent defects observed in the local PowerShell session:

1. Qwen/Ollama thinking output was exposed to the operator.
2. Read-only epistemic queries were incorrectly routed through the human-approval gate.
3. The displayed arithmetic identity for 144 was invalid.

## Correct runtime behavior

### Read-only requests

Definitions, classifications, comparisons, explanations, calculations, analysis and status inspection are read-only operations. They must be answered directly.

Examples:

```text
E, M
Define empirical evidence and mythology/story.
Compare [H] and [E].
Check this equation.
```

These requests do not require:

- human approval;
- a numbered evolution proposal;
- an `Action Required` banner;
- a change packet.

### Mutating or exporting requests

Human approval remains mandatory for operations that create, modify, delete, export, execute or persist state, including:

- files and source code;
- model weights or policies;
- identity and trust roots;
- durable memory;
- deployments and external systems;
- governed change packets.

Approval to export a proposal still does not authorize automatic execution.

## Thinking-output suppression

The v0.4 Modelfile now includes Qwen's `/no_think` control. The local bridge also forces the Ollama API field:

```json
{
  "think": false
}
```

The bridge copies the incoming payload before applying this setting, so caller-owned input is not mutated. Clients cannot override the v0.4 operator-output boundary with `"think": true`.

For direct CLI use, the explicit command is:

```powershell
ollama run mkultra:0.4 --think=false "E, M"
```

Inside an interactive Ollama session, use:

```text
/set nothink
```

## Arithmetic correction

The valid identity is:

```text
F_12 = 144 = 12^2 = 2^4 * 3^2
```

The rejected identity is:

```text
144 = 24 * 3^2
```

because:

```text
24 * 3^2 = 24 * 9 = 216
```

When the visualization represents a different node count, use separate symbols:

```text
Lambda = 144
N_nodes = 144000
```

The rendered node count must state whether it is complete, aggregated or sampled.

## Apply locally

After this branch is merged:

```powershell
cd "C:\Users\TheSteelWill\MirrorME"
git pull origin main
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\update-mkultra-v0.4.ps1
```

The update script rebuilds `mkultra:0.4` from the corrected Modelfile. Merely restarting an already-created Ollama model does not import Modelfile changes.

Then verify direct CLI behavior:

```powershell
ollama run mkultra:0.4 --think=false "E, M"
```

Expected result:

```text
[E] Empirical evidence: observable, reproducible measurements or records, interpreted within a defined protocol and uncertainty.

[M] Mythology/story: symbolic or narrative material without empirical authority.

Boundary: [M] may motivate a hypothesis, but it cannot be promoted directly to [E] without a defined test and supporting observations.
```
