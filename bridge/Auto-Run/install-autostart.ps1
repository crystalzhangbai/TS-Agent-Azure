param(
    [int]$Port = 3978,
    [switch]$SkipEndpointUpdate,
    [switch]$CurrentUser
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$taskName = "SRE-Bridge-Autostart"

$pwsh = (Get-Command powershell -ErrorAction SilentlyContinue)
if (-not $pwsh) {
    throw "powershell not found"
}

$arg = "-NoProfile -ExecutionPolicy Bypass -File `"$scriptDir\bridge-daemon.ps1`" -Port $Port"
if ($SkipEndpointUpdate) {
    $arg += " -SkipEndpointUpdate"
}

$action = New-ScheduledTaskAction -Execute $pwsh.Source -Argument $arg
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1)

if ($CurrentUser) {
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null
} else {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -RunLevel Highest -Force | Out-Null
}

Write-Host "[ok] Scheduled task installed: $taskName" -ForegroundColor Green
Write-Host "Start now: schtasks /Run /TN $taskName"
