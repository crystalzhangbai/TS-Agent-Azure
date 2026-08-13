# Playbook E — VMSS (Virtual Machine Scale Sets) (Core)

> **Purpose**: One-page decision tree for cases involving **Azure Virtual Machine Scale Sets** (VMSS) in both Uniform and Flexible orchestration modes. Use this first; drop into [`playbook-E-vmss-deep.md`](playbook-E-vmss-deep.md) for per-TSG bodies.
>
> **Source**: Distilled from `/SME Topics/Virtual Machine Scale Sets (VMSS)/*` (45 TSGs + Workflows + key How-Tos) on csswiki AzureIaaSVM. KQL bodies live mostly inline in the deep file (INLINE style) due to verbatim RCA wording and PG-bug references; common CRP / NRP / NetMon queries delegate to [`crp-queries.md`](../catalogs/crp-queries.md) / [`networking-queries.md`](../catalogs/networking-queries.md) / [`azurecm-queries.md`](../catalogs/azurecm-queries.md) where the same bodies are already cataloged.
>
> **Scope**:
>
> - **Deployment / Create / Delete** — `Unable to Create_VMSS`, `Unable to Delete_VMSS`, `ApplicationGatewayErrorApplyingConfiguration`, `AlreadyLeaseOnContainer`.
> - **Scaling** — `AllocationFailures`, `SubnetIsFull`, `Exceeds 40 Limit`, `CostToBalance is not Zero`, `PublicIPCountLimitExceeded`, `ComputerNamePrefixTooLong`, `MoreInstancesThanRequested` (overprovisioning), `StandBy Pools`, `Scaling differences Uniform vs Flex`, `ScalingPolicyAKS`, `Scale-out Network unreachable (AzDO Pipelines)`, `CannotDeployThrottled` (CRP throttling), Auto AZ Balance.
> - **Upgrade / OS Image** — `MaxUnhealthyUpgradedInstancePercent`, `Uniform AutoOSUpgrade`, `Latest Version AutoOSUpgrades`, `PropertyChangeNotAllowed`, `VmssUDWalkTimeout` (SF), `OSPTO during scale-out`, `enableAutomaticUpdates vs AutoOSUpgrade vs UpgradePolicy`.
> - **State** — `FailedState`, `HealthDegraded`, `OrchestrationServiceNotInRunningState` (auto-repair), `LongRunningOperation`, `Retryable Error`, `Placement Group Errors` (SPG), `MaxPerTenantCertificatesCountReached`.
> - **Extensions** — `VM Extension Provisioning Error`, `Operation Not Allowed on Extension Marked for Deletion`, `Resource Lock Causing Extension Failures` (Linux RPM lock), `Failed to restart CMG VMSS` (DSC SAS token + Rolling Upgrade outage).
> - **Networking / Connectivity** — `Cannot Ping/RDP/SSH (H-series MTU bug)`, `Stale IP After Scale-in`.
> - **Flex-specific** — `VMSS Flex Orchestration Mode`, `Azure Fleet`, `Ghost Load Balancing Devices`, `VMSS Instance Mix`, `Spot Priority Mix`, `VmssFlexAutoOSUpgrade` (out-of-scope), `Spot Evictions Multi Placement Group`.
> - **Spot** — `Spot Known Issues` (SkuNotAvailable, autoscale not restoring), `SpotEvictionsMultiPlacementGroup`.
> - **Workflows** — `Scaling Issues Workflow`, `Cannot RDP/SSH VMSS Workflow`, `Cannot Update Scale Set Workflow`.
> - **How-Tos covered**: `Helpful Kusto Queries`, `Terminate Notifications` (IMDS Scheduled Events), `Host Caching In VMSS` (Uniform vs Flex), `Autorepair_VMSS` (via Orchestration Service TSG).
>
> **Boundary**:
>
> - VMSS instance actually **rebooted** during an upgrade or LM window → start with [`playbook-A-restarts-core.md`](playbook-A-restarts-core.md), come back here for the **scale-out / upgrade correlation** sub-step.
> - VMSS instance only **slowed down** → [`playbook-C-performance-core.md`](playbook-C-performance-core.md).
> - VMSS instance **cant start/stop** due to a generic CRP error code (`AllocationFailed`, `OperationNotAllowed`, etc.) that is NOT VMSS-shape-specific → [`playbook-B-cant-start-stop-core.md`](playbook-B-cant-start-stop-core.md); this playbook owns the **VMSS-orchestration-specific** allocation/upgrade/rolling-walk failures.
> - Maintenance window or Live Migration on a VMSS instance → [`playbook-D-maintenance-core.md`](playbook-D-maintenance-core.md).
> - Per-extension RCA (waagent, CSE script content, DSC config logic) → delegate to [`vm-log-analyzer`](../../../vm-log-analyzer/SKILL.md) after using this playbook to isolate which extension + which instance.
> - **Service Fabric VMSS** specific UDWalk / MR / durability issues — VM team supports investigation, but **SF team drives**. See § VMSS-UDWalk-1 and § VMSS-Alloc-1.

