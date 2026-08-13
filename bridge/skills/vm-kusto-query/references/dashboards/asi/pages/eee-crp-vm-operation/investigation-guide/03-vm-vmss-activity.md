# VM / VMSS Activity

> Source: **EEE CRP — VM Operation** dashboard, chapter **VM / VMSS Activity** (8 queries across 4 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## CRP Operation Log

### Component Call

_Widget purpose:_ Component Call History

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Table`
Source panel: `VM / VMSS Activity > CRP Operation Log > CRP Operation Log > Component Call History`

```kusto
cluster('azcrp.kusto.windows.net').database('crp_allprod').ComponentQoSEvent
| where PreciseTimeStamp between (starttime..endtime)
| where activityId == operationid
| project PreciseTimeStamp, activityId, componentName, operationName, operationResult, resultDetails, durationInMs, fabricCluster, fabricTenantName
| order by PreciseTimeStamp asc
```

**Params:** `{starttime}`, `{endtime}`, `{operationid}`

---

### CRP Context Operation

_Widget purpose:_ CRP Context Activity Log

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Table`
Source panel: `VM / VMSS Activity > CRP Operation Log > CRP Operation Log > CRP Context Activity Log`

```kusto
cluster('azcrp.kusto.windows.net').database('crp_allprod').ContextActivity
| where PreciseTimeStamp between (starttime .. endtime)
| where activityId == operationid
| project PreciseTimeStamp, traceLevel, traceCode, Tid, subscriptionId, activityId, message, callerName, lineNumber, sourceFile, RPTenant, goalSeekingActivityId, tenantId, Node
| project PreciseTimeStamp, traceLevel, Tid, activityId, message, callerName, lineNumber, sourceFile
| extend level = case (traceLevel == 1, "critical", 
    traceLevel == 2, "error", 
    traceLevel == 3, "warning", 
    "info")
| order by PreciseTimeStamp asc
```

**Params:** `{starttime}`, `{endtime}`, `{operationid}`

---

### Component Call

_Widget purpose:_ Operation Timeline

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Timeline`
Source panel: `VM / VMSS Activity > CRP Operation Log > CRP Operation Log > Operation Timeline`

```kusto
cluster('azcrp.kusto.windows.net').database('crp_allprod').ComponentQoSEvent
| where PreciseTimeStamp between (starttime..endtime)
| where activityId == operationid
| project PreciseTimeStamp, activityId, componentName, operationName, operationResult, resultDetails, durationInMs, fabricCluster, fabricTenantName
| extend StartTime = datetime_add('Millisecond', -toint(durationInMs), PreciseTimeStamp), EndTime = PreciseTimeStamp
| extend Health = case (operationResult == "Success", "Healthy", "Unhealthy")
| extend GroupBy = strcat(componentName, " : ", operationName), Content = operationName
| order by StartTime asc
```

**Params:** `{starttime}`, `{endtime}`, `{operationid}`

---

## NRP Operation Log

### NRP Operation Log

Cluster: `nrp` · Database: `mdsnrp` · Type: `Table`
Source panel: `VM / VMSS Activity > NRP Operation Log > NRP Operation Log > NRP Operation Log`

```kusto
cluster('nrp.kusto.windows.net').database('mdsnrp').FrontendOperationEtwEvent
| where PreciseTimeStamp between (starttime .. endtime)
| where InternalCorrelationId == crpoperationid
| project PreciseTimeStamp, Level, ResourceGroup, ResourceName, ResourceType, CorrelationRequestId, Message, HttpMethod, OperationName, OperationId
| order by PreciseTimeStamp asc
```

**Params:** `{starttime}`, `{endtime}`, `{crpoperationid}`

---

### NRP Operation Timeline

Cluster: `nrp` · Database: `mdsnrp` · Type: `Timeline`
Source panel: `VM / VMSS Activity > NRP Operation Log > NRP Operation Log > NRP Operation Timeline`

```kusto
cluster('nrp.kusto.windows.net').database('mdsnrp').QosEtwEvent
| where PreciseTimeStamp between (starttime .. endtime)
| where InternalCorrelationId == crpoperationid
| project PreciseTimeStamp, todatetime(StartTime), CorrelationRequestId, OperationId, OperationName, ResourceGroup, ResourceName, ResourceType, HttpMethod, Success, DurationInMilliseconds, ErrorCode, ErrorDetails
| extend EndTime = PreciseTimeStamp, GroupBy = OperationName, Content = ErrorCode
| extend Health = case (Success == 0, "Unhealthy", "Healthy")
| order by StartTime asc
```

**Params:** `{starttime}`, `{endtime}`, `{crpoperationid}`

---

## VM Allocation

### VM Allocation in CRP

_Widget purpose:_ VM Allocation

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Table`
Source panel: `VM / VMSS Activity > VM Allocation > VM Allocation > VM Allocation`

```kusto
let starttime_crp_allocator = toscalar(cluster('azcrp.kusto.windows.net').database('crp_allprod').ContextActivity
| where PreciseTimeStamp between( starttime .. endtime )
| where activityId == operationid
| where message contains "+ ComputeAllocatorService.AllocateCompute"
| project PreciseTimeStamp);
let endtime_crp_allocator = toscalar(cluster('azcrp.kusto.windows.net').database('crp_allprod').ContextActivity
| where PreciseTimeStamp between( starttime .. endtime )
| where activityId == operationid
| where message contains "- ComputeAllocatorService.AllocateCompute"
| project PreciseTimeStamp);
cluster('azcrp.kusto.windows.net').database('crp_allprod').ContextActivity
| where PreciseTimeStamp between( starttime_crp_allocator .. endtime_crp_allocator )
| where activityId == operationid
| project PreciseTimeStamp, traceLevel, traceCode, Tid, subscriptionId, activityId, message, callerName, lineNumber, sourceFile, RPTenant, goalSeekingActivityId, tenantId, Node
| project PreciseTimeStamp, traceLevel, Tid, activityId, message, callerName, lineNumber, sourceFile
| order by PreciseTimeStamp asc
| extend level = case (traceLevel == 1, "critical", 
    traceLevel == 2, "error", 
    traceLevel == 3, "warning", 
    "info")
```

**Params:** `{starttime}`, `{endtime}`, `{operationid}`

**Signal filters seen in KQL:** `message contains "+ ComputeAllocatorService.AllocateCompute"` · `message contains "- ComputeAllocatorService.AllocateCompute"`

---

## VMSS Goal Seeking (VMSS Only)

### VMSS Container Goal Seeking Timeline

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Timeline`
Source panel: `VM / VMSS Activity > VMSS Goal Seeking (VMSS Only) > VMSS Goal Seeking (VMSS Only) > VMSS Container Goal Seeking Timeline`

```kusto
cluster('azcrp.kusto.windows.net').database('crp_allprod').VmssVMGoalSeekingActivity
| where PreciseTimeStamp between (starttime .. endtime)
| where activityId == operationid
| project PreciseTimeStamp, traceLevel, Tid, activityId, message, vMName, goalStateResourceId
| order by vMName asc, PreciseTimeStamp asc
| extend StartTime = PreciseTimeStamp, Content = "", GroupBy = vMName, Health = "healthy"
| extend flag = case (prev(vMName) <> vMName, "start", 
    next(vMName) <> vMName, "end", "")
| where flag <> ""
| extend EndTime = case(next(flag) == "end", next(PreciseTimeStamp), PreciseTimeStamp)
| where flag <> "end"
| project StartTime, EndTime, Content, GroupBy, Health, activityId
```

**Params:** `{starttime}`, `{endtime}`, `{operationid}`

**Signal filters seen in KQL:** `flag <> "end"`

---

### VMSS Goal Seeking Operation

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Table`
Source panel: `VM / VMSS Activity > VMSS Goal Seeking (VMSS Only) > VMSS Goal Seeking (VMSS Only) > VMSS Goal Seeking Operation`

```kusto
cluster('azcrp.kusto.windows.net').database('crp_allprod').VmssVMGoalSeekingActivity
| where PreciseTimeStamp between (starttime .. endtime)
| where activityId == operationid
| project PreciseTimeStamp, traceLevel, Tid, activityId, message, vMName, goalStateResourceId
| order by PreciseTimeStamp asc
| extend level = case( traceLevel == 1, "critical", 
    traceLevel == 2, "error",
    traceLevel == 3, "warning",
    "info")
```

**Params:** `{starttime}`, `{endtime}`, `{operationid}`

---
