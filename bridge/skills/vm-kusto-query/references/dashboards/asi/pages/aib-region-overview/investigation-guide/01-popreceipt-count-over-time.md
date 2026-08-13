# PopReceipt Count Over Time

> Source: **RegionOverview** dashboard, chapter **PopReceipt Count Over Time** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### PopReceipt Count Over Time - No VMSS

_Widget purpose:_ PopReceipt Count Over Time

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `TimeSeries`
Source panel: `PopReceipt Count Over Time`

```kusto
let interval = 1m;
let threshold = 80;
// let targetSector = "eastus";
// concurrent message limit
AsyncContextActivity
| where PreciseTimeStamp between ( queryFrom .. queryTo )
| where RPTenant == "prod"
| where RPSector == targetRegion
| where  operationName != "SourceImageTriggerEvaluationTask"
| summarize MessageInProcess = dcount(popReceipt) by bin(PreciseTimeStamp, interval), RPSector
| extend Threshold = threshold
| extend HalfThreshold = 0.5*threshold
| render timechart with (title = "PopReceipt Count Over Time")
```

**Params:** `{queryFrom}`, `{queryTo}`, `{targetRegion}`

**Signal filters seen in KQL:** `RPTenant == "prod"` · `operationName != "SourceImageTriggerEvaluationTask"`

---

### ListRpSectors

_Widget purpose:_ PopReceipt Count Over Time

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `Filter` · Widget: `TimeSeries`
Source panel: `PopReceipt Count Over Time`

```kusto
AsyncContextActivity
| where RPTenant == "prod"
| distinct RPSector
| extend Value = RPSector
| project Value
```

**Signal filters seen in KQL:** `RPTenant == "prod"`

---
