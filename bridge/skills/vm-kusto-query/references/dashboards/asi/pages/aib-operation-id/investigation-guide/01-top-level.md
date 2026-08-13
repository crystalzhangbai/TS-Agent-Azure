# (top-level)

> Source: **operationID** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "operationID"

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `ResourceGet` · Widget: `Container`

```kusto
AsyncQoSEvents
| where operationID == local_operationID
| summarize min(PreciseTimeStamp) by correlationID, operationID, serviceBuild, RPSector, RPTenant, resourceGroupName, resourceName, subscriptionID
| take 1
```

**Params:** `{globalFrom}`, `{globalTo}`, `{local_operationID}`

---
