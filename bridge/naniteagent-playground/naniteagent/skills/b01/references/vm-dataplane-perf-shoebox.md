# RDOS Shoebox VM Performance Dashboard — Tile Reference

**Dashboard:** `RDOS / Shoebox / VMPerf-WithParameters`
**Source JSON:** `RDOS_Shoebox_VMPerf_WithParameters.json`

## Template Parameters

| Name | Display Name | Type | Default / Example | Used As | Affected Tiles | Hint Query |
|------|-------------|------|-------------------|---------|----------------|------------|
| `Region` | Region | string | `(all)` → e.g. `AzComputeShoeboxWUS2` | MDM `account` field override on all dataSources (`//dataSources`) | All MDM tiles (1–6, 8, 10–11, 13–23, 24 MDM) | `cluster('Azurecm').database('AzureCM').LogClusterSnapshot \| where PreciseTimeStamp >= ago(1h) \| summarize by shoeboxMdmAccountName` — filter pattern `*ComputeShoebox*` |
| `VMID` | VM unique ID (`virtualMachineUniqueId`) | string | `<virtualMachineUniqueId>` (or comma-separated list) | Dimension filter `ResourceId` = `{VMID}` (override key `value` on `//*[id='ResourceId']`) | All MDM tiles and all Kusto tiles via `{ResourceId}` token | MDM dimension `ResourceId` from `AzComputeShoeboxWUS2 / Shoebox / Percentage CPU` |

> ⚠️ Tiles marked **[CONFIDENTIAL]** must NOT be shared with external customers.

---

## Tile 1 — % CPU (Average)

| Field | Value |
|-------|-------|
| **Type** | MDM chart |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Region}` parameter (e.g. `AzComputeShoeboxWUS2`) |
| **MDM Namespace** | `Shoebox` |
| **Metric(s)** | `Percentage CPU` |
| **Sampling Type** | Average |
| **Dimension Filter** | `ResourceId` = `{VMID}` *(runtime-substituted from template parameter)* |
| **Split By** | `ResourceId` |

---

## Tile 2 — Data/OS/Temp Disk Queue Length (per Lun Average)

| Field | Value |
|-------|-------|
| **Type** | MDM chart |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Region}` parameter (e.g. `AzComputeShoeboxWUS2`) |
| **MDM Namespace** | `Shoebox` |
| **Metric(s)** | `Data Disk Queue Depth`, `OS Disk Queue Depth`, `Temp Disk Queue Depth` |
| **Sampling Type** | Max |
| **Dimension Filter** | `ResourceId` = `{VMID}` *(runtime-substituted from template parameter)* |
| **Split By** | `LUN` *(Data Disk Queue Depth only)*, `ResourceId` |

---

## Tile 3 — Network In Bytes Per Minute (Max)

| Field | Value |
|-------|-------|
| **Type** | MDM chart |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Region}` parameter (e.g. `AzComputeShoeboxWUS2`) |
| **MDM Namespace** | `Shoebox` |
| **Metric(s)** | `Network In Total` |
| **Sampling Type** | Max |
| **Dimension Filter** | `ResourceId` = `{VMID}` *(runtime-substituted from template parameter)* |
| **Split By** | `ResourceId` |

---

## Tile 4 — Network Out Bytes Per Minute (Max)

| Field | Value |
|-------|-------|
| **Type** | MDM chart |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Region}` parameter (e.g. `AzComputeShoeboxWUS2`) |
| **MDM Namespace** | `Shoebox` |
| **Metric(s)** | `Network Out Total` |
| **Sampling Type** | Max |
| **Dimension Filter** | `ResourceId` = `{VMID}` *(runtime-substituted from template parameter)* |
| **Split By** | `ResourceId` |

---

## Tile 5 — Data/OS/Temp Disk Read Bytes/sec Per Lun (Average)

