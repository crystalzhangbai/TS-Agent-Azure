# ResourceHealthAnnotationEvent

> Source: **EEE RDOS — WF Resource Health** dashboard, chapter **ResourceHealthAnnotationEvent** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Represents received annotations from Host/Fabric to GHS

### ResourceHealthAnnotationEvent DS

_Widget purpose:_ Represents received annotations from Host/Fabric to GHS

Cluster: `icmbrain` · Database: `AzureResourceHealth` · Type: `Table`
Source panel: `ResourceHealthAnnotationEvent > Represents received annotations from Host/Fabric to GHS`

```kusto
ResourceHealthAnnotationEvent
| where env_time between (query_StartTime..query_EndTime)
| where resourceId has query_vmId 
|project  monitorName, env_time, env_reportTime,env_metadata, annotation, resourceId, correlationId
```

**Params:** `{query_StartTime}`, `{query_EndTime}`, `{query_vmId}`

---
