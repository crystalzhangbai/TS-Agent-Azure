---
name: aks
description: >-
  AKS cluster troubleshooting skill for CSS engineers. Investigates Azure Kubernetes Service
  issues by combining Azure DevOps wiki search with Kusto (KQL) database queries. Use for
  node failures, cluster operations, upgrade issues, networking problems, control plane
  troubleshooting, and autoscaler analysis. Covers AKSprod, AKSccplogs, AKSinfra, and
  AKSmetrics databases.
license: MIT
compatibility: >-
  Uses the MCP servers defined in plugins/naniteagent/.mcp.json, including mslearn,
  csswiki, azurewiki, azurefrontdoor, seektheway, azuremcp, and workiq. Browser automation
  is handled via the playwright-cli skill (not an MCP server).
  Needs read access to AKSprod, AKSccplogs, AKSinfra, and AKSmetrics Kusto databases.
---

# AKS Cluster Troubleshooting Skill

Investigate and troubleshoot AKS cluster issues by combining wiki documentation search with Kusto database queries.

## MCP Servers

| MCP Server | Purpose |
|------------|---------|
| **mslearn** | Search Microsoft Learn for supporting documentation |
| **csswiki** | Search CSS supportability wiki content relevant to AKS issues |
| **azurewiki** | Search Azure engineering wiki content relevant to AKS issues |
| **azurefrontdoor** | Search Front Door documentation for adjacent networking issues |
| **seektheway** | Search deep-dive troubleshooting and SME guidance |
| **azuremcp** | Execute Azure and Kusto-related queries through the configured Azure MCP server |
| **workiq** | Access WorkIQ data when a workflow needs M365 context |

> 🌐 **Browser automation**: Use the **playwright-cli skill** for any UI-based follow-up investigation. It is a skill, not an MCP server — invoke it via the skill interface.

**Using Azure MCP for queries:**
- Use the Azure MCP server configured in `plugins/naniteagent/.mcp.json`
- Prefer local schema files first, then use MCP-based query execution when schema is unavailable
- Keep queries scoped to the target AKS database and time range

## Databases

| Database | Cluster URI | Purpose |
|----------|------------|---------|
| **AKSprod** | `https://akshuba.centralus.kusto.windows.net` | Cluster config, snapshots, operations |
| **AKSccplogs** | `https://aksccplogs.centralus.kusto.windows.net` | Control plane logs (audit, scheduler, etcd) |
| **AKSinfra** | `https://akshuba.centralus.kusto.windows.net` | Infrastructure & ARM operations |
| **AKSmetrics** | `https://akshuba.centralus.kusto.windows.net` | Performance metrics & monitoring |

> 📖 **Detailed database guide**: [references/database-guide.md](references/database-guide.md)

## Schema Verification — IMPORTANT

**Before writing any query, verify the table schema:**

1. **Check local schema files first** (preferred):
   - Full schemas: `table-schema/{database}/{table}-schema.json`
   - Quick reference: [references/TABLE_SCHEMA_REFERENCE.md](references/TABLE_SCHEMA_REFERENCE.md)

2. **Use MCP tool azuremcp ** (if local schema not available):
   ```
  Before running a KQL query on an unfamiliar table, always call azuremcp-kusto with command: kusto_table_schema to verify column names and types. Never fabricate column names.
   ```

**⚠️ Common schema pitfalls:**
- `ManagedClusterSnapshot` uses `namespace` for CCP namespace (NOT `ccpNamespace`)
- `AgentPoolSnapshot` uses `size` for node count (NOT `nodeCount`)
- `RemediatorEvent` uses `ccpNamespace`, NOT `clusterName`
- `ClusterAutoscaler` has no `level` column — filter on `log` field text
- Many tables have a `log` field with full JSON — parse with `todynamic(tostring(log))`

> 📖 **Query tips & common errors**: [references/query-best-practices.md](references/query-best-practices.md)

---

## Workflow

### Step 1 — Gather Information

Ask the user to provide:
- **Issue Description**: e.g., "pods failing to schedule", "cluster upgrade failed"
- **Error Message**: Any error messages or symptoms (if available)
- **Cluster Resource ID**: `/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.ContainerService/managedClusters/{name}`
- **Time Range**: When did the issue occur?
- **Affected Resources**: Specific pods, nodes, namespaces (optional)

### Step 2 — Search Documentation

Ask whether user wants to search the configured documentation sources for related guides:
- **azurewiki** → search for Azure engineering guidance and AKS-related writeups
- **csswiki** → search for CSS supportability content and known issues
- **mslearn** → search Microsoft Learn for public or supporting documentation
- **seektheway** → search deep-dive and advanced troubleshooting content

Summarize findings and ask whether to continue with Kusto queries.

### Step 3 — Parse Cluster Information

From the resource ID, extract and store:
- **Subscription ID**
- **Resource Group name**
- **Cluster name**

### Step 4 — Query Cluster Information

Run queries from [references/cluster-info-queries.md](references/cluster-info-queries.md):

| Query | Database | Use When |
|-------|----------|----------|
| **4.1 Basic Cluster Info** | AKSprod | Always — first query to run. Gets `ccpNamespace` for subsequent queries |
| **4.2 Comprehensive Info** | AKSprod | Need full cluster context (multi-table join) |
| **4.3 Network-Focused** | AKSprod | Network/connectivity issues |
| **4.4 Node Pools** | AKSprod | Node pool configuration, autoscaler settings |
| **4.5 Individual Nodes** | AKSccplogs | Node status, readiness, IP addresses |
| **4.6 Unhealthy Pods** | AKSccplogs | Pod crashes, OOMKills, CrashLoopBackOff |
| **4.7 Overlay Components** | AKSprod | Control plane component health |

