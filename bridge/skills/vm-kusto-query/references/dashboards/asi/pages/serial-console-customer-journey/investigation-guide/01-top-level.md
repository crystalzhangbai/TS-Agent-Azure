# (top-level)

> Source: **Customer Journey** dashboard, chapter **(top-level)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### uniquesubscriptions

_Widget purpose:_ Unique Subscriptions

Cluster: `https://azlinux.kusto.windows.net` · Database: `SerialConsole` · Type: `Single` · Widget: `Card`

```kusto
FrontEndQoSEvents
| distinct subscriptionID
| count
```

**Params:** `{queryFrom}`, `{queryTo}`

---

### icmcount

Cluster: `https://icmcluster.kusto.windows.net` · Database: `IcmDataWarehouse` · Type: `Table`

```kusto
Incidents
| where SourceCreateDate > ago(90d)
| where OwningTeamName contains "AzSerialConsole"
| where Status in ("ACTIVE")
| where isnull(ParentIncidentId)
| summarize count() by CorrelationId
| order by count_ desc
| limit 10
```

**Params:** `{queryFrom}`, `{queryTo}`

**Signal filters seen in KQL:** `OwningTeamName contains "AzSerialConsole"`

---
