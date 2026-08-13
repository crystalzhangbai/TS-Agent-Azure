# (top-level)

> Source: **EEE Storage - Managed Disk Events** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Managed Disk Lifecycle Events

Cluster: `disks.kusto.windows.net` · Database: `Disks` · Type: `Table`

```kusto
DiskRPResourceLifecycleEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where resourceName contains resname
| project PreciseTimeStamp,resourceName, resourceGroupName,  pseudosubscriptionId, blobUrl, diskEvent, RPTenant
```

**Params:** `{queryFrom}`, `{queryTo}`, `{resname}`

---
