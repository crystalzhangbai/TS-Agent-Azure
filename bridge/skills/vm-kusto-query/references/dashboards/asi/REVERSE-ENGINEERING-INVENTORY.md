# ASI Dashboard Reverse-Engineering Inventory

Catalog of ASI (Azure Service Insights) dashboard pages whose underlying KQL queries have been extracted into the `dashboards/asi/pages/<slug>/` library.

Each page directory contains:
- `library.json` - panel-organized KQL queries with full bodies, params, schemas
- `library.md` - human-readable index
- `meta.json` - service / page metadata, input parameters
- `investigation-guide/` - chapter-keyed markdown for symptom-driven investigation
- Raw extraction outputs (`page.json`, `queries.json`, `query-refs.json`, `compound-widget-groups.json`, `extraction-summary.json`)

The `vm-kusto-query` skill consumes `library.json` to run queries directly without rendering the ASI dashboard.

## Summary

- **Services reverse-engineered**: 33
- **Pages**: 162
- **Total query records** (sum across all pages, may include duplicate groupIds across services): 2332

## Services by query volume

| Service | Pages | Queries (sum) |
|---|--:|--:|
| EEE RDOS | 5 | 716 |
| Azure Host | 6 | 595 |
| NRP | 35 | 234 |
| Aztec | 17 | 182 |
| CRP | 14 | 140 |
| NodeService | 7 | 84 |
| ARM | 9 | 73 |
| Storage Tools | 6 | 46 |
| Azure Serial Console | 6 | 41 |
| Azure VM Image Builder | 14 | 38 |
| Network Manager | 7 | 30 |
| Managed Disk | 4 | 21 |
| Recovery Services Vaults | 3 | 20 |
| EEE CRP | 1 | 19 |
| VM Scuba | 1 | 17 |
| VM VMSS CRUD Hub | 1 | 16 |
| ACC CVM | 2 | 15 |
| Anvil Unhealthy | 4 | 14 |
| Fabric | 3 | 6 |
| ACC | 1 | 3 |
| DRP | 1 | 3 |
| EEE Storage | 2 | 3 |
| Execution Graph | 2 | 3 |
| Host Resource Manager | 1 | 3 |
| Mycroft | 1 | 3 |
| Azure Compute Gallery | 1 | 1 |
| Azure Dedicated Host | 2 | 1 |
| EEE Compute Manager | 1 | 1 |
| Network Analyser | 1 | 1 |
| Node Heartbeat | 1 | 1 |
| VM Details | 1 | 1 |
| VMDash | 1 | 1 |
| Fabric Platform | 1 | 0 |

## Per-service page detail

### EEE RDOS

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `vm-availability` | VM Availability | 300 | _(none)_ |
| `wf-unexpected-restart` | WF Unexpected Restart | 208 | _(none)_ |
| `eee-rdos-start-hub` | Start Hub | 172 | _(none)_ |
| `wf-resource-health` | WF Resource Health | 32 | _(none)_ |
| `eee-rdos-issue-detectors` | Issue Detectors | 4 | _(none)_ |

### Azure Host

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `azure-host-node` | Azure Host Node | 276 | _(none)_ |
| `azure-vm` | Azure VM | 228 | _(none)_ |
| `azure-host-compare` | Azure Host Compare | 43 | _(none)_ |
| `azure-vm-compare` | Azure VM Compare | 25 | _(none)_ |
| `azure-subscription` | Azure Subscription | 21 | _(none)_ |
| `azure-disk` | Azure Disk | 2 | _(none)_ |

