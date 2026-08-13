# Playbook K — Storage Performance / Throttling — Core

> **Companion to** [`playbook-K-storage-perf-deep.md`](./playbook-K-storage-perf-deep.md). INLINE style (small + high-value RCAs warrant verbatim bodies in deep file).
>
> Cross-link target for [`references/storage-account-queries.md`](../catalogs/storage-account-queries.md) (XArgus AccountPerfPercentiles5M + TenantPerfPercentiles5M already there).
>
> Use as **routing entry point** when a case is about storage performance — latency / throttling / availability drops / tenant-stamp-level perf — for any SA service (Blob / Page Blob / Table / Queue). NOT Azure Files (→ L); NOT SA control-plane (→ J); NOT managed disk perf (→ F).

## When to use this playbook

| Use Playbook K when... | Don't — use instead |
|---|---|
| Customer reports slow Storage Account / Blob latency | Azure Files SMB/NFS perf  → L |
| 429 / ServerBusy / `Operations per second is over the account limit` / `The server is busy` | Tactical 429 retry guidance (basics) → Playbook C § THR-Perf-3/4 |
| Drop in SA Availability(%) → need to verify Storage LSI / tenant stamp health | Active LSI suspected → Iridias first |
| Drop in SA Perceived Availability(%) → throttling RCA | SA CMK / management 503/InternalServerError  → J |
| Need to investigate XStore-side latency (FE / TableServer / Stream) | Managed disk-level latency (disk IO blip) → Playbook F § Disk-Perf |
| Need stamp-level (tenant-level) health check across many accounts on the same stamp | Single SA control-plane op failed → J § SA-Mgmt-* |
| Page Blob throttling / scalability target hit | Premium disk perf → Playbook F |

## Inputs to collect

| # | Item | Why |
|---|---|---|
| 1 | `SubscriptionId` + `StorageAccountName` | Primary filters |
| 2 | Tenant/Stamp name (e.g., `MS-xxxx-stmp`) | XArgus tenant-level + Jarvis PartitionDowntimeEvent |
| 3 | Issue StartTime / EndTime (UTC) | Pad ±15 min for XArgus 5M aggregation |
| 4 | Affected EntityType + Operation (e.g., `BlockBlob`/`PutBlock`, `PageBlob`/`GetPage`) | XArgus filter |
| 5 | Customer-perceived symptom (latency / throttling / availability drop / timeout) | Routes to symptom anchor |
| 6 | If 429: account API + RequestUrl + Client IP + UserAgent | Identify caller / app holding throttle |
| 7 | If availability drop: ASC / XPortal Shoebox screenshot | Confirm server vs perceived availability |
| 8 | If ARM-side: CorrelationId | ARMProd.Storage.StorageOperations correlation |

## Step-by-step

### Step 1 — Identify symptom domain

| Symptom | Goes to... |
|---|---|
| ARM call to internal storage fails 503 (`Operations per second is over account limit` OR `The server is busy`) | Step 2 (ARM-side XStore throttling) |
| Customer hits SA-level 429 / IOPS / Ingress / Egress limit | Step 3 (SA scalability / throttling) |
| Customer reports Blob / Page Blob latency spike (high P99/P99.9) | Step 4 (Account-level XArgus latency) |
| Drop in SA Availability(%) (server-side) — multiple accounts in same region/stamp | Step 5 (Tenant / stamp health) |
| Drop in SA Perceived Availability(%) (client-side / throttling) | Step 3 (SA throttling) |
| Page Blob throttling (specific to PageBlob entity type) | Step 6 (Page Blob deep dive) |
| **Azure Files share** — backend XStore perf investigation (XFileFE / metadata throttling / cross-zone traffic / Metadata Caching feature) | **Step 7 (Azure Files backend)** — K owns backend; client-side / Guest-OS / SMB/NFS deep  → L |
| Higher Client Latency than Server Latency | → Guest-OS perf workflow ([IaaS VM Perf](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495947)) — NOT a K deep |
| Azure Files SMB file open/save/close slow | → **Playbook L** (cross-link only — § SAF-Win-Explorer-Slow in K deep is a stub pointer) |
| Azure Files client-side / Guest-OS deep TS (netsh trace / tcpdump / mount.cifs -V) | → **Playbook L** (cross-link only — § SAF-AzureFiles-PerfWorkflow in K deep is the K-side scoping stub) |

