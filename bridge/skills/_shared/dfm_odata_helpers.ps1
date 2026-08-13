# =============================================================================
# Shared DFM (OneSupport Dynamics 365) OData helpers for ChinaVMSkills
# =============================================================================
# A robust OData calling layer for skills that read/write DFM case data through
# an authenticated playwright-cli browser session (cookies auto-attach, incl. the
# HttpOnly CrmOwinAuth cookie). Built on top of the session/auth layer in
# playwright_helpers.ps1 (dot-sourced below).
#
# Why this exists (Phase 1 of the d365 borrow plan):
#   Before this, every DFM-touching skill reinvented OData plumbing and parsed
#   results with FRAGILE regex (e.g. '^[^{]*({.*})[^}]*$'), which
#   breaks whenever the note/result payload contains braces, code blocks, tables,
#   or regex-replacement metacharacters ($1, $&). This module fixes both ends:
#     - INPUT  : method/url/body are passed into the page as a single base64
#                JSON blob (NO -replace placeholder substitution, NO JS escaping).
#     - OUTPUT : the result returns as a base64 marker __DFMAPI__<b64>__END__,
#                decoded + ConvertFrom-Json on the PowerShell side (NO greedy
#                brace regex).
#
# Functions:
#   Invoke-DfmApi          - call a DFM OData endpoint (GET/POST/PATCH/DELETE)
#   Get-DfmIncidentId      - ticketnumber (16-digit case #) -> incidentid GUID, cached
#   ConvertTo-DfmNoteHtml  - plain text -> simple <p>/<br/> HTML (opt-in renderer)
#   ConvertTo-JsString     - escape a string for a JS single-quoted literal
#
# CANONICAL LOCATION: .github/skills/_shared/dfm_odata_helpers.ps1
# Each DFM skill's scripts/load-helpers.ps1 dot-sources this single canonical copy.
# Dot-sourcing this file transitively loads playwright_helpers.ps1 (session/auth).
# =============================================================================

# ---- Bring in the session/auth layer (New-PwSessionId, Open-DfmHome, etc.) --
. (Join-Path $PSScriptRoot 'playwright_helpers.ps1')

# ---- Default DFM incidentId cache location (ticketnumber -> incidentid map) --
$Script:DfmCachePath = Join-Path $env:TEMP 'dfm-case-context.json'

function ConvertTo-JsString {
    <#
    .SYNOPSIS
    Escape a string so it can be embedded safely inside a JS single-quoted literal.

    .DESCRIPTION
    Handles backslash, single/double quotes, and CR/LF. Useful when building inline
    JS by hand. NOTE: Invoke-DfmApi does NOT use this — it passes data as a base64
    JSON blob instead, which is strictly safer. Kept as a general utility.
    #>
    param([Parameter(Mandatory)][AllowEmptyString()][string]$Text)
    $t = $Text
    $t = $t -replace '\\', '\\'
    $t = $t.Replace("'", "\'")
    $t = $t.Replace('"', '\"')
    $t = $t -replace "`r`n", '\n'
    $t = $t -replace "`n", '\n'
    $t = $t -replace "`r", '\n'
    return $t
}

function ConvertTo-DfmNoteHtml {
    <#
    .SYNOPSIS
    Convert plain text to simple HTML paragraphs so a DFM Timeline note renders
    cleanly instead of showing literal markdown '#' / '|' characters.

    .DESCRIPTION
    Each line becomes a <p>; blank lines become <p>&nbsp;</p>. HTML-special chars
    are escaped. This is an OPT-IN renderer — callers decide whether to send HTML
    or plain text as the annotation notetext. Posting behavior is NOT changed by
    default anywhere; a skill must explicitly pipe its body through this function.

    .PARAMETER Text
    The plain-text note body.

    .PARAMETER NoTrailingBlank
    Do not append a trailing blank paragraph.
    #>
    param(
        [Parameter(Mandatory)][AllowEmptyString()][string]$Text,
        [switch]$NoTrailingBlank
    )
    $lines = $Text -split "`r?`n"
    $parts = foreach ($line in $lines) {
        $escaped = $line.Replace('&', '&amp;').Replace('<', '&lt;').Replace('>', '&gt;').Replace('"', '&quot;')
        if ([string]::IsNullOrWhiteSpace($escaped)) {
            '<p>&nbsp;</p>'
        } else {
            "<p>$escaped</p>"
        }
    }
    $html = ($parts -join '')
    if (-not $NoTrailingBlank) { $html += '<p>&nbsp;</p>' }
    return $html
}

