---
description: KQL queries for Azure physical network: T0/T1/T2 device health, interface utilization, optical power, BGP sessions.
---

# Physical Network Kusto Queries

> Source: Azure Networking B01 Dashboard (aka.ms/b01)
> Pages: Physical Network, PhyNet T2-RH Utilization, PhyNet T2-AZNG Utilization, PhyNet Link

## Physical Network

### AZ-DC Mapping

```kql
let starttime = _startTime;
let endtime = _endTime;
let Regionss = Regionn;
cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where TIMESTAMP > starttime - 1h and TIMESTAMP < endtime
| where Region in (Regionss)
| distinct AvailabilityZone, DataCenterName
| summarize DataCenterName=make_list(DataCenterName) by AvailabilityZone
```

### NetScan - Region Level Path Loss Ratio(IPv4 + IPv6)

```kql
let starttime = _startTime;
let endtime = _endTime;
union cluster("azphynet").database("NetPerfKustoDB").PerfAnalyzer_NetScanPodSetPaths,cluster("azphynet").database("NetPerfKustoDB").PerfAnalyzer_NetScanV6PodSetPaths
| where startTime >= starttime and startTime <= endtime
| where region in (Regionn)
| summarize Noloss=countif(status  == "noloss"), All=count() by bin(startTime, 1m)
| project startTime, LossPathRatio= toreal((All - Noloss)) / All * 100
| render timechart 
//cluster('azphynet').database('NetPerfKustoDB').PerfAnalyzer_NetLatencyPodSetPaths 
//| where startTime >= starttime and startTime <= endtime
//| where region in (Regionn)
//| summarize Latency=round(avg(latencyMilliseconds), 4), SuccessRate=round(avg(successRate), 2) by bin(startTime, 1m), region
//| project startTime, Latency, SuccessRate, region
//| render timechart
```

### KHISLB - Loss Ratio to datacenter Level ------>>--->>Issue mitigation is typically delayed by 15–20 minutes due to KHI data source issues

```kql
let starttime = _startTime;
let endtime = _endTime;
let DCs=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where Region in (Regionn)
| distinct tolower(tostring(DataCenterName))
);
cluster('azphynet').database('azdhsd').KhiSlb
| where TIMESTAMP between (starttime .. endtime)
| where Datacenter !contains "BingEdge"
| where DC in (DCs)
| project TIMESTAMP, DC, LossRatio=netscan_loss
| render timechart
```

### PathScan - Loss Ratio to Cluster Level(IPv6)

```kql
let starttime = _startTime;
let endtime = _endTime;
let cluster=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where Region in (Regionn)
| distinct Tenant
);
cluster('azphynet').database('azdhsd').PathScanHealthCheckV6_Cluster
| where TIMESTAMP > starttime and TIMESTAMP < endtime
| where Cluster in (cluster)
| project TIMESTAMP, LossyPathRatio, Cluster
| render timechart
```

### NetScan - Lossy Path Count(IPv4)

```kql
let starttime = _startTime;
let endtime = _endTime;
let Regionss = Regionn;
cluster("azphynet").database("NetPerfKustoDB").PerfAnalyzer_NetScanPodSetPaths
| where startTime >= starttime and startTime <= endtime
| where region in (Regionn)
| where status == "lossy"
| summarize count() by bin(startTime, 1m)
| render timechart 

```

### NetScan - Lossy Path Count(IPv6)

```kql
let starttime = _startTime;
let endtime = _endTime;
let Regionss = Regionn;
cluster("azphynet").database("NetPerfKustoDB").PerfAnalyzer_NetScanV6PodSetPaths
| where startTime >= starttime and startTime <= endtime
| where region in (Regionn)
| where status == "lossy"
| summarize count() by bin(startTime, 1m)
| render timechart
```

### NetScan - Region Level DC-to-DC Noloss Path Count(IPv4)

```kql
let starttime = _startTime;
let endtime = _endTime;
cluster("azphynet").database("NetPerfKustoDB").PerfAnalyzer_NetScanPodSetPaths
| where startTime >= starttime and startTime <= endtime
| where region in (Regionn)
| extend SrcDC=split(startDevice, "-")[0]
| extend DstDC=split(endDevice, "-")[0]
| where status != "noloss"
| project startTime, SrcDC,startDevice, DstDC,endDevice, status, lossRate,viaNode,vantagePoint
| extend Path=strcat(SrcDC, "-", DstDC)
//| extend PathHash= hash(tostring(array_sort_asc(split(Path, "-"))))
| summarize count=count() by bin(startTime, 1m),Path
| render columnchart  
```

### NetScan - Region Level DC-to-DC NoLoss Path Count (IPv6)

```kql
let starttime = _startTime;
let endtime = _endTime;
cluster("azphynet").database("NetPerfKustoDB").PerfAnalyzer_NetScanV6PodSetPaths
| where startTime >= starttime and startTime <= endtime
| where region in (Regionn)
| extend SrcDC=split(startDevice, "-")[0]
| extend DstDC=split(endDevice, "-")[0]
| where status != "noloss"
| project startTime, SrcDC,startDevice, DstDC,endDevice, status, lossRate,viaNode,vantagePoint
| extend Path=strcat(SrcDC, "-", DstDC)
//| extend PathHash= hash(tostring(array_sort_asc(split(Path, "-"))))
| summarize count=count() by bin(startTime, 1m),Path
| render columnchart  
```

### Critical IcM Alert for PhyNet in defined Region

```kql
let devicelist=cluster("Azphynet").database("azdhmds").DeviceStatic
| where Regions in (Regionn)
| where DeviceName contains "t0" or DeviceName contains "t1" or DeviceName contains "t2" or DeviceName contains "rh" or DeviceName contains "rwa" or DeviceName contains "owr" or DeviceName contains "ah" or DeviceName contains "icr" or DeviceName contains "ier" or DeviceName contains "ter" or DeviceName contains "omt"
| distinct DeviceName;
let SPAN=cluster("Azphynet").database("azdhmds").DeviceStatic
| where Regions == "useast"
| where  Role== "Optical"
| distinct Slices;
cluster('azwan').database('Swan').f_GetHistoricIncidents(['_startTime'], ['_endTime'],  '')
| where Severity in (0,1,2,3)
| where OwningTeamName  contains "PhysicalNetwork" or OwningTeamName contains "NetScan" or OwningTeamName contains "SWANDRI" or OwningTeamName contains "NetAssistAutomation" or OwningTeamName contains "Optical"
| where Title contains "Regional DIP-DIP Availability Degraded causing KHI failure" or Title contains "BGP Hold Timer Expiry between" or Title contains "High Link Utilization" or Title contains "[LinkCrc]" or Title contains "[LinkFlap] Interface flaps between" or Title contains "Span Event" or Title contains "Device exhibiting millions of discards" or Title contains "BadDeviceReload" or Title contains "KHI"
| where OccurringDeviceName in~ (devicelist) or OccurringDeviceName in~ (SPAN)
| extend IcMLink=strcat("https://portal.microsofticm.com/imp/v3/incidents/details/", IncidentId, "/home")
| project IncidentId, OccurringDeviceName, CreateDate, Severity, Status, OwningTeamName, Title,ParentIncidentId, ChildCount, IcMLink
//union cluster('azwan').database('Swan').f_GetHistoricIncidents(['_startTime'], ['_endTime'],  'High Link Utilization') ,cluster('azwan').database('Swan').f_GetHistoricIncidents(['_startTime'], ['_endTime'],  'Regional DIP-DIP Availability Degraded causing KHI failure'),cluster('azwan').database('Swan').f_GetHistoricIncidents(['_startTime'], ['_endTime'], 'BGP Hold Timer Expiry between')
//| where Severity == "2"
//| where OwningTeamName contains "PhysicalNetwork" or OwningTeamName contains "NetScan" or OwningTeamName contains "SWANDRI" or OwningTeamName contains "NetAssistAutomation"
//| extend IcMLink=strcat("https://portal.microsofticm.com/imp/v3/incidents/details/", IncidentId, "/home")
//| project IncidentId, OccurringDeviceName, CreateDate, Severity, Status, OwningTeamName, Title,ParentIncidentId, ChildCount, IcMLink


```

### NetScan - Packet Corrupt Rate Per Region(IPv4)

```kql
let starttime = _startTime;
let endtime = _endTime;
cluster("azphynet").database("NetPerfKustoDB").PerfAnalyzer_NetScanPodSetPaths
| where startTime >= starttime and startTime <= endtime
| where corruptRate !=0
| summarize avg(corruptRate) by startTime
| render columnchart 
```

### NetScan - Region Level Path Loss Ratio Per Probe Agent DC(IPv4)

```kql
let starttime = _startTime;
let endtime = _endTime;
cluster("azphynet").database("NetPerfKustoDB").PerfAnalyzer_NetScanPodSetPaths
| where startTime >= starttime and startTime <= endtime
| where region in (Regionn)
| extend ProbeAgentDcCode=substring(vantagePoint, 0, 2)
| summarize Noloss=countif(status  == "noloss"), All=count() by bin(startTime, 1m),ProbeAgentDcCode
| project startTime, ProbeAgentDcCode,LossPathRatio= toreal((All - Noloss)) / All * 100
| render timechart 
//cluster('azphynet').database('NetPerfKustoDB').PerfAnalyzer_NetLatencyPodSetPaths 
//| where startTime >= starttime and startTime <= endtime
//| where region in (Regionn)
//| summarize Latency=round(avg(latencyMilliseconds), 4), SuccessRate=round(avg(successRate), 2) by bin(startTime, 1m), region
//| project startTime, Latency, SuccessRate, region
//| render timechart
```

### NetScan - Packet Corrupt Rate Per Region(IPv6)

```kql
let starttime = _startTime;
let endtime = _endTime;
cluster("azphynet").database("NetPerfKustoDB").PerfAnalyzer_NetScanV6PodSetPaths
| where startTime >= starttime and startTime <= endtime
| where region in (Regionn)
| where corruptRate !=0
| summarize avg(corruptRate) by startTime
| render columnchart 
```

### NetScan - Region Level Path Loss Ratio Per Probe Agent DC(IPv6)

```kql
let starttime = _startTime;
let endtime = _endTime;
cluster("azphynet").database("NetPerfKustoDB").PerfAnalyzer_NetScanV6PodSetPaths
| where startTime >= starttime and startTime <= endtime
| where region in (Regionn)
| extend ProbeAgentDcCode=substring(vantagePoint, 0, 2)
| summarize Noloss=countif(status  == "noloss"), All=count() by bin(startTime, 1m),ProbeAgentDcCode
| project startTime, ProbeAgentDcCode,LossPathRatio= toreal((All - Noloss)) / All * 100
| render timechart 
//cluster('azphynet').database('NetPerfKustoDB').PerfAnalyzer_NetLatencyPodSetPaths 
//| where startTime >= starttime and startTime <= endtime
//| where region in (Regionn)
//| summarize Latency=round(avg(latencyMilliseconds), 4), SuccessRate=round(avg(successRate), 2) by bin(startTime, 1m), region
//| project startTime, Latency, SuccessRate, region
//| render timechart
```

### PathScan - Loss Ratio to Cluster Level(IPv4)

```kql
let starttime = _startTime;
let endtime = _endTime;
let cluster=materialize(cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 1d  and PreciseTimeStamp <= endtime
| where Region in (Regionn)
| distinct Tenant
);
cluster('azphynet').database('azdhsd').PathScanHealthCheck_Cluster
| where TIMESTAMP > starttime and TIMESTAMP < endtime
| where Cluster in (cluster)
| project TIMESTAMP, LossyPathRatio, Cluster
| render timechart
```

