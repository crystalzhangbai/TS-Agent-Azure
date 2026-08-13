# CRP / Control Plane Queries — VM Operations, Allocation, ARM API Tracing

These queries target the Compute Resource Provider (CRP) and ARM control plane.
Use them when investigating VM create/update/delete/start/stop/redeploy failures,
allocation errors, or ARM API-level issues.

Cluster: `crp.kusto.windows.net`
Database: `CrpService`

> ⚠️ **MCP access note**: `crp.kusto.windows.net` may NOT be reachable via the Azure MCP kusto tool (DNS failure). **Prefer `azcrp.kusto.windows.net` / `crp_allprod`** for CRP queries — it has the same data with wider retention (~365 days). The `CrpService` cluster queries below are kept for reference only; for MCP execution, use the equivalent `azcrp` queries in the "CRP via azcrp Cluster" section below.

---

## CRP Operation Lifecycle

### CrpOperationQoSEtwTable — All CRP operations on a VM

Key columns: `subscriptionId`, `resourceGroupName`, `resourceName`, `operationName`, `resultCode`, `durationInMilliseconds`, `correlationRequestId`

```kusto
cluster('crp.kusto.windows.net').database('CrpService').CrpOperationQoSEtwTable
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| where subscriptionId == "{SubscriptionId}"
| where resourceName =~ "{VMName}"
| project PreciseTimeStamp, operationName, resultCode, durationInMilliseconds,
    correlationRequestId, clientApplicationId, resourceGroupName, resourceName,
    subscriptionId, errorCode, errorMessage
| order by PreciseTimeStamp asc
```

Interpretation:
- `resultCode == "OK"` or `resultCode == "200"` — operation succeeded
- `resultCode == "Conflict"` or `409` — concurrent operation conflict
- `operationName` values: `Microsoft.Compute/virtualMachines/write`, `start`, `powerOff`, `restart`, `deallocate`, `redeploy`, `delete`
- `durationInMilliseconds` > 300000 (5 min) — unusually slow operation

### CrpOperationQoSEtwTable — Failed operations only

```kusto
cluster('crp.kusto.windows.net').database('CrpService').CrpOperationQoSEtwTable
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| where subscriptionId == "{SubscriptionId}"
| where resourceName =~ "{VMName}"
| where resultCode !in ("OK", "200", "201", "202", "204", "Accepted")
| project PreciseTimeStamp, operationName, resultCode, errorCode, errorMessage,
    correlationRequestId, durationInMilliseconds
| order by PreciseTimeStamp asc
```

---

## Allocation & Placement

### CRPAllocationDetailsEtwTable — VM allocation/placement details

Key columns: `containerId`, `nodeId`, `allocationAction`, `allocationResult`, `failureReason`

```kusto
cluster('crp.kusto.windows.net').database('CrpService').CRPAllocationDetailsEtwTable
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| where subscriptionId == "{SubscriptionId}"
| where resourceName =~ "{VMName}"
| project PreciseTimeStamp, allocationAction, allocationResult, failureReason,
    containerId, nodeId, clusterName, availabilitySetName, availabilityZone,
    correlationRequestId, vmSize
| order by PreciseTimeStamp asc
```

Interpretation:
- `allocationResult == "Succeeded"` — VM placed successfully
- `allocationResult == "Failed"` — allocation failure (check `failureReason`)
- `failureReason` contains `"OverconstrainedAllocationRequest"` — no capacity in requested constraints
- `failureReason` contains `"AllocationFailed"` — general allocation failure

### CRPAllocationDetailsEtwTable — Allocation failures in a subscription

```kusto
cluster('crp.kusto.windows.net').database('CrpService').CRPAllocationDetailsEtwTable
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| where subscriptionId == "{SubscriptionId}"
| where allocationResult == "Failed"
| summarize count() by failureReason, vmSize, clusterName
| order by count_ desc
```

---

## Container Operations

> ⚠️ **`ContainerOperationQoSEvent` does NOT exist** on any cluster. Do NOT fabricate this table name. For container-level CRP operations, use `CRPContainerOperationsEtwTable` (on `crp.kusto.windows.net/CrpService` — not MCP-reachable) or filter `ApiQosEvent_nonGet` on `azcrp/crp_allprod` by the VM's `resourceName`.

### CRPContainerOperationsEtwTable — CRP container-level operation lifecycle

> ⚠️ This table is on `crp.kusto.windows.net` which is NOT reachable via MCP. For MCP-executable alternative, use `ApiQosEvent_nonGet` on `azcrp/crp_allprod` filtered by `resourceName` (see "CRP via azcrp Cluster" section below).

