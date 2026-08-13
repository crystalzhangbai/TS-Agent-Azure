param(
    [int]$Port = 3978,
    [switch]$SkipEndpointUpdate,
    [switch]$SkipPreflight
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Wrapper entrypoint for colleagues. Use this to avoid command-name/path confusion.
if (-not $SkipPreflight) {
    & (Join-Path $scriptDir "preflight-check.ps1")
}

if ($SkipEndpointUpdate) {
    & (Join-Path $scriptDir "launch-bridge.ps1") -Port $Port -SkipEndpointUpdate
} else {
    & (Join-Path $scriptDir "launch-bridge.ps1") -Port $Port
}