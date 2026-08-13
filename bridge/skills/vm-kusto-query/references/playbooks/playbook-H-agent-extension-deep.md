# Playbook H — Agent + Extension (AGEX + ADE) — Deep

> **Companion to** [`playbook-H-agent-extension-core.md`](./playbook-H-agent-extension-core.md). Core file is the routing entry point; this file holds full KQL bodies, customer-facing wording, and per-error workarounds. **All anchors are `AGEX-*` (Agent + Extension) or `ADE-*` (Azure Disk Encryption) or `SSE-*` (Server-Side Encryption with CMK)**.

> **Scope boundary**:
> - **Agent / Extension runtime issues** (GA not reporting, extension fails, wireserver blocked, certificate errors, auto-upgrade not happening) → **Playbook H**
> - **Extension fails at VM CREATE time, before VM exists** → Playbook G § DEPLOY-* (use H first; H cross-links to H)
> - **ADE encryption setting parameter conflict at attach** (`Parameter 'encryptionSettings' is not allowed`) → Playbook F § MD-Encryption-1 (already covered)
> - **CMK disk recovery (find DES for deleted CMK disks)** → Playbook F § MD-Encryption-2
> - **SSE+CMK with PV2/Ultra User MI issue** → § [SSE-PV2-Ultra-UserMI](#sse-pv2-ultra-usermi--ssecmk-fails-to-encrypt-premiumssdv2--ultra-with-user-assigned-mi) (this playbook)

## Cluster shortcuts

```kusto
let crp         = cluster('azcrp.kusto.windows.net').database('crp_allprod');
let crp_follow  = cluster('Azcsupfollower2.centralus.kusto.windows.net').database('crp_allprod');
let armprodgbl  = cluster('armprodgbl.eastus.kusto.windows.net').database('ARMProd');
let azcore      = cluster('azcore.centralus.kusto.windows.net').database('Fa');
let rsm         = cluster('azmc2.centralus.kusto.windows.net').database('rsm_Prod');
```

> **Foundation reference**: `references/azcore-queries.md` § Guest Agent & Extensions documents `GuestAgentExtensionEvents` (Operation = HeartBeat / ReportStatus / VmSettingsSummary; OperationSuccess; GAVersion; extension Name/Version). Most J anchors delegate to that table.

---

## Anchor Index

### Guest Agent (GA) — Windows
- [`AGEX-GA-StatusNotReported-Win`](#agex-ga-statusnotreported-win--windows-ga-not-reporting-status-3rd-party-av) — Windows GA Not Reporting (3rd-party AV / Blue Coat)
- [`AGEX-GA-Crash-Win`](#agex-ga-crash-win--windows-ga--extension-crash-dump-procedure-procdump--windbg) — Windows GA / Extension Crash (Procdump + Windbg procedure)
- [`AGEX-GA-FirewallWireServer-Win`](#agex-ga-firewallwireserver-win--windows-firewall-blocking-168631291680--32526) — Windows Firewall blocking 168.63.129.16 (ports 80 / 32526) + Multi-IP SkipAsSource
- [`AGEX-GA-CryptoCert-Win`](#agex-ga-cryptocert-win--keyset-does-not-exist--machinekeys-acl-fix) — Crypto/Cert errors (Keyset does not exist) + MachineKeys ACL fix
- [`AGEX-GA-NotAutoUpgrading-Win`](#agex-ga-notautoupgrading-win--windows-ga-not-auto-upgrading-manifest-timestamp-bug) — Windows GA not auto-upgrading (manifest timestamp registry bug)

### Guest Agent (GA) — Linux
- [`AGEX-GA-WireServerIOError-Linux`](#agex-ga-wireserveriomerror-linux--linux-wireserver-not-responding--ioerror-timed-out) — WireServer not responding / IOError timed out (SUSE wicked NIC reset)
- [`AGEX-GA-ConnectivityBlocked-Linux`](#agex-ga-connectivityblocked-linux--linux-iptablesnftables-blocking-wireserver) — Linux iptables / nftables blocking WireServer
- [`AGEX-GA-OldGoalState-Blacklist`](#agex-ga-oldgoalstate-blacklist--linux-walinuxagent-permanently-blacklisted-after-bad-upgrade) — Linux WALinuxAgent permanently blacklisted (error.json `was_fatal:true`)

### Extension — generic
- [`AGEX-Ext-90minTimeout`](#agex-ext-90mintimeout--90-minute-extension-timeout-blocks-vm-ops) — 90-min Extension Timeout (also blocks VM ops)
- [`AGEX-Ext-TimedOutWaiting`](#agex-ext-timedoutwaiting--timed-out-waiting-for-extension-handler-vs-extension) — Timed Out Waiting for Extension (handler vs extension distinction)
- [`AGEX-Ext-AzurePolicy`](#agex-ext-azurepolicy--extension-deploymentfailed-duetoazurepolicy-only-approved-extensions) — Extension DeploymentFailed DueToAzurePolicy ("Only approved VM extensions")
- [`AGEX-Ext-AutoUpgrade`](#agex-ext-autoupgrade--automatic-extension-upgrade-not-happening-rsm_prod-rollout--maintenance-policy-block) — Automatic Extension Upgrade not happening (rsm_Prod rollout + maintenance policy block)

### Extension — CustomScript (CSE)
- [`AGEX-Ext-CSE-DownloadTimeout`](#agex-ext-cse-downloadtimeout--cse-30-min-file-download-cap) — CSE 30-min file download cap
- [`AGEX-Ext-CSE-ExitCode50-124`](#agex-ext-cse-exitcode50-124--cse-aks-vmss-exit-code-50--124-network-block) — CSE ExitCode 50 / 124 (AKS VMSS network block)
- [`AGEX-Ext-CSE-Lock`](#agex-ext-cse-lock--cse-timed-out-waiting-for-lock-customer-script-too-long) — CSE Timed Out Waiting for Lock (script too long / AV holding lock)
- [`AGEX-Ext-CSE-Storage`](#agex-ext-cse-storage--cse-storage-account-failures-sa-firewall--pe--mi--sas) — CSE Storage Account failures (SA firewall / PE / MI / SAS)

### Extension — RunCommand
- [`AGEX-Ext-RunCommand-Conflict`](#agex-ext-runcommand-conflict--runcommandconflict-existing-rc-still-running) — RunCommandConflict (existing RC still running)
- [`AGEX-Ext-RunCommand-FabricOpFailed`](#agex-ext-runcommand-fabricopfailed--rc-v2-upgrade-extensionversion-conflict-mitigation) — RC v2 upgrade extensionVersions conflict mitigation

### Extension — VMAccess + Domain Join
- [`AGEX-Ext-VMAccess-Umbrella`](#agex-ext-vmaccess-umbrella--vmaccess-errors-9-error-routing-table) — VMAccess Errors (9-error routing table)
- [`AGEX-Ext-DomainJoin-Shutdown`](#agex-ext-domainjoin-shutdown--domain-join-failed-to-initiate-system-shutdown) — Domain Join "Failed to initiate system shutdown"
- [`AGEX-Ext-PerfDiagnostics-FIPS`](#agex-ext-perfdiagnostics-fips--azure-performance-diagnostics-fails-with-vmextensionprovisioningerror-fips-mode) — Azure Performance Diagnostics fails with VMExtensionProvisioningError (FIPS mode)

### GA Operations
- [`AGEX-GA-Logs-ETLDiskFillup`](#agex-ga-logs-etldiskfillup--c-windowsazure-logs-filling-with-runtimeevents--waappagent-etlold) — `C:\WindowsAzure\Logs` filling with `RuntimeEvents_*.etl.old` + `WaAppAgent_*.etl.old` (VMAgent upgrade)

### Azure Disk Encryption (ADE)
- [`ADE-AccessDenied`](#ade-accessdenied--access-denied--failed-to-configure-bitlocker-as-expected-aad-app--kv-access-policy) — Access Denied / Failed to configure bitlocker (AAD app → KV access policy)
- [`ADE-KVTenantID-Wrong`](#ade-kvtenantid-wrong--key-vault-associated-to-wrong-tenantid-kv-moved-tenants) — Key Vault Associated to Wrong TenantID (KV moved tenants)
- [`ADE-KVNotFoundDirectory`](#ade-kvnotfounddirectory--keyvault-not-found-in-the-directory-aad-tenant-mismatch) — Keyvault not found in the Directory (AAD tenant mismatch)
- [`ADE-NetworkAclsBypass`](#ade-networkaclsbypass--networkacls-bypass-must-include-azureservices) — networkAcls.bypass must include "AzureServices"
- [`ADE-VMStartup-SecretRetrievalFailed`](#ade-vmstartup-secretretrievalfailed--diskencryptionkeysecretretrievalfailed-vm-cant-boot-after-encryption) — DiskEncryptionKeySecretRetrievalFailed (VM can't boot)
- [`ADE-DataDisksSkipped`](#ade-datadisksskipped--data-disks-silently-skipped-extension-v2203736-regression) — Data Disks silently skipped (extension v2.2.0.37 regression → downgrade to 2.1)
- [`ADE-DataDiskSecretsMissing`](#ade-datadisksecretsmissing--data-disk-secrets-missing-on-bek-volume-fad--ade-conflict) — Data Disk secrets missing on BEK volume (FAD + ADE conflict)
- [`ADE-EncryptionAtHost-OSPTO`](#ade-encryptionathost-ospto--encryption-at-host-eah-osprovisioningtimeout-prereq-failures) — Encryption at Host (EAH) OSProvisioningTimeout (prereq failures)
- [`ADE-RHEL9-BootMountFailure`](#ade-rhel9-bootmountfailure--rhel-9-emergency-mode-after-enabling-ade-bls-cmdline-missing-update-bls-cmdline) — RHEL 9 Emergency mode after enabling ADE (BLS cmdline missing `--update-bls-cmdline`)
- [`ADE-Recovery-Unlock`](#ade-recovery-unlock--unlock-encrypted-linux--windows-disk-ade-recovery) — Unlock encrypted Linux + Windows disk (ADE recovery, `az vm repair` + manual BEK)
- [`ADE-Migration-DualToSingle`](#ade-migration-dualtosingle--migrate-ade-dual-pass-with-aad--single-pass-no-aad) — Migrate ADE Dual Pass (with AAD) → Single Pass (no AAD)
- [`ADE-Migration-To-EAH`](#ade-migration-to-eah--migrate-from-ade-to-encryption-at-host-retirement-2028-09-15) — Migrate from ADE → Encryption at Host (retirement 2028-09-15)
- [`ADE-IcMTemplate`](#ade-icmtemplate--asc-escalation-template-h3s3mb-for-eepg) — ASC escalation template `h3s3mb` for EEE/PG

### Server-Side Encryption with CMK (SSE+CMK)
- [`SSE-PV2-Ultra-UserMI`](#sse-pv2-ultra-usermi--ssecmk-fails-to-encrypt-premiumssdv2--ultra-with-user-assigned-mi) — SSE+CMK Fails to Encrypt PremiumSSDv2 / Ultra with User Assigned MI
- [`SSE-KeyVaultAccessForbidden`](#sse-keyvaultaccessforbidden--ssecmk-fails-with-keyvaultaccessforbidden--key-expired) — SSE+CMK Fails with KeyVaultAccessForbidden + Key Expired (DES MI lost KV perms)
- [`SSE-KeyDisabled`](#sse-keydisabled--ssecmk-vm-start-fails-keyvaultkeynotenabled-cmk-key-was-disabled) — SSE+CMK VM Start fails `KeyVaultKeyNotEnabled` (CMK key was disabled)
- [`SSE-WasPreviouslyADE`](#sse-waspreviouslyade--ssecmk-fails-disk-was-previously-encrypted-with-ade-ude-flag-persists) — SSE+CMK fails: disk was previously encrypted with ADE (UDE flag persists)
- [`SSE-MSINotFound`](#sse-msinotfound--cmk-storage-account-managedserviceidentitynotfound-msi-deleted) — CMK Storage Account `ManagedServiceIdentityNotFound` (MSI deleted)

### Foundation queries (delegated)
- See `references/azcore-queries.md` § Guest Agent & Extensions for `GuestAgentExtensionEvents` table (HeartBeat / ReportStatus / VmSettingsSummary + extension Name/Version/Message)

---

## AGEX-GA-StatusNotReported-Win — Windows GA not reporting status (3rd-party AV)

**Symptom**: Windows GA works, but Status: Not Reported. `TransparentInstaller.log` shows:
```
GetVersions() failed with exception: System.TimeoutException:
... HTTP request to 'http://168.63.129.16/?comp=versions' has exceeded the allotted timeout of 00:02:00.
```

**Cause**: 3rd-party AV (Symantec, Blue Coat Web Filter / Unified Agent) blocks WaAppAgent → WireServer status reporting.

**Mitigation**:
1. Confirm via Fiddler trace / Procmon (look for Blue Coat process interfering)
2. Customer disables AV / Blue Coat Agent + reboots

---

## AGEX-GA-Crash-Win — Windows GA / Extension Crash (Procdump + Windbg procedure)

**Scope**: WaAppAgent.exe / WindowsAzureGuestAgent.exe / extension exe suddenly disappears.

### Detection signatures

**App Event Log**:
```
Faulting application name: WaAppAgent.exe, version: 2.7.41491.949
Faulting module name: msvcrt.dll
Exception code: 0x40000015
```

**Agent log patterns**:
- `BadImageFormatException: An attempt was made to load a program with an incorrect format (HRESULT: 0x8007000B)`
- `RdCrypt Initialization failed. Error Code: -2147023143`
- `Failed to get TransportCertificate. Error: System.AccessViolationException`

### TSG 1 — Procdump as JIT (AeDebug) for repro

```cmd
md c:\dumps
:: Install procdump from https://docs.microsoft.com/en-us/sysinternals/downloads/procdump
procdump.exe -accepteula -ma -i c:\dumps
```

Disable when done: `procdump.exe -u`

For VM Agent installation debug: download VM Agent MSI + Procmon + Procdump to `c:\dumps`. Set procdump JIT. Start Procmon. Install MSI: `msiexec.exe /i c:\dumps\WindowsAzureVmAgent.<version>.msi /quiet /L*v c:\dumps\msiexec.log`. After install: `sc start rdagent` + `sc start WindowsAzureGuestAgent`. Stop Procmon → PML. Zip PML + msiexec.log + dumps + sc output.

### TSG 2 — Windbg live debug attach

Install Windbg from MS. F6 / File menu → Attach to process. Run:
```
.sympath SRV*https://msdl.microsoft.com/download/symbols
.reload /f
g
```

When stopped on exception: `kp` (stack), `r` (registers), `.dump /ma c:\temp\processdump.dmp`. Zip + send DMP.

### TSG 3 — Non-interactive / very-early crash

Set executable command-line in Windbg "Open Executable" — copy from `services.msc` → service properties → Path to Executable. Or use **ImageFileExecutionOptions** + 2-debugger approach (CDB server attaches; Windbg client commands it). Cross-link internal "TSG_Debug_with_CDB_and_Windbg".

### Dump analysis

```
.sympath SRV*c:\Symbols*http://symweb
```

GA private symbols on **Reddog share** — EEE consultation needed for access. Managed code: psscor2 / psscor4 / sos / mex extensions. Common commands: `!pe` (print exception), `!clrstack`. Reference: SOS Debug Tips, MEX Debug Tips, http://aka.ms/dbgwiki.

**Strategy**: Always involve TA / EEE for debugging strategy — repro setup is critical.

---

## AGEX-GA-FirewallWireServer-Win — Windows Firewall blocking 168.63.129.16 (80 / 32526)

Short: https://aka.ms/agexTSG009

**Symptom**: ASC/Portal shows VM Agent: Not Ready. Extensions Transitioning/Failed. WaAppAgent.log:
```
WARN (Ignoring) Exception while fetching supported versions from HostGAPlugin:
System.Net.WebException: Unable to connect to the remote server
---> System.Net.Sockets.SocketException: An attempt was made to access a socket in a way forbidden by its access permissions 168.63.129.16:32526
```

**Test**: `Test-NetConnection 168.63.129.16 -Port 80` → timeout. Also try port 32526.

### Mitigation 1: Windows Firewall / 3rd-party blocking 80 / 32526

```powershell
Get-NetFirewallRule -Enabled True -Direction Outbound -Action Block
```

Review outbound block rules → open Windows Defender Firewall with Advanced Security → check if 168.63.129.16 + port 80 / 32526 falls in any block range → disable the rule → wait few minutes → validate.

If GPO-defined: customer engages AD team. Capture report: `gpresult /h c:\temp\gpreport.html`.

If not a Firewall rule: validate via "How to determine WFP drops WoA" TSG. Engage Windows on Azure SMEs for non-firewall blocking.

> **CRITICAL FACT**: 168.63.129.16 is virtual IP of the **host node**, NOT subject to UDR / NSG. Only programs INSIDE Guest OS can block it. **Do not chase NSG/UDR for this issue.**

### Mitigation 2: Multi-IP VM routing via secondary IP

**Symptom**: `pathping 168.63.129.16` shows traffic exiting secondary IP instead of primary. Routing table confirms.

**Cause**: Windows by default may pick secondary IP for outbound when not configured otherwise.

**Resolution**: For each secondary IP:
```powershell
Set-NetIPAddress -IPAddress {Secondary_IP_Address} -SkipAsSource $true
```

Re-run pathping to confirm primary is now used.

---

## AGEX-GA-CryptoCert-Win — Keyset does not exist / MachineKeys ACL fix

### Error signatures
- `System.Security.Cryptography.CryptographicException: Keyset does not exist`
- `Failed to decode, decrypt, and deserialize the protected settings string. Error Message: Keyset does not exist`
- `Decrypting Protected Settings - Invalid provider type specified`
- `Failed to get TransportCertificate. Error: ... CryptographyNative+PInvokeException: Self-signed Certificate Generation failed. Error Code: -2146893808`

### Troubleshooting steps (all elevated)

**Step 1 — Find tenant cert UniqueKeyContainerName (PowerShell)**:
```powershell
(get-childitem Cert:\LocalMachine\My | where-object {$_.Subject -eq 'DC=Windows Azure CRP Certificate Generator'}).PrivateKey.CspKeyContainerInfo.UniqueKeyContainerName
```

**Step 2 — Backup ACL**:
```powershell
icacls C:\ProgramData\Microsoft\Crypto\RSA\MachineKeys /save machinekeys_permissions_before.aclfile /t
```

**Step 3 — Fix MachineKeys ACL (CMD)**:
```cmd
icacls C:\ProgramData\Microsoft\Crypto\RSA\MachineKeys\<UniqueKeyContainerName> /grant SYSTEM:(F)
icacls C:\ProgramData\Microsoft\Crypto\RSA\MachineKeys\<UniqueKeyContainerName> /grant Administrators:(RX)
```

**Step 4 — Verify post-state**:
```cmd
icacls C:\ProgramData\Microsoft\Crypto\RSA\MachineKeys /t > machinekeys_permissions_after.txt
```

**Step 5 — Retry extension OR restart Guest Agent services**

**Step 6 (fallback) — Also fix SystemKeys folder ACL**:
```cmd
icacls C:\ProgramData\Microsoft\Crypto\SystemKeys\* /grant SYSTEM:(F)
icacls C:\ProgramData\Microsoft\Crypto\SystemKeys\* /grant Administrators:(RX)
```
Collect PROCMON during GA restart, search "Access Denied".

**Step 7 (escalation) — SChannel trace + engage Windows Domain/Directory crypto team**:
```cmd
reg add HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\Schannel /v EventLogging /t REG_DWORD /d 7 /f
```
Ensure CAPI2 Event log is enabled.
```cmd
logman start schannel_trace -p "{37D2C3CD-C5D4-4587-8531-4696C44244C8}" 0x0000fdff -o schannel.etl -ets -ln schannel
:: repro the issue
logman stop schannel_trace -ets
```

---

## AGEX-GA-NotAutoUpgrading-Win — Windows GA not auto-upgrading (manifest timestamp bug)

**Symptom**: Windows GA stays on old version. RDAgent + WindowsAzureGuestAgent services running. Agent communicates with WireServer fine.

**Cause**: After previous failed upgrade, manifest timestamp registry value was NOT reset → next upgrade thinks it's already current.

**`TransparentInstaller.log` signature**:
```
About to loop through URIs and attempt to retrieve the LastModified header value.
Retrieved LastModifiedHeader for '...': Value: 'Thu, 10 Nov 2022 07:15:47 GMT'
Registry value for value 'ManifestTimeStamp' is 'Thu, 10 Nov 2022 07:15:47 GMT'
Manifest timestamp has not changed
```

### Resolution (ICM 365056350)

1. **Back up Guest Agent registry first**
2. Registry: `HKLM\Software\Microsoft\GuestAgent` → delete `ManifestTimeStamp` value
3. `services.msc` → restart `RDAgent` + `WindowsAzureGuestAgent`

---

## AGEX-GA-WireServerIOError-Linux — Linux WireServer not responding / IOError timed out

**Symptom (`/var/log/waagent.log`)**:
```
WireServer is not responding. Reset dhcp endpoint
Protocol endpoint not found: [ProtocolError] [Wireserver Exception] [HttpError] [HTTP Failed]
  GET http://168.63.129.16/?comp=versions -- IOError timed out -- 6 attempts made
```

Also: `An error occurred while retrieving the goal state ... ProtocolError: [ProtocolError] Exceeded max retry updating goal state`

**Cause**: When SUSE network manager `wicked` (or other Linux NM) stops/starts the Guest Network Interface (e.g., on DHCP renew), WALinuxAgent doesn't recover. Confirmed in `/var/log/messages`:
```
systemd: Stopping wicked managed network interfaces...
wickedd-dhcp4: Request to release DHCPv4 lease ...
systemd: Started wicked managed network interfaces.
[~4 min later → ProtocolError]
```

**Mitigation**: Restart WALinuxAgent OR VM. Long-term: WALinuxAgent dev team tracking in CRI 224267350.

---

## AGEX-GA-ConnectivityBlocked-Linux — Linux iptables / nftables blocking WireServer

**Symptom**: ASC/Portal VM Agent: Not Ready. Extensions Transitioning/Failed.
- `waagent.log`: `ConnectionRefusedError: [Errno 111] Connection refused`
- `systemctl status waagent.service` shows service IS running
- `sudo nc -v 168.63.129.16 80` (and 32526) returns timeout

### Background — default ADE rules in iptables `security` table

3 rules created by Linux VM Agent:
1. `ACCEPT DNS` (port 53) — all users
2. `ACCEPT` — all traffic from agent (root)
3. `DROP` — all other traffic to WireServer

Check default: `iptables -t security -L` or `nft -a list ruleset`. Customer can disable via `OS.EnableFirewall=n` in `/etc/waagent.conf`.

> **CRITICAL**: `iptables -L` (Filter table) takes precedence over Security table — always check there first.

### 3 scenarios

**Scenario 1**: Guest OS blocks all internet outbound + explicit rule for 168.63.129.16 missing
**Scenario 2**: `OUTPUT` chain default policy is `DROP` + no explicit accept for 168.63.129.16
**Scenario 3**: `iptables -L` empty but `nft -a list ruleset` has default `ip daddr 0.0.0.0/24 drop`

### Mitigation for Scenarios 1 + 2

```bash
sudo iptables -I OUTPUT -p tcp --dport 80 -d 168.63.129.16 -j ACCEPT
sudo iptables -I OUTPUT -p tcp --dport 32526 -d 168.63.129.16 -j ACCEPT
```

**Persist across reboots**:

Ubuntu / Debian:
```bash
sudo apt install iptables-persistent
sudo iptables-save > /etc/iptables/wireserver.v4
```

RHEL / SUSE:
```bash
sudo dnf install iptables-services
sudo systemctl stop firewalld
sudo systemctl disable firewalld
sudo systemctl start iptables
sudo systemctl enable iptables
sudo iptables-save > /etc/sysconfig/iptables
```

### Mitigation for Scenario 3

RHEL / SUSE:
```bash
sudo systemctl stop firewalld
sudo systemctl disable firewalld
```

Ubuntu / Debian:
```bash
sudo ufw disable
```

If still failing → another 3rd-party software uses iptables / nftables → customer engages Linux/security admin.

---

## AGEX-GA-OldGoalState-Blacklist — Linux WALinuxAgent permanently blacklisted

**Symptom**: `waagent --version` shows old agent as both running + Goal state agent:
```
WALinuxAgent-2.2.46 running on ubuntu 22.04
Goal state agent: 2.2.46
```

`waagent.log` shows WireServer connectivity issues + blacklist messages:
```
WARNING Daemon Agent WALinuxAgent-2.13.1.1 launched with command ... returned code: 1
WARNING Daemon Agent WALinuxAgent-2.13.1.1 is permanently blacklisted
INFO Daemon Installed Agent WALinuxAgent-2.2.46 is the most current agent
```

**Cause**: When new GA version doesn't terminate cleanly (e.g., WireServer connectivity failure on launch), agent gets **permanently blacklisted**. Marked via `error.json` with `"was_fatal": true` in the version folder.

### Mitigation

**Prerequisite**: Fix WireServer connectivity FIRST (see § [AGEX-GA-FirewallWireServer-Win](#agex-ga-firewallwireserver-win--windows-firewall-blocking-168631291680--32526) + § [AGEX-GA-ConnectivityBlocked-Linux](#agex-ga-connectivityblocked-linux--linux-iptablesnftables-blocking-wireserver)).

```bash
# 1. Confirm blacklist message
grep -i blacklist /var/log/waagent.log

# 2. Check version folder
ls -al /var/lib/waagent | grep WALinuxAgent

# 3. Confirm error.json with was_fatal:true
cat /var/lib/waagent/WALinuxAgent-2.13.1.1/error.json

# 4. Delete blacklist file
sudo rm -f /var/lib/waagent/WALinuxAgent-2.13.1.1/error.json

# 5. Restart waagent
sudo systemctl restart walinuxagent

# 6. (Optional) Reapply VM from Portal → forces GoalState refresh

# 7. Verify
waagent --version
ps -ef | grep -i agent
```

Reference: ICM 621866237

---

## AGEX-Ext-90minTimeout — 90-min Extension Timeout (blocks VM ops)

**Scope**: Extensions have a **90-min hardcoded timeout**. If an extension stays Transitioning, subsequent ops (other extensions OR VM start) also wait the full 90 min. Common cause of "my operation took 90 minutes".

**Detection in ASC**: Resource Explorer → Operations → operation took ~90 min. Click "Context MDM link" OR run KQL.

### Q1 — CRP ContextActivity by activityId

```kusto
cluster("azcrp").database("crp_allprod").ContextActivity
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| where activityId =~ "{OperationId}"
| project PreciseTimeStamp, message
```

Scroll: each extension reports status; you'll see one stuck reporting `Transitioning` every 15s until 90-min mark.

### Mitigation

Remove the stuck extension (use Extensions Workflow) OR fix the broken one, then retry the parent VM op. Specifically for RunCommand / CSE — customer just uninstalls extension, optionally reinstalls if script needed. RCAs after-the-fact are difficult.

---

## AGEX-Ext-TimedOutWaiting — Timed Out Waiting for Extension (handler vs extension)

**Message**: `Timed out waiting for extension <ExtensionName> to reach a terminal state. Failing the provisioning of the extension`

**Cause**: Extension did NOT update its status file with ultimate state within 90 min.

**Resolution**: Extension investigation required. **NOT** a guest agent issue.

### Handler vs extension nuance

If CRP ContextActivity has `Extension '<X>' was picked up for the Handler '<HandlerName>'` → the **handler** timed out, not the wrapped extension. Example:

```
2019-09-13 08:34:35.9919705, Extension 'AzureBackupWindowsWorkload' was picked up for the Hanlder 'Microsoft.SqlServer.Management.SqlIaaSAgent'.
2019-09-13 10:04:47.2242926, Timed out waiting for extension AzureBackupWindowsWorkload to reach a terminal state. Failing the provisioning of the extension.
```

The handler team (`SqlIaaSAgent` in the example) investigates root cause. Timeout is **NOT** due to enable command execution — the enable command may have succeeded but failed to update ultimate state.

**GA logs may have NO related messages** — EXPECTED. GA only knows if enable command timed out. If enable launches async process, GA can't catch status; GA continues reading status file every 15s + reports to CRP.

---

## AGEX-Ext-AzurePolicy — Extension DeploymentFailed DueToAzurePolicy

**Error**:
```
RequestDisallowedByPolicy: Resource 'AzurePerformanceDiagnostics' was disallowed by policy.
Policy identifiers: '[{"policyAssignment":{"name":"Only approved VM extensions should be installed", ...}]'
```

### Q1 — Cross-cluster trace by correlationId (ARM + CRP)

```kusto
let SubID = "{SubscriptionId}";
let RGName = "{ResourceGroupName}";
let starttime = datetime({StartTime});
let endtime = datetime({EndTime});
let CoID = "{CorrelationId}";
let EvnetSVC = cluster('armprodgbl.eastus.kusto.windows.net').database('ARMProd')
    | macro-expand isfuzzy=true ARMProdEG as X (
    X.database('Requests').EventServiceEntries
    | where subscriptionId == SubID and resourceUri contains RGName
    | where correlationId contains CoID
    | where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
    | project PreciseTimeStamp, ActivityId, operationId, Deployment, httpRequest, properties, ProviderName, correlationId, operationName, status, resourceUri);
let CRP = cluster('azcrp.kusto.windows.net').database('crp_allprod').ApiQosEvent_nonGet
    | where subscriptionId == SubID and resourceName contains RGName and correlationId contains CoID
    | where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
    | project PreciseTimeStamp, CRPClientRequestId=clientRequestId, httpStatusCode, goalSeekingActivityId, correlationId, CRPoperationId=operationId;
let ARM = cluster('armprodgbl.eastus.kusto.windows.net').database('ARMProd')
    | macro-expand isfuzzy=true ARMProdEG as X (
    X.database('Requests').HttpIncomingRequests
    | where subscriptionId == SubID and targetUri contains RGName and correlationId contains CoID
    | where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
    | extend resourceName = extract('\\/providers\\/[\\w-\\.]+\\/[\\w-\\.]+\\/([\\w-\\.]+)(\\/|\\?)', 1, targetUri)
    | where httpMethod !in ('GET', 'HEAD')
    | project PreciseTimeStamp, resourceName, TaskName, operationName, httpMethod, httpStatusCode, correlationId, targetUri, clientRequestId);
union EvnetSVC, ARM, CRP
| project PreciseTimeStamp, operationId, operationName, httpStatusCode, httpRequest, status, properties, resourceUri
| order by PreciseTimeStamp asc
```

### Mitigation

Azure Portal → Policy → Assignments → search policy → Edit assignment → add the failed extension name to "Approved Extensions" list → Save. Customer retries deployment.

**Collaboration**: If Azure Policy team needed → SAP `Azure/Azure Policy/Policy behavior not as expected/Policy enforcement not as expected` OR `Azure/Azure Policy/Authoring a custom policy/Policy Definition`.

### Cross-link

For **non-extension** `RequestDisallowedByPolicy` (PIP / NSG / UDR blocked at deploy time) → Playbook G § DEPLOY-Policy-Denied.

---

## AGEX-Ext-AutoUpgrade — Automatic Extension Upgrade not happening (rsm_Prod rollout + maintenance policy block)

**Scope**: VM has Automatic Extension Upgrade enabled on an extension, but the extension isn't getting upgraded.

**Verify Auto Upgrade is enabled**: ASC → VM → Extensions → select extension → "Enable automatic Upgrade" property = true.

**Publisher enrollment** required per version. Rollout takes 1-2 months in phases. Publisher list: https://aka.ms/vmextensionspublishers. Check publisher's RTO via azdeployer: https://azdeployer.trafficmanager.net/main/44444?identityProvider=dsts

### Q1 — Versions rolled out per region / phase

```kusto
let phaseMap = cluster('https://azmc2.centralus.kusto.windows.net').database('rsm_Prod').j_smdRtoRegionToPhaseMapRegular();
let monToPhase = cluster('https://azmc2.centralus.kusto.windows.net').database('rsm_Prod').j_smdRegiontocrpRegionMap()
| extend MonitoringApplicationUpper = toupper(strcat("RSM-", crpRegion, "_Monitoring"))
| join kind=leftouter phaseMap on $left.smdRegion == $right.region;
cluster('https://azmc2.centralus.kusto.windows.net').database('rsm_Prod').VMAutoExtensionUpgradeEvent
| where PreciseTimeStamp >= ago(180d)
| where type =~ "{ExtensionType}"
| extend MonitoringApplicationUpper = toupper(MonitoringApplication)
| join kind=leftouter monToPhase on $left.MonitoringApplicationUpper == $right.MonitoringApplicationUpper
| summarize max(version) by phase, crpRegion
| sort by phase desc
```

### Q2 — Specific VM current/target version + upgrade state

```kusto
cluster("azmc2.centralus.kusto.windows.net").database("rsm_Prod").VMStateEvent
| where TIMESTAMP >= ago(200d)
| where subscriptionId =~ "{SubID}"
| where vMId contains "{VMname}"
| where publisher =~ "{ExtensionPublisher}"
| where extensionType =~ "{ExtensionType}"
| project TIMESTAMP, publisher, extensionType, currentVersion, targetVersion, upgradeType, upgradeState
```

### Q3 — Upgrade event status / errors

```kusto
cluster("azmc2.centralus.kusto.windows.net").database("rsm_Prod").VMAutoExtensionUpgradeEvent
| where PreciseTimeStamp >= ago(30d)
| where subscriptionId =~ "{SubID}"
| where vMId contains "{VMname}"
| where publisher =~ "{ExtensionPublisher}"
| where type =~ "{ExtensionType}"
| project-reorder PreciseTimeStamp, vMId, publisher, type, version, status, errorCode, errorDetails, region
```

### Q4 — Maintenance Configuration blocking upgrade

```kusto
cluster('https://azmc2.centralus.kusto.windows.net').database('rsm_Prod').EventReaderPluginContextEvent
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where message contains "{SubID}"
| where message contains "{RGName}"
| where message contains "{VMname}"
| where message contains "received resourceresponse"
| sort by PreciseTimeStamp asc
| project PreciseTimeStamp, message
```

Look for `IsApproved: false` with `Reason: Update is disapproved since resource is associated to maintenance policies [...]`. Customer must update/remove Maintenance Configuration to unblock auto-upgrade.

---

## AGEX-Ext-CSE-DownloadTimeout — CSE 30-min file download cap

**Error in `handler.log`**:
```
[FATAL] Failed to download all specified files. Exiting. Exception: System.TimeoutException: Exceeded maximum file download time
at ... CustomScriptHandler.Downloader.DownloadManager.DownloadAsyncWithBlobClientDownloader(...)
```

**Cause**: CSE hits hardcoded **30-min** max download time for script files.

**Mitigation**: Inform customer of 30-min limit. They reduce script file size/count.

---

## AGEX-Ext-CSE-ExitCode50-124 — CSE AKS VMSS Exit Code 50 / 124 (network block)

**Scope**: CSE on AKS VMSS instances fails with ExitCode **50** (Connection reset by peer) or **124** (command timeout).

### Error signatures
- ExitCode 50: `Enable failed: failed to execute command: command terminated with exit status=50` + `[stderr] date: invalid date 'n/a'`
- ExitCode 124: `Enable failed: failed to execute command: command terminated with exit status=124` + curl progress meter showing hung downloads + `BootDatapoints` showing endpoints

**Cause**: ExitCode 50 = network reset; ExitCode 124 = command timed out. AKS bootstrap CSE can't reach AKS control plane or package repository. Usually firewall / NSG / routing blocks outbound.

### Investigation
1. Confirm post-allocation failure (not capacity / OSPTO)
2. Check NetVMA + EagleEye for platform network status on the node/container
3. If platform clean → guest-level. Collect guest logs from AKS instance under `/var/log/azure/`
4. **CRITICAL**: AKS deletes failing instance after 15-30 min. Collect logs IMMEDIATELY before deletion
5. **Managed OS disk**: ASC → Inspect IaaS Disk (IID) immediately, save locally before refresh
6. **Ephemeral OS disk**: IID doesn't work. Customer SSHs into instance, checks `/var/log/azure/cluster-provision.log`

### Mitigation
- DNS resolution, routing table, NSG checks. Ask about recent network changes
- Deeper networking → **OPEX Collaboration Optimization AzNet**
- AKS control-plane-only → SAP `Azure/Kubernetes Service (AKS)/Create, Upgrade, Scale and Delete operations (cluster or nodepool)`

Ref: https://learn.microsoft.com/en-us/azure/aks/outbound-rules-control-egress + https://learn.microsoft.com/en-us/troubleshoot/azure/azure-kubernetes/create-upgrade-delete/error-code-outboundconnfailvmextensionerror

---

## AGEX-Ext-CSE-Lock — CSE Timed Out Waiting for Lock (customer script too long)

**Message in `/var/log/azure/custom-script/handler.log`**:
```
custom-script-extension is open by the following processes:
COMMAND    PID USER  FD   TYPE DEVICE SIZE/OFF   NODE NAME
custom-sc 2336 root txt    REG    8,1  8192284 256072 /var/lib/waagent/Microsoft.Azure.Extensions.CustomScript-2.1.1/bin/custom-script-extension
sleeping for 3 seconds before retry, attempt 1 of 10
...
sleeping for 3 seconds before retry, attempt 10 of 10
Timed out waiting for lock on custom-script-extension
...
failed to execute command" error="command terminated with exit status=4"
```

**Cause**: Customer's script taking too long to run (and exits with non-zero code).

**Resolution**: Customer reviews script.

**Background**: CSE has built-in lock + 10-retry backoff. Originally added because AV / anti-malware sometimes held a lock on the executable preventing process start.

---

## AGEX-Ext-CSE-Storage — CSE Storage Account failures (SA firewall / PE / MI / SAS)

**Patterns**:
- SA firewall blocks VM IP → 403 / connectivity failure
- Private endpoint not in same VNet OR DNS doesn't resolve to PE IP
- Managed Identity auth: VM/VMSS missing MI or MI lacks `Storage Blob Data Reader` on SA/container
- SAS URL expired / regenerate needed
- Public network access disabled on SA → route via PE or whitelist VM IP

**Mitigation**:
- SA firewall → customer adds VM / VNet / IP to allowed range
- Private endpoint → ensure DNS resolves to PE IP from VM, OR use MI + storageAccountUri pattern
- MI auth → ensure VM/VMSS has MI assigned with `Storage Blob Data Reader` on SA / container
- SAS expired → regenerate SAS URL in CSE settings

---

## AGEX-Ext-RunCommand-Conflict — RunCommandConflict (existing RC still running)

**Error**:
```
{
  "innererror": { "internalErrorCode": "RunCommandConflict" },
  "code": "Conflict",
  "message": "Run command extension execution is in progress. Please wait for completion before invoking a run command."
}
```

### Q1 — Find existing RunCommand on VM (CRP)

```kusto
let subId = '{SubscriptionId}';
let opStartTime = todatetime('{StartTime}');
let opEndTime = todatetime('{EndTime}');
let resourceGroup = '{ResourceGroupName}';
let vmName = '{VMName}';
let virtualMachineID = '{VMId}';
cluster('azcsupfollower2.centralus').database('crp_allprod').ApiQosEvent
| where TIMESTAMP >= opStartTime and TIMESTAMP <= opEndTime and subscriptionId == subId and operationName !contains '.GET'
| join kind=leftouter (
    cluster('azcsupfollower2.centralus').database('crp_allprod').VMApiQosEvent
    | where TIMESTAMP >= opStartTime and TIMESTAMP <= opEndTime
    | where ((isnotnull(virtualMachineID) and isnotempty(virtualMachineID) and (vMId =~ virtualMachineID))
         or (resourceName =~ vmName and resourceGroupName =~ resourceGroup))
) on $left.goalSeekingActivityId == $right.operationId
| extend startTime = PreciseTimeStamp - e2EDurationInMilliseconds * 1ms, completeTime = PreciseTimeStamp
| extend state = case (resultType == 0, 'Success', resultType == 1, 'Client Error', resultType == 2, 'Internal Error', 'Unknown')
| where operationName has 'RunCommand'
| project startTime, completeTime, operationName, state, operationId, resourceGroupName, resourceName, correlationId,
          httpStatusCode, vmId=vMId, resultCode, errorDetails
| order by startTime desc
| take 5000
```

### Q2 — ARM JobTraces by correlationId (RESTRICTED to PG)

```kusto
let start = datetime({StartTime});
let end = datetime({EndTime});
cluster('armprodgbl.eastus.kusto.windows.net').database('ARMProd')
| macro-expand isfuzzy=true ARMProdEG as X (
    X.database('Jobs').JobTraces
    | where TIMESTAMP >= start and TIMESTAMP <= end
    | where correlationId contains '{CorrelationId}'
    | project TIMESTAMP, correlationId, operationName, jobId, message, exception
    | order by TIMESTAMP asc
)
```

Successful ARM trace ends with `Frontdoor job completed with status: 'Succeeded'`. If absent → RunCommand still running per platform.

### Mitigation
1. Wait for existing RunCommand to complete (up to 90-min default timeout)
2. Terminate hung script: customer SSH/RDP, find process (Windows: PowerShell/cmd under SYSTEM), terminate it

---

## AGEX-Ext-RunCommand-FabricOpFailed — RC v2 upgrade extensionVersions conflict mitigation

**Error on RunCommand v2 ('Managed RunCommand') upgrade** (Windows 2.0.4 → 2.0.5, Linux 1.3.1 → 1.3.2):
```
ResultCode: InternalExecutionError/FabricInternalOperationError
The fabric operation failed.
InternalDetail: A different extension upgrade info (version) with the same key has already been added to extensionVersions. Key: Microsoft.CPlat.Core.RunCommandHandlerWindows.
```

### Mitigation

**Step 1 — List all RunCommands v2 on VM**:
```powershell
$rg = "myRG"; $vmName = "myVM"
$runCommandsList = Get-AzVmRunCommand -ResourceGroupName $rg -VMName $vmName
```

**Step 2 — Delete ALL (ignore errors)**:
```powershell
for($i = 0; $i -lt $runCommandsList.Count; $i++) {
    Remove-AzVMRunCommand -ResourceGroupName $rg -VMName $vmName -RunCommandName $runCommandsList[$i].Name
}
```

Verify `$runCommandsList.Count -eq 0`. Removes the v2 extension.

**Variation for in-progress RC preservation**:
```powershell
for($i = 0; $i -lt $runCommandsList.Count; $i++) {
    $x = Get-AzVmRunCommand -ResourceGroupName $rg -VMName $vmName -RunCommandName $runCommandsList[$i].Name -Expand InstanceView
    if($x.InstanceView.ExecutionState -in ("Succeeded", "Failed", "Deleting")) {
        Remove-AzVMRunCommand -ResourceGroupName $rg -VMName $vmName -RunCommandName $runCommandsList[$i].Name
    }
}
```

**Step 3** — Subsequent use of RC v2 will pull latest (2.0.5 Windows, 1.3.2 Linux).

Ref: ICM 347259838

---

## AGEX-Ext-VMAccess-Umbrella — VMAccess Errors (9-error routing table)

VMAccess extension covers password resets, SSH key resets, RDP/SSH unavailable scenarios. The wiki TSG is an umbrella with 9 distinct errors:

| Error | Mitigation |
|---|---|
| `CannotModifyExtensionsWhenVMNotRunning` | Confirm VM is running in portal/ASC |
| `VMAccess Extension does not support Domain Controller` | Cannot reset password on DC. Follow VM Password Reset TSG |
| `VM 'vmname' has not reported status for VM agent or extensions` | Follow Guest Agent Basic Workflow. Cross-link § [AGEX-GA-StatusNotReported-Win](#agex-ga-statusnotreported-win--windows-ga-not-reporting-status-3rd-party-av) |
| `Cannot update Remote Desktop Connection settings for Administrator account ... password does not meet the password policy requirements` (COMException via DirectoryServices) | Follow EnableVMAccess Password Requirements TSG; password must satisfy domain policy |
| `The Admin User Account password cannot be null or empty if provided the username` | Provide password |
| `Provisioning of VM extension enablevmaccess has timed out` | Cross-link § [AGEX-Ext-90minTimeout](#agex-ext-90mintimeout--90-minute-extension-timeout-blocks-vm-ops) |
| `User account scsadmin already exists but cannot be updated because it is not in the Administrators group` | Customer adds user to Administrators group on DC |
| `MultipleExtensionsPerHandlerNotAllowed` (Windows) | Manually `Remove-AzVMExtension` and retry |
| `Enable failed: No password or ssh_key is specified` (Linux) | Provide password/ssh_key |

**RCA coding**: `Windows Azure\Compute\Virtual Machine\Password Reset`

---

## AGEX-Ext-DomainJoin-Shutdown — Domain Join "Failed to initiate system shutdown"

**Symptom**: JsonADDomainExtension fails with `Failed to initiate system shutdown`. VM restarts but stays in workgroup.

**Logs**:
- `C:\WindowsAzure\Logs\Plugins\Microsoft.Compute.JsonADDomainExtension\<Version>\ADDomainExtension.log`:
  ```
  Join failed for Domain '<>' with the error: Failed to initiate system shutdown.. More information: 0x0
  ```
- `C:\Windows\debug\Netlogon.log`:
  ```
  NetpDoDomainJoin: status: 0x0
  DeviceUnjoin: device unjoin finished. HRESULT: 0x00000000
  ```
  (VM joined then unjoined)

### Root cause

1. SYSTEM account missing "Shut down the system" privilege
2. Another script / scheduled task triggers restart during DJ process → interrupts extension

### Solution

**1. Verify SYSTEM Shutdown privilege**:
`Computer Configuration → Windows Settings → Security Settings → Local Policies → User Rights Assignment → Shut down the system`
Both SYSTEM + Administrators group should have it by default.

**2. Check System event log** for external restart events around extension activity time. Customer's scripts / extensions / automation may interrupt.

---

## ADE-AccessDenied — Access Denied / Failed to configure bitlocker as expected

**Error**:
```
VM has reported a failure when processing extension 'AzureDiskEncryption'.
Error message: "Failed to configure bitlocker as expected. Exception: Access denied
```

**Logs**:
- `C:\WindowsAzure\Logs\Plugins\Microsoft.Azure.Security.AzureDiskEncryption\<version>\Bitlocker.log`
- MDM Tables in ASC

### Mitigation 1: Grant KV permissions to AAD app (PowerShell)

1. Find Vault + ClientID (ApplicationID) in `APIQosEvent` (Jarvis), filter on `VMExtensions.VMExtensionOperation.PUT`. Note Node, OperationID, ContextActivity activityId.
2. Find ClientID in `SPIQosEvent` for the AAD app.
3. Grant:

```powershell
$keyVaultName = '<yourKeyVaultName>'
$aadClientID = '<yourAadAppClientID>'
$rgname = '<yourResourceGroup>'

Set-AzKeyVaultAccessPolicy -VaultName $keyVaultName -ServicePrincipalName $aadClientID `
    -PermissionsToKeys 'WrapKey' -PermissionsToSecrets 'Set' -ResourceGroupName $rgname
```

### Mitigation 2: Portal-based add of ApplicationID to KV access policy

Portal → Key Vault → Access Policies → Add Access Policy → select ApplicationID → grant `WrapKey` (keys) + `Set` (secrets) → SAVE.

---

## ADE-KVTenantID-Wrong — Key Vault Associated to Wrong TenantID (KV moved tenants)

**Error**:
```
Set-AzureRmVMDiskEncryptionExtension : Long running operation failed with status 'Failed'.
Additional Info: 'https://keyvaultname.vault.azure.net/secrets/secret-<>/version<> secret doesn't have the
DiskEncryptionKeyEncryptionAlgorithm tags. Please update the secret version, add the required tags and retry.'
```

**Cause**: KV tenant ID mismatch — KV was moved between subscriptions, OR sub's tenant changed. KV originally created in tenant A; sub now in tenant B → principals in B can't access KV.

### Mitigation

**Step 1 — Update KV tenant ID + clear access policies**:
```powershell
$vaultResourceId = (Get-AzKeyVault -VaultName myvault).ResourceId
$vault = Get-AzResource -ResourceId $vaultResourceId -ExpandProperties
$vault.Properties.TenantId = (Get-AzContext).Tenant.TenantId
$vault.Properties.AccessPolicies = @()
Set-AzResource -ResourceId $vaultResourceId -Properties $vault.Properties
```

**Step 2 — Clear stale encryption settings from VM model + reapply** (full `Set-EncryptionSettings.ps1` script, ~80 lines, in the wiki TSG). Process:
1. Stop VM
2. Set `EncryptionSettings.Enabled = false` on OsDisk
3. Set `DiskEncryptionKey = null` + `KeyEncryptionKey = null`
4. `Update-AzVM`
5. Set new EncryptionSettings with new KV references
6. `Update-AzVM`
7. Start VM

**Step 3 — Set new KV access policies with new tenant's principals**:
```powershell
Set-AzKeyVaultAccessPolicy ...
```

---

## ADE-KVNotFoundDirectory — Keyvault not found in the Directory (AAD tenant mismatch)

**Error**: `Keyvault not found in the directory`

**Cause**: KV not in same AAD tenant as the AAD Application.

**Resolution**: Move KV to same tenant as AAD App (use the [ADE-KVTenantID-Wrong](#ade-kvtenantid-wrong--key-vault-associated-to-wrong-tenantid-kv-moved-tenants) procedure if KV was moved).

---

## ADE-NetworkAclsBypass — networkAcls.bypass must include "AzureServices"

**Error**:
```
Failed to update key vault '<>'. Error: When enabledForDiskEncryption is true, networkAcls.bypass must include "AzureServices".
```

**Cause**: ADE requires KV access from trusted Azure services. KV network restriction without "AzureServices" bypass blocks ADE.

### Mitigation

Portal: KV → Networking → enable "Allow trusted Microsoft services to bypass this firewall" checkbox.

CLI:
```bash
az keyvault update --name "keyvaultname" --bypass AzureServices
```

Then retry ADE.

---

## ADE-VMStartup-SecretRetrievalFailed — DiskEncryptionKeySecretRetrievalFailed (VM can't boot after encryption)

**Error**: `DiskEncryptionKeySecretRetrievalFailed: Error encountered when retrieving secret from Key Vault`. VM fails to boot (OS disk can't be unlocked).

**Cause** (one of):
- KV containing disk encryption secret was deleted (soft or permanently)
- Specific secret deleted, expired, or version no longer exists
- RBAC / access policy changes block ADE / VM MI from retrieving secret
- Sub / tenant / resource moves broke trust path

### Mitigation

**1. Check KV existence + recoverable**:
```bash
az keyvault list-deleted
az keyvault recover --name <vaultName>
```

**2. Check secret + recover**:
```bash
az keyvault secret show --vault-name <vaultName> --name <secretName>
az keyvault secret recover --vault-name <vaultName> --name <secretName>
```

**3. Permanently lost** (worst case):
- **ADE (BEK/KEK)**: cannot unlock VM. Restore from backup / snapshot; rebuild VM + attach data disks if only OS disk blocked
- **SSE+CMK**: disable CMK or rotate to new key

### Preventive

- Enable **soft delete** + **purge protection** on all KVs used for ADE / CMK
- `az keyvault secret backup --vault-name <vaultName> --name <secretName>` regularly
- Alerts for secret / key expiration
- Azure Policy to enforce soft delete + purge protection + RBAC model

---

## ADE-DataDisksSkipped — Data Disks silently skipped (extension v2.2.0.37 regression)

**Symptom**: After encryption finishes, some data disks remain unencrypted. Higher risk on Storage Spaces disks + Windows Server 2012 data disks. Logs show:
```
BitlockerOperations::IntializeMachineVolumes Skipping Volume Backed by VHD: VolumeName: H:\, VolumeLabel: DataB1, ...
```

**Cause**: Regression in ADE extension **v2.2.0.37** — misidentifies storage space disks and WS2012 data disks as VHD-backed and silently skips them. New deployments / scale-outs hit this; existing encrypted VMs don't decrypt.

### Mitigation — Downgrade to v2.1.0.36 (note the major.minor change from 2.2 to 2.1)

```powershell
Remove-AzVMDiskEncryptionExtension -ResourceGroupName "MyResourceGroup" -VMName "MyTestVM"

$KVRGname = 'MyKeyVaultResourceGroup'
$VMRGName = 'MyVirtualMachineResourceGroup'
$vmName = 'MySecureVM'
$KeyVaultName = 'MySecureVault'
$KeyVault = Get-AzKeyVault -VaultName $KeyVaultName -ResourceGroupName $KVRGname
$diskEncryptionKeyVaultUrl = $KeyVault.VaultUri
$KeyVaultResourceId = $KeyVault.ResourceId
$sequenceVersion = [Guid]::NewGuid()

Set-AzVMDiskEncryptionExtension -TypeHandlerVersion 2.1 -DisableAutoUpgradeMinorVersion `
    -ResourceGroupName $VMRGname -VMName $vmName `
    -DiskEncryptionKeyVaultUrl $diskEncryptionKeyVaultUrl `
    -DiskEncryptionKeyVaultId $KeyVaultResourceId `
    -VolumeType "All" -SequenceVersion $sequenceVersion
```

VMSS variant: `Set-AzVmssDiskEncryptionExtension ... -TypeHandlerVersion 2.1 -DisableAutoUpgradeMinorVersion`

Ref: ICM 233082175

---

## ADE-DataDiskSecretsMissing — Data Disk secrets missing on BEK volume (FAD + ADE conflict)

**Symptom**: Data disk secret missing on BEK volume.

**Linux**: `LinuxPassPhraseFileName_1_0` not in `/mnt/azure_bek_disk`. Boot prompts for passphrase:
```
Please enter passphrase for disk Virtual_Disk ...
```

Log `/var/log/messages`:
```
Failed to activate, key file '/mnt/azure_bek_disk/LinuxPassPhraseFileName_1_0' missing.
```

**Windows**: similar — encrypted data disk fails to mount on boot.

### Root cause (Fast Attach/Detach + ADE incompatibility)

ADE doesn't support attach/detach as an update. When CRP creates tenant, then sends data disk info, then starts:

1. Fabric sends CCF with **NO** data disks first → ADE creates BEK disk based on OS disk only
2. Start command + new CCF (with data disks) arrives → BEK disk does **NOT** get recreated

→ Data disk encryption secrets missing from VM.

### Mitigation

**1. Deallocate + start VM** → remounts BEK volume + stores data disk secrets.

**2. Disable FAD for the VM** (if Trusted Launch NOT enabled):

Add tag:
```
Tag Name:  DisableFastDiskAttachDetach
Tag Value: true
```

> **WARNING**: Using this tag on a Trusted Launch VM may prevent boot.

**3. For sub-wide disable**: PG ICM to stop FAD on subscription basis.

### Tracking
- WI: https://msazure.visualstudio.com/One/_workitems/edit/30346848
- ICMs: 415927576, 520363645
- Related: [Data disks with ADE not being mounted at boot](https://supportability.visualstudio.com/AzureLinuxNinjas/_wiki/wikis/AzureLinuxNinjas/1542993/Data-disks-with-ADE-not-being-mounted-at-boot)

---

## ADE-EncryptionAtHost-OSPTO — Encryption at Host (EAH) OSProvisioningTimeout (prereq failures)

**Scope**: New VM with EAH enabled fails deploy with **OSProvisioningTimeout**. Same VM deploys fine without EAH. **No OS guest logs generated** (VM never reaches boot).

**Cause**: EAH initializes BEFORE OS provisioning. EAH prerequisite failures surface as OSPTO. Typical:

- Unsupported disk type / sector size:
  - **Ultra Disk** + **Premium SSD v2** fully supported
  - **512e Premium/Standard SSD** supported **only if created AFTER 2023-05-13**
- VM size doesn't support EAH
- Disks in lineage previously had **ADE** enabled
- Region / host capacity for EAH-capable host
- Custom images / snapshots with old disk metadata

### Validate

**1. Disk compatibility**:
```bash
az disk show -n <diskName> -g <rg> --query "{sku:sku.name, created:timeCreated}"
```
Disks created **before 2023-05-13** OR previously ADE-enabled → recreate the disk or generate new incremental snapshot.

**2. VM SKU supports EAH**:
```bash
az vm list-skus -l <region> --query "[?capabilities[?name=='EncryptionAtHostSupported']].name"
```

**3. Reproduce without EAH** — if it succeeds, confirms EAH prereq issue, not OS issue.

**4. Retry** with new disks, different region, or supported SKU.

### Cross-link
- Generic OSPTO at deploy → Playbook G § DEPLOY-Provision-OSPTO
- Cloud-init Linux OSPTO subset → Playbook G § DEPLOY-Provision-CloudInit

---

## ADE-IcMTemplate — ASC escalation template `h3s3mb` for EEE/PG

**Process**:
1. ASC case page → top right → **Escalate Case**
2. Search **All** → template **`h3s3mb`** → Next
3. Fill required fields → Submit

Used for all ADE escalations to EEE/PG when local mitigation fails.

---

## SSE-PV2-Ultra-UserMI — SSE+CMK Fails to Encrypt PremiumSSDv2 / Ultra with User Assigned MI

**Error**:
```
DiskEncryptionSet <Disk encryption Set name> with UserAssigned identity type is not supported for disk <disk name>
  since it has 'PremiumV2_LRS' SKU.
"internalErrorCode": "DirectDriveDiskNotSupportUserAssignedIdentityDes"
```

**Cause**: User-assigned managed identities are **NOT** supported for Ultra + Premium SSD v2 disks encrypted with CMK. This is a documented public restriction.

### Investigation
- Disk SKU == `PremiumV2_LRS` OR `UltraSSD_LRS`
- DES using **User Assigned MI** for authentication

### Mitigation
Create a new DES **without** User Assigned MI, OR use an existing DES with **System Assigned MI**. Then encrypt the PV2/Ultra disk.

Ref: https://learn.microsoft.com/en-us/azure/virtual-machines/disk-encryption#restrictions

---

## AGEX-Ext-PerfDiagnostics-FIPS — Azure Performance Diagnostics fails with VMExtensionProvisioningError (FIPS mode)

**Symptom**: Extension fails to install. Handler/Agent logs contain:
```
System.InvalidOperationException: This implementation is not part of the Windows Platform FIPS validated cryptographic algorithms
  at System.Security.Cryptography.MD5CryptoServiceProvider..ctor()
```

**Cause**: PerfInsights uses MD5; when FIPS mode is enabled on Windows VM, `MD5CryptoServiceProvider` throws. Bug: msazure ADO #10087255.

### Mitigation (with backup)
1. Check FIPS state in registry — `HKLM\System\CurrentControlSet\Control\Lsa\FipsAlgorithmPolicy` — `Enabled` value (0=disabled, 1=enabled).
2. Backup registry + OS disk.
3. Set `Enabled=0` → **reboot server**.
4. Retry extension install.

Engage Windows Guest OS team if customer cannot disable FIPS (regulatory requirement).

---

## AGEX-GA-Logs-ETLDiskFillup — `C:\WindowsAzure\Logs` filling with `RuntimeEvents_*.etl.old` + `WaAppAgent_*.etl.old`

**Symptom**: Customer reports disk full / disk space alerts. `C:\WindowsAzure\Logs` directory contains many `RuntimeEvents_xxxxxx.etl.old` and `WaAppAgent_xxxxxx.etl.old` files consuming significant disk space.

**Cause**: Old WindowsVMAgent versions did not rotate/clean old ETL files. Bug fixed in WinGA `2.7.41491.969`, further improved in `2.7.41491.1030+`.

### Mitigation
Upgrade WindowsVMAgent to **latest** version from https://github.com/Azure/WindowsVMAgent/releases. Once upgraded, the issue self-mitigates (old files cleaned up).

Ref: ADO #6330381 · https://docs.microsoft.com/en-US/troubleshoot/azure/virtual-machines/support-extensions-agent-version#minimum-supported-version-of-windows-vm-agent

---

## ADE-RHEL9-BootMountFailure — RHEL 9 Emergency mode after enabling ADE (BLS cmdline missing `--update-bls-cmdline`)

**Symptom**: VM not booting after enabling ADE feature on RHEL 9 — VM enters Emergency mode.

Console signatures:
```
dracut-initqueue[600]: + bootuuid=                          ← EMPTY
dracut-initqueue[600]: + crypttab_contains osencrypt /dev/sda
[ TIME ] Timed out waiting for device /dev/disk/by-uuid
[DEPEND] Dependency failed for /boot
A dependency job for boot.mount failed.
```

**Root cause**: BLS cmdline (`.conf` files in `/boot/loader/entries/`) NOT updated by `grub2-mkconfig`. Newer `grub2-mkconfig` requires `--update-bls-cmdline` flag, which ADE source code only appends when RHEL version >= 9.3 ([`redhatPatching.py`](https://github.com/Azure/azure-linux-extensions/blob/master/VMEncryption/main/patch/redhatPatching.py)). Also affected: any RHEL with `grub2-tools >= 2.06-69` (Aug 2023 patch onward).

### Mitigation (chroot in recovery VM)
```bash
# Option 1 — re-run mkconfig with the missing flag
grub2-mkconfig --update-bls-cmdline -o /boot/grub2/grub.cfg

# Option 2 — downgrade grub2-tools to pre-patch version
yum downgrade -y grub2-tools-2.06-61.el9
grub2-mkconfig -o /boot/grub2/grub.cfg
```

Tracking: ICM 527425501 (PG working on permanent fix).

---

## ADE-Recovery-Unlock — Unlock encrypted Linux + Windows disk (ADE recovery)

**When to use**: Collect logs from encrypted disk (normal tools fail), or fix OS file system on broken ADE VM. Works for BEK+KEK (with and without AAD).

**Unlock ≠ Decrypt** — unlock = read-only file access; decrypt = remove encryption entirely.

### Method 1 (preferred) — `az vm repair` automatic (single-pass only)

Linux:
```bash
az extension add -n vm-repair
az extension update -n vm-repair
az vm repair create -g <rg> -n <source-vm-name> --unlock-encrypted-vm --verbose
# After completion, login to repair VM — disk is already unlocked
# When done:
az vm repair restore -g <rg> -n <source-vm-name> --verbose
```

Windows: same commands. After unlock, in repair VM:
```cmd
manage-bde -off <DRIVE>:    # optional: decrypt fully
```

**Requires public IP** for repair VM. For dual-pass VMs, fall back to Method 2.

### Method 2 — Manual rescue VM

**Critical**: encrypted disk MUST be attached **DURING** repair VM creation, NOT after. BEK volume only auto-attaches when system detects encryption settings at create time.

#### Linux manual unlock
```bash
sudo -s
lsblk                              # find encrypted disk (multiple parts, no '/' mount)
umount /boot/efi; umount /boot     # if mounted

# Find + mount BEK volume
lsblk -fs | grep -i bek            # e.g. sdc1  vfat  BEK VOLUME
mkdir /mnt/azure_bek_disk
mount /dev/sdc1 /mnt/azure_bek_disk
ls -l /mnt/azure_bek_disk          # LinuxPassPhraseFileName = the key

# Mount boot partition (header lives here)
mkdir /{investigateboot,investigateroot}
mount /dev/sdd2 /investigateboot   # use -o nouuid if mount fails

# Unlock
cryptsetup luksOpen --key-file /mnt/azure_bek_disk/LinuxPassPhraseFileName \
  --header /investigateboot/luks/osluksheader /dev/sdd4 osencrypt
mount /dev/mapper/osencrypt /investigateroot   # activate LVM first if needed
```

#### Windows manual unlock
1. RDP to rescue VM → Disk Management → locate BEK volume → assign drive letter (e.g. G).
2. List hidden BEK files: `dir H: /a:h /b /s` — find the `.BEK` file.
3. Unlock:
   ```cmd
   manage-bde -unlock <DRIVE>: -RecoveryKey H:\<GUID>.BEK
   ```
4. Optional full decrypt: `manage-bde -off <DRIVE>:`.

For unmanaged disks or dual-pass: follow Manual Troubleshoot section in the wiki TSG.

---

## ADE-Migration-DualToSingle — Migrate ADE Dual Pass (with AAD) → Single Pass (no AAD)

**Scope**: Windows ADE 1.1.* → 2.2 ; Linux ADE 0.1.* → 1.2. PowerShell only (Az module >= 5.9.0).

### Determine ADE version
- Portal: VM → Extensions → `AzureDiskEncryption` or `AzureDiskEncryptionForLinux` → Version field
- CLI: `az vm get-instance-view --resource-group <rg> --name <vm>` → `TypeHandlerVersion`
- PowerShell: `Get-AzVM -ResourceGroupName <rg> -Name <vm> -Status` → `TypeHandlerVersion`

### Migrate command
```powershell
Set-AzVMDiskEncryptionExtension -ResourceGroupName <rg> -VMName <vm> -Migrate
# Confirm 'Y'. VM is rebooted.
```

**Hard constraint**: `-Migrate` works ONLY on VMs already encrypted with ADE + AAD. **Terminal error** if used on unencrypted VM or ADE-without-AAD VM.

Ref: https://docs.microsoft.com/en-us/azure/virtual-machines/linux/disk-encryption-upgrade

---

## ADE-Migration-To-EAH — Migrate from ADE → Encryption at Host (retirement 2028-09-15)

**Why**: Microsoft announced ADE retirement on Sep 15, 2028. Customers must migrate to Encryption at Host (EAH).

### Hard constraints
- **No in-place migration** — must create new disks + new VM.
- **Linux OS-disk ADE**: CANNOT disable; **MUST recreate VM** with new OS disk.
- **Windows ADE**: only encrypts OS-only OR OS+data; never data-only.
- **UDE flag persists** in disk metadata even after decryption. Snapshots + disk Copy method retain UDE flag → migration requires **Upload method** (new disk + VHD blob copy) to strip metadata.
- **Downtime required** for disk operations + VM recreation.
- **Domain-joined VMs**: remove from domain before delete; rejoin new VM (Linux uses `AADSSHLoginForLinux` extension).

### Workflow
1. Check domain join → if yes, document settings + remove from domain pre-migration.
2. Remove ADE (only when Windows OS+data OR Linux data-only).
3. Create copy of managed disks using **Upload + blob copy** (not snapshot Copy) — strips UDE flag.
4. Create new VM from new disks with **Encryption at Host enabled at create time**.
5. Verify config + rejoin domain.
6. Cleanup old resources.

### Disable ADE on Linux data-only
```bash
az vm encryption show --name <vm> --resource-group <rg>
az vm encryption disable --name <vm> --resource-group <rg> --volume-type data
az vm extension delete -g <rg> --vm-name <vm> -n AzureDiskEncryptionForLinux
sudo cryptsetup status /dev/mapper/<device-name>   # verify no longer active
```

### Linux OS-encrypted case
NOT migratable in place. Customer must recreate VM with new OS disk + EAH enabled at create time.

---

## SSE-KeyVaultAccessForbidden — SSE+CMK Fails with KeyVaultAccessForbidden + Key Expired

**Two scenarios** — same TSG covers both root causes:

### Symptom 1 — `KeyVaultAccessForbidden`
VM in Failed state. Disk Encryption Set's system-assigned MI lost access to Key Vault.

### Symptom 2 — Key expired
```
Unable to access key 'https://<keyVaultName>.vault.azure.net/keys/<keyname>/<Secret>'. Key is expired.
```

### Mitigation 1 — KV using **Access Policy** mode
1. Azure Portal → Disk Encryption Set → overview tab → click error notification (auto-grants required perms).
2. Or manually: KV → Access Policies → add DES → grant **Get + UnwrapKey + WrapKey** → Save.
3. Start the VM.

### Mitigation 1 alt — KV using **RBAC** mode
1. KV → Access Control (IAM) → Add Role Assignment.
2. Role: **Key Vault Crypto Service Encryption User**.
3. Members: select the DES (search by name/ID) → Review + Assign.

### Mitigation 2 — Key expired
- Manual: KV → Keys → expired key → Rotation policy → **Rotate now**.
- Auto: configure rotation policy per [Automatic key rotation of customer-managed keys](https://learn.microsoft.com/en-us/azure/virtual-machines/disk-encryption#automatic-key-rotation-of-customer-managed-keys).

---

## SSE-KeyDisabled — SSE+CMK VM Start fails `KeyVaultKeyNotEnabled` (CMK key was disabled)

**Error in Portal/ASC**: `KeyVaultKeyNotEnabled`
```
The key vault key 'https://<kv>.vault.azure.net/keys/<keyname>' used for disk encryption set '<DESName>' must be enabled state.
```

### Investigation — pull failed PUT from CRP via correlationId
```kusto
cluster("Azcsupfollower2.centralus.kusto.windows.net").database("crp_allprod").ApiQosEvent_nonGet
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where correlationId =~ trim(" ", "{correlation_id}")
| extend startTime = datetime_add('millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp)
| project-reorder startTime, PreciseTimeStamp, e2EDurationInMilliseconds, region, operationId, operationName,
          resourceGroupName, resourceName, httpStatusCode, resultCode, requestEntity, errorDetails, labels
| sort by PreciseTimeStamp asc
```
Filter on `resultCode == "KeyVaultKeyNotEnabled"`.

### Cause
KV key configured in DES for SSE+CMK was in **disabled** state → Azure can't unwrap DEK → VM can't attach encrypted disk during start.

### Mitigation
1. Portal → KV in error message → Keys → disabled key → Current Version.
2. Change `Enabled` from **No** to **Yes** → Save.
3. Start the VM.

---

## SSE-WasPreviouslyADE — SSE+CMK fails: disk was previously encrypted with ADE (UDE flag persists)

**Error**:
```
OperationNotAllowed: Disk '<disk-name>' was previously encrypted with Azure Disk Encryption.
Server-side encryption with customer managed keys cannot be enabled on this disk at this time.
```

### Investigation — check if UDE flag still on disk
```powershell
$VM = Get-AzVM -ResourceGroupName "<rg>" -Name "<vm>"
$osdisk = $VM.StorageProfile.OsDisk
$disk = Get-AzDisk -ResourceGroupName $vm.ResourceGroupName -DiskName $osdisk.Name
if ($disk.EncryptionSettingsCollection -eq $null) {
    "Never Encrypted"
} else {
    "Either encrypted or decrypted — UDE flag still set in metadata"
}
```

### Cause
ADE stamps `EncryptionSettingsCollection` (UDE flag) in disk metadata. Even after decryption, the flag persists → SSE+CMK enable fails. Public restriction: https://learn.microsoft.com/en-us/azure/virtual-machines/disk-encryption#restrictions

### Mitigation

#### Linux
- OS-disk Linux ADE: **CANNOT** decrypt OS+data → must rebuild VM.
- Data-disk-only Linux ADE: decrypt data disks → migrate to SSE+CMK.

#### Windows
1. Decrypt + remove ADE.
2. Copy managed disk to NEW managed disk (this strips UDE flag — but only via the `New-AzDiskConfig -CreateOption Copy` path):
```powershell
$region="eastus2"; $targetRG="<rg>"; $targetDiskName="<new>"
$sourceDiskId="/subscriptions/<>/resourceGroups/<>/providers/Microsoft.Compute/disks/<>"
$diskConfig = New-AzDiskConfig -SourceResourceId $sourceDiskId -Location $region -CreateOption Copy
New-AzDisk -Disk $diskConfig -ResourceGroupName $targetRG -DiskName $targetDiskName
```
3. Enable SSE+CMK on the new copied disk.

Note: for full ADE → EAH migration the Upload+blob-copy path is required (see [`ADE-Migration-To-EAH`](#ade-migration-to-eah--migrate-from-ade-to-encryption-at-host-retirement-2028-09-15)). The Copy path above is specifically the one Engineering supports for SSE+CMK enablement.

---

## SSE-MSINotFound — CMK Storage Account `ManagedServiceIdentityNotFound` (MSI deleted)

**Error**:
```
ManagedServiceIdentityNotFound
Managed Service Identity (MSI) was not found for resource ''.
```

**Scope**: CMK Storage Account update fails because the associated managed identity (system-assigned or user-assigned) was deleted. Need to regenerate MI + re-grant KV perms.

### Investigation
```powershell
$subscriptionId    = "<sub>"
$resourceGroupName = "<rg>"
$accountName       = "<sa>"
Set-AzContext -Subscription $subscriptionId

# Get current principal ID
## System assigned
(Get-AzStorageAccount -ResourceGroupName $resourceGroupName -Name $accountName).Identity.PrincipalId
## User assigned
(Get-AzStorageAccount -ResourceGroupName $resourceGroupName -Name $accountName).Identity.UserAssignedIdentities.Values.PrincipalId

# Verify exists in Entra ID
Get-AzADServicePrincipal -ObjectId $principalId
# Expected error if deleted: "Resource '<>' does not exist..."
```

### Mitigation 1 — System-assigned identity regen
```powershell
# Re-generate MI
Set-AzStorageAccount -ResourceGroupName $rg -Name $acct -IdentityType None
Set-AzStorageAccount -ResourceGroupName $rg -Name $acct -IdentityType SystemAssigned

# Grant KV access (depending on KV access mode)
$principalId = (Get-AzStorageAccount -ResourceGroupName $rg -Name $acct).Identity.PrincipalId
$sa = Get-AzStorageAccount -ResourceGroupName $rg -Name $acct
$kvUri  = $sa.Encryption.KeyVaultProperties.KeyVaultUri
$kvName = $kvUri.Split("/")[-1].Split(".")[0]
$kvRgName = (Get-AzKeyVault -VaultName $kvName).ResourceGroupName

# Legacy access policy:
Set-AzKeyVaultAccessPolicy -VaultName $kvName -ObjectId $principalId -PermissionsToKeys wrapkey,unwrapkey,get

# RBAC:
New-AzRoleAssignment -RoleDefinitionName 'Key Vault Crypto Service Encryption User' `
    -ObjectId $principalId `
    -Scope /subscriptions/$subscriptionId/resourcegroups/$kvRgName/providers/Microsoft.KeyVault/vaults/$kvName
```

### Mitigation 2 — User-assigned identity regen
Same KV grant pattern, but recreate UAMI via `New-AzUserAssignedIdentity` and re-link CMK with `Set-AzStorageAccount -IdentityType UserAssigned -UserAssignedIdentityId $userId.Id -KeyVaultUri $kvUri -KeyName $keyName -KeyVaultUserAssignedIdentityId $userId.Id`.

### Edge case — CMK→MMK then config save fails
If SA once had CMK enabled, switched to MMK, but MI was deleted — even Firewall/VNet config save fails. Mitigation: set identityType to None.
```powershell
Set-AzStorageAccount -ResourceGroupName $rg -Name $acct -IdentityType None
```
