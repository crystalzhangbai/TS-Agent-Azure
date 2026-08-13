# FW Operations

> Source: **NRP - Firewall** dashboard, chapter **FW Operations** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### AZ Firewall Operation Timline

_Widget purpose:_ FW Operations

Cluster: `nrp` · Database: `mdsnrp` · Type: `Timeline`
Source panel: `FW Operations`

```kusto
cluster("nrp.kusto.windows.net").database("mdsnrp").QosEtwEvent
| where PreciseTimeStamp between (qFrom .. qTo)
| where ResourceName =~ qName and ResourceGroup =~ qRG
| where SubscriptionId =~ qSub
| where HttpMethod !~ "GET"
| project PreciseTimeStamp, ResourceType, OperationId, OperationName, HttpMethod, Success, DurationInMilliseconds
| extend DurationInSeconds = round(DurationInMilliseconds / 1000)
| summarize arg_max(PreciseTimeStamp, *) by OperationId
| extend StartTime = PreciseTimeStamp
| extend Content = OperationName
| extend GroupBy = OperationName
```

**Params:** `{qFrom}`, `{qTo}`, `{qName}`, `{qSub}`, `{qRG}`

---
