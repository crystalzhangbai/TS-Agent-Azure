# Activity

> Source: **NRP - CorrelationRequestIdView** dashboard, chapter **Activity** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### correl_activity

_Widget purpose:_ Activity

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Activity`

```kusto
let time_span=10m;
let starttime=queryFrom;
let endtime=queryTo;
let resourceGroup_query=iff(isempty(resourceGroup_query_) or resourceGroup_query_ startswith("Test"), '', resourceGroup_query_);
//
let activity=FrontendOperationEtwEvent
| where TIMESTAMP between(starttime..endtime)
        | where region=='all' or Region==region
        | where SubscriptionId==subscriptionId
        | where isempty(correllationId) or CorrelationRequestId==correllationId
        | where isempty(resourceGroup_query) or ResourceGroup contains resourceGroup_query
        | extend ERR= Level<=2 or Message contains "exception"
        | extend err_msg=iff(ERR, iff(isnotempty(EventCode), EventCode, substring(Message, 0, 40)), ''),
                timepoint=bin(TIMESTAMP, time_span)
        | summarize n=count(),
                    Lock_actvity=countif(EventCode contains "lock"),
                    err=countif(ERR)
             by CorrelationRequestId, OperationId, timepoint, Level, RoleInstance, Pid
        | summarize 
                    activity=sum(n),
                    dcount(CorrelationRequestId),
                    dcount(OperationId),
                    Lock_actvity=sum(Lock_actvity),
                    err=sum(err),
                    Lvl2=sumif(n,Level==2),
                    Lvl4=sumif(n,Level==4),
                    Lvl8=sumif(n,Level==8)
             by timepoint, RoleInstance, Pid;
       let rrq=toscalar(activity| summarize count() by RoleInstance, Pid| top 1 by count_| project pack_all());
       let contentionrate=PerfCounterQuery_NRPCounter5m(starttime, endtime, role_instance_query=tostring(rrq.RoleInstance), countername_query="Contention Rate / sec", pid_query=tolong(rrq.Pid), time_span=time_span, CounterValueType="P90", ServiceTypes="GatewayService|Nrp.Frontend.Service|Nrp.RcFrontend.Service")
        | summarize ContentionRate=tolong(max(CounterValue)) by timepoint=bin(timepoint, time_span), label=strcat(RoleInstance, '|pid:', Pid)
        | where ContentionRate>0;
      activity 
      | project timepoint, label=strcat(RoleInstance, '|pid:', Pid), activity, dcount_OperationId, 
                 Lock_actvity, err, Lvl2, Lvl4, Lvl8
      | union contentionrate
      | project timepoint, label, ContentionRate,
                activity, dcount_OperationId, 
                 Lock_actvity, err, Lvl2, Lvl4
```

**Params:** `{queryFrom}`, `{queryTo}`, `{correllationId}`, `{subscriptionId}`, `{region}`, `{resourceGroup_query_}`

**Signal filters seen in KQL:** `region == "all"`

---