### PV

```kql
let pv=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('kusto').adxpageview| where page contains "b01/phynet";
let pvcount=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('microsoft').adxpageview | where page contains "b01/phynet" | summarize count();
union pv, pvcount
```

### Per Datacenter BGP Down Event In [T2<-->RH] or [T2<-->AZNG]

```kql
let st=_startTime;
let et=_endTime;
let starttime= _startTime;
let endtime = _endTime;
let device=cluster("Azphynet").database("azdhmds").DeviceStatic
| where Regions in (Regionn)
| where AzureDeviceType in ("RegionalHub","DCSpine","AZNGHub")
| distinct DeviceName;
cluster('azphynet.kusto.windows.net').database('azdhsd').BgpFlap
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where SrcDevice in (device)
| where DstDevice in (device)
| where state in ("Idle","Down")
| extend SrcDC=tostring(split(SrcDevice, "-")[0])
| extend SrcIDF=strcat("IDF",substring(tostring(split(SrcDevice, "-")[2]), 1, 1))
| extend SrcDCDeviceType=extract(@"[0-9]+([a-zA-Z0-9]+)$", 1, SrcDevice)
| extend DstDC=tostring(split(DstDevice, "-")[0])
| extend DstIDF=strcat("IDF", substring(tostring(split(DstDevice, "-")[2]), 1, 1))
| extend DstDCDeviceType=extract(@"[0-9]+([a-zA-Z0-9]+)$", 1, DstDevice)
| extend Pair=strcat(toupper(SrcDCDeviceType), "(", SrcDC,"-", SrcIDF, ")","---->", toupper(DstDCDeviceType), "(", DstDC, "-",DstIDF, ")")
| summarize count=count() by bin(TIMESTAMP, 1m),Pair
| render columnchart
```

### Per Datacenter BGP Up Event In [T2<-->RH] or [T2<-->AZNG]

```kql
let st=_startTime;
let et=_endTime;
let starttime= _startTime;
let endtime = _endTime;
let device=cluster("Azphynet").database("azdhmds").DeviceStatic
| where Regions in (Regionn)
| where AzureDeviceType in ("RegionalHub","DCSpine","AZNGHub")
| distinct DeviceName;
cluster('azphynet.kusto.windows.net').database('azdhsd').BgpFlap
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where SrcDevice in (device)
| where DstDevice in (device)
| where state in ("Established","Up")
| extend SrcDC=tostring(split(SrcDevice, "-")[0])
| extend SrcIDF=strcat("IDF",substring(tostring(split(SrcDevice, "-")[2]), 1, 1))
| extend SrcDCDeviceType=extract(@"[0-9]+([a-zA-Z0-9]+)$", 1, SrcDevice)
| extend DstDC=tostring(split(DstDevice, "-")[0])
| extend DstIDF=strcat("IDF", substring(tostring(split(DstDevice, "-")[2]), 1, 1))
| extend DstDCDeviceType=extract(@"[0-9]+([a-zA-Z0-9]+)$", 1, DstDevice)
| extend Pair=strcat(toupper(SrcDCDeviceType), "(", SrcDC,"-", SrcIDF, ")","---->", toupper(DstDCDeviceType), "(", DstDC, "-",DstIDF, ")")
| summarize count=count() by bin(TIMESTAMP, 1m),Pair
| render columnchart
```

### Per SPAN BGP Down Event In [T2-->RH] or [T2-->AZNG]

```kql
let st=_startTime;
let et=_endTime;
let starttime= _startTime;
let endtime = _endTime;
let device=cluster("Azphynet").database("azdhmds").DeviceStatic
| where Regions in (Regionn)
| where AzureDeviceType in ("RegionalHub","DCSpine","AZNGHub")
| distinct DeviceName;
let SPANInfo=cluster('waneng.westus2.kusto.windows.net').database('waneng').GetAllOpticalLinks
| extend pair = strcat(DeviceA, "->", DeviceZ);
cluster('azphynet.kusto.windows.net').database('azdhsd').BgpFlap
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where SrcDevice in (device)
| where DstDevice in (device)
| where state in ("Idle","Down")
| extend FlapPair=strcat(toupper(SrcDevice), "->", toupper(DstDevice))
| project TIMESTAMP, FlapPair
| join SPANInfo on  $left.FlapPair == $right.pair
| summarize count=count() by bin(TIMESTAMP, 1m), SolutionId
| render columnchart  
```

### Per SPAN BGP Up Event In [T2-->RH] or [T2-->AZNG]

```kql
let st=_startTime;
let et=_endTime;
let starttime= _startTime;
let endtime = _endTime;
let device=cluster("Azphynet").database("azdhmds").DeviceStatic
| where Regions in (Regionn)
| where AzureDeviceType in ("RegionalHub","DCSpine","AZNGHub")
| distinct DeviceName;
let SPANInfo=cluster('waneng.westus2.kusto.windows.net').database('waneng').GetAllOpticalLinks
| extend pair = strcat(DeviceA, "->", DeviceZ);
cluster('azphynet.kusto.windows.net').database('azdhsd').BgpFlap
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where SrcDevice in (device)
| where DstDevice in (device)
| where state in ("Established","Up")
| extend FlapPair=strcat(toupper(SrcDevice), "->", toupper(DstDevice))
| project TIMESTAMP, FlapPair
| join SPANInfo on  $left.FlapPair == $right.pair
| summarize count=count() by bin(TIMESTAMP, 1m), SolutionId
| render columnchart  
```

### Per Source Device - BGP Down Event In [T2<-->RH] or [T2<-->AZNG] 

```kql
let st=_startTime;
let et=_endTime;
let starttime= _startTime;
let endtime = _endTime;
let device=cluster("Azphynet").database("azdhmds").DeviceStatic
| where Regions in (Regionn)
| where AzureDeviceType in ("RegionalHub","DCSpine","AZNGHub")
| distinct DeviceName;
cluster('azphynet.kusto.windows.net').database('azdhsd').BgpFlap
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where SrcDevice in (device)
| where DstDevice in (device)
| where state in ("Idle","Down")
| project  TIMESTAMP, SrcDevice, DstDevice, state
| summarize  count() by bin(TIMESTAMP, 1m), SrcDevice
| render columnchart 
```

### RAW Data - BGP Down Event In [T2<-->RH] or [T2<-->AZNG] 

```kql
let st=_startTime;
let et=_endTime;
let starttime= _startTime;
let endtime = _endTime;
let device=cluster("Azphynet").database("azdhmds").DeviceStatic
| where Regions in (Regionn)
| where AzureDeviceType in ("RegionalHub","DCSpine","AZNGHub")
| distinct DeviceName;
cluster('azphynet.kusto.windows.net').database('azdhsd').BgpFlap
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where SrcDevice in (device)
| where DstDevice in (device)
| where state in ("Idle","Down")
| project  TIMESTAMP, SrcDevice, DstDevice, state
```

### Per Destination Device - BGP Down Event In [T2<-->RH] or [T2<-->AZNG] 

```kql
let st=_startTime;
let et=_endTime;
let starttime= _startTime;
let endtime = _endTime;
let device=cluster("Azphynet").database("azdhmds").DeviceStatic
| where Regions in (Regionn)
| where AzureDeviceType in ("RegionalHub","DCSpine","AZNGHub")
| distinct DeviceName;
cluster('azphynet.kusto.windows.net').database('azdhsd').BgpFlap
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where SrcDevice in (device)
| where DstDevice in (device)
| where state in ("Idle","Down")
| summarize count=count() by bin(TIMESTAMP, 1m), DstDevice
| render columnchart 
```

### RAW Data - BGP Up Event In [T2<-->RH] or [T2<-->AZNG] 

```kql
let st=_startTime;
let et=_endTime;
let starttime= _startTime;
let endtime = _endTime;
let device=cluster("Azphynet").database("azdhmds").DeviceStatic
| where Regions in (Regionn)
| where AzureDeviceType in ("RegionalHub","DCSpine","AZNGHub")
| distinct DeviceName;
cluster('azphynet.kusto.windows.net').database('azdhsd').BgpFlap
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where SrcDevice in (device)
| where DstDevice in (device)
| where state in ("Established","Up")
| project  TIMESTAMP, SrcDevice, DstDevice, state
```

### Per Source Device - BGP Up Event In [T2<-->RH] or [T2<-->AZNG] 

```kql
let st=_startTime;
let et=_endTime;
let starttime= _startTime;
let endtime = _endTime;
let device=cluster("Azphynet").database("azdhmds").DeviceStatic
| where Regions in (Regionn)
| where AzureDeviceType in ("RegionalHub","DCSpine","AZNGHub")
| distinct DeviceName;
cluster('azphynet.kusto.windows.net').database('azdhsd').BgpFlap
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where SrcDevice in (device)
| where DstDevice in (device)
| where state in ("Established","Up")
| project  TIMESTAMP, SrcDevice, DstDevice, state
| summarize  count() by bin(TIMESTAMP, 1m), SrcDevice
| render columnchart 
```

### Per Destination Device - BGP Up Event In [T2<-->RH] or [T2<-->AZNG] 

```kql
let st=_startTime;
let et=_endTime;
let starttime= _startTime;
let endtime = _endTime;
let device=cluster("Azphynet").database("azdhmds").DeviceStatic
| where Regions in (Regionn)
| where AzureDeviceType in ("RegionalHub","DCSpine","AZNGHub")
| distinct DeviceName;
cluster('azphynet.kusto.windows.net').database('azdhsd').BgpFlap
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where SrcDevice in (device)
| where DstDevice in (device)
| where state in ("Established","Up")
| summarize count=count() by bin(TIMESTAMP, 1m), DstDevice
| render columnchart 
```

### Critical IcM{0,1,2} Alert for all Region in PhyNet

```kql
cluster('azwan').database('Swan').f_GetHistoricIncidents(['_startTime'], ['_endTime'],  '')
| where Severity in (0,1,2)
| where OwningTeamName  contains "PhysicalNetwork" or OwningTeamName contains "NetScan" or OwningTeamName contains "SWANDRI" or OwningTeamName contains "NetAssistAutomation" or OwningTeamName contains "Optical"
| where Title contains "Regional DIP-DIP Availability Degraded causing KHI failure" or Title contains "BGP Hold Timer Expiry between" or Title contains "High Link Utilization" or Title contains "[LinkCrc]" or Title contains "[LinkFlap] Interface flaps between" or Title contains "Span Event" or Title contains "Device exhibiting millions of discards"
| extend IcMLink=strcat("https://portal.microsofticm.com/imp/v3/incidents/details/", IncidentId, "/home")
| project tostring(IncidentId), OccurringDeviceName, CreateDate, Severity, Status, OwningTeamName, Title,ParentIncidentId, ChildCount, IcMLink
//union cluster('azwan').database('Swan').f_GetHistoricIncidents(['_startTime'], ['_endTime'],  'High Link Utilization') ,cluster('azwan').database('Swan').f_GetHistoricIncidents(['_startTime'], ['_endTime'],  'Regional DIP-DIP Availability Degraded causing KHI failure'),cluster('azwan').database('Swan').f_GetHistoricIncidents(['_startTime'], ['_endTime'], 'BGP Hold Timer Expiry between')
//| where Severity == "2"
//| where OwningTeamName contains "PhysicalNetwork" or OwningTeamName contains "NetScan" or OwningTeamName contains "SWANDRI" or OwningTeamName contains "NetAssistAutomation"
//| extend IcMLink=strcat("https://portal.microsofticm.com/imp/v3/incidents/details/", IncidentId, "/home")
//| project IncidentId, OccurringDeviceName, CreateDate, Severity, Status, OwningTeamName, Title,ParentIncidentId, ChildCount, IcMLink
```

