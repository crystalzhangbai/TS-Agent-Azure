---
name: vm-lab
description: >
  Validate action plans, commands, and troubleshooting steps by executing them in a real
  Azure lab environment (fixed Linux + Windows VMs across two subscriptions).
  This skill is EXPLICIT-TRIGGER ONLY — it does NOT auto-trigger from context.
  Only invoke when the user explicitly says: "vm-lab", "lab验证", "lab里试试",
  "lab里跑一下", "在lab环境验证", "validate in lab", "test in lab", "run in lab",
  "lab测试", "用lab试一下", "lab环境测试一下".
  Do NOT trigger this skill automatically when other skills produce action plans or commands.
  The user decides when to send steps to the lab — this skill waits to be called.
---

# VM Lab — Action Plan Validator

Validate commands and troubleshooting steps by executing them against real Azure lab VMs. This skill receives action plans (from other skills or the user), classifies each step, routes it to the appropriate execution target (local CLI, Linux VM, Windows VM, or Azure Portal), runs it, and produces a per-step verification report.

**This skill is explicit-trigger only.** Other skills produce action plans; this skill validates them — but only when the user explicitly asks.

---

## When This Lab Helps (and When It Doesn't)

**Use vm-lab for** anything you can *build and observe* from VMs / disks / networking:

- validating commands **and the multi-line scripts you'll hand a customer** (PowerShell / Bash, user-data, cloud-init, CSE)
- multi-resource lifecycle experiments (image → VM → restore point → disk → VM, etc.)
- config-change & mitigation **regression** — resize SKU, toggle accelerated networking, flip a setting → confirm it applies cleanly *before* recommending it
- repair / rescue procedures — offline-disk swap to a rescue VM, `fsck` / `chkdsk` / GRUB / BCD / registry fix
- pre-validating a **TSG / KB / doc procedure** on the current image before forwarding it
- producing a clean **reference output / screenshot** for a customer email or ICM

These are **patterns, not a fixed menu** — if you can reproduce it by *creating resources and running commands*, it belongs here. Don't expect this section to list your exact case.

**Do NOT use vm-lab for** platform / hardware-side problems — the lab cannot manufacture a platform event. Route these elsewhere:

| Not lab-reproducible | Where it goes |
|---|---|
| Unexpected reboot / service-healing / host-side downtime | `vm-kusto-query` (RCA) + dashboards |
| E17 / IaaSxStoreOutage / disk **hardware** failure | `vm-kusto-query`, ICM |
| Real allocation / capacity failure ("no zones available") | `vm-kusto-query` (allocation), CRP |
| MANA / specific-host-hardware-only behavior | `vm-knowledge-search` + PG; lab has no control over host hardware |

The lab proves **guest-side and resource-lifecycle** behavior — nothing host-side.

> **Worked recipes** (concrete, end-to-end — open these instead of asking the skill to invent a flow):
> - [references/recipe-userdata-script.md](references/recipe-userdata-script.md) — did the VM's user-data / init script actually run? (image vs. restore-point build paths)
> - [references/recipe-rescue-vm-repair.md](references/recipe-rescue-vm-repair.md) — offline OS-disk repair via a rescue VM.

---

## Workflow Overview

```
User provides commands/steps (or references prior skill output)
        ↓
Step 1: Parse input → extract individual commands/steps
        ↓
Step 2: Classify each step → determine execution target
        ↓
Step 3: Pre-flight checks (VM running? subscription set? safety review)
        ↓
Step 4: Execute each step on the appropriate target
        ↓
Step 5: Generate verification report (✅/❌ per step + output)
```

---

## Step 1: Parse Input

Accept input in any of these forms:

### A) Numbered action plan (from other skills or user)
```
1. Run `az vm show -g myRG -n myVM` to check VM status
2. SSH into the VM and check `systemctl status nginx`
3. Open Azure Portal → VM → Networking → verify port 443 is allowed
```

### B) Raw commands
```
az vm list --subscription <sub-id>
systemctl status sshd
Get-Service -Name WinRM
```

