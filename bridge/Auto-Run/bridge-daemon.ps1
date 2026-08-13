param(
    [int]$Port = 3978,
    [switch]$SkipEndpointUpdate
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$runtimeDir = Join-Path $scriptDir "runtime"
New-Item -ItemType Directory -Path $runtimeDir -Force | Out-Null
$daemonPidFile = Join-Path $runtimeDir "bridge-daemon.pid"
Set-Content -Path $daemonPidFile -Value $PID

$restartDelaySec = 10
$loop = $true

Write-Host "[daemon] SRE Bridge watchdog started (PID=$PID)" -ForegroundColor Cyan

while ($loop) {
    $args = @("-Port", "$Port")
    if ($SkipEndpointUpdate) {
        $args += "-SkipEndpointUpdate"
    }

    Write-Host "[daemon] launch-bridge.ps1 starting..." -ForegroundColor Gray
    & (Join-Path $scriptDir "launch-bridge.ps1") @args
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0) {
        # Normal exit means tunnel stopped or script terminated; restart to keep service up.
        Write-Host "[daemon] launch exited normally; restarting in $restartDelaySec sec" -ForegroundColor Yellow
        Start-Sleep -Seconds $restartDelaySec
    } else {
        $failedDelay = 75
        Write-Host "[daemon] launch exited with code $exitCode; restarting in $failedDelay sec" -ForegroundColor Yellow
        Start-Sleep -Seconds $failedDelay
    }
}
