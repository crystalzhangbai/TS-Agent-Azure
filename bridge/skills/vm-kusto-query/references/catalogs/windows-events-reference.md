# Windows Events Reference — Host Node

> **Source TSG**: csswiki `/SME Topics/Unexpected Restarts/TSGs/Host Node Windows Events Investigation_Restarts`
>
> Master reference for Windows Event IDs surfaced on Azure host nodes (Hyper-V Root). Used by Playbook A (Restarts) and Playbook C (Performance). Cluster: `cluster("azcore.centralus.kusto.windows.net").database("Fa").WindowsEventTable` for raw host; `cluster("vmainsight").database("vmadb").WindowsEventTable` for vmadb-mirrored copy.
>
> **Note**: Single occurrences of specific events may NOT be conclusive — always cross-check at cluster level (see *Cluster-frequency check* at bottom) and against the false-positive list.

---

## TOC

- Host node issue indicators (storage / NTFS / StorPort / Hyper-V worker / VMMS / Resource Exhaustion / Event log)
- Disk health / latency / workload (local disks)
- False-positive errors / warnings
- VM status-change events on the host
- VM-impacting events on the host (StopDestroyWorkflowTimeout 70007, triple-fault, watchdog)
- Network events (mlx4eth63 / mlnx5 / Tcpip / NMAgent / VmSwitch / Vfpext / DNS)
- Cluster-frequency check pattern

---

## Host node issue indicators

| EventId | Provider | Channel | Message context |
|---|---|---|---|
| 1 | Blobcache | System | A fatal error was encountered performing an I/O operation to volume xx |
| 3 | Microsoft-Windows-FilterManager | System | Filter Manager failed to attach to volume; final status `0xC03A001C`. Volume unavailable until reboot |
| 7 | disk | System | The device has a bad block. Potential disk issue |
| 11 | LSI_SAS2i / LSI_SAS3i | System | The driver detected a controller error. Potential disk issue |
| 16 | vhddiskprt | System | xx.vhd failed to execute the specified IO request |
| 17 | vhddiskprt | System | 2-minute storage timeout (E17) — see STG-1 in `playbook-A-restarts-deep.md` |
| 41 | Microsoft-Windows-Kernel-Power | System | Unexpected host shutdown or power loss |
| 51 | disk | System | An error was detected on device during a paging operation |
| 52 | disk | System | Disk predicted failure; immediately back up and replace. Potential disk issue |
| 55 | Ntfs | System | Corruption discovered in the file system structure |
| 129 | Storahci / vhdmp / elxstor / HpCISSs3 / stornvme / LSI_SAS2i / LSI_SAS3i / VhdDiskPrt | System | Reset to device `\Device\RaidPort0` was issued. Potential disk or STORPORT driver issue. For NVMe → see HW-4 in `playbook-A-restarts-deep.md` and `asap-storage-queries.md` |
| 130 | Ntfs | System | The file system structure on a volume has now been repaired |
| 131 | Ntfs | System | The file system structure on a volume cannot be corrected |
| 140 | Microsoft-Windows-Ntfs | System | The system failed to flush data |
| 141 | Microsoft-Windows-Ntfs | System | IO failed because disk was full (software only) |
| 147 | Microsoft-Windows-Ntfs | Microsoft-Windows-Ntfs/Operational | An IO took more than 30000 ms |
| 149 | Microsoft-Windows-Ntfs | Microsoft-Windows-Ntfs/Operational | In the past xx seconds we had IO failures |
| 153 | disk | System | The IO operation at LBA xx for Disk xx was retried |
| 154 | disk | System | The IO operation at LBA xx for Disk xx failed due to a hardware error |
| 157 | disk | System | Disk xx has been surprise removed |
| 482 | ESENT | Application | An attempt to write to file at offset xx failed with system error... |
| 500 | Microsoft-Windows-StorPort | Microsoft-Windows-Storage-Storport/Operational | A request timed out for Storport Device |
| 504 (srbstatus 5) | Microsoft-Windows-StorPort | Microsoft-Windows-Storage-Storport/Operational | Unique IO errors — SRB status is busy |
| 504 (srbstatus 8) | Microsoft-Windows-StorPort | Microsoft-Windows-Storage-Storport/Operational | Unique IO error — SRB status returned device not found |
| 2004 | Microsoft-Windows-Resource-Exhaustion-Detector | System | Windows successfully diagnosed a low virtual memory condition (lists top consumers) |
| 6008 | Eventlog | System | Unexpected shutdown or power loss |
| 12030 | Microsoft-Windows-Hyper-V-Worker | Microsoft-Windows-Hyper-V-Worker-Admin | `<guid>` failed to start. Potential low memory condition |
| 12817 | Microsoft-Windows-Hyper-V-EmulatedStor | Microsoft-Windows-Hyper-V-Worker-Admin | See TSG `Poor_IO_Performance_on_WS2012R2` |

---

## Disk health / latency / workload (local disks)

