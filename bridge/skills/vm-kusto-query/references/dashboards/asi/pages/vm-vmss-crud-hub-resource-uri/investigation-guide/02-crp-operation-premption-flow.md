# CRP Operation Premption flow

> Source: **Resource URI** dashboard, chapter **CRP Operation Premption flow** (3 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### PreemptedOperations V2

Cluster: `azcore.centralus` · Database: `Crp` · Type: `Table`
Source panel: `CRP Operation Premption flow`

```kusto
let local_subscriptionId = split(ResURI,"/")[2];
let local_resourceGroupName = split(ResURI,"/")[4];
let local_resourceName = split(ResURI,"/")[8];
let local_vmssInstanceName = split(ResURI,"/")[10];
let opids = materialize(ApiQosEvent
| where PreciseTimeStamp between(queryFrom..2h)
| where tolower(subscriptionId) == tolower(local_subscriptionId) and operationName !contains "GET"
| where tolower(resourceGroupName) == tolower(local_resourceGroupName)
| where tolower(resourceName) startswith tolower(local_resourceName) or (isnotempty(tolower(local_vmssInstanceName)) and tolower(resourceName) startswith tolower(local_vmssInstanceName)));
let ctxact = materialize(ContextActivity
| where PreciseTimeStamp between(queryFrom..2h) and activityId in (opids | project operationId)
| where message has "is requesting preemption"  or message has "Not preempting current execution as it was preempted too many times." and message !has "`1" or message has "Execution preempted for" or message has "Switching activity-id to"
| project PreciseTimeStamp, activityId, message);
opids | join kind=inner ctxact on $left.operationId == $right.activityId
| parse message with * 'Activity ' ActivityIdWhichRequestedPreemption ' ' * 'Current preemption count is ' CurrentPreemptionCount '.'
| parse message with * 'Switching activity-id to ' SwitchedToActivityId
| distinct  StartTime=(PreciseTimeStamp-e2EDurationInMilliseconds * 1ms), EndTime=PreciseTimeStamp, resultCode, operationName, resourceGroupName, resourceName, correlationId, activityId, ActivityIdWhichRequestedPreemption, CurrentPreemptionCount,SwitchedToActivityId,  requestEntity, message
| order by StartTime asc
```

**Params:** `{queryFrom}`, `{ResURI}`

**Signal filters seen in KQL:** `message has "is requesting preemption"`

---

## CRP Operation Preemption Timeline

### Operations - StartTime

_Widget purpose:_ CRP Operation Preemption Timeline

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Timeline`
Source panel: `CRP Operation Premption flow > CRP Operation Preemption Timeline`

```kusto
let local_subscriptionId = tolower(split(ResURI,"/")[2]);
let local_resourceGroupName = split(ResURI,"/")[4];
let local_resourceName = split(ResURI,"/")[8];
let local_vmssInstanceName = split(ResURI,"/")[10];
let opids = materialize(ApiQosEvent
| where PreciseTimeStamp between(queryFrom..2h)
| where operationName !contains "GET"
| where subscriptionId == local_subscriptionId //and operationName == "VMScaleSetVMs.Start.POST"
| where tolower(resourceGroupName) == tolower(local_resourceGroupName)
| where tolower(resourceName) startswith tolower(local_resourceName) or (isnotempty(tolower(local_vmssInstanceName)) and tolower(resourceName) startswith tolower(local_vmssInstanceName)));
let ctxact = materialize(ContextActivity
| where PreciseTimeStamp between(queryFrom..2h) and activityId in (opids | project operationId)
| where message has "is requesting preemption"  or message has "Not preempting current execution as it was preempted too many times." and message !has "`1" or message has "Execution preempted for"  or message has "Switching activity-id to"
| project PreciseTimeStamp, activityId, message);
opids | join kind=inner ctxact on $left.operationId == $right.activityId
| parse message with * 'Activity ' ActivityIdWhichRequestedPreemption ' ' * 'Current preemption count is ' CurrentPreemptionCount '.'
| parse message with * 'Switching activity-id to ' SwitchedToActivityId
| summarize by StartTime=(PreciseTimeStamp-e2EDurationInMilliseconds * 1ms), EndTime=PreciseTimeStamp, Content=strcat(operationName,"/ActId:",activityId), activityId, operationName,ActivityIdWhichRequestedPreemption,SwitchedToActivityId
| where isnotempty(ActivityIdWhichRequestedPreemption) or isnotempty(SwitchedToActivityId)
| order by StartTime asc
| project StartTime, Content, operationName, activityId, ActivityIdWhichRequestedPreemption, SwitchedToActivityId
```

**Params:** `{queryFrom}`, `{ResURI}`

**Signal filters seen in KQL:** `message has "is requesting preemption"`

---

### Operations - Lifecycle until preemption

_Widget purpose:_ CRP Operation Preemption Timeline

Cluster: `azcore.centralus` · Database: `Crp` · Type: `Timeline`
Source panel: `CRP Operation Premption flow > CRP Operation Preemption Timeline`

```kusto
let local_subscriptionId = tolower(split(ResURI,"/")[2]);
let local_resourceGroupName = split(ResURI,"/")[4];
let local_resourceName = split(ResURI,"/")[8];
let local_vmssInstanceName = split(ResURI,"/")[10];
let opids = materialize(ApiQosEvent
| where PreciseTimeStamp between(queryFrom..2h)
| where operationName !contains "GET"
| where subscriptionId == local_subscriptionId //and operationName == "VMScaleSetVMs.Start.POST"
| where tolower(resourceGroupName) == tolower(local_resourceGroupName)
| where tolower(resourceName) startswith tolower(local_resourceName) or (isnotempty(tolower(local_vmssInstanceName)) and tolower(resourceName) startswith tolower(local_vmssInstanceName)));
let ctxact = materialize(ContextActivity
| where PreciseTimeStamp between(queryFrom..2h) and activityId in (opids | project operationId)
| where message has "is requesting preemption"  or message has "Not preempting current execution as it was preempted too many times." and message !has "`1" or message has "Execution preempted for" or message has "Switching activity-id to"
| project PreciseTimeStamp, activityId, message);
opids | join kind=inner ctxact on $left.operationId == $right.activityId
| parse message with * 'Activity ' ActivityIdWhichRequestedPreemption ' ' * 'Current preemption count is ' CurrentPreemptionCount '.'
| parse message with * 'Switching activity-id to ' SwitchedToActivityId
| summarize by StartTime=(PreciseTimeStamp-e2EDurationInMilliseconds * 1ms), EndTime=PreciseTimeStamp, Content=strcat(operationName,"/ActId:",activityId), activityId, operationName,ActivityIdWhichRequestedPreemption,SwitchedToActivityId
| where isnotempty(ActivityIdWhichRequestedPreemption) or isnotempty(SwitchedToActivityId)
| order by StartTime asc
| project StartTime, EndTime, Content, operationName, activityId, ActivityIdWhichRequestedPreemption,SwitchedToActivityId
```

**Params:** `{queryFrom}`, `{ResURI}`

**Signal filters seen in KQL:** `message has "is requesting preemption"`

---