### NRP

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `nrp-put-vmss-operation-drilldown` | PUT VMScaleSet Operation drill down | 30 | _(none)_ |
| `nrp-management-nic` | Management Nic | 19 | _(none)_ |
| `nrp-performance-drilldown` | Nrp Performance Drilldown | 19 | _(none)_ |
| `nrp-vnet-encryption` | Vnet Encryption | 17 | _(none)_ |
| `nrp-subnets` | Subnets | 12 | _(none)_ |
| `nrp-load-balancer` | Load Balancer | 10 | _(none)_ |
| `nrp-subscriptions` | Subscriptions | 10 | _(none)_ |
| `nrp-correlation-request-id-view` | CorrelationRequestIdView | 9 | _(none)_ |
| `nrp-delete-vmss-operation-drilldown` | DELETE VMScaleSet operation drilldown | 9 | _(none)_ |
| `nrp-firewall` | Firewall | 9 | _(none)_ |
| `nrp-private-endpoint` | Private Endpoint | 9 | _(none)_ |
| `nrp-read-operation-service` | ReadOperationService | 9 | _(none)_ |
| `nrp-resource-groups` | Resource Groups | 9 | _(none)_ |
| `nrp-vips` | NRP VIPs | 9 | _(none)_ |
| `nrp-network-interfaces` | Network Interfaces | 6 | _(none)_ |
| `nrp-route-tables` | Route Tables | 6 | _(none)_ |
| `nrp-delete-tenant-operation` | DeleteTenantOperation without Lock in Sync Part- Analysis | 5 | _(none)_ |
| `nrp-network-security-groups` | Network Security Groups | 5 | _(none)_ |
| `nrp-long-running-operations` | LongRunningOperations | 4 | _(none)_ |
| `nrp-backup-operation` | BackupOperation | 3 | _(none)_ |
| `nrp-latency-perf-investigation` | Latency and Performance Investigation Dashboard | 3 | _(none)_ |
| `nrp-virtual-networks` | Virtual Networks | 3 | _(none)_ |
| `nrp-client-operation-id-search` | ClientOperationId Search | 2 | _(none)_ |
| `nrp-customer-write-operations` | Customer Write Operations | 2 | _(none)_ |
| `nrp-frontend-qos` | Frontend QoS | 2 | _(none)_ |
| `nrp-gateway-qos` | Gateway QoS | 2 | _(none)_ |
| `nrp-name-reservation` | NRP Name Reservation | 2 | _(none)_ |
| `nrp-operation-id` | Operation Id | 2 | _(none)_ |
| `nrp-azure-profiles` | AzureProfiles | 1 | _(none)_ |
| `nrp-batch-manager-drilldown` | Batch Manager & NRP Performance Drill Down | 1 | _(none)_ |
| `nrp-byoip` | NRP BYOIP | 1 | _(none)_ |
| `nrp-operation-details` | NRP Operation details | 1 | _(none)_ |
| `nrp-pls-search` | PLS Search | 1 | _(none)_ |
| `nrp-private-link-service` | Private Link Service | 1 | _(none)_ |
| `nrp-public-ip-address` | Public IP Address | 1 | _(none)_ |

### Aztec

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `aztec-tenant` | Tenant {{tenantName}} | 77 | _(none)_ |
| `aztec-containers` | Containers | 30 | _(none)_ |
| `aztec-clusters` | Clusters | 15 | _(none)_ |
| `aztec-nodes` | Nodes | 13 | _(none)_ |
| `aztec-service-healing-investigations` | ServiceHealingInvestigations | 8 | _(none)_ |
| `aztec-virtual-machines` | Virtual Machines | 7 | _(none)_ |
| `aztec-related-activity-id` | RelatedActivityId | 6 | _(none)_ |
| `aztec-activity-id` | ActivityId | 4 | _(none)_ |
| `aztec-subscription` | Subscription | 4 | _(none)_ |
| `aztec-az-allocator-allocations` | AzAllocatorAllocations | 3 | _(none)_ |
| `aztec-azsm-cluster` | AzSM Cluster | 3 | _(none)_ |
| `aztec-walmart-dashboard` | Walmart Dashboard | 3 | _(none)_ |
| `aztec-availability-zones` | Availability Zones | 2 | _(none)_ |
| `aztec-azsm-application` | AzSM Application | 2 | _(none)_ |
| `aztec-datacenters` | DataCenters | 2 | _(none)_ |
| `aztec-regions` | Regions | 2 | _(none)_ |
| `aztec-azsm-service` | AzSM Service | 1 | _(none)_ |

