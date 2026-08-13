# Live Migration

> Source: **EEE RDOS — WF Unexpected Restart** dashboard, chapter **Live Migration** (19 queries across 15 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## AirLiveMigrationEvents

### AirLiveMigrationEventsL30d

Cluster: `vmainsight.kusto.windows.net` · Database: `Air` · Type: `Table`
Source panel: `Live Migration > AirLiveMigrationEvents`

```kusto
AirLiveMigrationEvents
| where EventTime >= ago(30d) and RoleInstanceName contains queryVMName and SubscriptionId == querySubscriptionid
| project EventTime, Cluster, RCALevel1, SessionId, ObjectId, NodeId, RoleInstanceName, Customer, ImpactingFailureReason, ImpactingFailureDiagnostics
```

**Params:** `{querySubscriptionid}`, `{queryVMName}`

---

## Check LM Disabled for Sub

### HolmesSubscriptionMetadataEvents

Cluster: `azurecm` · Database: `azurecm` · Type: `Table`
Source panel: `Live Migration > Check LM Disabled for Sub`

```kusto
HolmesSubscriptionMetadataEvents
| where PreciseTimeStamp between (queryFrom..queryTo) and subscriptionGUID == query_sub
| summarize arg_max(PreciseTimeStamp, *) by containerId
| summarize dcount(containerId) by subscriptionGUID, nonLiveMigratable
| project subscriptionGUID, nonLiveMigratable
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_sub}`

---

## Holmes Events

### HolmesEvents

Cluster: `azcore.centralus.kusto.windows.net` · Database: `AzureCP` · Type: `Table`
Source panel: `Live Migration > Holmes Events > Especial case: Triggertype PlannedMaintenance > HolmesEvents`

```kusto
HolmesGoalStateManagerEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where containerId == queryContainerId
| where message startswith "Triggering Holmes action"
| parse message with * "TriggerType:" triggerType:string ";" * "Deadline:" deadline:datetime "called from serviceName" serviceName:string " evaluatorName" evaluatorName:string
| project PreciseTimeStamp, containerId, nodeId, actionType,triggerType, deadline,serviceName, evaluatorName, message
| extend Content = actionType
| extend Health = "Degraded"
| extend StartTime = PreciseTimeStamp
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`

**Signal filters seen in KQL:** `message startswith "Triggering Holmes action"`

---

### HolmesRHMNodeVacateStatusEvent

Cluster: `azurecm` · Database: `AzureCM` · Type: `Table`
Source panel: `Live Migration > Holmes Events > Especial case: Triggertype PlannedMaintenance > HolmesRHMNodeVacateStatusEvent`

```kusto
HolmesRHMNodeVacateStatusEvent
| where PreciseTimeStamp between (queryFrom .. datetime_add('hour',24,queryTo))
| where targetNodeId contains queryNodeId
| extend VacateNodeRequestId= parse_json(nodeMigrationGoalState)['VacateNodeRequestId']
| summarize max(PreciseTimeStamp) by targetNodeId, tostring(VacateNodeRequestId)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### HolmesGoalStateManagerEvent

Cluster: `azcore.centralus` · Database: `AzureCP` · Type: `Table`
Source panel: `Live Migration > Holmes Events > LiveMigrationSessionValidationCriticalEventLog > HolmesGoalStateManagerEvent`

```kusto
HolmesGoalStateManagerEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where * contains queryContainerId
| where message has "Triggering Holmes action"
| project PreciseTimeStamp, containerId, nodeId, actionType, serviceName, evaluatorName, message
| extend StartTime = PreciseTimeStamp
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`

**Signal filters seen in KQL:** `message has "Triggering Holmes action"`

---

### LiveMigrationSessionValidationCriticalEventLog-cl

_Widget purpose:_ Provides validation information at the time of triggering Live Migration

Cluster: `azcore.centralus` · Database: `Fc` · Type: `Table`
Source panel: `Live Migration > Holmes Events > LiveMigrationSessionValidationCriticalEventLog > Provides validation information at the time of triggering Live Migration`

```kusto
LiveMigrationSessionValidationCriticalEventLog
| where TIMESTAMP between (queryFrom .. queryTo)
| where srcContainerId contains containerId
| project PreciseTimeStamp, exceptionType, exception
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`

---

## LiveMigration Failures

### LmFailures

Cluster: `vmainsight.kusto.windows.net` · Database: `Air` · Type: `Single` · Widget: `Row`
Source panel: `Live Migration > LiveMigration Failures`

```kusto
LiveMigrationFailureEvents
| where EventTime between ((queryFrom) ..(queryTo)) and SubscriptionId == query_SubscriptionId
| extend SrcContainer= ObjectId
| project EventTime,BlackoutDurationInSec = round(BlackoutDurationInSec, 2),RoleInstanceName,RCALevel1,RCALevel2, EvaluatorName, SrcContainer, Customer
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_SubscriptionId}`

---

### LiveMigrationFailures

_Widget purpose:_ LM failures by Subscription

Cluster: `vmainsight.kusto.windows.net` · Database: `Air` · Type: `Table`
Source panel: `Live Migration > LiveMigration Failures > LM failures by Subscription`

```kusto
LiveMigrationFailureEvents
| where EventTime between (queryFrom .. queryTo) and SubscriptionId == query_subscriptionId
| extend SrcContainer= ObjectId
| project EventTime,BlackoutDurationInSec = round(BlackoutDurationInSec, 2),RoleInstanceName,RCALevel1,RCALevel2, EvaluatorName, SrcContainer, Customer
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_subscriptionId}`

---

## LiveMigrationContainerDetails-New

### LiveMigrationEvents

Cluster: `Vmainsight` · Database: `Air` · Type: `Table`
Source panel: `Live Migration > LiveMigrationContainerDetails-New`

```kusto
let ContainerIds = split(queryContainerList,",");
union(
AirLiveMigrationEvents
| where EventTime >=queryStartTime and EventTime < queryEndTime
| where (ObjectId in (ContainerIds) or VirtualMachineUniqueId == queryVMId)
| project SessionId,LMStartTime=todatetime(Diagnostics.LiveMigrationStartTime),LMEndTime = EventTime,
IsLMSuccessful = true,SourceContainerId = ObjectId, DestinationContainerId = tostring(Diagnostics.DestinationContainerId),TenantName,RoleInstanceName,
Scenario = RCALevel1,Sub_Scenario = EvaluatorName,BlackoutDurationInSec = round(Duration/1s,2),
BlackoutStartTime = NetworkReadyTime - Duration, BlackoutEndTime = NetworkReadyTime,VirtualMachineUniqueId,SubscriptionId,Customer,
FailureReason = "", ImpactingFailure = IsImpactingFailure,ImpactingFailureReason,FailureOwnerTeam = EscalateTo
), 
(
LiveMigrationFailureEvents
| where EventTime >=queryStartTime and EventTime < queryEndTime
| where (ObjectId == queryContainerId or VirtualMachineUniqueId == queryVMId)
| project SessionId = tostring(Diagnostics.SessionId),LMStartTime=todatetime(Diagnostics.LiveMigrationStartTime),LMEndTime = EventTime,
IsLMSuccessful = false,SourceContainerId = ObjectId, DestinationContainerId = tostring(Diagnostics.DestinationContainerId),TenantName,RoleInstanceName,
Scenario = trim("LiveMigrationFailure:", RCALevel1), Sub_Scenario = EvaluatorName,
BlackoutDurationInSec, BlackoutStartTime,BlackoutEndTime,VirtualMachineUniqueId,SubscriptionId,Customer,
FailureReason=RCALevel2,ImpactingFailure = IsImpactingFailure, ImpactingFailureReason,FailureOwnerTeam = EscalateTo
)
```

**Params:** `{queryContainerId}`, `{queryStartTime}`, `{queryEndTime}`, `{querySubscriptionId}`, `{queryVMId}`, `{queryContainerList}`

---

## LiveMigrationContainerDetailsEventLog

### LiveMigrationContainerDetailsEventLog DS

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Live Migration > LiveMigrationContainerDetailsEventLog`

