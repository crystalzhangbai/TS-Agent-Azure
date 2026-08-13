<#
.SYNOPSIS
  Validate every SKILL.md in .github/skills/*/ against skill-loader rules.

.DESCRIPTION
  Catches the failures the Copilot CLI / VS Code skill loader rejects:
    1. description > 1024 chars
    2. YAML frontmatter that fails strict yaml.safe_load (e.g. unquoted
       values containing ": " which YAML treats as a nested mapping)
    3. missing required fields (name, description)
    4. name field that does not match the parent folder name

  Run from repo root before committing skill changes. Exit code is 0
  when all skills PASS, 1 when any FAIL — safe for pre-commit / CI.

.EXAMPLE
  pwsh .github\skills\_shared\validate-skills.ps1
  pwsh .github\skills\_shared\validate-skills.ps1 -SkillsRoot .github\skills
#>
[CmdletBinding()]
param(
  [string]$SkillsRoot = (Join-Path $PSScriptRoot '..')
)

$ErrorActionPreference = 'Stop'
$MAX_DESC = 1024

$skillsRoot = (Resolve-Path $SkillsRoot).Path
$skillDirs = Get-ChildItem -Path $skillsRoot -Directory |
  Where-Object { $_.Name -notlike '_*' -and (Test-Path (Join-Path $_.FullName 'SKILL.md')) }

if (-not $skillDirs) {
  Write-Host "No SKILL.md files found under $skillsRoot" -ForegroundColor Yellow
  exit 0
}

$pyCheck = @'
import sys, re, json, yaml, pathlib
path = pathlib.Path(sys.argv[1])
folder = path.parent.name
text = path.read_text(encoding='utf-8')
m = re.match(r'(?s)^---\s*\n(.*?)\n---', text)
out = {'folder': folder, 'errors': [], 'desc_len': None, 'name': None}
if not m:
    out['errors'].append('NO_FRONTMATTER')
    print(json.dumps(out)); sys.exit(0)
fm = m.group(1)
try:
    data = yaml.safe_load(fm) or {}
except yaml.YAMLError as e:
    msg = str(e).replace('\n', ' ')
    out['errors'].append(f'YAML_PARSE_FAIL: {msg[:200]}')
    print(json.dumps(out)); sys.exit(0)
name = data.get('name')
desc = data.get('description', '')
out['name'] = name
out['desc_len'] = len(desc) if isinstance(desc, str) else -1
if not name:
    out['errors'].append('MISSING_NAME')
elif name != folder:
    out['errors'].append(f'NAME_MISMATCH (frontmatter={name!r} folder={folder!r})')
if not isinstance(desc, str) or not desc.strip():
    out['errors'].append('MISSING_DESCRIPTION')
elif len(desc) > 1024:
    out['errors'].append(f'DESC_TOO_LONG ({len(desc)} > 1024)')
print(json.dumps(out))
'@

$tmp = New-TemporaryFile
Set-Content -Path $tmp -Value $pyCheck -Encoding UTF8

$results = @()
foreach ($dir in $skillDirs) {
  $skillMd = Join-Path $dir.FullName 'SKILL.md'
  $json = & python $tmp $skillMd 2>&1 | Out-String
  try {
    $r = $json | ConvertFrom-Json
  } catch {
    $results += [PSCustomObject]@{ Skill=$dir.Name; Status='FAIL'; DescLen='?'; Issues=("python invocation failed: " + $json.Trim()) }
    continue
  }
  $status = if ($r.errors.Count -eq 0) { 'PASS' } else { 'FAIL' }
  $results += [PSCustomObject]@{
    Skill   = $r.folder
    Status  = $status
    DescLen = $r.desc_len
    Issues  = ($r.errors -join '; ')
  }
}

Remove-Item $tmp -Force -ErrorAction SilentlyContinue

# Pretty print
$results | Sort-Object Status, Skill | Format-Table -AutoSize

$failed = @($results | Where-Object Status -eq 'FAIL')
if ($failed.Count -gt 0) {
  Write-Host ""
  Write-Host "$($failed.Count) skill(s) FAILED validation:" -ForegroundColor Red
  foreach ($f in $failed) {
    Write-Host "  ✗ $($f.Skill): $($f.Issues)" -ForegroundColor Red
  }
  Write-Host ""
  Write-Host "Fix hints:" -ForegroundColor Yellow
  Write-Host "  • DESC_TOO_LONG  → shrink description, move detail into the skill body or references/"
  Write-Host "  • YAML_PARSE_FAIL with 'mapping values not allowed' → an unquoted value contains ': ' (colon+space)."
  Write-Host "    Wrap that field's value in double quotes, OR remove the embedded colon."
  Write-Host "  • NAME_MISMATCH → frontmatter 'name:' must equal the parent folder name"
  exit 1
}

Write-Host ""
Write-Host "All $($results.Count) skills PASS." -ForegroundColor Green
exit 0
