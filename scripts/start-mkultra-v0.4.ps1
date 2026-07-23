[CmdletBinding()]
param(
  [string]$Model = $(if ($env:MIRRORME_MODEL) { $env:MIRRORME_MODEL } else { "mkultra:0.4" }),
  [int]$BridgePort = $(if ($env:MIRRORME_BRIDGE_PORT) { [int]$env:MIRRORME_BRIDGE_PORT } else { 8765 })
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ($Model -notmatch '^[A-Za-z0-9._:/-]+$') {
  throw "Model contains unsupported characters."
}
if ($BridgePort -lt 1 -or $BridgePort -gt 65535) {
  throw "BridgePort must be between 1 and 65535."
}

$ScriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepositoryRoot = Split-Path -Parent $ScriptDirectory
$BridgePath = Join-Path $RepositoryRoot "local_bridge/mkultra_v04_bridge.py"
$Modelfile = Join-Path $RepositoryRoot "ollama/Modelfile.mkultra-v0.4"

function Test-CommandAvailable {
  param([Parameter(Mandatory = $true)][string]$Name)
  return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Get-PythonLauncher {
  if (Test-CommandAvailable "python") {
    return [pscustomobject]@{ Command = "python"; Prefix = @() }
  }
  if (Test-CommandAvailable "py") {
    return [pscustomobject]@{ Command = "py"; Prefix = @("-3") }
  }
  if (Test-CommandAvailable "python3") {
    return [pscustomobject]@{ Command = "python3"; Prefix = @() }
  }
  throw "Python 3 was not found. Install Python with the Windows py launcher or add python to PATH."
}

if (-not (Test-CommandAvailable "ollama")) {
  throw "Ollama is not installed or not on PATH."
}
if (-not (Test-Path $BridgePath)) {
  throw "MKultra v0.4 bridge not found: $BridgePath"
}
if (-not (Test-Path $Modelfile)) {
  throw "MKultra v0.4 Modelfile not found: $Modelfile"
}

$python = Get-PythonLauncher
$models = (& ollama list | Out-String)
if ($LASTEXITCODE -ne 0) {
  throw "Unable to read the local Ollama model inventory."
}

if ($models -notmatch [regex]::Escape($Model)) {
  if ($Model -eq "mkultra:0.4") {
    Write-Host "[MODEL] Building mkultra:0.4 from the repository Modelfile"
    & ollama pull qwen3:8b
    if ($LASTEXITCODE -ne 0) { throw "Failed to pull qwen3:8b." }
    & ollama create $Model -f $Modelfile
    if ($LASTEXITCODE -ne 0) { throw "Failed to create ${Model}." }
  }
  else {
    Write-Host "[MODEL] Pulling custom model $Model"
    & ollama pull $Model
    if ($LASTEXITCODE -ne 0) { throw "Failed to pull ${Model}." }
  }
}

$arguments = @($python.Prefix) + @(
  $BridgePath,
  "--model", $Model,
  "--port", [string]$BridgePort
)

Write-Host "[BRIDGE] Starting MKultra v0.4 on http://127.0.0.1:$BridgePort using $Model"
& $python.Command @arguments
if ($LASTEXITCODE -ne 0) {
  throw "MKultra v0.4 bridge exited with code ${LASTEXITCODE}."
}
