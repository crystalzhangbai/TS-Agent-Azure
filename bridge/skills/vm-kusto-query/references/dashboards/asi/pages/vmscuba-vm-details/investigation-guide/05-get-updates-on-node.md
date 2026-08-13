# Get Updates on Node

> Source: **VM Scuba - VM Details** dashboard, chapter **Get Updates on Node** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Get-NodeUpdates

_Widget purpose:_ Get Updates on Node

Cluster: `minekraft.westus.kusto.windows.net` · Database: `crawler5` · Type: `Table`
Source panel: `Get Updates on Node`

```kusto
fEntityChangeEvents
| where EntityId == nodeId
| where ImpactDuration > 0
| project Payload,StartTime,EntityId, ChangeType, ImpactDuration
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId}`

---
