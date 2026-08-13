# ApiUnexpectedFailures IcMs

> Source: **Aztec — Tenant** dashboard, chapter **ApiUnexpectedFailures IcMs** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## ApiUnexpectedFailures IcMs

### Query ApiUnexpectedFailures in IcMDataWarehouse

_Widget purpose:_ ApiUnexpectedFailures in IcMDataWarehouse

Cluster: `icmcluster.kusto.windows.net` · Database: `IcMDataWarehouse` · Type: `Table`
Source panel: `ApiUnexpectedFailures IcMs > ApiUnexpectedFailures IcMs > ApiUnexpectedFailures in IcMDataWarehouse`

```kusto
IncidentsSnapshotV2
| where ImpactStartDate  between (datetime_add('day',-1, queryFrom) .. datetime_add('day',1, queryTo))
| where MonitorId startswith "ApiUnexpectedFailures_ApiName"
| where OccurringEnvironment == "PROD"
| where OccurringDatacenter =~ queryRegionName
| summarize arg_max(Lens_IngestionTime, Title, Severity, Status,ImpactStartDate, MitigateDate) by IncidentId
| parse Title with * "ApiName: " apiName ". Location:" location ". ResultCode: " resultCode ". " *
| order by IncidentId asc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{queryRegionName}`

**Signal filters seen in KQL:** `MonitorId startswith "ApiUnexpectedFailures_ApiName"` · `OccurringEnvironment == "PROD"`

---
