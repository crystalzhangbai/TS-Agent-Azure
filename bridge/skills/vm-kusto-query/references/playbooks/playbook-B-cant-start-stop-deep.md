# Playbook B — Cant Start-Stop / Allocation (deep TSG sections)

> Companion to [playbook-B-cant-start-stop-core.md](./playbook-B-cant-start-stop-core.md). The core file routes; this file holds the per-error-code and per-operation-kind drill-downs with KQL, interpretation, and customer-facing language hints. Sections are tagged so the core file can link straight in (e.g., `§ OP-Allocation`).
>
> When an error code is listed in `crp-queries.md` § `CRP Error-Code Routing Reference`, this file expands what to query, what to look for, and what to say. For tables not repeated here, follow the cross-reference back to the dedicated reference file.

---

## § OP-Allocation — `AllocationFailed` / `ZonalAllocationFailed` / `OverconstrainedAllocationRequest` / `NoSubscriptionMatchedQuota`

**Symptom**: Create / Start (from Deallocated) / Resize-up / Redeploy fails with one of the allocation error codes.

### Pull allocation details

```kusto
// cluster('Cirrus').database('Cirrus').CRPAllocationDetailsEtwTable
CRPAllocationDetailsEtwTable
| where TIMESTAMP between (datetime(<Start>) .. datetime(<End>))
| where SubscriptionId =~ "<SubscriptionId>"
| where vmName has "<VMName>" or correlationId == "<CorrelationId>"
| project TIMESTAMP, vmName, vmSize, region, AvailabilityZone, allocationResult,
          failureReason, candidateCluster, candidatesEvaluated, allocationTimeMs
| order by TIMESTAMP asc
```

→ Full body in `crp-queries.md` § `Allocation & Placement`.

### Interpretation

| `failureReason` substring | Meaning | Customer message |
|---|---|---|
| `NoSubscriptionMatchedQuota` | Subscription quota exhausted | Customer-action: file a quota increase. Not a platform issue. |
| `OverconstrainedAllocationRequest` | PPG / AvSet / colocation policies can't be satisfied (no single cluster has capacity for all members) | Suggest: split PPG, relax zone pin, or use a smaller SKU family. |
| `ZonalAllocationFailed` | Specific zone has no capacity for SKU | Try a different zone in same region, or remove zonal pin. |
| `VMDiskColocationPolicy*` / `T2SpineSelectionFault` | Premium disk + VM must land on same T2 spine — no capacity | See [Allocation-Failure-VMDiskColocationPolicy-T2SpineSelectionFault TSG](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495440) |
| Generic `AllocationFailed` (no specific reason) | Region/SKU capacity general | Suggest customer try a different region or smaller SKU; engage Capacity team if business-critical. |

### Cross-checks
- **Capacity recommender**: build the ASI Cluster utilization link from [`../dashboards/`](../dashboards/) and open Compute Capacity Advisory manually (wiki [Compute-Capacity-Advisory](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/500082)).
- **For PPG / AvSet failures** specifically — confirm member count and zone pinning in customer's deployment.
- **For disk colocation** failures (Premium Managed Disk + VM) — use `VMApiQosEvent` colocation verification in `crp-queries.md` § `CRP via azcrp Cluster`.

### Customer-facing wording template
> "Our allocation system was unable to place your VM `<VMName>` in `<region>`/`<zone>` because the requested combination of size `<vmSize>` and `<constraint>` is currently capacity-constrained. We recommend `<action>`."

---

## § OP-FabricTimeout — `OutOfTimeBudgetException` / `FabricInternalOperationError`

**Symptom**: CRP returned `OutOfTimeBudgetException` or `FabricInternalOperationError` — CRP could not get a timely response from the underlying fabric layer (AzSM / Job) for a Start/Stop/Update.

### Pull the CRP→Fabric handoff

```kusto
// cluster('Azcsupfollower').database('AzureCM').NodeServiceOperationEtwTable
NodeServiceOperationEtwTable
| where PreciseTimeStamp between (datetime(<Start>) .. datetime(<End>))
| where ContainerId has "<VMName>" or TenantName has "<VMName>"
| project PreciseTimeStamp, nodeId, OperationName, ResultType, DurationMs,
          ErrorMessage
| order by PreciseTimeStamp asc
```

