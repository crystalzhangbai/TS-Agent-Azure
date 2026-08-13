# PutVMScaleSet operation failures

> Source: **NRP - PUT VMScaleSet Operation drill down** dashboard, chapter **PutVMScaleSet operation failures** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### PutVmssFailuresPerRegion

_Widget purpose:_ PutVMScaleSet operation failures

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `PutVMScaleSet operation failures`

```kusto
let startTime = queryFrom;
let endTime = queryTo;
let location = region;
QosEtwEvent
| where PreciseTimeStamp between (startTime..endTime)
| where Region == location
| where OperationName == "PutVMScaleSetOperation"
| where Success == false
| where SliceNum(SourceAssemblyFileVersion) < 10
| extend usererr = iff (UserError == true, 1, 0)
| extend notusererr = iff (usererr  == false, 1, 0)
| summarize count(), UserErrors = sum(usererr), ServerSideErrors = sum(notusererr) by bin(PreciseTimeStamp, 5m)
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`

**Signal filters seen in KQL:** `OperationName == "PutVMScaleSetOperation"`

---
