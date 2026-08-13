# Shared DFM (OneSupport Dynamics 365) fact source

> **Single source of truth** for DFM OData entity names, endpoints, status codes,
> binding conventions, and known pitfalls. Any sw-skill that reads or writes DFM
> case data through the shared OData core links here instead of re-documenting the
> API in its own SKILL.md.

## What "DFM" means here

DFM is the **OneSupport Dynamics 365 CRM** that fronts CSS case management.

| Fact | Value |
|---|---|
| Host (page origin) | `https://onesupport.crm.dynamics.com` |
| App entry URL | `https://onesupport.crm.dynamics.com/main.aspx?appid=101acb62-8d00-eb11-a813-000d3a8b3117` |
| OData base | `https://onesupport.crm.dynamics.com/api/data/v9.0/` |
| Auth account | `microsoftsupport` (the `@microsoftsupport.com` support account — **NOT** the corp `@microsoft.com` account) |
| Auth mechanism | Cookie-based (browser auto-attaches the HttpOnly `CrmOwinAuth` cookie inside the logged-in page) |

The case Case (`incident`) entity is keyed by **`ticketnumber`** (the 16-digit DFM
case number you see in the UI) and **`incidentid`** (the GUID used in every OData
binding). Resolve one to the other with `Get-DfmIncidentId`.

## Canonical helper

All calls go through the shared core, not hand-rolled `fetch()`:

```
.github/skills/_shared/dfm_odata_helpers.ps1
  ├── Invoke-DfmApi          — call an OData endpoint (GET/POST/PATCH/DELETE), base64-marker result
  ├── Get-DfmIncidentId      — ticketnumber (16-digit case #) -> incidentid GUID, cached
  ├── ConvertTo-DfmNoteHtml  — plain text -> <p>/<br/> HTML (opt-in renderer)
  └── ConvertTo-JsString     — escape a string for a JS single-quoted literal
```

Dot-sourcing `dfm_odata_helpers.ps1` transitively loads `playwright_helpers.ps1`
(the session/auth layer: `New-PwSessionId`, `Open-DfmHome`, `Invoke-Pw`,
`Update-PwState`, `Get-DfmCaseStatement`). A skill's `scripts/load-helpers.ps1`
should source the core, never keep its own copy.

Minimal call pattern:

```powershell
. .github\skills\<skill>\scripts\load-helpers.ps1
$sid = New-PwSessionId 'dfm'
Open-DfmHome -SessionId $sid
$iid = Get-DfmIncidentId -SessionId $sid -CaseId '2605140030002786'
$r   = Invoke-DfmApi -SessionId $sid -Endpoint "/api/data/v9.0/incidents($iid)?`$select=title,ticketnumber"
if ($r._status -lt 400) { $r.title }
Stop-PwSession -SessionId $sid
```

## The reference docs

| Doc | Use it for |
|---|---|
| [`entity-model.md`](entity-model.md) | Entity relationships, `statuscode`/`statecode` value tables, OData `@odata.bind` naming conventions |
| [`api-reference.md`](api-reference.md) | Read/write endpoint catalog (Notes, Emails, Phone Calls, Labor, Customer Statement, ICM details, …) with `Invoke-DfmApi` examples |
| [`error-diagnosis.md`](error-diagnosis.md) | HTTP status → cause/fix map, the known-pitfall table (404/400/403), and auth recovery |
| [`write-safety.md`](write-safety.md) | The standing write-confirmation gate (show→confirm→execute), per-operation show-before-confirm table, the collab D7 carve-out, and the agent autonomy-boundary table |
| [`page-context.md`](page-context.md) | DFM page-state model (Dashboard / Case Form / Create Collaboration / Email editor) and which operations need which context |

## Consumers

Skills that touch DFM and should reference this fact source:

- **vm-case-triage** — reads case fields (status, contact, statement, Support Area Path) when triaging/routing.

## Provenance & maintenance

Facts harvested from the proven external `d365-case-ops` skill's `references/`
(entity-model, api-reference, technical-notes) and re-grounded against the
ChinaVMSkills session layer. When you discover a new DFM entity name, binding quirk,
or status code **in the field**, update the matching doc here — do **not** scatter
it into an individual skill's SKILL.md. One fact, one place.
