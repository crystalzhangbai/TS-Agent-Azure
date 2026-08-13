# Virtualization

> Source: **Azure Host - Azure VM** dashboard, chapter **Virtualization** (2 queries across 2 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## UnderhillEventTable

### Azure Host VM UnderhillEventTable

_Widget purpose:_ UnderhillEventTable

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Virtualization > UnderhillEventTable`

**Tables:** `UnderhillEventTable`
**Output columns:** `PreciseTimeStamp`, `Level`, `Message`

```kusto
UnderhillEventTable 
| where PreciseTimeStamp between(startTime..endTime) and NodeId == nodeId and Message contains containerId 
| project PreciseTimeStamp, Level, Message
| sort by PreciseTimeStamp asc
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`, `{containerId}`

---

## Virtualization Configuration

### Azure Host VM Virtualization Configuration

_Widget purpose:_ Virtualization Configuration

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`
Source panel: `Virtualization > Virtualization Configuration`

**Tables:** `HyperVVmConfigSnapshot`, `OsFileVersionTable`
**Aggregations:** `summarize by NodeId, ContainerId, VmProcessorCount, VmVersion, VmMemoryInMB, VmGeneration,` · `summarize by NodeId, HclFileName = FileName, HclFileVersion = FileVersion, HclFileTimeStam`
**Output columns:** `VmProcessorCount`, `VmVersion`, `VmMemoryInMB`, `VmGeneration`, `IsolationSetting`, `Hcl`, `HclFileName`, `HclFileVersion`, `HclFileTimeStamp`

```kusto
HyperVVmConfigSnapshot 
| where PreciseTimeStamp between(startTime..endTime) and NodeId == nodeId and ContainerId == containerId and SummaryType == "Configuration" 
| summarize by NodeId, ContainerId, VmProcessorCount, VmVersion, VmMemoryInMB, VmGeneration, HclEnabled, IsUnderhill, IsolationSetting 
| extend Hcl = case(HclEnabled =~ "true" and IsUnderhill =~ "true", "HCLv2 - OpenHCL/Underhill", HclEnabled =~ "true" and isempty(IsUnderhill), "HCLv1", "")
| project NodeId, ContainerId, VmProcessorCount, VmVersion, VmMemoryInMB, VmGeneration, Hcl, IsolationSetting 
| join kind = leftouter (
    OsFileVersionTable
    | where PreciseTimeStamp between((startTime-6h)..(endTime+6h)) and NodeId == nodeId and FileName =~ "vmfirmwarehcl.dll" 
    | summarize by NodeId, HclFileName = FileName, HclFileVersion = FileVersion, HclFileTimeStamp = FileTimeStamp
) on NodeId
| project VmProcessorCount, VmVersion, VmMemoryInMB, VmGeneration, IsolationSetting, Hcl, HclFileName, HclFileVersion, HclFileTimeStamp
```

**Params:** `{startTime}`, `{endTime}`, `{nodeId}`, `{containerId}`

---
