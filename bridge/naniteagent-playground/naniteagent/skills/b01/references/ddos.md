# Skill: DDoS Investigation - External ↔ Azure Public IP Traffic

## Description
End-to-end investigation of DDoS patterns using IPFIX (NetCapPlan) and DDoS flow logs. Enables analysis of traffic direction, top talkers, protocol distribution, and volumetric attack detection.

---

## Parameters

| Name | Type | Description | Example |
|------|------|-------------|---------|
| _startTime | datetime | Investigation start time | 2026-04-17 21:00 |
| _endTime | datetime | Investigation end time | 2026-04-17 22:00 |
| TargetPublicIP | string | Azure Public IP under investigation | 20.254.73.46 |
| SrcIPFilter | string | Optional source IP filter | 20.254.73.46 |
| Protocol | int | Protocol filter (6=TCP, 17=UDP, null=all) | 6 |
| dropThreshold | int | PPS threshold for anomaly detection | 50000 |
| lookbackDays | int | Historical analysis window | 60 |

---

## Scenario 1: Azure Public IP ↔ Internet Traffic (Detailed Flow View)

### Query
```kql
let starttime = _startTime;
let endtime = _endTime;
cluster('NetCapplan').database('NetCapPlan').RealTimeIpfixWithMetadata
| where TimeStamp between (starttime .. endtime)
| where SrcIpAddress contains SrcIPFilter
| project TimeStamp, SrcIpAddress, DstIpAddress, DstTransportPort, NumOfBytes, NumOfPackets
```

### Purpose
- Analyze bidirectional flows
- Identify destination ports and traffic volume
- Validate suspicious communication patterns

---

## Scenario 2: External Sources → Azure Public IP (Top Talkers / PPS)

### Query
```kql
let starttime = _startTime;
let endtime = _endTime;
cluster('NetCapplan').database('NetCapPlan').RealTimeIpfixWithMetadata
| where TimeStamp between (starttime .. endtime)
| where DstIpAddress == TargetPublicIP
| summarize PPS = sum(NumOfPackets) * 4096 
    by bin(TimeStamp, 5m), SrcIpAddress, IpProtocolIdentifier
| where isnull(Protocol) or IpProtocolIdentifier == Protocol
| sort by PPS desc
```

### Purpose
- Identify top attacking IPs
- Detect protocol-based attack signatures
- Visualize PPS spikes over time

---

## Scenario 3: DDoS Flow Logs (Volumetric Attack Detection)

### Query
```kql
let threshold = dropThreshold;
let lookback = lookbackDays;
cluster("aznwddos.centralus.kusto.windows.net").database("cnsgeneva").DDoSPcapFlowLogs
| where TIMESTAMP >= ago(lookback * 1d)
| where protocolNumber == 17
| where messageValue !has "Forwarded"
| summarize PPS = count() * 1024 / 30 
    by destPublicIpAddress, window = bin(TIMESTAMP, 30s)
| where PPS > threshold
| render timechart
```

### Purpose
- Detect volumetric attacks (UDP floods)
- Identify affected public IPs
- Correlate attack spikes over time

---

## Analyst Workflow (Recommended)

1. **Start with Scenario 2**
   - Identify top attacking sources

2. **Pivot to Scenario 1**
   - Validate flow characteristics (ports, bytes)

3. **Use Scenario 3**
   - Confirm volumetric DDoS patterns

---

## Notes

- Protocol filters:
  - `6` → TCP (SYN flood patterns)
  - `17` → UDP (amplification attacks)
- PPS multipliers are sampling-dependent (4096 / 1024)
- Always correlate with:
  - Azure DDoS Protection metrics
  - Customer-reported impact time