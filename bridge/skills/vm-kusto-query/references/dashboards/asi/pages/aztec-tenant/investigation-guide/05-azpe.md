# AzPE

> Source: **Aztec — Tenant** dashboard, chapter **AzPE** (4 queries across 3 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### AzPETenantSnapshot

_Widget purpose:_ AzPE

Cluster: `azpe` · Database: `azpe` · Type: `FeatureList` · Widget: `Card`
Source panel: `AzPE`

```kusto
AzPETenantSnapshot
| where PreciseTimeStamp between (min_of(queryFrom, datetime_add('day',-1, queryTo)) .. queryTo)
| where TenantName == queryTenantName
| summarize arg_max(PreciseTimeStamp,*) by TenantAvailabilityPolicy
| project features = pack(
    "ScheduledEvents", iif(TenantAvailabilityPolicy== "ScheduledEvents", "Enabled", "Disabled"),
    "Semiprivileged", iif(TenantAvailabilityPolicy== "Semiprivileged", "Enabled", "Disabled"), 
    "Privileged", iif(TenantAvailabilityPolicy== "Privileged", "Enabled", "Disabled"), 
    "Unprivileged", iif(TenantAvailabilityPolicy== "Unprivileged", "Enabled", "Disabled"), 
    "Default", iif(TenantAvailabilityPolicy== "Default", "Enabled", "Disabled"))    
| mv-expand bagexpansion=array features
| project FeatureName = tostring(features[0]), State = tostring(features[1])
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

## AzPE

### Query AzPEWorkflowEvent

_Widget purpose:_ AzPEWorkflowEvent

Cluster: `azpe` · Database: `azpe` · Type: `Table`
Source panel: `AzPE > AzPE > AzPEWorkflowEvent`

```kusto
let listEventId = MREvents
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where EntityId == queryTenantName
| distinct EventId;
AzPEWorkflowEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where WorkflowInstanceGuid in (listEventId) or EntityId == queryTenantName
| project PreciseTimeStamp, Tenant, WorkflowId, WorkflowType, WorkflowEventType, WorkflowEventData, WorkflowInstanceGuid
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

### Query MREvents

_Widget purpose:_ MR Events

Cluster: `azpe` · Database: `azpe` · Type: `Table`
Source panel: `AzPE > AzPE > MR Events`

```kusto
MREvents
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where EntityId == queryTenantName
| project PreciseTimeStamp, AzPEWorkflowId, WorkflowType, WorkflowEventType, EventId
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

## AzPENotificationStepResultEvents

### AzPENotificationStepResultEvents

Cluster: `accp.centralus` · Database: `azsm` · Type: `Table`
Source panel: `AzPE > AzPENotificationStepResultEvents`

```kusto
AzPENotificationStepResultEvents
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where tenantName == tenantNames
| project PreciseTimeStamp, azpeNotificationStepType, result, failure, Cluster
```

**Params:** `{queryFrom}`, `{queryTo}`, `{tenantNames}`

---