### SPAN Metadata Info

```kql
let starttime = _startTime;
let endtime = _endTime;
let Regionss = Regionn;
let endDeviceType = dynamic(['AZNGHub','RegionalHub']);
let startDeviceList= cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where CloudType == "Public"
| where Regions =~ Regionss
| where NgsDeviceType == "SpineRouter"
| project DeviceName;
let endDeviceList = cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where CloudType == "Public"
| where Regions =~ Regionss
| where NgsDeviceType in~ ( endDeviceType )
| join kind = leftouter cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceMetadata on $left.DeviceName==$right.DeviceName
| extend endLocation=strcat(LocationType, LocationIndex,"_",DcCode)
| project DeviceName;
let l3 = cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceInterfaceLinks
| where StartDevice in~ ( startDeviceList ) and EndDevice in~ ( endDeviceList );
let startL1omt = l3
| join ( cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceInterfaceLinks        
            | where LinkType == 'DeviceOpticalLink'    
            | project StartDevice, StartPort, StartPortChannel, EndDevice, EndPort)
        on $left.StartDevice == $right.StartDevice and $left.StartPort == $right.StartPort
| project StartDevice, StartPort, StartPortChannel, startOmt = EndDevice1, startOmtPort = EndPort1, EndDevice, EndPort;
startL1omt
|  extend spanid = tostring(split(startOmt, "-",1)[0])
| extend idf_number = extract(@"(010.-0.00)",0,StartDevice)
| extend idf = case(idf_number contains "0100", "IDF1", idf_number contains "0200", "IDF2", idf_number contains "0300", "IDF3", idf_number contains "0400", "IDF4", idf_number )
| join kind=leftouter(cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic)on $left.StartDevice == $right.DeviceName
| project StartDevice, StartPortChannel, spanid, EndDevice, idf, DcCode, Regions, EndPort
| join kind=leftouter (cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceMetadata) on $left.EndDevice == $right.DeviceName
//| extend rng_code = extract(@"(\w*-)",0,EndDevice)
| extend endDeviceLoc = strcat((extract(@"((\w*)-)",0,EndDevice)), LocationType, LocationIndex)
| project DcCode, StartDevice, StartPortChannel, spanid, endDeviceLoc, idf, Regions, EndDevice, EndPort
| summarize noOfLinks = count(EndPort) by DcCode, StartDevice, StartPortChannel, spanid, endDeviceLoc, idf, Regions, EndDevice
| summarize make_set(spanid), noOfDiffSpanLinksPerBundle = count_distinct(spanid) by StartPortChannel, StartDevice, DcCode, endDeviceLoc, idf, Regions, noOfLinks, EndDevice
| extend index1 = extract(@".*-.*-.*-(\d)", 1, EndDevice)              // first digit of suffix
| extend index2 = extract(@".*-.*-.*-(\d+)", 1, EndDevice)           // second digit of suffix
| extend DeviceIDF = extract(@"(.*-.*-.*-)", 1, EndDevice)            // prefix up to last dash
| extend rh_ah_direction = case(
      EndDevice contains "rhw", "rhw",
      EndDevice contains "rhe", "rhe",
      EndDevice contains "ahy", "ahy",
      EndDevice contains "ahz", "ahz",
      EndDevice contains "t2", "t2",
      extract(@"([a-zA-Z0-9]+)$", 1, EndDevice)                       // fallback = whatever suffix is
    ) 
| extend t2index1 = extract(@".*-.*-.*-(\d).*", 1, StartDevice)
| extend t2index2 = iff(StartDevice contains "dsp", extract(@".*-.*-.*-(\d\w).*", 1, StartDevice), extract(@".*-.*-.*-(\d+).*", 1, StartDevice))
| extend T2DeviceIDF = extract(@"(.*-.*-.*-).*", 1, StartDevice)
| mv-expand spanid = set_spanid
| summarize make_set(StartDevice), make_set(EndDevice), sum(noOfLinks), min(t2index2), max(t2index2), min(toint(index2)), max(toint(index2)) by tostring(spanid), DeviceIDF, T2DeviceIDF, idf, DcCode, endDeviceLoc, noOfDiffSpanLinksPerBundle,  rh_ah_direction
| extend t2Regex = iff(T2DeviceIDF contains "dsp" ,strcat(T2DeviceIDF, "[",min_t2index2, "-", max_t2index2, "]"),strcat(T2DeviceIDF, "[",min_t2index2, "-", max_t2index2, "]", "t2"))
| extend rhRegex = strcat(DeviceIDF, "[", min_index2, "-", max_index2, "]", rh_ah_direction),rh_ah_direction
| extend span_with_regex = strcat(tostring(spanid), ":", t2Regex, "_", rhRegex)
| summarize make_set(span_with_regex), make_set(spanid) by DcCode, idf, endDeviceLoc, noOfDiffSpanLinksPerBundle, sum_noOfLinks
| project StartDcCode = DcCode, idf, EndSite = endDeviceLoc, SpanInfo = set_spanid, DeviceRegexPerSpan = set_span_with_regex, noOfDiffSpanLinksPerBundle, TotalLinks = sum_noOfLinks
| order by StartDcCode, EndSite asc 
```

### Packet Discard Counter For AZNG and RH

```kql
let starttime = _startTime;
let endtime = _endTime;
let Regionss = Regionn;
let rhaznglist=cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where NgsDeviceType has_any ('RegionalHub', 'AZNGHub', "RegionalAggregator")
| where Regions in (Regionss)
| distinct tolower(DeviceName);
cluster('Aznwnetmon').database('aznwmds').sXInterfaceTable 
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where DeviceName in (rhaznglist)
| project ReceivedUtc, DeviceName,ifInDiscards_Counter, ifOutDiscards_Counter, ifInErrors_Counter, ifOutErrors_Counter
| summarize InDiscard=sum(ifInDiscards_Counter), OutDiscard=sum(ifOutDiscards_Counter), InError=sum(ifInErrors_Counter), OutError=sum(ifOutErrors_Counter) by bin(ReceivedUtc, 5m), DeviceName
| render columnchart
```

### Traffic Drain By Traffic_Shift_Away

```kql
let starttime = _startTime;
let endtime = _endTime;
let Regionss = Regionn;
let RegionDevicelist=cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where NgsDeviceType has_any ('RegionalHub', 'AZNGHub', "RegionalAggregator", "SpineRouter", "LeafRouter")
| where Regions in (Regionss)
| distinct tolower(DeviceName);
cluster('phynetval').database('aznwmds').AzureAaaMasterSessions
| where TIMESTAMP >= starttime and TIMESTAMP<=endtime
| where deviceName in (RegionDevicelist)
| where command contains "Traffic_Shift_Away"
| project PreciseTimeStamp, deviceName, user, command
| summarize count() by bin(PreciseTimeStamp, 1m), deviceName
| render columnchart  
```

### Traffic Drain By Isolate_Downstream_Neighbor

```kql
let starttime = _startTime;
let endtime = _endTime;
let Regionss = Regionn;
let RegionDevicelist=cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where NgsDeviceType has_any ('RegionalHub', 'AZNGHub', "RegionalAggregator", "SpineRouter", "LeafRouter")
| where Regions in (Regionss)
| distinct tolower(DeviceName);
cluster('phynetval').database('aznwmds').AzureAaaMasterSessions
| where TIMESTAMP >= starttime and TIMESTAMP<=endtime
| where deviceName in (RegionDevicelist)
| where command contains "Isolate_Downstream_Neighbor"
| project PreciseTimeStamp, deviceName, user, command
| summarize count() by bin(PreciseTimeStamp, 1m), deviceName
| render columnchart  
```

### Device Configuration Change by Route-Map

```kql
let starttime = _startTime;
let endtime = _endTime;
let Regionss = Regionn;
let RegionDevicelist=cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where NgsDeviceType has_any ('RegionalHub', 'AZNGHub', "RegionalAggregator", "SpineRouter", "LeafRouter")
| where Regions in (Regionss)
| distinct tolower(DeviceName);
cluster('phynetval').database('aznwmds').AzureAaaMasterSessions
| where TIMESTAMP >= starttime and TIMESTAMP<=endtime
| where deviceName in (RegionDevicelist)
| where command contains "Route-map"
| project PreciseTimeStamp, deviceName, user, command
| summarize count() by bin(PreciseTimeStamp, 1m), deviceName
| render columnchart  
```

### Traffic Drain To Destination DC-IDF By Isolate_Downstream_Neighbor

```kql
let starttime = _startTime;
let endtime = _endTime;
let Regionss = Regionn;
let RegionDevicelist=cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where NgsDeviceType has_any ('RegionalHub', 'AZNGHub', "RegionalAggregator", "SpineRouter", "LeafRouter")
| where Regions in (Regionss)
| distinct tolower(DeviceName);
let StartDeviceIPv4=cluster('Aznwcc').database('aznwmds').DeviceInterfaceLinks
| where StartDevice in (RegionDevicelist)
| where isnotempty(StartBGPV4Peer)
| distinct devicetoBGPPair=strcat(StartDevice,EndBGPV4Peer), device=EndDevice;
let StartDeviceIPv6=cluster('Aznwcc').database('aznwmds').DeviceInterfaceLinks
| where StartDevice in (RegionDevicelist)
| where isnotempty(StartBGPV6Peer)
| distinct devicetoBGPPair=strcat(StartDevice,EndBGPV6Peer), device=EndDevice;
let EndDeviceIPv4=cluster('Aznwcc').database('aznwmds').DeviceInterfaceLinks
| where EndDevice in (RegionDevicelist)
| where isnotempty(EndBGPV4Peer)
| distinct devicetoBGPPair=strcat(EndDevice,StartBGPV4Peer), device=StartDevice;
let EndDeviceIPv6=cluster('Aznwcc').database('aznwmds').DeviceInterfaceLinks
| where StartDevice in (RegionDevicelist)
| where isnotempty(EndDevice)
| distinct devicetoBGPPair=strcat(EndDevice,StartBGPV6Peer), device=StartDevice;
let DeviceList=union StartDeviceIPv4, StartDeviceIPv6, EndDeviceIPv4, EndDeviceIPv6
| distinct devicetoBGPPair=tolower(devicetoBGPPair), device;
cluster('phynetval').database('aznwmds').AzureAaaMasterSessions
| where TIMESTAMP >= starttime and TIMESTAMP<=endtime
| where deviceName in (RegionDevicelist)
| where command contains "Isolate_Downstream_Neighbor"
| where command startswith "neighbor"
| project PreciseTimeStamp, deviceName, user, command
| extend devicetoBGPPair = strcat(deviceName,tostring(split(command, " ")[1]))
| join kind=leftouter DeviceList on devicetoBGPPair
| project PreciseTimeStamp, deviceName, user, command, Peer=device
| extend DC=tostring(split(Peer, "-")[0])
| extend idf_number = extract(@"(010.-0.00)",0,Peer)
| extend IDF = case(idf_number contains "0100", "IDF1", idf_number contains "0200", "IDF2", idf_number contains "0300", "IDF3", idf_number contains "0400", "IDF4", idf_number )
| extend PeerLevel = case(
      Peer contains "rhw", "rhw",
      Peer contains "rhe", "rhe",
      Peer contains "ahy", "ahy",
      Peer contains "ahz", "ahz",
      Peer contains "t2", "t2",
      extract(@"([a-zA-Z0-9]+)$", 1, Peer)
    ) 
| extend Peer=toupper(strcat(DC,"-",IDF, "-", PeerLevel))
| summarize count() by bin(PreciseTimeStamp, 1m), Peer
| render columnchart 

```

