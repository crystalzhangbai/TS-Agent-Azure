---
description: KQL queries for NDPA (NetDataPathAgent) SoC PF Update blackout/brownout investigation on OverLake nodes. Covers SoC PilotFish firmware upgrade detection, FPGA blackout duration measurement from LinuxOverlakeSystemd, NicAgent BrownoutClient/ManaInstaller analysis, AzCore cluster mapping, and Air NDPA event streams.
---

# NDPA SoC PF Update — Blackout / Brownout Investigation

> Source: Learned from case investigation + Azure Networking B01 Dashboard + TSG: Host Networking Updates (aka.ms/AnpNmagentTsg)
> Scope: OverLake (SoC) nodes undergoing netdatapathagent FPGA/firmware upgrades

## When to Use

Use this reference when:
- RDOS Start Hub shows a **SoC PF Update** event (PilotFish update on SoC)
- Customer reports brief connectivity loss (~1-8 seconds) on an OverLake node
- You need to measure exact **blackout/brownout duration** during NDPA servicing
- VFP drop metrics are clean but network dips are observed in Shoebox metrics
- You need to distinguish between **SoC/FPGA blackout** vs **NicAgent NIC driver brownout**

## Key Concepts

### Two Independent Blackout Mechanisms

| Mechanism | Agent | Log Source | Typical Trigger |
|-----------|-------|-----------|-----------------|
| **SoC/FPGA Blackout** | netdatapathagent.exe | `LinuxOverlakeSystemd` (OvlProd) | SoC PF Update — FPGA firmware cutover |
| **NIC Driver Brownout** | NicAgent (BrownoutClient/ManaInstaller) | `NicAgentLogs` (NicAgent db) | Host-side MANA/Mellanox NIC driver install/upgrade |

These are independent — one can fire without the other.

### Expected Blackout Durations (per TSG)

| Scenario | Impact Type | Typical Duration |
|----------|-------------|-----------------|
| SoC firmware update (FPGA) | Blackout | <8 seconds (network freeze) |
| Live migration | Brownout/Blackout | ~12s outlier |
| SoC crash/reboot | Blackout | <30s transient |
| Queue overflow | Brownout | Variable |
| Host networking transition | Brownout | Variable |

## Investigation Steps

### Step 0: Confirm Node is OverLake

Check for a non-zero SocNodeId in LogContainerSnapshot or the RDOS Start Hub dashboard.

```kql
cluster('azurecm').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= datetime(START_TIME) and PreciseTimeStamp <= datetime(END_TIME)
| where containerId == "CONTAINER_ID"
| top 1 by PreciseTimeStamp desc
| project containerId, nodeId, Tenant, roleInstanceName
```

> **Important:** OverLake nodes have a **SoC NodeId** (different from the host NodeId). 
> The SoC machine name follows the pattern `<cluster_prefix>SOC` (e.g., `SE1AA1060719023SOC`).

### Step 1: Find the AzCore Regional Cluster

The brownout/blackout data lives on a **regional** azcore cluster, not the central one. Use this query to discover which regional cluster serves your node:

```kql
// Find AzCore cluster mapping for a node
cluster('azcore.centralus.kusto.windows.net').database('Fc').TMMgmtNodeEventsEtwTable
| where PreciseTimeStamp >= datetime(START_TIME) and PreciseTimeStamp <= datetime(END_TIME)
| where Tenant == "CLUSTER_NAME"
| where NodeId == "HOST_NODE_ID"
| project AzCoreCluster
| distinct AzCoreCluster
```

**Result example:** `https://azcore8.japaneast.kusto.windows.net`

> **Known mappings (partial):**
> - Korea Central (SE1PrdApp22) → `azcore8.japaneast.kusto.windows.net`
> - Add more as discovered...

### Step 2: Query SoC Blackout from LinuxOverlakeSystemd

This is the **authoritative source** for exact blackout duration during NDPA/FPGA upgrades:

```kql
// SoC Blackout — exact duration from netdatapathagent.exe logs
cluster('AZCORE_REGIONAL.kusto.windows.net').database('OvlProd').LinuxOverlakeSystemd
| where PreciseTimeStamp >= datetime(START_TIME) and PreciseTimeStamp <= datetime(END_TIME)
| where MachineName == "SOC_MACHINE_NAME"  // e.g., "SE1AA1060719023SOC"
| where MESSAGE has_any ("brownout", "blackout", "Brownout", "Blackout")
| project PreciseTimeStamp, NodeId, MachineName, SYSLOG_IDENTIFIER, MESSAGE
| order by PreciseTimeStamp asc
```

**Expected output messages:**
- `"Blackout Time for components : FPGA = <ms>"` — per-component blackout
- `"Total Blackout Time for NetDatapathAgent Servicing : <ms>"` — total blackout across all components
- If total = 0 in a subsequent log, it means that phase had no additional blackout

**Key columns in LinuxOverlakeSystemd:**
| Column | Description |
|--------|-------------|
| `TIMESTAMP` | Event timestamp |
| `PreciseTimeStamp` | High-precision timestamp |
| `NodeId` | SoC NodeId (NOT host NodeId) |
| `MachineName` | SoC machine name (e.g., SE1AA1060719023SOC) |
| `SYSLOG_IDENTIFIER` | Process name (look for `netdatapathagent.exe`) |
| `MESSAGE` | Full log message text |
| `Cluster` | AzureCM cluster name |
| `MachineFunction` | Machine role/function |

### Step 3: Query NicAgent Brownout/Blackout

Check if the NicAgent-level brownout path was also triggered (independent from SoC blackout):

```kql
// NicAgent Brownout/Blackout events
cluster('azcore.centralus.kusto.windows.net').database('NicAgent').NicAgentLogs
| where TIMESTAMP >= datetime(START_TIME) and TIMESTAMP <= datetime(END_TIME)
| where NodeId == "HOST_NODE_ID"
| where Function in (
    "BrownoutClient::StartBrownout", 
    "BrownoutClient::StopBrownout", 
    "ManaInstaller::EnterBlackout", 
    "ManaInstaller::HostDriverServicingEnterBlackout"
)
| project TIMESTAMP, NodeId, Function, Message, Cluster
| order by TIMESTAMP asc
```

**To calculate brownout duration:**

```kql
// NicAgent brownout duration calculation
cluster('azcore.centralus.kusto.windows.net').database('NicAgent').NicAgentLogs
| where TIMESTAMP >= datetime(START_TIME) and TIMESTAMP <= datetime(END_TIME)
| where NodeId == "HOST_NODE_ID"
| where Function in (
    "BrownoutClient::StartBrownout", 
    "BrownoutClient::StopBrownout", 
    "ManaInstaller::EnterBlackout", 
    "ManaInstaller::HostDriverServicingEnterBlackout"
)
| extend EventType = case(
    Function == "BrownoutClient::StartBrownout", "BrownoutStart",
    Function == "BrownoutClient::StopBrownout", "BrownoutStop",
    Function has "Blackout", "Blackout",
    "Other"
)
| summarize 
    BrownoutStart = minif(TIMESTAMP, EventType == "BrownoutStart"),
    BrownoutStop = minif(TIMESTAMP, EventType == "BrownoutStop"),
    BlackoutCount = countif(EventType == "Blackout")
    by Cluster, NodeId
| where isnotnull(BrownoutStart) and isnotnull(BrownoutStop)
| extend BrownoutDuration = BrownoutStop - BrownoutStart
| project Cluster, NodeId, BrownoutStart, BrownoutStop, BrownoutDuration, BlackoutCount
```

### Step 4: Check Air NDPA Event Streams (Optional — May Have Ingestion Delay)

These tables provide structured per-component breakdowns but may lag behind real-time:

