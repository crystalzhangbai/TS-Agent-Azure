$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pidFile = Join-Path $scriptDir "runtime\bridge.pids.json"
$daemonPidFile = Join-Path $scriptDir "runtime\bridge-daemon.pid"

if (Test-Path $daemonPidFile) {
    try {
        $daemonPid = (Get-Content $daemonPidFile -Raw).Trim()
        if ($daemonPid) {
            Stop-Process -Id ([int]$daemonPid) -Force -ErrorAction SilentlyContinue
            Write-Host "Stopped daemon PID $daemonPid"
        }
    } catch {
    }
    Remove-Item $daemonPidFile -Force -ErrorAction SilentlyContinue
}

if (-not (Test-Path $pidFile)) {
    Write-Host "No runtime/bridge.pids.json found. Nothing to stop."
    exit 0
}

$state = Get-Content $pidFile -Raw | ConvertFrom-Json
$pids = @($state.botPid, $state.tunnelPid) | Where-Object { $_ }

foreach ($pidValue in $pids) {
    try {
        $proc = Get-Process -Id $pidValue -ErrorAction Stop
        Stop-Process -Id $pidValue -Force
        Write-Host "Stopped PID $pidValue ($($proc.ProcessName))"
    } catch {
        Write-Host "PID $pidValue already stopped"
    }
}

Remove-Item $pidFile -Force
Write-Host "Stopped SRE Bridge runtime."