# (top-level)

> Source: **Execution Graph** dashboard, chapter **(top-level)** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Execution Graph"

Cluster: `https://egpublic.westus.kusto.windows.net` · Database: `eg` · Type: `ResourceGet` · Widget: `Container`

```kusto
AscSearchExecutionGraphV2(local_SubscriptionId, globalFrom, globalTo)
| where EgId == local_EgId
| take 1
```

**Params:** `{globalFrom}`, `{globalTo}`, `{local_EgId}`, `{local_SubscriptionId}`

---