```kusto
cluster('crp.kusto.windows.net').database('CrpService').CRPContainerOperationsEtwTable
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| where containerId == "{ContainerId}"
| project PreciseTimeStamp, operationType, operationStatus, containerId, nodeId,
    errorCode, errorMessage, durationMs
| order by PreciseTimeStamp asc
```

Interpretation:
- `operationType` values: `CreateContainer`, `StartContainer`, `StopContainer`, `DeleteContainer`, `MigrateContainer`
- `operationStatus == "Succeeded"` — operation completed
- `operationStatus == "Failed"` — check `errorCode` and `errorMessage`

---

## ARM API Tracing

### ARMProd HttpIncomingRequests — ARM incoming requests for a VM

Cluster: `armprod.kusto.windows.net`
Database: `ARMProd`

```kusto
cluster('armprod.kusto.windows.net').database('ARMProd').HttpIncomingRequests
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| where subscriptionId == "{SubscriptionId}"
| where resourceUri contains "{VMName}"
| project PreciseTimeStamp, httpMethod, resourceUri, httpStatusCode,
    correlationId, clientApplicationId, userAgent, durationInMilliseconds
| order by PreciseTimeStamp asc
```

Interpretation:
- Shows all ARM API calls to the VM resource (who called what, when, and the result)
- `httpStatusCode == 200/201/202` — success
- `httpStatusCode == 409` — conflict (concurrent operation)
- `httpStatusCode == 429` — throttled
- `clientApplicationId` — identifies the caller (portal, CLI, SDK, automation)
- Useful for confirming whether a restart/deallocate was customer-initiated vs platform-initiated

### ARMProd HttpIncomingRequests — API calls by correlation ID

```kusto
cluster('armprod.kusto.windows.net').database('ARMProd').HttpIncomingRequests
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| where correlationId == "{CorrelationId}"
| project PreciseTimeStamp, httpMethod, resourceUri, httpStatusCode,
    clientApplicationId, userAgent, durationInMilliseconds
| order by PreciseTimeStamp asc
```

---

## CRP API QoS

### CrpApiQoSEtwTable — CRP API-level quality of service

```kusto
cluster('crp.kusto.windows.net').database('CrpService').CrpApiQoSEtwTable
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| where subscriptionId == "{SubscriptionId}"
| where resourceName =~ "{VMName}"
| project PreciseTimeStamp, apiName, httpStatusCode, durationInMilliseconds,
    correlationRequestId, errorCode, errorDetails, clientApplicationId
| order by PreciseTimeStamp asc
```

Interpretation:
- `apiName` — the CRP API method called (e.g., `VirtualMachines_CreateOrUpdate`, `VirtualMachines_Start`)
- `httpStatusCode == 200` — success
- `httpStatusCode >= 400` — client/server error (check `errorCode` and `errorDetails`)
- Use `correlationRequestId` to trace across CRP -> AzureCM -> RDOS

---

## CRP via azcrp Cluster (crp_allprod)

> **Note**: The queries below target `azcrp.kusto.windows.net` / database `crp_allprod`, which is a different cluster from `crp.kusto.windows.net` / `CrpService` used in the sections above. The `azcrp` cluster provides API QoS events with slightly different schemas and wider retention (~365 days) for CRP operations.

### ApiQosEvent — All CRP operations (including GETs)

Get full CRP API call history for a VM resource including read operations; use to correlate customer-side API calls with platform-side events. `StartTime` is back-calculated from e2e duration.

```kusto
cluster('azcrp.kusto.windows.net').database('crp_allprod').ApiQosEvent
| where PreciseTimeStamp between(datetime('{Start}') .. datetime('{End}'))
| where subscriptionId == '{SubscriptionId}'
| where resourceName == '{ResourceName}'
| extend StartTime = datetime_add('Millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp)
| project StartTime, EndTime = PreciseTimeStamp, resourceName, correlationId, operationId,
    operationName, httpStatusCode, resultCode, resultType, errorDetails,
    e2EDurationInMilliseconds, durationInMin = round(e2EDurationInMilliseconds / 60000.0, 2),
    requestEntity
```

### ApiQosEvent_nonGet — Mutating CRP operations only

Get only mutating CRP operations (PUT/POST/DELETE) for a VM resource; fewer rows and cleaner signal for change tracking and causation analysis.

