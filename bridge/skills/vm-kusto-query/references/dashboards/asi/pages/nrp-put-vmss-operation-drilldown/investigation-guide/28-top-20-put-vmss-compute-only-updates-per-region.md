# Top 20 Put Vmss Compute-only updates per region

> Source: **NRP - PUT VMScaleSet Operation drill down** dashboard, chapter **Top 20 Put Vmss Compute-only updates per region** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### TopPutVmssCouPerRegion

_Widget purpose:_ Top 20 Put Vmss Compute-only updates per region

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Top 20 Put Vmss Compute-only updates per region`

```kusto
FrontendOperationEtwEvent
| where PreciseTimeStamp between(queryFrom..queryTo)
| where OperationName == "PutVMScaleSetOperation"
| where Region == region
| extend isCoU = iff (EventCode == "VmssOperationIsComputeOnlyUpdate", 1, 0)
| extend Resource = strcat(ResourceGroup, "+", ResourceName)
| extend slice = SliceNum(SourceAssemblyFileVersion)
| project PreciseTimeStamp, OperationId, OperationName, Region, SubscriptionId, Resource, isCoU, slice
| summarize totalPutVmssOps= dcount(OperationId), computeOnlyOps = dcountif(OperationId, isCoU ==1 ) by SubscriptionId, Region, Resource, slice
| extend computeOnlyPc = round (1.0 * computeOnlyOps / totalPutVmssOps, 2) *100
| order by computeOnlyOps desc
| take 20
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`

**Signal filters seen in KQL:** `OperationName == "PutVMScaleSetOperation"`

---