```kusto
// cluster('Azcsupfollower').database('AzureCM').TMMgmtJobEventsEtwTable
TMMgmtJobEventsEtwTable
| where PreciseTimeStamp between (datetime(<Start>) .. datetime(<End>))
| where JobName has "<VMName>" or TenantName has "<VMName>"
| project PreciseTimeStamp, JobName, JobState, JobOperation, Message
| order by PreciseTimeStamp asc
```

### Interpretation

- `NodeServiceOperationEtwTable.DurationMs > 90000` for `StartContainer`/`StopContainer` → host-side hang. Pivot to `azcore-queries.md` (HyperV / RDOS) for that `nodeId`.
- `JobState` stuck in `Executing` past CRP timeout → fabric workflow hung. Engage AzSM SME via [AzSM-Azure-Fabric How-To](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/500342).
- Multiple `Faulted` job rows for same VM → check if the node went `Unhealthy` (Playbook A § Service Healing) or if there was an in-flight host update (`operations-queries.md` § Azure Policy Engine).

### Drill into the AzLifecycle (AZSM) slice

When `JobState` is stuck or `Faulted` but `TMMgmtJobEventsEtwTable` doesn't say why, the root cause is usually inside the AzLifecycle service. The AzLifecycle slice logs are on a **different cluster** (`accp.centralus / AZSM`) — see [`azurecm-queries.md`](../catalogs/azurecm-queries.md) § AzLifecycle / AZSM:

1. `AzSMTenantSnapshotV2` (on `azcsupfollower.AzureCM`) → get `applicationName` to identify which `AzLifecycle-Slice<N>-P<n>` owns the tenant.
2. `AzSMUpdateTenantEvents` on `accp.centralus.AZSM` → did the UpdateTenant call from CRP land, and what happened next.
3. `AzSMTenantStatemachineEvents` → where the state machine got stuck (filter `message contains "UpdateTenant"`).
4. `AzSMExceptionsEvents` → exception stack thrown inside the slice — usually the smoking gun.

If an AzLifecycle exception identifies a downstream fabric/hardware fault, hand off per Playbook A.

### TSG anchor
[OutofTimeBudgetException wiki](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495454)

---

## § OP-StartTimeout — `VMStartTimedOut`

**Symptom**: Start / Restart / Redeploy returned `VMStartTimedOut`.

```kusto
// cluster('Azcsupfollower').database('AzureCM').LogNodeSnapshot
LogNodeSnapshot
| where PreciseTimeStamp between (datetime(<Start>) .. datetime(<End>))
| where nodeId == "<NodeId>"
| project PreciseTimeStamp, nodeId, nodeState, healthState,
          unhealthyReason, AllDisksAbc, AllDisksInStripe
| order by PreciseTimeStamp asc
```

→ See `azurecm-queries.md` § `LogNodeSnapshot ABC detection` for `AllDisksAbc` interpretation.

### Routing
- `nodeState != Ready` during the start window → host issue. Cross with `TMMgmtNodeEventsEtwTable` for DirtyShutdown / BugCheck.
- `nodeState == Ready` but VM didn't come up → boot device / disk attach issue. Pivot to `disks-queries.md` § `DiskManagerApiQoSEvent` + `azcore-queries.md` § HyperV.
- `unhealthyReason` populated → that's the kernel-level fault — route per `_shared-vm-identification.md` Q3.

### TSG anchor
[VM-Did-Not-Start-in-the-Allotted-Time wiki](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495485)

---

## § OP-OSPTO — `OSProvisioningTimedOut`

**Symptom**: Create returned `OSProvisioningTimedOut` (most common on Create; can also appear on rebuild). CRP successfully started the VM but the in-guest provisioning agent never reported Ready.

### Pivot from CRP to guest

