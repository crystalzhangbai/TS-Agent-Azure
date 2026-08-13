# (top-level)

> Source: **CRP VMSS Fabric Placements Investigation Guide** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### FabricPlacements

_Widget purpose:_ Fabric Placements

Cluster: `moseisley.kusto.windows.net` · Database: `AzureCM` · Type: `Table`

```kusto
LogContainerSnapshot
| where PreciseTimeStamp between(queryFrom .. queryTo) 
    and additionalContainerProperties has queryVmssUniqueId
| extend additionalContainerProperties = parse_json(additionalContainerProperties)
| where additionalContainerProperties.VmssUniqueId == queryVmssUniqueId
| extend InstanceName = trim_start("_", roleInstanceName), ComputerName = tostring(additionalContainerProperties.ComputerName)
| summarize 
    FirstSeen = min(PreciseTimeStamp), 
    LastSeen = max(PreciseTimeStamp)
    by InstanceName, ComputerName, tenantName, nodeId, containerId, virtualMachineUniqueId, isEphemeralVM, FabricHost = Tenant, RegionFriendlyName, AvailabilityZone
| project-reorder FirstSeen, LastSeen
| order by FirstSeen desc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryVmssUniqueId}`

---