---

## Step 0 — Inputs you need

| Variable | Source |
|---|---|
| `{SubscriptionId}` | DFM / customer email / resource ID |
| `{ResourceGroupName}` | DFM / resource ID |
| `{VMSSName}` | DFM / resource ID |
| `{InstanceId}` | from ASC operations / customer report ("instance 5 broken") |
| `{OrchestrationMode}` | `Uniform` or `Flexible` — derive from ASC ScaleSet view or `az vmss show` (`orchestrationMode` field) |
| `{TenantName}` / `{TenantId}` | derived in Step 1 from `LogTenantSnapshot` (per-PG tenant), or from `VmssVMGoalSeekingActivity` message body |
| `{NodeId}` / `{ContainerId}` | per instance — same path as Playbook A, via `LogContainerSnapshot` |
| `{CorrelationId}` / `{OperationId}` / `{ActivityId}` | from ASC → VMSS → Operations → expand failed op → CRP MDM link; or from customer's CLI/PS error |
| `{StartTime}` / `{EndTime}` (UTC) | Customer report — extend ±2h |
| `{ErrorCode}` | the bit after `ProvisioningState/failed/` (e.g., `AllocationFailed`, `OSProvisioningTimedOut`, `VMExtensionProvisioningTimeout`) |
| `{ImageReference}` | for Auto OS Upgrade scenarios — get from VMSS Model |
| `{ExtensionName}` / `{ExtensionType}` | for extension failures |

Universal VM-identification queries (split resource ID, find Node/Container per instance): see [`_shared-vm-identification.md`](../_meta/_shared-vm-identification.md).

---

## Step 1 — Identify VMSS shape and orchestration mode

**VMSS is not a single VM.** Decide first which orchestration mode the scale set uses — every downstream decision depends on it.

| Source | What to read |
|---|---|
| ASC → ScaleSet view | "ScaleSet with Uniform Orchestration" vs "ScaleSet with Flexible Orchestration" headers |
| `az vmss show -g <rg> -n <vmss>` | `orchestrationMode` field (`Uniform` / `Flexible`) |
| KQL on a Flex VMSS — verify via `ConvergedApiVmss = true` label | see deep § VMSS-Flex-1 (Orchestration Mode → Q1 Find VMO operations) |

**Capability matrix** (see deep § VMSS-Flex-1 for full table):

| Capability | Uniform | Flex |
|---|---|---|
| Max instances | 1000 | 1000 |
| Multiple VM sizes / OS in one VMSS | ❌ | ✓ |
| Per-instance OS-disk control (swap disk, redeploy with replacement disk) | ❌ | ✓ |
| Per-instance host caching change | ❌ | ✓ |
| Service Fabric | ✓ | ❌ |
| Azure Dedicated Host | ✓ | ❌ |
| Instance Protection | ✓ | ❌ |
| Spot + Standard mix | ❌ (all-Spot only) | ✓ (Spot Priority Mix) |
| Backup / Site Recovery | ❌ | ✓ |
| Auto AZ Balance | ✓ | ✓ |
| AutoOSUpgrade | ✓ | ⚠ Private Preview only — § VMSS-Flex-AutoOSUpgrade |

