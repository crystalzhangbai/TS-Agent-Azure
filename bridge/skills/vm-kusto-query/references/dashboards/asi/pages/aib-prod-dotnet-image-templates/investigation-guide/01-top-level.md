# (top-level)

> Source: **Prod Dotnet Image Templates** dashboard, chapter **(top-level)** (6 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Gen2 2022 WS image templates

_Widget purpose:_ Prod Win 2022 Gen 2 Dotnet 6 & 8 Image templates 

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `Table`

```kusto
UsageKpiEvent
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where subscriptionID == "b80bcd5c-0c74-4b9e-b0c3-d67ce3803c5a" and resourceGroupName == "1PGalDotnetRG"
| where  operationName == "PostRunTemplateHandler.POST"
| where resourceName startswith "image-template-2022-datacenter-azure-edition" and resourceName !contains "dotnet"
| summarize arg_max(PreciseTimeStamp, hypervgen, operationstatus, correlationID, latencyinms) by resourceName
| project Date=format_datetime(PreciseTimeStamp, 'yyyy-MM-dd'), Time=format_datetime(PreciseTimeStamp, 'HH:mm:ss'), ResourceName=resourceName, hypervgen, Status=operationstatus, correlationID, BuildTimeMinutes=latencyinms/(60*1000)
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `subscriptionID == "b80bcd5c-0c74-4b9e-b0c3-d67ce3803c5a"` · `operationName == "PostRunTemplateHandler.POST"` · `resourceName startswith "image-template-2022-datacenter-azure-edition"`

---

### Prod Gen 2 Windows 2022 Dotnet 8 Images

_Widget purpose:_ Prod Win 2022 Gen 2 Dotnet 8 Image templates 

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `Table`

```kusto
cluster('azcrp.kusto.windows.net').database('vmimagebuilder').UsageKpiEvent
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where subscriptionID == "b80bcd5c-0c74-4b9e-b0c3-d67ce3803c5a" and resourceGroupName == "1PGalDotnetRG"
| where  operationName == "PostRunTemplateHandler.POST"
| where hypervgen == "V2"
| where resourceName contains "2022" and resourceName contains "dotnet8" and resourceName !contains "preview"
| summarize arg_max(PreciseTimeStamp, hypervgen, operationstatus, correlationID, latencyinms) by resourceName
| project Date=format_datetime(PreciseTimeStamp, 'yyyy-MM-dd'), Time=format_datetime(PreciseTimeStamp, 'HH:mm:ss'), ResourceName=resourceName, hypervgen, Status=operationstatus, BuildTimeMinutes=latencyinms/(60*1000),correlationID
| order by Date asc
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `subscriptionID == "b80bcd5c-0c74-4b9e-b0c3-d67ce3803c5a"` · `operationName == "PostRunTemplateHandler.POST"` · `hypervgen == "V2"` · `resourceName contains "2022"`

---

### Dotnet 10 Gen 2 Windows 2022 Dotnet Images

_Widget purpose:_ Prod Win 2022 Gen 2 Dotnet 10 Image templates

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `Table`

```kusto
UsageKpiEvent
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where subscriptionID == "b80bcd5c-0c74-4b9e-b0c3-d67ce3803c5a" and resourceGroupName == "1PGalDotnetRG"
| where  operationName == "PostRunTemplateHandler.POST"
| where hypervgen == "V2" and resourceName contains "2022" and resourceName !contains "preview" and resourceName contains "dotnet10"
| summarize arg_max(PreciseTimeStamp, hypervgen, operationstatus, correlationID, latencyinms) by resourceName
| project Date=format_datetime(PreciseTimeStamp, 'yyyy-MM-dd'), Time=format_datetime(PreciseTimeStamp, 'HH:mm:ss'), ResourceName=resourceName, hypervgen, Status=operationstatus, BuildTimeMinutes=latencyinms/(60*1000),correlationID
| order by Date asc
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `subscriptionID == "b80bcd5c-0c74-4b9e-b0c3-d67ce3803c5a"` · `operationName == "PostRunTemplateHandler.POST"` · `hypervgen == "V2"`

---

### Dotnet 10 Gen 2 Windows 2025 Dotnet Images

_Widget purpose:_ Prod Win 2025 Gen 2 Dotnet 10 Image templates

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `Table`

```kusto
UsageKpiEvent
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where subscriptionID == "b80bcd5c-0c74-4b9e-b0c3-d67ce3803c5a" and resourceGroupName == "1PGalDotnetRG"
| where  operationName == "PostRunTemplateHandler.POST"
| where hypervgen == "V2" and resourceName contains "2025" and resourceName !contains "preview" and resourceName contains "dotnet10"
| summarize arg_max(PreciseTimeStamp, hypervgen, operationstatus, correlationID, latencyinms) by resourceName
| project Date=format_datetime(PreciseTimeStamp, 'yyyy-MM-dd'), Time=format_datetime(PreciseTimeStamp, 'HH:mm:ss'), ResourceName=resourceName, hypervgen, Status=operationstatus, BuildTimeMinutes=latencyinms/(60*1000),correlationID
| order by Date asc
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `subscriptionID == "b80bcd5c-0c74-4b9e-b0c3-d67ce3803c5a"` · `operationName == "PostRunTemplateHandler.POST"` · `hypervgen == "V2"`

---

### Prod Gen 1 Windows 2022 Dotnet 8 Images

_Widget purpose:_ Prod Win 2022 Gen 1 Dotnet 8 Image templates

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `Table`

```kusto
cluster('azcrp.kusto.windows.net').database('vmimagebuilder').UsageKpiEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where subscriptionID == "b80bcd5c-0c74-4b9e-b0c3-d67ce3803c5a" and resourceGroupName == "1PGalDotnetRG"
| where  operationName == "PostRunTemplateHandler.POST"
| where resourceName contains "2022-datacenter" and resourceName !contains "preview" and resourceName !contains "azure"  and resourceName contains "dotnet8"
| summarize arg_max(PreciseTimeStamp, *) by resourceName
| project Date=format_datetime(PreciseTimeStamp, 'yyyy-MM-dd'), Time=format_datetime(PreciseTimeStamp, 'HH:mm:ss'), ResourceName=resourceName, hypervgen, Status=operationstatus, BuildTimeMinutes=latencyinms/(60*1000), correlationID
| order by Date asc
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `subscriptionID == "b80bcd5c-0c74-4b9e-b0c3-d67ce3803c5a"` · `operationName == "PostRunTemplateHandler.POST"` · `resourceName contains "2022-datacenter"`

---

### Dotnet 10 Gen 1 Windows 2022 Dotnet Images

_Widget purpose:_ Prod Win 2022 Gen 1 Dotnet 10 Image templates

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `Table`

```kusto
UsageKpiEvent
| where PreciseTimeStamp  between (queryFrom .. queryTo)
| where subscriptionID == "b80bcd5c-0c74-4b9e-b0c3-d67ce3803c5a" and resourceGroupName == "1PGalDotnetRG"
| where  operationName == "PostRunTemplateHandler.POST"
| where hypervgen == "V1" and resourceName contains "2022" and resourceName !contains "preview" and resourceName contains "dotnet10"
| summarize arg_max(PreciseTimeStamp, hypervgen, operationstatus, correlationID, latencyinms) by resourceName
| project Date=format_datetime(PreciseTimeStamp, 'yyyy-MM-dd'), Time=format_datetime(PreciseTimeStamp, 'HH:mm:ss'), ResourceName=resourceName, hypervgen, Status=operationstatus, BuildTimeMinutes=latencyinms/(60*1000),correlationID
| order by Date asc
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `subscriptionID == "b80bcd5c-0c74-4b9e-b0c3-d67ce3803c5a"` · `operationName == "PostRunTemplateHandler.POST"` · `hypervgen == "V1"`

---
