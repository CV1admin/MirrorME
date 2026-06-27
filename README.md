# MirrorME — Civilisation.One Engineering Console

A Vite + React + TypeScript application for the Civilisation.One / MirrorME project.

## What is included

- MirrorME / MKone dashboard layout
- Live simulated telemetry stream
- Vireax stability, drift, and error state handling
- Cognitive Flight Recorder chat panel
- Local/Ollama chat path for private local testing
- Gemini browser test path when `VITE_GEMINI_API_KEY` is explicitly configured
- Contradiction Trap / logic audit panel
- Civilisation.One dashboard layer
- GitHub Pages deployment workflow

## Local development

```bash
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

## Checks and production build

```bash
npm run typecheck
npm run build
```

Or run both:

```bash
npm run check
```

Preview the production build:

```bash
npm run preview
```

## Environment

Copy `.env.example` to `.env.local` for local development.

```bash
cp .env.example .env.local
```

Use:

```text
VITE_GEMINI_API_KEY=
OPENAI_API_KEY=
```

Security boundary:

- `VITE_GEMINI_API_KEY` is browser-visible and only suitable for local/demo browser testing.
- `OPENAI_API_KEY` is server-only. Do not expose it in Vite client code.
- `.env.local` is ignored by Git.

## GitHub Pages deployment

The repository includes:

```text
.github/workflows/deploy-pages.yml
```

The workflow builds the Vite app and publishes the `dist` directory to GitHub Pages on every push to `main`.

Expected public URL after Pages is enabled:

```text
https://cv1admin.github.io/MirrorME/
```

In GitHub repository settings, set:

```text
Settings → Pages → Source → GitHub Actions
```

## Runtime note

This public deployment is static. It does not include a backend database, persistent private memory, or verified hardware telemetry. Dashboard telemetry is generated client-side and should be treated as simulated.

## Safety boundary

- Do not paste secrets into chat.
- Do not commit `.env`, `.env.local`, `node_modules`, `.next`, `dist`, or `build`.
- Do not treat simulated telemetry as biological or hardware measurement.
- Declared metrics are hypotheses until connected to verified instrumentation.
