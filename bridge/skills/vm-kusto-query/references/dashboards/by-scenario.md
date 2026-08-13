# Dashboards — By Investigation Scenario

> Hand-curated map of which dashboard pages are worth opening for each kind of investigation.
> For a complete machine-generated listing, see [INDEX.md](INDEX.md); for grepping panel names, see [panel-index.md](panel-index.md).
>
> **Workflow** (preferred — every ASI page has an Investigation Guide):
> 1. Pick the scenario below that matches your TSG / case.
> 2. Click the page link — it opens that page's `investigation-guide/README.md` (curated, symptom-keyed chapter index).
> 3. Pick the chapter whose intent matches your symptom; the chapter file inlines the KQL bodies with purpose / params / signal-filter hints.
> 4. Substitute params (`{globalFrom}`, `{nodeId}`, `{_vmid}`, `{_containerid}`, …) with your case values. If alias resolution is unclear, see the page's `meta.json` (`paramAliases`).
> 5. Run via the kusto MCP tool (preferred) or the page's `replay.py` script (auto-resolves all aliases).
>
> **Fallback**: when no Investigation Guide exists, open `library.md` and copy the `kustoQuery` field from `library.json`.

---

## VM lifecycle, availability, restarts

| Page | Why open it |
|------|-------------|
| [azure-vm](asi/pages/azure-vm/investigation-guide/README.md) | **Primary** Azure VM page — 160 panels covering AIR-BP, ASAP NVMe, container/tenant health, Hyper-V events, VMA/VMAL ops, Holmes, scheduled events, RH annotations |
| [azure-vm-compare](asi/pages/azure-vm-compare/investigation-guide/README.md) | Side-by-side comparison between two VMs |
| [vm-availability](asi/pages/vm-availability/investigation-guide/README.md) | VM availability metric trends, downtime annotations |
| [vmd-vm-config](asi/pages/vmd-vm-config/investigation-guide/README.md) | VM config snapshot (HW SKU, image, extensions) |
| [vmdash-vmhistory](asi/pages/vmdash-vmhistory/investigation-guide/README.md) | VMHistory lookup (region/tenant/node) |
| [vmscuba-vm-details](asi/pages/vmscuba-vm-details/investigation-guide/README.md) | VM Scuba details |
| [wf-unexpected-restart](asi/pages/wf-unexpected-restart/investigation-guide/README.md) | Unexpected-restart workflow / root-cause categorization |
| [wf-resource-health](asi/pages/wf-resource-health/investigation-guide/README.md) | Resource Health workflow (RHC events) |
| [fabric-virtual-machines](asi/pages/fabric-virtual-machines/investigation-guide/README.md) | Fabric (TM) view of VMs |

## Host node / cluster / fabric

| Page | Why open it |
|------|-------------|
| [azure-host-node](asi/pages/azure-host-node/investigation-guide/README.md) | **Primary** host node page — 234 panels: AIR-BP/AIR-J, Direct Drive perf, Anvil events, fabric fault handler, hawkeye, host charts (ASAP, memory, CPU), Hyper-V, kernel agent |
| [azure-host-compare](asi/pages/azure-host-compare/investigation-guide/README.md) | Two-node comparison |
| [fabric-nodes](asi/pages/fabric-nodes/investigation-guide/README.md) | Fabric/TM node view |
| [fabric-containers](asi/pages/fabric-containers/investigation-guide/README.md) | Fabric/TM container view |
| [nh-nodes](asi/pages/nh-nodes/investigation-guide/README.md) | Node Health rollup |
| [hrm-nodeid](asi/pages/hrm-nodeid/investigation-guide/README.md) | Host Resource Manager per nodeId |
| [ns-node-view](asi/pages/ns-node-view/investigation-guide/README.md) | Node Service view (incl. Anvil repair diagnostics) |
| [ns-node-capabilities-service](asi/pages/ns-node-capabilities-service/investigation-guide/README.md) | Node capability service traces |
| [ns-fast-attach-detach-operations](asi/pages/ns-fast-attach-detach-operations/investigation-guide/README.md) | Fast attach/detach (NVMe) operations |
| [ns-peregrine](asi/pages/ns-peregrine/investigation-guide/README.md) / [ns-peregrine-container-events](asi/pages/ns-peregrine-container-events/investigation-guide/README.md) | Peregrine (serial console backend) |
| [ns-cumulus-test-suite](asi/pages/ns-cumulus-test-suite/investigation-guide/README.md) / [ns-cumulus-tip-node-session](asi/pages/ns-cumulus-tip-node-session/investigation-guide/README.md) | Cumulus test runs / TiP sessions |

