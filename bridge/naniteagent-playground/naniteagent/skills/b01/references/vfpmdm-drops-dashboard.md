# VfpMDM dpop dropsDashboard / dropsDashboard_OVL2 — Merged Tile Reference

> 📋 **Merged Dashboard** — This reference combines tiles from the pre-OVL2 (`dpop/dropsDashboard`) and OVL2 (`dpop/dropsDashboard_OVL2`) dashboards. Each tile is tagged with its source: **[Both]** = present in both, **[Pre-OVL2 only]** = legacy FPGA-NETWORK/Mellanox, **[OVL2 only]** = new FPGA-NETWORK-V2/BNIC/PDP architecture.

**Dashboards:** `VfpMDM / dpop/dropsDashboard` + `VfpMDM / dpop/dropsDashboard_OVL2`  
**Source JSON:** `VfpMDM_dpop_dropsDashboard.json`, `VfpMDM_dpop_dropsDashboard_OVL2.json`  
**Raw Tile Counts:** 84 (Pre-OVL2) + 108 (OVL2)  
**Merged Reference Counts:** 105 entries — 86 MDM, 19 HTML / static, 0 Kusto, 0 Mixed

## Template Parameters

| Name | Display Name | Type | Default / Example | Used As | Affected Tiles |
|------|-------------|------|-------------------|---------|----------------|
| `Account` | Account | string | *(empty)* — resolves to e.g. `VfpMdmAM` | MDM `account` field override | All MDM tiles |
| `Cluster` | Cluster | string | ` (all) ` | Dimension filter `Cluster` | All MDM tiles |
| `NodeId` | NodeId | string | *(empty)* | Dimension filter `NodeId` | All MDM tiles |
| `ContainerId` | ContainerId | string | *(empty)* | Dimension filter `ContainerId` | `VfpPort*` namespace tiles |

**Hint queries / resolvers:**
- `Account` — pattern filter `VfpMdm*`
- `Cluster` — MDM hint from `VfpMdmBN / FPGA-CONFIG / IsGolden`, dimension `Cluster`
- `NodeId` — MDM hint from `VfpMdmBN / FPGA-CONFIG / IsGolden`, dimension `NodeId`
- `ContainerId` — MDM hint from `VfpMdmAM / VfpPortTcpMetrics / FinPacketsInRate`, dimension `ContainerId`

> ⚠️ Tiles marked **** must NOT be shared with external customers.

---

## 1. FPGA / GFT Drops

### Tile 1 — Host Networking Drops Dashboard
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Source** | [Both] |
| **Content** | Merged overview tile for host networking drops. |

---
### Tile 2 — FPGA Drops
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Source** | [Both] |
| **Content** | Section header for FPGA / GFT / PDP loss counters. |

---
### Tile 3 — FPGA-PFC (GFT Drops) Description
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Source** | [Both] |
| **Content** | Merged description for FPGA-PFC / GFT drops. |

---
### Tile 4 — FPGA-PFC Packets Outbound - Description
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Source** | [Both] |
| **Content** | Explains outbound FPGA-PFC counters. |

---
### Tile 5 — FPGA-PFC Packets Inbound - Description
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Source** | [Both] |
| **Content** | Explains inbound FPGA-PFC counters. |

---
### Tile 6 — FPGA-PFC Packets Sent
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `FPGA-PFC` |
| **Metric(s)** | `NicNumPfcPacketsRx`, `TorNumPfcPacketsTx` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `NodeId`, `NodeIP` |

---
### Tile 7 — GFT Outbound Drops
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `FPGA-PFC` |
| **Metric(s)** | `NicNumPfcPacketsRxClockCrossingDrop`, `NicNumPfcPacketsRxDropsForLosslessChannel`, `NicNumPfcPacketsRxDropsForLossyChannel`, `NicNumPfcPacketsRxFrameCheckSequenceErrorDrop`, `NicNumPfcPacketsRxMaximumTransmissionUnitErrorDrop`, `NicNumPfcPacketsTxDropsForLosslessChannel`, `NicNumPfcPacketsTxDropsForLossyChannel` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `NodeId`, `NodeIP` |

---
### Tile 8 — GFT Inbound Drops
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `FPGA-PFC` |
| **Metric(s)** | `TorNumPfcPacketsRxClockCrossingDrop`, `TorNumPfcPacketsRxDropsForLosslessChannel`, `TorNumPfcPacketsRxDropsForLossyChannel`, `TorNumPfcPacketsRxFrameCheckSequenceErrorDrop`, `TorNumPfcPacketsRxMaximumTransmissionUnitErrorDrop`, `TorNumPfcPacketsTxDropsForLosslessChannel`, `TorNumPfcPacketsTxDropsForLossyChannel` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `NodeId`, `NodeIP` |

---
### Tile 9 — FPGA-PFC Packets Received
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `FPGA-PFC` |
| **Metric(s)** | `NicNumPfcPacketsTx`, `TorNumPfcPacketsRx` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `NodeId`, `NodeIP` |

---
### Tile 10 — FPGA Outbound Errors
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Pre-OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `FPGA-NETWORK` |
| **Metric(s)** | `NIC-Receive-FCS-Error`, `Short-Cable-FCS-Error-Rate` |
| **Sampling Type** | `Sum` + `Rate` |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `NodeId` |

---
### Tile 11 — FPGA-NETWORK Outbound Traffic
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Pre-OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `FPGA-NETWORK` |
| **Metric(s)** | `TOR-Transmit-Count`, `NIC-Receive-Count` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `NodeId` |

---
### Tile 12 — FPGA Inbound Errors
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Pre-OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `FPGA-NETWORK` |
| **Metric(s)** | `TOR-Receive-FCS-Error` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `NodeId` |

---
### Tile 13 — FPGA-NETWORK Inbound Traffic
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Pre-OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `FPGA-NETWORK` |
| **Metric(s)** | `TOR-Receive-Count`, `NIC-Transmit-Count` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `NodeId` |

---
### Tile 14 — GFTv3 : Net-switch NIC Lossy Drops
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Pre-OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `FPGA-GFT` |
| **Metric(s)** | `NicLMtuDropCount`, `NicLOverflowDropCount`, `NicLMalformedDropCount`, `NicLErrorDropCount0-5` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `NodeId` |

---
### Tile 15 — GFTv3 : Net-switch TOR Lossy Drops
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Pre-OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `FPGA-GFT` |
| **Metric(s)** | `TorLMtuDropCount`, `TorLOverflowDropCount`, `TorLMalformedDropCount`, `TorLErrorDropCount0-5` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `NodeId` |

---
### Tile 16 — FPGA-PDP Packets Outbound/Inbound - Description
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Source** | [OVL2 only] |
| **Content** | Merged PDP description tile for OVL2 MAC0 / MAC1 counters. |

---
### Tile 17 — FPGA-PDP-MAC0 Packets Inbound errors
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `GdmaPdpNetBuffMetrics` |
| **Metric(s)** | `MAC0RXStfwCRCErrDropCount`, `MAC0RXStfwMalformedPacketDropCount`, `MAC0RXStfwMTUErrDropCount`, `MAC0RXStfwOversizePacketDropCount`, `MAC0RXStfwOvflDropCount`, `MAC0RXStfwPayloadLenDropCount`, `MAC0RXStfwSizeErrDropCount`, `MAC0RXStfwSopEopErrDropCount`, `MAC0RXStfwBuff0WatermarkDropCount`, `MAC0RXStfwBuff1WatermarkDropCount`, `MAC0RXStfwBuff2WatermarkDropCount` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | PDP hardware dims |

---
### Tile 18 — FPGA-PDP-MAC1 Packets Inbound errors
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `GdmaPdpNetBuffMetrics` |
| **Metric(s)** | `MAC1RXStfwCRCErrDropCount`, `MAC1RXStfwMalformedPacketDropCount`, `MAC1RXStfwMTUErrDropCount`, `MAC1RXStfwOversizePacketDropCount`, `MAC1RXStfwOvflDropCount`, `MAC1RXStfwPayloadLenDropCount`, `MAC1RXStfwSizeErrDropCount`, `MAC1RXStfwSopEopErrDropCount`, `MAC1RXStfwBuff0WatermarkDropCount`, `MAC1RXStfwBuff1WatermarkDropCount`, `MAC1RXStfwBuff2WatermarkDropCount` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | PDP hardware dims |

---
### Tile 19 — FPGA-PDP-MAC0 Packets Outbound errors
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `GdmaPdpNetBuffMetrics` |
| **Metric(s)** | `MAC0TXBuff0DropPacketCount`, `MAC0TXBuff1DropPacketCount`, `MAC0TXBuff2DropPacketCount` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | PDP hardware dims |

---
### Tile 20 — FPGA-PDP-MAC1 Packets Outbound errors
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `GdmaPdpNetBuffMetrics` |
| **Metric(s)** | `MAC1TXBuff0DropPacketCount`, `MAC1TXBuff1DropPacketCount`, `MAC1TXBuff2DropPacketCount` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | PDP hardware dims |

