# AKS Kusto Database Guide

> Quick reference for the four AKS Kusto databases, their key tables, and common query patterns.

## AKSprod — Snapshot & Operations Tables

**Cluster URI**: `https://akshuba.centralus.kusto.windows.net`

### Key Tables

| Table | Description | Primary Filter |
|-------|-------------|----------------|
| `ManagedClusterSnapshot` | Cluster-level config (version, SKU, addons, network) | `clusterName` or `subscription` + `managedClusterResourceGroup` |
| `AgentPoolSnapshot` | Node pool configs (VM size, count, autoscaler, OS) | `clusterName` + `name` |
| `ControlPlaneWrapperSnapshot` | Control plane wrapper config (network profile, cloud provider) | `subscription` + `clusterName` |
| `AsyncQoSEvents` | Async RP operations (create/update/delete/upgrade/scale) | `namespace` or `resourceName` |

### Common Filters
```kql
// By CCP namespace (most precise)
| where cluster_id == '{ccpNamespace}'

// By cluster name (convenient but may match multiple)
| where clusterName == '{clusterName}'

// By subscription
| where subscriptionID == '{subscriptionId}'
```

### Snapshot Query Pattern
Snapshot tables are periodically updated. Always get the latest snapshot:
```kql
TableName
| where PreciseTimeStamp > ago(2h)
| where cluster_id == '{ccpNamespace}'
| order by PreciseTimeStamp desc
| take 1
```

---

## AKSccplogs — Control Plane Logs

**Cluster URI**: `https://akshuba.centralus.kusto.windows.net`

### Key Tables

| Table | Description | Primary Filter |
|-------|-------------|----------------|
| `KubeAudit` | Kubernetes API audit logs (all API calls) | `cluster_id` + `verb` + `objectRef.resource` |
| `KubeScheduler` | Scheduler decisions and failures | `cluster_id` |
| `KubeControllerManager` | Controller manager logs | `cluster_id` |
| `Etcd` | etcd cluster logs | `cluster_id` |
| `CloudControllerManager` | Cloud controller manager logs | `cluster_id` |

### KubeAudit Query Pattern
```kql
cluster('akshuba.centralus').database('AKSccplogs').KubeAudit
| where PreciseTimeStamp between(datetime({start}) .. datetime({end}))
| where cluster_id == '{ccpNamespace}'
| where verb in ('create', 'update', 'delete', 'patch')
| where objectRef.resource == '{resource}'  // e.g., 'pods', 'nodes', 'deployments'
| project PreciseTimeStamp, verb, 
    resource = objectRef.resource,
    name = objectRef.name, 
    namespace = objectRef.namespace,
    user = user.username,
    responseCode = responseStatus.code
```

### Audit Log Levels
| Level | Content | Use Case |
|-------|---------|----------|
| `Metadata` | Request metadata only | Track who did what |
| `Request` | Metadata + request body | See what was requested |
| `RequestResponse` | Metadata + request + response | Full details (heavy) |

### Important Notes
- **⚠️ KubeAudit is the largest table** — always use tight time filters
- **Filter by `objectRef.resource`** to avoid scanning everything
- **`requestObject` and `responseObject`** are dynamic fields — use `todynamic()` or dot notation
- **Node info** is in `responseObject.status` for node-related audit entries

---

## AKSprod — RP Operations & Events

**Cluster URI**: `https://akshuba.centralus.kusto.windows.net`
**DATABASE**: `AKSprod`

> **Note**: Tables `AKSControlPlaneEvents`, `ControlPlaneOperations`, and `NodeOperations` do **not** exist. Use the tables below for operation and event tracking.

### Key Tables

| Table | Description | Primary Filter |
|-------|-------------|----------------|
| `AsyncQoSEvents` | Async RP operation lifecycle (CRUD/upgrade/scale results) | `namespace` or `resourceName` |
| `FrontEndContextActivity` | Front-end request/operation traces | `operationID` |
| `AsyncContextActivity` | Async operation context traces | `operationID` |
| `RemediatorEvent` | Node remediation events | `ccpNamespace` |
| `AutoUpgraderEvents` | Auto-upgrade scheduling and execution | `resourceName` |

