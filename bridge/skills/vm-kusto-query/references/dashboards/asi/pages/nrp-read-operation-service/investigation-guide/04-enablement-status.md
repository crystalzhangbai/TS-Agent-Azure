# Enablement Status

> Source: **NRP - ReadOperationService** dashboard, chapter **Enablement Status** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### ReadOperationService OperationEnablement

_Widget purpose:_ Enablement Status

Cluster: `nrp.kusto.windows.net` · Database: `mdsnrp` · Type: `Table`
Source panel: `Enablement Status`

```kusto
QosEtwEvent
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where SourceAssemblyFileVersion has_cs "readoperations"
| extend SuccessRate=iff(ErrorCode != "InternalServerError", 1.0, 0.0)
| summarize OperationCount=count(), SubCount=dcount(SubscriptionId), SuccessRate=round(avg(SuccessRate) * 100.0, 2), Slices=make_set(SliceNum(SourceAssemblyFileVersion)) by Region, OperationName
| order by OperationCount desc
```

**Params:** `{queryFrom}`, `{queryTo}`

---
