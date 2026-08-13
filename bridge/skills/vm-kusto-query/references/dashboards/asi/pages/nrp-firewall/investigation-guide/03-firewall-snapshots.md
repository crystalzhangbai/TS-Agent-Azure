# Firewall Snapshots

> Source: **NRP - Firewall** dashboard, chapter **Firewall Snapshots** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Az firewall snapshots

_Widget purpose:_ Firewall Snapshots

Cluster: `argwus2nrpone.westus2` · Database: `AzureResourceGraph` · Type: `Table`
Source panel: `Firewall Snapshots`

```kusto
cluster("argwus2nrpone.westus2.kusto.windows.net").database("AzureResourceGraph").Resources
| where timestamp between (qFrom .. qTo)
| where name =~ qName and type == 'microsoft.network/azurefirewalls'
| where subscriptionId =~ qSub and resourceGroup =~ qRG
| order by timestamp asc
| extend prevProps = prev(properties)
| where tostring(prevProps) != tostring(properties)
```

**Params:** `{qFrom}`, `{qTo}`, `{qName}`, `{qRG}`, `{qSub}`

---
