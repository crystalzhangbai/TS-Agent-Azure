---
description: KQL queries for Azure WAN backbone: WAN link utilization, Moby paths, backbone health, DWDM.
---

# WAN Backbone Kusto Queries

> Source: Azure Networking B01 Dashboard (aka.ms/b01)
> Pages: WAN, WAN Moby, WAN Link

## WAN

### Real time Region-to-Region Latency and Loss Ratio(Always use this one as the real time latency between regions) - This monitoring is TCP Based - Which means this monitoring is over Best Effort queue

```kql
let starttime= _startTime;
let endtime = _endTime;
let srcregion=strcat("InterRegion/", SourceRegion);
let dstregion=strcat("InterRegion/", DestinationRegion);
cluster('Aznwnetmon').database('ThousandEyes').CMTestMetrics
| where TestTime > starttime and TestTime <= endtime
| where TestName == srcregion or TestName == dstregion
| where AgentName contains SourceRegion or AgentName contains DestinationRegion
| extend AgentRegion=tostring(split(AgentName, "-")[2])
| where AgentRegion == SourceRegion or AgentRegion == DestinationRegion
| extend Direction = iff(TestName == srcregion, strcat(DestinationRegion, "-->", SourceRegion), strcat(SourceRegion, "-->", DestinationRegion))
| summarize AvgLatency=round(avg(AvgLatency), 2), LossRatio=round(avg(Loss), 2) by Direction, bin(TestTime, 1m)
| render timechart
```

### Best Effort - Average Latency of all links from Source Region to Destination Region

```kql
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
let SRegion=materialize(RegionMap | where CMTMRegion==SourceRegion | distinct SSRegion);
let DRegion=materialize(RegionMap | where CMTMRegion==DestinationRegion | distinct SSRegion);
let SrcRegion=toscalar(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= _startTime - 1h and PreciseTimeStamp <= _endTime
| where Region in (SRegion)
| extend letters = extract(@"[a-zA-Z]+", 0, tolower(DataCenterName))
| distinct letters
| summarize make_list(letters)
);
let DstRegion=toscalar(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= _startTime - 1h and PreciseTimeStamp <= _endTime
| where Region in (DRegion)
| extend letters = extract(@"[a-zA-Z]+", 0, tolower(DataCenterName))
| distinct letters
| summarize make_list(letters)
);
union cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionOneOceania'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionOneEu'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionOneAPAC'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionIndia'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionOneLatam'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionEU1'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionNAM1'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionOneNam'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionOneApac'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionAPAC2'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionNam1'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionUSStageEast'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionAPAC1'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionApac2')
| where TrafficClass =~ "Default"
| where PathPriority =~ "Primary"
| where (isnotempty(SrcRegion[0]) and Source contains SrcRegion[0]) or (isnotempty(SrcRegion[1]) and Source contains SrcRegion[1]) or (isnotempty(SrcRegion[2]) and Source contains SrcRegion[2]) or (isnotempty(SrcRegion[3]) and Source contains SrcRegion[3]) or (isnotempty(SrcRegion[4]) and Source contains SrcRegion[4]) or (isnotempty(SrcRegion[5]) and Source contains SrcRegion[5]) or (isnotempty(SrcRegion[6]) and Source contains SrcRegion[6]) or (isnotempty(SrcRegion[7]) and Source contains SrcRegion[7]) 
| where (isnotempty(DstRegion[0]) and Destination contains DstRegion[0]) or (isnotempty(DstRegion[1]) and Destination contains DstRegion[1]) or (isnotempty(DstRegion[2]) and Destination contains DstRegion[2]) or (isnotempty(DstRegion[3]) and Destination contains DstRegion[3]) or (isnotempty(DstRegion[4]) and Destination contains DstRegion[4]) or (isnotempty(DstRegion[5]) and Destination contains DstRegion[5]) or (isnotempty(DstRegion[6]) and Destination contains DstRegion[6]) or (isnotempty(DstRegion[7]) and Destination contains DstRegion[7]) 
| summarize minLatency = min(LatencyMs), maxLatency = max(LatencyMs) by bin(TimeStamp, 1m), RouterHops,RouterHopsWithPorts, PathPriority, TrafficClass,TimeStamp, Source, Destination
| distinct TimeStamp,Source, Destination, minLatency, maxLatency,RouterHops,RouterHopsWithPorts, PathPriority, TrafficClass
| extend Path=strcat(Source, "---->", Destination)
//| summarize avg(minLatency), avg(maxLatency) by bin(TimeStamp, 1m),Path
| summarize avg(maxLatency) by bin(TimeStamp, 1m),Path
| render columnchart 
```

### Best Effort Path - raw data from Source Region to Destination Region

```kql
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
let SRegion=materialize(RegionMap | where CMTMRegion==SourceRegion | distinct SSRegion);
let DRegion=materialize(RegionMap | where CMTMRegion==DestinationRegion | distinct SSRegion);
let SrcRegion=toscalar(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= _startTime - 1h and PreciseTimeStamp <= _endTime
| where Region in (SRegion)
| extend letters = extract(@"[a-zA-Z]+", 0, tolower(DataCenterName))
| distinct letters
| summarize make_list(letters)
);
let DstRegion=toscalar(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= _startTime - 1h and PreciseTimeStamp <= _endTime
| where Region in (DRegion)
| extend letters = extract(@"[a-zA-Z]+", 0, tolower(DataCenterName))
| distinct letters
| summarize make_list(letters)
);
union cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionOneOceania'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionOneEu'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionOneAPAC'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionIndia'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionOneLatam'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionEU1'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionNAM1'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionOneNam'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionOneApac'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionAPAC2'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionNam1'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionUSStageEast'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionAPAC1'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionApac2')
| where TrafficClass =~ "Default"
| where PathPriority =~ "Primary"
| where (isnotempty(SrcRegion[0]) and Source contains SrcRegion[0]) or (isnotempty(SrcRegion[1]) and Source contains SrcRegion[1]) or (isnotempty(SrcRegion[2]) and Source contains SrcRegion[2]) or (isnotempty(SrcRegion[3]) and Source contains SrcRegion[3]) or (isnotempty(SrcRegion[4]) and Source contains SrcRegion[4]) or (isnotempty(SrcRegion[5]) and Source contains SrcRegion[5]) or (isnotempty(SrcRegion[6]) and Source contains SrcRegion[6]) or (isnotempty(SrcRegion[7]) and Source contains SrcRegion[7]) 
| where (isnotempty(DstRegion[0]) and Destination contains DstRegion[0]) or (isnotempty(DstRegion[1]) and Destination contains DstRegion[1]) or (isnotempty(DstRegion[2]) and Destination contains DstRegion[2]) or (isnotempty(DstRegion[3]) and Destination contains DstRegion[3]) or (isnotempty(DstRegion[4]) and Destination contains DstRegion[4]) or (isnotempty(DstRegion[5]) and Destination contains DstRegion[5]) or (isnotempty(DstRegion[6]) and Destination contains DstRegion[6]) or (isnotempty(DstRegion[7]) and Destination contains DstRegion[7]) 
| summarize minLatency = min(LatencyMs), maxLatency = max(LatencyMs) by bin(TimeStamp, 1m), RouterHops,RouterHopsWithPorts, PathPriority, TrafficClass,TimeStamp, Source, Destination
| extend Path=strcat(Source, "---->", Destination)
| distinct TimeStamp,Path, MaxPathLatency=maxLatency, RouterHopsWithPorts
| where RouterHopsWithPorts contains RouteHop
```

