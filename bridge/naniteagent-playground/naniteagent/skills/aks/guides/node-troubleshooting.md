# AKS Node Troubleshooting Guide

This guide covers troubleshooting node-related issues in AKS clusters, including node lifecycle, networking problems, and CNI configuration.

## When to Use This Guide

Use this guide when investigating:
- **Node not ready**: Nodes stuck in NotReady state
- **Node failures**: Nodes failing to register or crashing
- **Node provisioning issues**: VMs created but not joining the cluster
- **Unregistered nodes**: VMs exist in Azure but have no k8s node object

## Prerequisites

**Ask the user** for:
- Specific node names (if known)
- Time range when the issue occurred
- Symptoms observed (e.g., pods not scheduling, nodes disappearing)

**Database:** `AKSccplogs`

---

## Understanding Node Lifecycle

When Cluster Autoscaler scales up or nodes are provisioned:
1. VM created in Azure VMSS/VMS (visible in cloud provider)
2. Node boots and kubelet starts
3. CNI initialization (network config in `/etc/cni/net.d/`)
4. Node registers with Kubernetes API server
5. Node transitions to Ready state

**Unregistered Nodes:** VMs that exist in Azure but have no corresponding k8s node object
- Default timeout: **15 minutes** (`--max-node-provision-time`)
- If node doesn't register within timeout → Cluster Autoscaler deletes VM and retries

---

## Step 1: Check Kubernetes Events for Node Lifecycle

```kql
cluster('akshuba.centralus').database('AKSccplogs').AKSKubeEvents
| where PreciseTimeStamp between (datetime('{startTime}') .. datetime('{endTime}'))
| where namespace == '{ccpNamespace}'
| where name has_any ('{nodeName1}', '{nodeName2}')
   or reason has_any ('NodeNotReady', 'DeletingNode', 'RegisteredNode', 'NodeReady',
                      'NodeHasSufficientMemory', 'NodeHasNoDiskPressure',
                      'ContainerdStart', 'CoreDNSUnreachable', 'KubeletServingCertificateInvalid')
| project PreciseTimeStamp, name, reason, message, type
| order by PreciseTimeStamp asc
| take 100
```

**Key Event Reasons to Investigate:**
- `DeletingNode` + "does not exist in cloud provider" → VM missing from Azure
- `CoreDNSUnreachable` → Network not initialized, can't reach DNS
- `KubeletServingCertificateInvalid` → Certificate issues during node bootstrap
- `NoVMEventScheduled` with "IMDS query failed" → Can't reach Azure metadata service (169.254.169.254)
- `ContainerdStart` → Container runtime restarting (may indicate issues)
- `NodeHasSufficientMemory`, `NodeHasNoDiskPressure` → Positive health signals

---

## Step 2: Check CloudControllerManager for Node/VMSS Sync Issues

```kql
cluster('akshuba.centralus').database('AKSccplogs').CloudControllerManager  
| where PreciseTimeStamp between (datetime('{startTime}') .. datetime('{endTime}'))
| where namespace == '{ccpNamespace}' 
| where log has_any ('{nodeName1}', '{nodeName2}', 'instance not found', 'vmNotFound')
   or log has_any ('Unable to find node', 'InstanceShutdownByProviderID')
| project PreciseTimeStamp, log, pod_name
| order by PreciseTimeStamp asc
| take 100
```

**Key Log Patterns:**
- `"Unable to find node ... instance not found"` → Node registered in k8s but missing from Azure VMSS
- `"InstanceShutdownByProviderID gets power status"` → Checking VM power state
- `"InstanceShutdownByProviderID gets provisioning state 'Creating'"` → VM still provisioning in Azure
- `"Failed to reconcile LoadBalancer ... instance not found"` → LB update failing due to missing VMs

---

## Step 3: Verify Cluster Network Configuration

