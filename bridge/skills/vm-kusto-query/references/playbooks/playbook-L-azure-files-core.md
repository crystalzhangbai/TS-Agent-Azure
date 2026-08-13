# Playbook L — Azure Files + Azure File Sync (AFS) — Core

> **Companion to** [`playbook-L-azure-files-deep.md`](./playbook-L-azure-files-deep.md). ROUTER style — 315+ wiki pages across 3 areas merged. Most KQL/Geneva queries live in deep file; foundational SA / XStore queries delegate to [`references/storage-account-queries.md`](../catalogs/storage-account-queries.md).
>
> Use as **routing entry point** when a case is about an Azure File Share, NFS share, or Azure File Sync (AFS). NOT SA control plane (→ J), NOT XStore backend perf (→ K), NOT managed disk (→ F), NOT guest-OS perf only (→ G).

## When to use this playbook

| Use Playbook L when... | Don't — use instead |
|---|---|
| Customer can't mount Azure File Share (SMB / NFS / MacOS) | SA control plane / "cannot create share"  → J |
| Identity-based auth fails (AAD Kerb / AD DS / Entra Only Kerb / OAuth REST / MI for SMB) | Generic AAD app reg → AAD team |
| Azure File Sync (AFS) agent install / register / sync / cloud tiering issue | SA-level throttling → K § SA-Perf-SAThrottle |
| Sync error code `ECS_E_*` from AFS server | Backend XStore perf / latency  → K |
| File share snapshot / backup / soft delete recovery | Account-level recovery → J § SA-Recovery-FilesSMB |
| NFS-specific TS (Linux NFS v4.1) | NFS account create / SA setup  → J |
| Premium SMB Metadata Caching feature behavior | Feature enablement / no perf benefit → K § SA-Perf-AzureFiles-MetadataCaching |
| Cross-zone latency / Zonal Placement | XStore backend latency analysis → K § SA-Perf-AzureFiles-Backend |

## Inputs to collect

| # | Item | Why |
|---|---|---|
| 1 | `SubscriptionId` + `StorageAccountName` + `FileShareName` | Primary filters |
| 2 | UNC path or mount command attempted (verbatim) | Format / DNS / FQDN validation |
| 3 | Client OS (Windows version / Linux distro+kernel / MacOS version) | OS-specific TSG routing |
| 4 | Source location (Azure VM / on-prem / VPN / ExpressRoute) | Network reach + port 445 ISP block check |
| 5 | Auth method (storage account key / AAD Kerb / AD DS / Entra Only / OAuth REST / MI) | Identity routing |
| 6 | Exact error message + screenshot | Error-code routing (key dimension) |
| 7 | Timestamp UTC | Backend log correlation |
| 8 | For sync: Storage Sync Service name + Sync Group + Server Endpoint + AFS agent version | AFS routing |
| 9 | For sync errors: `ECS_E_*` error code from ASC | Per-error sync TSG |
| 10 | VM Name (client) | Network trace correlation |

## Step-by-step

### Step 1 — Identify problem domain

| Symptom | Goes to... |
|---|---|
| Cannot connect / mount / map an Azure File Share | Step 2 (Connectivity / Mount errors) |
| Identity-based auth failure (any kind) | Step 3 (Identity) |
| Snapshot / Backup / Soft Delete / Recovery (data side) | Step 4 (Snapshot + Backup + Recovery) |
| Encryption in Transit configuration / TS | Step 5 (Encryption in Transit) |
| Azure File Sync (AFS): agent / sync / tiering / recall | Step 6 (AFS) |
| Misc generic Files error (QUOTA, ClientOtherError, Slow Excel, RestAPI Empty, Audit, FAQ) | Step 7 (Misc + Features) |
| Performance latency / throttling (backend) | → **Playbook K** (cross-link, do NOT do here) |

### Step 2 — Connectivity / Mount routing

