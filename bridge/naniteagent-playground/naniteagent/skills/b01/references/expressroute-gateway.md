---
description: KQL queries for ER Gateway diagnostics: gateway health, tunnel status, connection drops, packet stats, BGP peers.
---

# ExpressRoute Gateway Kusto Queries

> Source: Azure Networking B01 Dashboard (aka.ms/b01)
> Pages: ER Gateway

## ER Gateway

### ExpressRoute Gateways Under Subscription(1 day delay)

```kql
//forpageview
let pv=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('kusto').adxpageview| where page contains "b01/exrgateway";
//forpageview
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let ShoeBoxMdm=materialize(cluster('AzureCM').database('AzureCM').LogClusterSnapshot 
| distinct Region, shoeboxMdmAccountName);
cluster('hybridnetworking').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 2d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayType == "Dedicated"
| distinct GatewayName,GatewayId, GatewayVmSize,VIPAddress, ProvisioningState,VNetName, VNetId, GatewayTenantVersion, GatewayType,Region,GatewayDeploymentType,AzureDeploymentVmSize, PhysicalZones
```

### Connected Circuits Per Gateway(1 day delay)

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let gwname = ErGwName;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let ShoeBoxMdm=materialize(cluster('AzureCM').database('AzureCM').LogClusterSnapshot 
| distinct Region, shoeboxMdmAccountName);
let gatewayvNetid = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct VNetId);
let skey=cluster('hybridnetworking').database('aznwmds').TunnelIntfTable   
| where PreciseTimeStamp > starttime - 1d and PreciseTimeStamp < endtime
| where VnetId in (gatewayvNetid)
| distinct ServiceKey;
cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp > starttime - 1d and PreciseTimeStamp < endtime
| where AzureServiceKey in (skey)
| distinct ServiceKey=AzureServiceKey, NRPResouceUri=NrpResourceUri, VrfNames=tostring(parse_xml(VrfIds)["ArrayOfString"]["string"]), DeviceName=strcat(PrimaryDeviceName,",", SecondaryDeviceName), ServiceProviderName
| extend ERCircuitsss=split(NRPResouceUri, "/")
| extend ERCircuitSubscription=ERCircuitsss[4]
| extend ERCircuitName=ERCircuitsss[10]
| extend ERCircuitTroubleshootingLink=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubscriptionID=v-",ERCircuitSubscription,"&p-ExpressRouteCircuitName=v-",ERCircuitName,"#d7150dfa-a8d2-438d-b97f-6de6b0da282c")
| project ERCircuitUri=NRPResouceUri, ServiceKey, DeviceName,ServiceProviderName, VrfNames,ERCircuitTroubleshootingLink
| join kind=leftouter (cluster("Hybridnetworking").database("aznwmds").VnetConfigTable | where PreciseTimeStamp > starttime -1d and PreciseTimeStamp < endtime) on ServiceKey 
| where VNetId in (gatewayvNetid)
| project   GatewayId, ERCircuitUri, ServiceKey,ServiceProviderName, Weight=RoutingWeight, FastPath=DirectTunnelsStatus, DeviceName, VrfNames,ERCircuitTroubleshootingLink
| distinct GatewayId, CircuitSubscriptionId=tostring(split(ERCircuitUri, "/")[4]),CircuitName=tostring(split(ERCircuitUri, "/")[10]), ServiceKey,ServiceProviderName, Weight, FastPath, DeviceName, VrfNames,ERCircuitTroubleshootingLink,ERCircuitUri
//let gatewayid = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
//| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
//| where CustomerSubscriptionId == subscriptionid
//| where GatewayName == gwname
//| distinct GatewayId);
//cluster('hybridnetworking').database('aznwmds').ERTunnelHealthTable    
//| where PreciseTimeStamp > starttime and PreciseTimeStamp < endtime
//| where GatewayId in (gatewayid)
//| distinct ServiceKey, NRPResouceUri, VrfName, GatewayId, DeviceName
////| summarize Vrfs=make_list(VrfName), DeviceName=make_list(DeviceName) by NRPResouceUri, GatewayId,ServiceKey
//| summarize Vrfs=tostring(make_list(VrfName)), DeviceName=tostring(make_list(DeviceName)) by NRPResouceUri, GatewayId,ServiceKey
//| extend ERCircuitsss=split(NRPResouceUri, "/")
//| extend  ERCircuitSubscription=ERCircuitsss[2]
//| extend ERCircuitName=ERCircuitsss[8]
//| extend ERCircuitTroubleshootingLink=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubscriptionID=v-",ERCircuitSubscription,"&p-ExpressRouteCircuitName=v-",ERCircuitName,"&p-SyslogFilter=all#d7150dfa-a8d2-438d-b97f-6de6b0da282c")
//| project   GatewayId, ERCircuitUri=NRPResouceUri, ServiceKey, DeviceName, Vrfs,ERCircuitTroubleshootingLink
//| join kind=leftouter (cluster("Hybridnetworking").database("aznwmds").VnetConfigTable | where PreciseTimeStamp > starttime -1d and PreciseTimeStamp < endtime) on ServiceKey and GatewayId
//| project   GatewayId, ERCircuitUri, ServiceKey,Weight=RoutingWeight, FastPath=DirectTunnelsStatus, DeviceName, Vrfs,ERCircuitTroubleshootingLink
//| distinct GatewayId, CircuitSubscriptionId=tostring(split(ERCircuitUri, "/")[2]),CircuitName=tostring(split(ERCircuitUri, "/")[8]), ServiceKey,Weight, FastPath, DeviceName, Vrfs,ERCircuitTroubleshootingLink,ERCircuitUri
```

### Gateway Instance Dashboard

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let gwname = ErGwName;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let ShoeBoxMdm=materialize(cluster('AzureCM').database('AzureCM').LogClusterSnapshot 
| distinct Region, shoeboxMdmAccountName);
let gatewayid = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct GatewayId);
let gatewaymaps = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct GatewayName,GatewayId);
cluster('hybridnetworking.kusto.windows.net').database('aznwmds').ErVpnGwToContainerId
| where PreciseTimeStamp >= starttime - 2h and PreciseTimeStamp <= endtime
| where GatewayId in (gatewayid)
| join kind=inner gatewaymaps on $left.GatewayId == $right.GatewayId
| distinct GatewayName, GatewayId, Region, Tenant=Cluster, RoleInstanceName, nodeId=toupper(NodeId), containerId=ContainerId, VMSize, DataCenterName, CA=tostring(CA), CAv6=tostring(CAv6)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on $left.nodeId == $right.NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| extend nodeId=tolower(nodeId)
| join kind=leftouter cluster('overlakedata.southcentralus.kusto.windows.net').database('overlake-syslog').OverlakeMapV2 on $left.nodeId == $right.NodeId
//| join kind=inner cluster('aznwsdn').database("aznwmds").MdmVfpVnetAccountMaps on $left.Tenant == $right.Cluster
| join kind=inner cluster("azurehn.kusto.windows.net").database("Azurehn").MdmVfpVnetAccountMaps() on $left.Tenant == $right.Cluster
| extend VFPDashBoard=strcat("https://portal.microsoftgeneva.com/dashboard/VfpMDM/dpop/SupportDashboard?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend VFPDropDashBoard=strcat("https://portal.microsoftgeneva.com/dashboard/VfpMDM/dpop/dropsDashboard?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend SupportDashBoard=strcat("https://portal.microsoftgeneva.com/s/54D24FEA?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend DropDashBoard=strcat("https://portal.microsoftgeneva.com/dashboard/VfpMDM/dpop/dropsDashboard?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend FPGADashboard=strcat("https://portal.microsoftgeneva.com/dashboard/VfpMDM/DatapathDashboards/FpgaDashboardGft/FpgaDashboardGftv3?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend InvestigateNode=strcat("https://dataexplorer.azure.com/dashboards/bea4ccac-baf1-45f3-b160-533232cbfdaa?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH-mm-ss'),"Z&p-_endTime=", format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime, 'HH-mm-ss'), "Z&p-_NodeId=v-", nodeId, "&p-_ContainerId=v-", containerId, "&p-_ICMId=all#2f4843e6-c1e5-4564-ad27-cde71cebc7c7")
| extend ASIHostNode=strcat("https://azureserviceinsights.trafficmanager.net/view/services/Azure%20Host/pages/Azure%20Host%20Node?nodeId=",tolower(nodeId),"&globalFrom=",format_datetime(starttime, 'yyyy-MM-dd'),"T",format_datetime(starttime, 'HH'), "%3A",format_datetime(starttime, 'mm'), "%3A51.000Z&globalTo=",format_datetime(endtime, 'yyyy-MM-dd'),"T",format_datetime(endtime, 'HH'), "%3A",format_datetime(endtime, 'mm'),"%3A51.000Z")
| extend NetVMA=strcat("https://aka.ms/netvma/?destValue=&pathQuery=false&sdnPath=false&showPingMesh=false&startTime=", format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'), "&endTime=", format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime, 'HH:mm:ss'), "&value=", containerId)
| extend PerVMAvailability=strcat("https://portal.microsoftgeneva.com/s/A03537E6?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VNETAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend PerProcessorPNICDashboard=strcat("https://portal.microsoftgeneva.com/dashboard/VfpMDM/DatapathDashboards/PerProcessorNdisDashboard?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend VFPFullRule=strcat("https://portal.microsoftgeneva.com/?page=actions&acisEndpoint=Public&managementOpen=false&automatedTestsReportOpen=false&tab=Extensions&acisRolloutEndpoint=Public&selectedNodeType=3&extension=SupportabilityFabric&group=Fabric%20Operations&operationId=GetVfpFiltersForContainer&operationName=Get%20VFP%20Filters%20(ACL%20and%20VNET)%20programmed%20on%20containers&inputMode=single&params={%22smefabrichostparam%22:%22", Cluster, "%22,%22smenodeidparam%22:%22", nodeId, "%22,%22smecontaineridparam%22:%22", containerId,"%22,%22smemacaddressparam%22:%22%22,%22smelayerparam%22:%22%22,%22smegroupparam%22:%22%22,%22smeruleparam%22:%22%22,%22smenatpoolparam%22:%22%22,%22smenatrangeparam%22:%22%22,%22smespaceparam%22:%22%22,%22smemappingparam%22:%22%22,%22smevfpfiltercommandparam%22:%22list-rule%22,%22smevfpfilteroptionsparam%22:%22%22}&actionEndpoint=Production&genevatraceguid=9964f627-a5ca-435a-a749-e60f4a56c7f0")
| extend ListUnifiedFlow=strcat("https://portal.microsoftgeneva.com/?page=actions&acisEndpoint=Public&managementOpen=false&automatedTestsReportOpen=false&tab=Extensions&acisRolloutEndpoint=Public&selectedNodeType=3&extension=SupportabilityFabric&group=Fabric%20Operations&operationId=GetVfpFiltersForContainer&operationName=Get%20VFP%20Filters%20(ACL%20and%20VNET)%20programmed%20on%20containers&inputMode=single&params={%22smefabrichostparam%22:%22", Cluster, "%22,%22smenodeidparam%22:%22", nodeId, "%22,%22smecontaineridparam%22:%22", containerId,"%22,%22smemacaddressparam%22:%22%22,%22smelayerparam%22:%22%22,%22smegroupparam%22:%22%22,%22smeruleparam%22:%22%22,%22smenatpoolparam%22:%22%22,%22smenatrangeparam%22:%22%22,%22smespaceparam%22:%22%22,%22smemappingparam%22:%22%22,%22smevfpfiltercommandparam%22:%22list-unified-flow%22,%22smevfpfilteroptionsparam%22:%22%22}&actionEndpoint=Production&genevatraceguid=9964f627-a5ca-435a-a749-e60f4a56c7f0")
//| distinct GatewayName, GatewayId, RoleInstanceName, VMSize,Region,DataCenterName, Cluster, nodeId, containerId, VFPDashBoard, VFPDropDashBoard, SupportDashBoard, DropDashBoard, FPGADashboard, InvestigateNode, ASIHostNode, NetVMA, PerVMAvailability, PerProcessorPNICDashboard,VFPFullRule, ListUnifiedFlow
| extend ProcessTupleOutbound=strcat("https://portal.microsoftgeneva.com/?page=actions&acisEndpoint=Public&managementOpen=false&automatedTestsReportOpen=false&tab=Extensions&acisRolloutEndpoint=Public&selectedNodeType=3&extension=SupportabilityFabric&group=Fabric%20Operations&operationId=GetVfpFiltersForContainer&operationName=Get%20VFP%20Filters%20(ACL%20and%20VNET)%20programmed%20on%20containers&inputMode=single&params={%22smefabrichostparam%22:%22", Cluster, "%22,%22smenodeidparam%22:%22", nodeId, "%22,%22smecontaineridparam%22:%22", containerId,"%22,%22smemacaddressparam%22:%22%22,%22smelayerparam%22:%22%22,%22smegroupparam%22:%22%22,%22smeruleparam%22:%22%22,%22smenatpoolparam%22:%22%22,%22smenatrangeparam%22:%22%22,%22smespaceparam%22:%22%22,%22smemappingparam%22:%22%22,%22smevfpfiltercommandparam%22:%22process-tuples%22,%22smevfpfilteroptionsparam%22:%22\\%226%20", CA, "%201234%208.8.8.8%20443%20out%201\\%22%22}&actionEndpoint=Production&genevatraceguid=6138abc0-1c93-4b03-bf62-a63eaa6d9ad2")
| join kind=leftouter (cluster('AzureCM').database('AzureCM').LogNodeSnapshot | where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime) on nodeId
| where EndPort != "N"
| distinct RoleInstanceName,CA, CAv6, VMSize,Region, DataCenterName,Cluster, ToR=EndDevice, ToRPort=EndPort, nodeId,ipAddress, containerId, SocNodeId, VFPDashBoard, VFPDropDashBoard, SupportDashBoard, DropDashBoard, FPGADashboard, InvestigateNode, ASIHostNode, NetVMA, PerVMAvailability, PerProcessorPNICDashboard,VFPFullRule, ListUnifiedFlow,ProcessTupleOutbound
| join kind=leftouter (cluster('AzureCM').database('AzureCM').LogContainerSnapshot | where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime) on containerId
| where ToRPort != "N"
| summarize T0=make_list(ToR) by RoleInstanceName,CA, CAv6, VMSize,Region, DataCenterName,tenantName,Cluster, nodeId, nodeipAddress=ipAddress, containerId, subscriptionId,SocNodeId,VFPDashBoard, VFPDropDashBoard, SupportDashBoard, DropDashBoard, FPGADashboard, InvestigateNode, ASIHostNode, NetVMA, PerVMAvailability, PerProcessorPNICDashboard,VFPFullRule, ListUnifiedFlow,ProcessTupleOutbound
| extend VMdash=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubIdOrContainerId=v-",containerId,"&&p-VMName=v-ContaizerId&p-DataPathScan=v-No#8ed1e2a2-d979-401b-9609-7580ad07ccd1")
| extend IsOverLake=iff(isempty(SocNodeId), "No", "Yes")
| distinct RoleInstanceName,CA, CAv6, VMSize,Region, DataCenterName,tenantName,Cluster, T0=tostring(T0), nodeId, nodeipAddress,IsOverLake, SocNodeId, containerId, subscriptionId,VMdash,  VFPDashBoard, VFPDropDashBoard, SupportDashBoard, DropDashBoard, FPGADashboard, InvestigateNode, ASIHostNode, NetVMA, PerVMAvailability, PerProcessorPNICDashboard,VFPFullRule, ListUnifiedFlow,ProcessTupleOutbound
| order  by RoleInstanceName asc


```

