# Host Storage Internal (test VMs only)

> Source: **Azure Host Compare Investigation Guide** dashboard, chapter **Host Storage Internal (test VMs only)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Hagrid Perf VMs

### Azure Host Test VMs Max Latencies

_Widget purpose:_ {{nodeId1}} VM's Max Latencies (in milliseconds)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Host Storage Internal (test VMs only) > Hagrid Perf VMs > {{nodeId1}} VM's Max Latencies (in milliseconds)`

```kusto
let _endTime = queryTo + 2h;
let _startTime = queryFrom - 2h;
let cs = database('Fc').LogContainerSnapshot | where PreciseTimeStamp between (_startTime .. _endTime) and nodeId == nodeIdStr
| distinct containerId;
let startTime = ago(2d);
database('Sc').WorkloadResult
| where PreciseTimeStamp between (_startTime .. _endTime) and RoleInstance in (cs) 
        and TestType contains "summary"
        and TestType contains "OD1-" and TestType contains "TJ1-"
| extend Summary = parse_json(Summary)
| extend Lat_max = todouble(Summary.Lat_max)
| project PreciseTimeStamp, Lat_max, VmType = strcat(RoleInstance, "-", tostring(parse_json(InstanceMetadata).compute.storageProfile.dataDisks[0].caching))
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeIdStr}`

---

### Azure Host Test VMs Max Latencies

_Widget purpose:_ {{nodeId2}} VM's Max Latencies (in milliseconds)

Cluster: `storageclient.eastus.kusto.windows.net` · Database: `Fa` · Type: `TimeSeries`
Source panel: `Host Storage Internal (test VMs only) > Hagrid Perf VMs > {{nodeId2}} VM's Max Latencies (in milliseconds)`

```kusto
let _endTime = queryTo + 2h;
let _startTime = queryFrom - 2h;
let cs = database('Fc').LogContainerSnapshot | where PreciseTimeStamp between (_startTime .. _endTime) and nodeId == nodeIdStr
| distinct containerId;
let startTime = ago(2d);
database('Sc').WorkloadResult
| where PreciseTimeStamp between (_startTime .. _endTime) and RoleInstance in (cs) 
        and TestType contains "summary"
        and TestType contains "OD1-" and TestType contains "TJ1-"
| extend Summary = parse_json(Summary)
| extend Lat_max = todouble(Summary.Lat_max)
| project PreciseTimeStamp, Lat_max, VmType = strcat(RoleInstance, "-", tostring(parse_json(InstanceMetadata).compute.storageProfile.dataDisks[0].caching))
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeIdStr}`

---
