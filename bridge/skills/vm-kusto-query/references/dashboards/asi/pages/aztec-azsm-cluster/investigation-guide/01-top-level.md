# (top-level)

> Source: **Aztec AzSM Cluster Investigation Guide** dashboard, chapter **(top-level)** (3 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "AzSM Cluster"

Cluster: `accp.centralus` · Database: `AZSM` · Type: `ResourceGet` · Widget: `Container`

```kusto
LogAzSMSnapshot
| where Cluster == local_Cluster
| top 1 by PreciseTimeStamp desc
```

**Params:** `{local_Cluster}`

---

### AzSM Cluster Health

Cluster: `azurecm` · Database: `azurecm` · Type: `Timeline`

```kusto
AzSMApplicationHealthEvent
| where PreciseTimeStamp between(global_startTime..global_endTime)
| where Cluster == queryCluster and healthState != "Ok"
| extend Resource = applicationName
| project PreciseTimeStamp, Resource, healthState, description
| order by PreciseTimeStamp asc
| extend PrevTime = prev(PreciseTimeStamp)
| extend NextTime = next(PreciseTimeStamp)
| extend PrevApi = prev(Resource)
| extend NextApi = next(Resource)
| where 
isnull(PrevTime) or 
isnull(NextTime) or 
(Resource != PrevApi or Resource != NextApi) 
| extend StartTime = PreciseTimeStamp
| extend EndTime = next(PreciseTimeStamp)
| where NextApi == Resource
| project StartTime, EndTime, Resource, Content = Resource, healthState, description
| extend Health = case(
    healthState == "Warning", "Degraded",
    healthState == "Error", "Unhealthy",
    "")
| extend description = iif(isempty(description), "N/A", description)
| extend Content = strcat(healthState, " - ", Content)
| extend Tooltip = strcat("Description: ", description, "<br/>Start: ", StartTime, "<br/>EndTime: ", EndTime)
| extend EndTime = iif(isnull(EndTime), datetime_add('minute', 1, StartTime), EndTime)
```

**Params:** `{queryCluster}`

---

### AzSM Applications

_Widget purpose:_ Applications

Cluster: `accp.centralus` · Database: `AZSM` · Type: `Table`

```kusto
AzSMApplicationHealthEvent
| where PreciseTimeStamp between(global_startTime..global_endTime)
| where Cluster == queryCluster
| summarize arg_max(PreciseTimeStamp, *) by applicationName
| project tableApplicationName = applicationName, healthState
```

**Params:** `{queryCluster}`

---
