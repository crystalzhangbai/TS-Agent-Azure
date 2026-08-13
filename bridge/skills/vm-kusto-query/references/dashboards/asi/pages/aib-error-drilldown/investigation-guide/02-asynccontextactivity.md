# AsyncContextActivity

> Source: **Error Drilldown** dashboard, chapter **AsyncContextActivity** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## AsyncContextActivity

### AsyncContextActivity

Cluster: `azcrp.kusto.windows.net` · Database: `vmimagebuilder` · Type: `Table`
Source panel: `AsyncContextActivity > AsyncContextActivity`

```kusto
AsyncContextActivity
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where correlationID == local_correlationID
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{local_correlationID}`

---
