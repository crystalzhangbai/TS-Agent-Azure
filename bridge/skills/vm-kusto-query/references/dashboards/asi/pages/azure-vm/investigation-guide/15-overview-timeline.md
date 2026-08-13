# Overview & Timeline

> Source: **Azure Host - Azure VM** dashboard, chapter **Overview & Timeline** (7 queries across 3 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Prefetch

Cluster: `egpublic.westus.kusto.windows.net` · Database: `eg` · Type: `Timeline`
Source panel: `Overview & Timeline`

**Tables:** `IaasVmOperations`
**Output columns:** `StartTime`, `EndTime`, `Health`, `Content`

```kusto
cluster('egpublic.westus.kusto.windows.net').database('eg').IaasVmOperations
| where StartTime between (startTime .. endTime)
        and ContainerId == containerId
| extend DataPathExtendedPropertiesJson = parse_json(DataPathExtendedPropertiesJson)
| extend PrefetchEndTime = todatetime(DataPathExtendedPropertiesJson.PrefetchEndTime),
        VmBootEndTime = todatetime(DataPathExtendedPropertiesJson.VmBootEndTime),
        StartVmEndTime = todatetime(DataPathExtendedPropertiesJson.StartVmEndTime)
| project StartTime = datetime_add('second', -PrefetchDurationInSeconds, PrefetchEndTime), EndTime = PrefetchEndTime, Health = case(PrefetchDurationInSeconds < 15, "Healthy", "Degraded"), Content = "Prefetch"
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`

---

### VmBoot

Cluster: `egpublic.westus.kusto.windows.net` · Database: `eg` · Type: `Timeline`
Source panel: `Overview & Timeline`

**Tables:** `IaasVmOperations`
**Output columns:** `StartTime`, `EndTime`, `Health`, `Content`

```kusto
cluster('egpublic.westus.kusto.windows.net').database('eg').IaasVmOperations
        | where StartTime between (startTime .. endTime)
                and ContainerId == containerId
        | extend DataPathExtendedPropertiesJson = parse_json(DataPathExtendedPropertiesJson)
        | extend PrefetchEndTime = todatetime(DataPathExtendedPropertiesJson.PrefetchEndTime),
                 VmBootEndTime = todatetime(DataPathExtendedPropertiesJson.VmBootEndTime),
                StartVmEndTime = todatetime(DataPathExtendedPropertiesJson.StartVmEndTime)
        | project StartTime = datetime_add('second', -VmBootDurationInSeconds, VmBootEndTime), EndTime = VmBootEndTime, Health = case(VmBootDurationInSeconds < 15, "Healthy", "Degraded"), Content = "VmBoot"
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`

---

### Provisioning

Cluster: `egpublic.westus.kusto.windows.net` · Database: `eg` · Type: `Timeline`
Source panel: `Overview & Timeline`

**Tables:** `IaasVmOperations`
**Output columns:** `StartTime`, `EndTime`, `Health`, `Content`

```kusto
cluster('egpublic.westus.kusto.windows.net').database('eg').IaasVmOperations
    | where StartTime between (startTime .. endTime)
            and ContainerId == containerId
    | extend DataPathExtendedPropertiesJson = parse_json(DataPathExtendedPropertiesJson)
    | extend PrefetchEndTime = todatetime(DataPathExtendedPropertiesJson.PrefetchEndTime),
             VmBootEndTime = todatetime(DataPathExtendedPropertiesJson.VmBootEndTime),
             StartVmEndTime = todatetime(DataPathExtendedPropertiesJson.StartVmEndTime)
    | project StartTime = VmBootEndTime, EndTime = datetime_add('second', ProvisioningDurationInSeconds, VmBootEndTime), Health = case(ProvisioningDurationInSeconds < 25, "Healthy", "Degraded"), Content = "Provisioning"
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`

---

### Xstore Server Read Latency

Cluster: `egpublic.westus.kusto.windows.net` · Database: `eg` · Type: `Timeline`
Source panel: `Overview & Timeline`

**Tables:** `IaasVmOperations`, `OsXIOSurfaceLatencyHistogramTableV2`
**Aggregations:** `summarize Q50 = max(Bin_Q50) by PreciseTimeStamp = todatetime(OsDiagHostTimeStamp), OsDiag`
**Output columns:** `StartTime`, `EndTime`, `Health`, `Content`

```kusto
cluster('egpublic.westus.kusto.windows.net').database('eg').IaasVmOperations
    | where StartTime between (startTime .. endTime)
            and ContainerId == containerId
    | extend DataPathExtendedPropertiesJson = parse_json(DataPathExtendedPropertiesJson)
    | extend PrefetchEndTime = todatetime(DataPathExtendedPropertiesJson.PrefetchEndTime),
             VmBootEndTime = todatetime(DataPathExtendedPropertiesJson.VmBootEndTime),
             StartVmEndTime = todatetime(DataPathExtendedPropertiesJson.StartVmEndTime)
    | distinct ContainerId, E2EDurationInSeconds, StartTime
    | join kind=inner(
        cluster('storageclient.eastus.kusto.windows.net').database('Fa').OsXIOSurfaceLatencyHistogramTableV2
        | where PreciseTimeStamp between ((startTime - 5m).. endTime) and SurfaceName contains containerId
        | where IsNewDisk == 1 and DiskType == 1 and HistogramTypeEnum == 33 // writes: 34 // Xstore Server Reads, Writes
        | parse BlobPath with BlobPath "?" *
        | parse SurfaceName with ContainerId "_" *
        | summarize Q50 = max(Bin_Q50) by PreciseTimeStamp = todatetime(OsDiagHostTimeStamp), OsDiagDurationInSec
        , ContainerId
    ) on ContainerId
    | where PreciseTimeStamp between (StartTime .. (datetime_add('second', E2EDurationInSeconds, StartTime)))
    | extend Health = case(Q50 <= 7000, "Healthy", "Degraded")
    | project StartTime = datetime_add('second', -OsDiagDurationInSec, PreciseTimeStamp), EndTime = PreciseTimeStamp, Health, Content = strcat(Q50/1000.0, "ms")
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`

---

### Azure Host VM TDPR Reads from Cache Latency

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Overview & Timeline`

**Tables:** `IaasVmOperations`, `OsXIOSurfaceLatencyHistogramTableV2`
**Aggregations:** `summarize Q50 = max(Bin_Q50) by PreciseTimeStamp = todatetime(OsDiagHostTimeStamp), OsDiag`
**Output columns:** `StartTime`, `EndTime`, `Health`, `Content`

```kusto
cluster('egpublic.westus.kusto.windows.net').database('eg').IaasVmOperations
    | where StartTime between (startTime .. endTime)
            and ContainerId == containerId
    | extend DataPathExtendedPropertiesJson = parse_json(DataPathExtendedPropertiesJson)
    | extend PrefetchEndTime = todatetime(DataPathExtendedPropertiesJson.PrefetchEndTime),
             VmBootEndTime = todatetime(DataPathExtendedPropertiesJson.VmBootEndTime),
             StartVmEndTime = todatetime(DataPathExtendedPropertiesJson.StartVmEndTime)
    | distinct ContainerId, E2EDurationInSeconds, StartTime
    | join kind=inner(
        cluster('storageclient.eastus.kusto.windows.net').database('Fa').OsXIOSurfaceLatencyHistogramTableV2
        | where PreciseTimeStamp between ((startTime - 5m).. endTime) and SurfaceName contains containerId
        | where IsNewDisk == 1 and DiskType == 1 and HistogramTypeEnum == 0 // writes: 34 // Xstore Server Reads, Writes
        | parse BlobPath with BlobPath "?" *
        | parse SurfaceName with ContainerId "_" *
        | summarize Q50 = max(Bin_Q50) by PreciseTimeStamp = todatetime(OsDiagHostTimeStamp), OsDiagDurationInSec
        , ContainerId
    ) on ContainerId
    | where PreciseTimeStamp between (StartTime .. (datetime_add('second', E2EDurationInSeconds, StartTime)))
    | extend Health = case(Q50 <= 7000, "Healthy", "Degraded")
    | project StartTime = datetime_add('second', -OsDiagDurationInSec, PreciseTimeStamp), EndTime = PreciseTimeStamp, Health, Content = strcat(Q50/1000.0, "ms")
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`, `{containerId}`

---

## Execution Graph Data for the VM

### EG for VM

_Widget purpose:_ Execution Graph Data for the VM

Cluster: `egpublic.westus.kusto.windows.net` · Database: `eg` · Type: `Table`
Source panel: `Overview & Timeline > Execution Graph Data for the VM`

**Tables:** `IaasVmOperations`
**Output columns:** `StartTime`, `OperationName`, `E2EDurationInSeconds`, `PrefetchDurationInSeconds`, `VmBootDurationInSeconds`, `ProvisioningDurationInSeconds`, `DataPathDurationInSeconds`, `ControlPathDurationInSeconds`, `FailureCategory`, `FailureSignature`

```kusto
IaasVmOperations
| where StartTime between (startTime .. endTime)
        and ContainerId == containerId
        and OperationName in ("CrpNewDeployment", "CrpStartVM", "CrpCreateVM")
| extend DataPathExtendedPropertiesJson = parse_json(DataPathExtendedPropertiesJson)
| extend PrefetchEndTime = DataPathExtendedPropertiesJson.PrefetchEndTime,
         VmBootEndTime = DataPathExtendedPropertiesJson.VmBootEndTime,
         StartVmEndTime = DataPathExtendedPropertiesJson.StartVmEndTime
| project StartTime, OperationName, E2EDurationInSeconds, PrefetchDurationInSeconds, VmBootDurationInSeconds, ProvisioningDurationInSeconds, DataPathDurationInSeconds, ControlPathDurationInSeconds, FailureCategory, FailureSignature, EgUrl
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`

---

## TDPR Insights for the VM (for the time selected)

### TDPR Insights 

_Widget purpose:_ TDPR Insights for the VM (for the time selected)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `Table`
Source panel: `Overview & Timeline > TDPR Insights for the VM (for the time selected)`

```kusto
StorageClientInsightsForContainer2(containerId, nodeId, startTime, endTime)
| project PreciseTimeStamp, Message, EventName, level = case(EventName contains "Update", "warning", "error") |  where EventName contains "TDPR"
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

**Signal filters seen in KQL:** `EventName contains "TDPR"`

---
