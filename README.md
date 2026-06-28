# MirrorME — Civilisation.One Engineering Console

MirrorME is a Vite + React + TypeScript engineering console for the Civilisation.One / MirrorME project.

It provides a local-first interface for simulated telemetry, reasoning workflows, audit panels, and multi-model orchestration experiments through the VIREAX / QVIREAX layer.

---

## What is included

- MirrorME / MKone dashboard layout
- Live simulated telemetry stream
- Vireax stability, drift, and error state handling
- Cognitive Flight Recorder chat panel
- Local/Ollama chat path for private local testing
- Local MirrorME bridge on `http://localhost:8765`
- Static SPA 404 redirect for direct `/mirrorme` page loads
- Gemini browser test path when `VITE_GEMINI_API_KEY` is explicitly configured
- GPT/OpenAI adapter boundary prepared for server-side integration
- Contradiction Trap / logic audit panel
- Civilisation.One dashboard layer
- GitHub Pages deployment workflow

---

## Correct URLs

Local development URL:

```text
http://localhost:3000/#/mirrorme
```

GitHub Pages URL:

```text
https://cv1admin.github.io/MirrorME/#/mirrorme
```

Do not use this direct path as the primary URL:

```text
https://cv1admin.github.io/MirrorME/mirrorme
```

The app uses hash routing. A static `public/404.html` redirect is included so accidental direct `/mirrorme` page loads can be redirected back to the hash route after deployment.

---

## Current architecture

```text
MirrorME UI
  |
  |-- Dashboard telemetry layer
  |-- Cognitive Flight Recorder chat panel
  |-- Contradiction Trap / audit panel
  |-- Civilisation.One dashboard layer
  |
  +-- VIREAX / QVIREAX reasoning layer
        |
        |-- ModelRouter
        |-- AdapterSpec
        |-- StaticAdapter                 # current mock adapter
        |-- future OpenAIAdapter           # GPT backend adapter
        |-- local MirrorME bridge          # localhost:8765
        |-- Local/Ollama adapter           # localhost:11434 through bridge
        |-- audit ledger
        |-- policy gate
```

The current repository already declares GPT as an OpenAI-backed model role inside the VIREAX/QVIREAX path, but the active adapter is still static/mock unless a real backend adapter is added.

Current role map:

```text
GPT      -> architect
Grok     -> critic
Gemini   -> context_analyst
Claude   -> safety_reviewer
DeepSeek -> technical_validator
Llama    -> local_fallback
```

---

## Local development

Install dependencies:

```bash
npm install
```

Run development server:

```bash
npm run dev
```

Open:

```text
http://localhost:3000/#/mirrorme
```

---

## Connect to local MirrorME

The default local connection path is:

```text
MirrorME browser UI
  -> http://localhost:8765/api/chat
  -> local_bridge/mirrorme_bridge.py
  -> http://localhost:11434/api/chat
  -> Ollama local model
```

Start Ollama:

```bash
ollama serve
```

Pull a local model:

```bash
ollama pull llama3.1:8b
```

Start the MirrorME local bridge:

```bash
python local_bridge/mirrorme_bridge.py
```

Check bridge health:

```bash
curl http://localhost:8765/health
```

Start the UI:

```bash
npm run dev
```

Open:

```text
http://localhost:3000/#/mirrorme
```

The chat service now defaults to the local bridge:

```text
provider: ollama
endpoint: http://localhost:8765
model: llama3.1:8b
```

Full guide:

```text
docs/LOCAL_MIRRORME_CONNECT.md
```

---

## Checks and production build

Run type checks:

```bash
npm run typecheck
```

Build production output:

```bash
npm run build
```

Run both:

```bash
npm run check
```

Preview production build:

```bash
npm run preview
```

---

## Environment setup

Copy `.env.example` to `.env.local` for local development:

```bash
cp .env.example .env.local
```

Environment variables:

```text
VITE_GEMINI_API_KEY=
OPENAI_API_KEY=
```

### Security boundary

- `VITE_GEMINI_API_KEY` is browser-visible because Vite exposes variables prefixed with `VITE_`.
- `VITE_GEMINI_API_KEY` is suitable only for local/demo browser testing.
- `OPENAI_API_KEY` is server-only.
- Local MirrorME/Ollama mode does not require a cloud API key.
- Never expose `OPENAI_API_KEY` in Vite client code.
- Never commit `.env`, `.env.local`, API keys, private tokens, or credentials.

---

## GPT / OpenAI integration plan

### Current state

GPT is already registered conceptually in the QVIREAX runner:

```python
AdapterSpec(model="GPT", provider="OpenAI", role="architect")
```

At the moment, the active response path uses `StaticAdapter`, so GPT is not yet making a live OpenAI API call.

Current behavior:

```text
input task -> ModelRouter -> StaticAdapter -> mock AdapterResult
```

Target behavior:

```text
input task -> ModelRouter -> OpenAIAdapter -> OpenAI API -> AdapterResult
```

### Required backend adapter

Create a server/local-only adapter such as:

```text
qviraex/vireax/openai_adapter.py
```

The adapter should:

- read `OPENAI_API_KEY` from the server/local environment
- never expose the key to browser code
- accept an `AdapterEnvelope`
- send the prompt and role metadata to OpenAI
- return a normal `AdapterResult`
- log model, provider, role, and audit metadata
- never log secrets

Recommended adapter shape:

```python
from __future__ import annotations

import os

from openai import OpenAI

from .adapters import AdapterEnvelope, AdapterResult, AdapterSpec


class OpenAIAdapter:
    def __init__(self, spec: AdapterSpec, model_name: str = "gpt-4.1-mini") -> None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")

        self.spec = spec
        self.model_name = model_name
        self.client = OpenAI(api_key=api_key)

    def respond(self, envelope: AdapterEnvelope) -> AdapterResult:
        system_message = (
            "You are the GPT architect model inside the MirrorME/VIREAX reasoning stack. "
            "Separate facts, assumptions, hypotheses, and implementation steps. "
            "Do not fabricate sources or claim unsupported tool access."
        )

        response = self.client.responses.create(
            model=self.model_name,
            input=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": envelope.prompt},
            ],
        )

        output = response.output_text

        return AdapterResult(
            model=self.spec.model,
            provider=self.spec.provider,
            role=envelope.role,
            output=output,
            confidence=0.80,
            metadata={
                "backend_model": self.model_name,
                "session_id": envelope.metadata.get("session_id"),
                "operator": envelope.metadata.get("operator"),
            },
        )
```

Then replace the static GPT adapter registration with the real adapter only in a trusted backend/local runtime.

Example:

```python
from qviraex.vireax.adapters import AdapterSpec, StaticAdapter
from qviraex.vireax.openai_adapter import OpenAIAdapter

router.register(
    OpenAIAdapter(
        AdapterSpec(model="GPT", provider="OpenAI", role="architect")
    )
)

router.register(
    StaticAdapter(AdapterSpec(model="Claude", provider="Anthropic", role="safety_reviewer"))
)
router.register(
    StaticAdapter(AdapterSpec(model="Llama", provider="Meta", role="local_fallback"))
)
```

---

## Local/Ollama path

For private local testing, keep the local model route separate from cloud GPT.

Recommended routing:

```text
GPT/OpenAI      -> backend only, API key required
Llama/Ollama    -> local fallback, no cloud dependency
Gemini browser  -> demo/local browser path only
StaticAdapter   -> tests, smoke checks, offline mock runs
```

This separation prevents accidental secret exposure and keeps MirrorME operational when cloud models are unavailable.

---

## Running QVIREAX demo

If the Python package path is configured, run:

```bash
python -m qviraex
```

Expected current behavior:

```text
QVIREAX online
MRQL ritual: demo v0.1
VIREAX state: FINAL_OUTPUT
Next action: COMMIT_AUDIT
Audit hash: sha256:...
```

Because the current adapter is static, this validates routing and audit flow, not live GPT reasoning.

---

## GitHub Pages deployment

The repository includes:

```text
.github/workflows/deploy-pages.yml
```

The workflow builds the Vite app and publishes the `dist` directory to GitHub Pages on every push to `main`.

Expected public URL after Pages is enabled:

```text
https://cv1admin.github.io/MirrorME/#/mirrorme
```

In GitHub repository settings, set:

```text
Settings -> Pages -> Source -> GitHub Actions
```

---

## Runtime note

This public deployment is static. It does not include a backend database, persistent private memory, or verified hardware telemetry.

Dashboard telemetry is generated client-side and must be treated as simulated unless connected to verified instrumentation.

---

## Safety boundary

- Do not paste secrets into chat.
- Do not commit `.env`, `.env.local`, `node_modules`, `.next`, `dist`, or `build`.
- Do not treat simulated telemetry as biological or hardware measurement.
- Do not treat static adapter output as a real model response.
- Declared metrics are hypotheses until connected to verified instrumentation.
- GPT/OpenAI access must run through a backend or trusted local runtime only.
- Local MirrorME bridge must stay bound to localhost unless explicitly secured.

---

## Project status

```text
MirrorME UI:              active
VIREAX router:            active
Static model adapters:    active
GPT role declaration:     active
Live GPT/OpenAI adapter:  pending
Local MirrorME bridge:    active
Local/Ollama route:       active through localhost:8765
Static 404 redirect:      active after deployment
Persistent memory:        not included in static public deployment
Verified telemetry:       not included in static public deployment
```