```kusto
cluster('azcrp.kusto.windows.net').database('crp_allprod').ApiQosEvent_nonGet
| where PreciseTimeStamp between(datetime('{Start}') .. datetime('{End}'))
| where subscriptionId == '{SubscriptionId}'
| where resourceName == '{ResourceName}'
| extend StartTime = datetime_add('Millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp)
| project StartTime, EndTime = PreciseTimeStamp, resourceName, correlationId, operationId,
    operationName, httpStatusCode, resultCode, resultType, errorDetails,
    e2EDurationInMilliseconds, durationInMin = round(e2EDurationInMilliseconds / 60000.0, 2),
    requestEntity
```

### ContextActivity — CRP internal workflow trace

Deep-dive trace of a CRP internal workflow by `activityId`; maps an operation to internal CRP caller chain and source files. Use when API call succeeded but downstream behavior is unexpected.

```kusto
cluster('azcrp').database('crp_allprod').ContextActivity
| where PreciseTimeStamp between(datetime('{Start}') .. datetime('{End}'))
| where activityId == '{ActivityId}'
| project PreciseTimeStamp, message, callerName, sourceFile
```

### VMApiQosEvent — Disk colocation verification (Premium Managed Disk)

"Premium Managed Disk Performance Optimization" silently colocates premium MDs on the same network spine as the VM (target write latency ~2 ms, read ~3 ms). The only post-hoc way to verify whether a specific VM's disks actually got colocated is to parse `extraVMProperties.ColocationSkipDetails` on the relevant `VMApiQosEvent` row.

```kusto
let SubId = "{SubscriptionId}";
let RgName = "{ResourceGroupName}";
let VmName = "{VMName}";
let vmDeploymentDate = datetime({StartTime}); // VM create / start / restart time
let timerange = 12d;
cluster("azcrp").database("crp_allprod").VMApiQosEvent
| where PreciseTimeStamp between (vmDeploymentDate .. timerange)
    and subscriptionId == SubId
    and resourceGroupName =~ RgName
    and resourceName =~ VmName
    and isManaged == "True"
| extend colocationSkipDetails       = extractjson("$.ColocationSkipDetails", extraVMProperties)
| extend colocationSkipDetailsReason = extractjson("$.Reason", colocationSkipDetails)
| extend colocationStatus = iff(networkSpineIds != "", "Colocation succeeded",
                            iff(networkSpineIds == "" and colocationSkipDetailsReason != "",
                                "Colocation skipped and normal allocation succeeded", "N/A"))
| project TIMESTAMP, operationName, resultType, colocationStatus, colocationSkipDetails, networkSpineIds, operationId
```

Interpretation:
- `colocationStatus = "Colocation succeeded"` + non-empty `networkSpineIds` → premium disk + VM are on the same spine.
- `colocationStatus = "Colocation skipped..."` → check `colocationSkipDetailsReason` (typical causes: VM SKU not eligible, region/capacity, unmanaged disk).
- Workaround when not colocated: stop-deallocate then start the VM (this also triggers colocation for existing premium MDs).
- TSG: [Disk Collocation_Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/Disk-Collocation_Perf).

### VMApiQosEvent + AlertingEvent — Colocation allocation failures

When a VM create/start fails and you suspect "colocation could not be satisfied" (e.g., capacity-bound spines), join the failed `VMApiQosEvent` rows against `AlertingEvent` filtered on colocation/networkspine alert codes.

```kusto
let _subscriptionId = "{SubscriptionId}";
let _resourceGroupName = "{ResourceGroupName}";
let _vmName = "{VMName}";
let vmDeploymentDate = datetime({StartTime});
cluster("azcrp").database("crp_allprod").VMApiQosEvent
| where PreciseTimeStamp between (vmDeploymentDate .. 1d)
| where subscriptionId == _subscriptionId and resourceGroupName == _resourceGroupName and resourceName contains _vmName
| where isManaged == "True"
| where resultType == 2
| join kind=leftouter (
    cluster("azcrp").database("crp_allprod").AlertingEvent
    | where PreciseTimeStamp between (vmDeploymentDate .. 1d)
    | where message contains "colocation" or alertCode contains "networkspine" or alertCode contains "colocation"
    | extend operationId = activityId
  ) on MonitoringApplication, subscriptionId, operationId
| extend colocationStatus = iff(alertCode != "",
                            "Colocation was skipped but operation still failed",
                            "Colocation was NOT skipped and operation failed")
| project operationId, operationName, resourceGroupName, resourceName, colocationStatus,
    colocationSkipReasonCode = alertCode, colocationSkipReason = message
```

