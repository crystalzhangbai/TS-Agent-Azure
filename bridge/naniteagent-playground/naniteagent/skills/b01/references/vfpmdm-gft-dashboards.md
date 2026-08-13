# VfpMDM GFTDashboards — Merged Tile Reference

> 📋 **Merged Dashboard** — This reference combines tiles from 4 GFT sub-dashboards: FlowOffloadDashboard, GftNodeDashboard, GftPortDashboard, GftVfpPortDashboard. Each tile is tagged with its source dashboard(s). Where tiles overlap between GftPort and GftVfpPort, the union of all metrics is shown.

**Dashboards:** `VfpMDM / GFTDashboards/FlowOffloadDashboard`, `VfpMDM / GFTDashboards/GftNodeDashboard`, `VfpMDM / GFTDashboards/GftPortDashboard`, `VfpMDM / GFTDashboards/GftVfpPortDashboard`  
**Source JSON:** `VfpMDM_GFTDashboards_FlowOffloadDashboard.json`, `VfpMDM_GFTDashboards_GftNodeDashboard.json`, `VfpMDM_GFTDashboards_GftPortDashboard.json`, `VfpMDM_GFTDashboards_GftVfpPortDashboard.json`  
**Raw Tile Counts:** 62 total — 51 MDM, 11 HTML / static, 0 Kusto, 0 Mixed  
**Merged Reference Counts:** 58 entries — 47 MDM, 11 HTML / static, 0 Kusto, 0 Mixed

## Template Parameters

| Name | Display Name | Type | Default / Example | Used As | Affected Tiles |
|------|-------------|------|-------------------|---------|----------------|
| `Account` | Account | string | ` (all) ` — resolves to e.g. `VfpMdmAM` | MDM `account` field override | All MDM tiles |
| `Cluster` | Cluster | string | *(empty)* | Dimension filter `Cluster` | All MDM tiles |
| `NodeId` | NodeId | string | *(empty)* | Dimension filter `NodeId` | All MDM tiles |
| `ContainerId` | ContainerId | string | *(empty)* | Dimension filter `ContainerId` | FlowOffload, GftPort, GftVfpPort tiles |

**Hint queries / resolvers:**
- `Account` — pattern filter `VfpMdm*`
- `Cluster` — MDM hint from `VfpMdm*`, dimension `Cluster`
- `NodeId` — MDM hint from `VfpMdm*`, dimension `NodeId`
- `ContainerId` — pattern `*` in GftVfpPort and `VfpMdm*` in FlowOffload / GftPort

**MDM Namespaces Used:** `VfpPortGftMetrics`, `VfpPortMetrics`, `GFTVPort`, `GFTLWF`, `FPGA-GFT`

---

## 1. Overview & State

### Tile 1 — Description
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Source** | [FlowOffload] |
| **Content** | Dashboard description tile summarizing GFT flow-offload aggregation counters and how the dashboard should be used. |

---
### Tile 2 — Overview
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Source** | [FlowOffload] |
| **Content** | Section header for the overview metrics area. |

---
### Tile 3 — Total Flows
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [FlowOffload] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics` |
| **Metric(s)** | `SharedGftNumOffloadedFlowEntries`, `GftOffloadLimit` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---
### Tile 4 — GFT State
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [GftVfpPort] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics` |
| **Metric(s)** | `GftInUse`, `DscpGuardsConfigFailed`, `VxlanConfigFailed`, `MacFilterSet`, `VPortPresent`, `GftMultiTenancyConfigFailed`, `MultitenancyEnabled`, `IsUntaggedOrZeroFilterRemoved` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---
### Tile 5 — GFT VPort State
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [GftPort] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `GFTVPort` |
| **Metric(s)** | `NumCurrentFlows`, `GftEnabled`, `MacAddressSet`, `VfEnabled`, `NumGftCurrentTunnelObjects`, `NumGftCurrentDtlsEncryptionTunnelObjects` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---
### Tile 6 — GFT Node State
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [GftNode] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `GFTLWF` |
| **Metric(s)** | `LocalVPortOffloadsEnabled` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |

---
### Tile 7 — GFT Node Flow and Error Counters
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [GftNode] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `GFTLWF` |
| **Metric(s)** | `NumSoftwareReset`, `NumIngressCorruptDramFlowCount`, `NumGftL2FlowTableFull`, `NumGftL2CacheLineFull`, `NumGftL2CacheCollisions`, `NumGftIngressTotalOffloadedFlows`, `NumGftEgressTotalOffloadedFlows`, `NumEgressCorruptDramFlowCount`, `NumGftDropInvalidPacket`, `NumGftFpgaSlotErrors`, `NumGftEgressTotalOffloadedLocalVPortFlows`, `NumGftIngressTotalOffloadedLocalVPortFlows`, `NumGftFpgaFlowStateBitIncorrect`, `NumGftFpgaDataSizeMismatchError`, `NumGftFpgaActionMatchCountZero` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |

