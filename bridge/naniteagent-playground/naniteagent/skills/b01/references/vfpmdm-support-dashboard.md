# VfpMDM dpop Support Dashboard — Tile Reference

**Dashboard:** `VfpMDM / dpop/SupportDashboard`  
**Source JSON:** `VfpMDM_dpop_SupportDashboard.json`  
**Total Tiles:** `31`

## Template Parameters

| Name | Display Name | Type | Default / Example | Used As | Affected Tiles | Hint Query |
|------|-------------|------|-------------------|---------|----------------|------------|
| `Account` | Account | string | ` (all) ` → e.g. `VfpMdmAM` | MDM `account` field override on all MDM data sources (`//dataSources`) | All MDM tiles | Pattern filter `VfpMdm*` |
| `ContainerId` | ContainerId | string | *(empty)* | Dimension filter `ContainerId` = `{ContainerId}` (override key `value` on `//*[id='ContainerId']`) | MDM tiles with `VfpPort*` namespaces (1, 2, 11, 13, 14, 15, 17, 20, 27, 29, 30, 31) | MDM dimension `ContainerId` from `VfpMdmAM / VfpPortTcpMetrics / FinPacketsInRate` |
| `NodeId` | NodeId | string | *(empty)* | Dimension filter `NodeId` = `{NodeId}` (override key `value` on `//*[id='NodeId']`); KQL substitution in Kusto tiles | All MDM tiles and Kusto tiles 22–23 | MDM dimension `NodeId` from `VfpMdmBN / FPGA-CONFIG / IsGolden` |
| `Cluster` | Cluster | string | ` (all) ` | Dimension filter `Cluster` = `{Cluster}` (override key `value` on `//*[id='Cluster']`) | All MDM tiles | MDM dimension `Cluster` from `VfpMdmBN / FPGA-CONFIG / IsGolden` |

> ⚠️ Tiles marked **** must NOT be shared with external customers.

---

## Tile 1 — TCP Inbound Connection Establishment

| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VfpPortTcpMetrics` |
| **Metric(s)** | `TcpSynPacketInRate`, `TcpSynAckPacketOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`; `NodeId` = `{NodeId}`; `ContainerId` = `{ContainerId}` *(runtime-substituted when provided)* |
| **Split By** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---

## Tile 2 — TCP Outbound Connection Establishment

| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VfpPortTcpMetrics` |
| **Metric(s)** | `TcpSynPacketOutRate`, `TcpSynAckPacketInRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`; `NodeId` = `{NodeId}`; `ContainerId` = `{ContainerId}` *(runtime-substituted when provided)* |
| **Split By** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---

## Tile 3 — Portal Bytes / Packets

| Field | Value |
|-------|-------|
| **Type** | HTML |
| **Content** | Describes total packets and bytes observed through AccelNet and the VFP stack per minute for each vPort. |

---

## Tile 4 — FPGA GFT Healthy

| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmBN`) |
| **MDM Namespace** | `FPGA-GFT` |
| **Metric(s)** | `FPGAGftHealthy` |
| **Sampling Type** | Healthy |
| **Dimension Filter** | `Cluster` = `{Cluster}`; `NodeId` = `{NodeId}` *(runtime-substituted when provided)* |
| **Split By** | `Cluster`, `NodeId` |

---

## Tile 5 — TCP Connection Establishment

| Field | Value |
|-------|-------|
| **Type** | HTML |
| **Content** | Explains how `TcpSynPacket{In/Out}Rate` and `TcpSynAckPacket{In/Out}Rate` indicate inbound and outbound TCP connection setup behavior. |

---

## Tile 6 — FPGA-CONFIG (IsGolden)

| Field | Value |
|-------|-------|
| **Type** | HTML |
| **Content** | Notes that `IsGolden` must be `0` for AccelNet to function correctly on production nodes. |

---

## Tile 7 — VFP Flows Description

| Field | Value |
|-------|-------|
| **Type** | HTML |
| **Content** | Explains `CurrentTotalFlowEntryIn/Out` and `CreatedTotalFlowEntryIn/OutRate` as current and newly created VFP flow counts. |

---

## Tile 8 — FPGA-CONFIG (IsGolden)

| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmBN`) |
| **MDM Namespace** | `FPGA-CONFIG` |
| **Metric(s)** | `IsGolden` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`; `NodeId` = `{NodeId}` *(runtime-substituted when provided)* |
| **Split By** | `Cluster`, `NodeId` |

---

## Tile 9 — FPGA GFT Healthy Description

| Field | Value |
|-------|-------|
| **Type** | HTML |
| **Content** | Explains `FPGAGftHealthy` and that a value of `1` indicates the FPGA GFT path is healthy with no detected errors. |

---

## Tile 10 — VMSwitch Dropped Packets Description

| Field | Value |
|-------|-------|
| **Type** | HTML |
| **Content** | Explains `ResourceDropInRate` as packets dropped because the VMSwitch could not deliver them to the guest VM. |

---

## Tile 11 — Outbound VFP Flows

| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VfpPortFlowStats` |
| **Metric(s)** | `CurrentTotalFlowEntryOut`, `CreatedTotalFlowEntryOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`; `NodeId` = `{NodeId}`; `ContainerId` = `{ContainerId}` *(runtime-substituted when provided)* |
| **Split By** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---

## Tile 12 — DroppedFragPacketInRate

| Field | Value |
|-------|-------|
| **Type** | HTML |
| **Content** | Explains that VFP drops fragmented UDP packets by design and points engineers to the UDP Fragmentation TSG for validation guidance. |

---

## Tile 13 — Inbound VFP Flows

| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VfpPortFlowStats` |
| **Metric(s)** | `CurrentTotalFlowEntryIn`, `CreatedTotalFlowEntryInRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`; `NodeId` = `{NodeId}`; `ContainerId` = `{ContainerId}` *(runtime-substituted when provided)* |
| **Split By** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---

## Tile 14 — DroppedFragPacketInRate

| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VfpPortDropMetrics` |
| **Metric(s)** | `DroppedFragPacketInRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`; `NodeId` = `{NodeId}`; `ContainerId` = `{ContainerId}` *(runtime-substituted when provided)* |
| **Split By** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---

## Tile 15 — VFP Ratelimiter Drops (inbound / outbound)

| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VfpPortMetrics` |
| **Metric(s)** | `SlowPathPacketsDroppedInRate`, `SlowPathPacketsDroppedOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`; `NodeId` = `{NodeId}`; `ContainerId` = `{ContainerId}` *(runtime-substituted when provided)* |
| **Split By** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |
| **Operational Note** | If this tile is red, ask the customer to scale up the VM size. Do **not** disclose internal rate-limit thresholds. |

---

## Tile 16 — VMSwitch Extension Dropped Packets Description

| Field | Value |
|-------|-------|
| **Type** | HTML |
| **Content** | Explains `DroppedAclPacketInRate` and `DroppedAclPacketOutRate` as packets dropped by customer-configured VFP ACL rules. |

---

## Tile 17 — DroppedFragPacketOutRate

| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VfpPortDropMetrics` |
| **Metric(s)** | `DroppedFragPacketOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`; `NodeId` = `{NodeId}`; `ContainerId` = `{ContainerId}` *(runtime-substituted when provided)* |
| **Split By** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---

## Tile 18 — VMSwitch Dropped Packets

| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VmsNicDropMetrics` |
| **Metric(s)** | `ResourceDropInRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`; `NodeId` = `{NodeId}` *(runtime-substituted when provided)* |
| **Split By** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---

## Tile 19 — RDMA

| Field | Value |
|-------|-------|
| **Type** | HTML |
| **Content** | Describes the RDMA Success/Failure and RDMA Client Latency tiles, including how to interpret operation status and latency percentiles. |

---

## Tile 20 — VFP ACL drops (inbound / outbound)

| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VfpPortDropMetrics` |
| **Metric(s)** | `DroppedAclPacketInRate`, `DroppedAclPacketOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`; `NodeId` = `{NodeId}`; `ContainerId` = `{ContainerId}` *(runtime-substituted when provided)* |
| **Split By** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---

## Tile 21 — Packet Errors

| Field | Value |
|-------|-------|
| **Type** | HTML |
| **Content** | Links to the FCS errors troubleshooting content on eng.ms for investigating packet corruption and related network error counters. |

---

## Tile 22 — RDMA Success/Failure Rate

| Field | Value |
|-------|-------|
| **Type** | Kusto chart |
| **Data Source** | Kusto |
| **Cluster** | `netperf.kusto.windows.net` |
| **Database** | `NetPerfKustoDB` |
| **Table(s)** | `EStatsClientLatencyPerApp` |
| **Parameter Tokens** | `{NodeId}`, `{startTime}`, `{endTime}` |

**Key KQL logic:**
```kql
// {NodeId} = runtime value from template parameter
// {startTime}, {endTime} = dashboard time range
let impactedNodeId = "{NodeId}";
let impactStartTime = datetime({startTime});
let impactEndTime = datetime({endTime});
cluster('Netperf').database('NetPerfKustoDB').EStatsClientLatencyPerApp
| where NodeId =~ impactedNodeId
| where PreciseTimeStamp >= impactStartTime and PreciseTimeStamp <= impactEndTime
| summarize SuccessCount=countif(OperationStatus == 'SUCCESS'), FailureCount=countif(OperationStatus != 'SUCCESS') by PreciseTimeStamp, NodeId
| summarize SuccessfulOperations=sum(SuccessCount), FailedOperations=sum(FailureCount) by bin(PreciseTimeStamp, 1m)
```

---

## Tile 23 — RDMA Client Latency (in microseconds)

| Field | Value |
|-------|-------|
| **Type** | Kusto chart |
| **Data Source** | Kusto |
| **Cluster** | `netperf.kusto.windows.net` |
| **Database** | `NetPerfKustoDB` |
| **Table(s)** | `EStatsClientLatencyPerApp` |
| **Parameter Tokens** | `{NodeId}`, `{startTime}`, `{endTime}` |

**Key KQL logic:**
```kql
// {NodeId} = runtime value from template parameter
// {startTime}, {endTime} = dashboard time range
let impactedNodeId = "{NodeId}";
let impactStartTime = datetime({startTime});
let impactEndTime = datetime({endTime});
cluster('netperf.kusto.windows.net').database('NetPerfKustoDB').EStatsClientLatencyPerApp
| where NodeId =~ impactedNodeId
| where PreciseTimeStamp >= impactStartTime and PreciseTimeStamp <= impactEndTime
| where OperationStatus == 'SUCCESS'
| summarize avg(P50), avg(P90), avg(P99), avg(P99_9), avg(P99_99) by bin(PreciseTimeStamp, 1m)
```

---

## Tile 24 — FPGA FCS Errors

| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmBN`) |
| **MDM Namespace** | `FPGA-NETWORK`, `FPGA-NETWORK-V2` |
| **Metric(s)** | `TOR-Receive-FCS-Error`, `NIC-Receive-FCS-Error`, `Short-Cable-FCS-Error-Rate`, `MAC0-Receive-FCS-Error`, `MAC1-Receive-FCS-Error` |
| **Sampling Type** | `Sum` for `TOR-Receive-FCS-Error`, `NIC-Receive-FCS-Error`; `Rate` for `Short-Cable-FCS-Error-Rate`, `MAC0-Receive-FCS-Error`, `MAC1-Receive-FCS-Error` |
| **Dimension Filter** | `Cluster` = `{Cluster}`; `NodeId` = `{NodeId}` *(runtime-substituted when provided)* |
| **Split By** | `Cluster`, `MacAddress`, `NodeId`, `VNetId` |

---

## Tile 25 — NIC Errors

| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmBN`) |
| **MDM Namespace** | `MlnxAdapterCounters`, `Mlx5TrafficCounters`, `GdmaBnicGlobalMetrics` |
| **Metric(s)** | `MlnxAdapterCounters`: `Packets_Received_Errors_Rate`, `Packets_Received_Frame_Length_Error_Rate`, `Packets_Received_Bad_CRC_Error_Rate`, `Packets_Received_Symbol_Error_Rate`; `Mlx5TrafficCounters`: `Packets_Received_Errors`, `Packets_Received_Symbol_Error`, `Packets_Received_Bad_CRC_Error`; `GdmaBnicGlobalMetrics`: `InTotalErrors`, `NumOfInErrorsRxVportDisabled`, `NumOfInErrorsSteeringUcast`, `NumOfInErrorsSteeringMcast` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`; `NodeId` = `{NodeId}` *(runtime-substituted when provided)* |
| **Split By** | `Cluster`, `MacAddress`, `NodeId`, `VNetId` |

---

## Tile 26 — Port timer duration errors

| Field | Value |
|-------|-------|
| **Type** | HTML |
| **Content** | Links to `aka.ms/vfpporttimertsg` for investigating abnormal VFP port timer duration and run-count behavior. |

---

## Tile 27 — Portal Bytes and Packets

| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VfpPortMetrics` |
| **Metric(s)** | `TotalPortalBytesInRate`, `TotalPortalBytesOutRate`, `TotalPortalPacketsInRate`, `TotalPortalPacketsOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`; `NodeId` = `{NodeId}`; `ContainerId` = `{ContainerId}` *(runtime-substituted when provided)* |
| **Split By** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---

## Tile 28 — Host Datapath (VFP) Dashboard

| Field | Value |
|-------|-------|
| **Type** | HTML |
| **Content** | Welcome tile describing the Host Datapath (VFP) Support Dashboard and the main investigation areas covered by the dashboard. |

---

## Tile 29 — Port Timer run count

| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VfpPortTimerMetrics` |
| **Metric(s)** | `PortTimerRunCount` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`; `NodeId` = `{NodeId}`; `ContainerId` = `{ContainerId}` *(runtime-substituted when provided)* |
| **Split By** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |
| **Operational Note** | If unhealthy at time of impact for the relevant container, follow `aka.ms/vfpporttimertsg`. |

---

## Tile 30 — Port Timer (average)

| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VfpPortTimerMetrics` |
| **Metric(s)** | `PortTimerDurationAverage` |
| **Sampling Type** | Average |
| **Dimension Filter** | `Cluster` = `{Cluster}`; `NodeId` = `{NodeId}`; `ContainerId` = `{ContainerId}` *(runtime-substituted when provided)* |
| **Split By** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |
| **Operational Note** | If unhealthy at time of impact for the relevant container, follow `aka.ms/vfpporttimertsg`. |

---

## Tile 31 — Port Timer (max)

| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VfpPortTimerMetrics` |
| **Metric(s)** | `PortTimerDurationMaximum` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`; `NodeId` = `{NodeId}`; `ContainerId` = `{ContainerId}` *(runtime-substituted when provided)* |
| **Split By** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |
| **Operational Note** | If unhealthy at time of impact for the relevant container, follow `aka.ms/vfpporttimertsg`. |

## Summary Table

| # | Tile Title | Source | Metrics / Tables | Confidential |
|---|-----------|--------|-----------------|:------------:|
| 1 | TCP Inbound Connection Establishment | MDM `VfpPortTcpMetrics` | `TcpSynPacketInRate`, `TcpSynAckPacketOutRate` | |
| 2 | TCP Outbound Connection Establishment | MDM `VfpPortTcpMetrics` | `TcpSynPacketOutRate`, `TcpSynAckPacketInRate` | |
| 3 | Portal Bytes / Packets | HTML | AccelNet and VFP portal bytes/packets description | |
| 4 | FPGA GFT Healthy | MDM `FPGA-GFT` | `FPGAGftHealthy` | |
| 5 | TCP Connection Establishment | HTML | TCP SYN / SYN-ACK explanation | |
| 6 | FPGA-CONFIG (IsGolden) | HTML | `IsGolden` guidance | |
| 7 | VFP Flows Description | HTML | VFP flow metrics explanation | |
| 8 | FPGA-CONFIG (IsGolden) | MDM `FPGA-CONFIG` | `IsGolden` | |
| 9 | FPGA GFT Healthy Description | HTML | `FPGAGftHealthy` explanation | |
| 10 | VMSwitch Dropped Packets Description | HTML | `ResourceDropInRate` explanation | |
| 11 | Outbound VFP Flows | MDM `VfpPortFlowStats` | `CurrentTotalFlowEntryOut`, `CreatedTotalFlowEntryOutRate` | |
| 12 | DroppedFragPacketInRate | HTML | UDP fragmentation behavior and TSG link | |
| 13 | Inbound VFP Flows | MDM `VfpPortFlowStats` | `CurrentTotalFlowEntryIn`, `CreatedTotalFlowEntryInRate` | |
| 14 | DroppedFragPacketInRate | MDM `VfpPortDropMetrics` | `DroppedFragPacketInRate` | |
| 15 | VFP Ratelimiter Drops | MDM `VfpPortMetrics` | `SlowPathPacketsDroppedInRate`, `SlowPathPacketsDroppedOutRate` | |
| 16 | VMSwitch Extension Dropped Packets Description | HTML | ACL drop explanation | |
| 17 | DroppedFragPacketOutRate | MDM `VfpPortDropMetrics` | `DroppedFragPacketOutRate` | |
| 18 | VMSwitch Dropped Packets | MDM `VmsNicDropMetrics` | `ResourceDropInRate` | |
| 19 | RDMA | HTML | RDMA latency and success/failure description | |
| 20 | VFP ACL drops | MDM `VfpPortDropMetrics` | `DroppedAclPacketInRate`, `DroppedAclPacketOutRate` | |
| 21 | Packet Errors | HTML | FCS errors TSG link | |
| 22 | RDMA Success/Failure Rate | Kusto `netperf.kusto.windows.net/NetPerfKustoDB` | `EStatsClientLatencyPerApp` | |
| 23 | RDMA Client Latency | Kusto `netperf.kusto.windows.net/NetPerfKustoDB` | `EStatsClientLatencyPerApp` | |
| 24 | FPGA FCS Errors | MDM `FPGA-NETWORK`, `FPGA-NETWORK-V2` | FCS error metrics across TOR/NIC/MAC | |
| 25 | NIC Errors | MDM `MlnxAdapterCounters`, `Mlx5TrafficCounters`, `GdmaBnicGlobalMetrics` | NIC receive and steering error metrics | |
| 26 | Port timer duration errors | HTML | `aka.ms/vfpporttimertsg` link | |
| 27 | Portal Bytes and Packets | MDM `VfpPortMetrics` | Portal bytes and packet rate metrics | |
| 28 | Host Datapath (VFP) Dashboard | HTML | Dashboard welcome/overview content | |
| 29 | Port Timer run count | MDM `VfpPortTimerMetrics` | `PortTimerRunCount` | |
| 30 | Port Timer (average) | MDM `VfpPortTimerMetrics` | `PortTimerDurationAverage` | |
| 31 | Port Timer (max) | MDM `VfpPortTimerMetrics` | `PortTimerDurationMaximum` | |
