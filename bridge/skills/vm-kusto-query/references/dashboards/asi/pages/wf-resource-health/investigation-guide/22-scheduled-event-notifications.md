# Scheduled Event Notifications

> Source: **EEE RDOS — WF Resource Health** dashboard, chapter **Scheduled Event Notifications** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### AzPEWorkflowEvent

Cluster: `azpe.kusto.windows.net` · Database: `azpe` · Type: `Table`
Source panel: `Scheduled Event Notifications`

```kusto
let workflowId = cluster("azpe.kusto.windows.net").database("azpe").AzPEWorkflowEvent
| where PreciseTimeStamp between (startTime .. endTime) and EntityId == tenantName and WorkflowEventData contains roleInstanceName
| distinct WorkflowId;
cluster("azpe.kusto.windows.net").database("azpe").AzPEWorkflowEvent
| where PreciseTimeStamp between (startTime .. endTime) and WorkflowId in (workflowId) and EntityId == tenantName
| project PreciseTimeStamp, WorkflowEventType, WorkflowEventData
| sort by PreciseTimeStamp asc
```

**Params:** `{startTime}`, `{endTime}`, `{tenantName}`, `{roleInstanceName}`

---
