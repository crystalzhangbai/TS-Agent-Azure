# Host Hardware Faults

> Source: EEE RDOS Start Hub dashboard (8 queries).

Use when investigating: **bugcheck (BSOD on host), WHEA, memory errors, disk hardware errors, SEL events, NVMe controller issues, host hardware fingerprint**. These queries identify physical hardware failure root cause.

---

### DCM SEL (Sparkle)

_Purpose:_ Node Health

Cluster: `sparkle.eastus.kusto.windows.net` · Database: `defaultdb` · Type: `Timeline`

```kusto
cluster("sparkle.eastus.kusto.windows.net").database("defaultdb").SparkleSELByNodeId(nodeId=queryNodeId, queryFrom, queryTo)
| where isnotempty( DataCenter )
| where SensorType <> "" and BMCSelItemMessage <> ""
| where BMCSelTimestamp > queryFrom
// | where SensorType == 'Management Subsystem Health'
| distinct BMCSelTimestamp, Cluster, RecordId, RecordType, BMCSelItemMessage, SensorId, SensorType, EventData1, 
  EventData2, EventData3, EventDataDetails1, EventDataDetails2, EventDataDetails3, RawHex
| project StartTime = BMCSelTimestamp, RecordId, BMCSelItemMessage, RawHex, Content = SensorType
| extend Health = case (BMCSelItemMessage contains ' CRT ' or BMCSelItemMessage contains ' MAJ ', 'Unhealthy', 
    BMCSelItemMessage contains ' MIN ', 'Degraded', 'Neutral')
| order by StartTime asc, RecordId asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `SensorType == "Management Subsystem Health"`

---

### DCM SEL

_Purpose:_ Node Health

Cluster: `azuredcm` · Database: `AzureDCMDb` · Type: `Timeline`

```kusto
cluster("azuredcm.kusto.windows.net").database("AzureDCMDb").RhwChassisSelItemEtwTable
| where BmcSelItemTimeStamp between(queryFrom .. queryTo)
| where ResourceId == queryNodeId
| where BmcSelItemSensorName <> "BMC Health"
| where BmcSelItemEventType in ( "Critical Interrupt", "Processor", "Temparature", "Memory", "Button", "OS Critical Stop") or 
    (BmcSelItemEventType == 'Battery' and BmcSelItemDetails contains 'Failed') or 
    (BmcSelItemEventType == 'Management Subsystem Health' and BmcSelItemDetails contains 'HAL error') or 
    (BmcSelItemEventType == 'Voltage' and BmcSelItemSensorName !contains 'CPU' and BmcSelItemSeverity == 'MAJ') or 
    (BmcSelItemEventType == 'Power Supply' and BmcSelItemDetails in ('AC Lost', 'Failure detected'))
| distinct BmcSelItemTimeStamp, Cluster, BmcSelItemId, BmcSelItemSeverity, BmcSelItemSource, BmcSelItemEventType, BmcSelItemSensorName, BmcSelItemDetails, BmcSelItemRawHex
| order by BmcSelItemTimeStamp asc
| extend level = case (BmcSelItemSeverity == "CRT", "critical", "info")
| extend Content = BmcSelItemDetails, Health = "Unhealthy"
| project StartTime = BmcSelItemTimeStamp, Cluster, BmcSelItemId, BmcSelItemSeverity, BmcSelItemSource, BmcSelItemEventType, BmcSelItemSensorName, BmcSelItemDetails, BmcSelItemRawHex, level, Content, Health
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

**Signal filters seen in KQL:** `BmcSelItemSensorName <> "BMC Health"`

---

### Kernel/Driver Events

_Purpose:_ Node Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable
| where PreciseTimeStamp  between(queryFrom .. queryTo)
| where NodeId == queryNodeId
| where not (ProviderName contains "Kernel-Processor" and EventId == 37) // eliminating periodical processor report event every day.
| where not (ProviderName == "Microsoft-Windows-Kernel-PnP") // eliminating PnP messages
// | where not (ProviderName contains "PnP" and EventId == 1010) // eliminating PnP errors. 
| where ProviderName in ("OSHostPlugin", "UpdateNotification", "NMAgent", "Microsoft-Windows-UserModePowerService", "EventLog") or 
    ProviderName contains "Microsoft-Windows-Kernel" or
    (ProviderName == "CSI-CloudFPGA-FPGAMgmt" and Description contains "EventType: AfterInstall") or 
    (ProviderName == "CSI-CloudFPGA-FPGAMgmt" and Description contains "EventType: BeforeInstall") or 
    (ProviderName == "CSI-CloudFPGA-FPGAMgmt" and Description contains "FPGA driver install") or
    (ProviderName contains "vfpext" and EventId == 7036) or
    (ProviderName == "Microsoft-Windows-Kernel-General" and EventId == "12") or
    (ProviderName == "Microsoft-Windows-Kernel-General" and EventId == "18") or 
    (ProviderName contains "Microsoft-Windows-Kernel-Power" and EventId == "41")
