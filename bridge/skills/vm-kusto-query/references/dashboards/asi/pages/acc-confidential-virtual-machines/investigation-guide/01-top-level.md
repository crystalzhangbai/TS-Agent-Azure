# (top-level)

> Source: **Azure Confidential Compute - Confidential Virtual Machines** dashboard, chapter **(top-level)** (3 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Virtual Machines"

Cluster: `azurecm` · Database: `AzureCM` · Type: `ResourceGet` · Widget: `Container`

```kusto
LogContainerSnapshot
| where PreciseTimeStamp >= global_startTime and PreciseTimeStamp <= global_endTime
| where virtualMachineUniqueId == local_virtualMachineUniqueId
| summarize arg_max(PreciseTimeStamp, *) by virtualMachineUniqueId
```

**Params:** `{local_subscriptionId}`, `{local_virtualMachineUniqueId}`

---

### VM Containers

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`

```kusto
LogContainerSnapshot
| where PreciseTimeStamp between(global_startTime..global_endTime)
| where virtualMachineUniqueId == queryVmId
| extend Resource = containerId
| project PreciseTimeStamp, Resource
| order by PreciseTimeStamp asc
| extend PrevTime = prev(PreciseTimeStamp)
| extend NextTime = next(PreciseTimeStamp)
| extend Prev = prev(Resource)
| extend Next = next(Resource)
| where 
isnull(PrevTime) or 
isnull(NextTime) or 
(Resource != Prev or Resource != Next) 
| extend StartTime = PreciseTimeStamp
| extend EndTime = next(PreciseTimeStamp)
| summarize StartTime = arg_min(StartTime, *), EndTime = max(EndTime) by Resource
| project StartTime, EndTime, Content = Resource
| extend EndTime = iif(isnull(EndTime), datetime_add('minute', 1, StartTime), EndTime)
| extend Tooltip = strcat("Container: ", Content, "<br/>","FirstSeen: ", StartTime, "<br/>", "EndTime: ", EndTime)
```

**Params:** `{queryVmId}`

---

### VMA

Cluster: `vmainsight` · Database: `vmadb` · Type: `Timeline`

```kusto
let queryIncludeCustomerInitiated = true;
VMA
| where PreciseTimeStamp between(global_startTime..global_endTime)
| where VmUniqueId == queryVmOrContainerId or ContainerId == queryVmOrContainerId
| where isempty(queryTenantName) or TenantName == queryTenantName
| where queryIncludeCustomerInitiated or RCAEngineCategory != 'CustomerInitiated'
| order by PreciseTimeStamp asc
| extend CustomerInitiated = tobool(strcmp(RCAEngineCategory, 'CustomerInitiated') == 0)
| project StartTime, EndTime, DurationInSec = datetime_diff('second', EndTime, StartTime), CustomerInitiated,
AvailabilityState, NodeIp, RCA, RCAEngineCategory, RCACSSCategory, RCALevel1, RCALevel2, RCALevel3, NodeId,
Detail, DowntimeReasonHint, scaleSetName = Usage_VMScaleSetName, resourceGroupName = Usage_ResourceGroupName,
RoleInstanceName = substring(RoleInstanceName, 1, strlen(RoleInstanceName)), ContainerId, vmId = VmUniqueId
| summarize StartTime = arg_max(StartTime, *) by bin(StartTime, 1m)
| extend Tooltip = strcat(
    "ContainerId: ", ContainerId, 
    "<br/>VMId: ", vmId, 
    "<br/>NodeId: ", NodeId, 
    "<br/>RoleInstanceName: " , RoleInstanceName, 
    "<br/>Customer Initiated: ", CustomerInitiated,
    "<br/>RCA: ", RCA,
    "<br/>RCAEngineCategory: ", RCAEngineCategory,
    "<br/>RCACSSCategory: ", RCACSSCategory,
    "<br/>RCALevel1: ", RCALevel1,
    "<br/>RCALevel2: ", RCALevel2,
    "<br/>RCALevel3: ", RCALevel3
    )
| project StartTime, Content = RCALevel3, Resource = RCALevel3, Tooltip
```

**Params:** `{queryVmOrContainerId}`, `{queryTenantName}`, `{global_startTime}`, `{global_endTime}`

---
