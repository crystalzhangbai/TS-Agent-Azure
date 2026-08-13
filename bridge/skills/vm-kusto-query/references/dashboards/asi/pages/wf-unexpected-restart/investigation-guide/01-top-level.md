# (top-level)

> Source: **EEE RDOS — WF Unexpected Restart** dashboard, chapter **(top-level)** (15 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### VM stop check

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `IssueDetector`

```kusto
TMMgmtNodeEventsEtwTable  
| where TIMESTAMP between (queryFrom .. queryTo) and NodeId =~ queryNodeId and Message has strcat(queryContainerId , " of type Microsoft.Cis.Fabric.Controller.Tdm.VirtualMachineContainerReference to be deleted on node")
| project  PreciseTimeStamp, Message
| take 1
| extend Description = "VM stop was triggered by Fabric/CM"
| extend Severity = "information"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`, `{queryContainerId}`

---

### VM shutdown check

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`

```kusto
WindowsEventTable
| where PreciseTimeStamp >= query_BeginTime and PreciseTimeStamp <= query_EndTime
| where NodeId =~ query_NodeId and Description has queryContainerId
| where EventId == 18502
| project TimeCreated,NodeId,Level,Channel,EventId,ProviderName,Description
| take 1
| extend Description = "VM could not gracefully shutdown within 10 min, so it was turned off"
| extend Severity = "information"
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`, `{queryContainerId}`

---

### VM guest OS shutdown

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`

```kusto
WindowsEventTable
| where PreciseTimeStamp >= queryFrom and PreciseTimeStamp <= queryTo
| where NodeId =~ query_NodeId and Description has queryContainerId
| where EventId == 18508
| project TimeCreated,NodeId,Level,Channel,EventId,ProviderName,Description
| take 1
| extend Description = "VM was shutdown by the guest operating system"
| extend Severity = "information"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_NodeId}`, `{queryContainerId}`

---

### Sudden power loss logged

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`

```kusto
WindowsEventTable
| where PreciseTimeStamp >= query_BeginTime and PreciseTimeStamp <= query_EndTime
| where NodeId =~ query_NodeId
| where EventId == 41 and ProviderName == "Microsoft-Windows-Kernel-Power"
| project TimeCreated,NodeId,Level,Channel,EventId,ProviderName,Description
| order by TimeCreated asc
| take 1
| extend Description = "Sudden power loss of host node logged"
| extend Severity = "warning"
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

---

### Power Supply input lost

Cluster: `sparkle.eastus.kusto.windows.net` · Database: `defaultdb` · Type: `IssueDetector`

```kusto
SparkleSELByNodeId(query_NodeId)
| where BMCSelTimestamp between (query_BeginTime .. query_EndTime)
| where SensorType == "Power Supply" and EventDataDetails1 contains "Power Supply input lost or out-of-range"
| project Timestamp = BMCSelTimestamp,
          Source = GeneratorId,
          EventType,
          Sensor = SensorType,
          Details = EventDataDetails1,
          RawHex
| take 1
| extend Description = "SEL: Power Supply input lost"
| extend Severity = "warning"
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_NodeId}`

**Signal filters seen in KQL:** `SensorType == "Power Supply"`

---

### VmStart_failed_Host_LowMem

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`

```kusto
WindowsEventTable  
| where PreciseTimeStamp >= queryFrom and PreciseTimeStamp <= queryTo
| where NodeId =~ queryNodeId
| where EventId in (3050,3122,12030) and ProviderName == "Microsoft-Windows-Hyper-V-Worker"
| take 1
| extend Description = "VM failed to start due to insufficient Memory on Host Node"
| extend Severity = "Critical"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### Container Info_UnexpectedRestart DS

_Widget purpose:_ External Links

Cluster: `azcore.centralus.kusto.windows.net` · Database: `AzureCP` · Type: `Single` · Widget: `Card`

```kusto
MycroftContainerSnapshot
| where PreciseTimeStamp  between (query_BeginTime..query_EndTime)
| where ContainerId == query_ContainerId
| where isnotempty(RoleInstanceName)
| top 1 by PreciseTimeStamp
| join kind=inner(
    cluster('azcore.centralus.kusto.windows.net').database('AzureCP').MycroftClusterSnapshot
    | where PreciseTimeStamp between ((query_BeginTime - 1h) .. (query_EndTime + 1h))
    | distinct ShoeboxMdmAccountName, Tenant
) on $left.Tenant == $right.Tenant
| extend startTimeInMs = datetime_diff('Millisecond',query_BeginTime, startofyear(datetime("1970"))), endTimeInMs = datetime_diff('Millisecond',query_EndTime, startofyear(datetime("1970")))
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_ContainerId}`

---

### Retrieve Resource "VM" Unexpected Restart DS

_Widget purpose:_ External Links

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `ResourceGet` · Widget: `Card`

```kusto
print  tenantName = local_TenantName, containerId = local_ContainerId, nodeId = local_NodeId, vmId = local_vmId
```

**Params:** `{local_ContainerId}`, `{local_NodeId}`, `{local_TenantName}`, `{local_vmId}`

---

### vfpMDM

_Widget purpose:_ External Links

Cluster: `azurehn` · Database: `azurehn` · Type: `Single` · Widget: `Card`

```kusto
MdmVfpVnetAccountMaps
| where Cluster == queryCluster
| project VfpAccount
```

**Params:** `{queryCluster}`

---

### TimeCalcFrom

_Widget purpose:_ External Links

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Single` · Widget: `Card`

```kusto
let toUnixTime = (dt: datetime) { 
    (dt - datetime(1970-01-01)) / 1s 
};
print UnixFrom = toUnixTime(queryFrom)
```

**Params:** `{queryFrom}`

---

### TimeCalcTo

_Widget purpose:_ External Links

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Single` · Widget: `Card`

```kusto
let toUnixTime = (dt: datetime) { 
    (dt - datetime(1970-01-01)) / 1s 
};
print UnixTo = toUnixTime(queryTo)
```

**Params:** `{queryTo}`

---

### Unix Time Helper

_Widget purpose:_ External Links

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `Single` · Widget: `Card`

```kusto
let toUnixTime = (dt:datetime) 
{ 
    (dt - datetime(1970-01-01)) / 1s 
};
print unixTimeFrom = toUnixTime(queryFrom)*1000, unixTimeTo = toUnixTime(queryTo)*1000, queryFrom = queryFrom, queryTo = queryTo
```

**Params:** `{queryFrom}`, `{queryTo}`

---

### LM check

_Widget purpose:_ External Links

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fc` · Type: `IssueDetector` · Widget: `Card`

```kusto
LiveMigrationContainerDetailsEventLog
| where destinationContainerId == query_ContainerId or sourceContainerId == query_ContainerId 
| where PreciseTimeStamp > query_BeginTime and PreciseTimeStamp < query_EndTime
| project sessionId
| join kind=inner    
(LiveMigrationSessionCompleteLog  
| where PreciseTimeStamp > query_BeginTime and PreciseTimeStamp < query_EndTime
| where  status == "Faulted"
| project PreciseTimeStamp, sessionId, status, elapsedTime, reason ,message, subscriptionId, vmUniqueId) on $left.sessionId == $right.sessionId
| take 1
| extend Description = "LM attempt failed for VM"
| extend Severity = "warning"
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_ContainerId}`

**Signal filters seen in KQL:** `status == "Faulted"`

---

### SOCNodeId

Cluster: `overlakedata.southcentralus.kusto.windows.net` · Database: `overlake-syslog` · Type: `Single` · Widget: `CompoundWidgetContainer`

```kusto
let QueryFilterByNodeId = cluster('overlakedata.southcentralus.kusto.windows.net').database('overlake-syslog').OverlakeMap_Latest
| where NodeId =~ queryNodeId;
QueryFilterByNodeId
| summarize count()
| extend OverlakeState = iff(count_ == 0, "Not Enabled", "Enabled")
| project OverlakeState, NodeId = tolower(queryNodeId)
| join kind=leftouter (QueryFilterByNodeId) on NodeId
| project SocNodeId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---

### OverlakeNodeMap

_Widget purpose:_ Overlake / SoC

Cluster: `azcore.centralus.kusto.windows.net` · Database: `OvlProd` · Type: `Single` · Widget: `Card`

```kusto
let socId = toscalar(cluster('azcore.centralus.kusto.windows.net').database('SharedWorkspace').htos(queryNodeId) | take 1);
let overlakeEnabled = iff(isempty(socId), "Not Enabled", "Enabled");
print overlakeEnabled, NodeId = queryNodeId, SocNodeId = socId
| join kind=leftouter(cluster('azcore.centralus.kusto.windows.net').database('OvlProd').LinuxOverlakeVersion
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId =~ socId
) on $left.SocNodeId == $right.NodeId
| project OverlakeState = overlakeEnabled, NodeId = queryNodeId, SocNodeId = socId, MachineName, MachineFunction, Version = PRETTY_NAME, Region
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryNodeId}`

---
