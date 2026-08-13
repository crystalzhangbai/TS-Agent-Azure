param(
    [switch]$SkipAzureCli,
    [switch]$ForceReinstall,
    [int]$RetryCount = 2
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[setup] $Message" -ForegroundColor Cyan
}

function Refresh-Path {
    $machinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path = "$machinePath;$userPath"
}

function Test-IsAdmin {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Invoke-WithRetry {
    param(
        [scriptblock]$Action,
        [string]$Description,
        [int]$MaxRetries = 2
    )

    for ($attempt = 1; $attempt -le ($MaxRetries + 1); $attempt++) {
        try {
            & $Action
            return
        } catch {
            if ($attempt -gt $MaxRetries) {
                throw
            }
            Write-Host "[warn] $Description failed (attempt $attempt). retrying..." -ForegroundColor Yellow
            Start-Sleep -Seconds 2
        }
    }
}

function Ensure-WingetAvailable {
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        throw "winget is not available. Please install App Installer from Microsoft Store first."
    }
}

function Ensure-WingetPackage {
    param(
        [string]$Id,
        [string]$Name,
        [switch]$Force
    )

    if (-not $Force) {
        $listOutput = winget list -e --id $Id --accept-source-agreements 2>$null | Out-String
        if ($LASTEXITCODE -eq 0 -and $listOutput -match [regex]::Escape($Id)) {
            Write-Host "[ok] $Name already installed" -ForegroundColor Green
            return
        }
    }

    Write-Step "installing $Name ($Id)"
    Invoke-WithRetry -Description "install $Name" -MaxRetries $RetryCount -Action {
        winget install -e --id $Id --accept-package-agreements --accept-source-agreements --silent
        if ($LASTEXITCODE -ne 0) {
            throw "winget install returned exit code $LASTEXITCODE"
        }
    }
    Write-Host "[ok] installed $Name" -ForegroundColor Green
}

function Show-EnvironmentSummary {
    $osArch = [System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture
    $procArch = [System.Runtime.InteropServices.RuntimeInformation]::ProcessArchitecture
    Write-Host "[info] OS architecture: $osArch" -ForegroundColor Gray
    Write-Host "[info] PowerShell process architecture: $procArch" -ForegroundColor Gray
    if ($osArch -eq "Arm64" -and $procArch -ne "Arm64") {
        Write-Host "[warn] running x64/x86 shell on ARM64 Windows can reduce compatibility. Prefer native ARM64 PowerShell if available." -ForegroundColor Yellow
    }
}

Write-Step "preflight checks"
Show-EnvironmentSummary
if (-not (Test-IsAdmin)) {
    Write-Host "[warn] not running as Administrator. Install may still work, but Admin mode is recommended." -ForegroundColor Yellow
}

Ensure-WingetAvailable
Ensure-WingetPackage -Id "Python.Python.3.12" -Name "Python 3.12" -Force:$ForceReinstall
if (-not $SkipAzureCli) {
    Ensure-WingetPackage -Id "Microsoft.AzureCLI" -Name "Azure CLI" -Force:$ForceReinstall
}
Ensure-WingetPackage -Id "Microsoft.devtunnel" -Name "Dev Tunnel CLI" -Force:$ForceReinstall

Refresh-Path

Write-Step "verifying commands"
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[warn] python command is not available in current terminal yet. open a new terminal and run again if needed." -ForegroundColor Yellow
} else {
    $pyVer = python --version 2>&1
    Write-Host "[ok] $pyVer" -ForegroundColor Green
}

if (-not $SkipAzureCli) {
    if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
        Write-Host "[warn] az command is not available in current terminal yet. open a new terminal and run again if needed." -ForegroundColor Yellow
    } else {
        $azVer = ""
        try {
            $azVersionJson = az version -o json 2>$null
            if ($LASTEXITCODE -eq 0 -and $azVersionJson) {
                $azVersionObj = $azVersionJson | ConvertFrom-Json -ErrorAction Stop
                $azVer = ($azVersionObj.'azure-cli' + "").Trim()
            }
        } catch {
            $azVer = ""
        }

        if ($azVer) {
            Write-Host "[ok] Azure CLI $azVer" -ForegroundColor Green
        } else {
            Write-Host "[ok] Azure CLI installed" -ForegroundColor Green
        }
    }
}

if (-not (Get-Command devtunnel -ErrorAction SilentlyContinue)) {
    Write-Host "[warn] devtunnel command is not available in current terminal yet. open a new terminal and run again if needed." -ForegroundColor Yellow
} else {
    Write-Host "[ok] devtunnel installed" -ForegroundColor Green
}

Write-Host "[next] start bridge with: .\\bridge\\run.cmd" -ForegroundColor Green