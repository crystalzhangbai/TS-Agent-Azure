# =============================================================================
# Playwright CLI helpers for ChinaVMSkills
# =============================================================================
# Shared helper functions for all skills that automate browser interactions via
# `playwright-cli`. Provides:
#   - URL-based account routing (corp vs microsoftsupport)
#   - One-line session opening with the right auth state pre-loaded
#   - State refresh workflow (headed login + state-save)
#
# Usage from a skill (PowerShell):
#     . "$PSScriptRoot\load-helpers.ps1"   # one-line dot-source from skill's scripts/
#     $sid = New-PwSessionId "graph"
#     Start-PwSession -SessionId $sid -Url $url
#     playwright-cli -s=$sid snapshot
#     playwright-cli -s=$sid close
#
# CANONICAL LOCATION: .github/skills/_shared/playwright_helpers.ps1
# Each skill's scripts/load-helpers.ps1 dot-sources this single canonical copy.
# Do NOT duplicate this file under any skill's scripts/ folder.
#
# When a tool migrates to the @microsoftsupport.com account, add a regex to
# $Script:AccountRoutes below.
# =============================================================================

# ---- Path resolution (auto-detect, no hardcoded workspace path) -------------
# Resolution order for the directory that holds .playwright-cli/ auth state:
#   1. $env:SW_PLAYWRIGHT_DIR (explicit override)
#   2. Walk up from $PSScriptRoot looking for a sibling .playwright-cli/
#   3. Fall back to $PSScriptRoot\.playwright-cli (created on first use)
function Resolve-PwCliDir {
    if ($env:SW_PLAYWRIGHT_DIR) { return $env:SW_PLAYWRIGHT_DIR }
    $dir = $PSScriptRoot
    for ($i = 0; $i -lt 6 -and $dir; $i++) {
        $candidate = Join-Path $dir '.playwright-cli'
        if (Test-Path $candidate) { return $candidate }
        $parent = Split-Path $dir -Parent
        if (-not $parent -or $parent -eq $dir) { break }
        $dir = $parent
    }
    return (Join-Path $PSScriptRoot '.playwright-cli')
}

$Script:PwCliDir       = Resolve-PwCliDir
$Script:CorpStatePath  = Join-Path $Script:PwCliDir "state-corp.json"
$Script:MsftSStatePath = Join-Path $Script:PwCliDir "state-microsoftsupport.json"
$Script:CorpProfileDir = Join-Path $Script:PwCliDir "profile-corp"
$Script:MsftSProfileDir = Join-Path $Script:PwCliDir "profile-microsoftsupport"

# URL routing table — order matters; first match wins.
# Add new patterns here when a tool migrates to the @microsoftsupport.com account.
$Script:AccountRoutes = @(
    @{ Pattern = 'onesupport\.crm\.dynamics\.com';   Account = 'microsoftsupport' },
    @{ Pattern = 'azuresupportcenter\.azure\.com';   Account = 'microsoftsupport' },
    @{ Pattern = 'aka\.ms/onesupport';               Account = 'microsoftsupport' }
    # Everything else defaults to 'corp'.
)

$Script:StateFiles = @{
    'corp'             = $Script:CorpStatePath
    'microsoftsupport' = $Script:MsftSStatePath
}

$Script:ProfileDirs = @{
    'corp'             = $Script:CorpProfileDir
    'microsoftsupport' = $Script:MsftSProfileDir
}

# Probe URLs used by Update-PwState to drive headed login per account.
$Script:LoginProbeUrls = @{
    'corp'             = 'https://asi.azure.ms/'
    'microsoftsupport' = 'https://onesupport.crm.dynamics.com/main.aspx?appid=101acb62-8d00-eb11-a813-000d3a8b3117'
}

