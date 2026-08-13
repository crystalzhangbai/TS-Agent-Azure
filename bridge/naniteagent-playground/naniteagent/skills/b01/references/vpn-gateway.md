---
description: KQL queries for Azure VPN Gateway troubleshooting: tunnel status, IKE diagnostics, S2S/P2S connectivity.
---

# VPN Gateway Kusto Queries

> Source: Azure Networking B01 Dashboard (aka.ms/b01)
> Pages: VPN Gateway

## VPN Gateway

### VPN Gateway under this Subscription

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
cluster('hybridnetworking').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayType != "Dedicated"
| distinct GatewayName,GatewayId, GatewayVmSize,VIPAddress, ProvisioningState,VNetName, VNetId, GatewayType,Region,GatewayDeploymentType,AzureDeploymentVmSize, PhysicalZones
```

### VPN Gateway Configuration and Metrics

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let vpngwname = VPNGwName;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let min = datetime_diff('minute',endtime,starttime);
let ShoeBoxMdm=materialize(cluster('AzureCM').database('AzureCM').LogClusterSnapshot 
| distinct Region, shoeboxMdmAccountName);
cluster('hybridnetworking').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayType != "Dedicated"
| where GatewayName == vpngwname
| extend BGPSettings=parse_xml(BgpSettings)
| extend ASN=tostring(BGPSettings["BgpSettings"]["Asn"]), BgpPeeringAddress=tostring(BGPSettings["BgpSettings"]["BgpPeeringAddress"]),CustomAPIPABGPIPaddress=tostring(BGPSettings["BgpSettings"]["BgpPeeringAddresses"]["IPConfigurationBgpPeeringAddress"]["CustomBgpIpAddresses"]["a:string"])
| extend GatewayTenantLog=strcat("https://portal.microsoftgeneva.com/logs/dgrep?be=DGrep&time=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'), "Z&offset=", min, "&offsetUnit=Minutes&UTC=true&ep=Diagnostics%20PROD&ns=BrkGWT&en=GatewayTenantLogsTable&scopingConditions=[[%22Tenant%22,%22", GatewayId,"%22],[%22__Region__%22,%22", Region,"%22]]&conditions=[]&clientQuery=orderby%20preciseTimeStamp%20asc&chartEditorVisible=true&chartType=line&chartLayers=[[%22New%20Layer%22,%22%22]]%20")
| extend TenantGeneral=strcat("https://portal.microsoftgeneva.com/s/76394F20?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22BrkProd%22},{%22query%22:%22//*[id='GatewayId']%22,%22key%22:%22value%22,%22replacement%22:%22",GatewayId, "%22},{%22query%22:%22//*[id='DeploymentId']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='RoleInstance']%22,%22key%22:%22value%22,%22replacement%22:%22%22}]&globalStartTime=",startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend TenantSystemStats=strcat("https://portal.microsoftgeneva.com/s/7D08A374?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22BrkProd%22},{%22query%22:%22//*[id='GatewayId']%22,%22key%22:%22value%22,%22replacement%22:%22",GatewayId, "%22},{%22query%22:%22//*[id='DeploymentId']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='RoleInstance']%22,%22key%22:%22value%22,%22replacement%22:%22%22}]&globalStartTime=",startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend TenantTunnelStats=strcat("https://portal.microsoftgeneva.com/s/48F16755?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22BrkProd%22},{%22query%22:%22//*[id='GatewayId']%22,%22key%22:%22value%22,%22replacement%22:%22",GatewayId, "%22},{%22query%22:%22//*[id='DeploymentId']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='RoleInstance']%22,%22key%22:%22value%22,%22replacement%22:%22%22}]&globalStartTime=",startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend TenantLiveMigration=strcat("https://portal.microsoftgeneva.com/s/A4776DA?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22BrkProd%22},{%22query%22:%22//*[id='GatewayId']%22,%22key%22:%22value%22,%22replacement%22:%22",GatewayId, "%22},{%22query%22:%22//*[id='DeploymentId']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='RoleInstance']%22,%22key%22:%22value%22,%22replacement%22:%22%22}]&globalStartTime=",startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend TenantInstanceVfpDashboard=strcat("https://portal.microsoftgeneva.com/s/B18CCCFD?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22BrkProd%22},{%22query%22:%22//*[id='GatewayId']%22,%22key%22:%22value%22,%22replacement%22:%22",GatewayId, "%22},{%22query%22:%22//*[id='DeploymentId']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='RoleInstance']%22,%22key%22:%22value%22,%22replacement%22:%22%22}]&globalStartTime=",startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend P2SConnStats=strcat("https://portal.microsoftgeneva.com/s/CB4BD7F9?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22BrkProd%22},{%22query%22:%22//*[id='GatewayId']%22,%22key%22:%22value%22,%22replacement%22:%22",GatewayId, "%22},{%22query%22:%22//*[id='DeploymentId']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='RoleInstance']%22,%22key%22:%22value%22,%22replacement%22:%22%22}]&globalStartTime=",startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend RouteLearnedByGateway=strcat("https://portal.microsoftgeneva.com/?page=actions&acisEndpoint=Public&managementOpen=false&automatedTestsReportOpen=false&bakingDetailsOpen=false&tab=Extensions&acisRolloutEndpoint=Public&selectedNodeType=3&extension=Brooklyn&group=Troubleshooting%20Operations&operationId=getrouteslearnedbyagateway&operationName=Get%20Routes%20Learned%20By%20A%20Gateway&inputMode=single&params={%22subscriptionid%22:%22", subscriptionid, "%22,%22gatewayid%22:%22",GatewayId,"%22,%22gatewayinstancenumber%22:%22%22,%22bgppeeraddress%22:%22%22,%22resourcelookupregionparameter%22:%22", Region, "%22}&actionEndpoint=Brooklyn%20-%20Prod&genevatraceguid=a211d49e-e07b-422e-b744-a6ced4d8cf5d")
| extend RouteAdvertisedByGateway=strcat("https://portal.microsoftgeneva.com/?page=actions&acisEndpoint=Public&managementOpen=false&automatedTestsReportOpen=false&bakingDetailsOpen=false&tab=Extensions&acisRolloutEndpoint=Public&selectedNodeType=3&extension=Brooklyn&group=Troubleshooting%20Operations&operationId=getroutesadvertisedbyagateway&operationName=Get%20Routes%20Advertised%20By%20A%20Gateway&inputMode=single&params={%22subscriptionid%22:%22", subscriptionid, "%22,%22gatewayid%22:%22",GatewayId,"%22,%22gatewayinstancenumber%22:%22%22,%22bgppeeraddress%22:%22%22,%22resourcelookupregionparameter%22:%22", Region, "%22}&actionEndpoint=Brooklyn%20-%20Prod&genevatraceguid=a211d49e-e07b-422e-b744-a6ced4d8cf5d")
| extend VPNGatewayBGPPeerStatus=strcat("https://portal.microsoftgeneva.com/?page=actions&acisEndpoint=Public&managementOpen=false&automatedTestsReportOpen=false&bakingDetailsOpen=false&tab=Extensions&acisRolloutEndpoint=Public&selectedNodeType=3&extension=Brooklyn&group=Troubleshooting%20Operations&operationId=getgatewaybgppeerstatus&operationName=Get%20Gateway%20BGP%20Peer%20Status&inputMode=single&params={%22subscriptionid%22:%22", subscriptionid, "%22,%22gatewayid%22:%22",GatewayId,"%22,%22gatewayinstancenumber%22:%22%22,%22bgppeeraddress%22:%22%22,%22resourcelookupregionparameter%22:%22", Region, "%22}&actionEndpoint=Brooklyn%20-%20Prod&genevatraceguid=a211d49e-e07b-422e-b744-a6ced4d8cf5d")
| extend AdjacencyTable=strcat("https://portal.microsoftgeneva.com/?page=actions&acisEndpoint=Public&managementOpen=false&automatedTestsReportOpen=false&bakingDetailsOpen=false&tab=Extensions&acisRolloutEndpoint=Public&selectedNodeType=3&extension=Brooklyn&group=ExR%20Diagnostic%20Operations&operationId=getadjacencytable&operationName=Get%20Adjacency%20Table&inputMode=single&params={%22gatewayid%22:%22", GatewayId,"%22,%22gatewayinstancenumber%22:%22%22}&actionEndpoint=Brooklyn%20-%20Prod&genevatraceguid=87d19dce-2f80-44f9-9f4b-ee4172406230")
| extend ListIKESA=strcat("https://portal.microsoftgeneva.com/?page=actions&acisEndpoint=Public&managementOpen=false&automatedTestsReportOpen=false&bakingDetailsOpen=false&tab=Extensions&acisRolloutEndpoint=Public&selectedNodeType=3&extension=Brooklyn&group=VPN%20Diagnostics%20Operations&operationId=listgatewayikesas&operationName=List%20Gateway%20IKE%20SAs&inputMode=single&params={%22subscriptionid%22:%22",subscriptionid, "%22,%22gatewayid%22:%22",GatewayId,"%22,%22gatewayinstancenumber%22:%22%22,%22bgppeeraddress%22:%22%22,%22resourcelookupregionparameter%22:%22", Region, "%22}&actionEndpoint=Brooklyn%20-%20Prod&genevatraceguid=a211d49e-e07b-422e-b744-a6ced4d8cf5d")
| distinct GatewayName, HostedServiceName, GatewayId, DeploymentId,Region,PhysicalZones, GatewayVmSize,VIPAddress, CAs,ProvisioningState,VNetName, VNetId, GatewayType,GatewayDeploymentType,AzureDeploymentVmSize, GatewaySubscriptionStorageName, VPNTunnelingProtocols, VPNClientAddressPool, VpnGatewayGeneration,IsMultiTenantCustomerGateway, IsGrpcEnabled, VnetPeeringCount, OSVersion, ASN, BgpPeeringAddress, CustomAPIPABGPIPaddress,EnabledGatewayFeatures, JoinedCertificateDetails,GatewayTenantLog,TenantGeneral,TenantSystemStats, TenantTunnelStats,TenantLiveMigration,TenantInstanceVfpDashboard,P2SConnStats,RouteLearnedByGateway,RouteAdvertisedByGateway,VPNGatewayBGPPeerStatus,AdjacencyTable,ListIKESA
| evaluate narrow()
| project Type=Column, Value
```

