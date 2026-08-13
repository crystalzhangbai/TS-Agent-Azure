# BatchManager transaction job dequeue times (ms)

> Source: **NRP - PUT VMScaleSet Operation drill down** dashboard, chapter **BatchManager transaction job dequeue times (ms)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### BatchManagerDequeueJobTimesPerSub

_Widget purpose:_ BatchManager transaction job dequeue times (ms)

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `BatchManager transaction job dequeue times (ms)`

```kusto
FrontendOperationEtwEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where Region == region
| where SubscriptionId == subId
| where EventCode == "TransactionJobDequeued"
| parse Message with *" duration in queue: "durationMs
| project PreciseTimeStamp,SubscriptionId, OperationId, CorrelationRequestId, OperationName, Message, durationMs
| summarize percentiles(toint(durationMs), 50) by bin(PreciseTimeStamp, 5m)
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`, `{subId}`

**Signal filters seen in KQL:** `EventCode == "TransactionJobDequeued"`

---