```kql
// Node-level SoC NDPA upgrade event (use SoC NodeId, NOT host NodeId)
cluster('vmainsight').database('Air')._EventStream_SoC_NDPAServiceUpgrade
| where EventTime >= datetime(START_TIME) and EventTime <= datetime(END_TIME)
| where NodeId == "SOC_NODE_ID"  // or Cluster == "CLUSTER_NAME"
| project EventTime, NodeId, SocUpgradeStartTime, SocUpgradeEndTime, 
    SocBlackOutStartTime, SocBlackOutEndTime, SocBlackOutDurationInSeconds,
    SocBlackOutDurationInSecondsFromNDPA,
    SocBlackOutDurationInSecondsFromVFPComponents,
    SocBlackOutDurationInSecondsFromGFTComponents,
    SocBlackOutDurationInSecondsFromBackplaneComponents,
    SocBlackOutDurationInSecondsFromFPGAComponents,
    SocGreyOutDurationInSeconds,
    InstalledVersion, PackagedVersion, VMCountOnNode, TotalUpgradeDurationSeconds
```

```kql
// Container-level NDPA blackout (per-VM impact)
cluster('vmainsight').database('Air')._EventStream_Container_NDPASocAgentServicing_WithMetadata
| where EventTime >= datetime(START_TIME) and EventTime <= datetime(END_TIME)
| where containerId == "CONTAINER_ID"
| project EventTime, containerId, SocBlackOutDurationInSeconds, 
    SocBlackOutDurationInSecondsFromNDPA, SocGreyOutDurationInSeconds,
    TotalUpgradeDurationSeconds, InstalledVersion, PackagedVersion
```

> **Note:** If these tables return empty, fall back to `LinuxOverlakeSystemd` (Step 2) which is the authoritative real-time source. The Air tables are processed asynchronously and may have hours of ingestion delay.

### Step 5: Corroborate with Shoebox Metrics (Network Impact)

Use MDM Shoebox to measure customer-visible impact:

```
MDM Account: AzComputeShoebox<REGION_CODE> (e.g., AzComputeShoeboxKRC for Korea Central)
MDM Namespace: Shoebox
Dimension: ResourceId = <virtualMachineUniqueId>
Key metrics: "Inbound Flows", "Network In Total", "Network Out Total", "Percentage CPU"
```

Compare the metric dip window with the blackout timestamp from Step 2. A 3-second FPGA blackout typically manifests as a 1-2 minute dip at 1-minute MDM resolution.

## Interpretation Guide

### Reading the Blackout Log Messages

| Log Message Pattern | Meaning |
|---|---|
| `Blackout Time for components : FPGA = <N>` | FPGA contributed N milliseconds of blackout |
| `Blackout Time for components : VFP = <N>` | VFP contributed N milliseconds |
| `Blackout Time for components : FPGA = <N>, VFP = <M>` | Multiple components contributed |
| `Total Blackout Time for NetDatapathAgent Servicing : <N>` | Sum of all component blackouts for this servicing phase |
| `Total Blackout Time for NetDatapathAgent Servicing : 0` | Subsequent phase completed with no blackout |

### Common Pitfalls

1. **Host NodeId vs SoC NodeId** — The SoC has its own NodeId. When querying `LinuxOverlakeSystemd` or Air NDPA tables, use the **SoC NodeId** or **MachineName** (e.g., `SE1AA1060719023SOC`), not the host NodeId.

2. **Air tables empty** — `_EventStream_SoC_NDPAServiceUpgrade` may have ingestion delay of hours. Always use `LinuxOverlakeSystemd` as the authoritative source.

3. **AzCore cluster is regional** — Don't query `azcore.centralus` for OvlProd data. First discover the correct regional cluster via `TMMgmtNodeEventsEtwTable.AzCoreCluster`.

4. **NicAgent vs SoC paths are independent** — A SoC FPGA upgrade does NOT trigger NicAgent BrownoutClient. They serve different update scenarios.

5. **Shoebox resolution is 1 minute** — A 3-second blackout appears as a dip in one 1-minute bucket. The actual blackout is much shorter than the metric dip suggests.

## TSG References

