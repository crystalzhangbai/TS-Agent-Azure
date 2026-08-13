---
description: KQL queries for Azure internet peering, monitoring, traffic collector, IPFIX/NetFlow/SFlow analysis.
---

# Internet Peering & Monitoring Kusto Queries

> Source: Azure Networking B01 Dashboard (aka.ms/b01)
> Pages: Internet-Peering, Internet-Monitoring, Traffic Collector, IPFIX(NetFlow) vs SFlow

## Internet-Peering

### Peer Info - Microsoft&Internet Routing Preference

```kql
let starttime = _startTime;
let endtime = _endTime;
let ASNPeer=cluster('azwanedge.westus2.kusto.windows.net').database('Peering').PeeringDataAsn_Prod | where IngestionTimeStamp >= starttime - 5d and IngestionTimeStamp <= endtime
| where PeerAsn == ISPASN
| distinct PeerAsn, PeerName
| summarize take_any(PeerName) by PeerAsn;
union cluster('azwanedge.westus2').database('Peering').PeeringDataDirect_Prod, cluster('azwanedge.westus2').database('Peering').PeeringDataExchange_Prod
| where IngestionTimestamp >= starttime - 5d and IngestionTimestamp <= endtime
| where PeerAsn == ISPASN
| summarize Configstarttime=min(IngestionTimestamp), Configendtime=max(IngestionTimestamp) by  PeerAsn,ProvisionedBandwidthInMbps, PeeringLocation, ProvisioningState, MicrosoftDeviceId,ConnectionState, MicrosoftSessionIPv4Address, MicrosoftSessionIPv6Address, PeerSessionIPv4Address, PeerSessionIPv6Address, PeeringSkuTier, PeeringSkuFamily, PeeringSkuSize, PeeringType,MasterSubscriptionId, MasterResourceGroupName, DirectPeeringType, MicrosoftPortId, SessionStateV4,SessionStateV6
| join kind=leftouter ASNPeer on PeerAsn
| project Configstarttime,Configendtime,PeerAsn, PeerName, PeeringSkuTier, PeeringSkuFamily, PeeringType, PeeringLocation,ConnectionState, ProvisionedBandwidthInMbps, DirectPeeringType,MicrosoftDeviceId, MicrosoftPortId,SessionStateV4, SessionStateV6, MicrosoftSessionIPv4Address, MicrosoftSessionIPv6Address





```

### RouteExchangeHistory

```kql
let starttime = _startTime;
let endtime = _endTime;
let prefix=iff(isnotempty(prefixfilter), prefixfilter, "a.b.c");
cluster('azwan').database('WanEdge').IteBmpRoutes
| where RouteReceivedTimestamp >= starttime - 15d and RouteReceivedTimestamp <= endtime
//| where PeerAsn == ISPASN
| where RouterName contains routername
| where PeerAsn != 8075
| where Prefix startswith prefix
| summarize arg_max(RouteReceivedTimestamp, RouterName, PeerIp, PeerAsn, PeerName, AddOrWithdraw, Prefix, AsPath, AsPathName) by RouterName, PeerIp, PeerAsn, PeerName, AddOrWithdraw, Prefix, AsPath, AsPathName
| project RouteReceivedTimestamp, RouterName, PeerIp, PeerAsn, PeerName, AddOrWithdraw, Prefix, AsPath, AsPathName


```

### ASN Information

```kql
let starttime= _startTime;
let endtime = _endTime;
let ASN = ISPASN;
cluster('azwanedge.westus2.kusto.windows.net').database('Peering').PeeringDataAsn_Prod
| where IngestionTimeStamp >= starttime - 1d and IngestionTimeStamp <= endtime
| where  PeerAsn == ASN
| distinct PeerAsnName, PeerAsn, PeerName, ErrorMessage, ValidationState, Role, Email, Phone, IsMapsProvider
| evaluate narrow()
| project Key=Column, Value
```

### BGP Down event between IER and the specific ISP

```kql
let starttime = _startTime;
let endtime = _endTime;
cluster('azwan').database('WanEdge').IteBmpPeerings
| where Timestamp >= starttime and Timestamp <= endtime
| where PeerAsn !in ("8075", "8069", "8068", "12076")
| where PeerAsn == ISPASN
| where State == "Down"
| project Timestamp, RouterName, LocalIp, LocalAsn, PeerIp, PeerAsn, PeerName, FourOctetAsNumCapable, AddPathCapable, State 
| summarize count() by bin(Timestamp, 1m), RouterName
| render columnchart 
```

### Best Effort Drop in IER devices Of ISPASN

```kql
let starttime = _startTime;
let endtime = _endTime;
let devices=materialize(cluster('azwan').database('WanEdge').IteBmpPeerings
| where Timestamp >= starttime - 30d and Timestamp <= endtime
| where PeerAsn !in ("8075", "8069", "8068", "12076")
| where PeerAsn == ISPASN
| distinct RouterName);
cluster('azwan').database('WanEdge').IteBestEffortDrops
| where IngestionTimestamp >= starttime and IngestionTimestamp <= endtime
| where DeviceName in~ (devices)
| project IngestionTimestamp, DeviceName, IfAddressV4, IfAddressV6, PacketsDropped, LinkSpeedInGbps=IfSpeed/1000, Utilization, IfDescription
| project IngestionTimestamp, DeviceName, PacketsDropped
| render columnchart 


```

### Max Loss Ratio between Internal CMTest Agent(In Azure DC) and The specific ASN

```kql
let starttime= _startTime;
let endtime = _endTime;
let ASN = iff(isnotempty(ISPASN), ISPASN, "plipala");
cluster('Aznwnetmon').database('ThousandEyes').CMTestMetrics
| where TestTime between (starttime .. endtime)
| where IngestionTenant !contains "dev"
| where TestName startswith "Peering"
| where TestName contains ASN
| extend Region=tostring(split(AgentName, "-")[2])
| extend Ier=tostring(split(TestName, "/")[1])
| extend Test=strcat(Region, "-->",Ier, "-->", TestId)
| summarize MaxLoss=max(Loss) by bin(TestTime, 1m), Test
| order by TestTime asc
| render timechart
```

### Max Latency between Internal CMTest Agent(In Azure DC) and The specific ASN

```kql
let starttime= _startTime;
let endtime = _endTime;
let ASN = iff(isnotempty(ISPASN), ISPASN, "plipala");
cluster('Aznwnetmon').database('ThousandEyes').CMTestMetrics
| where TestTime between (starttime .. endtime)
| where IngestionTenant !contains "dev"
| where TestName startswith "Peering"
| where TestName contains ASN
| extend Region=tostring(split(AgentName, "-")[2])
| extend Ier=tostring(split(TestName, "/")[1])
| extend Test=strcat(Region, "-->",Ier, "-->", TestId)
| summarize MaxLatency=max(AvgLatency) by bin(TestTime, 1m), Test
| order by TestTime asc
| render timechart
```

### Network Availability from ISP user in different Country to Office [Microsoft Network]

