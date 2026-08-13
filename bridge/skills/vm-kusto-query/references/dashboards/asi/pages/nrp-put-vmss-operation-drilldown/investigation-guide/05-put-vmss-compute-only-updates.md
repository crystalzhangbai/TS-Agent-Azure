# Put Vmss Compute only updates

> Source: **NRP - PUT VMScaleSet Operation drill down** dashboard, chapter **Put Vmss Compute only updates** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### CoUPerSubscription

_Widget purpose:_ Put Vmss Compute only updates

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Put Vmss Compute only updates`

```kusto
FrontendOperationEtwEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where Region == region
| where SubscriptionId == subId
| where OperationName in ("PutVMScaleSetOperation")
| extend coU = iff (EventCode == "VmssOperationIsComputeOnlyUpdate", 1, 0)
| extend updateVmssWhenCou = iff (Message startswith "Saving VMSS resource with updated properties.", 1, 0)
| summarize computeOnlyUpdates= dcountif(OperationId, coU == 1) , vmssUpdatedWhenComputeOnlyUpdates = sum(updateVmssWhenCou),  totalPutVmssOperations= dcount(OperationId) by bin(PreciseTimeStamp, 5m)
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`, `{subId}`

---