**`singlePlacementGroup` (SPG)** is the second shape switch:

| SPG value | Behavior | Max instances (Platform Image) | Max instances (Custom Image) | Reversible? |
|---|---|---|---|---|
| `true` | Single placement group → single cluster (or spanned scope on AzSM) | 100 (1 PG) or 100/zone with multi-AZ | 100 | n/a |
| `false` | Multiple PGs → instances may land on multiple clusters | 1,000 | 600 | ❌ **Cannot be reverted to true** |

If `singlePlacementGroup=false` is set, certain workloads break (Service Fabric explicitly does not support it). Always have the SPG conversation BEFORE recommending the flip.

See deep § VMSS-Shape-1 (SPG / orchestration / capability matrix) for full decision recipes.

---

## Step 2 — Classify the case by symptom bucket

Pick the bucket from customer wording — then dispatch to the right deep §.

### 2a. Customer wording → bucket → deep §

| Customer phrase (EN / 中文) | Bucket | Deep § |
|---|---|---|
| "VMSS scale-out failing / cannot add instances / `AllocationFailed` (扩容失败 / 分配失败)" | `VMSS-Scale-Allocation` | § VMSS-Alloc-1 (capacity / zone / sub-pinning / resize), § VMSS-Alloc-2 (`Subnet is Full`), § VMSS-Alloc-3 (`Exceeds 40 limit`), § VMSS-Alloc-4 (`PublicIPCountLimit / StaticPublicIPCountLimitReached`), § VMSS-Alloc-5 (`ComputerNamePrefixTooLong`) |
| "VMSS scale-out creates MORE instances than I asked (扩容多了)" | `VMSS-Scale-Overprovision` | § VMSS-Scale-2 (overprovisioning explanation) |
| "Manual scale gives `CostToBalance is not zero`" | `VMSS-Scale-CostToBalance` | § VMSS-Scale-4 (RDBug 9156278; scale gradually) |
| "Autoscale not working / not honoring target on Spot (自动扩容不工作)" | `VMSS-Scale-Autoscale` | § VMSS-Scale-5 (Spot autoscale workaround), § VMSS-Spot-1 (Spot Known Issues) |
| "Scaling in / Manual+Autoscale toggle leaves stale IP (扩缩容后残留 IP)" | `VMSS-Scale-StaleIP` | § VMSS-Scale-6 (NRP race; VMSS update to re-sync) |
| "Standby Pools / pool degraded / scale-out not pulling from pool" | `VMSS-Scale-StandbyPool` | § VMSS-StandbyPool-1 |
| "Auto AZ Balance not rebalancing / `ZoneRebalancingNotEnabled` etc." | `VMSS-Scale-AutoAZ` | § VMSS-AutoAZ-1 |
| "Scale-out for AKS-managed VMSS not following scaling policy" | `VMSS-Scale-AKS` | § VMSS-Scale-AKS-1 (use AKS cluster autoscaler instead) |
| "Scale-out fails with `Network is unreachable` / Azure DevOps agent pool" | `VMSS-Scale-NetUnreach` | § VMSS-Scale-NetUnreach-1 (ADO IP allowlist) |
| "Cannot deploy / `OutOfTimeBudgetException` / `ThrottledException` (部署被限流)" | `VMSS-Throttle` | § VMSS-Throttle-1 (CRP throttling — global, no per-sub increase) |
| "Spot evictions left instances in `Stopped` state / multi-PG (多PG Spot 驱逐残留)" | `VMSS-Spot-MPG` | § VMSS-Spot-2 (KVS write conflict, by-design) |
| "VMSS in **Failed** state (`ProvisioningState/failed/<code>`)" | `VMSS-FailedState` | § VMSS-FailedState-1 (router; identify error code → dispatch to deep sub-§) |
| "VMSS shows **Health Degraded** in Activity Log / Resource Health" | `VMSS-HealthDegraded` | § VMSS-HealthDegraded-1 |
| "VMSS auto-repair shows `OrchestrationServiceNotInRunningState`" | `VMSS-AutoRepair-Paused` | § VMSS-OrchSvc-1 (resume orchestration service) |
| "Op took 7h+ / `VmssUDWalkTimeoutException` (Service Fabric only)" | `VMSS-UDWalk` | § VMSS-UDWalk-1 (SF MR durability mismatch or block) |
| "VMSS op takes > 30 min / long-running deployment (操作长时间挂起)" | `VMSS-LongRunningOp` | § VMSS-LongRunningOp-1 (ContextActivity + VmssVMGoalSeekingActivity gap analysis) |
| "`OperationNotAllowed` exceeds 100/300 instances → `Placement Group Errors`" | `VMSS-SPG` | § VMSS-SPG-1 (singlePlacementGroup flip irreversible) |
| "`MaxPerTenantCertificatesCountReached` / 199 cert limit" | `VMSS-MaxCerts` | § VMSS-MaxCerts-1 (FcShell + identify stale model certs) |
| "VMSS `RetryableError` referencing AppGw/LB/NIC in updating state" | `VMSS-Retryable` | § VMSS-Retryable-1 |
| "VMSS delete fails with `ApplicationGatewayErrorApplyingConfiguration`" | `VMSS-Delete-AppGw` | § VMSS-Delete-AppGw-1 (engage AzNet → EEE Cloudnet) |
| "VMSS delete fails with `ContainerAlreadyOnLease` / blob snapshot block" | `VMSS-Delete-Lease` | § VMSS-Delete-Lease-1 (Azure Forensics App ID `95cfa93e-...`) |
| "VMSS cannot delete / generic error" | `VMSS-CantDelete` | § VMSS-CantDelete-1 (force delete, network profile errors) |
| "VMSS cannot create / template validation failure" | `VMSS-CantCreate` | § VMSS-CantCreate-1 |
| "Rolling Upgrade aborted: `MaxUnhealthyUpgradedInstancePercentExceededInRollingUpgrade`" | `VMSS-RollingUpgrade` | § VMSS-Upgrade-1 |
| "Auto OS Upgrade not happening on Marketplace image" | `VMSS-AutoOSUpgrade` | § VMSS-Upgrade-2 (UniformAutoOSUpgrade — image=latest, MaxUnhealthy, rollout phase) |
| "Auto OS Upgrade enable fails with `Platform or Gallery image with version set to latest`" | `VMSS-AutoOSUpgrade-Latest` | § VMSS-Upgrade-3 (Latest Version AutoOSUpgrades) |
| "Manual upgrade fails with `PropertyChangeNotAllowed` (Marketplace VersionOnlyChange bug)" | `VMSS-PropertyChange` | § VMSS-Upgrade-4 (Bug 32803545; use Max Surge) |
| "OSPTO error during scale-out after image change" | `VMSS-OSPTO-ScaleOut` | § VMSS-OSPTO-1 |
| "CMG (SCCM Cloud Management Gateway) restart fails / DSC SAS token expired" | `VMSS-CMG` | § VMSS-CMG-1 (refresh SAS + switch from Rolling to Automatic) |
| "Cannot Update Scale Set workflow (cannot do ANY op on VMSS)" | `VMSS-CantUpdate-Workflow` | § VMSS-Workflow-2 |
| "Cannot Scale workflow (any scale op fails)" | `VMSS-Scale-Workflow` | § VMSS-Workflow-1 |
| "Cannot RDP/SSH VMSS Instances workflow" | `VMSS-CantRDPSSH-Workflow` | § VMSS-Workflow-3 |
| "Cannot RDP/SSH H-series VMSS / MTU / NMAgent error 0x803d0006" | `VMSS-CantRDPSSH-Hseries` | § VMSS-CantRDPSSH-1 |
| "VM Extension provisioning error / timeout / handler non-transient (any extension fail)" | `VMSS-Ext-Provision` | § VMSS-Ext-1 |
| "PUT extension fails: `OperationNotAllowedOnVMExtensionMarkedForDeletion`" | `VMSS-Ext-Deleting` | § VMSS-Ext-2 (upgrade instances to clear stuck delete) |
| "Linux VMSS multiple extensions installing concurrently / RPM lock error 95" | `VMSS-Ext-RPMLock` | § VMSS-Ext-3 (extension sequencing) |
| "VMSS Flex backend pool reference still present after LB/AppGw deletion (Ghost LB)" | `VMSS-Flex-GhostLB` | § VMSS-Flex-GhostLB-1 |
| "VMSS Flex deployed Instance Mix not balancing across SKUs" | `VMSS-Flex-InstanceMix` | § VMSS-Flex-InstanceMix-1 |
| "Spot Priority Mix grayed out in Portal / not seeing base VMs / wrong ratio" | `VMSS-Flex-SpotMix` | § VMSS-Flex-SpotMix-1 |
| "Azure Fleet (Compute Fleet) deploy issue" | `VMSS-Flex-Fleet` | § VMSS-Flex-Fleet-1 |
| "VMSS Flex AutoOSUpgrade enablement request" | `VMSS-Flex-AutoOSUpgrade` | § VMSS-Flex-AutoOSUpgrade-1 (Private Preview — CSAM only, NOT CSS scope) |
| "How does host caching work on VMSS Uniform vs Flex" | `VMSS-HowTo-HostCaching` | § VMSS-HowTo-HostCaching-1 |
| "How to enable Terminate Notifications / IMDS Scheduled Events on VMSS" | `VMSS-HowTo-TerminateNotif` | § VMSS-HowTo-TerminateNotif-1 |

