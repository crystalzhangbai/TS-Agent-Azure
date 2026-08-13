# (top-level)

> Source: **subscriptionID** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "subscriptionID"

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `ResourceGet` · Widget: `Container`

```kusto
AsyncContextActivity
| where subscriptionID == local_subscriptionID
| distinct subscriptionID, resourceGroupName, resourceName
```

**Params:** `{globalFrom}`, `{globalTo}`, `{local_subscriptionID}`

---
