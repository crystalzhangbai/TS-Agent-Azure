# (top-level)

> Source: **Aztec Nodes Investigation Guide** dashboard, chapter **(top-level)** (8 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Nodes"

Cluster: `azurecm` · Database: `AzureCM` · Type: `ResourceGet` · Widget: `Container`

```kusto
LogNodeSnapshot
| where nodeId == local_nodeId
| top 1 by PreciseTimeStamp desc
```

**Params:** `{local_nodeId}`, `{globalFrom}`, `{globalTo}`

---

### Node Flags

Cluster: `azurecm` · Database: `AzureCM` · Type: `FeatureList` · Widget: `Container`

```kusto
LogNodeSnapshot
| where nodeId == queryNodeId
| top 1 by PreciseTimeStamp desc
| project isIsolated, isOffline, isProtected, isMaintenanceOs, isPeriodic, IsProcessorSpeculationControlEnabled
| project features = pack(
    "Isolated", isIsolated, 
    "Offline", isOffline, 
    "Protected", isProtected, 
    "MaintenanceOs", isMaintenanceOs,
    "Periodic", isPeriodic,
    "ProcessorSpeculationControlEnabled", IsProcessorSpeculationControlEnabled
    )
| mv-expand bagexpansion=array features
| project FeatureName = tostring(features[0]), Enabled = tobool(features[1])
```

**Params:** `{queryNodeId}`

---

### Node Hosting Environment

_Widget purpose:_ Hosting Environment

Cluster: `azurecm` · Database: `azurecm` · Type: `Table`

```kusto
LogNodeSnapshot
| where PreciseTimeStamp > ago(28d)
| where nodeId == queryNodeId
| top 1 by PreciseTimeStamp desc
| project hostingEnvironment
| extend json = parse_json(hostingEnvironment)
| mv-expand bagexpansion=array json
| project Name = tostring(json[0]), Value = tostring(json[1])
```

**Params:** `{queryNodeId}`

---

### Node State

_Widget purpose:_ Node State and Health

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`

```kusto
LogNodeSnapshot
| where PreciseTimeStamp between(global_startTime..global_endTime)
| where nodeId == queryNodeId 
| extend Resource = nodeState
| project PreciseTimeStamp, Resource
| order by PreciseTimeStamp asc
| extend PrevTime = prev(PreciseTimeStamp)
| extend NextTime = next(PreciseTimeStamp)
| extend PrevResource = prev(Resource)
| extend NextResource = next(Resource)
| where 
isnull(PrevTime) or 
isnull(NextTime) or 
(Resource != PrevResource or Resource != NextResource) 
| extend StartTime = PreciseTimeStamp
| extend EndTime = next(PreciseTimeStamp)
| where NextResource == Resource
| project StartTime, EndTime, Content = Resource
| extend EndTime = iif(isnull(EndTime), datetime_add('minute', 1, StartTime), EndTime)
```

**Params:** `{queryNodeId}`

---

### Node Availability State

_Widget purpose:_ Node State and Health

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`

```kusto
LogNodeSnapshot
| where PreciseTimeStamp between(global_startTime..global_endTime)
| where nodeId == queryNodeId 
| extend Resource = nodeAvailabilityState
| project PreciseTimeStamp, Resource, faultInfo
| order by PreciseTimeStamp asc
| extend PrevTime = prev(PreciseTimeStamp)
| extend NextTime = next(PreciseTimeStamp)
| extend PrevResource = prev(Resource)
| extend NextResource = next(Resource)
| where 
isnull(PrevTime) or 
isnull(NextTime) or 
(Resource != PrevResource or Resource != NextResource) 
| extend StartTime = PreciseTimeStamp
| extend EndTime = next(PreciseTimeStamp)
| where NextResource == Resource
| extend Tooltip = faultInfo
| extend Health = iif(Resource == "Available", "Healthy", "Unhealthy")
| project StartTime, EndTime, Content = Resource, Tooltip, Health
| extend EndTime = iif(isnull(EndTime), datetime_add('minute', 1, StartTime), EndTime)
```

**Params:** `{queryNodeId}`

---

### Node OS Image

_Widget purpose:_ Node State and Health

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`

```kusto
LogNodeSnapshot
| where PreciseTimeStamp between(global_startTime..global_endTime)
| where nodeId == queryNodeId 
| extend hostEnv = parse_json(hostingEnvironment)
| extend osBaseImage = tostring(hostEnv.OSBaseImageName)
| extend osTargetImage = tostring(hostEnv.OSTargetImageName)
//| extend Resource = strcat("Base: ", osBaseImage, "<br/>Target: ", osTargetImage)
| extend Resource = osBaseImage
| project PreciseTimeStamp, Resource, faultInfo
| order by PreciseTimeStamp asc
| extend PrevTime = prev(PreciseTimeStamp)
| extend NextTime = next(PreciseTimeStamp)
| extend PrevResource = prev(Resource)
| extend NextResource = next(Resource)
| where 
isnull(PrevTime) or 
isnull(NextTime) or 
(Resource != PrevResource or Resource != NextResource) 
| extend StartTime = PreciseTimeStamp
| extend EndTime = next(PreciseTimeStamp)
| where NextResource == Resource
| project StartTime, EndTime, Content = Resource
| extend EndTime = iif(isnull(EndTime), datetime_add('minute', 1, StartTime), EndTime)
```

**Params:** `{queryNodeId}`

---

### Node Disk Configuration

_Widget purpose:_ Node State and Health

Cluster: `azurecm` · Database: `AzureCM` · Type: `Timeline`

```kusto
LogNodeSnapshot
| where PreciseTimeStamp between(global_startTime..global_endTime)
| where nodeId == queryNodeId 
| extend Resource = diskConfiguration
| project PreciseTimeStamp, Resource
| order by PreciseTimeStamp asc
| extend PrevTime = prev(PreciseTimeStamp)
| extend NextTime = next(PreciseTimeStamp)
| extend PrevResource = prev(Resource)
| extend NextResource = next(Resource)
| where 
isnull(PrevTime) or 
isnull(NextTime) or 
(Resource != PrevResource or Resource != NextResource) 
| extend StartTime = PreciseTimeStamp
| extend EndTime = next(PreciseTimeStamp)
| where NextResource == Resource
| project StartTime, EndTime, Content = Resource
| extend EndTime = iif(isnull(EndTime), datetime_add('minute', 1, StartTime), EndTime)
```

**Params:** `{queryNodeId}`

---

### Node VMA

_Widget purpose:_ Node State and Health

Cluster: `vmainsight` · Database: `vmadb` · Type: `Timeline`

```kusto
VmImpactingEventsV1
| where PreciseTimeStamp between(global_startTime..global_endTime)
| where NodeId == queryNodeId and RCAEngineCategory != "CustomerInitiated"
| extend Content = strcat(RCAEngineCategory, " - ", RCALevel1)
| extend Tooltip = strcat("RCALevel2: ", RCALevel2, "<br/>RCALevel3: ", RCALevel3, "<br/>Detail: ", Detail)
| project StartTime = PreciseTimeStamp, Content, Tooltip
```

**Params:** `{queryNodeId}`

---
