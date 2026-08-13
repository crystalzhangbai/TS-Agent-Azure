# Playbook C — Performance / ASAP / Throttling (Deep)

> **Purpose**: TSG-by-TSG router for the `/SME Topics/Performance/*` family on csswiki AzureIaaSVM. Use this **after** Step 2/3 of [`playbook-C-performance-core.md`](playbook-C-performance-core.md) has classified the symptom.
>
> **Why router style**: ~80% of the perf TSGs are dashboard panel walkthroughs (EEE Host Node, ASI Storage, Geneva VM Dashboard). KQL bodies were backfilled into the per-cluster reference files during Stage 4 of the references restructure. This playbook tells you **which section of which file to open + which panel to screenshot**, not what to type.
>
> **Source TSGs** (csswiki AzureIaaSVM `/SME Topics/Performance/TSGs`, audited 2026-06-05 — **all 42 wiki TSGs covered**) + custom chapters from internal RCA experience:
>
> Already covered prior to 2026-06-05:
>
> - Troubleshooting Missing Shoebox Disk Metrics_Perf — STG-Perf-1
> - Datapath Update Impact_Perf — STG-Perf-3
> - VhdDiskPrt Event 16 Investigation_Perf + VhdDiskPr Event 2 and 3_Perf — STG-Perf-4.Q1/Q2
> - Poor IO Performance on Windows Server 2012 R2_Perf — STG-Perf-4.Q5
> - AirDiskBlip BlobCache Write during Congestion_Perf — STG-Perf-5
> - VM Availability Metric missing_Perf + Unhealthy VM Status in Azure Portal Despite Normal Functionality_Perf — STG-Perf-7
> - Excessive Network Out Usage_Perf — NET-Perf-2
> - Available Memory shows 0GB_Perf — MEM-Perf-1
>
> Added 2026-06-05 backfill (32 TSGs):
>
> - **GPU (6)**: NC and NV-series Virtual Machines_Perf, Linux N-Series VMs Not Detecting GPUs_Perf, Linux GPU Nvidia Slow_Perf, Windows GPU CUDA_Perf, Graphics Application not using NV GPU_Perf, Zooming_slow_In_RDP_GPU_Perf
> - **CPU (3)**: Troubleshoot High CPU_Perf, CPU SKU Clock difference_Perf, Incorrect CPU Core Hyperthreading_Perf
> - **Compute hang (1)**: Troubleshoot VM Hung or Frozen_Perf
> - **Memory (5)**: Low Memory Windows Troubleshooting_Perf, 2GB Low Memory Windows Troubleshooting_Perf, Reserved Memory 2gb windows_perf, Memory Hardware Reserved in Windows_Perf, Available Memory 50MB Less TrustedVM_Perf
> - **Storage / Disk (8)**: Disk Cache_Perf, Host Caching Not Enabled_Perf, Disk Latency Counter Not Available NVME Controller_Perf, VhdDiskPr Event 47 Investigation_Perf, Queue Depth constantly 1_Perf, Enabling Performance Plus_Perf, Troubleshooting Disk using ASI_Perf, Troubleshooting Ultra and PremiumV2 Disks using Tenant Health Dashboard_Perf
> - **Network (1)**: Host Networking Updates_Perf
> - **Tools / Perf Insights (3)**: Managed Identities Support in Performance Diagnostics_Perf, Perf Inisghts - KeyBasedAuthenticationNotPermitted_Perf, Performance InformationMessage OnDisk Page_Perf
> - **Misc (3)**: AzCLI Commands Slow Docker Container_Perf, Discrepancy between VM & Portal Metrics_Perf, VM SKU Cached Limits_Perf
> - **Linux guest (2)**: NVMe troubleshooting_Linux, OOM Killer Linux_Perf
>
> Custom chapters (NOT in csswiki Perf TSG list — added from internal RCA experience):
>
> - **§ ASAP** — AMD v6/v7 + Boost-for-Storage NVMe controller reset (`asap-storage-queries.md` router)
> - **§ Throttling** — VM disk throttle (Geneva Shoebox %), VM SKU cached/uncached limits, storage account 429 / ServerBusy, Azure Files metadata throttle
>
> **Convention**: `{NodeId}`, `{ContainerId}`, `{StartTime}`, `{EndTime}`, `{SubscriptionId}`, `{VMName}`, `{VMId}`, `{TenantName}` — UTC throughout.

---

## TOC

- **§ STG-Perf — Storage / Disk perf** (15 sections)
  - STG-Perf-1: Missing disk metrics (ABC host config — short path)
  - STG-Perf-2: Disk colocation verification (premium MD)
  - STG-Perf-3: Storage Datapath (DPP) cut-over impact
  - STG-Perf-4: Local cache disk burst (VhdDiskPrt Event 16) + Event 504 srbstatus=5 + WS2012R2 IDE-mode (EventId 12817)
  - STG-Perf-5: Blob cache write congestion (BSPausedWrites)
  - STG-Perf-6: XStore / XArgus account-level latency
  - STG-Perf-7: VM Availability Metric missing (Kyber pipeline)
  - STG-Perf-8: Disk Cache (host caching policy)
  - STG-Perf-9: Host Caching Not Enabled
  - STG-Perf-10: Disk Latency counter not available on NVMe Controller
  - STG-Perf-11: VhdDiskPr Event 47 investigation
  - STG-Perf-12: Queue Depth constantly 1
  - STG-Perf-13: Enabling Performance Plus (disk burst)
  - STG-Perf-14: Troubleshooting Disk using ASI (dashboard pointer)
  - STG-Perf-15: Ultra / PremiumV2 Disks via Tenant Health Dashboard
- **§ NET-Perf — Network perf** (3 sections)
  - NET-Perf-1: Host pingmesh latency anomalies
  - NET-Perf-2: Excessive outbound + metric discrepancy (likely VM breach / SYN flood)
  - NET-Perf-3: Host Networking Updates impact
- **§ CPU-Perf — CPU perf** (4 sections)
  - CPU-Perf-1: Noisy-neighbor / host CPU contention
  - CPU-Perf-2: Troubleshoot High CPU (in-guest)
  - CPU-Perf-3: CPU SKU clock difference (base vs boost)
  - CPU-Perf-4: Incorrect CPU core / hyperthreading reporting
- **§ MEM-Perf — Memory perf** (6 sections)
  - MEM-Perf-1: "Available Memory" metric missing in portal (Windows guest)
  - MEM-Perf-2: Low Memory Windows (general)
  - MEM-Perf-3: 2GB Low Memory Windows
  - MEM-Perf-4: Reserved Memory 2GB Windows
  - MEM-Perf-5: Memory Hardware Reserved in Windows
  - MEM-Perf-6: Available Memory 50MB Less on TrustedVM
- **§ HANG — Compute hang** (1 section)
  - HANG-Perf-1: Troubleshoot VM Hung or Frozen
- **§ GPU-Perf — GPU perf** (6 sections)
  - GPU-Perf-1: NC / NV-series VM intro and SKU pick
  - GPU-Perf-2: Linux N-Series VMs not detecting GPUs
  - GPU-Perf-3: Linux GPU Nvidia driver slow
  - GPU-Perf-4: Windows GPU CUDA setup
  - GPU-Perf-5: Graphics Application not using NV GPU (Windows DirectX)
  - GPU-Perf-6: Zooming slow in RDP over GPU
- **§ LM-Perf — Live Migration perf**
  - LM-Perf-1: LM-induced freeze / post-LM slowness
- **§ MAINT-Perf — Maintenance perf**
  - MAINT-Perf-1: Host update / VMPHU window
- **§ ASAP — SmartNIC / Boost-for-Storage NVMe** (AMD v6/v7 + other Boost SKUs)
  - ASAP-Perf-1: NVMe Controller Reset — canonical probe (when platform tables clean but guest hangs)
  - ASAP-Perf-2: Per-disk ASAP counters (latency, IOPS/BPS, exceptions)
  - ASAP-Perf-3: Node-level ASAP health (missed sample windows)
- **§ Throttling — quota / rate limits**
  - THR-Perf-1: VM disk throttle (Geneva Shoebox VM Cached/UnCached IOPS% + BW%)
  - THR-Perf-2: VM SKU cached / uncached / network limits reference
  - THR-Perf-3: Storage account 429 / ServerBusy / account-level throttle
  - THR-Perf-4: Azure Files metadata throttle
- **§ TOOL-Perf — Perf Insights / Performance Diagnostics extension** (3 sections)
  - TOOL-Perf-1: Managed Identities support in Performance Diagnostics
  - TOOL-Perf-2: Perf Insights — KeyBasedAuthenticationNotPermitted
  - TOOL-Perf-3: Performance InformationMessage OnDisk page interpretation
- **§ MISC-Perf — Misc** (3 sections)
  - MISC-Perf-1: AzCLI commands slow inside Docker container
  - MISC-Perf-2: Discrepancy between VM and Portal metrics
  - MISC-Perf-3: VM SKU cached limits lookup
- **§ OS-Perf-Linux — Linux guest** (delegates)
  - OS-Perf-Linux-1: NVMe troubleshooting (Linux guest)
  - OS-Perf-Linux-2: OOM Killer (Linux guest)
- **§ GUEST — Guest OS perf** (out-of-scope — delegate)

---

# § STG-Perf — Storage perf

## STG-Perf-1: Missing disk metrics (ABC host config)

> **TSG**: `/SME Topics/Performance/Disk Metrics_Perf`
> **Scope**: "Why don't I see disk utilization counters in the portal for my standard-storage VM?"
> **Verdict in 1 query.** This is the short path — most cases close here without further investigation.

### STG-Perf-1.Q1 — ABC detection on the host

See [`azurecm-queries.md`](../catalogs/azurecm-queries.md) → **LogNodeSnapshot — ABC (Azure Blob Cache) host configuration detection**.

```kusto
cluster('Azcsupfollower').database('AzureCM').LogNodeSnapshot
| where nodeId == "{NodeId}" and PreciseTimeStamp > ago(2h)
| distinct diskConfiguration
```

| Output | Action |
|---|---|
| `AllDisksAbc` | ABC enabled — metrics SHOULD appear. Check portal time range / customer scope. If still missing → escalate (rare path: metric pipeline issue). |
| `AllDisksInStripe` | Pure standard host — ABC disabled — metrics correctly absent. Close case with TSG link below + offer "stop-deallocate + start" to land on an ABC host. |

### STG-Perf-1.Customer-facing wording

> "Your VM is currently placed on a host node that runs pure standard-storage backend (no Azure Blob Cache layer). Disk-utilization counters (read/write IOPS, latency) are sourced from the ABC layer and are therefore not emitted for VMs on this host class — this is expected platform behavior, not a bug or outage. If you stop-deallocate the VM and then start it again, the next allocation may land on a mixed-storage (ABC-enabled) host, after which the counters will start appearing. The behavior is documented in our internal TSG: [Disk Metrics_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/Disk-Metrics_Perf)."

---

## STG-Perf-2: Disk colocation verification (premium managed disk)

> **TSG**: `/SME Topics/Performance/Disk Collocation_Perf`
> **Scope**: Customer expects "Premium Managed Disk Performance Optimization" (~2 ms write / ~3 ms read) but sees 5-10 ms. Was the VM's premium MD actually placed on the same network spine as the VM?

### STG-Perf-2.Q1 — Verify colocation status

See [`crp-queries.md`](../catalogs/crp-queries.md) → **VMApiQosEvent — Disk colocation verification (Premium Managed Disk)**. Returns `colocationStatus` from `extraVMProperties.ColocationSkipDetails`.

### STG-Perf-2.Q2 — Investigate allocation failures involving colocation

If the VM start/redeploy operation itself failed and you suspect spine capacity, see [`crp-queries.md`](../catalogs/crp-queries.md) → **VMApiQosEvent + AlertingEvent — Colocation allocation failures**.

### STG-Perf-2.Interpretation

| `colocationStatus` | Meaning | Customer action |
|---|---|---|
| `Colocation succeeded` + non-empty `networkSpineIds` | Premium MD is on same spine as VM | Latency >2 ms is NOT a colocation issue — investigate XArgus / XStore tenant (STG-Perf-6). |
| `Colocation skipped and normal allocation succeeded` | Allocated, but not on the optimized spine | Check `colocationSkipDetailsReason`. **Workaround:** stop-deallocate then start; this re-evaluates colocation for the existing premium MDs. |
| `N/A` | Old/incomplete event row | Trigger a stop-start to generate a fresh `VMApiQosEvent` and re-query. |

### STG-Perf-2.Escalation

- `colocationStatus = "Colocation was skipped but operation still failed"` with `alertCode` containing `networkspine` → **WACAP** team (capacity).
- Other colocation failures → standard CRP escalation.
- TSG: [Disk Collocation_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/Disk-Collocation_Perf).

---

## STG-Perf-3: Storage Datapath (DPP) cut-over impact

> **TSG**: `/SME Topics/Performance/Datapath Update Impact_Perf`
> **Scope**: Customer reports a single ~5-15 s disk-IO freeze ("random N-second blip"); the underlying cause is a per-node storage datapath (DPP = DataPath Plugin) version cut-over. Compute is unaffected (`ComputeImpact: "None"`, `DiskImpact: "Freeze"`, `EstimatedImpactDurationInSeconds: 9`).

### STG-Perf-3.Q1 — Was there a DPP cut-over on this node in the window?

See [`azurecm-queries.md`](../catalogs/azurecm-queries.md) → **ServiceVersionSwitch — Storage Datapath (DPP) updates on a node**. Filter `NewVersion contains 'Datapath'`. Sample old→new: `Datapath_7_10_0_94_153_10_0_94` → `Datapath_7_10_0_173_153_10_0_173`.

