# vm-kusto-query / references — Navigation Map

Files here are split into 3 buckets by **role in the skill workflow**, plus the dashboards sub-tree. Use this map to jump straight to the right file.

```
references/
├── _meta/        — universal queries, conventions, KQL syntax, authoring workflow
├── playbooks/    — 24 scenario-routing playbooks (A–L × {core, deep})
├── catalogs/     — 15 KQL catalogs organized by investigation area
└── dashboards/   — reverse-engineered KQL from ASI dashboards
```

---

## I need to do case RCA → [`playbooks/`](playbooks/)

24 files, paired core (router) + deep (TSG bodies):

| Letter | Topic |
|---|---|
| A | Unexpected VM restarts / downtime |
| B | Can't Start/Stop / Allocation / CRP errors |
| C | Performance / ASAP / Throttling |
| D | Planned Maintenance + Live Migration + ADH |
| E | VMSS (Uniform + Flex) |
| F | Disk lifecycle |
| G | Deployment |
| H | Agent + Extension + Encryption (ADE/SSE+CMK/EAH) |
| I | Identity & Console (IMDS + MSI + SAC) |
| J | Storage Account (Mgmt + CMK + Recovery + Delete + Billing + ESAN) |
| K | Storage Performance / Throttling (XStore + Azure Files backend) |
| L | Azure Files + Azure File Sync (AFS) |

Workflow: read `<X>-core.md` first; drop into `<X>-deep.md` only when the core router narrows to a specific section.

---

## I need to find a KQL query → [`catalogs/`](catalogs/)

15 files, organized by **investigation area** (not necessarily 1 file = 1 cluster — many areas span multiple clusters).

### Single-cluster catalogs (file ≈ one cluster.db)

| File | Cluster.db |
|---|---|
| `aplat-queries.md` | aplat.westcentralus / APlat (Kyber VM Availability) |
| `disks-queries.md` | disks.kusto / Disks (managed disk lifecycle) |
| `wdgeventstore-queries.md` | wdgeventstore / HostOSDeploy (host OS build) |

### Primary-cluster catalogs (one main cluster + occasional joins)

| File | Primary cluster | Joined-with |
|---|---|---|
| `azurecm-queries.md` | Azcsupfollower / AzureCM | accp(TIP), APlat, Gandalf(manifest) |
| `azcore-queries.md` | azcore.Fa (RDOS) | azcsupfollower.AzureCM |
| `vmainsight-queries.md` | vmainsight / vmadb, Vmadiag | AzureCM, moseisley |

### Cross-cluster topical catalogs (file = investigation theme, spans many clusters)

| File | Theme | Clusters touched |
|---|---|---|
| `crp-queries.md` | CRP control plane | azcrp, crp, ARMProd, Cirrus |
| `hardware-queries.md` | Host hardware | AzureDCM, Sparkle |
| `networking-queries.md` | Networking | NRP, Aznw, Azslb, AzureDCM, HybridNetworking, netperf (12 clusters) |
| `operations-queries.md` | Operations / Ops data | Hawkeye, ICM, Watson, AzPE, vmainsight |
| `storage-account-queries.md` | Storage Account | XStore, XArgus, XLivesite, ARMProd × N regions, accprod, pav2data, hdmprod |
| `vm-properties-queries.md` | EEE-style VM properties | AzureCM, AzureCP, storageclient.Fa |
| `asap-storage-queries.md` | ASAP / SmartNIC NVMe | storageclient.Fa (sub-area of azcore) |

### Cross-cluster reference dictionaries (lookup tables, not query catalogs per se)

| File | Scope |
|---|---|
| `windows-events-reference.md` | Host Windows EventIds (60+ entries: storage, NTFS, StorPort, Hyper-V, network, VM-impacting). False-positive list + cluster-frequency check pattern. |
| `pcie-failure-queries.md` | PCIe failure investigation (Sparkle SEL, Partner_RAS, topology) + RawHex decode + C2789 7U Server BDF mapping (Table 11, 115 rows) |

ROUTER-style playbooks (B/C/D/etc.) delegate KQL bodies *to* the catalogs above.

---

## I need to write a new playbook / see common variables → [`_meta/`](_meta/)

| File | Purpose |
|---|---|
| `_shared-vm-identification.md` | The 8–10 universal queries every playbook needs at Step 0/1/2 (VM↔Node, container/node health, VMA RCA). Canonical source of truth. |
| `conventions.md` | Variable placeholders (`{VMName}`, `{NodeId}`, …), **Query Lookup Order** (catalogs → playbook → IG → schema explore), ADX deep-link pattern, cataloging rules |
| `investigation-loop.md` | **State machine** for the natural-language → KQL → interpret → next-query → RCA loop (S0–S6). Read once before starting any case. |
| `result-interpretation.md` | **Pivot-query interpretation tables** — 15 high-value tables (VMA, LogContainerHealthSnapshot, CrpOperationQoSEtwTable, AccountPerfPercentiles5M, ImdsApiRequests, …). What `rowCount==0` means, per-value branch targets. |
| `schema-exploration-workflow.md` | **Tier-2 fallback** when no curated KQL exists: domain→cluster mapping, `.show` cheat sheet, 3-step sample→validate flow. |
| `operational-discipline.md` | Cluster **permission matrix** (default / JIT / PG-only), **query guardrails**, **per-case budget**, **error classification** with recovery actions, **MCP vs Python** decision rule. |
| `kql-language.md` | KQL operator quick-reference, common patterns, best practices |

---

## I need to find the KQL behind an ASI panel → [`dashboards/`](dashboards/)

Reverse-engineered KQL libraries from internal dashboards. 163 pages, ~2300 panel queries committed locally. **Every ASI page (162/162) ships an `investigation-guide/` folder** — that is the preferred entry point: it's a curated, symptom-keyed set of chapter files with KQL bodies inlined and grouped by intent.

**Start with one of the navigation files** (don't dive straight into per-page folders):

| File | When to use |
|---|---|
| [`dashboards/panel-index.md`](dashboards/panel-index.md) | **Grep this** when a TSG mentions an ASI panel name. Flat table of all 2300 queries; each row's `Guide` column jumps to that page's investigation guide. |
| [`dashboards/by-scenario.md`](dashboards/by-scenario.md) | Hand-curated map of which pages to open for each kind of investigation (VM / host / EEE / CRP / disk / networking / …). Page links go straight to the page's investigation guide. |
| [`dashboards/INDEX.md`](dashboards/INDEX.md) | Per-portal directory of all pages (slug · service · panel/query counts · **investigation-guide link** · top clusters). Auto-generated. |
| [`dashboards/README.md`](dashboards/README.md) | Folder layout, replay workflow, security notes. |

**Tip — symptom-driven grep**: skip the indexes and grep the investigation guides directly when a TSG describes a symptom rather than a panel:

```powershell
Select-String "ContainerState" .github/skills/vm-kusto-query/references/dashboards/asi/pages/*/investigation-guide/*.md
```

Each individual page lives at `dashboards/<portal>/pages/<slug>/` with:
- `investigation-guide/` — curated `README.md` chapter index + `01-...md`, `02-...md`, … chapters with **inline KQL bodies** (preferred);
- `library.md` — panel→KQL metadata table (no bodies; fallback when a page has no guide);
- `library.json` — machine-readable form, `panels[<path>].queries[].kustoQuery` holds the raw KQL text (used by `replay.py`);
- optional `replay.py` — execution engine that auto-resolves param aliases.

Index regeneration: `python _work/_scratch/build-dashboards-index.py` rebuilds `INDEX.md` + `panel-index.md`.