| Field | Value |
|-------|-------|
| **Type** | MDM chart |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Region}` parameter (e.g. `AzComputeShoeboxWUS2`) |
| **MDM Namespace** | `Shoebox` |
| **Metric(s)** | `Data Disk Read Bytes/sec`, `OS Disk Read Bytes/sec`, `Data Disk Max Burst Bandwidth`, `Data Disk Target Bandwidth`, `OS Disk Max Burst Bandwidth`, `OS Disk Target Bandwidth`, `Temp Disk Read Bytes/sec` |
| **Sampling Type** | Max |
| **Dimension Filter** | `ResourceId` = `{VMID}` *(runtime-substituted from template parameter)* |
| **Split By** | `LUN` *(Data Disk metrics only)*, `ResourceId` |

---

## Tile 6 — Data/OS/Temp Disk Write Bytes/sec (Per Lun Average)

| Field | Value |
|-------|-------|
| **Type** | MDM chart |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Region}` parameter (e.g. `AzComputeShoeboxWUS2`) |
| **MDM Namespace** | `Shoebox` |
| **Metric(s)** | `Data Disk Write Bytes/sec`, `OS Disk Write Bytes/sec`, `Temp Disk Write Bytes/sec` |
| **Sampling Type** | Max |
| **Dimension Filter** | `ResourceId` = `{VMID}` *(runtime-substituted from template parameter)* |
| **Split By** | `LUN` *(Data Disk Write Bytes/sec only)*, `ResourceId` |

---

## Tile 7 — VM Performance Dashboard (Header)

| Field | Value |
|-------|-------|
| **Type** | HTML |
| **Content** | Dashboard header tile showing parameter usage instructions (`Region` = MDM account, `VMID` = VM resource ID), confidentiality notice for starred tiles, permissions table (rdos, AzureCM, Vmainsight, Xstore, Azcrp, aznwsdn clusters with required idweb/myAccess groups), and link to aka.ms/vmdash and the VM Performance Dashboard TSG |

---

## Tile 8 — Data/OS/Temp Disk Latency (per Lun Average, milliseconds)

| Field | Value |
|-------|-------|
| **Type** | MDM chart |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Region}` parameter (e.g. `AzComputeShoeboxWUS2`) |
| **MDM Namespace** | `Shoebox` |
| **Metric(s)** | `Data Disk Latency`, `OS Disk Latency`, `Temp Disk Latency` |
| **Sampling Type** | Max |
| **Dimension Filter** | `ResourceId` = `{VMID}` *(runtime-substituted from template parameter)* |
| **Split By** | `LUN` *(Data Disk Latency only)*, `ResourceId` |

---

## Tile 9 — % Memory Pressure (Max) [CONFIDENTIAL]

| Field | Value |
|-------|-------|
| **Type** | Kusto chart |
| **Data Source** | Kusto |
| **Cluster** | `https://azcore.centralus.kusto.windows.net` |
| **Database** | `Fa` |
| **Table(s)** | `VmHealthRawStateEtwTable`, `VmCounterFiveMinuteRoleInstanceCentralBondTable` |

**Key KQL logic:**
```kql
// {ResourceId} = VM unique ID(s) from VMID template parameter
// {startTime}, {endTime} = dashboard time range
let vmid = split("{ResourceId}", ",");
let starttime = datetime({startTime});
let endtime = datetime({endTime});
let containerids = VmHealthRawStateEtwTable
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where VirtualMachineUniqueId in (vmid)
| summarize by ContainerId;
VmCounterFiveMinuteRoleInstanceCentralBondTable
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where VmId in(containerids)
| where isnotempty(RoleInstanceId)
| where CounterName contains "Maximum Pressure"
| project TIMESTAMP, MaxCounterValue, RoleInstanceId
```

---

## Tile 10 — Data/OS/Temp Disk Read IOPS per Lun (Average)

