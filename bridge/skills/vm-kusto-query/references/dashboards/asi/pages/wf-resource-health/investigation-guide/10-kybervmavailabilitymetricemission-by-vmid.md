# KyberVmAvailabilityMetricEmission by VmId

> Source: **EEE RDOS — WF Resource Health** dashboard, chapter **KyberVmAvailabilityMetricEmission by VmId** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### KyberVmAvailabilityMetricEmissionByVMID

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `APlat` · Type: `Table`
Source panel: `KyberVmAvailabilityMetricEmission by VmId`

```kusto
KyberContainerHealthMetricData
| where PreciseTimeStamp between ((queryFrom - 10d) .. (queryTo + 1h))
| where VirtualMachineUniqueId == queryVmId
| distinct  PreciseTimeStamp, ContainerId,IcHeartbeat,PowerState,HyperVHandshake,HealthUpdateTimeStamp,ApiVersion;
KyberVmAvailabilityMetricEmission
| where PreciseTimeStamp between ((queryFrom - 10d) .. (queryTo + 1h))
| where VirtualMachineUniqueId == queryVmId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryVmId}`

---
