# Azure VM Image Builder — correlationID: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T12:12:12.041Z.
> Total: 2 unique KQL queries across 1 panels (3 widget refs).

## Page inputs (URL params)

- `correlationID` — (no description)

## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 2

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "correlationID" | ResourceGet | azcrp | vmimagebuilder | local_correlationID, globalFrom, globalTo |
| 2 | AsyncContextActivity by CorrelationID | Table | azcrp | vmimagebuilder | correlationID, level |