| Field | Value |
|-------|-------|
| **Type** | MDM chart |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Region}` parameter (e.g. `AzComputeShoeboxWUS2`) |
| **MDM Namespace** | `Shoebox` |
| **Metric(s)** | `Data Disk Read Operations/Sec`, `OS Disk Read Operations/Sec`, `Data Disk Max Burst IOPS`, `OS Disk Max Burst IOPS`, `Data Disk Target IOPS`, `OS Disk Target IOPS`, `Temp Disk Read Operations/Sec` |
| **Sampling Type** | Max |
| **Dimension Filter** | `ResourceId` = `{VMID}` *(runtime-substituted from template parameter)* |
| **Split By** | `LUN` *(Data Disk and OS/Data Target IOPS metrics)*, `ResourceId` |

---

## Tile 11 — Data/OS/Temp Disk Write IOPS per Lun (Average)

| Field | Value |
|-------|-------|
| **Type** | MDM chart |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Region}` parameter (e.g. `AzComputeShoeboxWUS2`) |
| **MDM Namespace** | `Shoebox` |
| **Metric(s)** | `Data Disk Write Operations/Sec`, `OS Disk Write Operations/Sec`, `Temp Disk Write Operations/Sec` |
| **Sampling Type** | Max |
| **Dimension Filter** | `ResourceId` = `{VMID}` *(runtime-substituted from template parameter)* |
| **Split By** | `LUN` *(Data Disk Write Operations/Sec only)*, `ResourceId` |

---

## Tile 12 — VM History, HostAnalyzer Command, NetVMA Link and Physical Resource Info [CONFIDENTIAL]

| Field | Value |
|-------|-------|
| **Type** | Kusto grid |
| **Data Source** | Kusto |
| **Cluster** | `https://azurecm.kusto.windows.net` |
| **Database** | `AzureCM` |
| **Table(s)** | `LogContainerSnapshot` (primary); cross-cluster: `Aznwsdn/aznwmds/MdmVfpVnetAccountMaps`, `Azurecm/AzureCM/LogNodeSnapshot`, `Azurecm/AzureCM/LogContainerPolicySnapshot`, `LogNodeNetworkSpineLevelInformation`, `vmainsight/CAD/CADDAILY` |

**Key KQL logic:**
```kql
// {ResourceId} = VM unique ID(s); {startTime}, {endTime} = dashboard time range
let vmids = split("{ResourceId}", ",");
let starttime = datetime({startTime});
let endtime = datetime({endTime});
let allvms = LogContainerSnapshot  // azurecm/AzureCM
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| summarize arg_max(PreciseTimeStamp, *) by containerId
| extend HostAnalyzerCommand = strcat(@"\\reddog\Builds\...\HostAnalyzer.ps1 -cluster ", Tenant, @" -nodeId ", nodeId, @" -containerId ", containerId, @" -startTime ", "{startTime}", @" -endTime ", "{endTime}")
| extend AsiLink       = strcat("https://asi.azure.ms/services/Azure%20Host/pages/Azure%20VM?containerId=", containerId)
| extend NetVMALink     = strcat("https://aka.ms/netvma/?startTime={startTime}&endTime={endTime}&value=", containerId)
| extend NodeDatapathLink = "", ContainerVFPLink = ""  // Jarvis VFP dashboard deep-links (fill in if you have the exact link format)
| project ContainerCreation, LastObserveTime, subid, Region, roleInstanceName, virtualMachineUniqueId, VMType,
          HostAnalyzerCommand, AsiLink, NetVMALink, VMEvents, NodeDatapathLink, ContainerVFPLink, Tenant, nodeId, containerId;
let nodeids = toscalar(allvms | summarize make_set(nodeId));
allvms
| join kind=inner (cluster("Aznwsdn.kusto.windows.net").database("aznwmds").MdmVfpVnetAccountMaps)
    on $left.Tenant == $right.Cluster
| join kind=inner (cluster("Azurecm").database("AzureCM").LogNodeSnapshot | where nodeId in~ (allvms | distinct nodeId))
    on Tenant, nodeId
| join kind=inner (cluster("Azurecm").database("AzureCM").LogContainerPolicySnapshot
    | extend physicalCores = todouble(virtualCores) * todouble(coreLimit) / 100.0 + todouble(overheadPhysicalCores) / 1000.0)
    on containerType, Tenant, machinePoolName
| join kind=inner (LogNodeNetworkSpineLevelInformation | where nodeId in~ (nodeids))
    on nodeId
| join kind=inner (cluster("vmainsight.kusto.windows.net").database("CAD").CADDAILY | where NodeId in~ (allvms | distinct nodeId))
    on $left.containerId == $right.ContainerId
| project ContainerCreation, LastObserveTime, subid, Region, roleInstanceName, virtualMachineUniqueId, VMType,
          HostAnalyzerCommand, AsiLink, NetVMALink, ContainerVFPLink, NodeDatapathLink,
          virtualCores, coreLimit, physicalCores, memoryInMB, networkBandwidthInKbps, diskInMiB,
          Tenant, tenantName, nodeId, containerId, GA_GuestOSVersion, Hardware_Location,
          t1NetworkSpine, t2NetworkSpine, Network_TOR2, Hardware_Rack, StorageCluster1..4,
          containerType, machinePoolName, deploymentGeneration
| order by ContainerCreation asc
```

