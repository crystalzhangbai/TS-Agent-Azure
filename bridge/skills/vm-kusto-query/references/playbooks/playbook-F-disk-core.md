# Playbook F — Disk Lifecycle (Core)

> **Companion to** [`playbook-F-disk-deep.md`](./playbook-F-disk-deep.md). Use this file as the **routing entry point** when a case is about a managed-disk create/attach/detach/resize/snapshot/convert/delete/encryption/billing scenario. Full KQL bodies + customer-facing RCAs live in the deep file under `MD-*` anchors. Foundation queries (`DiskRPResourceLifecycleEvent`, `DiskManagerApiQoSEvent`, `DiskManagerContextActivityEvent`, etc.) live in `references/disks-queries.md`.

## When to use this playbook

| Use Playbook F when... | Don't — use instead |
|---|---|
| Customer reports `OperationNotAllowed` / `LeaseIdMissing` / `LiveResizeStorageClientFailure` / `SnapshotLimitReached` / `Parameter 'encryptionSettings' is not allowed` / `OverconstrainedZonalAllocationRequest` / `TlsVersionNotPermitted` / `502 Bad Gateway` on Compute APIs | Disk caused a VM restart with platform telemetry → Playbook A § STG-1..4 (DiskHardwareFailure / DiskIOBlip / VirtualDiskFault) |
| Disk creation, attach, detach, resize, snapshot, convert, delete, encryption, billing, or visibility scenario | Disk performance / throttling / latency without lifecycle failure → Playbook C § STG-Perf-* |
| Recovering a deleted disk (soft-delete restore) | Generic CRP disk operation errors (CRP-side only) → Playbook B § OP-DiskMgmt / OP-DiskLease |
| `stornvme` Event 129 + IO timeout pattern | Deep ASAP NVMe RCA (controller resets, BQE/NQE, full vs partial offload) → `asap-storage-queries.md` |
| Standard HDD/SSD billable-transaction dispute | Storage account-level capacity/throttling/billing on non-disk SKUs → `storage-account-queries.md` |
| VMSS disk management (host caching, sharedDisks, swap OS for VMSS instance) | (Already covered in Playbook E — VMSS) |

## Inputs to collect

| # | Item | Why |
|---|---|---|
| 1 | `SubscriptionId` | Primary filter for every Kusto query |
| 2 | `ResourceGroupName` | Secondary filter |
| 3 | `DiskName` | Primary identifier (managed disks are RP resources) |
| 4 | `VMName` (if attached) | For attach/detach + ADE/UDE history |
| 5 | `CorrelationId` / `OperationId` | Cross-RP correlation (ARM → CRP → DiskRP). Customer usually has this in CLI output |
| 6 | `StartTime` / `EndTime` (UTC) | Pad ±15min around the customer-reported timestamp |
| 7 | `DiskType` (SKU) | `Standard_LRS` / `StandardSSD_LRS` / `Premium_LRS` / `Premium_ZRS` / `PremiumV2_LRS` / `UltraSSD_LRS` / `Standard_ZRS` — gates many recovery + billing decisions |
| 8 | `DiskSizeGB` | For tier verification + resize delta |
| 9 | Error code + error message (verbatim) | Routes to specific MD-* anchor (see Step 2) |

## Step-by-step

### Step 1 — Identify the disk + verify current state

