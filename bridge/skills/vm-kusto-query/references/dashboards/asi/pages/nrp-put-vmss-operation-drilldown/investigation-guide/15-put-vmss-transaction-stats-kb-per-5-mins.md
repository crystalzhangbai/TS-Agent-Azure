# Put Vmss transaction stats (KB) per 5 mins

> Source: **NRP - PUT VMScaleSet Operation drill down** dashboard, chapter **Put Vmss transaction stats (KB) per 5 mins** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### PutVmssTransactionStatsPerSub

_Widget purpose:_ Put Vmss transaction stats (KB) per 5 mins

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Put Vmss transaction stats (KB) per 5 mins`

```kusto
KvsTransactionEtwEvent
| where PreciseTimeStamp between (queryFrom ..queryTo)
| where Region == region
| where SubscriptionId == subId
| where OperationName in ("PutVMScaleSetOperation")
| project PreciseTimeStamp, ReadCount, ReadSize, AddCount, AddSize, ReadDuration, CommitDuration, UpdateCount, UpdateSize, OperationId
| summarize readSizeKb = sum(ReadSize)/1000, addSizeKb = sum(AddSize)/1000, updateSizeKb = sum(UpdateSize)/1000 by bin(PreciseTimeStamp, 5m)
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`, `{subId}`

---
