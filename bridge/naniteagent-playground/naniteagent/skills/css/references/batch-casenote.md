---
description: Batch-add analysis notes (Note/Annotation) to D365 Case Timeline via OData API browser injection. No need to open each case manually. Self-contained — no external scripts required.
version: 2.0.0
---

# Batch Add Case Notes via OData API (Browser Injection)

**Primary Use**: Batch-add local analysis note files to D365 Case Timeline  
**URL**: `https://onesupport.crm.dynamics.com/`  
**Tool**: `playwright-browser_*` (navigate, evaluate, run_code, wait_for)  
**Trigger Words**: `添加 case note`, `add case note`, `batch note`, `批量 note`

> ⚠️ **CRITICAL**: NEVER pass note file content as inline text or Agent context.
> ALWAYS use the PowerShell file-read + Base64 approach below.
> Note files can be 20KB+ each — passing them through Agent context will cause
> "content too long" errors. PowerShell reads files directly and generates the
> injection script without any content passing through the Agent.

#### Prerequisites
- Playwright MCP connected
- D365 is open and authenticated in the browser
- Note files for each case are prepared (Markdown or plain text)

#### Tool Mapping Reference

| Action | Playwright Tool | Notes |
|--------|----------------|-------|
| Open D365 | `playwright-browser_navigate` url=... | SSO auto-login |
| Query incidentid | `playwright-browser_evaluate` function=... | OData FetchXML, uses existing auth cookie |
| Generate IIFE | `powershell` | Reads files, Base64 encodes, writes .js — **all in PowerShell, no external scripts** |
| Inject IIFE | `playwright-browser_run_code` code=... | `page.addScriptTag({ path })` bypasses CSP |
| Read results | `playwright-browser_evaluate` function=... | `window.__notesResult` |
| Wait | `playwright-browser_wait_for` time=N | API calls need 10-30s |

#### Workflow Steps

```
Step 1: Navigate → https://onesupport.crm.dynamics.com/
        → wait_for text="Dynamics 365" (SSO auto-login)

Step 2: evaluate → batch-query all case incidentids (FetchXML)

Step 3: PowerShell → read note files → Base64 encode → generate IIFE .js file
        (self-contained, no external Python script needed)

Step 4: evaluate → clear window.__notesResult (if rerunning)
        run_code → page.addScriptTag({ path: '.js' }) inject and execute
        → wait_for time=15 (depends on case count)
        → evaluate → read window.__notesResult for verification

Step 5: Clean up temporary .js file
```

#### Step 2: Batch Query incidentid

```javascript
// playwright-browser_evaluate function:
async () => {
  const caseIds = ['CASE_ID_1', 'CASE_ID_2', /* ... */];
  const results = {};
  for (const caseId of caseIds) {
    const fetchXml = `<fetch top="1"><entity name="incident">
      <attribute name="incidentid"/><attribute name="ticketnumber"/><attribute name="title"/>
      <filter><condition attribute="ticketnumber" operator="eq" value="${caseId}"/></filter>
    </entity></fetch>`;
    const resp = await fetch(`/api/data/v9.0/incidents?fetchXml=${encodeURIComponent(fetchXml)}`, {
      headers: { 'Accept': 'application/json', 'OData-MaxVersion': '4.0', 'OData-Version': '4.0' }
    });
    const data = await resp.json();
    if (data.value?.length > 0) {
      results[caseId] = { incidentid: data.value[0].incidentid, title: data.value[0].title };
    }
  }
  return results;
}
```

> **Key point**: `fetch` on the D365 page context automatically carries the auth cookie — no extra token needed.

#### Step 3: Generate IIFE JavaScript (PowerShell — self-contained)

> **No external Python script needed.** The PowerShell below reads note files,
> Base64-encodes them, and generates the complete IIFE .js file directly.

```powershell
# ── Input: $caseMap is a hashtable from Step 2 results ──
# Key = caseId (ticketnumber), Value = incidentid (GUID)
# $noteDir   = base directory containing case folders
# $notePattern = filename pattern, e.g. "{0}-InternalNote.md" where {0} = caseId
# $subject   = note title in D365 Timeline

# Example values (Agent should adapt to actual paths):
# $noteDir = "C:\work\cases"
# $notePattern = "{0}-InternalNote.md"
# $subject = "Investigation Notes"

$jsItems = @()
foreach ($caseId in $caseMap.Keys) {
    $noteFile = Join-Path $noteDir $caseId ($notePattern -f $caseId)
    if (-not (Test-Path $noteFile)) {
        Write-Host "WARNING: File not found: $noteFile, skipping $caseId"
        continue
    }
    $content = Get-Content $noteFile -Raw -Encoding UTF8
    $b64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($content))
    $incidentId = $caseMap[$caseId]
    $jsItems += "{c:'$caseId',i:'$incidentId',b:'$b64'}"
}

if ($jsItems.Count -eq 0) { Write-Error "No valid cases to process"; return }

$safeSubject = $subject -replace "\\", "\\\\" -replace "'", "\'"
$jsData = $jsItems -join ",`n"

