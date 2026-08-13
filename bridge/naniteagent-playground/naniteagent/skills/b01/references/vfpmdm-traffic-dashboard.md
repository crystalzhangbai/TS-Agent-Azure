# VfpMDM dpop TrafficDashboard — Tile Reference

**Dashboard:** `VfpMDM / dpop/TrafficDashboard`  
**Tile Counts:** 24 total — 10 MDM, 14 HTML / static, 0 Kusto, 0 Mixed

## Template Parameters

| Name | Display Name | Type | Default / Example | Used As | Affected Tiles |
|------|-------------|------|-------------------|---------|----------------|
| `Account` | Account | string | *(empty)* → e.g. `VfpMdmAM` | MDM `account` field override | All MDM tiles |
| `Cluster` | Cluster | string | ` (all) ` | Dimension filter `Cluster` | All MDM tiles |
| `NodeId` | NodeId | string | *(empty)* | Dimension filter `NodeId` | All MDM tiles |
| `ContainerId` | ContainerId | string | *(empty)* | Dimension filter `ContainerId` | Tiles 20, 22 |

**Hint queries / resolvers:**
- `Account` — pattern filter `VfpMdm*`
- `Cluster` — MDM hint from `VfpMdmBN / FPGA-CONFIG / IsGolden`, dimension `Cluster`
- `NodeId` — MDM hint from `VfpMdmBN / FPGA-CONFIG / IsGolden`, dimension `NodeId`
- `ContainerId` — MDM hint from `VfpMdmAM / VfpPortTcpMetrics / FinPacketsInRate`, dimension `ContainerId`

> ⚠️ This reference may include internal-only details; do not share externally without review.

---

## Tile 1 — VFP Drops
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Content** | Section header / description tile for the VFP drops area of the broader datapath dashboard set. |

---

## Tile 2 — FPGA-PFC Packets Sent
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `FPGA-PFC` |
| **Metric(s)** | `NicNumPfcPacketsRx`, `TorNumPfcPacketsTx` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}` *(runtime-substituted from template parameter)*, `NodeId` = `{NodeId}` *(runtime-substituted from template parameter)* |
| **Output Columns** | `Cluster`, `NodeId`, `NodeIP` |

---

## Tile 3 — FPGA-PFC Packets Outbound - Description
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Content** | Describes outbound FPGA / PFC packet flow and explains NIC/TOR PFC packet counters. |

---

## Tile 4 — (no title)
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Content** | Section header / descriptive tile for virtual NIC metrics. |

---

## Tile 5 — (no title)
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Content** | Section header / descriptive tile for Mellanox NIC metrics. |

---

## Tile 6 — Packets Sent/Received (pNIC) Description
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Content** | Explains Physical NIC packet and byte receive counters used by the pNIC traffic tiles. |

---

## Tile 7 — Packets/Bytes Received (pNIC)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `PhysicalNicMetrics` |
| **Metric(s)** | `PacketsReceivedRate`, `BytesReceivedRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}` *(runtime-substituted from template parameter)*, `NodeId` = `{NodeId}` *(runtime-substituted from template parameter)* |
| **Output Columns** | `Cluster`, `MacAddress`, `NodeId`, `NodeIP` |

---

## Tile 8 — Bytes Sent/Received (pNIC) Description
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Content** | Explains Physical NIC byte and packet send counters used by the pNIC traffic tiles. |

---

## Tile 9 — Packets/Bytes Sent (pNIC)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `PhysicalNicMetrics` |
| **Metric(s)** | `PacketsSentRate`, `BytesSentRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}` *(runtime-substituted from template parameter)*, `NodeId` = `{NodeId}` *(runtime-substituted from template parameter)* |
| **Output Columns** | `Cluster`, `MacAddress`, `NodeId`, `NodeIP` |

---

## Tile 10 — Packets Sent/Received (vNIC) Description
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Content** | Explains virtual NIC packet receive / send counters used by the vNIC traffic tiles. |

---

## Tile 11 — Packets Sent/Received (vNIC)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VirtualNicMetrics` |
| **Metric(s)** | `PacketsReceivedRate`, `PacketsSentRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}` *(runtime-substituted from template parameter)*, `NodeId` = `{NodeId}` *(runtime-substituted from template parameter)* |
| **Output Columns** | `Cluster`, `MacAddress`, `NodeId`, `NodeIP` |

