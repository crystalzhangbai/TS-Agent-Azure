# Support Area Path Catalog

> ⚠️ **Single source of truth** for SME team → Support Area Path mapping lives at:
> `support-area-path-map.md`
>
> Do NOT duplicate the table here. This file is for **scope-decision metadata** — which paths are in/out of VM scope, owning team, common keywords, and "when to suggest this path" tips.

---

## In-scope VM/Storage paths — scope classification

| SAP (short) | In VM Scope? | Common Trigger Keywords | When to suggest |
|---|---|---|---|
| XStore Triage | ✅ Yes | disk blackout, storage server fault, disk unavailable | Disk I/O failure clearly at storage fabric layer; Kusto shows XStore errors |
| Host Networking Triage | ✅ Yes | VFP drops, AccelNet anomaly, host NIC, RDMA | VM loses network from host NIC / VFP perspective; not a guest OS network config issue |
| ANP | ✅ Yes | node anomaly, node diagnostics, unexplained reboot | Node-level behavior not explained by HW or storage fault |
| Hardware Triage | ✅ Yes | WHEA, SEL, MCE, hardware fault, memory error | RCA confirms HardwareFault; platform events show HW-level failure |
| Compute Manager | ✅ Yes | VM lifecycle, allocation, VM start/stop/delete | CRP-level allocation failure, lifecycle operations broken |
| CRP / Resource Provider | ✅ Yes | allocation failure, CRP API error, 503 on VM create | ARM → CRP layer errors on VM provision/resize |
| Disks RP | ✅ Yes | managed disk provisioning, disk create/delete fails | Disk-level lifecycle; not I/O performance inside VM |
| Azure Boost / ASAP | ✅ Yes | NVMe, Azure Boost, stornvme, controller reset | Event 129, NVMe timeout, ASAP-specific counters |
| Azure Files Sync | ✅ Yes | AFS sync, file share sync error, cloud endpoint | Azure File Sync agent errors, sync session failures |

---

## Out-of-scope paths — scope classification

| SAP (short) | In VM Scope? | Common Trigger Keywords | When to suggest |
|---|---|---|---|
| AKS Cluster Operations | ❌ No (AKS) | AKS cluster, node pool, cluster operations | AKS-level scheduler or control plane issue; VM team only if underlying VM allocation fails |
| AKS Autoscaler | ❌ No (AKS) | cluster autoscaler, scale-out failure, node scaling | Node count scaling logic; not VM allocation |
| Network Connectivity Triage | ❌ No (Network) | Express Route, vWAN, VPN gateway, BGP | Pure network routing/peering issue; no VM platform involved |
| Application Gateway Triage | ❌ No (Network) | AppGW, WAF, backend health, 502/504 | AppGW layer issues |
| Load Balancer Triage | ❌ No (Network) | SLB, backend health, load balancing rules | SLB layer issues |
| Azure VM Backup Triage | ❌ No (Backup) | Azure Backup, recovery point, backup vault, MARS | Backup job failures, RPO/RTO; VM team only if snapshot causes disk I/O |
| Azure Site Recovery Triage | ❌ No (ASR) | ASR, replication, failover, DR drill | Replication/failover issues |
| SQL on VM (joint) | ⚠️ Joint | SQL Server on VM, SQL query slow, SQL deadlock | SQL team owns SQL layer; escalate to VM if disk I/O / memory at platform level |
| SAP on VM (joint) | ⚠️ Joint | SAP HANA, HSR, SAP cluster, pacemaker | SAP team owns app layer; VM team if host/node fault detected |
| Container Apps Triage | ❌ No (Containers) | Container Apps, KEDA, Dapr | Container Apps team |
| Functions Triage | ❌ No (Functions) | Azure Functions, function app runtime | Functions team |

---

## Usage notes

- For the **full cascading path strings** (needed when the user navigates the DFM Support Area Path tree manually), always fetch from the canonical source:
  `@reference support-area-path-map.md`
- This file provides **routing verdict** (in/out of scope) and **trigger keywords**. Do not copy SAP strings here.
- When a new SAP path is discovered, add a row to the canonical map first, then add scope-classification metadata here.
