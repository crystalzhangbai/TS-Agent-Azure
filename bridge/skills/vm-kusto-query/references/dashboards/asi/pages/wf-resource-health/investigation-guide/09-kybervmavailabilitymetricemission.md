# KyberVmAvailabilityMetricEmission

> Source: **EEE RDOS — WF Resource Health** dashboard, chapter **KyberVmAvailabilityMetricEmission** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Represents Kyber emitted metric values

### KyberVmAvailabilityMetricEmission

_Widget purpose:_ Represents Kyber emitted metric values

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `Aplat` · Type: `Table`
Source panel: `KyberVmAvailabilityMetricEmission > Represents Kyber emitted metric values`

```kusto
KyberVmAvailabilityMetricEmission
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where ContainerId == containerId
| project PreciseTimeStamp, ContainerId, VirtualMachineUniqueId, ArmId, IsPeriodic, MetricValue, LastHealthStateChangeTime, LastHealthUpdateTime, TMContainerTimestamp
```

**Params:** `{queryFrom}`, `{queryTo}`, `{containerId}`

---
