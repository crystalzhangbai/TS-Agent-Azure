# DFM OData error diagnosis

> Shared fact source — see [`README.md`](README.md). When an `Invoke-DfmApi` call
> returns a non-2xx `_status` (or `$null`), find the symptom here. Entity/binding
> facts: [`entity-model.md`](entity-model.md); endpoint catalog:
> [`api-reference.md`](api-reference.md).

## How `Invoke-DfmApi` reports failures

Every response object carries:

| Field | Meaning |
|---|---|
| `_status` | HTTP status. `0` = a JS/network exception inside the page (not an HTTP error). |
| `_error` | Error text (the OData error body, trimmed) when `_status >= 400` or `_status -eq 0`. |
| `_entityId` | `OData-EntityId` header — present on successful creates (201/204). |

`Invoke-DfmApi` returns **`$null`** only when it got **no result marker at all** —
that means the browser session is lost or not on a DFM page, *not* an API error.
Distinguish the two: `$null` → re-open the session; an object with `_status >= 400`
→ a real API problem from the table below.

## HTTP status → cause → fix

| Status | Likely cause | Fix |
|---|---|---|
| **`$null`** (no marker) | Session lost / not on a DFM page / `about:blank` | `Open-DfmHome -SessionId $sid` then retry. A page on `about:blank` returns 401 on the fetch — must be on `onesupport.crm.dynamics.com`. |
| **`0`** | JS/network exception in-page (e.g. CSP, fetch threw) | Read `_error`; usually transient — retry once. If it persists, re-open the session. |
| **`400`** | Malformed request — bad bind casing, wrong type, bad `@odata.bind` | Check the binding name/case (see pitfalls below). Most common: lowercase `msdfm_caseid@odata.bind` instead of PascalCase `msdfm_CaseId@odata.bind`; or a Picklist sent as string. |
| **`401`** | Page not authenticated / fetch ran on a non-DFM origin | Ensure `Open-DfmHome` succeeded and the page is on `onesupport.crm.dynamics.com`. If still 401, auth state is stale → see 403 row. |
| **`403`** | Auth cookie expired, or no permission on this case | `Update-PwState microsoftsupport` (re-login with the **@microsoftsupport.com** support account, NOT corp). If login is fine but still 403, you lack access to that case — request access in DFM. |
| **`404`** | Wrong entity set name, or restricted entity queried directly | `msdfm_caserestrictedattributes` and similar must be read via the **incident navigation property** (`/incidents(<id>)/msdfm_CaseRestrictedAttributesId`). Verify the entity-set spelling (`msdfm_labors`, not `msdfm_efforts`). |
| **`412` / `429`** | Concurrency precondition / throttling | Back off and retry once; for `429` honor `Retry-After` if present in `_error`. |
| **`500`** | Server-side OData error (often a downstream bad payload) | Inspect `_error` for the inner exception; frequently a malformed body the platform accepted syntactically but rejected semantically. |

## Known pitfalls (the ones that actually bite)

| Pitfall | Symptom | Fix |
|---|---|---|
| `msdfm_caserestrictedattributes` queried as a top-level set | **404** | Read via incident nav prop: `/incidents(<id>)/msdfm_CaseRestrictedAttributesId?$select=...`. See [`api-reference.md`](api-reference.md#customer-statement-restricted-attributes--nav-only). |
| `msdfm_CaseId@odata.bind` lowercased | **400** | The Labor bind is **PascalCase** SchemaName: `msdfm_CaseId@odata.bind`. |
| Using `msdfm_efforts` for Labor | **404** | The Labor entity set is **`msdfm_labors`**. `msdfm_efforts` is an unrelated entity. |
| Phone Call regarding bind missing the `_phonecall` suffix | **400** | Use `regardingobjectid_incident_phonecall@odata.bind`. |
| `msdfm_classification` sent as a string | **400** | It's a **Picklist** — pass the Int32 (e.g. `337818`), not `"Troubleshooting"`. |
| `msdfm_durationpicker` ≠ `msdfm_duration` | silently wrong duration | Set both to the same value. |
| `CloseIncident` while activities are Open | **400/500** | Close all Open Emails/Phone Calls first, then resolve. |
| Unescaped `$select`/`$filter` in a PS double-quoted endpoint | empty query option → wrong/all rows | Backtick-escape (`` `$select ``) or build the string single-quoted. |
| Note body corrupted (`$1`, `$&`, braces, code blocks) | garbled notetext | **Already fixed** by the shared core — bodies go in as base64 JSON, results come back via a base64 marker. Never go back to `-replace` placeholder injection or `'^[^{]*({.*})[^}]*$'` result regex. |

## Auth recovery (the 403/401 playbook)

DFM auth is cookie-based against the **`microsoftsupport`** account. When a call
returns 403 (or repeated 401 after a confirmed `Open-DfmHome`):

```powershell
. .github\skills\<skill>\scripts\load-helpers.ps1
Update-PwState microsoftsupport     # headed login with your @microsoftsupport.com support account
```

- The corp `@microsoft.com` account will **not** work for DFM — it routes to a
  different tenant (`Get-PwAccountForUrl` maps `onesupport.crm.dynamics.com` →
  `microsoftsupport`).
- After refreshing state, re-open the session (`Open-DfmHome`) and retry. The
  `Get-DfmIncidentId` cache survives, so the retry is cheap.

## Quick decision flow

```
Invoke-DfmApi result
│
├── $null ............... session lost → Open-DfmHome → retry
├── _status 0 .......... in-page JS/network exception → read _error → retry once
├── _status 401/403 .... auth stale → Update-PwState microsoftsupport → Open-DfmHome → retry
├── _status 404 ........ wrong entity set OR restricted entity → use nav prop / fix set name
├── _status 400 ........ bad bind casing / wrong type → check entity-model bindings
└── _status >=500 ...... read _error; if throttling (429) back off; else inspect inner error
```
