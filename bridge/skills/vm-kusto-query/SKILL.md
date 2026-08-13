---
name: vm-kusto-query
description: "Azure infrastructure investigation via Kusto (KQL) across internal clusters (AzureCM, Disks RP, VMInsight, AzCore, AzureDCM, Sparkle, Hawkeye, ICM, Watson, AzPE, CRP, ARMProd, NRP, Hybridnetworking, XStore, XArgus, XLivesite, etc.). Use whenever users mention Kusto/KQL, VM restart/reboot/downtime, disk lifecycle, node fault, service healing, live migration, hardware failure, host update, allocation failure, CRP/ARM tracing, resource health, VFP, boot diagnostics, storage account / Azure Files / AFS / SMB / NFS / Elastic SAN, or networking. Pushy network triggers: network topology, EagleAI, connectivity diagnosis, VM-to-PE/VM-to-VM, Private Link, NSG, ExpressRoute, AFD, VPN, AppGW, vWAN, SLB, DDoS, NRP. Chinese: Kusto查询, KQL查询, 虚拟机重启, 磁盘, 根因分析, 节点故障, 网络拓扑, 连通性诊断, 网络连接, 存储账户, 存储性能, Azure 文件共享, AFS 同步. Default execution uses kusto/azuremcp; use eagleai for networking topology/NetworkARG."
compatibility: "Requires kusto or azuremcp for KQL; optional eagleai for networking topology/NetworkARG; optional csswiki for Azure DevOps wiki/search catalog refresh."
---

# Kusto Query Skill — Azure Infrastructure Investigation

