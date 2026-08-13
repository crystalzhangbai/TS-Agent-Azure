# EEE Start Hub — Outbound Link Inventory

Captured by playwright-cli DOM scrape on **2026-05-13** against the live page (authenticated session, persistent profile). Source data: [`raw/dom-link-harvest.json`](raw/dom-link-harvest.json).

> **Source URL** (case `0511gpuvmunexpectedredeployment013`):
> `https://asi.azure.ms/services/EEE%20RDOS/pages/Start%20Hub?cluster=IAD03PrdGPC06&containerid=…&nodeid=…&roleInstanceName=…&tenantname=…&vmid=…&globalFrom=…&globalTo=…`

- DOM anchors found: **79**
- Button / role=link items: **303** (mostly intra-page UI)
- Distinct external hosts: **12**

> **Note on completeness**: DOM scrape misses any link gated behind hover/click. The authoritative list lives in the ASI page widget tree (`page.json`) — capturable by re-running `_tooling/extract.js` with a fresh Bearer token. The list below is what's visibly anchored on first paint.

---

## A. Other ASI pages — high-priority RE targets

These are **separate ASI dashboards** that the Start Hub page links into. Each is a candidate for full library extraction (run the existing extract.js with adjusted `SERVICE`/`PAGE` constants).

| # | Service / Page | Path template (query keys) | Label on EEE | Why interesting |
|---|---|---|---|---|
| 1 | **EEE RDOS / VM Availability** | `?Tenant=&containerId=&globalFrom=&globalTo=&nodeId=&roleInstanceName=&tenantName=&virtualMachineUniqueId=` | "Page for General Scenarios" | The general VM availability investigation page; alternate entry to EEE for VM Down events |
| 2 | **EEE RDOS / WF Resource Health** | `?Cluster=&ContainerId=&NodeId=&SubscriptionId=&TenantName=&VMName=&VmId=&globalFrom=&globalTo=` | "Page for further investigation" | The WF (workflow) Resource Health drill-down — what customer-side Azure Resource Health reports |
| 3 | **EEE RDOS / WF Unexpected Restart** | `?globalFrom=&globalTo=&query_ContainerId=&query_NodeId=&query_SubscriptionId=&query_TenantName=&query_VMName=&query_cluster=&query_vmId=` | "Page for further investigation" / "LM tab on WF Unexpected Restart" | The dedicated "why did this VM restart" workflow page — has LM (Live Migration) tab |
| 4 | **EEE RDOS / Start Hub [Test]** | `?cluster=&containerid=&globalFrom=&globalTo=&nodeid=&roleInstanceName=&tenantname=&vmid=` | "Start Hub [Test Purpose Only]" | Likely a staged test version — probably not worth RE'ing for production use |
| 5 | **Aztec / Clusters** | `?Tenant=&globalFrom=&globalTo=` | "IAD03PrdGPC06" | Cluster-level dashboard (capacity, fault, fabric state) |
| 6 | **Aztec / Tenant {{tenantName}}** | `?globalFrom=&globalTo=&tenantName=` | tenant GUID | Tenant-level dashboard (note the literal `{{tenantName}}` in URL path is intentional ASI templating) |
| 7 | **Azure Host / Azure Host Node** | `?globalFrom=&globalTo=&nodeId=` | "Page for node performance" | Host node performance — equivalent to the **EEE HostNode** node-perf view; included in this dashboard catalog |
| 8 | **Azure Host / Azure VM** | `?containerId=&globalFrom=&globalTo=&nodeId=&virtualMachineUniqueId=` | "Page for VM performance" | VM-level performance — the **"Azure VM" graph** used for VM-level triage |

## B. ASI compoundWidget pop-outs (same library, sub-views)

These are stand-alone URLs for **individual panels of Start Hub itself**. Their underlying queries are already covered in `library.json` — no additional extraction needed. Useful as direct links when you want to share a single panel.