## EEE (one-stop investigation hub)

| Page | Why open it |
|------|-------------|
| [eee-rdos-start-hub](asi/pages/eee-rdos-start-hub/investigation-guide/README.md) | **EEE Start Hub** — 166 queries / 31 panels: at-a-glance availability (cluster/container/node/network), CRP operation, GA & extension, host CPU/mem, performance metrics, automated detectors. The single most useful page when triaging a VM availability case. |
| [eee-rdos-issue-detectors](asi/pages/eee-rdos-issue-detectors/investigation-guide/README.md) | Automated issue detectors (catalog of detector signals) |
| [eee-crp-vm-operation](asi/pages/eee-crp-vm-operation/investigation-guide/README.md) | EEE flavored CRP-operation drilldown |
| [eee-cm-throttling](asi/pages/eee-cm-throttling/investigation-guide/README.md) | CM throttling investigation |
| [eee-storage-managed-disk-events](asi/pages/eee-storage-managed-disk-events/investigation-guide/README.md) | Managed disk-side events seen from EEE |
| [eee-storage-xstore-transaction-resource-01](asi/pages/eee-storage-xstore-transaction-resource-01/investigation-guide/README.md) | XStore transaction-resource view |

## CRP (Compute Resource Provider)

| Page | Why open it |
|------|-------------|
| [crp-home](asi/pages/crp-home/investigation-guide/README.md) | CRP home portal |
| [crp-vm-start-troubleshooter](asi/pages/crp-vm-start-troubleshooter/investigation-guide/README.md) | **Best entry** for VM start failures |
| [crp-debug-vm-operation](asi/pages/crp-debug-vm-operation/investigation-guide/README.md) | CRP debug for a specific VM operation |
| [crp-operation-id](asi/pages/crp-operation-id/investigation-guide/README.md) / [crp-correlation-id](asi/pages/crp-correlation-id/investigation-guide/README.md) | Drill down by operationId / correlationId |
| [crp-debug-allocations](asi/pages/crp-debug-allocations/investigation-guide/README.md) | Allocation debugging |
| [crp-vmss-fabric-placements](asi/pages/crp-vmss-fabric-placements/investigation-guide/README.md) | VMSS fabric placement decisions |
| [crp-vms](asi/pages/crp-vms/investigation-guide/README.md) / [crp-scale-sets](asi/pages/crp-scale-sets/investigation-guide/README.md) | CRP-side VM / VMSS lookup |
| [crp-resource-groups](asi/pages/crp-resource-groups/investigation-guide/README.md) / [crp-subscriptions](asi/pages/crp-subscriptions/investigation-guide/README.md) | RG / subscription view |
| [crp-resource-move](asi/pages/crp-resource-move/investigation-guide/README.md) | Move operations |
| [crp-api-qos](asi/pages/crp-api-qos/investigation-guide/README.md) / [crp-gateway-qos](asi/pages/crp-gateway-qos/investigation-guide/README.md) | API / gateway QoS metrics |

## Disk (Managed Disks)

