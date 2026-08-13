---
description: NAT Gateway packet drop deep-dive troubleshooting — 3-layer ring architecture, 8 root cause scenarios (Mux crash, overload, noisy neighbor, maintenance, node isolation, SNAT exhaustion, rate limiting), Geneva dashboard links, KQL queries, and RCA templates.
---

# NAT Gateway Packet Drop Troubleshooting Skill

> **Scope**: NAT Gateway intermittent packet drops, connection timeouts, DataPath Availability degradation  
> **Last Updated**: 2026-04-03

---

## 1. Data Plane Architecture

```
Outbound (Steps ①②③):
  ① VM → MUX(MNAT VIP)     GRE | Outer: VM PA → MNAT VIP | Inner: VM CA → Internet IP
  ② MUX → NAT GW_IN_x      VXLAN Udp:10000 | Outer: VM PA → NAT_GW_IN PA | Inner: VM CA → Internet IP
  ③ NAT GW_IN → Internet    No encap | S: NATGW SNAT VIP | D: Internet IP

Return (Steps ④⑤⑥):
  ④ Internet → MUX(SNAT VIP)   No encap | S: Internet IP | D: NATGW SNAT VIP
  ⑤ MUX → NAT GW_IN_x          VXLAN Udp:20000 | Outer: Internet IP → NATGW_IN PA
  ⑥ NAT GW_IN → VM             GRE | Outer: VM PA → VM PA | Inner: Internet IP → VM CA

                          Internet
                         ↑        ↓
                    ③ Out      ④ Return
                         |        |
        MUX(MNAT VIP)    |    MUX(SNAT VIP)
        [SliceVip Ring]  |    [SNAT VIP Ring]
              ↑          |         ↓
         ① GRE      ② VXLAN:10000   ⑤ VXLAN:20000
              |          ↓         |
              VM    [ NAT GW_IN_0 / IN_1 / ... / IN_6 ]  ← MNAT Ring
                         |
                    ⑥ GRE to VM
```

### Three-Layer Ring Model (must check all three for DP drop)

| Ring | Role | Direction | How to Find |
|------|------|-----------|-------------|
| **MNAT Ring** | NAT Worker SNAT translation | Both | `NatGatewayAllocation` → NatSlice |
| **SliceVip Ring** | Outbound VIP forwarding ①→② | Outbound | MulticastGroup from B01 query |
| **SNAT VIP Ring** | Return VIP forwarding ④→⑤ | Return | Query `VipMetadataSnapshotRecord` with SNAT IP |

> ⚠️ SliceVip Ring and SNAT VIP Ring may be **different rings**!

---

## 2. Decision Tree

```
NATGW packet drop reported
    │
    ├─ Step 1: Get NATGW info (NatGwId, SliceVip, MNAT Ring, SNAT IPs, MulticastGroup)
    ├─ Step 1b: Get SliceVip Serving Ring + SNAT VIP Ring
    │
    ├─ Step 2: Check DataPath Availability
    │   ├─ 100% → Not platform issue → check customer side (SNAT exhaustion/NSG/UDR)
    │   └─ < 100% → Platform issue → continue
    │       ├─ Check Failed Probes (s/F28AA3D) → pinpoint exact time
    │       └─ Check DIP Drop (s/ED1F733C) → rule out backend
    │
    ├─ Step 3: Check Ring Health (SlbHealthEvent, SlbCritical, MuxStatsV2)
    │
    └─ Step 4: Root Cause — 8 scenarios
        ├─ A: Mux Crash           → SlbCritical: MuxShutdownUnexpected
        ├─ B: Mux Overload        → MuxStatsV2: dropped packets ↑ (SAAFD ring)
        ├─ C: Physical Network    → sXInterfaceTable: OutDiscards > 0
        ├─ D: Noisy Neighbor      → NATGW DP dash (clear GW ID filter) + MuxStatsV2 spike
        ├─ E: Instance Maint.     → Worker Health: nodes drop sequentially (rolling)
        ├─ F: Node Isolation      → Routes drop on single node + NotConnected MessageBus
        ├─ G: SNAT Port Exhaust.  → NAT Worker Stats: Allocation Failures spike
        └─ H: Rate Limiting       → Rate-Limit RxPktsDropped spike
```