## PhyNet T2-RH Utilization

### AZ-DC Mapping

```kql
let starttime = _startTime;
let endtime = _endTime;
let Regionss = Regionn;
cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where TIMESTAMP > starttime - 1h and TIMESTAMP < endtime
| where Region in (Regionss)
| distinct AvailabilityZone, DataCenterName
| summarize DataCenterName=make_list(DataCenterName) by AvailabilityZone
```

### SPAN Mapping: T2 - RH

```kql
let starttime = _startTime;
let endtime = _endTime;
let Regionss = Regionn;
let Datacname = DCName;
let dd=cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where NgsDeviceType has_any ('RegionalHub','SpineRouter', 'AZNGHub', 'RegionalAggregator','RegionalShim') 
| where Regions in (Regionss)
| where DeviceName contains Datacname
| distinct toupper(DeviceName);
cluster('waneng.westus2.kusto.windows.net').database('waneng').GetAllOpticalLinks
| where DeviceA in (dd) 
| where DeviceZ contains "rh"
| project SolutionId, DeviceA, DeviceZ, OpticalDeviceA, OpticalDeviceZ, PortA,PortZ, SpanType
| order  by DeviceA asc  
```

### IDF1: T2- RHW - Utilization

```kql
let starttime = _startTime;
let endtime = _endTime;
let Regionss = Regionn;
let Datacname = DCName;
let dd=cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where NgsDeviceType has_any ('RegionalHub','SpineRouter', 'AZNGHub', 'RegionalAggregator','RegionalShim') 
| where Regions in (Regionss)
| where DeviceName contains Datacname
| distinct toupper(DeviceName);
let SPANToLinks=cluster('waneng.westus2.kusto.windows.net').database('waneng').GetAllOpticalLinks
| where DeviceA in (dd) 
| where DeviceZ contains "rh"
| distinct SolutionId, link=tolower(strcat(DeviceA,"----",DeviceZ));
let IDF1=cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where NgsDeviceType has_any ('RegionalHub','SpineRouter', 'AZNGHub', 'RegionalAggregator','RegionalShim') 
| where NgsDeviceType == "SpineRouter"
| where Regions in (Regionss)
| where DeviceName contains Datacname
| extend IDF1=tostring(split(DeviceName, "-")[2])
| where IDF1 contains "1"
| distinct DeviceName = tolower(DeviceName);
cluster('azphynet.kusto.windows.net').database('azdhmds').InterfaceData 
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where deviceHostName in (IDF1)
| where ifAlias contains "RHE" or ifAlias contains "RHW"
| extend outUtilization = (ifHCOutOctetsDiff*8.0)/(interval * ifHighSpeed * 1000.00)*100 
| extend intUtilization = (ifHCInOctetsDiff*8.0)/(interval * ifHighSpeed * 1000.00)*100 
| project TIMESTAMP,deviceHostName, ifName,outUtilization, intUtilization, ifHCOutOctetsDiff, ifHCInOctetsDiff, ifHighSpeed, interval, ifAlias
| project TIMESTAMP=bin(TIMESTAMP,3m), link=strcat(deviceHostName, "----", tostring(split(ifAlias, ":")[0])), intUtilization=round(intUtilization,2), outUtilization=round(outUtilization,2)
| summarize InUtilization=avg(intUtilization), OutUtilization=avg(outUtilization) by bin(TIMESTAMP, 1m), link=tolower(link)
| join kind=leftouter SPANToLinks on $left.link == $right.link
| project TIMESTAMP, Link=strcat(SolutionId, ": ", link), InUtilization, OutUtilization
| render timechart
```

### IDF2: T2 - RHE - Utilization

```kql
let starttime = _startTime;
let endtime = _endTime;
let Regionss = Regionn;
let Datacname = DCName;
let dd=cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where NgsDeviceType has_any ('RegionalHub','SpineRouter', 'AZNGHub', 'RegionalAggregator','RegionalShim') 
| where Regions in (Regionss)
| where DeviceName contains Datacname
| distinct toupper(DeviceName);
let SPANToLinks=cluster('waneng.westus2.kusto.windows.net').database('waneng').GetAllOpticalLinks
| where DeviceA in (dd) 
| where DeviceZ contains "rh"
| distinct SolutionId, link=tolower(strcat(DeviceA,"----",DeviceZ));
let IDF2=cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where NgsDeviceType has_any ('RegionalHub','SpineRouter', 'AZNGHub', 'RegionalAggregator','RegionalShim') 
| where NgsDeviceType == "SpineRouter"
| where Regions in (Regionss)
| where DeviceName contains Datacname
| extend IDF2=tostring(split(DeviceName, "-")[2])
| where IDF2 contains "2"
| distinct DeviceName = tolower(DeviceName);
cluster('azphynet.kusto.windows.net').database('azdhmds').InterfaceData 
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where deviceHostName in (IDF2)
| where ifAlias contains "RHE" or ifAlias contains "RHW"
| extend outUtilization = (ifHCOutOctetsDiff*8.0)/(interval * ifHighSpeed * 1000.00)*100 
| extend intUtilization = (ifHCInOctetsDiff*8.0)/(interval * ifHighSpeed * 1000.00)*100 
| project TIMESTAMP,deviceHostName, ifName,outUtilization, intUtilization, ifHCOutOctetsDiff, ifHCInOctetsDiff, ifHighSpeed, interval, ifAlias
| project TIMESTAMP=bin(TIMESTAMP,3m), link=strcat(deviceHostName, "----", tostring(split(ifAlias, ":")[0])), intUtilization=round(intUtilization,2), outUtilization=round(outUtilization,2)
| summarize InUtilization=avg(intUtilization), OutUtilization=avg(outUtilization) by bin(TIMESTAMP, 1m), link=tolower(link)
| join kind=leftouter SPANToLinks on $left.link == $right.link
| project TIMESTAMP, Link=strcat(SolutionId, ": ", link), InUtilization, OutUtilization
| render timechart
```

### IDF3: T2 - RHW - Utilization

```kql
let starttime = _startTime;
let endtime = _endTime;
let Regionss = Regionn;
let Datacname = DCName;
let dd=cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where NgsDeviceType has_any ('RegionalHub','SpineRouter', 'AZNGHub', 'RegionalAggregator','RegionalShim') 
| where Regions in (Regionss)
| where DeviceName contains Datacname
| distinct toupper(DeviceName);
let SPANToLinks=cluster('waneng.westus2.kusto.windows.net').database('waneng').GetAllOpticalLinks
| where DeviceA in (dd) 
| where DeviceZ contains "rh"
| distinct SolutionId, link=tolower(strcat(DeviceA,"----",DeviceZ));
let IDF3=cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where NgsDeviceType has_any ('RegionalHub','SpineRouter', 'AZNGHub', 'RegionalAggregator','RegionalShim') 
| where NgsDeviceType == "SpineRouter"
| where Regions in (Regionss)
| where DeviceName contains Datacname
| extend IDF3=tostring(split(DeviceName, "-")[2])
| where IDF3 contains "3"
| distinct DeviceName = tolower(DeviceName);
cluster('azphynet.kusto.windows.net').database('azdhmds').InterfaceData 
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where deviceHostName in (IDF3)
| where ifAlias contains "RHE" or ifAlias contains "RHW"
| extend outUtilization = (ifHCOutOctetsDiff*8.0)/(interval * ifHighSpeed * 1000.00)*100 
| extend intUtilization = (ifHCInOctetsDiff*8.0)/(interval * ifHighSpeed * 1000.00)*100 
| project TIMESTAMP,deviceHostName, ifName,outUtilization, intUtilization, ifHCOutOctetsDiff, ifHCInOctetsDiff, ifHighSpeed, interval, ifAlias
| project TIMESTAMP=bin(TIMESTAMP,3m), link=strcat(deviceHostName, "----", tostring(split(ifAlias, ":")[0])), intUtilization=round(intUtilization,2), outUtilization=round(outUtilization,2)
| summarize InUtilization=avg(intUtilization), OutUtilization=avg(outUtilization) by bin(TIMESTAMP, 1m), link=tolower(link)
| join kind=leftouter SPANToLinks on $left.link == $right.link
| project TIMESTAMP, Link=strcat(SolutionId, ": ", link), InUtilization, OutUtilization
| render timechart
```

### IDF4: T2 - RHE - Utilization

```kql
let starttime = _startTime;
let endtime = _endTime;
let Regionss = Regionn;
let Datacname = DCName;
let dd=cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where NgsDeviceType has_any ('RegionalHub','SpineRouter', 'AZNGHub', 'RegionalAggregator','RegionalShim') 
| where Regions in (Regionss)
| where DeviceName contains Datacname
| distinct toupper(DeviceName);
let SPANToLinks=cluster('waneng.westus2.kusto.windows.net').database('waneng').GetAllOpticalLinks
| where DeviceA in (dd) 
| where DeviceZ contains "rh"
| distinct SolutionId, link=tolower(strcat(DeviceA,"----",DeviceZ));
let IDF4=cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where NgsDeviceType has_any ('RegionalHub','SpineRouter', 'AZNGHub', 'RegionalAggregator','RegionalShim') 
| where NgsDeviceType == "SpineRouter"
| where Regions in (Regionss)
| where DeviceName contains Datacname
| extend IDF4=tostring(split(DeviceName, "-")[2])
| where IDF4 contains "4"
| distinct DeviceName = tolower(DeviceName);
cluster('azphynet.kusto.windows.net').database('azdhmds').InterfaceData 
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where deviceHostName in (IDF4)
| where ifAlias contains "RHE" or ifAlias contains "RHW"
| extend outUtilization = (ifHCOutOctetsDiff*8.0)/(interval * ifHighSpeed * 1000.00)*100 
| extend intUtilization = (ifHCInOctetsDiff*8.0)/(interval * ifHighSpeed * 1000.00)*100 
| project TIMESTAMP,deviceHostName, ifName,outUtilization, intUtilization, ifHCOutOctetsDiff, ifHCInOctetsDiff, ifHighSpeed, interval, ifAlias
| project TIMESTAMP=bin(TIMESTAMP,3m), link=strcat(deviceHostName, "----", tostring(split(ifAlias, ":")[0])), intUtilization=round(intUtilization,2), outUtilization=round(outUtilization,2)
| summarize InUtilization=avg(intUtilization), OutUtilization=avg(outUtilization) by bin(TIMESTAMP, 1m), link=tolower(link)
| join kind=leftouter SPANToLinks on $left.link == $right.link
| project TIMESTAMP, Link=strcat(SolutionId, ": ", link), InUtilization, OutUtilization
| render timechart
```

### IDF1: T2 - RHW - Discard and Error  - Discard and Error

