# Routing Disambiguation — csswiki Project Selection

Reference companion to [`SKILL.md §3 Step 2.5`](../SKILL.md#step-25-route-csswiki-to-relevant-projects-topic-aware). The 5 ambiguous routing cases below are where misrouting most commonly happens — each block names the exact symptom and the correct `project` list.

> Also see [`csswiki-project-routing-examples.md`](csswiki-project-routing-examples.md) for the 23-row keyword → routed-project lookup table covering the easy cases.

---

## 1. Storage Account topics — where to route

- **VM OS / data disk** (Premium SSD, Standard SSD, IOPS limits, disk error events, encryption at rest, ADE) → **`AzureIaaSVM`** only.
- **Ultra Disk / Premium SSD v2 / Elastic SAN / shared disk** → **`AzureIaaSVM` + `AzureStorageDevices`**.
- **Storage Account container-level topics** (SA create/delete, SKU change, replication setting, RBAC on SA, access keys), **Storage networking** (SA firewall, Private Endpoint, VNet rule, Service Endpoint), **Azure Files** (SMB/NFS file share, mount, quota, identity-based auth), **Azure File Sync** (server/cloud endpoint, tiering, sync error) → **`AzureIaaSVM` only — do NOT add `AzureDev`** (these belong to CSS IaaS team's scope; `AzureDev`/`Dev_Storage` is CSS Storage team and does not cover them).
- **Azure Blob / Queue / Table / ADLS Gen2** — any aspect of these data services (SAS, lifecycle, soft delete, immutable, throttling, performance, versioning, blob index tags, etc.) → **`AzureIaaSVM` + `AzureDev`** (CSS Storage team owns these products).

## 2. Azure block storage vs Windows storage stack

`AzureStorageDevices` covers **Azure-side** block storage products (Ultra Disk / Premium SSD v2 / Elastic SAN). `WindowsSHA` covers the **Windows-side** storage stack (NTFS / ReFS file systems, MPIO, iSCSI, Failover Cluster CSV, Storage Spaces Direct).

| Symptom | Routes to |
|---|---|
| VM cannot attach Ultra Disk | `AzureStorageDevices` |
| Windows volume shows RAW after reboot / NTFS corruption | `WindowsSHA` |
| Guest cluster (S2D) on Azure VMs with shared Premium SSD v2 | Both — `AzureStorageDevices` (the Azure block device) AND `WindowsSHA` (the WSFC/S2D layer) |

## 3. Backup vs Site Recovery

They're separate projects. Use `AzureBackup` for VM/file/SQL backup; use `AzureSiteRecovery` for VM replication / failover. (Verified via ADO REST API: both are independent `wellFormed` projects in the supportability org.)

## 4. SQL on VM vs PaaS SQL

`AzureSQLVM` + `SQLServerWindows` are for SQL Server running **inside a VM** (IaaS). Azure SQL DB / Azure SQL MI (PaaS) are different projects (`AzureSQLDB`, `AzureSQLMI`) and **NOT in the vm-knowledge-search routing table** — out of scope. If the user asks about a PaaS SQL issue, tell them to search those wikis directly or escalate to the SQL PaaS team.

## 5. Windows boot/recovery vs Windows deployment

`WindowsEE` + `WindowsEEPreboot` cover **boot / recovery** (WinPE, bcdedit, BSOD 0x7B, repair).
`WindowsDevicesDeployment` covers **OS deployment / image build / activation** (sysprep, image capture, KMS, Autopilot, MDM, drivers).

| Symptom | Routes to |
|---|---|
| Failed `sysprep /generalize` exit code 0x80073cf2 | `WindowsDevicesDeployment` |
| Failed `bootmgr` after reboot, BSOD 0x7B at boot | `WindowsEE` + `WindowsEEPreboot` |
| Windows Activation 0xC004F074 (KMS host unreachable) | `WindowsDevicesDeployment` |
| WinPE boot media doesn't recognize NVMe disk | `WindowsEE` + `WindowsEEPreboot` |

---

## 🧢 Routing cap — max 4 projects per `project` list (prevents ranking dilution)

- **Always include `AzureIaaSVM`** (baseline, counts toward the 4); then add up to 3 topic-specific projects.
- If ≥4 trigger rows fire, **prefer projects where the actual symptom lives** in this priority order:
  1. **First tier** — Linux/SAP HA, SiteRecovery, Backup, SQL on VM, AVD, AzureAD, Containers
  2. **Second tier** — StorageDevices, Networking, StrategicWorkloads
  3. **Third tier** — Windows deep-stack (WindowsPerformance / Networking / SHA / UX / Directory / Devices / EE / EEPreboot)
- Dropped projects get picked up automatically by the Step 3 auto-broaden sweep if results come back thin.

---

## Why these disambiguations exist

Most routing mistakes come from **assuming the project name is descriptive** — `AzureDev` sounds like it covers "Azure storage", but it's actually the CSS Storage team's scope (Blob/Queue/Table/ADLS) and explicitly does NOT own Azure Files / File Sync / Storage Account networking. Similarly, `WindowsDevicesDeployment` sounds like "Windows things that get deployed" but is narrowly about the deployment/imaging pipeline, not boot recovery. The disambig blocks here encode the actual team scopes verified against ADO REST API + historical case routing.

Bad routing wastes one round-trip (search returns nothing or noise), then forces the Step 3 auto-broaden sweep. Correct routing lands the hit on the first call.
