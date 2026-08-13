# PCIe Failure Investigation Queries — Sparkle SEL, AzureDCM, HPC

Use these queries when the RCA identifies `pCIuncorrectable`, `PCIe Errors`,
`Surprise Down Error`, `Completion Timeout`, or any PCIe-related hardware fault.
The goal is to identify **which specific PCIe device** failed and classify the
failure pattern (GPU CTO, CX7 Surprise Link Down, Root Port CTO, etc.).

---

## H100 PCIe Topology (Quanta C2789)

Understanding the physical signal path is essential for tracing which component
failed. Each GPU has a dedicated PCIe chain from CPU through retimers, cables,
and switches:

```
[ CPU0 Sapphire Rapids ]
 └─ PE2 Root Port (lane 15:0, PCIe Gen5 x16)
      └─ Retimer #1 (Gen5 x16)       ← Host Processor Module side
           └─ Examax 6x14 Cable #4   ← 84-pin MCIO/Examax connector
                └─ CX7 #8 Switch (Upstream Port, PCIe Gen5 x16)
                     │
                     ├─ PCIe Gen5 x16 → Examax J3 Connector (to H100 Baseboard / HIB)
                     │    └─ Retimer #2 (Gen5 x16)   ← GPU baseboard side
                     │         └─ PCIe Gen4 x2 (control path)
                     │              └─ PCIe Switch (Mgmt)
                     │                   └─ NVLink Switch / NVSwitch
                     │
                     └─ CX7 Downstream Port → GPU endpoint
```

### Key topology facts

- **Two retimers** per GPU path: Retimer #1 is on the CPU/host side, Retimer #2
  is on the GPU baseboard side
- **Examax cables** (6×14, 84-pin) connect the Host Processor Module to the H100
  baseboard — physical cable faults can cause SLD
- **CX7 (ConnectX-7)** acts as a PCIe switch/fabric between the CPU Root Port and
  both the GPU endpoint and the NVLink Switch management path
- The NVLink Switch uses a **PCIe Gen4 x2/x4** sideband for management, firmware
  load, and reset — distinct from the high-speed NVLink data path
- Each Examax connector slot on the HIB (Host Interface Board) maps to a specific
  GPU and CX7 switch pair

### Topology segments where errors occur

| Segment | Typical Error | What It Means |
|---------|--------------|---------------|
| CPU Root Port → Retimer #1 | RP CTO | Root port lost communication downstream |
| Retimer #1 → Examax Cable | SLD | Physical cable or connector issue |
| Examax → CX7 Upstream Port | SLD | Cable or CX7 switch input failure |
| CX7 Downstream → GPU | CX7 SLD / GPU CTO | CX7 switch lost link to GPU |
| CX7 → Examax J3 → Retimer #2 → NVLink Switch | Control path fault | NVSwitch management path failure |

---

## Step 1 — Raw SEL Events around Issue Time

Cluster: `sparkle.eastus`  
Database: `defaultdb`

Pull all BMC System Event Log entries for the node in a window around the fault
time. These are the raw records that feed all downstream analysis.

```kusto
let _startTime = datetime({StartTime});
let _endTime   = datetime({EndTime});
cluster('sparkle.eastus').database("defaultdb").SparkleSEL
| where BMCSelTimestamp between (_startTime .. _endTime)
| where NodeId == "{NodeId}"
| project Cluster, NodeId, RecordId, BMCSelTimestamp, RawHex, EventDetail
| order by BMCSelTimestamp asc
```

Key columns:
- `RawHex` — 16-byte hex SEL record; bytes encode sensor type, error type, bus number
- `EventDetail` — JSON-decoded human-readable error description
- `RecordId` — monotonic within a BMC power cycle; gaps indicate BMC log wrap

---

## Step 2 — PCIe Failure Pattern Classification (GPU CTO / CX7 SLD / RP CTO)

Cluster: `sparkle.eastus`  
Database: `defaultdb`

This query classifies PCIe SEL events into three known failure buckets by matching
regex patterns on the `RawHex` field. Each bucket requires **two** matching records
(A = error source, B = error type) within the same 5-second window.

```kusto
let _startTime = datetime({StartTime});
let _endTime   = datetime({EndTime});
let BinWin = 5s;
cluster('sparkle.eastus').database("defaultdb").SparkleSEL
| where BMCSelTimestamp between (_startTime .. _endTime)
| where NodeId == "{NodeId}"
| project Cluster, NodeId, RecordId, BMCSelTimestamp, RawHex, EventDetail
// ── Pattern flags ──
| extend
    GPU_CTO_A     = iif(RawHex matches regex @".. .. 02 .. .. .. .. .. .. .. .. a1 6f a8 .. (0a|11|18|69|9d|ad|bd|dd)", 1, 0),
    GPU_CTO_B     = iif(RawHex matches regex @".. .. c0 .. .. .. .. .. .. .. .. .. .. .. 84 ..", 1, 0),
    CX7_SLD_A     = iif(RawHex matches regex @".. .. 02 .. .. .. .. .. .. .. .. a1 6f aa 00 (09|10|17|68|9c|ac|bc|dc)", 1, 0),
    CX7_SLD_B     = iif(RawHex matches regex @".. .. c0 .. .. .. .. .. .. .. .. .. .. .. 93 ..", 1, 0),
    RP_CTO_new_A  = iif(RawHex matches regex @".. .. 02 .. .. .. .. .. .. .. .. a1 6f a8 08 (04|0b|12|63|97|a7|b7|d7)", 1, 0),
    RP_CTO_new_B  = iif(RawHex matches regex @".. .. c0 .. .. .. .. .. .. .. .. .. .. .. 84 ..", 1, 0)
| summarize
    GPU_CTO_HasA      = max(GPU_CTO_A),
    GPU_CTO_HasB      = max(GPU_CTO_B),
    CX7_SLD_HasA      = max(CX7_SLD_A),
    CX7_SLD_HasB      = max(CX7_SLD_B),
    RP_CTO_new_HasA   = max(RP_CTO_new_A),
    RP_CTO_new_HasB   = max(RP_CTO_new_B),
    GPU_CTO_A_RawHex  = make_set_if(RawHex, GPU_CTO_A  == 1, 10),
    GPU_CTO_B_RawHex  = make_set_if(RawHex, GPU_CTO_B  == 1, 10),
    CX7_SLD_A_RawHex  = make_set_if(RawHex, CX7_SLD_A  == 1, 10),
    CX7_SLD_B_RawHex  = make_set_if(RawHex, CX7_SLD_B  == 1, 10),
    RP_CTO_new_A_RawHex = make_set_if(RawHex, RP_CTO_new_A == 1, 10),
    RP_CTO_new_B_RawHex = make_set_if(RawHex, RP_CTO_new_B == 1, 10)
    by Cluster, NodeId, bin(BMCSelTimestamp, BinWin)
// ── Bucketize ──
| extend BucketizedIssue = case(
    GPU_CTO_HasA == 1 and GPU_CTO_HasB == 1, "GPU_Completion Timeout: BIOS Check for GPU CTO Value",
    CX7_SLD_HasA == 1 and CX7_SLD_HasB == 1, "Legacy SLD between CX7 and GPU",
    RP_CTO_new_HasA == 1 and RP_CTO_new_HasB == 1 and CX7_SLD_HasA == 0, "CTO on RP after CX7 FW Update",
    "No Match"
    )
| where BucketizedIssue != "" and BucketizedIssue != "No Match"
// ── Extract failed bus number from the "A" record ──
| extend FailedPort = case(
    BucketizedIssue == "GPU_Completion Timeout: BIOS Check for GPU CTO Value", GPU_CTO_A_RawHex,
    BucketizedIssue == "Legacy SLD between CX7 and GPU", CX7_SLD_A_RawHex,
    BucketizedIssue == "CTO on RP after CX7 FW Update", RP_CTO_new_A_RawHex,
    "No Match"
    )
| extend firstVal = tostring(parse_json(FailedPort)[0])
| extend tokens  = extract_all(@"([0-9A-Fa-f]{2})", firstVal)
| extend b15     = tostring(tokens[14]),
         b16     = tostring(tokens[15])
| extend BusNumFailed = toint(strcat("0x", b16))
| project Cluster, NodeId, BMCSelTimestamp, BucketizedIssue, FailedPort, BusNumFailed
```

