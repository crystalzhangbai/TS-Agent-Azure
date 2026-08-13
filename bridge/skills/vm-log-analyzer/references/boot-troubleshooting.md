# Linux Boot Failure Troubleshooting Reference

> Domain knowledge for Linux boot-failure analysis (GRUB errors, fstab mount failure, kernel panic, dracut warnings, serial console startup anomalies, VM cannot boot, emergency mode).
> Pull this together with `branch-linux.md` when the issue is boot-related. Boot failures often need the Repair VM procedure in §4 below.

---

## 1. Boot Flow Overview

```
BIOS/UEFI → GRUB Bootloader → Kernel + Initramfs → systemd (PID 1) → Multi-user target
```

| Boot stage | Action | Failure symptoms |
|------------|--------|------------------|
| **GRUB** | Loads kernel and initramfs from /boot | `error: no such partition`, GRUB rescue prompt |
| **Kernel Init** | Decompresses kernel, initializes hardware | Kernel panic, black screen, hang |
| **Initramfs/Dracut** | Loads disk drivers, finds and mounts root partition | `dracut-initqueue: Warning: Could not boot` |
| **Root Mount** | Mounts the real root filesystem | `VFS: Unable to mount root fs` |
| **systemd Init** | Starts services, mounts fstab entries | `emergency mode`, start job timeouts |

---

## 2. GRUB Recovery Steps

### 2.1 Recovery from the GRUB rescue prompt

```bash
grub rescue> ls                           # list partitions
grub rescue> ls (hd0,2)/boot/             # find kernel files
grub rescue> set root=(hd0,2)
grub rescue> set prefix=(hd0,2)/boot/grub2
grub rescue> insmod normal
grub rescue> normal                       # load normal GRUB
```

### 2.2 Rebuild GRUB from a Repair VM

```bash
# Mount the OS disk partitions
mount /dev/sdc2 /mnt/rescue          # root partition
mount /dev/sdc1 /mnt/rescue/boot     # boot partition
mount -o bind /dev /mnt/rescue/dev
mount -o bind /proc /mnt/rescue/proc
mount -o bind /sys /mnt/rescue/sys
mount -o bind /run /mnt/rescue/run

# Chroot and rebuild
chroot /mnt/rescue
grub2-mkconfig -o /boot/grub2/grub.cfg    # RHEL/CentOS
grub2-install /dev/sdc                     # install to MBR
# Ubuntu:
update-grub && grub-install /dev/sdc
exit
```

### 2.3 Boot from an older kernel

```bash
# List available kernels
awk -F\' '/menuentry / {print }' /boot/grub2/grub.cfg   # RHEL
# Set the default kernel (0-indexed)
grub2-set-default 1
grub2-mkconfig -o /boot/grub2/grub.cfg
```

---

## 3. Fstab Mount Failure Fixes

### 3.1 Common issues

| Issue | Fix |
|-------|-----|
| Wrong UUID | Update from `blkid` output |
| Missing disk | Remove the entry or add `nofail` |
| Wrong filesystem type | Correct based on `blkid` |
| Filesystem corruption | Run `fsck` from the rescue VM |

### 3.2 Fix from a Rescue VM

```bash
mount /dev/sdc2 /mnt/rescue
cat /mnt/rescue/etc/fstab          # view current config
blkid /dev/sdc*                     # get correct UUIDs
vi /mnt/rescue/etc/fstab           # fix entries
# Best practice: use UUID= and add nofail for non-root partitions
# UUID=xxx /data ext4 defaults,nofail 0 2
```

### 3.3 Emergency mode recovery (Serial Console)

```bash
mount -o remount,rw /
vi /etc/fstab                       # fix the offending entry
systemctl daemon-reload
reboot
```

### 3.4 Device-name drift

Disk device names (/dev/sdb, /dev/sdc) can change after a reboot. Always use UUID= in fstab:

```bash
# Wrong:   /dev/sdb1  /data  ext4  defaults  0  2
# Correct: UUID=12345678-...  /data  ext4  defaults,nofail  0  2
blkid /dev/sdb1    # look up the UUID
```

---

## 4. Kernel Panic Analysis

### Common panic types