---

## Tile 12 — Bytes Sent/Received (vNIC) Description
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Content** | Explains virtual NIC byte receive / send counters used by the vNIC throughput tiles. |

---

## Tile 13 — Bytes Sent/Received (vNIC)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VirtualNicMetrics` |
| **Metric(s)** | `BytesReceivedRate`, `BytesSentRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}` *(runtime-substituted from template parameter)*, `NodeId` = `{NodeId}` *(runtime-substituted from template parameter)* |
| **Output Columns** | `Cluster`, `MacAddress`, `NodeId`, `NodeIP` |

---

## Tile 14 — Packets/Bytes Received (Mellanox NIC)
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Content** | Section header / description for Mellanox NIC receive-side metrics and counter semantics. |

---

## Tile 15 — Mellanox NIC counters Description
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Content** | Explains Mellanox NIC sent / received packet and byte counter meanings across the two namespaces. |

---

## Tile 16 — Packets/Bytes Received (Mellanox NIC)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `MlnxAdapterCounters`, `Mlx5TrafficCounters` |
| **Metric(s)** | `MlnxAdapterCounters`: `Bytes_Received_Rate`, `Packets_Received_Rate`; `Mlx5TrafficCounters`: `Bytes_Received`, `Packets_Received` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}` *(runtime-substituted from template parameter)*, `NodeId` = `{NodeId}` *(runtime-substituted from template parameter)* |
| **Output Columns** | `Cluster`, `IsBeNic`, `NicIp`, `NodeId`, `NodeIp` |

---

## Tile 17 — Packets/Bytes Sent (Mellanox NIC)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `MlnxAdapterCounters`, `Mlx5TrafficCounters` |
| **Metric(s)** | `MlnxAdapterCounters`: `Packets_Sent_Rate`, `Bytes_Sent_Rate`; `Mlx5TrafficCounters`: `Bytes_Sent`, `Packets_Sent` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}` *(runtime-substituted from template parameter)*, `NodeId` = `{NodeId}` *(runtime-substituted from template parameter)* |
| **Output Columns** | `Cluster`, `IsBeNic`, `NicIp`, `NodeId`, `NodeIp` |

---

## Tile 18 — (no title)
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Content** | Section header / descriptive tile for Physical NIC metrics. |

---

## Tile 19 — Metric Description Inbound Packets (VFP)
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Content** | Explains inbound VFP packet counters such as pending, throttled, intercept, non-IP, multicast, hairpinned, and unicast forwarded rates. |

---

## Tile 20 — Inbound Packets (VFP)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VfpPortMetrics` |
| **Metric(s)** | `PendingPacketInRate`, `ThrottledPacketInRate`, `TotalPacketInRate`, `InterceptInRate`, `MissedInterceptInRate`, `NonIpPacketInRate`, `TotalMulticastPacketsForwardedInRate`, `TotalPacketHairpinnedInRate`, `TotalUnicastPacketForwardedInRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}` *(runtime-substituted from template parameter)*, `NodeId` = `{NodeId}` *(runtime-substituted from template parameter)*, `ContainerId` = `{ContainerId}` *(runtime-substituted from template parameter)* |
| **Output Columns** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---

## Tile 21 — Metric Description Outbound Packets (VFP)
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Content** | Explains outbound VFP packet counters such as pending, throttled, intercept, non-IP, multicast, hairpinned, and unicast forwarded rates. |

---