### Interpretation — RawHex byte positions

| Byte(s) | Meaning |
|---------|---------|
| Byte 3 (`02`) | OEM sensor: PCIe AER record (Advanced Error Reporting) |
| Byte 3 (`c0`) | AER Status record with decoded error description |
| Byte 3 (`c7`) | Slot/Port assignment record (root port ↔ slot mapping) |
| Bytes 12–13 (`a1 6f`) | OEM PCIe AER event signature |
| Byte 14 | Error severity: `a7` = Correctable, `a8` = Uncorrectable Non-Fatal, `aa` = Fatal |
| Byte 15 | **Device:Function** — split the hex byte into two nibbles (high, low). Take all 4 bits of the high nibble + the MSB (first bit) of the low nibble → 5-bit Device ID. Take the remaining 3 bits of the low nibble → 3-bit Function ID. Example: `10` → high=`1`=`0001`, low=`0`=`0000` → Device=`00010`=2, Function=`000`=0 → `2.0`. Example: `00` → high=`0`=`0000`, low=`0`=`0000` → Device=`00000`=0, Function=`000`=0 → `0.0`. Example: `08` → high=`0`=`0000`, low=`8`=`1000` → Device=`00001`=1, Function=`000`=0 → `1.0` |
| Byte 16 | **PCIe Bus Number** of the device that reported the error |
| Byte 15 in `c0` records | AER status code: `84` = Completion Timeout, `93` = Surprise Down Error, `70` = Receiver Error |

### Failure bucket descriptions

| Bucket | Pattern A (source) | Pattern B (type) | Meaning |
|--------|-------------------|-------------------|---------|
| **GPU_Completion Timeout** | `a8` (Uncorr) on Nvidia GPU bus | `84` (CTO) | GPU stopped responding to PCIe transactions |
| **Legacy SLD between CX7 and GPU** | `aa` (Fatal) on CX7 switch downstream port | `93` (Surprise Down) | CX7 NIC PCIe switch lost link to downstream GPU |
| **CTO on RP after CX7 FW Update** | `a8` (Uncorr) on CPU Root Port | `84` (CTO) | Root Port CTO after CX7 firmware update; CX7 SLD absent |

### Three known PCIe issues (H100 / H200 SKUs)

These are the three categorized PCIe issues that correlate with Bugcheck 0x124 on
H100/H200 DC nodes:

**Issue 1 — Legacy PCIe SLD (Surprise Link Down) between CX7 Downstream Port and GPU**
- CX7 switch downstream port loses link to the GPU endpoint
- RP sees "ERR_FATAL/NON_FATAL received, Root Port Error" as a consequence
- No CX7 FW fix identified; CX7 FW updates that attempt to fix this may trigger Issue 3
- Work item: `https://azurecsi.visualstudio.com/C2789/_workitems/edit/1602652`
- Bucket match: `CX7_SLD_HasA == 1 && CX7_SLD_HasB == 1`

**Issue 2 — Completion Timeout (CTO) flagged by GPU**
- GPU-side Completion Timeout Value not programmed correctly by BIOS
- BIOS should set GPU DCTL2.CTV (bit 3:0) to `0x6` (210 ms)
- Fix: BIOS version `1C21.GN` or later
- Bucket match: `GPU_CTO_HasA == 1 && GPU_CTO_HasB == 1`

**Issue 3 — RP Completion Timeout after CX7 FW update (no SLD indication)**
- Root Port flags Completion Timeout but no Surprise Link Down is observed
- Occurs after CX7 FW updates that fix Issue 1: `28.44.1206`, `28.44.1210`,
  `28.40.1704`, `28.42.1404`
- Root cause not yet fully identified
- Bucket match: `RP_CTO_new_HasA == 1 && RP_CTO_new_HasB == 1 && CX7_SLD_HasA == 0`

### How CTO and SLD differ in SEL records

| # | Completion Timeout (CTO) | Surprise Link Down (SLD) |
|---|--------------------------|--------------------------|
| 1 | Requester (RP/EP) sends TLP, no completion returned | Link partner disappears without orderly link-down |
| 2 | TLP lost in path (retimer, switch, cable) | Link state transitions to Detect |
| 3 | SEL: CTO bit = 1 (`84` in AER status) | SEL: Surprise Down bit = 1 (`93` in AER status) |
| 4 | AER: link may still be up | AER: link is down |

### Example output interpretation

**Issue 1 (SLD) — CX7 downstream port:**
- RawHex A: `70 04 02 75 d6 21 69 01 00 04 13 a1 6f aa 00 09`
  - Byte 14 = `aa` (Fatal), Byte 15 = `00` (Dev 0, Fn 0), Byte 16 = `09` → **Bus 9**
  - EventDetail: `"Bus Fatal Error"`, Device 0, Function 0, Bus Number 9
- RawHex B: `71 04 c0 75 d6 21 69 37 01 00 63 15 79 19 93 73`
  - Byte 14 = `93` (Surprise Down Error)
  - EventDetail: `"Surprise Down Error Status, Uncorrected Error"`
- Result: **CX7_6 Switch Downstream Port** at BDF `09:00.0`

**Issue 2 (GPU CTO) — Nvidia GPU:**
- RawHex A: `f8 07 02 ee fb 24 69 01 00 04 13 a1 6f a8 00 18`
  - Byte 14 = `a8` (Uncorrectable), Byte 16 = `18` → **Bus 24 (0x18)**
  - EventDetail: `"Bus Uncorrectable Non-Fatal Error"`, Bus Number 24
- RawHex B: `f9 07 c0 ee fb 24 69 37 01 00 de 10 30 23 84 70`
  - Byte 14 = `84` (Completion Timeout)
- Result: **Nvidia Delta Next 3D Controller (GPU)** at BDF `18:00.0`

**Issue 3 (RP CTO after CX7 FW update):**
- RawHex A: `26 05 02 8e 4c 35 69 01 00 04 13 a1 6f a8 08 0b`
  - Byte 14 = `a8` (Uncorrectable), Byte 15 = `08` (Dev 1, Fn 0), Byte 16 = `0b` → **Bus 11 (0x0b)**