### C) Mixed instructions (commands + Portal steps)
```
1. az disk show -g rg1 -n disk1
2. On the VM, run: sudo fdisk -l
3. In Portal, go to VM > Disks > check if data disk LUN 0 is attached
```

**Parsing rules:**
- Lines starting with `az `, `Get-`, `Set-`, `New-`, `Remove-`, `$` → command
- Lines mentioning Portal, 门户, navigate, click, open, 打开 → Portal action
- Lines with Linux commands (`sudo`, `systemctl`, `cat`, `grep`, `df`, `mount`, etc.) → Linux SSH
- Lines with PowerShell cmdlets or Windows commands (`Get-Service`, `netsh`, `ipconfig`, `chkdsk`) → Windows
- Lines starting with `curl`, `wget` + ARM endpoint → ARM REST API
- If ambiguous, ask the user which target to use

---

## Step 2: Classify and Route

Each parsed step is classified into one of 5 execution modes:

| Mode | Target | How It Runs | When to Use |
|------|--------|-------------|-------------|
| **A: az CLI** | Local terminal | `run_in_terminal` directly | `az` commands, `az rest` calls |
| **B: Linux SSH** | Lab Linux VM | SSH via `ssh` CLI or `az vm run-command` | bash/Linux commands |
| **C: Windows** | Lab Windows VM | `az vm run-command invoke` or PowerShell remoting | PowerShell cmdlets, Windows commands |
| **D: Portal** | Azure Portal | `playwright-cli` browser automation (corp account) | GUI verification steps |
| **E: ARM REST** | Azure ARM API | `az rest --method GET/PUT --url ...` | API-level validation |

For detailed classification rules and edge cases, see [references/command-classification.md](references/command-classification.md).

---

## Step 3: Pre-flight Checks

Before executing, run these checks:

### 3.1 Lab VM Status
```powershell
# Check if lab VMs are running
az vm get-instance-view --ids <LINUX_VM_RESOURCE_ID> --query "instanceView.statuses[1].displayStatus" -o tsv
az vm get-instance-view --ids <WINDOWS_VM_RESOURCE_ID> --query "instanceView.statuses[1].displayStatus" -o tsv
```

If a VM is deallocated, ask the user:
> Lab VM `{vm_name}` is currently deallocated. Start it before running the validation? (Starting will incur compute costs)

Start it if confirmed:
```powershell
az vm start --ids <VM_RESOURCE_ID>
```

### 3.2 Subscription Context
```powershell
az account show --query "{name:name, id:id}" -o table
```
If not on the primary lab subscription, switch:
```powershell
az account set --subscription "<PRIMARY_SUB_ID>"
```

### 3.3 Safety Review

Before executing, scan all commands for destructive operations. **Always ask for confirmation** before running:

| Pattern | Risk Level | Action |
|---------|-----------|--------|
| `rm -rf`, `del /s`, `Remove-AzResource`, `az vm delete`, `az disk delete` | 🔴 Destructive | **Block** — ask user to confirm |
| `az vm restart`, `Stop-AzVM`, `az vm deallocate` | 🟡 Disruptive | **Warn** — explain impact, ask to confirm |
| `az resource create`, `New-AzVM`, `az vm create` | 🟡 Cost | **Warn** — show estimated cost if known |
| `az vm show`, `Get-AzVM`, `cat`, `systemctl status`, read-only commands | 🟢 Safe | Execute without confirmation |

If a command references the user's **production subscription** (not the lab subscription), **stop and alert**:
> ⚠️ Command targets subscription `{sub_id}` which is NOT your lab subscription. This could affect production resources. Are you sure?

---

## Step 4: Execute

### Mode A: az CLI (Local)

Run directly in the terminal:
```powershell
az vm show -g <rg> -n <vm> --subscription "<LAB_SUB_ID>" -o table
```

Capture: exit code, stdout, stderr.

### Mode B: Linux VM Commands

