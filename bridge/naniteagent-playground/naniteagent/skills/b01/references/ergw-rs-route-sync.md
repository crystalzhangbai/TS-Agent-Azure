---
description: KQL queries for investigating ERGW-to-RouteServer route synchronization issues — NextHop discrepancy, GRPC route delivery, adjacency table comparison.
---

# ERGW ↔ Route Server Route Sync Investigation

> Source: Kusto — hybridnetworking.kusto.windows.net / aznwmds
> Use Case: When ERGW advertises N NextHops for an on-prem route via GRPC, but Route Server Adjacency table shows fewer NextHops.

## When to Use

- VM effective route shows fewer NextHops than expected for an ExpressRoute on-prem prefix
- ERGW adjacency table has more NextHops than Route Server adjacency table
- Route Server adjacency table missing a specific NextHop (e.g., after new MSEE peer added)
- After BGP flap between ERGW and MSEE, Route Server adjacency changed

## Prerequisites — Get GatewayId and RouteServiceId

### Step 1: Get ERGW GatewayId

```kql
let starttime = _startTime;
let endtime = _endTime;
let subscriptionid = SubscriptionID;
let gwname = ErGwName;
cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantHealth
| where PreciseTimeStamp >= starttime - 1d and PreciseTimeStamp <= endtime
| where CustomerSubscriptionId == subscriptionid
| where GatewayType == "Dedicated"
| where GatewayName == gwname
| distinct GatewayId
```

### Step 2: Get RouteServiceId (from RouteServiceLogsTable)

```kql
let starttime = _startTime;
let endtime = _endTime;
let target_prefix = '10.110.0.0'; // replace with target prefix
cluster('hybridnetworking.kusto.windows.net').database('aznwmds').RouteServiceLogsTable
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where Message contains target_prefix
| where Message contains 'LogAdjacencies'
| distinct RouteServiceId
```

## Investigation Steps

### Step 1: Check ERGW Adjacency Table — How many NextHops does ERGW have?

Shows the ERGW internal adjacency table for a specific on-prem prefix, including all MSEE NextHops.

```kql
let starttime = _startTime;
let endtime = _endTime;
let gatewayid = GatewayId;
let target_prefix = '10.110.0.0'; // replace with target prefix
cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where GatewayId == gatewayid
| where Message startswith '<BGP> Updated adjacency table'
| where Message contains target_prefix
| project PreciseTimeStamp, RoleInstance, Message
| extend Route = extract(strcat(replace_string(target_prefix, '.', '\\.'), '/\\d+ -> \\[(.+?)\\]'), 1, Message)
| where isnotempty(Route)
| extend HopCount = countof(Route, 'NextHopAddress')
| project PreciseTimeStamp, RoleInstance, HopCount, Route
| order by PreciseTimeStamp asc
```

### Step 2: Check ERGW GRPC SendRouteToRS — What did ERGW send to Route Server?

Shows each GRPC route update that ERGW sent to Route Server. Each ERGW instance (IN_0, IN_1) sends separately.

```kql
let starttime = _startTime;
let endtime = _endTime;
let gatewayid = GatewayId;
let target_prefix = '10.110.0.0'; // replace with target prefix
cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where GatewayId == gatewayid
| where Message contains 'SendRouteToRS' and Message contains target_prefix
| project PreciseTimeStamp, RoleInstance, Message
| order by PreciseTimeStamp asc
```

### Step 3: Check Route Server Received GRPC Routes — Did RS receive the routes?

Shows how Route Server processed the incoming GRPC routes from ERGW.

```kql
let starttime = _startTime;
let endtime = _endTime;
let rsid = RouteServiceId;
let target_prefix = '10.110.0.0'; // replace with target prefix
cluster('hybridnetworking.kusto.windows.net').database('aznwmds').RouteServiceRoutingLog
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where RouteServiceId contains rsid
| where Message contains target_prefix
| where Message contains 'Grpc route'
| project TIMESTAMP, RoleInstance, Message
| order by TIMESTAMP asc
```

### Step 4: Check Route Server OnGrpcRouteExportEvent — Route count per MSEE peer

This is the key diagnostic. Shows all GRPC routes RS has for a prefix. Each MSEE peer should have **2 copies** (one from each ERGW instance IN_0 and IN_1). If a peer has only 1 copy, RS may not include its NextHop in the adjacency table.

```kql
let starttime = _startTime;
let endtime = _endTime;
let rsid = RouteServiceId;
let target_prefix = '10.110.0.0'; // replace with target prefix
cluster('hybridnetworking.kusto.windows.net').database('aznwmds').RouteServiceRoutingLog
| where TIMESTAMP >= starttime and TIMESTAMP <= endtime
| where RouteServiceId contains rsid
| where Message contains 'OnGrpcRouteExportEvent' and Message contains target_prefix
| project TIMESTAMP, RoleInstance, Message
| order by TIMESTAMP asc
```

