# (top-level)

> Source: **CRP OperationId Investigation Guide** dashboard, chapter **(top-level)** (3 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Operation Id"

_Widget purpose:_ Operation Name: {{operationName}}, OperationId {{operationId}} 

Cluster: `azcrp` · Database: `crp_allprod` · Type: `ResourceGet` · Widget: `Container`

```kusto
let operationStartTime = datetime_add("day", -1, local_startDate);
let operationEndTime = datetime_add("day", 1, local_endDate);
ApiQosEvent
//| where PreciseTimeStamp between (operationStartTime..operationEndTime)
| where operationId =~ local_operationId
| extend backup_region = region
| invoke QosToContext()
| extend requestEntityDynamic = parse_json(requestEntity)
| extend resultType = case(resultType == 0, "Success", 
                       resultType == 1, "Client Failure", 
                       resultType == 2, "Server Failure",
                       "Unknown")
| extend startTime = datetime_add('millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp)
| extend opStartTime = floor(startTime, 1m)
| extend endTime = PreciseTimeStamp
| extend opEndTime = floor(PreciseTimeStamp, 1m) + 1m
| extend e2eMin = ceiling((e2EDurationInMilliseconds/1000/60.0))
| extend jarvisQueryTimeOffset = -(e2eMin + 1)
| extend jarvisQueryTime = strcat(format_datetime(PreciseTimeStamp, 'yyyy-MM-dd') , 'T', format_datetime(datetime_add("minute", 1, PreciseTimeStamp), 'hh:mm'), "Z")
| project MonitoringApplication
  , Node
  , apiVersion
  , clientApplicationId
  , clientPrincipalName
  , correlationId
  , durationInMilliseconds
  , e2EDurationInMilliseconds
  , errorDetails
  , exceptionType
  , jarvisContextActivityLink
  , httpStatusCode
  , goalSeekingActivityId
  , operationId
  , operationName
  , partitionId
  , PreciseTimeStamp
  , region = backup_region
  , requestEntityDynamic
  , resourceGroupName
  , resourceName
  , resultType 
  , resultCode
  , serviceBuild
  , subscriptionId
  , userAgent
  , startTime
  , endTime
  , e2eMin
  , opStartTime
  , opEndTime
  , jarvisQueryTimeOffset
  , jarvisQueryTime
```

**Params:** `{globalFrom}`, `{globalTo}`, `{local_endDate}`, `{local_operationId}`, `{local_startDate}`

---

### CSS Insight for NetworkingInternalOperation

Cluster: `azcrp` · Database: `crp_allprod` · Type: `IssueDetector`

```kusto
let FRIC_RELEASE_TIME_LIMIT = 15; 
let CONTAINER_DESTROY_TIME_LIMIT = 15m;
let resultSet = materialize(cluster('Azcrp').database('crp_allprod').ApiQosEvent_nonGet
| where PreciseTimeStamp between(startTime..endTime)
| where operationId == queryOperationId
| where resultCode == 'NetworkingInternalOperationError'
| extend StartTime = datetime_add("Millisecond", -e2EDurationInMilliseconds, PreciseTimeStamp) // Start of CRP operation
| extend extractedTenantName = iif(errorDetails has 'serviceId: ', substring(errorDetails, indexof(errorDetails, 'serviceId: ') + strlen('serviceId: '), 36), '')
| extend isCleanupPendingInTM = iff(errorDetails has "IsCleanupPendingInTM: True", true, false)
| extend isCloudNet = not(isCleanupPendingInTM) // Cleanup Pending in TM = false
| extend extractedRoleInstanceName = tostring(split(split(errorDetails, 'Name: ', 1)[0], ' ', 0)[0])
| extend isNotNrpInternalException = iif(errorDetails !has 'NrpInternalException: TenantManager did not finish deleting resources serviceId', true, false)
| join kind = leftouter // Unfortunately i dont know if we have a way to pass in the role instance name here, cannot rely on the one passed by the insight as the VM with the FRIC issues could be a diffent one.
(
    cluster('azcsupfollower.kusto.windows.net').database('AzureCM').RnmOperationEvents
    | where PreciseTimeStamp between(startTime..endTime)
    | where message has "State: Released" // we just need one row where the state is released - this will return for all VMs in that tenant, we need to verify the roleInstanceName below. 
    | extend isReleasedPreciseTimeStamp = PreciseTimeStamp
    | project isReleasedPreciseTimeStamp, message, tenantName
) on $left.extractedTenantName == $right.tenantName
| extend timeToRelease =   abs(datetime_diff("minute", isReleasedPreciseTimeStamp, startTime))
| extend isReleasedTimely = iff (message has extractedRoleInstanceName and (timeToRelease < FRIC_RELEASE_TIME_LIMIT), true, false)
| extend isCloudNet = isReleasedTimely // isReleasedTimely == true if we released in less than FRIC_RELEASE_TIME_LIMIT minutes
| join kind = leftouter // all roles inside that tenant, we will filter it out later see below
(
  cluster('azcsupfollower.kusto.windows.net').database('AzureCM').LogContainerHealthSnapshot
  | where PreciseTimeStamp between(startTime..endTime)
  | where containerLifecycleState in~ ("ToBeDestroyedOnNode", "Destroyed")
  | summarize minPreciseTimeStamp = min(PreciseTimeStamp), maxPreciseTimeStamp = max(PreciseTimeStamp) by tenantName, containerId, roleInstanceName
) on $left.extractedTenantName == $right.tenantName
| extend timetoDestroy = maxPreciseTimeStamp - minPreciseTimeStamp
| extend isContainerDestroyedTimely = iff (timetoDestroy < CONTAINER_DESTROY_TIME_LIMIT, true, false)
| extend isRdos = not(isContainerDestroyedTimely) and not(isempty(timetoDestroy)) and extractedRoleInstanceName has roleInstanceName
| extend cloudnetFRICReleasedIn = iff(isempty(timeToRelease), "NA", tostring(timeToRelease))
| extend computerManagerFRICReleasedIn = iff(isempty(timeToRelease), "NA", tostring(timeToRelease)), " ", extractedRoleInstanceName, " tenantName: ", extractedTenantName
| extend rdosGuidance = strcat("Container has been in ToBeDestroyedOnNode state for ", tostring(timetoDestroy), ", **roleInstanceName: ", roleInstanceName, "**, **containerId: **", containerId, "**. Please see Steps 3 and 4 of TSG: https://aka.ms/CCSupNetworkingInternalError")
| extend cloudnetGuidance = strcat("Suspected Regional Network Manager (RNM) issue. Please collaborate with the Networking POD and refer to the 'Which IcM team should I engage?' section in TSG https://aka.ms/CCSupNetworkingInternalError. IsPendingInTM is false and FRIC released in :", cloudnetFRICReleasedIn)
| extend computeManagerGuidance = strcat("FRIC release notification took a long time or isCleanupPendingInTM = true, refer to Step 2 in TSG: https://aka.ms/CCSupNetworkingInternalError FRIC release time (s):**", computerManagerFRICReleasedIn, "**")
| extend generalGuidance = "Found NetworkingInternalOperationError that was something other than a NrpInternalException. Refer to the TSG: https://aka.ms/CCSupNetworkingInternalError."
| extend recommendedAction = iif(isNotNrpInternalException, generalGuidance, iff(isRdos, rdosGuidance, iff(isCloudNet, cloudnetGuidance, computeManagerGuidance)))
| project recommendedAction, startTime, isRdos, isCloudNet, timetoDestroy, timeToRelease, containerId, extractedRoleInstanceName, roleInstanceName, extractedTenantName, isContainerDestroyedTimely, errorDetails);
let emptyRoleInstanceResult = resultSet | where roleInstanceName == "" | project recommendedAction; 
let notEmptyRoleInstanceResult = resultSet | where extractedRoleInstanceName has roleInstanceName | project recommendedAction;
let countofEmptyRoleInstanceResult = toscalar(emptyRoleInstanceResult | count);
let finalResult = iff (toscalar(emptyRoleInstanceResult | count) > 0 , toscalar(emptyRoleInstanceResult), toscalar(notEmptyRoleInstanceResult));
let extractedTenantName =  toscalar(resultSet | project extractedTenantName); 
print finalResult 
| project Severity = 'Error', 
  Uri = strcat('https://azureserviceinsights.trafficmanager.net/view/services/Aztec/pages/Tenants?tenantName=', extractedTenantName,
    '&globalFrom=',startTime ,'&globalTo=', endTime), 
    UriText = strcat('Check Tenant ', extractedTenantName, ' in ASI'), 
  Title =  "CSS Insight for NetworkingInternalOperation",
  Description  = print_0  
| where Description != ""
```

**Params:** `{startTime}`, `{endTime}`, `{queryOperationId}`

**Signal filters seen in KQL:** `resultCode == "NetworkingInternalOperationError"` · `message has "State: Released"`

---

### CSS Insight for WaitForOngoingAllocation

Cluster: `Azcrp` · Database: `crp_allprod` · Type: `IssueDetector`

```kusto
let UPDATE_TENANT_TIME_LIMIT = 30m; 
let operationDetails = VMApiQosEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where operationId == queryOperationId
| where resultCode == "InternalExecutionError"
| where exceptionType == "Microsoft.Windows.Azure.GCM.FabricInterface.OutOfTimeBudgetException"
| where errorDetails contains "WaitforOngoingAllocation"
| where isnotempty(fabricTenantName)
| top 1 by PreciseTimeStamp desc;
let targetTenantName  = toscalar(operationDetails | project fabricTenantName);
operationDetails | project tenantName = fabricTenantName 
| join kind = leftouter 
(
   cluster('accp.centralus.kusto.windows.net').database('AZSM').AzSMTenantEvents
   | where PreciseTimeStamp between ((queryFrom-45d) .. queryTo)
   | where tenantName =~ targetTenantName
   | where message has "Update is still in progress for UpdateTenant, tenant with id"
   | summarize latestUpdateTenantProgressEventDateTime = max(PreciseTimeStamp) by tenantName, message
) on tenantName  
| project-away tenantName1, message
| join kind = leftouter  
(
   cluster('azcsupfollower.kusto.windows.net').database('AzureCM').AzSMTenantEvents
   | where PreciseTimeStamp between ((queryFrom-45d) .. queryTo)
   | where tenantName =~ targetTenantName
   | where message has "Tenant updated successfully!"
   | summarize latestUpdateTenantCompletedEventDateTime = max(PreciseTimeStamp) by tenantName, message
) on tenantName  
| project-away tenantName1, message
| extend updateTenantDuration = latestUpdateTenantCompletedEventDateTime - latestUpdateTenantProgressEventDateTime
| extend isUpdateTenantOverTheLimit = iff (updateTenantDuration  > UPDATE_TENANT_TIME_LIMIT, true, false)
| extend isUpdateTenantCompleted = iff (latestUpdateTenantCompletedEventDateTime > latestUpdateTenantProgressEventDateTime, true, false) 
| extend recommendation = case (
        isUpdateTenantCompleted and isUpdateTenantOverTheLimit, "UpdateTenant took a long time to complete, need RCA , CX can retry", 
        isUpdateTenantCompleted == false, "Updatetenant not progressing need mitigation", 
        "All OK. CX can retry")
| project Description =  recommendation, Severity = "Warning"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryOperationId}`

**Signal filters seen in KQL:** `resultCode == "InternalExecutionError"` · `exceptionType == "Microsoft.Windows.Azure.GCM.FabricInterface.OutOfTimeBudgetException"` · `errorDetails contains "WaitforOngoingAllocation"` · `message has "Update is still in progress for UpdateTenant, tenant with id"` · `message has "Tenant updated successfully!"`

---
