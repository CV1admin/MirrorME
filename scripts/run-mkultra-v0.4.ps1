[CmdletBinding()]
param(
  [string]$Model = $(if ($env:MIRRORME_MODEL) { $env:MIRRORME_MODEL } else { "mkultra:0.4" }),
  [int]$BridgePort = $(if ($env:MIRRORME_BRIDGE_PORT) { [int]$env:MIRRORME_BRIDGE_PORT } else { 8765 })
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepositoryRoot = Split-Path -Parent $ScriptDirectory
$BridgeLauncher = Join-Path $ScriptDirectory "start-mkultra-v0.4.ps1"

if (-not (Test-Path $BridgeLauncher)) {
  throw "MKultra v0.4 launcher not found: $BridgeLauncher"
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

Write-Host "[LOCAL] Starting MKultra v0.4 bridge in a separate PowerShell window"
Start-Process `
  -FilePath $shell.Source `
  -WorkingDirectory $RepositoryRoot `
  -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-File", $BridgeLauncher,
    "-Model", $Model,
    "-BridgePort", [string]$BridgePort
  ) | Out-Null

Start-Sleep -Seconds 2
Write-Host "[LOCAL] Starting UI at http://localhost:3000/#/mkultra-v04"
Push-Location $RepositoryRoot
try {
  & npm run dev:mkultra-v04
  if ($LASTEXITCODE -ne 0) {
    throw "MKultra v0.4 UI exited with code ${LASTEXITCODE}."
  }
}
finally {
  Pop-Location
}
