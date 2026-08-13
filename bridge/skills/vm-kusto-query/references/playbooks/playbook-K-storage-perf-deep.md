# Playbook K — Storage Performance / Throttling — Deep

> **Routed from** [`playbook-K-storage-perf-core.md`](./playbook-K-storage-perf-core.md). INLINE style — KQL bodies live here, supplemented by [`references/storage-account-queries.md`](../catalogs/storage-account-queries.md) § Storage Performance — XArgus.
>
> Scope: storage account performance + throttling + latency RCA — Blob / Page Blob / Table / Queue. **NOT Azure Files** (→ L); **NOT SA control-plane / billing / recovery** (→ J); **NOT managed-disk perf** (→ Playbook F); **NOT guest-OS perf** (→ Playbook G).

[[_TOC_]]

## Cluster shortcuts (for KQL bodies)

| Shorthand | Full path |
|---|---|
| `xargus.Production` | `cluster('xargus.centralus.kusto.windows.net').database('Production')` |
| `armprodgbl.ARMProd.Storage` | `cluster('armprodgbl.<region>.kusto.windows.net').database('ARMProd')` macro-expand → `Storage` DB |
| `azcore.Xstore` | `cluster('azcore.kusto.windows.net').database('Xstore')` (for SA properties / tenant lookup — cross-link to J utility) |
| `xstore.xstore` | `cluster('XStore').database('xstore')` (for stamp / account capacity — cross-link to J) |
| `azcore.Xstore` (centralus) | `cluster('azcore.centralus.kusto.windows.net').database('Xstore')` (for XStoreXFileThrottleTransaction — Files metadata throttling) |

## Anchor Index

