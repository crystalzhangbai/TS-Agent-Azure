# ICMP / ICMPv6 Analysis Reference

ICMP and ICMPv6 messages embedded in packet captures can reveal critical reachability and path issues. When analyzing a capture, always check for abnormal ICMP/ICMPv6 messages alongside the main application traffic.

---

## IPv4 ICMP

In IPv4, ICMP messages often help diagnose unreachable-destination problems.

| Type | Code | Meaning | Troubleshooting Hint |
|------|------|---------|----------------------|
| 3 | 0 | Network Unreachable | The router closest to the destination has no route to the target network. Check routing tables along the path. |
| 3 | 1 | Host Unreachable | The destination network is reachable, but the specific host cannot be reached (e.g., host is down or ARP fails). |
| 3 | 4 | Fragmentation Needed (DF Set) | A router on the path has a smaller MTU than the packet size, but the Don't-Fragment bit is set. This indicates an MTU / Path MTU Discovery issue. |
| 11 | 0 | TTL Exceeded in Transit | The packet's TTL reached zero before arriving at the destination. Possible causes: (1) the sender's initial TTL is too low, or (2) a routing loop exists, or (3) this is normal traceroute probing behavior. |

### Key Points

- When you see **Type 3 Code 4**, look at the **Next-Hop MTU** field in the ICMP payload to determine the constrained link MTU.
- When you see **Type 11 Code 0**, check the source IP of the ICMP reply — it identifies the router where TTL expired. A burst of these from many different routers may indicate a routing loop; a single occurrence is often a traceroute probe.

---

## IPv6 ICMPv6

In IPv6, ICMPv6 plays a much larger role than ICMP does in IPv4 because several fundamental mechanisms depend on it.

### Neighbor Discovery Protocol (NDP)

ARP is replaced by NDP in IPv6, which uses ICMPv6 message types 135 (Neighbor Solicitation) and 136 (Neighbor Advertisement).

- If a host sends a **Neighbor Solicitation (NS)** but never receives a corresponding **Neighbor Advertisement (NA)**, the host cannot resolve the neighbor's link-layer address. This prevents proper Layer 2 encapsulation, and data packets destined for that neighbor will fail to be sent.
- **Azure VFP applies a rate limit on ICMPv6 traffic.** Under high volumes of NDP traffic, some NS/NA exchanges may be dropped, leading to intermittent reachability issues.

### Router Advertisement (RA)

ICMPv6 Router Advertisement (Type 134) messages influence how hosts learn their default route.

| RA Field | Impact |
|----------|--------|
| **Router Lifetime** | Determines how long the advertising router remains a valid default gateway. If the lifetime expires and no new RA is received, the host removes the default route and loses connectivity. |
| **Source IPv6 Address** | The source address of the RA becomes the next-hop address of the default route installed on the host. Verify this address is correct and reachable. |

### Key Points

- Missing or delayed RA messages can cause a host to lose its default route silently.
- Always verify that the RA source address matches the expected gateway address.
- If NDP resolution failures are observed, consider Azure VFP ICMPv6 rate limiting as a possible cause.
