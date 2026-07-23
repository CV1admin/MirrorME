[CmdletBinding()]
param(
  [string]$ModelName = "mkultra:0.4",
  [switch]$SkipChecks,
  [switch]$SkipModel
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepositoryRoot = Split-Path -Parent $ScriptDirectory
$Modelfile = Join-Path $RepositoryRoot "ollama/Modelfile.mkultra-v0.4"
$ReportPath = Join-Path $RepositoryRoot "mkultra-v0.4-update-report.json"

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
  return $null
}

function Invoke-Checked {
  param(
    [Parameter(Mandatory = $true)][string]$Command,
    [Parameter(Mandatory = $true)][string[]]$Arguments
  )
  Write-Host "[RUN] $Command $($Arguments -join ' ')"
  & $Command @Arguments
  if ($LASTEXITCODE -ne 0) {
    throw "Command failed with exit code ${LASTEXITCODE}: $Command $($Arguments -join ' ')"
  }
}

$report = [ordered]@{
  version = "0.4.0"
  codename = "Governed Thin Line"
  repository_root = $RepositoryRoot
  model_name = $ModelName
  started_at = (Get-Date).ToUniversalTime().ToString("o")
  checks = [ordered]@{}
  model = [ordered]@{}
  automatic_self_modification = $false
  execution_authorized = $false
}

Push-Location $RepositoryRoot
try {
  if (-not $SkipChecks) {
    if (-not (Test-CommandAvailable "npm")) {
      throw "npm is not installed or not on PATH."
    }
    Invoke-Checked -Command "npm" -Arguments @("ci")
    Invoke-Checked -Command "npm" -Arguments @("run", "check")
    $report.checks.frontend = "passed"

    $python = Get-PythonLauncher
    if ($null -eq $python) {
      throw "Python 3 was not found. Install Python with the Windows py launcher or add python to PATH."
    }
    $pythonArgs = @($python.Prefix) + @(
      "-m", "unittest", "discover",
      "-s", "tests",
      "-p", "test_*.py",
      "-v"
    )
    Invoke-Checked -Command $python.Command -Arguments $pythonArgs
    $report.checks.python = "passed"
  }
  else {
    $report.checks.skipped = $true
  }

  if (-not $SkipModel) {
    if (-not (Test-CommandAvailable "ollama")) {
      throw "Ollama is not installed or not on PATH."
    }
    if (-not (Test-Path $Modelfile)) {
      throw "Modelfile not found: $Modelfile"
    }
    Invoke-Checked -Command "ollama" -Arguments @("pull", "qwen3:8b")
    Invoke-Checked -Command "ollama" -Arguments @("create", $ModelName, "-f", $Modelfile)
    $report.model.status = "created"
    $report.model.base = "qwen3:8b"
  }
  else {
    $report.model.status = "skipped"
  }

  $report.completed_at = (Get-Date).ToUniversalTime().ToString("o")
  $report.status = "passed"
}
catch {
  $report.completed_at = (Get-Date).ToUniversalTime().ToString("o")
  $report.status = "failed"
  $report.error = $_.Exception.Message
  throw
}
finally {
  $report | ConvertTo-Json -Depth 8 | Set-Content -Path $ReportPath -Encoding UTF8
  Pop-Location
  Write-Host "[REPORT] $ReportPath"
}