```kql
let starttime = _startTime;
let endtime = _endTime;
let Regionss = Regionn;
let Datacname = DCName;
let IDF1=cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where NgsDeviceType has_any ('RegionalHub','SpineRouter', 'AZNGHub', 'RegionalAggregator','RegionalShim') 
| where NgsDeviceType == "SpineRouter"
| where Regions in (Regionss)
| where DeviceName contains Datacname
| extend IDF1=tostring(split(DeviceName, "-")[2])
| where IDF1 contains "1"
| distinct DeviceName = tolower(DeviceName);
cluster('azphynet.kusto.windows.net').database('azdhmds').InterfaceData 
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where deviceHostName in (IDF1)
| where ifAlias contains "RHE" or ifAlias contains "RHW"
| project PreciseTimeStamp, deviceHostName, ifName, ifAlias, ifType,link=strcat(deviceHostName, "----", tostring(split(ifAlias, ":")[0])), ifOperStatus, InPacketDiscardPerFiveMinutes=ifInDiscardsDiff, OutPacketDiscardPerFiveMinutes=ifOutDiscardsDiff,InPacketErrorPerFiveMinutes=ifInErrorsDiff, OutPacketErrorPerFiveMinutes=ifOutErrorsDiff
| summarize InPacketErrorPerFiveMinutes=sum(InPacketErrorPerFiveMinutes), OutPacketErrorPerFiveMinutes=sum(OutPacketErrorPerFiveMinutes),InPacketDiscardPerFiveMinutes=sum(InPacketDiscardPerFiveMinutes),  OutPacketDiscardPerFiveMinutes=sum(OutPacketDiscardPerFiveMinutes) by bin(PreciseTimeStamp, 2m), link
| render timechart
```

### IDF2: T2 - RHE  - Discard and Error 

```kql
let starttime = _startTime;
let endtime = _endTime;
let Regionss = Regionn;
let Datacname = DCName;
let IDF2=cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where NgsDeviceType has_any ('RegionalHub','SpineRouter', 'AZNGHub', 'RegionalAggregator','RegionalShim') 
| where NgsDeviceType == "SpineRouter"
| where Regions in (Regionss)
| where DeviceName contains Datacname
| extend IDF2=tostring(split(DeviceName, "-")[2])
| where IDF2 contains "2"
| distinct DeviceName = tolower(DeviceName);
cluster('azphynet.kusto.windows.net').database('azdhmds').InterfaceData 
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where deviceHostName in (IDF2)
| where ifAlias contains "RHE" or ifAlias contains "RHW"
| project PreciseTimeStamp, deviceHostName, ifName, ifAlias, ifType,link=strcat(deviceHostName, "----", tostring(split(ifAlias, ":")[0])), ifOperStatus, InPacketDiscardPerFiveMinutes=ifInDiscardsDiff, OutPacketDiscardPerFiveMinutes=ifOutDiscardsDiff,InPacketErrorPerFiveMinutes=ifInErrorsDiff, OutPacketErrorPerFiveMinutes=ifOutErrorsDiff
| summarize InPacketErrorPerFiveMinutes=sum(InPacketErrorPerFiveMinutes), OutPacketErrorPerFiveMinutes=sum(OutPacketErrorPerFiveMinutes),InPacketDiscardPerFiveMinutes=sum(InPacketDiscardPerFiveMinutes),  OutPacketDiscardPerFiveMinutes=sum(OutPacketDiscardPerFiveMinutes) by bin(PreciseTimeStamp, 2m), link
| render timechart
```

### IDF3: T2 - RHW - Discard and Error

```kql
let starttime = _startTime;
let endtime = _endTime;
let Regionss = Regionn;
let Datacname = DCName;
let IDF3=cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where NgsDeviceType has_any ('RegionalHub','SpineRouter', 'AZNGHub', 'RegionalAggregator','RegionalShim') 
| where NgsDeviceType == "SpineRouter"
| where Regions in (Regionss)
| where DeviceName contains Datacname
| extend IDF3=tostring(split(DeviceName, "-")[2])
| where IDF3 contains "3"
| distinct DeviceName = tolower(DeviceName);
cluster('azphynet.kusto.windows.net').database('azdhmds').InterfaceData 
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where deviceHostName in (IDF3)
| where ifAlias contains "RHE" or ifAlias contains "RHW"
| project PreciseTimeStamp, deviceHostName, ifName, ifAlias, ifType,link=strcat(deviceHostName, "----", tostring(split(ifAlias, ":")[0])), ifOperStatus, InPacketDiscardPerFiveMinutes=ifInDiscardsDiff, OutPacketDiscardPerFiveMinutes=ifOutDiscardsDiff,InPacketErrorPerFiveMinutes=ifInErrorsDiff, OutPacketErrorPerFiveMinutes=ifOutErrorsDiff
| summarize InPacketErrorPerFiveMinutes=sum(InPacketErrorPerFiveMinutes), OutPacketErrorPerFiveMinutes=sum(OutPacketErrorPerFiveMinutes),InPacketDiscardPerFiveMinutes=sum(InPacketDiscardPerFiveMinutes),  OutPacketDiscardPerFiveMinutes=sum(OutPacketDiscardPerFiveMinutes) by bin(PreciseTimeStamp, 2m), link
| render timechart
```

### IDF4: T2 - RHE - Discard and Error

```kql
let starttime = _startTime;
let endtime = _endTime;
let Regionss = Regionn;
let Datacname = DCName;
let IDF4=cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where NgsDeviceType has_any ('RegionalHub','SpineRouter', 'AZNGHub', 'RegionalAggregator','RegionalShim') 
| where NgsDeviceType == "SpineRouter"
| where Regions in (Regionss)
| where DeviceName contains Datacname
| extend IDF4=tostring(split(DeviceName, "-")[2])
| where IDF4 contains "4"
| distinct DeviceName = tolower(DeviceName);
cluster('azphynet.kusto.windows.net').database('azdhmds').InterfaceData 
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where deviceHostName in (IDF4)
| where ifAlias contains "RHE" or ifAlias contains "RHW"
| project PreciseTimeStamp, deviceHostName, ifName, ifAlias, ifType,link=strcat(deviceHostName, "----", tostring(split(ifAlias, ":")[0])), ifOperStatus, InPacketDiscardPerFiveMinutes=ifInDiscardsDiff, OutPacketDiscardPerFiveMinutes=ifOutDiscardsDiff,InPacketErrorPerFiveMinutes=ifInErrorsDiff, OutPacketErrorPerFiveMinutes=ifOutErrorsDiff
| summarize InPacketErrorPerFiveMinutes=sum(InPacketErrorPerFiveMinutes), OutPacketErrorPerFiveMinutes=sum(OutPacketErrorPerFiveMinutes),InPacketDiscardPerFiveMinutes=sum(InPacketDiscardPerFiveMinutes),  OutPacketDiscardPerFiveMinutes=sum(OutPacketDiscardPerFiveMinutes) by bin(PreciseTimeStamp, 2m), link
| render timechart
```

### PV

```kql
let pv=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('kusto').adxpageview| where page contains "b01/phynett2";
let pvcount=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('microsoft').adxpageview | where page contains "b01/phynett2" | summarize count();
union pv, pvcount
```

## PhyNet T2-AZNG Utilization

### IDF1: T2- AZNG - Utilization

```kql
let starttime = _startTime;
let endtime = _endTime;
let Regionss = Regionn;
let Datacname = DCName;
let dd=cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where NgsDeviceType has_any ('RegionalHub','SpineRouter', 'AZNGHub', 'RegionalAggregator','RegionalShim') 
| where Regions in (Regionss)
| where DeviceName contains Datacname
| distinct toupper(DeviceName);
let SPANToLinks=cluster('waneng.westus2.kusto.windows.net').database('waneng').GetAllOpticalLinks
| where DeviceA in (dd) 
| where DeviceZ contains "ah"
| distinct SolutionId, link=tolower(strcat(DeviceA,"----",DeviceZ));
let IDF1=cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where NgsDeviceType has_any ('RegionalHub','SpineRouter', 'AZNGHub', 'RegionalAggregator','RegionalShim') 
| where NgsDeviceType == "SpineRouter"
| where Regions in (Regionss)
| where DeviceName contains Datacname
| extend IDF1=tostring(split(DeviceName, "-")[2])
| where IDF1 contains "1"
| distinct DeviceName = tolower(DeviceName);
cluster('azphynet.kusto.windows.net').database('azdhmds').InterfaceData 
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where deviceHostName in (IDF1)
| where ifAlias contains "AHZ" or ifAlias contains "AHY"
| extend outUtilization = (ifHCOutOctetsDiff*8.0)/(interval * ifHighSpeed * 1000.00)*100 
| extend intUtilization = (ifHCInOctetsDiff*8.0)/(interval * ifHighSpeed * 1000.00)*100 
| project TIMESTAMP,deviceHostName, ifName,outUtilization, intUtilization, ifHCOutOctetsDiff, ifHCInOctetsDiff, ifHighSpeed, interval, ifAlias
| project TIMESTAMP=bin(TIMESTAMP,3m), link=strcat(deviceHostName, "----", tostring(split(ifAlias, ":")[0])), intUtilization=round(intUtilization,2), outUtilization=round(outUtilization,2)
| summarize InUtilization=avg(intUtilization), OutUtilization=avg(outUtilization) by bin(TIMESTAMP, 1m), link=tolower(link)
| join kind=leftouter SPANToLinks on $left.link == $right.link
| project TIMESTAMP, Link=strcat(SolutionId, ": ", link), InUtilization, OutUtilization
| render timechart
```

### IDF2: T2 - AZNG - Utilization

```kql
let starttime = _startTime;
let endtime = _endTime;
let Regionss = Regionn;
let Datacname = DCName;
let dd=cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where NgsDeviceType has_any ('RegionalHub','SpineRouter', 'AZNGHub', 'RegionalAggregator','RegionalShim') 
| where Regions in (Regionss)
| where DeviceName contains Datacname
| distinct toupper(DeviceName);
let SPANToLinks=cluster('waneng.westus2.kusto.windows.net').database('waneng').GetAllOpticalLinks
| where DeviceA in (dd) 
| where DeviceZ contains "ah"
| distinct SolutionId, link=tolower(strcat(DeviceA,"----",DeviceZ));
let IDF2=cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where NgsDeviceType has_any ('RegionalHub','SpineRouter', 'AZNGHub', 'RegionalAggregator','RegionalShim') 
| where NgsDeviceType == "SpineRouter"
| where Regions in (Regionss)
| where DeviceName contains Datacname
| extend IDF2=tostring(split(DeviceName, "-")[2])
| where IDF2 contains "2"
| distinct DeviceName = tolower(DeviceName);
cluster('azphynet.kusto.windows.net').database('azdhmds').InterfaceData 
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where deviceHostName in (IDF2)
| where ifAlias contains "AHZ" or ifAlias contains "AHY"
| extend outUtilization = (ifHCOutOctetsDiff*8.0)/(interval * ifHighSpeed * 1000.00)*100 
| extend intUtilization = (ifHCInOctetsDiff*8.0)/(interval * ifHighSpeed * 1000.00)*100 
| project TIMESTAMP,deviceHostName, ifName,outUtilization, intUtilization, ifHCOutOctetsDiff, ifHCInOctetsDiff, ifHighSpeed, interval, ifAlias
| project TIMESTAMP=bin(TIMESTAMP,3m), link=strcat(deviceHostName, "----", tostring(split(ifAlias, ":")[0])), intUtilization=round(intUtilization,2), outUtilization=round(outUtilization,2)
| summarize InUtilization=avg(intUtilization), OutUtilization=avg(outUtilization) by bin(TIMESTAMP, 1m), link=tolower(link)
| join kind=leftouter SPANToLinks on $left.link == $right.link
| project TIMESTAMP, Link=strcat(SolutionId, ": ", link), InUtilization, OutUtilization
| render timechart
```

