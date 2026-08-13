# Lab Environment Configuration

> **Setup instruction**: Fill in the `<PLACEHOLDER>` values below with your actual lab environment details. This file is referenced by the vm-lab skill during execution.

> **Two usage models — read this first:**
> - **Fixed VMs (this file, OPTIONAL)** — long-lived Linux/Windows VMs you keep around for quick, repeated command validation. Filling in the placeholders below is only needed if you actually maintain such VMs. They can stay all-`<PLACEHOLDER>` if you only ever do scenario labs.
> - **Scenario labs (preferred for experiments)** — ephemeral, created from scratch into a dedicated `rg-<slug>-lab` and torn down when done. These do **not** use the fixed-VM entries below; they only need the **subscription IDs** and **region**. See *Scenario Lab — Build Ephemeral Experiments* in SKILL.md.
>
> The **subscriptions** section below applies to both models.

---

## Subscriptions

| Role | Name | Subscription ID | Monthly Credit | Notes |
|------|------|----------------|---------------|-------|
| **Primary** | $400 Subscription | `<PRIMARY_SUB_ID>` | $400 | Default for all operations |
| **Secondary** | $150 Subscription | `<SECONDARY_SUB_ID>` | $150 | Fallback when primary has restrictions |

### Known Limitations — Primary ($400)

| Limitation | Error Pattern | Workaround |
|------------|---------------|------------|
| Storage account access keys disabled | `StorageAccountAccessKeyDisabled` | Switch to secondary subscription |
| _Add more as discovered_ | | |

### Known Limitations — Secondary ($150)

| Limitation | Error Pattern | Workaround |
|------------|---------------|------------|
| Lower quota (smaller VM sizes only) | `QuotaExceeded` | Use smaller VM SKU or request quota increase |
| _Add more as discovered_ | | |

---

## Lab VMs

### Linux VM

| Property | Value |
|----------|-------|
| **VM Name** | `<LAB_LINUX_VM_NAME>` |
| **Resource Group** | `<LAB_LINUX_RG>` |
| **Resource ID** | `/subscriptions/<PRIMARY_SUB_ID>/resourceGroups/<LAB_LINUX_RG>/providers/Microsoft.Compute/virtualMachines/<LAB_LINUX_VM_NAME>` |
| **OS** | Ubuntu 22.04 LTS (or specify your distro) |
| **Size** | Standard_B2s (or specify) |
| **Public IP** | `<LAB_LINUX_IP>` |
| **SSH User** | `<LAB_LINUX_USER>` |
| **SSH Key** | `~/.ssh/id_rsa` (or specify path) |
| **SSH Command** | `ssh <LAB_LINUX_USER>@<LAB_LINUX_IP>` |
| **Subscription** | Primary ($400) |

### Windows VM

| Property | Value |
|----------|-------|
| **VM Name** | `<LAB_WIN_VM_NAME>` |
| **Resource Group** | `<LAB_WIN_RG>` |
| **Resource ID** | `/subscriptions/<PRIMARY_SUB_ID>/resourceGroups/<LAB_WIN_RG>/providers/Microsoft.Compute/virtualMachines/<LAB_WIN_VM_NAME>` |
| **OS** | Windows Server 2022 (or specify) |
| **Size** | Standard_B2s (or specify) |
| **Public IP** | `<LAB_WIN_IP>` |
| **Admin User** | `<LAB_WIN_USER>` |
| **RDP Port** | 3389 |
| **Subscription** | Primary ($400) |

---

## Network Configuration

| Property | Value |
|----------|-------|
| **VNet** | `<LAB_VNET_NAME>` |
| **Subnet** | `<LAB_SUBNET_NAME>` |
| **NSG** | `<LAB_NSG_NAME>` |
| **Allowed inbound** | SSH (22), RDP (3389) from your IP |

---

## Authentication

### Azure CLI
```powershell
# Verify logged-in account
az account show --query "{name:name, id:id, tenantId:tenantId}" -o table

# If not logged in
az login

# Set primary subscription
az account set --subscription "<PRIMARY_SUB_ID>"
```

### SSH Key (Linux VM)
```powershell
# Test SSH connectivity
ssh -o ConnectTimeout=5 <LAB_LINUX_USER>@<LAB_LINUX_IP> "hostname"
```

### Credentials Storage

**Never hardcode passwords or keys in skill files.** Use one of:

1. **SSH key** (Linux): Default `~/.ssh/id_rsa` — no password needed
2. **Environment variables** (Windows):
   ```powershell
   $env:LAB_WIN_PASSWORD = "..."   # Set in your terminal session, not in files
   ```
3. **az CLI credential** (az vm run-command): Uses your logged-in Azure identity — no VM-level credentials needed

---

## Quick Health Check

Run this to verify your lab environment is ready:

```powershell
# 1. Check Azure CLI login
az account show -o table

# 2. Check primary subscription
az account set --subscription "<PRIMARY_SUB_ID>"

# 3. Check Linux VM status
az vm get-instance-view --ids "<LINUX_VM_RESOURCE_ID>" --query "instanceView.statuses[1].displayStatus" -o tsv

# 4. Check Windows VM status
az vm get-instance-view --ids "<WINDOWS_VM_RESOURCE_ID>" --query "instanceView.statuses[1].displayStatus" -o tsv

# 5. Test SSH to Linux VM (if running)
ssh -o ConnectTimeout=5 <LAB_LINUX_USER>@<LAB_LINUX_IP> "echo 'SSH OK'"
```