---

## Tile 13 — CPU Credits Remaining (Min)

| Field | Value |
|-------|-------|
| **Type** | MDM chart |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Region}` parameter (e.g. `AzComputeShoeboxWUS2`) |
| **MDM Namespace** | `Shoebox` |
| **Metric(s)** | `CPU Credits Remaining` |
| **Sampling Type** | Min |
| **Dimension Filter** | `ResourceId` = `{VMID}` *(runtime-substituted from template parameter)* |
| **Split By** | `ResourceId` |

---

## Tile 14 — Total VM Data Disk Read Bytes/sec

| Field | Value |
|-------|-------|
| **Type** | MDM chart |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Region}` parameter (e.g. `AzComputeShoeboxWUS2`) |
| **MDM Namespace** | `Shoebox` |
| **Metric(s)** | `Data Disk Read Bytes/sec` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `ResourceId` = `{VMID}` *(runtime-substituted from template parameter)* |
| **Split By** | `ResourceId` *(LUN dimension aggregated — `isOutput=false`)* |

---

## Tile 15 — Network Flow Inbound (Max)

| Field | Value |
|-------|-------|
| **Type** | MDM chart |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Region}` parameter (e.g. `AzComputeShoeboxWUS2`) |
| **MDM Namespace** | `Shoebox` |
| **Metric(s)** | `Inbound Flows` |
| **Sampling Type** | Max |
| **Dimension Filter** | `ResourceId` = `{VMID}` *(runtime-substituted from template parameter)* |
| **Split By** | `ResourceId` |

---

## Tile 16 — Total VM Data Disk Read IOPS

| Field | Value |
|-------|-------|
| **Type** | MDM chart |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Region}` parameter (e.g. `AzComputeShoeboxWUS2`) |
| **MDM Namespace** | `Shoebox` |
| **Metric(s)** | `Data Disk Read Operations/Sec` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `ResourceId` = `{VMID}` *(runtime-substituted from template parameter)* |
| **Split By** | `ResourceId` *(LUN dimension aggregated — `isOutput=false`)* |

---

## Tile 17 — Network Flow Outbound (Max)

| Field | Value |
|-------|-------|
| **Type** | MDM chart |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Region}` parameter (e.g. `AzComputeShoeboxWUS2`) |
| **MDM Namespace** | `Shoebox` |
| **Metric(s)** | `Outbound Flows` |
| **Sampling Type** | Max |
| **Dimension Filter** | `ResourceId` = `{VMID}` *(runtime-substituted from template parameter)* |
| **Split By** | `ResourceId` |

---

## Tile 18 — Total VM Data Disk Write Bytes/sec

| Field | Value |
|-------|-------|
| **Type** | MDM chart |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Region}` parameter (e.g. `AzComputeShoeboxWUS2`) |
| **MDM Namespace** | `Shoebox` |
| **Metric(s)** | `Data Disk Write Bytes/sec` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `ResourceId` = `{VMID}` *(runtime-substituted from template parameter)* |
| **Split By** | `ResourceId` *(LUN dimension aggregated — `isOutput=false`)* |

---

## Tile 19 — Data and OS Disk Bandwidth Consumed Percentage per Lun (Average)