---
### Tile 21 — FPGA-PDP Packets Sent
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `GdmaPdpNetBuffMetrics` |
| **Metric(s)** | `MAC0TXBuff0PacketCount`, `MAC0TXBuff1PacketCount`, `MAC0TXBuff2PacketCount`, `MAC1TXBuff0PacketCount`, `MAC1TXBuff1PacketCount`, `MAC1TXBuff2PacketCount`, `MAC0RXStwfGoodPacketCount`, `MAC1RXStwfGoodPacketCount` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | PDP hardware dims |

---
### Tile 22 — FPGA-PDP Packets Received
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `GdmaPdpNetBuffMetrics` |
| **Metric(s)** | `MAC0RXStwfBuff0GoodPacketCount`, `MAC0RXStwfBuff1GoodPacketCount`, `MAC0RXStwfBuff2GoodPacketCount`, `MAC1RXStwfBuff0GoodPacketCount`, `MAC1RXStwfBuff1GoodPacketCount`, `MAC1RXStwfBuff2GoodPacketCount`, `MAC0RXStwfGoodPacketCount`, `MAC1RXStwfGoodPacketCount` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | PDP hardware dims |

---
### Tile 23 — FPGA-NETWORK-V2 Outbound Traffic
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `FPGA-NETWORK-V2` |
| **Metric(s)** | `MAC0-Transmit-Count`, `MAC1-Transmit-Count` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `NodeId`, MAC dims |

---
### Tile 24 — FPGA-NETWORK-V2 Inbound Traffic
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `FPGA-NETWORK-V2` |
| **Metric(s)** | `MAC0-Receive-Count`, `MAC1-Receive-Count` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `NodeId`, MAC dims |

---
### Tile 25 — FPGA OVL2 Inbound Errors
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `FPGA-NETWORK-V2` |
| **Metric(s)** | `MAC0-Receive-FCS-Error`, `MAC1-Receive-FCS-Error` |
| **Sampling Type** | Rate |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `NodeId`, MAC dims |

---

## 2. Physical NIC (pNIC) Drops & Traffic

### Tile 26 — NIC Drops
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Source** | [Both] |
| **Content** | Section header for NIC-level loss / traffic. |

---
### Tile 27 — Dropped Received/Sent Packets (pNIC/vNIC) Description
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Source** | [Both] |
| **Content** | Merged drop description for pNIC and vNIC tiles. |

---
### Tile 28 — Packets/Bytes Sent/Received (pNIC/vNIC) Description
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Source** | [Both] |
| **Content** | Merged traffic description for pNIC and vNIC tiles. |

---
### Tile 29 — Packets/Bytes Received (pNIC)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `PhysicalNicMetrics` |
| **Metric(s)** | `PacketsReceivedRate`, `BytesReceivedRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `MacAddress`, `NodeId`, `NodeIP` |

---
### Tile 30 — Packets/Bytes Sent (pNIC)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `PhysicalNicMetrics` |
| **Metric(s)** | `PacketsSentRate`, `BytesSentRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `MacAddress`, `NodeId`, `NodeIP` |

---
### Tile 31 — Dropped Received Packets (pNIC)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `PhysicalNicMetrics` |
| **Metric(s)** | `PacketsReceivedErrorsRate`, `PacketsReceivedDiscardedRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `MacAddress`, `NodeId`, `NodeIP` |

---
### Tile 32 — Dropped Sent Packets (pNIC)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `PhysicalNicMetrics` |
| **Metric(s)** | `PacketsOutboundDiscardedRate`, `PacketsOutboundErrorsRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `MacAddress`, `NodeId`, `NodeIP` |

---
### Tile 33 — Percentage of Dropped Received Packets (pNIC)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `PhysicalNicMetrics` *(OVL2)* / `FPGA-NETWORK` denom variant *(Pre-OVL2)* |
| **Metric(s)** | `PacketsReceivedErrorsRate / PacketsReceivedRate`, `PacketsReceivedDiscardedRate / PacketsReceivedRate` |
| **Sampling Type** | Computed ratio |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `MacAddress`, `NodeId`, `NodeIP` |
| **Notes** | Pre-OVL2 uses `NIC-Transmit-Count` denominator; OVL2 uses `PacketsReceivedRate`. |

---
### Tile 34 — Percentage of Dropped Sent Packets (pNIC)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `PhysicalNicMetrics` |
| **Metric(s)** | `PacketsOutboundDiscardedRate / PacketsSentRate`, `PacketsOutboundErrorsRate / PacketsSentRate` |
| **Sampling Type** | Computed ratio |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `MacAddress`, `NodeId`, `NodeIP` |

---

## 3. Virtual NIC (vNIC) Drops & Traffic

### Tile 35 — Dropped Received Packets (vNIC)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VirtualNicMetrics` |
| **Metric(s)** | `PacketsReceivedErrorsRate`, `PacketsReceivedDiscardedRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `MacAddress`, `NodeId`, `NodeIP` |

---
### Tile 36 — Dropped Sent Packets (vNIC)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VirtualNicMetrics` |
| **Metric(s)** | `PacketsOutboundDiscardedRate`, `PacketsOutboundErrorsRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `MacAddress`, `NodeId`, `NodeIP` |

---
### Tile 37 — Percentage of Dropped Received Packets (vNIC)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VirtualNicMetrics` |
| **Metric(s)** | `PacketsReceivedErrorsRate / PacketsReceivedRate`, `PacketsReceivedDiscardedRate / PacketsReceivedRate` |
| **Sampling Type** | Computed ratio |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `MacAddress`, `NodeId`, `NodeIP` |

---
### Tile 38 — Percentage of Dropped Sent Packets (vNIC)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VirtualNicMetrics` |
| **Metric(s)** | `PacketsOutboundDiscardedRate / PacketsSentRate`, `PacketsOutboundErrorsRate / PacketsSentRate` |
| **Sampling Type** | Computed ratio |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `MacAddress`, `NodeId`, `NodeIP` |