### 2b. First-look platform health (the "is this CRP, VMSS, or platform?" gate)

For ANY VMSS case, before deep-diving, baseline the failure picture via VMSS-level CRP QoS:

```kusto
let resourceUri = "/subscriptions/{SubscriptionId}/resourceGroups/{ResourceGroupName}/providers/Microsoft.Compute/virtualMachineScaleSets/{VMSSName}";
let starttime = datetime({StartTime});
let endtime = datetime({EndTime});
let parts = split(resourceUri, "/");
let SubId = tostring(parts[2]);
let RG = tostring(parts[4]);
let Vmss = tostring(parts[8]);
cluster("azcrp").database("crp_allprod").ApiQosEvent_nonGet
| where PreciseTimeStamp between (starttime..endtime)
  and subscriptionId =~ SubId
  and resourceGroupName =~ RG
  and resourceName =~ Vmss
  and operationName has_any ("PATCH", "PUT", "POST", "DELETE")
| extend duration = format_timespan(e2EDurationInMilliseconds*1ms, 'mm:ss')
| project PreciseTimeStamp, operationName, duration, httpStatusCode, resultCode, errorDetails, correlationId, operationId
| order by PreciseTimeStamp asc
```

Reads the failure ladder (one of):
- `OperationNotAllowed/QuotaExceededWithPortalLink` → § VMSS-Alloc-1 (Quota branch) — engage ASMS
- `AllocationFailed/...` → § VMSS-Alloc-1 (Cluster/Zone/Sub-Pin branch)
- `AllocationFailed/SubnetIsFull` → § VMSS-Alloc-2
- `OperationNotAllowed/TooManyRequestsReceived` → § VMSS-Throttle-1
- `OperationNotAllowed` "exceeds the total limit of '40'" → § VMSS-Alloc-3
- `OperationNotAllowed` "exceeds the total limit of '300'" → § VMSS-SPG-1 (multi-AZ × SPG=true × 100)
- `BadRequest/ComputerNamePrefixTooLongForScaleOut` → § VMSS-Alloc-5
- `InboundNatPoolFrontendPortRangeSmallerThanRequestedPorts` → § VMSS-Alloc-NatPool-1 (cross-link to Update Natpool Config wiki)
- `NetworkingInternalOperationError` → cross-link to [Fabric Internal Server Error TSG](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495442) + collab Networking
- `VmssUDWalkTimeoutException` → § VMSS-UDWalk-1 (SF only)
- `RetryableError` → § VMSS-Retryable-1
- `OperationNotAllowed/QuotaExceededWithPortalLink` on Flex per-instance PUT but VMSS-level PATCH returns 200 → § VMSS-Flex-ScalingDiff-1 (Flex vs Uniform quota timing — capacity/instance mismatch)
- `OperationNotAllowedOnVMExtensionMarkedForDeletion` → § VMSS-Ext-2
- `PropertyChangeNotAllowed` → § VMSS-Upgrade-4
- `VMExtensionProvisioningError`/`Timeout`/`HandlerNonTransientError`/`DependencyError` → § VMSS-Ext-1 (then route to specific extension; for Linux RPM lock → § VMSS-Ext-3)
- `OSProvisioningTimedOut` → § VMSS-OSPTO-1 (also handoff to [`vm-log-analyzer`](../../../vm-log-analyzer/SKILL.md) for guest waagent/cloud-init)
- `MaxUnhealthyUpgradedInstancePercentExceededInRollingUpgrade` → § VMSS-Upgrade-1
- `ContainerAlreadyOnLease` → § VMSS-Delete-Lease-1
- `ApplicationGatewayErrorApplyingConfiguration` → § VMSS-Delete-AppGw-1

