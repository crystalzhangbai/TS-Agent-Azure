---
description: KQL queries for Azure network device inventory, health status, OS versions, hardware model.
---

# Network Device Kusto Queries

> Source: Azure Networking B01 Dashboard (aka.ms/b01)
> Pages: Network Device

## Network Device

### Syslog without any Filter

```kql
let starttime= _startTime;
let endtime = _endTime;
cluster('azphynet.kusto.windows.net').database('azdhmds').SyslogData
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where Device == tolower(_DeviceName)
| where Message contains SyslogFilter
| project PreciseTimeStamp, Device, EventName,Message, Severity
```

### AAA Log

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
cluster('phynetval').database('aznwmds').AzureAaaMasterSessions
| where TIMESTAMP >= starttime and TIMESTAMP<=endtime
| where deviceName == tolower(_DeviceName)
| where command != ""
| project PreciseTimeStamp, deviceName, user, command
```

### Line Protocol(Layer 2) Down Count between this Device and its Peer

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
cluster('azphynet.kusto.windows.net').database('azdhmds').SyslogData
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where Device == _DeviceName
| where EventName contains "DOWN"
| project PreciseTimeStamp, Device, Severity, FacilityMessage, EventName,Message
| summarize count() by EventName, bin(PreciseTimeStamp, 1m)
| project PreciseTimeStamp, EventName, count=count_
| render columnchart  
//cluster('azphynet.kusto.windows.net').database('azdhmds').SyslogData
//| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
//| where Device == _DeviceName
//| where EventName contains "LINEPROTO-5-UPDOWN"
//| where Message contains "changed state to down"
//| project PreciseTimeStamp, Device, Severity, FacilityMessage, EventName,Message
//| extend ToDevice = tostring(split(extract(@"\(([^)]+)\)", 1, Message), ":")[0])
//| extend DC = tostring(split(ToDevice, "-")[0])
//| project PreciseTimeStamp, Device, ToDC=DC, ToDevice
//| summarize count() by bin(PreciseTimeStamp, 5m)
//| render columnchart  

```

### MACSEC related Events Counter

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
cluster('azphynet.kusto.windows.net').database('azdhmds').SyslogData
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where Device == _DeviceName
| where EventName contains "MKA"
| project PreciseTimeStamp, Device, Severity, FacilityMessage, EventName,Message
| extend ToDevice = tostring(split(extract(@"\(([^)]+)\)", 1, Message), ":")[0])
| extend DC = tostring(split(ToDevice, "-")[0])
| project PreciseTimeStamp, Device, ToDC=DC, ToDevice
| summarize count() by bin(PreciseTimeStamp, 5m)
| render columnchart  
```

### CPU Utilization

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
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
let subscriptionid = SubscriptionID;
cluster('azphynet.kusto.windows.net').database('azdhmds').DevicePerformanceCounters
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where deviceName == tolower(_DeviceName)
| project PreciseTimeStamp, deviceName, UsedMemory=usedMemory/1000000000, AvailableMemory=(totalMemory - usedMemory)/1000000000, TotalMemoy=totalMemory/1000000000
| render timechart 

```

### Device Interface Discard/Error Counter

```kql
let starttime= _startTime;
let endtime = _endTime;
cluster('Aznwnetmon').database('aznwmds').sXInterfaceTable 
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where DeviceName == tolower(_DeviceName)
| project ReceivedUtc, DeviceName,ifInDiscards_Counter, ifOutDiscards_Counter, ifInErrors_Counter, ifOutErrors_Counter
| summarize InDiscard=sum(ifInDiscards_Counter), OutDiscard=sum(ifOutDiscards_Counter), InError=sum(ifInErrors_Counter), OutError=sum(ifOutErrors_Counter) by bin(ReceivedUtc, 1m), DeviceName
| render columnchart  


```

### If the Device State Change

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let devicename = toupper(_DeviceName);
cluster('azphynet.kusto.windows.net').database('azphynetmds').DeviceLifecycleStateChange()
|  where TIMESTAMP> starttime - 1d and TIMESTAMP < endtime + 1d
| where DeviceName == devicename
```

### Device Bundle Interface Utilization in %

```kql
let starttime= _startTime;
let endtime = _endTime;
cluster('Aznwnetmon').database('aznwmds').sXInterfaceTable 
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where DeviceName ==  tolower(_DeviceName)
| extend ToDevice=tostring(split(ifAlias, ":")[0])
| where ifName contains "Bundle" or ifName  contains "channel" or ifName contains "ae"
| extend inUtilization = (ifHCInOctets_Counter*8.0)/(Interval * ifHighSpeed * 1000000.00)*100.00
| extend outUtilization = (ifHCOutOctets_Counter*8.0)/(Interval * ifHighSpeed * 1000000.00)*100.00
| summarize inUtilization = avg(inUtilization),outUtilization=avg(outUtilization) by bin(PreciseTimeStamp,1m), ifName
| render timechart    
```

### Syslog in Critical Level

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
cluster('azphynet.kusto.windows.net').database('azdhmds').SyslogData
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where Device == tolower(_DeviceName)
| where Message contains SyslogFilter
| where Severity == "Critical" or Severity == "Error"
//| extend Message = iff(_DeviceName !contains "t0", split(Message, "%")[1], split(Message, "T0")[1])
| project PreciseTimeStamp,Message, Severity
```

