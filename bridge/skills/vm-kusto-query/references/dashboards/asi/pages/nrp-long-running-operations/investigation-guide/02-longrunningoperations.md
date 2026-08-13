# LongRunningOperations

> Source: **NRP - LongRunningOperations** dashboard, chapter **LongRunningOperations** (3 queries across 3 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### LongRunningOperations

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `LongRunningOperations`

```kusto
let groupBy="";
let region_query=iff(isempty(region_query_) or region_query_=="all", '', region_query_);
let knownOperations=dynamic([
  "DeleteNicOperation",
  "GetPublishedResourceDataOperation",
  "BackupOperation",
  "PutVMScaleSetOperation",
  "PutNetworkSecurityGroupOperation",
  "PutPrivateEndpointOperation",
  "PutLoadBalancerOperation",
  "PutSubscriptionOperation",
  "DeletePacketCaptureOperation",
  "DeleteTenantOperation",
  "PutKeyValueItemOperation",
  "DeleteLoadBalancerOperation",
  "PutSecurityRuleOperation",
  "AllocateTenantNetworkResourcesOperation",
  "ValidateVMScaleSetOperation",
  "GetNicEffectiveRouteTableOperation",
  "PutPrivateDnsZoneGroupOperation",
  "DeleteFlowLogOperation",
  "GetTenantClustersOperation",
  "PutFlowLogOperation",
  "PutNicOperation"
]);
let operationName_query_list=iff(apply_knownOperations, knownOperations, iff(isempty(operationName_query_) or operationName_query_ startswith ("Test"), dynamic(null), split(operationName_query_, ',')));
let safe_time_window=1d;
//
let UseSafeWindow=isempty(region_query) or isempty(operationName_query_list);
let starttime=queryFrom;//iff(UseSafeWindow, queryTo-safe_time_window, queryFrom);
let endtime=queryTo;//iff(UseSafeWindow, starttime+safe_time_window, queryTo);
//
let projectString="SourceAssemblyFileVersion, TIMESTAMP, SubscriptionId, OperationName, CorrelationRequestId, OperationId, Tid, EventCode, Sequence, Continuation, msg_sz=string_size(Message), Message, group=strcat(CorrelationRequestId)";
let duration_threshold=min_OpertionDurationTHreshold_hr*1000.0*60.0*60.0;
let toprecs=QosEtwEvent
    | where PreciseTimeStamp between(starttime..endtime)
    | where isempty(region_query) or Region==region_query
    | where isempty(operationName_query_list) or OperationName in (operationName_query_list)
    | where isnotempty(CorrelationRequestId) and isnotempty(SubscriptionId)
    | where DurationInMilliseconds>duration_threshold
    | where SourceAssemblyFileVersion contains "release/"
    | join kind = leftouter (ClientAppIds) on $left.ClientAppId == $right.ApplicationId
    | extend Slice=SliceNum(SourceAssemblyFileVersion)
    | summarize count()
                by Region, 
                    Slice, rb=ReleaseBuild(SourceAssemblyFileVersion),
                    SubscriptionId,  OperationName, CorrelationRequestId, OperationId, 
                    ApplicationName, 
                    opDurationInHours=DurationInMilliseconds/1000.0/60.0/60.0
    | order by count_ desc;
let correlids=toscalar(toprecs|summarize make_set(CorrelationRequestId));
QosEtwEvent
    | where PreciseTimeStamp between(starttime..endtime)
    | where isempty(region_query) or Region==region_query
    | where CorrelationRequestId in  (correlids) 
    | extend DurationInHrs=DurationInMilliseconds/1000.0/60.0/60.0
    | invoke QosToFE(project_str=projectString, time_window=1d)
    | summarize max_DurationInHrs=arg_max(DurationInHrs, querylink_kusto),
                sum_DurationInHrs=sum(DurationInHrs),
                n=count(),
                min(TIMESTAMP), max(TIMESTAMP)
           by Region, SubscriptionId, OperationName, OperationId, CorrelationRequestId
    | extend opid_Duration=sum_DurationInHrs//datetime_diff("minute", max_TIMESTAMP, min_TIMESTAMP)/60.0
    | summarize Operation_max_DurationInHrs=arg_max(max_DurationInHrs, querylink_kusto),
                sum_DurationInHrs=sum(sum_DurationInHrs),
                n=sum(n),
                dcount(OperationId),
                max(opid_Duration),
                sum(opid_Duration),
                min_TIMESTAMP=min(min_TIMESTAMP), max_TIMESTAMP=max(max_TIMESTAMP)
          by Region, SubscriptionId, CorrelationRequestId, OperationName
    | extend d=bag_pack_columns(dcount_OperationId, sum_opid_Duration, querylink_kusto)      
    | summarize max_DurationInHrs=arg_max(Operation_max_DurationInHrs, max_OperationName=OperationName, querylink_kusto),
                sum_DurationInHrs=sum(sum_DurationInHrs),
                OperationNames=make_bag_if(bag_pack(OperationName, strcat('opids:', dcount_OperationId, ' max_duration_hrs:', round(Operation_max_DurationInHrs, 1))), Operation_max_DurationInHrs>0.5),
                op_dict=make_bag(bag_pack(OperationName, C)),
                sum_opid_Duration=sum(sum_opid_Duration),
                min_TIMESTAMP=min(min_TIMESTAMP), max_TIMESTAMP=max(max_TIMESTAMP)
          by Region, SubscriptionId, CorrelationRequestId
    | join kind = leftouter (cluster('executiongraph.kusto.windows.net').database('eg').SubscriptionMetadata| project SubscriptionId, SubscriptionName)  on SubscriptionId| project-away *1
    | extend correl_Log_Duration=round(datetime_diff("minute", max_TIMESTAMP, min_TIMESTAMP)/60.0,1)
    | extend TimeRange=strcat(substring(min_TIMESTAMP, 0, 16), '\n\r', substring(max_TIMESTAMP, 0, 16))
    | extend max_DurationInHrs=round(max_DurationInHrs,1)
    | sort by max_DurationInHrs
```

**Params:** `{queryFrom}`, `{queryTo}`, `{operationName_query_}`, `{region_query_}`, `{min_OpertionDurationTHreshold_hr}`, `{apply_knownOperations}`

**Signal filters seen in KQL:** `SourceAssemblyFileVersion contains "release/"`

---

## OperationId_Timings

### opidTimings

_Widget purpose:_ OperationId_Timings

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `LongRunningOperations > OperationId_Timings`

```kusto
FrontendOperationEtwEvent|union  FrontendReadOperationEtwEvent
| where TIMESTAMP between(queryFrom..queryTo)
| where CorrelationRequestId==correlationRequestId
| summarize mint=min(PreciseTimeStamp), maxt=max(PreciseTimeStamp) by OperationName, OperationId
| extend duration_hrs=round(datetime_diff("minute", maxt, mint)/60.0,2)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{correlationRequestId}`

---

## OperationNames

### expand

_Widget purpose:_ OperationNames

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `LongRunningOperations > OperationNames`

```kusto
print ops=todynamic(op_dict)
| mv-expand ops
| extend OperationName=bag_keys(ops)
| mv-expand OperationName
| extend OperationName=tostring(OperationName)
| extend d=parse_json(ops)[OperationName]
| project OperationName, dcount_OperationId=tolong(d['dcount_OperationId']), sum_opid_Duration=round(toreal(d['sum_opid_Duration']), 4), querylink_kusto=tostring(d['querylink_kusto'])
| sort by sum_opid_Duration
```

**Params:** `{queryFrom}`, `{queryTo}`, `{op_dict}`

---
