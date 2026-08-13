# DiskTier Stats

> Source: **Azure Subscription Investigation Guide** dashboard, chapter **DiskTier Stats** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## TotalDisks by Tier

### Azure Host Subscription Disk Stats by Tier

_Widget purpose:_ TotalDisks by Tier

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `CategoryChart`
Source panel: `DiskTier Stats > TotalDisks by Tier`

```kusto
XdiskSvcEvent
| where PreciseTimeStamp between (queryFrom .. queryTo) and message contains subscriptionId
        and eventType == 411
| extend ConfigValue = parse_json(message)
| extend DiskTier = tostring(ConfigValue["x-ms-access-tier"]),
         IOPS = ConfigValue["x-ms-blob-iops-limit"],
         MBPS = ConfigValue["x-ms-blob-throughput-limit"]
| union (
    OsUltraSSDConfigTable
    | where PreciseTimeStamp between (queryFrom .. queryTo) and ArmId contains subscriptionId
    | extend ConfigName = BlobPath
    | extend DiskTier = case(DiskSkuType == 0 or isempty(DiskSkuType), "UltraDisk", DiskSkuType == 1, "PremiumV2", "UltraDisk")
)
| summarize TotalDisks = dcount(ConfigName) by DiskTier
| sort by TotalDisks desc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{subscriptionId}`

---