Interpretation:
- A row with `colocationStatus = "Colocation was skipped but operation still failed"` and `alertCode` containing `networkspine` → spine-level capacity issue. Route to **WACAP** team as capacity failure.
- Typical exception payload pattern: `Microsoft.Windows.Azure.GCM.Allocator.AllFabricsFailedToAllocateException: Colocation of the tenants did not succeed in any of the allowed network spines : bn7-AZ1-Shared-T2-Set1, ...`
- Non-capacity colocation failures → escalate via the standard CRP escalation path.

### Physical Zone ↔ Logical Zone Mapping

Resolve the correspondence between logical availability zones (1/2/3) and physical zone names for a given subscription and region.

Cluster: `azcrpbifollower.kusto.windows.net` → Database: `bi_allprod`

```kusto
let _SubscriptionID = '{SubscriptionId}';
let _Region = '{Region}';
cluster('azcrpbifollower.kusto.windows.net').database('bi_allprod').Subscription
| where SubscriptionId == _SubscriptionID
| where Region contains _Region
| where TIMESTAMP > ago(1d)
| limit 1
| extend AvZones = todynamic(AvailabilityZoneMappings)
| project SubscriptionId, Region,
    Zone1 = AvZones[0].PhysicalZone,
    Zone2 = AvZones[1].PhysicalZone,
    Zone3 = AvZones[2].PhysicalZone
```

> Output shape: `SubscriptionId | Region | Zone1 | Zone2 | Zone3`

---

## Investigation Flow: VM Operation Failure (Create / Start / Stop / Delete)

When a VM operation (create, start, stop, delete, redeploy, update) fails or is reported "stuck", run these tables in order. Each step narrows the failure layer (ARM → CRP → Allocator → Container → Node).

| Step | Table / Source | What it tells you |
|---|---|---|
| 1 | `CrpOperationQoSEtwTable` (`Cirrus`) | Find the operation by `OperationId` / `SubscriptionId` / time. Returns `OperationName`, `ResultType`, `ErrorCode`, `ErrorMessage`, `DurationMs`. This is your starting point. |
| 2 | `CRPAllocationDetailsEtwTable` (`Cirrus`) | For Create/Start — see allocation result (success, NoSubscriptionMatchedQuota, AllocationFailed, ZonalAllocationFailed). Includes target Cluster / Region. |
| 3 | `CRPContainerOperationsEtwTable` (`Cirrus`) | Container-level CRP operations (CreateContainer, StartContainer, etc.) and their result codes. |
| 4 | `HttpIncomingRequests` (`armprod`) | Trace the ARM API call — confirms client identity, IP, user agent, httpStatusCode. Useful when CRP rows are missing → blocked before CRP. |
| 5 | `LogContainerHealthSnapshot` (`Azcsupfollower` / `AzureCM`) | Container state at the time of failure — `containerState`, `faultInfo`, `containerLifecycleState`. |
| 6 | `NodeServiceOperationEtwTable` (`AzureCM`) | Was a StartContainer / StopContainer slow or failing on the target node? |
| 7 | `TMMgmtNodeEventsEtwTable` (`AzureCM`) | Node-level issues (DirtyShutdown, BugCheck, PXEEvent) that may have blocked the op. |

### When to branch
- **Step 1 returns `NoSubscriptionMatchedQuota` / quota error** → not a platform failure — recommend customer raise a quota request.
- **Step 2 returns `AllocationFailed`** → SKU/region capacity issue — pivot to `vm-kusto-query` § Allocation, and build the ASI Cluster utilization link from [`../dashboards/`](../dashboards/) or open ASI manually.
- **Step 3 returns container fault** → pivot to `_shared-vm-identification.md` Q2 (`LogContainerHealthSnapshot.faultInfo`) for the FaultCode → route by Playbook A § STG / § HW.
- **Step 4 returns 4xx with non-customer identity** → likely throttling — check ARM throttling tables.
- **Step 5/6 show stuck `StartContainer`** → host-side issue — pivot to `azcore-queries.md` (HyperV / RDOS) and `_shared-vm-identification.md` Q3 (`LogNodeSnapshot.nodeState`).

> See also: `_shared-vm-identification.md` Q7 (`KronoxVmOperationEvent`) — runs in parallel with Step 1 to confirm whether the customer or platform initiated the op.

---

## CRP Error-Code Routing Reference

