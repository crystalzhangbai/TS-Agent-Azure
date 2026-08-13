# Scheduled Events

> Source: **CRP — VMs** dashboard, chapter **Scheduled Events** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Query Scheduled Events in AzPEWorkflowEvent

_Widget purpose:_ Scheduled Events

Cluster: `azpe` · Database: `azpe` · Type: `Table`
Source panel: `Scheduled Events`

```kusto
let tenantNames = toscalar(cluster('azcsupfollower').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where virtualMachineUniqueId == queryVMId
| distinct tenantName);
AzPEWorkflowEvent
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where EntityId in (tenantNames)
| project PreciseTimeStamp, TenantName = EntityId, Tenant, WorkflowId, WorkflowType, WorkflowEventType, WorkflowEventData, WorkflowInstanceGuid
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryVMId}`

---