---

## 2. Flow Offload Success / Failed / Blocked / Retry

### Tile 8 — Flow Offload Reasons (Error Legend)
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Source** | [FlowOffload] |
| **Content** | Explains Generic Error, GenID Mismatch, hardware/software errors, half-open TCP, and other offload-failure meanings. |

---
### Tile 9 — Flow Offload Reasons (Success / Blocked / Failed Guide)
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Source** | [FlowOffload] |
| **Content** | Describes the Success / Blocked / Failed reason families used across the flow-offload tiles. |

---
### Tile 10 — Overview Metrics Rate Outbound
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [FlowOffload] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics` |
| **Metric(s)** | `GftNumOffloadBlockedOutRate`, `GftNumTotalOffloadFlowsOutRate`, `GftNumOffloadFlowEntryFailedOutRate`, `GftNumOffloadProfileFailedOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---
### Tile 11 — Overview Metrics Rate Inbound
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [FlowOffload] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics` |
| **Metric(s)** | `GftNumOffloadBlockedInRate`, `GftNumTotalOffloadFlowsInRate`, `GftNumOffloadFlowEntryFailedInRate`, `GftNumOffloadProfileFailedInRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---
### Tile 12 — Flow Offload Success Reasons (Inbound)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [FlowOffload] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics`, `VfpPortMetrics` |
| **Metric(s)** | `GftNumTotalOffloadReasonConnEstablishedInRate`, `GftNumTotalOffloadReasonReconciliationInRate`, `GftNumTotalOffloadReasonTimerInRate`, `GftNumTotalOffloadReasonDtlsSessionEstablishedInRate`, `GftNumTotalOffloadReasonModifyInRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---
### Tile 13 — Flow Offload Success Reasons (Outbound)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [FlowOffload] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics`, `VfpPortMetrics` |
| **Metric(s)** | `GftNumTotalOffloadReasonConnEstablishedOutRate`, `GftNumTotalOffloadReasonReconciliationOutRate`, `GftNumTotalOffloadReasonTimerOutRate`, `GftNumTotalOffloadReasonDtlsSessionEstablishedOutRate`, `GftNumTotalOffloadReasonModifyOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---
### Tile 14 — Flow Offload Failed Reasons (Inbound)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [FlowOffload] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics`, `FPGA-GFT` |
| **Metric(s)** | `GftNumTotalOffloadFailedGenericErrorInRate`, `GftNumTotalOffloadFailedGenIDMismatchInRate`, `GftNumTotalOffloadFailedGftHWInRate`, `GftNumTotalOffloadFailedGftSWInRate`, `GftNumTotalOffloadFailedTCPHalfOpenInRate`, `IndirectionUnitHashCollisionCount`, `GftNumTotalOffloadLimitReachedInRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---
### Tile 15 — Flow Offload Failed Reasons (Outbound)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [FlowOffload] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics`, `FPGA-GFT` |
| **Metric(s)** | `GftNumTotalOffloadFailedGenericErrorOutRate`, `GftNumTotalOffloadFailedGenIDMismatchOutRate`, `GftNumTotalOffloadFailedGftHWOutRate`, `GftNumTotalOffloadFailedGftSWOutRate`, `GftNumTotalOffloadFailedTCPHalfOpenOutRate`, `IndirectionUnitHashCollisionCount`, `GftNumTotalOffloadLimitReachedOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---
### Tile 16 — Flow Offload Retry Reason Breakdown (Inbound)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [FlowOffload] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics` |
| **Metric(s)** | `GftNumTotalRetryReasonMeteringNotOffloadedInRate`, `GftNumTotalOffloadRetryReasonMeteringNotOffloadedInRate`, `GftNumTotalOffloadRetryReasonFlowOffloadFailedInRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---
### Tile 17 — Flow Offload Retry Reason Breakdown (Outbound)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [FlowOffload] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics` |
| **Metric(s)** | `GftNumTotalRetryReasonMeteringNotOffloadedOutRate`, `GftNumTotalOffloadRetryReasonMeteringNotOffloadedOutRate`, `GftNumTotalOffloadRetryReasonFlowOffloadFailedOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---
### Tile 18 — Retried Offloaded Flows
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [GftVfpPort] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics` |
| **Metric(s)** | `GftNumTotalOffloadRetryReasonFlowOffloadFailedInRate`, `GftNumTotalOffloadRetryReasonFlowOffloadFailedOutRate`, `GftNumTotalOffloadRetryReasonMeteringNotOffloadedInRate`, `GftNumTotalOffloadRetryReasonMeteringNotOffloadedOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---
## 3. Packet Counters (Node Level)

### Tile 21 — GFT Parser Counters
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [GftNode] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `FPGA-GFT` |
| **Metric(s)** | `ParserCounterNicpacketCount`, `ParserCounterTorpacketCount` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |

---
### Tile 22 — GFT IN Node Packet Counters
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [GftNode] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `GFTLWF` |
| **Metric(s)** | `NumEgressDefaultVPort`, `NumEgressNonDefaultVPort`, `NumGftDropEgressCopyIncorrectVPortId`, `NumGftDropEgressCopyVPortIdDisabled`, `NumGftDropEgressExcDefaultVPortId`, `NumGftDropEgressExcIncorrectVPortId`, `NumGftDropEgressExcVPortIdDisabled`, `NumGftEgressCopyPackets`, `NumGftEgressExcCohortNotFound`, `NumGftEgressExcFlowNotFound`, `NumGftEgressExcFragPackets`, `NumGftEgressExcNoVportFound`, `NumGftEgressExcSyn` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |

---
### Tile 23 — GFT OUT Node Packet Counters
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [GftNode] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `GFTLWF` |
| **Metric(s)** | `NumGftDropIngressCopyChecksumFailed`, `NumGftDropIngressCopyIncorrectVPortId`, `NumGftDropIngressCopyVPortIdDisabled`, `NumGftDropIngressExcChecksumFailed`, `NumGftDropIngressExcDefaultVPortId`, `NumGftDropIngressExcIncorrectVPortId`, `NumGftDropIngressExcVPortIdDisabled`, `NumGftDropIngressExcVPortNotFound`, `NumGftIngressCopyPackets`, `NumGftIngressExcBcMc`, `NumGftIngressExcCohortNotFound`, `NumGftIngressExcFlowNotFound`, `NumGftIngressExcGftDisabled`, `NumGftIngressExcSyn` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |

---
### Tile 24 — GFT OUT Node Packet Counters - Description
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Source** | [GftNode] |
| **Content** | Placeholder description tile associated with node-level outbound packet counters. |

---
### Tile 25 — GFT Cache Counters
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [GftNode] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `FPGA-GFT` |
| **Metric(s)** | `LookupCounterL1cachemissCount`, `LookupCounterL1lookupCount`, `LookupCounterL2cachemissCount`, `LookupCounterL2lookupCount`, `LookupCounterTotalpacketCount`, `LookupCounterFlowmatchCount` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |

---
### Tile 26 — GftLwf VLAN Packet Drops
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [GftNode] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `GFTLWF` |
| **Metric(s)** | `NumGftDropIngressCopyVlanNotAllowed`, `NumGftDropIngressCopyVlanStripFailed`, `NumGftDropIngressExcVlanNotAllowed`, `NumGftDropIngressExcVlanStripFailed` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |

---

## 4. Packet Counters (VPort Level)

### Tile 27 — GFT IN Vport Packet Counters
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [GftPort + GftVfpPort] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics`, `GFTVPort` |
| **Metric(s)** | `GftCopyPacketsInRate`, `GftCopyResetPacketsInRate`, `GftCopyFinPacketsInRate`, `GftDropCopyPacketsInRate`, `GftExceptionPacketsInRate`, `GftDropExceptionPacketsInRate`, `GftExceptionUFPacketsInRate`, `GftExceptionUFOffloadedPacketsInRate`, `GftExceptionUFOffloadPendingPacketsInRate`, `GftExceptionUFOffloadFailedPacketsInRate`, `GftExceptionUFOffloadDeferredPacketsInRate`, `GftExceptionUFOffloadBlockedPacketsInRate`, `NumGftEgressCopyPackets`, `NumGftEgressExcFlowNotFound`, `NumGftEgressExcCohortNotFound`, `NumGftEgressExcFragPackets`, `NumGftEgressExcSyn`, `NumGftEgressExcTunnelNotFound`, `NumGftEgressExcDtlsPlainText`, `NumGftEgressExcPostDecrypt` |
| **Sampling Type** | Sum |
| **Note** | GftVfpPort contributes the `VfpPortGftMetrics` subset; GftPort adds `GFTVPort` packet / tunnel / DTLS counters. |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---
### Tile 28 — GFT OUT VPort Packet counters
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [GftPort + GftVfpPort] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics`, `GFTVPort` |
| **Metric(s)** | `GftCopyPacketsOutRate`, `GftCopyResetPacketsOutRate`, `GftCopyFinPacketsOutRate`, `GftDropCopyPacketsOutRate`, `GftExceptionPacketsOutRate`, `GftDropExceptionPacketsOutRate`, `GftExceptionUFPacketsOutRate`, `GftExceptionUFOffloadedPacketsOutRate`, `GftExceptionUFOffloadPendingPacketsOutRate`, `GftExceptionUFOffloadFailedPacketsOutRate`, `GftExceptionUFOffloadDeferredPacketsOutRate`, `GftExceptionUFOffloadBlockedPacketsOutRate`, `NumGftIngressCopyPackets`, `NumGftIngressExcCohortNotFound`, `NumGftIngressExcFragPackets`, `NumGftIngressExcFlowNotFound`, `NumGftIngressExcSyn`, `NumGftIngressExcTunnelNotFound` |
| **Sampling Type** | Sum |
| **Note** | GftVfpPort contributes the `VfpPortGftMetrics` subset; GftPort adds `GFTVPort` packet and tunnel counters. |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---

## 5. Exception & Copy Packets

### Tile 29 — Reasons for Exception/Copy Packets
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Source** | [FlowOffload] |
| **Content** | Investigation guidance for interpreting exception versus copy packet families. |

---
### Tile 30 — UF Exception Packet Breakdown by Protocol
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Source** | [FlowOffload] |
| **Content** | Explains the aggregate UF exception metrics and the TCP / UDP / ESP / ICMP protocol breakdown tiles. |

---
### Tile 31 — Exception & Copy Packet
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Source** | [FlowOffload] |
| **Content** | Section header for exception and copy packet analysis. |

---
### Tile 32 — Copy Packet Categories (Inbound Rate)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [FlowOffload] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics` |
| **Metric(s)** | `GftCopyPacketsInRate`, `GftDropCopyPacketsInRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |
| **Additional Dimensions** | `MacAddress`, `VNetId` |

---
### Tile 33 — CopyPacket Categories (Outbound Rate)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [FlowOffload] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics` |
| **Metric(s)** | `GftCopyPacketsOutRate`, `GftDropCopyPacketsOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---
### Tile 34 — Exception Packet Categories (Inbound Rate)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [FlowOffload] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics` |
| **Metric(s)** | `GftExceptionUFPacketsInRate`, `GftExceptionUFOffloadFailedPacketsInRate`, `GftExceptionUFOffloadBlockedPacketsInRate`, `GftExceptionUFOffloadPendingPacketsInRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---
### Tile 35 — Exception Packet Categories (Outbound Rate)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [FlowOffload] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics` |
| **Metric(s)** | `GftExceptionUFPacketsOutRate`, `GftExceptionUFOffloadFailedPacketsOutRate`, `GftExceptionUFOffloadBlockedPacketsOutRate`, `GftExceptionUFOffloadPendingPacketsOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---
### Tile 36 — OFFLOADED - GftExceptionUFPackets Protocol (Inbound Rate)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [FlowOffload] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics`, `VfpPortMetrics`, `GFTVPort` |
| **Metric(s)** | `GftExceptionUFOffloadedTCPPacketsInRate`, `GftExceptionUFOffloadedUDPPacketsInRate`, `GftExceptionUFOffloadedESPPacketsInRate`, `GftExceptionICMPPacketsInRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---
### Tile 37 — OFFLOADED - GftExceptionUFPackets Protocol (Outbound Rate)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [FlowOffload] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics`, `VfpPortMetrics`, `GFTVPort` |
| **Metric(s)** | `GftExceptionUFOffloadedTCPPacketsOutRate`, `GftExceptionUFOffloadedUDPPacketsOutRate`, `GftExceptionUFOffloadedESPPacketsOutRate`, `GftExceptionICMPPacketsOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---
### Tile 38 — BLOCKED - GftExceptionUFOffloadBlockedPackets Protocol (Inbound Rate)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [FlowOffload] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `GFTVPort` |
| **Metric(s)** | `GftExceptionUFOffloadBlockedTCPPacketsInRate`, `GftExceptionUFOffloadBlockedUDPPacketsInRate`, `GftExceptionUFOffloadBlockedESPPacketsInRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---
### Tile 39 — BLOCKED - GftExceptionUFOffloadBlockedPackets Protocol (Outbound Rate)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [FlowOffload] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `GFTVPort` |
| **Metric(s)** | `GftExceptionUFOffloadBlockedTCPPacketsOutRate`, `GftExceptionUFOffloadBlockedUDPPacketsOutRate`, `GftExceptionUFOffloadBlockedESPPacketsOutRate` |
| **Sampling Type** | Sum |
| **Note** | Original dashboard title said “Inbound” but the metrics are all `*OutRate`; the merged reference normalizes the title to Outbound. |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---
### Tile 40 — FAILED - GftExceptionUFOffloadFailedPackets Protocol (Inbound Rate)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [FlowOffload] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `GFTVPort` |
| **Metric(s)** | `GftExceptionUFOffloadFailedTCPPacketsInRate`, `GftExceptionUFOffloadFailedUDPPacketsInRate`, `GftExceptionUFOffloadFailedESPPacketsInRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---
### Tile 41 — FAILED - GftExceptionUFOffloadFailedPackets Protocol (Outbound Rate)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [FlowOffload] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `GFTVPort` |
| **Metric(s)** | `GftExceptionUFOffloadFailedTCPPacketsOutRate`, `GftExceptionUFOffloadFailedUDPPacketsOutRate`, `GftExceptionUFOffloadFailedESPPacketsOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---
### Tile 42 — Midstream Exception Packets (Inbound Rate)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [FlowOffload] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics` |
| **Metric(s)** | `MidstreamPacketsForGenIDMismatchInRate`, `MidstreamPacketsForGftHWErrorInRate`, `MidstreamPacketsForHashCollisionInRate`, `TcpMidstreamPacketsForHalfOpenConnInRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---
### Tile 43 — Midstream Exception Packets (Outbound Rate)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [FlowOffload] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics` |
| **Metric(s)** | `MidstreamPacketsForGenIDMismatchOutRate`, `MidstreamPacketsForGftHWErrorOutRate`, `MidstreamPacketsForHashCollisionOutRate`, `TcpMidstreamPacketsForHalfOpenConnOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---

## 6. Flow Offload Counters (VPort Level)

### Tile 44 — GFT IN VPort Flow Offloads counters
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [GftPort + GftVfpPort] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics`, `GFTVPort` |
| **Metric(s)** | `GftNumTotalOffloadFlowsInRate`, `GftNumTotalOffloadReasonReconciliationInRate`, `GftNumTotalOffloadReasonDeferredInRate`, `GftNumTotalOffloadReasonConnEstablishedInRate`, `GftNumTotalOffloadReasonTimerInRate`, `GftNumOffloadProfileFailedInRate`, `GftNumOffloadFlowEntryFailedInRate`, `GftNumOffloadBlockedInRate`, `GftNumTotalUFReoffloadReqdInRate`, `NumGftEgressTotalOffloadedFlows`, `NumGftEgressTotalOffloadedLocalVPortFlows`, `NumGftEgressTotalLocalVPortFlowsFailedOffload` |
| **Sampling Type** | Sum |
| **Note** | GftPort adds `GFTVPort` totals for local-vPort flow state; GftVfpPort adds `GftNumTotalUFReoffloadReqdInRate`. |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---
### Tile 45 — GFT OUT VPort Flow Offload Counters
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [GftPort + GftVfpPort] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics`, `GFTVPort` |
| **Metric(s)** | `GftNumTotalOffloadFlowsOutRate`, `GftNumTotalOffloadReasonReconciliationOutRate`, `GftNumTotalOffloadReasonDeferredOutRate`, `GftNumTotalOffloadReasonConnEstablishedOutRate`, `GftNumTotalOffloadReasonTimerOutRate`, `GftNumOffloadProfileFailedOutRate`, `GftNumOffloadFlowEntryFailedOutRate`, `GftNumOffloadBlockedOutRate`, `GftNumTotalUFReoffloadReqdOutRate`, `NumGftIngressTotalOffloadedFlows`, `NumGftIngressTotalOffloadedLocalVPortFlows`, `NumGftIngressTotalLocalVPortFlowsFailedOffload` |
| **Sampling Type** | Sum |
| **Note** | GftPort adds `GFTVPort` totals for local-vPort flow state; GftVfpPort adds `GftNumTotalUFReoffloadReqdOutRate`. |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---

## 7. Blocked Flow Offloads (VPort Level)

### Tile 46 — Flow Offloads Blocked
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Source** | [FlowOffload] |
| **Content** | Section header for blocked-flow-offload metrics. |

---
### Tile 47 — Flow Offload Blocked Breakdown (Inbound)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [FlowOffload] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics` |
| **Metric(s)** | `GftNumTotalOffloadBlockReasonLocalDestInRate`, `GftNumTotalOffloadBlockReasonLocalSourceInRate`, `GftNumTotalOffloadBlockReasonMissingActionsInRate`, `GftNumTotalOffloadBlockReasonMultiTenancyInRate`, `GftNumTotalOffloadBlockReasonMultipleMeteringInRate`, `GftNumTotalOffloadBlockReasonQoSInRate`, `GftNumTotalOffloadBlockReasonDtlsInRate`, `GftNumTotalOffloadBlockReasonUnsupportedActionInRate`, `GftNumTotalOffloadBlockReasonEncryptedVxlanInRate`, `GftNumTotalOffloadBlockReasonDnsTrafficInRate`, `GftNumTotalOffloadBlockReasonUdpUseVxlanDestPortInRate`, `GftNumTotalOffloadBlockReasonConfigVxlanFailedInRate`, `GftNumTotalOffloadBlockReasonDoubleEncapEspInRate`, `GftNumTotalOffloadBlockReasonHairpinMirrorInRate`, `GftNumTotalOffloadBlockReasonMulticastInRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---
### Tile 48 — Flow Offload Blocked Breakdown (Outbound)
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [FlowOffload] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics` |
| **Metric(s)** | `GftNumTotalOffloadBlockReasonLocalDestOutRate`, `GftNumTotalOffloadBlockReasonLocalSourceOutRate`, `GftNumTotalOffloadBlockReasonMissingActionsOutRate`, `GftNumTotalOffloadBlockReasonMultiTenancyOutRate`, `GftNumTotalOffloadBlockReasonMultipleMeteringOutRate`, `GftNumTotalOffloadBlockReasonQoSOutRate`, `GftNumTotalOffloadBlockReasonDtlsOutRate`, `GftNumTotalOffloadBlockReasonUnsupportedActionOutRate`, `GftNumTotalOffloadBlockReasonEncryptedVxlanOutRate`, `GftNumTotalOffloadBlockReasonDnsTrafficOutRate`, `GftNumTotalOffloadBlockReasonUdpUseVxlanDestPortOutRate`, `GftNumTotalOffloadBlockReasonConfigVxlanFailedOutRate`, `GftNumTotalOffloadBlockReasonDoubleEncapEspOutRate`, `GftNumTotalOffloadBlockReasonHairpinMirrorOutRate`, `GftNumTotalOffloadBlockReasonMulticastOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---
### Tile 49 — GFT IN VPort Blocked Flow Offload Counters
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [GftVfpPort] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics` |
| **Metric(s)** | `GftNumOffloadBlockedInRate`, `GftNumTotalOffloadBlockReasonLocalDestInRate`, `GftNumTotalOffloadBlockReasonLocalSourceInRate`, `GftNumTotalOffloadBlockReasonMissingActionsInRate`, `GftNumTotalOffloadBlockReasonMultiTenancyInRate`, `GftNumTotalOffloadBlockReasonMultipleMeteringInRate`, `GftNumTotalOffloadBlockReasonQoSInRate`, `GftNumTotalOffloadBlockReasonDtlsInRate`, `GftNumTotalOffloadBlockReasonUnsupportedActionInRate`, `GftNumTotalOffloadBlockReasonEncryptedVxlanInRate`, `GftNumTotalOffloadBlockReasonDnsTrafficInRate`, `GftNumTotalOffloadBlockReasonUdpUseVxlanDestPortInRate`, `GftNumTotalOffloadBlockReasonConfigVxlanFailedInRate`, `GftNumTotalOffloadBlockReasonDoubleEncapEspInRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---
### Tile 50 — GFT OUT VPort Blocked Flow Offload Counters
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [GftVfpPort] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics` |
| **Metric(s)** | `GftNumOffloadBlockedOutRate`, `GftNumTotalOffloadBlockReasonLocalDestOutRate`, `GftNumTotalOffloadBlockReasonLocalSourceOutRate`, `GftNumTotalOffloadBlockReasonMissingActionsOutRate`, `GftNumTotalOffloadBlockReasonMultiTenancyOutRate`, `GftNumTotalOffloadBlockReasonMultipleMeteringOutRate`, `GftNumTotalOffloadBlockReasonQoSOutRate`, `GftNumTotalOffloadBlockReasonDtlsOutRate`, `GftNumTotalOffloadBlockReasonUnsupportedActionOutRate`, `GftNumTotalOffloadBlockReasonEncryptedVxlanOutRate`, `GftNumTotalOffloadBlockReasonDnsTrafficOutRate`, `GftNumTotalOffloadBlockReasonUdpUseVxlanDestPortOutRate`, `GftNumTotalOffloadBlockReasonConfigVxlanFailedOutRate`, `GftNumTotalOffloadBlockReasonDoubleEncapEspOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---

## 8. Traffic & Byte Counters

### Tile 51 — GFT Packet Counters
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [GftVfpPort] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics` |
| **Metric(s)** | `GftTotalPacketsInRate`, `GftTotalPacketsOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---
### Tile 52 — GFT Byte Counters
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [GftVfpPort] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics` |
| **Metric(s)** | `GftTotalBytesInRate`, `GftTotalBytesOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---
### Tile 53 — GFT Container Offload Counters
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [GftVfpPort] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics` |
| **Metric(s)** | `GftOffloadLimit`, `SharedGftNumOffloadedFlowEntries` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |
| **Note** | Same metric pair as FlowOffload tile **Total Flows**, but kept as a separate entry because the original tile title and placement differ. |

