# Top 15 VMSS resources undergoing updates

> Source: **NRP - PUT VMScaleSet Operation drill down** dashboard, chapter **Top 15 VMSS resources undergoing updates** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### TopVmssResourcesPerSub

_Widget purpose:_ Top 15 VMSS resources undergoing updates

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Top 15 VMSS resources undergoing updates`

```kusto
QosEtwEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where Region == region
| where SubscriptionId == subId
| where OperationName == "PutVMScaleSetOperation"
| summarize CountOfOperations = count() by ResourceGroup, ResourceName
| order by CountOfOperations desc 
| take 15
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`, `{subId}`

**Signal filters seen in KQL:** `OperationName == "PutVMScaleSetOperation"`

---