| Field | Value |
|-------|-------|
| **Type** | MDM chart |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Region}` parameter (e.g. `AzComputeShoeboxWUS2`) |
| **MDM Namespace** | `Shoebox` |
| **Metric(s)** | `Data Disk Bandwidth Consumed Percentage` (Max), `OS Disk Bandwidth Consumed Percentage` (Average), `Data Disk Used Burst BPS Credits Percentage` (Max), `OS Disk Used Burst BPS Credits Percentage` (Max) |
| **Sampling Type** | Mixed — see individual metrics above |
| **Dimension Filter** | `ResourceId` = `{VMID}` *(runtime-substituted from template parameter)* |
| **Split By** | `LUN` *(Data Disk metrics only)*, `ResourceId` |

---

## Tile 20 — Total VM Data Disk Write IOPS

| Field | Value |
|-------|-------|
| **Type** | MDM chart |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Region}` parameter (e.g. `AzComputeShoeboxWUS2`) |
| **MDM Namespace** | `Shoebox` |
| **Metric(s)** | `Data Disk Write Operations/Sec` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `ResourceId` = `{VMID}` *(runtime-substituted from template parameter)* |
| **Split By** | `ResourceId` *(LUN dimension aggregated — `isOutput=false`)* |

---

## Tile 21 — Data and OS Disk IOPS Consumed Percentage per Lun (Average)

| Field | Value |
|-------|-------|
| **Type** | MDM chart |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Region}` parameter (e.g. `AzComputeShoeboxWUS2`) |
| **MDM Namespace** | `Shoebox` |
| **Metric(s)** | `Data Disk IOPS Consumed Percentage` (Max), `OS Disk IOPS Consumed Percentage` (Average), `Data Disk Used Burst IO Credits Percentage` (Max), `OS Disk Used Burst IO Credits Percentage` (Max) |
| **Sampling Type** | Mixed — see individual metrics above |
| **Dimension Filter** | `ResourceId` = `{VMID}` *(runtime-substituted from template parameter)* |
| **Split By** | `LUN` *(Data Disk metrics only)*, `ResourceId` |

---

## Tile 22 — VM Overall Disk Bandwidth Consumed Percentage (Average)

| Field | Value |
|-------|-------|
| **Type** | MDM chart |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Region}` parameter (e.g. `AzComputeShoeboxWUS2`) |
| **MDM Namespace** | `Shoebox` |
| **Metric(s)** | `VM Cached Bandwidth Consumed Percentage`, `VM Uncached Bandwidth Consumed Percentage` |
| **Sampling Type** | Average |
| **Dimension Filter** | `ResourceId` = `{VMID}` *(runtime-substituted from template parameter)* |
| **Split By** | `ResourceId` |

---

## Tile 23 — VM Overall Disk IOPS Consumed Percentage (Average)

| Field | Value |
|-------|-------|
| **Type** | MDM chart |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Region}` parameter (e.g. `AzComputeShoeboxWUS2`) |
| **MDM Namespace** | `Shoebox` |
| **Metric(s)** | `VM Cached IOPS Consumed Percentage`, `VM Uncached IOPS Consumed Percentage` |
| **Sampling Type** | Average |
| **Dimension Filter** | `ResourceId` = `{VMID}` *(runtime-substituted from template parameter)* |
| **Split By** | `ResourceId` |

---

## Tile 24 — Ram Size and Available RAM [CONFIDENTIAL]

### Kusto Source

| Field | Value |
|-------|-------|
| **Data Source** | Kusto — provides RAM capacity (physical memory bytes) from host-level counters |
| **Cluster** | `https://azcore.centralus.kusto.windows.net` |
| **Database** | `Fa` |
| **Table(s)** | `VmHealthRawStateEtwTable`, `VmCounterFiveMinuteRoleInstanceCentralBondTable` |

