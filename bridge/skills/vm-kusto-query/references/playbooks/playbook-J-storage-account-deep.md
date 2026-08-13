# Playbook J — Storage Account (Consolidated) — Deep

> **Companion to** [`playbook-J-storage-account-core.md`](./playbook-J-storage-account-core.md). Heavy delegate to [`references/storage-account-queries.md`](../catalogs/storage-account-queries.md) (581 lines / 30+ KQL — covers XStore/XArgus/XLivesite/PAV2 queries for SA properties, perf, billing, recovery, failover, throttling, Azure Files).
>
> 5 merged wiki areas:
> - `/SME Topics/Storage Account Management/...` — SA lifecycle, CMK, MI, network
> - `/SME Topics/Storage Billing/...` — billing inquiries, SKU change billing
> - `/SME Topics/Recover Storage Objects/...` — soft-delete / blob / container / file recovery
> - `/SME Topics/Unable to Delete Storage/...` — locks / immutability / migration blocking deletion
> - `/SME Topics/Azure Elastic SAN/...` — ESAN volume / volume group / iSCSI

## Cluster shortcuts

| Short | Full |
|---|---|
| `azcore.Xstore` | `cluster('azcore.centralus.kusto.windows.net').database('Xstore')` |
| `xstore.xstore` | `cluster('xstore.kusto.windows.net').database('xstore')` |
| `xargus.Production` | `cluster('xargus.centralus.kusto.windows.net').database('Production')` |
| `armprodgbl.ARMProd` | `cluster('armprodgbl.eastus.kusto.windows.net').database('ARMProd')` |
| `armprod-multi` | entity_group of `armprodeus.eastus` / `armprodweu.westeurope` / `armprodsea.southeastasia` (`ARMProd` DB) |
| `Azcsupfollower.crp_allprod` | `cluster('Azcsupfollower2.centralus.kusto.windows.net').database('crp_allprod')` |
| `rdfeprod.rdfeprodDB` | `cluster('rdfeprod.kusto.windows.net').database('rdfeprodDB')` |
| `azmsicl.azmsidb` | `cluster('azmsicl.kusto.windows.net').database('azmsidb')` (CoreIdentity MSI-Telemetry access required) |
| `xlivesite.XHealthDiskTriage` | `cluster('xlivesite.kusto.windows.net').database('XHealthDiskTriage')` |
| `Azcrpbi.bi_allprod` | `cluster('Azcrpbi.kusto.windows.net').database('bi_allprod')` |
| `xdataanalytics.XStore` | `cluster('XStore').database('xdataanalytics')` (alt: `cluster('xstore.kusto.windows.net').database('xdataanalytics')`) |
| `armprodgbl.ARMProd.Traces` | `armprodgbl.ARMProd` macro-expand → `Traces` DB |

## Anchor Index

