# Resources

> Source: **ARM Resource Groups Investigation Guide** dashboard, chapter **Resources** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Resource Group Resources

_Widget purpose:_ Resources

Cluster: `armprod` · Database: `CosmosToKusto` · Type: `Table`
Source panel: `Resources`

```kusto
ResourcesTable
| where SubscriptionId == querySubscriptionId and ResourceGroupName =~ queryResourceGroupName
| summarize arg_max(SnapshotDate, *) by ResourceId
| extend tokens = split(ResourceId, "/")
| extend ResourceName = tostring(tokens[array_length(tokens) - 1])
| extend ResourceProvider = tokens[0]
| project-away tokens
| order by ResourceName asc
```

**Params:** `{querySubscriptionId}`, `{queryResourceGroupName}`

---