### MSEE-To-ER Gateway Configuration(1 day delay)

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let gwname = ErGwName;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let ShoeBoxMdm=materialize(cluster('AzureCM').database('AzureCM').LogClusterSnapshot 
| distinct Region, shoeboxMdmAccountName);
let gatewayvNetid = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct VNetId);
cluster('hybridnetworking').database('aznwmds').TunnelIntfTable   
| where PreciseTimeStamp > starttime - 2d and PreciseTimeStamp < endtime
| where VnetId in (gatewayvNetid)
| join kind=leftouter (cluster("Hybridnetworking").database("aznwmds").VnetConfigTable | where PreciseTimeStamp >= starttime - 2d and PreciseTimeStamp < endtime) on ServiceKey and $left.VnetId == $right.VNetId
| distinct ConnectionName=tostring(split(NrpResourceUri,"Microsoft.Network/connections/")[1]), GatewayId,ToCircuit=ServiceKey, DeviceName, MSEETunnelInterface=InterfaceName, tostring(GreKey),MSEETunnelInterfaceIP=IpAddress, TunnelSourceIP=SourceIp, TunnelDestinationIP=DestinationIp, Weight=RoutingWeight,FastPathStatus=DirectTunnelsStatus,PrivateLinkFastPath=EnablePrivateLinkFastPath,State, Description

```

### Gateway Configuration(1 day delay)

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let gwname = ErGwName;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let min = datetime_diff('minute',endtime,starttime);
let ShoeBoxMdm=materialize(cluster('AzureCM').database('AzureCM').LogClusterSnapshot 
| distinct Region, shoeboxMdmAccountName);
cluster('hybridnetworking').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayType == "Dedicated"
| where GatewayName == gwname //or GatewayId contains GatewayIds
//| where GatewayID contains GatewayID
| extend ErGwVMSS=iff(GatewayVmSize  contains "AZ", strcat("/subscriptions/", SubscriptionId, "/resourceGroups/armrg-", GatewayId, "/providers/Microsoft.Compute/virtualMachineScaleSets/ergw"), "N/A")
| extend ErGwELB=iff(GatewayVmSize  contains "AZ", strcat("/subscriptions/", SubscriptionId, "/resourceGroups/armrg-", GatewayId, "/providers/Microsoft.Network/loadBalancers/ergwLoadBalancer"), "N/A")
//| extend GatewayTenantLog=strcat("https://portal.microsoftgeneva.com/logs/dgrep?be=DGrep&time=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'), "Z&offset=", min, "&offsetUnit=Minutes&UTC=true&ep=Diagnostics%20PROD&ns=BrkGWT&en=GatewayTenantLogsTable&scopingConditions=[[%22Tenant%22,%22", GatewayId,"%22],[%22__Region__%22,%22","%22]]&conditions=[]&clientQuery=orderby%20preciseTimeStamp%20asc&chartEditorVisible=true&chartType=line&chartLayers=[[%22New%20Layer%22,%22%22]]%20")
| extend GatewayDashboard=strcat("https://portal.microsoftgeneva.com/s/3CBF8937?overrides=[{%22query%22:%22//widgets[guid=\\%226ab9c159-6f0a-4b0a-9606-fb10a2058280\\%22]//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22BrkProd%22},{%22query%22:%22//widgets[guid=\\%2282be34f0-284e-46e5-b5eb-dde75359fbb3\\%22]//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22BrkProd%22},{%22query%22:%22//widgets[guid=\\%227969f8a0-907b-4dd9-9151-9c08448f9ad6\\%22]//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22BrkProd%22},{%22query%22:%22//*[id='", GatewayId,"']%22,%22key%22:%22value%22,%22replacement%22:%22GatewayId%22},{%22query%22:%22//*[id='gatewayId']%22,%22key%22:%22value%22,%22replacement%22:%22",GatewayId,"%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| distinct GatewayName,GatewayId, GatewayVmSize,VIPAddress, PublicIpResourceUris,VNetName, VNetId, SubnetResourceUri,GatewayTenantVersion, GatewayType,Region,AzureDeploymentVmSize, PhysicalZones,CAs,SkipUpgradeProperties,ErGwELB,ErGwVMSS,GatewayDashboard
| evaluate narrow()
| project Type=Column, Value
```