---

## 3. KQL Queries

### Step 1: NATGW Basic Info

> If ARG access is denied, stop and ask user for NATGW metadata.

```kql
let starttime = datetime({StartTime});
let endtime = datetime({EndTime});
let SubscriptionID = "{SubscriptionId}";
let NATGN = "{NATGatewayName}";
let NatGwId = toscalar(
    cluster('argwus2nrpone.westus2').database('AzureResourceGraph').Resources
    | where subscriptionId == SubscriptionID
    | where timestamp >= starttime - 2d and timestamp <= endtime
    | where type == "microsoft.network/natgateways" and name == NATGN
    | distinct ResourceGUID=tostring(parse_json(properties)["resourceGuid"])
    | extend NatGatewayId=strcat("NGW_", ResourceGUID)
    | distinct NatGatewayId);
cluster('Azslb').database('azslbmds').NatGatewayAllocation
| where env_time >= starttime - 1d and env_time <= endtime
| where NatGatewayId in (NatGwId)
| extend NatGatewayIds=tostring(split(tostring(NatGatewayId), "NGW_")[1])
| distinct SdnId, NatGatewayId=NatGatewayIds, SnatIpAddresses, Protocols, Subnets,
  IdleTimeoutInSeconds, VnetId, NatSlice, SliceVip
| join kind=leftouter cluster('azslb').database('azslbmds').VipMetadataSnapshotRecord
  on $left.SliceVip == $right.Vip
| distinct SdnId, NatGatewayId, SnatIpAddresses, Protocols, Subnets,
  IdleTimeoutInSeconds, VnetId, NatSlice, SliceVip,
  NATRing = strcat("Slb-",extract(@"Slice_(.+?)""", 1, VmLocs))
```

### Step 1b: SliceVip Serving Ring

> SliceVip Serving Ring = MulticastGroup rings. `env_cloud_role` is the **reporting** ring, NOT the serving ring.

```kql
cluster('Azslb').database('azslbmds').VipMetadataSnapshotRecord
| where env_time >= datetime({StartTime}) - 6h and env_time <= datetime({EndTime}) + 1h
| where Vip in ('{SliceVip}')
| distinct Vip, VmLocs, env_cloud_role, Type, CountHosts
```

### Step 3: Ring Health Checks

```kql
// SlbCritical — detect Mux crashes
cluster('Azslb').database('azslbmds').SlbCritical
| where env_time between (datetime({StartTime}) .. datetime({EndTime}))
| where env_cloud_role == "{Ring}"
| project env_time, env_cloud_roleInstance, Critical, Message
| order by env_time asc
```

```kql
// SlbHealthEvent — data plane alerts
cluster('Azslb').database('azslbmds').SlbHealthEvent
| where env_time between (datetime({StartTime}) .. datetime({EndTime}))
| where env_cloud_role == "{Ring}"
| project env_time, env_cloud_roleInstance, HealthEventType, VipOrIlbCA, IsCustomerFacing, Description
| order by env_time asc
```

```kql
// NodeHealthEvent — Service Fabric node health
// ⚠️ Uses TIMESTAMP/Role/NodeName, NOT env_time/env_cloud_role
cluster('Azslb').database('azslbmds').NodeHealthEvent
| where TIMESTAMP between (datetime({StartTime}) .. datetime({EndTime}))
| where Role == "{Ring}"
| where HealthState in ('Error', 'Warning')
| project TIMESTAMP, NodeName, SourceId, HealthState, Description
| order by TIMESTAMP asc
```

