# Playbook I — Identity & Console (IMDS + MSI + SAC) — Deep

> **Companion to** [`playbook-I-identity-console-core.md`](./playbook-I-identity-console-core.md). Full bodies for the 3 merged sub-areas:
>
> - **IMDS** (Instance Metadata Service) — `169.254.169.254` reachability, routing, error codes, GuestProxyAgent / MSP
> - **MSI** (Managed Service Identity) — token acquisition + Azure Policy auto-re-enable
> - **SAC** (Serial Access Console) — boot diag prereqs, RBAC, EMS/BCD config, host-side rdnpc, service health

## Cluster shortcuts

| Short | Full |
|---|---|
| `azcore.Fa` | `cluster('azcore.centralus.kusto.windows.net').database('Fa')` |
| `azcore.Xstore` | `cluster('azcore.centralus.kusto.windows.net').database('Xstore')` |
| `azcore.SharedWorkspace` | `cluster('azcore.centralus.kusto.windows.net').database('SharedWorkspace')` |
| `azcrp.crp_allprod` | `cluster('azcrp.kusto.windows.net').database('crp_allprod')` (a.k.a. `Azcsupfollower2.centralus.kusto.windows.net/crp_allprod`) |
| `armprodgbl.ARMProd` | `cluster('armprodgbl.eastus.kusto.windows.net').database('ARMProd')` |
| `armprodgbl.ARMProdEG.General` | `armprodgbl` macro-expand → `X.database('General').PolicyServiceDebug` |
| `azlinux.SerialConsole` | `cluster('AzLinux').database('SerialConsole')` (also referred to as `azlinux.kusto.windows.net/serialconsole`) |
| `azlinux.AzureLinux` | `cluster('AzLinux').database('AzureLinux')` |
| `azmsicl.azmsidb` | `cluster('azmsicl.kusto.windows.net').database('azmsidb')` (requires `MSI-Telemetry` group in CoreIdentity — see MSI-Basic-Workflow access steps) |

## Anchor Index