### CRP

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `crp-vms` | VMs | 25 | _(none)_ |
| `crp-operation-id` | OperationId | 21 | _(none)_ |
| `crp-debug-allocations` | Debug Allocations | 20 | _(none)_ |
| `crp-debug-vm-operation` | Debug VM Operation | 18 | _(none)_ |
| `crp-scale-sets` | Scale Sets | 16 | _(none)_ |
| `crp-subscriptions` | Subscriptions | 16 | _(none)_ |
| `crp-resource-move` | Resource Move | 7 | _(none)_ |
| `crp-vm-start-troubleshooter` | VM Start Troubleshooter | 4 | _(none)_ |
| `crp-correlation-id` | CorrelationId | 3 | _(none)_ |
| `crp-resource-groups` | Resource Groups | 3 | _(none)_ |
| `crp-api-qos` | API QoS | 2 | _(none)_ |
| `crp-gateway-qos` | Gateway QoS | 2 | _(none)_ |
| `crp-home` | CRP Home | 2 | _(none)_ |
| `crp-vmss-fabric-placements` | VMSS Fabric Placements | 1 | _(none)_ |

### NodeService

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `ns-node-view` | NodeService_NodeView | 40 | _(none)_ |
| `ns-peregrine-container-events` | Peregrine_ContainerEvents | 23 | _(none)_ |
| `ns-peregrine` | NodeService_Peregrine | 9 | _(none)_ |
| `ns-cumulus-test-suite` | CumulusTestSuite | 4 | _(none)_ |
| `ns-cumulus-tip-node-session` | Cumulus Tip Node Session | 4 | _(none)_ |
| `ns-fast-attach-detach-operations` | FastAttachDetachOperations | 3 | _(none)_ |
| `ns-node-capabilities-service` | NodeCapabilitiesService | 1 | _(none)_ |

### ARM

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `arm-cobe-control-plane-region-insights` | CoBe AzControlPlaneRegionInsights | 19 | _(none)_ |
| `arm-correlation-ids` | Correlation Ids | 11 | _(none)_ |
| `arm-customer-journey` | Customer Journey | 10 | _(none)_ |
| `arm-sub-throttling` | Sub Throttling | 8 | _(none)_ |
| `arm-subscriptions` | Subscriptions | 8 | _(none)_ |
| `arm-activity-ids` | Activity Ids | 6 | _(none)_ |
| `arm-deployments` | Deployments | 5 | _(none)_ |
| `arm-azure-recall` | Azure Recall | 3 | _(none)_ |
| `arm-resource-groups` | Resource Groups | 3 | _(none)_ |

### Storage Tools

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `storage-account` | Storage Account | 12 | _(none)_ |
| `storage-lifecycle-management` | Life Cycle Managment | 10 | _(none)_ |
| `blob-inventory` | Blob Inventory | 7 | _(none)_ |
| `storage-billing-drilldown` | Billing Drilldown | 6 | _(none)_ |
| `storage-control-plane-dashboard` | Control Plane Dashboard | 6 | _(none)_ |
| `storage-tenant` | Storage Tenant | 5 | _(none)_ |

### Azure Serial Console

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `serial-console-peregrine-container-events` | Peregrine_ContainerEvents | 21 | _(none)_ |
| `serial-console-home` | Serial Console Home | 8 | _(none)_ |
| `serial-console-ux-activities` | UX Activities | 6 | _(none)_ |
| `serial-console-usage-statistics` | Usage Statistics | 3 | _(none)_ |
| `serial-console-customer-journey` | Customer Journey | 2 | _(none)_ |
| `serial-console-gateway-health-check` | Gateway Health Check | 1 | _(none)_ |

### Azure VM Image Builder

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `aib-kpis` | AIB KPIs | 8 | _(none)_ |
| `aib-prod-dotnet-image-templates` | Prod Dotnet Image Templates | 6 | _(none)_ |
| `aib-error-drilldown` | Error Drilldown | 4 | _(none)_ |
| `aib-preview-dotnet-image-templates` | Preview Dotnet Image Templates | 4 | _(none)_ |
| `aib-service-build` | serviceBuild | 3 | _(none)_ |
| `aib-build-status` | Build Status | 2 | _(none)_ |
| `aib-correlation-id` | correlationID | 2 | _(none)_ |
| `aib-customer-drilldown` | Customer Drilldown | 2 | _(none)_ |
| `aib-region-overview` | RegionOverview | 2 | _(none)_ |
| `aib-async-qos-events` | AsyncQoSEvents by Operation | 1 | _(none)_ |
| `aib-deployments` | Deployments | 1 | _(none)_ |
| `aib-operation-id` | operationID | 1 | _(none)_ |
| `aib-subscription-id` | subscriptionID | 1 | _(none)_ |
| `aib-subscriptions-with-failures` | Subscriptions with Failures | 1 | _(none)_ |