### Discard and Error Counter over all WAN devices

> **sXInterfaceTable Column Name Reference:**
> - `PreciseTimeStamp` — timestamp (NOT `vscpTimeStamp`)
> - `ifName` — interface name (NOT `InterfaceName`)
> - `ifOutDiscards_Counter` / `ifInDiscards_Counter` — per-interval **delta** counters (NOT `OutDiscards`/`InDiscards`)
> - `_Raw_ifOutDiscards_Counter` / `_Raw_ifInDiscards_Counter` — SNMP **cumulative** counters
> - `ifOutErrors_Counter` / `ifInErrors_Counter` — per-interval delta error counters
> - `ifDescr` — interface description
> - `Interval` — seconds between SNMP polls (useful for calculating per-second rates)

```kql
let starttime= _startTime;
let endtime = _endTime;
cluster('Aznwnetmon').database('aznwmds').sXInterfaceTable 
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where DeviceName contains "icr" or DeviceName contains "ier" or DeviceName contains "ibr" or DeviceName contains "owr" or DeviceName contains "rwa" or DeviceName contains "sw"
| project ReceivedUtc, DeviceName,ifInDiscards_Counter, ifOutDiscards_Counter, ifInErrors_Counter, ifOutErrors_Counter, ifDescr
| extend Device=strcat(DeviceName, ":", ifDescr)
| summarize InDiscard=sum(ifInDiscards_Counter), OutDiscard=sum(ifOutDiscards_Counter), InError=sum(ifInErrors_Counter), OutError=sum(ifOutErrors_Counter) by bin(ReceivedUtc, 5m), Device
| summarize DiscardAndErrorCounter=sum(InDiscard + OutDiscard + InError + OutError) by ReceivedUtc, Device
| where DiscardAndErrorCounter > 100
| render columnchart
```

### Queue Drop Counter for best-effort over MSEE devices - 5 minutes interval

```kql
let starttime= _startTime;
let endtime = _endTime;
union cluster('aznwwanhealthprod04').database('aznwmds').QosQueueStats, cluster('Aznwnetmon').database('aznwmds').QosQueueStats
| where ReceivedUtc > starttime and ReceivedUtc < endtime
| where QoSQueueName contains "best-effort"
| where DroppedPackets != "0"
| where LinkId startswith "exr"
| project ReceivedUtc, LinkId=strcat(QoSQueueName, "---->", LinkId), DroppedPackets
| summarize DroppedPackets=sum(DroppedPackets) by bin(ReceivedUtc, 1m), LinkId
| render columnchart
//union cluster("aznwwanhealthprod04").database('aznwmds').QosQueueStats, cluster('Aznwnetmon').database('aznwmds').QosQueueStats
//| where ReceivedUtc > now(-1h) and ReceivedUtc < now()
//| where ReceivedUtc > starttime and ReceivedUtc < endtime
//| where DroppedPackets > 100
//| where SrcInterfaceDescription !contains "MSEE to service"
//| where InterfaceDescription !contains "MSEE"
//| where QoSQueueName == "best-effort"
//| extend Device=strcat(DeviceName, InterfaceName, SrcDeviceName, SrcInterfaceName)
//| project ReceivedUtc, Device, DroppedPackets
//| render columnchart

```

### ISIS Event

```kql
let starttime= _startTime;
let endtime = _endTime;
cluster('azwan').database('OneWan').IsisSyslog
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| project TIMESTAMP, SrcDC, DstDC, DeviceName, Interface=IfName, EgressDeviceName, EventType,  Message
```

### SWAN Tunnel Down Event

```kql
union cluster('azwan').database('Swan').f_SwanTunnelDownHistoryByDeployment(['_startTime'], ['_endTime'], "ProductionOneApac"),cluster('azwan').database('Swan').f_SwanTunnelDownHistoryByDeployment(['_startTime'], ['_endTime'], "ProductionOneEu"), cluster('azwan').database('Swan').f_SwanTunnelDownHistoryByDeployment(['_startTime'], ['_endTime'], "ProductionOneNam"),cluster('azwan').database('Swan').f_SwanTunnelDownHistoryByDeployment(['_startTime'], ['_endTime'], "ProductionOneOceania"),cluster('azwan').database('Swan').f_SwanTunnelDownHistoryByDeployment(['_startTime'], ['_endTime'], "ProductionOneLatam")
| distinct bin(TimeStamp, 1m), Machine, Source, Destination, Family, TunnelLabel
| summarize count() by TimeStamp//, Source
| render columnchart

```

### ISIS Neighbor Down event

```kql
let starttime= _startTime;
let endtime = _endTime;
cluster('azwan').database('OneWan').IsisSyslog
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where EventType == "ISIS_DN"
| project TIMESTAMP, SrcDC, DstDC, DeviceName, EgressDeviceName, EventType,  Message
| extend Pair=strcat(DeviceName, "---->", EgressDeviceName)
| summarize count=count() by bin(TIMESTAMP, 1m), Pair, EventType
| project TIMESTAMP, Pair, count
| render columnchart 
```

### Cisco NPU Trap Drop Counter

```kql
let starttime= _startTime;
let endtime = _endTime;
cluster('azwan').database('Swan').CiscoNpuTraps
| where Timestamp >= starttime -1h and Timestamp <= endtime
//| where TrapType  !contains "LABEL_LOOKUP"
| extend Device=strcat(DeviceName, "---->", TrapType)
| summarize PacketDrop=sum(PacketsDropped) by bin(Timestamp, 2m), Device
| extend i=strcat(Device, Timestamp)
| order by i asc 
| extend PacketDrops=PacketDrop - prev(PacketDrop)
| where PacketDrops > 100
| project Timestamp, Device, PacketDrops
| where Timestamp > starttime and Timestamp < endtime
| render columnchart
```

### Arista CPU Queue Drop Counter

```kql
let starttime= _startTime;
let endtime = _endTime;
cluster('azwan').database('Swan').AristaCpuQueueCounter 
| where Timestamp >= starttime -1h and Timestamp <= endtime
| extend Device=strcat(DeviceName, "---->", CounterName)
| summarize PacketDrop=sum(DroppedPackets) by bin(Timestamp, 2m), Device
| extend i=strcat(Device, Timestamp)
| order by i asc 
| extend PacketDrops=PacketDrop - prev(PacketDrop)
| where PacketDrops > 100
| project Timestamp, Device, PacketDrops
| summarize Packetdrops=sum(PacketDrops) by Timestamp, Device
| where Timestamp > starttime and Timestamp < endtime
| render columnchart
```