### STG-Perf-3.Q2 — Confirm the AzPE impact payload

See [`operations-queries.md`](../catalogs/operations-queries.md) → **AzPEWorkflowEvent — Storage Datapath (DPP) update impact monitor**. Expected payload in `WorkflowEventData.ImpactInformation.Impact.Value`:

```json
{ "DiskImpact": "Freeze", "ComputeImpact": "None", "EstimatedImpactDurationInSeconds": 9 }
```

### STG-Perf-3.Q3 — Region rollout progress for the target build

See [`operations-queries.md`](../catalogs/operations-queries.md) → **GetSimpleDeploymentProgress() — Region-level rollout summary**. Pass the target build label and a region list to report `Complete | InRollout | Remaining | Total | CompletionPercentage` per region.

### STG-Perf-3.Customer-facing wording

> "Between {StartTime} and {EndTime}, your host node received a storage-datapath version update (DPP). This is a routine in-place rollout that pauses disk IO for approximately 9 seconds while the new datapath binary takes over; compute (CPU/memory) is unaffected. Workloads that cannot tolerate this brief pause can subscribe to the IMDS Scheduled Events API to receive advance notice and drain, or — for perf-critical VMs — request VMPHU disablement (some limitations apply). The current rollout status of the target build in your region is {CompletionPercentage}%. TSG: [Datapath Update Impact_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/Datapath-Update-Impact_Perf)."

---

## STG-Perf-4: Local cache disk burst / sustained-IO slow

> **TSG**: `/SME Topics/Performance/Local Disk Investigation_Perf` (covers VhdDiskPrt Event 2/3/16 + Windows Event 504 srbstatus=5 + Event 505 latency histogram)
> **Scope**: Premium VMs on ABC hosts where the underlying local cache disk burst-rate or sustained-IO limits are saturated, leaking back as IO latency to guest.

### STG-Perf-4.Q1 — VhdDiskPrt Event 16 burst overrun

See [`azcore-queries.md`](../catalogs/azcore-queries.md) → **OsVhddiskEventTable — VhdDiskPrt Event 2/3/16 binary data parse** (compact form for Event 16). Event 16 = burst-credit overrun on the cache disk.

### STG-Perf-4.Q2 — VhdDiskPrt Event 2/3 sustained-IO drop

Same reference → full-form query with all 16 `ParamBinary1` substring slots. Event 2 = sustained IO slow, Event 3 = sustained IO dropped.

### STG-Perf-4.Q3 — Windows Event 504 (srbstatus=5) on host

See [`azcore-queries.md`](../catalogs/azcore-queries.md) → **WindowsEventTable** with the extended-EventId tip line; filter `EventId == 504 and Description contains "srbstatus 5"`. srbstatus=5 = `SRB_STATUS_BUSY`, i.e. host disk returned busy to the storage port.

### STG-Perf-4.Q4 — Windows Event 505 latency histogram parsing

See [`azcore-queries.md`](../catalogs/azcore-queries.md) → **WindowsEventTable — Event 505 local disk latency histogram parsing**. Each row = histogram of local disk IO latency buckets for one 5-minute window.

### STG-Perf-4.Q5 — WS2012R2 IDE-mode resource VHD slow I/O (EventId 12817)

Only applies when the guest is **Windows Server 2012 R2** and is sustained `<10 MB/s` on the resource (temp) VHD. Host raises `EventId 12817` indicating the VM dropped to the IDE path instead of the SCSI/VSP path.

See [`azcore-queries.md`](../catalogs/azcore-queries.md) → **WindowsEventTable — EventId 12817 (WS2012R2 IDE-mode resource VHD slow I/O)** for both per-node and subscription-wide sweep forms. Mitigation: WS2012R2 is end-of-extended-support — guidance is to upgrade to WS2016+. No host-side fix exists.

### STG-Perf-4.Interpretation

- **Event 16 only** → burst-credit issue → customer should size up (P-tier with higher burst, or move to Ultra/v6+).
- **Event 2/3 + Event 504 srbstatus=5** → host cache disk struggling → check `DiskHealthRawStateEtwTable` for HW; if disk is healthy, this is host overcommit → § CPU/MEM-Perf cross-check.
- **Event 505 histogram tail (>50 ms buckets non-zero)** → cache disk tail latency → match with STG-Perf-5 if writes are involved.

---

## STG-Perf-5: Blob cache write congestion (BSPausedWrites)

> **TSG**: `/SME Topics/Performance/Blob Cache Write Congestion_Perf` (embedded in azcore)
> **Scope**: Write-heavy premium workload on ABC. ABC pauses guest writes when it can't drain to backend fast enough → `BSPausedWrites` counter increments. Latency leaks to guest as IO completion stalls.

### STG-Perf-5.Q1 — BSPausedWrites counter on this node

See [`azcore-queries.md`](../catalogs/azcore-queries.md) → **OsBlobCacheInternalCounterTable — Blob cache write congestion / paused-writes counter**.

### STG-Perf-5.Q2 — Correlate with backend (XStore tenant)

See [`storage-account-queries.md`](../catalogs/storage-account-queries.md) → **XArgus section** (`TenantPerfPercentiles5M`) for tenant-side write throughput at the same window. If tenant is at server-busy / throttle threshold → backend root cause.

### STG-Perf-5.Interpretation

- **BSPausedWrites > 0 + XStore tenant healthy** → ABC node-local write back-pressure → check host load (§ CPU/MEM-Perf). Possible mitigation: customer reduces write bursts or moves to v6+/NVMe-direct.
- **BSPausedWrites > 0 + XStore tenant throttled** → backend storage account hot → § STG-Perf-6.

---

## STG-Perf-6: XStore / XArgus account-level latency

> **Scope**: Account-level deep dive when the cache/host layer is clean.

### STG-Perf-6.Q1 — XArgus account percentile latency

See [`storage-account-queries.md`](../catalogs/storage-account-queries.md) → **XArgus section**: `AccountPerfPercentiles5M` and `TenantPerfPercentiles5M` for P50/P90/P99 by 5-minute bin.

### STG-Perf-6.Q2 — XStore disk blackout / failure triage

See [`storage-account-queries.md`](../catalogs/storage-account-queries.md) → **XStore Disk Triage section**: `XHealth_DiskBlackoutXStoreTriage`, `XHealth_DiskFailureXStoreTriage`.

### STG-Perf-6.Q3 — Throttling (429 / ServerBusy)

See [`storage-account-queries.md`](../catalogs/storage-account-queries.md) → **Throttling section** (`StorageOperations` macro on `armprodgbl`). If the account is hitting per-account or per-partition limits, this is the root.

### STG-Perf-6.Escalation

Backend issue confirmed → escalate to **XStore** (EEE Storage) by opening an ICM manually via ASC (Escalate ticket); include storage account name, tenant, time window, percentile evidence, blackout/triage hits.

---

## STG-Perf-7: VM Availability Metric missing (Kyber pipeline)

> **TSG**: `/SME Topics/Performance/TSGs/VM Availability Metric missing_Perf`
> **Scope**: Customer reports the **VM Availability Metric** (Azure Portal → VM → Monitor) is missing or has gaps. Preview-feature metric emitted by **Kyber CoreService** on the `aplat` Service Fabric cluster. Fix priority is limited (preview).
>
> **Required inputs**: `{SubscriptionId}`, `{ContainerId}`, `{NodeId}`, `{VMId}` (VirtualMachineUniqueId), `{TenantName}` (e.g., `koreacentral-prod-a`), `{StartTime}`, `{EndTime}`.

### STG-Perf-7.Q1 — Did Kyber emit metric rows for this container?

See [`aplat-queries.md`](../catalogs/aplat-queries.md) → **KyberContainerHealthMetricData — Per-container metric emission status**. Normal cadence ≈ 1 row / 2 min 30 s; gaps > 5 min indicate the pipeline stalled.

### STG-Perf-7.Q2 — Did the host RDAgent enqueue the upstream event?

See [`aplat-queries.md`](../catalogs/aplat-queries.md) → **RdAgentAzPubSubEtwTable — Upstream enqueue from host RDAgent**. Empty here = host-side break (RDAgent crash / AzPubSub backlog) before Kyber ever sees the data.

### STG-Perf-7.Q3 — Why did Kyber skip emission?

See [`aplat-queries.md`](../catalogs/aplat-queries.md) → **KyberVmAvailabilityMetricEmissionSkipped — Why Kyber chose not to emit**. `Reason contains "stale"` → freshness threshold tripped; `Reason contains "dedup"` → expected dedup behavior (portal display is the actual gap).

### STG-Perf-7.Q4 — Is the emission flat tenant-wide?

See [`aplat-queries.md`](../catalogs/aplat-queries.md) → **KyberVmAvailabilityMetricEmission — Cross-check emitted volume**. Renders a time-chart of distinct VMs Kyber emitted for. Tenant-wide drop to 0 → Kyber service issue, not VM-specific.

### STG-Perf-7.Decision matrix

| Q1 | Q2 | Q3 | Q4 | Verdict |
|---|---|---|---|---|
| has rows | n/a | n/a | n/a | Metric pipeline healthy → portal display / time-range / customer scope issue |
| empty | present | rows w/ "stale" | normal | Enqueue→consume lag → escalate **EEE Host Node** |
| empty | empty | empty | normal | Host-side (RDAgent / AzPubSub queue) → escalate **EEE Host Node** |
| empty | n/a | n/a | flat tenant-wide | Kyber CoreService unhealthy → escalate **EEE Host Node** with `{TenantName}` + window |

### STG-Perf-7.Customer-facing wording

> "The VM Availability Metric you queried in the portal is a **preview feature** that depends on a metric-emission pipeline (`Kyber.CoreService`) separate from the rest of the platform telemetry. Between {StartTime} and {EndTime} we confirmed the upstream RDAgent did publish health events for your container, but the downstream Kyber service did not emit them — we have engaged the Kyber back-end team to investigate. As a workaround, the **VM Availability** view in the **Resource Health** blade is sourced from a different (production) pipeline and remains accurate for SLA assessment."

---

## STG-Perf-8: Disk Cache policy

> **TSG**: [Disk Cache_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FDisk-Cache_Perf)
> **Scope**: Customer reports disk perf below SKU spec OR wants to understand `ReadOnly` / `ReadWrite` / `None` cache modes for OS/data disks.

### STG-Perf-8.Key facts

| Disk role | Default cache | Allowed | Recommended |
|---|---|---|---|
| OS disk | `ReadWrite` | RW/RO | `ReadWrite` (Standard / Premium SSD); `None` for Premium SSD V2 / Ultra (cache not supported) |
| Data disk — random IO | `None` | RW/RO/None | `None` (caching hurts pure random) |
| Data disk — read-heavy / sequential | `None` | RW/RO/None | `ReadOnly` |
| Premium SSD V2 / Ultra Disk | n/a | `None` only | `None` (only supported value) |

### STG-Perf-8.Q1 — Confirm current cache config (no KQL)

Customer-side: Portal → VM → Disks → click disk → `Host caching` field, OR `az vm show -n {VM} -g {RG} --query 'storageProfile.dataDisks[].caching'`.

### STG-Perf-8.Customer-facing wording

> "Per the SKU specification, the IOPS / BW caps depend on the **cache mode**. Switching the data disk from `ReadWrite` to `None` (or vice versa) requires a VM stop/start — not just a disk detach/attach. After changing, re-run your benchmark to confirm the expected limit applies."

---

## STG-Perf-9: Host Caching Not Enabled (premium hosts that **could** cache)

> **TSG**: [Host Caching Not Enabled_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FHost-Caching-Not-Enabled_Perf)
> **Scope**: VM is placed on a premium-eligible (ABC) host but the disk is configured with `caching=None` — customer sees lower IOPS than the cached limit advertises, doesn't realize they opted out of cache.

### STG-Perf-9.Q1 — Detect ABC on the host

See STG-Perf-1.Q1 (LogNodeSnapshot `diskConfiguration` field). If `AllDisksAbc` → ABC available → check customer's per-disk `caching` field.

### STG-Perf-9.Customer-facing wording

> "Your VM is on a premium-eligible host (Azure Blob Cache is available) but your data disk is configured with `Host caching = None`. The IOPS/BW caps you've been comparing to are the **cached** caps — to actually benefit you need `caching=ReadOnly` (read-heavy) or `caching=ReadWrite` (mixed). Note: setting `ReadWrite` on a disk with concurrent multi-writer access can cause corruption — use `ReadOnly` for read-heavy workloads only."

---

## STG-Perf-10: Disk Latency counter not available on NVMe Controller

> **TSG**: [Disk Latency Counter Not Available NVME Controller_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FDisk-Latency-Counter-Not-Available-NVME-Controller_Perf)
> **Scope**: Customer-facing PerfCounter `\PhysicalDisk(*)\Avg. Disk sec/Read|Write` returns 0 / blank on NVMe-controller VMs (Ebsv5/Easv5/Ebdsv5/Ebsv6/Easv6 etc.). Known guest-side limitation when using NVMe controller in Azure VMs.

### STG-Perf-10.Key facts

- The Windows `PhysicalDisk` perfmon counter is populated from the SCSI miniport — NVMe stack does not feed it the same way.
- Use **Storport ETW** (`Microsoft-Windows-StorPort`) Event 504 / 505 instead — see STG-Perf-4 (host-side equivalent: `WindowsEventTable` Event 505 latency histogram via `azcore-queries.md`).
- Linux side: use `iostat -xt 1` (NVMe latency reported correctly under `r_await` / `w_await`).

