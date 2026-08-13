param(
    [int]$Port = 3978,
    [string]$TunnelId = ""
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command devtunnel -ErrorAction SilentlyContinue)) {
    throw "devtunnel CLI not found in PATH"
}

if ($TunnelId) {
    Write-Host "Starting existing dev tunnel $TunnelId on port $Port" -ForegroundColor Cyan
    devtunnel host -t $TunnelId -p $Port --allow-anonymous
} else {
    Write-Host "Starting a new dev tunnel on port $Port" -ForegroundColor Cyan
    devtunnel host -p $Port --allow-anonymous
}