- **[TSG: Host Networking Updates](https://dev.azure.com/Supportability/AzureNetworking/_wiki/wikis/Wiki/337081/TSG-Host-Networking-Updates)** (`aka.ms/AnpNmagentTsg`)
- RDOS Start Hub → SoC PF Update section (visible in the OverLake/PilotFish timeline)
- **[Mark Node Unallocatable Mitigations — High Memory Pressure](https://eng.ms/docs/cloud-ai-platform/azure-core/azure-compute/general-purpose-host-arunki/host-networking/datapath-documentation/pmem/mitigations/highmemorypressure)**

---

## PMEM High Memory Pressure → Unallocatable (OverLake Nodes Only)

> **Applies to:** OverLake-enabled VMs only (nodes with a SoC NodeId).  
> **Signature:** Node marked Unallocatable (FaultCode 10036) with FaultReason "Manually injected fault - high memory usage", followed by Live Migration (AllowLM=true) typically 1-24 hours later.  
> **Source:** [eng.ms — Mark Node Unallocatable Mitigations](https://eng.ms/docs/cloud-ai-platform/azure-core/azure-compute/general-purpose-host-arunki/host-networking/datapath-documentation/pmem/mitigations/highmemorypressure)

### When to Use

Use this section when investigating customer Live Migration on an OverLake node where:
- RDOS Start Hub shows **Unallocatable** event a few hours before the LM
- No SoC PF Update / NDPA servicing is visible
- No NicAgent brownout is visible
- The node has high PMEM heap usage (>85%)

### Mechanism

The AccelNet/OaaS automation monitors PMEM heap usage on all OverLake SoC nodes and proactively fences nodes before they hit the critical 95% failure threshold:

| Action | Threshold | Automation |
|--------|-----------|-----------|
| **Mark Unallocatable** | PMEM heap > **85%** | FaultCode 10036, AllowLM=true |
| **Restore to Rotation** | PMEM heap < **45%** | Checked every 30 minutes |

### OaaS Fault Injection Payload

```
Oaas(pfgold\orchestrationpolicy\Oaas\VirtualEnvironments\AccelNet\MarkNodeUnallocatable) {
  "FaultCode": "10036",
  "FabricOperation": "ForceNodeState",
  "FaultScope": "SM",
  "FaultReason": "Manually injected fault - high memory usage",
  "OnEmptyNode": "PushToHumanInvestigate",
  "OnUnexpectedReboot": "PushToHumanInvestigate",
  "OnTimeout": "PushToHumanInvestigate:3d",
  "AllowLM": "true"
}
```

### PmemMetricsDashboard URL

Geneva portal dashboard for live PMEM MDM metrics. Use this URL template — fill `<ACCOUNT>`, `<CLUSTER>`, `<NODEID>`, and epoch-ms timestamps. Note: when using this URL in scripts/tools, URL-encode the `overrides` JSON (browsers typically do this automatically).

```
https://portal.microsoftgeneva.com/dashboard/VfpMDM/PmemMetricsDashboard/PmemMetricsDashboard?overrides=[{"query":"//dataSources","key":"account","replacement":"<ACCOUNT>"},{"query":"//*[id='Region']","key":"value","replacement":""},{"query":"//*[id='Cluster']","key":"value","replacement":"<CLUSTER>"},{"query":"//*[id='NodeId']","key":"value","replacement":"<NODEID>"},{"query":"//*[id='SoCId']","key":"value","replacement":""},{"query":"//*[id='HeapId']","key":"value","replacement":""},{"query":"//*[id='HeapLevel']","key":"value","replacement":""},{"query":"//*[id='BuildVersion']","key":"value","replacement":""}]&globalStartTime=<EPOCH_MS_START>&globalEndTime=<EPOCH_MS_END>&pinGlobalTimeRange=true
```

**Override parameters:**

| Parameter | Override query | Notes |
|---|---|---|
| Account | `{"query":"//dataSources","key":"account","replacement":"<VfpMdmXX>"}` | e.g. `VfpMdmSN`, resolve via `MdmVfpVnetAccountMaps()` |
| Cluster | `{"query":"//*[id='Cluster']","key":"value","replacement":"<CLUSTER>"}` | e.g. `SAT13PrdApp46` |
| NodeId | `{"query":"//*[id='NodeId']","key":"value","replacement":"<NODEID>"}` | host NodeId GUID |
| SoCId / HeapId / HeapLevel / BuildVersion | `{"query":"//*[id='...']","key":"value","replacement":""}` | leave empty unless known |
| globalStartTime / globalEndTime | query params | epoch milliseconds (UTC) |
| pinGlobalTimeRange | `true` | required to lock the time range |

**PowerShell to build URL:**

```pwsh
$account = "VfpMdmSN"; $cluster = "SAT13PrdApp46"; $nodeId = "<NODEID>"
$startMs = [long]([datetime]"2026-06-12T08:00:00Z" - [datetime]"1970-01-01T00:00:00Z").TotalMilliseconds
$endMs   = [long]([datetime]"2026-06-12T12:00:00Z" - [datetime]"1970-01-01T00:00:00Z").TotalMilliseconds
$ov = '[{"query":"//dataSources","key":"account","replacement":"' + $account + '"},{"query":"//*[id=''Region'']","key":"value","replacement":""},{"query":"//*[id=''Cluster'']","key":"value","replacement":"' + $cluster + '"},{"query":"//*[id=''NodeId'']","key":"value","replacement":"' + $nodeId + '"},{"query":"//*[id=''SoCId'']","key":"value","replacement":""},{"query":"//*[id=''HeapId'']","key":"value","replacement":""},{"query":"//*[id=''HeapLevel'']","key":"value","replacement":""},{"query":"//*[id=''BuildVersion'']","key":"value","replacement":""}]'
$url = "https://portal.microsoftgeneva.com/dashboard/VfpMDM/PmemMetricsDashboard/PmemMetricsDashboard?overrides=$([Uri]::EscapeDataString($ov))&globalStartTime=$startMs&globalEndTime=$endMs&pinGlobalTimeRange=true"
# PowerShell single-quoted strings: '' is the escape sequence for a literal ' — no Replace needed
$url
```

**Key PMEM MDM metrics** (via `mdm series <account> BACKPLANE-PMEM-MALLOC-METRICS <metric> --dims "Cluster=<C>;NodeId=<N>;NodeIP=<IP>" --sampling Average`):

| Metric | Description | Threshold |
|---|---|---|
| `pmem_percent_used` | PMEM heap usage % | >85% triggers Unallocatable |
| `pmem_percent_frag` | PMEM fragmentation % | — |
| `pmem_heap_stat_bytes_total_normal` | Total normal heap bytes | — |
| `pmem_heap_stat_bytes_used_normal` | Used normal heap bytes | — |
| `pmem_stat_alloc_fail` | Allocation failures | >0 is abnormal |
| `pmem_stat_alloc_ok` | Successful allocations | operational baseline |
| `pmem_heap_stat_heap_full_events` | Heap-full events | >0 is concerning |
| `pmem_heap_mitigation_triggered` | Mitigation triggers | >0 = high pressure event |

> Note: BACKPLANE-PMEM-METRICS (OOM_BackPlane, CrashCount, etc.) only have data when actual crash/OOM events occur. Empty = healthy.

### Investigation Steps — PMEM High Memory Unallocatable

#### Step 1: Confirm Node is OverLake and Find AzCore Cluster

```kql
// Find AzCore cluster mapping for the node
cluster('azcore.centralus.kusto.windows.net').database('Fc').TMMgmtNodeEventsEtwTable
| where PreciseTimeStamp >= datetime(START_TIME) and PreciseTimeStamp <= datetime(END_TIME)
| where Tenant == "CLUSTER_NAME"
| where NodeId == "HOST_NODE_ID"
| project AzCoreCluster
| distinct AzCoreCluster
```

#### Step 2: Query PMEM Heap Usage from LinuxOverlakeSystemd

```kql
// PMEM heap usage trend (5-min bins) — use SoC NodeId
cluster('AZCORE_REGIONAL.kusto.windows.net').database('OvlProd').LinuxOverlakeSystemd
| where PreciseTimeStamp between(datetime(START_TIME) .. datetime(END_TIME))
| where NodeId == "SOC_NODE_ID"
| where SYSLOG_IDENTIFIER == "netdatapathagent.exe"
| where MESSAGE has "m_pmem_heap_usage"
| parse MESSAGE with * "m_pmem_heap_usage (threshold: " threshold:double ") - [ " heapPct:double "," *
| where isnotnull(heapPct)
| summarize AvgHeap=avg(heapPct), MaxHeap=max(heapPct), MinHeap=min(heapPct) by bin(PreciseTimeStamp, 5m)
| order by PreciseTimeStamp asc
```

**Expected result:** Heap usage >85% around the Unallocatable fence time, dropping after LM completes.

#### Step 3: Check for Allocation Failures (Should Be Zero)

```kql
// Verify no actual allocation failures (proactive mitigation = no failures expected)
cluster('AZCORE_REGIONAL.kusto.windows.net').database('OvlProd').LinuxOverlakeSystemd
| where PreciseTimeStamp between(datetime(START_TIME) .. datetime(END_TIME))
| where NodeId == "SOC_NODE_ID"
| where SYSLOG_IDENTIFIER == "netdatapathagent.exe"
| where MESSAGE has "pmem_alloc_failures_count_cached"
| parse MESSAGE with * "pmem_alloc_failures_count_cached: " failCount:long "," *
| where failCount > 0
| project PreciseTimeStamp, MESSAGE
```

If this returns empty, the proactive mitigation worked as designed (node was fenced before failures occurred).

### Key Columns in LinuxOverlakeSystemd

| Column | Description |
|--------|-------------|
| `NodeId` | **SoC NodeId** (NOT host NodeId) — GUID format, lowercase |
| `MachineName` | SoC machine name (e.g., `SJC221062403029SOC`) |
| `SYSLOG_IDENTIFIER` | Process name — filter on `netdatapathagent.exe` for heap metrics |
| `MESSAGE` | Log text containing heap usage values |
| `Cluster` | AzureCM cluster name (e.g., `SJC22PrdApp02`) |

### Interpretation

- **Heap >85% + Unallocatable + AllowLM** = Expected OaaS behavior, no bug
- **Zero pmem_alloc_failures** = Proactive mitigation succeeded
- **Heap drops 10-20% after LM** = Confirms workload-driven pressure (VMs migrated off → less flow table pressure)
- **Recovery at <45%** = Node auto-restores to rotation (30-min polling)

### Public RCA Template (PMEM High Memory)

> The Microsoft Azure team has investigated the Live Migration event affecting your virtual machine. The physical host running your VM was experiencing **elevated persistent memory (PMEM) utilization** on the networking hardware. As a preventive measure, the platform proactively migrated your VM to a healthy host to avoid potential network connectivity degradation.
>
> This is an automated health management action designed to maintain network reliability. No data loss or extended downtime occurred — the VM was live-migrated with minimal interruption (typically sub-second to a few seconds of network freeze).
>
> To minimize impact from future platform maintenance events, we recommend deploying workloads across multiple VMs in an Availability Set or Virtual Machine Scale Set.

## Public RCA Template

> The Microsoft Azure team has finished investigating the issue with your virtual machine. We found the physical host running your VM was undergoing **regular maintenance of the host networking stack** which briefly impacted connectivity.
>
> Azure periodically performs updates to improve the reliability, performance, and security of the host infrastructure for virtual machines. We are continuously working on improving the platform, including reducing the impact duration of future updates.
>
> To enable customer applications to be notified of future host updates, we have invested in the [Scheduled Events](https://docs.microsoft.com/en-us/azure/virtual-machines/linux/scheduled-events) feature. To ensure high availability, please deploy on more than one VM configured with an Availability Set or Scale Set.
