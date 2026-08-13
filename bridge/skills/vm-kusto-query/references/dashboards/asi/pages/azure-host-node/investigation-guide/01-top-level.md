# (top-level)

> Source: **Azure Host — Azure Host Node** dashboard, chapter **(top-level)** (2 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### Retrieve Resource "Azure Host Node"

Cluster: `azurecm.kusto.windows.net` · Database: `AzureCM` · Type: `ResourceGet` · Widget: `Container`

```kusto
LogNodeSnapshot
| where PreciseTimeStamp between ((globalFrom - 1h) .. (globalTo + 1h)) and nodeId == local_nodeId
| summarize arg_max(PreciseTimeStamp, Region, Tenant, DataCenterName, nodeId, ipAddress, containerCount, diskConfiguration, machinePoolName, tipNodeSessionId) by hostingEnvironment
| extend hostingEnvironment = parse_json(hostingEnvironment)
| extend HostOsVhd = tostring(hostingEnvironment.OSBaseImageName), AgentPackage = tostring(hostingEnvironment.AgentPackageName), ipAddress
| distinct Region, Tenant, DataCenterName, nodeId, ipAddress, containerCount, HostOsVhd, AgentPackage, diskConfiguration, machinePoolName, tipNodeSessionId
| extend globalFrom = globalFrom
```

**Params:** `{local_nodeId}`, `{globalFrom}`, `{globalTo}`

---

### ExtendedFaultTable

Cluster: `azcore.centralus.kusto.windows.net` · Database: `Fa` · Type: `Table`

```kusto
let returnTable = cluster('azcore.centralus').database('Fa').
IfxOperationV2v1EtwTable
| where PreciseTimeStamp between (queryFrom .. queryTo)
| where NodeId == nodeid
| where OperationName == "ExtendedErrorDetail"
| project TIMESTAMP, Region, ResultType, ResultSignature, ContextInCsv, RoleBuildNumber; //, ActivityId, ParentActivityId, RootOperationId
let check = toscalar(returnTable
| summarize count());
returnTable
| extend ReturnFailureSignature = iif(check > 0, 1, 0)
// | project ContextInCsv
| extend ContextInCsvPlus = strcat(ContextInCsv, ",")
| extend failFuncIndexStart = indexof(ContextInCsvPlus, "FailedFunction(s),") + strlen("FailedFunction(s),")
| extend failFuncIndexEnd = indexof(ContextInCsvPlus, ",", failFuncIndexStart)
| extend failFuncValue = substring(ContextInCsvPlus, failFuncIndexStart, failFuncIndexEnd - failFuncIndexStart)
| extend failHrIndexStart = indexof(ContextInCsvPlus, "FailingHr,\" ") + strlen("FailingHr,\" ")
| extend failHrIndexEnd = indexof(ContextInCsvPlus, ",", failHrIndexStart)
| extend failHrValue = substring(ContextInCsvPlus, failHrIndexStart, failHrIndexEnd - failHrIndexStart - 2)
| project PreciseTimeStamp = TIMESTAMP, RdAgentVersion = RoleBuildNumber, Region, ResultType, ResultSignature, FailedFunction = failFuncValue, failedHrValue = failHrValue
```

**Params:** `{queryFrom}`, `{queryTo}`, `{nodeid}`

**Signal filters seen in KQL:** `OperationName == "ExtendedErrorDetail"`

---
