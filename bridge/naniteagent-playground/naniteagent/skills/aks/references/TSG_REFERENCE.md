# AKS Troubleshooting Guide (TSG) Reference

This document contains key insights and patterns learned from the official AKS TSG repository at:
`https://msazure.visualstudio.com/CloudNativeCompute/_git/aks-troubleshooting-guide/doc/tsg`

Last Updated: 2026-01-29

---

## Cluster Autoscaler & Node Provisioning

### Architecture
- **Location:** Cluster Autoscaler pod runs in **cx-underlay** (not visible to customers)
- **Access:** Customers can only debug via:
  - ConfigMap: `kubectl describe configmap cluster-autoscaler-status -n kube-system`
  - LogAnalytics/Container Insights
  - Control plane logs in Kusto

### Key Concepts

**Unregistered Nodes:**
- Definition: VMs that exist in Azure but have no corresponding Kubernetes node object
- Timeout: 15 minutes (configurable via `--max-node-provision-time`)
- Recovery: After timeout, Cluster Autoscaler deletes the VM and retries scale-up

**Scale-Up Flow:**
1. Pending pods trigger scheduler simulation
2. Autoscaler picks suitable nodepool (configurable via `--expander`)
3. Autoscaler calls Azure API to increase VMSS/VMS size
4. VMs provision in Azure
5. Nodes bootstrap and join cluster
6. If timeout exceeded → Delete unregistered nodes → Retry

