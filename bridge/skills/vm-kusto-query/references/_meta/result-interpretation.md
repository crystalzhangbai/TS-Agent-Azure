# Result Interpretation — pivot query → next step

> What each "hub" KQL's result means, and which anchor/playbook section to jump to next. Lives in the **S3 INTERPRET** state of [`investigation-loop.md`](investigation-loop.md). Every entry follows the same shape:
>
> **rowCount == 0** rule · **non-empty rules** keyed by a column value · **branch target** (`§ANCHOR` in deep file, or another pivot query).
>
> Pivot queries are the ~15 KQL across the platform whose result determines what to look at next. They are NOT all the queries — they are the **decision points**. Non-pivot KQL is interpreted in-place inside the playbook narrative.

---

## 1. VMA — Platform RCA classification

**Source**: [`catalogs/vmainsight-queries.md`](../catalogs/vmainsight-queries.md) § VMA, used at Playbook A Step 2.
**Cluster.DB.Table**: `Vmainsight.vmadb.VMA`
**Pivot column**: `RCALevel1`

| `RCALevel1` | Meaning | Next step |
|---|---|---|
| (rowCount == 0) | No platform-side RCA — either guest-side issue or wrong time window | Widen `_t1` by 4h; if still empty → Playbook A Step 5 (guest) + hand off to vm-log-analyzer |
| `HostOSCrash` | Host BSOD | `playbook-A-restarts-deep.md` § SW: Host Node Bugcheck + § SW: 0xEF |
| `NodeFault` / `UnhealthyNode_*` | Fabric power-cycled hung node | § SW: PowerCycle Unhealthy Node + § SW: Unhealthy Node Investigation |
| `Hardware*` (Disk/Memory/CPU/IERR/Network/PCIe) | HW fault confirmed | § HW family (match RCALevel2 to specific TSG) |
| `ServiceHealing*` + FaultCode `10005` / `0x80078000` | Blob cache + bad disk | § Storage: Blob Cache (FC 10005) |
| `ServiceHealing*` + FaultCode `10036` | NVA AN Boost SoC OOM | § HW: AN Overlake SoC (FC 10036) |
| `LiveMigration*` → `VFPRestoreFailure` | VFP state restore failed | § Storage: VFP Restore Failure (NMAgent 356) |
| `HostUpdate*` / `DataPathHostPluginUpdate` / `NmAgent` | Maintenance | § Maint: Host Update chain (cross-link Playbook D) |
| `IaaSxStoreOutage` / `Event17` | XStore backend disk fault | § Storage: E17 + XStore Triage |
| `ContainerFault` (generic) | Drill into `RCALevel2` | Run § Pivot #2 (LogContainerHealthSnapshot) for `faultInfo` |
| `Inconclusive` / empty | No fault recorded | Step 5 (guest OS) |

After picking the right `RCALevel1.RCALevel2` pair: run `GetArticleIdByFailureSignature("<L1.L2>")` to fetch the customer-RCA article ID.

---

## 2. LogContainerHealthSnapshot — Container state + faultInfo

**Source**: [`catalogs/azurecm-queries.md`](../catalogs/azurecm-queries.md) § Container Health, used at Playbook A Step 4.
**Cluster.DB.Table**: `Azcsupfollower.AzureCM.LogContainerHealthSnapshot`
**Pivot columns**: `containerOsState`, `faultInfo`, `containerLifecycleState`

