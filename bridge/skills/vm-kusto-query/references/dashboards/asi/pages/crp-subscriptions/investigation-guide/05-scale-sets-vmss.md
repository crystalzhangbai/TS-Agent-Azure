# Scale Sets / VMSS

> Source: **CRP Subscriptions Investigation Guide** dashboard, chapter **Scale Sets / VMSS** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Resource Group Scale Sets

_Widget purpose:_ Scale Sets / VMSS

Cluster: `azcrpbifollower` · Database: `bi_allprod` · Type: `Table`
Source panel: `Scale Sets / VMSS`

```kusto
VMScaleSet
| where PreciseTimeStamp between(queryFrom..queryTo)
| where SubscriptionId =~ querySubscriptionId
| where isempty(queryResourceGroup) or ResourceGroupName =~ queryResourceGroup
| summarize arg_max(PreciseTimeStamp, SubscriptionId, ResourceGroupName, VMScaleSetId, VMScaleSetName, VMScaleSetTimeCreated, VMScaleSetToBeDeleted, Region) by Key
| order by VMScaleSetName asc
```

**Params:** `{querySubscriptionId}`, `{queryResourceGroup}`, `{queryFrom}`, `{queryTo}`

---