```kql
// SlbException — Mux reconnection failures
cluster('Azslb').database('azslbmds').SlbException
| where env_time between (datetime({StartTime}) .. datetime({EndTime}))
| where env_cloud_role == "{Ring}"
| project env_time, env_cloud_roleInstance, Exception, Message
| order by env_time asc
```

```kql
// BGP Peer State
cluster('Azslb').database('azslbmds').BgpPeerStateSnapshotEvent
| where env_time between (datetime({StartTime}) .. datetime({EndTime}))
| where Ring == "{Ring}"
| where State != 'Established'
| project env_time, Node, MuxIP, PeerIP, State, RouteCount
```

```kql
// ToR Discards — rule out physical network
cluster('aznwnetmon').database('aznwmds').sXInterfaceTable
| where DeviceName == "{T0_DeviceName}"
| where PreciseTimeStamp between (datetime({StartTime}) .. datetime({EndTime}))
| where ifOutDiscards_Counter > 0 or ifInDiscards_Counter > 0
| project PreciseTimeStamp, DeviceName, ifName, ifOutDiscards_Counter, ifInDiscards_Counter
```

### Noisy Neighbor KQL (Scenario D)

```kql
// Find top NATGWs by connection count on a specific MNAT ring
let regionId = "{RegionShortId}";  // e.g., "bl" for eastus
let natRing  = "{MNAT_Ring}";
let startTime = datetime({StartTime});
let endTime   = datetime({EndTime});
let mnatSlice = toscalar(
    cluster("aznwsdn").database("aznwmds").SlbSliceInfo
    | where RegionShortId == regionId
    | where Rings contains natRing
    | summarize arg_max(DataIngestionTime, *) by SliceName
    | project SliceName);
let ringGateways = materialize(
    NatGatewayAllocation
    | where env_time > ago(1d) and env_cloud_name == regionId and NatSlice == mnatSlice
    | summarize arg_max(env_time, *) by NatGatewayId
    | extend gwId = replace_string(NatGatewayId, "NGW_", ""));
let mdmData = evaluate geneva_metrics_request(
    "slbv2{region}",
    'metricNamespace("NatService").metric("SNATConnectionCount").preaggregate("By-NatGatewayId-SnatVIP-Protocol-ConnectionState").samplingTypes("Sum") | zoom pktCountPerHour = sum(Sum) by 1h',
    startTime, endTime);
mdmData
| summarize pktCountPerHour = sum(tolong(pktCountPerHour)) by NatGatewayId, TimestampUtc
| where NatGatewayId in (ringGateways | project gwId)
| join kind=inner (ringGateways | project gwId, SnatIpAddresses, NatSlice, SliceVip, VnetId) on $left.NatGatewayId == $right.gwId
| extend pktCountPerHourInM = round(pktCountPerHour / 1000000.0, 2)
| order by pktCountPerHourInM desc
```

---

## 4. Dashboard Quick Reference

| Dashboard | Purpose | Shortlink | Key Params |
|-----------|---------|-----------|------------|
| **MNAT Ring Failed Probes** ⭐ | Pinpoint DP drop time | `s/F28AA3D` | Ring, account |
| **DIP Drop** | Rule out backend drops | `s/ED1F733C` | Ring, VipPort=65330, Protocol=UDP |
| **VIP Availability** | Which SLB Rings dropped | `s/F04A151C` | VipAddress (SNAT VIP) |
| **NATGW DP Overview** ⭐ | Find Noisy Neighbor (clear GW ID!) | `dashboard/slbv2/ManagedNat/ManagedNat%2520Metrics` | account, NatGatewayId=**empty** |
| **MuxStatsV2** ⭐ | Mux overload / drop evidence | `s/1EFA3C7A` | Ring, MDM accounts |
| **Ring Health** | Routes/MuxProber/SDN per node | `s/5820D435` | Ring, MDM accounts |
| **Worker Health** | NAT Worker node health (maintenance) | `s/6FAFB093` | Ring, account |
| **NAT Worker Stats** | SNAT allocation failures | `s/825D436E` | Ring, account |
| **Rate Limiting** | Rate-limit dropped packets | `s/2666D6C8` | Ring, account |
| **NATGW DataPath Avail** | Per-NATGW availability | `s/70F5B074` | NatGatewayId, account |
| **NATGW Throughput** | NATGW throughput metrics | `s/F372A89F` | NatGatewayId, account |

