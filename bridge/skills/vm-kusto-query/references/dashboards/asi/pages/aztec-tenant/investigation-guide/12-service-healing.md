# Service Healing

> Source: **Aztec — Tenant** dashboard, chapter **Service Healing** (6 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Service Healing

### AzSMServiceHealingStepResultEvents

Cluster: `accp.centralus` · Database: `AZSM` · Type: `Timeline`
Source panel: `Service Healing > Service Healing > AzSM Service Healing > AzSM Service Healing`

```kusto
let Table=AzSMServiceHealingStepResultEvents
| where PreciseTimeStamp between (queryFrom..queryTo)
| where tenantName == queryTenantName 
| order by containerMigrationStepType asc
| project PreciseTimeStamp, containerMigrationStepType, result, totalDurationInMilliSeconds, JobId, roleInstanceName
| extend flag = case (containerMigrationStepType <> prev(containerMigrationStepType) , "changed",containerMigrationStepType == prev(containerMigrationStepType) and result <>prev(result), "changedtime", "");
let StepCounts = 
    Table
    | summarize StepCount = count() by containerMigrationStepType;
Table
| join kind=inner (StepCounts) on containerMigrationStepType
| extend 
    StartTime = case(
        result == "Succeeded", datetime_add("millisecond", -1 * toint(totalDurationInMilliSeconds), PreciseTimeStamp),
         result == "Started", PreciseTimeStamp,
        datetime(null))
| extend 
    EndTime = case(
        StepCount == 1 and result == "Succeeded",  PreciseTimeStamp,
        StepCount % 2 !=0 and result == "Started", PreciseTimeStamp,
        StepCount > 1 and result == "Succeeded", PreciseTimeStamp,
        datetime(null)
    )
| where flag == "changedtime" or (flag== "changed" and StepCount == "1")
| extend Health = case (totalDurationInMilliSeconds> 600000, "Unhealthy",totalDurationInMilliSeconds between (300000 .. 600000), "Degraded", "Healthy")
| project StartTime, EndTime, Health, Content=containerMigrationStepType, totalDurationInMilliSeconds, JobId, GroupBy = strcat("Step-",containerMigrationStepType)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

**Signal filters seen in KQL:** `flag == "changedtime"`

---

### AzSMServiceHealingResultEvents

Cluster: `accp.centralus.kusto.windows.net` · Database: `AZSM` · Type: `Table`
Source panel: `Service Healing > Service Healing > AzSM Service Healing > AzSM Service Healing > AzSMServiceHealingResultEvents`

```kusto
AzSMServiceHealingResultEvents
| where PreciseTimeStamp between(queryFrom..queryTo)
| where tenantName =~ queryTenantName
| extend StartTime = datetime_add('millisecond', -totalDurationInMilliSeconds, PreciseTimeStamp)
| extend level = case(
    result == "Failed", "Error",
    result != "Succeeded", "Warning",
    "Info"
)
| project StartTime, PreciseTimeStamp, totalDurationInMilliSeconds, tenantName, EventMessage, result, sourceContainerId, targetContainerId, triggerId, level
| order by StartTime asc
```

**Params:** `{queryTenantName}`, `{queryFrom}`, `{queryTo}`

---

### AzSMServiceHealingStepResultEvents

Cluster: `accp.centralus.kusto.windows.net` · Database: `AZSM` · Type: `Table`
Source panel: `Service Healing > Service Healing > AzSM Service Healing > AzSM Service Healing > AzSMServiceHealingStepResultEvents`

```kusto
AzSMServiceHealingStepResultEvents
| where PreciseTimeStamp between(queryFrom..queryTo)
| where tenantName == queryTenantName
| extend level = case(
    result == "Failed", "Error",
    result == "TimedOut", "Warning",
    "Info"
)
| project PreciseTimeStamp, triggerId, containerMigrationStepType, result, totalDurationInMilliSeconds, failureReason, stepContext, targetContainerId, level
| order by PreciseTimeStamp asc
```

**Params:** `{queryTenantName}`, `{queryFrom}`, `{queryTo}`

---

### AzSMServiceHealingTriggerEvents

Cluster: `accp.centralus.kusto.windows.net` · Database: `AZSM` · Type: `Table`
Source panel: `Service Healing > Service Healing > AzSM Service Healing > AzSM Service Healing > AzSMServiceHealingTriggerEvents`

```kusto
AzSMServiceHealingTriggerEvents
| where PreciseTimeStamp between(queryFrom..queryTo)
| where tenantName =~ queryTenantName
| order by PreciseTimeStamp asc
| summarize FirstSeen = min(PreciseTimeStamp), LastSeen = max(PreciseTimeStamp),triggerIdList = make_list(triggerId) by triggerObjectId, triggerType, faultCode, faultReason 
| order by FirstSeen asc
```

**Params:** `{queryTenantName}`, `{queryFrom}`, `{queryTo}`

---

### Query ServiceHealingTenantStatusEtwTable

_Widget purpose:_ ServiceHealingTenantStatusEtwTable

Cluster: `azcore.centralus` · Database: `Fc` · Type: `Table`
Source panel: `Service Healing > Service Healing > Service Healing > Service Healing > ServiceHealingTenantStatusEtwTable`

```kusto
ServiceHealingTenantStatusEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where TenantName == queryTenantName
| project PreciseTimeStamp, State, Context, Message
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

### Query ServiceHealingTriggerEtwTable

_Widget purpose:_ ServiceHealingTriggerEtwTable

Cluster: `azcore.centralus` · Database: `Fc` · Type: `Table`
Source panel: `Service Healing > Service Healing > Service Healing > Service Healing > ServiceHealingTriggerEtwTable`

```kusto
ServiceHealingTriggerEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where TenantName == queryTenantName
| project PreciseTimeStamp, Tenant, TriggerId, TriggerType, TriggerObjectId, FaultCode, FaultReason, FaultInfoCorrelationGuid, AffectedUpdateDomain, RoleInstanceName
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---
