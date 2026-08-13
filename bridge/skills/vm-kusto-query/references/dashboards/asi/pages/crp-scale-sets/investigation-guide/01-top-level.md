# (top-level)

> Source: **CRP — Scale Sets** dashboard, chapter **(top-level)** (8 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Scale Sets"

Cluster: `azcrpbifollower` · Database: `bi_allprod` · Type: `ResourceGet` · Widget: `Container`

```kusto
// LogicalCompute_VirtualMachineScaleSetNRT
// | where SubscriptionId =~ local_subscriptionId and ResourceGroupName =~ local_resourceGroupName and ResourceName =~ local_vmssName
// | top 1 by TimeStamp desc
cluster('azcrpbifollower.kusto.windows.net').database('bi_allprod').VMScaleSet
| where PreciseTimeStamp between (globalFrom .. globalTo)
| where SubscriptionId =~ local_subscriptionId
| where ResourceGroupName =~ local_resourceGroupName
| where VMScaleSetName =~ local_vmssName
| where isempty(local_VMScaleSetId) or VMScaleSetId =~ local_VMScaleSetId
| summarize SnapshotTime = arg_max(PreciseTimeStamp, *)  by SubscriptionId = tolower(SubscriptionId), ResourceGroupName= tolower(ResourceGroupName), ResourceName = tolower(VMScaleSetName), vmssName = tolower(VMScaleSetName)
| extend VMScaleSetId = tolower(VMScaleSetId) 
| extend ArmResourceId = strcat("/subscriptions/", SubscriptionId, "/resourceGroups/", ResourceGroupName, "/providers/Microsoft.Compute/virtualMachineScaleSets/", VMScaleSetName)
| extend queryVMSSResourceId = ArmResourceId
| extend OrchestrationType = iif(isempty(OrchestrationMode), "Uniform", OrchestrationMode)
```

**Params:** `{local_resourceGroupName}`, `{local_subscriptionId}`, `{local_VMScaleSetId}`, `{local_vmssName}`, `{globalFrom}`, `{globalTo}`

---

### Find OS Prov Failures

_Widget purpose:_ Auto Issue Detection

Cluster: `azcrpbifollower` · Database: `bi_allprod` · Type: `IssueDetector`

```kusto
cluster("azcrpbifollower").database("bi_allprod").VMAllocationInfo
| where PreciseTimeStamp between (qFrom .. qTo)
| where ResourceGroupName =~ qRG and SubscriptionId == qSub 
| parse-where kind=regex flags=i VMName with "_" VMScaleSetName "_" InstanceId:long
| where VMScaleSetName =~ qVMSS
| project PreciseTimeStamp, VMName, InstanceId, State, IsGuestOSProvisioned
| summarize arg_max(PreciseTimeStamp, *) by InstanceId
| where IsGuestOSProvisioned != 'True'
| extend Message = strcat('VM: ', VMName, ' is reporting that IsGuestOSProvisioned is false. It needs to be re-imaged.')
| summarize make_set(Message)
| extend Title = "VMs have failed OS Provisioning state."
| extend Description = array_strcat(set_Message, "<br>")
| extend Severity = "critical"
| where isnotempty(Description)
| project Title, Description, Severity
```

**Params:** `{qFrom}`, `{qTo}`, `{qSub}`, `{qRG}`, `{qVMSS}`

**Signal filters seen in KQL:** `IsGuestOSProvisioned != "True"`

---

### Query SF Extension 

_Widget purpose:_ Service Fabric

Cluster: `azcrpbifollower` · Database: `bi_allprod` · Type: `Single` · Widget: `Card`

```kusto
VMScaleSetVMExtension
| where PreciseTimeStamp between (min_of(datetime_add("hour", -8, queryTo), queryFrom) .. queryTo)
| where SubscriptionId == querySubId
| where ResourceGroupName =~ queryResourceGroup
| where VMScaleSetName =~ queryVmssName
| where Publisher contains "Microsoft.Azure.ServiceFabric"
| summarize count(), SnapshotTime = max(PreciseTimeStamp) 
| extend SFExtensionEnabled =  iif(count_ > 0, "Installed", "Not Detected")
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryResourceGroup}`, `{querySubId}`, `{queryVmssName}`, `{queryParam5}`

**Signal filters seen in KQL:** `Publisher contains "Microsoft.Azure.ServiceFabric"`

---

### Locate SF Cluster 

_Widget purpose:_ Service Fabric

Cluster: `sflogs` · Database: `SFRP` · Type: `Single` · Widget: `Card`

```kusto
NodeTypeVMSSMapping
| where PreciseTimeStamp  between (min_of((queryTo - 90d), queryFrom) .. queryTo)
| where VMSSId =~ queryVmssArmId
| project PreciseTimeStamp,  VMSSId = tolower(VMSSId), ClusterId = tolower(ClusterId), ClusterResourceId = tolower(ClusterResourceId), NodeTypeName = tolower(NodeTypeName)
| summarize SnapshotTime = arg_max(PreciseTimeStamp, *)
// | where isnotempty(ClusterResourceId)
| extend SubscriptionId = tostring(split(ClusterResourceId, "/")[2])
| extend ResourceGroup = tostring(split(ClusterResourceId, "/")[4])
| extend ClusterName = tostring(split(ClusterResourceId, "/")[8])
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryVmssArmId}`

---

### VMSS Request Deltas

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Timeline`

```kusto
VmssQoSEvent
| where PreciseTimeStamp between(queryFrom..queryTo)
| where resourceGroupName =~ queryResourceGroupName and subscriptionId =~ querySubscriptionId
| where vmssName =~ queryScaleSetName
| where vMCountDelta != 0
| where operationName != "VirtualMachineScaleSets.repairVMs.POST"
| extend Content = strcat(
    "VM Delta: ", vMCountDelta,
    "<br/>Target Instance Count: ", targetInstanceCount
)
| extend Tooltip = strcat(
    "VM Delta: ", vMCountDelta,
    "<br/>Target Instance Count: ", targetInstanceCount,
    "<br/>Note, the delta is the number of VMs added or removed by the request"
)
| project StartTime = PreciseTimeStamp, Content, Tooltip, operationId, operationName
| order by StartTime asc
```

**Params:** `{querySubscriptionId}`, `{queryResourceGroupName}`, `{queryScaleSetName}`, `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `operationName != "VirtualMachineScaleSets.repairVMs.POST"`

---

### VMSS State

Cluster: `azcrpbifollower` · Database: `bi_allprod` · Type: `Timeline`

```kusto
cluster('azcrpbifollower').database('bi_allprod').VMScaleSetAllocationInfo 
| where TIMESTAMP between (qFrom .. qTo)
| where ResourceGroupName =~ qRG and SubscriptionId =~ qSub and VMScaleSetName =~ qVMSS
| project StartTime = PreciseTimeStamp, Content = State
| order by StartTime asc
| serialize
| where (Content != prev(Content) or Content != next(Content)) 
| extend EndTime = next(StartTime)
| where Content != prev(Content)
```

**Params:** `{qFrom}`, `{qTo}`, `{qRG}`, `{qSub}`, `{qVMSS}`

---

### VMSS Operations

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Timeline`

```kusto
cluster("azcrp").database("crp_allprod").VmssQoSEvent
| where PreciseTimeStamp between(qFrom .. qTo)
| where resourceGroupName =~ qRG and subscriptionId =~ qSub
| where vmssName =~ qVMSS
| project StartTime = PreciseTimeStamp, operationName, resultType, predominantErrorCode, operationId
| extend 
    Content = tostring(split(operationName, '.')[1]), 
    Health = iff(resultType == 0, "Healthy", "Error"), 
    Tooltip = predominantErrorCode
| project StartTime, Content, Health, Tooltip, operationId
```

**Params:** `{qFrom}`, `{qTo}`, `{qRG}`, `{qSub}`, `{qVMSS}`

---

### Query ResourceHealthAzureActivityLogEvent

Cluster: `icmbrain` · Database: `AzureResourceHealth` · Type: `Table`

```kusto
ResourceHealthAzureActivityLogEvent
| where env_time between(queryFrom .. queryTo)
| where subscriptionId == querySubId
| where resourceId contains queryResourceId
| project env_time, resourceId, correlationId, level, resourceType, eventTimestamp, stage, ["title"], details, healthStatus, healthEventType, healthEventCategory, healthEventCause
| order by eventTimestamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryResourceId}`, `{querySubId}`

---
