# AIR-J

> Source: **Azure Host — Azure Host Node** dashboard, chapter **AIR-J** (4 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## AIR-J Trend

### CPU Jitter comparison with baseline

_Widget purpose:_ Jitter Trend (1h granularity, 90d retention)

Cluster: `intmgmtshared.centralus.kusto.windows.net` · Database: `Public` · Type: `TimeSeries`
Source panel: `AIR-J > AIR-J Trend > AIR-J Trend > Jitter Trend (1h granularity, 90d retention)`

```kusto
View_HA_BaselineCompare_prod(nodeId, startTime-2h, endTime+2h) 
| project Timestamp, nodeCpuJitterScoreV1 = CpuJitterScoreV1, fleetwideCpuJitterScoreV1 = avg_CpuJitterScoreV1
| render timechart
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

### CPU Jitter (High granularity)

_Widget purpose:_ Jitter Trend (5sec granularity, 7d retention)

Cluster: `intmgmtshared.centralus.kusto.windows.net` · Database: `Fleet` · Type: `TimeSeries`
Source panel: `AIR-J > AIR-J Trend > AIR-J Trend > Jitter Trend (5sec granularity, 7d retention)`

```kusto
NodeCpuJitterBaseView_prod(startTime, endTime) 
| where  NodeId =~ nodeId 
| project Timestamp, nodeCpuJitterScoreV1 = CpuJitterScoreV1
| render timechart
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

## Utilization & Incidents

### AIR-J Incidents

_Widget purpose:_ AIR-J incidents

Cluster: `intmgmtshared.centralus.kusto.windows.net` · Database: `Public` · Type: `Table`
Source panel: `AIR-J > Utilization & Incidents > Utilization & Incidents > AIR-J incidents`

```kusto
View_HA_Incidents_prod(nodeId, startTime-2h, endTime+2h)
| sort by Timestamp asc
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---

### Node Utilization Landscape

_Widget purpose:_ Node Utilization

Cluster: `intmgmtshared.centralus.kusto.windows.net` · Database: `Public` · Type: `TimeSeries`
Source panel: `AIR-J > Utilization & Incidents > Utilization & Incidents > Node Utilization`

```kusto
View_HA_Landscape_prod(nodeId, startTime-2h, endTime+2h) 
| render timechart
```

**Params:** `{nodeId}`, `{startTime}`, `{endTime}`

---