## Tile 22 — Outbound Packets (VFP)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VfpPortMetrics` |
| **Metric(s)** | `PendingPacketOutRate`, `ThrottledPacketOutRate`, `TotalPacketOutRate`, `InterceptOutRate`, `MissedInterceptOutRate`, `NonIpPacketOutRate`, `TotalMulticastPacketsForwardedOutRate`, `TotalPacketHairpinnedOutRate`, `TotalUnicastPacketForwardedOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}` *(runtime-substituted from template parameter)*, `NodeId` = `{NodeId}` *(runtime-substituted from template parameter)*, `ContainerId` = `{ContainerId}` *(runtime-substituted from template parameter)* |
| **Output Columns** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---

## Tile 23 — FPGA-PFC Packets Received
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `FPGA-PFC` |
| **Metric(s)** | `NicNumPfcPacketsTx`, `TorNumPfcPacketsRx` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}` *(runtime-substituted from template parameter)*, `NodeId` = `{NodeId}` *(runtime-substituted from template parameter)* |
| **Output Columns** | `Cluster`, `NodeId`, `NodeIP` |

---

## Tile 24 — Traffic
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Content** | Dashboard header / glossary tile describing the traffic path (ToR ↔ FPGA ↔ NIC ↔ VF/PF/Root) and PF / VF terminology. |

---

## Summary Table

| # | Tile Title | Source | Metrics / Tables | Confidential |
|---|-----------|--------|-----------------|:------------:|
| 1 | VFP Drops | HTML | Section header / description | |
| 2 | FPGA-PFC Packets Sent | MDM | `FPGA-PFC`: `NicNumPfcPacketsRx`, `TorNumPfcPacketsTx` | |
| 3 | FPGA-PFC Packets Outbound - Description | HTML | Description tile | |
| 4 | (no title) | HTML | Virtual NIC metrics header | |
| 5 | (no title) | HTML | Mellanox NIC metrics header | |
| 6 | Packets Sent/Received (pNIC) Description | HTML | Physical NIC receive metrics description | |
| 7 | Packets/Bytes Received (pNIC) | MDM | `PhysicalNicMetrics`: `PacketsReceivedRate`, `BytesReceivedRate` | |
| 8 | Bytes Sent/Received (pNIC) Description | HTML | Physical NIC send metrics description | |
| 9 | Packets/Bytes Sent (pNIC) | MDM | `PhysicalNicMetrics`: `PacketsSentRate`, `BytesSentRate` | |
| 10 | Packets Sent/Received (vNIC) Description | HTML | Virtual NIC packet metrics description | |
| 11 | Packets Sent/Received (vNIC) | MDM | `VirtualNicMetrics`: `PacketsReceivedRate`, `PacketsSentRate` | |
| 12 | Bytes Sent/Received (vNIC) Description | HTML | Virtual NIC byte metrics description | |
| 13 | Bytes Sent/Received (vNIC) | MDM | `VirtualNicMetrics`: `BytesReceivedRate`, `BytesSentRate` | |
| 14 | Packets/Bytes Received (Mellanox NIC) | HTML | Mellanox receive metrics header | |
| 15 | Mellanox NIC counters Description | HTML | Mellanox counter description | |
| 16 | Packets/Bytes Received (Mellanox NIC) | MDM | `MlnxAdapterCounters`, `Mlx5TrafficCounters` receive metrics | |
| 17 | Packets/Bytes Sent (Mellanox NIC) | MDM | `MlnxAdapterCounters`, `Mlx5TrafficCounters` send metrics | |
| 18 | (no title) | HTML | Physical NIC metrics header | |
| 19 | Metric Description Inbound Packets (VFP) | HTML | Inbound VFP metrics description | |
| 20 | Inbound Packets (VFP) | MDM | `VfpPortMetrics` inbound packet rates | |
| 21 | Metric Description Outbound Packets (VFP) | HTML | Outbound VFP metrics description | |
| 22 | Outbound Packets (VFP) | MDM | `VfpPortMetrics` outbound packet rates | |
| 23 | FPGA-PFC Packets Received | MDM | `FPGA-PFC`: `NicNumPfcPacketsTx`, `TorNumPfcPacketsRx` | |
| 24 | Traffic | HTML | Dashboard header / glossary | |