**Scale-Down Conditions (node won't scale down if):**
- Node group at minimum size
- Node has `cluster-autoscaler.kubernetes.io/scale-down-disabled` annotation
- Node unneeded for <10 minutes (`--scale-down-unneeded-time`)
- Scale-up in last 10 minutes (`--scale-down-delay-after-add`)
- Failed scale-down in last 3 minutes (`--scale-down-delay-after-failure`)
- Node utilization >50% (`--scale-down-utilization-threshold`)
  - **Important:** Utilization = sum of pod requests, NOT actual usage

### Common Issues

**"No expansion options" in logs:**
- No nodepool can fit the pending pod (resource constraints, labels, taints)
- Nodepool already at maximum count
- Previous scale-up failed → exponential back-off active

**Scale-up issued but nodes not appearing:**
- Check NPS logs for scale operation failures
- Check node CSE (Custom Script Extension) for failures
- Check network connectivity to API server
- After 15 minutes, unregistered nodes are deleted automatically

---

## CNI (Container Network Interface)

### BYO CNI

**Expected Behavior:**
- Nodes start in `NotReady` state with error: `"cni plugin not initialized"`
- This is **NORMAL** and **EXPECTED** until customer installs their CNI
- Pods without `node.kubernetes.io/not-ready:NoSchedule` toleration won't schedule

**Supportability:**
- Microsoft does **NOT** support CNI-related issues for BYO CNI clusters
- Public docs: https://docs.microsoft.com/en-us/azure/aks/use-byo-cni

**Detection:**
- CLI: `--network-plugin=none`
- MC: `networkProfile.networkPlugin == "none"`
- ASI: Shows "Network Plugin: None"

**Customer Responsibility:**
- Install and maintain CNI (Cilium, Calico, etc.)
- Troubleshoot all pod-to-pod networking issues
- Configure network policies

---

### Azure CNI Overlay

**Architecture:**
- Uses routing domains instead of route tables (like Kubenet)
- Pods get IPs from overlay network space (e.g., 100.64.0.0/10)
- No IP exhaustion in node subnet

**Components:**
1. **DNC/DNC-RC:** Runs in CCP, manages IP allocations
2. **CNS (Container Network Service):** Daemonset on nodes, allocates IPs to pods
3. **NodeNetworkConfiguration (NNC):** CR per node with IP range assignments

**Required Node Labels:**
```
kubernetes.azure.com/podnetwork-type: overlay
kubernetes.azure.com/nodenetwork-vnetguid: <vnet-resource-guid>
```

**Verification Commands:**
```bash
# Check NNCs (should be 1 per node)
kubectl get nnc -A

# Check CNS daemonset
kubectl get ds -n kube-system azure-cns

# Check NNC IP ranges
kubectl get nnc <node-nnc-name> -o yaml
```

**Common Issues:**

1. **Pods stuck in ContainerCreating:**
   - Error: `"Failed to get IP address from CNS ... connection refused"`
   - Cause: CNS not running or crashed
   - Fix: Check CNS pod logs, restart CNS if needed

2. **CNS in CrashLoopBackoff with "conflist checksum validation failed":**
   - Cause: Race condition with service mesh CNI chaining (Istio/Linkerd)
   - Occurs after node image upgrade
   - Mitigation: Manually reimage node or disable CNI chaining
   - ICM: #477306895 (Istio), #486529812 (Linkerd)

3. **No NNCs created:**
   - Check DNC-RC logs in ControlPlaneEventsAll (category: "requestcontroller")
   - Escalate to Container Networking team

4. **Shared subnet with Kubenet clusters:**
   - Kubenet's route table rules interfere with Overlay traffic
   - Symptom: Pod-to-pod calls timeout
   - Solution: Use separate subnets for different CNI types

**Kusto Queries:**

DNC-RC logs:
```kql
union cluster('akshuba.centralus').database('AKSccplogs').ControlPlaneEvents, cluster('akshuba.centralus').database('AKSccplogs').ControlPlaneEventsNonShoebox
| where PreciseTimeStamp > ago(1h)
| where ccpNamespace == "{ccpNamespace}"
| where category == "requestcontroller"
| extend logData = parse_json(tostring(parse_json(properties).log))
| project PreciseTimeStamp, logData.level, logData.component, logData.msg
```

---

### Azure CNI (Classic)

**IP Allocation:**
- Each node pre-allocates IPs: `maxPods + overhead`
- IPs consumed from node subnet
- Can lead to subnet exhaustion in large clusters

**Common Issues:**
- Subnet IP exhaustion → New nodes can't provision
- Calculation: `(nodeCount × maxPods) + overhead ≈ needed IPs`

---

### Kubenet

**Architecture:**
- Uses route tables for pod routing
- Each node gets a /24 subnet from clusterSubnet (e.g., 10.244.0.0/24)
- Node's PodCIDR field populated with assigned subnet

**Common Issues:**
- Route table rules missing or incorrect
- NSG blocking pod traffic
- Route table attached to wrong subnet

---

## Node Lifecycle & Health Monitoring

### Node Problem Detector Events

The Node Problem Detector (NPD) runs on each node and reports issues as Kubernetes events:

**Event Reasons:**
- `CoreDNSUnreachable`: Can't reach DNS service → Network not initialized
- `KubeletServingCertificateInvalid`: Certificate issues → Bootstrap failure
- `NoVMEventScheduled`: IMDS query failed → Can't reach Azure metadata (169.254.169.254)
- `PreemptScheduled`, `TerminateScheduled`, etc.: IMDS queries for VM events
- `FreezeScheduled`, `RebootScheduled`: Node health check plugin timeouts

**Troubleshooting Pattern:**
1. Get node events: `kubectl get events --field-selector involvedObject.name=<node-name>`
2. Look for NPD warnings around the time of failure
3. IMDS failures often indicate network/routing problems
4. DNS failures indicate CNI not initialized

---

## Kusto Query Patterns

### Cluster Autoscaler Logs
```kql
union cluster('akshuba.centralus').database('AKSccplogs').ControlPlaneEvents, cluster('akshuba.centralus').database('AKSccplogs').ControlPlaneEventsNonShoebox
| where PreciseTimeStamp > ago(1h)
| where ccpNamespace == "{ccpNamespace}"
| where category == "cluster-autoscaler"
| extend logData = tostring(parse_json(properties).log)
| where logData !has "request.go" and logData !has "clusterstate.go:623"
| project PreciseTimeStamp, logData
| order by PreciseTimeStamp asc
```

### Node Lifecycle Events
```kql
cluster('akshuba.centralus').database('AKSccplogs').AKSKubeEvents
| where PreciseTimeStamp > ago(1h)
| where namespace == "{ccpNamespace}"
| where reason has_any ('NodeNotReady', 'DeletingNode', 'RegisteredNode', 'NodeReady')
| project PreciseTimeStamp, name, reason, message, type
| order by PreciseTimeStamp asc
```

### CNI Overlay - DNC-RC Logs
```kql
union cluster('akshuba.centralus').database('AKSccplogs').ControlPlaneEvents, cluster('akshuba.centralus').database('AKSccplogs').ControlPlaneEventsNonShoebox
| where PreciseTimeStamp > ago(1h)
| where ccpNamespace == "{ccpNamespace}"
| where category == "requestcontroller"
| extend logData = parse_json(tostring(parse_json(properties).log))
| project PreciseTimeStamp, logData.level, logData.component, logData.msg
```

---

## Escalation Paths

| Component | Team | Channel |
|-----------|------|---------|
| Cluster Autoscaler pod crashes | CAS SIG | Teams: Cluster Autoscaler SIG |
| Node provisioning failures | AKS-RP team | Wenxuan Wang, Renee Li, Wenjun Gao |
| Azure CNI/CNI Overlay | Container Networking | sig-container-networking |
| DNC/DNC-RC/CNS issues | Container Networking | CloudNet/ContainerNetworking |
| VMSS/VM creation failures | CRP team | Compute RP |
| Subnet/NSG/Route table | Azure Networking | SDN/Networking team |

---

## Reference Links

- [Cluster Autoscaler FAQ](https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/FAQ.md)
- [AKS Cluster Autoscaler Docs](https://docs.microsoft.com/en-us/azure/aks/cluster-autoscaler)
- [BYO CNI Wiki](https://msazure.visualstudio.com/CloudNativeCompute/_wiki/wikis/CloudNativeCompute.wiki/204722/BYO-CNI)
- [Azure CNI Overlay Wiki](https://dev.azure.com/msazure/CloudNativeCompute/_wiki/wikis/CloudNativeCompute.wiki/432365/Azure-CNI-Overlay-Migration)
- [TSG Repository](https://msazure.visualstudio.com/CloudNativeCompute/_git/aks-troubleshooting-guide?path=/doc/tsg)

---

## Key Timeouts & Defaults

| Parameter | Default Value | Description |
|-----------|---------------|-------------|
| `--max-node-provision-time` | 15 minutes | Time before unregistered node is deleted |
| `--scale-down-unneeded-time` | 10 minutes | How long node must be underutilized |
| `--scale-down-delay-after-add` | 10 minutes | Delay after scale-up before scale-down |
| `--scale-down-delay-after-failure` | 3 minutes | Delay after failed scale-down |
| `--scale-down-utilization-threshold` | 0.5 (50%) | Node utilization threshold for scale-down |
| `--scan-interval` | 10 seconds | How often autoscaler evaluates |

