# (top-level)

> Source: **Container** dashboard, chapter **(top-level)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Container"

Cluster: `mycroft.westcentralus.kusto.windows.net` · Database: `Mycroft` · Type: `ResourceGet` · Widget: `Container`

```kusto
MycroftContainerSnapshot
| where ContainerId == local_ContainerId
| top 1 by PreciseTimeStamp desc 
| extend JSON = parse_json(AdditionalContainerProperties)
| project-away TIMESTAMP, Pid, Tid, ActivityId, Version, SourceNamespace, SourceMoniker, SourceVersion, 
    __AuthType__, __AuthIdentity__
```

**Params:** `{local_ContainerId}`

---

### Container LifecycleState Timeline

_Widget purpose:_ Container Health

Cluster: `mycroft.westcentralus.kusto.windows.net` · Database: `Mycroft` · Type: `Timeline`

```kusto
cluster("mycroft.westcentralus").database("Mycroft").MycroftContainerHealthSnapshot
| where ContainerId == queryContainerId
| project LifecycleState, PreciseTimeStamp
| order by PreciseTimeStamp asc
| where 
    isnull(prev(PreciseTimeStamp)) or isnull(next(PreciseTimeStamp)) or 
    (LifecycleState != prev(LifecycleState) or LifecycleState != next(LifecycleState))
| extend StartTime = PreciseTimeStamp
| extend EndTime = next(PreciseTimeStamp)
| where next(LifecycleState) == LifecycleState or isempty(next(LifecycleState))
| extend EndTime = iif(isnull(EndTime), datetime_add('minute', 1, StartTime), EndTime)
| project StartTime, EndTime, Content = LifecycleState
```

**Params:** `{queryContainerId}`

---