function Get-PwAccountForUrl {
    <#
    .SYNOPSIS
    Return 'corp' or 'microsoftsupport' based on the URL.
    #>
    param([Parameter(Mandatory)][string]$Url)
    foreach ($r in $Script:AccountRoutes) {
        if ($Url -match $r.Pattern) { return $r.Account }
    }
    return 'corp'
}

function New-PwSessionId {
    <#
    .SYNOPSIS
    Generate a unique playwright-cli session id with the given prefix.
    Format: <prefix>-<HHmmssfff>  (e.g. "graph-104215123")
    #>
    param([string]$Prefix = 'pw')
    "{0}-{1}" -f $Prefix, (Get-Date -Format 'HHmmssfff')
}

function Invoke-PwCleanup {
    <#
    .SYNOPSIS
    Purge stale playwright-cli debug artifacts (console-*.log / page-*.yml).
    Throttled to run at most once per 24h unless -Force is passed.
    NEVER touches state-*.json or profile-* directories — only ephemeral debug output.

    .PARAMETER OlderThanDays
    Delete debug artifacts last modified more than N days ago. Default 7.

    .PARAMETER Force
    Ignore the 24h throttle and run cleanup immediately.

    .EXAMPLE
    Invoke-PwCleanup                          # opportunistic, no-op if ran in last 24h
    Invoke-PwCleanup -Force                   # force-run with default 7-day cutoff
    Invoke-PwCleanup -Force -OlderThanDays 1  # aggressive: keep only files <1d old
    #>
    param(
        [int]$OlderThanDays = 7,
        [switch]$Force
    )
    if (-not (Test-Path $Script:PwCliDir)) { return }
    $marker = Join-Path $Script:PwCliDir '.last-cleanup'
    if (-not $Force -and (Test-Path $marker)) {
        if (((Get-Date) - (Get-Item $marker).LastWriteTime).TotalHours -lt 24) { return }
    }
    $cutoff  = (Get-Date).AddDays(-$OlderThanDays)
    $deleted = 0
    foreach ($pattern in 'console-*.log','page-*.yml') {
        Get-ChildItem -Path $Script:PwCliDir -Filter $pattern -File -ErrorAction SilentlyContinue |
            Where-Object { $_.LastWriteTime -lt $cutoff } |
            ForEach-Object {
                try { Remove-Item -LiteralPath $_.FullName -Force -ErrorAction Stop; $deleted++ } catch {}
            }
    }
    Set-Content -LiteralPath $marker -Value (Get-Date -Format o) -Force -ErrorAction SilentlyContinue
    if ($deleted -gt 0) {
        Write-Verbose ("Invoke-PwCleanup: removed {0} debug artifact(s) older than {1}d from {2}" -f $deleted, $OlderThanDays, $Script:PwCliDir)
    }
}

function Start-PwSession {
    <#
    .SYNOPSIS
    Open a fresh in-memory playwright-cli msedge session, load the right auth
    state based on the URL, and navigate. Returns nothing.

    .PARAMETER SessionId
    Unique session id, e.g. from New-PwSessionId.

    .PARAMETER Url
    The first URL to navigate to. Used to pick the right auth state file.

    .PARAMETER NoState
    Skip loading any state (useful for public pages or when explicitly testing
    unauthenticated behavior).
    #>
    param(
        [Parameter(Mandatory)][string]$SessionId,
        [Parameter(Mandatory)][string]$Url,
        [switch]$NoState
    )
    # Opportunistic cleanup of old debug artifacts (throttled to 1/day, never fails the session)
    try { Invoke-PwCleanup } catch { }
    # Opportunistic profile cache compaction (throttled to 1/week, locked files skipped)
    try { Invoke-PwProfileCompact } catch { }

    $account = Get-PwAccountForUrl $Url
    $state   = $Script:StateFiles[$account]

    & playwright-cli "-s=$SessionId" open about:blank --browser msedge | Out-Null

    if (-not $NoState) {
        if (Test-Path $state) {
            & playwright-cli "-s=$SessionId" state-load $state | Out-Null
        } else {
            Write-Warning ("No state file at {0} (account={1}). Run: Update-PwState {1}" -f $state, $account)
        }
    }

    & playwright-cli "-s=$SessionId" goto $Url
}

