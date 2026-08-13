# LEGO EKG & Vitals

> Source: **Aztec — Clusters** dashboard, chapter **LEGO EKG & Vitals** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## EKG & Vitals

### LEGO - EKG & Vitals

_Widget purpose:_ EKG & Vitals

Cluster: `silverstonepcs.eastus.kusto.windows.net` · Database: `silverstonepcsdb` · Type: `TimeSeries`
Source panel: `LEGO EKG & Vitals > EKG & Vitals`

```kusto
let startTimeStr="2020/09/14 10:00:00";
let endTimeStr = "2020/09/15 02:00:00";
let baseStartTimeStr="2020/09/13 00:00:00";
let baseEndTimeStr = "2020/09/13 12:00:00";
let functionTable = datatable(functionname:string)
[
    'fFabricatorUptimeStatus',
    'fDataCenterManagerHealthStatus',
    'fFcClusterNodeStatus',
    'fFcClusterVmHealth',
    'fFcClusterTorStatus',
    'fSlbv1ManagerRoleStatus',
    'fXStoreStatus',
    'fPfDMHealth'
];
fStateEngineV1(functionTable, queryRegion, queryCluster, queryFrom, queryTo, queryFrom, queryTo)
| extend Resource = strcat("ResourceType:", ResourceType, ", Resource:", Resource, ", Feature:", Feature)
| project SnapshotTime, Resource, HealthIndicator
| order by SnapshotTime asc
```

**Params:** `{queryRegion}`, `{queryCluster}`, `{queryFrom}`, `{queryTo}`

---
