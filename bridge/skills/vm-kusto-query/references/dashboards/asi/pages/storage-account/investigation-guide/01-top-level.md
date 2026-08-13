# (top-level)

> Source: **Storage Account Investigation Guide** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Storage Account"

_Widget purpose:_ {{StorageAccountName}}

Cluster: `azcore.centralus` · Database: `Xstore` · Type: `ResourceGet` · Widget: `Container`

```kusto
let offsetTimeInMinutes = datetime_diff('minute', globalTo, globalFrom);
cluster('azcore.centralus').database('Xstore').XStoreAccountProperties
| where TIMESTAMP between(globalFrom .. globalTo) 
| where Account startswith strcat(trim(@"[\s]+", local_StorageAccountName), ";") 
| where IsPrimaryReplica == 1
| summarize arg_max(TIMESTAMP, *) by Account, Subscription, AccountType, ResourceGroup
| extend StorageAccountName= split(Account, ';')[0]
| extend ResourceUri=strcat("/subscriptions/",Subscription,"/resourceGroups/",ResourceGroup,"/providers/",iff(IsSrp == 1, "Microsoft.Storage", "Microsoft.ClassicStorage"),"/storageAccounts/",StorageAccountName)
| extend TenantName = split(Tenant, "-")[1]
| extend IsSrp = iff(IsSrp == 1, true, false), IsXio = iff(IsXio == 1, true, false), IsPrimaryReplica = iff(IsPrimaryReplica == 1, true, false), IsLifecycleManagementEnabled = iff(IsLifecycleManagementEnabled == 1, true, false),
IsChangeFeedEnabled = iff(IsChangeFeedEnabled == 1, true, false), IsBlobInventoryEnabled = iff(IsBlobInventoryEnabled == 1, true, false), IsHnsEnabled = iff(IsHnsEnabled == 1, true, false), IsValidForBilling = iff(IsValidForBilling == 1, true, false),
IsAccountBillingDisabled = iff(IsAccountBillingDisabled == 1, true, false)
| extend Properties = todynamic(Properties)
| extend XlsServiceMetadata = todynamic(XlsServiceMetadata)
| extend IsSoftDeleteEnabled = Properties.BlobDeleteRetentionEnabled
| extend SoftDeleteRetentionDays = Properties.BlobDeleteRetentionDays
| extend BlobStaticWebsiteEnabled = Properties.BlobStaticWebsiteEnabled
| extend IsManagedBySrp = Properties.IsManagedBySrp
| extend allowBlobPublicAccess = XlsServiceMetadata.allowBlobPublicAccess
| extend allowKeyBasedAccess = XlsServiceMetadata.allowSharedKeyAccess
| extend IsContainerSoftDeleteEnabled = XlsServiceMetadata.containerDeleteRetentionPolicy.enabled
| extend ContainerSoftDeleteRetentionDays = XlsServiceMetadata.containerDeleteRetentionPolicy.retentionDays
| extend minimumTlsVersion = XlsServiceMetadata.minimumTlsVersion
| extend isLargeFileSharesEnabled = XlsServiceMetadata.isLargeFileSharesEnabled
| extend publicNetworkAccess = XlsServiceMetadata.publicNetworkAccess
| extend IsRegionalAccount = (XlsServiceMetadata.virtualizationType contains "RegionalFE")
| extend supportsHttpsTrafficOnly = XlsServiceMetadata.supportsHttpsTrafficOnly
| extend offsetTimeInMinutes = offsetTimeInMinutes
// Build Header msg
| extend HeaderMsg = strcat("<span style='color: orange'>PLEASE NOTE: The metadata listed below last updated at ", TIMESTAMP, "</span>")
// if Account not found, retuns empty line instead of ASI resource was found error and cat image, with a red header msg
| union (        
    print Account="", HeaderMsg = strcat("<span style='color:red'><b>",trim(@"[\s]+", local_StorageAccountName),"</b> Account Name not found</span>")
)
| sort by Tenant nulls last
| limit 1
```

**Params:** `{local_StorageAccountName}`, `{globalFrom}`, `{globalTo}`

---