### ER Gateway SLB Dashboard(1 minute delay) - Need to Figure Out why VWAN Gateway doesn't show

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let gwname = ErGwName;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let min = datetime_diff('minute',endtime,starttime);
let ErGwVIP=toscalar(cluster('hybridnetworking').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayType == "Dedicated"
| where GatewayName == gwname
| distinct VIP=VIPAddress);
cluster('azslb').database('azslbmds').VipMetadataSnapshotRecord
| where env_time > starttime - 6h and env_time < endtime + 1h
| where Vip == ErGwVIP
| summarize by Vip, VipUri, Type, SKU, AltAddress, VmLocs, CountHosts, env_cloud_role, Region
| join (cluster('azslb').database('azslbmds').SlbMetadataVersionRecord
| where env_time > starttime - 1h and env_time < endtime + 1h
|summarize by Region, MdmAccountName, ArmRegion
| extend HPAccountName = strcat("slbhp", substring(MdmAccountName, 5))) on $left.Region == $right.Region
| extend BandwithUsage=strcat("https://portal.microsoftgeneva.com/dashboard/slbv2prod/AzureMonitor/BandwidthUsage?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22slbhp", ArmRegion,"%22},{%22query%22:%22//*[id='VipAddress']%22,%22key%22:%22value%22,%22replacement%22:%22",ErGwVIP,"%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend VIPAvailability=strcat("https://portal.microsoftgeneva.com/dashboard/slbv2prod/AzureMonitor/VipAvailability_DataPathAvailability?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",MdmAccountName, "%22},{%22query%22:%22//*[id='VipAddress']%22,%22key%22:%22value%22,%22replacement%22:%22",ErGwVIP, "%22},{%22query%22:%22//*[id='Slbv2MDMAccount']%22,%22key%22:%22value%22,%22replacement%22:%22slbv2francecentral%22},{%22query%22:%22//*[id='CaAddress']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='DipPort']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='ProtocolType']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='DipAddress']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='HostAddress']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='Ring']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='LoadBalancerArmId']%22,%22key%22:%22value%22,%22replacement%22:%22""%22},{%22query%22:%22//*[id='PublicIpArmId']%22,%22key%22:%22value%22,%22replacement%22:%22", "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend DipAvailability=strcat("https://portal.microsoftgeneva.com/dashboard/slbv2prod/AzureMonitor/DipAvailability_HealthProbeStatus?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",MdmAccountName, "%22},{%22query%22:%22//*[id='VipAddress']%22,%22key%22:%22value%22,%22replacement%22:%22",ErGwVIP, "%22},{%22query%22:%22//*[id='Slbv2MDMAccount']%22,%22key%22:%22value%22,%22replacement%22:%22slbv2francecentral%22},{%22query%22:%22//*[id='CaAddress']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='DipPort']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='ProtocolType']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='DipAddress']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='HostAddress']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='Ring']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='LoadBalancerArmId']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='PublicIpArmId']%22,%22key%22:%22value%22,%22replacement%22:%22", "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend Sflowdashboard=strcat("https://portal.microsoftgeneva.com/s/B40A24AB?overrides=[{%22query%22:%22//*[id='DestinationVIP']%22,%22key%22:%22value%22,%22replacement%22:%22",ErGwVIP,"%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend Netflowdashboard=strcat("https://portal.microsoftgeneva.com/s/A5CECCEE?overrides=[{%22query%22:%22//*[id='DestinationVIP']%22,%22key%22:%22value%22,%22replacement%22:%22",ErGwVIP,"%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend DDOSStandardPlanCRIDashboard=strcat("https://portal.microsoftgeneva.com/s/BA074862?overrides=[{%22query%22:%22//*[id='DestinationVIP']%22,%22key%22:%22value%22,%22replacement%22:%22",ErGwVIP,"%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| distinct Vip, SKU, CountHosts, BandwithUsage,VIPAvailability,DipAvailability,Netflowdashboard,DDOSBasicPlanSflowDashbard=Sflowdashboard,DDOSStandardPlanCRIDashboard
| extend GatewayVIPTroubleshoot=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-VIP=v-",ErGwVIP,"#a172102b-f768-4cc9-982f-0acc07d4765f")
| evaluate narrow()
| project Key=Column, Value




```

### Tenant Log

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let gwname = ErGwName;
let GatewayID=materialize(cluster('hybridnetworking').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayType == "Dedicated"
| where GatewayName == gwname
| distinct GatewayId
);
cluster("hybridnetworking").database("aznwmds").GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where GatewayId in (GatewayID)
| where Message !startswith "GetAdjacencyTableWithValidation"
| where Message !startswith "GatewayMesh"
| where Message !startswith "ERGatewayRouteUpdateMonitor"
| project PreciseTimeStamp, GatewayId,RoleInstance,Message
```

### ER Gateway SLB MUX Dashboard(1 minute delay) - Need to Figure Out why VWAN Gateway doesn't show

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let gwname = ErGwName;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let min = datetime_diff('minute',endtime,starttime);
let ErGwVIP=toscalar(cluster('hybridnetworking').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayType == "Dedicated"
| where GatewayName == gwname
| distinct VIP=VIPAddress);
cluster('azslb').database('azslbmds').DSMulticastGroupEvent
| where env_time > starttime - 1h and env_time < endtime + 1h
| where SegmentName != "0.0.0.0_0" and SegmentName != "::_0"
| where Uri has "MuxPoolManager"
| summarize arg_max(env_time, *) by SegmentName, Uri
| project env_cloud_name, SegmentName, GroupIncarnationId, MulticastGroup
| extend CidrString = replace_string(SegmentName, "_", "/")
| extend Ipv4Cidr = iff(CidrString has ":", "", CidrString), Ipv6Cidr = iff(CidrString has ":", CidrString, "")
| where ipv6_is_in_range(ErGwVIP, Ipv6Cidr) or ipv4_is_in_range(ErGwVIP, Ipv4Cidr)
| extend groupIncarnationIdStr = replace_string(GroupIncarnationId, "-azr", "-az,r")
| join (
cluster('azslb').database('azslbmds').SlbMetadataVersionRecord
| where env_time > starttime - 1h and env_time < endtime + 1h
| summarize by Region, MdmAccountName, ArmRegion) on $left.env_cloud_name == $right.Region
| extend MuxProber = strcat("https://jarvis-west.dc.ad.msft.net/dashboard/slbv2stage/Mux/MuxProber?overrides=[%7B%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22slbintv2", ArmRegion, "%22},{%22query%22:%22//*[id=%27Ring%27]%22,%22key%22:%22value%22,%22replacement%22:%22", groupIncarnationIdStr, "%22},{%22query%22:%22//*[id=%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend MuxStatsV2 = strcat("https://jarvis-west.dc.ad.msft.net/dashboard/slbv2stage/Mux/MuxStatsV2?overrides=[%7B%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22slbintv2", ArmRegion, "%22},{%22query%22:%22//*[id=%27Ring%27]%22,%22key%22:%22value%22,%22replacement%22:%22", groupIncarnationIdStr, "%22},{%22query%22:%22//*[id=%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| project CidrString, MulticastGroup, MuxProber, MuxStatsV2
| evaluate narrow()
| project Key=Column, Value
```

### Network Latency between ErGw Region and IER devices of its connected MSEE

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let gwname = ErGwName;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let ShoeBoxMdm=materialize(cluster('AzureCM').database('AzureCM').LogClusterSnapshot 
| distinct Region, shoeboxMdmAccountName);
let gatewayid = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct GatewayId);
let ErGwVIP=toscalar(cluster('hybridnetworking').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayType == "Dedicated"
| where GatewayName == gwname
| distinct VIP=VIPAddress);
let ErGwRegion=cluster('azslb').database('azslbmds').VipMetadataSnapshotRecord
| where env_time > starttime - 6h and env_time < endtime + 1h
| where Vip == ErGwVIP
| summarize by Vip, VipUri, Type, SKU, AltAddress, VmLocs, CountHosts, env_cloud_role, Region
| join (cluster('azslb').database('azslbmds').SlbMetadataVersionRecord
| where env_time > starttime - 1h and env_time < endtime + 1h
|summarize by Region, MdmAccountName, ArmRegion
| extend HPAccountName = strcat("slbhp", substring(MdmAccountName, 5))) on $left.Region == $right.Region
| distinct ArmRegion;
let TestAgentNamesss=cluster('Aznwnetmon').database('ThousandEyes').CMTestMetrics
| where TestTime > starttime and TestTime <= endtime
| where TestName startswith "Peering"
| distinct AgentName
| extend AgentRegion=split(AgentName, "-")[2]
| where AgentRegion in (ErGwRegion)
| distinct AgentName;
let MSEEDevices=cluster('hybridnetworking').database('aznwmds').ERTunnelHealthTable    
| where PreciseTimeStamp > starttime and PreciseTimeStamp < endtime
| where GatewayId in (gatewayid)
| distinct DeviceName;
let IERs=cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where StartDevice in (MSEEDevices)
| where LinkType == "DeviceInterfaceLink"
| distinct EndDevice;
let IERrelatedTestName=cluster('Aznwnetmon').database('ThousandEyes').CMTestMetrics
| where TestTime > starttime and TestTime <= endtime
| where TestName startswith "Peering"
| extend DeviceName=tostring(split(TestName, "/")[1])
| where DeviceName in (IERs)
| distinct TestName;
cluster('Aznwnetmon').database('ThousandEyes').CMTestMetrics
| where TestTime > starttime and TestTime <= endtime
| where TestName in (IERrelatedTestName)
| where AgentName in (TestAgentNamesss)
| summarize AvgLatency=round(avg(AvgLatency), 2) by bin(TestTime, 1m), AS=tostring(split(split(TestName, "AS")[1], "-")[0]), IER=tostring(split(TestName, "/")[1]), ProbeRegion=tostring(split(AgentName, "-")[2])
| project TestTime, ProbeFrom=strcat(ProbeRegion, " to ASN ", AS, " via ", IER), AvgLatency
| render timechart
```

### Network Loss Ratio between ErGw Region and IER devices of its connected MSEE

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let gwname = ErGwName;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let ShoeBoxMdm=materialize(cluster('AzureCM').database('AzureCM').LogClusterSnapshot 
| distinct Region, shoeboxMdmAccountName);
let gatewayid = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct GatewayId);
let ErGwVIP=toscalar(cluster('hybridnetworking').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayType == "Dedicated"
| where GatewayName == gwname
| distinct VIP=VIPAddress);
let ErGwRegion=cluster('azslb').database('azslbmds').VipMetadataSnapshotRecord
| where env_time > starttime - 6h and env_time < endtime + 1h
| where Vip == ErGwVIP
| summarize by Vip, VipUri, Type, SKU, AltAddress, VmLocs, CountHosts, env_cloud_role, Region
| join (cluster('azslb').database('azslbmds').SlbMetadataVersionRecord
| where env_time > starttime - 1h and env_time < endtime + 1h
|summarize by Region, MdmAccountName, ArmRegion
| extend HPAccountName = strcat("slbhp", substring(MdmAccountName, 5))) on $left.Region == $right.Region
| distinct ArmRegion;
let TestAgentNamesss=cluster('Aznwnetmon').database('ThousandEyes').CMTestMetrics
| where TestTime > starttime and TestTime <= endtime
| where TestName startswith "Peering"
| distinct AgentName
| extend AgentRegion=split(AgentName, "-")[2]
| where AgentRegion in (ErGwRegion)
| distinct AgentName;
let MSEEDevices=cluster('hybridnetworking').database('aznwmds').ERTunnelHealthTable    
| where PreciseTimeStamp > starttime and PreciseTimeStamp < endtime
| where GatewayId in (gatewayid)
| distinct DeviceName;
let IERs=cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where StartDevice in (MSEEDevices)
| where LinkType == "DeviceInterfaceLink"
| distinct EndDevice;
let IERrelatedTestName=cluster('Aznwnetmon').database('ThousandEyes').CMTestMetrics
| where TestTime > starttime and TestTime <= endtime
| where TestName startswith "Peering"
| extend DeviceName=tostring(split(TestName, "/")[1])
| where DeviceName in (IERs)
| distinct TestName;
cluster('Aznwnetmon').database('ThousandEyes').CMTestMetrics
| where TestTime > starttime and TestTime <= endtime
| where TestName in (IERrelatedTestName)
| where AgentName in (TestAgentNamesss)
| summarize LossRatio=round(avg(Loss), 2) by bin(TestTime, 1m), AS=tostring(split(split(TestName, "AS")[1], "-")[0]), IER=tostring(split(TestName, "/")[1]), ProbeRegion=tostring(split(AgentName, "-")[2])
| project TestTime, ProbeFrom=strcat(ProbeRegion, " to ASN ", AS, " via ", IER), LossRatio
```

### Any maintenance over ExpressRoute Gateway?

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let gwname = ErGwName;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let min = datetime_diff('minute',endtime,starttime);
let ShoeBoxMdm=materialize(cluster('AzureCM').database('AzureCM').LogClusterSnapshot 
| distinct Region, shoeboxMdmAccountName);
let GatewayID=cluster('hybridnetworking').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayType == "Dedicated"
| where GatewayName == gwname
| distinct GatewayId;
let DeploymentInfo = cluster('hybridnetworking').database('aznwmds').ErVpnGwToContainerId
| where ingestion_time() between (starttime .. endtime)
| where GatewayId in (GatewayID)
| distinct TenantId;
let guestOsUpdates = cluster('azcore.centralus.kusto.windows.net').database('Fc').TMMgmtTenantManagementJobInfoEtwTable
| where PreciseTimeStamp between (starttime .. endtime)
| where TenantName in (DeploymentInfo)
| summarize min(PreciseTimeStamp), max(PreciseTimeStamp) by JobID
| extend GuestOsUpgradeInProgress = True;
let VmssOsUpdates = cluster('azcore.centralus.kusto.windows.net').database('Crp').VmssVMApiQosEvent
|where TIMESTAMP between (starttime .. endtime)
| where operationName == "VirtualMachineScaleSets.AutoOSUpgrade.POST"
| where resourceGroupName =~ strcat("armrg-", toscalar(GatewayID))
| summarize min(PreciseTimeStamp), max(PreciseTimeStamp) by operationId
| extend VmssOsUpgradeInProgress = True;
let FleetUpgrade = cluster('hybridnetworking').database('aznwmds').AsyncWorkerLogsTable
| where PreciseTimeStamp between (starttime .. endtime)
| where GatewayId in (GatewayID)
| where OperationName == "UpgradeGateway"
| where Message startswith "AsyncWorkerReportsTimeToStartExecutionEvent :" or Message startswith "DeleteQueueMessage: "
| summarize min_PreciseTimeStamp = min(PreciseTimeStamp), max_PreciseTimeStamp = max(PreciseTimeStamp) by ActivityId
| distinct min_PreciseTimeStamp, max_PreciseTimeStamp, ActivityId
| extend PlatformMaintenanceInProgress = True;
union VmssOsUpdates, guestOsUpdates, FleetUpgrade
| project MaintenanceStartTime = min_PreciseTimeStamp, MaintenanceEndTime=max_PreciseTimeStamp, GuestOsUpgradeInProgress, VmssOsUpgradeInProgress, PlatformMaintenanceInProgress
```

### ER Gateway Maintenance Events (by TenantName)

> Use this when you know the ER Gateway TenantName directly (e.g., from ASC). Useful for diagnosing BGP route selection changes after maintenance — BGP session flaps can reset route age and trigger asymmetric routing (MSEE Rule 10: oldest path wins).

```kql
cluster('azurecm').database('AzureCM').TMMgmtSlaMeasurementEventEtwTable
| where PreciseTimeStamp >= datetime('YYYY-MM-DD HH:mm:ss') and PreciseTimeStamp <= datetime('YYYY-MM-DD HH:mm:ss')
| where TenantName == '<ER_Gateway_TenantName>'
| project PreciseTimeStamp, Tenant, RoleInstanceName, Context, EntityState, TenantName, ContainerID, NodeID, Detail0, ActivityId
```

### PV

```kql
let pv=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('kusto').adxpageview| where page contains "b01/exrgateway";
let pvcount=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('microsoft').adxpageview | where page contains "b01/exrgateway" | summarize count();
union pv, pvcount
```

### Scheduled Event

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let gwname = ErGwName;
let GatewayID=materialize(cluster('hybridnetworking').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayType == "Dedicated"
| where GatewayName == gwname
| distinct GatewayId
);
cluster("hybridnetworking").database("aznwmds").GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where GatewayId in (GatewayID)
| where Message startswith "ScheduledEvents"
| where Message !contains "ScheduledEvents: Document is still the same. Skipping update tracker checks."
| project PreciseTimeStamp, GatewayId,RoleInstance,Message
```

### vNet Container Count

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let gwname = ErGwName;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let min = datetime_diff('minute',endtime,starttime);
let ShoeBoxMdm=materialize(cluster('AzureCM').database('AzureCM').LogClusterSnapshot 
| distinct Region, shoeboxMdmAccountName);
let vNetId=toscalar(cluster('hybridnetworking').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayType == "Dedicated"
| where GatewayName == gwname 
| distinct VNetId);
let vNetIdz=toupper(strcat("{", vNetId, "}"));
cluster("vnetkusto.northcentralus").database("veritas").InterfaceProgramEndFiveMinuteTable 
| where TIMESTAMP >= starttime - 3h and TIMESTAMP <= endtime + 3h
| where VnetGuid in (vNetIdz)
| distinct  TIMESTAMP=bin(TIMESTAMP, 5m), ContainerId
| summarize count=count() by TIMESTAMP
| render timechart 
```

### History Adjacency Table On GatewayTenantWorker_IN_0

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let gwname = ErGwName;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let gatewayvNetid = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct VNetId);
let GatewayConnectedCircuit=cluster('hybridnetworking').database('aznwmds').TunnelIntfTable   
| where PreciseTimeStamp > starttime - 2d and PreciseTimeStamp < endtime
| where VnetId in (gatewayvNetid)
| distinct ServiceKey, TunnelSourceIP=SourceIp,MSEETunnelInterfaceIP=IpAddress
| join kind=leftouter  (cluster('hybridnetworking').database('aznwmds').CircuitTable | where PreciseTimeStamp > starttime - 5d and PreciseTimeStamp < endtime) on $left.ServiceKey == $right.AzureServiceKey
| distinct ServiceKey, AzureSubscriptionId, CircuitName, TunnelSourceIP, MSEETunnelInterfaceIP;
let gatewayId = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 3d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct GatewayId);
let AdjacencyPrefixCount=cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime - 7d  and TIMESTAMP <= endtime + 1d
| where GatewayId in~ (gatewayId)
| where RoleInstance == "GatewayTenantWorker_IN_0"
| where Message contains "NextHopAddress" and Message contains "SourcePeer"
| project PreciseTimeStamp,RoleInstance, Message
| serialize
| extend IsNewAdjacency = iff(Message contains "<BGP> Updated adjacency table to version", 1, 0) 
| extend AdjacencyGroup = row_cumsum(IsNewAdjacency)
| project PreciseTimeStamp,RoleInstance, IsNewAdjacency, AdjacencyGroup, Message
| summarize PreciseTimeStamp = min(PreciseTimeStamp), EndTime= max(PreciseTimeStamp), Message = strcat_array(make_list(Message), "") by AdjacencyGroup,RoleInstance
| project PreciseTimeStamp, RoleInstance,EndTime, AdjacencyGroup, Message
| parse Message with * "<BGP> Updated adjacency table to version "TableVersion": Adjacencies List "ListNumber" of "TotalLists"\n" RouteEntry
//| extend RouteEntry = trim_end('\\n',RouteEntry)
| extend RouteEntry = split(trim_end('\\n',RouteEntry),'\n')
| project PreciseTimeStamp, RoleInstance,TableVersion, ListNumber, TotalLists,RouteEntry, Message
| summarize PreciseTimeStamp=take_anyif(PreciseTimeStamp, ListNumber == 1), RouteEntry=make_set(RouteEntry) by TableVersion, RoleInstance
| extend RouteEntryLength=array_length(RouteEntry)
| where isnotempty(TableVersion)
| project PreciseTimeStamp, RoleInstance, TableVersion,RouteEntryLength, RouteEntry
| mv-expand SingleRouteEntry = RouteEntry
| extend SingleRouteEntry_str = tostring(SingleRouteEntry)
| extend Prefix = extract(@"^([\d\.\/]+)", 1, SingleRouteEntry_str)
| extend NextHopAddress = extract_all(@"NextHopAddress:\s*([\d\.]+)", SingleRouteEntry_str)
| where isnotempty(Prefix)
| mv-expand NextHopAddress = NextHopAddress
| project PreciseTimeStamp,RoleInstance, TableVersion, RouteEntryLength,Prefix
| distinct TableVersion, Prefix
| summarize PrefixCount=count() by TableVersion;
cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime - 7d  and TIMESTAMP <= endtime + 1d
| where GatewayId in~ (gatewayId)
| where RoleInstance == "GatewayTenantWorker_IN_0"
| where Message contains "NextHopAddress" and Message contains "SourcePeer"
| project PreciseTimeStamp,RoleInstance, Message
| serialize
| extend IsNewAdjacency = iff(Message contains "<BGP> Updated adjacency table to version", 1, 0) 
| extend AdjacencyGroup = row_cumsum(IsNewAdjacency)
| project PreciseTimeStamp,RoleInstance, IsNewAdjacency, AdjacencyGroup, Message
| summarize PreciseTimeStamp = min(PreciseTimeStamp), EndTime= max(PreciseTimeStamp), Message = strcat_array(make_list(Message), "") by AdjacencyGroup,RoleInstance
| project PreciseTimeStamp, RoleInstance,EndTime, AdjacencyGroup, Message
| parse Message with * "<BGP> Updated adjacency table to version "TableVersion": Adjacencies List "ListNumber" of "TotalLists"\n" RouteEntry
//| extend RouteEntry = trim_end('\\n',RouteEntry)
| extend RouteEntry = split(trim_end('\\n',RouteEntry),'\n')
| project PreciseTimeStamp, RoleInstance,TableVersion, ListNumber, TotalLists,RouteEntry, Message
| summarize PreciseTimeStamp=take_anyif(PreciseTimeStamp, ListNumber == 1), RouteEntry=make_set(RouteEntry) by TableVersion, RoleInstance
| where isnotempty(TableVersion)
| project PreciseTimeStamp, RoleInstance, TableVersion, RouteEntry
| mv-expand SingleRouteEntry = RouteEntry
| extend SingleRouteEntry_str = tostring(SingleRouteEntry)
| extend Prefix = extract(@"^([\d\.\/]+)", 1, SingleRouteEntry_str)
| extend NextHopAddress = extract_all(@"NextHopAddress:\s*([\d\.]+)", SingleRouteEntry_str)
| where isnotempty(Prefix)
| mv-expand NextHopAddress = NextHopAddress
| project PreciseTimeStamp,RoleInstance, TableVersion,Prefix, NextHopAddress=tostring(NextHopAddress)
| join kind=leftouter AdjacencyPrefixCount on TableVersion
| join kind=leftouter  GatewayConnectedCircuit on $left.NextHopAddress == $right.TunnelSourceIP
| where RoleInstance == "GatewayTenantWorker_IN_0"
| extend RouteSource=iff(isempty(ServiceKey), "IPSec", "ExpressRoute")
| distinct PreciseTimeStamp=bin(PreciseTimeStamp, 1m),RoleInstance, TableVersion_PrefixCount=strcat(TableVersion,"_", PrefixCount), Prefix,RouteSource,NextHopAddress, CircuitName, ServiceKey,CircuitSubscriptionId=AzureSubscriptionId
| distinct AdjacencyTableUpdateTimeStamp=PreciseTimeStamp, AdjacencyTableVersion_PrefixCount=TableVersion_PrefixCount,RouteSource, Prefix, ServiceKey,CircuitName, CircuitSubscriptionId
| extend ERCircuitTroubleshootingLink=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubscriptionID=v-",CircuitSubscriptionId,"&p-ExpressRouteCircuitName=v-",CircuitName,"&p-SyslogFilter=all#d7150dfa-a8d2-438d-b97f-6de6b0da282c")
| extend ERCircuitTroubleshootingLink=iff(isnotempty(ServiceKey), ERCircuitTroubleshootingLink, "-")
| order  by AdjacencyTableUpdateTimeStamp
```

### Adjacency Table Size On GatewayTenantWorker_IN_0

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let gwname = ErGwName;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let gatewayId = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct GatewayId);
cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime - 3d  and TIMESTAMP <= endtime + 3d
| where GatewayId in~ (gatewayId)
| where RoleInstance == "GatewayTenantWorker_IN_0"
| where Message contains "Updated adjacency table to version"
| where Message contains "Adjacency table size"
| project PreciseTimeStamp,RoleInstance, Message
| parse Message with "<BGP> Updated adjacency table to version " TableVersion "(HEX: " HEX ") at time " * ". Adjacency table size: " TableSize
| summarize arg_max(PreciseTimeStamp, *) by TableVersion,RoleInstance
| project PreciseTimeStamp, RoleInstance, TableSize=toint(TableSize)
| render scatterchart       
```