```kusto
LiveMigrationContainerDetailsEventLog
| where destinationContainerId == query_ContainerId or sourceContainerId == query_ContainerId 
| where PreciseTimeStamp > query_BeginTime
| where PreciseTimeStamp < query_EndTime
| project sessionId
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_ContainerId}`

---

## LiveMigrations for Subscription

### AirLiveMigrationEvents DS

Cluster: `vmainsight` · Database: `Air` · Type: `Table`
Source panel: `Live Migration > LiveMigrations for Subscription`

```kusto
AirLiveMigrationEvents
| where EventTime >= ago(30d) and SubscriptionId == querySubscriptionId
| extend BlackoutInSec = round(Duration/1s, 2)
| summarize LM_count = count(), percentiles(BlackoutInSec, 50, 90, 99, 99.9) by SubscriptionId, RCALevel1, NodeId, RoleInstanceName, EventTime, Customer
```

**Params:** `{querySubscriptionId}`

---

## LiveMigrationSessionCompleteLog

### LiveMigrationSessionCompleteLog DS

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Live Migration > LiveMigrationSessionCompleteLog`

```kusto
LiveMigrationContainerDetailsEventLog
| where destinationContainerId == query_ContainerId or sourceContainerId == query_ContainerId 
| where PreciseTimeStamp > query_BeginTime
| where PreciseTimeStamp < query_EndTime
| project sessionId
| join kind=inner    
(LiveMigrationSessionCompleteLog  
| where PreciseTimeStamp > query_BeginTime
| where PreciseTimeStamp < query_EndTime
| project PreciseTimeStamp, sessionId, status, elapsedTime, reason ,message, subscriptionId, vmUniqueId) on $left.sessionId == $right.sessionId
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_ContainerId}`

---

## LiveMigrationSessionCreatedLog

### LiveMigrationSessionCreatedLog DS

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Live Migration > LiveMigrationSessionCreatedLog`

