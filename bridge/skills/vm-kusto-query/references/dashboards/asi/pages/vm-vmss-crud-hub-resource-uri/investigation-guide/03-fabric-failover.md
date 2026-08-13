# Fabric Failover

> Source: **Resource URI** dashboard, chapter **Fabric Failover** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get Failovers

Cluster: `azcore.centralus` · Database: `Crp` · Type: `Timeline`
Source panel: `Fabric Failover`

```kusto
//Portion of the query is from the EEE RDOS Fabric Failover query - Thanks Kenichiro and Adam!
let unix_epoch_start = datetime(1/1/1970);
let opids = materialize(ApiQosEvent
| where PreciseTimeStamp between((queryFrom)..(queryTo))
| where operationName !contains "GET"
| where subscriptionId =~ subId
| where resourceGroupName =~ rgName
| where resourceName == resName
|where operationName !in ("AsyncOperationCompletionOperation", "VirtualMachines.RetrieveBootDiagnosticsData.POST", "VirtualMachines.RetrieveVMConsoleScreenshot.POST", "Deployments.Preflight.POST", "DiskRPCallback.AllocateDisks.POST", "VirtualMachines.RetrieveVMConsoleScreenshot.POST","CustomerSupport.RetrieveSasUri.POST", "VMScaleSetCleanupInternalOperation","NrpCallback.DeleteTenant.POST", "VirtualMachines.RetrieveVMConsoleSerialLogs.POST", "NrpCallback.FinalizeTenantResourceAllocation.POST", "NrpCallback.RevertTenantResourceAllocation.POST", "NrpCallback.DeallocateAllTenantNetworkResources.POST", "NrpCallback.AllocateTenantNetworkResources.POST", "NrpCallback.CommitTenantResourceAllocation.POST","RestorePoints.RestorePointOperation.PUT", "Subscriptions.Register.PUT", "AsyncOperationCallbackOperation", "RestorePoints.RestorePointOperation.DELETE", "RestorePoints.RetrieveSasUris.POST", "FabricCallback.OnRoleInstanceStateChange.POST", "RestorePoints.RestorePointOperation.DELETE")
| extend startTime = datetime_add('millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp)
| distinct  operationId);
//opids
let tenants = materialize(ComponentQoSEvent
| where PreciseTimeStamp between((queryFrom)..(queryTo))
| where fabricTenantName != ""
| where activityId in (opids)
|distinct fabricTenantName); 
//tenants
let clusters = materialize(cluster('azcore.centralus').database('Fc').TMMgmtTenantEventsEtwTable
| where PreciseTimeStamp between((queryFrom)..(queryTo))
| where TenantName in~ (tenants) 
| distinct Tenant);
cluster('azcore.centralus').database('AzureCP').MycroftClusterSnapshot
| where PreciseTimeStamp between((queryFrom)..(queryTo))
| where ClusterName in~  (clusters)
| order by ClusterName, PreciseTimeStamp asc 
| extend  StartTime = PreciseTimeStamp//, tenantName, roleInstanceName, Tenant
| extend flag = case (prev(RoleInstanceName) <> RoleInstanceName or prev(ClusterName) != ClusterName, "changed", "")
| where flag <> ""
| extend EndTime = case (isnotempty(next(StartTime)) and next(Tenant) == Tenant, next(StartTime) , queryTo)
| extend startTimeTicks = datetime_diff("second", queryFrom, unix_epoch_start ) * 1000
| extend endTimeTicks = datetime_diff("second", queryTo, unix_epoch_start) * 1000
| extend dashBoardUrl = strcat("https://portal.microsoftgeneva.com/s/95693FBB?overrides=[{\"query\":\"//*[id='Tenant']\",\"key\":\"value\",\"replacement\":\"" , Tenant, "\"}]&globalStartTime=", startTimeTicks, "&globalEndTime=" , endTimeTicks, "&pinGlobalTimeRange=true")
| extend RCAInvestigation = strcat("https://dataexplorer.azure.com/dashboards/e8223032-9f30-427b-8f17-07c287223be1?p-_startTime=", StartTime,"&p-_endTime=", EndTime, "&p-_azsmClusterName=all&p-clusterName=v-", Tenant,"&p-tenantNameStr=all&p-_containerId=all&p-_roleInstanceName=all&p-hostNodeId=all&p-_resourceGroupName=all&p-_SubscriptionId=all#f467fefa-0fdb-4d57-86e0-647570db312c") 
| project StartTime, EndTime, GroupBy = Tenant, Content = RoleInstanceName, dashBoardUrl, RCAInvestigation
```

**Params:** `{queryFrom}`, `{queryTo}`, `{subId}`, `{rgName}`, `{resName}`

---
