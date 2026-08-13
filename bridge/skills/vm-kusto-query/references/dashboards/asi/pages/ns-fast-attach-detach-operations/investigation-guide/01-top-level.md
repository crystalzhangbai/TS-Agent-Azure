# (top-level)

> Source: **NodeService - FastAttachDetachOperations** dashboard, chapter **(top-level)** (3 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "FastAttachDetachOperations"

Cluster: `azcrp.kusto.windows.net` · Database: `crp_allprod` · Type: `ResourceGet` · Widget: `Container`

```kusto
print local_vMId
```

**Params:** `{globalFrom}`, `{globalTo}`, `{local_vMId}`

---

### Timeline query

Cluster: `azcrp.kusto.windows.net` · Database: `crp_allprod` · Type: `Timeline`

```kusto
let crpLogs = cluster('azcrp.kusto.windows.net').database('crp_allprod').VMApiQosEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where vMId == vmid
| extend startTimeStamp = PreciseTimeStamp - (durationInMilliseconds * 1ms);
let resourceName = crpLogs | take 1 | project resourceName;
let operationIds = crpLogs | project operationId;
let correlationIds = crpLogs | project correlationId;
let crpPostGoalStateLogs = ContextActivity
| union VmssVMGoalSeekingActivity
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where activityId in (operationIds)
| where message contains "posting" and message contains toscalar(resourceName)
| where vMName == "" or vMName == toscalar(resourceName)
| project PreciseTimeStamp, Message=message, Source="CRPPostGoalStateEvents";
let crpNotificationLogs = ApiQosEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where requestEntity == vmid
| where operationName contains "OnNodeGoalComplementsStatus" and operationName !contains "Detached"
| extend req = parse_json(requestEntity)
| extend
    GoalAchieved                = tobool(req.GoalAchieved),
    GoalStateLocatorsRevision   = toint(req.GoalStateLocatorsRevision),
    SvdVersion                  = toint(req.SvdVersion),
    VMIncarnationNumber         = toint(req.VMIncarnationNumber),
    ContainerId                 = tostring(req.ContainerId),
    MessageTick                 = tolong(req.MessageTick)
| mv-apply meta = req.CorrelationMetadata to typeof(dynamic) on (
    where meta.Key == "CRPActivityId"
    | summarize CRPActivityId = any(meta.Value)
)
| project
    PreciseTimeStamp, Message=requestEntity, Source="CRPNotificationEvents";
let correlationId = correlationIds | take 1;
let nodeServiceLogs = cluster('azcore.centralus').database('Fa').NodeServiceEventEtwTable
//| where Message contains vmid
| where NodeId == "62d56ee0-21a5-af5e-5574-cc9dc4498c75"
| where PreciseTimeStamp between (queryFrom..queryTo)
| where (Message contains vmid and Message contains "Updating locator path" or Message contains "Updated goal locators on - ") or (Message contains toscalar(correlationId))
| project PreciseTimeStamp, Message, Source="NodeServiceEvents";
let nodeServiceMadariLogs = cluster('azcore.centralus').database('Fa').NodeServiceMadariEventsEtwTable
//| where Message contains vmid
| where ContextSelector contains vmid
| where NodeId == "62d56ee0-21a5-af5e-5574-cc9dc4498c75"
| where Message contains "Type:"
| where PreciseTimeStamp between (queryFrom..queryTo)
| project PreciseTimeStamp, Message=strcat("ctxsel: ", ContextSelector, " relpath: ", RelativePath, " | Message: " , Message), Source="NodeServiceMadariEvents";
//| where Message contains "Updating locator path" or Message contains "Updated goal locators on - "
//| project PreciseTimeStamp, Pid, NodeId, Message;
crpPostGoalStateLogs
| union crpNotificationLogs
| union nodeServiceLogs
| union nodeServiceMadariLogs
| project StartTime=PreciseTimeStamp, Content=Message, Message, GroupBy=Source
```

**Params:** `{queryFrom}`, `{queryTo}`, `{vmid}`

**Signal filters seen in KQL:** `message contains "posting"` · `operationName contains "OnNodeGoalComplementsStatus"` · `meta.Key == "CRPActivityId"` · `NodeId == "62d56ee0-21a5-af5e-5574-cc9dc4498c75"` · `Message contains "Type:"` · `Message contains "Updating locator path"`

---

### Unioned Logs

Cluster: `azcrp.kusto.windows.net` · Database: `crp_allprod` · Type: `Table`

```kusto
let nodeid = toscalar(cluster('azcore.centralus').database('AzureCP').MycroftContainerSnapshot
| where VirtualMachineUniqueId == vmid
| take 1
| project NodeId);
let crpLogs = cluster('azcrp.kusto.windows.net').database('crp_allprod').VMApiQosEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where vMId == vmid
| extend startTimeStamp = PreciseTimeStamp - (durationInMilliseconds * 1ms);
let resourceName = crpLogs | take 1 | project resourceName;
let operationIds = crpLogs | project operationId;
let correlationIds = crpLogs | project correlationId;
let crpPostGoalStateLogs = ContextActivity
| union VmssVMGoalSeekingActivity
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where activityId in (operationIds)
| where message contains "posting" and message contains toscalar(resourceName)
| where vMName == "" or vMName == toscalar(resourceName)
| project PreciseTimeStamp, Message=message, Source="CRPPostGoalStateEvents";
let crpNotificationLogs = ApiQosEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where requestEntity == vmid
| where operationName contains "OnNodeGoalComplementsStatus" and operationName !contains "Detached"
| extend req = parse_json(requestEntity)
| extend
    GoalAchieved                = tobool(req.GoalAchieved),
    GoalStateLocatorsRevision   = toint(req.GoalStateLocatorsRevision),
    SvdVersion                  = toint(req.SvdVersion),
    VMIncarnationNumber         = toint(req.VMIncarnationNumber),
    ContainerId                 = tostring(req.ContainerId),
    MessageTick                 = tolong(req.MessageTick)
| mv-apply meta = req.CorrelationMetadata to typeof(dynamic) on (
    where meta.Key == "CRPActivityId"
    | summarize CRPActivityId = any(meta.Value)
)
| project
    PreciseTimeStamp, Message=requestEntity, Source="CRPNotificationEvents";
let correlationId = correlationIds | take 1;
let nodeServiceLogs = cluster('azcore.centralus').database('Fa').NodeServiceEventEtwTable
| where NodeId == nodeid
| where PreciseTimeStamp between (queryFrom..queryTo)
| where (Message contains vmid and Message contains "Updating locator path" or Message contains "Updated goal locators on - ") or (Message contains toscalar(correlationId))
| project PreciseTimeStamp, Message, Source="NodeServiceEvents";
let nodeServiceMadariLogs = cluster('azcore.centralus').database('Fa').NodeServiceMadariEventsEtwTable
| where ContextSelector contains vmid
| where NodeId == nodeid
| where Message contains "Type:"
| where PreciseTimeStamp between (queryFrom..queryTo)
| project PreciseTimeStamp, Message=strcat("ctxsel: ", ContextSelector, " relpath: ", RelativePath, " | Message: " , Message), Source="NodeServiceMadariEvents";
let nodeServiceHostProxyEnqueueRawLogs = cluster('azcore.centralus').database('Fa').NodeServiceHostProxyEtwTable
| where Message contains vmid
| where PreciseTimeStamp between (queryFrom..queryTo)
| parse Message with * "[request_id=" RequestId "][" *;
let nodeServiceHostProxyEnqueueLogs = nodeServiceHostProxyEnqueueRawLogs
| project PreciseTimeStamp, Message, Source="NodeServiceHostProxyEtwTable";
let requestIds = nodeServiceHostProxyEnqueueRawLogs | project RequestId;
let nodeServiceHostProxySentLogs = cluster('azcore.centralus').database('Fa').NodeServiceHostProxyEtwTable
| where Message contains "Successfully sent"
| where NodeId == nodeid
| where PreciseTimeStamp between (queryFrom..queryTo)
| parse Message with * "[request_id=" RequestId "][" *
| where RequestId in (requestIds)
| project PreciseTimeStamp, Message, Source="NodeServiceHostProxyEtwTable";
crpPostGoalStateLogs
| union crpNotificationLogs
| union nodeServiceLogs
| union nodeServiceMadariLogs
| union nodeServiceHostProxyEnqueueLogs
| union nodeServiceHostProxySentLogs
| project PreciseTimeStamp, Source, Message
```

**Params:** `{queryFrom}`, `{queryTo}`, `{vmid}`

**Signal filters seen in KQL:** `message contains "posting"` · `operationName contains "OnNodeGoalComplementsStatus"` · `meta.Key == "CRPActivityId"` · `Message contains "Type:"` · `Message contains "Successfully sent"`

---