### Queue Drop Counter for Scavenger over all WAN devices

```kql
let starttime= _startTime;
let endtime = _endTime;
union cluster('aznwwanhealthprod04').database('aznwmds').QosQueueStats, cluster('Aznwnetmon').database('aznwmds').QosQueueStats
//| where ReceivedUtc > now(-1h) and ReceivedUtc < now()
| where ReceivedUtc > starttime and ReceivedUtc < endtime
| where QoSQueueName == "scavenger"
| where DroppedPackets != "0"
| summarize DroppedPackets=sum(DroppedPackets) by bin(ReceivedUtc, 1m), LinkId
| render columnchart

//union cluster("aznwwanhealthprod04").database('aznwmds').QosQueueStats, cluster('Aznwnetmon').database('aznwmds').QosQueueStats
//| where ReceivedUtc > now(-1h) and ReceivedUtc < now()
//| where ReceivedUtc > starttime and ReceivedUtc < endtime
//| where DroppedPackets > 100
//| where SrcInterfaceDescription !contains "MSEE to service"
//| where InterfaceDescription !contains "MSEE"
//| where QoSQueueName != "best-effort"
//| extend Device=strcat(DeviceName, InterfaceName, SrcDeviceName, SrcInterfaceName)
//| project ReceivedUtc, Device, DroppedPackets
//| render columnchart

```

### IcM Alert for WAN Team - Severity 0,1,2 Only

```kql
cluster('azwan').database('Swan').f_GetHistoricIncidents(['_startTime'], ['_endTime'],  '')
| where Severity in (0,1,2) 
| where OwningTeamName contains "SWANDRI" or OwningTeamName contains "Optical" or OwningTeamName contains "CNDIR" or OwningTeamName contains "WANNOC-NIA" or OwningTeamName contains "AzureCoreNetworkDRI"
| extend IcMLink=strcat("https://portal.microsofticm.com/imp/v3/incidents/details/", IncidentId, "/home")
| project IncidentId, OccurringDeviceName, CreateDate, Severity, Status, OwningTeamName, Title,ParentIncidentId, ChildCount, IcMLink
```

### Moby Alert

```kql
cluster('azwan').database('Swan').f_GetHistoricIncidents(['_startTime'], ['_endTime'], '')
| where OwningTeamName == "CLOUDNET\\Moby"
| extend IcMLink=strcat("https://portal.microsofticm.com/imp/v3/incidents/details/", IncidentId, "/home")
| project IncidentId, OccurringDeviceName, CreateDate, Severity, Status, OwningTeamName, Title,ParentIncidentId, ChildCount, IcMLink
```

### SLB Probe Loss Ratio - Leverage PATTERN between non-working and working hour

```kql
let starttime= _startTime;
let endtime = _endTime;
let Regionx=todynamic(strcat('["', SourceRegion, '","', DestinationRegion, '"]'));
cluster('Azslb').database('azslbmds').OutboundProbeResultHistoryEvent
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where ProbeResultReason == "Succeeded" or ProbeResultReason == "Timeout"
| where Region in~ (Regionx) or ProbeTargetRegion in~ (Regionx)
| project PreciseTimeStamp, Region, ProbeTargetRegion, ProbeTargetType, ProbeResult, ProbeResultReason
| extend ProbePair=strcat(Region, "---->", ProbeTargetRegion)
| summarize Down=countif(ProbeResult  == "DOWN"), All=count() by bin(PreciseTimeStamp, 1m),ProbePair
| project PreciseTimeStamp,ProbePair, LossPathRatio= round(toreal(Down)/All * 100)
| render timechart
```

### Scavenger - Average Latency of all links from Source Region to Destination Region

```kql
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
let SRegion=materialize(RegionMap | where CMTMRegion==SourceRegion | distinct SSRegion);
let DRegion=materialize(RegionMap | where CMTMRegion==DestinationRegion | distinct SSRegion);
let SrcRegion=toscalar(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= _startTime - 1h and PreciseTimeStamp <= _endTime
| where Region in (SRegion)
| extend letters = extract(@"[a-zA-Z]+", 0, tolower(DataCenterName))
| distinct letters
| summarize make_list(letters)
);
let DstRegion=toscalar(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= _startTime - 1h and PreciseTimeStamp <= _endTime
| where Region in (DRegion)
| extend letters = extract(@"[a-zA-Z]+", 0, tolower(DataCenterName))
| distinct letters
| summarize make_list(letters)
);
union cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionOneOceania'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionOneEu'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionOneAPAC'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionIndia'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionOneLatam'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionEU1'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionNAM1'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionOneNam'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionOneApac'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionAPAC2'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionNam1'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionUSStageEast'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionAPAC1'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionApac2')
| where TrafficClass =~ "Scavenger"
| where PathPriority =~ "Primary"
| where (isnotempty(SrcRegion[0]) and Source contains SrcRegion[0]) or (isnotempty(SrcRegion[1]) and Source contains SrcRegion[1]) or (isnotempty(SrcRegion[2]) and Source contains SrcRegion[2]) or (isnotempty(SrcRegion[3]) and Source contains SrcRegion[3]) or (isnotempty(SrcRegion[4]) and Source contains SrcRegion[4]) or (isnotempty(SrcRegion[5]) and Source contains SrcRegion[5]) or (isnotempty(SrcRegion[6]) and Source contains SrcRegion[6]) or (isnotempty(SrcRegion[7]) and Source contains SrcRegion[7]) 
| where (isnotempty(DstRegion[0]) and Destination contains DstRegion[0]) or (isnotempty(DstRegion[1]) and Destination contains DstRegion[1]) or (isnotempty(DstRegion[2]) and Destination contains DstRegion[2]) or (isnotempty(DstRegion[3]) and Destination contains DstRegion[3]) or (isnotempty(DstRegion[4]) and Destination contains DstRegion[4]) or (isnotempty(DstRegion[5]) and Destination contains DstRegion[5]) or (isnotempty(DstRegion[6]) and Destination contains DstRegion[6]) or (isnotempty(DstRegion[7]) and Destination contains DstRegion[7]) 
| summarize minLatency = min(LatencyMs), maxLatency = max(LatencyMs) by bin(TimeStamp, 1m), RouterHops,RouterHopsWithPorts, PathPriority, TrafficClass,TimeStamp, Source, Destination
| distinct TimeStamp,Source, Destination, minLatency, maxLatency,RouterHops,RouterHopsWithPorts, PathPriority, TrafficClass
| extend Path=strcat(Source, "---->", Destination)
//| summarize avg(minLatency), avg(maxLatency) by bin(TimeStamp, 1m),Path
| summarize avg(maxLatency) by bin(TimeStamp, 1m),Path
| render columnchart 
```

### Scavenger Path - raw data from Source Region to Destination Region