1. **Confirm CRP completed bring-up**: Step 2 in core shows `Success` for `BeginCreateOrUpdate` but Final operation returns `OSProvisioningTimedOut`.
2. **Confirm the GuestOsStateProvisioning(Recovery) sequence**: pull `TMMgmtSlaMeasurementEventEtwTable` filtered by `ContainerID` and project `EntityState` — see the EntityState dictionary in [`azurecm-queries.md`](../catalogs/azurecm-queries.md) § Disk-Configuration Switch / EntityState dictionary. Sequence `GuestOsStateProvisioning` → `GuestOsStateProvisioningRecovery` → `Reboot` proves the guest never reported Ready.
3. **Check the KVP channel**: did the in-guest agent ever talk back? Run `IfxOperationV2v1EtwTable` `GuestOsKVPItems` → `KVPData` per [`azcore-queries.md`](../catalogs/azcore-queries.md) § Guest KVP Data. No KVP rows = agent never started or wireserver blocked.
4. **Boot diagnostics screenshot**: ask customer to enable boot diagnostics (or grab from ASC) to see GRUB / Windows boot screen state.
5. **Guest log analysis**: hand off to `vm-log-analyzer` skill:
   - Linux: `/var/log/waagent.log`, `/var/log/cloud-init.log`, `/var/log/syslog` (look for `Provisioning failed`, `WALinuxAgent` errors, network not up).
   - Windows: `C:\WindowsAzure\Logs\WaAppAgent.log`, `setupact.log`, unattend.xml processing.
6. **Known patterns**:
   - Custom image without `waagent -deprovision` → IP/hostname conflict.
   - Cloud-init user-data script blocking (e.g., apt update behind firewall) → agent never gets to Ready.
   - Linux NIC not coming up due to bad netplan/cloud-config from image.

### TSG anchors
- [OSProvisioningTimedOut (OSPTO) wiki](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495667)
- [Provisioning Workflow wiki](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495735)
- [GuestOsStateProvisioningRecovery wiki](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495487)

### Customer-facing wording template
> "The platform successfully started VM `<VMName>` at `<TIMESTAMP>`, but the Windows/Linux provisioning agent inside the guest did not complete bootstrap within the allotted `30 / 60` minutes. This is typically caused by `<image / cloud-init / agent>` — please collect `<log paths>` and confirm `<known pattern>`."

---

## § OP-NetworkInternalError — `NetworkingInternalOperationError`

**Symptom**: Start / Restart / Create failed because NRP couldn't attach or detach the NIC.

```kusto
// cluster('hybridnetworking').database('Logs').NrpResourceLifecycleEvents
// — preferred path: networking-queries.md § NRP
```

### Steps
1. Pull the NRP NIC operation matching `<CorrelationId>` — see `networking-queries.md` § Hybridnetworking / NRP.
2. Identify whether the NIC is shared / orphaned / has a stale association.
3. If NIC is in a failed state → may need NRP SME collab ([NetworkingInternalOperationError wiki](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495442)).
4. For "Unregistration-Of-Implicit-Nic-Via-Arm-Failed" pattern (Delete only) — see that specific TSG: [Unregistration-Of-Implicit-Nic-Via-Arm-Failed](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495457).

---

## § OP-DiskMgmt — `InternalDiskManagementError` (commonly on Delete)

**Symptom**: Delete VM returned `InternalDiskManagementError`. The VM container is gone but a managed disk is stuck.

```kusto
// cluster('Disks').database('Disks').DiskManagerApiQoSEvent
DiskManagerApiQoSEvent
| where PreciseTimeStamp between (datetime(<Start>) .. datetime(<End>))
| where SubscriptionId =~ "<SubscriptionId>"
| where ResourceName has "<VMName>" or ResourceName has "<DiskName>"
| project PreciseTimeStamp, OperationName, ResultType, ErrorCode,
          ErrorMessage, DurationMs
| order by PreciseTimeStamp asc
```

→ See `disks-queries.md` § `DiskManagerApiQoSEvent — Backend Existence Check`.

### Interpretation
- If Disk RP reports the underlying blob is gone but the disk resource still exists → ask customer to retry delete; if still failing, raise collab to **Disk RP team**.
- If lease still held → see § OP-DiskLease below.

### TSG anchor
[Failed-to-Delete-VM-InternalDiskManagementError wiki](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/518459).

---

## § OP-DiskLease — `AcquireDiskLeaseFailed`

**Symptom**: Start of an **unmanaged** (page-blob backed) VM fails because the previous container's lease is still held.

### Steps
1. Identify the page-blob URL from the VM's `storageProfile.osDisk.vhd.uri`.
2. Check the lease state via XStore — escalate to **XStore SME** with the blob URL and timestamp to break the lease.
3. Long-term remediation: convert to managed disks.

