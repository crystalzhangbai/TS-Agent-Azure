# ReadOperationService Load

> Source: **NRP - ReadOperationService** dashboard, chapter **ReadOperationService Load** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### ReadOperationService OperationTimeseries

_Widget purpose:_ ReadOperationService Load

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `ReadOperationService Load`

```kusto
QosEtwEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where SourceAssemblyFileVersion has_cs "readoperations"
| summarize count() by bin(PreciseTimeStamp, granularity), OperationName
```

**Params:** `{queryFrom}`, `{queryTo}`, `{granularity}`

---