### VPN Gateway SLB Metrics

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let vpngwname = VPNGwName;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let min = datetime_diff('minute',endtime,starttime);
let VPNGatewayVIP=toscalar(cluster('hybridnetworking').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayType != "Dedicated"
| where GatewayName == vpngwname
| project VIP=VIPAddress);
cluster('azslb').database('azslbmds').VipMetadataSnapshotRecord
| where env_time > starttime - 6h and env_time < endtime + 1h
| where Vip == VPNGatewayVIP
| summarize by Vip, VipUri, Type, SKU, AltAddress, VmLocs, CountHosts, env_cloud_role, Region
| join (cluster('azslb').database('azslbmds').SlbMetadataVersionRecord
| where env_time > starttime - 1h and env_time < endtime + 1h
|summarize by Region, MdmAccountName, ArmRegion
| extend HPAccountName = strcat("slbhp", substring(MdmAccountName, 5))) on $left.Region == $right.Region
| extend BandwithUsage=strcat("https://portal.microsoftgeneva.com/dashboard/slbv2prod/AzureMonitor/BandwidthUsage?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22slbhp", ArmRegion,"%22},{%22query%22:%22//*[id='VipAddress']%22,%22key%22:%22value%22,%22replacement%22:%22",VPNGatewayVIP,"%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend VIPAvailability=strcat("https://portal.microsoftgeneva.com/dashboard/slbv2prod/AzureMonitor/VipAvailability_DataPathAvailability?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",MdmAccountName, "%22},{%22query%22:%22//*[id='VipAddress']%22,%22key%22:%22value%22,%22replacement%22:%22",VPNGatewayVIP, "%22},{%22query%22:%22//*[id='Slbv2MDMAccount']%22,%22key%22:%22value%22,%22replacement%22:%22slbv2francecentral%22},{%22query%22:%22//*[id='CaAddress']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='DipPort']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='ProtocolType']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='DipAddress']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='HostAddress']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='Ring']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='LoadBalancerArmId']%22,%22key%22:%22value%22,%22replacement%22:%22""%22},{%22query%22:%22//*[id='PublicIpArmId']%22,%22key%22:%22value%22,%22replacement%22:%22", "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend DipAvailability=strcat("https://portal.microsoftgeneva.com/dashboard/slbv2prod/AzureMonitor/DipAvailability_HealthProbeStatus?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",MdmAccountName, "%22},{%22query%22:%22//*[id='VipAddress']%22,%22key%22:%22value%22,%22replacement%22:%22",VPNGatewayVIP, "%22},{%22query%22:%22//*[id='Slbv2MDMAccount']%22,%22key%22:%22value%22,%22replacement%22:%22slbv2francecentral%22},{%22query%22:%22//*[id='CaAddress']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='DipPort']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='ProtocolType']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='DipAddress']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='HostAddress']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='Ring']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='LoadBalancerArmId']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='PublicIpArmId']%22,%22key%22:%22value%22,%22replacement%22:%22", "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend Sflowdashboard=strcat("https://portal.microsoftgeneva.com/s/B40A24AB?overrides=[{%22query%22:%22//*[id='DestinationVIP']%22,%22key%22:%22value%22,%22replacement%22:%22",VPNGatewayVIP,"%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend Netflowdashboard=strcat("https://portal.microsoftgeneva.com/s/A5CECCEE?overrides=[{%22query%22:%22//*[id='DestinationVIP']%22,%22key%22:%22value%22,%22replacement%22:%22",VPNGatewayVIP,"%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend DDOSStandardPlanCRIDashboard=strcat("https://portal.microsoftgeneva.com/s/BA074862?overrides=[{%22query%22:%22//*[id='DestinationVIP']%22,%22key%22:%22value%22,%22replacement%22:%22",VPNGatewayVIP,"%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| distinct Vip, SKU, CountHosts, BandwithUsage,VIPAvailability,DipAvailability,Netflowdashboard,DDOSBasicPlanSflowDashbard=Sflowdashboard,DDOSStandardPlanCRIDashboard
| extend GatewayVIPTroubleshoot=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-VIP=v-",VPNGatewayVIP,"#a172102b-f768-4cc9-982f-0acc07d4765f")
| evaluate narrow()
| project Key=Column, Value

```

### VPN Gateway Instance Infra Metrics

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let vpngwname = VPNGwName;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let ShoeBoxMdm=materialize(cluster('AzureCM').database('AzureCM').LogClusterSnapshot 
| distinct Region, shoeboxMdmAccountName);
let gatewayid = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == vpngwname
| distinct GatewayId);
let gatewaymaps = materialize(cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayName == vpngwname
| distinct GatewayName,GatewayId);
cluster('hybridnetworking.kusto.windows.net').database('aznwmds').ErVpnGwToContainerId
| where PreciseTimeStamp >= starttime - 2h and PreciseTimeStamp <= endtime
| where GatewayId in (gatewayid)
| join kind=inner gatewaymaps on $left.GatewayId == $right.GatewayId
| distinct GatewayName, GatewayId, Region, Tenant=Cluster, RoleInstanceName, nodeId=toupper(NodeId), containerId=ContainerId, VMSize, DataCenterName, CA=tostring(CA), CAv6=tostring(CAv6)
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on $left.nodeId == $right.NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
//| join kind=inner cluster('aznwsdn').database("aznwmds").MdmVfpVnetAccountMaps on $left.Tenant == $right.Cluster
| join kind=inner cluster("azurehn.kusto.windows.net").database("Azurehn").MdmVfpVnetAccountMaps() on $left.Tenant == $right.Cluster
| extend VFPDashBoard=strcat("https://portal.microsoftgeneva.com/dashboard/VfpMDM/dpop/SupportDashboard?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend VFPDropDashBoard=strcat("https://portal.microsoftgeneva.com/dashboard/VfpMDM/dpop/dropsDashboard?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend SupportDashBoard=strcat("https://portal.microsoftgeneva.com/s/9FDB0A67?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend DropDashBoard=strcat("https://portal.microsoftgeneva.com/dashboard/VfpMDM/dpop/dropsDashboard?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend FPGADashboard=strcat("https://portal.microsoftgeneva.com/dashboard/VfpMDM/DatapathDashboards/FpgaDashboardGft/FpgaDashboardGftv3?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend InvestigateNode=strcat("https://dataexplorer.azure.com/dashboards/bea4ccac-baf1-45f3-b160-533232cbfdaa?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH-mm-ss'),"Z&p-_endTime=", format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime, 'HH-mm-ss'), "Z&p-_NodeId=v-", nodeId, "&p-_ContainerId=v-", containerId, "&p-_ICMId=all#2f4843e6-c1e5-4564-ad27-cde71cebc7c7")
| extend ASIHostNode=strcat("https://azureserviceinsights.trafficmanager.net/view/services/Azure%20Host/pages/Azure%20Host%20Node?nodeId=",tolower(nodeId),"&globalFrom=",format_datetime(starttime, 'yyyy-MM-dd'),"T",format_datetime(starttime, 'HH'), "%3A",format_datetime(starttime, 'mm'), "%3A51.000Z&globalTo=",format_datetime(endtime, 'yyyy-MM-dd'),"T",format_datetime(endtime, 'HH'), "%3A",format_datetime(endtime, 'mm'),"%3A51.000Z")
| extend NetVMA=strcat("https://aka.ms/netvma/?destValue=&pathQuery=false&sdnPath=false&showPingMesh=false&startTime=", format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'), "&endTime=", format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime, 'HH:mm:ss'), "&value=", containerId)
| extend PerVMAvailability=strcat("https://portal.microsoftgeneva.com/s/A03537E6?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VNETAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend PerProcessorPNICDashboard=strcat("https://portal.microsoftgeneva.com/dashboard/VfpMDM/DatapathDashboards/PerProcessorNdisDashboard?overrides=[{%22query%22:%22//dataSources%22,%22key%22:%22account%22,%22replacement%22:%22",VfpAccount, "%22},{%22query%22:%22//*[id%3D%27Cluster%27]%22,%22key%22:%22value%22,%22replacement%22:%22",Tenant,"%22},{%22query%22:%22//*[id%3D%27NodeId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",nodeId, "%22},{%22query%22:%22//*[id%3D%27ContainerId%27]%22,%22key%22:%22value%22,%22replacement%22:%22",containerId, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend VFPFullRule=strcat("https://portal.microsoftgeneva.com/?page=actions&acisEndpoint=Public&managementOpen=false&automatedTestsReportOpen=false&tab=Extensions&acisRolloutEndpoint=Public&selectedNodeType=3&extension=SupportabilityFabric&group=Fabric%20Operations&operationId=GetVfpFiltersForContainer&operationName=Get%20VFP%20Filters%20(ACL%20and%20VNET)%20programmed%20on%20containers&inputMode=single&params={%22smefabrichostparam%22:%22", Cluster, "%22,%22smenodeidparam%22:%22", nodeId, "%22,%22smecontaineridparam%22:%22", containerId,"%22,%22smemacaddressparam%22:%22%22,%22smelayerparam%22:%22%22,%22smegroupparam%22:%22%22,%22smeruleparam%22:%22%22,%22smenatpoolparam%22:%22%22,%22smenatrangeparam%22:%22%22,%22smespaceparam%22:%22%22,%22smemappingparam%22:%22%22,%22smevfpfiltercommandparam%22:%22list-rule%22,%22smevfpfilteroptionsparam%22:%22%22}&actionEndpoint=Production&genevatraceguid=9964f627-a5ca-435a-a749-e60f4a56c7f0")
| extend ListUnifiedFlow=strcat("https://portal.microsoftgeneva.com/?page=actions&acisEndpoint=Public&managementOpen=false&automatedTestsReportOpen=false&tab=Extensions&acisRolloutEndpoint=Public&selectedNodeType=3&extension=SupportabilityFabric&group=Fabric%20Operations&operationId=GetVfpFiltersForContainer&operationName=Get%20VFP%20Filters%20(ACL%20and%20VNET)%20programmed%20on%20containers&inputMode=single&params={%22smefabrichostparam%22:%22", Cluster, "%22,%22smenodeidparam%22:%22", nodeId, "%22,%22smecontaineridparam%22:%22", containerId,"%22,%22smemacaddressparam%22:%22%22,%22smelayerparam%22:%22%22,%22smegroupparam%22:%22%22,%22smeruleparam%22:%22%22,%22smenatpoolparam%22:%22%22,%22smenatrangeparam%22:%22%22,%22smespaceparam%22:%22%22,%22smemappingparam%22:%22%22,%22smevfpfiltercommandparam%22:%22list-unified-flow%22,%22smevfpfilteroptionsparam%22:%22%22}&actionEndpoint=Production&genevatraceguid=9964f627-a5ca-435a-a749-e60f4a56c7f0")
| extend ProcessTupleOutbound=strcat("https://portal.microsoftgeneva.com/?page=actions&acisEndpoint=Public&managementOpen=false&automatedTestsReportOpen=false&tab=Extensions&acisRolloutEndpoint=Public&selectedNodeType=3&extension=SupportabilityFabric&group=Fabric%20Operations&operationId=GetVfpFiltersForContainer&operationName=Get%20VFP%20Filters%20(ACL%20and%20VNET)%20programmed%20on%20containers&inputMode=single&params={%22smefabrichostparam%22:%22", Cluster, "%22,%22smenodeidparam%22:%22", nodeId, "%22,%22smecontaineridparam%22:%22", containerId,"%22,%22smemacaddressparam%22:%22%22,%22smelayerparam%22:%22%22,%22smegroupparam%22:%22%22,%22smeruleparam%22:%22%22,%22smenatpoolparam%22:%22%22,%22smenatrangeparam%22:%22%22,%22smespaceparam%22:%22%22,%22smemappingparam%22:%22%22,%22smevfpfiltercommandparam%22:%22process-tuples%22,%22smevfpfilteroptionsparam%22:%22\\%226%20", CA, "%201234%208.8.8.8%20443%20out%201\\%22%22}&actionEndpoint=Production&genevatraceguid=6138abc0-1c93-4b03-bf62-a63eaa6d9ad2")
| extend nodeId=tolower(nodeId)
| join kind=leftouter (cluster('AzureCM').database('AzureCM').LogNodeSnapshot | where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime) on nodeId
| where EndPort != "N"
| distinct RoleInstanceName,CA, CAv6, VMSize,Region, DataCenterName,Cluster, ToR=EndDevice, ToRPort=EndPort, nodeId,ipAddress, containerId, VFPDashBoard, VFPDropDashBoard, SupportDashBoard, DropDashBoard, FPGADashboard, InvestigateNode, ASIHostNode, NetVMA, PerVMAvailability, PerProcessorPNICDashboard,VFPFullRule, ListUnifiedFlow,ProcessTupleOutbound
| summarize T0=make_list(ToR) by RoleInstanceName,CA, CAv6, VMSize,Region, DataCenterName,Cluster, nodeId, nodeipAddress=ipAddress, containerId, VFPDashBoard, VFPDropDashBoard, SupportDashBoard, DropDashBoard, FPGADashboard, InvestigateNode, ASIHostNode, NetVMA, PerVMAvailability, PerProcessorPNICDashboard,VFPFullRule, ListUnifiedFlow,ProcessTupleOutbound
| extend VMdash=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubIdOrContainerId=v-",containerId,"&&p-VMName=v-ContaizerId&p-DataPathScan=v-No#8ed1e2a2-d979-401b-9609-7580ad07ccd1")
| distinct RoleInstanceName,CA, CAv6, VMSize,Region, DataCenterName,Cluster, T0=tostring(T0), nodeId, nodeipAddress, containerId, VMdash,VFPDashBoard, VFPDropDashBoard, SupportDashBoard, DropDashBoard, FPGADashboard, InvestigateNode, ASIHostNode, NetVMA, PerVMAvailability, PerProcessorPNICDashboard,VFPFullRule, ListUnifiedFlow,ProcessTupleOutbound
| order  by RoleInstanceName asc
```

### TunnelEvent Log

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let vpngwname = VPNGwName;
let VPNIns = todynamic(VPNGatewayInstance);
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let GatewayID=materialize(cluster('hybridnetworking').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayType != "Dedicated"
| where GatewayName == vpngwname
| distinct GatewayId
);
cluster('hybridnetworking').database('aznwmds').TunnelEventsTable 
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where RoleInstance in (VPNIns)
| where GatewayId in (GatewayID)
| project PreciseTimeStamp,GatewayBuildVersion,  RoleInstance,TunnelName, Message, TunnelStateChangeReason, IkeImplementationType, NegotiatedSAs,IsPlannedFailover
```

### IKE Log

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let vpngwname = VPNGwName;
let VPNIns = todynamic(VPNGatewayInstance);
let GatewayID=materialize(cluster('hybridnetworking').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime -1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayType != "Dedicated"
| where GatewayName == vpngwname
| distinct GatewayId
);
cluster("hybridnetworking").database("aznwmds").IkeLogsTable
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where GatewayId in (GatewayID)
| where RoleInstance in (VPNIns)
| project PreciseTimeStamp,RoleInstance,Message=EventMessage
```

### GatewayTenant Log

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let vpngwname = VPNGwName;
let VPNIns = todynamic(VPNGatewayInstance);
let GatewayID=materialize(cluster('hybridnetworking').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayType != "Dedicated"
| where GatewayName == vpngwname
| distinct GatewayId
);
cluster("hybridnetworking").database("aznwmds").GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where GatewayId in (GatewayID)
| where RoleInstance in (VPNIns)
| project PreciseTimeStamp, RoleInstance,Message
```

### VPN Gateway SLB Mux Metrics

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let vpngwname = VPNGwName;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let min = datetime_diff('minute',endtime,starttime);
let VPNGatewayVIP=toscalar(cluster('hybridnetworking').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayType != "Dedicated"
| where GatewayName == vpngwname
| project VIP=VIPAddress);
cluster('azslb').database('azslbmds').DSMulticastGroupEvent
| where env_time > starttime - 1h and env_time < endtime + 1h
| where SegmentName != "0.0.0.0_0" and SegmentName != "::_0"
| where Uri has "MuxPoolManager"
| summarize arg_max(env_time, *) by SegmentName, Uri
| project env_cloud_name, SegmentName, GroupIncarnationId, MulticastGroup
| extend CidrString = replace_string(SegmentName, "_", "/")
| extend Ipv4Cidr = iff(CidrString has ":", "", CidrString), Ipv6Cidr = iff(CidrString has ":", CidrString, "")
| where ipv6_is_in_range(VPNGatewayVIP, Ipv6Cidr) or ipv4_is_in_range(VPNGatewayVIP, Ipv4Cidr)
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

### IPSec Connection

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let vpngwname = VPNGwName;
let VPNIns = todynamic(VPNGatewayInstance);
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let GatewayID=materialize(cluster('hybridnetworking').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayType != "Dedicated"
| where GatewayName == vpngwname
| distinct GatewayId
);
cluster('hybridnetworking').database('aznwmds').ConnectionConfiguration 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where GatewayId in (GatewayID)
| where ConnectionType == "IPsec"
| join kind=leftouter (cluster('hybridnetworking').database('aznwmds').LocalNetworkGatewayTable | where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime) on $left.LocalNetworkSiteName == $right.Id
| extend AddressSpace=tostring(parse_xml(AddressSpace).ArrayOfString["string"])
| extend BGPSettings=parse_xml(BgpSettings)
| extend ASN=tostring(BGPSettings.BgpSettings.Asn), BgpPeeringIP=tostring(BGPSettings.BgpSettings.BgpPeeringAddress), BgpPeerWeight=tostring(BGPSettings.BgpSettings.PeerWeight)
//| distinct ConnectionName, ConnectedEntityId, LocalNetworkGateway=LocalNetworkSiteName, ConnectionType, EncryptionType, GatewayConnectionProtocol,  PfsGroup, HashAlgorithm, SALifeTimeSeconds, SADataSizeKilobytes, IkeDPDTimeout, RoutingWeight, EnableBgp, EnableInternetSecurity, UseLocalAzureIpAddress, UsePolicyBasedTrafficSelectors, IpsecPolicies,GatewayCustomBgpIpAddresses, Gateway1CustomBgpIpAddresses,AddressSpace, ASN, BgpPeeringIP, BgpPeerWeight,IpAddress, Fqdn,RouteLimit
//| extend LNGProperties=tostring(pack("LocalNetworkGatewayName", LocalNetworkSiteName, "LNGIPAddress", IpAddress, "LNGFqdn", Fqdn, "RouteLimit", RouteLimit, "AddressSpace", AddressSpace, "ASN", ASN, "BgpPeeringAddress", BgpPeeringIP, "BgpPeerWeight", BgpPeerWeight))
//| extend IkePolicy=tostring(pack("EncryptionType", EncryptionType, "HashAlgorithm", HashAlgorithm, "PfsGroup", PfsGroup, "SALifeTimeSeconds", SALifeTimeSeconds, "SADataSizeKilobytes", SADataSizeKilobytes, "IkeDPDTimeout", IkeDPDTimeout, "RoutingWeight", RoutingWeight, "IpsecPolicies", IpsecPolicies))
| distinct ConnectionName, ConnectionType, Protocol=GatewayConnectionProtocol,IsBGPEnabled=EnableBgp, UsePolicyBasedTrafficSelectors,LNGName=GatewayName, LNGIPAddress=IpAddress,  LNGFqdn=Fqdn, LNGAddressSpace=AddressSpace, LNGASN=ASN, LNGBgpPeeringIP=BgpPeeringIP, CustomIpsecPolicies=IpsecPolicies, GatewayCustomBgpIpAddresses, Gateway1CustomBgpIpAddresses


```

### P2S Log Table

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let vpngwname = VPNGwName;
let VPNIns = todynamic(VPNGatewayInstance);
let GatewayID=materialize(cluster('hybridnetworking').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayType != "Dedicated"
| where GatewayName == vpngwname
| distinct GatewayId
);
cluster("hybridnetworking").database("aznwmds").P2SLogsTable
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where GatewayId in (GatewayID)
| where RoleInstance in (VPNIns)
| project PreciseTimeStamp, RoleInstance,EventMessage
```

### PV

```kql
let pv=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('kusto').adxpageview| where page contains "b01/vpngateway";
let pvcount=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('microsoft').adxpageview | where page contains "b01/vpngateway" | summarize count();
union pv, pvcount
```

