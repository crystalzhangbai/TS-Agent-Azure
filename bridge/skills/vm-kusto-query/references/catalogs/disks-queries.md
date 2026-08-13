# Disks RP Queries — Managed Disk Lifecycle, Existence Check, Storage Layer, Recovery

Primary cluster: `cluster("disks.kusto.windows.net").database("Disks")`

This file holds **reusable KQL bodies** that Playbook F (`playbook-F-disk-core.md` + `playbook-F-disk-deep.md`) and other playbooks delegate to. Per-error-code TSGs (delete leased, billing, snapshot leak, encryption, colocation, etc.) live in the deep file; this reference covers the **foundation queries** that show up across many scenarios.

---

## Table inventory (Disks DB)

| Table | What it captures |
|---|---|
| `DiskRPResourceLifecycleEvent` | Per-disk lifecycle events (Create, Update, Attach, Detach, Delete, SoftDelete, HardDelete, DDSnapshotCreate, DDSnapshotCopyCompleted, DDDiskImportCompleted, DDRestoreFromInstantAccessSnapshot). Primary join key: `id` (DiskRP internal ID), `resourceName`, `crpDiskId` |
| `DiskManagerApiQoSEvent` | Per-API-call quality-of-service for Disks RP operations (GET, PUT, PATCH, DELETE, snapshot ops). Use to verify backend existence + correlate by `correlationId` |
| `DiskManagerContextActivityEvent` | Verbose per-activity trace logs (Goal-seeking pipeline, blob lease state, FooterValidationError messages). Joined to `DiskManagerApiQoSEvent` via `activityId` (= `operationId`) |
| `DiskManagerBackgroundTaskContextActivityEvent` | Background tasks (cross-region snapshot copy, hydration). `taskName` + `traceCode` identify the task |
| `Disk` | Latest-known disk snapshot table (different column names: `DisksId`, `DisksName`, `DiskResourceType`, `OwnershipState`, `AccountType`, `BlobUrl`, `StorageAccountName`, `DiskSizeBytes`, `CrpDiskId`) |
| `AssociatedXStoreEntityResourceLifecycleEvent` | Storage-layer events (entity name/type, hydration state, storage account name) |
| `DiskRPDiskEncryptionSetLifecycleEvent` | DES lifecycle — needed to recover deleted CMK-encrypted disks (find KV + key URL for deleted DES) |

---

## DiskRPResourceLifecycleEvent — Disk Lifecycle

Key columns: `subscriptionId`, `resourceGroupName`, `resourceName`, `diskType`, `diskEvent`, `stage`, `state`, `storageAccountType`, `id` (internal Disk RP ID), `crpDiskId`, `diskSizeBytes`, `blobUrl`, `storageAccountName`, `diskOwner`, `diskEncryptionSetId`, `MonitoringApplication` (= `DiskRP-<Region>_Monitoring`), `RPTenant`

### Find disk by name & subscription

```kusto
cluster("disks.kusto.windows.net").database("Disks").DiskRPResourceLifecycleEvent
| where subscriptionId == "{SubscriptionId}"
| where resourceName == "{DiskName}"
| where PreciseTimeStamp >= ago(90d)
| project PreciseTimeStamp, resourceName, subscriptionId, resourceGroupName,
          diskEvent, stage, state, storageAccountType, diskSizeBytes, id
| order by PreciseTimeStamp asc
```

### Full lifecycle (latest state per disk)

```kusto
cluster("disks.kusto.windows.net").database("Disks").DiskRPResourceLifecycleEvent
| where resourceName == "{DiskName}"
| where subscriptionId == "{SubscriptionId}"
| summarize arg_max(PreciseTimeStamp, *) by resourceName
| project PreciseTimeStamp, resourceName, subscriptionId, resourceGroupName,
          diskEvent, stage, state, storageAccountType, diskOwner, id
```

### Disk lifecycle by storage account

```kusto
cluster('Disks').database('Disks').DiskRPResourceLifecycleEvent
| where (TIMESTAMP >= datetime({StartTime}) and TIMESTAMP <= datetime({EndTime}))
| where subscriptionId == "{SubscriptionId}"
| where storageAccountName == "{StorageAccountName}"
| project TIMESTAMP, resourceName, diskEvent
```

