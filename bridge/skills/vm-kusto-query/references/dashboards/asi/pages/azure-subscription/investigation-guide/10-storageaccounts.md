# StorageAccounts

> Source: **Azure Subscription Investigation Guide** dashboard, chapter **StorageAccounts** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## StorageAccount Summary

### Azure Host Subscription StorageAccounts

_Widget purpose:_ StorageAccount Summary

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `StorageAccounts > StorageAccount Summary`

```kusto
OsXIOSurfaceCounterTable
| where PreciseTimeStamp between ((startTime - 2h) .. (endTime + 2h)) and ArmId contains subId
| parse BlobPath with * "/" StorageAccount "/" *
| summarize ActiveDisks = dcount(BlobPath) by StorageAccount, StorageTenant, Region
```

**Params:** `{startTime}`, `{endTime}`, `{subId}`

---