**Primary method — `az vm run-command` (preferred for freshly-built / scenario VMs):**
```powershell
az vm run-command invoke --resource-group <LAB_RG> --name <LAB_LINUX_VM> --command-id RunShellScript --scripts "@<path-to-script.sh>" --subscription "<LAB_SUB_ID>" --query "value[0].message" -o tsv
```
Runs via ARM as **root**, needs **no SSH key / NSG inbound / public IP** setup — so it Just Works on a VM you created seconds ago. This is what you almost always want in a scenario lab.

**Optimization — SSH direct (only for long-lived, pre-configured VMs):**
```powershell
ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 <LAB_LINUX_USER>@<LAB_LINUX_IP> "<command>"
```

> **When to use which:** Default to **run-command** for any VM you just built or any scenario lab — it sidesteps SSH key/NSG/IP plumbing entirely and runs as root. Use **SSH** only for a long-lived fixed VM that already has key + inbound-22 configured, when you want faster, streaming output. Caveats for run-command: ~**4 KB output limit** (tail/grep large logs before returning), ~15–30 s/call, and **pass scripts as a file with `--scripts "@file"`** — never inline (PowerShell mangles quotes/`=`). See [references/gotchas.md](references/gotchas.md).

### Mode C: Windows VM Commands

**Primary method — az vm run-command:**
```powershell
az vm run-command invoke --resource-group <LAB_RG> --name <LAB_WIN_VM> --command-id RunPowerShellScript --scripts "<powershell_command>" --subscription "<LAB_SUB_ID>"
```

**Fallback — PowerShell remoting** (if configured):
```powershell
Invoke-Command -ComputerName <LAB_WIN_IP> -Credential $cred -ScriptBlock { <command> }
```

### Mode D: Portal (playwright-cli)

Portal automation uses the **corp account** (`@microsoft.com`). URLs under
`portal.azure.com` are automatically routed to `state-corp.json` by the
helper script.

> **First-time setup (run once):** If `.playwright-cli\state-corp.json` is missing or expired:
> ```powershell
> . <repo-root>\.github\skills\vm-lab\scripts\load-helpers.ps1
> Update-PwState corp   # sign in with your corp account (@microsoft.com)
> ```

Then automate Portal verification:

```powershell
. <repo-root>\.github\skills\vm-lab\scripts\load-helpers.ps1
$sid = New-PwSessionId 'portal'
Start-PwSession -SessionId $sid -Url "https://portal.azure.com/#@<tenant>/resource/<resource_id>/overview"
Start-Sleep -Seconds 8                # Portal SPA load
Invoke-Pw $sid snapshot                # locate element to verify
# Extract the value via snapshot or DOM, compare against expected
Stop-PwSession -SessionId $sid
```

**When playwright-cli cannot perform the action** (complex multi-step Portal workflows, unsupported controls):
1. Try generating an equivalent `az CLI` command instead
2. If no CLI equivalent exists, generate a Portal deep link and ask the user to verify manually:
   > I couldn't automate this Portal step. Please open this link and verify: `https://portal.azure.com/#@.../resource/.../networking`

### Mode E: ARM REST API

```powershell
az rest --method GET --url "https://management.azure.com/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Compute/virtualMachines/<vm>?api-version=2024-07-01"
```

---

## Step 5: Subscription Management

The lab uses two Azure subscriptions. See [references/lab-environment.md](references/lab-environment.md) for details.

### Switching Logic

1. **Default**: Always start with the primary ($400) subscription
2. **On error**: If a command fails due to subscription-level restrictions (e.g., storage account access key disabled, features not enabled), automatically try the secondary ($150) subscription:
   ```powershell
   az account set --subscription "<SECONDARY_SUB_ID>"
   # Re-run the failed command
   ```
3. **Report the switch**: Note in the verification report which subscription was used

### Known Limitation Triggers (auto-switch to secondary)

