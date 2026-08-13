# Table Schema Quick Reference

This document provides key fields for commonly used tables in AKS troubleshooting queries.

## ⚡ Query Performance Best Practices

To avoid timeouts and improve query performance, follow these guidelines:

### 1. Always Limit Results
```kql
| take 30                    // Hard limit on rows returned
| top 10 by PreciseTimeStamp desc  // Limit with ordering
| limit 20                   // Same as take
```

### 2. Use Narrow Time Ranges
```kql
// ✅ Good: Specific time window (1-2 hours)
| where PreciseTimeStamp between (datetime('2026-02-02T19:00:00Z') .. datetime('2026-02-02T21:00:00Z'))

// ⚠️ Acceptable: Recent data only
| where PreciseTimeStamp > ago(2d)

// ❌ Bad: Wide time range without other filters
| where PreciseTimeStamp > ago(30d)
```

### 3. Apply Filters Early (Before Parsing)
```kql
// ✅ Good: Filter first, then parse
| where namespace == '{ccpNamespace}'
| where log contains 'error'
| extend logd = todynamic(log)

// ❌ Bad: Parse everything, then filter
| extend logd = todynamic(log)
| where namespace == '{ccpNamespace}'
```

### 4. Use Summarize for Aggregations
```kql
// ✅ Good: Summarize instead of returning all rows
| summarize count() by alertname, status, severity
| order by count_ desc
| limit 20

// ❌ Bad: Returning raw data for large result sets
| project PreciseTimeStamp, alertname, status, message
```

### 5. Project Only Needed Columns
```kql
// ✅ Good: Select only required fields
| project PreciseTimeStamp, clusterName, provisioningState

// ❌ Bad: Returning entire row with dynamic fields
| project *
```

### 6. Use Efficient String Matching
```kql
// ✅ Fast: Exact match or contains
| where clusterName == 'my-cluster'
| where log contains 'error'

// ✅ Fast: has_any for multiple keywords
| where log has_any ('error', 'failed', 'timeout')

// ⚠️ Slower: Regex patterns
| where log matches regex 'error.*timeout'
```

---

## AKSprod Database Tables

### ManagedClusterSnapshot
**Purpose**: Cluster configuration snapshots
**Key Fields**:
- `subscription` (string) - Subscription ID (**use for filtering**)
- `managedClusterResourceGroup` (string) - Managed cluster resource group (**use for filtering**)
- `customerResourceGroup` (string) - Customer resource group name
- `clusterName` (string) - Cluster name (**use for filtering**)
- `namespace` (string) - **CCP namespace** (use this for filtering control plane logs)
- `location` (string) - Azure region
- `UnderlayName` (string) - Underlay cluster name
- `provisioningState` (string) - Cluster state
- `clusterNodeCount` (int) - Total node count
- `powerState` (dynamic) - Power state (Running/Stopped)
- `sku` (dynamic) - SKU tier
- `outboundType` (string) - Outbound connectivity type
- `addonProfiles` (dynamic) - Addon configurations
- `orchestratorProfile` (dynamic) - Contains orchestratorVersion
- `hostedMasterProfile` (dynamic) - Contains FQDN
- `LoadBalancerProfile` (dynamic) - LB configuration
- `PreciseTimeStamp` (datetime) - Record timestamp

**Note**: Many fields are `dynamic` type - use `tostring()` or `todynamic()` to extract values.