### SA Management — Account state + lifecycle
- [`SA-Mgmt-StuckCreating`](#sa-mgmt-stuckcreating--storage-account-stuck-in-creating-state-accountbeingdeleted-or-exclusive-lock) — Storage Account Stuck in Creating State (AccountBeingDeleted OR exclusive lock)
- [`SA-Mgmt-OperationInProgress`](#sa-mgmt-operationinprogress--storageaccountoperationinprogress-error-concurrent-op-conflict) — `StorageAccountOperationInProgress` error (concurrent op conflict)
- [`SA-Mgmt-IncreaseLimits`](#sa-mgmt-increaselimits--increase-storage-account-capacity-limits-ingressegressiopstx) — Increase SA Capacity Limits (Ingress/Egress/IOPS/Capacity)
- [`SA-Mgmt-UnknownEncryptionKeySource`](#sa-mgmt-unknownencryptionkeysource--ssrp-metadata-inconsistency-update-fails-fixed-by-pg-scrub) — `UnknownEncryptionKeySource` (Emerging — SRP metadata inconsistency)
- [`SA-Mgmt-DiskSpaceCryptoException`](#sa-mgmt-diskspacecryptoexception--internalservererror-not-enough-space-on-disk-cmk-createupdate-cert-temp-file-leak) — `There is not enough space on the disk` (Emerging — CMK create/update cert temp-file leak)
- [`SA-Mgmt-502-BadGateway`](#sa-mgmt-502-badgateway--502-bad-gateway-microsoftstorage-failed-to-return-collection-response-sub-not-registered-in-new-region-rp-endpoint) — 502 Bad Gateway / `Microsoft.Storage failed to return collection response` (sub not registered in new region RP endpoint)
- [`SA-Mgmt-NotVisible`](#sa-mgmt-notvisible--storage-account-not-visible-in-portal-or-powershell-subscription-sync-issue--arm-sync-required) — SA Not Visible in Portal/PowerShell (subscription sync issue → ARM Sync required)
- [`SA-Mgmt-FailedToUpdate-AppId-Invalid`](#sa-mgmt-failedtoupdate-appid-invalid--failed-to-update-v1-sa-specified-app-id-not-valid-classic-to-arm-stuck-in-prepare) — Failed to update v1 SA `specified app id not valid` (Classic→ARM stuck in Prepare)
- [`SA-Mgmt-DoubleEncryption`](#sa-mgmt-doubleencryption--infrastructure-encryption-feature-create-time-only-not-disableable) — Infrastructure Encryption (Double Encryption) feature (create-time-only, not disableable)

### SA Management — Network + firewall
- [`SA-Mgmt-NetworkSourceDeleted`](#sa-mgmt-networksourcedeleted--networkacls-virtualnetworkrule-state-networksourcedeleted-ghost-subnet-acl) — `NetworkAclsNetworkSourceDeleted` (ghost subnet ACL after subnet recreate)

### SA Management — CMK (Customer-Managed Keys)
- [`SA-CMK-KVTokenCannotBeAcquired`](#sa-cmk-kvtokencannotbeacquired--keyvaultaccesstokencannotbeacquired-uami-deleted) — `KeyVaultAccessTokenCannotBeAcquired` (UAMI deleted, regenerate)
- [`SA-CMK-FailedToUpdate`](#sa-cmk-failedtoupdate--failed-to-update-mystorageaccount-pg-manual-patching-required) — `Failed to Update <SA>` (regression bug 2320437 — PG manual patching)
- [`SA-CMK-PowerShell-MissingParams`](#sa-cmk-powershell-missingparams--set-azstorageaccount-missing-pre-requisites-uami-3-extra-params-needed) — `Set-AzStorageAccount Missing pre-requisites` (UAMI needs `-IdentityType UserAssigned` + 2 more)
- [`SA-CMK-Conflict409`](#sa-cmk-conflict409--encryption-scope-invalid-conflict-409-encryptionscopenotavailable) — `Encryption scope invalid: Conflict 409` (EncryptionScopeNotAvailable)
- [`SA-CMK-ConfigSwitching`](#sa-cmk-configswitching--storage-encryption-with-cmk-configuration-switching-fails-kv-authentication-failure-5-step-deep-dive) — CMK Configuration Switching Fails (KV authentication failure 5-step deep dive + 4 key status table)
- [`SA-CMK-CrossTenant-DataPlane`](#sa-cmk-crosstenant-dataplane--cross-tenant-cmk-internalerror-500-kv-inaccessible-or-federated-mi-deleted) — Cross-Tenant CMK 500 (KV inaccessible / federated MI deleted)
- [`SA-CMK-CrossTenant-GatewayAuth`](#sa-cmk-crosstenant-gatewayauth--gateway-authentication-failed-for-microsoftstorage-invalid-federatedidentityclientid) — `Gateway authentication failed for 'Microsoft.Storage'` (invalid federatedIdentityClientId)
- [`SA-CMK-CrossTenant-KVKeyNotFound`](#sa-cmk-crosstenant-kvkeynotfound--keyvaultencryptionkeynotfound-3-causes-kv-deleted--rbac-incl-cmg--nsp-mismatch) — `KeyVaultEncryptionKeyNotFound` (3 causes: KV deleted / RBAC / NSP mismatch)
- [`SA-CMK-CrossTenant-403-500`](#sa-cmk-crosstenant-403-500--storage-blob-403-or-500-multi-tenant-app-or-fic-or-uami-deletion-4-sub-causes) — Storage Blob 403 or 500 (multi-tenant app / FIC / UAMI deletion — 4 sub-causes)

### SA Recovery
- [`SA-Recovery-Main`](#sa-recovery-main--master-recovery-scoping-tsg--csar-first--ad-cssstgapprovers-jit-elevation) — Master recovery scoping TSG (CSAR first + AD-CSSStgApprovers JIT elevation)
- [`SA-Recovery-QuickReference`](#sa-recovery-quickreference--ownership-routing-matrix-12-storage-object-types) — Recovery ownership routing matrix (12 storage object types)
- [`SA-Recovery-ARM`](#sa-recovery-arm--arm-storage-account-recovery-csar-first-then-icm) — ARM Storage Account Recovery (CSAR first, then ICM to XStore\Location Service)
- [`SA-Recovery-Classic`](#sa-recovery-classic--classic-storage-account-recovery-rdfe-based) — Classic SA Recovery (rdfe-based)
- [`SA-Recovery-BlobData`](#sa-recovery-blobdata--blob-data-recovery-dev-storage-owns-blob-recovery-asc-insight-first) — Blob Data Recovery (Dev Storage owns; ASC Blob Recovery Insight first; page blob = IaaS)
- [`SA-Recovery-Container`](#sa-recovery-container--container-recovery-dev-storage-owns-requires-geo-replication--sas-token-handling-rules) — Container Recovery (Dev Storage owns; requires geo-replication; strict SAS-token handling)
- [`SA-Recovery-FilesSMB`](#sa-recovery-filessmb--azure-files-smb-recovery-pg-via-icm-sev-3-only-jarvis-dgrep-investigation) — Azure Files SMB recovery (PG via ICM Sev 3 only; Jarvis DGrep investigation; NFS not recoverable)

### SA Delete — unable-to-delete TSGs
- [`SA-Delete-AccountIsLocked`](#sa-delete-accountislocked--accountislocked-vhdartifact-still-references-sa) — `AccountIsLocked` (VHD/artifact still references SA)
- [`SA-Delete-AccountProtected`](#sa-delete-accountprotected--classic-sa-accountprotectedfromdeletion-protection-lock) — Classic SA `AccountProtectedFromDeletion` (Protection lock)
- [`SA-Delete-AccountProtected-Detect`](#sa-delete-accountprotected-detect--determine-if-sa-is-protected-from-deletion-xlocation--dgrep-detection-methods) — Determine if SA is Protected from Deletion (XLocation + DGrep detection methods)
- [`SA-Delete-Blob`](#sa-delete-blob--unable-to-delete-blob-vhd--iaas-non-vhd--dev-storage) — Unable to Delete Blob (VHD = IaaS, non-VHD = Dev Storage)
- [`SA-Delete-BlobContainer`](#sa-delete-blobcontainer--unable-to-delete-blob-container-lease--immutability--changefeed--firewall) — Unable to Delete Blob Container (lease / immutability / `$blobchangefeed` / firewall)
- [`SA-Delete-FileShare`](#sa-delete-fileshare--unable-to-delete-azure-file-share-arm-lock-common-cause) — Unable to Delete Azure File Share (ARM lock common cause)
- [`SA-Delete-FileShare-BackupLock`](#sa-delete-fileshare-backuplock--azurebackupprotectionlock-auto-recreated-by-backup-policy) — `AzureBackupProtectionLock` (auto-recreated by Azure Backup policy)
- [`SA-Delete-Migrating`](#sa-delete-migrating--storage-account-in-process-of-being-migrated-classic-arm-not-committed) — SA in Process of Being Migrated (Classic→ARM not committed)

### SA Billing
- [`SA-Billing-SKUChange`](#sa-billing-skuchange--storage-sku-change-billing-30-day-grace-window-for-replication-conversions) — Storage SKU Change Billing (30-day grace window for replication conversions)
- [`SA-Billing-UltimateGuide`](#sa-billing-ultimateguide--storage-billing-cases-foundation-tsg--xstore_billingmodelini-glossary--3-toolsets) — Storage Billing Cases foundation TSG + `Xstore_BillingModel.ini` glossary + 3 toolsets (Xportal/ASI/Diagnostic Settings)
- [`SA-Billing-Foundations`](#sa-billing-foundations--general-sa-billing-investigation-delegated-to-storage-account-queriesmd) — General SA billing investigation (delegated to `storage-account-queries.md`)

### SA Utilities (foundation TSGs cross-linked from every error)
- [`SA-Util-LookupCRUD-CtrlPlane`](#sa-util-lookupcrud-ctrlplane--lookup-control-plane-sa-create-and-delete-operations-3-step-foundation-flow) — Lookup Control Plane SA CRUD ops (3-step foundation flow)
- [`SA-Util-QueryRSRP`](#sa-util-queryrsrp--query-storage-detailed-rsrp-logs-foundation-jarvis-dgrep-regionalsrp) — Query Storage detailed RSRP Logs (foundation Jarvis DGrep RegionalSRP)
- [`SA-Util-IdentifyBlobsActiveLease`](#sa-util-identifyblobsactivelease--identify-blobs-with-active-lease-foundation-for-vhd-lease-investigation-stamp-owned-locks-asc-jarvis-actions) — Identify Blobs with Active Lease (foundation for VHD lease investigation + Stamp Owned Locks + ASC + Jarvis Actions)

### Elastic SAN
- [`ESAN-Performance`](#esan-performance--high-latency--low-throughput-xstore-induced--shard-level-5000-iops-256-mbs-limit) — ESAN Performance (high latency / low throughput; shard-level 5000 IOPS / 256 MB/s limit)
- [`ESAN-Connectivity`](#esan-connectivity--iscsi-login-failed--io-timeouts-windows-event-157-vnet-acl-or-network) — ESAN Connectivity (iSCSI login fail / I/O timeouts Event 157 / VNET ACL or network)
- [`ESAN-DiskUnmount`](#esan-diskunmount--disk-unmount-unexpectedly-windows-failover-cluster-mpio-linkdowntime-30s) — Disk Unmount Unexpectedly (Windows Failover cluster MPIO — LinkDownTime 30s)
- [`ESAN-MDSnapshot-NotInitialized`](#esan-mdsnapshot-notinitialized--volume-from-md-snapshot-not-initialized-via-powershell-missing-creationdatacreatesource-flag) — Volume from MD snapshot not initialized (PowerShell missing `-CreationDataCreateSource` flag)
- [`ESAN-DataRecovery`](#esan-datarecovery--volume--volume-group--snapshot-soft-delete-recovery-10-day-retention) — Volume / Volume Group / Snapshot soft-delete recovery (10-day retention)
- [`ESAN-QuotaIncrease`](#esan-quotaincrease--quota-increase-only-max-esan-per-sub-region-supported-cap-iops-bw-not-customer-controllable) — Quota Increase (only Max ESAN per sub/region supported; cap / IOPS / BW not customer-controllable)
- [`ESAN-CheckConfiguration`](#esan-checkconfiguration--inspect-esan--vg--volume-properties-via-asc--jarvis-dgrep--jarvis-actions) — Inspect ESAN / VG / Volume properties via ASC + Jarvis DGrep + Jarvis Actions
- [`ESAN-EmergingIssue-ScaleOut`](#esan-emergingissue-scaleout--esan-scale-out-failing-aug-2024-canada-central-bug-hotfix-rolled-out) — ESAN Scale-Out failing (Aug 2024 Canada Central bug, hotfix rolled out)

---

## SA-Mgmt-StuckCreating — Storage Account Stuck in Creating State (AccountBeingDeleted OR exclusive lock)

### 2 root causes
1. **Same-name account recently deleted** — physical data GC takes **up to 14 days**. Recreating with same name fails with `AccountBeingDeleted`.
2. **Platform issue** — exclusive lock from a different operation.

### Triage flow

#### Step 1 — Find the recent failed operation
Use [Finding Storage CRUD Operations](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/496167) to identify the failing op. Capture `PreciseTimeStamp` + `CorrelationId`.

#### Step 2 — Pull detailed RSRP logs
Use [Query Storage RSRP Logs](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/2182782) with the captured timestamp + correlationId. Filter `TraceLevel <= 4`.

Look for one of:
- `Unable to acquire Exclusive Account lock 'SA'. Conflicting locks: <guid>[<timestamp>]`
- `Sending response: {"error":{"code":"StorageAccountInCreating","message":"Cannot delete the storage account while it is being created."}}`

#### Step 3a — If `StorageAccountInCreating`
1. Find last Creation Operation via Query Storage entry-level ARM RSRP Logs
2. Collect CorrelationId
3. Query detailed RSRP \u2192 look for:
   ```
   Account creation failed for account <SA> on stamp <stamp> with Error AccountBeingDeleted,
   Message: The specified account is in the process of being deleted but still physically exists.
   ```
4. Pull Storage Verbose Logs if RequestId matches
5. Escalate to PG with all 3 log dumps

#### Step 3b — If Exclusive Lock
Query RSRP again with the **conflicting lock's** PreciseTimeStamp + CorrelationId. If `AccountBeingDeleted` \u2192 customer must either pick a different name OR wait up to 14 days for GC.

### Customer message
> The previous storage account with this name is still being garbage-collected (up to 14 days). Options: use a different name OR wait for GC to complete.

---

## SA-Mgmt-OperationInProgress — `StorageAccountOperationInProgress` Error (concurrent op conflict)

**Symptom**: SA create/update/delete fails with `StorageAccountOperationInProgress`.

**Cause**: A previous op (often a long-running encryption or migration op) is still in flight.

**Mitigation**: Wait. Use `storage-account-queries.md` § Storage Account Recovery (SKU change/migration tracking) to identify the in-flight op via `armprodgbl.ARMProd.HttpOutgoingRequests` filtered to `targetUri contains '<SA>'` + `operationName contains 'AccountMigrations'`.

If no in-flight op visible after 24h → PG escalation.

---

## SA-Mgmt-IncreaseLimits — Increase Storage Account Capacity Limits (Ingress/Egress/IOPS/TX)

### ICM template
`https://portal.microsofticm.com/imp/v3/incidents/create?tmpl=O2tP1h`

### Hard rules

| Rule | Detail |
|---|---|
| **Current usage must exceed public targets** | [Scalability targets for standard accounts](https://learn.microsoft.com/en-us/azure/storage/common/scalability-targets-standard-account) |
| **5 PiB is a SOFT limit** | Capacity increase only needed at **15 PiB** (transfer to XStore/Capacity Management) |
| **NO sub-minute throttling increase** | Only sustained high usage. Direct to [retry guidance](https://learn.microsoft.com/en-us/azure/architecture/best-practices/retry-service-specific#azure-storage) |
| **Regional accounts** | 200 Gbps Ingress/Egress per 1 PB stored. Below 1 PB stored = NOT approved. Exception requires Jurgen Willis OR Maneesh Sah approval. |
| **1 SA per ICM** | For Bandwidth/TPS requests, file separate ICMs per account. |

### Mandatory info per ICM
- Customer contact (Name / Email / Company / Phone)
- 5 questions:
  1. Current usage evidence (TB/PB / Gbps / IOPS) — screenshots OK
  2. Throttling impact + desired experience; timestamps if errors
  3. Production vs Test vs PoC? PoC timeframe?
  4. Workload characteristics (e.g., ML 100 Gbps from 100 nodes; transactional batch)
  5. Growth projections at 30d / 90d / 6mo / 1yr

### Note — Firewall rule count increase
For SA firewall **number of rules** increase, see [Storage Account Firewall TSG](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/496118/Firewall-and-Virtual-Networks-Workflow_Storage?anchor=public-ip-whitelisting).

---

## SA-Mgmt-UnknownEncryptionKeySource — SRP metadata inconsistency (update fails, fixed by PG scrub)

**Symptom**: SA update fails with `UnknownEncryptionKeySource`. ASC shows NO encryption settings for the SA.

Failed-op trace:
```
SubStatus: BadRequest
ErrorCode: UnknownEncryptionKeySource
ErrorMessage: is not a known encryption key source.
```

**Root cause**: SRP code bug accepted an update in the past that cleared **immutable** metadata properties. Data plane wasn't updated to match → SRP rejects further updates.

**Mitigation**: PG already deployed fix + proactively scrubbing affected accounts. If customer still affected: ICM (ref: 272642511 / 256576594 / 269061401).

---

## SA-Mgmt-DiskSpaceCryptoException — `InternalServerError: Not enough space on disk` (CMK create/update cert temp-file leak)

**Symptom**: Cannot CREATE or UPDATE SA with CMK:
```
SubStatus: InternalServerError
ErrorCode: UnexpectedException
Exception: System.Security.Cryptography.CryptographicException: There is not enough space on the disk.
```

**Root cause (INTERNAL — do not share)**: Loading certificates during the operation creates temp files that aren't deleted → disk fills up. PG investigating.

### Identify
ASC → Operations → SRP Operations (for the SA, or at Subscription level for new accounts). Look for exact exception:
```
System.Security.Cryptography.CryptographicException: There is not enough space on the disk.
at StorageResourceProvider.Common.SrpUtilities.ConstructIdentityCertificate ...
```

**Mitigation**: PG manual intervention required. Escalate to EEE/PG. ICM ref: 529542316.

---

## SA-Mgmt-NetworkSourceDeleted — `NetworkAcls VirtualNetworkRule ... state NetworkSourceDeleted` (ghost subnet ACL)

### Symptom
Adding subnet to SA Selected Networks fails:
```
Failed to save firewall and virtual network settings for storage account 'SA'.
Error: NetworkAcls VirtualNetworkRule VNet/Subnet with state NetworkSourceDeleted in accounts <OtherSA>
is required to be removed before it can be added again.
```
Error code: `NetworkSourceDeleted`

### Cause
Subnet (or VNet+Subnet) deleted and recreated using the same name. Original firewall record in OLD SA was NOT auto-removed (ghost record) — compliance reasons require customer consent for cleanup.

### Investigation

#### KQL 1 — find failed op with `NetworkAclsNetworkSourceDeleted`
```kusto
let Clusters = entity_group [
    cluster("https://armprodeus.eastus.kusto.windows.net"),
    cluster("https://armprodweu.westeurope.kusto.windows.net"),
    cluster("https://armprodsea.southeastasia.kusto.windows.net")
];
macro-expand isfuzzy=true Clusters as ARMProd (
    ARMProd.database("Requests").EventServiceEntries
    | where resourceUri has "/{StorageAccountName}"
    | where operationName has_any ("Microsoft.Storage", "Microsoft.ClassicStorage")
    | where operationName !has_any ("LISTKEYS", "AUDIT/ACTION")
    | where PreciseTimeStamp >= ago(24h)
    | where properties has "NetworkAclsNetworkSourceDeleted"
    | project PreciseTimeStamp, resourceUri, operationName, status, properties, correlationId, claims
)
```

#### KQL 2 — find the subnet DELETE operation
```kusto
cluster("armprodgbl.eastus.kusto.windows.net").database("ARMProd")
| macro-expand isfuzzy=true ARMProdEG as X (
    X.database("Requests").HttpIncomingRequests
    | where subscriptionId == "{SubscriptionId}"
    | where PreciseTimeStamp >= ago(1d)
    | where targetUri contains "{SUBNET_NAME}"
    | where httpMethod == "DELETE"
    | project PreciseTimeStamp, operationName, httpMethod, httpStatusCode, targetUri, userAgent, correlationId
)
```

### Identify all SAs holding the ghost ACL
Jarvis: https://jarvis-west.dc.ad.msft.net/41C44AF1 — fill SubId (+ region), search `NetworkSourceDeleted` → each entry = SA still holding the old subnet record.

### Mitigation
Customer manually removes the ACL with `NetworkSourceDeleted` from EACH affected SA.

### Customer message
> The error is a ghost ACL record left when a subnet with the same name was previously deleted. Due to compliance, we cannot auto-clean these records. Please remove the ACL with state `NetworkSourceDeleted` from the storage accounts listed in the error message.

---

## SA-CMK-KVTokenCannotBeAcquired — `KeyVaultAccessTokenCannotBeAcquired` (UAMI deleted)

### Symptom
Blob access fails (403):
```
KeyVaultAccessTokenCannotBeAcquired
... Unable to acquire an access token for Key Vault from Azure Active Directory using the identity of this resource ...
(XFEHybridBlob.exe: KeyVaultUnableToGetAadTokenException)
```
Pull via [Query Storage Verbose Logs](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/690091).

### Root cause
User-assigned MI on the SA has been **deleted**.

### Investigation

#### Get the UAMI ID from ASC
ASC → Storage Account → Managed Identity → User Assigned Identity →
`/subscriptions/<sub>/resourcegroups/<rg>/providers/microsoft.managedidentity/userassignedidentities/<UAMI>`

#### Verify deletion via azmsicl
```kusto
cluster('azmsicl.kusto.windows.net').database('azmsidb').OperationEvent
| where env_time > ago(14d)
| where operationName contains "delete" or operationName contains "put"
| where resourceType == "microsoft.managedidentity"
| where resourceId contains "{userassignedidentityname}"
| project env_time, operationName, operationType, callerIpAddress, resultSignature,
          resultType, resultDescription, resourceType, UserAgent, resourceId, TenantId
```
Look for `IdentityDeleteRequest` event.

### Mitigation
1. Customer regenerates the managed identity
2. Re-link UAMI to SA per [Configure CMK for an Existing Account](https://learn.microsoft.com/en-us/azure/storage/common/customer-managed-keys-configure-cross-tenant-existing-account#configure-customer-managed-keys-for-an-existing-account)

Cross-link: Playbook H § SSE-MSINotFound is the equivalent for the **CMK Storage Account** managed identity (slightly different scope).

---

## SA-CMK-FailedToUpdate — `Failed to Update <SA>` (PG manual patching required)

### Symptom
`Failed to Update <storage-account-name>` when enabling CMK from Portal/PS. KeyVault is OK (Fiddler shows KV 200 OK); failure is in the Storage call.

### Investigation (5-step)

| Step | Action |
|---|---|
| 1 | Collect Fiddler / Browser HAR trace |
| 2 | Fiddler analysis — prove KV call succeeded; Storage call failed |
| 3 | ARM Kusto: query `armprodgbl` HttpIncomingRequests filtered to SA name; pick correlationId of failing PUT |
| 4 | DGrep in Jarvis with correlationId: `https://jarvis-west.dc.ad.msft.net/1562DA7C`. If no failure here but only in Step 3 → ARM-side issue. |
| 5 | SrpTool inspect: `Get-RsrpAccount` → `$account.internalProperties`. Known regression: `$account.internalProperties.encryptionKeys[1].value` returns NULL. |

### Mitigation
**Product regression — ADO bug `2320437`**. Storage account requires **manual patching by PG**.

File ICM with SA details + reference bug 2320437. Engage XStore Triage:
- Anthony Kunnel Jose `Anthony.Kunnel@microsoft.com`
- Priyaranjan Pandey `priyapan@microsoft.com`

---

## SA-CMK-PowerShell-MissingParams — `Set-AzStorageAccount` Missing pre-requisites (UAMI needs 3 extra params)

### Symptom
```
Set-AzStorageAccount : Missing pre-requisites to enable EncryptionAtRest/Customer Managed Key for this storage account.
For more information, see - https://aka.ms/storagecmkconfiguration
```
Works via Portal but fails via PowerShell.

### Cause
Public doc only shows the system-assigned MI parameter set. For **user-assigned MI**, must add 3 extra params.

### Mitigation
```powershell
Set-AzStorageAccount -ResourceGroupName $rgName `
    -AccountName $accountName `
    -KeyvaultEncryption -KeyName $key.Name `
    -KeyVaultUri $keyVault.VaultUri `
    -IdentityType UserAssigned `
    -UserAssignedIdentityId $userIdentity.Id `
    -KeyVaultUserAssignedIdentityId $userIdentity.Id
```
Ref: https://learn.microsoft.com/en-us/powershell/module/az.storage/set-azstorageaccount?view=azps-9.2.0#example-15-update-a-storage-account-to-keyvault-encryption-and-access-keyvault-with-user-assigned-identity

---

## SA-CMK-Conflict409 — `Encryption scope invalid: Conflict 409` (EncryptionScopeNotAvailable)

### Symptom
Uploading file to container fails: `The given encryption scope is invalid: Conflict 409`

### Investigation (4-step)
1. ASC → encryption scopes \u2192 verify source = Microsoft.KeyVault + Enabled
2. ASC → XDiagnostics → failed transactions. Look for:
   ```
   Role: Nephos.Blob
   Status: EncryptionScopeNotAvailable
   Operation: GetBlobMetadata / PutBlob
   InternalStatus: SASClientOtherError
   HttpStatusCode: 409
   ActivityId: <guid>
   ```
3. If not in ASC: Fiddler / Browser HAR or [Xportal autoanalysis](https://xportal.trafficmanager.net/autoanalysis/report/79bbb530-cda9-4b1b-971a-e9bd6d7acbe3?environment=Production)
4. Check SA is configured for CMK (not MMK)

### Mitigation
Configure SA to use **CMK** instead of MMK; select the KV with desired keys.

---

## SA-CMK-CrossTenant-DataPlane — Cross-Tenant CMK 500 (KV inaccessible / federated MI deleted)

### Symptom
Accessing CMK-encrypted blob fails:
```
InternalError | Server encountered an internal error. Please try again after some time.
RequestId: xxxxxxxx-701e-0082-5811-xxxxxxxxxxxx
```

### Cause (2 sub-causes)
1. `federatedIdentityClientId` (multi-tenant app registration) on the SA is invalid OR deleted
2. User-assigned MI on the SA is deleted OR misconfigured

### Investigation
- DGrep: https://portal.microsoftgeneva.com/s/4D66A766
- XDS via ASC/XPortal with ActivityID: sample [Xportal report](https://xportal.trafficmanager.net/autoanalysis/report/0d1c6fc8-4a3a-4029-836b-db4325af9f61?environment=Production)

### Error chain signature
```
XFEHybridBlob.exe: UnexpectedXStoreError ...
StorageManagerException: The Customer Managed Key is not available on the storage account.
  ---> Cannot read access token from azure active directory
  ---> System.Net.WebException: The remote server returned an error: (401) Unauthorized
```

### Resolution
Engage **Authentication - Application Experiences** team to recover the multi-tenant app registration OR the user-assigned MI.

---

## SA-CMK-CrossTenant-GatewayAuth — `Gateway authentication failed for 'Microsoft.Storage'` (invalid federatedIdentityClientId)

### Symptom
New SA creation with cross-tenant CMK fails:
```
Gateway authentication failed for 'Microsoft.Storage'.
```
SRP log:
```
[AAD] Authentication provider caught exception: AADSTS700016: Application with identifier '<appId>'
was not found in the directory 'Default Directory'.
```

### Investigation
- DGrep SRP failures: https://portal.microsoftgeneva.com/s/B11BD0DE → grab Operation ID
- Full SRP log via Operation ID: https://portal.microsoftgeneva.com/s/B684B832

### Resolution
Customer must use a valid `federatedIdentityClientId`. Engage **Authentication - Application Experiences** if needed.

---

## SA-CMK-CrossTenant-KVKeyNotFound — `KeyVaultEncryptionKeyNotFound` (3 causes: KV deleted / RBAC incl. CMG / NSP mismatch)

### Symptom
```
The key vault key is not found to unwrap the encryption key. (KeyVaultEncryptionKeyNotFound)
```

### 3 root causes
1. KV Key does not exist (deleted)
2. **Lack of RBAC perms** including the **CMG (Cloud Management Gateway)** scenario: when MMK→CMK switch happens on a CMG-managed resource, the access policy auto-reverts and SA loses access
3. SA is part of an **NSP (Network Security Perimeter)** but KV is outside the perimeter

### Resolution flow
1. ASC → Resource Explorer → SA → Encryption → note KV URI / Key Name / Key Version
2. ASC → lookup KV. If KV missing → [Restore Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/general/key-vault-recovery); else collab with **Azure Key Vault CSS team** (SAP: `Azure\Key Vault\Key Vault Administration\Key Vault Recovery (Soft Delete & Purge Protection)`)
3. Validate Key still exists. If deleted → [Restore KV Key](https://learn.microsoft.com/en-us/azure/key-vault/general/key-vault-recovery); else collab with KV team (SAP: `Azure\Key Vault\Managing Keys\Azure storage encryption (CMK)`)
4. Key exists → verify SA's MI has **Key Vault Crypto Service Encryption User** RBAC role
5. **CMG case**: once access granted, IMMEDIATELY switch encryption back from CMK → MMK (CMG-managed encryption changes are unsupported)
6. Check if SA is part of NSP per `/SME-Topics/.../How-to-check-NSP-configuration_Storage`. If yes, associate KV with same NSP.

---

## SA-Recovery-QuickReference — Ownership routing matrix (12 storage object types)

| Storage Object | Recovery Possible? | Owner | TSG |
|---|---|---|---|
| **Storage Account (ARM)** | Best effort | CSS → PG only if issues | Try [CSAR](https://docs.microsoft.com/en-us/azure/storage/common/storage-account-recover) first → ICM (this playbook § SA-Recovery-ARM) |
| **Storage Account (Classic)** | Best effort | CSS → PG | § SA-Recovery-Classic |
| **Managed Disk** | Best effort | CSS → PG | Playbook F § MD-Delete |
| **File Share — SMB** | Best effort | PG via ICM | § SA-Recovery-FilesSMB |
| **Files/folders from existing SMB share** | Best effort | PG via ICM | § SA-Recovery-FilesSMB |
| **Files / File Share — NFS** | **NO** | n/a | Customer must use Soft Delete + [NFS Snapshots](https://learn.microsoft.com/en-us/azure/storage/files/storage-snapshots-files?tabs=portal#nfs-file-share-snapshots) |
| **Files/folders from existing VM disk** | **NO** | n/a | Azure Backup for VMs OR Managed Snapshots |
| **HNS / ADLS Gen2 files/folders** | Best effort | **Dev Storage PaaS** | [Dev Storage ADLS Gen2 TSG](https://supportability.visualstudio.com/AzureDev/_wiki/wikis/Dev_Storage/1832930) |
| **Page Blob / unmanaged disk** | Best effort | PG via ICM (IaaS) | § SA-Recovery-BlobData (page blob path) |
| **Block Blob** | Best effort | **Dev Storage PaaS** | [Dev Storage TSG](https://supportability.visualstudio.com/AzureDev/_wiki/wikis/Dev_Storage/1832798) |
| **Container** | Best effort | **Dev Storage PaaS** | § SA-Recovery-Container |
| **Table** | Best effort | **Dev Storage PaaS** | — |
| **Queue** | **NO** | n/a | n/a |

### Best practices to share with customer
[Data Protection Overview](https://docs.microsoft.com/en-us/azure/storage/blobs/data-protection-overview)

---

## SA-Recovery-ARM — ARM Storage Account Recovery (CSAR first, then ICM)

### Order of attempts
1. **CSAR (Customer Controlled Storage Account Recovery)** — ALWAYS try first
   - Public doc: https://docs.microsoft.com/en-us/azure/storage/common/storage-account-recover
   - Customer self-service via Portal (within retention window)
2. ONLY if CSAR fails → manual ICM workflow

### Find the deletion event
Use `storage-account-queries.md` § Storage Account Recovery → `Find ARM Storage Account Deletion Events` KQL on `armprodgbl.ARMProd.EventServiceEntries` filtered by SubID + SA name + `operationName has "/storageAccounts/delete"`.

### Required ICM info
- SA name + RG + Subscription + Region
- Deletion timestamp (from KQL)
- Business justification

### Routing
ASC → escalate → IcM template for Storage Account Recovery → **XStore\Location Service** team. Sev 3 typical; Sev 2 only if real outage.
Help moving ICM: Storage Account Recovery Team `CSSStgRec@microsoft.com`.

---

## SA-Recovery-Classic — Classic Storage Account Recovery (rdfe-based)

### Find deletion event
Use `storage-account-queries.md` § `Find Classic Storage Account Deletion Events` KQL. Filter `resourceProvider has "Microsoft.ClassicStorage"` in ARMProd.EventServiceEntries.

### Workflow
Same as ARM — try CSAR-equivalent first (most Classic SA recovery is via PG manual restore). Note: Classic SA retirement is ongoing; recommend customer migrate to ARM if they still need long-term storage.

---

## SA-Recovery-BlobData — Blob Data Recovery (Dev Storage owns; ASC Blob Recovery Insight first; page blob = IaaS)

### ⚠ Scope transfer (2023)
**Block Blob + Container recovery is owned by Dev Storage PaaS team**, NOT IaaS.
- Dev Storage TSG: https://supportability.visualstudio.com/AzureDev/_wiki/wikis/Dev_Storage/1832798/Recover-Blob-Data
- IaaS team still owns: **Unmanaged disk (page blob)** recovery

### Check if ADLS Gen2 (HNS)
ASC → SA Summary → Configurations → `Data Lake Storage Gen2 Hierarchical Enabled`. If **Enabled** → use [Recover ADLS Gen2 TSG](https://supportability.visualstudio.com/AzureDev/_wiki/wikis/Dev_Storage/1832930) (Dev Storage); SAP: `Data Lake Storage Gen2\Deletion and Recovery\Recover ADLS Gen2 Data`.

### Recovery hard constraints
- Valid business justification
- No new blob created with same name
- Standard: deleted **≤ 6 days ago**
- Premium: deleted **< 3 days ago**
- Full blob path + deletion time
- Recovery chances drop SIGNIFICANTLY after 1–2 days

### Process — always use Blob Recovery ASC Insight first
ASC → Resource Explorer → SA → Blob tab → **Blob/Container Deletion Lookup & Recovery** → Run. Recommended Actions auto-creates ICM if recovery is possible. See [Blob Recovery ASC Insight TSG](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/692892).

### Manual ICM route (only if ASC Insight fails)
SAP: **Azure\Blob Storage\Deletion and Recovery\Recover Blob Data**
- Sev 3/4 → **EEE**
- Sev 2 → **XStore\GC** (requires Storage TA to move ICM)

---

## SA-Recovery-Container — Container Recovery (Dev Storage owns; requires geo-replication; strict SAS-token handling)

### ⚠ Scope transfer (2023)
Container recovery is **Dev Storage PaaS team** — NOT IaaS.

### HARD constraint — LRS = NO recovery
Container recovery requires **geo-replication** (GRS / RAGRS / GZRS / RAGZRS). If SA is LRS → tell customer recovery is NOT possible.

### ADLS Gen2 check
Same as Blob recovery — if HNS enabled → use ADLS Gen2 TSG.

### 6-step workflow
1. ASC → Blob/Container Deletion Lookup & Recovery → Run with container name + time window
2. Customer changes replication to **Read Access** (RA-GRS) if not already
3. Customer creates **container-level SAS token**:
   ```powershell
   $storageAccount = "<name>"; $storageKey = "<key>"
   $ctx = New-AzureStorageContext -StorageAccountName $storageAccount -StorageAccountKey $storageKey
   $startTime = Get-Date; $endTime = $startTime.AddMonths(1)
   New-AzureStorageContainerSASToken -Name "<containerName>" -Permission rl `
     -StartTime $startTime -ExpiryTime $endTime -Context $ctx -FullUri
   ```
4. Customer designates **destination account** (must be DIFFERENT from source)
5. Customer creates **account-level SAS token** for destination:
   - Allowed services: Blob
   - Resource types: Service + Container + Object
   - Permissions: Read + Write + Delete + List + Add + Create
   - Expiration: ≥ 2 weeks
6. File ICM via ASC → selects **container recovery** → routes to **XStore\Location Service**

### ⚠ SAS Token handling rules
- SAS tokens go via **email to engineer ONLY** — NOT in ICM details, NOT in case notes
- Help moving ICM: Storage TAs or `CSSStgRec@microsoft.com`

### Required ICM info
SA name + type + replication + container name(s) + approximate deletion time

---

## SA-Recovery-FilesSMB — Azure Files SMB recovery (PG via ICM Sev 3 only; Jarvis DGrep investigation)

### Hard rules
- **SMB ONLY** — NFS not supported (use NFS snapshots instead)
- Deleted **≤ 6 days ago**
- Resource-intensive, takes multiple days, requires business justification
- Best-effort, no SLA; **does NOT qualify for Sev 2** even if customer escalates
- If the SA itself was deleted: do § SA-Recovery-ARM FIRST
- Check for active Backup or Snapshots first — if present, recover from there

### Investigate deletion event via Jarvis DGrep (NOT Kusto)
[Jarvis/MDM link](https://portal.microsoftgeneva.com/s/A6816406) → Logs section:
```
Namespace: Xstore
Events: DiagnosticAuditLog, DiagnosticAuditTable
Tenant: <StorageCluster>
Role: XSmbServer, Nephos.File, XNfsServer
Filter: ownerAccountName == <SA>, objectKey contains <deleted-path>
```

Key columns:
- **Category / OperationName**: SMB = `StorageDelete/Close` ; NFS = `StorageDelete/Nfs4Remove` (NFS = NOT recoverable)
- **requestId**: Storage ActivityId
- **requestUrl / objectKey**: deleted path
- **UserAgent**: client (.NET / PS / az CLI)
- **CallerIPAddress**: IP+port (IPv6 → convert via ASC → SA tab → Tools)

### ICM submission
- ASC template → **Sev 3 ONLY**
- Include: business justification, SA name, file share name, target type (share / dir / files), full path, deletion time
- Urgent: contact DRI of SMB team or `xsmbincidents@microsoft.com`

---

## SA-Delete-AccountIsLocked — `AccountIsLocked` (VHD/artifact still references SA)

### Symptom
```
code: AccountIsLocked
Message: The storage account cannot be deleted due to its artifacts being in use.
For more information on troubleshooting this issue, see
https://azure.microsoft.com/documentation/articles/storage-cannot-delete-storage-account-container-vhd/
```

### Investigation
```kusto
let sub = "{SubscriptionId}";
let start = datetime({StartTime});
let end   = datetime({EndTime});
cluster("armprodgbl.eastus.kusto.windows.net").database("ARMProd")
| macro-expand isfuzzy=true ARMProdEG as X (
    X.database("Requests").EventServiceEntries
    | where PreciseTimeStamp between (start..end)
    | where subscriptionId == sub
    | where operationName == "Microsoft.Storage/storageAccounts/delete"
    | where status == "Failed"
    | where properties contains "AccountIsLocked"
    | project PreciseTimeStamp, correlationId, operationName, properties, resourceUri
    | take 1
)
```

### Mitigation
Follow [Storage resource deletion errors](https://docs.microsoft.com/en-us/azure/virtual-machines/troubleshooting/storage-resource-deletion-errors) to find the referencing artifact (typically unmanaged VM VHD).

If NO artifacts found referencing the SA → **file ICM** — CRP on-call must manually edit CRP KVP data (ICM precedent 145650914).

---

## SA-Delete-AccountProtected — Classic SA `AccountProtectedFromDeletion` (Protection lock)

### Symptom
Classic SA op fails:
```
'<SA>': Encountered an internal server error. The tracking id is '<guid>'. (Code: InternalServerError).
```
Internal: `The specified account is protected from deletion (AccountProtectedFromDeletion)`.

### Cause
Classic SA has a **Protection lock** enabled.

### Investigation — Jarvis DGrep (NOT Kusto)
```
Namespace: Rdfe
Events: ServiceContextActivityEtwTable, RdfeExceptionEventEtwTable
Filter: OperationId == <OperationId>
```
Filter `Trace <= 4`. Look for:
```
XLS Error: Conflict - AccountDeletionConflict ...
<Code>AccountProtectedFromDeletion</Code><Message>The specified account is protected from deletion</Message>
```

### Resolution
If error == `AccountProtectedFromDeletion` → escalate per `/Unable-to-Delete-Workflow` § Product Engineering Escalation.

### Case coding
`Root cause - Azure Storage\Storage Account Management\Account deletion issue\Delete protection lock`

---

## SA-Delete-BlobContainer — Unable to Delete Blob Container (lease / immutability / `$blobchangefeed` / firewall)

### ⚠ Scope
Blob Container delete is owned by **Dev Storage** team (2023 scope transfer).

### Error → root cause table

| Error message | Cause | Action |
|---|---|---|
| `There is currently a lease on the container and no lease ID was specified` | Active lease on container/blobs | [Identify Blobs with Active Lease](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/496150) → break lease |
| `ContainerProtectedFromDeletion ... ImmutabilityPolicy` | Time-based retention immutability | [Remove Time-Based Retention](https://supportability.visualstudio.com/AzureDev/_wiki/wikis/Dev_Storage/1832444) (Dev Storage) |
| `'$blobchangefeed' is a system container and it cannot be deleted` | Blob change feed enabled — system container is READ-ONLY | Customer controls retention only; container cannot be deleted. Does NOT block SA deletion. |
| `No Access (403)` | SA Firewall enabled and caller IP not whitelisted | [Whitelist Public IP](https://docs.microsoft.com/en-us/azure/storage/common/storage-network-security#grant-access-from-an-internet-ip-range) |
| Other | — | Advanced TS via Storage Verbose logs |

### Triage flow
1. ASC Insights
2. Query Storage FrontEnd logs → collect Error Message + Error Code + TimeFrame + ActivityId
3. Look up error in table above
4. If not found → Advanced TS (Storage Verbose logs) → PG escalation

---

## SA-Delete-Migrating — SA in Process of Being Migrated (Classic→ARM not committed)

### Symptoms
```
Unable to delete storage account 'SA': 'Storage account 'SA' is in the process of being migrated and hence cannot be changed.'.
(Code: StorageAccountOperationFailed).
```
OR `XrpMigrationInProgress` OR `AccountPendingMigrationToSrp`.

### Cause
Classic→ARM migration was started but **not committed**.

### Prereqs
- User is **Co-Administrator** (Classic Administrator role)
- [Install Az PS Service Management module](https://learn.microsoft.com/en-us/powershell/azure/servicemanagement/install-azure-ps)

### Commit migration
```powershell
Move-AzureStorageAccount -Commit -StorageAccountName <SA> -Debug
```

### If commit fails — Abort
```powershell
Move-AzureStorageAccount -Abort -StorageAccountName <SA> -Debug
```

### If "Storage account Not found"
1. Validate tenant: `Select-AzSubscription -SubscriptionName "abc" -TenantId "..."`
2. Verify via Kusto:
   ```kusto
   cluster('rdfeprod.kusto.windows.net').database('rdfeprodDB').CommitStorageServiceMigrationOperationEtwTable
   | where TIMESTAMP between (datetime({StartTime}) .. datetime({EndTime}))
   | where * contains "{StorageAccountName}"
   | project TIMESTAMP, EventName, MigrationPhase
   ```
3. Verify Classic Admin rights
4. Custom REST API fallback:
   ```powershell
   Set-AzContext -SubscriptionId <sub>
   $Token = "Bearer {0}" -f (Get-AzAccessToken -Resource "https://management.core.windows.net/").Token
   $headers = @{Authorization = $Token; 'x-ms-version' = '2016-03-01'}
   Invoke-RestMethod -Method Post -Headers $headers `
     -Uri "https://management.core.windows.net/<subId>/services/storageservices/<SA>/migration?comp=commit" `
     -UseBasicParsing -Verbose
   ```

### Review historical migration ops
```kusto
cluster('armprodgbl.eastus.kusto.windows.net').database('ARMProd')
| macro-expand isfuzzy=true ARMProdEG as X (
    X.database('Requests').HttpIncomingRequests
    | where subscriptionId == "{SubscriptionId}"
    | where httpMethod != "GET"
    | where targetUri contains "{StorageAccountName}"
    | where operationName endswith "Migration"
    | where PreciseTimeStamp >= now(-90d)
    | project PreciseTimeStamp, operationName, httpMethod, httpStatusCode, targetUri, correlationId, commandName
)
```

### Escalation
ASC → CRI; if ASC fails use [AzureRT IcM Template](https://aka.ms/CRI-AzureRT). Sev1/2 → PG; Sev3/4 → EEE.

---

## SA-Billing-SKUChange — Storage SKU Change Billing (30-day grace window for replication conversions)

### Customer complaint
Billed for **old SKU** for 30 days after converting (e.g., RA-GRS → LRS / GRS → LRS).

### Expected behavior (per public doc)
> If you remove read access to the secondary region (change from RA-GRS to GRS or LRS), that account is billed as RA-GRS for an additional **30 days** beyond the date that it was converted.

Ref: [Costs of changing replication](https://learn.microsoft.com/en-us/azure/storage/common/redundancy-migration?tabs=portal#costs-associated-with-changing-how-data-is-replicated)

### ASC discrepancy signal
- Storage Account **Summary** tab → shows NEW SKU (LRS)
- Capacity & Migration Status tab → still shows OLD SKU (RAGRS)

Discrepancy disappears once 30-day billing window completes.

### Patch vs Migration (different cost behaviors)
Per [Redundancy-Migration doc](https://learn.microsoft.com/en-us/azure/storage/common/redundancy-migration?tabs=powershell):
- Docs that mention **Azure Portal / PowerShell / CLI** → **patch** (immediate, no migration)
- Docs that mention **Perform a Conversion** → **migration** (internal data move)

### Investigation KQL

#### 1) Find migration / conversion start (HttpOutgoing AccountMigrations)
```kusto
let Clusters = entity_group [cluster("https://armprodeus.eastus.kusto.windows.net"),
  cluster("https://armprodweu.westeurope.kusto.windows.net"),
  cluster("https://armprodsea.southeastasia.kusto.windows.net")];
macro-expand isfuzzy=true Clusters as ARMProd (
  ARMProd.database("Requests").HttpOutgoingRequests
  | where subscriptionId == "{SubscriptionId}"
  | where operationName contains "AccountMigrations"
  | where targetUri contains "{StorageAccountName}"
  | project PreciseTimeStamp, ActivityId, operationName, correlationId,
            subscriptionId, armServiceRequestId, targetUri
)
```

#### 2) Patch operations (PATCH RP — immediate SKU swap)
```kusto
let Clusters = entity_group [cluster("https://armprodeus.eastus.kusto.windows.net"),
  cluster("https://armprodweu.westeurope.kusto.windows.net"),
  cluster("https://armprodsea.southeastasia.kusto.windows.net")];
macro-expand isfuzzy=true Clusters as ARMProd (
  ARMProd.database("Requests").EventServiceEntries
  | where subscriptionId == "{SubscriptionId}"
  | where resourceUri contains "{StorageAccountName}"
  | where TIMESTAMP between (datetime({StartTime}) .. datetime({EndTime}))
)
| project PreciseTimeStamp, subscriptionId, ActivityId, correlationId, operationName, customerOperationName, properties, httpRequest
```

### Customer message
> The 30-day extended billing is expected per public docs (RA-GRS retention after downgrade). Verify the conversion start date — if outside 30 days, escalate.

### Cross-references
- [Check Storage Account Redundancy Migration Status](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/929809)
- [Storage Account SKU change Copilot Storage](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/2165506)

---

## SA-Billing-Foundations — General SA billing investigation (delegated to `storage-account-queries.md`)

For non-SKU-change billing inquiries (capacity, transactions, billing meter breakdown, transaction count by request type, PAV2 meter lookup) — delegate to:

| Investigation | TSG / KQL location |
|---|---|
| Daily billing by meter | `storage-account-queries.md` § Storage Billing & Transaction Analysis → `XStoreAccountBillingDaily` |
| Filter specific MeterId | Same § — `XStoreAccountBillingDaily` with `MeterId == '{}'` |
| Daily transaction count by request type | Same § — `XStoreAccountTransactionsDaily` |
| Transaction details with access tier | Same § — `AccountTransactionsDaily` |
| Billing meter metadata lookup | Same § — `pav2data.aipusageaudit.AllMeters` |

Use Cases:
- "Why is my SA bill higher this month?" → `XStoreAccountBillingDaily` for the affected meter
- "What's `MeterId X`?" → `pav2data.aipusageaudit.AllMeters` for ProductName + SkuName
- "Why so many `ListBlobs` calls?" → `XStoreAccountTransactionsDaily` filter by `RequestType`

---

## ESAN-Performance — High latency / low throughput (XStore induced / shard-level 5000 IOPS 256 MB/s limit)

### Common causes
- **XStore induced**: degraded request processing OR throttling
- **Networking** (hard to pinpoint without client VM access)
- **Client-side bottleneck** (hard to pinpoint without client VM access)

### Investigation entry points
- [ESAN Perf Dashboard](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/1683509/Elastic-SAN-How-To_Storage?anchor=elastic-san-perf-dashboard)
- Shoebox metrics: [Tenant Level](https://xportal.trafficmanager.net/sla/mdm/tenant/$/dashboards) / [Account Level](https://xportal.trafficmanager.net/sla/mdm/account/$/dashboards)
- DGrep: `FEExtendedPerfSummaryMetric` event table; note activity IDs
- XDS Log Search: deep-dive per activity ID

### KQL — latency histogram per 5-min (iSCSI ops)
```kusto
let _startTime = datetime('{StartTime}');
let _endTime = datetime('{EndTime}');
cluster("xargus.centralus.kusto.windows.net").database("Production").AccountPerfPercentiles5M
| where TimeWindow between (_startTime .. _endTime)
| where Operation in ("IscsiRead", "IscsiWrite")
| where Tenant == "{Tenant}"     // e.g. MS-LON23PrdStp03A
| where Account == "{Account}"   // e.g. aa-4aaaaaaaaaa40
```

Same KQL is in `storage-account-queries.md` § Elastic SAN Performance.

### Known issue (INTERNAL only — do NOT share)
Sequential workload bandwidth/IOPS throttling. Shard-level limits are **5,000 IOPS** and **256 MB/s** per shard — below volume-level scale targets ([Volume Scale Targets](https://learn.microsoft.com/en-us/azure/storage/elastic-san/elastic-san-scale-targets#volume-scale-targets): 1 GiB-64 TiB → 750-80,000 IOPS, 60-1280 MB/s). PG working on eliminating; no ETA.

### Resolution
Stripe multiple volumes (Windows Storage Spaces). Guide: [Deploy Storage Spaces](https://learn.microsoft.com/en-us/windows-server/storage/storage-spaces/deploy-standalone-storage-spaces).

---

## ESAN-Connectivity — iSCSI Login Failed / I/O timeouts (Windows Event 157 / VNET ACL or network)

### Symptom 1 — I/O timeouts AFTER login
Windows: disk unmounts on I/O timeout (**Event 157**). Initiator typically retries; if retry succeeds → I/O resumes; if retry fails → disk disappears (same path as login failure).

### Symptom 2 — iSCSI Login Failed (3 sub-causes)

| Failure | Common cause |
|---|---|
| Authentication Error / Access Denied | **VNET ACL misconfigured** |
| Target Error | Error during login processing at the target |
| Connection Failed | Network error OR target dropped the login |

### Debugging Auth + Target errors
Server-side telemetry exists for both — use XStore log traces.

### Debugging Connection Failed
**NO server-side logs.** Need client-side info:
- **Logs**: Windows Event Viewer / Linux syslog
- **Network tools**:
  - DNS: `nslookup`
  - Ping/Traceroute: PsPing (Win) / `tcp traceroute` (Linux)
  - Network trace: Wireshark / tcpdump → pcap

---

## ESAN-DiskUnmount — Disk Unmount Unexpectedly (Windows Failover cluster MPIO — LinkDownTime 30s)

### Symptom
Windows Failover cluster node restart takes down >1 path. iSCSI initiator fails to re-establish; MPIO tries failover to another failing path → disk unmounts.

### Resolution
Change iSCSI initiator session timeout (`LinkDownTime`) from **15s → 30s**.

Guide: [ESAN best practices iSCSI](https://learn.microsoft.com/en-us/azure/storage/elastic-san/elastic-san-best-practices#iscsi)

---

## ESAN-MDSnapshot-NotInitialized — Volume from MD snapshot not initialized (PowerShell missing `-CreationDataCreateSource` flag)

### Symptom
Creating ESAN volume from MD snapshot **via PowerShell** → disk shows as **not initialized**. Does NOT happen via Portal.

### Cause
PowerShell missing switch `-CreationDataCreateSource DiskSnapshot`.

### Mitigation
```powershell
New-AzElasticSanVolume ... -CreationDataCreateSource DiskSnapshot ...
```

### Verify via DGrep
Failure: request missing `CreateSource`; response shows `CreateSource: None`.
- Failure sample: https://portal.microsoftgeneva.com/s/3BB4556
- Success sample: https://portal.microsoftgeneva.com/s/BA3C26DD

---

## ESAN-DataRecovery — Volume / Volume Group / Snapshot soft-delete recovery (10-day retention)

### Scope
Internal soft-delete feature performed by **ESAN PG**. Granular file-level recovery NOT possible.

### Retention
**10 days** after deletion before permanent deletion.

### Workflow
1. From ASC: collect ESAN Resource ID + Region + Deletion date (Operations tab → deletion op → OperationID)
2. If deletion > 10 days ago → NOT recoverable
3. If within retention → ICM routed to **SAN RP team** with:
   - ESAN Resource ID
   - Region
   - Volume / Group / Snapshot name(s)
   - Deletion date + OperationID
4. VG recovery: customer must recreate VG with same name + encryption config
5. Volume / snapshot recovery: restore with same name; check no naming conflict

---

## ESAN-QuotaIncrease — Quota Increase (only Max ESAN per sub/region supported)

### Available quota increases (only ONE supported)

| Resource | Max | Increase supported? |
|---|---|---|
| Max ESAN per sub per region | **5** | **YES** |
| Capacity-only units (TiB) | Region-varies | No |
| Base capacity units (TiB) | Region-varies | No |
| Min total SAN capacity (TiB) | Region-varies | No |
| Max total IOPS | Region-varies | No |
| Max total throughput (MB/s) | Region-varies | No |

[Public scale targets](https://learn.microsoft.com/en-us/azure/storage/elastic-san/elastic-san-scale-targets)

### ICM template
Team: **ElasticSANRP**, Owning Service: **Xstore**.
Title: `Quota Increase for Customer Subscription | <case#>`
Include: company name, business justification, timeline, ESAN sub ID, region, current/requested ESAN count.

---

## ESAN-CheckConfiguration — Inspect ESAN / VG / Volume properties via ASC + Jarvis DGrep + Jarvis Actions

### ASC paths
- **ESAN properties + scalability limits**: Resource Explorer → ESAN → Summary tab → Properties + Scalability Limits
- **Volume Groups**: Resource Explorer → ESAN → Volume Group tab
- **Volumes**: Volume Group section → search by Volume Name → Volume properties

### Jarvis DGrep templates
[Combined ESAN/VG/Volume query](https://portal.microsoftgeneva.com/s/B9202605):
```
Endpoint: Diagnostics PROD
Namespace: ElasticSan
Events: ElasticSanStatisticsEvent, VolumeGroupStatisticsEvent, VolumeStatisticsEvent
Filter: SubscriptionId == <SubscriptionId>
```

Property objects:
- **ESAN** (`elasticSanStatistics`): `BaseSizeTB`, `ExtendedSizeTB`, `ProvisionedIops`, `ProvisionedMBps`, `TotalSizeTB`, `VolumeGroupCount`, `TotalSizeConsumed`, `AvailabilityZones`
- **VG** (`volumeGroupProperties`): `EncryptionType`, `ProtocolType`, `PrivateEndpointConnections`
- **Volume** (`volumeProperties`): `VolumeSize`, `StorageAccount`, `CreationSource`, `TargetIqn`, `StorageTargetState`, `TargetPortalHostname:Port` (default 3260)

### Jarvis Actions (requires SAW)
https://jarvis-east.dc.ad.msft.net/actions → filter `ElasticSAN` → 7 operations (Get ElasticSan, Get VolumeGroup, ...). Endpoint = Production.

---

## SA-Mgmt-502-BadGateway — 502 Bad Gateway / `Microsoft.Storage failed to return collection response` (sub not registered in new region RP endpoint)

### Symptoms
- HTTP 502 BadGateway with `ProviderError` / `Microsoft.Storage failed to return collection response for type '...'`
- Terraform / Portal Diagnostic Settings / SDK fail
- Alt RSRP signature: `{"error":{"code":"SubscriptionNotFound","message":"Subscription <subId> was not found."}}`

### Cause (INTERNAL)
New region in buildout — subscriptions NOT registered to that RP endpoint yet. ARM still tries to forward the call. Known issue.

### Investigation

#### Step 1 — collect correlationId
Customer-provided OR use [`SA-Util-LookupCRUD-CtrlPlane`](#sa-util-lookupcrud-ctrlplane--lookup-control-plane-sa-create-and-delete-operations-3-step-foundation-flow) to narrow down.

#### Step 2 — ARM Traces KQL
```kusto
macro-expand isfuzzy=true ARMProdEG as X
(
    X.database("Traces").Traces
    | extend $cluster = X.$current_cluster_endpoint
    | where PreciseTimeStamp >= datetime("{StartTime}") and PreciseTimeStamp <= datetime("{EndTime}")
    | where correlationId == "{correlationId}"
)
| project $cluster, PreciseTimeStamp, correlationId, operationName, message, exception
```
In `message` column look for `Region: <X>, Status: NotFound` — that's the affected region.

#### Step 3 — Verify RP registration status
**GME credentials** → Jarvis Action: Azure Resource Manager > Resource Provider Management > **Get subscription registration for a resource provider**. Look for the affected region missing from the RP endpoint registration list.

### Resolution

| Error | Condition | Action |
|---|---|---|
| `Subscription <id> was not found` | Sub truly doesn't exist | Customer error — check sub ID |
| `Subscription <id> was not found` | Sub truly DOES exist | Customer re-registers: `Register-AzResourceProvider -ProviderNamespace Microsoft.Storage` OR `az provider register --namespace 'Microsoft.Storage'`. SAW alt: Jarvis Action `Register resource provider (self service)` |

---

## SA-Mgmt-NotVisible — Storage Account Not Visible in Portal or PowerShell (subscription sync issue → ARM Sync required)

### Symptom
Customer cannot see SA in Portal / PowerShell / CLI, but can still access data within it.

### Cause
Subscription sync issue.

### Resolution flow (5 checks, do in order)

#### 1. Verify correct subscription
- **Portal**: change directory
- **PowerShell**: use correct cmdlet family — ARM uses `*Rm*` (`Install-Module AzureRM`, `Add-AzureRmAccount`, `Select-AzureRmSubscription`); Classic does not (`Install-Module Azure`, `Add-AzureAccount`, `Select-AzureSubscription`)

#### 2. Review owning subscription (Classic only)
[XPortal](https://xportal.trafficmanager.net/sla/mdm/account/$/metadata) → Basic Info tab → SA name → see metadata + subscriptionId.

#### 3. Double-check SA in target subscription
Jarvis: ARM → Resource Group Management → [Get resources from the subscription](https://jarvis-west.dc.ad.msft.net/CF9FDF8F).

#### 4. Validate Storage Provider registered on subscription
Jarvis: ARM → Resource Provider Management → [Get resource providers for a subscription](https://jarvis-west.dc.ad.msft.net/C113AD4C). Verify:
- ARM SA → `Microsoft.Storage` = `Registered`
- Classic SA → `Microsoft.ClassicStorage` = `Registered`

If `NotRegistered` → register it.

#### 5. Perform an ARM Sync (last resort, requires SAW)
Follow [How to perform an ARM Sync](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/748069/ARM-Storage-Account-Recovery_Storage?anchor=step-5%3A-arm-resource-sync).

**⚠ CRITICAL**: BEFORE running ARM Sync, verify if customer needs RCA — RCA may NOT be possible after sync. If RCA needed: collab with **ARM team** (SAP: `Azure/Azure Resource Manager (ARM)/Resource Management/Resource not showing up`). Do NOT route RCA to Compute/Storage EEE.

### Case coding
`Root Cause - Windows Azure\Azure Portal\Sync issue with the portal`

---

## SA-Mgmt-FailedToUpdate-AppId-Invalid — Failed to update v1 SA `specified app id not valid` (Classic→ARM stuck in Prepare)

### Symptom
Update of any config option fails for recently-migrated Classic-to-ARM v1 SA:
```
Failed to update v1 storage account. Error: The specified app id is not valid for the request.
```

### Cause
Classic SA migrated to ARM and transformed into SA v1, **stuck in Prepare state** — customer did NOT hit Commit button.

### Investigation
Activity Log → failed op → JSON → correlationId. Jarvis DGrep: https://portal.microsoftgeneva.com/s/35F7D729. Look for: `"migrationstate":"Prepare","provisioningState":"Succeeded"`.

### Mitigation
Customer hits **Commit** button on Classic SA. Or PowerShell:
```powershell
Import-Module Az
Connect-AzAccount
Select-AzureSubscription -SubscriptionName "<sub>"
Move-AzStorageAccount -Commit -StorageAccountName "<SA>"
```

Cross-link: [`SA-Delete-Migrating`](#sa-delete-migrating--storage-account-in-process-of-being-migrated-classic-arm-not-committed) covers the same Classic→ARM migration issue when blocking DELETE; this anchor covers the same issue when blocking UPDATE.

---

## SA-Mgmt-DoubleEncryption — Infrastructure Encryption (Double Encryption) feature (create-time-only, not disableable)

### Scope
Extra layer of encryption using platform-managed keys on top of MMK/CMK. **ONLY enableable at SA CREATE TIME**. Cannot be enabled on existing accounts. Cannot be disabled once on.

### Compatibility
- Only GPv2-pricing accounts (all kinds EXCEPT `Storage`)
- All public + Fairfax regions

### Verify subscription is signed up
Customer registration command:
```powershell
Register-AzProviderFeature -ProviderNamespace Microsoft.Storage -FeatureName AllowRequireInfrastructureEncryption
Register-AzResourceProvider -ProviderNamespace Microsoft.Storage
```
Jarvis Action: https://jarvis-west.dc.ad.msft.net/1C7878E7 — check `Microsoft.Storage/AllowRequireInfrastructureEncryption` registration state. If `Registering` → reach out to Ozge Gun (`Ozge.Gun@microsoft.com`).

### How to enable (create-time)
- **Portal**: Create SA → Advanced tab → **Require Infrastructure Encryption** (defaults OFF)
- **CLI**: `az storage account create ... --require-infrastructure-encryption`
- **PowerShell**: `New-AzStorageAccount ... -RequireInfrastructureEncryption`

State shown in Portal Encryption blade.

### Verify on existing SA
DGrep: https://jarvis-west.dc.ad.msft.net/8E0324D9 — look for SRP property:
```json
"encryption": { "requireInfrastructureEncryption": true }
```

### Verify it was set at create-time
DGrep: https://jarvis-west.dc.ad.msft.net/63AC607C — review request body. If `requireInfrastructureEncryption: true` at create but now disabled → escalate to EEE/PG.

---

## SA-CMK-ConfigSwitching — Storage Encryption with CMK Configuration Switching Fails (KV authentication failure 5-step deep dive)

### Symptoms
- `The operation "List" is not enabled in this key vault's access policy.`
- `httpStatusCode 400 / KeyVaultAuthenticationFailure / The operation failed because of authentication issue on the keyvault.`
- Browser DevTool: `Forbidden / does not have keys list permission on key vault`

### Investigation (5-step)

#### Step 1 — KV Access configuration (both old + new KVs)
- **RBAC mode**: MI must have `Key Vault Crypto Service Encryption User` RBAC role
- **Access Policies mode**: MI must have `wrapkey + unwrapkey + Get`

Via Portal: KV → Access Control (IAM) OR Access Policies.
Via ASC: KV URI → Properties → Access Policies → filter MI ID.

#### Step 2 — KV Firewall settings
If Portal shows "Allow public access from specific VNets/IPs" OR "Disable public access" → must confirm **Allow trusted Microsoft services to bypass this firewall** is ENABLED. Via ASC: KV → Properties → Resource Properties → expect `Bypass: AzureServices`.

#### Step 3 — SRP Jarvis analysis
DGrep: https://portal.microsoftgeneva.com/s/57EE6327 → collect correlationId.
Expected exception signature: `SrpErrorCode KeyVaultAuthenticationFailure` in `KeyVaultClientAccess.WrapOrUnWrapKey`.

#### Step 4 — KV Jarvis analysis (key status impacts)
DGrep: https://portal.microsoftgeneva.com/s/9BDA31B7

**Key status table** during CMK switch:

| Old key status | Wrap/Unwrap | Impact |
|---|---|---|
| **Enabled** | Both work | Normal |
| **Disabled** | Neither | New requests fail |
| **Deleted** | Permanently lost | All wrapped data inaccessible — KV soft-delete + purge protection MUST be enabled when CMK is used |
| **Expired** | New ops fail; existing wrapped data still accessible | |

Look for `HTTP 403: ForbiddenByFirewall` → KV firewall/ACL (AzureServices bypass not enabled).

#### Step 5 — Mitigation: regenerate System MI + reassign RBAC/Access Policy
If system-assigned MI expired:
- Via https://resources.azure.com/ → navigate to SA → Edit → `identity.type=None` → PUT → `identity.type=SystemAssigned` → PUT
- Then re-assign RBAC `Key Vault Crypto Service Encryption User` OR Access Policy `Get + WrapKey + UnwrapKey` to the regenerated MI

---

## SA-CMK-CrossTenant-403-500 — Storage Blob 403 or 500 (multi-tenant app / FIC / UAMI deletion — 4 sub-causes)

### Symptoms
- HTTP 403: `This request is not authorized to perform this operation using this permission.`
- HTTP 500: `Server encountered an internal error.`
- XDS log: `KeyVaultUnableToGetAadTokenException` → `Cannot read access token from azure active directory` → `400 Bad Request` from AAD → Setting status code to 500

### 4 known causes
1. **Soft-Deleted multi-tenant app** (in service-provider tenant)
2. **Hard-Deleted multi-tenant app** (auto after 30 days of soft-delete unless manual purge)
3. **Deleted Federated Identity Credential (FIC)** on the multi-tenant app
4. **Deleted User-Assigned MI assigned to the FIC**

During private preview, blob access continued ~2.5 days after soft-delete before failing.

### Detection via AAD sign-in events
Normal: SP sign-in events recorded in BOTH service-provider AND customer tenants with `Federated credential ID` populated. After deletion: NO sign-in events in either tenant.

For FIC-only / UAMI-only deletion, sign-in failures DO appear:
- Error code **7000226**
- Failure reason: `No federated identity credential policy found on application ({appid}). The client_assertion ... does not match the subject or application being requested.`
- `Federated credential ID` field is EMPTY

### Solution 1 — Soft-Deleted multi-tenant app
Global admin → Entra ID → [App registrations](https://portal.azure.com/#blade/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/RegisteredApps) → Deleted Applications tab → select app → **Restore app registration**.

### Solution 2 — Hard-Deleted multi-tenant app (rebuild from scratch)
```bash
az login
appName="{app_name}"
appObjectId=$(az ad app create --display-name $appName --available-to-other-tenants true --query objectId --out tsv)
appId=$(az ad app show --id $appObjectId --query appId --out tsv)
```
Then recreate FIC (see Solution 3) + update SA `federatedIdentityClientId` via [Storage Accounts - Update REST API](https://docs.microsoft.com/en-us/rest/api/storagerp/storage-accounts/update). Each customer tenant must delete the old SP and register the new one + assign **Key Vault Crypto Service Encryption User** role on the KV.

### Solution 3 — Deleted FIC (recreate FIC only)
App registration → Certificates & secrets → Federated credentials → **Add credential** → **Other issuer**:
- Subject identifier = SP objectId of the managed identity
- Issuer URL contains service provider's `{tenantId}`
- Audience: `api://AzureADTokenExchange` (default)

### Solution 4 — Deleted UAMI assigned to FIC
1. Create new UAMI in same subscription as the SA
2. Edit FIC's `Subject identifier` to point at new UAMI's SP objectId
3. SA → Encryption blade → Change key → User-assigned identity → Change → select new UAMI → Save

---

## SA-Recovery-Main — Master recovery scoping TSG (CSAR first + AD-CSSStgApprovers JIT elevation)

### CRITICAL upfront message to customer
> All supported recovery scenarios are **best effort only** — recovery NOT guaranteed. Set expectations on initial contact.

### Scope
All storage recovery handled by **VM POD**, EXCEPT Block Blobs / Containers / ADLS Gen2 / Tables → **Dev Storage PaaS**.

### Eligibility rules
- Date of request ≤ 14 days from deletion
- Recovery only if SA NOT permanently GC'd on backend (GC: "anytime" to 15 days)
- **CUSTOMER MUST NOT RE-CREATE the account with same name** — may break recovery. If already re-created → delete it first; choose correct deletion timestamp.

### 5 scoping questions (document in case notes)
1. What was deleted? (SA / container / blob name)
2. Precise time of deletion
3. Region of SA
4. How deleted (portal / PS / automation)
5. For SA recovery: have they tried CSAR ([Recover a deleted SA](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-recover)) first? **Required**.

### Special: Disabled Subscription
If customer accidentally deleted SA + sub got disabled → collab with **ASMS (Subscriptions Team)** to reactivate sub first, then proceed.

### Azure Files Recovery quick checks (ASC)
ASC → Summary tab → Files Configurations:
- `Azure Backup Protected = N/A` → NOT enabled
- Snapshot Timestamp `12/31/9999 23:59:59` + Snapshot Version `7131` → NO snapshots

### Case coding
- Support Topic: `Routing Azure Storage Management\Deletion and Recovery\Recover deleted account`
- Root Cause: `Storage Account Management\Recover deleted account\Recovery successful`

### JIT elevation for storage recovery operations
Request JIT elevation for **Scope: Storage → Access Level: CustomerServiceOperator** via `aka.ms/oneidentity`. Members of `AD-CSSStgApprovers` (TAs + SEEs) approve.

---

## SA-Delete-AccountProtected-Detect — Determine if SA is Protected from Deletion (XLocation + DGrep detection methods)

### Symptom
SA deletion fails with:
```
Encountered an internal server error. The tracking id is '<guid>'. (Code: InternalServerError)
```
**Not all InternalServerError messages are this issue** — must verify.

### Detection method 1 — XLocation account flags
1. Browse: https://xlocationsn3prod.location-diagnostics.store.core.windows.net/master/listaccountinformation.html
2. Enter SA name → List Account information → XML output includes `IsProtectedFromDeletion`

### Detection method 2 — DGrep for AccountProtectedFromDeletion
Query: https://jarvis-west.dc.ad.msft.net/82453C0D — set time range + SA name → look for SA deletion ops failed with `AccountProtectedFromDeletion`.

### Cause
Intentional protection (often added by internal Microsoft teams to vital accounts).

### Resolution
Open ICM to request removal of the protection.

Cross-link: [`SA-Delete-AccountProtected`](#sa-delete-accountprotected--classic-sa-accountprotectedfromdeletion-protection-lock) handles the Classic SA variant of this; this anchor is the **detection** procedure (works for ARM + Classic).

---

## SA-Delete-Blob — Unable to Delete Blob (VHD = IaaS, non-VHD = Dev Storage)

### ⚠ Scope
- **Blob is VHD** (unmanaged disk) → IaaS scope (this section)
- **Blob is non-VHD** → Dev Storage scope (transfer case)

### Triage
1. ASC Insights
2. [Query Storage FrontEnd logs](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/690089) → collect Error Message + Error Code + TimeFrame + ActivityId + RequestUrl
3. Determine VHD or non-VHD

### Blobs - VHDs → error routing table

| Error | Action |
|---|---|
| `There is currently a lease on the blob and no lease ID was specified` OR `disk currently in use by VM <X> running within hosted service` | [`SA-Util-IdentifyBlobsActiveLease`](#sa-util-identifyblobsactivelease--identify-blobs-with-active-lease-foundation-for-vhd-lease-investigation-stamp-owned-locks-asc-jarvis-actions) → find owning VM → delete or detach |
| `This operation is not permitted because the blob has snapshots` | Delete snapshots first per [Create and manage blob snapshots](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/496136) |
| `No Access (403)` | SA Firewall enabled + caller IP not whitelisted → [Allow Public IP](https://docs.microsoft.com/en-us/azure/storage/common/storage-network-security#grant-access-from-an-internet-ip-range) |
| Other VHD errors | Advanced TS via Verbose logs |

---

## SA-Delete-FileShare — Unable to Delete Azure File Share (ARM lock common cause)

### Triage
1. ASC Insights
2. [`SA-Util-LookupCRUD-CtrlPlane`](#sa-util-lookupcrud-ctrlplane--lookup-control-plane-sa-create-and-delete-operations-3-step-foundation-flow) → Error Message + Error Code + TimeFrame + CorrelationId
3. Lookup error; if not found → Advanced TS

### Error table

| Error | Action |
|---|---|
| `Share can't be deleted - A resource lock affects this share` | ARM Lock on SA / RG / Subscription. [Remove lock](https://docs.microsoft.com/en-us/azure/azure-resource-manager/management/lock-resources) |
| Other | Advanced TS → RSRP Verbose Logs ([`SA-Util-QueryRSRP`](#sa-util-queryrsrp--query-storage-detailed-rsrp-logs-foundation-jarvis-dgrep-regionalsrp)) |

For specifically `AzureBackupProtectionLock` → see [`SA-Delete-FileShare-BackupLock`](#sa-delete-fileshare-backuplock--azurebackupprotectionlock-auto-recreated-by-backup-policy).

---

## SA-Delete-FileShare-BackupLock — `AzureBackupProtectionLock` (auto-recreated by Azure Backup policy)

### Symptom
```
A resource lock affects this share. Resource locks can exist on the subscription, resource group, and storage account level.
To force deletion, remove the lock and attempt share deletion again.
```
Even after deleting the lock, it's **auto-recreated by Azure Backup policy** at next backup schedule.

### Root cause
Azure Files Backup stores snapshots in the SAME SA as the backed-up share. Backup applies Delete lock on SA (by design). If SA deleted → all snapshots lost.
Ref: [Azure Backup QnA](https://learn.microsoft.com/en-us/azure/backup/backup-azure-files-faq#why-is-it-recommended-to-enable-lock-on-the-storage-account-)

### Workaround 1 (immediate)
Delete the lock — it WILL be recreated at next backup. Customer must delete lock each time they want to delete files.

### Workaround 2 (permanent — requires stop+delete backup)
1. For NEW SAs: deploy without backup policy initially; enable backup WITHOUT storage account lock
2. For EXISTING backups:
   - **Hard delete required** to re-enable backup without lock
   - If soft delete enabled: disable soft delete first ([Disable soft delete](https://learn.microsoft.com/en-us/azure/backup/backup-azure-security-feature-cloud?tabs=azure-portal#enable-and-disable-soft-delete)) then delete data
   - Recovery Services Vault → Backup item → Delete backup data
3. Set up new backup policy without SA lock

---

## SA-Billing-UltimateGuide — Storage Billing Cases foundation TSG + `Xstore_BillingModel.ini` glossary + 3 toolsets

### Required info per case
Bare minimum to start:
1. Brief description of complaint
2. SA name
3. MeterID(s)
4. Normal consumption period (start + end)
5. Abnormal consumption period (start + end)

### No MeterID — list top meters
```kusto
cluster("XStore").database("xdataanalytics").XStoreAccountBillingDaily
| where TimePeriod >= datetime({StartTime})
| where TimePeriod <= datetime({EndTime})
| where AccountName contains "{StorageAccountName}"
| project TimePeriod, AccountName, StgMeterName, MeterId, ProratedQuantity
| sort by ProratedQuantity desc
```
Add `| where MeterId == "<X>"` to filter further.

**Access prereq**: `XDAKustoClusterAccess` group ([request access](https://coreidentity.microsoft.com/manage/Entitlement/entitlement/xdakustoclus-uqdt)).

### Glossary
- **MeterID**: unique billing identifier for a service/resource
- **Meter Name**: human-friendly name of the billing meter
- **Prorated Quantity**: consumption per meter, adjusted per billing policy. **CRITICAL**: units vary (GB / MB / KB / etc.) per MeterID — ALWAYS check `Xstore_BillingModel.ini` for the unit.

### `Xstore_BillingModel.ini` (deep dive)
[XStore code repo](https://msazure.visualstudio.com/One/_git/Storage-XStore?path=/src/DynamicConfig/Schema/XHealth/XStore_BillingModel.ini) — access via XStore code repo access package (contact `CssIaaStorageTAs@microsoft.com`).

For each MeterID, check:
- `BillingPolicy` — the unit (e.g., `GB`, `GbTotal_GeoReplicationIngress`)
- `ApiLists` — which Request Types fall under this meter (e.g., `ADLSGen2Write, ADLSGen1Write, ADLSGen2IterativeWrite`)
- `OperationType`, `Redundancy`, `AccessTier`, `BillingMeter`

### 3 toolsets for billing analysis

#### Tool 1: Xportal Shoebox
- ASC → SA → Performance → select time → "Shoebox API Investigation Dashboard"
- OR direct link with params: HotPathAccount, Tenant, AccountResourceId, AccountName
- Output: Transaction Total per API

#### Tool 2: ASI Storage Tools
- [Storage Account dashboard](https://asi.azure.ms/services/Storage%20Tools/pages/Storage%20Account): SA details + limits + usage + MDM dashboards + DGrep + Jarvis Actions + transactions by request type
- [Billing Drilldown](https://asi.azure.ms/services/Storage%20Tools/pages/Billing%20Drilldown): Billable Transactions + Ingress + Egress + Account Billing Daily totals

#### Tool 3: Customer enables Diagnostic Settings (WARNING: extra cost)
- SA → Monitoring → Diagnostic settings → + Add → select Logs + Metrics + destination (Log Analytics workspace)
- After save, allow few minutes for data → reproduce → use Insights view or Logs

---

## SA-Util-LookupCRUD-CtrlPlane — Lookup Control Plane SA Create and Delete Operations (3-step foundation flow)

### Purpose
Find CRUD ops of an SA + who performed + when. Entry-point referenced by AccountStuckCreating / NetworkSourceDeleted / 502BadGateway / FileShare Delete / Account Migration / etc.

### Note
For **data-plane** ops (Blob / File / Container CRUD) → use [Lookup Data Plane CRUD](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/496103).

### 3-step flow

#### 1. Query Storage entry-level (ARM/RSRP) Logs
See [Query Storage entry-level ARM RSRP Logs](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/2182782). Collect:
- PreciseTimeStamp
- CorrelationId
- Request nature (Create / Update / Delete)
- requestBody
- Error message

#### 2. (Optional) Correlate IDs with resources/users
Identify caller (User / Service Principal / Application) per [Correlating IDs](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/2182782/Query-Storage-entry-level-ARM-RSRP-Logs_Storage?anchor=correlating-ids-with-resources/users).

#### 3. Query Storage RSRP Logs (verbose)
See [`SA-Util-QueryRSRP`](#sa-util-queryrsrp--query-storage-detailed-rsrp-logs-foundation-jarvis-dgrep-regionalsrp).

---

## SA-Util-QueryRSRP — Query Storage detailed RSRP Logs (foundation Jarvis DGrep RegionalSRP)

### Prerequisites
- CorrelationId
- SA name
- Accurate operation time

### Jarvis DGrep query template
[Query Link Example](https://portal.microsoftgeneva.com/s/8F4B0DA6):
```
Namespace: RegionalSRP
Events: ServiceApiQosEvent, ServiceOperationActivityEvent
Tenant/Moniker: RSRP<REGION>          (e.g. RSRPNorthEurope)
Time range: <issue window>
Filtering: Subscription == <SubscriptionId>
Filtering: CorrelationId == <CorrelationId>
```
For RSRP region mapping see [Find Region and Stamp Storage Account](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/496144).

### Review tips
- Filter by `logLevel` (Critical / Error / Information / Verbose)
- If logs contain ActivityId like `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxx000000` (`000000` suffix) → points to a data-plane op made by Storage subsystem → follow [Query Storage Verbose Logs](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/690091) to persist them

### Example data-plane signal in RSRP
```
Update Account failed on stamp dub14prdstrz26a for account <SA> with error Error InvalidXmlDocument,
Message: XML specified is not syntactically valid. RequestId:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxx000000
```

---

## SA-Util-IdentifyBlobsActiveLease — Identify Blobs with Active Lease (foundation for VHD lease investigation + Stamp Owned Locks + ASC + Jarvis Actions)

### Purpose
When SA deletion blocked by `AccountIsLocked` OR blob deletion blocked by lease error → find which VHD/blob holds the active lease.

### Method 1 — ASC (preferred)
ASC → Resource Explorer → SA → **Disks/Images** tab → review Disks + OS Images + VM Images.

### Method 2 — Jarvis Actions

#### Look up Classic Disks (in a sub)
AzureRT → Microsoft → Service Management → **List Disks**. [Example](https://jarvis-west.dc.ad.msft.net/24AD3E6A) — shows all disks per SA + VHD path + attached VM.

#### Display all subscription objects
AzureRT → Subscription Management → **Get Subscription Rows (TSQ)**. [Example](https://jarvis-west.dc.ad.msft.net/E44F5CCF). RowKey prefixes:
- `VMImage` — image of a VM
- `OSImage` — uploaded image
- `Disk` — Classic OS Disk

#### Look up ARM leases
CRP → Production → Subscription Operations → **Get Subscription Details (persistent data)**. [Example](https://jarvis-west.dc.ad.msft.net/BBAE719F). Additional Prefix:
- All SAs in sub: `/StorageAccounts`
- Specific SA: `/StorageAccounts/<NAME-IN-CAPS>`

### Blob/resource NOT found → Stamp Owned Locks check
1. ASC → Resource Explorer → SA → Properties → **Stamp Owned Locks**
2. Value `V0:microsoft.compute:<SA>` → **CRP Lock** present (often legitimate)
3. Value `N/A` → escalate to Product Engineering
4. For CRP Lock — verify VM association via Kusto:
   ```kusto
   cluster("Azcrpbi").database("bi_allprod").StorageBlob
   | where PreciseTimeStamp > ago(5d) and StorageAccountName =~ "{StorageAccountName}"
   ```

---

## ESAN-EmergingIssue-ScaleOut — ESAN Scale-Out failing (Aug 2024 Canada Central bug, hotfix rolled out)

### Symptom
ESAN scale-out fails from Azure Portal: `Failed to Update Elastic SAN <X>. Error: Service Error`. Originally reported in Canada Central, August 2024.

### Cause
ESAN RP bug — hotfix rolled out August 2024. Not expected to re-occur. Ref ICM 529832765.

### Workaround 1 — fix VNETs + retry from Portal
Volume Groups may be configured with missing subnets in VNETs. Either recreate the missing subnets OR update VG to remove the broken VNETs.

### Workaround 2 — PowerShell with explicit `publicNetworkAccess`
```powershell
Set-AzContext -Subscription <subid>
Update-AzElasticSan -Name <esan-name> -ResourceGroupName <rg> `
    -PublicNetworkAccess Enabled `
    -BaseSizeTiB <intValue> -ExtendedCapacitySizeTiB <intValue>
```
Set `publicNetworkAccess=Enabled` (only because ESAN already has that value).

### Escalation
If issue recurs post-Aug-2024 hotfix → ICM to ESAN PG.
