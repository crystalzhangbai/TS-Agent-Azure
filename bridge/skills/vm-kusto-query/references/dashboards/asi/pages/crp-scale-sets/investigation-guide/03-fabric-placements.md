# Fabric Placements

> Source: **CRP — Scale Sets** dashboard, chapter **Fabric Placements** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### FabricPlacements

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Fabric Placements`

```kusto
let containerIds = LogContainerSnapshot
| where PreciseTimeStamp between(queryFrom .. queryTo) 
    and additionalContainerProperties has queryVmssUniqueId    
| extend additionalContainerProperties = parse_json(additionalContainerProperties)
| where additionalContainerProperties.VmssUniqueId == queryVmssUniqueId
| distinct containerId;
LogContainerSnapshot
| where PreciseTimeStamp between(queryFrom .. now()) 
| where containerId in (containerIds)
| extend ComputerName = tostring(parse_json(additionalContainerProperties).ComputerName)
| summarize 
    LastSeen = max(PreciseTimeStamp)
    by creationTime = todatetime(creationTime), roleInstanceName, ComputerName, tenantName, nodeId, containerId, virtualMachineUniqueId, isEphemeralVM, FabricHost = Tenant, RegionFriendlyName, updateDomain, AvailabilityZone
| project-reorder creationTime, LastSeen
| order by roleInstanceName asc, creationTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryVmssUniqueId}`

---