### Adjacency Table Size On GatewayTenantWorker_IN_1

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let gwname = ErGwName;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let gatewayId = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct GatewayId);
cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime - 3d  and TIMESTAMP <= endtime + 1d
| where GatewayId in~ (gatewayId)
| where RoleInstance == "GatewayTenantWorker_IN_1"
| where Message contains "Updated adjacency table to version"
| where Message contains "Adjacency table size"
| project PreciseTimeStamp,RoleInstance, Message
| parse Message with "<BGP> Updated adjacency table to version " TableVersion "(HEX: " HEX ") at time " * ". Adjacency table size: " TableSize
| summarize arg_max(PreciseTimeStamp, *) by TableVersion,RoleInstance
| project PreciseTimeStamp, RoleInstance, TableSize=toint(TableSize)
| render scatterchart       
```

### Adjacency Table On GatewayTenantWorker_IN_0

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let gwname = ErGwName;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let ErPrefix = todynamic(ErOnpremPrefix);
let gatewayvNetid = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct VNetId);
let GatewayConnectedCircuit=cluster('hybridnetworking').database('aznwmds').TunnelIntfTable   
| where PreciseTimeStamp > starttime - 2d and PreciseTimeStamp < endtime
| where VnetId in (gatewayvNetid)
| distinct ServiceKey, TunnelSourceIP=SourceIp,MSEETunnelInterfaceIP=IpAddress
| join kind=leftouter  (cluster('hybridnetworking').database('aznwmds').CircuitTable | where PreciseTimeStamp > starttime - 5d and PreciseTimeStamp < endtime) on $left.ServiceKey == $right.AzureServiceKey
| distinct ServiceKey, AzureSubscriptionId, CircuitName, TunnelSourceIP, MSEETunnelInterfaceIP;
let gatewayId = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 3d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct GatewayId);
let LatestAdjTableVersion=cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime - 7d  and TIMESTAMP <= endtime
| where GatewayId in~ (gatewayId)
| where RoleInstance == "GatewayTenantWorker_IN_0"
| where Message contains "Updated adjacency table to version"
| where Message contains "Adjacency table size"
| project PreciseTimeStamp,RoleInstance, Message
| parse Message with "<BGP> Updated adjacency table to version "TableVersion" (HEX: " HEX ") at time " * ". Adjacency table size: " TableSize
| summarize max(TableVersion);
cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime - 7d  and TIMESTAMP <= endtime + 1d
| where GatewayId in~ (gatewayId)
| where RoleInstance == "GatewayTenantWorker_IN_0"
| where Message contains "NextHopAddress" and Message contains "SourcePeer"
| project PreciseTimeStamp,RoleInstance, Message
| serialize
| extend IsNewAdjacency = iff(Message contains "<BGP> Updated adjacency table to version", 1, 0) 
| extend AdjacencyGroup = row_cumsum(IsNewAdjacency)
| project PreciseTimeStamp,RoleInstance, IsNewAdjacency, AdjacencyGroup, Message
| summarize PreciseTimeStamp = min(PreciseTimeStamp), EndTime= max(PreciseTimeStamp), Message = strcat_array(make_list(Message), "") by AdjacencyGroup,RoleInstance
| project PreciseTimeStamp, RoleInstance,EndTime, AdjacencyGroup, Message
| parse Message with * "<BGP> Updated adjacency table to version "TableVersion": Adjacencies List "ListNumber" of "TotalLists"\n" RouteEntry
//| extend RouteEntry = trim_end('\\n',RouteEntry)
| extend RouteEntry = split(trim_end('\\n',RouteEntry),'\n')
| where TableVersion in (LatestAdjTableVersion)
| project PreciseTimeStamp, RoleInstance,TableVersion, ListNumber, TotalLists,RouteEntry, Message
| summarize PreciseTimeStamp=take_anyif(PreciseTimeStamp, ListNumber == 1), RouteEntry=make_set(RouteEntry) by TableVersion, RoleInstance
| where isnotempty(TableVersion)
| project PreciseTimeStamp, RoleInstance, TableVersion, RouteEntry
| mv-expand SingleRouteEntry = RouteEntry
| extend SingleRouteEntry_str = tostring(SingleRouteEntry)
| extend Prefix = extract(@"^([\d\.\/]+)", 1, SingleRouteEntry_str)
| extend NextHopAddress = extract_all(@"NextHopAddress:\s*([\d\.]+)", SingleRouteEntry_str)
| where isnotempty(Prefix)
| mv-expand NextHopAddress = NextHopAddress
| project PreciseTimeStamp,RoleInstance, TableVersion,Prefix, NextHopAddress=tostring(NextHopAddress)
| join kind=leftouter  GatewayConnectedCircuit on $left.NextHopAddress == $right.TunnelSourceIP
| where RoleInstance == "GatewayTenantWorker_IN_0"
| extend RouteSource=iff(isempty(ServiceKey), "IPSec", "ExpressRoute")
| distinct PreciseTimeStamp=bin(PreciseTimeStamp, 1m),RoleInstance, TableVersion, Prefix,RouteSource,NextHopAddress, CircuitName, ServiceKey,CircuitSubscriptionId=AzureSubscriptionId
| distinct AdjacencyTableUpdateTimeStamp=PreciseTimeStamp, TableVersion,RouteSource, Prefix, ServiceKey,CircuitName, CircuitSubscriptionId
| extend ERCircuitTroubleshootingLink=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubscriptionID=v-",CircuitSubscriptionId,"&p-ExpressRouteCircuitName=v-",CircuitName,"&p-SyslogFilter=all#d7150dfa-a8d2-438d-b97f-6de6b0da282c")
| extend ERCircuitTroubleshootingLink=iff(isnotempty(ServiceKey), ERCircuitTroubleshootingLink, "-")
| where iff(isnull(ErPrefix), true, Prefix in(ErPrefix))


```

### Packet Drop Counter In Physical Interface Of Selected Prefix Connected MSEE

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let gwname = ErGwName;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let ErPrefix = todynamic(ErOnpremPrefix);
let gatewayvNetid = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct VNetId);
let GatewayConnectedCircuit=cluster('hybridnetworking').database('aznwmds').TunnelIntfTable   
| where PreciseTimeStamp > starttime - 2d and PreciseTimeStamp < endtime
| where VnetId in (gatewayvNetid)
| distinct ServiceKey, TunnelSourceIP=SourceIp,MSEETunnelInterfaceIP=IpAddress
| join kind=leftouter  (cluster('hybridnetworking').database('aznwmds').CircuitTable | where PreciseTimeStamp > starttime - 5d and PreciseTimeStamp < endtime) on $left.ServiceKey == $right.AzureServiceKey
| distinct ServiceKey, AzureSubscriptionId, CircuitName, TunnelSourceIP, MSEETunnelInterfaceIP;
let gatewayId = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 3d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct GatewayId);
let LatestAdjTableVersion=cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime - 7d  and TIMESTAMP <= endtime
| where GatewayId in~ (gatewayId)
| where RoleInstance == "GatewayTenantWorker_IN_0"
| where Message contains "Updated adjacency table to version"
| where Message contains "Adjacency table size"
| project PreciseTimeStamp,RoleInstance, Message
| parse Message with "<BGP> Updated adjacency table to version "TableVersion" (HEX: " HEX ") at time " * ". Adjacency table size: " TableSize
| summarize max(TableVersion);
let PrefixServiceKey=cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime - 7d  and TIMESTAMP <= endtime + 1d
| where GatewayId in~ (gatewayId)
| where RoleInstance == "GatewayTenantWorker_IN_0"
| where Message contains "NextHopAddress" and Message contains "SourcePeer"
| project PreciseTimeStamp,RoleInstance, Message
| serialize
| extend IsNewAdjacency = iff(Message contains "<BGP> Updated adjacency table to version", 1, 0) 
| extend AdjacencyGroup = row_cumsum(IsNewAdjacency)
| project PreciseTimeStamp,RoleInstance, IsNewAdjacency, AdjacencyGroup, Message
| summarize PreciseTimeStamp = min(PreciseTimeStamp), EndTime= max(PreciseTimeStamp), Message = strcat_array(make_list(Message), "") by AdjacencyGroup,RoleInstance
| project PreciseTimeStamp, RoleInstance,EndTime, AdjacencyGroup, Message
| parse Message with * "<BGP> Updated adjacency table to version "TableVersion": Adjacencies List "ListNumber" of "TotalLists"\n" RouteEntry
//| extend RouteEntry = trim_end('\\n',RouteEntry)
| extend RouteEntry = split(trim_end('\\n',RouteEntry),'\n')
| where TableVersion in (LatestAdjTableVersion)
| project PreciseTimeStamp, RoleInstance,TableVersion, ListNumber, TotalLists,RouteEntry, Message
| summarize PreciseTimeStamp=take_anyif(PreciseTimeStamp, ListNumber == 1), RouteEntry=make_set(RouteEntry) by TableVersion, RoleInstance
| where isnotempty(TableVersion)
| project PreciseTimeStamp, RoleInstance, TableVersion, RouteEntry
| mv-expand SingleRouteEntry = RouteEntry
| extend SingleRouteEntry_str = tostring(SingleRouteEntry)
| extend Prefix = extract(@"^([\d\.\/]+)", 1, SingleRouteEntry_str)
| extend NextHopAddress = extract_all(@"NextHopAddress:\s*([\d\.]+)", SingleRouteEntry_str)
| where isnotempty(Prefix)
| mv-expand NextHopAddress = NextHopAddress
| project PreciseTimeStamp,RoleInstance, TableVersion,Prefix, NextHopAddress=tostring(NextHopAddress)
| join kind=leftouter  GatewayConnectedCircuit on $left.NextHopAddress == $right.TunnelSourceIP
| where RoleInstance == "GatewayTenantWorker_IN_0"
| extend RouteSource=iff(isempty(ServiceKey), "IPSec", "ExpressRoute")
| distinct PreciseTimeStamp=bin(PreciseTimeStamp, 1m),RoleInstance, TableVersion, Prefix,RouteSource,NextHopAddress, CircuitName, ServiceKey,CircuitSubscriptionId=AzureSubscriptionId
| distinct AdjacencyTableUpdateTimeStamp=PreciseTimeStamp, TableVersion,RouteSource, Prefix, ServiceKey,CircuitName, CircuitSubscriptionId
| extend ERCircuitTroubleshootingLink=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubscriptionID=v-",CircuitSubscriptionId,"&p-ExpressRouteCircuitName=v-",CircuitName,"&p-SyslogFilter=all#d7150dfa-a8d2-438d-b97f-6de6b0da282c")
| extend ERCircuitTroubleshootingLink=iff(isnotempty(ServiceKey), ERCircuitTroubleshootingLink, "-")
| where iff(isnull(ErPrefix), true, Prefix in(ErPrefix))
| distinct ServiceKey;
let DeviceNames=materialize(cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d
| where AzureServiceKey in (PrefixServiceKey)
| distinct ServiceKey=AzureServiceKey
| join kind=leftouter cluster("Hybridnetworking").database("aznwmds").SubIntfTable on ServiceKey
| join kind=leftouter cluster("Hybridnetworking").database("aznwmds").VrfTable on ServiceKey
| distinct DeviceNames=DeviceName);
let InterfaceNames=materialize(cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where AzureServiceKey in (PrefixServiceKey)
| distinct ServiceKey=AzureServiceKey
| join kind=leftouter cluster("Hybridnetworking").database("aznwmds").SubIntfTable on ServiceKey
| join kind=leftouter cluster("Hybridnetworking").database("aznwmds").VrfTable on ServiceKey
| project InterfaceNames=strcat(DeviceName, "-", tostring(split(InterfaceName,".")[0]))
| distinct tostring(InterfaceNames));
cluster('Aznwnetmon').database('aznwmds').sXInterfaceTable 
| where ReceivedUtc >= starttime and ReceivedUtc <= endtime
| where DeviceName in (DeviceNames)
| extend DeviceIF=strcat(DeviceName, "-", ifName)
| where DeviceIF in (InterfaceNames)
| project ReceivedUtc, DeviceName, DeviceIp, ifName, ifAdminStatus, ifOperStatus, ifDescr, ifInDiscards_Counter, ifOutDiscards_Counter, ifInErrors_Counter, ifOutErrors_Counter, DeviceIF
| project ReceivedUtc, DeviceIF, ifInDiscards_Counter, ifOutDiscards_Counter, ifInErrors_Counter, ifOutErrors_Counter
| render columnchart


```

### Moby Loss Ratio to the MSEE Of Selected Prefix Connected MSEE

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let gwname = ErGwName;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let ErPrefix = todynamic(ErOnpremPrefix);
let gatewayvNetid = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct VNetId);
let GatewayConnectedCircuit=cluster('hybridnetworking').database('aznwmds').TunnelIntfTable   
| where PreciseTimeStamp > starttime - 2d and PreciseTimeStamp < endtime
| where VnetId in (gatewayvNetid)
| distinct ServiceKey, TunnelSourceIP=SourceIp,MSEETunnelInterfaceIP=IpAddress
| join kind=leftouter  (cluster('hybridnetworking').database('aznwmds').CircuitTable | where PreciseTimeStamp > starttime - 5d and PreciseTimeStamp < endtime) on $left.ServiceKey == $right.AzureServiceKey
| distinct ServiceKey, AzureSubscriptionId, CircuitName, TunnelSourceIP, MSEETunnelInterfaceIP;
let gatewayId = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 3d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct GatewayId);
let LatestAdjTableVersion=cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime - 7d  and TIMESTAMP <= endtime
| where GatewayId in~ (gatewayId)
| where RoleInstance == "GatewayTenantWorker_IN_0"
| where Message contains "Updated adjacency table to version"
| where Message contains "Adjacency table size"
| project PreciseTimeStamp,RoleInstance, Message
| parse Message with "<BGP> Updated adjacency table to version "TableVersion" (HEX: " HEX ") at time " * ". Adjacency table size: " TableSize
| summarize max(TableVersion);
let PrefixServiceKey=cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime - 7d  and TIMESTAMP <= endtime + 1d
| where GatewayId in~ (gatewayId)
| where RoleInstance == "GatewayTenantWorker_IN_0"
| where Message contains "NextHopAddress" and Message contains "SourcePeer"
| project PreciseTimeStamp,RoleInstance, Message
| serialize
| extend IsNewAdjacency = iff(Message contains "<BGP> Updated adjacency table to version", 1, 0) 
| extend AdjacencyGroup = row_cumsum(IsNewAdjacency)
| project PreciseTimeStamp,RoleInstance, IsNewAdjacency, AdjacencyGroup, Message
| summarize PreciseTimeStamp = min(PreciseTimeStamp), EndTime= max(PreciseTimeStamp), Message = strcat_array(make_list(Message), "") by AdjacencyGroup,RoleInstance
| project PreciseTimeStamp, RoleInstance,EndTime, AdjacencyGroup, Message
| parse Message with * "<BGP> Updated adjacency table to version "TableVersion": Adjacencies List "ListNumber" of "TotalLists"\n" RouteEntry
//| extend RouteEntry = trim_end('\\n',RouteEntry)
| extend RouteEntry = split(trim_end('\\n',RouteEntry),'\n')
| where TableVersion in (LatestAdjTableVersion)
| project PreciseTimeStamp, RoleInstance,TableVersion, ListNumber, TotalLists,RouteEntry, Message
| summarize PreciseTimeStamp=take_anyif(PreciseTimeStamp, ListNumber == 1), RouteEntry=make_set(RouteEntry) by TableVersion, RoleInstance
| where isnotempty(TableVersion)
| project PreciseTimeStamp, RoleInstance, TableVersion, RouteEntry
| mv-expand SingleRouteEntry = RouteEntry
| extend SingleRouteEntry_str = tostring(SingleRouteEntry)
| extend Prefix = extract(@"^([\d\.\/]+)", 1, SingleRouteEntry_str)
| extend NextHopAddress = extract_all(@"NextHopAddress:\s*([\d\.]+)", SingleRouteEntry_str)
| where isnotempty(Prefix)
| mv-expand NextHopAddress = NextHopAddress
| project PreciseTimeStamp,RoleInstance, TableVersion,Prefix, NextHopAddress=tostring(NextHopAddress)
| join kind=leftouter  GatewayConnectedCircuit on $left.NextHopAddress == $right.TunnelSourceIP
| where RoleInstance == "GatewayTenantWorker_IN_0"
| extend RouteSource=iff(isempty(ServiceKey), "IPSec", "ExpressRoute")
| distinct PreciseTimeStamp=bin(PreciseTimeStamp, 1m),RoleInstance, TableVersion, Prefix,RouteSource,NextHopAddress, CircuitName, ServiceKey,CircuitSubscriptionId=AzureSubscriptionId
| distinct AdjacencyTableUpdateTimeStamp=PreciseTimeStamp, TableVersion,RouteSource, Prefix, ServiceKey,CircuitName, CircuitSubscriptionId
| extend ERCircuitTroubleshootingLink=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubscriptionID=v-",CircuitSubscriptionId,"&p-ExpressRouteCircuitName=v-",CircuitName,"&p-SyslogFilter=all#d7150dfa-a8d2-438d-b97f-6de6b0da282c")
| extend ERCircuitTroubleshootingLink=iff(isnotempty(ServiceKey), ERCircuitTroubleshootingLink, "-")
| where iff(isnull(ErPrefix), true, Prefix in(ErPrefix))
| distinct ServiceKey;
let Deviceslist=toscalar(cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d
| where AzureServiceKey in (PrefixServiceKey)
| distinct ServiceKey=AzureServiceKey
| join kind=leftouter cluster("Hybridnetworking").database("aznwmds").SubIntfTable on ServiceKey
| join kind=leftouter cluster("Hybridnetworking").database("aznwmds").VrfTable on ServiceKey
| distinct DeviceNames=DeviceName
| summarize DeviceNamesList=make_list(DeviceNames)
| extend Devicelist=strcat('("', array_strcat(DeviceNamesList, '","'), '")')
| distinct Devicelist
);
let moby_query = strcat('metricNamespace("Canary").metric("PacketSuccess").dimensions("Region", "Device", "DestRegion", "DestDevice", "DestIP", "WanType").samplingTypes("Average") | where DestDevice in ', Deviceslist);
evaluate geneva_metrics_request('MobyProdMetrics',moby_query, starttime, endtime)
| where Average != 0
| summarize Average=(1-avg(Average))*100 by bin(TimestampUtc, 1m), DestDevice
| render timechart


```

