# Traces

> Source: **ARM Activity Ids Investigation Guide** dashboard, chapter **Traces** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Activity Id Traces

_Widget purpose:_ Traces

Cluster: `armprodgbl.eastus` · Database: `ARMProd` · Type: `Table`
Source panel: `Traces`

```kusto
macro-expand isfuzzy=true ARMProdEG as X
(
    union X.database('Traces').Traces //, X.database('Jobs').JobTraces
    | where PreciseTimeStamp between (queryFrom .. queryTo)
    | where isnotempty(queryActivityId) and ActivityId == queryActivityId
    | extend level = iif(isnotempty(exception) and exception != "<null>", "Error", "")
    | project TIMESTAMP, operationName, message, exception, level
)
| order by TIMESTAMP asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryActivityId}`

---
