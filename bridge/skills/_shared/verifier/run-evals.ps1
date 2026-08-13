<#
.SYNOPSIS
  Authoring-regression linter for the verifier layer (counterpart to validate-skills.ps1).

.DESCRIPTION
  This does NOT replay live LLM routing/grounding assertions — that needs the real skill
  harness (fresh-context critic + MCP tools) and is a future capability. What it DOES, offline
  and deterministically, is guard the *authoring* of the verifier layer so a refactor can't
  silently break a verification pack:

    For every  .github/skills/<skill>/references/verification-pack.md :
      1. declares a  > **V-type:**  header
      2. links back to BOTH shared contracts
         (_shared/verifier/verifier-subagent.md  +  evidence-ledger.md)
      3. has the canonical sections: Truth source · 命门 · Checklist · Verifier procedure
      4. names at least one verdict class (CONTRADICTED / UNSUPPORTED / INFERRED / GROUNDED)
      5. the owning SKILL.md wires a gate (links to references/verification-pack.md)

    For every  .github/skills/<skill>/evals/evals.json :
      6. parses as JSON and has a non-empty evals[] array

  Exit code is 0 when everything passes, 1 when anything fails — safe for pre-commit / CI.

.EXAMPLE
  pwsh .github\skills\_shared\verifier\run-evals.ps1
  pwsh .github\skills\_shared\verifier\run-evals.ps1 -SkillsRoot .github\skills
#>
[CmdletBinding()]
param(
  [string]$SkillsRoot = (Join-Path $PSScriptRoot '..\..')
)

$ErrorActionPreference = 'Stop'
$skillsRoot = (Resolve-Path $SkillsRoot).Path

# --- canonical requirements every verification-pack must meet ---------------
$contractSubagent = 'verifier-subagent.md'
$contractLedger   = 'evidence-ledger.md'
$sectionChecks = @(
  @{ Name = 'V-type header';      Pattern = 'V-type:' }
  @{ Name = 'Truth source';       Pattern = 'Truth source' }
  @{ Name = '命门 section';        Pattern = '命门' }
  @{ Name = 'Checklist';          Pattern = 'Checklist' }
  @{ Name = 'Verifier procedure'; Pattern = 'Verifier procedure' }
)
$verdictClasses = @('CONTRADICTED','UNSUPPORTED','INFERRED','GROUNDED')

$results = @()

# --- 1..5  verification-pack authoring checks -------------------------------
$packs = Get-ChildItem -Path $skillsRoot -Directory |
  Where-Object { $_.Name -notlike '_*' } |
  ForEach-Object { Join-Path $_.FullName 'references\verification-pack.md' } |
  Where-Object { Test-Path $_ }

foreach ($pack in $packs) {
  $skill = (Split-Path (Split-Path $pack -Parent) -Parent | Split-Path -Leaf)
  $text  = Get-Content -Path $pack -Raw -Encoding UTF8
  $issues = @()

  foreach ($c in $sectionChecks) {
    if ($text -notmatch [regex]::Escape($c.Pattern)) { $issues += "missing '$($c.Name)'" }
  }
  if ($text -notmatch [regex]::Escape($contractSubagent)) { $issues += "no link to $contractSubagent" }
  if ($text -notmatch [regex]::Escape($contractLedger))   { $issues += "no link to $contractLedger" }
  if (-not ($verdictClasses | Where-Object { $text -match $_ })) { $issues += 'names no verdict class' }

  # 5. owning SKILL.md wires a gate
  $skillMd = Join-Path (Split-Path (Split-Path $pack -Parent) -Parent) 'SKILL.md'
  if (Test-Path $skillMd) {
    $md = Get-Content -Path $skillMd -Raw -Encoding UTF8
    if ($md -notmatch 'references/verification-pack\.md') { $issues += 'SKILL.md does not wire a gate' }
  } else {
    $issues += 'SKILL.md missing'
  }

  $results += [PSCustomObject]@{
    Skill  = $skill
    Check  = 'pack'
    Status = $(if ($issues.Count -eq 0) { 'PASS' } else { 'FAIL' })
    Issues = ($issues -join '; ')
  }
}

# --- 6  evals.json parses ----------------------------------------------------
$pyParse = @'
import sys, json, pathlib
p = pathlib.Path(sys.argv[1])
try:
    d = json.loads(p.read_text(encoding='utf-8'))
except Exception as e:
    print('PARSE_FAIL: ' + str(e).replace('\n',' ')[:160]); sys.exit(0)
ev = d.get('evals')
if not isinstance(ev, list) or len(ev) == 0:
    print('NO_EVALS'); sys.exit(0)
print('OK ' + str(len(ev)))
'@
$tmp = New-TemporaryFile
Set-Content -Path $tmp -Value $pyParse -Encoding UTF8

$evalFiles = Get-ChildItem -Path $skillsRoot -Directory |
  Where-Object { $_.Name -notlike '_*' } |
  ForEach-Object { Join-Path $_.FullName 'evals\evals.json' } |
  Where-Object { Test-Path $_ }

foreach ($ev in $evalFiles) {
  $skill = (Split-Path (Split-Path $ev -Parent) -Parent | Split-Path -Leaf)
  $out = (& python $tmp $ev 2>&1 | Out-String).Trim()
  $ok = $out -like 'OK *'
  $results += [PSCustomObject]@{
    Skill  = $skill
    Check  = 'evals'
    Status = $(if ($ok) { 'PASS' } else { 'FAIL' })
    Issues = $(if ($ok) { "$($out.Substring(3)) eval(s)" } else { $out })
  }
}
Remove-Item $tmp -Force -ErrorAction SilentlyContinue

# --- report ------------------------------------------------------------------
$results | Sort-Object Status, Skill, Check | Format-Table -AutoSize

$failed = @($results | Where-Object Status -eq 'FAIL')
if ($failed.Count -gt 0) {
  Write-Host ""
  Write-Host "$($failed.Count) verifier-layer check(s) FAILED:" -ForegroundColor Red
  foreach ($f in $failed) { Write-Host "  ✗ [$($f.Check)] $($f.Skill): $($f.Issues)" -ForegroundColor Red }
  Write-Host ""
  Write-Host "Fix hints:" -ForegroundColor Yellow
  Write-Host "  • missing section → restore the canonical pack layout (Truth source · 命门 · Checklist · Verifier procedure)"
  Write-Host "  • no link to contract → link back to _shared/verifier/verifier-subagent.md and evidence-ledger.md"
  Write-Host "  • SKILL.md does not wire a gate → add the Verification Gate section that links references/verification-pack.md"
  Write-Host ""
  Write-Host "Note: this is an offline authoring linter. Live routing/grounding replay needs the skill harness (future)." -ForegroundColor DarkGray
  exit 1
}

Write-Host ""
Write-Host "All $($results.Count) verifier-layer check(s) PASS ($($packs.Count) packs, $($evalFiles.Count) eval sets)." -ForegroundColor Green
Write-Host "Note: offline authoring linter only — live routing/grounding replay needs the skill harness (future)." -ForegroundColor DarkGray
exit 0