If KQL returns 0 rows but the customer insists there's a failure → either time window is wrong, OR they're using a derived resource (CMG VMSS / AKS managed VMSS / SF managed VMSS — those have ownership questions). Use [`_shared-vm-identification.md`](../_meta/_shared-vm-identification.md) to confirm.

---

## Step 3 — Drill per-instance (when needed)

Many VMSS issues need per-instance breakdown. Once you have the `{VMSSName}` + `{StartTime}` window:

### 3a. Per-instance error + provisioning state (Failed-state router)

```kusto
cluster('azcrpbifollower').database('bi_allprod').VMScaleSetVMInstanceAllocationInfo
| where TIMESTAMP between (datetime({StartTime}) .. 20d)
  and SubscriptionId == "{SubscriptionId}"
  and ResourceGroupName =~ "{ResourceGroupName}"
  and VMScaleSetName =~ "{VMSSName}"
| summarize min(TIMESTAMP) by InstanceIdString, State, ExtensionState, Error
| order by InstanceIdString, min_TIMESTAMP asc
```

Full deep recipe in § VMSS-FailedState-1.

### 3b. Per-instance goal-seeking activity (for stuck/long-running ops)

```kusto
cluster("Azcsupfollower2.centralus.kusto.windows.net").database("crp_allprod").VmssVMGoalSeekingActivity
| where PreciseTimeStamp > datetime({StartTime}) and PreciseTimeStamp < datetime({EndTime})
| where activityId == "{OperationId}"
| project PreciseTimeStamp, vMName, message
```