- No CX7 SLD records present → CX7_SLD_HasA == 0
- Result: **CPU Root Port** CTO, bus 11 — CX7 FW `28.40.1704`

> **Note:** The regex bus-byte alternations (`0a|11|18|...`) are SKU-specific. If the
> query returns 0 rows but raw SEL shows PCIe errors, the bus numbering may differ
> for the node's SKU. Use Step 3 to identify the failing bus manually.

---

## Step 3 — PCIe-Related SEL Events by Keyword

Cluster: `sparkle.eastus`  
Database: `defaultdb`

Fallback search when the regex-based classification (Step 2) returns no results.
Filters raw SEL by EventDetail keywords.

```kusto
let _startTime = datetime({StartTime});
let _endTime   = datetime({EndTime});
cluster('sparkle.eastus').database("defaultdb").SparkleSEL
| where BMCSelTimestamp between (_startTime .. _endTime)
| where NodeId == "{NodeId}"
| where EventDetail has_any ("PCIe", "PCI", "Uncorrectable", "Fatal", "AER", "Bus", "error", "Surprise", "Completion")
| project Cluster, NodeId, RecordId, BMCSelTimestamp, RawHex, EventDetail
| order by BMCSelTimestamp asc
```

Key `EventDetail` signatures to look for:
- `"Surprise Down Error Status (Optional), Uncorrected Error"` — Surprise Link Down (fatal)
- `"Receiver Error Status, Correctable Error"` — link instability (often precedes SLD)
- `"ERR_FATAL/NON_FATAL received, Root Port Error"` — root port received fatal error from downstream
- `"unspecified value: 253"` — cascading uncorrectable errors (common after SLD)
- `"FPGA State": "FPGA Not Ready"` — FPGA lost communication (collateral damage)

---

## Step 4 — Partner_RAS_PCIe_TelemetryOutput (Pre-Analyzed PCIe RCA)

Cluster: `sparkle.eastus`  
Database: `defaultdb`

This table contains **pre-analyzed PCIe failure records** produced by the Sparkle
RAS pipeline. It identifies the exact failing BDF (Bus:Device.Function), vendor/device
IDs, and PCIe location class. **Check this table first** — it often gives the answer
directly without manual SEL parsing.

```kusto
cluster('sparkle.eastus').database("defaultdb").Partner_RAS_PCIe_TelemetryOutput
| where NodeId == "{NodeId}"
| where Date >= datetime({StartDate}) and Date <= datetime({EndDate})
| project NodeId, Date, StartTime, RCALevel2, Csi_HwBucket,
          BusDevFn, SelError, DeviceID, VendorID, PCIe_Location, PCIe_Class,
          Gen, HwSkuId, Cluster, ClusterType, Manufacturer, ProductName,
          BIOSVersion, BmcVersion, CPUVendor, EndpointData
```

Key columns:
- `BusDevFn` — Bus:Device.Function of the failing component (e.g., `25:2.0`)
- `SelError` — decoded error type (e.g., `Surprise Down Error Status`)
- `VendorID` / `DeviceID` — PCI vendor/device IDs (`8086` = Intel, `15b3` = Mellanox/Nvidia)
- `PCIe_Location` — `RootPort`, `Endpoint`, `Switch`, `SwitchDownstreamPort`
- `Csi_HwBucket` — hardware team escalation bucket (e.g., `Motherboard`, `GPU`, `NIC`)
- `RCALevel2` — high-level RCA category (e.g., `Hardware Failure - PCIe Errors`)
- `EndpointData` — JSON with downstream device details (populated for switch/RP errors)

### Common VendorID / DeviceID mappings

| VendorID | Vendor | Common DeviceIDs |
|----------|--------|-----------------|
| `8086` | Intel | `347d` = Sapphire Rapids PCIe Root Port |
| `10de` | Nvidia | `2330`/`2331` = H100 GPU, `2324` = A100 GPU |
| `15b3` | Mellanox/Nvidia | `a2dc` = ConnectX-7 NIC, `101e` = ConnectX-6 Dx |

---

## Step 5 — PCIe Bus-to-Device Topology Mapping

Cluster: `sparkle.eastus`  
Database: `defaultdb`

Maps PCIe bus numbers to physical slot locations and device labels using the
SKU-specific topology table. Use the `HwSkuId` obtained from Step 4 or from
`AzureDCMDb.ResourceSnapshotV1`.

```kusto
cluster('sparkle.eastus').database("defaultdb").Partner_Topology
| where HwSkuId == "{HwSkuId}"
| top 100 by DataCollectedOn desc
| project PCIeSlot, BusNumber, DeviceNumber, FunctionNumber, LocationLabel, Generation
| distinct PCIeSlot, BusNumber, DeviceNumber, FunctionNumber, LocationLabel
| order by toint(BusNumber) asc
```

Also available as `Partner_Topology_v1` with additional `PMCSlotNumber` column:

```kusto
cluster('sparkle.eastus').database("defaultdb").Partner_Topology_v1
| where HwSkuId == "{HwSkuId}"
| top 100 by DataCollectedOn desc
| project PCIeSlot, BusNumber, DeviceNumber, FunctionNumber, LocationLabel, Generation, PMCSlotNumber
| distinct PCIeSlot, BusNumber, DeviceNumber, FunctionNumber, LocationLabel, PMCSlotNumber
| order by toint(BusNumber) asc
```

Interpretation:
- Cross-reference `BusNumFailed` from Step 2 with `BusNumber` here to find the `LocationLabel`
- `LocationLabel` identifies the physical device (e.g., GPU, NIC, NVMe SSD, M.2 connector)
- `PCIeSlot` / `PMCSlotNumber` — physical slot on the baseboard

> **Note:** These tables are keyed by `HwSkuId`, not `NodeId`. All nodes with the
> same SKU share the same bus topology.

---

## Step 6 — HPC Interconnect HCA Telemetry

Cluster: `hpcfuntelemetry.eastus`  
Database: `HPCInterconnectInventory`

For GPU/HPC nodes, retrieves ConnectX NIC adapter details including firmware and
driver versions. Useful when the PCIe failure involves a CX7/CX6 NIC.

```kusto
cluster('hpcfuntelemetry.eastus').database("HPCInterconnectInventory").HCATelemetry
| where NodeId == "{NodeId}"
| top 1 by ingestion_time()
| project Cluster, NodeId, PreciseTimeStamp, Adapter, DriverVersion, FirmwareVersion
```

Key columns:
- `Adapter` — NIC name (e.g., `ConnectX-7 #4`)
- `FirmwareVersion` — CX7 FW version (relevant for "CTO on RP after CX7 FW Update" bucket)
- `DriverVersion` — Mellanox driver version

---

## Step 7 — Node SKU & Hardware Info

Cluster: `Azuredcm`  
Database: `AzureDCMDb`

Get the SKU, model, and manufacturer for a node. The `Sku` value is used as input
to the topology query in Step 5.

```kusto
cluster("Azuredcm").database("AzureDCMDb").ResourceSnapshotV1
| where ResourceId == "{NodeId}"
| project ResourceId, Tenant, Sku, Model, Manufacturer, HostName, IPAddress
```