**Key KQL logic:**
```kql
// {ResourceId} = VM unique ID(s); {startTime}, {endTime} = dashboard time range; {account} = MDM account name
let vmid = split("{ResourceId}", ",");
let starttime = datetime({startTime});
let endtime = datetime({endTime});
let containerids = VmHealthRawStateEtwTable
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where VirtualMachineUniqueId in (vmid)
| summarize by ContainerId, VirtualMachineUniqueId;
let vmtable = containerids;
VmCounterFiveMinuteRoleInstanceCentralBondTable
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where VmId in(containerids)
| where CounterName contains "physical memory"
| extend CounterName = "Physical Memory Bytes"
| summarize by bin(TIMESTAMP, 1m), RamSize=MaxCounterValue*1024*1024, RoleInstanceId, containerid
| join kind=inner vmtable on $left.containerid == $right.ContainerId
| project TIMESTAMP, RamSize, RoleInstanceId=strcat(RoleInstanceId, '-', VirtualMachineUniqueId)
```

### MDM Source

| Field | Value |
|-------|-------|
| **Data Source** | MDM — provides available memory bytes (live measured) |
| **MDM Account** | Dynamic — from `{Region}` parameter (e.g. `AzComputeShoeboxWUS2`) |
| **MDM Namespace** | `Shoebox` |
| **Metric(s)** | `Available Memory Bytes` |
| **Sampling Type** | Average |
| **Dimension Filter** | `ResourceId` = `{VMID}` *(runtime-substituted from template parameter)* |
| **Split By** | `ResourceId` |

---

## Tile 25 — Disk IO Outliers [CONFIDENTIAL]

| Field | Value |
|-------|-------|
| **Type** | Kusto grid |
| **Data Source** | Kusto |
| **Cluster** | `https://azurecm.kusto.windows.net` |
| **Database** | `AzureCM` |
| **Table(s)** | `LogContainerSnapshot` (primary); cross-cluster: `azcore.centralus.kusto.windows.net/Fa` → `OsXIOSurfaceCounterTable`, `HyperVStorageStackTable` |

**Key KQL logic:**
```kql
// {ResourceId} = VM unique ID(s); {startTime}, {endTime} = dashboard time range
let vmids = split("{ResourceId}", ",");
let starttime = datetime({startTime});
let endtime = datetime({endTime});
let allvms = LogContainerSnapshot  // azurecm/AzureCM
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where virtualMachineUniqueId in (vmids)
| summarize arg_max(PreciseTimeStamp, *) by containerId
| project roleInstanceName, virtualMachineUniqueId, VMType, Tenant=tolower(Tenant), nodeId, containerId;
let nodeids = toscalar(allvms | summarize make_set(nodeId));
let containerids = toscalar(allvms | summarize make_set(containerId));
// Surface counter: throttled wait time > 10 seconds
let surfaceTable = cluster('azcore.centralus.kusto.windows.net').database('Fa').OsXIOSurfaceCounterTable
| where PreciseTimeStamp > starttime and PreciseTimeStamp < endtime
| where AvgThrottledWaitTimeInSec > 10
| where SurfaceName has_any (containerids);
// HyperV storage stack events: EventId 9 (IO completion anomalies)
let HVStorageStackTable = cluster('azcore.centralus.kusto.windows.net').database('Fa').HyperVStorageStackTable
| where PreciseTimeStamp > starttime and PreciseTimeStamp < endtime
| where NodeId in~ (nodeids)
| where EventId in (9)
| where Message has_any (containerids);
union surfaceTable, HVStorageStackTable
| join kind=inner allvms on $left.containerId == $right.containerId
| project EvtSource, TIMESTAMP, roleInstanceName, AvgThrottledWaitTimeInSec, IOPS, MBPS,
          DeltaThrottled, DeltaThrottleTimeInSec, SCSICommand, DataLength, Status, DurationMs,
          VMType, NodeId, containerId, SurfaceName, IsXIOdisk, CachePolicy, ArmId, BlobPath
| order by TIMESTAMP asc
```

---

## Summary Table

