# Put Vmss resource type read stats

> Source: **NRP - PUT VMScaleSet Operation drill down** dashboard, chapter **Put Vmss resource type read stats** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### PutVmssResourceTypeReadStats

_Widget purpose:_ Put Vmss resource type read stats

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Put Vmss resource type read stats`

```kusto
KvsTransactionEtwEvent
| where PreciseTimeStamp between (queryFrom ..queryTo)
| where Region == region
| where SubscriptionId == subId
| where OperationName in ("PutVMScaleSetOperation")
| project PreciseTimeStamp, ReadCount, ReadSize, AddCount, AddSize, TypeBasedReadCount, UpdateCount, UpdateSize, OperationId
| where ReadCount > 0
| extend IpConfigurationsReadCount = toint(extract(@"ipConfigurations : (\d+);", 1, TypeBasedReadCount))
| extend SubnetReadCount = toint(extract(@"subnets : (\d+);", 1, TypeBasedReadCount))
| extend VnetReadCount = toint(extract(@"virtualNetworks : (\d+);", 1, TypeBasedReadCount))
| extend vmssReadCount = toint(extract(@"virtualMachineScaleSets : (\d+);", 1, TypeBasedReadCount))
| extend nicReadCount = toint(extract(@"networkInterfaces : (\d+);", 1, TypeBasedReadCount))
| extend tenantReadCount = toint(extract(@"tenants : (\d+);", 1, TypeBasedReadCount))
| extend vmReadCount = toint(extract(@"virtualMachines : (\d+);", 1, TypeBasedReadCount))
| summarize AvgNicReadCount = round(todouble(sum(nicReadCount)) / dcount(OperationId),2), 
            //AvgIpConfigurationsReadCount = round(todouble(sum(IpConfigurationsReadCount)) / dcount(OperationId),2),
            AvgVMReadCount = round(todouble(sum(vmReadCount)) / dcount(OperationId),2),
            AvgTenantReadCount = round(todouble(sum(tenantReadCount)) / dcount(OperationId),2) by bin(PreciseTimeStamp, 5m)
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`, `{subId}`

---