Look for guest-agent errors ("Failed to get most recent VM Agent status") OR specific extension messages — see deep § VMSS-LongRunningOp-1.

### 3c. Per-VMSS-VM op (for Flex; uses `VmssVMApiQosEvent`)

```kusto
let resourceUri = "{VMSSResourceId}";
cluster("azcrp.kusto.windows.net").database("crp_allprod").VmssVMApiQosEvent
| where PreciseTimeStamp between (datetime({StartTime}) .. 1d)
| where subscriptionId =~ split(resourceUri,"/")[2] 
  and resourceGroupName contains split(resourceUri,"/")[4] 
  and resourceName contains split(resourceUri,"/")[8]
| project PreciseTimeStamp, subscriptionId, resourceGroupName, resourceName, correlationId, operationId, operationName, resultCode, errorDetails
```

Used in § VMSS-Spot-2 (multi-PG eviction) and any Flex per-VM RCA.

---

## Step 4 — Verbose per-operation trace (ContextActivity)

When the verdict needs per-step "where did it hang / what message was emitted":

```kusto
cluster("Azcsupfollower2.centralus.kusto.windows.net").database("crp_allprod").ContextActivity
| where PreciseTimeStamp > datetime({StartTime}) and PreciseTimeStamp < datetime({EndTime})
| where activityId == "{OperationId}"
| project goalStateResourceId, PreciseTimeStamp, traceLevel, message, sourceFile, lineNumber, subscriptionId, activityId, Node
```

