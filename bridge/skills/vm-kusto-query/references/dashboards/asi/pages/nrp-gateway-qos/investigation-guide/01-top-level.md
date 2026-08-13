# (top-level)

> Source: **NRP - Gateway QoS** dashboard, chapter **(top-level)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Gateway QoS"

Cluster: `armprod.kusto.windows.net` · Database: `ARMProd` · Type: `ResourceGet` · Widget: `Container`

```kusto
let startTime = datetime_add('hour', -1, local_PreciseTimeStamp);
let endTime = datetime_add('hour', 1, local_PreciseTimeStamp);
print("")
| project PreciseTimeStamp = local_PreciseTimeStamp, clientRequestId = local_clientRequestId
| join kind = fullouter
(
HttpOutgoingRequests
| where PreciseTimeStamp between(startTime..endTime)
| where clientRequestId == local_clientRequestId
| where httpStatusCode != -1
| extend table = "HttpOutgoingRequests"
| union
HttpIncomingRequests
| where PreciseTimeStamp between(startTime..endTime)
| where clientRequestId == local_clientRequestId
| where httpStatusCode != -1
| extend table = "HttpIncomingRequests"
) on clientRequestId
| extend PreciseTimeStamp = coalesce(PreciseTimeStamp, PreciseTimeStamp1), clientRequestId = coalesce(clientRequestId, clientRequestId1)
| project-away PreciseTimeStamp1, clientRequestId1
| take 1
```

**Params:** `{local_PreciseTimeStamp}`, `{local_clientRequestId}`

---

### Gateway QoS

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `CoBeTimeline`

```kusto
let startTime = datetime_add('hour', -12, timestamp);
let endTime = datetime_add('hour', 12, timestamp);
NRPGatewayService(clientRequestId, startTime, endTime);
```

**Params:** `{timestamp}`, `{clientRequestId}`

---
