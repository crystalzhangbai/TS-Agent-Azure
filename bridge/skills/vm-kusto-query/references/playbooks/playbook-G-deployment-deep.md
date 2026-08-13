# Playbook G — Deployment (Deep)

> **Companion to** [`playbook-G-deployment-core.md`](./playbook-G-deployment-core.md). Core file is the routing entry point; this file holds full KQL bodies, customer-facing wording, and per-error workarounds. **All anchors are `DEPLOY-*`** — pasteable directly from the core router. Foundation queries live in `references/crp-queries.md`, `references/operations-queries.md`, `references/vm-properties-queries.md`.

> **Scope boundary** vs Playbook B (Can't Start-Stop): Playbook G owns **deployment-time / create-time** failures (resource did NOT exist before this op). Playbook B owns **runtime** CRP errors on already-existing resources (`OperationNotAllowed` on start/stop/restart/delete/redeploy, OSPTO on already-created VMs, etc.). When in doubt: if `IsNew:True` in labels → H. If acting on existing → B.

## Cluster shortcuts

```kusto
let crp         = cluster('azcrp.kusto.windows.net').database('crp_allprod');
let crp_follow  = cluster('Azcsupfollower2.centralus.kusto.windows.net').database('crp_allprod');
let crp_bi      = cluster('azcrpbifollower.kusto.windows.net').database('bi_allprod');
let armprodgbl  = cluster('armprodgbl.eastus.kusto.windows.net').database('ARMProd');
let armprodeus  = cluster('armprodeus.eastus.kusto.windows.net').database('Requests');
let armprodweu  = cluster('armprodweu.westeurope.kusto.windows.net').database('Requests');
let armprodsea  = cluster('armprodsea.southeastasia.kusto.windows.net').database('Requests');
let azcm        = cluster('AzureCM.kusto.windows.net').database('AzureCM');
let azcm_follow = cluster('Azcsupfollower').database('AzureCM');
let azcore      = cluster('azcore.centralus.kusto.windows.net').database('Fa');
let aznwsdn     = cluster('aznwsdn.kusto.windows.net').database('aznwmds');
let casprod     = cluster('azcrpeus.kusto.windows.net').database('casprod');
let allocator   = cluster('azureallocator.westcentralus.kusto.windows.net').database('AzureAllocator');
let azmarket    = cluster('Azmarket').database('StoreApi');
```

---

## Anchor Index

### CRP throttle / preemption / restart
- [`DEPLOY-CRP-Preempted`](#deploy-crp-preempted--crp-operation-preempted-concurrent-ops) — CRP Operation Preempted (concurrent ops)
- [`DEPLOY-CRP-Restarted`](#deploy-crp-restarted--crp-service-restart-vmredeploymentfailed--taskcanceledexception) — CRP Service Restart (VMRedeploymentFailed)
- [`DEPLOY-CRP-RBT`](#deploy-crp-rbt--crp-resource-based-throttling-rbt) — CRP Resource Based Throttling
- [`DEPLOY-CRP-Throttle`](#deploy-crp-throttle--crp-throttling-context-activity-internal-limits) — CRP Throttling Context Activity
- [`DEPLOY-CRP-SubThrottle`](#deploy-crp-subthrottle--subscriptionrequeststhrottled-arm-side) — SubscriptionRequestsThrottled (ARM-side)

### CA/PA mapping (post-deploy network blip)
- [`DEPLOY-CAPA-Delay`](#deploy-capa-delay--capa-mapping-delay-network-blip-post-create) — CA/PA Mapping Delay
- [`DEPLOY-CAPA-Incorrect`](#deploy-capa-incorrect--capa-mapping-incorrect-wrong-pa-mapped) — CA/PA Mapping Incorrect

### Allocation + SKU at deploy
- [`DEPLOY-Alloc-SkuNotAvailable`](#deploy-alloc-skunotavailable--skunotavailable-notavailableforsubscription-availabilityzonenotsupported) — SkuNotAvailable / NotAvailableForSubscription / AvailabilityZoneNotSupported
- [`DEPLOY-Alloc-InvalidVMSize`](#deploy-alloc-invalidvmsize--zero-width-space-in-vmsize-parameter) — Failed to Deploy VM InvalidVMSize (zero-width space)
- [`DEPLOY-Alloc-AnyZone`](#deploy-alloc-anyzone--zoneplacementpolicy-any-overconstrained) — Failed to Create VM with AnyZone
- [`DEPLOY-Alloc-LocNotFound`](#deploy-alloc-locnotfound--locationnotfoundforrolesize-rdfe) — LocationNotFoundForRoleSize (RDFE)
- [`DEPLOY-Alloc-LongDeploy`](#deploy-alloc-longdeploy--long-deployment-eg-analysis) — Long Deployment

### PPG
- [`DEPLOY-PPG-NotFound`](#deploy-ppg-notfound--ppg-cannot-be-found-region-mismatch) — PPG Cannot be Found (region mismatch)
- [`DEPLOY-PPG-Overconstrained`](#deploy-ppg-overconstrained--ppg-overconstrainedallocationrequest-t2-spine-pinned) — PPG OverconstrainedAllocationRequest

### Capacity Reservation (ODCR)
- [`DEPLOY-CR-CUD`](#deploy-cr-cud--capacity-reservation-create-update-delete) — Capacity Reservation Create / Update / Delete (full RCA)

### Gen2 / Trusted Launch / Confidential / Hibernation
- [`DEPLOY-Gen2-CannotBoot`](#deploy-gen2-cannotboot--cannot-boot-hypervisor-generation-2) — Cannot Boot Hypervisor Generation 2
- [`DEPLOY-Gen2-GreyedOut`](#deploy-gen2-greyedout--gen2-vm-option-greyed-out-custom-vhd) — Gen2 VM Option Greyed Out (custom VHD)
- [`DEPLOY-Gen2-UnmanagedVM`](#deploy-gen2-unmanagedvm--hypervisorgeneration2notallowedforunmanagedvm) — HypervisorGeneration2NotAllowedForUnmanagedVM
- [`DEPLOY-Gen2-Identify`](#deploy-gen2-identify--identify-gen2-vm-multi-source-detection) — Identify Gen2 VM
- [`DEPLOY-Conf-DCasv5`](#deploy-conf-dcasv5--confidential-vms-dcasv5--ecasv5-security-profile) — Confidential VMs (DCasv5 / ECasv5) security profile
- [`DEPLOY-Conf-OEPlatform`](#deploy-conf-oeplatform--confidential-computing-oe-platform-error-sgx-driver) — Confidential Computing OE Platform Error
- [`DEPLOY-Hibernate-Fails`](#deploy-hibernate-fails--creating-vm-with-hibernation-enabled-fails) — Creating VM with Hibernation Enabled Fails

### Image / Marketplace / Publisher
- [`DEPLOY-Image-PlatformNotFound`](#deploy-image-platformnotfound--platformimagenotfound-3-step-pircas-chain) — PlatformImageNotFound (EA-only image with non-EA sub)
- [`DEPLOY-Image-BlobNotFound`](#deploy-image-blobnotfound--imageblobnotfound-resourcenotfound) — ImageBlobNotFound / ResourceNotFound (managed)
- [`DEPLOY-Image-NotFound`](#deploy-image-notfound--imagenotfound-portal-deploy) — ImageNotFound (portal)
- [`DEPLOY-Image-IncorrectBlobType`](#deploy-image-incorrectblobtype--incorrectimageblobtype-block-vs-page-blob) — IncorrectImageBlobType (block vs page)
- [`DEPLOY-Image-Publisher`](#deploy-image-publisher--publisher-image-issues-3rd-party) — Publisher Image Issues (3rd-party)
- [`DEPLOY-Image-SIG`](#deploy-image-sig--create-vm-from-sig-image-fails) — Create VM from SIG Image Fails
- [`DEPLOY-Image-SIGCrossTenant`](#deploy-image-sigcrosstenant--failed-deploy-of-sig-image-across-tenants) — SIG Image Across Tenants
- [`DEPLOY-Image-VMSSACG`](#deploy-image-vmssacg--create-vmss-from-acg-image-fails-os-state-and-image-type-change) — Create VMSS from ACG Image Fails (OS state, image type)
- [`DEPLOY-Marketplace-PurchaseErrors`](#deploy-marketplace-purchaseerrors--marketplace-purchase-validation-errors) — Marketplace Purchase Errors
- [`DEPLOY-Marketplace-Eligibility`](#deploy-marketplace-eligibility--marketplacepurchaseeligibilityfailed-9-symptoms) — MarketplacePurchaseEligibilityFailed (9 symptoms)

### ACG (Azure Compute Gallery)
- [`DEPLOY-ACG-Gallery`](#deploy-acg-gallery--cannot-create-shared-image-gallery) — Cannot Create Shared Image Gallery
- [`DEPLOY-ACG-Definition`](#deploy-acg-definition--cannot-create-shared-image-definition) — Cannot Create Shared Image Definition
- [`DEPLOY-ACG-Version`](#deploy-acg-version--cannot-create-shared-image-version-replication--timeout--size-limits) — Cannot Create Shared Image Version (replication / timeout / size)
- [`DEPLOY-ACG-Quota`](#deploy-acg-quota--increasing-acg-quota-limits) — Increasing ACG Quota Limits

### AIB (Azure Image Builder)
- [`DEPLOY-AIB-ConnectionError`](#deploy-aib-connectionerror--nsg-blocking-winrmssh-on-existing-vnet) — ConnectionError (NSG blocks WinRM/SSH)
- [`DEPLOY-AIB-NoCustomizer`](#deploy-aib-nocustomizer--azure-policy-blocking-aib-staging-resources) — NoCustomizerScript (Azure Policy)
- [`DEPLOY-AIB-CIS`](#deploy-aib-cis--build-failures-with-cis-hardened-images) — Build Failures with CIS Hardened Images

### Container + Disk at deploy
- [`DEPLOY-Container-PoolNotFound`](#deploy-container-poolnotfound--preprovisioneddiskpoolnotfound-non-fatal) — PreprovisionedDiskPoolNotFound (non-fatal, ignore)
- [`DEPLOY-Container-LargeResource`](#deploy-container-largeresource--container-creation-fails-during-large-resource-vhd-prep) — Container Creation Fails During Large Resource VHD Prep (G5 series 6.5 TB resource disk)
- [`DEPLOY-Disk-BlobInUse`](#deploy-disk-blobinuse--diskblobalreadyinusebyanotherdisk) — DiskBlobAlreadyInUseByAnotherDisk
- [`DEPLOY-Disk-BlobPendingCopy`](#deploy-disk-blobpendingcopy--diskblobpendingcopyoperation) — DiskBlobPendingCopyOperation
- [`DEPLOY-Disk-TargetBlobExists`](#deploy-disk-targetblobexists--targetdiskblobalreadyexists-blob-already-attached) — TargetDiskBlobAlreadyExists (target VHD already attached)

### Storage account at deploy
- [`DEPLOY-SA-LocationMismatch`](#deploy-sa-locationmismatch--storageaccountlocationmismatch) — StorageAccountLocationMismatch
- [`DEPLOY-SA-TypeNotSupported`](#deploy-sa-typenotsupported--blob-storage-rejected-for-boot-diag) — Storage Account Type Not Supported

### Quota + region + policy
- [`DEPLOY-Quota-Deployment`](#deploy-quota-deployment--deploymentquotaexceeded-800rg) — Deployment Quota Exceeded (800/RG)
- [`DEPLOY-Quota-vCPU`](#deploy-quota-vcpu--quotaexceeded-vcpu) — Quota Exceeded (vCPU/regional)
- [`DEPLOY-Region-NotRegistered`](#deploy-region-notregistered--cannot-deploy-in-new-region) — Cannot Deploy in New Region
- [`DEPLOY-Reg-Missing`](#deploy-reg-missing--missingsubscriptionregistration) — MissingSubscriptionRegistration
- [`DEPLOY-Policy-Denied`](#deploy-policy-denied--requestdisallowedbypolicy) — RequestDisallowedByPolicy

### Provisioning / OSPTO at deploy
- [`DEPLOY-Provision-OSPTO`](#deploy-provision-ospto--osprovisioningtimedout-deploy-time) — OSProvisioningTimedOut (deploy-time)
- [`DEPLOY-Provision-CloudInit`](#deploy-provision-cloudinit--cloud-init-failures-linux-ospto-subset) — Cloud Init Failures (Linux OSPTO subset)
- [`DEPLOY-Sysprep-Failed`](#deploy-sysprep-failed--sysprep-failed-or-stuck-generalizationstate-mitigation) — Sysprep Failed or Stuck (GeneralizationState mitigation)
- [`DEPLOY-Image-OSProfile`](#deploy-image-osprofile--cannot-set-osprofile-on-existing-osdisk-createoption-attach-vs-fromimage) — Cannot set OSProfile on existing OSDisk (CreateOption=Attach vs FromImage)

### Update / state
- [`DEPLOY-Update-VMRedeploymentFailed`](#deploy-update-vmredeploymentfailed--vmredeploymentfailed-customer-facing) — VMRedeploymentFailed (customer-facing, cross-link CRP-Restarted)
- [`DEPLOY-Update-VMStuckInUpdating`](#deploy-update-vmstuckinupdating--vm-stuck-in-updating-nsg--manifest) — VM Stuck in Updating (NSG / manifest download)

---

## DEPLOY-CRP-Preempted — CRP Operation Preempted (concurrent ops)

**Scope**: Concurrent CRP ops on the same resource. The newer op preempts the older one. **NOT a failure** — safeguard mechanism to maintain a single goal state. If `operationId != goalSeekingActivityId`, the op is preempted.

### 3 Scenarios

1. **No changes** (impatient user starts VM twice): work continues under new operationId; no impact
2. **Later op cancels previous**: e.g., PUT/START followed by DELETE → DELETE wins; previous ends with `OperationPreempted: The operation has been preempted by a more recent operation`
3. **Previous merges into latest** (most-common customer complaint): operation appears slow because it shows in-progress until ALL preempted goals are met. Customer says "start took 10 min" but VM actually started in 30s — only delayed because CSE installed by a sibling op took 10 min

### Q1 — Identify preempted ops (operationId vs goalSeekingActivityId)

```kusto
let subId = '{SubscriptionId}';
let RGName = '{ResourceGroupName}';
let ResourceName = '{ResourceName}';
let starttime = datetime({StartTime});
let endtime = 5d;
cluster('Azcsupfollower2.centralus.kusto.windows.net').database('crp_allprod').ApiQosEvent_nonGet
| where PreciseTimeStamp between (starttime .. endtime)
    and operationName !contains "FabricCallback"
    and operationName !contains "AsyncOperation"
    and subscriptionId == subId
    and resourceGroupName == RGName
    and resourceName == ResourceName
| extend StartTime = PreciseTimeStamp - e2EDurationInMilliseconds*1ms, EndTime = PreciseTimeStamp
| extend IsPreempted = iff(isnotempty(goalSeekingActivityId) and operationId != goalSeekingActivityId, true, false)
| project StartTime, EndTime, Duration=e2EDurationInMilliseconds*1ms, IsPreempted, operationId, goalSeekingActivityId,
          operationName, resourceGroupName, resourceName, httpStatusCode, resultCode, errorDetails,
          region, userAgent, clientApplicationId, clientPrincipalName, correlationId
```

### Q2 — Full context across all preempting ops in a chain

```kusto
let starttime = datetime({StartTime});
let endtime = 5d;
cluster('Azcsupfollower2.centralus.kusto.windows.net').database('crp_allprod').ContextActivity
| where PreciseTimeStamp between (starttime .. endtime)
    and activityId in (
        'opId1',  // all operationIds sharing the same goalSeekingActivityId
        'opId2',
        'opId3'
    )
| project PreciseTimeStamp, activityId, message, sourceFile
```

### Customer-facing RCA (verbatim — for long-running ops complaint)

> Thank you for reaching out to Microsoft Azure Support. We have completed the analysis of the delayed <OperationName> operations of the VMSS/VM <Resource name> that occurred on <Datetime>.
> Azure is a multi-provider product where different resource providers collaborate with each other to complete an operation. Due to its complexity, additional measures are taken to make sure resource integrity is maintained when there are concurrent operations against a resource. One of these measures is called preemption. Preemption will merge all concurrent operations against a resource to maintain a single goal state. **It does not cause the operation to fail, but it can delay the operation complete time.**
> To check if the resource is functioning, we recommend checking the OS or application state directly using PSPing, health probe, Application Health Extension for VM or VMSS, or other methods, instead of relying on the operation result. We apologize for any inconvenience this may cause you.

### Mitigation
- Don't double-click portal buttons / don't fire same API multiple times
- Use psping / health probe / app health to check actual resource state instead of operation result
- CRP QoS `UserAgent` column tells you what triggered the duplicate op (Portal / PS / CLI / specific app)

---

## DEPLOY-CRP-Restarted — CRP Service Restart (VMRedeploymentFailed / TaskCanceledException)

**Scope**: Customer op (typically Redeploy) fails mid-flight because CRP service restarted. Expected — restarts happen regularly during the day.

**Customer symptoms**: `VMRedeploymentFailed` or `TaskCanceledException`.

### Q1 — Context Activity for the failed operationId

```kusto
cluster('Azcsupfollower2.centralus.kusto.windows.net').database('crp_allprod').ContextActivity
| where PreciseTimeStamp > datetime({StartTime}) and PreciseTimeStamp < datetime({EndTime})
| where activityId == "{OperationId}"
| project PreciseTimeStamp, traceLevel, message, sourceFile, lineNumber, subscriptionId, activityId, Node
```

**Confirming signatures** (look for ALL of these):
- `Processing stopped. Exception: System.Threading.Tasks.TaskCanceledException: A task was canceled.`
- `Restarting operation after service restart. Original start time: <T>. Times restarted: 1`
- `Declaring the RedeployVMOperation failed. We don't know when this operation was issued and don't want to cause an unexpected redeploy.`

Also: the `Node` column should CHANGE during the restart (e.g., `CRP_TY11.2` → `CRP_TY11.27`) — confirms a different CRP node picked up the retry.

### Mitigation
After CRP restart, it doesn't know if the redeploy completed and refuses to redo it (to avoid unexpected reboot). Customer clears the Failed state by:

```powershell
# Either trigger an empty Update (safest):
$vm = Get-AzVM -ResourceGroupName 'rg' -Name 'vmname'
Update-AzVM -ResourceGroupName 'rg' -VM $vm
# OR add/remove an empty data disk
```

---

## DEPLOY-CRP-RBT — CRP Resource Based Throttling (RBT)

**Scope**: VM / VMSS being moved from Subscription-Based Throttling (SBT) → Resource-Based Throttling (RBT). RBT = per-resource quota + sub max, all on 1-min window. Token bucket algorithm.

**RBT policy names** end in `Resource` or `SubscriptionMaximum` — that's how you tell RBT errors apart from SBT.

### Policies (key subset)

| Tier | Policy | Per-resource | Sub max |
|---|---|---|---|
| VM | Low Cost Get | 6/VM/min | 10000/min |
| VM | PutVMSSResource | 4/VM/min | 500/min |
| VM | UpdateVMSSResource | 4/VM/min | 500/min |
| VM | DeleteVMSSResource | 4/VM/min | 500/min |
| VMSS | Low Cost Get | 12/VMSS/min | 1000/min |
| VMSS | High Cost Get | 10/VMSS/min | 500/min |
| VMSS | PutVMSSResource | 2/VMSS/min | 125/min |
| VMSS | UpdateVMSSResource | 2/VMSS/min | 500/min |
| VMSS | DeleteVMSSResource | 2/VMSS/min | 175/min |
| VMSS VM | GetVMScaleSetVMResource | 6/VMSSVM/min | 2000/min |
| VMSS VM | VMScaleSetVMActionsResource | 2/VMSSVM/min | 500/min |
| VMSS VM | DeleteVMScaleSetVMResource | 2/VMSSVM/min | 500/min |

### Q1 — Check which regions have RBT enabled

```kusto
cluster('azcrp.kusto.windows.net').database('crp_allprod').DynamicConfigServiceSnapshot
| where PreciseTimeStamp > ago(6h)
| where settingName contains "EnableResourceBasedThrottlingInNonAuditMode"
| where MonitoringApplication !="USSTG"
| distinct MonitoringApplication, wFAppName
| order by wFAppName asc
| summarize make_list(wFAppName) by MonitoringApplication
```

### Q2 — Verify if sub opted out to SBT (AFEC flag)

```kusto
cluster('azcrpbifollower').database('bi_allprod').Subscription
| where PreciseTimeStamp > ago(1h)
| where SubscriptionId == "{SubscriptionId}"
| where Region == "{Region}"
| extend EnabledForceSubscriptionBasedThrottling = RegisteredFeatures has "Microsoft.Compute/ForceSubscriptionBasedThrottling"
| project PreciseTimeStamp, Region, SubscriptionId, EnabledForceSubscriptionBasedThrottling
```

### Q3 — Which RBT policies are throttling the sub

```kusto
cluster('azcrp.kusto.windows.net').database('crp_allprod').ApiQosEvent
| where PreciseTimeStamp between (datetime({StartTime}) .. 1d)
| where MonitoringApplication == "CRP-{Region}_Monitoring"
| where subscriptionId == "{SubscriptionId}"
| where httpStatusCode == 429
| where resultCode == "OperationNotAllowed/TooManyRequestsReceived"
| extend throttledPolicyName = tostring(parse_json(errorDetails).details[0].target)
| summarize count() by throttledPolicyName
```

### Disable RBT (revert to SBT — only if confirmed regression)

```powershell
Register-AzProviderFeature -FeatureName "ForceSubscriptionBasedThrottling" -ProviderNamespace "Microsoft.Compute"
```

### Mitigation logic
1. Consistent call pattern + throttling increased → disable RBT + escalate to PG
2. Increased call pattern → customer must reduce; allowed limit shown in error details

---

## DEPLOY-CRP-Throttle — CRP Throttling Context Activity (internal limits)

> **⚠ INTERNAL ONLY**: CRP throttle limits are NOT publicly published. Share with customers only with TA approval on case-by-case basis.

**Error variants**:
- `Operation 'Microsoft.Compute/virtualMachines/read' failed as server encountered too many requests. Please try after '120' seconds.`
- `Request throttled. Policies violated: VMScaleSetBatchedVMRequests5Min;...`
- `ResourceCollectionRequestsThrottled`
- `OperationNotAllowed / TooManyRequestsReceived` HTTP 429
- Error JSON: `operationGroup`, `startTime`, `endTime`, `allowedRequestCount`, `measuredRequestCount`

### Q1 — Trace by correlationId in ARM

```kusto
let corid = "{CorrelationId}";
cluster('armprodgbl.eastus.kusto.windows.net').database('ARMProd')
| macro-expand isfuzzy=true ARMProdEG as X (
    X.database('Requests').HttpIncomingRequests
    | where correlationId == corid
    | where PreciseTimeStamp > datetime({StartTime}) and PreciseTimeStamp < datetime({EndTime})
    | where httpStatusCode == "429"
)
```

### Q2 — Find exact throttle type in CRP

```kusto
cluster('azcrp.kusto.windows.net').database('crp_allprod').ApiQosEvent
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where subscriptionId == "{SubscriptionId}"
| where correlationId contains "{CorrelationId}"
| where httpStatusCode == "429"
| project PreciseTimeStamp, Node, subscriptionId, operationId, clientRequestId, correlationId, operationName, httpStatusCode, errorDetails
```

### Alternative: Jarvis Diagnostics
- URL: https://jarvis-west.dc.ad.msft.net/7307A353
- Endpoint: Diagnostics PROD, Namespace: CRP, Event: ThrottlingContextActivity, filter: message contains SubID

### Mitigation
Limits are global, not per-subscription. Customer must reduce/spread API calls. Throttling Error Analyzer: https://docs.microsoft.com/en-us/azure/virtual-machines/troubleshooting/troubleshooting-throttling-errors#api-call-rate-and-throttling-error-analyzer

### RCA coding

| Scenario | Coding |
|---|---|
| Single-VM blocked | `Windows Azure\Virtual Machines\VM Deployment, Start, Stop, Resize, Delete failures\Azure Platform\ARM throttling` |
| Customer advisory | `Windows Azure\Virtual Machines\Administration\HowTo: Customer exceeded Reads/Writes triggering throttling` |
| VMSS create | `\VM Scale Sets\Deployment Issues\Throttling limits` |
| VMSS upgrade | `\VM Scale Sets\Reimage/Upgrade\Throttling` |
| VMSS scale-out | `\VM Scale Sets\Scale-out Issues\Throttling limits` |
| VMSS scale-in | `\VM Scale Sets\Scale-In Issues\Throttling limits` |

---

## DEPLOY-CRP-SubThrottle — SubscriptionRequestsThrottled (ARM-side)

**Scope**: ARM-side throttle (separate from CRP). Limits per sub:

| Type | Default = Max |
|---|---|
| ARM API Reads | 12000/hour |
| ARM API Writes | 1200/hour |

**Determining ARM vs RP**: `failureCause == "gateway"` → ARM; blank or `"service"` → RP.

### Q1 — Outgoing requests by status code

```kusto
cluster('armprodgbl.eastus.kusto.windows.net').database('ARMProd')
| macro-expand isfuzzy=true ARMProdEG as X (
    X.database('Requests').HttpOutgoingRequests
    | where subscriptionId == "{SubscriptionId}"
    | where (TIMESTAMP > datetime({StartTime}) and TIMESTAMP < datetime({EndTime}))
    | summarize count() by httpStatusCode, httpMethod, failureCause
    | order by count_
)
```

### Q2 — Which RP/host is throttling

```kusto
let subid = "{SubscriptionId}";
cluster('armprodgbl.eastus.kusto.windows.net').database('ARMProd')
| macro-expand isfuzzy=true ARMProdEG as X (
    X.database('Requests').HttpOutgoingRequests
    | where TIMESTAMP >= now(-5d)
    | where subscriptionId == subid
    | where httpStatusCode == 429
    | summarize count() by hostName
    | order by count_ desc
)
```

### Q3 — Which operation type throttled

```kusto
let subid = "{SubscriptionId}";
cluster('armprodgbl.eastus.kusto.windows.net').database('ARMProd')
| macro-expand isfuzzy=true ARMProdEG as X (
    X.database('Requests').HttpIncomingRequests
    | where TIMESTAMP >= now(-5d)
    | where subscriptionId == subid
    | where httpStatusCode == 429
    | summarize count() by bin(TIMESTAMP, 1d), operationName
    | order by count_ desc
)
```

### Q4 — Single client vs many clients

```kusto
let subid = "{SubscriptionId}";
let opname = "POST/SUBSCRIPTIONS/RESOURCEGROUPS/PROVIDERS/MICROSOFT.STORAGE/STORAGEACCOUNTS/LISTSERVICESAS";
cluster('armprodgbl.eastus.kusto.windows.net').database('ARMProd')
| macro-expand isfuzzy=true ARMProdEG as X (
    X.database('Requests').HttpIncomingRequests
    | where TIMESTAMP >= now(-5d)
    | where subscriptionId == subid
    | where httpStatusCode != -1
    | where operationName == opname
    | summarize count() by clientIpAddress, principalOid, clientApplicationId, userAgent, httpStatusCode
    | order by count_ desc
)
```

### Q5 — Incoming requests by status code (complement to Q1)

```kusto
cluster('armprodgbl.eastus.kusto.windows.net').database('ARMProd')
| macro-expand isfuzzy=true ARMProdEG as X (
    X.database('Requests').HttpIncomingRequests
    | where subscriptionId == "{SubscriptionId}"
    | where (TIMESTAMP > datetime({StartTime}) and TIMESTAMP < datetime({EndTime}))
    | summarize count() by httpStatusCode, httpMethod, failureCause
    | order by count_
)
```

### Q6 — Total requests/hour timechart

```kusto
cluster('armprodgbl.eastus.kusto.windows.net').database('ARMProd')
| macro-expand isfuzzy=true ARMProdEG as X (
    X.database('Requests').HttpIncomingRequests
    | where PreciseTimeStamp > datetime({StartTime}) and PreciseTimeStamp < datetime({EndTime})
    | where subscriptionId == "{SubscriptionId}"
    | summarize count() by bin(PreciseTimeStamp, 1h)
    | render timechart
)
```

### Mitigation
Customer must reduce client request rate. No per-sub bump without PG approval.

---

## DEPLOY-CAPA-Delay — CA/PA Mapping Delay (network blip post-create)

**Scope**: VM created OK but suffers post-create network blip / connectivity issues / long-running deploy. Root cause: CA/PA (Customer Address ↔ Physical Address) mapping took > 10 min from VM create time. Affects CloudInit / Custom Script Extension that depend on network during provisioning.

Short link: https://aka.ms/CAPAMappingDelay

### Q1 — Compute CAPAMappingDuration (cross-cluster join)

```kusto
let subId = '{SubscriptionId}';
let RGName = '{ResourceGroupName}';
let ResourceName = '{VmName}';
let VMCreateTime =
    toscalar(cluster('azcsupfollower2.centralus').database('crp_allprod').ApiQosEvent_nonGet
    | where subscriptionId =~ subId
        and resourceGroupName =~ RGName
        and resourceName =~ ResourceName
        and operationName has "ResourceOperation.PUT"
        and labels has '"IsNew": "True"'
    | top 1 by PreciseTimeStamp desc
    | project PreciseTimeStamp);
let VMHostInfo = (
    cluster('azcrpbifollower').database('bi_allprod').VM
    | where SubscriptionId =~ subId and ResourceGroupName =~ RGName and VMName =~ ResourceName
    | top 1 by TIMESTAMP desc
    | project VMId
    | join kind=inner (
        cluster('azcsupfollower').database('AzureCM').LogContainerSnapshot
        | where PreciseTimeStamp between ((VMCreateTime-5m) .. 1h)
            and subscriptionId =~ subId and roleInstanceName has ResourceName
        | top 1 by TIMESTAMP desc
        | project containerId, virtualMachineUniqueId) on $left.VMId == $right.virtualMachineUniqueId
    );
let VNETInfo = (cluster('aznwsdn.kusto.windows.net').database('aznwmds').InterfaceProgramEndFiveMinuteTable
    | where FirstTimeStamp between ((VMCreateTime-5m) .. 30m)
        and ContainerId == toscalar((VMHostInfo | project containerId))
        and Detail == "SUCCESS"
    | top 1 by FirstTimeStamp desc
    | extend IPAddress = tostring(split(CustomerAddress, "/")[0])
    | distinct VnetGuid, IPAddress, NodeIP, MACAddress
    | join kind=leftouter (
        cluster('aznwsdn.kusto.windows.net').database('aznwmds').InterfaceAliasProgrammedFiveMinuteTable
        | where FirstTimeStamp between ((VMCreateTime-5m) .. 30m)
            and ContainerId == toscalar((VMHostInfo | project containerId))
        | parse Detail with * "{VA_HLIP_" IPAddress:string "=" *
        | where isnotempty(IPAddress)
        | distinct NodeId, ContainerId, VnetGuid, IPAddress, MACAddress
    ) on VnetGuid, MACAddress
    | extend IPAddress = coalesce(IPAddress, IPAddress1)
    | distinct VnetGuid, IPAddress, NodeIP, MACAddress
    | parse VnetGuid with "{" VnetGuid "}"
    );
cluster('azcsupfollower').database('AzureCM').DCMLNMPubSubTaskEventEtwTable
| where PreciseTimeStamp between ((VMCreateTime-5m) .. 1d)
    and VnetId =~ toscalar((VNETInfo | project VnetGuid))
    and CustomerAddress =~ toscalar((VNETInfo | project IPAddress))
    and TaskStatus == "UpdateTaskAdded"
| top 1 by PreciseTimeStamp asc
| project CAPAMappingPublishedTime = PreciseTimeStamp, VMCreateTime
| extend CAPAMappingDuration = (CAPAMappingPublishedTime - VMCreateTime)
```

If `CAPAMappingDuration` < 10 min → TSG NOT relevant.

### Mitigation
- Customer redeploys or restarts the VM
- If still failing → IcM **Cloudnet\Network Manager**. Example: 339178967

---

## DEPLOY-CAPA-Incorrect — CA/PA Mapping Incorrect (wrong PA mapped)

**Scope**: Wrong PA mapped to CA (not just delayed) → ongoing network issues post-create / start / resize / redeploy.

Short link: https://aka.ms/CAPAMappingIncorrect

### Q1 — Detect wrong CA/PA mapping

```kusto
let monitorDurationInMinutes = 10;
let startTime = datetime({StartTime});
let nodeId = "{NodeId}";
let containerId = "{ContainerId}";
let endTime = datetime_add('minute', monitorDurationInMinutes, startTime);
let failurePercentageThreshold = 90;
cluster('aznwsdn').database("aznwmds").AggVmHealthFailureVscStateEventTable
| where healthEventTime between (startTime..endTime)
| where OwnDsMappingsStatus != 1 and PortProgrammingStatus == 1
| where VmId !contains "_pps-" and VmId !contains "_Empty" and VmId !contains "Deployment_" and VmId !contains "_eas"
| where NodeId == nodeId and ContainerId == containerId
| summarize mappingSyncVoilationCount = count() by Cluster, NodeId, ContainerId, VmId, NmAgentBuildInfo, MacAddress
| extend FailurePercentage = round(100 * toreal(mappingSyncVoilationCount) / monitorDurationInMinutes, 2)
| extend IsWrongCAPAMapping = iff(FailurePercentage >= failurePercentageThreshold, "Yes", "No")
```

If `IsWrongCAPAMapping == "No"` OR `FailurePercentage < 90` → TSG NOT relevant.

**Logic**: NMAgent checks CA/PA every 1 min. In X minutes we expect X records for a wrong mapping. Threshold 90% allows for timestamp filter slack.

### Mitigation
- Customer redeploys VM
- If still failing → IcM **Cloudnet\Network Manager**
- Related WI: [16544979 (Ga S2)](https://msazure.visualstudio.com/One/_workitems/edit/16544979)

---

## DEPLOY-Alloc-SkuNotAvailable — SkuNotAvailable / NotAvailableForSubscription / AvailabilityZoneNotSupported

Short: https://aka.ms/CCSupSkuNotAvailable

### Errors
- `SkuNotAvailable: The requested size for resource ... is currently not available in location '<>' zones '' for subscription '<>'. Please try another size or deploy to a different location or zones. See https://aka.ms/azureskunotavailable for details.`
- `NotAvailableForSubscription`
- `AvailabilityZoneNotSupported: The zone(s) '2' for resource '<>' is not supported. The supported zones for location 'eastus' are '3,1'.`
- ODCR variant: `Following SKUs have failed for Capacity Restrictions: Standard_M416ms_v2`

### Causes
1. SKU not whitelisted for sub in this location/zone
2. SKU not allowed for ODCR (On-Demand Capacity Reservation)

### Q1 — Check ODCR blocklist for the sub

```kusto
cluster("azcrpeus.kusto.windows.net").database("casprod").CasAdminOfferRestrictionsBlockList
| where LocationName contains "{Region}"
| where SubscriptionId == "{SubscriptionId}"
| project Timestamp, OfferFamily, EnforcementType, OfferTerm, PhysicalAvailabilityZone, IsZonalRestriction, OfferRestrictionType
```

### Validation tools
1. **Compute Capacity Advisory (CCA)** in ASC (any VM → CCA tab) — near-real-time SKU availability
2. ASC → Resource Explorer → Subscription → RP Details → SKU Restrictions (Regional vs Zone)
3. ACIS backup: `GetResourceProviderSkusForSubscription` endpoint

### Mitigation
- **Cause 1 (sub not whitelisted)**: Transfer to CCE (Capacity Customer Experience) via SAP `Azure/Service and subscription limits (quotas)/Compute-VM (cores-vCPUs) subscription limit increases - Azure Subscription limit/quota support ({Language}) - Non CSS`. Info needed: SubID + Region + SKU + Restriction Type (Regional/Zone) + # cores
- **Cause 2 (ODCR)**: ICM **WACAP** team via ASC template **M2N2J3**

---

## DEPLOY-Alloc-InvalidVMSize — Zero-width space in vmSize parameter

**Error**: `InvalidParameter / InvalidVMSize` HTTP 400 — "The value `Standard_D2als_v6​` provided for the VM size is not valid" even though the size IS listed in the error's valid-sizes list.

**Root cause**: Invisible zero-width space (U+200b) at tail of `vmSize` string in `requestEntity`. Copy/paste through a text editor exposes it.

### Q1 — Find the failed PUT

```kusto
cluster('azcrp.kusto.windows.net').database('crp_allprod').ApiQosEvent_nonGet
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where subscriptionId =~ "{SubscriptionId}"
| where errorDetails has "provided for the VM size is not valid"
| project PreciseTimeStamp, operationId, operationName, httpStatusCode, resultCode, requestEntity, errorDetails
| sort by PreciseTimeStamp asc
```

### Mitigation
Remove the zero-width space. Re-type the value rather than copy-pasting.

---

## DEPLOY-Alloc-AnyZone — zonePlacementPolicy=Any overconstrained

**Scope**: VM created with `placement.zonePlacementPolicy = "Any"` + restrictive `includeZones`/`excludeZones` → `OverconstrainedZonalAllocationRequest`.

### Q1 — Zone placement handler trace

```kusto
cluster('azcrp.kusto.windows.net').database('crp_allprod').ContextActivity
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where MonitoringApplication == "CRP-{Region}_Monitoring"
| where subscriptionId == "{SubscriptionId}"
| where activityId == "{OperationId}"
| where sourceFile contains "ColocationAllocatorZonePlacementHandler.cs" or message contains "zone placement"
| project PreciseTimeStamp, goalStateResourceId, traceLevel, message, callerName, lineNumber, sourceFile, Node, Pid, Tid
```

Shows `preselectedAvailabilityZones` filtering: includeZones/excludeZones, disk's zone, publicIP zone, storage supported zones. Last log shows which zone was selected (or none).

### Mitigation
Loosen excludeZones, broaden includeZones, or pick a SKU available in more zones.

---

## DEPLOY-Alloc-LocNotFound — LocationNotFoundForRoleSize (RDFE)

**Error**: `LocationNotFoundForRoleSize: The requested VM tier is currently not available in <region> for this subscription. Please try another tier or deploy to a different location.`

Short: https://aka.ms/ClientFailure-LocationNotFoundForRoleSize

### Investigation
- EG RCA shows: `[MCIO-CAS] Deployment was blocked by CapacityManager PerformCapacityCheck`
- DGrep Jarvis https://jarvis-west.dc.ad.msft.net/79879332 → Aggregates: Count by Level → filter Level 3 (Warning)

### Root cause
RDFE deployment blocked by CapacityManager — sub not enabled for VM tier in region.

### Mitigation
Same path as [DEPLOY-Alloc-SkuNotAvailable](#deploy-alloc-skunotavailable--skunotavailable-notavailableforsubscription-availabilityzonenotsupported) — CCE transfer.

---

## DEPLOY-Alloc-LongDeploy — Long Deployment (EG analysis)

**Scope**: Deployment > 10 min and ≤ 40 min (platform-flagged threshold). No SLA on deployment times.

### Approach (no KQL — use Execution Graph)
1. Get `operationId` from CRP QoS
2. Open EG: `http://aka.ms/egv?id={OperationId}`
3. Identify which component lost the most time:
   - **Extension provisioning** → drill into specific extension execution
   - **Container workflow blocked** → expand HA Command, Container, Node info
4. Cross-link to Playbook B § OP-OSPTO if provisioning hung; Playbook D if PM/LM in window

---

## DEPLOY-PPG-NotFound — PPG Cannot be Found (region mismatch)

**Error**: `NotFound: Proximity Placement Group '/subs/<>/.../proximityPlacementGroups/<>' cannot be found.`

**Cause**: VM and PPG in DIFFERENT regions.

**Mitigation**: All PPG resources must be in same region as PPG. Move VM target or recreate PPG.

---

## DEPLOY-PPG-Overconstrained — PPG OverconstrainedAllocationRequest (T2 spine pinned)

**Error**: `OverconstrainedAllocationRequest: Allocation failed. VM(s) with the following constraints cannot be allocated... Constraints applied are: VM Size, Proximity Placement Group`

**Cause**: SKU not available in the T2 Spine the PPG is currently pinned to. Example: customer deployed 4× `Standard_D1_v2` first → PPG pinned to T2 spine without `ND6s_v3` capacity → ND6s_v3 add-on fails.

### Resolution
1. **Deallocate ALL VMs in the PPG**
2. **Allocate the most specialized/exotic SKU FIRST** — forces PPG repinning to a T2 spine that supports it
3. Then allocate common SKUs

---

## DEPLOY-CR-CUD — Capacity Reservation Create / Update / Delete

**Scope**: On-Demand Capacity Reservation (ODCR) end-to-end RCA for failed create / update / delete.

### Scenario 1: Create reservation fails (AllocationFailed)

#### Q1 — PUT op detail

```kusto
cluster("azcrp").database("crp_allprod").ApiQosEvent_nonGet
| where PreciseTimeStamp between (datetime({startTime}) .. now())
| where subscriptionId == "{subscriptionId}"
| where operationName contains "CapacityReservations.CapacityReservationOperation"
| where operationName !in ("AsyncOperationCompletionOperation","VirtualMachines.RetrieveBootDiagnosticsData.POST","VirtualMachines.RetrieveVMConsoleSerialLogs.POST", "VirtualMachines.RetrieveVMConsoleScreenshot.POST", "VirtualMachines.WriteSerialConsoleConnectionMetadata.POST", "VirtualMachines.ConfigurePatching.POST") and operationName !startswith "Restore"
| extend startTime=PreciseTimeStamp-e2EDurationInMilliseconds*1ms
| extend totalSeconds = e2EDurationInMilliseconds / 1000
| extend duration = strcat(totalSeconds/60, "m ", totalSeconds%60, "s")
| project startTime, PreciseTimeStamp, subscriptionId, resourceGroupName, resourceName, region, correlationId,
          operationName, operationId, goalSeekingActivityId, duration, clientApplicationId, userAgent,
          httpStatusCode, labels, requestEntity, resultCode, errorDetails
| sort by PreciseTimeStamp asc
```

Look for `AllocationFailed/CapacityReservationAllocationFailure` + `requestEntity` shows SKU + region + reserved count.

#### Q2 — Verify reservation by Name (returns CapacityReservationId)

```kusto
cluster("azcrpbifollower.kusto.windows.net").database("bi_allprod").CapacityReservation
| where PreciseTimeStamp between (datetime({startTime}) .. now())
| where SubscriptionId == "{SubscriptionId}"
| where Name == "{Name}"
| project PreciseTimeStamp, CapacityReservationGroupName, CapacityReservationId, ReservedCount, Region,
          ResourceGroupName, Name, PhysicalAvailabilityZone, SkuName
| sort by PreciseTimeStamp desc
```

Take the **latest timestamp** (other rows are 30-min periodic snapshots). Empty `PhysicalAvailabilityZone` = regional reservation; otherwise = physical zone.

#### Q3 — Identify VMs in reservation (used / unused)

```kusto
cluster("azureallocator.westcentralus.kusto.windows.net").database("AzureAllocator").AllocatorReservationServiceUsageSnapshot
| where PreciseTimeStamp between (datetime({startTime}) .. now())
| where reservationId == "{ReservationId}"
| summarize arg_max(PreciseTimeStamp, *) by reservedContainerCount, usedVMIds, unUsedVMIds
| project PreciseTimeStamp, reservationId, reservationType, reservedContainerCount, unUsedVMIds, usedVMIds, vmSize
| sort by PreciseTimeStamp desc
```

#### Scenario 1 mitigation
1. ASC → any VM in sub → **Compute Capacity Advisory** tab → confirm SKU + qty available in target region/zone
2. CCA shows available → ask customer to retry
3. If persists → Deployment SME or Stop_Start SME via Ava, OR ICM **WACAP/Incident Manager** via ASC

### Scenario 2: Update reservation fails

Same Q1 + Q2 to identify ReservedCount (prior to update) and reservation name. ASC → CapacityReservations → Resource Change History → Lookback (max 14 days) shows the change. Or use Q2 directly (further back than 14 days).

**Mitigation**: Same as Scenario 1. To get reservation out of Failed state when capacity unavailable → customer must **revert ReservedCount to its original value**.

### Scenario 3: Delete reservation fails (CapacityReservationCannotBeDeleted)

**Error**: `OperationNotAllowed/CapacityReservationCannotBeDeleted: Capacity Reservation '<>' cannot be deleted. Before deleting a capacity reservation please ensure that it is not referenced by any VM or VMSS VM.`

#### Q4 — Find failed CRP DELETE

```kusto
cluster("azcrp").database("crp_allprod").ApiQosEvent_nonGet
| where PreciseTimeStamp between (datetime({startTime}) .. now())
| where SubscriptionId == "{SubscriptionId}"
| where operationName contains "CapacityReservations.CapacityReservationOperation.DELETE"
| where operationName !in ("AsyncOperationCompletionOperation","VirtualMachines.RetrieveBootDiagnosticsData.POST","VirtualMachines.RetrieveVMConsoleSerialLogs.POST", "VirtualMachines.RetrieveVMConsoleScreenshot.POST", "VirtualMachines.WriteSerialConsoleConnectionMetadata.POST", "VirtualMachines.ConfigurePatching.POST") and operationName !startswith "Restore"
| project PreciseTimeStamp, subscriptionId, resourceGroupName, resourceName, region, correlationId, operationName,
          operationId, goalSeekingActivityId, clientApplicationId, userAgent, httpStatusCode, labels,
          requestEntity, resultCode, errorDetails
| sort by PreciseTimeStamp asc
```

#### Q5 — Get VM details from usedVMIds → containerId / nodeId

```kusto
cluster("AzureCM").database("AzureCM").LogContainerSnapshot
| where PreciseTimeStamp between (datetime({startTime}) .. now())
| where subscriptionId == "{subscriptionId}"
| where virtualMachineUniqueId == "{VMId}"
| summarize min(PreciseTimeStamp), max(PreciseTimeStamp) by roleInstanceName, creationTime,
          virtualMachineUniqueId, Tenant, containerId, nodeId, tenantName, containerType,
          updateDomain, availabilitySetName, subscriptionId, AvailabilityZone, DataCenterName
| project vmname=roleInstanceName, containerType, virtualMachineUniqueId, Cluster=Tenant, NodeId=nodeId,
          ContainerCreationTime=todatetime(creationTime), ContainerId=containerId,
          StartTimeStamp=min_PreciseTimeStamp, EndTimeStamp=max_PreciseTimeStamp,
          tenantName, updateDomain, availabilitySetName, AvailabilityZone, DataCenterName
| order by ContainerCreationTime asc
```

#### Scenario 3 mitigation
Share VM details with customer so they can disassociate from reservation. Doc: https://learn.microsoft.com/en-us/azure/virtual-machines/capacity-reservation-remove-vm

### Known issue: Subscription pinning + ODCR incompatibility
Subs with pinning should not be allowed to use ODCR, but `CapacityReservationGroup` creation is not blocked → VM PATCH fails when both exist. Bug [37369664](https://msazure.visualstudio.com/One/_workitems/edit/37369664).

---

## DEPLOY-Gen2-CannotBoot — Cannot Boot Hypervisor Generation 2

**Cause**: Gen2 image + VM size that doesn't support Gen2 (Gen2 requires premium-storage-capable SKU subset).

**Mitigation**: Pick a Gen2-supported SKU. Ref: https://docs.microsoft.com/en-us/azure/virtual-machines/windows/sizes-general

---

## DEPLOY-Gen2-GreyedOut — Gen2 VM Option Greyed Out (custom VHD)

**Symptom**: Customer created Gen2 VM in Hyper-V → converted VHDX to VHD → uploaded as page blob → created managed disk → Gen2 option greyed out in portal (stuck on Gen1).

**Cause**: HyperV Generation property NOT set on the managed disk during import.

### Resolution

```powershell
$sourceUri = 'https://xyzstorage.blob.core.windows.net/vhd/abcd.vhd'
$osDiskName = 'gen2Disk'
$diskconfig = New-AzDiskConfig -Location 'East US 2 EUAP' -DiskSizeGB 127 `
    -AccountType Standard_LRS -OsType Windows -HyperVGeneration "V2" `
    -SourceUri $sourceUri -CreateOption 'Import'
New-AzDisk -DiskName $osDiskName -ResourceGroupName 'Gen2VMTest' -Disk $diskconfig
```

`-HyperVGeneration "V2"` is the critical flag.

Doc: https://docs.microsoft.com/en-us/azure/virtual-machines/windows/generation-2#managed-image-or-managed-disk

---

## DEPLOY-Gen2-UnmanagedVM — HypervisorGeneration2NotAllowedForUnmanagedVM

**Error**: `BadRequest / HypervisorGeneration2NotAllowedForUnmanagedVM: Generation 2 Hypervisor Image and VM Size can only be used with managed-disk VMs.`

**Cause**: Historic platform bug (Workitem 16325050) — CRP failed to validate HyperV Generation on PUT/Update for existing Gen2 VM from custom image, even when `labels.HasManagedDisk=True`. Fix rolled out late 2019.

### Q1 — Verify VM is managed-disk

```kusto
cluster('azcrp.kusto.windows.net').database('crp_allprod').ApiQosEvent_nonGet
| where subscriptionId == "{SubscriptionId}"
| where resourceName == "{VMName}"
| where labels has '"HasManagedDisk"'
| project PreciseTimeStamp, labels, errorDetails, resultCode
```

Parent ICM: 130988811.

---

## DEPLOY-Gen2-Identify — Identify Gen2 VM (multi-source detection)

### Detection methods (in-guest, ASC, Kusto)
1. **Guest log**: `C:\Windows\Panther\setupact.log` — search `Callback_BootEnvironmentDetect` → `EFI` (Gen2) or `BIOS` (Gen1)
2. **ASC** VM Property tab → HyperV Generation Type
3. **Disk Management** UEFI partition
4. **Windows** `msinfo32.exe` → BIOS Mode = UEFI (Gen2) vs Legacy (Gen1)
5. **Registry** `Computer\HKEY_LOCAL_MACHINE\HARDWARE\DESCRIPTION\System\BIOS\BIOSVersion` contains "UEFI" = Gen2

### Q1 — Single VM in Kusto

```kusto
let StartDate = datetime({StartTime});
let EndDate = datetime({EndTime});
let subscription = "{SubscriptionId}";
let vm = "{VMName}";
cluster('Azcsupfollower').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= StartDate and PreciseTimeStamp <= EndDate
| where subscriptionId contains subscription and roleInstanceName contains vm
| project PreciseTimeStamp, creationTime, roleInstanceName, additionalContainerProperties,
          containerId, nodeId, tenantName
| summarize arg_max(PreciseTimeStamp, *) by containerId
| extend tempvariable = parse_json(additionalContainerProperties)
| extend IsGen2VM = tempvariable.IsGen2VM
| project PreciseTimeStamp, VMCreated=creationTime, IsGen2VM, roleInstanceName, containerId, nodeId, tenantName
```

### Q2 — All Gen2 VMs in subscription (sweep)
Same as Q1, drop the `roleInstanceName contains vm` filter.

### Q3 — Clusters in a region supporting Gen2

```kusto
let region = "{Region}";
cluster('Azcsupfollower').database('AzureCM').TMMgmtFabricSettingEtwTable
| where PreciseTimeStamp >= ago(1h)
| where Name contains "gen2vm"
| where Value contains "true"
| where Region contains region
| summarize by Value, Tenant, LastModifiedTime, Region
```

### Q4 — Is Gen2 available on a specific cluster

```kusto
let clus = "{ClusterName}";
cluster('Azcsupfollower').database('AzureCM').TMMgmtFabricSettingEtwTable
| where PreciseTimeStamp >= ago(1h)
| where Name contains "gen2vm"
| where Tenant contains clus
| summarize by Tenant, Gen2Availability=Value, LastModifiedTime
```

---

## DEPLOY-Conf-DCasv5 — Confidential VMs (DCasv5 / ECasv5) security profile

**Scope**: AMD SEV-SNP confidential VMs. Strict `securityProfile` requirements.

**Symptom**: `VM '<VMName>' did not start in the allotted time. The VM may still start successfully. Please check the power state later. Reapplying the virtual machine may resolve the issue.`

**Root cause**: `securityProfile.securityType` set to `TrustedLaunch` instead of `ConfidentialVM`. Nested Confidential VM doesn't support virtual Trusted Launch.

### Mitigation
**Recreate** the VM (reapply/restart/stop-start will NOT fix). Use one of:
- `securityType = ConfidentialVM` + `uefiSettings.secureBootEnabled=true` + `vTpmEnabled=true`
- Empty `securityProfile: { }` (or omit entirely)

### Required configs
- VM size: confidential VM family (DCasv5/ECasv5 etc.)
- OS image: qualified-list only
- securityType: `VMGuestStateOnly` (VMGS-only) or `DiskWithVMGuestState` (full OS disk pre-encryption — longer provisioning)

Docs: https://learn.microsoft.com/en-us/azure/confidential-computing/virtual-machine-solutions-amd

---

## DEPLOY-Conf-OEPlatform — Confidential Computing OE Platform Error (SGX driver)

**Symptom**: DC2/DC4 VM, openenclave samples fail with `OE_PLATFORM_ERROR on oe_create_enclave()`.

**Cause**: Kernel changed (upgrade/downgrade/update) since SGX DCAP driver install.

### Mitigation

```bash
wget https://download.01.org/intel-sgx/dcap-1.0/sgx_linux_x64_driver_dcap_36594a7.bin -O sgx_linux_x64_driver.bin
chmod +x sgx_linux_x64_driver.bin
sudo ./sgx_linux_x64_driver.bin
```

If still failing → escalate to **ACC team** (template: `SME-Topics/Deployment/Azure-Virtual-Machine-ACC-Escalation-Template`).

**RCA coding**: `Root Cause - Windows Azure\Virtual Machine\Third Party Issues/Questions`

---

## DEPLOY-Hibernate-Fails — Creating VM with Hibernation Enabled Fails

**Scope**: VM PUT with `additionalCapabilities.hibernationEnabled = true` fails with BadRequest/Conflict at control plane, OR succeeds at control plane but extension fails in guest.

### Control-plane error codes (all customer errors — DO NOT escalate to PG)

| Error code | Meaning |
|---|---|
| UnsupportedHibernationOSDiskNotSupportedForVMWithHibernationCapability | OS disk lacks HibernationSupported capability |
| UnsupportedHibernationPlatformImageNotSupportedForVMWithHibernationCapability | Platform image lacks hibernation support |
| UnsupportedHibernationSharedImageGalleryImageNotSupportedForVMWithHibernationCapability | SIG image lacks hibernation support |
| HibernationCapabilityNotSupportedForSpotVMs | Spot VMs not supported |
| UserVMImageNotSupportedForVMWithHibernationCapability | User VM image not supported |
| DedicatedHostNotSupportedForVMWithHibernationCapability | ADH not supported |
| CapacityReservationNotSupportedForVMWithHibernationCapability | ODCR not supported |
| UpdatingHibernationCapabilityOnlyAllowedOnDeallocatedVMs | Must deallocate first |
| HibernationCannotBeEnabled_InsufficientDiskSpace | OS disk size must > VM memory |
| HibernationNotSupportedForAvSetVMs | Only standalone + VMSS Flex; not AvSet |

### Windows VMs — AzureHibernateExtension (auto-installed by CRP)

#### Q1 — Extension logs from AzCore

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').GuestAgentExtensionEvents
| where VMId == "{VMId}"
| where Name == "Microsoft.CPlat.Core.WindowsHibernateExtension"
| where PreciseTimeStamp between (datetime({StartTime}) .. 1d)
```

In-guest logs: `C:\WindowsAzure\Logs\Plugins\Microsoft.CPlat.Core.WindowsHibernateExtension\<version>`

#### Windows routing table

| Failure message | Owner |
|---|---|
| `Page file is in temp disk. Please move it to OS disk` | Customer issue. Marketplace images auto-move; custom images don't |
| `Enabling hibernate failed. Response from the powercfg command: ...` | WSD CFE / HCCompute-Guest OS Health ([Core OS TSG](https://eng.ms/docs/cloud-ai-platform/azure-edge-platform-aep/aep-platform/core-os/rdos/livesite/tsg/virtualization/hyperv-guest-hibernate)) |
| Any other (non-powercfg) | AzureRT / Extensions (potential bug) |

#### Validate after fix
`powercfg /a` should show Hibernate available. Reapply VM API if extension still in Failed state.

### Linux VMs — LinuxHibernateExtension (NOT auto-installed)

Customer must add extension OR install `hibernation-setup-tool` package from packages.microsoft.com.

#### Q2 — Linux extension logs

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').GuestAgentExtensionEvents
| where VMId == "{VMId}"
| where Name == "Microsoft.CPlat.Core.LinuxHibernateExtension"
| where PreciseTimeStamp between (datetime({StartTime}) .. 3d)
```

#### In-guest validation
- `systemctl status hibernation-setup-tool` should show `Inactive (dead)` + `Swap file for VM hibernation set up successfully`
- Or `journalctl -b -u hibernation-setup-tool.service`

#### Linux routing
- `Hibernation not allowed for this VM. Please enable Hibernation during VM creation` → Customer
- `Hibernation not recommended for a machine with more than 256GB of RAM` → Customer
- `System ran out of disk space while allocating hibernation file` → Customer

---

## DEPLOY-Image-PlatformNotFound — PlatformImageNotFound (3-step PirCas chain)

**Error**: `PlatformImageNotFound: The platform image '<>' is not available. Verify that all fields in the storage profile are correct.` OR `InvalidParameter / imageReference: The following list of images referenced from the deployment template are not found: Publisher:.., Offer:.., Sku:.., Version: latest.`

Short: https://aka.ms/CCSupPlatformImageNotFound

**Cause**: Not all marketplace images available for all subscription types. Most common: BYOL / SQL images require EA subscription, customer trying with MSDN/VSDev.

### Q1 — Find PlatformImageNotFound in ApiQosEvent (note operationId)

```kusto
cluster('Azcsupfollower2.centralus.kusto.windows.net').database('crp_allprod').ApiQosEvent
| where PreciseTimeStamp > datetime({StartTime})
| where PreciseTimeStamp < datetime({EndTime})
| where subscriptionId == '{SubscriptionId}'
| where operationName !contains 'Get'
| project PreciseTimeStamp, operationId, correlationId, operationName, resultCode, errorDetails,
          requestEntity, subscriptionId, resourceGroupName, resourceName, userAgent, region, RPTenant
```

### Q2 — Query PirCasApiQosEvent using operationId as correlationId

```kusto
cluster('Azcsupfollower2.centralus.kusto.windows.net').database('crp_allprod').PirCasApiQosEvent
| where PreciseTimeStamp > datetime({StartTime})
| where PreciseTimeStamp < datetime({EndTime})
| where subscriptionId == '{SubscriptionId}'
| where correlationId == '{OperationIdFromQ1}'
| project PreciseTimeStamp, subscriptionId, operationId, correlationId, operationName, httpStatusCode,
          resultCode, exceptionType, errorDetails, publisher, offer, sku, ['version']
```

Find the `VMImagesConsumption.ListVMImagesVersionsFromLocation.GET` row — note its `operationId`.

### Q3 — PirCasContextActivityEvent for the SubID quota header

```kusto
cluster('Azcsupfollower2.centralus.kusto.windows.net').database('crp_allprod').PirCasContextActivityEvent
| where PreciseTimeStamp > datetime({StartTime})
| where PreciseTimeStamp < datetime({EndTime})
| where activityId == '{OperationIdFromQ2}'
| project PreciseTimeStamp, subscriptionId, activityId, traceLevel, message, callerName
```

**Look for**: `Request Headers: [x-ms-subscription-quota-ids: MSDNDevTest_2014-09-01 ...]` AND `Request message contains x-ms-subscription-quota-ids header but does not contain EA quotas. Block access to EA images since caller is not authorized`.

### Mitigation
1. Use EA subscription, OR
2. Pick non-EA-restricted image: `az vm image list` / https://docs.microsoft.com/en-us/azure/virtual-machines/windows/cli-ps-findimage

VMSS variant: same TSG applies.

---

## DEPLOY-Image-BlobNotFound — ImageBlobNotFound / ResourceNotFound

### Error (unmanaged)
`ImageBlobNotFound: Unable to find VHD blob with URI https://<>/vhds/<>.vhd for disk '<>'`

### Error (managed)
`ResourceNotFound: Resource 'Microsoft.Compute/images/<name>' under Resource Group '<>' was not found`

### Investigation
EG: `http://aka.ms/egv?id={OperationId}` — shows ResultCode/ResultDetails with Custom Image URI customer referenced.

### Mitigation
- **Unmanaged**: customer verifies URI exists in storage account. If image doesn't exist: revisit sysprep + capture/generalize steps; image may be in different SA/container
- **Managed**: Portal → Images blade → confirm Resource ID + RG in deployment matches actual image

---

## DEPLOY-Image-NotFound — ImageNotFound (portal deploy)

**Error**: Portal: "Image not found"; Jarvis ContextActivity: `Operation=ReflectedHttpActionDescriptor.ExecuteAsync, Status=404 (NotFound)`

**Cause**: Image removed from marketplace OR ineligible subscription type (BYOL image visible to EA customer in portal but actually deploying with non-EA sub).

### Investigation
- Check image still in Azure Marketplace
- `az vm image list` to verify platform availability
- Confirm subscription type vs image eligibility

### Mitigation
Cross-link to [DEPLOY-Image-Publisher](#deploy-image-publisher--publisher-image-issues-3rd-party). Customer to use eligible sub or alternate image.

---

## DEPLOY-Image-IncorrectBlobType — IncorrectImageBlobType (block vs page blob)

**Error**: `IncorrectImageBlobType: Disk blobs can only be of type page blob. Blob https://<>/<>.vhd for disk 'VM_boot' is of type block blob.`

**Cause**: VHD uploaded as block blob (default when copying via File Storage cmdlets). VHDs MUST be page blob.

**Mitigation**: AzCopy with `/BlobType:page`:

```
azcopy copy <source> <dest> --blob-type=PageBlob
```

EG: `http://aka.ms/egv?id={OperationId}` shows IncorrectImageBlobType with blob URI.

---

## DEPLOY-Image-Publisher — Publisher Image Issues (3rd-party)

Short: https://aka.ms/CCSupPublisher

### Precondition: rule out Azure platform first
This TSG only applies after ruling out: image-missing-from-region, image-missing-from-marketplace, specific-version-unavailable, non-Azure (ARM/CRP/PIR/Fabric) issues, default-extension failures.

### Q1 — Success / failure rate per image SKU

```kusto
let s = ago(30d);
let e = now();
cluster("Azcsupfollower2.centralus.kusto.windows.net").database("crp_allprod").VMApiQosEvent
| where PreciseTimeStamp between (s..e)
| where operationName == "VirtualMachines.ResourceOperation.PUT" or operationName contains "VirtualMachineScaleSets.ResourceOperation.PUT"
| where platformImage contains "{ImageSubstring}"   // e.g., "sql2019-ws2019"
| project PreciseTimeStamp, galleryImage, platformImage, userVMImage, resultCode, vMSize,
          operationId, errorDetails, exceptionType, resultType
| summarize success = count(isempty(resultCode)), failure = count(isnotempty(resultCode)) by platformImage
| extend successRate = round((todouble(success)/todouble(success + failure))*100, 2)
| sort by successRate asc nulls last
```

### Q2 — Simpler variant

```kusto
let s = ago(30d);
let e = now();
cluster("Azcsupfollower2.centralus.kusto.windows.net").database("crp_allprod").VMApiQosEvent
| where PreciseTimeStamp between (s..e)
| where operationName == "VirtualMachines.ResourceOperation.PUT"
| where platformImage contains "{ImageSubstring}"
| project PreciseTimeStamp, platformImage, resultCode
| summarize success = countif(isempty(resultCode)), failure = countif(isnotempty(resultCode)) by platformImage
| extend successRate = round((todouble(success)/todouble(success + failure))*100, 2)
| sort by successRate asc nulls last
```

### Publisher contact process (internal — DO NOT share contacts with customer)
1. Get Publisher/Offer/SKU/Version from customer
2. https://storemanagement.microsoft.com/ — search offer → get Publisher ID (Seller ID)
3. https://partner.microsoft.com/en-us/dashboard/Account/WorkOnBehalfOf — paste Seller ID → Marketplace offers → offer listing → Engineering contact

### Escalation
- **Collab to ASMS** first via SAP `Subscription management\Purchase, sign up or upgrade issues\Unable to make a purchase`
- ASMS triages → may IcM Marketplace team
- ❌ Do NOT IcM EEE AzureRT or VCPE (out of scope)
- Partner-opened SRs → Partner Portal team via SAP `Partner Center/Offer Certification/Certification/Azure Virtual Machine offer`

### 3rd party SAPs
`Azure/Virtual Machine running <OS>/Cannot create a VM/Troubleshoot custom image deployment failures`

---

## DEPLOY-Image-SIG — Create VM from SIG Image Fails

### Required imageReference format
`/subscriptions/<SUBID>/resourceGroups/<RG>/providers/Microsoft.Compute/galleries/<GALLERY>/images/<DEF>/versions/<VERSION>`

`SUBID` must be the subscription where SIG was created (NOT where VM is being deployed).

### Common error scenarios

| Error | Mitigation |
|---|---|
| User creating VM lacks read access to image version | Grant Reader on shared image version |
| Image version not found | Replicate image version to VM's target region |
| VM/VMSS creation takes a long time | Confirm OS type matches; confirm sysprep correct; cross-link OSPTO (Playbook B § OP-OSPTO) |
| `NotFound: The platform image '/subs/<wrongSubId>/.../versions/<v>' is not available` | Use SIG subscription ID, not VM target sub ID |
| `ImageNotFound`: image reference missing `/versions/<V>` | Append `/versions/<V>` — complete reference required |

---

## DEPLOY-Image-SIGCrossTenant — Failed Deploy of SIG Image Across Tenants

Same scenarios as `DEPLOY-Image-SIG` plus Service Principal access requirement across tenants.

### Mitigation
- Request customer share SP access on the resource
- Confirm image reference includes `/versions/<V>`
- Confirm replication includes target region

How-to: https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/496054

---

## DEPLOY-Image-VMSSACG — Create VMSS from ACG Image Fails (OS state and image-type change)
### Error 1 — OS State mismatch
`OperationNotAllowed: Cannot update Virtual Machine Scale Set <X> as the current OS state of the VM Scale Set is Generalized which is different from the updated gallery image OS state which is Specialized`

VMSS OS State is metadata in Model View — cannot change in-place. Workaround: match generalized↔generalized, or redeploy VMSS with the Specialized image.

### Error 2 — Image type cannot be changed
`OperationNotAllowed: The Image type for a Virtual Machine Scale Set may not be changed.`

If VMSS was NOT originally created from ACG image, update image reference via portal (VMSS → Instances → Settings → Operating System), API, or PS:

```powershell
Update-AzVmss -ResourceGroupName "<rg>" -VMScaleSetName "<vmss>" `
    -ImageReferenceId "/subscriptions/{SubId}/resourceGroups/{RG}/providers/Microsoft.Compute/galleries/<gal>/images/<def>/versions/2.0.0"
```

### Cross-link
Deeper VMSS-ACG upgrade scenarios → Playbook E § VMSS-Upgrade-*.

---

## DEPLOY-Image-OSProfile — Cannot set OSProfile on existing OSDisk (CreateOption=Attach vs FromImage)

**Scope**: Customer tries to set `osProfile` (machine name / password / SSH key) on a deployment that references an **existing** OS disk.

**Error**: `OSProfile is not allowed when CreateOption is Attach.`

### Cause
Customer used `CreateOption="Attach"` instead of `"FromImage"`. With `Attach`, the OS disk is a **specialized** disk (already provisioned), so the platform cannot change machine name / password / etc.

### Customer's misuse pattern

**PowerShell**:
```powershell
$vm = Set-AzVMOSDisk -VM $vm -Name $osDiskName -VhdUri $osDiskUri -CreateOption attach -Windows
```

**JSON template**:
```json
"storageProfile": {
  "osDisk": {
    "name": "[concat(parameters('vmName'))]",
    "osType": "[parameters('osType')]",
    "caching": "ReadWrite",
    "vhd": { "uri": "[parameters('osDiskVhdUri')]" },
    "createOption": "Attach"
  }
}
```

### Mitigation
Two options:
1. **Create sysprepped version** of the OSDisk (generalize), then use `CreateOption=FromImage`. Ref: https://azure.microsoft.com/en-us/documentation/articles/virtual-machines-windows-upload-image/
2. **Use password reset extension** instead of trying to change credentials at create-time. Ref: https://docs.microsoft.com/en-us/troubleshoot/azure/virtual-machines/reset-rdp

---

---

## DEPLOY-Marketplace-PurchaseErrors — Marketplace Purchase Validation Errors

**Symptom**: `Marketplace purchase validation failed for VM` + errorCode 161056 + correlation Id. Often "offer removed from marketplace" / eligibility / etc.

### Q1 — Find ARM EventServiceEntries for the marketplace op

```kusto
let Clusters = entity_group [cluster('https://armprodeus.eastus.kusto.windows.net'),
                             cluster('https://armprodweu.westeurope.kusto.windows.net'),
                             cluster('https://armprodsea.southeastasia.kusto.windows.net')];
macro-expand isfuzzy = true Clusters as ARMProd
(
ARMProd.database("Requests").EventServiceEntries
  | where PreciseTimeStamp between (datetime({Starttime}) .. datetime({Endtime}))
  | where subscriptionId == '{SubscriptionId}'
  | where operationName !contains "Microsoft.Authorization"
  | where operationName !contains "restorePoint"
  | project PreciseTimeStamp, ActivityId, correlationId, operationName, operationId, resourceProvider,
            level, status, subStatus, httpRequest, properties, resourceUri, armServiceRequestId,
            authorization, claims, RoleInstance, SourceNamespace
)
```

### Q2 — Confirm Store API response (Marketplace traces)

```kusto
let Clusters = entity_group [cluster('https://armprodeus.eastus.kusto.windows.net'),
                             cluster('https://armprodweu.westeurope.kusto.windows.net'),
                             cluster('https://armprodsea.southeastasia.kusto.windows.net')];
macro-expand isfuzzy = true Clusters as ARMProd
(
ARMProd.database("Requests").MarketplaceTraces
  | where PreciseTimeStamp between (datetime({Starttime}) .. datetime({Endtime}))
  | where correlationId == "{CorrelationId}"
  | project PreciseTimeStamp, Level, TaskName, ActivityId, subscriptionId, correlationId, operationName,
            providerNamespace, resourceType, resourceId, message, exception
)
```

**NOTE**: `MarketplaceTraces` is now restricted to PG only.

### Action
**Collab to ASMS** via SAP `Azure\Subscription management\Purchase, sign up or upgrade issues\Unable to make a purchase`. ASMS may engage Azure Commerce Embedded Escalation Engineering (ACEEE) via IcM.

ASMS TSG: https://internal.evergreen.microsoft.com/en-us/topic/bbe34ff4-83bf-e83d-a92c-da8ad66fec5c

---

## DEPLOY-Marketplace-Eligibility — MarketplacePurchaseEligibilityFailed (9 symptoms)

Umbrella error: `MarketplacePurchaseEligibilityFailed: Marketplace purchase eligibilty check returned errors. See inner errors for details.`

**Always read inner errors** — symptom routes mitigation:

### Symptom 1: Legal terms not accepted (programmatic deploy)
`Legal terms have not been accepted ... configure programmatic deployment for the Marketplace item or create it there for the first time`
**Mitigation**: Deploy from portal once OR set programmatic deployment attribute. Palo Alto images: deploy solution template once first.

### Symptom 2: Legal terms via Get/Set-AzMarketplaceTerms

```powershell
$agreementTerms = Get-AzMarketplaceterms -Publisher "<pub>" -Product "<prod>" -Name "<sku>"
Set-AzMarketplaceTerms -Publisher "<pub>" -Product "<prod>" -Name "<sku>" -Terms $agreementTerms -Accept
```
```bash
az vm image accept-terms --urn paloaltonetworks:vmseries1:bundle1:8.1.0
```

### Symptom 3: Offer/Publisher Not Found
`Offer with PublisherId: '<>' and OfferId: '<>' not found. If this offer has been created recently, please allow up to 30 minutes`
**Mitigation**: Wait 30 min if recent publish; else → [DEPLOY-Marketplace-PurchaseErrors](#deploy-marketplace-purchaseerrors--marketplace-purchase-validation-errors) → ASMS.

### Symptom 4: Marketplace purchase not enabled (EA)
`Marketplace purchase is not enabled.`
**Mitigation**: EA Admin enables in EA Portal: https://docs.microsoft.com/en-us/azure/cost-management-billing/manage/ea-portal-get-started#azure-marketplace

### Symptom 5: Unknown payment instrument
`unknown payment instrument(s) is unsupported for offer with OfferId: <>, PlanId <>.`
**Mitigation**: Update payment method: https://docs.microsoft.com/en-us/azure/cost-management-billing/manage/change-credit-card

### Symptom 6: Organization in deleted state
`Organization is in deleted state`
**Mitigation**: Collab ASMS via SAP `Azure > Subscription Management > Take ownership of my subscription`. Gather: Account Owner type (MSA/Org), name, phone+area, SubID, products, company, ZIP. Customer will need to reconfigure all RBAC after billing owner change.

### Symptom 7: IsStopSell + Market restriction
Error: `... was removed from the marketplace for new purchase.`

#### Q1 — Verify IsStopSell + Market in StoreApi

```kusto
cluster('Azmarket').database('StoreApi').DiagnosticsEvent
| where correlationId == '{CorrelationId}' and message contains "isStopSell"
| project env_time, message
```

Look for `"IsStopSellEnabled":true` + `"Market":"<CountryCode>"` — vendor disabled in that market.
**Mitigation**: Customer contacts publisher.

### Symptom 8: Offer not sold in customer's market
`The Offer: '<>' cannot be purchased by subscription: '<>' as it is not to be sold in market: '<CountryCode>'`

**Mitigation**: If customer deploying from OS disk with plan info from JSON/PS where platform doesn't expect plan → § DEPLOY-Image-VMMarketplaceInvalidInput Scenario 3. Else publisher contact.

### Symptom 9: BYOS Linux gold images (RHEL etc.)
`You have not accepted the legal terms on this subscription: '<>' for this plan.`

```powershell
Get-AzMarketplaceTerms -Publisher redhat -Product rhel-byos -Name rhel-lvm87
Set-AzMarketplaceTerms -Accept -Publisher redhat -Product rhel-byos -Name rhel-lvm87
```

If old `AzureRm*` cmdlets fail with `Cannot bind argument to parameter 'Name'` → `Install-Module -Name Az.Tools.Migration`.

---

## DEPLOY-ACG-Gallery — Cannot Create Shared Image Gallery

### Errors

#### Same name in different locations
`InvalidResourceLocation HTTP 409: The resource '<>' already exists in location '<>' in resource group '<>'`
**Mitigation**: Gallery names must be unique per subscription.

#### Invalid name
`The entity name 'galleryName' is invalid according to its validation rule: ^[^_\W][\w-._]{0,79}(?<![-.])$.`
**Mitigation**: Uppercase/lowercase letters, digits, dots, periods. Max 80 chars. No leading underscore/special char.

---

## DEPLOY-ACG-Definition — Cannot Create Shared Image Definition

### Errors

#### Invalid name
`The entity name 'galleryImageName' is invalid according to its validation rule: ^[^_\W][\w-._]{0,79}(?<![-.])$.`
**Mitigation**: Letters/digits/dots/dashes/periods. Max 80 chars.

#### Equal mandatory properties (Publisher/Offer/SKU dup)
`OperationNotAllowed HTTP 409: Gallery image: '<>' identified by (publisher: '<>', offer: '<>', sku: '<>') already exists. Choose a different publisher, offer, sku combination.`
**Mitigation**: Use unique Publisher+Offer+SKU combo across all definitions in same Gallery.

---

## DEPLOY-ACG-Version — Cannot Create Shared Image Version (replication / timeout / size limits)

### Errors

#### Invalid name
`The image version name is invalid. The image version name should follow Major(int).Minor(int).Patch(int) format, for e.g: 1.0.0, 2018.12.1 etc.`

#### Source image not found
`NotFound: Source Image '<>' is not found. Please check source image exists, and is in the same region as gallery image version being created.`
**Mitigation**: Source image must exist + same region as version + same subscription as gallery.

#### Source image in use
`Conflict: The source image '<>' is being used by another replication currently. Please retry after some time.`

#### Replication to target region not complete
`Failed: Replication to all the target regions not completed. The replication job has not completed at region: '<X>'.`

**Customer-side validation**:
```bash
az sig image-version show -g <RG> -r <GalleryName> -i <DefinitionName> --gallery-image-version <V> --expand "ReplicationStatus"
```
```powershell
Get-AzGalleryImageVersion -ResourceGroupName "<RG>" -GalleryName "<GalleryName>" -GalleryImageDefinitionName "<DefinitionName>" -GalleryImageVersionName "<V>" -ExpandReplicationStatus
```

**Jarvis-side**: Get ActivityId via [CapsApiQosEvent](https://jarvis-west.dc.ad.msft.net/859A5A0D) filtered by SubID. Look for `operationName == ExternalGalleryApi.PutGalleryImageVersion.PUT`, get OperationId, then check [CapsContextActivityEvent](https://jarvis-west.dc.ad.msft.net/CD608982) by ActivityId.

#### Timeout (image too big) — 6h limit
Context Activity: `Operation failed: InternalExecutionError ... System.TimeoutException: Execution timed out after 06:00:00. Last executing block: CopySeedBlobsIntoRegionBlock (Build).`

In Context Activity log starting with "Input gallery image version is", find OS/data disk sizes.

**Size limits**:
- OS disk max for ACG: **2 TB**
- Data disk:
  - No data disk → delete + recreate version
  - Data disk < 1 TB → delete + recreate version
  - Data disk ≥ 1 TB → SIG NOT supported for big images

Engineering can sometimes extend timeout to 24h depending on customer category.

---

## DEPLOY-ACG-Quota — Increasing ACG Quota Limits

Per-sub-per-region ACG resource limits (galleries, image definitions, image versions, replicas per version, replica regions). Quota increase via CCE or self-service portal Quota tab.

**SAP**: `Azure/Service and subscription limits (quotas)/Compute-VM (cores-vCPUs) subscription limit increases`

---

## DEPLOY-AIB-ConnectionError — NSG blocking WinRM/SSH on existing VNet

### Symptom
AIB into existing VNet with restrictive NSG (DenyAll inbound before defaults). Build fails after ~30 min:

- **Windows**: `WinRM connection err: unknown error Post "https://10.0.11.7:5986/wsman": proxyconnect tcp: dial tcp 10.241.228.0:60000: i/o timeout`
- **Linux**: `TCP connection to SSH ip/port failed: Error connecting to bastion: dial tcp 10.241.10.0:60000: connect: connection timed out`

### Root cause
AIB deploys build VM + proxy VM. Communicates via:
- `168.63.129.16` → covered by `AzureLoadBalancer` source rule
- Private Endpoint IP (a VNET address) → NOT covered, blocked by DenyAll

Only triggers when DenyAll inbound rule is BEFORE default `AllowVnetInBound`.

### Mitigation — add inbound rules BEFORE DenyAll
1. TCP 60000-60001 from `AzureLoadBalancer` to `VirtualNetwork`
2. TCP 60000-60001, 22, 5986 from `VirtualNetwork` to `VirtualNetwork` (or Any↔Any if customer agrees)

Public: https://learn.microsoft.com/en-us/azure/virtual-machines/linux/image-builder-networking#what-is-deployed-during-an-image-build

---

## DEPLOY-AIB-NoCustomizer — Azure Policy blocking AIB staging resources

### Symptom
- Provisioning Error Code: `NoCustomizerScript`
- Generic provisioning error msg pointing to `aka.ms/azvmimagebuilderts`
- Packer logs: `Image template is not provisioned; cannot get packer logs`
- **No customization.log file created**

### Cause
Azure Policy denies creation of one of AIB's backing resources:
- The `IT_<originalRG>_*` staging RG
- The storage account inside staging RG for logs
- (Less common) The image template itself

### Investigation (ASC)
1. Subscription → Operations tab → narrow timeframe
2. Filter by original RG (catches `IT_*` staging RG too — name contains original RG name)
3. Find `Microsoft.Authorization/policies/deny/action` with **Failed** status
4. Click the failed `storageAccounts/write` (or `resourceGroups/write`) → error includes Azure Policy name

### Mitigation
Adjust Azure Policy to allow AIB to create:
- Staging RG (named `IT_<originalRG>_<timestamp>_*`)
- Storage account in staging RG
- Image template resource

If complex → collab Azure Policy team (verify via AVA / TA).

---

## DEPLOY-AIB-CIS — Build Failures with CIS Hardened Images

### Symptom
- `runState == "failed"` in ASC
- Source image from `center-for-internet-security-inc / cis-windows-server / cis-windows-server2019-l1-gen2`
- customization.log: `PACKER ... azure-arm,error []string{"Timeout waiting for WinRM."}`

### Cause
CIS hardening disrupts WinRM (firewall rules, services, security policies). AIB/Packer rely on WinRM → timeout.

### Status (as of June 2025)
**No built-in AIB fix.** Not on roadmap. Packer / AWS have workarounds but not integrated into AIB.

### Customer guidance
- Acknowledge known issue
- Cause: CIS hardening interferes with WinRM
- Current limitation: no automated AIB solution
- Gather AIB template + customization.log if further investigation needed

Ref: https://learn.microsoft.com/en-us/azure/virtual-machines/linux/image-builder-troubleshoot#prerequisites

---

## DEPLOY-Container-PoolNotFound — PreprovisionedDiskPoolNotFound (non-fatal)

### What you'll see
```
PreprovisionedVMReuseResult: AzsmEscrowUnexpectedFailure. Escrow for pre-provisioned resources in AzSM failed,
"AllocationFault":"PreprovisionedDiskPoolNotFound", errorDetails: PoolNotFoundException--Unable to find a pool for the given request.
EscrowId=<>
```

### Solution
**NOT a fatal failure.** No preprovisioned VM in escrow was available, so CRP creates a normal deployment. Happens frequently and is normal. **Ignore and continue investigating logs for the actual failure.**

---

## DEPLOY-Container-LargeResource — Container Creation Fails During Large Resource VHD Prep

**Scope**: Deploying Standard **G5** VMs (or other SKUs with very large local resource disk, **6.5 TB+**) — Container creation fails because preparing the large resource VHD hits a Windows partition / drive-letter timing bug (WMI / `MSFT_Partition::AddAccessPath` returns `0x80070467` = `ERROR_DISK_OPERATION_FAILED`).

Known ICMs: [188681750](https://portal.microsofticm.com/imp/v3/incidents/details/188681750/home), [199396301](https://portal.microsofticm.com/imp/v3/incidents/details/199396301/home).

### Q1 — Confirm via Service Healing tenant status

```kusto
cluster("AzureCM").database("AzureCM").ServiceHealingTenantStatusEtwTable
| where TenantName == "{TenantName}"
| where PreciseTimeStamp > datetime({StartTime})
| where PreciseTimeStamp < datetime({EndTime})
| project PreciseTimeStamp, State, Message
```

**Look for** `Message` containing:
- `Operation 'CreateContainer' is configured to surface a fault after 4 successive failures`
- `FailedFunction(s): PrepareDiskImage, DiskPrepareVhd Failed in creating the Resource VHD., RuntimeVmBaseContainer::PrepareResourceVhd`
- `FailingHr: 0x80070467 HRESULT_FROM_WIN32(ERROR_DISK_OPERATION_FAILED)`
- `EscalateTo: RDOS\Azure Host OS Mitigations`

### Agent-log signature (from CSS support package, if collected)
```
ERROR ... MI_Session_Invoke failed invoking MSFT_Partition::AddAccessPath with ReturnValue: 1
ERROR ... <- AddAccessPathOnPartition=0x80070467
```

### Customer-facing RCA (verbatim from TSG)

> Microsoft Azure team has finished investigating the issue with your Virtual Machine instance <INSTANCE NAME>. We identified that the physical host node where your VM was placed was impacted due to a platform bug. A timing issue occurs when preparing the large resource VHD resulting in the failure. Our core platform engineers have identified a fix for this issue. The fix will be deployed after testing and validation is completed. For immediate mitigation, we recommend using a SKU size which uses a resource VHD less than 4 TB or eliminating the use of resource VHD.
>
> We are continuously working on improving the platform and apologize for any inconvenience this may have caused to you.
>
> Microsoft Azure Team

### Mitigation
- Immediate: use a SKU with resource VHD < 4 TB, or eliminate the resource VHD
- Long-term fix: Azure Host OS (track via parent ICMs above)

Reference: https://docs.microsoft.com/en-us/azure/virtual-machines/sizes-previous-gen

---

## DEPLOY-Disk-BlobInUse — DiskBlobAlreadyInUseByAnotherDisk

**Error**: `DiskBlobAlreadyInUseByAnotherDisk: Blob https://<>/vhds/<>.vhd is already in use by another disk belonging to VM 'vmname'.`

**Cause**: Customer's template references an OS VHD URI that already belongs to existing VM, OR customer used same VM name as existing deployment.

### Mitigation
- Use unique OS VHD URI for the new deployment
- Use unique VM name
- ASC → Disks under storage account → search VHD URI → see which VM has it leased

---

## DEPLOY-Disk-BlobPendingCopy — DiskBlobPendingCopyOperation

Short: http://aka.ms/DiskBlobPendingCopyOperation

**Error**: `DiskBlobPendingCopyOperation: Disk blob <>.vhd is not ready. Copy state: Pending. Please retry when the blob is ready.`

**Cause**: VHD copy operation hadn't completed before deploy attempt.

**Mitigation**: `Get-AzStorageBlobCopyState` to confirm copy done, then retry deploy.

---

## DEPLOY-Disk-TargetBlobExists — TargetDiskBlobAlreadyExists (blob already attached)

Short: https://aka.ms/targetdiskblobalreadyexists

**Error**: `TargetDiskBlobAlreadyExists: Blob "BLOB.VHD" already exists. Please provide a different blob URI as target for disk '<>-osDisk'.`

**Cause**: The target blob name has already been used — either it is currently attached to another VM (running as a VM via `AttachDisk` primitive) OR a VHD with the same name was previously deleted but the slot is still considered in use.

### Mitigation
- If the blob is already attached to a running VM — use a **different** blob URI for the new deployment
- If the customer wants to use the blob as an **image source** — the deployment must use the `FromImage` primitive (not `AttachDisk`). VHD MUST be sysprepped, otherwise the deploy will fail with provisioning timeout

Doc: https://azure.microsoft.com/en-us/documentation/articles/virtual-machines-windows-upload-image/

Distinct from [DEPLOY-Disk-BlobInUse](#deploy-disk-blobinuse--diskblobalreadyinusebyanotherdisk) which is about *another disk* holding the blob; this anchor is about the *target* blob slot.

---

## DEPLOY-SA-LocationMismatch — StorageAccountLocationMismatch

Short: http://aka.ms/StorageAccountLocationMismatch

**Error**: `StorageAccountLocationMismatch` — VM region ≠ referenced storage account region.

### Q1 — Count affected correlations

```kusto
cluster('armprodgbl.eastus.kusto.windows.net').database('ARMProd')
| macro-expand isfuzzy=true ARMProdEG as X (
    X.database('Requests').EventServiceEntries
    | where status == "Failed"
    | where properties contains "StorageAccountLocationMismatch"
    | where TIMESTAMP > ago(10d)
    | summarize dcount(correlationId)
)
```

### Troubleshooting
Check ContextActivity (MDM) for `HttpStatusCode.Forbidden 403 from StorageAccountEndpoint service` — confirms cert/region mismatch.

### Mitigation
Use storage account in same region as VM. If CRP/SRP cert config issue → ICM template `Virtual Machines | IaaS provisioning`.

---

## DEPLOY-SA-TypeNotSupported — Blob Storage rejected for boot diag

**Error**: `StorageAccountTypeNotSupported: boot diagnostics uses STORAGEACCOUNT which is a Blob storage account. Please retry with General purpose storage account.`

**Cause**: "Blob Storage" account types don't support page blobs. VM + Extension resources require page blobs.

**Mitigation**: Use **General Purpose v1 or v2** storage account. **Managed boot diagnostics** (no SA needed) is preferred modern alternative.

---

## DEPLOY-Quota-Deployment — DeploymentQuotaExceeded (800/RG)

**Error**: `DeploymentQuotaExceeded` — RG limited to 800 deployments in history.

### Mitigation — delete old deployments from RG history (does NOT affect resources)

**Azure CLI**:
```bash
az deployment group delete --resource-group <RG> --name <deployName>
az deployment group list --resource-group <RG> --query "length(@)"
```

**Azure PowerShell**:
```powershell
Remove-AzResourceGroupDeployment -ResourceGroupName <RG> -Name <deployName>
(Get-AzResourceGroupDeployment -ResourceGroupName <RG>).Count
```

Docs: https://docs.microsoft.com/en-us/azure/azure-resource-manager/deployment-quota-exceeded

---

## DEPLOY-Update-VMRedeploymentFailed — VMRedeploymentFailed (customer-facing)

**Error**: `VMRedeploymentFailed: VM 'VMNAME' redeployment failed due to an internal error. Please retry later`

**Cause**: Generic CRP-side failure on redeploy. **Most commonly** triggered by CRP service restart mid-operation (see [DEPLOY-CRP-Restarted](#deploy-crp-restarted--crp-service-restart-vmredeploymentfailed--taskcanceledexception) for the root-cause RCA via ContextActivity).

### Mitigation (FDR — retry)

Keep retrying the redeploy via portal or PowerShell. Each retry is on a fresh CRP node and typically succeeds:

```powershell
Login-AzAccount
$vmname = Get-AzVM -ResourceGroupName "ResourceGroupName"
$rgname = Get-AzResourceGroup -Name "ResourceGroupName"
Set-AzVM -Redeploy -ResourceGroupName $rgname -Name $vmname
```

### When to escalate vs retry
- First or second failure on redeploy → retry (CRP service restart pattern)
- 3+ consecutive failures on different retry attempts → run [DEPLOY-CRP-Restarted](#deploy-crp-restarted--crp-service-restart-vmredeploymentfailed--taskcanceledexception) Q1 ContextActivity. If NO `Restarting operation after service restart` message present, escalate to CRP team — likely a different root cause
- Customer needs Failed-state cleared between retries → trigger empty Update (see CRP-Restarted mitigation)

---

## DEPLOY-Update-VMStuckInUpdating — VM stuck in Updating (NSG / manifest)

**Scope**: VM stays in `Updating` state for prolonged periods. Two known patterns:

### Pattern A — Blocking NSG (most common)
**Cause**: NSG blocks access to Azure Storage stamps (or Azure datacenter IPs in general) so the in-guest agent can't download extension manifests / heartbeat back.

**Investigation**: ASC → NSG blade for the VM's NIC. Look for outbound deny rules.

**Mitigation**: Relax NSG to allow outbound to Azure backend traffic. Customer can use Azure public IP list https://www.microsoft.com/en-us/download/details.aspx?id=56519 to scope rules.

### Pattern B — Error in downloading version manifest
In the VM **Instance View**:
```
"message": "Error in downloading version manifest via HostGAPlugin for Microsoft.Azure.Diagnostics.IaaSDiagnostics from:
  https://rdfepirv2bl2prdstr01.blob.core.windows.net/.../*_manifest.xml,
  Exception: Unable to connect to the remote server"
```

**Cause**: Extension's manifest blob is unreachable from the VM — same root cause as Pattern A (NSG / network policy blocks Storage endpoint) but surfaces in extension instance view, not NSG audit.

**Mitigation**: Same as Pattern A — fix outbound to Storage stamps. After fix, extension auto-recovers on next heartbeat.

### RCA coding
`Rootcause - Windows Azure/Virtual Machines/Deployment Issues/How Tos/ Advisory`

---

## DEPLOY-Quota-vCPU — QuotaExceeded (vCPU)

Common variants: per-region vCPU, total regional vCPU, per-family vCPU (e.g., `Standard DSv3 Family`).

### Mitigation
- CCE quota increase via SAP `Azure/Service and subscription limits (quotas)/Compute-VM (cores-vCPUs) subscription limit increases`
- Self-service: Portal → My quotas → request increase
- Doc: https://learn.microsoft.com/en-us/azure/azure-portal/supportability/per-vm-quota-requests

For SKU-not-available (similar symptom, different root cause) → [DEPLOY-Alloc-SkuNotAvailable](#deploy-alloc-skunotavailable--skunotavailable-notavailableforsubscription-availabilityzonenotsupported).

---

## DEPLOY-Region-NotRegistered — Cannot Deploy in New Region

Short: http://aka.ms/Nfufxw

**Cause**: Customer sub not registered in new region.

### Mitigation
- **Auto**: deploy a VM in any other region (registration auto-occurs for new region)
- **Manual**: `Register-AzResourceProvider -ProviderNamespace Microsoft.Compute`
- **CLI**: `az provider register --namespace Microsoft.Compute`
- If RP already registered → engage billing to enable region for sub

### Cross-link
For 502 Bad Gateway variant of same root cause → Playbook F § MD-Platform-1.

---

## DEPLOY-Reg-Missing — MissingSubscriptionRegistration

**Error**: `MissingSubscriptionRegistration: The subscription is not registered to use namespace 'Microsoft.Network'` (or any RP)

**Cause**: Portal auto-registers RPs; PowerShell/CLI/Terraform/SDK do NOT.

### Mitigation

```bash
az provider register --namespace 'Microsoft.Compute'
az provider register --namespace 'Microsoft.Network'
az provider register --namespace 'Microsoft.Storage'
```
```powershell
Register-AzResourceProvider -ProviderNamespace Microsoft.Compute
Register-AzResourceProvider -ProviderNamespace Microsoft.Network
Register-AzResourceProvider -ProviderNamespace Microsoft.Storage
```

---

## DEPLOY-Policy-Denied — RequestDisallowedByPolicy

**Error**: `Forbidden / RequestDisallowedByPolicy: The resource action '<>' is disallowed by one or more policies. Policy identifier(s): '<policyResourceId>'.`

### Q1 — Find RequestDisallowedByPolicy events in ARM

```kusto
cluster('armprodgbl.eastus.kusto.windows.net').database('ARMProd')
| macro-expand isfuzzy=true ARMProdEG as X (
    X.database('Requests').EventServiceEntries
    | where PreciseTimeStamp between (datetime({BeginTime}) .. datetime({EndTime}))
    | where subscriptionId == "{SubscriptionId}"
    | where properties contains "RequestDisallowedByPolicy"
    //| where properties contains "<policyName>"   // optional: scope to specific policy
    | project TIMESTAMP, subscriptionId, correlationId, operationName, resourceUri, status, subStatus, properties
)
```

### Look up the policy (ACIS)
`GetSubscriptionPolicyDefinitions` endpoint in ACIS. Common MSIT example: `SDOStdPolicyNetwork` blocks PIP, NSG, UDR, RouteTables, ClassicCompute/Storage/Network on subs with ExpressRoute circuit.

### Mitigation
- Customer's policy admin modifies/exempts policy
- For MSIT subs: redirect to MSIT (ExpressRoute Provider Subscription Model wiki)
- Customer refactors template to avoid blocked resource

---

## DEPLOY-Provision-OSPTO — OSProvisioningTimedOut (deploy-time)

Short: https://aka.ms/CCSupOSPTO

**Scope**: Deployment fails with `OSProvisioningTimedOut`. Timeouts:
- Windows: 40 min
- Linux: 20 min

VM may be Started and OS running even though VM in Failed state — PA didn't communicate completion.

### Common causes
- Image not prepared correctly (sysprep / waagent / cloud-init)
- Provisioning Agent (PA) issues
- Host or wireserver issues
- Platform networking issues

### Investigation
**Save the failed VM** before deleting — without it, no RCA guarantee.

Follow [Provisioning Workflow](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495735) — guides through PA / image / host investigation.

### Mitigation
**Failed state cannot be cleared.** After investigation, customer options:
1. Delete failed VM, save the disk, deploy new specialized VM from existing disk
2. Delete failed VM + recreate from scratch (after fixing image)

### Cross-link
- Deeper OSPTO RCA (Linux waagent / cloud-init / KVP guest logs) → Playbook B § OP-OSPTO
- ASAP-related VM-stuck-during-create → `asap-storage-queries.md`
- Cross-link to CAPA-Delay if extension hang due to network blip

---

## DEPLOY-Provision-CloudInit — Cloud Init Failures (Linux OSPTO subset)

**Scope**: Linux VM hits [OSProvisioningTimeout](#deploy-provision-ospto--osprovisioningtimedout-deploy-time) because cloud-init never completes.

### Symptoms
- ASC: "cloud-init did not complete" finding
- Serial log shows: `INFO Wait for cloud-init to copy ovf-env.xml` then no progress
- VM stuck "Creating" beyond Linux 20-min OSPTO threshold

### Investigation
- Guest logs: `/var/log/cloud-init.log` + `/var/log/cloud-init-output.log`
- Check cloud-init version (older versions have known bugs around Azure datasource) — see internal TSG "OSPTO with an old Cloud-Init"
- Custom user-data script errors typically appear at end of `cloud-init-output.log`
- Cross-link to **vm-log-analyzer** skill for cloud-init log analysis

### Common causes
- Custom user-data script blocks indefinitely (no timeout)
- Custom user-data tries to apt-get / yum without retry on transient network failure
- Old cloud-init version on customer's custom image
- VNet DNS doesn't resolve `168.63.129.16` (IMDS / WireServer dependency)

### Mitigation
Failed state can't be cleared. Customer must:
1. Capture serial log + cloud-init logs from failed VM (save the failed VM before deleting)
2. Fix the cloud-init script / upgrade cloud-init in their custom image
3. Recreate VM from fixed image

### Cross-link
- Generic OSPTO routing → [DEPLOY-Provision-OSPTO](#deploy-provision-ospto--osprovisioningtimedout-deploy-time)
- Cloud-init log deep analysis → vm-log-analyzer skill
- CA/PA delay causing intermittent network during cloud-init → [DEPLOY-CAPA-Delay](#deploy-capa-delay--capa-mapping-delay-network-blip-post-create)

**RCA coding**: `Root Cause - Windows Azure\Compute\Virtual Machines\OS Provisioning Timeout`

---

## DEPLOY-Sysprep-Failed — Sysprep failed or stuck (GeneralizationState mitigation)

**Scope**: Customer's Windows custom image fails sysprep during capture OR sysprep is stuck during cleanup phase.

### Investigation
- Primary logs:
  - `C:\Windows\System32\Sysprep\Panther\setupact.log`
  - `C:\Windows\System32\Sysprep\Panther\setuperr.log`

### Common failure signatures

**1. Cleanup phase failure** (after multiple sysprep runs):
```
Error [0x0f0073] SYSPRP RunDlls:Not running DLLs; either the machine is in an invalid state or we couldn't update the recorded state, dwRet = 0x1f
Error [0x0f00ae] SYSPRP WinMain:Hit failure while processing sysprep cleanup external providers; hr = 0x8007001f
```

**2. App not provisioned for all users** (UWP / Modern app installed per-user):
```
SYSPRP Package Microsoft.LanguageExperiencePackfr-FR_<version> was installed for a user, but not provisioned for all users. This package will not function properly in the sysprep image.
SYSPRP Failed to remove apps for the current user: 0x80073cf2.
SYSPRP ActionPlatform::LaunchModule: Failure occurred while executing 'SysprepGeneralizeValidate' from C:\Windows\System32\AppxSysprep.dll; dwRet = 0x3cf2
```

### Root cause
Running sysprep multiple times (especially after a previous failure) leaves the registry in an invalid state. Specifically:
```
HKLM:\SYSTEM\Setup\Status\SysprepStatus\GeneralizationState = 3   # invalid
```
Value `3` means generalize phase started but didn't complete — subsequent sysprep runs fail.

### Mitigation

**Reset GeneralizationState back to a valid value, then rerun sysprep**:

```powershell
Set-ItemProperty -Path 'HKLM:\SYSTEM\Setup\Status\SysprepStatus' -Name GeneralizationState -Value 7
```

`7` = generalize ready or already prepared. After this change rerun:
```powershell
C:\Windows\System32\Sysprep\sysprep.exe /generalize /oobe /shutdown
```

If the second failure pattern (per-user apps) appears — customer must first uninstall the offending per-user packages (or provision them for all users) before sysprep can succeed:
```powershell
Get-AppxPackage -AllUsers <PackageName> | Remove-AppxPackage -AllUsers
```

---