$jsCode = @"
(async()=>{
const D=[$jsData];
const S='$safeSubject';
const R=[];
for(const x of D){
  try{
    const t=(typeof TextDecoder!=='undefined'?new TextDecoder('utf-8').decode(Uint8Array.from(atob(x.b),c=>c.charCodeAt(0))):decodeURIComponent(escape(atob(x.b))));
    const r=await fetch('/api/data/v9.0/annotations',{
      method:'POST',
      headers:{
        'Accept':'application/json',
        'Content-Type':'application/json',
        'OData-MaxVersion':'4.0',
        'OData-Version':'4.0'
      },
      body:JSON.stringify({
        subject:S,
        notetext:t,
        'objectid_incident@odata.bind':'/incidents('+x.i+')'
      })
    });
    R.push({c:x.c,s:r.ok||r.status===204?'OK':'FAIL',h:r.status});
  }catch(e){R.push({c:x.c,s:'ERR',e:e.message})}
}
window.__notesResult=R;
})();
"@

$outputJs = "$env:TEMP\d365-batch-notes-iife.js"
[System.IO.File]::WriteAllText($outputJs, $jsCode, [System.Text.Encoding]::UTF8)
$size = (Get-Item $outputJs).Length
Write-Host "Generated: $outputJs ($size bytes, $($jsItems.Count) cases)"
Write-Host "Subject: $subject"
```

**What this does** (Agent does NOT need to read/process file content):
1. Reads each note file from disk directly
2. Base64-encodes the full UTF-8 content
3. Embeds encoded data as JS string literals in an IIFE
4. Writes the complete .js file to `$env:TEMP`

The IIFE, when injected into the D365 page, will:
- Decode Base64 → UTF-8 text (uses `TextDecoder('utf-8')` with `decodeURIComponent(escape(atob()))` fallback)
- POST each note to `/api/data/v9.0/annotations`
- Store results in `window.__notesResult`

#### Step 4: Inject & Read Results

```javascript
// 4a. Clear previous results (if rerunning) — playwright-browser_evaluate:
() => { window.__notesResult = null; return 'cleared'; }
```

```javascript
// 4b. Inject — playwright-browser_run_code:
async (page) => {
  await page.addScriptTag({ path: 'C:/Users/.../AppData/Local/Temp/d365-batch-notes-iife.js' });
}
```

> ⚠️ `addScriptTag({ path })` reads a local file and injects it into the page, bypassing CSP restrictions on localhost fetch.
> Use forward slashes in the path for `addScriptTag`.

```javascript
// 4c. Wait 10-30s then read — playwright-browser_evaluate:
() => { return window.__notesResult; }
```

**Expected results**:
- `{ c: "CASE_ID", s: "OK", h: 204 }` — Success
- `{ c: "CASE_ID", s: "FAIL", h: 403 }` — API error
- `{ c: "CASE_ID", s: "ERR", e: "message" }` — JS exception

#### Step 5: Clean Up

```powershell
Remove-Item "$env:TEMP\d365-batch-notes-iife.js" -Force -ErrorAction SilentlyContinue
```

#### OData API Reference

```
POST /api/data/v9.0/annotations
{
  "subject": "Note Title",
  "notetext": "Note content (Markdown or plain text)",
  "objectid_incident@odata.bind": "/incidents({incidentid})"
}
→ Success: HTTP 204 No Content
```

#### Implementation Notes (Gotchas)

1. **Content must NEVER pass through Agent context**: Use PowerShell to read files and Base64-encode directly — note files can be 20KB+ each
2. **CSP restriction**: `fetch('http://localhost:...')` is blocked by D365 → use `page.addScriptTag({ path })` to inject local scripts
3. **Node.js API unavailable**: `require('fs')` / `import('fs')` not available in `playwright-browser_run_code` → PowerShell handles all file I/O
4. **Timeout**: `page.waitForFunction` default 5s is insufficient → use `wait_for time=15` after injection, then evaluate to read results
5. **CJK encoding**: `atob()` does not handle multi-byte UTF-8 → IIFE decodes bytes with `TextDecoder('utf-8')`
6. **TEMP path**: `process.env.TEMP` is unavailable in run_code sandbox → PowerShell resolves the path and Agent uses it in `addScriptTag`
7. **Write confirmation**: Must confirm the case list and note subject with the user before injection (safety rule)
8. **Rerunning**: Clear `window.__notesResult` before re-injection to avoid reading stale results

#### Checklist

```
□ 1. D365 is authenticated in the browser
□ 2. Note files for each case are prepared
□ 3. evaluate to query incidentids
□ 4. PowerShell reads files + Base64 encodes + generates IIFE .js (NO external scripts)
□ 5. Confirm write operation with user (case list + note subject)
□ 6. evaluate to clear window.__notesResult
□ 7. addScriptTag to inject and execute
□ 8. wait_for + evaluate to read window.__notesResult for verification
□ 9. Clean up temporary .js file
```
