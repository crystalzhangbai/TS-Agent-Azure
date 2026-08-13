# AKS Architecture - Understanding Nodes and Databases

## AKS Cluster Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CUSTOMER SUBSCRIPTION                         │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         Customer Managed Cluster (MC_* RG)                 │ │
│  │                                                            │ │
│  │  ┌──────────────────┐  ┌──────────────────┐              │ │
│  │  │  Worker Node 1   │  │  Worker Node 2   │  ...         │ │
│  │  │  (Data Plane)    │  │  (Data Plane)    │              │ │
│  │  │  - Kubelet       │  │  - Kubelet       │              │ │
│  │  │  - Customer Pods │  │  - Customer Pods │              │ │
│  │  │  - CNI Plugin    │  │  - CNI Plugin    │              │ │
│  │  └──────────────────┘  └──────────────────┘              │ │
│  │         ↑ ↑ ↑                                             │ │
│  └─────────┼─┼─┼─────────────────────────────────────────────┘ │
│            │ │ │  API Calls                                    │
└────────────┼─┼─┼──────────────────────────────────────────────┘
             │ │ │
             │ │ │
┌────────────┼─┼─┼──────────────────────────────────────────────┐
│            │ │ │   AKS INFRASTRUCTURE (Microsoft-owned)        │
│            ↓ ↓ ↓                                               │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │     Customer Underlay (CX Underlay)                       │ │
│  │     Kubernetes cluster that hosts CCPs                    │ │
│  │                                                            │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │ │
│  │  │ Master Node │  │ Infra Node  │  │ Agent Node  │       │ │
│  │  ├─────────────┤  ├─────────────┤  ├─────────────┤       │ │
│  │  │ Underlay    │  │ - Nanny     │  │ CCP Pods:   │       │ │
│  │  │ Control     │  │ - Scheduler │  │ - APIServer │       │ │
│  │  │ Plane:      │  │ - Logging   │  │ - Etcd      │       │ │
│  │  │ - APIServer │  │ - Metrics   │  │ - Controller│       │ │
│  │  │ - Etcd      │  │             │  │ - Scheduler │       │ │
│  │  │ - Scheduler │  │             │  │ - Guard     │       │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘       │ │
│  │        ↑↑↑           ↑↑↑              ↑↑↑                 │ │
│  └────────┼┼┼───────────┼┼┼──────────────┼┼┼─────────────────┘ │
│           │││           │││              │││                   │
│           AKSinfra      AKSinfra         AKSccplogs            │
│           Database      Database         Database              │
└───────────────────────────────────────────────────────────────┘
```

## Database Scope Clarification

### AKSinfra Database
**Tracks**: AKS **underlay infrastructure** (Microsoft-owned nodes)

**Underlay Node Types**:
1. **Master Nodes** (`k8s-master-*`)
   - Run underlay Kubernetes control plane
   - Manage the underlay cluster itself
   
2. **Infra Nodes** (`k8s-infra-*`)
   - Run AKS infrastructure services:
     - UnderlayNanny (remediation)
     - InfraScheduler
     - Logging/Monitoring agents
   
3. **Agent Nodes** (`k8s-agent-*`)
   - Run **Customer Control Plane (CCP)** pods:
     - Customer's kube-apiserver
     - Customer's etcd
     - Customer's kube-controller-manager
     - Customer's kube-scheduler
     - Guard (AAD auth)
     - CSI controllers

**Tables**:
- `ProcessInfo`: Containers on underlay nodes (including CCP pods)
- `UnderlayNodeInfo`: Underlay node health metrics
- `UnderlayNanny`: Underlay remediation logs

### AKSccplogs Database
**Tracks**: **Customer Control Plane (CCP)** logs

**What runs here**:
- Customer's Kubernetes control plane components (running as pods on underlay agent nodes)
- Logs from kube-apiserver, etcd, controller-manager, scheduler
- Kubernetes events from customer's cluster
- Audit logs from customer's API server

**Tables**: KubeAudit, ControlPlaneEvents, ClusterAutoscaler, etc.

### Customer Worker Nodes
**Where they are**:
- In customer's subscription (MC_* resource group)
- VMSS instances: `aks-nodepool*-*-vmss*`
- These are the nodes customers see in `kubectl get nodes`

**Where their logs are**:
- **NOT in AKSinfra** (those are underlay nodes)
- Customer can collect via:
  - Container Insights / Azure Monitor
  - Custom log collectors
  - SSH to nodes directly

## Common Confusion

❌ **WRONG**: "Customer worker node `aks-nodepool1-12345-vmss000001` logs are in AKSinfra ProcessInfo"

✅ **CORRECT**: "AKSinfra ProcessInfo contains logs from underlay nodes (`k8s-master-*`, `k8s-infra-*`, `k8s-agent-*`) which host the CCP pods for customers"

## Troubleshooting Decision Tree

**Issue with customer worker nodes** (aks-nodepool*-vmss*):
- ❌ Don't query AKSinfra
- ✅ Query AKSccplogs for control plane events (node registration, etc.)
- ✅ Query AKSprod for cluster operations
- ✅ Use Azure portal/CLI to check node status
- ✅ SSH to nodes if needed

**Issue with control plane availability**:
- ✅ Query AKSccplogs for CCP logs
- ✅ Query AKSinfra to check underlay health (if CCP pods are impacted)
- ✅ Query AKSprod for RP operations

**Issue with underlay infrastructure**:
- ✅ Query AKSinfra for underlay node health
- ✅ Check UnderlayNanny for remediation events
- ✅ Escalate to AKS infrastructure team

## Tools for Access

- **aks-prod-tools**: Access underlay API server or underlay nodes
- **hcpdebug**: Access customer control plane (CCP) API server
- **kubectl**: Access customer cluster (via customer credentials)

## Key Insight from Testing

In your CNI failure case:
- **Affected nodes**: `aks-nodepoolu1-23357134-vmss000aw8`, `vmss000b9r`
- **These are**: Customer worker nodes (in customer subscription)
- **Should NOT query**: AKSinfra ProcessInfo (those are underlay nodes)
- **Should query**: 
  - AKSccplogs → KubeSystemEvents (for node events)
  - AKSccplogs → ControlPlaneEvents (for node registration)
  - Customer should check nodes directly (SSH, Container Insights)