```kql
let starttime= _startTime;
let endtime = _endTime;
let ASN = ISPASN;
cluster("azwanedge.westus2").database("Peering").v3MOIAvailabilityAggregates_ASN_Country_Dest
| where env_time >= starttime and env_time <= endtime
| where clientAsn == ASN
| where destinationType in ('Outlook', 'Office', 'Akamai', 'GCP')
| where destinationType == "Office"
| summarize Availability=avg(availability) by bin(env_time,1m), destinationType, clientCountry
| project env_time, clientCountry, Availability
| render timechart 
//cluster('azwanedge.westus2').database('peering').MOIAvailability5minAggregates_ASN_Country
//| where env_time >= starttime and env_time <= endtime
//| where clientAsn == ASN
//| where availability != 100
//| summarize availability=avg(availability) by bin(env_time, 1m), clientCountry
//| project env_time, clientCountry, availability
//| render timechart  
```

### pv

```kql
let pv=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('kusto').adxpageview| where page contains "b01/internetpeering";
let pvcount=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('microsoft').adxpageview | where page contains "b01/internetpeering" | summarize count();
union pv, pvcount
```

### ITE Congestion Control observed with the AS  - Microsoft Routing Preference Only

```kql
let starttime= _startTime;
let endtime = _endTime;
let ASN = ISPASN;
let PeerInfo=cluster('azwan').database('WanEdge').IteBmpPeerings 
| where PeerAsn == ASN
| distinct PeerIp;
let PeerRouterName=cluster('azwan').database('WanEdge').IteBmpPeerings 
| where PeerAsn == ASN
| distinct RouterName;
cluster('phynetval').database('aznwmds').AzureAaaMasterSessions
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where deviceName in~ (PeerRouterName)
| where deviceName startswith "ter" or deviceName startswith "ier" or deviceName startswith "ipr"
| where command contains "exact reject"
| where command startswith "set policy-options policy-statement ITE-IngressCongestionControl"
| extend EdgePOP= tostring(extract(@"(\d{1,3}(?:\.\d{1,3}){3})", 1, command))
| extend IPPrefix = tostring(extract(@"(\d{1,3}(?:\.\d{1,3}){3}/\d{1,2})", 1, command))
| where EdgePOP in (PeerInfo)
| project PreciseTimeStamp, deviceName, EdgePOP, IPPrefix,command

```

### Peer Information

```kql
let starttime = _startTime;
let endtime = _endTime;
cluster('azwan').database('WanEdge').IteBmpPeerings
| where Timestamp >= starttime - 30d and Timestamp <= endtime
| where PeerAsn !in ("8075", "8069", "8068", "12076")
| where PeerAsn == ISPASN
| where RouterName contains routername
//| project Timestamp, RouterName, LocalIp, LocalAsn, PeerIp, PeerAsn, PeerName, FourOctetAsNumCapable, AddPathCapable, State 
| summarize Configstarttime=min(Timestamp), Configendtime=max(Timestamp) by RouterName, LocalIp, LocalAsn, PeerIp, PeerAsn, PeerName, FourOctetAsNumCapable, AddPathCapable, State 
| project Configstarttime,Configendtime, RouterName, LocalIp, LocalAsn, PeerIp, PeerAsn, PeerName, FourOctetAsNumCapable, AddPathCapable, State 
```

### Network Availability from ISP user in different Country to GCP

```kql
let starttime= _startTime;
let endtime = _endTime;
let ASN = ISPASN;
cluster("azwanedge.westus2").database("Peering").v3MOIAvailabilityAggregates_ASN_Country_Dest
| where env_time >= starttime and env_time <= endtime
| where clientAsn == ASN
| where destinationType in ('Outlook', 'Office', 'Akamai', 'GCP')
| where destinationType == "GCP"
| summarize Availability=avg(availability) by bin(env_time,1m), destinationType, clientCountry
| project env_time, clientCountry, Availability
| render timechart 
//cluster('azwanedge.westus2').database('peering').MOIAvailability5minAggregates_ASN_Country
//| where env_time >= starttime and env_time <= endtime
//| where clientAsn == ASN
//| where availability != 100
//| summarize availability=avg(availability) by bin(env_time, 1m), clientCountry
//| project env_time, clientCountry, availability
//| render timechart  
```

### Network Availability from ISP user in different Country to Outlook [Microsoft Network]

```kql
let starttime= _startTime;
let endtime = _endTime;
let ASN = ISPASN;
cluster("azwanedge.westus2").database("Peering").v3MOIAvailabilityAggregates_ASN_Country_Dest
| where env_time >= starttime and env_time <= endtime
| where clientAsn == ASN
| where destinationType in ('Outlook', 'Office', 'Akamai', 'GCP')
| where destinationType == "Outlook"
| summarize Availability=avg(availability) by bin(env_time,1m), destinationType, clientCountry
| project env_time, clientCountry, Availability
| render timechart 
//cluster('azwanedge.westus2').database('peering').MOIAvailability5minAggregates_ASN_Country
//| where env_time >= starttime and env_time <= endtime
//| where clientAsn == ASN
//| where availability != 100
//| summarize availability=avg(availability) by bin(env_time, 1m), clientCountry
//| project env_time, clientCountry, availability
//| render timechart  
```

### Network Availability from ISP user in different Country to Akamai

```kql
let starttime= _startTime;
let endtime = _endTime;
let ASN = ISPASN;
cluster("azwanedge.westus2").database("Peering").v3MOIAvailabilityAggregates_ASN_Country_Dest
| where env_time >= starttime and env_time <= endtime
| where clientAsn == ASN
| where destinationType in ('Outlook', 'Office', 'Akamai', 'GCP')
| where destinationType == "Akamai"
| summarize Availability=avg(availability) by bin(env_time,1m), destinationType, clientCountry
| project env_time, clientCountry, Availability
| render timechart 
//cluster('azwanedge.westus2').database('peering').MOIAvailability5minAggregates_ASN_Country
//| where env_time >= starttime and env_time <= endtime
//| where clientAsn == ASN
//| where availability != 100
//| summarize availability=avg(availability) by bin(env_time, 1m), clientCountry
//| project env_time, clientCountry, availability
//| render timechart  
```

## Internet-Monitoring

### Avg Latency between external CMTest Agent and Azure Region (Storage) - Internet Routing Preference 

```kql
let starttime= _startTime;
let endtime = _endTime;
let Regionz = todynamic(InternetMonitorRegion);
cluster('Aznwnetmon').database('ThousandEyes').CMTestMetrics
| where TestTime between (starttime .. endtime)
| where TestName startswith "RP/Storage"
| where IngestionTenant !contains "dev"
| extend Region = extract("RP/Storage-(.*)-(.*)", 1, TestName)
| where Region in~ (Regionz)
| summarize AvgLatency = floor(avg(AvgLatency), 1) by Region, bin(TestTime, 1m)
| order by TestTime asc
| render timechart
```

### Avg Loss Ratio between external CMTest Agent and Azure Region (Storage) - Microsoft Routing Preference 

