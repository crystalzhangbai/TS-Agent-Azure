# VM Charts

> Source: **Azure Host Compare Investigation Guide** dashboard, chapter **VM Charts** (8 queries across 8 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## VM Available Memory {{nodeId1}}

### Azure Host VMs Memory Usage

_Widget purpose:_ VM Available Memory {{nodeId1}}

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Charts > VM Available Memory {{nodeId1}}`

```kusto
VmCounterFiveMinuteRoleInstanceCentralBondTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId // and CounterName contains @"\Hyper-V Dynamic Memory VM" and CounterName contains "Current Pressure"
        and CounterName contains "Guest Available Memory"
| project PreciseTimeStamp, RoleInstanceId, AverageCounterValue
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

## VM Available Memory {{nodeId2}}

### Azure Host VMs Memory Usage

_Widget purpose:_ VM Available Memory {{nodeId2}}

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Charts > VM Available Memory {{nodeId2}}`

```kusto
VmCounterFiveMinuteRoleInstanceCentralBondTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId // and CounterName contains @"\Hyper-V Dynamic Memory VM" and CounterName contains "Current Pressure"
        and CounterName contains "Guest Available Memory"
| project PreciseTimeStamp, RoleInstanceId, AverageCounterValue
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

## VM CPU {{nodeId1}}

### Azure Host VMs CPU Usage

_Widget purpose:_ VM CPU {{nodeId1}}

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Charts > VM CPU {{nodeId1}}`

```kusto
VmCounterFiveMinuteRoleInstanceCentralBondTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and CounterName == "Percentage CPU"
| project PreciseTimeStamp, RoleInstanceId, AverageCounterValue
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

## VM CPU {{nodeId2}}

### Azure Host VMs CPU Usage

_Widget purpose:_ VM CPU {{nodeId2}}

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Charts > VM CPU {{nodeId2}}`

```kusto
VmCounterFiveMinuteRoleInstanceCentralBondTable
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeId and CounterName == "Percentage CPU"
| project PreciseTimeStamp, RoleInstanceId, AverageCounterValue
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

## VM Disk IOPS {{nodeId1}}

### Azure Host StorageClient VMs Disk IOPS

_Widget purpose:_ VM Disk IOPS {{nodeId1}}

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Charts > VM Disk IOPS {{nodeId1}}`

```kusto
let containers = cluster("AzureCM.kusto.windows.net").database("AzureCM").LogContainerSnapshot
| where PreciseTimeStamp between ((startTime - 2h) .. (endTime + 1h)) and nodeId == nodeIdStr
| summarize arg_max(PreciseTimeStamp, roleInstanceName) by containerId
| distinct containerId, roleInstanceName
| extend metric = strcat(roleInstanceName, " (", substring(containerId, 0, 13), ")")
;
OsXIOSurfaceCounterTable | union (OsRDSSDSurfaceCounterTable)
| extend OsDiagHostTimeStamp = todatetime(OsDiagHostTimeStamp)
| union (OsUltraSSDCounterTable | extend SurfaceName = ContainerId, OsDiagHostTimeStamp = PreciseTimeStamp)
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeIdStr and IsNewDisk == 0
| extend containerId = tostring(case(indexof(SurfaceName, "~") > 0, split(SurfaceName, "~")[0], split(SurfaceName, "_")[0]))
| summarize IOPS = sum(IOPS) by bin(todatetime(OsDiagHostTimeStamp), 5m), containerId
| join kind=leftouter(
    containers
) on containerId
| project-away containerId, containerId1
```

**Params:** `{nodeIdStr}`, `{startTime}`, `{endTime}`

---

## VM Disk IOPS {{nodeId2}}

### Azure Host StorageClient VMs Disk IOPS

_Widget purpose:_ VM Disk IOPS {{nodeId2}}

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Charts > VM Disk IOPS {{nodeId2}}`

```kusto
let containers = cluster("AzureCM.kusto.windows.net").database("AzureCM").LogContainerSnapshot
| where PreciseTimeStamp between ((startTime - 2h) .. (endTime + 1h)) and nodeId == nodeIdStr
| summarize arg_max(PreciseTimeStamp, roleInstanceName) by containerId
| distinct containerId, roleInstanceName
| extend metric = strcat(roleInstanceName, " (", substring(containerId, 0, 13), ")")
;
OsXIOSurfaceCounterTable | union (OsRDSSDSurfaceCounterTable)
| extend OsDiagHostTimeStamp = todatetime(OsDiagHostTimeStamp)
| union (OsUltraSSDCounterTable | extend SurfaceName = ContainerId, OsDiagHostTimeStamp = PreciseTimeStamp)
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeIdStr and IsNewDisk == 0
| extend containerId = tostring(case(indexof(SurfaceName, "~") > 0, split(SurfaceName, "~")[0], split(SurfaceName, "_")[0]))
| summarize IOPS = sum(IOPS) by bin(todatetime(OsDiagHostTimeStamp), 5m), containerId
| join kind=leftouter(
    containers
) on containerId
| project-away containerId, containerId1
```

**Params:** `{nodeIdStr}`, `{startTime}`, `{endTime}`

---

## VM Disk MBPS {{nodeId1}}

### Azure Host VM StorageClient Disk MBPS

_Widget purpose:_ VM Disk MBPS {{nodeId1}}

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Charts > VM Disk MBPS {{nodeId1}}`

```kusto
let containers = cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp between ((startTime - 2h) .. (endTime + 1h)) and nodeId == nodeIdStr
| summarize arg_max(PreciseTimeStamp, roleInstanceName) by containerId
| distinct containerId, roleInstanceName
| extend metric = strcat(roleInstanceName, " (", substring(containerId, 0, 13), ")")
;
OsXIOSurfaceCounterTable | union (OsRDSSDSurfaceCounterTable)
| union (OsUltraSSDCounterTable | extend SurfaceName = ContainerId)
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeIdStr and IsNewDisk == 0
| extend containerId = tostring(case(indexof(SurfaceName, "~") > 0, split(SurfaceName, "~")[0], split(SurfaceName, "_")[0]))
| summarize MBPS = sum(MBPS) by bin(PreciseTimeStamp, 5m), containerId
| join kind=inner(
    containers
) on containerId
| project-away containerId, containerId1
```

**Params:** `{nodeIdStr}`, `{startTime}`, `{endTime}`

---

## VM Disk MBPS {{nodeId2}}

### Azure Host VM StorageClient Disk MBPS

_Widget purpose:_ VM Disk MBPS {{nodeId2}}

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `VM Charts > VM Disk MBPS {{nodeId2}}`

```kusto
let containers = cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp between ((startTime - 2h) .. (endTime + 1h)) and nodeId == nodeIdStr
| summarize arg_max(PreciseTimeStamp, roleInstanceName) by containerId
| distinct containerId, roleInstanceName
| extend metric = strcat(roleInstanceName, " (", substring(containerId, 0, 13), ")")
;
OsXIOSurfaceCounterTable | union (OsRDSSDSurfaceCounterTable)
| union (OsUltraSSDCounterTable | extend SurfaceName = ContainerId)
| where PreciseTimeStamp between (startTime .. endTime) and NodeId == nodeIdStr and IsNewDisk == 0
| extend containerId = tostring(case(indexof(SurfaceName, "~") > 0, split(SurfaceName, "~")[0], split(SurfaceName, "_")[0]))
| summarize MBPS = sum(MBPS) by bin(PreciseTimeStamp, 5m), containerId
| join kind=inner(
    containers
) on containerId
| project-away containerId, containerId1
```

**Params:** `{nodeIdStr}`, `{startTime}`, `{endTime}`

---
