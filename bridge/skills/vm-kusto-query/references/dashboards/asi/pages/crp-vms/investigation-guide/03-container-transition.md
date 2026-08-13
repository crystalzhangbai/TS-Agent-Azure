# Container Transition

> Source: **CRP — VMs** dashboard, chapter **Container Transition** (3 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### ContainerStateTransition

_Widget purpose:_ Container Transition

Cluster: `azcore.centralus` · Database: `AzureCP` · Type: `Timeline`
Source panel: `Container Transition`

```kusto
MycroftContainerHealthSnapshot
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where (isnotempty(queryVmId) and VirtualMachineUniqueId =~ queryVmId) or (isempty(queryVmId) and ContainerId =~ queryContainerId)
| project StartTime = PreciseTimeStamp, ClusterName, RoleInstanceName,  TenantName, ContainerId, NodeId, 
  Content = ContainerState, ActualOperationalState, LifecycleState, OsState, FaultInfo , VirtualMachineUniqueId
| order by StartTime asc
| extend flag = case (Content <> prev(Content), "changed", "")
| where flag <> "" or LifecycleState == "Destroyed"
| extend EndTime = case(isnotempty(next(StartTime)), next(StartTime), queryTo)
| where LifecycleState <> "Destroyed"
| extend Health = case (Content in ("ContainerStateUnresponsive", "ContainerStateUnhealthy", "ContainerStateUnknown"), "Unhealthy", Content == "ContainerStateStarted", "Healthy", "Degraded")
| extend GroupBy = strcat("Container (", substring(ContainerId, 0, 8), "~)")
| project StartTime, EndTime, Content, Health, GroupBy, ClusterName, TenantName, ContainerId, NodeId, VirtualMachineUniqueId, RoleInstanceName
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryVmId}`, `{queryContainerId}`

**Signal filters seen in KQL:** `LifecycleState <> "Destroyed"`

---

### ContainerOSStateTransition

_Widget purpose:_ Container Transition

Cluster: `azcore.centralus` · Database: `AzureCP` · Type: `Timeline`
Source panel: `Container Transition`

```kusto
MycroftContainerHealthSnapshot
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where (isnotempty(queryVmId) and VirtualMachineUniqueId =~ queryVmId) or (isempty(queryVmId) and ContainerId =~ queryContainerId)
| project PreciseTimeStamp, ClusterName, RoleInstanceName,  TenantName, ContainerId, NodeId, 
  ContainerState, ActualOperationalState, LifecycleState, OsState, FaultInfo, VirtualMachineUniqueId
| project StartTime = PreciseTimeStamp, Content = OsState, LifecycleState, ClusterName, RoleInstanceName, TenantName, ContainerId, NodeId, VirtualMachineUniqueId
| order by StartTime asc
| extend flag = case (Content <> prev(Content), "changed", "")
| where flag <> "" or LifecycleState == "Destroyed"
| extend EndTime = case(isnotempty(next(StartTime)), next(StartTime), queryTo)
| where LifecycleState <> "Destroyed"
| extend Health = case (Content in ("ContainerOsStateUnknown", "ContainerOsStateUnresponsive", "ContainerOsStateUnhealthy"), "Unhealthy", 
    Content in ("ContainerOsStateHealthy", "ContainerOsStateProvisioningCompleted"), "Healthy", 
    Content in ("ContainerOsStateInternalShutdown", "ContainerOsStateProvisioningTimedOut", "ContainerOsStateProvisioningRecovery", "ContainerOsStateProvisioningFailed"), "Degraded", 
    "Neutral")
| extend GroupBy = strcat("ContainerOs (", substring(ContainerId, 0, 8), "~)")
| project StartTime, EndTime, Content, Health, GroupBy, ClusterName, TenantName, RoleInstanceName, ContainerId, NodeId, VirtualMachineUniqueId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryVmId}`, `{queryContainerId}`

**Signal filters seen in KQL:** `LifecycleState <> "Destroyed"`

---

## Extended Error Details (If Any)

### Get Extended Container Error Details

_Widget purpose:_ Extended Error Details (If Any)

Cluster: `azurecm` · Database: `azurecm` · Type: `Table`
Source panel: `Container Transition > Extended Error Details (If Any)`

```kusto
cluster("azurecm").database("azurecm").LogContainerHealthSnapshot
| where PreciseTimeStamp between(qFrom .. qTo) and containerId == qContainer
| where isnotempty(faultInfo)
| extend faultJson = parse_json(faultInfo)
| extend 
    reason = tostring(faultJson.Reason), 
    correlationId = tostring(faultJson.CorrelationGuid),
    faultTime = tostring(faultJson.Time),
    ExtendedDetails = faultJson.ExtendedDetails
| project PreciseTimeStamp, containerId, nodeId, virtualMachineUniqueId, roleInstanceName, 
    tenantName, reason, correlationId, faultTime, faultJson, ExtendedDetails = faultJson.ExtendedDetails
| summarize arg_max(PreciseTimeStamp, ExtendedDetails) by containerId
| mv-expand row = ExtendedDetails 
| extend Name = tostring(row.Name), Value = tostring(row.Value)
| project Name, Value
| order by Name asc
```

**Params:** `{qFrom}`, `{qTo}`, `{qContainer}`

---