---

## Manual Triage — When No Known Issue Matches

When the Step 2 classification query returns "No Match" or 0 rows but raw SEL
(Step 1) shows PCIe errors, use this manual approach from the raw SEL data:

### 1. Run the raw SEL query (Step 1)

### 2. Identify the two paired records for each error event

Each PCIe error produces **two SEL records** within the same second:
- **Record A** (byte 3 = `02`): OEM AER record — contains Bus:Device.Function
  and error severity
- **Record B** (byte 3 = `c0`): AER Status record — contains the specific error
  code (CTO, SLD, Receiver Error, etc.)

### 3. Parse the A record to find Bus:Device.Function

From the RawHex of the `02` record:
- **Byte 14**: Error severity
  - `a7` = Correctable
  - `a8` = Uncorrectable Non-Fatal
  - `aa` = Fatal
- **Byte 15**: Encodes **Device and Function** number. Decoding rule:
  1. Split the hex byte into two nibbles: high nibble (bits 7–4) and low nibble (bits 3–0)
  2. **Device ID** (5 bits) = all 4 bits of high nibble + MSB (bit 3) of low nibble
  3. **Function ID** (3 bits) = remaining 3 bits (bits 2–0) of low nibble
  4. Examples:
     - `00` → `0000` + `0000` → Device = `00000` = 0, Function = `000` = 0 → **0.0**
     - `08` → `0000` + `1000` → Device = `00001` = 1, Function = `000` = 0 → **1.0**
     - `10` → `0001` + `0000` → Device = `00010` = 2, Function = `000` = 0 → **2.0**
     - `19` → `0001` + `1001` → Device = `00011` = 3, Function = `001` = 1 → **3.1**
- **Byte 16**: **PCIe Bus Number** (hex) — convert to decimal for topology lookup

### 4. Parse the B record to determine error type

From the RawHex of the `c0` record:
- **Byte 14** (AER status code):
  - `84` = Completion Timeout
  - `93` = Surprise Down Error
  - `70` = Receiver Error (correctable, often precedes fatal)
  - `9d` = ERR_FATAL/NON_FATAL received (Root Port error)

### 5. Cross-reference with topology

Use the Bus Number from step 3 to look up the device in Step 5 (Partner_Topology)
or Step 4 (Partner_RAS_PCIe_TelemetryOutput).

### Example — CPU Root Port Surprise Link Down (from IAD03PrdGPC06)

```
Record A: ea 04 02 18 b1 34 69 01 00 04 13 a1 6f aa 10 19
  → Byte 3 = 02 (AER record)
  → Byte 14 = aa (Fatal)
  → Byte 15 = 10 → Device 2, Function 0 (also in EventDetail JSON)
  → Byte 16 = 19 → Bus 25 (0x19)
  → EventDetail: {"Bus Fatal Error"}, Device 2, Function 0, Bus 25

Record B: eb 04 c0 18 b1 34 69 37 01 00 86 80 7d 34 93 9d
  → Byte 3 = c0 (AER Status)
  → Byte 14 = 93 (Surprise Down Error)
  → Bytes 12-13 = 7d 34 → DeviceID 0x347d (Intel Sapphire Rapids Root Port)
  → EventDetail: {"Surprise Down Error Status, Uncorrected Error"},
    {"ERR_FATAL/NON_FATAL received, Root Port Error"}

Conclusion: CPU Root Port (Bus 25, Device 2, Function 0) reported SLD — the
downstream CX7 switch on Slot 16 lost link.
```

### DeviceID reference for `c0` records (bytes 12–13, little-endian)

The `c0` AER status record encodes the PCI DeviceID in bytes 12–13 (little-endian).
This helps identify the reporting device without a topology lookup:

| Bytes 12–13 | DeviceID | Device |
|-------------|----------|--------|
| `7d 34` | `0x347d` | Intel Sapphire Rapids PCIe Root Port |
| `30 23` / `31 23` | `0x2330` / `0x2331` | Nvidia H100 GPU |
| `dc a2` | `0xa2dc` | Mellanox ConnectX-7 NIC |
| `24 23` | `0x2324` | Nvidia A100 GPU |
| `1e 10` | `0x101e` | Mellanox ConnectX-6 Dx |

---

## Related ICMs (reference)

| ICM | Description |
|-----|-------------|
| Incident-558515455 | BugCheckCode 0x00000124, PCIe fatal, ByteDance VM redeployed |
| Incident-573912146 | HardwareFault.pCIfatal, GPU VM unexpected reboot (LVL09PrdGPC06 & AVC01PrdGPC02) |
| Incident-601774144 | Multiple Nodes Fault Received PCIe Error |
| Incident-606473035 | VM Start Timed Out due to faulted node, RCALevel2 "Hardware Failure - PCIe Errors" |
| Incident-707055362 | GPU VM PCI Error on LVL09PrdGPC06 |

---

## Investigation Workflow Summary

```
1. Start with Step 4 (Partner_RAS_PCIe_TelemetryOutput)
   → Often gives BusDevFn, VendorID, DeviceID, SelError directly
   → If data exists, you likely have enough to identify the failed device

2. If Step 4 has no data or needs more detail:
   → Run Step 1 (raw SEL) to see all events
   → Run Step 2 (pattern classification) to bucket the failure
   → Run Step 3 (keyword search) as fallback if Step 2 returns 0 rows

3. If Step 2 returns "No Match" but SEL has PCIe errors:
   → Use "Manual Triage" section to parse RawHex bytes manually
   → Find the paired A (02) + B (c0) records within the same second
   → Extract Bus:Device.Function from the A record (bytes 14-16)
   → Identify error type from the B record (byte 14: 84=CTO, 93=SLD)
   → Read DeviceID from bytes 12-13 of the c0 record (little-endian)

4. To map bus number to physical device:
   → Get HwSkuId from Step 4 or Step 7
   → Run Step 5 (topology) to find LocationLabel for the failed bus
   → Refer to the H100 PCIe Topology section for signal path context

5. For CX7 NIC failures:
   → Run Step 6 (HCA telemetry) to get firmware/driver versions
   → Check CX7 FW against known-issue versions:
     28.44.1206 / 28.44.1210 (cluster-level updates)
     28.40.1704 / 28.42.1404 (fail-and-fix decoupled IB FW)

6. Classify into known issues:
   → Issue 1 (Legacy SLD): CX7 SLD + no CX7 FW fix → cable/connector/CX7 HW
   → Issue 2 (GPU CTO): GPU CTO value → check BIOS version ≥ 1C21.GN
   → Issue 3 (RP CTO post-FW): RP CTO + no SLD + updated CX7 FW → escalate
```

---

## Appendix A — C2789 7U Server PCIe Logical-to-Physical Mapping (Table 11)

> Source: ByteDance PCIfatal Error wiki (H100 & H200). Use this table to translate a
> `Bus:Device.Function` (decoded from a Sparkle SEL RawHex) into a physical device,
> CPU port, and cable on the C2789 (Quanta) 7U server.

### CPU0 Domain — root / PCH / DMI