---
### Tile 39 — Packets/Bytes Received (vNIC)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Pre-OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VirtualNicMetrics` |
| **Metric(s)** | `PacketsReceivedRate`, `BytesReceivedRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `MacAddress`, `NodeId`, `NodeIP` |

---
### Tile 40 — Packets/Bytes Sent (vNIC)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Pre-OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VirtualNicMetrics` |
| **Metric(s)** | `PacketsSentRate`, `BytesSentRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `MacAddress`, `NodeId`, `NodeIP` |

---
### Tile 41 — Packets Sent/Received (vNIC)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VirtualNicMetrics` |
| **Metric(s)** | `PacketsReceivedRate`, `PacketsSentRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `MacAddress`, `NodeId`, `NodeIP` |

---
### Tile 42 — Bytes Sent/Received (vNIC)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VirtualNicMetrics` |
| **Metric(s)** | `BytesReceivedRate`, `BytesSentRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `MacAddress`, `NodeId`, `NodeIP` |

---

## 4. Mellanox NIC (Pre-OVL2 only)

### Tile 43 — Mellanox NIC counters Description
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Source** | [Pre-OVL2 only] |
| **Content** | Merged Mellanox counter description tile. |

---
### Tile 44 — Packets/Bytes Received (Mellanox NIC) Description
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Source** | [Pre-OVL2 only] |
| **Content** | Receive-side Mellanox description tile. |

---
### Tile 45 — Dropped Received Packets (Mellanox NIC)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Pre-OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `MlnxAdapterCounters`, `Mlx5TrafficCounters`, `MlnxBusCounters` |
| **Metric(s)** | `Packets_Received_Errors_Rate`, `Packets_Received_Discarded_Rate`, `Packets_Received_Frame_Length_Error_Rate`, `Packets_Received_Bad_CRC_Error_Rate`, `Packets_Received_Symbol_Error_Rate`, `Packets_Received_Errors`, `Packets_Received_Symbol_Error`, `Packets_Received_Bad_CRC_Error`, `Packets_Received_Discarded_No_Recv_WQEs`, `No_WQE_Drops/sec` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `NodeId`, Mellanox dims |

---
### Tile 46 — Dropped Outbound Packets (Mellanox NIC)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Pre-OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `MlnxAdapterCounters`, `Mlx5TrafficCounters` |
| **Metric(s)** | `Packets_Outbound_Errors_Rate`, `Packets_Outbound_Discarded_Rate`, `Packets_Outbound_Errors`, `Packets_Outbound_Discarded` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `NodeId`, Mellanox dims |

---
### Tile 47 — Packets/Bytes Received (Mellanox NIC)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Pre-OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `MlnxAdapterCounters`, `Mlx5TrafficCounters` |
| **Metric(s)** | `Bytes_Received_Rate`, `Packets_Received_Rate`, `Bytes_Received`, `Packets_Received` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `NodeId`, Mellanox dims |

---
### Tile 48 — Packets/Bytes Sent (Mellanox NIC)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Pre-OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `MlnxAdapterCounters`, `Mlx5TrafficCounters` |
| **Metric(s)** | `Packets_Sent_Rate`, `Bytes_Sent_Rate`, `Bytes_Sent`, `Packets_Sent` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `NodeId`, Mellanox dims |

---
### Tile 49 — Percentage of dropped Received Packets (Mellanox NIC)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Pre-OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `MlnxAdapterCounters` |
| **Metric(s)** | `Packets_Received_Errors_Rate / Packets_Received_Rate` |
| **Sampling Type** | Computed ratio |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `NodeId`, Mellanox dims |

---
### Tile 50 — Percentage of dropped Outbound Packets (Mellanox NIC)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Pre-OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `MlnxAdapterCounters` |
| **Metric(s)** | `Packets_Outbound_Errors_Rate / Packets_Sent_Rate`, `Packets_Outbound_Discarded_Rate / Packets_Sent_Rate` |
| **Sampling Type** | Computed ratio |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `NodeId`, Mellanox dims |

---

## 5. BNIC (OVL2 only)

### Tile 51 — BNIC counters Description
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Source** | [OVL2 only] |
| **Content** | Merged BNIC description tile. |

---
### Tile 52 — Packets Received/Sent (BNIC *) Description tiles
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Source** | [OVL2 only] |
| **Content** | Merged BNIC packet-count description tiles. |

---
### Tile 53 — Bytes Received/Sent (BNIC *) Description tiles
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Source** | [OVL2 only] |
| **Content** | Merged BNIC byte-count description tiles. |

---
### Tile 54 — Packets Received (BNIC Global/SoC/Host)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `GdmaBnicGlobalMetrics`, `GdmaBnicPfMetrics`, `GdmaBnicPvfMetrics` |
| **Metric(s)** | `NumOfInPackets` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | Global/PF/PVF dims |

---
### Tile 55 — Packets Sent (BNIC Global/SoC/Host)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `GdmaBnicGlobalMetrics`, `GdmaBnicPfMetrics`, `GdmaBnicPvfMetrics` |
| **Metric(s)** | `NumOfOutPackets` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | Global/PF/PVF dims |

---
### Tile 56 — Packets Received (BNIC Vf)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `GdmaBnicVfMetrics` |
| **Metric(s)** | `NumOfInPackets` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | VF dims |

---
### Tile 57 — Packets Sent (BNIC Vf)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `GdmaBnicVfMetrics` |
| **Metric(s)** | `NumOfOutPackets` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | VF dims |

---
### Tile 58 — Bytes Received (BNIC Global/SoC/Host)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `GdmaBnicGlobalMetrics`, `GdmaBnicPfMetrics`, `GdmaBnicPvfMetrics` |
| **Metric(s)** | `NumOfInOctets` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | Global/PF/PVF dims |

---
### Tile 59 — Bytes Sent (BNIC Global/SoC/Host)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `GdmaBnicGlobalMetrics`, `GdmaBnicPfMetrics`, `GdmaBnicPvfMetrics` |
| **Metric(s)** | `NumOfOutOctets` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | Global/PF/PVF dims |

---
### Tile 60 — Bytes Received (BNIC Vf)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `GdmaBnicVfMetrics` |
| **Metric(s)** | `NumOfInOctets` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | VF dims |

---
### Tile 61 — Bytes Sent (BNIC Vf)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `GdmaBnicVfMetrics` |
| **Metric(s)** | `NumOfOutOctets` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | VF dims |

---
### Tile 62 — Percentage of dropped Received Packets (BNIC Global)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `GdmaBnicGlobalMetrics` |
| **Metric(s)** | `InTotalErrors/NumOfInPackets`, `NumOfInDiscardsNoWQE/NumOfInPackets`, `NumOfInErrorsRxVportDisabled/NumOfInPackets`, `NumOfInErrorsSteeringUcast/NumOfInPackets`, `NumOfInErrorsSteeringMcast/NumOfInPackets` |
| **Sampling Type** | Computed ratio |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | BNIC Global dims |

---
### Tile 63 — Percentage of dropped Sent Packets (BNIC Global)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `GdmaBnicGlobalMetrics` |
| **Metric(s)** | `OutTotalErrors/NumOfOutPackets`, `NumOfOutErrorsGfDisabled/NumOfOutPackets`, `NumOfOutErrorsVportDisabled/NumOfOutPackets`, `NumOfOutErrorsInvalidVportOffsetPackets/NumOfOutPackets`, `NumOfOutErrorsVlanEnforcement`, `NumOfOutErrorsEthTypeEnforcement`, `NumOfOutErrorsSAEnforcement`, `NumOfOutErrorsSQPDIDEnforcement`, `NumOfOutErrorsCQPDIDEnforcement`, `NumOfOutErrorsMtuViolation`, `NumOfOutErrorsInvalidOob` |
| **Sampling Type** | Computed ratio |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | BNIC Global dims |

---
### Tile 64 — Dropped Received Packets (BNIC Global)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `GdmaBnicGlobalMetrics` |
| **Metric(s)** | `InTotalErrors`, `NumOfInDiscardsNoWQE`, `NumOfInErrorsRxVportDisabled`, `NumOfInErrorsSteeringUcast`, `NumOfInErrorsSteeringMcast` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | BNIC Global dims |

---
### Tile 65 — Dropped Sent Packets (BNIC Global)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `GdmaBnicGlobalMetrics` |
| **Metric(s)** | `OutTotalErrors`, `NumOfOutErrorsGfDisabled`, `NumOfOutErrorsVportDisabled`, `NumOfOutErrorsInvalidVportOffsetPackets`, `NumOfOutErrorsVlanEnforcement`, `NumOfOutErrorsEthTypeEnforcement`, `NumOfOutErrorsSAEnforcement`, `NumOfOutErrorsSQPDIDEnforcement`, `NumOfOutErrorsCQPDIDEnforcement`, `NumOfOutErrorsMtuViolation`, `NumOfOutErrorsInvalidOob` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | BNIC Global dims |

---
### Tile 66 — Percentage of dropped Received Packets (BNIC SoC Pf)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `GdmaBnicPfMetrics` |
| **Metric(s)** | `InTotalErrors/NumOfInPackets`, `NumOfInDiscardsNoWQE/NumOfInPackets`, `NumOfInErrorsRxVportDisabled/NumOfInPackets` |
| **Sampling Type** | Computed ratio |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | SoC PF dims |

---
### Tile 67 — Dropped Received Packets (BNIC SoC Pf)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `GdmaBnicPfMetrics` |
| **Metric(s)** | `InTotalErrors`, `NumOfInDiscardsNoWQE`, `NumOfInErrorsRxVportDisabled` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | SoC PF dims |

---
### Tile 68 — Percentage of dropped Sent Packets (BNIC SoC Pf)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `GdmaBnicPfMetrics`, `GdmaRnicPfMetrics` |
| **Metric(s)** | Same sent-drop percentage family as BNIC Global |
| **Sampling Type** | Computed ratio |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | SoC PF dims |

---
### Tile 69 — Dropped Sent Packets (BNIC SoC Pf)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `GdmaBnicPfMetrics` |
| **Metric(s)** | Same sent-drop family as BNIC Global |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | SoC PF dims |

---
### Tile 70 — Percentage of dropped Received Packets (BNIC Host Pvf)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `GdmaBnicPvfMetrics` |
| **Metric(s)** | Same receive-drop percentage family as BNIC SoC Pf |
| **Sampling Type** | Computed ratio |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | PVF dims |

---
### Tile 71 — Percentage of dropped Sent Packets (BNIC Host Pvf)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `GdmaBnicPvfMetrics` |
| **Metric(s)** | Same sent-drop percentage family as BNIC Global |
| **Sampling Type** | Computed ratio |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | PVF dims |

---
### Tile 72 — Dropped Received Packets (BNIC Host Pvf)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `GdmaBnicPvfMetrics` |
| **Metric(s)** | `InTotalErrors`, `NumOfInDiscardsNoWQE`, `NumOfInErrorsRxVportDisabled` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | PVF dims |

---
### Tile 73 — Dropped Sent Packets (BNIC Host Pvf)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `GdmaBnicPvfMetrics` |
| **Metric(s)** | Same sent-drop family as BNIC Global |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | PVF dims |

---
### Tile 74 — Percentage of dropped Received Packets (BNIC Vf)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `GdmaBnicVfMetrics` |
| **Metric(s)** | Same receive-drop percentage family as BNIC SoC Pf |
| **Sampling Type** | Computed ratio |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | VF dims |

---
### Tile 75 — Percentage of dropped Sent Packets (BNIC Vf)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `GdmaBnicVfMetrics` |
| **Metric(s)** | Same sent-drop percentage family as BNIC Global |
| **Sampling Type** | Computed ratio |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | VF dims |

---
### Tile 76 — Dropped Received Packets (BNIC Vf)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `GdmaBnicVfMetrics` |
| **Metric(s)** | `InTotalErrors`, `NumOfInDiscardsNoWQE`, `NumOfInErrorsRxVportDisabled` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | VF dims |

---
### Tile 77 — Dropped Sent Packets (BNIC Vf)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `GdmaBnicVfMetrics` |
| **Metric(s)** | Same sent-drop family as BNIC Global |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | VF dims |

---

## 6. VFP Port Drops (VfpPortDropMetrics) — Sets 1-4

### Tile 78 — VFP Drops
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Source** | [Both] |
| **Content** | Section header for VFP port drops. |

---
### Tile 79 — Description - Inbound/Outbound Packets Drop Metrics
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Source** | [Both] |
| **Content** | Merged description for VfpPortDropMetrics Sets 1-4. |

---
### Tile 80 — Inbound Packets Drop Metrics - Set 1
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VfpPortDropMetrics` |
| **Metric(s)** | `DropNonIpPacketInRate`, `DroppedBroadcastLimiterPacketInRate`, `DroppedForwardingPacketInRate`, `DroppedInvalidRulePacketInRate`, `DroppedMacSpoofingPacketInRate`, `DroppedMalformedPacketInRate`, `DroppedResourcesPacketInRate`, `DroppedSimulationPacketInRate`, `DropArpLimiterPacketInRate`, `DropArpGuardPacketInRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |
| **Output Columns** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---
### Tile 81 — Outbound Packets Drop Metrics - Set 1
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VfpPortDropMetrics` |
| **Metric(s)** | `DropNonIpPacketOutRate`, `DroppedBroadcastLimiterPacketOutRate`, `DroppedForwardingPacketOutRate`, `DroppedInvalidRulePacketOutRate`, `DroppedMacSpoofingPacketOutRate`, `DroppedMalformedPacketOutRate`, `DroppedResourcesPacketOutRate`, `DroppedSimulationPacketOutRate`, `DropArpLimiterPacketOutRate`, `DropArpGuardPacketOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |
| **Output Columns** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---
### Tile 82 — Inbound Packets Drop Metrics - Set 2
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VfpPortDropMetrics` |
| **Metric(s)** | `DropArpFilterPacketInRate`, `DropIpv4SpoofingPacketInRate`, `DroppedAclPacketInRate`, `DroppedNoRuleMatchPacketInRate`, `DropIpv6SpoofingPacketInRate`, `DropInvalidPacketInRate`, `DropBlockedPacketInRate`, `DropBroadcastPacketInRate`, `DropDhcpGuardPacketInRate`, `DropDhcpLimiterPacketInRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |
| **Output Columns** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---
### Tile 83 — Outbound Packets Drop Metrics - Set 2
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VfpPortDropMetrics` |
| **Metric(s)** | `DropArpFilterPacketOutRate`, `DropIpv4SpoofingPacketOutRate`, `DroppedAclPacketOutRate`, `DroppedNoRuleMatchPacketOutRate`, `DropIpv6SpoofingPacketOutRate`, `DropInvalidPacketOutRate`, `DropBlockedPacketOutRate`, `DropBroadcastPacketOutRate`, `DropDhcpGuardPacketOutRate`, `DropDhcpLimiterPacketOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |
| **Output Columns** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---
### Tile 84 — Inbound Packets Drop Metrics - Set 3
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VfpPortDropMetrics` |
| **Metric(s)** | `DroppedPendingPacketDtlsInRate`, `DroppedPendingPacketFragInRate`, `DroppedPendingPacketGftInRate`, `DroppedPendingPacketMappingInRate`, `DroppedPendingPacketNatInRate`, `DroppedPendingPacketPARouteInRate`, `DroppedPendingPacketQosInRate`, `DroppedPendingPADiscoveryInRate`, `DroppedExpiredPendedPacketInRate`, `DroppedPendingPacketInRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |
| **Output Columns** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---
### Tile 85 — Outbound Packets Drop Metrics - Set 3
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VfpPortDropMetrics` |
| **Metric(s)** | `DroppedPendingPacketDtlsOutRate`, `DroppedPendingPacketFragOutRate`, `DroppedPendingPacketGftOutRate`, `DroppedPendingPacketMappingOutRate`, `DroppedPendingPacketNatOutRate`, `DroppedPendingPacketPARouteOutRate`, `DroppedPendingPacketQosOutRate`, `DroppedPendingPADiscoveryOutRate`, `DroppedExpiredPendedPacketOutRate`, `DroppedPendingPacketOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |
| **Output Columns** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---
### Tile 86 — Inbound Packets Drop Metrics - Set 4
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VfpPortDropMetrics` |
| **Metric(s)** | `DroppedPADiscoveryPacketsInRate`, `DroppedResourcesLayerFlowMaxFlowsLimitInRate`, `DroppedResourcesMemoryInRate`, `DroppedPARouteRuleInRate`, `DroppedFragPacketInRate`, `DroppedResourcesUnifiedFlowMaxFlowsLimitInRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |
| **Output Columns** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---
### Tile 87 — Outbound Packets Drop Metrics - Set 4
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VfpPortDropMetrics` |
| **Metric(s)** | `DroppedRedirectPacketsOutRate`, `DroppedPADiscoveryPacketsOutRate`, `DroppedResourcesLayerFlowMaxFlowsLimitOutRate`, `DroppedResourcesMemoryOutRate`, `DroppedPARouteRuleOutRate`, `DroppedFragPacketOutRate`, `DroppedResourcesUnifiedFlowMaxFlowsLimitOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |
| **Output Columns** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---

## 7. VMSwitch Drops (VmsNicDropMetrics) — Sets 1-4

### Tile 88 — Inbound Packet Drop Metrics - Set 1
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VmsNicDropMetrics` |
| **Metric(s)** | `BridgeReservedDropInRate`, `InvalidDataDropInRate`, `InvalidPacketDropInRate`, `ResourceDropInRate`, `NotReadyDropInRate`, `DisconnectedDropInRate`, `NotAcceptedDropInRate`, `BusyDropInRate`, `FilteredDropInRate`, `FilteredVlanDropInRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---
### Tile 89 — Outbound Packet Drop Metrics - Set 1
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VmsNicDropMetrics` |
| **Metric(s)** | `BridgeReservedDropOutRate`, `InvalidDataDropOutRate`, `InvalidPacketDropOutRate`, `ResourceDropOutRate`, `NotReadyDropOutRate`, `DisconnectedDropOutRate`, `NotAcceptedDropOutRate`, `BusyDropOutRate`, `FilteredDropOutRate`, `FilteredVlanDropOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---
### Tile 90 — Inbound Packet Drop Metrics - Set 2
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VmsNicDropMetrics` |
| **Metric(s)** | `UnauthorizedVlanDropInRate`, `UnauthorizedMacDropInRate`, `SecurityPolicyDropInRate`, `PVlanSettingDropInRate`, `QosDropInRate`, `IpSecDropInRate`, `MacSpoofingDropInRate`, `DhcpGuardDropInRate`, `RouterGuardDropInRate`, `UnknownDropInRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---
### Tile 91 — Outbound Packet Drop Metrics - Set 2
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VmsNicDropMetrics` |
| **Metric(s)** | Outbound equivalents of the Set 2 receive-drop family (`*OutRate`) |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---
### Tile 92 — Inbound Packet Drop Metrics - Set 3
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VmsNicDropMetrics` |
| **Metric(s)** | `VirtualSubnetIdDropInRate`, `VfpNotPresentDropInRate`, `InvalidConfigDropInRate`, `MtuMismatchDropInRate`, `NativeForwardingReqDropInRate`, `InvalidVlanFormatDropInRate`, `InvalidDestMacDropInRate`, `InvalidSourceMacDropInRate`, `FirstNbTooSmallDropInRate`, `WnvDropInRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---
### Tile 93 — Outbound Packet Drop Metrics - Set 3
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VmsNicDropMetrics` |
| **Metric(s)** | Outbound equivalents of the Set 3 receive-drop family (`*OutRate`) |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---
### Tile 94 — Inbound Packet Drop Metrics - Set 4
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VmsNicDropMetrics` |
| **Metric(s)** | `StormLimitDropInRate`, `InjectedIcmpDropInRate`, `DestListUpdateDropInRate`, `DisabledDropInRate`, `PacketFilterDropInRate`, `SwitchDataDisabledDropInRate`, `FilteredIsoUntaggedDropInRate`, `DroppedPacketsIncomingRate`, `ExtensionsDroppedPacketsOutgoingRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---
### Tile 95 — Outbound Packet Drop Metrics - Set 4
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VmsNicDropMetrics` |
| **Metric(s)** | `StormLimitDropOutRate`, `InjectedIcmpDropOutRate`, `DestListUpdateDropOutRate`, `DisabledDropOutRate`, `PacketFilterDropOutRate`, `SwitchDataDisabledDropOutRate`, `FilteredIsoUntaggedDropOutRate`, `DroppedPacketsOutgoingRate`, `ExtensionsDroppedPacketsOutgoingRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---

## 8. VFP Traffic & Misc (Injected resets, DNS/DHCP, Backplane)

### Tile 96 — Metric Description Inbound/Outbound Packets (VFP)
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Source** | [Both] |
| **Content** | Merged description for inbound / outbound VFP packet counters. |

---
### Tile 97 — Injected Resets Description
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Source** | [Pre-OVL2 only] |
| **Content** | Legacy injected-reset description tile. |

---
### Tile 98 — Dropped DNS/DHCP Packets Description
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Source** | [Pre-OVL2 only] |
| **Content** | Legacy DNS / DHCP drop description tile. |

---
### Tile 99 — Inbound Packets (VFP)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VfpPortMetrics` |
| **Metric(s)** | `PendingPacketInRate`, `ThrottledPacketInRate`, `TotalPacketInRate`, `InterceptInRate`, `MissedInterceptInRate`, `NonIpPacketInRate`, `TotalMulticastPacketsForwardedInRate`, `TotalPacketHairpinnedInRate`, `TotalUnicastPacketForwardedInRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |
| **Output Columns** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---
### Tile 100 — Outbound Packets (VFP)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VfpPortMetrics` |
| **Metric(s)** | `PendingPacketOutRate`, `ThrottledPacketOutRate`, `TotalPacketOutRate`, `InterceptOutRate`, `MissedInterceptOutRate`, `NonIpPacketOutRate`, `TotalMulticastPacketsForwardedOutRate`, `TotalPacketHairpinnedOutRate`, `TotalUnicastPacketForwardedOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |
| **Output Columns** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---
### Tile 101 — Backplane Metrics (Number of Errors Received and Transmitted)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `BACKPLANE-METRICS` |
| **Metric(s)** | `NumOfErrorsReceived`, `NumOfErrorsTransmitted`, `NumOfMissedErrorsReceived` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |
| **Output Columns** | Backplane dims |

---
### Tile 102 — Injected resets (VFP)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Both — Pre-OVL2 has extra ResetResponse metrics] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VfpPortDropMetrics` *(both)* / `VfpPortMetrics` *(legacy extra metrics)* |
| **Metric(s)** | `TcpConnectionsResetByInjectedResetInRate`, `TcpConnectionsResetByInjectedResetOutRate`; Pre-OVL2 also adds `TcpConnectionsResetByResetResponseInRate`, `TcpConnectionsResetByResetResponseOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |
| **Output Columns** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |
| **Notes** | OVL2 keeps only injected-reset metrics. |

---
### Tile 103 — Injected resets cause
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Pre-OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VfpPortMetrics` |
| **Metric(s)** | `TcpConnectionsResetHalfTTLInRate`, `TcpConnectionsResetHalfTTLOutRate`, `NonSynStatefulNatsInRate`, `NonSynStatefulNatsOutRate`, `UFsXvlanLmResetInjectedInRate`, `UFsXvlanLmResetInjectedOutRate`, `UFsXvlanLmResetReInjectedInRate`, `UFsXvlanLmResetReInjectedOutRate`, `UFsXvlanLmResetsFailedInRate`, `UFsXvlanLmResetsFailedOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |
| **Output Columns** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---
### Tile 104 — Dropped DNS/DHCP In Rate
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Pre-OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VfpPortDropMetrics` |
| **Metric(s)** | `DroppedDhcpPacketsInRate`, `DroppedDnsPacketsInRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |
| **Output Columns** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---
### Tile 105 — Dropped DNS/DHCP Out Rate
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [Pre-OVL2 only] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter (e.g. `VfpMdmAM`) |
| **MDM Namespace** | `VfpPortDropMetrics` |
| **Metric(s)** | `DroppedDhcpPacketsOutRate`, `DroppedDnsPacketsOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |
| **Output Columns** | `Cluster`, `ContainerId`, `MacAddress`, `NodeId`, `VNetId` |

