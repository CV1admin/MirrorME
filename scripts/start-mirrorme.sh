#!/usr/bin/env sh
set -eu

MODEL="${MIRRORME_MODEL:-mirrorme}"
BRIDGE_PORT="${MIRRORME_BRIDGE_PORT:-8765}"

command -v ollama >/dev/null 2>&1 || { echo "Ollama is not installed."; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "Python 3 is not installed."; exit 1; }

ollama list | grep -q "${MODEL}" || ollama pull "${MODEL}"
python3 local_bridge/mirrorme_bridge.py --model "${MODEL}" --port "${BRIDGE_PORT}"