| Compound widget | Path |
|---|---|
| Container & Tenant Health (v.113) | `/services/EEE RDOS/compoundWidgets/Container & Tenant Health` |
| Fabric Available Nodes (v.14) | `/services/EEE RDOS/compoundWidgets/Fabric Available Nodes` |
| Network Health (v.64) | `/services/EEE RDOS/compoundWidgets/Network Health` |
| Node Software Health (v.74) | `/services/EEE RDOS/compoundWidgets/Node Software Health` |
| Node Update (v.6) | `/services/EEE RDOS/compoundWidgets/Node Update` |
| Physical Node (v.2) | `/services/EEE RDOS/compoundWidgets/Physical Node` |
| Services on Node (v.10) | `/services/EEE RDOS/compoundWidgets/Services on Node` |
| Start Hub - AI Tool (v.2) | `/services/EEE RDOS/compoundWidgets/Start Hub - AI Tool` |
| Start Hub - Automated Detector (v.95) | `/services/EEE RDOS/compoundWidgets/Start Hub - Automated Detector` |
| Start Hub - Container (v.9) | `/services/EEE RDOS/compoundWidgets/Start Hub - Container` |
| Start Hub - Container Transition (v.28) | `/services/EEE RDOS/compoundWidgets/Start Hub - Container Transition` |
| Start Hub - General Tool Links (v.36) | `/services/EEE RDOS/compoundWidgets/Start Hub - General Tool Links` |
| Start Hub - Network / TOR (v.29) | `/services/EEE RDOS/compoundWidgets/Start Hub - Network / TOR` |
| Start Hub - Overlake / SoC (v.7) | `/services/EEE RDOS/compoundWidgets/Start Hub - Overlake / SoC` |
| Start Hub - VM (v.11) | `/services/EEE RDOS/compoundWidgets/Start Hub - VM` |
| Start Hub - Workflows/Scenarios Links (v.9) | `/services/EEE RDOS/compoundWidgets/Start Hub - Workflows/Scenarios Links` |
| StartHub - NodePerformanceMetrics (v.6) | `/services/EEE RDOS/compoundWidgets/StartHub-NodePerformanceMetrics` |
| VM Availability (Public Cloud) - CRP Operation (v.7) | `/services/EEE RDOS/compoundWidgets/VM Availability (Public Cloud) - CRP Operation` |
| VM Availability (Public Cloud) - Cluster Health (v.10) | `/services/EEE RDOS/compoundWidgets/VM Availability (Public Cloud) - Cluster Health` |

## C. External portals & tools — separate RE projects

Each row below is a candidate for its own `dashboards/<portal>/pages/<page>/` entry. Some are PowerBI/SaaS dashboards (no per-panel API to capture — Playwright fallback likely), others are URL-templated query tools (just need to document the templates).

| # | Tool | URL template | Source-type guess | Notes |
|---|------|--------------|-------------------|-------|
| 1 | **AIR Dashboard** | `https://aka.ms/airdash` | unknown — follow the redirect | Likely a separate ASI / Geneva dashboard |
| 2 | **Auto Draft RCA** | `https://aka.ms/AutoDraftRCA` | unknown | Likely a workflow tool |
| 3 | **Decomm Dashboard** | `http://aka.ms/azdecom/pbiapp` | PowerBI | Resource decomm tracking |
| 4 | **Azure Capacity** | `https://aka.ms/azurecapacity` | unknown | Capacity dashboard |
| 5 | **FixTracker** | `https://aka.ms/fixtracker` | unknown | Fix/repair tracking |
| 6 | **HA Release Tool** | `https://aka.ms/harelease` | unknown | Host agent release tracking |
| 7 | **Iridias** | `https://aka.ms/iridias` | unknown | (resolve aka.ms) |
| 8 | **Polaris Bot** | `https://aka.ms/polarisbot` | unknown | (resolve aka.ms) |
| 9 | **RCA List** | `https://aka.ms/rcalist` | unknown | RCA inventory |
| 10 | **WISE** | `https://aka.ms/wise` | unknown | (resolve aka.ms) |
| 11 | **Evaluate Node CPU Usage** | `https://aka.ms/Evaluate_Node_CPU_Usage?p-Spatial_Baseline_Param=&p-endTimeParam=&p-nodeIdParam=&p-startTimeParam=` | ADX dashboard (URL params suggest dataexplorer.azure.com after redirect) | Templated CPU evaluation |
| 12 | **RDMA Dash** (ADX) | `https://dataexplorer.azure.com/dashboards/49ff7d6a-5bf0-4307-ad55-6bac34f15a59?p-_ContainerId=&p-_ICMId=&p-_NodeId=&p-_endTime=&p-_nodeIds=&p-_startTime=&p-peers=` | **ADX Dashboard** | Direct Kusto-dashboard link; we CAN extract its KQL via ADX `/v1/rest/query?dashboardId=` API |
| 13 | **Node Story** | `https://azurehostosapp.azurewebsites.net/node-story?nodeId=&time=` | Custom backend (Azure Web App) | Service-specific backend |
| 14 | **Node Story (Sub)** | `https://mhfgatewayfrontdoor.accia-ame.azure.com/webapp/aegis-dashboard/nodestory?datetime=&nodeId=` | Custom backend (Aegis dashboard) | Azure subscription-flavored variant |
| 15 | **Eagle Eye** | `https://eagleeye.trafficmanager.net/diagnostics/EagleEye/VMToDest?CustomerProblemCategory=&Dest=&EndTime=&SrcVm=&StartTime=` | Custom backend | Network diagnostics |
| 16 | **NetVMA** | `https://netvma.trafficmanager.net/?destValue=&endTime=&pathQuery=&sdnPath=&startTime=&value=` | Custom backend | VM network diagnostics |
| 17 | **Azure Watson** | `https://portal.watson.azure.com/?$filter=` | Watson portal (REST?) | Crash dump search |
| 18 | **Resource SKU by Region (PowerBI)** | `https://msit.powerbi.com/groups/me/reports/939367b4-36cd-4fe9-b8fe-f1923e2a1a28/ReportSection` | PowerBI | Playwright fallback only — PowerBI doesn't expose per-tile data via simple REST |
| 19 | **EEE-RDOS-Tool-in-ASI wiki** | `https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/807976/...` | Wiki | Read-only doc; no RE needed |
| 20 | **ASI Kusto access guide** | `https://eng.ms/docs/products/azure-service-insights/onboarding/kustoaccess` | Docs | No RE needed |
| 21 | **CoreIdentity entitlement (ICM Kusto access)** | `https://coreidentity.microsoft.com/manage/entitlement/entitlement/icmkustoacce-ufk0` | Entitlement portal | No RE needed |