**⚠️ Important Filtering Notes:**
- Use `clusterName` or `name` to filter by cluster (NOT `resourceId` - this field doesn't exist)
- Use `customerResourceGroup` to filter by resource group
- The `namespace` field contains the CCP namespace (NOT `ccpNamespace` - that field doesn't exist in this table)
- Use `cluster_id` for ARM resource ID matching
- **ALWAYS use `subscription` and `managedClusterResourceGroup` filters for optimal query performance**

**Example Query (Optimized):**
```kql
cluster('akshuba.centralus').database('AKSprod').ManagedClusterSnapshot
| where PreciseTimeStamp > ago(2d)
| where subscription contains '{subscriptionId}'
| where clusterName contains '{clusterName}'
| where managedClusterResourceGroup contains '{resourceGroup}'
| top 1 by PreciseTimeStamp desc
| project PreciseTimeStamp, clusterName, ccpNamespace=namespace, location, provisioningState, clusterNodeCount,
    kubernetesVersion = tostring(todynamic(orchestratorProfile).orchestratorVersion),
    sku_tier = tostring(todynamic(sku).tier),
    outboundType, UnderlayName
```

**Note**: Use `contains` for partial matching or `==` for exact matching. The `subscription`, `clusterName`, and `managedClusterResourceGroup` filters significantly improve query performance by narrowing the search scope early.

### AsyncQoSEvents
**Purpose**: Async operation quality of service events
**Key Fields**:
- `subscriptionID` (string)
- `resourceGroupName` (string)
- `resourceName` (string) - Cluster name
- `operationID` (string) - **Unique operation identifier**
- `operationName` (string) - Operation type
- `suboperationName` (string)
- `resultType` (long) - 0=success, 1=user error, 2=service error
- `resultCode` (string)
- `resultSubCode` (string)
- `errorDetails` (string)
- `k8sCurrentVersion` (string)
- `k8sGoalVersion` (string)
- `PreciseTimeStamp` (datetime)

### FrontEndQoSEvents
**Purpose**: Frontend API quality of service events
**Key Fields**: Similar to AsyncQoSEvents plus:
- `httpMethod` (string)
- `httpStatus` (long)
- `userAgent` (string)
- `correlationID` (string)
- `latency` (long) - milliseconds

### FrontEndContextActivity / AsyncContextActivity
**Purpose**: Detailed operation traces
**Key Fields**:
- `operationID` (string) - **Correlate with QoS events**
- `operationName` (string)
- `msg` (string) - Log message
- `level` (string) - error, warning, info
- `fileName` (string)
- `lineNumber` (long)
- `PreciseTimeStamp` (datetime)

### AgentPoolSnapshot
**Purpose**: Node pool configuration snapshots
**Key Fields** (top-level columns):
- `subscription` (string) - Subscription ID (**use for filtering**)
- `clusterName` (string) - Cluster name (**use for filtering**)
- `name` (string) - Pool name
- `vmSize` (string)
- `orchestratorVersion` (string) - K8s version
- `provisioningState` (string)
- `enableAutoScaling` (bool)
- `minCount`, `maxCount` (string)
- `osType`, `osSku` (string)
- `osDiskSizeGB` (long)
- `osDiskCaching` (string) - "ReadOnly", "ReadWrite", "None"
- `kubeletDiskType` (string) - "OS" or "Temporary"
- `storageProfile` (dynamic) - "ManagedDisks", "StorageAccount"
- `mode` (string) - System or User
- `distro` (string) - OS distribution
- `log` (string) - **Full JSON config** (contains additional fields like `osDiskType`)

**⚠️ Important**: `osDiskType` is NOT a top-level column! Extract from `log` field:
```kql
| extend logd = todynamic(log)
| extend osDiskType = tostring(logd.osDiskType)
```

**Example Query (Optimized):**
```kql
cluster('akshuba.centralus').database('AKSprod').AgentPoolSnapshot
| where PreciseTimeStamp > ago(3d)
| where subscription contains '{subscriptionId}'
| where clusterName == '{clusterName}'
| where name == '{nodePoolName}'
| top 1 by PreciseTimeStamp desc
| project PreciseTimeStamp, poolName=name, vmSize, osDiskSizeGB, osDiskCaching, 
    kubeletDiskType, storageProfile, enableAutoScaling, minCount, maxCount, 
    orchestratorVersion, osType, mode, distro
```

**Example Query (with osDiskType from log):**
```kql
cluster('akshuba.centralus').database('AKSprod').AgentPoolSnapshot
| where PreciseTimeStamp > ago(3d)
| where subscription == '{subscriptionId}'
| where clusterName == '{clusterName}'
| top 1 by PreciseTimeStamp desc
| extend logd = todynamic(log)
| project name, vmSize, osDiskSizeGB, osDiskCaching,
    osDiskType = tostring(logd.osDiskType),
    diffDiskSettings = logd.diffDiskSettings
```

### AutoUpgraderEvents
**Purpose**: Auto-upgrade operation logs
**Key Fields**:
- `resourceName` (string) - Cluster name
- `msg` (string) - Event message
- `messageType` (string)
- `operationID` (string)

### RemediatorEvent
**Purpose**: Node auto-remediation events (reimage, redeploy, etc.)
**Key Fields**:
- `ccpNamespace` (string) - **CCP namespace** (**use for filtering - NOT clusterName**)
- `resourceName` (string) - Cluster name
- `agentPoolName` (string) - Node pool name
- `operationName` (string) - Operation type
- `reason` (string) - Remediation reason
- `remediation` (string) - Remediation action taken
- `state` (string) - Operation state
- `msg` (string) - Log message
- `error` (string) - Error details if failed
- `PreciseTimeStamp` (datetime)

**⚠️ Important**: This table does NOT have a `clusterName` column. Use `ccpNamespace` for filtering!

**Example Query:**
```kql
cluster('akshuba.centralus').database('AKSprod').RemediatorEvent
| where PreciseTimeStamp between (datetime('{startTime}') .. datetime('{endTime}'))
| where ccpNamespace == '{ccpNamespace}'
| project PreciseTimeStamp, operationName, agentPoolName, reason, state, msg, remediation
| order by PreciseTimeStamp desc
| take 20
```

### AKSAlertmanager
**Purpose**: Prometheus alerts for cluster health monitoring
**Key Fields** (top-level columns - no need to parse from log):
- `cluster_id` (string) - CCP namespace / cluster ID (**use for filtering**)
- `alertname` (string) - Alert name (e.g., "NodeNotReady", "APIServerDown")
- `severity` (string) - "critical", "warning", "info"
- `status` (string) - "firing" or "resolved"
- `message` (string) - Alert message
- `description` (string) - Alert description
- `summary` (string) - Alert summary
- `startsAt` (string) - ISO timestamp when alert started
- `endsAt` (string) - ISO timestamp when alert ended
- `alert_labels` (dynamic) - Additional labels (node, pod, etc.)
- `alert_annotations` (dynamic) - Alert annotations
- `node` (string) - Node name (if applicable)
- `nodepool` (string) - Node pool name
- `PreciseTimeStamp` (datetime)
- `UnderlayName` (string)
- `log` (string) - Raw log (usually not needed)

**⚠️ Note**: Unlike many other tables, AKSAlertmanager has alert fields as **top-level columns**. No need to use `todynamic(log)`!

**Example Query (Optimized - use summarize to avoid large results):**
```kql
cluster('akshuba.centralus').database('AKSprod').AKSAlertmanager
| where PreciseTimeStamp between (datetime('{startTime}') .. datetime('{endTime}'))
| where cluster_id == '{ccpNamespace}'
| where status == 'firing'
| summarize count() by alertname, severity
| order by count_ desc
| limit 20
```

**Common Alert Names:**
| Category | Alerts |
|----------|--------|
| API Server | `APIServerDown`, `ClientGoHighErrorRate`, `KubeAPIErrorsHigh` |
| Nodes | `NodeNotReady`, `NodeMemoryPressure`, `NodeDiskPressure` |
| Certificates | `CertificateExpired`, `CertificateExpiringSoon` |
| Etcd | `EtcdHighCommitDurations`, `EtcdMembersDown` |
| Remediation | `ReimageNode`, `RedeployNode` |
| DaemonSets | `KubeProxyDaemonSetNotScheduled`, `AzureFileDaemonSetNotReady` |

## AKSccplogs Database Tables

### KubeAudit
**Purpose**: Kubernetes API audit logs
**Key Fields**:
- `auditID` (string)
- `user` (dynamic) - User information
- `verb` (string) - get, list, create, update, delete, patch, watch
- `objectRef` (dynamic) - Resource being accessed
- `requestURI` (string)
- `responseStatus` (dynamic)
- `stage` (string) - ResponseComplete, RequestReceived
- `PreciseTimeStamp` (datetime)
- `UnderlayName` (string)
- `cluster_id` (string)

**Note**: `KubeAudit` is a direct table in AKSccplogs — query it directly for efficient structured access. The same data is also accessible via `ControlPlaneEvents` or `ControlPlaneEventsNonShoebox` with `| where category == 'kube-audit'`, but direct `KubeAudit` access is preferred.

### ControlPlaneEvents / ControlPlaneEventsNonShoebox
**Purpose**: Control plane event logs (including audit)
**Key Fields**:
- `ccpNamespace` (string) - **Use namespace from ManagedClusterSnapshot**
- `category` (string) - 'kube-audit', 'kube-controller-manager', etc.
- `operationName` (string)
- `properties` (string) - JSON string containing log details
- `resourceId` (string)
- `PreciseTimeStamp` (datetime)

**Common pattern to parse properties**:
```kql
| extend props = todynamic(properties)
| extend logMessage = tostring(props.log)
```

### AKSKubeEvents / KubeSystemEvents
**Purpose**: Kubernetes events from the cluster
**Key Fields**:
- `namespace` (string) - **Use ccpNamespace for cluster filtering** (**required**)
- `kind` (string) - Resource kind: "Node", "Pod", "Deployment", etc.
- `name` (string) - Resource name (node name, pod name, etc.)
- `reason` (string) - Event reason
- `message` (string) - Event description
- `type` (string) - "Normal", "Warning", "Error"
- `reportingController` (string) - Component reporting the event
- `reportingInstance` (string) - Instance reporting (often node name)
- `lastObservedTime` (datetime) - When event was last observed
- `PreciseTimeStamp` (datetime)
- `cluster_id` (string)
- `resourceId` (string)

**Example Query (Node events - Optimized):**
```kql
cluster('akshuba.centralus').database('AKSccplogs').AKSKubeEvents
| where PreciseTimeStamp between (datetime('{startTime}') .. datetime('{endTime}'))
| where namespace == '{ccpNamespace}'
| where kind == 'Node'
| where reason has_any ('NodeNotReady', 'NodeReady', 'RegisteredNode', 'ScaleDown', 'DeletingNode')
| project PreciseTimeStamp, NodeName=name, Reason=reason, Type=type, Message=message
| order by PreciseTimeStamp asc
| take 50
```

**Example Query (Pod scheduling issues - Optimized):**
```kql
cluster('akshuba.centralus').database('AKSccplogs').AKSKubeEvents
| where PreciseTimeStamp between (datetime('{startTime}') .. datetime('{endTime}'))
| where namespace == '{ccpNamespace}'
| where kind == 'Pod'
| where reason has_any ('FailedScheduling', 'Evicted', 'FailedMount', 'BackOff')
| project PreciseTimeStamp, PodName=name, Reason=reason, Type=type, Message=message
| take 30
```

**Common Node Event Reasons:**
| Reason | Meaning |
|--------|---------|
| `NodeNotReady` | Node transitioned to NotReady |
| `FreezeScheduled` | Azure scheduled maintenance event |
| `RebootScheduled` | Azure scheduled reboot |
| `TerminateScheduled` | Node termination scheduled |
| `ContainerdStart` | Container runtime restarting |
| `CoreDNSUnreachable` | DNS connectivity issues |
| `NodeHasSufficientMemory` | Memory pressure resolved |
| `NodeHasNoDiskPressure` | Disk pressure resolved |

**Common Pod Event Reasons:**
| Reason | Meaning |
|--------|---------|
| `FailedScheduling` | Pod couldn't be scheduled |
| `Evicted` | Pod evicted from node |
| `OOMKilled` | Container killed due to OOM |
| `BackOff` | Container crash loop |
| `Unhealthy` | Probe failed |
| `FailedMount` | Volume mount failed |

### ClusterAutoscaler
**Purpose**: Cluster autoscaler logs
**Key Fields**:
- `namespace` (string) - **Use ccpNamespace** (**required for filtering**)
- `log` (string) - Log message
- `pod` (string)
- `PreciseTimeStamp` (datetime)

**Example Query (Optimized):**
```kql
cluster('akshuba.centralus').database('AKSccplogs').ClusterAutoscaler
| where PreciseTimeStamp between (datetime('{startTime}') .. datetime('{endTime}'))
| where namespace == '{ccpNamespace}'
| where log has_any ('ScaleUp', 'ScaleDown', 'timeout', 'Timeout', 'unregistered', 'failed', 'error')
| project PreciseTimeStamp, log
| order by PreciseTimeStamp asc
| take 30
```

**Example Query (Summarize node group status):**
```kql
cluster('akshuba.centralus').database('AKSccplogs').ClusterAutoscaler
| where PreciseTimeStamp between (datetime('{startTime}') .. datetime('{endTime}'))
| where namespace == '{ccpNamespace}'
| where log contains 'clusterstate.go' and log contains '{nodePoolName}'
| project PreciseTimeStamp, log
| take 30
```

### CloudControllerManager
**Purpose**: Cloud controller manager logs
**Key Fields**:
- `cluster_id` (string) - **Use for cluster filtering** (NOT `namespace`)
- `namespace` (string) - CCP namespace (available but `cluster_id` is preferred filter)
- `log` (string) - Log message
- `pod_name` (string) - Pod name (also `pod` field available)
- `pod` (string) - Pod name (same pod, alternative field name)

### CSIAzureDiskController / CSIAzureFileController / CSIAzureBlobController
**Purpose**: CSI driver logs
**Key Fields**:
- `namespace` (string) - **Use ccpNamespace**
- `log` (string) - Log message
- `level` (string)
- `pod` (string)
- `file` (string) - Source code file

### Etcd
**Purpose**: Etcd database logs
**Key Fields**:
- `namespace` (string) - **Use ccpNamespace**
- `log` (string) - JSON structured log message
- `level` (string)
- `pod` (string)
- `cluster_id` (string)
- `PreciseTimeStamp` (datetime)

**Common Log Patterns for Pressure Detection:**
- `"apply request took too long"` - Indicates etcd slowness
- `"took"` field shows actual duration (normal < 100ms)
- `"expected-duration":"100ms"` - Baseline expectation
- Operations on `/registry/minions/` = node operations
- Operations on `/registry/pods/` = pod operations

### Guard
**Purpose**: AAD authentication logs
**Key Fields**:
- `log` (string)
- `level` (string)
- `pod` (string)

### KubeControllerManager
**Purpose**: Kubernetes controller manager logs
**Key Fields**:
- `cluster_id` (string) - **Use ccpNamespace for filtering**
- `pod_name` (string) - Pod name
- `namespace` (string)
- `log` (string) - Log message (**Note: field is `log`, NOT `msg`**)
- `time` (datetime)
- `PreciseTimeStamp` (datetime)

> **Note**: This table was incorrectly referenced as `KubeControllerManagerLogs` in some older documentation. The correct table name is `KubeControllerManager`.

### KubeScheduler
**Purpose**: Kubernetes scheduler logs
**Key Fields**:
- `cluster_id` (string) - **Use ccpNamespace for filtering**
- `pod_name` (string) - Pod name
- `namespace` (string)
- `log` (string) - Log message
- `time` (datetime)
- `PreciseTimeStamp` (datetime)

### KonnectivityServer
**Purpose**: Konnectivity server logs (API server to node tunnel)
**Key Fields**:
- `namespace` (string) - **Use ccpNamespace**
- `log` (string) - Log message
- `pod` (string) - Pod name (**Note: NOT pod_name**)
- `container` (string)
- `hostMachine` (string)
- `PreciseTimeStamp` (datetime)

### CCPKonnectivityAgent
**Purpose**: Konnectivity agent logs (runs on customer nodes)
**Key Fields**:
- `namespace` (string) - **Use ccpNamespace**
- `log` (string) - Log message
- `pod` (string) - Pod name (**Note: NOT pod_name**)
- `container` (string)
- `hostMachine` (string)
- `PreciseTimeStamp` (datetime)

## AKSinfra Database Tables

**IMPORTANT**: AKSinfra contains data about **AKS underlay infrastructure**, NOT customer worker nodes!

**Underlay Infrastructure**:
- **Master nodes**: Run the underlay Kubernetes control plane
- **Infra nodes**: Run AKS infrastructure services (nanny, scheduler)  
- **Agent nodes**: Run customer control plane (CCP) pods

**Customer worker nodes** (the nodes customers see in `kubectl get nodes`) are **NOT** tracked in AKSinfra. They are in the customer's subscription.

### ProcessInfo
**Purpose**: Container and process information from **underlay nodes** (NOT customer worker nodes)
**Key Fields**:
- `UnderlayName` (string)
- `Host` (string) - Node name
- `PodName` (string)
- `PodNamespace` (string)
- `State` (string)
- `Status` (string)
- `CPUUtil` (real)
- `MemUtil` (real)
- `log` (string)

### UnderlayNodeInfo
**Purpose**: Node health and configuration for **underlay infrastructure nodes**
**Key Fields**:
- `UnderlayName` (string)
- `HostName` (string)
- `K8sReady`, `K8sMemoryPressure`, `K8sDiskPressure` (string)
- `K8sVersion` (string)
- `CPUCores`, `CPULoad1`, `CPULoad5`, `CPULoad15` (long/real)
- `MemAvail`, `MemUsed`, `MemTotal` (long)
- `DockerVersion` (string)

### UnderlayNanny
**Purpose**: Underlay infrastructure remediation service logs
**Key Fields**:
- `underlay` (string)
- `msg` (string)
- `signal` (string)
- `remediation_node` (string)
- `level` (string)

## AKSmetrics Database Tables

### KubePodStatusReason / KubePodContainerStatusReady
**Purpose**: Pod and container metrics
**Key Fields**:
- `Timestamp` (datetime)
- `Pod` (string)
- `Container` (string)
- `Namespace` (string)
- `Host` (string)
- `UnderlayName` (string)
- `Value` (real)

## Common Patterns

### Time Filtering
```kql
| where PreciseTimeStamp between (datetime('2026-01-28T10:00:00Z') .. datetime('2026-01-28T12:00:00Z'))
| where PreciseTimeStamp >= ago(2h)
```

### Cluster Filtering
```kql
// For RP tables (AKSprod)
| where subscriptionID == '{sub-id}'
| where resourceGroupName == '{rg-name}'
| where resourceName == '{cluster-name}'  // or clusterName

// For control plane tables (AKSccplogs)
| where namespace == '{ccpNamespace}'  // Get from ManagedClusterSnapshot
| where ccpNamespace == '{ccpNamespace}'
```

### Dynamic Field Parsing
```kql
// Parse JSON string to dynamic
| extend props = todynamic(properties)
| extend logMsg = tostring(props.log)

// Extract from nested dynamic object
| extend version = tostring(orchestratorProfile.orchestratorVersion)
```

### Correlation
```kql
// By operationID (RP traces)
union cluster('akshuba.centralus').database('AKSprod').FrontEndContextActivity, cluster('akshuba.centralus').database('AKSprod').AsyncContextActivity
| where operationID == '{operation-id}'

// By cluster (across tables)
let ccpNS = '{ccpNamespace}';
union cluster('akshuba.centralus').database('AKSccplogs').AKSKubeEvents, cluster('akshuba.centralus').database('AKSccplogs').ClusterAutoscaler
| where namespace == ccpNS
```
