# ResourceHealthAzureActivityLogEvent

> Source: **CRP — VMs** dashboard, chapter **ResourceHealthAzureActivityLogEvent** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Query ResourceHealthAzureActivityLogEvent

_Widget purpose:_ ResourceHealthAzureActivityLogEvent

Cluster: `icmbrain` · Database: `AzureResourceHealth` · Type: `Table`
Source panel: `ResourceHealthAzureActivityLogEvent`

```kusto
ResourceHealthAzureActivityLogEvent
| where eventTimestamp between (queryFrom .. queryTo)
| where subscriptionId == querySubId
| where resourceId =~ queryResourceId
| sort by eventTimestamp desc
| project processingTimestamp = eventTimestamp, eventTimestamp, correlationId, eventDataId, healthStatus, level, healthEventType, healthEventCause, ['title']
| union 
(
   ActivityLogForProdDiagnosticPipeline
   | where ['time'] between (queryFrom .. queryTo)
   | where resourceId =~ queryResourceId
   | extend props=parse_json(properties), eventTimestamp = ['time'], stage = operationName, healthEventCategory = category
   | extend healthStatus = strcat(props['previousHealthStatus'], '->', props['currentHealthStatus']), healthEventCause = tostring(props['cause']), healthEventType = tostring(props['type']), ['title'] = tostring(props['title'])
   | project processingTimestamp = eventTimestamp, eventTimestamp, correlationId, healthStatus, level, healthEventType, healthEventCause, ['title'] 
)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryResourceId}`, `{querySubId}`

---