### IDF3: T2 - AZNG - Utilization

```kql
let starttime = _startTime;
let endtime = _endTime;
let Regionss = Regionn;
let Datacname = DCName;
let dd=cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where NgsDeviceType has_any ('RegionalHub','SpineRouter', 'AZNGHub', 'RegionalAggregator','RegionalShim') 
| where Regions in (Regionss)
| where DeviceName contains Datacname
| distinct toupper(DeviceName);
let SPANToLinks=cluster('waneng.westus2.kusto.windows.net').database('waneng').GetAllOpticalLinks
| where DeviceA in (dd) 
| where DeviceZ contains "ah"
| distinct SolutionId, link=tolower(strcat(DeviceA,"----",DeviceZ));
let IDF3=cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where NgsDeviceType has_any ('RegionalHub','SpineRouter', 'AZNGHub', 'RegionalAggregator','RegionalShim') 
| where NgsDeviceType == "SpineRouter"
| where Regions in (Regionss)
| where DeviceName contains Datacname
| extend IDF3=tostring(split(DeviceName, "-")[2])
| where IDF3 contains "3"
| distinct DeviceName = tolower(DeviceName);
cluster('azphynet.kusto.windows.net').database('azdhmds').InterfaceData 
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where deviceHostName in (IDF3)
| where ifAlias contains "AHZ" or ifAlias contains "AHY"
| extend outUtilization = (ifHCOutOctetsDiff*8.0)/(interval * ifHighSpeed * 1000.00)*100 
| extend intUtilization = (ifHCInOctetsDiff*8.0)/(interval * ifHighSpeed * 1000.00)*100 
| project TIMESTAMP,deviceHostName, ifName,outUtilization, intUtilization, ifHCOutOctetsDiff, ifHCInOctetsDiff, ifHighSpeed, interval, ifAlias
| project TIMESTAMP=bin(TIMESTAMP,3m), link=strcat(deviceHostName, "----", tostring(split(ifAlias, ":")[0])), intUtilization=round(intUtilization,2), outUtilization=round(outUtilization,2)
| summarize InUtilization=avg(intUtilization), OutUtilization=avg(outUtilization) by bin(TIMESTAMP, 1m), link=tolower(link)
| join kind=leftouter SPANToLinks on $left.link == $right.link
| project TIMESTAMP, Link=strcat(SolutionId, ": ", link), InUtilization, OutUtilization
| render timechart
```

### IDF4: T2 - AZNG - Utilization

```kql
let starttime = _startTime;
let endtime = _endTime;
let Regionss = Regionn;
let Datacname = DCName;
let dd=cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where NgsDeviceType has_any ('RegionalHub','SpineRouter', 'AZNGHub', 'RegionalAggregator','RegionalShim') 
| where Regions in (Regionss)
| where DeviceName contains Datacname
| distinct toupper(DeviceName);
let SPANToLinks=cluster('waneng.westus2.kusto.windows.net').database('waneng').GetAllOpticalLinks
| where DeviceA in (dd) 
| where DeviceZ contains "ah"
| distinct SolutionId, link=tolower(strcat(DeviceA,"----",DeviceZ));
let IDF4=cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where NgsDeviceType has_any ('RegionalHub','SpineRouter', 'AZNGHub', 'RegionalAggregator','RegionalShim') 
| where NgsDeviceType == "SpineRouter"
| where Regions in (Regionss)
| where DeviceName contains Datacname
| extend IDF4=tostring(split(DeviceName, "-")[2])
| where IDF4 contains "4"
| distinct DeviceName = tolower(DeviceName);
cluster('azphynet.kusto.windows.net').database('azdhmds').InterfaceData 
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where deviceHostName in (IDF4)
| where ifAlias contains "AHZ" or ifAlias contains "AHY"
| extend outUtilization = (ifHCOutOctetsDiff*8.0)/(interval * ifHighSpeed * 1000.00)*100 
| extend intUtilization = (ifHCInOctetsDiff*8.0)/(interval * ifHighSpeed * 1000.00)*100 
| project TIMESTAMP,deviceHostName, ifName,outUtilization, intUtilization, ifHCOutOctetsDiff, ifHCInOctetsDiff, ifHighSpeed, interval, ifAlias
| project TIMESTAMP=bin(TIMESTAMP,3m), link=strcat(deviceHostName, "----", tostring(split(ifAlias, ":")[0])), intUtilization=round(intUtilization,2), outUtilization=round(outUtilization,2)
| summarize InUtilization=avg(intUtilization), OutUtilization=avg(outUtilization) by bin(TIMESTAMP, 1m), link=tolower(link)
| join kind=leftouter SPANToLinks on $left.link == $right.link
| project TIMESTAMP, Link=strcat(SolutionId, ": ", link), InUtilization, OutUtilization
| render timechart
```

### IDF1: T2- AZNG  - Discard and Error

```kql
let starttime = _startTime;
let endtime = _endTime;
let Regionss = Regionn;
let Datacname = DCName;
let IDF1=cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where NgsDeviceType has_any ('RegionalHub','SpineRouter', 'AZNGHub', 'RegionalAggregator','RegionalShim') 
| where NgsDeviceType == "SpineRouter"
| where Regions in (Regionss)
| where DeviceName contains Datacname
| extend IDF1=tostring(split(DeviceName, "-")[2])
| where IDF1 contains "1"
| distinct DeviceName = tolower(DeviceName);
cluster('azphynet.kusto.windows.net').database('azdhmds').InterfaceData 
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where deviceHostName in (IDF1)
| where ifAlias contains "AHZ" or ifAlias contains "AHY"
| project PreciseTimeStamp, deviceHostName, ifName, ifAlias, ifType,link=strcat(deviceHostName, "----", tostring(split(ifAlias, ":")[0])), ifOperStatus, InPacketDiscardPerFiveMinutes=ifInDiscardsDiff, OutPacketDiscardPerFiveMinutes=ifOutDiscardsDiff,InPacketErrorPerFiveMinutes=ifInErrorsDiff, OutPacketErrorPerFiveMinutes=ifOutErrorsDiff
| summarize InPacketErrorPerFiveMinutes=sum(InPacketErrorPerFiveMinutes), OutPacketErrorPerFiveMinutes=sum(OutPacketErrorPerFiveMinutes),InPacketDiscardPerFiveMinutes=sum(InPacketDiscardPerFiveMinutes),  OutPacketDiscardPerFiveMinutes=sum(OutPacketDiscardPerFiveMinutes) by bin(PreciseTimeStamp, 2m), link
| render timechart
```

### IDF2: T2 - AZNG  - Discard and Error

```kql
let starttime = _startTime;
let endtime = _endTime;
let Regionss = Regionn;
let Datacname = DCName;
let IDF2=cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where NgsDeviceType has_any ('RegionalHub','SpineRouter', 'AZNGHub', 'RegionalAggregator','RegionalShim') 
| where NgsDeviceType == "SpineRouter"
| where Regions in (Regionss)
| where DeviceName contains Datacname
| extend IDF2=tostring(split(DeviceName, "-")[2])
| where IDF2 contains "2"
| distinct DeviceName = tolower(DeviceName);
cluster('azphynet.kusto.windows.net').database('azdhmds').InterfaceData 
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where deviceHostName in (IDF2)
| where ifAlias contains "AHZ" or ifAlias contains "AHY"
| project PreciseTimeStamp, deviceHostName, ifName, ifAlias, ifType,link=strcat(deviceHostName, "----", tostring(split(ifAlias, ":")[0])), ifOperStatus, InPacketDiscardPerFiveMinutes=ifInDiscardsDiff, OutPacketDiscardPerFiveMinutes=ifOutDiscardsDiff,InPacketErrorPerFiveMinutes=ifInErrorsDiff, OutPacketErrorPerFiveMinutes=ifOutErrorsDiff
| summarize InPacketErrorPerFiveMinutes=sum(InPacketErrorPerFiveMinutes), OutPacketErrorPerFiveMinutes=sum(OutPacketErrorPerFiveMinutes),InPacketDiscardPerFiveMinutes=sum(InPacketDiscardPerFiveMinutes),  OutPacketDiscardPerFiveMinutes=sum(OutPacketDiscardPerFiveMinutes) by bin(PreciseTimeStamp, 2m), link
| render timechart
```

### IDF3: T2 - AZNG - Discard and Error

```kql
let starttime = _startTime;
let endtime = _endTime;
let Regionss = Regionn;
let Datacname = DCName;
let IDF3=cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where NgsDeviceType has_any ('RegionalHub','SpineRouter', 'AZNGHub', 'RegionalAggregator','RegionalShim') 
| where NgsDeviceType == "SpineRouter"
| where Regions in (Regionss)
| where DeviceName contains Datacname
| extend IDF3=tostring(split(DeviceName, "-")[2])
| where IDF3 contains "3"
| distinct DeviceName = tolower(DeviceName);
cluster('azphynet.kusto.windows.net').database('azdhmds').InterfaceData 
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where deviceHostName in (IDF3)
| where ifAlias contains "AHZ" or ifAlias contains "AHY"
| project PreciseTimeStamp, deviceHostName, ifName, ifAlias, ifType,link=strcat(deviceHostName, "----", tostring(split(ifAlias, ":")[0])), ifOperStatus, InPacketDiscardPerFiveMinutes=ifInDiscardsDiff, OutPacketDiscardPerFiveMinutes=ifOutDiscardsDiff,InPacketErrorPerFiveMinutes=ifInErrorsDiff, OutPacketErrorPerFiveMinutes=ifOutErrorsDiff
| summarize InPacketErrorPerFiveMinutes=sum(InPacketErrorPerFiveMinutes), OutPacketErrorPerFiveMinutes=sum(OutPacketErrorPerFiveMinutes),InPacketDiscardPerFiveMinutes=sum(InPacketDiscardPerFiveMinutes),  OutPacketDiscardPerFiveMinutes=sum(OutPacketDiscardPerFiveMinutes) by bin(PreciseTimeStamp, 2m), link
| render timechart
```

### IDF4: T2 - AZNG - Discard and Error

```kql
let starttime = _startTime;
let endtime = _endTime;
let Regionss = Regionn;
let Datacname = DCName;
let IDF4=cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where NgsDeviceType has_any ('RegionalHub','SpineRouter', 'AZNGHub', 'RegionalAggregator','RegionalShim') 
| where NgsDeviceType == "SpineRouter"
| where Regions in (Regionss)
| where DeviceName contains Datacname
| extend IDF4=tostring(split(DeviceName, "-")[2])
| where IDF4 contains "4"
| distinct DeviceName = tolower(DeviceName);
cluster('azphynet.kusto.windows.net').database('azdhmds').InterfaceData 
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where deviceHostName in (IDF4)
| where ifAlias contains "AHZ" or ifAlias contains "AHY"
| project PreciseTimeStamp, deviceHostName, ifName, ifAlias, ifType,link=strcat(deviceHostName, "----", tostring(split(ifAlias, ":")[0])), ifOperStatus, InPacketDiscardPerFiveMinutes=ifInDiscardsDiff, OutPacketDiscardPerFiveMinutes=ifOutDiscardsDiff,InPacketErrorPerFiveMinutes=ifInErrorsDiff, OutPacketErrorPerFiveMinutes=ifOutErrorsDiff
| summarize InPacketErrorPerFiveMinutes=sum(InPacketErrorPerFiveMinutes), OutPacketErrorPerFiveMinutes=sum(OutPacketErrorPerFiveMinutes),InPacketDiscardPerFiveMinutes=sum(InPacketDiscardPerFiveMinutes),  OutPacketDiscardPerFiveMinutes=sum(OutPacketDiscardPerFiveMinutes) by bin(PreciseTimeStamp, 2m), link
| render timechart
```

