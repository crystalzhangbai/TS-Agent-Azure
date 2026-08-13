---
description: Accelerated Connections (internal name Sirius) troubleshooting — AMD Pensando DSC-200 SDN-appliance architecture, vNIC AuxiliaryMode/AuxiliarySku enablement, control-plane and data-plane Geneva/Jarvis dashboards, SiriusMDS Dgrep log sources, validation steps, known error codes, and CRI pre-checks.
---

# Accelerated Connections (internal: Sirius) Troubleshooting Skill

> **Scope**: Accelerated Connections (Sirius) feature enablement, control-plane programming, data-plane packet flow, and appliance health for NVA / high-CPS workloads.
> **Customer-facing name**: Accelerated Connections (previously "Connections Per Second Optimization")
> **Internal name**: Sirius
> **CRI / IcM escalation queue**: **Cloudnet/Sirius**
> **Last Updated**: 2026-06-23

---

## 1. What is Accelerated Connections / Sirius

Accelerated Connections is an extension to Accelerated Networking that offloads a VM's vNIC flow processing onto a dedicated SDN appliance (Sirius) built on **AMD Pensando DSC-200 ("Elba") programmable cards**. It targets high Connections-Per-Second (CPS) and high Total-Active-Connection workloads (NVAs such as F5, Cisco, Checkpoint, Palo Alto).

- Without Accelerated Connections: ~50K CPS and ~1M total connections per VM (host SDN / VFP + FPGA).
- With Accelerated Connections: millions of CPS and far higher active-connection counts, sized per Auxiliary SKU (A1/A2/A4/A8).

Public docs: https://learn.microsoft.com/en-us/azure/networking/nva-accelerated-connections

### 1.1 Hardware
- A **Sirius appliance** = a pair of 3U servers (labeled S1 and S2), each with up to six programmable DSC-200 cards in PCIe slots.
- Each card has two 100Gbps QSFP+ connectors and 32GB DRAM.
- The internal card / device is referred to as the **Elba card**, identified by a **DeviceId**.

### 1.2 Enablement model — AuxiliaryMode
The feature is enabled at the **vNIC level** (not VM level) via two new NIC properties:

| Property | Values | Notes |
|----------|--------|-------|
| `auxiliaryMode` | `AcceleratedConnections` | Creates an ENI on the Sirius appliance, associated 1:1 with the vNIC |
| `auxiliarySku` | `A1`, `A2`, `A4`, `A8` | Performance tier; each ENI/AuxSku is billed separately |

Minimum VM size per SKU: A1/A2 → 4 vCPU, A4 → 8 vCPU, A8 → 32 vCPU. API version `2022-11-01` or later. Accelerated Networking must already be enabled on the vNIC.

Terraform (provider >= 3.74.0) example:
```hcl
resource "azurerm_network_interface" "nic" {
  accelerated_networking_enabled = true
  auxiliary_mode                 = "AcceleratedConnections"
  auxiliary_sku                  = "A1"
  # ...
}
```

> Enabling on an existing VM: add `auxiliaryMode`/`auxiliarySku` to the vNIC **while the VM is running**, then stop (deallocate) and start the VM as separate operations. Adding the config while the VM is stopped causes start failure. VMSS cannot be enabled in place — it must be redeployed.

### 1.3 High Availability & Scale
- **Active-Passive** with two (2) SDN appliances.
- **Overprovisioning**: the same ENI is handled by multiple appliance cards.
- **Pairing**: each card on appliance S1 has a "paired" card on S2 sharing the same VIP (look for a `Machine`/`PairedMachine` pair in dashboards).
- **Flow splitting**: TOR (or source node) splits traffic across the different VIPs of the overprovisioned cards.

