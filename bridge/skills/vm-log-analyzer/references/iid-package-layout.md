# Azure IID (Inspect IaaS Disk) — Shared Package Layout

> Cross-platform reference for the IID package format. IID dumps the **same skeleton** for Linux and Windows VMs — only the OS-specific content under `device_N/` differs.
> For OS-specific details: see [branch-linux.md § "Azure IID (Inspect IaaS Disk) for Linux"](branch-linux.md) and [branch-windows.md § "Azure IID (Inspect IaaS Disk) — Windows Package Layout"](branch-windows.md).

## Contents

- [What IID actually is](#what-iid-actually-is)
- [Top-level skeleton](#top-level-skeleton)
- [`results.txt` reading guide (universal)](#resultstxt-reading-guide-universal)
- [`scanfilelist.tsv` + CredentialScanner footer](#scanfilelisttsv--credentialscanner-footer)
- [The FAILED-line whitelist principle](#the-failed-line-whitelist-principle)
- [`diskinfo.txt`](#diskinfotxt)
- [`device_N/` numbering rule](#device_n-numbering-rule)
- [Path convention — RELATIVE, not absolute](#path-convention--relative-not-absolute)
- [IID + ConsoleLog are usually collected as a pair](#iid--consolelog-are-usually-collected-as-a-pair)
- [Quick triage flow (any platform)](#quick-triage-flow-any-platform)

---

## What IID actually is

**IID = Inspect IaaS Disk**, an Azure offline disk-inspection service. It detaches a snapshot of the customer VM's OS disk, mounts it via Guestfish on a Microsoft-side worker, runs a **manifest** (a fixed list of ~200–415 operations: `mount`, `ll`, `cat`, `copy`), then packages the results.

Two consequences flow from "fixed manifest":

1. The package is a **curated subset** of the OS disk filesystem tree — not the whole disk, not a runtime tool output. Don't expect every Linux/Windows path to be present.
2. **Many manifest operations are template-preset** for components the customer didn't install (HPC Pack, ServiceFabric, FSLogix, OpenSSH server, pacemaker, netplan). Their `FAILED` lines are **expected**, not problems to chase. See [the FAILED whitelist principle](#the-failed-line-whitelist-principle) below.

Common manifests: `diagnostic` (default), `provisioning`, `boot`. The active manifest is recorded in `results.txt` top section.

---

## Top-level skeleton

Every IID extraction (Linux or Windows) follows this exact 4-piece layout:

```
<IID-extract-root>/
├── diskinfo.txt              # df + statvfs — partition sizes, FS types, free space
├── results.txt               # ⭐ MAIN ANALYSIS FILE — full log of all manifest operations
├── scanfilelist.tsv          # files IID attempted to copy + success/failure
└── device_N/                 # per-disk filesystem subset (N starts at 0)
    └── <OS-specific content — see branch-linux.md or branch-windows.md>
```

That's it. If any of the four are missing, the extraction itself failed — treat as a broken package and ask for a re-collection.

---

## `results.txt` reading guide (universal)

`results.txt` is the IID service's execution log. **Always read the top ~30 lines FIRST** — they're the highest-signal section across both platforms, and they contain pre-analysis conclusions that save you from misdiagnosing the rest of the package.

The top section is structured (Linux example shown; Windows is structurally identical, just different distro/FS values):

```
Execution start time: 03:39:34.

========== Request Info ==========
Storage Acct: md-<hash>.z34.blob.storage.azure.net   ← customer's managed disk
Container/Vhd: /<container>/<vhd>
Manifest requested: diagnostic                        ← manifest type (diagnostic / provisioning / boot)
Inspect service Operational ID: <guid>
Guestfish version: 1.57.5.                            ← tool used to mount disk offline
========== End Request Info ==========

Filesystem Status:
/dev/sda1: xfs  [uuid=...]
/dev/sda2: xfs  [uuid=...]
/dev/sda14: unknown [uuid=]                           ← BIOS boot partition; "unknown" is normal
/dev/sda15: vfat [uuid=...]                           ← EFI system partition

Inspection Status:
/dev/sda2

Inspection Metadata for /dev/sda2
Type: linux                                            ← ⭐ OS family (linux / windows)
Distribution: centos                                   ← ⭐ distro (linux) or "windows" (Windows)
Product Name: CentOS Linux release 7.9.2009 (Core)     ← ⭐ OS version
                                                         (Windows shows e.g. "Windows Server 2012 R2 Datacenter")

Mount Points:                                          ← ⭐ mount results
/: /dev/sda2
/boot: /dev/sda1
/boot/efi: /dev/sda15
/mnt/resource: /dev/disk/cloud/azure_resource-part1
Mounting /dev/sda2 on / SUCCEEDED.
Mounting /dev/sda1 on /boot SUCCEEDED.
...
```

Three things to capture from this section before going further:

| Field | Why it matters |
|---|---|
| `Manifest requested` | Tells you what subset of paths the IID tool will have tried. `diagnostic` ≠ `boot` — don't expect all paths to exist. |
| `Inspection Metadata` (OS family + distro + version) | Decides which OS-specific reference (branch-linux.md or branch-windows.md) to pull. |
| `Mounting ... on / SUCCEEDED/FAILED` | If the root mount FAILED, you have a serious disk problem and no other file in the package will help — that IS the answer. |

The middle of `results.txt` is hundreds of `Executing Operation [N/total]` blocks. Skim the `ll <dir>` outputs for fast inventory of the OS disk without opening individual files. Skim the `copy` outputs for the FAILED/SUCCEEDED pattern.

---

## `scanfilelist.tsv` + CredentialScanner footer

`scanfilelist.tsv` is the list of files IID attempted to copy out, one per line, with a status column. The **tail of `results.txt`** also reports CredentialScanner statistics:

```
CredentialScanner: Statistics - No. Scanned Files: 1216, ..., No. Files Containing Secrets: 0, No. Files Removed: 0
```

What to look for:

- `No. Files Containing Secrets: 0` is what you want — non-zero means IID **redacted or removed files** that leaked credentials. Those files will be **missing from `device_N/`** even though they exist on the real VM. If you can't find a config file you expect, check this counter before assuming it was never there.
- `No. Files Removed: > 0` is more serious than `Redacted: > 0` — Removed = entire file gone; Redacted = file present but secrets masked.

---

## The FAILED-line whitelist principle

A normal IID extraction has many `FAILED` lines in `results.txt`. This is by design:

> **The IID manifest is a one-size-fits-all template. It tries paths for components / features / packages that a typical customer VM doesn't have. A path that doesn't exist returns FAILED, but it's not an error — it just means the customer didn't install that thing.**

Examples (full lists in branch-linux.md and branch-windows.md):
- **Linux**: HPC InfiniBand sysfs paths (only on HB/HC/ND SKUs), `/etc/netplan/*.yaml` (Ubuntu only), `/var/log/pacemaker*` (HA cluster only), distro-specific package logs (`dnf` vs `yum` vs `zypp`).
- **Windows**: `Microsoft-ServiceFabric%4*.evtx`, `Active Directory Web Services.evtx`, `Microsoft-Windows-FSLogix*.evtx`, `HPC Pack 2016/2019/...`, `OpenSSH%4*.evtx`, `Microsoft-Windows-BitLocker*.evtx`.

A typical Windows IID has **~50% FAILED operations** (~204 of 415 in observed cases). A typical Linux IID with no extensions installed has 30–40% FAILED. Don't be alarmed.

**FAILED lines that genuinely matter** (same rule both platforms):

- **`Mounting ... on / FAILED` or `... on /boot FAILED`** in the top "Mount Points" section → real boot/disk problem
- **Registry hive copy failed** (Windows: SOFTWARE/SYSTEM) or **core syslog copy failed** (Linux: `/var/log/messages` or `/etc/fstab` or `/etc/os-release`) → filesystem corruption or disk damage
- **A filesystem `/dev/sdXN: unknown [uuid=]`** for a partition other than the BIOS boot partition (sda14 on Gen2 Linux) → corrupted / unrecognized FS

Anything else FAILED — check against the platform-specific whitelist before bothering the customer.

---

## `diskinfo.txt`

Output of `df` + `statvfs` against the offline-mounted partitions. Always quickly scan for:

- Any partition at **100% used** (`/var` full breaks logging; `/boot` full breaks kernel updates; `/` full breaks almost everything).
- **Drive letter mapping** (Windows): shows which Linux device path corresponds to which Windows volume letter (e.g. `C: /dev/sda2`). Useful because IID exposes everything through Linux device paths.

---

## `device_N/` numbering rule

- `device_0` = the **OS disk** (boot partition + root). Almost always present.
- `device_1`, `device_2`, … = data disks. **Rare** — IID usually dumps only `device_0` because data disks are huge and often customer-owned data. If the customer has a problem on a data disk, you may need to ask for a manual collection rather than expect IID to grab it.

---

## Path convention — RELATIVE, not absolute

Same convention as sosreport: paths inside `device_N/` are **relative**, no leading `/` or `\`.

- Linux IID: log files at `device_0/var/log/...`, config at `device_0/etc/...`
- Windows IID: hives at `device_0/Windows/System32/config/...`, evtx at `device_0/Windows/System32/winevt/Logs/...`

Don't confuse with live-system absolute paths in customer reports — when the customer says "/var/log/messages", inside the IID it's `device_0/var/log/messages`.

---

## IID + ConsoleLog are usually collected as a pair

A case folder containing an IID download usually also contains a paired serial console log (Linux) or boot diagnostics screenshot (Windows). They complement each other:

| Source | What it gives you | What it can't tell you |
|---|---|---|
| **IID** | Static state of `/etc`, `/var/log`, registry hives, agent state as of the snapshot time | Anything happening on the running kernel; live process state; events after the snapshot |
| **ConsoleLog** / serial console | Live kernel messages, systemd unit timing, cloud-init output, BIOS/UEFI POST, BSOD screen | Anything outside the serial console scope (app logs, registry state) |

For **boot issues**, always look at both. IID alone can't tell you what happened on the running kernel; ConsoleLog alone can't tell you why `/etc/fstab` has a bad UUID.

---

## Quick triage flow (any platform)

A checklist, not a rigid pipeline — skip steps the user has already scoped out:

1. **`results.txt` top 30 lines** → confirm OS family + distro + version + mount status. Any `Mounting ... FAILED` for `/` or `/boot` means the disk has a serious problem and that's likely the answer.
2. **`results.txt` CredentialScanner tail** → confirm `Files Removed: 0`. If non-zero, some files in `device_N/` are intentionally missing.
3. **`diskinfo.txt`** → check for any partition at 100% used.
4. **Check the case-dir root for engineer pre-analysis files** (Windows: `findings.txt` / `system_errors.txt` / `xray_ISSUES-FOUND_*.txt`. Linux: less common but possible). Read them BEFORE manually drilling into raw `.evtx` or `messages` — they may have already solved the case.
5. **Branch by user's actual question** → follow the symptom-routing tables in branch-linux.md or branch-windows.md.

If `results.txt` top 30 lines are unreadable or absent, the IID extraction itself is broken — ask for a re-collection rather than try to work with a partial package.
