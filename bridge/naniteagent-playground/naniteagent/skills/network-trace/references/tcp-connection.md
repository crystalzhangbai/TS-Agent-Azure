# tcp-connection.md — TCP Session Deep Analysis

## Purpose

Perform deep analysis on a specific TCP five-tuple session, focusing on different aspects depending on the problem scenario.

## Pre-Analysis — Session Completeness Check

Before analysis, **first** check the capture file's coverage completeness for the session.

Use the Wireshark `tcp.completeness` filter for quick assessment (bitmask, maximum 63):

| Bit | Value | Meaning |
|-----|-------|---------|
| 0 | 1 | SYN |
| 1 | 2 | SYN-ACK |
| 2 | 4 | ACK |
| 3 | 8 | DATA |
| 4 | 16 | FIN |
| 5 | 32 | RST |

```
# Show only complete sessions (SYN + SYN-ACK + ACK + DATA + FIN = 31)
tcp.completeness == 31

# Show sessions that ended with RST
tcp.completeness & 32
```

| Check Item | Description |
|-----------|-------------|
| Three-way handshake (SYN → SYN-ACK → ACK) | Whether fully captured |
| Session termination | Whether FIN four-way teardown or RST termination is present |
| Intermediate data | Whether there are missing/truncated packets |

> 📌 An incomplete session limits the depth of analysis. Inform the user that conclusions may not be comprehensive.

## Scenario 1 — Connectivity Issues (Unreachable)

### Analysis Focus

**First, determine the boundary**: Is it a TCP-layer issue or an upper-layer protocol issue?

```
Connectivity Issue Boundary Determination
├─ Was the three-way handshake successful?
│  ├─ SYN sent but no SYN-ACK     → TCP-layer unreachable (network/firewall/target not listening)
│  ├─ SYN-ACK received but no ACK → Client-side issue
│  └─ Handshake successful        → TCP is connected, problem is in upper-layer protocol
│
├─ Was an RST received?
│  ├─ RST immediately after SYN   → Port not listening or firewall rejection
│  └─ RST during data transfer    → Application-layer abnormal closure
│
└─ Was an ICMP Unreachable received?
   └─ Network-layer unreachable / administratively prohibited
```

### Checklist

- Was the SYN packet sent? Is the destination IP/Port correct?
- Was there a SYN-ACK response?
- Was there an RST or ICMP Unreachable?
- If the handshake succeeded, check whether the upper-layer protocol (TLS handshake, HTTP request, etc.) is normal

### RST Source Identification

When an RST is observed, determine **who sent it** — this is critical because middleboxes (firewalls, load balancers, DDoS appliances) often inject RSTs on behalf of the real endpoint.

**Method 1 — TTL analysis:**

Compare the TTL of the RST packet against normal packets from the same source IP:
- If TTL matches → likely sent by the actual endpoint
- If TTL differs significantly → likely injected by a middlebox at a different hop count

**Method 2 — IP Identification field:**

Compare the `ip.id` of the RST against the IP.ID sequence of normal packets from the same source:
- If IP.ID fits the monotonically increasing sequence → same host sent it
- If IP.ID is out of range (e.g., 0, or a completely different range) → injected by a different device

**Method 3 — Timing and TCP state:**

- RST with `seq=0` + ACK flag → often a response to an unexpected SYN (port not open, or middlebox rejection)
- RST immediately after SYN with no SYN-ACK ever seen → upstream device blocking the connection

### Azure DDoS SYN Authentication

Azure DDoS Protection uses SYN cookie-based authentication that creates specific patterns in captures:

**SYN Auth V1 (SYN cookie + RST):**
1. Client sends SYN
2. DDoS appliance responds with SYN-ACK containing a SYN cookie (encoded in the sequence number)
3. Client sends ACK (proving it is a real client)
4. DDoS appliance sends RST to the client
5. Client re-sends SYN (now whitelisted)
6. SYN reaches the real server

**Observable capture patterns:**
- SYN-ACK with **limited MSS values** (only 8 possible, encoded in 3 bits of the cookie)
- **No SACK option** in the SYN-ACK (SYN cookies reject TCP options)
- An RST appears between the initial handshake and the real connection — this is **expected behavior**, not an error
- The real connection follows with a second SYN

> ⚠️ Do NOT misinterpret the DDoS authentication RST as a connectivity failure. Look for the pattern: SYN → SYN-ACK → ACK → RST → SYN → (real handshake).

## Scenario 2 — Performance Issues (Slow TCP Transfer)

### Analysis Focus

1. **Calculate packet rate and locate the performance degradation point**
   - Compute bps/pps per time window
   - Identify time periods with significant rate drops

2. **Observe anomalies**

   | Symptom | Analysis Method |
   |---------|----------------|
   | Increased RTT | Calculate ACK-RTT and compare against baseline |
   | Packet loss | Check retransmission ratio |
   | Out-of-order | Check TCP seq and IP.ID ordering |
   | Window shrinkage | Check TCP Window Size trend (see Window Analysis below) |
   | Zero Window | Receiver buffer full (see Window Analysis below) |