| Page | Why open it |
|------|-------------|
| [md-disks](asi/pages/md-disks/investigation-guide/README.md) | Disk lookup |
| [md-managed-by-vm](asi/pages/md-managed-by-vm/investigation-guide/README.md) | Disks owned by a VM |
| [md-operation-id](asi/pages/md-operation-id/investigation-guide/README.md) / [md-correlation-id](asi/pages/md-correlation-id/investigation-guide/README.md) | DRP operation/correlation drilldown |
| [azure-disk](asi/pages/azure-disk/investigation-guide/README.md) | Azure-side disk view (storage tenant + xstore) |
| [drp-operation-id](asi/pages/drp-operation-id/investigation-guide/README.md) | DRP operation drilldown |

## Allocation / scheduling (Aztec / AZSM / fabric placement)

| Page | Why open it |
|------|-------------|
| [aztec-clusters](asi/pages/aztec-clusters/investigation-guide/README.md) | Cluster availability, AzSM service health |
| [aztec-containers](asi/pages/aztec-containers/investigation-guide/README.md) | **30 queries** — container snapshot, Air managed events, container lifecycle |
| [aztec-nodes](asi/pages/aztec-nodes/investigation-guide/README.md) | Node-side aztec view |
| [aztec-virtual-machines](asi/pages/aztec-virtual-machines/investigation-guide/README.md) | VM-side aztec view |
| [aztec-az-allocator-allocations](asi/pages/aztec-az-allocator-allocations/investigation-guide/README.md) | AzAllocator allocations |
| [aztec-az**sm-cluster** / **azsm-application** / **azsm-service**](asi/pages/aztec-azsm-cluster/investigation-guide/README.md) | AZSM hierarchy |
| [aztec-service-healing-investigations](asi/pages/aztec-service-healing-investigations/investigation-guide/README.md) | SH investigation hub |
| [aztec-availability-zones](asi/pages/aztec-availability-zones/investigation-guide/README.md) / [aztec-regions](asi/pages/aztec-regions/investigation-guide/README.md) / [aztec-datacenters](asi/pages/aztec-datacenters/investigation-guide/README.md) | Topology |
| [aztec-tenant](asi/pages/aztec-tenant/investigation-guide/README.md) / [aztec-subscription](asi/pages/aztec-subscription/investigation-guide/README.md) | Tenant / subscription rollups |
| [aztec-activity-id](asi/pages/aztec-activity-id/investigation-guide/README.md) / [aztec-related-activity-id](asi/pages/aztec-related-activity-id/investigation-guide/README.md) | Trace by activityId |
| [aztec-walmart-dashboard](asi/pages/aztec-walmart-dashboard/investigation-guide/README.md) | Customer-specific (Walmart) rollup |

## ARM (control plane)

| Page | Why open it |
|------|-------------|
| [arm-activity-ids](asi/pages/arm-activity-ids/investigation-guide/README.md) / [arm-correlation-ids](asi/pages/arm-correlation-ids/investigation-guide/README.md) | Trace by activityId / correlationId |
| [arm-customer-journey](asi/pages/arm-customer-journey/investigation-guide/README.md) | Customer journey across ARM ops |
| [arm-deployments](asi/pages/arm-deployments/investigation-guide/README.md) | Deployment-history view |
| [arm-resource-groups](asi/pages/arm-resource-groups/investigation-guide/README.md) / [arm-subscriptions](asi/pages/arm-subscriptions/investigation-guide/README.md) | RG / sub lookup |
| [arm-sub-throttling](asi/pages/arm-sub-throttling/investigation-guide/README.md) | Subscription throttling |
| [arm-cobe-control-plane-region-insights](asi/pages/arm-cobe-control-plane-region-insights/investigation-guide/README.md) | Regional control-plane insights (incl. ICM correlation) |
| [arm-azure-recall](asi/pages/arm-azure-recall/investigation-guide/README.md) | Recall events |

## Networking (NRP, NM, VFP)