| EventId | Provider | Channel | Message context |
|---|---|---|---|
| 146 | Microsoft-Windows-Ntfs | Microsoft-Windows-Ntfs/Operational | IO latency summary (workload indicator) |
| 505 | Microsoft-Windows-StorPort | Microsoft-Windows-Storage-Storport/Operational | Latency buckets 16/64/2048/**5120/5120+** ms. Non-zero in upper buckets → slow IO |
| 510 | Microsoft-Windows-StorPort | Microsoft-Windows-Storage-Storport/Operational | SMART data for SATA drive (health log) |
| 512 | Microsoft-Windows-StorPort | Microsoft-Windows-Storage-Storport/Operational | NVMe health log |

---

## False-positive errors / warnings (DO NOT escalate on these alone)

| EventId | Provider | Note |
|---|---|---|
| 0 | CMClientLib | Empty payload |
| 15 | TPM | "TPM hardware non-recoverable error" — benign on Azure hosts |
| 236 | Microsoft-Windows-Hyper-V-VmSwitch | "Failed to allocate virtual function for NIC … status = device not in a valid state" — benign **if followed by success Event 12584**. See OneNote: CloudNet › DataPath › `Failed to allocate virtual function event 236` |
| 1008 | Microsoft-Windows-Perflib | BITS perf DLL failed — benign |
| 1023 | Microsoft-Windows-Perflib | ASP.NET counter DLL load failure — benign |
| 3095 | Netlogon | "Computer configured as workgroup member" — benign |
| 5010 | vfpext | "Fail to write to windows event log" — benign |
| 5015 | vfpext | "Port already associated to a VM Context" — confirmed benign by Cloudnet PG (ICM 381150921) |
| 7000 | Service Control Manager | `mst64` service failed — digital signature warning, benign |

---

## VM status-change events on the host (Hyper-V-Worker / Hyper-V-Worker-Admin)

| EventId | Meaning |
|---|---|
| 18500 | VM started successfully (by HyperV) |
| 18502 | VM was turned off (forced — graceful-shutdown timeout, or ForceDelete by customer) |
| 18504 | VM shutdown by Host Node — `CleanShutdown by wvchelper, Reason: Stop call` (VM stop from Fabric or service healing) |
| 18508 | VM shutdown by the guest operating system |
| 18512 | VM reset by Host Node |
| 18514 | VM reset by guest operating system |

---

## VM-impacting events on the host

| EventId | Provider | Meaning | Likely cause |
|---|---|---|---|
| 14070 | Microsoft-Windows-Hyper-V-VMMS | Virtual machine quit unexpectedly | Platform |
| 14154 | Microsoft-Windows-Hyper-V-VMMS | Failed to remove device `Microsoft:Hyper-V:Virtual Hard Disk`: `0x80041024` | Platform — Storport driver bug (see STG-2 / MAINT-1) |
| 15140 | Microsoft-Windows-Hyper-V-VMMS | VM failed to turn off | Platform |
| 16000 | Microsoft-Windows-Hyper-V-VMMS | VMMS unexpected error: `Call was canceled by the message filter (0x80010002)` | Platform |
| 16010 | Microsoft-Windows-Hyper-V-VMMS | The operation failed | Platform |
| 18190 | Microsoft-Windows-Hyper-V-VMMS | Worker process health is **critical** | **StopDestroyWorkflowTimeout 70007** → see SW-8 in `playbook-A-restarts-deep.md` |
| 18524 | Microsoft-Windows-Hyper-V-Worker | `Nat-Worker` was paused for critical error | Platform — critical |
| 18540 | Microsoft-Windows-Hyper-V-Worker | VM reset — guest requested unsupported operation → **triple fault** | Guest OS |
| 18550 | Microsoft-Windows-Hyper-V-Worker | VM reset — unrecoverable VP error / **triple fault** in hypervisor | Platform |
| 18560 | Microsoft-Windows-Hyper-V-Worker | VM reset — unrecoverable VP error / **triple fault** | Platform |
| 18570 | Microsoft-Windows-Hyper-V-Worker | Guest executed intercepting instruction not supported by Hyper-V emulation | Guest OS |
| 18572 | Microsoft-Windows-Hyper-V-Worker | General protection exception during host emulation | Platform |
| 18590 | Microsoft-Windows-Hyper-V-Worker-Admin | VM fatal error — guest reported failure with ErrorCode0..4 | Likely Guest OS |
| 18600 | Microsoft-Windows-Hyper-V-Chipset | **VM watchdog timeout** and was reset | Guest OS |
| 18602 | Microsoft-Windows-Hyper-V-Worker-Admin | VM fatal error + memory dump generated. ErrorCode: `0x80` | Guest OS |
| 18604 | Microsoft-Windows-Hyper-V-Worker | VM fatal error but **memory dump could NOT be generated**. Error `0x2` | Guest OS |
| 18610 | Microsoft-Windows-Hyper-V-Worker-Admin | **Fatal virtual firmware error** with ErrorCode0..4 | Guest OS |
| 19050 | Microsoft-Windows-Hyper-V-VMMS | VM is not in a valid state to perform operation | **StopDestroyWorkflowTimeout** (SW-8) |
| 19060 | Microsoft-Windows-Hyper-V-VMMS | Failed `Modifying Resource` — VM is in `Moving Virtual Machine to Suspended State` | **StopDestroyWorkflowTimeout** (SW-8) |
| 19062 | Microsoft-Windows-Hyper-V-VMMS | Timed out waiting for `Modifying Resource` | **StopDestroyWorkflowTimeout** (SW-8) |
| 19064 | Microsoft-Windows-Hyper-V-VMMS | Could not perform `Modifying Resource` — another operation pending | **StopDestroyWorkflowTimeout** (SW-8) |
| 21102 | Microsoft-Windows-Hyper-V-Worker-Admin | Could not recover from migration failure | **StopDestroyWorkflowTimeout** (SW-8) |

### VMPHU correlation (used in MAINT-1)
- **18518** (Microsoft-Windows-Hyper-V-Worker) — VM `resumeTimestamp` after host plugin update
- **18598** (Microsoft-Windows-Hyper-V-Worker) — VM `saveTimestamp` before host plugin update
- `VMPHU_Downtime = resumeTimestamp - saveTimestamp`

---

## Network events on the host

**Owned by CloudNet (NOT RDOS)**. Common providers: `mlx4eth63`, `mlnx5`, `mlnx5hpc`, `mlxCx4Lx`, `Tcpip`, `AzureHostNetworking`, `NMAgent`, `Microsoft-Windows-Hyper-V-SynthNic`, `Microsoft-Windows-Hyper-V-VmSwitch`, `Vfpext`, `Microsoft-Windows-DNS-Client`.

| EventId | Provider | Message context |
|---|---|---|
| 2 | mlx4eth63 | Failed to initialize Mellanox ConnectX Ethernet Adapter |
| 2 | mlnx5hpc | ConnectX-5 Adapter failed to initialize due to FW initialization timeout |
| 7 | mlxCx4Lx | Adapter device successfully stopped |
| 14 | mlxCx4Lx / mlx4eth63 | Link is down (physical disconnect, damage, or other end-port down) |
| 20 | mlnx5 / mlnx5hpc | "EQ stuck on EQn 0x4. Attempting recovery." → see TSG `Ethernet Adapter EQ stuck on EQn 0x4` |
| 21 | mlx4eth63 | ConnectX-3 Pro "TX cq stuck on cqn #X uncompleted send #Y. HCA NIC will be reset" (`LogTxCqError`) |
| 22 | mlnx5 | "Receive completion handling timeout on RxQueue 0x25, Cq is armed. Attempting recovery." |
| 22 | Microsoft-Windows-Hyper-V-VmSwitch | Media disconnected on NIC `/DEVICE/xxx` |
| 86 | mlx4eth63 | VMQ "Rx ring stuck on cqn #X srqn #Y QueueID #Z" |
| 301 | NMAgent | `RESTORE_COMPLETED` — shown after NMAgent update/restart. Used to detect host plugin update completion (see MAINT-1) |
| 356 | NMAgent | "Save of VFP State Failure for Container: `<ContainerId>`" — see STG-3 (Live Migration VFPRestoreFailure) |
| 4227 | Tcpip | "TCP/IP failed to establish outgoing connection because the local endpoint was recently used to connect to the same remote endpoint" |

---

## Cluster-frequency check pattern (false-positive validation)

If a suspicious event appears, check whether it's fleet-wide (likely benign noise) or node-local (suspect platform issue):

```kusto
cluster("vmainsight").database("vmadb").WindowsEventTable
| where PreciseTimeStamp between (datetime({StartTime}) .. 24h)
    and Cluster == "{Cluster}"
    and EventId == "{EventId}"
    and Description has "{KeywordOrModuleName}"
| project TimeCreated, Cluster, NodeId, EventId, ProviderName, Description
| summarize count() by NodeId
```

- **Most nodes affected** → likely benign / known noise
- **Only the suspect NodeId** → real platform issue → cross-reference HW-x or SW-x sections in `playbook-A-restarts-deep.md`

---

## ASI cross-check

EEE RDOS WF Unexpected Restart page validates host event IDs visually: <https://asi.azure.ms/services/EEE%20RDOS/pages/WF%20Unexpected%20Restart>

---

## Cross-references

| When you need | Go to |
|---|---|
| Restart investigation by failure mode (SW/HW/STG/MAINT) | [`playbook-A-restarts-deep.md`](../playbooks/playbook-A-restarts-deep.md) |
| Storage performance / IO blip via storport events | [`playbook-C-performance-deep.md`](../playbooks/playbook-C-performance-deep.md) § STG-Perf |
| NVMe-specific event 129 (Storahci/stornvme) | `asap-storage-queries.md` |
| Network-specific event 356 (NMAgent) | [`playbook-A-restarts-deep.md`](../playbooks/playbook-A-restarts-deep.md) § STG-3 |
| StopDestroyWorkflowTimeout 70007 (events 18190, 19050, 19060, 19062, 19064, 21102) | [`playbook-A-restarts-deep.md`](../playbooks/playbook-A-restarts-deep.md) § SW-8 |
