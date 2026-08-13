# Network

> Source: **EEE RDOS — VM Availability** dashboard, chapter **Network** (9 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Network

### Windows Event Log for Networking

_Widget purpose:_ Event Logs for Network Component

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Network > Network > Network Event Log > Network Event Log > Event Logs for Network Component`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable
| where PreciseTimeStamp  between(starttime .. endtime)
| where NodeId == nodeid
| where not (ProviderName == "NETLOGON" and  EventId == 3095)
| where not (ProviderName == 'IPMIDRV' and EventId == 1004)
| where ProviderName <> "CMClientLib"
| where EventId <> 7000
| where EventId <> 1023
| where EventId !in (505, 504, 146, 145, 142)
| where Description !contains "RDMA Session Init Failed."
| where ProviderName == "vfpext" or 
        ProviderName contains "FPGA" or 
        ProviderName contains "mlx" or 
        ProviderName == "VfpExt" or 
        ProviderName contains "Microsoft-Windows-Iphlpsvc" or 
        ProviderName == "NMAgent" or 
        ProviderName contains "mlnx" or 
        (ProviderName == "Application Error" and Description contains "WireServer")
| project PreciseTimeStamp, TimeCreated, Cluster, Level, ProviderName, EventId, Channel, Description, NodeId
| order by TimeCreated asc 
| extend level = case (Level == 1, "critical",
  Level == 2, "error", 
  Level == 3, "warning", 
  "info")
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

**Signal filters seen in KQL:** `ProviderName <> "CMClientLib"` · `ProviderName == "vfpext"`

---

### Timeline for Windows Event Log related to Network Component

_Widget purpose:_ Timeline for Network Component

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Timeline`
Source panel: `Network > Network > Network Event Log > Network Event Log > Timeline for Network Component`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').WindowsEventTable
| where PreciseTimeStamp  between(starttime .. endtime)
| where NodeId == nodeid
| where not (ProviderName == "NETLOGON" and  EventId == 3095)
| where not (ProviderName == 'IPMIDRV' and EventId == 1004)
| where ProviderName <> "CMClientLib"
| where EventId <> 7000
| where EventId <> 1023
| where EventId !in (505, 504, 146, 145, 142)
| where Description !contains "RDMA Session Init Failed."
| where ProviderName == "vfpext" or 
        (ProviderName contains "FPGA" and Description !contains "EventType: -all") or 
        ProviderName contains "mlx" or 
        ProviderName == "VfpExt" or 
        ProviderName contains "Microsoft-Windows-Iphlpsvc" or 
        ProviderName == "NMAgent" or 
        ProviderName contains "mlnx" or 
        (ProviderName == "Application Error" and Description contains "WireServer")
| project PreciseTimeStamp, StartTime = todatetime(TimeCreated), Cluster, Level, ProviderName, EventId, Channel, Description, NodeId
| extend GroupBy = strcat(ProviderName, " - ", EventId), Content = "", EndTime = datetime_add("minute", 1, StartTime)
| order by GroupBy asc, StartTime asc
```

**Params:** `{starttime}`, `{endtime}`, `{nodeid}`

**Signal filters seen in KQL:** `ProviderName <> "CMClientLib"` · `ProviderName == "vfpext"`

---

### Query InterfaceProgramEndFiveMinuteTable

_Widget purpose:_ Interface Program State from InterfaceProgramEndFiveMinuteTable

Cluster: `aznwsdn` · Database: `aznwmds` · Type: `Table`
Source panel: `Network > Network > NM Programming > NM Programming > Interface Program State from InterfaceProgramEndFiveMinuteTable`

```kusto
cluster('aznwsdn').database('aznwmds').InterfaceProgramEndFiveMinuteTable
| where FirstTimeStamp between (queryStart .. queryEnd)
| where ContainerId == queryContainerId
| where NodeId == queryNodeId
| project FirstTimeStamp, ContainerId, MACAddress, Detail, NmAgentBuildInfo, VnetGuid, VnetId, LastTimeStamp
| order by FirstTimeStamp asc
```

**Params:** `{queryContainerId}`, `{queryNodeId}`, `{queryStart}`, `{queryEnd}`

---

### Query DCMNMAgentProgrammingDurationEtwTable

_Widget purpose:_ NM Programming from DCMNMAgentProgrammingDurationEtwTable

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Network > Network > NM Programming > NM Programming > NM Programming from DCMNMAgentProgrammingDurationEtwTable`

```kusto
cluster('azcsupfollower').database('AzureCM').DCMNMAgentProgrammingDurationEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where nodeId == queryNodeId
| where interfaceId contains queryContainerId
| project PreciseTimeStamp, nodeId, interfaceId, message
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`, `{queryNodeId}`

---

### Query SoC Bugchecks

_Widget purpose:_ SoC BugChecks

Cluster: `azuredcm.kusto.windows.net` · Database: `AzureDCMDb` · Type: `Table`
Source panel: `Network > Network > SoC > SoC BugChecks`

```kusto
let _ContainerId = queryContainerId;
let _NodeId = queryNodeId;
let _startTime = queryStart;
let _endTime = queryEnd;

let NodeInformation = () {
    let impactedContainerId = tolower(["_ContainerId"]);
    let impactStartTime =["_startTime"];
    let impactEndTime = ["_endTime"];
    let output = materialize(cluster("azurehn.kusto.windows.net").database("Azurehn").fn_GetNodeInfo_v2(impactStartTime, impactEndTime,["_NodeId"], impactedContainerId));
    output
};
let impactedContainerId = tolower(["_ContainerId"]);
let impactStartTime =["_startTime"];
let impactEndTime = ["_endTime"];
let impactedNodeId = toscalar(NodeInformation | project NodeId);
let socID = toscalar(NodeInformation | project SocId);
let BladeNameTable = cluster('azuredcm.kusto.windows.net').database('AzureDCMDb').ResourceSnapshotV1
    | where PreciseTimeStamp > ago(2d)
    | where ResourceId =~ impactedNodeId or ResourceId =~ socID
    | project HostName, DeviceType
    | distinct HostName, DeviceType
    | limit 2;

let startSearchTime = impactStartTime - 3h;
let endSearchTime = impactEndTime + 3h;
let SocName1 = toscalar(BladeNameTable | where DeviceType == "SoC" | project HostName);
let HostName = toscalar(BladeNameTable | where DeviceType == "Blade" | project HostName);
let SocName2 = strcat(HostName, "SOC");
let SocName = iff(isempty(SocName1), SocName2, SocName1);
let crashApMachineName = toscalar(
    cluster('Azuredcm').database('AzureDCMDb').dcmInventoryMachines
    | where AzureNodeId =~ impactedNodeId
    | project MachineName);
let crashSocName = toscalar(
    cluster('Azuredcm').database('AzureDCMDb').dcmInventoryMachines
    | where AzureNodeId =~ socID
    | project MachineName);
let hostdumps=cluster('azurewatsoncustomer').database('AzureWatsonCustomer').CustomerCrashOccurredV2
    | extend CrashTimeDt = PreciseTimeStamp
    | where PreciseTimeStamp >= startSearchTime and PreciseTimeStamp <= endSearchTime
    | union (
        cluster('azurewatsoncustomer').database('AzureWatsonCustomer').CustomerDumpAnalysisResultV2
        | extend CrashTimeDt = iff(isempty(crashTime), PreciseTimeStamp, todatetime(crashTime))
        | where CrashTimeDt between (impactStartTime .. impactEndTime)
        | where apMachine =~ crashApMachineName and isnotempty(crashApMachineName)
        | extend Description=bucketString)
    | where apMachine =~ crashApMachineName and isnotempty(crashApMachineName)
    | extend
        WatsonURL = strcat("https://azurewatson.microsoft.com/?DumpUID=", dumpUid, "&NodeID=", impactedNodeId),
        Description = iff(isempty(bucketString), process , bucketString),
        Type = "Host";
let socdumps=cluster('azurewatsoncustomer').database('AzureWatsonCustomer').CustomerCrashOccurredV2
    | extend CrashTimeDt = PreciseTimeStamp
    | where PreciseTimeStamp >= startSearchTime and PreciseTimeStamp <= endSearchTime
    | union (
        cluster('azurewatsoncustomer').database('AzureWatsonCustomer').CustomerDumpAnalysisResultV2
        | extend CrashTimeDt = iff(isempty(crashTime), PreciseTimeStamp, todatetime(crashTime))
        | where CrashTimeDt between (impactStartTime .. impactEndTime)
        | where apMachine =~ SocName
        | extend Description=bucketString)
    | where apMachine =~ crashSocName and isnotempty(crashSocName)
    | extend
        WatsonURL = strcat("https://azurewatson.microsoft.com/?DumpUID=", dumpUid, "&NodeID=", socID),
        Description = iff(isempty(bucketString), process , bucketString),
        Type = "SOC";
hostdumps
| union socdumps
| project CrashTimeDt, Type, Description, WatsonURL, apMachine
| sort by CrashTimeDt
```

**Params:** `{queryStart}`, `{queryEnd}`, `{queryContainerId}`, `{queryNodeId}`

**Signal filters seen in KQL:** `DeviceType == "SoC"` · `DeviceType == "Blade"`

---

### Query SoC Crash

_Widget purpose:_ SoC Crash Query

Cluster: `azurehn.kusto.windows.net` · Database: `Azurehn` · Type: `Table`
Source panel: `Network > Network > SoC > SoC Crash Query`

```kusto
let _NodeId = queryNodeId;
let _startTime = queryStart;
let _endTime = queryEnd;

let socID = toscalar(cluster('azuredcm.kusto.windows.net').database('AzureDCMDb').GetSocOrNodeFromResourceId(queryNodeId));
cluster('azcore.centralus.kusto.windows.net').database('OvlProd').LinuxOverlakeSystemd
| where PreciseTimeStamp between (queryStart .. queryEnd)
| where NodeId =~ socID
| where MESSAGE contains "dumped core"
| project PreciseTimeStamp, MESSAGE, _SYSTEMD_UNIT
```

**Params:** `{queryStart}`, `{queryEnd}`, `{queryNodeId}`

**Signal filters seen in KQL:** `MESSAGE contains "dumped core"`

---

### Query Soc Memory Usage

_Widget purpose:_ SoC Memory Usage

Cluster: `azurehn.kusto.windows.net` · Database: `Azurehn` · Type: `TimeSeries`
Source panel: `Network > Network > SoC > SoC Memory Usage`

```kusto
let _ContainerId = queryContainerId;
let _NodeId = queryNodeId;
let _startTime = queryStart;
let _endTime = queryEnd;

let NodeInformation = () {
    let impactedContainerId = tolower(["_ContainerId"]);
    let impactStartTime =["_startTime"];
    let impactEndTime = ["_endTime"];
    let output = materialize(cluster("azurehn.kusto.windows.net").database("Azurehn").fn_GetNodeInfo_v2(impactStartTime, impactEndTime,["_NodeId"], impactedContainerId));
    output
};
let impactedContainerId = tolower(["_ContainerId"]);
let impactStartTime =["_startTime"];
let impactEndTime = ["_endTime"];
let impactedNodeId = toscalar(NodeInformation | project NodeId);
let socID = toscalar(NodeInformation | project SocId);
let timeSpan=impactEndTime - impactStartTime;
let bucketSize=case(timeSpan > 7d, "6h", timeSpan > 1d, "1h", "1m");
let SocName = toscalar(NodeInformation | project SoCMachineName);
let account = 'Overlake';
let query = strcat('metricNamespace("procstat").metric("memory_rss").preaggregate("By-cluster-host-process_name").samplingTypes("Average") | where host == "', SocName, '" | zoom binnedAvg=avg(Average) by ', tostring(bucketSize));
let metric = evaluate geneva_metrics_request(account, query, impactStartTime, impactEndTime);
metric 
|project TimestampUtc = column_ifexists("TimestampUtc", 0), binnedAvg=(column_ifexists("binnedAvg",0))/1e6,process_name=column_ifexists("process_name","unknown")
|project-rename binnedAvgMemoryInMB = binnedAvg
```

**Params:** `{queryStart}`, `{queryEnd}`, `{queryContainerId}`, `{queryNodeId}`

**Signal filters seen in KQL:** `host == "', SocName, '"`

---

### Query SoC CPU

_Widget purpose:_ SoC Process CPU Usage in MB

Cluster: `azurehn.kusto.windows.net` · Database: `Azurehn` · Type: `TimeSeries`
Source panel: `Network > Network > SoC > SoC Process CPU Usage in MB`

```kusto
let _ContainerId = queryContainerId;
let _NodeId = queryNodeId;
let _startTime = queryStart;
let _endTime = queryEnd;

let NodeInformation = () {
    let impactedContainerId = tolower(["_ContainerId"]);
    let impactStartTime =["_startTime"];
    let impactEndTime = ["_endTime"];
    let output = materialize(cluster("azurehn.kusto.windows.net").database("Azurehn").fn_GetNodeInfo_v2(impactStartTime, impactEndTime,["_NodeId"], impactedContainerId));
    output
};
let impactedContainerId = tolower(["_ContainerId"]);
let impactStartTime =["_startTime"];
let impactEndTime = ["_endTime"];
let impactedNodeId = toscalar(NodeInformation | project NodeId);
let socID = toscalar(NodeInformation | project SocId);
let timeSpan=impactEndTime - impactStartTime;
let bucketSize=case(timeSpan > 7d, "6h", timeSpan > 1d, "1h", "1m");
let SocName = toscalar(NodeInformation | project SoCMachineName);
let account = 'Overlake';
let query = strcat('metricNamespace("procstat").metric("cpu_usage").preaggregate("by-cluster-host-process_name").samplingTypes("Average") | where host == "', SocName, '" | zoom binnedAverage=avg(Average) by ', tostring(bucketSize));
let metric = evaluate geneva_metrics_request(account, query, impactStartTime, impactEndTime);
metric
|project TimestampUtc = column_ifexists("TimestampUtc", 0), binnedAverage=column_ifexists("binnedAverage",0),process_name=column_ifexists("process_name","unknown")
```

**Params:** `{queryStart}`, `{queryEnd}`, `{queryContainerId}`, `{queryNodeId}`

**Signal filters seen in KQL:** `host == "', SocName, '"`

---

### Query Soc Memory Usage

_Widget purpose:_ SoC Process CPU Usage in MB

Cluster: `azurehn.kusto.windows.net` · Database: `Azurehn` · Type: `TimeSeries`
Source panel: `Network > Network > SoC > SoC Process CPU Usage in MB`

```kusto
let _ContainerId = queryContainerId;
let _NodeId = queryNodeId;
let _startTime = queryStart;
let _endTime = queryEnd;

let NodeInformation = () {
    let impactedContainerId = tolower(["_ContainerId"]);
    let impactStartTime =["_startTime"];
    let impactEndTime = ["_endTime"];
    let output = materialize(cluster("azurehn.kusto.windows.net").database("Azurehn").fn_GetNodeInfo_v2(impactStartTime, impactEndTime,["_NodeId"], impactedContainerId));
    output
};
let impactedContainerId = tolower(["_ContainerId"]);
let impactStartTime =["_startTime"];
let impactEndTime = ["_endTime"];
let impactedNodeId = toscalar(NodeInformation | project NodeId);
let socID = toscalar(NodeInformation | project SocId);
let timeSpan=impactEndTime - impactStartTime;
let bucketSize=case(timeSpan > 7d, "6h", timeSpan > 1d, "1h", "1m");
let SocName = toscalar(NodeInformation | project SoCMachineName);
let account = 'Overlake';
let query = strcat('metricNamespace("procstat").metric("memory_rss").preaggregate("By-cluster-host-process_name").samplingTypes("Average") | where host == "', SocName, '" | zoom binnedAvg=avg(Average) by ', tostring(bucketSize));
let metric = evaluate geneva_metrics_request(account, query, impactStartTime, impactEndTime);
metric 
|project TimestampUtc = column_ifexists("TimestampUtc", 0), binnedAvg=(column_ifexists("binnedAvg",0))/1e6,process_name=column_ifexists("process_name","unknown")
|project-rename binnedAvgMemoryInMB = binnedAvg
```

**Params:** `{queryStart}`, `{queryEnd}`, `{queryContainerId}`, `{queryNodeId}`

**Signal filters seen in KQL:** `host == "', SocName, '"`

---