```kusto
LiveMigrationContainerDetailsEventLog
| where destinationContainerId == query_ContainerId or sourceContainerId == query_ContainerId 
| where PreciseTimeStamp > query_BeginTime
| where PreciseTimeStamp < query_EndTime
| project sessionId
| join kind=inner    
(LiveMigrationSessionCreatedLog
| where PreciseTimeStamp > query_BeginTime
| where PreciseTimeStamp < query_EndTime
| project PreciseTimeStamp, sessionId, traceCode, migrationConstraint, message, subscriptionId, roleInstanceName, virtualMachineUniqueId) on $left.sessionId == $right.sessionId
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_ContainerId}`

---

## LiveMigrationSessionCriticalLog

### LiveMigrationSessionCriticalLog DS

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Live Migration > LiveMigrationSessionCriticalLog`

```kusto
LiveMigrationContainerDetailsEventLog
| where destinationContainerId == query_ContainerId or sourceContainerId == query_ContainerId 
| where PreciseTimeStamp > query_BeginTime
| where PreciseTimeStamp < query_EndTime
| project sessionId
| join kind=inner    
(LiveMigrationSessionCriticalLog
| where PreciseTimeStamp > query_BeginTime
| where PreciseTimeStamp < query_EndTime
| project PreciseTimeStamp, sessionId, exceptionType , exception, lmContext) on $left.sessionId == $right.sessionId
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_ContainerId}`

---

## LiveMigrationSessionStatusEventLog

### LiveMigrationSessionStatusEventLog DS

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Live Migration > LiveMigrationSessionStatusEventLog`

```kusto
LiveMigrationContainerDetailsEventLog
| where destinationContainerId == query_ContainerId or sourceContainerId == query_ContainerId 
| where PreciseTimeStamp > query_BeginTime
| where PreciseTimeStamp < query_EndTime
| project sessionId
| join kind=inner    
(LiveMigrationSessionStatusEventLog
| where PreciseTimeStamp > query_BeginTime
| where PreciseTimeStamp < query_EndTime
| project PreciseTimeStamp, ['state'] , message, subscriptionId, vmUniqueId, sessionId) on $left.sessionId == $right.sessionId
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_ContainerId}`

