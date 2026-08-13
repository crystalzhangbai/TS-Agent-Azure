# TMMgmtLeaseManagerEtwTable

> Source: **Aztec Containers Investigation Guide** dashboard, chapter **TMMgmtLeaseManagerEtwTable** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Query TMMgmtLeaseManagerEtwTable

_Widget purpose:_ TMMgmtLeaseManagerEtwTable

Cluster: `azcsupfollower` · Database: `AzureCM` · Type: `Table`
Source panel: `TMMgmtLeaseManagerEtwTable`

```kusto
TMMgmtLeaseManagerEtwTable
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where ContainerId == queryContainerId
| project PreciseTimeStamp, LeaseAction, Message
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`

---
