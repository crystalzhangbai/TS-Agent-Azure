# GatewayApiQoSEvent

> Source: **CRP OperationId Investigation Guide** dashboard, chapter **GatewayApiQoSEvent** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## GatewayApiQoSEvent

### OperationId GatewayApiQoSEvent GET

_Widget purpose:_ GatewayApiQoSEvent - operationId {{operationId}}

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Single` · Widget: `Card`
Source panel: `GatewayApiQoSEvent > GatewayApiQoSEvent > GatewayApiQoSEvent - operationId {{operationId}}`

```kusto
let adjustedStart = datetime_add('hour', -6, local_startDate);
let adjustedEnd = datetime_add('hour', 6, local_endDate);
GatewayApiQoSEvent
| where PreciseTimeStamp between (adjustedStart..adjustedEnd)
| where operationId =~ local_operationId
| extend startIndex = indexof(targetEndpoint, "/subscriptions")
| extend resourceId = substring(targetEndpoint, startIndex, indexof(targetEndpoint,"?") - startIndex)
| project PreciseTimeStamp,httpStatusCode,resultCode,lastPhase,targetEndpoint,targetRPNode,serviceName,serviceBuild,userName, resourceId
```

**Params:** `{local_operationId}`, `{local_endDate}`, `{local_startDate}`

---