### Moby Loss Ratio to the IERs&ICRs&RWAs Of Selected Prefix Connected MSEE

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let gwname = ErGwName;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let ErPrefix = todynamic(ErOnpremPrefix);
let gatewayvNetid = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct VNetId);
let GatewayConnectedCircuit=cluster('hybridnetworking').database('aznwmds').TunnelIntfTable   
| where PreciseTimeStamp > starttime - 2d and PreciseTimeStamp < endtime
| where VnetId in (gatewayvNetid)
| distinct ServiceKey, TunnelSourceIP=SourceIp,MSEETunnelInterfaceIP=IpAddress
| join kind=leftouter  (cluster('hybridnetworking').database('aznwmds').CircuitTable | where PreciseTimeStamp > starttime - 5d and PreciseTimeStamp < endtime) on $left.ServiceKey == $right.AzureServiceKey
| distinct ServiceKey, AzureSubscriptionId, CircuitName, TunnelSourceIP, MSEETunnelInterfaceIP;
let gatewayId = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 3d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct GatewayId);
let LatestAdjTableVersion=cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime - 7d  and TIMESTAMP <= endtime
| where GatewayId in~ (gatewayId)
| where RoleInstance == "GatewayTenantWorker_IN_0"
| where Message contains "Updated adjacency table to version"
| where Message contains "Adjacency table size"
| project PreciseTimeStamp,RoleInstance, Message
| parse Message with "<BGP> Updated adjacency table to version "TableVersion" (HEX: " HEX ") at time " * ". Adjacency table size: " TableSize
| summarize max(TableVersion);
let PrefixServiceKey=cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime - 7d  and TIMESTAMP <= endtime + 1d
| where GatewayId in~ (gatewayId)
| where RoleInstance == "GatewayTenantWorker_IN_0"
| where Message contains "NextHopAddress" and Message contains "SourcePeer"
| project PreciseTimeStamp,RoleInstance, Message
| serialize
| extend IsNewAdjacency = iff(Message contains "<BGP> Updated adjacency table to version", 1, 0) 
| extend AdjacencyGroup = row_cumsum(IsNewAdjacency)
| project PreciseTimeStamp,RoleInstance, IsNewAdjacency, AdjacencyGroup, Message
| summarize PreciseTimeStamp = min(PreciseTimeStamp), EndTime= max(PreciseTimeStamp), Message = strcat_array(make_list(Message), "") by AdjacencyGroup,RoleInstance
| project PreciseTimeStamp, RoleInstance,EndTime, AdjacencyGroup, Message
| parse Message with * "<BGP> Updated adjacency table to version "TableVersion": Adjacencies List "ListNumber" of "TotalLists"\n" RouteEntry
//| extend RouteEntry = trim_end('\\n',RouteEntry)
| extend RouteEntry = split(trim_end('\\n',RouteEntry),'\n')
| where TableVersion in (LatestAdjTableVersion)
| project PreciseTimeStamp, RoleInstance,TableVersion, ListNumber, TotalLists,RouteEntry, Message
| summarize PreciseTimeStamp=take_anyif(PreciseTimeStamp, ListNumber == 1), RouteEntry=make_set(RouteEntry) by TableVersion, RoleInstance
| where isnotempty(TableVersion)
| project PreciseTimeStamp, RoleInstance, TableVersion, RouteEntry
| mv-expand SingleRouteEntry = RouteEntry
| extend SingleRouteEntry_str = tostring(SingleRouteEntry)
| extend Prefix = extract(@"^([\d\.\/]+)", 1, SingleRouteEntry_str)
| extend NextHopAddress = extract_all(@"NextHopAddress:\s*([\d\.]+)", SingleRouteEntry_str)
| where isnotempty(Prefix)
| mv-expand NextHopAddress = NextHopAddress
| project PreciseTimeStamp,RoleInstance, TableVersion,Prefix, NextHopAddress=tostring(NextHopAddress)
| join kind=leftouter  GatewayConnectedCircuit on $left.NextHopAddress == $right.TunnelSourceIP
| where RoleInstance == "GatewayTenantWorker_IN_0"
| extend RouteSource=iff(isempty(ServiceKey), "IPSec", "ExpressRoute")
| distinct PreciseTimeStamp=bin(PreciseTimeStamp, 1m),RoleInstance, TableVersion, Prefix,RouteSource,NextHopAddress, CircuitName, ServiceKey,CircuitSubscriptionId=AzureSubscriptionId
| distinct AdjacencyTableUpdateTimeStamp=PreciseTimeStamp, TableVersion,RouteSource, Prefix, ServiceKey,CircuitName, CircuitSubscriptionId
| extend ERCircuitTroubleshootingLink=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubscriptionID=v-",CircuitSubscriptionId,"&p-ExpressRouteCircuitName=v-",CircuitName,"&p-SyslogFilter=all#d7150dfa-a8d2-438d-b97f-6de6b0da282c")
| extend ERCircuitTroubleshootingLink=iff(isnotempty(ServiceKey), ERCircuitTroubleshootingLink, "-")
| where iff(isnull(ErPrefix), true, Prefix in(ErPrefix))
| distinct ServiceKey;
let MSEEDeviceslist=cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d
| where AzureServiceKey in (PrefixServiceKey)
| distinct ServiceKey=AzureServiceKey
| join kind=leftouter cluster("Hybridnetworking").database("aznwmds").SubIntfTable on ServiceKey
| join kind=leftouter cluster("Hybridnetworking").database("aznwmds").VrfTable on ServiceKey
| distinct EndDevice=DeviceName;
let IERs=cluster('Aznwcc').database('aznwmds').DeviceInterfaceLinks
| where StartDevice in~ (MSEEDeviceslist)
| where isnotempty(StartBGPV4Peer) or isnotempty(StartBGPV6Peer)
| distinct EndDevice;
let ICRRWAs=cluster('Aznwcc').database('aznwmds').DeviceInterfaceLinks
| where StartDevice in~ (IERs)
| where EndDevice !startswith "extisp"
| where isnotempty(StartBGPV4Peer) or isnotempty(StartBGPV6Peer)
| distinct EndDevice;
let MobyCoreDevices=toscalar(union IERs, ICRRWAs
| summarize DeviceNamesList=make_list(EndDevice)
| extend Devicelist=strcat('("', array_strcat(DeviceNamesList, '","'), '")')
| distinct Devicelist);
let moby_query = strcat('metricNamespace("Canary").metric("PacketSuccess").dimensions("Region", "Device", "DestRegion", "DestDevice", "DestIP", "WanType").samplingTypes("Average") | where DestDevice in ', MobyCoreDevices);
evaluate geneva_metrics_request('MobyProdMetrics',moby_query, starttime, endtime)
| where Average != 0
| summarize Average=(1-avg(Average))*100 by bin(TimestampUtc, 1m), DestDevice
| render timechart


```

### Gateway Mesh Latency

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let gwname = ErGwName;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let gatewayId = toscalar(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 3d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct GatewayId);
let GatewayPingMesh_Query = strcat('metricNamespace("GatewayHealth").metric("GatewayMeshLatency").dimensions("GatewayId", "GatewayMeshDestination", "GatewayMeshSource").samplingTypes("Average") | where GatewayId == ', '"',gatewayId, '"');
evaluate geneva_metrics_request('AznwErUSWest',GatewayPingMesh_Query, starttime, endtime)
| extend Pair=strcat(GatewayMeshSource, "->",GatewayMeshDestination)
| project TimestampUtc, Pair, Average
| render timechart 

```

### BGP Peer RTT Metrics

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let gwname = ErGwName;
let gatewayId = toscalar(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 3d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct GatewayId);
let gatewayvNetid = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct VNetId);
let MSEETunnelMapping=cluster('hybridnetworking').database('aznwmds').TunnelIntfTable   
| where PreciseTimeStamp > starttime - 2d and PreciseTimeStamp < endtime
| where VnetId in (gatewayvNetid)
| distinct DeviceName, IpAddress;
let BGPPeerRTT_Query = strcat('metricNamespace("GatewayHealth").metric("BgpPeerTcpSmoothedRttMetric").dimensions("GatewayId","BgpPeerAddress", "RoleInstance").samplingTypes("Average") | where GatewayId == ', '"',gatewayId, '"');
evaluate geneva_metrics_request('AznwErUSWest',BGPPeerRTT_Query, starttime, endtime)
| project TimestampUtc,RoleInstance,BgpPeerAddress, Average
| join kind=leftouter MSEETunnelMapping on $left.BgpPeerAddress == $right.IpAddress
| project TimestampUtc, BGPPeer=strcat(RoleInstance, "->",DeviceName, ":", BgpPeerAddress), Average
| render timechart

```

### Inbound Traffic(From MSEE to vNet) in Mbps

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let gwname = ErGwName;
let gatewayId = toscalar(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 3d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct GatewayId);
let gatewayvNetid = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct VNetId);
let skey=cluster('hybridnetworking').database('aznwmds').TunnelIntfTable   
| where PreciseTimeStamp > starttime - 1d and PreciseTimeStamp < endtime
| where VnetId in (gatewayvNetid)
| distinct ServiceKey;
let circuitidname=cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp > starttime - 1d and PreciseTimeStamp < endtime
| where AzureServiceKey in (skey)
| distinct AzureServiceKey, CircuitName;
let BitsIn_Query = strcat('metricNamespace("Shoebox").metric("BitsInPerSecond").dimensions("GatewayId", "ServiceKey").samplingTypes("Average") | where GatewayId == ', '"',gatewayId, '"');
evaluate geneva_metrics_request('HybridGWShoeboxProd',BitsIn_Query, starttime, endtime)
| project TimestampUtc, ServiceKey, Average
| join kind=leftouter circuitidname on $left.ServiceKey == $right.AzureServiceKey
| project TimestampUtc, Circuit=CircuitName, Mbps=round(toreal(Average/1000000), 2)
| render timechart 
```

