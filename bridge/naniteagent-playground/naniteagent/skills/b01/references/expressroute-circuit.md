---
description: KQL queries for ExpressRoute Circuit diagnostics: circuit health, peering status, BGP routes, ARP table, bandwidth utilization.
---

# ExpressRoute Circuit Kusto Queries

> Source: Azure Networking B01 Dashboard (aka.ms/b01)
> Pages: ExpressRoute Circuit

## ExpressRoute Circuit

### ExpressRoute Circuits under the subscription

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d
| where AzureSubscriptionId == subscriptionid
| distinct CircuitName, ServiceKey=AzureServiceKey, Location, Sku, BillingType,DedicatedCircuitStatus,PortPairId, ServiceProviderProvisioningState, Bandwidth, ServiceProviderName,Region, PrimaryDeviceName, SecondaryDeviceName, AllowGlobalReach, GatewayManagerVersion
```

### Sub Interface Configuration(Towards to CE)

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d
| where AzureSubscriptionId == subscriptionid
| where CircuitName == ExpressRouteCircuitName
//| distinct ServiceKey=AzureServiceKey
| extend ServiceKey=AzureServiceKey
| join kind=leftouter (cluster("Hybridnetworking").database("aznwmds").SubIntfTable | where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d) on ServiceKey
| join kind=leftouter (cluster("Hybridnetworking").database("aznwmds").VrfTable | where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d) on ServiceKey
//| distinct DeviceName, VRF = replace_string(VrfId, "-", ""), VrfId, SubInterfaceName=InterfaceName, MSEESubInterfaceIPv4=IpAddress,MSEESubInterfaceIPv6=IpAddressv6,IsTrafficCollectorEnabled=IsIpfixEnabled, State, Statev6, Type, CTag, STag, PerVRFIPv4RoutesLimit=MaximumRoutesLimit, PerVRFIPv6RoutesLimit=MaximumRoutesLimitv6,Description
| summarize ConfigStartTime=min(PreciseTimeStamp), ConfigEndTime=max(PreciseTimeStamp) by Type, DeviceName, VRF = replace_string(VrfId, "-", ""), VrfId, SubInterfaceName=InterfaceName, MSEESubInterfaceIPv4=IpAddress,MSEESubInterfaceIPv6=IpAddressv6,IsTrafficCollectorEnabled=IsIpfixEnabled, State, Statev6, CTag, STag, PerVRFIPv4RoutesLimit=MaximumRoutesLimit, PerVRFIPv6RoutesLimit=MaximumRoutesLimitv6,Description
//| project ConfigStartTime, ConfigEndTime, DeviceName, VRF, VrfId, SubInterfaceName, MSEESubInterfaceIPv4,MSEESubInterfaceIPv6,IsTrafficCollectorEnabled, State, Statev6, Type, CTag, STag, PerVRFIPv4RoutesLimit, PerVRFIPv6RoutesLimit,Description
//cluster("Hybridnetworking").database("aznwmds").CircuitTable 
//| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d
//| where AzureSubscriptionId == subscriptionid
//| where CircuitName == ExpressRouteCircuitName
//| distinct ServiceKey=AzureServiceKey
//| join kind=leftouter cluster("Hybridnetworking").database("aznwmds").SubIntfTable on ServiceKey
//| join kind=leftouter cluster("Hybridnetworking").database("aznwmds").VrfTable on ServiceKey
//| distinct DeviceName, VRF = replace_string(VrfId, "-", ""), VrfId, SubInterfaceName=InterfaceName, MSEESubInterfaceIPv4=IpAddress,MSEESubInterfaceIPv6=IpAddressv6,IsTrafficCollectorEnabled=IsIpfixEnabled, State, Statev6, Type, CTag, STag, PerVRFIPv4RoutesLimit=MaximumRoutesLimit, PerVRFIPv6RoutesLimit=MaximumRoutesLimitv6,Description



```

