# Connect MirrorME to a Local Model

This guide connects the MirrorME browser UI to a local MirrorME/Ollama runtime.

The safe local path is:

```text
MirrorME browser UI
  -> http://localhost:8765/api/chat
  -> local_bridge/mirrorme_bridge.py
  -> http://localhost:11434/api/chat
  -> Ollama local model
```

This keeps the model on the operator's machine. No OpenAI, Gemini, Claude, or other cloud API is used by the local bridge.

---

## 1. Install Ollama

Install Ollama from the official Ollama installer for your operating system.

Then pull a model:

```bash
ollama pull llama3.1:8b
```

Optional smaller model:

```bash
ollama pull llama3.2:3b
```

---

## 2. Start Ollama

In one terminal:

```bash
ollama serve
```

Ollama should listen on:

```text
http://localhost:11434
```

Test it:

```bash
curl http://localhost:11434/api/tags
```

---

## 3. Start the MirrorME local bridge

In the repository root:

```bash
python local_bridge/mirrorme_bridge.py
```

Default bridge address:

```text
http://localhost:8765
```

Health check:

```bash
curl http://localhost:8765/health
```

Expected response:

```json
{"ok":true,"service":"mirrorme-local-bridge"}
```

Run with a different model:

```bash
python local_bridge/mirrorme_bridge.py --model llama3.2:3b
```

Run with a different Ollama URL:

```bash
python local_bridge/mirrorme_bridge.py --ollama-url http://127.0.0.1:11434
```

---

## 4. Start MirrorME UI

In another terminal:

```bash
npm install
npm run dev
```

Open:

```text
http://localhost:3000/#/mirrorme
```

---

## 5. Configure the browser UI for local mode

Open browser DevTools Console and run:

```js
localStorage.setItem('mirrorme_model_config', JSON.stringify({
  provider: 'ollama',
  ollamaEndpoint: 'http://localhost:8765',
  ollamaModel: 'llama3.1:8b'
}));
location.reload();
```

The chat panel will now send messages to the local bridge.

---

## 6. Direct test without the UI

```bash
curl -N http://localhost:8765/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model":"llama3.1:8b",
    "stream":true,
    "messages":[
      {"role":"system","content":"You are MirrorME local runtime. Answer clearly."},
      {"role":"user","content":"MirrorME local connection test."}
    ]
  }'
```

Expected behavior: streamed newline-delimited JSON from Ollama.

---

## 7. Security boundary

- The bridge binds to `127.0.0.1` by default.
- Do not expose this bridge to the public internet.
- Do not put API keys into the browser.
- Do not log private prompts if the machine is shared.
- Treat all telemetry in the static UI as simulated unless connected to verified instrumentation.
- This bridge is local software plumbing, not identity verification and not consciousness evidence.

---

## Troubleshooting

### `ollama_unreachable`

Start Ollama:

```bash
ollama serve
```

Check installed models:

```bash
ollama list
```

Pull the configured model:

```bash
ollama pull llama3.1:8b
```

### Browser still uses Gemini

Reset the local config:

```js
localStorage.setItem('mirrorme_model_config', JSON.stringify({
  provider: 'ollama',
  ollamaEndpoint: 'http://localhost:8765',
  ollamaModel: 'llama3.1:8b'
}));
location.reload();
```

### CORS error

Use the bridge endpoint:

```text
http://localhost:8765
```

Do not point the browser directly at Ollama unless your local Ollama CORS settings allow it.

---

## Status

```text
Local bridge:       added
Ollama proxy:       added
Browser config:     localStorage-based
Cloud dependency:   none for local route
Persistent memory:  not added here
Identity handshake: not added here
```
