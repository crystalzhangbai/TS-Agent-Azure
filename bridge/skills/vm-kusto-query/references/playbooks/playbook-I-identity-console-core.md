# Playbook I — Identity & Console (IMDS + MSI + SAC) — Core

> **Companion to** [`playbook-I-identity-console-deep.md`](./playbook-I-identity-console-deep.md). Use this as the **routing entry point** when a case is about:
>
> - **IMDS** — `169.254.169.254` reachability, error codes, GuestProxyAgent / MSP enforcement
> - **MSI** — Managed Service Identity (System or User Assigned) token acquisition + Azure Policy auto-re-enable
> - **SAC** — Serial Access Console connect failures, in-guest EMS/BCD config, host-side rdnpc, SACSVR health

Full bodies live in deep file under `IMDS-* / MSI-* / SAC-*` anchors.

## When to use this playbook

| Use Playbook I when... | Don't — use instead |
|---|---|
| IMDS `169.254.169.254` unreachable / 4XX / 5XX | Generic VM networking issue → `networking-queries.md` direct |
| `az login --identity` returns 403 / MSI token fails | CMK Storage Account MSI deleted → Playbook H § SSE-MSINotFound |
| System-Assigned MI auto-re-enables itself after disable | Azure Policy blocking extension install → Playbook H § AGEX-Ext-AzurePolicy |
| SAC connect errors (400 / 403 / 404 / 429) | RDP/SSH bucket — `Cant-RDP-SSH` workflow |
| Serial Console stops working after VM restart (host rdnpc) | Generic VM restart RCA → Playbook A |
| EMS not configured in Guest OS (BCD missing) | VM Non-boot recovery → `/SME-Topics/Cant-RDP-SSH/Non-Boot` |
| SACSVR service hung/crashed (Windows Service Control Mgr codes 5/1053/1058/etc) | Generic Windows perf / hang case |
| GuestProxyAgent / MSP / InVmAccessControlProfile blocks app access | Extension provisioning failure → Playbook H § AGEX-Ext-* |

## Inputs to collect

| # | Item | Why |
|---|---|---|
| 1 | `SubscriptionId` + `ResourceGroupName` + `VMName` | Primary filters |
| 2 | NodeId (for IMDS host-side Wireserver query) | `WireserverHeartbeatEtwTable` |
| 3 | VM size + OS family (Win vs Linux) | v5 Ice Lake check for SAC; BCD vs grub for EMS |
| 4 | Error message + HTTP code (verbatim) | 400/403/404/429 routing for SAC; 4XX/5XX for IMDS |
| 5 | StartTime / EndTime (UTC) | Pad ±15 min |
| 6 | CorrelationId (for MSI auto-re-enable case) | ARMProd PolicyServiceDebug |
| 7 | Boot Diagnostics storage account name | SA firewall + HNS check |
| 8 | Primary NIC + Primary IP | IMDS routing fix |

## Step-by-step

### Step 1 — Identify problem domain (IMDS vs MSI vs SAC)

| Symptom | Goes to... |
|---|---|
| `169.254.169.254` unreachable / IMDS HTTP error | Step 2 (IMDS) |
| `az login --identity` 403 OR system MI keeps re-enabling | Step 3 (MSI) |
| Serial Console error message / cannot connect to SAC | Step 4 (SAC) |

### Step 2 — IMDS routing

