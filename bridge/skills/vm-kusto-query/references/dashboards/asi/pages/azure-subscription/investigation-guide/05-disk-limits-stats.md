# Disk Limits Stats

> Source: **Azure Subscription Investigation Guide** dashboard, chapter **Disk Limits Stats** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Disk Limits Stats

### Azure Host Subscription Disk Limits Stats

_Widget purpose:_ Disk Limits Stats

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Disk Limits Stats > Disk Limits Stats`

```kusto
DiskShoeboxCounterTable
| where subscriptionId == subId and PreciseTimeStamp between (startTime .. endTime) 
        and MDMCounterName contains "percentage"
| summarize TotalDisks = dcount(DiskArmId), Disks_doingMax = dcountif(DiskArmId, P100 >= 95 or P100 >= 95) by MDMCounterName
| sort by Disks_doingMax desc
```

**Params:** `{startTime}`, `{endTime}`, `{subId}`

---
