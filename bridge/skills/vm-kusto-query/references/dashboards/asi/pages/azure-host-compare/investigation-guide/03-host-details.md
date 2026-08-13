# Host Details

> Source: **Azure Host Compare Investigation Guide** dashboard, chapter **Host Details** (8 queries across 4 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Node1 Details

### Retrieve Resource "Azure Host Node"

_Widget purpose:_ Node1 Details

Cluster: `azurecm.kusto.windows.net` · Database: `AzureCM` · Type: `ResourceGet` · Widget: `Card`
Source panel: `Host Details > Node1 Details`

```kusto
LogNodeSnapshot
| where PreciseTimeStamp between ((globalFrom - 1h) .. (globalTo + 1h)) and nodeId == local_nodeId
| summarize arg_max(PreciseTimeStamp, Region, Tenant, DataCenterName, nodeId, ipAddress, containerCount, diskConfiguration, machinePoolName, tipNodeSessionId) by hostingEnvironment
| extend hostingEnvironment = parse_json(hostingEnvironment)
| extend HostOsVhd = tostring(hostingEnvironment.OSBaseImageName), AgentPackage = tostring(hostingEnvironment.AgentPackageName), ipAddress
| distinct Region, Tenant, DataCenterName, nodeId, ipAddress, containerCount, HostOsVhd, AgentPackage, diskConfiguration, machinePoolName, tipNodeSessionId
| extend globalFrom = globalFrom
```

**Params:** `{local_nodeId}`, `{globalFrom}`, `{globalTo}`

---

### Retrieve Node Hardware Details

_Widget purpose:_ Node1 Details

Cluster: `azuredcm.kusto.windows.net` · Database: `AzureDCMDb` · Type: `Single` · Widget: `Card`
Source panel: `Host Details > Node1 Details`

```kusto
cluster("azuredcm.kusto.windows.net").database("AzureDCMDb").RdmResourceSnapshot
| where ResourceId == local_nodeId and PreciseTimeStamp > ago(1d)
| summarize arg_max(PreciseTimeStamp, Sku, Manufacturer, Model, ResourceId) by ResourceId
| project Sku, Manufacturer, Model, ResourceId
| join kind=leftouter(
    cluster("azuredcm.kusto.windows.net").database("AzureDCMDb").dcmInventoryComponentSystemDirect 
    | where NodeId == local_nodeId
    | extend Total_RootVP = case(HyperVCore_MinRoot == 0, HyperVCore_PhysicalCoreCount, HyperVCore_MinRoot) 
    | project NodeId, PhysicalCoreCount = HyperVCore_PhysicalCoreCount, Total_LP = HyperVCore_LogicalCoreCount, Total_RootVP, Hostname | take 1
) on $left.ResourceId == $right.NodeId
| project-away ResourceId, NodeId
//| extend globalFrom = globalFrom
```

**Params:** `{queryFrom}`, `{queryTo}`, `{local_nodeId}`

---

### Host OS Version

_Widget purpose:_ Node1 Details

Cluster: `wdgeventstore.kusto.windows.net` · Database: `HostOSDeploy` · Type: `Single` · Widget: `Card`
Source panel: `Host Details > Node1 Details`

```kusto
cluster('wdgeventstore.kusto.windows.net').database('HostOSDeploy').nodes
| where nodeId == local_nodeId
| distinct nodeId, HostOS = OSVersion | take 1 | project HostOS
```

**Params:** `{queryFrom}`, `{queryTo}`, `{local_nodeId}`

---

## Node2 Details

### Retrieve Resource "Azure Host Node"

_Widget purpose:_ Node2 Details

Cluster: `azurecm.kusto.windows.net` · Database: `AzureCM` · Type: `ResourceGet` · Widget: `Card`
Source panel: `Host Details > Node2 Details`

```kusto
LogNodeSnapshot
| where PreciseTimeStamp between ((globalFrom - 1h) .. (globalTo + 1h)) and nodeId == local_nodeId
| summarize arg_max(PreciseTimeStamp, Region, Tenant, DataCenterName, nodeId, ipAddress, containerCount, diskConfiguration, machinePoolName, tipNodeSessionId) by hostingEnvironment
| extend hostingEnvironment = parse_json(hostingEnvironment)
| extend HostOsVhd = tostring(hostingEnvironment.OSBaseImageName), AgentPackage = tostring(hostingEnvironment.AgentPackageName), ipAddress
| distinct Region, Tenant, DataCenterName, nodeId, ipAddress, containerCount, HostOsVhd, AgentPackage, diskConfiguration, machinePoolName, tipNodeSessionId
| extend globalFrom = globalFrom
```

**Params:** `{local_nodeId}`, `{globalFrom}`, `{globalTo}`

---

### Retrieve Node Hardware Details

_Widget purpose:_ Node2 Details

Cluster: `azuredcm.kusto.windows.net` · Database: `AzureDCMDb` · Type: `Single` · Widget: `Card`
Source panel: `Host Details > Node2 Details`

```kusto
cluster("azuredcm.kusto.windows.net").database("AzureDCMDb").RdmResourceSnapshot
| where ResourceId == local_nodeId and PreciseTimeStamp > ago(1d)
| summarize arg_max(PreciseTimeStamp, Sku, Manufacturer, Model, ResourceId) by ResourceId
| project Sku, Manufacturer, Model, ResourceId
| join kind=leftouter(
    cluster("azuredcm.kusto.windows.net").database("AzureDCMDb").dcmInventoryComponentSystemDirect 
    | where NodeId == local_nodeId
    | extend Total_RootVP = case(HyperVCore_MinRoot == 0, HyperVCore_PhysicalCoreCount, HyperVCore_MinRoot) 
    | project NodeId, PhysicalCoreCount = HyperVCore_PhysicalCoreCount, Total_LP = HyperVCore_LogicalCoreCount, Total_RootVP, Hostname | take 1
) on $left.ResourceId == $right.NodeId
| project-away ResourceId, NodeId
//| extend globalFrom = globalFrom
```

**Params:** `{queryFrom}`, `{queryTo}`, `{local_nodeId}`

---

### Host OS Version

_Widget purpose:_ Node2 Details

Cluster: `wdgeventstore.kusto.windows.net` · Database: `HostOSDeploy` · Type: `Single` · Widget: `Card`
Source panel: `Host Details > Node2 Details`

```kusto
cluster('wdgeventstore.kusto.windows.net').database('HostOSDeploy').nodes
| where nodeId == local_nodeId
| distinct nodeId, HostOS = OSVersion | take 1 | project HostOS
```

**Params:** `{queryFrom}`, `{queryTo}`, `{local_nodeId}`

---

## VMs running in {{nodeId1}}

### Azure Host Running VMs Query

_Widget purpose:_ VMs running in {{nodeId1}}

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Table`
Source panel: `Host Details > VMs running in {{nodeId1}}`

```kusto
let vmDetails = LogContainerSnapshot
| where PreciseTimeStamp between ((startTime - 1h) .. (endTime + 1h)) and nodeId == nodeIdStr
| extend DiskControlerType = tostring(parse_json(additionalContainerProperties).DiskControllerType) 
| union (
    cluster('storageclient.eastus.kusto.windows.net').database('AzureCP').MycroftContainerSnapshot
    | where PreciseTimeStamp between ((startTime - 1h) .. (endTime + 1h)) and NodeId == nodeIdStr and isnotempty(RoleInstanceName)
    | extend containerId = ContainerId, creationTime = tostring(CreationTime), roleInstanceName = RoleInstanceName, 
         subscriptionId = SubscriptionId, containerType = PolicyName, virtualMachineUniqueId = VirtualMachineUniqueId,
         nodeId = NodeId, tipNodeSessionId = TipNodeSessionId, tenantName = TenantName, availabilitySetName = AvailabilitySetName,
         billingType = "", roleType = RoleType, additionalContainerProperties = AdditionalContainerProperties, Tenant = ClusterName
)
| summarize arg_max(PreciseTimeStamp, creationTime, roleInstanceName, subscriptionId, containerType, virtualMachineUniqueId, nodeId, DiskControlerType) by containerId
| extend creationTime = todatetime(creationTime), lastKnownTime = PreciseTimeStamp, DiskControlerType = case(isnotempty(DiskControlerType), DiskControlerType, containerType contains "_v6", "NVMe", "SCSI")
| project creationTime, lastKnownTime, roleInstanceName, DiskControlerType, containerType, containerId, virtualMachineUniqueId, nodeId, subscriptionId;
let subscriptionDetailsDataStudio = cluster('datastudiostreaming').database('Shared').DataStudio_AzureSubscription_Snapshot
| where SubscriptionId in~ ((vmDetails | distinct subscriptionId))
| distinct SubscriptionId, SubscriptionName, CustomerName;
let subscriptionDetailsCustomerDomData = cluster('customerdomrptwus3prod.westus3').database('CustomerDomData').CustomerModel
| where SubscriptionGuid_String in~ ((vmDetails | distinct subscriptionId))
| distinct SubscriptionId = SubscriptionGuid_String, SubscriptionName = FriendlySubscriptionName, CloudCustomerName, TopParentName = TPNameTranslated;
let subscriptionDetails = union subscriptionDetailsDataStudio, subscriptionDetailsCustomerDomData
| summarize take_anyif(SubscriptionName, isnotempty(SubscriptionName)), 
            take_anyif(CustomerName, isnotempty(CustomerName)), 
            take_anyif(CloudCustomerName, isnotempty(CloudCustomerName)), 
            take_anyif(TopParentName, isnotempty(TopParentName))
            by SubscriptionId
| distinct SubscriptionId, SubscriptionName, 
           CustomerName = case(isnotempty(CustomerName), CustomerName, isnotempty(CloudCustomerName), CloudCustomerName, isnotempty(TopParentName), TopParentName, strcat(SubscriptionName, ' ', CloudCustomerName, ' ', TopParentName));
vmDetails | join kind = leftouter subscriptionDetails on $left.subscriptionId == $right.SubscriptionId
| distinct creationTime, lastKnownTime, roleInstanceName, DiskControlerType, containerType, containerId, virtualMachineUniqueId, nodeId, subscriptionId, SubscriptionName, CustomerName
| order by creationTime asc
| join kind = leftouter (cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapMapVfIdToContainerIdOvl2(nodeIdStr, startTime, endTime)) on containerId
| project-away containerId1;
```

**Params:** `{nodeIdStr}`, `{startTime}`, `{endTime}`

---

## VMs running in {{nodeId2}}

### Azure Host Running VMs Query

_Widget purpose:_ VMs running in {{nodeId2}}

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Table`
Source panel: `Host Details > VMs running in {{nodeId2}}`

```kusto
let vmDetails = LogContainerSnapshot
| where PreciseTimeStamp between ((startTime - 1h) .. (endTime + 1h)) and nodeId == nodeIdStr
| extend DiskControlerType = tostring(parse_json(additionalContainerProperties).DiskControllerType) 
| union (
    cluster('storageclient.eastus.kusto.windows.net').database('AzureCP').MycroftContainerSnapshot
    | where PreciseTimeStamp between ((startTime - 1h) .. (endTime + 1h)) and NodeId == nodeIdStr and isnotempty(RoleInstanceName)
    | extend containerId = ContainerId, creationTime = tostring(CreationTime), roleInstanceName = RoleInstanceName, 
         subscriptionId = SubscriptionId, containerType = PolicyName, virtualMachineUniqueId = VirtualMachineUniqueId,
         nodeId = NodeId, tipNodeSessionId = TipNodeSessionId, tenantName = TenantName, availabilitySetName = AvailabilitySetName,
         billingType = "", roleType = RoleType, additionalContainerProperties = AdditionalContainerProperties, Tenant = ClusterName
)
| summarize arg_max(PreciseTimeStamp, creationTime, roleInstanceName, subscriptionId, containerType, virtualMachineUniqueId, nodeId, DiskControlerType) by containerId
| extend creationTime = todatetime(creationTime), lastKnownTime = PreciseTimeStamp, DiskControlerType = case(isnotempty(DiskControlerType), DiskControlerType, containerType contains "_v6", "NVMe", "SCSI")
| project creationTime, lastKnownTime, roleInstanceName, DiskControlerType, containerType, containerId, virtualMachineUniqueId, nodeId, subscriptionId;
let subscriptionDetailsDataStudio = cluster('datastudiostreaming').database('Shared').DataStudio_AzureSubscription_Snapshot
| where SubscriptionId in~ ((vmDetails | distinct subscriptionId))
| distinct SubscriptionId, SubscriptionName, CustomerName;
let subscriptionDetailsCustomerDomData = cluster('customerdomrptwus3prod.westus3').database('CustomerDomData').CustomerModel
| where SubscriptionGuid_String in~ ((vmDetails | distinct subscriptionId))
| distinct SubscriptionId = SubscriptionGuid_String, SubscriptionName = FriendlySubscriptionName, CloudCustomerName, TopParentName = TPNameTranslated;
let subscriptionDetails = union subscriptionDetailsDataStudio, subscriptionDetailsCustomerDomData
| summarize take_anyif(SubscriptionName, isnotempty(SubscriptionName)), 
            take_anyif(CustomerName, isnotempty(CustomerName)), 
            take_anyif(CloudCustomerName, isnotempty(CloudCustomerName)), 
            take_anyif(TopParentName, isnotempty(TopParentName))
            by SubscriptionId
| distinct SubscriptionId, SubscriptionName, 
           CustomerName = case(isnotempty(CustomerName), CustomerName, isnotempty(CloudCustomerName), CloudCustomerName, isnotempty(TopParentName), TopParentName, strcat(SubscriptionName, ' ', CloudCustomerName, ' ', TopParentName));
vmDetails | join kind = leftouter subscriptionDetails on $left.subscriptionId == $right.SubscriptionId
| distinct creationTime, lastKnownTime, roleInstanceName, DiskControlerType, containerType, containerId, virtualMachineUniqueId, nodeId, subscriptionId, SubscriptionName, CustomerName
| order by creationTime asc
| join kind = leftouter (cluster('storageclient.eastus.kusto.windows.net').database('Fa').AsapMapVfIdToContainerIdOvl2(nodeIdStr, startTime, endTime)) on containerId
| project-away containerId1;
```

**Params:** `{nodeIdStr}`, `{startTime}`, `{endTime}`

---
