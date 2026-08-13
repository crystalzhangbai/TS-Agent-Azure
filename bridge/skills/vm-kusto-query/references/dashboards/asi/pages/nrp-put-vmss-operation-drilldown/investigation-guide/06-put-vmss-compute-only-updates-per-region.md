# PUT Vmss Compute-only updates per region

> Source: **NRP - PUT VMScaleSet Operation drill down** dashboard, chapter **PUT Vmss Compute-only updates per region** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### ComputeOnlyUpdatesPerRegion

_Widget purpose:_ PUT Vmss Compute-only updates per region

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `PUT Vmss Compute-only updates per region`

```kusto
FrontendOperationEtwEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where Region == region
| where OperationName in ("PutVMScaleSetOperation")
| extend coU = iff (EventCode == "VmssOperationIsComputeOnlyUpdate", 1, 0)
| summarize computeOnlyOps= dcountif(OperationId, coU == 1) , putVmssOPCount= dcount(OperationId) by bin(PreciseTimeStamp, 5m)
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`

---
