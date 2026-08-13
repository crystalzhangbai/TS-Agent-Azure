# Containers

> Source: **Aztec — Tenant** dashboard, chapter **Containers** (6 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Containers

### AggregateState

_Widget purpose:_ Container Health

Cluster: `azurecm` · Database: `AzureCM` · Type: `Filter` · Widget: `Table`
Source panel: `Containers > Containers > Container Health`

```kusto
datatable (Value:string, Description:string)
[
    "StateTransition", "State Transition Only (default)",
    "All", "All"
]
```

---

### Query LogContainerHealthSnapshot

_Widget purpose:_ Container Health

Cluster: `Azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Containers > Containers > Container Health`

```kusto
LogContainerHealthSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where tenantName == queryTenantName
| where isempty(queryContainerId) or containerId =~ queryContainerId
| project PreciseTimeStamp, Tenant, roleInstanceName,  tenantName, containerId, nodeId, 
  containerState, actualOperationalState, containerLifecycleState, containerOsState, containerIsolationState, faultInfo , virtualMachineUniqueId 
| order by roleInstanceName, PreciseTimeStamp asc
| extend flag = case (
  containerState <> prev(containerState) 
  or actualOperationalState <> prev(actualOperationalState) 
  or containerLifecycleState <> prev(containerLifecycleState) 
  or containerOsState <> prev(containerOsState) 
  or containerIsolationState <> prev(containerIsolationState) 
  or faultInfo <> prev(faultInfo)
  or roleInstanceName <> prev(roleInstanceName),
  "changed", "")
| where queryFilter == "All" or (queryFilter != "All" and flag <> "")  
| extend level = case (containerOsState in ("ContainerOsStateUnknown", "ContainerOsStateUnresponsive", "ContainerOsStateUnhealthy"), "critical", 
    containerOsState in ("ContainerOsStateHealthy", "ContainerOsStateProvisioningCompleted"), "info", 
    containerOsState in ("ContainerOsStateInternalShutdown", "ContainerOsStateProvisioningTimedOut", "ContainerOsStateProvisioningRecovery", "ContainerOsStateProvisioningFailed"), "error", 
    "warning")
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`, `{queryFilter}`, `{queryContainerId}`

**Signal filters seen in KQL:** `queryFilter == "All"`

---

### Container Health

_Widget purpose:_ Container Health Timeline

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Containers > Containers > Container Health Timeline > Container Health Timeline`

```kusto
cluster('azcsupfollower').database('AzureCM').LogContainerHealthSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where tenantName == queryTenantName
| project PreciseTimeStamp, Tenant, roleInstanceName,  tenantName, containerId, nodeId, 
  containerState, actualOperationalState, containerLifecycleState, containerOsState, faultInfo , virtualMachineUniqueId
| project StartTime = PreciseTimeStamp, Content = containerState, containerLifecycleState, Tenant, tenantName, roleInstanceName, containerId, nodeId, virtualMachineUniqueId
| order by roleInstanceName asc, containerId asc, StartTime asc
| extend flag = case (Content <> prev(Content), "changed", containerId <> prev(containerId), "changed", "")
| where flag <> ""
// | where flag <> "" or containerLifecycleState == "Destroyed"
//| where containerLifecycleState <> "Destroyed"
| extend EndTime = case(isnotempty(next(StartTime)) and next(containerId) == containerId, next(StartTime), queryTo)
| extend Health = case (Content in ("ContainerStateUnresponsive", "ContainerStateUnhealthy", "ContainerStateUnknown"), "red", 
  Content == "ContainerStateDestroyed", "Neutral", 
  Content == "ContainerStateStarted", "Healthy", "Degraded")
| extend GroupBy = strcat(roleInstanceName, " - ", containerId)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

**Signal filters seen in KQL:** `containerLifecycleState <> "Destroyed"`

---

### Tenant Containers

_Widget purpose:_ Containers

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Containers > Containers > Containers`

```kusto
LogContainerSnapshot
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where tenantName == queryTenantName
| summarize arg_max(PreciseTimeStamp, *) by subscriptionId, roleInstanceName, virtualMachineUniqueId, nodeId, containerId, creationTime = todatetime(creationTime), updateDomain
| project roleInstanceName, virtualMachineUniqueId, nodeId, containerId, cluster = Tenant, tableDcName = DataCenterName, tableAzName = AvailabilityZone, creationTime, max_PreciseTimeStamp=PreciseTimeStamp, updateDomain
| order by roleInstanceName asc, creationTime asc
```

**Params:** `{queryTenantName}`, `{queryFrom}`, `{queryTo}`

---

### Tenant Instance Count

_Widget purpose:_ Role Instance Count - LogTenantSnapshot

Cluster: `azcsupfollower` · Database: `azurecm` · Type: `TimeSeries`
Source panel: `Containers > Containers > Role Instance Count - LogTenantSnapshot`

```kusto
LogTenantSnapshot
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where tenantName == queryTenantName
| summarize Instances = tolong(max(numRoleInstances)) by bin(PreciseTimeStamp, 5m)
| order by PreciseTimeStamp asc
```

**Params:** `{queryTenantName}`, `{queryFrom}`, `{queryTo}`

---

### RoleState for PaaS Containers

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Timeline`
Source panel: `Containers > Containers > Role State Timeline for PaaS Containers`

```kusto
cluster("azcsupfollower.kusto.windows.net").database("AzureCM").LogRoleInstanceSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where tenantName == queryTenantName
| project PreciseTimeStamp, Tenant, roleInstanceName, roleState, containerId
| order by roleInstanceName asc, containerId asc, PreciseTimeStamp asc
| extend Content = roleState
| extend StartTime = PreciseTimeStamp
| extend flag = case (Content <> prev(Content), "changed", containerId <> prev(containerId), "changed", "")
| where flag <> ""
| extend EndTime = case(isnotempty(next(StartTime)) and next(containerId) == containerId, next(StartTime), queryTo)
| extend Health = case (Content in ("RoleStateUnresponsive", "RoleStateAborted", "RoleStateBusy"), "red", 
  Content in ("RoleStateCreated", "RoleStateStarting", "RoleStateDestroyed", "RoleStateStopping", "RoleStateRecycle"), "Neutral", 
  Content == "RoleStateStarted", "Healthy", "Degraded")
| extend GroupBy = strcat(roleInstanceName, " - ", containerId)
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryTenantName}`

---
