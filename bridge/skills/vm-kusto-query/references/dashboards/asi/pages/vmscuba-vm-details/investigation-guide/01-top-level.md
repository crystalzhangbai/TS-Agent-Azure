# (top-level)

> Source: **VM Scuba - VM Details** dashboard, chapter **(top-level)** (3 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get-VMDetails

_Widget purpose:_ VM Details

Cluster: `moseisley.kusto.windows.net` · Database: `AzureCM` · Type: `Single` · Widget: `Container`

```kusto
cluster('moseisley.kusto.windows.net').database('AzureCM').LogContainerSnapshot 
| where roleInstanceName == tolower(RoleInstanceName) 
|distinct subscriptionId,roleInstanceName, nodeId, containerId, virtualMachineUniqueId, tenantName
```

**Params:** `{queryFrom}`, `{queryTo}`, `{RoleInstanceName}`

---

### Get-TOR

_Widget purpose:_ VM Details

Cluster: `moseisley.kusto.windows.net` · Database: `AzureCM` · Type: `Single` · Widget: `Container`

```kusto
LogContainerSnapshot
//| where TIMESTAMP> datetime({startTime}) and TIMESTAMP <= datetime({endTime})
| where subscriptionId == subscriptionId
| where roleInstanceName == roleInstanceName
| summarize arg_max(PreciseTimeStamp,*) by Tenant, containerId, containerType, nodeId, tenantName, subscriptionId, availabilitySetName, roleInstanceName, virtualMachineUniqueId
| distinct containerId,nodeId,roleInstanceName, subscriptionId,containerType
| join kind= inner
    hint.strategy = shuffle ( cluster("azphynet").database("azdhmds").Servers
    | project NodeId = tolower(NodeId) , DeviceName = tolower(DeviceName)
)
on $left.nodeId == $right.NodeId
| project NodeId, DeviceName,containerId,nodeId,roleInstanceName, subscriptionId ,containerType
| join kind= inner
    hint.strategy = shuffle (cluster("azphynet").database("azdhmds").DeviceInterfaceLinks)
on $left.DeviceName == $right.StartDevice
| project containerId,nodeId,roleInstanceName,DeviceName = EndDevice, subscriptionId,containerType
| join kind=inner
(
    cluster('aznwalerting.kusto.windows.net').database('aznwmds').Devices
)
on DeviceName
| distinct TOR= DeviceName
```

**Params:** `{queryFrom}`, `{queryTo}`, `{subscriptionId}`, `{roleInstanceName}`

---

### Get-SessionId

_Widget purpose:_ VM Details

Cluster: `AzureCM.kusto.windows.net` · Database: `AzureCM` · Type: `Single` · Widget: `Container`

```kusto
cluster("AzureCM").database("AzureCM").LiveMigrationContainerDetailsEventLog
| where sourceContainerId == containerId
|distinct sessionId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`

---
