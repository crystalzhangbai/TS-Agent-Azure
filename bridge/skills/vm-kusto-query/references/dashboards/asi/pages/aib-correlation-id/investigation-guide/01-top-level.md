# (top-level)

> Source: **correlationID** dashboard, chapter **(top-level)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "correlationID"

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `ResourceGet` · Widget: `CompoundWidgetContainer`

```kusto
AsyncContextActivity
| where correlationID == local_correlationID
| summarize min(PreciseTimeStamp) by correlationID, operationID, serviceBuild, RPSector, RPTenant, resourceGroupName, resourceName, subscriptionID
| take 1
```

**Params:** `{local_correlationID}`, `{globalFrom}`, `{globalTo}`

---

### AsyncContextActivity by CorrelationID

_Widget purpose:_ AsyncContextActivity errors

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `Table`

```kusto
let correlationIdInput = correlationID;
let levelInput = level;
AsyncContextActivity
| where correlationID == correlationIdInput
| where level == levelInput
| project PreciseTimeStamp,operationID, serviceBuild, level, fileName, lineNumber, msg
```

**Params:** `{correlationID}`, `{level}`

---
