# ResourceHealthStatusTransitionEvent

> Source: **EEE RDOS — WF Resource Health** dashboard, chapter **ResourceHealthStatusTransitionEvent** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Represents received health reports ( and generating proper health status transitions) from Host to GHS for Virtual Machines

### ResourceHealthStatusTransitionEvent DS

_Widget purpose:_ Represents received health reports ( and generating proper health status transitions) from Host to GHS for Virtual Machines

Cluster: `icmbrain` · Database: `AzureResourceHealth` · Type: `Table`
Source panel: `ResourceHealthStatusTransitionEvent > Represents received health reports ( and generating proper health status transitions) from Host to GHS for Virtual Machines`

```kusto
let healthStatusMapping = dynamic({"0": "Healthy (0)", "1": "Unhealthy (1)", "2": "Warning (2)", "3": "Unknown (3)", "4": "ErrorOrWarning (4)"});
ResourceHealthStatusTransitionEvent
| where env_time between (query_StartTime..query_EndTime)
| where resourceId has query_vmId
| extend ContainerId = parse_json(env_metadata).ContainerId
| extend NodeId = parse_json(env_metadata).NodeId
| extend ArmId = parse_json(env_metadata).ArmId
| project env_time, previousHealthStatus=healthStatusMapping[tostring(previousHealthStatus)], 
newHealthStatus=healthStatusMapping[tostring(newHealthStatus)],
 VMId=resourceId,ContainerId,NodeId,resourceType, ArmId, env_metadata,  env_cloud_location
```

**Params:** `{query_StartTime}`, `{query_EndTime}`, `{query_vmId}`

---
