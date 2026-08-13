# ResourceHealthAzureActivityLogEvent

> Source: **EEE RDOS — WF Resource Health** dashboard, chapter **ResourceHealthAzureActivityLogEvent** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### ResourceHealthAzureActivityLogEvent

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `ResourceHealthAzureActivityLogEvent`

```kusto
VmShoeboxCounterTable
| where PreciseTimeStamp between ((queryFrom - 1h) .. (queryTo + 1h)) and VmId =~ query_ContainerId
| project LArmId=tolower(ArmId)
| join kind=inner
(cluster("icmbrain.kusto.windows.net").database("AzureResourceHealth").ResourceHealthAzureActivityLogEvent
| where env_time between (queryFrom..queryTo)
| project env_time, eventTimestamp, env_cloud_location, healthStatus, ['title'], healthEventType, healthEventCause, internalId, resourceId, correlationId,ArmId=tolower(resourceId)) on $left.LArmId == $right.ArmId
| order by env_cloud_location asc, eventTimestamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_ContainerId}`

---