```kql
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
let SRegion=materialize(RegionMap | where CMTMRegion==SourceRegion | distinct SSRegion);
let DRegion=materialize(RegionMap | where CMTMRegion==DestinationRegion | distinct SSRegion);
let SrcRegion=toscalar(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= _startTime - 1h and PreciseTimeStamp <= _endTime
| where Region in (SRegion)
| extend letters = extract(@"[a-zA-Z]+", 0, tolower(DataCenterName))
| distinct letters
| summarize make_list(letters)
);
let DstRegion=toscalar(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= _startTime - 1h and PreciseTimeStamp <= _endTime
| where Region in (DRegion)
| extend letters = extract(@"[a-zA-Z]+", 0, tolower(DataCenterName))
| distinct letters
| summarize make_list(letters)
);
union cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionOneOceania'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionOneEu'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionOneAPAC'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionIndia'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionOneLatam'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionEU1'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionNAM1'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionOneNam'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionOneApac'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionAPAC2'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionNam1'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionUSStageEast'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionAPAC1'),cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(['_startTime'], ['_endTime'], 'ProductionApac2')
| where TrafficClass =~ "Scavenger"
| where PathPriority =~ "Primary"
| where (isnotempty(SrcRegion[0]) and Source contains SrcRegion[0]) or (isnotempty(SrcRegion[1]) and Source contains SrcRegion[1]) or (isnotempty(SrcRegion[2]) and Source contains SrcRegion[2]) or (isnotempty(SrcRegion[3]) and Source contains SrcRegion[3]) or (isnotempty(SrcRegion[4]) and Source contains SrcRegion[4]) or (isnotempty(SrcRegion[5]) and Source contains SrcRegion[5]) or (isnotempty(SrcRegion[6]) and Source contains SrcRegion[6]) or (isnotempty(SrcRegion[7]) and Source contains SrcRegion[7]) 
| where (isnotempty(DstRegion[0]) and Destination contains DstRegion[0]) or (isnotempty(DstRegion[1]) and Destination contains DstRegion[1]) or (isnotempty(DstRegion[2]) and Destination contains DstRegion[2]) or (isnotempty(DstRegion[3]) and Destination contains DstRegion[3]) or (isnotempty(DstRegion[4]) and Destination contains DstRegion[4]) or (isnotempty(DstRegion[5]) and Destination contains DstRegion[5]) or (isnotempty(DstRegion[6]) and Destination contains DstRegion[6]) or (isnotempty(DstRegion[7]) and Destination contains DstRegion[7]) 
| summarize minLatency = min(LatencyMs), maxLatency = max(LatencyMs) by bin(TimeStamp, 1m), RouterHops,RouterHopsWithPorts, PathPriority, TrafficClass,TimeStamp, Source, Destination
| extend Path=strcat(Source, "---->", Destination)
| distinct TimeStamp,Path, MaxPathLatency=maxLatency, RouterHopsWithPorts
| where RouterHopsWithPorts contains RouteHop
```

### PV

```kql
let pv=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('kusto').adxpageview| where page contains "b01/wan";
let pvcount=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('microsoft').adxpageview | where page contains "b01/wan" | summarize count();
union pv, pvcount
```

### Moby Availability from other regions' WAN devices to the WAN devices in $SourceRegion

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
let SRegion=materialize(RegionMap | where CMTMRegion==SourceRegion | distinct SSRegion);
let SrcRegionIER=toscalar(cluster("Azphynet").database("azdhmds").DeviceStatic
| where Regions in (SRegion)
| where DeviceName contains "icr" or DeviceName contains "owr"
| take 1
| distinct DeviceName);
cluster('waneng.westus2').database('waneng').f_GetMobyRawData(SrcRegionIER,true,starttime,endtime)
| summarize SrcRegionAvailability=avg(Average) by bin(TimestampUtc, 1m)
| render timechart
```

### Moby Availability for other regions' WAN devices to the WAN devices in $DestinationRegion

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
let DRegion=materialize(RegionMap | where CMTMRegion==DestinationRegion | distinct SSRegion);
let DstRegionIER=toscalar(cluster("Azphynet").database("azdhmds").DeviceStatic
| where Regions in (DRegion)
| where DeviceName contains "icr" or DeviceName contains "owr"
| take 1
| distinct DeviceName);
cluster('waneng.westus2').database('waneng').f_GetMobyRawData(DstRegionIER,true,starttime,endtime)
| summarize DstRegionAvailability=avg(Average) by bin(TimestampUtc, 1m)
| render timechart
```

### Moby Availability from other regions' WAN devices to the WAN devices in $SourceRegion

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
let SRegion=materialize(RegionMap | where CMTMRegion==SourceRegion | distinct SSRegion);
let SrcRegionIER=toscalar(cluster("Azphynet").database("azdhmds").DeviceStatic
| where Regions in (SRegion)
| where DeviceName contains "icr" or DeviceName contains "owr"
| take 1
| distinct DeviceName);
cluster('waneng.westus2').database('waneng').f_GetMobyRawData(SrcRegionIER,true,starttime,endtime)
| where Average !in (0,1)
| summarize count() by bin(TimestampUtc, 5m), DestDevice
| render columnchart 
```

### Moby Availability for other regions' WAN devices to the WAN devices in $DestinationRegion

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
let DRegion=materialize(RegionMap | where CMTMRegion==DestinationRegion | distinct SSRegion);
let DstRegionIER=toscalar(cluster("Azphynet").database("azdhmds").DeviceStatic
| where Regions in (DRegion)
| where DeviceName contains "icr" or DeviceName contains "owr"
| take 1
| distinct DeviceName);
cluster('waneng.westus2').database('waneng').f_GetMobyRawData(DstRegionIER,true,starttime,endtime)
| where Average !in (0,1)
| summarize count() by bin(TimestampUtc, 5m), DestDevice
| render columnchart 
```

### BGP Disconnect event between all MSEEs and Gateways

```kql
let starttime= _startTime;
let endtime = _endTime;
cluster('Eagleeyecentralus.centralus').database('ImpactAnalysis').SysLog_MSEEToGatewayBGPDisconnects
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| summarize count() by bin(PreciseTimeStamp, 5m), Device
| render columnchart 
```

### Forwarding Equivalence Class(FEC) Error

```kql
let devicename = todynamic(_DeviceName);
let starttime = _startTime;
let endtime = _endTime;
cluster('azphynet.kusto.windows.net').database('azdhmds').SyslogData
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where Severity == "Error"
| where EventName contains "FEC"
| project PreciseTimeStamp, Device, EventName,Message, Severity
```

### Moby Availability = 0 Lossy Count From other region to $SrcRegion

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
let SRegion=materialize(RegionMap | where CMTMRegion==SourceRegion | distinct SSRegion);
let SrcRegionIER=toscalar(cluster("Azphynet").database("azdhmds").DeviceStatic
| where Regions in (SRegion)
| where DeviceName contains "icr" or DeviceName contains "owr"
| take 1
| distinct DeviceName);
cluster('waneng.westus2').database('waneng').f_GetMobyRawData(SrcRegionIER,true,starttime,endtime)
| where Average == 0
| summarize count() by bin(TimestampUtc, 1m)
| render timechart 
```

### Moby Availability = 0 Lossy Count From other region to $DestinationRegion

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
let DRegion=materialize(RegionMap | where CMTMRegion==DestinationRegion | distinct SSRegion);
let DstRegionIER=toscalar(cluster("Azphynet").database("azdhmds").DeviceStatic
| where Regions in (DRegion)
| where DeviceName contains "icr" or DeviceName contains "owr"
| take 1
| distinct DeviceName);
cluster('waneng.westus2').database('waneng').f_GetMobyRawData(DstRegionIER,true,starttime,endtime)
| where Average == 0
| summarize count() by bin(TimestampUtc, 1m)
| render timechart 
```