| # | Bus:Dev.Fn | Description | Vendor:Device ID | CPU Port | Width | Speed | Physical Slot | Cable |
|---|---|---|---|---|---|---|---|---|
| 1 | 00:0d.0 | PCH PE3[10] | 8086:1bbd | CPU0 DMI port | x1 | 5.0 GT/s | | |
| 2 | 01:00.0 | AST1150 PCIe-PCIe Bridge | 1a03:1150 | | x1 | 5.0 GT/s | | |
| 3 | 02:00.0 | ASPEED Graphics | 1a03:2000 | | - | - | | |
| 4 | 00:10.0 | PCH PE3[3:0] | 8086:1bb0 | CPU0 DMI port | x4 | 8.0 GT/s | | |
| 5 | 03:00.0 | Samsung NVMe SSD Controller | 144d:a80a | | x4 | 8.0 GT/s | HPM M.2 Slot#1 (Boot) - Bottom | |

### CPU0 Port 0 [15:0] — Examax #3 (GPU #0/nvidia-smi → GPU #3/physical)

| # | Bus:Dev.Fn | Description | Vendor:Device ID | CPU Port | Width | Speed | Physical Slot | Cable |
|---|---|---|---|---|---|---|---|---|
| 6 | 04:01.0 | CPU0 Root Port | 8086:352A | CPU0 Port 0 [15:0] | x16 | 32.0 GT/s | | Examax #3 |
| 7 | 05:00.0 | CX7_6 Switch Upstream Port | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #3 |
| 8 | 06:00.0 | CX7_6 Switch Downstream Port#1 | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #3 |
| 9 | 07:00.0 | CX7 #6 IB MT28861 PCIe Endpoint | 15b3:1021 | | x16 | 32.0 GT/s | CX7 #6 (mt4129_pciconf0) | Examax #3 |
| 10 | 06:02.0 | CX7_6 Switch Downstream Port#2 | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #3 |
| 11 | 08:00.0 | CX7_6 Switch Upstream Port | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #3 |
| 12 | 09:00.0 | CX7_6 Switch Downstream Port | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #3 |
| 13 | 0a:00.0 | Nvidia Delta Next 3D Controller | 10de:2330 | | x16 | 32.0 GT/s | GPU #0 (nvidia-smi) / GPU #3 (physical) | Examax #3 |

### CPU0 Port 1 [15:0] — Examax #4 (GPU #1/nvidia-smi → GPU #2/physical)

| # | Bus:Dev.Fn | Description | Vendor:Device ID | CPU Port | Width | Speed | Physical Slot | Cable |
|---|---|---|---|---|---|---|---|---|
| 14 | 0b:01.0 | CPU0 Root Port | 8086:352A | CPU0 Port 1 [15:0] | x16 | 32.0 GT/s | | Examax #4 |
| 15 | 0c:00.0 | CX7_7 Switch Upstream Port | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #4 |
| 16 | 0d:00.0 | CX7_7 Switch Downstream Port#1 | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #4 |
| 17 | 0e:00.0 | CX7 #7 IB MT28861 PCIe Endpoint | 15b3:1021 | | x16 | 32.0 GT/s | CX7 #7 (mt4129_pciconf1) | Examax #4 |
| 18 | 0d:02.0 | CX7_7 Switch Downstream Port#2 | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #4 |
| 19 | 0f:00.0 | CX7_7 Switch Upstream Port | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #4 |
| 20 | 10:00.0 | CX7_7 Switch Downstream Port | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #4 |
| 21 | 11:00.0 | Nvidia Delta Next 3D Controller | 10de:2330 | | x16 | 32.0 GT/s | GPU #1 (nvidia-smi) / GPU #2 (physical) | Examax #4 |

### CPU0 Port 2 [15:0] — Examax #4 (GPU #2/nvidia-smi → GPU #4/physical)

| # | Bus:Dev.Fn | Description | Vendor:Device ID | CPU Port | Width | Speed | Physical Slot | Cable |
|---|---|---|---|---|---|---|---|---|
| 22 | 12:01.0 | CPU0 Root Port | 8086:352A | CPU0 Port 2 [15:0] | x16 | 32.0 GT/s | | Examax #4 |
| 23 | 13:00.0 | CX7_8 Switch Upstream Port | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #4 |
| 24 | 14:00.0 | CX7_8 Switch Downstream Port#1 | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #4 |
| 25 | 15:00.0 | CX7 #8 IB MT28861 PCIe Endpoint | 15b3:1021 | | x16 | 32.0 GT/s | CX7 #8 (mt4129_pciconf2) | Examax #4 |
| 26 | 14:02.0 | CX7_8 Switch Downstream Port#2 | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #4 |
| 27 | 16:00.0 | CX7_8 Switch Upstream Port | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #4 |
| 28 | 17:00.0 | CX7_8 Switch Downstream Port | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #4 |
| 29 | 18:00.0 | Nvidia Delta Next 3D Controller | 10de:2330 | | x16 | 32.0 GT/s | GPU #2 (nvidia-smi) / GPU #4 (physical) | Examax #4 |

### CPU0 Port 3 [3:2] — Examax #3 (NVSwitch #1–#4 via PMC-Sierra Bridge)

| # | Bus:Dev.Fn | Description | Vendor:Device ID | CPU Port | Width | Speed | Physical Slot | Cable |
|---|---|---|---|---|---|---|---|---|
| 30 | 19:02.0 | CPU0 Root Port | 8086:347d | CPU0 Port 3 [3:2] | x2 | 16.0 GT/s | | Examax #3 |
| 31 | 1a:00.0 | PMC-Sierra PCIe Bridge | 11f8:4128 | | x2 | 16.0 GT/s | | Examax #3 |
| 32 | 1a:00.1 | PMC-Sierra Memory Controller | 11f8:4128 | | x2 | 16.0 GT/s | | Examax #3 |
| 33 | 1b:00.0 | PMC-Sierra PCIe Downstream Port#1 | 11f8:4128 | | x2 | 16.0 GT/s | | Examax #3 |
| 34 | 1c:00.0 | Nvidia PCIe Endpoint#1 | 10de:22a3 | | x2 | 16.0 GT/s | NVSwitch #1 | Examax #3 |
| 35 | 1b:01.0 | PMC-Sierra PCIe Downstream Port#2 | 11f8:4128 | | x2 | 16.0 GT/s | | Examax #3 |
| 36 | 1d:00.0 | Nvidia PCIe Endpoint#2 | 10de:22a3 | | x2 | 16.0 GT/s | NVSwitch #2 | Examax #3 |
| 37 | 1b:02.0 | PMC-Sierra PCIe Downstream Port#3 | 11f8:4128 | | x2 | 16.0 GT/s | | Examax #3 |
| 38 | 1e:00.0 | Nvidia PCIe Endpoint#3 | 10de:22a3 | | x2 | 16.0 GT/s | NVSwitch #3 | Examax #3 |
| 39 | 1b:03.0 | PMC-Sierra PCIe Downstream Port#4 | 11f8:4128 | | x2 | 16.0 GT/s | | Examax #3 |
| 40 | 1f:00.0 | Nvidia PCIe Endpoint#4 | 10de:22a3 | | x2 | 16.0 GT/s | NVSwitch #4 | Examax #3 |

### CPU0 Port 3 [7:4] — NVMe M.2 Slot#2

