# Playbook L — Azure Files + Azure File Sync (AFS) — Deep

> **Routed from** [`playbook-L-azure-files-core.md`](./playbook-L-azure-files-core.md). ROUTER style — high-priority anchors with verbatim KQL where it exists, plus distilled TSG content. Foundation SA queries delegate to [`references/storage-account-queries.md`](../catalogs/storage-account-queries.md). AFS Jarvis queries inline.
>
> Scope: Azure Files + Azure File Sync (AFS) + Azure Files Identity. **NOT** XStore backend perf (→ K), **NOT** SA control plane (→ J), **NOT** managed disk (→ F), **NOT** Guest-OS deep TS (→ G).

[[_TOC_]]

## Cluster shortcuts

| Shorthand | Full path |
|---|---|
| `azcore.Xstore` | `cluster('azcore.kusto.windows.net').database('Xstore')` |
| `xstore.xstore` | `cluster('XStore').database('xstore')` |
| `KailaniSVC` (AFS Jarvis MDM namespace) | Geneva MDM: `Namespace=KailaniSVC` (Jarvis https://jarvis-west.dc.ad.msft.net/) |
| `Xstore` Files namespace (Jarvis MDM) | Geneva MDM: `Namespace=Xstore` events `XSMBPerfMetric / XNfsPerfMetric / FrontEndSummaryPerfLogs` |

## Reusable references
- [Azure Files Connectivity Troubleshooter — AzFileDiagnostics tool ([Win](https://github.com/Azure-Samples/azure-files-samples/tree/master/AzFileDiagnostics/Windows) / [Linux](https://github.com/Azure-Samples/azure-files-samples/tree/master/AzFileDiagnostics/Linux))]
- [Troubleshoot Azure Files connectivity issues (SMB)](https://learn.microsoft.com/en-us/troubleshoot/azure/azure-storage/files/connectivity/files-troubleshoot-smb-connectivity?tabs=windows)
- [Azure File Sync deployment guide](https://docs.microsoft.com/en-us/azure/storage/files/storage-sync-files-deployment-guide?tabs=portal)
- [Troubleshoot Azure File Sync](https://docs.microsoft.com/en-us/azure/storage/files/storage-sync-files-troubleshoot)
- [Azure File Sync release notes](https://docs.microsoft.com/en-us/azure/storage/files/storage-files-release-notes)
- [aka.ms/iridias](https://aka.ms/iridias) — Storage LSI / outage check (FIRST step for any sudden-breakage case)

---

## AF-Mount-Workflow — Azure Files Connectivity Workflow master entry-point (pre-flight checks DNS Port 445 AzFileDiagnostics Storage Account Firewall Security Settings Storage Logs FrontEndLogs IpAuthorizationError)

### Scope
Master TSG for SMB account-key-auth mount issues. Does NOT cover identity-based auth (→ Step 3) or NFS (→ § AF-Mount-NFS-Workflow).

### Data collection
1. SubscriptionId
2. SA name
3. File Share name
4. Timestamp (UTC)
5. VM name + source (Azure / on-prem / VPN / ExR)
6. Error message + mount command (verbatim)
7. **Recommended NET USE syntax from non-admin CMD** for best error code:
   ```
   NET USE * \\<sa>.file.core.windows.net\<share> /User:Azure\<sa> <key>
   ```
8. Screenshot

### Pre-flight (in order)
1. Validate FQDN format: `\\<sa>.file.core.windows.net\<share>`. NOT IP. If short name → DFS-N or Windows Share (engage Windows Networking T2).
2. DNS resolve to expected IP (public vs private endpoint)? If failing → DNS issue (customer side).
3. Network reach port 445:
   - Win: `Test-NetConnection <sa>.file.core.windows.net -Port 445`
   - Linux: `nc -zv <sa>.file.core.windows.net 445`

### If Network Reach **SUCCEEDS** → Security checks
- **SA Firewall**: even if test succeeds, firewall doesn't BLOCK reach — it adds auth check. Validate by temporarily setting Network Access = "All". If fixes → add caller IP / VNET to allow list, OR use private endpoint.
- **SA Security Settings** (Portal: File Service → File Shares → Security): with key auth, requires **NTLM v2** + **AES-128-GCM**. Set Profile to "Maximum compatibility" for TS, customer adjusts later.
- **From ASC** Summary tab → Files Configurations: `SMB Protocol / SMB Channel Encryption / Authentication Methods / Kerberos Ticket Encryption` (N/A = default Max Compat, not blocking).
- **Check Storage FrontEnd Logs** in ASC xDiagnostics → look for `IpAuthorizationError` for true source IP seen on backend (often differs from customer-expected due to NAT/topology).

### If Network Reach **FAILS** → Network checks
- **ISP blocks port 445** common on on-prem without VPN — use VPN or [SMB workarounds](https://learn.microsoft.com/en-us/troubleshoot/azure/azure-storage/files/connectivity/files-troubleshoot-smb-connectivity?tabs=windows#cause-1-port-445-is-blocked).
- VPN/Azure-to-Azure failure → middlebox (proxy / firewall on customer VNETs) → customer networking team.
- Last resort: collect network trace (next section).

### Network trace collection
- **Windows**: [SMBClientLogs script](https://github.com/Azure-Samples/azure-files-samples/tree/master/AzFileDiagnostics/Windows#how-to-run-the-smbclientlogs-script):
  ```powershell
  .\SmbClientLogs.ps1 -Start -CaptureNetwork
  # reproduce mount
  .\SmbClientLogs.ps1 -Stop
  # send zip to DTM
  ```
- **Linux**: [SMBDiagnostics](https://github.com/Azure-Samples/azure-files-samples/tree/master/SMBDiagnostics):
  ```bash
  yum install tcpdump   # or apt-get / dnf
  chmod +x ./smbclientlogs.sh
  ./smbclientlogs.sh start CaptureNetwork
  # reproduce mount
  ./smbclientlogs.sh stop
  # output.zip contains cifs_diag.txt + cifs_dmesg + cifs_trace + os_details + cifs_traffic.pcap
  ```

### Network team engagement
- Traffic over Azure VNET → engage **Networking** via *AzStorNet* AVA channel
- Traffic on-prem (no VPN/PE) → **Windows Networking T2**

### Special scenarios
- **Cannot create File Share** → validate SA kind: `Storage / StorageV2 / FileStorage` (NOT `BlobStorage`). If create from Portal works but other methods fail → client-side investigation.
- **Unable to resolve storage Endpoint — PartitionedDNS** → check if SA uses [Azure DNS Zone endpoint](https://supportability.visualstudio.com/AzureDev/_wiki/wikis/Dev_Storage/1832471/PartitionedDns-enabled-Storage-accounts-5000-storage-account-limit) (`myaccount.<zone>.<service>.storage.azure.net`). Customer must update app to use new endpoint format.

---

## AF-Mount-Win-53-67-87 — System error 53 / 67 / 87 / 123 or 0x80070035 (port 445 blocked / DNS failure / SMB version mismatch / Secure Transfer Required)

### Symptom
`System error 53 has occurred. The network path was not found.`
`System error 67 has occurred. The network name cannot be found.`
`System error 87 has occurred. The parameter is incorrect.`
`System error 123` (invalid filename / directory / volume label syntax).
`0x80070035` (PowerShell variant of error 53).

### Top causes (in order of frequency)
1. **Port 445 blocked** by ISP, customer firewall, NSG, or VNET routing
2. **DNS failure** — endpoint not resolving to expected IP
3. **SMB version mismatch** — client doesn't support SMB 3.x, SA requires Secure Transfer (SMB 3.x mandatory for cross-region or on-prem)
4. **Secure Transfer Required** enabled + client < SMB 3.x
5. **Old client OS without KB3114025** (Win 8.1 / WS 2012 R2)
6. **DNS short-name / DFS-N misconfiguration**

### Steps
1. Run [AzFileDiagnostics Windows](https://github.com/Azure-Samples/azure-files-samples/tree/master/AzFileDiagnostics/Windows) → captures OS version + SMB version + LmCompatibilityLevel + reach + firewall validation
2. Confirm `Test-NetConnection <sa>.file.core.windows.net -Port 445` succeeds
3. Check Secure Transfer setting on SA (Portal → Configuration → Secure transfer required). If ON + client < SMB 3.0, disable Secure Transfer for TS only, OR upgrade client.
4. Verify Get-SmbConnection / Get-SmbClientConfiguration → client SMB version

### Workarounds
- ISP-blocked 445 → VPN, or alternative port via [port workarounds](https://learn.microsoft.com/en-us/troubleshoot/azure/azure-storage/files/connectivity/files-troubleshoot-smb-connectivity?tabs=windows#cause-1-port-445-is-blocked)
- Win 8.1 / WS 2012 R2 → install KB3114025

---

## AF-Mount-Win-5 — System error 5 Access Denied during mount or map (Storage Account Firewall blocks the connection)

### Symptom
`System error 5 has occurred. Access is denied.` when running NET USE.

### Cause
**Storage Account Firewall (Public network access)** blocking the connection. Even with correct credentials, the firewall pre-empts the auth step.

### Resolution
1. Portal → SA → Networking → "Allow access from" set to "All networks" temporarily to confirm
2. Once confirmed → add customer's IP / VNET / Service Endpoint / Private Endpoint to allow list

Reference: [5 Mount Error_Storage wiki](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495034/5-Mount-Error_Storage?anchor=3.-storage-account-firewall).

---

## AF-Mount-Win-64 — System error 64 Network name no longer available (Secure Transfer Required / SMB 3 encryption)

### Symptom
`System error 64 has occurred. The specified network name is no longer available.`

### Cause
- Secure Transfer Required + client cannot negotiate SMB 3.x encryption
- Account stamp migration mid-mount (transient)
- Cross-region without SMB 3.x

### Resolution
- Verify client SMB 3.x capability (`Get-SmbClientConfiguration`)
- Upgrade Win 8.1 → install KB3114025
- Confirm SA Secure Transfer Required setting matches client capability

---

## AF-Mount-Win-1326-Key — System error 1326 with storage account key (credential typo / `Azure\` prefix missing in username)

### Symptom
`System error 1326 has occurred. The user name or password is incorrect.` when mounting with storage account key.

### Cause
- Typo in storage account key (copy-paste error including trailing whitespace)
- Username missing `Azure\` prefix — must be `/User:Azure\<sa>` not `/User:<sa>`
- Key rotated; client still using old key
- Storage Account Firewall blocking the request (rare — usually error 5)

### Resolution
- Recopy key from Portal → SA → Access keys (use key1 OR key2 directly, no quotes)
- Verify NET USE syntax: `NET USE * \\<sa>.file.core.windows.net\<share> /User:Azure\<sa> <key>`

---

## AF-Mount-Win-MultipleConn — Multiple connections to a server or shared resource by the same user (net use /y delete + clear saved creds)

### Symptom
`System error 1219 has occurred. Multiple connections to a server or shared resource by the same user, using more than one user name, are not allowed.`

### Cause
Windows allows only ONE credential per server endpoint per user session. If user already has a mount or saved credential, mounting again with different creds fails.

### Resolution
1. List existing connections: `net use`
2. Delete conflicting: `net use \\<sa>.file.core.windows.net /delete /yes`
3. Clear saved creds: `cmdkey /list` then `cmdkey /delete:<sa>.file.core.windows.net`
4. Reboot if still failing (locks may persist)
5. Re-mount

---

## AF-Mount-Win-DriveLetterMissing — Mount succeeds drive letter not visible (user context issue elevated vs non-elevated, use New-SmbGlobalMapping)

### Symptom
`NET USE * \\<sa>...` returns success, but no drive letter visible in File Explorer.

### Cause
- Mounted from **elevated** CMD/PowerShell — drive only available to elevated user context (UAC split). File Explorer runs non-elevated → can't see it.
- Mounted as different Windows user

### Resolution
- Mount from **non-elevated** CMD for File Explorer visibility
- For Win Server 2019+ globally accessible mount: use `New-SmbGlobalMapping`:
  ```powershell
  $cred = New-Object System.Management.Automation.PSCredential -ArgumentList "Azure\<sa>", (ConvertTo-SecureString -String "<key>" -AsPlainText -Force)
  New-SmbGlobalMapping -RemotePath "\\<sa>.file.core.windows.net\<share>" -Credential $cred -LocalPath "Y:" -Persistent $true
  ```

---

## AF-Mount-Win-NetUseUnknownOpt — Option is unknown when running Net Use (quote issues in command)

### Symptom
`The option /<X> is unknown.` from `net use`.

### Cause
- Special characters in storage account key (e.g., `/`, `=`, `+`) interpreted as options
- Missing or wrong quote handling
- Storage account key starts with `/` triggering false-positive option parse

### Resolution
Wrap key in double quotes, OR use `/SAVECRED` + cmdkey approach:
```cmd
NET USE * \\<sa>.file.core.windows.net\<share> /User:Azure\<sa> "<key>"
```

---

## AF-Mount-Win-NoEncryption — You are copying a file to a destination that does not support encryption (EFS not supported on Files)

### Symptom
Copy from local Windows file (with EFS encrypted attribute) to mapped Azure Files drive → `You are copying a file to a destination that does not support encryption`.

### Cause
**EFS (Encrypting File System)** is NOT supported on Azure Files. Azure Files has SSE (server-side encryption at rest) but not the user-key-encrypted file attribute model.

### Resolution
- Customer must decrypt files locally before copying, OR
- Skip EFS files in copy (use `robocopy /XA:E`)
- Use Azure Files SSE + customer-managed keys instead (different model)

---

## AF-Mount-Win-IIS-UNC — Unable to mount Azure File Share within IIS virtual directory (Application Pool identity needs mount)

### Symptom
IIS app served from Azure Files UNC virtual directory returns access errors or fails to start.

### Cause
IIS App Pool runs as `ApplicationPoolIdentity` or other user — that user has no mount/credentials to the Azure Files share. Mount visibility is per-user context.

### Resolution
- Use `New-SmbGlobalMapping` to make share globally available system-wide
- OR set IIS App Pool identity to specific user, then mount the share for that user account
- OR store creds in Windows Credential Manager for the App Pool identity user

---

## AF-Mount-Win-MSI-UNC — Unable to run MSI installer using UNC path (msiexec needs network provider or mapped drive)

### Symptom
`msiexec /i \\<sa>.file.core.windows.net\<share>\installer.msi` fails.

### Cause
MSI installer requires the path to be accessible as a local drive or via Network Provider — Azure Files UNC may not be resolved correctly when invoked from non-mounted context.

### Resolution
- Map drive first, install via mapped letter: `net use Z: \\... && msiexec /i Z:\installer.msi`
- Copy MSI locally first

---

## AF-Mount-Win-BadOption-524 — Azure FileShare Mount Issue Bad Option or Unknown Error 524 (SMB version or options not supported)

### Symptom
`mount error: bad option` or `Unknown error 524`.

### Cause
- Mount options syntax error
- SMB version unsupported on client kernel
- `vers=` option set to unsupported version

### Resolution
- Check mount syntax for typos
- Specify supported version: `vers=3.0` (or `vers=2.1` for older clients)
- Update kernel / CIFS utils if old

---

## AF-Mount-Win-ForwardSlash — Cannot Map Drive Storage Account Forward Slash (Net Use syntax uses backslash not forward slash)

### Symptom
Customer uses `NET USE * //sa.file.core.windows.net/share` → fails.

### Cause
Windows NET USE requires **backslash** path syntax (`\\` not `//`).

### Resolution
Use UNC format with backslashes: `\\<sa>.file.core.windows.net\<share>`.

---

## AF-Mount-Win-NetworkPathNotFound — Mount error Network path was not found on Windows (Port 445 blocked / DNS resolution failed / VNET routing)

### Symptom
`The network path was not found.` (error 0x80070035 wrapper)

### Causes
Same as § AF-Mount-Win-53-67-87 — port 445, DNS, routing.

### Steps
Run AzFileDiagnostics + DNS + reach test as in § AF-Mount-Workflow.

---

## AF-Mount-Win-OverReboot — Unable to connect to Azure Files Over Reboot (credentials not persisted / need cmdkey or Credential Manager persistence)

### Symptom
Mount works initially; after Windows reboot, mount disappears or fails.

### Cause
- NET USE without `/persistent:yes`
- Credential not saved in Credential Manager
- Drive letter mapping not persisted

### Resolution
```powershell
# Save credential persistently
cmdkey /add:<sa>.file.core.windows.net /user:Azure\<sa> /pass:<key>
# Then persistent mount
net use Z: \\<sa>.file.core.windows.net\<share> /persistent:yes
```

Or use `New-SmbGlobalMapping -Persistent $true`.

---

## AF-Mount-Win-RandomClose — Azure File Share Mount Issue Randomly Closing (SMB idle timeout on firewall / load balancer / client keepalive)

### Symptom
Mount is up, but connections randomly drop / shares become inaccessible until remount.

### Cause
- Idle SMB connection killed by client-side firewall or middlebox
- Network path through a stateful firewall with low session idle timeout
- Client `SMB SessionTimeout` registry too low

### Resolution
- Increase `SessionTimeout` registry: `HKLM\System\CurrentControlSet\Services\LanmanWorkstation\Parameters\SessTimeout` (DWORD, default 60s, increase to 300+)
- Configure firewall to allow longer idle SMB sessions
- Implement keepalive via scheduled task touching the share

---

## AF-Mount-Win-StampMigration — Losing mount after stamp migration (customer must remount after platform stamp move)

### Symptom
Customer's mount stops working after platform-side stamp migration completes (rare; transparent normally).

### Cause
Some clients don't gracefully re-handle the redirect to new stamp endpoint.

### Resolution
Customer remounts the share. If recurring → check `WatchAddress` registry, network trace for redirect handling.

---

## AF-Mount-Linux-11 — Mount error(11) Resource temporarily unavailable (Ubuntu 16.10 kernel claims SMB3 encryption but doesn't support — use vers=2.1 as workaround)

### Symptom
`mount error(11): Resource temporarily unavailable` on Linux mount.

### Cause
Known **Ubuntu 16.10 kernel v4.8** bug — client claims SMB 3.0 encryption support but doesn't actually support it.

### Resolution
- Upgrade to Ubuntu 16.04 (LTS) or 18.04+
- OR use `vers=2.1` mount option:
  ```bash
  sudo mount -t cifs //<sa>.file.core.windows.net/<share> <mount-point> \
    -o vers=2.1,username=<sa>,password=<key>,dir_mode=0777,file_mode=0777,serverino
  ```
- Note: vers=2.1 doesn't support Secure Transfer Required — must be disabled on SA, OR use vers=3.0 from fixed kernel

---

## AF-Mount-Linux-13 — Mount error(13) Permission denied (port 445 blocked / SMB encryption mismatch / firewall / Secure Transfer Required / credentials wrong)

### Symptom
`mount error(13): Permission denied`.

### Top causes (in order)
1. **Storage Account Firewall** blocking client IP
2. **Secure Transfer Required** + client < SMB 3.x without encryption
3. Wrong credentials (verify Azure portal key)
4. Username format wrong (need plain `<sa>` not `Azure\<sa>` on Linux)
5. Port 445 blocked by ISP/firewall

### Investigation
1. Test reach: `nc -zv <sa>.file.core.windows.net 445`
2. AzFileDiagnostics Linux
3. Verify CIFS supports encryption: `modinfo cifs | grep encrypt`
4. Test with `vers=3.0,sec=ntlmssp` mount options
5. Check `dmesg | tail` for kernel error detail

### Resolution
- Whitelist client IP in SA Firewall
- Upgrade CIFS utils or kernel for SMB 3.x
- Disable Secure Transfer Required on SA for legacy clients
- Correct credentials syntax

---

## AF-Mount-Linux-115 — Mount error(115) Operation now in progress or Unknown error / Could not resolve address (DNS resolution failed / check storage endpoint)

### Symptom
`mount error(115): Operation now in progress` OR `mount error: could not resolve address <sa>:Unknown error`.

### Cause
- DNS failure to resolve `<sa>.file.core.windows.net`
- Mount syntax typo in SA name
- Private endpoint configured but DNS not pointing to PE IP

### Resolution
- Verify SA name spelling
- `nslookup <sa>.file.core.windows.net` — confirm resolution
- For private endpoint: check `/etc/resolv.conf` + private DNS zone
- Cross-link `Mount Error 115 Linux_Storage` wiki

---

## AF-Mount-Linux-2 — Mount error(2) No such file or directory (share doesn't exist or typo / SMB version not supported)

### Symptom
`mount error(2): No such file or directory`.

### Cause
- Share doesn't exist (typo)
- SMB version on client doesn't support the share configuration
- Mount path typo (wrong slash direction, etc.)

### Resolution
- Verify share exists in Portal → SA → File shares
- Verify mount path: `/<share>` (lowercase, exact)
- Try with `vers=3.0` explicit option

---

## AF-Mount-Linux-Generic — Errors mounting Azure Files share on Linux (umbrella — AzFileDiagnosticsLinux script + SMBDiagnostics tcpdump cifs_trace/cifs_diag/cifs_dmesg trace bundle)

### Catch-all for other Linux mount errors
1. Run [AzFileDiagnostics Linux](https://github.com/Azure-Samples/azure-files-samples/tree/master/AzFileDiagnostics/Linux)
2. Verify: distro version, CIFS utils installed, SMB 2.1+ support, encryption support if SMB3
3. Test port 445 reach, check iptables
4. Collect SMB diag bundle (output.zip):
   - `cifs_diag.txt` — internal SMB client debug data
   - `cifs_dmesg` — kernel logs since reboot
   - `cifs_trace` — kernel event logs
   - `os_details.txt` — distro info
   - `cifs_traffic.pcap` — network capture
5. If unresolved → engage **Linux SME Team** via [wiki link](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/494925)

---

## AF-Mount-MacOS — Azure File Share mount issues on Mac OS / Cannot mount no route to host (SMB version or port 445 blocked)

### Symptom
MacOS Finder: `There was a problem connecting to the server` or terminal: `no route to host`.

### Cause
- Port 445 blocked by ISP (very common for on-prem Mac)
- MacOS SMB version mismatch (10.13+ supports SMB 3, older don't)
- DNS / hosts file misconfiguration

### Resolution
- Test reach: `nc -zv <sa>.file.core.windows.net 445`
- Mount syntax:
  ```bash
  open -g smb://<sa>.file.core.windows.net/<share>
  ```
  or via Finder → Go → Connect to Server → `smb://<sa>.file.core.windows.net/<share>`, username `<sa>`, password = key
- VPN required if 445 blocked

---

## AF-Mount-NFS-Workflow — NFS v4 for Azure Files master workflow (Premium only, private endpoint required, no Azure Files ZRS for NFS, mount syntax, fstab entry, Secure Transport encryption in transit)

### Prereqs (NFS v4.1 on Azure Files)
- **Premium FileStorage SA kind** ONLY
- **LRS** redundancy (no ZRS / GRS for NFS)
- **Private Endpoint required** (NFS doesn't support public endpoint)
- VNET configured to route to private endpoint
- Linux client with NFS v4.1 support (RHEL 7.5+, Ubuntu 18.04+, etc.)
- Set up private DNS zone for `privatelink.file.core.windows.net`

### Mount syntax
```bash
sudo mount -t nfs <sa>.file.core.windows.net:/<sa>/<share> /mnt/<share> -o vers=4,minorversion=1,sec=sys
```

### fstab entry (auto-mount on boot)
```
<sa>.file.core.windows.net:/<sa>/<share>  /mnt/<share>  nfs  vers=4,minorversion=1,sec=sys  0  0
```

### Encryption in Transit (Preview)
- Currently NFS v4.1 over the wire is NOT encrypted by default
- Customer enables **Secure Transport for NFS** via [Encryption in Transit feature](https://learn.microsoft.com/en-us/azure/storage/files/encryption-in-transit-for-nfs-shares) — uses `aznfs` mount helper + stunnel
- → see § AF-EncryptionInTransit-NFS-Overview

### TS common issues
- "No route to host" → VNET routing / private endpoint missing
- "Permission denied" → root mount required, then chown for non-root access (default `no_root_squash`)
- "Stale file handle" → client cache out of sync, remount

---

## AF-Mount-NFS-Reclaim10019 — Cannot access or mount NFS nfs4 reclaim open state error=10019 (client ID already exists, need reboot client or restart rpcbind)

### Symptom
`nfs4 reclaim of open state for file <X> failed with error=10019` after client reboot or network blip.

### Cause
NFS client ID held by server from previous session, but server hasn't expired it yet. Client re-mount attempts to reclaim same ID and fails.

### Resolution
- Wait ~5 min (lease expiry on server side)
- Restart rpcbind: `systemctl restart rpcbind`
- Reboot client
- Use unique mount client ID per client

---

## AF-Mount-NFS-Perms — Permission Issues NFS 4.1 (default uid/gid mapping / chown required after mount vs default no_root_squash)

### Symptom
After mount, non-root user can't access files. Or files owned by `nobody:nobody`.

### Cause
- NFS Azure Files uses **no_root_squash** by default — root can read/write
- For non-root access, customer must chmod/chown after mount
- ID mapping issue if customer uses Kerberos NFS (sec=krb5)

### Resolution
- After mount as root: `chown -R <user>:<group> /mnt/<share>` and `chmod 0777 /mnt/<share>` (or appropriate)
- For Kerberos NFS → ensure idmapd config matches

---

## AF-Mount-NFS-NotSupported — NfsFileShares is Not Supported for the Account (non-Premium SA / non-FileStorage kind / region not supported)

### Symptom
Creating NFS share fails: `NfsFileShares is not supported for the storage account`.

### Cause
- SA is not `FileStorage` kind (must be Premium FileStorage)
- Region doesn't support NFS yet
- SA is GRS/GZRS (NFS only LRS or ZRS)

### Resolution
- Create new FileStorage SA in NFS-supported region (LRS or ZRS only)
- Migrate data if needed

---

## AF-Mount-NFS-SuSE — NFS Not Working on SuSE (distro-specific config / missing nfs-utils / firewalld rules)

### Symptom
NFS mount fails on SUSE Enterprise Linux specifically.

### Cause
- nfs-utils package not installed
- firewalld blocking NFS ports
- AppArmor blocking nfs-client

### Resolution
- Install: `zypper install nfs-utils nfs-client`
- Configure firewalld: `firewall-cmd --add-service=nfs --permanent && firewall-cmd --reload`
- Disable or configure AppArmor profile for nfs-client

---

## AF-Mount-NFS-RHEL-dfh — Incorrect storage account names in df -h output for NFS shares on RHEL after reboot (systemd mount resolution edge case)

### Symptom
After RHEL reboot, `df -h` shows wrong SA name for NFS-mounted share, OR shows `(error)` for the mount point.

### Cause
systemd mount unit resolves DNS at boot when network may not be fully up — gets cached/wrong result.

### Resolution
- Add `_netdev,x-systemd.requires=network-online.target` to fstab options
- Or use a systemd mount unit with `After=network-online.target`

---

## AF-Mount-NFS-fpsync — Troubleshooting fpsync issues (parallel rsync tool for fast NFS copy, permission / stale handle / memory exhaustion edge cases)

### Symptom
`fpsync` (parallel rsync wrapper) on Azure Files NFS fails with stale handle / OOM / partial sync.

### Resolution
- Reduce parallel workers (`-n` arg) for SA throttling
- Pre-allocate dest tree (mkdir -p) to avoid concurrent mkdir races
- Increase client memory if OOM
- For ARM clients use `fpart` with manual rsync invocation

---

## AF-Identity-AADKerb-Hybrid-Flow — Master troubleshooting flow for Entra Kerberos hybrid identities (7-step prereq check, feature registration, Azure AD Kerberos, storage acct config, RBAC, disable clipping, Fiddler trace)

### Scope
Master flow for **Microsoft Entra Kerberos** (formerly AAD Kerberos) on **hybrid identities** (synced from on-prem AD to AAD via AAD Connect). Cloud-only identities use § AF-Identity-EntraOnly-* instead.

### 7-step prerequisite check
1. **Feature registration**: `Get-AzProviderFeature -ProviderNamespace Microsoft.Storage -FeatureName AADKerb` must be `Registered`
2. **Azure AD Kerberos enabled on SA**: Portal → SA → File shares → Active Directory → "Microsoft Entra Kerberos" tab → Set up
3. **Storage account configured**: AD Domain Name + AD Domain GUID populated (from `Set-AzStorageAccount -EnableAzureActiveDirectoryKerberosForFile`)
4. **API permissions on App Reg**: `OpenID` + `profile` + `User.Read` admin-consented for the Storage app reg
5. **Client AAD-joined or Hybrid AAD-joined** (not workgroup, not domain-only)
6. **RBAC role assigned at share-scope**: `Storage File Data SMB Share Reader / Contributor / Elevated Contributor` to user
7. **Client TGT loaded**: `klist get` must return tickets from `kerberos.microsoftonline.com`

### Decision tree on error
- Mount succeeds, files inaccessible → § AF-Identity-AADKerb-5 (RBAC)
- Specified network password incorrect → § AF-Identity-AADKerb-86
- Account name incorrect → § AF-Identity-AADKerb-1396
- Hybrid sync issue → § AF-Identity-ADDS-VerifyADSync
- Klist error 0x80090303 → § AF-Identity-AADKerb-Klist0x80090303
- AVD/FSLogix → § AF-Identity-AADKerb-AVD-FSLogix

### Diagnostic data collection
- klist purge + retry: `klist purge; net use ...`
- Fiddler trace (capture HTTPS calls to `login.microsoftonline.com` and `kerberos.microsoftonline.com`)
- Use [Debug-AzStorageAccountAuth script](https://github.com/Azure-Samples/azure-files-samples) for end-to-end check

---

## AF-Identity-AADKerb-86 — Error 86 The specified network password is not correct (AAD Kerb cached Kerberos ticket stale / klist purge + re-run mount)

### Symptom
On hybrid-joined client, mount returns `System error 86 has occurred. The specified network password is not correct.`

### Cause
- Cached Kerberos TGT from previous session is stale
- User account password recently changed; TGT not refreshed
- AAD Kerb policy not yet propagated to client

### Resolution
```cmd
klist purge
klist get krbtgt
net use Z: \\<sa>.file.core.windows.net\<share>
```

If still failing, restart client OR sign out/in to refresh AAD identity.

---

## AF-Identity-AADKerb-1326 — Error 1326 Mount Error (AAD Kerb user not synced to AAD / policy blocking Windows Hello PIN)

### Symptom
`System error 1326. The user name or password is incorrect.` on AAD Kerb mount.

### Cause
- User account exists in on-prem AD but not synced to AAD (no AAD object)
- Policy disabling Windows Hello PIN → client can't acquire AAD token
- AAD Connect sync stale / broken

### Resolution
- Verify user synced: `Get-AzureADUser -ObjectId <userPrincipalName>` should return object
- Force AAD Connect delta sync
- Verify Windows Hello PIN works on client (logoff/logon test)

---

## AF-Identity-AADKerb-1396 — Error 1396 Target account name incorrect (SPN not registered / Storage acct not AAD Kerb enabled / wrong SPN)

### Symptom
`System error 1396. The target account name is incorrect.`

### Cause
- SPN `cifs/<sa>.file.core.windows.net` not registered for SA's AAD Kerb identity
- AAD Kerberos was not properly enabled on SA
- Wrong SPN format used in mount

### Resolution
- Verify AAD Kerb enabled on SA (Portal → File shares → Active Directory → Microsoft Entra Kerberos)
- Re-run `Set-AzStorageAccount -EnableAzureActiveDirectoryKerberosForFile`
- Validate SPN: `setspn -Q cifs/<sa>.file.core.windows.net` (from domain-joined client)

---

## AF-Identity-AADKerb-5 — Error 5 Access Denied (share- and file-level RBAC permissions check Storage File Data SMB Share Reader vs Contributor vs Elevated Contributor)

### Symptom
Mount succeeds but file/folder access returns `Access is denied`.

### Cause
**Share-level RBAC** missing or wrong role.

### Required RBAC roles (assigned at SA / Share scope)
| Role | What it grants |
|---|---|
| `Storage File Data SMB Share Reader` | Read files/folders |
| `Storage File Data SMB Share Contributor` | Read + write + delete |
| `Storage File Data SMB Share Elevated Contributor` | All Contributor + manage NTFS ACLs |

### Resolution
- Portal → SA → Access Control (IAM) → Add role assignment → choose role → user/group
- Wait 5-10 min for propagation
- Klist purge on client + re-mount

NTFS ACLs are a separate layer (after share RBAC grants access).

---

## AF-Identity-AADKerb-Klist0x80090303 — Klist Failed With 0x80090303 (specified target is unknown or unreachable, Azure AD Kerberos realm or SPN not registered / no Internet, no AAD reach)

### Symptom
`klist` or mount returns `0x80090303 The specified target is unknown or unreachable`.

### Cause
- Client cannot reach `kerberos.microsoftonline.com` (no Internet, blocked by firewall/proxy)
- Azure AD Kerberos realm not registered in client OS (older clients)
- SPN missing from AAD app reg for SA

### Resolution
- Test: `Test-NetConnection kerberos.microsoftonline.com -Port 443`
- Configure proxy to allow `kerberos.microsoftonline.com`, `login.microsoftonline.com`
- Verify SPN registered (§ AF-Identity-AADKerb-1396)
- For older Win10 (<1809): may need feature update

---

## AF-Identity-AADKerb-JoinGraphBadRequest — Microsoft Entra Kerberos Join Graph BadRequest (AzureAD Kerberos domain join step failing, Azure Policy / Graph API permission issue)

### Symptom
During AAD Kerb enablement on SA: Graph API returns BadRequest when registering SA as AAD Kerb computer object.

### Cause
- Caller (admin running `Set-AzStorageAccount`) missing Graph API permissions
- Azure Policy blocking AAD object creation
- SA already enrolled and conflict

### Resolution
- Verify caller has `Microsoft.Storage/storageAccounts/write` + Graph API `Application.ReadWrite.All` or admin consent
- Check Azure Policy assignments for AAD object creation restrictions
- If retrying: first disable AAD Kerb, then re-enable

---

## AF-Identity-AADKerb-StorageTokenFail — Microsoft Entra Kerberos authentication Unable to Retrieve Storage Token (trust relationship failing / client not AAD joined / token acquisition blocked)

### Symptom
Client attempts mount with AAD Kerb → `Unable to retrieve storage token` error.

### Cause
- Client is workgroup/domain-only (not AAD-joined or AAD-hybrid-joined)
- TPM issue prevents Windows Hello / WAM token acquisition
- Conditional Access policy blocking token request

### Resolution
- Verify client device: `dsregcmd /status` — must show `AzureAdJoined : YES` or `DomainJoined : YES AzureAdJoined : YES`
- Check Conditional Access logs in AAD for blocked sign-ins
- Reset TPM if hardware issue

---

## AF-Identity-AADKerb-Multiforest — ADAuth Files Multiforest (user in different forest than SA / add suffix routing / add trust relationship)

### Symptom
User from Forest A trying to access SA registered to Forest B fails with auth errors.

### Cause
- No suffix routing for the user's domain
- No trust relationship between forests
- AAD Kerb expects user UPN to match SA forest

### Resolution
- Configure suffix routing on the trust (Active Directory Domains and Trusts → Trust → Properties)
- Or migrate users to SA's forest
- Reference: [ADAuth Files Multiforest_Storage](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495037)

---

## AF-Identity-AADKerb-AVD-FSLogix — Azure Files AAD Kerb with AVD and FSLogix support boundaries (FSLogix profile on AAD Kerb share supported configurations)

### Scope
Define support boundaries for using AAD Kerb-authenticated Azure Files as the backing store for **FSLogix profile containers** in **Azure Virtual Desktop (AVD)** sessions.

### Supported configurations
- **AAD-joined session hosts** + AAD Kerb on SA + FSLogix profile container on AAD Kerb share = SUPPORTED
- **Hybrid AAD-joined session hosts** + AAD Kerb + FSLogix = SUPPORTED with hybrid identity
- **AD DS-only joined session hosts** + AAD Kerb = NOT a valid scenario (use AD DS auth instead)

### Required RBAC on share
- `Storage File Data SMB Share Contributor` to user (or group containing user)
- NTFS ACLs configured for user's profile path

### Common issues
- FSLogix logs show "Access Denied" → check RBAC + NTFS ACL chain
- Profile load slow → cross-link K § SA-Perf-AzureFiles-Backend

---

## AF-Identity-AADKerb-PromptedCreds — User Prompted for Credentials Repeatedly (cached creds stale / single sign-on not configured / client not AAD joined)

### Symptom
On AAD Kerb mount attempt, user is repeatedly prompted for credentials.

### Cause
- Single sign-on not configured (client not AAD-joined)
- Stale cached creds in Windows Credential Manager
- AAD MFA required + client can't complete interactive flow

### Resolution
- Verify AAD-joined state (`dsregcmd /status`)
- Clear Credential Manager entries for the SA
- Check Conditional Access — if MFA required for AAD Kerb, client must complete browser sign-in first

---

## AF-Identity-ADDS-ShortName — Mount with short name / DFS-I vs FQDN (SPN considerations when using friendly names)

### Symptom
Mount via `\\shortname\share` fails or returns unexpected auth errors.

### Cause
SPN registered for FQDN; short name lookup uses NTLM fallback or wrong SPN.

### Resolution
- Use FQDN: `\\<sa>.file.core.windows.net\<share>`
- For DFS-N: confirm DFS namespace properly configured
- For shortname mount: register SPN for short name OR use DNS CNAME

---

## AF-Identity-ADDS-1219 — 1219 Mount Error (multiple sessions with same server using different credentials / credential conflict)

### Symptom
`System error 1219` on AD DS mount.

### Same as § AF-Mount-Win-MultipleConn but in AD DS auth context
Same resolution: `net use /delete` existing connections, `cmdkey /delete` saved creds.

---

## AF-Identity-ADDS-64 — 64 Mount Error AD DS context (stale SPN / computer object deleted / Secure Transfer Required SMB3)

### Symptom
`System error 64. The specified network name is no longer available.` in AD DS context.

### Cause
- Storage account's AD computer object stale / deleted
- SPN broken
- Secure Transfer + client SMB < 3.x

### Resolution
- Verify computer object: `Get-ADComputer <SA-CompObjName>` (from domain-joined client)
- Re-run `Join-AzStorageAccount` if computer object missing
- Verify SMB version

---

## AF-Identity-ADDS-PasswordError — Specified Network Password is not Correct - AD DS context (Kerberos ticket acquisition failing / AD trust broken / SPN mismatch)

### Symptom
`System error 86. The specified network password is not correct.` on AD DS mount.

### Cause
- User's Kerberos TGT can't acquire ticket for the SA SPN
- AD trust between user's domain and SA's domain broken
- SPN mismatch

### Resolution
- `klist purge` + `klist get cifs/<sa>.file.core.windows.net`
- Validate trust: `nltest /sc_query:<sa-domain>`
- Verify SPN: `setspn -L <SA-CompObjName>`
- Reset SA's AD password via AzFilesHybrid module

---

## AF-Identity-ADDS-AccountDisabled — Kerberos error STATUS_ACCOUNT_DISABLED (storage acct computer object in AD disabled / user account disabled in AD)

### Symptom
Network trace shows Kerberos response: `KDC_ERR_CLIENT_REVOKED` or status `STATUS_ACCOUNT_DISABLED`.

### Cause
- SA's computer object in AD is disabled (admin disabled, GPO, etc.)
- User account in AD disabled

### Resolution
- Enable SA computer object in ADUC
- Enable user account
- Verify with `Get-ADComputer <name> -Properties Enabled`

---

## AF-Identity-ADDS-CachedCreds — Cached Credentials cause mount failure (cmdkey deletes or Credential Manager cleanup)

Symptoms + resolution same as § AF-Mount-Win-MultipleConn + AAD Kerb 86, but in AD DS context.

---

## AF-Identity-ADDS-CannotBind — Cannot Bind Positional Parameters (AzFilesHybrid PowerShell module version mismatch / cmdlet param changed between versions)

### Symptom
`Cannot bind positional parameter because no parameters that take pipeline input were found` from AzFilesHybrid cmdlets.

### Cause
Module version mismatch — using older syntax with newer module OR vice versa.

### Resolution
- Update AzFilesHybrid: `Install-Module AzFilesHybrid -Force`
- Use named parameters explicitly (not positional)
- Check release notes for cmdlet param changes

---

## AF-Identity-ADDS-CannotTakeOwnership — Cannot take ownership of file on Azure Files AD DS (share permission model difference / super user not Domain Admin on Azure Files)

### Symptom
Admin can't take ownership of file: `Access is denied`.

### Cause
Azure Files AD DS has different super-user semantics — "Domain Admins" group does NOT have automatic ownership rights. Only `Storage File Data SMB Share Elevated Contributor` role grants NTFS ACL management.

### Resolution
- Assign `Storage File Data SMB Share Elevated Contributor` to admin user
- Wait 5-10 min for propagation
- Re-mount + try ownership take

---

## AF-Identity-ADDS-DomainNotPopulate — Domain does not populate in output of AzFilesHybrid PowerShell module (storage acct not domain-joined / missing rights)

### Symptom
`(Get-AzStorageAccount).AzureFilesIdentityBasedAuth.ActiveDirectoryProperties.DomainName` returns empty.

### Cause
SA not properly joined to AD DS, OR caller lacks rights to read the property.

### Resolution
- Re-run `Join-AzStorageAccount`
- Verify caller has Reader role on SA
- Check AzFilesHybrid log for join errors

---

## AF-Identity-ADDS-FailedToEnumerate — Failed to enumerate files or folders (share-level RBAC grants mount but not list / NTFS ACL deny / access-based enumeration)

### Symptom
Mount succeeds, `dir` returns no files (or "Access denied"), but user can navigate to known full paths.

### Cause
- Share-level RBAC missing or wrong (Read role needed for list)
- NTFS ACL with explicit Deny on list/traverse
- Access-Based Enumeration filtering out folders user can't access

### Resolution
- Verify `Storage File Data SMB Share Reader` (minimum) on share
- Check NTFS ACL on root folder: `Get-Acl Z:\` (mounted path)
- Disable ABE if used / verify user has list perms

---

## AF-Identity-ADDS-FSLogix — FSLogix profile container on Azure Files AD DS (permission model requirements / share RBAC + NTFS ACL + SMB options)

### Required setup
1. Share-level RBAC: `Storage File Data SMB Share Elevated Contributor` to FSLogix users group
2. NTFS ACL on `\Profiles` folder:
   - `CREATOR OWNER` = Full Control (Subfolders + files only)
   - `Users` (or FSLogix users) = Modify (This folder only)
   - `SYSTEM + Administrators` = Full Control (all)
3. FSLogix config: `VHDLocations` set to UNC path of share

### Common issues
- Profile load slow → cross-link K § SA-Perf-AzureFiles-Backend + § SA-Perf-AzureFiles-HeavyMetadata
- "Profile cannot be loaded" → check NTFS ACL `CREATOR OWNER`
- Profile orphaned → user's SID changed (recreate ACL)

---

## AF-Identity-ADDS-JoinErrors — AD join errors / New-ADComputer failure when running Join-AzStorageAccount (permission / OU path / AD replication issues)

### Common errors during Join-AzStorageAccount
1. **`New-ADComputer: Access is denied`** → caller lacks `Create Computer Objects` right on target OU
2. **`Cannot find specified OU`** → invalid `-OrganizationalUnitDistinguishedName` value
3. **`Replication issue`** → object created on one DC, query went to another → wait for AD replication
4. **`Object already exists`** → previous failed attempt left ghost computer object, delete it first

### Resolution
- Grant caller `Create Computer Objects` + `Read All Properties` on target OU
- Verify OU DN format: `OU=AzureStorage,DC=contoso,DC=com`
- Wait 15 min for replication or force: `repadmin /syncall`
- Delete ghost object in ADUC before retry

---

## AF-Identity-ADDS-ModuleInstall — Module install error for AzFilesHybrid (execution policy / missing prereqs / Internet blocked)

### Common errors
- `Execution of scripts is disabled` → `Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope CurrentUser`
- `Cannot install` from PSGallery → set `Install-PackageProvider NuGet -Force; Set-PSRepository PSGallery -InstallationPolicy Trusted`
- Missing modules `Az.Storage`, `Az.Accounts`, `ActiveDirectory` → install them first
- No internet → use offline copy from a separate machine

---

## AF-Identity-ADDS-Permissions — Permissions issue when managing or accessing shares (3-layer permission model share RBAC + NTFS ACL + SMB options)

### 3-layer permission model
1. **Storage Account level** (Azure RBAC): `Reader / Contributor / Owner` for management plane access
2. **Share level** (Storage RBAC): `Storage File Data SMB Share Reader / Contributor / Elevated Contributor` for data plane
3. **NTFS ACL** (file/folder level): standard Windows ACL inside the share

All three layers must pass for full access.

### Common matrix
- Customer can mount but can't read files → Share RBAC `Reader` missing
- Mount + read, can't write → Share RBAC `Contributor` missing
- All works but can't change ACL → Share RBAC `Elevated Contributor` missing

---

## AF-Identity-ADDS-RobocopyLimits — RoboCopy limitations on Azure Files AD DS (large FS, ACL may not copy / owner may not preserve / use /MT and /COPYALL)

### Known limits
- `/COPYALL` (incl. ACL) may fail if caller lacks `Elevated Contributor`
- Owner preservation requires `SeRestorePrivilege`/`Elevated Contributor`
- Very long paths (> 256 chars) may fail
- Multithreaded (`/MT:32`+) may hit SA scalability targets (1000 IOPS / 60 MB/s)

### Best practices
- Use `/MT:8` or `/MT:16` (not too many threads)
- Use `/COPYALL /B /R:3 /W:5 /LOG+:robocopy.log`
- For very large datasets → Azure Data Box or AzCopy with snapshot

---

## AF-Identity-ADDS-Err86-Win7 — System Error 86 on Windows 7 or 2008 R2 (SMB encryption not supported / Secure Transfer Required mismatch)

### Cause
Win 7 / Server 2008 R2 doesn't support SMB 3.x encryption, but SA Secure Transfer Required is enabled.

### Resolution
- Disable Secure Transfer on SA (security tradeoff)
- OR upgrade client to Win 8.1+/WS 2012 R2+ with KB3114025
- OR use a Windows Server 2016+ jumpbox to proxy access

---

## AF-Identity-ADDS-RIDAllocation — Unable to allocate Relative Identifier (RID master FSMO not available / RID pool exhausted on storage acct creation)

### Symptom
`New-ADComputer` for SA fails: `The directory service was unable to allocate a relative identifier`.

### Cause
- RID Master FSMO down or unreachable
- RID pool exhausted on the DC

### Resolution
- Verify RID Master FSMO accessible: `netdom query fsmo`
- Check RID pool status: `dcdiag /test:ridmanager /v`
- Have AD admin extend RID pool or seize FSMO if needed

---

## AF-Identity-ADDS-ADWebServices — Unable to contact Active Directory Web Services (ADWS service down / firewall / missing on DC)

### Symptom
AzFilesHybrid module: `Unable to find a default server with Active Directory Web Services running`.

### Cause
- ADWS service stopped on DC
- ADWS port (9389) blocked
- DC running pre-Server 2008 R2 (ADWS introduced then)

### Resolution
- Start ADWS service: `Get-Service ADWS | Start-Service`
- Allow port 9389 in firewall
- Upgrade DC to 2008 R2+

---

## AF-Identity-ADDS-VerifyADSync — Verify on-prem AD user synced to AAD (AAD Connect sync status / user AAD ObjectId match / Foreign Security Principal FSP required for AAD Kerb)

### Steps
1. On-prem: `Get-ADUser <user>` → note `ObjectGUID`
2. Cloud: `Get-AzureADUser -ObjectId <UPN>` → verify object exists with matching `OnPremisesSecurityIdentifier`
3. For AAD Kerb: verify Foreign Security Principal exists for the user in SA's AAD

### Resolution
- Force AAD Connect sync: `Start-ADSyncSyncCycle -PolicyType Delta`
- If user filtered out by AAD Connect → adjust sync rules
- If FSP missing → reset AAD Kerb on SA

---

## AF-Identity-ADDS-AccessDenied-NTFS — Access Denied while trying to update File Share NTFS permission (share RBAC grants mount but not ACL management / need Storage File Data SMB Share Elevated Contributor)

### Symptom
`icacls Z:\folder /grant <user>:F` returns `Access is denied`.

### Cause
Caller has `Contributor` role on share — that grants R/W but NOT ACL management. ACL management requires `Elevated Contributor`.

### Resolution
- Assign `Storage File Data SMB Share Elevated Contributor` to caller
- Wait 5-10 min, klist purge, remount, retry

---

## AF-Identity-EntraOnly-Mount — How to mount Azure Files SMB with Entra Only Kerberos (cloud-only AAD-joined or hybrid-joined, no on-prem AD required, AAD Kerb enable + RBAC + mount)

### Scope
For **cloud-only environments** (no on-prem AD, no AAD Connect). Client is AAD-joined or AAD-hybrid-joined (with the latter still needing some on-prem AD presence).

### Setup steps
1. SA must be in supported AAD Kerb region
2. Enable AAD Kerb on SA:
   ```powershell
   Set-AzStorageAccount -ResourceGroupName <rg> -Name <sa> -EnableAzureActiveDirectoryKerberosForFile $true
   ```
3. Grant API permissions to the auto-created App Reg in AAD
4. Assign RBAC on share scope:
   - `Storage File Data SMB Share Reader / Contributor / Elevated Contributor`
5. From AAD-joined client:
   ```cmd
   net use Z: \\<sa>.file.core.windows.net\<share>
   ```
   (No /User: param needed — uses signed-in AAD identity)

### Reference
[Mount Azure Files SMB Entra Only Kerberos_Storage](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/2182739)

---

## AF-Identity-EntraOnly-TSG — Azure Files SMB authentication with Entra Only Kerberos TSG (prereqs, supported clients AAD-joined / AAD-hybrid-joined, no on-prem AD, limitations, troubleshooting flow)

### Supported clients
- Win 10 21H2+ (some earlier with KB)
- Win 11 (all versions)
- WS 2022+
- Must be **AAD-joined** or **AAD hybrid-joined**

### Not supported
- AD DS-only joined clients (use § AF-Identity-ADDS-* instead)
- Workgroup clients
- macOS (use storage account key instead)
- Linux (use storage account key OR cifs-utils with sec=ntlmssp)

### Troubleshooting
- Mount fails → § AF-Identity-AADKerb-Hybrid-Flow (same TS applies)
- Klist 0x80090303 → § AF-Identity-AADKerb-Klist0x80090303
- Error 5 access denied → § AF-Identity-AADKerb-5

---

## AF-Identity-OAuth-REST-ASC-NoData — ASC unable to view data Share level with OAuth REST (shared key access disabled / data action RBAC missing / bearer token not acquired)

### Symptom
ASC → Files tab → "View files" fails to load when SA has `AllowSharedKeyAccess=false`.

### Cause
ASC view uses REST data plane — requires AAD token + correct RBAC.

### Resolution
- Grant `Storage File Data Privileged Contributor` to engineer's AAD user at SA scope
- ASC retries with bearer token automatically

---

## AF-Identity-OAuth-REST-RestrictKey — Restrict key-based access with OAuth REST (`AllowSharedKeyAccess=false` data plane only AAD token / implications for existing key-based tools)

### Feature
`Set-AzStorageAccount -AllowSharedKeyAccess $false` blocks all key-based data plane access — only AAD token works.

### Implications
- Existing key-based mounts FAIL after enabling
- AzCopy with key fails; use `--auth-mode login` instead
- Azure Storage Explorer with key fails; sign in with AAD instead
- AFS sync server using key fails; configure MI on AFS

### Tools that break (without migration)
- BACPAC import/export via key
- Old SDK versions
- Legacy automation scripts using keys

---

## AF-Identity-OAuth-REST-RoleCheck — Role assignment check for OAuth REST (`Storage File Data Privileged Contributor / Reader`, share-level vs data action needed)

### Available roles for Files OAuth REST
| Role | What it grants |
|---|---|
| `Storage File Data Privileged Contributor` | Full data plane: list shares, read/write files, manage permissions |
| `Storage File Data Privileged Reader` | Read only at data plane |
| `Storage Blob Data Reader/Contributor` | NOT applicable to Files (Blob only) |

### Check
- Portal → SA → Access Control (IAM) → Role assignments
- PowerShell: `Get-AzRoleAssignment -Scope /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/<sa>`

---

## AF-Identity-OAuth-REST-AuthMismatch — AuthorizationPermissionMismatch error (data plane RBAC missing Storage File Data Privileged Contributor or Reader needed for OAuth REST data actions)

### Symptom
REST call returns 403 with `<Code>AuthorizationPermissionMismatch</Code>`.

### Cause
- Caller has SA management roles (Contributor / Owner) but missing data plane role
- Data plane requires `Storage File Data Privileged Contributor/Reader` explicitly

### Resolution
- Assign the data plane role at SA or share scope
- Wait 5-10 min for propagation
- Retry REST call

---

## AF-Identity-Linux-ADDS — Linux AD Auth over SMB for Azure Files overview + troubleshooting (keytab setup, cifs-utils, krb5.conf, multiuser mount option required)

### Scope
Use AD-DS identity from Linux client (not AAD Kerb). Use case: Linux servers in domain need to mount Azure Files using domain credentials.

### Prereqs
- Linux client joined to AD DS (realmd / sssd / winbind)
- cifs-utils installed
- krb5.conf configured with realm
- keytab file with computer account

### Mount syntax (multiuser mode)
```bash
mount -t cifs //<sa>.file.core.windows.net/<share> /mnt/<share> \
  -o sec=krb5,vers=3.0,multiuser,cruid=$(id -u)
```

### Common issues
- "Permission denied" → check keytab + realm in krb5.conf
- "Cannot allocate memory" → kernel cifs version too old (need 4.10+)
- "No tickets in cache" → run `kinit` first

---

## AF-Identity-MI-SMB — Azure Files Managed Identity Support for SMB HowTo + TSG (system or user-assigned MI / RBAC / mount from Azure VM without creds, Preview)

### Feature
Azure VM with MI can mount Azure Files SMB share **without storage account key OR domain credentials**. Uses MI token for auth.

### Prereqs
- Premium Files (FileStorage) SA
- Azure VM with system-assigned or user-assigned MI
- RBAC: `Storage File Data SMB Share Reader/Contributor/Elevated Contributor` on share for the MI
- Win Server 2022 or Win 11 client OS

### Mount (no creds in command)
```powershell
# MI auth happens automatically when caller is the MI
net use Z: \\<sa>.file.core.windows.net\<share>
```

### Common issues
- MI token can't be acquired → IMDS unreachable (Playbook I § IMDS-*)
- 403 on mount → RBAC missing
- Feature not GA in all regions → check region availability

---

## AF-Identity-RBAC-SMBAdmin — How to assign RBAC roles for SMB admin privileges (Storage File Data SMB Share Elevated Contributor, NTFS ACL management takes effect)

### Steps
1. Portal → SA → File shares → select share → Access Control (IAM)
2. Add role assignment → `Storage File Data SMB Share Elevated Contributor`
3. Assign to user/group/MI
4. Wait 5-10 min for propagation
5. Klist purge + remount on client
6. Verify ACL management: `icacls Z:\test.txt /grant <user>:F`

---

## AF-Snapshot-Access — Access Azure File Share Snapshot (Portal, ASC, PowerShell, AzCopy, Storage Explorer methods)

### 5 access methods
1. **Portal** → SA → File shares → Snapshots tab → click snapshot → Browse
2. **ASC** → Resource Explorer → SA → Files → Snapshots
3. **PowerShell**: `Get-AzStorageShareSnapshot -Name <share>` then `New-AzStorageContext` with `-SnapshotTime`
4. **AzCopy**: `azcopy copy "https://<sa>.file.core.windows.net/<share>?sharesnapshot=<timestamp>" "local/path" --recursive`
5. **Storage Explorer**: connect to SA → expand share → "Show Snapshots"

### Mount snapshot via SMB (read-only)
```cmd
net use Z: \\<sa>.file.core.windows.net\<share>?<snapshot-timestamp> /User:Azure\<sa> <key>
```

---

## AF-Snapshot-SMB — SMB File Share Snapshots (creation + management / SMB version 2.x requirement / max 200 snapshots per share)

### Limits
- Max **200 snapshots per share**
- SMB 2.x or later client required to access
- Snapshots are read-only

### Creation
- Portal: SA → File shares → select share → + Add snapshot
- PowerShell: `(Get-AzStorageShare -Name <share>).Snapshot()`
- AzCopy: `azcopy make`
- Auto via Azure Backup policy

### Deletion (manual)
- Portal: select snapshot → Delete
- PowerShell: `Remove-AzStorageShare -Name <share> -SnapshotTime <ts>`

### Cost
Billed at share's tier rate (capacity + transactions).

---

## AF-Snapshot-NFS — NFS File Share Snapshots (Preview, Premium only, API version 2022-11-01, no snapshot mount via NFS protocol itself)

### Status: PUBLIC PREVIEW
- Premium FileStorage SA only
- Available via REST API 2022-11-01+, PowerShell preview module
- Snapshot is read-only point-in-time copy
- **NOT mountable via NFS protocol** — must copy to live share to restore

### Creation
```bash
az storage share-rm snapshot --storage-account <sa> --name <share>
```

### Access (copy method)
- Snapshot list: `az storage share-rm list --include-snapshots`
- Restore: copy from snapshot to a new share

---

## AF-Backup-AzBackup — Back-up Azure File Share with Azure Backup (Recovery Services Vault + backup policy + restore options)

### Setup
1. Create / use existing Recovery Services Vault
2. Vault → Backup → Workload = Azure File Share
3. Select SA → select share
4. Configure backup policy (frequency, retention)
5. Enable backup

### Backup operation
- Creates a share snapshot under the share (with `AzureFileSync` initiator marker)
- Snapshot stored in same SA (so SA delete fails — see J § SA-Delete-FileShare-BackupLock for the auto-recreated lock)

### Restore
- File-level: vault → restore → select file → mount restored snapshot to existing share
- Item-level: copy specific files from snapshot to live share
- Share-level: replace entire share contents

---

## AF-Backup-Check — Check Azure File Share Backup or Snapshot existence (ASC Files Configurations / Azure Backup / Snapshot Version 7131 / Timestamp 12/31/9999 signals not configured)

### ASC signals
ASC → Summary tab → **Files Configurations** section:
| Field | Value | Meaning |
|---|---|---|
| `Azure Backup Protected` | `N/A` | NOT enabled |
| `Azure Backup Protected` | `Yes` | Enabled |
| `Snapshot Version` | `7131` | NO snapshots exist |
| `Snapshot Timestamp` | `12/31/9999 23:59:59` | NO snapshots exist |

If both = "no signals" → no backup or snapshot exists → no recovery possible beyond Soft Delete (if enabled).

---

## AF-Backup-ACLNotRestored — Azure Backup doesn't restore manually assigned NTFS ACLs (known limitation, only inherited ACLs restored, manual or icacls script after restore)

### Symptom
After Azure Backup restore, custom NTFS ACLs are missing or reset to inherited.

### Cause
Known limitation — Azure Backup for SMB Files restores inherited ACLs but loses manually-set explicit ACLs on individual files/folders.

### Workaround
- Pre-restore: export ACLs with `icacls /save`
- Post-restore: re-apply ACLs with `icacls /restore`
- For FSLogix: re-apply CREATOR OWNER pattern

### Cross-link
J § SA-Recovery-FilesSMB for PG escalation when restore otherwise fails.

---

## AF-Recovery-SoftDelete — Soft Delete for File Shares (1 to 365-day retention, ASC Search File Share Soft Deleted Time + Expiry Time, billing implications)

### Feature
Soft Delete protects accidentally-deleted shares for 1-365 days (configurable).

### Configuration
- Portal: SA → File service → Properties → Soft delete → toggle ON
- Set retention 1-365 days
- Backwards compatible (apps don't need changes)

### How to check if a deleted share is recoverable
ASC → Resource Explorer → SA → Files → **Search File Share**:
- `Soft Deleted Time` = when share was soft-deleted
- `Expiry Time` = when share will be permanently deleted
  - Future = recoverable
  - `12/31/9999 23:59:59` = share is alive (not soft deleted)
- If share properties don't show up → permanently deleted, only Snapshot or external backup can restore

### Billing
- Soft deleted shares billed at **used** capacity (not provisioned)
- Premium shares: snapshot rate
- Standard shares: regular rate
- Free after permanent expiry

### Restore
Portal: Soft-deleted shares blade → Restore.

### Case coding
- `Routing Azure Storage File\Deletion and Recovery\Issue using soft delete feature`
- `Routing Azure Storage File\Deletion and Recovery\Recover deleted file share`

### Cross-link
For permanently-deleted shares (post-retention) → **Playbook J § SA-Recovery-FilesSMB** (Sev 3 ICM, best-effort).

---

## AF-EncryptionInTransit-Overview — Azure Files Encryption in Transit settings for SMB and NFS (Secure Transfer Required flag, SMB 3 encryption AES-128-GCM/AES-256-GCM, NFS 4.1 with TLS RPC with TLS)

### SMB
- **Secure Transfer Required** flag on SA → forces SMB 3.x encryption + HTTPS (REST)
- SMB Channel Encryption: AES-128-GCM (older) or AES-256-GCM (Win11/WS2022+)
- Pre-SMB-3 clients (Win 7, WS 2008 R2) can't connect when Secure Transfer Required = ON

### NFS
- NFS by default NOT encrypted in transit
- **Encryption in Transit for NFS** (Preview) — uses stunnel + `aznfs` mount helper for TLS tunneling on port 2049 → TLS port
- → see § AF-EncryptionInTransit-NFS-Overview

---

## AF-EncryptionInTransit-NFS-Overview — Encryption in Transit for Azure Files NFSv4.1 overview (TLS 1.3 via stunnel / aznfs mount helper / per-mount TLS tunneling)

### Feature
NFS v4.1 mount over TLS 1.3 tunnel via:
- `stunnel` daemon on Linux client
- `aznfs` mount helper (auto-configures stunnel)

### Setup
1. Install aznfs: `wget -O - https://github.com/Azure/AZNFS-mount/raw/main/aznfs_install.sh | bash`
2. Mount with aznfs:
   ```bash
   mount -t aznfs <sa>.file.core.windows.net:/<sa>/<share> /mnt/<share> -o vers=4,minorversion=1,sec=sys
   ```
3. aznfs auto-creates stunnel listener on local port → TLS to Azure on remote port

### Verify
- `cat /proc/mounts | grep aznfs`
- `systemctl status aznfswatchdog` (background monitor)

---

## AF-EncryptionInTransit-NFS-Troubleshooting — Encryption in Transit Azure Files NFSv4.1 Troubleshooting (stunnel config / port 2049 vs TLS port / cert trust chain / mount helper version)

### Common issues
1. **Mount hangs**: stunnel can't connect to remote TLS port → check NSG/firewall, must allow outbound to SA on TLS port
2. **Cert trust failure**: aznfs uses Mozilla CA bundle; outdated → update aznfs
3. **Port 2049 conflict**: aznfs uses local port 2049 for tunnel ingress; check no other NFS server running

### Diagnostic
```bash
journalctl -u aznfswatchdog -n 50
journalctl -u stunnel-aznfs -n 50
ss -tnlp | grep 2049
```

---

## AF-NFS-CollectTraces — Collect NFS client and network trace for Encryption in Transit (tcpdump on port 2049 / rpcdebug nlm / cat /proc/mounts /proc/net/rpc/nfs/fh)

### Procedure
```bash
# Network trace on local NFS port (before TLS tunnel)
tcpdump -i lo -w nfs-local.pcap port 2049

# Or on physical NIC (TLS-encrypted traffic)
tcpdump -i eth0 -w nfs-tls.pcap host <sa>.file.core.windows.net

# Detailed NLM debug
rpcdebug -m nfs -s all
rpcdebug -m nfsd -s all
# Reproduce issue
rpcdebug -m nfs -c all
rpcdebug -m nfsd -c all

# Snapshot of state
cat /proc/mounts | grep nfs
cat /proc/net/rpc/nfs

# View running NFS handles
find /proc/net/rpc/ -type f -exec cat {} \;
```

---

## AFS-Sync-Workflow — Master Azure File Sync workflow (Feature overview + Terminology, Cloud Endpoint + Server Endpoint + Sync Group + Registered Server + Storage Sync Service, RBAC, DON'T unregister-server warning, Telemetry events mapping)

### Terminology
| Term | Definition |
|---|---|
| **Storage Sync Service** | Top-level Azure resource for AFS (peer of SA) |
| **Sync Group** | Defines sync topology — set of endpoints kept in sync |
| **Registered Server** | Trust relationship between server (or cluster) and Storage Sync Service |
| **Cloud Endpoint** | Azure file share that's part of a sync group |
| **Server Endpoint** | Specific folder on a registered server (or volume) |
| **Cloud Tiering** | Optional — tier infrequently used files > 64 KiB to Azure Files |

### Scenario capabilities
- Multi-site sync: up to **50 servers per sync group**
- Cloud tiering: HSM-style with `StorageSync.sys` filter creating reparse points
- Rapid Disaster Recovery: namespace-first restore
- Cloud-backup via snapshots (preview hardening to backup vault)

### ⚠ CRITICAL warning
**DO NOT unregister-server or recreate-endpoints to "fix" sync issues unless explicitly instructed by Microsoft engineer.** Unregister is DESTRUCTIVE:
- SEPs de-provisioned
- Tiered files ORPHANED
- Recreate SEPs delayed until Orphaned Files Cleanup completes (can take hours for large namespaces)
- Tiered files **outside** SEP namespace **may be permanently lost**

### RBAC for AFS (built-in roles)
| Role | Permissions |
|---|---|
| `Azure File Sync Administrator` | Full mgmt of all Storage Sync Service resources |
| `Azure File Sync Reader` | Read-only on Storage Sync Service |

### Latest agent version
Check [release notes](https://docs.microsoft.com/en-us/azure/storage/files/storage-files-release-notes) — best practice: keep agent up-to-date.

### Region requiring access request
France South, South Africa West, UAE Central — customer must request Azure Storage access before using AFS.

### Standard 100 TiB shares limitations
- LRS or ZRS only (no GRS/GZRS)
- Cannot enable Large File Share then change redundancy to GRS/GZRS
- Cannot disable Large File Share once enabled

### AFS Telemetry Events (Jarvis MDM namespace `KailaniSVC`)
| EventId | Type | Description |
|---|---|---|
| 7003 / 7006 | Upload | Batch upload telemetry (throughput + throttling) |
| 7004 / 7005 | Download | Batch download telemetry (throughput + throttling) |
| 9121 | Sync error | Per-session sync error event |

### Master TS resources
- [Troubleshoot Azure File Sync (Public)](https://docs.microsoft.com/en-us/azure/storage/files/storage-sync-files-troubleshoot)
- [Per file/directory sync errors](https://docs.microsoft.com/en-us/azure/storage/file-sync/file-sync-troubleshoot?tabs=portal1%2Cazure-portal#troubleshooting-per-filedirectory-sync-errors)
- [Common sync errors](https://docs.microsoft.com/en-us/azure/storage/file-sync/file-sync-troubleshoot?tabs=portal1%2Cazure-portal#common-sync-errors)
- [Common management errors](https://docs.microsoft.com/en-us/azure/storage/file-sync/file-sync-troubleshoot?tabs=portal1%2Cazure-portal#sync-group-management)
- [Tiering errors](https://docs.microsoft.com/en-us/azure/storage/file-sync/file-sync-troubleshoot?tabs=portal1%2Cazure-portal#tiering-errors-and-remediation)
- [Recall errors](https://docs.microsoft.com/en-us/azure/storage/file-sync/file-sync-troubleshoot?tabs=portal1%2Cazure-portal#recall-errors-and-remediation)

---

## AFS-Sync-Conflict — Conflict Issues (ECS_E_SYNC_CONSTRAINT_CONFLICT / ECS_E_SYNC_FILE_IN_USE / ECS_E_SYNC_MERGE_TOMBSTONE_CHECKS_FAILED, customer runs FileSyncErrorReport.ps1, Jarvis ServerTelemetryEvents EventId 9121 and ServerItemResultsEvents by ClientCorrelationId)

### Symptom
ASC shows sync errors with per-item error codes. Common combos:
- `ECS_E_SYNC_FILE_IN_USE` (file locked by another process)
- `ECS_E_SYNC_CONSTRAINT_CONFLICT` (dependent on a file that's failing)
- `ECS_E_SYNC_MERGE_TOMBSTONE_CHECKS_FAILED` (download direction; tombstone consistency error)
- `ERROR_ALREADY_EXISTS` (file conflict)
- `ERROR_INVALID_NAME` (invalid char in filename)
- `ERROR_FILE_NOT_FOUND`

### Step 1 — ASC Sync Health check
ASC → SA → File Sync → Sync Group → Server Endpoint → Health tab

Look for:
- Old agent version → recommend upgrade FIRST
- Per-item error counts

### Step 2 — Customer runs FileSyncErrorReport.ps1
[FileSyncErrorReport.ps1](https://docs.microsoft.com/en-us/azure/storage/files/storage-sync-files-troubleshoot?tabs=portal1%2Cazure-portal#how-do-i-see-if-there-are-specific-files-or-folders-that-are-not-syncing)

This is the ONLY way to get filename detail — CSS/PG/XEEE cannot see filenames in logs.

### Step 3 — CSS-side Jarvis correlation (KailaniSVC.ServerTelemetryEvents EventId 9121)

```
Namespace:  KailaniSVC
Events:     ServerTelemetryEvents
TimeRange:  Now-1d to Now
Filter:     ServerEventId == 9121 AND SubscriptionId == <subId> AND SyncGroupName == <name>
Order by:   PreciseTimeStamp desc
```

Each row's `EventDescription` contains: `ServerEndpointName, SyncGroupName, ClientCorrelationId, SyncDirection, ItemHResult, PersistentCount, TransientCount, SessionHResult`.

Note `ClientCorrelationId` (e.g., `{1EE3DD30-A89E-4826-B172-94E7956F1B5F}`).

### Step 4 — Per-item details via ServerItemResultsEvents

```
Namespace:  KailaniSVC
Events:     ServerItemResultsEvents
TimeRange:  Now-1d to Now
Filter:     SubscriptionId == <subId> AND CorrelationId == "<ClientCorrelationId>"
Order by:   PreciseTimeStamp desc
```

Result shows the file hashes failing + persistent/transient classification.

### Resolution
- Persistent errors → customer must take action (close file, rename invalid chars, etc.)
- Transient → will auto-retry; monitor next sync session
- File in use → customer runs FileSyncErrorReport.ps1, identifies files, closes them
- Tombstone errors → consistency error, may require PG escalation

---

## AFS-Sync-NotSyncingFromShare — File not syncing from File Share to Server (cloud change detection runs every 24h / REST changes don't update SMB last modified / customer can trigger change detection job manually)

### Cause
- Cloud change detection job runs every **24h** on cloud endpoint (Azure file share)
- Changes made via REST (REST API / PowerShell / AzCopy / Storage Explorer) do NOT update SMB last-modified attribute → not detected as a change by sync
- Changes made via SMB on Azure file share directly are detected

### Resolution
- Customer waits for next 24h change detection cycle, OR
- Trigger manual change detection: Portal → Storage Sync Service → Sync Group → Cloud endpoint → Recall hot files / trigger change detection
- For REST-modified files: re-modify via SMB or wait for next cycle

### Reference
[AFS FAQ on Azure file share direct changes](https://docs.microsoft.com/en-us/azure/storage/files/storage-files-faq#azure-file-sync) (search "change detection job").

---

## AFS-Sync-NotSyncingFromServer — File not syncing from Server to File Share (realtime CRUD expected few mins, ASC validation, Server Endpoint upload errors, AzureFileSyncErrorReport.ps1)

### Expectation
Server-side CRUD (Create / Update / Delete) is REALTIME — file should appear on cloud share in **few minutes max**.

### Step 1 — Validate basic
- ASC → SA → File Sync → Sync Group → Server Endpoint → Health
- Check upload/download progress timestamps recent
- Validate cloud endpoint matches customer's file share URL
- Customer might be checking wrong file share

### Step 2 — Check the file specifically
- Customer screenshot of changed file (path + size + timestamp)
- ASC → SA → File share → look for same file (size + timestamp match)
- If file IS there → already synced, customer's check timing issue

### Step 3 — Server endpoint upload errors
- ASC → upload error count
- If errors exist: customer runs `AzureFileSyncErrorReport.ps1` → identify files in error → fix per error code (parent folder change typically blocks child file sync)

### Step 4 — Collect server diagnostic logs
- Per [AFSDiag procedure](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/510939/Azure-File-Sync-Workflow_Storage?anchor=how-to%3A-view-diagnostic-data-collected-from-a-server)

### Step 5 — Check sync agent health
- ASC → Registered Servers → Server endpoint → Status (should be Online)
- If not Online → § AFS-Agent-RegFailures

### Step 6 — Check SA / share restrictions
- IP whitelisted? (RSRP subscription)
- Firewall enabled?
- RBAC: if `AllowSharedKeyAccess=false`, MI must be configured

### Step 7 — Check upload/download errors per AFS troubleshooting guide

### Step 8 — Agent version
- If not latest, customer upgrades per release notes

### Scenario: `ECS_E_NOT_ENOUGH_REMOTE_STORAGE`
See § AFS-Sync-NotEnoughRemoteStorage.

---

## AFS-Sync-NotEnoughRemoteStorage — ECS_E_NOT_ENOUGH_REMOTE_STORAGE (file share at 5TB default limit, customer expands to Large File Share up to 100TB)

### Symptom
File upload to cloud share fails: `ECS_E_NOT_ENOUGH_REMOTE_STORAGE`. ASC shows Cloud Endpoint Data Size = 5 TB (at limit).

### Cause
Default Azure file share is 5 TB. Server has more data to upload → fails for lack of space.

### Resolution
Customer expands share to **Large File Share** (up to 100 TB) per [Create Large File Share](https://docs.microsoft.com/en-us/azure/storage/files/storage-files-how-to-create-large-file-share?tabs=azure-portal):
- LRS or ZRS only
- Once enabled, cannot disable
- Cannot convert to GRS/GZRS after enabling

---

## AFS-Sync-NotEnoughLocalStorage — ECS_E_NOT_ENOUGH_LOCAL_STORAGE Not enough space on server to sync (enable cloud tiering or add disk capacity)

### Symptom
Server cannot download files locally — volume full.

### Resolution
- **Enable cloud tiering** on server endpoint with low Volume Free Space %
- Add disk capacity to volume
- Tier specific large files manually: `Invoke-StorageSyncFileRecall`

---

## AFS-Sync-MetadataKnowledgeLimit — ECS_E_SYNC_METADATA_KNOWLEDGE_LIMIT_REACHED (2134375908, very large namespace, namespace split or PG escalation required)

### Symptom
Sync fails with `ECS_E_SYNC_METADATA_KNOWLEDGE_LIMIT_REACHED` (hex 2134375908).

### Cause
Sync metadata knowledge graph exceeded internal scalability limit. Typically for very large namespaces (100M+ files).

### Resolution
- Split into multiple sync groups (each with smaller namespace)
- PG escalation if customer can't split

---

## AFS-Sync-MgmtFileLocks — ECS_E_MGMT_FILE_LOCKS_OPERATION_ERROR (file lock management failure during sync, reboot server / check VSS state)

### Cause
- Local file system lock manager has stuck state
- VSS shadow copy snapshot interferes with locks

### Resolution
- Restart server (clears lock state)
- Disable VSS sync if conflicts → § AFS-Sync-CancelledByVSS

---

## AFS-Sync-CancelledByVSS — ECS_E_SYNC_CANCELLED_BY_VSS (TSG 428, Disable VSS Sync, VSS snapshot taken during sync session cancels it, scheduling conflict)

### Symptom
Sync session repeatedly cancels with `ECS_E_SYNC_CANCELLED_BY_VSS`.

### Cause
VSS snapshot (Windows Backup, NTBackup, third-party) taken during sync session causes the session to cancel.

### Resolution
- Reschedule VSS / backup to NOT overlap with sync window
- Disable VSS sync if customer doesn't need it: refer to [TSG 428](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/784056)

---

## AFS-Sync-DirectoryRenameFailed — ECS_E_DIRECTORY_RENAME_FAILED (TSG 504, per-item upload error on directory rename, rename target name conflict or permissions issue)

### Cause
- Target name already exists on cloud
- Caller doesn't have rename permission
- Cloud endpoint case-sensitivity mismatch

### Resolution
- Customer identifies failing rename via FileSyncErrorReport.ps1
- Manually delete conflicting target on cloud, OR rename to unique name on server first

### Reference
[TSG 504](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/1032001)

---

## AFS-Sync-ServerCredentialNeeded — ECS_E_SERVER_CREDENTIAL_NEEDED (server can't authenticate to cloud, SA key rotated / MI not configured / shared key access disabled)

### Cause
- SA key rotated, AFS server still using old key → re-acquire
- `AllowSharedKeyAccess = false` on SA but MI not configured for AFS → AFS can't auth
- MI configured but missing required RBAC role

### Resolution
- If using key: refresh by re-registering server OR using `Reset-StorageSyncCredential`
- Migrate to MI: § AFS-Identity-MI-Overview
- Verify MI has `Storage File Data SMB Share Elevated Contributor` on share

---

## AFS-Sync-Progress — TSG 349 AFS Sync Progress and Initial Sync (ASC Sync Status tab, upload throughput vs total data size, rapid disaster recovery namespace first then recall)

### Initial sync stages
1. **Namespace seeding** (~few min for 100K files) — full namespace appears as tiered files
2. **Data upload/download** — files actually transferred
3. **Tiering** — if cloud tiering enabled, files older than policy criteria are tiered

### Progress monitoring
- ASC → Sync Group → Sync Status → "Files synced" + "Total files" + "Bytes synced" + "Total bytes"
- Local server: `Get-StorageSyncFileTransferProgress` PowerShell

### Rapid Disaster Recovery
- Add new server to existing sync group → full namespace appears immediately as tiered placeholders
- Background recall fills local disk based on tiering policy

### Reference
[TSG 349](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/784054)

---

## AFS-Sync-UploadAccessDenied — AFS Uploading Failed with Access Denied (share RBAC or key issue, MI not configured correctly, SA firewall blocking server IP)

### Cause
- SA key invalid (rotated) and MI not configured
- MI configured but missing data plane RBAC role
- SA firewall blocking server's public IP

### Resolution
- Verify firewall allows server IP / VNET / Service Endpoint
- For MI: assign `Storage File Data SMB Share Elevated Contributor`
- For key: refresh credential via `Reset-StorageSyncCredential`

---

## AFS-Sync-MgmtForbidden — AFS MgmtForbidden Failed to provision replica group (SA permissions, MI missing, shared key access disabled without MI fallback)

### Cause
AFS service tries to call SA management API but is forbidden — typically MI missing or RBAC not granted.

### Resolution
- Verify AFS Storage Sync Service's system MI exists and has:
  - `Reader and Data Access` role on SA (legacy)
  - OR `Storage Account Contributor` + `Storage File Data SMB Share Elevated Contributor` on share (current)
- Re-register server endpoint after fixing perms

---

## AFS-Sync-MgmtStorageAccountInaccessible — AFS MgmtStorageAccountInaccessible (SA firewall blocking AFS service, private endpoint, MI not trusted, key rotated)

### Cause
AFS management calls to SA blocked by network/firewall/perms.

### Resolution
- SA firewall: add "Trusted Microsoft services" exception
- If private endpoint only: verify PE for `StorageSync` service in VNET
- Refresh key or migrate to MI

---

## AFS-Sync-CantAccessFile — Unable to sync with ERROR_CANT_ACCESS_FILE (file locked by app, antivirus quarantine, file system corruption)

### Cause
- File locked exclusively by app/process
- Antivirus has file quarantined
- File system corruption (run `chkdsk`)

### Resolution
- Close locking app (Process Explorer to find holder)
- Add AFS folder to AV exclusion (per `StorageSync.sys` filter requirements)
- Run `chkdsk /f` on volume

---

## AFS-Sync-UnableDeleteTiered — Unable to delete tiered file (cloud tiering recall fails, cert revocation, server offline)

### Cause
- When deleting tiered file, AFS attempts recall first → fails because of cert/network
- Server endpoint offline → tiering filter can't proceed

### Resolution
- Check § AFS-Tiering-UnableRecallCertRev for cert
- Bring server endpoint online
- Force-delete via `Invoke-StorageSyncCloudTiering -RemoveFromCloud` if appropriate

---

## AFS-Sync-UnableRename — Unable to rename file 0x800705AA (ERROR_NO_SYSTEM_RESOURCES, server resource exhaustion / VSS snapshot conflict)

### Cause
Server low on memory/handles OR VSS snapshot holding file.

### Resolution
- Restart server
- Postpone VSS during heavy sync activity

---

## AFS-Agent-InstallIssues — File Sync Agent Installation Issues (MSI error codes, exit code mapping, missing prereqs .NET 4.6.1 + PowerShell 5.1 Internet access for cloud endpoints validation)

### Common install issues
- **.NET Framework 4.6.1+** required (Win 2012 R2 needs upgrade)
- **PowerShell 5.1+** required
- **Internet access** to cloud endpoints during install (validation calls)
- **Server not joined to AD** for AD-required scenarios

### Investigation
- MSI log: `%TEMP%\StorageSyncAgent.log`
- Or `msiexec /i StorageSyncAgent.msi /l*v install.log`
- Exit code 1603 = generic; check log details

### Common fixes
- Install .NET 4.6.1+
- Update PowerShell
- Allow `https://*.afs.azure.net` outbound

---

## AFS-Agent-TSG222 — TSG 222 AFS Agent Installation troubleshooting (msiexec logs, StorageAgent MSI logs, StorageSyncGuestAgentInstall logs)

### Log locations
- `%TEMP%\StorageSyncAgent.log` — MSI install log
- `%ProgramData%\StorageSync\` — runtime logs
- Windows Event Log: `Applications and Services Logs → Microsoft → FileSync`

### Reference
[TSG 222](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/784051)

---

## AFS-Agent-UpdaterHang — File Sync Agent Updater Hang (stuck during version upgrade, manual MSI install, check AutoUpdater service status)

### Symptom
AFS agent upgrade hangs at "Updating Azure File Sync".

### Resolution
1. Stop FileSyncSvc + StorageSyncAgentUpdater service
2. Manually install latest MSI from [release notes](https://docs.microsoft.com/en-us/azure/storage/files/storage-files-release-notes)
3. Start services
4. Verify version: `(Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Azure\StorageSync').AgentVersion`

---

## AFS-Agent-Upgrade — Azure File Sync Agent Upgrade (major vs minor update, release notes, rollback via MSI uninstall/install old version, ring deployment stable / preview)

### Upgrade rings
- **Stable** (default) — recommended for production
- **Preview** — early access for testing
- **Test** — Microsoft internal use only

### Set ring via PowerShell
```powershell
Set-StorageSyncAgentAutoUpdatePolicy -PolicyTrack Stable
```

### Manual upgrade
1. Download latest MSI from [release notes](https://docs.microsoft.com/en-us/azure/storage/files/storage-files-release-notes)
2. Run MSI → upgrade in-place (preserves config)
3. Verify version

---

## AFS-Agent-UpgradeIssue — Azure File Sync Agent Upgrade Issue (MSI rollback / existing config corruption / server endpoint state machine disrupted)

### Common upgrade issues
- MSI rolls back mid-install → check log for cause (perms, .NET, AV blocking)
- After upgrade, sync stops → restart FileSyncSvc service
- After upgrade, agent shows "Not Registered" → re-register via `Register-AzStorageSyncServer`

---

## AFS-Agent-Rollback — Sync Agent Installation Rollback (failed upgrade rollback, MSI installer, restore previous agent, re-register if needed)

### When to rollback
- New version has regression affecting customer
- Upgrade left agent in bad state

### Procedure
1. Uninstall current agent: `msiexec /x StorageSyncAgent.msi`
2. Install previous version MSI
3. Verify FileSyncSvc starts
4. If "Not Registered" → re-register

---

## AFS-Agent-AutoUpdaterPolicy — Filesync Agent AutoUpdater Policy (3 ring types Stable, Preview, Test, how to set via PowerShell, server registration vs individual)

### Policy values
- `Stable` (default)
- `Preview`
- `Test` (Microsoft internal only)

### Set per-server
```powershell
Set-StorageSyncAgentAutoUpdatePolicy -PolicyTrack Stable
```

### Set globally (all servers in sync service)
Configure in Storage Sync Service properties.

---

## AFS-Agent-RegFailures — File Sync troubleshoot agent registration failures (StorageSync registration REST call failure, firewall blocks mgmt endpoints, MI not configured)

### Common failures
- Firewall blocks `https://management.azure.com` or `https://*.afs.azure.net`
- Caller missing `Microsoft.StorageSync/register/action` perm
- MI not configured but `AllowSharedKeyAccess = false` on target SA
- Server not joined to a supported AD/cloud auth context

### Investigation
- `Test-NetConnection management.azure.com -Port 443`
- Check registration log: `%TEMP%\StorageSyncRegister.log`
- Verify caller role: `Get-AzRoleAssignment -SignInName <user>`

### Reference
[File Sync troubleshoot agent registration](https://learn.microsoft.com/en-us/azure/storage/file-sync/file-sync-troubleshoot-installation)

---

## AFS-Agent-UnableRegisterSEP — AFS Unable to register Azure File Sync Server Endpoint (volume not supported network, NTFS required, cloud tiering prereqs, path in use)

### Symptom
`Register Server Endpoint` fails with various errors.

### Common causes
- **Volume not NTFS** (ReFS, FAT32 unsupported)
- **Network volume** (UNC path / mapped drive) — only local non-removable disk
- **Path already in use** by another server endpoint
- **System volume cloud tiering attempted** (not supported on system volume)
- **Path doesn't exist** or no permissions

### Resolution
- Use NTFS local volume only
- Use unique path
- Don't enable tiering on C:\

---

## AFS-Agent-ReplaceServer — Replace File Sync Server procedure (pre-stage cloud-tiered data on new server, re-register, re-create SEP, orphaned files cleanup)

### Procedure for hardware refresh
1. On NEW server: install AFS agent, register with same Storage Sync Service
2. Pre-stage data (optional, for faster initial sync): use Robocopy to seed namespace from old server
3. Create Server Endpoint on new server pointing to same Sync Group
4. Wait for initial sync (namespace + cloud tiering policy applies)
5. Validate data presence
6. Decommission old server (deregister cleanly, NOT just shutdown)

### ⚠ Critical
Old server tiered files become orphaned if old server is unregistered before new server is fully sync'd.

---

## AFS-Agent-ReplaceDrive — File Sync Replace Drive procedure (move SEP to new volume without orphaning tiered files, xcopy backup/restore method)

### Procedure for drive replacement
1. Deregister Server Endpoint (NOT server)
2. Use Robocopy to copy data from old drive to new drive (preserve attributes + ACLs)
3. Recreate Server Endpoint on new drive
4. Reconcile orphaned tiered files via PG escalation if any

---

## AFS-Agent-RegProxyFirewall — How to register Server Endpoint with Restricted Network or Proxy Firewall (required endpoints list, proxy config, bypass list)

### Required outbound endpoints
- `https://*.afs.azure.net` (AFS service)
- `https://management.azure.com` (ARM)
- `https://login.microsoftonline.com` (AAD auth)
- `https://*.blob.core.windows.net` (Azure Storage)
- `https://*.file.core.windows.net` (Azure Files)

### Proxy config
- Set system proxy via `netsh winhttp set proxy` for FileSyncSvc
- Or use AFS agent proxy setting in registry
- Add `bypass-list` for `*.afs.azure.net` if needed

### Reference
[Set up AFS proxy and firewall](https://docs.microsoft.com/en-us/azure/storage/files/storage-sync-files-firewall-and-proxy)

---

## AFS-Agent-Hung — AFS Agent Hung (FileSyncSvc not responding, restart service, collect kernel dump TSG AFS, check disk space)

### Symptom
FileSyncSvc shows running but no progress, no logs, sync stuck.

### Resolution
1. Stop service: `Stop-Service FileSyncSvc -Force`
2. Check disk space (low disk space can hang sync)
3. Start service: `Start-Service FileSyncSvc`
4. If recurs, collect kernel dump per [TSG AFS Kernel dump](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/784058)
5. Engage PG with dump

---

## AFS-Tiering-Master — Master AFS Cloud Tiering TSG (architecture, how it works StorageSync.sys + reparse points, tiering policies volume free space + date-based, feature bitmap, ESE database)

### Architecture
- `StorageSync.sys` kernel-mode file system filter
- When file is tiered: replaced with **reparse point** with URL to cloud blob
- Reparse point sets NTFS `offline` attribute → Explorer shows APLO in Attributes column
- File access triggers seamless recall — user doesn't see it's not local
- Recall pulls from cloud via HTTPS, no SMB

### Tiering policies (per Server Endpoint)
1. **Volume Free Space** policy — tier until X% free
2. **Date-Based** policy — tier files older than N days
3. Both can be combined

### Heat Store (local ESE database)
- Location: `C:\ProgramData\StorageSync\HeatStore\`
- Tracks file access heat for tiering decisions
- ESE (Extensible Storage Engine) database
- If corrupt → see § AFS-Tiering-CorruptHeatStore

### Feature bitmap
StorageSync.sys uses a feature bitmap to gate tiering decisions. Some features (like date-based tiering) require minimum agent version.

### Reference
[TSG AFS Cloud Tiering](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495822)

---

## AFS-Tiering-WhyTiered — TSG AFS Cloud Tiering Check why a file is tiered (fsutil reparsepoint query, StorageSync CLI, heat store investigation, per-file attribute check)

### Check if file is tiered
```cmd
fsutil reparsepoint query <file>
# If reparse point present → file is tiered
```

Or check Windows Explorer Attributes column for `APLO`.

### Find why tiered
- Volume free space dropped below policy threshold → file tiered
- File older than date policy → file tiered
- Manual recall via PowerShell: `Invoke-StorageSyncFileRecall -Path <path>`

### Heat store investigation
- View heat score via diagnostic dump (§ AFS-Tiering-DumpHeatStore)
- Files with lowest heat score tiered first

---

## AFS-Tiering-DumpHeatStore — TSG AFS Cloud Tiering Dump heat store data (cdpsvc stop, ESE database dump, heat score decimation format)

### Procedure
1. Stop CDP service if running: `Stop-Service cdpsvc`
2. Use ESE management tools (esentutl) to dump heat store DB:
   ```cmd
   esentutl /d "C:\ProgramData\StorageSync\HeatStore\HeatStore.edb"
   ```
3. Parse output via PG-provided tooling

### Reference
[TSG AFS Cloud Tiering Dump heat store](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/863880)

---

## AFS-Tiering-HeatProcessExclusion — TSG AFS Cloud Tiering Heat tracking process name exclusion from last access time tracking (Set-StorageSyncServer cmdlet or registry key, prevent backup or AV from promoting files)

### Use case
Backup software / AV reads all files → updates last-access time → all files appear "hot" → tiering policy doesn't tier → volume fills.

### Resolution
Exclude backup/AV processes from heat tracking:
```powershell
Set-StorageSyncServer -HeatTrackingProcessNamesExclusionList @("backupd.exe", "antivirus.exe")
```

Or via registry: `HKLM\Software\Microsoft\Azure\StorageSync\HeatTrackingProcessNamesExclusionList` (REG_MULTI_SZ).

---

## AFS-Tiering-CorruptHeatStore — TSG AFS Cloud Tiering Identify a corrupt heatstore (Event ID 9006, ESE database recovery, rebuild heatstore procedure)

### Symptom
EventLog `StorageSync` channel shows Event ID **9006** — heatstore corruption.

### Resolution
- Try ESE recovery: `esentutl /r edb /l "C:\ProgramData\StorageSync\HeatStore\"`
- If recovery fails → delete heatstore (§ AFS-Tiering-DeleteHeatStore) → AFS rebuilds empty (loses heat history but functional)

---

## AFS-Tiering-HeatStore — TSG AFS Heat Store (purpose, location C:\ProgramData\StorageSync\, ESE database structure, size considerations)

### What it is
- ESE database tracking per-file last-access time + access frequency ("heat")
- Used to make tiering decisions
- Located: `C:\ProgramData\StorageSync\HeatStore\`
- Size grows with file count — can reach GB for large endpoints

### Backup recommendation
NOT in normal backup scope — auto-rebuilds if deleted, but loses heat history (suboptimal tiering after delete).

---

## AFS-Tiering-DeleteESE — TSG 196 AFS Delete an ESE database on the server (corrupt heatstore delete procedure, FileSyncSvc stop, delete database.db restart, rebuilds on next start)

### When to use
- Heatstore corruption per § AFS-Tiering-CorruptHeatStore
- After explicit instruction from PG

### Procedure
```cmd
Stop-Service FileSyncSvc
Remove-Item "C:\ProgramData\StorageSync\HeatStore\HeatStore.edb"
Remove-Item "C:\ProgramData\StorageSync\HeatStore\*.log"
Remove-Item "C:\ProgramData\StorageSync\HeatStore\*.chk"
Start-Service FileSyncSvc
```

Empty heatstore rebuilds on next access.

### Reference
[TSG 196](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/863876)

---

## AFS-Tiering-CollectHeatStoreOffline — TSG 212 AFS Cloud Tiering Collect heatstore for offline analysis (stop FileSyncSvc, copy C:\ProgramData\StorageSync\HeatStore\db, send to DTM)

### Procedure
```cmd
Stop-Service FileSyncSvc
robocopy "C:\ProgramData\StorageSync\HeatStore" "%TEMP%\HeatStore-backup" /MIR
Start-Service FileSyncSvc
# Zip %TEMP%\HeatStore-backup and send via DTM
```

### Reference
[TSG 212](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/863877)

---

## AFS-Tiering-DeleteHeatStore — TSG 213 AFS Cloud Tiering Deleting a heatstore procedure (FileSyncSvc stop, delete C:\ProgramData\StorageSync\HeatStore\db, restart rebuilds empty)

Same as § AFS-Tiering-DeleteESE.

---

## AFS-Tiering-GreyX — Grey 'X' on Tiered Files (Windows Explorer offline attribute displays as grey X, APLO attribute, StorageSync.sys filter not loaded, reparse point corruption)

### Symptom
Windows Explorer shows tiered files with grey X icon and APLO attribute.

### Cause
- **Normal display** when StorageSync.sys filter is loaded and file is tiered
- **Stuck X** indicates `StorageSync.sys` filter not loaded → no recall on access
- Reparse point corruption

### Investigation
- Check filter loaded: `fltmc instances` → look for `StorageSync.sys`
- If not loaded: restart FileSyncSvc; if persistent, reinstall agent
- Check reparse point: `fsutil reparsepoint query <file>`

---

## AFS-Tiering-RecallPerf — Recall Performance Study (recall bandwidth influenced by disk IOPS + network + ESE database size, customer prestaging best practices)

### Recall throughput factors
- Local disk IOPS / throughput
- Network bandwidth + latency
- Heat store ESE database size (larger = more memory + IOPS pressure)
- File size (small files more overhead per file)

### Best practices
- Use SSD for endpoint volume
- Network ≥ 10 GbE for high-throughput scenarios
- Pre-stage frequently-accessed files (disable tiering for them via process exclusion or category)
- Avoid AV full-file scans

---

## AFS-Tiering-CacheMaxThreshold — TSG AFS Recall Error file system cache usage reached maximum threshold (Event ID 9023, cloud tiering policy too aggressive, enable Volume Free Space policy)

### Symptom
Event Log StorageSync channel: Event ID **9023** — "File system cache usage reached maximum threshold". Recalls fail.

### Cause
- Cloud tiering policy too aggressive — tiering too much, recall demands exceed cache capacity
- Bulk recall operation exceeds cache budget

### Resolution
- Enable / adjust Volume Free Space policy to keep more local files
- Adjust Date-Based policy to be less aggressive
- Throttle recall operations (avoid bulk recall)

---

## AFS-Tiering-MacOSSlowRecall — TSG AFS MacOS slow file recall tiering (SMB client not optimized for tiered files, prestage files or disable tiering for Mac clients)

### Symptom
Mac clients accessing tiered files via SMB experience very slow access.

### Cause
MacOS SMB client doesn't handle reparse points efficiently — triggers many round-trips per recall.

### Resolution
- Pre-stage files Mac clients need
- Disable tiering for Mac-accessed shares
- Use NFS instead if possible

---

## AFS-Tiering-UnableRecallCertRev — Unable to recall due to certificate revocation (server cert expired, OCSP or CRL validation failing, proxy blocking cert validation endpoints)

### Symptom
Recall fails with certificate error.

### Cause
- Server-side cert expired
- OCSP / CRL endpoint unreachable (proxy blocking)
- System time skewed → cert appears expired

### Resolution
- Verify cert: `Get-ChildItem Cert:\LocalMachine\My\<thumbprint>`
- Allow OCSP / CRL endpoints through proxy (Microsoft's revocation endpoints)
- Sync system time

---

## AFS-Tiering-ServerCertIssues — AFS Server Certificate Issues (cert bound to StorageSync channel expired, invalid thumbprint, cert chain broken)

### Symptom
AFS sync fails with TLS/cert errors at server channel.

### Resolution
- Check cert binding: `netsh http show sslcert`
- Verify cert chain trust
- Reset cert binding via [TSG AFS Server Certificate Issues](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/784059)

---

## AFS-Identity-MI-Overview — AFS Manage Identities (system-assigned MI default for new deployments since v19.0.0.0, eliminates shared key dependency, prereqs v19.0.0+ trusted services allowed key access enabled)

### Benefits
- Eliminates shared keys (SA key + SAS) dependency
- Compliance with key-rotation policies
- Internal teams using AFS no longer need shared key exception

### Default behavior
**Managed identities are enabled BY DEFAULT for all newly-created Storage Sync Services.**

### MI usage scenarios
- Storage Sync Service authentication to Azure file share
- Registered server authentication to Azure file share
- Registered server authentication to Storage Sync Service

### Prerequisites
- Storage Sync Service deployed + at least one registered server
- **AFS agent version 19.0.0.0 or later**
- On target storage accounts:
  - Caller must be `Owner` OR have `Microsoft.Authorization/roleAssignments/write`
  - "Allow Azure services on the trusted services list" must be ENABLED
  - "Allow storage account key access" must be ENABLED (yes, even with MI — needed during onboarding)
- `Az.StorageSync` PowerShell module **v2.2.0 or later**:
  ```powershell
  Install-Module Az.StorageSync -Force -AllowClobber
  ```

### Reference
[How To system MI for AFS](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/2180200/How-To-for-a-system-managed-identity-on-Azure-File-Sync_Storage)

---

## AFS-Identity-MI-ExpectedIssues — Expected Issues for Managed Identities on Azure File Sync (known limitations preview, must allow trusted services, shared key access required during onboarding)

### Known limitations
- "Allow trusted services" exception MUST be on, even with MI (sync uses this path)
- "Allow shared key access" required during initial onboarding
- Some legacy operations may still use key path
- Region availability — check feature availability before enabling

### Reference
[Expected Issues](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/2180201/Expected-Issues-for-Managed-Identities-on-Azure-File-Sync_Storage)

---

## AFS-Arc-Extension — Azure Arc Extension for File Sync (extension install + config + telemetry via Arc, troubleshooting extension deployment failure, state recovery, query Arc events)

### Use case
Run AFS on **Arc-enabled** non-Azure servers (on-prem or other clouds) — Arc Extension provides management plane integration.

### Install
- From Azure Portal: Arc → Servers → select server → Extensions → + Add → "Azure File Sync"
- Or via az CLI: `az connectedmachine extension create --machine-name <server> --extension-instance-name AzureFileSyncAgent --type "AzureFileSyncAgent" --publisher "Microsoft.AzureFileSyncAgent"`

### Troubleshooting deployment failure
- Check extension status: `az connectedmachine extension show ...`
- Logs on server: `C:\ProgramData\AzureConnectedMachineAgent\Log\`
- Common: server time skewed, network blocked to Arc endpoints

### Telemetry
- Extension events visible in Azure Activity Log
- Query Arc events: `mcp_csswiki_wit_query_by_wiql` not relevant — use Azure Monitor or Activity Log REST API

### Reference
[Azure Arc Extension TSG](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/2030131)

---

## AFS-Arc-SoftwareAssurance — How to check Software Assurance benefits for Azure File Sync on Arc Enabled Servers (Arc enables SA benefit tracking without license server vs paid billing)

### Feature
Customers with Windows Server Software Assurance can run AFS on Arc-enabled WS without paying per-server AFS charge.

### Check status
- Portal → Arc → Server → Properties → "Software Assurance Benefit"
- Or via REST API: GET on the Arc machine resource

### Activate benefit
Customer attests SA eligibility via portal toggle.

---

## AFS-Perf-SlowSync — Azure File Sync Slow Sync Throughput and Bandwidth TSG (telemetry events 7003/7004/7005/7006, Get-StorageSyncNetworkLimit cmdlet, AFSDiag bandwidth config, root cause patterns table)

### Symptom
Slow sync — long delays after file CRUD before replication completes.

### Key signals
| EventId | Type | Description |
|---|---|---|
| 7003 | Upload | Batch upload telemetry (throughput + throttling) |
| 7006 | Upload | Batch upload telemetry (throughput + throttling) |
| 7004 | Download | Batch download telemetry (throughput + throttling) |
| 7005 | Download | Batch download telemetry (throughput + throttling) |

### Investigation steps

#### Step 1 — Validate sync behavior
Confirm delay between file CRUD on server and appearance on cloud (or vice versa).

#### Step 2 — Analyze telemetry events
Filter EventIds 7003/7004/7005/7006 in StorageSync Event Log → look for reduced throughput / throttling signs.

#### Step 3 — Check agent bandwidth limits
```powershell
Get-StorageSyncNetworkLimit
```
Validate configured caps + time-based throttling rules.

#### Step 4 — Inspect local diagnostics
- Windows Event Log → StorageSync channel
- AfsDiag output (registry config + bandwidth)
- Verify network limit config matches expected

#### Step 5 — Correlate findings

| Signal | Expected | Investigation focus |
|---|---|---|
| Telemetry throughput | Matches expected bandwidth | If low → possible throttling |
| Configured limits | Matches design | If restrictive → root cause |
| Diagnostics | Consistent with config | If mismatch → agent/config issue |

### Root cause patterns

| Pattern | Likely cause |
|---|---|
| Low throughput + configured limits | Agent bandwidth throttling |
| Low throughput + no limits | External / network constraint |
| Errors + delays | Sync processing or transient issues |

### Resolution
- Adjust or remove bandwidth limits if throttling unintended
- Validate network capacity + constraints
- Re-test sync after config changes
- Escalate if throughput low without limits OR telemetry inconsistent

### Reference
[Set Azure File Sync network limits](https://learn.microsoft.com/en-us/azure/storage/file-sync/file-sync-server-registration#set-azure-file-sync-network-limits)

---

## AFS-Perf-TSG124 — TSG 124 How to investigate sync performance and progress (upload vs download throughput, initial sync vs ongoing, per-file vs batched perf, customer prestaging best practices)

### Initial sync vs ongoing
- **Initial sync**: bulk upload entire namespace + data → can take hours/days
- **Ongoing**: realtime CRUD propagation (few minutes for most ops)

### Upload throughput formula
Limited by SLOWEST of:
- Server local disk read IOPS
- Network upload bandwidth
- Cloud share IOPS (1000 IOPS / 60 MB/s per share for Standard)
- AFS agent thread count

### Customer prestaging
For initial sync, customer can:
1. Use Robocopy from server to Azure VM in same region (faster network)
2. AzCopy from on-prem to Azure file share
3. Azure Data Box for huge datasets

### Reference
[TSG 124](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/784355)

---

## AFS-Perf-SlowEnumeration — Slow Enumeration of files and folders (cloud tiered files reparse point lookup, SMB traversal cost, registry tuning, prestaging)

### Symptom
`dir` or Explorer browse slow on AFS server with tiered files.

### Cause
Cloud-tiered files have reparse points → directory enumeration costs higher than non-tiered.

### Resolution
- Use **AFS Recall Mode** for high-traversal folders (disable tiering)
- Use registry tuning per [Slow enumeration TSG](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495832)
- Cross-link K § SAF-Win-Explorer-Slow (Windows-side registry workaround)

---

## AFS-Tools-AFSDiag — How to investigate AFSDiag traces (collect AFSDiag via Debug-StorageSync, what it contains event logs telemetry registry CLI, output structure)

### Collect
```powershell
Debug-StorageSync -Output C:\temp\AFSDiag
```

Or older: `afsdiag.ps1` from installation dir.

### Output contains
- Event logs (StorageSync channel + System + Application)
- AFS telemetry events
- Registry values (StorageSync keys)
- AFS PowerShell cmdlet output
- Network config snapshot

---

## AFS-Tools-Dashboards — Access to File Sync Dashboards (ICM dashboards list, ASC equivalents, how to request access)

### Available dashboards
- ICM dashboards (PG-managed): tenant-level + service health
- ASC: SA-level + Sync Group-level
- Power BI dashboard (PG presentations)

### Request access
Via aka.ms/CoreIdentity for specific dashboard entitlements (varies per dashboard).

---

## AFS-Tools-MgmtOps — How to find AFS Mgmt Operations on Registered Server (StorageSync Azure Activity Log filter, API version + correlationId, per-server op history)

### Find mgmt ops
- Portal → Storage Sync Service → Activity Log
- Filter by resource ID of specific Registered Server
- Inspect API call: includes correlationId for log correlation

### Cross-reference with logs
- Server-side: `%ProgramData%\StorageSync\` matched by correlationId

---

## AFS-Tools-DGrepTelemetry — TSG 170 AFS Formatting Server Telemetry Events in DGrep (KailaniSVC namespace, ServerTelemetryEvents, EventId mapping, CorrelationId join with ServerItemResultsEvents)

### Procedure
Jarvis DGrep query:
```
Namespace:  KailaniSVC
Events:     ServerTelemetryEvents
TimeRange:  <issue window>
Filter:     SubscriptionId == <subId> AND/OR ServerName == <name>
```

`EventDescription` field contains structured key-value pairs (parse with regex).

For per-item drill-down: use `CorrelationId` to join with `ServerItemResultsEvents`.

### Reference
[TSG 170](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/784046)

---

## AFS-Tools-CrashDumps — TSG 173 AFS Generating Crash Dumps filesyncsvc (procdump, werfault, registry setup for LocalDumps, memory dump collection)

### Procdump method (manual)
```cmd
procdump -ma -i C:\dumps    # install as JIT debugger
# Reproduce crash
# Dump appears in C:\dumps
```

### LocalDumps registry method (automatic)
Set: `HKLM\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps\FileSyncSvc.exe`
- `DumpFolder` = `C:\dumps`
- `DumpType` = `2` (full dump)
- `DumpCount` = `5`

### Reference
[TSG 173](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/784047)

---

## AFS-Tools-DiagnosticsToggle — TSG 174 AFS Enabling or disabling diagnostics on customer server (Debug-StorageSync enable / disable, logging level control, customer consent required)

### Enable diagnostics
```powershell
Debug-StorageSync -Enable
```

### Disable
```powershell
Debug-StorageSync -Disable
```

### ⚠ Customer consent
Always confirm customer authorization before enabling — diagnostics may collect PII per Microsoft data collection policy.

### Reference
[TSG 174](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/784048)

---

## AFS-Tools-MissingTelemetry — TSG 193 AFS Investigate missing server telemetry or server showing no activity (MonAgentLauncher, GenevaMonitoringAgent state, health channel failure, server not uploading events)

### Symptom
ASC shows server as no recent activity / no events.

### Investigation
1. Check service state: `Get-Service MonAgentHost, GenevaMonitoringAgent` → should be Running
2. Check Geneva channel: `%ProgramData%\AzureMonitorAgent\` logs
3. Network: outbound to Geneva collector endpoints
4. Verify time sync (cert validation)

### Reference
[TSG 193](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/784049)

---

## AFS-Tools-GetShareId — TSG 206 AFS How to get ShareId from SyncGroup and Subscription ID (needed for DGrep correlation, REST API GET StorageSyncServices/syncGroups/cloudEndpoints)

### REST API call
```
GET https://management.azure.com/subscriptions/<subId>/resourceGroups/<rg>/providers/Microsoft.StorageSync/storageSyncServices/<service>/syncGroups/<sg>/cloudEndpoints/<ce>?api-version=2022-09-01
```

Response contains `azureFileShareName` and internal `shareId` used for DGrep filtering.

### Reference
[TSG 206](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/784050)

---

## AFS-Tools-WPT — TSG 227 AFS Windows Performance Toolkit for Customer Servers (wprui, wpa, FileSyncSvc recording profile, analyzing disk IO, CPU, memory traces)

### Use case
Deep perf analysis when standard tools insufficient (CPU spike, memory leak, etc.).

### Collect
```cmd
wprui.exe   # GUI tool
# Or command line:
wpr -start GeneralProfile -filemode
# Reproduce issue
wpr -stop C:\perftrace.etl
```

### Analyze with WPA
```cmd
wpa.exe C:\perftrace.etl
```

### Reference
[TSG 227](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/784052)

---

## AFS-Tools-WinHTTPTraces — TSG 268 AFS Collect WinHTTP traces (netsh trace start scenario InternetClient + SSL + filemode circular, analyzing mgmt or sync channel failures)

### Collect
```cmd
netsh trace start scenario=InternetClient capture=yes report=yes tracefile=C:\winhttp.etl
# Reproduce issue
netsh trace stop
```

### Analyze
- Convert ETL: `netsh trace convert input=C:\winhttp.etl`
- View in Microsoft Message Analyzer or PerfView

### Reference
[TSG 268](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/784053)

---

## AFS-Tools-PETroubleshoot — TSG 372 AFS How to Troubleshoot Private Endpoint failures (PE not resolving, VNET routing blocked, mgmt endpoint still needs public DNS resolution or PE for StorageSync)

### Symptom
After enabling private endpoint, AFS sync stops working.

### Resolution
- AFS uses **two** types of endpoints:
  - **Storage Sync Service** mgmt PE (resource type: `Microsoft.StorageSync`)
  - **SA** data PE (resource type: `Microsoft.Storage`)
- Both must be configured if you want full PE-only
- Verify DNS resolution: `Resolve-DnsName <sa>.file.core.windows.net` should return private IP
- VNET routing: server must be able to reach PE IP

### Reference
[TSG 372](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/784055)

---

## AFS-Tools-SyncCloudEnum — TSG AFS Sync investigation Cloud Enumeration and Upload Session (Cloud change detection job 24h cycle, upload session state machine, investigation via Jarvis EventId mapping)

### Cloud change detection
- Runs **every 24h** on cloud endpoint
- Discovers changes made via REST API / direct SMB on Azure file share
- Customer can trigger manual change detection via Portal

### Upload session state machine
- Init → Discover → Plan → Upload → Complete
- Errors at each stage logged in StorageSync EventLog + Jarvis KailaniSVC

### Reference
[TSG AFS Sync investigation](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/784060)

---

## AFS-EmergingIssues — Current AFS Emerging Issues (v17 server registration fails / v16 low disk space mode bug / MonAgentLauncher + AzureStorageSyncMonitor / FileSyncSvc failed to start / WININET_E_DECODING_FAILED / Access Control Regression / v17 bytes synced metric bug / v15.1 known bug / 0x8000FFFF no system MI found)

### Current (at time of writing)

| Issue | Brief | Status |
|---|---|---|
| AFS 0x8000FFFF no system MI found | After enabling MI on existing sync service | Mitigation: re-create system MI |
| AFS v16 agent low disk space mode bug | False-positive low disk space detection | Workaround: upgrade to v17+ |
| AFS Agent v17 Server Registration ServerRegistration.exe fails | Registration utility regression | Mitigation: use PowerShell Register-AzStorageSyncServer |
| AFS Agent MonAgentLauncher + AzureStorageSyncMonitor | Monitoring agent restart loop | Update to latest agent |
| FileSyncSvc failed to start | Various causes (see TSG) | Check dependencies + .NET version |
| WININET_E_DECODING_FAILED | Sync channel decoding error | Mitigated by network team |
| File Sync Access Control Regression | Sync RBAC enforcement regression | Mitigated |
| File Sync v17 bytes synced metric unexpected increase bug | Metric reporting bug | Cosmetic only — sync actual progress unaffected |
| File Sync Agent v15.1 known bug | Various — upgrade required | Upgrade to v17+ |

Check current Emerging Issues in wiki for latest state.

---

## AF-Errors-QuotaExceeded — Azure File Share QUOTA_EXCEEDED during file access (share capacity full, customer expands share quota via portal or PowerShell — note different from 1816 Not enough quota)

### Symptom
File ops fail with `QUOTA_EXCEEDED`.

### Cause
Share has hit its quota (provisioned size for Premium, configured quota for Standard).

### Resolution
- Portal: SA → File shares → select share → Quota → increase
- PowerShell: `Set-AzStorageShareQuota -Name <share> -Quota <new-GB>`

### Note
Different from Windows error 1816 "Not enough quota is available" — that's about NTFS quota on local disk.

---

## AF-Errors-IOError — Cannot Access File Path / Input/Output Error (disconnected mount, stale handle, server stamp migration, client needs remount)

### Cause
- Mount became stale (server migrated stamps, client didn't notice)
- File handle was open during platform-side event
- Network blip during file access

### Resolution
- Unmount + remount the share
- For Linux: `umount -f /mnt/<share>; mount -t cifs ...`

---

## AF-Errors-InsufficientResources — Status Insufficient Resources (too many concurrent connections, client handle limit 2000 per share, reduce concurrent mounts)

### Cause
- Hit **2000 concurrent open handle limit per share**
- Or hit other scalability limit

### Resolution
- Reduce concurrent connections
- Close idle handles via § AF-HowTo-HandlesClosure
- Use multiple shares to distribute load

---

## AF-Errors-ClientOtherError — Azure Files ClientOtherError (catch-all for client-side errors, usually harmless, XstoreFrontEnd logs show actual cause, mostly expected client disconnect / abort)

### What it means
Catch-all bucket in `XSMBPerfMetric` for client-side errors. Often:
- Client abort (Ctrl+C, network blip)
- Client closed connection mid-operation

Usually **harmless** — backend logs (`XSMBPerfMetric.InternalStatus`) show actual cause if needed.

---

## AF-Errors-RestAPIEmpty — Azure Files RestAPI Empty Value Response (List Shares or List Files returns empty, firewall blocking, invalid SAS or key, null vs not-set)

### Symptom
REST call (e.g., `ListFiles`) returns empty body or `null` values.

### Common causes
- SA firewall blocking caller IP
- SAS token expired
- Invalid key in Authorization header
- Property genuinely null vs not present
- Pagination — check `nextMarker`

### Resolution
- Check Network Watcher for firewall block
- Refresh SAS / regen key
- Inspect raw response with REST client (Postman)

---

## AF-Errors-CopyAlreadyExists — Copy Files File Explorer File Already Exists Error (case sensitivity mismatch Windows vs Azure Files, storage keeps original case on first write)

### Symptom
File Explorer says file already exists when name only differs by case.

### Cause
Azure Files is **case-preserving but case-insensitive**. Two names that differ only by case collide. First name written keeps the case.

### Resolution
- Rename one file with totally different name (not just case)
- Delete + recreate with desired case if needed

---

## AF-Errors-DriveMappedDiffUser — Azure Files Drive Mapped Under Different User (mount persisted in Credential Manager under other account, use cmdkey delete or New-SmbGlobalMapping)

### Symptom
User A sees Z: mapped but can't access. User B previously mapped Z: with own creds.

### Resolution
- User A: `cmdkey /delete:<sa>.file.core.windows.net` to clear stale entry
- Mount under current user OR use `New-SmbGlobalMapping` for system-wide
- Reboot to clear OS-level state if stuck

---

## AF-Errors-EmptyMetricsDim — Empty File Share Metrics Dimension In Portal (no data on File Share Name dimension, customer on pre-2018 account, share metrics not enabled, filter by tier needed)

### Cause
- Pre-2018 SAs may not report per-share dimensions
- Diagnostic settings not enabled
- Filter by share name returns empty if filter incorrect

### Resolution
- Enable diagnostic settings on SA
- Verify filter format (exact share name match)
- For old SAs, may need re-create as v2

---

## AF-Errors-UnableDeleteFile — Unable to delete file in Azure File Share (file open handle, lease, readonly attribute, retention lock, use AzFileShareHandlerClose)

### Common causes
- Open file handle from another client
- Read-only file attribute
- Retention lock (immutable storage)
- ACL deny on delete

### Resolution
- List handles: `Get-AzStorageFileHandle -ShareName <share> -Path <file>`
- Force-close: `Close-AzStorageFileHandle -ShareName <share> -Path <file> -HandleId <id> -CloseAll`
- Remove read-only: `attrib -R <file>`
- Check NTFS ACL for Delete perm

---

## AF-HowTo-HandlesClosure — Azure Files Handles Closure (how to list and force-close handles, az storage share list-handle, az storage share close-handle, Invoke-AzFileShareHandle)

### List handles
```powershell
Get-AzStorageFileHandle -ShareName <share> -Path <path> -Recursive
```

```cli
az storage share list-handle --account-name <sa> --name <share> --path <path>
```

### Force-close
```powershell
Close-AzStorageFileHandle -ShareName <share> -Path <path> -HandleId <handleId>
# Or all:
Close-AzStorageFileHandle -ShareName <share> -Path <path> -CloseAll
```

```cli
az storage share close-handle --account-name <sa> --name <share> --path <path> --handle-id <id>
```

---

## AF-Errors-UnableCreateShare — Unable to create file share (SA kind incompatible BlobStorage not supported, quota exceeded, region not supported, client permissions missing)

### Common causes
- SA kind `BlobStorage` (NOT supported for Files — must be `Storage`, `StorageV2`, `FileStorage`)
- Hit subscription quota for shares
- Region doesn't support share type (Premium FileStorage limited to certain regions)
- Caller missing `Microsoft.Storage/storageAccounts/fileServices/shares/write`

### Resolution
- Check SA kind, create new SA if needed
- Check subscription quota
- Verify region availability
- Grant `Storage Account Contributor` to caller

---

## AF-HowTo-FilesVsBlob — Azure Files versus Blob (Protocol SMB/NFS/REST vs REST-only, POSIX vs flat namespace, scenario decision matrix shared FS vs object store)

### Files vs Blob

| Dimension | Azure Files | Azure Blob |
|---|---|---|
| Protocol | SMB, NFS, REST | REST only |
| Namespace | POSIX hierarchical | Flat (with virtual hierarchy via /) |
| Use case | Shared file system | Object storage |
| Mount as drive | Yes | No (with workarounds) |
| File ops semantics | POSIX | Object-store semantics |
| Concurrent writes | SMB locking | Blob lease / no lock |
| Cost/GB | Higher | Lower |
| Snapshot | Per-share | Per-blob |
| Tiering | Premium/Standard | Hot/Cool/Cold/Archive |

### When to use Files
- Lift-and-shift apps needing SMB
- FSLogix profiles
- Shared config / app data needing POSIX

### When to use Blob
- Backup / archive
- Object storage for apps
- Streaming media
- Data lake (with ADLS Gen2)

---

## AF-HowTo-Win7-WS2008 — Azure Files Windows 7 + Windows Server 2008 R2 (KB3114025 required, SMB 2.1 only, Secure Transfer Required must be disabled or TLS 1.2 cyphers needed)

### Constraints
- Only SMB 2.1 (no SMB 3.x → no encryption-in-transit)
- Secure Transfer Required must be **disabled** on SA
- KB3114025 required for handle perf

### Migration path
Upgrade clients to Win 8.1+ / WS 2012 R2+ for SMB 3.x.

---

## AF-HowTo-MountVHD — Mount VHD on FileShare (store VHDX on Azure Files, mount as local disk, workaround for app compat issues, latency tradeoff)

### Use case
App can't handle SMB share semantics → store VHD/VHDX on Azure Files, mount as virtual disk locally.

### Procedure
1. Mount Azure file share to drive letter Z:
2. Create or copy VHDX to `Z:\app.vhdx`
3. Mount VHDX: `Mount-VHD -Path Z:\app.vhdx -Passthru | Get-Disk | Initialize-Disk ...`
4. App accesses files via mounted local drive letter

### Tradeoff
- Latency increases due to extra layer (Azure Files → VHD → app)
- Lose Azure Files cloud-native features (snapshot at file level)

---

## AF-HowTo-MountSpecificUserGroup — Mounting Azure File Share using a specific user and group (uid + gid + dir_mode + file_mode mount options for Linux CIFS, username + password for Windows NET USE)

### Linux CIFS
```bash
mount -t cifs //<sa>.file.core.windows.net/<share> /mnt/<share> \
  -o vers=3.0,username=<sa>,password=<key>,dir_mode=0755,file_mode=0644,uid=1000,gid=1000,serverino
```

### Windows NET USE
```cmd
net use Z: \\<sa>.file.core.windows.net\<share> /User:Azure\<sa> <key>
```

---

## AF-HowTo-SMBSecurity — Security settings for SMB protocols in Azure File Shares (SMB 3.0/3.1 version, SMB Channel Encryption AES-128-GCM/AES-256-GCM, Authentication Methods NTLMv2 vs Kerberos, Profile Max Compatibility)

### Configurable settings (Portal → SA → File shares → Security)
- **SMB Protocol Version**: 3.0 / 3.1.1 minimum
- **SMB Channel Encryption**: AES-128-CCM / AES-128-GCM / AES-256-GCM
- **Authentication Methods**: NTLMv2 / Kerberos
- **Kerberos Ticket Encryption**: AES-128 / AES-256 / RC4 (legacy)
- **Profile**: Maximum Compatibility (all enabled) / Maximum Security / Custom

### For TS, set Profile = Maximum Compatibility
- Adjust narrower after issue resolved per customer security policy

---

## AF-HowTo-CheckIOPS — Check IOPS on Azure File Share (ASC Performance tab, Azure Monitor, Shoebox MDM, per-share limits 1000 IOPS Standard or provisioned IOPS Premium)

### Limits
- **Standard**: 1000 IOPS per share, 60 MB/s
- **Premium**: provisioned, scales with quota
- **Provisioned v2** (newer model): decoupled IOPS + bandwidth

### Check current IOPS
- ASC → SA → Performance tab → File service filter → Transactions/Sec
- Azure Monitor → SA Metrics → Transactions per share
- XPortal Shoebox API Investigation (internal)

---

## AF-HowTo-Premium — Premium Files overview (FileStorage account kind, SSD-backed, provisioned IOPS + lower latency, baseline + burst IOPS, throughput formulas)

### Premium Files characteristics
- **Account kind**: `FileStorage`
- **SSD-backed**
- **Provisioned model** — pay for capacity, get scaled IOPS + bandwidth
- **Lower latency** than Standard (typically 1-2 ms server latency)

### IOPS formula (Premium v1)
- **Baseline IOPS** = max(400, 1 IOPS × ProvisionedGiB) up to 100K per share
- **Burst IOPS** = max(4000, 3 × Baseline)
- **Throughput** = 60 + 0.06 × ProvisionedGiB MB/s

### Reference
[Premium Files](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/495813)

---

## AF-HowTo-LargeFileShare — Large File Share Overview + HowTo (100 TiB, up to 10000 IOPS, LRS or ZRS only, no GRS/GZRS, enable via portal or PowerShell, no disable after enable)

### Capabilities
- Up to **100 TiB capacity**
- Up to **10000 IOPS**
- Up to **300 MB/s throughput**

### Restrictions
- **LRS or ZRS only** — no GRS / GZRS
- Cannot disable once enabled
- Cannot convert to GRS/GZRS after enabling

### Enable
- Portal: SA → Configuration → Large file shares → Enabled
- PowerShell: `Update-AzStorageAccountNetworkRuleSet` (or similar)
- CLI: `az storage account update --enable-large-file-share`

---

## AF-HowTo-HotCoolTiers — Hot + Cool Tiers for Azure Files (TransactionOptimized vs Hot vs Cool vs Archive not available on Files, billing implications, tier change impact)

### Available tiers (Standard only)
- **TransactionOptimized** — high IOPS / low capacity cost — default
- **Hot** — balanced
- **Cool** — low capacity cost / higher transaction cost

### Note
- **Archive tier NOT available on Azure Files** (only Blob)
- Premium Files has separate model (provisioned)

### Tier change impact
- Affects billing immediately
- Transaction cost differs (Cool = higher per-tx, capacity = lower)
- No data movement / migration

---

## AF-HowTo-OSRestrictions — OS Restrictions for Azure Files (supported Windows versions, Linux distros, MacOS, SMB 2.1 minimum vs SMB 3.x for cross-region on-prem, Secure Transfer Required)

### Minimum supported
- **Windows**: Win 7 / WS 2008 R2 + KB3114025 (SMB 2.1)
- **Linux**: kernel 4.11+ for SMB 3.x encryption; cifs-utils 5.5+
- **MacOS**: 10.13+

### For cross-region or on-prem clients
- Must have **SMB 3.x** with encryption
- Secure Transfer Required = ON forces SMB 3.x

### Reference
[OS Restrictions](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/496158)

---

## AF-HowTo-FAQ — Azure Files FAQ (common questions decision matrix for most frequently asked customer questions)

### Top FAQs
- "Can I encrypt at rest?" → Yes, SSE by default + CMK optional
- "Can I use my own DNS?" → Yes via PE + private DNS zone
- "Max file size?" → 4 TiB per file
- "Max share size?" → 5 TiB default, 100 TiB with Large File Share
- "Snapshot retention max?" → 200 snapshots per share
- "REST + SMB concurrent?" → Yes
- "Backup options?" → Azure Backup, snapshot, third-party tools

Cross-link [Azure Files FAQ public docs](https://docs.microsoft.com/en-us/azure/storage/files/storage-files-faq).

---

## AF-HowTo-AuditFileShare — Audit File Share (Diagnostic Settings for audit logs, Azure Files audit via StorageRead / StorageWrite / StorageDelete log categories, retention)

### Setup
1. SA → Diagnostic settings → + Add
2. Categories:
   - `StorageRead`
   - `StorageWrite`
   - `StorageDelete`
3. Destination: Log Analytics OR Storage Account OR Event Hub
4. Configure retention

### Query audit logs in Log Analytics
```kusto
StorageFileLogs
| where TimeGenerated > ago(1h)
| where OperationName in ("GetFile", "PutFile", "DeleteFile")
| project TimeGenerated, OperationName, Uri, StatusText, CallerIpAddress, UserAgentHeader
```

---

## AF-HowTo-SMBMultichannel — SMB Multichannel (Premium Files only, higher throughput per client, enable on SA, client must have multiple NICs or RSS, troubleshoot not active)

### Feature
- Premium Files only
- Single client gets multi-connection throughput boost
- Client must have multiple NICs or RSS (Receive Side Scaling)

### Enable on SA
```powershell
Update-AzStorageFileServiceProperty -ResourceGroupName <rg> -StorageAccountName <sa> -SmbMultichannelEnabled $true
```

### Verify active on client
```powershell
Get-SmbMultichannelConnection
```

### Troubleshoot not active
- Verify client OS supports (WS 2016+ / Win 10+)
- Multiple NICs or RSS-capable single NIC
- SMB 3.0+ negotiated

---

## AF-HowTo-UDKSAS — User Delegation SAS for Azure Files (uses AAD credentials instead of key, how to create via Azure CLI, troubleshooting permission denied or signature invalid)

### Use case
SAS token signed with AAD user delegation key (not SA key) — for short-lived, fine-grained, audit-friendly delegation.

### Create UDK SAS
```cli
az storage share generate-sas \
  --account-name <sa> \
  --name <share> \
  --permissions r \
  --expiry 2026-12-31T00:00:00Z \
  --as-user --auth-mode login
```

### Common issues
- "Permission denied" → caller AAD principal missing `Storage File Data Privileged Reader/Contributor`
- "Signature invalid" → clock skew, expired UDK key
- UDK key rotates every 7 days

---

## AF-Premium-V2 — Azure Files Provisioned V2 model overview + troubleshooting (Provisioned IOPS + bandwidth decoupled from capacity, new billing model, limits, changes vs V1)

### V2 vs V1 differences
| Aspect | V1 (Premium) | V2 (Provisioned V2) |
|---|---|---|
| IOPS | Scales with quota | Independently provisioned |
| Bandwidth | Scales with quota | Independently provisioned |
| Capacity | Provisioned | Provisioned (separate from IOPS) |
| Billing | Per-GB | Per-GB + per-IOPS + per-throughput |

### Use case
Customer needs lots of IOPS but small capacity (e.g., DB temp files, FSLogix metadata).

### Troubleshooting
- Verify limits provisioned correctly
- Monitor actual usage vs provisioned
- Reference [Provisioned V2 Troubleshooting](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/2030093)

---

## AF-Zonal-HowTo — How to create Azure File Shares with Zonal Placement (Premium LRS only, specific region list, pin to AZ, align VM AZ, cross-link K Cross-Zone Traffic detection)

### Use case
Cross-link from K § SA-Perf-AzureFiles-Backend Cross-Zone Traffic detection — pin SA to AZ to reduce latency.

### Eligibility
- **Premium LRS only**
- Supported regions (18-region list — see K § SA-Perf-AzureFiles-Backend)
- Customer signs up via [Zonal Placement preview form](https://forms.office.com/Pages/ResponsePage.aspx?id=v4j5cvGGr0GRqy180BHbR3YF4IzZBh5DsKmgV8Q2xEFUN1FMVVBTWkFPWk5TSDhIWTFJSzFDSzNTSyQlQCN0PWcu)

### Create
After feature enabled on subscription:
- Portal: SA → Create with Zone parameter
- ARM: `availabilityZone` property on SA resource

---

## AF-Zonal-TSG — Azure File Share Zonal Placement TSG (eligibility check, portal config, verification, customer misuse non-eligible config)

### Common issues
- Customer not Premium LRS → not eligible
- Customer in non-supported region → not eligible
- Customer didn't sign up via form → feature not enabled on sub
- Customer expects zonal placement but configured GRS — mutually exclusive

### Resolution
- Verify eligibility before configuration
- Submit signup form
- Wait for feature enablement on sub (manual today)

---

## AF-ManagedFileShares — Managed File Shares overview + troubleshooting + Query Logs (newer Managed vs classic file shares, feature differences, per-share management API)

### Feature
Newer storage model — Managed File Shares are managed as top-level Azure resources (not nested under SA → File services → shares).

### Differences from classic
- Per-share API + RBAC + lifecycle management
- Decoupled from SA — share can live independently
- Different log format

### Query Managed File Share Logs
- New log table in Log Analytics: `AzureManagedFileShareLogs`
- Different schema than classic `StorageFileLogs`

### Troubleshooting
[Managed File Share Troubleshooting](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/2030218)

---

## AF-CSIDriver-v2 — Azure Disk CSI Driver v2 (AKS PVC using Azure Files, mounting via CSI driver, upgrade from v1, troubleshooting PVC mount failures)

### Use case
AKS uses CSI driver to mount Azure Files as Persistent Volumes (PVs / PVCs).

### Driver options
- **azurefile-csi-driver** (v1, deprecated)
- **azurefile-csi-driver-v2** (current)

### Common issues
- PVC stuck in Pending → check storage class + CSI driver pods running
- Mount failure on pod → check share exists + RBAC + node network reach
- Slow mount → cross-link K § SA-Perf-AzureFiles-Backend

---

## AF-EmergingIssues — Azure Files Emerging Issues umbrella (Network credential prompt not loading mount UNC, RBAC SMB TrackingID_2MP7 JP0, Azure Files Identity Emerging)

### Current Files-All emerging
- Network credential prompt not loading when mounting via UNC path (Win bug)
- RBAC SMB TrackingID_2MP7 JP0 — share-level RBAC propagation regression
- Azure Files Identity issues (rolling list)

Check wiki Emerging Issues area for current state before triaging long-running issues.

---

## AF-Mount-Win-PSDriveNoPersist — Azure File Share Unable to access via File Explorer when mounted with PowerShell `New-PSDrive` missing `-Persist` option (PowerShell session-only drive vs persistent network drive)

### Symptom
- Mount via PowerShell `New-PSDrive` succeeds → drive accessible from PowerShell session
- File Explorer access fails OR shows Used/Free GB = blank
- After session close: drive gone

### Cause
`New-PSDrive` without `-Persist` creates a **PowerShell session-only drive** that:
- Exists only in current PowerShell session
- Disappears when session ends
- NOT visible in File Explorer / other apps / future sessions

The Azure Portal connection script includes `-Persist` by default — only an issue if customer manually removed it.

### Resolution

**Option 1**: Use `-Persist` with PowerShell
```powershell
New-PSDrive -Name Z -PSProvider FileSystem `
    -Root "\\<sa>.file.core.windows.net\<share>" -Persist
```

**Option 2**: Use `net use` (always persistent unless `/persistent:no`)
```cmd
net use Z: \\<sa>.file.core.windows.net\<share> <key> /user:<sa>
```

### Cross-link
[Mount SMB Azure file share on Windows](https://learn.microsoft.com/en-us/azure/storage/files/storage-how-to-use-files-windows?tabs=azure-portal).

---

## AF-Perf-SlowAccessUNCPath — Azure Files Slow Access via UNC Path (Windows Client for NFS feature causes nfsclnt.exe port 111 sunrpc retries — 5+ min open via UNC, mounted drive works fine)

### Symptom
- Customer opens file via UNC `\\<sa>.file.core.windows.net\<share>\file.xlsx` → takes 5+ minutes
- Same file via mounted drive letter (e.g., Z:) opens fast
- Affects Office apps (Excel, Word, PowerPoint) and Explorer
- May intermittently fail to connect

### Cause
**Windows "Client for NFS" feature installed.** When accessing UNC, Windows tries NFS first via:
- `nfsclnt.exe` repeatedly retries port **111 (sunrpc)**
- Azure Files storage sends RST on port 111 (NFS not exposed for SMB shares)
- nfsclnt.exe keeps retrying → 5+ min delay before SMB fallback

### Investigation
- Procmon log filtered by storage IP → `nfsclnt.exe` continuously trying port 111 sunrpc
- WireShark → TCP retransmissions on port 111 + RST from storage

### Resolution
**Remove "Client for NFS" Windows feature + restart**:
```powershell
Remove-WindowsFeature -Name NFS-Client -Restart
```

Or via Server Manager → Remove Roles and Features → uncheck Client for NFS.

After restart, UNC access works correctly.

### Cross-link
- If "Client for NFS" not installed and Office files still slow → § AF-Errors-SlowOpenOffice (cross-link K § SAF-Win-Explorer-Slow registry workaround)
- [files-nfs-protocol support reference](https://learn.microsoft.com/en-us/azure/storage/files/files-nfs-protocol#support-for-azure-storage-features)

---

## AF-Identity-Coexistence — Coexistence feature: hybrid identity client accessing both AD DS and Entra Kerberos storage accounts (host-to-realm mapping via Intune CSP / GPO / `ksetup` registry, troubleshooting workflow)

### Scope
Hybrid scenario where the **same client** must access:
- Some SAs joined to **on-prem AD DS**
- Other SAs configured for **Microsoft Entra Kerberos** (cloud Kerberos)

Without coexistence configuration, client may request tickets from the WRONG KDC → auth fails even with correct share config.

### Symptom
Users can't access AD DS-joined Azure Files shares from machines configured for Entra Kerberos. Client retrieves Kerberos ticket from `kerberos.microsoft.com` instead of on-prem DC → AD DS auth fails.

### How coexistence works
Client needs **host-to-realm mappings**:
- `<sa-adds>.file.core.windows.net` → on-prem AD realm (e.g., `CONTOSO.LOCAL`)
- `<sa-entra>.file.core.windows.net` → Entra Kerberos realm (`AADKERBEROS.REALM`)

Windows then requests tickets from the appropriate KDC per SA.

### Verify client configuration

#### Group Policy
`Computer Configuration → Administrative Templates → System → Kerberos → Define host name-to-Kerberos realm mappings`
Should be Enabled and contain correct mappings.

#### Registry
```cmd
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Kerberos\Domain_realm
```
Should display configured mappings.

### Configure host-to-realm mappings (3 supported methods)

#### Method 1: Intune Policy CSP
Configure `Kerberos/HostToRealm` → add entry per AD DS-joined SA.

#### Method 2: GPO
Enable `Define host name-to-Kerberos realm mappings` → specify each SA → correct realm.

#### Method 3: `ksetup` registry
```cmd
ksetup /addhosttorealmmap <sa>.file.core.windows.net <REALMNAME>
```
Example: `ksetup /addhosttorealmmap oldstore123.file.core.windows.net CONTOSO.LOCAL`

### Troubleshooting workflow
1. Access issue reported
2. Check if client is configured for Entra Cloud Kerberos
3. `klist` → verify if there's a TGS ticket for the failed SA
   - **NO ticket** → check Realm-to-Host mapping under `HKLM\SYSTEM\CurrentControlSet\Control\Lsa\Kerberos\HostToRealm`
   - **YES ticket** → coexistence configured correctly; check SMB session setup from backend SMB / Jarvis logs

### Reference
[Configure coexistence with on-premises AD DS](https://learn.microsoft.com/en-us/azure/storage/files/storage-files-identity-auth-hybrid-identities-enable?tabs=azure-portal%2Cregkey#configure-coexistence-with-storage-accounts-using-on-premises-ad-ds)

---

## AF-Identity-SMBWindowsPermissionModel — SMB Windows Permission Model TSG (3-layer permission model deep dive: Azure RBAC mgmt + Storage File Data SMB Share RBAC + NTFS ACL, RoleAssignmentScheduleInstances reading, sysinternals AccessChk troubleshooting)

### Scope
Definitive deep dive on the **3-layer SMB Windows permission model** for Azure Files. Referenced from every Identity auth TSG. Use when customer hits "access denied" despite plausible config.

### 3-layer model (all must pass)
| Layer | Role examples | Scope | Tool |
|---|---|---|---|
| **1. Azure RBAC** (mgmt plane) | `Reader`, `Contributor`, `Owner`, `Storage Account Contributor` | Subscription / RG / SA | `Get-AzRoleAssignment` |
| **2. Storage File Data SMB Share RBAC** (data plane) | `Storage File Data SMB Share Reader / Contributor / Elevated Contributor` | SA or per-share | `Get-AzRoleAssignment -Scope <share-resource-id>` |
| **3. NTFS ACL** (file/folder ACL) | Read / Write / Modify / Full Control | Per file/folder | `icacls Z:\path`, `Get-Acl Z:\path` |

### Common matrix
- Customer can mount but can't read files → Layer 2 `Reader` role missing
- Can read but can't write → Layer 2 `Contributor` role missing
- Can write but can't change ACLs → Layer 2 `Elevated Contributor` role missing
- All Azure roles correct but Access Denied → Layer 3 NTFS ACL deny

### Reading current role assignments (per-user, per-scope)
```powershell
# All assignments at SA scope for a user
Get-AzRoleAssignment -SignInName <user@domain> -Scope /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/<sa>

# All assignments per share
Get-AzRoleAssignment -Scope /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/<sa>/fileServices/default/fileshares/<share>
```

### Sysinternals AccessChk (NTFS ACL effective rights)
```cmd
accesschk.exe <user> Z:\<path>
# Shows effective permissions per the user's group memberships + NTFS ACLs
```

### Troubleshooting flow
1. Verify Layer 1: caller is at least Reader at SA scope
2. Verify Layer 2: appropriate Storage File Data SMB Share role on share (or SA)
3. Wait 5-10 min after role change (AAD propagation)
4. Klist purge + remount
5. Verify Layer 3: `icacls Z:\path` shows expected ACEs
6. If still failing: file-level audit via `auditpol` to see WHO Windows says is being denied

### Role propagation troubleshooting
- AAD changes: usually 5-10 min
- Stuck > 30 min → check `RoleAssignmentScheduleInstances` REST API for stale assignment OR Conditional Access conflict
- Force AAD sign-out / sign-in to refresh client token

---

## AF-Identity-Diagnostic-DebugAzStorageAccountAuth — Diagnostic tool: `Debug-AzStorageAccountAuth` PowerShell cmdlet (FIRST step for AD DS or Entra Kerberos auth issues, basic checks runs with logged-on AD user, AzFilesHybrid v0.1.2+, PowerShell 5.1, .NET 4.7.2+ Az 2.8.0+ Az.Storage 4.3.0+)

### Scope
Foundation diagnostic — should be **FIRST step** for any AD DS or Entra Kerberos auth issue.

### Scenarios supported
- ✅ On-prem AD DS authentication
- ✅ Microsoft Entra Kerberos for hybrid user identities
- ❌ **Entra DS** (Azure AD DS) accounts NOT supported — manual validation required

### Prerequisites
- .NET Framework 4.7.2+
- Azure PowerShell Az module 2.8.0+ + Az.Storage 4.3.0+
- ActiveDirectory PowerShell module
- AzFilesHybrid v0.1.2+
- **PowerShell 5.1** on device joined to on-prem AD DS

### Setup
1. Download + unzip [AzFilesHybrid releases](https://github.com/Azure-Samples/azure-files-samples/releases)
2. Open admin PowerShell:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope CurrentUser
   ```
3. Navigate to unzipped folder:
   ```powershell
   .\CopyToPSPath.ps1
   Import-Module -Name AzFilesHybrid
   ```

### Execution (must run as AD user with Owner perm on SA)
```powershell
# Non-admin PowerShell session
Connect-AzAccount   # sign in as hybrid identity to test

$ResourceGroupName = "<rg>"
$StorageAccountName = "<sa>"

Debug-AzStorageAccountAuth `
    -StorageAccountName $StorageAccountName `
    -ResourceGroupName $ResourceGroupName `
    -Verbose
```

### Filter to specific checks
```powershell
# Only share-level RBAC checks
Debug-AzStorageAccountAuth `
    -Filter CheckSidHasAadUser,CheckUserRbacAssignment `
    -StorageAccountName $StorageAccountName `
    -ResourceGroupName $ResourceGroupName

# Only file-level NTFS ACL check (need mounted share)
Debug-AzStorageAccountAuth `
    -Filter CheckUserFileAccess `
    -StorageAccountName $StorageAccountName `
    -ResourceGroupName $ResourceGroupName `
    -FilePath "Z:\example.txt"
```

### Reference
- [Self-diagnostics steps](https://learn.microsoft.com/en-us/troubleshoot/azure/azure-storage/files/security/files-troubleshoot-smb-authentication?tabs=azure-portal#self-diagnostics-steps) (full list of checks)

---

## AF-Identity-Diagnostic-FiddlerKerberos — Diagnostic tool: Fiddler with `Kerberos.NET` extension for Entra Kerberos HTTPS-over-KDC-Proxy debugging (Wireshark/netsh can't see encrypted traffic; Fiddler decrypts HTTPS; klist get cifs/<SA>.file.core.windows.net + inspect ErrorCode in Kerberos response)

### Scope
**Microsoft Entra Kerberos uses HTTPS for KDC requests** (KDC Proxy scheme). Wireshark / netsh capture see only encrypted TCP — **must use Fiddler** to inspect Kerberos request/response.

### Setup
1. Download + install [Fiddler Classic](https://www.telerik.com/download/fiddler/fiddler4)
2. Install [Kerberos.NET Fiddler extension](https://github.com/dotnet/Kerberos.NET/releases) (run `setup.exe` — silent install)
3. Open Fiddler as **admin/elevated**
4. Tools → Options:
   - ✅ Decrypt HTTPS traffic
   - ✅ Ignore server certificate errors
   - Accept Fiddler cert add/trust prompts
5. **Restart computer** to apply new settings

### Debugging
1. Open Fiddler as admin
2. CMD: `klist get cifs/<sa>.file.core.windows.net`
3. In Fiddler trace → look for requests to Entra ID → click → view Kerberos tab (request + response)
4. Inspect `ErrorCode` in response (e.g., empty password on service principal)
5. Use `Client Request ID` + Timestamp from response → engage Entra ID Support Team with these IDs

### Troubleshooting Scenario 1: HTTPS traffic still not decrypted
- Tools → Options → HTTPS → Actions → Reset All Certificates
- Wait ~20s
- Restart Fiddler → retry

### Troubleshooting Scenario 2: `klist failed 0xc000005e/-1073741730 / Error 0x51f`
Fiddler proxy settings stuck after process exit. Cleanup:
```cmd
netsh winhttp reset autoproxy
netsh winhttp reset proxy
```
Then delete subentry with port `:8888` from:
`HKLM\SYSTEM\ControlSet001\Services\iphlpsvc\Parameters\ProxyMgr`

Restart machine + retry.

---

## AF-Identity-Diagnostic-Misc — Misc Identity diagnostic tools (Check Valid SID / Check Domain Joined / Check SA Service Principal Name / Check Kerberos Ticket / Get Entra Request ID / Collect Network Trace for domain auth)

### Quick-reference toolkit (Identity How-Tos)

#### Check user/group has a valid SID
```powershell
([System.Security.Principal.NTAccount]"<DOMAIN>\<user>").Translate([System.Security.Principal.SecurityIdentifier]).Value
```
If translation fails → user/group doesn't exist OR not synced to AAD.

#### Check if client is domain-joined
```cmd
dsregcmd /status
# Look for: DomainJoined : YES / AzureAdJoined : YES / Hybrid
```
Or:
```cmd
nltest /dsgetdc:<domain>     # query DC
systeminfo | findstr /B "Domain"
```

#### Check Azure Storage Account Service Principal Name (SPN)
```powershell
# From domain-joined client
setspn -L <SA-computer-object-name>
# Should show: cifs/<sa>.file.core.windows.net AND HOST/<sa>.file.core.windows.net
```

#### Check Kerberos Ticket
```cmd
klist            # list all tickets
klist purge      # clear all tickets
klist get cifs/<sa>.file.core.windows.net   # request new ticket
```

#### Get Entra Request ID from Entra Kerberos ticket request
After running `klist get cifs/<sa>.file.core.windows.net`:
- Capture HTTPS trace via Fiddler (§ AF-Identity-Diagnostic-FiddlerKerberos)
- Entra response includes `Client Request ID` header + Timestamp
- Use these to engage Entra ID Support for AAD-side investigation

#### Collect network trace for Azure Files domain authentication issues
```cmd
netsh trace start scenario=NetConnection capture=yes report=yes tracefile=C:\authtrace.etl
# Reproduce mount/auth issue
netsh trace stop
# Convert ETL to readable: netsh trace convert input=C:\authtrace.etl
```
Open in Microsoft Message Analyzer or Wireshark for SMB/Kerberos packet analysis.

For Entra Kerberos HTTPS traffic specifically → use Fiddler (Kerberos request is encrypted HTTPS, netsh sees only TCP).

---

## AF-Identity-StepByStep-AADJ-HAADJ — Step-by-step setup: AADJ and HAADJ clients accessing ADDS-joined Azure File Shares (hybrid storage with AAD-joined / hybrid-joined clients, configure Realm-To-Host mapping or use Entra Kerberos with on-prem AD)

### Scope
Setup guide for the scenario where:
- Client is **AAD-joined** or **hybrid AAD-joined**
- Storage Account is joined to **on-prem AD DS** (not Entra Kerberos)
- Customer wants the AADJ/HAADJ client to access the AD DS-joined share

### Two approaches

#### Approach 1: Configure Coexistence (client-side host-to-realm mapping)
See § AF-Identity-Coexistence for full procedure. Add mapping:
```
<sa>.file.core.windows.net → ON-PREM-AD-REALM.LOCAL
```
Now AADJ/HAADJ client's Kerberos request for that SA goes to on-prem AD DC instead of `kerberos.microsoft.com`.

#### Approach 2: Migrate SA to Entra Kerberos
If feasible, instead of forcing coexistence:
1. Enable Entra Kerberos on SA (alongside AD DS — yes, both can coexist on same SA in some configs)
2. AADJ/HAADJ client uses Entra Kerberos automatically
3. Lift restriction over time

### Prereqs for Coexistence approach
- AADJ/HAADJ client has network reach to on-prem AD DC
- On-prem AD trusts the hybrid user identity
- User account synced to AAD via AAD Connect

### Verification
```cmd
klist purge
net use Z: \\<sa>.file.core.windows.net\<share>
klist            # should show TGS for cifs/<sa>... with on-prem realm
```

### Cross-link
- § AF-Identity-Coexistence (the mechanism)
- § AF-Identity-AADKerb-Hybrid-Flow (Entra Kerberos hybrid alternative)

---

## AFS-Sync-CertRevocationFix — AFS server registration / sync fails with certificate revocation (`CRYPT_E_NO_REVOCATION_DLL` "No installed or registered DLL was found that was able to verify revocation"), seen on Windows Server 2012 + Agent v17.3 — registry fix at `HKLM\SOFTWARE\Microsoft\Cryptography\OID\EncodingType 1\CertDllVerifyRevocation\DEFAULT\Dll = cryptnet.dll`

### Symptom
- AFS server registration shows security alert: "Revocation information for the security certificate for this site is not available. Do you want to proceed?"
- Or sync fails to validate AFS service cert revocation
- Observed on **Windows Server 2012** with **Agent Version 17.3**

### Cause
**`CRYPT_E_NO_REVOCATION_DLL`** — no DLL registered to verify cert revocation. The cryptnet.dll registry entry is missing or corrupted.

### Mitigation
1. Open `regedit.exe`
2. Navigate to:
   ```
   HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Cryptography\OID\EncodingType 1\CertDllVerifyRevocation\DEFAULT
   ```
3. Check for value:
   - **Name**: `Dll`
   - **Type**: `REG_MULTI_SZ`
   - **Data**: `C:\Windows\System32\cryptnet.dll`
4. If missing or wrong → recreate with above values
5. Verify `cryptnet.dll` exists on disk
6. Retry registration / sync

### Cross-link
- For tiered-file recall cert revocation issues → § AFS-Tiering-UnableRecallCertRev (different issue, file-recall-time validation)
- For server cert binding issues → § AFS-Tiering-ServerCertIssues

---

## AFS-Tools-EnableAuditing — TSG AFS Enable Files and Folder Auditing on Windows Server (Windows Audit policy + SACL on AFS root for who-deleted-this-file investigation, registry GUID for FileSystem events, Security Event Log Event IDs 4663+4660+4656)

### Use case
"Who deleted this file?" / "Who modified this file?" investigation on AFS-synced server. Standard Windows audit policy works for AFS-tracked files (StorageSync.sys filter doesn't interfere).

### Setup

#### Step 1 — Enable audit policy
```cmd
auditpol /set /subcategory:"File System" /success:enable /failure:enable
auditpol /set /subcategory:"Handle Manipulation" /success:enable /failure:enable
```

#### Step 2 — Configure SACL on AFS root folder
```powershell
$acl = Get-Acl "D:\AFS-data"
$auditRule = New-Object System.Security.AccessControl.FileSystemAuditRule(
    "Everyone",
    "Delete,WriteData,AppendData,WriteAttributes,WriteExtendedAttributes",
    "ContainerInherit,ObjectInherit",
    "None",
    "Success,Failure")
$acl.AddAuditRule($auditRule)
Set-Acl "D:\AFS-data" $acl
```

#### Step 3 — Review Security Event Log
Filter by Event IDs:
- **4663** — Object access (read/write/delete)
- **4660** — Object deleted
- **4656** — Handle requested (precursor to ops)

Each event includes:
- `Subject` — who performed
- `Object Name` — path
- `Accesses` — what perms

### ⚠ Performance impact
Auditing all ops generates LOTS of events. Limit SACL scope to specific folders + specific permissions for production use.

### Reference
[TSG AFS Enable files+folder Auditing](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/784057)

---

## AFS-Tools-KernelDump — TSG AFS Getting Kernel Dump for Investigation (System dump for `StorageSync.sys` filter or driver-level investigation, NotMyFault sysinternals + crashdump registry config + reproduce + collect MEMORY.DMP for PG)

### Use case
AFS hang at kernel level OR `StorageSync.sys` filter suspected of corruption / lock / driver issue. PG requires kernel dump (not user-mode process dump).

### Setup

#### Configure full memory dump
1. System → Properties → Advanced → Startup and Recovery → Settings
2. Write debugging information → **Complete memory dump**
3. Dump file location: `%SystemRoot%\MEMORY.DMP` (default)
4. ✅ Overwrite any existing file
5. Restart not required for config; required if dump file location changed and need pagefile resize

#### Trigger dump via NotMyFault (Sysinternals)
1. Download [NotMyFault64.exe](https://learn.microsoft.com/en-us/sysinternals/downloads/notmyfault)
2. Run as admin
3. Select crash type (e.g., "High IRQL fault (kernel-mode)")
4. Click "Crash" → server BSODs → dump written

#### Alternative: trigger dump via keyboard combo
1. Set registry: `HKLM\SYSTEM\CurrentControlSet\Services\<i8042prt or kbdhid>\Parameters\CrashOnCtrlScroll = 1`
2. Restart
3. Hold Right Ctrl + press Scroll Lock twice → triggers BSOD + dump

#### Collect dump for PG
- Default: `C:\Windows\MEMORY.DMP`
- Size: typically equals physical RAM
- Compress + send via DTM

### ⚠ Coordinate before crashing production
Crashing the server causes downtime. Notify customer + schedule.

### Reference
[TSG AFS Getting Kernel dump](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/784058)
