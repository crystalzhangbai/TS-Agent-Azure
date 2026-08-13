# csswiki Project Routing — Worked Examples

Reference table for [`SKILL.md` §3 Step 2.5](../SKILL.md#step-25-route-csswiki-to-relevant-projects-topic-aware). Each row shows a representative keyword set and the resulting `project` list when the Step 2.5 routing rules are applied (without the max-4 cap kicking in — these are simple-to-medium cases).

For the max-4-projects cap rule and which projects to drop first when there are too many triggers, see the "Routing cap" blockquote in `SKILL.md` §3 Step 2.5.

## Examples

| Keywords | Routed project list |
|---|---|
| `RDP internal error MachineKeys` | `["AzureIaaSVM"]` (pure VM core) |
| `SNAT outbound connection drop` | `["AzureIaaSVM", "AzureNetworking"]` |
| `SAP HANA Pacemaker fencing SBD` | `["AzureIaaSVM", "AzureLinuxNinjas"]` |
| `MANA network adapter Linux SUSE` | `["AzureIaaSVM", "AzureNetworking", "AzureLinuxNinjas"]` |
| `MARS backup restore fails` | `["AzureIaaSVM", "AzureBackup"]` |
| `ASR replication health failure VM` | `["AzureIaaSVM", "AzureSiteRecovery"]` |
| `Managed Identity token 401` | `["AzureIaaSVM", "AzureAD"]` |
| `AKS pod CrashLoopBackOff containerd` | `["AzureIaaSVM", "AzureContainers"]` |
| `Azure Files SMB mount permission denied` | `["AzureIaaSVM"]` (Files = IaaS-team scope, no AzureDev) |
| `Azure File Sync server endpoint health error` | `["AzureIaaSVM"]` (File Sync = IaaS-team scope, no AzureDev) |
| `Storage Account firewall Private Endpoint VNet rule` | `["AzureIaaSVM"]` (SA networking = IaaS-team scope, no AzureDev) |
| `blob 503 ServerBusy throttling SAS download` | `["AzureIaaSVM", "AzureDev"]` (Blob → AzureDev) |
| `SQL Server AlwaysOn AG on Azure VM` | `["AzureIaaSVM", "AzureSQLVM", "SQLServerWindows"]` |
| `Ultra Disk IOPS limit` | `["AzureIaaSVM", "AzureStorageDevices"]` |
| `AVD session host FSLogix profile` | `["AzureIaaSVM", "WindowsVirtualDesktop"]` |
| `Windows BSOD INACCESSIBLE_BOOT_DEVICE` | `["AzureIaaSVM", "WindowsEE", "WindowsEEPreboot"]` |
| `Windows Server Failover Cluster CSV offline` | `["AzureIaaSVM", "WindowsSHA"]` |
| `NTFS volume corruption chkdsk` | `["AzureIaaSVM", "WindowsSHA"]` |
| `Windows Activation 0xC004F074 KMS host` | `["AzureIaaSVM", "WindowsDevicesDeployment"]` |
| `sysprep generalize fails 0x80073cf2` | `["AzureIaaSVM", "WindowsDevicesDeployment"]` |
| `Explorer.exe crash DWM black screen RDP session` | `["AzureIaaSVM", "WindowsUserExperience"]` |
| `Windows AD DC kerberos KRB_AP_ERR` | `["AzureIaaSVM", "WindowsDirectoryServices"]` |
| `VM disk IOPS performance (regular Premium SSD)` | `["AzureIaaSVM"]` (disk-side, NOT AzureDev or AzureStorageDevices) |

## How to use

When the user's query keywords match a row here, copy the project list directly. When the query straddles multiple rows, take the union and then apply the §3 Step 2.5 max-4 cap.

When the query doesn't match any row at all, default to `["AzureIaaSVM"]` and let Step 3's auto-broaden sweep handle the discovery.
