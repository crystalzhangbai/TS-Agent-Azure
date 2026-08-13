# VMSS Extensions

> Source: **CRP — Scale Sets** dashboard, chapter **VMSS Extensions** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Query VMSS Extensions

_Widget purpose:_ VMSS Extensions

Cluster: `azcrpbifollower` · Database: `bi_allprod` · Type: `Table`
Source panel: `VMSS Extensions`

```kusto
VMScaleSetVMExtension
| where PreciseTimeStamp between (min_of(queryTo-2h, queryFrom) .. queryTo)
| where SubscriptionId == querySubId
| where ResourceGroupName =~ queryResourceGroup
| where VMScaleSetName =~ queryVmssName
| summarize arg_max(PreciseTimeStamp, *) by Publisher, Type, InputVersion, Name, Id
| order by Publisher asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubId}`, `{queryResourceGroup}`, `{queryVmssName}`

---
