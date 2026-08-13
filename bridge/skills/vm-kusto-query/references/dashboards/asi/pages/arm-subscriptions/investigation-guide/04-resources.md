# Resources

> Source: **ARM — Subscriptions** dashboard, chapter **Resources** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## All Resources

### Subscription Resources

_Widget purpose:_ All Resources

Cluster: `argwus2nrpone.westus2` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `Resources > All Resources`

```kusto
Resources
| where subscriptionId == querySubscriptionId
| summarize arg_max(timestamp, deleted, name, type, subscriptionId, subResourceGroup, resourceGroup, location, properties) by id
| project 
    ResourceId = id, 
    ResourceName = name, 
    ResourceGroupName = resourceGroup,
    ResourceProvider = type, 
    Location = location, 
    ProvisioningState = tostring(properties.provisioningState),
    Deleted = tobool(deleted)
```

**Params:** `{querySubscriptionId}`

---