---

## LiveMigrationSessionStatusEventLog_Errors

### LiveMigrationSessionStatusEventLog_Error DS

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Table`
Source panel: `Live Migration > LiveMigrationSessionStatusEventLog_Errors`

```kusto
LiveMigrationContainerDetailsEventLog
| where destinationContainerId == query_ContainerId or sourceContainerId == query_ContainerId 
| where PreciseTimeStamp > query_BeginTime
| where PreciseTimeStamp < query_EndTime
| project sessionId
| join kind=inner    
(LiveMigrationSessionStatusEventLog
| where PreciseTimeStamp > query_BeginTime
| where PreciseTimeStamp < query_EndTime
| where ['type'] == "Error"
| project PreciseTimeStamp, ['state'] , message, subscriptionId, vmUniqueId, sessionId) on $left.sessionId == $right.sessionId
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_ContainerId}`

---

## LiveMigrationSubscriptionDetails-New

### LiveMigrationEventsOnSubscription

Cluster: `Vmainsight` · Database: `Air` · Type: `Table`
Source panel: `Live Migration > LiveMigrationSubscriptionDetails-New`

```kusto
union(
AirLiveMigrationEvents
| where EventTime >= queryStartTime and EventTime < queryEndTime
| where SubscriptionId == querySubscriptionId
| project VirtualMachineUniqueId,SubscriptionId,SessionId,Scenario = RCALevel1,BlackoutDurationInSec = round(Duration/1s,2),Sub_Scenario = EvaluatorName
| extend status = "Completed"
),
(
LiveMigrationFailureEvents
| where EventTime >= queryStartTime and EventTime < queryEndTime
| where SubscriptionId == querySubscriptionId
| project VirtualMachineUniqueId,SubscriptionId,Scenario = trim("LiveMigrationFailure:", RCALevel1),BlackoutDurationInSec,Sub_Scenario = EvaluatorName
| extend status = "Failed"
)
| summarize TotalLMs = dcount(SessionId), TotalSuccessfulLMs = dcountif(SessionId,status == "Completed"), percentiles(BlackoutDurationInSec,50,90,99,99.5) by SubscriptionId,Scenario,Sub_Scenario
| project SubscriptionId, Scenario, Sub_Scenario, TotalLMs,TotalSuccessfulLMs, Blackout_P50 = round(percentile_BlackoutDurationInSec_50,2),Blackout_P90 = round(percentile_BlackoutDurationInSec_90,2),
Blackout_P99 = round(percentile_BlackoutDurationInSec_99,2),Blackout_P99_5 = round(percentile_BlackoutDurationInSec_99_5,2)
```

**Params:** `{querySubscriptionId}`, `{queryStartTime}`, `{queryEndTime}`

---

## LMSupportCaseCorrelation-New

### LMSupportCases

Cluster: `https://supportrptwus3prod.westus3.kusto.windows.net` · Database: `AceHubSupportData` · Type: `Table`
Source panel: `Live Migration > LMSupportCaseCorrelation-New`

