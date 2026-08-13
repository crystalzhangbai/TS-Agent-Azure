---
description: KQL queries for Azure Firewall diagnostics: rule processing, threat intel, SNAT, network/application rules.
---

# Azure Firewall Kusto Queries

> Source: Azure Networking B01 Dashboard (aka.ms/b01)
> Pages: Azure Firewall

## Azure Firewall

### Azure Firewalls under this subscription

```kql
cluster("hybridnetworking.kusto.windows.net").database('GatewayManager').SecureGatewayTable
| where CustomerSubscriptionId == SubscriptionID
| extend ResourceURI = strcat('/subscriptions/',CustomerSubscriptionId,'/resourceGroups/',ResourceGroup,'/providers/Microsoft.Network/azureFirewalls/',GatewayName)
| extend FirewallvNet=split(SubnetId, "/subnets/AzureFirewallSubnet")[0]
| project AzureFirewallName=GatewayName, Location, SkuName, SkuTier,GatewayTenantVersion=Version, ResourceURI, FirewallPolicyId,FirewallvNet
```

### Azure Firewall Dashboard

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let min = datetime_diff('minute',endtime,starttime);
cluster("hybridnetworking.kusto.windows.net").database('GatewayManager').SecureGatewayTable
| where CustomerSubscriptionId == SubscriptionID
| where GatewayName == FirewallName
| extend ResourceURI = strcat('/subscriptions/',CustomerSubscriptionId,'/resourceGroups/',ResourceGroup,'/providers/Microsoft.Network/azureFirewalls/',GatewayName)
| extend FirewallvNet=tostring(split(SubnetId, "/subnets/AzureFirewallSubnet")[0])
| project AzureFirewallName=GatewayName, Location, SkuName, SkuTier,GatewayTenantVersion=Version, ResourceURI, FirewallPolicyId,FirewallvNet, GatewayId
| extend ResourceGroupName=strcat("ARMRG-", toupper(GatewayId))
| join cluster('fimpubameprodwestus.westus.kusto.windows.net').database('AzureGraphMigration').LogicalCompute_VirtualMachineNRT on ResourceGroupName
| extend VMScaleSetId=tolower(VMSSArmId)
| extend AzureFirewallILB=tolower(strcat(split(VMScaleSetId, "microsoft.compute/virtualmachinescalesets/")[0], "microsoft.network/loadbalancers/",split(VMScaleSetId,"microsoft.compute/virtualmachinescalesets/")[1], "lb"))
| extend AzureFirewallELB=tolower(strcat(split(VMScaleSetId, "microsoft.compute/virtualmachinescalesets/")[0], "microsoft.network/loadbalancers/",split(VMScaleSetId,"microsoft.compute/virtualmachinescalesets/")[1], "publiclb"))
| extend DataplaneMetrics=strcat("https://portal.microsoftgeneva.com/s/DF5CBDF1?overrides=[{%22query%22:%22//*[id='ResourceId']%22,%22key%22:%22value%22,%22replacement%22:%22",ResourceURI,"%22},{%22query%22:%22//*[id='Hostname']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='Region']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id=%5c%22tenant%5c%22]%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[comparand=%5c%22Tenant%5c%22]%22,%22key%22:%22values%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='rid']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='GatewayId']%22,%22key%22:%22value%22,%22replacement%22:%22%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend PerformanceMetrics=strcat("https://portal.microsoftgeneva.com/s/B4A3E93E?overrides=[{%22query%22:%22//*[id='ResourceId']%22,%22key%22:%22value%22,%22replacement%22:%22",ResourceURI, "%22},{%22query%22:%22//*[id='GatewayId']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='Region']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='Hostname']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='GatewayVersion']%22,%22key%22:%22value%22,%22replacement%22:%22%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend DataplaneLogs=strcat("https://portal.microsoftgeneva.com/logs/dgrep?be=DGrep&time=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'), "Z&offset=", min, "&offsetUnit=Minutes&UTC=true&ep=Diagnostics%20PROD&ns=GSAGW&en=AzureMonitor&scopingConditions=[[%22Tenant%22,%22",ResourceURI,"%22]]&conditions=[]&clientQuery=orderby%20PreciseTimeStamp%20asc&aggregatesVisible=true&aggregates=[%22Count%20by%20ActivityId%22]&chartEditorVisible=true&chartType=line&chartLayers=[[%22New%20Layer%22,%22%22]]%20")
| extend RuntimeLog=strcat("https://portal.microsoftgeneva.com/logs/dgrep?be=DGrep&time=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'), "Z&offset=", min, "&offsetUnit=Minutes&UTC=true&ep=Diagnostics%20PROD&ns=GSAGW&en=Runtime&scopingConditions=[[%22Tenant%22,%22",ResourceURI,"%22]]&conditions=[]&clientQuery=orderby%20PreciseTimeStamp%20asc&aggregatesVisible=true&aggregates=[%22Count%20by%20ActivityId%22]&chartEditorVisible=true&chartType=line&chartLayers=[[%22New%20Layer%22,%22%22]]%20")
| extend InterComponentDashboard=strcat("https://portal.microsoftgeneva.com/s/88416F1E?overrides=[{%22query%22:%22//*[id='Hostname']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='Region']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='ResourceId']%22,%22key%22:%22value%22,%22replacement%22:%22", ResourceURI, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| distinct AzureFirewallName, GatewayId, Location, SkuName, SkuTier, GatewayTenantVersion,ResourceURI, FirewallPolicyId, FirewallvNet,  AzureFirewallELB,AzureFirewallILB,VMScaleSetId=tolower(VMScaleSetId),DataplaneMetrics,PerformanceMetrics,DataplaneLogs,RuntimeLog,InterComponentDashboard
| distinct AzureFirewallName, GatewayId, Location, SkuName, SkuTier, GatewayTenantVersion,ResourceId=ResourceURI, FirewallPolicyId, FirewallvNet, VMScaleSetId=tolower(VMScaleSetId),DataplaneMetrics,PerformanceMetrics,DataplaneLogs,RuntimeLog,InterComponentDashboard
| evaluate narrow()
| project Name=Column, Value
```

### Firewall Instance Infra dashboard

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let FirewallGatewayId=materialize(
cluster("hybridnetworking.kusto.windows.net").database('GatewayManager').SecureGatewayTable
| where CustomerSubscriptionId == SubscriptionID
| where GatewayName == FirewallName
| distinct GatewayId);
cluster("hybridnetworking.kusto.windows.net").database('aznwmds').SecureGatewayToContainerId
| where PreciseTimeStamp >= starttime - 2h and PreciseTimeStamp <= endtime
| where GatewayId in (FirewallGatewayId)
| project PreciseTimeStamp, RoleInstanceName, Region, AvailabilityZone, DataCenterName, Cluster, NodeId, ContainerId, VMSize
| distinct RoleInstanceName, Region, AvailabilityZone, DataCenterName, Tenant=Cluster, nodeId=NodeId, containerId=ContainerId, VMSize
//| join kind=inner cluster('aznwsdn').database("aznwmds").MdmVfpVnetAccountMaps on $left.Tenant == $right.Cluster
| join kind=inner cluster("azurehn.kusto.windows.net").database("Azurehn").MdmVfpVnetAccountMaps() on $left.Tenant == $right.Cluster
| extend VFPDashBoard=strcat("https://portal.microsoftgeneva.com/dashboard/VfpMDM/dpop/SupportDashboard?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend VFPDropDashBoard=strcat("https://portal.microsoftgeneva.com/dashboard/VfpMDM/dpop/dropsDashboard?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend SupportDashBoard=strcat("https://portal.microsoftgeneva.com/s/9FDB0A67?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend DropDashBoard=strcat("https://portal.microsoftgeneva.com/dashboard/VfpMDM/dpop/dropsDashboard?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend FPGADashboard=strcat("https://portal.microsoftgeneva.com/dashboard/VfpMDM/DatapathDashboards/FpgaDashboardGft/FpgaDashboardGftv3?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend InvestigateNode=strcat("https://dataexplorer.azure.com/dashboards/bea4ccac-baf1-45f3-b160-533232cbfdaa?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH-mm-ss'),"Z&p-_endTime=", format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime, 'HH-mm-ss'), "Z&p-_NodeId=v-", nodeId, "&p-_ContainerId=v-", containerId, "&p-_ICMId=all#2f4843e6-c1e5-4564-ad27-cde71cebc7c7")
| extend ASIHostNode=strcat("https://azureserviceinsights.trafficmanager.net/view/services/Azure%20Host/pages/Azure%20Host%20Node?nodeId=",nodeId,"&globalFrom=",format_datetime(starttime, 'yyyy-MM-dd'),"T",format_datetime(starttime, 'HH'), "%3A",format_datetime(starttime, 'mm'), "%3A51.000Z&globalTo=",format_datetime(endtime, 'yyyy-MM-dd'),"T",format_datetime(endtime, 'HH'), "%3A",format_datetime(endtime, 'mm'),"%3A51.000Z")
| extend NetVMA=strcat("https://aka.ms/netvma/?destValue=&pathQuery=false&sdnPath=false&showPingMesh=false&startTime=", format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'), "&endTime=", format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime, 'HH:mm:ss'), "&value=", containerId)
| extend PerVMAvailability=strcat("https://portal.microsoftgeneva.com/s/A03537E6?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VNETAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend PerProcessorPNICDashboard=strcat("https://portal.microsoftgeneva.com/dashboard/VfpMDM/DatapathDashboards/PerProcessorNdisDashboard?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend VFPFullRule=strcat("https://portal.microsoftgeneva.com/?page=actions&acisEndpoint=Public&managementOpen=false&automatedTestsReportOpen=false&tab=Extensions&acisRolloutEndpoint=Public&selectedNodeType=3&extension=SupportabilityFabric&group=Fabric%20Operations&operationId=GetVfpFiltersForContainer&operationName=Get%20VFP%20Filters%20(ACL%20and%20VNET)%20programmed%20on%20containers&inputMode=single&params={%22smefabrichostparam%22:%22", Cluster, "%22,%22smenodeidparam%22:%22", nodeId, "%22,%22smecontaineridparam%22:%22", containerId,"%22,%22smemacaddressparam%22:%22%22,%22smelayerparam%22:%22%22,%22smegroupparam%22:%22%22,%22smeruleparam%22:%22%22,%22smenatpoolparam%22:%22%22,%22smenatrangeparam%22:%22%22,%22smespaceparam%22:%22%22,%22smemappingparam%22:%22%22,%22smevfpfiltercommandparam%22:%22list-rule%22,%22smevfpfilteroptionsparam%22:%22%22}&actionEndpoint=Production&genevatraceguid=9964f627-a5ca-435a-a749-e60f4a56c7f0")
| extend ListUnifiedFlow=strcat("https://portal.microsoftgeneva.com/?page=actions&acisEndpoint=Public&managementOpen=false&automatedTestsReportOpen=false&tab=Extensions&acisRolloutEndpoint=Public&selectedNodeType=3&extension=SupportabilityFabric&group=Fabric%20Operations&operationId=GetVfpFiltersForContainer&operationName=Get%20VFP%20Filters%20(ACL%20and%20VNET)%20programmed%20on%20containers&inputMode=single&params={%22smefabrichostparam%22:%22", Cluster, "%22,%22smenodeidparam%22:%22", nodeId, "%22,%22smecontaineridparam%22:%22", containerId,"%22,%22smemacaddressparam%22:%22%22,%22smelayerparam%22:%22%22,%22smegroupparam%22:%22%22,%22smeruleparam%22:%22%22,%22smenatpoolparam%22:%22%22,%22smenatrangeparam%22:%22%22,%22smespaceparam%22:%22%22,%22smemappingparam%22:%22%22,%22smevfpfiltercommandparam%22:%22list-unified-flow%22,%22smevfpfilteroptionsparam%22:%22%22}&actionEndpoint=Production&genevatraceguid=9964f627-a5ca-435a-a749-e60f4a56c7f0")
| extend VMdash=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubIdOrContainerId=v-",containerId,"&&p-VMName=v-ContaizerId&p-DataPathScan=v-No#8ed1e2a2-d979-401b-9609-7580ad07ccd1")
| distinct RoleInstanceName, VMSize,Region, AvailabilityZone, DataCenterName, Cluster, nodeId, containerId, VMdash,VFPDashBoard, VFPDropDashBoard, SupportDashBoard, DropDashBoard, FPGADashboard, InvestigateNode, ASIHostNode, NetVMA, PerVMAvailability, PerProcessorPNICDashboard,VFPFullRule, ListUnifiedFlow


```

### Azure Firewall LB Dashboard

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let min = datetime_diff('minute',endtime,starttime);
let AzFwInsSub=toscalar(cluster("hybridnetworking.kusto.windows.net").database('GatewayManager').SecureGatewayTable
| where CustomerSubscriptionId == SubscriptionID
| where GatewayName == FirewallName
| extend ResourceURI = strcat('/subscriptions/',CustomerSubscriptionId,'/resourceGroups/',ResourceGroup,'/providers/Microsoft.Network/azureFirewalls/',GatewayName)
| extend FirewallvNet=tostring(split(SubnetId, "/subnets/AzureFirewallSubnet")[0])
| project AzureFirewallName=GatewayName, Location, SkuName, SkuTier,GatewayTenantVersion=Version, ResourceURI, FirewallPolicyId,FirewallvNet, GatewayId
| extend ResourceGroupName=strcat("ARMRG-", toupper(GatewayId))
| join cluster('fimpubameprodwestus.westus.kusto.windows.net').database('AzureGraphMigration').LogicalCompute_VirtualMachineNRT on ResourceGroupName
| distinct VMScaleSetId=tolower(VMSSArmId)
| distinct AzFwInstanceSub=tostring(split(VMScaleSetId, "/")[2]));
let AzFwInsRG=toscalar(cluster("hybridnetworking.kusto.windows.net").database('GatewayManager').SecureGatewayTable
| where CustomerSubscriptionId == SubscriptionID
| where GatewayName == FirewallName
| extend ResourceURI = strcat('/subscriptions/',CustomerSubscriptionId,'/resourceGroups/',ResourceGroup,'/providers/Microsoft.Network/azureFirewalls/',GatewayName)
| extend FirewallvNet=tostring(split(SubnetId, "/subnets/AzureFirewallSubnet")[0])
| project AzureFirewallName=GatewayName, Location, SkuName, SkuTier,GatewayTenantVersion=Version, ResourceURI, FirewallPolicyId,FirewallvNet, GatewayId
| extend ResourceGroupName=strcat("ARMRG-", toupper(GatewayId))
| join cluster('fimpubameprodwestus.westus.kusto.windows.net').database('AzureGraphMigration').LogicalCompute_VirtualMachineNRT on ResourceGroupName
| distinct VMScaleSetId=tolower(VMSSArmId)
| distinct AzFwInstanceResourceGroup=tostring(split(VMScaleSetId, "/")[4]));
cluster('argwus2nrpone.westus2').database('AzureResourceGraph').Resources 
| where timestamp >= starttime - 2d and timestamp <= endtime
| where type == "microsoft.network/loadbalancers"
| where subscriptionId == AzFwInsSub
| distinct id,subscriptionId,LBRG=tostring(split(id, "/")[4]), LoadBalancerArmId=tostring(properties["resourceGuid"])
| where id contains AzFwInsRG
| extend LBTroubleshooting=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubscriptionID=v-",subscriptionId,"&p-LoadBalancerArmID=v-", LoadBalancerArmId,"#ff0766c1-b667-4a69-8b56-d96d04f392ee")
| extend Type=iff(id contains "public", "External", "Internal")
| project Name=tostring(split(id, "/")[8]),Type,SubscriptionId=subscriptionId, ResourceGroup=LBRG, LoadBalancerArmId, LBTroubleshooting,ResourceId=id
```

### Azure Firewall Public IP

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let min = datetime_diff('minute',endtime,starttime);
let AzFwELB=cluster("hybridnetworking.kusto.windows.net").database('GatewayManager').SecureGatewayTable
| where CustomerSubscriptionId == SubscriptionID
| where GatewayName == FirewallName
| extend ResourceURI = strcat('/subscriptions/',CustomerSubscriptionId,'/resourceGroups/',ResourceGroup,'/providers/Microsoft.Network/azureFirewalls/',GatewayName)
| extend FirewallvNet=tostring(split(SubnetId, "/subnets/AzureFirewallSubnet")[0])
| project AzureFirewallName=GatewayName, Location, SkuName, SkuTier,GatewayTenantVersion=Version, ResourceURI, FirewallPolicyId,FirewallvNet, GatewayId
| extend ResourceGroupName=strcat("ARMRG-", toupper(GatewayId))
| join cluster('fimpubameprodwestus.westus.kusto.windows.net').database('AzureGraphMigration').LogicalCompute_VirtualMachineNRT on ResourceGroupName
| extend VMScaleSetId=tolower(VMSSArmId)
| extend AzureFirewallILB=tolower(strcat(split(VMScaleSetId, "microsoft.compute/virtualmachinescalesets/")[0], "microsoft.network/loadbalancers/",split(VMScaleSetId,"microsoft.compute/virtualmachinescalesets/")[1], "lb"))
| extend AzureFirewallELB=tolower(strcat(split(VMScaleSetId, "microsoft.compute/virtualmachinescalesets/")[0], "microsoft.network/loadbalancers/",split(VMScaleSetId,"microsoft.compute/virtualmachinescalesets/")[1], "publiclb"))
| distinct AzureFirewallELB;
let FrontendIP=toscalar(cluster('argwus2nrpone.westus2').database('AzureResourceGraph').Resources 
| where timestamp >= starttime - 3d and timestamp <= endtime
| where type == "microsoft.network/loadbalancers"
| where id in~ (AzFwELB)
| project FrontendIP=properties["frontendIPConfigurations"]);
let FrontendIPLength=toscalar(cluster('argwus2nrpone.westus2').database('AzureResourceGraph').Resources 
| where timestamp >= starttime - 3d and timestamp <= endtime
| where type == "microsoft.network/loadbalancers"
| where id in~ (AzFwELB)
| project FrontendIPLength=array_length(properties["frontendIPConfigurations"]));
let PublicIPlist=range i from 0 to FrontendIPLength step 1
| project FIP=FrontendIP[i]["properties"]["publicIPAddress"]["id"],FPrefix=FrontendIP[i]["properties"]["publicIPPrefix"]["id"]
| where FIP != ""
| evaluate narrow()
| extend Value=iff(isempty(Value), "Imemptryemptryemptryemptryemptry", Value)
| project Value;
cluster('argwus2nrpone.westus2.kusto.windows.net').database('AzureResourceGraph').Resources
| where timestamp >= starttime - 3d and timestamp <= endtime
| where id in~ (PublicIPlist)
| project id, IP=tostring(properties["ipAddress"])
| extend UseCase=iff(id contains "management", "ManagementIP", "DataPathIP")
| distinct IP, UseCase//, ResourceId=id
| extend VIPTroubleshoot=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-VIP=v-",IP,"#a172102b-f768-4cc9-982f-0acc07d4765f")
```

### Azure Firewall LB Internal IP

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let min = datetime_diff('minute',endtime,starttime);
let AzFwILB=cluster("hybridnetworking.kusto.windows.net").database('GatewayManager').SecureGatewayTable
| where CustomerSubscriptionId == SubscriptionID
| where GatewayName == FirewallName
| extend ResourceURI = strcat('/subscriptions/',CustomerSubscriptionId,'/resourceGroups/',ResourceGroup,'/providers/Microsoft.Network/azureFirewalls/',GatewayName)
| extend FirewallvNet=tostring(split(SubnetId, "/subnets/AzureFirewallSubnet")[0])
| project AzureFirewallName=GatewayName, Location, SkuName, SkuTier,GatewayTenantVersion=Version, ResourceURI, FirewallPolicyId,FirewallvNet, GatewayId
| extend ResourceGroupName=strcat("ARMRG-", toupper(GatewayId))
| join cluster('fimpubameprodwestus.westus.kusto.windows.net').database('AzureGraphMigration').LogicalCompute_VirtualMachineNRT on ResourceGroupName
| extend VMScaleSetId=tolower(VMSSArmId)
| extend AzureFirewallILB=tolower(strcat(split(VMScaleSetId, "microsoft.compute/virtualmachinescalesets/")[0], "microsoft.network/loadbalancers/",split(VMScaleSetId,"microsoft.compute/virtualmachinescalesets/")[1], "lb"))
| distinct AzureFirewallILB;
let FrontendIP=toscalar(cluster('argwus2nrpone.westus2').database('AzureResourceGraph').Resources 
| where timestamp >= starttime - 3d and timestamp <= endtime
| where type == "microsoft.network/loadbalancers"
| where id in~ (AzFwILB)
| project FrontendIP=properties["frontendIPConfigurations"]);
range i from 0 to 2 step 1
| project IPConfigure=FrontendIP[i]["id"], FIP=FrontendIP[i]["properties"]["privateIPAddress"]
| where IPConfigure != ""
| extend UseCase=iff(IPConfigure contains "mgmt", "ManagementIP", "DataPathIP")
| project IP=FIP, UseCase

```

### Firewall Policy Configuration

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let min = datetime_diff('minute',endtime,starttime);
let FirewallPolicyId=cluster("hybridnetworking.kusto.windows.net").database('GatewayManager').SecureGatewayTable
| where CustomerSubscriptionId == SubscriptionID
| where GatewayName == FirewallName
| distinct FirewallPolicyId;
cluster('argwus2nrpone.westus2').database('AzureResourceGraph').Resources
| where timestamp >= starttime - 3d and timestamp <= endtime
| where id in~ (FirewallPolicyId)
| project timestamp, id, location,DNSServer=tostring(strcat_array(properties["dnsSettings"]["servers"],",")),IsDNSProxyEnabled=tostring(properties["dnsSettings"]["enableProxy"]),threatIntelMode=tostring(properties["threatIntelMode"]),ChildPolicies=tostring(properties["childPolicies"]),IntrusionDetection=tostring(properties["intrusionDetection"])//,properties
| distinct DNSServer, IsDNSProxyEnabled, threatIntelMode, ChildPolicies, IntrusionDetection
| evaluate narrow()
| project Key=Column, Value
```

### PV

```kql
let pv=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('kusto').adxpageview| where page contains "b01/azureFirewalls";
let pvcount=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('microsoft').adxpageview | where page contains "b01/azureFirewalls" | summarize count();
union pv, pvcount
```