### TSG anchor
[Currently-a-Lease-on-the-Blob-and-No-Lease-ID wiki](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495439).

---

## § OP-Throttle — ARM `429 TooManyRequests`

**Symptom**: ARM returned 429 for `<operationName>` on `<resourceUri>`.

### Steps
1. From Step 1 ARM ingress query, pull `userAgent`, `callerIdentities`, `clientIpAddress`.
2. If `userAgent` is a non-interactive tool (Terraform / Ansible / custom script) — customer is hitting their own subscription's request rate. Recommend exponential back-off and pagination.
3. If multiple SPNs are hitting from same tenant — review tenant-level coordination.
4. ARM throttling limits are documented in MS Learn — link customer to those.

---

## § OP-Lock — `409 ScopeLocked`

**Symptom**: ARM rejected because the VM / RG / subscription has a CanNotDelete or ReadOnly lock.

### Steps
1. From ARM error, identify which scope has the lock (resource / RG / subscription).
2. Customer action: locate the lock in Portal → Settings → Locks → remove.

### TSG anchor
[Scope-Locked wiki](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495460).

---

## § OP-Policy — `403 RequestDisallowedByPolicy`

**Symptom**: Azure Policy assignment blocked the request.

### Steps
1. From ARM error, copy the `policyDefinitionDisplayName` and `policyAssignmentId`.
2. Send to customer with: "Your subscription/RG has policy `<name>` (assignment `<id>`) that disallows this request. Please review and amend the policy or exempt the resource if intended."
3. Customer-action only — platform side has no path to bypass a policy.

---

## § OP-RBAC — `403 AuthorizationFailed`

**Symptom**: ARM rejected because the caller lacks the role assignment.

### Steps
1. From ARM error, identify required action (e.g., `Microsoft.Compute/virtualMachines/start/action`).
2. Customer assigns Virtual Machine Contributor (or a custom role with the action) to the caller.

---

## § OP-BadRequest — `400 BadRequest` / `OperationNotAllowed`

**Symptom**: CRP rejected the request shape or current resource state.

### Common causes
- Resize across incompatible SKU families (e.g., requires VM stopped first).
- Start on a VM that is already Running (or has hibernation in progress).
- Resource currently in a transitional state (Deleting / Updating).
- Required field missing or invalid (often Terraform / SDK older versions).

### Steps
1. Read `ErrorMessage` verbatim — usually self-explanatory.
2. Ask customer for the request body (Portal → JSON View or Terraform plan).
3. Common fixes documented across `Cant-Start-Stop/TSGs/` — search for the specific message in csswiki.

---

## § OP-Retry — `RetryableError` that eventually failed

**Symptom**: CRP retried the operation but exhausted its retry budget.

### Steps
1. Use Step 3 (`ContextActivity`) to trace each retry attempt.
2. Identify the underlying error on the last retry — route via § OP-FabricTimeout / § OP-NetworkInternalError / etc.
3. If retries all failed with same downstream error → that downstream component is the real issue; ignore the CRP `RetryableError` wrapper.

---

## § OP-Delete — Delete-specific failures

**Pattern A — `InternalDiskManagementError`**: see § OP-DiskMgmt above.

**Pattern B — Force-delete required**: customer tried `az vm delete` but VM is stuck. See [Failed-to-Force-Delete-VM wiki](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495447).

**Pattern C — VM auto-deleted by Azure Compute**: customer says "we didn't delete it". See [Customer-VM-Got-Deleted-by-Azure-Compute wiki](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495445) — usually evicted Spot / non-production cleanup. Confirm via:

```kusto
// cluster('Cirrus').database('Cirrus').CrpOperationQoSEtwTable
CrpOperationQoSEtwTable
| where TIMESTAMP between (datetime(<Start>) .. datetime(<End>))
| where ResourceId has "<VMName>"
| where OperationName has "Delete"
| project TIMESTAMP, OperationName, callerIdentity, ResultType, ErrorMessage
```

→ Look at `callerIdentity` — `EvictionService` / `MadariScheduler` / `Compute Resource Provider` means platform-initiated.

