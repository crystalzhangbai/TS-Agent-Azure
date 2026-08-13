# File Versions

> Source: **Azure Host Compare Investigation Guide** dashboard, chapter **File Versions** (2 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## FileVersions

### Azure Host FileVersion Compare

_Widget purpose:_ FileVersions

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `SharedWorkspace` · Type: `Table`
Source panel: `File Versions > FileVersions`

```kusto
GetFileVersion(nodeId1, queryFrom, queryTo)
| join kind=fullouter(
    GetFileVersion(nodeId2, Time2From, Time2To)
) on FileName
| project FileName, Node1_version = FileVersion, Node2_version = FileVersion1
| extend level = case(Node1_version != Node2_version, "warning", "info")
| sort by level desc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId1}`, `{Time2From}`, `{Time2To}`, `{nodeId2}`

---

## PF Services

### Azure Host PF Services Compare

_Widget purpose:_ PF Services

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `AutopilotDeployment` · Type: `Table`
Source panel: `File Versions > PF Services`

```kusto
ServiceManagerInstrumentation
| where PreciseTimeStamp between ((queryFrom - 2h) .. (queryTo + 2h)) and NodeId == nodeId1
| summarize arg_max(PreciseTimeStamp, *) by ServiceName
| project ServiceName, ServiceVersion
| join kind=inner(
    ServiceManagerInstrumentation
    | where PreciseTimeStamp between ((Time2From - 2h) .. (Time2To + 2h)) and NodeId == nodeId2
    | summarize arg_max(PreciseTimeStamp, *) by ServiceName
    | project ServiceName, ServiceVersion
) on ServiceName
| project ServiceName, Node1_version = ServiceVersion, Node2_version = ServiceVersion1
| extend level = case(Node1_version != Node2_version, "warning", "info")
| sort by ServiceName desc
| sort by level desc
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeId1}`, `{Time2From}`, `{Time2To}`, `{nodeId2}`

---
