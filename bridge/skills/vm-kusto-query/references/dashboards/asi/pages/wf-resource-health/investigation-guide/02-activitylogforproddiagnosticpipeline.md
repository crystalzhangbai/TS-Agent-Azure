# ActivityLogForProdDiagnosticPipeline

> Source: **EEE RDOS — WF Resource Health** dashboard, chapter **ActivityLogForProdDiagnosticPipeline** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Represents resource health events that have been pushed from GHS (Geneva Health) to customer activity log

### ResourceHealthAzureActivityLogEvent_UnexpectedRestart DS

_Widget purpose:_ Represents resource health events that have been pushed from GHS (Geneva Health) to customer activity log

Cluster: `icmbrain` · Database: `AzureResourceHealth` · Type: `Table`
Source panel: `ActivityLogForProdDiagnosticPipeline > Represents resource health events that have been pushed from GHS (Geneva Health) to customer activity log`

```kusto
ActivityLogForProdDiagnosticPipeline
| where todatetime(env_time) between (query_StartTime..query_EndTime)
| where resourceType == "Microsoft.Compute/virtualMachines"
| where resourceId has query_ResourceId
| extend Title= parse_json(properties)['title']
| extend Cause= parse_json(properties)['cause']
| extend Type= parse_json(properties)['type']
| extend CurrentHealthStatus= parse_json(properties)['currentHealthStatus']
| extend PreviousHealthStatus= parse_json(properties)['previousHealthStatus']
| extend Details= parse_json(properties)['details']
|project env_time, Title , Cause , Type, CurrentHealthStatus, PreviousHealthStatus, Details, resourceId
```

**Params:** `{query_StartTime}`, `{query_EndTime}`, `{query_ResourceId}`

**Signal filters seen in KQL:** `resourceType == "Microsoft.Compute/virtualMachines"`

---

### VmShoeboxCounterTable DS

_Widget purpose:_ Represents resource health events that have been pushed from GHS (Geneva Health) to customer activity log

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Single` · Widget: `Table`
Source panel: `ActivityLogForProdDiagnosticPipeline > Represents resource health events that have been pushed from GHS (Geneva Health) to customer activity log`

```kusto
VmShoeboxCounterTable
| where PreciseTimeStamp between ((query_StartTime - 1h) .. (query_EndTime + 1h)) and VmId =~ query_ContainerId
| distinct ArmId
```

**Params:** `{query_StartTime}`, `{query_EndTime}`, `{query_ContainerId}`

---