### Outbound Traffic(From vNet to MSEE) in Mbps

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let gwname = ErGwName;
let gatewayId = toscalar(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 3d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct GatewayId);
let gatewayvNetid = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct VNetId);
let skey=cluster('hybridnetworking').database('aznwmds').TunnelIntfTable   
| where PreciseTimeStamp > starttime - 1d and PreciseTimeStamp < endtime
| where VnetId in (gatewayvNetid)
| distinct ServiceKey;
let circuitidname=cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp > starttime - 1d and PreciseTimeStamp < endtime
| where AzureServiceKey in (skey)
| distinct AzureServiceKey, CircuitName;
let BitsOut_Query = strcat('metricNamespace("Shoebox").metric("BitsOutPerSecond").dimensions("GatewayId", "ServiceKey").samplingTypes("Average") | where GatewayId == ', '"',gatewayId, '"');
evaluate geneva_metrics_request('HybridGWShoeboxProd',BitsOut_Query, starttime, endtime)
| project TimestampUtc, ServiceKey, Average
| join kind=leftouter circuitidname on $left.ServiceKey == $right.AzureServiceKey
| project TimestampUtc, Circuit=CircuitName, Mbps=round(toreal(Average/1000000), 2)
| render timechart 
```

### ExpressRoute Circuit Bits In Utilization(SubInterface) Of Selected Prefix

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let gwname = ErGwName;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let ErPrefix = todynamic(ErOnpremPrefix);
let gatewayvNetid = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct VNetId);
let GatewayConnectedCircuit=cluster('hybridnetworking').database('aznwmds').TunnelIntfTable   
| where PreciseTimeStamp > starttime - 2d and PreciseTimeStamp < endtime
| where VnetId in (gatewayvNetid)
| distinct ServiceKey, TunnelSourceIP=SourceIp,MSEETunnelInterfaceIP=IpAddress
| join kind=leftouter  (cluster('hybridnetworking').database('aznwmds').CircuitTable | where PreciseTimeStamp > starttime - 5d and PreciseTimeStamp < endtime) on $left.ServiceKey == $right.AzureServiceKey
| distinct ServiceKey, AzureSubscriptionId, CircuitName, TunnelSourceIP, MSEETunnelInterfaceIP;
let gatewayId = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 3d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct GatewayId);
let skey=cluster('hybridnetworking').database('aznwmds').TunnelIntfTable   
| where PreciseTimeStamp > starttime - 1d and PreciseTimeStamp < endtime
| where VnetId in (gatewayvNetid)
| distinct ServiceKey;
let circuitidname=cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp > starttime - 1d and PreciseTimeStamp < endtime
| where AzureServiceKey in (skey)
| distinct AzureServiceKey, CircuitName;
let LatestAdjTableVersion=cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime - 7d  and TIMESTAMP <= endtime
| where GatewayId in~ (gatewayId)
| where RoleInstance == "GatewayTenantWorker_IN_0"
| where Message contains "Updated adjacency table to version"
| where Message contains "Adjacency table size"
| project PreciseTimeStamp,RoleInstance, Message
| parse Message with "<BGP> Updated adjacency table to version "TableVersion" (HEX: " HEX ") at time " * ". Adjacency table size: " TableSize
| summarize max(TableVersion);
let PrefixServiceKey=toscalar(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime - 7d  and TIMESTAMP <= endtime + 1d
| where GatewayId in~ (gatewayId)
| where RoleInstance == "GatewayTenantWorker_IN_0"
| where Message contains "NextHopAddress" and Message contains "SourcePeer"
| project PreciseTimeStamp,RoleInstance, Message
| serialize
| extend IsNewAdjacency = iff(Message contains "<BGP> Updated adjacency table to version", 1, 0) 
| extend AdjacencyGroup = row_cumsum(IsNewAdjacency)
| project PreciseTimeStamp,RoleInstance, IsNewAdjacency, AdjacencyGroup, Message
| summarize PreciseTimeStamp = min(PreciseTimeStamp), EndTime= max(PreciseTimeStamp), Message = strcat_array(make_list(Message), "") by AdjacencyGroup,RoleInstance
| project PreciseTimeStamp, RoleInstance,EndTime, AdjacencyGroup, Message
| parse Message with * "<BGP> Updated adjacency table to version "TableVersion": Adjacencies List "ListNumber" of "TotalLists"\n" RouteEntry
//| extend RouteEntry = trim_end('\\n',RouteEntry)
| extend RouteEntry = split(trim_end('\\n',RouteEntry),'\n')
| where TableVersion in (LatestAdjTableVersion)
| project PreciseTimeStamp, RoleInstance,TableVersion, ListNumber, TotalLists,RouteEntry, Message
| summarize PreciseTimeStamp=take_anyif(PreciseTimeStamp, ListNumber == 1), RouteEntry=make_set(RouteEntry) by TableVersion, RoleInstance
| where isnotempty(TableVersion)
| project PreciseTimeStamp, RoleInstance, TableVersion, RouteEntry
| mv-expand SingleRouteEntry = RouteEntry
| extend SingleRouteEntry_str = tostring(SingleRouteEntry)
| extend Prefix = extract(@"^([\d\.\/]+)", 1, SingleRouteEntry_str)
| extend NextHopAddress = extract_all(@"NextHopAddress:\s*([\d\.]+)", SingleRouteEntry_str)
| where isnotempty(Prefix)
| mv-expand NextHopAddress = NextHopAddress
| project PreciseTimeStamp,RoleInstance, TableVersion,Prefix, NextHopAddress=tostring(NextHopAddress)
| join kind=leftouter  GatewayConnectedCircuit on $left.NextHopAddress == $right.TunnelSourceIP
| where RoleInstance == "GatewayTenantWorker_IN_0"
| extend RouteSource=iff(isempty(ServiceKey), "IPSec", "ExpressRoute")
| distinct PreciseTimeStamp=bin(PreciseTimeStamp, 1m),RoleInstance, TableVersion, Prefix,RouteSource,NextHopAddress, CircuitName, ServiceKey,CircuitSubscriptionId=AzureSubscriptionId
| distinct AdjacencyTableUpdateTimeStamp=PreciseTimeStamp, TableVersion,RouteSource, Prefix, ServiceKey,CircuitName, CircuitSubscriptionId
| extend ERCircuitTroubleshootingLink=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubscriptionID=v-",CircuitSubscriptionId,"&p-ExpressRouteCircuitName=v-",CircuitName,"&p-SyslogFilter=all#d7150dfa-a8d2-438d-b97f-6de6b0da282c")
| extend ERCircuitTroubleshootingLink=iff(isnotempty(ServiceKey), ERCircuitTroubleshootingLink, "-")
| where iff(isnull(ErPrefix), true, Prefix in(ErPrefix))
| distinct ServiceKey
| summarize ServicesKey=make_list(ServiceKey)
| extend SKeys=strcat('("', array_strcat(ServicesKey, '","'), '")')
| distinct SKeys
);
let BitsIn_Query = strcat('metricNamespace("Shoebox").metric("BitsInPerSecond").dimensions("ServiceKey", "DeviceName", "PeeringType", "InterfaceName").samplingTypes("Average") | where ServiceKey in ', PrefixServiceKey);
evaluate geneva_metrics_request('AzureERShoeboxProd',BitsIn_Query, starttime, endtime)
| project TimestampUtc, PeeringType, DeviceName, InterfaceName, ServiceKey, Average
| join kind=leftouter circuitidname on $left.ServiceKey == $right.AzureServiceKey
| project TimestampUtc, Circuit=strcat(CircuitName, ":", DeviceName, ":", InterfaceName), Mbps=round(toreal(Average/1000000), 2)
| render timechart


```

### ExpressRoute Circuit Bits Out Utilization(SubInterface) Of Selected Prefix

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let gwname = ErGwName;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let ErPrefix = todynamic(ErOnpremPrefix);
let gatewayvNetid = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct VNetId);
let GatewayConnectedCircuit=cluster('hybridnetworking').database('aznwmds').TunnelIntfTable   
| where PreciseTimeStamp > starttime - 2d and PreciseTimeStamp < endtime
| where VnetId in (gatewayvNetid)
| distinct ServiceKey, TunnelSourceIP=SourceIp,MSEETunnelInterfaceIP=IpAddress
| join kind=leftouter  (cluster('hybridnetworking').database('aznwmds').CircuitTable | where PreciseTimeStamp > starttime - 5d and PreciseTimeStamp < endtime) on $left.ServiceKey == $right.AzureServiceKey
| distinct ServiceKey, AzureSubscriptionId, CircuitName, TunnelSourceIP, MSEETunnelInterfaceIP;
let gatewayId = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 3d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct GatewayId);
let skey=cluster('hybridnetworking').database('aznwmds').TunnelIntfTable   
| where PreciseTimeStamp > starttime - 1d and PreciseTimeStamp < endtime
| where VnetId in (gatewayvNetid)
| distinct ServiceKey;
let circuitidname=cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp > starttime - 1d and PreciseTimeStamp < endtime
| where AzureServiceKey in (skey)
| distinct AzureServiceKey, CircuitName;
let LatestAdjTableVersion=cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime - 7d  and TIMESTAMP <= endtime
| where GatewayId in~ (gatewayId)
| where RoleInstance == "GatewayTenantWorker_IN_0"
| where Message contains "Updated adjacency table to version"
| where Message contains "Adjacency table size"
| project PreciseTimeStamp,RoleInstance, Message
| parse Message with "<BGP> Updated adjacency table to version "TableVersion" (HEX: " HEX ") at time " * ". Adjacency table size: " TableSize
| summarize max(TableVersion);
let PrefixServiceKey=toscalar(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime - 7d  and TIMESTAMP <= endtime + 1d
| where GatewayId in~ (gatewayId)
| where RoleInstance == "GatewayTenantWorker_IN_0"
| where Message contains "NextHopAddress" and Message contains "SourcePeer"
| project PreciseTimeStamp,RoleInstance, Message
| serialize
| extend IsNewAdjacency = iff(Message contains "<BGP> Updated adjacency table to version", 1, 0) 
| extend AdjacencyGroup = row_cumsum(IsNewAdjacency)
| project PreciseTimeStamp,RoleInstance, IsNewAdjacency, AdjacencyGroup, Message
| summarize PreciseTimeStamp = min(PreciseTimeStamp), EndTime= max(PreciseTimeStamp), Message = strcat_array(make_list(Message), "") by AdjacencyGroup,RoleInstance
| project PreciseTimeStamp, RoleInstance,EndTime, AdjacencyGroup, Message
| parse Message with * "<BGP> Updated adjacency table to version "TableVersion": Adjacencies List "ListNumber" of "TotalLists"\n" RouteEntry
//| extend RouteEntry = trim_end('\\n',RouteEntry)
| extend RouteEntry = split(trim_end('\\n',RouteEntry),'\n')
| where TableVersion in (LatestAdjTableVersion)
| project PreciseTimeStamp, RoleInstance,TableVersion, ListNumber, TotalLists,RouteEntry, Message
| summarize PreciseTimeStamp=take_anyif(PreciseTimeStamp, ListNumber == 1), RouteEntry=make_set(RouteEntry) by TableVersion, RoleInstance
| where isnotempty(TableVersion)
| project PreciseTimeStamp, RoleInstance, TableVersion, RouteEntry
| mv-expand SingleRouteEntry = RouteEntry
| extend SingleRouteEntry_str = tostring(SingleRouteEntry)
| extend Prefix = extract(@"^([\d\.\/]+)", 1, SingleRouteEntry_str)
| extend NextHopAddress = extract_all(@"NextHopAddress:\s*([\d\.]+)", SingleRouteEntry_str)
| where isnotempty(Prefix)
| mv-expand NextHopAddress = NextHopAddress
| project PreciseTimeStamp,RoleInstance, TableVersion,Prefix, NextHopAddress=tostring(NextHopAddress)
| join kind=leftouter  GatewayConnectedCircuit on $left.NextHopAddress == $right.TunnelSourceIP
| where RoleInstance == "GatewayTenantWorker_IN_0"
| extend RouteSource=iff(isempty(ServiceKey), "IPSec", "ExpressRoute")
| distinct PreciseTimeStamp=bin(PreciseTimeStamp, 1m),RoleInstance, TableVersion, Prefix,RouteSource,NextHopAddress, CircuitName, ServiceKey,CircuitSubscriptionId=AzureSubscriptionId
| distinct AdjacencyTableUpdateTimeStamp=PreciseTimeStamp, TableVersion,RouteSource, Prefix, ServiceKey,CircuitName, CircuitSubscriptionId
| extend ERCircuitTroubleshootingLink=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubscriptionID=v-",CircuitSubscriptionId,"&p-ExpressRouteCircuitName=v-",CircuitName,"&p-SyslogFilter=all#d7150dfa-a8d2-438d-b97f-6de6b0da282c")
| extend ERCircuitTroubleshootingLink=iff(isnotempty(ServiceKey), ERCircuitTroubleshootingLink, "-")
| where iff(isnull(ErPrefix), true, Prefix in(ErPrefix))
| distinct ServiceKey
| summarize ServicesKey=make_list(ServiceKey)
| extend SKeys=strcat('("', array_strcat(ServicesKey, '","'), '")')
| distinct SKeys
);
let BitsOut_Query = strcat('metricNamespace("Shoebox").metric("BitsOutPerSecond").dimensions("ServiceKey", "DeviceName", "PeeringType", "InterfaceName").samplingTypes("Average") | where ServiceKey in ', PrefixServiceKey);
evaluate geneva_metrics_request('AzureERShoeboxProd', BitsOut_Query, starttime, endtime)
| project TimestampUtc, PeeringType, DeviceName, InterfaceName, ServiceKey, Average
| join kind=leftouter circuitidname on $left.ServiceKey == $right.AzureServiceKey
| project TimestampUtc, Circuit=strcat(CircuitName, ":", DeviceName, ":", InterfaceName), Mbps=round(toreal(Average/1000000), 2)
| render timechart


```

### [ Metrics ] - BGP Availability between CE and MSEE Of Selected Prefix ExpressRoute Circuit  - Low accuracy

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let gwname = ErGwName;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let ErPrefix = todynamic(ErOnpremPrefix);
let gatewayvNetid = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct VNetId);
let GatewayConnectedCircuit=cluster('hybridnetworking').database('aznwmds').TunnelIntfTable   
| where PreciseTimeStamp > starttime - 2d and PreciseTimeStamp < endtime
| where VnetId in (gatewayvNetid)
| distinct ServiceKey, TunnelSourceIP=SourceIp,MSEETunnelInterfaceIP=IpAddress
| join kind=leftouter  (cluster('hybridnetworking').database('aznwmds').CircuitTable | where PreciseTimeStamp > starttime - 5d and PreciseTimeStamp < endtime) on $left.ServiceKey == $right.AzureServiceKey
| distinct ServiceKey, AzureSubscriptionId, CircuitName, TunnelSourceIP, MSEETunnelInterfaceIP;
let gatewayId = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 3d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct GatewayId);
let skey=cluster('hybridnetworking').database('aznwmds').TunnelIntfTable   
| where PreciseTimeStamp > starttime - 1d and PreciseTimeStamp < endtime
| where VnetId in (gatewayvNetid)
| distinct ServiceKey;
let circuitidname=cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp > starttime - 1d and PreciseTimeStamp < endtime
| where AzureServiceKey in (skey)
| distinct AzureServiceKey, CircuitName;
let LatestAdjTableVersion=cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime - 7d  and TIMESTAMP <= endtime
| where GatewayId in~ (gatewayId)
| where RoleInstance == "GatewayTenantWorker_IN_0"
| where Message contains "Updated adjacency table to version"
| where Message contains "Adjacency table size"
| project PreciseTimeStamp,RoleInstance, Message
| parse Message with "<BGP> Updated adjacency table to version "TableVersion" (HEX: " HEX ") at time " * ". Adjacency table size: " TableSize
| summarize max(TableVersion);
let PrefixServiceKey=toscalar(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime - 7d  and TIMESTAMP <= endtime + 1d
| where GatewayId in~ (gatewayId)
| where RoleInstance == "GatewayTenantWorker_IN_0"
| where Message contains "NextHopAddress" and Message contains "SourcePeer"
| project PreciseTimeStamp,RoleInstance, Message
| serialize
| extend IsNewAdjacency = iff(Message contains "<BGP> Updated adjacency table to version", 1, 0) 
| extend AdjacencyGroup = row_cumsum(IsNewAdjacency)
| project PreciseTimeStamp,RoleInstance, IsNewAdjacency, AdjacencyGroup, Message
| summarize PreciseTimeStamp = min(PreciseTimeStamp), EndTime= max(PreciseTimeStamp), Message = strcat_array(make_list(Message), "") by AdjacencyGroup,RoleInstance
| project PreciseTimeStamp, RoleInstance,EndTime, AdjacencyGroup, Message
| parse Message with * "<BGP> Updated adjacency table to version "TableVersion": Adjacencies List "ListNumber" of "TotalLists"\n" RouteEntry
//| extend RouteEntry = trim_end('\\n',RouteEntry)
| extend RouteEntry = split(trim_end('\\n',RouteEntry),'\n')
| where TableVersion in (LatestAdjTableVersion)
| project PreciseTimeStamp, RoleInstance,TableVersion, ListNumber, TotalLists,RouteEntry, Message
| summarize PreciseTimeStamp=take_anyif(PreciseTimeStamp, ListNumber == 1), RouteEntry=make_set(RouteEntry) by TableVersion, RoleInstance
| where isnotempty(TableVersion)
| project PreciseTimeStamp, RoleInstance, TableVersion, RouteEntry
| mv-expand SingleRouteEntry = RouteEntry
| extend SingleRouteEntry_str = tostring(SingleRouteEntry)
| extend Prefix = extract(@"^([\d\.\/]+)", 1, SingleRouteEntry_str)
| extend NextHopAddress = extract_all(@"NextHopAddress:\s*([\d\.]+)", SingleRouteEntry_str)
| where isnotempty(Prefix)
| mv-expand NextHopAddress = NextHopAddress
| project PreciseTimeStamp,RoleInstance, TableVersion,Prefix, NextHopAddress=tostring(NextHopAddress)
| join kind=leftouter  GatewayConnectedCircuit on $left.NextHopAddress == $right.TunnelSourceIP
| where RoleInstance == "GatewayTenantWorker_IN_0"
| extend RouteSource=iff(isempty(ServiceKey), "IPSec", "ExpressRoute")
| distinct PreciseTimeStamp=bin(PreciseTimeStamp, 1m),RoleInstance, TableVersion, Prefix,RouteSource,NextHopAddress, CircuitName, ServiceKey,CircuitSubscriptionId=AzureSubscriptionId
| distinct AdjacencyTableUpdateTimeStamp=PreciseTimeStamp, TableVersion,RouteSource, Prefix, ServiceKey,CircuitName, CircuitSubscriptionId
| extend ERCircuitTroubleshootingLink=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubscriptionID=v-",CircuitSubscriptionId,"&p-ExpressRouteCircuitName=v-",CircuitName,"&p-SyslogFilter=all#d7150dfa-a8d2-438d-b97f-6de6b0da282c")
| extend ERCircuitTroubleshootingLink=iff(isnotempty(ServiceKey), ERCircuitTroubleshootingLink, "-")
| where iff(isnull(ErPrefix), true, Prefix in(ErPrefix))
| distinct ServiceKey
| summarize ServicesKey=make_list(ServiceKey)
| extend SKeys=strcat('("', array_strcat(ServicesKey, '","'), '")')
| distinct SKeys
);
let BGP_Status_Query = strcat('metricNamespace("Shoebox").metric("BgpAvailability").dimensions("Peer", "ServiceKey").samplingTypes("Sum") | where ServiceKey in ', PrefixServiceKey);
evaluate geneva_metrics_request('AzureERShoeboxProd',BGP_Status_Query, starttime, endtime)
| project TimestampUtc, Peer, ServiceKey, Sum
| join kind=leftouter circuitidname on $left.ServiceKey == $right.AzureServiceKey
| project TimestampUtc, Circuit=strcat(CircuitName, "->", Peer), Sum
| render timechart 


```