### Optical Link Information for Device if Optical Device involves

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let devicename = toupper(_DeviceName);
cluster('waneng.westus2.kusto.windows.net').database('waneng').GetAllOpticalLinks
| where DeviceA  == devicename or DeviceZ == devicename
| distinct OpticalDeviceA, OpticalDeviceZ, DeviceA, DeviceZ, SolutionId
```

### Device Meta Data

```kql
let devicename = tolower(_DeviceName);
let starttime = _startTime;
let endtime = _endTime;
let startunixtime = tolong(starttime-datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime-datetime(1970-01-01)) / 10000;
let wan=cluster("azwan").database("Swan").GetSwanDeviceMetadata() 
| where DeviceName  == devicename
| extend CoreTool=strcat("https://coretools.azurefd.net/#/device/home?target=",DeviceName,"&time=",startunixtime, "%252C", endunixtime, "&useUtc=true&renderType=chart&keywords=&searchContext=devices&summary=Device&linkDirection=forwardandreverse&interfaceType=portchannel&dataType=&domain=All&cloudType=Public")
| evaluate narrow()
| project Key=Column, Value;
let phynet=cluster("Azphynet").database("azdhmds").DeviceStatic
| where DeviceName == devicename
| join cluster("Azphynet").database("azdhmds").DeviceMetadata on DeviceName
| extend Coretool=strcat("https://coretools.azurefd.net/#/device/home?target=",DeviceName,"&time=",startunixtime, "%252C", endunixtime, "&useUtc=true&renderType=chart&keywords=&searchContext=devices&summary=Device&linkDirection=forwardandreverse&interfaceType=portchannel&dataType=&domain=All&cloudType=Public")
| project DeviceName, Coretool,Region=Regions, Datacenter, DcCode, Cluster,NgsDeviceType,StaticIP, LoopbackV6, ManagementIP, ManagementV6, PreferredIP, HardwareSku, Slices, AzureDeviceType, CloudType,DeploymentType, Status, OSVersion, Location, Role,FirmwareProfile, SerialNumber,ASN, Vender, LocationType=strcat(toupper(LocationType), LocationIndex), DeviceSkuExt
| evaluate narrow()
| project Key=Column, Value;
union wan, phynet


```

### Related IcM for Device

```kql
let starttime= _startTime - 1d;
let endtime = _endTime + 1d;
cluster('azwan').database('Swan').f_GetHistoricIncidents(starttime, endtime,  _DeviceName)
| where OccurringDeviceName == _DeviceName or Title contains _DeviceName 
| extend IcMLink=strcat("https://portal.microsofticm.com/imp/v3/incidents/details/", IncidentId, "/home")
| project IncidentId, OccurringDeviceName, CreateDate, Severity, Status, OwningTeamName, Title,ParentIncidentId, ChildCount, IcMLink
```

### Queue Drop Counter - WAN device only

```kql
let starttime= _startTime;
let endtime = _endTime;
union cluster("aznwwanhealthprod04").database('aznwmds').QosQueueStats
//| where ReceivedUtc > now(-1h) and ReceivedUtc < now()
| where ReceivedUtc > starttime and ReceivedUtc < endtime
| where DroppedPackets > 100
| where SrcInterfaceDescription !contains "MSEE to service"
| where SrcDeviceName == tolower(_DeviceName)
| project ReceivedUtc, Link=strcat(QoSQueueName, " drop----LinkId ", LinkId), DroppedPackets
| render columnchart
```

### Device History Configuration

```kql
let starttime= _startTime;
let endtime = _endTime;
cluster('Aznwcc').database('aznwmds').DeviceConfigData
| where Timestamp >= starttime - 2d and Timestamp <= endtime + 1d
| where Hostname == tolower(_DeviceName)
| project Timestamp,Device=Hostname, ConfigType, Config
```

### Device Interface Links

```kql
cluster('Aznwcc').database('aznwmds').DeviceInterfaceLinks
| where StartDevice == tolower(_DeviceName) or EndDevice  == tolower(_DeviceName)
| where * !contains "null"
| project StartDevice, EndDevice,StartPortChannel,EndPortChannel, StartPort,EndPort,StartBGPV4Peer, EndBGPV4Peer,StartBGPV6Peer, EndBGPV6Peer, BandwidthInGbps

