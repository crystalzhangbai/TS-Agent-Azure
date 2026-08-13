# CommonWebOperationStart

> Source: **Aztec RelatedActivityId Investigation Guide** dashboard, chapter **CommonWebOperationStart** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## CommonWebOperationStart

### RelatedActivityId CommonWebOperationStart

_Widget purpose:_ CommonWebOperationStart

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Table`
Source panel: `CommonWebOperationStart > CommonWebOperationStart`

```kusto
let queryFrom = datetime_add("day", -1, queryOperationTime);
let queryTo = datetime_add("day", 1, queryOperationTime);
CommonWebOperationStart
| where PreciseTimeStamp between (queryFrom..queryTo)
| where RelatedActivityId =~ local_RelatedActivityId
| project PreciseTimeStamp, ActivityId, HttpMethod, Url, ProcessName, ConfigurationType
| order by PreciseTimeStamp asc
```

**Params:** `{queryOperationTime}`, `{local_RelatedActivityId}`

---