### Soft-delete check (regional filter via MonitoringApplication)

Used by § MD-Delete-2 (Managed Disk Recovery) to verify a disk is soft-deleted and eligible for restore. Premium SSD v2 and Ultra SSD are NOT recoverable in any state.

```kusto
cluster("disks.kusto.windows.net").database("Disks").DiskRPResourceLifecycleEvent
| where MonitoringApplication == "DiskRP-{Region}_Monitoring" // e.g., DiskRP-centralus_Monitoring
| where subscriptionId == "{SubscriptionId}"
| where resourceName contains "{DeletedDiskName}"
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| project PreciseTimeStamp, resourceGroupName, resourceName, blobUrl, storageAccountType, diskEvent, RPTenant
```

Verify latest `diskEvent == "SoftDelete"` AND `storageAccountType != "UltraSSD_LRS"` and `!= "Premium_SSDv2"`.

### Lifecycle event enum

`diskEvent` values: `Create`, `Update`, `Attach`, `Detach`, `Delete`, `SoftDelete`, `HardDelete`, `DDSnapshotCreate`, `DDSnapshotCopyCompleted`, `DDDiskImportCompleted`, `DDRestoreFromInstantAccessSnapshot`

`state` values: `Unattached`, `Attached`, `Reserved`, `ActiveSAS`

---

## DiskManagerApiQoSEvent — Backend Existence Check + Operation Triage

### Existence check (does this disk exist?)

```kusto
cluster("disks.kusto.windows.net").database("Disks").DiskManagerApiQoSEvent
| where resourceName == "{DiskName}"
| where subscriptionId == "{SubscriptionId}"
| project PreciseTimeStamp, operationName, httpStatusCode, resourceName,
          clientApplicationId, userAgent, region
| order by PreciseTimeStamp desc
| limit 10
```

Interpretation:
- `httpStatusCode == 200` + `clientApplicationId == "Azure Resource Graph"` → Disk **exists**
- `httpStatusCode == 404` → Disk has been **deleted**
- `operationName == "Disks.ResourceOperation.GET"` → ARG periodic crawl

### Full op detail for an operation (live resize, snapshot, etc.)

This is the foundation query used by § MD-Resize-2 (LiveResize) and several other deep-file sections.

```kusto
cluster('disks.kusto.windows.net').database('Disks').DiskManagerApiQoSEvent
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where subscriptionId contains "{SubscriptionId}"
| where resourceGroupName contains "{ResourceGroupName}"
| where resourceName contains "{DiskName}"
| where operationName !contains "Disks.ResourceOperation.GET"
| where operationName !contains "DiskOperations.Get.GET"
| project PreciseTimeStamp, correlationId, operationId, operationName, resultCode,
          resourceName, errorDetails, userAgent, requestEntity,
          subscriptionId, resourceGroupName, region, e2EDurationInMilliseconds, httpStatusCode
| order by PreciseTimeStamp asc
```

### Disk attach/detach operations for a VM (around disk attach time)

```kusto
cluster('disks.kusto.windows.net').database('Disks').DiskManagerApiQoSEvent
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where subscriptionId == "{SubscriptionId}"
| where resourceName contains "{DiskName}" or resourceGroupName contains "{ResourceGroupName}"
| where operationName has_any ("Attach", "Detach")
| project PreciseTimeStamp, correlationId, operationId, operationName, resultCode,
          resourceName, errorDetails, e2EDurationInMilliseconds, httpStatusCode,
          subscriptionId, resourceGroupName, region
| order by PreciseTimeStamp asc
```

> **IMPORTANT**: The duration column on `DiskManagerApiQoSEvent` is `e2EDurationInMilliseconds` — NOT `durationMs`, `DurationMs`, or `duration`. Using the wrong name causes SEM0100.

### Get disk op via correlationId (cross-RP join from ARM correlation)

```kusto
cluster("disks.kusto.windows.net").database("Disks").DiskManagerApiQoSEvent
| where PreciseTimeStamp > datetime({StartTime}) and PreciseTimeStamp < datetime({EndTime})
| where subscriptionId == "{SubscriptionId}"
| where correlationId == "{CorrelationId}"
```