```

### HardwareProxyDeviceLogs - Phynet device only

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
cluster('azphynet').database('DeviceAccess').HardwareProxyDeviceLogs
| where TIMESTAMP >= starttime and TIMESTAMP<=endtime
| where hostName == toupper(_DeviceName)
| where log contains SyslogFilter
| project PreciseTimeStamp, hostName, log
```

### Device Interface Name and Inst mapping

```kql
let devicename = tolower(_DeviceName);
cluster("netcapplan").database("NetCapPlan").RouterInterfaces
| where DeviceName  == devicename
| distinct  ifName, ifInst

```

### Device Status and Health

```kql
let devicename = todynamic(_DeviceName);
let starttime = _startTime;
let endtime = _endTime;
let startTime = bin(starttime, 5m);
                let endTime = datetime_add('minute', 5, bin(endtime, 5m));
                cluster("azphynet.kusto.windows.net").database('azdhmds').f_DeviceHealthLookupMultiSearch(startTime, endTime, devicename)
                | order by TIMESTAMP asc
```

### PV

```kql
let pv=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('kusto').adxpageview| where page contains "b01/networkdevice";
let pvcount=cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('microsoft').adxpageview | where page contains "b01/networkdevice" | summarize count();
union pv, pvcount
```

### TOR Maintenance Notification Service(TINS) Log

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let devicename = toupper(_DeviceName);
cluster('azwan.kusto.windows.net').database('FUSE').TinsRequestState
| where Timestamp >= starttime - 14d and Timestamp <= endtime + 14d
| where Device =~ devicename
| project Timestamp, Requestor,TorIsolationNotificationRequestId, RequestTime, PreviousRequestState, CurrentRequestState,  Message
```

### VM List under the TOR

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let devicename = toupper(_DeviceName);
let nid= cluster('azphynet.kusto.windows.net').database('azdhmds').DeviceInterfaceLinks
| where LinkType =~ 'DeviceInterfaceLink' and EndDevice =~ devicename
| summarize by DeviceName = StartDevice
| join cluster('aznwcc').database('aznwmds').Servers on $left.DeviceName == $right.DeviceName
| distinct NodeId;
cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= starttime - 5h and PreciseTimeStamp <= endtime + 5h
| where nodeId in~ (nid)
| extend SKU=tostring(split(billingType, "|")[1])
| distinct  roleInstanceName,subscriptionId, containerId, nodeId, SKU, AvailabilityZone, availabilitySetName
| extend VMdash=strcat("https://web.kusto.windows.net/dashboards/f9ee36ad-73f0-4ae6-b752-f8be89e9245c?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH:mm:ss'),"Z&p-_endTime=",format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime,'HH:mm:ss'),"Z&p-SubIdOrContainerId=v-",containerId,"&&p-VMName=v-ContaizerId&p-DataPathScan=v-No#8ed1e2a2-d979-401b-9609-7580ad07ccd1")
| extend NodeDash=strcat("https://aka.ms/b01?p-_startTime=",format_datetime(starttime, 'yyyy-MM-dd'), "T", format_datetime(starttime,'HH-mm-ss'),"Z&p-_endTime=", format_datetime(endtime,'yyyy-MM-dd'), "T", format_datetime(endtime, 'HH-mm-ss'), "Z&p-nodeid=v-", nodeId, "#805057f2-367d-4cb7-9986-89fbd2533f94")
```

### [ WAN Device Only ] - Moby Availability Ratio - From Other WAN devices to the $DeviceName

```kql
let starttime= _startTime;
let endtime = _endTime;
cluster('waneng.westus2').database('waneng').f_GetMobyRawData(_DeviceName, false,starttime,endtime)
| summarize avg(Average) by bin(TimestampUtc, 1m)
| render timechart
```

### [ WAN Device Only ] - Moby Availability status from Other WAN devices to the Region of $DeviceName

```kql
let starttime= _startTime;
let endtime = _endTime;
cluster('waneng.westus2').database('waneng').f_GetMobyRawData(_DeviceName,true,starttime,endtime)
| summarize avg(Average) by bin(TimestampUtc, 1m)
| render timechart
```

### Hardware Proxy Api Call Log - Phynet device only

```kql
let starttime= _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
cluster('azphynet').database('DeviceAccess').HardwareProxyApiCall
| where TIMESTAMP >= starttime and TIMESTAMP<=endtime
| where deviceName =~ toupper(_DeviceName)
| where inputs contains SyslogFilter
| project TIMESTAMP, clientId, operationName, inputs, success, faultType, duration
| order by TIMESTAMP asc
```

