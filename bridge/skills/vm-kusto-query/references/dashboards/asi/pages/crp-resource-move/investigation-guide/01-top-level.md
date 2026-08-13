# (top-level)

> Source: **CRP Resource Move Investigation Guide** dashboard, chapter **(top-level)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Resource Move"

Cluster: `armprodgbl.eastus` · Database: `ARMProd` · Type: `ResourceGet` · Widget: `Container`

```kusto
print correlationId = local_correlationId
```

**Params:** `{local_correlationId}`, `{globalFrom}`, `{globalTo}`

---

### Move ARM Event

_Widget purpose:_ Operation Info

Cluster: `armprod` · Database: `ARMProd` · Type: `Single` · Widget: `Card`

```kusto
cluster('armprod.kusto.windows.net').database('ARMProd').EventServiceEntries
| where PreciseTimeStamp between (starttime .. endtime)
| where correlationId contains correlationid
| where operationName !contains "Microsoft.Authorization"
| where operationName !contains "restorePoint"
| where operationName contains 'move'
| project PreciseTimeStamp, ActivityId , correlationId, operationName, operationId, 
  resourceProvider, level, status, subStatus, httpRequest, properties, resourceUri, 
  armServiceRequestId, authorization, claims, RoleInstance, SourceNamespace, ReleaseVersion
| top 1 by PreciseTimeStamp asc
```

**Params:** `{starttime}`, `{endtime}`, `{correlationid}`

**Signal filters seen in KQL:** `operationName contains "move"`

---
