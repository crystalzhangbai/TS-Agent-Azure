# Playbook G — Deployment (Core)

> **Companion to** [`playbook-G-deployment-deep.md`](./playbook-G-deployment-deep.md). Use this file as the **routing entry point** when a case is about a **deployment-time / create-time** failure (CRP throttling/preemption, allocation, SKU, PPG, capacity reservation, Gen2/TL/Confidential/Hibernation, image/marketplace/ACG/AIB, container/disk at deploy, storage account at deploy, quota/region/policy, OSPTO at create). Full KQL bodies + customer wording live in the deep file under `DEPLOY-*` anchors. Foundation queries live in `references/crp-queries.md`, `references/operations-queries.md`, `references/vm-properties-queries.md`.

## When to use this playbook

| Use Playbook G when... | Don't — use instead |
|---|---|
| Failure happened during VM/VMSS **create** (resource didn't exist before) — `labels.IsNew=True` | Failure on an existing VM start/stop/restart/delete → Playbook B |
| `SkuNotAvailable` / `OverconstrainedZonalAllocationRequest` / `InvalidVMSize` at create | `AllocationFailed` on existing VM start → Playbook B § OP-Allocation |
| Image / Marketplace / ACG / AIB / Publisher issues | Disk-only lifecycle (delete/resize/snapshot of existing managed disk) → Playbook F |
| Capacity Reservation create / update / delete failures | Customer ICM about quota in general (no compute failure) → CCE quota team |
| Gen2 / Trusted Launch / Hibernation / Confidential at create | Generic CRP throttling on runtime ops → Playbook B |
| Marketplace purchase eligibility / legal terms | ASMS subscription/billing issues — collab to ASMS team |
| OSPTO at first create | OSPTO RCA in guest (waagent / cloud-init analysis) → Playbook B + vm-log-analyzer |
| Long Deployment (>10min) | Long Deployment caused by PM/LM in same window → Playbook D |
| VMSS-specific shape/upgrade/scale issue | → Playbook E (VMSS) |

## Inputs to collect

| # | Item | Why |
|---|---|---|
| 1 | `SubscriptionId` | Primary filter for every Kusto query |
| 2 | `ResourceGroupName` | Secondary filter |
| 3 | `VMName` / `VMSSName` | Resource identifier |
| 4 | `CorrelationId` | ARM → CRP correlation. Customer has it in CLI/PS output or Activity Log |
| 5 | `OperationId` | CRP → DiskRP / PirCas correlation |
| 6 | `StartTime` / `EndTime` (UTC) | Pad ±15 min around customer-reported timestamp |
| 7 | Exact error code + message (verbatim) | Routes to specific DEPLOY-* anchor |
| 8 | Deployment method (Portal / CLI / PS / Terraform / SDK / ARM template) | Routes to RP-registration / programmatic-purchase / sysprep-image scenarios |
| 9 | Image source (Marketplace / PlatformImage / SIG / ACG / Custom VHD / AIB) | Routes to image-specific anchor |
| 10 | Customer's VM size + region + zone | Used by SkuNotAvailable / AnyZone / PPG / CR scenarios |

## Step-by-step

### Step 1 — Confirm this is a deploy-time failure

Foundation query in `references/crp-queries.md` § `CrpOperationQoSEtwTable`:

```kusto
cluster('Azcsupfollower2.centralus.kusto.windows.net').database('crp_allprod').ApiQosEvent_nonGet
| where subscriptionId == "{SubscriptionId}"
| where resourceName =~ "{ResourceName}"
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| project PreciseTimeStamp, operationName, labels, resultCode, errorDetails, requestEntity, correlationId, operationId
| order by PreciseTimeStamp asc
```

- `labels has '"IsNew": "True"'` → deploy-time (Playbook G)
- Otherwise → likely runtime op on existing resource (Playbook B)

### Step 2 — Classify the symptom → route to DEPLOY-* anchor

#### CRP-side throttling / preemption / restart

| Symptom | Anchor |
|---|---|
| Op flagged `IsPreempted=true` (operationId ≠ goalSeekingActivityId) / customer says "operation took 10 min, but VM was usable in 30 sec" | § [DEPLOY-CRP-Preempted](./playbook-G-deployment-deep.md#deploy-crp-preempted--crp-operation-preempted-concurrent-ops) |
| `VMRedeploymentFailed` / `TaskCanceledException` + ContextActivity shows `Restarting operation after service restart` | § [DEPLOY-CRP-Restarted](./playbook-G-deployment-deep.md#deploy-crp-restarted--crp-service-restart-vmredeploymentfailed--taskcanceledexception) |
| Throttled policies end with `Resource` or `SubscriptionMaximum` | § [DEPLOY-CRP-RBT](./playbook-G-deployment-deep.md#deploy-crp-rbt--crp-resource-based-throttling-rbt) |
| 429 / `TooManyRequestsReceived` / `ResourceCollectionRequestsThrottled` (other policy names) | § [DEPLOY-CRP-Throttle](./playbook-G-deployment-deep.md#deploy-crp-throttle--crp-throttling-context-activity-internal-limits) ⚠ internal |
| `SubscriptionRequestsThrottled` / `OperationNotAllowed` 429 with `failureCause=gateway` | § [DEPLOY-CRP-SubThrottle](./playbook-G-deployment-deep.md#deploy-crp-subthrottle--subscriptionrequeststhrottled-arm-side) |

#### CA/PA mapping (post-deploy network blip)

| Symptom | Anchor |
|---|---|
| VM created OK but network blip / CloudInit fails / extension fails post-create; long deployment | § [DEPLOY-CAPA-Delay](./playbook-G-deployment-deep.md#deploy-capa-delay--capa-mapping-delay-network-blip-post-create) |
| Persistent network issues after create / start / resize / redeploy | § [DEPLOY-CAPA-Incorrect](./playbook-G-deployment-deep.md#deploy-capa-incorrect--capa-mapping-incorrect-wrong-pa-mapped) |

#### Allocation / SKU / capacity at deploy

| Symptom | Anchor |
|---|---|
| `SkuNotAvailable` / `NotAvailableForSubscription` / `AvailabilityZoneNotSupported` | § [DEPLOY-Alloc-SkuNotAvailable](./playbook-G-deployment-deep.md#deploy-alloc-skunotavailable--skunotavailable-notavailableforsubscription-availabilityzonenotsupported) |
| `InvalidParameter / InvalidVMSize` even though SKU is in valid list | § [DEPLOY-Alloc-InvalidVMSize](./playbook-G-deployment-deep.md#deploy-alloc-invalidvmsize--zero-width-space-in-vmsize-parameter) |
| `OverconstrainedZonalAllocationRequest` with `zonePlacementPolicy=Any` | § [DEPLOY-Alloc-AnyZone](./playbook-G-deployment-deep.md#deploy-alloc-anyzone--zoneplacementpolicy-any-overconstrained) |
| `LocationNotFoundForRoleSize` (RDFE) | § [DEPLOY-Alloc-LocNotFound](./playbook-G-deployment-deep.md#deploy-alloc-locnotfound--locationnotfoundforrolesize-rdfe) |
| Deployment > 10 min but eventually succeeds — customer wants RCA | § [DEPLOY-Alloc-LongDeploy](./playbook-G-deployment-deep.md#deploy-alloc-longdeploy--long-deployment-eg-analysis) |
| `NotFound: Proximity Placement Group ... cannot be found` | § [DEPLOY-PPG-NotFound](./playbook-G-deployment-deep.md#deploy-ppg-notfound--ppg-cannot-be-found-region-mismatch) |
| `OverconstrainedAllocationRequest` with PPG + VM Size constraints | § [DEPLOY-PPG-Overconstrained](./playbook-G-deployment-deep.md#deploy-ppg-overconstrained--ppg-overconstrainedallocationrequest-t2-spine-pinned) |
| Capacity reservation Create/Update/Delete fails (ODCR) | § [DEPLOY-CR-CUD](./playbook-G-deployment-deep.md#deploy-cr-cud--capacity-reservation-create-update-delete) |

#### Gen2 / Trusted Launch / Hibernation / Confidential

| Symptom | Anchor |
|---|---|
| Gen2 image + non-Gen2 SKU | § [DEPLOY-Gen2-CannotBoot](./playbook-G-deployment-deep.md#deploy-gen2-cannotboot--cannot-boot-hypervisor-generation-2) |
| Gen2 option greyed out after custom VHD upload | § [DEPLOY-Gen2-GreyedOut](./playbook-G-deployment-deep.md#deploy-gen2-greyedout--gen2-vm-option-greyed-out-custom-vhd) |
| `HypervisorGeneration2NotAllowedForUnmanagedVM` on PUT/Update | § [DEPLOY-Gen2-UnmanagedVM](./playbook-G-deployment-deep.md#deploy-gen2-unmanagedvm--hypervisorgeneration2notallowedforunmanagedvm) |
| Question: "Is this VM Gen1 or Gen2?" | § [DEPLOY-Gen2-Identify](./playbook-G-deployment-deep.md#deploy-gen2-identify--identify-gen2-vm-multi-source-detection) |
| Confidential VM DCasv5/ECasv5 with `securityType=TrustedLaunch` fails to start | § [DEPLOY-Conf-DCasv5](./playbook-G-deployment-deep.md#deploy-conf-dcasv5--confidential-vms-dcasv5--ecasv5-security-profile) |
| `OE_PLATFORM_ERROR on oe_create_enclave()` on DC2/DC4 | § [DEPLOY-Conf-OEPlatform](./playbook-G-deployment-deep.md#deploy-conf-oeplatform--confidential-computing-oe-platform-error-sgx-driver) |
| Hibernation-enabled VM PUT fails (BadRequest/Conflict) or extension fails to enable in guest | § [DEPLOY-Hibernate-Fails](./playbook-G-deployment-deep.md#deploy-hibernate-fails--creating-vm-with-hibernation-enabled-fails) |

#### Image / Marketplace / ACG / AIB

| Symptom | Anchor |
|---|---|
| `PlatformImageNotFound` (often EA-only image with non-EA sub) | § [DEPLOY-Image-PlatformNotFound](./playbook-G-deployment-deep.md#deploy-image-platformnotfound--platformimagenotfound-3-step-pircas-chain) |
| `ImageBlobNotFound` (unmanaged) / `ResourceNotFound` (managed image) | § [DEPLOY-Image-BlobNotFound](./playbook-G-deployment-deep.md#deploy-image-blobnotfound--imageblobnotfound-resourcenotfound) |
| `ImageNotFound` in portal | § [DEPLOY-Image-NotFound](./playbook-G-deployment-deep.md#deploy-image-notfound--imagenotfound-portal-deploy) |
| `IncorrectImageBlobType` (VHD as block blob) | § [DEPLOY-Image-IncorrectBlobType](./playbook-G-deployment-deep.md#deploy-image-incorrectblobtype--incorrectimageblobtype-block-vs-page-blob) |
| 3rd-party / publisher image fails (Azure platform ruled out) | § [DEPLOY-Image-Publisher](./playbook-G-deployment-deep.md#deploy-image-publisher--publisher-image-issues-3rd-party) |
| VM from SIG image fails (access / not found / sub mismatch / incomplete imageRef) | § [DEPLOY-Image-SIG](./playbook-G-deployment-deep.md#deploy-image-sig--create-vm-from-sig-image-fails) |
| Cross-tenant SIG deploy fails | § [DEPLOY-Image-SIGCrossTenant](./playbook-G-deployment-deep.md#deploy-image-sigcrosstenant--failed-deploy-of-sig-image-across-tenants) |
| VMSS update to ACG image fails (OS state mismatch / image type change) | § [DEPLOY-Image-VMSSACG](./playbook-G-deployment-deep.md#deploy-image-vmssacg--create-vmss-from-acg-image-fails-os-state-and-image-type-change) |
| `Marketplace purchase validation failed` / errorCode 161056 / offer removed | § [DEPLOY-Marketplace-PurchaseErrors](./playbook-G-deployment-deep.md#deploy-marketplace-purchaseerrors--marketplace-purchase-validation-errors) |
| `MarketplacePurchaseEligibilityFailed` (umbrella, 9 sub-symptoms) | § [DEPLOY-Marketplace-Eligibility](./playbook-G-deployment-deep.md#deploy-marketplace-eligibility--marketplacepurchaseeligibilityfailed-9-symptoms) |
| ACG: Cannot create Gallery | § [DEPLOY-ACG-Gallery](./playbook-G-deployment-deep.md#deploy-acg-gallery--cannot-create-shared-image-gallery) |
| ACG: Cannot create Image Definition | § [DEPLOY-ACG-Definition](./playbook-G-deployment-deep.md#deploy-acg-definition--cannot-create-shared-image-definition) |
| ACG: Cannot create Image Version / replication stuck / 6h timeout / 2TB OS disk limit | § [DEPLOY-ACG-Version](./playbook-G-deployment-deep.md#deploy-acg-version--cannot-create-shared-image-version-replication--timeout--size-limits) |
| ACG: quota increase | § [DEPLOY-ACG-Quota](./playbook-G-deployment-deep.md#deploy-acg-quota--increasing-acg-quota-limits) |
| AIB: WinRM/SSH timeout, NSG/DenyAll blocking | § [DEPLOY-AIB-ConnectionError](./playbook-G-deployment-deep.md#deploy-aib-connectionerror--nsg-blocking-winrmssh-on-existing-vnet) |
| AIB: `NoCustomizerScript` + no customization.log + Azure Policy denial | § [DEPLOY-AIB-NoCustomizer](./playbook-G-deployment-deep.md#deploy-aib-nocustomizer--azure-policy-blocking-aib-staging-resources) |
| AIB: CIS-hardened image WinRM timeout | § [DEPLOY-AIB-CIS](./playbook-G-deployment-deep.md#deploy-aib-cis--build-failures-with-cis-hardened-images) |

#### Container + Disk + Storage Account at deploy

| Symptom | Anchor |
|---|---|
| ContextActivity shows `PreprovisionedDiskPoolNotFound` | § [DEPLOY-Container-PoolNotFound](./playbook-G-deployment-deep.md#deploy-container-poolnotfound--preprovisioneddiskpoolnotfound-non-fatal) (non-fatal, ignore) |
| G-series VM create fails with `CreateContainer` failure + `0x80070467` + large resource VHD (6.5TB) | § [DEPLOY-Container-LargeResource](./playbook-G-deployment-deep.md#deploy-container-largeresource--container-creation-fails-during-large-resource-vhd-prep) |
| `DiskBlobAlreadyInUseByAnotherDisk` | § [DEPLOY-Disk-BlobInUse](./playbook-G-deployment-deep.md#deploy-disk-blobinuse--diskblobalreadyinusebyanotherdisk) |
| `DiskBlobPendingCopyOperation` | § [DEPLOY-Disk-BlobPendingCopy](./playbook-G-deployment-deep.md#deploy-disk-blobpendingcopy--diskblobpendingcopyoperation) |
| `TargetDiskBlobAlreadyExists` (target VHD slot already in use) | § [DEPLOY-Disk-TargetBlobExists](./playbook-G-deployment-deep.md#deploy-disk-targetblobexists--targetdiskblobalreadyexists-blob-already-attached) |
| `StorageAccountLocationMismatch` | § [DEPLOY-SA-LocationMismatch](./playbook-G-deployment-deep.md#deploy-sa-locationmismatch--storageaccountlocationmismatch) |
| `StorageAccountTypeNotSupported` (boot diag on Blob Storage account) | § [DEPLOY-SA-TypeNotSupported](./playbook-G-deployment-deep.md#deploy-sa-typenotsupported--blob-storage-rejected-for-boot-diag) |

#### Quota / region / policy / RP-registration

| Symptom | Anchor |
|---|---|
| `DeploymentQuotaExceeded` (800/RG history) | § [DEPLOY-Quota-Deployment](./playbook-G-deployment-deep.md#deploy-quota-deployment--deploymentquotaexceeded-800rg) |
| `QuotaExceeded` (per-region vCPU / per-family quota) | § [DEPLOY-Quota-vCPU](./playbook-G-deployment-deep.md#deploy-quota-vcpu--quotaexceeded-vcpu) |
| Cannot deploy in a newly-released region | § [DEPLOY-Region-NotRegistered](./playbook-G-deployment-deep.md#deploy-region-notregistered--cannot-deploy-in-new-region) |
| `MissingSubscriptionRegistration` (RP not registered for sub) | § [DEPLOY-Reg-Missing](./playbook-G-deployment-deep.md#deploy-reg-missing--missingsubscriptionregistration) |
| `RequestDisallowedByPolicy` / `Forbidden` due to Azure Policy | § [DEPLOY-Policy-Denied](./playbook-G-deployment-deep.md#deploy-policy-denied--requestdisallowedbypolicy) |

#### Provisioning at deploy

| Symptom | Anchor |
|---|---|
| `OSProvisioningTimedOut` at FIRST create | § [DEPLOY-Provision-OSPTO](./playbook-G-deployment-deep.md#deploy-provision-ospto--osprovisioningtimedout-deploy-time) (cross-link Playbook B § OP-OSPTO for deeper guest RCA) |
| Linux VM OSPTO + `Wait for cloud-init to copy ovf-env.xml` / cloud-init never completes | § [DEPLOY-Provision-CloudInit](./playbook-G-deployment-deep.md#deploy-provision-cloudinit--cloud-init-failures-linux-ospto-subset) |
| Sysprep failed or stuck during cleanup phase (custom Windows image capture) | § [DEPLOY-Sysprep-Failed](./playbook-G-deployment-deep.md#deploy-sysprep-failed--sysprep-failed-or-stuck-generalizationstate-mitigation) |
| `OSProfile is not allowed when CreateOption is Attach` (specialized OS disk) | § [DEPLOY-Image-OSProfile](./playbook-G-deployment-deep.md#deploy-image-osprofile--cannot-set-osprofile-on-existing-osdisk-createoption-attach-vs-fromimage) |
| `VMRedeploymentFailed` customer-facing (retry pattern) | § [DEPLOY-Update-VMRedeploymentFailed](./playbook-G-deployment-deep.md#deploy-update-vmredeploymentfailed--vmredeploymentfailed-customer-facing) |
| VM stuck in Updating state / extension manifest download fails | § [DEPLOY-Update-VMStuckInUpdating](./playbook-G-deployment-deep.md#deploy-update-vmstuckinupdating--vm-stuck-in-updating-nsg--manifest) |

### Step 3 — Pull foundation evidence

Per `references/crp-queries.md`:
- `ApiQosEvent_nonGet` filtered by `correlationId` → `operationId`, `operationName`, `resultCode`, `errorDetails`, `requestEntity`, `labels`
- `ContextActivity` filtered by `activityId == "{OperationId}"` → verbose trace (preemption, service restart, allocation handler, image lookup, etc.)
- `CRPAllocationDetailsEtwTable` for placement / failure reason (allocation scenarios)

### Step 4 — Apply DEPLOY-* anchor logic

The deep file's per-anchor section provides: scope, KQL bodies, interpretation, mitigation, and customer-facing RCA wording where applicable.

### Step 5 — Cross-RP confirmation

| If symptom involves... | Also pull |
|---|---|
| ARM-side throttling | `armprodgbl` `HttpIncomingRequests` / `HttpOutgoingRequests` (macro-expand) |
| Marketplace purchase | `armprod*` `EventServiceEntries` + `MarketplaceTraces` (regional cluster macro-expand) |
| SIG/ACG image | `Azcsupfollower2.centralus.crp_allprod.PirCasApiQosEvent` + `PirCasContextActivityEvent` |
| CA/PA mapping | `aznwsdn.aznwmds.InterfaceProgramEndFiveMinuteTable` + `DCMLNMPubSubTaskEventEtwTable` |
| Capacity Reservation | `azureallocator.westcentralus.AzureAllocator` + `azcrpbifollower.bi_allprod.CapacityReservation` |
| ODCR SKU block | `azcrpeus.casprod.CasAdminOfferRestrictionsBlockList` |
| Hibernation extension | `azcore.centralus.Fa.GuestAgentExtensionEvents` |
| Disk lifecycle at deploy | `disks.kusto.windows.net.Disks` (see Playbook F + `references/disks-queries.md`) |

### Step 6 — Specialized tools

| Need | Tool |
|---|---|
| Visualize deployment time-distribution | Execution Graph: `http://aka.ms/egv?id={OperationId}` |
| CRP Throttling dashboard | Jarvis Diagnostics PROD → CRP namespace → ThrottlingContextActivity event |
| SKU availability check | ASC → any VM → Compute Capacity Advisory (CCA) tab |
| SKU restrictions per sub | ASC → Subscription → RP Details → SKU Restrictions; or ACIS GetResourceProviderSkusForSubscription |
| Look up Azure Policy on RG | ACIS `GetSubscriptionPolicyDefinitions` endpoint |
| Throttling Error Analyzer (customer-shareable) | https://docs.microsoft.com/en-us/azure/virtual-machines/troubleshooting/troubleshooting-throttling-errors#api-call-rate-and-throttling-error-analyzer |

### Step 7 — Customer reply + handoffs

| Scenario | Owner |
|---|---|
| Preemption / long-deploy explanation | Use canned RCA in § [DEPLOY-CRP-Preempted](./playbook-G-deployment-deep.md#deploy-crp-preempted--crp-operation-preempted-concurrent-ops) |
| CRP-side throttling (NOT customer-shareable limits) | Customer-enablement template in § [DEPLOY-CRP-Throttle](./playbook-G-deployment-deep.md#deploy-crp-throttle--crp-throttling-context-activity-internal-limits) — TA approval first |
| SKU whitelist / quota / capacity reservation allocation | **CCE (Capacity Customer Experience)** team — SAP `Azure/Service and subscription limits (quotas)/Compute-VM (cores-vCPUs) subscription limit increases - Azure Subscription limit/quota support ({Language}) - Non CSS` |
| ODCR SKU not allowed | **WACAP** team — ASC ICM template **M2N2J3** |
| Subscription / billing / marketplace purchase | **ASMS** team — SAP `Subscription management\Purchase, sign up or upgrade issues\Unable to make a purchase`. May engage **ACEEE** → Marketplace via IcM |
| Bad CA/PA mapping | **Cloudnet\Network Manager** team — IcM |
| ARM cache / RP-not-showing | **ARM team** — `Azure/Azure Resource Manager (ARM)/Resource Management/Resource not showing up` |
| AIB Azure Policy denial | **Azure Policy** team (via AVA / TA confirmation) |
| Confidential Computing (SGX/SEV-SNP) | **ACC team** — escalation template at `SME-Topics/Deployment/Azure-Virtual-Machine-ACC-Escalation-Template` |
| Hibernation Windows `powercfg` failure | **WSD CFE / HCCompute-Guest OS Health** |
| Hibernation non-powercfg extension failure | **AzureRT / Extensions** |
| 3rd-party Publisher Image | Per Publisher contact process (do NOT share contact with customer) + ASMS triage first |
| Live cases needing SME | **Deployment SME** or **Stop_Start SME** via Ava |

## Cross-references

| Other playbook / reference | Why |
|---|---|
| Playbook B § OP-* | Runtime CRP errors on existing resources (start/stop/restart/delete/redeploy/resize) — Playbook G ends, Playbook B begins, at the IsNew=True/False boundary |
| Playbook A § STG / NET / CPU / MEM | Restart RCA — once VM exists and rebooted |
| Playbook C § STG-Perf / NET-Perf | Performance on running VM (not deploy-time) |
| Playbook D § PM / LM / ADH | Maintenance + Live Migration + Dedicated Host — Playbook G cross-links here when Long Deployment overlaps with PM/LM window |
| Playbook E § VMSS-* | All VMSS-shape-specific deploy/scale/upgrade issues (Playbook G VMSS ACG anchor links here) |
| Playbook F § MD-* | Managed disk lifecycle (delete/resize/snapshot/recovery) on existing disks. Cross-link from Playbook G § DEPLOY-Disk-* and § DEPLOY-SA-* for deploy-time disk failures |
| `references/crp-queries.md` | Foundation for all CRP queries (ApiQosEvent, ContextActivity, CRPAllocationDetailsEtwTable) |
| `references/operations-queries.md` | ARM HttpIncomingRequests + EventServiceEntries macro-expand patterns |
| `references/vm-properties-queries.md` | EEE-style VM properties (HasManagedDisk, IsGen2, etc.) |
| `asap-storage-queries.md` | ASAP-related VM-stuck-during-create or guest-hang patterns on AMD v6/v7 SKUs (Playbook G § DEPLOY-Provision-OSPTO cross-links here) |