#### 2a. Pre-flight (run first for ALL mount cases)
1. Validate UNC path FQDN format: `\\<sa>.file.core.windows.net\<share>` (no IP, no short name unless DFS-N)
2. DNS resolution check: `nslookup <sa>.file.core.windows.net` (private vs public endpoint)
3. Port 445 network reach: `Test-NetConnection <sa>.file.core.windows.net -Port 445` (Win) / `nc -zv <sa>.file.core.windows.net 445` (Linux)
4. Run **AzFileDiagnostics** tool ([Win](https://github.com/Azure-Samples/azure-files-samples/tree/master/AzFileDiagnostics/Windows) / [Linux](https://github.com/Azure-Samples/azure-files-samples/tree/master/AzFileDiagnostics/Linux))

→ § [AF-Mount-Workflow](./playbook-L-azure-files-deep.md#af-mount-workflow--azure-files-connectivity-workflow-master-entry-point-pre-flight-checks-dns-port-445-azfilediagnostics-storage-account-firewall-security-settings-storage-logs-frontendlogs-ipauthorizationerror) (master TSG + DNS / Firewall / Security Settings / Storage Logs flow)

#### 2b. Windows SMB mount errors (account-key auth)

| Error | Anchor |
|---|---|
| `System error 53 / 67 / 87 / 123` / `0x80070035` (network reach / DNS / port 445 / OS unsupported / encryption mismatch) | § [AF-Mount-Win-53-67-87](./playbook-L-azure-files-deep.md#af-mount-win-53-67-87--system-error-53-67-87-123-or-0x80070035-port-445-blocked--dns-failure--smb-version-mismatch--secure-transfer-required) |
| `System error 5 Access Denied` mount | § [AF-Mount-Win-5](./playbook-L-azure-files-deep.md#af-mount-win-5--system-error-5-access-denied-during-mount-or-map-storage-account-firewall-blocks-the-connection) (SA firewall blocking) |
| `System error 64` (network name no longer available) | § [AF-Mount-Win-64](./playbook-L-azure-files-deep.md#af-mount-win-64--system-error-64-network-name-no-longer-available-secure-transfer-required--smb-3-encryption) |
| `System error 1326` with access keys | § [AF-Mount-Win-1326-Key](./playbook-L-azure-files-deep.md#af-mount-win-1326-key--system-error-1326-with-storage-account-key-credential-typo--azure-prefix-missing-in-username) |
| `Multiple connections to a server` (different username) | § [AF-Mount-Win-MultipleConn](./playbook-L-azure-files-deep.md#af-mount-win-multipleconn--multiple-connections-to-a-server-or-shared-resource-by-the-same-user-net-use-y-delete--clear-saved-creds) |
| Mount succeeds, drive letter doesn't show | § [AF-Mount-Win-DriveLetterMissing](./playbook-L-azure-files-deep.md#af-mount-win-driveletter-missing--mount-succeeds-drive-letter-not-visible-user-context-issue-elevated-vs-non-elevated--use-new-smbglobalmapping) (elevated context — use New-SmbGlobalMapping) |
| `The option <ID> is unknown` (Net Use) | § [AF-Mount-Win-NetUseUnknownOpt](./playbook-L-azure-files-deep.md#af-mount-win-netuseunknownopt--option-is-unknown-when-running-net-use-quote-issues-in-command) |
| `Destination doesn't support encryption` when copying | § [AF-Mount-Win-NoEncryption](./playbook-L-azure-files-deep.md#af-mount-win-noencryption--you-are-copying-a-file-to-a-destination-that-does-not-support-encryption-efs-not-supported-on-files) |
| Unable to mount within IIS virtual directory | § [AF-Mount-Win-IIS-UNC](./playbook-L-azure-files-deep.md#af-mount-win-iis-unc--unable-to-mount-azure-file-share-within-iis-virtual-directory-application-pool-identity-needs-mount) |
| Unable to run MSI installer using UNC path | § [AF-Mount-Win-MSI-UNC](./playbook-L-azure-files-deep.md#af-mount-win-msi-unc--unable-to-run-msi-installer-using-unc-path-msiexec-needs-network-provider-or-mapped-drive) |
| Bad Option / Unknown Error 524 | § [AF-Mount-Win-BadOption-524](./playbook-L-azure-files-deep.md#af-mount-win-badoption-524--azure-fileshare-mount-issue-bad-option-or-unknown-error-524-smb-version-or-options-not-supported) |
| `Cannot Map Drive Storage Account Forward Slash` | § [AF-Mount-Win-ForwardSlash](./playbook-L-azure-files-deep.md#af-mount-win-forwardslash--cannot-map-drive-storage-account-forward-slash-net-use-syntax-uses-backslash-not-forward-slash) |
| `Network path was not found` on Windows | § [AF-Mount-Win-NetworkPathNotFound](./playbook-L-azure-files-deep.md#af-mount-win-networkpathnotfound--mount-error-network-path-was-not-found-on-windows-port-445-blocked--dns-resolution-failed--vnet-routing) |
| Unable to Connect to Azure Files Over Reboot | § [AF-Mount-Win-OverReboot](./playbook-L-azure-files-deep.md#af-mount-win-overreboot--unable-to-connect-to-azure-files-over-reboot-credentials-not-persisted-need-cmdkey-or-credential-manager-persistence) |
| File Share Randomly Closing | § [AF-Mount-Win-RandomClose](./playbook-L-azure-files-deep.md#af-mount-win-randomclose--azure-file-share-mount-issue-randomly-closing-smb-idle-timeout-on-firewall--load-balancer--client-keepalive) |
| Losing Mount after Stamp Migration | § [AF-Mount-Win-StampMigration](./playbook-L-azure-files-deep.md#af-mount-win-stampmigration--losing-mount-after-stamp-migration-customer-must-remount-after-platform-stamp-move) |
| Mount via PowerShell `New-PSDrive` works but **File Explorer can't access** / Used+Free GB blank | § [AF-Mount-Win-PSDriveNoPersist](./playbook-L-azure-files-deep.md#af-mount-win-psdrivenopersist--azure-file-share-unable-to-access-via-file-explorer-when-mounted-with-powershell-new-psdrive-missing--persist-option-powershell-session-only-drive-vs-persistent-network-drive) (missing `-Persist` option — PowerShell session-only drive) |

#### 2c. Linux SMB mount errors (CIFS account-key auth)

| Error | Anchor |
|---|---|
| `mount error(11): Resource temporarily unavailable` (Ubuntu 16.10 kernel bug) | § [AF-Mount-Linux-11](./playbook-L-azure-files-deep.md#af-mount-linux-11--mount-error11-resource-temporarily-unavailable-ubuntu-1610-kernel-claims-smb3-encryption-but-doesnt-support--use-vers21-as-workaround) |
| `mount error(13): Permission denied` | § [AF-Mount-Linux-13](./playbook-L-azure-files-deep.md#af-mount-linux-13--mount-error13-permission-denied-port-445-blocked--smb-encryption-mismatch--firewall--secure-transfer-required--credentials-wrong) |
| `mount error(115): Operation in progress` / `Unknown error` | § [AF-Mount-Linux-115](./playbook-L-azure-files-deep.md#af-mount-linux-115--mount-error115-operation-now-in-progress-or-unknown-error-could-not-resolve-address-dns-resolution-failed--check-storage-endpoint) |
| `mount error(2): No such file or directory` | § [AF-Mount-Linux-2](./playbook-L-azure-files-deep.md#af-mount-linux-2--mount-error2-no-such-file-or-directory-share-doesnt-exist-or-typo--smb-version-not-supported) |
| Generic errors mounting Azure Files on Linux | § [AF-Mount-Linux-Generic](./playbook-L-azure-files-deep.md#af-mount-linux-generic--errors-mounting-azure-files-share-on-linux-umbrella-azfilediagnosticslinux-script--smbdiagnostics-tcpdump-cifs_tracecifs_diagcifs_dmesg-trace-bundle) |

#### 2d. MacOS

| Symptom | Anchor |
|---|---|
| File share mount issues on MacOS | § [AF-Mount-MacOS](./playbook-L-azure-files-deep.md#af-mount-macos--azure-file-share-mount-issues-on-mac-os--cannot-mount-no-route-to-host-smb-version-or-port-445-blocked) |

#### 2e. NFS (Linux NFS v4.1)

| Symptom | Anchor |
|---|---|
| NFS v4 master setup + mount workflow | § [AF-Mount-NFS-Workflow](./playbook-L-azure-files-deep.md#af-mount-nfs-workflow--nfs-v4-for-azure-files-master-workflow-premium-only-private-endpoint-required-no-azure-files-zrs-for-nfs-mount-syntax-fstab-entry-secure-transport-encryption-in-transit) |
| `Cannot access or mount NFS nfs4 reclaim open state error=10019` | § [AF-Mount-NFS-Reclaim10019](./playbook-L-azure-files-deep.md#af-mount-nfs-reclaim10019--cannot-access-or-mount-nfs-nfs4-reclaim-open-state-error10019-client-id-already-exists-need-reboot-client-or-restart-rpcbind) |
| Permission Issues NFS 4.1 | § [AF-Mount-NFS-Perms](./playbook-L-azure-files-deep.md#af-mount-nfs-perms--permission-issues-nfs-41-default-uidgid-mapping--chown-required-after-mount-vs-default-no_root_squash) |
| `NfsFileShares is Not Supported for the Account` | § [AF-Mount-NFS-NotSupported](./playbook-L-azure-files-deep.md#af-mount-nfs-notsupported--nfsfileshares-is-not-supported-for-the-account-non-premium-sa--non-filestorage-kind--region-not-supported) |
| NFS Not Working SuSE | § [AF-Mount-NFS-SuSE](./playbook-L-azure-files-deep.md#af-mount-nfs-suse--nfs-not-working-on-suse-distro-specific-config--missing-nfs-utils--firewalld-rules) |
| Incorrect SA names in `df -h` output (RHEL after reboot) | § [AF-Mount-NFS-RHEL-dfh](./playbook-L-azure-files-deep.md#af-mount-nfs-rhel-dfh--incorrect-storage-account-names-in-df-h-output-for-nfs-shares-on-rhel-after-reboot-systemd-mount-resolution-edge-case) |
| Troubleshooting fpsync issues | § [AF-Mount-NFS-fpsync](./playbook-L-azure-files-deep.md#af-mount-nfs-fpsync--troubleshooting-fpsync-issues-parallel-rsync-tool-for-fast-nfs-copy-permission--stale-handle--memory-exhaustion-edge-cases) |

### Step 3 — Identity routing

#### 3a. Pre-flight scoping
- Identity model in use? (Storage Account Key / AAD Kerb hybrid / AD DS on-prem / Entra Only Kerb / OAuth REST / MI for SMB)
- Client domain-joined? Hybrid or cloud-only?
- File share AD DS configured or AAD Kerb registered?
- Customer using FSLogix / AVD?

#### 3b. AAD Kerberos (Entra hybrid)

| Symptom | Anchor |
|---|---|
| Master AAD Kerb troubleshooting flow (hybrid identities) | § [AF-Identity-AADKerb-Hybrid-Flow](./playbook-L-azure-files-deep.md#af-identity-aadkerb-hybrid-flow--master-troubleshooting-flow-for-entra-kerberos-hybrid-identities-7-step-prereq-check-feature-registration-azure-ad-kerberos-storage-acct-config-rbac-disable-clipping-fiddler-trace) |
| Error 86 The Specified Network Password is not Correct | § [AF-Identity-AADKerb-86](./playbook-L-azure-files-deep.md#af-identity-aadkerb-86--error-86-the-specified-network-password-is-not-correct-aad-kerb-cached-kerberos-ticket-stale--klist-purge--re-run-mount) |
| Error 1326 Mount Error | § [AF-Identity-AADKerb-1326](./playbook-L-azure-files-deep.md#af-identity-aadkerb-1326--error-1326-mount-error-aad-kerb-user-not-synced-to-aad--policy-blocking-windows-hello-pin) |
| Error 1396 The target account name is incorrect | § [AF-Identity-AADKerb-1396](./playbook-L-azure-files-deep.md#af-identity-aadkerb-1396--error-1396-target-account-name-incorrect-spn-not-registered--storage-acct-not-aad-kerb-enabled--wrong-spn) |
| Error 5 Access Denied (mount succeeds, files access fails) | § [AF-Identity-AADKerb-5](./playbook-L-azure-files-deep.md#af-identity-aadkerb-5--error-5-access-denied-share-and-file-level-rbac-permissions-check-storage-file-data-smb-share-reader-vs-contributor-vs-elevated-contributor) |
| `Klist Failed With 0x80090303` (target unknown/unreachable) | § [AF-Identity-AADKerb-Klist0x80090303](./playbook-L-azure-files-deep.md#af-identity-aadkerb-klist0x80090303--klist-failed-with-0x80090303-specified-target-is-unknown-or-unreachable-azure-ad-kerberos-realm-or-spn-not-registered--no-internet-no-aad-reach) |
| Entra Kerberos Join Graph BadRequest | § [AF-Identity-AADKerb-JoinGraphBadRequest](./playbook-L-azure-files-deep.md#af-identity-aadkerb-joingraphbadrequest--microsoft-entra-kerberos-join-graph-badrequest-azuread-kerberos-domain-join-step-failing-azure-policy--graph-api-permission-issue) |
| Entra Kerberos Unable to Retrieve Storage Token | § [AF-Identity-AADKerb-StorageTokenFail](./playbook-L-azure-files-deep.md#af-identity-aadkerb-storagetokenfail--microsoft-entra-kerberos-authentication-unable-to-retrieve-storage-token-trust-relationship-failing--client-not-aad-joined--token-acquisition-blocked) |
| ADAuth Files Multiforest | § [AF-Identity-AADKerb-Multiforest](./playbook-L-azure-files-deep.md#af-identity-aadkerb-multiforest--adauth-files-multiforest-user-in-different-forest-than-sa--add-suffix-routing--add-trust-relationship) |
| AAD Kerb with AVD + FSLogix (support boundaries) | § [AF-Identity-AADKerb-AVD-FSLogix](./playbook-L-azure-files-deep.md#af-identity-aadkerb-avd-fslogix--azure-files-aad-kerb-with-avd-and-fslogix-support-boundaries-fslogix-profile-on-aad-kerb-share-supported-configurations) |
| User Prompted for Credentials Repeatedly | § [AF-Identity-AADKerb-PromptedCreds](./playbook-L-azure-files-deep.md#af-identity-aadkerb-promptedcreds--user-prompted-for-credentials-repeatedly-cached-creds-stale--single-sign-on-not-configured--client-not-aad-joined) |
| **Coexistence**: client must access both AD DS-joined AND Entra Kerberos SAs (host-to-realm mapping required) | § [AF-Identity-Coexistence](./playbook-L-azure-files-deep.md#af-identity-coexistence--coexistence-feature-hybrid-identity-client-accessing-both-ad-ds-and-entra-kerberos-storage-accounts-host-to-realm-mapping-via-intune-csp--gpo--ksetup-registry-troubleshooting-workflow) (Intune CSP / GPO / `ksetup` registry methods) |
| AADJ / HAADJ client needs to access AD DS-joined SA (hybrid storage scenarios) | § [AF-Identity-StepByStep-AADJ-HAADJ](./playbook-L-azure-files-deep.md#af-identity-stepbystep-aadj-haadj--step-by-step-setup-aadj-and-haadj-clients-accessing-adds-joined-azure-file-shares-hybrid-storage-with-aad-joined--hybrid-joined-clients-configure-realm-to-host-mapping-or-use-entra-kerberos-with-on-prem-ad) (2 approaches: Coexistence config OR migrate SA to Entra Kerberos) |
| Deep dive into SMB Windows 3-layer permission model (Azure RBAC + Share RBAC + NTFS ACL) | § [AF-Identity-SMBWindowsPermissionModel](./playbook-L-azure-files-deep.md#af-identity-smbwindowspermissionmodel--smb-windows-permission-model-tsg-3-layer-permission-model-deep-dive-azure-rbac-mgmt--storage-file-data-smb-share-rbac--ntfs-acl-roleassignmentscheduleinstances-reading-sysinternals-accesschk-troubleshooting) (reading current role assignments via PowerShell + sysinternals AccessChk for effective NTFS ACL) |

#### 3c. AD DS (on-prem AD)

| Symptom | Anchor |
|---|---|
| Mount with shortname / DFS-N | § [AF-Identity-ADDS-ShortName](./playbook-L-azure-files-deep.md#af-identity-adds-shortname--mount-with-short-name--dfs-n-vs-fqdn-spn-considerations-when-using-friendly-names) |
| 1219 Mount Error | § [AF-Identity-ADDS-1219](./playbook-L-azure-files-deep.md#af-identity-adds-1219--1219-mount-error-multiple-sessions-with-same-server-using-different-credentials--credential-conflict) |
| 64 Mount Error (AD DS context) | § [AF-Identity-ADDS-64](./playbook-L-azure-files-deep.md#af-identity-adds-64--64-mount-error-ad-ds-context-stale-spn--computer-object-deleted--secure-transfer-required-smb3) |
| Specified Network Password Mount Error (AD DS) | § [AF-Identity-ADDS-PasswordError](./playbook-L-azure-files-deep.md#af-identity-adds-passworderror--specified-network-password-is-not-correct--ad-ds-context-kerberos-ticket-acquisition-failing--ad-trust-broken--spn-mismatch) |
| Kerberos `STATUS_ACCOUNT_DISABLED` | § [AF-Identity-ADDS-AccountDisabled](./playbook-L-azure-files-deep.md#af-identity-adds-accountdisabled--kerberos-error-status_account_disabled-storage-acct-computer-object-in-ad-disabled--user-account-disabled-in-ad) |
| Cached Credentials problem | § [AF-Identity-ADDS-CachedCreds](./playbook-L-azure-files-deep.md#af-identity-adds-cachedcreds--cached-credentials-cause-mount-failure-cmdkey-deletes-or-credential-manager-cleanup) |
| Cannot Bind Positional Parameters (PowerShell module) | § [AF-Identity-ADDS-CannotBind](./playbook-L-azure-files-deep.md#af-identity-adds-cannotbind--cannot-bind-positional-parameters-azfilesag-powershell-module-version-mismatch--cmdlet-param-changed-between-versions) |
| Cannot Take Ownership | § [AF-Identity-ADDS-CannotTakeOwnership](./playbook-L-azure-files-deep.md#af-identity-adds-cannottakeownership--cannot-take-ownership-of-file-on-azure-files-ad-ds-share-permission-model-difference--super-user-not-domain-admin-on-azure-files) |
| Domain Does Not Populate (PowerShell) | § [AF-Identity-ADDS-DomainNotPopulate](./playbook-L-azure-files-deep.md#af-identity-adds-domainnotpopulate--domain-does-not-populate-in-output-of-azfilesag-powershell-module-storage-acct-not-domain-joined--missing-rights) |
| Failed to Enumerate files/folders | § [AF-Identity-ADDS-FailedToEnumerate](./playbook-L-azure-files-deep.md#af-identity-adds-failedtoenumerate--failed-to-enumerate-files-or-folders-share-level-rbac-grants-mount-but-not-list--ntfs-acl-deny--access-based-enumeration) |
| FSLogix on AD DS | § [AF-Identity-ADDS-FSLogix](./playbook-L-azure-files-deep.md#af-identity-adds-fslogix--fslogix-profile-container-on-azure-files-ad-ds-permission-model-requirements--share-rbac--ntfs-acl--smb-options) |
| Join Errors / New ADComputerFailure | § [AF-Identity-ADDS-JoinErrors](./playbook-L-azure-files-deep.md#af-identity-adds-joinerrors--ad-join-errors--new-adcomputer-failure-when-running-join-azstorageaccount-permission--ou-path--ad-replication-issues) |
| Module Install Error (AzFilesHybrid) | § [AF-Identity-ADDS-ModuleInstall](./playbook-L-azure-files-deep.md#af-identity-adds-moduleinstall--module-install-error-for-azfileshybrid-execution-policy--missing-prereqs--internet-blocked) |
| Permissions Issue | § [AF-Identity-ADDS-Permissions](./playbook-L-azure-files-deep.md#af-identity-adds-permissions--permissions-issue-when-managing-or-accessing-shares-3-layer-permission-model-share-rbac--ntfs-acl--smb-options) |
| RoboCopy Limitations | § [AF-Identity-ADDS-RobocopyLimits](./playbook-L-azure-files-deep.md#af-identity-adds-robocopylimits--robocopy-limitations-on-azure-files-ad-ds-large-fs-acl-may-not-copy--owner-may-not-preserve--use-mt-and-copyall) |
| System Error 86 on Windows 7 / Server 2008 | § [AF-Identity-ADDS-Err86-Win7](./playbook-L-azure-files-deep.md#af-identity-adds-err86-win7--system-error-86-on-windows-7-or-2008-r2-smb-encryption-not-supported--secure-transfer-required-mismatch) |
| Unable to Allocate Relative Identifier (RID) | § [AF-Identity-ADDS-RIDAllocation](./playbook-L-azure-files-deep.md#af-identity-adds-ridallocation--unable-to-allocate-relative-identifier-rid-master-fsmo-not-available--rid-pool-exhausted-on-storage-acct-creation) |
| Unable to contact AD Web Services | § [AF-Identity-ADDS-ADWebServices](./playbook-L-azure-files-deep.md#af-identity-adds-adwebservices--unable-to-contact-active-directory-web-services-adws-service-down--firewall--missing-on-dc) |
| Verify On-Prem AD User Synced to AAD | § [AF-Identity-ADDS-VerifyADSync](./playbook-L-azure-files-deep.md#af-identity-adds-verifyadsync--verify-on-prem-ad-user-synced-to-aad-aad-connect-sync-status--user-aad-objectid-match-foreign-security-principal-fsp-required-for-aad-kerb) |
| Access Denied while updating NTFS permission | § [AF-Identity-ADDS-AccessDenied-NTFS](./playbook-L-azure-files-deep.md#af-identity-adds-accessdenied-ntfs--access-denied-while-trying-to-update-file-share-ntfs-permission-share-rbac-grants-mount-but-not-acl-management--need-storage-file-data-smb-share-elevated-contributor) |

#### 3d. Entra Only Kerberos (no on-prem AD)

| Symptom | Anchor |
|---|---|
| Mount Azure Files SMB with Entra Only Kerberos | § [AF-Identity-EntraOnly-Mount](./playbook-L-azure-files-deep.md#af-identity-entraonly-mount--how-to-mount-azure-files-smb-with-entra-only-kerberos-cloud-only-aad-joined-or-hybrid-joined-no-on-prem-ad-required-aad-kerb-enable--rbac--mount) |
| Master TSG for Entra Only Kerberos | § [AF-Identity-EntraOnly-TSG](./playbook-L-azure-files-deep.md#af-identity-entraonly-tsg--azure-files-smb-authentication-with-entra-only-kerberos-tsg-prereqs-supported-clients-aad-joined-aad-hybrid-joined-no-on-prem-ad--limitations--troubleshooting-flow) |

#### 3e. OAuth REST (Entra ID over REST API)

| Symptom | Anchor |
|---|---|
| ASC unable to view data Share level (OAuth REST) | § [AF-Identity-OAuth-REST-ASC-NoData](./playbook-L-azure-files-deep.md#af-identity-oauth-rest-asc-nodata--asc-unable-to-view-data-share-level-with-oauth-rest-shared-key-access-disabled--data-action-rbac-missing--bearer-token-not-acquired) |
| Restrict key-based access (OAuth REST) | § [AF-Identity-OAuth-REST-RestrictKey](./playbook-L-azure-files-deep.md#af-identity-oauth-rest-restrictkey--restrict-key-based-access-with-oauth-rest-allowsharedkeyaccess-false--data-plane-only-aad-token--implications-for-existing-key-based-tools) |
| Role assignment check (OAuth REST) | § [AF-Identity-OAuth-REST-RoleCheck](./playbook-L-azure-files-deep.md#af-identity-oauth-rest-rolecheck--role-assignment-check-for-oauth-rest-storage-file-data-privileged-contributor--reader--share-level-vs-data-action-needed) |
| `AuthorizationPermissionMismatch` (OAuth REST) | § [AF-Identity-OAuth-REST-AuthMismatch](./playbook-L-azure-files-deep.md#af-identity-oauth-rest-authmismatch--authorizationpermissionmismatch-error-data-plane-rbac-missing-storage-file-data-privileged-contributor-or-reader-needed-for-oauth-rest-data-actions) |

#### 3f. Linux AD DS over SMB

| Symptom | Anchor |
|---|---|
| Linux AD Auth over SMB overview + troubleshooting | § [AF-Identity-Linux-ADDS](./playbook-L-azure-files-deep.md#af-identity-linux-adds--linux-ad-auth-over-smb-for-azure-files-overview--troubleshooting-keytab-setup--cifs-utils--krb5conf--multiuser-mount-option-required) |

#### 3g. Managed Identity for SMB (newer feature)

| Symptom | Anchor |
|---|---|
| MI for Azure Files SMB HowTo + TSG | § [AF-Identity-MI-SMB](./playbook-L-azure-files-deep.md#af-identity-mi-smb--azure-files-managed-identity-support-for-smb-howto--tsg-system-or-user-assigned-mi--rbac--mount-from-azure-vm-without-creds-preview) |

#### 3h. RBAC SMB admin

| Symptom | Anchor |
|---|---|
| How to assign RBAC roles for SMB admin privileges | § [AF-Identity-RBAC-SMBAdmin](./playbook-L-azure-files-deep.md#af-identity-rbac-smbadmin--how-to-assign-rbac-roles-for-smb-admin-privileges-storage-file-data-smb-share-elevated-contributor--ntfs-acl-management-takes-effect) |

#### 3i. Identity Diagnostic Tools (cross-referenced from every Identity TSG)

| When to use | Anchor |
|---|---|
| **FIRST step** for any AD DS / Entra Kerberos auth issue | § [AF-Identity-Diagnostic-DebugAzStorageAccountAuth](./playbook-L-azure-files-deep.md#af-identity-diagnostic-debugazstorageaccountauth--diagnostic-tool-debug-azstorageaccountauth-powershell-cmdlet-first-step-for-ad-ds-or-entra-kerberos-auth-issues-basic-checks-runs-with-logged-on-ad-user-azfileshybrid-v012-powershell-51-net-472-az-280-azstorage-430) (AzFilesHybrid cmdlet — runs basic checks with logged-on AD user) |
| Entra Kerberos HTTPS-over-KDC-Proxy traffic inspection (Wireshark/netsh sees only encrypted TCP) | § [AF-Identity-Diagnostic-FiddlerKerberos](./playbook-L-azure-files-deep.md#af-identity-diagnostic-fiddlerkerberos--diagnostic-tool-fiddler-with-kerberosnet-extension-for-entra-kerberos-https-over-kdc-proxy-debugging-wiresharknetsh-cant-see-encrypted-traffic-fiddler-decrypts-https-klist-get-cifssafilecorewindowsnet--inspect-errorcode-in-kerberos-response) (Fiddler + Kerberos.NET extension; `klist get` to trigger + inspect ErrorCode) |
| Misc Identity diagnostic quick-reference (SID / domain joined / SPN / Kerberos ticket / Entra Request ID / netsh trace) | § [AF-Identity-Diagnostic-Misc](./playbook-L-azure-files-deep.md#af-identity-diagnostic-misc--misc-identity-diagnostic-tools-check-valid-sid--check-domain-joined--check-sa-service-principal-name--check-kerberos-ticket--get-entra-request-id--collect-network-trace-for-domain-auth) (6 diagnostic snippets) |

### Step 4 — Snapshot + Backup + Recovery routing

| Symptom | Anchor |
|---|---|
| Access File Share Snapshot | § [AF-Snapshot-Access](./playbook-L-azure-files-deep.md#af-snapshot-access--access-azure-file-share-snapshot-portal-asc-powershell-azcopy-storage-explorer-methods) |
| SMB File Share Snapshots (creation + management) | § [AF-Snapshot-SMB](./playbook-L-azure-files-deep.md#af-snapshot-smb--smb-file-share-snapshots-creation--management--smb-version-2x-requirement--max-200-snapshots-per-share) |
| NFS File Share Snapshots (preview) | § [AF-Snapshot-NFS](./playbook-L-azure-files-deep.md#af-snapshot-nfs--nfs-file-share-snapshots-preview-premium-only--api-version-2022-11-01--no-snapshot-mount-via-nfs-protocol-itself) |
| Back-Up Azure File Share (Azure Backup) | § [AF-Backup-AzBackup](./playbook-L-azure-files-deep.md#af-backup-azbackup--back-up-azure-file-share-with-azure-backup-recovery-services-vault--backup-policy--restore-options) |
| Check Backup or Snapshot existence | § [AF-Backup-Check](./playbook-L-azure-files-deep.md#af-backup-check--check-azure-file-share-backup-or-snapshot-existence-asc-files-configurations--azure-backup--snapshot-version-7131--timestamp-12319999-signals-not-configured) |
| Backup doesn't restore manually assigned NTFS ACLs | § [AF-Backup-ACLNotRestored](./playbook-L-azure-files-deep.md#af-backup-aclnotrestored--azure-backup-doesnt-restore-manually-assigned-ntfs-acls-known-limitation-only-inherited-acls-restored--manual-or-icacls-script-after-restore) |
| Soft Delete for File Shares (preview) | § [AF-Recovery-SoftDelete](./playbook-L-azure-files-deep.md#af-recovery-softdelete--soft-delete-for-file-shares-1-to-365-day-retention--asc-search-file-share-soft-deleted-time--expiry-time--billing-implications) |
| Recover deleted SMB File Share (PG-owned) | → **Playbook J § SA-Recovery-FilesSMB** (Sev 3 ICM only) |

### Step 5 — Encryption in Transit routing

| Symptom | Anchor |
|---|---|
| Encryption in Transit overview (SMB + NFS) | § [AF-EncryptionInTransit-Overview](./playbook-L-azure-files-deep.md#af-encryptionintransit-overview--azure-files-encryption-in-transit-settings-for-smb-and-nfs-secure-transfer-required-flag--smb-3-encryption-aes-128-gcmaes-256-gcm--nfs-41-with-tls-rpc-with-tls) |
| NFSv4.1 Encryption in Transit overview | § [AF-EncryptionInTransit-NFS-Overview](./playbook-L-azure-files-deep.md#af-encryptionintransit-nfs-overview--encryption-in-transit-for-azure-files-nfsv41-overview-tls-13-via-stunnel--aznfs-mount-helper--per-mount-tls-tunneling) |
| NFSv4.1 Encryption in Transit troubleshooting | § [AF-EncryptionInTransit-NFS-Troubleshooting](./playbook-L-azure-files-deep.md#af-encryptionintransit-nfs-troubleshooting--encryption-in-transit-azure-files-nfsv41-troubleshooting-stunnel-config--port-2049-vs-tls-port--cert-trust-chain--mount-helper-version) |
| Collect NFS client and network traces | § [AF-NFS-CollectTraces](./playbook-L-azure-files-deep.md#af-nfs-collecttraces--collect-nfs-client-and-network-trace-for-encryption-in-transit-tcpdump-on-port-2049--rpcdebug-nlm--cat-procmountinfo--cat-procnetrpcnfsfh) |

### Step 6 — Azure File Sync (AFS) routing

#### 6a. AFS Pre-flight scoping
- AFS agent version on registered server?
- Latest GA version per release notes?
- Server endpoint count?
- Cloud tiering enabled?
- Managed identities enabled (default for new deployments since v19.0.0.0)?

#### 6b. AFS Sync errors

| Symptom | Anchor |
|---|---|
| Master AFS Sync Workflow + Common Sync Errors table | § [AFS-Sync-Workflow](./playbook-L-azure-files-deep.md#afs-sync-workflow--master-azure-file-sync-workflow-feature-overview--terminology-cloud-endpoint--server-endpoint--sync-group--registered-server--storage-sync-service--rbac--don-not-unregister-server-warning--telemetry-events-mapping) |
| Conflict Issues (`ECS_E_SYNC_CONSTRAINT_CONFLICT`, `ECS_E_SYNC_FILE_IN_USE`, `ECS_E_SYNC_MERGE_TOMBSTONE_CHECKS_FAILED`) | § [AFS-Sync-Conflict](./playbook-L-azure-files-deep.md#afs-sync-conflict--conflict-issues-ecs_e_sync_constraint_conflict--ecs_e_sync_file_in_use--ecs_e_sync_merge_tombstone_checks_failed-customer-runs-filesyncerrorreportps1--jarvis-servertelemetryevents-eventid-9121-and-serveritemresultsevents-by-clientcorrelationid) |
| File Not Syncing from FileShare → Server | § [AFS-Sync-NotSyncingFromShare](./playbook-L-azure-files-deep.md#afs-sync-notsyncingfromshare--file-not-syncing-from-file-share-to-server-cloud-change-detection-runs-every-24h--rest-changes-dont-update-smb-last-modified--customer-can-trigger-change-detection-job-manually) |
| File Not Syncing from Server → FileShare | § [AFS-Sync-NotSyncingFromServer](./playbook-L-azure-files-deep.md#afs-sync-notsyncingfromserver--file-not-syncing-from-server-to-file-share-realtime-crud-expected-few-mins-asc-validation--server-endpoint-upload-errors--azurefilesyncerrorreportps1) |
| `ECS_E_NOT_ENOUGH_REMOTE_STORAGE` | § [AFS-Sync-NotEnoughRemoteStorage](./playbook-L-azure-files-deep.md#afs-sync-notenoughremotestorage--ecs_e_not_enough_remote_storage-file-share-at-5tb-default-limit--customer-expands-to-large-file-share-up-to-100tb) |
| `ECS_E_NOT_ENOUGH_LOCAL_STORAGE` (not enough space to sync) | § [AFS-Sync-NotEnoughLocalStorage](./playbook-L-azure-files-deep.md#afs-sync-notenoughlocalstorage--ecs_e_not_enough_local_storage-not-enough-space-on-server-to-sync--enable-cloud-tiering-or-add-disk-capacity) |
| `ECS_E_SYNC_METADATA_KNOWLEDGE_LIMIT_REACHED` (huge namespace) | § [AFS-Sync-MetadataKnowledgeLimit](./playbook-L-azure-files-deep.md#afs-sync-metadataknowledgelimit--ecs_e_sync_metadata_knowledge_limit_reached-2134375908-very-large-namespace-namespace-split-or-pg-escalation-required) |
| `ECS_E_MGMT_FILE_LOCKS_OPERATION_ERROR` | § [AFS-Sync-MgmtFileLocks](./playbook-L-azure-files-deep.md#afs-sync-mgmtfilelocks--ecs_e_mgmt_file_locks_operation_error-file-lock-management-failure-during-sync--reboot-server--check-vss-state) |
| `ECS_E_SYNC_CANCELLED_BY_VSS` (TSG 428) | § [AFS-Sync-CancelledByVSS](./playbook-L-azure-files-deep.md#afs-sync-cancelledbyvss--ecs_e_sync_cancelled_by_vss-tsg-428-disable-vss-sync--vss-snapshot-taken-during-sync-session-cancels-it--scheduling-conflict) |
| `ECS_E_DIRECTORY_RENAME_FAILED` (TSG 504) | § [AFS-Sync-DirectoryRenameFailed](./playbook-L-azure-files-deep.md#afs-sync-directoryrenamefailed--ecs_e_directory_rename_failed-tsg-504-per-item-upload-error-on-directory-rename-rename-target-name-conflict-or-permissions-issue) |
| `ECS_E_SERVER_CREDENTIAL_NEEDED` | § [AFS-Sync-ServerCredentialNeeded](./playbook-L-azure-files-deep.md#afs-sync-servercredentialneeded--ecs_e_server_credential_needed-server-cant-authenticate-to-cloud-sa-key-rotated--mi-not-configured--shared-key-access-disabled) |
| TSG 349 Sync Progress and Initial Sync | § [AFS-Sync-Progress](./playbook-L-azure-files-deep.md#afs-sync-progress--tsg-349-afs-sync-progress-and-initial-sync-asc-sync-status-tab--upload-throughput-vs-total-data-size--rapid-disaster-recovery-namespace-first-then-recall) |
| AFS Uploading Failed with Access Denied | § [AFS-Sync-UploadAccessDenied](./playbook-L-azure-files-deep.md#afs-sync-uploadaccessdenied--afs-uploading-failed-with-access-denied-share-rbac-or-key-issue--mi-not-configured-correctly--sa-firewall-blocking-server-ip) |
| `MgmtForbidden Failed to provision replica group` | § [AFS-Sync-MgmtForbidden](./playbook-L-azure-files-deep.md#afs-sync-mgmtforbidden--afs-mgmtforbidden-failed-to-provision-replica-group-sa-permissions--mi-missing--shared-key-access-disabled-without-mi-fallback) |
| `MgmtStorageAccountInaccessible` | § [AFS-Sync-MgmtStorageAccountInaccessible](./playbook-L-azure-files-deep.md#afs-sync-mgmtstorageaccountinaccessible--afs-mgmtstorageaccountinaccessible-sa-firewall-blocking-afs-service-private-endpoint--mi-not-trusted--key-rotated) |
| **AFS registration / sync fails with `CRYPT_E_NO_REVOCATION_DLL`** (WS 2012 + Agent 17.3) | § [AFS-Sync-CertRevocationFix](./playbook-L-azure-files-deep.md#afs-sync-certrevocationfix--afs-server-registration--sync-fails-with-certificate-revocation-crypt_e_no_revocation_dll-no-installed-or-registered-dll-was-found-that-was-able-to-verify-revocation-seen-on-windows-server-2012--agent-v173--registry-fix-at-hklmsoftwaremicrosoftcryptographyoidencodingtype-1certdllverifyrevocationdefaultdll--cryptnetdll) (registry fix: `HKLM\SOFTWARE\Microsoft\Cryptography\OID\EncodingType 1\CertDllVerifyRevocation\DEFAULT\Dll = cryptnet.dll`) |
| Unable to Sync `ERROR_CANT_ACCESS_FILE` | § [AFS-Sync-CantAccessFile](./playbook-L-azure-files-deep.md#afs-sync-cantaccessfile--unable-to-sync-with-error_cant_access_file-file-locked-by-app--antivirus-quarantine--file-system-corruption) |
| Unable to Delete Tiered File | § [AFS-Sync-UnableDeleteTiered](./playbook-L-azure-files-deep.md#afs-sync-unabledeletetiered--unable-to-delete-tiered-file-cloud-tiering-recall-fails--cert-revocation--server-offline) |
| AFS Unable to rename file `0x800705AA` | § [AFS-Sync-UnableRename](./playbook-L-azure-files-deep.md#afs-sync-unablerename--unable-to-rename-file-0x800705aa-error_no_system_resources-server-resource-exhaustion--vss-snapshot-conflict) |

#### 6c. AFS Agent install / upgrade / register

| Symptom | Anchor |
|---|---|
| File Sync Agent Installation Issues | § [AFS-Agent-InstallIssues](./playbook-L-azure-files-deep.md#afs-agent-installissues--file-sync-agent-installation-issues-msi-error-codes--exit-code-mapping--missing-prereqs-net-461--powershell-51-internet-access-for-cloud-endpoints-validation) |
| TSG 222 Agent Installation TS | § [AFS-Agent-TSG222](./playbook-L-azure-files-deep.md#afs-agent-tsg222--tsg-222-afs-agent-installation-troubleshooting-msiexec-logs--storageagent-msi-logs--storagesyncguestagentinstall-logs) |
| File Sync Agent Updater Hang | § [AFS-Agent-UpdaterHang](./playbook-L-azure-files-deep.md#afs-agent-updaterhang--file-sync-agent-updater-hang-stuck-during-version-upgrade--manual-msi-install--check-autoupdater-service-status) |
| Azure File Sync Agent Upgrade (master) | § [AFS-Agent-Upgrade](./playbook-L-azure-files-deep.md#afs-agent-upgrade--azure-file-sync-agent-upgrade-major-vs-minor-update--release-notes--rollback-via-msi-uninstallinstall-old-version--ring-deployment-stable--preview) |
| Azure File Sync Agent Upgrade Issue (errors during) | § [AFS-Agent-UpgradeIssue](./playbook-L-azure-files-deep.md#afs-agent-upgradeissue--azure-file-sync-agent-upgrade-issue-msi-rollback--existing-config-corruption--server-endpoint-state-machine-disrupted) |
| Sync Agent Installation Rollback | § [AFS-Agent-Rollback](./playbook-L-azure-files-deep.md#afs-agent-rollback--sync-agent-installation-rollback-failed-upgrade-rollback-msi-installer--restore-previous-agent--re-register-if-needed) |
| Filesync Agent AutoUpdater Policy | § [AFS-Agent-AutoUpdaterPolicy](./playbook-L-azure-files-deep.md#afs-agent-autoupdaterpolicy--filesync-agent-autoupdater-policy-3-ring-types-stable-preview-test--how-to-set-via-powershell--server-registration-vs-individual) |
| Agent registration failures (master) | § [AFS-Agent-RegFailures](./playbook-L-azure-files-deep.md#afs-agent-regfailures--file-sync-troubleshoot-agent-registration-failures-storagesync-registration-rest-call-failure--firewall-blocks-mgmt-endpoints--mi-not-configured) |
| Unable to Register Server Endpoint | § [AFS-Agent-UnableRegisterSEP](./playbook-L-azure-files-deep.md#afs-agent-unableregistersep--afs-unable-to-register-azure-file-sync-server-endpoint-volume-not-supported-network--ntfs-required--cloud-tiering-prereqs--path-in-use) |
| Replace File Sync Server | § [AFS-Agent-ReplaceServer](./playbook-L-azure-files-deep.md#afs-agent-replaceserver--replace-file-sync-server-procedure-pre-stage-cloud-tiered-data-on-new-server--re-register--re-create-sep--orphaned-files-cleanup) |
| File Sync Replace Drive | § [AFS-Agent-ReplaceDrive](./playbook-L-azure-files-deep.md#afs-agent-replacedrive--file-sync-replace-drive-procedure-move-sep-to-new-volume-without-orphaning-tiered-files--xcopy-backup-restore-method) |
| How to Register Server Endpoint with Restricted Network / Proxy Firewall | § [AFS-Agent-RegProxyFirewall](./playbook-L-azure-files-deep.md#afs-agent-regproxyfirewall--how-to-register-server-endpoint-with-restricted-network-or-proxy-firewall-required-endpoints-list--proxy-config--bypass-list) |
| AFS Agent Hung | § [AFS-Agent-Hung](./playbook-L-azure-files-deep.md#afs-agent-hung--afs-agent-hung-filesyncsvc-not-responding--restart-service--collect-kernel-dump-tsg-afs--check-disk-space) |

#### 6d. AFS Cloud Tiering

| Symptom | Anchor |
|---|---|
| Master Cloud Tiering TSG | § [AFS-Tiering-Master](./playbook-L-azure-files-deep.md#afs-tiering-master--master-afs-cloud-tiering-tsg-architecture--how-it-works-storagesyncsys-reparse-points--tiering-policies-volume-free-space--date-based--feature-bitmap--ese-database) |
| Check why a file is tiered | § [AFS-Tiering-WhyTiered](./playbook-L-azure-files-deep.md#afs-tiering-whytiered--tsg-afs-cloud-tiering-check-why-a-file-is-tiered-fsutil-reparsepoint-query--storagesync-cli--heat-store-investigation--per-file-attribute-check) |
| Dump heat store data | § [AFS-Tiering-DumpHeatStore](./playbook-L-azure-files-deep.md#afs-tiering-dumpheatstore--tsg-afs-cloud-tiering-dump-heat-store-data-cdpsvc-stop--ese-database-dump--heat-score-decimation-format) |
| Heat tracking process exclusion | § [AFS-Tiering-HeatProcessExclusion](./playbook-L-azure-files-deep.md#afs-tiering-heatprocessexclusion--tsg-afs-cloud-tiering-heat-tracking-process-name-exclusion-from-last-access-time-tracking-set-storagesyncserver-cmdlet-or-registry-key-prevent-backup-or-av-from-promoting-files) |
| Identify a corrupt heatstore | § [AFS-Tiering-CorruptHeatStore](./playbook-L-azure-files-deep.md#afs-tiering-corruptheatstore--tsg-afs-cloud-tiering-identify-a-corrupt-heatstore-event-id-9006--ese-database-recovery--rebuild-heatstore-procedure) |
| Heat Store overview | § [AFS-Tiering-HeatStore](./playbook-L-azure-files-deep.md#afs-tiering-heatstore--tsg-afs-heat-store-purpose--location-windowsstoragesync--ese-database-structure--size-considerations) |
| TSG 196 Delete ESE database | § [AFS-Tiering-DeleteESE](./playbook-L-azure-files-deep.md#afs-tiering-deleteese--tsg-196-afs-delete-an-ese-database-on-the-server-corrupt-heatstore-delete-procedure--filesyncsvc-stop--delete-databasedb-restart--rebuilds-on-next-start) |
| TSG 212 Collect heatstore for offline analysis | § [AFS-Tiering-CollectHeatStoreOffline](./playbook-L-azure-files-deep.md#afs-tiering-collectheatstoreoffline--tsg-212-afs-cloud-tiering-collect-heatstore-for-offline-analysis-stop-filesyncsvc--copy-windowsstoragesyncheatstoredb--send-to-dtm) |
| TSG 213 Deleting heatstore | § [AFS-Tiering-DeleteHeatStore](./playbook-L-azure-files-deep.md#afs-tiering-deleteheatstore--tsg-213-afs-cloud-tiering-deleting-a-heatstore-procedure-filesyncsvc-stop--delete-windowsstoragesyncheatstoredb--restart-rebuilds-empty) |
| Grey 'X' on Tiered Files | § [AFS-Tiering-GreyX](./playbook-L-azure-files-deep.md#afs-tiering-greyx--grey-x-on-tiered-files-windows-explorer-offline-attribute-displays-as-grey-x-aplo-attribute--storagesyncsys-filter-not-loaded--reparse-point-corruption) |
| Recall Performance Study | § [AFS-Tiering-RecallPerf](./playbook-L-azure-files-deep.md#afs-tiering-recallperf--recall-performance-study-recall-bandwidth-influenced-by-disk-iops--network--ese-database-size--customer-prestaging-best-practices) |
| Recall Error file system cache reached maximum threshold | § [AFS-Tiering-CacheMaxThreshold](./playbook-L-azure-files-deep.md#afs-tiering-cachemaxthreshold--tsg-afs-recall-error-file-system-cache-usage-reached-maximum-threshold-event-id-9023--cloud-tiering-policy-too-aggressive--enable-volume-free-space-policy) |
| MacOS slow file recall tiering | § [AFS-Tiering-MacOSSlowRecall](./playbook-L-azure-files-deep.md#afs-tiering-macosslowrecall--tsg-afs-macos-slow-file-recall-tiering-smb-client-not-optimized-for-tiered-files--prestage-files-or-disable-tiering-for-mac-clients) |
| Unable to Recall due to Cert Revocation | § [AFS-Tiering-UnableRecallCertRev](./playbook-L-azure-files-deep.md#afs-tiering-unablerecallcertrev--unable-to-recall-due-to-certificate-revocation-server-cert-expired--ocsp-or-crl-validation-failing--proxy-blocking-cert-validation-endpoints) |
| Server Certificate Issues | § [AFS-Tiering-ServerCertIssues](./playbook-L-azure-files-deep.md#afs-tiering-servercertissues--afs-server-certificate-issues-cert-bound-to-storagesync-channel-expired--invalid-thumbprint--cert-chain-broken) |

#### 6e. AFS Identity (Managed Identity for AFS)

| Symptom | Anchor |
|---|---|
| AFS Manage Identities (overview) | § [AFS-Identity-MI-Overview](./playbook-L-azure-files-deep.md#afs-identity-mi-overview--afs-manage-identities-system-assigned-mi-default-for-new-deployments-since-v19000-eliminates-shared-key-dependency-prereqs-v1900-trusted-services-allowed-key-access-enabled) |
| Expected Issues for Managed Identities on AFS | § [AFS-Identity-MI-ExpectedIssues](./playbook-L-azure-files-deep.md#afs-identity-mi-expectedissues--expected-issues-for-managed-identities-on-azure-file-sync-known-limitations-preview-must-allow-trusted-services--shared-key-access-required-during-onboarding) |

#### 6f. AFS Arc Extension

| Symptom | Anchor |
|---|---|
| Azure Arc Extension for File Sync (overview + TSG) | § [AFS-Arc-Extension](./playbook-L-azure-files-deep.md#afs-arc-extension--azure-arc-extension-for-file-sync-extension-install--config--telemetry-via-arc--troubleshooting-extension-deployment-failure--state-recovery--query-arc-events) |
| Software Assurance Benefits for AFS on Arc | § [AFS-Arc-SoftwareAssurance](./playbook-L-azure-files-deep.md#afs-arc-softwareassurance--how-to-check-software-assurance-benefits-for-azure-file-sync-on-arc-enabled-servers-arc-enables-sa-benefit-tracking-without-license-server-vs-paid-billing) |

#### 6g. AFS Performance (slow sync / recall)

| Symptom | Anchor |
|---|---|
| Slow Sync Throughput + Bandwidth | § [AFS-Perf-SlowSync](./playbook-L-azure-files-deep.md#afs-perf-slowsync--azure-file-sync-slow-sync-throughput-and-bandwidth-tsg-telemetry-events-7003700470057006--get-storagesyncnetworklimit-cmdlet--afsdiag-bandwidth-config--root-cause-patterns-table) |
| TSG 124 How to investigate sync performance + progress | § [AFS-Perf-TSG124](./playbook-L-azure-files-deep.md#afs-perf-tsg124--tsg-124-how-to-investigate-sync-performance-and-progress-upload-vs-download-throughput--initial-sync-vs-ongoing--per-file-vs-batched-perf--customer-prestaging-best-practices) |
| Slow Enumeration of Files and Folders | § [AFS-Perf-SlowEnumeration](./playbook-L-azure-files-deep.md#afs-perf-slowenumeration--slow-enumeration-of-files-and-folders-cloud-tiered-files-reparse-point-lookup--smb-traversal-cost--registry-tuning--prestaging) |

#### 6h. AFS Investigation tools

| Symptom | Anchor |
|---|---|
| How to Investigate AFSDiag Traces | § [AFS-Tools-AFSDiag](./playbook-L-azure-files-deep.md#afs-tools-afsdiag--how-to-investigate-afsdiag-traces-collect-afsdiag-via-debug-storagesync--what-it-contains-event-logs-telemetry-registry-cli--output-structure) |
| Access to File Sync Dashboards | § [AFS-Tools-Dashboards](./playbook-L-azure-files-deep.md#afs-tools-dashboards--access-to-file-sync-dashboards-icm-dashboards-list--asc-equivalents--how-to-request-access) |
| How To Find AFS Mgmt Operations on Registered Server | § [AFS-Tools-MgmtOps](./playbook-L-azure-files-deep.md#afs-tools-mgmtops--how-to-find-afs-mgmt-operations-on-registered-server-storagesync-azure-activity-log-filter--api-version-correlationid--per-server-op-history) |
| TSG 170 Formatting Server Telemetry in DGrep | § [AFS-Tools-DGrepTelemetry](./playbook-L-azure-files-deep.md#afs-tools-dgreptelemetry--tsg-170-afs-formatting-server-telemetry-events-in-dgrep-kailanisvc-namespace--servertelemetryevents--eventid-mapping--correlationid-join-with-serveritemresultsevents) |
| TSG 173 Generating Crash Dumps filesyncsvc | § [AFS-Tools-CrashDumps](./playbook-L-azure-files-deep.md#afs-tools-crashdumps--tsg-173-afs-generating-crash-dumps-filesyncsvc-procdump--werfault--registry-setup-for-localdumps--memory-dump-collection) |
| TSG 174 Enable / Disable diagnostics on customer server | § [AFS-Tools-DiagnosticsToggle](./playbook-L-azure-files-deep.md#afs-tools-diagnosticstoggle--tsg-174-afs-enabling-or-disabling-diagnostics-on-customer-server-debug-storagesync-enable--disable--logging-level-control--customer-consent-required) |
| TSG 193 Missing Server Telemetry | § [AFS-Tools-MissingTelemetry](./playbook-L-azure-files-deep.md#afs-tools-missingtelemetry--tsg-193-afs-investigate-missing-server-telemetry-or-server-showing-no-activity-monagentlauncher--genevamonitoringagent-state--health-channel-failure--server-not-uploading-events) |
| TSG 206 Get ShareId from SyncGroup | § [AFS-Tools-GetShareId](./playbook-L-azure-files-deep.md#afs-tools-getshareid--tsg-206-afs-how-to-get-shareid-from-syncgroup-and-subscription-id-needed-for-dgrep-correlation--rest-api-get-storagesyncservicessyncgroupscloudendpoints) |
| TSG 227 Windows Performance Toolkit for Customer Servers | § [AFS-Tools-WPT](./playbook-L-azure-files-deep.md#afs-tools-wpt--tsg-227-afs-windows-performance-toolkit-for-customer-servers-wprui--wpa--filesyncsvc-recording-profile--analyzing-disk-io-cpu-memory-traces) |
| TSG 268 Collect WinHTTP traces | § [AFS-Tools-WinHTTPTraces](./playbook-L-azure-files-deep.md#afs-tools-winhttptraces--tsg-268-afs-collect-winhttp-traces-netsh-trace-start-scenario-internetclient--ssl--filemode-circular--analyzing-mgmt-or-sync-channel-failures) |
| TSG 372 Troubleshoot Private Endpoint failures | § [AFS-Tools-PETroubleshoot](./playbook-L-azure-files-deep.md#afs-tools-petroubleshoot--tsg-372-afs-how-to-troubleshoot-private-endpoint-failures-pe-not-resolving--vnet-routing-blocked--mgmt-endpoint-still-needs-public-dns-resolution-or-pe-for-storagesync) |
| TSG AFS Sync investigation Cloud Enumeration + Upload Session | § [AFS-Tools-SyncCloudEnum](./playbook-L-azure-files-deep.md#afs-tools-synccloudenum--tsg-afs-sync-investigation-cloud-enumeration-and-upload-session-cloud-change-detection-job-24h-cycle--upload-session-state-machine--investigation-via-jarvis-eventid-mapping) |
| **TSG AFS Enable files+folder Auditing on Windows Server** (who-deleted-this-file / who-modified) | § [AFS-Tools-EnableAuditing](./playbook-L-azure-files-deep.md#afs-tools-enableauditing--tsg-afs-enable-files-and-folder-auditing-on-windows-server-windows-audit-policy--sacl-on-afs-root-for-who-deleted-this-file-investigation-registry-guid-for-filesystem-events-security-event-log-event-ids-46634660465) (auditpol + SACL + Event IDs 4663/4660/4656) |
| **TSG AFS Getting Kernel Dump for Investigation** (AFS hang at kernel level OR StorageSync.sys filter suspected) | § [AFS-Tools-KernelDump](./playbook-L-azure-files-deep.md#afs-tools-kerneldump--tsg-afs-getting-kernel-dump-for-investigation-system-dump-for-storagesyncsys-filter-or-driver-level-investigation-notmyfault-sysinternals--crashdump-registry-config--reproduce--collect-memorydmp-for-pg) (NotMyFault Sysinternals OR Ctrl+ScrLk keyboard trigger + MEMORY.DMP collection) |

#### 6i. AFS Emerging Issues (current at time of writing)

| Symptom | Anchor |
|---|---|
| AFS Emerging Issues umbrella | § [AFS-EmergingIssues](./playbook-L-azure-files-deep.md#afs-emergingissues--current-afs-emerging-issues-v17-server-registration-fails--v16-low-disk-space-mode-bug--monagentlauncher--azurestoragesyncmonitor--filesyncsvc-failed-to-start--wininet_e_decoding_failed--access-control-regression--v17-bytes-synced-metric-bug--v151-known-bug--0x8000ffff-no-system-mi-found) |

### Step 7 — Misc Files errors + features

| Symptom | Anchor |
|---|---|
| `QUOTA_EXCEEDED` during file access | § [AF-Errors-QuotaExceeded](./playbook-L-azure-files-deep.md#af-errors-quotaexceeded--azure-file-share-quota_exceeded-during-file-access-share-capacity-full--customer-expands-share-quota-via-portal-or-powershell--note-different-from-1816-not-enough-quota) |
| Cannot Access File Path / `Input/output error` | § [AF-Errors-IOError](./playbook-L-azure-files-deep.md#af-errors-ioerror--cannot-access-file-path-input-output-error-disconnected-mount--stale-handle--server-stamp-migration--client-needs-remount) |
| `Status Insufficient Resources` | § [AF-Errors-InsufficientResources](./playbook-L-azure-files-deep.md#af-errors-insufficientresources--status-insufficient-resources-too-many-concurrent-connections--client-handle-limit-2000-per-share--reduce-concurrent-mounts) |
| ClientOtherError | § [AF-Errors-ClientOtherError](./playbook-L-azure-files-deep.md#af-errors-clientothererror--azure-files-clientothererror-catch-all-for-client-side-errors-usually-harmless--xstorefrontend-logs-show-actual-cause--mostly-expected-client-disconnect--abort) |
| RestAPI Empty Value Response | § [AF-Errors-RestAPIEmpty](./playbook-L-azure-files-deep.md#af-errors-restapiempty--azure-files-restapi-empty-value-response-list-shares-or-list-files-returns-empty--firewall-blocking--invalid-sas-or-key--null-vs-not-set) |
| Copy Files File Explorer "Already Exists" | § [AF-Errors-CopyAlreadyExists](./playbook-L-azure-files-deep.md#af-errors-copyalreadyexists--copy-files-file-explorer-file-already-exists-error-case-sensitivity-mismatch-windows-vs-azure-files-storage-keeps-original-case-on-first-write) |
| Drive Mapped Under Different User | § [AF-Errors-DriveMappedDiffUser](./playbook-L-azure-files-deep.md#af-errors-drivemappeddiffuser--azure-files-drive-mapped-under-different-user-mount-persisted-in-credential-manager-under-other-account--use-cmdkey-delete-or-new-smbglobalmapping) |
| Empty Metrics Dimension In Portal | § [AF-Errors-EmptyMetricsDim](./playbook-L-azure-files-deep.md#af-errors-emptymetricsdim--empty-file-share-metrics-dimension-in-portal-no-data-on-file-share-name-dimension--customer-on-pre-2018-account--share-metrics-not-enabled--filter-by-tier-needed) |
| Unable to Delete File in Azure File Share | § [AF-Errors-UnableDeleteFile](./playbook-L-azure-files-deep.md#af-errors-unabledeletefile--unable-to-delete-file-in-azure-file-share-file-open-handle--lease--readonly-attribute--retention-lock--use-azfileshandlerclose) |
| Files Handles Closure (force-close handles) | § [AF-HowTo-HandlesClosure](./playbook-L-azure-files-deep.md#af-howto-handlesclosure--azure-files-handles-closure-how-to-list-and-force-close-handles-az-storage-share-list-handle--az-storage-share-close-handle--invoke-azfilesharehandle) |
| Unable to Create File Share | § [AF-Errors-UnableCreateShare](./playbook-L-azure-files-deep.md#af-errors-unablecreateshare--unable-to-create-file-share-sa-kind-incompatible-blobstorage-not-supported--quota-exceeded--region-not-supported--client-permissions-missing) |
| Azure Files vs Blob (clarification questions) | § [AF-HowTo-FilesVsBlob](./playbook-L-azure-files-deep.md#af-howto-filesvsblob--azure-files-versus-blob-protocol-smbnfsrest-vs-restonly--posix-vs-flat-namespace--scenario-decision-matrix-shared-fs-vs-object-store) |
| Azure Files Win7 / WS2008 R2 (legacy OS) | § [AF-HowTo-Win7-WS2008](./playbook-L-azure-files-deep.md#af-howto-win7-ws2008--azure-files-windows-7--windows-server-2008-r2-kb3114025-required--smb-21-only--secure-transfer-required-must-be-disabled-or-tls-12-cyphers-needed) |
| Mount VHD on File Share | § [AF-HowTo-MountVHD](./playbook-L-azure-files-deep.md#af-howto-mountvhd--mount-vhd-on-fileshare-store-vhdx-on-azure-files--mount-as-local-disk--workaround-for-app-compat-issues--latency-tradeoff) |
| Mounting Azure File Share Using a Specific User and Group | § [AF-HowTo-MountSpecificUserGroup](./playbook-L-azure-files-deep.md#af-howto-mountspecificusergroup--mounting-azure-file-share-using-a-specific-user-and-group-uid--gid--dir_mode--file_mode-mount-options-for-linux-cifs--username--password-for-windows-net-use) |
| Security Settings for SMB Protocols | § [AF-HowTo-SMBSecurity](./playbook-L-azure-files-deep.md#af-howto-smbsecurity--security-settings-for-smb-protocols-in-azure-file-shares-smb-30-31-version--smb-channel-encryption-aes-128-gcmaes-256-gcm--authentication-methods-ntlmv2-vs-kerberos--profile-max-compatibility) |
| Check IOPS on Azure File Share | § [AF-HowTo-CheckIOPS](./playbook-L-azure-files-deep.md#af-howto-checkiops--check-iops-on-azure-files-share-asc-performance-tab--azure-monitor--shoebox-mdm--per-share-limits-1000-iops-standard-or-provisioned-iops-premium) |
| Premium Files overview | § [AF-HowTo-Premium](./playbook-L-azure-files-deep.md#af-howto-premium--premium-files-overview-filestorage-account-kind--ssd-backed--provisioned-iops--lower-latency--baseline--burst-iops--throughput-formulas) |
| Large File Share (100 TiB) | § [AF-HowTo-LargeFileShare](./playbook-L-azure-files-deep.md#af-howto-largefileshare--large-file-share-overview--howto-100-tib--up-to-10000-iops--lrs-or-zrs-only-no-grsgzrs--enable-via-portal-or-powershell-no-disable-after-enable) |
| Hot + Cool Tiers for Azure Files | § [AF-HowTo-HotCoolTiers](./playbook-L-azure-files-deep.md#af-howto-hotcooltiers--hot--cool-tiers-for-azure-files-transactionoptimized-vs-hot-vs-cool-vs-archive-not-available-on-files--billing-implications--tier-change-impact) |
| OS Restrictions for Azure Files | § [AF-HowTo-OSRestrictions](./playbook-L-azure-files-deep.md#af-howto-osrestrictions--os-restrictions-for-azure-files-supported-windows-versions--linux-distros--macos--smb-21-minimum-vs-smb-3x-for-cross-region-on-prem--secure-transfer-required) |
| Azure Files FAQ | § [AF-HowTo-FAQ](./playbook-L-azure-files-deep.md#af-howto-faq--azure-files-faq-common-questions-decision-matrix-for-most-frequently-asked-customer-questions) |
| Audit File Share (auditing access) | § [AF-HowTo-AuditFileShare](./playbook-L-azure-files-deep.md#af-howto-auditfileshare--audit-file-share-diagnostic-settings-for-audit-logs--azure-files-audit-via-storageread--storagewrite--storagedelete-log-categories--retention) |
| SMB Multichannel | § [AF-HowTo-SMBMultichannel](./playbook-L-azure-files-deep.md#af-howto-smbmultichannel--smb-multichannel-premium-files-only--higher-throughput-per-client--enable-on-sa--client-must-have-multiple-nics-or-rss--troubleshoot-not-active) |
| User Delegation SAS for Azure Files | § [AF-HowTo-UDKSAS](./playbook-L-azure-files-deep.md#af-howto-udksas--user-delegation-sas-for-azure-files-uses-aad-credentials-instead-of-key--how-to-create-via-azure-cli--troubleshooting-permission-denied-or-signature-invalid) |
| Premium Provisioned V2 (new billing model) | § [AF-Premium-V2](./playbook-L-azure-files-deep.md#af-premium-v2--azure-files-provisioned-v2-model-overview-+-troubleshooting-provisioned-iops--bandwidth--decoupled-from-capacity--new-billing-model--limits--changes-vs-v1) |
| Zonal Placement (HowTo) | § [AF-Zonal-HowTo](./playbook-L-azure-files-deep.md#af-zonal-howto--how-to-create-azure-file-shares-with-zonal-placement-premium-lrs-only--specific-region-list--pin-to-az--align-vm-az--cross-link-K-cross-zone-traffic-detection) |
| Zonal Placement TSG | § [AF-Zonal-TSG](./playbook-L-azure-files-deep.md#af-zonal-tsg--azure-file-share-zonal-placement-tsg-eligibility-check--portal-config--verification--customer-misuse-non-eligible-config) |
| Managed File Shares (new feature) | § [AF-ManagedFileShares](./playbook-L-azure-files-deep.md#af-managedfileshares--managed-file-shares-overview--troubleshooting--query-logs-newer-managed-vs-classic-file-shares--feature-differences--per-share-management-api) |
| Azure Disk CSI Driver v2 (AKS use of File Shares) | § [AF-CSIDriver-v2](./playbook-L-azure-files-deep.md#af-csidriver-v2--azure-disk-csi-driver-v2-aks-pvc-using-azure-files--mounting-via-csi-driver--upgrade-from-v1--troubleshooting-pvc-mount-failures) |
| Files Emerging Issues (Files-All) | § [AF-EmergingIssues](./playbook-L-azure-files-deep.md#af-emergingissues--azure-files-emerging-issues-umbrella-network-credential-prompt-not-loading-mount-unc--rbac-smb-trackingid_2mp7-jp0--azure-files-identity-emerging) |
| **Files Slow Access via UNC Path** (Windows "Client for NFS" feature retries port 111 sunrpc — 5+ min open via UNC) | § [AF-Perf-SlowAccessUNCPath](./playbook-L-azure-files-deep.md#af-perf-slowaccessuncpath--azure-files-slow-access-via-unc-path-windows-client-for-nfs-feature-causes-nfsclntexe-port-111-sunrpc-retries--5-min-open-via-unc-mounted-drive-works-fine) (Remove Client for NFS feature + restart fixes; cross-link K § SAF-Win-Explorer-Slow if NFS feature NOT installed but Office files still slow) |

### Step 8 — Pull foundation evidence

| Data | Cluster.Database.Table | When |
|---|---|---|
| AFS Sync Server Telemetry (per-server sync events) | Jarvis MDM `KailaniSVC.ServerTelemetryEvents` | AFS sync error RCA (EventId 9121 for sync errors) |
| AFS Per-Item Sync Results (per-file detail) | Jarvis MDM `KailaniSVC.ServerItemResultsEvents` | AFS per-file failure (CorrelationId from ServerTelemetryEvents) |
| Azure Files Front End Logs (per-request) | Jarvis MDM `Xstore.XSMBPerfMetric / XNfsPerfMetric / FrontEndSummaryPerfLogs` | Mount + IO-level failure RCA (cross-link K § SA-Perf-AzureFiles-Backend) |
| Files-specific error transactions in ASC | ASC → SA → xDiagnostics → "Gather Failure Transactions" | Identify `IpAuthorizationError` (firewall) + per-error breakdown |
| Storage Account properties (kind / SKU / region / file endpoint) | `azcore.Xstore.XStoreAccountProperties` | Foundation (J § SA-Mgmt-* utility) |
| Cross-link AFS Cert Channel issues | Jarvis MDM `KailaniSVC.ServerCertEvents` | AFS cert expiry / revocation cases |
| AFS Heat Store events (cloud tiering) | EventLog StorageSync channel | Local server-side (use AFSDiag to collect) |

Foundation KQL bodies in [`references/storage-account-queries.md`](../catalogs/storage-account-queries.md). AFS Jarvis queries inline in deep file.

### Step 9 — Mitigation + handoffs

| Scenario | Owner |
|---|---|
| **AFS sync session corruption / agent stuck** (after exhausting TSG steps) | **AFS PG** via ICM (XSync queue) — collect AFSDiag + Get-StorageSync* output |
| **AFS Cert revocation cascading recall failure** | AFS PG via ICM — provide server cert thumbprint + cert chain validation results |
| **Azure Files cross-zone latency** (Zonal Placement preview not yet available in region) | → **Playbook K § SA-Perf-AzureFiles-Backend** Zonal Placement signup form |
| **Heavy metadata throttling** (Files metadata IOPS) | → **Playbook K § SA-Perf-AzureFiles-HeavyMetadata** + § SA-Perf-AzureFiles-MetadataCaching |
| **SA-level throttling** (1000 IOPS / 60 MB/s per share hit) | → **K § SA-Perf-SAThrottle** + J § SA-Mgmt-IncreaseLimits |
| **SMB Identity AAD Kerb deep escalation** (after exhausting flow) | **Storage AAD Kerb PG** via ICM (CSS AAD Kerb queue) — provide Fiddler trace + Jarvis OAuth REST logs |
| **AD DS join failures** | AD team for cert / DC / trust issues; CSS AzFilesHybrid module owner for module-side issues |
| **NFS protocol regression / encryption-in-transit bug** | NFS PG via ICM (Premium Files PG, SMB+NFS team) |
| **Soft-deleted File Share recoverable** | Customer follows portal restore steps (Soft Delete TSG); NOT recoverable post-retention |
| **File share permanently deleted / no snapshot or backup** | → **Playbook J § SA-Recovery-FilesSMB** (PG Sev 3 ICM only, best-effort) |
| **AFS agent install MSI generic failure** | TSG 222 MSI logs → if PG-only → AFS PG ICM with installation logs |
| **Tiered file orphaned by unregister-server** | **Cannot recover automatically** — orphaned files may be permanently lost (re-tier from cloud after recreate SEP) |
| **Customer wants to use AFS in unsupported region** (France South / South Africa West / UAE Central) | Customer requests Storage access via Azure Marketplace before AFS deployment |
| **MI-related AFS sync sudden failure** | Verify MI not deleted (cross-link J § SA-CMK-KVTokenCannotBeAcquired pattern for UAMI delete detection) |

## Cross-references

| Other playbook / reference | Why |
|---|---|
| Playbook J § SA-Recovery-FilesSMB | Recover deleted Azure Files SMB share (PG Sev 3 ICM, best-effort) |
| Playbook J § SA-Util-LookupCRUD-CtrlPlane | SA CRUD ops (when SA-level config change suspected) |
| Playbook J § SA-Mgmt-IncreaseLimits | Quota increase for file share IOPS / throughput |
| Playbook K § SA-Perf-AzureFiles-Backend | XStore backend perf RCA (XFileFE Read/Write + per-share limits + cross-zone) |
| Playbook K § SA-Perf-AzureFiles-HeavyMetadata | Metadata IOPS throttling (`SuccessWithMetadataWarning/Throttling`) |
| Playbook K § SA-Perf-AzureFiles-MetadataCaching | Premium SMB Metadata Caching feature enablement |
| Playbook K § SAF-AzureFiles-PerfWorkflow | Master perf entry-point scoping (referenced from L perf cases) |
| Playbook K § SAF-Win-Explorer-Slow | Windows Explorer slow file open/save/close (registry workaround) |
| Playbook G | Guest-OS perf when Client Latency >> Server Latency |
| Playbook I | If MSI fails (SAC) or IMDS issues on AFS server |
| Playbook H | If ADE/AGEX on AFS agent server |
| `references/storage-account-queries.md` | Foundation KQL (SA props, XArgus perf, throttling) |
| https://aka.ms/iridias | Active Storage LSI check (FIRST step for any "suddenly broken" case) |
| https://aka.ms/xportal | SA tenant + Shoebox API Investigation |
| https://github.com/Azure-Samples/azure-files-samples | AzFileDiagnostics (Win + Linux) + SMBClientLogs + SMBDiagnostics scripts |