| Page | Why open it |
|------|-------------|
| [nrp-operation-id](asi/pages/nrp-operation-id/investigation-guide/README.md) / [nrp-client-operation-id-search](asi/pages/nrp-client-operation-id-search/investigation-guide/README.md) / [nrp-correlation-request-id-view](asi/pages/nrp-correlation-request-id-view/investigation-guide/README.md) | NRP operation drilldowns |
| [nrp-frontend-qos](asi/pages/nrp-frontend-qos/investigation-guide/README.md) / [nrp-gateway-qos](asi/pages/nrp-gateway-qos/investigation-guide/README.md) / [nrp-performance-drilldown](asi/pages/nrp-performance-drilldown/investigation-guide/README.md) / [nrp-latency-perf-investigation](asi/pages/nrp-latency-perf-investigation/investigation-guide/README.md) | NRP perf |
| [nrp-load-balancer](asi/pages/nrp-load-balancer/investigation-guide/README.md) / [nrp-vips](asi/pages/nrp-vips/investigation-guide/README.md) / [nrp-firewall](asi/pages/nrp-firewall/investigation-guide/README.md) / [nrp-byoip](asi/pages/nrp-byoip/investigation-guide/README.md) / [nrp-public-ip-address](asi/pages/nrp-public-ip-address/investigation-guide/README.md) / [nrp-network-security-groups](asi/pages/nrp-network-security-groups/investigation-guide/README.md) | Per-resource-type pages |
| [nrp-virtual-networks](asi/pages/nrp-virtual-networks/investigation-guide/README.md) / [nrp-subnets](asi/pages/nrp-subnets/investigation-guide/README.md) / [nrp-route-tables](asi/pages/nrp-route-tables/investigation-guide/README.md) / [nrp-vnet-encryption](asi/pages/nrp-vnet-encryption/investigation-guide/README.md) | VNet hierarchy |
| [nrp-network-interfaces](asi/pages/nrp-network-interfaces/investigation-guide/README.md) / [nrp-management-nic](asi/pages/nrp-management-nic/investigation-guide/README.md) | NIC views |
| [nrp-private-endpoint](asi/pages/nrp-private-endpoint/investigation-guide/README.md) / [nrp-private-link-service](asi/pages/nrp-private-link-service/investigation-guide/README.md) / [nrp-pls-search](asi/pages/nrp-pls-search/investigation-guide/README.md) | Private link |
| [nrp-azure-profiles](asi/pages/nrp-azure-profiles/investigation-guide/README.md) / [nrp-name-reservation](asi/pages/nrp-name-reservation/investigation-guide/README.md) | Profiles / reservations |
| [nrp-read-operation-service](asi/pages/nrp-read-operation-service/investigation-guide/README.md) / [nrp-long-running-operations](asi/pages/nrp-long-running-operations/investigation-guide/README.md) / [nrp-customer-write-operations](asi/pages/nrp-customer-write-operations/investigation-guide/README.md) | Operation categories |
| [nrp-delete-tenant-operation](asi/pages/nrp-delete-tenant-operation/investigation-guide/README.md) / [nrp-delete-vmss-operation-drilldown](asi/pages/nrp-delete-vmss-operation-drilldown/investigation-guide/README.md) / [nrp-put-vmss-operation-drilldown](asi/pages/nrp-put-vmss-operation-drilldown/investigation-guide/README.md) | Delete / Put VMSS ops |
| [nrp-batch-manager-drilldown](asi/pages/nrp-batch-manager-drilldown/investigation-guide/README.md) / [nrp-backup-operation](asi/pages/nrp-backup-operation/investigation-guide/README.md) / [nrp-operation-details](asi/pages/nrp-operation-details/investigation-guide/README.md) | Misc NRP |
| [nrp-resource-groups](asi/pages/nrp-resource-groups/investigation-guide/README.md) / [nrp-subscriptions](asi/pages/nrp-subscriptions/investigation-guide/README.md) | NRP-side RG/sub |
| [nm-merlin-timeline](asi/pages/nm-merlin-timeline/investigation-guide/README.md) / [nm-mizar-validation](asi/pages/nm-mizar-validation/investigation-guide/README.md) / [nm-nic-interfaces-merlin](asi/pages/nm-nic-interfaces-merlin/investigation-guide/README.md) | NM (Merlin / Mizar) timelines |
| [nm-nsm-plus-wcf-request-search](asi/pages/nm-nsm-plus-wcf-request-search/investigation-guide/README.md) / [nm-nsm-qos-info-search](asi/pages/nm-nsm-qos-info-search/investigation-guide/README.md) | NSM / WCF |
| [nm-tdpr](asi/pages/nm-tdpr/investigation-guide/README.md) / [nm-vip-search](asi/pages/nm-vip-search/investigation-guide/README.md) | TDPR / VIP search |
| [netan-packetcapturehelper](asi/pages/netan-packetcapturehelper/investigation-guide/README.md) | NetAn packet capture helper |

