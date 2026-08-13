# (top-level)

> Source: **NRP - NRP Name Reservation** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Operations with NRS call

Cluster: `https://nrp.kusto.windows.net/` · Database: `mdsnrp` · Type: `TimeSeries`

```kusto
let opidLst=FrontendOperationEtwEvent
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
| where Message contains "name reservation"
| distinct OperationId;
FrontendOperationEtwEvent
| where (PreciseTimeStamp > startTime and PreciseTimeStamp < endTime)
| where OperationId in (opidLst)
| summarize count() by bin(PreciseTimeStamp, 1h), Region
```

**Params:** `{startTime}`, `{endTime}`, `{region}`

**Signal filters seen in KQL:** `Message contains "name reservation"`

---
