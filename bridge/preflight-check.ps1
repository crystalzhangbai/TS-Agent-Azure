param(
    [switch]$FailOnTodo
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

function Get-PythonExe {
    $venv = Join-Path $scriptDir ".venv\Scripts\python.exe"
    if (Test-Path $venv) {
        try {
            & $venv --version *> $null
            if ($LASTEXITCODE -eq 0) {
                return $venv
            }
        } catch {
        }
    }
    if (Get-Command python -ErrorAction SilentlyContinue) {
        return "python"
    }
    if (Get-Command py -ErrorAction SilentlyContinue) {
        return "py -3"
    }
    throw "No Python found. Please install Python or create .venv first."
}

$pyCmd = Get-PythonExe
$tmp = Join-Path $env:TEMP "sre_preflight_report.py"
$pyCode = @'
import json
import os
import sys
sys.path.insert(0, os.getcwd())
from preflight_todo import build_preflight_report
print(json.dumps(build_preflight_report(), ensure_ascii=True))
'@
Set-Content -Path $tmp -Value $pyCode -Encoding UTF8

if ($pyCmd -eq "py -3") {
    $raw = py -3 $tmp
    if ($LASTEXITCODE -ne 0) {
        throw "preflight python runner failed via py -3"
    }
} else {
    $raw = & $pyCmd $tmp
    if ($LASTEXITCODE -ne 0) {
        throw "preflight python runner failed via $pyCmd"
    }
}

$report = $raw | ConvertFrom-Json

$lines = @()
$lines += "SRE Bridge Preflight"
$lines += "=" * 64
$lines += ""
$lines += "Summary: $($report.passed)/$($report.total) passed"
$lines += ""

$idx = 1
foreach ($item in $report.items) {
    $icon = if ($item.checked) { "[x]" } else { "[ ]" }
    $state = if ($item.checked) { "PASS" } else { "TODO" }
    $lines += "$idx. $icon [$state] $($item.title)"
    $lines += "   Current: $($item.detail)"
    if (-not $item.checked) {
        $lines += "   Fix: $($item.fix)"
    }
    $lines += ""
    $idx++
}

$lines += "Next Steps"
$lines += "-" * 64
foreach ($step in $report.next_steps) {
    $lines += "- $step"
}

$outText = $lines -join "`r`n"

Write-Host "[info] Preflight result opened in popup window." -ForegroundColor Cyan

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$form = New-Object System.Windows.Forms.Form
$form.Text = "SRE Bridge Preflight Check"
$form.Width = 980
$form.Height = 760
$form.StartPosition = "CenterScreen"

$panel = New-Object System.Windows.Forms.Panel
$panel.Dock = "Top"
$panel.Height = 46

$label = New-Object System.Windows.Forms.Label
$label.Dock = "Fill"
$label.TextAlign = [System.Drawing.ContentAlignment]::MiddleLeft
$label.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
$label.Padding = New-Object System.Windows.Forms.Padding(12, 0, 0, 0)

if ($report.ok) {
    $panel.BackColor = [System.Drawing.Color]::FromArgb(223, 246, 228)
    $label.ForeColor = [System.Drawing.Color]::FromArgb(17, 94, 33)
    $label.Text = "Status: READY | All preflight checks passed"
} else {
    $panel.BackColor = [System.Drawing.Color]::FromArgb(255, 243, 224)
    $label.ForeColor = [System.Drawing.Color]::FromArgb(140, 78, 0)
    $label.Text = "Status: ACTION REQUIRED | Complete TODO items before launch"
}

$panel.Controls.Add($label)

$box = New-Object System.Windows.Forms.TextBox
$box.Multiline = $true
$box.ReadOnly = $true
$box.ScrollBars = "Both"
$box.WordWrap = $false
$box.Font = New-Object System.Drawing.Font("Consolas", 10)
$box.Dock = "Fill"
$box.Text = $outText

$form.Controls.Add($box)
$form.Controls.Add($panel)
[void]$form.ShowDialog()

if ($FailOnTodo -and (-not $report.ok)) {
    exit 2
}

exit 0
