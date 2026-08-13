# Service Healing

> Source: **EEE RDOS — WF Unexpected Restart** dashboard, chapter **Service Healing** (12 queries across 3 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## AzSM

### Service Healing Trigger Type

Cluster: `accp.centralus` · Database: `AZSM` · Type: `Timeline`
Source panel: `Service Healing > AzSM`

```kusto
AzSMServiceHealingTriggerEvents
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where tenantName =~ queryTenantname and roleInstanceNames in (queryRI)
| order by PreciseTimeStamp asc
| summarize StartTime = min(PreciseTimeStamp), arg_max(PreciseTimeStamp, triggerType, faultCode, faultReason, faultCode) by triggerId
| join kind=leftouter (AzSMServiceHealingStepResultEvents
    | where PreciseTimeStamp between(queryFrom .. queryTo)
    | where tenantName == queryTenantname
    | summarize EndTime = max(PreciseTimeStamp), arg_max(PreciseTimeStamp, result) by triggerId, failureReason, targetContainerId 
) on triggerId
| project StartTime, EndTime, triggerType, triggerId, faultReason, targetContainerId, result
| extend Health = iif (result != "Succeeded", "Unhealthy", "Degraded")
| extend Content = triggerType
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantname}`, `{queryRI}`

---

### AzSMServiceHealingStepResultEvents

Cluster: `accp.centralus` · Database: `AZSM` · Type: `Timeline`
Source panel: `Service Healing > AzSM`

```kusto
let Table=AzSMServiceHealingStepResultEvents
| where PreciseTimeStamp between (queryFrom..queryTo)
| where tenantName == querytenantName and roleInstanceName  contains RIname
| order by containerMigrationStepType asc
| project PreciseTimeStamp, containerMigrationStepType, result, totalDurationInMilliSeconds, JobId
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

**Params:** `{queryFrom}`, `{queryTo}`, `{querytenantName}`, `{RIname}`

**Signal filters seen in KQL:** `flag == "changedtime"`

---

### AzSMServiceHealingResultEvents_clmendes

_Widget purpose:_ AzSMServiceHealingResultEvents

Cluster: `accp.centralus` · Database: `AZSM` · Type: `Table`
Source panel: `Service Healing > AzSM > AzSMServiceHealingResultEvents`

```kusto
let jobids=AzSMServiceHealingTriggerEvents
| where PreciseTimeStamp between (queryFrom..queryTo)
| where tenantName =~ queryTenantName
| where roleInstanceNames contains queryRIName
| distinct JobId;
AzSMServiceHealingResultEvents
| where PreciseTimeStamp between (queryFrom..queryTo)
| where JobId has_any (jobids)
| extend StartTime = datetime_add('millisecond', -totalDurationInMilliSeconds, PreciseTimeStamp)
| extend level = case(
    result == "Failed", "Error",
    result != "Succeeded", "Warning",
    "Info"
)
| project StartTime, PreciseTimeStamp, totalDurationInMilliSeconds, tenantName, EventMessage, result, sourceContainerId, targetContainerId, triggerId, level
| order by StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`, `{queryRIName}`

---

### AzSMServiceHealingStepResultEvents_clmendes

_Widget purpose:_ AzSMServiceHealingStepResultEvents

Cluster: `accp.centralus` · Database: `AZSM` · Type: `Table`
Source panel: `Service Healing > AzSM > AzSMServiceHealingStepResultEvents`

```kusto
let jobids= AzSMServiceHealingTriggerEvents
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where tenantName =~ querytenantName and roleInstanceNames contains queryRIName
| distinct JobId;
AzSMServiceHealingStepResultEvents
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where JobId has_any (jobids)
| extend level = case(
    totalDurationInMilliSeconds > 600000, "Error",
    totalDurationInMilliSeconds between (300000 .. 600000), "Warning",
    "Info"
)
| project PreciseTimeStamp,Tenant, JobId, containerMigrationStepType, result,totalDurationInMilliSeconds, failureReason, targetContainerId, stepContext, level
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querytenantName}`, `{queryRIName}`

---

### AzSMServiceHealingTriggerEvents_clmendes

_Widget purpose:_ AzSMServiceHealingTriggerEvents

Cluster: `accp.centralus` · Database: `AZSM` · Type: `Table`
Source panel: `Service Healing > AzSM > AzSMServiceHealingTriggerEvents`

```kusto
AzSMServiceHealingTriggerEvents
| where PreciseTimeStamp between (queryFrom..queryTo)
| where tenantName =~ queryTenantName and roleInstanceNames contains queryRIName
| project PreciseTimeStamp,Tenant,triggerType, migrationRequestDetails, JobId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`, `{queryRIName}`

---

### AzSMTenantEvents_clmendes

_Widget purpose:_ AzSMTenantEvents

Cluster: `accp.centralus` · Database: `AZSM` · Type: `Table`
Source panel: `Service Healing > AzSM > AzSMTenantEvents`

```kusto
AzSMTenantEvents
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where tenantName =~ queryTenantName
| project PreciseTimeStamp, Tenant, tenantName, applicationName, EventId, message, status
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`, `{queryRIName}`

---

### AzSMTenantStatemachineEvents_clmendes

_Widget purpose:_ AzSMTenantStatemachineEvents

Cluster: `accp.centralus` · Database: `AZSM` · Type: `Table`
Source panel: `Service Healing > AzSM > AzSMTenantStatemachineEvents`

```kusto
AzSMTenantStatemachineEvents
| where PreciseTimeStamp between (queryFrom..queryTo)
| where tenantName =~ queryTenantName
| where PreciseTimeStamp between (queryFrom .. queryTo) and * contains "ServiceHealing"
| project PreciseTimeStamp, stateMachineState, stateMachineId, message
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`, `{queryRIName}`

---

## Fabric

### ServiceHealingTenantStatusEtwTable_clmendes

_Widget purpose:_ ServiceHealingTenantStatusEtwTable

Cluster: `azcore.centralus` · Database: `Fc` · Type: `Table`
Source panel: `Service Healing > Fabric > ServiceHealingTenantStatusEtwTable`

```kusto
let trigger=ServiceHealingTriggerEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo) 
| where TenantName =~ queryTenantName and RoleInstanceName contains queryRIName
| distinct TriggerId;
let context=ServiceHealingTenantStatusEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo) 
| where TenantName =~ queryTenantName
| where Message has_any(trigger)
| distinct Context;
let contextcount= toscalar(context
| summarize count());
ServiceHealingTenantStatusEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo) 
| where contextcount >= 0 and TenantName =~ queryTenantName
| project PreciseTimeStamp,Tenant, TenantName, State, Context, Message
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`, `{queryRIName}`

---

### ServiceHealingTriggerEtwTable_clmendes

_Widget purpose:_ ServiceHealingTriggerEtwTable

Cluster: `azcore.centralus` · Database: `Fc` · Type: `Table`
Source panel: `Service Healing > Fabric > ServiceHealingTriggerEtwTable`

```kusto
ServiceHealingTriggerEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo)​
| where TenantName contains queryTenantName and RoleInstanceName contains queryRIName
| project PreciseTimeStamp, Tenant, TenantName, TriggerId, TriggerType, FaultReason, RoleInstanceName
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`, `{queryRIName}`

---

### TMMgmtTenantManagementJobInfoEtwTable_clmendes

_Widget purpose:_ TMMgmtTenantManagementJobInfoEtwTable

Cluster: `azcore.centralus` · Database: `Fc` · Type: `Table`
Source panel: `Service Healing > Fabric > TMMgmtTenantManagementJobInfoEtwTable`

```kusto
let trigger=ServiceHealingTriggerEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo) 
| where TenantName =~ queryTenantName and RoleInstanceName contains queryRIName
| distinct TriggerId;
let context=ServiceHealingTenantStatusEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo) 
| where TenantName =~ queryTenantName
| where Message has_any(trigger)
| distinct Context;
let contextcount= toscalar(context
| summarize count());
let contextextended=ServiceHealingTenantStatusEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo) 
| where contextcount > 0 or (contextcount == 0 and TenantName =~ queryTenantName)
| distinct Context;
TMMgmtTenantManagementJobInfoEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo) 
| where JobID has_any (contextextended)
| project PreciseTimeStamp,Tenant, TenantName, JobID, JobType, Message
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryRIName}`, `{queryTenantName}`

---

## Overview

### IssueDetector AzSMServiceHealing

_Widget purpose:_ Detector for Service Healings

Cluster: `azcore.centralus` · Database: `AzureCP` · Type: `IssueDetector`
Source panel: `Service Healing > Overview > Detector for Service Healings`

```kusto
AzSMServiceHealingTriggerEvents
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where tenantName =~ queryTenantName
| where  roleInstanceNames contains queryRIName
| order by PreciseTimeStamp asc
| count
| extend Description = iff(Count>0, "VM was service healed. Please use the AzSM tab for more information. ",'')
| extend Severity = iff(Count>0, "Critical ",'')
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`, `{queryRIName}`

---

### IssueDetector FabricServiceHealing

_Widget purpose:_ Detector for Service Healings

Cluster: `azcore.centralus` · Database: `Fc` · Type: `IssueDetector`
Source panel: `Service Healing > Overview > Detector for Service Healings`

```kusto
ServiceHealingTriggerEtwTable
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where TenantName =~ queryTenantName
| where  RoleInstanceName contains queryRIName
| order by PreciseTimeStamp asc
| count
| extend Description = iff(Count>0, "VM was service healed. Please use the Fabric tab for more information.",'')
| extend Severity = iff(Count>0, "Critical",'')
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`, `{queryRIName}`

---
