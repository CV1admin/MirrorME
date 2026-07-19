param(
  [string]$Model = $(if ($env:MIRRORME_MODEL) { $env:MIRRORME_MODEL } else { "mirrorme" }),
  [int]$BridgePort = $(if ($env:MIRRORME_BRIDGE_PORT) { [int]$env:MIRRORME_BRIDGE_PORT } else { 8765 })
)

$ErrorActionPreference = "Stop"
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) { throw "Ollama is not installed or not on PATH." }
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw "Python is not installed or not on PATH." }

$models = ollama list
if ($models -notmatch [regex]::Escape($Model)) {
  ollama pull $Model
}

python local_bridge/mirrorme_bridge.py --model $Model --port $BridgePort
