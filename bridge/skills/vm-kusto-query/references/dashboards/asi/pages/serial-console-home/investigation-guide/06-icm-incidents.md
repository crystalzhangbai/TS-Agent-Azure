# ICM Incidents

> Source: **Serial Console Home** dashboard, chapter **ICM Incidents** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Homepage - ICM incidents

_Widget purpose:_ ICM Incidents

Cluster: `icmcluster` · Database: `IcMDataWarehouse` · Type: `Table`
Source panel: `ICM Incidents`

```kusto
let tenantName="AzTux";
let owningTeam="AZLINUX\\AzSerialConsole";
database("IcMDataWarehouse").Incidents
| where Lens_IngestionTime > ago(3d) and OwningTeamName == owningTeam
| summarize argmax(Lens_IngestionTime, *) by IncidentId
| where max_Lens_IngestionTime_Severity <= 4
| project IncidentId, CreateDate=max_Lens_IngestionTime_CreateDate, MitigatedDate=max_Lens_IngestionTime_MitigateDate, Title=max_Lens_IngestionTime_Title, Severity=max_Lens_IngestionTime_Severity, OwningTeam=max_Lens_IngestionTime_OwningTeamName, Status=max_Lens_IngestionTime_Status
| where CreateDate > ago(60d)
| where Status != "RESOLVED"
| order by Status asc, CreateDate desc
```

**Signal filters seen in KQL:** `Status != "RESOLVED"`

---