### BGP Availability between MSEE Of Selected Prefix ExpressRoute Circuit and ErGw - Low accuracy

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let gwname = ErGwName;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let ErPrefix = todynamic(ErOnpremPrefix);
let gatewayvNetid = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct VNetId);
let GatewayConnectedCircuit=cluster('hybridnetworking').database('aznwmds').TunnelIntfTable   
| where PreciseTimeStamp > starttime - 2d and PreciseTimeStamp < endtime
| where VnetId in (gatewayvNetid)
| distinct ServiceKey, TunnelSourceIP=SourceIp,MSEETunnelInterfaceIP=IpAddress
| join kind=leftouter  (cluster('hybridnetworking').database('aznwmds').CircuitTable | where PreciseTimeStamp > starttime - 5d and PreciseTimeStamp < endtime) on $left.ServiceKey == $right.AzureServiceKey
| distinct ServiceKey, AzureSubscriptionId, CircuitName, TunnelSourceIP, MSEETunnelInterfaceIP;
let gatewayId = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 3d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct GatewayId);
let skey=cluster('hybridnetworking').database('aznwmds').TunnelIntfTable   
| where PreciseTimeStamp > starttime - 1d and PreciseTimeStamp < endtime
| where VnetId in (gatewayvNetid)
| distinct ServiceKey;
let circuitidname=cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp > starttime - 1d and PreciseTimeStamp < endtime
| where AzureServiceKey in (skey)
| distinct AzureServiceKey, CircuitName;
let LatestAdjTableVersion=cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime - 7d  and TIMESTAMP <= endtime
| where GatewayId in~ (gatewayId)
| where RoleInstance == "GatewayTenantWorker_IN_0"
| where Message contains "Updated adjacency table to version"
| where Message contains "Adjacency table size"
| project PreciseTimeStamp,RoleInstance, Message
| parse Message with "<BGP> Updated adjacency table to version "TableVersion" (HEX: " HEX ") at time " * ". Adjacency table size: " TableSize
| summarize max(TableVersion);
let PrefixServiceKey=toscalar(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime - 7d  and TIMESTAMP <= endtime + 1d
| where GatewayId in~ (gatewayId)
| where RoleInstance == "GatewayTenantWorker_IN_0"
| where Message contains "NextHopAddress" and Message contains "SourcePeer"
| project PreciseTimeStamp,RoleInstance, Message
| serialize
| extend IsNewAdjacency = iff(Message contains "<BGP> Updated adjacency table to version", 1, 0) 
| extend AdjacencyGroup = row_cumsum(IsNewAdjacency)
| project PreciseTimeStamp,RoleInstance, IsNewAdjacency, AdjacencyGroup, Message
| summarize PreciseTimeStamp = min(PreciseTimeStamp), EndTime= max(PreciseTimeStamp), Message = strcat_array(make_list(Message), "") by AdjacencyGroup,RoleInstance
| project PreciseTimeStamp, RoleInstance,EndTime, AdjacencyGroup, Message
| parse Message with * "<BGP> Updated adjacency table to version "TableVersion": Adjacencies List "ListNumber" of "TotalLists"\n" RouteEntry
//| extend RouteEntry = trim_end('\\n',RouteEntry)
| extend RouteEntry = split(trim_end('\\n',RouteEntry),'\n')
| where TableVersion in (LatestAdjTableVersion)
| project PreciseTimeStamp, RoleInstance,TableVersion, ListNumber, TotalLists,RouteEntry, Message
| summarize PreciseTimeStamp=take_anyif(PreciseTimeStamp, ListNumber == 1), RouteEntry=make_set(RouteEntry) by TableVersion, RoleInstance
| where isnotempty(TableVersion)
| project PreciseTimeStamp, RoleInstance, TableVersion, RouteEntry
| mv-expand SingleRouteEntry = RouteEntry
| extend SingleRouteEntry_str = tostring(SingleRouteEntry)
| extend Prefix = extract(@"^([\d\.\/]+)", 1, SingleRouteEntry_str)
| extend NextHopAddress = extract_all(@"NextHopAddress:\s*([\d\.]+)", SingleRouteEntry_str)
| where isnotempty(Prefix)
| mv-expand NextHopAddress = NextHopAddress
| project PreciseTimeStamp,RoleInstance, TableVersion,Prefix, NextHopAddress=tostring(NextHopAddress)
| join kind=leftouter  GatewayConnectedCircuit on $left.NextHopAddress == $right.TunnelSourceIP
| where RoleInstance == "GatewayTenantWorker_IN_0"
| extend RouteSource=iff(isempty(ServiceKey), "IPSec", "ExpressRoute")
| distinct PreciseTimeStamp=bin(PreciseTimeStamp, 1m),RoleInstance, TableVersion, Prefix,RouteSource,NextHopAddress, CircuitName, ServiceKey,CircuitSubscriptionId=AzureSubscriptionId
| distinct AdjacencyTableUpdateTimeStamp=PreciseTimeStamp, TableVersion,RouteSource, Prefix, ServiceKey,CircuitName, CircuitSubscriptionId
| extend ERCircuitTroubleshootingLink=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubscriptionID=v-",CircuitSubscriptionId,"&p-ExpressRouteCircuitName=v-",CircuitName,"&p-SyslogFilter=all#d7150dfa-a8d2-438d-b97f-6de6b0da282c")
| extend ERCircuitTroubleshootingLink=iff(isnotempty(ServiceKey), ERCircuitTroubleshootingLink, "-")
| where iff(isnull(ErPrefix), true, Prefix in(ErPrefix))
| distinct ServiceKey
| summarize ServicesKey=make_list(ServiceKey)
| extend SKeys=strcat('("', array_strcat(ServicesKey, '","'), '")')
| distinct SKeys
);
let BGP_Status_Query = strcat('metricNamespace("Shoebox").metric("ExpressRouteDashboard").dimensions("GatewayId","DeviceName", "Child1","ServiceKey").samplingTypes("HealthSignal") | where ServiceKey in ', PrefixServiceKey, 'and GatewayId =="',toscalar(gatewayId), '"');
evaluate geneva_metrics_request('AzureERShoeboxProd',BGP_Status_Query, starttime, endtime)
| where Child1 != "PhysicalStatus"
| project TimestampUtc, GatewayInstance=Child1, ServiceKey, DeviceName, HealthSignal
| join kind=leftouter circuitidname on $left.ServiceKey == $right.AzureServiceKey
| project TimestampUtc, Pair=strcat(CircuitName, ":", DeviceName, "<->", GatewayInstance), HealthSignal
| render timechart 


```

### [ Syslog ] - BGP *Flap* Event between CE and MSEE Of Selected Prefix ExpressRoute Circuit

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let gwname = ErGwName;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let ErPrefix = todynamic(ErOnpremPrefix);
let gatewayvNetid = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct VNetId);
let GatewayConnectedCircuit=cluster('hybridnetworking').database('aznwmds').TunnelIntfTable   
| where PreciseTimeStamp > starttime - 2d and PreciseTimeStamp < endtime
| where VnetId in (gatewayvNetid)
| distinct ServiceKey, TunnelSourceIP=SourceIp,MSEETunnelInterfaceIP=IpAddress
| join kind=leftouter  (cluster('hybridnetworking').database('aznwmds').CircuitTable | where PreciseTimeStamp > starttime - 5d and PreciseTimeStamp < endtime) on $left.ServiceKey == $right.AzureServiceKey
| distinct ServiceKey, AzureSubscriptionId, CircuitName, TunnelSourceIP, MSEETunnelInterfaceIP;
let gatewayId = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 3d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct GatewayId);
let skey=cluster('hybridnetworking').database('aznwmds').TunnelIntfTable   
| where PreciseTimeStamp > starttime - 1d and PreciseTimeStamp < endtime
| where VnetId in (gatewayvNetid)
| distinct ServiceKey;
let circuitidname=cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp > starttime - 1d and PreciseTimeStamp < endtime
| where AzureServiceKey in (skey)
| distinct AzureServiceKey, CircuitName;
let LatestAdjTableVersion=cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime - 7d  and TIMESTAMP <= endtime
| where GatewayId in~ (gatewayId)
| where RoleInstance == "GatewayTenantWorker_IN_0"
| where Message contains "Updated adjacency table to version"
| where Message contains "Adjacency table size"
| project PreciseTimeStamp,RoleInstance, Message
| parse Message with "<BGP> Updated adjacency table to version "TableVersion" (HEX: " HEX ") at time " * ". Adjacency table size: " TableSize
| summarize max(TableVersion);
let PrefixServiceKey=cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime - 7d  and TIMESTAMP <= endtime + 1d
| where GatewayId in~ (gatewayId)
| where RoleInstance == "GatewayTenantWorker_IN_0"
| where Message contains "NextHopAddress" and Message contains "SourcePeer"
| project PreciseTimeStamp,RoleInstance, Message
| serialize
| extend IsNewAdjacency = iff(Message contains "<BGP> Updated adjacency table to version", 1, 0) 
| extend AdjacencyGroup = row_cumsum(IsNewAdjacency)
| project PreciseTimeStamp,RoleInstance, IsNewAdjacency, AdjacencyGroup, Message
| summarize PreciseTimeStamp = min(PreciseTimeStamp), EndTime= max(PreciseTimeStamp), Message = strcat_array(make_list(Message), "") by AdjacencyGroup,RoleInstance
| project PreciseTimeStamp, RoleInstance,EndTime, AdjacencyGroup, Message
| parse Message with * "<BGP> Updated adjacency table to version "TableVersion": Adjacencies List "ListNumber" of "TotalLists"\n" RouteEntry
//| extend RouteEntry = trim_end('\\n',RouteEntry)
| extend RouteEntry = split(trim_end('\\n',RouteEntry),'\n')
| where TableVersion in (LatestAdjTableVersion)
| project PreciseTimeStamp, RoleInstance,TableVersion, ListNumber, TotalLists,RouteEntry, Message
| summarize PreciseTimeStamp=take_anyif(PreciseTimeStamp, ListNumber == 1), RouteEntry=make_set(RouteEntry) by TableVersion, RoleInstance
| where isnotempty(TableVersion)
| project PreciseTimeStamp, RoleInstance, TableVersion, RouteEntry
| mv-expand SingleRouteEntry = RouteEntry
| extend SingleRouteEntry_str = tostring(SingleRouteEntry)
| extend Prefix = extract(@"^([\d\.\/]+)", 1, SingleRouteEntry_str)
| extend NextHopAddress = extract_all(@"NextHopAddress:\s*([\d\.]+)", SingleRouteEntry_str)
| where isnotempty(Prefix)
| mv-expand NextHopAddress = NextHopAddress
| project PreciseTimeStamp,RoleInstance, TableVersion,Prefix, NextHopAddress=tostring(NextHopAddress)
| join kind=leftouter  GatewayConnectedCircuit on $left.NextHopAddress == $right.TunnelSourceIP
| where RoleInstance == "GatewayTenantWorker_IN_0"
| extend RouteSource=iff(isempty(ServiceKey), "IPSec", "ExpressRoute")
| distinct PreciseTimeStamp=bin(PreciseTimeStamp, 1m),RoleInstance, TableVersion, Prefix,RouteSource,NextHopAddress, CircuitName, ServiceKey,CircuitSubscriptionId=AzureSubscriptionId
| distinct AdjacencyTableUpdateTimeStamp=PreciseTimeStamp, TableVersion,RouteSource, Prefix, ServiceKey,CircuitName, CircuitSubscriptionId
| extend ERCircuitTroubleshootingLink=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubscriptionID=v-",CircuitSubscriptionId,"&p-ExpressRouteCircuitName=v-",CircuitName,"&p-SyslogFilter=all#d7150dfa-a8d2-438d-b97f-6de6b0da282c")
| extend ERCircuitTroubleshootingLink=iff(isnotempty(ServiceKey), ERCircuitTroubleshootingLink, "-")
| where iff(isnull(ErPrefix), true, Prefix in(ErPrefix))
| distinct ServiceKey
;
let MSEEDevices=cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d
| where AzureServiceKey in (PrefixServiceKey)
| distinct PrimaryDeviceName, SecondaryDeviceName
| extend DeviceList = pack_array(PrimaryDeviceName, SecondaryDeviceName)
| mv-expand DeviceName = DeviceList
| project DeviceName;
let Vrf=cluster("Hybridnetworking").database("aznwmds").VrfTable | where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d
| where ServiceKey in (PrefixServiceKey)
| distinct VrfId = tolower(replace_string(VrfId, "-", ""));
cluster('azphynet.kusto.windows.net').database('azdhmds').SyslogData
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where Device in (MSEEDevices)
| where Message contains "BGP"
| extend AristaVRF = extract(@"VRF\s+([A-Za-z0-9-]+)", 1, Message)
| extend JuniperVRF = extract(@"instance\s+([A-Za-z0-9-]+)", 1, Message)
| extend ASN = extract(@"AS\s+(\d+)", 1, Message)
| extend VRF=tolower(iif(isempty(AristaVRF),JuniperVRF,AristaVRF))
| where VRF in (Vrf)
| where ASN != "65515"
| project PreciseTimeStamp, Device,ASN, VRF, EventName,Message
| summarize count() by bin(PreciseTimeStamp, 1m), EventName
| render columnchart 
```