### Moby Availability = 0 Lossy count from other regions' WAN devices to the WAN devices in $SourceRegion

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
let SRegion=materialize(RegionMap | where CMTMRegion==SourceRegion | distinct SSRegion);
let SrcRegionIER=toscalar(cluster("Azphynet").database("azdhmds").DeviceStatic
| where Regions in (SRegion)
| where DeviceName contains "icr" or DeviceName contains "owr"
| take 1
| distinct DeviceName);
cluster('waneng.westus2').database('waneng').f_GetMobyRawData(SrcRegionIER,true,starttime,endtime)
| where Average == 0
| summarize count() by bin(TimestampUtc, 5m), DestDevice
| render timechart  
```

### Moby Availability = 0 Lossy count from other regions' WAN devices to the WAN devices in $DestinationRegion

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
let DRegion=materialize(RegionMap | where CMTMRegion==DestinationRegion | distinct SSRegion);
let DstRegionIER=toscalar(cluster("Azphynet").database("azdhmds").DeviceStatic
| where Regions in (DRegion)
| where DeviceName contains "icr" or DeviceName contains "owr"
| take 1
| distinct DeviceName);
cluster('waneng.westus2').database('waneng').f_GetMobyRawData(DstRegionIER,true,starttime,endtime)
| where Average == 0
| summarize count() by bin(TimestampUtc, 5m), DestDevice
| render columnchart 
```

### WAN Device Configuration Change 

```kql
let starttime= _startTime;
let endtime = _endTime;
let devicename = cluster("Azphynet").database("azdhmds").DeviceStatic
| where CloudType =~ 'Public' 
| where AzureDeviceType in ("SwanRouter","OneWANRouter","RegionalWANAggregator","InternetBackboneRouter", "InternetEdgeRouter", "InternetPeeringRouter", "InternetPeeringRouter", "InternetCoreRouter")
| distinct DeviceName;
let includePattern = @'(?i)^commit|^write';
let excludePattern = @'(?i)(commit\scheck)|(commit-configuration)';
cluster("phynetval").database("aznwmds").AzureAaaMasterSessions
| where TIMESTAMP between (starttime - 20m .. endtime + 20m)
| where deviceName in~ (devicename)
| where command matches regex includePattern and not (command matches regex excludePattern)
| project PreciseTimeStamp, deviceRegion, deviceName, user, command
| summarize count() by  bin(PreciseTimeStamp, 5m), deviceName
| render columnchart 
```

### IET Policy fires on Internet Edge(Microsoft Routing Preference)

```kql
let starttime= _startTime;
let endtime = _endTime;
cluster("Aznwwanhealthui01.westus").database("aznwmds").IteRoutePolicyMetrics
| where Timestamp >= starttime - 30m and Timestamp <= endtime + 30m
| distinct IngestionAt, SrcDeviceName, SrcInterfaceName, Direction,PolicyName,Prefixes, PolicyStatement, PolicyAction, NumPrefixes, PolicyActivated
| summarize count() by bin(IngestionAt, 1m), SrcDeviceName
| render columnchart  
```

### IET Policy fires on Internet Edge(Microsoft Routing Preference)

```kql
let starttime= _startTime;
let endtime = _endTime;
cluster("Aznwwanhealthui01.westus").database("aznwmds").IteRoutePolicyMetrics
| where Timestamp >= starttime - 30m and Timestamp <= endtime + 30m
| distinct IngestionAt, SrcDeviceName, SrcInterfaceName, Direction,PolicyName,Prefixes, PolicyStatement, PolicyAction, NumPrefixes, PolicyActivated
```

### WAN Device Configuration Change 

```kql
let starttime= _startTime;
let endtime = _endTime;
let devicename = cluster("Azphynet").database("azdhmds").DeviceStatic
| where CloudType =~ 'Public' 
| where AzureDeviceType in ("SwanRouter","OneWANRouter","RegionalWANAggregator","InternetBackboneRouter", "InternetEdgeRouter", "InternetPeeringRouter", "InternetPeeringRouter", "InternetCoreRouter")
| distinct DeviceName;
let includePattern = @'(?i)^commit|^write';
let excludePattern = @'(?i)(commit\scheck)|(commit-configuration)';
cluster("phynetval").database("aznwmds").AzureAaaMasterSessions
| where TIMESTAMP between (starttime - 20m .. endtime + 20m)
| where deviceName in~ (devicename)
| where command matches regex includePattern and not (command matches regex excludePattern)
| project PreciseTimeStamp, deviceRegion, deviceName, user, command
```

### Queue Drop Counter for best-effort over all WAN devices - 5 minutes interval

```kql
let starttime= _startTime;
let endtime = _endTime;
union cluster('aznwwanhealthprod04').database('aznwmds').QosQueueStats, cluster('Aznwnetmon').database('aznwmds').QosQueueStats
| where ReceivedUtc > starttime and ReceivedUtc < endtime
| where QoSQueueName contains "best-effort"
| where DroppedPackets != "0"
| where LinkId !startswith "exr"
| project ReceivedUtc, LinkId=strcat(QoSQueueName, "---->", LinkId), DroppedPackets
| summarize DroppedPackets=sum(DroppedPackets) by bin(ReceivedUtc, 1m), LinkId
| render columnchart
//union cluster("aznwwanhealthprod04").database('aznwmds').QosQueueStats, cluster('Aznwnetmon').database('aznwmds').QosQueueStats
//| where ReceivedUtc > now(-1h) and ReceivedUtc < now()
//| where ReceivedUtc > starttime and ReceivedUtc < endtime
//| where DroppedPackets > 100
//| where SrcInterfaceDescription !contains "MSEE to service"
//| where InterfaceDescription !contains "MSEE"
//| where QoSQueueName == "best-effort"
//| extend Device=strcat(DeviceName, InterfaceName, SrcDeviceName, SrcInterfaceName)
//| project ReceivedUtc, Device, DroppedPackets
//| render columnchart

```

### SWAN Tunnel Down Event

```kql
union cluster('azwan').database('Swan').f_SwanTunnelDownHistoryByDeployment(['_startTime'], ['_endTime'], "ProductionOneApac"),cluster('azwan').database('Swan').f_SwanTunnelDownHistoryByDeployment(['_startTime'], ['_endTime'], "ProductionOneEu"), cluster('azwan').database('Swan').f_SwanTunnelDownHistoryByDeployment(['_startTime'], ['_endTime'], "ProductionOneNam"),cluster('azwan').database('Swan').f_SwanTunnelDownHistoryByDeployment(['_startTime'], ['_endTime'], "ProductionOneOceania"),cluster('azwan').database('Swan').f_SwanTunnelDownHistoryByDeployment(['_startTime'], ['_endTime'], "ProductionOneLatam")
| distinct bin(TimeStamp, 1m), Machine, Source, Destination, Family, TunnelLabel
```