## Recovery / Anvil / In-place repair

| Page | Why open it |
|------|-------------|
| [anvil-node](asi/pages/anvil-node/investigation-guide/README.md) | Anvil node lookup |
| [anvil-unhealthy-helper](asi/pages/anvil-unhealthy-helper/investigation-guide/README.md) | Unhealthy node helper |
| [anvil-node-in-place-recovery-status](asi/pages/anvil-node-in-place-recovery-status/investigation-guide/README.md) | In-place recovery status |
| [anvil-node-recovery-detail](asi/pages/anvil-node-recovery-detail/investigation-guide/README.md) | Recovery action details |

## Storage account / blob / XStore

| Page | Why open it |
|------|-------------|
| [storage-account](asi/pages/storage-account/investigation-guide/README.md) | Per-storage-account view |
| [storage-tenant](asi/pages/storage-tenant/investigation-guide/README.md) | Storage tenant rollup |
| [storage-control-plane-dashboard](asi/pages/storage-control-plane-dashboard/investigation-guide/README.md) | Storage CP |
| [storage-lifecycle-management](asi/pages/storage-lifecycle-management/investigation-guide/README.md) | Lifecycle policy investigations |
| [storage-billing-drilldown](asi/pages/storage-billing-drilldown/investigation-guide/README.md) | Billing |
| [blob-inventory](asi/pages/blob-inventory/investigation-guide/README.md) | Blob inventory |

## Recovery Services Vault (RSV)

| Page | Why open it |
|------|-------------|
| [rsv-hsr](asi/pages/rsv-hsr/investigation-guide/README.md) | HSR (hardened soft delete / heartbeat) |
| [rsv-private-endpoint](asi/pages/rsv-private-endpoint/investigation-guide/README.md) / [rsv-privateendpointpage](asi/pages/rsv-privateendpointpage/investigation-guide/README.md) | RSV private endpoints |

## Confidential VM / Dedicated Host / Image Builder / Gallery