| # | Bus:Dev.Fn | Description | Vendor:Device ID | CPU Port | Width | Speed | Physical Slot | Cable |
|---|---|---|---|---|---|---|---|---|
| 41 | 19:03.0 | CPU0 Root Port | 8086:352b | CPU0 Port 3 [7:4] | x4 | 8.0 GT/s | | |
| 42 | 20:00.0 | Samsung NVMe SSD Controller | 144d:a80a | | x4 | 8.0 GT/s | HPM M.2 Slot#2 (Service) - Top | |

### CPU0 Port 3 [15:8] — Examax #4 (E1.S NVMe #5–#8 via PEX890xx Switch)

| # | Bus:Dev.Fn | Description | Vendor:Device ID | CPU Port | Width | Speed | Physical Slot | Cable |
|---|---|---|---|---|---|---|---|---|
| 43 | 19:05.0 | CPU0 Root Port | 8086:352c | CPU0 Port 3 [15:8] | x8 | 32.0 GT/s | | Examax #4 |
| 44 | 21:00.0 | PEX890xx PCIe Gen 5 Switch | 1000:c030 | | x8 | 32.0 GT/s | HIB PCIe Gen5 Switch | Examax #4 |
| 45 | 22:00.0 | PEX890xx PCIe Gen 5 Switch Downstream Port#1 | 1000:c030 | | x16 | 5.0 GT/s | | Examax #4 |
| 46 | 23:00.0 | PEX890xx PCIe Gen 5 Switch Upstream Port | 1000:c030 | | x16 | 5.0 GT/s | | Examax #4 |
| 47 | 24:10.0 | PEX890xx PCIe Gen 5 Switch Downstream Port#1 | 1000:c030 | | x4 | 16.0 GT/s | | Examax #4 |
| 48 | 25:00.0 | Samsung NVMe PCIe Endpoint | 144d:a826 | | x4 | 16.0 GT/s | E1.S#5 | Examax #4 |
| 49 | 24:14.0 | PEX890xx PCIe Gen 5 Switch Downstream Port#2 | 1000:c030 | | x4 | 16.0 GT/s | | Examax #4 |
| 50 | 26:00.0 | Samsung NVMe PCIe Endpoint | 144d:a826 | | x4 | 16.0 GT/s | E1.S#6 | Examax #4 |
| 51 | 24:18.0 | PEX890xx PCIe Gen 5 Switch Downstream Port#3 | 1000:c030 | | x4 | 16.0 GT/s | | Examax #4 |
| 52 | 27:00.0 | Samsung NVMe PCIe Endpoint | 144d:a826 | | x4 | 16.0 GT/s | E1.S#7 | Examax #4 |
| 53 | 24:1c.0 | PEX890xx PCIe Gen 5 Switch Downstream Port#4 | 1000:c030 | | x4 | 16.0 GT/s | | Examax #4 |
| 54 | 28:00.0 | Samsung NVMe PCIe Endpoint | 144d:a826 | | x4 | 16.0 GT/s | E1.S#8 | Examax #4 |

### CPU0 Port 4 [15:0] — Examax #3 (GPU #3/nvidia-smi → GPU #1/physical)

| # | Bus:Dev.Fn | Description | Vendor:Device ID | CPU Port | Width | Speed | Physical Slot | Cable |
|---|---|---|---|---|---|---|---|---|
| 55 | 03:01.0 | CPU0 Root Port | 8086:352A | CPU0 Port 4 [15:0] | x16 | 32.0 GT/s | | Examax #3 |
| 56 | 64:00.0 | CX7_5 Switch Upstream Port | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #3 |
| 57 | 65:00.0 | CX7_5 Switch Downstream Port#1 | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #3 |
| 58 | 66:00.0 | CX7 #5 IB MT28861 PCIe Endpoint | 15b3:1021 | | x16 | 32.0 GT/s | CX7 #5 (mt4129_pciconf3) | Examax #3 |
| 59 | 65:02.0 | CX7_5 Switch Downstream Port#2 | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #3 |
| 60 | 67:00.0 | CX7_5 Switch Upstream Port | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #3 |
| 61 | 68:00.0 | CX7_5 Switch Downstream Port | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #3 |
| 62 | 69:00.0 | Nvidia Delta Next 3D Controller | 10de:2330 | | x16 | 32.0 GT/s | GPU #3 (nvidia-smi) / GPU #1 (physical) | Examax #3 |

### CPU1 Domain

#### CPU1 DMI — Examax #2

| # | Bus:Dev.Fn | Description | Vendor:Device ID | CPU Port | Width | Speed | Physical Slot | Cable |
|---|---|---|---|---|---|---|---|---|
| 63 | 20:05.0 | CPU1 Root Port | 8086:352c | CPU1 DMI | x8 | 32.0 GT/s | | Examax #2 |

#### HPM PCIe Gen5 Switch — Examax #2

| # | Bus:Dev.Fn | Description | Vendor:Device ID | CPU Port | Width | Speed | Physical Slot | Cable |
|---|---|---|---|---|---|---|---|---|
| 64 | 81:00.0 | PEX890xx PCIe Gen 5 Switch upstream Port | 1000:c030 | | x8 | 32.0 GT/s | HPM PCIe Gen5 Switch | Examax #2 |
| 65 | 82:00.0 | PEX890xx PCIe Gen 5 Switch Downstream Port#1 | 1000:c030 | | x16 | 5.0 GT/s | | Examax #2 |
| 66 | 83:00.0 | PEX890xx PCIe Gen 5 Switch upstream Port | 1000:c030 | | x16 | 5.0 GT/s | | Examax #2 |
| 67 | 84:00.0 | PEX890xx PCIe Gen 5 Switch Downstream Port#1 | 1000:c030 | | x4 | 16.0 GT/s | | Examax #2 |
| 68 | 85:00.0 | Samsung NVMe PCIe Endpoint | 144d:a826 | | x4 | 16.0 GT/s | E1.S#1 | Examax #2 |
| 69 | 84:04.0 | PEX890xx PCIe Gen 5 Switch Downstream Port#2 | 1000:c030 | | x4 | 16.0 GT/s | | Examax #2 |
| 70 | 86:00.0 | Samsung NVMe PCIe Endpoint | 144d:a826 | | x4 | 16.0 GT/s | E1.S#2 | Examax #2 |
| 71 | 84:08.0 | PEX890xx PCIe Gen 5 Switch Downstream Port#3 | 1000:c030 | | x4 | 16.0 GT/s | | Examax #1 |
| 72 | 87:00.0 | Samsung NVMe PCIe Endpoint | 144d:a826 | | x4 | 16.0 GT/s | E1.S#3 | Examax #1 |
| 73 | 84:0c.0 | PEX890xx PCIe Gen 5 Switch Downstream Port#4 | 1000:c030 | | x4 | 16.0 GT/s | | Examax #1 |
| 74 | 88:00.0 | Samsung NVMe PCIe Endpoint | 144d:a826 | | x4 | 16.0 GT/s | E1.S#4 | Examax #1 |

#### HPM PCIe Gen5 Switch Downstream Port#5 — NVMe M.2 Slot#3

