# PutVmss transaction stats (KB) by region

> Source: **NRP - PUT VMScaleSet Operation drill down** dashboard, chapter **PutVmss transaction stats (KB) by region** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### PutVmssTransactionStatsPerRegion

_Widget purpose:_ PutVmss transaction stats (KB) by region

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `PutVmss transaction stats (KB) by region`

```kusto
KvsTransactionEtwEvent
| where PreciseTimeStamp between (queryFrom ..queryTo)
| where Region == region
| where OperationName in ("PutVMScaleSetOperation")
| project PreciseTimeStamp, ReadCount, ReadSize, AddCount, AddSize, ReadDuration, CommitDuration, UpdateCount, UpdateSize, OperationId
| summarize readSizeKb = sum(ReadSize)/1000, addSizeKb = sum(AddSize)/1000, updateSizeKb = sum(UpdateSize)/1000 by bin(PreciseTimeStamp, 5m)
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`

---
