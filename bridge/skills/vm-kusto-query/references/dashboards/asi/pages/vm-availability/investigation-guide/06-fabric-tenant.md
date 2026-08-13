# Fabric / Tenant

> Source: **EEE RDOS — VM Availability** dashboard, chapter **Fabric / Tenant** (29 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Fabric / Compute Manager

### Allocation Limit

_Widget purpose:_ Deployment Limit

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `TimeSeries`
Source panel: `Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Capacity > Cluster Capacity > Deployment Limit`

```kusto
LogClusterCapacity
| where PreciseTimeStamp between (starttime .. endtime)
| where Tenant == cluster
| project PreciseTimeStamp, newDeploymentEmptyNodesLimitForAllocation, newDeploymentLimitForAllocation, upgradeEmptyNodesLimitForAllocation, upgradeLimitForAllocation
```

**Params:** `{starttime}`, `{endtime}`, `{cluster}`

---

### Allocatable State

_Widget purpose:_ New Deployment Allocatable State

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Capacity > Cluster Capacity > New Deployment Allocatable State`

```kusto
cluster('azcsupfollower').database('AzureCM').LogClusterCapacity
| where PreciseTimeStamp between (starttime .. endtime)
| where Tenant == cluster
| project PreciseTimeStamp, categoryByMachinePoolNameJson, isAcceptedNewDeployment = tostring(parse_json(newDeploymentStatusJson).isAcceptingNewDeployments), rejectReason = tostring(parse_json(newDeploymentStatusJson).rejectReason)
| order by PreciseTimeStamp asc
| extend flag = case (prev(isAcceptedNewDeployment) <> isAcceptedNewDeployment, "changed", "")
| where flag <> ""
| extend StartTime = PreciseTimeStamp, Content = ""
| extend EndTime = case (isnotempty(next(isAcceptedNewDeployment)), next(PreciseTimeStamp), endtime)
| extend Health = case (isAcceptedNewDeployment == "true", "healthy", 
    isAcceptedNewDeployment == "false", "unhealthy", 
    "degraded")
| project StartTime, EndTime, Content, Health
```

**Params:** `{starttime}`, `{endtime}`, `{cluster}`

---

### Node Count

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `TimeSeries`
Source panel: `Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Capacity > Cluster Capacity > Node Count`

```kusto
LogClusterCapacity
| where PreciseTimeStamp between (starttime .. endtime)
| where Tenant == cluster
| project PreciseTimeStamp, totalNodes, allocatableNodes, totalHen, ofrAndHiNodes
```

**Params:** `{starttime}`, `{endtime}`, `{cluster}`

---

### Util Core

_Widget purpose:_ Utilization Core

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `TimeSeries`
Source panel: `Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Capacity > Cluster Capacity > Utilization Core`

```kusto
LogClusterCapacity
| where PreciseTimeStamp between (starttime .. endtime)
| where Tenant == cluster
| project PreciseTimeStamp, categoryByMachinePoolNameJson, coresUsedFraction //, memoryUsedFraction
```

**Params:** `{starttime}`, `{endtime}`, `{cluster}`

---

### Util Memory

_Widget purpose:_ Utilization Memory

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `TimeSeries`
Source panel: `Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Capacity > Cluster Capacity > Utilization Memory`

```kusto
LogClusterCapacity
| where PreciseTimeStamp between (starttime .. endtime)
| where Tenant == cluster
| project PreciseTimeStamp, categoryByMachinePoolNameJson, memoryUsedFraction
```

**Params:** `{starttime}`, `{endtime}`, `{cluster}`

---

### Fabricator Instance

_Widget purpose:_ Fabricator

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Health > Fabric Health > Fabricator`

```kusto
cluster('azcsupfollower').database('AzureCM').LogClusterSnapshot
| where PreciseTimeStamp between (starttime .. endtime)
| where tenantName == cluster
| order by PreciseTimeStamp asc 
| project StartTime = PreciseTimeStamp, tenantName, roleInstanceName
| extend flag = case (prev(roleInstanceName) <> roleInstanceName, "changed", "")
| where flag <> ""
| extend EndTime = case (isnotempty(next(StartTime)), next(StartTime), endtime)
| extend Content = roleInstanceName
| extend Health = "Neutral"
```

**Params:** `{starttime}`, `{endtime}`, `{cluster}`

---

### Fabricator Downtime

_Widget purpose:_ Fabricator

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Health > Fabric Health > Fabricator`

```kusto
let clusters = print Tenant = cluster;
FabricFailoverDowtimeRawDataPerCluster(clusters=clusters, startTime=starttime, endTime=endtime)
| project StartTime = DownTimeStart, EndTime = DownTimeEnd, Content = strcat(tostring(DurationInMs/1000), " secs"), Health = "Unhealthy"
```

**Params:** `{starttime}`, `{endtime}`, `{cluster}`

---

### NodeStateHumanInvestigateCount

_Widget purpose:_ HumanInvestigate Node Count / Hour

Cluster: `azurecm` · Database: `AzureCM` · Type: `TimeSeries`
Source panel: `Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Health > Fabric Health > HumanInvestigate Node Count / Hour`

```kusto
cluster('azcsupfollower.kusto.windows.net').database('AzureCM').LogNodeSnapshot
| where PreciseTimeStamp between (starttime .. endtime)
// | where nodeId == nodeid
| where Tenant == cluster
| where nodeState == "HumanInvestigate"
| distinct bin(PreciseTimeStamp, 1h), nodeId, nodeState, machinePoolName
| order by PreciseTimeStamp asc 
| extend Counter = strcat(machinePoolName, ":", nodeState)
| summarize count() by PreciseTimeStamp, machinePoolName
```

**Params:** `{starttime}`, `{endtime}`, `{cluster}`

**Signal filters seen in KQL:** `nodeState == "HumanInvestigate"`

---

### NodeStateReadyCount

_Widget purpose:_ HumanInvestigate Node Count / Hour

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `TimeSeries`
Source panel: `Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Health > Fabric Health > HumanInvestigate Node Count / Hour`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fc').LogNodeSnapshot
| where PreciseTimeStamp between (starttime .. endtime)
// | where nodeId == nodeid
| where Tenant == cluster
| where nodeState == "Ready"
| distinct bin(PreciseTimeStamp, 1h), nodeId, nodeState, machinePoolName
| order by PreciseTimeStamp asc 
| extend Counter = strcat(machinePoolName, ":", nodeState)
| summarize count() by PreciseTimeStamp, machinePoolName
```

**Params:** `{starttime}`, `{endtime}`, `{cluster}`

**Signal filters seen in KQL:** `nodeState == "Ready"`

---

### NodeStateOFRCount

_Widget purpose:_ OutForRepair Node Count / Hour

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `TimeSeries`
Source panel: `Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Health > Fabric Health > OutForRepair Node Count / Hour`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fc').LogNodeSnapshot
| where PreciseTimeStamp between (starttime .. endtime)
// | where nodeId == nodeid
| where Tenant == cluster
| where nodeState == "OutForRepair"
| distinct bin(PreciseTimeStamp, 1h), nodeId, nodeState, machinePoolName
| order by PreciseTimeStamp asc 
| extend Counter = strcat(machinePoolName, ":", nodeState)
| summarize count() by PreciseTimeStamp, machinePoolName
```

**Params:** `{starttime}`, `{endtime}`, `{cluster}`

**Signal filters seen in KQL:** `nodeState == "OutForRepair"`

---

### NodeStateReadyCount

_Widget purpose:_ Ready Node Count

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `TimeSeries`
Source panel: `Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Health > Fabric Health > Ready Node Count`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fc').LogNodeSnapshot
| where PreciseTimeStamp between (starttime .. endtime)
// | where nodeId == nodeid
| where Tenant == cluster
| where nodeState == "Ready"
| distinct bin(PreciseTimeStamp, 1h), nodeId, nodeState, machinePoolName
| order by PreciseTimeStamp asc 
| extend Counter = strcat(machinePoolName, ":", nodeState)
| summarize count() by PreciseTimeStamp, machinePoolName
```

**Params:** `{starttime}`, `{endtime}`, `{cluster}`

**Signal filters seen in KQL:** `nodeState == "Ready"`

---

### Unhealthy Node Count

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fc` · Type: `TimeSeries`
Source panel: `Fabric / Tenant > Fabric / Compute Manager > Cluster > Cluster Health > Fabric Health > Unhealthy Node Count`

```kusto
cluster('storageclient.eastus.kusto.windows.net').database('Fc').LogNodeSnapshot
| where PreciseTimeStamp between (starttime .. endtime)
// | where nodeId == nodeid
| where Tenant == cluster
| where nodeState == "Unhealthy"
| distinct bin(PreciseTimeStamp, 30m), nodeId, nodeState, machinePoolName
| order by PreciseTimeStamp asc 
| extend Counter = strcat(machinePoolName, ":", nodeState)
| summarize count() by PreciseTimeStamp, machinePoolName
```

**Params:** `{starttime}`, `{endtime}`, `{cluster}`

**Signal filters seen in KQL:** `nodeState == "Unhealthy"`

---

### Quyry HolmesGoalStateManagerEvent

_Widget purpose:_ HolmesGoalStateManagerEvent

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Fabric / Tenant > Fabric / Compute Manager > Live Migration > HolmesGoalStateManagerEvent`

```kusto
HolmesGoalStateManagerEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where containerId == queryContainerId
| project PreciseTimeStamp, containerId, nodeId, actionType, message
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`

---

### Query LiveMigrationSessionCompleteLog

_Widget purpose:_ LiveMigrationSessionCompleteLog 

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Fabric / Tenant > Fabric / Compute Manager > Live Migration > LiveMigrationSessionCompleteLog `

```kusto
LiveMigrationSessionCompleteLog
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where sourceContainerId== queryContainerId
| project PreciseTimeStamp, triggerType, sessionId, elapsedTime, reason, message, sourceContainerId, sourceNodeId, destinationContainerId, destinationNodeId
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`

---

### Query LiveMigrationSessionStatusEventLog

_Widget purpose:_ LiveMigrationSessionStatusEventLog

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Fabric / Tenant > Fabric / Compute Manager > Live Migration > LiveMigrationSessionStatusEventLog`

```kusto
LiveMigrationSessionStatusEventLog
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where sourceContainerId== queryContainerId
| project PreciseTimeStamp,sessionId, sourceContainerId, destinationContainerId, type, state, message
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`

---

### Query TMMgmtNodeEventsEtwTable

_Widget purpose:_ Node Management Events from TMMgmtNodeEventsEtwTable

Cluster: `azcsupfollower` · Database: `azurecm` · Type: `Table`
Source panel: `Fabric / Tenant > Fabric / Compute Manager > Node Management > Node Management > Node Management Events from TMMgmtNodeEventsEtwTable`

```kusto
cluster("azcsupfollower").database("AzureCM").TMMgmtNodeEventsEtwTable
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where NodeId == queryNodeId
| where queryCheckContainerOnly != true or Message contains queryContainerId  
| project  PreciseTimeStamp, Message, RoleInstance 
| extend level = case( 
    Message contains "faultInfo changed", "error", 
    Message contains "Setting node Fault", "error", 
    Message contains "repair request", "warning", 
    Message ==  "Out of goal state", "warning",
    Message contains "Reason to regenerate CCF for container", "warning",
    Message contains "->", "warning",    
    "info")
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{queryContainerId}`, `{queryCheckContainerOnly}`

---

### Query TMMgmtNodeTraceEtwTable

_Widget purpose:_ TMMgmtNodeTraceEtwTable

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Fabric / Tenant > Fabric / Compute Manager > Node Management > Node Management > TMMgmtNodeTraceEtwTable`

```kusto
TMMgmtNodeTraceEtwTable
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where BladeID == queryNodeId
| where Message != "Runtime package image is deployed on the node by RdAgentUpdater/Pf"
| project PreciseTimeStamp, Message, ActivityId
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `Message != "Runtime package image is deployed on the node by RdAgentUpdater/Pf"`

---

### Tenant Scheduled Events

Cluster: `azpe` · Database: `azpe` · Type: `Timeline`
Source panel: `Fabric / Tenant > Fabric / Compute Manager > Scheduled Events`

```kusto
cluster("azpe.kusto.windows.net").database("azpe").AzPEWorkflowEvent 
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where EntityId == queryTenantName    
| extend impactedInstances = tostring((parse_json(WorkflowEventData).Containers))
| project StartTime = PreciseTimeStamp,  impactedInstances, WorkflowInstanceGuid, WorkflowType, WorkflowEventType, WorkflowId, WorkflowEventData
//| project StartTime = PreciseTimeStamp, AzPEWorkflowId, WorkflowType, impactedInstances, WorkflowEventType, EventId, TenantManagementJobMessage, WorkflowEventData 
| extend Content = strcat (WorkflowType, " - ", WorkflowEventType), Health = iif (impactedInstances contains queryInstanceName, "Degraded", "Neutral")
| order by StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`, `{queryInstanceName}`

---

### Scheduled Events Enablement Status

Cluster: `azpe` · Database: `azpe` · Type: `Timeline`
Source panel: `Fabric / Tenant > Fabric / Compute Manager > Scheduled Events`

```kusto
let peSettings = (cluster("azpe").database("azpe").AzPETenantSettingsSnapshot
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where TenantName == queryTenantName
| where Name == "IsMREnabledForAllRoles"
| project PreciseTimeStamp, enabled = Value);
let countPeSettings=toscalar(peSettings | count);
let fcTenantSettings = (cluster("azurecm").database("AzureCM").LogTenantOverridableSettingsSnapshot 
| where countPeSettings == 0
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where tenantName == queryTenantName
| where name == "IsMREnabledForAllRoles"
| project PreciseTimeStamp, enabled = value);
union peSettings, fcTenantSettings
| order by PreciseTimeStamp asc
| extend StartTime = PreciseTimeStamp
| extend flag = case (enabled <> prev(enabled), "changed", "")
| where flag <> ""
| extend EndTime = case (isnotempty(next(StartTime)), next(StartTime), queryTo)
| extend Content = iif (enabled == "True", "Enabled", "Not Enabled")
| extend Health = case(Content == "Enabled", "Health", "Neutral")
| project StartTime, EndTime, Health, Content
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

**Signal filters seen in KQL:** `Name == "IsMREnabledForAllRoles"`

---

### TMMgmtTenantManagementJobInfoEtwTable

_Widget purpose:_ Events in TMMgmtTenantManagementJobInfoEtwTable

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Fabric / Tenant > Fabric / Compute Manager > Scheduled Events > Events in TMMgmtTenantManagementJobInfoEtwTable`

```kusto
TMMgmtTenantManagementJobInfoEtwTable
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where TenantName == queryTenantName
| project PreciseTimeStamp, Tenant, Context, JobID, JobType, JobStatus, Message 
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

### Query Tenant in AzPEWorkflowEvent

_Widget purpose:_ Scheduled Events in AzPEWorkflowEvent

Cluster: `azpe` · Database: `azpe` · Type: `Table`
Source panel: `Fabric / Tenant > Fabric / Compute Manager > Scheduled Events > Scheduled Events in AzPEWorkflowEvent`

```kusto
AzPEWorkflowEvent
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where EntityId == queryTenantName
| project PreciseTimeStamp, WorkflowId, WorkflowType, WorkflowEventType, WorkflowEventData, WorkflowInstanceGuid
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

### Query AzSMServiceHealingResultEvents

_Widget purpose:_ AzSMServiceHealingResultEvents

Cluster: `accp.centralus` · Database: `AZSM` · Type: `Table`
Source panel: `Fabric / Tenant > Fabric / Compute Manager > Service Healing > AzSM Service Healing > AzSMServiceHealingResultEvents`

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

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

### Query AzSMServiceHealingStepResultEvents

_Widget purpose:_ AzSMServiceHealingStepResultEvents

Cluster: `accp.centralus` · Database: `AZSM` · Type: `Table`
Source panel: `Fabric / Tenant > Fabric / Compute Manager > Service Healing > AzSM Service Healing > AzSMServiceHealingStepResultEvents`

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

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

### Query AzSMServiceHealingTriggerEvents

_Widget purpose:_ AzSMServiceHealingTriggerEvents

Cluster: `accp.centralus` · Database: `AZSM` · Type: `Table`
Source panel: `Fabric / Tenant > Fabric / Compute Manager > Service Healing > AzSM Service Healing > AzSMServiceHealingTriggerEvents`

```kusto
AzSMServiceHealingTriggerEvents
| where PreciseTimeStamp between(queryFrom..queryTo)
| where tenantName =~ queryTenantName
| order by PreciseTimeStamp asc
| summarize FirstSeen = min(PreciseTimeStamp), LastSeen = max(PreciseTimeStamp),triggerIdList = make_list(triggerId) by ContainerId = triggerObjectId, triggerType, faultCode, faultReason, migrationRequestDetails 
| order by FirstSeen asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

### Query ServiceHealingTenantStatusEtwTable

_Widget purpose:_ ServiceHealingTenantStatusEtwTable

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Fabric / Tenant > Fabric / Compute Manager > Service Healing > TM Service Healing > ServiceHealingTenantStatusEtwTable`

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

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Fabric / Tenant > Fabric / Compute Manager > Service Healing > TM Service Healing > ServiceHealingTriggerEtwTable`

```kusto
ServiceHealingTriggerEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where TenantName == queryTenantName
| project PreciseTimeStamp, Tenant, TriggerId, TriggerType, TriggerObjectId, FaultCode, FaultReason, FaultInfoCorrelationGuid, AffectedUpdateDomain, RoleInstanceName
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

### Query AzSMTenantEvents

_Widget purpose:_ AzSMTenantEvents

Cluster: `accp.centralus` · Database: `AZSM` · Type: `Table`
Source panel: `Fabric / Tenant > Fabric / Compute Manager > Tenant Management > Tenant Management > AzSMTenantEvents`

```kusto
AzSMTenantEvents
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where tenantName == queryTenantName
| project PreciseTimeStamp, tenantName, Cluster, message
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

### Query AzSMTenantStatemachineEvents

_Widget purpose:_ AzSMTenantStatemachineEvents

Cluster: `accp.centralus` · Database: `AZSM` · Type: `Table`
Source panel: `Fabric / Tenant > Fabric / Compute Manager > Tenant Management > Tenant Management > AzSMTenantStatemachineEvents`

```kusto
AzSMTenantStatemachineEvents
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where tenantName == queryTenantName
| project PreciseTimeStamp, Tenant, stateMachineState, message
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---

### Query TMMgmtTenantEventsEtwTable

_Widget purpose:_ Tenant Management Events from TMMgmtTenantEventsEtwTable

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Fabric / Tenant > Fabric / Compute Manager > Tenant Management > Tenant Management > Tenant Management Events from TMMgmtTenantEventsEtwTable`

```kusto
cluster("azcsupfollower").database("AzureCM").TMMgmtTenantEventsEtwTable
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where TenantName == queryTenantName
| project PreciseTimeStamp,RoleInstance, Message
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---
