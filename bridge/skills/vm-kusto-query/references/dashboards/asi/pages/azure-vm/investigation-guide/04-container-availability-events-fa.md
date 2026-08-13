# Container Availability Events (Fa)

> Source: **Azure Host - Azure VM** dashboard, chapter **Container Availability Events (Fa)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## ContainerAvailabilityImpactingEtwTable

### Azure Host VM Container Availability Impacting Events

_Widget purpose:_ ContainerAvailabilityImpactingEtwTable

Cluster: `azcore.centralus` · Database: `Fa` · Type: `Table`
Source panel: `Container Availability Events (Fa) > ContainerAvailabilityImpactingEtwTable`

**Tables:** `ContainerAvailabilityImpactingEtwTable`
**Output columns:** `PreciseTimeStamp`, `ProviderName`, `NodeId`, `ContainerId`, `ActivityType`, `ActivityDetails`

```kusto
ContainerAvailabilityImpactingEtwTable
| where PreciseTimeStamp between (_startTime.._endTime) and VmId == _vmId
| project PreciseTimeStamp, ProviderName, NodeId, ContainerId, ActivityType, ActivityDetails
| sort by PreciseTimeStamp
```

**Params:** `{_startTime}`, `{_endTime}`, `{_vmId}`

---