### Step 2 — ARM-side XStore throttling routing

| Symptom | Anchor |
|---|---|
| ARM operation failed with 503 + StatusMessage `Operations per second is over the account limit` OR `The server is busy` (ARM internal storage access) | § [SA-Perf-ARM-XStore-Throttle](./playbook-K-storage-perf-deep.md#sa-perf-arm-xstore-throttle--arm-503-on-internal-xstore-call-operations-per-second-over-account-limit-or-server-is-busy) (ARMProd.Storage.StorageOperations KQL with macro-expand + StatusMessage signatures + customer-RCA template + ⚠ open collab with **CSS ARM team FIRST** before opening ICM) |

### Step 3 — SA scalability + throttling routing

| Symptom | Anchor |
|---|---|
| Customer needs to understand SA usage / activity (verify spike, baseline) | § [SA-Perf-CheckActivity](./playbook-K-storage-perf-deep.md#sa-perf-checkactivity--check-storage-account-activity-via-asc--xportal--azure-monitor--diagnostic-logs) (4 tools: ASC + XPortal + Azure Monitor + Diagnostic Logs) |
| 429 / Throttling Errors / Bandwidth Throttling / IOPS Throttling visible on SA dashboard | § [SA-Perf-SAThrottle](./playbook-K-storage-perf-deep.md#sa-perf-sathrottle--sa-level-throttling-iops-ingress-egress-scalability-target-hit) (XPortal Shoebox + ASC Perf tab + scalability targets table + MDM Storage Account API Errors deep dive) |
| Customer asks "what is the throttling timeout / how should client retry" | § [SA-Perf-SAThrottle](./playbook-K-storage-perf-deep.md#sa-perf-sathrottle--sa-level-throttling-iops-ingress-egress-scalability-target-hit) → links out to [Storage Service Throttling Timeouts (Dev_Storage 1833046)](https://supportability.visualstudio.com/AzureDev/_wiki/wikis/Dev_Storage/1833046/Storage-Service-Throttling-Timeouts) + retry guidance |

### Step 4 — Account-level XArgus latency routing

| Symptom | Anchor |
|---|---|
| Customer reports high P99 / P99.9 latency on Blob / PageBlob / Table operation | § [SA-Perf-XArgus-Account](./playbook-K-storage-perf-deep.md#sa-perf-xargus-account--account-level-latency-percentiles-via-xargus-p50p90p99p999--auth-fe-tableserver-stream-breakdown) (AccountPerfPercentiles5M KQL + XArgus access prereq + tooling) |
| Need to understand which layer is causing latency (Client vs Server, FE vs TableServer vs Stream) | § [SA-Perf-XArgus-Account](./playbook-K-storage-perf-deep.md#sa-perf-xargus-account--account-level-latency-percentiles-via-xargus-p50p90p99p999--auth-fe-tableserver-stream-breakdown) (layer-wise latency interpretation table) |
| Need to identify the highest-latency request for AutoAnalysis | § [SA-Perf-XArgus-Account](./playbook-K-storage-perf-deep.md#sa-perf-xargus-account--account-level-latency-percentiles-via-xargus-p50p90p99p999--auth-fe-tableserver-stream-breakdown) (Server Request Id co-located with latency percentile) |

### Step 5 — Tenant / stamp health routing

| Symptom | Anchor |
|---|---|
| Multiple SAs in same region all show latency / availability drop at the same time | § [SA-Perf-TenantHealth](./playbook-K-storage-perf-deep.md#sa-perf-tenanthealth--storage-tenant-stamp-level-health-check--xargus-tenant-percentiles--xportal-tenant-dashboard) (XPortal tenant dashboard with Low Total Availability Account Count + High PutPage Latency Account Count charts + TenantPerfPercentiles5M KQL + Iridias LSI check) |
| Need stamp identification from a SA endpoint | § [SA-Perf-TenantHealth](./playbook-K-storage-perf-deep.md#sa-perf-tenanthealth--storage-tenant-stamp-level-health-check--xargus-tenant-percentiles--xportal-tenant-dashboard) (`nslookup <SA>.blob.core.windows.net` method + XPortal method) |
| Server Latency time-spent breakdown points to TableServer partition issue | § [SA-Perf-PartitionDowntime](./playbook-K-storage-perf-deep.md#sa-perf-partitiondowntime--jarvis-mdmgeneva-xstorepartitiondowntimeevent--load-balancing-split-events) (Jarvis Xstore.PartitionDowntimeEvent: LBType + Reason) |

### Step 6 — Page Blob specific routing

| Symptom | Anchor |
|---|---|
| Page Blob latency / throughput / IOPS issue (DiskPageBlob vs PageBlob distinction) | § [SA-Perf-PageBlob](./playbook-K-storage-perf-deep.md#sa-perf-pageblob--azure-page-blob-deep-dive--xblobfe-getpageputpage-+-scalability-targets-+-mdm-frontend-logs) (XBlobFE GetPage / PutPage filtering in Shoebox + scalability target check + MDM FrontEnd Logs Blob template + migration to Premium Page Blobs guidance) |
| `ServerTimeoutError` in MDM FrontEnd Blob logs | § [SA-Perf-PageBlob](./playbook-K-storage-perf-deep.md#sa-perf-pageblob--azure-page-blob-deep-dive--xblobfe-getpageputpage-+-scalability-targets-+-mdm-frontend-logs) → cross-link § SA-Perf-PartitionDowntime |

### Step 7 — Azure Files backend routing (XStore-side; client-side / SMB/NFS / Guest-OS → L)

| Symptom | Anchor |
|---|---|
| Master scoping + data collection for an Azure Files perf case (PerfInsights `azurefiles` scenario + scoping questions + reference limits) | § [SAF-AzureFiles-PerfWorkflow](./playbook-K-storage-perf-deep.md#saf-azurefiles-perfworkflow--cross-link-stub-azure-files-performance-workflow-master-entry-point--scoping-questions--internal-data-collection--perfinsights-azurefiles-scenario--labbox--guest-os-funnels-to-L) (cross-link stub — Guest-OS deep TS goes to L) |
| Azure Files share backend XStore perf (XFileFE Read/Write + per-share 1000 IOPS / 60 MB/s limits + MDM Geneva XFileFE logs) | § [SA-Perf-AzureFiles-Backend](./playbook-K-storage-perf-deep.md#sa-perf-azurefiles-backend--azure-files-share-backend-perf-investigation--xfilefe-readwrite-+-per-share-1000-iops--60-mbs-limits-+-cross-zone-traffic-detection-+-mdm-xstorefrontendsummaryperflogs--xnfsperfmetric--xsmbperfmetric) (sibling to PageBlob) |
| End-to-end latency >> Server latency on Azure Files — likely cross-zone traffic (>10ms gap signal) | § [SA-Perf-AzureFiles-Backend](./playbook-K-storage-perf-deep.md#sa-perf-azurefiles-backend--azure-files-share-backend-perf-investigation--xfilefe-readwrite-+-per-share-1000-iops--60-mbs-limits-+-cross-zone-traffic-detection-+-mdm-xstorefrontendsummaryperflogs--xnfsperfmetric--xsmbperfmetric) (Cross-Zone Traffic section + Zonal Placement preview signup form + eligibility: Premium LRS + specific regions) |
| Heavy metadata workload causing throttling (`SuccessWithMetadataThrottling` ResponseType) or warning (`SuccessWithMetadataWarning`) | § [SA-Perf-AzureFiles-HeavyMetadata](./playbook-K-storage-perf-deep.md#sa-perf-azurefiles-heavymetadata--azure-files-heavy-metadata-throttling--successwithmetadatawarning--successwithmetadatathrottling-rca-via-xstorexfilethrottletransaction-+-metadata-iops-tier-table) (XStoreXFileThrottleTransaction KQL + metadata IOPS tier table 12K Standard/12K Premium HDD/35K Premium SSD w/ caching) |
| Customer wants to enable Premium SMB Metadata Caching feature (Preview) | § [SA-Perf-AzureFiles-MetadataCaching](./playbook-K-storage-perf-deep.md#sa-perf-azurefiles-metadatacaching--premium-smb-files-metadata-caching-runtime-state-preview--primary-fix-path-for-heavy-metadata-throttling--afec-feature-registration-+-region-list-+-no-backend-verification-+-pm-contacts) (FileStorage kind only + AFEC registration + region list + ~1h hydration + no backend verification + PM contacts) |

### Step 8 — Pull foundation evidence

| Data | Cluster.Database.Table | When |
|---|---|---|
| Account-level latency percentiles (P50 / P90 / P99 / P99.9) | `xargus.centralus.kusto.windows.net.Production.AccountPerfPercentiles5M` (or 1H/1D) | Latency RCA per SA |
| Tenant-level latency percentiles (stamp-wide) | `xargus.centralus.kusto.windows.net.Production.TenantPerfPercentiles5M` (or 1H/1D) | Stamp-wide perf health check |
| ARM call → XStore 503 throttle correlation | `armprodgbl.<region>.ARMProd.Storage.StorageOperations` (macro-expand) | ARM internal storage call failures |
| Stamp partition downtime / load balance / split | Jarvis MDM `Xstore.PartitionDowntimeEvent` | Server-side latency / availability drop with TableServer-side time |
| SA throttling trace (HostKQL pattern in storage-account-queries.md) | `armprodgbl.<region>.ARMProd.Storage.StorageOperations` (alt: XPortal Shoebox / ASC Perf tab) | 429 throttling RCA |
| SA properties + tenant + stamp lookup | `azcore.Xstore.XStoreAccountProperties` + `xstore.xstore.AccountCapacityDailyV3` | Foundation lookup (cross-link J § SA-Mgmt-* utility) |
| Azure Files share metadata throttling RCA | `azcore.centralus.kusto.windows.net.Xstore.XStoreXFileThrottleTransaction` joined to `xstore.xstore.StorageAccountCapTX` | Step 7 § SA-Perf-AzureFiles-HeavyMetadata (SuccessWithMetadataWarning / SuccessWithMetadataThrottling) |

Foundation KQL bodies live in [`references/storage-account-queries.md`](../catalogs/storage-account-queries.md) § Storage Performance — XArgus + § Storage Operations (StorageOperations table).

### Step 9 — Mitigation + handoffs

| Scenario | Owner |
|---|---|
| **ARM-side XStore throttling** (parent ICM 234324617, mitigated 2021-04-21) | **CSS ARM team FIRST** (collab) — do NOT open new ICM unless they direct |
| Customer SA hitting scalability target (IOPS / Ingress / Egress) | Customer migrates blobs, increases SA count, or moves to Premium SKU; quota increase via ICM template `O2tP1h` → **XStore Quota team** (J § SA-Mgmt-IncreaseLimits) |
| Customer hitting 20,000 IOPS limit on Standard SA, may have 50,000 IOPS variant | Verify per [Announcing larger, higher scale storage accounts](https://azure.microsoft.com/en-us/blog/announcing-larger-higher-scale-storage-accounts/); customer eligibility check |
| Server-side latency / availability drop confirmed (XStore Stamp issue) | Iridias / ICM lookup for active LSI; if NOT existing → ICM to **XStore PG** (Tenant impacting) |
| Server-side `ServerTimeoutError` → Table Server partition issue | Investigate `Xstore.PartitionDowntimeEvent` for `LBType=Split` + Reason; if persistent → **XStore PG** (Partition team) |
| Higher Client Latency than Server Latency | NOT a Storage issue → IaaS VM Perf workflow / Guest-OS investigation (Playbook G / OS team) |
| Azure Files SMB Windows Explorer slow file open/save/close | → **Playbook L** (registry workaround in client; not server-side) |
| Linux OS disk full → `No space left on device` | → **Playbook F § OS-Disk-Resize** or Linux disk cleanup (out of K scope) |
| Page Blob throttling / scalability hit | Customer reduces per-blob TX, leverages multiple page blobs, OR migrates to [Premium Page Blobs (Disks)](https://docs.microsoft.com/en-us/azure/virtual-machines/windows/premium-storage) |
| Azure Files Heavy Metadata throttling (`SuccessWithMetadataThrottling` confirmed) | Standard share → migrate to Premium SSD + enable Metadata Caching (K § SA-Perf-AzureFiles-MetadataCaching); Premium share → enable Metadata Caching. Workarounds: mount VHD on share, split into multiple shares, modify app |
| Azure Files cross-zone traffic detected (end-to-end vs Server diff >10ms) | Zonal Placement preview signup form — **ONLY if Premium LRS + supported region** (see § SA-Perf-AzureFiles-Backend eligibility list). Pin SA to AZ + align VM to same AZ |
| Azure Files Metadata Caching feature registered but no perf benefit after 1 week | Open ICM with subscription IDs + company name. PM contacts CC `metadatacss@microsoft.com` |
| Customer asks for SLA on Standard Storage latency | **There is NO SLA on Storage latency**. Reference numbers (Standard 2-digit ms, Premium 1-digit ms) are INTERNAL ONLY — do NOT share with customer |

## Cross-references

| Other playbook / reference | Why |
|---|---|
| Playbook C § THR-Perf-3 / 4 | Tactical 429 throttling response (basics); K owns deep XStore-side RCA |
| Playbook J § SA-Mgmt-IncreaseLimits | SA capacity / IOPS / Ingress / Egress quota increase (template `O2tP1h`) |
| Playbook J § SA-Util-QueryRSRP | RSRP verbose logs for any SA op (CorrelationId-based) — useful when K detects ARM-side issue and wants to trace deeper into SRP |
| Playbook J § SA-Util-LookupCRUD-CtrlPlane | 3-step control-plane SA CRUD ops foundation (orientation when ARM error involves a recent SA config change) |
| Playbook L (TBD) | Azure Files + AFS — SMB / NFS perf, Heavy Metadata, Premium Files SMB Runtime State Metadata Caching, Azure Files Storage Back End Performance |
| Playbook F § Disk-Perf | Managed disk perf (per-disk IOPS/MBps limit hit, disk IO blip, accelerated networking) |
| Playbook G | IaaS VM Perf — when Client Latency >> Server Latency suggests Guest-OS perf issue |
| `references/storage-account-queries.md` | All XArgus + ARMProd.Storage.StorageOperations + perf-related KQL foundation bodies |
| [Storage Service Throttling Timeouts](https://supportability.visualstudio.com/AzureDev/_wiki/wikis/Dev_Storage/1833046/Storage-Service-Throttling-Timeouts) (Dev_Storage wiki 1833046) | Dev Storage retry/timeout reference for 503/throttling |
| https://aka.ms/iridias | Active Storage LSI / outage tracker — **always check FIRST** for availability drops |
| https://aka.ms/xportal | SA tenant/stamp lookup + Shoebox API Investigation Dashboard |
| https://aka.ms/CoreIdentity | XArgusKustoAccess + XStorePartnersKusto entitlement requests (24h propagation, 48h SLA) |
