# TMMgmtContainerTraceEtwTable

> Source: **Aztec Containers Investigation Guide** dashboard, chapter **TMMgmtContainerTraceEtwTable** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Query TMMgmtContainerTraceEtwTable

_Widget purpose:_ TMMgmtContainerTraceEtwTable

Cluster: `azcore.centralus` · Database: `Fc` · Type: `Table`
Source panel: `TMMgmtContainerTraceEtwTable`

```kusto
TMMgmtContainerTraceEtwTable
| where PreciseTimeStamp between(queryFrom .. queryTo)
| where ContainerID  == queryContainerId
| project PreciseTimeStamp, Message
| order by PreciseTimeStamp asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryContainerId}`

---
