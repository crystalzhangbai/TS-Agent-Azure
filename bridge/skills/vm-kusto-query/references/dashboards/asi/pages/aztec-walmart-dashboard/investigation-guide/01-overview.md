# Overview

> Source: **Aztec Walmart Dashboard Investigation Guide** dashboard, chapter **Overview** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Failure Trend

### Exceptions

_Widget purpose:_ Failure Trend

Cluster: `azurecm` · Database: `AzureCM` · Type: `TimeSeries`
Source panel: `Overview > Failure Trend`

```kusto
let SubscriptionFilter = iff(local_subscriptionId!= "", true, false);
let A = cluster('azcrpeus.kusto.windows.net').database('CommonDims').Dim_Subscription
| where  FriendlySubscriptionName contains "walmart" or TPName contains "walmart"
| where SubscriptionGuid == local_subscriptionId
| project SubscriptionGuid;
let B =  cluster('azcrpeus.kusto.windows.net').database('CommonDims').Dim_Subscription
| where  FriendlySubscriptionName contains "walmart" or TPName contains "walmart"
| project SubscriptionGuid;
let funcA = view(){
        A
    };
let funcB= view(){
        B
    };
let walmartSubs = union (funcA() | where SubscriptionFilter), (funcB() | where not(SubscriptionFilter));
let fabricatorImpactedOperations = 
 cluster('azcrp.kusto.windows.net').database('crp_allprod').VMApiQosEvent
    | where PreciseTimeStamp between(startTime..endTime)
    and MonitoringApplication !contains 'Validation' and resultType == 2
                and fabricCluster has '-prod-'
                and resultCode in ('AllocationFailed','InternalExecutionError')
                |project fabricCluster,operationId,fabricTenantName
                |join kind=inner 
                (
                    cluster('accp.centralus.kusto.windows.net').database('AZSM').AzSMQoSEvents
                    |where PreciseTimeStamp between(startTime..endTime)  and result != 'Success' and operation in ('SaveTenantGoalStateAsync','DeleteTenantAsync','StopTenantAsync')
                    and exceptionType == 'System.ServiceModel.FaultException`1[Microsoft.Windows.Azure.Fabric.Cfx.Contracts.Faults.ServiceUnavailableFault]'
                    |project Cluster,tenantName
                ) on $left.fabricCluster==$right.Cluster and $left.fabricTenantName== $right.tenantName
                |distinct operationId;
let overallwithoutExceptionQos = cluster('azcrp.kusto.windows.net').database('crp_allprod').VMApiQosEvent
    | where PreciseTimeStamp between(startTime..endTime)
    and MonitoringApplication !contains 'Validation'
                 and resultType == 2
                and isnotempty(fabricCluster)
    | where subscriptionId in (walmartSubs)
              |extend isAzSM = fabricCluster has '-prod-'
              |extend isFabricatorDown=operationId in (fabricatorImpactedOperations)
              |parse MonitoringApplication with * 'CRP-' Region '_Monitoring'
              |where isnotempty(Region)
              |parse errorDetails with * 'One or more errors occurred. ---> ' Exception ':' *;
let overallQos = AzSMErrorClassification(overallwithoutExceptionQos);
let userVisibleQos = overallQos | where operationName !startswith 'Subscriptions.'
    and      operationName !startswith 'FabricCallback' and operationName != 'AsyncOperationCallbackOperation' and
              operationName !startswith 'VMMeteringData' and operationName != 'VMScaleSetCleanupInternalOperation' and
              operationName !startswith 'Backup.' and operationName  !contains 'VMConsole' and
              operationName !startswith 'GeoConfig' and operationName !startswith 'KvsData' and 
              operationName !startswith 'SystemInfo' and 
              operationName != 'RestorePoints.RetrieveSasUris.POST' and            // used only by the Backup service 
              operationName != 'RestorePointCollections.ResourceOperation.GET' and //
              operationName != 'RestorePoints.RestorePointOperation.GET' and       //
              operationName !startswith 'CustomerSupport' and operationName !startswith 'Configuration' and
              operationName != 'VirtualMachineScaleSets.migrationInfo.GET';
let userVisibleQosExceptions = userVisibleQos | project PreciseTimeStamp, Region,isAzSM,resultCode,exceptionType,exceptionDetails,errorDetails, Category='User Visible',isComputeManagerIssue, fabricCluster, fabricTenantName, operationName, operationId, resultType;
userVisibleQosExceptions
| where isComputeManagerIssue == true
| project PreciseTimeStamp, Region, resultCode, exceptionType, errorDetails =substring(errorDetails, 0, 2500), fabricCluster, fabricTenantName, operationId, operationName
| summarize count() by  bin (PreciseTimeStamp, 1hr), exceptionType
| render linechart
```

**Params:** `{startTime}`, `{endTime}`, `{local_subscriptionId}`

**Signal filters seen in KQL:** `FriendlySubscriptionName contains "walmart"`

---
