# Support Boundary Rules

Borderline scenarios where ownership is not obvious. Use these rules to produce a clear verdict and, if needed, a handoff message to the other team.

---

## Scenario index

Jump to the scenario matching the case; the full **Quick-reference verdict table** is at the bottom of this file.

1. VM boot slow but stuck at OS load screen
2. SQL on Azure VM — query is slow (+ TDE/EKM with Azure Key Vault via Managed Identity)
3. AKS node fails to start
4. Azure Files mount fails from VM
5. VM extension fails
6. SAP HANA cluster fault
7. Azure Disk Encryption (ADE) fails during VM extension provisioning
8. 3rd Party OS / NVA / Marketplace image issues
9. Migration & Move — cross-region / cross-subscription / cross-RG
10. AKS VMSS — allocation, autoscale, resize
11. SAP workloads (ASW:SAP team)
12. Terraform deployment failure
13. Extension ownership — escalation table
14. IIS / Guest OS application issues
15. Service Fabric (SF) cluster on VMSS — ⚠️ DATA-LOSS RISK
16. Start / Stop / Delete / Resize / Redeploy / Restart operations
17. DevOps VMSS — scale set agents
18. Hotpatching (Windows Server Azure Edition)
19. Cross-Tenant CMK for Storage / Managed Disks
20. VM Restore Points
21. Is this even a Storage-vertical case?
22. Azure Site Recovery (ASR) / Disaster Recovery
23. Azure Bastion connectivity (VM ⇄ Networking collaboration)
24. Azure Advisor recommendations
25. Managed Identity on a VM — auth failure vs VM feature
26. Windows Extended Security Updates (ESU)
27. AVD external B2B identities, FSLogix & Entra login on session hosts
28. Linux support-scope limits — CVEs & new cluster deployments
29. Adjacent-service boundaries (Copilot / Key Vault / Managed HSM / ANF backup / Resiliency Hub)

---

## Rule format

Each scenario lists:
- **Trigger signal** — what the case description or logs show
- **Who decides** — which team owns the investigation
- **VM team action** — what VM CSS does before/during handoff
- **Handoff message template** — copy-paste for the transfer note

---

## Scenario 1: VM boot slow but stuck at OS load screen

**Trigger signal:** Customer reports VM unreachable; console log shows OS loading (e.g., grub menu, Windows startup animation) but never completing.

**Who decides:** Check the console log first.
- If the boot fails **before** OS hands off to kernel/userspace (e.g., GRUB misconfiguration, BCD corruption, no boot disk) → **VM/Storage team** (boot disk / platform issue).
- If the kernel loads and OS hangs **inside** the guest (systemd, Windows session manager, driver load) → **handoff to OS team** or customer for OS-level fix.

**VM team action:** Collect console log via `Get-DfmCaseStatement`, extract last 50 lines, identify where boot stalls. Run `vm-kusto-query` for host-level reboot/node events at the same timestamp.

**Handoff message template:**
> Console log shows the VM kernel loads successfully and stalls inside the guest OS (last line: `<last_console_line>`). This is an OS-layer issue beyond Azure platform scope. Recommending the customer engage OS support or check OS-level startup logs.

---

## Scenario 2: SQL on Azure VM — query is slow

**Trigger signal:** Customer says SQL Server queries are slow or timeouts on an Azure VM.

**Who decides:**
- **SQL team** owns the SQL layer (query plan, index, lock, deadlock, database performance, query optimization, SQL service availability, SQL config).
- **VM / Azure Platforms team** owns only if platform-level I/O or memory pressure is confirmed (e.g., Kusto shows high disk latency at storage layer, or VM is on a noisy neighbor host).

**VM team action:** Run `vm-kusto-query` for disk I/O latency (OsAsapCounterTable, StorageLatency) and VM CPU/memory metrics. If platform looks clean → hand off to SQL team. If I/O latency spike confirmed → stay in VM/Storage scope and collab with XStore or Disks RP.

**Diagnostic tools by domain:**
- Infrastructure (VM/disk/network): PerfInsights, ASC Host Analyzer, Azure Monitor.
- SQL Server: SQL Log Scout, Query Store, Extended Events.

**Important:** Do NOT misroute to SQL PG unless the issue is confirmed SQL-specific. Define the support boundary at the start of the investigation.

**Handoff message template:**
> Platform investigation shows no abnormal disk I/O or memory pressure at the Azure host level. SQL query performance is within the SQL Server / guest OS scope. Transferring to SQL on VM team for further investigation.

**SAP:** `Azure/SQL Server in VM - Windows/SQL Administration and Management`

**Ref:** https://supportability.visualstudio.com/AzureSQLVM/_wiki/wikis/AzureSQLVM/2262778