```kql
let starttime= _startTime;
let endtime = _endTime;
let RegionMap = datatable(CMTMRegion: string, SSRegion: string)
[
"canadacentral", "canadacentral",
"northeurope", "europenorth",
"uaecentral", "uaec",
"southafricawest", "southafricaw",
"koreasouth", "koreasouth",
"westus3", "uswest3",
"japaneast", "japaneast",
"gcp", "gcp",
"australiaeast", "australiaeast",
"australiacentral2", "australiac",
"northcentralus", "usnorth",
"australiasoutheast", "australiasoutheast",
"norwayeast", "norwaye",
"australiacentral", "australiac",
"koreacentral", "koreacentral",
"francecentral", "francec",
"germanynorth", "",
"switzerlandnorth", "germanyn",
"qatarcentral", "qatarc",
"ukwest", "ukwest",
"westus", "uswest",
"norwaywest", "norwayw",
"centralus", "uscentral",
"westus2", "uswest2",
"francesouth", "frances",
"germanywestcentral", "germanywc",
"southeastasia", "asiasoutheast",
"westeurope", "europewest",
"westcentralus", "uswestcentral",
"japanwest", "japanwest",
"uaenorth", "uaen",
"italynorth", "italyn",
"southindia", "indiasouth",
"canadaeast", "canadaeast",
"eastasia", "asiaeast",
"uksouth", "uksouth",
"eastus2", "useast2",
"southafricanorth", "southafrican",
"southcentralus", "southcentralus",
"centralindia", "indiacentral",
"eastus", "useast",
"brazilsouth", "brazilsouth",
"switzerlandwest", "switzerlandw",
"israelcentral", "israelc",
"westindia", "indiawest",
"polandcentral", "polandc",
"aws", "aws",
"swedencentral", "swedenc"
];
let Regionz = todynamic(InternetMonitorRegion);
let ARMRegion=RegionMap
| where CMTMRegion  in~ (Regionz)
| distinct SSRegion;
let clusterzz = cluster('Azurecm').database('AzureCM').LogClusterSnapshot
| where PreciseTimeStamp >= now(-1h)
| where Region in~ (ARMRegion)
| distinct Tenant;
cluster('Aznwnetmon').database('ThousandEyes').CMTestMetrics
| where TestTime between (starttime .. endtime)
| where IngestionTenant !contains "dev"
| where TestId contains "netmon.azure.com"
| extend cluster=tostring(split(TestId, "-")[0])
| where cluster in~ (clusterzz)
| summarize AvgLoss = avg(Loss) by cluster, bin(TestTime, 1m)
| order by TestTime asc
| render timechart
```

### Avg Latency between Internal CMTest Agent(In Azure DC) and External Network over IER 

```kql
let starttime= _startTime;
let endtime = _endTime;
let Regionz = todynamic(InternetMonitorRegion);
cluster('Aznwnetmon').database('ThousandEyes').CMTestMetrics
| where TestTime between (starttime .. endtime)
| where IngestionTenant !contains "dev"
| where TestName startswith "Peering"
| extend Region=tostring(split(AgentName, "-")[2])
| where Region in~ (Regionz)
| summarize AvgLatency=avg(AvgLatency) by bin(TestTime, 1m), AS=tostring(split(split(TestName, "/")[2], "AS")[1])
| order by TestTime asc
| render timechart
```

### Avg Loss Ratio between Internal CMTest Agent(In Azure DC) and External Network over IER 

```kql
let starttime= _startTime;
let endtime = _endTime;
let Regionz = todynamic(InternetMonitorRegion);
cluster('Aznwnetmon').database('ThousandEyes').CMTestMetrics
| where TestTime between (starttime .. endtime)
| where IngestionTenant !contains "dev"
| where TestName startswith "Peering"
| extend Region=tostring(split(AgentName, "-")[2])
| where Region in~ (Regionz)
| summarize AvgLoss=avg(Loss) by bin(TestTime, 1m), AS=tostring(split(split(TestName, "/")[2], "AS")[1])
| order by TestTime asc
| render timechart
```

### Avg Loss Ratio between external CMTest Agent and Azure Region (Storage) - Internet Routing Preference 

```kql
let starttime= _startTime;
let endtime = _endTime;
let Regionz = todynamic(InternetMonitorRegion);
cluster('Aznwnetmon').database('ThousandEyes').CMTestMetrics
| where TestTime between (starttime .. endtime)
| where TestName startswith "RP/Storage"
| where IngestionTenant !contains "dev"
| extend Region = extract("RP/Storage-(.*)-(.*)", 1, TestName)
| where Region in~ (Regionz)
| summarize Loss = floor(avg(Loss), 1) by Region, bin(TestTime, 1m)
| order by TestTime asc
| render timechart
```

### Avg Latency between external CMTest Agent and TER DC - Internet Routing Preference VIPs

```kql
let starttime= _startTime;
let endtime = _endTime;
let RegionMap = datatable(CMTMRegion: string, SSRegion: string)
[
"canadacentral", "canadacentral",
"northeurope", "europenorth",
"uaecentral", "uaec",
"southafricawest", "southafricaw",
"koreasouth", "koreasouth",
"westus3", "uswest3",
"japaneast", "japaneast",
"gcp", "gcp",
"australiaeast", "australiaeast",
"australiacentral2", "australiac",
"northcentralus", "usnorth",
"australiasoutheast", "australiasoutheast",
"norwayeast", "norwaye",
"australiacentral", "australiac",
"koreacentral", "koreacentral",
"francecentral", "francec",
"germanynorth", "",
"switzerlandnorth", "germanyn",
"qatarcentral", "qatarc",
"ukwest", "ukwest",
"westus", "uswest",
"norwaywest", "norwayw",
"centralus", "uscentral",
"westus2", "uswest2",
"francesouth", "frances",
"germanywestcentral", "germanywc",
"southeastasia", "asiasoutheast",
"westeurope", "europewest",
"westcentralus", "uswestcentral",
"japanwest", "japanwest",
"uaenorth", "uaen",
"italynorth", "italyn",
"southindia", "indiasouth",
"canadaeast", "canadaeast",
"eastasia", "asiaeast",
"uksouth", "uksouth",
"eastus2", "useast2",
"southafricanorth", "southafrican",
"southcentralus", "southcentralus",
"centralindia", "indiacentral",
"eastus", "useast",
"brazilsouth", "brazilsouth",
"switzerlandwest", "switzerlandw",
"israelcentral", "israelc",
"westindia", "indiawest",
"polandcentral", "polandc",
"aws", "aws",
"swedencentral", "swedenc"
];
let Regionz = todynamic(InternetMonitorRegion);
let ARMRegion=RegionMap
| where CMTMRegion  in~ (Regionz)
| distinct SSRegion;
let TERDeviceName = cluster("Azphynet").database("azdhmds").DeviceStatic
| where DeviceName startswith "ter"
| distinct DeviceName, Regions
| where Regions in~ (ARMRegion)
| distinct DeviceName;
cluster('Aznwnetmon').database('ThousandEyes').CMTestMetrics
| where TestTime between (starttime .. endtime)
| where IngestionTenant !contains "dev"
| extend AgentName = substring(AgentName,11)
| where TestName startswith "rp/terprobe"
| extend Ter=tostring(split(TestName, "/terprobe/")[1])
| where Ter in~ (TERDeviceName)
| extend dc=tostring(split(Ter, ".")[1])
| summarize AvgLatency=avg(AvgLatency) by bin(IngestionTimestamp,1m),dc
| render timechart
```

