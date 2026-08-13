# Registry Keys

> Source: **Azure Host Compare Investigation Guide** dashboard, chapter **Registry Keys** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Registry Keys in the Nodes (different is highlighted)

### Azure Host Node Compare Registry Keys

_Widget purpose:_ Registry Keys in the Nodes (different is highlighted)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Registry Keys > Registry Keys in the Nodes (different is highlighted)`

```kusto
OsConfigTable
| where PreciseTimeStamp between ((queryFrom - 7h) .. queryTo) and NodeId == nodeId1 and ConfigType == "registry"
| summarize arg_max(PreciseTimeStamp, *) by ConfigName, ConfigPath
| project Component, ConfigName = strcat(ConfigPath, "\\", ConfigName), ConfigValue
| join kind=fullouter(
    OsConfigTable
    | where PreciseTimeStamp between ((Time2From - 7h) .. Time2To) and NodeId == nodeId2 and ConfigType == "registry"
    | summarize arg_max(PreciseTimeStamp, *) by ConfigName, ConfigPath
    | project Component, ConfigName = strcat(ConfigPath, "\\", ConfigName), ConfigValue
) on ConfigName
//| where ConfigValue != ConfigValue1
| where ConfigName !contains "StartTime" and ConfigName !contains "DatapathExecutionSummary"
| project Component = case(isempty(Component), Component1, Component), ConfigName = case(isempty(ConfigName), ConfigName1, ConfigName ) , ConfigValue, ConfigValue1
| extend level = case(ConfigValue != ConfigValue1, "warning", "info")
| sort by level desc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId1}`, `{Time2From}`, `{Time2To}`, `{nodeId2}`

---