3. **Packet length calculation — important caveat**

   > ⚠️ **Do NOT use the actual total length from the capture file (`frame.len`) to calculate transfer rates.**
   >
   > Reason: Packets may be truncated (snaplen) to control capture file size.
   >
   > **You must use the Total Length field from the IP header** (`ip.len`) to calculate the actual transmitted data volume.

### Window Analysis

Track TCP Window Size changes over the session lifetime to identify bottlenecks:

**Window shrinkage pattern:**
- Gradually decreasing receive window → receiver cannot process data fast enough (application bottleneck)
- Sudden window drop → receiver memory pressure or buffer exhaustion

**Zero Window:**
- Receiver advertises window = 0 → TCP receive buffer is full, sender must stop
- Sender starts a **persist timer** and periodically sends **window probes** (1-byte segments)
- Receiver sends a **window update** (usually in an ACK) when buffer space is available
- **Deadlock risk**: If the window update ACK is lost, both sides wait indefinitely — the persist timer/window probe mechanism prevents this

**Throughput estimation:**

```
Theoretical max throughput = Window Size / RTT
```

If observed throughput is far below `bandwidth`, check whether it is **window-limited** (Window/RTT < bandwidth) or **loss-limited** (retransmissions reducing effective throughput).

## Scenario 3 — TCP Packet Loss & Retransmission

### Analysis Steps

1. **Calculate packet loss rate**
   - Retransmitted packets / total packets
   - Track loss rate changes over time intervals

2. **Identify retransmission type**

   | Retransmission Type | Characteristics | Description |
   |--------------------|-----------------|-------------|
   | **RTO (Retransmission Timeout)** | Same seq retransmitted after timeout | Typically high RTT; greatest performance impact |
   | **Fast Retransmit** | Triggered after 3 Duplicate ACKs | Recovers faster than RTO |
   | **SACK Selective Retransmission** | Retransmits specific segments based on SACK option | Precisely retransmits only lost segments |
   | **TLP (Tail Loss Probe)** | Retransmits the last segment before RTO fires | Probes for loss at the tail of a transaction; see below |

3. **TLP + DSACK — Avoiding False Loss Diagnosis (Important)**

   TLP (Tail Loss Probe) sends a probe retransmission **before** the RTO timer expires to detect tail losses faster. If the original packet was NOT actually lost, the receiver will respond with a **DSACK** (Duplicate SACK, RFC 2883).

   **How to identify TLP + DSACK (not real loss):**
   - Sender retransmits a segment (TLP probe)
   - Receiver responds with a SACK where the **left edge of the first SACK block is below the ACK number** (`ACK >= SRE`) — this is a DSACK
   - DSACK tells the sender: "I already had this data — your retransmission was unnecessary"

   **Why this matters:**
   - Wireshark marks TLP probes as `[TCP Retransmission]` — this inflates the apparent retransmission/loss count
   - If followed by DSACK, it indicates **no actual packet loss occurred** — it was a speculative probe
   - Misinterpreting TLP + DSACK as real loss leads to incorrect diagnosis (e.g., blaming network for drops that didn't happen)

   **How to distinguish:**

   | Pattern | Meaning |
   |---------|---------|
   | Retransmission + DSACK (ACK ≥ SRE) | **Not real loss** — TLP probe, original arrived fine |
   | Retransmission + normal SACK (ACK < SLE < SRE) | **Real loss** — segment was actually missing |
   | Retransmission + no SACK at all | Ambiguous — may be RTO or SACK not negotiated |

4. **Loss direction**
   - Determine whether loss occurs in the send or receive direction
   - Combine with the capture point location to identify at which hop the loss occurs

## Scenario 4 — TCP Out-of-Order

### Analysis Method

> ⚠️ **Do NOT rely solely on TCP Sequence Number to determine out-of-order.**

You must combine the following information for a comprehensive judgment:

| Field | How to Judge |
|-------|-------------|
| **TCP Seq Number** | A later-arriving packet has a seq lower than the maximum seq already received |
| **IP.ID** | Whether IP.ID is monotonically increasing in the same direction. If IP.ID is also out-of-order, it indicates **network-layer reordering** (not TCP-layer retransmission) |
| **Timestamp** | Time gap between the out-of-order packet and its neighbors |

### Distinguishing Out-of-Order vs Retransmission

```
TCP Seq out-of-order + IP.ID out-of-order → Network-layer reordering (path change, multipath load balancing, etc.)
TCP Seq out-of-order + IP.ID in-order     → TCP-layer retransmission (resend after loss)
```

### Out-of-Order Impact Assessment

- Minor reordering (1-2 packets) is typically handled automatically by the receiver's TCP stack, with minimal impact
- Severe reordering may trigger Duplicate ACKs → unnecessary fast retransmissions → performance degradation
