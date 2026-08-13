# edit.md — Capture File Editing & Processing

## Purpose

Edit, transform, and process capture files. Primarily uses the Wireshark command-line tool suite.

## Tools

For pcap/pcapng formats, prefer the following tools:

| Tool | Documentation | Use Case |
|------|---------------|----------|
| **tshark** | https://www.wireshark.org/docs/man-pages/tshark.html | Packet filtering, field extraction, format conversion |
| **editcap** | https://www.wireshark.org/docs/man-pages/editcap.html | Packet editing, deduplication, truncation, time adjustment |
| **mergecap** | https://www.wireshark.org/docs/man-pages/mergecap.html | Merging multiple capture files |

> 📖 For additional tools, see https://www.wireshark.org/docs/man-pages — browse as needed to find the right tool.

For txt or tabular formats, use scripts (Python, etc.) to achieve similar logic.

## Common Operations

### 1. Extract a Subset of Packets

Filter specific packets from the capture and write them to a new file.

**pcap/pcapng:**
```bash
# Use tshark -Y for filtering + -w to write output
tshark -r input.pcap -Y "ip.addr == 10.0.0.1 && tcp.port == 443" -w filtered.pcap

# Extract by time range
editcap -A "2024-01-01 10:00:00" -B "2024-01-01 10:05:00" input.pcap output.pcap

# Extract by packet number range (e.g., packets 100-200)
editcap -r input.pcap output.pcap 100-200
```

**txt/tabular:** Use scripts to filter rows by condition; the approach is similar.

### 2. Merge Capture Files

Merge multiple capture files into one, ordered by timestamp.

```bash
mergecap -w merged.pcap file1.pcap file2.pcap file3.pcap
```

### 3. Remove Duplicate Packets

```bash
# Use editcap -d to deduplicate
editcap -d input.pcap output.pcap
```

> ⚠️ For captures with ERSPAN/NVGRE/VXLAN encapsulation, deduplication based on outer headers will fail because each encapsulated copy has different outer addresses. Strip the encapsulation first, then deduplicate:

```bash
# Step 1: Strip the outer encapsulation headers (N = number of bytes to chop)
editcap -C <bytes_to_chop> input.pcap stripped.pcap

# Step 2: Deduplicate on the stripped (inner) packets
editcap -d stripped.pcap output.pcap
```

> Note: `-s` sets the snapshot length (truncates each packet to N bytes) and does **not** skip header bytes for comparison purposes. Use `-C` to chop/remove leading bytes from each packet.

### 4. Strip Headers

```bash
# Remove the first N bytes from each packet
editcap -C <bytes_to_chop> input.pcap output.pcap
```

Use case: Remove outer encapsulation headers (e.g., ERSPAN, VXLAN) to retain only the inner Overlay packets.

### 5. Convert pcap to CSV

Use tshark to convert pcap to CSV format with specified fields:

```bash
tshark -r test.pcap -T fields \
  -e frame.number \
  -e frame.time_epoch \
  -e frame.time_delta_displayed \
  -e ip.src \
  -e ip.dst \
  -e ip.id \
  -e _ws.col.Protocol \
  -e tcp.seq \
  -e tcp.ack \
  -e frame.len \
  -e tcp.srcport \
  -e tcp.dstport \
  -e udp.srcport \
  -e udp.dstport \
  -e tcp.analysis.ack_rtt \
  -e frame.protocols \
  -e _ws.col.Info \
  -e eth.src \
  -e eth.dst \
  -e ipv6.src \
  -e ipv6.dst \
  -e ip.proto \
  -e dns.id \
  -e ip.ttl \
  -e ip.flags \
  -e tcp.flags \
  -e tcp.window_size_value \
  -e esp.sequence \
  -e mysql.command \
  > test.csv
```

Fields can be added or removed based on user requirements.

### 6. Other Operations

If the user has needs not covered above:

1. First consult the tool list at https://www.wireshark.org/docs/man-pages
2. Determine whether an existing tool can meet the requirement
3. If no ready-made tool is available, consider using a combination of tshark + scripts
