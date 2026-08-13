# (top-level)

> Source: **Preview Dotnet Image Templates** dashboard, chapter **(top-level)** (4 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Preview Gen 2 Windows 2022 Dotnet Images

_Widget purpose:_ Preview Gen 2 Dotnet 8 Image templates 

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `Table`

```kusto
cluster('azcrp.kusto.windows.net').database('vmimagebuilder').UsageKpiEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where subscriptionID == "b80bcd5c-0c74-4b9e-b0c3-d67ce3803c5a" and resourceGroupName == "1PGalDotnetRG"
| where operationName contains "POST" and resourceName startswith "it-preview-2022-datacenter-azure-edition"
| summarize arg_max(PreciseTimeStamp, hypervgen, operationstatus, correlationID, latencyinms) by resourceName
| project Date=format_datetime(PreciseTimeStamp, 'yyyy-MM-dd'), Time=format_datetime(PreciseTimeStamp, 'HH:mm:ss'), ResourceName=resourceName, hypervgen, Status=operationstatus, BuildTimeMinutes=latencyinms/(60*1000), correlationID
| order by Date asc
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `subscriptionID == "b80bcd5c-0c74-4b9e-b0c3-d67ce3803c5a"` · `operationName contains "POST"`

---

### Dotnet 10 Preview Gen 2 Windows 2022 Dotnet Images

_Widget purpose:_ 2022 Gen 2 Preview Dotnet 10 Image templates

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `Table`

```kusto
UsageKpiEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where subscriptionID == "b80bcd5c-0c74-4b9e-b0c3-d67ce3803c5a" 
| where operationName contains "POST" and resourceName startswith "it-preview-2022" and resourceName contains "dotnet10"
| summarize arg_max(PreciseTimeStamp, hypervgen, operationstatus, correlationID, latencyinms) by resourceName
| project Date=format_datetime(PreciseTimeStamp, 'yyyy-MM-dd'), Time=format_datetime(PreciseTimeStamp, 'HH:mm:ss'), ResourceName=resourceName, hypervgen, Status=operationstatus, BuildTimeMinutes=latencyinms/(60*1000), correlationID
| order by Date asc
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `subscriptionID == "b80bcd5c-0c74-4b9e-b0c3-d67ce3803c5a"` · `operationName contains "POST"`

---

### Preview Gen 1 Windows 2022 Dotnet Images

_Widget purpose:_ Preview Gen 1 Dotnet 8 Image templates

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `Table`

```kusto
cluster('azcrp.kusto.windows.net').database('vmimagebuilder').UsageKpiEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where subscriptionID == "b80bcd5c-0c74-4b9e-b0c3-d67ce3803c5a" and resourceGroupName == "1PGalDotnetRG"
| where operationName contains "POST" and resourceName startswith "it-preview-2022-datacenter" and hypervgen == "V1"
| summarize arg_max(PreciseTimeStamp, hypervgen, operationstatus, correlationID, latencyinms) by resourceName
| project Date=format_datetime(PreciseTimeStamp, 'yyyy-MM-dd'), Time=format_datetime(PreciseTimeStamp, 'HH:mm:ss'), ResourceName=resourceName, hypervgen, Status=operationstatus, BuildTimeMinutes=latencyinms/(60*1000), correlationID
| order by Date asc
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `subscriptionID == "b80bcd5c-0c74-4b9e-b0c3-d67ce3803c5a"` · `operationName contains "POST"`

---

### Dotnet 10 Preview Gen 2 Windows 2025 Dotnet Images

_Widget purpose:_ 2025 Gen 2 Preview Dotnet 10 Image templates

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `Table`

```kusto
UsageKpiEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where subscriptionID == "b80bcd5c-0c74-4b9e-b0c3-d67ce3803c5a" 
| where operationName contains "POST" and resourceName startswith "it-preview-2025" and resourceName contains "dotnet10"
| summarize arg_max(PreciseTimeStamp, hypervgen, operationstatus, correlationID, latencyinms) by resourceName
| summarize arg_max(PreciseTimeStamp, *) by resourceName
| project Date=format_datetime(PreciseTimeStamp, 'yyyy-MM-dd'), Time=format_datetime(PreciseTimeStamp, 'HH:mm:ss'), ResourceName=resourceName, hypervgen, Status=operationstatus, BuildTimeMinutes=latencyinms/(60*1000), correlationID
| order by Date asc
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `subscriptionID == "b80bcd5c-0c74-4b9e-b0c3-d67ce3803c5a"` · `operationName contains "POST"`

---
