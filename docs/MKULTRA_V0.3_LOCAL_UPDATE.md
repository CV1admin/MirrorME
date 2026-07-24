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

## Directory roles

Use separate directories for source code, synchronized repositories, and Ollama's internal model data:

```text
C:\Users\TheSteelWill\MirrorME
    MirrorME Git source checkout

C:\Users\TheSteelWill\CivilisationOne
    local workspace for the other synchronized repositories

C:\Users\TheSteelWill\.ollama
    Ollama-managed model data and blobs
```

Do not clone MirrorME into `.ollama`, and do not manually copy the MKultra Modelfile into `.ollama`. `ollama create` reads the Modelfile from the Git checkout and writes its model data to `.ollama` automatically.

## What “update all repositories” means

The updater synchronizes the repositories listed in:

```text
repositories/mkultra-v0.3-repositories.json
```

The current MirrorME checkout is updated in place. Other repositories are cloned or fast-forwarded under the configured workspace root.

The updater does **not** write version commits into unrelated remote repositories.

Local synchronization policy:

- use the current MirrorME checkout;
- clone other repositories that are absent;
- fetch and fast-forward clean repositories;
- skip repositories containing local uncommitted changes;
- never force-push;
- never reset or delete local work;
- continue processing after an individual repository failure;
- record a JSON update report.

## Prerequisites

Install and configure:

- Git;
- Python 3.11 or later, preferably with the Windows `py` launcher;
- Node.js 22 and npm;
- Ollama;
- Git Credential Manager or credentials capable of reading the required private repositories.

The updater does not request, print, or store GitHub tokens.

Check commands:

```powershell
git --version
py -3 --version
node --version
npm --version
ollama --version
```

The updater tries `python`, then `py -3`, then `python3`. Python tests are skipped with a warning when none is available.

## Update MirrorME after PR merge

The MKultra v0.3 feature branch has been merged. Use `main`:

```powershell
cd "C:\Users\TheSteelWill\MirrorME"

git switch main
git fetch origin
git pull --ff-only origin main
git status
```

Expected status:

```text
On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
```

## Optional Python virtual environment

The repository currently has no root `pyproject.toml`, `setup.py`, or `setup.cfg`, so `pip install -e .` is not a valid setup step.

Tests can run directly from the repository root. An isolated interpreter is still useful:

```powershell
cd "C:\Users\TheSteelWill\MirrorME"

py -3 -m venv .venv
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
```

No editable package installation is required for the current test suite.

## Run the updater

```powershell
cd "C:\Users\TheSteelWill\MirrorME"
Set-ExecutionPolicy -Scope Process Bypass

.\scripts\update-mkultra-v0.3.ps1 `
  -Root "C:\Users\TheSteelWill\CivilisationOne" `
  -ModelName "mkultra:0.3"
```

The script will:

1. use the current MirrorME checkout;
2. synchronize the repositories listed in the manifest;
3. keep MirrorME on `main`;
4. run the repository-level Python test suite;
5. run `npm ci` and `npm run check` when available;
6. pull `qwen3:8b`;
7. create the local Ollama model `mkultra:0.3`;
8. write `MKultra_v0.3-update-report.json` in the workspace root.

## Safe preview

```powershell
.\scripts\update-mkultra-v0.3.ps1 `
  -Root "C:\Users\TheSteelWill\CivilisationOne" `
  -DryRun
```

## Skip expensive phases

Synchronize repositories without tests or model creation:

```powershell
.\scripts\update-mkultra-v0.3.ps1 `
  -Root "C:\Users\TheSteelWill\CivilisationOne" `
  -SkipChecks `
  -SkipModel
```

## Build the model directly

From the MirrorME source checkout:

```powershell
cd "C:\Users\TheSteelWill\MirrorME"

ollama pull qwen3:8b
ollama create mkultra:0.3 -f ".\ollama\Modelfile.mkultra-v0.3"
ollama list
```

Expected model entry:

```text
mkultra:0.3
```

`ollama run mkultra:0.3` only works after `ollama create` succeeds. Before creation, Ollama attempts a registry pull and reports that the manifest does not exist.

## Run MKultra

```powershell
ollama run mkultra:0.3
```

## Start the local bridge

With the virtual environment active:

```powershell
cd "C:\Users\TheSteelWill\MirrorME"
python local_bridge\mirrorme_bridge.py --model "mkultra:0.3"
```

Without an active virtual environment, use the Windows launcher:

```powershell
cd "C:\Users\TheSteelWill\MirrorME"
py -3 local_bridge\mirrorme_bridge.py --model "mkultra:0.3"
```

In a second PowerShell window:

```powershell
cd "C:\Users\TheSteelWill\MirrorME"
npm run dev
```

Open:

```text
http://localhost:3000/#/mirrorme
```

## Validation commands

PowerShell syntax:

```powershell
[void][scriptblock]::Create(
    (Get-Content ".\scripts\update-mkultra-v0.3.ps1" -Raw)
)
```

Python tests:

```powershell
py -3 -m unittest discover -s tests -p "test_*.py" -v
```

When the virtual environment is active:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

Frontend:

```powershell
npm ci
npm run check
```

Ollama:

```powershell
ollama list
ollama show mkultra:0.3
```

## Integrity boundaries

The current identity verifier requires an injected signature verifier. Test callbacks are not production trust roots.

Before production activation, implement:

- audited RFC 8785 canonical JSON;
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

The updater never deletes local branches or resets working trees. To return MirrorME to the current production branch:

```powershell
cd "C:\Users\TheSteelWill\MirrorME"
git switch main
git pull --ff-only origin main
```

Remove the local model only when explicitly intended:

```powershell
ollama rm mkultra:0.3
```