### [ Syslog ] - BGP Flap Event between [CE|ErGw] and MSEE Of Selected Prefix ExpressRoute Circuit

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let gwname = ErGwName;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let ErPrefix = todynamic(ErOnpremPrefix);
let gatewayvNetid = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct VNetId);
let GatewayConnectedCircuit=cluster('hybridnetworking').database('aznwmds').TunnelIntfTable   
| where PreciseTimeStamp > starttime - 2d and PreciseTimeStamp < endtime
| where VnetId in (gatewayvNetid)
| distinct ServiceKey, TunnelSourceIP=SourceIp,MSEETunnelInterfaceIP=IpAddress
| join kind=leftouter  (cluster('hybridnetworking').database('aznwmds').CircuitTable | where PreciseTimeStamp > starttime - 5d and PreciseTimeStamp < endtime) on $left.ServiceKey == $right.AzureServiceKey
| distinct ServiceKey, AzureSubscriptionId, CircuitName, TunnelSourceIP, MSEETunnelInterfaceIP;
let gatewayId = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 3d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct GatewayId);
let GatewayCA=cluster('hybridnetworking.kusto.windows.net').database('aznwmds').ErVpnGwToContainerId
| where PreciseTimeStamp >= starttime - 2h and PreciseTimeStamp <= endtime
| where GatewayId in (gatewayId)
| distinct tostring(CA);
let skey=cluster('hybridnetworking').database('aznwmds').TunnelIntfTable   
| where PreciseTimeStamp > starttime - 1d and PreciseTimeStamp < endtime
| where VnetId in (gatewayvNetid)
| distinct ServiceKey;
let circuitidname=cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp > starttime - 1d and PreciseTimeStamp < endtime
| where AzureServiceKey in (skey)
| distinct AzureServiceKey, CircuitName;
let LatestAdjTableVersion=cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime - 7d  and TIMESTAMP <= endtime
| where GatewayId in~ (gatewayId)
| where RoleInstance == "GatewayTenantWorker_IN_0"
| where Message contains "Updated adjacency table to version"
| where Message contains "Adjacency table size"
| project PreciseTimeStamp,RoleInstance, Message
| parse Message with "<BGP> Updated adjacency table to version "TableVersion" (HEX: " HEX ") at time " * ". Adjacency table size: " TableSize
| summarize max(TableVersion);
let PrefixServiceKey=cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime - 7d  and TIMESTAMP <= endtime + 1d
| where GatewayId in~ (gatewayId)
| where RoleInstance == "GatewayTenantWorker_IN_0"
| where Message contains "NextHopAddress" and Message contains "SourcePeer"
| project PreciseTimeStamp,RoleInstance, Message
| serialize
| extend IsNewAdjacency = iff(Message contains "<BGP> Updated adjacency table to version", 1, 0) 
| extend AdjacencyGroup = row_cumsum(IsNewAdjacency)
| project PreciseTimeStamp,RoleInstance, IsNewAdjacency, AdjacencyGroup, Message
| summarize PreciseTimeStamp = min(PreciseTimeStamp), EndTime= max(PreciseTimeStamp), Message = strcat_array(make_list(Message), "") by AdjacencyGroup,RoleInstance
| project PreciseTimeStamp, RoleInstance,EndTime, AdjacencyGroup, Message
| parse Message with * "<BGP> Updated adjacency table to version "TableVersion": Adjacencies List "ListNumber" of "TotalLists"\n" RouteEntry
//| extend RouteEntry = trim_end('\\n',RouteEntry)
| extend RouteEntry = split(trim_end('\\n',RouteEntry),'\n')
| where TableVersion in (LatestAdjTableVersion)
| project PreciseTimeStamp, RoleInstance,TableVersion, ListNumber, TotalLists,RouteEntry, Message
| summarize PreciseTimeStamp=take_anyif(PreciseTimeStamp, ListNumber == 1), RouteEntry=make_set(RouteEntry) by TableVersion, RoleInstance
| where isnotempty(TableVersion)
| project PreciseTimeStamp, RoleInstance, TableVersion, RouteEntry
| mv-expand SingleRouteEntry = RouteEntry
| extend SingleRouteEntry_str = tostring(SingleRouteEntry)
| extend Prefix = extract(@"^([\d\.\/]+)", 1, SingleRouteEntry_str)
| extend NextHopAddress = extract_all(@"NextHopAddress:\s*([\d\.]+)", SingleRouteEntry_str)
| where isnotempty(Prefix)
| mv-expand NextHopAddress = NextHopAddress
| project PreciseTimeStamp,RoleInstance, TableVersion,Prefix, NextHopAddress=tostring(NextHopAddress)
| join kind=leftouter  GatewayConnectedCircuit on $left.NextHopAddress == $right.TunnelSourceIP
| where RoleInstance == "GatewayTenantWorker_IN_0"
| extend RouteSource=iff(isempty(ServiceKey), "IPSec", "ExpressRoute")
| distinct PreciseTimeStamp=bin(PreciseTimeStamp, 1m),RoleInstance, TableVersion, Prefix,RouteSource,NextHopAddress, CircuitName, ServiceKey,CircuitSubscriptionId=AzureSubscriptionId
| distinct AdjacencyTableUpdateTimeStamp=PreciseTimeStamp, TableVersion,RouteSource, Prefix, ServiceKey,CircuitName, CircuitSubscriptionId
| extend ERCircuitTroubleshootingLink=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubscriptionID=v-",CircuitSubscriptionId,"&p-ExpressRouteCircuitName=v-",CircuitName,"&p-SyslogFilter=all#d7150dfa-a8d2-438d-b97f-6de6b0da282c")
| extend ERCircuitTroubleshootingLink=iff(isnotempty(ServiceKey), ERCircuitTroubleshootingLink, "-")
| where iff(isnull(ErPrefix), true, Prefix in(ErPrefix))
| distinct ServiceKey
;
let MSEEDevices=cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d
| where AzureServiceKey in (PrefixServiceKey)
| distinct PrimaryDeviceName, SecondaryDeviceName
| extend DeviceList = pack_array(PrimaryDeviceName, SecondaryDeviceName)
| mv-expand DeviceName = DeviceList
| project DeviceName;
let Vrf=cluster("Hybridnetworking").database("aznwmds").VrfTable | where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d
| where ServiceKey in (PrefixServiceKey)
| distinct VrfId = tolower(replace_string(VrfId, "-", ""));
let CircuitNameVRF=cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d
| where AzureServiceKey in (PrefixServiceKey)
| extend ServiceKey=AzureServiceKey
| join kind=leftouter (cluster("Hybridnetworking").database("aznwmds").SubIntfTable | where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d) on ServiceKey
| distinct SubscriptionId, CircuitName, ServiceKey, VrfId, VRF = tolower(replace_string(VrfId, "-", ""));
cluster('azphynet.kusto.windows.net').database('azdhmds').SyslogData
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where Device in (MSEEDevices)
| where Message contains "BGP"
| extend AristaVRF = extract(@"VRF\s+([A-Za-z0-9-]+)", 1, Message)
| extend JuniperVRF = extract(@"instance\s+([A-Za-z0-9-]+)", 1, Message)
| extend ASN = extract(@"AS\s+(\d+)", 1, Message)
| extend BGP_Peer = extract(@"(\d{1,3}(?:\.\d{1,3}){3})", 1, Message)
| extend VRF=tolower(iif(isempty(AristaVRF),JuniperVRF,AristaVRF))
| where VRF in (Vrf)
| where ASN != 65515 or (ASN == 65515 and BGP_Peer in (GatewayCA))
| project PreciseTimeStamp, Device,VRF, ASN, BGP_Peer,EventName,Message
| join kind=leftouter  CircuitNameVRF on VRF
| project PreciseTimeStamp,SubscriptionId, CircuitName,Device,ASN,BGP_Peer, EventName,Message
```

### [ Syslog ] - BGP *Flap* Event between MSEE Of Selected Prefix ExpressRoute Circuit and ErGw

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let gwname = ErGwName;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let ErPrefix = todynamic(ErOnpremPrefix);
let gatewayvNetid = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct VNetId);
let GatewayConnectedCircuit=cluster('hybridnetworking').database('aznwmds').TunnelIntfTable   
| where PreciseTimeStamp > starttime - 2d and PreciseTimeStamp < endtime
| where VnetId in (gatewayvNetid)
| distinct ServiceKey, TunnelSourceIP=SourceIp,MSEETunnelInterfaceIP=IpAddress
| join kind=leftouter  (cluster('hybridnetworking').database('aznwmds').CircuitTable | where PreciseTimeStamp > starttime - 5d and PreciseTimeStamp < endtime) on $left.ServiceKey == $right.AzureServiceKey
| distinct ServiceKey, AzureSubscriptionId, CircuitName, TunnelSourceIP, MSEETunnelInterfaceIP;
let gatewayId = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 3d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == gwname
| distinct GatewayId);
let GatewayCA=cluster('hybridnetworking.kusto.windows.net').database('aznwmds').ErVpnGwToContainerId
| where PreciseTimeStamp >= starttime - 2h and PreciseTimeStamp <= endtime
| where GatewayId in (gatewayId)
| distinct tostring(CA);
let skey=cluster('hybridnetworking').database('aznwmds').TunnelIntfTable   
| where PreciseTimeStamp > starttime - 1d and PreciseTimeStamp < endtime
| where VnetId in (gatewayvNetid)
| distinct ServiceKey;
let circuitidname=cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp > starttime - 1d and PreciseTimeStamp < endtime
| where AzureServiceKey in (skey)
| distinct AzureServiceKey, CircuitName;
let LatestAdjTableVersion=cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime - 7d  and TIMESTAMP <= endtime
| where GatewayId in~ (gatewayId)
| where RoleInstance == "GatewayTenantWorker_IN_0"
| where Message contains "Updated adjacency table to version"
| where Message contains "Adjacency table size"
| project PreciseTimeStamp,RoleInstance, Message
| parse Message with "<BGP> Updated adjacency table to version "TableVersion" (HEX: " HEX ") at time " * ". Adjacency table size: " TableSize
| summarize max(TableVersion);
let PrefixServiceKey=cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime - 7d  and TIMESTAMP <= endtime + 1d
| where GatewayId in~ (gatewayId)
| where RoleInstance == "GatewayTenantWorker_IN_0"
| where Message contains "NextHopAddress" and Message contains "SourcePeer"
| project PreciseTimeStamp,RoleInstance, Message
| serialize
| extend IsNewAdjacency = iff(Message contains "<BGP> Updated adjacency table to version", 1, 0) 
| extend AdjacencyGroup = row_cumsum(IsNewAdjacency)
| project PreciseTimeStamp,RoleInstance, IsNewAdjacency, AdjacencyGroup, Message
| summarize PreciseTimeStamp = min(PreciseTimeStamp), EndTime= max(PreciseTimeStamp), Message = strcat_array(make_list(Message), "") by AdjacencyGroup,RoleInstance
| project PreciseTimeStamp, RoleInstance,EndTime, AdjacencyGroup, Message
| parse Message with * "<BGP> Updated adjacency table to version "TableVersion": Adjacencies List "ListNumber" of "TotalLists"\n" RouteEntry
//| extend RouteEntry = trim_end('\\n',RouteEntry)
| extend RouteEntry = split(trim_end('\\n',RouteEntry),'\n')
| where TableVersion in (LatestAdjTableVersion)
| project PreciseTimeStamp, RoleInstance,TableVersion, ListNumber, TotalLists,RouteEntry, Message
| summarize PreciseTimeStamp=take_anyif(PreciseTimeStamp, ListNumber == 1), RouteEntry=make_set(RouteEntry) by TableVersion, RoleInstance
| where isnotempty(TableVersion)
| project PreciseTimeStamp, RoleInstance, TableVersion, RouteEntry
| mv-expand SingleRouteEntry = RouteEntry
| extend SingleRouteEntry_str = tostring(SingleRouteEntry)
| extend Prefix = extract(@"^([\d\.\/]+)", 1, SingleRouteEntry_str)
| extend NextHopAddress = extract_all(@"NextHopAddress:\s*([\d\.]+)", SingleRouteEntry_str)
| where isnotempty(Prefix)
| mv-expand NextHopAddress = NextHopAddress
| project PreciseTimeStamp,RoleInstance, TableVersion,Prefix, NextHopAddress=tostring(NextHopAddress)
| join kind=leftouter  GatewayConnectedCircuit on $left.NextHopAddress == $right.TunnelSourceIP
| where RoleInstance == "GatewayTenantWorker_IN_0"
| extend RouteSource=iff(isempty(ServiceKey), "IPSec", "ExpressRoute")
| distinct PreciseTimeStamp=bin(PreciseTimeStamp, 1m),RoleInstance, TableVersion, Prefix,RouteSource,NextHopAddress, CircuitName, ServiceKey,CircuitSubscriptionId=AzureSubscriptionId
| distinct AdjacencyTableUpdateTimeStamp=PreciseTimeStamp, TableVersion,RouteSource, Prefix, ServiceKey,CircuitName, CircuitSubscriptionId
| extend ERCircuitTroubleshootingLink=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubscriptionID=v-",CircuitSubscriptionId,"&p-ExpressRouteCircuitName=v-",CircuitName,"&p-SyslogFilter=all#d7150dfa-a8d2-438d-b97f-6de6b0da282c")
| extend ERCircuitTroubleshootingLink=iff(isnotempty(ServiceKey), ERCircuitTroubleshootingLink, "-")
| where iff(isnull(ErPrefix), true, Prefix in(ErPrefix))
| distinct ServiceKey
;
let MSEEDevices=cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d
| where AzureServiceKey in (PrefixServiceKey)
| distinct PrimaryDeviceName, SecondaryDeviceName
| extend DeviceList = pack_array(PrimaryDeviceName, SecondaryDeviceName)
| mv-expand DeviceName = DeviceList
| project DeviceName;
let Vrf=cluster("Hybridnetworking").database("aznwmds").VrfTable | where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d
| where ServiceKey in (PrefixServiceKey)
| distinct VrfId = tolower(replace_string(VrfId, "-", ""));
cluster('azphynet.kusto.windows.net').database('azdhmds').SyslogData
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where Device in (MSEEDevices)
| where Message contains "BGP"
| extend AristaVRF = extract(@"VRF\s+([A-Za-z0-9-]+)", 1, Message)
| extend JuniperVRF = extract(@"instance\s+([A-Za-z0-9-]+)", 1, Message)
| extend ErGw_Peer = extract(@"(\d{1,3}(?:\.\d{1,3}){3})", 1, Message)
| extend ASN = extract(@"AS\s+(\d+)", 1, Message)
| extend VRF=tolower(iif(isempty(AristaVRF),JuniperVRF,AristaVRF))
| where VRF in (Vrf)
| where ErGw_Peer in (GatewayCA)
| where ASN == "65515"
| project PreciseTimeStamp, Device,ASN, VRF, EventName,Message
| summarize count() by bin(PreciseTimeStamp, 1m), EventName
| render columnchart 
```

