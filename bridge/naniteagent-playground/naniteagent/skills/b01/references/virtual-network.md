---
description: KQL queries for VNet, VirtualWAN, Route Server, hybrid network list, NSG, NMAgent.
---

# Virtual Network & Hybrid Networking Kusto Queries

> Source: Azure Networking B01 Dashboard (aka.ms/b01)
> Pages: Virtual Network, VirtualWAN&RS, Hybrid Network List, NSM-NMagent

## Virtual Network

### vNet under this Subscription

```kql
let starttime = _startTime;
let endtime = _endTime;
cluster('argwus2nrpone.westus2').database('AzureResourceGraph').Resources
| where timestamp >= starttime - 2d and timestamp <= endtime
| where subscriptionId == SubscriptionID
| where type == "microsoft.network/virtualnetworks"
| distinct Name=name, vNetId=tostring(properties["resourceGuid"]), AddressSpace=tostring(properties["addressSpace"]["addressPrefixes"]), Region=location, ResourceURI=id
```

### vNet Configuration

```kql
let starttime = _startTime;
let endtime = _endTime;
let vNetNa = vNetName;
cluster('argwus2nrpone.westus2').database('AzureResourceGraph').Resources
| where timestamp >= starttime - 2d and timestamp <= endtime
| where subscriptionId == SubscriptionID
| where name == vNetNa
| where type == "microsoft.network/virtualnetworks"
| extend RemotePeeringCount=array_length((properties["virtualNetworkPeerings"]))
| distinct Name=name,Region=location,  vNetId=tostring(properties["resourceGuid"]), AddressSpace=tostring(properties["addressSpace"]["addressPrefixes"]),RemotePeeringCount, CustomDNS=tostring(properties["dhcpOptions"]["dnsServers"]), ResourceURI=id, EnabledDDOSProtection=tostring((properties["enableDdosProtection"])), DDOSProtectionPlan=tostring(properties["ddosProtectionPlan"]["id"])
| evaluate narrow()
| project Key=Column, Value
```

### vNet Peering - Randomly response one from the Time Range

```kql
let starttime = _startTime;
let endtime = _endTime;
let vNetNa = vNetName;
let start = 0;
let remotepeeringc=toscalar(cluster('argwus2nrpone.westus2').database('AzureResourceGraph').Resources
| where timestamp >= starttime - 2d and timestamp <= endtime
| where subscriptionId == SubscriptionID
| where name == vNetNa
| where type == "microsoft.network/virtualnetworks"
| distinct RemotePeeringCount=array_length((properties["virtualNetworkPeerings"])));
let end = toint(remotepeeringc);
let peers=toscalar(cluster('argwus2nrpone.westus2').database('AzureResourceGraph').Resources
| where timestamp >= starttime - 2d and timestamp <= endtime
| where subscriptionId == SubscriptionID
| where name == vNetNa
| where type == "microsoft.network/virtualnetworks"
| project RemotePeering=(properties["virtualNetworkPeerings"]));
range i from 0 to end step 1
| project PeerName=peers[i]["name"],RemotevNetResourceURI=peers[i]["properties"]["remoteVirtualNetwork"]["id"],RemotevNetID=peers[i]["properties"]["resourceGuid"],RemotevNetAddressSpace=peers[i]["properties"]["remoteAddressSpace"]["addressPrefixes"],allowVirtualNetworkAccess=peers[i]["properties"]["allowVirtualNetworkAccess"],allowForwardedTraffic=peers[i]["properties"]["allowForwardedTraffic"],allowGatewayTransit=peers[i]["properties"]["allowGatewayTransit"],useRemoteGateways=peers[i]["properties"]["useRemoteGateways"]
| where PeerName != ""

```

### How many VMs are programed over the vNet

```kql
let starttime = _startTime;
let endtime = _endTime;
let vNetNa = vNetName;
let vNetIdz = toscalar(cluster('argwus2nrpone.westus2').database('AzureResourceGraph').Resources
| where timestamp >= starttime - 2d and timestamp <= endtime
| where subscriptionId == SubscriptionID
| where name == vNetNa
| where type == "microsoft.network/virtualnetworks"
| distinct vNetId=tostring(properties["resourceGuid"])
);
let vNetIdzz = toupper(strcat("{",vNetIdz, "}"));
cluster('vnetkusto.northcentralus').database('veritas').InterfaceProgramEndFiveMinuteTable
| where FirstTimeStamp >= starttime and FirstTimeStamp <= endtime
| where VnetGuid in (vNetIdzz)
| where Detail != "Unblock Port Event On Restore" 
| where Detail !startswith "Set Static Arp Entries Event"
| where Detail !startswith "Configure VMMQ to Enable It"
//| project FirstTimeStamp,ContainerId, MACAddress,Detail,NmAgentBuildInfo,NodeId,VnetGuid,VnetId,Cluster,LastTimeStamp
| project FirstTimeStamp,ContainerId
| summarize count() by bin(FirstTimeStamp, 1m), ContainerId
| project FirstTimeStamp, ContainerId
| summarize count=count() by bin(FirstTimeStamp, 1m)
| render columnchart
```

### vNet Gateway Dashboard

```kql
let starttime = _startTime;
let endtime = _endTime;
let vNetNa = vNetName;
let vnetIdzz=cluster('argwus2nrpone.westus2').database('AzureResourceGraph').Resources
| where timestamp >= starttime - 2d and timestamp <= endtime
| where subscriptionId == SubscriptionID
| where name == vNetNa
| where type == "microsoft.network/virtualnetworks"
| distinct vNetId=tostring(properties["resourceGuid"]);
cluster('hybridnetworking').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 2d and PreciseTimeStamp <= endtime
| where VNetId in (vnetIdzz)
| distinct CustomerSubscriptionId, GatewayName,GatewayType,SubnetResourceUri
| extend IsErGwDeployed=iff(GatewayType == "Dedicated", strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubscriptionID=v-",CustomerSubscriptionId,"&p-ErGwName=v-", GatewayName,"#6b3ed060-2146-4831-b1f6-7ad8fddf93e7"), "No")
| extend IsVPNGwDeployed=iff(GatewayType == "DynamicRouting" or GatewayType == "StaticRouting", strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubscriptionID=v-",CustomerSubscriptionId,"&p-VPNGwName=v-",GatewayName,"&p-VPNGatewayInstance=v-GatewayTenantWorker_IN_0&p-VPNGatewayInstance=v-GatewayTenantWorker_IN_1#d8c7c83e-5344-441f-b96d-cc3fc821ff3c"), "No")
| distinct CustomerSubscriptionId, SubnetResourceUri,IsErGwDeployed,IsVPNGwDeployed
| distinct IsErGwDeployed,IsVPNGwDeployed
//| join kind=leftouter cluster("hybridnetworking.kusto.windows.net").database('GatewayManager').SecureGatewayTable on $left.CustomerSubscriptionId == $right.VnetSubscriptionId 
//| where SubnetId contains replace_string(SubnetResourceUri,"GatewaySubnet","AzureFirewallSubnet")
//| extend IsAzureFirewallDeployed=iff(isnotempty(GatewayName), strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubscriptionID=v-",CustomerSubscriptionId,"&p-FirewallName=v-",GatewayName,"#fd14907e-3f08-4fe9-a76d-d6692e799a90"), "No")
//| distinct IsErGwDeployed,IsVPNGwDeployed,IsAzureFirewallDeployed
| evaluate narrow()
| project Key=Column, Value
```