| Signal | Meaning | Next step |
|---|---|---|
| (rowCount == 0 over impact window) | Container never went unhealthy during window | RCA is NOT a container fault. Re-check VMA (#1) and TMMgmtRoleInstanceDowntimeEventEtwTable (#5) |
| `containerOsState == "ContainerOsStateUnresponsive"` | Guest OS hung | Hand off to **vm-log-analyzer** (guest dump) + Playbook A § SW: Unhealthy Node |
| `containerOsState == "GuestOsStateProvisioningRecovery"` | Guest provisioning loop | Playbook A § SW: Provisioning Recovery or Playbook B § OP-OSPTO |
| `faultInfo.FaultCode == 10005` + `0x80078000` | Blob cache + bad disk | Playbook A § Storage: Blob Cache |
| `faultInfo.FaultCode == 10036` | AN Overlake SoC OOM | Playbook A § HW: AN Overlake SoC |
| `faultInfo.OrangeType == "Unallocatable_ResetNodeHealth"` | Host marked Unallocatable | Playbook A § SW: Host Node Marked Unallocatable |
| `faultInfo.FaultCode == 7011` | XStore unavailable | Playbook A § Storage: E17 + XStore Triage |
| `faultInfo.code` contains `NetworkUnavailable` | Networking | [`catalogs/networking-queries.md`](../catalogs/networking-queries.md) § VFP |
| `faultInfo.code` contains `HostUnresponsive` | Host hung | Playbook A § SW: PowerCycle Unhealthy Node |
| `containerLifecycleState == "Deleted"` mid-window | VM was deleted by control plane | Pivot to #6 (CRP CrpOperationQoSEtwTable) to find caller |
| `containerLifecycleState` flips → new `containerId` appears | VM was Service Healed (host change) | Run § Pivot #4 (ServiceHealingTriggerEtwTable) for trigger |

---

## 3. LogContainerSnapshot — VM ↔ Node identity

**Source**: [`catalogs/azurecm-queries.md`](../catalogs/azurecm-queries.md) § Container Snapshot, used at Playbook A Step 1.
**Cluster.DB.Table**: `Azcsupfollower.AzureCM.LogContainerSnapshot`
**Pivot column**: `containerId` × time

| Signal | Meaning | Next step |
|---|---|---|
| (rowCount == 0) | Wrong sub/VM or VM never landed on a host | Verify resource exists; check `vmainsight.vmadb.VMA` with looser filter |
| Single stable `containerId` over window | VM stayed on same host the whole time | Continue with Step 2 (VMA) |
| `creationTime` shifts mid-window | VM was Service Healed or Live Migrated | Note OLD & NEW `containerId` / `nodeId`. Branch to LM session check (`LiveMigrationSessionCompleteLog`) and SH trigger (#4) |
| Multiple `containerId` in window with distinct `nodeId` | Same as above, host changed | Same as above |
| `containerType == "Tenant"` (rare) | Classic VM | Use rdfeprod cluster, not azcrp |

---

## 4. ServiceHealingTriggerEtwTable — Why was the VM healed

**Cluster.DB.Table**: `AzureCM.AzureCM.ServiceHealingTriggerEtwTable`
**Pivot columns**: `TriggerType`, `FaultCode`, `FaultReason`

| Signal | Meaning | Next step |
|---|---|---|
| (rowCount == 0) | No SH happened in window — VM stayed put (or LM, check `LiveMigrationSessionCompleteLog` separately) | If `containerId` did change, run [`catalogs/azurecm-queries.md`](../catalogs/azurecm-queries.md) § LM |
| `TriggerType == "FaultInjection"` | Engineer manually triggered SH (testing / mitigation) | Check `IcMDataWarehouse` for parent ICM (ops-side action) |
| `TriggerType == "Defrag"` | Capacity defrag rebalance | Playbook D § PM-1 (no fault, scheduled work) |
| `TriggerType == "OnDemand"` | Customer or PG-triggered | Check `KronoxVmOperationEvent` (#7) for who called it |
| `TriggerType == "PlannedMaintenance"` | Maintenance-driven SH | Playbook D § PM-15 |
| `FaultCode == 10005` | Blob cache + bad disk | Playbook A § Storage: Blob Cache |
| `FaultCode == 10036` | NVA OOM | Playbook A § HW: AN Overlake SoC |
| Other `FaultCode` non-zero | Look up code in Hawkeye Wiki | Cross-link to `hardware-queries.md` for SEL correlation |

---

## 5. TMMgmtRoleInstanceDowntimeEventEtwTable — Was there platform downtime

**Cluster.DB.Table**: `Azcsupfollower.AzureCM.TMMgmtRoleInstanceDowntimeEventEtwTable`
**Pivot columns**: `DowntimeReason`, `DowntimeStartTime`/`DowntimeEndTime`

| Signal | Meaning | Next step |
|---|---|---|
| (rowCount == 0 over window) | No platform downtime — VM impact is guest-side or network-only | Hand off to vm-log-analyzer; if customer insists on impact, run VFP / SLB queries |
| `DowntimeReason == "ServiceHealing"` | Confirmed SH downtime | Pivot to #4 (ServiceHealingTriggerEtwTable) |
| `DowntimeReason == "Maintenance"` / `HostUpdate` | Planned maintenance | Playbook D § PM-* |
| `DowntimeReason == "Reboot"` | Platform reboot | Pivot to #7 (KronoxVmOperationEvent) for caller |
| `DowntimeReason == "MemoryPreservingMaintenance"` | MPR / brownout | Playbook D § PM-5 (no impact RCA needed; explain to customer) |
| Duration > 10 min | Long downtime, likely fault | Continue with VMA (#1) for cause |
| Duration < 30 s | Short downtime — could be data path | Pivot to networking-queries.md if customer reports connectivity blip |

---

## 6. CrpOperationQoSEtwTable — Did the CRP op succeed

**Source**: [`catalogs/crp-queries.md`](../catalogs/crp-queries.md) § CRP Operations, used by Playbook B / D / E / F / G / H.
**Cluster.DB.Table**: `crp.CrpService.CrpOperationQoSEtwTable`
**Pivot columns**: `resultCode`, `errorCode`, `operationName`

| Signal | Meaning | Next step |
|---|---|---|
| (rowCount == 0 with correct `correlationRequestId`) | The op went to ARM but not CRP — pivot to `armprodgbl.eastus.ARMProd.HttpIncomingRequests` | Check § OP-Throttle / § OP-RBAC / § OP-Policy |
| `resultCode == "Success"` | Op succeeded — the failure must be downstream (extension, guest, network) | Check `ApiQosEvent_nonGet` for sub-steps + hand off to Playbook H if extension related |
| `errorCode == "AllocationFailed"` / `OverconstrainedAllocationRequest` / `ZonalAllocationFailed` | Capacity / placement | Playbook B § OP-Allocation + `CRPAllocationDetailsEtwTable` |
| `errorCode == "OSProvisioningTimedOut"` | Guest agent never reported Ready | Playbook B § OP-OSPTO + check `GuestOsKVPItems` |
| `errorCode == "VMStartTimedOut"` / `OutOfTimeBudgetException` | Start timeout — host/disk slow | Playbook B § OP-StartTimeout |
| `errorCode == "FabricInternalOperationError"` | CRP↔Fabric communication | Playbook B § OP-FabricTimeout |
| `errorCode == "InternalDiskManagementError"` / `AcquireDiskLeaseFailed` | Disk issue | Playbook B § OP-DiskMgmt / § OP-DiskLease + Playbook F § MD-* |
| `errorCode == "RequestDisallowedByPolicy"` | Azure Policy | Playbook B § OP-Policy / Playbook H § AGEX-Ext-AzurePolicy |
| `errorCode == "TooManyRequests"` / 429 | Throttle | Playbook B § OP-Throttle |
| `errorCode == "ResourceNotFound"` for delete | Already deleted | No action |
| Other `errorCode` not in Playbook B | New error code | Schema-explore CRP for parent `ContextActivity` then write a one-off; if the error code is recurring, add a routing row to Playbook B |
| `durationInMilliseconds > 900000` (15 min) | Op timed out | Likely a downstream resource hang — cross-reference with disks / network |

---

## 7. KronoxVmOperationEvent — Platform-initiated VM operation

**Cluster.DB.Table**: `Azcsupfollower.AzureCM.KronoxVmOperationEvent`
**Pivot columns**: `Operation`, `TriggerType`, `Initiator`

| Signal | Meaning | Next step |
|---|---|---|
| (rowCount == 0) | No platform op — customer-initiated or no op at all | Check `CrpOperationQoSEtwTable` (#6) for customer-initiated ops |
| `Initiator == "Customer"` | Customer used Portal/CLI/PS | Pivot to `CrpOperationQoSEtwTable` for the ARM trace |
| `Initiator == "PlatformMaintenance"` | Maintenance reboot | Playbook D § PM-* |
| `Initiator == "ServiceHealing"` | SH reboot | Pivot to #4 (ServiceHealingTriggerEtwTable) |
| `Initiator == "InternalPowerOff"` / `FabricCallback InternalPowerOffVMOperation` | Host had Hyper-V Worker memory failure | Playbook B § OP-FabricInternalPowerOff + check `WindowsEventTable` Hyper-V EventId 12030 / 3122 / 3050 |
| `Operation == "Reboot"` + `AllowLM == false` | Reboot was forced (no LM) | Playbook A § SW or § MAINT |

---

## 8. LogNodeSnapshot — Host node state

**Cluster.DB.Table**: `Azcsupfollower.AzureCM.LogNodeSnapshot`
**Pivot columns**: `nodeState`, `nodeAvailabilityState`, `faultInfo`

| Signal | Meaning | Next step |
|---|---|---|
| (rowCount == 0) | Wrong `nodeId` or out of retention | Re-derive `nodeId` from `LogContainerSnapshot` (#3) |
| `nodeAvailabilityState == "Unallocatable"` | Host marked bad | Playbook A § SW: Host Node Marked Unallocatable |
| `nodeState == "Ready"` throughout | Host healthy — issue is per-container, not per-node | Stay in container-level tables |
| `faultInfo.OrangeType == "OFR_*"` | Out-of-Fabric Repair | Pivot to `hardware-queries.md` for HW replacement record |
| `containerCount` drops to 0 in window | Host evacuated (all VMs moved) | Check `vmainsight.Air.AirManagedEvents` for the maintenance event |
| `diskConfiguration` changes | Host disk swap | Hardware repair — cross-link `hardware-queries.md` |
| `rootUpdateAllocationType` non-null | Host being updated | Playbook D § PM-HostUpdate |

---

## 9. AirManagedEvents — Maintenance / SH at the host

**Cluster.DB.Table**: `vmainsight.Air.AirManagedEvents`
**Pivot columns**: `EventCategory`, `TriggerType`, `EventStatus`

| Signal | Meaning | Next step |
|---|---|---|
| (rowCount == 0) | No maintenance | If VM still rebooted, branch to #1 (VMA) — not maintenance |
| `TriggerType == "Decom"` | Hardware decommissioning | Playbook D § PM-2 / § HOW-9 |
| `TriggerType == "ServiceHealing"` + `EventCategory == "PlannedMaintenance"` | SSM expired → forced SH | Playbook D § PM-15 → Playbook A § MAINT-1 |
| `TriggerType == "OnDemand"` | Engineer-initiated | Check ICM for parent incident |
| `EventStatus == "Started"` only (never "Completed") | Maintenance stuck | Playbook D § PM-12 + escalate to Air/AzPE team |
| `EventCategory == "Defrag"` | Rebalance | Playbook D § PM-1 |

---

## 10. ApiQosEvent_nonGet (CRP detailed trace)

**Cluster.DB.Table**: `azcrp.crp_allprod.ApiQosEvent_nonGet`
**Pivot columns**: `resultCode`, `errorDetails`, `operationName`

| Signal | Meaning | Next step |
|---|---|---|
| (rowCount == 0) | The op never reached azcrp (ARM-side throttle / RBAC) | Pivot to `armprodgbl.eastus.ARMProd.HttpIncomingRequests` filtered by `correlationRequestId` |
| `resultCode == "OK"` | Sub-op succeeded | Trace `ContextActivity` for next sub-step |
| `errorDetails` contains `IsPreempted=true` | CRP preempted the op (service restart or higher-priority op took over) | Playbook G § DEPLOY-CRP-Preempted |
| `errorDetails` contains `TaskCanceledException` | CRP service restart mid-op | Playbook G § DEPLOY-CRP-Restarted |
| `errorDetails` contains `provided for the VM size is not valid` + zero-width chars | U+200B in vmSize | Playbook G § DEPLOY-Alloc-InvalidVMSize |
| `errorDetails` contains `OverconstrainedZonal` | Zone placement fail | Playbook G § DEPLOY-Alloc-AnyZone |
| Long `ContextActivity` chain across multiple `operationId` | Long-running CRP op | Join all operationIds via `ContextActivity` |

---

## 11. DiskManagerApiQoSEvent — Managed disk control plane

**Source**: [`catalogs/disks-queries.md`](../catalogs/disks-queries.md), used by Playbook F.
**Cluster.DB.Table**: `disks.kusto.windows.net.Disks.DiskManagerApiQoSEvent`
**Pivot columns**: `operationName`, `resultCode`, `errorMessage`

| Signal | Meaning | Next step |
|---|---|---|
| (rowCount == 0) | Op never reached Disks RP — pivot to ARM HttpIncoming | Playbook F entry recheck |
| `resultCode == "Success"` for delete | Disk deleted as expected | Done |
| `errorMessage` contains `disk is attached` | Disk still attached, customer must detach first | Cross-link Playbook B § OP-Delete |
| `errorMessage` contains `acquired by another` (lease) | Lease held by VM | Run `StorageBlob` join (§ SA-Util-IdentifyBlobsActiveLease) |
| `errorMessage` contains `LiveResizeStorageClientFailure` | XStore-side resize failure | Playbook F § MD-Resize-LiveResize (Pattern A or B branching by error subtype) |
| `errorMessage` contains `SnapshotLimitReached` | 100 snapshots per source-disk hit | Playbook F § MD-Snapshot-LimitReached |
| `errorMessage` contains `EncryptionKeyNotFound` | DES/KV key gone | Playbook H § SSE-KeyDisabled / § SSE-KVKeyNotFound |

---

## 12. WireserverHeartbeatEtwTable — IMDS reachability from host

**Cluster.DB.Table**: `azcore.centralus.Fa.WireserverHeartbeatEtwTable`
**Pivot columns**: `Status`, `ContainerId`

| Signal | Meaning | Next step |
|---|---|---|
| (rowCount == 0 for the container) | Host never saw IMDS heartbeat — host or hypervisor side | Playbook I § IMDS-Reach-CannotReach RC: Routing |
| `Status == "Ok"` consistently | Host-side IMDS healthy — issue is in-guest | Playbook I § IMDS-Reach-CannotReach RC: Proxy / FW |
| `Status != "Ok"` intermittent | Host Wireserver flaky | Cross-link to `AzureHost-VmService` collab |
| Long gap then resume | Container was paused or LM'd | Pivot to LM session table |

---

## 13. XArgus AccountPerfPercentiles5M — Storage account latency

**Source**: [`catalogs/storage-account-queries.md`](../catalogs/storage-account-queries.md), used by Playbook K.
**Cluster.DB.Table**: `xargus.centralus.kusto.windows.net.Production.AccountPerfPercentiles5M`
**Pivot columns**: `External_AvgLatencyMs`, `Server_AvgLatencyMs`, `FE_AvgLatencyMs`, `TableServer_AvgLatencyMs`, `Stream_AvgLatencyMs`, `Auth_AvgLatencyMs`

| Signal | Meaning | Next step |
|---|---|---|
| (rowCount == 0) | Account not in XArgus (recent account / wrong tenant) | Check `XStoreAccountProperties` for region + creation time; retry with correct stamp |
| `External - Server > 10ms` | Cross-zone or client-side network | Playbook K § SA-Perf-AzureFiles-Backend (Zonal Placement preview check) |
| `Server` high, `FE` low | TableServer or Stream layer issue | Drill into `FE_*` and `TableServer_*` |
| `TableServer_*` high | Hot partition | Playbook K § SA-Perf-PartitionDowntime (Jarvis `Xstore.PartitionDowntimeEvent`) |
| `Stream_*` high | Storage tier slow | Escalate to XStore team (collab) |
| `Auth_*` high | Identity layer (rare) | Cross-link MSI / KV CMK path |
| All layers high consistently | Stamp-level issue | Playbook K § SA-Perf-TenantHealth |

---

## 14. ImdsApiRequests() function — IMDS host-side errors

**Cluster.DB**: `azcore.centralus.SharedWorkspace`
**Pivot columns**: `httpStatusCode`, `endpoint`

| Signal | Meaning | Next step |
|---|---|---|
| (rowCount == 0) | No IMDS traffic from this VM container | Verify ContainerId; check WireserverHeartbeatEtwTable (#12) |
| `httpStatusCode == 200` dominant | IMDS healthy host-side | Issue is in-guest — Playbook I § IMDS-GuestProxyAgent or guest firewall |
| `httpStatusCode == 400` cluster | Missing Metadata header / bad request | Playbook I § IMDS-Token-4xx |
| `httpStatusCode == 410` | Stale goal state | Playbook I § IMDS-Token-4xx (retry then redeploy) |
| `httpStatusCode == 429` | Hit 5 QPS | Customer must throttle (no platform fix) |
| `httpStatusCode == 500` cluster | Host dependency (CRP/NRP/AAD) failing | Playbook I § IMDS-Token-5xx (ICM by endpoint) |

---

## 15. ApiQosEvent / ARMProd HttpIncomingRequests — ARM-side entry

**Cluster.DB.Table**: `armprodgbl.eastus.ARMProd.HttpIncomingRequests` (multi-region macro-expand for completeness)
**Pivot columns**: `httpStatusCode`, `failureCause`, `targetResourceProvider`

| Signal | Meaning | Next step |
|---|---|---|
| (rowCount == 0 with correct `correlationRequestId`) | Customer's request never reached ARM — likely client / SDK / Az CLI issue | Ask customer to share full az CLI/SDK log |
| `httpStatusCode == 200` and downstream `CrpOperationQoSEtwTable` empty | ARM accepted, but op never reached CRP — pivot to `EventServiceEntries` for Policy/lock | Playbook B § OP-Policy / § OP-Lock |
| `httpStatusCode == 401` / `403` | RBAC | Playbook B § OP-RBAC |
| `httpStatusCode == 429` + `failureCause == "subscription throttling"` | ARM subscription throttle | Playbook G § DEPLOY-CRP-SubThrottle |
| `httpStatusCode == 503` + `failureCause == "gateway"` | Resource Based Throttling | Playbook G § DEPLOY-CRP-RBT |
| `httpStatusCode == 500` from RP | RP internal error | Pivot to `ApiQosEvent_nonGet` (#10) |

---

## Rules for new pivot entries

When you discover a query whose result legitimately determines the next anchor, add it here:

1. **Cluster.DB.Table** — full qualifier
2. **Pivot columns** — the 1–3 columns whose values drive branching
3. **rowCount == 0 rule** — what does "no rows" mean (almost always different from "fault")
4. **Per-value rules** — match exact strings or regex patterns to next anchor
5. **Cross-link** — back to the catalog/playbook the query lives in

Keep each entry under 25 lines. If you need more, that's not a pivot — it's a playbook section.
