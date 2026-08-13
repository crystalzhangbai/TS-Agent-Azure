# (top-level)

> Source: **Aztec Regions Investigation Guide** dashboard, chapter **(top-level)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Regions"

Cluster: `azurecm` · Database: `AzureCM` · Type: `ResourceGet` · Widget: `Container`

```kusto
LogClusterSnapshot
| where PreciseTimeStamp between(global_startTime..global_endTime)
| where Region =~ local_Region
| top 1 by PreciseTimeStamp desc
| project Region
```

**Params:** `{local_Region}`

---

### Region DCs and AZs

_Widget purpose:_ AZs and Data Centers

Cluster: `azurecm` · Database: `azurecm` · Type: `Table`

```kusto
LogClusterSnapshot 
| where PreciseTimeStamp between(global_startTime..global_endTime)
| where Region == queryRegion
| summarize Clusters = dcount(Tenant) by AvailabilityZone, DataCenterName
| order by DataCenterName asc, AvailabilityZone asc
```

**Params:** `{queryRegion}`

---