---
### Tile 54 — GFT Rule Counter Allocated
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [GftVfpPort] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics` |
| **Metric(s)** | `GftNumRuleCounterAllocated` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---

## 9. Configuration

### Tile 55 — Flow Offloads Retry
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Source** | [FlowOffload] |
| **Content** | Section header for retry and delayed-offload analysis. |

---
### Tile 56 — Flow Buffer Errors
| Field | Value |
|-------|-------|
| **Type** | HTML / MarkDown |
| **Source** | [FlowOffload] |
| **Content** | Describes flow-buffer construction in GFT software and why each error class matters. |

---
### Tile 19 — Re-Offload Requests
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [GftVfpPort] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics` |
| **Metric(s)** | `GftNumTotalUFReoffloadReqdInRate`, `GftNumTotalUFReoffloadReqdOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---
### Tile 20 — Delayed Offloads
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [GftVfpPort] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics` |
| **Metric(s)** | `GftNumTotalRetryReasonMeteringNotOffloadedInRate`, `GftNumTotalRetryReasonMeteringNotOffloadedOutRate`, `GftNumTotalRetryReasonOffloadFailedInRate`, `GftNumTotalRetryReasonOffloadFailedOutRate` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---
### Tile 57 — Flow Buffer Error Metrics
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [FlowOffload] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `GFTLWF` |
| **Metric(s)** | `GftCreateFlowBufInvalidDTLSHeader`, `GftCreateFlowBufIncorrectActionInvalidParameters`, `GftCreateFlowBufMissingHeaderFieldsPushAction`, `GftCreateFlowBufMissingHeaderFieldsPopAction`, `GftCreateFlowBufMissingHeaderFieldsModifyAction`, `GftCreateFlowBufMissingHeaderFieldsIgnoreAction` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}` |

---
### Tile 58 — Multitenancy Allowed VLANs Config
| Field | Value |
|-------|-------|
| **Type** | MDM grid |
| **Source** | [GftVfpPort] |
| **Data Source** | MDM |
| **MDM Account** | Dynamic — from `{Account}` parameter |
| **MDM Namespace** | `VfpPortGftMetrics` |
| **Metric(s)** | `MultitenancyUseVlanMask`, `MultitenancyUseVlanRangeMaxValue`, `MultitenancyUseVlanRangeMinValue`, `MultitenancyVlanMask`, `MultitenancyVlanRangeMaxValue`, `MultitenancyVlanRangeMinValue` |
| **Sampling Type** | Sum |
| **Dimension Filter** | `Cluster` = `{Cluster}`, `NodeId` = `{NodeId}`, `ContainerId` = `{ContainerId}` |

---

## Summary

| Tile # | Title | Type | Source | Section |
|-------:|-------|------|--------|---------|
| 1 | Description | HTML | FlowOffload | Overview & State |
| 2 | Overview | HTML | FlowOffload | Overview & State |
| 3 | Total Flows | MDM | FlowOffload | Overview & State |
| 4 | GFT State | MDM | GftVfpPort | Overview & State |
| 5 | GFT VPort State | MDM | GftPort | Overview & State |
| 6 | GFT Node State | MDM | GftNode | Overview & State |
| 7 | GFT Node Flow and Error Counters | MDM | GftNode | Overview & State |
| 8 | Flow Offload Reasons (Error Legend) | HTML | FlowOffload | Flow Offload Success / Failed / Blocked / Retry |
| 9 | Flow Offload Reasons (Success / Blocked / Failed Guide) | HTML | FlowOffload | Flow Offload Success / Failed / Blocked / Retry |
| 10 | Overview Metrics Rate Outbound | MDM | FlowOffload | Flow Offload Success / Failed / Blocked / Retry |
| 11 | Overview Metrics Rate Inbound | MDM | FlowOffload | Flow Offload Success / Failed / Blocked / Retry |
| 12 | Flow Offload Success Reasons (Inbound) | MDM | FlowOffload | Flow Offload Success / Failed / Blocked / Retry |
| 13 | Flow Offload Success Reasons (Outbound) | MDM | FlowOffload | Flow Offload Success / Failed / Blocked / Retry |
| 14 | Flow Offload Failed Reasons (Inbound) | MDM | FlowOffload | Flow Offload Success / Failed / Blocked / Retry |
| 15 | Flow Offload Failed Reasons (Outbound) | MDM | FlowOffload | Flow Offload Success / Failed / Blocked / Retry |
| 16 | Flow Offload Retry Reason Breakdown (Inbound) | MDM | FlowOffload | Flow Offload Success / Failed / Blocked / Retry |
| 17 | Flow Offload Retry Reason Breakdown (Outbound) | MDM | FlowOffload | Flow Offload Success / Failed / Blocked / Retry |
| 18 | Retried Offloaded Flows | MDM | GftVfpPort | Flow Offload Success / Failed / Blocked / Retry |
| 19 | Re-Offload Requests | MDM | GftVfpPort | Configuration |
| 20 | Delayed Offloads | MDM | GftVfpPort | Configuration |
| 21 | GFT Parser Counters | MDM | GftNode | Packet Counters (Node Level) |
| 22 | GFT IN Node Packet Counters | MDM | GftNode | Packet Counters (Node Level) |
| 23 | GFT OUT Node Packet Counters | MDM | GftNode | Packet Counters (Node Level) |
| 24 | GFT OUT Node Packet Counters - Description | HTML | GftNode | Packet Counters (Node Level) |
| 25 | GFT Cache Counters | MDM | GftNode | Packet Counters (Node Level) |
| 26 | GftLwf VLAN Packet Drops | MDM | GftNode | Packet Counters (Node Level) |
| 27 | GFT IN Vport Packet Counters | MDM | GftPort + GftVfpPort | Packet Counters (VPort Level) |
| 28 | GFT OUT VPort Packet counters | MDM | GftPort + GftVfpPort | Packet Counters (VPort Level) |
| 29 | Reasons for Exception/Copy Packets | HTML | FlowOffload | Exception & Copy Packets |
| 30 | UF Exception Packet Breakdown by Protocol | HTML | FlowOffload | Exception & Copy Packets |
| 31 | Exception & Copy Packet | HTML | FlowOffload | Exception & Copy Packets |
| 32 | Copy Packet Categories (Inbound Rate) | MDM | FlowOffload | Exception & Copy Packets |
| 33 | CopyPacket Categories (Outbound Rate) | MDM | FlowOffload | Exception & Copy Packets |
| 34 | Exception Packet Categories (Inbound Rate) | MDM | FlowOffload | Exception & Copy Packets |
| 35 | Exception Packet Categories (Outbound Rate) | MDM | FlowOffload | Exception & Copy Packets |
| 36 | OFFLOADED - GftExceptionUFPackets Protocol (Inbound Rate) | MDM | FlowOffload | Exception & Copy Packets |
| 37 | OFFLOADED - GftExceptionUFPackets Protocol (Outbound Rate) | MDM | FlowOffload | Exception & Copy Packets |
| 38 | BLOCKED - GftExceptionUFOffloadBlockedPackets Protocol (Inbound Rate) | MDM | FlowOffload | Exception & Copy Packets |
| 39 | BLOCKED - GftExceptionUFOffloadBlockedPackets Protocol (Outbound Rate) | MDM | FlowOffload | Exception & Copy Packets |
| 40 | FAILED - GftExceptionUFOffloadFailedPackets Protocol (Inbound Rate) | MDM | FlowOffload | Exception & Copy Packets |
| 41 | FAILED - GftExceptionUFOffloadFailedPackets Protocol (Outbound Rate) | MDM | FlowOffload | Exception & Copy Packets |
| 42 | Midstream Exception Packets (Inbound Rate) | MDM | FlowOffload | Exception & Copy Packets |
| 43 | Midstream Exception Packets (Outbound Rate) | MDM | FlowOffload | Exception & Copy Packets |
| 44 | GFT IN VPort Flow Offloads counters | MDM | GftPort + GftVfpPort | Flow Offload Counters (VPort Level) |
| 45 | GFT OUT VPort Flow Offload Counters | MDM | GftPort + GftVfpPort | Flow Offload Counters (VPort Level) |
| 46 | Flow Offloads Blocked | HTML | FlowOffload | Blocked Flow Offloads (VPort Level) |
| 47 | Flow Offload Blocked Breakdown (Inbound) | MDM | FlowOffload | Blocked Flow Offloads (VPort Level) |
| 48 | Flow Offload Blocked Breakdown (Outbound) | MDM | FlowOffload | Blocked Flow Offloads (VPort Level) |
| 49 | GFT IN VPort Blocked Flow Offload Counters | MDM | GftVfpPort | Blocked Flow Offloads (VPort Level) |
| 50 | GFT OUT VPort Blocked Flow Offload Counters | MDM | GftVfpPort | Blocked Flow Offloads (VPort Level) |
| 51 | GFT Packet Counters | MDM | GftVfpPort | Traffic & Byte Counters |
| 52 | GFT Byte Counters | MDM | GftVfpPort | Traffic & Byte Counters |
| 53 | GFT Container Offload Counters | MDM | GftVfpPort | Traffic & Byte Counters |
| 54 | GFT Rule Counter Allocated | MDM | GftVfpPort | Traffic & Byte Counters |
| 55 | Flow Offloads Retry | HTML | FlowOffload | Configuration |
| 56 | Flow Buffer Errors | HTML | FlowOffload | Configuration |
| 57 | Flow Buffer Error Metrics | MDM | FlowOffload | Configuration |
| 58 | Multitenancy Allowed VLANs Config | MDM | GftVfpPort | Configuration |