### Network Manager

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `nm-vip-search` | VIP Search | 10 | _(none)_ |
| `nm-nsm-qos-info-search` | NsmQosInfo Search | 6 | _(none)_ |
| `nm-tdpr` | TDPR | 5 | _(none)_ |
| `nm-mizar-validation` | Mizar Validation | 3 | _(none)_ |
| `nm-nsm-plus-wcf-request-search` | NsmPlus WcfRequest Search | 3 | _(none)_ |
| `nm-merlin-timeline` | MerlinTimeline | 2 | _(none)_ |
| `nm-nic-interfaces-merlin` | Nic Interfaces (Merlin) | 1 | _(none)_ |

### Managed Disk

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `md-correlation-id` | Correlation Id | 9 | _(none)_ |
| `md-disks` | Disks | 6 | _(none)_ |
| `md-operation-id` | Operation Id | 4 | _(none)_ |
| `md-managed-by-vm` | Managed by VM | 2 | _(none)_ |

### Recovery Services Vaults

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `rsv-hsr` | HSR | 16 | _(none)_ |
| `rsv-private-endpoint` | Private Endpoint | 2 | _(none)_ |
| `rsv-privateendpointpage` | PrivateEndpointPage | 2 | _(none)_ |

### EEE CRP

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `eee-crp-vm-operation` | VM Operation | 19 | _(none)_ |

### VM Scuba

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `vmscuba-vm-details` | VM Details | 17 | _(none)_ |

### VM VMSS CRUD Hub

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `vm-vmss-crud-hub-resource-uri` | Resource URI | 16 | _(none)_ |

### ACC CVM

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `cvm-confidential-virtual-machine` | Confidential Virtual Machine | 12 | _(none)_ |
| `cvm-fabric-settings` | Fabric Settings | 3 | _(none)_ |

### Anvil Unhealthy

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `anvil-node-recovery-detail` | Node Recovery Detail | 5 | _(none)_ |
| `anvil-node-in-place-recovery-status` | Node In Place Recovery Status | 4 | _(none)_ |
| `anvil-unhealthy-helper` | Unhealthy Helper | 4 | _(none)_ |
| `anvil-node` | Node | 1 | _(none)_ |

### Fabric

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `fabric-virtual-machines` | Virtual Machines | 3 | _(none)_ |
| `fabric-containers` | Containers | 2 | _(none)_ |
| `fabric-nodes` | Nodes | 1 | _(none)_ |

### ACC

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `acc-confidential-virtual-machines` | Confidential Virtual Machines | 3 | _(none)_ |

### DRP

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `drp-operation-id` | Operation Id | 3 | _(none)_ |

### EEE Storage

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `eee-storage-xstore-transaction-resource-01` | xstore transaction resource 01 | 2 | _(none)_ |
| `eee-storage-managed-disk-events` | Managed Disk Events | 1 | _(none)_ |

### Execution Graph

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `execution-graph-correlation-or-operation-id` | Correlation or Operation Id | 2 | _(none)_ |
| `execution-graph` | Execution Graph | 1 | _(none)_ |

### Host Resource Manager

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `hrm-nodeid` | NodeId | 3 | _(none)_ |

### Mycroft

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `mycroft-container` | Container | 3 | _(none)_ |

### Azure Compute Gallery

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `acg-copy-statistics` | Copy Statistics | 1 | _(none)_ |

### Azure Dedicated Host

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `adh-host-groups` | Host Groups | 1 | _(none)_ |
| `adh-adh-host-list-under-an-adh-group` | ADH Host list under an ADH Group | 0 | _(none)_ |

### EEE Compute Manager

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `eee-cm-throttling` | Throttling | 1 | _(none)_ |