## WAN Moby

### Region Availability in %

```kql
let starttime = _startTime;
let endtime = _endTime;
let dccode=replace(@"\]", ")", replace(@"\[", "(", tostring(RegionDCCode)));
let moby_query = strcat('metricNamespace("Canary").metric("PacketSuccess").dimensions("Region", "Device", "DestRegion", "DestDevice", "DestIP", "WanType").samplingTypes("Average") | where DestRegion in~ ', dccode);
evaluate geneva_metrics_request('MobyProdMetrics',moby_query, starttime, endtime)
| where Average != 0
| summarize Average=avg(Average) * 100 by bin(TimestampUtc, 1m), WanType




```

### MSEE Device Loss In %

```kql
let starttime = _startTime;
let endtime = _endTime;
let dccode=replace(@"\]", ")", replace(@"\[", "(", tostring(RegionDCCode)));
let moby_query = strcat('metricNamespace("Canary").metric("PacketSuccess").dimensions("Region", "Device", "DestRegion", "DestDevice", "DestIP", "WanType").samplingTypes("Average") | where DestRegion in ', dccode);
evaluate geneva_metrics_request('MobyProdMetrics',moby_query, starttime, endtime)
| where WanType =~ "MSEE"
| where Average != 0
| summarize Average=(1-avg(Average))*100 by bin(TimestampUtc, 1m), DestDevice
| render timechart 




```

### Device Loss % In Core Network

```kql
let starttime = _startTime;
let endtime = _endTime;
let dccode=replace(@"\]", ")", replace(@"\[", "(", tostring(RegionDCCode)));
let moby_query = strcat('metricNamespace("Canary").metric("PacketSuccess").dimensions("Region", "Device", "DestRegion", "DestDevice", "DestIP", "WanType").samplingTypes("Average") | where DestRegion in ', dccode);
evaluate geneva_metrics_request('MobyProdMetrics',moby_query, starttime, endtime)
| where WanType =~ "core"
| where Average != 0
| summarize Average=(1-avg(Average))*100 by bin(TimestampUtc, 1m), Device=DestDevice
| render timechart 




```

### Device Loss % In SWAN

```kql
let starttime = _startTime;
let endtime = _endTime;
let dccode=replace(@"\]", ")", replace(@"\[", "(", tostring(RegionDCCode)));
let moby_query = strcat('metricNamespace("Canary").metric("PacketSuccess").dimensions("Region", "Device", "DestRegion", "DestDevice", "DestIP", "WanType").samplingTypes("Average") | where DestRegion in ', dccode);
evaluate geneva_metrics_request('MobyProdMetrics',moby_query, starttime, endtime)
| where WanType =~ "swan"
| where Average != 0
| summarize Average=(1-avg(Average))*100 by bin(TimestampUtc, 1m), DestDevice
| render timechart 




```

### Loss = 0 Count For Device

```kql
let starttime = _startTime;
let endtime = _endTime;
let dccode=replace(@"\]", ")", replace(@"\[", "(", tostring(RegionDCCode)));
let moby_query = strcat('metricNamespace("Canary").metric("PacketSuccess").dimensions("Region", "Device", "DestRegion", "DestDevice", "DestIP", "WanType").samplingTypes("Average") | where DestRegion in~ ', dccode);
evaluate geneva_metrics_request('MobyProdMetrics',moby_query, starttime, endtime)
| where Average == 0
| summarize count=count() by bin(TimestampUtc, 1m),Device=DestDevice




```

## WAN Link

### Interface bandwidth allocation By TE Based on $(StartDeviceName:StartInterfaceName)

```kql
let st= _startTime;
let et = _endTime;
let sdn=StartDeviceName;
let sin=StartInterfaceName;
let endDevice=toscalar(cluster('Azwan').database('Swan').Swan_Topology_Links()
| where StartNode in~ (sdn)
| where StartInterface == sin
| distinct EndNode
);
let DeploymentType=toscalar(cluster('Azwan').database('Swan').SwanDeviceMetadata_Latest 
| where DeviceName in~ (sdn)
| distinct DeploymentName);
let RoutePath=toscalar(cluster('Azwan').database('Swan').Swan_Topology_Links_ByDeployment_History(st, et, DeploymentType)
| where StartNode in~ (sdn) and StartInterface == sin
| project LastUpdatedOpState, LastUpdatedBw, StartNode, StartInterface, EndNode, EndInterface, Machine,OperationalState, ConfigBwMbps, OperationalBwMbps, LossBandwidth=ConfigBwMbps - OperationalBwMbps
| extend RoutePath=strcat(StartNode, ":", StartInterface, "-", EndNode, ":", EndInterface)
| distinct RoutePath);
cluster('Azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(st,et,DeploymentType) 
//| where RouterHopsWithPorts matches regex routerport 
| where RouterHopsWithPorts contains RoutePath 
| where PathPriority == "Primary" 
| summarize AllocatedGbps = (sum(AllocatedMbps)/1e3),RequestedGbps = (sum(RequestedMbps)/1e3),BwOnPathGbps=round(sum(BwOnPath)/1000) by bin(TimeStamp,30s) //, TrafficClass, Source, Destination, 
| project TimeStamp, RequestedGbps,AllocatedGbps,BwOnPathGbps
| render columnchart 

```

### Link Operational State by BgpLs

```kql
let st= _startTime;
let et = _endTime;
let sdn=StartDeviceName;
let sin=StartInterfaceName;
let endDevice=toscalar(cluster('Azwan').database('Swan').Swan_Topology_Links()
| where StartNode in~ (sdn)
| where StartInterface == sin
| distinct EndNode
);
let DeploymentType=toscalar(cluster('Azwan').database('Swan').SwanDeviceMetadata_Latest 
| where DeviceName in~ (sdn)
| distinct DeploymentName);
cluster('Azwan').database('Swan').Swan_Topology_Links_ByDeployment_History(st, et, DeploymentType)
| where StartNode in~ (sdn) and StartInterface == sin
//| project LastUpdatedOpState, LastUpdatedBw, StartNode, StartInterface, EndNode, EndInterface, Machine,OperationalState, ConfigBwMbps, OperationalBwMbps, LossBandwidth=ConfigBwMbps - OperationalBwMbps
| project todatetime(LastUpdatedOpState), OperationalState
| project todatetime(LastUpdatedOpState), OperationalState
| summarize count() by OperationalState, bin(LastUpdatedOpState, 1m)
| project LastUpdatedOpState, OperationalState, Count=count_
| render timechart   




```

### Swan Logs - Filtered - TESwanTopologyFetcher

