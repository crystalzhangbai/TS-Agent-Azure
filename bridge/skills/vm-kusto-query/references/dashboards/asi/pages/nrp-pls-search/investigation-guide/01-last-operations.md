# Last Operations

> Source: **NRP - PLS Search** dashboard, chapter **Last Operations** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### PLS_QosEtw

_Widget purpose:_ Last Operations

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Last Operations`

```kusto
QosEtwEvent
| where TIMESTAMP between (queryFrom .. queryTo)
| where SubscriptionId =~ PLS_Subscription
| where ResourceGroup =~ PLS_ResourceGroup
| where ResourceName =~ PLS_ResourceName
| where HttpMethod != "GET"
| project TIMESTAMP, OperationName, OperationId, CorrelationRequestId, ErrorCode, ErrorDetails, Region, Success, UserError
| sort by TIMESTAMP desc
| take 4 // Remove for all operations ran
```

**Params:** `{queryFrom}`, `{queryTo}`, `{PLS_Subscription}`, `{PLS_ResourceGroup}`, `{PLS_ResourceName}`, `{PLS_Key}`

**Signal filters seen in KQL:** `HttpMethod != "GET"`

---
