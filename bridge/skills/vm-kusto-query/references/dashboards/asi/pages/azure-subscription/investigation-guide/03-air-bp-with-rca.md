# AIR-BP with RCA

> Source: **Azure Subscription Investigation Guide** dashboard, chapter **AIR-BP with RCA** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Disk AIR-BP

### Azure Host Subscription Disk AIR-BP

_Widget purpose:_ Disk AIR-BP

Cluster: `Vmainsight` · Database: `Air` · Type: `Table`
Source panel: `AIR-BP with RCA > Disk AIR-BP`

```kusto
AirDiskIOBlipEvents
| where EventTime  between (queryFrom .. queryTo) and SubscriptionId == subId
| where TotalIOsGt1s > 0
| project EventTime, RoleInstanceName, ContainerId, RCAType, RCALevel1, RCALevel2, RCALevel3, StorageCluster, BlobPath
```

**Params:** `{queryFrom}`, `{queryTo}`, `{subId}`

---
