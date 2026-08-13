# Linux / Cluster Log Analysis Reference

> Domain knowledge for Linux guest OS log analysis. Pull this when analyzing Linux syslog / dmesg / journal / OOM / kernel panic / waagent / cloud-init / sosreport / supportconfig / Pacemaker / Nginx / K8s logs.
> **Boot failures** (GRUB / fstab / initramfs / kernel panic / serial console): also load [references/boot-troubleshooting.md](boot-troubleshooting.md) for the repair workflow and Repair VM procedure.
> This is a reference; combine its log location tables and error-pattern catalog with your own `view` / `grep` work. It does not impose a fixed pipeline.

## Contents

- [Log File Quick Reference](#log-file-quick-reference)
- [Error Patterns](#error-patterns) (general)
- [Error Patterns — Performance / Memory](#error-patterns--performance--memory)
- [Error Patterns — Network (OS layer)](#error-patterns--network-os-layer)
- [Error Patterns — Azure Agent / Provisioning](#error-patterns--azure-agent--provisioning)
- [Error Patterns — Pacemaker / Corosync (Linux cluster)](#error-patterns--pacemaker--corosync-linux-cluster)
- [Error Patterns — Nginx / Apache](#error-patterns--nginx--apache)
- [Error Patterns — Kubernetes / Container](#error-patterns--kubernetes--container)
- [Analysis Decision Tree](#analysis-decision-tree)
- [Azure Diagnostics Supplement](#azure-diagnostics-supplement)
- [Azure IID (Inspect IaaS Disk) for Linux](#azure-iid-inspect-iaas-disk-for-linux) — Linux-only details; see also [iid-package-layout.md](iid-package-layout.md) for the cross-platform shared rules
- [sosreport Directory Layout (RHEL/CentOS/Fedora)](#sosreport-directory-layout-rhelcentosfedora)
- [supportconfig Directory Layout (SUSE/SLES)](#supportconfig-directory-layout-susesles)
- [Scenario → File Mapping Table](#scenario--file-mapping-table)
- [Log → Config Cross-Reference](#log--config-cross-reference)
- [Log Collection Commands Quick Reference](#log-collection-commands-quick-reference)
- [Cross-Platform Related Skills](#cross-platform-related-skills)
- [AzureIaaSVM Wiki TSG References](#azureiaasvm-wiki-tsg-references)

---

## Log File Quick Reference

| Layer | Log type | Key path | Distro notes |
|---|---|---|---|
| OS | syslog | `/var/log/syslog` | Ubuntu/Debian |
| OS | messages | `/var/log/messages` | RHEL/CentOS/SLES |
| OS | Kernel log | `dmesg`, `/var/log/kern.log` | kern.log only on Ubuntu/Debian |
| OS | systemd journal | `/var/log/journal/`, `journalctl` export | systemd distros |
| OS | Auth log | `/var/log/auth.log` | Ubuntu/Debian |
| OS | Security log | `/var/log/secure` | RHEL/CentOS |
| OS | Boot log | `/var/log/boot.log` | RHEL/CentOS |
| OS | Audit log | `/var/log/audit/audit.log` | SELinux environments (RHEL/CentOS) |
| OS | Kdump | `/var/crash/` | When kdump is configured |
| Azure | waagent | `/var/log/waagent.log` | All Azure Linux VMs |
| Azure | cloud-init | `/var/log/cloud-init.log` | cloud-init VMs |
| Azure | Extension logs | `/var/log/azure/` | All Azure Linux VMs |
| Azure | Serial Console | Azure Portal > Serial Console | All Azure VMs |
| Azure | GRUB config | `/boot/grub2/grub.cfg` | Varies by distro |
| Azure | fstab | `/etc/fstab` | All |
| Cluster | Pacemaker | `/var/log/pacemaker.log`, `/var/log/cluster/corosync.log` | |
| Cluster | Corosync | `/var/log/corosync.log` | |
| Web | Nginx | `/var/log/nginx/access.log`, `/var/log/nginx/error.log` | |
| Web | Apache | `/var/log/apache2/error.log`, `/var/log/httpd/error_log` | |
| Container | K8s pod logs | `kubectl logs <pod> --previous` | |
| Container | kubelet | `/var/log/messages` or `journalctl -u kubelet` | |

---

## Error Patterns

### OS — OOM Killer

```
Out of memory: Kill process <pid> (<name>) score <n> or sacrifice child
Killed process <pid> (<name>) total-vm:<n>kB
```

- **Meaning**: memory exhausted; the kernel force-killed a process
- **Impact correlation**: process killed → service disruption, database connections dropped (see correlation-rules.md rule 1)

### OS — Kernel Panic

```
Kernel panic - not syncing: <reason>
BUG: unable to handle kernel NULL pointer dereference
```

- **Meaning**: fatal kernel error; the system halts
- **Impact correlation**: VM / host reboot; all services interrupted

### OS — Disk I/O errors

```
blk_update_request: I/O error, dev <sda>, sector <n>
EXT4-fs error (device <sda>): <function>
Buffer I/O error on dev <sda>, logical block <n>
```

- **Meaning**: disk read/write failure (physical failure or driver issue)
- **Impact correlation**: filesystem corruption, database write failure (see correlation-rules.md rule 2)

### OS — Systemd service failure

```
<service>.service: Main process exited, code=exited, status=<n>/<sig>
<service>.service: Failed with result 'exit-code'
Failed to start <Service Description>
```

### OS — SSH authentication failure

```
Failed password for <user> from <ip> port <port> ssh2
Invalid user <user> from <ip>
Connection closed by authenticating user <user> <ip> [preauth]
```

- **Meaning**: brute-force attempt or authentication misconfiguration

### OS — SSH connection / configuration issues

| Pattern (grep string) | Meaning | Fix |
|------------------------|---------|-----|
| `Connection refused` | SSH daemon not running | `systemctl start sshd` |
| `Connection timed out` | Network blocked | Check NSG (VM_Graph_Reader) |
| `Permission denied (publickey)` | SSH key auth failed | Check authorized_keys permissions (700/600) |
| `PAM: pam_open_session: Too many open files` | FD limit exhausted | Increase limits.conf limits |
| `no hostkeys available -- exiting` | Host key missing | Regenerate with `ssh-keygen -A` |
| `This account is currently not available` | Shell set to nologin | `usermod -s /bin/bash <user>` |

---

## Error Patterns — Performance / Memory

### OS — Additional performance patterns

| Pattern (grep string) | Meaning | Fix |
|------------------------|---------|-----|
| `blocked for more than 120 seconds` | I/O hung; process stuck waiting on disk | Check disk health; review iostat |
| `page allocation failure: order:` | Memory fragmentation; cannot allocate contiguous pages | Reboot; check for memory leaks |
| `EDAC MC: error` | Hardware ECC memory error | Platform issue, check VM_Kusto_Query |

---

## Error Patterns — Network (OS layer)

| Pattern (grep string) | Meaning | Fix |
|------------------------|---------|-----|
| `Temporary failure in name resolution` | DNS resolution failed | Check `/etc/resolv.conf` |
| `eth0: link is not ready` | NIC link down | Check Accelerated Networking |
| `nf_conntrack: table full, dropping packet` | Connection tracking table full | `sysctl -w net.netfilter.nf_conntrack_max=262144` |

---

## Error Patterns — Azure Agent / Provisioning

### waagent issues

| Pattern (grep string) | Meaning | Fix |
|------------------------|---------|-----|
| `Failed to provision the vm` | VM provisioning failed | Inspect cloud-init.log and waagent.log for the detailed error |
| `Error mounting dvd` | Cannot mount the ISO configuration disc | Check that the Hyper-V kernel modules are loaded |
| `Wire server is not responding` | Cannot reach 168.63.129.16 | Verify routing (`ip route`) and firewall rules |
| `GoalState error` | Goal-state fetch failed | `systemctl restart walinuxagent` |

### cloud-init issues

```
cloud-init: error: DataSourceAzure: unable to obtain DHCP address
cloud-init: error: Failed to retrieve Instance Metadata
```

- **Meaning**: VM cannot fetch metadata from Azure during init
- **Check**: `cloud-init status --long`, network config, DHCP client state

---

## Error Patterns — Pacemaker / Corosync (Linux cluster)

### Fencing triggered

```
stonith: <node> will be fenced
Scheduling Node <node> for STONITH
```

- **Meaning**: node is forcibly fenced — usually triggered by heartbeat timeout or resource failure
- **Impact correlation**: resources fail over to another node (see correlation-rules.md rule 8)

### Resource start failure

```
<resource>_start_0 on <node> 'unknown error' (1)
<resource>_monitor_0 on <node> 'not running' (7)
```

- **Common causes**: fencing agent misconfigured, resource dependency not met

### Corosync heartbeat loss

```
TOTEM: A processor failed, forming new configuration
corosync[<pid>]: [TOTEM ] A new membership
```

- **Meaning**: cluster node communication broken; triggers re-election (see correlation-rules.md rule 9)

---

## Error Patterns — Nginx / Apache

### Upstream connection failure

```
connect() failed (111: Connection refused) while connecting to upstream
upstream timed out (110: Connection timed out) while reading response header
no live upstreams while connecting to upstream
```

- **Impact correlation**: frontend returns 502/503; see correlation-rules.md rule 6

### Permission / configuration errors

```
open() "<path>" failed (13: Permission denied)
directory index of "<path>" is forbidden
```

---

## Error Patterns — Kubernetes / Container

### Pod OOMKilled

```
OOMKilled
Reason: OOMKilled
Exit Code: 137
```

- **Meaning**: container killed for exceeding its memory limit
- **Impact correlation**: pod restarts; if restart count exceeds the limit it enters CrashLoopBackOff

### CrashLoopBackOff

```
Back-off restarting failed container
CrashLoopBackOff
```

**Diagnosis**:
```bash
kubectl describe pod <pod-name> -n <namespace>   # inspect Events and Last State
kubectl logs <pod-name> --previous               # view logs from the previous crash
```

### Node NotReady

```
node/<node> condition: Ready=False
Taint node.kubernetes.io/not-ready
```

- **Meaning**: node is unreachable or out of resources; pods on it will be evicted

---

## Analysis Decision Tree

```
Linux issue
├── VM / node reboot
│   ├── Search dmesg / syslog for kernel panic or OOM
│   ├── Check last reboot / journalctl --since to confirm reboot time
│   └── If Azure Diagnostics available → look for platform reboot events
│
├── Service unavailable
│   ├── systemctl status <service> + journalctl -u <service>
│   ├── Check OOM (was the service process killed by OOM Killer?)
│   └── Check disk I/O errors (do they affect the service's data directory?)
│
├── Cluster failover / fencing
│   ├── corosync.log → heartbeat timeout?
│   ├── pacemaker.log → fencing operation confirmation
│   ├── Check system clock (time jumps can falsely trigger fencing, see correlation-rules.md rule 3)
│   └── Check network (NIC state changes, see rule 4)
│
├── Web service errors (502/503)
│   ├── nginx error.log → upstream connection failure
│   ├── Trace back to whether backend processes crashed (OOM / service failure)
│   └── See correlation-rules.md rule 6
│
└── Container / K8s issues
    ├── kubectl describe pod → review recent Events for errors
    ├── kubectl logs --previous → last logs before the crash
    └── kubectl top node/pod → resource usage over limit?
```

---

## Azure Diagnostics Supplement

### VM platform reboot

```json
"operationName": "Microsoft.Compute/virtualMachines/restart"
"status": "Succeeded"
"initiatedBy": "platform"
```

### Disk attach failure

```json
"operationName": "Microsoft.Compute/virtualMachines/attachDataDisk"
"status": "Failed"
"error": { "code": "AttachDiskWhileBeingDetached" }
```

### RBAC permission denied

```json
"authorization": { "action": "..." }
"properties": { "statusCode": "Forbidden" }
```

---

## Azure IID (Inspect IaaS Disk) for Linux

When the input is an Azure IID package for a Linux VM, the layout differs significantly from sosreport / supportconfig — IID is a **curated subset of the OS disk's filesystem tree** extracted by Azure offline (via Guestfish), not a tool-generated snapshot from inside a running OS.

> The IID skeleton (`diskinfo.txt` / `results.txt` / `scanfilelist.tsv` / `device_N/`), the `results.txt` reading rules, the FAILED-whitelist principle, the CredentialScanner footer, and the IID + ConsoleLog pairing pattern are **identical across Linux and Windows** — see [`iid-package-layout.md`](iid-package-layout.md) for the shared rules.
>
> This section covers **Linux-only** specifics: case-dir naming, `device_0/{etc,var,usr}` content, Linux-specific FAILED whitelist, `var/log/` and `var/lib/waagent/` and `etc/` cheat sheets, and the Linux triage flow.

### Top-level layout of the case-logs folder

A case-logs folder containing a Linux IID download usually looks like this:

```
<caselogs>\<case-id>\
├── <region>-<timestamp>-...-InspectIaaSDisk-...zip                 # raw IID archive (~10–50 MB)
├── <region>-<timestamp>-...-InspectIaaSDisk-...\                   # auto-extracted directory (same name as zip)
└── <vmname>-azure-<region>-<timestamp>-...ConsoleLog_<hash>.log    # paired serial console log (~1–20 MB)
```

For Linux, the IID + serial ConsoleLog pairing matters more than usual because boot issues require both — see [iid-package-layout.md § "IID + ConsoleLog are usually collected as a pair"](iid-package-layout.md#iid--consolelog-are-usually-collected-as-a-pair).

### `device_N/` Linux content overview

```
device_0/                       # OS disk; data disks (device_1+) almost never present
├── etc/                        # selected /etc files & subdirs
├── usr/                        # selected /usr/lib/systemd/ etc.
└── var/
    ├── log/                    # /var/log/* — the actual log files, read these
    └── lib/                    # /var/lib/waagent/, /var/lib/cloud/, /var/lib/NetworkManager/, /var/lib/dhclient/
```

Paths are RELATIVE (no leading `/`) — sosreport convention. See [iid-package-layout.md § "Path convention"](iid-package-layout.md#path-convention--relative-not-absolute).

### Linux-specific FAILED whitelist (in `results.txt`)

The shared principle is in [iid-package-layout.md § "FAILED-line whitelist principle"](iid-package-layout.md#the-failed-line-whitelist-principle); Linux-specific expected failures:

| FAILED pattern | Why it's expected |
|---|---|
| `/sys/class/infiniband/mlx5_ib*` | Only on HPC SKUs (HB/HC/ND series) |
| `/etc/netplan/*.yaml`, `/etc/network/interfaces*`, `/etc/ufw/*`, `/etc/ssh/sshd_config.d/*` | Ubuntu/Debian only |
| `/var/log/pacemaker*`, `/var/log/corosync*`, `/var/log/cluster/*` | HA cluster only |
| `/var/log/dpkg*` (Ubuntu) / `/var/log/dnf*` (newer RHEL) / `/var/log/zypp/history` (SUSE) | Distro-specific package managers |
| `/var/log/azure-proxy-agent/*`, `/var/log/rhuicheck.log` | Only if those agents are installed |
| `/var/lib/waagent/*/config/*.settings`, `*/status/*.status` | Only when extensions are installed |
| `Mounting .../mnt/resource FAILED` | Often expected (resource disk may legitimately not exist on some SKUs / Gen2 / no temp disk) |

**Real FAILED that matters** (same rule both platforms): root/`/boot` mount failures, missing `/etc/fstab` or `/etc/os-release`, corrupted filesystem UUIDs (other than BIOS-boot sda14).

### `device_0\var\log\` — Linux IID log files cheat sheet

| File | What it is | Common size | When to read |
|---|---|---|---|
| `messages` | RHEL/CentOS syslog (kern + system + apps) | **often hundreds of MB** — `grep` first, NEVER `view` full | Almost any issue |
| `messages-YYYYMMDD` | Rotated older syslog | varies | Issues older than current `messages` |
| `dmesg`, `dmesg.old` | Kernel ring buffer at last boot | 30–100 KB | Hardware / disk / network driver issues |
| `boot.log`, `boot.log-YYYYMMDD` | systemd boot stage messages | 15–200 KB | Boot failure / slow boot |
| `waagent.log` | Azure Linux Agent log (provisioning, extension install, goal state) | 1–10 MB | Extension failure, provisioning issue, agent unavailable |
| `cloud-init.log` | cloud-init phases (init, modules-config, modules-final) | 500 KB – 5 MB | First-boot provisioning, image migration (AWS→Azure), custom data |
| `secure`, `secure-YYYYMMDD` | SSH login / sudo / PAM | 100–500 KB | Cannot SSH, brute-force, sudo failure |
| `audit/audit.log` | SELinux audit | varies | SELinux denials |
| `yum.log` (RHEL/CentOS) / `dpkg.log` (Ubuntu) | Package install/update history | small | "Was kernel updated right before the crash?" timing questions |
| `cron`, `cron-YYYYMMDD` | Cron job execution log | varies | Cron failures, suspect cron caused the issue |
| `azure/` (subdir) | Azure extension handler logs (Custom Script, RunCommand, AAD, etc.) | varies | Extension failures (often missing if no extension was installed) |

### `device_0\var\lib\waagent\` — Azure Linux Agent state

| File / pattern | Meaning |
|---|---|
| `GoalState.<N>.xml`, `Incarnation`, `SharedConfig.xml` | Latest goal state pushed by Azure platform to this VM |
| `ovf-env.xml` | Initial provisioning XML (hostname, admin credentials hash, custom data) |
| `history\<YYYY-MM-DDTHH-MM-SS>__<incarnation>[-hash].zip` | ⭐ **Time-stamped archive of every past goal state.** Use this to answer "when did the platform push X to this VM" — each zip = one goal-state update (reimage, extension install, redeploy, NIC change, etc.). Filenames are sortable. |
| `WALinuxAgent-<version>\error.json` | Agent's own error records — small JSON, always quickly inspect |
| `event_status.json`, `fast_track.json` | Agent telemetry & fast-track state |
| `<extension-name>\` (e.g. `Microsoft.Azure.Extensions.CustomScript-2.x.x\`) | Per-extension config + status + handler.log (often absent in IID if no extensions installed) |

### `device_0\etc\` — high-value Azure-specific config files

| Path | What it tells you |
|---|---|
| `fstab` | ⭐ Mount config — first stop for boot failures, missing `nofail` on data disks, wrong UUID after disk swap, etc. |
| `crypttab` | LUKS-encrypted disk config (Azure Disk Encryption customers) |
| `waagent.conf` | Azure Linux Agent config (Provisioning.Enabled, ResourceDisk.Format, AutoUpdate.Enabled, swap config, etc.) |
| `cloud/cloud.cfg` + `cloud/cloud.cfg.d/91-azure_datasource.cfg` | ⭐ cloud-init datasource — **if `datasource_list` lacks `Azure`, this is an AWS/GCP image running on Azure** (classic slow-boot / no-network root cause for migrated VMs) |
| `cloud/cloud.cfg.d/10-azure-kvp.cfg`, `05_logging.cfg` | Azure-specific cloud-init add-ons |
| `udev/rules.d/66-azure-storage.rules` | Azure data-disk symlinks (`/dev/disk/azure/scsi1/lunN`) |
| `udev/rules.d/68-azure-sriov-nm-unmanaged.rules` | Accelerated Networking — tells NetworkManager to ignore SR-IOV VF devices |
| `udev/rules.d/99-azure-hyperv-ptp.rules` | Hyper-V PTP clock source (time sync) |
| `udev/rules.d/99-azure-product-uuid.rules` | Azure product UUID exposure |
| `ssh/sshd_config` | SSH service config (port, PasswordAuth, AllowUsers, AllowGroups, etc.) |
| `centos-release` / `redhat-release` / `os-release` | Distribution + version |
| `resolv.conf`, `nsswitch.conf`, `hosts` | DNS resolution chain (often the root of "VM can't reach metadata service / 168.63.129.16" issues) |
| `sysctl.conf`, `sysctl.d/*` | Kernel tuning (look here for perf / TCP-stack / IP-forwarding questions) |
| `sudoers`, `sudoers.d/90-cloud-init-users` | Sudo policy (cloud-init creates the latter for the admin user) |
| `selinux/config` | SELinux enforcing/permissive/disabled state |
| `NetworkManager/`, `sysconfig/network-scripts/` | Network interface config (varies by distro) |

### Quick triage flow for a fresh IID Linux package

A *checklist*, not a rigid pipeline — skip steps the user has already scoped out. Steps 1–3 are universal (see [iid-package-layout.md § "Quick triage flow"](iid-package-layout.md#quick-triage-flow-any-platform)); step 4 is Linux-specific:

1. **`results.txt` top 30 lines** → confirm distro, OS version, mount status. Any `Mounting ... FAILED` for `/` or `/boot` means the disk has a serious problem and that's likely the answer.
2. **`results.txt` CredentialScanner statistics** (tail) → check that secrets weren't stripped (else some files in `device_N\` will be missing).
3. **`diskinfo.txt`** → check if any partition is at 100% used (`/var` full breaks logging; `/boot` full breaks kernel updates; `/` full breaks almost everything).
4. **Branch by user's actual question** (Linux-specific):
   - Boot issue → pair with the `ConsoleLog_*.log` in the same case folder + read `device_0\etc\fstab`, `etc\crypttab`, `var\log\boot.log`
   - Provisioning / first-boot → `var\log\cloud-init.log`, `var\log\waagent.log`, `etc\cloud\cloud.cfg.d\91-azure_datasource.cfg`, `var\lib\waagent\ovf-env.xml`
   - SSH issue → `etc\ssh\sshd_config`, `var\log\secure`, `etc\pam.d\sshd`
   - Crash / OOM / panic → `var\log\messages` (grep — file is large), `var\log\dmesg`, `var\log\dmesg.old`
   - Extension failure → `var\log\waagent.log`, `var\lib\waagent\<extension-name>\`, `var\log\azure\<extension>\`
   - Network → `etc\resolv.conf`, `etc\sysconfig\network-scripts\`, `etc\NetworkManager\`, `var\log\messages` (grep `NetworkManager|dhclient|VF|hv_netvsc`)
   - "When did the platform do X?" → enumerate `var\lib\waagent\history\*.zip` by timestamp, extract the suspect ones

---

## sosreport Directory Layout (RHEL/CentOS/Fedora)

When the input is a sosreport archive, use the following directory layout to locate logs and config files:

```
sosreport-<hostname>-<date>/
├── date, hostname, uname, uptime       # basic system info
├── installed-rpms                       # installed packages
├── free, df, mount, ps                  # system state snapshot
├── dmidecode                            # hardware inventory
├── proc/                                # /proc snapshot
│   ├── meminfo, cpuinfo, cmdline
│   └── ...
├── etc/                                 # config files
│   ├── fstab, resolv.conf, os-release
│   ├── sysconfig/
│   └── ...
├── var/log/                             # log files (primary log source)
│   ├── messages                         # syslog (RHEL)
│   ├── secure                           # auth log (RHEL)
│   ├── dmesg, boot.log, cron
│   ├── audit/audit.log
│   └── ...
└── sos_commands/                        # plugin command output
    ├── boot/                            # bootloader, initramfs
    ├── block/                           # lsblk, blkid, fdisk
    ├── filesys/                         # mount, df, fstab
    ├── kernel/                          # sysctl, lsmod, dmesg
    ├── logs/                            # journalctl export
    ├── memory/                          # free, vmstat, slab
    ├── networking/                      # ip, ss, iptables, ethtool
    ├── process/                         # ps, top
    ├── systemd/                         # systemctl output
    ├── yum/                             # yum history, repolist
    ├── cron/                            # crontab list
    ├── pam/                             # PAM config
    ├── selinux/                         # SELinux state
    └── ...
```

---

## supportconfig Directory Layout (SUSE/SLES)

supportconfig uses a flat text-file structure:

```
nts_<hostname>_<date>/
├── basic-environment.txt      # uname, hostname, uptime, os-release
├── basic-health-check.txt     # system health summary
├── boot.txt                   # GRUB, initrd, boot config
├── messages.txt               # /var/log/messages contents
├── security-access.txt        # auth logs (secure, wtmp, btmp)
├── hardware.txt               # lspci, dmidecode, lscpu
├── disk.txt                   # disks, partitions, LVM, multipath
├── fs-diskio.txt              # filesystem, mount, df, I/O stats
├── memory.txt                 # free, vmstat, /proc/meminfo
├── network.txt                # ip, routes, firewall, DNS
├── dns.txt                    # /etc/resolv.conf, dig output
├── modules.txt                # loaded kernel modules
├── proc.txt                   # /proc entries
├── rpm.txt                    # installed packages (rpm -qa)
├── chkconfig.txt              # systemd unit status
├── systemd.txt                # systemd journal, units, timers
├── cron.txt                   # cron config and log entries
├── crash.txt                  # crash dump info (if any)
├── ntp.txt                    # NTP/chrony time sync
├── pam.txt                    # PAM config
├── updates.txt                # zypper / patch config
├── lvm.txt                    # LVM details
├── nfs.txt                    # NFS config
├── sysconfig.txt              # /etc/sysconfig entries
├── etc.txt                    # key /etc/ file contents
├── y2log.txt                  # YaST log
├── plugin-suse_public_cloud.txt  # SUSE Public Cloud plugin output
└── public_cloud/              # SUSE Public Cloud plugin subdirectory
    ├── cloudregister.txt      # /var/log/cloudregister — registration attempts and errors
    ├── regionserverclnt.txt   # /etc/regionserverclnt.cfg — region server config
    ├── repositories.txt       # /etc/zypp/repos.d/* contents
    ├── services.txt           # /etc/zypp/services.d/* contents
    ├── credentials.txt        # /etc/zypp/credentials.d/* contents
    ├── instanceinit.txt       # cloud-init + waagent logs
    ├── metadata.txt           # Azure instance metadata (azuremetadata output)
    ├── frameworkpackages.txt   # cloud-related RPM packages
    ├── updateinfrastructure.txt # zypper ref output
    ├── registrationcache.txt  # /var/cache/cloudregister contents
    ├── osrelease.txt          # /etc/os-release
    └── hosts.txt              # /etc/hosts
```

---

## Scenario → File Mapping Table

Based on the input format, look up logs and config files in the right location:

| Scenario | Live System | sosreport | supportconfig |
|----------|-------------|-----------|---------------|
| System crash / reboot | kern.log, dmesg, journalctl | `var/log/messages`, `var/log/dmesg`, `sos_commands/kernel/`, `sos_commands/logs/` | `messages.txt`, `crash.txt`, `boot.txt` |
| Auth / SSH failure | auth.log / secure | `var/log/secure`, `var/log/audit/audit.log`, `sos_commands/pam/` | `security-access.txt`, `pam.txt` |
| Service failure | journalctl -u, syslog | `var/log/messages`, `sos_commands/systemd/`, `sos_commands/logs/` | `messages.txt`, `systemd.txt`, `chkconfig.txt` |
| Disk / filesystem error | kern.log, dmesg | `var/log/messages`, `var/log/dmesg`, `sos_commands/block/`, `sos_commands/filesys/` | `messages.txt`, `disk.txt`, `fs-diskio.txt` |
| OOM | kern.log, dmesg | `var/log/messages`, `var/log/dmesg`, `sos_commands/memory/` | `messages.txt`, `memory.txt` |
| Network issue | syslog, dmesg | `var/log/messages`, `sos_commands/networking/` | `messages.txt`, `network.txt`, `dns.txt` |
| Cron job failure | cron.log, syslog | `var/log/cron`, `sos_commands/cron/` | `cron.txt` |
| Boot failure | boot.log, dmesg | `var/log/boot.log`, `var/log/dmesg`, `sos_commands/boot/` | `boot.txt`, `messages.txt` |
| Package issue | dpkg.log / yum.log | `var/log/yum.log`, `sos_commands/yum/`, `installed-rpms` | `rpm.txt`, `updates.txt` |
| Hardware issue | dmesg | `dmidecode`, `var/log/dmesg`, `sos_commands/kernel/` | `hardware.txt`, `messages.txt`, `modules.txt` |
| Time sync | journalctl, chrony/ntp logs | `sos_commands/chrony/` or `sos_commands/ntp/` | `ntp.txt` |
| SELinux / security | audit.log | `var/log/audit/audit.log`, `sos_commands/selinux/` | `security-access.txt`, `messages.txt` |
| **Config: fstab / mounts** | `/etc/fstab`, `mount` | `etc/fstab`, `sos_commands/filesys/` | `fs-diskio.txt`, `etc.txt` |
| **Config: network / DNS** | `/etc/sysconfig/network-scripts/`, `/etc/resolv.conf` | `etc/sysconfig/network-scripts/`, `etc/resolv.conf`, `sos_commands/networking/` | `network.txt`, `dns.txt`, `sysconfig.txt` |
| **Config: firewall** | `iptables -L`, `firewalld` | `sos_commands/networking/`, `etc/sysconfig/iptables` | `network.txt` |
| **Config: sysctl / kernel** | `/etc/sysctl.conf`, `sysctl -a` | `etc/sysctl.conf`, `sos_commands/kernel/` | `proc.txt`, `etc.txt` |
| **Config: PAM / auth** | `/etc/pam.d/`, `/etc/ssh/sshd_config` | `etc/pam.d/`, `etc/ssh/`, `sos_commands/pam/` | `pam.txt`, `security-access.txt` |
| **Config: systemd units** | `/etc/systemd/`, `systemctl list-unit-files` | `etc/systemd/`, `sos_commands/systemd/` | `systemd.txt`, `chkconfig.txt` |
| **Config: GRUB / boot** | `/etc/default/grub`, `/boot/grub2/` | `etc/default/grub`, `sos_commands/boot/` | `boot.txt` |
| **Config: LVM / storage** | `pvs`, `vgs`, `lvs`, `/etc/lvm/` | `sos_commands/lvm2/`, `sos_commands/block/` | `lvm.txt`, `disk.txt` |
| **Config: NTP / time** | `/etc/chrony.conf`, `/etc/ntp.conf` | `etc/chrony.conf`, `sos_commands/chrony/` | `ntp.txt` |
| **Config: software sources** | `/etc/yum.repos.d/`, `/etc/zypp/` | `etc/yum.repos.d/`, `sos_commands/yum/` | `updates.txt`, `rpm.txt` |
| **SUSE cloud registration** | `/var/log/cloudregister`, SUSEConnect --status | N/A (RHEL family) | `public_cloud/cloudregister.txt`, `public_cloud/regionserverclnt.txt`, `plugin-suse_public_cloud.txt` |
| **Azure Agent (waagent)** | `/var/log/waagent.log`, journalctl | `var/log/waagent.log`, `sos_commands/logs/` | `public_cloud/instanceinit.txt`, `messages.txt` |

---

## Log → Config Cross-Reference

When analyzing an anomaly, always cross-check the related config file to confirm root cause:

| Log finding | Config to check |
|-------------|-----------------|
| Mount failure (dmesg/messages) | `fstab`, `sos_commands/filesys/` or `fs-diskio.txt` |
| Network unreachable / DNS failure | NIC config, `resolv.conf`, firewall rules |
| Service start failure | systemd unit file, service-specific config (under `etc/`) |
| Auth rejected | `sshd_config`, `pam.d/`, SELinux/AppArmor state |
| Kernel parameter issue | `sysctl.conf`, boot cmdline (`proc/cmdline` or `boot.txt`) |
| Storage / LVM error | LVM config, `fstab`, multipath config |
| Time drift / sync failure | `chrony.conf` or `ntp.conf`, timezone setting |

---

## Log Collection Commands Quick Reference

### System overview

```bash
uname -a && uptime && hostnamectl
journalctl -xb --no-pager
journalctl -p err -b --no-pager
dmesg -T | tail -100
systemctl --failed
```

### Boot & filesystem

```bash
df -h && mount && cat /etc/fstab
lsblk -f && blkid
cat /etc/default/grub
ls -la /boot/
```

### SSH & auth

```bash
systemctl status sshd && sshd -T
tail -100 /var/log/auth.log       # Ubuntu
tail -100 /var/log/secure         # RHEL
```

### Azure Agent

```bash
grep -i "error\|fail" /var/log/waagent.log
systemctl status walinuxagent && waagent --version
cloud-init status --long
ls -la /var/log/azure/
```

### Performance & memory

```bash
free -m && cat /proc/loadavg
grep -i "oom\|killed process" /var/log/syslog /var/log/messages 2>/dev/null
top -bn1 | head -20
iostat -xz 1 5
ss -tuln && ip addr show && ip route show
```

### Cron job analysis

```bash
# Cron execution log
grep CRON /var/log/syslog | tail -20          # Ubuntu/Debian
cat /var/log/cron | tail -20                   # RHEL/CentOS

# Cron jobs for a specific user
grep "CRON.*<username>" /var/log/syslog

# Cron errors
grep CRON /var/log/syslog | grep -iE "error|fail|cannot"
```

### Package analysis

```bash
# Recent package operations (Debian/Ubuntu)
tail -50 /var/log/dpkg.log
cat /var/log/apt/history.log | tail -50

# Recent package operations (RHEL/CentOS)
tail -50 /var/log/yum.log

# Check for broken packages
dpkg --audit                                   # Debian
yum check                                      # RHEL
```

### journalctl common filters

```bash
# By time range
journalctl --since "2024-01-01 00:00:00" --until "2024-01-01 23:59:59"

# By priority (0=emerg, 1=alert, 2=crit, 3=err, 4=warning)
journalctl -p err                              # errors and above
journalctl -p warning..err                     # warnings to errors only

# By service
journalctl -u sshd -u nginx                   # multiple services

# Kernel messages only
journalctl -k

# JSON output
journalctl -o json-pretty -n 5

# Journal disk usage
journalctl --disk-usage
```

---

## Cross-Platform Related Skills

| Skill | Purpose |
|-------|---------|
| **VM_Kusto_Query** | Query Azure platform logs; correlate host events (e.g. platform reboot, live migration) with customer OS timestamps |
| **VM_Graph_Reader** | Inspect VM configuration (disk, NIC, NSG) to verify log-analysis conclusions (e.g. is NSG blocking SSH?) |

---

## AzureIaaSVM Wiki TSG References

### Boot & filesystem

- `SME Topics/Linux on Azure/TSGs/RHEL7,8 Boot Recovery_Linux` — RHEL boot recovery
- `SME Topics/Linux on Azure/TSGs/Dracut initqueue Warning Could Not Boot_Linux` — Dracut / initramfs failure
- `SME Topics/Linux on Azure/TSGs/LinuxVM boot failure due to invalid kernel parameter_Linux` — invalid GRUB parameter
- `SME Topics/Linux on Azure/TSGs/Troubleshoot Empty Boot Directory_Linux` — empty /boot
- `SME Topics/Linux on Azure/TSGs/Initramfs partuuid Ubuntu 22.x Ubuntu 24.x_Linux` — Ubuntu PARTUUID issues
- `SME Topics/Linux on Azure/TSGs/Steps to boot Ubuntu VMs from older kernel_Linux` — boot from an older kernel
- `SME Topics/Linux on Azure/TSGs/Disks shuffled post reboot_Linux` — disk-name drift

### Kernel & crash

- `SME Topics/Linux on Azure/TSGs/Kernel Crash NMI Watchdog_Linux` — NMI watchdog crash
- `SME Topics/Linux on Azure/TSGs/Accelerated Networking causing kernel hang_Linux` — Accelerated Networking kernel hang
- `SME Topics/Linux on Azure/TSGs/Complete Guide to Linux kdump Setup_Linux` — kdump configuration
- `SME Topics/Linux on Azure/TSGs/Complete Guide to Linux kdump Analysis_Linux` — kdump analysis

### SSH & auth

- `SME Topics/Linux on Azure/TSGs/SSHLogin PAM TooManyOpenFIles ErrorinServiceModule SSHsessionImmediatedisconnection_Linux` — PAM FD exhaustion
- `SME Topics/Linux on Azure/TSGs/Unable To Login No Shell_Linux` — shell misconfiguration
- `SME Topics/Linux on Azure/TSGs/Brute Force_Linux` — brute-force detection
- `SME Topics/Linux on Azure/How Tos/Restart SSH Service_Linux` — restart SSH service

### Performance & disk

- `SME Topics/Linux on Azure/How Tos/Performance Troubleshooting_Linux` — performance analysis
- `SME Topics/Linux on Azure/How Tos/Configure Swap Space_Linux` — configure swap to prevent OOM
- `SME Topics/Linux on Azure/TSGs/IO delays while attaching or dettaching data disks_Linux` — disk I/O latency

### Agent & network

- `SME Topics/Linux on Azure/TSGs/Waagent Error Mounting DVD_Linux` — Agent DVD mount error
- `SME Topics/Linux on Azure/TSGs/Failure in Name Resolution_Linux` — DNS resolution failure
- `SME Topics/Linux on Azure/TSGs/Gateway not persistent_Linux` — gateway persistence

### Tools

- `Tools/VM assist for Linux_Tool` — automated Linux VM troubleshooting
- `Tools/Linux Perf Insights_Tool` — Linux VM performance analysis
