# (top-level)

> Source: **Unhealthy Node Analysis - Node In Place Recovery Status** dashboard, chapter **(top-level)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### In Place Impact Details

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `APlat` · Type: `Table`

```kusto
cluster('aplat.westcentralus.kusto.windows.net').database('APlat').AnvilRepairServiceForgeEvents
| where PreciseTimeStamp between (st ..et ) and Message contains "Initiated In Place repair with Node Recovery Response =" and TreeActionName == "NodeInPlaceRecoveryAction"
| project PreciseTimeStamp, Tenant, TreeNodeKey, TreeActionName, Message, RequestIdentifier, ResourceId
| join kind=leftouter (cluster('aplat.westcentralus.kusto.windows.net').database('APlat').AnvilRepairServiceForgeEvents
| where PreciseTimeStamp between (st ..et ) and Message contains "Action Completed with Response == "
| summarize arg_max(PreciseTimeStamp, *) by RequestIdentifier
| project PreciseTimeStamp, TreeNodeKey, TreeActionName, Message, RequestIdentifier, ResourceId) on RequestIdentifier, ResourceId
| parse-where Message with "Initiated In Place repair with Node Recovery Response = "NodeRecoveryResponse: dynamic 
| parse Message1 with "Action Completed with Response == "actionResponse: dynamic ", Duration "durationInSeconds : double" seconds."
| extend ImpactId = tostring(NodeRecoveryResponse["ImpactId"]), Status = tobool(NodeRecoveryResponse["Status"]), Result = tostring(NodeRecoveryResponse["Result"]), ErrorCode = tostring(NodeRecoveryResponse["ErrorCode"])
| extend OutputResult = iff(actionResponse contains "TimeoutOnAction", "TimeoutOnAction", tostring(actionResponse["Output"]["Result"]))
| project StartTime = PreciseTimeStamp, EndTime = PreciseTimeStamp1, Tenant, ImpactId, Status, Result, ErrorCode, OutputResult, durationInSeconds, RequestIdentifier, ResourceId
| summarize dcount(ResourceId), percentiles(durationInSeconds, 50, 90, 99) by OutputResult
```

**Params:** `{st}`, `{et}`

---

### NodeInPlaceStimEvents

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `APlat` · Type: `Table`

```kusto
cluster('aplat.westcentralus.kusto.windows.net').database('APlat').AnvilRepairServiceForgeEvents
| where PreciseTimeStamp between (st ..et ) and Message contains "Initiated In Place repair with Node Recovery Response =" and TreeActionName == "NodeInPlaceRecoveryAction"
| project PreciseTimeStamp, Tenant, TreeNodeKey, TreeActionName, Message, RequestIdentifier, ResourceId
| join kind=leftouter (cluster('aplat.westcentralus.kusto.windows.net').database('APlat').AnvilRepairServiceForgeEvents
| where PreciseTimeStamp between (st ..et ) and Message contains "Action Completed with Response == "
| summarize arg_max(PreciseTimeStamp, *) by RequestIdentifier
| project PreciseTimeStamp, TreeNodeKey, TreeActionName, Message, RequestIdentifier, ResourceId) on RequestIdentifier, ResourceId
| parse-where Message with "Initiated In Place repair with Node Recovery Response = "NodeRecoveryResponse: dynamic 
| parse Message1 with "Action Completed with Response == "actionResponse: dynamic ", Duration "durationInSeconds : double" seconds."
| extend ImpactId = tostring(NodeRecoveryResponse["ImpactId"]), Status = tobool(NodeRecoveryResponse["Status"]), Result = tostring(NodeRecoveryResponse["Result"]), ErrorCode = tostring(NodeRecoveryResponse["ErrorCode"])
| extend OutputResult = iff(actionResponse contains "TimeoutOnAction", "TimeoutOnAction", tostring(actionResponse["Output"]["Result"]))
| project InPlaceStartTime = PreciseTimeStamp, InPlaceEndTime = PreciseTimeStamp1, Tenant, ImpactId, Status, Result, ErrorCode, OutputResult, durationInSeconds, RequestIdentifier, ResourceId
| join kind=inner (cluster('hawkeyedataexplorer.westus2.kusto.windows.net').database('HawkeyeLogs').HawkeyeStimImpactEvents
| where StartTime between (st .. et)
| summarize arg_max(PreciseTimeStamp, *) by CadPrimaryKey) on $left.ResourceId == $right.NodeId
| extend Relevant = InPlaceStartTime between (StartTime..EndTime)
| where Relevant
| extend DurationInMin = datetime_diff("Minute", EndTime, StartTime)
| extend PowerCycleDuration = durationInSeconds/60
| project StartTime, EndTime, DurationInMin,  NodeId, ContainerId, OutputResult, PowerCycleDuration, ImpactId, Status, Result, ErrorCode, StimAttribution, StimHealthSignalsData, NodeAdditionalDetails, AnvilActionBag
| extend InsightLink = strcat("https://azureserviceinsights.trafficmanager.net/view/services/Stim/pages/Stim Impact Detail?ResourceId=", NodeId, "&ContainerId=", ContainerId, "&globalFrom=", StartTime - 1h, "&globalTo=", EndTime + 1h)
| sort by DurationInMin desc
```

**Params:** `{st}`, `{et}`

---