```kql
let st= _startTime;
let et = _endTime;
let sdn=StartDeviceName;
let swanmachine = cluster('Azwan').database('Swan').SwanLogsProd
| where TimeStamp >= st and TimeStamp <= et
| where Component == "SwanController"
| where Title == "FibPusher"
| where Message contains sdn
| where Message contains "Pushing FIB to"
| distinct Machine;
cluster('Azwan').database('Swan').SwanLogsProd
| where TimeStamp >= st and TimeStamp <= et
| where Machine  in (swanmachine)
| where Component == "TESwanTopologyFetcher"
//| where Message contains "Fetching/Validating SwanTopology caught exception" or  Message contains "successfully fetched swantopology"
//| project TimeStamp, Level, Title, Machine, Message
| project TimeStamp,  Message, Level




```

### Link Bandwidth State by BgpLs

```kql
let st= _startTime;
let et = _endTime;
let sdn=StartDeviceName;
let sin=StartInterfaceName;
let endDevice=toscalar(cluster('Azwan').database('Swan').Swan_Topology_Links()
| where StartNode == sdn
| where StartInterface in~ (sdn)
| distinct EndNode
);
let DeploymentType=toscalar(cluster('Azwan').database('Swan').SwanDeviceMetadata_Latest 
| where DeviceName in~ (sdn)
| distinct DeploymentName);
cluster('Azwan').database('Swan').Swan_Topology_Links_ByDeployment_History(st, et, DeploymentType)
| where StartNode in~ (sdn) and StartInterface == sin
| project bin(todatetime(LastUpdatedBw),1m), ConfigBwMbps, OperationalBwMbps, LossBandwidth=ConfigBwMbps - OperationalBwMbps
| render timechart  

```

### Link State by Topology Service

```kql
let st= _startTime;
let et = _endTime;
let sdn=StartDeviceName;
let sin=StartInterfaceName;
let endDevice=toscalar(cluster('Azwan').database('Swan').Swan_Topology_Links()
| where StartNode in~ (sdn)
| where StartInterface == sin
| distinct EndNode
);
let DeploymentType=toscalar(cluster('Azwan').database('Swan').SwanDeviceMetadata_Latest 
| where DeviceName in~ (sdn)
| distinct DeploymentName);
cluster('Azwan').database('Swan').Swan_Topology_Links_ByDeployment_History(st, et, DeploymentType)
| where StartNode in~ (sdn) and StartInterface == sin
| project LastUpdatedOpState, LastUpdatedBw, StartNode, StartInterface, EndNode, EndInterface, Machine,OperationalState, ConfigBwMbps, OperationalBwMbps, LossBandwidth=ConfigBwMbps - OperationalBwMbps



```

### Swan Logs - Filtered - FibPusher Event

```kql
let st= _startTime;
let et = _endTime;
let sdn=StartDeviceName;
cluster('Azwan').database('Swan').SwanLogsProd
| where TimeStamp >= st and TimeStamp <= et
| where Component == "SwanController"
| where Title == "FibPusher"
| where Message contains sdn
| where Message contains "Pushing FIB to" or Message contains "exception"
| project TimeStamp, Message, Level


```

### Device Metadata

```kql
let st= _startTime;
let et = _endTime;
let startunixtime = tolong(st-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(et-datetime(1970-01-01)) / 10000;
let stn=StartDeviceName;
let devicename = tolower(_DeviceName);
cluster("azwan").database("Swan").GetSwanDeviceMetadata() 
| where DeviceName  in~ (stn)
| extend Coretool=strcat("https://coretools.azurefd.net/#/device/home?target=",DeviceName,"&time=",startunixtime, "%252C", endunixtime, "&useUtc=true&renderType=chart&keywords=&searchContext=devices&summary=Device&linkDirection=forwardandreverse&interfaceType=portchannel&dataType=&domain=All&cloudType=Public")
| evaluate narrow()
| project Key=Column, Value
```

### Device Link Metadata

```kql
//forpageview
let pv=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('kusto').adxpageview| where page contains "b01/wanlink";
//forpageview
let st= _startTime;
let et = _endTime;
let stn = StartDeviceName;
let DeploymentType=toscalar(cluster('Azwan').database('Swan').SwanDeviceMetadata_Latest 
| where DeviceName ==  stn
| distinct DeploymentName);
cluster('Azwan').database('Swan').Swan_Topology_Links_ByDeployment_History(st, et, DeploymentType) 
//| distinct StartNode=tolower(StartNode), StartInterface
| where StartNode in~ (stn)
| distinct StartNode, StartInterface, EndNode, EndInterface
```

### Expected VS Actual Link Utilization Observed By TE

```kql
let st= _startTime;
let et = _endTime;
let stn=StartDeviceName;
let sif=StartInterfaceName;
let routerport=strcat(stn, ":", sif);
let perc = 95;
let DeploymentType=toscalar(cluster('Azwan').database('Swan').SwanDeviceMetadata_Latest 
| where DeviceName in (stn)
| distinct DeploymentName);
let linkk=materialize(cluster('Azwan').database('Swan').Swan_Topology_Links_ByDeployment_History(st, et, DeploymentType) 
| where StartNode in~ (stn) and StartInterface in~ (sif)
| distinct linkkey=tostring(strcat(StartNode, ":", StartInterface, "-", EndNode, ":", EndInterface)));
let Arista=cluster('Azwan').database('Swan').f_SwanProd_TEScheduler_ExpectedVsActualLinkUtilization(st,et,DeploymentType)//,cluster('Azwan').database('Swan').f_SwanProd_TEScheduler_ExpectedVsActualLinkUtilization_OneWAN(st,et,DeploymentType)
| where LinkKey in~ (linkk)
| project TimeStamp, RequestedUtilization, AllocatedUtilization, ActualUtilization
| render timechart;
let Cisco=cluster('Azwan').database('Swan').f_SwanProd_TEScheduler_ActualLinkUtilization_OneWAN(_startTime, _endTime)
| where DeviceName =~ stn and ifDescr =~ sif
| summarize LinkCapacity = toint(percentile(IfSpeed, perc)), ActualUtilization = toint(percentile(ActualUtilization, perc)),ActualOutMbps = toint(percentile(ActualOutMbps, perc)) by bin(TimeStamp, 5m), DeviceName, ifDescr, RemoteDeviceName
| extend LinkKey = tolower(strcat(DeviceName, ':', ifDescr, '-', RemoteDeviceName, ':', ifDescr))
| project TimeStamp, LinkKey, LinkCapacity, ActualOutMbps, ActualUtilization
| join kind=inner (cluster('Azwan').database('Swan').f_SwanProd_TEScheduler_ExpectedLinkUtilization_OneWAN(_startTime, _endTime, DeploymentType)) on TimeStamp, LinkKey
| project TimeStamp, Machine, DeploymentType="ProductionOneNam", LinkKey, Region, RemoteRegion, LinkCapacity, RsvpBandwidthMbps, SwanBandwidthMbps,
RsvpReservedMbps, RsvpUsedMbps, SwanRequestedMbps, SwanAllocatedMbps, ActualOutMbps, ExpectedUtilization, ActualUtilization
| extend ErrorInMbps =  (ActualUtilization - ExpectedUtilization) * (LinkCapacity / 100)
| project TimeStamp, SwanAllocatedMbps, SwanRequestedMbps, ActualOutMbps
| render timechart;
union Arista, Cisco

```

