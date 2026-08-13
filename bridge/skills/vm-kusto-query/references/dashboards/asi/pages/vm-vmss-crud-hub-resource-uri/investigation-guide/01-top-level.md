# (top-level)

> Source: **Resource URI** dashboard, chapter **(top-level)** (7 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Resource URI"

Cluster: `azcore.centralus` · Database: `Crp` · Type: `ResourceGet` · Widget: `Container`

```kusto
macro-expand isfuzzy=false entity_group [cluster('azcore.centralus.kusto.windows.net')] as X (
    X.database('Crp').ApiQosEvent
| where PreciseTimeStamp between (globalFrom .. globalTo)
| where subscriptionId =~ local_subscriptionId
| where resourceGroupName =~ local_resourceGroupName
| where resourceName =~ local_resourceName)
| top 1 by PreciseTimeStamp desc 
| extend ResourceURI = local_ResourceURI
| project subscriptionId, resourceGroupName, resourceName, region , ResourceURI
```

**Params:** `{globalFrom}`, `{globalTo}`, `{local_resourceGroupName}`, `{local_resourceName}`, `{local_ResourceURI}`, `{local_subscriptionId}`

---

### Failover Issue Detector Query

_Widget purpose:_ Issues Detected

Cluster: `azcore.centralus` · Database: `Crp` · Type: `IssueDetector`

```kusto
let opids = materialize(ApiQosEvent
| where PreciseTimeStamp between((queryFrom)..queryTo)
| where operationName !contains "GET"
| where subscriptionId =~ subId
| where resourceGroupName =~ rgName
| where resourceName == resName
|where operationName !in ("AsyncOperationCompletionOperation", "VirtualMachines.RetrieveBootDiagnosticsData.POST", "VirtualMachines.RetrieveVMConsoleScreenshot.POST", "Deployments.Preflight.POST", "DiskRPCallback.AllocateDisks.POST", "VirtualMachines.RetrieveVMConsoleScreenshot.POST","CustomerSupport.RetrieveSasUri.POST", "VMScaleSetCleanupInternalOperation","NrpCallback.DeleteTenant.POST", "VirtualMachines.RetrieveVMConsoleSerialLogs.POST", "NrpCallback.FinalizeTenantResourceAllocation.POST", "NrpCallback.RevertTenantResourceAllocation.POST", "NrpCallback.DeallocateAllTenantNetworkResources.POST", "NrpCallback.AllocateTenantNetworkResources.POST", "NrpCallback.CommitTenantResourceAllocation.POST","RestorePoints.RestorePointOperation.PUT", "Subscriptions.Register.PUT", "AsyncOperationCallbackOperation", "RestorePoints.RestorePointOperation.DELETE", "RestorePoints.RetrieveSasUris.POST", "FabricCallback.OnRoleInstanceStateChange.POST", "RestorePoints.RestorePointOperation.DELETE")
| distinct  operationId);
let tenantNames = materialize (ComponentQoSEvent
| where PreciseTimeStamp between((queryFrom)..queryTo)
| where fabricTenantName != ""
| where activityId in (opids)
//|summarize min(PreciseTimeStamp),max(PreciseTimeStamp) by fabricCluster, fabricTenantName
| distinct fabricTenantName);
let clusters = materialize(cluster('azcore.centralus').database('Fc').TMMgmtTenantEventsEtwTable
| where PreciseTimeStamp between((queryFrom -1d)..(queryTo +1d))
| where TenantName in~ (tenantNames) 
| distinct Tenant);
cluster('azcore.centralus').database('Fc').LogFabricatorStartUpDetails
| where PreciseTimeStamp between((queryFrom)..(queryTo))
| where Tenant in~  (clusters)
| sort by PreciseTimeStamp asc 
| where phase =~ "ManagementCtr.Step 0" | take 1 //or PreciseTimeStamp == firstPreciseTimeStamp | take 1
| extend Description = "Fabricators for the clusters the VM(s) were on have failed over,  head on over to the Fabric failover tab below for details or refer this TSG: https://aka.ms/CSSFabricFailoverOps"
| extend Severity = 'warning'
```

**Params:** `{queryFrom}`, `{queryTo}`, `{subId}`, `{rgName}`, `{resName}`

**Signal filters seen in KQL:** `phase =~ "ManagementCtr.Step 0"`

---

### NeworkingInternalOperationError Detector 

_Widget purpose:_ Issues Detected

Cluster: `azcore.centralus` · Database: `Crp` · Type: `IssueDetector`

```kusto
ApiQosEvent
    | where PreciseTimeStamp between(queryFrom..queryTo)
    | where operationName !contains "GET"
    and subscriptionId == subId
    and resourceGroupName =~ rgName
    and resourceName contains resName
    and resultCode == 'NetworkingInternalOperationError' | take 1
    | extend Description = "Operations have failed with NetworkingInternalOperationError, review the NetworkingInternalOperationError tab below for more details. TSG: https://aka.ms/CCSupNetworkingInternalError"
    | extend Severity = "error"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{subId}`, `{rgName}`, `{resName}`

---

### Slow Extensions

_Widget purpose:_ Issues Detected

Cluster: `azcore.centralus` · Database: `Crp` · Type: `IssueDetector`

```kusto
let opids = materialize(ApiQosEvent
| where PreciseTimeStamp between (queryFrom..queryTo)
| where subscriptionId =~ subId and operationName !contains "GET"
| where resourceGroupName =~ resourceGroupName
| where resourceName has resName
| where operationName !in ("AsyncOperationCompletionOperation", "VirtualMachines.RetrieveBootDiagnosticsData.POST", "VirtualMachines.RetrieveVMConsoleScreenshot.POST", "Deployments.Preflight.POST", "DiskRPCallback.AllocateDisks.POST", "VirtualMachines.RetrieveVMConsoleScreenshot.POST","CustomerSupport.RetrieveSasUri.POST", "VMScaleSetCleanupInternalOperation","NrpCallback.DeleteTenant.POST", "VirtualMachines.RetrieveVMConsoleSerialLogs.POST", "NrpCallback.FinalizeTenantResourceAllocation.POST", "NrpCallback.RevertTenantResourceAllocation.POST", "NrpCallback.DeallocateAllTenantNetworkResources.POST", "NrpCallback.AllocateTenantNetworkResources.POST", "NrpCallback.CommitTenantResourceAllocation.POST","RestorePoints.RestorePointOperation.PUT", "Subscriptions.Register.PUT", "AsyncOperationCallbackOperation", "RestorePoints.RestorePointOperation.DELETE", "RestorePoints.RetrieveSasUris.POST", "FabricCallback.OnRoleInstanceStateChange.POST", "RestorePoints.RestorePointOperation.DELETE")
| where e2EDurationInMilliseconds > 600000
| extend startTime = datetime_add('millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp)
| distinct  operationId);//opids
let longGoalSeekOpids = materialize(ComponentQoSEvent
| where PreciseTimeStamp between (queryFrom..queryTo)
| where fabricTenantName != ""
| where activityId in (opids)
| where operationName == "PollForVMExtensionsProvisioningResult" and durationInMs > 600000
| summarize by activityId);
//longGoalSeekOpids
union ContextActivity, VmssVMGoalSeekingActivity 
| where PreciseTimeStamp between (queryFrom..queryTo)
| where activityId in (longGoalSeekOpids)
| where message contains  "Handler status is 'NotReady'" or message contains "has reported status 'Transitioning'" or message contains '"status": "transitioning"' or message contains "has reported status 'NotReady'"
| summarize  arg_min(PreciseTimeStamp, activityId), arg_max(PreciseTimeStamp, activityId) by message
| extend FirstTimeStamp = PreciseTimeStamp
| extend LastTimeStamp = PreciseTimeStamp1
| extend FirstActivityId = activityId
| extend LastActivityId = activityId1
| extend duration = LastTimeStamp - FirstTimeStamp
| take 1 
| extend Description = "Extensions have been in transioning or NotReady state for more than 10 minutes, review the Slow Extensions tab under CRP Troubleshooting below for more detail. TSG: https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/884230/90-minute-extension-timeout_AGEX"
| extend Severity = "warning"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{subId}`, `{rgName}`, `{resName}`

**Signal filters seen in KQL:** `operationName == "PollForVMExtensionsProvisioningResult"` · `message contains "Handler status is 'NotReady'"`

---

### VMStartTimedOut Detector

_Widget purpose:_ Issues Detected

Cluster: `azcore.centralus` · Database: `Crp` · Type: `IssueDetector`

```kusto
ApiQosEvent
    | where PreciseTimeStamp between(queryFrom..queryTo)
    | where operationName !contains "GET"
    and subscriptionId == subId
    and resourceGroupName =~ rgName
    and resourceName =~ resName
    and resultCode == 'VMStartTimedOut' | take 1
    | extend Description = "Operations have failed with VMStartTimedOut, review the VMStartTimedOut tab below for more details. TSG: http://aka.ms/VMStartTimedOut "
    | extend Severity = "error"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{subId}`, `{rgName}`, `{resName}`

---

### Failures / Slow operations

Cluster: `azcore.centralus` · Database: `Crp` · Type: `Timeline`

```kusto
ApiQosEvent
| where PreciseTimeStamp between(queryFrom..queryTo)
| where operationName !contains "GET"
| where subscriptionId =~ subId
| where resourceGroupName =~ rgName
| where resourceName contains resName
| where resultCode != "" or e2EDurationInMilliseconds > 600000
|where operationName !in ("AsyncOperationCompletionOperation", "VirtualMachines.RetrieveBootDiagnosticsData.POST", "VirtualMachines.RetrieveVMConsoleScreenshot.POST", "Deployments.Preflight.POST", "DiskRPCallback.AllocateDisks.POST", "VirtualMachines.RetrieveVMConsoleScreenshot.POST","CustomerSupport.RetrieveSasUri.POST", "VMScaleSetCleanupInternalOperation","NrpCallback.DeleteTenant.POST", "VirtualMachines.RetrieveVMConsoleSerialLogs.POST", "NrpCallback.FinalizeTenantResourceAllocation.POST", "NrpCallback.RevertTenantResourceAllocation.POST", "NrpCallback.DeallocateAllTenantNetworkResources.POST", "NrpCallback.AllocateTenantNetworkResources.POST", "NrpCallback.CommitTenantResourceAllocation.POST","RestorePoints.RestorePointOperation.PUT", "Subscriptions.Register.PUT", "AsyncOperationCallbackOperation", "RestorePoints.RestorePointOperation.DELETE", "RestorePoints.RetrieveSasUris.POST", "FabricCallback.OnRoleInstanceStateChange.POST", "RestorePoints.RestorePointOperation.DELETE")
| extend StartTime = datetime_add('millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp)
//| extend EndTime = PreciseTimeStamp
| extend Content = strcat(operationName, iff(resultCode != "", strcat(" - ", resultCode), ""), iff (e2EDurationInMilliseconds >= long(600000), strcat(" - Duration: ", e2EDurationInMilliseconds, " Ms"), ""))
| project  StartTime, Content, PreciseTimeStamp, operationName, httpStatusCode, resultCode, errorDetails,  clientPrincipalName, clientApplicationId, userAgent, correlationId, operationId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{subId}`, `{rgName}`, `{resName}`

---

### Active Azsm/Fabric Tenants

Cluster: `azcore.centralus` · Database: `Crp` · Type: `Timeline`

```kusto
let unix_epoch_start = datetime(1/1/1970);
let opids = materialize(ApiQosEvent
| where PreciseTimeStamp between((queryFrom)..queryTo)
| where operationName !contains "GET"
| where subscriptionId =~ subId
| where resourceGroupName =~ rgName
| where resourceName == resName
|where operationName !in ("AsyncOperationCompletionOperation", "VirtualMachines.RetrieveBootDiagnosticsData.POST", "VirtualMachines.RetrieveVMConsoleScreenshot.POST", "Deployments.Preflight.POST", "DiskRPCallback.AllocateDisks.POST", "VirtualMachines.RetrieveVMConsoleScreenshot.POST","CustomerSupport.RetrieveSasUri.POST", "VMScaleSetCleanupInternalOperation","NrpCallback.DeleteTenant.POST", "VirtualMachines.RetrieveVMConsoleSerialLogs.POST", "NrpCallback.FinalizeTenantResourceAllocation.POST", "NrpCallback.RevertTenantResourceAllocation.POST", "NrpCallback.DeallocateAllTenantNetworkResources.POST", "NrpCallback.AllocateTenantNetworkResources.POST", "NrpCallback.CommitTenantResourceAllocation.POST","RestorePoints.RestorePointOperation.PUT", "Subscriptions.Register.PUT", "AsyncOperationCallbackOperation", "RestorePoints.RestorePointOperation.DELETE", "RestorePoints.RetrieveSasUris.POST", "FabricCallback.OnRoleInstanceStateChange.POST", "RestorePoints.RestorePointOperation.DELETE")
| distinct  operationId);
let tenantNames = materialize (ComponentQoSEvent
| where PreciseTimeStamp between((queryFrom)..queryTo)
| where fabricTenantName != ""
| where activityId in (opids)
//|summarize min(PreciseTimeStamp),max(PreciseTimeStamp) by fabricCluster, fabricTenantName
| distinct fabricTenantName);
//| extend Content = fabricTenantName
//| extend StartTime = min_PreciseTimeStamp , EndTime = max_PreciseTimeStamp
//| distinct fabricTenantName);
cluster('azcore.centralus').database('Fc').LogTenantSnapshot //More accurate and we can get the actual fabric cluster and other details. 
| where PreciseTimeStamp between((queryFrom)..queryTo)
| where tenantName in~ (tenantNames)
//| summarize StartTime = arg_min(PreciseTimeStamp, tenantName), EndTime = arg_max(PreciseTimeStamp, tenantName)by  Cluster =  Tenant, tenantName, isSpannable, isSpanned
| summarize StartTime = arg_min(PreciseTimeStamp, tenantName)by  Cluster =  Tenant, tenantName, isSpannable, isSpanned
| extend startTimeTicks = datetime_diff("second", queryFrom, unix_epoch_start ) * 1000
| extend endTimeTicks = datetime_diff("second", queryTo, unix_epoch_start) * 1000
| extend FailoverDashBoardUrl = strcat("https://portal.microsoftgeneva.com/s/FEEEA?overrides=[{\"query\":\"//*[id='Tenant']\",\"key\":\"value\",\"replacement\":\"" , Cluster, "\"}]&globalStartTime=", startTimeTicks, "&globalEndTime=" , endTimeTicks, "&pinGlobalTimeRange=true")
| project StartTime, Content = tenantName, Cluster, isSpannable, isSpanned, FailoverDashBoardUrl
```

**Params:** `{queryFrom}`, `{queryTo}`, `{subId}`, `{resName}`, `{rgName}`

---
