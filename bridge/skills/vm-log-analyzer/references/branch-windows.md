# Windows VM Log Analysis Reference

> Domain knowledge for Windows guest OS log analysis — event logs, CBS, RDP, WU, AD, IID/TSS/xray packages, BSOD bugcheck context.
> The **W-Step 1/2/3 workflow below is a Windows-specific checklist** (classify → assess log availability → analyze) — use it as a guide, not a hard pipeline. Skip steps the user has already answered (e.g. if user only asked about RDP, jump straight to the RDP section).

## Contents

- [Public Info](#public-info)
  - [Log Package Type Quick Reference](#log-package-type-quick-reference)
  - [Azure IID (Inspect IaaS Disk) — Windows Package Layout](#azure-iid-inspect-iaas-disk--windows-package-layout) — see also [iid-package-layout.md](iid-package-layout.md) for the cross-platform shared rules
  - [Knowledge Search Trigger Rules](#knowledge-search-trigger-rules)
  - [Generic Event ID Quick Reference](#generic-event-id-quick-reference)
  - [MCP Server Concurrent Query Table](#mcp-server-concurrent-query-table)
- [W-Step 1 — Classification / Routing](#w-step-1--classification--routing)
- [W-Step 2 — Log Availability Assessment](#w-step-2--log-availability-assessment)
- [W-Step 3 — Analysis and Reporting](#w-step-3--analysis-and-reporting)
- [RDP](#rdp) — connection flow, Event IDs, decision tree, repair commands
- [No Boot / BSOD](#no-boot--bsod) — boot diagnostics, stop codes, decision tree, WinRE repair
- [Unexpected Restart Triage](#unexpected-restart-triage) — Event 1074 5-tuple decision tree, Crash vs Hang, dump compliance, timezone trap
- [DND](#dnd) — Windows Update / CBS / servicing / activation / driver failures
- [Directory Services](#directory-services) — domain join, Netlogon, w32tm
- [Performance](#performance) — Event 2004, pool exhaustion, perfmon/PerfView

---

## Public Info

### Log Package Type Quick Reference

| Package | Source | Typical contents |
|---|---|---|
| **IID** (Inspect IaaS Disk) | Azure Support Center → VM → Diagnose and Solve → Inspect IaaS Disk | Whole OS disk snapshot: `device_0/Windows/System32/{config,winevt/Logs}/` (registry hives + 70+ evtx) + `device_0/WindowsAzure/Logs/` (agent + extension logs) + `device_0/Packages/Plugins/` |
| **TSS** (TroubleShooting Script) | Run TSS.ps1 inside the VM with scenario-specific parameters | Scenario-specific logs (RDP/WU/AD/etc.) + network info |
| **xray** | Embedded in TSS or run standalone | Pre-analysis result (ISSUES-FOUND files) — read first |
| **Engineer pre-analysis** (at case dir root, not from IID) | CSS engineer runs `Get-WinEvent -Path` / `reg load` against the IID hives, exports to `.txt` | `findings.txt` (JSON from ASC GuestAnalyzer), `system_errors.txt`, `app_errors.txt`, `rdpcore_*.txt`, `rcm_*.txt`, `lsm_op.txt`, `schannel_xml.txt`, `tls_registry_output.txt` + `query_tls.ps1` |

### Azure IID (Inspect IaaS Disk) — Windows Package Layout

> The IID skeleton (`diskinfo.txt` / `results.txt` / `scanfilelist.tsv` / `device_N/`), the `results.txt` reading rules, the FAILED-whitelist principle, the CredentialScanner footer, and the IID + ConsoleLog pairing pattern are **identical across Linux and Windows** — see [`iid-package-layout.md`](iid-package-layout.md) for the shared rules.
>
> This section covers **Windows-only** specifics: case-dir layout with engineer pre-analysis files, `device_0/Windows/` content, evtx binary + size warnings, registry hive offline access, `WindowsAzure/` agent state, and the Windows triage cheat sheet.
>
> Real reference: case `2601160030001591` (Windows Server 2012 R2).

#### Top-level case directory (Windows convention)

A typical Windows support case directory mixes the IID archive with engineer-generated pre-analysis files:

```
<caseId>/
├── <VMname>-InspectIaaSDisk-<hash>.ztv_<hash>.zip      ← raw IID archive (~180 MB compressed)
├── <VMname>-InspectIaaSDisk-<hash>.ztv_<hash>/         ← extracted IID package (skeleton in iid-package-layout.md)
│   └── device_0/                                       ← OS disk content (see below)
│       ├── Windows/                                    ← Windows filesystem subset
│       ├── WindowsAzure/                               ← Azure VM Agent state + logs
│       └── Packages/Plugins/                           ← Azure VM extension .zip packages
├── SR_<datetime>_<hash>[.zip]                          ← sibling Support Recovery package (separate tool)
└── *.txt + *.ps1                                       ← ★ engineer pre-analysis files (read FIRST)
    ├── findings.txt                                    ← JSON from ASC GuestAnalyzer (Critical/Warning + aka.ms TSG URLs)
    ├── system_errors.txt                               ← Get-WinEvent dump of System.evtx Error/Warning
    ├── app_errors.txt                                  ← Get-WinEvent dump of Application.evtx Error/Warning
    ├── rdpcore_op.txt / rdpcore_admin.txt              ← RemoteDesktopServices-RdpCoreTS events
    ├── rcm_op.txt / rcm_admin.txt                      ← TerminalServices-RemoteConnectionManager
    ├── lsm_op.txt                                      ← TerminalServices-LocalSessionManager
    ├── schannel_xml.txt                                ← Schannel events (XML format)
    ├── tls_registry_output.txt                         ← offline reg query results (SCHANNEL/RDP-Tcp/FIPS)
    └── query_tls.ps1                                   ← the script that produced tls_registry_output.txt
```

> **Read order rule**: engineer pre-analysis files at the case-dir root **FIRST** → IID `results.txt` top 30 lines (per [iid-package-layout.md](iid-package-layout.md)) → drill into specific `.evtx` only when pre-analysis is insufficient.

#### Windows-specific FAILED whitelist (in `results.txt`)

A normal Windows VM IID has ~50% FAILED operations (~204 of 415 in observed cases). The shared principle is in [iid-package-layout.md § "FAILED-line whitelist principle"](iid-package-layout.md#the-failed-line-whitelist-principle); Windows-specific expected failures:

| FAILED pattern | Why it's expected |
|---|---|
| `Microsoft-ServiceFabric%4*.evtx` | VM is not a Service Fabric node |
| `Active Directory Web Services.evtx`, `DFS Replication.evtx`, `DNS Server.evtx`, `Directory Service.evtx`, `Microsoft-Windows-DNSServer%4Audit.evtx` | VM is not a DC / DNS server |
| `Microsoft-Windows-BitLocker*.evtx` | BitLocker not enabled |
| `Microsoft-Windows-FSLogic*.evtx`, `Microsoft-Windows-FSLogix*.evtx` | FSLogix not installed |
| `OpenSSH%4*.evtx` | OpenSSH server not installed |
| `Microsoft-Windows-CAPI2%4Operational.evtx` | CAPI2 logging off by default |
| `MicrosoftAzureRecoveryServices-Replication.evtx` | Not ASR-protected |
| `/Program Files/Microsoft HPC Pack 2019/...` and `2016/...` (14 entries) | Not an HPC node |
| `/Windows/Panther/VmAgentInstaller.xml` | Agent installed via different path |
| `Microsoft-Windows-schannel%4Operational.evtx`, `Microsoft-Windows-RemoteDesktopServices-RemoteDesktopSessionManager%4Admin.evtx` | Channel/RDS-SM operational logging off by default on Server 2012 R2 |

**Real FAILED that matters**: anything under `Registry Hives` (SOFTWARE/SYSTEM copy failed = disk corruption), core evtx (System/Application/Security copy failed = filesystem issue), mount failures in the top section.

#### `device_0/Windows/System32/winevt/Logs/` — Event logs

~70 evtx files. **All are binary** — you cannot `view`/`Get-Content` them; use `Get-WinEvent -Path` or `wevtutil epl`.

**Critical size warnings** (default Windows Server limits):

| File | Default size | Reference case |
|---|---|---|
| `Security.evtx` | **1024 MB** (1 GB) | 1024 MB (at cap) |
| `Application.evtx` | 20 MB (often raised to 200+ MB by GPO) | 196 MB |
| `System.evtx` | 20 MB (often raised) | 86 MB |
| `Microsoft-Windows-PowerShell%4Operational.evtx` | 15 MB | 15 MB |
| `Microsoft-Windows-TaskScheduler%4Operational.evtx` | 10 MB | 10 MB |
| Most other channels | 1–8 MB | varies |

**Conversion commands** (run on a Windows analyst box; do NOT try in WSL):

```powershell
# Filter to Error/Warning, full message body
Get-WinEvent -Path .\System.evtx -FilterXPath "*[System[Level<=3]]" |
    Format-List TimeCreated, Id, ProviderName, Level, Message |
    Out-File system_errors.txt

# Single Event ID, all levels
Get-WinEvent -Path .\System.evtx -FilterHashtable @{Id=41} | Format-List *

# Convert to XML for grep-friendly form
wevtutil epl .\Security.evtx security_export.xml /lf:true   # /lf treats input as logfile
```

> **Performance trap**: `Get-WinEvent -Path Security.evtx` (full 1 GB scan, no filter) can take 5–10 min and may OOM. Always use `-FilterHashtable` or `-FilterXPath` with `Id=` or `TimeCreated >=` first.

#### `device_0/Windows/System32/config/` — Registry hives

| File | Typical size | Notes |
|---|---|---|
| `SOFTWARE` | 100–200 MB | HKLM\SOFTWARE — installed apps, run keys, GPO settings, Windows component config |
| `SYSTEM` | 50–100 MB | HKLM\SYSTEM — services, drivers, network adapters, mounted devices, last-known-good |
| `SECURITY` | small | HKLM\SECURITY (LSA secrets, etc.) |
| `SAM` | small | HKLM\SAM (local accounts) |
| `DEFAULT` | small | HKU\.DEFAULT |
| `*.LOG1` / `*.LOG2` | varies | Transaction logs — **MUST replay** to get a consistent view of the hive |

**Two ways to read** (offline, on a Windows analyst box):

```powershell
# Method A: reg load — quick reg query (engineer style — see query_tls.ps1)
reg load HKLM\OFFLINE_SYSTEM "<iid>\device_0\Windows\System32\config\SYSTEM"
reg query "HKLM\OFFLINE_SYSTEM\ControlSet001\Control\SecurityProviders\SCHANNEL\Protocols" /s
reg unload HKLM\OFFLINE_SYSTEM

# Method B: Hive Editor / offline hive tools — recommended for browsing / deleted-key recovery
```

**Recommendation**: for non-trivial work, use a Hive Editor or `reg load` offline for browsing, hive comparison, transaction-log replay, and deleted-key recovery. Use `reg load` inline only when you need a single key (TLS settings, RDP-Tcp config, etc.).

#### `device_0/WindowsAzure/` — Azure VM Agent

```
WindowsAzure/
├── Config/<GUID>.xml + <GUID>/                 ← Goal State configs (one folder per push)
├── GuestAgent_<version>/                       ← Agent binaries (multiple versions accumulate)
└── Logs/
    ├── WaAppAgent.log                          ← ★ main agent log (often 5-10 MB)
    ├── TransparentInstaller.log                ← ★ extension install / upgrade log (often 5-10 MB)
    ├── MonitoringAgent.log                     ← MA install/start
    ├── AggregateStatus/                        ← *.json (one snapshot every ~15 sec, valuable for timeline)
    └── Plugins/<extension-name>/<version>/     ← per-extension logs (CommandExecution_*.log, etc.)
```

| File | When to read it |
|---|---|
| `WaAppAgent.log` | Agent heartbeat, goal-state processing, plugin-handler invocations, "ProvisioningError" / "Error: failed to" lines |
| `TransparentInstaller.log` | Extension MSI install / agent self-update failures |
| `AggregateStatus/*.json` | Per-15-sec snapshot of every extension's reported status (handler version, last status, error code). Excellent for "when did X extension fail" timelines. |
| `Plugins/<ext>/<ver>/CommandExecution_*.log` | CustomScript / DSC / MDE / etc. — the actual command's stdout/stderr |

#### Engineer pre-analysis files — read FIRST

When a CSS engineer attaches IID to a case, they often pre-digest it. **Always check the case-dir root first.**

| File | Format | What it is |
|---|---|---|
| `findings.txt` | **JSON** | ASC GuestAnalyzer output. Contains `AlertName`, `Type` (Critical/Warning/Informational), `Section: GuestAnalyzer`, and often `TSG: https://aka.ms/...`. **Equivalent to Linux xray ISSUES-FOUND.** |
| `system_errors.txt` / `app_errors.txt` | Plain text (Get-WinEvent dump) | `TimeCreated / Id / ProviderName / Level / Message` — all Error+Warning events from System.evtx / Application.evtx. The fastest way to spot Event 41 (Kernel-Power), 6008 (unexpected shutdown), 7000/7001/7031 (service failures). |
| `rdpcore_op.txt` / `rdpcore_admin.txt` / `rdpcore_op_detail.txt` | Plain text | Microsoft-Windows-RemoteDesktopServices-RdpCoreTS events. Read for RDP "internal error" / "session disconnected" cases. |
| `rcm_op.txt` / `rcm_admin.txt` | Plain text | Microsoft-Windows-TerminalServices-RemoteConnectionManager — RDP listener / port binding issues. |
| `lsm_op.txt` | Plain text | Microsoft-Windows-TerminalServices-LocalSessionManager — session state changes, GINA / Winlogon. |
| `schannel_xml.txt` | XML | Schannel events (36870 / 36871 / 36874 / 36888) — TLS/SSL credential failures, cipher negotiation. |
| `tls_registry_output.txt` | Plain text | Output of offline `reg query` against SCHANNEL / Protocols / Ciphers / Hashes / KeyExchangeAlgorithms / RDP-Tcp / FIPS keys. |
| `query_tls.ps1` | PowerShell | The script that produced `tls_registry_output.txt`. Pattern: `reg load HKLM\OFFLINE_SYSTEM <hive>` → `reg query` → `reg unload`. Reusable template for any offline hive query. |

> **Provenance note**: these files are **not part of IID itself** — they're engineer-generated by running tools against the extracted IID. Trust them as a head start, but if the customer claim contradicts them, fall back to the raw `.evtx` (the engineer's filter might have missed something).

#### Triage cheat sheet — symptom → which file FIRST

| Symptom | Read this first | Then drill into |
|---|---|---|
| **Unexpected reboot / BSOD** | `system_errors.txt` (Event 41 Kernel-Power + 6008 EventLog pair) | `app_errors.txt` Event 1001 WER (dump path) → `device_0/Windows/Minidump/*.dmp` if present |
| **RDP failure** | `rdpcore_op.txt` + `rcm_op.txt` + `tls_registry_output.txt` (TLS misconfig is the #1 cause) | `schannel_xml.txt` → System.evtx Schannel events |
| **Service start failure** | `system_errors.txt` (Event 7000/7001/7031/7034) | `device_0/Windows/System32/config/SYSTEM` → check service config via `reg load` |
| **Certificate expiry / auto-enrollment** | `app_errors.txt` (Event 64 CertificateServicesClient-AutoEnrollment) | `device_0/Windows/System32/CertSrv/CertEnroll/` if present |
| **TLS / Schannel error** | `tls_registry_output.txt` + `schannel_xml.txt` | `query_tls.ps1` (re-run with extra keys if needed) |
| **Extension failure** | `findings.txt` (often pre-flagged) | `device_0/WindowsAzure/Logs/WaAppAgent.log` + `Plugins/<ext>/<ver>/CommandExecution_*.log` |
| **Slow boot / boot hang** | `findings.txt` + `system_errors.txt` | `device_0/Windows/Panther/setup.etl` (ETW, needs PerfView) + System.evtx Event 100 (Diagnostics-Performance) |
| **GPO / domain join issue** | `system_errors.txt` (Event 1058/1006 GroupPolicy, 5719 NETLOGON) | Microsoft-Windows-GroupPolicy%4Operational.evtx + Netlogon.log |
| **Patching / Windows Update issue** | `findings.txt` | `device_0/Windows/Logs/CBS/CBS.log` + `device_0/Windows/SoftwareDistribution/ReportingEvents.log` |
| **Network adapter / NIC issue** | `system_errors.txt` (Event 4201/4202 Netio, 27 e1iexpress) | Microsoft-Windows-NdisImPlatform%4Operational.evtx + NetworkProfile evtx |

---

### Knowledge Search Trigger Rules

| Situation | Trigger action |
|---|---|
| Unrecognized error code | Trigger `vm-knowledge-search` → csswiki + mslearn |
| Look up known internal Bug | Call `osbugs` MCP (Microsoft OS project, search work items) |
| Look up internal KB / resolved cases | Call `internalkb` MCP (ContentIdea project, search) |

> `vm-knowledge-search` covers the generic knowledge layer; `osbugs` and `internalkb` are Windows OS-specific and called directly from this branch.

### Generic Event ID Quick Reference

> Cross-scenario events that any Windows VM analysis should scan first. Scenario-specific Event IDs appear under their respective sections.

| EventID | Source | Meaning | Scenario |
|---|---|---|---|
| **System start/stop** | | | |
| 6005 | EventLog | EventLog service started (system startup marker) | Boot / startup-time confirmation |
| 6006 | EventLog | EventLog service stopped (clean shutdown marker) | Boot / shutdown-time confirmation |
| 6009 | EventLog | OS version info (logged at boot) | Boot / OS version confirmation |
| 41 | Kernel-Power | Unexpected reboot (includes BugcheckCode) | BSOD / unexpected reboot |
| 6008 | EventLog | Previous unexpected shutdown | BSOD / unexpected power loss |
| 1074 | User32 | A process initiated shutdown/restart (includes reason code and process name) | Planned reboot / WU reboot |
| **Service crash** | | | |
| 7031 | Service Control Manager | Service unexpected termination | Performance / service fault |
| 7034 | Service Control Manager | Service repeatedly terminated unexpectedly | Performance / service fault |
| 7023 | Service Control Manager | Service terminated with error (includes error code) | All scenarios |
| 7000 | Service Control Manager | Service failed to start | Boot / service dependency |
| 7001 | Service Control Manager | Service did not start due to dependency failure | Boot / service dependency |
| 7036 | Service Control Manager | Service state change (entered running/stopped) | Service state tracking |
| **Application crash** | | | |
| 1000 | Application Error | Application crash — includes faulting module name and exception code | RDP (explorer crash) / Performance |
| 1001 | Windows Error Reporting | WER report (detailed module info and BugCheck parameters) | BSOD / app crash |
| 1026 | .NET Runtime | Unhandled exception in .NET application | App failure |
| **Disk / storage** | | | |
| 55 | Ntfs | NTFS filesystem structural corruption | BSOD / Boot |
| 153 | disk | Disk I/O retry (storage latency) | Performance / Boot |
| 129 | storahci / storport | Storage device reset (timeout) | Performance / Boot |
| 51 | disk | Disk error during paging operation | Performance |
| 11 | disk | Disk controller error | Performance / Boot |
| **Security / login** | | | |
| 4624 | Security | Successful logon (includes logon type and source IP) | RDP / audit |
| 4625 | Security | Failed logon (includes detailed SubStatus reason) | RDP / Directory Services |
| 4648 | Security | Logon attempted with explicit credentials (e.g. runas) | Security audit |

### MCP Server Concurrent Query Table

In W-Step 3 analysis you may concurrently query the following MCP servers to enrich the diagnostic conclusions. If any server is unavailable, skip it and do not block the flow.

| MCP Server | Query focus |
|---|---|
| `mslearn` | Official error code definitions, KB articles, Microsoft-recommended fixes |
| `csswiki` | CSS internal Wiki — known issues, support SOPs, escalation guidance |
| `seektheway` | seektheway Wiki — troubleshooting guides, service-specific runbooks |
| `azurewiki` | msazure Wiki — Azure platform known issues, engineering notes |
| `arr` | Azure Rapid Response — active incidents, rapid-response guidance |
| `osbugs` | Microsoft OS work items — Windows known bugs |
| `internalkb` | ContentIdea internal KB — patterns from resolved cases |
| `azuremcp` | Azure resource context — VM config, SKU constraints, platform events |

---

## W-Step 1 — Classification / Routing

Based on the problem description and screenshots, classify into one of the following scenarios and jump to the corresponding H3 section:

| Scenario | Trigger signals | Jump to |
|---|---|---|
| **RDP** | Cannot connect · black screen · CredSSP · NLA · Remote Desktop | [§ RDP](#rdp) |
| **No Boot / BSOD** | VM cannot start · blue screen · Stop Code · 0x... · boot loop · OS not found | [§ No Boot / BSOD](#no-boot--bsod) |
| **DND** (Devices and Deployment) | Windows Update failure · KB won't install · CBS errors · activation failure · driver install · sysprep | [§ DND](#dnd) |
| **Directory Services** | Cannot join domain · Netlogon errors · w32tm / time sync · Kerberos failure | [§ Directory Services](#directory-services) |
| **Performance** | VM slow · high CPU/memory/disk · service crash · resource exhaustion · pool exhaustion | [§ Performance](#performance) |

If classification is ambiguous, ask the user to clarify before proceeding.

---

## W-Step 2 — Log Availability Assessment

### When a log package is already provided

Scan the folder and identify the key files:

```powershell
Get-ChildItem -Path "<LogPath>" -Recurse |
  Select-Object Name, Length, LastWriteTime |
  Sort-Object LastWriteTime -Descending
```

If an `xray_ISSUES-FOUND_*.txt` file is present, **read it first** to obtain the pre-analysis conclusions before drilling into the raw logs.

### When no logs are available

**Preferred**: collect an IID package via ASC (Inspect IaaS Disk).
**Alternatives** (by scenario):

| Scenario | Quick collection command |
|---|---|
| DND / WU | `wevtutil epl Microsoft-Windows-WindowsUpdateClient/Operational C:\logs\wu.evtx` |
| DND / CBS | `copy C:\Windows\Logs\CBS\CBS.log C:\logs\` |
| RDP | `wevtutil epl Microsoft-Windows-TerminalServices-LocalSessionManager/Operational C:\logs\rdp.evtx` |
| No Boot | Azure Portal → VM → Boot Diagnostics (screenshot) |
| Directory Services | `copy C:\Windows\debug\netlogon.log C:\logs\` && `w32tm /query /status > C:\logs\w32tm.txt` |

---

## W-Step 3 — Analysis and Reporting

### Analysis Flow

1. **Extract query terms**: pull error codes, Event IDs, KB numbers, and symptom keywords from the description + error screenshots
2. **Knowledge search** (concurrent):
   - `vm-knowledge-search` → csswiki + mslearn (generic knowledge layer)
   - `osbugs` → search error code / symptom keywords (Windows OS known bugs)
   - `internalkb` → search error code / symptom keywords (internal KB / resolved cases)
3. **Read logs**: follow each scenario's "priority log read" order and cross-check against the knowledge search results
4. **Produce the RCA report**

### RCA Report Format

```
## Diagnosis: [Scenario] — [one-line root cause]

**Confidence:** High / Medium / Low

> Confidence criteria:
> - **High**: log evidence clearly points to the root cause and MCP references (mslearn/osbugs/csswiki) confirm the match
> - **Medium**: logs likely match a pattern, MCP partially supports, but key evidence is missing
> - **Low**: evidence insufficient — explicitly state what data is still needed (e.g. dump file, specific event logs, etc.)

### Root Cause
[Clearly explain the failure, citing log evidence + knowledge-search findings]

### Key Log Evidence
**[log filename, timestamp]**
```
[Raw log snippet — preserve original text, timestamps, error codes]
```
> Explanation: [what this entry shows and how it ties to the root cause]

### Repair Steps
1. [Copy-paste-runnable command]
2. [Next step]
3. [Verification command]

### References
- [mslearn / csswiki] Doc title — URL — relevance to this case
- [osbugs] Bug #XXXXX — description and status
- [internalkb] Article title — description
```

---

## RDP

### RDP Connection Flow

```
Client → NSG/Firewall → Public IP / LB → Windows Firewall → RDP Listener (3389) → NLA/CredSSP Auth → Session
```

> Walk this path layer by layer during troubleshooting; first identify which layer is failing.

### Priority Log Read

| Priority | Log / file | IID/TSS package path |
|---|---|---|
| 1 | LocalSessionManager event log | `*_evt_*TerminalServices*.txt/.csv` |
| 2 | System event log | `*_evt_System.txt` |
| 3 | Security event log | `*_evt_*Security*.txt` |
| 4 | Registry: TermServices | `*_reg_TermServices.txt` |
| 5 | Network / proxy | `*_NETWORK_Proxy.txt`, `*_NETWORK_TCPIP_info.txt` |

### Key Event IDs

| EventID | Source | Meaning |
|---|---|---|
| 1149 | TerminalServices-LocalSessionManager | User authenticated (RDP pre-session) |
| 21 | TerminalServices-LocalSessionManager | Session logon succeeded |
| 24 | TerminalServices-LocalSessionManager | Session disconnected |
| 25 | TerminalServices-LocalSessionManager | Session reconnect succeeded |
| 39 | TerminalServices-LocalSessionManager | Session disconnected by the network |
| 40 | TerminalServices-LocalSessionManager | Session disconnected — reason code is the key |
| 1158 | TerminalServices-LocalSessionManager | Maximum number of connections exceeded |
| 261 | TerminalServices-RemoteConnectionManager | Listener accepted a new connection |
| 258 | TerminalServices-RemoteConnectionManager | Listener state change (started/stopped) |
| 131 | TerminalServices-RdpCoreTS | Connection disconnected — includes disconnect reason code |
| 140 | TerminalServices-RdpCoreTS | Connection from an IP disconnected (frequent = unstable network) |
| 226 | TerminalServices-RdpCoreTS | RDP connection attempt details |
| 56 | TermDD | Terminal Device Driver error |
| 4625 | Security | Logon failure — check SubStatus |
| 4771 | Security | Kerberos pre-authentication failure |

### Decision Tree

```
Cannot RDP
├── "Remote Desktop can't connect to the remote computer"
│   ├── Is RDP enabled? reg_TermServices.txt → fDenyTSConnections = 0 means enabled
│   ├── Is port 3389 listening? NETWORK_TCPIP_info.txt
│   └── Is the firewall blocking 3389? (NSG or Windows Firewall)
│
├── "CredSSP / NLA / Oracle remediation"
│   ├── Client and server CredSSP patch levels do not match
│   └── Fix: set AllowEncryptionOracle = 2 on the client, or patch both sides
│
├── NLA prevents connection (expired cert, missing CredSSP, etc.)
│   ├── Temporarily disable NLA:
│   │   Set-ItemProperty "HKLM:\...\WinStations\RDP-Tcp" -Name UserAuthentication -Value 0
│   └── Re-enable NLA after the fix
│
├── Black screen after sign-in
│   ├── Event 1149 (auth success) immediately followed by Event 40 (disconnect)
│   ├── Explorer.exe failed to start (userinit/shell registry value damaged)
│   └── Server-side GPU / display driver issue
│
├── Event 56 / TermDD error
│   └── Usually caused by MTU mismatch or NIC binding configuration
│
├── Logon failure: 0xC000006D / 0xC0000064
│   ├── Wrong credentials or account locked out
│   ├── Security log Event 4625 SubStatus gives the precise reason
│   └── Unlock the account: net user <username> /active:yes (or unlock in AD)
│
├── Certificate error / self-signed cert warning
│   ├── RDP Listener certificate expired or damaged
│   └── Fix: delete the old cert → restart TermService so the system regenerates a self-signed cert
│
├── Cannot RDP after Windows Update
│   ├── Check the update install time in the System log → roll back the update
│   └── Or the update changed NLA/CredSSP behavior
│
├── Cannot RDP after NSG / firewall change
│   ├── Check that Azure NSG inbound rules allow the destination port
│   └── Check Windows Firewall rules
│
└── Frequent disconnects (connects but unstable)
    ├── Event 131/140 appearing often → network layer instability
    ├── Check Keep-Alive settings and session timeout configuration
    └── Check Azure VM network latency (VM_Graph_Reader)
```

### Common Error Codes

| Code | Meaning | Fix |
|---|---|---|
| `0xC000006D` | Wrong username/password | Verify credentials; check account lockout |
| `0xC0000064` | Account does not exist | Check the SAM/AD account |
| `0xC000006E` | Account restriction | Check logon hours / workstation restriction |
| `0x4` | NLA authentication failure | Apply CredSSP patch or set AllowEncryptionOracle |
| `0x204` | Connection refused / port closed | Enable RDP, check firewall |

### Key Registry Values

```
HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server
  fDenyTSConnections = 0    (0 = RDP enabled)

HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp
  PortNumber = 3389

HKLM\SOFTWARE\Policies\Microsoft\Windows NT\Terminal Services
  (Check whether a GPO override disables RDP)
```

### Repair Commands

```powershell
# Enable RDP via registry
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server" -Name fDenyTSConnections -Value 0

# Allow RDP through Windows Firewall
Enable-NetFirewallRule -DisplayGroup "Remote Desktop"
# Alternative (CMD / legacy systems):
# netsh advfirewall firewall set rule group="remote desktop" new enable=Yes

# Fix CredSSP Oracle Remediation (run on the connection initiator)
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\CredSSP\Parameters" -Name AllowEncryptionOracle -Value 2

# Temporarily disable NLA (when NLA is blocking the connection)
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" -Name UserAuthentication -Value 0

# Check RDP service status
Get-Service TermService | Select-Object Status, StartType

# Start the RDP service
Start-Service TermService
Set-Service TermService -StartupType Automatic

# === Session diagnostics ===
# List active RDP sessions
qwinsta
query user

# Admin force-connect to the console session
mstsc /admin

# Reconnect a disconnected session
tscon <SessionID> /dest:console

# === Azure-specific ===
# Reset VM password via Azure CLI (when login is impossible)
# az vm user reset-password --resource-group <RG> --name <VM> --username <user> --password <newpwd>
```

---

## No Boot / BSOD

### Priority Log Read

| Priority | Log / file | IID/TSS package path |
|---|---|---|
| 1 | System event log | `*_evt_System.txt` |
| 2 | BCD output | `*_BCDEdit.txt` |
| 3 | CBS.log | `logs\CBS\CBS.log` |
| 4 | Boot Diagnostics screenshot | Azure Portal → VM → Boot Diagnostics |
| 5 | Memory Dump | `%SystemRoot%\MEMORY.DMP` or `Minidump\*.dmp` |

### Screenshot Quick Classification

| Screenshot content | Likely Stop Code / problem |
|---|---|
| "INACCESSIBLE_BOOT_DEVICE" | 0x7B — storage driver missing |
| "SYSTEM_THREAD_EXCEPTION_NOT_HANDLED" | 0x7E — third-party driver fault |
| "PAGE_FAULT_IN_NONPAGED_AREA" | 0x50 — memory / driver corruption |
| "CRITICAL_PROCESS_DIED" | 0xEF — critical OS process crashed |
| Winload error / 0xC0000034 / 0xC0000098 | BCD / winload corruption |
| Black screen with no text, spinning circle | Boot hang — check Event 41 |
| Stuck at "Getting Windows ready" | WU install was interrupted mid-flight |

### Key Event IDs

| EventID | Source | Meaning |
|---|---|---|
| 41 | Kernel-Power | Unexpected reboot — check the BugcheckCode parameter |
| 6008 | EventLog | Previous unexpected shutdown |
| 1001 | BugCheck | BSOD record — includes Stop Code + 4 parameters |
| 6 | BugCheck | Dump file written to disk |

### Common Stop Codes

| Stop Code | Name | Common cause |
|---|---|---|
| `0x7B` | INACCESSIBLE_BOOT_DEVICE | Storage driver missing after VM series change |
| `0x7E` | SYSTEM_THREAD_EXCEPTION | Third-party driver (parameter 2 = faulting module address) |
| `0x50` | PAGE_FAULT_IN_NONPAGED_AREA | Driver or memory corruption |
| `0x0A` | IRQL_NOT_LESS_OR_EQUAL | Driver IRQ violation |
| `0xEF` | CRITICAL_PROCESS_DIED | Critical OS process terminated |
| `0xC0000034` | — | BCD object not found |
| `0xC0000098` | — | winload.efi missing or corrupted |
| `0xC000021A` | STATUS_SYSTEM_PROCESS_TERMINATED | Winlogon/CSRSS crash |

### Decision Tree

```
VM won't boot / BSOD
├── Boot Diagnostics shows a Stop Code
│   ├── 0x7B INACCESSIBLE_BOOT_DEVICE
│   │   ├── Storage controller driver missing after VM series change
│   │   └── Fix: enable storahci/storport in the registry (Start = 0) or DISM-inject the driver offline
│   ├── 0xC0000034 / 0xC0000098 (BCD/winload errors)
│   │   ├── BCD corrupted or device/path misconfigured
│   │   └── Fix: rebuild BCD from WinRE (bcdedit /rebuildbcd)
│   ├── 0x7E SYSTEM_THREAD_EXCEPTION_NOT_HANDLED
│   │   └── Third-party driver fault; parameter 2 = faulting module address
│   ├── 0x50 PAGE_FAULT_IN_NONPAGED_AREA
│   │   └── Memory corruption or driver issue; dump analysis required
│   └── 0xC000021A STATUS_SYSTEM_PROCESS_TERMINATED
│       └── Winlogon or CSRSS crash — check CBS.log for failed updates
│
├── Stuck at "Getting Windows ready" / spinning circle
│   ├── Windows Update install interrupted
│   ├── Check CBS.log for unfinished servicing transactions
│   └── Fix: WinRE → DISM /remove-package to remove the recent update
│
├── OS not found / no bootable device
│   ├── MBR/VBR corrupted or active partition misconfigured
│   └── Fix: bootrec /fixmbr, /fixboot, /rebuildbcd (from WinRE)
│
└── Reboot loop (immediate restart with no error)
    ├── Check Event 41 (Kernel-Power) and Event 6008
    └── Dump analysis is usually needed to identify the faulting module
```

### Repair Commands (run from WinRE / Recovery CMD)

```cmd
REM === BCD repair ===
bcdedit /export C:\BCD_Backup
bcdedit /rebuildbcd

REM Rebuild boot files (UEFI disks)
bcdboot C:\Windows /s C: /f ALL

REM === MBR/Boot repair (MBR disks) ===
bootrec /fixmbr
bootrec /fixboot
bootrec /rebuildbcd

REM === Enable critical storage drivers (0x7B fix — runs against the offline OS) ===
reg load HKLM\BROKENSYSTEM C:\Windows\System32\config\SYSTEM
reg add "HKLM\BROKENSYSTEM\ControlSet001\Services\storahci" /v Start /t REG_DWORD /d 0 /f
reg add "HKLM\BROKENSYSTEM\ControlSet001\Services\storport" /v Start /t REG_DWORD /d 0 /f
reg add "HKLM\BROKENSYSTEM\ControlSet001\Services\stornvme" /v Start /t REG_DWORD /d 0 /f
reg unload HKLM\BROKENSYSTEM

REM === Registry RegBack recovery (registry corruption / 0x74 BAD_SYSTEM_CONFIG_INFO) ===
REM Note: Win10 1803+ disables the RegBackup scheduled task by default; the RegBack folder may be empty or all-zero
REM First verify RegBack files are valid (size > 0)
dir C:\Windows\System32\config\RegBack\
REM If RegBack is valid, back up current hives and restore
cd C:\Windows\System32\config
ren SYSTEM SYSTEM.old
ren SOFTWARE SOFTWARE.old
ren DEFAULT DEFAULT.old
copy RegBack\SYSTEM .
copy RegBack\SOFTWARE .
copy RegBack\DEFAULT .

REM === Safe Mode boot (bypass third-party drivers/services) ===
REM Enable Safe Mode with Networking
bcdedit /set {default} safeboot network
REM Enable minimal Safe Mode
bcdedit /set {default} safeboot minimal
REM Be sure to clear Safe Mode after the fix
bcdedit /deletevalue {default} safeboot

REM === Windows Update rollback ===
REM List installed updates
wmic qfe list brief /format:table
dism /image:C:\ /get-packages | findstr Package_for_KB
REM Uninstall a specific update (WinRE offline — for spinner hang / post-update BSOD)
dism /image:C:\ /remove-package /packagename:<PackageName>
REM Online uninstall (if the system can reach Safe Mode)
wusa /uninstall /kb:<KBNUMBER> /quiet /norestart
REM Check for pending servicing transactions (pending.xml present = interrupted transaction)
dir C:\Windows\WinSxS\pending.xml

REM === Driver rollback ===
REM List installed third-party drivers
dism /image:C:\ /Get-Drivers /Format:Table
REM Remove the problem driver (oem<n>.inf comes from the previous output)
dism /image:C:\ /Remove-Driver /Driver:<oem0.inf>

REM === Disk / filesystem repair ===
chkdsk C: /r /f

REM === Component store repair (offline) ===
dism /image:C:\ /cleanup-image /restorehealth /source:D:\sources\install.wim
```

---

## Unexpected Restart Triage

> Methodology distilled from CSS Wiki — `Understand-Guest-OS-Reboots_Restarts` (pageId 496368), `Get-OS-Dump-from-Azure-VM_RDP-SSH` (pageId 496340), `Windows-Guest-Restart-Investigation_Restarts` (pageId 496372). Read these wiki pages for full reasoning; this section is the working summary.

### Two questions every restart investigation must answer

1. **Was the OS still alive at shutdown time?** → branches into **Crash** vs **Hang** vs **Planned reboot**.
2. **Who triggered the action?** → branches into **Platform** (Azure-initiated maintenance / reboot / redeploy / resize) vs **Customer / Admin** (RDP-initiated, scripts, monitoring agent) vs **Guest OS itself** (Windows Update, BSOD-induced reboot).

Every other step below is in service of these two.

### Crash vs Hang vs Planned reboot — three distinct paths

| Category | Definition | Primary signal | Investigation path |
|---|---|---|---|
| **Crash** | OS terminated unexpectedly (bugcheck / BSOD). | System.evtx Event 41 with `BugcheckCode != 0`; Event 1001 (WER-SystemErrorReporting) pointing to `C:\Windows\MEMORY.DMP` | Memory dump analysis (windbg / Watson submission). See "Crash dump collection" below. |
| **Hang — soft** | OS unresponsive for a while, recovered without reboot. | No Event 41; gap in heartbeat / no logon possible but logs resume | Likely deadlock / resource exhaustion. Check Event 2004 (Resource-Exhaustion-Detector), pool exhaustion, paged/nonpaged pool counters. Often needs a live kernel dump captured while hung. |
| **Hang — hard** | OS unresponsive, required reboot to recover. | Event 41 with `BugcheckCode == 0` (no bugcheck — abrupt power loss / NMI / host-side fault); Event 6008 pair | Cannot be diagnosed from guest logs alone — there's no dump. Pivot to platform side: Hyper-V Worker Event 18590 + ASI EEE RDOS (see below). |
| **Planned reboot** | Shutdown initiated cleanly via API/script/UI. | Event 1074 (User32) present + Event 6006 (clean stop) ≈ same timestamp | Identify the trigger via the **Event 1074 decision tree** below. Do NOT pursue dump analysis. |

> ⚠️ **Trap**: `Event 41 with BugcheckCode = 0` is **not** a BSOD — it's an abrupt power loss (host crash, kernel-mode hang, NMI). No dump will exist. Don't ask the customer for a dump that physically can't be produced.

### Event 1074 — "who triggered shutdown" decision tree

Event 1074 (Source: `User32`, System log) is the single most informative event for any clean shutdown/reboot. It carries **User**, **Process**, **Reason**, **Reason Code**, **Shutdown Type**, and **`<computer>`** fields. Read all of them; never look at just one.

| `User` field | `Process` field | Most likely trigger | Verify by |
|---|---|---|---|
| `NT AUTHORITY\SYSTEM` | `svchost.exe` with Reason `Other (Planned)` or `Operating System: Service pack` | **Platform-initiated** — Azure Fabric Controller reboot / planned maintenance / redeploy / resize | Cross-check Azure Service Insights (ASI) → Resource Events / Operations Tab → look for `Restart` / `Redeploy` / `Reimage` / `Service Healing` near the timestamp |
| `NT AUTHORITY\SYSTEM` | `svchost.exe` with Reason mentioning **Windows Update** | **Guest OS auto-update reboot** | Cross-check WindowsUpdateClient%4Operational.evtx for `KB*` install around the same time |
| Domain user (e.g. `CONTOSO\admin`) | `Explorer.exe` (Server 2012 R2) or `RuntimeBroker.exe` (Server 2016/2019/2022) or `winlogon.exe` (Server 2008 R2) | **Customer / admin clicked Restart in the UI** (Start Menu / Ctrl+Alt+Del) | Cross-check Security.evtx Event 4624 (logon) right before the 1074 — same user, RDP logon type 10 |
| Domain user | `cmd.exe` / `powershell.exe` | **Admin ran `shutdown /r` from a console** | Cross-check `cmd.exe` history if PowerShell logging on; otherwise can only confirm via user interview |
| `NT AUTHORITY\SYSTEM` | `wmiprvse.exe` | **Remote WMI call** (DSC extension, monitoring agent, SCOM, Ansible/Chef) | Cross-check WaAppAgent.log for DSC handler activity; check Microsoft-Windows-DSC%4Operational Event 4102 |
| Any | Any | `<computer>` field name ≠ this VM's name | **Remote shutdown from another machine** via `shutdown /m \\target` or remote WMI | Investigate the source computer; the local VM is the **victim**, not the actor |

> 📌 **OS version matters**: the `Process` field for a UI-initiated restart shifts across Windows Server versions — 2008 R2 = `winlogon.exe`, 2012 R2 = `Explorer.exe`, 2016+ = `RuntimeBroker.exe`. Don't say "it wasn't a user restart" just because you didn't see `Explorer.exe` on a 2019 VM.

> 📌 **Reason Codes are NOT cross-version stable**: codes like `0x500ff`, `0x80070015`, `0x80020003` carry different meanings on 2008 R2 vs 2016+. Always look up the reason code for the **specific** OS version — never hardcode an interpretation.

### Platform-side BSOD detection (when guest dump is absent)

Sometimes the customer reports a reboot but the IID has no `MEMORY.DMP` (dump disabled, dump file deleted before collection, hard hang with no dump generation). You can still confirm a BSOD happened from the **host side** via Kusto:

| Platform signal | What it confirms |
|---|---|
| **Hyper-V Worker Event 18590** with `Description contains "0x80"` | Guest reported `ErrorCode0: 0x80` = NMI-triggered bugcheck (Serial Console "Send NMI" or driver-injected NMI). |
| **Hyper-V Management** events: "Injecting a non-maskable interrupt" timestamp ≈ Event 18590 | Platform-injected NMI to force a dump on a hung VM. |
| **ASI → EEE RDOS** → `ContainerOsStateUnhealthy` + `HeartBeatStateLostCommunication` annotated `VirtualMachineCrashed` | Container layer detected the guest crashed even with no agent heartbeat. |

Sample Kusto (delegate to `vm-kusto-query` skill to actually run):

```kql
cluster("azcore.centralus.kusto.windows.net").database("Fa").WindowsEventTable
| where EventId == "18590" and Description contains "0x80"
| where TIMESTAMP between (datetime(<start>) .. datetime(<end>))
```

### Crash dump collection — compliance rules

If a BSOD occurred and `C:\Windows\MEMORY.DMP` is missing or unhelpful, you may need a fresh dump. Before requesting one:

1. **Customer must approve dump collection.** Check DFM for the consent flag. If `false`, ask the customer for written approval (email) and save it as evidence in the case — do not proceed without it.
2. **Always request Kernel dump first.** Only escalate to Complete dump (which captures all RAM including user-mode and may contain PII) if Kernel dump turns out to be insufficient. Minimizes downtime + data-exposure surface.
3. **Hand off to Watson** (`https://portal.watson.azure.com/dump?`) for actual analysis — vm-log-analyzer is not the dump-analysis tool. We identify *that* a dump is needed, not parse it.

### Reading wall-clock times: the time-zone trap

> **Event Viewer always displays the local timezone of the machine viewing the log — not UTC, not the customer's local timezone, not the Azure region's timezone.**

When the customer says "the VM rebooted at 14:00" — always clarify:
- Is that customer's local time, VM's configured timezone, or UTC?
- The IID `.evtx` you're reading is rendered in whatever timezone your analyst box is set to.
- One robust fix: convert all evidence to UTC before correlating across IID, Kusto, ASI, and customer statements.

### Highest-signal evidence checklist (do these in order)

1. **`system_errors.txt`** (if engineer pre-analysis exists) or `Get-WinEvent -Path System.evtx -FilterHashtable @{Id=41,1074,6008,6005,6006,1001}` — get the restart pair with one query.
2. **Match Event 41 / 6008 timestamps** — they should be ~10 seconds apart. If 1074 also exists at the same timestamp → planned reboot, stop digging for a dump. If 1074 absent → unplanned, continue.
3. **Decode Event 1074** using the decision tree above. Cross-check ASI Resource Events for the same timestamp.
4. **If unplanned**: check Event 1001 for dump path → grab `C:\Windows\MEMORY.DMP` if present and consent obtained.
5. **If unplanned + no dump**: pivot to Kusto (Hyper-V Worker Event 18590) + ASI EEE RDOS.

---

## DND

> Covers: Windows Update failure, CBS / component store corruption, activation failure, driver installation failure, sysprep errors

### Priority Log Read

| Priority | Log / file | What to look for |
|---|---|---|
| 1 | Setup event log | `*_evt_Setup.txt` — WUSA errors, Servicing Events 1013/1014/1015 |
| 2 | CBS.log | `logs\CBS\CBS.log` — HRESULT errors, "Failed to" entries |
| 3 | CbsPersist_*.log | `logs\CBS\CbsPersist_*.log` — historical CBS sessions (large; filter by date range) |
| 4 | WU ETL converted log | `*_WindowsUpdateETL_Converted.log` — update title, error code, DeploymentAction |
| 5 | WU reporting log | `*_WindowsUpdate_ReportingEvents.log` — final install status per KB |
| 6 | DISM log | `logs\DISM\dism.log` |
| 7 | DISM CheckHealth | `*_dism_CheckHealth.txt` |
| 8 | xray ISSUES-FOUND | `xray_ISSUES-FOUND_*.txt` — read first (pre-analysis output) |
| 9 | Summary | `*__SUMMARY.TXT` — OS version, recent reboot, last installed updates |

### Key Event IDs

| EventID | Source | Meaning |
|---|---|---|
| 1 | Microsoft-Windows-Servicing | Package install started |
| 2 | Microsoft-Windows-Servicing | Package install completed |
| 1013 | Microsoft-Windows-Servicing | CBS corruption scan started |
| 1014 | Microsoft-Windows-Servicing | CBS corruption scan completed — compare "repaired" vs "found" counts |
| 1015 | Microsoft-Windows-Servicing | **Warning: corruption not repaired** — blocks subsequent servicing |
| 19 | WindowsUpdateClient | Update install succeeded |
| 20 | WindowsUpdateClient | Update install failed |

### Common Error Codes

| HRESULT (decimal) | Hex | Meaning |
|---|---|---|
| 2148468792 | `0x800F0838` | CBS_E_MANIFEST_INVALID — CBS corruption |
| 2147942405 | `0x80070005` | Access denied (TrustedInstaller) |
| 2147942402 | `0x80070002` | File not found |
| 2149842956 | `0x8024200D` | WU database corruption |
| 2147954690 | `0x80072EE2` | Network timeout, cannot reach WU |
| 2148532254 | `0x800F09DE` | Pending reboot blocks servicing |
| 2148007946 | `0x800F080C` | CBS_E_UNKNOWN_UPDATE — component unrecognized |

### Decision Tree

```
DND issue
├── Windows Update KB install failed
│   ├── 0x800F0838 → CBS corruption (see CBS branch below)
│   ├── 0x80070005 → TrustedInstaller not running or permissions lost
│   │   Fix: sc config TrustedInstaller start= auto && net start TrustedInstaller
│   ├── 0x8024200D / 0x80242006 → WU database corruption
│   │   Fix: reset the SoftwareDistribution folder
│   ├── 0x80072EE2 / 0x8024402C → network timeout
│   │   Check: proxy or firewall blocking WU endpoints
│   ├── 0x80070002 → source files missing
│   │   Fix: run SFC /scannow first
│   └── 0x800F09DE / 0x800F0922 → reboot required
│       Fix: reboot and retry
│
├── CBS / component store corruption
│   ├── Event 1015 (corruption not repaired)
│   │   Step 1: DISM /Online /Cleanup-Image /RestoreHealth
│   │   Step 2: DISM /Source:WIM /LimitAccess (if step 1 fails)
│   │   Step 3: SFC /scannow
│   │   Step 4 (last resort): in-place repair upgrade Setup.exe /auto upgrade
│   └── CBS.log repeatedly shows 0x800F080C
│       → Foundation Package unrecognized; rebuild the component store
│
├── Activation failure
│   ├── 0x8007232B → KMS host unreachable (DNS SRV record cannot resolve)
│   ├── 0xC004F074 → KMS host reachable but cannot connect (check port 1688)
│   └── 0xC004C008 → MAK key exhausted (contact the licensing team)
│
├── Driver install failure
│   ├── Check setupapi.dev.log for "error" entries near the install timestamp
│   ├── Event 219 (driver load failure), Event 7026 (driver not started at boot)
│   └── Fix: DISM offline driver injection
│
└── Sysprep failure
    ├── Check %WINDIR%\System32\Sysprep\Panther\setupact.log + setuperr.log
    ├── Common cause: Store apps not ready for generalization
    └── Fix: remove the problem app package before sysprep
```

### Repair Commands

```powershell
# CBS / component store repair
DISM /Online /Cleanup-Image /RestoreHealth
DISM /Online /Cleanup-Image /RestoreHealth /Source:D:\sources\install.wim /LimitAccess
DISM /Online /Cleanup-Image /ScanHealth
sfc /scannow

# Windows Update reset
net stop wuauserv; net stop cryptSvc; net stop bits; net stop msiserver
Rename-Item C:\Windows\SoftwareDistribution SoftwareDistribution.old
Rename-Item C:\Windows\System32\catroot2 catroot2.old
net start wuauserv; net start cryptSvc; net start bits; net start msiserver

# Activation diagnostics and repair
slmgr /dli
slmgr /xpr
slmgr /skms <kmshost>:1688
slmgr /ato
Test-NetConnection -ComputerName <kmshost> -Port 1688
# KMS SRV record verification
Resolve-DnsName -Name _vlmcs._tcp.<domain> -Type SRV

# TrustedInstaller repair
sc config TrustedInstaller start= auto
net start TrustedInstaller

# In-place repair upgrade (last resort; mount ISO as D:)
D:\setup.exe /auto upgrade /DynamicUpdate disable

# Offline driver injection (for driver install failures)
dism /online /add-driver /driver:<driver-path> /recurse
```

---

## Directory Services

> Covers: AD domain join failure, Netlogon secure channel break, w32tm time-sync issues

### Priority Log Read

| Priority | Log / file | IID/TSS package path |
|---|---|---|
| 1 | Netlogon.log | `logs\NetSetup\netlogon.log` or `C:\Windows\debug\netlogon.log` |
| 2 | System event log | `*_evt_System.txt` — EventID 5719, 3210, 1129, 29, 36, 47 |
| 3 | DSRegCmd output | `*_DSregCmd.txt` — device / domain join state |
| 4 | SystemInfo | `*_SystemInfo.txt` — confirm domain membership |
| 5 | Network info | `*_NETWORK_TCPIP_info.txt` — DNS server settings (critical) |
| 6 | DNS client cache | `*_NETWORK_DnsClient_ipconfig-displaydns.txt` |
| 7 | MiscInfo | `*_MiscInfo.txt` — netlogon service state |

### Key Event IDs

| EventID | Source | Meaning |
|---|---|---|
| 5719 | NETLOGON | Cannot establish a secure channel to a DC |
| 3210 | NETLOGON | Authentication with the DC failed |
| 5722 | NETLOGON | Computer account password mismatch on the DC side |
| 1129 | GroupPolicy | Group Policy processing failed — DC unreachable |
| 4 | Kerberos-Key-Distribution-Center | KDC cannot find an account key |
| 29 | W32Time | NTP source unreachable |
| 36 | W32Time | Time sync has not succeeded for X seconds |
| 37 | W32Time | Time offset exceeds the warning threshold |
| 35 | W32Time | A new time source was selected |
| 47 | W32Time | Configured NTP peer returned no valid response |

### Netlogon.log Key Patterns

```
# DC discovery failure (DNS issue)
[CRITICAL] [domain] DsGetDcName: NO entry found: Status = 0x54B (ERROR_NO_SUCH_DOMAIN)

# Secure channel password mismatch
[LOGON] [domain] NO_TRUST_SAM_ACCOUNT

# Authentication failure
[LOGON] [domain] 0xC000006D  (STATUS_LOGON_FAILURE)

# DC discovery succeeded (baseline reference)
[MISC] DsGetDcName called: flags: 0x40001010 domain: <name> -> found DC: \\<DC-name>
```

### Domain-Join Failure Decision Tree

```
Domain join failed
├── "The specified domain does not exist or cannot be contacted"
│   ├── DNS cannot resolve the domain name
│   │   Check: DNS server in TCPIP_info.txt must be the DC IP, not 8.8.8.8
│   │   Fix: point DNS to the domain controller IP
│   └── Cannot reach the DC over the network (ports 389/88/445/3268 blocked)
│       Fix: update NSG / firewall rules
│
├── "Account already exists" / NERR_SetupAlreadyJoined (0x8b)
│   ├── A stale computer account with a mismatching password exists in AD
│   │   Fix 1: delete the computer account in ADUC and re-join
│   │   Fix 2: netdom resetpwd /server:<DC> /ud:<admin> /pd:*
│   └── Check Netlogon.log: NO_TRUST_SAM_ACCOUNT or WRONG_PASSWORD
│
├── "Access denied" / 0x5
│   ├── The joining account lacks OU-join permission
│   └── User reached the 10-machine join quota (domain default policy)
│       Fix: delegate "Create Computer Objects" on the OU, or use an admin account
│
├── 0x6BF / RPC_S_UNKNOWN_IF
│   ├── RPC service not running on the DC
│   └── SMB (port 445) or RPC (port 135) blocked by firewall
│       Fix: update NSG / firewall to allow 135 and 445
│
└── Join succeeded but authentication fails
    ├── Event 5719: secure channel broken
    │   Fix 1: nltest /sc_reset:<domain>
    │   Fix 2: netdom resetpwd /server:<DC> /ud:<domain>\<admin> /pd:*
    └── Time offset > 5 minutes (Kerberos hard limit)
        → Fix Windows Time sync first (see §w32tm below)
```

### w32tm Time-Sync Decision Tree

```
Windows Time out of sync
├── w32tm /query /status shows "Last Successful Sync Time: never" or a stale timestamp
│   ├── W32Time service not running → net start w32time
│   └── NTP source unreachable (UDP 123 blocked by firewall)
│       Check: Test-NetConnection <NTP-server> -Port 123
│
├── Event 29: NTP source unreachable
│   Fix: w32tm /config /manualpeerlist:"time.windows.com,0x8" /syncfromflags:manual /update
│
├── Event 47: configured NTP peer no response
│   ├── NTP server address misconfigured
│   └── NSG / firewall blocking UDP 123
│
├── Large time offset (causes Kerberos failures — 5-minute hard limit)
│   ├── Force immediate sync: w32tm /resync /force
│   └── If offset > 5 minutes, set the time manually first: Set-Date -Date "<correct UTC time>"
│
└── Domain-member VM not syncing from the DC
    ├── Expected hierarchy: domain member → DC → PDC Emulator → external NTP
    ├── Check: w32tm /query /source → should show the DC name, not "Local CMOS Clock"
    └── Fix: w32tm /config /syncfromflags:domhier /update && w32tm /resync /rediscover
```

### Repair Commands

```powershell
# Diagnostics
nltest /dsgetdc:<domain.com>
nltest /sc_verify:<domain.com>

# Test the required ports to the DC
Test-NetConnection -ComputerName <DC-IP> -Port 389   # LDAP
Test-NetConnection -ComputerName <DC-IP> -Port 88    # Kerberos
Test-NetConnection -ComputerName <DC-IP> -Port 445   # SMB
Test-NetConnection -ComputerName <DC-IP> -Port 3268  # Global Catalog
Test-NetConnection -ComputerName <DC-IP> -Port 135   # RPC

# Test SRV DNS records
Resolve-DnsName -Name _ldap._tcp.dc._msdcs.<domain.com> -Type SRV
Resolve-DnsName -Name _kerberos._tcp.dc._msdcs.<domain.com> -Type SRV

# Reset secure channel (no reboot required)
nltest /sc_reset:<domain.com>
netdom resetpwd /server:<DC-name> /ud:<domain>\<admin> /pd:*

# Re-join the domain (reboot required)
$cred = Get-Credential
Remove-Computer -UnjoinDomainCredential $cred -Force
Add-Computer -DomainName <domain.com> -Credential $cred -OUPath "OU=Servers,DC=domain,DC=com" -Force -Restart

# w32tm diagnostics and repair
w32tm /query /status
w32tm /query /source
w32tm /query /configuration
w32tm /query /peers
w32tm /stripchart /computer:time.windows.com /samples:3 /dataonly
w32tm /resync /force
w32tm /config /manualpeerlist:"time.windows.com,0x8" /syncfromflags:manual /update
w32tm /config /syncfromflags:domhier /update && w32tm /resync /rediscover

# Full W32Time reset (when the service is broken)
net stop w32time
w32tm /unregister
w32tm /register
net start w32time
```

### Azure VM Time Sync Notes

- Azure provides time to VMs via **Hyper-V Time Synchronization** (`VMICTimeProvider`) from the host — highest priority when running on an Azure VM
- **Domain-member VMs**: should sync through the DC hierarchy (domain member → DC → PDC Emulator → external NTP); **do not** point a single domain member directly to `time.windows.com`
- **Standalone VMs** (not domain-joined): use `time.windows.com` or rely on the Hyper-V time provider
- The NSG must allow **outbound UDP 123**, otherwise the VM cannot reach external NTP sources

---

## Performance

> See [references/windows-performance.md](windows-performance.md) for the full Performance scenario: Event IDs (2004/1001/333/153/129/11/51/2019/2020/7031/7034), PowerShell collection commands, PerfInsights workflow, decision tree, cross-skill references, and Wiki TSGs.