**⚠️ Always run 4.1 first** — it returns the `ccpNamespace` value needed by all other queries.

**Quick start query** (Step 4.1 — always run this first):

```kql
ManagedClusterSnapshot
| where PreciseTimeStamp > ago(2d)
| where clusterName == '{Cluster name}'
| take 1
| project 
    // Basic Info
    PreciseTimeStamp,
    clusterName,
    ccpNamespace = namespace,
    location,
    provisioningState,
    clusterNodeCount,
    // Kubernetes Version
    kubernetesVersion = tostring(todynamic(orchestratorProfile).orchestratorVersion),
    // SKU
    sku_tier = tostring(todynamic(sku).tier),
    // Outbound
    outboundType,
    // Underlay
    UnderlayName,
    // Power State
    powerState = tostring(todynamic(powerState).code),
    // Addons
    addonProfiles
```


**⚠️ Critical:** Save the returned `ccpNamespace` value — it is required for filtering in all subsequent queries.

> 📖 **All cluster info queries (4.1-4.7)**: [references/cluster-info-queries.md](references/cluster-info-queries.md)

### Step 5 — Check Cluster Health

Run health check queries based on issue type:

| Check | Database | Use When |
|-------|----------|----------|
| **Recent Operations** | AKSprod | Operation failures, stuck operations |
| **API Server Latency** | AKSccplogs | Slow API responses, timeouts |
| **API Server Errors** | AKSccplogs | 4xx/5xx errors, throttling (429) |
| **etcd Health** | AKSccplogs | Database size, slow requests, leader elections |

> 📖 **All health check queries**: [references/cluster-health-checks.md](references/cluster-health-checks.md)

### Step 6 — Issue-Specific Investigation

Based on the issue type, use the appropriate troubleshooting guide:

| Issue Type | Guide | Keywords |
|-----------|-------|----------|
| **Node failures** | [guides/node-troubleshooting.md](guides/node-troubleshooting.md) | node not ready, node failure, provisioning, unregistered |
| **Cluster operations** | [guides/cluster-operations.md](guides/cluster-operations.md) | upgrade, start/stop, autoscaler, scale, CA |
| **Audit/compliance** | [guides/audit-logs.md](guides/audit-logs.md) | audit, API activity, who/what/when, pod status |
| **Deployment issues** | Use CloudControllerManager in AKSccplogs | deployment, service, load balancer, replica |

**For deployment issues** (not covered by specific guides):

```kql
// Database: AKSccplogs
CloudControllerManager  
| where PreciseTimeStamp between (datetime('{startTime}') .. datetime('{endTime}'))
| where namespace == '{ccpNamespace}' 
| where log has_any ('{keyword1}', '{keyword2}')
| project PreciseTimeStamp, log, pod_name
| order by PreciseTimeStamp asc
| take 100
```

### Step 7 — Summarize Findings

Present findings in structured format:
1. **Root Cause** (confirmed or suspected)
2. **Evidence** (query results, timeline)
3. **Impact** (scope of affected resources)
4. **Recommended Actions** (mitigation, fix, escalation)

---

## Reference Documents

### Architecture & Schemas
| Document | Purpose |
|----------|---------|
| [references/ARCHITECTURE.md](references/ARCHITECTURE.md) | AKS architecture, database scope, troubleshooting decision tree |
| [references/TABLE_SCHEMA_REFERENCE.md](references/TABLE_SCHEMA_REFERENCE.md) | Quick reference for all Kusto table schemas |
| [references/TSG_REFERENCE.md](references/TSG_REFERENCE.md) | TSG patterns: autoscaler, CNI, node lifecycle, escalation |

### Query References
| Document | Purpose |
|----------|---------|
| [references/cluster-info-queries.md](references/cluster-info-queries.md) | Cluster info queries (Steps 4.1–4.7) |
| [references/cluster-health-checks.md](references/cluster-health-checks.md) | Health checks (Step 5) |
| [references/database-guide.md](references/database-guide.md) | Database overview, cross-DB queries, common patterns |
| [references/query-best-practices.md](references/query-best-practices.md) | Query errors, performance tips, presentation |

### Troubleshooting Guides
| Guide | Scope |
|-------|-------|
| [guides/node-troubleshooting.md](guides/node-troubleshooting.md) | Node lifecycle, registration, CNI issues |
| [guides/cluster-operations.md](guides/cluster-operations.md) | CRUD ops, auto-upgrade, cluster autoscaler |
| [guides/audit-logs.md](guides/audit-logs.md) | Kubernetes API audit log analysis |

### Schema Files
- `table-schema/{database}/{table}-schema.json` — JSON schema per table

---

## Quick Reference: Time Ranges

| Investigation Type | Recommended Range |
|-------------------|-------------------|
| Current state / snapshot | `ago(2h)` |
| Recent operations | `ago(24h)` |
| Upgrade history | `ago(7d)` |
| Intermittent issues | `ago(12h)` to `ago(3d)` |
| Audit log analysis | `ago(1h)` to `ago(6h)` |

## Quick Reference: Key Identifiers

| Identifier | Source | Used In |
|-----------|--------|---------|
| `clusterName` | Resource ID or user input | AKSprod queries (ManagedClusterSnapshot) |
| `ccpNamespace` | Step 4.1 query result (`namespace` field) | AKSccplogs queries (KubeAudit, etc.) |
| `cluster_id` | Same as `ccpNamespace` | Most tables across all databases |
| `subscriptionID` | Resource ID | ARM operation queries |
