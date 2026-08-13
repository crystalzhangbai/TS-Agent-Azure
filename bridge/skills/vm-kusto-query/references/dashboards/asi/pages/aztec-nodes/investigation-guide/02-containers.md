# Containers

> Source: **Aztec Nodes Investigation Guide** dashboard, chapter **Containers** (3 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Containers

### Node container counts

_Widget purpose:_ Container Time Series

Cluster: `azurecm` · Database: `AzureCM` · Type: `TimeSeries`
Source panel: `Containers > Containers > Container Time Series`

```kusto
LogNodeSnapshot
| where PreciseTimeStamp between(qFrom .. qTo)
| where isnotempty(qNodeId) and nodeId == qNodeId
| summarize 
    containers = max(toint(containerCount)), 
    aliveContainers = max(toint(aliveContainerCount)) 
    by bin(PreciseTimeStamp, 5m)
| order by PreciseTimeStamp asc
```

**Params:** `{qFrom}`, `{qTo}`, `{qNodeId}`

---

### Host Node Container Timeline

_Widget purpose:_ Container Timeline

Cluster: `azcore.centralus` · Database: `AzureCP` · Type: `Timeline`
Source panel: `Containers > Containers > Container Timeline`

```kusto
cluster('azcore.centralus').database('AzureCP').MycroftContainerSnapshot
| where PreciseTimeStamp between(qFrom .. qTo) and NodeId == qHostNode
| project PreciseTimeStamp, NodeId, ContainerId, VirtualMachineUniqueId, RoleInstanceName, CreationTime
| extend StartTime = PreciseTimeStamp
| order by CreationTime asc, StartTime asc 
| where (ContainerId != next(ContainerId) or ContainerId != prev(ContainerId)) 
| extend EndTime = next(StartTime)
| where ContainerId != prev(ContainerId)
| extend Content = ContainerId
| extend Tooltip = strcat(
    Content,
    "<br/>Node: ", NodeId
)
| extend EndTime = iif(isnull(EndTime), datetime_add('minute', 5, StartTime), EndTime)
| extend GroupBy = ContainerId
| project StartTime, EndTime, Content, Tooltip, GroupBy
```

**Params:** `{qFrom}`, `{qTo}`, `{qHostNode}`

---

## Table View

### Node Containers

_Widget purpose:_ Containers

Cluster: `azurecm` · Database: `AzureCM` · Type: `Table`
Source panel: `Containers > Table View > Containers`

```kusto
LogContainerSnapshot
| where PreciseTimeStamp between(global_startTime..global_endTime)
| where nodeId == queryNodeId
| summarize take_any(nodeId, containerId, containerType, creationTime, roleInstanceName, tenantName, virtualMachineUniqueId) by containerId
| extend creationTime = todatetime(creationTime)
| order by creationTime desc
```

**Params:** `{queryNodeId}`

---
