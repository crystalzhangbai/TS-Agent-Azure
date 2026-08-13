# Command Classification Rules

How to classify user-provided commands and steps into the correct execution mode.

---

## Classification Decision Tree

```
Input line
  ├── Starts with `az ` or `az.cmd `?
  │     ├── Contains `vm run-command` → Mode A (local CLI, it runs on the VM via ARM)
  │     ├── Contains `rest --method` → Mode E (ARM REST, but still runs locally)
  │     └── Other `az` commands → Mode A (local CLI)
  │
  ├── PowerShell cmdlet (Get-*, Set-*, New-*, Remove-*, Invoke-*, Test-*, Start-*, Stop-*)?
  │     ├── Azure cmdlet (Get-AzVM, New-AzDisk, etc.) → Mode A (local CLI — runs locally with Az module)
  │     └── Windows cmdlet (Get-Service, Get-EventLog, netsh, ipconfig, etc.) → Mode C (Windows VM)
  │
  ├── Linux command (sudo, systemctl, cat, grep, df, mount, fdisk, lsblk, journalctl, etc.)?
  │     └── Mode B (Linux VM via SSH)
  │
  ├── Portal / GUI instruction (contains "Portal", "门户", "navigate", "click", "打开", "open blade")?
  │     └── Mode D (Playwright Portal automation)
  │
  ├── ARM REST API URL (contains `management.azure.com`)?
  │     └── Mode E (via `az rest`)
  │
  └── Ambiguous?
        └── Ask the user: "Should I run this on the Linux VM, Windows VM, or locally?"
```

---

## Mode A: az CLI (Local)

### Identification Patterns
- Line starts with `az `
- Azure PowerShell cmdlets (`Get-AzVM`, `New-AzDisk`, `Set-AzVMExtension`, etc.)

### Examples
```
az vm show -g myRG -n myVM -o table
az disk list --subscription <sub> -o table
az network nsg rule list -g myRG --nsg-name myNSG -o table
az storage account show -g myRG -n mystorageaccount
Get-AzVM -ResourceGroupName myRG -Name myVM
```

### Execution
```powershell
# Run directly in terminal
az vm show -g myRG -n myVM -o table
```

### Subscription Awareness
- If the command includes `--subscription`, use it as-is
- If no `--subscription`, the currently set subscription is used
- Always verify the target subscription matches a lab subscription before executing

---

## Mode B: Linux VM (SSH)

### Identification Patterns
- Starts with `sudo`, `systemctl`, `journalctl`, `cat`, `grep`, `awk`, `sed`, `tail`, `head`
- Starts with `ls`, `df`, `du`, `mount`, `umount`, `fdisk`, `lsblk`, `blkid`, `pvs`, `lvs`, `vgs`
- Starts with `yum`, `apt`, `apt-get`, `dnf`, `zypper`, `pip`, `npm`
- Starts with `service`, `chkconfig`, `timedatectl`, `hostnamectl`
- Starts with `ifconfig`, `ip `, `ss `, `netstat`, `iptables`, `firewall-cmd`, `nslookup`, `dig`, `ping`, `traceroute`, `tcpdump`
- Starts with `waagent`, `cloud-init`, `hv_kvp_daemon`
- Contains `/etc/`, `/var/log/`, `/home/`, `/opt/`, `/usr/`
- Starts with `chmod`, `chown`, `mkdir`, `cp`, `mv`, `rm ` (note: `rm` needs safety check)
- Bash-specific: starts with `#!/bin/bash`, `export`, `source`, `echo`, `printf`, pipes (`|`)

### Examples
```
systemctl status waagent
sudo cat /var/log/waagent.log | tail -50
df -h
sudo fdisk -l
journalctl -u cloud-init --since "1 hour ago"
ip addr show
```

### Execution
```powershell
ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 <user>@<ip> "systemctl status waagent"
```

---

## Mode C: Windows VM (PowerShell / run-command)

