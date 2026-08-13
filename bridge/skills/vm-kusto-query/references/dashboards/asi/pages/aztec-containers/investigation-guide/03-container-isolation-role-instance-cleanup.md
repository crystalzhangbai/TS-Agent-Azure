# Container Isolation & Role Instance Cleanup

> Source: **Aztec Containers Investigation Guide** dashboard, chapter **Container Isolation & Role Instance Cleanup** (2 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Container Isolation - TMMgmtContainerIsolationStatusEtwTable

### Query TMMgmtContainerIsolationStatusEtwTable

_Widget purpose:_ Container Isolation - TMMgmtContainerIsolationStatusEtwTable

Cluster: `azcore.centralus` · Database: `Fc` · Type: `Table`
Source panel: `Container Isolation & Role Instance Cleanup > Container Isolation - TMMgmtContainerIsolationStatusEtwTable`

```kusto
TMMgmtContainerIsolationStatusEtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where ContainerId == queryContainerId
| project PreciseTimeStamp, Context1, Context2, Message
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`

---

## Role Instance Cleanup Events

### Container Role Instance Cleanup Events

_Widget purpose:_ Role Instance Cleanup Events

Cluster: `azcore.centralus` · Database: `Fc` · Type: `Table`
Source panel: `Container Isolation & Role Instance Cleanup > Role Instance Cleanup Events`

```kusto
LogRoleInstanceCleanupEvent
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where containerId == queryContainerId
| order by PreciseTimeStamp asc
```

**Params:** `{queryContainerId}`, `{queryFrom}`, `{queryTo}`

---
