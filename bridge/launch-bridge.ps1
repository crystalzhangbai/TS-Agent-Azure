param(
    [int]$Port = 3978,
    [switch]$SkipEndpointUpdate,
    [int]$TunnelRetryMax = 3
)

$ErrorActionPreference = "Stop"

function Import-DotEnv {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        return
    }

    Get-Content $Path | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#")) {
            return
        }

        $parts = $line.Split("=", 2)
        if ($parts.Count -ne 2) {
            return
        }

        $key = $parts[0].Trim()
        $value = $parts[1].Trim()
        Set-Item -Path ("Env:" + $key) -Value $value
    }
}

function Wait-ForHttpOk {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 20
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3
            if ($resp.StatusCode -eq 200) {
                return $true
            }
        } catch {
            Start-Sleep -Milliseconds 700
        }
    }
    return $false
}

function Normalize-TunnelBaseUrl {
    param([string]$Url)

    if ([string]::IsNullOrWhiteSpace($Url)) {
        return ""
    }

    $clean = $Url.Trim()
    if ($clean.EndsWith("/api/messages")) {
        $clean = $clean.Substring(0, $clean.Length - "/api/messages".Length)
    }
    return $clean.TrimEnd("/")
}

function Select-TunnelBaseUrlFromText {
    param(
        [string]$Text,
        [int]$Port
    )

    if ([string]::IsNullOrWhiteSpace($Text)) {
        return ""
    }

    # Accept multiple devtunnel host formats, e.g.:
    # https://name-3978.asse.devtunnels.ms
    # https://name-3978.jpe1.devtunnels.ms
    # https://name.jpe1.devtunnels.ms/api/messages
    $pattern = "https://[a-z0-9-]+(?:\.[a-z0-9-]+)*\.devtunnels\.ms(?:/api/messages)?"
    $matches = [regex]::Matches($Text.ToLowerInvariant(), $pattern)
    if (-not $matches -or $matches.Count -eq 0) {
        return ""
    }

    $normalized = @()
    foreach ($m in $matches) {
        $u = Normalize-TunnelBaseUrl -Url $m.Value
        if ($u) {
            $normalized += $u
        }
    }

    if ($normalized.Count -eq 0) {
        return ""
    }

    # Prefer URL that includes port suffix if present, but do not require it.
    $preferred = $normalized | Where-Object { $_ -match ("-" + $Port + "\.") } | Select-Object -First 1
    if ($preferred) {
        return $preferred
    }

    return ($normalized | Select-Object -First 1)
}

function Get-TunnelUrlFromLog {
    param(
        [string]$LogPath,
        [int]$Port,
        [int]$TimeoutSeconds = 25
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)

    while ((Get-Date) -lt $deadline) {
        if (Test-Path $LogPath) {
            $text = Get-Content $LogPath -Raw -ErrorAction SilentlyContinue
            if ([string]::IsNullOrWhiteSpace($text)) {
                Start-Sleep -Milliseconds 800
                continue
            }
            $url = Select-TunnelBaseUrlFromText -Text $text -Port $Port
            if ($url) {
                return $url
            }
        }
        Start-Sleep -Milliseconds 800
    }

    return ""
}

function Get-TunnelUrlFallback {
    param([int]$Port)

    try {
        $raw = devtunnel list | Out-String
        if ([string]::IsNullOrWhiteSpace($raw)) {
            return ""
        }

        $url = Select-TunnelBaseUrlFromText -Text $raw -Port $Port
        if ($url) {
            return $url
        }
    } catch {
        return ""
    }

    return ""
}

function Get-ArmToken {
    param(
        [string]$TenantId,
        [string]$ClientId,
        [string]$ClientSecret
    )

    $tokenUrl = "https://login.microsoftonline.com/$TenantId/oauth2/v2.0/token"
    $body = @{
        client_id = $ClientId
        client_secret = $ClientSecret
        scope = "https://management.azure.com/.default"
        grant_type = "client_credentials"
    }

    $resp = Invoke-RestMethod -Method Post -Uri $tokenUrl -Body $body -ContentType "application/x-www-form-urlencoded"
    return $resp.access_token
}

