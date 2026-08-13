# (top-level)

> Source: **NRP - ClientOperationId Search** dashboard, chapter **(top-level)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "ClientOperationId Search"

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `ResourceGet` · Widget: `Container`

```kusto
let startTime = datetime_add('hour', -12, local_PreciseTimeStamp);
let endTime = datetime_add('hour', 12, local_PreciseTimeStamp);
FrontendOperationEtwEvent
| where PreciseTimeStamp >= startTime and PreciseTimeStamp < endTime
| where ClientOperationId == local_ClientOperationId
| take 1
```

**Params:** `{local_PreciseTimeStamp}`, `{local_ClientOperationId}`

---

### ClientOperationId

Cluster: `armprod.kusto.windows.net` · Database: `armprod` · Type: `CoBeTimeline`

```kusto
let startTime = datetime_add('hour', -12, timestamp);
let endTime = datetime_add('hour', 12, timestamp);
NRPClientOperationId(clientRequestId, startTime, endTime);
```

**Params:** `{timestamp}`, `{clientRequestId}`

---