**How to read the output:**
```
"10.110.0.0/16": ["10.14.1.6","10.14.1.6",     ← ×2 (normal)
                   "10.14.1.10","10.14.1.10",   ← ×2 (normal)
                   "10.14.1.18"]                 ← ×1 (abnormal — may cause missing NextHop in ADJ)
```

### Step 5: Check Route Server Adjacency Table — What NextHops does RS have?

Shows the RS adjacency table (LogAdjacencies) which is what VM effective routes are based on.

```kql
let starttime = _startTime;
let endtime = _endTime;
let rsid = RouteServiceId;
let target_prefix = '10.110.0.0'; // replace with target prefix
cluster('hybridnetworking.kusto.windows.net').database('aznwmds').RouteServiceLogsTable
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where RouteServiceId contains rsid
| where Message contains target_prefix and Message contains 'LogAdjacencies'
| project PreciseTimeStamp, RoleInstance, Message
| order by PreciseTimeStamp desc
```

### Step 6: Check ERGW BGP Flap — Was there a BGP reconvergence event?

BGP flaps between ERGW and MSEE peers can trigger route re-advertisement which may fix or change the RS adjacency.

```kql
let starttime = _startTime;
let endtime = _endTime;
let gatewayid = GatewayId;
let target_prefix = '10.110.0.0'; // replace with target prefix
cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where GatewayId == gatewayid
| where Message startswith '<BGP> Updated adjacency table'
| where Message contains target_prefix
| project PreciseTimeStamp, RoleInstance, Message
| extend Route = extract(strcat(replace_string(target_prefix, '.', '\\.'), '/\\d+ -> \\[(.+?)\\]'), 1, Message)
| where isnotempty(Route)
| extend HopCount = countof(Route, 'NextHopAddress')
| summarize FirstSeen=min(PreciseTimeStamp), LastSeen=max(PreciseTimeStamp), Count=count() by HopCount
| order by FirstSeen asc
```

### Step 7: Check ERGW Peer Registration — When was the MSEE peer registered?

Shows when a specific MSEE peer was registered on the ERGW with its NextHop mapping.

```kql
let starttime = _startTime;
let endtime = _endTime;
let gatewayid = GatewayId;
let msee_peer = '10.14.1.18'; // replace with target MSEE peer IP
cluster('hybridnetworking.kusto.windows.net').database('aznwmds').GatewayTenantLogsTable
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where GatewayId == gatewayid
| where Message contains msee_peer and (Message contains 'Peer:' or Message contains 'PeerNexthopMapping')
| project PreciseTimeStamp, RoleInstance, Message
| order by PreciseTimeStamp asc
```

### Step 8: Track specific NextHop in Route Server — When did it appear/disappear?

Tracks when a specific NextHop (encap address) first appeared or disappeared in the RS adjacency table.

```kql
let starttime = _startTime;
let endtime = _endTime;
let rsid = RouteServiceId;
let target_prefix = '10.110.0.0'; // replace with target prefix
let target_nexthop = '10.63.111.5'; // replace with the NextHop to track
cluster('hybridnetworking.kusto.windows.net').database('aznwmds').RouteServiceLogsTable
| where PreciseTimeStamp >= starttime and PreciseTimeStamp <= endtime
| where RouteServiceId contains rsid
| where Message contains target_prefix and Message contains 'LogAdjacencies'
| project PreciseTimeStamp, RoleInstance, HasTargetNH = Message contains target_nexthop
| order by PreciseTimeStamp asc
```

## Data Flow Reference

```
On-Premise → MSEE peers → ERGW (BGP) → Route Server (GRPC) → VM (effective routes)
                            │                    │
                     GatewayTenantLogsTable   RouteServiceRoutingLog
                     (SendRouteToRS)          (OnGrpcRouteExportEvent)
                     (Updated adjacency)      (LogAdjacencies)
```

## Key Tables

| Table | Content | Used For |
|-------|---------|----------|
| `GatewayTenantLogsTable` | ERGW internal logs — BGP, adjacency updates, GRPC sends | Steps 1, 2, 6, 7 |
| `GatewayTenantHealth` | ERGW metadata — GatewayId lookup | Prerequisites |
| `RouteServiceRoutingLog` | RS routing decisions — GRPC route received, OnGrpcRouteExportEvent | Steps 3, 4 |
| `RouteServiceLogsTable` | RS system logs — LogAdjacencies (final adjacency table) | Steps 5, 8 |

## Known Behavior

- ERGW has 2 instances (IN_0 and IN_1). Each sends GRPC routes to RS independently.
- RS `OnGrpcRouteExportEvent` should show **2 copies** per MSEE peer (one from each ERGW instance).
- If a MSEE peer has only **1 copy** in `OnGrpcRouteExportEvent`, its NextHop may not appear in the RS adjacency table.
- After a BGP flap, ERGW re-sends all routes in a batch, which may resolve the discrepancy.
