# Guest Agent Generic Logs

> Source: **Aztec Containers Investigation Guide** dashboard, chapter **Guest Agent Generic Logs** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Guest Agent Generic Logs

### Container Guest Agent Generic Logs

_Widget purpose:_ Guest Agent Generic Logs

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Guest Agent Generic Logs > Guest Agent Generic Logs`

```kusto
GuestAgentGenericLogs
| where PreciseTimeStamp between(global_startTime..global_endTime)
| where ContainerId == queryContainerId
| project 
    PreciseTimeStamp, Level, GAVersion, EventName, CapabilityUsed, Context1, Context2, Context3
| order by PreciseTimeStamp asc
```

**Params:** `{queryContainerId}`

---