### Avg Loss Ratio between external CMTest Agent and TER DC - Internet Routing Preference VIPs

```kql
let starttime= _startTime;
let endtime = _endTime;
let RegionMap = datatable(CMTMRegion: string, SSRegion: string)
[
"canadacentral", "canadacentral",
"northeurope", "europenorth",
"uaecentral", "uaec",
"southafricawest", "southafricaw",
"koreasouth", "koreasouth",
"westus3", "uswest3",
"japaneast", "japaneast",
"gcp", "gcp",
"australiaeast", "australiaeast",
"australiacentral2", "australiac",
"northcentralus", "usnorth",
"australiasoutheast", "australiasoutheast",
"norwayeast", "norwaye",
"australiacentral", "australiac",
"koreacentral", "koreacentral",
"francecentral", "francec",
"germanynorth", "",
"switzerlandnorth", "germanyn",
"qatarcentral", "qatarc",
"ukwest", "ukwest",
"westus", "uswest",
"norwaywest", "norwayw",
"centralus", "uscentral",
"westus2", "uswest2",
"francesouth", "frances",
"germanywestcentral", "germanywc",
"southeastasia", "asiasoutheast",
"westeurope", "europewest",
"westcentralus", "uswestcentral",
"japanwest", "japanwest",
"uaenorth", "uaen",
"italynorth", "italyn",
"southindia", "indiasouth",
"canadaeast", "canadaeast",
"eastasia", "asiaeast",
"uksouth", "uksouth",
"eastus2", "useast2",
"southafricanorth", "southafrican",
"southcentralus", "southcentralus",
"centralindia", "indiacentral",
"eastus", "useast",
"brazilsouth", "brazilsouth",
"switzerlandwest", "switzerlandw",
"israelcentral", "israelc",
"westindia", "indiawest",
"polandcentral", "polandc",
"aws", "aws",
"swedencentral", "swedenc"
];
let Regionz = todynamic(InternetMonitorRegion);
let ARMRegion=RegionMap
| where CMTMRegion  in~ (Regionz)
| distinct SSRegion;
let TERDeviceName = cluster("Azphynet").database("azdhmds").DeviceStatic
| where DeviceName startswith "ter"
| distinct DeviceName, Regions
| where Regions in~ (ARMRegion)
| distinct DeviceName;
cluster('Aznwnetmon').database('ThousandEyes').CMTestMetrics
| where TestTime between (starttime .. endtime)
| where IngestionTenant !contains "dev"
| extend AgentName = substring(AgentName,11)
| where TestName startswith "rp/terprobe"
| extend Ter=tostring(split(TestName, "/terprobe/")[1])
| where Ter in~ (TERDeviceName)
| extend dc=tostring(split(Ter, ".")[1])
| summarize AvgLoss=avg(Loss) by bin(IngestionTimestamp,1m),dc
| render timechart
```

### Avg Latency between external CMTest Agent and Azure Region (Storage) - Microsoft Routing Preference 

```kql
let starttime= _startTime;
let endtime = _endTime;
let RegionMap = datatable(CMTMRegion: string, SSRegion: string)
[
"canadacentral", "canadacentral",
"northeurope", "europenorth",
"uaecentral", "uaec",
"southafricawest", "southafricaw",
"koreasouth", "koreasouth",
"westus3", "uswest3",
"japaneast", "japaneast",
"gcp", "gcp",
"australiaeast", "australiaeast",
"australiacentral2", "australiac",
"northcentralus", "usnorth",
"australiasoutheast", "australiasoutheast",
"norwayeast", "norwaye",
"australiacentral", "australiac",
"koreacentral", "koreacentral",
"francecentral", "francec",
"germanynorth", "",
"switzerlandnorth", "germanyn",
"qatarcentral", "qatarc",
"ukwest", "ukwest",
"westus", "uswest",
"norwaywest", "norwayw",
"centralus", "uscentral",
"westus2", "uswest2",
"francesouth", "frances",
"germanywestcentral", "germanywc",
"southeastasia", "asiasoutheast",
"westeurope", "europewest",
"westcentralus", "uswestcentral",
"japanwest", "japanwest",
"uaenorth", "uaen",
"italynorth", "italyn",
"southindia", "indiasouth",
"canadaeast", "canadaeast",
"eastasia", "asiaeast",
"uksouth", "uksouth",
"eastus2", "useast2",
"southafricanorth", "southafrican",
"southcentralus", "southcentralus",
"centralindia", "indiacentral",
"eastus", "useast",
"brazilsouth", "brazilsouth",
"switzerlandwest", "switzerlandw",
"israelcentral", "israelc",
"westindia", "indiawest",
"polandcentral", "polandc",
"aws", "aws",
"swedencentral", "swedenc"
];
let Regionz = todynamic(InternetMonitorRegion);
let ARMRegion=RegionMap
| where CMTMRegion  in~ (Regionz)
| distinct SSRegion;
let clusterzz = cluster('Azurecm').database('AzureCM').LogClusterSnapshot
| where PreciseTimeStamp >= now(-1h)
| where Region in~ (ARMRegion)
| distinct Tenant;
cluster('Aznwnetmon').database('ThousandEyes').CMTestMetrics
| where TestTime between (starttime .. endtime)
| where IngestionTenant !contains "dev"
| where TestId contains "netmon.azure.com"
| extend cluster=tostring(split(TestId, "-")[0])
| where cluster in~ (clusterzz)
| summarize AvgLatency = avg(AvgLatency)  by cluster, bin(TestTime, 1m)
| order by TestTime asc
| render timechart
```

### PV

```kql
let pv=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('kusto').adxpageview| where page contains "b01/internetmonitoring";
let pvcount=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('microsoft').adxpageview | where page contains "b01/internetmonitoring" | summarize count();
union pv, pvcount
```

## Traffic Collector

