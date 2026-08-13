# ASAP NVMe

> Source: **Azure Host - Azure VM** dashboard, chapter **ASAP NVMe** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Azure VM ASAP NVMe TDPR Query

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `ASAP NVMe`

**Output columns:** `PreciseTimeStamp`, `Source`, `EventId`, `EventName`, `Message`, `level`

```kusto
AsapOverlake2BootEvents(nodeId, startTime, endTime, containerId)
| where Source in ("UMED", "BlobcacheCounters", "BlobcacheHistogram")
| extend level = case(Level <= 2, "error", Level == 3, "warning", "info")
| project PreciseTimeStamp, Source, EventId, EventName, Message, level
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`, `{containerId}`

---