| project PreciseTimeStamp, todatetime(TimeCreated), Cluster, Level, ProviderName, EventId, Channel, Description, NodeId
| order by TimeCreated asc
| extend level = case (Level == 1, "critical", 
    Level == 2, "error", 
    Level == 3, "warning",
    "info")
| project StartTime = TimeCreated, Cluster, Level, ProviderName, EventId, Channel, Description, NodeId, Content = strcat(ProviderName, " - ", EventId)
| extend Health = case (Level <= 2, "Unhealthy", Level == 3, "Degraded", "Healthy")
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Remarkable Event - Disk

_Purpose:_ Node Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

```kusto
let referenceTable = datatable(ProviderName:string, EventId:string, ShortName:string, Category:string, Health:string) [
    // disk
    "disk", 7, "disk", "Disk", "Unhealthy",
    "LSI_SAS2i", 11, "LSI_SAS", "Disk", "Unhealthy",
    "LSI_SAS3i", 11, "LSI_SAS", "Disk", "Unhealthy",
    "VhdDiskPrt", 16, "VhdDiskPrt", "Disk", "Degraded",
    "VhdDiskPrt", 17, "VhdDiskPrt", "Disk", "Unhealthy",
    "disk", 52, "disk", "Disk", "Degraded",
    "Ntfs", 55, "Ntfs", "Disk", "Degraded",
    "VhdDiskPrt", 66, "VhdDiskPrt", "Disk", "Degraded",
    "VhdDiskPrt", 67, "VhdDiskPrt", "Disk", "Degraded",
    "Storahci", 129, "Storahci", "Disk", "Unhealthy",
    "vhdmp", 129, "vhdmp", "Disk", "Unhealthy",
    "elxstor", 129, "elxstor", "Disk", "Unhealthy",
    "HpCISSs3", 129, "HpCISSs3", "Disk", "Unhealthy",
    "stornvme", 129, "stornvme", "Disk", "Unhealthy",
    "LSI_SAS2i", 129, "LSI_SAS", "Disk", "Unhealthy",
    "LSI_SAS3i", 129, "LSI_SAS", "Disk", "Unhealthy",
    "VhdDiskPrt", 129, "VhdDiskPrt", "Disk", "Unhealthy",
    "Microsoft-Windows-Ntfs", 141, "NTFS", "Disk", "Unhealthy",
    "Microsoft-Windows-Ntfs", 147, "NTFS", "Disk", "Degraded",
    "Microsoft-Windows-Ntfs", 149, "NTFS", "Disk", "Degraded",
    "disk", 153, "disk", "Disk", "Degraded",
    "disk", 154, "disk", "Disk", "Degraded",
    "Microsoft-Windows-StorPort", 500, "StorPort", "Disk", "Unhealthy",
    "Microsoft-Windows-Hyper-V-NvmeDirectDriver", 5006, "HyperV NVME", "Disk", "Unhealthy",
    //"Microsoft-Windows-Hyper-V-NvmeDirectDriver", 6003, "HyperV NVME", "Disk", "Unhealthy", // in most cases, this event is ignorable
];
cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| project PreciseTimeStamp, todatetime(TimeCreated), Cluster, Level, ProviderName, EventId, Channel, Description, NodeId
| join kind=inner (referenceTable) on $left.ProviderName == $right.ProviderName and $left.EventId == $right.EventId
| extend Content = strcat (ShortName, ", ", EventId)
| project StartTime = TimeCreated, Cluster, Level, ProviderName, EventId, Channel, Description, NodeId, ShortName, Category, Content, Health
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Remarkable Event - WHEA

_Purpose:_ Node Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

```kusto
let referenceTable = datatable(ProviderName:string, EventId:string, ShortName:string, Category:string, Health:string) [
    // WHEA
    "Microsoft-Windows-WHEA-Logger", 16, "WHEA", "Hardware", "Unhalthy",
    //"Microsoft-Windows-WHEA-Logger", 17, "WHEA", "Hardware", "Degraded",
    "Microsoft-Windows-WHEA-Logger", 22, "WHEA", "Hardware", "Unhalthy",
    "Microsoft-Windows-WHEA-Logger", 23, "WHEA", "Hardware", "Degraded",
    "Microsoft-Windows-WHEA-Logger", 26, "WHEA", "Hardware", "Unhalthy",
    "Microsoft-Windows-WHEA-Logger", 40, "WHEA", "Hardware", "Unhalthy",
    "Microsoft-Windows-WHEA-Logger", 41, "WHEA", "Hardware", "Degraded",
    "Microsoft-Windows-WHEA-Logger", 46, "WHEA", "Hardware", "Unhalthy",
    "Microsoft-Windows-WHEA-Logger", 47, "WHEA", "Hardware", "Degraded",
    "Microsoft-Windows-Kernel-PnP", 902, "PnP",  "Driver/Hardware", "Degraded",
    "Microsoft-Windows-Kernel-PnP", 903, "PnP",  "Driver/Hardware", "Degraded",
];
cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| project PreciseTimeStamp, todatetime(TimeCreated), Cluster, Level, ProviderName, EventId, Channel, Description, NodeId
| join kind=inner (referenceTable) on $left.ProviderName == $right.ProviderName and $left.EventId == $right.EventId
| extend Content = strcat (ShortName, ", ", EventId)
| where Description !contains "Component: Memory"
| project StartTime = TimeCreated, Cluster, Level, ProviderName, EventId, Channel, Description, NodeId, ShortName, Category, Content, Health
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Remarkable Event - Memory