| # | Bus:Dev.Fn | Description | Vendor:Device ID | CPU Port | Width | Speed | Physical Slot | Cable |
|---|---|---|---|---|---|---|---|---|
| 75 | 84:10.0 | PEX890xx PCIe Gen 5 Switch Downstream Port#5 | 1000:c030 | | x4 | 8.0 GT/s | HPM PCIe Gen5 Switch | |
| 76 | 89:00.0 | Samsung NVMe SSD Controller | 144d:a80a | | x4 | 8.0 GT/s | HPM M.2 Slot#3 (Service) | |

#### HPM PCIe Gen5 Switch Downstream Port#2 — Examax #1

| # | Bus:Dev.Fn | Description | Vendor:Device ID | CPU Port | Width | Speed | Physical Slot | Cable |
|---|---|---|---|---|---|---|---|---|
| 77 | 82:08.0 | PEX890xx PCIe Gen 5 Switch Downstream Port#2 | 1000:c030 | | x16 | 5.0 GT/s | | |
| 78 | 8a:00.0 | PEX890xx PCIe Gen 5 Switch upstream Port | 1000:c030 | | x16 | 5.0 GT/s | | |
| 79 | 8b:10.0 | PEX890xx PCIe Gen 5 Switch Downstream Port | 1000:c030 | | x8 | 16.0 GT/s | | |
| 80 | 8c:00.0 | Mellanox CX-5 | 15b3:1019 | | x8 | 16.0 GT/s | CX5 | |

#### CPU1 Port 0 [15:0] — Examax #1 (GPU #4/nvidia-smi → GPU #5/physical)

| # | Bus:Dev.Fn | Description | Vendor:Device ID | CPU Port | Width | Speed | Physical Slot | Cable |
|---|---|---|---|---|---|---|---|---|
| 81 | 97:01.0 | CPU1 Root Port | 8086:352A | CPU1 Port 0 [15:0] | x16 | 32.0 GT/s | | Examax #1 |
| 82 | 98:00.0 | CX7_1 Switch Upstream Port | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #1 |
| 83 | 99:00.0 | CX7_1 Switch Downstream Port#1 | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #1 |
| 84 | 9a:00.0 | CX7 #1 IB MT28861 PCIe Endpoint | 15b3:1021 | | x16 | 32.0 GT/s | CX7 #1 (mt4129_pciconf4) | Examax #1 |
| 85 | 99:02.0 | CX7_1 Switch Downstream Port#2 | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #1 |
| 86 | 9b:00.0 | CX7_1 Switch Upstream Port | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #1 |
| 87 | 9c:00.0 | CX7_1 Switch Downstream Port | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #1 |
| 88 | 9d:00.0 | Nvidia Delta Next 3D Controller | 10de:2330 | | x16 | 32.0 GT/s | GPU #4 (nvidia-smi) / GPU #5 (physical) | Examax #1 |

#### CPU1 Port 1 [15:0] — Examax #2 (GPU #5/nvidia-smi → GPU #6/physical)

| # | Bus:Dev.Fn | Description | Vendor:Device ID | CPU Port | Width | Speed | Physical Slot | Cable |
|---|---|---|---|---|---|---|---|---|
| 89 | a7:01.0 | CPU1 Root Port | 8086:352A | CPU1 Port 1 [15:0] | x16 | 32.0 GT/s | | Examax #2 |
| 90 | a8:00.0 | CX7_3 Switch Upstream Port | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #2 |
| 91 | a9:00.0 | CX7_3 Switch Downstream Port#1 | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #2 |
| 92 | aa:00.0 | CX7 #3 IB MT28861 PCIe Endpoint | 15b3:1021 | | x16 | 32.0 GT/s | CX7 #3 (mt4129_pciconf5) | Examax #2 |
| 93 | a9:02.0 | CX7_3 Switch Downstream Port#2 | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #2 |
| 94 | ab:00.0 | CX7_3 Switch Upstream Port | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #2 |
| 95 | ac:00.0 | CX7_3 Switch Downstream Port | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #2 |
| 96 | ad:00.0 | Nvidia Delta Next 3D Controller | 10de:2330 | | x16 | 32.0 GT/s | GPU #5 (nvidia-smi) / GPU #6 (physical) | Examax #2 |

#### CPU1 Port 2 [15:0] — Examax #2 (GPU #6/nvidia-smi → GPU #8/physical)

| # | Bus:Dev.Fn | Description | Vendor:Device ID | CPU Port | Width | Speed | Physical Slot | Cable |
|---|---|---|---|---|---|---|---|---|
| 97 | b7:01.0 | CPU1 Root Port | 8086:352A | CPU1 Port 2 [15:0] | x16 | 32.0 GT/s | | Examax #2 |
| 98 | b8:00.0 | CX7_4 Switch Upstream Port | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #2 |
| 99 | b9:00.0 | CX7_4 Switch Downstream Port#1 | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #2 |
| 100 | ba:00.0 | CX7 #4 IB MT28861 PCIe Endpoint | 15b3:1021 | | x16 | 32.0 GT/s | CX7 #4 (mt4129_pciconf6) | Examax #2 |
| 101 | b9:02.0 | CX7_4 Switch Downstream Port#2 | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #2 |
| 102 | bb:00.0 | CX7_4 Switch Upstream Port | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #2 |
| 103 | bc:00.0 | CX7_4 Switch Downstream Port | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #2 |
| 104 | bd:00.0 | Nvidia Delta Next 3D Controller | 10de:2330 | | x16 | 32.0 GT/s | GPU #6 (nvidia-smi) / GPU #8 (physical) | Examax #2 |

#### CPU1 Port 3 [15:0] — Examax #1 (Celestica I Peak HIP)

| # | Bus:Dev.Fn | Description | Vendor:Device ID | CPU Port | Width | Speed | Physical Slot | Cable |
|---|---|---|---|---|---|---|---|---|
| 105 | c7:01.0 | CPU1 Root Port | 8086:352A | CPU1 Port 3 [15:0] | x16 | 8.0 GT/s | | |
| 106 | c8:00.0 | Celestica I Peak HIP 0 | 1414:b20d | | x16 | 8.0 GT/s | | |
| 107 | c8:00.1 | Celestica I Peak HIP 1 | 1414:b28d | | x16 | 8.0 GT/s | | |

#### CPU1 Port 4 [15:0] — Examax #1 (GPU #7/nvidia-smi → GPU #7/physical)

| # | Bus:Dev.Fn | Description | Vendor:Device ID | CPU Port | Width | Speed | Physical Slot | Cable |
|---|---|---|---|---|---|---|---|---|
| 108 | d7:01.0 | CPU1 Root Port | 8086:352A | CPU1 Port 4 [15:0] | x16 | 32.0 GT/s | | Examax #1 |
| 109 | d8:00.0 | CX7_2 Switch Upstream Port | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #1 |
| 110 | d9:00.0 | CX7_2 Switch Downstream Port#1 | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #1 |
| 111 | da:00.0 | CX7 #2 IB MT28861 PCIe Endpoint | 15b3:1021 | | x16 | 32.0 GT/s | CX7 #2 (mt4129_pciconf7) | Examax #1 |
| 112 | d9:02.0 | CX7_2 Switch Downstream Port#2 | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #1 |
| 113 | db:00.0 | CX7_2 Switch Upstream Port | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #1 |
| 114 | dc:00.0 | CX7_2 Switch Downstream Port | 15b3:1979 | | x16 | 32.0 GT/s | | Examax #1 |
| 115 | dd:00.0 | Nvidia Delta Next 3D Controller | 10de:2330 | | x16 | 32.0 GT/s | GPU #7 (nvidia-smi) / GPU #7 (physical) | Examax #1 |

