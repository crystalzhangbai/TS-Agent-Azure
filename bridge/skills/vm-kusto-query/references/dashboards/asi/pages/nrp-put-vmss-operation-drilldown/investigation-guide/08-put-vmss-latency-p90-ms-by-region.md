# Put Vmss Latency (P90 ms) by region 

> Source: **NRP - PUT VMScaleSet Operation drill down** dashboard, chapter **Put Vmss Latency (P90 ms) by region ** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### PutVmssP90Latency

_Widget purpose:_ Put Vmss Latency (P90 ms) by region 

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Put Vmss Latency (P90 ms) by region `

```kusto
QosEtwEvent
| where PreciseTimeStamp  between (queryFrom ..queryTo)
| where Region == region
| where OperationName in ("PutVMScaleSetOperation")
| summarize percentiles(DurationInMilliseconds, 90) by bin(PreciseTimeStamp, 5m)
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`

---
