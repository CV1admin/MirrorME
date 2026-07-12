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
- xAI/Grok server-side critic adapter for QNIP review
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
        |-- StaticAdapter                 # simulation/fallback adapter
        |-- XAIAdapter                    # live server-side Grok critic
        |-- future OpenAIAdapter           # GPT backend adapter
        |-- local MirrorME bridge          # localhost:8765
        |-- Local/Ollama adapter           # localhost:11434 through bridge
        |-- audit ledger
        |-- policy gate
```

The current repository declares GPT as an OpenAI-backed model role inside the VIREAX/QVIREAX path, but the active GPT adapter is still static/mock unless a real backend adapter is added. Grok can use the live xAI Responses API when `XAI_API_KEY` is configured server-side.

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

## xAI / Grok QNIP integration

The live Grok adapter is server-side Python code. It must not be placed in the Vite browser bundle.

PowerShell configuration for the current terminal:

```powershell
$env:XAI_API_KEY = "PASTE_YOUR_KEY_LOCALLY"
$env:XAI_MODEL = "grok-4.5"
python -m qviraex
```

Expected mode:

```text
xAI Grok adapter: LIVE_XAI_API
```

Without `XAI_API_KEY`, Grok remains explicitly marked as:

```text
xAI Grok adapter: STATIC_SIMULATION
```

Installation and security guide:

```text
docs/XAI_QNIP_INSTALL.md
```

Quantum-network integration specification:

```text
docs/QUANTUM_NETWORK_INTEGRATION_PROTOCOL.md
```

Grok acts only as an advisory critic. It cannot authorize QNIP sessions, control quantum hardware, verify Bell pairs, or turn simulated telemetry into physical evidence.

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

Run Python tests:

```bash
python -m unittest discover -s qviraex/vireax/tests -p "test_*.py" -v
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
XAI_API_KEY=
XAI_MODEL=grok-4.5
XAI_BASE_URL=https://api.x.ai/v1
```

### Security boundary

- `VITE_GEMINI_API_KEY` is browser-visible because Vite exposes variables prefixed with `VITE_`.
- `VITE_GEMINI_API_KEY` is suitable only for local/demo browser testing.
- `OPENAI_API_KEY` is server-only.
- `XAI_API_KEY` is server-only and must never use a `VITE_` prefix.
- Local MirrorME/Ollama mode does not require a cloud API key.
- Never expose server API keys in Vite client code.
- Never commit `.env`, `.env.local`, API keys, private tokens, or credentials.

---

## GPT / OpenAI integration plan

### Current state

GPT is already registered conceptually in the QVIREAX runner:

```python
AdapterSpec(model="GPT", provider="OpenAI", role="architect")
```

At the moment, the active GPT response path uses `StaticAdapter`, so GPT is not yet making a live OpenAI API call.

Current behavior:

```text
GPT role declaration
    -> ModelRouter
    -> StaticAdapter
    -> deterministic mock response
```