### Azure Firewall Dashboard

```kql
let starttime = _startTime;
let endtime = _endTime;
let vNetNa = vNetName;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let min = datetime_diff('minute',endtime,starttime);
let vnetResourceURI=cluster('argwus2nrpone.westus2').database('AzureResourceGraph').Resources
| where timestamp >= starttime - 2d and timestamp <= endtime
| where subscriptionId == SubscriptionID
| where name == vNetNa
| where type == "microsoft.network/virtualnetworks"
| distinct strcat(id,"/subnets/AzureFirewallSubnet");
cluster("hybridnetworking.kusto.windows.net").database('GatewayManager').SecureGatewayTable
| where SubnetId in~ (vnetResourceURI)
| extend FirewallTroubleshootingLink=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubscriptionID=v-",VnetSubscriptionId,"&p-FirewallName=v-",GatewayName,"#fd14907e-3f08-4fe9-a76d-d6692e799a90")
| project AzureFirewallName=GatewayName, FirewallTroubleshootingLink
| evaluate narrow()
| project Name=Column, Value
```

### PV

```kql
let pv=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('kusto').adxpageview| where page contains "b01/virtualNetwork";
let pvcount=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('microsoft').adxpageview | where page contains "b01/virtualNetwork" | summarize count();
union pv, pvcount
```

## VirtualWAN&RS