| Symptom | Anchor |
|---|---|
| Generic "cannot reach 169.254.169.254" — Proxy / FW / Wireserver / routing — start here | § [IMDS-Reach-CannotReach](./playbook-I-identity-console-deep.md#imds-reach-cannotreach--cannot-reach-server-umbrella-proxy--firewall--wireserver--routing) |
| Multi-NIC VM + IMDS unreachable + no FW/AV — primary-NIC routing rule | § [IMDS-Reach-MultiNic](./playbook-I-identity-console-deep.md#imds-reach-multinic--bad-routing-multiple-nics--imds-primary-nic-only-rule) |
| Win Server 2008R2/2012R2 ESU install fails (`ERROR_INSTALL_TRANSFORM_FAILURE 1624` / `ERROR_NO_SIGNATURE 951` / `CRYPT_E_NOT_FOUND` / `E_FAIL`) + log shows `ESU: Checking IMDS` | § [IMDS-Reach-Win2012-ESU](./playbook-I-identity-console-deep.md#imds-reach-win2012-esu--esu-installation-fails-due-to-imds-unreachable-2008r2--2012r2) |
| Need IMDS HTTP status code meaning / want a reproducible in-guest test | § [IMDS-Token-ErrorCodes](./playbook-I-identity-console-deep.md#imds-token-errorcodes--imds-http-error-code-table--in-guest-test-script) |
| Per-4xx code (400/404/405/410/429) deep dive with mitigation | § [IMDS-Token-4xx](./playbook-I-identity-console-deep.md#imds-token-4xx--4xx-error-deep-dive-400--404--405--410--429) |
| 5xx error — host-side / dependency component failing (CRP/NRP/DRP/AAD) | § [IMDS-Token-5xx](./playbook-I-identity-console-deep.md#imds-token-5xx--5xx-error-deep-dive-imdsapirequests-kql--icm-component-routing-table) (`ImdsApiRequests` KQL + ICM team table per endpoint) |
| Need to remind self of IMDS hard limits (5 QPS / no container / 500 = host) | § [IMDS-Token-KnownIssues](./playbook-I-identity-console-deep.md#imds-token-knownissues--imds-hard-facts-rate-limit--containers--host-side) |
| App access to WireServer/IMDS blocked + GuestProxyAgent installed (`InVmAccessControlProfile` not whitelisting app) | § [IMDS-GuestProxyAgent](./playbook-I-identity-console-deep.md#imds-guestproxyagent--vm-applications-access-to-wireserveroimds-fails-msp--invmaccesscontrolprofile) |
| GPA VM extension status / module start health / connection summary / port 3080 conflict | § [IMDS-GPA-Extension-Telemetry](./playbook-I-identity-console-deep.md#imds-gpa-extension-telemetry--guest-proxy-agent-vm-extension-status--connection-summary-via-azcore-fa-kql) (4 KQL: GuestAgentExtensionEvents, CRP PUT/PATCH, GPA module start, proxied connection summary) |
| Need to capture netsh / Wireshark / tcpdump for IMDS troubleshooting | § [IMDS-Util-NetTrace](./playbook-I-identity-console-deep.md#imds-util-nettrace--collect-network-traces-windows-netshetl2pcapng-wireshark-linux-tcpdump) |
| Need IMDS host-side KQL functions `ImdsErrors` / `ImdsApiRequests` / `ImdsHeartbeats` | § [IMDS-Util-HostKQL](./playbook-I-identity-console-deep.md#imds-util-hostkql--host-side-imds-kql-functions-imdserrors--imdsapirequests--imdsheartbeats) |
| `ImdsApiRequests` doesn't show the call — check raw WireServer host logs | § [IMDS-Util-WireServerLogs](./playbook-I-identity-console-deep.md#imds-util-wireserverlogs--troubleshoot-imds-via-host-wireserver-logs-wiremarshal--rest-log-grep-patterns) (WireMarshal + REST log grep patterns) |

### Step 3 — MSI routing

| Symptom | Anchor |
|---|---|
| `az login --identity` → `Get Token request returned http error: 403, reason: Forbidden` (System-Assigned MI) | § [MSI-System-403](./playbook-I-identity-console-deep.md#msi-system-403--system-assigned-mi-403-forbidden-on-az-login-identity) |
| Customer disables system-assigned MI but it auto-re-enables after minutes / Azure Policy enforces MI on VMs | § [MSI-CannotDelete-Policy](./playbook-I-identity-console-deep.md#msi-cannotdelete-policy--cannot-delete-system-assigned-mi-azure-policy-auto-re-enables) |
| `ManagedServiceIdentityAccessInternalError` after subscription tenant move | § [MSI-AccessInternalError-TenantMove](./playbook-I-identity-console-deep.md#msi-accessinternalerror-tenantmove--managedserviceidentityaccessinternalerror-after-tenant-move-azmsicl-trace) (3-KQL chain crp_allprod + azmsicl; **CSS Cloud Identity**, NOT AzureRT) |
| General-purpose MSI RP telemetry (any MSI delay or error from CRP / ARM angle) | § [MSI-Util-AzMsiCl](./playbook-I-identity-console-deep.md#msi-util-azmsicl--msi-rp-telemetry-azmsiclazmsidb-operationevent--customtraceevent--httpoutgoing-3-kql) (3-KQL pattern + CoreIdentity MSI-Telemetry access steps) |
| PerfInsights install unexpectedly removed user-assigned MI from VM | § [MSI-PerfInsights-Removal](./playbook-I-identity-console-deep.md#msi-perfinsights-removal--perfinsights-install-removes-user-assigned-mi-from-vm-identity-block-bug) |

### Step 4 — SAC routing

#### Step 4a — Connect-time errors (HTTP code routing)

| Symptom | Anchor |
|---|---|
| `'Bad Request' (400) - Boot diagnostics settings ... is disabled` OR `power state is deallocated` OR `storage account ... could not be found` OR `Invalid boot diagnostics storage account ... kind is one of: BlobStorage, BlockBlobStorage, FileStorage, or Storage` OR bare `(400) - BadRequest` | § [SAC-Connect-400](./playbook-I-identity-console-deep.md#sac-connect-400--sac-400-bad-request-umbrella-5-causes-bd-disabled--deallocated--sa-deleted--adls-gen2--uri-mismatch) (5-cause umbrella) |
| `'Forbidden (403) - Forbidden'` OR `A 'Forbidden' response was encountered when accessing this VM's boot diagnostic storage account` | § [SAC-Connect-403](./playbook-I-identity-console-deep.md#sac-connect-403--sac-403-forbidden-rbac-missing-vm-contributor-or-sa-firewall-blocking) |
| `'Not Found' (404) - Unable to retrieve boot diagnostics settings` | § [SAC-Connect-404](./playbook-I-identity-console-deep.md#sac-connect-404--sac-404-not-found-boot-diagnostics-disabled) |
| `'ERR_BAD_REQUEST' (429) - Request failed with status code 429` | § [SAC-Connect-429](./playbook-I-identity-console-deep.md#sac-connect-429--sac-429-err_bad_request-sa-firewall-blocks-serialconsole-service-tag-ips) |
| `'ERR_BAD_REQUEST' (409) - Request failed with status 409` (Read-Only lock on VM or RG) | § [SAC-Connect-409](./playbook-I-identity-console-deep.md#sac-connect-409--sac-409-err_bad_request-read-only-lock-blocks-post-action) |
| `(ServiceUnavailable) - Cloud Shell is not available at this moment` | § [SAC-Connect-ServiceUnavailable](./playbook-I-identity-console-deep.md#sac-connect-serviceunavailable--cloud-shell-is-not-available-acs-lsi-or-region-issue) (ACS LSI; fallback to v2 preview)

#### Step 4b — Host + guest service issues

| Symptom | Anchor |
|---|---|
| After Stop/Start: `Sorry, the serial console was unable to connect to the VM because the service did not respond in a timely manner` — multiple VMs on same node affected | § [SAC-Host-RdnpcStuck](./playbook-I-identity-console-deep.md#sac-host-rdnpcstuck--serial-console-not-working-after-vm-restart-rdnamedpipecapture-stuck) |
| Same "service did not respond" message but on Azure v5 series (Dv5/Ev5/etc) — Ice Lake incompatibility | § [SAC-Guest-ServiceTimeout](./playbook-I-identity-console-deep.md#sac-guest-servicetimeout--sac-service-did-not-respond-linux-ems-config--azure-v5-ice-lake-incompatibility) (RC 2) |
| Same "service did not respond" message on non-v5 + Linux guest (firewall / unendorsed distro / EMS not set up) | § [SAC-Guest-ServiceTimeout](./playbook-I-identity-console-deep.md#sac-guest-servicetimeout--sac-service-did-not-respond-linux-ems-config--azure-v5-ice-lake-incompatibility) (RC 1) |

#### Step 4c — Windows-specific BCD / EMS / SACSVR

| Symptom | Anchor |
|---|---|
| `An error occurred while attempting to access the boot configuration data. The system cannot find the file specified` (when enabling EMS) | § [SAC-Win-BCDMissingEMS](./playbook-I-identity-console-deep.md#sac-win-bcdmissingems--system-cannot-find-file-bcd-store-missing-ems-settings--full-rebuild) |
| SAC connects but text scrolls nonstop (no login prompt; not "Press Enter") | § [SAC-Win-ContinuousText](./playbook-I-identity-console-deep.md#sac-win-continuoustext--sac-continuously-written-text-bcd-ems-not-configured-online--offline-fix) |
| `Connected to the serial port of the VM. If no login prompt is displayed, press ENTER.` + pressing Enter does nothing | § [SAC-Win-NoLoginPrompt](./playbook-I-identity-console-deep.md#sac-win-nologinprompt--if-no-login-prompt-is-displayed-press-enter-ems-not-active-in-guest) |
| `Launching of Command Prompt channels is disabled` (SAC connects but `cmd` channel blocked) | § [SAC-Win-CmdDisabled](./playbook-I-identity-console-deep.md#sac-win-cmddisabled--launching-of-command-prompt-channels-is-disabled-sacdrv-reg-key) |
| `Unable to launch a Command Prompt. The service responsible for launching Command Prompt channels has not yet registered.` (SACSVR hung/crashed/disabled) | § [SAC-Win-SacsvrBroken](./playbook-I-identity-console-deep.md#sac-win-sacsvrbroken--unable-to-launch-command-prompt-channel-sacsvr-hungcrasheddisabled-11-error-codes) |

#### Step 4d — Linux + how-to

| Symptom | Anchor |
|---|---|
| `Another connection is currently in progress to this VM` (Linux SAC) | § [SAC-Linux-AnotherConn](./playbook-I-identity-console-deep.md#sac-linux-anotherconn--another-connection-in-progress-linux--no-sighup-enforcement-tmout-mitigation) |
| `Web socket is closed or could not be opened` (customer proxy / firewall blocks WSS upgrade) | § [SAC-Browser-WebSocket](./playbook-I-identity-console-deep.md#sac-browser-websocket--web-socket-is-closed-or-could-not-be-opened-customer-proxyfirewall-blocks-wss) (2-KQL `ConnectorContainerActivity`) |
| SAC connects but stays on black screen after the banner | § [SAC-Browser-BlackScreen](./playbook-I-identity-console-deep.md#sac-browser-blackscreen--terminal-banner-followed-by-black-screen-browser-mitigation-trace) |
| Need to verify SAC RBAC prerequisites + look up principalOid from KQL | § [SAC-HowTo-CheckRBAC](./playbook-I-identity-console-deep.md#sac-howto-checkrbac--check-rbac-role-assignment-prereqs--principaloid-lookup) |
| Need F8 / Advanced Boot Menu access via SAC (Windows) | § [SAC-HowTo-AdvBootMenu](./playbook-I-identity-console-deep.md#sac-howto-advbootmenu--advanced-boot-menu-via-sac-bcdedit-displaybootmenu--bootems) |
| SAC CMD channel management (open / switch / close / lock / timeout config) | § [SAC-HowTo-ChannelMgmt](./playbook-I-identity-console-deep.md#sac-howto-channelmgmt--sac-cmd-channel-management-open-switch-close-lock-timeout-config) |
| Need to collect browser HAR traces for SAC / RDP / SSH failures BEFORE telemetry surfaces | § [SAC-HowTo-CollectBrowserTraces](./playbook-I-identity-console-deep.md#sac-howto-collectbrowsertraces--collect-edgechrome-har-traces-for-sac-rdpssh-failures-before-telemetry) |
| Pull error log per SAC connection attempt by SessionID (with `Code 4XXX` reason mapping) | § [SAC-HowTo-SessionId](./playbook-I-identity-console-deep.md#sac-howto-sessionid--gather-error-log-per-connection-attempt-sessionid-lookup--reason-mapping-2-kql) (2 KQL) |
| Get unified E2E timeline across browser + ACS + host telemetry (by portalSessionId) | § [SAC-HowTo-E2EView](./playbook-I-identity-console-deep.md#sac-howto-e2eview--get-unified-e2e-view-of-serial-console-request-portalsessionid-3-kql) (3 KQL) |
| Map a SAC connection to its target host node (3 methods: SerialConsoleHostMessages, SerialConsoleUsage, Jarvis fallback) | § [SAC-HowTo-HostNode](./playbook-I-identity-console-deep.md#sac-howto-hostnode--determine-target-host-node-serialterminalid--serialconsolehostmessages--serialconsoleusage-jarvis-fallback) |
| Check SAC host package version (agent version counts by Datacenter / Cluster) | § [SAC-HowTo-HostVersion](./playbook-I-identity-console-deep.md#sac-howto-hostversion--determine-host-package-version-agent-version-counts-by-datacentercluster) |

### Step 5 — Pull foundation evidence

| Data | Cluster.Database.Table | When |
|---|---|---|
| Wireserver heartbeat per node | `azcore.Fa.WireserverHeartbeatEtwTable` | IMDS unreachable (RC 3 — host-side) |
| HostAnalyzer report (BD logs) | ASC → Resource Explorer → VM → Diagnostics | IMDS + per-VM call trace correlation |
| SAC connection failures by principal | `armprodgbl.ARMProd.HttpIncoming/Outgoing` | SAC 403 (RBAC) — extract principalOid |
| SAC pod-side errors | `azlinux.SerialConsole.PortalActivity` | SAC 403 / 400 — server-side error detail |
| Storage account HNS flag | `azcore.Xstore.XStoreAccountProperties` | SAC 400 RC 4 — ADLS Gen2 incompatibility |
| Azure Policy enforcing system MI | `armprodgbl.ARMProd.General.PolicyServiceDebug` (PG-restricted) | MSI auto-re-enable |
| GuestProxyAgent connection log | `C:\WindowsAzure\ProxyAgent\Logs\ProxyAgent.Connection.log` (Win) / `/var/log/azure-proxy-agent/ProxyAgent.Connection.log` (Linux) | IMDS app denied by MSP |

### Step 6 — Apply anchor logic

Each deep-file anchor provides: scope, error signatures, log paths (in-guest), KQL bodies, customer-facing mitigation steps, escalation paths.

### Step 7 — Cross-RP / specialized investigation

| Need | Tool |
|---|---|
| ARM API trace through MSI / SAC operations | `armprodgbl.eastus.ARMProd.HttpIncomingRequests` + `HttpOutgoingRequests` |
| Find Azure Policy that's auto-re-enabling system MI | `armprodgbl.eastus.ARMProd.General.PolicyServiceDebug` (PG-restricted — SDE escalation needed) |
| Storage account HNS / V2 properties | `azcore.Xstore.XStoreAccountProperties` (`IsHnsEnabled` flag) |
| Boot Diagnostics blob (kernel log + screenshot) | ASC → VM → Boot Diagnostics tab (always works even when SAC bi-dir is broken on v5) |
| GuestProxyAgent VM instance view substatuses | ARM REST: `GET /subscriptions/.../virtualMachines/<vm>/instanceView?api-version=2024-07-01` → `extensions[name=AzureGuestProxyAgentExtension].substatuses` |

### Step 8 — Mitigation + handoffs

| Scenario | Owner |
|---|---|
| `rdnamedpipecapture` stuck on host after VM restart | **AzureHost-VmService 3-4 on-calls** (restart `rdnpc` on host). PG approval needed for `sc stop/start rdnamedpipecapture` via `Invoke-IAgentInvokeCommand`. |
| Azure v5 / Ice Lake SAC incompatibility | **No active mitigation other than resize** to non-v5 series (e.g., Dv4). Long-term fix promised early CY2022. |
| SACSVR crash/hang requiring dump analysis | **GES → Windows EE Premier** (Premier) OR **Windows EE Pro** (Pro). Override generic Windows routing. |
| Azure Policy auto-re-enabling system MI | **Customer-side**: review + disable the Built-in `Add system-assigned managed identity to enable Guest Configuration assignments...` policy assignment. SDE needed for `PolicyServiceDebug` KQL. |
| MSP (GuestProxyAgent / InVmAccessControlProfile) denying app | **AzureRT / Extensions team** — InVmAccessControlProfile owners |
| ADLS Gen2 SA used for Boot Diagnostics | **Customer-side**: switch BD to a separate SA without HNS. ADLS PG status: no fix yet. |
| Storage Account firewall blocking SerialConsole IPs | **Customer-side**: add SerialConsole service tag IPs as exceptions (PS helper from § SAC-Connect-403, or manual). |
| ESU install fails with IMDS HRESULTs | **TA submits ICM** template `6q3N3P` after route + 2022-Feb 2B+ SSU verified. |
| BCD store missing critical sections (EMS Settings) | **Offline rescue VM + bcdboot rebuild** (Gen1/Gen2 specific). For non-boot fix first → `/SME-Topics/Cant-RDP-SSH/Non-Boot`. |

## Cross-references

| Other playbook / reference | Why |
|---|---|
| Playbook H § SSE-MSINotFound | CMK Storage Account MSI deleted (different from MSI-System-403 which is VM-MI auth) |
| Playbook H § AGEX-Ext-AzurePolicy | Azure Policy blocking extension install (different from MSI-CannotDelete-Policy which targets MI specifically) |
| Playbook H § AGEX-GA-FirewallWireServer-Win | Windows Firewall blocking `168.63.129.16` — IMDS depends on WireServer, so symptoms overlap |
| Playbook D § PM-11 / WF-3 | IMDS Scheduled Events API (different from generic IMDS reachability — PM-11 is about whether SE were emitted, not whether the endpoint is reachable) |
| Playbook E § VMSS-HowTo-TerminateNotif-1 | VMSS Terminate Notifications via in-guest IMDS |
| Playbook A — Unexpected Restart | If SAC reveals BSOD/kernel panic on the VM, the restart RCA lives in A |
| `/SME-Topics/Cant-RDP-SSH/Non-Boot` | When SAC fails because VM cannot boot at all — fix non-boot first |
| `references/azcore-queries.md` § Wireserver / GuestAgent | WireserverHeartbeatEtwTable foundation queries |
| `references/networking-queries.md` | VFP / SLB / NRP queries for advanced networking diagnosis |
| `vm-log-analyzer` skill | Guest log analysis (waagent.log, ProxyAgent.Connection.log, Bitlocker.log, journal) |
