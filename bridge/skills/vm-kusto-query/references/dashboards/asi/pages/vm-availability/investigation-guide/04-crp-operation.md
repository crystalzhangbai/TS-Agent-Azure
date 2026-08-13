# CRP / Operation

> Source: **EEE RDOS — VM Availability** dashboard, chapter **CRP / Operation** (5 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Operation

### CRP VM Snapshot

_Widget purpose:_ VM Entity

Cluster: `azcrpbifollower` · Database: `bi_allprod` · Type: `Single` · Widget: `Card`
Source panel: `CRP / Operation > Operation > CRP KVS > VM Entity`

```kusto
union cluster('azcrpbifollower.kusto.windows.net').database('bi_allprod').VM ,  cluster('azcrpbifollower.kusto.windows.net').database('bi_allprod').VMScaleSetVMInstance
| where PreciseTimeStamp between (queryFrom .. queryTo) 
| where (VMId == vmid or VMScaleSetVMInstanceId ==vmid)and (toupper(VMName) == toupper(trim_start("_", queryRoleInstanceName)) or toupper(strcat(VMScaleSetName,"_",InstanceIdString)) == toupper(trim_start("_", queryRoleInstanceName)))
| top 1 by PreciseTimeStamp asc
| extend ArmResourceId = iff(isempty(vmid),strcat("/subscriptions/", SubscriptionId, "/resourceGroups/", ResourceGroupName, "/providers/Microsoft.Compute/virtualMachineScaleSets/", VMScaleSetName) ,strcat("/subscriptions/", SubscriptionId, "/resourceGroups/", ResourceGroupName, "/providers/Microsoft.Compute/virtualMachines/", VMName) )
| project PreciseTimeStamp, ResourceGroupName = tolower(ResourceGroupName), SubscriptionId = tolower(SubscriptionId), VMId, VMName = tolower(VMName), Region, Key, VMTags, VMResourcePurchasePlan, VMTimeCreated, VMToBeDeleted, VMSize, DesiredPowerState, NetworkProfile, 
   ComputerName, OSDiskOSType, OSDiskCreateOption, OSDiskCachingType, OSDiskId, OSDiskTimeCreated, OSDiskToBeDeleted, OSDiskManagedDiskStorageAccountType, 
   AvailabilitySetKey, HyperVGeneration, CommitSequenceNumber, ArmResourceId
| extend Dummy = "***"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{vmid}`, `{queryRoleInstanceName}`

---

### CRP Operations

_Widget purpose:_ CRP Operation

Cluster: `Azcrp` · Database: `crp_allprod` · Type: `Table`
Source panel: `CRP / Operation > Operation > CRP Operation > CRP Operation > CRP Operation`

```kusto
let vmname = trim_start("_", queryRoleInstanceName);
let vmssname = trim_end("_[0-9]+", vmname);
cluster('azcrp.kusto.windows.net').database('crp_allprod').ApiQosEvent
| where PreciseTimeStamp between(starttime .. endtime)
| where subscriptionId == querySubId
| where resourceName contains vmname or
        (vmssname <> "" and resourceName contains vmssname)
| where operationName !contains "GET"
| extend fitlerOperationType =  case (operationName contains "Callback" or operationName =~ "AsyncOperationCompletionOperation", 1, 
  operationName has_any("AllocateDisks", "RetrieveBootDiagnosticsData", "RetrieveVMConsoleScreenshot", "PreflightRetrieveSasUri", "OnRoleInstanceStateChange",
  "Register", "Preflight", "ExtensionOperation", "RetrieveSasUris", "RetrieveVMConsoleSerialLogs"), 2, 
  3)
| where fitlerOperationType >= iif(filterValue == "All", 0, iif(filterValue == "ExcludeCallbacks", 2, 3))
| extend StartTime = datetime_add('Millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp)
| extend durationInMin = e2EDurationInMilliseconds / 1000 / 60
| project StartTime, EndTime = PreciseTimeStamp, operationId, correlationId, operationName, resourceGroupName, resourceName, 
  httpStatusCode, e2EDurationInMilliseconds, resultType, resultCode, errorDetails, requestEntity, subscriptionId, userAgent, clientApplicationId,
  apiVersion, labels, region, RPTenant, clientPrincipalName, clientRequestId, durationInMin, fitlerOperationType
| order by StartTime asc
| extend level = case (resultCode <> "", "error", "info")
```

**Params:** `{starttime}`, `{endtime}`, `{vmid}`, `{filterValue}`, `{querySubId}`, `{queryRoleInstanceName}`

---

### filterCRP

_Widget purpose:_ CRP Operation

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Filter` · Widget: `Table`
Source panel: `CRP / Operation > Operation > CRP Operation > CRP Operation > CRP Operation`

```kusto
datatable (Value:string, Description:string)
[
    "Critical", "Critical NonGet Operations (default)",
    "ExcludeCallbacks", "All NonGet Operations without Callbacks",
    "All", "All NonGet Operations"
]
```

---

### CRP Operation Timeline

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Timeline`
Source panel: `CRP / Operation > Operation > CRP Operation > CRP Operation > CRP Operation Timeline`

```kusto
let vmname = trim_start("_", queryInstanceName);
let vmssname = trim_end("_[0-9]+", vmname);
cluster('azcrp.kusto.windows.net').database('crp_allprod').ApiQosEvent
| where PreciseTimeStamp between(starttime .. endtime)
| where subscriptionId =~ querySubId
| where resourceName contains vmname or 
        (vmssname <> "" and resourceName contains vmssname)
| where operationName !contains "GET"
| where operationName !contains "NrpCallback"
| where operationName !contains "AllocateDisks"
| where operationName !contains "ExtensionOperation"
| extend StartTime = datetime_add('Millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp)
| extend durationInMin = e2EDurationInMilliseconds / 1000 / 60
| project StartTime, EndTime = PreciseTimeStamp, operationId, correlationId, operationName, resourceGroupName, resourceName, 
  httpStatusCode, e2EDurationInMilliseconds, resultCode, errorDetails, requestEntity, subscriptionId, userAgent, 
  apiVersion, labels, region, RPTenant, clientPrincipalName, clientRequestId, durationInMin
| extend Health = case (isnotempty(resultCode), "Unhealthy", "Healthy")
| extend GroupBy = operationName
| extend Content = case (isnotempty(resultCode), resultCode, tostring(httpStatusCode))
| order by operationName asc
```

**Params:** `{starttime}`, `{endtime}`, `{vmid}`, `{queryInstanceName}`, `{querySubId}`

---

### Fabric Callback to CRP

_Widget purpose:_ Fabric Callback

Cluster: `azcrp` · Database: `crp_allprod` · Type: `Table`
Source panel: `CRP / Operation > Operation > CRP Operation > CRP Operation > Fabric Callback`

```kusto
let vmname = trim_start("_", queryRoleInstanceName);
cluster("azcrp.kusto.windows.net").database("crp_allprod").ApiQosEvent
| where PreciseTimeStamp between(starttime .. endtime)
| where subscriptionId == querySubId
| where resourceName contains vmname
| where operationName contains "FabricCallback"
| extend StartTime = datetime_add('Millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp)
| extend durationInMin = e2EDurationInMilliseconds / 1000 / 60
| project EndTime = PreciseTimeStamp, StartTime, operationId, correlationId, operationName, resourceGroupName, resourceName, 
  httpStatusCode, e2EDurationInMilliseconds, resultCode, errorDetails, requestEntity, subscriptionId, userAgent, 
  apiVersion, labels, region, RPTenant, clientPrincipalName, clientRequestId, durationInMin
| project StartTime, EndTime, correlationId, operationId, httpStatusCode, resultCode, errorDetails, requestEntity, clientPrincipalName
| extend fabric_serviceInstanceName = parse_json(requestEntity).serviceInstanceName, 
    fabric_roleInstanceIsRunning = parse_json(requestEntity).roleInstanceIsRunning, 
    fabric_roleInstanceIsExpectedToRun = parse_json(requestEntity).roleInstanceIsExpectedToRun, 
    fabric_vmId = parse_json(requestEntity).vmId,
    fabric_guestOsProvisioningResult = parse_json(requestEntity).guestOsProvisioningResult,
    fabric_expectedRunningStateChangedReason = parse_json(requestEntity).expectedRunningStateChangedReason,
    fabric_containerState_isUpdatedToLatestConfigFile = parse_json(requestEntity).containerState.isUpdatedToLatestConfigFile,
    fabric_containerState_isRunning = parse_json(requestEntity).containerState.isRunning,
    fabric_containerState_isFaulted = parse_json(requestEntity).containerState.isFaulted,
    fabric_containerState_toBeDeleted = parse_json(requestEntity).containerState.toBeDeleted,
    fabric_containerState_normalizedFaultInfo_faultCode = parse_json(requestEntity).containerState.normalizedFaultInfo.faultCode
| order by StartTime asc
```

**Params:** `{starttime}`, `{endtime}`, `{vmid}`, `{querySubId}`, `{queryRoleInstanceName}`

**Signal filters seen in KQL:** `operationName contains "FabricCallback"`

---
