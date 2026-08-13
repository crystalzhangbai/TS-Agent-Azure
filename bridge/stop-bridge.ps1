$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pidFile = Join-Path $scriptDir "runtime\bridge.pids.json"
$daemonPidFile = Join-Path $scriptDir "runtime\bridge-daemon.pid"
$botPort = 3978

function Stop-ProcessSafe {
    param(
        [int]$Pid,
        [string]$Reason
    )

    try {
        $proc = Get-Process -Id $Pid -ErrorAction Stop
        Stop-Process -Id $Pid -Force
        Write-Host "Stopped PID $Pid ($($proc.ProcessName)) via $Reason"
        return $true
    } catch {
        Write-Host "PID $Pid already stopped"
        return $false
    }
}

if (Test-Path $daemonPidFile) {
    try {
        $daemonPid = (Get-Content $daemonPidFile -Raw).Trim()
        if ($daemonPid) {
            Stop-ProcessSafe -Pid ([int]$daemonPid) -Reason "daemon pid file" | Out-Null
        }
    } catch {
    }
    Remove-Item $daemonPidFile -Force -ErrorAction SilentlyContinue
}

if (Test-Path $pidFile) {
    $state = Get-Content $pidFile -Raw | ConvertFrom-Json
    $pids = @($state.botPid, $state.tunnelPid) | Where-Object { $_ }

    foreach ($pidValue in $pids) {
        Stop-ProcessSafe -Pid ([int]$pidValue) -Reason "runtime pid file" | Out-Null
    }

    Remove-Item $pidFile -Force
    Write-Host "Stopped SRE Bridge runtime from pid tracking."
} else {
    Write-Host "No runtime/bridge.pids.json found. Trying port fallback."
}

$listeners = Get-NetTCPConnection -LocalPort $botPort -State Listen -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty OwningProcess -Unique

if ($listeners) {
    foreach ($ownerPid in $listeners) {
        Stop-ProcessSafe -Pid ([int]$ownerPid) -Reason "port $botPort listener" | Out-Null
    }
    Write-Host "Port fallback finished for $botPort."
} else {
    Write-Host "No listener found on port $botPort."
}

Write-Host "Stop flow completed."