Delegate to `references/disks-queries.md`:
- Find disk by name → `DiskRPResourceLifecycleEvent` filtered by `subscriptionId` + `resourceName`
- Latest state per disk (with `arg_max(PreciseTimeStamp, *)`)
- Backend existence check → `DiskManagerApiQoSEvent` (`httpStatusCode 200/404` distinguishes exists vs deleted)
- If disk has been deleted → § [MD-Delete-2](./playbook-F-disk-deep.md#md-delete-2--managed-disk-recovery-soft-delete) for recovery verification

### Step 2 — Classify the symptom → route to MD-* anchor

| Customer symptom / error code | Anchor |
|---|---|
| Disk delete returns `OperationNotAllowed` / "DiskIsAttached" / managedBy stale | § [MD-Delete-1](./playbook-F-disk-deep.md#md-delete-1--unable-to-delete-managed-disk-4-cause-router) |
| Customer wants to recover a deleted disk | § [MD-Delete-2](./playbook-F-disk-deep.md#md-delete-2--managed-disk-recovery-soft-delete) |
| Databricks cluster disks stuck `ToBeDeleted` / `LeaseIdMissing` | § [MD-Delete-3](./playbook-F-disk-deep.md#md-delete-3--unable-to-delete-disk-leased) |
| Unmanaged VM delete `TlsVersionNotPermitted` | § [MD-Delete-4](./playbook-F-disk-deep.md#md-delete-4--deleting-unmanaged-vm-tlsversionnotpermitted) |
| PV2 cumulative snapshot taking too long | § [MD-Snapshot-1](./playbook-F-disk-deep.md#md-snapshot-1--pv2-cumulative-snapshot-timing) |
| Instant Access Snapshot / `InvalidInstantAccessRequest` / `AzdError_InstantAccessNotEnabled` | § [MD-Snapshot-2](./playbook-F-disk-deep.md#md-snapshot-2--instant-access-snapshot) |
| `SnapshotLimitReached` | § [MD-Snapshot-3](./playbook-F-disk-deep.md#md-snapshot-3--unable-to-create-new-snapshot-snapshotlimitreached) |
| Cross-region snapshot copy stalled at <100% | § [MD-Snapshot-4](./playbook-F-disk-deep.md#md-snapshot-4--cross-region-snapshot-copy-hung) |
| `ChangeDiskSizeWhileAttachedNotAllowed` | § [MD-Resize-1](./playbook-F-disk-deep.md#md-resize-1--changedisksizewhileattachednotallowed) |
| `LiveResizeStorageClientFailure` (Pattern A SRP Timeout vs Pattern B FooterValidationError) | § [MD-Resize-2](./playbook-F-disk-deep.md#md-resize-2--liveresizestorageclientfailure-pattern-a-srp-timeout-vs-pattern-b-footervalidationerror) |
| `LiveDiskPropertyChangeOfVMOfSizeNotSupported` / `OperationNotAllowedDataDisk` | § [MD-Resize-3](./playbook-F-disk-deep.md#md-resize-3--livediskpropertychangeofvmofsizenotsupported) |
| `InvalidResizeWithName` (shrinking) | § [MD-Resize-4](./playbook-F-disk-deep.md#md-resize-4--invalidresizewithname-shrinking-managed-disks) |
| `OperationNotAllowed` + "resource disk to non-resource disk" (diskless SKU resize / temp-disk family mismatch) | § [MD-Resize-5](./playbook-F-disk-deep.md#md-resize-5--unable-to-resize-diskless-vms-temp-disk-sku-mismatch) |
| 512N vs 512E sectors / mixed Stripe + ABC nodes (SQL AOAG) | § [MD-Convert-1](./playbook-F-disk-deep.md#md-convert-1--512n-vs-512e-stripe-vs-abc-node-placement) |
| Premium SSD v2 → Standard HDD conversion | § [MD-Convert-2](./playbook-F-disk-deep.md#md-convert-2--premium-ssd-v2--standard-hdd-snapshot-workaround) |
| OS↔Data disk content swap → no-boot | § [MD-Convert-3](./playbook-F-disk-deep.md#md-convert-3--osdata-disk-content-swap-conversion) |
| Revert managed-disk VM to unmanaged (legacy ask, discouraged) | § [MD-Convert-4](./playbook-F-disk-deep.md#md-convert-4--revert-managed-disk-vm-to-unmanaged-legacy) |
| `Parameter 'encryptionSettings' is not allowed` (PV2 attach to UDE-tagged VM) | § [MD-Encryption-1](./playbook-F-disk-deep.md#md-encryption-1--parameter-encryptionsettings-is-not-allowed-pv2--ude-conflict) |
| CMK disk recovery — find DES + KV + key URL for deleted disks | § [MD-Encryption-2](./playbook-F-disk-deep.md#md-encryption-2--find-des-for-cmk-disk-recovery) |
| SAS token expiration / 60-day max | § [MD-Encryption-3](./playbook-F-disk-deep.md#md-encryption-3--sas-token-expiration-60-day-max) |
| Disk not visible in portal "Attach existing" dropdown | § [MD-Visibility-1](./playbook-F-disk-deep.md#md-visibility-1--disk-not-visible-in-portal-zonal-mismatch) |
| Disk attached but not visible in Windows guest | § [MD-Visibility-2](./playbook-F-disk-deep.md#md-visibility-2--disk-not-visible-in-windows-guest) |
| Disk attached but missing in Linux guest (LUN 0 unused) | § [MD-Visibility-3](./playbook-F-disk-deep.md#md-visibility-3--disk-not-found-linux-lun-0-problem) |
| Disk resized in Azure but Windows still shows old size | § [MD-Visibility-4](./playbook-F-disk-deep.md#md-visibility-4--disk-size-not-updated-in-windows-after-resize) |
| Spanned volume shows Failed / foreign disks after partial copy | § [MD-Visibility-5](./playbook-F-disk-deep.md#md-visibility-5--spanned-disk-missing) |
| Generic Event 129 reset (storahci / vhdmp / stornvme) | § [MD-Event-1](./playbook-F-disk-deep.md#md-event-1--event-129-reset-to-device-generic-stornvme-storahci-vhdmp) |
| `stornvme` Event 129 + IO timeout (ASAP/NVMe known issue) | § [MD-Event-2](./playbook-F-disk-deep.md#md-event-2--stornvme-event-129-asap--io-timeout-known-issue) + cross-link `asap-storage-queries.md` |
| Windows Event 157 "disk surprise removed" (cluster + non-cluster mitigations) | § [MD-Event-3](./playbook-F-disk-deep.md#md-event-3--event-157-disk-surprise-remove) |
| VM allocation failure with `VMDiskColocationAllocator` in error details (East US2 EUAP / East Asia) | § [MD-Colocation-1](./playbook-F-disk-deep.md#md-colocation-1--software-latency-zone-slz-silent-feature-) ⚠ SILENT |
| `OverconstrainedZonalAllocationRequest` on VM with UltraSSD enabled | § [MD-UltraSSD-1](./playbook-F-disk-deep.md#md-ultrassd-1--overconstrainedzonalallocationrequest-ultrassd) |
| Standard HDD/SSD billable-transaction dispute | § [MD-Billing-1](./playbook-F-disk-deep.md#md-billing-1--standard-hddssd-billing-anomalies) |
| `Get-AzVM` returns 502 / "failed to return collection response for virtualMachines" | § [MD-Platform-1](./playbook-F-disk-deep.md#md-platform-1--502-gateway-error-on-virtualmachines-collection) |
| Shared disk: data on one side not visible on other | § [MD-Shared-1](./playbook-F-disk-deep.md#md-shared-1--shared-disk-not-propagating-cluster-fs-required) |
| Ambiguous — customer just says "can't attach/detach/create/resize" | § [MD-Workflow-Router](./playbook-F-disk-deep.md#md-workflow-router--attachdetach--create--delete--resize) |
| Ephemeral OS disk concept / size / reimage question | § [MD-Other-Ephemeral](./playbook-F-disk-deep.md#md-other-ephemeral--ephemeral-os-disk) |
| Bulk remove unattached data disks | § [MD-Other-Unattached](./playbook-F-disk-deep.md#md-other-unattached--remove-unattached-data-disks-from-subscription) |
| Direct upload (grant-access + AzCopy) issues | § [MD-Other-Upload](./playbook-F-disk-deep.md#md-other-upload--managed-disk-direct-upload) |
| Unmanaged disk retirement (2026-03-31 EOL) | § [MD-Other-Unmanaged-Retirement](./playbook-F-disk-deep.md#md-other-unmanaged-retirement--unmanaged-disk-retirement-2026-03-31) |
| Unmanaged OS disk swap via Storage Explorer + CLI | § [MD-Other-Unmanaged-OSSwap](./playbook-F-disk-deep.md#md-other-unmanaged-osswap--unmanaged-os-disk-swap-storage-explorer--cli) |

### Step 3 — Pull foundation evidence

Per `references/disks-queries.md`:
- `DiskManagerApiQoSEvent` filtered by `correlationId` (or `operationId`) → returns `operationName` + `resultCode` + `errorDetails` + `requestEntity` + `e2EDurationInMilliseconds`
- Take the `operationId` from above → `DiskManagerContextActivityEvent` filtered by `activityId == "{OperationId}"` → verbose trace messages (lease state, FooterValidationError, UDE flag, preemption switches)

### Step 4 — Apply MD-* anchor logic

The deep file's per-anchor section provides: scope, full KQL bodies, interpretation, mitigation, and (where applicable) verbatim customer RCA wording. Follow the routing decisions inside the anchor (e.g., Pattern A vs B for live resize).

### Step 5 — Cross-RP confirmation (if multi-RP)

| If customer-visible symptom involves... | Also pull |
|---|---|
| ARM correlation chain | `armprodgbl` `HttpIncomingRequests` filtered by `correlationId` (see § [MD-Platform-1](./playbook-F-disk-deep.md#md-platform-1--502-gateway-error-on-virtualmachines-collection) Q1 for the macro-expand pattern) |
| CRP VM allocation involving disks | `azcrp.crp_allprod.VMApiQosEvent` / `ApiQosEvent_nonGet` (see § [MD-UltraSSD-1](./playbook-F-disk-deep.md#md-ultrassd-1--overconstrainedzonalallocationrequest-ultrassd) Q1 / § [MD-Colocation-1](./playbook-F-disk-deep.md#md-colocation-1--software-latency-zone-slz-silent-feature-)) |
| ARM cache / managedBy staleness | Collab to **ARM team** — see [MD-Delete-1 cause 2](./playbook-F-disk-deep.md#md-delete-1--unable-to-delete-managed-disk-4-cause-router) |
| ASAP / NVMe controller resets | `asap-storage-queries.md` |
| Storage account capacity/transactions (non-disk perspective) | `storage-account-queries.md` |

### Step 6 — Specialized investigations

| Need | Tool |
|---|---|
| Disk Recovery Dashboard | https://portal.microsoftgeneva.com/s/31C27072 |
| Cross-region snapshot DGrep | https://portal.microsoftgeneva.com/s/62803206 |
| Recovery Template (Sev 4 IcM) | https://aka.ms/ManagedDiskRecoveryTemplate + email `cssdiskrec@microsoft.com` |
| Disk SME engagement (live cases) | Ava channel — Disk SME on-call |
| ICM templates | Use Disk Recovery Template above; for CRP-allocation/colocation use CRP collab template (Playbook B) |
| ARM Sync (cache mismatch) | Collab ARM team: `Azure/Azure Resource Manager (ARM)/Resource Management/Resource not showing up` |

### Step 7 — Mitigation & customer reply

- For lifecycle failures (delete/resize/snapshot) → apply the anchor-specific workaround verbatim (often deallocate + retry, or detach→resize→reattach, or PS recipe in the anchor)
- For platform/known-issues → use the anchor's customer-facing RCA paragraph (e.g., § [MD-Event-2](./playbook-F-disk-deep.md#md-event-2--stornvme-event-129-asap--io-timeout-known-issue) has the December 2025 fleet-wide rollout messaging; § [MD-Platform-1](./playbook-F-disk-deep.md#md-platform-1--502-gateway-error-on-virtualmachines-collection) has the multi-region register-RP messaging)
- For silent features (§ [MD-Colocation-1](./playbook-F-disk-deep.md#md-colocation-1--software-latency-zone-slz-silent-feature-) SLZ) → **do not name the feature**. Use generic "platform optimization" or "allocation policy" wording.

### Step 8 — Handoffs

| Scenario | Owner |
|---|---|
| Soft-delete recovery | **EEEAzureRT** (via Recovery Template Sev 4 IcM + `cssdiskrec@microsoft.com`) |
| Hard-delete (NOT recoverable in most cases) | Hard Deleted Disk TSG, but typically must explain to customer that data is gone |
| Stale `managedBy` after VM deletion | **EEEAzureRT** for KVS update |
| Blob lease blocking delete | **Engineering** via ASC ICM (breaks lease from backend) |
| Reserved-name disk delete | **EEEAzureRT** for backend delete |
| Subscription not registered with new region (502) | Customer self-service `Register-AzResourceProvider -ProviderNamespace Microsoft.Compute` |
| ARM cache resource-not-showing | **ARM Team** collab |
| CRP+disk colocation allocation failures (capacity related) | **WACAP** team first |
| Direct upload SAS issues | XStore team via Disk SME |
| SLZ silent-feature anomalies | Internal-only escalation to PG (do NOT mention to customer) |
| Live cases needing SME | **Disk SME via Ava channel** |

## Cross-references

| Other playbook / reference | Why |
|---|---|
| Playbook A § STG-1..4 | Disk-caused VM restarts (DiskHardwareFailure, DiskIOBlip, VirtualDiskFault on host) — platform-side telemetry, not lifecycle ops |
| Playbook B § OP-DiskMgmt / § OP-DiskLease | Generic CRP-side disk operation errors (CRP-only perspective) |
| Playbook C § STG-Perf-* | Disk performance / throttling / latency without lifecycle failure |
| Playbook E § VMSS-HowTo-HostCaching | VMSS-specific disk management (host caching, sharedDisks) |
| `references/disks-queries.md` | Foundation queries for `DiskRPResourceLifecycleEvent` / `DiskManagerApiQoSEvent` / `DiskManagerContextActivityEvent` / `DiskManagerBackgroundTaskContextActivityEvent` / `DiskRPDiskEncryptionSetLifecycleEvent` |
| `asap-storage-queries.md` | ASAP NVMe deep RCA — § [MD-Event-2](./playbook-F-disk-deep.md#md-event-2--stornvme-event-129-asap--io-timeout-known-issue) cross-links here |
| `storage-account-queries.md` | XStore deep dive for storage-account-level perspective (non-disk) |
| `crp-queries.md` | CRP-side allocation queries (foundation for § [MD-UltraSSD-1](./playbook-F-disk-deep.md#md-ultrassd-1--overconstrainedzonalallocationrequest-ultrassd) and § [MD-Colocation-1](./playbook-F-disk-deep.md#md-colocation-1--software-latency-zone-slz-silent-feature-)) |
