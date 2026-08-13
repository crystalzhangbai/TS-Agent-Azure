# Recipe — Offline OS-disk repair via a rescue VM

A worked example for the **"VM won't boot, fix the OS disk offline"** class of procedure.
Rehearse it in the lab before running it on a (lab) subscription, and hand the team a proven runbook.

## When to reach for this
A VM won't boot — bad `/etc/fstab`, broken GRUB, corrupt BCD/registry, full OS disk — and
you need to repair the OS disk **offline** by mounting it on a healthy *rescue* VM, then
validate that swapping it back boots.

> **Production shortcut**: `az vm repair create/run/restore` (the VM-repair extension)
> automates this whole flow. This recipe does it **manually** so each step is visible and
> teachable — and the manual flow is your fallback when the extension can't be used.

## Resource topology (the part the building-blocks table doesn't cover)
```
prob-vm (broken OS disk)  --snapshot-->  snap-probos
                                              |
                                  new disk from snapshot: repair-osdisk
                                              |
                          mount as DATA disk on rescue-vm (healthy, same region)
                                              |
                              fix offline (fsck / chkdsk / edit fstab / BCD / registry)
                                              |
                                  detach  -->  swap back as OS disk on prob-vm
```
Never repair the original disk in place — always work on a **snapshot-derived copy** so the
original stays recoverable.

## Steps
```powershell
# 0. (lab repro only) induce a boot fault so there's something to fix, e.g. a bad fstab mount:
az vm run-command invoke -g rg-rescue-lab -n prob-vm --command-id RunShellScript `
  --scripts "echo '/dev/sdz1 /data ext4 defaults 0 1' | sudo tee -a /etc/fstab; sudo reboot"

# 1. find + snapshot the problem OS disk
$os = az vm show -g rg-rescue-lab -n prob-vm --query "storageProfile.osDisk.managedDisk.id" -o tsv
az snapshot create -g rg-rescue-lab -n snap-probos --source $os

# 2. create a working managed disk from the snapshot (original stays untouched)
az disk create -g rg-rescue-lab -n repair-osdisk --source snap-probos

# 3. mount it as a DATA disk on a healthy rescue VM (same region/zone)
az vm disk attach -g rg-rescue-lab --vm-name rescue-vm --name repair-osdisk

# 4. repair offline via run-command on rescue-vm (root, no SSH — gotchas.md §5)
az vm run-command invoke -g rg-rescue-lab -n rescue-vm --command-id RunShellScript --scripts "@fix.sh"
#    Windows rescue-vm: RunPowerShellScript -> chkdsk X: /f, bcdedit on the offline BCD store,
#    or use a Hive Editor / reg load offline for SOFTWARE/SYSTEM hive edits.

# 5. detach the repaired disk
az vm disk detach -g rg-rescue-lab --vm-name rescue-vm --name repair-osdisk

# 6. swap it back as prob-vm's OS disk (prob-vm must be deallocated)
az vm deallocate -g rg-rescue-lab -n prob-vm
az vm update -g rg-rescue-lab -n prob-vm --os-disk repair-osdisk

# 7. start and verify boot
az vm start -g rg-rescue-lab -n prob-vm
az vm get-instance-view -g rg-rescue-lab -n prob-vm --query "instanceView.statuses[1].displayStatus" -o tsv  # expect: VM running
az vm run-command invoke -g rg-rescue-lab -n prob-vm --command-id RunShellScript --scripts "cat /etc/fstab; mount | grep data || echo 'bad mount gone'"
```

`fix.sh` (LF-normalized file, gotchas.md §2) — illustrative Linux repair:
```bash
#!/bin/bash
dev=$(lsblk -rno NAME,FSTYPE | awk '$2=="ext4"{print $1}' | tail -1)   # the attached data-disk partition
sudo fsck -y /dev/$dev || true
mp=$(mktemp -d); sudo mount /dev/$dev "$mp"
sudo sed -i '/\/dev\/sdz1/d' "$mp/etc/fstab"   # remove the bad mount line
sudo umount "$mp"
echo "REPAIRED $(date -u)"
```

## Gotchas specific to this flow
- **Same region** for snapshot / disk / rescue VM — a managed disk only attaches to a VM in its region.
- `az vm update --os-disk` requires the target VM **stopped/deallocated** — deallocate `prob-vm` first.
- **Windows**: offline registry/BCD work — mount the disk, then use a Hive Editor / `reg load` offline for hive edits;
  `bcdedit /store <X>:\boot\BCD ...` for boot config.
- Keep both the **snapshot** and the **original disk** until boot is confirmed — they're your rollback.

## Cleanup
One RG, kept by default. Teardown on confirmation: `az group delete -n rg-rescue-lab --yes --no-wait`.
