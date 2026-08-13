# ARM Event

> Source: **CRP Resource Move Investigation Guide** dashboard, chapter **ARM Event** (2 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## ARM Event

### ARM Event

Cluster: `armprod` · Database: `ARMProd` · Type: `Table`
Source panel: `ARM Event > ARM Event`

```kusto
cluster('armprod.kusto.windows.net').database('ARMProd').EventServiceEntries
| where PreciseTimeStamp between (starttime .. endtime)
| where correlationId contains correlationid
| where operationName !contains "Microsoft.Authorization"
| where operationName !contains "restorePoint"
| project PreciseTimeStamp, ActivityId , correlationId, operationName, operationId, 
  resourceProvider, level, status, subStatus, httpRequest, properties, resourceUri, 
  armServiceRequestId, authorization, claims, RoleInstance, SourceNamespace, ReleaseVersion
| extend level = case (level == 1, "critical",
  level == 2, "error", 
  level == 3, "warning", 
  "info")
```

**Params:** `{starttime}`, `{endtime}`, `{correlationid}`

---

## Latest Error Details

### Error Details

_Widget purpose:_ Latest Error Details

Cluster: `armprod` · Database: `ARMProd` · Type: `Single` · Widget: `Card`
Source panel: `ARM Event > Latest Error Details`

```kusto
cluster('armprod.kusto.windows.net').database('ARMProd').EventServiceEntries
| where PreciseTimeStamp between (starttime .. endtime)
| where correlationId == correlationid
| where operationName !contains "Microsoft.Authorization"
| where operationName !contains "restorePoint"
| where operationName contains 'move'
| where status == "Failed"
| top 1 by PreciseTimeStamp desc
| project PreciseTimeStamp, ActivityId , correlationId, operationName, operationId, 
  resourceProvider, level, status, subStatus, httpRequest, properties, resourceUri, 
  armServiceRequestId, authorization, claims, RoleInstance, SourceNamespace, ReleaseVersion
| project PreciseTimeStamp, correlationId, parse_json(properties).statusCode, parse_json(properties).statusMessage
```

**Params:** `{starttime}`, `{endtime}`, `{correlationid}`

**Signal filters seen in KQL:** `operationName contains "move"` · `status == "Failed"`

---