### PV

```kql
let pv=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('kusto').adxpageview| where page contains "b01/phynett2";
let pvcount=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('microsoft').adxpageview | where page contains "b01/phynett2" | summarize count();
union pv, pvcount
```

### SPAN Mapping: T2 - AZNG

```kql
let starttime = _startTime;
let endtime = _endTime;
let Regionss = Regionn;
let Datacname = DCName;
let dd=cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceStatic 
| where NgsDeviceType has_any ('RegionalHub','SpineRouter', 'AZNGHub', 'RegionalAggregator','RegionalShim') 
| where Regions in (Regionss)
| where DeviceName contains Datacname
| distinct toupper(DeviceName);
cluster('waneng.westus2.kusto.windows.net').database('waneng').GetAllOpticalLinks
| where DeviceA in (dd) 
| where DeviceZ contains "ah"
| project SolutionId, DeviceA, DeviceZ, OpticalDeviceA, OpticalDeviceZ, PortA,PortZ, SpanType
| order  by DeviceA asc 
```

### AZ-DC Mapping

```kql
let starttime = _startTime;
let endtime = _endTime;
let Regionss = Regionn;
cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where TIMESTAMP > starttime - 1h and TIMESTAMP < endtime
| where Region in (Regionss)
| distinct AvailabilityZone, DataCenterName
| summarize DataCenterName=make_list(DataCenterName) by AvailabilityZone
```

## PhyNet Link

### Related IcM for Device

```kql
cluster('azwan').database('Swan').f_GetHistoricIncidents(['_startTime'], ['_endTime'],  "*")
| where OccurringDeviceName == tolower(_DeviceName) or OccurringDeviceName == EndDevicess or Title contains EndDevicess or Title contains _DeviceName
| extend IcMLink=strcat("https://portal.microsofticm.com/imp/v3/incidents/details/", IncidentId, "/home")
| project IncidentId, OccurringDeviceName, CreateDate, Severity, Status, OwningTeamName, Title,ParentIncidentId, ChildCount, IcMLink
```

### Device Meta Data

```kql
let devicename = tolower(_DeviceName);
cluster("Azphynet").database("azdhmds").DeviceStatic
| where DeviceName == devicename
| join cluster("Azphynet").database("azdhmds").DeviceMetadata on DeviceName
| project DeviceName, Region=Regions, Datacenter, DcCode, Cluster,NgsDeviceType,StaticIP, LoopbackV6, ManagementIP, ManagementV6, PreferredIP, HardwareSku, Slices, AzureDeviceType, CloudType,DeploymentType, Status, OSVersion, Location, Role,FirmwareProfile, SerialNumber,ASN, Vender, LocationType=strcat(toupper(LocationType), LocationIndex), DeviceSkuExt
| evaluate narrow()
| project Key=Column, Value
```

### If the Device State Change

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let devicename = toupper(_DeviceName);
cluster('azphynet').database('azphynetmds').DeviceLifecycleStateChange()
|  where TIMESTAMP> starttime and TIMESTAMP < endtime
| where DeviceName == devicename or DeviceName == toupper(EndDevicess)
```

### AAA Log

```kql
let starttime= _startTime;
let endtime = _endTime;
cluster('phynetval').database('aznwmds').AzureAaaMasterSessions
| where TIMESTAMP >= starttime and TIMESTAMP<=endtime
| where deviceName == tolower(_DeviceName)
| where command != ""
| where command !startswith "terminal "
| where command !startswith "show "
| where command !startswith "exit "
| where command !startswith "end "
| project PreciseTimeStamp, deviceName, user, command
```

### Optical Link Information for Device if Optical Device involves

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let devicename = toupper(_DeviceName);
let ed= toupper(EndDevicess);
cluster('waneng.westus2.kusto.windows.net').database('waneng').GetAllOpticalLinks
| where DeviceA == devicename or DeviceZ == devicename
| where DeviceA == ed or DeviceZ == ed
| distinct OpticalDeviceA, OpticalDeviceZ, DeviceA, DeviceZ, SolutionId
```

### CPU Utilization

```kql
let starttime= _startTime;
let endtime = _endTime;
cluster('azphynet.kusto.windows.net').database('azdhmds').DevicePerformanceCounters
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where deviceName == tolower(_DeviceName)
| project PreciseTimeStamp, deviceName, cpu5Sec, cpu1Min, cpu5Min
| render timechart 

```

### Memory Utilization

```kql
let starttime= _startTime;
let endtime = _endTime;
cluster('azphynet.kusto.windows.net').database('azdhmds').DevicePerformanceCounters
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where deviceName == tolower(_DeviceName)
| project PreciseTimeStamp, deviceName, UsedMemory=usedMemory/1000000000, AvailableMemory=(totalMemory - usedMemory)/1000000000, TotalMemoy=totalMemory/1000000000
| render timechart 

```

### Interface Status

```kql
let starttime= _startTime;
let endtime = _endTime;
let ed = EndDevicess;
let rightsp=toscalar(cluster('Aznwcc').database('aznwmds').DeviceInterfaceLinks
| where StartDevice == tolower(_DeviceName)
| where EndDevice == ed
| where StartPort !contains "Management"
| where StartPort !contains "console"
| distinct Port=StartPort);
let reversesp=toscalar(cluster('Aznwcc').database('aznwmds').DeviceInterfaceLinks
| where EndDevice == tolower(_DeviceName)
| where StartPort !contains "Management"
| where StartPort !contains "console"
| where StartDevice == ed
| distinct Port=EndPort);
let ddinterface=iff(_DeviceName contains "rh", reversesp,rightsp);
cluster('Aznwnetmon').database('aznwmds').sXInterfaceTable 
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where DeviceName ==  tolower(_DeviceName)
| extend ToDevice=tostring(split(ifAlias, ":")[0])
| where ifName in~ (ddinterface)
| extend inUtilization = (ifHCInOctets_Counter*8.0)/(Interval * ifHighSpeed * 1000000.00)*100.00
| extend outUtilization = (ifHCOutOctets_Counter*8.0)/(Interval * ifHighSpeed * 1000000.00)*100.00
| extend Interface=tostring(strcat(DeviceName, ":", ifName))
| summarize inUtilization = avg(inUtilization),outUtilization=avg(outUtilization),InDiscard=sum(ifInDiscards_Counter), OutDiscard=sum(ifOutDiscards_Counter), InError=sum(ifInErrors_Counter), OutError=sum(ifOutErrors_Counter) by bin(PreciseTimeStamp,5m), Interface
| render timechart
```

### Device History Configuration

```kql
let starttime= _startTime;
let endtime = _endTime;
cluster('Aznwcc').database('aznwmds').DeviceConfigData
| where Timestamp >= starttime - 1d and Timestamp <= endtime
| where Hostname == tolower(_DeviceName)
| project Timestamp,Device=Hostname, ConfigType, Config
```

### Link Configuration

```kql
let ed = EndDevicess;
cluster('Aznwcc').database('aznwmds').DeviceInterfaceLinks
| where StartDevice == tolower(_DeviceName) or EndDevice == tolower(_DeviceName)
| where StartPort !contains "Management"
| where StartPort !contains "console"
| where * contains ed
| project StartDevice, EndDevice,StartPortChannel,EndPortChannel, StartPort,EndPort,StartBGPV4Peer, EndBGPV4Peer,StartBGPV6Peer, EndBGPV6Peer
| evaluate narrow()
| project Key=Column, Value

```

### Interface Status

```kql
let starttime= _startTime;
let endtime = _endTime;
let ed = EndDevicess;
let rightsp=toscalar(cluster('Aznwcc').database('aznwmds').DeviceInterfaceLinks
| where StartDevice == tolower(ed)
| where EndDevice == _DeviceName
| where StartPort !contains "Management"
| where StartPort !contains "console"
| distinct Port=StartPort);
let reversesp=toscalar(cluster('Aznwcc').database('aznwmds').DeviceInterfaceLinks
| where StartDevice == tolower(_DeviceName)
| where EndDevice == ed
| where StartPort !contains "Management"
| where StartPort !contains "console"
| distinct Port=EndPort);
let ddinterface=iff(ed contains "rh",reversesp, rightsp);
cluster('Aznwnetmon').database('aznwmds').sXInterfaceTable 
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where DeviceName == ed
| extend ToDevice=tostring(split(ifAlias, ":")[0])
| where ifName in~ (ddinterface)
| extend inUtilization = (ifHCInOctets_Counter*8.0)/(Interval * ifHighSpeed * 1000000.00)*100.00
| extend outUtilization = (ifHCOutOctets_Counter*8.0)/(Interval * ifHighSpeed * 1000000.00)*100.00
| extend Interface=tostring(strcat(DeviceName, ":", ifName))
| summarize inUtilization = avg(inUtilization),outUtilization=avg(outUtilization),InDiscard=sum(ifInDiscards_Counter), OutDiscard=sum(ifOutDiscards_Counter), InError=sum(ifInErrors_Counter), OutError=sum(ifOutErrors_Counter) by bin(PreciseTimeStamp,5m), Interface
| render timechart
```

### BGP Event

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let ed = EndDevicess;
let EBGPPeerv4=toscalar(cluster('Aznwcc').database('aznwmds').DeviceInterfaceLinks
| where StartDevice == tolower(_DeviceName) and EndDevice  == ed
| where StartPort !contains "Management"
| where StartPort !contains "console"
| where * contains ed
| project EndBGPV4Peer);
let EBGPPeerv6=toscalar(cluster('Aznwcc').database('aznwmds').DeviceInterfaceLinks
| where StartDevice == tolower(_DeviceName) and EndDevice  == ed
| where StartPort !contains "Management"
| where StartPort !contains "console"
| where * contains ed
| project EndBGPV6Peer);
cluster('azphynet.kusto.windows.net').database('azdhmds').SyslogData
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where Device == tolower(_DeviceName)
| where EventName contains "BGP"
//| extend Message=iff(Message contains "T2", split(Message, "%")[1], Message)
| extend Message=split(Message, "%")[1]
| where Message contains EBGPPeerv4 or Message contains EBGPPeerv6
| project PreciseTimeStamp,Message
```

### BGP Event

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let ed = EndDevicess;
let SBGPPeerv4=toscalar(cluster('Aznwcc').database('aznwmds').DeviceInterfaceLinks
| where StartDevice == tolower(_DeviceName) and EndDevice  == ed
| where StartPort !contains "Management"
| where StartPort !contains "console"
| project StartBGPV4Peer);
let SBGPPeerv6=toscalar(cluster('Aznwcc').database('aznwmds').DeviceInterfaceLinks
| where StartDevice == tolower(_DeviceName) and EndDevice  == ed
| where StartPort !contains "Management"
| where StartPort !contains "console"
| project StartBGPV6Peer);
cluster('azphynet.kusto.windows.net').database('azdhmds').SyslogData
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where Device == ed
| where EventName contains "BGP"
| extend Message=split(Message, "%")[1]
| where Message contains SBGPPeerv4 or Message contains SBGPPeerv6
| project PreciseTimeStamp,Message
```

