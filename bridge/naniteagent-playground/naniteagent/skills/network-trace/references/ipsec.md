# ipsec.md — IPsec Traffic Analysis

## Purpose

Analyze IPsec traffic (UDP 500, UDP 4500, IP Protocol 50) to troubleshoot VPN connectivity, tunnel establishment, and encrypted data transfer issues.

## Key Protocols and Ports

| Protocol / Port | Usage |
|-----------------|-------|
| UDP 500 | IKE (ISAKMP) negotiation |
| UDP 4500 | NAT-Traversal (NAT-T) encapsulated IKE and ESP |
| IP Protocol 50 | ESP (Encapsulating Security Payload) data |

## Analysis Focus Areas

### 1. Distinguish ISAKMP and ESP Packets

For IPsec connectivity issues, identify and verify each phase of the negotiation:

| Phase | Description | Typical Mode |
|-------|-------------|--------------|
| IKE Phase 1 | Identity and key exchange | Main Mode (6 messages) |
| IKE Phase 2 | SA negotiation for data tunnel | Quick Mode (3 messages) |
| Data Transfer | Encrypted payload exchange | ESP |

**Wireshark display filters:**

```
# ISAKMP (IKE) negotiation packets
isakmp

# IKE Phase 1 — Main Mode
isakmp.exchangetype == 2

# IKE Phase 2 — Quick Mode
isakmp.exchangetype == 32

# ESP packets
esp
```

**Verification steps:**

1. Confirm IKE Phase 1 completes successfully (all 6 Main Mode messages exchanged).
2. Confirm IKE Phase 2 completes successfully (Quick Mode 3-way exchange).
3. Verify ESP data packets flow bidirectionally after negotiation.
4. If any phase stalls or shows retransmissions, identify which side stops responding and the last message exchanged.

### 2. NAT-Traversal (NAT-T) Detection

If NAT-T is present, the behavior of IPsec traffic changes:

- **Initial IKE negotiation** (Phase 1, first messages): UDP 500
- **After NAT detection**: Later Phase 1 messages and all subsequent traffic switch to **UDP 4500**
- **ESP data phase**: Encapsulated inside UDP 4500 (instead of raw IP Protocol 50)

**Wireshark display filters:**

```
# NAT-T encapsulated traffic
udp.port == 4500

# NAT-T keepalive (single-byte 0xff payload)
udp.port == 4500 && data.len == 1

# Check for NAT-D (NAT Discovery) payloads in IKE
isakmp.payloadtype == 20 || isakmp.payloadtype == 15
```

**What to look for:**

- Presence of NAT-D payloads in Phase 1 indicates NAT detection is being performed.
- If traffic transitions from UDP 500 to UDP 4500 mid-negotiation, NAT-T is active.
- Verify that both peers agree on NAT-T usage; mismatches cause tunnel failure.

### 3. IP MTU and Fragmentation After IPsec Encapsulation

IPsec encapsulation adds overhead (ESP header, IV, padding, authentication trailer), which can cause the encapsulated packet to exceed the path MTU.

**Common symptoms:**

- Small packets (e.g., ICMP ping) work, but large data transfers fail or stall.
- TCP connections establish but data transfer hangs.
- IP fragments observed after the IPsec endpoint.

**Wireshark display filters:**

```
# IP fragmentation
ip.flags.mf == 1 || ip.frag_offset > 0

# ICMP "Fragmentation Needed" (PMTUD)
icmp.type == 3 && icmp.code == 4

# DF bit set (Do Not Fragment)
ip.flags.df == 1
```

**Analysis steps:**

1. Check whether the DF (Don't Fragment) bit is set on inner packets.
2. Look for ICMP "Fragmentation Needed" messages — if they are blocked, PMTUD will fail.
3. Calculate the effective MTU: Original MTU minus IPsec overhead (typically 50–80 bytes depending on algorithm and mode).
4. If fragmentation is occurring, check whether fragments are being reassembled correctly at the receiving end.

### 4. Packet Loss and Reordering via SPI and Sequence Number

ESP packets contain an **SPI (Security Parameter Index)** and a **Sequence Number** that can be used to detect packet loss and reordering.

**Wireshark display filters:**

```
# Filter by specific SPI
esp.spi == 0xXXXXXXXX

# Show all ESP packets sorted by sequence number
esp
```

**Analysis steps:**

1. Filter ESP packets by SPI to isolate a single SA (Security Association) direction.
2. Examine the Sequence Number field for gaps — gaps indicate packet loss.
3. Check for out-of-order sequence numbers — this indicates reordering.
4. Compare packet counts in each direction (by SPI) to identify asymmetric loss.
5. Note: Each direction of an IPsec tunnel uses a different SPI. Identify both SPIs to analyze both directions.

## Troubleshooting Checklist

| Step | Check | Filter / Method |
|------|-------|-----------------|
| 1 | IKE Phase 1 initiator sends first packet | `isakmp.exchangetype == 2` |
| 2 | Phase 1 responder replies | Same filter, verify bidirectional |
| 3 | Phase 1 completes (6 messages for Main Mode) | Count ISAKMP messages |
| 4 | IKE Phase 2 starts | `isakmp.exchangetype == 32` |
| 5 | Phase 2 completes (3 messages for Quick Mode) | Count Quick Mode messages |
| 6 | ESP data flows | `esp` — verify both directions |
| 7 | NAT-T active? | Check for UDP 4500 transition |
| 8 | Fragmentation issues? | `ip.flags.mf == 1 \|\| ip.frag_offset > 0` |
| 9 | Packet loss? | Check ESP sequence number gaps |
| 10 | Reordering? | Check ESP sequence number order |
