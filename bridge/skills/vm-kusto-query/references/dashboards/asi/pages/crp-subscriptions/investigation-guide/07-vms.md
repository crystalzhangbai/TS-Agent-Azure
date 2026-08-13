# VMs

> Source: **CRP Subscriptions Investigation Guide** dashboard, chapter **VMs** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## VMs

### Subscription VMs

_Widget purpose:_ VMs

Cluster: `azcrpbifollower` · Database: `bi_allprod` · Type: `Table`
Source panel: `VMs > VMs`

```kusto
VM
| where PreciseTimeStamp between(queryFrom..queryTo)
| where SubscriptionId =~ querySubscriptionId
| summarize FirstSeen = min(PreciseTimeStamp), LastSeen = max(PreciseTimeStamp), arg_max(PreciseTimeStamp, *) by VMId
| order by ResourceGroupName asc, LastSeen desc
```

**Params:** `{querySubscriptionId}`, `{queryResourceGroupName}`, `{queryFrom}`, `{queryTo}`

---
