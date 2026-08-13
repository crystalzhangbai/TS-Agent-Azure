# VMs Availability (AIR-R)

> Source: **Azure Subscription Investigation Guide** dashboard, chapter **VMs Availability (AIR-R)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Azure Host Subscription AIR-R

_Widget purpose:_ VMs Availability (AIR-R)

Cluster: `vmainsight` · Database: `vmadb` · Type: `Table`
Source panel: `VMs Availability (AIR-R)`

```kusto
VMA_NRT
| where PreciseTimeStamp between (queryFrom .. queryTo) and Subscription == subId
        and RCA !contains "CustomerInitiated"
| distinct StartTime, EndTime, RoleInstanceName, ContainerId, NodeId, RCA
```

**Params:** `{queryFrom}`, `{queryTo}`, `{subId}`

---
