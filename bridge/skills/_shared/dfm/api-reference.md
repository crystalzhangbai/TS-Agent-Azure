# DFM (OneSupport Dynamics 365) OData API reference

> Shared fact source — see [`README.md`](README.md). Entity names, bindings, and
> status values are in [`entity-model.md`](entity-model.md); failure modes are in
> [`error-diagnosis.md`](error-diagnosis.md). This file is the endpoint catalog,
> written for the shared `Invoke-DfmApi` helper.

## Calling convention

Every call runs inside the authenticated DFM page, so cookies auto-attach. Use the
shared core — never hand-roll `fetch()`:

```powershell
. .github\skills\<skill>\scripts\load-helpers.ps1
$sid = New-PwSessionId 'dfm'; Open-DfmHome -SessionId $sid
$iid = Get-DfmIncidentId -SessionId $sid -CaseId '<16-digit case #>'   # ticketnumber -> GUID (cached)
$r   = Invoke-DfmApi -SessionId $sid -Endpoint '<relative OData path>' [-Method GET|POST|PATCH|DELETE] [-Body '<json>']
```

- **Endpoints are relative** (`/api/data/v9.0/...`); they resolve against the page
  origin `https://onesupport.crm.dynamics.com`.
- The returned object always carries `_status` (HTTP), `_entityId` (the
  `OData-EntityId` header, for creates), and `_error` (on `_status >= 400` or `0`).
  Collection results are under `.value`.
- `Invoke-DfmApi` adds the standard headers (`Accept: application/json`,
  `OData-MaxVersion: 4.0`, `OData-Version: 4.0`) and, for POST/PATCH, sets
  `Content-Type: application/json` automatically. Build the body with
  `ConvertTo-Json` — all escaping is handled (the body is passed into the page as
  base64; **no `-replace` placeholder substitution, no fragile result regex**).

> **PowerShell `$` gotcha**: in a double-quoted endpoint string, escape OData
> system query options with a backtick — `` "`$select=..." ``, `` "`$filter=..." `` —
> or build the string single-quoted. An unescaped `$select` interpolates to empty.

> **OData vs FetchXML**: the examples below use OData query strings (`$select`,
> `$filter`, `$expand`, `$orderby`) — cleanest for `Invoke-DfmApi`. For queries that
> need cross-entity `link-entity` joins or aggregates, pass FetchXML instead:
> `/<entityset>?fetchXml=<URL-encoded fetchxml>`.

---

## Read endpoints

### Case basic info