> **MDM Account naming**: External `slbv2{region}`, Internal `slbintv2{region}`  
> **Epoch ms formula** (KQL): `tolong(starttime-datetime(1970-01-01)) / 10000`

### Dashboard Link Templates

**Failed Probes** (`s/F28AA3D`):
```
https://portal.microsoftgeneva.com/s/F28AA3D?overrides=[
  {"query":"//dataSources[namespace='BandwidthUsage' or namespace='VipStats' or namespace='NatService' or namespace='Health' or namespace='DipHealth']","key":"account","replacement":"slbv2{region}"},
  {"query":"//dataSources[namespace!='BandwidthUsage' and namespace!='VipStats' and namespace!='NatService' and namespace!='Health' and namespace!='DipHealth']","key":"account","replacement":"slbv2{region}2euap"},
  {"query":"//*[id='Ring']","key":"value","replacement":"{Ring}"}
]&globalStartTime={epochMs}&globalEndTime={epochMs}&pinGlobalTimeRange=true
```

**DIP Drop** (`s/ED1F733C`):
```
https://portal.microsoftgeneva.com/dashboard/slbv2prod/AzureMonitor/DipAvailability_HealthProbeStatus?overrides=[
  {"query":"//dataSources","key":"account","replacement":"slbv2{region}"},
  {"query":"//*[id='Slbv2MDMAccount']","key":"value","replacement":"slbv2{region}"},
  {"query":"//*[id='Ring']","key":"value","replacement":"{Ring}"},
  {"query":"//*[id='VipPort']","key":"value","replacement":"65330"},
  {"query":"//*[id='ProtocolType']","key":"value","replacement":"UDP"},
  {"query":"//*[id='CaAddress']","key":"value","replacement":""},
  {"query":"//*[id='DipPort']","key":"value","replacement":""},
  {"query":"//*[id='DipAddress']","key":"value","replacement":""},
  {"query":"//*[id='HostAddress']","key":"value","replacement":""},
  {"query":"//*[id='LoadBalancerArmId']","key":"value","replacement":""},
  {"query":"//*[id='PublicIpArmId']","key":"value","replacement":""},
  {"query":"//*[id='VipAddress']","key":"value","replacement":""},
  {"query":"//*[id='AddressFamily']","key":"value","replacement":""}
]&globalStartTime={epochMs}&globalEndTime={epochMs}&pinGlobalTimeRange=true
```

**VIP Availability** (`s/F04A151C`):
```
https://portal.microsoftgeneva.com/dashboard/slbv2prod/AzureMonitor/VipAvailability_DataPathAvailability?overrides=[
  {"query":"//dataSources","key":"account","replacement":"slbv2{region}"},
  {"query":"//*[id='Slbv2MDMAccount']","key":"value","replacement":"slbv2{region}"},
  {"query":"//*[id='VipAddress']","key":"value","replacement":"{SNAT_VIP}"},
  {"query":"//*[id='Ring']","key":"value","replacement":""},
  {"query":"//*[id='AddressFamily']","key":"value","replacement":""},
  {"query":"//*[id='LoadBalancerArmId']","key":"value","replacement":""},
  {"query":"//*[id='PublicIpArmId']","key":"value","replacement":""},
  {"query":"//*[id='VnetId']","key":"value","replacement":""}
]&globalStartTime={epochMs}&globalEndTime={epochMs}&pinGlobalTimeRange=true
```

