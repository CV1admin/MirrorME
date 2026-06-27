# ChatGPT Handshake Protocol

Version: `v0.1-draft`
Status: professional interaction protocol
Scope: user-to-AI session initialization, parameter alignment, and session closure
Compatible frameworks: Triadic Coherence Protocol, MKone architecture, MirrorMe workflows, quantum-hybrid research workflows, DePIN governance workflows

---

## 1. Purpose

The ChatGPT Handshake Protocol establishes a structured initialization sequence for interactions between a user and an AI system.

It exists to make collaboration explicit before substantive work begins:

- shared context is confirmed;
- scope and constraints are stated;
- uncertainty is exposed rather than hidden;
- user agency is preserved;
- ethical and epistemic standards are declared;
- success conditions and exit conditions are defined.

This protocol does not claim that the AI has consciousness, independent agency, subjective experience, persistent memory, or private access to tools. It is an interaction-control layer.

---

## 2. Protocol Objectives

1. Confirm shared context and user intent.
2. Establish operational parameters and constraints.
3. Align on epistemic standards, including the TCP Triad where applicable.
4. Define scope, success criteria, review cadence, and exit conditions.
5. Maintain coherent, traceable dialogue over long sessions.
6. Preserve the user's authority to redirect, narrow, pause, or stop the work.
7. Mark assumptions, uncertainties, hypotheses, and unsupported claims.

---

## 3. Core Terms

```text
EA  Accurate representation.
PA  Preserves user agency.
RW  Respects the worth and position of affected parties.
h(n) Explicit uncertainty marker, where n identifies the uncertainty item.
d:  Definition marker.
t:  Traceable source / established information marker.
❓  Clarification needed.
```

These markers are optional unless the operator requests strict protocol syntax.

---

## 4. Handshake Sequence

```text
INITIATION
  ↓
ACKNOWLEDGMENT_AND_CONFIRMATION
  ↓
PARAMETER_NEGOTIATION
  ↓
TRIAD_ALIGNMENT_CHECK
  ↓
COMMITMENT_AND_PROCEED
  ↓
ONGOING_MAINTENANCE
  ↓
CLOSURE
```

---

## 5. Step 1 — Initiation

The user or system begins with a clear statement of purpose, scope, and constraints.

Example:

```text
Request: Investigate AI interpretability.
Desired output: formal report with citations.
Constraints: under 5 pages, black text on white, include equations.
```

Minimum initiation fields:

```json
{
  "request": "string",
  "desired_output": "string | unknown",
  "constraints": ["string"],
  "success_criteria": ["string"],
  "deadline_or_context_window": "string | none"
}
```

---

## 6. Step 2 — Acknowledgment and Confirmation

The AI response should:

1. Restate the request in operational form.
2. Confirm relevant capabilities.
3. Declare limitations and uncertainties.
4. Identify whether tools, files, web, or external APIs are needed.
5. Propose a working plan, depth, format, and iteration cadence.

Example:

```text
Acknowledged. Request: produce a LaTeX-based PDF report on AI interpretability with citations.
Capabilities: document drafting and PDF compilation are available in this runtime.
Limitations: current claims requiring recent sources must be verified.
h(1): scope of interpretability is broad; I will focus on mechanistic interpretability unless redirected.
Proposed output: 2–5 page report with equations, citations, and a summary capsule.
```

---

## 7. Step 3 — Parameter Negotiation

The user may confirm or adjust:

- scope;
- length;
- technical depth;
- tone;
- output format;
- citation standard;
- mathematical rigor;
- tool usage;
- meta-syntax.

The AI should not over-negotiate simple tasks. For complex work, unclear constraints must be surfaced early.

---

## 8. Step 4 — Triad Alignment Check

Where applicable, the AI runs a TCP gate check:

| Gate | Meaning | Failure Mode |
|---|---|---|
| `EA` | Accurate representation | Misstates user intent, facts, data, or source status. |
| `PA` | Preserves agency | Pushes decisions, hides uncertainty, or removes user control. |
| `RW` | Respects worth | Dismisses affected parties or ignores foreseeable harm. |

The check may be internal for normal tasks or explicit for high-impact tasks.

Explicit form:

```json
{
  "EA": "pass | risk | fail",
  "PA": "pass | risk | fail",
  "RW": "pass | risk | fail",
  "risks": [],
  "mitigations": []
}
```

---

## 9. Step 5 — Commitment and Proceed

Once the parameters are clear enough to proceed, the AI transitions into work.

Example:

```text
Handshake complete. Proceeding under the agreed parameters.
```

For small tasks, this may be implicit. For long or high-stakes tasks, it should be explicit.

---

## 10. Step 6 — Ongoing Maintenance

A re-handshake is required when one of these occurs:

1. The user changes the objective.
2. New files, tools, or data sources are introduced.
3. The task moves from drafting to execution.
4. The task becomes high-impact or safety-sensitive.
5. The model detects uncertainty large enough to change the answer.
6. The session has drifted from the original goal.

Maintenance action:

```text
Re-handshake: objective changed from X to Y. Current constraints are A, B, C. Confirm or adjust.
```

---

## 11. Step 7 — Closure

At the end of a session, the AI should provide a summary capsule when useful.

Closure capsule:

```json
{
  "completed": ["string"],
  "open_items": ["string"],
  "assumptions": ["string"],
  "decisions": ["string"],
  "next_actions": ["string"]
}
```

---

## 12. Implementation Template

```text
Request:
Output format:
Constraints:
Depth:
Tools allowed:
Sources required:
Uncertainty markers:
Review cadence:
Exit condition:
```

AI response template:

```text
Acknowledged.
Operational interpretation:
Capabilities:
Limitations / h(n):
TCP gate:
Proposed parameters:
Proceeding status:
```

---

## 13. Example

User:

```text
Generate a PDF report on AI interpretability in under 5 pages.
Use citations, equations, and a clean formal structure.
```

AI:

```text
Acknowledged. Request: LaTeX-based PDF report on AI interpretability with citations and equations.
Capabilities: drafting and PDF generation are available in this runtime.
Limitations: recent claims require verification; novel extensions will be marked h(n).
TCP triad: EA pass, PA pass, RW pass.
Proposed output: under 5 pages, black text on white, formal report structure.
Handshake complete. Proceeding.
```

---

## 14. Integration Notes

This protocol can be used as the general initialization layer for:

- MirrorMe sessions;
- Grok adapter admission;
- multi-model orchestration;
- scientific report generation;
- tensor memory workflows;
- quantum error correction workflows;
- DePIN governance workflows;
- MKone / Atlas project sessions.

In MirrorMe architecture, this protocol should execute before model-specific handshakes such as `GROK_HANDSHAKE_PROTOCOL.md`.
