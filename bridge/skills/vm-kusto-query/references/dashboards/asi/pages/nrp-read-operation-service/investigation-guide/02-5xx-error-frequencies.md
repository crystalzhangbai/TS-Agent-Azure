# 5xx Error Frequencies

> Source: **NRP - ReadOperationService** dashboard, chapter **5xx Error Frequencies** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### ReadOperationService Errors

_Widget purpose:_ 5xx Error Frequencies

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `5xx Error Frequencies`

```kusto
QosEtwEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where SourceAssemblyFileVersion has_cs "readoperations"
| where UserError == false
| summarize count(), SampleError=take_any(ErrorDetails), Slice=make_set(strcat(SliceNum(SourceAssemblyFileVersion), "_", Region)), Ops=make_set(OperationName) by newEMHash(ErrorDetails, ErrorCode)
| project SampleError=substring(SampleError, 0, 500), Count=count_, Slice, Ops
| order by Count desc
```

**Params:** `{queryFrom}`, `{queryTo}`

---
