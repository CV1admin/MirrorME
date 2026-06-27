# CVoneWeb — MirrorMe / MKone Engineering Console

A Vite + React application for the Civilisation.One / MirrorMe project.

## What is included

- MirrorMe / MKone dashboard layout
- 3D cognitive field visualizer using React Three Fiber
- Live simulated telemetry stream
- Vireax stability / drift / error charts using Recharts
- Cognitive Flight Recorder chat panel
- Offline chat fallback for static GitHub Pages deployment
- Contradiction Trap / logic audit panel
- Artifact table
- Runtime settings page
- GitHub Pages deployment workflow
- MK-HIGE information-system engine prototype
- Complex matrix validation for MirrorME local model state safety

## Documentation

- `docs/MIRRORME_SYSTEM_INSTRUCTION.md` — canonical MirrorMe compact offline model instruction v1.5-beta.
- `docs/MK_HIGE_INFORMATION_SYSTEM_ENGINE.md` — measurable information-system engine for coherence, entropy potential, resonance, and harmony.
- `docs/MIRRORME_LOCAL_MODEL_UPGRADE.md` — local model complex trace and Hermitian validation guardrails.

## Local development

```bash
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

## HIGE local model validation

Run complex matrix runtime validation:

```bash
npm run test:hige:complex
```

Run the HIGE type-checker:

```bash
npm run typecheck:hige
```

The complex validator checks square shape, finite entries, Hermitian repair, real trace normalization, and suppression of imaginary trace drift before local-model state is used by HIGE/QHEL-style metrics.

## Production build

```bash
npm run build
npm run preview
```

## GitHub Pages deployment

The repository includes:

```text
.github/workflows/deploy-pages.yml
```

The workflow builds the Vite app and publishes the `dist` directory to GitHub Pages on every push to `main`.

Expected public URL after Pages is enabled:

```text
https://cv1admin.github.io/CVoneWeb/
```

In GitHub repository settings, set:

```text
Settings → Pages → Source → GitHub Actions
```

Latest clean deployment restart: 2026-06-19 08:00 America/New_York.
Latest deployment trigger after workflow cache fix: 2026-06-19 08:05 America/New_York.
Latest rerun trigger: 2026-06-19 08:10 America/New_York.

## Runtime note

This public deployment is static. It does not include a backend database, persistent private memory, or verified hardware telemetry. Dashboard telemetry is generated client-side and should be treated as simulated.

If `GEMINI_API_KEY` is not configured at build time, the chat uses the local offline fallback built into `services/geminiService.ts`.

## Safety boundary

- Do not paste secrets into chat.
- Do not treat simulated telemetry as biological or hardware measurement.
- Declared metrics are hypotheses until connected to verified instrumentation.
- Complex matrix validation is a software guardrail, not proof of physical quantum computation.