---

## Appendix B — Quick Bus-to-Device Lookup

### GPUs & CX7 NICs

| Bus (Hex) | Bus (Dec) | Device | nvidia-smi # | Physical # | Cable |
|---|---|---|---|---|---|
| 0a | 10 | GPU #0 | nvidia-smi GPU 0 | Physical GPU 3 | Examax #3 |
| 11 | 17 | GPU #1 | nvidia-smi GPU 1 | Physical GPU 2 | Examax #4 |
| 18 | 24 | GPU #2 | nvidia-smi GPU 2 | Physical GPU 4 | Examax #4 |
| 69 | 105 | GPU #3 | nvidia-smi GPU 3 | Physical GPU 1 | Examax #3 |
| 9d | 157 | GPU #4 | nvidia-smi GPU 4 | Physical GPU 5 | Examax #1 |
| ad | 173 | GPU #5 | nvidia-smi GPU 5 | Physical GPU 6 | Examax #2 |
| bd | 189 | GPU #6 | nvidia-smi GPU 6 | Physical GPU 8 | Examax #2 |
| dd | 221 | GPU #7 | nvidia-smi GPU 7 | Physical GPU 7 | Examax #1 |
| 07 | 7 | CX7 #6 | mt4129_pciconf0 | | Examax #3 |
| 0e | 14 | CX7 #7 | mt4129_pciconf1 | | Examax #4 |
| 15 | 21 | CX7 #8 | mt4129_pciconf2 | | Examax #4 |
| 66 | 102 | CX7 #5 | mt4129_pciconf3 | | Examax #3 |
| 9a | 154 | CX7 #1 | mt4129_pciconf4 | | Examax #1 |
| aa | 170 | CX7 #3 | mt4129_pciconf5 | | Examax #2 |
| ba | 186 | CX7 #4 | mt4129_pciconf6 | | Examax #2 |
| da | 218 | CX7 #2 | mt4129_pciconf7 | | Examax #1 |

### NVSwitch, NVMe & Root Ports

| Bus (Hex) | Bus (Dec) | Device | Physical Slot | Cable |
|---|---|---|---|---|
| 1c | 28 | NVSwitch #1 | | Examax #3 |
| 1d | 29 | NVSwitch #2 | | Examax #3 |
| 1e | 30 | NVSwitch #3 | | Examax #3 |
| 1f | 31 | NVSwitch #4 | | Examax #3 |
| 03 | 3 | Samsung NVMe | HPM M.2 Slot#1 (Boot) | |
| 20 | 32 | Samsung NVMe | HPM M.2 Slot#2 (Service) - Top | |
| 89 | 137 | Samsung NVMe | HPM M.2 Slot#3 (Service) | |
| 25 | 37 | Samsung NVMe | E1.S#5 | Examax #4 |
| 26 | 38 | Samsung NVMe | E1.S#6 | Examax #4 |
| 27 | 39 | Samsung NVMe | E1.S#7 | Examax #4 |
| 28 | 40 | Samsung NVMe | E1.S#8 | Examax #4 |
| 85 | 133 | Samsung NVMe | E1.S#1 | Examax #2 |
| 86 | 134 | Samsung NVMe | E1.S#2 | Examax #2 |
| 87 | 135 | Samsung NVMe | E1.S#3 | Examax #1 |
| 88 | 136 | Samsung NVMe | E1.S#4 | Examax #1 |

> Block diagram: refer to **Figure 24: C2789 PCIe Mapping Block Diagram** in the original ByteDance H100 PCIfatal wiki for the physical signal-path topology.

---

## Appendix C — Known Scenario Samples & Action Plans

| # | Bus:Device.Function | Description | CPU Port | Physical Slot | Scenario | Action Plan |
|---|---|---|---|---|---|---|
| 1 | A7:01.0 | CPU1 Root Port | CPU1 Port 1 [15:0] | | Downstream till CX7, path includes Retimer and Linking Cable. Old Retimer issue fixed in Retimer firmware 5B. If fatal error continues, indicates motherboard hw issue or HIB issue (board on top of motherboard). Link-cable damage probability is low (usually shows as PCIe bus degrade). | For constant node failure with this device, ICM HW team to replace motherboard, then HIB. Node AC cycle first — expect a node reboot on 1st occurrence. If failure persists, raise ICM to replace motherboard. |
| 2 | 09:00.0 | CX7_6 Switch Downstream Port | | | CX7 firmware issue [Bug 1602652](https://azurecsi.visualstudio.com/C2789/_workitems/edit/1602652): [ZT Scale] Fatal error GPU recoverable Gen4 TO [(NVBug 4390973)](https://nvbug/4390973). MS is currently testing the new fw. | Deliver, close case. (Rebecca has one case following this symptom.) |
| 3 | 85:00.0 | Samsung NVMe PCIe Endpoint | | E1.S#1 | Unexpected — could be NVMe health related | Raise separate ICM |
| 4 | 0a:00.0 | Nvidia Delta Next 3D Controller | | GPU #0 (nvidia-smi) / GPU #3 (physical) | GPU Uncorrectable Error Status register Completion Timeout bit flagged. If host bugcheck 0x124 happened alongside → hit [Incident-558515455](https://portal.microsofticm.com/imp/v3/incidents/details/558515455/home) | ETA for 1C21.GN2 BIOS deployment completion is May 9, 2025. If a cluster constantly reports this, raise ICM to prioritize the patch. |
| 5 | 19:02.0 | CPU0 Root Port | CPU0 Port 3 [3:2] | | Downstream connected to NVSwitch | Either GPU issue or GPU BB issue — combine with `LogNodeSnapshot` for further diagnostic |

> **Note**: GPU clusters carry extremely heavy workloads. NVIDIA designed this system expecting hardware failures may occur. The most common first step is an AC power cycle; if the same error persists, the related component is replaced as a cost-effective resolution.

---

## Appendix D — Hardware Replacement Record Check

When you suspect a HW replacement may have happened (or want to confirm one didn't), use **Datacenter Central**:

1. Open **Datacenter Central**
2. Search node id by **AssetName: nodeid**
3. Record sample — check Fault Description, Severity, State, SLA, Work Window Start Date, Relationships, Actual Arrival Date, Created Date
4. Identify the actual hardware replacement:
   - **Failed part(s)** — Board Layout Image
   - Part type, Manufacturer, Model, Serial, Location, Repair action
   - Example: `Processor | GenuineIntel | Intel(R) Xeon(R) Platinum 8480C | UNKNOWN | CPU1 | Replace`
5. If no entry is located here after OFR, that probably indicates only power recycling happened — not a replacement.

Goal: identify the failing component and analyze a node's failure trend so we can manage ICMs without creating a load of duplicate effort.
