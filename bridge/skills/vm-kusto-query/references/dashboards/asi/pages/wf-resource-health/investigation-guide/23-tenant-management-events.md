# Tenant Management Events

> Source: **EEE RDOS — WF Resource Health** dashboard, chapter **Tenant Management Events** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Query TMMgmtTenantEventsEtwTable

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Tenant Management Events`

```kusto
cluster("azcsupfollower").database("AzureCM").TMMgmtTenantEventsEtwTable
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where TenantName == queryTenantName
| project PreciseTimeStamp,Tenant, RoleInstance, Message
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---
