# CommonWebOperationEnd

> Source: **Aztec RelatedActivityId Investigation Guide** dashboard, chapter **CommonWebOperationEnd** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## CommonWebOperationEnd

### RelatedActivityId CommonWebOperationEnd

_Widget purpose:_ CommonWebOperationEnd

Cluster: `AzureCM` · Database: `AzureCM` · Type: `Table`
Source panel: `CommonWebOperationEnd > CommonWebOperationEnd`

```kusto
let queryFrom = datetime_add("day", -1, queryOperationTime);
let queryTo = datetime_add("day", 1, queryOperationTime);
CommonWebOperationEnd
| where PreciseTimeStamp between (queryFrom..queryTo)
| where RelatedActivityId =~ local_RelatedActivityId
| project PreciseTimeStamp,ActivityId,HttpMethod,Url,HttpStatusCode,Result,Exception
| order by PreciseTimeStamp desc
```

**Params:** `{local_RelatedActivityId}`, `{queryOperationTime}`

---