function Stop-PwSession {
    <#
    .SYNOPSIS
    Close a playwright-cli session. Safe to call even if already closed.
    #>
    param([Parameter(Mandatory)][string]$SessionId)
    & playwright-cli "-s=$SessionId" close 2>$null | Out-Null
}

function Invoke-PwProfileCompact {
    <#
    .SYNOPSIS
    Shrink playwright-cli browser profiles by deleting cache subdirectories.
    Preserves ALL login state (Network/Cookies, Login Data, Web Data, Preferences,
    IndexedDB, Local Storage). Throttled to once per 7 days unless -Force.

    .PARAMETER Force
    Ignore the 7-day throttle and run compaction immediately.

    .EXAMPLE
    Invoke-PwProfileCompact           # opportunistic, no-op if ran in last 7d
    Invoke-PwProfileCompact -Force    # force-run now; reports MB freed
    #>
    param([switch]$Force)
    if (-not (Test-Path $Script:PwCliDir)) { return }
    $marker = Join-Path $Script:PwCliDir '.last-compact'
    if (-not $Force -and (Test-Path $marker)) {
        if (((Get-Date) - (Get-Item $marker).LastWriteTime).TotalDays -lt 7) { return }
    }

    # Cache subdirs under <profile>/Default/ — safe to delete, Edge rebuilds them.
    $defaultCacheDirs = @(
        'Cache', 'Service Worker', 'Code Cache',
        'GPUCache', 'ShaderCache', 'GrShaderCache',
        'DawnWebGPUCache', 'DawnGraphiteCache', 'GraphiteDawnCache'
    )
    # Cache subdirs at <profile>/ root (Edge writes these here too).
    $rootCacheDirs = @(
        'BrowserMetrics', 'GrShaderCache', 'ShaderCache',
        'GraphiteDawnCache', 'component_crx_cache', 'extensions_crx_cache', 'Crashpad'
    )

    $freedBytes = 0L
    Get-ChildItem -Path $Script:PwCliDir -Directory -Filter 'profile-*' -ErrorAction SilentlyContinue | ForEach-Object {
        $profileDir = $_.FullName
        $targets = @()
        $targets += ($defaultCacheDirs | ForEach-Object { Join-Path $profileDir "Default\$_" })
        $targets += ($rootCacheDirs    | ForEach-Object { Join-Path $profileDir $_ })
        foreach ($t in $targets) {
            if (Test-Path $t) {
                $sz = (Get-ChildItem $t -Recurse -File -Force -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum
                try {
                    Remove-Item -LiteralPath $t -Recurse -Force -ErrorAction Stop
                    $freedBytes += [long]$sz
                } catch {
                    Write-Verbose ("Invoke-PwProfileCompact: skipped (locked?) {0}: {1}" -f $t, $_.Exception.Message)
                }
            }
        }
    }

    Set-Content -LiteralPath $marker -Value (Get-Date -Format o) -Force -ErrorAction SilentlyContinue
    if ($freedBytes -gt 0) {
        Write-Verbose ("Invoke-PwProfileCompact: freed {0} MB of profile cache" -f [math]::Round($freedBytes/1MB,1))
    }
}

function Invoke-Pw {
    <#
    .SYNOPSIS
    Run a playwright-cli command against a named session. Recommended over
    bare `playwright-cli -s=$sid ...` because PowerShell can mis-parse the
    `-s=$sid` token when the call line contains complex JS expressions.

    .EXAMPLE
    Invoke-Pw $sid snapshot
    Invoke-Pw $sid goto https://asi.azure.ms/
    Invoke-Pw $sid press PageDown
    Invoke-Pw $sid eval "() => location.href"
    #>
    param(
        [Parameter(Mandatory, Position=0)][string]$SessionId,
        [Parameter(ValueFromRemainingArguments=$true)][string[]]$Args
    )
    & playwright-cli "-s=$SessionId" @Args
}

function Test-PwAuthenticated {
    <#
    .SYNOPSIS
    Check if the current page in a session looks authenticated (no MS login
    form visible). Returns $true / $false.
    #>
    param([Parameter(Mandatory)][string]$SessionId)
    $expr = "() => !document.querySelector('input[name=loginfmt]') && !location.href.includes('login.microsoftonline.com')"
    $result = & playwright-cli "-s=$SessionId" --raw eval $expr 2>$null
    return ($result -match 'true')
}

function Update-PwState {
    <#
    .SYNOPSIS
    Refresh the auth state for an account by opening a headed msedge with a
    persistent profile, prompting the user to log in, then saving state.

    .PARAMETER Account
    Either 'corp' or 'microsoftsupport'.

    .EXAMPLE
    . "$PSScriptRoot\..\..\_shared\playwright_helpers.ps1"   # or: . "$PSScriptRoot\load-helpers.ps1" from a skill
    Update-PwState corp
    # ... log in in the popup window, then press Enter in the terminal ...
    #>
    param(
        [Parameter(Mandatory)]
        [ValidateSet('corp','microsoftsupport')]
        [string]$Account
    )
    $profileDir = $Script:ProfileDirs[$Account]
    $statePath  = $Script:StateFiles[$Account]
    $probeUrl   = $Script:LoginProbeUrls[$Account]
    $sid        = "refresh-$Account-$(Get-Date -Format 'HHmmss')"

    New-Item -ItemType Directory -Force -Path $profileDir | Out-Null

    Write-Host "Opening headed msedge for account '$Account'..." -ForegroundColor Cyan
    Write-Host "Profile dir: $profileDir" -ForegroundColor DarkGray
    Write-Host "Probe URL  : $probeUrl"   -ForegroundColor DarkGray

    playwright-cli -s=$sid open $probeUrl `
        --browser msedge --headed --persistent --profile $profileDir | Out-Null

    if ($Account -eq 'microsoftsupport') {
        Write-Host ""
        Write-Host "Please log in with your OneSupport account (<your-alias>@microsoftsupport.com)" -ForegroundColor Yellow
        Write-Host "NOT the corp @microsoft.com account!" -ForegroundColor Yellow
    } else {
        Write-Host ""
        Write-Host "Please log in with your corp account (@microsoft.com)" -ForegroundColor Yellow
    }
    Read-Host "Press Enter when login is complete and the target page has loaded"

    playwright-cli -s=$sid state-save $statePath | Out-Null
    playwright-cli -s=$sid close | Out-Null

    if (Test-Path $statePath) {
        $size = (Get-Item $statePath).Length
        Write-Host "[OK] Saved $Account state -> $statePath ($size bytes)" -ForegroundColor Green
    } else {
        Write-Error "Failed to save state to $statePath"
    }
}

function Get-PwSessions {
    <#
    .SYNOPSIS
    Wrapper around `playwright-cli list` for visibility.
    #>
    playwright-cli list
}

function Open-DfmHome {
    <#
    .SYNOPSIS
    Open the DFM (OneSupport Dynamics) home page in a playwright-cli session.
    Idempotent: if the session already exists and is already on any DFM page
    (home OR case detail), this returns immediately — no re-navigate, no
    wait. On a fresh session, it auto-loads auth state, navigates, and waits
    for the Dynamics shell to be ready by polling the DOM (NOT
    `waitForLoadState('networkidle')` — Dynamics never reaches networkidle).

    Auth state is auto-loaded based on the URL (microsoftsupport account).

    .EXAMPLE
    $sid = New-PwSessionId 'dfm'
    Open-DfmHome -SessionId $sid
    Get-DfmCaseStatement -SessionId $sid -CaseId '2605130030001386'
    #>
    param([Parameter(Mandatory)][string]$SessionId)
    $dfmUrl = 'https://onesupport.crm.dynamics.com/main.aspx?appid=101acb62-8d00-eb11-a813-000d3a8b3117'

    # Idempotency check: if session is already on any DFM page, do nothing.
    $currentUrl = & playwright-cli "-s=$SessionId" --raw eval "() => location.href" 2>$null
    $currentUrl = ($currentUrl -join "`n").Trim()
    if ($currentUrl -and ($currentUrl -match 'onesupport\.crm\.dynamics\.com')) {
        Write-Verbose "Session $SessionId already on DFM ($currentUrl) - skipping."
        return
    }

    # Fresh session — open + state-load + navigate.
    Start-PwSession -SessionId $SessionId -Url $dfmUrl | Out-Null

    # Poll for the Dynamics shell to be ready. We accept any of:
    #   - global search box, OR
    #   - the navigation site map, OR
    #   - body innerText containing "Dynamics 365" / "Active Cases".
    # 30s upper bound, then proceed regardless (caller will detect issues).
    $readyJs = @"
async page => {
  const T = 30000;
  const ok = await page.waitForFunction(() => {
    if (document.querySelector('input#GlobalSearchBox')) return true;
    if (document.querySelector('input[role="searchbox"][placeholder*="Search" i]')) return true;
    if (document.querySelector('[data-id="navbar-container"]')) return true;
    const t = document.body && document.body.innerText || '';
    return /Dynamics 365/i.test(t) && /Active Cases|Copilot Service|Cases/i.test(t);
  }, { timeout: T, polling: 500 }).catch(() => false);
  return { ready: !!ok };
}
"@
    $tmpReady = New-TemporaryFile
    try {
        Set-Content -Path $tmpReady -Value $readyJs -Encoding UTF8
        & playwright-cli "-s=$SessionId" run-code --filename $tmpReady.FullName 2>$null | Out-Null
    } finally {
        Remove-Item $tmpReady -ErrorAction SilentlyContinue
    }

    # Dismiss any overlay (Copilot intro, sub menu).
    & playwright-cli "-s=$SessionId" press Escape 2>$null | Out-Null
}

function Get-DfmCaseStatement {
    <#
    .SYNOPSIS
    Open a DFM case by its 16-digit case id and return parsed fields as a
    PowerShell hashtable. Encapsulates the entire navigate -> search -> open ->
    extract flow in one round-trip, so calling agents don't have to do the
    snapshot/find-ref/click loop that caused minutes-long stalls.

    .DESCRIPTION
    Returns @{
        CaseId            = '...'    # As shown on the page
        CustomerStatement = '...'    # The Restricted Information body
        StatusReason      = '...'    # e.g. "Troubleshooting"
        PrimaryContact    = '...'    # Customer contact name
        AssignedTo        = '...'    # Case owner / engineer
        ServiceName       = '...'    # e.g. "Unified Suppt | Enterprise Base"
        Severity          = '...'    # e.g. "C"
        Url               = '...'    # Current URL for reference
        Ok                = $true/$false
        Error             = $null or string
    }

    The session must already be authenticated and on a DFM page — call
    Open-DfmHome first.

    .EXAMPLE
    $sid = New-PwSessionId 'dfm'
    Open-DfmHome -SessionId $sid
    $data = Get-DfmCaseStatement -SessionId $sid -CaseId '2605130030001386'
    if ($data.Ok) { Write-Host $data.CustomerStatement }
    #>
    param(
        [Parameter(Mandatory)][string]$SessionId,
        [Parameter(Mandatory)][ValidatePattern('^\d{16}$')][string]$CaseId,
        [int]$TimeoutMs = 60000
    )

    # All work happens in a single run-code call. The callback is invoked in
    # Node.js context with `page` — to touch `document` / `location` we must
    # use `page.evaluate(() => { ... })`. Single round-trip; minimal output.
    $js = @"
async page => {
  const caseId = '$CaseId';
  const T = $TimeoutMs;

  const isOnThisCase = async () => page.evaluate(id => {
    const t = (document.body && document.body.innerText) || '';
    return t.includes(id) && /severity/i.test(t) && /assigned to/i.test(t);
  }, caseId);

  try {
    if (!(await isOnThisCase())) {
      // 1) Find the global search box.
      const searchBox = await page.waitForSelector(
        'input#GlobalSearchBox, input[role="searchbox"][placeholder*="Search" i]',
        { timeout: T }
      ).catch(() => null);
      if (!searchBox) {
        return { Ok: false, Error: 'Search box not found', Url: page.url() };
      }
      await searchBox.fill('');
      await searchBox.type(caseId, { delay: 20 });
      await searchBox.press('Enter');

      // 2) Wait for the AG Grid result row and click the title button.
      //    Cases rows expose a clickable customer-title button at
      //    [col-id="title"] button. Notes rows lack col-id="title", so this
      //    filter naturally selects the Cases table.
      const titleBtn = page.locator('.ag-row')
        .filter({ hasText: caseId })
        .locator('[col-id="title"] button')
        .first();
      try {
        await titleBtn.waitFor({ state: 'visible', timeout: T });
      } catch (e) {
        return { Ok: false, Error: 'Search result not found (no Cases row matched)', Url: page.url() };
      }
      await titleBtn.click();

      // 3) Wait for case detail to swap in (Severity + Assigned To appear).
      await page.waitForFunction(id => {
        const t = (document.body && document.body.innerText) || '';
        return t.includes(id) && /severity/i.test(t) && /assigned to/i.test(t);
      }, caseId, { timeout: T }).catch(() => {});
      await page.waitForTimeout(1500);
    }

    // 4) Restricted information section is virtualized + collapsed by default
    //    on the Summary tab. Scroll it into view and click the per-section
    //    "Click to expand this section" button if present. This is critical —
    //    Customer Statement textarea is not in the DOM until expanded.
    const ensureExpanded = async () => {
      const sec = page.locator('[data-id="CSC_Restricted_information_section"]').first();
      try { await sec.waitFor({ state: 'attached', timeout: 15000 }); } catch (e) { return false; }
      try { await sec.scrollIntoViewIfNeeded({ timeout: 5000 }); } catch (e) {}
      await page.waitForTimeout(500);
      const expandBtn = sec.locator('button[aria-label="Click to expand this section"]').first();
      if (await expandBtn.count() > 0) {
        try { await expandBtn.click({ timeout: 5000 }); } catch (e) {}
        await page.waitForTimeout(2000);
      }
      return true;
    };

    await ensureExpanded();

    // 5) Wait specifically for the Customer Statement textarea to materialize.
    let csReady = await page.waitForFunction(() => {
      return [...document.querySelectorAll('textarea')]
        .some(t => /customer statement/i.test(t.getAttribute('aria-label') || ''));
    }, { timeout: 20000 }).then(() => true).catch(() => false);

    // 5b) Retry once: re-expand and wait again if the textarea didn't appear.
    if (!csReady) {
      await ensureExpanded();
      csReady = await page.waitForFunction(() => {
        return [...document.querySelectorAll('textarea')]
          .some(t => /customer statement/i.test(t.getAttribute('aria-label') || ''));
      }, { timeout: 20000 }).then(() => true).catch(() => false);
    }

    // 6) Extract everything in one evaluate() call.
    const data = await page.evaluate(id => {
      const result = { Ok: false, Error: null, CaseId: id, CustomerStatement: null,
                       StatusReason: null, PrimaryContact: null, AssignedTo: null,
                       ServiceName: null, Severity: null, Url: location.href };

      // Customer Statement — find textarea by aria-label.
      const csTa = [...document.querySelectorAll('textarea')]
        .find(t => /customer statement/i.test(t.getAttribute('aria-label') || ''));
      if (csTa) {
        result.CustomerStatement = (csTa.value || csTa.innerText || '').trim() || null;
      }

      // Fallback: read the section's innerText after the "Customer Statement" label.
      if (!result.CustomerStatement) {
        const sec = document.querySelector('[data-id="CSC_Restricted_information_section"]');
        if (sec) {
          const txt = sec.innerText || '';
          const m = txt.match(/Customer Statement\s*\*?\s*([\s\S]+)/i);
          if (m) result.CustomerStatement = m[1].trim() || null;
        }
      }

      // Header fields: Dynamics 365 case header renders as value-on-top,
      // label-below pairs in the form-header element. Parse by line.
      //   <Title> - Saved
      //   Case
      //   <caseId> | <ServiceName>
      //   Case number / Service name
      //   <Severity>
      //   Severity
      //   <StatusReason>
      //   Status reason
      //   <AssignedTo>
      //   Assigned To
      const headerEl = document.querySelector('[data-id="form-header"]');
      if (headerEl) {
        const lines = (headerEl.innerText || '').split('\n')
          .map(l => l.trim()).filter(Boolean);
        const valueBefore = labelRe => {
          for (let i = 1; i < lines.length; i++) {
            if (labelRe.test(lines[i])) {
              const v = lines[i - 1];
              if (v && !labelRe.test(v)) return v;
            }
          }
          return null;
        };
        result.Severity      = valueBefore(/^severity$/i);
        result.StatusReason  = valueBefore(/^status reason$/i);
        result.AssignedTo    = valueBefore(/^assigned to$/i);
        result.PrimaryContact = valueBefore(/^primary contact$/i);
        const csvLine = valueBefore(/^case number\s*\/\s*service name$/i);
        if (csvLine) {
          const m = csvLine.match(/^(\d+)\s*\|\s*(.+)$/);
          if (m) {
            result.CaseId = m[1];
            result.ServiceName = m[2].trim();
          } else {
            result.ServiceName = csvLine;
          }
        }
      }

      // Fallback: also try Customer/Primary contact from form body if header missed.
      if (!result.PrimaryContact) {
        const contactEl = document.querySelector('[data-id*="primarycontactid"] a, [data-id*="primarycontactid"] .ms-Link');
        if (contactEl) {
          const v = (contactEl.innerText || '').trim();
          if (v && v.length < 100) result.PrimaryContact = v;
        }
      }

      result.Ok = !!result.CustomerStatement;
      if (!result.Ok) {
        result.Error = 'Customer Statement not found (section may be inaccessible or empty)';
      }
      return result;
    }, caseId);

    return data;
  } catch (e) {
    return { Ok: false, Error: String((e && e.message) || e), Url: page.url() };
  }
}
"@

    $tmp = New-TemporaryFile
    try {
        Set-Content -Path $tmp -Value $js -Encoding UTF8
        $raw = & playwright-cli "-s=$SessionId" --raw run-code --filename $tmp.FullName 2>&1
        $joined = ($raw -join "`n").Trim()
        if (-not $joined) { return @{ Ok = $false; Error = 'No output from playwright-cli' } }
        try {
            $obj = $joined | ConvertFrom-Json -ErrorAction Stop
        } catch {
            if ($joined -match '(?s)\{[^{}]*"Ok"[^{}]*\}|\{.*\}') {
                $obj = $Matches[0] | ConvertFrom-Json -ErrorAction Stop
            } else {
                return @{ Ok = $false; Error = "JSON parse failed: $joined" }
            }
        }
        $h = @{}
        foreach ($p in $obj.PSObject.Properties) { $h[$p.Name] = $p.Value }
        return $h
    } finally {
        Remove-Item $tmp -ErrorAction SilentlyContinue
    }
}
