# GetVirtualNetworkOperation Concurrency Cirrus Runs

> Source: **NRP - ReadOperationService** dashboard, chapter **GetVirtualNetworkOperation Concurrency Cirrus Runs** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### ReadOperationService GetVnet Cirrus

_Widget purpose:_ GetVirtualNetworkOperation Concurrency Cirrus Runs

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `GetVirtualNetworkOperation Concurrency Cirrus Runs`

```kusto
let cirrusMetadata = cluster("cirrus.kusto.windows.net").database("cirrus").PerfMeasurement
| where StartTime between(queryFrom..queryTo)
| where SubscriptionId == "75903edc-ce96-496f-8580-a4e306a69490"
| where RequestName contains "ConcurrentVnetGet"
| distinct RequestName, ResourceName
| parse RequestName with region"."concurrencyLevel"ConcurrentVnetGet."ipConfigCount:int"IpConfigs-CloudEx"
| project ipConfigCount, concurrencyLevel, ResourceName, Baseline=iff(region=="CentralUsEUAP", "Frontend", "ReadOperationService");
cluster("nrp.kusto.windows.net").database("mdsnrp").FrontendReadOperationEtwEvent
| where Region in ("useast2euap", "uscentraleuap")
| where PreciseTimeStamp between(queryFrom..queryTo)
| where SubscriptionId == "75903edc-ce96-496f-8580-a4e306a69490"
| where ResourceType == "virtualNetworks"
| summarize max(PreciseTimeStamp), min(PreciseTimeStamp) by OperationId, ResourceGroup
| extend accurateTime = max_PreciseTimeStamp - min_PreciseTimeStamp
| summarize StartTime=min(min_PreciseTimeStamp), Requests=count(), percentiles(accurateTime, 50, 75, 90, 95, 99, 99.9, 100) by ResourceGroup
| join cirrusMetadata on $left.ResourceGroup == $right.ResourceName
| project Baseline, StartTime, Requests, ipConfigCount, percentile_accurateTime_50, percentile_accurateTime_75, percentile_accurateTime_90, percentile_accurateTime_95, percentile_accurateTime_99, percentile_accurateTime_99_9, percentile_accurateTime_100
| where ipConfigCount == vnetSize
| order by ipConfigCount, Baseline
```

**Params:** `{queryFrom}`, `{queryTo}`, `{vnetSize}`

**Signal filters seen in KQL:** `SubscriptionId == "75903edc-ce96-496f-8580-a4e306a69490"` · `RequestName contains "ConcurrentVnetGet"` · `ResourceType == "virtualNetworks"`

---
