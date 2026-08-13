# Tenants

> Source: **Aztec — Clusters** dashboard, chapter **Tenants** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Tenants

### Cluster Tenants

_Widget purpose:_ Tenants

Cluster: `azurecm` · Database: `AzureCM` · Type: `Table`
Source panel: `Tenants > Tenants`

```kusto
LogTenantSnapshot
| where PreciseTimeStamp between(queryFrom..queryTo)
| where Tenant == queryCluster
| summarize arg_max(PreciseTimeStamp, *) by tenantName
| project tenantName, AvailabilityZone, subscriptionId, todatetime(dateCreated), state, tenantOwners
```

**Params:** `{queryCluster}`, `{queryFrom}`, `{queryTo}`

---