function Invoke-DfmApi {
    <#
    .SYNOPSIS
    Call a DFM (OneSupport Dynamics 365) OData endpoint from inside an authenticated
    playwright-cli session and return the parsed result as a PSObject.

    .DESCRIPTION
    Runs `fetch()` inside the logged-in DFM page (cookies auto-attach, including the
    HttpOnly CrmOwinAuth cookie). The method/url/body are passed into the page as a
    single base64-encoded JSON blob (no escaping pitfalls), and the result is returned
    via a base64 marker (__DFMAPI__<b64>__END__) that is decoded on the PowerShell
    side — eliminating the fragile JSON regex the old scripts used.

    The returned object always carries:
        _status   - HTTP status (0 on a JS/network exception)
        _entityId - OData-EntityId response header (for 201/204 create results), or ''
        _error    - error text when _status >= 400 or _status -eq 0 (absent on success)
    Plus the parsed JSON body fields (e.g. .value for collection queries).

    Returns $null only when no result marker could be obtained at all (session lost).

    .PARAMETER SessionId
    An existing playwright-cli session already on a DFM page (use Open-DfmHome first).

    .PARAMETER Endpoint
    OData path, relative (e.g. "/api/data/v9.0/annotations") or absolute. Relative
    paths resolve against the page origin (onesupport.crm.dynamics.com).

    .PARAMETER Method
    GET (default), POST, PATCH, or DELETE.

    .PARAMETER Body
    JSON string for POST/PATCH. Build it with ConvertTo-Json — all escaping is handled.

    .PARAMETER TimeoutMs
    Reserved for future use; fetch itself is not externally timed here.

    .EXAMPLE
    $sid = New-PwSessionId 'dfm'; Open-DfmHome -SessionId $sid
    $r = Invoke-DfmApi -SessionId $sid -Endpoint "/api/data/v9.0/incidents?`$top=1&`$select=ticketnumber"
    $r.value[0].ticketnumber

    .EXAMPLE
    $body = @{ subject='x'; notetext='y'; 'objectid_incident@odata.bind'="/incidents($id)" } | ConvertTo-Json
    $r = Invoke-DfmApi -SessionId $sid -Method POST -Endpoint "/api/data/v9.0/annotations" -Body $body
    if ($r._status -lt 400) { $r._entityId }
    #>
    param(
        [Parameter(Mandatory)][string]$SessionId,
        [Parameter(Mandatory)][string]$Endpoint,
        [ValidateSet('GET','POST','PATCH','DELETE')][string]$Method = 'GET',
        [string]$Body = '',
        [int]$TimeoutMs = 60000
    )

    # Build the args blob. ConvertTo-Json handles ALL escaping of body/url.
    $argsObj = [ordered]@{
        method = $Method.ToUpper()
        url    = $Endpoint
        body   = $Body
    }
    $argsJson = $argsObj | ConvertTo-Json -Compress -Depth 30
    $argsB64  = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($argsJson))

    # JS template. %%ARGS_B64%% is replaced with a LITERAL .Replace (base64 is safe
    # and .Replace avoids regex-metacharacter pitfalls of -replace).
    $jsTemplate = @'
async page => {
  const __ARGS_B64__ = '%%ARGS_B64%%';
  const out = await page.evaluate(async (b64) => {
    const dec = (s) => decodeURIComponent(escape(atob(s)));
    const enc = (s) => btoa(unescape(encodeURIComponent(s)));
    const marker = (obj) => '__DFMAPI__' + enc(JSON.stringify(obj)) + '__END__';
    try {
      const args = JSON.parse(dec(b64));
      const url = (args.url.indexOf('http') === 0) ? args.url : (location.origin + args.url);
      const headers = {
        'Accept': 'application/json',
        'OData-MaxVersion': '4.0',
        'OData-Version': '4.0'
      };
      const opts = { method: args.method, headers: headers, credentials: 'include' };
      if (args.method !== 'GET' && args.method !== 'DELETE' && args.body) {
        headers['Content-Type'] = 'application/json';
        opts.body = args.body;
      }
      const resp = await fetch(url, opts);
      const status = resp.status;
      const entityId = (resp.headers && resp.headers.get) ? (resp.headers.get('OData-EntityId') || '') : '';
      if (status === 204) return marker({ _status: status, _entityId: entityId });
      if (status >= 400) {
        const errText = await resp.text().catch(() => '');
        return marker({ _status: status, _entityId: entityId, _error: errText.substring(0, 1500) });
      }
      const ct = (resp.headers.get('Content-Type') || '');
      let data;
      if (ct.indexOf('application/json') >= 0) {
        data = await resp.json();
      } else {
        data = { _raw: (await resp.text()).substring(0, 4000) };
      }
      if (data === null || typeof data !== 'object') { data = { _value: data }; }
      data._status = status;
      data._entityId = entityId;
      return marker(data);
    } catch (e) {
      return marker({ _status: 0, _error: (e && e.message) ? e.message : String(e) });
    }
  }, __ARGS_B64__);
  return out;
}
'@
    $js = $jsTemplate.Replace('%%ARGS_B64%%', $argsB64)

    $tmp = New-TemporaryFile
    try {
        Set-Content -Path $tmp -Value $js -Encoding UTF8
        $raw    = & playwright-cli "-s=$SessionId" --raw run-code --filename $tmp.FullName 2>&1
        $joined = ($raw -join "`n")

        if ($joined -match '__DFMAPI__([A-Za-z0-9+/=]+)__END__') {
            $b64 = $Matches[1]
            try {
                $json = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($b64))
                return ($json | ConvertFrom-Json)
            } catch {
                Write-Warning "[dfm-odata] Result marker decode/parse failed: $($_.Exception.Message)"
                return $null
            }
        }

        $snippet = if ($joined.Length -gt 300) { $joined.Substring(0, 300) } else { $joined }
        Write-Warning "[dfm-odata] No __DFMAPI__ result marker. Session may be lost or not on a DFM page. Raw: $snippet"
        return $null
    } finally {
        Remove-Item -LiteralPath $tmp -ErrorAction SilentlyContinue
    }
}