| # | Tile Title | Source | Metrics / Tables | Confidential |
|---|-----------|--------|-----------------|:------------:|
| 1 | % CPU (Average) | MDM `Shoebox` | `Percentage CPU` (Avg) | |
| 2 | Data/OS/Temp Disk Queue Length | MDM `Shoebox` | `Data/OS/Temp Disk Queue Depth` (Max) | |
| 3 | Network In Bytes Per Minute | MDM `Shoebox` | `Network In Total` (Max) | |
| 4 | Network Out Bytes Per Minute | MDM `Shoebox` | `Network Out Total` (Max) | |
| 5 | Data/OS/Temp Disk Read Bytes/sec Per Lun | MDM `Shoebox` | `Data/OS/Temp Disk Read Bytes/sec`, Burst/Target metrics (Max) | |
| 6 | Data/OS/Temp Disk Write Bytes/sec | MDM `Shoebox` | `Data/OS/Temp Disk Write Bytes/sec` (Max) | |
| 7 | VM Performance Dashboard (Header) | HTML | Instructions, permissions table, TSG links | |
| 8 | Data/OS/Temp Disk Latency | MDM `Shoebox` | `Data/OS/Temp Disk Latency` (Max) | |
| 9 | % Memory Pressure (Max) | Kusto `azcore/Fa` | `VmHealthRawStateEtwTable`, `VmCounterFiveMinuteRoleInstanceCentralBondTable` | ✅ |
| 10 | Data/OS/Temp Disk Read IOPS per Lun | MDM `Shoebox` | `Data/OS/Temp Disk Read Operations/Sec`, Burst/Target IOPS (Max) | |
| 11 | Data/OS/Temp Disk Write IOPS per Lun | MDM `Shoebox` | `Data/OS/Temp Disk Write Operations/Sec` (Max) | |
| 12 | VM History, HostAnalyzer, NetVMA, Physical Info | Kusto `azurecm/AzureCM` | `LogContainerSnapshot` + cross-cluster `LogNodeSnapshot`, `CADDAILY`, `MdmVfpVnetAccountMaps` | ✅ |
| 13 | CPU Credits Remaining (Min) | MDM `Shoebox` | `CPU Credits Remaining` (Min) | |
| 14 | Total VM Data Disk Read Bytes/sec | MDM `Shoebox` | `Data Disk Read Bytes/sec` (Sum, all LUNs) | |
| 15 | Network Flow Inbound (Max) | MDM `Shoebox` | `Inbound Flows` (Max) | |
| 16 | Total VM Data Disk Read IOPS | MDM `Shoebox` | `Data Disk Read Operations/Sec` (Sum, all LUNs) | |
| 17 | Network Flow Outbound (Max) | MDM `Shoebox` | `Outbound Flows` (Max) | |
| 18 | Total VM Data Disk Write Bytes/sec | MDM `Shoebox` | `Data Disk Write Bytes/sec` (Sum, all LUNs) | |
| 19 | Data and OS Disk Bandwidth % per Lun | MDM `Shoebox` | `Data/OS Disk Bandwidth Consumed %`, Burst BPS Credits % (Max/Avg) | |
| 20 | Total VM Data Disk Write IOPS | MDM `Shoebox` | `Data Disk Write Operations/Sec` (Sum, all LUNs) | |
| 21 | Data and OS Disk IOPS % per Lun | MDM `Shoebox` | `Data/OS Disk IOPS Consumed %`, Burst IO Credits % (Max/Avg) | |
| 22 | VM Overall Disk Bandwidth % | MDM `Shoebox` | `VM Cached/Uncached Bandwidth Consumed %` (Avg) | |
| 23 | VM Overall Disk IOPS % | MDM `Shoebox` | `VM Cached/Uncached IOPS Consumed %` (Avg) | |
| 24 | Ram Size and Available RAM | Mixed: Kusto `azcore/Fa` + MDM `Shoebox` | `VmCounterFiveMinuteRoleInstanceCentralBondTable`, `Available Memory Bytes` | ✅ |
| 25 | Disk IO Outliers | Kusto `azurecm/AzureCM` + `azcore/Fa` | `LogContainerSnapshot`, `OsXIOSurfaceCounterTable`, `HyperVStorageStackTable` | ✅ |