### Traffic Collector under the subscription

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = iff(isnotempty(SubscriptionID), SubscriptionID, "plipala");
cluster('hybridnetworking').database('aznwmds').AtcTenant
| where TIMESTAMP >= starttime - 1d and TIMESTAMP <= endtime + 1d
| where resourceId contains subscriptionid
//| extend SubscriptionId = extract("/SUBSCRIPTIONS/([^/]+)/RESOURCEGROUPS/", 1, resourceId)
| extend Name=tostring(split(resourceId, "/")[-1])
| distinct Name, ResourceID=resourceId, ServicePrefix, Region, Tenant
```

### ExpressRoute Circuit under the selected Traffic Collector. ATC pulls this data from NFVRP

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = iff(isnotempty(SubscriptionID), SubscriptionID, "plipala");
let ATCErCount=toscalar(cluster('hybridnetworking').database('aznwmds').AtcTenant
| where TIMESTAMP >= starttime - 1d and TIMESTAMP <= endtime + 1d
| where resourceId contains subscriptionid
| extend Name=tostring(split(resourceId, "/")[-1])
| where Name == TCN
| where message contains "ATC circuit config ["
| summarize Configstarttime=min(TIMESTAMP), Configendtime=max(TIMESTAMP) by Name, message 
| extend formatstring=replace_string(message, "ATC Circuit config ", "")
| extend ATCConfiguration=parse_json(substring(formatstring, 0, strlen(formatstring) - 1))
| distinct ExpressRouteCircuitNumber=array_length(ATCConfiguration));
cluster('hybridnetworking').database('aznwmds').AtcTenant
| where TIMESTAMP >= starttime - 1d and TIMESTAMP <= endtime + 1d
| where resourceId contains subscriptionid
| extend Name=tostring(split(resourceId, "/")[-1])
| where Name == TCN
| where message contains "ATC circuit config ["
| summarize Configstarttime=min(TIMESTAMP), Configendtime=max(TIMESTAMP) by Name, message 
| extend formatstring=replace_string(message, "ATC Circuit config ", "")
| extend ATCConfiguration=parse_json(substring(formatstring, 0, strlen(formatstring) - 1))
| extend ExpressRouteCircuitNumber=array_length(ATCConfiguration)
| project Configstarttime,Configendtime, Name, ExpressRouteCircuitNumber, ATCConfiguration
//| project ATCConfiguration
//range i from 0 to toint(ATCErCount) step 1
//| project CircuitResourceURI=ATCErConfig[i].ExRCircuitId,ExRCircuitServiceKey=ATCErConfig[i].ExRCircuitServiceKey,DirectPortID=ATCErConfig[i].ExRCircuitDirectPortId
//| where CircuitResourceURI != ""
//| extend CircuitResourceURI=split(CircuitResourceURI, "/")
//| project CircuitName=CircuitResourceURI[8],ServiceKey=ExRCircuitServiceKey, Subscription=CircuitResourceURI[2], DirectPortID

```

### ATC Dashboard

```kql
let starttime= _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let subscriptionid = iff(isnotempty(SubscriptionID), SubscriptionID, "plipala");
let TCNname = TCN;
let TCId=cluster('hybridnetworking').database('aznwmds').AtcTenant
| where TIMESTAMP >= starttime - 1d and TIMESTAMP <= endtime + 1d
| where resourceId contains subscriptionid
| where resourceId contains TCNname
| distinct ResourceID=resourceId;
cluster('hybridnetworking').database('NfvRpMds').AzureTrafficCollectorTable
| where env_time >= starttime - 1d and env_time <= endtime
| where AtcResourceId in~ (TCId)
| extend AtcELB=strcat("/subscriptions/",AtcSubscriptionId,"/resourceGroups/", ResourceGroupName, "/providers/Microsoft.Network/loadBalancers/atctenantlb")
| extend AtcVMSS=strcat("/subscriptions/",AtcSubscriptionId,"/resourceGroups/", ResourceGroupName, "/providers/Microsoft.Compute/virtualMachineScaleSets/atctenant")
| extend AtcMetricsDashboard=strcat("https://portal.microsoftgeneva.com/s/7015AB64?overrides=[{%22query%22:%22//*[id='Location']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='RoleInstance']%22,%22key%22:%22value%22,%22replacement%22:%22%22},{%22query%22:%22//*[id='ResourceID']%22,%22key%22:%22value%22,%22replacement%22:%22",AtcResourceId,"%22}]&globalStartTime=",startunixtime, "&globalEndTime=", endunixtime, "&pinGlobalTimeRange=true")
| extend AtcControlPlaneLog=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH-mm-ss'),"Z&p-_endTime=", format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime, 'HH-mm-ss'), "Z&p-SubscriptionID=", CustomerSubscriptionId,"&p-ResourceURI=v-", AtcResourceId, "&p-CorrelationId=v-CorrelationRequestId&p-HttpMethod=all&p-taskname=v-HttpIncomingRequestStart#d1d4e231-22ae-4d17-95f9-eecac5ed1695")
| extend AtcVipTroubleshooting=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-VIP=v-", Vip,"#a172102b-f768-4cc9-982f-0acc07d4765f")
| distinct env_cloud_location, CustomerSubscriptionId, ResourceGuid, AtcSubscriptionId, ResourceGroupName, TenantVersion, Zones, AtcVip=Vip, VmSku, GatewayId, ProvisioningState,AtcELB,AtcVMSS, AtcVipTroubleshooting,AtcControlPlaneLog, AtcMetricsDashboard
| evaluate narrow()
| project Key=Column, Value
```

### ATC Tenant Log - Filtering Log by putting "Keywords" in TenantLogFilter parameter : As sample for keywords "_1" which will only filter role instance atctenant_1 log

```kql
let starttime= _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let subscriptionid = iff(isnotempty(SubscriptionID), SubscriptionID, "plipala");
let TCNname = TCN;
let AtcTenantLogFilter = ATCTenantLogFilter;
let TCId=cluster('hybridnetworking').database('aznwmds').AtcTenant
| where TIMESTAMP >= starttime - 1d and TIMESTAMP <= endtime + 1d
| where resourceId contains subscriptionid
| where resourceId contains TCNname
| distinct ResourceID=resourceId;
cluster('hybridnetworking').database('aznwmds').AtcTenant
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where resourceId in~ (TCId)
| where RoleInstance contains AtcTenantLogFilter or message contains AtcTenantLogFilter
| project PreciseTimeStamp, Role, RoleInstance, level, message

```

### ATC Tenant Error Log 

```kql
let starttime= _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let subscriptionid = iff(isnotempty(SubscriptionID), SubscriptionID, "plipala");
let TCNname = TCN;
let TCId=cluster('hybridnetworking').database('aznwmds').AtcTenant
| where TIMESTAMP >= starttime - 1d and TIMESTAMP <= endtime + 1d
| where resourceId contains subscriptionid
| where resourceId contains TCNname
| distinct ResourceID=resourceId;
cluster('hybridnetworking').database('aznwmds').AtcTenant
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where resourceId in~ (TCId)
| where level != "Information"
| project PreciseTimeStamp, Role, RoleInstance, level, message

```

### ATC LB Load Balancing Rule Configuration + Instance Metrics

