$ErrorActionPreference = "Stop"
$taskName = "SRE-Bridge-Autostart"

try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction Stop
    Write-Host "[ok] Removed scheduled task: $taskName" -ForegroundColor Green
} catch {
    Write-Host "[info] Scheduled task not found: $taskName" -ForegroundColor Yellow
}