### Tunnel Interface configuration towards to ExpressRoute Gateway

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d
| where AzureSubscriptionId == subscriptionid
| where CircuitName == ExpressRouteCircuitName
| distinct ServiceKey=AzureServiceKey, EnableDirectPortRateLimit
| join kind=leftouter (cluster("Hybridnetworking").database("aznwmds").TunnelIntfTable | where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d) on ServiceKey
| join kind=leftouter (cluster("Hybridnetworking").database("aznwmds").VnetConfigTable | where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d) on ServiceKey and $left.VnetId == $right.VNetId
| distinct  DeviceName, VrfId, TunnelInterface=InterfaceName, BGPIpAddress=IpAddress, BGPIpAddressv6=IpAddressv6, SourcePort, TunnelSourceIpOnMSEE=SourceIp, TunnelDstIpErGwVIP=DestinationIp, LinkedVnetId=VnetId, LinkedGatewayId=GatewayId1,EnableDirectPortRateLimit,Description, FastPathStatus=DirectTunnelsStatus,RoutingWeight,PeeredCircuitServiceKey
| where PeeredCircuitServiceKey == "" 
| extend LinkedvNetName=tostring(split(Description, " ")[3])
//| project DeviceName, VRF = replace_string(VrfId, "-", ""), VrfId, TunnelInterface, BGPIpAddress, BGPIpAddressv6, SourcePort, TunnelSourceIpOnMSEE, TunnelDstIpErGwVIP,LinkedvNetName, FastPathStatus, LinkedVnetId,EnableDirectPortRateLimit, LinkedGatewayId, Description
| join kind=leftouter (cluster('hybridnetworking').database('aznwmds').GatewayTenantHealth | where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d) on $left.LinkedGatewayId == $right.GatewayId
| project LinkedvNetName, LinkedVnetId, LinkedGatewayId, FastPathStatus, RoutingWeight,DeviceName,  TunnelInterface, BGPIpAddress, BGPIpAddressv6, SourcePort, TunnelSourceIpOnMSEE, TunnelDstIpErGwVIP, Description, GatewayName,CustomerSubscriptionId
| summarize DeviceNames=make_list(DeviceName), BGPIpAddressesOnMSEE=make_list(BGPIpAddress), BGPIpAddressv6esOnMSEE=make_list(BGPIpAddressv6), Descriptions=make_list(Description), TunnelSourceIpOnMSEEs=make_list(TunnelSourceIpOnMSEE) by LinkedGatewayName=GatewayName,LinkedGatewayId,LinkedvNetName, LinkedVnetId, FastPathStatus, RoutingWeight,SourcePort,  TunnelDstIpErGwVIP,TunnelInterface,CustomerSubscriptionId
| extend ERGatewayTroubleshootingLink=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubscriptionID=v-",CustomerSubscriptionId,"&p-ErGwName=v-", LinkedGatewayName,"&p-ErOnpremPrefix=no-selection#6b3ed060-2146-4831-b1f6-7ad8fddf93e7")