Filter by `message contains "extension"` for extension issues; `message contains "tenant"` for AzSM-tenant placement; `message contains "SkuSplit"` for Flex Instance Mix + Fleet interactions; `message contains "Connecting tenant update domain"` for SF UDWalk progress.

---

## Step 5 — Specialized RPs (Standby Pool / Auto AZ Balance / Fleet)

VMSS-related resources sometimes live in **separate RPs**, not under the parent VMSS:

| Feature | RP | Where the data is |
|---|---|---|
| **Standby Pool** | `Microsoft.StandbyPool` → `standbyVirtualMachinePools` | KQL: `cluster("azurecm.kusto.windows.net").database("AzureCM").PMaaSPoolRPPoolOverviewSnapshot` + `PMaaSVMPoolOverviewSnapshot` + `PMaaSPoolManagerPoolInDegradedStateMetric` (see § VMSS-StandbyPool-1) |
| **Auto AZ Balance** | activity log only — actions emit to `cluster("azmc2.centralus.kusto.windows.net").database("rsm_prod").ArmActivityLogEvent` + ineligibility reasons in `AutomaticRebalancingV2ContextEvent` (see § VMSS-AutoAZ-1) |
| **Azure Compute Fleet** | `Microsoft.AzureFleet` → KQL on `cluster("azfleet.southcentralus.kusto.windows.net").database("fleet_prod")` (see § VMSS-Flex-Fleet-1) — requires CoreIdentity `ComputeFleet-Kusto` group |
| **Auto OS Upgrade rollout phase** | `cluster("azmc2.centralus.kusto.windows.net").database("rsm_prod").VmssStateEvent` (see § VMSS-Upgrade-2) |
| **Autoscale trigger details** | `cluster('azureinsights.kusto.windows.net').database('Insights').JobTraces` + `ScaleAction` (see § VMSS-Workflow-1) |

---

## Step 6 — Ownership handoffs