Once Step 1 (`CrpOperationQoSEtwTable` or `ApiQosEvent`) returns the failed operation, the `ErrorCode` / `errorDetails` field drives which TSG you open next. This table mirrors the official **Cant-Start-Stop-Home** decision tree.

### CrpOperationQoSEtwTable — Pull the error code for a single failed op

```kusto
// cluster('Cirrus').database('Cirrus').CrpOperationQoSEtwTable
let opId = "<OperationId-from-customer>";
CrpOperationQoSEtwTable
| where TIMESTAMP between (datetime(<Start>) .. datetime(<End>))
| where OperationId == opId or correlationId == opId
| project TIMESTAMP, OperationName, ResultType, ErrorCode, ErrorMessage,
          ResourceId, SubscriptionId, DurationMs, correlationId
| order by TIMESTAMP asc
```

### Error code → TSG / next action

| ErrorCode (CRP) | Layer | Meaning | Primary TSG |
|---|---|---|---|
| `AllocationFailed` / `ZonalAllocationFailed` | Allocator | No capacity for the SKU/zone/region | [Service Allocation Failures](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495461) → drill with `CRPAllocationDetailsEtwTable` |
| `OverconstrainedAllocationRequest` | Allocator | PPG / AvSet / colocation constraints can't be satisfied | [OverconstrainedAllocationRequest RCA](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495467) — recommend PPG split |
| `NoSubscriptionMatchedQuota` | Quota | Subscription quota exhausted for the family | Recommend customer raise quota request — NOT a platform failure |
| `OutOfTimeBudgetException` / `FabricInternalOperationError` | CRP→Fabric | CRP couldn't get a response from AzSM/Job within the time budget | [OutofTimeBudgetException](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495454) — pivot to `NodeServiceOperationEtwTable` + `LogContainerHealthSnapshot` |
| `VMStartTimedOut` | Container/Node | StartContainer didn't complete within CRP's wait | [VM Did Not Start in the Allotted Time](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495485) — pivot to `LogNodeSnapshot.nodeState` + `azcore-queries.md` HyperV |
| `OSProvisioningTimedOut` | Guest OS | Provisioning agent never reported Ready (mostly Create) | [OSProvisioningTimedOut (OSPTO)](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495667) — pivot to guest log analysis (`vm-log-analyzer`) |
| `NetworkingInternalOperationError` | NRP | NRP failed to attach/detach NIC during the VM op | [NetworkingInternalOperationError](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495442) — pivot to `networking-queries.md` § NRP |
| `InternalDiskManagementError` | Disk RP | Disk attach/detach/release on Delete failed | [Failed to Delete VM — InternalDiskManagementError](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/518459) — pivot to `disks-queries.md` § DiskManagerApiQoSEvent |
| `AcquireDiskLeaseFailed` | XStore | Unmanaged page-blob lease still held by previous container | [Disk Lease wiki](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495439) — break-lease via XStore SME |
| `BadRequest` / `OperationNotAllowed` | CRP | Request shape rejected (resource state, locked, missing field) | Review `ErrorMessage`; usually customer-action |
| `RetryableError` / `InternalOperationError` (generic) | CRP | Transient — check if the next retry succeeded via `OperationId` in `ContextActivity` | Trace `ContextActivity` activityId chain |

### ARM-layer rejects (operation never reached CRP)

If Step 1 returns **no rows**, the failure was caught upstream by ARM. Use `armprod` cluster (`HttpIncomingRequests`) and route on the HTTP error:

| ARM error | Action |
|---|---|
| `403 AuthorizationFailed` | RBAC — customer-side fix |
| `409 ScopeLocked` | [Scope Locked](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495460) — customer removes lock |
| `403 RequestDisallowedByPolicy` | Customer reviews / amends Azure Policy |
| `429 TooManyRequests` | ARM throttling — check `userAgent` / `clientIp`; advise back-off |
| `5xx / InternalServerError` | Collab with ARM Pod |

### Pivot back to platform tables after error-code identified

- For **container-level retries** (`OutOfTimeBudgetException`, `VMStartTimedOut`, etc.) → `azurecm-queries.md` § `LogContainerHealthSnapshot.faultInfo` + `_shared-vm-identification.md` Q2.
- For **allocator failures** → build the ASI Cluster utilization / Compute Capacity Advisory links from [`../dashboards/`](../dashboards/) or open the pages manually.
- For **disk-side errors** → `disks-queries.md` (DiskRPResourceLifecycleEvent + DiskManagerApiQoSEvent).
- For **NIC-side errors** → `networking-queries.md` § Hybridnetworking + NRP.
