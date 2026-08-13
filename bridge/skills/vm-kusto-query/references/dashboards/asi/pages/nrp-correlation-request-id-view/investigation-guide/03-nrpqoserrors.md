# NRPQosErrors

> Source: **NRP - CorrelationRequestIdView** dashboard, chapter **NRPQosErrors** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### qos_errs

_Widget purpose:_ NRPQosErrors

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `NRPQosErrors`

```kusto
let qos_errs=QosEtwEvent
| where TIMESTAMP between(queryFrom..queryTo) and isnotempty(coalesce(subscriptionId, correlationId, resourceGroupName))
| where region=='all' or Region==region
| where isempty(subscriptionId) or SubscriptionId==subscriptionId
| where isempty(correlationId) or CorrelationRequestId==correlationId
| where isempty(resourceGroupName) or ResourceGroup==resourceGroupName
| where ignoreSuccess==false or Success==False
| extend RoleInstancePid=strcat(RoleInstance, '|', Pid),
         Resource=strcat(ResourceGroup, '|', ResourceName)
| summarize RoleInstancePid=strcat_array(array_sort_asc(make_set(RoleInstancePid)), ','), 
            dcount(CorrelationRequestId), 
            dcount(OperationId), 
            dcount(Resource), 
            Resources=make_set(Resource, 5), 
            max(TIMESTAMP),
            take_any(ErrorDetails) 
        by Table="QosEtwEvent", StackTrace, OperationName, UserError, ErrorCode;
let frontend_errs=FrontendOperationEtwEvent
| where TIMESTAMP between(queryFrom..queryTo) and isnotempty(coalesce(subscriptionId, correlationId))
| where region=='all' or Region==region
| where isempty(subscriptionId) or SubscriptionId==subscriptionId
| where isempty(correlationId) or CorrelationRequestId==correlationId
| where isempty(resourceGroupName) or ResourceGroup==resourceGroupName
| where Level<=2
| extend RoleInstancePid=strcat(RoleInstance, '|', Pid),
         Resource=strcat(ResourceGroup,'|', ResourceName)
| summarize RoleInstancePid=strcat_array(array_sort_asc(make_set(RoleInstancePid)), ','), dcount(CorrelationRequestId), dcount(OperationId), dcount(Resource), Resources=make_set(Resource, 5), max(TIMESTAMP),  take_any(ErrorDetails=Message) by Table="FrontendOperationEtwEvent", OperationName, EventCode;
qos_errs| union frontend_errs
| extend Resources=strcat('n=', dcount_Resource, '\n', strcat_array(Resources, '\n'))
| sort by OperationName, Table
```

**Params:** `{queryFrom}`, `{queryTo}`, `{correlationId}`, `{subscriptionId}`, `{region}`, `{resourceGroupName}`, `{ignoreSuccess}`

**Signal filters seen in KQL:** `region == "all"`

---