| Panic message | Likely cause | Action |
|---------------|--------------|--------|
| `VFS: Unable to mount root fs on unknown-block(0,0)` | Root device not found | Verify GRUB `root=` matches `blkid`; rebuild initramfs |
| `Attempted to kill init!` | PID 1 crashed; binary corrupted | Verify systemd integrity from a rescue VM |
| `Out of memory and no killable processes` | Memory fully exhausted | Resize the VM; configure swap |
| `BUG: soft lockup - CPU#X stuck` | CPU stuck in kernel code | Update kernel; check drivers |
| `NMI watchdog: Watchdog detected hard LOCKUP` | CPU frozen | Check platform events (VM_Kusto_Query); update kernel |

### Kdump analysis

```bash
systemctl status kdump              # verify kdump is running
ls -la /var/crash/                  # find crash dump files
cat /var/crash/*/vmcore-dmesg.txt | tail -50  # quick look at the crash log

# Deep analysis with the crash tool
crash /usr/lib/debug/lib/modules/$(uname -r)/vmlinux /var/crash/*/vmcore
# crash> bt     # backtrace
# crash> log    # kernel log
# crash> ps     # process list
```

---

## 5. Initramfs / Dracut Issues

### Symptoms

- `dracut-initqueue: Warning: Could not boot.`
- `Warning: /dev/disk/by-uuid/<UUID> does not exist`
- `Dropping to debug shell` → `dracut:/#`
- Ubuntu: `ALERT! /dev/disk/by-uuid/<UUID> does not exist`

### Root causes

1. **UUID mismatch**: root partition UUID changed but GRUB / initramfs still references the old UUID
2. **Missing drivers**: initramfs lacks the disk controller driver
3. **Corrupted initramfs**: file truncated or damaged
4. **PARTUUID change**: GPT/MBR was modified

### Recovery: rebuild initramfs

```bash
# From a rescue VM chroot:
# RHEL/CentOS:
dracut -f --add-drivers "hv_storvsc hv_vmbus" /boot/initramfs-$(uname -r).img $(uname -r)

# Ubuntu/Debian:
update-initramfs -u -k all

# Fix UUID mismatch:
blkid /dev/sdc2                           # get the actual UUID
vi /etc/default/grub                      # update root=UUID=<new>
grub2-mkconfig -o /boot/grub2/grub.cfg    # RHEL
update-grub                                # Ubuntu
```

---

## 6. Serial Console Boot Diagnosis

| Screen content | Meaning | Next step |
|----------------|---------|-----------|
| GRUB menu | GRUB OK; issue is after GRUB | Watch for kernel-load errors |
| `grub>` or `grub rescue>` | GRUB broken | GRUB recovery (Section 2) |
| Stops after kernel messages | Kernel hung | Read the last message to locate the failing subsystem |
| `dracut:/#` prompt | Initramfs debug shell | Root-device issue (Section 5) |
| `You are in emergency mode` | Critical systemd mount failed | Fix fstab (Section 3) |
| Login prompt | Boot completed | Issue is SSH / network, not boot |
| No output / black screen | Serial console not configured | Enable it in GRUB config |

---

## 7. Repair VM Workflow

### Use Azure VM Repair (recommended)

```bash
az vm repair create --name <brokenVM> --resource-group <rgName> --verbose
# SSH into the repair VM, fix the issue
az vm repair restore --name <brokenVM> --resource-group <rgName> --verbose
```

### Manual workflow

```bash
# 1. Deallocate the broken VM
az vm deallocate --name <vm> --resource-group <rg>

# 2. Detach the OS disk and attach it as a data disk on a rescue VM
# 3. Mount and chroot
mount /dev/sdc2 /mnt/rescue
mount /dev/sdc1 /mnt/rescue/boot
for d in dev proc sys run; do mount -o bind /$d /mnt/rescue/$d; done
chroot /mnt/rescue

# 4. Fix (GRUB / fstab / initramfs / kernel / etc.)
# 5. Exit chroot, unmount, reattach the disk, start the VM
```

### Common repair scenarios

| Scenario | Steps |
|----------|-------|
| GRUB broken | Chroot → `grub2-install` → `grub2-mkconfig` |
| Fstab UUID wrong | Edit `/mnt/rescue/etc/fstab` → correct UUID from `blkid` |
| Missing kernel | Chroot → `yum reinstall kernel` |
| Initramfs corrupt | Chroot → `dracut -f` / `update-initramfs -u` |
| Filesystem corruption | `fsck -y /dev/sdcX` (ext4) or `xfs_repair` (XFS) |
| SELinux relabel | Chroot → `touch /.autorelabel` → reboot |

### VM Assist for Linux

- Azure Portal: VM > Help + Support
- Automated log collection and analysis
- Identifies common boot, disk, network, agent issues
- Provides guided remediation steps
- Try this before a manual fix
