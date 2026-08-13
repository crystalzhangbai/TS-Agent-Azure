# PutVmss P50 latency (ms) by region

> Source: **NRP - PUT VMScaleSet Operation drill down** dashboard, chapter **PutVmss P50 latency (ms) by region** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### PutVmssLatencyPerRegion

_Widget purpose:_ PutVmss P50 latency (ms) by region

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `PutVmss P50 latency (ms) by region`

```kusto
QosEtwEvent
| where PreciseTimeStamp  between (queryFrom ..queryTo)
| where Region == region
| where OperationName in ("PutVMScaleSetOperation")
| summarize percentiles(DurationInMilliseconds, 50) by bin(PreciseTimeStamp, 5m)
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`

---