function Get-DfmIncidentId {
    <#
    .SYNOPSIS
    Resolve a 16-digit DFM case number (ticketnumber) to its incidentid GUID,
    with a small on-disk cache to skip repeat lookups.

    .DESCRIPTION
    Cache is a JSON map { "<ticketnumber>": "<incidentid>" } at
    $env:TEMP\dfm-case-context.json. On a cache miss it queries the incidents
    entity via Invoke-DfmApi, stores the result, and returns the GUID.
    Returns $null if the case is not found or the lookup fails (e.g. HTTP 403).

    .PARAMETER SessionId
    An authenticated DFM playwright-cli session (Open-DfmHome first).

    .PARAMETER CaseId
    The 16-digit case number, e.g. 2605140030002786.

    .PARAMETER NoCache
    Bypass the cache for both read and write (always do a fresh lookup).

    .EXAMPLE
    $sid = New-PwSessionId 'dfm'; Open-DfmHome -SessionId $sid
    $iid = Get-DfmIncidentId -SessionId $sid -CaseId '2605140030002786'
    #>
    param(
        [Parameter(Mandatory)][string]$SessionId,
        [Parameter(Mandatory)][string]$CaseId,
        [switch]$NoCache
    )

    # ---- Cache read ----
    if (-not $NoCache -and (Test-Path $Script:DfmCachePath)) {
        try {
            $cache = Get-Content -LiteralPath $Script:DfmCachePath -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($cache -and ($cache.PSObject.Properties.Name -contains $CaseId)) {
                $cached = $cache.$CaseId
                if ($cached) { return $cached }
            }
        } catch { }  # corrupt cache -> ignore, re-query
    }

    # ---- Query ----
    $endpoint = "/api/data/v9.0/incidents?`$select=incidentid,ticketnumber&`$filter=ticketnumber eq '$CaseId'"
    $resp = Invoke-DfmApi -SessionId $SessionId -Endpoint $endpoint
    if (-not $resp) { return $null }
    if (($resp.PSObject.Properties.Name -contains '_status') -and ($resp._status -ge 400 -or $resp._status -eq 0)) {
        $hint = if ($resp._status -eq 403) { ' (auth expired — run: Update-PwState microsoftsupport)' } else { '' }
        Write-Warning "[dfm-odata] incidentId lookup failed for $CaseId — HTTP $($resp._status)$hint"
        return $null
    }
    if (-not $resp.value -or $resp.value.Count -eq 0) {
        Write-Warning "[dfm-odata] Case $CaseId not found in DFM."
        return $null
    }
    $incidentId = $resp.value[0].incidentid

    # ---- Cache write ----
    if (-not $NoCache -and $incidentId) {
        try {
            $map = @{}
            if (Test-Path $Script:DfmCachePath) {
                $existing = Get-Content -LiteralPath $Script:DfmCachePath -Raw -Encoding UTF8 | ConvertFrom-Json
                if ($existing) {
                    foreach ($p in $existing.PSObject.Properties) { $map[$p.Name] = $p.Value }
                }
            }
            $map[$CaseId] = $incidentId
            ($map | ConvertTo-Json -Compress) | Set-Content -LiteralPath $Script:DfmCachePath -Encoding UTF8
        } catch { }  # cache write is best-effort
    }

    return $incidentId
}
