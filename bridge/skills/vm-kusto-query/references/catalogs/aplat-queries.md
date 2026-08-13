# APlat / Kyber Queries — VM Availability Metric Pipeline

Cluster: `aplat.westcentralus.kusto.windows.net`
Database: `APlat`

> **Scope**: The "VM Availability Metric" exposed in Azure Portal (preview) is emitted by **Kyber CoreService** running on the Service Fabric `APlat` cluster. The four tables below let you trace a missing-metric report from the customer's portal view all the way back to the host node's `RdAgentAzPubSubEtwTable`.
>
> **Service instance gotcha**: `ServiceName == "fabric:/Kyber/Kyber.CoreService"` is instance 0. For other instances append `/<N>` (e.g., `fabric:/Kyber/Kyber.CoreService/2` = instance 3, 0-indexed). When you don't know the instance, use `ServiceName contains "fabric:/Kyber/Kyber.CoreService"`.
>
> **Standard variables**: `{TenantName}` (e.g., `koreacentral-prod-a`), `{ContainerId}`, `{NodeId}`, `{VMId}` (VirtualMachineUniqueId), `{StartTime}`, `{EndTime}` (UTC).

---

## KyberContainerHealthMetricData — Per-container metric emission status

Confirms whether Kyber actually generated availability metric rows for the container in the reported window. Normal cadence ≈ one row every 2 minutes 30 seconds; gaps indicate the pipeline stopped.

```kusto
let st = datetime({StartTime});
let et = datetime({EndTime});
cluster("aplat.westcentralus.kusto.windows.net").database("APlat").KyberContainerHealthMetricData
| where Tenant == "{TenantName}"
| where PreciseTimeStamp between (st .. et)
| where ServiceName contains "fabric:/Kyber/Kyber.CoreService"
| where ContainerId == "{ContainerId}"
| project PreciseTimeStamp, ContainerId, ServiceName, IcHeartbeat, PowerState, HyperVHandshake, HealthUpdateTimeStamp, ApiVersion
| order by PreciseTimeStamp asc
```

Interpretation:
- No rows or > 5-minute gaps → metric pipeline stalled at Kyber → escalate (see § Escalation below).
- Rows present but `IcHeartbeat`/`HyperVHandshake` flapping → guest agent / Hyper-V IC issue, not a metric-pipeline bug.

## RdAgentAzPubSubEtwTable — Upstream enqueue from host RDAgent

Confirms the host RDAgent actually published `ResourceHealthEvents` for the container. If this is empty, the pipeline broke *before* Kyber — focus on the host node.

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").RdAgentAzPubSubEtwTable
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where NodeId == "{NodeId}"
| where Message contains "AzureCompute.Node.ResourceHealthEvents"
| where Message contains "{ContainerId}"
| project PreciseTimeStamp, Region, Cluster, NodeId, Message, Level
| order by PreciseTimeStamp asc
```

Interpretation:
- Empty → RDAgent didn't publish (host-side); check node health, RDAgent crash, AzPubSub queue backlog.
- Present → events left the host fine → bottleneck is downstream (Kyber consume / emission).

## KyberVmAvailabilityMetricEmissionSkipped — Why Kyber chose not to emit

When Kyber received the event but decided to skip emission (stale data, dedup, version mismatch, etc.), it logs the reason here. This is the highest-signal table for "metric is missing for *this specific window*" scenarios.

```kusto
let st = datetime({StartTime});
let et = datetime({EndTime});
cluster("aplat.westcentralus.kusto.windows.net").database("APlat").KyberVmAvailabilityMetricEmissionSkipped
| where Tenant == "{TenantName}"
| where PreciseTimeStamp between (st .. et)
| where ServiceName contains "fabric:/Kyber/Kyber.CoreService"
| where ContainerId == "{ContainerId}"
| project PreciseTimeStamp, ContainerId, ServiceName, Reason
| order by PreciseTimeStamp asc
```

Interpretation:
- `Reason contains "stale"` → data older than the freshness threshold; check time-sync on host + RDAgent enqueue lag (Q2).
- `Reason contains "dedup"` or `"version"` → expected dedup behavior; portal display issue is the actual gap.
- Empty + Q1 also empty → Kyber never received it → focus on Q2 (RDAgent enqueue).

## KyberVmAvailabilityMetricEmission — Cross-check emitted volume

Counts distinct VMs Kyber emitted metric for, per minute. Use as a sanity-check: if this is also flat or zero in the window, the issue is platform-wide for that `{TenantName}` (cluster outage / Kyber service unhealthy), not customer-specific.

```kusto
let st = datetime({StartTime});
let et = datetime({EndTime});
cluster("aplat.westcentralus.kusto.windows.net").database("APlat").KyberVmAvailabilityMetricEmission
| where Tenant == "{TenantName}"
  and PreciseTimeStamp between (st .. et)
  and ServiceName contains "fabric:/Kyber/Kyber.CoreService"
| summarize dcount(VirtualMachineUniqueId) by bin(PreciseTimeStamp, 1m)
| render timechart
```

Interpretation:
- Tenant-wide drop to 0 → Kyber service issue, not VM-specific → escalate to EEE Host Node.
- Tenant-wide normal but customer VM missing → narrow with Q1 + Q3 above.

---

## Escalation

After running Q1–Q4:
- **All four clean** → portal display / customer scope / time-range issue.
- **Q1 empty, Q2 present, Q3 has rows with "stale"** → enqueue → consume lag; engage EEE Host Node (formerly EEE RDOS) after TA discussion.
- **Q2 empty** → host-side (RDAgent / AzPubSub queue) → EEE Host Node.
- **Q4 tenant-wide flat** → Kyber CoreService unhealthy → EEE Host Node, attach `{TenantName}` and time window.

**Expectation setting**: VM Availability Metric is a **preview feature** — fix priority and ETA are limited.

References:
- TSG: [VM Availability Metric missing_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FVM-Availability-Metric-missing_Perf)
- Background: [No VM Availability Metric Emissions from Kyber — Overview](https://dev.azure.com/msazure/AzureWiki/_wiki/wikis/AzureWiki.wiki/433356/No-VM-Availability-Metric-Emissions-from-Kyber)