### Swan Logs - Unfiltered

```kql
let st= _startTime;
let et = _endTime;
let sdn=StartDeviceName;
let swanmachine = cluster('Azwan').database('Swan').SwanLogsProd
| where TimeStamp >= st and TimeStamp <= et
| where Component == "SwanController"
| where Title == "FibPusher"
| where Message contains sdn
| where Message contains "Pushing FIB to"
| distinct Machine;
cluster('Azwan').database('Swan').SwanLogsProd
| where TimeStamp >= st and TimeStamp <= et
| where Machine  in (swanmachine)
| where Component == "SwanController" or Component  == "RestFibWriter"or Component == "TESwanTopologyFetcher"
| where Title == "FibPusher" or Title == "FibProcessor" or Title == "RestFibWriter" or Title == "TESwanTopologyFetcher"
| where Message contains sdn or Message contains "Successfully fetched SwanTopology"
| project TimeStamp,Title,  Message,Level, Machine


```

### Device Syslog - Filtered - FIB Program State

```kql
let st= _startTime;
let et = _endTime;
let sdn=StartDeviceName;
let DP = format_datetime(_startTime, 'yyyy-MM-dd');
cluster('azphynet').database('azdhmds').SyslogData
| where TIMESTAMP between (datetime(2024-07-15 13:20:00)..datetime(2024-07-15 14:00:00))
| where tolower(Device) has "ibr02.cpt21"
| where Message contains "ProgramFIB Done" and Message contains "MB2"
 | extend v = extract(" INFO\\[(.*?)\\] ", 1, Message)
| extend FIBProgramStartTime = iff(v != "", todatetime(strcat(DP, split(v, " ")[2])), PreciseTimeStamp)
| project FIBProgramStartTime, FIBProgramFinishTime=PreciseTimeStamp, Message


```

### Swan Critical Log

```kql
let st= _startTime;
let et = _endTime;
let sdn=StartDeviceName;
let swanmachine = cluster('Azwan').database('Swan').SwanLogsProd
| where TimeStamp >= st and TimeStamp <= et
| where Component == "SwanController"
| where Title == "FibPusher"
| where Message contains sdn
| where Message contains "Pushing FIB to"
| distinct Machine;
let DeploymentType=toscalar(cluster('Azwan').database('Swan').SwanDeviceMetadata_Latest 
| where DeviceName in (sdn)
| distinct DeploymentName);
cluster('Azwan').database('Swan').f_GetSwanCriticalLogs(st,et, DeploymentType, logLevel=".*")
| where Machine in (swanmachine)
| where Level != "i" and Level !="d" and Level != "w"
| project TimeStamp, Machine,  Message, Level




```

### Interface Utilization Per Port Channel Interface - In - [ SNMP ] 

```kql
let st= _startTime;
let et = _endTime;
let stn=StartDeviceName;
let sif=StartInterfaceName;
let links = cluster("aznwwanhealthprod03").database('aznwmds').InterfaceLinksMetadata 
| where SrcDeviceName =~ stn 
| where SrcPortChannel =~ sif 
| distinct SrcInterfaceName; 
cluster("aznwalerting").database('aznwmds').sXInterfaceTable 
| where PreciseTimeStamp between (st..et) 
| where DeviceName =~ stn 
| where ifName in~ (links) 
| project PreciseTimeStamp,ifName,InGbps=round(ifHCInOctets_Counter*8/Interval/1e9,0)
| render timechart
```

### Interface Utilization Per Port Channel Interface - Out - [ SNMP ]

```kql
let st= _startTime;
let et = _endTime;
let stn=StartDeviceName;
let sif=StartInterfaceName;
let links = cluster("aznwwanhealthprod03").database('aznwmds').InterfaceLinksMetadata 
| where SrcDeviceName =~ stn 
| where SrcPortChannel =~ sif 
| distinct SrcInterfaceName; 
cluster("aznwalerting").database('aznwmds').sXInterfaceTable 
| where PreciseTimeStamp between (st..et) 
| where DeviceName =~ stn 
| where ifName in~ (links) 
| project PreciseTimeStamp,ifName, OutGbps=round(ifHCOutOctets_Counter*8/Interval/1e9,0)
| render timechart
```

### PV

```kql
let pv=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('kusto').adxpageview| where page contains "b01/wanlinks";
let pvcount=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('microsoft').adxpageview | where page contains "b01/wanlinks" | summarize count();
union pv, pvcount
```

### Top Flow over the Interface

```kql
let st= _startTime;
let et = _endTime;
let sdn=StartDeviceName;
let sin=StartInterfaceName;
cluster('azwan').database('swan').f_TopEgressFlowsFromIpfix(st, et, sdn, sin)

```

### Bandwidth Predictor Demand Status

```kql
let st= _startTime;
let et = _endTime;
let stn=StartDeviceName;
let sif=StartInterfaceName;
let account = "SwanBandwidthPredictor";
let namespace= "BandwidthPredictor";
let metricName='IsLeader';
let DeploymentT=toscalar(cluster('Azwan').database('Swan').SwanDeviceMetadata_Latest 
| where DeviceName in~ (stn)
| distinct DeploymentName);
let metric = strcat('metricNamespace("', namespace, '").metric("', metricName, '").dimensions("DeploymentType", "Machine").samplingTypes("Sum")');
let Bwpleader=evaluate geneva_metrics_request(account, metric, st, et)
| where DeploymentType =~ DeploymentT
| where Sum == 1
| take 1
| distinct Machine;
cluster('azwan').database('swan').SwanCsvHistoryProd 
| where TimeStamp between (st..et) 
| where Machine in (Bwpleader)
| where Title =~ 'Demands_LC.csv' 
| extend SourceRouter = extract("SourceRouter=(.*?),", 1, Message, typeof(string)) 
| extend DestinationRegion = extract("DestinationRegion=(.*?),", 1, Message, typeof(string)) 
| where SourceRouter =~ stn
| extend Mbps = extract("Mbps=(.*?)$", 1, Message, typeof(real)) 
| summarize GbpsFromBwp=round(sum(Mbps)/1000) by Timestamp=bin(TimeStamp, 1m),DestinationRegion
| render columnchart
```

### IPFIX observed by SWAN - Currently not all WAN devices have enabled IPPrefix

```kql
let st= _startTime;
let et = _endTime;
let stn=StartDeviceName;
let sif=StartInterfaceName;
cluster('azwan').database('swan').IpfixPrefixLevelBandwidthInfoStreaming 
| where UpdateTimeUtc >= st and UpdateTimeUtc <= et
| where Switch =~ stn
| project UpdateTimeUtc, Switch, IngressIfIndex, SrcPrefix, DstPrefix,Mbps,SrcToDst=strcat(SrcRegion, "---->", DstRegion)
| summarize sum(Mbps) by bin(UpdateTimeUtc, 1m), SrcToDst
| render timechart     
```