> **Investigation loop**: Every case follows the state machine in [`references/_meta/investigation-loop.md`](references/_meta/investigation-loop.md):
> **S0 IDENTIFY** (sub/VM/disk/SA + time) → **S1 ROUTE** (Quick Dispatch table below; full 346-row table in [`references/_meta/scenario-routing.md`](references/_meta/scenario-routing.md)) → **S2 FIND-AND-RUN** (lookup order: catalogs → playbook → IG → schema explore) → **S3 INTERPRET** (apply [`result-interpretation.md`](references/_meta/result-interpretation.md)) → **S4** CONCLUDE or BRANCH → **S5** EXPAND if dry → **S6 REPORT**.
> **Terminology note**: **IG** means **Investigation Guide** under `references/dashboards/asi/pages/*/investigation-guide/` — i.e., KQL chapters reverse-engineered from ASI dashboard pages and curated for investigation.
> **Scope policy**: reverse-engineering scope is **ASI only**. For Jarvis/Geneva dashboard data, use the `dgrep` skill directly instead of adding new `dashboards/jarvis/` reverse-engineered content.
> **Execution policy**: default to **Kusto first** for all investigations. If required telemetry is unavailable in Kusto (or Kusto signal is insufficient for the asked symptom) and the scenario is Jarvis/Geneva-backed, switch to the `dgrep` skill as the fallback path.
> Always honor the guardrails in [`operational-discipline.md`](references/_meta/operational-discipline.md): time + identity + `| take 1000`; ≤30 KQL / case; stop-and-report on JIT/PG walls or consecutive errors.
> **Speed**: when S2 needs ≥3 *independent* queries (same window, different tables/clusters), run them in parallel — either fan out multiple `kusto` / `azuremcp` KQL calls in **one** assistant turn, or use `python scripts/kusto_runner.py --batch <file.json> --max-workers 5 --server-timeout 60`. See [Parallel Execution](references/_meta/operational-discipline.md#parallel-execution--eliminate-the-10-minutes-no-results-problem) for the decision rule. Serialize only when query N depends on query N-1's output.
> **S6 output format**: the investigation's default deliverable is the shared **complete-analysis format** ([`../_shared/output/complete-analysis-format.md`](../_shared/output/complete-analysis-format.md)) — 问题描述 / 时间 / 环境(含 Resource URI)/ 已完成诊断分析(每步 = 分析一句 + `[kusto]` 全限定 KQL + 结果 + 解读 + 因此/导向)/ 后续计划 — **not** a terse summary. Render the Evidence-Ledger rows inline; see [`investigation-loop.md` § S6](references/_meta/investigation-loop.md#s6--report).

## Knowledge Sources

> **`references/` layout** (3-tier, see [`references/README.md`](references/README.md)):
> - `_meta/` — universal queries, conventions, KQL syntax, authoring workflow
> - `playbooks/` — 24 scenario-routing playbooks (A–L × {core, deep})
> - `catalogs/` — 15 KQL catalogs organized by investigation area (azurecm, azcore, vmainsight, crp, disks, networking, storage-account, windows-events-reference, pcie-failure-queries, ...)
> - `dashboards/` — reverse-engineered KQL from internal ASI dashboards (active scope)

| File | Purpose |
|------|---------|
| `references/_meta/_shared-vm-identification.md` | **Universal queries** — the 8-10 KQL queries every playbook needs at Step 0/1/2 (VM↔Node, container/node health, VMA RCA, signature→KB). Canonical source of truth. |
| `references/_meta/conventions.md` | Variable placeholder convention, **Query Lookup Order (catalogs → playbook → IG → schema explore)**, ADX deep-link opening pattern, cataloging rules for new queries, catalog maintenance |
| `references/_meta/investigation-loop.md` | **State machine for the natural-language → KQL → interpret → next-query → RCA loop** (S0 IDENTIFY → S1 ROUTE → S2 FIND-AND-RUN → S3 INTERPRET → S4 CONCLUDE/BRANCH → S5 EXPAND → S6 REPORT). Stop conditions, branching rules, flowchart. Read this once before starting any investigation. |
| `references/_meta/result-interpretation.md` | **Pivot-query result interpretation tables** — for 15 high-value tables (VMA, LogContainerHealthSnapshot, ServiceHealingTriggerEtwTable, CrpOperationQoSEtwTable, KronoxVmOperationEvent, AirManagedEvents, ApiQosEvent_nonGet, DiskManagerApiQoSEvent, WireserverHeartbeatEtwTable, AccountPerfPercentiles5M, ImdsApiRequests, ARMProd HttpIncomingRequests, etc.), what `rowCount==0` means, per-value branch targets. |
| `references/_meta/schema-exploration-workflow.md` | **Tier-2 fallback** when no curated KQL exists — domain→cluster mapping, ADX `.show` cheat sheet, 3-step sample→guess→validate flow. |
| `references/_meta/operational-discipline.md` | **Cluster permission matrix** (default / JIT / PG-only), **query guardrails** (time + identity + take 1000), **per-case budget** (30 KQL / 5000 rows / 4 clusters), **error classification** (Sem0001/0011/401/403/throttle/timeout) with recovery actions, **MCP vs Python** decision rule, stop-and-report contract. |
| `references/playbooks/playbook-A-restarts-core.md` | **Playbook A (core)** — VM Restart / Downtime RCA 8-step decision flow with RCALevel1 routing table |
| `references/playbooks/playbook-A-restarts-deep.md` | **Playbook A (deep)** — 17 restart-related TSGs organized as §SW (5) + §HW (7) + §STG (4) + §MAINT (1) + §GUEST pointer |
| `references/playbooks/playbook-C-performance-core.md` | **Playbook C (core)** — VM Performance / ASAP / Throttling 9-step decision flow with symptom-bucket routing (DiskLatency / CPU / CPU-Guest / Memory / Hang / GPU / Network / IntermittentBlip / PostMaintBlip / MissingMetrics / ASAP / Throttling / Tool-PerfDiag / Misc) |
| `references/playbooks/playbook-C-performance-deep.md` | **Playbook C (deep)** — 42 TSGs across §STG-Perf (15), §NET-Perf (3), §CPU-Perf (4), §MEM-Perf (6), §HANG (1), §GPU-Perf (6), §ASAP (3 custom), §Throttling (4 custom), §LM/MAINT/TOOL/MISC/OS-Perf-Linux (10), §GUEST pointer. |
| `references/playbooks/playbook-B-cant-start-stop-core.md` | **Playbook B (core)** — Cant Start-Stop / Allocation (Create / Start / Stop / Restart / Redeploy / Delete / Resize / Update) 8-step router mirroring the Cant-Start-Stop-Home decision tree (ARM ingress → CRP op → error-code routing → container/node → disk/NIC → guest OS → recurrence) |
| `references/playbooks/playbook-B-cant-start-stop-deep.md` | **Playbook B (deep)** — Cant Start-Stop TSG bodies grouped by CRP/ARM error code (§OP-* covering Allocation/FabricTimeout/StartTimeout/OSPTO/NetworkInternalError/DiskMgmt/DiskLease/Throttle/Lock/Policy/RBAC/BadRequest/Retry/FabricInternalPowerOff) + per-operation index (§OP-Delete / Resize / Redeploy / Hibernate). |
| `references/playbooks/playbook-D-maintenance-core.md` | **Playbook D (core)** — Planned Maintenance + Live Migration + Dedicated Host 8-step router (VM/Host identify → bucket classify → AzPE / Air / NodeServiceOp / LM session / ADH placement → cross-link to A/B/D) |
| `references/playbooks/playbook-D-maintenance-deep.md` | **Playbook D (deep)** — 15 PM TSGs (§PM-1..15) + 9 ADH TSGs (§ADH-1..9) + LM common (§LM-Common) + 11 PM How-Tos (§HOW-1..11) + 4 ADH How-Tos (§ADH-HOW-1..4) + 5 Workflows (§WF-1..5). |
| `references/playbooks/playbook-E-vmss-core.md` | **Playbook E (core)** — VMSS (Uniform + Flex) 7-step router (orchestration mode + SPG identify → symptom-bucket dispatch → CRP/NRP/NRP-StandbyPool/Fleet/AutoAZ KQL → specialized RP routing → ownership handoff to AKS/SF/AzDO/ASMS/CMG/AppInsights) |
| `references/playbooks/playbook-E-vmss-deep.md` | **Playbook E (deep)** — 60+ VMSS TSGs (Uniform + Flex) with full KQL: §VMSS-Shape / Alloc / Scale / StandbyPool / Spot / FailedState / OrchSvc / Move / Delete / CantCreate / Upgrade / OSPTO / CMG / Workflow / CantRDPSSH / Ext / Autoscale / InstanceProtection / Flex / HowTo. Anchor prefix `VMSS-*`. |
| `references/playbooks/playbook-F-disk-core.md` | **Playbook F (core)** — Disk Lifecycle 8-step router (identify disk + verify state → symptom-bucket dispatch by error code → DiskRP/CRP/ARM KQL → specialized RP routing → ownership handoff to EEEAzureRT/ARM Team/WACAP/Disk SME via Ava). Routes to `MD-*` anchors in deep file. |
| `references/playbooks/playbook-F-disk-deep.md` | **Playbook F (deep)** — 34 Disk Management TSGs + 4 Workflows: §MD-Delete (incl. Soft-Delete bulk-by-RG with 60+ region mapping) + §MD-Snapshot / Resize (incl. LiveResizeStorageClientFailure Pattern A/B) / Convert / Encryption / Visibility / Event (stornvme Event 129 ASAP) / Colocation-SLZ (⚠ silent feature, 6 KQL) / UltraSSD / Billing (PAv2 + XStore hourly) / Platform-502 / Shared / Workflow-Router / Other. Anchor prefix `MD-*`. |
| `references/playbooks/playbook-G-deployment-core.md` | **Playbook G (core)** — Deployment 7-step router (identify deploy-time vs runtime via `labels.IsNew` → symptom-bucket dispatch → CRP/ARM/PirCas/aznwsdn/Allocator KQL → specialized RP routing → ownership handoff to CCE/WACAP/ASMS/Cloudnet/Policy/ACC). Routes to `DEPLOY-*` anchors in deep file. |
| `references/playbooks/playbook-G-deployment-deep.md` | **Playbook G (deep)** — 47 sections / 39 KQL for Deployment: §CRP-Preempted/Restarted/RBT/Throttle/SubThrottle + §CAPA-Delay/Incorrect + §Alloc-* + §PPG-* + §CR-CUD (ODCR) + §Gen2-* + §Conf-* + §Hibernate + §Image-* (PlatformImage / SIG / SIGCrossTenant / VMSSACG / Marketplace / Publisher / VHD / AIB) + §ACG + §AIB + §Container + §Disk + §SA + §Quota + §Region + §Policy + §Provision-OSPTO. Anchor prefix `DEPLOY-*`. |
| `references/playbooks/playbook-H-agent-extension-core.md` | **Playbook H (core)** — Agent + Extension + Encryption (ADE/SSE+CMK/EAH) 8-step router (identify GA vs Extension vs Encryption → symptom-bucket dispatch → azcore Fa GuestAgentExtensionEvents + CRP/ARM + rsm_Prod RSM rollout + ASC h3s3mb template → ownership handoff to EEE/PG/Windows-Domain-crypto/AzNet/AKS/Azure-Policy). Routes to `AGEX-* / ADE-* / SSE-*` anchors in deep file. |
| `references/playbooks/playbook-I-identity-console-core.md` | **Playbook I (core)** — Identity & Console (IMDS + MSI + SAC) merged 8-step router (identify IMDS vs MSI vs SAC → symptom-bucket dispatch → ARMProd HttpIncoming/Outgoing + AzLinux SerialConsole.PortalActivity + azcore Fa WireserverHeartbeatEtwTable + Xstore XStoreAccountProperties + PolicyServiceDebug → ownership handoff to AzureHost-VmService/AzureRT-Extensions/Windows-EE-GES/Customer-Policy-owner). Routes to `IMDS-* / MSI-* / SAC-*` anchors in deep file. |
| `references/playbooks/playbook-J-storage-account-core.md` | **Playbook J (core)** — Storage Account (Consolidated) (5 wiki areas merged: Storage Account Mgmt + Storage Billing + Recover Storage Objects + Unable to Delete Storage + Azure Elastic SAN) 10-step router (identify Mgmt vs CMK vs Recovery vs Delete vs Billing vs ESAN → symptom-bucket dispatch → SA Util foundation lookups → delegate heavily to storage-account-queries.md for KQL bodies). Routes to `SA-Mgmt-* / SA-CMK-* / SA-Recovery-* / SA-Delete-* / SA-Billing-* / SA-Util-* / ESAN-*` anchors in deep file. |
| `references/playbooks/playbook-J-storage-account-deep.md` | **Playbook J (deep)** — 50 sections / 10 KQL for Storage Account control plane: §SA-Mgmt (10 incl. NetworkSourceDeleted, 502-BadGateway sub-not-registered, NotVisible ARM Sync, Classic→ARM stuck, DoubleEncryption create-time-only) + §SA-CMK (9 incl. UAMI deleted, KV-MovedTenant, CrossTenant-DataPlane federated MI, AADSTS700016, ConfigSwitching deep-dive) + §SA-Recovery (7 incl. main scoping TSG + AD-CSSStgApprovers JIT) + §SA-Delete (7 incl. AccountIsLocked / AccountProtectedFromDeletion / Blob VHD-only / Classic→ARM) + §SA-Billing + §SA-Util + §ESAN. Anchor prefix `SA-Mgmt-* / SA-CMK-* / SA-Recovery-* / SA-Delete-* / SA-Billing-* / SA-Util-* / ESAN-*`. |
| `references/playbooks/playbook-I-identity-console-deep.md` | **Playbook I (deep)** — 43 sections / 31 KQL for IMDS + MSI + SAC: §IMDS-Reach (3 incl. Win2012-ESU) + §IMDS-Token (4 incl. 4xx/5xx deep-dive) + §IMDS-GuestProxyAgent (5-step) + §IMDS-GPA-Extension-Telemetry (4 KQL) + §IMDS-Util + §MSI (5 incl. azmsicl 3-KQL chain, PerfInsights UAMI overwrite bug) + §SAC-Connect (6 HTTP codes) + §SAC-Host-RdnpcStuck + §SAC-Guest-ServiceTimeout (v5 Ice Lake) + §SAC-Browser (2) + §SAC-Win (5 incl. SacsvrBroken 11 SCM codes) + §SAC-Linux + §SAC-HowTo (7). Heavy use of `azmsicl.azmsidb` (CoreIdentity JIT) + `AzLinux.SerialConsole` + azcore IMDS functions. Anchor prefix `IMDS-* / MSI-* / SAC-*`. |
| `references/playbooks/playbook-K-storage-perf-core.md` | **Playbook K (core)** — Storage Performance / Throttling — INLINE style (small but high-value RCAs warrant verbatim bodies). 9-step router (identify ARM-side XStore throttling vs SA scalability/throttling vs XArgus account latency vs tenant/stamp health vs Page Blob deep dive vs **Azure Files backend XStore-side perf** → symptom-bucket dispatch → cross-link C § THR-Perf-3/4 for tactical retry + J § SA-Mgmt-IncreaseLimits for quota + L TBD for client-side Azure Files Guest-OS perf). Routes to `SA-Perf-* / SAF-* / LinuxOSDisk-Full` anchors in deep file. |
| `references/playbooks/playbook-K-storage-perf-deep.md` | **Playbook K (deep)** — 16 sections / 4 KQL for Storage Performance + Throttling + XArgus latency: §SA-Perf (6: ARM-XStore-Throttle ⚠ CSS ARM-team-collab-FIRST rule, CheckActivity 4-tool matrix ASC/XPortal/AzMonitor/DiagLogs, SAThrottle 20k/50k IOPS, XArgus-Account `AccountPerfPercentiles5M` via XStorePartnersKusto JIT, TenantHealth `TenantPerfPercentiles5M` + Iridias LSI, PartitionDowntime Jarvis MDM) + §SA-Perf-PageBlob (XBlobFE GetPage/PutPage) + §SA-Perf-AzureFiles-Backend (XFileFE per-share 1000 IOPS / 60 MB/s, Cross-Zone Traffic >10ms gap, Zonal Placement preview) + §SA-Perf-AzureFiles-HeavyMetadata (SuccessWithMetadataWarning/Throttling Nov 2024) + §LinuxOSDisk-Full. Anchor prefix `SA-Perf-* / SAF-* / LinuxOSDisk-Full`. |
| `references/playbooks/playbook-H-agent-extension-deep.md` | **Playbook H (deep)** — 44 sections / 10 KQL for Agent + Extension + Encryption: §AGEX-GA (Win 5 + Linux 3 + Logs ETL fillup) + §AGEX-Ext (generic 4 incl. 90minTimeout/AzurePolicy/AutoUpgrade / CSE 4 incl. ExitCode 50/124 AKS / RunCommand 2 / VMAccess 9-error / DomainJoin / PerfDiag-FIPS) + §ADE (10 incl. KV-moved-tenants, FAD+ADE conflict, v2.2.0.37 regression, RHEL9 BootMount, Recovery-Unlock) + §ADE-Migration + §SSE+CMK (5 incl. PV2-Ultra-UserMI). Anchor prefix `AGEX-* / ADE-* / SSE-*`. Foundation table `azcore.Fa.GuestAgentExtensionEvents`. |
| `references/catalogs/azurecm-queries.md` | AzureCM: container/node lifecycle, faults, recovery, SH, LM, identity change history, allocatable VM count / capacity (Allocator vs AzureCM authority) |
| `references/catalogs/vmainsight-queries.md` | VMInsight: VMA RCA, Air events, host updates, Vmadiag heartbeat/VFP diagnosis |
| `references/catalogs/disks-queries.md` | Disks RP foundation: managed disk lifecycle, existence check, ContextActivity verbose trace (lease/footer/UDE signatures), BackgroundTask (cross-region copy), DiskRPDiskEncryptionSetLifecycleEvent, all-region MonitoringApplication mapping. Delegated to by Playbook F. |
| `references/catalogs/crp-queries.md` | CRP operations, allocation, ARM API, azcrp QoS, AZ zone mapping; VM Op Failure investigation flow + **CRP Error-Code Routing Reference** (per-errorCode → TSG mapping table) |
| `references/catalogs/hardware-queries.md` | AzureDCM + Sparkle: hardware inventory, WHEA/SEL |
| `references/catalogs/operations-queries.md` | Hawkeye, ICM, Watson, AzPE, Resource Health, ASW case analytics |
| `references/catalogs/azcore-queries.md` | AzCore/RDOS: HyperV, VM health, node service, OS logs, NVMe errors |
| `references/catalogs/vm-properties-queries.md` | EEE-style VM properties & disk surface queries (cross-cluster) |
| `references/catalogs/pcie-failure-queries.md` | PCIe failure investigation: Kusto queries (Sparkle SEL, Partner_RAS, topology), RawHex decode rules, regex classification, 3 known issues; **C2789 7U Server BDF mapping (Table 11, 115 rows)**, quick lookup tables, scenario samples + action plans, HW replacement record check |
| `references/catalogs/networking-queries.md` | Azure Networking: NRP, VPN, ExR, AppGW, vWAN, SLB, CDN, DDoS |
| `references/eagleai-networking.md` | **EagleAI networking path**: when/how to use `eagleai` for EagleEye topology, end-to-end connectivity, NSG/Private Link/ExpressRoute/AFD diagnosis, and NetworkARG (`eearg.westus2` / `AzureResourceGraph`) |
| `references/catalog-AzureNetworking.md` | CSS AzureNetworking catalog: ARM/networking clusters, tables, NetworkARG templates, and service-specific KQL for NRP, Hybridnetworking, SLB, CDN/AFD, DDoS, vWAN/ExpressRoute |
| `references/catalogs/storage-account-queries.md` | Storage Account: XStore properties, XArgus performance, billing, recovery, failover, throttling, Azure Files, Elastic SAN |
| `references/catalogs/asap-storage-queries.md` | ASAP / SmartNIC / Boost-for-Storage NVMe controller reset probe (storageclient.Fa) — AMD v6/v7 SKU "guest hang" that platform-side tables miss; canonical probe + PF/Nvme/Kms EventId tables + escalation to EEE Storage |
| `references/kql-language.md` | Expanded KQL syntax, query discipline, schema-guard, SEM0100/error recovery, copied from CSS and adapted to the fully-qualified-table rule |
| `references/_meta/kql-language.md` | KQL operators, patterns, best practices, common errors |
| `references/dashboards/INDEX.md` | **Cross-page directory** of all reverse-engineered dashboard pages (per-portal: page slug · service · panel/query counts · **investigation-guide link** · top clusters). Auto-generated. |
| `references/dashboards/panel-index.md` | **Flat panel listing — grep this** when a TSG mentions an ASI panel name. 2300+ rows: panel-path · query-name · cluster.database · **guide link** · page link. |
| `references/dashboards/by-scenario.md` | **Hand-curated map** of which dashboard pages to open for each investigation scenario (VM lifecycle · host node · EEE · CRP · disk · networking · etc.). Page links point at the Investigation Guide. |
| `references/dashboards/<portal>/pages/<slug>/investigation-guide/` | **Preferred KQL entry point** — curated, symptom-keyed chapters (`01-...md`, `02-...md`, ...) with KQL bodies inlined, plus a `README.md` chapter index. Available on 162/162 ASI pages. |
| `references/dashboards/<portal>/pages/<slug>/library.md` | Per-page panel→KQL metadata index (panel paths, query names, cluster.db — no KQL bodies). Fallback when no investigation guide exists. |
| `references/dashboards/<portal>/pages/<slug>/library.json` | Per-page machine-readable form. `panels[<path>].queries[].kustoQuery` holds the raw KQL text (used by `replay.py` and by humans only when the guide is missing). |
| `references/dashboards/<portal>/pages/<slug>/replay.py` | Optional script to run a panel's KQL with placement context (vmid/nodeid/containerid/time range). |
| `scripts/kusto_runner.py` | General-purpose single-query runner (--cluster --database --query) **AND parallel batch runner (--batch <file.json> --max-workers 5 --server-timeout 60)**. Use `--batch` whenever you have ≥3 independent KQL queries to fan out — one auth pool, true thread-pool concurrency, per-query timeout, isolated failures. See *Parallel Execution* in [`_meta/operational-discipline.md`](references/_meta/operational-discipline.md#parallel-execution--eliminate-the-10-minutes-no-results-problem). Also used as the execution engine for dashboard-replay scripts under `references/dashboards/<portal>/pages/<page>/replay.py`. |
| `scripts/kusto_vm_investigate.py` | Automated 9-step VM investigation (--subscription-id --vm-name) |
| `scripts/kusto_disk_investigate.py` | Automated 4-step disk investigation (--subscription-id --disk-name) |
| `scripts/kusto_catalog_builder.py` | Rebuild `references/catalog-<wiki-project>.md` from Azure DevOps wiki (`csswiki` is the interactive wiki/search MCP); target script is equivalent to the CSS source builder |

> **Dashboards reference**: Reverse-engineered KQL libraries behind internal dashboards live at [`references/dashboards/`](references/dashboards/). Active reverse-engineering scope is **ASI** (162 pages, 2300+ panel KQL queries). For Jarvis/Geneva dashboard data, use the `dgrep` skill. **Two main uses**:
>
> 1. **TSG says "look at ASI panel X" / "check ASI for symptom Y"** → grep [`references/dashboards/panel-index.md`](references/dashboards/panel-index.md) for the panel name (or grep the Investigation Guides directly for a symptom: `Select-String "<keyword>" references/dashboards/asi/pages/*/investigation-guide/*.md`). The matched row's `Guide` column links to the page's `investigation-guide/README.md` — open the chapter that matches your symptom, the KQL body is inlined; run it via the Azure MCP `kusto` tool. No need to open the portal.
> 2. **Looking for KQL that's not in `catalogs/`** → consult [`references/dashboards/by-scenario.md`](references/dashboards/by-scenario.md) to pick the right page(s) for your scenario (links jump straight to each page's Investigation Guide). Read the KQL inline from the page's `investigation-guide/`; run it via the Azure MCP `kusto` tool. **Dashboard KQL stays in `dashboards/`** — it is page-scoped and not curated for cross-case reuse; do not copy it into `catalogs/`.
>
> Index regeneration: `python _work/_scratch/build-dashboards-index.py` rebuilds `INDEX.md` + `panel-index.md` from the per-page `library.json` files. `by-scenario.md` is hand-maintained. The raw API capture (`raw/`) is gitignored locally.

---

## Scenario Routing — Quick Dispatch

Match user intent to the right **Playbook** (A–L), then open that playbook's **core** file — it is the 2nd-tier router for its area.

| User intent (any language) | Playbook | Entry file |
|----------------------------|----------|------------|
| VM restart / downtime / RDP-SSH failed / unavailable (VM 重启 / 掉线 / 不可用) | **A** | `references/playbooks/playbook-A-restarts-core.md` |
| VM performance / ASAP / throttling / latency / slow (VM 性能 / 限流) | **C** | `references/playbooks/playbook-C-performance-core.md` |
| VM start/stop/restart/redeploy/delete/resize/update failed (启停失败 / Allocation) | **B** | `references/playbooks/playbook-B-cant-start-stop-core.md` |
| VM/VMSS create / deployment failed / SKU / Image / Quota / AIB / ACG (部署失败 / 创建失败) | **G** | `references/playbooks/playbook-G-deployment-core.md` |
| Planned maintenance / Live Migration / Dedicated Host / Workflow / Decom (计划维护 / LM) | **D** | `references/playbooks/playbook-D-maintenance-core.md` |
| VMSS (Uniform / Flex / Standby / Auto AZ / Scale / Upgrade) | **E** | `references/playbooks/playbook-E-vmss-core.md` |
| Managed disk lifecycle: delete / resize / snapshot / convert / encryption / SLZ / Event 129 (磁盘 lifecycle) | **F** | `references/playbooks/playbook-F-disk-core.md` |
| Guest agent / Extension / ADE / SSE+CMK / Encryption at Host (GA / Extension / 加密) | **H** | `references/playbooks/playbook-H-agent-extension-core.md` |
| IMDS / MSI / Serial Console / GuestProxyAgent (身份 / 控制台) | **I** | `references/playbooks/playbook-I-identity-console-core.md` |
| Storage Account control plane / CMK / Recovery / Delete / Billing / Elastic SAN (存储账户) | **J** | `references/playbooks/playbook-J-storage-account-core.md` |
| Storage performance / XStore 503 / SA throttling / XArgus latency / Azure Files backend perf | **K** | `references/playbooks/playbook-K-storage-perf-core.md` |
| Azure Files / Azure File Sync (AFS) / file share / SMB / NFS / 文件共享 / AFS 同步 | **L** | `references/playbooks/playbook-L-azure-files-core.md` |
| Network topology / connectivity diagnosis / VM-to-PE / VM-to-VM / Private Link / NSG / ExpressRoute / AFD / NetworkARG | EagleAI + Networking catalog | `references/eagleai-networking.md` + `references/catalog-AzureNetworking.md` |
| Ad-hoc / custom KQL / schema exploration | _meta | `references/_meta/kql-language.md` + `references/_meta/schema-exploration-workflow.md` |

> **Quick Dispatch covers ~85% of cases by intent class.** For the **full 346-row routing table** (with exact cluster.database + first table for every documented scenario, including cross-playbook edge cases and rarely-seen wordings), open [`references/_meta/scenario-routing.md`](references/_meta/scenario-routing.md). Always consult it when the user's wording is ambiguous, mentions a specific error code, or spans multiple playbooks.


### Disambiguation Rules (Important)

1. **Always identify VM identity first** via `LogContainerSnapshot` to get `containerId`, `nodeId`, `tenantName`.
2. **Do not treat same-node events as same-VM events** unless `ContainerId` or `RoleInstanceName` matches target VM.
3. If the user says "node fault" (节点异常) but asks about impact to a single VM, query node-level and VM-level tables in parallel, then intersect by time + VM identity.
4. If the user asks "was this customer-perceptible" (是否客户可感知), prioritize downtime/health-state tables before deep RCA tables.
5. If the user gives only **resourceId**, first parse `{SubscriptionId}/{ResourceGroupName}/{VMName}` then map to internal IDs.
6. **Control-plane vs data-plane determination**: If VM heartbeat/WireServer is healthy (no faultInfo in `LogContainerHealthSnapshot`, no RCA events in VMA) but SSH/Ping/RDP is down, prioritize VFP/SDN data-plane fault — route to `vmainsight.Vmadiag` (`Atlas_VmStateTransitionEvent`, `vfp_restore_fails`) rather than continuing to dig into AzureCM.
7. **Disk fault ambiguity**: A "disk-related" issue must first be classified as either an I/O-layer fault (XStore/IaaSxStoreOutage — evidence in AzureCM) or a resource-layer issue (attach/detach/disk not found — evidence in disks.Disks); the two use entirely different tables.
8. **Storage account query routing**: When the user asks about a "storage account" (存储账户), determine the sub-scenario first: properties/config → `azcore.Xstore`; performance/latency → `xargus.Production`; billing → `xstore.xdataanalytics`; deletion/recovery → `armprodgbl.ARMProd`; throttling → `armprodgbl.ARMProd`; stamp/tenant → `xstore.xstore`. Do not default to `disks.Disks` for storage account queries — that cluster is for managed disk resources only.
9. **VM perf anomaly — MUST check `AirDiskIOBlipEvents` before concluding "platform clean"**: When a customer reports CPU spike, freeze, slow IO, or IO hang, do NOT conclude the platform is clean based only on negative `KronoxVmOperationEvent` / `TMMgmtNodeFaultEtwTable` / `LogContainerHealthSnapshot` / `VMA` / `AirManagedEvents` results. Those tables only catch managed ops, node hardware faults, threshold-breaching availability events, and planned maintenance — they MISS host↔storage CloudNet brownouts and disk IO blips entirely. Always run `cluster('vmainsight').database('Air').AirDiskIOBlipEvents` filtered by NodeId (and optionally VirtualMachineUniqueId) — `RCALevel1 == "CloudNet"` → EEE Cloudnet, `RCALevel1 == "Xstore"` → EEE Storage. See `references/catalogs/vmainsight-queries.md` § AirDiskIOBlipEvents.
10. **AMD `*_v6` / `*_v7` SKU "guest hang" — MUST run ASAP probe**: On Boost-for-Storage SKUs that use SmartNIC NVMe offload (confirmed on `Standard_E96as_v7`, AMD v6/v7 family), a host-side ASAP NVMe Controller Reset produces the EXACT same "guest hang" signature in Geneva (CPU/IO drop to zero). Standard platform queries (Service Healing, NodeFault, VMA, Kronox, LogContainerHealthSnapshot) MISS this entirely because container/node still report Healthy. Always run the canonical ASAP probe on `storageclient.eastus.Fa.AsapNvmeEtwTraceLogEventTable` before concluding "guest-side issue". In-guest tells: Windows `stornvme` controller reset, Linux `nvme nvmeX: I/O timeout`. EEE indicator: "ASAP Controller Reset, Message: VfId N". See `references/catalogs/asap-storage-queries.md`.
11. **AzCore region routing**: `azcore.centralus.kusto.windows.net` only holds counter / HyperV data for US regions. For Korea Central / other Asia / EU regions, use the regional AzCore shard (Mooncake `Rdosmc`, FairFax `Rdosff`, others as applicable). **Do not conclude "no host CPU data" from one cluster returning 0 rows** — the cluster is wrong. Fall back to Geneva VM Dashboard (vmdash) for guest counters.

> **Cross-playbook routing** (VMSS / Disk / Deployment / Agent / Identity / Storage — which playbook owns what): the Quick Dispatch table above maps intent → Playbook; the full per-row mapping with cluster + first table is in [`references/_meta/scenario-routing.md`](references/_meta/scenario-routing.md). Routing logic was previously duplicated in 6 disambiguation rules and has been removed in favor of that single source of truth.

### Networking-specialized path — `eagleai` (optional MCP)

Use `eagleai` only for Azure Networking topology and end-to-end connectivity. The default raw Kusto path remains `kusto` / `azuremcp` for compute, storage, host, CRP, ARM, and ordinary catalog queries.

Read [`references/eagleai-networking.md`](references/eagleai-networking.md) first when the symptom is VM→Private Endpoint, VM→VM, ExpressRoute, Azure Front Door, NSG analysis, Private Link, VPN/vWAN/AppGW/SLB, or NetworkARG topology/property lookup.

`eagleai` tools:

| Tool | Signature | Use |
|---|---|---|
| `EagleAI` | `EagleAI(user_query: str)` | General networking entry point when the right path is unclear. |
| `execute_kusto_query` | `execute_kusto_query(query: str, cluster: str, database: str)` | Raw KQL against a known cluster/database; for NetworkARG use `cluster=eearg.westus2`, `database=AzureResourceGraph`. |
| `DiscoverTopology` | `DiscoverTopology(user_query: str)` | EagleEye topology/connectivity diagnosis for VM↔destination, ExpressRoute, AFD, NSG, Private Link, vWAN/Hub/NVA. |

For `EagleAI` / `DiscoverTopology`, the `user_query` must include resource ARM IDs, an absolute UTC time window, and the symptom. For NetworkARG raw rows, keep KQL fully-qualified, e.g. `cluster('eearg.westus2').database('AzureResourceGraph').Resources | where id =~ '{ResourceArmId}'`.

---

## Workflow

When the user requests a Kusto-based investigation:

### Step 1 — Identify Scenario

1. Match the user's intent against the **Scenario Routing — Quick Dispatch** table above. Pick the matching Playbook letter and open its `core` file — that file is the 2nd-tier router for its area and will hand off to the right `deep` section or catalog.
2. If the wording is ambiguous, mentions a specific error code, spans multiple playbooks, or you need the exact first cluster.database + first table for a less-common scenario → open the full 346-row table at [`references/_meta/scenario-routing.md`](references/_meta/scenario-routing.md).
3. If nothing matches even there, route to `references/_meta/kql-language.md` + `references/_meta/schema-exploration-workflow.md` for ad-hoc KQL.

### Step 2 — Build Query

1. **Check query templates first** — look up the appropriate reference file (from Step 1) for ready-to-use KQL patterns
2. If no template matches, look up table name and key columns in the reference files
3. **MANDATORY — Fully-qualified table reference.** Every query MUST use `cluster('<host>').database('<db>').<Table>` form. Never write bare `<Table>` — even when the cluster/db is "obvious from context". Example:
   - ✅ `cluster('Azurecm').database('AzureCM').LogContainerSnapshot | where ...`
   - ❌ bare table names that omit `cluster('<host>').database('<db>')`
   - This rule applies in chat replies, ADX deep links, reference files, and cataloged queries. It is the single biggest source of "query won't run" friction.
4. Apply patterns from `references/_meta/kql-language.md`:
   - Always filter by `PreciseTimeStamp` first
   - Use `let` blocks for variables and cross-cluster lookups
   - Prefer `has` over `contains` for string searches
   - Put the smaller table on the LEFT side of a `join`
   - For expanded syntax, schema-guard, and error recovery guidance, also read `references/kql-language.md`.

### Step 2.5 — Verify Query Before Sharing (MANDATORY — the SEM0100 gate)

**This is the single behavioral gate that prevents all SEM0100 "phantom table/column" errors.** The rule is *methodological*, not encyclopedic — you cannot memorize every column name, so instead you classify each query by source and verify only when needed.

**3-tier verification flow — classify the query, then act:**

| Query source | Action | Extra cost |
|---|---|---|
| 🟢 **Verbatim from a `catalogs/` or playbook template** | Run directly — trusted | 0 calls |
| 🟢 **Template with only the time window / identity filter changed** | Run directly — column/table names unchanged | 0 calls |
| 🟡 **Template with a table or column name changed, OR fully ad-hoc (from memory / schema exploration / user wording)** | **MUST** run `cluster('<host>').database('<db>').<Table> \| getschema` or `cluster('<host>').database('<db>').<Table> \| take 1` and confirm every projected/filtered column exists **before** the real query | +1 call |

**Never guess a table or column name.** If it is not literally in a template or a `getschema` result you've already seen this session, it is unverified — verify first.

**Efficiency note:** the two 🟢 tiers cover the large majority of queries and add **zero** overhead — do not over-verify template queries. Only the 🟡 tier pays the +1 `getschema` call, and only once per new table.

**Parallel rule:** only fan out queries in parallel when **all** are 🟢 (template-based). If **any** query in the batch is 🟡 (ad-hoc), verify it sequentially first — batch-firing unverified queries triggers the "two consecutive schema errors → stop" rule and kills the investigation.

**Mid-investigation recovery:** if a query fails with `Sem0001` (table) / `Sem0011` (column) / `Failed to resolve ... named 'X'` — do **not** retry unchanged. Run `getschema`, fix the name, re-run. For the bounded blacklist of phantom tables, the 6 high-hallucination tables' correct columns, and the cluster-switch procedure, see **[`references/_meta/operational-discipline.md`](references/_meta/operational-discipline.md#known-schema-pitfalls--the-sem0100-blacklist-single-source-of-truth) § Known Schema Pitfalls** — the single source of truth (do not duplicate it here).

**When opening a query in ADX**, it must already have been verified (executed via MCP or schema-checked).

### Step 3 — Execute

**Default: execute immediately, no confirmation.** Investigation is time-sensitive and results provide context to evaluate the query itself. Display the KQL alongside the results so the user can review.

**Execution tiers — pick the right behavior:**

| Tier | When | Action (single query) | Parallel Behavior (≥2 independent queries) |
|------|------|--------|---|
| 🟢 **Auto-run** | Query comes from a `references/*.md` template AND time window ≤ 7d AND single cluster AND plan has ≤3 queries on ≤1 cluster | Run silently, show KQL + result. **Do NOT ask the user "ok to proceed?" — 🟢 means just go.** Missing inputs (RG name, exact VM name format) should be inferred from context or filled with broad placeholders; only ask if a query literally cannot be constructed | Fan out without asking — MCP same-turn (≤4) or `kusto_runner.py --batch`. Show KQL of each + per-query timing in the summary |
| 🟡 **Run with warning** | Time window > 7d **OR** cross-cluster join **OR** ad-hoc query constructed from schema (not template) **OR** plan spans ≥2 clusters AND ≥4 queries (multi-cluster fan-out) | One-line warning before run: `Running (large window / cross-cluster / N queries across M clusters) — abort with Ctrl+C if wrong`, then execute | One-line batch overview first (`N queries, M clusters, window=Xd, max-workers=K`), then fan out. Same tier criteria apply per query |
| 🛑 **Show first, wait for "go"** | User question has 2+ valid interpretations **OR** full-table scan (no time filter) **OR** time window > 30d **OR** result set likely > 10k rows **OR** batch size > 10 queries | Show KQL + brief rationale, ask `跑吗? (y/skip)` once. After explicit go, never re-ask in same session for similar queries | List the full batch spec (labels + clusters + KQL bodies, or the JSON if writing one) and ask once `跑这 N 条吗? (y/skip)`. Approval applies to the whole batch, not per-query |
| 🚫 **Always wait** | Write operations (`icm` comment, `csswiki` / Azure DevOps update, wiki edit) **OR** user explicitly said "先看 query / show me first / 别直接跑 / open in ADX" | Show only, do not execute | Show spec only. **Never bypass 🚫 by claiming "it's just a batch"** — opt-out applies to single AND batch execution |

**User opt-out keywords** (force 🚫 mode for the rest of session):
- EN: "show me first", "don't run", "just show the query", "open in ADX", "preview only"
- CN: "先看 query", "别直接跑", "先告诉我", "只要 query"

**Once user says these, stay in show-only mode until they say "now run it / 跑吧 / 执行".**

**MCP-first — use the `kusto` MCP or Azure MCP's `kusto` tool:**

For raw KQL, use `kusto` when available, or call the `azuremcp` `kusto` tool (CLI: `npx -y @azure/mcp@latest kusto query`) with these
**required parameters** — note the internal clusters are NOT ARM-registered, so you must use
`cluster-uri` (the full URL), not `cluster` (the ARM name):

| Parameter | Value | Notes |
|-----------|-------|-------|
| `cluster-uri` | `https://{host}.kusto.windows.net` | **Always use `cluster-uri`, never `cluster`** — internal clusters aren't in any subscription |
| `database` | The database name | e.g., `AzureCM`, `Disks`, `vmadb` |
| `query` | The KQL query | |
| `tenant` | `72f988bf-86f1-41af-91ab-2d7cd011db47` | Microsoft Corp tenant — required for auth |
| `auth-method` | `Credential` | Uses `az login` credential |

Display format:
```
**Query** (`{cluster}/{database}`):
\```kusto
{KQL}
\```
**Results**: {table or summary}
```

> Query format rule (fully-qualified `cluster('...').database('...').Table`) — see Step 2 rule 3. Applies to chat, ADX deep links, reference files, and cross-cluster joins.
> Networking topology exception: use `eagleai` per [`references/eagleai-networking.md`](references/eagleai-networking.md); raw NetworkARG KQL still follows the same fully-qualified table rule.

**Python fallback** (when MCP is unavailable or for batch/automation):
```bash
# Single ad-hoc query
python <skill_path>/scripts/kusto_runner.py \
    --cluster <host> --database <db> --query "<KQL>" --format table|json|csv|kv

# VM investigation (9-step automated)
python <skill_path>/scripts/kusto_vm_investigate.py \
    --subscription-id <id> --vm-name <name> --start-date YYYY-MM-DD --end-date YYYY-MM-DD

# Disk investigation (4-step automated)
python <skill_path>/scripts/kusto_disk_investigate.py \
    --subscription-id <id> --disk-name <name>
```

### Step 4 — Show Query / Open in ADX

If the user explicitly asks for the raw query ("show me the query", "open in ADX"), see [`references/_meta/conventions.md`](references/_meta/conventions.md#opening-queries-in-azure-data-explorer-deep-link) § Opening Queries in Azure Data Explorer. Query format rule (fully-qualified) — see Step 2 rule 3.

### Step 5 — Summarize / RCA

Use the **RCA Report Template** in [`references/_meta/conventions.md`](references/_meta/conventions.md#rca-report-template).

### Step 5.5 — Verification Gate (V2 — Reasoning Chain)

Before a Kusto-derived root cause reaches a customer (RCA / FQR) or an ICM, this is a **closing gate**.

→ **Self-check before send.** Before the Kusto-derived root cause reaches a customer or an ICM,
re-verify each load-bearing fact yourself — re-run the linchpin query against the internal
read-only cluster and diff the claimed value against the actual returned value. This section
declares what this gate covers.

- **Pack (domain semantics):** [`references/verification-pack.md`](references/verification-pack.md) —
  re-run via the `kusto` MCP, the value↔claim binding / falsification / branch-exclusion / time-window
  checklist, and the column semantics (`BootReason`, ServiceHealing/NodeFault) the critic must read.
- **Maker obligation (build it *during* the investigation):** emit an Evidence Ledger row per
  load-bearing claim ([`_shared/verifier/evidence-ledger.md`](../_shared/verifier/evidence-ledger.md))
  — pin the **verbatim KQL + returned value**, an **absolute** time window, and `expected_if_false`.
- **Signature FAIL here:** MISMATCH on a linchpin re-run ⇒ `CONTRADICTED` ⇒ FAIL; the SEM0100 query
  gate carries over as the fabricated-identifier check.
- **Boundary:** re-run only against **internal read-only** clusters via MCP — never the customer's
  subscription. The card is advisory; the human decides to send.

### Step 6 — Catalog New Queries

After executing any query, check whether it contains clusters, databases, or tables not yet documented in the `references/` folder. If so, follow the **Cataloging New Queries** process in [`references/_meta/conventions.md`](references/_meta/conventions.md#cataloging-new-queries).

---

## Variable Convention

See [`references/_meta/conventions.md`](references/_meta/conventions.md#variable-convention) § Variable Convention for all standardized placeholders (`{NodeId}`, `{ContainerId}`, `{VMName}`, etc.) and the Resource ID extraction pattern.

---

## Investigation Flows

Detailed step-by-step query sequences live in the per-scenario playbooks under [`references/playbooks/`](references/playbooks/) (A–L × {core, deep}). Pick the playbook via the **Scenario Routing — Quick Dispatch** table above, then follow its `core` file. The state machine for the natural-language → KQL → interpret → next-query loop is in [`references/_meta/investigation-loop.md`](references/_meta/investigation-loop.md) (S0–S6).

---

## Clusters Quick Reference

| Alias | URI | Database(s) | Purpose |
|-------|-----|-------------|---------|
| AzureCM | `azurecm.kusto.windows.net` | AzureCM | Container/node lifecycle, faults, recovery, SH, LM |
| Azcsupfollower | `Azcsupfollower.kusto.windows.net` | AzureCM | Follower cluster (same data, preferred for CSS) |
| Disks | `disks.kusto.windows.net` | Disks | Managed disk lifecycle, DiskManagerApiQoS |
| VMInsight | `vmainsight.kusto.windows.net` | vmadb, Air, Vmadiag | VMA RCA, Air events, heartbeat/VFP diagnosis |
| moseisley | `moseisley.kusto.windows.net` | vmadb, Air | VMA RCA follower (same data as vmainsight) |
| AzCore | `azcore.centralus.kusto.windows.net` | Fa | RDOS: HyperV, VM health, node service, OS logs, NVMe |
| AzCore Geneva | `azcore.centralus.kusto.windows.net` | acccvmtmgeneva | VM lifecycle Geneva trace (tagId = ContainerId) |
| AzCore SharedWorkspace | `azcore.centralus.kusto.windows.net` | SharedWorkspace | Cross-cluster helper fns (e.g., `GetHyperVVmIdFromContainerId`) |
| AzCore AzureCP | `azcore.centralus.kusto.windows.net` | AzureCP | `MycroftContainerSnapshot` (VmId ↔ ContainerId) |
| AzLifecycle / AZSM | `accp.centralus.kusto.windows.net` | AZSM | AzSM slice state machine, UpdateTenant events, exceptions (root cause for OutOfTimeBudgetException) |
| AzureDCM | `Azuredcm` | AzureDCMDb | Hardware inventory, repair history |
| Sparkle | `sparkle.eastus` | defaultdb | WHEA/SEL hardware errors |
| Hawkeye | `hawkeyedataexplorer.westus2.kusto.windows.net` | HawkeyeLogs | Automated unhealthy node RCA |
| ICM | `icmcluster` | ACM.Publisher, ACM.Backend | Customer notifications |
| Watson | `Azurewatsoncustomer` | AzureWatsonCustomer | Host bugcheck analysis |
| AzPE | `azpe.kusto.windows.net` | azpe | Host update workflow orchestration |
| APlat | `aplat.westcentralus.kusto.windows.net` | APlat | Anvil/Tardigrade service healing |
| Gandalf | `Gandalf` | gandalf | Unallocatable node detection |
| StorageClient | `storageclient.eastus.kusto.windows.net` | AzureCP, Fa | Mycroft snapshots, disk surfaces, ASAP mapping |
| CRP | `crp.kusto.windows.net` | CrpService | CRP VM operations, allocation, container ops |
| ARMProd | `armprod.kusto.windows.net` | ARMProd | ARM API incoming requests, correlation tracing |
| IcMDataWarehouse | `icmcluster` | IcMDataWarehouse | ICM incident details, incident correlation |
| azcrp | `azcrp.kusto.windows.net` | crp_allprod | CRP API QoS (wider retention ~365d) |
| azcsupfollower2 | `azcsupfollower2.centralus.kusto.windows.net` | crp_allprod | CRP API operations (follower) |
| azcrpbifollower | `azcrpbifollower.kusto.windows.net` | bi_allprod | CRP BI: subscription & AZ metadata |
| Azdeployer | `Azdeployer.kusto.windows.net` | AzDeployerKusto | Planned maintenance |
| azureallocator | `azureallocator.westcentralus.kusto.windows.net` | AzureAllocator | VM allocation capacity |
| azsh | `azsh.kusto.windows.net` | azshmds | Resource Health |
| Nrp | `Nrp.kusto.windows.net` | mdsnrp | Network Resource Provider (NRP) operations |
| Hybridnetworking | `Hybridnetworking.kusto.windows.net` | aznwmds | VPN, ExR, AppGW, vWAN, Gateway Manager |
| Armprodgbl | `Armprodgbl.eastus.kusto.windows.net` | ARMProd | ARM global (Unionizer for regional routing) |
| Azslb | `Azslb.kusto.windows.net` | azslbmds | Software Load Balancer |
| Azurecdn | `Azurecdn.kusto.windows.net` | azurecdnmds | Azure Front Door / CDN |
| Aznwddos | `Aznwddos.centralus.kusto.windows.net` | cnsgeneva | DDoS Protection PCAP flow logs |

Auth via Microsoft Corp tenant — see Step 3 MCP params table. **Never** use the customer's tenant ID (global Key Rule #1).

---

## Kusto Query Tips & Best Practices

- **Time range**: Always use the narrowest time range possible. Start with +/- 1 hour around the incident time.
- **Cross-cluster joins**: Put the smaller dataset on the left side of the join.
- **Follower clusters**: Use `Azcsupfollower` instead of `azurecm` for read-heavy queries.
- **arg_max pattern**: Use `summarize arg_max(PreciseTimeStamp, *) by key` to get the latest record per entity.
- **Parameterization**: Always use `let` variables at the top of queries.
- **Case sensitivity**: Use `=~` for case-insensitive comparison. VM names and subscription IDs should use `=~`.
- **Large result sets**: Add `| take 1000` to prevent pulling millions of rows.

> For comprehensive KQL syntax reference, patterns, schema guard, and common errors, see `references/_meta/kql-language.md` and the expanded CSS-derived `references/kql-language.md`.