### IMDS — reachability + 169.254.169.254
- [`IMDS-Reach-CannotReach`](#imds-reach-cannotreach--cannot-reach-server-umbrella-proxy--firewall--wireserver--routing) — Cannot Reach Server umbrella (Proxy / Firewall / Wireserver / Routing)
- [`IMDS-Reach-MultiNic`](#imds-reach-multinic--bad-routing-multiple-nics--imds-primary-nic-only-rule) — Bad Routing Multiple NICs + Primary-NIC-only rule
- [`IMDS-Reach-Win2012-ESU`](#imds-reach-win2012-esu--esu-installation-fails-due-to-imds-unreachable-2008r2--2012r2) — Win Server 2008R2/2012R2 ESU install failure (4 HRESULTs)

### IMDS — errors + telemetry
- [`IMDS-Token-ErrorCodes`](#imds-token-errorcodes--imds-http-error-code-table--in-guest-test-script) — IMDS HTTP error code table + in-guest test scripts (PS + curl)
- [`IMDS-Token-4xx`](#imds-token-4xx--4xx-error-deep-dive-400--404--405--410--429) — 4xx error deep dive (400 / 404 / 405 / 410 / 429) with example scenarios
- [`IMDS-Token-5xx`](#imds-token-5xx--5xx-error-deep-dive-imdsapirequests-kql--icm-component-routing-table) — 5xx error deep dive (`ImdsApiRequests` KQL + ICM component routing table)
- [`IMDS-Token-KnownIssues`](#imds-token-knownissues--imds-hard-facts-rate-limit--containers--host-side) — IMDS hard facts: 5 QPS, no container, host-side, no SLA
- [`IMDS-GuestProxyAgent`](#imds-guestproxyagent--vm-applications-access-to-wireserveroimds-fails-msp--invmaccesscontrolprofile) — VM apps WireServer/IMDS access fails (MSP / InVmAccessControlProfile / 5-step triage)
- [`IMDS-GPA-Extension-Telemetry`](#imds-gpa-extension-telemetry--guest-proxy-agent-vm-extension-status--connection-summary-via-azcore-fa-kql) — GuestProxyAgent VM Extension telemetry (4 KQL: extension events, CRP PUT/PATCH, GPA start status, proxied connection summary)

### IMDS — utilities + foundation
- [`IMDS-Util-NetTrace`](#imds-util-nettrace--collect-network-traces-windows-netshetl2pcapng-wireshark-linux-tcpdump) — Collect network traces (Windows netsh+etl2pcapng / Wireshark; Linux tcpdump)
- [`IMDS-Util-HostKQL`](#imds-util-hostkql--host-side-imds-kql-functions-imdserrors--imdsapirequests--imdsheartbeats) — Host-side IMDS KQL functions (`ImdsErrors` / `ImdsApiRequests` / `ImdsHeartbeats` in `azcore.SharedWorkspace`)
- [`IMDS-Util-WireServerLogs`](#imds-util-wireserverlogs--troubleshoot-imds-via-host-wireserver-logs-wiremarshal--rest-log-grep-patterns) — Troubleshoot IMDS via host WireServer logs (WireMarshal + REST log grep patterns)

### MSI
- [`MSI-System-403`](#msi-system-403--system-assigned-mi-403-forbidden-on-az-login-identity) — System-Assigned MI 403 Forbidden on `az login --identity` (4 root causes)
- [`MSI-CannotDelete-Policy`](#msi-cannotdelete-policy--cannot-delete-system-assigned-mi-azure-policy-auto-re-enables) — Cannot Delete System-Assigned MI (Azure Policy auto-re-enables)
- [`MSI-AccessInternalError-TenantMove`](#msi-accessinternalerror-tenantmove--managedserviceidentityaccessinternalerror-after-tenant-move-azmsicl-trace) — `ManagedServiceIdentityAccessInternalError` after subscription tenant move (3-KQL azmsicl + crp trace)
- [`MSI-Util-AzMsiCl`](#msi-util-azmsicl--msi-rp-telemetry-azmsiclazmsidb-operationevent--customtraceevent--httpoutgoing-3-kql) — MSI RP telemetry (`azmsicl.azmsidb` OperationEvent + CustomTraceEvent + ARMProd HttpOutgoing 3-KQL pattern)
- [`MSI-PerfInsights-Removal`](#msi-perfinsights-removal--perfinsights-install-removes-user-assigned-mi-from-vm-identity-block-bug) — PerfInsights install removes user-assigned MI from VM identity block (bug)

### SAC — connect-time errors (400 / 403 / 404 / 429)
- [`SAC-Connect-400`](#sac-connect-400--sac-400-bad-request-umbrella-5-causes-bd-disabled--deallocated--sa-deleted--adls-gen2--uri-mismatch) — SAC 400 Bad Request umbrella (5 causes)
- [`SAC-Connect-403`](#sac-connect-403--sac-403-forbidden-rbac-missing-vm-contributor-or-sa-firewall-blocking) — SAC 403 Forbidden (RBAC missing VM Contributor OR SA firewall blocking)
- [`SAC-Connect-404`](#sac-connect-404--sac-404-not-found-boot-diagnostics-disabled) — SAC 404 Not Found (Boot Diagnostics disabled)
- [`SAC-Connect-429`](#sac-connect-429--sac-429-err_bad_request-sa-firewall-blocks-serialconsole-service-tag-ips) — SAC 429 ERR_BAD_REQUEST (SA firewall blocks SerialConsole service tag IPs)

### SAC — host + guest issues
- [`SAC-Host-RdnpcStuck`](#sac-host-rdnpcstuck--serial-console-not-working-after-vm-restart-rdnamedpipecapture-stuck) — Serial Console not working after VM Restart (rdnamedpipecapture stuck)
- [`SAC-Guest-ServiceTimeout`](#sac-guest-servicetimeout--sac-service-did-not-respond-linux-ems-config--azure-v5-ice-lake-incompatibility) — SAC Service did not respond (Linux EMS config + Azure v5 Ice Lake incompatibility)

### SAC — Windows BCD / EMS / SACSVR
- [`SAC-Win-BCDMissingEMS`](#sac-win-bcdmissingems--system-cannot-find-file-bcd-store-missing-ems-settings--full-rebuild) — System Cannot Find File (BCD store missing EMS Settings, full BCD rebuild)
- [`SAC-Win-ContinuousText`](#sac-win-continuoustext--sac-continuously-written-text-bcd-ems-not-configured-online--offline-fix) — SAC Continuously Written Text (BCD EMS not configured; online + offline fix)
- [`SAC-Win-NoLoginPrompt`](#sac-win-nologinprompt--if-no-login-prompt-is-displayed-press-enter-ems-not-active-in-guest) — "If no login prompt is displayed, press Enter" (EMS not active in guest)
- [`SAC-Win-CmdDisabled`](#sac-win-cmddisabled--launching-of-command-prompt-channels-is-disabled-sacdrv-reg-key) — Launching of Command Prompt channels is disabled (SacDrv DisableCmdSessions reg key)
- [`SAC-Win-SacsvrBroken`](#sac-win-sacsvrbroken--unable-to-launch-command-prompt-channel-sacsvr-hungcrasheddisabled-11-error-codes) — Unable to launch Command Prompt channel (SACSVR hung/crashed/disabled, 11 error codes)

### SAC — Linux + how-to
- [`SAC-Linux-AnotherConn`](#sac-linux-anotherconn--another-connection-in-progress-linux--no-sighup-enforcement-tmout-mitigation) — Another connection in progress LINUX — no SIGHUP enforcement, TMOUT mitigation
- [`SAC-Connect-409`](#sac-connect-409--sac-409-err_bad_request-read-only-lock-blocks-post-action) — SAC 409 ERR_BAD_REQUEST (Read-Only lock blocks SAC POST action)
- [`SAC-Connect-ServiceUnavailable`](#sac-connect-serviceunavailable--cloud-shell-is-not-available-acs-lsi-or-region-issue) — "Cloud Shell is not available" (ACS LSI or region issue)
- [`SAC-Browser-WebSocket`](#sac-browser-websocket--web-socket-is-closed-or-could-not-be-opened-customer-proxyfirewall-blocks-wss) — "Web Socket is closed or could not be opened" (customer proxy/firewall blocks WSS)
- [`SAC-Browser-BlackScreen`](#sac-browser-blackscreen--terminal-banner-followed-by-black-screen-browser-mitigation-trace) — "Terminal Banner Followed by Black Screen" (browser mitigation; collect HAR trace)
- [`SAC-HowTo-CheckRBAC`](#sac-howto-checkrbac--check-rbac-role-assignment-prereqs--principaloid-lookup) — Check RBAC Role Assignment (prereqs + principalOid lookup)
- [`SAC-HowTo-AdvBootMenu`](#sac-howto-advbootmenu--advanced-boot-menu-via-sac-bcdedit-displaybootmenu--bootems) — Advanced Boot Menu via SAC (bcdedit displaybootmenu + bootems)
- [`SAC-HowTo-ChannelMgmt`](#sac-howto-channelmgmt--sac-cmd-channel-management-open-switch-close-lock-timeout-config) — SAC CMD Channel Management (open / switch / close / lock / timeout config)
- [`SAC-HowTo-CollectBrowserTraces`](#sac-howto-collectbrowsertraces--collect-edgechrome-har-traces-for-sac-rdpssh-failures-before-telemetry) — Collect Edge/Chrome HAR traces (for SAC + RDP/SSH failures before telemetry)
- [`SAC-HowTo-SessionId`](#sac-howto-sessionid--gather-error-log-per-connection-attempt-sessionid-lookup--reason-mapping-2-kql) — Gather Error Log per Connection Attempt (sessionId lookup + reason mapping, 2 KQL)
- [`SAC-HowTo-E2EView`](#sac-howto-e2eview--get-unified-e2e-view-of-serial-console-request-portalsessionid-3-kql) — Get Unified E2E View of Serial Console Request (portalSessionId, 3 KQL)
- [`SAC-HowTo-HostNode`](#sac-howto-hostnode--determine-target-host-node-serialterminalid--serialconsolehostmessages--serialconsoleusage-jarvis-fallback) — Determine Target Host Node (serialTerminalId → SerialConsoleHostMessages + SerialConsoleUsage, Jarvis fallback)
- [`SAC-HowTo-HostVersion`](#sac-howto-hostversion--determine-host-package-version-agent-version-counts-by-datacentercluster) — Determine Host Package Version (agent version counts by Datacenter/Cluster)

---

## IMDS-Reach-CannotReach — Cannot Reach Server umbrella (Proxy / Firewall / Wireserver / Routing)

**Scope**: `curl -H Metadata:true http://169.254.169.254/...` times out or returns wrong response. 4 root causes — eliminate in order.

### 1. Proxy intercepting traffic
- Wireshark shows request going to IP **other than** `169.254.169.254`
- IMDS does not work through proxies — public restriction: https://learn.microsoft.com/en-us/azure/virtual-machines/instance-metadata-service?tabs=linux#proxies
- **Mitigation**: whitelist `169.254.169.254` in proxy OR temporarily remove proxy for testing

### 2. Firewall / Antivirus blocking
- netsh / Wireshark trace shows NO packets reaching IMDS interface
- **Mitigation**: ask customer about AV / FW. Whitelist BOTH:
  - `168.63.129.16` (Wireserver — IMDS dependency)
  - `169.254.169.254` (IMDS)

### 3. Wireserver connectivity (host side)
GA in Failed state → suspect Wireserver. Check heartbeat on the host node:

```kusto
let startDate = datetime({StartTime});
let endDate = datetime({EndTime});
let theNodeId = "{NodeId}";
cluster('azcore.centralus.kusto.windows.net').database('Fa').WireserverHeartbeatEtwTable
| where PreciseTimeStamp between (startDate..endDate)
| where NodeId == theNodeId
| project PreciseTimeStamp, Status
| make-series kind=nonempty sum(Status) default=0 on PreciseTimeStamp from startDate to endDate step 1m
| render timechart
```

If Wireserver alive: pull HostAnalyzer (ASC → Resource Explorer → VM → Diagnostics → run Host Analyzer report for the relevant time window). Grep `..\Logs\Logs\WireServerLogs` for the VM's ContainerId:
```
[INFO] ProcessGetMetaDataRequest server = 127.0.0.1, port = 8889,
       path = /metadata/instance?api-version=...,
       containerId = 909febb7-2f8b-4e95-8638-bdcd2955d769
[INFO] ProcessGetMetaDataRequest imdsUrl = /metadata/instance?api-version=...&cid=<>
[INFO] ProcessGetMetaDataRequest httpStatus code = 200 totalBytesRead = 1033
```
If no record with the VM's ContainerId → networking issue, not Wireserver.

### 4. Network limitations (NICs / IPs / routes)
See [`IMDS-Reach-MultiNic`](#imds-reach-multinic--bad-routing-multiple-nics--imds-primary-nic-only-rule).

### Client-side red flags
- Specialized OS disk
- Migrated from on-prem
- Custom image with software/registries changed
- Never worked
- Many VMs affected on DIFFERENT Azure nodes

---

## IMDS-Reach-MultiNic — Bad Routing Multiple NICs + Primary-NIC-only rule

**Symptoms**:
- 169.254.169.254 unreachable via HTTP
- NO firewall / AV blocking
- VM has multiple NICs OR multiple private IPs
- Custom image (esp. on-prem origin)
- OS uses static IPs (not DHCP)

**Root cause**: IMDS responds **ONLY to requests from Primary NIC + Primary IP**. IMDS has no auth — it relies on primary-NIC isolation to verify caller identity.

### Investigation

Find primary NIC + IP via Cloud Shell:
```powershell
$ResourceGroup = '<rg>'
$VmName = '<vm>'
$NicNames = az vm nic list --resource-group $ResourceGroup --vm-name $VmName | ConvertFrom-Json | ForEach-Object { $_.id.Split('/')[-1] }
foreach ($NicName in $NicNames) {
    $Nic = az vm nic show --resource-group $ResourceGroup --vm-name $VmName --nic $NicName | ConvertFrom-Json
    Write-Host $NicName, $Nic.primary, $Nic.macAddress
}
```

Capture netsh trace + convert to PCAP:
```cmd
netsh trace start capture=yes tracefile=c:\temp\%computername%_nettrace.etl
netsh trace stop
REM Convert ETL → PCAP per Networking wiki "How-to-Convert-ETL-capture-to-PCAPNG-Files"
```
Look for HTTP requests to IMDS going through a **non-Primary** IP.

Check OS routing:
```cmd
route print
```
Match interface index against MAC of Primary NIC noted above.

### Mitigation (Windows)
```cmd
route delete 169.254.169.254 -p
route ADD 169.254.169.254 MASK 255.255.255.255 <PrimaryGatewayIP> METRIC 2 IF <PrimaryNicIfIndex> -p
route ADD 168.63.129.16   MASK 255.255.255.255 <PrimaryGatewayIP> METRIC 2 IF <PrimaryNicIfIndex> -p
```
- Gateway IP from `ipconfig`
- Interface index from top of `route print`
- `-p` = persistent across reboots

### Notes
- Static IP ↔ DHCP transitions WILL change routes
- For custom images, **fix the golden image**, don't patch each VM
- Precedent ICM: 387242978

---

## IMDS-Reach-Win2012-ESU — ESU Installation fails due to IMDS unreachable (2008R2 / 2012R2)

**Scope**: Azure provides FREE ESU for Win Server 2008 / 2008R2 / 2012 / 2012R2 + SQL 2012 — installer requires IMDS access. If IMDS unreachable, ESU AI installer fails with one of 4 HRESULTs.

### VM type matrix
| Type | ARM-deployed | Auto-ESU | TSG path |
|---|---|---|---|
| ARM VM | Yes | Yes | This TSG (Mitigation 1 + 2) |
| Classic VM | No | No | Manual key install (rare; retiring) |
| VMware / Stack HCI / Stack Hub / Nutanix on Azure | No | No | Contact Azure Stack team or 3rd-party support |

### Symptom signatures in setupreport / CBS log

| HRESULT | Signature |
|---|---|
| `ERROR_INSTALL_TRANSFORM_FAILURE (1624)` | `ESU: wrong response HRESULT_FROM_WIN32(1624)` |
| `ERROR_NO_SIGNATURE (951)` | `Network Retry Counts : 30 ... check failed HRESULT_FROM_WIN32(951)` |
| `CRYPT_E_NOT_FOUND` | `The chain does not seem valid ... check failed CRYPT_E_NOT_FOUND` |
| `E_FAIL` | `Network Retry Counts : 30 ... check failed E_FAIL` |

All 4 share signature `ESU: Is IMDS check needed:TRUE → ESU: Checking IMDS → ...`.

### Root cause 1 — IMDS unreachable (route / multi-NIC / proxy)

**Mitigation 1**: Check 2022-Feb 2B+ SSU is installed (fix was to make ESU AI bypass proxy when calling IMDS — no longer uses `WINHTTP_ACCESS_TYPE_DEFAULT_PROXY`). Reference KBs:
- Win Server 2008 SP2: `KB5010452` (Feb 8, 2022)
- Win Server 2008 R2 SP1 / Win7 SP1: `KB5010451` (Feb 8, 2022)

Related ICM: 271109300.

Then validate network connectivity:
```cmd
telnet 169.254.169.254 80
telnet 168.63.129.16 80
route print
ipconfig /all
```
Confirm interface = Primary NIC + Primary IP (full procedure: [`IMDS-Reach-MultiNic`](#imds-reach-multinic--bad-routing-multiple-nics--imds-primary-nic-only-rule)).

Add route if missing:
```cmd
route add 169.254.169.254/32 <PrimaryGatewayIP> metric 1 -p
```

### Root cause 2 — missing trusted root/intermediate certificates

**Mitigation 2**: install the 4 ESU prereq updates per https://learn.microsoft.com/en-us/windows-server/get-started/extended-security-updates-deploy.

No ESU MAK product key needed in Azure — Azure provides ESU free via IMDS.

### Escalation
TA submits ICM: `https://portal.microsofticm.com/imp/v3/incidents/create?tmpl=6q3N3P`

---

## IMDS-Token-ErrorCodes — IMDS HTTP error code table + in-guest test script

### HTTP error code table

| Code | Reason |
|---|---|
| 200 OK | Server responded correctly |
| 400 Bad Request | Missing `Metadata: true` header |
| 404 Not Found | Requested element doesn't exist |
| 405 Method Not Allowed | Only GET and POST supported |
| 429 Too Many Requests | API max **5 queries/second** |
| 500 Service Error | Retry; **Host-side problem** |

Ref: https://learn.microsoft.com/en-us/azure/virtual-machines/windows/instance-metadata-service?tabs=linux#errors-and-debugging

### In-guest PowerShell test (forces no-proxy, retry 5x)
```powershell
$Proxy = New-Object System.Net.WebProxy
$WebSession = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$WebSession.Proxy = $Proxy
for ($i = 1; $i -le 5; $i++) {
  try {
    $response = Invoke-WebRequest -Headers @{"Metadata"="true"} -Method GET `
        -Uri "http://169.254.169.254/metadata/instance?api-version=2021-02-01" -WebSession $WebSession
    $StatusCode = $response.StatusCode
  } catch {
    $StatusCode = $_.Exception.Response.StatusCode
    $errorMessage = $_.ErrorDetails.Message
  }
  Write-Output "Attempt $i: Status Code - $StatusCode"
  if ($errorMessage) { Write-Output "Error message: $errorMessage" }
}
```

### Linux equivalent
```bash
curl -H "Metadata: true" -s --noproxy '*' \
  "http://169.254.169.254/metadata/instance?api-version=2021-02-01"
```

---

## IMDS-Token-KnownIssues — IMDS hard facts (rate limit / containers / host-side)

Memorize:
- **5 queries / second** hard rate limit → exceed = 429
- **500 Error = HOST problem** (file ICM)
- **Port 80 blocked** → `curl: (7) Failed to connect to 169.254.169.254 port 80: Connection timed out`
- **Does NOT work in containers** (any kind — Docker / K8s / etc)
- Service runs on the **Host**, not the VM
- **No external SLA**

Ref: https://learn.microsoft.com/en-us/azure/virtual-machines/windows/instance-metadata-service?tabs=linux#frequently-asked-questions

---

## IMDS-GuestProxyAgent — VM Applications Access to WireServer/IMDS Fails (MSP / InVmAccessControlProfile)

**Scope**: New Metadata Security Protocol (MSP / `GuestProxyAgent`) blocks app traffic to WireServer (`168.63.129.16`) or IMDS (`169.254.169.254`) if the app is NOT in the InVmAccessControlProfile whitelist.

### 5-step triage

#### 1. Check GuestProxyAgent service running
Delegate to: `/SME-Topics/Metadata-Security-Protocol/TSGs/Guest-Proxy-Agent-VM-Extension.md`
- If service stuck/failing: restart the service
- If key-latch issue: reset latched key

#### 2. Verify GuestProxyAgent has correct profile via VM instance view
GET `/subscriptions/.../virtualMachines/<vm>/instanceView?api-version=2024-07-01`

Look for extension `AzureGuestProxyAgentExtension` → substatuses → `ComponentStatus/ProxyAgentStatus/succeeded` → message contains:
- `imdsRuleId` → e.g. `/.../InVmAccessControlProfiles/WindowsIMDS/Versions/1.3.0`
- `wireServerRuleId` → e.g. `/.../InVmAccessControlProfiles/WindowsWireServer/Versions/1.2.0`
- `secureChannelState` → e.g. `WireServer Enforce - IMDS Audit`

#### 3. Check app is whitelisted in current InVmAccessControlProfile
Review the profile content; ensure the calling app's process name + identity is in the privilege/identity list.

#### 4. Examine GuestProxyAgent connection log for exact deny reason

| OS | Log path |
|---|---|
| Windows | `C:\WindowsAzure\ProxyAgent\Logs\ProxyAgent.Connection.log` |
| Linux | `/var/log/azure-proxy-agent/ProxyAgent.Connection.log` |

Deny pattern signature:
```
[INFO] Connection:16763 - Start to match privilege 'MSIToken'
[INFO] Connection:16763 - Matched privilege path '/metadata/identity/auth2/token'
[INFO] Connection:16763 - Not matched process name 'SecurityScanMgr.exe' from identity 'SecurityScanMgr'
... (many more "Not matched" lines for each identity in the profile)
[INFO] Connection:16763 - Privilege matched once, but no identity matches.
[WARN] Connection:16763 - Denied unauthorize request: {... "processName":"powershell_ise.exe" ...}
[INFO] {... "responseStatus":"403 Forbidden Request" ...}
```
The log explicitly tells you which `processName` / `processFullPath` was denied and which identity rules it tried to match.

#### 5. Escalation owner
**AzureRT / Extensions** team.

---

## IMDS-Util-NetTrace — Collect Network Traces (Windows netsh+etl2pcapng, Wireshark; Linux tcpdump)

### Windows — netsh + etl2pcapng (preferred)

Start trace:
```cmd
mkdir c:\IMDS_TRACE
netsh trace start scenario=netconnection capture=yes report=yes persistent=yes ^
  tracefile=c:\IMDS_TRACE\%computername%.etl maxSize=500MB
ipconfig /flushdns
```

Reproduce (PS v6+):
```powershell
Invoke-RestMethod -Headers @{"Metadata"="true"} -Method GET -NoProxy `
  -Uri "http://169.254.169.254/metadata/instance?api-version=2021-02-01" | ConvertTo-Json -Depth 64
```

Stop + convert ETL → PCAPNG:
```cmd
netsh trace stop
REM Download https://github.com/microsoft/etl2pcapng → C:\IMDS_TRACE
Etl2pcapng.exe %computername%.etl %computername%.pcapng
```

### Windows — Wireshark (if netsh fails)
Install Wireshark → start capture → reproduce → stop. Filter: `ip.dst == 168.63.129.16`.

### Linux — tcpdump
```bash
sudo su -
tcpdump -i 1 -s 0 -w /tmp/IMDS.pcap &
curl -s -H Metadata:true --noproxy "*" "http://169.254.169.254/metadata/instance?api-version=2021-02-01" | jq
kill -9 <pid>
tcpdump -r /tmp/IMDS.pcap | grep -B2 -i /metadata/instance | less
```

---

## MSI-System-403 — System-Assigned MI 403 Forbidden on `az login --identity`

### Symptom
```
az login --identity
  → Failed to connect to MSI. Please make sure MSI is configured correctly.
  Get Token request returned http error: 403, reason: Forbidden
```

### 4 root causes — run all 4 checks

#### RC 1: Managed Identity NOT enabled
Portal → VM → Identity → verify System-Assigned status == **On**.

#### RC 2: Incorrect role assignment
MI lacks the role required for the target operation (Reader / Contributor / workload-specific like `Storage Blob Data Reader`). Add role assignment.

#### RC 3: Network restriction blocking IMDS endpoint
VM cannot reach `http://169.254.169.254/metadata/identity`. Apply [`IMDS-Reach-CannotReach`](#imds-reach-cannotreach--cannot-reach-server-umbrella-proxy--firewall--wireserver--routing) + [`IMDS-Reach-MultiNic`](#imds-reach-multinic--bad-routing-multiple-nics--imds-primary-nic-only-rule).

#### RC 4: Proxy intercepting `az login --identity`
Find URLs being called:
```bash
az login --identity --debug
```
Whitelist each URL in the proxy, or remove proxy for testing.

### MSI support boundaries
See `/SME-Topics/Managed-Service-Identity-(MSI)/Workflows/Basic-Workflow_MSI` § Support Boundaries.

---

## MSI-CannotDelete-Policy — Cannot Delete System-Assigned MI (Azure Policy auto-re-enables)

### Symptom
Customer tries to disable system-assigned MI via Portal / PS / az CLI. Operation appears to succeed but the MI **reappears** after minutes. This blocks user-assigned-MI usage (system-assigned is default when present).

### Root cause 1 — Azure Policy auto-re-enables system MI

Built-in policies that DO this:
- `Add system-assigned managed identity to enable Guest Configuration assignments on virtual machines with no identities`
- `Add system-assigned managed identity to enable Guest Configuration assignments on VMs with a user-assigned identity`

Full catalog: https://docs.microsoft.com/en-us/azure/governance/policy/samples/built-in-policies

#### Find the offending policy via correlationId
Customer turns off MI → waits 5 min → grabs `correlationId` from Activity Log.

```kusto
cluster('armprodgbl.eastus.kusto.windows.net').database('ARMProd')
| macro-expand isfuzzy=true ARMProdEG as X (
    X.database('General').PolicyServiceDebug
    | where TIMESTAMP > ago(24h)
    | where SubscriptionId == "{SubscriptionId}"
    | where CorrelationId == "{CorrelationId}"
    | project OperationName, Message
)
```
**NOTE**: `PolicyServiceDebug` table is **PG-restricted** (SDE access only). Alternative: extract policy info from Activity Log JSON.

Then Portal → search "Policy" → Assignments → search by Assignment ID → see the policy.

#### If customer cannot disable policy + still wants user-assigned MI via IMDS
Add `mi_res_id` query param:
```
GET 'http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/&mi_res_id=/subscriptions/.../resourceGroups/.../providers/Microsoft.ManagedIdentity/userAssignedIdentities/<UAMI>'
Header: Metadata: true
```
Ref: https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/how-to-use-vm-token#get-a-token-using-http

### Root cause 2 — Portal-side bug
Follow Portal TSG: `/SME-Topics/Portal-Home`.

---

## SAC-Connect-400 — SAC 400 Bad Request umbrella (5 causes: BD disabled / deallocated / SA deleted / ADLS Gen2 / URI mismatch)

5 distinct symptom wordings → 5 root causes:

| # | Error wording | Root cause | Mitigation |
|---|---|---|---|
| 1 | `Boot diagnostics settings for '<VM>' is disabled` | BD was enabled once, now disabled | Portal → enable BD; SA must NOT have firewall on |
| 2 | `The VM power state is deallocated. Azure Serial Console will not function when the VM is deallocated` | VM Stopped-Deallocated (Stopped = OK; Stopped-Deallocated = no SAC) | Start the VM |
| 3 | `The storage account '<SA>' used for boot diagnostics on this VM could not be found` | BD-linked SA was deleted | Edit BD config → point to existing SA |
| 4 | `Invalid boot diagnostics storage account ... Verify that boot diagnostics is enabled for this VM and that its kind is one of: 'BlobStorage', 'BlockBlobStorage', 'FileStorage', or 'Storage'` (SAC immediately shows `SAC>` prompt then fails) | BD SA is V2 with **ADLS Gen2 / Hierarchical Namespaces** enabled — incompatible with blob storage APIs | Switch BD to a separate SA without HNS enabled |
| 5 | Bare `(400) - BadRequest` | BD storage URI value mismatch — `http://` vs `https://` mismatch with SA endpoints | Reset BD URI via `az vm boot-diagnostics enable --storage https://...` |

### Mitigation 4 — detect ADLS Gen2 / HNS

#### Portal way
ASC → Resource Explorer → storage account → Configuration → check **Data Lake Storage Gen2 Hierarchical Namespace Enabled**.

#### `az serial-console connect` symptom
Fails with cryptic traceback: `ValueError: No value for given attribute` in `get_storage_account_info`.

#### Kusto check
```kusto
let local_StorageAccountName = "{StorageAccountName}";
let globalFrom = datetime("{StartTime}");
let globalTo   = datetime("{EndTime}");
cluster("azcore.centralus.kusto.windows.net").database("Xstore").XStoreAccountProperties
| where TIMESTAMP between(globalFrom .. globalTo)
| where Account startswith strcat(local_StorageAccountName, ";")
| project IsHnsEnabled
```
`IsHnsEnabled = 1` → HNS on → incompatible. `0` → fine.

### Mitigation 5 — fix URI scheme mismatch
The BD URI is NOT visible in Portal — check via ASC → VM Properties tab. Common cause: ARM template / az CLI enabled BD without `https://`.

```bash
az vm boot-diagnostics enable \
  --name <vm> --resource-group <rg> \
  --storage https://<sa>.blob.core.windows.net/
```
(VM reboot may be required for changes to take effect.)

### ADLS team status
ADLS team is aware (since Q3CY19). Blob/Gen2 interop story pending — workaround is the only path today.

---

## SAC-Connect-403 — SAC 403 Forbidden (RBAC missing VM Contributor OR SA firewall blocking)

### Two symptoms — same code, different causes

#### Symptom 1 — RBAC denied
```
The serial console connection to the VM encountered an error: 'Forbidden (403) - Forbidden
```
User lacks **Virtual Machine Contributor** role on the target VM.

#### Symptom 2 — Storage account firewall blocking
```
A 'Forbidden' response was encountered when accessing this VM's boot diagnostic storage account '<SA>'.
This is often caused when the storage account firewall is enabled.
```
(Also seen as 429 from SAC — see [`SAC-Connect-429`](#sac-connect-429--sac-429-err_bad_request-sa-firewall-blocks-serialconsole-service-tag-ips).)

### Investigation — find principal of failed access

```kusto
let starttime = datetime("{StartTime}");
let endtime   = datetime("{EndTime}");
let SubID    = "{SubId}";
let HTTPIncoming = cluster("armprodgbl.eastus.kusto.windows.net").database("ARMProd")
    | macro-expand isfuzzy=true ARMProdEG as X (
        X.database('Requests').HttpIncomingRequests
        | where subscriptionId == SubID
        | where PreciseTimeStamp between (starttime ..endtime)
        | extend resourceName = extract('\\/providers\\/[\\w-\\.]+\\/[\\w-\\.]+\\/([\\w-\\.]+)(\\/|\\?)', 1, targetUri)
        | where httpStatusCode <> -1 and httpStatusCode != 200
        | where authorizationAction contains "SerialConsole"
    );
let HTTPOutgoing = cluster("armprodgbl.eastus.kusto.windows.net").database("ARMProd")
    | macro-expand isfuzzy=true ARMProdEG as X (
        X.database('Requests').HttpOutgoingRequests
        | where subscriptionId == SubID
        | where PreciseTimeStamp between (starttime ..endtime)
        | extend resourceName = extract('\\/providers\\/[\\w-\\.]+\\/[\\w-\\.]+\\/([\\w-\\.]+)(\\/|\\?)', 1, targetUri)
        | where httpStatusCode <> -1 and httpStatusCode != 200
    );
union HTTPIncoming, HTTPOutgoing
| project PreciseTimeStamp, resourceName, authorizationAction, operationName, httpMethod,
          httpStatusCode, TaskName, principalOid, principalPuid, targetUri, subscriptionId, tenantId,
          correlationId, clientIpAddress, errorCode, errorMessage, commandName, authorizationSource
```

### Investigation — SAC pod side
```kusto
cluster("AzLinux").database("SerialConsole").PortalActivity
| where TIMESTAMP > ago(7d)
| where subscriptionId =~ "{SubId}"
| where vmName contains "{VMName}"
| where metadata contains "err"
| project activitytimestamp, message, metadata, sessionId, subscriptionId, vmName, connectorPodName
```

### Mitigation 1 — RBAC fix
Portal → VM → Access Control (IAM) → Role Assignments → grant user **Virtual Machine Contributor** role.

### Mitigation 2 — SA firewall: add SerialConsole service tag IPs as exceptions
Helper PS function `Add-SerialConsoleIPsToStorageAccountFirewall` (from wiki) uses `Get-AzNetworkServiceTag` → filter `SerialConsole` service tag → strip `/32` → expand `/31` → `Add-AzStorageAccountNetworkRule`.

**Caveat per CSS Custom Code policy**: share with disclaimer; customer should review + understand before running.

Manual alternative: get SerialConsole service tag IP list per VM region from https://learn.microsoft.com/en-us/troubleshoot/azure/virtual-machines/serial-console-linux#use-serial-console-with-custom-boot-diagnostics-storage-account-firewall-enabled → add to SA firewall.

---

## SAC-Connect-404 — SAC 404 Not Found (Boot Diagnostics disabled)

### Symptom
```
The serial console connection to the VM encountered an error: 'Not Found'
(404) - Unable to retrieve boot diagnostics settings for '<VM NAME>'.
To use serial console, ensure that boot diagnostics is enabled for this VM.
```

### Root cause
VM was created with **Boot Diagnostics DISABLED**.

### Mitigation
1. Portal → VM → Boot Diagnostics → Settings → **Enable**
2. When picking the storage account, **ensure the SA does NOT have Storage Firewall enabled** (or add SerialConsole IPs — see [`SAC-Connect-403`](#sac-connect-403--sac-403-forbidden-rbac-missing-vm-contributor-or-sa-firewall-blocking))
3. Retry SAC

---

## SAC-Connect-429 — SAC 429 ERR_BAD_REQUEST (SA firewall blocks SerialConsole service tag IPs)

### Symptom
```
Preparing console connection to <VMName>
The serial console connection to the VM encountered an error: 'ERR_BAD_REQUEST'
(429) - Request failed with status code 429
```
Also surfaces as 403 with: `A 'Forbidden' response was encountered when accessing this VM's boot diagnostic storage account ...`

### Root cause
Boot Diagnostics SA has **Azure Storage Firewalls** enabled → IP allowlist excludes the SerialConsole service IPs.

### Investigation
```kusto
let starttime = datetime({StartTime});
let endtime   = datetime({EndTime});
let SubID = "{SubscriptionId}";
cluster('armprodgbl.eastus.kusto.windows.net').database('ARMProd')
| macro-expand isfuzzy=true ARMProdEG as X (
    X.database('Requests').HttpIncomingRequests
    | where subscriptionId == SubID
    | where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
    | extend resourceName = extract('\\/providers\\/[\\w-\\.]+\\/[\\w-\\.]+\\/([\\w-\\.]+)(\\/|\\?)', 1, targetUri)
    | where httpStatusCode <> -1 and httpStatusCode != 200
    | where authorizationAction contains "SerialConsole"
    | where operationName contains "SERIALCONSOLE"
    | where resourceName contains "{VMName}"
    | where httpStatusCode == "429"
| project PreciseTimeStamp, resourceName, authorizationAction, operationName, httpMethod,
          httpStatusCode, TaskName, principalOid, principalPuid, targetUri, subscriptionId,
          tenantId, correlationId, clientIpAddress, errorCode, errorMessage, commandName, authorizationSource)
```

### Mitigation
1. ASC → Resource Explorer → storage account holding bootdiagnostics folder
2. Azure Storage Firewall and Virtual Networks → verify default action == **Deny** and Virtual Network Rule has an allow segment (= firewall enabled)
3. Add SerialConsole service tag IPs as exceptions (PS function from [`SAC-Connect-403`](#sac-connect-403--sac-403-forbidden-rbac-missing-vm-contributor-or-sa-firewall-blocking) OR manual per https://learn.microsoft.com/en-us/troubleshoot/azure/virtual-machines/serial-console-linux#use-serial-console-with-custom-boot-diagnostics-storage-account-firewall-enabled)
4. Retry SAC

---

## SAC-Host-RdnpcStuck — Serial Console not working after VM Restart (rdnamedpipecapture stuck)

### Symptom
After customer stops/starts VM, SAC connection fails:
```
Sorry, the serial console was unable to connect to the VM because the service did not respond in a timely manner.
Please retry your connection.
```
Often affects MANY VMs on the same node. **Host-side issue.**

### Self-mitigation (toggle BD)
1. Portal → VM → Support + troubleshooting → Boot diagnostics → Settings
2. Set Status = **Disable** → Save → wait for "successfully disabled" (~1 min)
3. Set Status back to previous (likely "Enable with custom storage account") → pick previous SA → Save
4. Retry SAC

**OR**: redeploy the VM.

### Backend mitigation (if self-mitigation fails)
Engage **AzureHost-VmService 3-4 on-calls** to restart `rdnpc` on the host. Or with **PG approval**:
```powershell
$n | Invoke-IAgentInvokeCommand "sc stop rdnamedpipecapture"
$n | Invoke-IAgentInvokeCommand "sc start rdnamedpipecapture"
```

### RCA template (use when customer asks for explanation)
The rdnpc service got stuck on the host after the stop/start; restarting the service mitigates it. Known platform bug. Tracking: ICM 230541633, bug 9466707. No ETA on permanent fix.

---

## SAC-Guest-ServiceTimeout — SAC Service did not respond (Linux EMS config + Azure v5 Ice Lake incompatibility)

### Symptom
```
Sorry, the serial console was unable to connect to the VM because the service did not respond in a timely manner.
```

### 2 root causes

#### Root cause 1 — Guest OS not configured for single-user mode OR local firewall
Applies to: **NON-v5 VM sizes**.

##### Mitigation 1
Verify Linux distro is endorsed: https://docs.microsoft.com/en-us/azure/virtual-machines/linux/endorsed-distros AND has SAC support per https://docs.microsoft.com/en-us/azure/virtual-machines/troubleshooting/serial-console-linux#serial-console-linux-distribution-availability. If custom/unendorsed image: engage image vendor to fix grub/EMS config.

##### Mitigation 2
Ask customer to check guest firewall (iptables/firewalld/nftables) — may be blocking SAC's port.

#### Root cause 2 — Azure v5 series + 3rd-gen Intel Xeon Platinum 8370C (Ice Lake) incompatibility
Affects: **Dv5/Dsv5, Ddv5/Ddsv5, Ev5/Esv5, Edv5/Edsv5, Ebsv5/Ebdsv5 preview**.

Bi-directional SAC broken; **serial logs + screenshots in boot diagnostics still work**.

##### Mitigation 3
**Resize VM to a non-affected series** (e.g., Dv4) → SAC works. Long-term fix promised for early CY2022 deployment.

### Cross-references
- For host-side rdnpc stuck after restart → [`SAC-Host-RdnpcStuck`](#sac-host-rdnpcstuck--serial-console-not-working-after-vm-restart-rdnamedpipecapture-stuck)
- For Win BCD missing EMS settings → [`SAC-Win-BCDMissingEMS`](#sac-win-bcdmissingems--system-cannot-find-file-bcd-store-missing-ems-settings--full-rebuild)

---

## SAC-Win-BCDMissingEMS — "System Cannot Find File" (BCD store missing EMS Settings, full rebuild)

### Symptom chain
1. SAC connects but ends up on:
   - [`SAC-Win-NoLoginPrompt`](#sac-win-nologinprompt--if-no-login-prompt-is-displayed-press-enter-ems-not-active-in-guest) ("Press Enter") OR
   - [`SAC-Win-ContinuousText`](#sac-win-continuoustext--sac-continuously-written-text-bcd-ems-not-configured-online--offline-fix)

   Either indicates **EMS NOT enabled** in Guest BCD.

2. Customer tries to enable EMS → gets:
   ```
   An error occurred while attempting to access the boot configuration data.
   The system cannot find the file specified.
   ```

### Root cause
BCD store has CRITICAL sections missing — specifically the **EMS Settings** section (where port + baud are configured).

### Investigation
```cmd
REM Online (if VM boots): logged into VM via RDP or SAC
bcdedit /enum all

REM Offline (broken VM): attach OS disk to rescue VM
bcdedit /store <FULL PATH TO BCD FILE> /enum all
```
Expected output should include: Windows Boot Manager + Windows Boot Loader + **EMS Settings**. If EMS Settings missing → confirmed.

### Mitigation (OFFLINE ONLY — must use rescue VM)
Cannot create individual BCD sections; must rebuild entire store via `bcdboot`. **Backup `\boot` folder first.**

#### Generation 1 (BIOS) VM
```cmd
bcdboot <WINDOWS_DRIVE>:\windows /s <BCD_DRIVE>: /v /f BIOS

REM Re-add boot manager flags (not added by default)
bcdedit /store <BCD_DRIVE>:\boot\bcd /set {<BootLoaderID>} integrityservices enable
bcdedit /store <BCD_DRIVE>:\boot\bcd /set {<BootLoaderID>} recoveryenabled Off
bcdedit /store <BCD_DRIVE>:\boot\bcd /set {<BootLoaderID>} bootstatuspolicy IgnoreAllFailures

REM Re-enable EMS for SAC
bcdedit /store <BCD_DRIVE>:\boot\bcd /set {bootmgr} displaybootmenu yes
bcdedit /store <BCD_DRIVE>:\boot\bcd /set {bootmgr} timeout 5
bcdedit /store <BCD_DRIVE>:\boot\bcd /set {bootmgr} bootems yes
bcdedit /store <BCD_DRIVE>:\boot\bcd /ems {current} on
bcdedit /store <BCD_DRIVE>:\boot\bcd /emssettings EMSPORT:1 EMSBAUDRATE:115200
```

#### Generation 2 (UEFI) VM
Same as Gen 1 but:
```cmd
bcdboot <WINDOWS_DRIVE>:\windows /s <EFI_PARTITION_VOLUME>: /v /f UEFI
```
Then the same `bcdedit /store ... /set ...` block as Gen 1.

Reattach disk to source VM → boot.

### If VM cannot boot AT ALL
Fix non-boot first — see `/SME-Topics/Cant-RDP-SSH` (Non-Boot bucket) before attempting BCD rebuild.

---

## SAC-Win-ContinuousText — SAC Continuously Written Text (BCD EMS not configured; online + offline fix)

### Symptom
After SAC connects, a bunch of text gets written nonstop. (Different from [`SAC-Win-NoLoginPrompt`](#sac-win-nologinprompt--if-no-login-prompt-is-displayed-press-enter-ems-not-active-in-guest) where nothing happens.)

### Root cause
Serial Console NOT enabled at Guest OS level — Windows BCD missing EMS configuration.

### Online mitigation (VM bootable) — push BCD edits 4 ways

#### Option 1: CSE inline script
```cmd
cmd
bcdedit /set {bootmgr} displaybootmenu yes
bcdedit /set {bootmgr} timeout 5
bcdedit /set {bootmgr} bootems yes
bcdedit /ems {current} on
bcdedit /emssettings EMSPORT:1 EMSBAUDRATE:115200
shutdown /r /t 0 /f
```

#### Option 2: Remote PowerShell (PSSession + Invoke-Command) — same commands

#### Option 3: Azure PowerShell one-liner
```powershell
Set-AzureRmVMExtension -ResourceGroupName $rg -VMName $vm -Location $loc `
  -Name EnableSAC -Publisher Microsoft.Compute `
  -ExtensionType CustomScriptExtension -TypeHandlerVersion 1.9 `
  -SettingString '{"commandToExecute":"cmd.exe /c bcdedit /set {bootmgr} displaybootmenu yes && bcdedit /set {bootmgr} timeout 5 && bcdedit /set {bootmgr} bootems yes && bcdedit /ems {current} on && bcdedit /emssettings EMSPORT:1 EMSBAUDRATE:115200 && shutdown /r /t 0 /f"}'
```
Check Substatuses StdOut/StdErr for success/failure.

#### Option 4: RDP direct — same `bcdedit` commands locally

### Offline mitigation (VM cannot boot) — `az vm repair` + repair script
```bash
az account set --subscription "<SubId>"
az extension add -n vm-repair
az extension update -n vm-repair

rg="<rg>"; vm="<vm>"
az vm repair create --verbose -g $rg -n $vm
# Use Public IP for quick access. Provide admin user+pwd when prompted.

# Apply the SAC enable fix (script lives in repair-script-library):
az vm repair run -g $rg -n $vm --verbose --run-on-repair --run-id win-sacdump-on

# Swap disks back + clean up:
az vm repair restore -g $rg -n $vm --verbose
```

### Offline mitigation — manual BCD edit on rescue VM
```cmd
REM Attach OS disk to rescue VM, set ONLINE in Disk Management
REM Find drive letter containing \windows folder
bcdedit /store <DRIVE>:\boot\bcd /enum   REM find boot loader identifier (path \Windows\system32\winload.exe)

bcdedit /store <DRIVE>:\boot\bcd /set {bootmgr} displaybootmenu yes
bcdedit /store <DRIVE>:\boot\bcd /set {bootmgr} timeout 5
bcdedit /store <DRIVE>:\boot\bcd /set {bootmgr} bootems yes
bcdedit /store <DRIVE>:\boot\bcd /ems {<BootLoaderID>} ON
bcdedit /store <DRIVE>:\boot\bcd /emssettings EMSPORT:1 EMSBAUDRATE:115200
```

If disk encrypted: unlock first via ADE recovery TSG (see Playbook H § ADE-Recovery-Unlock).

---

## SAC-Win-NoLoginPrompt — "If no login prompt is displayed, press Enter" (EMS not active in guest)

### Symptom
```
Connected to the serial port of the VM.
If no login prompt is displayed, press ENTER.
```
Pressing Enter → nothing happens.

### Root cause
Azure platform connected to VM successfully, but Guest OS not connecting to EMS. 4 sub-causes:
1. Serial Console not enabled on Guest (Windows: BCD EMS missing — see [`SAC-Win-ContinuousText`](#sac-win-continuoustext--sac-continuously-written-text-bcd-ems-not-configured-online--offline-fix))
2. Boot Diagnostics not enabled (see [`SAC-Connect-404`](#sac-connect-404--sac-404-not-found-boot-diagnostics-disabled))
3. Windows custom VM / hardened appliance / boot config blocking serial port
4. OS unhealthy / kernel didn't start (Windows or Linux)

### Mitigation
Enable SAC in Guest:
- **Windows**: per Basic-Workflow_SAC § On Windows VMs (same BCD commands as [`SAC-Win-ContinuousText`](#sac-win-continuoustext--sac-continuously-written-text-bcd-ems-not-configured-online--offline-fix))
- **Linux**: per Basic-Workflow_SAC § On Linux VMs (typically `console=ttyS0` grub kernel arg + agetty on ttyS0)

If VM not booting at all → fix non-boot first (see `/SME-Topics/Cant-RDP-SSH/Non-Boot`).

---

## SAC-Win-CmdDisabled — "Launching of Command Prompt channels is disabled" (SacDrv DisableCmdSessions reg key)

### Symptom
SAC connects but CMD channel fails:
```
Launching of Command Prompt channels is disabled
```

### Root cause
EMS configured to disable CMD channels (registry key `HKLM\SYSTEM\CurrentControlSet\Services\SacDrv\DisableCmdSessions` set).

### Mitigation ONLINE (VM boots)
```cmd
reg delete "HKLM\SYSTEM\CurrentControlSet\Services\SacDrv" /v DisableCmdSessions
```
Then restart VM.

### Mitigation OFFLINE (3 paths)

#### Path 1: Recovery Script (preferred)
1. Phase 1: mount broken OS disk on rescue VM
2. ```cmd
   reg load HKLM\BROKENSYSTEM f:\windows\system32\config\SYSTEM
   reg delete "HKLM\BROKENSYSTEM\CurrentControlSet\Services\SacDrv" /v DisableCmdSessions
   reg unload HKLM\BROKENSYSTEM
   ```
3. Phase 2: reassemble original VM with fixed disk

#### Path 2: OSDisk Swap API
Stop + deallocate → (decrypt if encrypted) → snapshot broken OS disk → attach to rescue → same `reg load/delete/unload` → detach → OSDisk swap API to reattach to original VM.

#### Path 3: Recreate ARM VM
Export VM config JSON → clone OS disk backup via Storage Explorer → delete VM → attach disk to rescue → same `reg load/delete/unload` → detach → recreate VM from JSON.

---

## SAC-Win-SacsvrBroken — "Unable to launch Command Prompt channel" (SACSVR hung/crashed/disabled, 11 error codes)

### Symptom
```
Error: Unable to launch a Command Prompt. The service responsible for launching Command Prompt channels has not yet registered.
This may be because the service is not yet started, is disabled by the administrator, is malfunctioning or is unresponsive.
```

### Root cause
`Special Administration Console Helper` service (`sacsvr`) is broken: disabled, hung, or crashing.

### Pre-check
If VM has perf degradation → switch case to **Slow VM / Performance workflow** (not SAC). Run host analyzer first.

### Triage
```cmd
sc query sacsvr
```

| Status | Branch |
|---|---|
| Starting/Stopping | service crashing/hanging (procdump + GES) |
| Stopped | `sc start sacsvr` then check failure code below |

### Failure code routing (after `sc start sacsvr`)

| Code | Meaning | Branch |
|---|---|---|
| 5 | `ACCESS_DENIED` | Procmon trace for `Result is ACCESS DENIED` → fix ACL on registry/files |
| 1053 | `SERVICE_REQUEST_TIMEOUT` | crashing/hanging |
| 1058 | `SERVICE_DISABLED` | enable in SCM (StartType=Auto) |
| 1059 | `CIRCULAR_DEPENDENCY` | fix service dependency chain |
| 1067 | `PROCESS_ABORTED` | crashing/hanging |
| 1068 | `SERVICE_DEPENDENCY_FAIL` | fix dependency |
| 1069 | `SERVICE_LOGON_FAILED` | fix logon account credentials |
| 1070 | `SERVICE_START_HANG` | crashing/hanging |
| 1077 | `SERVICE_NEVER_STARTED` | enable in SCM |
| 1079 | `DIFFERENT_SERVICE_ACCOUNT` | match startup account to shared container |
| 1753 | dependency | fix dependency |

### Crashing / hanging procedure (procdump + GES)
1. Download Procmon/Procdump to rescue VM → detach → attach utility disk to broken VM
2. `procdump.exe -s 5 -n 3 -ma sacsvr` → 3 dumps 5 sec apart
3. Upload dumps to DTM workspace
4. Engage GES: Product `Windows Svr 20XX Datacenter` → Support topic `Routing Windows V3\System Performance\An application or process hangs or crashes` → override to **Windows EE Premier** (Premier) OR **Windows EE Pro** (Pro)

### ACCESS_DENIED procedure (procmon)
1. Procmon trace: `procmon /Quiet /Minimized /BackingFile c:\temp\ProcMonTrace.PML`
2. Reproduce: `sc start SACSVR`
3. Stop: `procmon /Terminate`
4. Filter PML by `Result is ACCESS DENIED` → fix the registry/file ACL using a healthy machine as reference

---

## SAC-Linux-AnotherConn — "Another connection in progress LINUX" — no SIGHUP enforcement, TMOUT mitigation

### Symptom
```
Another connection is currently in progress to this VM. Please wait and retry the request.
The serial console connection was closed. To reconnect, press "Enter".
```

### Root cause 1 (most common)
If user A is connected to SAC and user B successfully connects to the same VM, A is disconnected, B is connected to A's session. **But disconnect doesn't log A out** — no SIGHUP enforcement (still on roadmap).

#### Mitigation 1 (preferred)
Reboot VM, then retry SAC.

#### Mitigation 1 (Linux session timeout)
Add to `/etc/profile` or `/etc/bash_profile`:
```bash
export TMOUT=600   # auto-logout after 10 min idle
```

#### Mitigation 1 (access control)
Limit who has VM Contributor on the VM AND on the BD storage account (both required for SAC).

### Root cause 2 — Incompatible Distro (FreeBSD, non-Marketplace)

#### Mitigation 2
FreeBSD audit config: https://docs.freebsd.org/en/books/handbook/audit/#audit-config. Per [Linux + OSS support](https://learn.microsoft.com/en-us/troubleshoot/azure/cloud-services/support-linux-open-source-technology), FreeBSD is best-effort only.

---

## SAC-HowTo-CheckRBAC — Check RBAC Role Assignment (prereqs + principalOid lookup)

### Prerequisites for SAC access
1. Boot Diagnostics enabled on VM
2. Local password user inside VM (use VMAccess `Reset password` if needed)
3. Azure account has **Virtual Machine Contributor** role on BOTH the VM AND the BD storage account
4. ARM deployment (Classic NOT supported)
5. SA must allow `Allow storage account key access` (else SAC fails)

### Find principalOid of failed SAC access
Same KQL as [`SAC-Connect-403`](#sac-connect-403--sac-403-forbidden-rbac-missing-vm-contributor-or-sa-firewall-blocking) § Investigation. Extract `principalOid` from output.

### ASC → verify role assignment
1. ASC → Resource Explorer → select subscription → Access Control → Check Access
2. Input `principalOid` from KQL → returns role definition ID
3. Look up role definition → verify it has SAC-required permissions

---

## SAC-HowTo-AdvBootMenu — Advanced Boot Menu via SAC (bcdedit displaybootmenu + bootems)

### Why
Access Windows advanced boot menu without nested virtualization. Enables F8-style boot option selection through SAC.

### Configure BCD (admin CMD on Win VM)
```cmd
bcdedit /set {bootmgr} displaybootmenu yes
bcdedit /set {bootmgr} timeout 20
bcdedit /set {bootmgr} bootems yes
```

Meanings:
- `displaybootmenu yes` → show boot menu at boot
- `timeout 20` → menu visible 20 sec before default option chosen
- `bootems yes` → enable EMS boot (required for SAC interaction at boot)

Reboot VM. Connect SAC during boot → press F8 → advanced boot menu appears.

---

## IMDS-Token-4xx — 4xx error deep dive (400 / 404 / 405 / 410 / 429)

Companion to [`IMDS-Token-ErrorCodes`](#imds-token-errorcodes--imds-http-error-code-table--in-guest-test-script). Most 4xx errors mean the **request** is wrong, not the server.

| Code | Cause | Mitigation |
|---|---|---|
| **400 Bad Request** | Missing `Metadata: true` header OR missing `format=json` param when querying a leaf node | Add the missing header/param |
| **404 Not Found** | URL path doesn't match any IMDS endpoint | Compare against [IMDS endpoint catalog](https://learn.microsoft.com/en-us/azure/virtual-machines/instance-metadata-service?tabs=linux#endpoint-categories) |
| **405 Method Not Allowed** | Used a method other than GET (POST allowed only on Scheduled Events) | Change to GET |
| **410 Gone** | Endpoint was valid earlier; resource no longer exists (similar to 500) | **Retry for up to 70 sec**, then redeploy VM. If still failing → go to [`IMDS-Token-5xx`](#imds-token-5xx--5xx-error-deep-dive-imdsapirequests-kql--icm-component-routing-table) |
| **429 Too Many Requests** | Hit 5 QPS rate limit | Add delay between requests; review [IMDS rate limits](https://learn.microsoft.com/en-us/azure/virtual-machines/instance-metadata-service?tabs=linux#rate-limiting) |

Best-practice retry guidance: https://learn.microsoft.com/en-us/azure/architecture/best-practices/transient-faults

---

## IMDS-Token-5xx — 5xx error deep dive (`ImdsApiRequests` KQL + ICM component routing table)

**Scope**: 5xx from IMDS = server-side / dependency component problem (CRP / NRP / DRP / AAD). Customer should already have retry mechanisms.

### Investigation — find failing API requests on the host
```kusto
let startDate = datetime({StartTime});
let endDate = datetime({EndTime});
let theContainerId = "{ContainerId}";
let theNodeId = "{NodeId}";
cluster("azcore.centralus").database("SharedWorkspace").ImdsApiRequests(startDate, endDate, theNodeId, theContainerId)
//| where Url == "/metadata/reprovisiondata"
| order by TIMESTAMP asc
| take 10
```
Identify which `/metadata/...` URL is returning 5xx → routes to the right dependency component below.

### Escalation — IcM component routing by query endpoint

| Component | Query endpoint | IcM team | Contact |
|---|---|---|---|
| Instance Metadata Service (IMDS) | `/metadata/instance` | `OneFleet Node\AzureInstanceMetadataService` | minnielahoti@microsoft.com |
| Attestation | `/metadata/attested` | `InstanceMetadataService` | minnielahoti@microsoft.com |
| Network | `/metadata/instance/network` | `CloudNet\Network Manager` | cnnmdev@microsoft.com |
| Scheduled events | `/metadata/scheduledevents` | `OneDeploy\Policy Engine` | azpolicyenginehot@microsoft.com |
| Identity | `/metadata/identity` | `Managed Service Identity\Triage` | msieng@microsoft.com |
| WireServer | * | `OneFleet Node\AzureHost-Agent-Sev-3-4` | azhostagent@microsoft.com |

ICM template: `https://portal.microsofticm.com/imp/v3/incidents/create?tmpl=6q3N3P`
PG backlog: https://msazure.visualstudio.com/One/_backlogs/backlog/Azure-Compute-MetadataServer/Backlog%20items

---

## IMDS-GPA-Extension-Telemetry — Guest Proxy Agent VM Extension status + connection summary via azcore.Fa KQL

**Companion to** [`IMDS-GuestProxyAgent`](#imds-guestproxyagent--vm-applications-access-to-wireserveroimds-fails-msp--invmaccesscontrolprofile). Use these KQL when GPA extension misbehaves or to verify GPA modules are healthy.

### 1) Extension events per VM (provisioning state)
```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').GuestAgentExtensionEvents
| where VMId == "{VmUniqueId}"
| where Name == "Microsoft.CPlat.ProxyAgent.ProxyAgentWindows"   // or ProxyAgentLinux
```
Look at most recent `OperationSuccess` / `Message`. Cross-link CRP-side error code via the GPA Extension TSG `Common Error Codes` table (EXIT_CODE_HANDLERENV_ERR=1, STATUS_CODE_NOT_OK=4, EXIT_CODE_SERVICE_START_ERR=7, EXIT_CODE_NOT_SUPPORTED_OS_VERSION=10, etc.).

### 2) CRP PUT / PATCH for GPA extension
```kusto
cluster('azcrp.kusto.windows.net').database('crp_allprod').ApiQosEvent_nonGet
| where operationName in ("VirtualMachines.ResourceOperation.PUT", "VirtualMachineScaleSets.ResourceOperation.PUT",
                          "VirtualMachines.ResourceOperation.PATCH", "VirtualMachineScaleSets.ResourceOperation.PATCH")
| where subscriptionId == "{SubscriptionId}"
| where resourceName contains "{VMName}"
```

### 3) GPA critical module start status (proxy_listener / key_keeper / redirector)
```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').GuestAgentGenericLogs
| where PreciseTimeStamp >= ago(7d)
| where ExecutionMode == "ProxyAgent"
| where SubscriptionId == "{SubscriptionId}" and ResourceGroupName == "{ResourceGroupName}"
    and RoleInstanceName contains "{VMName}"
| extend PreciseTimeStamp = todatetime(Context2), ProxyAgentVersion = GAVersion,
         message = Context1, module_name = Context3, task = TaskName
| where message has "elapsed" and message has "message"
| project PreciseTimeStamp, ProxyAgentVersion, module_name, task, message
```
Expected modules (all should show `start` with elapsed ms + "Started ..." message): `proxy_listener` (port 3080), `key_keeper` (poll_secure_channel_status), `redirector` (eBPF maps).

### 4) Proxied connection summary (allow/deny statistics)
```kusto
cluster('azcore.centralus.kusto.windows.net').database('Fa').GuestAgentGenericLogs
| where PreciseTimeStamp >= ago(1d)
| where ExecutionMode == "ProxyAgent"
| where SubscriptionId == "{SubscriptionId}" and ResourceGroupName == "{ResourceGroupName}"
    and RoleInstanceName contains "{VMName}"
| extend PreciseTimeStamp = todatetime(Context2), ProxyAgentVersion = GAVersion,
         message = Context1, module_name = Context3, task = TaskName
| where task == "log_connection_summary"
| project PreciseTimeStamp, ProxyAgentVersion, module_name, task, message
```

### Common in-VM checks (Windows MSP)
3 services must be RUNNING:
```cmd
sc query eBPFCore
sc query NetEbpfExt
sc query GuestProxyAgent
```

In-VM log paths:
- Status JSON: `C:\WindowsAzure\ProxyAgent\Logs\status.json`
- Detailed log: `C:\WindowsAzure\ProxyAgent\Logs\ProxyAgent.log` (retains 20 old files)
- Connection log: `C:\WindowsAzure\ProxyAgent\Logs\ProxyAgent.Connection.log` (retains 20 old files)

### Common gotcha: Proxy Listener could not be started (port 3080 taken)
Status JSON shows `"Failed to bind TcpListener '127.0.0.1:3080' ... (os error 10048)"`. Fix:
```cmd
netstat -ano | findstr :3080
tasklist /FI "PID eq <PID>"
taskkill /PID <PID>
net stop GuestProxyAgent
net start GuestProxyAgent
```

### Common gotcha: app binds to specific source IP (not loopback)
GPA / WFP cannot redirect requests that bind to a specific local IP (e.g., `10.80.0.7`). Customer must remove `ServicePoint.BindIPEndPointDelegate`-style binding. Security-by-design — GPA refuses to bind to non-loopback to avoid turning local exploits into remote exploits.

---

## IMDS-Util-HostKQL — Host-side IMDS KQL functions (`ImdsErrors` / `ImdsApiRequests` / `ImdsHeartbeats`)

**Scope**: The 3 most-used IMDS host-side KQL functions in `azcore.SharedWorkspace`. All take `(startDate, endDate, theNodeId [, theContainerId])`.

Access docs: https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/496459/Kusto-Endpoints_Tool

### `ImdsErrors()` — get IMDS-specific errors (e.g., IMDS failing to retrieve from CRP)
```kusto
let startDate = datetime({StartTime});
let endDate = datetime({EndTime});
let theNodeId = "{NodeId}";
cluster("azcore.centralus").database("SharedWorkspace").ImdsErrors(startDate, endDate, theNodeId)
| order by TIMESTAMP asc
| take 10
```

### `ImdsApiRequests()` — pull per-request response details
```kusto
let startDate = datetime({StartTime});
let endDate = datetime({EndTime});
let theContainerId = "{ContainerId}";
let theNodeId = "{NodeId}";
cluster("azcore.centralus").database("SharedWorkspace").ImdsApiRequests(startDate, endDate, theNodeId, theContainerId)
| where Url == "/metadata/reprovisiondata"   // or any /metadata/... path
| order by TIMESTAMP asc
| take 10
```
Used in [`IMDS-Token-5xx`](#imds-token-5xx--5xx-error-deep-dive-imdsapirequests-kql--icm-component-routing-table) to identify which dependency is failing.

### `ImdsHeartbeats()` — verify IMDS version + uptime on the node
```kusto
let startDate = datetime({StartTime});
let endDate = datetime({EndTime});
let theNodeId = "{NodeId}";
cluster("azcore.centralus").database("SharedWorkspace").ImdsHeartbeats(startDate, endDate, nodeId=theNodeId)
| project TIMESTAMP, Status = 1
| make-series kind=nonempty sum(Status) default=0 on TIMESTAMP from startDate to endDate step 1h
| render timechart
```

More queries: https://eng.ms/docs/cloud-ai-platform/azure-core/azure-compute/general-purpose-host-arunki/azure-instance-metadata-service/compute-azlinux-metadataserver/troubleshooting/kusto-queries

---

## IMDS-Util-WireServerLogs — Troubleshoot IMDS via host WireServer logs (WireMarshal + REST log grep patterns)

**Scope**: When `azcore.SharedWorkspace.ImdsApiRequests` doesn't show the call, the next step is checking raw WireServer logs on the host to see if the call reached the host at all.

### Collect WireServer logs from the host
Use [Collect WireServer Logs (AGEX)](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/494974/Collect-WireServer-Logs_AGEX). Result is a ZIP — unzip → `<node-id-date-time>\Logs\WireServerLogs\`.

### File structure + grep patterns

| File | Search by | What it tells you |
|---|---|---|
| `WireMarshal_<datetime>.log` | `containerId = <ContainerId>` | Health of WireServer process. If call missing → WireServer down on the host. |
| `REST_<datetime>.log` | DIP (PA IP) of the Guest VM (from ASC) | All requests from Guest VMs + associated response code |

### `WireMarshal` log signature (success)
```
[2023/10/03, 22:26:41.957, INFO, 00009312] ProcessGetMetaDataRequest server = 127.0.0.1, port = 8889,
  path = /metadata/instance/network/interface/?format=text&api-version=2017-04-02,
  containerId = xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
[INFO] ProcessGetMetaDataRequest imdsUrl = /metadata/instance/.../format=text&api-version=2017-04-02&cid=<>
[INFO] ProcessGetMetaDataRequest httpStatus code = 200 totalBytesRead = 2
```

### `REST` log signature (success)
```
[2023/10/04, 10:31:56.632, INFO, 00021244] Received request from Client Id = 'XXX.XXX.XX.XX:XXXXX'
  To = 'XX.XXX.XX.X:XXXX', RequestUrl:'/metadata/instance?api-version=2018-02-01'. Request Id = 83928
[INFO] Request type = 'MetadataIMDS'. Request Id = 83928.
[INFO] Request 83928 processing complete. Http response status code = 200
```

Need timestamp + ContainerId from ASC VM page to filter the log lines.

---

## MSI-AccessInternalError-TenantMove — `ManagedServiceIdentityAccessInternalError` after tenant move (azmsicl trace)

### Symptom
VM operation fails with:
```
ManagedServiceIdentityAccessInternalError
Internal error encountered when retrieving managed service identity details for
'https://control-westus2.identity.azure.net/subscriptions/<sub>/resourcegroups/<rg>/providers/Microsoft.Compute/virtualMachines/<vm>/credentials'.
Received non-retriable error: Response StatusCode: 'BadRequest', ReasonPhrase: 'Bad Request'.
```

### Root cause
Subscription was moved between Entra ID tenants. MSI does NOT auto-recreate managed identities on tenant move (change made by MSI team on Sep 11, see [ICM 206212464](https://portal.microsofticm.com/imp/v3/incidents/details/206212464/home)). **Not a CRP issue** — engage **Managed Service Identity / Triage** team, NOT AzureRT.

### Investigation (3-KQL chain — needs azmsicl access)

#### 1) Find the failing CRP request via correlationId
```kusto
cluster('Azcsupfollower2.centralus.kusto.windows.net').database('crp_allprod').ApiQosEvent_nonGet
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where correlationId =~ trim(" ", "{CorrelationId}")
| extend startTime = datetime_add('millisecond', -e2EDurationInMilliseconds, PreciseTimeStamp)
| project startTime, PreciseTimeStamp, e2EDurationInMilliseconds, region, operationId, operationName,
          resourceGroupName, resourceName, httpStatusCode, resultCode, requestEntity, errorDetails
| sort by PreciseTimeStamp asc
```
**Note**: CRP correlationId does NOT match the MSI internal correlationId — use the timestamp + resourceId to narrow down in step 2.

#### 2) Find MSI operation on the same resource (narrow window!)
```kusto
cluster('azmsicl.kusto.windows.net').database('azmsidb').OperationEvent
| where env_time between (datetime({StartTime}) .. datetime({EndTime}))
| where operationName == "CredentialsGetRequest"
| extend correlationId = substring(split(env_cv, "_")[0], 2)
| where resourceId =~ "/subscriptions/{SubscriptionId}/resourcegroups/{RG}/providers/microsoft.compute/virtualmachines/{VM}"
| extend activityId = split(env_cv, "_")[2]
| extend env_cv_custom = strcat(split(env_cv, "_")[0], "_00000000-0000-0000-0000-000000000000_", split(env_cv, "_")[2])
| project env_time, env_seqNum, operationName, resourceId, resourceType, resultType, IdentityType, ObjectId, activityId
| sort by env_time asc, env_seqNum asc
```
Pull `activityId` for step 3.

#### 3) Get detailed trace by MSI internal activityId
```kusto
cluster('azmsicl.kusto.windows.net').database('azmsidb').CustomTraceEvent
| where env_time between (datetime({StartTime}) .. datetime({EndTime}))
| where ActivityId == "{ActivityId}"
| project env_time, env_seqNum, TraceLevel, TagId, Message
| sort by env_time asc, env_seqNum asc
```
Expected signature for tenant-move root cause:
```
Exception occurred ... CredentialsGetRequest ... MsiException: Subscription: <sub> moved from Tenant <TenantID>
on Resource: /subscriptions/<sub>/resourcegroups/<rg>/providers/Microsoft.Compute/virtualMachines/<vm>
```

The CRP `requestEntity` URI's `tid=` query param reveals the **attempted** tenant (not the actual current tenant).

### Mitigation
- **System-assigned MI**: disable → re-enable
- **User-assigned MI**: delete → recreate → reattach to all resources
- Customer doc: https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/known-issues#will-managed-identities-be-recreated-automatically-if-i-move-a-subscription-to-another-directory

### Escalation
**CSS Cloud Identity** owns this. IcM route: `Managed Service Identity / Triage`. **Do NOT route to AzureRT**.

---

## MSI-Util-AzMsiCl — MSI RP telemetry (`azmsicl.azmsidb` 3-KQL pattern)

**Scope**: General-purpose MSI RP telemetry pattern when CRP / ARM shows MSI-related delay or error and you need to dig into the MSI RP side.

### Access prerequisite
Request access to **MSI-Telemetry** group in CoreIdentity:
- Link: https://coreidentity.microsoft.com/manage/entitlement/entitlement/msitelemetry-0aty
- Permission: Read Only
- Then add Kusto Data Source `https://azmsicl.kusto.windows.net:443`, alias `Azmsicl`, expand `Azmsicl > azmsidb > TraceEvent`

### 3-KQL pattern (System or User Assigned MI assign/remove)

#### Step 1 — Summary of assign/remove operations for a resource
```kusto
cluster("azmsicl.kusto.windows.net").database("azmsidb").OperationEvent
| where env_time >= datetime({StartTime}) and env_time <= datetime({EndTime})
| where resourceId contains "{SubscriptionId}" and resourceId contains "{VMName}"
| project env_cv, operationName, resultSignature, resourceId
```
Inspect `resultSignature` column. For a failed request, copy the right-most GUID from `env_cv` — that's the MSI internal **ActivityId**.

#### Step 2 — Detailed trace by ActivityId
```kusto
cluster("azmsicl.kusto.windows.net").database("azmsidb").CustomTraceEvent
| where env_time >= datetime({StartTime}) and env_time <= datetime({EndTime})
| where ActivityId == "{ActivityId}"
| project Message
```

#### Step 3 — ARM → MSI outgoing calls (when ARM has delays / errors talking to MSI)
```kusto
cluster("armprodgbl.eastus.kusto.windows.net").database("ARMProd")
| macro-expand isfuzzy=true ARMProdEG as X (
    X.database('Requests').HttpOutgoingRequests
    | where TIMESTAMP >= datetime({StartTime}) and TIMESTAMP < datetime({EndTime})
    | where targetUri contains "/Microsoft.ManagedIdentity/"
    | where subscriptionId == "{SubscriptionId}"
    | where targetUri contains "{UserIdentityName}"   // for UAMI; remove for system-assigned
    | project TIMESTAMP, operationName, correlationId, httpStatusCode, errorCode, exceptionMessage, targetUri
)
```

### MSI ICM path
Cross-reference: [AAD TSG ICM Path](https://supportability.visualstudio.com/AzureAD/_wiki/wikis/AzureAD/183967/Azure-AD-Managed-Identities-(MSI)?anchor=icm-paths)

---

## MSI-PerfInsights-Removal — PerfInsights install removes user-assigned MI from VM identity block (bug)

### Symptom
Installing **Performance Diagnostics (PerfInsights)** unexpectedly **removes** existing user-assigned managed identities from the VM. PUT operation replaces the identity block without including all previously assigned identities.

### Investigation
1. Azure Activity Log → look for PUT operations modifying the VM identity block around the time of PerfInsights install. Look for user-agent `azure-resource-manager/2.0` + client principal name.
2. Verify the PUT request payload — did it include BOTH system-assigned AND user-assigned identities, or did it overwrite with only one?
3. Was the operation triggered via Portal or CLI?

### Permission requirement
To assign / manage MSIs the installer needs `Microsoft.Authorization/roleAssignments/write`. Built-in roles that grant this:
- User Access Administrator
- Owner
- Role Based Access Control Administrator

### Mitigation
- Always include both system + user identities explicitly in PUT payloads. Reference: https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/how-to-configure-managed-identities?pivots=qs-configure-portal-windows-vm
- Verify permissions before triggering install
- Set up alerts for identity modifications to detect future cases

Ref: https://dev.azure.com/Supportability/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/496105/User-Assigned-Identity-Support-for-Storage_Storage

---

## SAC-Connect-409 — SAC 409 ERR_BAD_REQUEST (Read-Only lock blocks SAC POST action)

### Symptom
```
The serial console connection to the VM encountered an error: 'ERR_BAD_REQUEST'
(409) - Request failed with status 409
```

### Root cause
A **read-only lock** is applied at the resource (VM) level OR the resource group level. SAC access uses a **POST** API operation at CRP level (`VirtualMachines.WriteSerialConsoleConnectionMetadata.POST`), which a ReadOnly lock blocks.

### Required Azure actions for SAC (any of these blocked by ReadOnly lock breaks SAC)

| Azure Action | Purpose |
|---|---|
| `Microsoft.Compute/virtualMachines/start/action` | Starts the VM |
| `Microsoft.Compute/virtualMachines/read` | Get VM properties |
| `Microsoft.Compute/virtualMachines/write` | Create/update VM |
| `Microsoft.Resources/subscriptions/resourceGroups/read` | Get/list RGs |
| `Microsoft.Storage/storageAccounts/listKeys/action` | Get SA access keys |
| `Microsoft.Storage/storageAccounts/read` | Get SA properties |
| `Microsoft.SerialConsole/serialPorts/connect/action` | Connects to serial port |

### Mitigation
1. Portal → VM → Locks → verify if a Read-Only lock is applied (also check resource group level)
2. If found, inform customer the Read-Only lock blocks SAC POST
3. If customer is concerned about deletion: **switch to Delete lock** (prevents delete, allows SAC)
4. Retry SAC

---

## SAC-Connect-ServiceUnavailable — "Cloud Shell is not available" (ACS LSI or region issue)

### Symptom
```
The serial console connection to the VM encountered an error: ''
(ServiceUnavailable) - Cloud Shell is not available at this moment, please retry later.
```

### Root cause
Serial Console uses **Azure Cloud Shell** underneath. If ACS is having issues in the region, SAC is impacted. Usually caused by an **ACS LSI** in the region.

### Mitigation 1 — workaround: use SAC v2 preview (does not depend on ACS)
Share with customer: https://aka.ms/serialconsolev2preview

### Mitigation 2 — confirm via known LSI list
Check for ongoing Azure Cloud Shell LSI in the customer's region:
- 03/19/2019 → ICM 110759662
- 05/28/2019 → ICM 123375128
- 30/10/2021 → ICM 269592792

If you find a new ACS LSI, add it to the wiki.

### Mitigation 3 — telemetry deep dive
If no LSI found, use [`SAC-HowTo-E2EView`](#sac-howto-e2eview--get-unified-e2e-view-of-serial-console-request-portalsessionid-3-kql) to pull the SAC connection timeline. Note: telemetry appears ~2 hours after the connection attempt.

---

## SAC-Browser-WebSocket — "Web Socket is closed or could not be opened" (customer proxy/firewall blocks WSS)

Short URL: https://aka.ms/AAjwypw

### Symptom
SAC fails (via Portal OR `az serial-console connect -g <rg> -n <vm>`):
```
The serial console encountered the following web socket error communication with the VM:
'error: Web socket is closed or could not be opened.'.
Please validate your network connection and retry the attempt.
```

### Root cause
Customer's on-prem firewall/proxy blocks WebSocket (WSS) connections from their workstation → blocks the WSS leg to `wss://<region>.gateway.serialconsole.azure.com/...`.

### Investigation

#### 1) Verify SAC reached the container (look for session_id but missing customer-data-channel)
```kusto
cluster('AzLinux').database('SerialConsole').ConnectorContainerActivity
| where subscriptionId == "{SubscriptionId}"
| where resourceGroup == "{ResourceGroup}"
| where vmName == "{VMName}"
| project TIMESTAMP, message
```
Look for `SESSION_ID::...`, `AZURE_CLOUD::prod`, `RP_REGION::...`, `BUILD_INFO::...`, `VM_LOCATION::...`, `HOST_CONNECTION::wss://...` — these confirm container setup. If `Customer Data Channel Connected` is MISSING, it's a client-side WSS issue.

#### 2) Drill in on the specific sessionId
```kusto
cluster('azlinux').database('SerialConsole').ConnectorContainerActivity
| where sessionId == "{SessionId}"
| project TIMESTAMP, message
```

#### Cross-check with Azure Cloud Shell
Customer also unable to connect via Cloud Shell terminal → confirms client-side WSS block.

### Mitigation
- If SAC works in Portal but not Cloud Shell (or vice versa): use the working path as workaround; check for [ongoing CRI/LSI](https://portal.microsofticm.com/imp/v3/incidents/search/advanced?sl=chngd2ymk5u); if none, report to AzTux/SerialConsole team
- If BOTH fail: customer's firewall/proxy is blocking WSS upgrade. Customer fix:
  1. Take browser HAR traces ([`SAC-HowTo-CollectBrowserTraces`](#sac-howto-collectbrowsertraces--collect-edgechrome-har-traces-for-sac-rdpssh-failures-before-telemetry)) to show what's denied during HTTP→WSS upgrade
  2. Configure proxy/firewall to allow WebSocket upgrade traffic to the SAC gateway URL

---

## SAC-Browser-BlackScreen — "Terminal Banner Followed by Black Screen" (browser mitigation; collect HAR trace)

### Symptom
After SAC connects, browser shows the local banner then a **black screen** — no host data appears.

### Root cause
Likely browser-side issue. SAC's local terminal UI has a fixed-size buffer; if the server-side serial log buffer dump is large, it can scroll the welcome banner out of view, but the screen should not stay black indefinitely.

### How SAC connect normally works (for reference)
1. Browser shows initial banner locally (before host connection completes)
2. Backend pushes "successfully connected to serial port of the VM" message
3. SAC sends a slice of the host's serial output buffer (the same buffer ACIS reads for serial logs)

### Investigation
Always collect **browser traces** (HAR file via Edge/Chrome F12) — see [`SAC-HowTo-CollectBrowserTraces`](#sac-howto-collectbrowsertraces--collect-edgechrome-har-traces-for-sac-rdpssh-failures-before-telemetry).

Look for:
- Critical browser console errors (F12 → Console tab)
- Failed HTTP/WSS requests in the HAR
- Whether any host-pushed message arrived before the black screen

### Mitigation
Depends on what the HAR shows. Typically: ask customer to test in a different browser; if same issue → escalate to SAC team with HAR + browser version.

---

## SAC-HowTo-ChannelMgmt — SAC CMD Channel Management (open / switch / close / lock / timeout config)

**Scope**: How to manage multiple EMS channels in SAC on a Windows VM.

### Open a new channel
At the SAC `SAC>` prompt: type `cmd` → EMS spawns a new channel `Cmd0001` (incrementing index).

### Switch between channels
- By number: `ch -si <#>`
- By name: `ch -sn <ChannelName>`
- Keyboard shortcut to next channel: `ESC+TAB`
- Back to EMS prompt: `ESC+TAB+0` (then press Enter)

### List + close channels
- List all channels (status A=Active / I=Inactive, type V=VT-UTF8 / R=Raw): `ch`
- Close by number: `ch -ci <#>`
- Close by name: `ch -cn <ChannelName>`
- **Emergency kill all** (last resort — also kills the channel you're in): `taskkill /f /im sacsess.exe`

### Channel timeout config (default 30 min idle → Inactive)
Maximum 24 hours allowed. Set via registry:
```cmd
reg add "HKLM\SYSTEM\CurrentControlSet\Services\sacsvr\Parameters" /v TimeOutInterval /t REG_DWORD /d <MINUTES>
```

Disable timeout entirely (channels stay Active forever):
```cmd
reg add "HKLM\SYSTEM\CurrentControlSet\Services\sacsvr\Parameters" /v TimeOutDisabled /t REG_DWORD /d 1
```

### Lock all CMD channels
From the EMS prompt (NOT from a CMD channel): `LOCK` — locks all CMD channels at once.

---

## SAC-HowTo-CollectBrowserTraces — Collect Edge/Chrome HAR traces (for SAC + RDP/SSH failures before telemetry)

**Scope**: When a SAC / RDP / SSH connection attempt fails BEFORE telemetry is generated (which takes ~2 hours to surface), browser HAR traces are the only way to see what's happening on the client side.

Companion: [Azure Portal How To Collect Browser Traces](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/506417).

### Edge
1. Open Azure Portal → VM blade
2. **F12** → Network tab → Stop (■) → Clear (🗑)
3. Click Play (▶) → reproduce the SAC failure
4. Stop → Export as **HAR** file

### Chrome
1. Same — F12 → Network tab → Stop Recording → Clear
2. Record Network Log → reproduce
3. Stop → right-click trace → **Save as HAR with context**

### What to look at in HAR
- WebSocket upgrade attempts (HTTP 101 expected; non-101 = blocked)
- Failed requests to `*.gateway.serialconsole.azure.com`
- TLS handshake failures
- Proxy interception evidence

---

## SAC-HowTo-SessionId — Gather Error Log per Connection Attempt (sessionId lookup + reason mapping, 2 KQL)

**Scope**: When the SAC connection reached the container (user sees "Connecting to console of {vmname}" in Portal), a `SessionID` was issued. Use it to pull all validation telemetry for THAT specific attempt.

If the connection failed BEFORE reaching the container (e.g., ACS container provision failure), there may be telemetry but no `serialTerminalID` — fall back to [`SAC-HowTo-E2EView`](#sac-howto-e2eview--get-unified-e2e-view-of-serial-console-request-portalsessionid-3-kql).

**Prerequisite**: connected to Azure VPN OR SAW device to run the KQL.

### Step 1 — find SessionID by sub + RG + VM
```kusto
cluster('azlinux.kusto.windows.net').database('serialconsole').ConnectorContainerActivity
| where TIMESTAMP > ago(1h)
| where subscriptionId == "{SubscriptionId}"
| where message has "SESSION_ID"
| where vmName == "{VMName}"
| project TIMESTAMP, message, vmName, subscriptionId
```
Pick the entry near the customer's failed-attempt timestamp; extract `SessionID` from `message`.

### Step 2 — track that SessionID for the full validation chain
```kusto
cluster('azlinux.kusto.windows.net').database('serialconsole').ConnectorContainerActivity
| where TIMESTAMP > ago(1h)
| where subscriptionId == "{SubscriptionId}"
| where sessionId == "{SessionID}"
| project PreciseTimeStamp, message, resourceGroup, sessionId
```

### Interpret — look for `Code 4XXX` reason strings
Examples:
- `Enter sessionCleanup():: Source: CustomerDataChannel::signalHost(). Code: 4403. Reason: StorageAccountForbidden`
- `Caught error in uploading pages to blob::: RestError: This request is not authorized to perform this operation.`

The reason string maps directly to the underlying problem (e.g., `StorageAccountForbidden` → SA firewall blocks SerialConsole, route to [`SAC-Connect-403`](#sac-connect-403--sac-403-forbidden-rbac-missing-vm-contributor-or-sa-firewall-blocking) / [`SAC-Connect-429`](#sac-connect-429--sac-429-err_bad_request-sa-firewall-blocks-serialconsole-service-tag-ips)).

---

## SAC-HowTo-E2EView — Get Unified E2E View of Serial Console Request (portalSessionId, 3 KQL)

**Scope**: SAC E2E spans **3 sources** (customer browser → ACS container → host service) whose clocks don't perfectly align — but combining their telemetry gives the best end-to-end timeline.

**Prerequisite**: connected to Azure VPN OR SAW device. If connection didn't reach container, `portalSessionId` may be missing — then start with the connection-error-specific TSG instead.

### Path A — known timeframe, want the FIRST attempt in that window
```kusto
let StartDate = datetime({StartDate});
let EndDate = datetime({EndDate});
let subscription = "{SubscriptionId}";
let vm = "{VMName}";
cluster('AzLinux').database('SerialConsole').PortalActivity
| where TIMESTAMP >= StartDate and TimeStamp <= EndDate
| where subscriptionId contains subscription
| where vmName contains vm
| project portalSessionId, TIMESTAMP, message, vmName, ContainerName
```

### Path B — multiple attempts in the window; pick a specific portalSessionId

#### Step B1: determine portalSessionId
```kusto
let subscription = "{SubscriptionId}";
let vm = "{VMName}";
cluster('AzLinux').database('SerialConsole').PortalActivity
| where TIMESTAMP > ago(1h)
| where subscriptionId contains subscription
| where vmName contains vm
| project portalSessionId, TIMESTAMP, message, vmName, ContainerName
| take 1
```

#### Step B2: pull full timeline by portalSessionId
```kusto
cluster('AzLinux').database('SerialConsole').PortalActivity
| where TIMESTAMP > ago(1d)
| where portalSessionId contains "{PortalSessionId}"
| project TableName = "PortalActivity", TIMESTAMP, message, vmName
```

Same shape can be applied to other tables (ConnectorContainerActivity, SerialConsoleHostMessages) → union the 3 → single chronological view.

---

## SAC-HowTo-HostNode — Determine Target Host Node (serialTerminalId → SerialConsoleHostMessages + SerialConsoleUsage, Jarvis fallback)

**Scope**: Map a SAC connection to its target host node. 3 methods.

### Method 1 — `SerialConsoleHostMessages` (host receives signal to connect to container)
```kusto
cluster('AzLinux').database('AzureLinux').SerialConsoleHostMessages
| where TimeStamp > ago(1d)
| where Message contains "{serialTerminalId}"
```
Requires several hours for host logging to surface in Kusto.

### Method 2 — `SerialConsoleUsage` (best-effort metadata mapping)
```kusto
cluster('AzLinux').database('AzureLinux').SerialConsoleUsage
| where TimeStamp > ago(1d)
| where SerialTerminalId == "{serialTerminalId}"
```

### Method 3 — Manual via Jarvis (requires SAW or vSAW)
1. Use `serialTerminalId` → get Subscription / location / RG / VMName
2. Jarvis → **CRP → VM Operations → GET VM** (pass sub/loc/RG/VM, request `Model + InstanceView`) → returns fabric name + tenant name
3. Jarvis → **SupportabilityFabric → Fabric Operations → Get Container Settings by VM name** (pass fabric name + tenant name + VMName) → returns **Node Id + Container Id**

How to get the `serialTerminalId` itself: see [serialTerminalId TSG](https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/496035).

---

## SAC-HowTo-HostVersion — Determine Host Package Version (agent version counts by Datacenter/Cluster)

**Scope**: Check if SAC host-side package version is the suspect when connection setup fails on reaching the host.

### Query 1 — agent version counts by DC + Cluster
```kusto
cluster('AzLinux').database('AzureLinux').SerialConsoleHostMessages
| summarize TIMESTAMP = max(TIMESTAMP) by Cluster, NodeId
| join (
    NamedPipeServicesPackageVersion
    | project DataCenter, TIMESTAMP, Cluster, NodeId, AgentPackageName
) on Cluster, NodeId, TIMESTAMP
| project DataCenter, TIMESTAMP, Cluster, NodeId, AgentPackageName
| summarize NodeCount = count(NodeId) by DataCenter, Cluster, AgentPackageName
```

### Query 2 — find nodes running a specific AgentPackageName (use the value from Query 1)
```kusto
cluster('AzLinux').database('AzureLinux').SerialConsoleHostVersionInfo
| summarize TIMESTAMP = max(TIMESTAMP) by Cluster, NodeId
| join (
    NamedPipeServicesPackageVersion
    | project DataCenter, TIMESTAMP, Cluster, NodeId, AgentPackageName
) on Cluster, NodeId, TIMESTAMP
| project DataCenter, TIMESTAMP, Cluster, NodeId, AgentPackageName
| where AgentPackageName == "{AgentPackageName}"
```

Use these to identify if a particular host package version is correlated with the failure (e.g., stale rollout, regression in a new build).
