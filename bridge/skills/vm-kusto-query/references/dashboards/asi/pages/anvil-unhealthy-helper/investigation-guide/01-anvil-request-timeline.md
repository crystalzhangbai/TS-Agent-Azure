# Anvil Request Timeline

> Source: **Unhealthy Node Analysis - Unhealthy Helper** dashboard, chapter **Anvil Request Timeline** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Anvil Request Timeline

Cluster: `aplat.westcentralus.kusto.windows.net` · Database: `APlat` · Type: `Timeline`
Source panel: `Anvil Request Timeline`

```kusto
cluster('aplat.westcentralus.kusto.windows.net').database('APlat').AnvilRepairServiceRequestSnapshot
| where PreciseTimeStamp between (st ..et ) and Request contains nId
| project PreciseTimeStamp, RequestAuthor, RequestIdentifier, CorrelationIdentifier, Status, SubStatus, Request
| sort by PreciseTimeStamp asc
| summarize StartTime = min(PreciseTimeStamp), EndTime = max(PreciseTimeStamp), RequestAuthor = take_any(RequestAuthor), CorrelationIdentifier = take_any(CorrelationIdentifier), Request = take_any(Request) by RequestIdentifier, SubStatus
| project StartTime, EndTime, Content = SubStatus, GroupBy = CorrelationIdentifier, ToolTip = tostring(bag_pack_columns(RequestAuthor, CorrelationIdentifier, Request, RequestIdentifier))
```

**Params:** `{st}`, `{et}`, `{nId}`

---