Use ManagedClusterSnapshot query (Step 4) to check:
- `networkPlugin`: "azure" (Azure CNI), "kubenet", or empty/"none" (BYO CNI)
- `networkPolicy`: "azure", "calico", "cilium", etc.
- `networkPluginMode`: "overlay" (Azure CNI Overlay)
- `maxPodsPerNode`: Affects IP allocation (Azure CNI pre-allocates IPs)
- `addonProfiles`: Check CNI-related addons

---

## Step 4: For Cluster Autoscaler Scale-Up Issues

Check Cluster Autoscaler logs in ControlPlaneEvents:

```kql
union cluster('akshuba.centralus').database('AKSccplogs').ControlPlaneEvents, cluster('akshuba.centralus').database('AKSccplogs').ControlPlaneEventsNonShoebox
| where PreciseTimeStamp between (datetime('{startTime}') .. datetime('{endTime}'))
| where ccpNamespace == '{ccpNamespace}'
| where category == 'cluster-autoscaler'
| extend logData = tostring(parse_json(properties).log)
| where logData !has 'request.go' and logData !has 'clusterstate.go:623'  // Filter noise
| project PreciseTimeStamp, logData
| order by PreciseTimeStamp asc
| take 100
```

**Look for:**
- `"Estimated N nodes needed in {nodepool}"` → Scale-up triggered
- `"Final scale-up plan"` → Which nodepool is scaling
- `"Successfully scaled up"` → Scale-up completed
- `"No expansion options"` → No nodepool can accommodate pending pods
- `"longUnregistered"` → Nodes taking >15min to join, will be deleted

---

## Analysis Guide by Network Plugin

### 1. Azure CNI (networkPlugin: "azure")

- **Symptoms:** Nodes stuck in NotReady, pods in ContainerCreating
- **Common causes:**
  - IP address exhaustion in subnet (check subnet available IPs)
  - CNI binary download failures (check node logs for download errors)
  - Azure CNI configuration issues
- **Verification:**
  - Check if pods show: `"Failed to create pod sandbox ... IPAM Invoker Add failed"`
  - Verify subnet has available IPs: `(maxPods × nodeCount) + overhead`

### 2. Azure CNI Overlay (networkPluginMode: "overlay")

- **Components:** DNC/DNC-RC (in CCP) + CNS (daemonset on nodes)
- **Required node labels:**
  ```
  kubernetes.azure.com/podnetwork-type: overlay
  kubernetes.azure.com/nodenetwork-vnetguid: {vnet-guid}
  ```
- **Troubleshooting:**
  - Check NodeNetworkConfiguration CRs: `kubectl get nnc -A`
  - One NNC should exist per node
  - Check CNS daemonset: `kubectl get ds -n kube-system azure-cns`
  - Check DNC-RC logs in ControlPlaneEventsAll with category "requestcontroller"
- **Common errors:**
  - `"Failed to get IP address from CNS ... connection refused"` → CNS not running
  - `"conflist checksum validation failed"` → Race with service mesh CNI chaining

### 3. BYO CNI (networkPlugin: "none" or empty)

- **Expected behavior:** Nodes start as `NotReady` until customer installs CNI
- **Error message is NORMAL:** `"cni plugin not initialized"`
- **Supportability:** Microsoft does NOT support BYO CNI networking issues
- **Customer action required:** Install their chosen CNI (Cilium, Calico, etc.)
- **Verification:** Check if customer has installed CNI daemonset

### 4. Kubenet (networkPlugin: "kubenet")

- Uses route tables for pod routing
- Check route table in node subnet for proper routes
- Each node gets a /24 from clusterSubnet

---

## Step 5: Check Konnectivity and Webhook Issues

When nodes are NotReady due to CNS/CNI failures, the root cause may be **webhook timeouts** caused by Konnectivity proxy issues.

### Check for Webhook Timeouts

