# NRP — BackupOperation: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T12:49:54.172Z.
> Total: 3 unique KQL queries across 3 panels (3 widget refs).

## Page inputs (URL params)


## Panels

### Backup Initiated Less than 20% of the total time.
Path: `Backup Initiated Less than 20% of the total time.`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Not scheduled backup | Table | https://nrp | mdsnrp | startTime, endTime |

### Backup Scheduled vs Failed Per Region
Path: `Backup Scheduled vs Failed Per Region`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Backup Scheduled | Table | https://nrp | mdsnrp | startTime, endTime, region |

### Top Error Code in Backup Operations
Path: `Top Error Code in Backup Operations`  ·  Queries: 1

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Backup Top Error | Table | https://nrp | mdsnrp | startTime, endTime |