**Pattern D — NIC unregistration failed during delete**: see [Unregistration-Of-Implicit-Nic-Via-Arm-Failed](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495457).

**Pattern E — `VM-Marked-for-Deletion`** (Madari restore-point cleanup): see [VM-Marked-for-Deletion wiki](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495454).

---

## § OP-Resize — Resize-specific failures

**Pattern A — SKU not available in current region / cluster**: Resize requires landing on a host that supports the target SKU.
- Stop-then-resize (Deallocate first) usually unblocks because allocator can re-pick a cluster.
- See [Unable-to-Resize-VM_Size-Not-Available-in-the-Portal](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495466).

**Pattern B — Cross-family resize blocked**: e.g., D-series → M-series often requires Deallocate.

**Pattern C — `Start-or-Resize-Operation-Fail-Due-to-Node-Low-Memory`** (in-place resize-up failed because current node is full):
- See [Start-or-Resize-Operation-Fail-Due-to-Node-Low-Memory wiki](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495463).
- Remediation: deallocate + resize so allocator picks a new node.

**Pattern D — Discrepancy on VM size**: CRP shows one size, customer Portal shows another. See [Discrepancy-on-VM-size wiki](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495446).

---

## § OP-Redeploy — Redeploy-specific failures

**Pattern A — Customer-initiated redeploy fails with allocation error** → § OP-Allocation (redeploy is essentially a re-allocation to a different host).

**Pattern B — Platform-initiated redeploy** (scheduled-event / Madari) → see [VMRedeploymentFailed-ScheduledEvent](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/1084289) + cross with `operations-queries.md` § Maintenance & Customer Notifications.

**Pattern C — VFPRestoreFailure during LM** (live-migration leg of redeploy): see [Live-Migration-Failure-due-to-VFPRestoreFailure](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/1084290) — cross with Playbook A § LM.

**Pattern D — Redeploy / Restart delayed by ~15 minutes** — usually Scheduled Events are enabled and the platform is waiting on the in-guest agent to ack the event. Confirm with `GetScheduledEventsEnablementStatusV3()` per [`operations-queries.md`](../catalogs/operations-queries.md) § AzPE. If `ScheduledEventsStatus == True`, explain to customer and point to the IMDS `/metadata/scheduledevents` POST `StartRequests` workflow to pre-approve.

---

## § OP-Hibernate — Hibernation-specific failures

- [Subsequent-hibernation-attempt-fails wiki](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495449) — typical recovery: customer must start VM, then re-try hibernate (state file invalidated).
- Pre-req: VM must be created with hibernation enabled; PG-only for certain SKU families.

---

## § OP-FabricInternalPowerOff — `FabricCallback / InternalPowerOffVMOperation / DetachedAsync-Post`

**Symptom**: VM was unexpectedly power-cycled by the host (no customer action), and CRP recorded a `FabricCallback / InternalPowerOffVMOperation / DetachedAsync-Post` callback. Common root cause: host-side memory operation failed (e.g., RAM block creation took too long, or HyperV worker hit a memory fault), so the host killed the VM to recover.

**Prereq**: ContainerId, NodeId, time window (from § OP-StartTimeout pivot, or directly from `LogContainerHealthSnapshot` `containerLifecycleState == Stopped` with no customer op).

### 1. Host-side Hyper-V Worker memory failure

Three EventIds in `WindowsEventTable` mark Hyper-V Worker memory ops that failed and trigger the host to power-off the affected VM. See [`azcore-queries.md`](../catalogs/azcore-queries.md) § WindowsEventTable — Hyper-V Worker memory operation failures (filter `EventId in ("12030", "3122", "3050")`).

### 2. Confirm the VM that suffered the memory delay

`HyperVWorkerTable` filter `TaskName == "TimeSpentInMemoryOperation"` and `Message has "ReservingRam" and "CreateRamMemoryBlocks"` and the `Seconds > 120` parse — see [`azcore-queries.md`](../catalogs/azcore-queries.md) § HyperVWorkerTable — Memory allocation delays (>120s). The `Message` payload contains the HyperV VmId — map to ContainerId via `GetHyperVVmIdFromContainerId()` (same file, § GetHyperVVmIdFromContainerId).

### 3. NRP-side detach trace (if NIC was already torn down by the time the customer saw the error)

