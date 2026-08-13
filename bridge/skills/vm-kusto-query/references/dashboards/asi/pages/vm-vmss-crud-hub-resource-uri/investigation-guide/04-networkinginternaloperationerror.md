# NetworkingInternalOperationError

> Source: **Resource URI** dashboard, chapter **NetworkingInternalOperationError** (3 queries across 3 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### statemachinevents

Cluster: `azcore.centralus` · Database: `Crp` · Type: `Table`
Source panel: `NetworkingInternalOperationError`

```kusto
let startTime = queryFrom;
let endTime = queryTo;
//Do not edit below this line
let FRIC_RELEASE_TIME_LIMIT = 15m; 
let CONTAINER_DESTROY_TIME_LIMIT = 15m;
let CrpOp = materialize(
    macro-expand isfuzzy=true entity_group [cluster('azcore.centralus.kusto.windows.net')] as X(
        X.database('Crp').ApiQosEvent
            | where PreciseTimeStamp between(startTime..endTime)
                and subscriptionId == subid
                and resourceGroupName =~ rgName
                and resourceName =~ resName
                and resultCode == 'NetworkingInternalOperationError'
            |extend extractCode = iif(errorDetails has 'Code: ', extract('Code: (.*)', 1, tostring(errorDetails)), '')
            | extend NRPerrortype = case (
                        extractCode in ("RnmServiceDeletionCleanupTimeout","RnmServiceInstanceCleanupTimeout"), 'FricReleaseIssue', //FRIC release issues
                            'NotComputeToBlame')
            )
        | project PreciseTimeStamp, NRPerrortype , errorDetails //, operationName, resultCode, requestEntity - will need it only when testing the query
        | top 1 by PreciseTimeStamp asc
);
let FricReleaseIssue =materialize( 
    CrpOp  
        | where NRPerrortype != 'NotComputeToBlame'
        | extend 
            extractedTenantName = iif(errorDetails has 'serviceId: ', extract('serviceId: (.*?),', 1, tostring(errorDetails)),''),
            extractedDeletedTime = iif(errorDetails has 'DeletedDateTime: ', extract('DeletedDateTime: (.*?) IsCleanupPendingInTM',1, tostring(errorDetails)),''),
            extractedFabricId = tolower(iif(errorDetails has 'FabricId: ', extract('FabricId: (.*?) PendingDeleteInFabric',1, tostring(errorDetails)),'')),
            extractedRoleInstanceName = iff(isempty(toupper(extract("Name: (.*?) ", 1, tostring(errorDetails)))),strcat("_",toupper(resName)),toupper(extract("Name: (.*?) ", 1,tostring(errorDetails)))),
            isCleanupPendingInTM = iff(errorDetails has "IsCleanupPendingInTM: True" , true, false),
            isPendingDeleteInFa = iff(errorDetails has "PendingDeleteInFabric: True", true, false),
            extractedNetworkServiceInstanceId = iif(errorDetails has "NetworkServiceInstanceId: ", extract('NetworkServiceInstanceId: ([a-fA-F0-9]{8}[-]?([a-fA-F0-9]{4}[-]?){3}[a-fA-F0-9]{12})', 1, tostring(errorDetails)),'') 
            //We have the scenario where the vip is stuck associated with a ghost tenant so this helps to confirm
        | extend extractedVipReleasePending = iff(errorDetails contains "VipReleasePendingInRnmBeforeNsmQuery",true,false)
        | extend extractedVipReleasePendingNsm = iff( errorDetails contains 'VipReleasePendingInNsmPlus',true,false)
        // We just want to focus on the scenario where RNM/NSM blames Compute
        | where isCleanupPendingInTM or isPendingDeleteInFa
);
let nsId = toscalar(FricReleaseIssue | project extractedNetworkServiceInstanceId);
let StartRNMcheck = todatetime(toscalar(FricReleaseIssue | project extractedDeletedTime));
let tenantNameFromCrP=(FricReleaseIssue | project extractedTenantName);
//Check Rnm Release notification state
FricReleaseIssue
    | join kind = leftouter (
        macro-expand isfuzzy=false entity_group [cluster('azcore.centralus.kusto.windows.net')] as X(
            X.database("AzureCP").AzSMTenantStatemachineEvents
            | where PreciseTimeStamp between(todatetime(StartRNMcheck) ..now())
                and tenantName in (tenantNameFromCrP) and isnotempty(tenantName)
                | project PreciseTimeStamp, tenantName , stateMachineId , stateMachineState , message 
                | where * contains "rnm"
        )
    ) on $left.extractedTenantName==$right.tenantName
    | project PreciseTimeStamp, tenantName, stateMachineId, stateMachineState, message
```

**Params:** `{queryFrom}`, `{queryTo}`, `{subid}`, `{rgName}`, `{resName}`

**Signal filters seen in KQL:** `NRPerrortype != "NotComputeToBlame"`

---

## Automated query

### NIOE

_Widget purpose:_ Automated query

Cluster: `azcore.centralus` · Database: `Crp` · Type: `Single` · Widget: `Card`
Source panel: `NetworkingInternalOperationError > Automated query`

```kusto
let startTime = queryFrom;
let endTime = queryTo;
//Do not edit below this line
let FRIC_RELEASE_TIME_LIMIT = 15m; 
let CONTAINER_DESTROY_TIME_LIMIT = 15m;
let CrpOp = materialize(
    macro-expand isfuzzy=true entity_group [cluster('azcore.centralus.kusto.windows.net')] as X(
        X.database('Crp').ApiQosEvent
            | where PreciseTimeStamp between(startTime..endTime)
                and subscriptionId == subid
                and resourceGroupName =~ rgName
                and (resourceName =~resName or split( resourceName,"/")[0]=~ resName)
                and resultCode == 'NetworkingInternalOperationError'
            |extend extractCode = iif(errorDetails has 'Code: ', extract('Code: (.*)', 1, tostring(errorDetails)), '')
            | extend NRPerrortype = case (
                        extractCode in ("RnmServiceDeletionCleanupTimeout","RnmServiceInstanceCleanupTimeout"), 'FricReleaseIssue', //FRIC release issues
                            'NotComputeToBlame')
            )
        | project PreciseTimeStamp, NRPerrortype , errorDetails //, operationName, resultCode, requestEntity - will need it only when testing the query
        | top 1 by PreciseTimeStamp asc
);
let FricReleaseIssue =materialize( 
    CrpOp  
        | where NRPerrortype != 'NotComputeToBlame'
        | extend 
            extractedTenantName = iif(errorDetails has 'serviceId: ', extract('serviceId: (.*?),', 1, tostring(errorDetails)),''),
            extractedDeletedTime = iif(errorDetails has 'DeletedDateTime: ', extract('DeletedDateTime: (.*?) IsCleanupPendingInTM',1, tostring(errorDetails)),''),
            extractedFabricId = tolower(iif(errorDetails has 'FabricId: ', extract('FabricId: (.*?) PendingDeleteInFabric',1, tostring(errorDetails)),'')),
            extractedRoleInstanceName = iff(isempty(toupper(extract("Name: (.*?) ", 1, tostring(errorDetails)))),strcat("_",toupper(resName)),toupper(extract("Name: (.*?) ", 1,tostring(errorDetails)))),
            isCleanupPendingInTM = iff(errorDetails has "IsCleanupPendingInTM: True" , true, false),
            isPendingDeleteInFa = iff(errorDetails has "PendingDeleteInFabric: True", true, false),
            extractedNetworkServiceInstanceId = iif(errorDetails has "NetworkServiceInstanceId: ", extract('NetworkServiceInstanceId: ([a-fA-F0-9]{8}[-]?([a-fA-F0-9]{4}[-]?){3}[a-fA-F0-9]{12})', 1, tostring(errorDetails)),'') 
            //We have the scenario where the vip is stuck associated with a ghost tenant so this helps to confirm
        | extend extractedVipReleasePending = iff(errorDetails contains "VipReleasePendingInRnmBeforeNsmQuery",true,false)
        // We just want to focus on the scenario where RNM/NSM blames Compute
        | where isCleanupPendingInTM or isPendingDeleteInFa
);
let NotComputetoBlame = CrpOp| extend result=iff(NRPerrortype == "NotComputeToBlame",true,false)|project result, errorDetails;
let nsId = toscalar(FricReleaseIssue | project extractedNetworkServiceInstanceId);
let StartRNMcheck = todatetime(toscalar(FricReleaseIssue | project extractedDeletedTime));
let tenantNameFromCrP=(FricReleaseIssue | project extractedTenantName);
let CheckRnmContainerState = (
//Check Rnm Release notification state
    FricReleaseIssue
    | join kind = leftouter (
        macro-expand isfuzzy=false entity_group [cluster('azcore.centralus.kusto.windows.net')] as X(
            X.database("AzureCP").RnmOperationEvents
            | where PreciseTimeStamp between(todatetime(StartRNMcheck) ..now())
                and tenantName in (tenantNameFromCrP) and isnotempty(tenantName)
            | project RnmPreciseTimeStamp=PreciseTimeStamp, Cluster, EventMessage, tenantName
            | extend EventMessage = array_slice(extract_all("(.*?)\\r\\n", EventMessage), 1, -1),
                errorexists = iif(EventMessage contains 'Exception',strcat('Yes.','\n', 'Exception: ',extract("Exception:\\s(.*)", 1, tostring(EventMessage))),'No')
            | mv-expand EventMessage
            | extend
                NetworkServiceId = iff(isempty(nsId),'', extract('NetworkServiceInstanceId: ([a-fA-F0-9]{8}[-]?([a-fA-F0-9]{4}[-]?){3}[a-fA-F0-9]{12})', 1, tostring(EventMessage))),
                RoleInstanceName = toupper(extract("RoleInstanceName: (.*?),", 1, tostring(EventMessage))),
                State = extract("State: (.*?),", 1, tostring(EventMessage)),
                Fabric = extract("FabricId: (.*?),", 1, tostring(EventMessage))
            | project-away EventMessage
        )
    | summarize arg_min(RnmPreciseTimeStamp, *) by RoleInstanceName,NetworkServiceId,State,Fabric
    ) on $left.extractedRoleInstanceName == $right.RoleInstanceName and  $left.extractedNetworkServiceInstanceId == $right.NetworkServiceId and $left.extractedFabricId==$right.Fabric
        | extend TimeToRelease = iff(State == 'Released'and NetworkServiceId =~ nsId and errorexists=='No' , RnmPreciseTimeStamp-StartRNMcheck, todynamic("")) 
        | extend RnmState = case(
                                State == 'Released' and TimeToRelease < FRIC_RELEASE_TIME_LIMIT and errorexists=='No' , "ReleasedTimely",
                                State == 'Released' and TimeToRelease >= FRIC_RELEASE_TIME_LIMIT and errorexists=='No', "ReleasedNotTimely",
                                isempty(State) and todatetime(StartRNMcheck) < ago(30d),"DataRolledOut",
                                "NotReleased"
                                )
        | top 1 by RnmPreciseTimeStamp desc 
); 
//To understand if the Container still exists or not - this helps to understand on scenarios where the data has rolledout
let ContainerData=cluster('Azurecm').database('azurecm').LogContainerSnapshot
            | where PreciseTimeStamp between(StartRNMcheck-1h..now())
                and tenantName  in (tenantNameFromCrP)
                and roleInstanceName   in~ (FricReleaseIssue | project extractedRoleInstanceName)
                and isnotempty(tenantName) 
                and todatetime(creationTime) < todatetime(StartRNMcheck)
            | project containerId;        
let ContainerState = CheckRnmContainerState
| join kind = leftouter(  
        cluster('Azurecm').database('azurecm').LogContainerHealthSnapshot
                | where PreciseTimeStamp between(StartRNMcheck..now())
                    and tenantName  in (tenantNameFromCrP)
                    and isnotempty(tenantName) 
       | summarize ToBeDestroyedOnNodeTime=minif(PreciseTimeStamp, containerLifecycleState  =~ "ToBeDestroyedOnNode"), DestroyedTime=minif(PreciseTimeStamp, containerLifecycleState =~ "Destroyed" or (containerLifecycleState =~ "Suspended" and containerState =~ "ContainerStateDestroyed")) by containerId, RoleInstanceName=toupper(roleInstanceName), tenantName
   // | extend RoleInstanceName = toupper(roleInstanceName)
    ) on $left.extractedRoleInstanceName == $right.RoleInstanceName      
   | where containerId in (toscalar(ContainerData))
    | extend TimeToDestroyContainer = iif(isempty(ToBeDestroyedOnNodeTime) and isnotempty(DestroyedTime),timespan(null),DestroyedTime-ToBeDestroyedOnNodeTime )
   | extend ContainerDestroyState = case (        
                                             totimespan(TimeToDestroyContainer) < CONTAINER_DESTROY_TIME_LIMIT, "DestroyedTimely",
                                             totimespan(TimeToDestroyContainer) >= CONTAINER_DESTROY_TIME_LIMIT, "DestroyedNotTimely",
                                             ((toscalar(ContainerData|count)) < 1 and isnotempty(DestroyedTime)) ,"Destroyed",
                                             "NotDestroyed"
)
    ;
 //  To get the vip and the exact tenantName to whom the vip is associated with
let vipReleasePendingIssue = ContainerState
    | extend vip = iif(errorDetails has 'FabricId: ', extract('IPAddress: (.*?) RevertPendingInFabric',1, tostring(errorDetails)), '')
    | join kind=leftouter(
        macro-expand isfuzzy=false entity_group [cluster('azcore.centralus.kusto.windows.net')] as X (
            X.database('Fc').LogTenantSnapshot
                | where PreciseTimeStamp  > ago(3h)
                |  project-rename vipTenantName=tenantName
                | distinct Tenant=tolower(Tenant), vips, vipTenantName)
                | extend extractedVipReleasePending=true//regardless of the fact that they are the same or not, we always want this variable as true on this request
    ) on $left.extractedFabricId==$right.Tenant and $left.vip==$right.vips and extractedVipReleasePending
       | top 1 by PreciseTimeStamp asc;
let TenantStateinFabric = toscalar( 
        macro-expand isfuzzy=false entity_group [cluster('azcore.centralus.kusto.windows.net')] as X (
            union X.database('Fc').LogTenantSnapshot ,X.database('AzureCP').AzSMTenantSnapshotV2
            | where PreciseTimeStamp > ago(3h)
            | where tenantName in (tenantNameFromCrP)  and isnotempty(tenantName) 
            | count
            | extend TenantStatus=case(
                                Count >0 ,'TenantStillExists',
                                toscalar(CrpOp | project NRPerrortype)!='FricReleaseIssue',''
                                ,'TenantisDestroyed')
            )
        | project TenantStatus
);////Make recommendations based on the current state.
let resultSet = (
      union vipReleasePendingIssue, NotComputetoBlame//);resultSet     
       | where (isnotempty(NRPerrortype) and isempty(result)) or (isempty(NRPerrortype) and result)
        | extend
             Recommendation = case(
                result, strcat("This Networking Internal Error is not associated with a FRIC release issue. Please review the error detail to further troubleshoot and work with Azure Networking Pod over a collaboration." , '\n' ,"Error Detail:  ", '\n' ,  errorDetails ),
                extractedVipReleasePending, strcat("It looks like vip: ", vips, " is still in use by another TenantName: ", vipTenantName, ". Please open IcM with 'Support/EEE Compute Manager' to assist with the vip release."),
                RnmState == "ReleasedTimely", strcat("The Rnm release notification was sent timely. A retry might resolve the issue, but if operations are still failing please engage 'Cloudnet/EEE Cloudnet'."),
                RnmState == "ReleasedNotTimely" and ContainerDestroyState == "DestroyedTimely", strcat("The initial error was likely caused by delay in Rnm release for ", extractedRoleInstanceName, ". The Rnm release notification was sent at ", RnmPreciseTimeStamp, ". Retrying the operation will likely resolve the issue. If issue still persists, please review data collection steps of 'Engaging EEE ComputeManager' in http://aka.ms/CCSupNetworkingInternalError to troubleshoot."),  
                RnmState == "ReleasedNotTimely" and ContainerDestroyState == "DestroyedNotTimely", strcat("The initial error was likely caused by delay in container destroy for ", extractedRoleInstanceName, ". The container ", containerId, " is now destroyed and the Rnm release notification is sent. Retrying the operation will likely resolve the issue. If issue still presist, please follow please review data collection steps of 'Engaging EEE ComputeManager' to troubleshoot."),  
                RnmState == "ReleasedNotTimely" and ContainerDestroyState == "Destroyed", strcat ("There might have been a delay on the container destroy for ", extractedRoleInstanceName, ". The container ", containerId, " no longer reference the roleinstance so the ContainerId state needs to be reviewed. Please engage 'Support/EEE ComputeManager' after confirming the current status of the containerId and discussing with a TA."),
                RnmState ==  "NotReleased" and ContainerDestroyState in ("DestroyedNotTimely", "DestroyedTimely","Destroyed") and TenantStateinFabric == 'TenantStillExists' , strcat("The container ", containerId, " for ", extractedRoleInstanceName, " was destroyed at ", DestroyedTime, ", but the release notification is not yet sent. As the tenantName still exists, please open IcM with 'Support/EEE Compute Manager' after double checking the current status and discussing with a TA."),
                RnmState ==  "NotReleased" and ContainerDestroyState in ("DestroyedNotTimely", "DestroyedTimely","Destroyed") and TenantStateinFabric == 'TenantisDestroyed' , strcat("The container ", containerId, " for ", extractedRoleInstanceName, " was destroyed at ", DestroyedTime, " and the TenantName no longer exists. However the release notification was not yet sent. For mitigation, please open IcM with 'Support/EEE ComputeManager' after double checking the current status and discussing with a TA. Please make sure to confirm if customer wants a RCA as we still have data to perform investigation."),
                RnmState ==  "NotReleased" and ContainerDestroyState == "NotDestroyed" and TenantStateinFabric != 'TenantisDestroyed', strcat("The container ",  containerId, " is not yet destroyed. Please follow step 5 in http://aka.ms/CCSupNetworkingInternalError to identify if there may be Service Healing or other node issues. If it has been less than an hour since the initial failure, please wait for some time and retry. If it has been more than an hour and no Service Healthing or node issues are identified, please open IcM with 'Support/EEE RDOS' after double checking the current status and discussing with a TA. The container was set to be destroyed since: ", ToBeDestroyedOnNodeTime),
                RnmState == "NotReleased" and ContainerDestroyState == "NotDestroyed" and TenantStateinFabric == 'TenantisDestroyed' , strcat("The container ", containerId, " for ", extractedRoleInstanceName, " is in a orphan state (Tenant has been destroyed however container still appears in the node). Please engage 'Support/EEE ComputeManager' after double checking the current status and discussing with a TA."),
                RnmState == "DataRolledOut" and  ContainerDestroyState in ("DestroyedNotTimely", "DestroyedTimely","Destroyed")  and TenantStateinFabric == 'TenantisDestroyed' , strcat ("The tenant has been destroyed however the logs have rolled over to provide a RCA, please open IcM with 'Support/EEE ComputeManager' after double checking the current status and discussing with a TA."),
               RnmState == "DataRolledOut" and TenantStateinFabric == 'TenantStillExists' , strcat ("The tenant looks to still exist however the logs have rolled over to provide a RCA, please open IcM with 'Support/EEE Compute Manager' after double checking the current status and discussing with a TA."),
               "We are unable to auto detect the status. It's possible that this query didn't capture the start of the issue, please adjust the start and end time to cover larger timespan to ensure accurate result. If adjusting the timespan still doesn't give you results, please manual investigation steps in the TSG to troubleshoot further.")
);
resultSet
| project  Recommendation, extractedRoleInstanceName, extractedTenantName,extractedNetworkServiceInstanceId, extractedFabricId, DeletedDateTime=StartRNMcheck, WasFRICsentButExceptionOccured=errorexists ,RnmState, TimeToRelease, containerId, ContainerDestroyState, TimeToDestroyContainer, DestroyedTime, TenantStateinFabric
```

**Params:** `{queryFrom}`, `{queryTo}`, `{subid}`, `{rgName}`, `{resName}`

**Signal filters seen in KQL:** `NRPerrortype != "NotComputeToBlame"`

---

## RNM release notification

### RnmOperationEvents

_Widget purpose:_ RNM release notification

Cluster: `azcore.centralus` · Database: `Crp` · Type: `Table`
Source panel: `NetworkingInternalOperationError > RNM release notification`

```kusto
let startTime = queryFrom;
let endTime = queryTo;
//Do not edit below this line
let FRIC_RELEASE_TIME_LIMIT = 15m; 
let CONTAINER_DESTROY_TIME_LIMIT = 15m;
let CrpOp = materialize(
    macro-expand isfuzzy=true entity_group [cluster('azcore.centralus.kusto.windows.net')] as X(
        X.database('Crp').ApiQosEvent
            | where PreciseTimeStamp between(startTime..endTime)
                and subscriptionId == subid
                and resourceGroupName =~ rgName
                and resourceName =~ resName
                and resultCode == 'NetworkingInternalOperationError'
            |extend extractCode = iif(errorDetails has 'Code: ', extract('Code: (.*)', 1, tostring(errorDetails)), '')
            | extend NRPerrortype = case (
                        extractCode in ("RnmServiceDeletionCleanupTimeout","RnmServiceInstanceCleanupTimeout"), 'FricReleaseIssue', //FRIC release issues
                            'NotComputeToBlame')
            )
        | project PreciseTimeStamp, NRPerrortype , errorDetails //, operationName, resultCode, requestEntity - will need it only when testing the query
        | top 1 by PreciseTimeStamp asc
);
let FricReleaseIssue =materialize( 
    CrpOp  
        | where NRPerrortype != 'NotComputeToBlame'
        | extend 
            extractedTenantName = iif(errorDetails has 'serviceId: ', extract('serviceId: (.*?),', 1, tostring(errorDetails)),''),
            extractedDeletedTime = iif(errorDetails has 'DeletedDateTime: ', extract('DeletedDateTime: (.*?) IsCleanupPendingInTM',1, tostring(errorDetails)),''),
            extractedFabricId = tolower(iif(errorDetails has 'FabricId: ', extract('FabricId: (.*?) PendingDeleteInFabric',1, tostring(errorDetails)),'')),
            extractedRoleInstanceName = iff(isempty(toupper(extract("Name: (.*?) ", 1, tostring(errorDetails)))),strcat("_",toupper(resName)),toupper(extract("Name: (.*?) ", 1,tostring(errorDetails)))),
            isCleanupPendingInTM = iff(errorDetails has "IsCleanupPendingInTM: True" , true, false),
            isPendingDeleteInFa = iff(errorDetails has "PendingDeleteInFabric: True", true, false),
            extractedNetworkServiceInstanceId = iif(errorDetails has "NetworkServiceInstanceId: ", extract('NetworkServiceInstanceId: ([a-fA-F0-9]{8}[-]?([a-fA-F0-9]{4}[-]?){3}[a-fA-F0-9]{12})', 1, tostring(errorDetails)),'') 
            //We have the scenario where the vip is stuck associated with a ghost tenant so this helps to confirm
        | extend extractedVipReleasePending = iff(errorDetails contains "VipReleasePendingInRnmBeforeNsmQuery",true,false)
        | extend extractedVipReleasePendingNsm = iff( errorDetails contains 'VipReleasePendingInNsmPlus',true,false)
        // We just want to focus on the scenario where RNM/NSM blames Compute
        | where isCleanupPendingInTM or isPendingDeleteInFa
);
let nsId = toscalar(FricReleaseIssue | project extractedNetworkServiceInstanceId);
let StartRNMcheck = todatetime(toscalar(FricReleaseIssue | project extractedDeletedTime));
let tenantNameFromCrP=(FricReleaseIssue | project extractedTenantName);
//Check Rnm Release notification state
FricReleaseIssue
    | join kind = leftouter (
        macro-expand isfuzzy=false entity_group [cluster('azcore.centralus.kusto.windows.net')] as X(
            X.database("AzureCP").RnmOperationEvents
            | where PreciseTimeStamp between(todatetime(StartRNMcheck) ..now())
                and tenantName in (tenantNameFromCrP) and isnotempty(tenantName)
            | project RnmPreciseTimeStamp=PreciseTimeStamp, Cluster, EventMessage, tenantName
            | extend EventMessage = array_slice(extract_all("(.*?)\\r\\n", EventMessage), 1, -1),
                errorexists = iif(EventMessage contains 'Exception',strcat('Yes.','\n', 'Exception: ',extract("Exception:\\s(.*)", 1, tostring(EventMessage))),'No')
            | mv-expand EventMessage
            | extend
                NetworkServiceId = iff(isempty(nsId),'', extract('NetworkServiceInstanceId: ([a-fA-F0-9]{8}[-]?([a-fA-F0-9]{4}[-]?){3}[a-fA-F0-9]{12})', 1, tostring(EventMessage))),
                RoleInstanceName = toupper(extract("RoleInstanceName: (.*?),", 1, tostring(EventMessage))),
                State = extract("State: (.*?),", 1, tostring(EventMessage)),
                Fabric = extract("FabricId: (.*?),", 1, tostring(EventMessage))
        )
    | summarize arg_min(RnmPreciseTimeStamp, *) by RoleInstanceName,NetworkServiceId,State, Fabric
    ) on $left.extractedRoleInstanceName == $right.RoleInstanceName and  $left.extractedNetworkServiceInstanceId == $right.NetworkServiceId and $left.extractedFabricId==$right.Fabric
    | project RnmPreciseTimeStamp, extractedDeletedTime, extractedFabricId, extractedNetworkServiceInstanceId, extractedTenantName, State, EventMessage
```

**Params:** `{queryFrom}`, `{queryTo}`, `{subid}`, `{rgName}`, `{resName}`

**Signal filters seen in KQL:** `NRPerrortype != "NotComputeToBlame"`

---
