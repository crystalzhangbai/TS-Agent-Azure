# Resource Health

> Source: **VM Scuba - VM Details** dashboard, chapter **Resource Health** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get-ResourceHealth

_Widget purpose:_ Resource Health

Cluster: `icmbrain.kusto.windows.net` · Database: `AzureResourceHealth` · Type: `Table`
Source panel: `Resource Health`

```kusto
cluster("icmbrain.kusto.windows.net").database('AzureResourceHealth').ResourceHealthAzureActivityLogEvent
| where subscriptionId =~ subscriptionId and  resourceId has trim_start("_",roleInstanceName) 
//| where  TIMESTAMP between (queryFrom .. queryTo)
| extend resourceName = tolower(tostring(split(resourceId,'/')[-1])),reason =['title'], id = tostring(split((split(internalId, '/')[-1]), ':')[0])
| project eventTimestamp, subscriptionId, resourceName, healthStatus, reason, healthEventType, healthEventCause, level, id, internalId, resourceId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{roleInstanceName}`, `{subscriptionId}`

---