| Page | Why open it |
|------|-------------|
| [acc-confidential-virtual-machines](asi/pages/acc-confidential-virtual-machines/investigation-guide/README.md) / [cvm-confidential-virtual-machine](asi/pages/cvm-confidential-virtual-machine/investigation-guide/README.md) / [cvm-fabric-settings](asi/pages/cvm-fabric-settings/investigation-guide/README.md) | Confidential VM |
| [adh-host-groups](asi/pages/adh-host-groups/investigation-guide/README.md) / [adh-adh-host-list-under-an-adh-group](asi/pages/adh-adh-host-list-under-an-adh-group/investigation-guide/README.md) | Azure Dedicated Host |
| [aib-kpis](asi/pages/aib-kpis/investigation-guide/README.md) / [aib-build-status](asi/pages/aib-build-status/investigation-guide/README.md) / [aib-error-drilldown](asi/pages/aib-error-drilldown/investigation-guide/README.md) / [aib-customer-drilldown](asi/pages/aib-customer-drilldown/investigation-guide/README.md) / [aib-region-overview](asi/pages/aib-region-overview/investigation-guide/README.md) / [aib-subscriptions-with-failures](asi/pages/aib-subscriptions-with-failures/investigation-guide/README.md) / [aib-correlation-id](asi/pages/aib-correlation-id/investigation-guide/README.md) / [aib-operation-id](asi/pages/aib-operation-id/investigation-guide/README.md) / [aib-subscription-id](asi/pages/aib-subscription-id/investigation-guide/README.md) / [aib-deployments](asi/pages/aib-deployments/investigation-guide/README.md) / [aib-service-build](asi/pages/aib-service-build/investigation-guide/README.md) / [aib-async-qos-events](asi/pages/aib-async-qos-events/investigation-guide/README.md) / [aib-preview-dotnet-image-templates](asi/pages/aib-preview-dotnet-image-templates/investigation-guide/README.md) / [aib-prod-dotnet-image-templates](asi/pages/aib-prod-dotnet-image-templates/investigation-guide/README.md) | Image Builder (AIB) |
| [acg-copy-statistics](asi/pages/acg-copy-statistics/investigation-guide/README.md) | Azure Compute Gallery copy statistics |

## Serial Console

| Page | Why open it |
|------|-------------|
| [serial-console-home](asi/pages/serial-console-home/investigation-guide/README.md) | Entry page |
| [serial-console-customer-journey](asi/pages/serial-console-customer-journey/investigation-guide/README.md) | End-to-end customer journey |
| [serial-console-gateway-health-check](asi/pages/serial-console-gateway-health-check/investigation-guide/README.md) | Gateway health |
| [serial-console-peregrine-container-events](asi/pages/serial-console-peregrine-container-events/investigation-guide/README.md) | Peregrine container events for SAC |
| [serial-console-usage-statistics](asi/pages/serial-console-usage-statistics/investigation-guide/README.md) | Usage stats |
| [serial-console-ux-activities](asi/pages/serial-console-ux-activities/investigation-guide/README.md) | UX activities (failed login etc.) |

## Misc / cross-cutting tools

| Page | Why open it |
|------|-------------|
| [execution-graph](asi/pages/execution-graph/investigation-guide/README.md) / [execution-graph-correlation-or-operation-id](asi/pages/execution-graph-correlation-or-operation-id/investigation-guide/README.md) | Execution-graph viewer (cross-service traces) |
| [mycroft-container](asi/pages/mycroft-container/investigation-guide/README.md) | Mycroft container probes |
| [fp-favorites](asi/pages/fp-favorites/investigation-guide/README.md) | Favorites portal |
| [azure-subscription](asi/pages/azure-subscription/investigation-guide/README.md) | Subscription rollup |
| [vm-vmss-crud-hub-resource-uri](asi/pages/vm-vmss-crud-hub-resource-uri/investigation-guide/README.md) | VM/VMSS CRUD hub (by resource URI) |

---

## When you don't know which page to open

1. **Grep `panel-index.md`** for the panel name the TSG mentions, e.g.:
   ```powershell
   Select-String "Container State" .github/skills/vm-kusto-query/references/dashboards/panel-index.md
   ```
   The matched row's `Guide` column links straight to that page's `investigation-guide/README.md`.
2. **Grep the Investigation Guides directly** when the TSG describes a symptom (no panel name):
   ```powershell
   Select-String "ContainerState" .github/skills/vm-kusto-query/references/dashboards/asi/pages/*/investigation-guide/*.md
   ```
3. If the TSG cites an ASI URL with a service / page name, match it against [INDEX.md](INDEX.md) (slug column).
4. If the TSG just says "look at ASI for VM availability" — start with `eee-rdos-start-hub`, then `azure-vm`, then `azure-host-node`. All three have rich Investigation Guides.
