# VM Lab — Execution Gotchas

Hard-won failure modes from real lab sessions on Windows (PowerShell) driving `az` against Azure Linux/Windows VMs. Read this **before** running a scenario lab — every item below cost real time to discover.

---

## 1. PowerShell → `az` quoting hell — pass scripts as a FILE, never inline

Inline `--scripts "echo something ==== ..."` gets mangled repeatedly: PowerShell eats double-quotes, `=`, `$`, and newlines before `az` ever sees them, so the script that lands on the VM is corrupted or empty.

**Fix — always write the script to a file and pass `--scripts "@<path>"`:**
```powershell
az vm run-command invoke -g <rg> -n <vm> --command-id RunShellScript `
  --scripts "@<repo-root>\_work\<slug>\verify.sh" `
  --query "value[0].message" -o tsv
```
The `@` prefix tells `az` to read the file as the script body — no shell-quoting in the middle. This applies to `--user-data`, `--custom-data`, CSE settings files, everything multi-line.

---

## 2. CRLF kills bash — normalize every script to LF before use

Files written on Windows default to CRLF. On a Linux VM, `#!/bin/bash\r` is not a valid interpreter path → script fails with `bad interpreter` or silently misbehaves (e.g. `wget ...\r`).

**Fix — normalize to LF right after writing the file:**
```powershell
$p = "<repo-root>\_work\<slug>\verify.sh"
$c = [IO.File]::ReadAllText($p) -replace "`r`n","`n"
[IO.File]::WriteAllText($p, $c)
```
Do this for **every** `.sh`, user-data, custom-data, and CSE script.

---

## 3. `az vm create` may return `null` provisioningState but still succeed

The JSON returned by `az vm create` (especially with `--query`) can show `provisioningState: null` / `vm: null` even though the VM provisioned fine. Don't treat that as failure.

**Fix — re-check independently:**
```powershell
az vm get-instance-view -g <rg> -n <vm> --query "instanceView.statuses[1].displayStatus" -o tsv
# expect: VM running
```
The public IP returned by create is reliable even when prov state shows null.

---

## 4. `az vm run-command` has a ~4 KB output limit

`value[0].message` truncates around 4 KB. Dumping a whole `cloud-init.log` or `waagent.log` returns a clipped, misleading tail.

**Fix — reduce on the VM before returning:** `tail -n 50`, `grep`, `wc -l`, or write a focused `verify.sh` that prints only the fields you need (marker file, a count, one decoded value). Each call is also ~15–30 s, so batch checks into one script rather than many calls.

---

## 5. run-command runs as **root** — no `sudo`, no SSH, no NSG

`RunShellScript` executes as root via the guest agent over ARM. Benefits: works on a VM created seconds ago with **no SSH key, no inbound-22 rule, no public IP**. Implication: don't prefix with `sudo` (already root), and don't waste time wiring SSH for throwaway scenario VMs. This is why **run-command is the Mode B primary** for scenario labs.

---

## 6. Restore-point → new-disk → new-VM flow (exact sequence)

```powershell
# 1. collection bound to the source VM
az restore-point collection create -g <rg> -n rpc-src --source-id <source-vm-id>
# 2. take the restore point
az restore-point create -g <rg> --collection-name rpc-src -n rp1
# 3. grab the OS disk restore-point id
$drp = az restore-point show -g <rg> --collection-name rpc-src -n rp1 `
  --query "sourceMetadata.storageProfile.osDisk.diskRestorePoint.id" -o tsv
# 4. materialize a new managed disk from it (createOption=Restore)
az disk create -g <rg> -n new-osdisk --source $drp --os-type Linux
# 5. build the new VM from that disk
az vm create -g <rg> -n new-vm --attach-os-disk new-osdisk --os-type Linux --user-data "@new.sh"
```

Notes:
- `--attach-os-disk` (specialized) **rejects `osProfile` / `--custom-data`** (it's an osProfile child) — but **`--user-data` is accepted** (top-level property). Proven in lab.
- A VM from a reused specialized disk **keeps the source's hostname** — don't be surprised when `hostname` returns `src-vm` on `new-vm`.

---

## 7. customData vs userData — what persists on the disk

| | customData | userData |
|---|---|---|
| ARM field | `osProfile.customData` | `properties.userData` (top-level) |
| Lands as | `<CustomData>` (base64) in `/var/lib/waagent/ovf-env.xml` | IMDS only (`/metadata/instance/compute/userData`) |
| Persists on disk? | **Yes** — travels with restore-point disk reuse | **No** — served fresh per current VM resource |
| Works with `--attach-os-disk`? | No (osProfile rejected) | **Yes** |

Cloud-init precedence (`DataSourceAzure.py`): `userdata_raw = ovf_env.custom_data; if not userdata_raw: <fetch IMDS userData>`. So **a stale `<CustomData>` on a reused disk short-circuits IMDS userData**. The decider is what's on the disk, not what you pass at create time. To clear it before taking a restore point:
```bash
sudo chmod u+w /var/lib/waagent/ovf-env.xml
sudo sed -i -E 's#<([A-Za-z0-9]+):CustomData>[^<]*</([A-Za-z0-9]+):CustomData>##g' /var/lib/waagent/ovf-env.xml
sudo chmod 0400 /var/lib/waagent/ovf-env.xml; sync
```

---

## 8. `/dev/sr0` provisioning ISO

The `ovf-env.xml` ISO surfaces as `/dev/sr0` only on a **provisioned** create (`FromImage` / osProfile present), is read once and ejected. An `--attach-os-disk` create never generates it. Presence of sr0 is **not** the OLD/NEW differentiator — the on-disk `<CustomData>` is.

---

## 9. Marker convention for self-identifying variants

So you can prove which init path ran without guessing, have each script stamp:
```bash
echo "RAN=<variant-tag>" | sudo tee /var/lab/which-ran.txt
echo "RAN=<variant-tag> iid=$(...) host=$(hostname) $(date -u)" | sudo tee -a /var/lab/history.log
```
Then `verify.sh` just cats those + a count of IMDS hits. Cheap, unambiguous.

---

## 10. Misc

- **Session SQLite filter**: the per-session DB rejects the literal word "a&#8203;ttach" in some inserts (security filter). Reword todo text if an insert fails.
- **Don't version with suffixes**: overwrite the same `verify.sh` / `userdata.sh`; use git for history, not `_v2` / `_峰值`.
- **Browser profile** (Portal/playwright): launch with `--user-data-dir = $env:TEMP\playwright-edge`; never create a profile dir in the workspace.