```kusto
let MCCSubs = cluster('Vmainsight').database('vmadb').HighRiskWorkloads 
| distinct SubscriptionID;
cluster('supportrptwus3prod.westus3').database('AceHubSupportData').MSaaSSupportCases
| where todatetime(CaseCreatedOn) >= queryBeginTime and todatetime(CaseCreatedOn) <= queryEndTime
and SubscriptionId == querySubscriptionId and CaseNumber == queryCaseNumber
| distinct SupportTopic, SubscriptionId, Title, CaseNumber, CaseCreatedOn, ResourceId, ProblemStartTime = todatetime(ProblemStartTime), IncidentId
| extend IsMCC = SubscriptionId in (MCCSubs)
| extend roleInstanceName = tostring(split(ResourceId, "/")[-1])
| join kind=leftouter (
cluster('Azurecm').database('AzureCM').LiveMigrationSessionCreatedLog
| where PreciseTimeStamp >= queryBeginTime and PreciseTimeStamp <= queryEndTime
| project LMStartTime = PreciseTimeStamp, roleInstanceName = trim_start("_", roleInstanceName), subscriptionId, sessionId
) on roleInstanceName, $left.SubscriptionId == $right.subscriptionId
| join kind=leftouter (
cluster('Azurecm').database('AzureCM').LiveMigrationSessionCompleteLog
| where PreciseTimeStamp >= queryBeginTime and PreciseTimeStamp <= queryEndTime
| project LMEndTime = PreciseTimeStamp,  sessionId,vmUniqueId
) on sessionId
| where ProblemStartTime between (LMStartTime .. LMEndTime) or (ProblemStartTime - LMEndTime) between (0m .. 30m)
| summarize arg_max(LMStartTime, *) by CaseNumber
| project CaseNumber, CaseCreatedOn = todatetime(CaseCreatedOn), IsMCC, SubscriptionId, roleInstanceName, LMStartTime, sessionId, VirtualMachineUniqueId = vmUniqueId
| join kind=leftouter (
cluster('Vmainsight').database('Air').AirLiveMigrationEvents
| where EventTime >= queryBeginTime and EventTime <= queryEndTime
| project EventTime, SessionId, ImpactingFailureReason, BlackoutInSec = round(Duration/1s, 2), IsLMSuccess = 1, Customer, VMSize
) on $left.sessionId == $right.SessionId
| join kind=leftouter (
cluster('Vmainsight').database('Air').LiveMigrationFailureEvents
| where EventTime >= queryBeginTime and EventTime <= queryEndTime
| extend sessionId = tostring(parse_json(Diagnostics)["SessionId"]), BlackoutInSec = round(BlackoutDurationInSec, 2)
| project EventTime, sessionId, ImpactingFailureReason, BlackoutInSec, RCALevel2, Customer, VMSize
) on sessionId
| extend BlackoutInSec = coalesce(BlackoutInSec, BlackoutInSec1)
| extend ImpactingFailureReason = coalesce(ImpactingFailureReason, ImpactingFailureReason1)
| extend Customer = coalesce(Customer, Customer1)
| extend VMSize = coalesce(VMSize, VMSize1)
| extend IsLMSuccess = coalesce(IsLMSuccess, 0)
| extend LMEndTime = coalesce(EventTime, EventTime1)
| project CaseNumber, Customer, IsMCC, SubscriptionId,VirtualMachineUniqueId, LMStartTime, LMEndTime, sessionId, IsLMSuccess, BlackoutInSec, FailureReason = RCALevel2, ImpactingFailureReason
```

**Params:** `{queryBeginTime}`, `{queryEndTime}`, `{querySubscriptionId}`, `{queryCaseNumber}`

---

## VM eligible for LM

### LmApplicableVms

Cluster: `moseisley.kusto.windows.net` · Database: `Air` · Type: `Table`
Source panel: `Live Migration > VM eligible for LM > LmApplicableVms`

```kusto
let LatestSnapshotTime = 
toscalar (
    LmApplicableVms
    | summarize max(SnapshotTime)
);
LmApplicableVms
| where ContainerId == queryContainerId | as Source
| where SnapshotTime >= LatestSnapshotTime-7d
| extend AllColumns = pack_all()
| mv-expand ColumnName = bag_keys(AllColumns)
| extend ColumnValue = tostring(AllColumns[tostring(ColumnName)])
| where ColumnValue == "true"
| summarize LMInEligibleReasons = make_list(ColumnName) by SnapshotTime, ContainerId, IsLmDisabledTenantVm, IsLmEligible
| extend LMInEligibleReasons = iff(IsLmEligible != true, LMInEligibleReasons, "")
| project SnapshotTime, ContainerId, IsLmDisabledTenantVm, IsLmEligible, LMInEligibleReasons
| sort by SnapshotTime asc
```

**Params:** `{queryContainerId}`

**Signal filters seen in KQL:** `ColumnValue == "true"`

---