### SA Performance — ARM-side XStore throttling
- [`SA-Perf-ARM-XStore-Throttle`](#sa-perf-arm-xstore-throttle--arm-503-on-internal-xstore-call-operations-per-second-over-account-limit-or-server-is-busy) — ARM 503 on internal XStore call (`Operations per second over account limit` OR `Server is busy`)

### SA Performance — SA-level throttling + activity check
- [`SA-Perf-CheckActivity`](#sa-perf-checkactivity--check-storage-account-activity-via-asc--xportal--azure-monitor--diagnostic-logs) — Check Storage Account Activity via ASC + XPortal + Azure Monitor + Diagnostic Logs
- [`SA-Perf-SAThrottle`](#sa-perf-sathrottle--sa-level-throttling-iops-ingress-egress-scalability-target-hit) — SA-level throttling (IOPS / Ingress / Egress scalability target hit)

### SA Performance — XArgus latency RCA
- [`SA-Perf-XArgus-Account`](#sa-perf-xargus-account--account-level-latency-percentiles-via-xargus-p50p90p99p999--auth-fe-tableserver-stream-breakdown) — Account-level latency percentiles via XArgus (P50/P90/P99/P99.9) + Auth/FE/TableServer/Stream breakdown

### SA Performance — Tenant / stamp health
- [`SA-Perf-TenantHealth`](#sa-perf-tenanthealth--storage-tenant-stamp-level-health-check--xargus-tenant-percentiles--xportal-tenant-dashboard) — Storage Tenant (stamp) level health check + XArgus tenant percentiles + XPortal tenant dashboard
- [`SA-Perf-PartitionDowntime`](#sa-perf-partitiondowntime--jarvis-mdmgeneva-xstorepartitiondowntimeevent--load-balancing-split-events) — Jarvis MDM/Geneva `Xstore.PartitionDowntimeEvent` + load balancing / split events

### SA Performance — Page Blob deep dive
- [`SA-Perf-PageBlob`](#sa-perf-pageblob--azure-page-blob-deep-dive--xblobfe-getpageputpage-+-scalability-targets-+-mdm-frontend-logs) — Azure Page Blob deep dive + XBlobFE GetPage/PutPage + scalability targets + MDM FrontEnd logs

### SA Performance — Azure Files backend (XStore-side; client-side SMB/NFS → L)
- [`SA-Perf-AzureFiles-Backend`](#sa-perf-azurefiles-backend--azure-files-share-backend-perf-investigation--xfilefe-readwrite-+-per-share-1000-iops--60-mbs-limits-+-cross-zone-traffic-detection-+-mdm-xstorefrontendsummaryperflogs--xnfsperfmetric--xsmbperfmetric) — Azure Files share backend perf investigation (XFileFE Read/Write + per-share 1000 IOPS / 60 MB/s limits + Cross-Zone Traffic detection + MDM `Xstore.FrontEndSummaryPerfLogs / XNfsPerfMetric / XSMBPerfMetric`)
- [`SA-Perf-AzureFiles-HeavyMetadata`](#sa-perf-azurefiles-heavymetadata--azure-files-heavy-metadata-throttling--successwithmetadatawarning--successwithmetadatathrottling-rca-via-xstorexfilethrottletransaction-+-metadata-iops-tier-table) — Heavy Metadata throttling RCA (`SuccessWithMetadataWarning` / `SuccessWithMetadataThrottling` ResponseTypes + 1 KQL `XStoreXFileThrottleTransaction` joined to `StorageAccountCapTX` + metadata IOPS tier table)
- [`SA-Perf-AzureFiles-MetadataCaching`](#sa-perf-azurefiles-metadatacaching--premium-smb-files-metadata-caching-runtime-state-preview--primary-fix-path-for-heavy-metadata-throttling--afec-feature-registration-+-region-list-+-no-backend-verification-+-pm-contacts) — Premium SMB Files Metadata Caching (Runtime State Preview) — primary fix path for heavy-metadata throttling (AFEC feature registration + region list + no backend verification today + PM contacts)
- [`SAF-AzureFiles-PerfWorkflow`](#saf-azurefiles-perfworkflow--cross-link-stub-azure-files-performance-workflow-master-entry-point--scoping-questions--internal-data-collection--perfinsights-azurefiles-scenario--labbox--guest-os-funnels-to-L) — Cross-link stub: Azure Files Performance Workflow master entry-point (scoping questions + internal data collection + PerfInsights `azurefiles` scenario + LabBox + Guest OS funnels to L)

### Cross-link stubs (NOT deep — routes elsewhere)
- [`SAF-Win-Explorer-Slow`](#saf-win-explorer-slow--cross-link-stub-azure-files-smb-windows-explorer-slow-file-opensaveclose---registry-workaround) — Cross-link stub: Azure Files SMB Windows Explorer slow file open/save/close → registry workaround
- [`LinuxOSDisk-Full`](#linuxosdisk-full--cross-link-stub-linux-os-disk-full-no-space-left-on-device---du-locate-+-rotate-+-cleanup) — Cross-link stub: Linux OS disk full → du locate + rotate + cleanup

## Reusable terminology (Azure Storage Performance)

| Term | Meaning |
|---|---|
| **Availability(%)** | % storage subsystem up. Drop = SERVER-side issue (LB op / subsystem failure / hardware) |
| **Perceived Availability(%)** | % from client view. Drop = CLIENT-side / throttling (subsystem was up but request failed by policy) |
| **Server Latency (ms)** | Time storage subsystem took to process the request |
| **Client Latency (ms)** | End-to-end (client→server→client) — includes network |

### Latency-interpretation rule of thumb

| ServerLat | ClientLat | Diagnosis |
|---|---|---|
| 5 ms | 12 ms | Healthy (5ms proc + 7ms net) |
| 15 ms | 900 ms | **CLIENT-side / network problem** (885ms net) |
| 1000 ms | 1100 ms | **SERVER-side problem** (1s proc + 100ms net) |

### Reference latency (INTERNAL ONLY — do NOT share with customer)
- Standard Storage: 2-digit ms typical
- Premium Storage: 1-digit ms typical
- **NO public SLA on Storage latency**

---

## SA-Perf-ARM-XStore-Throttle — ARM 503 on internal XStore call (`Operations per second over account limit` OR `Server is busy`)

### Symptom
Customer-impacting ARM API failure with HTTP **503 ServiceUnavailable** caused by ARM's internal calls to XStore being throttled. Customer sees transient ARM API failure; underlying XStore returned throttle response.

### Error signatures (two variants)
Both indicate ARM-to-XStore call throttled — transient, retryable.

```
StatusMessage: Operations per second is over the account limit.
```
```
StatusMessage: The server is busy.
ErrorMessage: 0:The server is busy.
```

Exception chain (typical):
```
Microsoft.WindowsAzure.Storage.StorageException: Unexpected HTTP status code 'ServiceUnavailable'.
   ---> System.Net.WebException: The remote server returned an error: (503) Server Unavailable.
   at System.Net.HttpWebRequest.EndGetResponse(IAsyncResult asyncResult)
```

### Reference incidents
Parent ICM: 234324617. Mitigated **2021-04-21**. Recurrences are typically transient.

### Detection KQL (`armprodgbl.<region>.ARMProd.Storage.StorageOperations` — macro-expand all ARMProd regions)
```kusto
cluster('armprodgbl.eastus.kusto.windows.net').database('ARMProd')
| macro-expand isfuzzy=true ARMProdEG as X (
   X.database('Storage').StorageOperations
   | where PreciseTimeStamp between (datetime({StartTime})..datetime({EndTime}))
   | where correlationId =~ trim(" ", "{correlation_id}")
   | project-reorder PreciseTimeStamp, SourceNamespace, operationName, TaskName,
                     resourceType, resourceName, accountName, exceptionMessage
   | sort by PreciseTimeStamp asc
)
```

Expected output (faulted entry sample):
```
PreciseTimeStamp                   SourceNamespace   operationName                                                  resourceType  resourceName       accountName             operationStatus  exceptionMessage
2021-03-29 07:12:30.1341411        csmNorthEuropeRPF StorageDataProvider.FindRangeSegmented.Resource                table         resources007       rpfdloc03proddb01       Faulted          Microsoft.WindowsAzure.Storage.StorageException: Unexpected HTTP status code 'ServiceUnavailable'...
```

Look at the `exceptionMessage` tail — `StatusMessage:` line reveals which throttle variant fired.

### ⚠ Collab note
If you are NOT from CSS ARM team:
1. **Open collab with CSS ARM team FIRST** — they own the upstream ARM call.
2. **Do NOT open a new ICM** — the parent ICM is already in place and the issue is well-understood.
3. If recurrence appears systemic (not transient), CSS ARM will engage XStore PG via their established channel.

### Mitigation
- **Tactical**: Customer retries the operation per [General REST and retry guidelines](https://docs.microsoft.com/en-us/azure/architecture/best-practices/retry-service-specific#general-rest-and-retry-guidelines).
- **Long-term**: ARM team owns rate-limiting and retry behavior; no customer-side config.

### Customer-facing RCA template
> Hi {customer},
>
> Thank you for reaching out to Microsoft Azure Support. We have completed the analysis of {problem statement}. Azure is a multi-regional product, where relative information of resources and their state needs to be replicated across multiple regions. Our investigation discovered that the issue that you encountered on {date} was caused by a **transient failure when attempting to connect to Azure Resource Manager's internal storage**. We want to apologize for any inconvenience that this may have caused, and we are continuously working on improving the platform to prevent these types of failures in the future.
>
> We recommend reviewing the following [General REST and retry guidelines](https://docs.microsoft.com/en-us/azure/architecture/best-practices/retry-service-specific#general-rest-and-retry-guidelines).
>
> Again, we apologize for any inconvenience that this may have caused.
>
> Sincerely,
> Microsoft Azure

### Related references
- [ARM vs RP Throttling explained](https://dev.azure.com/Supportability/AzureDev/_wiki/wikis/AzureDev/545681/Throttling?anchor=arm-vs-rp-throttling)
- [Understanding ARM throttling Error 429](https://dev.azure.com/Supportability/AzureDev/_wiki/wikis/AzureDev/469399/Throttling-(Error-429)-response-from-ARM)
- [Storage Service Throttling Timeouts (Dev_Storage 1833046)](https://supportability.visualstudio.com/AzureDev/_wiki/wikis/Dev_Storage/1833046/Storage-Service-Throttling-Timeouts) — pro tip from the source TSG: for 503s and Blob API throttling, this Dev_Storage page is the canonical reference; if a .NET or SDK consumer is hitting it, Dev Storage may be a better case owner.

---

## SA-Perf-CheckActivity — Check Storage Account Activity (via ASC + XPortal + Azure Monitor + Diagnostic Logs)

### Purpose
Foundation TSG referenced from every K anchor. Determines whether a SA is actively used + whether usage matches a reported spike — both for internal investigation and customer-facing tooling.

### Tooling matrix

| View | Tool | Useful for |
|---|---|---|
| **Internal** | Azure Support Center (ASC) | Historical + latest transactions, graphical view |
| **Internal** | XPortal (XDS Legacy) | Historical + latest transactions, graphical view |
| **External** (customer) | Azure Monitor Storage Metrics | Customer-visible: historical + latest transactions, graphical view |
| **External** (customer) | Storage Diagnostic Logging | IO-level detail: Client IP, User Agent, request type (PUT/GET/DELETE/etc.) |

### Internal — XPortal (XDS Legacy)
1. https://xportal.trafficmanager.net/sla/account
2. Enter SA name in "Account" field
3. Tenant auto-populates
4. Select UTC time period
5. Granularity: Hourly / Daily / Realtime
6. Review metrics (Transactions/Sec, Transactions, Ingress, Egress per API)

### Internal — Azure Support Center (ASC)
1. https://azuresupportcenter.msftcloudes.com/ticketdetails
2. Resource Explorer → search Storage Account
3. Performance tab
4. Filter Timeframe + All services
5. Review metrics → analysis

### Relevant APIs / Roles
- **Total / All**: aggregate
- **XFileFe All / File** | **XBlobFe All / Blob** | **XTableFe All / Table** | **XQueueFe All / Queue**: per-API breakdown

### Metrics
1. Transactions/Sec / Account IOPS
2. Transactions
3. Ingress + Egress

### External — Azure Monitor (customer-runs)
- [Access metrics in Azure portal](https://learn.microsoft.com/en-us/azure/storage/blobs/monitor-blob-storage?tabs=azure-portal#analyzing-metrics)
- [Access metrics with PowerShell](https://learn.microsoft.com/en-us/azure/storage/blobs/monitor-blob-storage?tabs=azure-powershell#analyzing-metrics)
- [Storage Insights overview](https://learn.microsoft.com/en-us/azure/storage/common/storage-insights-overview)

### External — Diagnostic Logging (must be enabled BEFORE the issue)
Required enable steps (Blob / Queue / Table — Files separate):
- [Monitor Azure Blob Storage](https://learn.microsoft.com/en-us/azure/storage/blobs/monitor-blob-storage?tabs=azure-portal#collection-and-routing)
- [Monitor Azure Files](https://learn.microsoft.com/en-us/azure/storage/files/storage-files-monitoring?tabs=azure-portal#collection-and-routing)
- [Monitor Azure Queue Storage](https://learn.microsoft.com/en-us/azure/storage/queues/monitor-queue-storage?tabs=azure-portal#collection-and-routing)
- [Monitor Azure Table Storage](https://learn.microsoft.com/en-us/azure/storage/tables/monitor-table-storage?tabs=azure-portal#collection-and-routing)

Access / analysis:
- [Analyzing Blob logs](https://learn.microsoft.com/en-us/azure/storage/blobs/monitor-blob-storage?tabs=azure-portal#analyzing-logs)
- [Analyzing Files logs](https://learn.microsoft.com/en-us/azure/storage/files/storage-files-monitoring?tabs=azure-portal#analyzing-logs)

### Lab (training only)
https://aka.ms/LabBox — `azCopyBenchmark.json` deploys a VM with this scenario built-in. NOT shareable with customers.

---

## SA-Perf-SAThrottle — SA-level throttling (IOPS / Ingress / Egress scalability target hit)

### Symptom
- Customer reports 429 / `Throttling` errors on Storage Account
- SA dashboard shows: **Throttling Errors(%)** rising, **Bandwidth Throttling** / **IOPS Throttling** / **Server Throttling (amount)** counters non-zero
- **Perceived Availability(%) / Customer Perceived Availability(%)** drops (client-side observable)
- **Availability(%)** remains stable (server is healthy — request failed by limit policy)

### Tooling

#### XPortal (MDM) — Shoebox API Investigation
1. https://xportal.trafficmanager.net/sla/mdm/account/$/dashboards
2. Enter SA name → Refresh
3. Open **Shoebox API Investigation Dashboard**
4. Time range filter
5. ObjectType filter: BlockBlob / DiskPageBlob / PageBlob / Queue / Table / File
6. Authentication + API filters

#### Azure Support Center (ASC) — Performance tab
1. https://azuresupportcenter.msftcloudes.com/ticketdetails
2. Resource Explorer → SA → Performance
3. Filter Timeframe + All services (or specific API)

### Metrics checklist
1. **Perceived Availability(%)** drop → client-side throttling
2. **Availability(%)** drop → SERVER-side problem (see § SA-Perf-TenantHealth)
3. **Throttling Errors(%)** + bandwidth/IOPS/server throttling amounts
4. **Transactions/Sec / Account IOPS** — vs **20,000 IOPS** baseline limit (some Standard SAs eligible for **50,000 IOPS** per [Announcing larger, higher scale storage accounts](https://azure.microsoft.com/en-us/blog/announcing-larger-higher-scale-storage-accounts/))
5. **Ingress / Egress** — vs published [Scalability targets for a storage account](https://docs.microsoft.com/en-us/azure/storage/common/storage-scalability-targets#scalability-targets-for-a-storage-account)

### Analysis decision tree

#### SA throttling confirmed
1. Per-API check: re-run the metrics above filtered by the affected API (XBlobFE / XFileFE / etc.)
2. If non-XBlobFE → engage the API-specific team or recommend customer migrate
3. If XBlobFE Page Blob → continue to § [SA-Perf-PageBlob](#sa-perf-pageblob--azure-page-blob-deep-dive--xblobfe-getpageputpage-+-scalability-targets-+-mdm-frontend-logs)

#### Not confirmed at SA level
Use MDM(Jarvis/Geneva) Storage Account API Errors (template `Azure-Storage-Front-End-Logs-Blob.md`). Search for:
- **Blob/s** being throttled
- **RequestUrl** (path accessed)
- **Status / InternalStatus** (throttle cause)
- **ClientIP** (source of traffic)
- **UserAgent** (method of access)

Only ERROR operations are logged (successful ops not visible here).

### Mitigation
- **Customer-side**: implement retry per [General REST and retry guidelines](https://docs.microsoft.com/en-us/azure/architecture/best-practices/retry-service-specific#general-rest-and-retry-guidelines) + see [Storage Service Throttling Timeouts (Dev_Storage 1833046)](https://supportability.visualstudio.com/AzureDev/_wiki/wikis/Dev_Storage/1833046/Storage-Service-Throttling-Timeouts) for timeout-specific guidance
- **Architecture**: reduce per-blob TX, leverage multiple SAs (sharding), move hot blobs to separate SA
- **Quota**: J § SA-Mgmt-IncreaseLimits (ICM template `O2tP1h` → XStore Quota team) — only if customer is genuinely beyond published targets

### Cross-link
For TACTICAL retry guidance (basics) → **Playbook C § THR-Perf-3 / 4**. K owns the DEEP RCA.

---

## SA-Perf-XArgus-Account — Account-level latency percentiles via XArgus (P50/P90/P99/P99.9) + Auth/FE/TableServer/Stream breakdown

### Symptom
- Customer reports SA Blob / Table / Queue latency spike (high P99 / P99.9)
- ASC / XPortal shows Server Latency higher than normal — need percentile-level + per-layer breakdown
- Need the **Server Request Id of the highest-latency request** for AutoAnalysis acceleration

### Data flow (intel — explains the 25min SLA + 5M granularity)
XStore FEs (and soon TSes) → exponential histograms → XAgg `XArgus Health` role → aggregates per 5m → pushes to WarmPath (MDS) → Geneva Delivery Service → XArgus Skywalker Regional Kusto DBs → main cluster `xargus.centralus.kusto.windows.net`. On main cluster: histograms parsed, percentiles computed via logarithmic interpolation.

**SLA**: 99% of data arrives within **25 minutes** of XStore source. Granularities: 5M / 1H / 1D.

### Access — REQUIRED entitlements
Go to https://aka.ms/CoreIdentity:
1. **XArgusKustoAccess** → permission level **Viewer**
2. **XStorePartnersKusto** → permission level **XP_AllDB_ReadOnly**

Business justification REQUIRED on submission:
- Team Name
- Tables planned to access + why
- XStore Engg you are working with

Propagation: up to **24h**. Acceptance SLA: **48h**. Missing justification = denied.

### Tables (cluster: `xargus.centralus.kusto.windows.net` / DB: `Production`)

| Scope | 5M | 1H | 1D |
|---|---|---|---|
| Account | `AccountPerfPercentiles5M` | `AccountPerfPercentiles1H` | `AccountPerfPercentiles1D` |
| Tenant (stamp) | `TenantPerfPercentiles5M` | `TenantPerfPercentiles1H` | `TenantPerfPercentiles1D` |

### KQL — Account latency percentiles
```kusto
cluster('xargus.centralus.kusto.windows.net').database('Production').AccountPerfPercentiles5M
| where TimeWindow >= ago(1h)
| where EntityType == "BlockBlob"
| where Operation == "PutBlock"
| where Account == "{StorageAccountName}"
| project TimeWindow, Tenant, Account, EntityType, Operation, RequestCount, RequestSizeKB_Avg,
          ServerTimeMs_P50_0, ServerTimeMs_P90_0, ServerTimeMs_P99_0, ServerTimeMs_P99_9
| take 10
```

Replace `EntityType` (BlockBlob / PageBlob / Table / Queue / File) and `Operation` (PutBlock / GetBlob / GetPage / PutPage / etc.) per case.

### Latency-layer interpretation
XArgus has latency data from multiple layers — relevant columns vary per table version, but key fields commonly include:
- **ExternalTimeMs** — end-to-end client perspective
- **ServerTimeMs** — total server processing
- **FETimeMs** — Front End layer
- **TableServerTimeMs** — Table Server layer
- **StreamTimeMs** — Stream layer (persistence)
- **AuthTimeMs** — auth handshake
- **CacheTimeMs** — read cache layer

Compare layer-wise to isolate hot layer:
- Hot FE → load balancing / FE capacity
- Hot TableServer → partition contention / hot partition (cross-link § SA-Perf-PartitionDowntime)
- Hot Stream → backend storage stamp / disk
- Hot Auth → AAD / token validation
- Hot Cache → cache miss

### Server Request Id for AutoAnalysis
XArgus stores the **Server Request Id of the highest-latency request for every latency field**. Use to:
- Co-locate raw FE/TS logs for that specific request
- Skip needing to scan logs for outliers (XArgus already identified them)
- Plug into AutoAnalysis tools directly

### XArgus Portal (no SAW required for view)
1. https://aka.ms/xportal → search SA → Refresh
2. Click tenant name → XArgus Portal opens
3. Detail metric charts on XStore-side

---

## SA-Perf-TenantHealth — Storage Tenant (stamp) level health check + XArgus tenant percentiles + XPortal tenant dashboard

### Symptom
- Multiple SAs in same region show latency / availability drop at the same time
- Customer SA latency spikes correlate with platform issues — need to isolate "is this our stamp" vs "is this just this account"
- Need stamp-wide perf baseline

### Get stamp/tenant info

#### Method 1 — DNS / nslookup
```bash
nslookup <storage_account_name>.blob.core.windows.net
```
Endpoint pattern: `https://<sa>.<service>.core.windows.net/` — DNS resolution reveals the underlying stamp.

#### Method 2 — XPortal
1. https://aka.ms/xportal → enter SA → Refresh
2. Click tenant name (e.g., `MS-xxxx-stmp`)
3. View: tenant health model + tenant transactions + tenant CPU + traffic + latency metrics

### ⚠ Always FIRST step
Check https://aka.ms/Iridias for active Storage outage in customer's region. If active LSI matches — DO NOT investigate further as a unique case; piggyback the LSI ICM.

### Tenant Health Model Dashboard (XPortal)
High-level diagnosis signals for the stamp:
- Hardware Failures
- Alerts
- Available Memory
- CPU / Memory Throttling
- Node Latency

**Two key charts to check FIRST**:
- **Low Total Availability Account Count** — # of accounts on the stamp currently impacted (availability dropping)
- **High PutPage Latency Account Count** — # of accounts on the stamp currently seeing elevated PutPage latency

If significant blip + stays elevated:
1. Search ICM database — XArgus may have already fired
2. Get help from XStore engineering to identify if related to a tenant-level outage

**Caveat**: These metrics show **SYMPTOMS, not causes**. You must dig into logs from the underlying components (FE / TS / Stream) to identify which component team to engage.

### KQL — Tenant latency percentiles
```kusto
cluster('xargus.centralus.kusto.windows.net').database('Production').TenantPerfPercentiles5M
| where TimeWindow >= ago(1h)
| where EntityType == "PageBlob"
| where Operation == "PutBlock"
| where Tenant == "{Tenant}"
| project TimeWindow, Tenant, EntityType, Operation, RequestCount, RequestSizeKB_Avg,
          ServerTimeMs_P50_0, ServerTimeMs_P90_0, ServerTimeMs_P99_0, ServerTimeMs_P99_9
| take 10
```

Same EntityType / Operation filter parameters as § SA-Perf-XArgus-Account.

### Architecture references
- Public: [Azure Storage architecture design](https://learn.microsoft.com/en-us/azure/architecture/guide/storage/storage-start-here)
- Internal: [Azure-Storage-Architecture wiki](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/1368980/Azure-Storage-Architecture_Storage)
- XStore Training - Livesite Fundamentals (SharePoint, internal video)

---

## SA-Perf-PartitionDowntime — Jarvis MDM/Geneva `Xstore.PartitionDowntimeEvent` + load balancing / split events

### Symptom
- SA Server Latency time-breakdown shows long `TotalTableServerTimeInMs`
- MDM Storage Account API Errors logs show `ServerTimeoutError`
- Need to confirm: was Table Server doing a load-balance / partition split during the issue window?

### Required inputs
- **Tenant** (stamp name like `MS-xxxx-stmp`)
- **Time range** (issue window)
- **LastTSPartition** (partition identifier — typically obtained from MDM Storage Account API Errors row)

### Jarvis query

1. Jarvis https://jarvis-west.dc.ad.msft.net/ → Logs section
2. Example query link: https://jarvis-west.dc.ad.msft.net/759055F3
3. Parameters:

```
Namespace:   Xstore
Events:      PartitionDowntimeEvent
Tenant:      <StorageCluster>
Time range:  <issue window>
Filtering:   AnyField contains <LastTSPartition>
```

### Output fields to look at
- **LBType** — type of load-balance op (e.g., `Split`, `Merge`, `Move`)
- **Reason** — what triggered the LB op

### Interpretation
- `LBType=Split` during issue window → partition was being split → temporary unavailability for that partition's blobs/entities is expected; transient
- Frequent splits on same partition → hot partition / workload-pattern issue → customer should diversify keys / use sharding
- No LB events but ServerTimeoutError persists → escalate to **XStore PG** (Partition team) via ICM

---

## SA-Perf-PageBlob — Azure Page Blob deep dive + XBlobFE GetPage/PutPage + scalability targets + MDM FrontEnd logs

### Scope
Page Blob perf issues. Customer reports: high latency on disk-backed VHDs OR generic Page Blob storage; throttling; throughput/IOPS not as expected.

### Distinguish DiskPageBlob vs PageBlob
- **DiskPageBlob** (XPortal Shoebox ObjectType) = Page Blob backing an unmanaged disk (Classic VM disk)
- **PageBlob** (XPortal Shoebox ObjectType) = generic Page Blob (customer-uploaded VHD-like blob)

Both filter via XBlobFE in Shoebox; ObjectType field distinguishes.

### Investigation tools (same 3 as § SA-Perf-CheckActivity but with PageBlob filter)

#### XPortal Shoebox API Investigation
1. https://xportal.trafficmanager.net/sla/mdm/account/$/dashboards
2. Enter SA → Refresh
3. Open **Shoebox API Investigation Dashboard**
4. Time range
5. ObjectType filter: `DiskPageBlob` or `PageBlob`
6. API filter: e.g., `GetPage`, `PutPage`

#### ASC Performance tab
ASC → Resource Explorer → SA → Performance tab → Filter Timeframe + **Blob** service

#### xDash (Legacy)
aka.ms/xdash → Account | Account SLA → SA → time range

### Key XBlobFE APIs for Page Blob
- **XBlobFe All / Blob Service** — aggregate
- **XBlobFe GetPage** — Read ops (Page + Block blobs)
- **XBlobFe PutPage** — Write Page Blob ops

### Metrics
1. **Perceived Availability(%) / Customer Perceived Availability(%)** — drop = throttling
2. **Availability(%)** — drop = server-side / platform
3. **Throttling Errors(%)** + Bandwidth / IOPS / Server Throttling (amount)
4. **Transactions/Sec / Blob IOPS**
5. **Ingress(Mbps) / Egress(Mbps)** — throughput
6. **Client Latency (ms) + Server Latency (ms)**

### Analysis decision tree

#### Throttling
1. Check vs [Scalability targets for Azure Blobs](https://docs.microsoft.com/en-us/azure/storage/common/storage-scalability-targets#azure-blob-storage-scale-targets)
2. xDash limit: it doesn't separate Page vs Block in one SA (mixed granularity)
3. If scalability target reached:
   - **Confirmed**: customer must reduce per-blob TX, leverage multiple blobs, OR migrate to [Premium Page Blobs (Disks)](https://docs.microsoft.com/en-us/azure/virtual-machines/windows/premium-storage)
   - **Not confirmed**: drill into MDM Storage Account API Errors → Blob/s throttled / RequestUrl / Status+InternalStatus / ClientIP / UserAgent

#### Server issues — Availability lost
1. Check https://aka.ms/iridias for active Storage LSI in customer region
2. MDM Storage Account API Errors → check time spent across layers: `TimeInMs`, `TotalFeTimeInMs`, `TotalTableServerTimeInMs`, etc.
3. If `ServerTimeoutError` → drill into § [SA-Perf-PartitionDowntime](#sa-perf-partitiondowntime--jarvis-mdmgeneva-xstorepartitiondowntimeevent--load-balancing-split-events)
4. Server-side confirmed → engage XStore PG via ICM

#### High Latency
Apply the latency-interpretation rule of thumb (top of file):
- **Higher Client than Server** → not Storage → Guest-OS via [IaaS VM Perf workflow](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495947) (cross-link Playbook G)
- **Higher or equal Server** → Iridias check + MDM logs time-spent per layer; escalate if confirmed server-side

### MDM Storage Account API Errors
Sourced via template `/.templates/SME-Topics/Storage-Performance/Azure-Storage-Front-End-Logs-Blob.md`. Note: only ERROR ops are logged (no successful ones).

Key fields to project:
- `TimeInMs` (total)
- `TotalFeTimeInMs` (FE layer)
- `TotalTableServerTimeInMs` (TS layer)
- `Operation` (e.g., GetPage / PutPage)
- `RequestUrl` (resource targeted)
- `Status` + `InternalStatus` (cause / internal error code)
- `ClientIP` + `UserAgent` (caller)

### Cross-link
For per-disk-level IOPS / MBps cap RCA on managed disks → **Playbook F § Disk-Perf** (different layer: per-disk SKU cap, not SA-level XBlobFE).

---

## SAF-Win-Explorer-Slow — Cross-link stub: Azure Files SMB Windows Explorer slow file open/save/close → registry workaround

### Scope note
This is one of the K wiki TSGs (`Slow Perf for File Open Save and Close_Storage`) but the actual fix is a **Windows guest-OS workaround for Azure Files SMB**, not a Storage-side fix. Lives in **Playbook L** (Azure Files); kept here as a navigation stub.

### Symptom
Customer sees slow performance when opening / saving / closing files hosted in Azure File Share (SMB). Windows Explorer file transfer slow.

### Cause
Windows Explorer performs folder traversal before user-intended op. Reference: [Bypass Traverse Checking / Change Notify Privilege](https://blogs.technet.microsoft.com/markrussinovich/2005/10/19/the-bypass-traverse-checking-or-is-it-the-change-notify-privilege/).

### Resolution (apply on Windows VM/Machine where the app runs; reboot)
```reg
Windows Registry Editor Version 5.00
[HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\policies\Explorer]
"UseDesktopIniCache"=dword:00000000
"NoRemoteRecursiveEvents"=dword:00000001
"NoRemoteChangeNotify"=dword:00000001
"NoRecentDocsNetHood"=dword:00000001
"NoDetailsThumbnailOnNetwork"=dword:00000001
[HKEY_LOCAL_MACHINE\System\CurrentControlSet\Services\MRXSmb\Parameters]
"InfoCacheLevel"=dword:00000010
[HKEY_CLASSES_ROOT\*\shellex\PropertySheetHandlers\CryptoSignMenu]
"SuppressionPolicy"=dword:00100000
[HKEY_CLASSES_ROOT\*\shellex\PropertySheetHandlers\{3EA48300-8CF6-101B-84FB-666CCB9BCD32}]
"SuppressionPolicy"=dword:00100000
[HKEY_CLASSES_ROOT\*\shellex\PropertySheetHandlers\{883373C3-BF89-11D1-BE35-080036B11A03}]
"SuppressionPolicy"=dword:00100000
[HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\explorer\SCAPI]
"Flags"=dword:00100c02
[HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager]
"SafeDllSearchMode"=dword:00000001
"SafeProcessSearchMode"=dword:00000001
```

### Case coding
`Routing Windows V3\Windows Desktop, User Logon, and User Profiles\Windows Explorer performance or slowness`

### Cross-link
Full Azure Files perf coverage → **Playbook L** (TBD).

---

## LinuxOSDisk-Full — Cross-link stub: Linux OS disk full → du locate + rotate + cleanup

### Scope note
This is one of the K wiki TSGs (`Correcting Full OS Disk Without Resize_Storage`) but it's a **generic Linux guest-OS disk-cleanup TSG**, not a Storage perf issue. Kept here as a navigation stub.

### Symptom
Linux VM OS disk full → typical errors:
- `touch new` → `cannot touch "new": No space left on device`
- waagent: `ERROR:IOError: [Errno 28] No space left on device: '/var/lib/waagent/events/...tmp'`
- cloud-init: `OSError: [Errno 28] No space left on device: '/var/lib/cloud/data/tmp...'`

### Diagnostic + cleanup
```bash
df -h                            # find 100% partition
cd /
sudo du -hs * 2>/dev/null        # find offender directory (e.g., /var = 28G)
cd /var
sudo du -hs *                    # recurse into offender
# delete or rotate; rinse and repeat
```

### Common offenders
- `/var/log` (no log rotation) — fix: logrotate config
- `/var/lib/waagent/events` — clear old events
- `/var/cache/apt` — `apt-get clean`
- App logs without rotation
- Docker dangling layers — `docker system prune`

### Cross-link
- For OS disk resize → **Playbook F § OS-Disk-Resize**
- For full Linux guest-OS disk corruption / fsck recovery → **Playbook G** (GuestOS)

---

## SA-Perf-AzureFiles-Backend — Azure Files share backend perf investigation + XFileFE Read/Write + per-share 1000 IOPS / 60 MB/s limits + Cross-Zone Traffic detection + MDM `Xstore.FrontEndSummaryPerfLogs / XNfsPerfMetric / XSMBPerfMetric`

### Scope
**XStore backend perf investigation** for an Azure Files SA. Sibling to § SA-Perf-PageBlob (same Shoebox / ASC / MDM tooling pattern, but XFileFE instead of XBlobFE).

For **client-side / SMB / NFS / Guest-OS** investigation → **Playbook L** (TBD).

### Investigation tools (XPortal / ASC / xDash with File filter)

#### XPortal Shoebox API Investigation
1. https://xportal.trafficmanager.net/sla/mdm/account/$/dashboards
2. Enter SA → Refresh
3. Open **Shoebox API Investigation Dashboard**
4. Filter ObjectType = `File`
5. API + Authentication filters

#### ASC Performance tab
ASC → Resource Explorer → SA → Performance → Filter Timeframe + **File** service

### Key XFileFE APIs for Azure Files
- **XFileFE All / File** — aggregate
- **XFileFE Write** — write activities
- **XFileFE Read** — read activities

### Metrics (same matrix as PageBlob but with per-share targets)
1. **Perceived Availability(%) / Customer Perceived Availability(%)** — drop = throttling (client-side)
2. **Availability(%)** — drop = server-side / platform
3. **Throttling Errors(%)** + Bandwidth / IOPS / Server Throttling (amount)
4. **Transactions/Sec / File IOPS** — vs **1,000 IOPS** per File Share
5. **Ingress(Mbps) / Egress(Mbps)** — vs **60 MB/s (480 Mbps)** per share throughput
6. **Client Latency (ms) + Server Latency (ms) / File Server Latency**

### ⚠ Per-share aggregation caveat
**All XPortal / ASC counters show aggregate metrics for ALL Azure File Shares in the SA.** No per-share granularity in current tooling. Analyzing multi-share SAs is more complex; MDM logs (below) provide the only per-share drill-down.

### Analysis decision tree

#### Throttling
1. Check vs [Scalability Targets for Azure Files](https://docs.microsoft.com/en-us/azure/storage/common/storage-scalability-targets#azure-files-scale-targets)
2. **Confirmed**: customer must reduce per-share TX OR leverage multiple shares
3. **Not confirmed**: drill MDM Storage Account API Errors (below) for Share/RequestUrl/Status/InternalStatus/ClientIP/UserAgent
4. **No CSS tooling besides MDM** provides per-share granularity → may need Guest OS investigation (Playbook L)
5. **Scalability NOT reached** → could be server-side → Advanced TS workflow

#### Server-side (Availability drop)
1. Iridias check for active Storage LSI
2. MDM Storage Account API Errors → time-spent across layers (TimeInMs / TotalFeTimeInMs / TotalTableServerTimeInMs)
3. `ServerTimeoutError` → drill § SA-Perf-PartitionDowntime
4. Confirmed server-side → escalate XStore PG via ICM

#### High Latency — special Cross-Zone Traffic detection (NEW vs PageBlob)
- **Higher Client Latency than Server**: standard guidance = client-side / Guest-OS resource contention or network
- **⚠ NEW signal**: end-to-end vs Server Latency diff **>10ms** may indicate **cross-zone traffic** between VM and Files share

##### Zonal Placement preview signup (cross-zone fix)
Recommend customer fill [Zonal Placement signup form](https://forms.office.com/Pages/ResponsePage.aspx?id=v4j5cvGGr0GRqy180BHbR3YF4IzZBh5DsKmgV8Q2xEFUN1FMVVBTWkFPWk5TSDhIWTFJSzFDSzNTSyQlQCN0PWcu) to:
1. Pin existing SA to a specific Availability Zone (after becoming aware of current Zone)
2. Align VM deployments to the same Zone

**⚠ Eligibility (BOTH conditions required)**:
1. Customer uses **Premium LRS** Storage Account
2. Account is in one of these supported regions: `useast, useast2, uscentral, ussouth, uswest3, canadacentral, germanywc, japanwest, qatarc, indonesiac, italyn, israelc, newzealandn, mexicoc, polandc, spainc, malaysiaw, chilec`

Do **NOT** recommend the form unless BOTH conditions met.

### MDM Jarvis Geneva query for XFileFE
Example: https://portal.microsoftgeneva.com/s/CCDBA70C
```
Namespace:   Xstore
Events:      FrontEndSummaryPerfLogs, XNfsPerfMetric, XSMBPerfMetric
Tenant:      <StorageCluster>
Time range:  <issue window>
Filtering:   Account contains <StorageAccountName>
```

Note 3 event names — split by protocol:
- `FrontEndSummaryPerfLogs` — front-end summary (all protocols)
- `XSMBPerfMetric` — SMB protocol per-op detail
- `XNfsPerfMetric` — NFS protocol per-op detail

#### Fields to project
Operation (Read/Write/Other), RequestUrl, HttpStatusCode, Status (e.g., OperationTimedOut, ServerBusy), InternalStatus (e.g., ClientTimeoutError, ClientPartitionRequestThrottlingError), UserAgent, ClientIP, TimeInMs / TotalFeTimeInMs / TotalTableServerTimeInMs.

### Cross-link
- Metadata-specific throttling → § SA-Perf-AzureFiles-HeavyMetadata
- Premium SMB Metadata Caching feature enablement → § SA-Perf-AzureFiles-MetadataCaching
- Foundation workflow + Guest OS prep → § SAF-AzureFiles-PerfWorkflow → **Playbook L** for deep Guest-OS investigation

---

## SA-Perf-AzureFiles-HeavyMetadata — Azure Files Heavy Metadata throttling — `SuccessWithMetadataWarning` / `SuccessWithMetadataThrottling` RCA via `XStoreXFileThrottleTransaction` + metadata IOPS tier table

### Symptom
Customer reports latency-only Azure Files perf issue (no failures) with workload heavy in metadata ops: `createfile`, `openfile`, `closefile`, `queryinfo`, `querydirectory`.

Typical workload patterns: web/app services, DevOps tasks, indexing/batch jobs, virtual desktops with home directories, "many small files" applications.

### Metadata IOPS limits per share tier (2025)

| Share type | Approx Metadata IOPS limit |
|---|---|
| Standard HDD Pay-as-you-Go | up to **12,000** |
| Premium HDD Provisioned V1 | up to **12,000** |
| **Premium w/ Metadata Caching — SSD Provisioned V1** | up to **35,000** |

Public source: [Azure File Share Scalability targets](https://learn.microsoft.com/en-us/azure/storage/files/storage-files-scale-targets#azure-file-share-scale-targets).

### New ResponseTypes (~November 2024)
- **`SuccessWithMetadataWarning`** — metadata IOPS approaching limit; throttling risk rising. Op succeeds.
- **`SuccessWithMetadataThrottling`** — metadata IOPS exceeded share capacity → THROTTLED. Op never fails (retried), but latency impacted.

Customer-side: setup Azure Monitor → Transactions metric → **Apply splitting** on Response Type → metadata response types appear in dropdown if activity occurred in the timeframe.

### Step 1 — Confirm heavy-metadata workload (XPortal)
1. Open [XPortal Shoebox API Investigation Dashboard](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/496479/XPortal_Tool?anchor=shoebox-api-investigation-dashboard(mdm)---**recommended**)
2. Adjust **Timeframe**; set **ObjectType = File**
3. Review **Sum of Errors** widget:
   - `SuccessWithMetadataThrottling` present → **CONFIRMED throttled**
   - Only `SuccessWithMetadataWarning` → high IOPS but not yet throttled
   - Note: `ClientOtherErrors` are mostly harmless / expected from client side
4. Check **Total Transactions** (hover for operation types — confirm they're metadata-related)
5. Check **Server Latency** Average + Q99.9 (reference only: Standard ~2-digit ms, Premium ~1-digit ms — NO SLA)
6. Check **Transactions Per Second** metadata op count

If clear heavy-metadata throttling → Step 2. Otherwise check [non-metadata Storage Backend Performance](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495816) OR Step 3 (advanced).

### Step 2 — Improvement paths (per share tier)

#### Standard share (ordered for better perf)
1. **Migrate** to [Premium SSD tier](https://learn.microsoft.com/en-us/azure/storage/files/understanding-billing#provisioned-v1-model) → enable [Metadata Caching](https://learn.microsoft.com/en-us/azure/storage/files/smb-performance?tabs=portal#metadata-caching-for-premium-smb-file-shares) (see § SA-Perf-AzureFiles-MetadataCaching)
2. [Add and Mount a VHD on the File Share](https://learn.microsoft.com/en-us/troubleshoot/azure/azure-storage/files/performance/files-troubleshoot-performance?tabs=windows#workarounds) — may not be applicable to all customers
3. Modify app to reduce metadata ops
4. Separate into multiple File Shares in same SA
5. Step 3 advanced investigation

#### Premium share (ordered for better perf)
1. **Enable Metadata Caching** (if not enabled — § SA-Perf-AzureFiles-MetadataCaching)
2. Add+Mount VHD workaround
3. Modify app
4. Separate into multiple shares
5. Step 3 advanced investigation

### Step 3 — Advanced Investigation KQL
Cluster: `azcore.centralus.kusto.windows.net` → `Xstore` → `XStoreXFileThrottleTransaction` joined to `xstore.xstore.StorageAccountCapTX`.

```kusto
set maxmemoryconsumptionperiterator=68719476736;
set notruncation;
let startDate = datetime({StartDate});
let endDate = datetime({EndDate});
let storageAccounts = (
    cluster("xstore").database("xstore").StorageAccountCapTX
    | where AccountName has "{StorageAccountName}"
    | project
        timestamp = Timestamp,
        clusterName = Tenant,
        subscriptionId = SubscriptionId,
        Account = AccountName,
        storageAccountCreateDate = AccountCreationTime,
        fileShareCount = FileContainerCount,
        provisionedSizeTiB = XFileProvisionedBytes / pow(1024, 4),
        state = State,
        kindCode = AccountTypeInAccountRow,
        billingType = BillingType,
        usageType = UsageType,
        TPName,
        Tenant
    | where timestamp between (startDate..endDate)
    | project-away state, kindCode, billingType
);
cluster("azcore.centralus.kusto.windows.net").database("Xstore").XStoreXFileThrottleTransaction
| where TIMESTAMP between (startDate..endDate)
| extend storageAccountInfoArr = split(Account, ";")
| extend Account = tostring(storageAccountInfoArr[0])
| join hint.strategy=shuffle kind=inner (storageAccounts) on Account
| summarize provisionedSizeTiB = avg(provisionedSizeTiB),
            sum(SuccessWithMetadataWarning),
            avg(MinFileMetadataIopsWithWarning),
            sum(SuccessWithMetadataThrottling),
            avg(MinFileMetadataIopsWithThrottling),
            sum(SuccessWithServerBusy)
            by Account, TPName, usageType, Tenant
```

#### Result interpretation
| Field | Meaning |
|---|---|
| `sum_SuccessWithMetadataWarning` | # ops triggering warning |
| `avg_MinFileMetadataIopsWithWarning` | Avg IOPS rate when warning triggered |
| `sum_SuccessWithMetadataThrottling` | # ops actually throttled |
| `avg_MinFileMetadataIopsWithThrottling` | Avg IOPS rate when throttled |
| `sum_SuccessWithServerBusy` | # generic server-busy responses |

Decision:
- `sum_SuccessWithMetadataThrottling > 0` → CONFIRMED throttled by Files metadata
- `=0` → NOT throttled by metadata
- `Warning > 0 AND Throttling = 0` → heavy metadata workload but not yet throttled

#### DGrep + Verbose log correlation
- [FrontEnd Logs DGrep](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/690089/Query-Storage-FrontEnd-Logs_Storage?anchor=dgrep-/-jarvis) — filter by `RequestUri` or `Container` for specific share; aggregate by `RequestUri / Client / SmbCommand / Status / Operation`; extract `ActivityId` of relevant ops
- [Verbose logs](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/690091) by `ActivityId` for failing/relevant ops

### Step 4 — Escalation
Required: customer scenario (app + workload), Timeframe UTC, prior step results.

### Cross-link
- § SA-Perf-AzureFiles-Backend (foundation)
- § SA-Perf-AzureFiles-MetadataCaching (Premium feature enablement — primary fix)
- § SA-Perf-PartitionDowntime (if Server-side TS issues found)

---

## SA-Perf-AzureFiles-MetadataCaching — Premium SMB Files Metadata Caching (Runtime State Preview) — primary fix path for heavy-metadata throttling (AFEC feature registration + region list + no backend verification + PM contacts)

### Feature: Runtime State / Metadata Cache for Premium SMB Files
**UNLIMITED PUBLIC PREVIEW**. In-memory cache for the Files Service runtime state with persistence on xCache. Caches metadata for `Create / Open / Close / Delete`, plus handle/lease state, plus portions of the namespace.

Engineering result: less FileTable iteration per open/close; less table server page cache pressure; less GC pressure; more consistent latency at scale + during peak cluster usage.

[Blog post](https://techcommunity.microsoft.com/t5/azure-storage-blog/accelerate-metadata-heavy-workloads-with-metadata-caching/ba-p/4261442)

### Performance improvements (publicly claimed)
- **≥ 30%** reduction in metadata latency
- **≥ 60%** increase in available IOPS
- **≥ 60%** increase in network throughput

All measured on metadata-heavy workloads at scale.

### Eligibility
- **Account kind**: `FileStorage` (Premium SMB file shares ONLY)
- **No additional cost**
- **Both Windows AND Linux** SMB clients benefit
- NFS protocol NOT yet supported (PG working on parallel progress)

### How to register
[Microsoft Learn: Register for the feature](https://learn.microsoft.com/en-us/azure/storage/files/smb-performance?tabs=portal#register-for-the-feature) — uses AFEC feature registration. Customer can opt in **directly from Azure Portal**.

### Onboarding behavior
- Once SA's sub onboarded → **all NEW SAs auto-benefit**
- For EXISTING SAs in same sub → must be enabled separately (PM-assisted for now)
- Cache hydration: typically **~1 hour** after File Shares move to Azure (INTERNAL info — do NOT share with customer)
- If data infrequently accessed → cache clears → needs rehydration

### Region availability (~24 regions, list grows)
Asia East, Australia Central, Brazil South, Canada Central, France Central, Germany West Central, Japan East, Japan West, Jio India West, India Central, India South, Korea Central, Mexico Central, Norway East, Poland Central, Qatar Central, Spain Central, Sweden Central, Switzerland North, UAE North, UK West, US South Central, US West Central, US West 3

Authoritative list: [public docs](https://learn.microsoft.com/en-us/azure/storage/files/smb-performance#regional-availability).

> As new regions are added, premium file storage accounts in those regions are auto-onboarded for all subscriptions registered for the feature.

### ⚠ Backend verification limitation
**Currently NO way to verify cache usage** in the backend for a customer's workload. Dashboards coming in near future.

If account looks healthy + customer enabled feature + waited (e.g., > 1 week) + no perf benefit:
→ Escalate via ICM with subscription IDs + company name.

### PM escalation contacts
For (a) existing-SA enablement assistance, (b) registration not effective after 1 week, (c) feature questions:
- Yakshit Gohel <yagohel@microsoft.com>
- Drew Bailey <abail@microsoft.com>
- Matias Ezequiel Rimoldi <marimo@microsoft.com>
- Adam Groves <agroves@microsoft.com>
- CC: `metadatacss@microsoft.com`

### Verification approach (workaround for no-backend-check)
Customer compares perf of metadata-caching-enabled SA vs non-enabled SA on identical workload. If enabled SA significantly better on `Create / Open / Close / Delete` → feature working.

### Cross-link
- § SA-Perf-AzureFiles-HeavyMetadata (primary parent — feature is the fix for heavy-metadata throttling)
- § SA-Perf-AzureFiles-Backend (foundation backend perf TSG)

---

## SAF-AzureFiles-PerfWorkflow — Cross-link stub: Azure Files Performance Workflow master entry-point (scoping questions + internal data collection + PerfInsights `azurefiles` scenario + LabBox + Guest OS funnels to L)

### Scope note
Master entry-point workflow for Azure Files perf cases. Mixed K/L — most deep Guest-OS investigation goes to L. K captures the scoping + foundational data-collection portion (referenced from § SA-Perf-AzureFiles-Backend + § SA-Perf-AzureFiles-HeavyMetadata as a prerequisite).

### Scoping questions (case-opening triage)

#### 1. WHEN does it happen?
- New deployment?
- When was the last "good" perf?
- What was the last change?
- Intermittent or constant?

#### 2. WHERE?
- Azure VM / on-prem / both?
- Windows / Linux / both?
- Other VMs on same Azure?
- Other SAs in same region (cross-SA pattern)?

#### 3. WHAT exactly?
- Customer definition of "bad" vs "good" perf — manage expectations (Azure Files won't match 2 on-prem 10 GigE servers)
- Specific error messages + where seen?

### Required customer-provided data
1. Issue description
2. SubscriptionId
3. SA Name
4. Azure File Share Name
5. Timeframe (UTC)
6. Frequency
7. VM Name
8. Error message

### Internal data collection
Azure Files NOT shown in ASC — retrieve internally:
1. Type of SA (Standard_LRS / etc.)
2. Kind (Storage / Storagev2 / FileStorage)
3. Location
4. Storage Cluster (tenant)
5. File Endpoint
6. SA Analytic settings for Files
7. Capacity

### Reference limits (Standard tier)
- 1,000 IOPS per share
- 60 MB/s throughput per share
- 2,000 open handles per share
- Public: [Scalability targets for blobs/queues/tables/files](https://docs.microsoft.com/en-us/azure/storage/common/storage-scalability-targets#scalability-targets-for-blobs-queues-tables-and-files)

### PerfInsights for Azure Files (Windows VM)
```
PerfInsights.exe /r azurefiles /sr 997121217306799
```
- Y to agree (diagnostic info + EULA)
- Reproduce the issue
- Press any key to stop
- Output: `CollectedData_YYYY-MM-DD_HH-MM-FFF.zip` in current folder
- **Note**: more granular Azure File Share metrics in PerfInsights v3.3.9+
- **Linux**: PerfInsights for Azure Files is in development

### LabBox training scenarios (NOT for customers)
- **Scenario 1 — Throttling**: https://aka.ms/LabBox `FileSharePerformanceIOPSThrottling.json`
- **Scenario 2 — Heavy Metadata**: https://aka.ms/LabBox `FileSharePerformanceHeavyMetadata.json`

Each: deploy template → wait 10 minutes → ready to troubleshoot.

### Best-practice reminders (cross-link)
- 1 MB I/O size for optimal perf (if no specific minimum requirement)
- Set file size in advance if known (avoid extending writes if app supports)
- Windows: use AzCopy for Windows (between shares) OR Robocopy with /MT (between on-prem ↔ share)
- Win8.1 / WS2012 R2: install KB3114025 (improves Create/Close handle perf)
- Linux: use AzCopy for Linux (not RSync — no parallel IO)

### Funnel
1. **Scoping + data collection** (this section)
2. **Backend investigation** → § SA-Perf-AzureFiles-Backend
3. **Metadata-specific deep dive** → § SA-Perf-AzureFiles-HeavyMetadata
4. **Guest OS investigation / Advanced TS** → **Playbook L** (TBD: netsh trace `filesharing` scenario / Linux tcpdump / mount.cifs -V / /proc/fs/cifs/DebugData / Windows Networking T2 / Linux SME)