_Purpose:_ Node Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

```kusto
let referenceTable = datatable(ProviderName:string, EventId:string, ShortName:string, Category:string, Health:string) [
    // Memory events
    "Microsoft-Windows-WHEA-Logger", 16, "WHEA", "Hardware", "Unhalthy",
    "Microsoft-Windows-WHEA-Logger", 17, "WHEA", "Hardware", "Degraded",
    "Microsoft-Windows-WHEA-Logger", 22, "WHEA", "Hardware", "Unhalthy",
    "Microsoft-Windows-WHEA-Logger", 23, "WHEA", "Hardware", "Degraded",
    "Microsoft-Windows-WHEA-Logger", 26, "WHEA", "Hardware", "Unhalthy",
    "Microsoft-Windows-WHEA-Logger", 40, "WHEA", "Hardware", "Unhalthy",
    "Microsoft-Windows-WHEA-Logger", 41, "WHEA", "Hardware", "Degraded",
    "Microsoft-Windows-WHEA-Logger", 46, "WHEA", "Hardware", "Unhalthy",
    "Microsoft-Windows-WHEA-Logger", 47, "WHEA", "Hardware", "Degraded",
    "Microsoft-Windows-Resource-Exhaustion-Detector", 2004, "ResourceExaust", "Memory", "Unhealthy",
    "Microsoft-Windows-Hyper-V-Worker", 3050, "Hyper-V", "Hardware", "Unhealthy",
    "Microsoft-Windows-Hyper-V-Worker", 3122, "Hyper-V", "Hardware", "Unhealthy",
    "Microsoft-Windows-Hyper-V-Worker", 3273, "Hyper-V", "Hardware", "Unhealthy",
    "Microsoft-Windows-Hyper-V-VID", 5043, "Hyper-V", "Hardware", "Unhealthy",
    "Microsoft-Windows-Hyper-V-VID", 5043, "Hyper-V", "Hardware", "Unhealthy",
];
cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId == queryNodeId
| project PreciseTimeStamp, todatetime(TimeCreated), Cluster, Level, ProviderName, EventId, Channel, Description, NodeId
| where (ProviderName == "Microsoft-Windows-WHEA-Logger" and Description contains "Component: Memory") or 
        Description contains "0x8007000E" or
        ProviderName <> "Microsoft-Windows-WHEA-Logger"
| join kind=inner (referenceTable) on $left.ProviderName == $right.ProviderName and $left.EventId == $right.EventId
| extend ShortName = case (isempty(ShortName), ProviderName, ShortName) // in case of 0x8007000E
| extend Health = case (isempty(Health), "Unhealthy", Health) // in case of 0x8007000E
| extend Content = strcat (ShortName, ", ", EventId)
| project StartTime = TimeCreated, Cluster, Level, ProviderName, EventId, Channel, Description, NodeId, ShortName, Category, Content, Health
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Remarkable Event - HyperV

_Purpose:_ Node Health

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`

