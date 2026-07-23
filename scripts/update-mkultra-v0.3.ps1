[CmdletBinding()]
param(
    [string]$Root = (Join-Path $HOME "CivilisationOne"),
    [string]$ModelName = "mkultra:0.3",
    [switch]$SkipModel,
    [switch]$SkipChecks,
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)][string]$Command,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [string]$WorkingDirectory = ""
    )

    $display = "$Command $($Arguments -join ' ')"
    if ($DryRun) {
        Write-Host "[DRY RUN] $display"
        return
    }

    if ($WorkingDirectory) {
        Push-Location $WorkingDirectory
    }
    try {
        & $Command @Arguments
        if ($LASTEXITCODE -ne 0) {
            throw "Command failed with exit code $LASTEXITCODE: $display"
        }
    }
    finally {
        if ($WorkingDirectory) {
            Pop-Location
        }
    }
}

function Test-CommandAvailable {
    param([Parameter(Mandatory = $true)][string]$Name)
    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

if (-not (Test-CommandAvailable "git")) {
    throw "git is required but was not found on PATH"
}

$ScriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepositoryRoot = Split-Path -Parent $ScriptDirectory
$ManifestPath = Join-Path $RepositoryRoot "repositories/mkultra-v0.3-repositories.json"

if (-not (Test-Path $ManifestPath)) {
    throw "Repository manifest not found: $ManifestPath"
}

$manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json
if ($manifest.release -ne "MKultra_v0.3") {
    throw "Unexpected repository manifest release: $($manifest.release)"
}

if (-not (Test-Path $Root) -and -not $DryRun) {
    New-Item -ItemType Directory -Path $Root -Force | Out-Null
}

$results = [System.Collections.Generic.List[object]]::new()

foreach ($repository in $manifest.repositories) {
    $fullName = [string]$repository.full_name
    $parts = $fullName.Split("/", 2)
    if ($parts.Count -ne 2) {
        throw "Invalid repository name in manifest: $fullName"
    }

    $repoName = $parts[1]
    $target = Join-Path $Root $repoName
    $cloneUrl = "https://github.com/$fullName.git"
    $ref = if ($null -ne $repository.PSObject.Properties["ref"] -and $repository.ref) {
        [string]$repository.ref
    }
    else {
        [string]$repository.default_branch
    }

    $record = [ordered]@{
        repository = $fullName
        target = $target
        ref = $ref
        status = "pending"
        message = ""
    }

    try {
        if (-not (Test-Path (Join-Path $target ".git"))) {
            Write-Host "[CLONE] $fullName -> $target"
            Invoke-Checked -Command "git" -Arguments @("clone", "--filter=blob:none", $cloneUrl, $target)
        }
        else {
            $dirty = (& git -C $target status --porcelain)
            if ($LASTEXITCODE -ne 0) {
                throw "Unable to inspect repository status"
            }
            if ($dirty) {
                $record.status = "skipped-dirty"
                $record.message = "Local changes detected; repository was not modified"
                Write-Warning "[SKIP] $fullName has local changes"
                $results.Add([pscustomobject]$record)
                continue
            }
        }

        Write-Host "[FETCH] $fullName"
        Invoke-Checked -Command "git" -Arguments @("-C", $target, "fetch", "origin", "--prune")

        $localRefExists = $false
        if (-not $DryRun) {
            & git -C $target show-ref --verify --quiet "refs/heads/$ref"
            $localRefExists = ($LASTEXITCODE -eq 0)
        }

        if ($localRefExists) {
            Invoke-Checked -Command "git" -Arguments @("-C", $target, "checkout", $ref)
        }
        else {
            Invoke-Checked -Command "git" -Arguments @("-C", $target, "checkout", "-B", $ref, "origin/$ref")
        }

        Invoke-Checked -Command "git" -Arguments @("-C", $target, "merge", "--ff-only", "origin/$ref")
        $record.status = "updated"
        $record.message = "Fast-forwarded to origin/$ref"
    }
    catch {
        $record.status = "failed"
        $record.message = $_.Exception.Message
        Write-Warning "[FAILED] $fullName: $($_.Exception.Message)"
    }

    $results.Add([pscustomobject]$record)
}

$mirrorPath = Join-Path $Root "MirrorME"

if (-not $SkipChecks) {
    if (-not (Test-Path $mirrorPath) -and -not $DryRun) {
        throw "MirrorME checkout was not created: $mirrorPath"
    }

    Write-Host "[CHECK] Python unit tests"
    if (Test-CommandAvailable "python") {
        Invoke-Checked -Command "python" -Arguments @(
            "-m", "unittest", "discover", "-s", "qviraex", "-p", "test_*.py"
        ) -WorkingDirectory $mirrorPath
    }
    else {
        Write-Warning "python was not found; Python tests skipped"
    }

    if ((Test-CommandAvailable "npm") -and (Test-Path (Join-Path $mirrorPath "package-lock.json"))) {
        Write-Host "[CHECK] Node dependencies and project checks"
        Invoke-Checked -Command "npm" -Arguments @("ci") -WorkingDirectory $mirrorPath
        Invoke-Checked -Command "npm" -Arguments @("run", "check") -WorkingDirectory $mirrorPath
    }
    else {
        Write-Warning "npm or package-lock.json unavailable; Node checks skipped"
    }
}

if (-not $SkipModel) {
    if (-not (Test-CommandAvailable "ollama")) {
        throw "ollama is required to build $ModelName but was not found on PATH"
    }

    $modelfile = Join-Path $mirrorPath "ollama/Modelfile.mkultra-v0.3"
    if (-not (Test-Path $modelfile) -and -not $DryRun) {
        throw "MKultra v0.3 Modelfile not found: $modelfile"
    }

    Write-Host "[MODEL] Pulling qwen3:8b"
    Invoke-Checked -Command "ollama" -Arguments @("pull", "qwen3:8b")
    Write-Host "[MODEL] Creating $ModelName"
    Invoke-Checked -Command "ollama" -Arguments @("create", $ModelName, "-f", $modelfile)
}

$report = [ordered]@{
    release = "MKultra_v0.3"
    completed_at = (Get-Date).ToUniversalTime().ToString("o")
    root = $Root
    model = $ModelName
    dry_run = [bool]$DryRun
    repositories = $results
}

$reportPath = Join-Path $Root "MKultra_v0.3-update-report.json"
if ($DryRun) {
    $report | ConvertTo-Json -Depth 8
}
else {
    $report | ConvertTo-Json -Depth 8 | Set-Content -Path $reportPath -Encoding UTF8
    Write-Host "Update report: $reportPath"
}

$failed = @($results | Where-Object { $_.status -eq "failed" }).Count
$dirty = @($results | Where-Object { $_.status -eq "skipped-dirty" }).Count
Write-Host "MKultra v0.3 local update completed. Failed: $failed; skipped dirty: $dirty"

if ($failed -gt 0) {
    exit 2
}
