# 5xx Error Rates

> Source: **NRP - ReadOperationService** dashboard, chapter **5xx Error Rates** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### ReadOperationService ErrorRates

_Widget purpose:_ 5xx Error Rates

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `5xx Error Rates`

```kusto
QosEtwEvent
| where SourceAssemblyFileVersion has_cs "readoperations"
| where UserError == false
| where Success == false
| where PreciseTimeStamp between (queryFrom .. queryTo)
| make-series count() on PreciseTimeStamp from queryFrom to queryTo step 5min by strcat(Region, "_", SliceNum(SourceAssemblyFileVersion))
| mv-expand count_, PreciseTimeStamp
| project PreciseTimeStamp=todatetime(PreciseTimeStamp), Slice=Column1, Count=toint(count_)
```

**Params:** `{queryFrom}`, `{queryTo}`

---
