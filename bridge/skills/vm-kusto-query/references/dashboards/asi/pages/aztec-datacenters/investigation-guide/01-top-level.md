# (top-level)

> Source: **Aztec DataCenters Investigation Guide** dashboard, chapter **(top-level)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "DataCenters"

Cluster: `azurecm` · Database: `azurecm` · Type: `ResourceGet` · Widget: `Container`

```kusto
LogClusterSnapshot 
| where (Region == local_Region or RegionFriendlyName == local_Region) and DataCenterName == local_DataCenterName
| top 1 by PreciseTimeStamp desc
```

**Params:** `{local_DataCenterName}`, `{local_Region}`

---

### DataCenter Clusters

_Widget purpose:_ Clusters / Tenants

Cluster: `azurecm` · Database: `azurecm` · Type: `Table`

```kusto
LogClusterSnapshot 
| where PreciseTimeStamp between(global_startTime..global_endTime)
| where (Region == queryRegion or RegionFriendlyName == queryRegion) and DataCenterName == queryDataCenter
| summarize arg_max(PreciseTimeStamp, *) by Tenant
| project Tenant, ClusterName = Tenant, buildVersion
| order by Tenant asc
```

**Params:** `{queryRegion}`, `{queryDataCenter}`

---
