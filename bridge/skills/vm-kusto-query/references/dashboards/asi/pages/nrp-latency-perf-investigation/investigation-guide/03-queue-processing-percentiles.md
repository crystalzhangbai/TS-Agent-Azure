# Queue Processing Percentiles

> Source: **NRP - Latency and Performance Investigation Dashboard** dashboard, chapter **Queue Processing Percentiles** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Queue Processing Percentiles

Cluster: `https://nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Queue Processing Percentiles`

```kusto
FrontendOperationEtwEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where Region == region
| where SubscriptionId == subscriptionId
| project PreciseTimeStamp, Message, OperationId, OperationName, EventCode, SourceAssemblyFileVersion, RoleInstance
| parse Message with "Dequeue job id "id" of type "jobName" for execution in queue "queueId" duration in queue: "duration
| summarize percentiles(toint(duration), 50, 75, 95, 99) by queueId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{region}`, `{subscriptionId}`

---