| Error Pattern | Cause | Action |
|---------------|-------|--------|
| `StorageAccountAccessKeyDisabled` | Primary sub policy blocks storage access keys | Switch to secondary |
| `AuthorizationFailed` on specific resource types | RBAC restriction on primary | Switch to secondary |
| `QuotaExceeded` | Primary sub quota exhausted | Switch to secondary |

---

## Step 6: Generate Verification Report

After all steps complete, produce this report:

```
## Lab Verification Report

**Source**: [what was being validated — e.g., "vm-knowledge-search TSG steps for ADE troubleshooting"]
**Lab Environment**: Primary subscription ($400) / Linux VM: running / Windows VM: deallocated
**Timestamp**: 2026-03-22 14:30 UTC

### Results

| # | Command / Action | Target | Status | Output / Evidence |
|---|-----------------|--------|--------|-------------------|
| 1 | `az vm show -g lab-rg -n lab-linux` | az CLI | ✅ | VM running, size=Standard_B2s |
| 2 | `systemctl status nginx` | Linux VM | ❌ | Unit nginx.service not found |
| 3 | Portal: VM > Networking > check port 443 | Portal | ✅ | NSG rule "AllowHTTPS" found, priority 100 |

### Summary
- **Passed**: 2/3 steps
- **Failed**: 1 step

### Failed Step Details
**Step 2**: `systemctl status nginx`
- **Error**: `Unit nginx.service could not be found.`
- **Likely cause**: nginx is not installed on this VM
- **Suggested fix**: `sudo apt-get install -y nginx` (Ubuntu) or `sudo yum install -y nginx` (RHEL)

### Subscription Used
- Steps 1–3: Primary subscription ($400)
```

---

## Scenario Lab — Build Hands-on Experiments

The Mode A–E flow above assumes you're validating a list of commands against **pre-existing fixed VMs**. But a large class of real validation work is different: you need to **build a controlled multi-resource scenario from scratch** to prove a mechanism — e.g. *image → VM → restore point → new disk → new VM*, comparing behaviour across variants. This section is the workflow for that.

> **Trigger**: user asks to "build a lab", "reproduce", "create a source VM and …", "spin up a VM to test X", or any multi-resource experiment that the fixed lab VMs can't represent. Still explicit-trigger only.