```kql
let starttime= _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let subscriptionid = iff(isnotempty(SubscriptionID), SubscriptionID, "plipala");
let TCNname = TCN;
let TCId=cluster('hybridnetworking').database('aznwmds').AtcTenant
| where TIMESTAMP >= starttime - 1d and TIMESTAMP <= endtime + 1d
| where resourceId contains subscriptionid
| where resourceId contains TCNname
| distinct ResourceID=resourceId;
let TCVIP=cluster('hybridnetworking').database('NfvRpMds').AzureTrafficCollectorTable
| where env_time >= starttime - 1d and env_time <= endtime
| where AtcResourceId in~ (TCId)
| distinct Vip;
cluster('Azslb').database('azslbmds').DipEndpointProbeHistoryEvent 
| where TIMESTAMP > starttime - 2h and TIMESTAMP <= endtime
| where Vip in (TCVIP)
| join kind=leftouter cluster('AzureCM').database('AzureCM').LogContainerSnapshot on $left.ContainerId == $right.containerId
| where PreciseTimeStamp > starttime - 4h and PreciseTimeStamp <= endtime
| distinct  NrpLoadBalancerId,Vip, VipPort, DipCA, DipPort, ProbeType, ProbePort,Region,DataCenter=DC, Tenant=Cluster, nodeId=toupper(NodeId), containerId=ContainerId, roleInstanceName
| join kind=leftouter(cluster('aznwcc').database('aznwmds').Servers) on $left.nodeId == $right.NodeId
| join kind=leftouter(cluster('aznwcc').database('aznwmds').DeviceInterfaceLinks) on $left.DeviceName == $right.StartDevice
| join kind=inner (cluster("azurehn.kusto.windows.net").database("Azurehn").MdmVfpVnetAccountMaps() | extend Cluster=tolower(Cluster)) on $left.Tenant == $right.Cluster
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
| distinct  NrpLoadBalancerId,Vip, VipPort, DipCA, DipPort, ProbeType, ProbePort,Region,DataCenter, Tenant, nodeId=NodeId, containerId, roleInstanceName,VFPDashBoard, VFPDropDashBoard, SupportDashBoard, DropDashBoard, FPGADashboard, InvestigateNode, ASIHostNode, NetVMA, PerVMAvailability, PerProcessorPNICDashboard,VFPFullRule, ListUnifiedFlow
```

### PV

```kql
let pv=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('kusto').adxpageview| where page contains "b01/trafficcollectors";
let pvcount=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('microsoft').adxpageview | where page contains "b01/trafficcollectors" | summarize count();
union pv, pvcount
```

### RegistrationTelemetry - Diagnostic Setting

```kql
let starttime= _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let subscriptionid = iff(isnotempty(SubscriptionID), SubscriptionID, "plipala");
let TCNname = TCN;
let TCId=cluster('hybridnetworking').database('aznwmds').AtcTenant
| where TIMESTAMP >= starttime - 1d and TIMESTAMP <= endtime + 1d
| where resourceId contains subscriptionid
| where resourceId contains TCNname
| distinct ResourceID=resourceId;
cluster('Azureinsights.kusto.windows.net').database('Insights').RegistrationTelemetry
| where PreciseTimeStamp > starttime - 3d and PreciseTimeStamp < endtime 
| where resourceId in~ (TCId)
| extend EventHubNameSpace=tostring(split(eventHubAuthorizationRuleId, "/authorizationrules/RootManageSharedAccessKey")[0])
| project PreciseTimeStamp, TrafficCollectName=tostring(split(resourceId, "MICROSOFT.NETWORKFUNCTION/AZURETRAFFICCOLLECTORS/")[1]), categories,usingServiceBus, usingStorage, usingOms, storageAccount, EventHubNameSpace,EventHubName=eventHubName, eventHubLocation, blobName, creationTimeDate, lastModifiedTimeDate
```

### Number of Record in Resource Provider's Blob

```kql
let starttime= _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let subscriptionid = iff(isnotempty(SubscriptionID), SubscriptionID, "plipala");
let TCNname = TCN;
let TCId=cluster('hybridnetworking').database('aznwmds').AtcTenant
| where TIMESTAMP >= starttime - 1d and TIMESTAMP <= endtime + 1d
| where resourceId contains subscriptionid
| where resourceId contains TCNname
| distinct ResourceID=resourceId;
cluster('Azureinsights.kusto.windows.net').database('Insights').InputBlobFirstTagMetadata
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp < endtime 
| where firstTagValue in~ (TCId)
| project PreciseTimeStamp, Tenant, Role, serviceIdentity, firstTagValue, numberOfRecords, blobPath
| summarize numberOfRecords=sum(numberOfRecords) by bin(PreciseTimeStamp, 1m)
| render timechart 
```

## IPFIX(NetFlow) vs SFlow

### IPFIX - Core | SrcIpPrefix ----> DstIpPrefix 

```kql
let starttime = _startTime;
let endtime = _endTime;
let SrcIp=iff(isnotempty(SrcIpPrefix), SrcIpPrefix, "a.b.c");
let DstIp=iff(isnotempty(DstIpPrefix), DstIpPrefix, "x.y.z");
let SrcIps=iff(SrcIp == "a.b.c" and DstIp != "x.y.z", "", SrcIp);
let DstIps=iff(SrcIp != "a.b.c" and DstIp == "x.y.z", "", DstIp);
cluster('netcapplan').database('NetCapPlan').RealTimeIpfixWithMetadata
| where TimeStamp >= starttime and TimeStamp <= endtime
| where RouterName !startswith "ier"
| where SrcIpAddress startswith SrcIps or SrcIpAddress in (pack_array(split(SrcIps, ","))[0])
| where DstIpAddress startswith DstIps or DstIpAddress in (pack_array(split(DstIps, ","))[0])
| extend Device=tostring(strcat(RouterName, "---->InterfaceName: ", IngressIfName))
| project TimeStamp , RouterName, IngressIfName, EgressIfName, SrcIpAddress, DstIpAddress, DstTransportPort, SrcAs, DstAs, NextHop,Device
| order by TimeStamp desc | order by RouterName
| summarize count() by Device, bin(TimeStamp, 1m)
| render timechart

```

### IPFIX - Core | DstIpPrefix ----> SrcIpPrefix  

```kql
let starttime = _startTime;
let endtime = _endTime;
let SrcIp=iff(isnotempty(SrcIpPrefix), SrcIpPrefix, "a.b.c");
let DstIp=iff(isnotempty(DstIpPrefix), DstIpPrefix, "x.y.z");
let SrcIps=iff(SrcIp == "a.b.c" and DstIp != "x.y.z", "", SrcIp);
let DstIps=iff(SrcIp != "a.b.c" and DstIp == "x.y.z", "", DstIp);
cluster('netcapplan').database('NetCapPlan').RealTimeIpfixWithMetadata
| where TimeStamp >= starttime and TimeStamp <= endtime
| where RouterName !startswith "ier"
| where SrcIpAddress startswith DstIps or SrcIpAddress in (pack_array(split(DstIps, ","))[0])
| where DstIpAddress startswith SrcIps or DstIpAddress in (pack_array(split(SrcIps, ","))[0])
| extend Device=tostring(strcat(RouterName, "---->InterfaceName: ", EgressIfName))
| project TimeStamp , RouterName, IngressIfName, EgressIfName, SrcIpAddress, DstIpAddress, DstTransportPort, SrcAs, DstAs, NextHop,Device
| order by TimeStamp desc | order by RouterName
| summarize count() by Device, bin(TimeStamp, 1m)
| render timechart
```

### sFlow - TER Only | Internet Routing Preference | SrcIpPrefix ----> DstIpPrefix

