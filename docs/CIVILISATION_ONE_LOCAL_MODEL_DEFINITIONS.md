# Civilisation.One Members and MirrorME Local Model Definitions

Status: operational draft.

This document defines the purpose of the Civilisation.One platform, the role of members, and the local MirrorME model boundary.

---

## 1. Civilisation.One

Civilisation.One is a public-benefit knowledge, education, research, and coordination platform.

Purpose:

- reduce confusion through structured knowledge
- support open scientific education
- organise research and engineering projects
- separate facts, assumptions, hypotheses, and simulations
- support transparent public-benefit collaboration
- acknowledge measured achievement and contribution

Civilisation.One should coordinate, analyse, educate, verify, and document. It should not be presented as a government, bank, religion, or command authority.

---

## 2. Member

A member is a human participant with one primary Civilisation.One account or node.

A member may participate as a learner, builder, researcher, reviewer, educator, sponsor, node operator, or community contributor.

Member roles describe function and responsibility. They do not define human value.

### Member purposes

| Role | Purpose |
|---|---|
| Learner | Study, ask questions, complete pathways, build skills. |
| Builder | Contribute code, tools, designs, simulations, and infrastructure. |
| Researcher | Submit theories, experiments, papers, datasets, and verification tasks. |
| Reviewer | Check claims, find contradictions, improve quality. |
| Educator | Create lessons, explain concepts, mentor others. |
| Sponsor | Support public-benefit work through transparent programs. |
| Node operator | Run local or edge infrastructure under defined privacy rules. |
| Community contributor | Participate in discussion, feedback, and governance processes. |

---

## 3. MirrorME

MirrorME is the member-side AI interface and local reasoning node.

Purpose:

- organise thoughts, tasks, and project work
- connect to local or optional backend AI models
- audit reasoning and contradictions
- support learning and research workflows
- prepare memory candidates under user approval
- keep sensitive work local where possible

MirrorME is an AI-assisted interface. It is not a final authority, legal identity system, or biological verification system.

---

## 4. VIREAX

VIREAX is the orchestration and audit layer.

Purpose:

- route tasks to suitable models
- separate verified facts from assumptions
- detect contradictions
- preserve safety and truth boundaries
- produce audit blocks and next actions
- coordinate local and optional backend model paths

VIREAX should recommend and audit. It should not command the member.

---

## 5. MirrorME local model

The MirrorME local model is an AI model running on the member machine, usually through Ollama.

Default path:

```text
MirrorME UI
  -> http://localhost:8765/api/chat
  -> local_bridge/mirrorme_bridge.py
  -> http://localhost:11434/api/chat
  -> Ollama local model
```

Purpose:

- private drafting
- local reasoning
- code and documentation help
- offline fallback
- local audit reports
- development testing

Local model output is useful but not automatically verified. Important claims still require source checks, tests, or review.

---

## 6. Local bridge

The local bridge is a small local server between the browser UI and Ollama.

Purpose:

- give the UI one stable localhost endpoint
- proxy chat requests to Ollama
- expose health checks
- expose local handshake checks
- keep local operation separate from cloud adapters

Default bridge:

```text
http://localhost:8765
```

Rules:

- keep the bridge on localhost by default
- do not commit secrets to the repo
- do not place backend keys in browser code
- provide clear error messages when Ollama is unavailable

---

## 7. Local handshake

The local handshake confirms a temporary local runtime session.

Endpoints:

```text
GET  /api/handshake/challenge
POST /api/handshake/verify
GET  /api/handshake/status?session_id=...
```

Purpose:

- confirm the bridge is reachable
- issue a short-lived challenge
- verify the returned challenge data
- report a local session state
- gate future higher-risk features such as persistent memory

The handshake is local session confirmation only. It is not a broad identity proof.

---

## 8. Optional OpenAI Platform backend

OpenAI Platform support is optional and should be implemented as a backend or trusted-local adapter.

Purpose:

- use stronger hosted models when local models are insufficient
- support code review, writing, summarisation, and research workflows
- allow VIREAX to compare local and hosted model outputs

Boundary:

```text
MirrorME UI
  -> local/backend adapter
  -> OpenAI Platform
```

Rules:

- keep `OPENAI_API_KEY` server-side or trusted-local only
- do not expose API keys in browser code
- keep local Ollama mode working without cloud access
- log provider, model, role, and audit metadata, but never secrets

---

## 9. Civilisation.One platform modules

| Module | Purpose |
|---|---|
| Member Node | Account, consent, contribution history, learning record. |
| MirrorME Node | Local AI interface and member reasoning assistant. |
| Project Node | Public-benefit project page, milestones, tasks, documents. |
| Research Node | Claim, evidence, theory, simulation, and review workspace. |
| Education Node | Courses, lessons, tests, progression, and certificates. |
| Verification Node | Source checks, contradiction checks, evidence labels. |
| Donation Program Node | Transparent public-benefit support channels. |
| Governance Node | Proposals, voting, moderation, and accountability logs. |
| Country Node | Localised coordination, language support, and regional context. |
| Center Node | Coordination, analytics, auditing, and system health. |

---

## 10. Information states

| State | Definition |
|---|---|
| Draft | Not yet reviewed. |
| Hypothesis | Plausible but requires testing or evidence. |
| Verified | Supported by sources, tests, or accepted process. |
| Simulated | Generated by a software model, not necessarily measured. |
| Local-only | Kept on the member machine unless explicitly exported. |
| Public contribution | User-approved content submitted to a shared layer. |
| Member achievement | Logged learning milestone, review, build task, or contribution. |

---

## 11. Operating principles

```text
Facts over belief.
Measured progress over promises.
Consent over extraction.
Verification over authority.
Coordination over command.
Transparency over hidden control.
Human agency over automation.
```

---

## 12. Current implementation status

```text
MirrorME UI:                active
Local dashboard:            active
Local bridge:               active
Ollama route:               active
Handshake endpoints:        active
OpenAI backend adapter:     optional / pending
Member system:              draft definition
Persistent memory:          pending memory policy gate
Civilisation.One platform:  dashboard prototype
```

---

## 13. Next implementation steps

1. Add provider Settings UI.
2. Add local handshake UI panel.
3. Add member definition cards to the dashboard.
4. Add memory policy gate before persistent storage.
5. Add optional OpenAI backend adapter only after key boundary is confirmed.
6. Add bridge and route tests.
7. Add schema files for member and project nodes.