### Network Analyser

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `netan-packetcapturehelper` | PacketCaptureHelper | 1 | _(none)_ |

### Node Heartbeat

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `nh-nodes` | Nodes | 1 | _(none)_ |

### VM Details

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `vmd-vm-config` | VM Config | 1 | _(none)_ |

### VMDash

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `vmdash-vmhistory` | VMHistory | 1 | _(none)_ |

### Fabric Platform

| Slug | Page | Q | Inputs |
|---|---|--:|---|
| `fp-favorites` | Favorites | 0 | _(none)_ |

## Reverse-engineering methodology

### Tools (under `dashboards/asi/_tooling/`)

1. **`extract.js`** - Walks an ASI page widget tree, follows Compound Widget references, batch-fetches resolved KQL queries via `/api/queries/search`. Output: `page.json`, `queries.json`, `query-refs.json`, `compound-widget-groups.json`, `extraction-summary.json`.
2. **`build-library.js`** - Reshapes raw outputs into a panel-organized `library.json` + `library.md` + `meta.json`.
3. **`build-investigation-guide.py`** - Generates symptom-keyed chapter markdown under `investigation-guide/` (auto-split at 45 KB).

### Token capture flow

```
playwright-cli -s=asi attach --cdp=http://127.0.0.1:9222
playwright-cli -s=asi goto <ASI page URL>
# wait ~8s for the page to issue authenticated API calls, then:
playwright-cli -s=asi --raw requests           # find /api/services/<svc>/pages/<id>
playwright-cli -s=asi --raw request <N>        # extract authorization: Bearer header
# save bearer token to dashboards/asi/pages/wf-unexpected-restart/raw/token.txt
playwright-cli -s=asi detach
```

Token TTL is ~1 hour; refresh per batch.

### Standard pipeline

```powershell
$env:PYTHONIOENCODING = "utf-8"   # fixes Unicode print on cp1252
node dashboards\asi\_tooling\extract.js   --token <tokenFile> --service "<Svc>" --page <pageId> --out <outDir>
node dashboards\asi\_tooling\build-library.js --raw <outDir> --out <outDir> --service "<Svc>" --page "<Title>"
python dashboards\asi\_tooling\build-investigation-guide.py --library <outDir>\library.json --out <outDir>\investigation-guide --title "<Svc> - <Title>"
```

### Parallelism

- `extract.js` is API-heavy; safe throttle is **3 concurrent**. Higher throttles (>= 8) occasionally produced empty `queries.json` due to a race condition in `/api/queries/search`.
- `build-library.js` and `build-investigation-guide.py` are local-only; safe at throttle 8-10.

### Special cases

- **EEE RDOS Issue Detectors**: 4 `IssueDetector_EI_*` KQL queries exist only inside Compound Widget Groups and are not referenced by any page. Captured via a synthetic `page.json` stub + hand-built `query-refs.json` running through the same pipeline. See `eee-rdos-issue-detectors/`.
- **Azure Portal**: Uses a non-standard widget schema (inline `root.queries[]` with `selectedProperties` groupId references). `extract.js` does not handle it; skipped intentionally.
- **Compound widget expansion**: Some pages list N visible query widgets but the pipeline resolves more KQLs after following CompoundWidget references (counts in the per-service tables above reflect resolved query records, not widgets).

### Verification

Every page is validated by sampling the first 80 chars of each query KQL body and checking the normalized text appears in at least one `investigation-guide/*.md` file. **Current state: 0 missing queries across all 162 pages.**

## Out of scope

- **Azure Portal** (5 pages) - incompatible schema.
- **Service Fabric** (55 pages), **Fabric Container Service** (15 pages), **Storage Host Agent** (7 pages) - mostly SF / Storage team internal pages; few are customer-facing for VM support cases.
- **Network Connectivity** (8 pages, ER / VPN) - not yet evaluated; potentially in scope for future.
- **External tools** (Eagle Eye, Node Story, standalone vmdash, aka.ms tools) - outside the ASI domain.
- 0-page catalog entries (AzureStorage, Storage, Compute, VMSS, VM Config, Host Networking, Host Analyzer Ex, etc.) - services exist in the ASI catalog but have no published pages.