| Trigger | Engage |
|---|---|
| VMSS in **AKS** managed cluster — scaling policy ignored, autoscaler issue | **AKS team** (collab). Check clientApplicationId in ASC Tenant Explorer to confirm cluster name. § VMSS-Scale-AKS-1 |
| VMSS is **Service Fabric** managed — durability/MR/UDWalk timeout | **SF team** drives. Collab SAP: `Azure/Service Fabric/Issues related to the Cluster/My problem is related to cluster upgrade`. § VMSS-Alloc-1 + § VMSS-UDWalk-1 |
| VMSS is **Azure DevOps Pipelines** scale set agent — scaling not happening | **Azure DevOps Services** team. § VMSS-Workflow-1 |
| Resource Lock / certs in **Key Vault** | Customer-side; show how to remove specific stale certs via PowerShell § VMSS-MaxCerts-1 |
| Quota exceeded | **ASMS** (Subscription Management). SAP: `Azure/Service and subscription limits (quotas)/Compute-VM (cores-vCPUs) subscription limit increases` |
| **Application Gateway / LB / NIC / VNet** errors during VMSS op | **Azure Networking** collab. § VMSS-Delete-AppGw-1 / § VMSS-Retryable-1 / § VMSS-CantDelete-1 |
| **Subscription pinning** allocation error (`ComputeAllocationFailureWithSubscriptionPinning`) | **WACAP** via [ICM template N3o3z1](https://portal.microsofticm.com/imp/v3/incidents/create?tmpl=N3o3z1) |
| **Azure Forensics** retains many blob snapshots blocking delete | `AzForensics@microsoft.com` |
| **Cloud Management Gateway** (SCCM/MECM) Rolling Upgrade outage | **SC ConfigMgr** team. Collab SAP: `Management Tools/Configuration Manager/Microsoft Configuration Manager (current branch)/Cloud Services/Cloud Management Gateway (CMG)`. § VMSS-CMG-1 |
| **Application Insights / Azure Monitor Autoscale** triggers misfiring | **Application Insights** team. SAP: `Azure/Autoscale/Scale actions didn't perform as expected/Autoscale didn't scale as expected` |
| Sev 3 generic VMO/Fleet escalation | [ICM template l1Y1E3](https://portal.microsofticm.com/imp/v3/incidents/create?tmpl=l1Y1E3) — Azure RT |
| Sev 2 generic VMSS escalation | [VCPE engagement](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/2113626) |

---

## Step 7 — Write the customer reply

VMSS RCA templates favor concrete fact statements + a fix recipe. The deep file holds **verbatim wording** for the cases that ship public-RCA blurbs (Spot eviction multi-PG, Flex vs Uniform scaling differences, throttling). For everything else, follow the standard FQR/LQR/RCA shape (drafted manually, keep internal identifiers out):

- **Issue summary** — one line: "VMSS X failed to scale out at T because Y".
- **Investigation** — name the table you queried + the verdict row.
- **Root cause** — choose one: Quota, Capacity (cluster/zone/sub-pin), Subnet, SPG, Image, Extension, Throttle, KVS conflict (Spot MPG), Customer config (SF MR mismatch / Rolling Upgrade default), Platform bug (cross-ref ICM).
- **Resolution** — paste the CLI/PS one-liner OR the workflow step (e.g., "Stop all instances → resize → start" for cluster-pinning escapes).
- **Prevention** — set expectations on SPG irreversibility, AutoOSUpgrade rollout phase, Spot eviction policy, throttling being global.

For "Strike / close case" wording on Spot-eviction-multi-PG and Flex-vs-Uniform scaling differences, copy the deep file's `Customer-Facing wording` blocks verbatim — they're legally vetted.

---

## Cross-link contract

This playbook cross-links to:

- [`playbook-A-restarts-deep.md`](playbook-A-restarts-deep.md) — when a VMSS instance is reported as having **rebooted** during a scale/upgrade window (router → A).
- [`playbook-B-cant-start-stop-deep.md`](playbook-B-cant-start-stop-deep.md) — generic `AllocationFailed` / `OperationNotAllowed` not specific to VMSS shape (router → B § OP-Allocation, OP-OSPTO, OP-Delete, OP-Throttle, OP-Lock, OP-Policy).
- [`playbook-C-performance-deep.md`](playbook-C-performance-deep.md) — VMSS instance perceived as **slow** during scale-out or upgrade (router → C § STG-Perf-* / § NET-Perf-*).
- [`playbook-D-maintenance-deep.md`](playbook-D-maintenance-deep.md) — VMSS instance affected by **planned maintenance / LM** in the same window (router → D § PM-3 (List Affected VMSS PowerShell) / § PM-15 / § LM-Common).
- [`crp-queries.md`](../catalogs/crp-queries.md) — generic CRP `ApiQosEvent` / `ContextActivity` patterns.
- [`networking-queries.md`](../catalogs/networking-queries.md) — NRP `QosEtwEvent` for stale-IP and ghost-LB scenarios.
- [`storage-account-queries.md`](../catalogs/storage-account-queries.md) — when ghost backend pool / blob-lease scenarios need XStore-side confirmation.
- [`asap-storage-queries.md`](../catalogs/asap-storage-queries.md) — only via Playbook C dispatch (VMSS instances on Boost-NVMe SKUs).
- [`_shared-vm-identification.md`](../_meta/_shared-vm-identification.md) — universal VM↔Node mapping.
- [`vm-log-analyzer`](../../../vm-log-analyzer/SKILL.md) skill — for OSPTO root cause (waagent / cloud-init / sysprep state.ini) + extension log analysis.
- Final FQR/LQR/RCA composition — drafted manually (keep internal identifiers out).