```kql
union cluster('akshuba.centralus').database('AKSccplogs').ControlPlaneEvents, cluster('akshuba.centralus').database('AKSccplogs').ControlPlaneEventsNonShoebox
| where PreciseTimeStamp between (datetime('{startTime}') .. datetime('{endTime}'))
| where ccpNamespace == '{ccpNamespace}'
| where category == 'kube-apiserver'
| extend logData = tostring(parse_json(properties).log)
| where logData has_any ('webhook', 'context deadline', 'ccp-webhook', 'timeout')
| project PreciseTimeStamp, logData
| order by PreciseTimeStamp asc
| take 100
```

### Check Konnectivity Proxy Error Rate

```kql
union cluster('akshuba.centralus').database('AKSccplogs').ControlPlaneEvents, cluster('akshuba.centralus').database('AKSccplogs').ControlPlaneEventsNonShoebox
| where PreciseTimeStamp between (datetime('{startTime}') .. datetime('{endTime}'))
| where ccpNamespace == '{ccpNamespace}'
| where category == 'kube-apiserver'
| extend logData = tostring(parse_json(properties).log)
| where logData has 'proxy error'
| summarize count() by bin(PreciseTimeStamp, 5m)
| order by PreciseTimeStamp asc
```

### Check Konnectivity Server Logs

```kql
cluster('akshuba.centralus').database('AKSccplogs').KonnectivityServer
| where PreciseTimeStamp between (datetime('{startTime}') .. datetime('{endTime}'))
| where namespace == '{ccpNamespace}'
| where log has_any ('error', 'timeout', 'failed', 'close', 'disconnect')
| project PreciseTimeStamp, log, pod
| order by PreciseTimeStamp asc
| take 50
```

**Note**: Use `pod` column, NOT `pod_name` for KonnectivityServer table.

### Check Konnectivity Agent Logs

```kql
cluster('akshuba.centralus').database('AKSccplogs').CCPKonnectivityAgent
| where PreciseTimeStamp between (datetime('{startTime}') .. datetime('{endTime}'))
| where namespace == '{ccpNamespace}'
| where log has_any ('error', 'timeout', 'disconnect', 'dial')
| project PreciseTimeStamp, log, pod
| order by PreciseTimeStamp asc
| take 50
```

**Note**: Use `pod` column, NOT `pod_name` for CCPKonnectivityAgent table.

### Key Log Patterns:
- `"proxy error from localhost:9443"` → Konnectivity proxy overloaded/failing
- `"context deadline exceeded"` → Webhook timeout (usually 10s for AKS webhook)
- `"Failed calling webhook, failing closed"` → Webhook blocked operation (failurePolicy: Fail)
- `"500 Internal Server Error"` → Konnectivity server error

### Webhook-CNI Failure Chain

When webhooks timeout during large scale-ups:
1. Konnectivity proxy saturated → API-to-node tunnel fails
2. Webhook calls timeout → Pod creation blocked
3. azure-cns DaemonSet pods can't start on new nodes
4. CNI not initialized → Nodes stuck NotReady

---

## Step 6: Check API Server and Etcd Pressure

When large scale-ups cause node NotReady issues, the root cause may be **control plane resource exhaustion**. API server slowness and etcd pressure can cascade to webhook timeouts and CNI failures.

### Check Etcd Slow Requests

```kql
cluster('akshuba.centralus').database('AKSccplogs').Etcd
| where PreciseTimeStamp between (datetime('{startTime}') .. datetime('{endTime}'))
| where namespace == '{ccpNamespace}'
| where log has_any ('slow', 'took too long', 'overload', 'apply request took')
| project PreciseTimeStamp, log
| order by PreciseTimeStamp asc
| take 50
```

**Key Patterns:**
- `"apply request took too long"` with `took` > 100ms → Etcd under pressure
- Normal: < 100ms, Warning: 100-500ms, Critical: > 500ms
- Operations on `/registry/minions/` (nodes) and `/registry/pods/` are common bottlenecks

### Check API Server Timeout/Throttling