```kql
let starttime = _startTime;
let endtime = _endTime;
let SrcIp=iff(isnotempty(SrcIpPrefix), SrcIpPrefix, "a.b.c");
let DstIp=iff(isnotempty(DstIpPrefix), DstIpPrefix, "x.y.z");
let SrcIps=iff(SrcIp == "a.b.c" and DstIp != "x.y.z", "", SrcIp);
let DstIps=iff(SrcIp != "a.b.c" and DstIp == "x.y.z", "", DstIp);
cluster('azwanedge.westus2.kusto.windows.net').database('ITE').WANsFlow
| where Timestamp >= starttime and Timestamp <= endtime
| where SourceIp startswith SrcIps or SourceIp in (pack_array(split(SrcIps, ","))[0])
| where DestinationIp startswith DstIps or DestinationIp in (pack_array(split(DstIps, ","))[0])
| order by Timestamp desc | order by DeviceName
| summarize Entry=count() by DeviceName=strcat(DeviceName, "-IngressInt:", IngressInterface), bin(Timestamp, 1m)
| render timechart
//| summarize Gbps = sum(EstimatedMbps)/1000 by DeviceName, bin(Timestamp, 1m)
//| project Timestamp, Gbps
//| render timechart 


```

### sFlow - TER Only | Internet Routing Preference | DstIpPrefix ----> SrcIpPrefix

```kql
let starttime = _startTime;
let endtime = _endTime;
let SrcIp=iff(isnotempty(SrcIpPrefix), SrcIpPrefix, "a.b.c");
let DstIp=iff(isnotempty(DstIpPrefix), DstIpPrefix, "x.y.z");
let SrcIps=iff(SrcIp == "a.b.c" and DstIp != "x.y.z", "", SrcIp);
let DstIps=iff(SrcIp != "a.b.c" and DstIp == "x.y.z", "", DstIp);
cluster('azwanedge.westus2.kusto.windows.net').database('ITE').WANsFlow
| where Timestamp >= starttime and Timestamp <= endtime
| where SourceIp startswith DstIps or SourceIp in (pack_array(split(DstIps, ","))[0])
| where DestinationIp startswith SrcIps or DestinationIp in (pack_array(split(SrcIps, ","))[0])
| order by Timestamp desc | order by DeviceName
| summarize Entry=count() by DeviceName=strcat(DeviceName, "-EgressInt:", EgressInterface), bin(Timestamp, 1m)
| render timechart
//| summarize Gbps = sum(EstimatedMbps)/1000 by DeviceName, bin(Timestamp, 1m)
//| project Timestamp, Gbps
//| render timechart 

```

### IPFIX - Backbone | SrcIpPrefix ---->DstIpPrefix

```kql
let starttime = _startTime;
let endtime = _endTime;
let SrcIp=iff(isnotempty(SrcIpPrefix), SrcIpPrefix, "a.b.c");
let DstIp=iff(isnotempty(DstIpPrefix), DstIpPrefix, "x.y.z");
let SrcIps=iff(SrcIp == "a.b.c" and DstIp != "x.y.z", "", SrcIp);
let DstIps=iff(SrcIp != "a.b.c" and DstIp == "x.y.z", "", DstIp);
let m = cluster("aznwalertingbackup").database("aznwmds").DeviceStatic 
| where CloudType == "Public"
| where DeploymentType in ("Core", "ExpressRoute") or (DeploymentType =~ "Fabric" and NgsDeviceType =~ "VpnAggregator")
| where Vender in ("Juniper", "Cisco", "Arista")
| project DeviceName, IPs = pack_array(StaticIP, ManagementIP)
| mv-expand DeviceIp = IPs
| where DeviceIp != "0.0.0.0"
| summarize by DeviceName, DeviceIPAddress=tostring(DeviceIp);
cluster("azwan").database("WarpPROD").MPLSRealTimeIpfix
| where TimeStamp >= starttime and TimeStamp <= endtime
| where SourceIPv4Address startswith SrcIps or SourceIPv6Address startswith SrcIps or SourceIPv4Address in (pack_array(split(SrcIps, ","))[0]) or SourceIPv6Address in (pack_array(split(SrcIps, ","))[0])
| where DestinationIPv4Address startswith DstIps or DestinationIPv6Address startswith DstIps or DestinationIPv4Address in (pack_array(split(DstIps, ","))[0]) or DestinationIPv6Address in (pack_array(split(DstIps, ","))[0])
| join kind=leftouter m on $left.IpAddress == $right. DeviceIPAddress
| extend QueueName=iff(IPClassOfService == 32, "Scavenger", "Best-Effort")
| extend Pair = strcat(DeviceName, "-->Queue: ", QueueName)
| project TimeStamp, DeviceName, SourceIPv4Address, DestinationIPv4Address,SourceIPv6Address,DestinationIPv6Address,IPClassOfService,Pair
| order by TimeStamp desc | order by DeviceName
| summarize Count=count() by Pair, bin(TimeStamp, 1m)
| render timechart

```

### IPFIX - Backbone | DstIpPrefix ---->SrcIpPrefix

```kql
let starttime = _startTime;
let endtime = _endTime;
let SrcIp=iff(isnotempty(SrcIpPrefix), SrcIpPrefix, "a.b.c");
let DstIp=iff(isnotempty(DstIpPrefix), DstIpPrefix, "x.y.z");
let SrcIps=iff(SrcIp == "a.b.c" and DstIp != "x.y.z", "", SrcIp);
let DstIps=iff(SrcIp != "a.b.c" and DstIp == "x.y.z", "", DstIp);
let m = cluster("aznwalertingbackup").database("aznwmds").DeviceStatic 
| where CloudType == "Public"
| where DeploymentType in ("Core", "ExpressRoute") or (DeploymentType =~ "Fabric" and NgsDeviceType =~ "VpnAggregator")
| where Vender in ("Juniper", "Cisco", "Arista")
| project DeviceName, IPs = pack_array(StaticIP, ManagementIP)
| mv-expand DeviceIp = IPs
| where DeviceIp != "0.0.0.0"
| summarize by DeviceName, DeviceIPAddress=tostring(DeviceIp);
cluster("azwan").database("WarpPROD").MPLSRealTimeIpfix
| where TimeStamp >= starttime and TimeStamp <= endtime
| where SourceIPv4Address startswith DstIps or SourceIPv6Address startswith DstIps or SourceIPv4Address in (pack_array(split(DstIps, ","))[0]) or SourceIPv6Address in (pack_array(split(DstIps, ","))[0])
| where DestinationIPv4Address startswith SrcIps or DestinationIPv6Address startswith SrcIps or DestinationIPv4Address in (pack_array(split(SrcIps, ","))[0]) or DestinationIPv6Address in (pack_array(split(SrcIps, ","))[0])
| join kind=leftouter m on $left.IpAddress == $right. DeviceIPAddress
| extend QueueName=iff(IPClassOfService == 32, "Scavenger", "Best-Effort")
| extend Pair = strcat(DeviceName, "-->Queue: ", QueueName)
| project TimeStamp, DeviceName, SourceIPv4Address, DestinationIPv4Address,SourceIPv6Address,DestinationIPv6Address,IPClassOfService,Pair
| order by TimeStamp desc | order by DeviceName
| summarize Count=count() by Pair, bin(TimeStamp, 1m)
| render timechart

```

### sFlow - Backbone | SrcIpPrefix ---->DstIpPrefix