```powershell
# by ticketnumber (this is exactly what Get-DfmIncidentId does)
Invoke-DfmApi -SessionId $sid -Endpoint "/api/data/v9.0/incidents?`$select=incidentid,ticketnumber,title,severitycode,statuscode,statecode&`$filter=ticketnumber eq '$caseId'"

# by incidentid (direct)
Invoke-DfmApi -SessionId $sid -Endpoint "/api/data/v9.0/incidents($iid)?`$select=title,ticketnumber,severitycode,statuscode,_owninguser_value,msdfm_supportareapath"
```

> Add the header `Prefer: odata.include-annotations="*"` (via a future param) to get
> `@OData.Community.Display.V1.FormattedValue` human-readable values; otherwise you
> get raw option-set integers (decode with [`entity-model.md`](entity-model.md)).

### Customer Statement (Restricted Attributes) — nav-only

> ⚠️ `msdfm_caserestrictedattributes` cannot be queried as a top-level entity set
> (404). Read it through the `incident` navigation property:

```powershell
Invoke-DfmApi -SessionId $sid -Endpoint "/api/data/v9.0/incidents($iid)/msdfm_CaseRestrictedAttributesId?`$select=msdfm_customerstatement,msdfm_symptom,msdfm_overview,msdfm_businessimpact,msdfm_issuecontext,msdfm_rootcausedescription,msdfm_solutiondescriptionmultiline,msdfm_resolution,msdfm_actionplancustomerviewable,msdfm_currentstatuscustomerviewable"
```

(A DOM helper `Get-DfmCaseStatement` can also surface this field via the
Restricted-information toggle; the OData path above is the faster read.)

### Notes (annotations)

```powershell
Invoke-DfmApi -SessionId $sid -Endpoint "/api/data/v9.0/annotations?`$select=annotationid,subject,notetext,createdon,modifiedon,_createdby_value&`$filter=_objectid_value eq $iid&`$orderby=createdon desc&`$top=100"
```

### Emails

```powershell
Invoke-DfmApi -SessionId $sid -Endpoint "/api/data/v9.0/emails?`$select=subject,torecipients,sender,statuscode,statecode,createdon,senton,directioncode,description&`$filter=_regardingobjectid_value eq $iid&`$orderby=createdon desc&`$top=100"
```

`statuscode`: `1`=Draft, `2`=Completed, `3`=Pending Send, `4`=Sent, `6`=Canceled.

### Phone calls

```powershell
Invoke-DfmApi -SessionId $sid -Endpoint "/api/data/v9.0/phonecalls?`$select=subject,phonenumber,directioncode,createdon,description,statuscode&`$filter=_regardingobjectid_value eq $iid&`$orderby=createdon desc&`$top=50"
```

### Labor — entity set `msdfm_labors`

> ⚠️ The entity set is **`msdfm_labors`** (not `msdfm_efforts`).

```powershell
Invoke-DfmApi -SessionId $sid -Endpoint "/api/data/v9.0/msdfm_labors?`$select=msdfm_laborid,msdfm_classification,msdfm_date,msdfm_duration,msdfm_description,createdon&`$filter=_msdfm_caseid_value eq $iid&`$orderby=createdon desc&`$top=50"
```

### Attachments count (DTM) — FetchXML aggregate

```powershell
$fx = [uri]::EscapeDataString(@"
<fetch aggregate="true"><entity name="msdfm_dtmattachmentmetadata">
  <attribute name="msdfm_dtmattachmentmetadataid" aggregate="count" alias="count"/>
  <filter><condition attribute="msdfm_caseid" operator="eq" value="$iid"/></filter>
</entity></fetch>
"@)
Invoke-DfmApi -SessionId $sid -Endpoint "/api/data/v9.0/msdfm_dtmattachmentmetadatas?fetchXml=$fx"
```

### ICM details

```powershell
Invoke-DfmApi -SessionId $sid -Endpoint "/api/data/v9.0/msdfm_icmdetails?`$select=msdfm_status,msdfm_severity,msdfm_name,msdfm_title,msdfm_icmid,msdfm_url,msdfm_createdate&`$filter=_msdfm_caseid_value eq $iid&`$top=50"
```

### Contact email (for greeting / recipient)

```powershell
Invoke-DfmApi -SessionId $sid -Endpoint "/api/data/v9.0/contacts($contactId)?`$select=emailaddress1,fullname,telephone1"
```

### My open cases (current user, active)

FetchXML with the `eq-userid` shortcut:

```powershell
$fx = [uri]::EscapeDataString(@"
<fetch count="100"><entity name="incident">
  <attribute name="incidentid"/><attribute name="ticketnumber"/><attribute name="title"/>
  <attribute name="severitycode"/><attribute name="statuscode"/><attribute name="modifiedon"/>
  <filter>
    <condition attribute="statecode" operator="eq" value="0"/>
    <condition attribute="msdfm_assignedtoid" operator="eq-userid"/>
  </filter>
  <order attribute="modifiedon" descending="true"/>
</entity></fetch>
"@)
Invoke-DfmApi -SessionId $sid -Endpoint "/api/data/v9.0/incidents?fetchXml=$fx"
```

---

## Write endpoints

> 🔒 **All writes require explicit user confirmation before execution** — show the
> exact content, wait for go-ahead, then POST/PATCH. This is the standing
> write-safety rule across DFM skills.

### Add Note — `POST /annotations`

```powershell
$body = [ordered]@{
  subject                        = '[IR] Initial investigation'
  notetext                       = $noteText                       # plain text by default; ConvertTo-DfmNoteHtml for HTML
  'objectid_incident@odata.bind' = "/incidents($iid)"
} | ConvertTo-Json -Compress -Depth 5
$r = Invoke-DfmApi -SessionId $sid -Method POST -Endpoint '/api/data/v9.0/annotations' -Body $body
# success: $r._status -eq 204, $r._entityId carries the new annotation URL
```

### Record Labor — `POST /msdfm_labors`

> ⚠️ `msdfm_CaseId@odata.bind` is **PascalCase** (lowercase → 400).
> `msdfm_durationpicker` must equal `msdfm_duration`.

```powershell
$body = [ordered]@{
  msdfm_classification        = 337818            # Troubleshooting (Int32 Picklist)
  msdfm_date                  = '2026-06-22T00:00:00.000Z'
  msdfm_description           = 'See case notes'
  msdfm_duration              = 30
  msdfm_durationpicker        = 30
  statuscode                  = 1
  statecode                   = 0
  'msdfm_CaseId@odata.bind'   = "/incidents($iid)"
} | ConvertTo-Json -Compress -Depth 5
Invoke-DfmApi -SessionId $sid -Method POST -Endpoint '/api/data/v9.0/msdfm_labors' -Body $body
```

### Add Phone Call — `POST /phonecalls`

> ⚠️ regarding bind uses the `_phonecall` suffix.

```powershell
$body = [ordered]@{
  subject       = 'Customer call'
  directioncode = $true
  statuscode    = 1
  statecode     = 0
  phonecall_activity_parties = @(
    @{ 'partyid_contact@odata.bind'    = "/contacts($contactId)"; participationtypemask = 2 },
    @{ 'partyid_systemuser@odata.bind' = "/systemusers($userId)"; participationtypemask = 1 }
  )
  'regardingobjectid_incident_phonecall@odata.bind' = "/incidents($iid)"
} | ConvertTo-Json -Compress -Depth 6
Invoke-DfmApi -SessionId $sid -Method POST -Endpoint '/api/data/v9.0/phonecalls' -Body $body
```

### Update case status — `PATCH /incidents(<guid>)`

```powershell
$body = @{ statuscode = 847050020 } | ConvertTo-Json   # e.g. Mitigated
Invoke-DfmApi -SessionId $sid -Method PATCH -Endpoint "/api/data/v9.0/incidents($iid)" -Body $body
```

`statuscode` values → [`entity-model.md`](entity-model.md).

### Resolve case — `POST /CloseIncident`

> ⚠️ Close all Open activities (Email/Phone Call) first, or the call errors.

```powershell
$body = @{
  IncidentResolution = @{
    subject                = 'Case Resolved'
    'incidentid@odata.bind' = "/incidents($iid)"
  }
  Status = -1
} | ConvertTo-Json -Depth 5
Invoke-DfmApi -SessionId $sid -Method POST -Endpoint '/api/data/v9.0/CloseIncident' -Body $body
```

### Close a phone-call activity — `POST /phonecalls(<guid>)/Microsoft.Dynamics.CRM.CloseActivity`

```powershell
Invoke-DfmApi -SessionId $sid -Method POST -Endpoint "/api/data/v9.0/phonecalls($phonecallId)/Microsoft.Dynamics.CRM.CloseActivity" -Body (@{ Status = 2 } | ConvertTo-Json)
```

---

## Standard headers added by `Invoke-DfmApi`

```
Accept: application/json
OData-MaxVersion: 4.0
OData-Version: 4.0
Content-Type: application/json     (POST/PATCH with a body only)
```

See [`error-diagnosis.md`](error-diagnosis.md) for the known-pitfall table and what
each HTTP status means here.
