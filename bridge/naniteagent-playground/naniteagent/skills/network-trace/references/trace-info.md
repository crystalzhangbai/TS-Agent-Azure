# info.md — Capture File Summary Analysis

## Purpose

Perform a basic analysis of the capture file and output summary information similar to Wireshark's `capinfos`, helping the user quickly understand the overall contents of the capture.

## Pre-Analysis — Encapsulation Detection (Important)

Before analysis, you **must** check whether the capture file contains common encapsulation layers:

### Azure-Specific Encapsulation

Captures from Azure TOR or MSEE typically contain multiple encapsulation layers:

```
[Ethernet] → [Outer IP] → [ERSPAN/NVGRE/VXLAN] → [Inner Ethernet] → [Inner IP (Overlay)] → [TCP/UDP/...]
```

- **Always analyze the innermost Overlay IP packets**, as the Overlay carries the actual business traffic and is meaningful for analysis
- Underlay encapsulation (ERSPAN, NVGRE, VXLAN) is only used for network forwarding and should not be treated as the analysis target

### Custom Port Identification (Important)

The following situations affect upper-layer protocol identification:

- **Azure Underlay VXLAN uses UDP 65330** (non-standard, instead of 4789) — this must be recognized
- Prompt the user about any other custom protocol-to-port mappings, for example:
  - 8080 → HTTP
  - 8443 → HTTPS
  - Other application-specific custom ports

> ⚠️ Failure to identify custom ports will lead to incorrect protocol classification, affecting all subsequent analysis results.

### Segment Offload Awareness (Important)

Modern NICs use offload features that affect how packets appear in captures:

| Feature | Direction | Effect on Capture |
|---------|-----------|-------------------|
| **LSO / TSO** (Large/TCP Segmentation Offload) | Send path | Capture shows jumbo segments (e.g., 64KB) **before** the NIC splits them into MTU-sized packets. These are NOT real wire-size packets. |
| **RSC / LRO** (Receive Segment Coalescing / Large Receive Offload) | Receive path | NIC or driver merges multiple received segments into one large segment **before** passing to the OS. Capture shows coalesced packets that never existed on the wire. |

> ⚠️ When offload is active:
> - **Packet counts are underestimated** (one captured segment = multiple wire packets)
> - **Packet sizes exceed MTU** — this is expected, not an error
> - **Timing analysis is distorted** — merged segments share a single timestamp
> - **Retransmission/out-of-order detection may be inaccurate** — Wireshark sees the coalesced view, not the wire view
>
> If precise per-packet analysis is needed, recommend the user disable offload features before recapturing:
> - Windows: `netsh int tcp set global rsc=disabled` / Disable in NIC advanced properties
> - Linux: `ethtool -K <iface> tso off gso off gro off lro off`

## Expected Output

Output the following summary information (including but not limited to):

### Basic Information

| Item | Description |
|------|-------------|
| Packet count | Total number of packets in the capture file |
| File size | Size of the capture file on disk |
| Duration | Time span from the first packet to the last packet |
| Start time | Timestamp of the first packet |
| End time | Timestamp of the last packet |

### Traffic Statistics

| Item | Description |
|------|-------------|
| Overall rate (bps) | Total bit rate |
| Overall rate (pps) | Total packet rate |

### Protocol Distribution

| Item | Description |
|------|-------------|
| IP version | IPv4 / IPv6 distribution |
| Upper-layer protocols | Count distribution of TCP, UDP, ESP, or other protocols |
| Session count | Number of five-tuple sessions for common protocols (TCP, UDP) |

### Capture Point Identification

Attempt to infer the capture location: **Client** / **Server** / **Intermediate device**

Criteria:

1. **Source/Destination MAC addresses**
   - Whether they match known device MACs (gateway, switch, etc.)
   - Whether all MAC addresses are identical (indicates a mirrored/SPAN capture from an intermediate device)

2. **TTL analysis**
   - Whether TTL values are close to common initial values (64/128/255)
   - TTL consistency in a single direction

3. **Traffic direction pattern**
   - Request/response ratio and direction

> 📌 If the capture point cannot be determined automatically, you **must ask the user** to confirm the capture location. Identifying the capture point is critical for all subsequent analysis.
