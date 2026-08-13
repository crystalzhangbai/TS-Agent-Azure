# Azure Serial Console — Serial Console Home: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T11:59:23.947Z.
> Total: 8 unique KQL queries across 8 panels (8 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Portal Image Tag  | Table | azlinux | SerialConsole | queryFrom, queryTo |

### Config Audits
Path: `Config Audits`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | WIP Trivy Config Audits | TimeSeries | https://azlinux | SerialConsole | queryFrom, queryTo |

### Current DRI
Path: `Current DRI`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Get Current On-Call | Single | icmcluster | DirectoryServicePROD | queryFrom, queryTo |

### Exposed Secrets
Path: `Exposed Secrets`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | WIP Trivy Exposed Secrets | TimeSeries | https://azlinux | SerialConsole | queryFrom, queryTo |

### Gateway Health Check Failure Percentage
Path: `Gateway Health Check Failure Percentage`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Gateway To RP Healthcheck | TimeSeries | azlinux | SerialConsole | queryFrom, queryTo |

### ICM Incidents
Path: `ICM Incidents`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Homepage - ICM incidents | Table | icmcluster | IcMDataWarehouse | - |

### Vulnerabilities > Vulnerabilities by Severity
Path: `Vulnerabilities > Vulnerabilities by Severity`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | WIP Trivy Vulernabilities by Severity | CategoryChart | https://azlinux | SerialConsole | queryFrom, queryTo |

### Vulnerabilities > Vulnerabilities by Time
Path: `Vulnerabilities > Vulnerabilities by Time`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | WIP Trivy Vulnerabilities | TimeSeries | https://azlinux | SerialConsole | queryFrom, queryTo |
