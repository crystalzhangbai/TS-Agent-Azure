# (top-level)

> Source: **Aztec Virtual Machines Investigation Guide** dashboard, chapter **(top-level)** (6 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Virtual Machines"

Cluster: `azurecm` · Database: `AzureCM` · Type: `ResourceGet` · Widget: `Container`

```kusto
LogContainerSnapshot
| where PreciseTimeStamp between(global_startTime..global_endTime)
| where virtualMachineUniqueId == local_virtualMachineUniqueId
| top 1 by PreciseTimeStamp desc
```

**Params:** `{local_virtualMachineUniqueId}`

---

### MDM Shoebox Region

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Single` · Widget: `Container`

```kusto
let region_names = cluster('AzureCM.kusto.windows.net').database('AzureCM').LogContainerSnapshot
| where Region == queryVmRegion or RegionFriendlyName == queryVmRegion
| take 1
| project RPTenant = RegionFriendlyName, Region
| join kind=leftouter (
    cluster("aznwnetmon").database('aznwmds').RegionNamesMap
    | distinct RegionCode, RegionName
    | project RegionCode, Region = RegionName
) on Region
| project RPTenant, Region, RegionCode;
let rp_tenant = region_names | take 1 | project RPTenant;
region_names
| join kind=leftouter (
    cluster('AzureCM.kusto.windows.net').database('AzureCM').LogClusterSnapshot
    | where RegionFriendlyName in (rp_tenant)
    | take 1
    | project RPTenant = RegionFriendlyName, shoeboxMdmAccountName
) on RPTenant
| project-away RPTenant1
```

**Params:** `{queryVmRegion}`

---

### VM Containers

_Widget purpose:_ VM Timeline

Cluster: `azcore.centralus` · Database: `AzureCP` · Type: `Timeline`

```kusto
cluster('azcore.centralus').database('AzureCP').MycroftContainerSnapshot
| where PreciseTimeStamp between(qFrom .. qTo) and VirtualMachineUniqueId == qVmId
| project PreciseTimeStamp, NodeId, ContainerId, VirtualMachineUniqueId, RoleInstanceName, CreationTime
| extend StartTime = PreciseTimeStamp
| order by CreationTime asc, StartTime asc 
| where (ContainerId != next(ContainerId) or ContainerId != prev(ContainerId)) 
| extend EndTime = next(StartTime)
| where ContainerId != prev(ContainerId)
| extend Content = ContainerId
| extend Tooltip = strcat("NodeId: ", NodeId, "<br/>ContainerId: ", ContainerId)
| extend EndTime = iif(isnull(EndTime), datetime_add('minute', 5, StartTime), EndTime)
| extend GroupBy = strcat("Container: ", substring(ContainerId, 0, 8))
| project StartTime, EndTime, Content, Tooltip, GroupBy
```

**Params:** `{qVmId}`, `{qFrom}`, `{qTo}`

---

### Container VMA

_Widget purpose:_ VM Timeline

Cluster: `azcore.centralus` · Database: `AzureCP` · Type: `Timeline`

```kusto
let cloudEnv = "public";
let containers = cluster('azcore.centralus').database('AzureCP').MycroftContainerSnapshot
| where PreciseTimeStamp between ((qFrom - 2h) .. (qTo + 2h)) and VirtualMachineUniqueId == qVM
| distinct ContainerId
;
cluster("vmainsight").database("vmadb").VMA
| where PreciseTimeStamp between (qFrom .. qTo) 
| where VmUniqueId == qVM or ContainerId in (containers)
| extend Health = "Unhealthy"
| extend Content = case(isnotempty(RCA_CSS), RCA_CSS, RCA)
| extend ToolTip = NODESERVICE_RCA
| extend ActualEndTime = EndTime
| project StartTime, ActualEndTime, Content, Health, E17_ClusterFailureReportUrl, TM_RCA, DowntimeReasonHint, ContainerId, NodeId, VMADrilldown, Class, SubClass, RCA, RCA_CSS, DevRCA_EscalateTo, NodeStats_RCALevel1History, Detail
```

**Params:** `{qFrom}`, `{qTo}`, `{qVM}`

---

### Air VMA

_Widget purpose:_ VM Timeline

Cluster: `vmainsight` · Database: `Air` · Type: `Timeline`

```kusto
GetVMAvailabilityImpactEvents(queryVmId, global_startTime, global_endTime)
| extend Content = strcat(
    EventType,
    " - ",
    EventSource
)
| extend Tooltip = 
strcat(
    "Event Type: ", 
    EventType,
    "<br/>EventSource: ",
    EventSource,
    "<br/>Impact Category: ",
    ImpactCategory,
    "<br/>Article Id: ",
    ArticleId,    
    "<br/>InternalArticleId: ",
    InternalArticleId
)
| project StartTime = ImpactBeginTimeStamp, Content, Tooltip
```

**Params:** `{queryVmId}`

---

### VM Hosts

_Widget purpose:_ VM Timeline

Cluster: `azcore.centralus` · Database: `AzureCP` · Type: `Timeline`

```kusto
cluster('azcore.centralus').database('AzureCP').MycroftContainerSnapshot
| where PreciseTimeStamp between(qFrom .. qTo) and VirtualMachineUniqueId == qVmId
| project PreciseTimeStamp, NodeId, ContainerId, VirtualMachineUniqueId, RoleInstanceName, CreationTime
| extend StartTime = PreciseTimeStamp
| order by CreationTime asc, StartTime asc 
| where (NodeId != next(NodeId) or NodeId != prev(NodeId)) 
| extend EndTime = next(StartTime)
| where NodeId != prev(NodeId)
| extend Content = NodeId
| extend Tooltip = strcat("NodeId: ", NodeId, "<br/>ContainerId: ", ContainerId)
| extend EndTime = iif(isnull(EndTime), datetime_add('minute', 5, StartTime), EndTime)
| extend GroupBy = strcat("Host: ", substring(NodeId, 0, 8))
| project StartTime, EndTime, Content, Tooltip, GroupBy
```

**Params:** `{qFrom}`, `{qTo}`, `{qVmId}`

---
