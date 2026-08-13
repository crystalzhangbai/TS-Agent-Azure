# Sub level

> Source: **NRP - DELETE VMScaleSet operation drilldown** dashboard, chapter **Sub level** (4 queries across 4 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Delete VMSS Ip configurations reads

### DeleteVmssIpConfigReads

_Widget purpose:_ Delete VMSS Ip configurations reads

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Sub level > Delete VMSS Ip configurations reads`

```kusto
KvsTransactionEtwEvent
| where PreciseTimeStamp between (queryFrom ..queryTo)
| where Region == region
| where SubscriptionId == subId
| where OperationName in ("DeleteVMScaleSetOperation")
| project PreciseTimeStamp, ReadCount, ReadSize, AddCount, AddSize, TypeBasedReadCount, UpdateCount, UpdateSize, OperationId
| where ReadCount > 0
| extend IpConfigurationsReadCount = toint(extract(@"ipConfigurations : (\d+);", 1, TypeBasedReadCount))
| summarize AvgIpConfigurationsReadCount = round(todouble(sum(IpConfigurationsReadCount)) / dcount(OperationId),2) by bin(PreciseTimeStamp, 5m)
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`, `{subId}`

---

## Delete VMSS Subnet reads

### DeleteVmssSubnetReadsSub

_Widget purpose:_ Delete VMSS Subnet reads

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Sub level > Delete VMSS Subnet reads`

```kusto
KvsTransactionEtwEvent
| where PreciseTimeStamp between (queryFrom ..queryTo)
| where Region == region
| where SubscriptionId == subId
| where OperationName in ("DeleteVMScaleSetOperation")
| project PreciseTimeStamp, ReadCount, ReadSize, AddCount, AddSize, TypeBasedReadCount, UpdateCount, UpdateSize, OperationId
| where ReadCount > 0
| extend IpConfigurationsReadCount = toint(extract(@"ipConfigurations : (\d+);", 1, TypeBasedReadCount))
| extend SubnetReadCount = toint(extract(@"subnets : (\d+);", 1, TypeBasedReadCount))
| extend VnetReadCount = toint(extract(@"virtualNetworks : (\d+);", 1, TypeBasedReadCount))
| extend vmssReadCount = toint(extract(@"virtualMachineScaleSets : (\d+);", 1, TypeBasedReadCount))
| extend nicReadCount = toint(extract(@"networkInterfaces : (\d+);", 1, TypeBasedReadCount))
| extend tenantReadCount = toint(extract(@"tenants : (\d+);", 1, TypeBasedReadCount))
| extend vmReadCount = toint(extract(@"virtualMachines : (\d+);", 1, TypeBasedReadCount))
| summarize //AvgVnetReadCount = round(todouble(sum(VnetReadCount)) / dcount(OperationId),2),
            //AvgNicReadCount = round(todouble(sum(nicReadCount)) / dcount(OperationId),2), 
            //AvgIpConfigurationsReadCount = round(todouble(sum(IpConfigurationsReadCount)) / dcount(OperationId),2),
            AvgSubnetReadCount = round(todouble(sum(SubnetReadCount)) / dcount(OperationId),2)  by bin(PreciseTimeStamp, 5m)
            //AvgVMReadCount = round(todouble(sum(vmReadCount)) / dcount(OperationId),2),
            //AvgTenantReadCount = round(todouble(sum(tenantReadCount)) / dcount(OperationId),2) by bin(PreciseTimeStamp, 5m)
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`, `{subId}`

---

## Sub lock duration

### DeleteVmssSubLockSub

_Widget purpose:_ Sub lock duration

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Sub level > Sub lock duration`

```kusto
let location = region;
let startTime = queryFrom;
let endTime = queryTo;
let subIds = subId;
let regex="Operation (.+) \\((.+)\\) released lock (.+) after (\\d+) ms";
let dvmss=WriteOperationResponseEtwEvent
| where PreciseTimeStamp between (startTime..endTime)
| where Region == location
| where SubscriptionId in (subIds)
| where OperationName in ("DeleteVMScaleSetOperation")
| where HttpStatusCode == "Accepted"
| distinct OperationId;
//dvmss;
let subLock=FrontendOperationEtwEvent
| where Region == location
| where SubscriptionId in (subIds)
| where PreciseTimeStamp between (startTime..endTime)
| where OperationName in ("DeleteVMScaleSetOperation")
| where EventCode == "LockReleased"
| extend cou = OperationId in (dvmss)
| extend LockName=extract(regex, 3, Message)
| extend LockDuration=toint(extract(regex, 4, Message))
| where LockName == SubscriptionId
| summarize sum(LockDuration) by bin(PreciseTimeStamp, 1d)
| render timechart;
subLock;
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`, `{subId}`

**Signal filters seen in KQL:** `HttpStatusCode == "Accepted"` · `EventCode == "LockReleased"`

---

## Transaction stats (KB)

### DeleteVmssTransactionStatsSub

_Widget purpose:_ Transaction stats (KB)

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `TimeSeries`
Source panel: `Sub level > Transaction stats (KB)`

```kusto
KvsTransactionEtwEvent
| where PreciseTimeStamp between (queryFrom ..queryTo)
| where Region == region
| where SubscriptionId == subId
| where OperationName in ("DeleteVMScaleSetOperation")
| project PreciseTimeStamp, ReadCount, ReadSize, AddCount, AddSize, ReadDuration, CommitDuration, UpdateCount, UpdateSize, OperationId
| summarize readSizeKb = sum(ReadSize)/1000, addSizeKb = sum(AddSize)/1000, updateSizeKb = sum(UpdateSize)/1000 by bin(PreciseTimeStamp, 5m)
| render timechart
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`, `{subId}`

---
