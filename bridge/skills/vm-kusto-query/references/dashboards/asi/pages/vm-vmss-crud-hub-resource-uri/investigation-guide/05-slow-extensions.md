# Slow Extensions

> Source: **Resource URI** dashboard, chapter **Slow Extensions** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Slow Extensions v2

Cluster: `azcore.centralus` · Database: `Crp` · Type: `Table`
Source panel: `Slow Extensions`

```kusto
let subid = tolower(split(ResURI,"/")[2]);
let rgName = split(ResURI,"/")[4];
let resName = split(ResURI,"/")[8];
let vmssInstanceName = split(ResURI,"/")[10];
let LONG_DURATION = 600000;
let opids = materialize(ApiQosEvent
| where PreciseTimeStamp between (queryFrom..queryTo)
| where operationName !contains "GET"
| where subscriptionId =~ subid
| where resourceGroupName =~ tostring(rgName)
| where resourceName has tostring(resName) or (isnotempty(vmssInstanceName) and resourceName has tostring(vmssInstanceName))
| where e2EDurationInMilliseconds > LONG_DURATION
| where operationName !in ("AsyncOperationCompletionOperation", "VirtualMachines.RetrieveBootDiagnosticsData.POST", "VirtualMachines.RetrieveVMConsoleScreenshot.POST", "Deployments.Preflight.POST", "DiskRPCallback.AllocateDisks.POST", "VirtualMachines.RetrieveVMConsoleScreenshot.POST","CustomerSupport.RetrieveSasUri.POST", "VMScaleSetCleanupInternalOperation","NrpCallback.DeleteTenant.POST", "VirtualMachines.RetrieveVMConsoleSerialLogs.POST", "NrpCallback.FinalizeTenantResourceAllocation.POST", "NrpCallback.RevertTenantResourceAllocation.POST", "NrpCallback.DeallocateAllTenantNetworkResources.POST", "NrpCallback.AllocateTenantNetworkResources.POST", "NrpCallback.CommitTenantResourceAllocation.POST","RestorePoints.RestorePointOperation.PUT", "Subscriptions.Register.PUT", "AsyncOperationCallbackOperation", "RestorePoints.RestorePointOperation.DELETE", "RestorePoints.RetrieveSasUris.POST", "FabricCallback.OnRoleInstanceStateChange.POST", "RestorePoints.RestorePointOperation.DELETE")
| extend startTime = datetime_add('millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp)
| distinct  operationId);//opids
let longGoalSeekOpids = materialize(ComponentQoSEvent
| where PreciseTimeStamp between (queryFrom..queryTo)
| where fabricTenantName != ""
| where activityId in (opids)
| where operationName == "PollForVMExtensionsProvisioningResult" and durationInMs > LONG_DURATION
| summarize by activityId);
//longGoalSeekOpids
 macro-expand isfuzzy=true entity_group [cluster('azcore.centralus.kusto.windows.net').database('Crp')] as X (
union X.ContextActivity, X.VmssVMGoalSeekingActivity
| where PreciseTimeStamp between (queryFrom..queryTo)
| where activityId in (longGoalSeekOpids)
//Is there a way to avoid contains? maybe if we use "has" instead? Need to test.
| where message contains  "Handler status is 'NotReady'" 
        or message contains "has reported status 'Transitioning'" 
        or message contains '"status": "transitioning"' 
        or message contains "has reported status 'NotReady'" 
        or message contains "reported to be in state 'Installing'. Waiting for the handler to finish installation." 
| summarize  arg_min(PreciseTimeStamp, activityId), arg_max(PreciseTimeStamp, activityId) by message
| extend FirstTimeStamp = PreciseTimeStamp
| extend LastTimeStamp = PreciseTimeStamp1
| extend FirstActivityId = activityId
| extend LastActivityId = activityId1
| extend duration = LastTimeStamp - FirstTimeStamp)
| project duration, FirstTimeStamp, FirstActivityId, LastTimeStamp, LastActivityId, message
```

**Params:** `{queryFrom}`, `{queryTo}`, `{ResURI}`

**Signal filters seen in KQL:** `operationName == "PollForVMExtensionsProvisioningResult"` · `message contains "Handler status is 'NotReady'"`

---
