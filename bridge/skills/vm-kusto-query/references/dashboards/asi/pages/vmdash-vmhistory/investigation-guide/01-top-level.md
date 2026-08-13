# (top-level)

> Source: **VMDash - VMHistory** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "VMHistory"

Cluster: `Azurecm` · Database: `AzureCM` · Type: `ResourceGet` · Widget: `Container`

```kusto
LogNodeSnapshot
| where PreciseTimeStamp > ago(3h) and nodeId == local_nodeId
| extend hostingEnvironment = parse_json(hostingEnvironment)
| extend HostOS = tostring(hostingEnvironment.OSBaseImageName), AgentPackage = tostring(hostingEnvironment.AgentPackageName), ipAddress
| distinct Region, Tenant, DataCenterName, nodeId, ipAddress, containerCount, HostOS, AgentPackage, diskConfiguration, machinePoolName
| join kind=leftouter(
    cluster('Azuredcm').database('AzureDCMDb').ResourceSnapshotHistoryV1
    | where ResourceId == local_nodeId and PreciseTimeStamp > ago(1d)
    | summarize arg_max(PreciseTimeStamp, *)
    | project Sku, Manufacturer, Model, ResourceId
) on $left.nodeId == $right.ResourceId
| project-away ResourceId
```

**Params:** `{local_Region}`, `{local_Tenant}`, `{local_nodeId}`

---