**Noisy Neighbor** (`dashboard/slbv2/ManagedNat/ManagedNat%2520Metrics`):
```
https://portal.microsoftgeneva.com/dashboard/slbv2/ManagedNat/ManagedNat%2520Metrics?overrides=[
  {"query":"//dataSources[namespace='BandwidthUsage' or namespace='VipStats' or namespace='NatService' or namespace='Health' or namespace='DipHealth']","key":"account","replacement":"slbv2{region}"},
  {"query":"//*[id='NatGatewayId']","key":"value","replacement":""}
]&globalStartTime={epochMs}&globalEndTime={epochMs}&pinGlobalTimeRange=true
```

**MuxStatsV2** (`s/1EFA3C7A`):
```
https://portal.microsoftgeneva.com/dashboard/slbv2prod/SlbQOS/RingHealth?overrides=[
  {"query":"//*[id='Ring']","key":"value","replacement":"{Ring}"},
  {"query":"//*[id='ClusterName']","key":"value","replacement":"{Ring}"},
  {"query":"//*[id='NodeId']","key":"value","replacement":""},
  {"query":"//dataSources[namespace='BandwidthUsage' or namespace='VipStats' or namespace='NatService' or namespace='Health' or namespace='DipHealth']","key":"account","replacement":"slbv2{region}"},
  {"query":"//dataSources[namespace!='BandwidthUsage' and namespace!='VipStats' and namespace!='NatService' and namespace!='Health' and namespace!='DipHealth']","key":"account","replacement":"slbintv2{region}"}
]&globalStartTime={epochMs}&globalEndTime={epochMs}&pinGlobalTimeRange=true
```

---

## 5. Scenario Details

### A: Mux Crash
- **Smoking gun**: `SlbCritical` → `Critical == "MuxShutdownUnexpected"`
- **Pattern**: Normal logs → complete silence (process dead) → `MuxUnifiedLwfDeviceControl` reinit on recovery
- **Pingmesh**: 0% but ToR links UP with zero errors

### B: Mux Overload (SAAFD Ring)
- **Smoking gun**: MuxStatsV2 shows `MuxDroppedPackets` increasing
- **Check**: `SlbMetadataVersionRecord` to confirm ring type
- **Fix**: SLB team increases core allocation for SAAFD rings

### C: Physical Network
- **Smoking gun**: `sXInterfaceTable` → `ifOutDiscards_Counter > 0`
- If ToR Discards = 0 → rule out physical network

### D: Noisy Neighbor (Mux Level)
- **Signature**: Multiple NATGWs drop simultaneously + shared SLB Ring
- **Key step**: NATGW DP Dashboard (`dashboard/slbv2/ManagedNat/ManagedNat%2520Metrics`) with **NatGatewayId cleared** → reveals traffic spike source
- **Confirmation**: MuxStatsV2 packets/sec spike (baseline ~300-400k → 2000k+ = overload)
- **Alt**: KQL query via `SlbSliceInfo` + `SNATConnectionCount` MDM to rank all NATGWs on ring

### E: Instance Maintenance (Rolling Update)
- **Signature**: Worker nodes drop to 0 **one by one** with ~5-10min intervals, then recover
- **Dashboard**: Worker Health (`s/6FAFB093`)
- **Confirm**: AutoDri / RepairTask records in azslbmds

### F: Single Node Isolation (ToR Reboot)
- **Signature**: Only **1 node** Routes drop to 0 + MuxProber availability drop on that node only
- **Dashboard**: Ring Health (`s/5820D435`) → Routes per mux, SDN Gateway failures
- **Key indicators**: `NotConnected MessageBus`, `NoRoute` spike, SDN Gateway `500` errors
- **RCA**: ToR reboot → server isolated → internal monitoring detects and reboots server

### G: SNAT Port Exhaustion
- **Signature**: `Nat Allocation Failures - No Space in Reused Ports` spike in NAT Worker Stats
- **Dashboard**: NAT Worker Stats (`s/825D436E`)
- **⚠️ Important**: This is a **ring-level shared resource** — one NATGW exhausting ports affects all NATGWs on same ring
- **Also a type of noisy neighbor** at NAT Worker layer (vs Scenario D at Mux layer)