### 1.4 Reduced Tuples (why it scales)
VFP/FPGA normally match flows on a 5-tuple (proto, srcIP, srcPort, dstIP, dstPort). Accelerated Connections uses a **reduced 3-tuple (proto, srcIP, dstIP)** so new source ports reuse the same offloaded flow (~99% match), dramatically increasing CPS. The VFP rule that proves an ENI is correctly programmed is **`APPLIANCE_DECAP_RULE`** (its source IP is the Elba card's BGP address).

---

## 2. Decision Tree (CRI pre-checks)

> At any step that fails, escalate to CRI/IcM queue **Cloudnet/Sirius** with the captured evidence.

```
Accelerated Connections issue reported
    |
    ├─ Step 1: Feature misconfiguration  (→ Section 6.1 / 6.2)
    │     ├─ vNIC has auxiliaryMode=AcceleratedConnections + auxiliarySku set?  (Portal JSON view / Properties / ASC ext)
    │     ├─ Subscription onboarded to Merlin? (fastPathForced == 1, NRP "Get KeyValue Item")
    │     └─ VM SKU (<= Dv5) + region supported?
    │
    ├─ Step 2: Identify Sirius placement  (→ Section 3)
    │     ├─ VM name + SubId → ContainerId (LogContainerSnapshot)
    │     ├─ ContainerId → Cluster prefixed "Sirius" + DeviceId (InterfaceProgramEndFiveMinuteTable; primary)
    │     └─ (fallback/TA) ContainerId/NodeId → DeviceId via SiriusMDS Log table
    │
    ├─ Step 3: Upper Control Plane / Appliance details  (→ Section 5.1 Health Manager)
    │     ├─ Container/Appliance details populated? (Health Manager dashboard, 2 appliances expected)
    │     └─ BGP enabled == true on BOTH paired entries? (ElbaCardHealthTable bgppa / SC Health and Counters)
    │
    ├─ Step 4: Host Appliance + programming events  (→ Section 4 + Section 5.1 Sirius Controller)
    │     ├─ Appliance Programming Events / GoalState from 2 different Clusters/Appliances?
    │     └─ ElbaCardHealth / ServicingInfo / GoalState OK?
    │
    └─ Step 5: Data plane packet check  (→ Section 5.2 + Section 4 failure tables)
          ├─ Packets received per Device > 0 AND Packets sent per Device > 0?
          └─ Critical / gRPC failures? (SiriusCriticalFailureTable / SiriusGrpcFailureTable)
```

---

## 3. Identify Sirius Placement (Kusto)

### Step 1 — VM name + Subscription → ContainerId
```kusto
let varName1 = "{VMName}";
cluster('AzureCM').database('AzureCM').LogContainerSnapshot
| where roleInstanceName contains varName1
| where subscriptionId == "{SubscriptionId}"
```

### Step 2 — ContainerId → confirm "Sirius" cluster + get VnetGuid / DeviceId
A cluster with the **`Sirius`** prefix confirms the AC-enabled vNIC landed on a Sirius appliance. A container is offloaded onto **two** Sirius appliance clusters (active-passive pairing/overprovisioning), each with its own `DeviceId` (Elba card). The non-Sirius row is the compute/host cluster.
```kusto
cluster('vnetkusto.northcentralus').database('veritas').InterfaceProgramEndFiveMinuteTable
| where TIMESTAMP > ago(7d)
| where ContainerId contains "{ContainerId}"
| summarize LastSeen=max(TIMESTAMP), Count=count() by Cluster, VnetGuid, NodeId, DeviceId
| order by LastSeen desc
```
> `VnetGuid` is the VNet ID. For dashboard `VNetId` parameters use it **braced and uppercase**, e.g. `{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}`. For Kusto filters (e.g. `SdnApplianceEvent.VnetId`) use the **same GUID without braces**.

> **If no `Sirius`-prefixed rows appear**: the VM is not placed on Sirius. Re-check (1) the vNIC has `auxiliaryMode=AcceleratedConnections` (Section 6.1), (2) the subscription is onboarded to Merlin (Section 6.2), and (3) the region has Sirius capacity (region query below). If all pass, escalate to **Cloudnet/Sirius**.

#### Token glossary (used in all queries and dashboard URLs)
| Token | Source | Format |
|-------|--------|--------|
| `{ContainerId}` | placement Step 1/2 | GUID |
| `{ComputeCluster}` | placement non-Sirius row `Cluster` | e.g. `PNQ23PrdApp30` |
| `{HostNodeId}` | placement non-Sirius row `NodeId` | physical host node (rarely used in dashboards) |
| `{SiriusCluster1/2}` | placement Sirius rows `Cluster` | **full** `Sirius...` name |
| `{ApplianceNodeId1/2}` | placement Sirius rows `NodeId` | **appliance** node (this is what data-plane dashboards want) |
| `{DeviceId1/2}` | placement Sirius rows `DeviceId` | Elba card GUID |
| `{VNetId}` | placement `VnetGuid` | **braced + UPPERCASE** |
| `{VNetGuidNoBraces}` | same GUID as `{VNetId}` | **no braces** (Kusto filters) |
| `{Machine}` / `{PairedMachine}` | `{SiriusCluster1}` / `{SiriusCluster2}` **minus the `Sirius` prefix** | Health Manager only |
| `{ApplianceGroupId}` | `SdnApplianceEvent.ApplianceGrpId` | GUID; or leave blank + pick from dropdown |
| `{RackMachine}` | Health Manager dropdown (appliance/rack host) | optional; leave blank + pick from dropdown |
| `{APRegion}` | ARM region display name | e.g. `west%20us` (URL-encoded) |
| `{MacAddress}` | vNIC MAC (optional) | leave blank if not scoping by MAC |
| `{StartEpochMs}` / `{EndEpochMs}` | time window | Unix epoch **milliseconds, UTC** |

> **NodeId disambiguation**: `NodeId` means the **compute/host** node in the non-Sirius placement row, but the **Sirius appliance** node in the two Sirius rows. Data-plane dashboards (`Per ENI`, `Per Card`, `Per Sirius Appliance`) expect the **appliance** NodeId(s).

#### Worked example (placeholders)
The query returns one **compute/host** row (no DeviceId) plus **two** `Sirius`-prefixed appliance rows (active-passive pairing), each with its own NodeId and DeviceId:

| Cluster | Role | NodeId | DeviceId (Elba) |
|---------|------|--------|-----------------|
| `{ComputeCluster}` | Compute / host | `{HostNodeId}` | — |
| `{SiriusCluster1}` | Sirius appliance | `{ApplianceNodeId1}` | `{DeviceId1}` |
| `{SiriusCluster2}` | Sirius appliance (paired) | `{ApplianceNodeId2}` | `{DeviceId2}` |

- **VNetId** (braced, uppercase): `{VNetId}`
- **MDM account**: `VNetMDM<Region>`
- **Combine both paired appliances in one URL** — the Per ENI tiles accept **comma-separated** values for `Cluster`, `DeviceId`, and `NodeId`, so a single link overlays both cards:
  [open](https://portal.microsoftgeneva.com/dashboard/SiriusMDS/Sirius%2520Dashboards%2520/DataPath%2520Level%2520View%2520/Per%2520ENI?overrides=[{"query":"//dataSources","key":"account","replacement":"VNetMDM<Region>"},{"query":"//*[id='Cluster']","key":"value","replacement":"{SiriusCluster1},{SiriusCluster2}"},{"query":"//*[id='DeviceId']","key":"value","replacement":"{DeviceId1},{DeviceId2}"},{"query":"//*[id='ContainerId']","key":"value","replacement":"{ContainerId}"},{"query":"//*[id='NodeId']","key":"value","replacement":"{ApplianceNodeId1},{ApplianceNodeId2}"},{"query":"//*[id='VNetId']","key":"value","replacement":"{VNetId}"}]&globalStartTime={StartEpochMs}&globalEndTime={EndEpochMs}&pinGlobalTimeRange=true)
- Single-appliance variants (one card each):
  - Per ENI (appliance 1): [open](https://portal.microsoftgeneva.com/dashboard/SiriusMDS/Sirius%2520Dashboards%2520/DataPath%2520Level%2520View%2520/Per%2520ENI?overrides=[{"query":"//dataSources","key":"account","replacement":"VNetMDM<Region>"},{"query":"//*[id='Cluster']","key":"value","replacement":"{SiriusCluster1}"},{"query":"//*[id='DeviceId']","key":"value","replacement":"{DeviceId1}"},{"query":"//*[id='ContainerId']","key":"value","replacement":"{ContainerId}"},{"query":"//*[id='NodeId']","key":"value","replacement":"{ApplianceNodeId1}"},{"query":"//*[id='VNetId']","key":"value","replacement":"{VNetId}"}]&globalStartTime={StartEpochMs}&globalEndTime={EndEpochMs}&pinGlobalTimeRange=true)
  - Per ENI (appliance 2 / paired): [open](https://portal.microsoftgeneva.com/dashboard/SiriusMDS/Sirius%2520Dashboards%2520/DataPath%2520Level%2520View%2520/Per%2520ENI?overrides=[{"query":"//dataSources","key":"account","replacement":"VNetMDM<Region>"},{"query":"//*[id='Cluster']","key":"value","replacement":"{SiriusCluster2}"},{"query":"//*[id='DeviceId']","key":"value","replacement":"{DeviceId2}"},{"query":"//*[id='ContainerId']","key":"value","replacement":"{ContainerId}"},{"query":"//*[id='NodeId']","key":"value","replacement":"{ApplianceNodeId2}"},{"query":"//*[id='VNetId']","key":"value","replacement":"{VNetId}"}]&globalStartTime={StartEpochMs}&globalEndTime={EndEpochMs}&pinGlobalTimeRange=true)

> Dashboard URL conventions (time range, comma-separated multi-value, cluster naming) are defined once in **Section 5**. Convert a UTC window to epoch-ms with PowerShell: `[DateTimeOffset]::new([datetime]::SpecifyKind([datetime]"2026-06-19 03:00:00",'Utc')).ToUnixTimeMilliseconds()`.

### Find which regions have Sirius clusters
```kusto
cluster('vnetkusto.northcentralus').database('veritas').InterfaceProgramEndFiveMinuteTable
| where TIMESTAMP > ago(4d)
| where Cluster contains "Sirius"
| distinct Cluster
| extend DCID = trim_end('A', substring(Cluster, 6, 5))   // trim_end strips all trailing 'A' padding
| join kind=leftouter (
    cluster('kvcy2wf2t0n1epwsyck1cj.australiaeast').database('public').Region_xml
    | where Cloud == "Public"
    | distinct DCID, ID, ArmLocation, FriendlyName) on DCID
| distinct FriendlyName, ArmLocation
```

> Sirius-enabled regions (subject to capacity): North Central US, West Central US, East US, West US, East US 2, Central US, UK South, West Europe, Central India, North Europe, South Central US, Southeast Asia, Sweden Central, West US 2, West US 3, plus EUAP (East US 2 EUAP / Central US EUAP).

### Kusto data sources (cluster `vnetkusto.northcentralus` / database `veritas`)
| Table | Key columns | Used for |
|-------|-------------|----------|
| `InterfaceProgramEndFiveMinuteTable` | `ContainerId`, `Cluster`, `VnetGuid`, `NodeId`, `DeviceId` | Placement: ContainerId → 2 Sirius clusters + Elba `DeviceId` + appliance `NodeId` + VNet GUID |
| `SdnApplianceEvent` | `VnetId`, `Cluster`, `ApplianceGrpId`, `ApplianceId`, `EniType`, `NodeId` | Health Manager `ApplianceGroupId` / `RackMachine` lookup (`ApplianceGrpId`); `VnetId` is the GUID **without braces** |

---

## 4. Dgrep Log Sources (Namespace: SiriusMDS)

All Sirius controller logs are reachable via **Dgrep** (Endpoint **Diagnostics PROD**, Namespace **SiriusMDS**) and via AME Kusto. Use these for control-plane / appliance health investigation.

| Event (table) | Scoping / Filter | Use Case | Sample Query |
|---------------|------------------|----------|--------------|
| `Log` | Region; `NodeId` (req — from Section 3 placement), `VnetId` (opt). "Client query" = post-filter applied in the Dgrep results pane: `source \| sort by DeviceId desc` | Map NodeId/VnetId → Sirius Elba card **DeviceId** (fallback to the Section 3 placement query) | [F3BB79E](https://portal.microsoftgeneva.com/s/F3BB79E) |
| `ElbaCardHealthTable` | Region | Health status, driver version, firmware version, bgppa + device id + gRPC channel IP | - |
| `SiriusServicingInfoTable` | Region | Detect firmware upgrade logs | — |
| `SiriusCriticalFailureTable` | Region | Critical failures for a Sirius appliance | — |
| `SiriusGrpcFailureTable` | Region | Critical failures on a gRPC channel | — |
| `SiriusGoalStateReceivedTable` | Region | Confirm goal state programming | — |
| `SiriusMadariNotificationTable` | Region | Controller notifications | — |
| `SiriusMadariSubscriptionTable` | Region | Controller subscriptions | — |

### Dgrep query template
```
DataSource: Dgrep
- Endpoint:   Diagnostics PROD
- Namespace:  SiriusMDS
- Event:      <table from above, e.g. ElbaCardHealthTable>
- Scoping:    Region == <Region>           (add NodeId / VnetId filters for the Log table)
- Time range: 30 Hours                      (Device ID lookup: 15 Minutes)
```

---

## 5. Dashboards (Geneva / Jarvis)

Sirius dashboards live under **SiriusMDS > Sirius Dashboards**. The data-plane dashboards read from the per-region MDM account **`VNetMDM<Region>`** (e.g. `VNetMDMWestUS`, `VNetMDMCentralIndia`). Fill the `account` override with the correct region.

**Conventions (apply to every link below):**
1. **Time range** — links already include `{StartEpochMs}` / `{EndEpochMs}`; replace them with **Unix epoch milliseconds (UTC)**. If you paste a fresh dashboard URL, append `&globalStartTime=<epochMs>&globalEndTime=<epochMs>&pinGlobalTimeRange=true`.
2. **Multi-value** — data-plane dashboards accept **comma-separated** values (no spaces) for `Cluster`, `DeviceId`, `NodeId` to overlay both paired appliances. Health Manager does **not** follow this pattern.
3. **Cluster naming** — use the **full `Sirius...` name** everywhere **except** Health Manager's `Machine`/`PairedMachine`/`RackMachine`, which **drop the `Sirius` prefix**.

> **Per ENI appears in both views**: the **Data Plane** Per ENI (packet counters; `Cluster`/`DeviceId`/`NodeId` scope) is for packet-level RCA; the **Control Plane** Per ENI (`ContainerId`/`MacAddress`/`VNetId`) shows ENI programming state only.

### 5.1 Control Plane

**Health Manager** (Control Plane Level View) — primary appliance/pairing health.
[Open](https://portal.microsoftgeneva.com/dashboard/SiriusMDS/Sirius%2520Dashboards%2520/Control%2520Plane%2520Level%2520View%2520/Health%2520Manager?overrides=[{"query":"//*[id='Machine']","key":"value","replacement":"{Machine}"},{"query":"//*[id='DeviceId']","key":"value","replacement":"{DeviceId1}"},{"query":"//*[id='PairedMachine']","key":"value","replacement":"{PairedMachine}"},{"query":"//*[id='PairedDeviceId']","key":"value","replacement":"{DeviceId2}"},{"query":"//*[id='ApplianceGroupId']","key":"value","replacement":"{ApplianceGroupId}"},{"query":"//*[id='RackMachine']","key":"value","replacement":"{RackMachine}"}]&globalStartTime={StartEpochMs}&globalEndTime={EndEpochMs}&pinGlobalTimeRange=true)
- Scope params: `Machine`, `DeviceId`, `PairedMachine`, `PairedDeviceId`, `ApplianceGroupId`, `RackMachine`
- > **WARNING — naming rule**: `Machine` / `PairedMachine` / `RackMachine` use the appliance name **WITHOUT the `Sirius` prefix** (cluster `SiriusPN1AA1090106002` → `PN1AA1090106002`). Every **other** dashboard uses the full `Sirius...` cluster name.
- Mapping from the placement query (Section 3 Step 2): `Machine` = `{SiriusCluster1}` de-prefixed, `DeviceId` = `{DeviceId1}`; `PairedMachine` = `{SiriusCluster2}` de-prefixed, `PairedDeviceId` = `{DeviceId2}`. Active/passive order does not matter — either Sirius row can be `Machine`.
- **`ApplianceGroupId`** = `SdnApplianceEvent.ApplianceGrpId`. **`ApplianceGroupId` and `RackMachine` are optional in the URL** — leave them blank and select from the dashboard dropdowns once `Machine` + `DeviceId` load. To pre-fill `ApplianceGroupId`:
```kusto
cluster('vnetkusto.northcentralus').database('veritas').SdnApplianceEvent
| where TIMESTAMP > ago(1d)
| where VnetId =~ "{VNetGuidNoBraces}"            // GUID without braces, e.g. XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
| distinct Cluster, ApplianceGrpId, ApplianceId, EniType
```
- Use: confirm the active/paired appliance pair is healthy. Expect entries from **two** appliances (Machine + PairedMachine).

**SC Health and Counters** (Mapping Controller Dashboard) — Sirius Controller health & counters.
[Open](https://portal.microsoftgeneva.com/dashboard/SiriusMDS/Sirius%2520Dashboards%2520/Mapping%2520Controller%2520Dashboard/SC%2520Health%2520and%2520Counters?overrides=[{"query":"//*[id='APRegion']","key":"value","replacement":"{APRegion}"},{"query":"//*[id='Cluster']","key":"value","replacement":"{SiriusCluster1},{SiriusCluster2}"}]&globalStartTime={StartEpochMs}&globalEndTime={EndEpochMs}&pinGlobalTimeRange=true)
- Scope params: `APRegion` (ARM region display name, URL-encoded, e.g. `west%20us`), `Cluster` (full `Sirius...` name; comma-separate both appliances)
- Use: Sirius Controller (Madari) health, BGP/device/NIC-level programming state.

Other control-plane dashboards (under `SiriusMDS/Sirius Dashboards/Control Plane Level View`; append the same time-range suffix):
- **Sirius Controller**: [Open](https://portal.microsoftgeneva.com/dashboard/SiriusMDS/Sirius%2520Dashboards%2520/Control%2520Plane%2520Level%2520View%2520/Sirius%2520Controller?globalStartTime={StartEpochMs}&globalEndTime={EndEpochMs}&pinGlobalTimeRange=true) — device & NIC-level programming status
- **Per Card**: [Open](https://portal.microsoftgeneva.com/dashboard/SiriusMDS/Sirius%2520Dashboards%2520/Control%2520Plane%2520Level%2520View%2520/Per%2520Card?globalStartTime={StartEpochMs}&globalEndTime={EndEpochMs}&pinGlobalTimeRange=true) — scope `DeviceId`
- **Per ENI**: [Open](https://portal.microsoftgeneva.com/dashboard/SiriusMDS/Sirius%2520Dashboards%2520/Control%2520Plane%2520Level%2520View%2520/Per%2520ENI?overrides=[{"query":"//dataSources","key":"account","replacement":"VNetMDM<Region>"},{"query":"//*[id='MacAddress']","key":"value","replacement":""},{"query":"//*[id='ContainerId']","key":"value","replacement":"{ContainerId}"},{"query":"//*[id='VNetId']","key":"value","replacement":"{VNetId}"}]&globalStartTime={StartEpochMs}&globalEndTime={EndEpochMs}&pinGlobalTimeRange=true) — scope `ContainerId`, `MacAddress`, `VNetId` (braced + uppercase); confirms control-plane ENI programming state
- **Per Appliance**: [Open](https://portal.microsoftgeneva.com/dashboard/SiriusMDS/Sirius%2520Dashboards%2520/Control%2520Plane%2520Level%2520View%2520/Per%2520Appliance?globalStartTime={StartEpochMs}&globalEndTime={EndEpochMs}&pinGlobalTimeRange=true) — scope `Cluster`, `NodeId`

### 5.2 Data Plane

> Account override = `VNetMDM<Region>`. Conventions above (time range, comma-separated multi-value, full `Sirius...` cluster names) apply to every link.

**Per ENI** (DataPath Level View) — per-ENI packet path / counters.
[Open](https://portal.microsoftgeneva.com/dashboard/SiriusMDS/Sirius%2520Dashboards%2520/DataPath%2520Level%2520View%2520/Per%2520ENI?overrides=[{"query":"//dataSources","key":"account","replacement":"VNetMDM<Region>"},{"query":"//*[id='Cluster']","key":"value","replacement":"{SiriusCluster1},{SiriusCluster2}"},{"query":"//*[id='DeviceId']","key":"value","replacement":"{DeviceId1},{DeviceId2}"},{"query":"//*[id='MacAddress']","key":"value","replacement":"{MacAddress}"},{"query":"//*[id='ContainerId']","key":"value","replacement":"{ContainerId}"},{"query":"//*[id='NodeId']","key":"value","replacement":"{ApplianceNodeId1},{ApplianceNodeId2}"},{"query":"//*[id='VNetId']","key":"value","replacement":"{VNetId}"}]&globalStartTime={StartEpochMs}&globalEndTime={EndEpochMs}&pinGlobalTimeRange=true)
- Account: `VNetMDM<Region>`
- Scope params: `Cluster` (full `Sirius...` name), `DeviceId`, `MacAddress`, `ContainerId`, `NodeId` (appliance node), `VNetId` (braced + uppercase). Comma-separate to overlay both appliances.
- Use: confirm **Packets received per Device** and **Packets sent per Device** are non-zero when the VM is sending/receiving. All-zero across the window → escalate to Cloudnet/Sirius.

**Per Card** (DataPath Level View) — per-card counters. Scope `Cluster`, `DeviceId`, `NodeId`.
[Open](https://portal.microsoftgeneva.com/dashboard/SiriusMDS/Sirius%2520Dashboards%2520/DataPath%2520Level%2520View%2520/Per%2520Card?overrides=[{"query":"//dataSources","key":"account","replacement":"VNetMDM<Region>"},{"query":"//*[id='Cluster']","key":"value","replacement":"{SiriusCluster1},{SiriusCluster2}"},{"query":"//*[id='DeviceId']","key":"value","replacement":"{DeviceId1},{DeviceId2}"},{"query":"//*[id='NodeId']","key":"value","replacement":"{ApplianceNodeId1},{ApplianceNodeId2}"}]&globalStartTime={StartEpochMs}&globalEndTime={EndEpochMs}&pinGlobalTimeRange=true)

**Per Sirius Appliance** (DataPath Level View) — per-appliance counters. Scope `Cluster`, `NodeId`.
[Open](https://portal.microsoftgeneva.com/dashboard/SiriusMDS/Sirius%2520Dashboards%2520/DataPath%2520Level%2520View%2520/Per%2520Sirius%2520Appliance?overrides=[{"query":"//dataSources","key":"account","replacement":"VNetMDM<Region>"},{"query":"//*[id='Cluster']","key":"value","replacement":"{SiriusCluster1},{SiriusCluster2}"},{"query":"//*[id='NodeId']","key":"value","replacement":"{ApplianceNodeId1},{ApplianceNodeId2}"}]&globalStartTime={StartEpochMs}&globalEndTime={EndEpochMs}&pinGlobalTimeRange=true)

Dashboard wiki: [Dashboards for Virtual Network → Accelerated Connections (Sirius)](https://supportability.visualstudio.com/AzureNetworking/_wiki/wikis/Wiki/798401/Dashboards-for-Virtual-Network?anchor=accelerated-connections-(internal%3A-sirius))

---

## 6. Validation Steps

### 6.1 Confirm feature is set on the vNIC
- **Portal JSON view**: NIC → Overview → JSON view (latest API) → check `properties.auxiliaryMode` / `auxiliarySku`.
- **Portal Properties**: NIC → Properties → Auxiliary Mode / Auxiliary SKU labels appear only when set (read-only).
- **ASC extension**: AuxiliaryMode / AuxiliarySku plugins show the configured values (default `None`).

### 6.2 Confirm subscription is onboarded to Merlin (control plane)
**SAW only** — Geneva Action: NRP > NRP Admin Client > **Get KeyValue Item** ([F7219A31](https://portal.microsoftgeneva.com/F7219A31)).
Enter subscription ID + region; in the output under `value.limits`, **`fastPathForced == 1`** means onboarded for that region (`0` = not onboarded). Merlin onboarding can take 5–7 business days.

### 6.3 [TA only] ContainerId → Elba card
1. Get the **DeviceId** — primary: the placement query (Section 3 Step 2). Fallback: the SiriusMDS **`Log`** table (Section 4) when the placement row lacks a DeviceId or you need Elba-card confirmation.
2. Run test traffic in ASC and download **Effective VFP Rules**; look for **`APPLIANCE_DECAP_RULE`** (its source IP is the Elba card BGP address). If absent, the container is not correctly deployed as an AC VM.
3. Open [ApplianceRegionalServiceConfig.xml](https://msazure.visualstudio.com/One/_git/Networking-SdnInventoryProd?path=%2Fsrc%2FSiriusInventory%2FSiriusApplianceConfig%2FCloud%2FPublic%2FSiriusRegionalConfig) and search the DeviceId to find the Elba card, Appliance Name, and BiosId.

---

## 7. Known Error Codes

| Error Code | In-code Constant | Meaning |
|------------|------------------|---------|
| `0x80070054` | `ERROR_OUT_OF_STRUCTURES` | Overprovisioning (e.g. too many route tables allocated per card) |
| `0x800700b7` | `ERROR_ALREADY_EXISTS` | Already exists |
| `0x80070490` | `ERROR_NOT_FOUND` | Not found (usually from a delete call) |
| `0x8007139f` | `ERROR_INVALID_STATE` | gRPC UNKNOWN — card unresponsive, typically after a card crash |
| `0x80073de1` | `ERROR_API_UNAVAILABLE` | gRPC UNAVAILABLE — card interface reset / coming back online (crash recovery or driver install) |

Allocation failure (regional capacity): `AllFabricsFailedtoAllocateException: No compute stamps available …  Constraints applied: Networking, VMSize` → region lacks AC capacity for that VM size.

> These codes surface in `SiriusCriticalFailureTable` / `SiriusGrpcFailureTable` (Dgrep, Section 4) and in ARM/NRP deployment errors.

---

## 8. Known Limitations / Gotchas

- **[BUG, temporary]** **VM behind Load Balancer**: DataPath Availability metric shows **0** (IcM 600175731; fix ETA Mar/Apr 2026) — do not treat as an outage by itself.
- **Floating IP** on LB rule is **not supported** — recommend disabling Floating IP.
- **Default Outbound Access** is not supported.
- **NSG flow logs** and **VNet flow logs** are not supported with Accelerated Connections.
- **UDP fragmented traffic** dropped unless VNet-level `enable-udp-fragment-reordering` is set (internal-only flag).
- **Asymmetric non-SYN**: a NIC with AC enabled requires an NSG rule to allow the asymmetric SynAck (unlike standard Azure behavior).
- **Azure NetApp Files "Basic"**, Payment HSM "Dedicated", Oracle DB at Azure "Basic", Nutanix NC2, AVS Hybrid — AC VMs cannot communicate directly (use Standard SKU equivalents where available).
- **CPS cap**: ~50,000 per IP pair (2-tuple). The reduced-tuple offload (Section 1.4) keys on srcIP/dstIP, so reusing the same IP pair shares one offloaded flow and hits this per-pair cap; for perf testing vary **ports** (or use many IP pairs) to spread load across flows.
- **VM SKU**: supported up to Dv5 (Dv6 in progress). VMSS cannot be enabled in place — redeploy.
- IPSec ESP (proto 50) / AH (51): supported as of 2025-08-22 (previously dropped).

---

## 9. Reference Wiki Pages

- [Accelerated Connections Overview](https://supportability.visualstudio.com/AzureNetworking/_wiki/wikis/Wiki?pagePath=/Azure-Virtual-Network/Features-and-Functions/Accelerated-Connections-Overview)
- [Accelerated Connections Troubleshooting](https://supportability.visualstudio.com/AzureNetworking/_wiki/wikis/Wiki/1221112/Accelerated-Connections-Troubleshooting)
- [Log Sources for Virtual Networks → Sirius](https://supportability.visualstudio.com/AzureNetworking/_wiki/wikis/Wiki/531215/Log-Sources-for-Virtual-Networks?anchor=sirius)
- [Dashboards for Virtual Network → Accelerated Connections (Sirius)](https://supportability.visualstudio.com/AzureNetworking/_wiki/wikis/Wiki/798401/Dashboards-for-Virtual-Network)
- VNET-Wiki (internal): https://msazure.visualstudio.com/VNET-Wiki/_wiki/wikis/VNET-Wiki.wiki/357253/Sirius
- Study material work item: https://dev.azure.com/SeekTheWay/SeekTheWay/_workitems/edit/355
- NSDI'23 paper (Disaggregating Stateful Network Functions): https://www.usenix.org/system/files/nsdi23-bansal.pdf