**Related sub-scenario — SQL TDE / EKM with Azure Key Vault via Managed Identity (SQL Server 2022 CU17+):**
- Configuring TDE Extensible Key Management (EKM) with Azure Key Vault using a Microsoft Entra **managed identity** server credential is **in SQL-on-VM scope** — and is **only supported on Azure SQL VM** (not on SQL Server 2022 on-premises, where managed identity isn't available).
- Setup spans three layers: enable system/user-assigned MI on the VM (prefer **UMI**, one per region — a UMI doesn't span regions) → grant the MI the **Directory Readers** role (or Graph `User.Read.All` + `GroupMember.Read.All` + `Application.Read.All`) → grant **Key Vault Crypto Service Encryption User** on the AKV → install the SQL Server Connector and register the EKM provider.
- Keep these in SQL-VM scope. For deep MI token/auth failures collab Entra (see Scenario 25); for the AKV vault itself collab Key Vault (see Scenario 29). Product bugs in the feature → SQL Security PG (`SQLIdentityAndAuthn@microsoft.com`, ICM queue "ET1 RFCs Security").
- **SAP:** `Azure/SQL Server in VM - Windows/SQL Administration and Management/Encryption, TDE, Azure Key Vault (AKV)`
- **Ref:** https://supportability.visualstudio.com/AzureSQLVM/_wiki/wikis/AzureSQLVM/1790496

---

## Scenario 3: AKS node fails to start

**Trigger signal:** AKS node in NotReady state; customer asks Azure support for help.

**Who decides:**
- **AKS team** owns the scheduler, kubelet, and node provisioning pipeline.
- **VM team** owns only if the **underlying Azure VM allocation** fails (e.g., `AllocationFailed` error in CRP, capacity constraints, VM extensions failing on node VMs).

**VM team action:** Check if CRP shows allocation failure for the node VM (use `vm-kusto-query` on CRP operations table). If allocation succeeded but node is NotReady → route to AKS team.

**Handoff message template:**
> Azure platform confirms the underlying VM for this AKS node was successfully allocated (CRP op status: Succeeded). The node readiness issue is within AKS control plane / kubelet scope. Transferring to AKS Cluster Operations team.

---

## Scenario 4: Azure Files mount fails from VM

**Trigger signal:** Customer cannot mount Azure Files share from inside an Azure VM (SMB/NFS).

**Who decides:**
- **Azure Files team** owns the file share service (throttling, share quota, authentication, protocol errors).
- **VM team** owns only if the issue is a **NIC / DNS / host network** problem preventing TCP connectivity to the storage endpoint.

**VM team action:** From inside the VM, test connectivity: `Test-NetConnection <storage-account>.file.core.windows.net -Port 445`. If connectivity fails at network level, check AccelNet / VFP / DNS. If connectivity succeeds but mount still fails → route to Azure Files team.

**Handoff message template:**
> Network connectivity from the VM to the Azure Files endpoint is confirmed (port 445 reachable). The mount failure is within the Azure Files service layer (authentication, share quota, or protocol). Transferring to Azure Files team.

---

## Scenario 5: VM extension fails

**Trigger signal:** A VM extension (e.g., Custom Script Extension, AAD Login, Monitoring Agent) reports failure.

**Who decides:**
- **VM team** owns the extension **framework** (extension install/uninstall lifecycle, extension status reporting, ExtensionManager on the agent).
- **Sub-extension team** owns the specific extension behavior (e.g., MMA/AMA → Monitoring team; AAD Login → Identity team; CSE → customer's own script logic).

**VM team action:** Check extension status via `vm-kusto-query` (ExtensionTable, CRP operations). If the framework installed successfully but the extension's own handler failed → note the extension name and route to the specific team.

**Handoff message template:**
> The Azure VM extension framework successfully installed the `<ExtensionName>` extension (CRP status: Provisioning succeeded). The failure is within the extension handler itself. Transferring to the `<OwningTeam>` team for `<ExtensionName>`-specific investigation.

---

## Scenario 6: SAP HANA cluster fault

**Trigger signal:** SAP HANA HSR (HANA System Replication) failover occurred; customer reports data loss or degraded replication.

**Who decides:**
- **SAP team** owns the SAP HANA application layer (HSR config, pacemaker fencing, HANA internals).
- **VM team** owns if a **host-level fault** (node reboot, storage fault, network blip) triggered the failover.

**VM team action:** Run `vm-kusto-query` for VMA, service healing, and node events at the time of failover. If a host event is found → stay in VM scope and produce platform RCA. If platform looks clean → route to SAP team.

**Handoff message template:**
> Platform investigation shows no host-level fault (no node reboot, service healing event, or storage blip) at the time of the HANA failover. The HSR failover appears to be triggered by an SAP HANA application-layer event. Transferring to SAP on VM team.

---

## Scenario 7: Azure Disk Encryption (ADE) fails during VM extension provisioning

**Trigger signal:** VM extension `AzureDiskEncryption` or `AzureDiskEncryptionForLinux` reports failure.

**Who decides:**
- **VM team** owns the ADE extension framework installation.
- **Key Vault / Disk Encryption team** owns if the failure is Key Vault access, CMK key rotation, or encryption policy.

**VM team action:** Check CRP extension status. If `ExtensionProvisioningState = Failed` and error mentions Key Vault or CMK → route to Disk Encryption / Key Vault team. If agent can't install extension at all → VM scope.

---

---

## Scenario 8: 3rd Party OS / NVA / Marketplace image issues

**Trigger signal:** Customer uses a 3rd-party Marketplace image (CIS, Oracle Linux, Palo Alto NVA, Fortinet, Cisco NVA) and reports OS crash, config issue, performance problem, or patching failure.

**Who decides:**
- **3rd party vendor** owns OS crashes, performance issues, configuration, patching, and any customized kernel/agent behavior.
- **VM team** provides RCA for host-level issues (LSI, service healing, node reboot) and ensures platform is healthy.

**VM team action:**
1. Check for LSI / platform issues that could impact the customer.
2. Verify billing code in ASC (Linux IaaS vs RHEL/SUSE/SLES).
3. Find vendor support link: Portal → Marketplace → select image → Support link.
4. Set expectation: "Commercial Marketplace publishers are responsible for supporting their software."

**Handoff message template:**
> Platform investigation confirms no Azure infrastructure issues. The issue involves a 3rd-party Marketplace image (`<Publisher>:<Offer>:<SKU>`). Per Azure Marketplace policy, the publisher provides primary support for their offering. Please contact vendor support at `<vendor_support_url>`.

**Ref:** https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/1500237/3rd-Party-OS-Support-Boundaries_Process

---

## Scenario 9: Migration & Move — cross-region / cross-subscription / cross-RG

**Trigger signal:** Customer wants to migrate VMs between regions, subscriptions, resource groups, or from on-prem to Azure.

**Who decides:**
| Migration type | Owner |
|---|---|
| Move between resource groups | **VM team** |
| Move between subscriptions | **VM team** |
| Move between regions (Azure Resource Mover) | **Azure Backup/ASR team** |
| Move regional VMs to Availability Zones | **Azure Backup/ASR team** |
| Migrate from on-prem to Azure (Azure Migrate) | **Azure Backup/ASR team** |
| Move subscription to different tenant | **Azure Subscription Management** |
| Classic vNet/Storage to ARM | **Azure Networking / Storage Account team** |
| Cloud Management Gateway (CMG) migration | **SCCM/ConfigMgr team** |

**VM team action:** If the case involves cross-region moves or Azure Migrate, verify no platform allocation issues, then route to Azure Backup/ASR team via collab first.

**Handoff message template:**
> This migration scenario (`<migration_type>`) is owned by the `<owning_team>` team. Before transferring, we verified no Azure platform issues on the source VM. Transferring to `<SAP>`.

**Ref:** https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/506413/Support-Boundaries_Mig-Move

---

## Scenario 10: AKS VMSS — allocation, autoscale, resize

**Trigger signal:** AKS-managed VMSS reports `ZonalAllocationFailed`, `AllocationFailed`, `OverconstrainedAllocationRequest`, or autoscale not working.

**Who decides:**
- **VM team** owns capacity investigations and allocation failures on the underlying VMSS.
- **AKS team** owns the AKS cluster autoscaler, node pool configuration, and any AKS-specific behavior.

**Key limitations (unsupported by AKS):**
- Resizing VMSS SKU directly in Portal (must create new node pool + delete old)
- AutoOSUpgrade on AKS VMSS
- Direct VMSS operations outside of `az aks` commands

**VM team action:**
1. Check if allocation failure is capacity-related (use Compute Capacity Advisory in ASC).
2. **Do NOT recommend deploying to a different region** — AKS clusters cannot be moved across regions.
3. If allocation is constrained, recommend creating a new node pool with the desired SKU.
4. Keep AKS collab task open until both teams agree the scenario is VM-capacity only.

**Handoff message template:**
> Allocation failure confirmed on the AKS node pool VMSS. The VM team will investigate capacity constraints. AKS team should remain on collaboration for any AKS-level recovery or reconfiguration (e.g., create new node pool).

**Ref:** https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/496411/AKS-Support-Boundaries_VMSS

---

## Scenario 11: SAP workloads (ASW:SAP team)

**Trigger signal:** Customer runs SAP applications (S/4, BW, NetWeaver, SuccessFactors) or HANA/Oracle/SQL databases on Azure VMs and the issue appears SAP-specific.

**Who decides:**
- **ASW:SAP team** owns when customer uses SAP tools to detect/diagnose the issue, when symptoms depend on SAP running, or when customer expects SAP familiarity.
- **VM team** owns platform-level issues (host reboot, storage fault, network blip, allocation failure).

**VM team action:**
1. Rule out Azure platform issues first (run VMA/SH Kusto queries).
2. If Sev-A: Open collab to ASW team immediately + collect data per ASW data collection template.
3. If Sev-B/C: Open Ava request on ASW channel.

**Data to collect:**
- SAP application type (S/4, BW, NetWeaver, etc.)
- DB type (HANA, Oracle, MS SQL)
- Storage solution (ANF, Managed Disks, Azure Storage)
- Cluster or standalone

**Handoff message template:**
> The issue involves an SAP workload (`<SAP_app_type>` on `<DB_type>`). Platform investigation shows no host-level fault. The issue appears within SAP application layer scope. Routing to ASW:SAP team.

**Valid SAPs:** `Azure/SAP on Azure/*`

**Ref:** https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/1326359/Engage-Azure-Strategic-Workloads-ASW-SAP_Process

---

## Scenario 12: Terraform deployment failure

**Trigger signal:** Customer uses Terraform to deploy Azure resources and the deployment fails.

**Who decides:**
| Layer | Owner |
|---|---|
| Terraform HCL syntax / compilation | **Customer** (their code) |
| Terraform AzureRM/AzAPI provider issues | **Azure ARM team** |
| Resource provider errors (CRP, SRP, NRP) | **Respective RP team (VM, Storage, Networking)** |
| HashiCorp Terraform Engine bugs | **HashiCorp** (via ARM team escalation) |

**VM team action:**
- If the error is a CRP operation failure during VM deployment → stay in VM scope.
- If the error is Terraform provider or engine issue → route to ARM team: `Azure/Azure Resource Manager (ARM)/Client Tools/Terraform`.

**Handoff message template:**
> The Terraform deployment failure error (`<error_code>`) originates from `<layer>`. Transferring to `<owning_team>` for further investigation.

**Ref:** https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/1997098/Terraform-Support-Boundaries

---

## Scenario 13: Extension ownership — escalation table

**Trigger signal:** VM extension reports failure after installation.

**Who decides:** Depends on the specific extension (see table below).

| Extension | Owner | SAP |
|---|---|---|
| Azure Diagnostics (WAD/LAD) | Monitoring team | VM Extensions > Azure Diagnostics Extension issue |
| Azure Monitor Agent (AMA) | Monitoring team | Azure Monitor Agent (AMA) |
| Log Analytics (MMA/OMS) — deprecated | Monitoring team | Log Analytics agent (MMA and OMS) |
| Update Management | Monitoring team | VM Extensions > Update Management extension |
| DSC (Desired State Configuration) | Monitoring team | VM Extensions > Azure DSC extension |
| Guest Configuration (AzurePolicy) | Monitoring team | Azure Policy > Guest Configuration |
| Hybrid Worker Extension | Monitoring team | Azure Automation > Hybrid Runbook Worker |
| Service Fabric | Service Fabric team | Service Fabric > VMSS Extensions |
| Microsoft Defender Endpoint (MDE) | Endpoint Protection team | VM Extensions > Microsoft Antimalware |
| Azure DevOps Pipelines Agent | Azure DevOps team | Azure DevOps > Pipelines > Extensions |
| VMSnapshot (Backup) | Azure Backup team | Azure Backup > Extension issues |
| SiteRecovery | Azure Backup team | Azure Site Recovery > Replication/Failover |
| AADLoginForWindows | AAD team | See AAD wiki |
| AADSSHLoginForLinux | AAD team | See AAD wiki |
| SAP Enhanced Monitoring | SAP Support (via SAP) | Customer contacts SAP directly |
| Qualys Agent | Qualys (3rd party) | 3rd party |
| Key Vault VM Extension | Key Vault team | Key Vault > Managing Certificates > KV VM Extension |
| Network Watcher Agent | Azure Networking team | VM Extensions > Network Watcher agent |
| Guest Attestation | Azure Security team | Defender for Cloud > Server recommendations |
| SQL IaaS Extension | MSaaS SQL Core | SQL Server in VM > SQL IaaS Agent Extension |
| VM Application Extension | **VM team** | VM Extensions > Compute Gallery VM applications |
| Application Health Extension | **VM team** | VMSS > Health probes |
| VM Watch | **VM team** | VMSS > Health probes |
| Azure Disk Encryption (ADE) | **VM team** | VM Extensions > ADE extension issue |
| Custom Script Extension (CSE) | **VM team** | VM Extensions > CSE extension issue |
| Performance Diagnostics (PerfInsights) | **VM team** | VM Performance > PerfInsights tool |
| VM Access / enablevmaccess | **VM team** | VM Extensions > VM Access extension |
| Run Command | **VM team** | VM Extensions > Run-Command extension |
| GPU Driver (AMD/Nvidia) | HPC team | HPC VM Extensions |
| OpenSSH Extension | Windows team | Windows Server > OpenSSH |
| Azure Update Manager Extensions | Azure Update Manager team | Azure Update Manager > Onboarding |
| GenevaMonitoring | Not CSS — ICM to ASM-Dev | Not supported by CSS |

**VM team scope:**
- Extension **installation** lifecycle (install/uninstall/enable/disable)
- Extension status reporting
- Guest Agent / Extension Manager issues

**Sub-extension team scope:**
- Extension **handler** functionality
- Extension-specific errors/features

**Ref:** https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/494976/Extensions-Workflow_AGEX

---

## Scenario 14: IIS / Guest OS application issues

**Trigger signal:** Customer reports IIS application pool, ASP.NET, or other guest OS application issues on an Azure VM.

**Who decides:**
- **Servers / IIS team** owns IIS configuration, application pools, ASP.NET runtime issues.
- **Developer Tools / ASP.NET team** owns ASP.NET framework issues (install, upgrade, deployment).
- **VM team** owns only if platform-level issue (host reboot, disk I/O) directly caused the symptom.

**VM team action:**
1. Verify no platform events (reboot, storage blip) at the time of failure.
2. If issue is purely guest OS / application configuration → route to Servers or Developer Tools.

**Handoff message template:**
> Platform investigation shows no Azure infrastructure issues at the time of the IIS/application failure. This is a guest OS application configuration issue. Transferring to `<SAP>`.

**Common SAPs:**
- IIS: `Servers > Internet Information Services > Internet Information Services 10.0`
- ASP.NET: `Developer Tools > ASP.NET > Install and Deployment`

---

## Scenario 15: Service Fabric (SF) cluster on VMSS — ⚠️ DATA-LOSS RISK

**Trigger signal:** VMSS has a `ServiceFabric` tag, the Service Fabric Extension installed, an SF cluster in the same RG, OR the RG name starts with `sfc_<GUID>` (managed cluster). Customer reports node down, cluster issue, UDWalk timeout, scaling/resize failure.

**⚠️ CRITICAL — read before ANY action:**
Operations like **changing SKU, deallocate, restart, delete, re-image** on an SF cluster VMSS can cause **irreversible damage and data loss**. **ALWAYS open a collaboration task with the Service Fabric (SF) team BEFORE performing any of those actions**, regardless of who owns the case. VM CSS does not have the technical depth on SF internals and may break the cluster unknowingly.

**Who decides:**
| Issue | Owner |
|---|---|
| Can't RDP/SSH, non-boot, OS/kernel, BSOD (non-SF driver) | **VM team** |
| VMSS deployment failure | **VM team** |
| VM agent / extension issues (non-SF extension) | **VM team** |
| Start/stop, unexpected restart, scaling | **VM team** (follow general workflow) |
| `autoOSUpgrade` failed (health extension errors) | **VM team** |
| **UDWalk Timeout error** | **SF team drives**, VM collaborates |
| **Changing SKU (resize) in-place** | **SF team drives** |
| SF System Service, SF SDK app, Managed Clusters | **SF team** |
| SF Extension issue | **SF team** |
| Container/Docker from SF programming model | **SF team** |
| SF kernel components (LeaseLayer, KVS) BSOD | IaaS investigates → transfers to SF if SF driver |
| SF cert management, TLS/SSL tightening (SF context) | **SF team** |
| DSC Extension issue | **Automation team** |
| DNS, App Gateway in front of SF, VNet/ExR/VPN/SLB | **Azure Networking team** |

**VM team action:** Gather basic data (when noticed, recent changes). Review ASC Insights/health/operation logs. If any stop/deallocate/delete/scale action is needed for troubleshooting → engage SF team via collab FIRST.

**Collab SAP:** `Azure/Service Fabric/Cluster` → routes to queue **MSaaS POD Azure Dev SF**.

**Ref:** https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/496437

---

## Scenario 16: Start / Stop / Delete / Resize / Redeploy / Restart operations

**Trigger signal:** Azure VM management operation fails (start, stop, delete, resize, redeploy, restart).

**Who decides:** Start-Stop is **primarily IaaS VM POD**, but several sub-scenarios route elsewhere:

| Scenario | Supported by | SAP |
|---|---|---|
| Allocation failures | **VM** - Configuration | `Azure\Virtual Machine running…\Received Allocation Failure` |
| Slow start due to extension | **VM** (can collab) | `…\Cannot start or stop my VM\My VM is unresponsive to start or stop operations` |
| Failed to start — **subscription disabled** | **Azure Subscription Mgmt** | `Azure\Compute\Virtual Machines\Administration\HowTo:Subscription and Licensing Administration` |
| **Quota exceeded** | **Azure Subscription Mgmt** | (same as above; customer can self-increase quota) |
| NIC in failed state | **VM** | `…\My start or stop operation failed` (if AppGW/LB unhealthy → collab that team) |
| Network Internal Operation error | **VM** | `…\My start or stop operation failed` |
| Windows boot issue | **VM** (engage Windows Ava if needed) | `Azure/Virtual Machine running Windows/My VM is not booting/My VMs OS is not booting` |
| Linux boot issue | **VM** (engage Linux Ninjas) | `Azure/Virtual Machine running Linux/My VM is not booting/My VMs OS is not booting` |
| Start-Stop automation | **VM** | `…\My start or stop operation failed` |
| Failed to delete VM | **VM** | `…\Unable to delete Virtual Machine` |
| Failed to resize | **VM** | `…\Assistance with resizing my VM\My desired size is unavailable` |

**Note:** Do NOT manually override the destination queue unless instructed by your TA — queue varies by support topic, service level, contract, and cloud (Public/Fairfax/Mooncake).

**Ref:** https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/1369134

---

## Scenario 17: DevOps VMSS — scale set agents

**Trigger signal:** VMSS is used as an Azure DevOps Pipelines scale set agent (scaling driven by the DevOps Scale Set Agent Pool sizing job); customer reports scaling, build, or agent issues.

**Who decides:**
- **VM team** owns platform-level problems: resize, scaling, availability issues caused by the platform.
- **Azure DevOps team** owns if: DevOps Extension issue, DevOps agent install problem, the issue is in the Azure DevOps portal (not Azure Portal), Pipelines agents/pools, deployment via Azure DevOps, or build failures/delays related to the agent or code.

**Rule of thumb:** If a resize/scaling/availability issue is suspected to be caused by the **extension** → engage DevOps. Otherwise VM team resolves.

**DevOps SAP:** `Azure / Azure DevOps Services / Pipelines - Agents and Pools / Virtual machine scale set (VMSS) agent pool`

**Ref:** https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/1936417

---

## Scenario 18: Hotpatching (Windows Server Azure Edition)

**Trigger signal:** Customer issue involves hotpatching-enabled Windows images, the hotpatch feature, or guest patching.

**Who decides:** Split between **Azure IaaS VM** and **Azure Monitoring (Update Manager / UMC)**:

| Scenario | Supported by | SAP |
|---|---|---|
| VM provisioning failure (hotpatch image) | **VM** - Configuration | `Azure/Virtual Machine running Windows/Cannot create a VM` |
| Performance degradation after moving to hotpatch image | **VM** - Management | `…/VM Performance/CPU usage is higher than expected` |
| Enable/disable hotpatch via **Portal** | **UMC** | `Azure/Update management center/Issues related to change update settings page and patch orchestration settings` |
| Enable/disable hotpatch via **PowerShell/CLI** | **VM** - Configuration | `…/Windows Update, Guest Patching and OS Upgrades/Issue enabling HotPatching` |
| Windows updates fail to install at guest OS level | **VM** - Connectivity | `…/Update issue - patch fails to install` |
| Hotpatch VM not getting patched | **UMC** | `Azure/Azure Automation/Update Management/Update Deployment did not install some or all updates` |
| Hotpatch status wrong in UMC blade | **UMC** | `Azure/Update management center/Issues related to Portal UI/Data displayed on the page is wrong` |
| Hotpatching causes a VM restart | **VM** - Configuration | `Azure/Virtual Machine running Windows/VM restarted or stopped unexpectedly` |
| Workload-specific issue outside hotpatching | Team owning that workload | (consult TA) |

**Rule of thumb:** Patch **orchestration** (scheduling, deployment, portal settings) → UMC. Enabling the feature via CLI, provisioning, restart, and perf → VM.

**Ref:** https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/1077169

---

## Scenario 19: Cross-Tenant CMK for Storage / Managed Disks

**Trigger signal:** Customer configuring cross-tenant Customer-Managed Keys (CMK) for a storage account or managed disk reports a failure.

**Who decides:** The **storage account / disk management** piece routes to **IaaS VM POD**; the identity and Key Vault pieces route elsewhere:

| Scenario | Supporting team | SAP |
|---|---|---|
| Management of storage account for CMK | **IaaS Storage (VM POD)** | `Azure\Storage Account Management\Encryption\Issue encrypting with Customer Managed Keys(CMK)` |
| Cross-tenant CMK for **Managed Disks** setup | **VM POD** | (Disks encryption) |
| Multi-tenant AAD app registration | **Authentication - Application Experiences** | `Azure\Azure Active Directory App Integration and Development\app registrations\Questions about AppID or other URLs` |
| Configure managed identity as federated credential | **Authentication - Application Experiences** | `…\app registrations\Configuring Certificates and Client Secrets` |
| Create/Delete user-assigned managed identity | **Account Mgmt - User Management** | `Azure\Managed Identities for Azure Resources` |
| Assign managed identity to an RBAC role | **Account Mgmt - User Management** | `Azure\Role Based Access Control (RBAC)…\Problem with RBAC role assignments` |
| Managing Azure Key Vault | **Security team** | `Azure\Key Vault\Managing Access and Networking configuration\Key Vault Access Policies, Security Groups and RBAC` |

**Rule of thumb:** "Set up the storage account / disk for CMK" → VM POD. "Set up the identity or the Key Vault" → Identity / Security teams.

**Ref:** https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/643017

---

## Scenario 20: VM Restore Points

**Trigger signal:** Customer (often a 3rd-party backup vendor) uses the VM Restore Points API; reports backup failure or API issues. Restore Points do NOT use a Recovery Services Vault.

**Who decides:**
- **Azure Backup team** owns the **backup process** side (snapshot creation, extension behavior) — troubleshooting is nearly identical to Azure VM Backup.
- **Azure VM Compute team** owns **API calls failing or development to use the API**.

**VM team action:** Confirm backup solution, use ASC to check VM health + pull extension logs, Kusto for failed jobs. Correct the case SAP if needed.

**Routing SAP:** Under `Azure/Virtual Machine Running <OS>/Azure Features/Restore Points` (5 SAP buckets — 4 Linux flavors + Windows).

**Ref:** https://supportability.visualstudio.com/AzureBackup/_wiki/wikis/AzureBackup/1825769

---

## Scenario 21: Is this even a Storage-vertical case?

**Trigger signal:** Case mentions files, shares, blobs, or storage but it's unclear whether it's in Storage scope.

**Golden rule:** **If there is no storage account involved, it is NOT a storage-vertical case.**

**Storage vertical scope (IaaS Storage / VM POD):**
| Topic | In scope |
|---|---|
| Azure Files | Mount on Windows/Linux, Entra ID / AD DS integration |
| Azure File Sync | Sync issues, endpoints, cloud tiering, agent install/upgrade/register |
| Storage Account Mgmt | Unable to delete, recover deleted account, GRS→ZRS/LRS, upgrade to StorageV2 |
| AzCopy & Data Migration | AzCopy errors, data transfer |
| Billing & Monitoring | Usage checks, pricing, metrics/logs |
| Connectivity | 403 errors, private endpoints, storage account firewall |
| Performance | Latency/slowness, heavy metadata |

**Route elsewhere:**
- **Blob Storage / ADLS Gen2** (non-connectivity, blob recovery, REST API) → **PaaS Dev Storage team**
- Azure Files in **AVD** environments → **FSLogix team**
- Azure Files **authentication** → **Microsoft Entra ID & AD DS teams**
- **Private endpoint / connectivity** → **Azure Networking team**

**Note:** We do NOT support troubleshooting using logs/metrics from non-Microsoft/Azure 3rd-party tools.

**Ref:** https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/2174345

---

## Scenario 22: Azure Site Recovery (ASR) / Disaster Recovery

**Trigger signal:** Customer reports a replication, failover, recovery-plan, or DR issue involving Azure Site Recovery (A2A, Hyper-V/VMware-to-Azure, or Azure Stack DR).

**Who decides:**
- **ABRS team (Azure Backup & Recovery Services)** owns ASR end-to-end: replication health, Mobility Service/agent, failover/failback, recovery plans, RPO. SAP under `Azure/Azure Site Recovery/...`.
- **VM team** owns only the **source/target VM platform** layer — allocation failure when ASR boots the target VM, or a host fault on the source VM — not the replication pipeline itself.

**Azure Stack source/destination support matrix (from the ASR boundary sub-page):**

| Source | Destination | Supported | Owner |
|---|---|---|---|
| Azure Stack Hub | Azure | Yes (as physical-server replication) | **ABRS** |
| Azure | Azure Stack Hub | Yes (failback scripts) | **Azure Stack Hub team** |
| Azure Stack Hub | Azure Stack Hub | Yes | **Azure Stack Hub team** — SAP `Azure\Azure Stack Hub\Backup and Disaster Recovery` |
| Azure Stack Hub | Azure Stack HCI / Edge | No | — |
| Azure Stack HCI (Local) | Azure | Yes (preview) | **HCI team** pre-replication, **ABRS** from "Enable replication" onward |
| Azure Stack Edge | * | No | — |

**Handoff message template:**
> Platform investigation shows no source/target VM host fault. The issue is within the Azure Site Recovery replication/failover pipeline. Transferring to the ASR (ABRS) team. SAP: `Azure/Azure Site Recovery/<sub-topic>`.

**Note:** The CSS Wiki "Support Boundaries" landing page for ASR (id 1027849) is an empty parent; concrete boundary content lives in its sub-pages (e.g. *ASR on Azure Stack*, id 1027852). See also Scenario 9 (cross-region Migration & Move → Azure Backup/ASR).

**Ref:** https://supportability.visualstudio.com/AzureSiteRecovery/_wiki/wikis/AzureSiteRecovery/1027852

---

## Scenario 23: Azure Bastion connectivity (VM ⇄ Networking collaboration)

**Trigger signal:** Customer can't connect through Azure Bastion — black screen, failed login, disconnect, perf, or an RDS-license error. Bastion spans VM + Networking + Entra disciplines.

**Who decides:** **The team that receives the case first takes ownership and scopes it** using the General Scoping questions (client type, credential type, domain type, target, target OS, SKU/features, timestamps, error). Engage the other team via collab; **both teams stay engaged** until the owner is clear.

**Collab SAPs:**
- VM → Networking collab: `Azure/Bastion/Connectivity`
- Networking → VM collab: `Azure/Virtual Machine running Windows/Cannot connect to my VM/Failure to connect using RDP or SSH port`
- Always reference https://aka.ms/BastionSupportDoc in the collab.

**Who drives — after scoping:**
| Symptom | Driver |
|---|---|
| Failed credential login (some users ok); domain creds failing after VM-side steps done | **VM** (may pull AAD/DS) |
| Failed creds in **Tomcat** logs (portal validates against AAD before reaching the VM) | **Entra/AAD** |
| Black screen / wrong fonts / keyboard language / display size (UX) | **Networking** (may need VM) |
| Performance | First-touch team; Net checks Bastion metrics/latency, VM checks VM perf |
| Net trace: SYN reaches target, no response or RST | **VM** (packet reached the VM) |
| Net trace: SYN + SYN/ACK but TCP handshake never completes | **Networking** (likely asymmetric routing) |
| Net trace: TCP ok but no SSL attempt | **VM** (CredSSP restriction / event logs) |
| UDR / NSG questions | **Networking** |
| Host firewall / iptables | **VM** |
| `ERRINFO_LICENSE_NO_LICENSE_SERVER [0x00010101]` / Event ID 50280 (verify target is NOT an RDS Session Host) | **Windows User Experience** |
| Bastion deployment / configuration | **Networking** |
| Entra login / SSO on the VM | **VM first** (extension/config), then Entra |

**Note:** Connection to an RDS Session Host is **not supported** by Bastion.

**Ref:** https://supportability.visualstudio.com/AzureNetworking/_wiki/wikis/Wiki/1201042

---

## Scenario 24: Azure Advisor recommendations

**Trigger signal:** Case about Azure Advisor — the Advisor blade/score/UX, or a specific recommendation.

**Who decides:**
- **IaaS VM team owns the Advisor platform:** blade/portal UX, permissions/RBAC to view Advisor, the Advisor score, dismiss/postpone, configuration of Advisor itself.
- **The source service owns the recommendation content:** SQL recs → SQL/ASMS, Security recs → Defender/Security, Cost recs → Billing/ARM, Reliability/HA recs → the respective RP. VM opens a collab to that team; VM does not RCA why another service emitted a recommendation.

**Rule of thumb:** "Advisor itself isn't working / I can't see Advisor" → **VM**. "This specific recommendation is wrong / how do I act on it" → **source service**.

**Ref:** https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/1670372

---

## Scenario 25: Managed Identity on a VM — auth failure vs VM feature

**Trigger signal:** Customer uses a system- or user-assigned managed identity on a VM (for PerfInsights, CMK, app auth, etc.) and reports it failing.

**Who decides:**
- **Entra ID (Managed Identities) team owns the identity itself:** MI creation/assignment, token/auth failures (IMDS 401/403), role-assignment propagation. SAP `Azure\Managed Identities for Azure Resources\...`.
- **VM team owns the VM feature that consumes the MI:** e.g. PerfInsights "Managed Identity" mode (requires **Storage Blob Data Contributor** + **Storage Table Data Contributor** on the target storage account), extension behavior, the VM-side configuration.

**Rule of thumb:** token won't issue / identity not found / RBAC not effective → **Entra**. The VM feature or extension that uses an otherwise-working identity → **VM**.

**Ref:** https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/2056406

---

## Scenario 26: Windows Extended Security Updates (ESU)

**Trigger signal:** End-of-life Windows on an Azure VM under ESU — Windows 10 (EOL 14 Oct 2025, ESU to 10 Oct 2028) or Windows Server 2012/R2 (ESU to 13 Oct 2026), including AVD multi-session Win10/11.

**Support boundary (limited):** ESU covers **only** security-update install / activation / deployment and regressions **directly caused by an ESU update**.

**OUT of scope under ESU:** new feature requests, general RCA, performance issues, configuration / setup / design. For **Server 2012**, full support requires an active Unified / PSfP / Premier or PPI plan — otherwise limited support only.

**VM team action:** First verify Azure infrastructure is **not** at fault (platform RCA is always in VM scope). If the ask is OS-level break/fix/RCA on the EOL OS beyond a security-update regression, set expectations per the ESU boundary.

**Ref:** Win10 https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/2286428 · Server 2012 https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/1566510

---

## Scenario 27: AVD external B2B identities, FSLogix & Entra login on session hosts

**Trigger signal:** Azure Virtual Desktop case involving external/B2B guest sign-in, FSLogix profile containers on Azure Files with AAD Kerberos, or AADLoginForWindows on session hosts.

**Who decides — start with the AVD team to verify setup, then split:**
| Sub-scenario | Owner | SAP |
|---|---|---|
| B2B sign-in to AVD (Windows app / Web / Mac) | **AVD** | `Azure/Azure Virtual Desktop/Authenticating to Azure Virtual Desktop/Using Single Sign-On with Azure Virtual Desktop` |
| AADLoginForWindows ext fails to add/remove external user to local groups; or B2B/federated user with **VM Administrator/User Login** RBAC can't log in | **AAD – Authentication** | `Azure/Virtual Machine running Windows/VM Extensions not operating correctly/Azure Active Directory Login extension issue` |
| B2B guest on **AAD DS-joined** session host fails at orchestration (Error 10009) | **By design** — AAD DS can't resolve external identities. Only supported config = **Entra ID-joined** session hosts; **no workaround** | — |
| Azure Files + AAD Kerberos for FSLogix: AAD app/SP creation, API permissions | **AAD team** | — |
| Storage account setup, RBAC/NTFS perms, enabling Kerberos property; TGT/ticket present but still can't mount profile | **Azure Files team** | `Azure\Files Storage\Security\Azure Active Directory(AAD) Kerberos authentication` |
| FSLogix config on the session host | **AVD** | — |

**Ref:** FSLogix Kerb https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/544583 · AVD B2B https://supportability.visualstudio.com/AzureAD/_wiki/wikis/AzureAD/2251938

---

## Scenario 28: Linux support-scope limits — CVEs & new cluster deployments

**Trigger signal:** Linux VM customer asks us to (a) confirm/patch a specific CVE via the support case, or (b) design/deploy a new Pacemaker/SUSE/RHEL HA cluster (e.g. SAP HANA).

**Boundaries:**
- **CVEs are NOT tracked or remediated through support cases.** Point the customer to the distro's official channel (Red Hat Security/Errata, SUSE CVE DB/Bugzilla, Ubuntu CVE Tracker/USN, Oracle ULN) and the OS package manager (`dnf updateinfo list cves`, `zypper lp --cve`, `pro fix CVE-…`). Don't run or endorse 3rd-party scanners / pen-tests to "prove" exposure. Shared-responsibility model applies.
- **New cluster deployments (incl. cluster configuration) are out of scope** — that's Professional Services / design-architecture-deployment work. Team policy = **best-effort only**, after sending the customer the standard "no guaranteed timeframe or resolution" support-policy email.
- **SLES guest-OS support eligibility:** for vendor-backed SUSE support the VM must run a **Premium (PAYG) SLES image from the Azure Marketplace / Image Gallery** (not a BYOS/self-built image). Off-hours / weekend escalations on SUSE follow the **SUSE partner standby (on-call) schedule** — set the customer's expectation that deep SLES-internal fixes may wait for the SUSE partner's standby window rather than 24×7 Microsoft handling.

**VM/Linux team action:** Set expectations per the above; still own genuine Azure-platform faults (host/storage/network RCA) underneath.

**Ref:** CVEs https://supportability.visualstudio.com/AzureLinuxNinjas/_wiki/wikis/AzureLinuxNinjas/1683598 · New cluster deployments https://supportability.visualstudio.com/AzureLinuxNinjas/_wiki/wikis/AzureLinuxNinjas/686665 · SUSE standby https://supportability.visualstudio.com/AzureLinuxNinjas/_wiki/wikis/AzureLinuxNinjas/214275

---

## Scenario 29: Adjacent-service boundaries (quick reference)

These surface inside VM cases but are owned elsewhere; verify any VM-platform angle, then collab/route.

| Service / ask | Owner | Route / SAP | VM-side angle |
|---|---|---|---|
| **Azure Copilot** (in the Azure portal) | **IaaS VM POD owns it** | keep | Copilot-in-Windows = not supported; M365 / Dynamics / Security / GitHub Copilot variants → their respective teams |
| **Azure Key Vault** (vault/secret/key/cert mgmt, firewall, soft-delete, RBAC, KV VM extension) | **Key Vault (Entra) team** | `Azure\Key Vault\...` | **ADE / disk-encryption use of KV → VM**; KV consumed by AKS CSI, APIM, App Gateway, Front Door, SQL TDE → those teams |
| **Azure Managed HSM** (provision, security domain, keys, local RBAC, networking) | **Key Vault (Entra) team** | `Azure\Key Vault\Managed HSM...` | Dedicated HSM / Payment HSM are different services; SKR CVM config → Confidential Computing / VM |
| **Azure NetApp Files backup** | **ANF team — native, NOT Azure Backup** | `Azure\Azure NetApp Files\Backup and Restore` | none — just correct the SAP |
| **Azure Resiliency Hub / Infrastructure Resiliency Manager** (goals, recovery plans, drills, portal) | **Azure Resiliency Hub PG** (IcM service tree *Microsoft Azure Resiliency Hub*) | escalate via Resiliency Hub IcM matrix | ASR replication/failover beneath it → **ABRS** (Sc 22); detected VM resiliency solution = ASR zonal DR |

**Ref:** Copilot https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/1308230 · Key Vault https://supportability.visualstudio.com/AzureAD/_wiki/wikis/AzureAD/1285248 · Managed HSM https://supportability.visualstudio.com/AzureAD/_wiki/wikis/AzureAD/1379881 · NetApp Files backup https://supportability.visualstudio.com/AzureBackup/_wiki/wikis/AzureBackup/1818012 · Resiliency Manager https://supportability.visualstudio.com/AzureSiteRecovery/_wiki/wikis/AzureSiteRecovery/2674966

---

## Quick-reference verdict table

| Scenario | Trigger | Owner | Condition for VM scope |
|---|---|---|---|
| OS boot stall | Boot hangs at OS screen | OS team | Only if pre-kernel (GRUB/BCD) failure |
| SQL slow query | SQL performance issue on VM | SQL team | Only if platform I/O latency confirmed |
| AKS node NotReady | AKS node unreachable | AKS team | Only if VM allocation fails |
| Azure Files mount fail | Cannot mount SMB/NFS share | Azure Files team | Only if host NIC/DNS/network issue |
| VM extension fail | Extension handler fails | Sub-extension team | VM scope only if framework install fails |
| SAP HANA failover | HSR failover event | SAP team | Only if host-level fault found |
| ADE extension fail | AzureDiskEncryption fails | Disk Encryption/KV team | VM scope only if agent can't install extension |
| **3rd Party OS/NVA** | Marketplace image issue | Vendor | VM scope for platform/LSI RCA only |
| **Migration (cross-region)** | Azure Resource Mover | Azure Backup/ASR team | VM scope for allocation issues |
| **Migration (cross-sub/RG)** | Move resources | VM team | VM team owns |
| **AKS allocation** | ZonalAllocationFailed | VM team (capacity) | AKS stays on collab for cluster-level |
| **AKS autoscale** | Cluster autoscaler issue | AKS team | VM scope only if VMSS scaling failed |
| **SAP workload** | SAP app/DB issue | ASW:SAP team | VM scope for platform fault RCA |
| **Terraform** | Deployment failure | ARM / RP team | VM scope if CRP operation failed |
| **IIS / Guest app** | App pool, ASP.NET issue | Servers / Dev Tools | VM scope only if platform event caused it |
| **⚠️ Service Fabric VMSS** | SF cluster node/scale issue | SF team drives risky ops | VM owns boot/ext/OS — collab SF before ANY stop/delete/resize |
| **Start/Stop — sub disabled** | VM won't start | Azure Subscription Mgmt | Out of VM scope |
| **Start/Stop — quota** | Quota exceeded | Azure Subscription Mgmt | Customer self-serves |
| **Start/Stop — boot/NIC/delete/resize** | Mgmt op failed | VM team | VM owns |
| **DevOps VMSS** | Scale set agent issue | DevOps team if ext-caused | VM owns platform-level |
| **Hotpatching — orchestration** | Patch deploy / portal | UMC | VM owns provisioning/restart/CLI-enable |
| **Cross-Tenant CMK** | Storage/disk CMK setup | VM POD (storage), Identity/Security (KV+identity) | VM owns storage-account/disk side |
| **VM Restore Points** | Backup fails / API fails | Backup (process) vs Compute (API) | Backup process = Azure Backup |
| **Storage scope check** | Is it storage? | No storage account = not storage | Blob/ADLS → PaaS Dev |
| **ASR / Site Recovery** | Replication/failover/DR | ABRS (Azure Backup & Recovery) | VM scope only for source/target VM host/allocation |
| **Bastion connect** | Black screen / login / connectivity | First-touch team scopes; VM ⇄ Networking collab | VM drives when packet reaches VM / CredSSP / host firewall |
| **Advisor** | Advisor blade or a recommendation | VM owns blade/UX; source service owns recommendation | "Advisor not working" = VM; "this recommendation" = source service |
| **Managed Identity on VM** | MI token/auth fails vs VM feature | Entra (identity) vs VM (consuming feature) | VM owns the feature/extension using a working MI |
| **Windows ESU** | EOL Win10 / Server 2012 under ESU | VM (limited support) | Security-update install/regression only; RCA/perf out of scope |
| **AVD B2B / FSLogix** | External guest login / Entra login ext / FSLogix Kerb | AVD + AAD + Azure Files split | AADLoginForWindows ext failure = AAD; AAD DS-joined B2B fail = by design |
| **Linux CVE / new cluster** | Patch a CVE / deploy new HA cluster | Out of case scope (best-effort) | Platform fault RCA still VM |
| **Adjacent services** | Copilot / Key Vault / HSM / ANF backup / Resiliency Hub | Owned elsewhere | ADE use of KV → VM; rest route/collab |
