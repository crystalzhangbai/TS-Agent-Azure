---
description: KQL queries for Azure Virtual WAN and Route Server
---

# Virtual WAN & Route Server Kusto Queries

> Source: Kusto

## Virtual WAN (vwan, vhub)

### Get Virtual Hub information (name, resource id(ArmId aka rsID or routeServiceId), region, address space, etc.) via HV_vhub name

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let vnetName = hubVnetName;
cluster("Hybridnetworking.kusto.windows.net").database("aznwmds").VirtualHubTable
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where VnetName contains vnetName
| project CustomerSubscriptionId, HubName, NrpResourceUri, Location, AddressSpace, VnetName, routeServiceId=ArmId , VpnGatewayArmId, VnetId
```

### Query Virtual WAN inter-hub routes from rsID, (Route Server GUID)

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let rsId = routeServiceId;
cluster("Hybridnetworking.kusto.windows.net").database("aznwmds").RouteServiceInterHubLog
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where RouteServiceId contains rsId
```

## Route Server (RS)

### Query the configuration of RS, input require Route Server GUID , rsId

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let rsId = routeServiceId;
cluster('hybridnetworking.kusto.windows.net').database('aznwmds').RouteServiceTable
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where RouteServiceId contains rsId
| project TIMESTAMP, ActualVnetId, VnetRanges,VnetId, RoutingDomainId, ASN,BgpCommunities, NMAgentVIP, RouteServiceVIPs, RouteServicePeeringIPs
```

### Query the features enabled in RS , input require Route Server GUID , rsId

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let vnetId = rsVnetId;
cluster('hybridnetworking.kusto.windows.net').database('aznwmds').VirtualHubTable
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where VnetId contains vnetId
| join kind=inner (RouteServiceTable) on $left.ArmId == $right.HubArmId
| project TIMESTAMP, HubName, NrpResourceUri, IsUnManagedHub, UnManagedHubAllowBranchToBranch, HubRoutingPreference, RouteServiceId
```

### Query RS BGP logs, number of NLRI advertised, input require Route Server GUID , rsId

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let rsId = routeServiceId;
cluster('hybridnetworking.kusto.windows.net').database('aznwmds').RouteServiceBgpLogsTable
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where Tenant contains rsId
| where Message contains "<BGP>"
| project TIMESTAMP, RoleInstance, Message
```

### Query RS BGP updates, route-map logs, input require Route Server GUID , rsId

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let rsId = routeServiceId;
cluster('hybridnetworking.kusto.windows.net').database('aznwmds').RouteServiceRoutingLog
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where RouteServiceId contains rsId
| project TIMESTAMP, RoleInstance, Message
```

### Query RS peer information, input require Route Server GUID , rsId

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let rsId = routeServiceId;
cluster('hybridnetworking.kusto.windows.net').database('aznwmds').RouteServicePeerConfigTable
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where RouteServiceId contains rsId
| project TIMESTAMP, RoleInstance, PeerIp, PeerAsn, PeerType, PeerVipAddress, PeerWeight
```

### Query RS RoleInstance information (like maintenance) input require Route Server GUID , rsId

```kql
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let rsId = routeServiceId;
cluster('hybridnetworking.kusto.windows.net').database('aznwmds').RouteServiceLogsTable
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where RouteServiceId contains rsId
| where Message !contains "thumbprint"
| where Message !contains "returning NULL"
| project PreciseTimeStamp, RoleInstance, Message
```
