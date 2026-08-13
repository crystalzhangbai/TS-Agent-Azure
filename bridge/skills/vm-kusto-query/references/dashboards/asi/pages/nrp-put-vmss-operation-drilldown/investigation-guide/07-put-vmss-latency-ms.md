# Put Vmss latency (ms)

> Source: **NRP - PUT VMScaleSet Operation drill down** dashboard, chapter **Put Vmss latency (ms)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### PutVmssLatencyPerSub

_Widget purpose:_ Put Vmss latency (ms)

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Put Vmss latency (ms)`

```kusto
QosEtwEvent
| where PreciseTimeStamp between (queryFrom ..queryTo)
| where Region == region
| where SubscriptionId == subId
| where OperationName in ("PutVMScaleSetOperation")
| summarize percentiles(DurationInMilliseconds, 50, 75, 99) by bin(PreciseTimeStamp, 5m)
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`, `{subId}`

---
