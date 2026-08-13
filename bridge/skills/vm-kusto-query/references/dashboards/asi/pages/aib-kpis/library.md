# Azure VM Image Builder — AIB KPIs: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T12:12:17.406Z.
> Total: 8 unique KQL queries across 8 panels (8 widget refs).

## Page inputs (URL params)


## Panels

### AsyncQos
Path: `AsyncQos`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Improved AsyncQoS | Table | azcrp | vmimagebuilder | queryFrom, queryTo |

### Daily Builds - {{ binTime }}
Path: `Daily Builds - {{ binTime }}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Daily Build Success Rate | TimeSeries | azcrp | vmimagebuilder | queryFrom, queryTo, binTime, build |

### FrontEndQos
Path: `FrontEndQos`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | AIB FrontEndQOS Failures | Table | azcrp | vmimagebuilder | queryFrom, queryTo |

### Latest Data
Path: `Latest Data`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Latest Refresh DateTime | Single | azcrp | vmimagebuilder | - |

### Low KPIs ( < 99 )
Path: `Low KPIs ( < 99 )`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Operation Warnings | MultiRow | azcrp | vmimagebuilder | queryFrom, queryTo |

### Region Hit Count
Path: `Region Hit Count`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Region AsyncQoSEvent Count | CategoryChart | azcrp | vmimagebuilder | queryFrom, queryTo |

### Success Rate
Path: `Success Rate`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Overall Success Rate | DataSummary | azcrp | vmimagebuilder | queryFrom, queryTo |

### Success Rate by Request Type - {{binTime}}
Path: `Success Rate by Request Type - {{binTime}}`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Daily Build Success by Operation Type | TimeSeries | azcrp | vmimagebuilder | queryFrom, queryTo, binTime |
