# Detectors — Host CPU / Memory / Power

> Source: EEE RDOS Start Hub dashboard (2 queries).

Host CPU throttle, memory pressure, and thermal signatures.

---

### IssueDetector_HighHostCPU_temp_throttle

_Purpose:_ Automated Detector

Cluster: `sparkle.eastus.kusto.windows.net` · Database: `defaultdb` · Type: `IssueDetector`

```kusto
cluster("sparkle.eastus.kusto.windows.net").database("defaultdb").SparkleSELByNodeId(query_NodeId)
| where BMCSelTimestamp between (queryFrom .. queryTo) and ((SensorType == "Processor" and EventDataDetails1 == "Processor Automatically Throttled") or (SensorType == "Temperature" and EventDataDetails1 has "unspecified value") or (SensorType == "Fan" and EventDataDetails1 == "Pulse Width Modulation"))
| project Timestamp = BMCSelTimestamp, Source = GeneratorId, EventType, Sensor = SensorType, Details = EventDataDetails1, RawHex
| take 1
| extend Description = "High Host CPU temperatur or throttle found"
| extend Severity = "warning"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{query_NodeId}`

---

### IssueDetector_HighHostCPU_throttle

_Purpose:_ Automated Detector

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `IssueDetector`

```kusto
cluster("azcore.centralus.kusto.windows.net").database("Fa").WindowsEventTable
| where PreciseTimeStamp between (queryFrom .. queryTo) and NodeId == _nodeId
| where EventId == 37 and ProviderName == "Microsoft-Windows-Kernel-Processor-Power"
| project TimeCreated,NodeId,Level,Channel,EventId,ProviderName,Description
| take 1
| extend Description = "Host CPU throttle found"
| extend Severity = "warning"
```

**Params:** `{queryFrom}`, `{queryTo}`, `{_nodeId}`

---