## D. ADX Dashboards (Kusto Dashboard service)

These deserve special mention — `dataexplorer.azure.com/dashboards/<guid>` URLs are **Azure Data Explorer dashboards** (different mechanism than ASI). ADX has a documented API for fetching dashboard config + queries:

- `GET https://dataexplorer.azure.com/api/v1/dashboards/<guid>` (or similar — confirm)
- Each tile has its own KQL body, parameters, and target cluster/database
- Could be extracted with a similar approach as ASI — likely worth a dedicated `dashboards/adx/_tooling/`

| Dashboard | GUID | Title |
|---|---|---|
| RDMA Dash | `49ff7d6a-5bf0-4307-ad55-6bac34f15a59` | RDMA / RoCE diagnostics |
| Evaluate Node CPU Usage (via aka.ms redirect) | (resolves after redirect) | CPU usage evaluation |

Also: bare cluster links (`/clusters/<host>/databases/<db>`) — these are just ADX query workspaces, not dashboards; nothing to RE.

## E. Kusto clusters referenced in localStorage MSAL token cache

The page has acquired tokens for the following Kusto clusters during this session (extracted from `msal.2.token.keys.eb092fbe-b5f4-492f-bd9a-3787232fbdeb`):

- `icmcluster.kusto.windows.net`
- `azcore.centralus.kusto.windows.net`
- `azurecm.kusto.windows.net`
- `azpe.kusto.windows.net`
- `storageclient.eastus.kusto.windows.net`

Cross-reference: `library.json` queries reference more clusters than this (see meta.json), so the cache reflects what's been touched by this *specific session*, not the full set.

---

## Recommended next RE queue

Order of effort vs. value for the next ASI pages to extract:

1. **EEE RDOS / WF Unexpected Restart** — directly relevant to the user's most common case type ("unexpected reboot")
2. **EEE RDOS / WF Resource Health** — pairs naturally with #1
3. **EEE RDOS / VM Availability** — broader availability investigation
4. **Azure Host / Azure VM** — VM perf, complements Start Hub's host-side view
5. **Azure Host / Azure Host Node** — node perf
6. **Aztec / Tenant {{tenantName}}** — tenant-level fabric view
7. **Aztec / Clusters** — cluster-level fabric view

For external tools (section C), suggest:
- First, **resolve all `aka.ms` shortlinks** (one-shot HEAD requests) to see what they redirect to — many may go to the same ADX/ASI/Geneva endpoints we already cover.
- Then prioritize ADX Dashboards (RDMA Dash) since the extraction pattern is similar to ASI.
- Custom backends (Node Story, Eagle Eye, NetVMA) need per-target investigation.
- PowerBI → Playwright fallback only.
