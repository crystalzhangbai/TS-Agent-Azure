# Container State

> Source: **Aztec Containers Investigation Guide** dashboard, chapter **Container State** (3 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### AggregateState

Cluster: `azurecm` · Database: `AzureCM` · Type: `Filter` · Widget: `Table`
Source panel: `Container State`

```kusto
datatable (Value:string, Description:string)
[
    "StateTransition", "State Transition Only (default)",
    "All", "All"
]
```

---

### Query LogContainerHealthSnapshot by ContainerId

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `Container State`

```kusto
LogContainerHealthSnapshot
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where containerId == queryContainerId
| project PreciseTimeStamp, Tenant, roleInstanceName,  tenantName, containerId, nodeId, 
  containerState, actualOperationalState, containerLifecycleState, containerOsState, containerIsolationState, faultInfo , virtualMachineUniqueId
| order by PreciseTimeStamp asc
| extend flag = case (
  containerState <> prev(containerState) 
  or actualOperationalState <> prev(actualOperationalState) 
  or containerLifecycleState <> prev(containerLifecycleState) 
  or containerOsState <> prev(containerOsState)
  or containerIsolationState <> prev(containerIsolationState)  
  or faultInfo <> prev(faultInfo),
  "changed", "")
| where queryFilter == "All" or (queryFilter != "All" and flag <> "")  
| extend level = case (containerOsState in ("ContainerOsStateUnknown", "ContainerOsStateUnresponsive", "ContainerOsStateUnhealthy"), "critical", 
    containerOsState in ("ContainerOsStateHealthy", "ContainerOsStateProvisioningCompleted"), "info", 
    containerOsState in ("ContainerOsStateInternalShutdown", "ContainerOsStateProvisioningTimedOut", "ContainerOsStateProvisioningRecovery", "ContainerOsStateProvisioningFailed"), "error", 
    "warning")
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryFilter}`, `{queryContainerId}`

**Signal filters seen in KQL:** `queryFilter == "All"`

---

## Role Instance State - LogRoleInstanceSnapshot

### Query LogRoleInstanceSnapshot

_Widget purpose:_ Role Instance State - LogRoleInstanceSnapshot

Cluster: `azcore.centralus` · Database: `Fc` · Type: `Table`
Source panel: `Container State > Role Instance State - LogRoleInstanceSnapshot`

```kusto
set best_effort=true;
LogRoleInstanceSnapshot
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where containerId == queryContainerId
| project PreciseTimeStamp, roleInstanceName, containerId, Tenant, roleState, updateDomain, provisioningState, isExpectedToRun, isNmProgrammingComplete 
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`

---