The internal power-off may have also detached the NIC. Pull `FrontendOperationEtwEvent` filtered by `ClientOperationId == "{OperationId}"` (NOT CorrelationRequestId — the CRP op id is what flows down) — see [`networking-queries.md`](../catalogs/networking-queries.md) § NRP / Pivot from CRP via ClientOperationId.

### 4. Cross-container Geneva timeline (high-volume context)

When you need everything the platform did to a specific VM across multiple Redeploy/LM legs in one chronological view, use `acccvmtmgeneva.Log` keyed by `tagId in (ContainerIds)` — see [`azcore-queries.md`](../catalogs/azcore-queries.md) § acccvmtmgeneva.Log. The `MycroftContainerSnapshot` summary at the top of that section turns the `VirtualMachineUniqueId` into the full ContainerId set first.

### 5. Host firmware sanity

A stale `vmfirmwarehcl.dll` on the host is a known precursor to this class of failure — confirm with `OsFileVersionTable` filter `FileName == "vmfirmwarehcl.dll"` and `summarize arg_max(PreciseTimeStamp, *) by NodeId` (already in [`azcore-queries.md`](../catalogs/azcore-queries.md) § OsFileVersionTable). If the version on the host is below the SafeFly target, that's the root cause; engage HW team per Playbook A § HardwareFault.

### TSG anchor
[FabricCallback-InternalPowerOffVMOperation-DetachedAsync-Post wiki](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/1084288)

---

## § OP-Unknown — Error code not in the table

1. Search csswiki AzureIaaSVM for the exact error string (`mcp_csswiki_search_wiki`).
2. Search `internalkb` for known internal bug reports.
3. If still no match → file feedback via [Start-Stop Feedback form](https://supportability.visualstudio.com/AzureIaaSVM/_workitems/create/Feedback?templateId=e6c4efc9-5cf1-4d38-a5c7-f6d91d777ff2&ownerId=47822c91-ba84-4c8b-a535-c1b1b5d4e500) and engage SME via AVA channel.

---

## Quick links — operation-kind index

| Operation | Primary deep section |
|---|---|
| **Create** | § OP-Allocation, § OP-OSPTO, § OP-NetworkInternalError, § OP-Policy, § OP-BadRequest |
| **Start** (Deallocated → Running) | § OP-Allocation, § OP-StartTimeout, § OP-FabricTimeout, § OP-DiskLease |
| **Stop** / **Deallocate** | § OP-FabricTimeout, § OP-BadRequest (e.g., already stopped) |
| **Restart** | § OP-StartTimeout, § OP-FabricTimeout |
| **Redeploy** | § OP-Redeploy → § OP-Allocation |
| **Delete** | § OP-Delete → § OP-DiskMgmt / § OP-NetworkInternalError |
| **Resize** | § OP-Resize → § OP-Allocation (resize-up) |
| **Hibernate / Resume** | § OP-Hibernate → § OP-StartTimeout |
| **Update** (extension / SKU metadata only) | § OP-FabricTimeout, § OP-BadRequest |

---

## Cross-references back to other playbooks / refs

- [crp-queries.md](../catalogs/crp-queries.md) — all CRP & ARM tables, plus the master Error-Code Routing Reference table.
- [azurecm-queries.md](../catalogs/azurecm-queries.md) — LogContainerHealthSnapshot, LogNodeSnapshot, NodeServiceOperationEtwTable, TMMgmtJobEventsEtwTable.
- [disks-queries.md](../catalogs/disks-queries.md) — DiskRPResourceLifecycleEvent, DiskManagerApiQoSEvent.
- [networking-queries.md](../catalogs/networking-queries.md) — Hybridnetworking, NRP.
- [_shared-vm-identification.md](../_meta/_shared-vm-identification.md) — Q2 (faultInfo), Q3 (nodeState), Q7 (KronoxVmOperationEvent — customer vs platform).
- [playbook-A-restarts-core.md](playbook-A-restarts-core.md) / [playbook-A-restarts-deep.md](playbook-A-restarts-deep.md) — when a "Start failure" actually reveals an underlying restart / Service Healing.
- [playbook-C-performance-core.md](./playbook-C-performance-core.md) — for "Op succeeded but VM is slow afterward".
