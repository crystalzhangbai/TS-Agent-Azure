# Scope Decision Tree

Use this decision tree to determine whether a support case falls within **VM/Storage** scope or should be routed to another team.

---

## How to use

1. Extract the core symptom keywords from the case statement.
2. Match against the keyword table below.
3. If no exact match, apply the **General rules** at the bottom.
4. For borderline scenarios, consult `support-boundary-rules.md`.

---

## Keyword → Verdict Table

| Keyword / Signal | Verdict | Route to |
|---|---|---|
| `disk attach` / `disk detach` / `managed disk` | ✅ In scope | VM/Storage (Disks RP) |
| `disk encryption` / `ADE` / `CMK` / `SSE` | ✅ In scope | VM/Storage (Disk Encryption) |
| `VM boot` / `VM start` / `boot loop` / `boot stuck` | ✅ In scope | VM/Storage (Compute) |
| `VM performance` / `high CPU` / `high memory` / `I/O latency` | ✅ In scope | VM/Storage (Compute or Disks) |
| `VM extension failed` / `custom script extension` / `CSE` | ✅ In scope | VM/Storage (Extensions) |
| `VM lifecycle` / `VM allocation failed` / `VM delete` | ✅ In scope | VM/Storage (CRP/Compute) |
| `live migration` / `node fault` / `host reboot` | ✅ In scope | VM/Storage (Compute/HW) |
| `NVMe` / `Azure Boost` / `ASAP` / `stornvme` | ✅ In scope | VM/Storage (ASAP) |
| `AccelNet` / `VFP drops` / `host NIC` / `RDMA` | ✅ In scope | VM/Storage (Host Networking) |
| `XStore` / `storage server fault` / `disk blackout` | ✅ In scope | VM/Storage (XStore) |
| `Azure Files` / `SMB mount` / `NFS mount` / `AFS sync` | ✅ In scope | VM/Storage (Azure Files) |
| `hardware fault` / `WHEA` / `SEL` / `MCE` / `memory error` | ✅ In scope | VM/Storage (Hardware) |
| `console log` / `serial console` / `boot diagnostics` | ✅ In scope | VM/Storage (Compute) |
| `AKS cluster` / `node pool` / `cluster autoscaler` / `pod scheduling` | ❌ Out of scope | AKS Team |
| `AKS node fails` (scheduler-side) | ❌ Out of scope | AKS Team (VM team only if allocation fails) |
| `Express Route` / `peering` / `vWAN` / `VPN gateway` (network-only, no VM) | ❌ Out of scope | Network Team |
| `Application Gateway` / `WAF` / `AppGW` | ❌ Out of scope | AppGW Team |
| `Load Balancer` / `SLB` / `backend health` | ❌ Out of scope | SLB Team |
| `Azure Backup` / `backup vault` / `recovery point` | ❌ Out of scope | Backup Team |
| `Azure Site Recovery` / `ASR` / `replication` | ❌ Out of scope | ASR Team |
| `Container Apps` / `KEDA` / `Dapr` | ❌ Out of scope | Container Apps Team |
| `Azure Functions` / `function app runtime` | ❌ Out of scope | Functions Team |
| `SQL Server` / `SQL query slow` / `SQL deadlock` (on Azure VM) | ⚠️ Joint | SQL Team (VM team only if I/O or memory pressure at platform layer) |
| `SAP HANA` / `HSR` / `SAP cluster` | ⚠️ Joint | SAP Team (VM team if platform/host-level fault) |

---

## General Rules

1. **Platform vs. guest**: If the symptom originates at the Azure host / hypervisor / storage fabric → VM/Storage scope. If it originates inside the guest OS application layer → route to the relevant app team.
2. **Network on VM NIC**: NIC-level (VFP, AccelNet) → VM/Host Networking scope. Routing/BGP/peering between VNets/circuits → Network team.
3. **Disk vs. Database**: Disk I/O performance on VM → VM/Disks scope. SQL query performance on that disk → SQL team.
4. **"VM is the hosting substrate"** does not imply VM team ownership. AKS runs on VMs, but AKS cluster operations are AKS team's domain.
5. **If unclear**: Use `vm-knowledge-search` with query `support boundary <topic>`, then consult `support-boundary-rules.md`.

---

## Quick decision flowchart

```
Is the root issue at the Azure host/hypervisor/storage fabric?
  YES → VM/Storage in scope
  NO  → Is it a VM NIC / host network issue?
          YES → VM/Storage (Host Networking) in scope
          NO  → Is it a containerized workload on AKS?
                  YES → AKS Team
                  NO  → Is it network infrastructure (ExR / VPN / SLB)?
                          YES → Network Team
                          NO  → Is it backup / DR?
                                  YES → Backup/ASR Team
                                  NO  → SQL/SAP/Functions/etc. team
```