---

## DiskManagerContextActivityEvent — Verbose Activity Trace

Used to investigate failures that surface above the API layer (lease conflicts, FooterValidationError, encryption checks). Always filter by `activityId == "{OperationId}"` from `DiskManagerApiQoSEvent`.

### Generic verbose trace

```kusto
cluster('disks.kusto.windows.net').database('Disks').DiskManagerContextActivityEvent
| where PreciseTimeStamp > datetime({StartTime})
| where PreciseTimeStamp < datetime({EndTime})
| where activityId == "{ActivityId}"
| project PreciseTimeStamp, callerName, subscriptionId, message, sourceFile, lineNumber
```

### Filter for specific error signatures

```kusto
cluster('disks.kusto.windows.net').database('Disks').DiskManagerContextActivityEvent
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where subscriptionId contains "{SubscriptionId}"
| where activityId == "{ActivityId}"
| where message contains "{ErrorSignature}" // e.g. "FooterValidationError", "BreakLeaseFeatureState"
| project PreciseTimeStamp, callerName, subscriptionId, message, sourceFile, lineNumber, activityId
```

Common signatures and what they mean:
- `FooterValidationError` — Pattern B of LiveResize failure (see § MD-Resize-2)
- `BreakLeaseFeatureState: Enabled, leaseBreakable: False` — blob lease blocking delete (see § MD-Delete-1)
- `DiskServiceInternalError: The operation is not permitted because there is a lease on the blob` — lease conflict (same as above)
- `VM has legacy disk encryption - False, unified disk encryption - True` — UDE conflict with PV2 attach (see § MD-Encryption-1)
- `Switching activity-id to <X>` — preemption by sibling op (see § MD-Resize-2 note on preemption)

---

## DiskManagerBackgroundTaskContextActivityEvent — Background Tasks

Used to verify long-running background tasks (cross-region snapshot copy) are still progressing vs hung.

### Cross-region snapshot copy progress (TrackingAsyncCopyTask)

```kusto
let _region = "{Region}";
let _snapshotARMId = "/subscriptions/{SubscriptionId}/resourcegroups/{ResourceGroupName}/providers/microsoft.compute/snapshots/{SnapshotName}";
let _subid = tostring(split(_snapshotARMId, "/")[2]);
let _rgname = tostring(split(_snapshotARMId, "/")[4]);
let _rname = tostring(split(_snapshotARMId, "/")[8]);
cluster("disks").database("disks").DiskManagerBackgroundTaskContextActivityEvent
| where PreciseTimeStamp > ago(6h)
| where RPTenant =~ strcat("DiskRP-", _region) and taskName == "TrackingAsyncCopyTask" and traceCode == 710103 and lineNumber != 314
| where message contains strcat("/Subscriptions/", _subid, "/ResourceGroups/", _rgname, "/disks/", _rname)
| project PreciseTimeStamp, message, callerName
| order by PreciseTimeStamp asc
```

Interpretation:
- Rows present + progressing → copy still active
- No rows OR stale most-recent row + no `completionPercent` change → copy hung → ICM xstore/Triage (table-server issue)

---

## Disk Snapshot Table

Column names differ from lifecycle table: `DisksId`, `DisksName`, `ResourceGroup`, `DiskResourceType`, `OwnershipState`, `AccountType`, `BlobUrl`, `StorageAccountName`, `DiskSizeBytes`, `CrpDiskId`

```kusto
cluster("disks.kusto.windows.net").database("Disks").Disk
| where DisksName has "{DiskName}"
| order by PreciseTimeStamp desc
| limit 5
| project PreciseTimeStamp, DisksId, DisksName, DiskResourceType,
          OwnershipState, AccountType, ResourceGroup, DiskSizeBytes,
          BlobUrl, StorageAccountName, CrpDiskId
```

If not found here, the disk may have been deleted.

---

## AssociatedXStoreEntityResourceLifecycleEvent — Storage Layer