### vHubs under this Subscription(Snapshot One Day Delay)

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrvNetId = iff(isempty(SubIdOrHubvNetId), "xyzabc", SubIdOrHubvNetId);
cluster("Hybridnetworking").database("aznwmds").VirtualHubTable 
| where PreciseTimeStamp >= starttime - 2d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == SubIdOrvNetId or VnetId ==  SubIdOrvNetId
| distinct ParentWAN, HubName,ArmId, NrpResourceUri,HubvNetId=VnetId, AddressSpace,ParentWANLocation, Location
| extend vWANTroubleshooting=strcat("https://dataexplorer.azure.com/dashboards/02a21caf-ac85-46b0-a543-32891291a47a?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"&p-vWANGUID=v-",ParentWAN,"#051783a2-b0e5-4bd5-9619-f830ac80dbe4")
```

### vHub Information

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrvNetId = iff(isempty(SubIdOrHubvNetId), "xyzabc", SubIdOrHubvNetId);
let vHub = iff(vHubName == "vNetId", "vNetId",vHubName);
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let vHubvnetID=materialize(cluster("Hybridnetworking").database("aznwmds").VirtualHubTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where iif(vHub == "vNetId",VnetId in (SubIdOrvNetId), CustomerSubscriptionId == SubIdOrvNetId and HubName == vHub)
| distinct VnetId);
let RouteServiceIds=materialize(cluster("Hybridnetworking").database("aznwmds").RouteServiceMonitoringLog
| where PreciseTimeStamp >= starttime - 10m and PreciseTimeStamp <= endtime
| where VirtualNetworkId in (vHubvnetID)
| distinct RouteServiceId);
let RouteServiceVIPs=toscalar(cluster("Hybridnetworking").database("aznwmds").RouteServiceTable
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where RouteServiceId in (RouteServiceIds)
| where RouteServiceVIPs != "null"
| distinct RouteServiceVIPs);
cluster("Hybridnetworking").database("aznwmds").VirtualHubTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where iif(vHub == "vNetId",VnetId in (SubIdOrvNetId), CustomerSubscriptionId == SubIdOrvNetId and HubName == vHub)
| join  kind=leftouter cluster("Hybridnetworking").database("aznwmds").RouteServicePeerConfigTable on VnetId
| extend RouteServiceIdss=toscalar(RouteServiceIds)
| extend RouteServiceVIPs
| distinct  bin(CreatedTime, 1m), HubName, NrpResourceUri,ParentWANLocation, Location, ParentErGatewayId=ExpressRouteGatewayArmId, ParentVpnGatewayId=VpnGatewayArmId, AddressSpace, ResourceGroupForVnet, VnetName, VnetId, HubVnetSubscription, RouteTable, AutoScaleConfiguration,RouteServiceId=RouteServiceIdss,RouteServiceInstanceIP=LocalIps, RouteServiceVIPs,LocalAsn
|extend RouteServiceDashboard=strcat("https://portal.microsoftgeneva.com/s/E9A8D7C9?overrides=[{%22query%22:%22//*[id='RouteServiceId']%22,%22key%22:%22value%22,%22replacement%22:%22", RouteServiceId, "%22},{%22query%22:%22//*[id='resourceId']%22,%22key%22:%22value%22,%22replacement%22:%22",NrpResourceUri, "%22},{%22query%22:%22//*[id='ResourceId']%22,%22key%22:%22value%22,%22replacement%22:%22%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| evaluate narrow()
| project Key=Column, Value


```

### Connected vNets

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrvNetId = iff(isempty(SubIdOrHubvNetId), "xyzabc", SubIdOrHubvNetId);
let vHub = iff(vHubName == "vNetId", "vNetId",vHubName);
let vHubvnetID=materialize(cluster("Hybridnetworking").database("aznwmds").VirtualHubTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where iif(vHub == "vNetId",VnetId in (SubIdOrvNetId), CustomerSubscriptionId == SubIdOrvNetId and HubName == vHub)
| distinct VnetId);
let RouteServiceIds=materialize(cluster("Hybridnetworking").database("aznwmds").RouteServiceMonitoringLog
| where PreciseTimeStamp >= starttime - 10m and PreciseTimeStamp <= endtime
| where VirtualNetworkId in (vHubvnetID)
| distinct RouteServiceId);
let linkedvNet=materialize(cluster("Hybridnetworking").database("aznwmds").RouteServiceTable
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where RouteServiceId in (RouteServiceIds)
| where VnetRanges contains 'Address'
| distinct ConnectedvNetId=ActualVnetId, EnableInternetSecurity, VnetRanges
| extend vNetAddressSpace = parse_json(VnetRanges)
| mv-expand vNetAddressSpace
| extend Address = tostring(vNetAddressSpace.Address), Prefix = tostring(vNetAddressSpace.Prefix), BGPCommunity = tostring(vNetAddressSpace.BgpCommunities)
| extend vNetRange = strcat(Address, '/', Prefix)
| distinct ConnectedvNetId, vNetRange,BGPCommunity, EnableInternetSecurity
);
linkedvNet
```

### Route Service Peer List

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrvNetId = iff(isempty(SubIdOrHubvNetId), "xyzabc", SubIdOrHubvNetId);
let vHub = iff(vHubName == "vNetId", "vNetId",vHubName);
let vHubvNetId=materialize(cluster("Hybridnetworking").database("aznwmds").VirtualHubTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where iif(vHub == "vNetId",VnetId in (SubIdOrvNetId), CustomerSubscriptionId == SubIdOrvNetId and HubName == vHub)
| distinct VnetId);
cluster("Hybridnetworking").database("aznwmds").RouteServicePeerConfigTable
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where VnetId in (vHubvNetId)
| distinct PeerType,PeerIp, PeerAsn, PeerWeight, SoftPrefixLimit, HardPrefixLimit, DataPathEncapSrcIP,DataPathEncapDstIP 
```

### RouteServiceBgpLogsTable

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrvNetId = iff(isempty(SubIdOrHubvNetId), "xyzabc", SubIdOrHubvNetId);
let vHub = iff(vHubName == "vNetId", "vNetId",vHubName);
let vHubVnetId=materialize(cluster("Hybridnetworking").database("aznwmds").VirtualHubTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where iif(vHub == "vNetId",VnetId in (SubIdOrvNetId), CustomerSubscriptionId == SubIdOrvNetId and HubName == vHub)
| distinct VnetId);
cluster("Hybridnetworking").database("aznwmds").RouteServiceBgpLogsTable
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
|  where VirtualNetworkId in (vHubVnetId)
| project TIMESTAMP, RoleInstance, Message
```

### RouteServiceLogsTable

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrvNetId = iff(isempty(SubIdOrHubvNetId), "xyzabc", SubIdOrHubvNetId);
let vHub = iff(vHubName == "vNetId", "vNetId",vHubName);
let vHubvnetID=materialize(cluster("Hybridnetworking").database("aznwmds").VirtualHubTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where iif(vHub == "vNetId",VnetId in (SubIdOrvNetId), CustomerSubscriptionId == SubIdOrvNetId and HubName == vHub)
| distinct VnetId);
let RouteServiceIds=materialize(cluster("Hybridnetworking").database("aznwmds").RouteServiceMonitoringLog
| where PreciseTimeStamp >= starttime - 10m and PreciseTimeStamp <= endtime
| where VirtualNetworkId in (vHubvnetID)
| distinct RouteServiceId);
cluster("Hybridnetworking").database("aznwmds").RouteServiceLogsTable
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
|  where RouteServiceId in (RouteServiceIds)
| where Message !contains "GetAdjacencyTablev4Api"
| project TIMESTAMP, RoleInstance, Message
```

### ExpressRoute Gateway Information

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrvNetId = iff(isempty(SubIdOrHubvNetId), "xyzabc", SubIdOrHubvNetId);
let vHub = iff(vHubName == "vNetId", "vNetId",vHubName);
let ErGwName=materialize(cluster("Hybridnetworking").database("aznwmds").VirtualHubTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where iif(vHub == "vNetId",VnetId in (SubIdOrvNetId), CustomerSubscriptionId == SubIdOrvNetId and HubName == vHub)
| distinct ErGwName=strcat("CG_",ExpressRouteGatewayArmId));
cluster('hybridnetworking').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where GatewayName in (ErGwName)
| distinct ExpressRouteGatewayName=GatewayName,ExpressRouteGatewaySubscription=CustomerSubscriptionId,  GatewayId, GatewayVmSize, VIPAddress, ProvisioningState,GatewayType, Region, GatewayDeploymentType, AzureDeploymentVmSize, PhysicalZones
| extend ERGatewayTroubleshootingLink=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubscriptionID=v-",ExpressRouteGatewaySubscription,"&p-ErGwName=v-", ExpressRouteGatewayName,"#6b3ed060-2146-4831-b1f6-7ad8fddf93e7")
| evaluate narrow()
| project Key=Column, Value
```

### VPN Gateway Information

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrvNetId = iff(isempty(SubIdOrHubvNetId), "xyzabc", SubIdOrHubvNetId);
let vHub = iff(vHubName == "vNetId", "vNetId",vHubName);
let ParentGatewayId=materialize(cluster("Hybridnetworking").database("aznwmds").VirtualHubTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where iif(vHub == "vNetId",VnetId in (SubIdOrvNetId), CustomerSubscriptionId == SubIdOrvNetId and HubName == vHub)
| distinct VpnGatewayArmId);
cluster('hybridnetworking').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where ParentVpnGatewayId in (ParentGatewayId)
| distinct VPNGatewaySubscription=CustomerSubscriptionId, VPNGatewayName=GatewayName, GatewayId, GatewayVmSize, VIPAddress, ProvisioningState,GatewayType, Region, GatewayDeploymentType, AzureDeploymentVmSize, PhysicalZones
| extend VPNGatewayTroubleshootingLink=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubscriptionID=v-",VPNGatewaySubscription,"&p-VPNGwName=v-",VPNGatewayName,"&p-VPNGatewayInstance=v-GatewayTenantWorker_IN_0&p-VPNGatewayInstance=v-GatewayTenantWorker_IN_1#d8c7c83e-5344-441f-b96d-cc3fc821ff3c")
| evaluate narrow()
| project Key=Column, Value
```

### RouteService Instance Dashboard

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let SubIdOrvNetId = iff(isempty(SubIdOrHubvNetId), "xyzabc", SubIdOrHubvNetId);
let vHub = iff(vHubName == "vNetId", "vNetId",vHubName);
let ShoeBoxMdm=materialize(cluster('AzureCM').database('AzureCM').LogClusterSnapshot 
| distinct Region, shoeboxMdmAccountName);
let vHubvnetID=materialize(cluster("Hybridnetworking").database("aznwmds").VirtualHubTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where iif(vHub == "vNetId",VnetId in (SubIdOrvNetId), CustomerSubscriptionId == SubIdOrvNetId and HubName == vHub)
| distinct VnetId);
let RouteServiceIds=materialize(cluster("Hybridnetworking").database("aznwmds").RouteServiceMonitoringLog
| where PreciseTimeStamp >= starttime - 10m and PreciseTimeStamp <= endtime
| where VirtualNetworkId in (vHubvnetID)
| distinct RouteServiceId);
cluster('hybridnetworking.kusto.windows.net').database('aznwmds').RouteServiceToContainerId
| where PreciseTimeStamp >= starttime - 2h and PreciseTimeStamp <= endtime
| where RouteServiceId in (RouteServiceIds)
| distinct RouteServiceId,TenantId, VMSize, RoleInstanceName, Region, AvailabilityZone, DataCenterName, Tenant=Cluster, nodeId=NodeId,containerId=ContainerId,Tenantlower=tolower(Cluster)
| join kind=inner (cluster("azurehn.kusto.windows.net").database("Azurehn").MdmVfpVnetAccountMaps() 
| extend Tenant=tolower(Cluster)) on $left.Tenantlower == $right.Tenant
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
| distinct RouteServiceId, RoleInstanceName, VMSize,Region, Cluster, nodeId, containerId, VFPDashBoard, VFPDropDashBoard, SupportDashBoard, DropDashBoard, FPGADashboard, InvestigateNode, ASIHostNode, NetVMA, PerVMAvailability, PerProcessorPNICDashboard,VFPFullRule, ListUnifiedFlow
```

### RouteServiceInterHubLog

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrvNetId = iff(isempty(SubIdOrHubvNetId), "xyzabc", SubIdOrHubvNetId);
let vHub = iff(vHubName == "vNetId", "vNetId",vHubName);
let vHubvnetID=materialize(cluster("Hybridnetworking").database("aznwmds").VirtualHubTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where iif(vHub == "vNetId",VnetId in (SubIdOrvNetId), CustomerSubscriptionId == SubIdOrvNetId and HubName == vHub)
| distinct VnetId);
cluster("Hybridnetworking").database("aznwmds").RouteServiceInterHubLog
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
|  where VirtualNetworkId in (vHubvnetID)
| project TIMESTAMP, RoleInstance, Message
```

### SLB Information of Route Service VIP 0

```kql
let starttime = _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let min = datetime_diff('minute',endtime,starttime);
let SubIdOrvNetId = iff(isempty(SubIdOrHubvNetId), "xyzabc", SubIdOrHubvNetId);
let vHub = iff(vHubName == "vNetId", "vNetId",vHubName);
let vHubvnetID=materialize(cluster("Hybridnetworking").database("aznwmds").VirtualHubTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where iif(vHub == "vNetId",VnetId in (SubIdOrvNetId), CustomerSubscriptionId == SubIdOrvNetId and HubName == vHub)
| distinct VnetId);
let Region=toscalar(cluster("Hybridnetworking").database("aznwmds").VirtualHubTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where iif(vHub == "vNetId",VnetId in (SubIdOrvNetId), CustomerSubscriptionId == SubIdOrvNetId and HubName == vHub)
| distinct Location);
let SLBAccount =  strcat("slbv2", strcat_array(split(tolower(Region)," "),""));
let RouteServiceIds=materialize(cluster("Hybridnetworking").database("aznwmds").RouteServiceMonitoringLog
| where PreciseTimeStamp >= starttime - 10m and PreciseTimeStamp <= endtime
| where VirtualNetworkId in (vHubvnetID)
| distinct RouteServiceId);
let RSVIPs=toscalar(cluster("Hybridnetworking").database("aznwmds").RouteServiceTable
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where RouteServiceId in (RouteServiceIds)
| where RouteServiceVIPs != "null"
| distinct RouteServiceVIPs);
let VIP0=todynamic(RSVIPs)[0].IPAddress;
cluster('azslb').database('azslbmds').VipMetadataSnapshotRecord
| where env_time > starttime - 6h and env_time < endtime + 1h
| where Vip == VIP0
| summarize by Vip, VipUri, Type, SKU, AltAddress, VmLocs, CountHosts, env_cloud_role, Region
| join (cluster('azslb').database('azslbmds').SlbMetadataVersionRecord
| where env_time > starttime - 1h and env_time < endtime + 1h
|summarize by Region, MdmAccountName, ArmRegion
| extend HPAccountName = strcat("slbhp", substring(MdmAccountName, 5))) on $left.Region == $right.Region
| extend BandwithUsage=strcat("https://portal.microsoftgeneva.com/dashboard/slbv2prod/AzureMonitor/BandwidthUsage?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22slbhp", ArmRegion,"%22},{%22query%22:%22//*[id='VipAddress']%22,%22key%22:%22value%22,%22replacement%22:%22",Vip,"%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend VIPAvailability=strcat("https://portal.microsoftgeneva.com/dashboard/slbv2prod/AzureMonitor/VipAvailability_DataPathAvailability?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",MdmAccountName, "%22},{%22query%22:%22//*[id='VipAddress']%22,%22key%22:%22value%22,%22replacement%22:%22",Vip, "%22},{%22query%22:%22//*[id='Slbv2MDMAccount']%22,%22key%22:%22value%22,%22replacement%22:%22slbv2francecentral%22},{%22query%22:%22//*[id='CaAddress']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='DipPort']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='ProtocolType']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='DipAddress']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='HostAddress']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='Ring']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='LoadBalancerArmId']%22,%22key%22:%22value%22,%22replacement%22:%22""%22},{%22query%22:%22//*[id='PublicIpArmId']%22,%22key%22:%22value%22,%22replacement%22:%22", "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend DipAvailability=strcat("https://portal.microsoftgeneva.com/dashboard/slbv2prod/AzureMonitor/DipAvailability_HealthProbeStatus?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",MdmAccountName, "%22},{%22query%22:%22//*[id='VipAddress']%22,%22key%22:%22value%22,%22replacement%22:%22",Vip, "%22},{%22query%22:%22//*[id='Slbv2MDMAccount']%22,%22key%22:%22value%22,%22replacement%22:%22slbv2francecentral%22},{%22query%22:%22//*[id='CaAddress']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='DipPort']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='ProtocolType']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='DipAddress']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='HostAddress']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='Ring']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='LoadBalancerArmId']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='PublicIpArmId']%22,%22key%22:%22value%22,%22replacement%22:%22", "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend Sflowdashboard=strcat("https://portal.microsoftgeneva.com/s/B40A24AB?overrides=[{%22query%22:%22//*[id='DestinationVIP']%22,%22key%22:%22value%22,%22replacement%22:%22",Vip,"%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend Netflowdashboard=strcat("https://portal.microsoftgeneva.com/s/A5CECCEE?overrides=[{%22query%22:%22//*[id='DestinationVIP']%22,%22key%22:%22value%22,%22replacement%22:%22",Vip,"%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend DDOSStandardPlanCRIDashboard=strcat("https://portal.microsoftgeneva.com/s/BA074862?overrides=[{%22query%22:%22//*[id='DestinationVIP']%22,%22key%22:%22value%22,%22replacement%22:%22",Vip,"%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| distinct Vip, SKU, CountHosts, BandwithUsage,VIPAvailability,DipAvailability,Netflowdashboard,DDOSBasicPlanSflowDashbard=Sflowdashboard,DDOSStandardPlanCRIDashboard
| extend VIPTroubleshoot=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-VIP=v-",Vip,"#a172102b-f768-4cc9-982f-0acc07d4765f")
| evaluate narrow()
| project Key=Column, Value

```

### SLB Information of Route Service VIP 1 

```kql
let starttime = _startTime;
let endtime = _endTime;
let SubIdOrvNetId = iff(isempty(SubIdOrHubvNetId), "xyzabc", SubIdOrHubvNetId);
let vHub = iff(vHubName == "vNetId", "vNetId",vHubName);
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let min = datetime_diff('minute',endtime,starttime);
let vHubvnetID=materialize(cluster("Hybridnetworking").database("aznwmds").VirtualHubTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where iif(vHub == "vNetId",VnetId in (SubIdOrvNetId), CustomerSubscriptionId == SubIdOrvNetId and HubName == vHub)
| distinct VnetId);
let Region=toscalar(cluster("Hybridnetworking").database("aznwmds").VirtualHubTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where iif(vHub == "vNetId",VnetId in (SubIdOrvNetId), CustomerSubscriptionId == SubIdOrvNetId and HubName == vHub)
| distinct Location);
let SLBAccount =  strcat("slbv2", strcat_array(split(tolower(Region)," "),""));
let RouteServiceIds=materialize(cluster("Hybridnetworking").database("aznwmds").RouteServiceMonitoringLog
| where PreciseTimeStamp >= starttime - 10m and PreciseTimeStamp <= endtime
| where VirtualNetworkId in (vHubvnetID)
| distinct RouteServiceId);
let RSVIPs=toscalar(cluster("Hybridnetworking").database("aznwmds").RouteServiceTable
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where RouteServiceId in (RouteServiceIds)
| where RouteServiceVIPs != "null"
| distinct RouteServiceVIPs);
let VIP0=todynamic(RSVIPs)[1].IPAddress;
let VIPTroubleshoot=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-VIP=v-",VIP0,"#a172102b-f768-4cc9-982f-0acc07d4765f");
print VIP1=VIP0,VIPTroubleshoot=VIPTroubleshoot
| evaluate narrow()
| project Key=Column, Value

```

### Azure Firewall Information

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let min = datetime_diff('minute',endtime,starttime);
let SubIdOrvNetId = iff(isempty(SubIdOrHubvNetId), "xyzabc", SubIdOrHubvNetId);
let vHub = iff(vHubName == "vNetId", "vNetId",vHubName);
let vHubArmId=cluster("Hybridnetworking").database("aznwmds").VirtualHubTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where iif(vHub == "vNetId",VnetId in (SubIdOrvNetId), CustomerSubscriptionId == SubIdOrvNetId and HubName == vHub)
| distinct ArmId;
cluster("hybridnetworking.kusto.windows.net").database('GatewayManager').SecureGatewayTable
| where HubArmId in (vHubArmId)
| extend ResourceURI = strcat('/subscriptions/',CustomerSubscriptionId,'/resourceGroups/',ResourceGroup,'/providers/Microsoft.Network/azureFirewalls/',GatewayName)
| extend FirewallvNet=tostring(split(SubnetId, "/subnets/AzureFirewallSubnet")[0])
| project AzureFirewallName=GatewayName, Location, SkuName, SkuTier,GatewayTenantVersion=Version, ResourceURI, FirewallPolicyId,FirewallvNet, GatewayId, CustomerSubscriptionId
| extend ResourceGroupName=strcat("ARMRG-", toupper(GatewayId))
| join cluster('fimpubameprodwestus.westus.kusto.windows.net').database('AzureGraphMigration').LogicalCompute_VirtualMachineNRT on ResourceGroupName
| extend DataplaneMetrics=strcat("https://portal.microsoftgeneva.com/s/DF5CBDF1?overrides=[{%22query%22:%22//*[id='ResourceId']%22,%22key%22:%22value%22,%22replacement%22:%22",ResourceURI,"%22},{%22query%22:%22//*[id='Hostname']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='Region']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id=%5c%22tenant%5c%22]%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[comparand=%5c%22Tenant%5c%22]%22,%22key%22:%22values%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='rid']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='GatewayId']%22,%22key%22:%22value%22,%22replacement%22:%22%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend PerformanceMetrics=strcat("https://portal.microsoftgeneva.com/s/B4A3E93E?overrides=[{%22query%22:%22//*[id='ResourceId']%22,%22key%22:%22value%22,%22replacement%22:%22",ResourceURI, "%22},{%22query%22:%22//*[id='GatewayId']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='Region']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='Hostname']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='GatewayVersion']%22,%22key%22:%22value%22,%22replacement%22:%22%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend DataplaneLogs=strcat("https://portal.microsoftgeneva.com/logs/dgrep?be=DGrep&time=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'), "Z&offset=", min, "&offsetUnit=Minutes&UTC=true&ep=Diagnostics%20PROD&ns=GSAGW&en=AzureMonitor&scopingConditions=[[%22Tenant%22,%22",ResourceURI,"%22]]&conditions=[]&clientQuery=orderby%20PreciseTimeStamp%20asc&aggregatesVisible=true&aggregates=[%22Count%20by%20ActivityId%22]&chartEditorVisible=true&chartType=line&chartLayers=[[%22New%20Layer%22,%22%22]]%20")
| extend RuntimeLog=strcat("https://portal.microsoftgeneva.com/logs/dgrep?be=DGrep&time=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'), "Z&offset=", min, "&offsetUnit=Minutes&UTC=true&ep=Diagnostics%20PROD&ns=GSAGW&en=Runtime&scopingConditions=[[%22Tenant%22,%22",ResourceURI,"%22]]&conditions=[]&clientQuery=orderby%20PreciseTimeStamp%20asc&aggregatesVisible=true&aggregates=[%22Count%20by%20ActivityId%22]&chartEditorVisible=true&chartType=line&chartLayers=[[%22New%20Layer%22,%22%22]]%20")
| extend InterComponentDashboard=strcat("https://portal.microsoftgeneva.com/s/88416F1E?overrides=[{%22query%22:%22//*[id='Hostname']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='Region']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='ResourceId']%22,%22key%22:%22value%22,%22replacement%22:%22", ResourceURI, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend FirewallTroubleshootingLink=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubscriptionID=v-",CustomerSubscriptionId,"&p-FirewallName=v-",AzureFirewallName,"#fd14907e-3f08-4fe9-a76d-d6692e799a90")
| distinct AzureFirewallName, GatewayId, Location, SkuName, SkuTier, GatewayTenantVersion,ResourceURI, FirewallPolicyId, FirewallvNet,FirewallTroubleshootingLink, DataplaneMetrics,PerformanceMetrics,DataplaneLogs,RuntimeLog,InterComponentDashboard
| evaluate narrow()
| project Name=Column, Value
```

### PV

```kql
let pv=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('kusto').adxpageview| where page contains "b01/vwanrs";
let pvcount=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('microsoft').adxpageview | where page contains "b01/vwanrs" | summarize count();
union pv, pvcount
```

## Hybrid Network List

### ExpressRoute Gateways List(1 day delay)

```kql
let starttime= _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let HybridNetSubs = HybridNetSubID;
let subid = pack_array(split(HybridNetSubs, ","))[0];
cluster('hybridnetworking').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId in~ (subid)
| where GatewayType == "Dedicated"
| distinct GatewayName,CustomerSubscriptionId, GatewayId, GatewayVmSize, VIPAddress, ProvisioningState, VNetName, VNetId, GatewayTenantVersion, GatewayType, Region, GatewayDeploymentType, AzureDeploymentVmSize
| extend TroubleshootingLink=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubscriptionID=v-",CustomerSubscriptionId,"&p-ErGwName=v-", GatewayName,"&p-ErOnpremPrefix=no-selection#6b3ed060-2146-4831-b1f6-7ad8fddf93e7")
| extend GatewayDashboard=strcat("https://portal.microsoftgeneva.com/s/3CBF8937?overrides=[{%22query%22:%22//widgets[guid=\\%226ab9c159-6f0a-4b0a-9606-fb10a2058280\\%22]//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22BrkProd%22},{%22query%22:%22//widgets[guid=\\%2282be34f0-284e-46e5-b5eb-dde75359fbb3\\%22]//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22BrkProd%22},{%22query%22:%22//widgets[guid=\\%227969f8a0-907b-4dd9-9151-9c08448f9ad6\\%22]//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22BrkProd%22},{%22query%22:%22//*[id='", GatewayId,"']%22,%22key%22:%22value%22,%22replacement%22:%22GatewayId%22},{%22query%22:%22//*[id='gatewayId']%22,%22key%22:%22value%22,%22replacement%22:%22",GatewayId,"%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| distinct GatewayName,CustomerSubscriptionId, GatewayId, GatewayVmSize, VIPAddress,VNetName, VNetId,GatewayDashboard, TroubleshootingLink, ProvisioningState, GatewayTenantVersion, GatewayType, Region, GatewayDeploymentType, AzureDeploymentVmSize
```

### PV

```kql
let pv=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('kusto').adxpageview| where page contains "b01/exrgateway";
let pvcount=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('microsoft').adxpageview | where page contains "b01/exrgateway" | summarize count();
union pv, pvcount
```

### VPN Gateways List(1 day delay)

```kql
let starttime= _startTime;
let endtime = _endTime;
let HybridNetSubs = HybridNetSubID;
let subid = pack_array(split(HybridNetSubs, ","))[0];
cluster('hybridnetworking').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId in~ (subid)
| where GatewayType != "Dedicated"
| distinct GatewayName,CustomerSubscriptionId, GatewayId, GatewayVmSize,VIPAddress, ProvisioningState,VNetName, VNetId, GatewayTenantVersion, GatewayType,Region,GatewayDeploymentType,AzureDeploymentVmSize
| extend TroubleshootingLink=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubscriptionID=v-",CustomerSubscriptionId,"&p-VPNGwName=v-",GatewayName,"&p-VPNGatewayInstance=v-GatewayTenantWorker_IN_0&p-VPNGatewayInstance=v-GatewayTenantWorker_IN_1&p-LogFilterForMessageColume=all#d8c7c83e-5344-441f-b96d-cc3fc821ff3c")
| distinct GatewayName,CustomerSubscriptionId, GatewayId, GatewayVmSize,VIPAddress,TroubleshootingLink, ProvisioningState,VNetName, VNetId, GatewayTenantVersion, GatewayType,Region,GatewayDeploymentType,AzureDeploymentVmSize
| join kind=leftouter (cluster("hybridnetworking").database("aznwmds").IkeLogsTable | where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime)  on GatewayId
| where  EventMessage contains "Remote"
| extend LocalIP  = extract(@"Local\s+([\d\.]+):", 1, EventMessage)
| distinct GatewayName,CustomerSubscriptionId, GatewayId, GatewayVmSize,VIPAddress, ProvisioningState,VNetName, VNetId, GatewayTenantVersion, GatewayType,Region,GatewayDeploymentType,AzureDeploymentVmSize,LocalIP
| where isnotempty(LocalIP)
| extend TroubleshootingLink=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubscriptionID=v-",CustomerSubscriptionId,"&p-VPNGwName=v-",GatewayName,"&p-VPNGatewayInstance=v-GatewayTenantWorker_IN_0&p-VPNGatewayInstance=v-GatewayTenantWorker_IN_1#d8c7c83e-5344-441f-b96d-cc3fc821ff3c")
| distinct GatewayName,CustomerSubscriptionId, GatewayId, GatewayVmSize,LocalIP,VIPAddress,TroubleshootingLink, ProvisioningState,VNetName, VNetId, GatewayTenantVersion, GatewayType,Region,GatewayDeploymentType,AzureDeploymentVmSize
| summarize GatewayInstanceVIPs=strcat_array(make_set(LocalIP), ", ") by GatewayName,CustomerSubscriptionId, GatewayId, GatewayVmSize,VIPAddress,TroubleshootingLink, ProvisioningState,VNetName, VNetId, GatewayTenantVersion, GatewayType,Region,GatewayDeploymentType,AzureDeploymentVmSize
| distinct GatewayName,CustomerSubscriptionId, GatewayId, GatewayVmSize,GatewayInstanceVIPs,VIPAddress,TroubleshootingLink, ProvisioningState,VNetName, VNetId, GatewayTenantVersion, GatewayType,Region,GatewayDeploymentType,AzureDeploymentVmSize

```

### ExpressRoute Circuits List

```kql
let starttime= _startTime;
let endtime = _endTime;
let HybridNetSubs = HybridNetSubID;
let HybridNetSubss = iff(isnotempty(HybridNetSubs), HybridNetSubs, "plipala");
let subid = pack_array(split(HybridNetSubss, ","))[0];
cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d
| where AzureSubscriptionId in~ (subid)
| distinct CircuitName,AzureSubscriptionId, ServiceKey=AzureServiceKey, Sku, Location, BillingType, ProvisioningState=ServiceProviderProvisioningState, Bandwidth, ServiceProviderName,Region, PrimaryDeviceName, SecondaryDeviceName, AllowGlobalReach
| extend TroubleshootingLink=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubscriptionID=v-",AzureSubscriptionId,"&p-ExpressRouteCircuitName=v-",CircuitName,"#d7150dfa-a8d2-438d-b97f-6de6b0da282c")
| distinct CircuitName,AzureSubscriptionId, ServiceKey, Sku, Location, TroubleshootingLink, BillingType, ProvisioningState, Bandwidth, ServiceProviderName,Region, PrimaryDeviceName, SecondaryDeviceName, AllowGlobalReach
```

### Application Gateway List

```kql
let starttime= _startTime;
let endtime = _endTime;
let HybridNetSubs = HybridNetSubID;
let subid = pack_array(split(HybridNetSubs, ","))[0];
cluster('Hybridnetworking').database('GatewayManager').ApplicationGatewaysExtendedLatestProd
| where CustomerSubscriptionId in~ (subid)
| project GatewayName, CustomerSubscriptionId, GatewayId, SkuType,VirtualIPs, VnetName, VnetId,Region=LocationConstraint,GatewayVersion, VmssVmSKU,State
| extend TroubleshootingLink=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubscriptionID=v-",CustomerSubscriptionId,"&p-AppGwName=v-",GatewayName,"&p-SyslogFilter=all#abe59978-56d2-49b0-b1ed-1afa1d44c90f")
| distinct  GatewayName, CustomerSubscriptionId, GatewayId, SkuType,VirtualIPs, TroubleshootingLink,VnetName, VnetId,Region,GatewayVersion, VmssVmSKU,State
```

### Traffic Collectors List

```kql
let starttime= _startTime;
let endtime = _endTime;
let HybridNetSubs = HybridNetSubID;
let HybridNetSubss = iff(isnotempty(HybridNetSubs), HybridNetSubs, "plipala");
let subid = pack_array(split(HybridNetSubss, ","))[0];
cluster('hybridnetworking').database('aznwmds').AtcTenant
| where TIMESTAMP >= starttime - 1d and TIMESTAMP <= endtime + 1d
| where resourceId has_any (subid) 
| extend Name=tostring(split(resourceId, "/")[-1])
| extend SubscriptionId=tolower(tostring(split(resourceId, "/")[2]))
| distinct Name, SubscriptionId,resourceId=tolower(resourceId), Region, Tenant
| join (cluster('hybridnetworking').database('aznwmds').CircuitToAtcMappingTable | where PreciseTimeStamp >= now(-1d) | extend atcname=tolower(AtcName)) on $left.resourceId == $right.atcname
| distinct  Name, SubscriptionId, ATCResourceID=resourceId, Region, Tenant, ServiceKey=tolower(ServiceKey)
| join (cluster("Hybridnetworking").database("aznwmds").CircuitTable | where PreciseTimeStamp >= now(-1d)) on $left.ServiceKey == $right.AzureServiceKey
| distinct Name, SubscriptionId, Region, Tenant,CircuitName, ServiceKey,ATCResourceID
| summarize CircuitsUnderATC=strcat_array(make_set(CircuitName), ", "), ServicekeysUnderATC=strcat_array(make_set(ServiceKey), ", ") by Name, SubscriptionId, Region, Tenant, ATCResourceID
| extend TroubleshootingLink=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubscriptionID=v-",SubscriptionId,"&p-TCN=v-",Name,"&p-SyslogFilter=all#3579fdc1-f962-45a3-8f64-716c1d9f29da")
| project Name, SubscriptionId, Region, Tenant,CircuitsUnderATC, ServicekeysUnderATC,TroubleshootingLink,ATCResourceID

```

### ExpressRoute Direct Port List

```kql
let starttime= _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let HybridNetSubs = HybridNetSubID;
let HybridNetSubss = iff(isnotempty(HybridNetSubs), HybridNetSubs, "plipala");
let subid = pack_array(split(HybridNetSubss, ","))[0];
cluster("Hybridnetworking").database("aznwmds").PortGroupPortTable
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d
| where SubscriptionId  in~ (subid)
| extend DirectPortResourceUri=tostring(split(replace("https://[^/]+", "", NrpResourceUri), "/links")[0])
| extend ErDirectPortName=tostring(split(DirectPortResourceUri, "/")[8]), SubscriptionId=tostring(split(DirectPortResourceUri, "/")[2])
| distinct ErDirectPortName,SubscriptionId, DeviceName, DevicePortName, Region, MacSecState, Mtu,DirectPortResourceUri
| summarize Devices=strcat_array(make_set(DeviceName), ", ") by ErDirectPortName,SubscriptionId, DevicePortName, Region, MacSecState, Mtu,DirectPortResourceUri
| extend DirectPortDashboard=strcat("https://portal.microsoftgeneva.com/s/137102CD?overrides=[{%22query%22:%22//*[id='ResourceId']%22,%22key%22:%22value%22,%22replacement%22:%22",DirectPortResourceUri, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| distinct ErDirectPortName,SubscriptionId, Devices, DevicePortName, Region, MacSecState, Mtu,DirectPortDashboard, DirectPortResourceUri
```

### ExpressRoute Connection List(1 day delay)

```kql
let starttime= _startTime;
let endtime = _endTime;
let HybridNetSubs = HybridNetSubID;
let subid = pack_array(split(HybridNetSubs, ","))[0];
let gatewayvNetid = cluster('hybridnetworking').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId in~ (subid)
| where GatewayType == "Dedicated"
| distinct VNetId;
cluster('hybridnetworking').database('aznwmds').TunnelIntfTable   
| where PreciseTimeStamp > starttime - 2d and PreciseTimeStamp < endtime
| where VnetId in (gatewayvNetid)
| join kind=leftouter (cluster("Hybridnetworking").database("aznwmds").VnetConfigTable | where PreciseTimeStamp >= starttime - 2d and PreciseTimeStamp < endtime) on ServiceKey and $left.VnetId == $right.VNetId
| distinct ConnectionName=tostring(split(NrpResourceUri,"Microsoft.Network/connections/")[1]), GatewayId,ToCircuit=ServiceKey, DeviceName, MSEETunnelInterface=InterfaceName, tostring(GreKey),MSEETunnelInterfaceIP=IpAddress, TunnelSourceIP=SourceIp, TunnelDestinationIP=DestinationIp, Weight=RoutingWeight,FastPathStatus=DirectTunnelsStatus,PrivateLinkFastPath=EnablePrivateLinkFastPath,State, Description
| summarize MSEEs=strcat_array(make_set(DeviceName), ", "), MSEETunnelInterfaceBGPIP=strcat_array(make_set(MSEETunnelInterfaceIP), ", "), MSEETunnelSourceIP=strcat_array(make_list(TunnelSourceIP), ", ") by ConnectionName, GatewayId,ToCircuit, GreKey=tostring(GreKey), TunnelDestinationIP, Weight,FastPathStatus,PrivateLinkFastPath,State
| project ConnectionName, GatewayId,ToCircuit,MSEEs,MSEETunnelInterfaceBGPIP, MSEETunnelSourceIP,GreKey, TunnelDestinationIP, Weight,FastPathStatus,PrivateLinkFastPath,State
| join kind=leftouter (cluster('hybridnetworking').database('aznwmds').GatewayTenantHealth | where PreciseTimeStamp > starttime - 1d and PreciseTimeStamp < endtime) on $left.GatewayId == $right.GatewayId
| distinct ConnectionName, GatewayId,ToCircuit,MSEEs,MSEETunnelInterfaceBGPIP, MSEETunnelSourceIP,GreKey, TunnelDestinationIP, Weight,FastPathStatus,PrivateLinkFastPath,State, CustomerSubscriptionId, GatewayName
| extend ErGwTroubleshootingLink=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubscriptionID=v-",CustomerSubscriptionId,"&p-ErGwName=v-", GatewayName,"&p-ErGwTenantLogFilter=all#6b3ed060-2146-4831-b1f6-7ad8fddf93e7")
| distinct ConnectionName, GatewayId,ConnectionSubscriptoinId=CustomerSubscriptionId,ToCircuit,MSEEs,MSEETunnelInterfaceBGPIP, MSEETunnelSourceIP,GreKey, TunnelDestinationIP, Weight,FastPathStatus,PrivateLinkFastPath,State,  ErGwTroubleshootingLink
```

### DDOS Plan List

```kql
let starttime= _startTime;
let endtime = _endTime;
let HybridNetSubs = HybridNetSubID;
let subid = pack_array(split(HybridNetSubs, ","))[0];
cluster('argwus2nrpone.westus2').database('AzureResourceGraph').Resources
| where subscriptionId in~ (subid)
| where timestamp >= starttime - 2d and timestamp <= endtime
| where type == "microsoft.network/ddosprotectionplans"
| distinct name,  id
```

### Load Balancer List

```kql
let starttime= _startTime;
let endtime = _endTime;
let HybridNetSubs = HybridNetSubID;
let subid = pack_array(split(HybridNetSubs, ","))[0];
cluster('argwus2nrpone.westus2').database('AzureResourceGraph').Resources
| where subscriptionId in~ (subid)
| where timestamp >= starttime - 1d and timestamp <= endtime
| where type == "microsoft.network/loadbalancers"
| distinct id, subscriptionId,name, SKU=tostring(sku["name"]), Tier=tostring(sku["tier"]), location, ELB=tostring(parse_json(properties)["frontendIPConfigurations"][0]["properties"]["publicIPAddress"]["id"]), ILB=tostring(parse_json(properties)["frontendIPConfigurations"][0]["properties"]["privateIPAddress"]),LoadBalancerArmId=tostring(properties["resourceGuid"])
| extend ELB=case(isnotempty(ELB), "Yes", "No")
| extend  ILB=case(isnotempty(ILB), "Yes", "No")
| distinct subscriptionId, name, ResourceID=id,LoadBalancerArmId, SKU, Tier, location, ELB, ILB
| join kind=leftouter (cluster('Azslb').database('azslbmds').DipEndpointProbeHistoryEvent | where TIMESTAMP > starttime - 5h and TIMESTAMP <= endtime) on $left.LoadBalancerArmId == $right.NrpLoadBalancerId
| distinct subscriptionId, name, ResourceID,LoadBalancerArmId, SKU, Tier, location, ELB, ILB,Vip,ILBVipCA
| summarize Vips=strcat_array(make_set(Vip), ", "),ILBVipCA=strcat_array(make_set(ILBVipCA), ", ") by subscriptionId,name, ResourceID,LoadBalancerArmId, SKU, Tier, location, ELB, ILB 
| extend TroubleshootingLink=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubscriptionID=v-",subscriptionId,"&p-LoadBalancerArmID=v-",LoadBalancerArmId,"#ff0766c1-b667-4a69-8b56-d96d04f392ee")
| distinct SubscriptionId=subscriptionId, Name=name, LoadBalancerArmId, SKU, Tier, Location=location, ELB, ILB,Vips,ILBVipCA,TroubleshootingLink, ResourceID
```

### Virtual Network List

```kql
let starttime= _startTime;
let endtime = _endTime;
let HybridNetSubs = HybridNetSubID;
let subid = pack_array(split(HybridNetSubs, ","))[0];
cluster('argwus2nrpone.westus2').database('AzureResourceGraph').Resources
| where subscriptionId in~ (subid)
| where timestamp >= starttime - 2d and timestamp <= endtime
| where type == "microsoft.network/virtualnetworks"
| distinct Name=name, vNetId=tostring(properties["resourceGuid"]), AddressSpace=strcat_array((properties["addressSpace"]["addressPrefixes"]), ","), Region=location, ResourceURI=id,EnabledDDOSProtection=tostring((properties["enableDdosProtection"])), DDOSProtectionPlan=tostring(properties["ddosProtectionPlan"]["id"])
```

### DDOS Custom Policy List

```kql
let starttime= _startTime;
let endtime = _endTime;
let HybridNetSubs = HybridNetSubID;
let subid = pack_array(split(HybridNetSubs, ","))[0];
cluster('argwus2nrpone.westus2').database('AzureResourceGraph').Resources
| where subscriptionId in~ (subid)
| where timestamp >= starttime - 2d and timestamp <= endtime
| where type == "microsoft.network/ddoscustompolicies"
| distinct name,  id
```

## NSM-NMagent

### NSM to NMAgent Goal State

```kql
let starttime = _startTime;
let endtime = _endTime;
let nid = iff(isnotempty(nodeid), tolower(nodeid), "nodexyz");
let logfilter=nsmagentmessagefilter;
cluster('azurecm').database('AzureCM').DCMNMAgentProgrammingDurationEtwTable
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where nodeId == nid
| where * contains logfilter
| project PreciseTimeStamp, nodeId, interfaceId, ActivityId, programmingDelayInSeconds, message
```

### NSM - SetNetworkInterfaceConfiguration Event

```kql
let starttime = _startTime;
let endtime = _endTime;
let nid = iff(isnotempty(nodeid), tolower(nodeid), "nodexyz");
let logfilter=nsmagentmessagefilter;
let Act=cluster('azurecm').database('AzureCM').DCMNMAgentProgrammingDurationEtwTable
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where nodeId == nid
//| where * contains logfilter
| project PreciseTimeStamp, nodeId, interfaceId, ActivityId, programmingDelayInSeconds, message
| distinct ActivityId;
cluster('Azurecm').database('AzureCM').DCMNMQOSInfoEtwTable
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where operation =~ "SetNetworkInterfaceConfiguration"
| where ActivityId in (Act)
| where * contains logfilter
| extend EnableIOV = extract("EnableIOV=([a-zA-Z]+),",1,additionalMessage)
| project PreciseTimeStamp, ActivityId, operation, operationGroup,EnableIOV, additionalMessage
| sort by PreciseTimeStamp asc

```

