# Azure VM Image Builder — serviceBuild: KQL Query Library

> Auto-extracted from ASI on 2026-05-13T12:12:11.779Z.
> Total: 3 unique KQL queries across 1 panels (3 widget refs).

## Page inputs (URL params)


## Panels

### (top-level)
Path: `(top-level)`  ·  Queries: 3

| # | Name | Type | Cluster | Database | Params |
|---|------|------|---------|----------|--------|
| 1 | Retrieve Resource "serviceBuild" | ResourceGet | azcrp | vmimagebuilder | globalFrom, globalTo, local_serviceBuild |
| 2 | Service Build Saturation | Table | azcrp | vmimagebuilder | Build |
| 3 | Daily Build Success Rate | TimeSeries | azcrp | vmimagebuilder | queryFrom, queryTo, binTime, build |
