# Containers

> Source: **CRP — VMs** dashboard, chapter **Containers** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Fabric Placements

### VM Fabric Containers

_Widget purpose:_ Fabric Placements

Cluster: `Azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Containers > Fabric Placements`

```kusto
cluster('Azcsupfollower').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp between (global_startTime .. now())
| where virtualMachineUniqueId == queryVmId
| summarize LastSeen = arg_max(PreciseTimeStamp, *) by creationTime, roleInstanceName, Tenant, tenantName, containerId, nodeId, virtualMachineUniqueId, containerType, Region
| extend creationTime = todatetime(creationTime)
| extend OSType = parse_json(features).["Fabric.OSType"]
| order by creationTime asc
```

**Params:** `{querySubscriptionId}`, `{queryVmId}`, `{global_startTime}`, `{global_endTime}`

---