### Device Meta Data

```kql
let devicename = tolower(_DeviceName);
cluster("Azphynet").database("azdhmds").DeviceStatic
| where DeviceName == EndDevicess
| join cluster("Azphynet").database("azdhmds").DeviceMetadata on DeviceName
| project DeviceName, Region=Regions, Datacenter, DcCode, Cluster,NgsDeviceType,StaticIP, LoopbackV6, ManagementIP, ManagementV6, PreferredIP, HardwareSku, Slices, AzureDeviceType, CloudType,DeploymentType, Status, OSVersion, Location, Role,FirmwareProfile, SerialNumber,ASN, Vender, LocationType=strcat(toupper(LocationType), LocationIndex), DeviceSkuExt
| evaluate narrow()
| project Key=Column, Value
```

### CPU Utilization

```kql
let starttime= _startTime;
let endtime = _endTime;
cluster('azphynet.kusto.windows.net').database('azdhmds').DevicePerformanceCounters
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where deviceName == tolower(EndDevicess)
| project PreciseTimeStamp, deviceName, cpu5Sec, cpu1Min, cpu5Min
| render timechart 

```

### Memory Utilization

```kql
let starttime= _startTime;
let endtime = _endTime;
cluster('azphynet.kusto.windows.net').database('azdhmds').DevicePerformanceCounters
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where deviceName == tolower(EndDevicess)
| project PreciseTimeStamp, deviceName, UsedMemory=usedMemory/1000000000, AvailableMemory=(totalMemory - usedMemory)/1000000000, TotalMemoy=totalMemory/1000000000
| render timechart 

```

### AAA Log

```kql
let starttime= _startTime;
let endtime = _endTime;
cluster('phynetval').database('aznwmds').AzureAaaMasterSessions
| where TIMESTAMP >= starttime and TIMESTAMP<=endtime
| where deviceName == EndDevicess
| where command != ""
| where command !startswith "terminal "
| where command !startswith "show "
| where command !startswith "exit "
| where command !startswith "end "
| project PreciseTimeStamp, deviceName, user, command
```

### Device History Configuration

```kql
let starttime= _startTime;
let endtime = _endTime;
cluster('Aznwcc').database('aznwmds').DeviceConfigData
| where Timestamp >= starttime - 1d and Timestamp <= endtime
| where Hostname in (EndDevicess)
| project Timestamp,Device=Hostname, ConfigType, Config
```

### Link Event

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let ed = EndDevicess;
let SPort=toscalar(cluster('Aznwcc').database('aznwmds').DeviceInterfaceLinks
| where StartDevice == tolower(_DeviceName) and EndDevice  == ed
| where StartPort !contains "Management"
| where StartPort !contains "console"
| where * contains ed
| project StartPort);
let SPortChannel=toscalar(cluster('Aznwcc').database('aznwmds').DeviceInterfaceLinks
| where StartDevice == tolower(_DeviceName) and EndDevice  == ed
| where StartPort !contains "Management"
| where StartPort !contains "console"
| where * contains ed
| project StartPortChannel);
cluster('azphynet.kusto.windows.net').database('azdhmds').SyslogData
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where Device == tolower(_DeviceName)
| where Message contains SPort or Message contains SPortChannel
| extend Message=split(Message, "%")[1]
| project PreciseTimeStamp,Message
```

### Link Event

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let ed = EndDevicess;
let EPort=toscalar(cluster('Aznwcc').database('aznwmds').DeviceInterfaceLinks
| where StartDevice == tolower(_DeviceName) and EndDevice  == ed
| where StartPort !contains "Management"
| where StartPort !contains "console"
| project EndPort);
let EPortChannel=toscalar(cluster('Aznwcc').database('aznwmds').DeviceInterfaceLinks
| where StartDevice == tolower(_DeviceName) and EndDevice  == ed
| where StartPort !contains "Management"
| where StartPort !contains "console"
| project EndPortChannel);
cluster('azphynet.kusto.windows.net').database('azdhmds').SyslogData
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where Device == ed
| where Message contains EPort or Message contains EPortChannel
| extend Message=split(Message, "%")[1]
| project PreciseTimeStamp,Message
```

### Interface Bandwidth Status between DeviceName and the DC of EndDevice

```kql
let starttime= _startTime;
let endtime = _endTime;
let devicename = tolower(_DeviceName);
let ed = EndDevicess;
let rightdirect=toscalar(cluster('Aznwcc').database('aznwmds').DeviceInterfaceLinks
| where StartDevice == tolower(_DeviceName)
| where EndDevice == ed
| distinct DC=tostring(split(EndDevice, "-")[0]));
let reversedirect=toscalar(cluster('Aznwcc').database('aznwmds').DeviceInterfaceLinks
| where StartDevice == ed
| where EndDevice == tolower(_DeviceName)
| distinct DC=tostring(split(StartDevice,"-")[0]));
let DCCode=iff(isnotempty(rightdirect), rightdirect,reversedirect);
cluster('azphynet').database('azdhmds'). InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName == devicename
| where ifAlias contains DCCode
| project PreciseTimeStamp, deviceHostName, ifName, Pair=strcat(deviceHostName, "---->", tostring(split(ifAlias, ":")[0])), ifOperStatus, AverageInBandwidthGbps=round((ifHCInOctetsDiff * 8.0 / (interval / 1e3))/(1e9),2), AverageOutBandwithGbps=round((ifHCOutOctetsDiff * 8.0 / (interval / 1e3))/(1e9),2)
| summarize AverageInBandwidthGbps=sum(AverageInBandwidthGbps), AverageOutBandwithGbps=sum(AverageOutBandwithGbps) by bin(PreciseTimeStamp, 2m), Pair
| render timechart

```

### Interface Abnormal Counter between DeviceName and the DC of EndDevice

```kql
let starttime= _startTime;
let endtime = _endTime;
let devicename = tolower(_DeviceName);
let ed = EndDevicess;
let rightdirect=toscalar(cluster('Aznwcc').database('aznwmds').DeviceInterfaceLinks
| where StartDevice == tolower(_DeviceName)
| where EndDevice == ed
| distinct DC=tostring(split(EndDevice, "-")[0]));
let reversedirect=toscalar(cluster('Aznwcc').database('aznwmds').DeviceInterfaceLinks
| where StartDevice == ed
| where EndDevice == tolower(_DeviceName)
| distinct DC=tostring(split(StartDevice,"-")[0]));
let DCCode=iff(isnotempty(rightdirect), rightdirect,reversedirect);
cluster('azphynet').database('azdhmds'). InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName == devicename
| where ifAlias contains DCCode
| project PreciseTimeStamp, deviceHostName, ifName, Pair=strcat(deviceHostName, "---->", tostring(split(ifAlias, ":")[0])), ifType, ifOperStatus, InPacketDiscardPerFiveMinutes=ifInDiscardsDiff, OutPacketDiscardPerFiveMinutes=ifOutDiscardsDiff,InPacketErrorPerFiveMinutes=ifInErrorsDiff, OutPacketErrorPerFiveMinutes=ifOutErrorsDiff
| summarize InPacketDiscardPerFiveMinutes=sum(InPacketDiscardPerFiveMinutes),  OutPacketDiscardPerFiveMinutes=sum(OutPacketDiscardPerFiveMinutes),InPacketErrorPerFiveMinutes=sum(InPacketErrorPerFiveMinutes), OutPacketErrorPerFiveMinutes=sum(OutPacketErrorPerFiveMinutes) by bin(PreciseTimeStamp, 2m), Pair
| render timechart

```

### Interface Bandwidth Status between EndDeivce and the DC of DeviceName

```kql
let starttime= _startTime;
let endtime = _endTime;
let devicename = tolower(_DeviceName);
let ed = EndDevicess;
let rightdirect=toscalar(cluster('Aznwcc').database('aznwmds').DeviceInterfaceLinks
| where StartDevice == tolower(_DeviceName)
| where EndDevice == ed
| distinct DC=tostring(split(StartDevice, "-")[0]));
let reversedirect=toscalar(cluster('Aznwcc').database('aznwmds').DeviceInterfaceLinks
| where StartDevice == ed
| where EndDevice == tolower(_DeviceName)
| distinct DC=tostring(split(EndDevice,"-")[0]));
let DCCode=iff(isnotempty(rightdirect), rightdirect,reversedirect);
cluster('azphynet').database('azdhmds'). InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName == ed
| where ifAlias contains DCCode
| project PreciseTimeStamp, deviceHostName, ifName, Pair=strcat(deviceHostName, "---->", tostring(split(ifAlias, ":")[0])), ifOperStatus, AverageInBandwidthGbps=round((ifHCInOctetsDiff * 8.0 / (interval / 1e3))/(1e9),2), AverageOutBandwithGbps=round((ifHCOutOctetsDiff * 8.0 / (interval / 1e3))/(1e9),2)
| summarize AverageInBandwidthGbps=sum(AverageInBandwidthGbps), AverageOutBandwithGbps=sum(AverageOutBandwithGbps) by bin(PreciseTimeStamp, 2m), Pair
| render timechart

```

### Interface Abnormal Counter between EndDeivce and the DC of DeviceName

```kql
let starttime= _startTime;
let endtime = _endTime;
let devicename = tolower(_DeviceName);
let ed = EndDevicess;
let rightdirect=toscalar(cluster('Aznwcc').database('aznwmds').DeviceInterfaceLinks
| where StartDevice == tolower(_DeviceName)
| where EndDevice == ed
| distinct DC=tostring(split(StartDevice, "-")[0]));
let reversedirect=toscalar(cluster('Aznwcc').database('aznwmds').DeviceInterfaceLinks
| where StartDevice == ed
| where EndDevice == tolower(_DeviceName)
| distinct DC=tostring(split(EndDevice,"-")[0]));
let DCCode=iff(isnotempty(rightdirect), rightdirect,reversedirect);
cluster('azphynet').database('azdhmds'). InterfaceData
| where PreciseTimeStamp >= starttime  and PreciseTimeStamp <= endtime
| where deviceHostName == ed
| where ifAlias contains DCCode
| project PreciseTimeStamp, deviceHostName, ifName, Pair=strcat(deviceHostName, "---->", tostring(split(ifAlias, ":")[0])), ifType, ifOperStatus, InPacketDiscardPerFiveMinutes=ifInDiscardsDiff, OutPacketDiscardPerFiveMinutes=ifOutDiscardsDiff,InPacketErrorPerFiveMinutes=ifInErrorsDiff, OutPacketErrorPerFiveMinutes=ifOutErrorsDiff
| summarize InPacketDiscardPerFiveMinutes=sum(InPacketDiscardPerFiveMinutes),  OutPacketDiscardPerFiveMinutes=sum(OutPacketDiscardPerFiveMinutes),InPacketErrorPerFiveMinutes=sum(InPacketErrorPerFiveMinutes), OutPacketErrorPerFiveMinutes=sum(OutPacketErrorPerFiveMinutes) by bin(PreciseTimeStamp, 2m), Pair
| render timechart
```

### PV

```kql
let pv=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('kusto').adxpageview| where page contains "b01/phynetlinks";
let pvcount=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('microsoft').adxpageview | where page contains "b01/phynetlinks" | summarize count();
union pv, pvcount
```