```

### Circuit Metrics and Links

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let subscriptionid = SubscriptionID;
cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d
| where AzureSubscriptionId == subscriptionid
| where CircuitName == ExpressRouteCircuitName
| join kind=leftouter (cluster("Hybridnetworking").database("aznwmds").SubIntfTable | where PreciseTimeStamp >= starttime - 5d and PreciseTimeStamp <= endtime + 1d) on $left.AzureServiceKey == $right.ServiceKey
| extend PhyInterface=tostring(split(InterfaceName, ".")[0])
| distinct CircuitName, AzureServiceKey, Sku, Location, BillingType,DedicatedCircuitStatus, ResourceURI=replace("https://[^/]+", "", NrpResourceUri), PortPairId, ServiceProviderProvisioningState, Bandwidth, ServiceProviderName,Region, PrimaryDeviceName, SecondaryDeviceName, AllowGlobalReach,PhyInterface,InterfaceName
| extend CircuitDashboard=strcat("https://portal.microsoftgeneva.com/s/8817E257?overrides=[{%22query%22:%22//*[id='ResourceId']%22,%22key%22:%22value%22,%22replacement%22:%22",ResourceURI, "%22},{%22query%22:%22//*[id='ServiceKey/NRPResouceUri']%22,%22key%22:%22value%22,%22replacement%22:%22((",AzureServiceKey,")%20%20(",ResourceURI,"))%22},{%22query%22:%22//*[id='ServiceKey']%22,%22key%22:%22value%22,%22replacement%22:%22", AzureServiceKey, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend BandwidthDashboard=strcat("https://portal.microsoftgeneva.com/s/ADBFA076?overrides=[{%22query%22:%22//*[id='ResourceId']%22,%22key%22:%22value%22,%22replacement%22:%22",ResourceURI, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend DumpCircuitInfo=strcat("https://portal.microsoftgeneva.com/?page=actions&acisEndpoint=Public&managementOpen=false&automatedTestsReportOpen=false&bakingDetailsOpen=false&tab=Extensions&acisRolloutEndpoint=Public&selectedNodeType=3&extension=Brooklyn&group=ExR%20Diagnostic%20Operations&operationId=dumpcircuitinformation&operationName=Dump%20Circuit%20Information&inputMode=single&params={%22subscriptionid%22:%22%22,%22servicekey%22:%22",AzureServiceKey,"%22,%22vnetid%22:%22%22,%22vrfname%22:%22%22,%22nrpresourceuri%22:%22%22}&actionEndpoint=Brooklyn%20-%20Prod&genevatraceguid=2f25464f-5aec-4963-9908-6387dccddaa3")
| extend DumpRoutingInfo=strcat("https://portal.microsoftgeneva.com/?page=actions&acisEndpoint=Public&managementOpen=false&automatedTestsReportOpen=false&bakingDetailsOpen=false&tab=Extensions&acisRolloutEndpoint=Public&selectedNodeType=3&extension=Brooklyn&group=ExR%20Diagnostic%20Operations&operationId=dumproutinginfo&operationName=Dump%20Routing%20Information&inputMode=single&params={%22subscriptionid%22:%22%22,%22servicekey%22:%22",AzureServiceKey,"%22,%22vnetid%22:%22%22,%22vrfname%22:%22%22,%22nrpresourceuri%22:%22%22}&actionEndpoint=Brooklyn%20-%20Prod&genevatraceguid=2f25464f-5aec-4963-9908-6387dccddaa3")
| extend DebugACLPrimaryDevice=strcat("https://portal.microsoftgeneva.com/?page=actions&acisEndpoint=Public&managementOpen=false&automatedTestsReportOpen=false&bakingDetailsOpen=false&tab=Extensions&acisRolloutEndpoint=Public&selectedNodeType=3&extension=Brooklyn&group=ExR%20Diagnostic%20Operations&operationId=enabledebugacl&operationName=Enable%20Debug%20ACL&inputMode=single&params={%22devicename%22:%22",PrimaryDeviceName,"%22,%22interfacename%22:%22", InterfaceName,"%22,%22ipprotocol%22:%22Ip%22,%22ipport%22:%220%22,%22onpremipaddresscidr%22:%22%22,%22azureipaddresscidr%22:%22%22,%22aclvaliddurationseconds%22:%22120%22,%22deviceregion%22:%22Regional%22}&actionEndpoint=Brooklyn%20-%20Prod&genevatraceguid=40bcf5d8-1996-4aeb-9f6f-18d4d8f943a7")
| extend DebugACLSecondaryDevice=strcat("https://portal.microsoftgeneva.com/?page=actions&acisEndpoint=Public&managementOpen=false&automatedTestsReportOpen=false&bakingDetailsOpen=false&tab=Extensions&acisRolloutEndpoint=Public&selectedNodeType=3&extension=Brooklyn&group=ExR%20Diagnostic%20Operations&operationId=enabledebugacl&operationName=Enable%20Debug%20ACL&inputMode=single&params={%22devicename%22:%22",SecondaryDeviceName,"%22,%22interfacename%22:%22", InterfaceName,"%22,%22ipprotocol%22:%22Ip%22,%22ipport%22:%220%22,%22onpremipaddresscidr%22:%22%22,%22azureipaddresscidr%22:%22%22,%22aclvaliddurationseconds%22:%22120%22,%22deviceregion%22:%22Regional%22}&actionEndpoint=Brooklyn%20-%20Prod&genevatraceguid=40bcf5d8-1996-4aeb-9f6f-18d4d8f943a7")
| extend ValidatePrimaryDeviceConfiguration=strcat("https://portal.microsoftgeneva.com/?page=actions&acisEndpoint=Public&managementOpen=false&automatedTestsReportOpen=false&bakingDetailsOpen=false&tab=Extensions&acisRolloutEndpoint=Public&selectedNodeType=3&extension=Brooklyn&group=ExR%20Service%20Operations&operationId=validatedeviceconfiguration&operationName=Validate%20Device%20Configuration&inputMode=single&params={%22devicename%22:%22", PrimaryDeviceName,"%22,%22servicekey%22:%22",AzureServiceKey, "%22,%22bgppeertype%22:%22%22}&actionEndpoint=Brooklyn%20-%20Prod&genevatraceguid=61dc43c2-36f3-40cd-99f6-9921b0e593b2")
| extend ValidateSecondaryDeviceConfiguration=strcat("https://portal.microsoftgeneva.com/?page=actions&acisEndpoint=Public&managementOpen=false&automatedTestsReportOpen=false&bakingDetailsOpen=false&tab=Extensions&acisRolloutEndpoint=Public&selectedNodeType=3&extension=Brooklyn&group=ExR%20Service%20Operations&operationId=validatedeviceconfiguration&operationName=Validate%20Device%20Configuration&inputMode=single&params={%22devicename%22:%22", PrimaryDeviceName,"%22,%22servicekey%22:%22",AzureServiceKey, "%22,%22bgppeertype%22:%22%22}&actionEndpoint=Brooklyn%20-%20Prod&genevatraceguid=61dc43c2-36f3-40cd-99f6-9921b0e593b2")
| extend PrimaryMSEECoreTool=strcat("https://coretools.azurefd.net/#/device/home?target=",PrimaryDeviceName,"&time=",startunixtime, "%252C", endunixtime, "&useUtc=true&renderType=chart&keywords=&searchContext=devices&summary=Device&linkDirection=forwardandreverse&interfaceType=portchannel&dataType=&domain=All&cloudType=Public")
| extend SecondaryMSEECoreTool=strcat("https://coretools.azurefd.net/#/device/home?target=",SecondaryDeviceName,"&time=",startunixtime, "%252C", endunixtime, "&useUtc=true&renderType=chart&keywords=&searchContext=devices&summary=Device&linkDirection=forwardandreverse&interfaceType=portchannel&dataType=&domain=All&cloudType=Public")
| evaluate narrow()
| project Type=Column, Value

```