### STG-Perf-10.Customer guidance

> "Windows `PhysicalDisk` perfmon counters are not populated by the NVMe stack on Azure NVMe-controller VMs. To collect Avg disk sec/Read|Write, enable `Microsoft-Windows-StorPort/Operational` ETW and parse Event 505. On Linux use `iostat -xt`. This is a known guest-side limitation, not a platform fault."

---

## STG-Perf-11: VhdDiskPr Event 47 investigation

> **TSG**: [VhdDiskPr Event 47 Investigation_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FVhdDiskPr-Event-47-Investigation_Perf)
> **Scope**: Host-side `OsVhddiskEventTable` Event 47 logged — indicates VHDMP / blob-cache layer threw a specific error event for the customer's disk surface (paired with Event 16/2/3 family from STG-Perf-4).

### STG-Perf-11.Q1 — Pull Event 47 rows on the node

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").OsVhddiskEventTable
| where NodeId == "{NodeId}"
| where PreciseTimeStamp between (datetime({StartTime})-30m .. datetime({EndTime})+30m)
| where EventId == 47
| project PreciseTimeStamp, NodeId, ContainerId, ParamBinary, ParamString
| order by PreciseTimeStamp asc
```

Combine with STG-Perf-4 queries (Event 2/3/16, 504, 505) for a full local-cache stack picture.

### STG-Perf-11.Interpretation

- Event 47 alongside Event 16 → burst overrun on the local cache disk (same root cause as STG-Perf-4.Q1) — customer needs to throttle the burst or move to a larger SKU.
- Event 47 standalone, no Event 16/2/3 → uncommon, escalate to **EEE Storage** with NodeId + ContainerId + PreciseTimeStamp.

---

## STG-Perf-12: Queue Depth constantly 1

> **TSG**: [Queue Depth constantly 1_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FQueue-Depth-constantly-1_Perf)
> **Scope**: Customer benchmark (e.g., `diskspd`, `fio`, `iometer`) shows IOPS well below SKU limit AND `Current Disk Queue Length` (or equivalent) is always 1 — workload is single-threaded, not stretching the queue → not a platform fault, the IO pattern itself is the bottleneck.

### STG-Perf-12.Customer guidance

- Single-threaded synchronous IO can never exceed `1 / (per-op latency)` IOPS. For ~1 ms premium disk latency that ceiling is ~1000 IOPS regardless of SKU.
- To stretch the queue: `diskspd -o32 -t8 ...` (32 outstanding × 8 threads = 256 effective queue depth); `fio --iodepth=32 --numjobs=8 ...`.
- Application-level patterns that produce QD=1: `fsync()` / `O_DIRECT|O_SYNC` per op, single-threaded log writers, COBOL/legacy IO libraries.

### STG-Perf-12.Customer-facing wording

> "Your benchmark reports `Current Disk Queue Length = 1` for the entire run, which means the workload only ever issues one outstanding IO at a time. With ~1 ms premium SSD latency this caps you at ~1000 IOPS regardless of the SKU's headline number. Re-run with `-o32 -t8` (diskspd) or `--iodepth=32 --numjobs=8` (fio) to confirm the SKU limit is reachable."

---

## STG-Perf-13: Enabling Performance Plus (disk burst)

> **TSG**: [Enabling Performance Plus_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FEnabling-Performance-Plus_Perf)
> **Scope**: Customer asks how to enable Performance Plus on a managed disk (raises per-disk IOPS/BW above default for Premium SSD ≥ 513 GiB). This is a customer-side enablement question, not a platform fault.

### STG-Perf-13.Key facts

- Eligible: Premium SSD `P30+` (≥ 1 TiB historically; current min is `513 GiB` per public docs).
- Enabled at **disk create** time via ARM template or `az disk create --performance-plus true`.
- Cannot be toggled after creation — disk must be re-created (snapshot + new disk).

### STG-Perf-13.Customer guidance

> "Performance Plus is opt-in at disk creation time and cannot be enabled on an existing disk. Recommended steps: (1) snapshot the existing disk, (2) create a new disk from the snapshot with `--performance-plus true`, (3) swap the new disk for the existing data disk. See `az disk create` docs. Caps with Performance Plus enabled: <https://learn.microsoft.com/azure/virtual-machines/disks-enable-performance-plus>."

---

## STG-Perf-14: Troubleshooting Disk using ASI (dashboard pointer)

> **TSG**: [Troubleshooting Disk using ASI_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FTroubleshooting-Disk-using-ASI_Perf)
> **Scope**: How to use the **ASI Azure VM / Azure Host Node** dashboards to triage disk perf without writing KQL.

### STG-Perf-14.Dashboard pointers

Use this skill's dashboard catalog [`../dashboards/`](../dashboards/) (ASI/EEE/vmdash templates) to build the links, or open the ASI pages manually:

- **ASI Azure VM**: per-VM disk surface, blob cache hit ratio, observed IOPS/BW, throttle counters.
- **ASI Host Node**: per-node aggregate disk perf, ABC cache state, XStore tenant cross-link.
- **EEE HostNode**: same data + hardware/serial events sidebar.

### STG-Perf-14.Quick checks order

1. ASI Azure VM → Disk surfaces → confirm IOPS/BW vs SKU spec.
2. ASI Host Node → Cache health → confirm no BSPausedWrites flapping (cross-link STG-Perf-5).
3. ASI Host Node → XStore tenant link → if account-level latency, jump to STG-Perf-6.

---

## STG-Perf-15: Ultra / PremiumV2 Disks via Tenant Health Dashboard

> **TSG**: [Troubleshooting Ultra and PremiumV2 Disks using Tenant Health Dashboard_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FTroubleshooting-Ultra-and-PremiumV2-Disks-using-Tenant-Health-Dashboard_Perf)
> **Scope**: Customer reports Ultra Disk or Premium SSD V2 (PSSDv2) slowness — these SKUs are on the **Elastic SAN / Yarrow** backend, distinct from the regular Premium SSD path; standard XArgus / XStore queries don't apply.

### STG-Perf-15.Dashboard pointer

- **Tenant Health Dashboard** (ESAN / Yarrow tenant): customer-facing latency, IOPS, BW per disk. Owned by Storage PG.
- Link template: `https://portal.microsoftgeneva.com/dashboard/TenantHealth/...` (build from [`../dashboards/`](../dashboards/) if a template exists, or open Tenant Health manually).

### STG-Perf-15.Kusto cross-ref

When the dashboard shows degradation, see [`storage-account-queries.md`](../catalogs/storage-account-queries.md) → **Elastic SAN section** → `AccountPerfPercentiles5M` filtered to IscsiRead / IscsiWrite metrics.

### STG-Perf-15.Escalation

PSSDv2 / Ultra tenant-side faults → escalate to **Elastic SAN backend team** (PG) with TenantName + DiskUri + PreciseTimeStamp.

---

# § NET-Perf — Network perf

## NET-Perf-1: Host pingmesh latency anomalies

> **TSG**: `/SME Topics/Performance/Host Node Investigation_Perf`
> **Scope**: Customer reports elevated network RTT, TCP retransmits, intermittent connectivity slow; suspect host networking (NIC/spine).

### NET-Perf-1.Q1 — AzPingMesh server-to-server RTT (>10 ms threshold)

See [`networking-queries.md`](../catalogs/networking-queries.md) → **AzPingMeshServerStatus — Host pingmesh latency anomalies (>10 ms RTT)**.

### NET-Perf-1.Interpretation

- **Normal host RTT**: 300–1500 µs.
- **Threshold**: 10,000 µs (10 ms) used by the TSG to declare elevated host networking latency.
- **Amplification**: 5–20× baseline RTT typically maps to ~5× amplification on VM disk transmit latency (`CurAvgTxLatInms` in the VM shoebox).
- **UI cross-check**: open the EEE Host Node page (build the link from [`../dashboards/`](../dashboards/) or open it manually) → "Pingmesh" button on the right; same data with a chart.

### NET-Perf-1.Escalation

- Hit on one specific `serverIP` → that one host has a NIC/peer issue → **Host Networking** collab.
- Hit across many `serverIP` from same source host → spine-side issue → **Host Networking** + region datapath triage.

### NET-Perf-1.Q2 — VFP path (when relevant)

If pingmesh is clean but the customer sees packet-level issues, cross-link to [`vmainsight-queries.md`](../catalogs/vmainsight-queries.md) → **Vmadiag — vfp_restore_fails / EventData_SDN_DataPath**. Common after a recent LM (§ LM-Perf).

---

## NET-Perf-2: Excessive outbound + metric discrepancy (likely VM breach / SYN flood)

> **TSG**: `/SME Topics/Performance/TSGs/Excessive Network Out Usage_Perf`
> **Scope**: Customer is billed for huge VM outbound bandwidth but the portal **Network Out Total** metric shows almost nothing. Often paired with high VM CPU and slow SSH/RDP. Root cause is typically a breached VM generating a SYN flood toward public IPs.
>
> **Why the metric gap is real**: Host networking does not count *exception packets* in the `Network Out Total` aggregate counter. SYN floods are entirely exception traffic, so portal stays flat while the SLB / NAT actually transmits (and bills for) millions of packets per second. `Network Out billable (deprecated)` reflects the real volume — use it as the workaround metric until the host-networking PG ships a fix.

### NET-Perf-2.Q1 — Confirm the metric gap (vmdash, no KQL needed)

