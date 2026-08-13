# (top-level)

> Source: **Network Manager - NsmPlus WcfRequest Search** dashboard, chapter **(top-level)** (3 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "NsmPlus WcfRequest Search"

Cluster: `aznwsdn.kusto.windows.net` · Database: `nsmplus` · Type: `ResourceGet` · Widget: `Container`

```kusto
let startTime = datetime_add('day', -1, local_PreciseTimeStamp);
let endTime = datetime_add('hour', 1, local_PreciseTimeStamp);
WcfRequestProcessing
| where PreciseTimeStamp between (startTime .. endTime)
| where additional has local_TenantName
| summarize arg_max(PreciseTimeStamp, *) by additional
| extend TenantName = local_TenantName
| project PreciseTimeStamp, Tenant, action, additional, TenantName
| top 1 by PreciseTimeStamp desc
```

**Params:** `{local_PreciseTimeStamp}`, `{local_TenantName}`

---

### NsmPlusWcfRequest

Cluster: `aznwsdn.kusto.windows.net` · Database: `nsmplus` · Type: `CoBeTimeline`

```kusto
let startTime = datetime_add('hour', -12, timestamp);
let endTime = datetime_add('hour', 1, timestamp);
WcfRequestProcessing
| where PreciseTimeStamp between (startTime..endTime) 
| where additional has TenantName
| summarize arg_min(PreciseTimeStamp, *) by additional
| top 100 by PreciseTimeStamp desc
| project  StartTime = PreciseTimeStamp, EventId = messageId, EventName = action,
Properties = tostring(pack('additional', additional))
```

**Params:** `{timestamp}`, `{TenantName}`

---

### NsmPlus TraceLog

Cluster: `aznwsdn.kusto.windows.net` · Database: `nsmplus` · Type: `Table`

```kusto
let startTime = datetime_add('hour', -12, timestamp);
let endTime = datetime_add('hour', 1, timestamp);
TraceLogs
| where PreciseTimeStamp between (startTime..endTime) 
| where text contains TenantName
//| where text contains 'Exception'
//| where text !contains 'Updated: /vnets'
| project PreciseTimeStamp, Tenant, text 
| top 100 by PreciseTimeStamp desc
```

**Params:** `{timestamp}`, `{TenantName}`

**Signal filters seen in KQL:** `text contains "Exception"`

---