```kusto
cluster("disks.kusto.windows.net").database("Disks").AssociatedXStoreEntityResourceLifecycleEvent
| where parentDiskId == "{DiskRPInternalId}"
    or entityName has "{DiskName}"
| project PreciseTimeStamp, id, parentDiskId, entityName, entityType,
          lifecycleEventType, stage, entityUri, storageAccountName,
          storageAccountType, entitySizeBytes, isHydrated, subscriptionId
| order by PreciseTimeStamp asc
```

---

## DiskRPDiskEncryptionSetLifecycleEvent — DES Lifecycle (CMK Disk Recovery)

Used by § MD-Encryption-2 (Find DES for CMK disk) when recovering CMK-encrypted disks whose Key Vault was also deleted.

```kusto
cluster("disks.kusto.windows.net").database("Disks").DiskRPDiskEncryptionSetLifecycleEvent
| where PreciseTimeStamp >= datetime({StartTime})
| where subscriptionId == "{SubscriptionId}"
| project resourceName, resourceGroupName, keyVaultId, keyUrl
```

Joined to deleted-disk lifecycle via `diskeSet == resourceName AND diskeSetRg == resourceGroupName` — see § MD-Encryption-2 for full recipe.

---

## ID Cross-Reference

| Source | Table | Key Columns |
|--------|-------|-------------|
| ARM Subscription ID → VM internal IDs | `LogContainerSnapshot` (AzureCM) | `subscriptionId` → `containerId`, `nodeId`, `tenantName` |
| Disk Name → Subscription | `DiskRPResourceLifecycleEvent` | `resourceName` → `subscriptionId`, `resourceGroupName` |
| Disk Name → Backend Status | `DiskManagerApiQoSEvent` | `resourceName` → `httpStatusCode` |
| Disk internal ID → Storage | `AssociatedXStoreEntityResourceLifecycleEvent` | `parentDiskId` → `entityUri`, `storageAccountName` |
| CorrelationId → CRP op | `azcrp.crp_allprod.ApiQosEvent_nonGet` | `correlationId` (cross-cluster) |
| CorrelationId → DiskRP op | `disks.Disks.DiskManagerApiQoSEvent` | `correlationId` |
| OperationId → verbose trace | `disks.Disks.DiskManagerContextActivityEvent` | `activityId == operationId` |
| Deleted CMK disk → KV+key | `DiskRPResourceLifecycleEvent` JOIN `DiskRPDiskEncryptionSetLifecycleEvent` | `diskeSet == resourceName` |

---

## See also (delegates from Playbook F)

- § MD-Delete-1 — Unable to Delete Managed Disk (4-cause router)
- § MD-Delete-2 — Managed Disk Recovery (soft-delete bulk recovery, 2 KQL incl. all-region mapping)
- § MD-Delete-3 — Unable to Delete Disk Leased (Databricks + blob lease)
- § MD-Resize-2 — LiveResizeStorageClientFailure (Pattern A SRP Timeout vs Pattern B FooterValidationError)
- § MD-Snapshot-1 — PV2 Cumulative Snapshot timing
- § MD-Snapshot-2 — Instant Access Snapshot states + errors
- § MD-Snapshot-3 — Unable to Create New Snapshot (Azure Resource Graph for snapshot count)
- § MD-Snapshot-4 — Cross-Region Snapshot Copy (hung copy detection)
- § MD-Encryption-1 — Parameter encryptionSettings is not allowed (UDE conflict)
- § MD-Encryption-2 — Find DES for CMK disk recovery
- § MD-Billing-1 — Standard SSD/HDD billing (3 KQL: PAv2 + XStoreAccountCapacityHourly + XStoreAccountTransactionsHourly + XStoreAccountBillingHourly)
- § MD-Colocation-1 — Software Latency Zone (SLZ) silent feature (6 KQL — VMApiQosEvent + AlertingEvent + ProcessFailure + ApiQosEvent_nonGet)
- § MD-UltraSSD-1 — UltraSSD OverconstrainedZonalAllocationRequest
- § MD-Other-* — 502 Gateway, NVMe Event 129, TLS not permitted, etc.

Cross-link reference files:
- ASAP/NVMe-related disk reset events → `asap-storage-queries.md` (cross-cluster)
- Standard HDD/SSD billing → `storage-account-queries.md` (XStore deep dive)
- VM allocation failures referencing disks → `crp-queries.md` (CRP-side allocation)
