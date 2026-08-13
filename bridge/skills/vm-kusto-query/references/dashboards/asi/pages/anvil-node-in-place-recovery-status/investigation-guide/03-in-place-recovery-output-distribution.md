# In Place Recovery output Distribution

> Source: **Unhealthy Node Analysis - Node In Place Recovery Status** dashboard, chapter **In Place Recovery output Distribution** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Node In Place Output distribution

_Widget purpose:_ In Place Recovery output Distribution

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `APlat` · Type: `CategoryChart`
Source panel: `In Place Recovery output Distribution`

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
