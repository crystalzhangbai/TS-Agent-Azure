# PutVmss Ipconfigurations reads

> Source: **NRP - PUT VMScaleSet Operation drill down** dashboard, chapter **PutVmss Ipconfigurations reads** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### PutVmssIpConfigsPerSubRead

_Widget purpose:_ PutVmss Ipconfigurations reads

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `PutVmss Ipconfigurations reads`

```kusto
KvsTransactionEtwEvent
| where PreciseTimeStamp between (queryFrom ..queryTo)
| where Region == region
| where SubscriptionId == subId
| where OperationName in ("PutVMScaleSetOperation")
| project PreciseTimeStamp, ReadCount, ReadSize, AddCount, AddSize, TypeBasedReadCount, UpdateCount, UpdateSize, OperationId
| where ReadCount > 0
| extend IpConfigurationsReadCount = toint(extract(@"ipConfigurations : (\d+);", 1, TypeBasedReadCount))
| summarize AvgIpConfigurationsReadCount = round(todouble(sum(IpConfigurationsReadCount)) / dcount(OperationId),2) by bin(PreciseTimeStamp, 5m)
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`, `{subId}`

---
