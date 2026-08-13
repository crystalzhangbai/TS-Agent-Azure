---
name: b01
version: 1.0.0
description: "Azure Networking Kusto queries, Geneva Metrics (MDM), and DGrep log queries from B01 Dashboard (aka.ms/b01). Use this skill when troubleshooting Azure VM, ExpressRoute, VPN Gateway, Load Balancer, Application Gateway, Azure Firewall, Azure DDoS Protection, Front Door, NAT Gateway, Virtual Network, VirtualWAN, Route Server, Private Link, SLB, physical network, WAN backbone, NRP/ARM operations, Traffic Manager, or Host Networking (VFP MDM drops/traffic/GFT/support dashboards, AccelNet SLI, BNIC/OverLake, FPGA-PDP, VM dataplane perf shoebox, Internet Peering) with KQL, MDM, and DGrep."
---

# Azure Networking B01 Kusto Query Skill

> **Source:** Azure Networking B01 Dashboard ([aka.ms/b01](https://aka.ms/b01))  
> **Coverage:** 563+ production KQL queries across 30 reference files  
> **Last Updated:** 2026-06-08

## When to Use This Skill

Use this skill when you need KQL queries for:
- **VM troubleshooting** — host health, availability, platform events, GuestAgent, serial console, live migration, service healing
- **Host Networking** — VFP MDM drop/flow metrics, Host NIC drop diagnostics, AccelNet SLI, Network-Dashboard-VM links
- **ExpressRoute** — circuit health, peering, BGP, ARP, ER Gateway tunnels, bandwidth
- **VPN Gateway** — tunnel status, IKE diagnostics, S2S/P2S connectivity
- **Application Gateway** — backend health, WAF, access logs, config changes
- **Load Balancer / NAT Gateway** — health probes, SNAT, data path, NAT rules
- **Azure Firewall** — rule processing, threat intel, SNAT port usage
- **Azure DDoS Protection** — attack detection, protection status, mitigation metrics, incident investigation
- **Front Door / CDN** — routing, origin health, WAF, edge nodes
- **Virtual Network / VirtualWAN** — VNet peering, Route Server, NSG, NMAgent
- **Accelerated Connections (internal: Sirius)** — AMD Pensando SDN-appliance feature for high CPS / NVAs: vNIC AuxiliaryMode/Sku enablement, control/data-plane dashboards, SiriusMDS Dgrep logs, appliance & Elba-card health
- **Azure Virtual Network Manager (AVNM)** — commit deployment failures, goal state propagation, routing/connectivity/security admin configs, managed resource group issues
- **Private Link** — Private Endpoint and Private Link Service health, connectivity diagnostics, CRUD operations
- **Traffic Manager** — profile/endpoint inventory, health state changes, DNS query analytics, probe errors, frontend (ARM) logs, heat maps
- **NRP / ARM operations** — API throttling, write operations, error diagnosis
- **Physical Network / WAN** — T0/T1/T2 devices, link utilization, WAN backbone
- **SLB / Azure VIP** — SLB ring health, VIP diagnostics
- **Virtual WAN, Virtual Hub, Route Server** — Virtual WAN, Virtual Hub, Route Server diagnostics
- **IcM / CSAT** — incident data, customer satisfaction

## Key Data Sources

| Cluster | Database | Used For |
|---------|----------|----------|
| `cluster('azurecm')` | `AzureCM` | MDM metrics, region metadata |
| `cluster('Hybridnetworking')` | `aznwmds` | Gateway, Circuit, VPN, ER data |
| `cluster('Hybridnetworking')` | `GatewayManager` | App Gateway, ER Gateway manager |
| `cluster('nrp')` | `mdsnrp` | NRP write/read operations |
| `cluster('armprod')` | `ARMProd` | ARM HTTP requests, throttling |
| `cluster('azcrpmc')` | `crp_allprod` | CRP VM operations |
| `cluster('Azslb')` | `azslbmds` | Load Balancer, SLB ring |
| `cluster('azurecdn')` | `azurecdnmds` | Front Door, CDN |
| `cluster('waneng.westus2')` | `waneng` | WAN backbone |
| `cluster('apdmdata')` | `DeviceManager` | Network devices |
| `cluster('azurehn')` | `Azurehn` | VFP MDM account mapping, Host Networking metrics |
| `cluster('aztmmon')` | `aztmmondb` | Traffic Manager profiles, endpoints, health changes, DNS queries |
| `cluster('aznwsdn')` | `nsmplus` | AVNM commit lifecycle, goal states, deployment status, trace logs |
| `cluster('aznwddos.centralus')` | `cnsgeneva` | Azure DDoS Protection queries |
| `cluster('azcore.centralus')` | `Fc` | Node events, AzCoreCluster mapping |
| `cluster('azcore.centralus')` | `NicAgent` | NicAgent brownout/blackout (BrownoutClient, ManaInstaller) |
| `cluster('azcore[N].<region>')` | `OvlProd` | OverLake SoC systemd logs (`LinuxOverlakeSystemd`) — NDPA blackout |
| `cluster('vmainsight')` | `Air` | NDPA upgrade event streams (`_EventStream_SoC_NDPAServiceUpgrade`) |

## IMPORTANT - Kusto Query Format**:
When user ask to return Kusto queries to users, **always** use the fully qualified format:
```kusto
cluster("<clustername>").database("<dbname>").<tablename>
| where ...
```
## Reference Files

### Routing Guide — vm-infra.md vs hostnetworking.md vs vm-crp-crud.md

| User Scenario | Use File |
|---------------|----------|
| VM basic info (subscription, node, container, region, size) | `vm-infra.md` |
| VM downtime, availability, loss ratio, pingmesh | `vm-infra.md` |
| Physical network path (TOR↔T1↔T2↔RHW), discard/error counters | `vm-infra.md` |
| VFP flow state per container | `vm-infra.md` |
| Live migration, service healing, guest OS lookup | `vm-infra.md` |
| **Node dashboard deep-links by nodeId** (VFP/Drop/GFT/FPGA/NetVMA) | `vm-infra.md` |
| **SOC dashboard, SOC crash events, OverLake detection** | `vm-infra.md` |
| **Node state, availability, health signals (LogNodeSnapshot)** | `vm-infra.md` |
| **Host NIC discard/error/RDMA counters (Netperf)** | `vm-infra.md` |
| **Anvil Repair Service Request by nodeId** | `vm-infra.md` |
| **CA to VM mapping** (find VMs behind a Customer Address) | `vm-infra.md` |
| **VFP packet drops** (Resource/ACL/Malformed/Pending drop) | `hostnetworking.md` |
| **VFP flow creation rate (CPS)** | `hostnetworking.md` |
| **Host NIC drop** (AccelnetSLI, BNIC, OverLake counters) | `hostnetworking.md` |
| **Network-Dashboard-VM** (VFP/PNIC dashboard links) | `hostnetworking.md` |
| Host networking level packet loss investigation | `hostnetworking.md` → then `vm-infra.md` for physical path |
| **VFP MDM support metrics** (TCP SYN/ACK, FPGA GFT healthy, ratelimiter drops, RDMA) | `vfpmdm-support-dashboard.md` |
| **VFP MDM traffic counters** (pNIC/vNIC/Mellanox packets & bytes rates) | `vfpmdm-traffic-dashboard.md` |
| **VFP MDM drop counters** (VfpPortDropMetrics, VmsNicDropMetrics, BNIC, FPGA-PDP) | `vfpmdm-drops-dashboard.md` |
| **GFT flow offload investigation** (offload success/fail/blocked, exception packets) | `vfpmdm-gft-dashboards.md` |
| **ARM/CRP API operation lookup** (correlationId, operationId) | `vm-crp-crud.md` |
| **VM create/delete failure investigation** (CRP ApiQosEvent) | `vm-crp-crud.md` |
| **Compute capacity trends per SKU** | `vm-crp-crud.md` |
| **NDPA SoC PF Update blackout/brownout** (OverLake FPGA firmware upgrade) | `ndpa-soc-blackout.md` |
| **NicAgent brownout** (BrownoutClient, ManaInstaller NIC driver update) | `ndpa-soc-blackout.md` |
| **AzCore regional cluster mapping** (find which azcore# for a node) | `ndpa-soc-blackout.md` |
| **LinuxOverlakeSystemd blackout logs** (exact blackout duration in ms) | `ndpa-soc-blackout.md` |
| **PMEM high memory pressure → Unallocatable** (OverLake node, heap >85%, FaultCode 10036) | `ndpa-soc-blackout.md` |

> **Typical workflow for host networking packet drop:** Start with `hostnetworking.md` (VFP drops → Host NIC drops → Network-Dashboard-VM links), then escalate to `vm-infra.md` physical network path queries if VFP and Host NIC are clean.

### hostnetworking.md — Investigation Scope

Use `hostnetworking.md` when the suspected issue occurs **on the host node itself** or **on the connection between the TOR switch and the host node**. This covers the full host networking data-plane stack, including but not limited to:

- **TOR interfaces** — the TOR-facing port connecting to the host node (errors, discards, link flaps on the host-side interface)
- **TOR ↔ Host Node link** — the physical cable and link-layer connection between TOR and the server NIC
- **Gemini TOR Y-cable** — dual-TOR (active-standby) Y-cable status and switchover events
- **FPGA** — Azure SmartNIC FPGA datapath, GFT (Generic Flow Table) offload, FPGA capture diagnostics
- **SoC (OverLake)** — System-on-Chip networking counters (`NetDatapathPerfCounters`), backplane metrics
- **Accelerated Networking (AccelNet)** — AccelNet availability SLI (`AccelnetSLI`), enable/disable events, disruption categories
- **Host NIC (Mellanox / MANA)** — physical NIC drop counters (`GdmaBnicGlobalCounters`, `ManaBnicInternalCounters`), firmware events (`Mlnx5FwIntermediary_v1`), backpressure indicators
- **VFP / vSwitch** — Virtual Filtering Platform packet drops (Resource, ACL, NoRuleMatch, Malformed, Pending, Simulation), flow creation rate (CPS), unified flow entries
- **GFT (Generic Flow Table)** — hardware flow offload status, GFT dashboard links

**When to escalate to hostnetworking.md:** If investigation from `vm-infra.md` (e.g., Host-TOR PingMesh drop, disk read/write congestion pointing to network, or VFP flow state anomalies) suggests a host-level networking problem, proceed to `hostnetworking.md` for deeper diagnosis.

### Compute & VM
| File | Description | Queries |
|------|-------------|---------|
| [vm-infra.md](references/vm-infra.md) | **VM Infrastructure, Host & Node Investigation** (B01 VM-Dash + Node-Dash KQL queries): VM lookup by subscription/containerId → generates deep-links (VFPDashBoard, SupportDashBoard, VMPerf/Shoebox, NetVMA, ASIHostNode, InvestigateNode, NodeDash, VMCRUD, KernaCapture); CA-PA mapping; VM downtime events; loss ratio (cluster/DC/region); physical network path traversal Node→TOR→T1→T2→RHW/RHE→RA (bandwidth, PPS, discard/error per hop); Dual-TOR status; AHZ/AHY path; MKA/BGP/LinkFlap event counts; Host-TOR PingMesh; disk read/write congestion (RDMA/ECN via Netperf); VFP flow state per container; live migration & PV events; service healing; guest OS/image version lookup; MAC→ContainerID; ARM ResourceURI lookup; **Node-centric deep-links by nodeId** (VFPDashBoard, DropDashBoard, GFTDashboard, FPGADashboard, InvestigateNode, ASIHostNode, NetVMA, PerProcessorPNICDashboard); VMs under a node; SOC Dashboard (BackplaneMetrics, SOCDashboard, OverLake detection); SOC Crash Event analysis (WatsonCustomer crash dumps, faultingModule, bucketString); LogNodeSnapshot (nodeState, availability, health signals); Host NIC discard/error/RDMA counters; Anvil Repair Service Request; CA→VM mapping (Src/Dst VMs, WAN cross-region dashboard); CA→VM mapping Temu variant | 64 |
| [hostnetworking.md](references/hostnetworking.md) | **Host Networking**: VFP MDM drop/flow metrics, Host NIC drop diagnostics (AccelnetSLI, BNIC, OverLake), Network-Dashboard-VM dashboard links | 23 |
| [vm-crp-crud.md](references/vm-crp-crud.md) | CRP ARM API operations (ApiQosEvent, ContextActivity) and compute capacity trends per SKU | 3 |
| [vm-dataplane-perf-shoebox.md](references/vm-dataplane-perf-shoebox.md) | **VM Dataplane Performance — RDOS Shoebox MDM Dashboard** (`RDOS/Shoebox/VMPerf-WithParameters`): 25 tiles covering CPU % (avg), CPU credits remaining; disk queue depth/read/write bytes/IOPS/latency per LUN, disk bandwidth & IOPS consumed %, disk IO outliers [CONFIDENTIAL]; network in/out bytes per min, inbound/outbound flows; RAM size & available RAM [CONFIDENTIAL], memory pressure [CONFIDENTIAL]; VM history + HostAnalyzer command + NetVMA/ASI links + physical hardware layout (host cores, TOR, spine) [CONFIDENTIAL]. Template params: `Region` (→ MDM account e.g. `AzComputeShoeboxWUS2`) and `VMID` (→ `ResourceId` dimension filter). Confidential tiles (9, 12, 24, 25) require internal cluster access (`azcore/Fa`, `azurecm/AzureCM`). | 25 |
| [vfpmdm-support-dashboard.md](references/vfpmdm-support-dashboard.md) | **VFP MDM Support Dashboard** (`VfpMDM/dpop/SupportDashboard`): 31 tiles — TCP connection establishment (SYN/SynAck rates), FPGA GFT healthy, FPGA-CONFIG IsGolden, VFP flows (inbound/outbound), dropped frag packets, VFP ratelimiter drops, VMSwitch drops, VFP ACL drops, RDMA success/failure & latency (Kusto: netperf/NetPerfKustoDB), FPGA FCS errors, NIC errors (Mellanox/BNIC), portal bytes/packets, port timer metrics. Template params: `Account`, `NodeId`, `ContainerId`, `Cluster`. | 31 |
| [vfpmdm-traffic-dashboard.md](references/vfpmdm-traffic-dashboard.md) | **VFP MDM Traffic Dashboard** (`VfpMDM/dpop/TrafficDashboard`): 24 tiles — FPGA-PFC packets sent/received, pNIC packets/bytes sent/received, vNIC packets/bytes sent/received, Mellanox NIC counters (MlnxAdapterCounters, Mlx5TrafficCounters), VFP inbound/outbound packet rates (pending, throttled, total, intercept, multicast, hairpinned, unicast). Template params: `Account`, `NodeId`, `ContainerId`, `Cluster`. | 24 |
| [vfpmdm-drops-dashboard.md](references/vfpmdm-drops-dashboard.md) | **VFP MDM Drops Dashboard — Merged** (`VfpMDM/dpop/dropsDashboard` + `dropsDashboard_OVL2`): merged pre-OVL2 & OVL2 dashboards — FPGA-PFC/GFT drops, pNIC/vNIC dropped packets & percentages, Mellanox NIC drops (pre-OVL2), BNIC Global/SoC/Host/Vf drops (OVL2), VFP port drop metrics sets 1–4 (VfpPortDropMetrics), VMSwitch drop metrics sets 1–4 (VmsNicDropMetrics), injected resets, DNS/DHCP drops, backplane errors, FPGA-PDP errors (OVL2), FPGA-NETWORK-V2 traffic (OVL2). Each tile tagged `[Both]`/`[Pre-OVL2 only]`/`[OVL2 only]`. Template params: `Account`, `NodeId`, `ContainerId`, `Cluster`. | 86 |
| [vfpmdm-gft-dashboards.md](references/vfpmdm-gft-dashboards.md) | **VFP MDM GFT Dashboards — Merged** (4 sub-dashboards: FlowOffload, GftNode, GftPort, GftVfpPort): GFT flow offload success/failed/blocked/retry reasons, exception & copy packets, midstream packets, GFT node flow/error counters, parser/cache counters, VLAN drops, VPort packet counters, VPort flow offload counters, blocked breakdown, GFT state, packet/byte counters, container offload limits, multitenancy config. Namespaces: `VfpPortGftMetrics`, `GFTVPort`, `GFTLWF`, `FPGA-GFT`. Template params: `Account`, `NodeId`, `ContainerId`, `Cluster`. | 51 |
| [ndpa-soc-blackout.md](references/ndpa-soc-blackout.md) | **NDPA SoC PF Update — Blackout/Brownout Investigation**: OverLake SoC PilotFish firmware upgrade detection, FPGA blackout duration from `LinuxOverlakeSystemd` (OvlProd), NicAgent `BrownoutClient`/`ManaInstaller` analysis, AzCore regional cluster mapping (`TMMgmtNodeEventsEtwTable.AzCoreCluster`), Air NDPA event streams (`_EventStream_SoC_NDPAServiceUpgrade`), **PMEM high memory pressure → Unallocatable** (FaultCode 10036, heap >85% triggers OaaS MarkNodeUnallocatable with AllowLM=true; recovery at <45%). Clusters: `azcore[N].<region>` / OvlProd, `azcore.centralus` / NicAgent, `vmainsight` / Air. | 8 |

### Gateway & ExpressRoute
| File | Description | Queries |
|------|-------------|---------|
| [expressroute-circuit.md](references/expressroute-circuit.md) | Circuit health, peering, BGP routes, ARP, bandwidth | 17 |
| [expressroute-gateway.md](references/expressroute-gateway.md) | ER Gateway health, tunnel status, connection drops, BGP peers | 33 |
| [vpn-gateway.md](references/vpn-gateway.md) | VPN tunnel status, IKE diagnostics, S2S/P2S connectivity | 11 |
| [application-gateway.md](references/application-gateway.md) | Health probes, backend status, WAF, access logs, config changes | 18 |

### Load Balancing & Traffic
| File | Description | Queries |
|------|-------------|---------|
| [load-balancer.md](references/load-balancer.md) | Load Balancer health probes, SNAT, NAT Gateway rules | 15 |
| [natgw-packet-drop.md](references/natgw-packet-drop.md) | NAT Gateway packet drop deep-dive — 3-layer ring model, 8 RCA scenarios, Geneva dashboards | 9 |
| [azure-firewall.md](references/azure-firewall.md) | Firewall rule processing, threat intel, SNAT | 8 |
| [front-door-cdn.md](references/front-door-cdn.md) | Front Door routing, origin health, WAF, edge nodes | 11 |
| [slb-vip.md](references/slb-vip.md) | SLB ring health, Azure VIP diagnostics | 37 |
| [slb-deep-rca.md](references/slb-deep-rca.md) | SLB/MUX deep RCA — crash analysis, SF health, exceptions | 7 |

### Traffic Manager
| File | Description | Queries |
|------|-------------|---------|
| [traffic-manager.md](references/traffic-manager.md) | Profile/endpoint inventory, health state changes (Prod/Preview/FF/MC), DNS query analytics, probe error lookup, ARM control plane logs, traffic heat maps | 10 |

### Virtual Networking
| File | Description | Queries |
|------|-------------|---------|
| [virtual-network.md](references/virtual-network.md) | VNet, VirtualWAN, Route Server, hybrid network, NSG, NMAgent | 35 |
| [accelerated-connections-sirius.md](references/accelerated-connections-sirius.md) | **Accelerated Connections (internal: Sirius)** — AMD Pensando DSC-200 (Elba) SDN-appliance architecture, vNIC `auxiliaryMode`/`auxiliarySku` enablement, active-passive pairing/overprovisioning, reduced-3-tuple, **9 verified Geneva dashboards** (Control Plane: Health Manager, SC Health and Counters, Sirius Controller, Per Card, Per ENI, Per Appliance; Data Plane: Per ENI, Per Card, Per Sirius Appliance), **token glossary** + conventions (account `VNetMDM<Region>`, comma-separated multi-value Cluster/DeviceId/NodeId, `pinGlobalTimeRange` epoch-ms suffix, Health Manager drops the `Sirius` prefix), SiriusMDS Dgrep log sources (Log/ElbaCardHealth/ServicingInfo/Critical/Grpc/GoalState), placement Kusto via `cluster('vnetkusto.northcentralus').database('veritas')` — `InterfaceProgramEndFiveMinuteTable` (ContainerId → 2 Sirius clusters + DeviceId/NodeId + VnetGuid) and `SdnApplianceEvent` (ApplianceGrpId), Merlin onboarding validation, known error codes, CRI pre-checks (queue Cloudnet/Sirius) | 9 dash |
| [avnm-deploy.md](references/avnm-deploy.md) | Azure Virtual Network Manager (AVNM) deployment troubleshooting — commit lifecycle, goal state propagation, error diagnosis, managed RG failures | 18 |
| [private-link.md](references/private-link.md) | Private Endpoint and Private Link Service health checks, connectivity diagnostics | 9 |
| [nrp-arm-operations.md](references/nrp-arm-operations.md) | NRP/ARM API operations, throttling, Resource Graph | 19 |

### Physical Network & WAN
| File | Description | Queries |
|------|-------------|---------|
| [physical-network.md](references/physical-network.md) | T0/T1/T2 device health, interface utilization, optical, BGP | 79 |
| [wan-backbone.md](references/wan-backbone.md) | WAN link utilization, Moby paths, backbone health | 56 |
| [network-device.md](references/network-device.md) | Network device inventory, health status, OS versions | 25 |

### Internet & Monitoring
| File | Description | Queries |
|------|-------------|---------|
| [internet-peering.md](references/internet-peering.md) | Internet peering, monitoring, traffic collector, IPFIX/SFlow | 43 |
| [ddos.md](references/ddos.md) | DDoS investigation — IPFIX (NetCapPlan) & DDoS flow logs, traffic direction analysis, top talkers, protocol distribution, volumetric attack detection | 3 |
| [icm-csat.md](references/icm-csat.md) | IcM incident data, CSAT analysis | 4 |

### Virtual WAN & Route Server
| File | Description | Queries |
|------|-------------|---------|
| [virtualwan-rs.md](references/virtualwan-rs.md) | Virtual WAN, Virtual Hub, Route Server | 8 |
| [ergw-rs-route-sync.md](references/ergw-rs-route-sync.md) | ERGW↔Route Server route sync investigation — NextHop discrepancy, GRPC delivery, adjacency comparison | 10 |

## Common Query Patterns

### Cross-cluster query
```kql
cluster('Hybridnetworking').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp between (starttime .. endtime)
| where CustomerSubscriptionId == subscriptionid
```

### Dashboard parameters (replace before use)
- `SubscriptionID` — Azure subscription GUID
- `_startTime` / `_endTime` — Time range (datetime)
- Resource names: `AppGwName`, `ErGwName`, `VpnGwName`, `LBName`, `PEName`, `PLSName`, `PENICName`, `PLSNICName`, `ILBName`, etc.

### Unix timestamp conversion
```kql
let startunixtime = tolong(starttime - datetime(1970-01-01)) / 10000;
let endunixtime = tolong(endtime - datetime(1970-01-01)) / 10000;
```

### Private Link health check query
```kql
cluster('nrp').database("mdsnrp").QosEtwEvent
| where PreciseTimeStamp between (starttime .. endtime)
| where SubscriptionId == SubscriptionID
| where ResourceName == PEName
| where OperationName contains "PrivateEndpoint"
| project PreciseTimeStamp, Success, ResourceType, ResourceName, OperationName, ErrorCode, ErrorDetails, Region
| order by PreciseTimeStamp desc
```

## Cross-Region Network Jitter / Latency Troubleshooting SOP

When investigating cross-region (inter-DC) network jitter, latency spikes, or packet loss between VMs in different Azure regions, follow this **path-first, data-plane-first** methodology. Do NOT start with BGP flap checks — BGP flaps only indicate control plane issues, while most cross-region jitter is caused by data plane congestion (OutDiscards).

### Step 1: Trace the Full Physical Path (MUST DO FIRST)

**Layer 1 — VM → ToR:** Use `AzureCM.LogContainerSnapshot` + `aznwcc.Servers` to find each VM's T0 switch.
```kql
cluster('azurecm').database('AzureCM').LogContainerSnapshot
| where PreciseTimeStamp >= datetime(STARTTIME)
| where containerId in (dynamic(["CONTAINER_ID"]))
| take 1
| project containerId, Cluster, NodeId, AvailabilityZone
| join kind=inner (
    cluster('aznwcc').database('aznwmds').Servers 
    | where PreciseTimeStamp > ago(1d) 
    | distinct NodeId, DeviceName
) on NodeId
| project containerId, Cluster, NodeId, ToRDeviceName=DeviceName
```

**Layer 2 — ToR → WAN Edge:** Use `azphynet.DeviceInterfaceLinks` to verify T2 uplinks to RHWE/RA devices.

**Layer 3 — WAN Backbone Path (Swan TE):** Use TE demand's RouterHopsWithPorts to discover the full WAN path. Filter by Source (source-side WAN edge router) and Destination (destination-side WAN gateway city code):
```kql
// Forward path derivation: Source=source WAN edge, Destination=destination WAN gateway
// DO NOT pre-filter by intermediate hops — let TE tell you the path
cluster('azwan').database('Swan').f_SwanProd_TEScheduler_SolverDemands_Raw(
    datetime(STARTTIME), datetime(ENDTIME), 'DEPLOYMENT_NAME')
| where (Source == "owr03.SOURCE_SITE" or Source == "owr03.SOURCE_SITE2")
    and (Destination == "DEST_SITE1" or Destination == "DEST_SITE2")
| project Source, Destination, TrafficClass, PathPriority, RequestedMbps, RouterHopsWithPorts
```
**Important:** Swan TE Deployment names — use `ProductionNAM1` for NAM region OWR routers, `ProductionOneNam` for OneWAN routers, `ProductionOneEu` for EU. Source field uses full device name (e.g., `owr03.dub07`), Destination uses city code (e.g., `IAD11`, `CO8`).

### Step 2: Global Data Plane Scan — OutDiscards on ALL WAN Backbone Devices

**This is the single most important step.** Scan ALL WAN backbone routers for OutDiscards during the incident window:
```kql
cluster('aznwnetmon').database('aznwmds').sXInterfaceTable
| where DeviceName matches regex "^(ibr|owr|car)\\d+"
| where PreciseTimeStamp between (datetime(STARTTIME) .. datetime(ENDTIME))
| summarize MaxOutDiscards=max(ifOutDiscards_Counter) by DeviceName, ifName
| where MaxOutDiscards > 100
| order by MaxOutDiscards desc
```

**Critical — sXInterfaceTable correct column names:**
| Correct Column Name | Meaning | Common Mistake |
|---|---|---|
| `PreciseTimeStamp` | Timestamp | ~~vscpTimeStamp~~ |
| `ifName` | Interface name | ~~InterfaceName~~ |
| `ifOutDiscards_Counter` | OutDiscards per-interval **delta** | ~~OutDiscards~~ |
| `ifInDiscards_Counter` | InDiscards per-interval **delta** | ~~InDiscards~~ |
| `_Raw_ifOutDiscards_Counter` | OutDiscards **cumulative** SNMP counter | (no common mistake) |
| `ifOutErrors_Counter` | OutErrors per-interval delta | ~~OutErrors~~ |
| `ifInErrors_Counter` | InErrors per-interval delta | ~~InErrors~~ |
| `Interval` | Seconds between SNMP polls | — |
| `ifHighSpeed` | Link speed (Mbps) | — |
| `ifHCInOctets_Counter` / `ifHCOutOctets_Counter` | Octet counters (delta) | — |

### Step 3: Check Control Plane (BGP / ISIS / Swan Tunnel)

Only AFTER Steps 1-2. Check BGP flaps, ISIS neighbor down, Swan tunnel down on devices **confirmed to be on the path** from Step 1.

### Step 4: Deep Dive Root Cause Mechanism

If OutDiscards found: check Swan TE bandwidth allocation, traffic demand trends, link member status, and TE scheduler timing.

### Common Pitfalls to Avoid
1. **Don't start with BGP flap scans** — BGP flaps are control plane; most jitter is data plane (queue overflow)
2. **Don't investigate devices not on the path** — Always trace path first, then investigate
3. **Don't assume "WAN is clean" from BGP alone** — Zero BGP flaps does NOT mean zero data plane issues
4. **sXInterfaceTable column names are different from what you might expect** — See table above
5. **Swan TE data: DUB/EU devices often appear only in RouterHops, not as Source** — Use correct Source/Destination patterns
6. **ifOutDiscards_Counter is a per-interval DELTA, not cumulative** — Sum across intervals for total; use `_Raw_` prefix for cumulative counter


## SLB / MUX Node Failure Troubleshooting SOP

When investigating **SLB MUX node failures** — TOR Pingmesh drop to 0%, NAT Gateway / LB datapath availability impact, or VIP unavailability — follow this SOP. Full query details in [slb-deep-rca.md](references/slb-deep-rca.md).

> ⚠️ **Architecture Note:** SLB MUX nodes are managed by **Service Fabric**, NOT AzureCM. Do NOT search `LogNodeSnapshot`/`LogContainerSnapshot` for MUX node state — use azslbmds tables instead.

### Step 1: Identify the Ring and Faulted MUX Node
Use `slb-vip.md` queries:
- **Ring MUX Instance Information** → list all MUX nodes, NodeIds, ToR mapping
- **MUX Node TOR Pingmesh** → identify which node(s) had connectivity drop (0%)

### Step 2: Check MUX Process Crash — SlbCritical
Query `SlbCritical` in azslbmds for the ring. Look for `MuxShutdownUnexpected` — this is the **smoking gun** for MUX process crash. Also check for log gaps (silence = process dead).

### Step 3: Check Service Fabric Health — NodeHealthEvent
Query `NodeHealthEvent` (⚠️ uses `TIMESTAMP`/`Role`/`NodeName`, NOT `env_time`/`env_cloud_role`). Look for "Fabric node is down" (Error) from `System.FM`.

### Step 4: Check Data Plane Impact — SlbHealthEvent
Query `SlbHealthEvent` by Ring for `DataPathAvailabilityWarning` and `NoForwardingDip`. This reveals the blast radius — which VIPs and customers were affected.

### Step 5: Check Recovery Issues — SlbException
After crash recovery, MUX reconnects to SDN Gateway. Query `SlbException` for `WebException` to detect delayed recovery.

### Step 6: Exclude Physical Network
Use `slb-vip.md` → **Discard and Error packet counter over T0 of MUX** and `physical-network.md` queries to confirm ToR/T1 links were UP throughout.

### Key Principle: MUX Crash ≠ Network Fault
If TOR Pingmesh drops to 0% but ToR/T1 links are UP with zero errors, the root cause is almost always **MUX process crash** (VFP LWF driver lost its control process), not a physical network fault.

