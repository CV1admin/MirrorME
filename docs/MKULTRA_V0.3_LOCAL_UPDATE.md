# MKultra v0.3 — Local Update Guide

## Status

`MKultra v0.3`, codename **Persistent Mirror**, is an integration-development release.

It combines:

- verified Identity Capsule context;
- bounded Consciousness Observer Mode;
- short-memory Cognitive Continuum;
- non-evidential inspiration sparks;
- parallel Imagination Mode candidate comparison;
- controlled Dream Mode evaluation;
- DGREP review gating;
- local-first Ollama model construction.

It does not claim sentience and does not enable automatic persistence, external actions, policy mutation, or weight updates.

## What “update all repositories” means

The updater synchronizes the 37 repositories currently exposed to the `CV1admin` GitHub App installation into a local workspace.

It does **not** write a version marker into every remote repository. That would create unrelated commits without changing their functionality.

Local synchronization policy:

- clone repositories that are absent;
- fetch and fast-forward clean repositories;
- skip repositories containing local uncommitted changes;
- never force-push;
- never reset or delete local work;
- continue processing after an individual repository failure;
- record a JSON update report.

Repository inventory:

```text
repositories/mkultra-v0.3-repositories.json
```

## Prerequisites

Install and configure:

- Git;
- Python 3.11 or later;
- Node.js and npm for the MirrorME UI checks;
- Ollama;
- Git Credential Manager or SSH/HTTPS credentials capable of reading private `CV1admin` repositories.

The updater does not request, print, or store GitHub tokens.

## Windows installation

Clone the integration branch if MirrorME is not present:

```powershell
git clone --branch feature/mkultra-v0.3-full-stack `
  https://github.com/CV1admin/MirrorME.git `
  "C:\Users\TheSteelWill\MirrorME"
```

Run the updater:

```powershell
cd "C:\Users\TheSteelWill\MirrorME"
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\update-mkultra-v0.3.ps1 `
  -Root "C:\Users\TheSteelWill\CivilisationOne" `
  -ModelName "mkultra:0.3"
```

The script will:

1. read the repository manifest;
2. synchronize all listed local clones;
3. check out `feature/mkultra-v0.3-full-stack` for MirrorME;
4. run Python tests;
5. run `npm ci` and `npm run check` when available;
6. pull `qwen3:8b`;
7. create the Ollama model `mkultra:0.3`;
8. write `MKultra_v0.3-update-report.json` in the workspace root.

## Safe preview

Inspect operations without modifying the local filesystem:

```powershell
.\scripts\update-mkultra-v0.3.ps1 `
  -Root "C:\Users\TheSteelWill\CivilisationOne" `
  -DryRun
```

## Skip expensive phases

Repository synchronization only:

```powershell
.\scripts\update-mkultra-v0.3.ps1 `
  -Root "C:\Users\TheSteelWill\CivilisationOne" `
  -SkipChecks `
  -SkipModel
```

Build the model later:

```powershell
ollama pull qwen3:8b
ollama create mkultra:0.3 `
  -f "C:\Users\TheSteelWill\CivilisationOne\MirrorME\ollama\Modelfile.mkultra-v0.3"
```

## Run

```powershell
ollama run mkultra:0.3
```

For the MirrorME local bridge:

```powershell
cd "C:\Users\TheSteelWill\CivilisationOne\MirrorME"
python local_bridge\mirrorme_bridge.py --model "mkultra:0.3"
```

Then start the UI:

```powershell
npm run dev
```

Open:

```text
http://localhost:3000/#/mirrorme
```

## Validation commands

Python:

```powershell
python -m unittest discover -s qviraex -p "test_*.py"
```

Frontend:

```powershell
npm ci
npm run check
```

Ollama model inventory:

```powershell
ollama list
```

Expected model entry:

```text
mkultra:0.3
```

## Integrity boundaries

The current identity verifier requires an injected signature verifier. Test callbacks are not production trust roots.

Before production activation, implement:

- RFC 8785 canonical JSON;
- Ed25519 signature verification;
- encrypted key storage;
- signed append-only identity continuum;
- consent revocation;
- replay protection;
- concurrency control across authorized replicas;
- durable encrypted persistence;
- provider-backed parallel context execution;
- independent security review.

## Rollback

The updater never deletes local branches or resets working trees. To return MirrorME to `main`:

```powershell
cd "C:\Users\TheSteelWill\CivilisationOne\MirrorME"
git checkout main
git pull --ff-only origin main
```

Remove the local model only when explicitly intended:

```powershell
ollama rm mkultra:0.3
```