### Operation Tracking Pattern
```kql
cluster('akshuba.centralus').database('AKSprod').AsyncQoSEvents
| where PreciseTimeStamp > ago(24h)
| where namespace == '{ccpNamespace}'
| project PreciseTimeStamp, operationName, resultCode, errorDetails, operationID
| order by PreciseTimeStamp desc
```

---

## AKSmetrics — Performance Metrics

**Cluster URI**: `https://akshuba.centralus.kusto.windows.net`
**DATABASE**: `AKSmetrics`

### Key Tables

| Table | Description | Primary Filter |
|-------|-------------|----------------|
| `InsightsMetrics` | Container/node metrics (CPU, memory, disk) | `cluster_id` + `Name` |
| `KubeNodeInventory` | Node inventory and status | `ClusterId` |
| `KubePodInventory` | Pod inventory and status | `ClusterId` |
| `ContainerLog` | Container stdout/stderr logs | `ClusterId` |

### Metrics Query Pattern
```kql
cluster('akshuba.centralus').database('AKSmetrics').InsightsMetrics
| where TimeGenerated > ago(1h)
| where ClusterId contains '{ccpNamespace}'
| where Name == 'cpuUsageNanoCores'
| summarize avg(Val) by bin(TimeGenerated, 5m), Computer
```

> **Note**: AKSmetrics availability depends on whether the customer has monitoring enabled (Azure Monitor / Container Insights).

---

## Cross-Database Query Pattern

When you need data from multiple databases:

```kql
// Get cluster info from AKSprod
let clusterInfo = cluster('akshuba.centralus').database('AKSprod').ManagedClusterSnapshot
| where PreciseTimeStamp > ago(2h)
| where clusterName == '{clusterName}'
| take 1
| project cluster_id, clusterName, kubernetesVersion = tostring(todynamic(orchestratorProfile).orchestratorVersion);

// Then use cluster_id in AKSccplogs
cluster('akshuba.centralus').database('AKSccplogs').KubeAudit
| where PreciseTimeStamp > ago(1h)
| where cluster_id in ((clusterInfo | project cluster_id))
| where responseStatus.code >= 400
| summarize ErrorCount = count() by verb, resource = tostring(objectRef.resource)
```

---

## Common Query Patterns

### Time Range Best Practices

| Investigation Type | Recommended Range | Rationale |
|-------------------|-------------------|-----------|
| Current state / snapshot | `ago(2h)` | Snapshots update every ~15-30 min |
| Recent operations | `ago(24h)` | Operations may take hours |
| Upgrade history | `ago(7d)` | Upgrades can span multiple days |
| Intermittent issues | `ago(12h)` to `ago(3d)` | Need enough data to see patterns |
| Audit log analysis | `ago(1h)` to `ago(6h)` | Large data volume, keep focused |

### Performance Tips

1. **Always filter by `cluster_id` first** — this is the partition key
2. **Use `between()` for time ranges** — more efficient than `> ago()` for historical queries
3. **Limit `KubeAudit` queries** — add `verb`, `objectRef.resource` filters
4. **Use `take N`** instead of `top N by ... desc` for quick lookups
5. **Avoid `contains` on large string fields** — use `==` or `has` instead
6. **Use `summarize` to aggregate** before joining tables

### Common Field Gotchas

| Field | Gotcha | Correct Usage |
|-------|--------|---------------|
| `namespace` in MCS | This is CCP namespace, not K8s namespace | Use as cluster identifier |
| `objectRef.namespace` in KubeAudit | This IS the K8s namespace | Filter for workload namespace |
| `cluster_id` | Sometimes lowercase, sometimes not | Use `=~` for case-insensitive |
| `log` in MCS | Stringified JSON | Parse with `todynamic(tostring(log))` |
| `requestObject` / `responseObject` | Dynamic type | Use dot notation directly |
| `size` in AgentPoolSnapshot | Node count | Not VM size (that's `vmSize`) |