```kql
let starttime = _startTime;
let endtime = _endTime;
let SrcIp=iff(isnotempty(SrcIpPrefix), SrcIpPrefix, "a.b.c");
let DstIp=iff(isnotempty(DstIpPrefix), DstIpPrefix, "x.y.z");
let SrcIps=iff(SrcIp == "a.b.c" and DstIp != "x.y.z", "", SrcIp);
let DstIps=iff(SrcIp != "a.b.c" and DstIp == "x.y.z", "", DstIp);
let m = cluster("aznwalertingbackup").database("aznwmds").DeviceStatic 
| where CloudType == "Public"
| where DeploymentType in ("Core", "ExpressRoute") or (DeploymentType =~ "Fabric" and NgsDeviceType =~ "VpnAggregator")
| where Vender in ("Juniper", "Cisco", "Arista")
| project DeviceName, IPs = pack_array(StaticIP, ManagementIP)
| mv-expand DeviceIp = IPs
| where DeviceIp != "0.0.0.0"
| summarize by DeviceName, DeviceIPAddress=tostring(DeviceIp);
cluster("Netcapplan").database("NetCapPlan").RealTimeSFlow
| where TimeStamp >= starttime and TimeStamp <= endtime
| where SrcIpAddress startswith SrcIps or SrcIpAddress in (pack_array(split(SrcIps, ","))[0])
| where DstIpAddress startswith DstIps or DstIpAddress in (pack_array(split(DstIps, ","))[0])
| join kind=leftouter m on $left.IpAddress == $right.DeviceIPAddress
| extend QueueName=iff(IpClassOfService == 32, "Scavenger", "Best-Effort")
| where DeviceName !contains "ter"
| extend Pair = strcat(DeviceName, "-->Queue: ", QueueName)
| project TimeStamp, DeviceName,Pair
| order by TimeStamp desc | order by DeviceName
| summarize Count=count() by Pair, bin(TimeStamp, 1m)
//| summarize hint.strategy = shuffle Mbps = round((sum(FrameLength*8e-6*SamplingRate)/60), 2) by bin(TimeStamp, 1m), DeviceName
| render timechart

```

### sFlow - Backbone | DstIpPrefix ---->SrcIpPrefix

```kql
let starttime = _startTime;
let endtime = _endTime;
let SrcIp=iff(isnotempty(SrcIpPrefix), SrcIpPrefix, "a.b.c");
let DstIp=iff(isnotempty(DstIpPrefix), DstIpPrefix, "x.y.z");
let SrcIps=iff(SrcIp == "a.b.c" and DstIp != "x.y.z", "", SrcIp);
let DstIps=iff(SrcIp != "a.b.c" and DstIp == "x.y.z", "", DstIp);
let m = cluster("aznwalertingbackup").database("aznwmds").DeviceStatic 
| where CloudType == "Public"
| where DeploymentType in ("Core", "ExpressRoute") or (DeploymentType =~ "Fabric" and NgsDeviceType =~ "VpnAggregator")
| where Vender in ("Juniper", "Cisco", "Arista")
| project DeviceName, IPs = pack_array(StaticIP, ManagementIP)
| mv-expand DeviceIp = IPs
| where DeviceIp != "0.0.0.0"
| summarize by DeviceName, DeviceIPAddress=tostring(DeviceIp);
cluster("Netcapplan").database("NetCapPlan").RealTimeSFlow
| where TimeStamp >= starttime and TimeStamp <= endtime
| where SrcIpAddress startswith DstIps or SrcIpAddress in (pack_array(split(DstIps, ","))[0])
| where DstIpAddress startswith SrcIps or DstIpAddress in (pack_array(split(SrcIps, ","))[0])
| join kind=leftouter m on $left.IpAddress == $right.DeviceIPAddress
| where DeviceName !contains "ter"
| extend QueueName=iff(IpClassOfService == 32, "Scavenger", "Best-Effort")
| extend Pair = strcat(DeviceName, "-->Queue: ", QueueName)
| project TimeStamp, DeviceName,Pair
| order by TimeStamp desc | order by DeviceName
| summarize Count=count() by Pair, bin(TimeStamp, 1m)
//| summarize hint.strategy = shuffle Mbps = round((sum(FrameLength*8e-6*SamplingRate)/60), 2) by bin(TimeStamp, 1m), DeviceName
| render timechart
```

### PV

```kql
let pv=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('kusto').adxpageview| where page contains "b01/netflow";
let pvcount=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('microsoft').adxpageview | where page contains "b01/netflow" | summarize count();
union pv, pvcount
```

### IPFIX - IER Only | SrcIpPrefix ----> DstIpPrefix 

```kql
let starttime = _startTime;
let endtime = _endTime;
let SrcIp=iff(isnotempty(SrcIpPrefix), SrcIpPrefix, "a.b.c");
let DstIp=iff(isnotempty(DstIpPrefix), DstIpPrefix, "x.y.z");
let SrcIps=iff(SrcIp == "a.b.c" and DstIp != "x.y.z", "", SrcIp);
let DstIps=iff(SrcIp != "a.b.c" and DstIp == "x.y.z", "", DstIp);
cluster('netcapplan').database('NetCapPlan').RealTimeIpfixWithMetadata
| where TimeStamp >= starttime and TimeStamp <= endtime
| where RouterName startswith "ier" or RouterName contains "ipr"
| where SrcIpAddress startswith SrcIps or SrcIpAddress in (pack_array(split(SrcIps, ","))[0])
| where DstIpAddress startswith DstIps or DstIpAddress in (pack_array(split(DstIps, ","))[0])
| extend Device=tostring(strcat(RouterName, "---->InterfaceName: ", IngressIfName))
| project TimeStamp , RouterName, IngressIfName, EgressIfName, SrcIpAddress, DstIpAddress, DstTransportPort, SrcAs, DstAs, NextHop,Device
| order by TimeStamp desc | order by RouterName
| summarize count() by Device, bin(TimeStamp, 1m)
| render timechart

```

### IPFIX - IER Only | DstIpPrefix ----> SrcIpPrefix  

```kql
let starttime = _startTime;
let endtime = _endTime;
let SrcIp=iff(isnotempty(SrcIpPrefix), SrcIpPrefix, "a.b.c");
let DstIp=iff(isnotempty(DstIpPrefix), DstIpPrefix, "x.y.z");
let SrcIps=iff(SrcIp == "a.b.c" and DstIp != "x.y.z", "", SrcIp);
let DstIps=iff(SrcIp != "a.b.c" and DstIp == "x.y.z", "", DstIp);
cluster('netcapplan').database('NetCapPlan').RealTimeIpfixWithMetadata
| where TimeStamp >= starttime and TimeStamp <= endtime
| where RouterName startswith "ier" or RouterName contains "ipr"
| where SrcIpAddress startswith DstIps or SrcIpAddress in (pack_array(split(DstIps, ","))[0])
| where DstIpAddress startswith SrcIps or DstIpAddress in (pack_array(split(SrcIps, ","))[0])
| extend Device=tostring(strcat(RouterName, "---->InterfaceName: ", EgressIfName))
| project TimeStamp , RouterName, IngressIfName, EgressIfName, SrcIpAddress, DstIpAddress, DstTransportPort, SrcAs, DstAs, NextHop,Device
| order by TimeStamp desc | order by RouterName
| summarize count() by Device, bin(TimeStamp, 1m)
| render timechart
```