function Update-BotEndpointViaArm {
    param(
        [string]$ResourceId,
        [string]$Endpoint,
        [string]$TenantId,
        [string]$ClientId,
        [string]$ClientSecret
    )

    $token = Get-ArmToken -TenantId $TenantId -ClientId $ClientId -ClientSecret $ClientSecret
    $normalizedResourceId = ($ResourceId + "").Trim()
    if (-not $normalizedResourceId.StartsWith("/")) {
        $normalizedResourceId = "/" + $normalizedResourceId.TrimStart("/")
    }
    $uri = "https://management.azure.com{0}?api-version=2022-09-15" -f $normalizedResourceId

    $headers = @{ Authorization = "Bearer $token" }
    $current = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers

    $payload = @{
        location = $current.location
        sku = $current.sku
        kind = $current.kind
        tags = $current.tags
        properties = $current.properties
    }
    $payload.properties.endpoint = $Endpoint

    $jsonBody = $payload | ConvertTo-Json -Depth 50
    Invoke-RestMethod -Method Put -Uri $uri -Headers $headers -Body $jsonBody -ContentType "application/json" | Out-Null
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$runtimeDir = Join-Path $scriptDir "runtime"
New-Item -ItemType Directory -Path $runtimeDir -Force | Out-Null

Import-DotEnv -Path (Join-Path $scriptDir ".env")

$basePythonExe = $null
$basePythonArgs = @()

if (Get-Command python -ErrorAction SilentlyContinue) {
    $basePythonExe = "python"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $basePythonExe = "py"
    $basePythonArgs = @("-3")
} else {
    $fallbackPy = Join-Path $env:LOCALAPPDATA "Microsoft\WindowsApps\python.exe"
    if (Test-Path $fallbackPy) {
        $basePythonExe = $fallbackPy
    }
}

if (-not $basePythonExe) {
    Write-Host "[error] no usable Python launcher found (python/py)." -ForegroundColor Red
    Write-Host "Install Python first, then rerun this script." -ForegroundColor Red
    exit 1
}

$venvPython = Join-Path $scriptDir ".venv\Scripts\python.exe"
$venvHealthy = $false
if (Test-Path $venvPython) {
    try {
        & $venvPython --version *> $null
        if ($LASTEXITCODE -eq 0) {
            $venvHealthy = $true
        }
    } catch {
        $venvHealthy = $false
    }
}

if (-not $venvHealthy) {
    if (Test-Path (Join-Path $scriptDir ".venv")) {
        Write-Host "[setup] detected invalid copied .venv, rebuilding for this machine" -ForegroundColor Yellow
        Remove-Item (Join-Path $scriptDir ".venv") -Recurse -Force -ErrorAction SilentlyContinue
    } else {
        Write-Host "[setup] creating .venv" -ForegroundColor Cyan
    }

    & $basePythonExe @($basePythonArgs + @("-m", "venv", ".venv"))
    $venvPython = Join-Path $scriptDir ".venv\Scripts\python.exe"
    if (-not (Test-Path $venvPython)) {
        Write-Host "[error] failed to create .venv on this machine" -ForegroundColor Red
        exit 1
    }
}

# A copied .venv can contain hardcoded interpreter paths from another machine.
# If current venv python cannot run, rebuild venv locally on this machine.
$venvHealthy = $true
try {
    & $venvPython --version | Out-Null
    if ($LASTEXITCODE -ne 0) {
        $venvHealthy = $false
    }
} catch {
    $venvHealthy = $false
}

if (-not $venvHealthy) {
    Write-Host "[warn] existing .venv is invalid for this machine. Recreating .venv..." -ForegroundColor Yellow
    try {
        Remove-Item -Path (Join-Path $scriptDir ".venv") -Recurse -Force -ErrorAction Stop
    } catch {
        Write-Host "[warn] failed to remove old .venv; trying to continue with overwrite" -ForegroundColor Yellow
    }
    & $basePythonExe @($basePythonArgs + @("-m", "venv", ".venv"))
    $venvPython = Join-Path $scriptDir ".venv\Scripts\python.exe"
    if (-not (Test-Path $venvPython)) {
        Write-Host "[error] failed to recreate .venv using detected Python launcher" -ForegroundColor Red
        exit 1
    }
}

Write-Host "[setup] installing requirements" -ForegroundColor Cyan
& $venvPython -m pip install --prefer-binary -r (Join-Path $scriptDir "requirements.txt")

$listenerPids = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty OwningProcess -Unique
if ($listenerPids) {
    foreach ($pidValue in $listenerPids) {
        try {
            Stop-Process -Id $pidValue -Force -ErrorAction Stop
            Write-Host "[cleanup] stopped PID $pidValue on port $Port" -ForegroundColor Yellow
        } catch {
            Write-Host ("[cleanup] failed to stop PID {0}: {1}" -f $pidValue, $_.Exception.Message) -ForegroundColor Red
        }
    }
}

$botLog = Join-Path $runtimeDir "bot.log"
$botErrLog = Join-Path $runtimeDir "bot.err.log"
$tunnelLog = Join-Path $runtimeDir "tunnel.log"
$tunnelErrLog = Join-Path $runtimeDir "tunnel.err.log"
$pidFile = Join-Path $runtimeDir "bridge.pids.json"
Clear-Content -Path $botLog -ErrorAction SilentlyContinue
Clear-Content -Path $botErrLog -ErrorAction SilentlyContinue
Clear-Content -Path $tunnelLog -ErrorAction SilentlyContinue
Clear-Content -Path $tunnelErrLog -ErrorAction SilentlyContinue

Write-Host "[start] launching bot server" -ForegroundColor Cyan
$botProc = Start-Process -FilePath $venvPython `
    -ArgumentList "app.py" `
    -WorkingDirectory $scriptDir `
    -PassThru `
    -WindowStyle Hidden `
    -RedirectStandardOutput $botLog `
    -RedirectStandardError $botErrLog

if (-not (Wait-ForHttpOk -Url "http://127.0.0.1:$Port/" -TimeoutSeconds 20) -and `
    -not (Wait-ForHttpOk -Url "http://localhost:$Port/" -TimeoutSeconds 8)) {
    Write-Host "[error] bot failed health check on both http://127.0.0.1:$Port/ and http://localhost:$Port/" -ForegroundColor Red
    Write-Host "See log: $botLog" -ForegroundColor Red
    exit 1
}

if (-not (Get-Command devtunnel -ErrorAction SilentlyContinue)) {
    Write-Host "[error] devtunnel CLI not found in PATH" -ForegroundColor Red
    Write-Host "Install devtunnel then rerun launch-bridge.ps1" -ForegroundColor Red
    exit 1
}

Write-Host "[start] launching dev tunnel" -ForegroundColor Cyan
$devTunnelName = ($env:DEVTUNNEL_NAME + "").Trim()
$tunnelBaseUrl = ""
$tunnelProc = $null
$usingNamedTunnel = $false

$tunnelAttempts = @()
if ($devTunnelName) {
    $tunnelAttempts += ,@("host", "-t", $devTunnelName, "-p", "$Port", "--allow-anonymous")
    $tunnelAttempts += ,@("host", "-p", "$Port", "--allow-anonymous")
} else {
    $tunnelAttempts += ,@("host", "-p", "$Port", "--allow-anonymous")
}

for ($i = 0; $i -lt $tunnelAttempts.Count; $i++) {
    $attemptArgs = $tunnelAttempts[$i]
    $usingNamedTunnel = ($attemptArgs -contains "-t")

    if ($i -gt 0 -and $devTunnelName) {
        Write-Host "[warn] named tunnel start failed or not ready; retry without -t" -ForegroundColor Yellow
    }

    for ($retry = 1; $retry -le [Math]::Max(1, $TunnelRetryMax); $retry++) {
        Clear-Content -Path $tunnelLog -ErrorAction SilentlyContinue
        Clear-Content -Path $tunnelErrLog -ErrorAction SilentlyContinue

        $tunnelProc = Start-Process -FilePath "devtunnel" `
            -ArgumentList $attemptArgs `
            -WorkingDirectory $scriptDir `
            -PassThru `
            -WindowStyle Hidden `
            -RedirectStandardOutput $tunnelLog `
            -RedirectStandardError $tunnelErrLog

        Start-Sleep -Milliseconds 1200
        if ($tunnelProc.HasExited) {
            Write-Host ("[warn] dev tunnel process exited early (exit={0})" -f $tunnelProc.ExitCode) -ForegroundColor Yellow
        } else {
            $tunnelBaseUrl = Get-TunnelUrlFromLog -LogPath $tunnelLog -Port $Port -TimeoutSeconds 90
            if (-not $tunnelBaseUrl) {
                $tunnelBaseUrl = Get-TunnelUrlFallback -Port $Port
            }
            if ($tunnelBaseUrl) {
                break
            }
        }

        $tunnelOut = Get-Content $tunnelLog -Raw -ErrorAction SilentlyContinue
        $tunnelErr = Get-Content $tunnelErrLog -Raw -ErrorAction SilentlyContinue
        $rateLimited = Test-TunnelRateLimited -OutText $tunnelOut -ErrText $tunnelErr

        try {
            if ($tunnelProc -and -not $tunnelProc.HasExited) {
                Stop-Process -Id $tunnelProc.Id -Force -ErrorAction SilentlyContinue
            }
        } catch {
        }

        if ($rateLimited -and $retry -lt $TunnelRetryMax) {
            Write-Host "[warn] devtunnel rate limited, waiting 70 seconds before retry..." -ForegroundColor Yellow
            Start-Sleep -Seconds 70
            continue
        }

        if ($retry -lt $TunnelRetryMax) {
            Start-Sleep -Seconds 2
        }
    }

    if ($tunnelBaseUrl) {
        break
    }
}

$tunnelReady = $true
if (-not $tunnelBaseUrl) {
    $tunnelReady = $false
    $tunnelOut = Get-Content $tunnelLog -Raw -ErrorAction SilentlyContinue
    $tunnelErr = Get-Content $tunnelErrLog -Raw -ErrorAction SilentlyContinue
    $combined = (($tunnelOut + "`n" + $tunnelErr) + "").Trim()

    if ($combined -match "Login required") {
        Write-Host "[error] dev tunnel login required. Please run: devtunnel user login" -ForegroundColor Red
        Write-Host "[hint] login must be completed in this machine/user context, then rerun start script." -ForegroundColor Yellow
    }

    if ($combined -match "Unauthorized tunnel creation access" -or $combined -match "Request not permitted") {
        Write-Host "[error] dev tunnel creation is unauthorized for current identity." -ForegroundColor Red
        Write-Host "[hint] run: devtunnel user login" -ForegroundColor Yellow
        if ($devTunnelName) {
            Write-Host "[hint] or ask tunnel owner to grant create/use permission on named tunnel: $devTunnelName" -ForegroundColor Yellow
        } else {
            Write-Host "[hint] or provide DEVTUNNEL_NAME for a pre-created shared tunnel with proper permission." -ForegroundColor Yellow
        }
    }

    if ($combined -match "Rate limit exceeded") {
        Write-Host "[error] devtunnel rate limit exceeded. Please wait about one minute and retry." -ForegroundColor Red
        Write-Host "[hint] reduce frequent restart; keep one long-running tunnel process." -ForegroundColor Yellow
    }

    Write-Host "[warn] tunnel URL not detected from log yet." -ForegroundColor Yellow
    Write-Host "Check log: $tunnelLog" -ForegroundColor Yellow
    Write-Host "Check error log: $tunnelErrLog" -ForegroundColor Yellow
} else {
    Write-Host "[ok] tunnel url: $tunnelBaseUrl" -ForegroundColor Green
    if ($usingNamedTunnel -and $devTunnelName) {
        Write-Host "[info] using named tunnel: $devTunnelName" -ForegroundColor Gray
    } elseif ($devTunnelName) {
        Write-Host "[info] named tunnel fallback succeeded without -t" -ForegroundColor Gray
    }
}

$resourceId = $env:BOT_RESOURCE_ID
if (-not $SkipEndpointUpdate -and $resourceId -and $tunnelBaseUrl) {
    $endpoint = "$tunnelBaseUrl/api/messages"
    $mgmtTenantId = $env:MGMT_SP_TENANT_ID
    $mgmtClientId = $env:MGMT_SP_CLIENT_ID
    $mgmtClientSecret = $env:MGMT_SP_CLIENT_SECRET
    $updated = $false

    try {
        if ($mgmtTenantId -and $mgmtClientId -and $mgmtClientSecret) {
            Update-BotEndpointViaArm `
                -ResourceId $resourceId `
                -Endpoint $endpoint `
                -TenantId $mgmtTenantId `
                -ClientId $mgmtClientId `
                -ClientSecret $mgmtClientSecret
            Write-Host "[ok] Azure Bot endpoint updated via management SP: $endpoint" -ForegroundColor Green
            $updated = $true
        }

        if (-not $updated -and (Get-Command az -ErrorAction SilentlyContinue)) {
            az resource update --ids $resourceId --set properties.endpoint="$endpoint" -o none
            if ($LASTEXITCODE -ne 0) {
                throw "az resource update failed with exit code $LASTEXITCODE"
            }
            Write-Host "[ok] Azure Bot endpoint updated via Azure CLI: $endpoint" -ForegroundColor Green
            $updated = $true
        }

        if (-not $updated) {
            Write-Host "[warn] endpoint not updated: provide MGMT_SP_* or install/login Azure CLI" -ForegroundColor Yellow
            Write-Host "[hint] set BOT_RESOURCE_ID + MGMT_SP_* in .env for machine-independent auto update." -ForegroundColor Yellow
        }
    } catch {
        Write-Host ("[warn] endpoint update primary attempt failed: {0}" -f $_.Exception.Message) -ForegroundColor Yellow
        if (-not $updated -and (Get-Command az -ErrorAction SilentlyContinue)) {
            try {
                az resource update --ids $resourceId --set properties.endpoint="$endpoint" -o none
                if ($LASTEXITCODE -ne 0) {
                    throw "az resource update failed with exit code $LASTEXITCODE"
                }
                Write-Host "[ok] Azure Bot endpoint updated via Azure CLI fallback: $endpoint" -ForegroundColor Green
                $updated = $true
            } catch {
                Write-Host ("[warn] failed to update Azure Bot endpoint automatically: {0}" -f $_.Exception.Message) -ForegroundColor Yellow
                Write-Host "Run manually with endpoint: $endpoint" -ForegroundColor Yellow
            }
        } else {
            Write-Host "[warn] failed to update Azure Bot endpoint automatically" -ForegroundColor Yellow
            Write-Host "Run manually with endpoint: $endpoint" -ForegroundColor Yellow
        }
    }
} elseif (-not $SkipEndpointUpdate) {
    Write-Host "[warn] skip endpoint update: BOT_RESOURCE_ID missing or tunnel URL not ready" -ForegroundColor Yellow
}

@{
    botPid = $botProc.Id
    tunnelPid = $tunnelProc.Id
    port = $Port
    tunnelBaseUrl = $tunnelBaseUrl
    updatedAt = (Get-Date).ToString("s")
} | ConvertTo-Json | Set-Content -Path $pidFile

Write-Host "" 
Write-Host "[ready] SRE Bridge started" -ForegroundColor Green
Write-Host "  Local health: http://localhost:$Port/"
if ($tunnelBaseUrl) {
    Write-Host "  Tunnel: $tunnelBaseUrl"
    Write-Host "  Messaging endpoint: $tunnelBaseUrl/api/messages"
}
Write-Host "  Bot log: $botLog"
Write-Host "  Bot error log: $botErrLog"
Write-Host "  Tunnel log: $tunnelLog"
Write-Host "  Tunnel error log: $tunnelErrLog"
Write-Host "  Stop command: .\stop-bridge.ps1"

if (-not $tunnelReady) {
    Write-Host "[error] local bot is up, but tunnel is not ready; Teams cannot reach this bot yet." -ForegroundColor Red
    exit 1
}

function Test-TunnelRateLimited {
    param(
        [string]$OutText,
        [string]$ErrText
    )

    $combined = (($OutText + "`n" + $ErrText) + "").ToLowerInvariant()
    return ($combined -match "rate limit exceeded" -or $combined -match "too many requests")
}