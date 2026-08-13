# (top-level)

> Source: **NRP - ReadOperationService** dashboard, chapter **(top-level)** (3 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### ReadOperationService OperationCount

_Widget purpose:_ Operations Run on ReadOperationService

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `DataSummary`

```kusto
QosEtwEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where SourceAssemblyFileVersion has_cs "readoperations"
| summarize Value=tostring(count())
```

**Params:** `{queryFrom}`, `{queryTo}`

---

### ReadOperationService OperationReliability

_Widget purpose:_ ReadOperationService Reliability (Non 5xx Response Codes)

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `DataSummary`

```kusto
QosEtwEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where SourceAssemblyFileVersion has_cs "readoperations"
| where OperationName != "GetOperationResultOperation" // exclude misleading polling op
| extend reliability=iff(ErrorCode == "InternalServerError", 0.0, 1.0)
| summarize Value=strcat(round(avg(reliability) * 100, 2), "%")
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `OperationName != "GetOperationResultOperation"`

---

### ReadOperationService GatewayReliability

_Widget purpose:_ ReadOperationService Gateway-Level Reliability

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `DataSummary`

```kusto
GatewayServiceOperationEtwEvent
| where HttpMethod == "GET"
| where Message == "Request is valid for use with Operation Service."
| where PreciseTimeStamp  between(queryFrom..queryTo)
| where Region == "useast2euap"
| join kind=inner (GatewayServiceQosEtwEvent
    | where PreciseTimeStamp between(queryFrom..queryTo)
    | where Region == "useast2euap")
on OperationId
| extend SuccessRate=iff(ErrorDetails == "", 1.0, 0.0)
| summarize avg(SuccessRate)
| project Value=strcat(tostring(round(100.0 * avg_SuccessRate, 2)), "%")
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `HttpMethod == "GET"` · `Message == "Request is valid for use with Operation Service."` · `Region == "useast2euap"`

---
