# (top-level)

> Source: **Aztec Availability Zones Investigation Guide** dashboard, chapter **(top-level)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Availability Zones"

Cluster: `azurecm` · Database: `azurecm` · Type: `ResourceGet` · Widget: `Container`

```kusto
LogClusterSnapshot 
| where PreciseTimeStamp between(global_startTime..global_endTime)
| where Region == local_Region and AvailabilityZone == local_AvailabilityZone
| top 1 by PreciseTimeStamp
```

**Params:** `{local_Region}`, `{local_AvailabilityZone}`

---

### Availability Zone Data Centers

_Widget purpose:_ Data Centers

Cluster: `azurecm` · Database: `azurecm` · Type: `Table`

```kusto
LogClusterSnapshot 
| where PreciseTimeStamp between(global_startTime..global_endTime)
| where Region == queryRegion and AvailabilityZone == queryAvailabilityZone
| summarize Clusters = dcount(Tenant) by DataCenterName
| order by DataCenterName asc
| extend AzDataCenterName = DataCenterName
```

**Params:** `{queryRegion}`, `{queryAvailabilityZone}`

---
