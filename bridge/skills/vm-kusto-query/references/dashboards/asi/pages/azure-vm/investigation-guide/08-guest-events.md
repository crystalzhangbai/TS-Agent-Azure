# Guest Events

> Source: **Azure Host - Azure VM** dashboard, chapter **Guest Events** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Azure Host VM SC Events

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Sc` · Type: `Table`
Source panel: `Guest Events`

**Tables:** `SCSystemWindowsEventTable`, `WorkloadResult`
**Output columns:** `todatetime(TimeCreated)`, `tostring(EventId)`, `ProviderName`, `Description`, `level`

```kusto
SCSystemWindowsEventTable
| where PreciseTimeStamp between (startTime .. endTime) and RoleInstance == containerId
| project todatetime(TimeCreated), tostring(EventId), ProviderName, Description, level = toint(Level)
| union (
    WorkloadResult
    | where PreciseTimeStamp between (startTime .. endTime) and RoleInstance == containerId
    | project TimeCreated = todatetime(EndTime), EventId = tostring(1), ProviderName = TestType, Description = Summary, level = toint(4)
)
| extend level = case(level <= 2, "error", level == 3, "warning", "info")
| sort by TimeCreated asc
```

**Params:** `{startTime}`, `{endTime}`, `{containerId}`

---
