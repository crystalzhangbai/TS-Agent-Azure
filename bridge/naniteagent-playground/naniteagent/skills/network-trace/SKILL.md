---
name: network-trace
version: 1.0.0
description: >-
  Network packet capture analysis and processing tool. Analyzes pcap, pcapng,
  tcpdump text, and CSV/tabular capture files. Provides capture summary,
  TCP session analysis, and capture file editing/transformation.
  Trigger: pcap, pcapng, packet capture, network trace, tcpdump, wireshark,
  capture file, network capture, packet analysis.
---

# Network Trace Analysis & Processing Skill

A tool for analyzing and processing network packet capture files.

## Trigger Conditions

This skill requires the following:

1. **User has provided a capture file or capture log**
2. Supported file formats:
   - **pcap / pcapng** — Standard formats that Wireshark can open
   - **txt** — Text output from tcpdump
   - **csv / tabular** — Exported tabular formats

## Workflow

```
┌──────────────────────────────────────┐
│  1. Clarify user intent               │
│     ├─ Analyze a capture file?        │
│     └─ Edit/modify a capture file?    │
├──────────────────────────────────────┤
│  2. Run trace-info.md — output summary │
│     (always execute first)            │
├──────────────────────────────────────┤
│  3. Select the appropriate reference  │
│     ├─ Analysis → tcp-connection.md   │
│     └─ Processing → trace-edit.md     │
└──────────────────────────────────────┘
```

### Step 1 — Clarify Intent

Ask the user what they need:
- **Analyze**: Understand capture contents, troubleshoot network issues, analyze TCP sessions
- **Process**: Extract, merge, deduplicate, format conversion, and other file operations

### Step 2 — Summary (Mandatory)

Regardless of the user's goal, **always** execute [trace-info.md](references/trace-info.md) first to output a summary of the capture file. This helps both the user and the Agent establish a baseline understanding of the capture contents.

### Step 3 — Deep Dive by Need

Based on the user's specific requirements, select and invoke the corresponding reference document:

| Scenario | Reference | Description |
|----------|-----------|-------------|
| Capture summary & basic info | [trace-info.md](references/trace-info.md) | Packet count, duration, protocol distribution, capture point identification |
| Edit or process capture files | [trace-edit.md](references/trace-edit.md) | Extract, merge, deduplicate, strip headers, format conversion |
| TCP session deep analysis | [tcp-connection.md](references/tcp-connection.md) | Connectivity, performance, retransmission, out-of-order analysis |
| IPsec / VPN traffic analysis | [ipsec.md](references/ipsec.md) | IKE negotiation, NAT-T detection, ESP analysis, MTU/fragmentation, SPI-based loss detection |
| ICMP / ICMPv6 analysis | [icmp.md](references/icmp.md) | Unreachable diagnostics, MTU/fragmentation, TTL exceeded, NDP issues, Router Advertisement |

### Protocol-Aware Reference Selection

After running **trace-info.md**, inspect the protocol distribution in the summary output. If specific protocols are detected, **automatically** invoke the corresponding reference for deeper analysis:

| Detected Protocol / Traffic | Reference to Invoke |
|-----------------------------|---------------------|
| TCP sessions | [tcp-connection.md](references/tcp-connection.md) |
| ISAKMP, ESP, UDP 500/4500 | [ipsec.md](references/ipsec.md) |
| ICMP unreachable, TTL exceeded, ICMPv6 NDP/RA | [icmp.md](references/icmp.md) |

This ensures that protocol-specific analysis is applied whenever the capture contains relevant traffic, without requiring the user to explicitly request it.

## Important Notes

- Multiple reference documents can be combined, e.g., trace-info → then tcp-connection → then ipsec
- Beyond analyzing application-layer traffic, always pay attention to **abnormal ICMP/ICMPv6 messages** in the capture (e.g., Destination Unreachable, TTL Exceeded, NDP failures). These often reveal root causes that are not visible at the transport or application layer.
- If file processing is needed during analysis (e.g., stripping encapsulation), invoke trace-edit.md at any time
- Always confirm key assumptions with the user (e.g., capture point location, custom port mappings)