### Any ExpressRoute maintenance(TDO-FiltertherelatedCircuitMaintenance)

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let Devices= materialize(cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d
| where AzureSubscriptionId == subscriptionid
| where CircuitName == ExpressRouteCircuitName
| distinct PrimaryDeviceName, SecondaryDeviceName);
cluster('icmcluster.kusto.windows.net').database('ACM.Publisher').AlbnTargets_Expanded
| where PublishDateTime >= starttime - 30d and PublishDateTime <= endtime + 10d
| where Subscription == subscriptionid
| join kind=inner cluster('icmcluster.kusto.windows.net').database('ACM.Backend').PublishRequest on $left.TrackingId==$right.IncidentId
| where ImpactedServices contains "ExpressRoute"
| project CommunicationDateTime, Title, Stage, TrackingId = IncidentId, EventType, ImpactedServices, RichTextMessage, AdditionalProperties, Status, CommunicationId, Subscription
```

### Primary MSEE Syslog

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let PrimaryDevice=materialize(cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d
| where AzureSubscriptionId == subscriptionid
| where CircuitName == ExpressRouteCircuitName
| distinct PrimaryDeviceName);
cluster('azphynet.kusto.windows.net').database('azdhmds').SyslogData
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where Device in (PrimaryDevice)
| project PreciseTimeStamp, Device, Severity, FacilityMessage, EventName,Message
```

