# (top-level)

> Source: **CRP Gateway QoS Investigation Guide** dashboard, chapter **(top-level)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Gateway QoS"

Cluster: `armprodgbl.eastus` · Database: `ARMProd` · Type: `ResourceGet` · Widget: `Container`

```kusto
let startTime = datetime_add('hour', -12, local_PreciseTimeStamp);
let endTime = datetime_add('hour', 12, local_PreciseTimeStamp);
print("")
| project PreciseTimeStamp = local_PreciseTimeStamp, serviceRequestId = local_serviceRequestId
| join kind=fullouter (
    macro-expand isfuzzy=true ARMProdEG as X
    (
        union 
            X.database('Requests').HttpIncomingRequests,
            X.database('Requests').HttpOutgoingRequests
        | where PreciseTimeStamp between(startTime .. endTime)
        | where serviceRequestId == local_serviceRequestId
        | take 1
    )
) on serviceRequestId
| extend PreciseTimeStamp = coalesce(PreciseTimeStamp, PreciseTimeStamp1), serviceRequestId = coalesce(serviceRequestId, serviceRequestId1)
| project-away PreciseTimeStamp1, serviceRequestId1
| take 1
```

**Params:** `{local_PreciseTimeStamp}`, `{local_serviceRequestId}`, `{globalFrom}`, `{globalTo}`

---

### Gateway QoS

Cluster: `azcrp.kusto.windows.net` · Database: `crp_allprod` · Type: `CoBeTimeline`

```kusto
let startTime = datetime_add('hour', -12, timeStamp);
let endTime = datetime_add('hour', 12, timeStamp);
CRPGatewayQoS(operationId, startTime, endTime);
```

**Params:** `{operationId}`, `{timeStamp}`

---
