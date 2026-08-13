# (top-level)

> Source: **Confidential Virtual Machines - Confidential Virtual Machine** dashboard, chapter **(top-level)** (5 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Confidential Virtual Machine"

Cluster: `azcrp` · Database: `crp_allprod` · Type: `ResourceGet` · Widget: `Container`

```kusto
let vmDeploymentOperationId = toscalar(cluster('azcrp').database('crp_allprod').VMApiQosEvent
| where vMId == local_VMId
| where operationName == 'VirtualMachines.ResourceOperation.PUT' or operationName == 'VMExtensions.VMExtensionOperation.PUT'
| distinct operationId);
cluster('azcrp').database('crp_allprod').ApiQosEvent_nonGet
| where operationName == 'VirtualMachines.ResourceOperation.PUT' or operationId == 'VMExtensions.VMExtensionOperation.PUT'
| where subscriptionId =~ local_SubscriptionId and resourceGroupName =~ local_ResourceGroupName and resourceName =~ local_ResourceName
| where operationId in (vmDeploymentOperationId)
| project 
    SubscriptionId = local_SubscriptionId, 
    ResourceGroupName = local_ResourceGroupName, 
    ResourceName = local_ResourceName, 
    VMId = local_VMId, 
    DeploymentId = operationId,
    CorrelationId = correlationId,
    ResultCode = resultCode,
    ExceptionType = exceptionType,
    ErrorDetails = errorDetails,
    Region = region,
    RequestBody = requestEntity
```

**Params:** `{globalFrom}`, `{globalTo}`, `{local_SubscriptionId}`, `{local_ResourceGroupName}`, `{local_ResourceName}`, `{local_VMId}`

**Signal filters seen in KQL:** `operationName == "VirtualMachines.ResourceOperation.PUT"`

---

### CRP VM Events

_Widget purpose:_ VM Events

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Timeline`

```kusto
ApiQosEvent_nonGet
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where subscriptionId =~ querySubscriptionId and resourceGroupName =~ queryResourceGroup and resourceName =~ queryResourceName
| project StartTime = PreciseTimeStamp - (e2EDurationInMilliseconds * 1ms), EndTime = PreciseTimeStamp, correlationId, Content = operationName, Health = iff(isempty(resultCode), "Healthy", "Error"), CorrelationId = correlationId, ErrorDetails = errorDetails
```

**Params:** `{queryFrom}`, `{queryTo}`, `{querySubscriptionId}`, `{queryResourceGroup}`, `{queryResourceName}`, `{queryVmId}`

---

### Container Events

_Widget purpose:_ VM Events

Cluster: `azcore.centralus` · Database: `AzureCP` · Type: `Timeline`

```kusto
MycroftContainerHealthSnapshot
| where PreciseTimeStamp between ((queryFrom - 1d) .. (queryTo + 1d))
| where isnotempty(queryVmId) and VirtualMachineUniqueId == queryVmId
| sort by PreciseTimeStamp asc 
| extend StateChanged = ContainerState != prev(ContainerState)
| where StateChanged
| project 
StartTime = PreciseTimeStamp, 
EndTime = next(PreciseTimeStamp), 
Content = ContainerState, 
Health = case(
    ContainerState == "ContainerStateUnknown", "Degraded", 
    ContainerState == "ContainerStateStopped", "Degraded", 
    ContainerState == "ContainerStateDestroyed", "Error", 
    "Healthy"
)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryVmId}`

---

### VM Containers

Cluster: `azcore.centralus` · Database: `AzureCP` · Type: `Table` · Widget: `TabPane`

```kusto
MycroftContainerSnapshot
| where PreciseTimeStamp between ((queryFrom - 1d) .. (queryTo + 1d))
| where isnotempty(queryVmId) and VirtualMachineUniqueId == queryVmId
| summarize arg_max(PreciseTimeStamp, *) by ContainerId
| project FirstSeen = CreationTime, LastSeen = PreciseTimeStamp, ContainerId, ClusterName, NodeId, Sku = PolicyName, TipNodeSessionId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryVmId}`

---

### Execution Graph

Cluster: `executiongraph` · Database: `eg` · Type: `Table`

```kusto
IaasVmOperations
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where CrpVmId == queryVmId
| project Timestamp = StartTime, EgUrl, OperationName, E2EDurationInSeconds, Result, FailureCategory, FailureSignature
| sort by Timestamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryVmId}`

---
