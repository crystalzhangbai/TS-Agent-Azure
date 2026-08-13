# correlId

> Source: **NRP - CorrelationRequestIdView** dashboard, chapter **correlId** (7 queries across 7 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### correlId

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Timeline`
Source panel: `correlId`

```kusto
let qos_errs=QosEtwEvent
        | where TIMESTAMP between(queryFrom..queryTo)
        | where (region=="all" or isempty(region)) or Region ==region
        | where Success==false
        | where isempty(subscriptionId) or SubscriptionId ==subscriptionId
        | where isempty(correlationId) or CorrelationRequestId==correlationId
        | where isempty(operationId) or OperationId==operationId
        | where (isempty(resourceGroupName_) or resourceGroupName_ startswith "Test") or ResourceGroup ==resourceGroupName_
        | summarize qos_err_count=countif(Success==false), UserError=strcat_array(make_set(UserError), '|'), ErrorCodes=make_set_if(ErrorCode, isnotempty(ErrorCode)) by CorrelationRequestId;
FrontendOperationEtwEvent
| union  withsource=TableName FrontendReadOperationEtwEvent
| where Tables=='all' or TableName==Tables
        | where TIMESTAMP between(queryFrom..queryTo)
        | where (region=="all" or isempty(region)) or Region ==region
        | where isempty(subscriptionId) or SubscriptionId ==subscriptionId
        | where isempty(correlationId) or CorrelationRequestId==correlationId
        | where isempty(operationId) or OperationId==operationId
        | where (isempty(resourceGroupName_) or resourceGroupName_ startswith "Test") or ResourceGroup ==resourceGroupName_
        | where show_only_operationNames==false or isnotempty(OperationName)
        | extend query_key=bag_pack_columns(TIMESTAMP, Region, OperationName, SubscriptionId, CorrelationRequestId, OperationId, TableName, ResourceGroup, ResourceName)
        | extend  Content=strcat(OperationName, 'corrid:', substring(CorrelationRequestId, 0, 6), '|opid:', substring(OperationId, 0, 6))
        | join kind=leftouter qos_errs on CorrelationRequestId
        | extend ERR=qos_err_count>0//Level<=2 or Message contains "exception"
        | extend qos_err_msg=iff(ERR, strcat(';', strcat_array(ErrorCodes, ',')),''),
                 feerr_msg=iff((Level<=2 or Message contains "exception"), 
                                        strcat('FEmsg:', iff(isnotempty(EventCode), EventCode, substring(Message, 0, 40)))
                                        , '')
        | extend err_msg=strcat(qos_err_msg, feerr_msg)
        | summarize n=count(),
                    min(Sequence), max(Sequence),
                    err=sum(qos_err_count), err_msgs=make_set_if(err_msg, ERR==true),
                    min_Lvl=min(Level),
                    StartTime=arg_min(PreciseTimeStamp, query_key),
                    EndTime=max(PreciseTimeStamp),
                    num_locks=countif(EventCode=="Locked"),
                    ResourceGroups=strcat_array(make_set_if(ResourceGroup, isnotempty(ResourceGroup)), ','),
                    ResourceNames=strcat_array(make_set_if(ResourceName, isnotempty(ResourceName)), ',')
                    by Content
        | where show_only_errs==false or err>0
         | where show_only_locks==false or num_locks>0
        | extend Content=strcat(Content, '|n:', n, iff(err>0, strcat('|err:', err), ''), '|minLvl:', min_Lvl, iff(num_locks>0, strcat('|Locks:', num_locks), ''))
        | extend duration_msecs=datetime_diff("millisecond", EndTime, StartTime)
        | extend t=bin(datetime_diff("millisecond", StartTime, queryFrom), bin_size_sec*1000.0)
        | where duration_msecs>=minDurationToShow_sec*1000.0
        | extend Content=strcat(Content, '|msecs:', duration_msecs), t=tolong(t), duration_hrs=round(duration_msecs/1000.0/60.0/60.0,1)
        | extend GroupBy=strcat('msecs_from_qstart:', strcat_array(repeat('0', 8 - strlen(tostring(t))),''), tostring(t)), Health=iff(min_Lvl<=2, "Error", iff(min_Lvl<=4, "Degraded","Neutral")),
                 err_enum=strcat_array(err_msgs, ',')
        | sort by StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`, `{correlationId}`, `{operationId}`, `{bin_size_sec}`, `{minDurationToShow_sec}`, `{subscriptionId}`, `{show_only_errs}`, `{show_only_locks}`, `{show_only_operationNames}`, `{resourceGroupName_}`, `{Tables}`

**Signal filters seen in KQL:** `Tables == "all"`

---

## Activity

### correlActivity

_Widget purpose:_ Activity

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `correlId > Activity`

```kusto
let correllationId=tostring(qk.CorrelationRequestId);
let operationId=tostring(qk.OperationId);
let region=tostring(qk.Region);
let time_span=1m;
//
let activity=FrontendOperationEtwEvent
| where TIMESTAMP between(starttime..endtime)
        | where isempty(region) or Region ==region
        | where CorrelationRequestId==correllationId
       // | where isempty(operationId) or OperationId==operationId
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
                    Lvl2=sumif(n,Level<=2),
                    Lvl4=sumif(n,Level<=4),
                    Lvl8=sumif(n,Level<=8)
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

**Params:** `{qk}`, `{starttime}`, `{endtime}`

---

## ARMHttpIncomingOutgoing

### ARM_Correl

_Widget purpose:_ ARMHttpIncomingOutgoing

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `correlId > ARMHttpIncomingOutgoing`

```kusto
let starttime=todatetime(qk.TIMESTAMP)-1h;
let endtime=starttime+2h;
let correllationId_q=tostring(qk.CorrelationRequestId);
let subscriptionId_q=tostring(qk.SubscriptionId);
//
let ARMPRODEntityGroup = entity_group [cluster('armprodeus.eastus.kusto.windows.net'),
                                       cluster('armprodweu.westeurope.kusto.windows.net'),
                                       cluster('armprodsea.southeastasia.kusto.windows.net')];
macro-expand isfuzzy=true ARMPRODEntityGroup as X
    (
        X.database('Requests').HttpIncomingRequests | union X.database("Requests").HttpIncomingRequests
        | extend $cluster = X.$current_cluster_endpoint
        | where PreciseTimeStamp between(starttime..endtime)
       // | where targetResourceProvider=="MICROSOFT.NETWORK"
       | where ignore_200==false or bin(httpStatusCode, 100)!=200
        | where correlationId == correllationId_q
    )
```

**Params:** `{queryFrom}`, `{queryTo}`, `{test}`, `{qk}`, `{ignore_200}`

**Signal filters seen in KQL:** `targetResourceProvider == "MICROSOFT.NETWORK"`

---

## CRP_ApiQosEvent

### crp_apiqos

_Widget purpose:_ CRP_ApiQosEvent

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `correlId > CRP_ApiQosEvent`

```kusto
let starttime=todatetime(qk.TIMESTAMP)-1h;
let endtime=starttime+1h;
let correllationId_q=tostring(qk.CorrelationRequestId);
let operationId_q=tostring(qk.OperationId);
let subscriptionId_q=tostring(qk.SubscriptionId);
let nrp_region_q=tostring(qk.Region);
let arm_region=NRPToARM(nrp_region_q);
cluster('azcrp.kusto.windows.net').database('crp_allprod').ApiQosEvent
    | where PreciseTimeStamp  between (starttime..endtime)
    | where tolower(region)==arm_region or tolower(region)==nrp_region_q
    | where ignore_200==false or bin(httpStatusCode, 100)!=200
//
    | where operationId==correllationId_q or goalSeekingActivityId==correllationId_q// or subscriptionId==subscriptionId_q
    | extend queryMatch=iff(operationId==correllationId_q, 'nrp_correll_crpoperationId', iff(goalSeekingActivityId==correllationId_q, 'nrp_correll_crpgoalseekId', 'subid'))
    | project TIMESTAMP, region, queryMatch, operationName, resourceGroupName, resourceName, operationId, resultType, httpStatusCode, resultCode, exceptionType, errorDetails, ids=bag_pack_columns(subscriptionId, operationId, clientRequestId, correlationId, internalCorrelationId)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{qk}`, `{ignore_200}`

---

## FE_query

### fe_popup

_Widget purpose:_ FE_query

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `correlId > FE_query`

```kusto
let starttime=todatetime(qk.TIMESTAMP)-10m;
let endtime=starttime+1h;
let correllationId=tostring(qk.CorrelationRequestId);
let operationId=tostring(qk.OperationId);
let region=tostring(qk.Region);
let tid_query=iff(tid_query_>0, tolong(tid_query_), long(null));
//
FrontendOperationEtwEvent|union  FrontendReadOperationEtwEvent
| where TIMESTAMP between(starttime..endtime)
        | where isempty(region) or Region ==region
        //| where SubscriptionId =="322291f3-f4f0-4c13-81b3-a008a87d891b"
        | where CorrelationRequestId==correllationId
        | where isempty(operationId) or OperationId==operationId
        | where isempty(tid_query) or Tid==tid_query
        | where show_only_locks==false or EventCode contains "lock"
        | where Sequence >min_Sequence and (max_Sequence<=0 or Sequence <max_Sequence)
        | project SourceAssemblyFileVersion, TIMESTAMP, SubscriptionId, ResourceGroup, ResourceName, OperationName, 
                         CorrelationRequestId, OperationId, Tid, Level, EventCode, Sequence, Continuation, msg_sz=string_size(Message), Message, group=strcat(CorrelationRequestId),PreciseTimeStamp
        | invoke StepTimer()
        | where min_step_dur==0 or step_duration_ms >=min_step_dur
        | where Level <= maxLevel
        | extend ERR= Level<=2 or Message contains "exception"
        | where show_only_errs==false or ERR==true
```

**Params:** `{queryFrom}`, `{queryTo}`, `{qk}`, `{min_step_dur}`, `{maxLevel}`, `{tid_query_}`, `{min_Sequence}`, `{max_Sequence}`, `{show_only_locks}`, `{show_only_errs}`

**Signal filters seen in KQL:** `SubscriptionId == "322291f3-f4f0-4c13-81b3-a008a87d891b"`

---

## Request

### GetRequestBody

_Widget purpose:_ Request

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `correlId > Request`

```kusto
let starttime=todatetime(qk.TIMESTAMP)-10m;
let endtime=starttime+1d;
let correllationId=tostring(qk.CorrelationRequestId);
let operationId=tostring(qk.OperationId);
let region=tostring(qk.Region);
//print query=qk
WriteOperationResponseEtwEvent
| union ReadOperationResponseEtwEvent
| where TIMESTAMP between(starttime..endtime) 
| where Region==region 
| where CorrelationRequestId ==correllationId
| where QueryWithOperationId==false or OperationId==operationId 
| project TIMESTAMP, OperationName, HttpMethod, DurationInMillisecond, Request, Response, HttpStatusCode, Message, ErrorCode, CorrelationRequestId, OperationId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{qk}`, `{QueryWithOperationId}`

---

## TID_Timeline

### FE_Tid_query

_Widget purpose:_ TID_Timeline

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Timeline`
Source panel: `correlId > TID_Timeline`

```kusto
let starttime=todatetime(qk.TIMESTAMP)-1d;
let endtime=todatetime(qk.TIMESTAMP)+1d;
let correllationId=tostring(qk.CorrelationRequestId);
let operationId=tostring(qk.OperationId);
let region=tostring(qk.Region);
let errlist=iff(isempty(errors), dynamic(null), split(errors, ','));
//
FrontendOperationEtwEvent|union  FrontendReadOperationEtwEvent
| where TIMESTAMP between(starttime..endtime)
        | where isempty(region) or Region ==region
        | where CorrelationRequestId==correllationId
        | where isempty(operationId) or OperationId==operationId
        | extend ERR= Level<=2 or Message contains "exception"
        | extend err_msg=iff(ERR, iff(isnotempty(EventCode), EventCode, substring(Message, 0, 40)), '')
        | where isempty(errlist) or err_msg in (errlist)
        | summarize StartTime=min(PreciseTimeStamp),
                    EndTime=max(PreciseTimeStamp),
                    n=count(),
                    err=countif(ERR),
                    min_Lvl=min(Level),
                    err_msgs=make_set_if(err_msg, ERR==true),
                    num_locks=countif(EventCode contains "Lock"),
                    make_set(Level),
                    min(Sequence), max(Sequence)
                    by OperationName, CorrelationRequestId, OperationId, Tid
        | where select_locks==false or num_locks>0
        | extend //Content=strcat('Tid:', Tid, '|', OperationName, '|n:', n, iff(num_locks>0, strcat('|Locks:', num_locks), '')),
                 Content=strcat('Tid:', Tid, '|', OperationName, iff(err>0, strcat('err:', err), ''), '|n:', n, '|minLvl:', min_Lvl, '|Locks:', num_locks),
                 Tooltip=strcat_array(err_msgs, ','),
                GroupBy=strcat('Tid:', Tid, '|Opid:', substring(OperationId, 0, 8), '|', OperationName),
                Health=iff(min_Lvl<=2, "Error", iff(min_Lvl<=4, "Degraded","Neutral"))
        | sort by StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{qk}`, `{errors}`, `{select_locks}`

---
