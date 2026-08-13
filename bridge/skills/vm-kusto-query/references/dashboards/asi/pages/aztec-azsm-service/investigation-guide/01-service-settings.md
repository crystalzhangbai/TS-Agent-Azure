# Service Settings

> Source: **Aztec AzSM Service Investigation Guide** dashboard, chapter **Service Settings** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### AzSM Service Settings

_Widget purpose:_ Service Settings

Cluster: `accp.centralus` · Database: `AZSM` · Type: `Table`
Source panel: `Service Settings`

```kusto
AzSMSettingsSnapshot
| where PreciseTimeStamp > ago(6h)
| where Cluster == queryCluster and serviceName == queryServiceName
| summarize arg_max(PreciseTimeStamp, *) by configSection, settingName
| project configSection, settingName, settingValue
| order by configSection asc, settingName asc
```

**Params:** `{queryCluster}`, `{queryServiceName}`

---
