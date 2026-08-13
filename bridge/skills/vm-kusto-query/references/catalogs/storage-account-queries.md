# Storage Account Queries — Properties, Performance, Billing, Recovery, Failover, Throttling

Source: AzureIaaSVM ADO Wiki (manually curated from 20+ wiki pages)

---

## Clusters & Access

| Cluster | URI | Database(s) | Purpose | Access |
|---------|-----|-------------|---------|--------|
| **XStore** | `xstore.kusto.windows.net` | `xstore`, `xdataanalytics`, `XStoreNRT` | Account capacity, tenant catalog, billing, transactions, NRT config | [XStore Kusto Access](https://eng.ms/docs/cloud-ai-platform/azure-core/azure-storage/azure-storage-dev-mansah/xstore/team-docs/data/xstorekustoclusteraccessinformation) |
| **AzCore** | `azcore.centralus.kusto.windows.net` | `Xstore` | Account properties, geo replication config, file throttle, dynamic config | Same as AzCore Fa access |
| **XArgus** | `xargus.centralus.kusto.windows.net` | `Production` | Storage performance percentiles (account & tenant level) | Via XStore access |
| **ARMProd** | `armprodgbl.eastus.kusto.windows.net` | `ARMProd` (macro-expand) | Control plane operations — delete, failover, SKU change, throttling | FTE + Delivery Partner access |
| **XLivesite** | `xlivesite.kusto.windows.net` | `XHealthDiskTriage` | XStore disk failure / blackout triage | [XLivesiteKustoAccess](https://coreidentity.microsoft.com/manage/entitlement/entitlement/xlivesitekus-awhh) |
| **PAV2** | `pav2data.eastus.kusto.windows.net` | `aipusageaudit` | Billing meter metadata lookup | Via storage team |
| **XDeployment** | `xdeployment.westcentralus.kusto.windows.net` | `Deployment` | ASI / Storage deployment tools | [XDeploymentKustoAccess](https://coreidentity.microsoft.com/manage/entitlement/entitlement/xdeploymentk-vuu2) |

---

## Storage Account Properties & Configuration

Cluster: `azcore.centralus.kusto.windows.net`
Database: `Xstore`

### XStoreAccountProperties — Get account type, redundancy, configuration

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Xstore').XStoreAccountProperties
| where Account startswith '{StorageAccountName};'
| where TIMESTAMP > ago(7d)
| summarize arg_max(TIMESTAMP, *) by Account
| project TIMESTAMP, Account, Redundancy, AccountType, AccessTier,
          IsHnsEnabled, IsSrp, IsXio,
          Subscription, ResourceGroup, ArmLocation, State
```

Key fields:
- `Account` — Format: `accountname;creationTimestamp`; filter with `startswith '{name};'`
- `Redundancy` — `lrs`, `zrs`, `grs`, `ragrs`, `gzrs`, `ragzrs`
- `AccountType` — Numeric code: `0` = GPv1, `1` = GPv2, `131072` = Premium Block Blob
- `AccessTier` — `Hot`, `Cool`
- `IsHnsEnabled` — 1 = Data Lake Gen2 (hierarchical namespace)
- `IsXio` — 1 = Premium SSD backend; 0 = Standard HDD
- `IsSrp` — 1 = SRP/ARM managed
- `State` — 1 = Active

### Check Geo Priority Replication SLA

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Xstore').XStoreAccountProperties
| where Account startswith '{StorageAccountName};'
| where TIMESTAMP > ago(7d)
| summarize arg_max(TIMESTAMP, *) by Account
| project Account, SlaGeoEnabledServiceTypes, GeoReplicationBlobSLAEnabledTime
```

### Check Geo-Replication Config Flags

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Xstore').GeoReplicationConfig
| where AccountName == '{StorageAccountName}'
| project AccountName, GeoReplicationConfigFlags
```

Look for `GeoReplicationSLAEnabled` in the flags column.

### Full XStoreAccountProperties Schema Reference

| Column | Type | Description |
|--------|------|-------------|
| TIMESTAMP | datetime | Record timestamp |
| Account | string | `accountname;creationTime` |
| Redundancy | string | lrs, zrs, grs, ragrs, gzrs, ragzrs |
| AccountType | long | Numeric account kind (0=GPv1, 1=GPv2, 131072=Premium Block Blob) |
| AccessTier | string | Hot, Cool |
| IsHnsEnabled | long | 1 = Data Lake Gen2 enabled |
| IsSrp | long | 1 = SRP/ARM managed |
| IsXio | long | 1 = Premium SSD backend |
| Subscription | string | Subscription GUID |
| ResourceGroup | string | Resource group name |
| ArmLocation | string | Azure region |
| State | long | 1 = Active |
| Properties | string | JSON blob with extended properties |
| IsChangeFeedEnabled | long | 1 = Change feed enabled |
| IsLifecycleManagementEnabled | long | 1 = Lifecycle management enabled |
| Quota | long | Account quota |
| AccountMigrationStage | long | Migration status (0 = none) |
| GeoRegion | string | Geo-paired region info |
| Tags | string | Resource tags |
| SlaGeoEnabledServiceTypes | string | Geo SLA enabled service types |
| GeoReplicationBlobSLAEnabledTime | datetime | When geo SLA was enabled |

---

## Storage Account Tenant / Stamp Lookup

Cluster: `xstore.kusto.windows.net`
Database: `xstore`

### Find Storage Account Tenant (Stamp) by Account Name

```kusto
cluster('xstore.kusto.windows.net').database('xstore').AccountCapacityDailyV3
| where CapacityType == "total"
| where TimePeriod >= datetime({StartTime}) and TimePeriod < datetime({EndTime})
| where Account == '{StorageAccountName}'
| project AccountName, Tenant
```

Use case: Find which storage cluster (Tenant/Stamp) hosts a given storage account. The `Tenant` field gives the stamp name (e.g., `MS-BL5PrdStr04A`).

### TenantCatalog — Lookup Tenant Geo Domain and Region

```kusto
cluster('xstore.kusto.windows.net').database('xstore').TenantCatalog
| where AltName has '{StorageStampName}'
| project Name, GeoDomain, GeoRegion
| top 1 by GeoDomain
```

### StorageAccountCapTX — Account Capacity and File Share Info

```kusto
cluster('xstore.kusto.windows.net').database('xstore').StorageAccountCapTX
| where AccountName has '{StorageAccountName}'
| project
    timestamp = Timestamp,
    clusterName = Tenant,
    subscriptionId = SubscriptionId,
    Account = AccountName,
    storageAccountCreateDate = AccountCreationTime,
    fileShareCount = FileContainerCount,
    provisionedSizeTiB = XFileProvisionedBytes / pow(1024, 4)
```

---

## Storage Performance — XArgus

Cluster: `xargus.centralus.kusto.windows.net`
Database: `Production`

### Account-Level Performance Percentiles

```kusto
cluster('xargus.centralus.kusto.windows.net').database('Production').AccountPerfPercentiles5M
| where TimeWindow >= datetime({StartTime}) and TimeWindow <= datetime({EndTime})
| where Account == '{StorageAccountName}'
| where EntityType == '{EntityType}'
| where Operation == '{Operation}'
| project TimeWindow, Tenant, Account, EntityType, Operation,
          RequestCount, RequestSizeKB_Avg,
          ServerTimeMs_P50_0, ServerTimeMs_P90_0, ServerTimeMs_P99_0, ServerTimeMs_P99_9
```

Granularity variants:
- `AccountPerfPercentiles5M` — 5-minute granularity
- `AccountPerfPercentiles1H` — 1-hour granularity
- `AccountPerfPercentiles1D` — 1-day granularity

EntityType values: `BlockBlob`, `PageBlob`, `AppendBlob`, `XFile` (Azure Files), `XTable`, `XQueue`

Operation values: `PutBlock`, `PutBlob`, `GetBlob`, `GetBlockList`, `ListBlobs`, etc.

### Tenant-Level (Stamp) Performance Percentiles

```kusto
cluster('xargus.centralus.kusto.windows.net').database('Production').TenantPerfPercentiles5M
| where TimeWindow >= datetime({StartTime}) and TimeWindow <= datetime({EndTime})
| where Tenant == '{TenantName}'
| where EntityType == '{EntityType}'
| where Operation == '{Operation}'
| project TimeWindow, Tenant, EntityType, Operation,
          RequestCount, RequestSizeKB_Avg,
          ServerTimeMs_P50_0, ServerTimeMs_P90_0, ServerTimeMs_P99_0, ServerTimeMs_P99_9
```

Granularity variants: `TenantPerfPercentiles5M`, `TenantPerfPercentiles1H`, `TenantPerfPercentiles1D`

### Elastic SAN Performance (iSCSI)

```kusto
cluster('xargus.centralus.kusto.windows.net').database('Production').AccountPerfPercentiles5M
| where TimeWindow between (datetime({StartTime}) .. datetime({EndTime}))
| where Operation in ("IscsiRead", "IscsiWrite")
| where Tenant == '{TenantName}'
| where Account == '{AccountName}'
```

---

## Storage Billing & Transaction Analysis

### Daily Billing by Meter

Cluster: `xstore.kusto.windows.net`
Database: `xdataanalytics`

```kusto
cluster('xstore.kusto.windows.net').database('xdataanalytics').XStoreAccountBillingDaily
| where TimePeriod >= datetime({StartDate})
| where TimePeriod <= datetime({EndDate})
| where AccountName contains '{StorageAccountName}'
| project TimePeriod, AccountName, StgMeterName, MeterId, ProratedQuantity
| sort by ProratedQuantity desc
```

### Daily Billing by Meter — Filter Specific MeterId

```kusto
cluster('xstore.kusto.windows.net').database('xdataanalytics').XStoreAccountBillingDaily
| where TimePeriod >= datetime({StartDate})
| where TimePeriod <= datetime({EndDate})
| where AccountName contains '{StorageAccountName}'
| where MeterId == '{MeterId}'
| project TimePeriod, AccountName, StgMeterName, MeterId, ProratedQuantity
```

### Daily Transaction Count by Request Type

```kusto
cluster('xstore.kusto.windows.net').database('xdataanalytics').XStoreAccountTransactionsDaily
| where TimePeriod >= datetime({StartDate})
| where TimePeriod <= datetime({EndDate})
| where Account contains '{StorageAccountName};'
| where RequestType in ('ListBlobs','ListContainers','FilterBlobs','Nfs3ReadDir','Nfs3ReadDirPlus','CreateContainer','RestoreContainer')
| summarize sum(BillableTransactionCount) by bin(TimePeriod, 1d), RequestType
```

### Transaction Details with Access Tier

```kusto
cluster('xstore.kusto.windows.net').database('xdataanalytics').AccountTransactionsDaily
| where TimePeriod between (datetime({StartTime})..datetime({EndTime}))
      and BilledSubscription =~ '{SubscriptionId}'
| where AccountName contains '{StorageAccountName}'
| project TimePeriod, RequestType, AccessTier, TransactionType, TransactionCount, BillableTransactionCount
```

### Billing Meter Metadata Lookup (PAV2)

Cluster: `pav2data.eastus.kusto.windows.net`
Database: `aipusageaudit`

```kusto
cluster('pav2data.eastus.kusto.windows.net').database('aipusageaudit').AllMeters
| where ServiceFamily == "Storage"
| summarize arg_max(EffectiveDate, *) by BillingMeterId
| where BillingMeterId == '{BillingMeterId}'
| project BillingMeterId, ConsumptionID, ProductName, SkuName, MeterType, Feature,
          BillingRegion, AvailabilityRegion, MeterStatus, MeterState, Stage,
          Eligibility, AzureInstance, CurrentRate, DirectUOM
```

---

## Storage Account Recovery — Deletion Investigation

Cluster: `armprodgbl.eastus.kusto.windows.net`
Database: `ARMProd` (macro-expand)

### Find ARM Storage Account Deletion Events

```kusto
let SubID = '{SubscriptionId}';
let StorageAccountName = '{StorageAccountName}';
cluster('armprodgbl.eastus.kusto.windows.net').database('ARMProd')
| macro-expand isfuzzy=true ARMProdEG as X (
    X.database('Requests').EventServiceEntries
    | where PreciseTimeStamp >= ago(14d)
    | where subscriptionId == SubID
    | where resourceProvider == "Microsoft.Storage"
    | where resourceUri contains StorageAccountName
    | where operationName has "/storageAccounts/delete"
    | project PreciseTimeStamp, operationName, resourceUri, status, properties, subscriptionId, resourceProvider
)
```

### Find Classic Storage Account Deletion Events

```kusto
cluster('armprodgbl.eastus.kusto.windows.net').database('ARMProd')
| macro-expand isfuzzy=true ARMProdEG as X (
    X.database('Requests').EventServiceEntries
    | where subscriptionId == '{SubscriptionId}'
    | where resourceUri contains '{StorageAccountName}'
    | where PreciseTimeStamp >= ago(14d)
    | where operationName has "/storageAccounts/delete"
    | where resourceProvider has "Microsoft.ClassicStorage"
    | project PreciseTimeStamp, operationName, resourceUri, status, properties, subscriptionId, resourceProvider
)
```

### Storage Deletion Errors (ShoeboxEntries)

```kusto
cluster('Azcsupfollower.kusto.windows.net').database('ARMProd').ShoeboxEntries
| where resourceId contains "/{StorageAccountName}"
| where TIMESTAMP > ago(1d) and resultType == "Failure"
| project PreciseTimeStamp, resourceId, operationName, resultSignature, properties, correlationId
```

---

## Storage Account Failover

### Find Failover Operations

```kusto
cluster('armprodgbl.eastus.kusto.windows.net').database('ARMProd')
| macro-expand isfuzzy=true ARMProdEG as X
(
    X.database('Requests').HttpOutgoingRequests
    | where TIMESTAMP >= ago(30d)
    | where subscriptionId == '{SubscriptionId}' and targetUri contains '{StorageAccountName}'
    | where operationName contains "POST/SUBSCRIPTIONS/RESOURCEGROUPS/PROVIDERS/MICROSOFT.STORAGE/STORAGEACCOUNTS/FAILOVER"
    | project PreciseTimeStamp, subscriptionId, TaskName, ActivityId, correlationId,
              operationName, httpMethod, httpStatusCode, targetUri
)
```

---

## Storage SKU Change / Account Migration

### Find Account Migration Operations

```kusto
let Clusters = entity_group [
    cluster("https://armprodeus.eastus.kusto.windows.net"),
    cluster("https://armprodweu.westeurope.kusto.windows.net"),
    cluster("https://armprodsea.southeastasia.kusto.windows.net")
];
macro-expand isfuzzy = true Clusters as ARMProd
(ARMProd.database("Requests").HttpOutgoingRequests
| where subscriptionId == '{SubscriptionId}'
| where operationName contains "AccountMigrations"
| where targetUri contains '{StorageAccountName}'
| project PreciseTimeStamp, ActivityId, operationName, correlationId,
          subscriptionId, armServiceRequestId, targetUri
)
```

### Find SKU Change Events in Activity Log

```kusto
let Clusters = entity_group [
    cluster("https://armprodeus.eastus.kusto.windows.net"),
    cluster("https://armprodweu.westeurope.kusto.windows.net"),
    cluster("https://armprodsea.southeastasia.kusto.windows.net")
];
macro-expand isfuzzy = true Clusters as ARMProd
(ARMProd.database("Requests").EventServiceEntries
| where subscriptionId == '{SubscriptionId}'
| where resourceUri contains '{StorageAccountName}'
| where TIMESTAMP between (datetime({StartTime})..datetime({EndTime}))
| project PreciseTimeStamp, subscriptionId, ActivityId, correlationId,
          operationName, customerOperationName, properties, httpRequest
)
```

---

## Hybrid Data Migration — StorSimple / Storage Mover

> Wiki: AzureIaaSVM `/SME Topics/Storage Data Migration` — of the 50 TSGs, only this one contains KQL; the rest (AzCopy / Storage Mover Agent Offline / Redundancy) are all client-tool error troubleshooting + network connectivity + Support Bundle analysis, not Kusto.

### StorSimple Migration — Get Job Summary with Error Details

Use `JobId` to find the status and ErrorDetails of a migration job's 5 stages (Backup → ConfigureCompute → EstimatingFiles → CopyingFiles → CleanupCompute).

```kusto
cluster("https://hdmprod.kusto.windows.net").database("HybridDataServiceProd").DmsJobStats
| where PreciseTimeStamp > ago(10d)
| where JobId == '{JobId}'
| parse JobStages with "StageName:Backup, StageStatus:" BackupResult ", JobStageDetails:" *
        "StageName:ConfigureCompute, StageStatus:" EstimationConfigureComputeResult ", JobStageDetails:" *
        "StageName:EstimatingFiles, StageStatus:" EstimatingFilesResult ", JobStageDetails:" *
        "StageName:CopyingFiles, StageStatus:" CopyingFilesResult ", JobStageDetails:" *
        "StageName:CleanupCompute, StageStatus:" CleanupComputeResult ", JobStageDetails:" *
| project PreciseTimeStamp, JobStatus, JobId, ErrorDetails, JobDefinitionName, DeploymentName,
          RunHrs = JobExecutionTimeInMin / 60,
          EstimatedGB = BytesProcessedInEstimation / 1024 / 1024 / 1024,
          ProcessedGB = ByteProcessed / 1024 / 1024 / 1024,
          BackupResult, EstimatingFilesResult, CopyingFilesResult,
          ComputeResult = EstimationConfigureComputeResult,
          CleanupCompute = CleanupComputeResult,
          EstimatedItems = ItemsProcessedInEstimation, ItemProcessed, SubscriptionId
| order by PreciseTimeStamp desc
```

**Field interpretation**:
- `JobStatus` — overall status (Running / Completed / Failed)
- `ErrorDetails` — pinpoints the failure cause directly
- `BackupResult` / `EstimatingFilesResult` / `CopyingFilesResult` / `ComputeResult` / `CleanupCompute` — per-stage success/failure for the 5 stages; shows which step is stuck
- `RunHrs` — elapsed runtime
- `EstimatedGB` vs `ProcessedGB` — progress estimate

**Wiki source**: [StorSimple Migration & Get Job Summary with Error Details](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/_/StorSimple-Migration-%26-Get-Job-Summary-with-Error-Details_Storage)

**Note**: Other Storage Data Migration TSGs such as Storage Mover Agent Offline / AzCopy v10 **do not need Kusto** — they use `azcmagent check` network tests + Support Bundle (xdmreg.log / xdatamoved.log) text analysis; use the `vm-log-analyzer` skill.

---

## Storage Throttling Investigation

### ARM-Level Storage Throttling Trace

```kusto
cluster('armprodgbl.eastus.kusto.windows.net').database('ARMProd')
| macro-expand isfuzzy=true ARMProdEG as X (
    X.database('Storage').StorageOperations
    | where PreciseTimeStamp between (datetime({StartTime})..datetime({EndTime}))
    | where correlationId =~ trim(" ", "{CorrelationId}")
    | project-reorder PreciseTimeStamp, SourceNamespace, operationName, TaskName,
                      resourceType, resourceName, accountName, exceptionMessage
    | sort by PreciseTimeStamp asc
)
```

Common throttling error messages:
- `Operations per second is over the account limit.`
- `The server is busy.` (ServerBusy 503)

---

## Azure Files Performance — Metadata Throttling

Cluster: `azcore.centralus.kusto.windows.net`
Database: `Xstore`

### XStoreXFileThrottleTransaction — File Share Throttle Analysis

```kusto
let startDate = datetime({StartTime});
let endDate = datetime({EndTime});
let storageAccounts = (
    cluster("xstore.kusto.windows.net").database("xstore").StorageAccountCapTX
    | where AccountName has '{StorageAccountName}'
    | project
        timestamp = Timestamp,
        clusterName = Tenant,
        subscriptionId = SubscriptionId,
        Account = AccountName,
        storageAccountCreateDate = AccountCreationTime,
        fileShareCount = FileContainerCount,
        provisionedSizeTiB = XFileProvisionedBytes / pow(1024, 4)
);
cluster("azcore.centralus.kusto.windows.net").database("Xstore").XStoreXFileThrottleTransaction
| where TIMESTAMP between (startDate..endDate)
| extend storageAccountInfoArr = split(Account, ";")
| extend Account = tostring(storageAccountInfoArr[0])
| join hint.strategy=shuffle kind=inner (storageAccounts) on Account
| summarize provisionedSizeTiB = avg(provisionedSizeTiB),
            sum(SuccessWithMetadataWarning), avg(MinFileMetadataIopsWithWarning),
            sum(SuccessWithMetadataThrottling), avg(MinFileMetadataIopsWithThrottling),
            sum(SuccessWithServerBusy)
  by Account, TTPName, Tenant
```

---

## Azure Files Metadata Caching Configuration

### Check If Account Is Onboarded for Metadata Caching

Cluster: `xstore.kusto.windows.net`
Database: `XStoreNRT`

```kusto
cluster('xstore.kusto.windows.net').database('XStoreNRT').Xstore_DynamicConfigLatestValue
| where env_time > ago(1d)
| where env_cloud_environment == "Production"
| summarize arg_max(env_time, *) by env_cloud_name, SettingName, env_name
| where SettingName == "XStoreConfigSettings.XTableServer.XSmbXCacheRuntimeStateWhitelistedKeyRanges"
| where isnotempty(SettingValue)
| project KeyRange = split(SettingValue, ' '), env_cloud_name
| mv-expand KeyRange
| where KeyRange has '{StorageAccountName}'
| project RTSEnabledAccounts = substring(KeyRange, 0, indexof(KeyRange, ";")), env_cloud_name
```

### Track Metadata Caching Config Changes

Cluster: `azcore.centralus.kusto.windows.net`
Database: `Xstore`

```kusto
cluster('azcore.centralus.kusto.windows.net').database('Xstore').DynamicConfigChangedEvent
| where env_time > ago(7d)
| where env_cloud_name == '{TenantName}'
| where SettingName contains "XSmbXCacheRuntimeStateWhitelistedKeyRanges"
| where SettingCurrentValue contains '{StorageAccountName}'
| project env_time, Operation, SettingName, SettingCurrentValue, SettingPreviousValue, Tenant=env_cloud_name
| order by env_time asc
```

---

## XStore Disk Triage (Disk IO / Blackout)

Cluster: `xlivesite.kusto.windows.net`
Database: `XHealthDiskTriage`

### XStore Disk Blackout Triage

```kusto
cluster('xlivesite.kusto.windows.net').database('XHealthDiskTriage').XHealth_DiskBlackoutXStoreTriage
| where EventTime between (datetime({StartTime})..datetime({EndTime}))
| where NodeId == '{NodeId}'
| project EventTime, TriageCategory, TriageReason, TriageTimestamp,
          StorageRegion, StorageTenant, NodeId
```

### XStore Disk Failure Triage

```kusto
cluster('xlivesite.kusto.windows.net').database('XHealthDiskTriage').XHealth_DiskFailureXStoreTriage
| where EventTime between (datetime({StartTime})..datetime({EndTime}))
| where NodeId == '{NodeId}'
| project EventTime, TriageCategory, TriageReason, TriageTimestamp,
          StorageRegion, StorageTenant, NodeId
```

### Disk IO Blip Events (VMAInsight)

```kusto
cluster('vmainsight.kusto.windows.net').database('Air').AirDiskIOBlipEvents
| where EventTime between (datetime({StartTime}) .. datetime({EndTime}))
| where NodeId == '{NodeId}' and VirtualMachineUniqueId == '{VmId}'
| where TotalIOsGt1s > 0
| project EventTime, RoleInstanceName, RCAType, RCALevel1, RCALevel2, RCALevel3,
          BlobPath, VirtualMachineUniqueId, Customer, SubscriptionId
```

---

## Cloud Shell Storage Account Identification

Cluster: `accprod.kusto.windows.net`
Database: `cloudshellprod`

```kusto
cluster('accprod.kusto.windows.net').database('cloudshellprod').TenantDeployments
| where TIMESTAMP > ago(15m)
| where principalPuid == '{NetID}'
| where containerLog != ""
```

---

## Customer Diagnostic Logs (Log Analytics)

For storage accounts with diagnostic logging enabled, the following queries run against the customer's Log Analytics workspace (not Kusto clusters):

### Blob Storage 404 Error Trend

```kusto
// Note: StorageBlobLogs is a customer-side Log Analytics table, not an internal Kusto cluster.
// Run this in the customer's Log Analytics workspace.
StorageBlobLogs
| where StatusCode == 404
| summarize Count = count() by bin(TimeGenerated, 1h)
```

### TLS Version Check (Azure Resource Graph)

```kusto
// Note: This is an Azure Resource Graph query. Run via az graph query or portal.azure.com
resources
| where type =~ "Microsoft.Storage/storageAccounts"
| extend minimumTlsVersion = parse_json(properties).minimumTlsVersion
| project subscriptionId, resourceGroup, name, minimumTlsVersion
```

---

## Quick Reference — When to Use Which Query

| Scenario | First Query | Cluster.DB |
|----------|------------|------------|
| Check account type / redundancy / config | `XStoreAccountProperties` | azcore.Xstore |
| Find which stamp hosts the account | `AccountCapacityDailyV3` | xstore.xstore |
| Account performance / latency investigation | `AccountPerfPercentiles5M` | xargus.Production |
| Stamp-wide performance health check | `TenantPerfPercentiles5M` | xargus.Production |
| Storage billing breakdown | `XStoreAccountBillingDaily` | xstore.xdataanalytics |
| Transaction count by operation | `XStoreAccountTransactionsDaily` | xstore.xdataanalytics |
| Billing meter lookup | `AllMeters` | pav2data.aipusageaudit |
| Who deleted the storage account | `EventServiceEntries` (ARM) | armprodgbl.ARMProd |
| Storage account failover status | `HttpOutgoingRequests` (ARM) | armprodgbl.ARMProd |
| SKU change / migration tracking | `HttpOutgoingRequests` (ARM) | armprodgbl.ARMProd |
| Storage throttling trace | `StorageOperations` (ARM) | armprodgbl.ARMProd |
| Azure Files metadata throttling | `XStoreXFileThrottleTransaction` | azcore.Xstore |
| Metadata caching onboarding check | `Xstore_DynamicConfigLatestValue` | xstore.XStoreNRT |
| XStore disk blackout / failure | `XHealth_DiskBlackoutXStoreTriage` | xlivesite.XHealthDiskTriage |
| Disk IO blip RCA | `AirDiskIOBlipEvents` | vmainsight.Air |
| Elastic SAN performance | `AccountPerfPercentiles5M` (IscsiRead/Write) | xargus.Production |
| Geo-replication SLA check | `XStoreAccountProperties` + `GeoReplicationConfig` | azcore.Xstore |
| StorSimple migration job | `DmsJobStats` (parse 5 stages) | hdmprod.HybridDataServiceProd |

---

## Wiki Source Pages

| Topic | ADO Wiki Page (pageId) |
|-------|----------------------|
| XArgus Performance Investigation | [Use XArgus to Investigate XStore Issues](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/1303459) |
| Storage Billing with Troubleshooter | [Check Storage Billing with Troubleshooter](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/1066847) |
| Storage Billing Usage | [Check Storage Billing Usage](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/496135) |
| ARM Storage Account Recovery | [ARM Storage Account Recovery](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/748069) |
| Classic Storage Account Recovery | [Classic Storage Account Recovery](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/748071) |
| Storage Throttling | [Storage Throttling](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/496124) |
| Customer Managed Planned Failover | [Customer Managed Planned Failover TSG](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/1933066) |
| Storage SKU Change Billing | [Storage SKU Change Billing Check](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/2188505) |
| Geo Priority Replication SLA | [Storage Geo Priority Replication SLA TSG](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/2326054) |
| Storage Tenant Health Check | [Storage Tenant Health Check](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/1429515) |
| Azure Files Metadata Performance | [Azure Files Heavy Metadata Performance](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/1832156) |
| Files Metadata Caching | [Check Storage Account Metadata Caching](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/2182736) |
| Find SA Tenant/Stamp | [Check Storage Cluster VM Disks or SA](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/496257) |
| Unable to Delete Storage | [Unable to Delete Workflow](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/496242) |
| Elastic SAN Performance | [Elastic SAN Performance](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/1790667) |
| Kusto Endpoints | [Kusto Endpoints](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/496459) |
| StorSimple Migration Job Summary | [StorSimple Migration & Get Job Summary with Error Details](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/_/StorSimple-Migration-%26-Get-Job-Summary-with-Error-Details_Storage) |