### Identification Patterns
- Windows-specific cmdlets: `Get-Service`, `Get-EventLog`, `Get-WmiObject`, `Get-CimInstance`, `Get-WindowsFeature`
- Windows commands: `netsh`, `ipconfig`, `nslookup`, `tracert`, `chkdsk`, `sfc`, `dism`, `bcdedit`, `diskpart`
- Windows paths: `C:\`, `D:\`, `%TEMP%`, `$env:SystemRoot`
- Registry operations: `Get-ItemProperty HKLM:\...`, `reg query`
- Windows services: `sc query`, `net start`, `net stop`
- Event log: `wevtutil`, `Get-WinEvent`

### Examples
```powershell
Get-Service -Name WinRM
Get-EventLog -LogName System -Newest 20
ipconfig /all
netsh advfirewall firewall show rule name=all
Get-WinEvent -LogName System -MaxEvents 10
```

### Execution
```powershell
az vm run-command invoke --resource-group <rg> --name <vm> --command-id RunPowerShellScript --scripts "Get-Service -Name WinRM" --subscription "<sub>"
```

---

## Mode D: Portal (Playwright)

### Identification Patterns
- Contains: "Portal", "Azure Portal", "门户", "Azure 门户"
- Contains: "navigate to", "go to", "open", "click", "打开", "进入", "查看"
- Contains: "blade", "tab", "menu", "page", "section"
- Describes UI verification: "check if", "verify that", "confirm", "look at"

### Examples
```
Open Azure Portal → VM → Networking → verify inbound rule for port 22 exists
在Portal中查看VM的磁盘配置
Navigate to Storage Account > Access Keys and check if keys are accessible
Go to VM > Boot diagnostics > Screenshot tab
```

### Translation to Playwright
1. Construct the Portal deep link URL:
   - VM overview: `https://portal.azure.com/#@<tenant>/resource/<resource_id>/overview`
   - VM networking: `https://portal.azure.com/#@<tenant>/resource/<resource_id>/networking`
   - VM disks: `https://portal.azure.com/#@<tenant>/resource/<resource_id>/disks`
   - Storage account: `https://portal.azure.com/#@<tenant>/resource/<storage_resource_id>/keys`
2. Use `mcp_playwright_browser_navigate` → `wait_for` → `snapshot`
3. Search the snapshot for the element to verify
4. Report the finding

### Fallback
If Playwright cannot automate the step, try:
1. **az CLI equivalent**: Many Portal views have CLI counterparts (e.g., `az vm show`, `az network nsg rule list`)
2. **Portal deep link**: Generate the URL and ask the user to manually verify

---

## Mode E: ARM REST API

### Identification Patterns
- URL contains `management.azure.com`
- Starts with `curl` or `wget` and targets ARM endpoint
- Mentions specific API version (`api-version=2024-07-01`)

### Examples
```
GET https://management.azure.com/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Compute/virtualMachines/{vm}?api-version=2024-07-01
```

### Execution
```powershell
az rest --method GET --url "https://management.azure.com/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Compute/virtualMachines/<vm>?api-version=2024-07-01"
```

---

## Edge Cases

| Scenario | Resolution |
|----------|-----------|
| `ssh <user>@<ip> "<command>"` | Mode B — the ssh wrapper is just the transport, the command runs on Linux |
| `Invoke-Command -ComputerName ... -ScriptBlock { ... }` | Mode C — PowerShell remoting to Windows target |
| `az vm run-command invoke ... --scripts "bash_command"` | Mode A — it's an az CLI command that executes on the VM through ARM |
| `python script.py` provided as a step | Ask: "Should I run this on the Linux VM, Windows VM, or locally?" |
| `docker run ...` | Typically Mode B (Linux VM), unless explicitly targeting Windows containers |
| Steps that say "restart the VM" without a specific command | Translate to `az vm restart -g <rg> -n <vm>` → Mode A + safety check |
| `kubectl ...` commands | Typically Mode B (from Linux VM if kubectl is configured there), or local if kubeconfig is local |