```kusto
let referenceTable = datatable(ProviderName:string, EventId:string, SuspiciousCategory:string, Health:string) [
    // Guest OS 
    "Microsoft-Windows-Hyper-V-Worker", 18590, "GuestOS", "Degraded",
    "Microsoft-Windows-Hyper-V-Chipset", 18600, "GuestOS", "Degraded",
    "Microsoft-Windows-Hyper-V-Worker", 18602, "GuestOS", "Degraded",
    "Microsoft-Windows-Hyper-V-Worker", 18604, "GuestOS", "Degraded",
    "Microsoft-Windows-Hyper-V-Worker", 18540, "GuestOS", "Degraded", // triple fault by guest
    "Microsoft-Windows-Hyper-V-Worker", 18570, "GuestOS", "Degraded", // unsupported interception instruction
    "Microsoft-Windows-Hyper-V-Worker", 18610, "GuestOS", "Degraded", // guest virtual firmware - fatal error
    "Microsoft-Windows-Hyper-V-Chipset", 18610, "GuestOS", "Degraded", // guest virtual firmware - fatal error
    // Platform 
    "Microsoft-Windows-Hyper-V-VMMS", 14070, "Platform", "Degraded",
    "Microsoft-Windows-Hyper-V-VMMS", 14154, "Platform", "Degraded",
    "Microsoft-Windows-Hyper-V-VMMS", 15140, "Platform", "Degraded",
    "Microsoft-Windows-Hyper-V-VMMS", 16000, "Platform", "Degraded",
    "Microsoft-Windows-Hyper-V-Worker", 18550, "Platform/HyperV", "Degraded", // triple fault
    "Microsoft-Windows-Hyper-V-Worker", 18560, "Platform", "Degraded",  // triple fault
    "Microsoft-Windows-Hyper-V-Worker", 18572, "Platform", "Degraded",  // general protection
    "Microsoft-Windows-Hyper-V-Worker", 21102, "Platform/LM", "Degraded", // recover failure from migration under LM
    "Microsoft-Windows-Hyper-V-VMMS", 16010, "Platform/HyperV", "Degraded", // hyper-v operation error - ignorable if the count is not high. 
    // Platform - critical error
    "Microsoft-Windows-Hyper-V-VMMS", 18190, "Platform/HyperV", "Unhealthy", // hyper-v worker process issue
    "Microsoft-Windows-Hyper-V-Worker", 18524, "Platform", "Unhealthy", // network critical issue? 
    "Microsoft-Windows-Hyper-V-VMMS", 19050, "Platform/HyperV", "Unhealthy", // hyper-v operation failures. 
    "Microsoft-Windows-Hyper-V-VMMS", 19060, "Platform/HyperV", "Unhealthy", // hyper-v operation failures. 
    "Microsoft-Windows-Hyper-V-VMMS", 19062, "Platform/HyperV", "Unhealthy", // hyper-v operation timeout. 
    "Microsoft-Windows-Hyper-V-VMMS", 19064, "Platform/HyperV", "Unhealthy", // hyper-v operation being locked. 
    "Microsoft-Windows-Hyper-V-Worker", 21102, "Platform/LM", "Degraded", // recover failure from migration under LM
    "Microsoft-Windows-Hyper-V-Worker", 12004, "Platform/HyperV", "Unhealthy", // hyper-v bios error 
];
cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable
| where PreciseTimeStamp between( queryFrom .. queryTo )
| where NodeId == queryNodeId
| where ProviderName in ("Microsoft-Windows-Hyper-V-Worker", "Microsoft-Windows-Hyper-V-Chipset", "Microsoft-Windows-Hyper-V-VMMS")
| project PreciseTimeStamp, todatetime(TimeCreated), Level, Cluster, Channel, ProviderName, EventId, Description
| extend ProviderNameAndEventId = strcat (ProviderName, "_", EventId)
| join kind=leftouter (referenceTable) on $left.ProviderName == $right.ProviderName, $left.EventId == $right.EventId
| where SuspiciousCategory <> ""
| extend Content = EventId, StartTime = TimeCreated
| project StartTime, Level, Cluster, ProviderName, EventId, Description, SuspiciousCategory, Content, Health
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Azure Watson

_Purpose:_ Node Health

Cluster: `azurewatsoncustomer` · Database: `AzureWatsonCustomer` · Type: `Timeline`

```kusto
let azurewatsonlink = strcat("https://portal.watson.azure.com/?NodeId=", queryNodeId);
cluster('azurewatsoncustomer.kusto.windows.net').database('AzureWatsonCustomer').CustomerCrashOccurredV2
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where nodeIdentity == queryNodeId
| project PreciseTimeStamp, EventMessage, platform, crashMode, process, environment, dumpUid
| join kind= leftouter (
    cluster('azurewatsoncustomer.kusto.windows.net').database('AzureWatsonCustomer').CustomerDumpAnalysisResultV2
    | where PreciseTimeStamp between (queryFrom..queryTo)
    | project AnalyzedTime=PreciseTimeStamp, DumpAnalalysisMessage=EventMessage, faultingModule, faultingProcess, bucketString, crashTime, dumpType, bugId, bugLink, dumpUid
) on $left.dumpUid == $right.dumpUid
| extend AzureWatsonLink=azurewatsonlink
| where crashTime <> ""
| project StartTime = todatetime(crashTime), AnalyzedTime, dumpType, crashMode, platform, DumpAnalalysisMessage, faultingModule, faultingProcess, bugId, bugLink, AzureWatsonLink
| extend Content = strcat(crashMode, " ", faultingProcess,"!",faultingModule)
| extend Health = case (crashMode == "um", "Degraded", "Unhealthy")
| order by StartTime asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---
