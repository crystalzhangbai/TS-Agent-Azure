param(
    [int]$Port = 3978,
    [switch]$SkipBootstrap,
    [switch]$SkipEndpointUpdate
)

$ErrorActionPreference = "Stop"

function Import-DotEnvToMap {
    param([string]$Path)

    $map = @{}
    if (-not (Test-Path $Path)) {
        return $map
    }

    Get-Content $Path | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#") -or -not $line.Contains("=")) {
            return
        }

        $parts = $line.Split("=", 2)
        if ($parts.Count -ne 2) {
            return
        }

        $key = $parts[0].Trim()
        $value = $parts[1].Trim()
        $map[$key] = $value
    }

    return $map
}

function Test-AzLoggedIn {
    if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
        return $false
    }

    az account show -o none 2>$null | Out-Null
    return ($LASTEXITCODE -eq 0)
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host "[entry] colleague quick start" -ForegroundColor Cyan

if (-not $SkipBootstrap) {
    Write-Host "[step] bootstrap dependencies (python + devtunnel)" -ForegroundColor Cyan
    & (Join-Path $scriptDir "bootstrap.ps1") -SkipAzureCli
    if ($LASTEXITCODE -ne 0) {
        throw "bootstrap failed"
    }
}

$bridgeDir = Join-Path $scriptDir "bridge"
if (-not (Test-Path $bridgeDir)) {
    throw "bridge folder not found: $bridgeDir"
}

$envPath = Join-Path $bridgeDir ".env"
$envExamplePath = Join-Path $bridgeDir ".env.example"
if (-not (Test-Path $envPath)) {
    if (Test-Path $envExamplePath) {
        Copy-Item $envExamplePath $envPath
        Write-Host "[init] created bridge/.env from .env.example" -ForegroundColor Yellow
    } else {
        throw "missing bridge/.env and bridge/.env.example"
    }
}

$cfg = Import-DotEnvToMap -Path $envPath
$required = @(
    "MicrosoftAppId",
    "MicrosoftAppPassword",
    "MicrosoftAppTenantId",
    "FOUNDRY_PROJECT_ENDPOINT",
    "FOUNDRY_TENANT_ID",
    "FOUNDRY_CLIENT_ID",
    "FOUNDRY_CLIENT_SECRET"
)
$missing = @()
foreach ($k in $required) {
    if (-not $cfg.ContainsKey($k) -or [string]::IsNullOrWhiteSpace($cfg[$k])) {
        $missing += $k
    }
}

if ($missing.Count -gt 0) {
    Write-Host "[error] missing required settings in bridge/.env:" -ForegroundColor Red
    $missing | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    Write-Host "[hint] fill bridge/.env then rerun start-colleague.cmd" -ForegroundColor Yellow
    exit 1
}

$hasMgmtSp = (
    $cfg.ContainsKey("MGMT_SP_TENANT_ID") -and -not [string]::IsNullOrWhiteSpace($cfg["MGMT_SP_TENANT_ID"]) -and
    $cfg.ContainsKey("MGMT_SP_CLIENT_ID") -and -not [string]::IsNullOrWhiteSpace($cfg["MGMT_SP_CLIENT_ID"]) -and
    $cfg.ContainsKey("MGMT_SP_CLIENT_SECRET") -and -not [string]::IsNullOrWhiteSpace($cfg["MGMT_SP_CLIENT_SECRET"])
)

$canUseAz = Test-AzLoggedIn
$effectiveSkipEndpoint = $SkipEndpointUpdate
if (-not $effectiveSkipEndpoint -and -not $hasMgmtSp -and -not $canUseAz) {
    $effectiveSkipEndpoint = $true
    Write-Host "[mode] no MGMT_SP_* and no az login; will start bot but skip endpoint update" -ForegroundColor Yellow
    Write-Host "[action] owner can update endpoint after tunnel starts" -ForegroundColor Yellow
}

Set-Location $bridgeDir
if ($effectiveSkipEndpoint) {
    & (Join-Path $bridgeDir "run.ps1") -Port $Port -SkipEndpointUpdate
} else {
    & (Join-Path $bridgeDir "run.ps1") -Port $Port
}