> **Retention & teardown** (canonical rule in [Safety Rules](#safety-rules) §6): keep everything by default — don't auto-delete or auto-deallocate, because the user usually wants to open the lab and re-run the commands by hand (*眼见为实*). Put everything in one RG `rg-<slug>-lab` so a single `az group delete` cleans up, and delete only on explicit confirmation.

### Rules for scenario labs

1. **One dedicated resource group per scenario**, named `rg-<slug>-lab` (e.g. `rg-userdata-lab`). Everything you create goes inside it — never scatter resources into shared RGs. This makes teardown a single `az group delete`.
2. **Cheapest viable SKU.** Default `Standard_B1s` / `Standard_B2s`, smallest OS disk, no accelerated networking unless the test needs it. Warn the user of the rough hourly cost before the first `az vm create`.
3. **Verify with `az vm run-command` (Mode B primary)** — no SSH plumbing on fresh VMs.
4. **Write a teardown manifest as you go** (format below) — the record the user uses to delete the lab later, on their confirmation.
5. **Use a marker convention** so each variant is self-identifying, e.g. write `/var/lab/which-ran.txt` + append to `/var/lab/history.log` from each init script, then read them back to prove which path executed.

### Teardown manifest (scenario labs)

The single biggest record-keeping need is knowing **what got created** so the user can clean it up on demand. From the first `create`, maintain a manifest at `_work/<case-or-slug>/lab-teardown.md` listing the RG and every resource:

```markdown
# Teardown — rg-userdata-lab  (sub 313df58c-…, East Asia)
RG: rg-userdata-lab          # deleting the RG removes everything below
- VM      src-vm, new-vm, src2-vm, new2-vm, new3-vm
- Disk    new-osdisk, new-osdisk2, new-osdisk3
- RestorePointCollection  rpc-src (rp1), rpc-src2 (rp2)
- Extension  CSE on new2-vm
- RunCommand addlines on new3-vm
TEARDOWN: az group delete -n rg-userdata-lab --yes --no-wait
```

Because every resource lives in the one RG, the catch-all teardown is just:
```powershell
az group delete --name rg-<slug>-lab --yes --no-wait --subscription "<LAB_SUB_ID>"
```

### Closing a scenario session

Keep the lab alive by default — report the manifest path + the single RG name, and stop. Delete only when the user explicitly asks (then surface the manifest and run `az group delete -n rg-<slug>-lab --yes --no-wait`). You may *offer* `deallocate` to save cost, but act only on their choice. See [Safety Rules](#safety-rules) §6.

### Common scenario building blocks

| Goal | Command sketch |
|------|----------------|
| Source VM (provisioned) | `az vm create -g <rg> -n src-vm --image Ubuntu2404 --size Standard_B1s --user-data <file>` (or `--custom-data`) |
| Restore point | `az restore-point collection create --source-id <vmId>` → `az restore-point create -n rp1 --collection-name rpc-src -g <rg>` |
| New disk from RP | get `sourceMetadata.storageProfile.osDisk.diskRestorePoint.id` → `az disk create -n new-osdisk --source <drp-id> --os-type Linux` |
| New VM from that disk | `az vm create -g <rg> -n new-vm --attach-os-disk new-osdisk --os-type Linux --user-data <file>` |
| Inspect any VM (root) | `az vm run-command invoke -g <rg> -n <vm> --command-id RunShellScript --scripts "@verify.sh" --query "value[0].message" -o tsv` |

> All scripts passed to run-command must be **LF-normalized files**, never inline. `az vm create` may return `null` provisioningState in the create response yet still succeed — re-check with `az vm get-instance-view`. Full list: [references/gotchas.md](references/gotchas.md).

---

## Lab VM Lifecycle Management

To save cost, lab VMs can be started and stopped around validation sessions.

### Start Lab VMs
```powershell
# Start Linux VM
az vm start --ids <LINUX_VM_RESOURCE_ID> --no-wait
# Start Windows VM
az vm start --ids <WINDOWS_VM_RESOURCE_ID> --no-wait
# Wait for both
az vm wait --ids <LINUX_VM_RESOURCE_ID> --created
az vm wait --ids <WINDOWS_VM_RESOURCE_ID> --created
```

### Stop Lab VMs (only when the user asks)
Leave lab VMs running by default so the user can log in and re-run commands themselves ([Safety Rules](#safety-rules) §6); offer deallocate as a cost-saving option but wait for their request:
> The lab VMs are still running (and billing). Want me to deallocate them to save cost, or keep them up so you can run the commands yourself?

```powershell
az vm deallocate --ids <LINUX_VM_RESOURCE_ID> --no-wait
az vm deallocate --ids <WINDOWS_VM_RESOURCE_ID> --no-wait
```

Only start the VMs that are actually needed. If all steps are az CLI or Portal-only, no need to start any VM.

---

## Safety Rules

1. **Never execute destructive commands without explicit user confirmation** — this includes `rm -rf`, `del`, resource deletions, VM restarts, disk detach/delete
2. **Never run commands against production subscriptions** — all commands must target the lab subscription. If a command contains a subscription ID that is not one of the two lab subscriptions, stop and alert
3. **Timeout**: Each command has a 60-second timeout by default. Long-running operations (VM create, disk resize) get 300 seconds
4. **No credential storage**: Never hardcode passwords, keys, or tokens in commands or output. Reference environment variables (`$env:LAB_LINUX_PASSWORD`) or the `references/lab-environment.md` file
5. **Cost awareness**: Before creating resources (VMs, disks, storage accounts), estimate the hourly cost and warn the user. For scenario labs, keep a running tally of what's been created.
6. **Retention / teardown**: **Keep lab resources by default** — never auto-delete and never auto-deallocate. Put **everything you create in one RG** (`rg-<slug>-lab`) and maintain a **teardown manifest** (`_work/<slug>/lab-teardown.md`) listing the RG + every resource from the first `create`. Delete **only after explicit user confirmation** — the user often wants to inspect the VMs hands-on first (*眼见为实*). When you believe the work is done, surface the manifest and *ask*; do not act until the user says yes.

---

## Common Workflows

Every request reduces to the same loop — *parse → classify → pre-flight → execute → report* (Steps 1–6), or the build-from-scratch flow for experiments. Pick the entry by what the user asks:

| User says (example) | What to do |
|---|---|
| "验证一下上面给的排查步骤" | Parse the prior skill's numbered steps → classify each → run Steps 3–6 → verification report |
| "在 linux 上跑一下 `df -h`" | Single command → classify (Mode B) → execute via run-command → return output directly (no full report) |
| "在 Portal 里验证 NSG 有没有 443" | Mode D: build the VM's networking-blade URL → `playwright-cli` snapshot → report the finding |
| "试试这几个 storage 命令" | Mode A on primary sub; on access-key/RBAC/quota error auto-switch to secondary (Step 5) and re-run |
| "建源 VM→restore point→新 VM,看哪个脚本生效" | [Scenario Lab](#scenario-lab--build-hands-on-experiments): slug → `rg-<slug>-lab` → teardown manifest → cheapest SKU → verify via run-command + marker file → ask before teardown. Recipe: [recipe-userdata-script.md](references/recipe-userdata-script.md) |
| "演练救援 VM 修坏盘" | [recipe-rescue-vm-repair.md](references/recipe-rescue-vm-repair.md) |

Read [references/gotchas.md](references/gotchas.md) before any scenario lab.

---

## Static Verification Pack (manual self-check for commands/steps before send)

This skill's **command-classification** (Step 2) and **Safety Review** (Step 3.3) double as a
**manual self-check checklist** — the *static, paper-only* check that commands/steps about to be
sent to a customer are valid, correctly targeted, applicable, and that destructive ops are flagged.
Run this checklist yourself **without executing anything** before any commands reach a customer
(e.g. when a customer reply contains commands).

- **Checklist:** [`references/verification-pack.md`](references/verification-pack.md) — syntax / target
  mode (`command-classification.md`) / applicability / doc-match / destructive-flag (Step 3.3)
  checklist, mapped to verdict classes.
- **STATIC BY DEFAULT.** This is a paper check. It does **not** run anything in the lab, so it never
  breaks this skill's explicit-trigger iron rule. An **actual lab run** still happens **only** when
  the user explicitly says "validate in lab / 在 lab 验证" — at which point the normal Step 1→6
  workflow takes over against the fixed lab VMs (never a customer subscription).
- **Run it as a manual self-check** when an artifact about to reach a customer contains
  commands/steps. An unflagged destructive op ⇒ critical ⇒ FAIL; a Linux command sent to a Windows
  VM ⇒ `CONTRADICTED`.

---

## Cross-References

| Need | Use This Skill |
|------|----------------|
| Generate action plans to validate | `vm-knowledge-search`, `vm-kusto-query`, `vm-case-triage` |
| Analyze logs collected from lab VM | `vm-log-analyzer` |
| Read lab VM performance graphs | open vmdash/EEE manually |
| Write customer email with validated steps | manual (draft customer FQR/LQR/RCA yourself) |

## References

- [references/lab-environment.md](references/lab-environment.md) — subscriptions, optional fixed VMs, network, auth.
- [references/command-classification.md](references/command-classification.md) — Mode A–E classification rules + edge cases.
- [references/gotchas.md](references/gotchas.md) — hard-won execution gotchas (az quoting, CRLF, run-command limits, create-returns-null, restore-point flow). **Read before running scenario labs.**
- [references/recipe-userdata-script.md](references/recipe-userdata-script.md) — worked recipe: did the user-data / init script actually run? (real case `60e4550a`).
- [references/recipe-rescue-vm-repair.md](references/recipe-rescue-vm-repair.md) — worked recipe: offline OS-disk repair via a rescue VM.
