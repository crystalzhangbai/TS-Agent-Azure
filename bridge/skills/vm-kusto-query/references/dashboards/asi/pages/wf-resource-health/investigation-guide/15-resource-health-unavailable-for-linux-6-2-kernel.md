# Resource Health Unavailable for Linux 6.2 Kernel

> Source: **EEE RDOS — WF Resource Health** dashboard, chapter **Resource Health Unavailable for Linux 6.2 Kernel** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### RH_Unavailable_Linux_6_2

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Resource Health Unavailable for Linux 6.2 Kernel`

```kusto
VmHealthRawStateEtwTable
| where PreciseTimeStamp >= query_BeginTime and PreciseTimeStamp <= query_EndTime
| where ContainerId == query_ContainerId and HasHyperVHandshakeCompleted == "false"
| summarize max(PreciseTimeStamp) by HasHyperVHandshakeCompleted, ContainerId
| join (cluster('Vmainsight').database('CAD').VMA_Daily
| where GA_GuestOSVersion has "6.2.0" and GA_GuestOSVersion has "Linux") on $left.ContainerId == $right.ContainerId
| summarize max(PreciseTimeStamp) by GA_GuestOSVersion, ContainerId, HasHyperVHandshakeCompleted
| order by max_PreciseTimeStamp desc 
| take 5
```

**Params:** `{query_BeginTime}`, `{query_EndTime}`, `{query_ContainerId}`

**Signal filters seen in KQL:** `GA_GuestOSVersion has "6.2.0"`

---
