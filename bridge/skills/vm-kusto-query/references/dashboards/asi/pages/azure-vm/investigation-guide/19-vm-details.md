# VM Details

> Source: **Azure Host - Azure VM** dashboard, chapter **VM Details** (14 queries across 4 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Azure Host VM VMA Query

Cluster: `vmainsight.kusto.windows.net` · Database: `vmadb` · Type: `Timeline`
Source panel: `VM Details`

**Tables:** `LogContainerSnapshot`, `VMA`
**Output columns:** `StartTime`, `ActualEndTime`, `Content`, `Health`, `E17_ClusterFailureReportUrl`, `TM_RCA`, `DowntimeReasonHint`, `Detail`

```kusto
let VmId = toscalar(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp between ((startTime - 2h) .. (endTime + 2h)) and containerId == containerIdStr
| distinct virtualMachineUniqueId);
VMA
| where PreciseTimeStamp between (startTime .. endTime) 
| where ContainerId == containerIdStr or VmUniqueId == VmId
| extend Health = "Unhealthy"
| extend Content = case(isnotempty(RCA_CSS), RCA_CSS, RCA)
| extend ToolTip = NODESERVICE_RCA
| extend ActualEndTime = EndTime
| project StartTime, ActualEndTime, Content, Health, E17_ClusterFailureReportUrl, TM_RCA, DowntimeReasonHint, Detail
```

**Params:** `{startTime}`, `{endTime}`, `{containerIdStr}`, `{cloudEnv}`

---

### Azure Host VM Health Timeline

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `VM Details`

**Tables:** `VmHealthRawStateEtwTable`
**Output columns:** `Context`

```kusto
VmHealthRawStateEtwTable
| where PreciseTimeStamp between (startTime .. endTime) 
| where ContainerId == containerId
| project StartTime = PreciseTimeStamp, Content = VmHyperVIcHeartbeat, Context
| extend Health = case(Content == "HeartBeatStateOk", "Healthy", "Degraded")
| sort by StartTime asc
| serialize
| extend EndTime = case(isnotempty(next(StartTime)), next(StartTime), now())
| extend StartTime = case(isnotempty(prev(StartTime)), prev(EndTime), startTime - 1h),
         FilterOut = Content == next(Content) and Content == prev(Content)
| where FilterOut != 1
| extend EndTime = case(isnotempty(next(StartTime)), next(StartTime), now())
| extend StartTime = case(isnotempty(prev(StartTime)), prev(EndTime), startTime - 1h)
| extend Tooltip = Context
| project-away Context
```

**Params:** `{containerId}`, `{startTime}`, `{endTime}`

---

### Azure Host VM Impactful Events

Cluster: `vmainsight.kusto.windows.net` · Database: `Air` · Type: `Timeline`
Source panel: `VM Details`

**Tables:** `OSHPExecutionInstances`, `AirManagedEvents`

```kusto
AirManagedEvents
| where EventTime between ((startTime - 12h) .. (endTime + 12h))
| where ObjectType =~ "Container" and ObjectId == containerId
| extend UpdateType = split(EventSource, '_')[-1], Reference = iff(EventSource contains "VmPhu", "https://www.osgwiki.com/wiki/VM-PHU_Compute_Blackout", "")
| project StartTime = EventTime, //EndTime = EventTime + Duration, 
    Content = strcat(tostring(UpdateType), " (", Duration, ") "), Health = 'Unhealthy', 
    Tooltip = strcat(EventSource, " duration ", Duration), Diagnostics, Reference
//
//AirManagedEvents
//| where EventTime between ((startTime - 12h) .. (endTime + 12h))
//| where ObjectType =~ "Container" and ObjectId == containerId
//| extend UpdateType = split(EventSource, '_')[-1]
//| project StartTime = EventTime, EndTime = EventTime + Duration, UpdateType, Duration,
//    Content = strcat(tostring(UpdateType), " (", Duration, ") "), Health = 'Unhealthy', 
//    Tooltip = strcat(EventSource, " duration ", Duration), Diagnostics, NodeId
//| join kind = leftouter (
//    cluster("baseplatform.westus").database("vmphu").OSHPExecutionInstances
//    | where StartTime between (startTime .. endTime)
//    | extend OSHPStartTime = StartTime
//    //| where UpdateType == 'ksr_to_self'
//    //| extend ExecutionDetail = strcat('https://klondike.azurewebsites.net/scenario/vmphu/instance?InstanceId=', ExecutionId, " | Klondike Overview: aka.ms/FUNKlondike (how to access klondike: https://coreidentity.microsoft.com/manage/Entitlement/entitlement/funklondike-hfni)")
//    | extend KlondikeExecutionDetail = strcat('https://klondike.azurewebsites.net/scenario/vmphu/instance?InstanceId=', ExecutionId)
//    | project OSHPStartTime, UpdateType, NodeId, ExecutionId, KlondikeExecutionDetail
//) on NodeId
//| where OSHPStartTime < StartTime
//| project StartTime, //, EndTime
//          UpdateType = iff(isnotempty(UpdateType1), UpdateType1, UpdateType), 
//          Content, Duration, Tooltip, Health, Diagnostics, 
//          ExecutionDetail = iff(Content contains "VmPhu", KlondikeExecutionDetail, ""), 
//          Reference = iff(Content contains "VmPhu", "https://www.osgwiki.com/wiki/VM-PHU_Compute_Blackout", "")
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`

**Signal filters seen in KQL:** `ObjectType =~ "Container"` · `UpdateType == "ksr_to_self"`

---

### Azure Host VM CRP Actions

Cluster: `Azcrp` · Database: `crp_allprod` · Type: `Timeline`
Source panel: `VM Details`

**Tables:** `VMApiQosEvent`, `ApiQosEvent_nonGet`
**Aggregations:** `summarize arg_max(PreciseTimeStamp, resourceGroupName, resourceName, operationName) by correlationId, operationId, subscriptionId`

```kusto
//VMApiQosEvent
//| where PreciseTimeStamp between (startTime .. endTime) and vMId == vmId
//| extend StartTime = datetime_add("Millisecond", -durationInMilliseconds, PreciseTimeStamp) 
//| project StartTime, Content = strcat(resourceName, " | ", operationName), 
//        Health = iff(isnotempty(errorDetails) or isnotempty(exceptionType), "Unhealthy", "Neutral"), 
//        correlationId, operationId, resultCode, errorDetails
let vmOperations = VMApiQosEvent
| where PreciseTimeStamp between (startTime .. endTime) and vMId == vmId
| summarize arg_max(PreciseTimeStamp, resourceGroupName, resourceName, operationName) by correlationId, operationId, subscriptionId; //vmOperations
ApiQosEvent_nonGet
| where PreciseTimeStamp between (startTime .. endTime) 
and subscriptionId in ((vmOperations | distinct subscriptionId))
and resourceGroupName in ((vmOperations | distinct resourceGroupName))
and correlationId in ((vmOperations | distinct correlationId))
and operationName !startswith "AsyncOperation"
| extend StartTime = datetime_add("Millisecond", -durationInMilliseconds, PreciseTimeStamp) 
| project StartTime, Content = strcat(resourceName, " | ", operationName), 
        Health = iff(isnotempty(errorDetails) or isnotempty(exceptionType), "Unhealthy", "Neutral"), 
        correlationId, operationId, httpStatusCode, resultCode, errorDetails, requestEntity, userAgent
```

**Params:** `{startTime}`, `{endTime}`, `{vmId}`

---

### Azure Host VM DiskRP Actions

Cluster: `disks.kusto.windows.net` · Database: `Disks` · Type: `Timeline`
Source panel: `VM Details`

**Tables:** `OsXIOHealthSignalEvent`, `OsUltraSSDHealthSignalEvent`, `DiskManagerApiQoSEvent`

```kusto
let xioDisks = cluster('storageclient.eastus.kusto.windows.net').database('Fa').OsXIOHealthSignalEvent
| where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and SurfaceName contains containerId
| distinct ArmId;
let ddDisks = cluster('storageclient.eastus.kusto.windows.net').database('Fa').OsUltraSSDHealthSignalEvent
| where PreciseTimeStamp between (startTime..endTime) and NodeId == nodeId and ContainerId == containerId 
| distinct ArmId;
let diskDetails = union xioDisks, ddDisks
| where isnotempty(ArmId)
| parse ArmId with * "subscriptions/" subscriptionId "/resourceGroups/" resourceGroup "/" * "/disks/" diskName
| where isnotempty(subscriptionId) and isnotempty(resourceGroup) and isnotempty(diskName)
| project subscriptionId, resourceGroup, diskName, ArmId;
cluster('disks.kusto.windows.net').database('Disks').DiskManagerApiQoSEvent
| where PreciseTimeStamp between (startTime..endTime)
and subscriptionId in~ ((diskDetails | distinct subscriptionId)) and resourceGroupName in~ ((diskDetails | distinct resourceGroup)) and resourceName in~ ((diskDetails | distinct diskName))
| where operationName !endswith "GET"
| extend StartTime = datetime_add("Millisecond", -e2EDurationInMilliseconds, PreciseTimeStamp), EndTime = PreciseTimeStamp
| project StartTime, //EndTime, 
    Content = strcat(resourceName, " | ", operationName), Duration = EndTime - StartTime,
    Tooltip = strcat(resourceName, " | ", operationName, " | ", resultCode, " | Duration: ", EndTime - StartTime), 
    Health = iff(isnotempty(resultCode) or isnotempty(errorDetails) or isnotempty(exceptionType), "Unhealthy", "Neutral"), requestEntity
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

### Kyber Annotation Timeline

Cluster: `azcore.centralus.kusto.windows.net` · Database: `AzureCP` · Type: `Timeline`
Source panel: `VM Details`

**Tables:** `KyberAnnotationEvent`
**Output columns:** `StartTime`, `Content`, `Health`, `AnnotationMetadata`, `ResourceIdentityMetadata`, `SourceServiceName`

```kusto
KyberAnnotationEvent
| where PreciseTimeStamp between(queryFrom..queryTo)
| where ResourceId == containerId
| project OccurredTime, AnnotationName, AnnotationMetadata, ResourceIdentityMetadata, SourceServiceName
| extend FilterOut = 0
| extend Content = AnnotationName
| extend Health = "Unhealthy"
| project StartTime = OccurredTime, Content, Health,  AnnotationMetadata, ResourceIdentityMetadata, SourceServiceName
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`

---

### Azure Container Reuse Rejection

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Timeline`
Source panel: `VM Details`

**Tables:** `AllocatorContainerReuseRejectionReason`
**Output columns:** `StartTime`, `Health`, `Content`, `allocationId`, `rejectedContainerId`, `ruleName`, `reason`

```kusto
AllocatorContainerReuseRejectionReason
| where PreciseTimeStamp between (startTime .. endTime)
| where rejectedContainerId == containerId 
| extend Health = 'Unhealthy'
| extend Content = 'Existing container rejected by Allocator. A new container / node may be allocated for the VM'
| project StartTime = PreciseTimeStamp, Health, Content, allocationId, rejectedContainerId, ruleName, reason
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`

---

### Service Healing Trigger

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Timeline`
Source panel: `VM Details`

**Tables:** `ServiceHealingTenantStatusEtwTable`
**Output columns:** `StartTime`, `TenantName`, `Content`

```kusto
ServiceHealingTenantStatusEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where TenantName == tenant 
| project StartTime = PreciseTimeStamp, TenantName, Content=Message
```

**Params:** `{queryFrom}`, `{tenant}`, `{queryTo}`

---

### Service Healing Tenant Status

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Timeline`
Source panel: `VM Details`

**Tables:** `ServiceHealingTenantStatusEtwTable`
**Output columns:** `StartTime`, `Content`, `State`

```kusto
ServiceHealingTenantStatusEtwTable
| where TenantName == tenantName
| project StartTime = PreciseTimeStamp, Content = Message, State
```

**Params:** `{queryFrom}`, `{queryTo}`, `{tenantName}`

---

## {{VMName}} Details

### Azure Host VM ArmId

_Widget purpose:_ {{VMName}} Details

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Single` · Widget: `Card`
Source panel: `VM Details > {{VMName}} Details`

**Tables:** `VmShoeboxCounterTable`

```kusto
VmShoeboxCounterTable
| where PreciseTimeStamp between ((startTime - 1h) .. (endTime + 1h)) and VmId == containerId
| distinct ArmId
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`

---

### Azure Host VM HyperVVmConfigSnapshot

_Widget purpose:_ {{VMName}} Details

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Single` · Widget: `Card`
Source panel: `VM Details > {{VMName}} Details`

**Aggregations:** `summarize arg_max(PreciseTimeStamp, VmProcessorCount, VmVersion, VmGeneration, HclEnabled, by NodeId, ContainerId` · `summarize by NodeId, HclFile = strcat(FileName, " ", FileVersion), HclFileTimeStamp = File`
**Output columns:** `ContainerId1`

```kusto
let AzCoreKusto = entity_group [
           cluster('https://azcore1.southeastasia.kusto.windows.net'),
           cluster('https://azcore2.australiaeast.kusto.windows.net'),
           cluster('https://azcore3.brazilsouth.kusto.windows.net'),
           cluster('https://azcore4.canadacentral.kusto.windows.net'),
           cluster('https://azcore5.northeurope.kusto.windows.net'),
           cluster('https://azcore6.westeurope.kusto.windows.net'),
           cluster('https://azcore7.francecentral.kusto.windows.net'),
           cluster('https://azcore8.japaneast.kusto.windows.net'),
           cluster('https://azcore9.uksouth.kusto.windows.net'),
           cluster('https://azcore10.centralus.kusto.windows.net'),
           cluster('https://azcore11.southcentralus.kusto.windows.net'),
           cluster('https://azcore12.eastus.kusto.windows.net'),
           cluster('https://azcore13.eastus2.kusto.windows.net'),
           cluster('https://azcore14.westus2.kusto.windows.net'),
           cluster('https://azcore15.westus3.kusto.windows.net'),
           cluster('https://azcore16.eastasia.kusto.windows.net'),
           cluster('https://azcore17.centralindia.kusto.windows.net')
        ];
    print ContainerId = containerId
    | join kind=leftouter (
        macro-expand isfuzzy=true AzCoreKusto as data 
        (
            data.database('Fa').HyperVVmConfigSnapshot
            | where PreciseTimeStamp between ((startTime - 1h) .. (endTime + 1h)) and NodeId == nodeId and ContainerId == containerId and SummaryType == "Configuration"
            | summarize arg_max(PreciseTimeStamp, VmProcessorCount, VmVersion, VmGeneration, HclEnabled, IsUnderhill, IsolationSetting, SummaryType, SummaryJson) by NodeId, ContainerId
            | extend IsUnderhill = iff(isnotempty(IsUnderhill), IsUnderhill, parse_json(SummaryJson).Settings.hcl.IsUnderhill)
            | extend Hcl = case(HclEnabled =~ "true" and IsUnderhill =~ "true", "HCLv2 - OpenHCL/Underhill", HclEnabled =~ "true" and isempty(IsUnderhill), "HCLv1", "")
            //| project NodeId, ContainerId, VmProcessorCount, VmVersion, Hcl, IsolationSetting //, SummaryJson
            | join kind = leftouter (
                data.database('Fa').OsFileVersionTable
                | where PreciseTimeStamp between((startTime - 6h)..(endTime + 6h)) and NodeId == nodeId and FileName =~ "vmfirmwarehcl.dll" 
                | summarize by NodeId, HclFile = strcat(FileName, " ", FileVersion), HclFileTimeStamp = FileTimeStamp
            ) on NodeId
        | project ContainerId, VmProcessorCount, VmVersion, Hcl, IsolationSetting, HclFile, HclFileTimeStamp
        )
    ) on ContainerId
    | project-away ContainerId1 
    | project VmProcessorCount = case(isempty(VmProcessorCount), "", VmProcessorCount),
             VmVersion = case(isempty(VmVersion), "", VmVersion),
             Hcl = case(isempty(Hcl), "", Hcl),
             IsolationSetting = case(isempty(IsolationSetting), "", IsolationSetting),
             HclFile = case(isempty(HclFile), "", HclFile),
             HclFileTimeStamp = case(isempty(HclFileTimeStamp), "", HclFileTimeStamp)
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`, `{nodeId}`

---

## Insights for Host Node where VM is running 

### Azure Host Node StorageClient Insights

_Widget purpose:_ Insights for Host Node where VM is running 

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `Table`
Source panel: `VM Details > Insights for Host Node where VM is running `

**Output columns:** `PreciseTimeStamp`, `Message`, `EventName`, `ContainerId`, `level`

```kusto
let tempEndTime = iff(datetime_diff('day', startTime, endTime) > 1, startTime + 1d, endTime);
StorageClientInsightsForNodeV2(nodeId, startTime, tempEndTime)
//| where ContainerId != containerId or isempty(containerId) // this is already added above in the vm insights
| project PreciseTimeStamp, Message, EventName, ContainerId, level = case(EventName contains "Update" or EventName contains "CacheHint", "warning", "error")
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`, `{containerId}`

---

## Insights for the VM (for the time selected)

### Azure Host VM StorageClient Insights

_Widget purpose:_ Insights for the VM (for the time selected)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `Table`
Source panel: `VM Details > Insights for the VM (for the time selected)`

**Output columns:** `PreciseTimeStamp`, `Message`, `EventName`, `level`

```kusto
let tempEndTime = iff(datetime_diff('day', startTime, endTime) > 1, startTime + 1d, endTime);
StorageClientInsightsForContainer(containerId, nodeId, startTime, tempEndTime)
| union (
    StorageClientInsightsForNodeAndContainer(nodeId, containerId, startTime, tempEndTime)
)
| project PreciseTimeStamp, Message, EventName, level = case(isnotempty(level), level, EventName contains "Update" or EventName contains "CacheHint", "warning", "error")
| where level != "info"
```

**Params:** `{containerId}`, `{startTime}`, `{endTime}`, `{nodeId}`

**Signal filters seen in KQL:** `level != "info"`

---

### Azure Host VM Insights 3

_Widget purpose:_ Insights for the VM (for the time selected)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `Table`
Source panel: `VM Details > Insights for the VM (for the time selected)`

**Output columns:** `PreciseTimeStamp`, `Message`, `EventName`, `level`

```kusto
StorageClientInsightsForContainer2(containerId, nodeId, startTime, endTime)
| project PreciseTimeStamp, Message, EventName, level = case(EventName contains "Update", "warning", "error")
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`, `{containerId}`

---