---

## Summary Table

| # | Tile Title | Tile Type | Source | Metrics / Tables | Confidential |
|---|-----------|-----------|--------|------------------|:------------:|
| 1 | Host Networking Drops Dashboard | HTML | [Both] | HTML / static description | Yes |
| 2 | FPGA Drops | HTML | [Both] | HTML / static description | Yes |
| 3 | FPGA-PFC (GFT Drops) Description | HTML | [Both] | HTML / static description | Yes |
| 4 | FPGA-PFC Packets Outbound - Description | HTML | [Both] | HTML / static description | Yes |
| 5 | FPGA-PFC Packets Inbound - Description | HTML | [Both] | HTML / static description | Yes |
| 6 | FPGA-PFC Packets Sent | MDM | [Both] | MDM `FPGA-PFC`: `NicNumPfcPacketsRx`, `TorNumPfcPacketsTx` | Yes |
| 7 | GFT Outbound Drops | MDM | [Both] | MDM `FPGA-PFC`: `NicNumPfcPacketsRxClockCrossingDrop`, `NicNumPfcPacketsRxDropsForLosslessChannel`, `NicNumPfcPacketsRxDropsForLossyChannel`, `NicNumPfcPacketsRxFrameCheckSequenceErrorDrop`, `NicNumPfcPacketsRxMaximumTransmissionUnitErrorDrop`, `NicNumPfcPacketsTxDropsForLosslessChannel`, `NicNumPfcPacketsTxDropsForLossyChannel` | Yes |
| 8 | GFT Inbound Drops | MDM | [Both] | MDM `FPGA-PFC`: `TorNumPfcPacketsRxClockCrossingDrop`, `TorNumPfcPacketsRxDropsForLosslessChannel`, `TorNumPfcPacketsRxDropsForLossyChannel`, `TorNumPfcPacketsRxFrameCheckSequenceErrorDrop`, `TorNumPfcPacketsRxMaximumTransmissionUnitErrorDrop`, `TorNumPfcPacketsTxDropsForLosslessChannel`, `TorNumPfcPacketsTxDropsForLossyChannel` | Yes |
| 9 | FPGA-PFC Packets Received | MDM | [Both] | MDM `FPGA-PFC`: `NicNumPfcPacketsTx`, `TorNumPfcPacketsRx` | Yes |
| 10 | FPGA Outbound Errors | MDM | [Pre-OVL2 only] | MDM `FPGA-NETWORK`: `NIC-Receive-FCS-Error`, `Short-Cable-FCS-Error-Rate` | Yes |
| 11 | FPGA-NETWORK Outbound Traffic | MDM | [Pre-OVL2 only] | MDM `FPGA-NETWORK`: `TOR-Transmit-Count`, `NIC-Receive-Count` | Yes |
| 12 | FPGA Inbound Errors | MDM | [Pre-OVL2 only] | MDM `FPGA-NETWORK`: `TOR-Receive-FCS-Error` | Yes |
| 13 | FPGA-NETWORK Inbound Traffic | MDM | [Pre-OVL2 only] | MDM `FPGA-NETWORK`: `TOR-Receive-Count`, `NIC-Transmit-Count` | Yes |
| 14 | GFTv3 : Net-switch NIC Lossy Drops | MDM | [Pre-OVL2 only] | MDM `FPGA-GFT`: `NicLMtuDropCount`, `NicLOverflowDropCount`, `NicLMalformedDropCount`, `NicLErrorDropCount0-5` | Yes |
| 15 | GFTv3 : Net-switch TOR Lossy Drops | MDM | [Pre-OVL2 only] | MDM `FPGA-GFT`: `TorLMtuDropCount`, `TorLOverflowDropCount`, `TorLMalformedDropCount`, `TorLErrorDropCount0-5` | Yes |
| 16 | FPGA-PDP Packets Outbound/Inbound - Description | HTML | [OVL2 only] | HTML / static description | Yes |
| 17 | FPGA-PDP-MAC0 Packets Inbound errors | MDM | [OVL2 only] | MDM `GdmaPdpNetBuffMetrics`: `MAC0RXStfwCRCErrDropCount`, `MAC0RXStfwMalformedPacketDropCount`, `MAC0RXStfwMTUErrDropCount`, `MAC0RXStfwOversizePacketDropCount`, `MAC0RXStfwOvflDropCount`, `MAC0RXStfwPayloadLenDropCount`, `MAC0RXStfwSizeErrDropCount`, `MAC0RXStfwSopEopErrDropCount`, `MAC0RXStfwBuff0WatermarkDropCount`, `MAC0RXStfwBuff1WatermarkDropCount`, `MAC0RXStfwBuff2WatermarkDropCount` | Yes |
| 18 | FPGA-PDP-MAC1 Packets Inbound errors | MDM | [OVL2 only] | MDM `GdmaPdpNetBuffMetrics`: `MAC1RXStfwCRCErrDropCount`, `MAC1RXStfwMalformedPacketDropCount`, `MAC1RXStfwMTUErrDropCount`, `MAC1RXStfwOversizePacketDropCount`, `MAC1RXStfwOvflDropCount`, `MAC1RXStfwPayloadLenDropCount`, `MAC1RXStfwSizeErrDropCount`, `MAC1RXStfwSopEopErrDropCount`, `MAC1RXStfwBuff0WatermarkDropCount`, `MAC1RXStfwBuff1WatermarkDropCount`, `MAC1RXStfwBuff2WatermarkDropCount` | Yes |
| 19 | FPGA-PDP-MAC0 Packets Outbound errors | MDM | [OVL2 only] | MDM `GdmaPdpNetBuffMetrics`: `MAC0TXBuff0DropPacketCount`, `MAC0TXBuff1DropPacketCount`, `MAC0TXBuff2DropPacketCount` | Yes |
| 20 | FPGA-PDP-MAC1 Packets Outbound errors | MDM | [OVL2 only] | MDM `GdmaPdpNetBuffMetrics`: `MAC1TXBuff0DropPacketCount`, `MAC1TXBuff1DropPacketCount`, `MAC1TXBuff2DropPacketCount` | Yes |
| 21 | FPGA-PDP Packets Sent | MDM | [OVL2 only] | MDM `GdmaPdpNetBuffMetrics`: `MAC0TXBuff0PacketCount`, `MAC0TXBuff1PacketCount`, `MAC0TXBuff2PacketCount`, `MAC1TXBuff0PacketCount`, `MAC1TXBuff1PacketCount`, `MAC1TXBuff2PacketCount`, `MAC0RXStwfGoodPacketCount`, `MAC1RXStwfGoodPacketCount` | Yes |
| 22 | FPGA-PDP Packets Received | MDM | [OVL2 only] | MDM `GdmaPdpNetBuffMetrics`: `MAC0RXStwfBuff0GoodPacketCount`, `MAC0RXStwfBuff1GoodPacketCount`, `MAC0RXStwfBuff2GoodPacketCount`, `MAC1RXStwfBuff0GoodPacketCount`, `MAC1RXStwfBuff1GoodPacketCount`, `MAC1RXStwfBuff2GoodPacketCount`, `MAC0RXStwfGoodPacketCount`, `MAC1RXStwfGoodPacketCount` | Yes |
| 23 | FPGA-NETWORK-V2 Outbound Traffic | MDM | [OVL2 only] | MDM `FPGA-NETWORK-V2`: `MAC0-Transmit-Count`, `MAC1-Transmit-Count` | Yes |
| 24 | FPGA-NETWORK-V2 Inbound Traffic | MDM | [OVL2 only] | MDM `FPGA-NETWORK-V2`: `MAC0-Receive-Count`, `MAC1-Receive-Count` | Yes |
| 25 | FPGA OVL2 Inbound Errors | MDM | [OVL2 only] | MDM `FPGA-NETWORK-V2`: `MAC0-Receive-FCS-Error`, `MAC1-Receive-FCS-Error` | Yes |
| 26 | NIC Drops | HTML | [Both] | HTML / static description | Yes |
| 27 | Dropped Received/Sent Packets (pNIC/vNIC) Description | HTML | [Both] | HTML / static description | Yes |
| 28 | Packets/Bytes Sent/Received (pNIC/vNIC) Description | HTML | [Both] | HTML / static description | Yes |
| 29 | Packets/Bytes Received (pNIC) | MDM | [Both] | MDM `PhysicalNicMetrics`: `PacketsReceivedRate`, `BytesReceivedRate` | Yes |
| 30 | Packets/Bytes Sent (pNIC) | MDM | [Both] | MDM `PhysicalNicMetrics`: `PacketsSentRate`, `BytesSentRate` | Yes |
| 31 | Dropped Received Packets (pNIC) | MDM | [Both] | MDM `PhysicalNicMetrics`: `PacketsReceivedErrorsRate`, `PacketsReceivedDiscardedRate` | Yes |
| 32 | Dropped Sent Packets (pNIC) | MDM | [Both] | MDM `PhysicalNicMetrics`: `PacketsOutboundDiscardedRate`, `PacketsOutboundErrorsRate` | Yes |
| 33 | Percentage of Dropped Received Packets (pNIC) | MDM | [Both] | MDM `PhysicalNicMetrics` *(OVL2)* / `FPGA-NETWORK` denom variant *(Pre-OVL2)*: `PacketsReceivedErrorsRate / PacketsReceivedRate`, `PacketsReceivedDiscardedRate / PacketsReceivedRate` | Yes |
| 34 | Percentage of Dropped Sent Packets (pNIC) | MDM | [Both] | MDM `PhysicalNicMetrics`: `PacketsOutboundDiscardedRate / PacketsSentRate`, `PacketsOutboundErrorsRate / PacketsSentRate` | Yes |
| 35 | Dropped Received Packets (vNIC) | MDM | [Both] | MDM `VirtualNicMetrics`: `PacketsReceivedErrorsRate`, `PacketsReceivedDiscardedRate` | Yes |
| 36 | Dropped Sent Packets (vNIC) | MDM | [Both] | MDM `VirtualNicMetrics`: `PacketsOutboundDiscardedRate`, `PacketsOutboundErrorsRate` | Yes |
| 37 | Percentage of Dropped Received Packets (vNIC) | MDM | [Both] | MDM `VirtualNicMetrics`: `PacketsReceivedErrorsRate / PacketsReceivedRate`, `PacketsReceivedDiscardedRate / PacketsReceivedRate` | Yes |
| 38 | Percentage of Dropped Sent Packets (vNIC) | MDM | [Both] | MDM `VirtualNicMetrics`: `PacketsOutboundDiscardedRate / PacketsSentRate`, `PacketsOutboundErrorsRate / PacketsSentRate` | Yes |
| 39 | Packets/Bytes Received (vNIC) | MDM | [Pre-OVL2 only] | MDM `VirtualNicMetrics`: `PacketsReceivedRate`, `BytesReceivedRate` | Yes |
| 40 | Packets/Bytes Sent (vNIC) | MDM | [Pre-OVL2 only] | MDM `VirtualNicMetrics`: `PacketsSentRate`, `BytesSentRate` | Yes |
| 41 | Packets Sent/Received (vNIC) | MDM | [OVL2 only] | MDM `VirtualNicMetrics`: `PacketsReceivedRate`, `PacketsSentRate` | Yes |
| 42 | Bytes Sent/Received (vNIC) | MDM | [OVL2 only] | MDM `VirtualNicMetrics`: `BytesReceivedRate`, `BytesSentRate` | Yes |
| 43 | Mellanox NIC counters Description | HTML | [Pre-OVL2 only] | HTML / static description | Yes |
| 44 | Packets/Bytes Received (Mellanox NIC) Description | HTML | [Pre-OVL2 only] | HTML / static description | Yes |
| 45 | Dropped Received Packets (Mellanox NIC) | MDM | [Pre-OVL2 only] | MDM `MlnxAdapterCounters`, `Mlx5TrafficCounters`, `MlnxBusCounters`: `Packets_Received_Errors_Rate`, `Packets_Received_Discarded_Rate`, `Packets_Received_Frame_Length_Error_Rate`, `Packets_Received_Bad_CRC_Error_Rate`, `Packets_Received_Symbol_Error_Rate`, `Packets_Received_Errors`, `Packets_Received_Symbol_Error`, `Packets_Received_Bad_CRC_Error`, `Packets_Received_Discarded_No_Recv_WQEs`, `No_WQE_Drops/sec` | Yes |
| 46 | Dropped Outbound Packets (Mellanox NIC) | MDM | [Pre-OVL2 only] | MDM `MlnxAdapterCounters`, `Mlx5TrafficCounters`: `Packets_Outbound_Errors_Rate`, `Packets_Outbound_Discarded_Rate`, `Packets_Outbound_Errors`, `Packets_Outbound_Discarded` | Yes |
| 47 | Packets/Bytes Received (Mellanox NIC) | MDM | [Pre-OVL2 only] | MDM `MlnxAdapterCounters`, `Mlx5TrafficCounters`: `Bytes_Received_Rate`, `Packets_Received_Rate`, `Bytes_Received`, `Packets_Received` | Yes |
| 48 | Packets/Bytes Sent (Mellanox NIC) | MDM | [Pre-OVL2 only] | MDM `MlnxAdapterCounters`, `Mlx5TrafficCounters`: `Packets_Sent_Rate`, `Bytes_Sent_Rate`, `Bytes_Sent`, `Packets_Sent` | Yes |
| 49 | Percentage of dropped Received Packets (Mellanox NIC) | MDM | [Pre-OVL2 only] | MDM `MlnxAdapterCounters`: `Packets_Received_Errors_Rate / Packets_Received_Rate` | Yes |
| 50 | Percentage of dropped Outbound Packets (Mellanox NIC) | MDM | [Pre-OVL2 only] | MDM `MlnxAdapterCounters`: `Packets_Outbound_Errors_Rate / Packets_Sent_Rate`, `Packets_Outbound_Discarded_Rate / Packets_Sent_Rate` | Yes |
| 51 | BNIC counters Description | HTML | [OVL2 only] | HTML / static description | Yes |
| 52 | Packets Received/Sent (BNIC *) Description tiles | HTML | [OVL2 only] | HTML / static description | Yes |
| 53 | Bytes Received/Sent (BNIC *) Description tiles | HTML | [OVL2 only] | HTML / static description | Yes |
| 54 | Packets Received (BNIC Global/SoC/Host) | MDM | [OVL2 only] | MDM `GdmaBnicGlobalMetrics`, `GdmaBnicPfMetrics`, `GdmaBnicPvfMetrics`: `NumOfInPackets` | Yes |
| 55 | Packets Sent (BNIC Global/SoC/Host) | MDM | [OVL2 only] | MDM `GdmaBnicGlobalMetrics`, `GdmaBnicPfMetrics`, `GdmaBnicPvfMetrics`: `NumOfOutPackets` | Yes |
| 56 | Packets Received (BNIC Vf) | MDM | [OVL2 only] | MDM `GdmaBnicVfMetrics`: `NumOfInPackets` | Yes |
| 57 | Packets Sent (BNIC Vf) | MDM | [OVL2 only] | MDM `GdmaBnicVfMetrics`: `NumOfOutPackets` | Yes |
| 58 | Bytes Received (BNIC Global/SoC/Host) | MDM | [OVL2 only] | MDM `GdmaBnicGlobalMetrics`, `GdmaBnicPfMetrics`, `GdmaBnicPvfMetrics`: `NumOfInOctets` | Yes |
| 59 | Bytes Sent (BNIC Global/SoC/Host) | MDM | [OVL2 only] | MDM `GdmaBnicGlobalMetrics`, `GdmaBnicPfMetrics`, `GdmaBnicPvfMetrics`: `NumOfOutOctets` | Yes |
| 60 | Bytes Received (BNIC Vf) | MDM | [OVL2 only] | MDM `GdmaBnicVfMetrics`: `NumOfInOctets` | Yes |
| 61 | Bytes Sent (BNIC Vf) | MDM | [OVL2 only] | MDM `GdmaBnicVfMetrics`: `NumOfOutOctets` | Yes |
| 62 | Percentage of dropped Received Packets (BNIC Global) | MDM | [OVL2 only] | MDM `GdmaBnicGlobalMetrics`: `InTotalErrors/NumOfInPackets`, `NumOfInDiscardsNoWQE/NumOfInPackets`, `NumOfInErrorsRxVportDisabled/NumOfInPackets`, `NumOfInErrorsSteeringUcast/NumOfInPackets`, `NumOfInErrorsSteeringMcast/NumOfInPackets` | Yes |
| 63 | Percentage of dropped Sent Packets (BNIC Global) | MDM | [OVL2 only] | MDM `GdmaBnicGlobalMetrics`: `OutTotalErrors/NumOfOutPackets`, `NumOfOutErrorsGfDisabled/NumOfOutPackets`, `NumOfOutErrorsVportDisabled/NumOfOutPackets`, `NumOfOutErrorsInvalidVportOffsetPackets/NumOfOutPackets`, `NumOfOutErrorsVlanEnforcement`, `NumOfOutErrorsEthTypeEnforcement`, `NumOfOutErrorsSAEnforcement`, `NumOfOutErrorsSQPDIDEnforcement`, `NumOfOutErrorsCQPDIDEnforcement`, `NumOfOutErrorsMtuViolation`, `NumOfOutErrorsInvalidOob` | Yes |
| 64 | Dropped Received Packets (BNIC Global) | MDM | [OVL2 only] | MDM `GdmaBnicGlobalMetrics`: `InTotalErrors`, `NumOfInDiscardsNoWQE`, `NumOfInErrorsRxVportDisabled`, `NumOfInErrorsSteeringUcast`, `NumOfInErrorsSteeringMcast` | Yes |
| 65 | Dropped Sent Packets (BNIC Global) | MDM | [OVL2 only] | MDM `GdmaBnicGlobalMetrics`: `OutTotalErrors`, `NumOfOutErrorsGfDisabled`, `NumOfOutErrorsVportDisabled`, `NumOfOutErrorsInvalidVportOffsetPackets`, `NumOfOutErrorsVlanEnforcement`, `NumOfOutErrorsEthTypeEnforcement`, `NumOfOutErrorsSAEnforcement`, `NumOfOutErrorsSQPDIDEnforcement`, `NumOfOutErrorsCQPDIDEnforcement`, `NumOfOutErrorsMtuViolation`, `NumOfOutErrorsInvalidOob` | Yes |
| 66 | Percentage of dropped Received Packets (BNIC SoC Pf) | MDM | [OVL2 only] | MDM `GdmaBnicPfMetrics`: `InTotalErrors/NumOfInPackets`, `NumOfInDiscardsNoWQE/NumOfInPackets`, `NumOfInErrorsRxVportDisabled/NumOfInPackets` | Yes |
| 67 | Dropped Received Packets (BNIC SoC Pf) | MDM | [OVL2 only] | MDM `GdmaBnicPfMetrics`: `InTotalErrors`, `NumOfInDiscardsNoWQE`, `NumOfInErrorsRxVportDisabled` | Yes |
| 68 | Percentage of dropped Sent Packets (BNIC SoC Pf) | MDM | [OVL2 only] | MDM `GdmaBnicPfMetrics`, `GdmaRnicPfMetrics`: Same sent-drop percentage family as BNIC Global | Yes |
| 69 | Dropped Sent Packets (BNIC SoC Pf) | MDM | [OVL2 only] | MDM `GdmaBnicPfMetrics`: Same sent-drop family as BNIC Global | Yes |
| 70 | Percentage of dropped Received Packets (BNIC Host Pvf) | MDM | [OVL2 only] | MDM `GdmaBnicPvfMetrics`: Same receive-drop percentage family as BNIC SoC Pf | Yes |
| 71 | Percentage of dropped Sent Packets (BNIC Host Pvf) | MDM | [OVL2 only] | MDM `GdmaBnicPvfMetrics`: Same sent-drop percentage family as BNIC Global | Yes |
| 72 | Dropped Received Packets (BNIC Host Pvf) | MDM | [OVL2 only] | MDM `GdmaBnicPvfMetrics`: `InTotalErrors`, `NumOfInDiscardsNoWQE`, `NumOfInErrorsRxVportDisabled` | Yes |
| 73 | Dropped Sent Packets (BNIC Host Pvf) | MDM | [OVL2 only] | MDM `GdmaBnicPvfMetrics`: Same sent-drop family as BNIC Global | Yes |
| 74 | Percentage of dropped Received Packets (BNIC Vf) | MDM | [OVL2 only] | MDM `GdmaBnicVfMetrics`: Same receive-drop percentage family as BNIC SoC Pf | Yes |
| 75 | Percentage of dropped Sent Packets (BNIC Vf) | MDM | [OVL2 only] | MDM `GdmaBnicVfMetrics`: Same sent-drop percentage family as BNIC Global | Yes |
| 76 | Dropped Received Packets (BNIC Vf) | MDM | [OVL2 only] | MDM `GdmaBnicVfMetrics`: `InTotalErrors`, `NumOfInDiscardsNoWQE`, `NumOfInErrorsRxVportDisabled` | Yes |
| 77 | Dropped Sent Packets (BNIC Vf) | MDM | [OVL2 only] | MDM `GdmaBnicVfMetrics`: Same sent-drop family as BNIC Global | Yes |
| 78 | VFP Drops | HTML | [Both] | HTML / static description | Yes |
| 79 | Description - Inbound/Outbound Packets Drop Metrics | HTML | [Both] | HTML / static description | Yes |
| 80 | Inbound Packets Drop Metrics - Set 1 | MDM | [Both] | MDM `VfpPortDropMetrics`: `DropNonIpPacketInRate`, `DroppedBroadcastLimiterPacketInRate`, `DroppedForwardingPacketInRate`, `DroppedInvalidRulePacketInRate`, `DroppedMacSpoofingPacketInRate`, `DroppedMalformedPacketInRate`, `DroppedResourcesPacketInRate`, `DroppedSimulationPacketInRate`, `DropArpLimiterPacketInRate`, `DropArpGuardPacketInRate` | Yes |
| 81 | Outbound Packets Drop Metrics - Set 1 | MDM | [Both] | MDM `VfpPortDropMetrics`: `DropNonIpPacketOutRate`, `DroppedBroadcastLimiterPacketOutRate`, `DroppedForwardingPacketOutRate`, `DroppedInvalidRulePacketOutRate`, `DroppedMacSpoofingPacketOutRate`, `DroppedMalformedPacketOutRate`, `DroppedResourcesPacketOutRate`, `DroppedSimulationPacketOutRate`, `DropArpLimiterPacketOutRate`, `DropArpGuardPacketOutRate` | Yes |
| 82 | Inbound Packets Drop Metrics - Set 2 | MDM | [Both] | MDM `VfpPortDropMetrics`: `DropArpFilterPacketInRate`, `DropIpv4SpoofingPacketInRate`, `DroppedAclPacketInRate`, `DroppedNoRuleMatchPacketInRate`, `DropIpv6SpoofingPacketInRate`, `DropInvalidPacketInRate`, `DropBlockedPacketInRate`, `DropBroadcastPacketInRate`, `DropDhcpGuardPacketInRate`, `DropDhcpLimiterPacketInRate` | Yes |
| 83 | Outbound Packets Drop Metrics - Set 2 | MDM | [Both] | MDM `VfpPortDropMetrics`: `DropArpFilterPacketOutRate`, `DropIpv4SpoofingPacketOutRate`, `DroppedAclPacketOutRate`, `DroppedNoRuleMatchPacketOutRate`, `DropIpv6SpoofingPacketOutRate`, `DropInvalidPacketOutRate`, `DropBlockedPacketOutRate`, `DropBroadcastPacketOutRate`, `DropDhcpGuardPacketOutRate`, `DropDhcpLimiterPacketOutRate` | Yes |
| 84 | Inbound Packets Drop Metrics - Set 3 | MDM | [Both] | MDM `VfpPortDropMetrics`: `DroppedPendingPacketDtlsInRate`, `DroppedPendingPacketFragInRate`, `DroppedPendingPacketGftInRate`, `DroppedPendingPacketMappingInRate`, `DroppedPendingPacketNatInRate`, `DroppedPendingPacketPARouteInRate`, `DroppedPendingPacketQosInRate`, `DroppedPendingPADiscoveryInRate`, `DroppedExpiredPendedPacketInRate`, `DroppedPendingPacketInRate` | Yes |
| 85 | Outbound Packets Drop Metrics - Set 3 | MDM | [Both] | MDM `VfpPortDropMetrics`: `DroppedPendingPacketDtlsOutRate`, `DroppedPendingPacketFragOutRate`, `DroppedPendingPacketGftOutRate`, `DroppedPendingPacketMappingOutRate`, `DroppedPendingPacketNatOutRate`, `DroppedPendingPacketPARouteOutRate`, `DroppedPendingPacketQosOutRate`, `DroppedPendingPADiscoveryOutRate`, `DroppedExpiredPendedPacketOutRate`, `DroppedPendingPacketOutRate` | Yes |
| 86 | Inbound Packets Drop Metrics - Set 4 | MDM | [Both] | MDM `VfpPortDropMetrics`: `DroppedPADiscoveryPacketsInRate`, `DroppedResourcesLayerFlowMaxFlowsLimitInRate`, `DroppedResourcesMemoryInRate`, `DroppedPARouteRuleInRate`, `DroppedFragPacketInRate`, `DroppedResourcesUnifiedFlowMaxFlowsLimitInRate` | Yes |
| 87 | Outbound Packets Drop Metrics - Set 4 | MDM | [Both] | MDM `VfpPortDropMetrics`: `DroppedRedirectPacketsOutRate`, `DroppedPADiscoveryPacketsOutRate`, `DroppedResourcesLayerFlowMaxFlowsLimitOutRate`, `DroppedResourcesMemoryOutRate`, `DroppedPARouteRuleOutRate`, `DroppedFragPacketOutRate`, `DroppedResourcesUnifiedFlowMaxFlowsLimitOutRate` | Yes |
| 88 | Inbound Packet Drop Metrics - Set 1 | MDM | [Both] | MDM `VmsNicDropMetrics`: `BridgeReservedDropInRate`, `InvalidDataDropInRate`, `InvalidPacketDropInRate`, `ResourceDropInRate`, `NotReadyDropInRate`, `DisconnectedDropInRate`, `NotAcceptedDropInRate`, `BusyDropInRate`, `FilteredDropInRate`, `FilteredVlanDropInRate` | Yes |
| 89 | Outbound Packet Drop Metrics - Set 1 | MDM | [Both] | MDM `VmsNicDropMetrics`: `BridgeReservedDropOutRate`, `InvalidDataDropOutRate`, `InvalidPacketDropOutRate`, `ResourceDropOutRate`, `NotReadyDropOutRate`, `DisconnectedDropOutRate`, `NotAcceptedDropOutRate`, `BusyDropOutRate`, `FilteredDropOutRate`, `FilteredVlanDropOutRate` | Yes |
| 90 | Inbound Packet Drop Metrics - Set 2 | MDM | [Both] | MDM `VmsNicDropMetrics`: `UnauthorizedVlanDropInRate`, `UnauthorizedMacDropInRate`, `SecurityPolicyDropInRate`, `PVlanSettingDropInRate`, `QosDropInRate`, `IpSecDropInRate`, `MacSpoofingDropInRate`, `DhcpGuardDropInRate`, `RouterGuardDropInRate`, `UnknownDropInRate` | Yes |
| 91 | Outbound Packet Drop Metrics - Set 2 | MDM | [Both] | MDM `VmsNicDropMetrics`: Outbound equivalents of the Set 2 receive-drop family (`*OutRate`) | Yes |
| 92 | Inbound Packet Drop Metrics - Set 3 | MDM | [Both] | MDM `VmsNicDropMetrics`: `VirtualSubnetIdDropInRate`, `VfpNotPresentDropInRate`, `InvalidConfigDropInRate`, `MtuMismatchDropInRate`, `NativeForwardingReqDropInRate`, `InvalidVlanFormatDropInRate`, `InvalidDestMacDropInRate`, `InvalidSourceMacDropInRate`, `FirstNbTooSmallDropInRate`, `WnvDropInRate` | Yes |
| 93 | Outbound Packet Drop Metrics - Set 3 | MDM | [Both] | MDM `VmsNicDropMetrics`: Outbound equivalents of the Set 3 receive-drop family (`*OutRate`) | Yes |
| 94 | Inbound Packet Drop Metrics - Set 4 | MDM | [Both] | MDM `VmsNicDropMetrics`: `StormLimitDropInRate`, `InjectedIcmpDropInRate`, `DestListUpdateDropInRate`, `DisabledDropInRate`, `PacketFilterDropInRate`, `SwitchDataDisabledDropInRate`, `FilteredIsoUntaggedDropInRate`, `DroppedPacketsIncomingRate`, `ExtensionsDroppedPacketsOutgoingRate` | Yes |
| 95 | Outbound Packet Drop Metrics - Set 4 | MDM | [Both] | MDM `VmsNicDropMetrics`: `StormLimitDropOutRate`, `InjectedIcmpDropOutRate`, `DestListUpdateDropOutRate`, `DisabledDropOutRate`, `PacketFilterDropOutRate`, `SwitchDataDisabledDropOutRate`, `FilteredIsoUntaggedDropOutRate`, `DroppedPacketsOutgoingRate`, `ExtensionsDroppedPacketsOutgoingRate` | Yes |
| 96 | Metric Description Inbound/Outbound Packets (VFP) | HTML | [Both] | HTML / static description | Yes |
| 97 | Injected Resets Description | HTML | [Pre-OVL2 only] | HTML / static description | Yes |
| 98 | Dropped DNS/DHCP Packets Description | HTML | [Pre-OVL2 only] | HTML / static description | Yes |
| 99 | Inbound Packets (VFP) | MDM | [Both] | MDM `VfpPortMetrics`: `PendingPacketInRate`, `ThrottledPacketInRate`, `TotalPacketInRate`, `InterceptInRate`, `MissedInterceptInRate`, `NonIpPacketInRate`, `TotalMulticastPacketsForwardedInRate`, `TotalPacketHairpinnedInRate`, `TotalUnicastPacketForwardedInRate` | Yes |
| 100 | Outbound Packets (VFP) | MDM | [Both] | MDM `VfpPortMetrics`: `PendingPacketOutRate`, `ThrottledPacketOutRate`, `TotalPacketOutRate`, `InterceptOutRate`, `MissedInterceptOutRate`, `NonIpPacketOutRate`, `TotalMulticastPacketsForwardedOutRate`, `TotalPacketHairpinnedOutRate`, `TotalUnicastPacketForwardedOutRate` | Yes |
| 101 | Backplane Metrics (Number of Errors Received and Transmitted) | MDM | [Both] | MDM `BACKPLANE-METRICS`: `NumOfErrorsReceived`, `NumOfErrorsTransmitted`, `NumOfMissedErrorsReceived` | Yes |
| 102 | Injected resets (VFP) | MDM | [Both — Pre-OVL2 has extra ResetResponse metrics] | MDM `VfpPortDropMetrics` *(both)* / `VfpPortMetrics` *(legacy extra metrics)*: `TcpConnectionsResetByInjectedResetInRate`, `TcpConnectionsResetByInjectedResetOutRate`; Pre-OVL2 also adds `TcpConnectionsResetByResetResponseInRate`, `TcpConnectionsResetByResetResponseOutRate` | Yes |
| 103 | Injected resets cause | MDM | [Pre-OVL2 only] | MDM `VfpPortMetrics`: `TcpConnectionsResetHalfTTLInRate`, `TcpConnectionsResetHalfTTLOutRate`, `NonSynStatefulNatsInRate`, `NonSynStatefulNatsOutRate`, `UFsXvlanLmResetInjectedInRate`, `UFsXvlanLmResetInjectedOutRate`, `UFsXvlanLmResetReInjectedInRate`, `UFsXvlanLmResetReInjectedOutRate`, `UFsXvlanLmResetsFailedInRate`, `UFsXvlanLmResetsFailedOutRate` | Yes |
| 104 | Dropped DNS/DHCP In Rate | MDM | [Pre-OVL2 only] | MDM `VfpPortDropMetrics`: `DroppedDhcpPacketsInRate`, `DroppedDnsPacketsInRate` | Yes |
| 105 | Dropped DNS/DHCP Out Rate | MDM | [Pre-OVL2 only] | MDM `VfpPortDropMetrics`: `DroppedDhcpPacketsOutRate`, `DroppedDnsPacketsOutRate` | Yes |