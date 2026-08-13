# VmHealthRawStateEtwTable

> Source: **EEE RDOS — WF Resource Health** dashboard, chapter **VmHealthRawStateEtwTable** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### VmHealthRawStateEtwTable_ResourceHealth DS

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `VmHealthRawStateEtwTable`

```kusto
VmHealthRawStateEtwTable
| where VirtualMachineUniqueId =~ query_VMId
| where PreciseTimeStamp >= query_StartTime and PreciseTimeStamp <= query_EndTime
| project PreciseTimeStamp, Cluster, VmHyperVIcHeartbeat, VmPowerState, HasHyperVHandshakeCompleted, IsVscStateOperational, Context, VirtualMachineUniqueId, NodeId, NodeIdentity
```

**Params:** `{query_StartTime}`, `{query_EndTime}`, `{query_VMId}`

---
