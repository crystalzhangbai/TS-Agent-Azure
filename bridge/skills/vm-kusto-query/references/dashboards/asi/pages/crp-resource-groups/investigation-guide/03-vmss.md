# VMSS

> Source: **CRP Resource Groups Investigation Guide** dashboard, chapter **VMSS** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Scale Sets

### Resource Group Scale Sets

_Widget purpose:_ Scale Sets

Cluster: `azcrpbifollower` · Database: `bi_allprod` · Type: `Table`
Source panel: `VMSS > Scale Sets`

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