```kql
union cluster('akshuba.centralus').database('AKSccplogs').ControlPlaneEvents, cluster('akshuba.centralus').database('AKSccplogs').ControlPlaneEventsNonShoebox
| where PreciseTimeStamp between (datetime('{startTime}') .. datetime('{endTime}'))
| where ccpNamespace == '{ccpNamespace}'
| where category == 'kube-apiserver'
| extend logData = tostring(parse_json(properties).log)
| where logData has_any ('timeout', 'too many requests', '429', 'overload', 'throttl', 'dropped', 'queue')
| project PreciseTimeStamp, logData
| order by PreciseTimeStamp asc
| take 50
```

### Analyze API Server Request Latency Trends

```kql
union cluster('akshuba.centralus').database('AKSccplogs').ControlPlaneEvents, cluster('akshuba.centralus').database('AKSccplogs').ControlPlaneEventsNonShoebox
| where PreciseTimeStamp between (datetime('{startTime}') .. datetime('{endTime}'))
| where ccpNamespace == '{ccpNamespace}'
| where category == 'kube-apiserver'
| extend logData = tostring(parse_json(properties).log)
| where logData has 'Trace' and logData has 'ms)'
| parse logData with * "total time: " latencyMs:long "ms" *
| where latencyMs > 1000
| summarize count(), avgLatency=avg(latencyMs), maxLatency=max(latencyMs) by bin(PreciseTimeStamp, 5m)
| order by PreciseTimeStamp asc
```

### Control Plane Pressure Failure Chain

When control plane is under pressure during large scale-ups:

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. LARGE SCALE-UP TRIGGERED (many nodes at once)                    │
│    • Massive node heartbeats, pod scheduling, lease updates         │
│    • Many concurrent API requests                                   │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 2. ETCD OVERLOADED                                                  │
│    • Request latency: 100ms → 500-1600ms (5-16x slower)             │
│    • Read operations for nodes/pods taking too long                 │
│    • Key indicator: "apply request took too long"                   │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 3. API SERVER SLOW/UNRESPONSIVE                                     │
│    • Webhook calls timeout (depend on API server)                   │
│    • Konnectivity proxy errors (500 Internal Server Error)          │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 4. WEBHOOK FAILURES                                                 │
│    • aks-webhook-admission-controller times out                     │
│    • azure-cns pods can't be created on new nodes                   │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 5. CNI NOT INITIALIZED → NODES NotReady                             │
│    • "cni plugin not initialized" error                             │
│    • CoreDNS unreachable                                            │
└─────────────────────────────────────────────────────────────────────┘
```

### Recommendations for Control Plane Pressure

| Issue | Recommendation |
|-------|----------------|
| Basic tier with large cluster | Upgrade to **Standard tier** for better API server scaling |
| Large burst scale-ups | Limit with `max-nodes-per-scale-up` in autoscaler profile |
| Frequent etcd slowness | Review cluster size, consider splitting workloads |
| 100+ nodes | Standard/Premium tier recommended |

---

## Common Root Causes Summary

| Symptom | Likely Cause | Investigation |
|---------|--------------|---------------|
| Nodes deleted "does not exist in cloud provider" | VM failed to provision or was deleted from Azure | Check Azure Activity Log, VMSS operations |
| CoreDNS unreachable from node | CNI not initialized, no pod networking | Check CNI installation, node logs |
| IMDS timeout | Network/routing broken, can't reach 169.254.169.254 | Check NSG rules, routes, node network config |
| Pods stuck ContainerCreating | CNI IP allocation failure | Check CNI logs, available IPs, CNS/DNC |
| Node >15min unregistered | CSE failure, kubelet crash, network blocking API | Check node logs, CSE output, firewall rules |
| Webhook timeout with "ccp-webhook" | Konnectivity proxy overload | Check proxy error rate, scale-up size |
| azure-cns pods not starting | Webhook blocking pod creation | Check webhook timeout logs, failurePolicy |
| Etcd "apply request took too long" | Control plane overload during scale-up | Check etcd latency, consider Standard tier |
| Many nodes NotReady after scale-up | API server pressure + webhook cascade | Check etcd logs, proxy errors, scale batch size |
