# Playbook H — Agent + Extension (AGEX + ADE) — Core

> **Companion to** [`playbook-H-agent-extension-deep.md`](./playbook-H-agent-extension-deep.md). Use this file as the **routing entry point** when a case is about a Guest Agent issue (WaAppAgent / WALinuxAgent / RDAgent), an extension failure (CSE / RunCommand / VMAccess / Domain Join / Performance Diagnostics / Hibernation / Backup / Monitoring), or an Azure Disk Encryption (ADE / SSE+CMK / Encryption at Host) issue. Full bodies live in deep file under `AGEX-* / ADE-* / SSE-*` anchors.

## When to use this playbook

| Use Playbook H when... | Don't — use instead |
|---|---|
| Guest agent stuck Not Ready, no heartbeat, status not reporting | Brand new VM deploy where GA never came up → Playbook G § DEPLOY-Provision-OSPTO |
| Extension Transitioning / Failed at runtime (after VM exists) | Extension blocked at VM create by Azure Policy → Playbook G § DEPLOY-Policy-Denied |
| 90-min op delay caused by hung extension | Long deploy from Marketplace image → Playbook G § DEPLOY-Alloc-LongDeploy |
| CSE / Run Command / VMAccess / Domain Join errors | Hibernation extension at VM create → Playbook G § DEPLOY-Hibernate-Fails |
| ADE encryption setup / KV access / Bitlocker errors | ADE attach blocked on PV2/Ultra → Playbook F § MD-Encryption-1 |
| ADE secret recovery (VM can't boot) | CMK disk recovery (find DES for deleted CMK disks) → Playbook F § MD-Encryption-2 |
| SSE+CMK fails to encrypt PV2/Ultra with User MI | Generic disk encryption at host EAH OSPTO at create → § ADE-EncryptionAtHost-OSPTO (this playbook — cross-link to G § DEPLOY-Provision-OSPTO) |
| Auto-extension-upgrade not happening | New SKU not supported for sub → Playbook G § DEPLOY-Alloc-SkuNotAvailable |

## Inputs to collect

| # | Item | Why |
|---|---|---|
| 1 | `SubscriptionId` + `ResourceGroupName` + `VMName` | Primary filters |
| 2 | `VMId` (VirtualMachineUniqueId) | For `azcore.Fa.GuestAgentExtensionEvents` queries |
| 3 | `ContainerId` (from `LogContainerSnapshot`) | Same; some queries take ContainerId not VMId |
| 4 | Extension name + publisher + version | Routes to specific anchor |
| 5 | Error message + error code (verbatim) | Most TSGs are error-code-routed |
| 6 | OS family (Windows vs Linux) | Different log paths + different cmdlets |
| 7 | StartTime / EndTime (UTC) | Pad ±15 min |
| 8 | CorrelationId / OperationId | For ARM + CRP correlation |
| 9 | KV name + AAD app ClientID (for ADE) | KV access policy validation |

## Step-by-step

### Step 1 — Identify problem domain (GA vs Extension vs Encryption)

| Symptom | Goes to... |
|---|---|
| VM Agent status "Not Ready" / not heartbeating / extensions stuck Transitioning regardless of which extension | Step 2 (Guest Agent) |
| Specific extension errors with the agent otherwise Ready | Step 3 (Extension) |
| ADE / SSE+CMK / Encryption-at-Host related errors | Step 4 (Encryption) |

### Step 2 — Guest Agent routing

| Symptom | Anchor |
|---|---|
| Windows GA works but Status: Not Reported + `TransparentInstaller.log` shows 168.63.129.16 timeout + 3rd-party AV present | § [AGEX-GA-StatusNotReported-Win](./playbook-H-agent-extension-deep.md#agex-ga-statusnotreported-win--windows-ga-not-reporting-status-3rd-party-av) |
| Windows GA / extension process disappears + Event Log faulting app | § [AGEX-GA-Crash-Win](./playbook-H-agent-extension-deep.md#agex-ga-crash-win--windows-ga--extension-crash-dump-procedure-procdump--windbg) |
| Windows Firewall blocks 168.63.129.16 ports 80/32526 / `Test-NetConnection` timeout / multi-IP VM routing | § [AGEX-GA-FirewallWireServer-Win](./playbook-H-agent-extension-deep.md#agex-ga-firewallwireserver-win--windows-firewall-blocking-168631291680--32526) |
| `Keyset does not exist` / `Decrypting Protected Settings - Invalid provider type specified` / `Failed to get TransportCertificate` | § [AGEX-GA-CryptoCert-Win](./playbook-H-agent-extension-deep.md#agex-ga-cryptocert-win--keyset-does-not-exist--machinekeys-acl-fix) |
| Windows GA not auto-upgrading despite Ready + WireServer working + `Manifest timestamp has not changed` | § [AGEX-GA-NotAutoUpgrading-Win](./playbook-H-agent-extension-deep.md#agex-ga-notautoupgrading-win--windows-ga-not-auto-upgrading-manifest-timestamp-bug) |
| Linux `waagent.log`: `WireServer is not responding ... IOError timed out` (SUSE wicked or similar NM bouncing NIC) | § [AGEX-GA-WireServerIOError-Linux](./playbook-H-agent-extension-deep.md#agex-ga-wireserveriomerror-linux--linux-wireserver-not-responding--ioerror-timed-out) |
| Linux `ConnectionRefusedError [Errno 111]` + `nc -v 168.63.129.16` timeout / iptables or nftables blocking | § [AGEX-GA-ConnectivityBlocked-Linux](./playbook-H-agent-extension-deep.md#agex-ga-connectivityblocked-linux--linux-iptablesnftables-blocking-wireserver) |
| Linux `waagent --version` shows OLD version + `permanently blacklisted` in waagent.log | § [AGEX-GA-OldGoalState-Blacklist](./playbook-H-agent-extension-deep.md#agex-ga-oldgoalstate-blacklist--linux-walinuxagent-permanently-blacklisted-after-bad-upgrade) |

### Step 3 — Extension routing

| Symptom | Anchor |
|---|---|
| Customer complains op took 90 min — extension stuck Transitioning | § [AGEX-Ext-90minTimeout](./playbook-H-agent-extension-deep.md#agex-ext-90mintimeout--90-minute-extension-timeout-blocks-vm-ops) |
| `Timed out waiting for extension <X> to reach a terminal state` | § [AGEX-Ext-TimedOutWaiting](./playbook-H-agent-extension-deep.md#agex-ext-timedoutwaiting--timed-out-waiting-for-extension-handler-vs-extension) |
| `RequestDisallowedByPolicy: Resource '<X>' was disallowed by policy ... "Only approved VM extensions should be installed"` | § [AGEX-Ext-AzurePolicy](./playbook-H-agent-extension-deep.md#agex-ext-azurepolicy--extension-deploymentfailed-duetoazurepolicy-only-approved-extensions) |
| Auto Extension Upgrade enabled but not happening / maintenance config blocks | § [AGEX-Ext-AutoUpgrade](./playbook-H-agent-extension-deep.md#agex-ext-autoupgrade--automatic-extension-upgrade-not-happening-rsm_prod-rollout--maintenance-policy-block) |
| CSE: `Exceeded maximum file download time` | § [AGEX-Ext-CSE-DownloadTimeout](./playbook-H-agent-extension-deep.md#agex-ext-cse-downloadtimeout--cse-30-min-file-download-cap) |
| CSE on AKS VMSS: `exit status=50` or `exit status=124` | § [AGEX-Ext-CSE-ExitCode50-124](./playbook-H-agent-extension-deep.md#agex-ext-cse-exitcode50-124--cse-aks-vmss-exit-code-50--124-network-block) |
| CSE Linux: `Timed out waiting for lock on custom-script-extension` | § [AGEX-Ext-CSE-Lock](./playbook-H-agent-extension-deep.md#agex-ext-cse-lock--cse-timed-out-waiting-for-lock-customer-script-too-long) |
| CSE: storage account 403 / DNS / SAS / MI / PE failures | § [AGEX-Ext-CSE-Storage](./playbook-H-agent-extension-deep.md#agex-ext-cse-storage--cse-storage-account-failures-sa-firewall--pe--mi--sas) |
| `RunCommandConflict: Run command extension execution is in progress` | § [AGEX-Ext-RunCommand-Conflict](./playbook-H-agent-extension-deep.md#agex-ext-runcommand-conflict--runcommandconflict-existing-rc-still-running) |
| `FabricInternalOperationError: A different extension upgrade info ... with the same key has already been added to extensionVersions. Key: Microsoft.CPlat.Core.RunCommandHandlerWindows` | § [AGEX-Ext-RunCommand-FabricOpFailed](./playbook-H-agent-extension-deep.md#agex-ext-runcommand-fabricopfailed--rc-v2-upgrade-extensionversion-conflict-mitigation) |
| Any VMAccess extension error (9-error table) | § [AGEX-Ext-VMAccess-Umbrella](./playbook-H-agent-extension-deep.md#agex-ext-vmaccess-umbrella--vmaccess-errors-9-error-routing-table) |
| Domain Join: `Failed to initiate system shutdown` | § [AGEX-Ext-DomainJoin-Shutdown](./playbook-H-agent-extension-deep.md#agex-ext-domainjoin-shutdown--domain-join-failed-to-initiate-system-shutdown) |
| Azure Performance Diagnostics fails `VMExtensionProvisioningError` + `MD5CryptoServiceProvider` + FIPS validated | § [AGEX-Ext-PerfDiagnostics-FIPS](./playbook-H-agent-extension-deep.md#agex-ext-perfdiagnostics-fips--azure-performance-diagnostics-fails-with-vmextensionprovisioningerror-fips-mode) |
| `C:\WindowsAzure\Logs` filling with `RuntimeEvents_*.etl.old` / `WaAppAgent_*.etl.old` consuming disk space | § [AGEX-GA-Logs-ETLDiskFillup](./playbook-H-agent-extension-deep.md#agex-ga-logs-etldiskfillup--c-windowsazure-logs-filling-with-runtimeevents--waappagent-etlold) |

### Step 4 — Encryption routing (ADE + SSE+CMK + EAH)

| Symptom | Anchor |
|---|---|
| ADE Bitlocker.log: `Failed to configure bitlocker as expected. Exception: Access denied` | § [ADE-AccessDenied](./playbook-H-agent-extension-deep.md#ade-accessdenied--access-denied--failed-to-configure-bitlocker-as-expected-aad-app--kv-access-policy) |
| ADE: `secret doesn't have the DiskEncryptionKeyEncryptionAlgorithm tags` (KV was moved between subs/tenants) | § [ADE-KVTenantID-Wrong](./playbook-H-agent-extension-deep.md#ade-kvtenantid-wrong--key-vault-associated-to-wrong-tenantid-kv-moved-tenants) |
| ADE: `Keyvault not found in the directory` | § [ADE-KVNotFoundDirectory](./playbook-H-agent-extension-deep.md#ade-kvnotfounddirectory--keyvault-not-found-in-the-directory-aad-tenant-mismatch) |
| ADE: `networkAcls.bypass must include "AzureServices"` | § [ADE-NetworkAclsBypass](./playbook-H-agent-extension-deep.md#ade-networkaclsbypass--networkacls-bypass-must-include-azureservices) |
| `DiskEncryptionKeySecretRetrievalFailed` / encrypted VM can't boot | § [ADE-VMStartup-SecretRetrievalFailed](./playbook-H-agent-extension-deep.md#ade-vmstartup-secretretrievalfailed--diskencryptionkeysecretretrievalfailed-vm-cant-boot-after-encryption) |
| ADE finishes but data disks (esp. WS2012 + Storage Spaces) silently skipped | § [ADE-DataDisksSkipped](./playbook-H-agent-extension-deep.md#ade-datadisksskipped--data-disks-silently-skipped-extension-v2203736-regression) |
| Linux ADE VM boots prompting for passphrase / `LinuxPassPhraseFileName_1_0 missing` (FAD + ADE conflict) | § [ADE-DataDiskSecretsMissing](./playbook-H-agent-extension-deep.md#ade-datadisksecretsmissing--data-disk-secrets-missing-on-bek-volume-fad--ade-conflict) |
| Encryption at Host (EAH) at VM create: `OSProvisioningTimedOut` with no guest logs | § [ADE-EncryptionAtHost-OSPTO](./playbook-H-agent-extension-deep.md#ade-encryptionathost-ospto--encryption-at-host-eah-osprovisioningtimeout-prereq-failures) |
| SSE+CMK on PV2/Ultra: `DirectDriveDiskNotSupportUserAssignedIdentityDes` | § [SSE-PV2-Ultra-UserMI](./playbook-H-agent-extension-deep.md#sse-pv2-ultra-usermi--ssecmk-fails-to-encrypt-premiumssdv2--ultra-with-user-assigned-mi) |
| SSE+CMK VM in Failed state + `KeyVaultAccessForbidden` OR `Unable to access key ... Key is expired` | § [SSE-KeyVaultAccessForbidden](./playbook-H-agent-extension-deep.md#sse-keyvaultaccessforbidden--ssecmk-fails-with-keyvaultaccessforbidden--key-expired) |
| SSE+CMK VM Start fails `KeyVaultKeyNotEnabled` / DES key disabled in KV | § [SSE-KeyDisabled](./playbook-H-agent-extension-deep.md#sse-keydisabled--ssecmk-vm-start-fails-keyvaultkeynotenabled-cmk-key-was-disabled) |
| `OperationNotAllowed: Disk '<>' was previously encrypted with Azure Disk Encryption` when enabling SSE+CMK | § [SSE-WasPreviouslyADE](./playbook-H-agent-extension-deep.md#sse-waspreviouslyade--ssecmk-fails-disk-was-previously-encrypted-with-ade-ude-flag-persists) |
| CMK Storage Account: `ManagedServiceIdentityNotFound: MSI was not found for resource ''` | § [SSE-MSINotFound](./playbook-H-agent-extension-deep.md#sse-msinotfound--cmk-storage-account-managedserviceidentitynotfound-msi-deleted) |
| RHEL 9 enters Emergency mode after enabling ADE + `bootuuid=` empty + boot mount timeout | § [ADE-RHEL9-BootMountFailure](./playbook-H-agent-extension-deep.md#ade-rhel9-bootmountfailure--rhel-9-emergency-mode-after-enabling-ade-bls-cmdline-missing-update-bls-cmdline) |
| Need to unlock encrypted Linux/Windows disk for offline repair / log collection (BEK+KEK, with/without AAD) | § [ADE-Recovery-Unlock](./playbook-H-agent-extension-deep.md#ade-recovery-unlock--unlock-encrypted-linux--windows-disk-ade-recovery) |
| Migrate ADE Dual Pass (with AAD) \u2192 Single Pass (no AAD) — Windows 1.1.* \u2192 2.2 / Linux 0.1.* \u2192 1.2 | § [ADE-Migration-DualToSingle](./playbook-H-agent-extension-deep.md#ade-migration-dualtosingle--migrate-ade-dual-pass-with-aad--single-pass-no-aad) |
| Migrate from ADE to Encryption at Host (retirement 2028-09-15) — preserve UDE-aware migration | § [ADE-Migration-To-EAH](./playbook-H-agent-extension-deep.md#ade-migration-to-eah--migrate-from-ade-to-encryption-at-host-retirement-2028-09-15) |
| Need to escalate ADE / SSE+CMK / EAH issue to PG/EEE | § [ADE-IcMTemplate](./playbook-H-agent-extension-deep.md#ade-icmtemplate--asc-escalation-template-h3s3mb-for-eepg) (ASC template `h3s3mb`) |

### Step 5 — Pull foundation evidence

Delegate to `references/azcore-queries.md` § Guest Agent & Extensions:

**Heartbeat + extension status**:
```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').GuestAgentExtensionEvents
| where ContainerId == '{ContainerId}'
| where PreciseTimeStamp > ago(2h)
| where Operation in ('HeartBeat', 'ReportStatus', 'VmSettingsSummary')
| top 10 by PreciseTimeStamp desc
| project PreciseTimeStamp, GAVersion, OSVersion, Operation, OperationSuccess, Name, Version, Message, ContainerId, VMId
```

**All extension errors**:
```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').GuestAgentExtensionEvents
| where ContainerId == '{ContainerId}'
| where PreciseTimeStamp >= datetime({StartTime}) and PreciseTimeStamp <= datetime({EndTime})
| where OperationSuccess == false
| project PreciseTimeStamp, GAVersion, OSVersion, Operation, Name, Version, Message, ContainerId, VMId
```

### Step 6 — Apply anchor logic

Each deep-file anchor provides: scope, error signatures, log-file paths (in-guest), KQL bodies, customer-facing mitigation steps, escalation paths.

### Step 7 — Cross-RP / specialized investigation

| Need | Tool |
|---|---|
| ARM correlation chain through extension PUT | `armprodgbl.eastus.ARMProd.EventServiceEntries` macro-expand |
| Extension PUT via CRP | `azcrp.crp_allprod.ApiQosEvent_nonGet` + `VMApiQosEvent` |
| AutoExtensionUpgrade rollout status | `azmc2.centralus.rsm_Prod.VMAutoExtensionUpgradeEvent` + `VMStateEvent` + `j_smdRtoRegionToPhaseMapRegular()` |
| ARM Jobs trace (RC) | `armprodgbl.eastus.ARMProd.Jobs.JobTraces` (PG-restricted) |
| Extension logs persisted to AzCore | `azcore.Fa.GuestAgentExtensionEvents` filtered by `VMId` + extension `Name` |
| ADE Bitlocker logs (Windows in-guest) | `C:\WindowsAzure\Logs\Plugins\Microsoft.Azure.Security.AzureDiskEncryption\<version>\Bitlocker.log` |
| Guest agent logs (Windows) | `C:\WindowsAzure\Logs\WaAppAgent.log`, `TransparentInstaller.log`, App Event Log |
| Guest agent logs (Linux) | `/var/log/waagent.log`, `/var/log/azure/<extension>/`, `journalctl -u walinuxagent` |

### Step 8 — Mitigation + handoffs

| Scenario | Owner |
|---|---|
| GA cert/crypto deep dive needing SChannel trace | **Windows Domain/Directory crypto team** (after CAPI2 + Schannel trace) |
| GA dump analysis with private symbols | **EEE** (Reddog share access needed) |
| WireServer connectivity sporadic / DHCP / network bouncing | **WALinuxAgent dev team** (Linux) OR **Windows on Azure SMEs** |
| 3rd-party software blocking GA / extension | Customer engages their AV/security vendor |
| Azure Policy blocking extension | **Azure Policy team** via AVA / TA — SAP `Azure/Azure Policy/Policy behavior not as expected/Policy enforcement not as expected` |
| Auto Extension Upgrade not happening (specific publisher) | Check `aka.ms/vmextensionspublishers` + extension publisher SME |
| AKS CSE network failure | **OPEX Collaboration Optimization AzNet** OR **AKS Support** via SAP `Azure/Kubernetes Service (AKS)/Create, Upgrade, Scale and Delete operations` |
| ADE / SSE+CMK / EAH escalation | **EEE/PG** via ASC template **`h3s3mb`** |
| FAD + ADE conflict sub-wide disable | **PG ICM** to stop FAD on subscription basis |
| RC v2 upgrade bug (extensionVersions conflict) | Self-mitigated via `Remove-AzVMRunCommand` loop (no escalation needed) |

## Cross-references

| Other playbook / reference | Why |
|---|---|
| Playbook B § OP-OSPTO | OSPTO on existing VMs — Playbook H cross-links here when GA never came up |
| Playbook F § MD-Encryption-1 | PV2/Ultra disk attach blocked by ADE-tagged VM (different angle — disk-side) |
| Playbook F § MD-Encryption-2 | Find DES for deleted CMK disks (Playbook F owns this) |
| Playbook G § DEPLOY-Hibernate-Fails | Hibernation extension at first-create (H owns first-create; J owns existing VM extension issues) |
| Playbook G § DEPLOY-Policy-Denied | Generic `RequestDisallowedByPolicy` at VM/PIP/NSG level. § AGEX-Ext-AzurePolicy is the extension-specific variant |
| Playbook G § DEPLOY-Provision-OSPTO | Generic deploy-time OSPTO. § ADE-EncryptionAtHost-OSPTO is the EAH-specific subset |
| `references/azcore-queries.md` § Guest Agent & Extensions | `GuestAgentExtensionEvents` foundation queries (HeartBeat / ReportStatus / VmSettingsSummary) |
| `references/crp-queries.md` | CRP ApiQosEvent / ContextActivity for extension PUTs |
| `vm-log-analyzer` skill | Guest log analysis (waagent.log, cloud-init.log, Bitlocker.log, journal) |