### Secondary MSEE Syslog

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let SecondaryDeviceName=materialize(cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where AzureSubscriptionId == subscriptionid
| where CircuitName == ExpressRouteCircuitName
| distinct SecondaryDeviceName);
cluster('azphynet.kusto.windows.net').database('azdhmds').SyslogData
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where Device in (SecondaryDeviceName)
| project PreciseTimeStamp, Device, Severity, FacilityMessage, EventName,Message
```

### Drop and Error Counter Of MSEEs SubInterface

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let DeviceNames=materialize(cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d
| where AzureSubscriptionId == subscriptionid
| where CircuitName == ExpressRouteCircuitName
| distinct ServiceKey=AzureServiceKey
| join kind=leftouter cluster("Hybridnetworking").database("aznwmds").SubIntfTable on ServiceKey
| join kind=leftouter cluster("Hybridnetworking").database("aznwmds").VrfTable on ServiceKey
| distinct DeviceNames=DeviceName);
let InterfaceNames=materialize(cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where AzureSubscriptionId == subscriptionid
| where CircuitName == ExpressRouteCircuitName
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

### Is Direct Port Circuit?

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let subscriptionid = SubscriptionID;
cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d
| where AzureSubscriptionId == subscriptionid
| where CircuitName == ExpressRouteCircuitName
| join kind=leftouter (cluster("Hybridnetworking").database("aznwmds").SubIntfTable | where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d) on $left.AzureServiceKey == $right.ServiceKey
| extend PhyInterface=tostring(split(InterfaceName, ".")[0])
| join  kind=leftouter (cluster("Hybridnetworking").database("aznwmds").PortGroupPortTable | where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d)  on  $left.PhyInterface == $right.DevicePortName and $left.PrimaryDeviceName == $right.DeviceName
| distinct DirectPortResourceUri=tostring(split(replace("https://[^/]+", "", NrpResourceUri1), "/links")[0]),  MacSecState, EnableDirectPortRateLimit
| extend DirectPortDashboard=strcat("https://portal.microsoftgeneva.com/s/137102CD?overrides=[{%22query%22:%22//*[id='ResourceId']%22,%22key%22:%22value%22,%22replacement%22:%22",DirectPortResourceUri, "%22}]&globalStartTime=", startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend IsERDirectPort=case(isnotempty(DirectPortResourceUri), "Yes", "No")
| project IsERDirectPort, DirectPortResourceUri, EnableDirectPortRateLimit,MacSecState, DirectPortDashboard
| evaluate narrow()
| project Type=Column, Value


```

### Primary MSEE - IER Information

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let primarymsee=cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d
| where AzureSubscriptionId == subscriptionid
| where CircuitName == ExpressRouteCircuitName
| distinct PrimaryDeviceName;
cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where StartDevice in (primarymsee)
| where LinkType == "DeviceInterfaceLink"
| distinct MSEE=StartDevice, MSEEPortChannel=StartPortChannel, IER=EndDevice, IERPortChannel=EndPortChannel


```

### Secondary MSEE - IER Information

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let secondarymsee=cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d
| where AzureSubscriptionId == subscriptionid
| where CircuitName == ExpressRouteCircuitName
| distinct SecondaryDeviceName;
cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks
| where StartDevice in (secondarymsee)
| where LinkType == "DeviceInterfaceLink"
| distinct MSEE=StartDevice, MSEEPortChannel=StartPortChannel, IER=EndDevice, IERPortChannel=EndPortChannel


```

### ExpressRoute Fast Path Routes

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let vrfids = cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d
| where AzureSubscriptionId == subscriptionid
| where CircuitName == ExpressRouteCircuitName
| distinct ServiceKey=AzureServiceKey
| join kind=leftouter cluster("Hybridnetworking").database("aznwmds").SubIntfTable on ServiceKey
| distinct VrfId;
cluster("hybridnetworking").database("aznwmds").Mseev2RoutesLogsTable 
| where SnapshotTimestamp >= starttime - 1h and SnapshotTimestamp<= endtime + 1h
| where VrfId in (vrfids) 
| distinct SnapshotTimestamp, VrfId, VnetId, Vni, DeviceName, IpPrefix, MacAddress, Nexthop,  OperationId, RoleInstance, Tenant
| summarize ConfigStartTime=min(SnapshotTimestamp), ConfigEndTime=max(SnapshotTimestamp) by VrfId, VnetId, Vni, DeviceName, IpPrefix, MacAddress, Nexthop,OperationId, RoleInstance, Tenant
| project ConfigStartTime, ConfigEndTime, DeviceName, IpPrefix, MacAddress, Nexthop,VrfId, VnetId, Vni, OperationId, RoleInstance, Tenant
```

### ExpressRoute Fast Path Routes

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let vrfids = cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d
| where AzureSubscriptionId == subscriptionid
| where CircuitName == ExpressRouteCircuitName
| distinct ServiceKey=AzureServiceKey
| join kind=leftouter cluster("Hybridnetworking").database("aznwmds").SubIntfTable on ServiceKey
| distinct VrfId;
cluster("hybridnetworking").database("aznwmds").Mseev2RoutesLogsTable 
| where SnapshotTimestamp >= starttime - 1h and SnapshotTimestamp<= endtime + 1h
| where VrfId in (vrfids) 
| distinct SnapshotTimestamp, VnetId, VrfId, DeviceName, IpPrefix, Nexthop, Vni, MacAddress
| summarize count() by SnapshotTimestamp,DeviceName
| render timechart
```