### H: Rate Limiting
- **Signature**: `Rate-Limit RxPktsDropped/min` spike + ToR buffer overflow (OutDiscards on older hardware)
- **Dashboard**: Rate Limiting Counters (`s/2666D6C8`)
- **Default thresholds**: 50 Gbps BPS / 5 Mpps PPS per NatGateway per ring
- **Mitigation**: Reduce rate limit threshold or move high-traffic NATGW to ring with better ToR hardware
- **Note**: Mux (MNAT) itself handles ~300 Gbps; bottleneck is ToR buffer on older devices

---

## 6. Common Pitfalls

| # | Pitfall | Correct Approach |
|---|---------|-----------------|
| 1 | Searching AzureCM for Mux node state | Mux is Service Fabric managed — use `SlbCritical` / `NodeHealthEvent` |
| 2 | RoleInstance naming inconsistency | `SlbCritical`: `SlbRingHostRole_N`; `NodeHealthEvent`: `SlbRingHostRole.N` |
| 3 | Using `env_time` for `NodeHealthEvent` | Must use `TIMESTAMP` + `Role` / `NodeName` |
| 4 | Assuming Pingmesh 0% = network fault | If ToR UP + zero errors → likely Mux process crash |
| 5 | Not distinguishing SliceVip vs SNAT VIP | SliceVip = internal (outbound path); SNAT VIP = customer public IP (return path) |
| 6 | Treating `env_cloud_role` in VipMetadata as serving ring | `env_cloud_role` = reporting ring; **serving ring = MulticastGroup** |
| 7 | Only checking MNAT Ring, not SliceVip/SNAT VIP Rings | Must check all three layers |
| 8 | Filtering NatGatewayId when hunting noisy neighbor | Must **clear** NatGatewayId filter to see all NATGW traffic |
| 9 | Wrong year in Kusto timestamp | Current year is 2026; wrong year returns empty results |

---

## 7. RCA Templates

### Template A: Mux Overload / SAAFD

```
## Root Cause
NAT Gateway packet drops caused by SLB Mux overload on ring {ringName} (SAAFD type)
hosting the SliceVIP.

### Details
- NAT Gateway: {name} (Sub: {subId})
- SliceVip: {sliceVip}, MNAT Ring: {ringName}
- MuxStatsV2 showed dropped packets increase during {timerange}
- ToR links: zero discards/errors (physical network excluded)
- No Mux crash detected (SlbCritical clean)

### Mitigation
SLB team increasing core allocation for SAAFD rings.
```

### Template B: Noisy Neighbor

```
## Root Cause
NAT Gateway packet drops caused by noisy neighbor on shared SLB Ring.

### Details
- Affected: {name1}, {name2}
- Noisy Neighbor: {neighbor_name} (Sub: {neighbor_subId}, GW: {neighbor_gwId})
- Affected Rings: {ring1}, {ring2}, {ring3}
- MuxStatsV2: packets/sec spiked from {baseline}k to {peak}k ({multiplier}x)

### Evidence
1. Both NATGWs showed Failed Probes spike at {time}
2. DIP layer: zero drops (backend excluded)
3. VIP Availability dropped to {X}% on affected rings
4. NATGW DP Dashboard (unfiltered) identified noisy neighbor
5. MuxStatsV2 confirmed Mux overload

### Mitigation
{DDoS mitigation / traffic normalized / ring capacity rebalanced}
```

### Template C: Node Isolation

```
## Root Cause
NAT Gateway datapath degradation caused by server isolation after ToR reboot.

### Details
- Ring: {ringName}, Affected Node: {nodeId}
- Routes dropped to 0 on single node; MuxProber availability: {X}%
- MessageBus: NotConnected; SDN Gateway: 500 errors

### Mitigation
Internal monitoring detected isolated server and initiated reboot.
```
