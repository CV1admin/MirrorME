# Codex CLI with Ollama / gpt-oss:120b

This guide fixes the common Windows error:

```text
Error: failed to configure codex: invalid Codex config TOML: toml: invalid character at start of key: `
```

## Cause

The Codex config file is TOML. It must contain only TOML syntax.

Do not paste Markdown fences, shell prompts, or Windows command output into the config file.

Invalid examples inside `config.toml`:

```text
```
model = "gpt-oss:120b"
```

C:\Users\TheSteelWill>ollama launch codex
Error: failed to configure codex...
```

The backtick character at the start of the file is the usual cause of:

```text
toml: invalid character at start of key: `
```

---

## Correct Windows config path

Codex user config on Windows should be edited at:

```text
C:\Users\TheSteelWill\.codex\config.toml
```

Create the folder if it does not exist:

```powershell
mkdir "$env:USERPROFILE\.codex" -Force
notepad "$env:USERPROFILE\.codex\config.toml"
```

---

## Minimal Ollama config

Paste only this TOML into `config.toml`:

```toml
model = "gpt-oss:120b"
model_provider = "ollama_launch"

[model_providers.ollama_launch]
name = "Ollama"
base_url = "http://localhost:11434/v1"
wire_api = "responses"
```

Notes:

- Use `_` in provider id: `ollama_launch`.
- Do not include Markdown backticks in the actual config file.
- Do not include `C:\Users\...>` prompt text.
- Do not include error output.
- Keep `base_url` without a trailing slash unless Codex requires otherwise.

---

## Optional model catalog

Only add this if the file exists:

```toml
model_catalog_json = "C:/Users/TheSteelWill/.codex/model.json"
```

Prefer forward slashes in TOML paths on Windows.

Do not use this macOS path on Windows:

```toml
model_catalog_json = "/Users/you/.codex/model.json"
```

---

## Pull and run the model

In a separate terminal:

```powershell
ollama pull gpt-oss:120b
ollama serve
```

Check Ollama:

```powershell
curl http://localhost:11434/api/tags
```

Then start Codex:

```powershell
codex
```

If Codex supports OSS shortcut selection in the installed version, this may also work:

```powershell
codex --oss
```

---

## Important correction

This is not a valid command:

```powershell
ollama launch codex
```

Use:

```powershell
codex
```

with Ollama running separately.

---

## MirrorME repo workflow

```powershell
cd "C:\Users\TheSteelWill\CVone\CVone\CVone"
git pull
codex
```

Suggested Codex prompt:

```text
Audit this repo. Fix local dashboard startup, MirrorME bridge, and local handshake UI. Preserve localhost-only safety boundaries. Do not expose API keys. Do not modify persistent memory without an explicit memory policy gate.
```

---

## Safety boundary

- Keep Ollama on localhost.
- Do not paste API keys into Codex prompts.
- Do not store API keys in repo files.
- Do not expose the local MirrorME bridge to the public internet.
- Treat local model output as unverified unless backed by source files, commands, or tests.
