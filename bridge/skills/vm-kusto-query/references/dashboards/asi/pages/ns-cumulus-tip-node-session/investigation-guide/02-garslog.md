# GARSLog

> Source: **NodeService - Cumulus Tip Node Session** dashboard, chapter **GARSLog** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### GARSLog

Cluster: `azcore.centralus.kusto.windows.net` · Database: `AutopilotDeployment` · Type: `Table`
Source panel: `GARSLog`

```kusto
let _times = materialize(cluster('tipnodeservice.kusto.windows.net').database('TipNodeService').RequestHandlerEvent
| where tipNodeSessionId == _tipNodeSessionId
| summarize min(PreciseTimeStamp), max(PreciseTimeStamp));
let _startTime = materialize(_times | project min_PreciseTimeStamp);
let _endTime = materialize(_times | project max_PreciseTimeStamp);
let changeId = cluster('tipnodeservice.kusto.windows.net').database('TipNodeService').RequestHandlerEvent
| where PreciseTimeStamp > toscalar(_startTime) and PreciseTimeStamp < toscalar(_endTime)
| where tipNodeSessionId == _tipNodeSessionId
| where message has_cs "[AutoPilotAppImageHandler]"
//| where requestId == "5e2d6f0c-4559-4773-89d3-f9908e8e1b0f"
| where PreciseTimeStamp > toscalar(_startTime) and PreciseTimeStamp < toscalar(_endTime)
| distinct requestId;
let logs = cluster('tipnodeservice.kusto.windows.net').database('TipNodeService').RequestHandlerEvent
| where requestId in (changeId)
| where PreciseTimeStamp > toscalar(_startTime) and PreciseTimeStamp < toscalar(_endTime)
| project PreciseTimeStamp, requestId, message;
let serviceName = logs
| where message has_cs "Finished Building Image"
| parse message with * "Services: " parsedServiceName
| project serviceName = tostring(parsedServiceName);
let _azureNodeId = logs
| where message has_cs "Machine: "
| take 1
| parse message with * "Machine: " ParsedNodeId ", PEName" *
| project NodeId=tostring(ParsedNodeId);
let logWherePersistenceToObjectStorePresent = logs
| where message has_cs "SetAppOverridesForMachine succeeded";
cluster('azdeployer.kusto.windows.net').database('AzDeployerKusto').GARSLog
| where PreciseTimeStamp > toscalar(_startTime) and PreciseTimeStamp < toscalar(_endTime)
| where NodeId_Azure in (_azureNodeId)
| project PreciseTimeStamp, LogType, LogTitle, LogMessage;
```

**Params:** `{_tipNodeSessionId}`

**Signal filters seen in KQL:** `requestId == "5e2d6f0c-4559-4773-89d3-f9908e8e1b0f"`

---
