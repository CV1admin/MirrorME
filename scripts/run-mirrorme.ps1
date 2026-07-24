[CmdletBinding()]
param(
  [string]$Model = $(if ($env:MIRRORME_MODEL) { $env:MIRRORME_MODEL } else { "mkultra:0.3" }),
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
$BridgeScript = Join-Path $ScriptDirectory "start-mirrorme.ps1"

if (-not (Test-Path $BridgeScript)) {
  throw "Bridge launcher not found: $BridgeScript"
}
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
  throw "npm is not installed or not on PATH."
}

$shell = Get-Command pwsh -ErrorAction SilentlyContinue
if ($null -eq $shell) {
  $shell = Get-Command powershell -ErrorAction SilentlyContinue
}
if ($null -eq $shell) {
  throw "PowerShell executable was not found."
}

Write-Host "[LOCAL] Starting bridge in a separate PowerShell window"
Start-Process `
  -FilePath $shell.Source `
  -WorkingDirectory $RepositoryRoot `
  -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-File", $BridgeScript,
    "-Model", $Model,
    "-BridgePort", [string]$BridgePort
  ) | Out-Null

Start-Sleep -Seconds 2
Write-Host "[LOCAL] Starting UI at http://localhost:3000/#/mirrorme"
Push-Location $RepositoryRoot
try {
  & npm run dev:mirrorme
  if ($LASTEXITCODE -ne 0) {
    throw "MirrorME UI exited with code ${LASTEXITCODE}."
  }
}
finally {
  Pop-Location
}