Open the **VM Dashboard** ([aka.ms/vmdash](https://aka.ms/vmdash)) and switch the chart from `Network Out Total` (default) to `Network Out`. Add **Dimension → VM ID** and filter on `Resource ID = {VMId}` (VirtualMachineUniqueId). If `Network Out` is large but `Network Out Total` is flat → you have the discrepancy.

Use [`../dashboards/`](../dashboards/) to build vmdash / ASI navigation links, or open the dashboards manually.

### NET-Perf-2.Q2 — NetVMA / VFP container-level packet rates

Open **NetVMA** and search for the container ID. Massive outbound packet rate from the container = VM is the source. If unfamiliar with NetVMA, file a collab to the **Azure Networking team (ANP)** via DFM Create Collaboration (ANP triages and escalates to the networking PG; we follow up).

### NET-Perf-2.Q3 — SLB Public IP traffic profile (Jarvis SlbHpMDMAccount)

Go to the SLB MDM dashboard, choose location in `SlbHpMDMAccount`, put the VM public IP in `VipAddress` / `FrontIPAddress`. If virtually all packets are **SYN** with no matching responses, the workload is not a normal app — it's an outbound scan/flood.

### NET-Perf-2.Q4 — Guest-side per-destination breakdown

Delegate to [`vm-log-analyzer`](../../../vm-log-analyzer/SKILL.md):
- **Linux**: `iftop` or `iptraf-ng` for live per-destination traffic.
- **Windows**: **Resource Monitor** → Network tab → per-destination traffic.

### NET-Perf-2.Mitigation

1. **Stop the bleeding first** — either stop the VM, or block all outbound via NSG + OS firewall. **Redeploy does NOT help** — the VM is generating the traffic; moving hosts doesn't change that.
2. **If breach confirmed** (always assume yes if traffic pattern matches) — **rebuild the VM** from a clean image. Reset all credentials that the VM had access to (managed identity, stored keys, mounted secrets).
3. **Billing workaround for the customer** — they can dispute outbound bandwidth charges based on the metric discrepancy via standard billing escalation; document the time window and the `Network Out` vs `Network Out Total` gap as evidence.

### NET-Perf-2.Customer-facing wording

> "Between {StartTime} and {EndTime} we observed ~{PPS} packets per second of outbound traffic from your VM, predominantly TCP SYN packets directed at public IPs with no matching responses. This pattern is consistent with the VM having been compromised and used as a source for an outbound scan / SYN flood. We strongly recommend you (1) immediately block outbound traffic from this VM at the NSG and OS firewall level, (2) rotate any credentials, keys, or managed-identity scopes the VM had access to, and (3) rebuild the VM from a known-clean image. The discrepancy between the portal's `Network Out Total` and `Network Out billable` metrics is a known platform-side limitation (exception packets are not counted in the aggregate) and the engineering team is working on a fix."

Reference ICMs: `321891141`, `269337453`.

---

## NET-Perf-3: Host Networking Updates impact

> **TSG**: [Host Networking Updates_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FHost-Networking-Updates_Perf)
> **Scope**: Customer reports network latency spike / PPS drop, and the timestamp aligns with a host networking update (VFP / SDN agent / NetworkManager rollout) — distinct from VMPHU (covered by MAINT-Perf-1).

### NET-Perf-3.Q1 — Confirm host-networking rollout on the node in-window

See [`hybridnetworking-queries.md`](../catalogs/networking-queries.md) (if present in repo) — alternatively delegate to `Hybridnetworking` cluster:

```kusto
cluster("hybridnetworking.westus.kusto.windows.net").database("hybridnetworking").NetMonComponentRolloutEvents
| where NodeId == "{NodeId}"
| where PreciseTimeStamp between (datetime({StartTime})-1h .. datetime({EndTime})+1h)
| project PreciseTimeStamp, NodeId, Component, FromVersion, ToVersion, RolloutId, ActionResult
| order by PreciseTimeStamp asc
```

(Confirm exact table name with `vm-knowledge-search` if the rollout table has been renamed.)

### NET-Perf-3.Q2 — VFP restart timing

See [`vmainsight-queries.md`](../catalogs/vmainsight-queries.md) → **Vmadiag → vfp_restore_fails / vfp_restart_count**.

### NET-Perf-3.Interpretation

- Rollout `ActionResult = Success` AND timestamp aligns with customer-reported drop → expected blip during cut-over, advise the customer it was a planned host networking update.
- Rollout `ActionResult = Failed` / `RetryPending` → escalate to **Host Networking** team with NodeId + RolloutId.

---

# § CPU-Perf — CPU perf

## CPU-Perf-1: Noisy-neighbor / host CPU contention

> **Scope**: VM is CPU-bound from guest perspective; disk and network paths are clean. Suspect over-commit on the host.

### CPU-Perf-1.Q1 — Per-VM CPU on the host

See [`playbook-C-performance-core.md`](playbook-C-performance-core.md) Step 5 — same query template. Aggregates `CurAvgCpuUtilization` across all VMs on `{NodeId}`.

### CPU-Perf-1.Q2 — Per-VM list and SKU spread

```kusto
cluster("Azcsupfollower").database("AzureCM").LogContainerSnapshot
| where nodeId == "{NodeId}" and PreciseTimeStamp between (datetime({StartTime})-30m .. datetime({EndTime})+30m)
| summarize arg_max(PreciseTimeStamp, *) by roleInstanceName
| project roleInstanceName, virtualMachineSizeName=tostring(virtualMachineSize), subscriptionId
```

Use this to identify the co-tenants (don't share customer-cross identities outside, but useful for internal sizing).

### CPU-Perf-1.Q3 — Host bond/network counters (rule out NUMA contention by proxy)

See [`azcore-queries.md`](../catalogs/azcore-queries.md) → host-level counters (full bond table). Elevated kernel-side network/IRQ activity from another VM can cause apparent CPU steal.

### CPU-Perf-1.Verdict

- TotalCpu of node ≥ 95% sustained → confirmed over-commit; recommend customer move to dedicated host / larger SKU / different region of the same family.
- TotalCpu < 80% but customer still sees CPU pressure → guest OS issue (driver, antivirus, RunOnce) → delegate to [`vm-log-analyzer`](../../../vm-log-analyzer/SKILL.md).

---

## CPU-Perf-2: Troubleshoot High CPU (in-guest)

> **TSG**: [Troubleshoot High CPU_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FTroubleshoot-High-CPU_Perf)
> **Scope**: Customer reports sustained high CPU **inside the guest** (Task Manager / `top` shows ~100%). First rule out platform contention (CPU-Perf-1) — if node `TotalCpu < 80%`, this chapter applies.

### CPU-Perf-2.Customer-side data to collect

| OS | Tool | What |
|---|---|---|
| Windows | Performance Diagnostics — **Performance Counters + Process Trace** | Per-process CPU%, kernel vs user time, thread stacks |
| Windows | `wpr -start CPU -filemode` → `wpr -stop trace.etl` | Full ETW with CPU stacks for offline analysis |
| Linux | `top -H -p $(pidof <proc>)` + `perf top -p <pid>` | Per-thread CPU% and on-CPU function stacks |
| Linux | `sosreport` (RHEL/CentOS) / `supportconfig` (SLES) | Includes proc, sched, perf data — delegate to [`vm-log-analyzer`](../../../vm-log-analyzer/SKILL.md) |

### CPU-Perf-2.Common culprits checklist

1. Anti-virus / EDR scan (Defender, CrowdStrike, Carbon Black) — confirm scheduled-scan window, exclude DB / log directories.
2. Windows Update scan (`TiWorker.exe`, `TrustedInstaller.exe`) — defer or schedule outside business hours.
3. SQL Server compilations / `tempdb` contention — DBA escalation, not VM.
4. .NET / JVM GC pauses — application telemetry.
5. Runaway custom processes — kill / restart / patch.

### CPU-Perf-2.Customer-facing wording

> "Node-side CPU on host {NodeId} stayed below {TotalCpuPercent}% throughout the window {StartTime} – {EndTime}, so the platform did not throttle your CPU. The high CPU observed inside the VM is being driven by guest-side processes — please collect a Performance Diagnostics run (Performance Counters + Process Trace, ~10 min during the issue) and share the report so we can identify the specific process."

---

## CPU-Perf-3: CPU SKU clock difference (base vs boost frequency)

> **TSG**: [CPU SKU Clock difference_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FCPU-SKU-Clock-difference_Perf)
> **Scope**: Customer compares `Get-CimInstance Win32_Processor` / `lscpu` MHz output between two VMs of the same SKU and sees different values — concludes platform is "underclocking" their VM.

### CPU-Perf-3.Key facts

- Reported MHz is **base clock**, NOT the current operating clock. Azure VMs do NOT expose turbo-boost dynamic frequency.
- SKU documentation always quotes **base frequency**; **all-core turbo** is higher but not guaranteed (depends on workload, thermal, neighbor load).
- Two VMs of the same SKU in the same region MAY land on different hardware generations within the same SKU family (e.g., D_v5 can be Intel Ice Lake or Sapphire Rapids depending on cluster) → base frequencies differ.

### CPU-Perf-3.Q1 — Which CPU model on each VM?

See [`wdgeventstore-queries.md`](../catalogs/wdgeventstore-queries.md) → **nodes — Hardware lookup by NodeId** → `cpuModel` / `processorName`. Compare across the two VMs.

### CPU-Perf-3.Customer-facing wording

> "Within a single SKU family (e.g., `Standard_D8s_v5`) Azure may use multiple hardware generations across the fleet. Your VM A is on `{cpuModel_A}` (base {GHz_A}) and VM B is on `{cpuModel_B}` (base {GHz_B}). Both meet the published SKU spec — the headline number quoted in the SKU page is the **lowest** supported base frequency for that family. If your workload requires a specific hardware generation, please use the **CPU generation** filter at VM-create time or pin to a SKU subscript with a stable hardware contract (e.g., the `_v5` constrained-vCPU SKUs publish a single model)."

---

## CPU-Perf-4: Incorrect CPU core / hyperthreading reporting

> **TSG**: [Incorrect CPU Core Hyperthreading_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FIncorrect-CPU-Core-Hyperthreading_Perf)
> **Scope**: Customer counts `Logical Processors` vs `Physical Cores` and disputes the SKU spec. Some Azure SKUs disable SMT/HT at the hypervisor → "vCPU" actually equals a full physical core, not a hyperthread.

### CPU-Perf-4.Key facts

| SKU class | vCPU = | Example |
|---|---|---|
| Standard | 1 hyperthread (HT enabled) | `D-series`, `E-series`, most general purpose |
| Constrained-vCPU `_v5` | 1 hyperthread | `Standard_D8s_v5` |
| HPC / `H-series` | 1 physical core (HT disabled) | `HBv4`, `HX-series`, `HC-series` |
| Confidential VM `DCv5` (AMD SEV-SNP) | varies, see SKU page | `DCadsv5` |

### CPU-Perf-4.Customer-facing wording

> "On the `{SKU}` family, Azure {disables / enables} simultaneous multithreading (SMT/HT). That is why `Get-CimInstance Win32_Processor` reports {LogicalProcessors} logical and {Cores} physical — this matches the SKU spec ({sku_url}). It is not a misconfiguration; the platform sizes the VM per the published per-SKU core / vCPU contract."

---

# § MEM-Perf — Memory perf

## MEM-Perf-1: "Available Memory" metric missing in portal (Windows guest)

> **TSG**: `/SME Topics/Performance/TSGs/Available Memory shows 0GB_Perf`
> **Scope**: Windows VM portal shows **Available Memory = 0 GB** or the metric is entirely absent. Two distinct branches — platform (host OS too old) vs guest (dmvsc.sys stopped, Hyper-V role enabled inside guest, CVM by design, Linux balloon driver missing).

### MEM-Perf-1.Q1 — Host OS build check (rules in / out the platform branch)

See [`wdgeventstore-queries.md`](../catalogs/wdgeventstore-queries.md) → **nodes — Host OS version lookup by NodeId**.

| `OSVersion` | Branch |
|---|---|
| `RS 1.65*` | **Platform** — host predates the feature, no ETA on update. Use the customer-facing RCA wording below. |
| `RS 1.86+` (>99.7% of fleet) | **Guest-side** — jump to Q2. |

### MEM-Perf-1.Q2 — Guest-side root cause (no KQL needed)

Delegate to [`vm-log-analyzer`](../../../vm-log-analyzer/SKILL.md) to check:

| Symptom | Cause | Fix |
|---|---|---|
| `sc query dmvsc` STATE = STOPPED on **WS2016 / WS2019** | Hyper-V role enabled inside the guest → `dmvsc.sys` will not start (by design) | Remove the Hyper-V role + reboot; or upgrade guest to WS2022 / WS2025 |
| `bcdedit` shows `hypervisorlaunchtype Auto` | HvHost service active even without Hyper-V role | `bcdedit /set hypervisorlaunchtype off` + reboot |
| Confidential VM (CVM) | CVMs do not support dynamic memory by design | Enable VM Insights → `% Available memory` via DCR (Linux only), or accept limitation |
| Linux: `lsmod \| grep hv_balloon` empty | `hv-balloon` driver missing | Install `hyperv-tools` / appropriate distro package, reload module |

### MEM-Perf-1.Customer RCA wording (platform branch only)

> "The Microsoft Azure team has completed investigating the VM {VMName} where the *Guest Available Memory* metric is not presented in the portal. We identified that the physical host node where the VM is currently running has not yet been updated to an OS build that supports the metric. Once the Host OS is updated, the metric will become available. Unfortunately, we do not have an ETA on when the node will be updated at this time. We apologize for any inconvenience this may have caused you."

---

## MEM-Perf-2: Low Memory Windows (general)

> **TSG**: [Low Memory Windows Troubleshooting_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FLow-Memory-Windows-Troubleshooting_Perf)
> **Scope**: Windows guest reports low Available Memory but the actual reduction is not 2 GB exactly (otherwise MEM-Perf-3). Need to identify which process / kernel pool / driver is consuming memory.

### MEM-Perf-2.Customer-side data to collect

| Tool | What to capture |
|---|---|
| Performance Diagnostics — **Memory Trace** | Per-process working set + commit, kernel pool, driver footprint |
| `RAMMap.exe` (Sysinternals) | Per-category memory usage (Process Private, Mapped File, Driver Locked, Nonpaged Pool, Paged Pool) |
| `Get-Process \| sort WorkingSet64 -desc` | Quick top-process check |
| `poolmon.exe` (Windows SDK) | Per-pool-tag kernel allocations (driver leak) |

### MEM-Perf-2.Common causes

1. SQL Server / IIS / .NET process committed memory growth.
2. Driver leak (poolmon shows growing nonpaged-pool tag).
3. Defender / EDR cache growth.
4. CSV (Cluster Shared Volume) `csvfs.sys` memory pressure on S2D nodes.

### MEM-Perf-2.Customer-facing wording

> "Available Memory drop on the VM is driven by guest-side allocations, not by platform reservation. Please collect a Performance Diagnostics **Memory Trace** (~10 min during the issue) and a RAMMap snapshot — these together pinpoint which process or kernel pool is consuming the memory."

---

## MEM-Perf-3: 2GB Low Memory Windows

> **TSG**: [2GB Low Memory Windows Troubleshooting_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2F2GB-Low-Memory-Windows-Troubleshooting_Perf)
> **Scope**: Customer reports exactly **~2 GB less** Available Memory than the SKU advertises (e.g., 16 GB VM shows ~14 GB). This is a specific Windows-guest pattern, usually a memory reservation (driver, hypervisor visualization, CIM).

### MEM-Perf-3.Key facts

- On a 16 GB SKU, customer expects `Total Physical Memory` = 16384 MB but sees ~14336 MB (~2 GB delta).
- The delta is NOT lost — it is **Hardware Reserved** (see MEM-Perf-5 for confirmation method).
- Common cause: Hyper-V role enabled inside the guest (`Hypervisor reserved page table` for nested virt) → 2 GB reservation.

### MEM-Perf-3.Q1 — Check Hyper-V state in guest

```cmd
bcdedit /enum {current}
:: look for "hypervisorlaunchtype Auto" → Hyper-V is active in guest
sc query vmcompute
:: look for STATE=RUNNING → Hyper-V management running
```

### MEM-Perf-3.Fix

`bcdedit /set hypervisorlaunchtype off` + reboot → reservation released.

### MEM-Perf-3.Customer-facing wording

> "The exact ~2 GB delta you observe is reserved by the in-guest Hyper-V hypervisor (`hypervisorlaunchtype = Auto`). If you do not need nested virtualization, run `bcdedit /set hypervisorlaunchtype off` from an elevated cmd and reboot — Available Memory will return to the SKU spec."

---

## MEM-Perf-4: Reserved Memory 2GB Windows (variant of MEM-Perf-3)

> **TSG**: [Reserved Memory 2gb windows_perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FReserved-Memory-2gb-windows_perf)
> **Scope**: Effectively the same observed symptom as MEM-Perf-3 (2 GB reserved). This wiki is a sibling investigation note from a different reporter. **Action: triage with MEM-Perf-3 first**, only fall back to MEM-Perf-4 wiki if MEM-Perf-3 ruled out Hyper-V.

### MEM-Perf-4.Additional fallback causes

- Windows guest with `CrashDump` set to `Complete memory dump` reserves dump-file address space (typically equal to RAM, not 2 GB).
- `pagefile.sys` minimum + Windows resilient memory pool.
- Defender Application Guard / Hyper-V Isolated Containers reserving NUMA quota.

---

## MEM-Perf-5: Memory Hardware Reserved in Windows

> **TSG**: [Memory Hardware Reserved in Windows_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FMemory-Hardware-Reserved-in-Windows_Perf)
> **Scope**: Customer screenshots Task Manager → Memory → notices a "Hardware Reserved" slice and asks Azure to release it.

### MEM-Perf-5.Key facts

- "Hardware Reserved" in Task Manager = memory the firmware / hypervisor exposed but the OS cannot use directly (legacy chipset reservation pattern carried over to virtualized hardware).
- On Azure VMs this is normal and small (~50 MB on most SKUs) or larger (2 GB if Hyper-V enabled — see MEM-Perf-3/4).
- Cannot be released — it is a contract between the firmware (BIOS/UEFI) and the OS memory manager.

### MEM-Perf-5.Customer-facing wording

> "'Hardware Reserved' in Task Manager represents memory the system firmware reserves for chipset / hypervisor use — this is by-design and cannot be released by the OS or the platform. On Azure VMs the typical reservation is {value}; values larger than ~50 MB usually indicate a Hyper-V role enabled inside the guest (see MEM-Perf-3 to confirm and release ~2 GB)."

---

## MEM-Perf-6: Available Memory 50MB less on TrustedVM

> **TSG**: [Available Memory 50MB Less TrustedVM_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FAvailable-Memory-50MB-Less-TrustedVM_Perf)
> **Scope**: Customer on a **Trusted Launch VM** sees ~50 MB less Available Memory than a same-SKU non-Trusted VM. Specific to Trusted Launch (vTPM + secure-boot) overhead.

### MEM-Perf-6.Key facts

- vTPM + secure-boot + measured-boot machinery reserves ~50 MB on most SKUs.
- Reservation is by-design for the Trusted Launch security model — cannot be reclaimed without disabling Trusted Launch.
- If customer needs the full RAM, recreate the VM without Trusted Launch (loses vTPM + secure-boot guarantees).

### MEM-Perf-6.Customer-facing wording

> "The ~50 MB delta between your Trusted Launch VM and a non-Trusted same-SKU VM is reserved by the Trusted Launch security boundary (vTPM + secure-boot + measured-boot tables). This is by-design and cannot be reclaimed while Trusted Launch is enabled."

---

# § HANG — Compute hang

## HANG-Perf-1: Troubleshoot VM Hung or Frozen

> **TSG**: [Troubleshoot VM Hung or Frozen_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FTroubleshoot-VM-Hung-or-Frozen_Perf)
> **Scope**: VM stops responding to ping, RDP/SSH, and Serial Console — but the platform reports it as `Running` / `VM is up` (no host-side fault detected, no service-healing event).

### HANG-Perf-1.Q1 — Platform-side first (rule out service healing / LM / host fault)

Run the core flow's Step 2/3 (Service Healing) + Step 6 (Live Migration) on the VM's container. If any host-side event aligns with the hang → re-route to the matching playbook (Playbook A reboot / Playbook C cant-start-stop / STG-Perf-4 disk burst).

### HANG-Perf-2 — If platform clean, decide between in-guest crash vs hung user-mode

Two sub-cases:

| Case | What to look at | Delegate to |
|---|---|---|
| **Kernel-level hang** (bug-check candidate, no Serial Console output) | Force a crash dump via Azure Portal → VM → Boot diagnostics → **Reset** with `NMI` (if supported), OR `Restart` and collect Memory.dmp from `C:\Windows\` after boot | [`vm-log-analyzer`](../../../vm-log-analyzer/SKILL.md) (BSOD / kernel dump analysis) |
| **User-mode hang** (Serial Console still works, only RDP / app frozen) | Collect Performance Diagnostics, process dumps via `procdump` | [`vm-log-analyzer`](../../../vm-log-analyzer/SKILL.md) (process dump + ETW analysis) |
| **Linux uninterruptible sleep (D state)** | `cat /proc/<pid>/stack` over Serial Console | [`vm-log-analyzer`](../../../vm-log-analyzer/SKILL.md) |

### HANG-Perf-1.Q2 — ASAP / NVMe controller reset cross-check

On AMD v6/v7 + Boost-for-Storage SKUs, an NVMe controller reset can present as a guest freeze with no platform indication → see § ASAP and `asap-storage-queries.md`.

### HANG-Perf-1.Customer-facing wording

> "Between {StartTime} and {EndTime} we confirmed no host-side fault, service-healing event, live migration, or platform reboot on the container hosting {VMName}. The hang therefore originates inside the guest. Please (1) capture a memory dump as soon as the issue reproduces (NMI from portal if kernel hang, `procdump -ma <pid>` if user-mode), (2) share boot diagnostics screenshot + serial-console output from the hang window — we will analyze for a root cause."

---

# § GPU-Perf — GPU perf

## GPU-Perf-1: NC / NV-series VM intro and SKU pick

> **TSG**: [NC and NV-series Virtual Machines_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FNC-and-NV-series-Virtual-Machines_Perf)
> **Scope**: Customer is new to Azure GPU VMs and asks which N-series SKU to pick, what driver to install, or why their workload doesn't run. This is the orientation chapter — read first before any other GPU TSG.

### GPU-Perf-1.SKU family cheat sheet

| Family | GPU | Use case |
|---|---|---|
| **NC** (`NC`, `NCv2/v3`, `NCasT4_v3`, `NC_A100_v4`, `NCadsH100v5`) | NVIDIA Tesla / A100 / H100 | AI / ML training, HPC compute |
| **ND** (`NDv2`, `NDasrA100_v4`, `NDH100v5`) | NVIDIA + InfiniBand | Distributed deep-learning training |
| **NV** (`NV`, `NVv3`, `NVv4`, `NVads_A10_v5`) | NVIDIA Tesla M60 / AMD MI25 / NVIDIA A10 | Remote workstation, visualization, video encoding |
| **NG** (`NGads_V620_v1`) | AMD Radeon V620 | Cloud gaming / streaming |

### GPU-Perf-1.Q1 — Driver source

| OS | Source | Notes |
|---|---|---|
| Windows | Azure NVIDIA GPU Driver extension OR manual install from NVIDIA / Azure portal | NEVER use the consumer GeForce driver — must be the Tesla / Grid driver |
| Linux (Ubuntu/RHEL) | Azure NVIDIA GPU Driver extension OR `apt install cuda-drivers` from NVIDIA repo | Match the kernel version |

### GPU-Perf-1.Customer-facing wording

> "Each N-series family is purpose-built — NC for compute (CUDA), NV for visualization (RDP/Grid licensing), ND for distributed training (InfiniBand). Please share (1) which SKU you provisioned, (2) the OS and kernel, (3) `nvidia-smi` output, and (4) the workload type (CUDA training? Direct3D rendering? Video encode?) so we can route to the correct GPU TSG."

---

## GPU-Perf-2: Linux N-Series VMs not detecting GPUs

> **TSG**: [Linux N-Series VMs Not Detecting GPUs_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FLinux-N-Series-VMs-Not-Detecting-GPUs_Perf)
> **Scope**: `nvidia-smi` reports `No devices were found` OR `lspci -nn | grep -i nvidia` returns empty on a Linux N-series VM.

### GPU-Perf-2.Customer-side checklist

```bash
# 1. PCI visibility — should list NVIDIA GPU(s)
lspci -nn | grep -iE "nvidia|3d controller|vga"

# 2. Driver module loaded?
lsmod | grep nvidia

# 3. Driver vs kernel mismatch?
dmesg | grep -iE "nvidia|nvrm" | tail -50
modinfo nvidia | grep ^version

# 4. Confirm the Azure GPU extension installed cleanly
sudo cat /var/log/azure/nvidia-gpu-driver-extension/*.log | tail -200
```

### GPU-Perf-2.Common causes

1. Kernel updated → NVIDIA driver kernel module no longer matches → `dkms autoinstall` or reinstall driver.
2. Azure GPU extension installation failed mid-way (network issue / proxy / no internet) → check extension log.
3. Secure Boot enabled with unsigned NVIDIA module → either disable Secure Boot or use signed driver bundle.
4. Trusted Launch + Confidential Compute combos that don't expose GPU yet.

### GPU-Perf-2.Customer-facing wording

> "`lspci` not showing the NVIDIA device usually means the GPU passthrough surface is fine on the host but the guest driver / module is not loaded. Please share `dmesg | grep -i nvidia` and `cat /var/log/azure/nvidia-gpu-driver-extension/*.log` so we can confirm whether it is a kernel-driver mismatch or a Secure-Boot signing issue."

---

## GPU-Perf-3: Linux GPU Nvidia driver slow

> **TSG**: [Linux GPU Nvidia Slow_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FLinux-GPU-Nvidia-Slow_Perf)
> **Scope**: `nvidia-smi` detects the GPU but workload throughput / `nvidia-smi dmon` shows low SM utilization, low memory bandwidth, or sustained `P8` (low-power) state.

### GPU-Perf-3.Quick checks

```bash
# Power state — should be P0 under load
nvidia-smi --query-gpu=power.draw,power.limit,pstate,utilization.gpu,utilization.memory \
           --format=csv -l 1

# Persistence mode (required for low-latency kernel launch)
nvidia-smi -pm 1

# MIG mode — if accidentally enabled, partitions reduce capacity
nvidia-smi -L  # check for "MIG ..." entries

# ECC — enabled steals memory bandwidth, disable if not required
nvidia-smi --query-gpu=ecc.mode.current --format=csv
```

### GPU-Perf-3.Common causes

1. Persistence mode off → cold-start latency dominates short kernels → `nvidia-smi -pm 1` (persists across reboot via systemd unit).
2. CUDA version vs driver mismatch (CUDA toolkit too new for installed driver).
3. PCIe link width / speed throttled — `nvidia-smi -q | grep -E "PCI|Link"` → confirm Gen4 x16.
4. Thermal throttling (`pstate` flips to P8 when temp > 85°C — rare on Azure platform, escalate to GPU team if seen).

### GPU-Perf-3.Customer-facing wording

> "Please enable persistence mode (`sudo nvidia-smi -pm 1`) and confirm the GPU stays in P0 with high utilization under your workload. If persistence is on but `nvidia-smi dmon` still shows low SM utilization, share the `nvidia-smi -q` full dump — we'll check PCIe link width and thermal state."

---

## GPU-Perf-4: Windows GPU CUDA setup

> **TSG**: [Windows GPU CUDA_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FWindows-GPU-CUDA_Perf)
> **Scope**: Windows NC / ND VM — CUDA workload fails to launch, `nvidia-smi.exe` works but `cudaGetDeviceCount` returns 0 or the application reports `CUDA error: no CUDA-capable device is detected`.

### GPU-Perf-4.Checklist

1. Confirm the **Tesla / GRID** driver is installed, not the consumer driver. `nvidia-smi.exe` → top-right driver version must match the Tesla matrix.
2. Confirm the **CUDA Toolkit** version matches the driver (e.g., CUDA 12.x requires driver ≥ 525.x). Download from <https://developer.nvidia.com/cuda-toolkit-archive>.
3. Run the CUDA `deviceQuery` sample from the toolkit (`%ProgramFiles%\NVIDIA Corporation\CUDA Samples\v...\Bin\...\deviceQuery.exe`) → must report `Result = PASS`.
4. If running inside a container, ensure GPU is passed through (`--gpus all` for Docker Desktop with WSL2 backend; Hyper-V isolation does NOT support GPU passthrough today).
5. `%CUDA_VISIBLE_DEVICES%` env var not accidentally set to `-1` or empty.

### GPU-Perf-4.Customer-facing wording

> "Please run `deviceQuery.exe` from the CUDA Samples directory and share the output. If it reports `Result = FAIL`, the driver / CUDA version pair is incompatible — verify against <https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html#cuda-major-component-versions>."

---

## GPU-Perf-5: Graphics Application not using NV GPU (Windows DirectX)

> **TSG**: [Graphics Application not using NV GPU_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FGraphics-Application-not-using-NV-GPU_Perf)
> **Scope**: On an NV-series VM (visualization SKU), a Direct3D / OpenGL application renders on the Microsoft Basic Render driver / WARP software adapter instead of the NVIDIA GPU. Common with RDP sessions, screen-recording tools, and unsupported APIs.

### GPU-Perf-5.Q1 — Identify which adapter the app is using

- `dxdiag.exe` → Display tabs → look for `NVIDIA ...` device with `Driver Model: WDDM`. If `Microsoft Basic Render Driver` is the only entry, NVIDIA is not exposed to the user session.
- Task Manager → Performance → GPU pane → confirm NVIDIA GPU shows non-zero `3D` / `Copy` / `Encode` usage when the app is running.

### GPU-Perf-5.Common causes

1. **RDP session with default GPO** — `Use hardware graphics adapters for all Remote Desktop Services sessions` is disabled by default in older WS images. Enable via `gpedit.msc → Computer → Admin Templates → Windows Components → Remote Desktop Services → Remote Desktop Session Host → Remote Session Environment → Use hardware graphics adapters for all Remote Desktop Services sessions = Enabled`.
2. App-specific adapter selection — many apps default to integrated GPU even when discrete is present. Set per-app GPU preference in Windows Settings → Display → Graphics settings.
3. GRID licensing not activated — NV-series Tesla M60 / NVads A10 requires GRID licensing. Run `nvidia-smi -q | grep -i license` to confirm. Reinstall the Azure NVIDIA driver extension (it includes GRID license server config).

### GPU-Perf-5.Customer-facing wording

> "RDP sessions on Windows Server skip the discrete GPU by default. Enable the GPO `Use hardware graphics adapters for all Remote Desktop Services sessions` and reconnect — `dxdiag` should then show the NVIDIA GPU as the active 3D adapter."

---

## GPU-Perf-6: Zooming slow in RDP over GPU

> **TSG**: [Zooming_slow_In_RDP_GPU_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FZooming_slow_In_RDP_GPU_Perf)
> **Scope**: On NV-series VM, customer zooms / pans inside an application (CAD, viewer) over RDP and experiences laggy rendering even though `nvidia-smi` shows the GPU at low utilization.

### GPU-Perf-6.Root cause

- RDP uses `RemoteFX` / `H.264 AVC encoded` codec — the bottleneck is video **encoding** + network bandwidth, not GPU 3D throughput.
- Zoom / pan generates large frame-deltas → encoder spikes → client-side decode + render lags.

### GPU-Perf-6.Fix sequence

1. Enable `Configure H.264/AVC hardware encoding for Remote Desktop connections = Enabled` GPO — offloads encoding from CPU to NVIDIA NVENC.
2. Enable `Prioritize H.264/AVC 444 Graphics mode = Enabled` for higher quality.
3. Test from RDP client with **good network** (low jitter, ≥ 50 Mbps).
4. For high-fidelity workstation experiences, recommend customer evaluate **Azure Virtual Desktop** with multi-session + GPU passthrough.

### GPU-Perf-6.Customer-facing wording

> "Zoom/pan lag over RDP on an NV-series VM is dominated by H.264 encode latency, not by the GPU itself. Please enable the GPO `Configure H.264/AVC hardware encoding for Remote Desktop connections` so the NVIDIA NVENC engine offloads encoding — this typically removes the visible lag."

---

# § LM-Perf — Live Migration perf

## LM-Perf-1: LM-induced freeze / post-LM slowness

> **Scope**: Single freeze of seconds-to-minutes during the LM blackout, or sustained slowness on the *new* host after LM completes.
>
> **See also**: For LM **operational** investigation (TriggerType, defrag rationale, M-Series specifics, on-demand LM workflow, ADH LM contract), use [`playbook-D-maintenance-core.md`](playbook-D-maintenance-core.md) Step 4 → [`playbook-D-maintenance-deep.md`](playbook-D-maintenance-deep.md) § PM-5..8, § LM-Common. Stay here only for the **perf-degradation** angle.

### LM-Perf-1.Q1 — LM session in the window

See [`azurecm-queries.md`](../catalogs/azurecm-queries.md) → **Live Migration** section (`LiveMigrationSessionCompleteLog`, `LiveMigrationContainerDetailsEventLog`).

### LM-Perf-1.Q2 — Did the new host introduce a new bottleneck?

After confirming LM, re-run the core flow's Step 4 (VM shoebox) and Step 5 (host load) **on the destination NodeId** — perf may be fine on source and bad on destination. Common cause: customer moved to a busier host or a host with different ABC config (see STG-Perf-1).

### LM-Perf-1.Q3 — Was a VFP restore failure involved?

See [`vmainsight-queries.md`](../catalogs/vmainsight-queries.md) → **Vmadiag → vfp_restore_fails**. A failed VFP restore can leave the VM running with degraded network state.

### LM-Perf-1.Verdict

- Freeze ≤ 5 s, completes cleanly → expected LM blackout, communicate as such.
- Freeze > 30 s, or sustained slow after LM → check destination host (Q2) + VFP (Q3) + escalate via § STG-Perf-3 if a DPP cut-over also fired.

---

# § MAINT-Perf — Maintenance perf

## MAINT-Perf-1: Host update / VMPHU window

> **Scope**: Customer correlates perf degradation with a planned maintenance / host-plugin update event.
>
> **See also**: For PM **operational** investigation (which VMs were notified, AzPE workflow detail, VMPHU/SSM enrollment, SGX/Decom/Databricks RCA, customer-facing message), use [`playbook-D-maintenance-core.md`](playbook-D-maintenance-core.md) Steps 3+5+8 → [`playbook-D-maintenance-deep.md`](playbook-D-maintenance-deep.md) § PM-1..15, § HOW-1..11. Stay here only for the **perf-degradation** angle.

### MAINT-Perf-1.Q1 — VMPHU customer-impacting events

See [`vmainsight-queries.md`](../catalogs/vmainsight-queries.md) → **Air section** → `GetVMPhuEventsBySubId(...)`. Returns `ImpactBeginTimeStamp / ImpactEndTimeStamp / ImpactDurationTimeSpan` per impacted role instance.

### MAINT-Perf-1.Q2 — AirMaintenanceEvents on the node

```kusto
cluster("vmainsight.kusto.windows.net").database("Air").AirMaintenanceEvents
| where NodeId == "{NodeId}"
| where EventTime between (datetime({StartTime})-1h .. datetime({EndTime})+1h)
| extend Diagnostics = tostring(Diagnostics)
| project EventTime, NodeId, EventCategoryLevel2, EventCategoryLevel3, Component, OutageType, Diagnostics
```

### MAINT-Perf-1.Q3 — AzPE workflow for the operation

See [`operations-queries.md`](../catalogs/operations-queries.md) → **AzPEWorkflowEvent — Host update workflow**.

### MAINT-Perf-1.Customer guidance

- The window is communicated in advance via portal + email (Service Health). Customers can subscribe to **IMDS Scheduled Events** for in-VM advance notice.
- For perf-critical workloads: open a request to disable VMPHU on the subscription (limitations apply, requires PG approval).

---

# § ASAP — SmartNIC / Boost-for-Storage NVMe perf

> **When to use**: VM SKU is **AMD `*_v6` / `*_v7`** or any other **Boost-for-Storage** configuration (uses host-side SmartNIC NVMe-offloaded storage stack), AND the guest reports "hang" / "I/O timeout" / "disk freeze" for tens of seconds — BUT `LogContainerHealthSnapshot`, `VMA`, `KronoxVmOperationEvent`, `TMMgmtNodeFaultEtwTable` all come back **clean** (container Healthy, no SH, no node fault, no VMA RCA hit).
>
> **Why it matters**: An ASAP NVMe Controller Reset on the host produces the exact same in-guest signature (CPU/IO drop to zero) as a brief platform reboot — but the host-side container stays Healthy, so all standard platform-side probes miss it. Geneva CPU/IO graph looks identical to a SH event but Playbook A returns "no platform impact found".
>
> **In-guest tells**: Windows `stornvme` controller reset event in System log; Linux `nvme nvmeX: I/O timeout` / `controller reset` in dmesg. EEE indicator: `ASAP Controller Reset, Message: VfId N`.
>
> **Full reference**: [`asap-storage-queries.md`](../catalogs/asap-storage-queries.md) — cluster `storageclient.eastus.kusto.windows.net/Fa`. The chapters below route into that file's sections.

## ASAP-Perf-1: NVMe Controller Reset — canonical probe

> **Scope**: First query to run on AMD v6/v7 / Boost-for-Storage with guest-hang + clean platform tables.

### ASAP-Perf-1.Q1 — Controller reset / VfId hits on the node

See [`asap-storage-queries.md`](../catalogs/asap-storage-queries.md) → **Canonical controller-reset probe** (`AsapNvmeEtwTraceLogEventView` filtered by `NodeId`, time window, `Message has "Controller Reset" or Message has "VfId"`).

### ASAP-Perf-1.Q2 — Unified PF + KMS + NVMe timeline

See [`asap-storage-queries.md`](../catalogs/asap-storage-queries.md) → **Unified event timeline** (`GetAsapEventsOverlake2(nodeId, startTime, endTime)`, with `union` fallback across `AsapNvmeEtwTraceLogEventView` + `AsapPfEtwTraceLogEventView` + `AsapKmsEtwTraceLogEventView` when the function is unavailable).

### ASAP-Perf-1.Interpretation

- **Any hit on Q1** → host-side ASAP fault. The guest hang is **NOT** a guest OS issue, NOT a VM platform issue in the classic SH/LM/Kronox sense — it is a SmartNIC NVMe-offload fault. **Escalate to EEE Storage team** (provide NodeId, VfId, exact PreciseTimeStamp).
- **Q2 timeline** correlates the controller reset with any preceding PF/KMS/UMED events (e.g., `VM create`, `VF reset`, `namespace attach/detach`, `live migration coordination`) — include in escalation.

### ASAP-Perf-1.Customer-facing wording

Draft the customer-facing RCA manually under category **ContainerFault** (closest existing category; an ASAP-specific category may be added) — keep internal identifiers out. Do NOT use "ServiceHealing" or "VirtualDiskFault" — those are misleading for ASAP resets.

---

## ASAP-Perf-2: Per-disk ASAP counters (latency / IOPS / exceptions)

> **Scope**: After ASAP-Perf-1 confirms the fault scope, drill into the affected disk surface to quantify impact (latency spike, IOPS drop, exception count) for the RCA narrative.

### ASAP-Perf-2.Q1 — Disk metadata + basic perf counters

See [`asap-storage-queries.md`](../catalogs/asap-storage-queries.md) → **`OsAsapCounterTable` — per-disk counters** → **Basic performance counters** + **Counter starter query**. Returns per-disk IOPS, BPS, FO/PO ratios, exception counts, latency.

### ASAP-Perf-2.Q2 — Latency breakdown

See [`asap-storage-queries.md`](../catalogs/asap-storage-queries.md) → **Latency breakdown query** (parses `OsAsapCounterTable` latency histograms into per-disk latency percentile rows).

### ASAP-Perf-2.Q3 — VM → disk surface mapping

See [`asap-storage-queries.md`](../catalogs/asap-storage-queries.md) → `AsapMapVmToDiskOVL2()` (resolves which guest disk/LUN maps to which ASAP surface, when the customer's hang affects only specific disks).

### ASAP-Perf-2.Interpretation

- Exception counter > 0 around the controller-reset timestamp → confirms the reset signature.
- Latency P99 → infinity (sample missing) during the reset window → confirms the IO stall.
- Use the per-disk drilldown to write the customer-facing "your data disk LUN N was impacted from HH:MM:SS for X seconds" line.

---

## ASAP-Perf-3: Node-level ASAP health

> **Scope**: Recurrence check — has this node had repeated ASAP missed-sample windows / counter gaps in the last 30 days? If yes, flag for HW replacement candidate.

### ASAP-Perf-3.Q1 — Node-level counter health

See [`asap-storage-queries.md`](../catalogs/asap-storage-queries.md) → **`OsAsapNodeCounterTable` — node-level health** (missed event windows, latency-sample misses, OsDiag telemetry capture gaps).

### ASAP-Perf-3.Escalation

If this is the second+ ASAP controller reset on the same `NodeId` in 30 days → tag the IcM / collab to **EEE Storage** with "repeat offender" in the title; HW replacement may be warranted.

---

## ASAP-Perf-Disambiguation

| Question | Yes → | No → |
|---|---|---|
| Is the VM SKU `*_v6` / `*_v7` AMD or any other Boost-for-Storage SKU? | Run § ASAP first before § STG-Perf-6 | Skip § ASAP; use § STG-Perf for SCSI-stack VMs |
| Does customer's guest log show `stornvme` reset or `nvme nvmeX: I/O timeout`? | Strong ASAP signal — go straight to ASAP-Perf-1 | Run general perf flow |
| Is the host-side container Healthy + no SH + no NodeFault + no VMA hit, yet guest hung? | High suspicion of ASAP — § ASAP **before** delegating to vm-log-analyzer | Run Playbook A (something platform-side present) |
| EEE shows `ASAP Controller Reset, Message: VfId N`? | Already confirmed — skip ASAP-Perf-1.Q1 and go to ASAP-Perf-2 | Run ASAP-Perf-1.Q1 to confirm |

---

# § Throttling — VM / SKU / Storage rate limits

> **When to use**: Customer reports "VM is slow" / "disk IOPS lower than expected" / "burst not delivered" / "Azure Files share slow", AND Step 4 (VM shoebox) shows the VM CPU/disk/network counters look "normal but capped" rather than under platform impact. Throttling is **expected** behavior when the workload exceeds the SKU's per-VM or storage-account quota — the goal here is to **prove the cap was hit** and tell the customer which limit to raise / which SKU to move to.

## THR-Perf-1: VM disk throttle (Geneva Shoebox %)

> **Scope**: Confirm whether the VM's disk slowness is caused by hitting the **VM-level** Cached / Uncached IOPS or Bandwidth quota (per-VM disk cap from the SKU).

### THR-Perf-1.Q1 — Geneva Shoebox VM perf overview (1-min)

See [`azcore-queries.md`](../catalogs/azcore-queries.md) → **Geneva Shoebox VM Performance Overview (1-min granularity)** → `geneva_metrics_request` query. Returns per-1-min `CachedIOPS_Pct`, `UncachedIOPS_Pct`, `CachedBW_Pct`, `UncachedBW_Pct` columns (0 = no throttle, 100 = capped).

> **Note**: Requires Geneva-enabled Kusto endpoint (e.g., `sparkle.eastus`). Standard ADX cannot execute `geneva_metrics_request`. Region → shoebox account mapping is in the same section.

### THR-Perf-1.Q2 — AzCore 5-minute fallback

See [`azcore-queries.md`](../catalogs/azcore-queries.md) → `VmCounterFiveMinuteRoleInstanceCentralBondTable` — provides 5-min granularity for the same throttle counters when the 1-min Geneva path is not feasible.

### THR-Perf-1.Interpretation

- Any `*_Pct` column saturating at **100%** for sustained intervals (≥ 3 consecutive 1-min buckets) → VM hit the per-VM cap → workload is exceeding SKU limits.
- `CachedIOPS_Pct` saturated but `UncachedIOPS_Pct` low → cache disk is the bottleneck → consider migrating workload to data disk or sizing up.
- Both `CachedIOPS_Pct` + `UncachedIOPS_Pct` simultaneously saturated → the SKU's combined disk quota is the cap → move to a higher SKU family.
- Bandwidth saturated but IOPS not → large block-size workload → BW is the constraint.

### THR-Perf-1.Customer-facing wording

> "From {StartTime} to {EndTime}, your VM's `{IOPS|Bandwidth} Consumed Percentage` metric saturated at 100% for {N} minutes. This is the platform enforcing the per-VM disk quota for SKU `{VmSize}`, not a platform fault. To increase headroom: (1) move to a larger SKU family (e.g., `{NextSku}`) with higher per-VM disk limits, or (2) attach additional data disks to distribute IO load, or (3) enable burst on supported disk SKUs."

---

## THR-Perf-2: VM SKU cached / uncached / network limits reference

> **Scope**: Look up the official per-SKU limit so you can compare against the customer's observed IOPS/BW.

### THR-Perf-2.Q1 — Resolve VM SKU from container

Use [`_shared-vm-identification.md`](../_meta/_shared-vm-identification.md) Q1 to map `ContainerId` → `RoleSize` / `VmSize`.

### THR-Perf-2.Q2 — VM throttle counters list (from properties)

See [`vm-properties-queries.md`](../catalogs/vm-properties-queries.md) → `ThrottleCountersListString` projection (around L200-210). Gives the throttle counters the platform tracks for this disk surface on this VM.

### THR-Perf-2.Public reference

- Per-SKU IOPS / BW caps: <https://learn.microsoft.com/azure/virtual-machines/sizes-general> (and family-specific pages).
- Per-disk SKU caps: <https://learn.microsoft.com/azure/virtual-machines/disks-types>.
- Use the public docs as the customer-facing source of truth. The Kusto queries above only confirm "the cap was hit"; the public docs explain "what the cap is".

---

## THR-Perf-3: Storage account 429 / ServerBusy / account-level throttle

> **Scope**: Customer reports a workload hitting an Azure Storage account (Blob/Queue/Table) is slow / receiving `429 ServerBusy` / `503` responses. This is **not** VM-level — it's storage-account level (egress IOPS, ingress IOPS, ingress BW caps).

### THR-Perf-3.Q1 — XArgus account percentile + throttle counters

See [`storage-account-queries.md`](../catalogs/storage-account-queries.md) → **XArgus section** → `AccountPerfPercentiles5M` + `TenantPerfPercentiles5M`. Returns per-account 5m percentile latency + throttle counts.

### THR-Perf-3.Q2 — ARM-level storage throttling trace

See [`storage-account-queries.md`](../catalogs/storage-account-queries.md) → **Storage Throttling Investigation** → **ARM-Level Storage Throttling Trace** (L365-385 in that file). Surfaces 429 / 503 / ServerBusy from `StorageOperations` over the customer's window.

### THR-Perf-3.Interpretation

- `ServerBusy` / 503 in bursts → account-level capacity exceeded → recommend partitioning workload across multiple storage accounts.
- Sustained throttle on one container or partition → hot-partition problem → reshape blob naming / key naming for better distribution.
- All operations slow + no 429 → not throttle, escalate to XStore (use § STG-Perf-6).

---

## THR-Perf-4: Azure Files metadata throttle

> **Scope**: Customer reports Azure Files share slow specifically on directory listing / file open / metadata operations (not bulk read/write).

### THR-Perf-4.Q1 — Per-share throttle transaction count

See [`storage-account-queries.md`](../catalogs/storage-account-queries.md) → **Azure Files Performance — Metadata Throttling** → `XStoreXFileThrottleTransaction` query (L387-410 area in that file).

### THR-Perf-4.Interpretation

Per-share metadata IOPS has a per-account / per-share cap (Premium vs Standard differs). High `XStoreXFileThrottleTransaction` count → recommend Premium file share (much higher metadata IOPS budget) or splitting workload across multiple shares.

---

## THR-Perf-Disambiguation

| Customer phrase | Likely chapter |
|---|---|
| "VM disk slow / IOPS dropped" + same VM consistently | THR-Perf-1 first (cap?) → § STG-Perf-6 (account latency?) if not capped |
| "Storage account API returns 429 / ServerBusy / 503" | THR-Perf-3 |
| "Azure Files share `ls` / `dir` is slow but read is fine" | THR-Perf-4 |
| "Burst not delivered as documented" | THR-Perf-1 + check disk SKU burst eligibility in public docs |
| "Network throttle / outbound capped" | NET-Perf-2 (excessive outbound) + delegate to networking-queries.md |

---

# § TOOL-Perf — Perf Insights / Performance Diagnostics extension

## TOOL-Perf-1: Managed Identities support in Performance Diagnostics

> **TSG**: [Managed Identities Support in Performance Diagnostics_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FManaged-Identities-Support-in-Performance-Diagnostics_Perf)
> **Scope**: Customer enables Performance Diagnostics extension on a VM with Managed Identity (system-assigned or user-assigned) and the extension fails to upload the resulting trace.

### TOOL-Perf-1.Required role assignment

The MI principal must have **Storage Blob Data Contributor** on the storage account specified at extension install time. If the extension was deployed before the MI was assigned, re-run the extension after assigning the role.

### TOOL-Perf-1.Common error patterns

- `Authorization failed for the request. (403)` in the extension status JSON → role missing.
- `Storage account not found` → wrong storage-account name / customer chose a private endpoint without DNS resolution from the VM.
- Trusted-Launch + UEFI secure boot + MI all on → ensure extension version supports TVM (check extension version ≥ minimum noted in MS Learn).

### TOOL-Perf-1.Customer-facing wording

> "Performance Diagnostics extension uses the VM's Managed Identity to upload traces. Please grant the MI the **Storage Blob Data Contributor** role on the destination storage account and re-run the extension. If you continue to see 403 errors after granting the role, share the extension's status JSON from `C:\WindowsAzure\Logs\Plugins\Microsoft.Azure.Performance.Diagnostics.AzurePerformanceDiagnostics\` (Windows) or `/var/log/azure/Microsoft.Azure.Performance.Diagnostics.AzurePerformanceDiagnosticsLinux/` (Linux)."

---

## TOOL-Perf-2: Perf Insights — KeyBasedAuthenticationNotPermitted

> **TSG**: [Perf Inisghts - KeyBasedAuthenticationNotPermitted_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FPerf-Inisghts---KeyBasedAuthenticationNotPermitted_Perf) *(typo "Inisghts" preserved from wiki)*
> **Scope**: Performance Diagnostics extension fails with `KeyBasedAuthenticationNotPermitted` when uploading to a storage account that has `allowSharedKeyAccess = false` (entra-id-only storage account policy).

### TOOL-Perf-2.Root cause

Older versions of the extension uploaded with storage-account key auth; if the storage account disabled shared-key access, upload fails. Newer extension versions use AAD token via MI (TOOL-Perf-1).

### TOOL-Perf-2.Fix

- Upgrade the Performance Diagnostics extension to the latest version (supports MI / AAD upload).
- Assign **Storage Blob Data Contributor** to the VM MI on the target storage account (see TOOL-Perf-1).
- Alternatively, allow shared-key access on the storage account (`Set-AzStorageAccount -AllowSharedKeyAccess $true`) — not recommended for security-sensitive accounts.

### TOOL-Perf-2.Customer-facing wording

> "The error `KeyBasedAuthenticationNotPermitted` is raised because your storage account has `allowSharedKeyAccess = false` and the Performance Diagnostics extension version you have only supports shared-key upload. Please upgrade the extension to the latest version (which uses Managed Identity / AAD) and grant the VM's MI the Storage Blob Data Contributor role on the target storage account."

---

## TOOL-Perf-3: Performance InformationMessage OnDisk page interpretation

> **TSG**: [Performance InformationMessage OnDisk Page_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FPerformance-InformationMessage-OnDisk-Page_Perf)
> **Scope**: Performance Diagnostics HTML report shows an `InformationMessage` on the OnDisk page that the customer interprets as a finding. These messages are guidance text, not findings — most are non-actionable.

### TOOL-Perf-3.Common Information messages

| Message | Meaning | Action |
|---|---|---|
| `Latency counter not available for disk N` | NVMe controller — see STG-Perf-10 | None — known limitation |
| `Cache mode = None` | Disk cache disabled — see STG-Perf-8 | Inform customer; switch only if read-heavy |
| `Burst not enabled` | Premium SSD eligible for burst but customer hasn't enabled Performance Plus | Cross-link STG-Perf-13 |
| `Disk SKU < workload spec` | Customer's IOPS target exceeds SKU cap | Recommend upgrade or stripe with multiple disks |

### TOOL-Perf-3.Customer-facing wording

> "The OnDisk page `InformationMessage` block contains guidance / context — it is not an error or platform fault. {cite the specific message} indicates {explanation}; recommended action is {action_or_none}."

---

# § MISC-Perf — Misc

## MISC-Perf-1: AzCLI commands slow inside Docker container

> **TSG**: [AzCLI Commands Slow Docker Container_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FAzCLI-Commands-Slow-Docker-Container_Perf)
> **Scope**: Customer runs `az ...` commands from inside a Docker container on an Azure VM and observes ~10x slower response than on the host. Not a platform/VM perf issue — Docker DNS / network stack.

### MISC-Perf-1.Root cause + fix

- Container default DNS = `127.0.0.11` (Docker embedded DNS) → fallback chain on cache miss adds 5-30s delay.
- Fix: pass `--dns 168.63.129.16` (Azure WireServer DNS) or `--dns 8.8.8.8` to `docker run`, OR configure `/etc/docker/daemon.json` with `"dns": ["168.63.129.16"]`.
- Alternative: use `--network host` to skip Docker bridge (security trade-off).

### MISC-Perf-1.Customer-facing wording

> "AzCLI inside the container is hitting DNS resolution timeouts on the Docker embedded resolver. Run the container with `--dns 168.63.129.16` (Azure platform DNS) or update `/etc/docker/daemon.json`. This is a Docker network configuration issue, not an Azure VM platform fault."

---

## MISC-Perf-2: Discrepancy between VM and Portal metrics

> **TSG**: [Discrepancy between VM & Portal Metrics_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FDiscrepancy-between-VM-%26-Portal-Metrics_Perf)
> **Scope**: Customer compares in-guest perfmon / `top` / `iostat` numbers with Azure portal metrics for the same VM and sees different values. Sampling/aggregation rules differ — usually not a defect.

### MISC-Perf-2.Key differences

| Metric | In-guest source | Portal source | Why different |
|---|---|---|---|
| CPU % | Per-second OS scheduler | 1-min host-side aggregate | Smoothing flattens spikes |
| Disk IOPS | Per-second perfmon | 1-min host-side cooked counter | Burst credits + cache hits handled differently |
| Network bytes | Guest NIC counter | Host vNIC counter | Exception packets / VFP-injected traffic counted differently |
| Available Memory | Guest Memory Manager | Host hyperv counter via dmvsc | dmvsc may report 0 — see MEM-Perf-1 |

### MISC-Perf-2.Customer-facing wording

> "Guest-side counters and Azure Monitor metrics use different sampling rates and different observation points (guest OS vs host vNIC vs platform counter). Small discrepancies (~5–15%) are expected. Large discrepancies in a specific direction (e.g., portal shows 0 when guest shows 50%) usually point to a specific known issue — see MEM-Perf-1 for memory, NET-Perf-2 for network bytes."

---

## MISC-Perf-3: VM SKU cached limits lookup

> **TSG**: [VM SKU Cached Limits_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FVM-SKU-Cached-Limits_Perf)
> **Scope**: Lookup pointer for the official per-SKU `Cached IOPS`, `Cached BW`, `Uncached IOPS`, `Uncached BW`, `Max NICs`, `Max bandwidth` table. This is the canonical reference for THR-Perf-1 (disk throttle) and THR-Perf-2 (SKU limits).

### MISC-Perf-3.Official doc roots

| SKU family | Public doc |
|---|---|
| General purpose Dv5 / Dasv5 / Dadsv5 | <https://learn.microsoft.com/azure/virtual-machines/sizes/general-purpose/> |
| Memory optimized Ev5 | <https://learn.microsoft.com/azure/virtual-machines/sizes/memory-optimized/> |
| Storage optimized Lsv3 / Lasv3 | <https://learn.microsoft.com/azure/virtual-machines/sizes/storage-optimized/> |
| HPC / N-series GPU | <https://learn.microsoft.com/azure/virtual-machines/sizes/gpu-accelerated/> |
| Specialty SKUs (`Mv3`, `HBv4`, `NCadsH100v5`) | Per-SKU pages under <https://learn.microsoft.com/azure/virtual-machines/sizes/> |

### MISC-Perf-3.Cross-ref

For authoritative per-SKU contracts always quote the public docs above — they are sourced from the same Capacity/CRP service catalog as the customer-facing portal. If the customer observes throttling at numbers that disagree with the public doc (rare, may happen briefly during SKU launches), delegate to [`vm-kusto-query`](../../../vm-kusto-query/SKILL.md) to query `crp_allprod` SKU snapshot tables directly and reconcile.

---

# § OS-Perf-Linux — Linux guest (delegates)

## OS-Perf-Linux-1: NVMe troubleshooting (Linux guest)

> **TSG**: [NVMe troubleshooting_Linux](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FNVMe-troubleshooting_Linux)
> **Scope**: Linux guest on NVMe-controller SKU (Ebsv5 / Ebdsv5 / Easv6 etc.) reports NVMe timeouts, link resets, disk drops. Two distinct paths:
> 1. **Platform-side NVMe controller reset** (ASAP-induced) → § ASAP + `asap-storage-queries.md`.
> 2. **In-guest NVMe stack tuning** (queue depth, IO scheduler, multiqueue) → use `asap-storage-queries.md` for platform-side NVMe checks and [`vm-log-analyzer`](../../../vm-log-analyzer/SKILL.md) for `dmesg` / `journalctl -k` / sosreport NVMe trace analysis.

### OS-Perf-Linux-1.Quick guest-side checks

```bash
nvme list                                  # confirm controller(s) visible
nvme smart-log /dev/nvme0                  # health + media errors
dmesg | grep -iE "nvme|abort|reset" | tail
cat /sys/block/nvme0n1/queue/scheduler     # 'none' recommended for NVMe
cat /sys/block/nvme0n1/queue/nr_requests
```

### OS-Perf-Linux-1.Customer guidance

> "Please share output of `nvme list`, `nvme smart-log` for each controller, and `dmesg | grep -i nvme` covering the issue window. Also `journalctl -k -S '{issue start}' -U '{issue end}'`. We will distinguish a platform-side NVMe controller reset (ASAP, would show in host telemetry) from in-guest stack tuning issues."

---

## OS-Perf-Linux-2: OOM Killer (Linux guest)

> **TSG**: [OOM Killer Linux_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM?pagePath=%2FSME-Topics%2FPerformance%2FTSGs%2FOOM-Killer-Linux_Perf)
> **Scope**: Linux guest's OOM-killer fired and killed a process (`dmesg | grep -i 'killed process'`). This is a guest-side memory pressure event — platform is NOT involved (no host-side eviction on Azure VMs).

### OS-Perf-Linux-2.Required data

Delegate to [`vm-log-analyzer`](../../../vm-log-analyzer/SKILL.md):

- `dmesg -T | grep -A 50 -i 'killed process'` — captures the kill event + memory stats at time of OOM.
- `/var/log/syslog` or `journalctl -k` covering ±30 min around OOM timestamp.
- `cat /proc/meminfo` snapshot (if reproducible).
- `ps auxf` to identify long-running processes that may have leaked.

### OS-Perf-Linux-2.Common causes

1. Application memory leak (Java / Node.js / Python service).
2. `tmpfs` / `/run` / `/dev/shm` writes filling RAM.
3. `vm.overcommit_memory = 1` + large allocations failing silently until OOM.
4. cgroup memory limit too low for container workload.

### OS-Perf-Linux-2.Customer-facing wording

> "OOM Killer events are triggered by the Linux kernel inside the guest when memory pressure exceeds available RAM + swap — the Azure platform does not evict / kill guest processes. Please share the `dmesg -T | grep -A 50 'killed process'` output and `/var/log/syslog` covering the OOM timestamp; we'll identify the offending process and recommend either configuration tuning or a larger SKU."

---

# § GUEST — Guest OS perf (out of scope)

If the core playbook Step 4 shows **all VM counters are normal but the customer still reports slowness**, the bottleneck is inside the guest. Examples: antivirus scan, scheduled task, driver issue, paging pressure, app-level lock contention, kernel softlockup, fragmented filesystem.

**Action:** delegate to the [`vm-log-analyzer`](../../../vm-log-analyzer/SKILL.md) skill with the customer's guest-side artifacts (perfmon, ETW, sosreport, supportconfig, eventvwr, journalctl). Do not continue in this playbook.

---

## Cross-references summary

| Symptom | Primary playbook section | Primary reference file(s) | Source TSG |
|---|---|---|---|
| Missing disk metrics | STG-Perf-1 | `azurecm-queries.md` (LogNodeSnapshot) | Disk Metrics_Perf |
| Premium MD slow (~5+ ms) | STG-Perf-2 | `crp-queries.md` (VMApiQosEvent colocation) | Disk Collocation_Perf |
| Random N-second freeze | STG-Perf-3 + LM-Perf-1 | `azurecm-queries.md` (ServiceVersionSwitch) + `operations-queries.md` (AzPEWorkflowEvent / GetSimpleDeploymentProgress) | Datapath Update Impact_Perf |
| Cache disk burst / Event 16 | STG-Perf-4 | `azcore-queries.md` (OsVhddiskEventTable + WindowsEventTable) | Local Disk Investigation_Perf |
| WS2012R2 resource VHD <10 MB/s | STG-Perf-4.Q5 | `azcore-queries.md` (WindowsEventTable EventId 12817) | Poor IO Performance on Windows Server 2012 R2_Perf |
| Write congestion / BSPausedWrites | STG-Perf-5 | `azcore-queries.md` (OsBlobCacheInternalCounterTable) | Blob Cache Write Congestion_Perf |
| Account / tenant latency | STG-Perf-6 | `storage-account-queries.md` (XArgus + XStore triage) | — (delegate XStore) |
| VM Availability Metric missing | STG-Perf-7 | `aplat-queries.md` (Kyber tables) | VM Availability Metric missing_Perf |
| Disk cache policy / ReadOnly vs ReadWrite question | STG-Perf-8 | — (config + customer guidance) | Disk Cache_Perf |
| ABC host but cache=None (lower IOPS than expected) | STG-Perf-9 | `azurecm-queries.md` (LogNodeSnapshot diskConfiguration) | Host Caching Not Enabled_Perf |
| Windows PerfCounter `Avg Disk sec/Read|Write` empty on NVMe controller | STG-Perf-10 | — (guest-side ETW) | Disk Latency Counter Not Available NVME Controller_Perf |
| OsVhddiskEventTable Event 47 | STG-Perf-11 | `azcore-queries.md` (OsVhddiskEventTable EventId 47) | VhdDiskPr Event 47 Investigation_Perf |
| Benchmark IOPS far below SKU cap + QD=1 | STG-Perf-12 | — (customer benchmark guidance) | Queue Depth constantly 1_Perf |
| Customer asks to enable Performance Plus | STG-Perf-13 | — (`az disk create --performance-plus true`) | Enabling Performance Plus_Perf |
| Use ASI dashboards to triage disk | STG-Perf-14 | [`../dashboards/`](../dashboards/) | Troubleshooting Disk using ASI_Perf |
| Ultra / PremiumV2 disk slow (Yarrow / ESAN) | STG-Perf-15 | `storage-account-queries.md` (Elastic SAN) + Tenant Health Dashboard | Troubleshooting Ultra and PremiumV2 Disks using Tenant Health Dashboard_Perf |
| Network RTT / TCP retrans | NET-Perf-1 | `networking-queries.md` (AzPingMeshServerStatus) | Host Node Investigation_Perf |
| Huge outbound + metric gap (breach) | NET-Perf-2 | dashboards only (vmdash / NetVMA / SlbHpMDMAccount) | Excessive Network Out Usage_Perf |
| Host networking rollout induced blip | NET-Perf-3 | `hybridnetworking` cluster (NetMonComponentRolloutEvents) + `vmainsight-queries.md` (Vmadiag → vfp_restore_fails) | Host Networking Updates_Perf |
| CPU bound / noisy neighbor (platform) | CPU-Perf-1 | `azcore-queries.md` (VmCounter*) + `azurecm-queries.md` (LogContainerSnapshot co-tenants) | — |
| High CPU inside guest (platform clean) | CPU-Perf-2 | — (delegate `vm-log-analyzer` + Perf Diag) | Troubleshoot High CPU_Perf |
| Two same-SKU VMs report different CPU GHz | CPU-Perf-3 | `wdgeventstore-queries.md` (nodes hardware lookup) | CPU SKU Clock difference_Perf |
| vCPU vs physical core / HT confusion | CPU-Perf-4 | — (SKU spec lookup) | Incorrect CPU Core Hyperthreading_Perf |
| "Available Memory" metric missing | MEM-Perf-1 | `wdgeventstore-queries.md` (HostOSDeploy.nodes) | Available Memory shows 0GB_Perf |
| Windows guest low memory (general) | MEM-Perf-2 | — (Perf Diag Memory Trace + RAMMap + poolmon) | Low Memory Windows Troubleshooting_Perf |
| Windows ~2 GB Available Memory missing | MEM-Perf-3 | — (`bcdedit` Hyper-V check) | 2GB Low Memory Windows Troubleshooting_Perf |
| 2 GB reserved (fallback investigation) | MEM-Perf-4 | — (Hyper-V + dump file + AppGuard checks) | Reserved Memory 2gb windows_perf |
| Task Manager "Hardware Reserved" | MEM-Perf-5 | — (customer wording) | Memory Hardware Reserved in Windows_Perf |
| Trusted Launch VM 50 MB less Available Memory | MEM-Perf-6 | — (customer wording) | Available Memory 50MB Less TrustedVM_Perf |
| VM hung / frozen but platform reports Running | HANG-Perf-1 | core flow Step 2/3/6 + `vm-log-analyzer` (NMI dump / procdump) + § ASAP cross-check | Troubleshoot VM Hung or Frozen_Perf |
| Brand new to N-series GPU VMs | GPU-Perf-1 | — (SKU + driver orientation) | NC and NV-series Virtual Machines_Perf |
| Linux `nvidia-smi` reports "No devices found" | GPU-Perf-2 | — (`lspci`, `dmesg`, extension log) | Linux N-Series VMs Not Detecting GPUs_Perf |
| Linux GPU low SM utilization / P8 stuck | GPU-Perf-3 | — (`nvidia-smi -pm 1`, persistence mode) | Linux GPU Nvidia Slow_Perf |
| Windows CUDA `cudaGetDeviceCount = 0` | GPU-Perf-4 | — (Tesla driver + CUDA toolkit + deviceQuery) | Windows GPU CUDA_Perf |
| Windows app rendering on WARP not NVIDIA | GPU-Perf-5 | — (RDP GPO + per-app GPU pref + GRID licensing) | Graphics Application not using NV GPU_Perf |
| RDP zoom/pan laggy on NV-series | GPU-Perf-6 | — (H.264 NVENC GPO) | Zooming_slow_In_RDP_GPU_Perf |
| LM-related slow | LM-Perf-1 | `azurecm-queries.md` (LM section) + `vmainsight-queries.md` (Vmadiag) | — |
| Planned maintenance | MAINT-Perf-1 | `vmainsight-queries.md` (Air) + `operations-queries.md` (AzPE) | — |
| ASAP NVMe controller reset (AMD v6/v7 / Boost-for-Storage) | ASAP-Perf-1 / -2 / -3 | `asap-storage-queries.md` | — (custom, not in csswiki) |
| VM disk throttle (Cached/Uncached IOPS% saturated) | THR-Perf-1 / -2 | `azcore-queries.md` (Geneva Shoebox `geneva_metrics_request`) + `vm-properties-queries.md` (ThrottleCounters) | — (custom) |
| Storage account 429 / ServerBusy | THR-Perf-3 | `storage-account-queries.md` (XArgus + ARM throttling trace) | — (custom) |
| Azure Files metadata throttle | THR-Perf-4 | `storage-account-queries.md` (Azure Files metadata throttle) | — (custom) |
| Perf Diagnostics extension 403 to storage account | TOOL-Perf-1 | — (MI + Storage Blob Data Contributor role) | Managed Identities Support in Performance Diagnostics_Perf |
| Perf Diag extension `KeyBasedAuthenticationNotPermitted` | TOOL-Perf-2 | — (upgrade extension + MI) | Perf Inisghts - KeyBasedAuthenticationNotPermitted_Perf |
| Perf Diag OnDisk InformationMessage interpretation | TOOL-Perf-3 | — (message reference table) | Performance InformationMessage OnDisk Page_Perf |
| AzCLI slow inside Docker container | MISC-Perf-1 | — (Docker DNS configuration) | AzCLI Commands Slow Docker Container_Perf |
| In-guest vs portal metric discrepancy | MISC-Perf-2 | — (sampling differences explanation) | Discrepancy between VM & Portal Metrics_Perf |
| VM SKU cached/uncached limits lookup | MISC-Perf-3 | Public docs (`learn.microsoft.com/azure/virtual-machines/sizes/`) — reconcile via `crp_allprod` SKU snapshot only if customer observation disagrees | VM SKU Cached Limits_Perf |
| Linux NVMe timeouts / resets | OS-Perf-Linux-1 | `asap-storage-queries.md` (platform side) + `vm-log-analyzer` (guest dmesg/journalctl) | NVMe troubleshooting_Linux |
| Linux OOM Killer fired | OS-Perf-Linux-2 | `vm-log-analyzer` (dmesg / syslog OOM analysis) | OOM Killer Linux_Perf |
| Guest OS bottleneck | GUEST (delegate) | `vm-log-analyzer` skill | — |

---

## Standard variables (paste at top of every notebook)

```kusto
//{SubscriptionId}, {VMName}, {ResourceGroupName}, {NodeId}, {ContainerId}, {VMId}, {TenantName}, {Cluster}
//{StartTime} format 2026-06-01 14:30:00Z (subtract 30m-1h from reported start)
//{EndTime}   format 2026-06-01 17:30:00Z (add 30m-1h to reported end)
//{Symptom}   one of: DiskLatency / DiskIOPS-BW / CPU / Network / IntermittentBlip / PostMaintBlip / MissingMetrics / ASAP / Throttling
//For STG-Perf-3 region rollout:
//  {BuildLabel}  e.g. 'Datapath_7_10_0_173_153_10_0_173'
//  {RegionList}  e.g. 'uksouth', 'asiaeast', 'japaneast'
```