### ExpressRoute Circuit Global Reach Configuration

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let ErCircuitName=ExpressRouteCircuitName;
let selectedErSeviceKey=cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d
| where AzureSubscriptionId == subscriptionid
| where CircuitName == ErCircuitName
| distinct ServiceKey=AzureServiceKey;
cluster("Hybridnetworking").database("aznwmds").TunnelIntfTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d
| where ServiceKey  in (selectedErSeviceKey)
| where Description startswith "Circuit Connection from"
| distinct  DeviceName, VrfId, LocalMSEETunnelInterface=InterfaceName,LocalMSEEBGPIpAddress=IpAddress,LocalMSEEBGPIpAddressv6=IpAddressv6,LocalMSEETunnelIP=SourceIp, RemoteCircuitServiceKey=PeeredCircuitServiceKey, RemoteMSEETunnelIP=DestinationIp,  SourcePort,Description
```

### ExpressRoute Circuit For Microsoft Peering Route Filter Configuration

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let ErCircuitName=ExpressRouteCircuitName;
let selectedErSeviceKey=toscalar(cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d
| where AzureSubscriptionId == subscriptionid
| where CircuitName == ErCircuitName
| distinct ServiceKey=AzureServiceKey);
let RouteFilter=cluster("Hybridnetworking").database("aznwmds").RouteFilterTable
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d
| where CustomerSubscription == subscriptionid
| where Peerings contains selectedErSeviceKey
| distinct FilterResourceUri;
cluster("Hybridnetworking").database("aznwmds").RouteFilterRuleTable
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d
| where FilterResourceUri in (RouteFilter)
| extend ResourceURI=tostring(split(FilterResourceUri, "azure.com")[1])
| extend Communities= strcat_array(parse_xml(Communities)["ArrayOfString"]["string"], ", ")
| project PreciseTimeStamp, RuleName, ResourceURI, RuleType, Access, Communities
| order by PreciseTimeStamp asc 
| summarize ServicesEntryStartTime=min(PreciseTimeStamp), ServicesEntryEndTime=max(PreciseTimeStamp) by RuleName, ResourceURI, RuleType, Access, Communities
| project ServicesEntryStartTime, ServicesEntryEndTime, RuleName, ResourceURI, RuleType, Access, AdvertisedServices=Communities
| extend SupportBGPCommunities=iff(isnotempty(RuleName), strcat("https://learn.microsoft.com/en-us/azure/expressroute/expressroute-routing#bgp"), "")

```

### PV

```kql
let pv=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('kusto').adxpageview| where page contains "b01/expressroutecircuit";
let pvcount=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('microsoft').adxpageview | where page contains "b01/expressroutecircuit" | summarize count();
union pv, pvcount
```

### Blue Birds Agent Log

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let vrfids = cluster("Hybridnetworking").database("aznwmds").CircuitTable 
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime + 1d
| where AzureSubscriptionId == subscriptionid
| where CircuitName == ExpressRouteCircuitName
| distinct ServiceKey=AzureServiceKey
| join kind=leftouter cluster("Hybridnetworking").database("aznwmds").SubIntfTable on ServiceKey
| distinct VrfId;
let APICallOperationIdsFromDevice=cluster("hybridnetworking").database("aznwmds").Mseev2RoutesLogsTable 
| where SnapshotTimestamp >= starttime - 1h and SnapshotTimestamp<= endtime + 1h
| where VrfId in (vrfids) 
| distinct OperationId;
cluster("hybridnetworking").database("aznwmds").BlueBirdServiceLogsTable
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where ServicePrefix startswith "wavnet"
| where OperationId in (APICallOperationIdsFromDevice)
| where Message contains "reconcile" or Message contains "routes" or Message contains "dest:"
| project PreciseTimeStamp,OperationId, RoleInstance, Tenant, Level, Tid, Message
| order by PreciseTimeStamp asc
```

