# Playbook J — Storage Account (Consolidated) — Core

> **Companion to** [`playbook-J-storage-account-deep.md`](./playbook-J-storage-account-deep.md). Heavy delegate to [`references/storage-account-queries.md`](../catalogs/storage-account-queries.md) (581 lines / 30+ KQL).
>
> Use as **routing entry point** when a case is about a Storage Account control plane / data plane management issue (NOT account-level performance — that's Playbook K; NOT Azure Files — that's L; NOT managed disk lifecycle — that's Playbook F).

## When to use this playbook

| Use Playbook J when... | Don't — use instead |
|---|---|
| SA stuck in Creating / can't update / SRP metadata corrupt | VM disk attach failure → Playbook F |
| CMK errors (KV token, federated MI, encryption scope, KV key not found, cross-tenant CMK) | ADE / SSE+CMK on managed disks → Playbook H |
| `NetworkSourceDeleted` / ghost subnet ACL on SA firewall | VNet itself broken → networking-queries.md direct |
| Storage Account recovery (CSAR / ARM SA / Classic SA) | Managed disk recovery → Playbook F § MD-Delete |
| Blob / Container / Page Blob / SMB File recovery | Block Blob / Container = Dev Storage PaaS (this playbook routes) |
| Storage Account "Unable to Delete" (AccountIsLocked / Migrating / Protection lock) | Disk delete blocked → Playbook F |
| Storage Billing inquiries (SKU change 30-day grace, meter analysis, transaction count) | Subscription quota → Capacity Customer Experience |
| Elastic SAN (volume / volume group / iSCSI / quota) | XStore/XArgus stamp-level perf  → K |
| SA-level throttling tactical 429 → routes to C § THR-Perf-3 | Deep XArgus latency RCA → Playbook K |

## Inputs to collect

| # | Item | Why |
|---|---|---|
| 1 | `SubscriptionId` + `ResourceGroupName` + `StorageAccountName` | Primary filters |
| 2 | Error message + Error Code (verbatim) | Most TSGs are error-code-routed |
| 3 | StartTime / EndTime (UTC) | Pad ±15 min |
| 4 | CorrelationId / OperationId / ActivityId | For ARM + CRP correlation + XDS log search |
| 5 | KV name + KV Key URI (for CMK) | KV access perms validation |
| 6 | UAMI / federatedIdentityClientId (for CMK cross-tenant) | MI auth chain |
| 7 | For recovery: deletion timestamp + business justification | Required for PG ICM |
| 8 | For ESAN: ESAN Resource ID + Region + Volume / VG name | ESAN PG ICM |

## Step-by-step

### Step 1 — Identify problem domain (Mgmt vs CMK vs Recovery vs Delete vs Billing vs ESAN)

| Symptom | Goes to... |
|---|---|
| SA Create / Update / general operation fails (non-CMK, non-network) | Step 2 (Management) |
| Any CMK error (Portal, PS, blob access 403/500, EncryptionScope, KV Key Not Found, federated MI) | Step 3 (CMK) |
| Customer wants to recover a deleted resource (SA / blob / container / file share) | Step 4 (Recovery) |
| Cannot delete SA / container / blob / file share | Step 5 (Delete) |
| Billing question (SKU change, capacity, meter analysis) | Step 6 (Billing) |
| Elastic SAN any error | Step 7 (ESAN) |

### Step 2 — Management routing

| Symptom | Anchor |
|---|---|
| SA stuck in Creating state — same-name account recently deleted OR exclusive lock | § [SA-Mgmt-StuckCreating](./playbook-J-storage-account-deep.md#sa-mgmt-stuckcreating--storage-account-stuck-in-creating-state-accountbeingdeleted-or-exclusive-lock) |
| `StorageAccountOperationInProgress` (concurrent op conflict) | § [SA-Mgmt-OperationInProgress](./playbook-J-storage-account-deep.md#sa-mgmt-operationinprogress--storageaccountoperationinprogress-error-concurrent-op-conflict) |
| Customer requests SA quota increase (Ingress / Egress / IOPS / Capacity > 15PiB) | § [SA-Mgmt-IncreaseLimits](./playbook-J-storage-account-deep.md#sa-mgmt-increaselimits--increase-storage-account-capacity-limits-ingressegressiopstx) |
| `UnknownEncryptionKeySource` (SRP metadata inconsistency) | § [SA-Mgmt-UnknownEncryptionKeySource](./playbook-J-storage-account-deep.md#sa-mgmt-unknownencryptionkeysource--ssrp-metadata-inconsistency-update-fails-fixed-by-pg-scrub) |
| `InternalServerError: Not enough space on disk` when create/update with CMK (Emerging Issue cert temp-file leak) | § [SA-Mgmt-DiskSpaceCryptoException](./playbook-J-storage-account-deep.md#sa-mgmt-diskspacecryptoexception--internalservererror-not-enough-space-on-disk-cmk-createupdate-cert-temp-file-leak) |
| `NetworkAcls VirtualNetworkRule ... state NetworkSourceDeleted` (subnet deleted+recreated, ghost ACL) | § [SA-Mgmt-NetworkSourceDeleted](./playbook-J-storage-account-deep.md#sa-mgmt-networksourcedeleted--networkacls-virtualnetworkrule-state-networksourcedeleted-ghost-subnet-acl) |
| HTTP 502 Bad Gateway / `Microsoft.Storage failed to return collection response` / `Subscription was not found` | § [SA-Mgmt-502-BadGateway](./playbook-J-storage-account-deep.md#sa-mgmt-502-badgateway--502-bad-gateway-microsoftstorage-failed-to-return-collection-response-sub-not-registered-in-new-region-rp-endpoint) (sub not registered in region's new RP endpoint) |
| SA not visible in Portal/PS/CLI (but data still accessible) → subscription sync issue | § [SA-Mgmt-NotVisible](./playbook-J-storage-account-deep.md#sa-mgmt-notvisible--storage-account-not-visible-in-portal-or-powershell-subscription-sync-issue--arm-sync-required) (5-check flow, ARM Sync last resort) |
| `Failed to update v1 storage account. Error: The specified app id is not valid for the request.` | § [SA-Mgmt-FailedToUpdate-AppId-Invalid](./playbook-J-storage-account-deep.md#sa-mgmt-failedtoupdate-appid-invalid--failed-to-update-v1-sa-specified-app-id-not-valid-classic-to-arm-stuck-in-prepare) (Classic→ARM stuck in Prepare → `Move-AzStorageAccount -Commit`) |
| Customer asks about Infrastructure Encryption (Double Encryption) feature | § [SA-Mgmt-DoubleEncryption](./playbook-J-storage-account-deep.md#sa-mgmt-doubleencryption--infrastructure-encryption-feature-create-time-only-not-disableable) (create-time-only, not disableable) |

### Step 3 — CMK routing

| Symptom | Anchor |
|---|---|
| Blob 403 `KeyVaultAccessTokenCannotBeAcquired` / UAMI deleted | § [SA-CMK-KVTokenCannotBeAcquired](./playbook-J-storage-account-deep.md#sa-cmk-kvtokencannotbeacquired--keyvaultaccesstokencannotbeacquired-uami-deleted) |
| `Failed to Update <SA>` when enabling CMK from Portal/PS, KV verified OK | § [SA-CMK-FailedToUpdate](./playbook-J-storage-account-deep.md#sa-cmk-failedtoupdate--failed-to-update-mystorageaccount-pg-manual-patching-required) (regression bug 2320437, PG manual patch) |
| `Set-AzStorageAccount : Missing pre-requisites to enable EncryptionAtRest/CMK` (works in Portal but fails in PS) | § [SA-CMK-PowerShell-MissingParams](./playbook-J-storage-account-deep.md#sa-cmk-powershell-missingparams--set-azstorageaccount-missing-pre-requisites-uami-3-extra-params-needed) (add `-IdentityType UserAssigned` + 2 more) |
| `The given encryption scope is invalid: Conflict 409` / `EncryptionScopeNotAvailable` | § [SA-CMK-Conflict409](./playbook-J-storage-account-deep.md#sa-cmk-conflict409--encryption-scope-invalid-conflict-409-encryptionscopenotavailable) |
| Cross-tenant CMK: `InternalError 500 / Cannot read access token from azure active directory / 401 Unauthorized` | § [SA-CMK-CrossTenant-DataPlane](./playbook-J-storage-account-deep.md#sa-cmk-crosstenant-dataplane--cross-tenant-cmk-internalerror-500-kv-inaccessible-or-federated-mi-deleted) |
| Cross-tenant CMK: `Gateway authentication failed for 'Microsoft.Storage' / AADSTS700016` (new SA create) | § [SA-CMK-CrossTenant-GatewayAuth](./playbook-J-storage-account-deep.md#sa-cmk-crosstenant-gatewayauth--gateway-authentication-failed-for-microsoftstorage-invalid-federatedidentityclientid) |
| `KeyVaultEncryptionKeyNotFound` (KV deleted / RBAC missing / CMG scenario / NSP perimeter mismatch) | § [SA-CMK-CrossTenant-KVKeyNotFound](./playbook-J-storage-account-deep.md#sa-cmk-crosstenant-kvkeynotfound--keyvaultencryptionkeynotfound-3-causes-kv-deleted--rbac-incl-cmg--nsp-mismatch) |
| CMK config switching fails (KV authentication failure during enable/switch) | § [SA-CMK-ConfigSwitching](./playbook-J-storage-account-deep.md#sa-cmk-configswitching--storage-encryption-with-cmk-configuration-switching-fails-kv-authentication-failure-5-step-deep-dive) (5-step KV auth + 4 key status table + regen System MI via resources.azure.com) |
| Cross-tenant CMK: Storage Blob 403 / 500 — multi-tenant app or FIC or UAMI deleted | § [SA-CMK-CrossTenant-403-500](./playbook-J-storage-account-deep.md#sa-cmk-crosstenant-403-500--storage-blob-403-or-500-multi-tenant-app-or-fic-or-uami-deletion-4-sub-causes) (4 sub-causes + AAD sign-in error 7000226 detection) |

### Step 4 — Recovery routing

| Symptom | Anchor |
|---|---|
| Customer wants to recover something — start here for ownership matrix | § [SA-Recovery-Main](./playbook-J-storage-account-deep.md#sa-recovery-main--master-recovery-scoping-tsg--csar-first--ad-cssstgapprovers-jit-elevation) (master scoping TSG — CSAR first, 5 scoping questions, AD-CSSStgApprovers JIT) → § [SA-Recovery-QuickReference](./playbook-J-storage-account-deep.md#sa-recovery-quickreference--ownership-routing-matrix-12-storage-object-types) (12 storage object types) |
| Recover deleted **ARM Storage Account** | § [SA-Recovery-ARM](./playbook-J-storage-account-deep.md#sa-recovery-arm--arm-storage-account-recovery-csar-first-then-icm) (CSAR first, then XStore\Location Service ICM) |
| Recover deleted **Classic Storage Account** | § [SA-Recovery-Classic](./playbook-J-storage-account-deep.md#sa-recovery-classic--classic-storage-account-recovery-rdfe-based) |
| Recover deleted blob (block blob = Dev Storage; page blob = IaaS) | § [SA-Recovery-BlobData](./playbook-J-storage-account-deep.md#sa-recovery-blobdata--blob-data-recovery-dev-storage-owns-blob-recovery-asc-insight-first) |
| Recover deleted container (requires geo-replication; LRS = no recovery) | § [SA-Recovery-Container](./playbook-J-storage-account-deep.md#sa-recovery-container--container-recovery-dev-storage-owns-requires-geo-replication--sas-token-handling-rules) |
| Recover deleted SMB Azure Files share / files (NFS = NOT recoverable) | § [SA-Recovery-FilesSMB](./playbook-J-storage-account-deep.md#sa-recovery-filessmb--azure-files-smb-recovery-pg-via-icm-sev-3-only-jarvis-dgrep-investigation) |
| Recover deleted Managed Disk | → **Playbook F § MD-Delete** (not this playbook) |
| Recover ADLS Gen2 (HNS-enabled) files/folders | → **Dev Storage** [TSG](https://supportability.visualstudio.com/AzureDev/_wiki/wikis/Dev_Storage/1832930) |
| Recover deleted Elastic SAN volume / VG / snapshot | § [ESAN-DataRecovery](./playbook-J-storage-account-deep.md#esan-datarecovery--volume--volume-group--snapshot-soft-delete-recovery-10-day-retention) |

### Step 5 — Delete routing

| Symptom | Anchor |
|---|---|
| `AccountIsLocked` — SA cannot be deleted (artifacts still referencing — typically unmanaged VM VHD) | § [SA-Delete-AccountIsLocked](./playbook-J-storage-account-deep.md#sa-delete-accountislocked--accountislocked-vhdartifact-still-references-sa) |
| Classic SA `AccountProtectedFromDeletion` (Protection lock enabled) | § [SA-Delete-AccountProtected](./playbook-J-storage-account-deep.md#sa-delete-accountprotected--classic-sa-accountprotectedfromdeletion-protection-lock) |
| SA delete fails with generic `InternalServerError` — verify if Protected from Deletion | § [SA-Delete-AccountProtected-Detect](./playbook-J-storage-account-deep.md#sa-delete-accountprotected-detect--determine-if-sa-is-protected-from-deletion-xlocation--dgrep-detection-methods) (XLocation `listaccountinformation.html` + DGrep) |
| Unable to delete Blob (VHD = IaaS; non-VHD blob = Dev Storage) | § [SA-Delete-Blob](./playbook-J-storage-account-deep.md#sa-delete-blob--unable-to-delete-blob-vhd--iaas-non-vhd--dev-storage) |
| Unable to delete Blob Container (lease / immutability / `$blobchangefeed` / firewall 403) | § [SA-Delete-BlobContainer](./playbook-J-storage-account-deep.md#sa-delete-blobcontainer--unable-to-delete-blob-container-lease--immutability--changefeed--firewall) |
| Unable to delete Azure File Share (`Share can't be deleted - A resource lock affects this share`) | § [SA-Delete-FileShare](./playbook-J-storage-account-deep.md#sa-delete-fileshare--unable-to-delete-azure-file-share-arm-lock-common-cause) (ARM lock most common) |
| File share lock auto-recreated after deletion (`AzureBackupProtectionLock`) | § [SA-Delete-FileShare-BackupLock](./playbook-J-storage-account-deep.md#sa-delete-fileshare-backuplock--azurebackupprotectionlock-auto-recreated-by-backup-policy) (Azure Backup policy re-applies lock; 2 workarounds) |
| `XrpMigrationInProgress` / `AccountPendingMigrationToSrp` (Classic→ARM not committed) | § [SA-Delete-Migrating](./playbook-J-storage-account-deep.md#sa-delete-migrating--storage-account-in-process-of-being-migrated-classic-arm-not-committed) |

### Step 6 — Billing routing

| Symptom | Anchor |
|---|---|
| Customer billed for old SKU after redundancy conversion (e.g., RA-GRS → LRS) | § [SA-Billing-SKUChange](./playbook-J-storage-account-deep.md#sa-billing-skuchange--storage-sku-change-billing-30-day-grace-window-for-replication-conversions) (30-day grace per docs) |
| Storage billing case open / customer disputes meter / MeterID lookup / `Xstore_BillingModel.ini` glossary | § [SA-Billing-UltimateGuide](./playbook-J-storage-account-deep.md#sa-billing-ultimateguide--storage-billing-cases-foundation-tsg--xstore_billingmodelini-glossary--3-toolsets) (foundation TSG + 3 toolsets Xportal Shoebox / ASI / Diagnostic Settings) |
| General billing inquiries (capacity, meter analysis, transaction count) | § [SA-Billing-Foundations](./playbook-J-storage-account-deep.md#sa-billing-foundations--general-sa-billing-investigation-delegated-to-storage-account-queriesmd) (delegated to storage-account-queries.md) |

### Step 7 — Elastic SAN routing

| Symptom | Anchor |
|---|---|
| ESAN high latency / low throughput / IOPS or BW lower than expected on sequential | § [ESAN-Performance](./playbook-J-storage-account-deep.md#esan-performance--high-latency--low-throughput-xstore-induced--shard-level-5000-iops-256-mbs-limit) (shard-level 5000 IOPS / 256 MB/s limit — internal-only) |
| ESAN iSCSI login fails (Auth Error / Target Error / Connection Failed) | § [ESAN-Connectivity](./playbook-J-storage-account-deep.md#esan-connectivity--iscsi-login-failed--io-timeouts-windows-event-157-vnet-acl-or-network) |
| Windows disk unmount during Failover cluster restart (Event 157 / MPIO failover storm) | § [ESAN-DiskUnmount](./playbook-J-storage-account-deep.md#esan-diskunmount--disk-unmount-unexpectedly-windows-failover-cluster-mpio-linkdowntime-30s) (`LinkDownTime` 15→30s) |
| ESAN volume from MD snapshot shows as not initialized (PS only, not Portal) | § [ESAN-MDSnapshot-NotInitialized](./playbook-J-storage-account-deep.md#esan-mdsnapshot-notinitialized--volume-from-md-snapshot-not-initialized-via-powershell-missing-creationdatacreatesource-flag) (missing `-CreationDataCreateSource DiskSnapshot`) |
| Customer wants to recover deleted ESAN volume / VG / snapshot (10-day retention) | § [ESAN-DataRecovery](./playbook-J-storage-account-deep.md#esan-datarecovery--volume--volume-group--snapshot-soft-delete-recovery-10-day-retention) |
| Customer wants quota increase (only Max ESAN per sub/region supported) | § [ESAN-QuotaIncrease](./playbook-J-storage-account-deep.md#esan-quotaincrease--quota-increase-only-max-esan-per-sub-region-supported-cap-iops-bw-not-customer-controllable) |
| Need to check ESAN / VG / Volume properties (ASC + Jarvis DGrep + Jarvis Actions) | § [ESAN-CheckConfiguration](./playbook-J-storage-account-deep.md#esan-checkconfiguration--inspect-esan--vg--volume-properties-via-asc--jarvis-dgrep--jarvis-actions) |
| ESAN scale-out fails with `Service Error` (Aug 2024 Canada Central bug, hotfix rolled out) | § [ESAN-EmergingIssue-ScaleOut](./playbook-J-storage-account-deep.md#esan-emergingissue-scaleout--esan-scale-out-failing-aug-2024-canada-central-bug-hotfix-rolled-out) (workarounds: fix VNETs + retry OR PowerShell `Update-AzElasticSan -PublicNetworkAccess Enabled`) |

### Step 8 — SA Utilities (foundation lookups cross-linked from every step above)

| When to use | Anchor |
|---|---|
| Need to find SA CRUD ops + who performed + when (control-plane) | § [SA-Util-LookupCRUD-CtrlPlane](./playbook-J-storage-account-deep.md#sa-util-lookupcrud-ctrlplane--lookup-control-plane-sa-create-and-delete-operations-3-step-foundation-flow) (3-step foundation flow) |
| Need detailed RSRP verbose logs for a SA op (CorrelationId in hand) | § [SA-Util-QueryRSRP](./playbook-J-storage-account-deep.md#sa-util-queryrsrp--query-storage-detailed-rsrp-logs-foundation-jarvis-dgrep-regionalsrp) (Jarvis DGrep RegionalSRP + Region mapping + ActivityId `000000` suffix data-plane signal) |
| Need to identify which blobs/VHDs in an SA have active leases (blocks delete) | § [SA-Util-IdentifyBlobsActiveLease](./playbook-J-storage-account-deep.md#sa-util-identifyblobsactivelease--identify-blobs-with-active-lease-foundation-for-vhd-lease-investigation-stamp-owned-locks-asc-jarvis-actions) (ASC Disks/Images + 3 Jarvis Actions queries + Stamp Owned Locks check) |

### Step 9 — Pull foundation evidence

| Data | Cluster.Database.Table | When |
|---|---|---|
| SA properties (kind / SKU / HNS / IsXio / state) | `azcore.Xstore.XStoreAccountProperties` | First step for any SA case |
| Find Tenant/Stamp hosting SA | `xstore.xstore.AccountCapacityDailyV3` | Stamp-level lookup |
| ARM operations (Create/Delete/Update/Failover/SKU change) | `armprodgbl.ARMProd.EventServiceEntries` or `HttpOutgoingRequests` | Customer history of ops |
| SA capacity + file share count | `xstore.xstore.StorageAccountCapTX` | Capacity inquiries |
| Daily billing breakdown | `xstore.xdataanalytics.XStoreAccountBillingDaily` | Billing question |
| Daily transaction count | `xstore.xdataanalytics.XStoreAccountTransactionsDaily` | Transaction breakdown |
| Billing meter metadata | `pav2data.aipusageaudit.AllMeters` | "What's MeterId X?" |
| Cross-tenant CMK MSI deletion check | `azmsicl.azmsidb.OperationEvent` | UAMI deleted? |
| Classic→ARM migration status | `rdfeprod.rdfeprodDB.CommitStorageServiceMigrationOperationEtwTable` | Migration phase |
| Storage throttling trace | `armprodgbl.ARMProd.Storage.StorageOperations` | 429 / ServerBusy investigations |
| Azure Files metadata throttling | `azcore.Xstore.XStoreXFileThrottleTransaction` | File share throttling (cross-link L) |
| ESAN account-level perf | `xargus.Production.AccountPerfPercentiles5M` (IscsiRead/Write) | ESAN latency RCAs |
| XStore disk blackout / failure triage | `xlivesite.XHealthDiskTriage.XHealth_DiskBlackoutXStoreTriage` | Stamp-level disk failures (cross-link D / K) |

All bodies live in [`references/storage-account-queries.md`](../catalogs/storage-account-queries.md).

### Step 10 — Mitigation + handoffs

| Scenario | Owner |
|---|---|
| SRP metadata regression / Account stuck Creating / Update fails / CMK regression bug | **XStore Triage** (PG manual patching) — engage Anthony Kunnel Jose + Priyaranjan Pandey |
| Cross-tenant CMK (federated MI / multi-tenant app reg recovery) | **Authentication - Application Experiences** team |
| Key Vault key deleted / KV soft-delete recovery | **Azure Key Vault CSS team** (SAP: `Azure\Key Vault\Key Vault Administration\Key Vault Recovery (Soft Delete & Purge Protection)`) |
| Storage SA quota increase (Ingress/Egress/IOPS/TX) | ICM template `O2tP1h` → **XStore Quota team** |
| Storage SA Capacity > 15 PiB | **XStore/Capacity Management** (NOT the limits queue) |
| **Storage Account recovery (CSAR fails)** | **XStore\Location Service** team (CSSStgRec@microsoft.com for ICM moves) |
| Blob/Container/Table/ADLS Gen2 recovery | **Dev Storage PaaS team** (2023 scope transfer) |
| SMB Azure Files recovery | **SMB team** / `xsmbincidents@microsoft.com` (Sev 3 ONLY) |
| Classic→ARM migration stuck | **PG via CRI** (Sev1/2 PG, Sev3/4 EEE) |
| Subnet ghost ACL (`NetworkSourceDeleted`) | **Customer-side cleanup** (compliance prevents auto-removal) |
| ESAN data recovery (10-day retention) | **SAN RP team** |
| ESAN quota | **ElasticSANRP** team, Owning Service **Xstore** |
| SA throttling beyond docs | Document + retry guidance first; if sustained → quota increase via `O2tP1h` |

## Cross-references

| Other playbook / reference | Why |
|---|---|
| Playbook F | Managed disk lifecycle / delete / encryption / recovery (different from SA-level) |
| Playbook C § THR-Perf-3 / 4 | SA-level throttling (429 / ServerBusy) basics; K owns deep RCA |
| Playbook K (TBD) | Storage Performance / Throttling deep dive (XStore/XArgus latency RCA) |
| Playbook L (TBD) | Azure Files + Azure File Sync (specific SMB/NFS/AFS sync issues) |
| Playbook H § SSE-MSINotFound | CMK SA MSI deleted (similar to J § SA-CMK-KVTokenCannotBeAcquired but slightly different scope — J covers the CMK-as-SSE+CMK angle from disk side) |
| Playbook H § SSE-KeyVaultAccessForbidden | DES MI lost KV perms + key expired (managed-disk-side angle on KV access) |
| Playbook H § ADE-RHEL9-BootMountFailure | RHEL 9 disk encryption boot issue (different layer) |
| `references/storage-account-queries.md` | All foundation KQL bodies — SA props, perf, billing, recovery, failover, throttling, Azure Files |
| `references/disks-queries.md` | Managed disk foundation queries (cross-link from J recovery routing to F) |
