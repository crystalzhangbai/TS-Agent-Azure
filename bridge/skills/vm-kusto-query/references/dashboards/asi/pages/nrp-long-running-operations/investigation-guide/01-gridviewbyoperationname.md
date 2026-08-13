# GridViewByOperationName

> Source: **NRP - LongRunningOperations** dashboard, chapter **GridViewByOperationName** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### operationDurationGrid

_Widget purpose:_ GridViewByOperationName

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `GridViewByOperationName`

```kusto
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
//
let safe_time_window=1d;
let queryFrom=now()-lookback_days*1d;
let queryTo=now();
//
QosEtwEvent
    | where PreciseTimeStamp between(queryFrom..queryTo)
    | where isempty(region_query) or Region==region_query
   | where isempty(operationName_query_list) or OperationName in (operationName_query_list)
    | where isnotempty(CorrelationRequestId) and isnotempty(SubscriptionId)
    | extend DurationInHours=round(DurationInMilliseconds/1000.0/60.0/60.0, 2)*1h
    | where DurationInHours>duration_threshold*1h
    | where SourceAssemblyFileVersion contains "release/"
    //
    | extend DurationInHours_hr=DurationInHours/1h
    | summarize n=dcount(OperationId),
                max_DurationInHours=arg_max(DurationInHours, max_CorrelationRequestId=CorrelationRequestId),
                retry_err_Count=dcountif(OperationId, ErrorCode contains "Retr"),
                user_err_Count=dcountif(OperationId, Success==false and UserError==true),
                err_Count=dcountif(OperationId, Success==false and UserError==false)
                by OperationName, TeamName, duration_bin=iff(DurationInHours_hr<10, bin(DurationInHours_hr, 1.0), bin(DurationInHours_hr, 10))
    | sort by duration_bin asc
    | extend duration_bin=DigitFormat_real(duration_bin, zeros=2)
    | summarize
                d=make_bag(bag_pack(strcat(duration_bin, 'hr'), I)),
                max_DurationInHours=arg_max(max_DurationInHours, retry_err_Count, user_err_Count, err_Count, max_CorrelationRequestId)
                by OperationName, TeamName
    | evaluate bag_unpack(d)
    | sort by max_DurationInHours desc
```

**Params:** `{operationName_query_}`, `{region_query_}`, `{duration_threshold}`, `{lookback_days}`, `{apply_knownOperations}`

**Signal filters seen in KQL:** `SourceAssemblyFileVersion contains "release/"`

---
